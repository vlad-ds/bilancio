# Implementation Plan: VBT/Dealer Simulation Module

## Overview

This plan specifies the implementation of a secondary market dealer module for the Kalecki ring simulation, enabling debt liquidity via market-making. The module introduces:

- **Dealers**: Market makers that quote bid/ask prices and absorb customer flow
- **Value-Based Traders (VBTs)**: Deep-pocketed outside market that provides ultimate liquidity
- **Tickets**: Standardized debt claims of uniform size for trading
- **Maturity Buckets**: Short/Mid/Long classification with separate dealer/VBT pairs

**Goal**: Successfully simulate the worked examples from the specification without "cheating" (i.e., using only the specified formulas and event mechanics).

---

## 1. Module Structure

```
src/bilancio/
├── dealer/                          # NEW: Dealer module
│   ├── __init__.py
│   ├── models.py                    # Ticket, DealerState, VBTState data models
│   ├── kernel.py                    # L1 dealer pricing kernel
│   ├── vbt.py                       # Value-based trader anchor logic
│   ├── events.py                    # Dealer-specific events
│   ├── trading.py                   # Order flow and trade execution
│   └── simulation.py                # Dealer ring event loop
├── domain/
│   └── agents/
│       └── dealer.py                # NEW: Dealer and VBT agent types
├── config/
│   └── models.py                    # Extended with DealerConfig, VBTConfig
└── scenarios/
    └── generators/
        └── dealer_ring.py           # NEW: Dealer ring scenario generator
```

**Rationale**: Keep dealer logic self-contained in a dedicated module while integrating with existing domain and config patterns. This allows:
- Independent testing of dealer kernel
- Clear separation from existing ring experiments
- Easy feature flagging if dealer is optional

---

## 2. Data Models

### 2.1 Ticket Model (`dealer/models.py`)

Tickets are the tradeable unit - standardized debt claims.

```python
from dataclasses import dataclass, field
from decimal import Decimal
from bilancio.core.ids import InstrId, AgentId

@dataclass
class Ticket:
    """A standardized debt claim of face value S."""
    id: InstrId                      # Unique ticket identifier
    issuer_id: AgentId               # Who owes this debt (debtor)
    owner_id: AgentId                # Current holder (creditor)
    face: Decimal                    # Face value S (typically 1)
    maturity_day: int                # When this ticket matures (absolute day)
    remaining_tau: int = 0           # Remaining days to maturity (updated each day)
    bucket_id: str = ""              # "short" | "mid" | "long"
    serial: int = 0                  # For deterministic tie-breaking

    def __post_init__(self):
        """Compute initial remaining_tau and bucket."""
        # bucket_id set by engine based on remaining_tau
```

### 2.2 Bucket Configuration

```python
@dataclass
class BucketConfig:
    """Configuration for a maturity bucket."""
    name: str                        # "short", "mid", "long"
    tau_min: int                     # Minimum remaining maturity (inclusive)
    tau_max: int | None              # Maximum remaining maturity (None = unbounded)

# Default bucket ranges per specification
DEFAULT_BUCKETS = [
    BucketConfig("short", 1, 3),     # tau in {1, 2, 3}
    BucketConfig("mid", 4, 8),       # tau in {4, ..., 8}
    BucketConfig("long", 9, None),   # tau >= 9
]
```

### 2.3 Dealer State (`dealer/models.py`)

```python
@dataclass
class DealerState:
    """Per-bucket dealer state."""
    bucket_id: str                   # Which bucket this dealer trades

    # Balance sheet
    inventory: list[Ticket] = field(default_factory=list)  # Tickets held
    cash: Decimal = Decimal(0)       # Cash holdings

    # Derived quantities (recomputed after each trade)
    a: int = 0                       # Number of tickets held (len(inventory))
    x: Decimal = Decimal(0)          # Face inventory = a * S
    V: Decimal = Decimal(0)          # Mid-valued inventory = M*a + C
    K_star: int = 0                  # Max buy tickets fundable
    X_star: Decimal = Decimal(0)     # One-sided capacity in face units
    N: int = 1                       # Ladder rungs
    lambda_: Decimal = Decimal(1)    # Layoff probability
    I: Decimal = Decimal(0)          # Inside width

    # Quotes (computed from inventory and VBT anchors)
    bid: Decimal = Decimal(0)        # Current bid price b_c(x)
    ask: Decimal = Decimal(0)        # Current ask price a_c(x)
    midline: Decimal = Decimal(0)    # Current midline p(x)

    # Pin flags (for assertions)
    is_pinned_bid: bool = False      # bid == B (outside)
    is_pinned_ask: bool = False      # ask == A (outside)

    def ticket_ids_by_issuer(self) -> dict[AgentId, list[InstrId]]:
        """Group inventory tickets by issuer for settlement."""
        result: dict[AgentId, list[InstrId]] = {}
        for t in self.inventory:
            result.setdefault(t.issuer_id, []).append(t.id)
        return result
```

### 2.4 VBT State (`dealer/models.py`)

```python
@dataclass
class VBTState:
    """Per-bucket value-based trader state."""
    bucket_id: str

    # Anchors (exogenous or updated by loss rule)
    M: Decimal = Decimal(1)          # Outside mid
    O: Decimal = Decimal("0.30")     # Outside spread

    # Derived outside quotes
    A: Decimal = Decimal(0)          # Ask = M + O/2
    B: Decimal = Decimal(0)          # Bid = M - O/2

    # Sensitivity parameters for loss-based update
    phi_M: Decimal = Decimal(1)      # Mid sensitivity to loss
    phi_O: Decimal = Decimal("0.6")  # Spread sensitivity to loss

    # Optional clipping
    O_min: Decimal = Decimal(0)      # Minimum spread
    clip_nonneg_B: bool = True       # Clip B >= 0

    # Balance sheet (for double-entry consistency)
    inventory: list[Ticket] = field(default_factory=list)
    cash: Decimal = Decimal(0)

    def recompute_quotes(self):
        """Update A, B from M, O with optional clipping."""
        self.A = self.M + self.O / 2
        self.B = self.M - self.O / 2
        if self.clip_nonneg_B:
            self.B = max(Decimal(0), self.B)

    def update_from_loss(self, loss_rate: Decimal):
        """Apply loss-based anchor update rule."""
        # M_{t+1} = M_t - phi_M * l_t
        # O_{t+1} = O_t + phi_O * l_t
        self.M = self.M - self.phi_M * loss_rate
        self.O = max(self.O_min, self.O + self.phi_O * loss_rate)
        self.recompute_quotes()
```

---

## 3. Dealer Kernel Implementation (`dealer/kernel.py`)

The L1 dealer pricing kernel - the mathematical heart of the module.

```python
from decimal import Decimal, ROUND_FLOOR
from dataclasses import dataclass
from .models import DealerState, VBTState

# Guard threshold
M_MIN = Decimal("0.02")

@dataclass
class KernelParams:
    """Parameters for dealer kernel computation."""
    S: Decimal = Decimal(1)          # Standard ticket size

def recompute_dealer_state(
    dealer: DealerState,
    vbt: VBTState,
    params: KernelParams,
) -> None:
    """
    Recompute all derived dealer quantities from current (inventory, cash).

    This is the core L1 kernel from the specification.
    """
    S = params.S
    M = vbt.M
    O = vbt.O
    A = vbt.A
    B = vbt.B

    # Current inventory
    dealer.a = len(dealer.inventory)
    dealer.x = S * dealer.a

    # Guard: if M <= M_min, collapse to outside-only
    if M <= M_MIN:
        dealer.V = dealer.cash
        dealer.K_star = 0
        dealer.X_star = Decimal(0)
        dealer.N = 1
        dealer.lambda_ = Decimal(1)
        dealer.I = O  # Not used when pinned
        dealer.midline = M
        dealer.bid = B
        dealer.ask = A
        dealer.is_pinned_bid = True
        dealer.is_pinned_ask = True
        return

    # Mid-valued inventory
    dealer.V = M * dealer.a + dealer.cash

    # Maximum buy tickets fundable without borrowing
    dealer.K_star = int((dealer.V / M).to_integral_value(rounding=ROUND_FLOOR))

    # One-sided capacity in face units
    dealer.X_star = S * dealer.K_star

    # Ladder rungs
    dealer.N = dealer.K_star + 1

    # Layoff probability (reflecting random walk)
    # lambda = S / (X* + S)
    if dealer.X_star + S > 0:
        dealer.lambda_ = S / (dealer.X_star + S)
    else:
        dealer.lambda_ = Decimal(1)

    # Inside width (competitive equilibrium)
    # I = lambda * O
    dealer.I = dealer.lambda_ * O

    # Inventory-sensitive midline
    # p(x) = M - (O / (X* + 2S)) * (x - X*/2)
    if dealer.X_star + 2 * S > 0:
        slope = O / (dealer.X_star + 2 * S)
        dealer.midline = M - slope * (dealer.x - dealer.X_star / 2)
    else:
        dealer.midline = M

    # Interior quotes
    a_interior = dealer.midline + dealer.I / 2
    b_interior = dealer.midline - dealer.I / 2

    # Clipped quotes
    dealer.ask = min(A, a_interior)
    dealer.bid = max(B, b_interior)

    # Pin detection
    dealer.is_pinned_ask = (dealer.ask == A)
    dealer.is_pinned_bid = (dealer.bid == B)


def can_interior_buy(dealer: DealerState, params: KernelParams) -> bool:
    """
    Check if dealer can execute interior BUY (dealer buys ticket from customer).

    Interior buy feasible iff:
    - x + S <= X*  (capacity)
    - C >= b_c(x)  (cash available)
    """
    S = params.S
    return (
        dealer.x + S <= dealer.X_star and
        dealer.cash >= dealer.bid
    )


def can_interior_sell(dealer: DealerState, params: KernelParams) -> bool:
    """
    Check if dealer can execute interior SELL (dealer sells ticket to customer).

    Interior sell feasible iff:
    - x >= S (has inventory)
    """
    S = params.S
    return dealer.x >= S


@dataclass
class ExecutionResult:
    """Result of a trade execution."""
    executed: bool
    price: Decimal
    is_passthrough: bool             # True if routed to VBT
    ticket: "Ticket | None" = None   # Ticket transferred (for BUYs)
```

---

## 4. Trading Logic (`dealer/trading.py`)

Order flow and trade execution mechanics.

```python
from decimal import Decimal
from typing import Protocol
import random

from .models import DealerState, VBTState, Ticket
from .kernel import (
    recompute_dealer_state,
    can_interior_buy,
    can_interior_sell,
    ExecutionResult,
    KernelParams,
)

class TradeExecutor:
    """Executes trades between customers and dealers."""

    def __init__(self, params: KernelParams, rng: random.Random | None = None):
        self.params = params
        self.rng = rng or random.Random()

    def execute_customer_sell(
        self,
        dealer: DealerState,
        vbt: VBTState,
        ticket: Ticket,
    ) -> ExecutionResult:
        """
        Customer sells ticket to dealer (dealer buys).

        Events 1 (interior) or 9 (passthrough at outside bid).
        """
        # Check interior feasibility
        if can_interior_buy(dealer, self.params):
            # Interior execution at dealer bid
            price = dealer.bid

            # Update dealer state
            dealer.inventory.append(ticket)
            dealer.cash -= price
            ticket.owner_id = dealer.agent_id  # Transfer ownership

            # Recompute quotes
            recompute_dealer_state(dealer, vbt, self.params)

            return ExecutionResult(
                executed=True,
                price=price,
                is_passthrough=False,
                ticket=ticket,
            )
        else:
            # Passthrough at outside bid B
            price = vbt.B

            # VBT absorbs the ticket (dealer state unchanged)
            vbt.inventory.append(ticket)
            vbt.cash -= price
            ticket.owner_id = vbt.agent_id

            # Dealer state unchanged (x', C') = (x, C)
            # Just recompute to ensure consistency
            recompute_dealer_state(dealer, vbt, self.params)

            return ExecutionResult(
                executed=True,
                price=price,
                is_passthrough=True,
                ticket=ticket,
            )

    def execute_customer_buy(
        self,
        dealer: DealerState,
        vbt: VBTState,
        buyer_id: AgentId,
        issuer_preference: AgentId | None = None,
    ) -> ExecutionResult:
        """
        Customer buys ticket from dealer (dealer sells).

        Events 2 (interior) or 10 (passthrough at outside ask).

        Ticket selection: lowest maturity_day, then lowest serial (deterministic).
        """
        if can_interior_sell(dealer, self.params):
            # Interior execution at dealer ask
            price = dealer.ask

            # Select ticket to transfer (deterministic tie-breaker)
            ticket = self._select_ticket_to_sell(
                dealer.inventory,
                issuer_preference,
            )

            # Update dealer state
            dealer.inventory.remove(ticket)
            dealer.cash += price
            ticket.owner_id = buyer_id

            # Recompute quotes
            recompute_dealer_state(dealer, vbt, self.params)

            return ExecutionResult(
                executed=True,
                price=price,
                is_passthrough=False,
                ticket=ticket,
            )
        else:
            # Passthrough at outside ask A
            price = vbt.A

            # VBT provides ticket (dealer state unchanged)
            ticket = self._select_ticket_to_sell(
                vbt.inventory,
                issuer_preference,
            )

            vbt.inventory.remove(ticket)
            vbt.cash += price
            ticket.owner_id = buyer_id

            return ExecutionResult(
                executed=True,
                price=price,
                is_passthrough=True,
                ticket=ticket,
            )

    def _select_ticket_to_sell(
        self,
        inventory: list[Ticket],
        issuer_preference: AgentId | None,
    ) -> Ticket:
        """Select ticket by: issuer match, then lowest maturity, then lowest serial."""
        candidates = inventory

        if issuer_preference:
            matching = [t for t in candidates if t.issuer_id == issuer_preference]
            if matching:
                candidates = matching

        # Sort by maturity_day, then serial
        candidates = sorted(candidates, key=lambda t: (t.maturity_day, t.serial))
        return candidates[0]
```

---

## 5. Event Loop (`dealer/simulation.py`)

The dealer ring simulation event loop, following specification Section 11.

```python
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable
import random

from .models import Ticket, DealerState, VBTState, BucketConfig
from .kernel import recompute_dealer_state, KernelParams
from .trading import TradeExecutor
from .events import DealerEvent, EventLog

@dataclass
class DealerRingConfig:
    """Configuration for dealer ring simulation."""
    # Agents
    n_traders: int = 100             # Minimum 100 per spec

    # Tickets
    ticket_size: Decimal = Decimal(1)  # S

    # Buckets
    buckets: list[BucketConfig] = field(default_factory=lambda: DEFAULT_BUCKETS)

    # VBT anchors per bucket
    vbt_anchors: dict[str, tuple[Decimal, Decimal]] = field(default_factory=dict)
    # e.g., {"short": (1.0, 0.20), "mid": (1.0, 0.30), "long": (1.0, 0.40)}

    # VBT sensitivity
    phi_M: Decimal = Decimal(1)
    phi_O: Decimal = Decimal("0.6")

    # Guard
    M_min: Decimal = Decimal("0.02")
    clip_nonneg_B: bool = True

    # Order flow
    pi_sell: Decimal = Decimal("0.5")  # P(next arrival is SELL)
    N_max: int = 3                     # Max arrivals per period

    # Trader policies
    horizon_H: int = 3                 # Min days to liability for investment
    buffer_B: Decimal = Decimal(1)     # Cash buffer for investment eligibility

    # Initial allocation
    dealer_share: Decimal = Decimal("0.25")
    vbt_share: Decimal = Decimal("0.50")

    # RNG
    seed: int = 42


@dataclass
class TraderState:
    """Per-trader state for the dealer ring."""
    agent_id: AgentId

    # Balance sheet
    cash: Decimal = Decimal(0)
    tickets_owned: list[Ticket] = field(default_factory=list)

    # Liabilities
    obligations: list[Ticket] = field(default_factory=list)  # Tickets this agent issued

    # Single-issuer constraint (asset side)
    asset_issuer_id: AgentId | None = None  # k(i) in spec

    def payment_due(self, day: int) -> Decimal:
        """Total payment obligations due on this day."""
        return sum(
            t.face for t in self.obligations
            if t.maturity_day == day
        )

    def shortfall(self, day: int) -> Decimal:
        """Liquidity shortfall for day."""
        due = self.payment_due(day)
        return max(Decimal(0), due - self.cash)

    def earliest_liability_day(self, after_day: int) -> int | None:
        """Earliest liability date strictly after given day."""
        future = [t.maturity_day for t in self.obligations if t.maturity_day > after_day]
        return min(future) if future else None


class DealerRingSimulation:
    """
    Main simulation orchestrator for the dealer ring.

    Event loop per specification Section 11:
    1. Update maturities and buckets
    2. Dealer pre-computation (per bucket)
    3. Compute trading eligibility sets
    4. Randomized one-ticket order flow
    5. Settlement with proportional recovery
    6. VBT anchor update (if enabled)
    """

    def __init__(self, config: DealerRingConfig):
        self.config = config
        self.rng = random.Random(config.seed)

        # State
        self.day: int = 0
        self.dealers: dict[str, DealerState] = {}      # bucket -> dealer
        self.vbts: dict[str, VBTState] = {}            # bucket -> VBT
        self.traders: dict[AgentId, TraderState] = {}
        self.all_tickets: dict[InstrId, Ticket] = {}   # Global ticket registry

        # Event log
        self.events: EventLog = EventLog()

        # Kernel params
        self.params = KernelParams(S=config.ticket_size)
        self.executor = TradeExecutor(self.params, self.rng)

    def run_day(self) -> None:
        """Execute one simulation day."""
        self.day += 1

        # Phase 1: Update maturities and buckets
        self._update_maturities()
        self._rebucket_tickets()

        # Phase 2: Dealer pre-computation
        for bucket_id in self.dealers:
            recompute_dealer_state(
                self.dealers[bucket_id],
                self.vbts[bucket_id],
                self.params,
            )

        # Phase 3: Compute eligibility sets
        sell_eligible = self._compute_sell_eligible()
        buy_eligible = self._compute_buy_eligible()

        # Phase 4: Randomized order flow
        self._process_order_flow(sell_eligible, buy_eligible)

        # Phase 5: Settlement
        self._settle_maturing_debt()

        # Phase 6: VBT anchor update
        self._update_vbt_anchors()

    def _update_maturities(self) -> None:
        """Decrement remaining_tau for all tickets."""
        for ticket in self.all_tickets.values():
            ticket.remaining_tau = ticket.maturity_day - self.day

    def _rebucket_tickets(self) -> None:
        """
        Reassign bucket_id based on remaining_tau.
        If dealer/VBT holds migrating ticket, execute internal sale.
        """
        for ticket in self.all_tickets.values():
            old_bucket = ticket.bucket_id
            new_bucket = self._compute_bucket(ticket.remaining_tau)

            if old_bucket != new_bucket and new_bucket is not None:
                # Check if dealer or VBT holds this ticket
                owner_id = ticket.owner_id

                if owner_id == self.dealers[old_bucket].agent_id:
                    # Event 11: Dealer-to-dealer internal sale
                    self._rebucket_dealer_ticket(ticket, old_bucket, new_bucket)
                elif owner_id == self.vbts[old_bucket].agent_id:
                    # Event 12: VBT-to-VBT internal sale
                    self._rebucket_vbt_ticket(ticket, old_bucket, new_bucket)
                else:
                    # Trader-held: just update bucket_id
                    ticket.bucket_id = new_bucket

    def _rebucket_dealer_ticket(
        self,
        ticket: Ticket,
        old_bucket: str,
        new_bucket: str,
    ) -> None:
        """
        Event 11: Internal sale from old-bucket dealer to new-bucket dealer.
        Price = M_new (new bucket mid).
        """
        old_dealer = self.dealers[old_bucket]
        new_dealer = self.dealers[new_bucket]
        new_vbt = self.vbts[new_bucket]

        price = new_vbt.M  # Transfer at new bucket mid

        # Remove from old dealer
        old_dealer.inventory.remove(ticket)
        old_dealer.cash += price

        # Add to new dealer
        new_dealer.inventory.append(ticket)
        new_dealer.cash -= price
        ticket.owner_id = new_dealer.agent_id
        ticket.bucket_id = new_bucket

        # Recompute both dealers
        recompute_dealer_state(old_dealer, self.vbts[old_bucket], self.params)
        recompute_dealer_state(new_dealer, new_vbt, self.params)

        self.events.log_rebucket(ticket, old_bucket, new_bucket, price, "dealer")

    def _compute_sell_eligible(self) -> set[AgentId]:
        """Traders with shortfall > 0 and at least one ticket owned."""
        eligible = set()
        for trader in self.traders.values():
            if (trader.shortfall(self.day) > 0 and
                len(trader.tickets_owned) > 0 and
                not trader.defaulted):
                eligible.add(trader.agent_id)
        return eligible

    def _compute_buy_eligible(self) -> set[AgentId]:
        """Traders with horizon >= H and cash > buffer."""
        eligible = set()
        H = self.config.horizon_H
        B = self.config.buffer_B

        for trader in self.traders.values():
            earliest = trader.earliest_liability_day(self.day)
            horizon_ok = (earliest is None) or (earliest - self.day >= H)
            cash_ok = trader.cash > B

            if horizon_ok and cash_ok and not trader.defaulted:
                eligible.add(trader.agent_id)
        return eligible

    def _process_order_flow(
        self,
        sell_eligible: set[AgentId],
        buy_eligible: set[AgentId],
    ) -> None:
        """
        Randomized one-ticket order flow (Section 11, Step 4).
        """
        n = 0
        while n < self.config.N_max and (sell_eligible or buy_eligible):
            n += 1

            # Draw side preference
            z = self.rng.random() < float(self.config.pi_sell)

            if z:  # SELL preferred
                if sell_eligible:
                    agent_id = self.rng.choice(list(sell_eligible))
                    self._process_sell(agent_id, sell_eligible)
                elif buy_eligible:
                    # Fallback to BUY
                    agent_id = self.rng.choice(list(buy_eligible))
                    self._process_buy(agent_id, buy_eligible)
            else:  # BUY preferred
                if buy_eligible:
                    agent_id = self.rng.choice(list(buy_eligible))
                    self._process_buy(agent_id, buy_eligible)
                elif sell_eligible:
                    # Fallback to SELL
                    agent_id = self.rng.choice(list(sell_eligible))
                    self._process_sell(agent_id, sell_eligible)

    def _process_sell(self, agent_id: AgentId, eligible: set[AgentId]) -> None:
        """Process a SELL order from trader to dealer."""
        trader = self.traders[agent_id]

        # Select ticket to sell (shortest maturity first)
        ticket = self._select_ticket_to_sell(trader)
        if ticket is None:
            return

        # Get appropriate dealer
        dealer = self.dealers[ticket.bucket_id]
        vbt = self.vbts[ticket.bucket_id]

        # Execute trade
        result = self.executor.execute_customer_sell(dealer, vbt, ticket)

        if result.executed:
            # Update trader state
            trader.tickets_owned.remove(ticket)
            trader.cash += result.price

            # Remove from eligible set (one SELL per period)
            eligible.discard(agent_id)

            self.events.log_trade(
                day=self.day,
                side="SELL",
                trader_id=agent_id,
                ticket_id=ticket.id,
                bucket=ticket.bucket_id,
                price=result.price,
                is_passthrough=result.is_passthrough,
            )

    def _process_buy(self, agent_id: AgentId, eligible: set[AgentId]) -> None:
        """Process a BUY order from trader to dealer."""
        trader = self.traders[agent_id]

        # Choose bucket (Short -> Mid -> Long preference)
        bucket_id = self._select_bucket_to_buy(trader)
        if bucket_id is None:
            return

        dealer = self.dealers[bucket_id]
        vbt = self.vbts[bucket_id]

        # Check affordability
        price = dealer.ask if not dealer.is_pinned_ask else vbt.A
        if trader.cash < price:
            # No feasible execution, agent stays in eligible set
            return

        # Execute trade
        result = self.executor.execute_customer_buy(
            dealer, vbt, agent_id,
            issuer_preference=trader.asset_issuer_id,
        )

        if result.executed:
            # Update trader state
            trader.tickets_owned.append(result.ticket)
            trader.cash -= result.price

            # Set issuer constraint if first buy
            if trader.asset_issuer_id is None:
                trader.asset_issuer_id = result.ticket.issuer_id

            # Remove from eligible set
            eligible.discard(agent_id)

            self.events.log_trade(
                day=self.day,
                side="BUY",
                trader_id=agent_id,
                ticket_id=result.ticket.id,
                bucket=bucket_id,
                price=result.price,
                is_passthrough=result.is_passthrough,
            )

    def _settle_maturing_debt(self) -> None:
        """
        Settlement with proportional recovery (Section 11, Step 5).
        """
        # Collect all tickets maturing today, grouped by issuer
        maturing_by_issuer: dict[AgentId, list[Ticket]] = {}
        for ticket in self.all_tickets.values():
            if ticket.maturity_day == self.day:
                maturing_by_issuer.setdefault(ticket.issuer_id, []).append(ticket)

        for issuer_id, tickets in maturing_by_issuer.items():
            self._settle_issuer(issuer_id, tickets)

    def _settle_issuer(self, issuer_id: AgentId, tickets: list[Ticket]) -> None:
        """
        Settle all maturing tickets for one issuer with proportional recovery.
        """
        issuer = self.traders.get(issuer_id)
        if issuer is None or issuer.defaulted:
            # Already defaulted or not a trader (dealer/VBT)
            return

        N_i = len(tickets)
        D_i = sum(t.face for t in tickets)  # Total due
        C_i = issuer.cash                   # Available cash

        # Recovery rate
        R_i = min(Decimal(1), C_i / D_i) if D_i > 0 else Decimal(1)

        # Distribute to each holder
        for ticket in tickets:
            holder_id = ticket.owner_id
            q_h = ticket.face  # Face value of this ticket
            payment = q_h * R_i

            # Pay holder
            self._pay_holder(holder_id, payment)

            # Delete ticket
            del self.all_tickets[ticket.id]

        # Update issuer cash
        issuer.cash = C_i - R_i * D_i  # 0 if R < 1

        # Log settlement/default
        if R_i < Decimal(1):
            self.events.log_default(
                day=self.day,
                issuer_id=issuer_id,
                recovery_rate=R_i,
                total_due=D_i,
                total_paid=R_i * D_i,
            )
            issuer.defaulted = True
        else:
            self.events.log_settlement(
                day=self.day,
                issuer_id=issuer_id,
                total_paid=D_i,
            )

    def _pay_holder(self, holder_id: AgentId, amount: Decimal) -> None:
        """Credit payment to holder (trader, dealer, or VBT)."""
        if holder_id in self.traders:
            self.traders[holder_id].cash += amount
        else:
            # Check dealers and VBTs
            for dealer in self.dealers.values():
                if dealer.agent_id == holder_id:
                    dealer.cash += amount
                    return
            for vbt in self.vbts.values():
                if vbt.agent_id == holder_id:
                    vbt.cash += amount
                    return

    def _update_vbt_anchors(self) -> None:
        """
        Update VBT anchors based on bucket loss rates (Section 10).
        """
        for bucket_id, vbt in self.vbts.items():
            loss_rate = self._compute_bucket_loss_rate(bucket_id)
            if loss_rate > 0:
                vbt.update_from_loss(loss_rate)

                # Recompute dealer quotes with new anchors
                recompute_dealer_state(
                    self.dealers[bucket_id],
                    vbt,
                    self.params,
                )

    def _compute_bucket_loss_rate(self, bucket_id: str) -> Decimal:
        """
        Compute loss rate for tickets that matured today in this bucket.
        l_t = sum(face * (1 - R)) / sum(face) for maturing tickets.
        """
        # This requires tracking which tickets matured and their recovery rates
        # Implementation depends on how we log defaults
        return self.events.get_bucket_loss_rate(self.day, bucket_id)
```

---

## 6. Events and Logging (`dealer/events.py`)

Comprehensive event logging for observability.

```python
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

@dataclass
class EventLog:
    """Structured event log for dealer ring simulation."""

    events: list[dict] = field(default_factory=list)

    # Indexed structures for efficient lookup
    defaults_by_day: dict[int, list[dict]] = field(default_factory=dict)
    trades_by_day: dict[int, list[dict]] = field(default_factory=dict)

    def log(self, kind: str, day: int, **payload) -> None:
        """Append event to log."""
        event = {"kind": kind, "day": day, **payload}
        self.events.append(event)

    def log_trade(
        self,
        day: int,
        side: str,  # "BUY" or "SELL"
        trader_id: str,
        ticket_id: str,
        bucket: str,
        price: Decimal,
        is_passthrough: bool,
    ) -> None:
        event = {
            "kind": "Trade",
            "day": day,
            "side": side,
            "trader_id": trader_id,
            "ticket_id": ticket_id,
            "bucket": bucket,
            "price": str(price),
            "is_passthrough": is_passthrough,
        }
        self.events.append(event)
        self.trades_by_day.setdefault(day, []).append(event)

    def log_quote(
        self,
        day: int,
        bucket: str,
        dealer_bid: Decimal,
        dealer_ask: Decimal,
        vbt_bid: Decimal,
        vbt_ask: Decimal,
        inventory: int,
        capacity: Decimal,
        is_pinned_bid: bool,
        is_pinned_ask: bool,
    ) -> None:
        self.log(
            "DealerQuote",
            day=day,
            bucket=bucket,
            dealer_bid=str(dealer_bid),
            dealer_ask=str(dealer_ask),
            vbt_bid=str(vbt_bid),
            vbt_ask=str(vbt_ask),
            inventory=inventory,
            capacity=str(capacity),
            is_pinned_bid=is_pinned_bid,
            is_pinned_ask=is_pinned_ask,
        )

    def log_settlement(
        self,
        day: int,
        issuer_id: str,
        total_paid: Decimal,
    ) -> None:
        self.log(
            "Settlement",
            day=day,
            issuer_id=issuer_id,
            total_paid=str(total_paid),
            recovery_rate="1",
        )

    def log_default(
        self,
        day: int,
        issuer_id: str,
        recovery_rate: Decimal,
        total_due: Decimal,
        total_paid: Decimal,
    ) -> None:
        event = {
            "kind": "Default",
            "day": day,
            "issuer_id": issuer_id,
            "recovery_rate": str(recovery_rate),
            "total_due": str(total_due),
            "total_paid": str(total_paid),
        }
        self.events.append(event)
        self.defaults_by_day.setdefault(day, []).append(event)

    def log_rebucket(
        self,
        ticket: "Ticket",
        old_bucket: str,
        new_bucket: str,
        price: Decimal,
        holder_type: str,  # "dealer" or "vbt"
    ) -> None:
        self.log(
            "Rebucket",
            day=ticket.maturity_day - ticket.remaining_tau,  # Current day
            ticket_id=ticket.id,
            old_bucket=old_bucket,
            new_bucket=new_bucket,
            price=str(price),
            holder_type=holder_type,
        )

    def get_bucket_loss_rate(self, day: int, bucket_id: str) -> Decimal:
        """Compute loss rate for bucket from today's defaults."""
        defaults = self.defaults_by_day.get(day, [])

        total_loss = Decimal(0)
        total_face = Decimal(0)

        for d in defaults:
            # Would need bucket info attached to default events
            # For now, simplified: compute from recovery_rate
            due = Decimal(d["total_due"])
            rate = Decimal(d["recovery_rate"])
            loss = due * (1 - rate)

            total_loss += loss
            total_face += due

        if total_face > 0:
            return total_loss / total_face
        return Decimal(0)
```

---

## 7. Configuration Extensions (`config/models.py`)

Extend existing configuration system.

```python
# Add to existing models.py

@dataclass
class DealerRingConfig:
    """Configuration for dealer ring scenario."""

    # Ring structure
    n_traders: int = 100

    # Ticket parameters
    ticket_size: Decimal = Decimal(1)

    # Maturity buckets
    buckets: list[BucketConfig] = field(default_factory=lambda: [
        {"name": "short", "tau_min": 1, "tau_max": 3},
        {"name": "mid", "tau_min": 4, "tau_max": 8},
        {"name": "long", "tau_min": 9, "tau_max": None},
    ])

    # VBT anchors per bucket (initial M, O)
    vbt_anchors: dict[str, dict] = field(default_factory=lambda: {
        "short": {"M": "1.0", "O": "0.20", "phi_M": "1.0", "phi_O": "0.6"},
        "mid": {"M": "1.0", "O": "0.30", "phi_M": "1.0", "phi_O": "0.6"},
        "long": {"M": "1.0", "O": "0.40", "phi_M": "1.0", "phi_O": "0.6"},
    })

    # Guard
    guard: dict = field(default_factory=lambda: {
        "M_min": "0.02",
        "clip_nonneg_B": True,
    })

    # Order flow
    order_flow: dict = field(default_factory=lambda: {
        "pi_sell": "0.5",
        "N_max": 3,
    })

    # Trader policies
    trader_policy: dict = field(default_factory=lambda: {
        "H_min_invest": 3,
        "buffer_cash_B": "1.0",
    })

    # Initial allocation
    initial_allocation: dict = field(default_factory=lambda: {
        "dealer_share": "0.25",
        "vbt_share": "0.50",
        "traders_share": "0.25",
    })

    # Simulation
    seed: int = 42
    max_days: int = 30

    # Ring debt structure (borrowed from RingExplorerParams)
    kappa: Decimal | None = None  # Debt-to-liquidity ratio
    # ... other ring params
```

---

## 8. Assertions and Invariant Checks

Following the C1-C6 assertions from the examples document.

```python
# dealer/assertions.py

from decimal import Decimal
from .models import DealerState, VBTState, Ticket

EPSILON_CASH = Decimal("1e-10")
EPSILON_QTY = 0

def assert_c1_double_entry(
    cash_changes: dict[str, Decimal],
    qty_changes: dict[str, int],
) -> None:
    """C1: Conservation - sum of cash/qty changes is zero."""
    total_cash = sum(cash_changes.values())
    total_qty = sum(qty_changes.values())

    assert abs(total_cash) <= EPSILON_CASH, f"Cash not conserved: {total_cash}"
    assert abs(total_qty) <= EPSILON_QTY, f"Qty not conserved: {total_qty}"


def assert_c2_quote_bounds(dealer: DealerState, vbt: VBTState) -> None:
    """C2: Quotes within outside bounds."""
    assert dealer.bid >= vbt.B, f"Bid {dealer.bid} < B {vbt.B}"
    assert dealer.ask <= vbt.A, f"Ask {dealer.ask} > A {vbt.A}"

    # Pin detection consistency
    assert (dealer.ask == vbt.A) == dealer.is_pinned_ask
    assert (dealer.bid == vbt.B) == dealer.is_pinned_bid


def assert_c3_feasibility(
    dealer: DealerState,
    side: str,
    params: "KernelParams",
) -> None:
    """C3: Pre-check feasibility before interior execution."""
    S = params.S
    if side == "BUY":  # Dealer buys = customer sells
        assert dealer.x + S <= dealer.X_star, "Capacity check failed"
        assert dealer.cash >= dealer.bid, "Cash check failed"
    else:  # Dealer sells = customer buys
        assert dealer.x >= S, "Inventory check failed"


def assert_c4_passthrough_invariant(
    dealer_before: DealerState,
    dealer_after: DealerState,
) -> None:
    """C4: Passthrough leaves dealer state unchanged."""
    assert dealer_after.x == dealer_before.x, "Inventory changed in passthrough"
    assert dealer_after.cash == dealer_before.cash, "Cash changed in passthrough"


def assert_c5_equity_basis(
    dealer: DealerState,
    vbt: VBTState,
) -> None:
    """C5: Equity = C + M*a at VBT mid."""
    E = dealer.cash + vbt.M * dealer.a
    assert abs(E - dealer.V) <= EPSILON_CASH, f"Equity mismatch: {E} vs {dealer.V}"


def assert_c6_anchor_timing(
    vbt_before: VBTState,
    vbt_after: VBTState,
    during_order_flow: bool,
) -> None:
    """C6: Anchors don't change during order flow."""
    if during_order_flow:
        assert vbt_after.M == vbt_before.M, "M changed during order flow"
        assert vbt_after.O == vbt_before.O, "O changed during order flow"
```

---

## 9. Testing Strategy

### 9.1 Unit Tests - Dealer Kernel

```python
# tests/dealer/test_kernel.py

def test_capacity_computation():
    """Verify K* = floor(V/M) and X* = S*K*."""
    # Example from spec: a=2, C=2, M=1, S=1 -> V=4, K*=4, X*=4
    ...

def test_layoff_probability():
    """Verify lambda = S/(X* + S)."""
    # With X*=4, S=1 -> lambda = 1/5 = 0.2
    ...

def test_inside_width():
    """Verify I = lambda * O."""
    # With lambda=0.2, O=0.30 -> I = 0.06
    ...

def test_midline_formula():
    """Verify p(x) = M - O/(X*+2S) * (x - X*/2)."""
    # At balanced inventory x=2 (X*=4): p(2) = 1.0
    ...

def test_guard_regime():
    """When M <= M_min, X* := 0 and quotes pinned to outside."""
    ...
```

### 9.2 Integration Tests - Worked Examples

One test per example from the examples document:

```python
# tests/dealer/test_examples.py

def test_example_1_migrating_claim():
    """Example 1: Selling a migrating claim and dealer rebucketing."""
    ...

def test_example_2_maturing_debt():
    """Example 2: Maturing debt and cross-bucket reallocation."""
    ...

def test_example_3_outside_bid_clipping():
    """Example 3: Outside-bid clipping toggle (A/B variants)."""
    ...

def test_example_4_inventory_limit_layoff():
    """Example 4: Dealer reaches inventory limit and VBT layoff occurs."""
    ...

def test_example_5_dealer_earns():
    """Example 5: Dealer earns over time and inventory grows."""
    ...

def test_example_6_bid_passthrough():
    """Example 6: Bid-side pass-through at outside bid."""
    ...

def test_example_guard_low_mid():
    """Guard regime with M <= M_min."""
    ...

def test_example_partial_recovery():
    """Partial-recovery default with multiple claimant types."""
    ...

def test_example_trader_rebucketing():
    """Trader-held rebucketing without dealer-dealer transfer."""
    ...

def test_example_capacity_jump():
    """One-ticket trade pushes capacity across an integer."""
    ...

def test_example_order_flow_harness():
    """Minimal event-loop harness for arrivals."""
    ...

def test_example_ticket_transfer():
    """Ticket-level transfer (no generic materialization)."""
    ...
```

### 9.3 Property-Based Tests

```python
# tests/dealer/test_properties.py

from hypothesis import given, strategies as st

@given(st.decimals(min_value="0.01", max_value="10"))
def test_quotes_always_within_bounds(M):
    """For any valid M, quotes satisfy B <= b_c(x) <= a_c(x) <= A."""
    ...

@given(st.integers(min_value=0, max_value=100))
def test_inventory_on_ladder(inventory):
    """Inventory always on valid ladder rung."""
    ...

def test_passthrough_conserves_dealer_state():
    """Passthrough trades don't change dealer (x, C)."""
    ...
```

---

## 10. CLI Integration

Add commands to the existing CLI.

```python
# Add to ui/cli.py

@app.command()
def dealer_ring(
    scenario: str = typer.Argument(..., help="Path to dealer ring scenario YAML"),
    out: str = typer.Option("out/dealer", help="Output directory"),
    max_days: int = typer.Option(30, help="Maximum simulation days"),
    seed: int = typer.Option(42, help="RNG seed"),
    html: str = typer.Option(None, help="Path for HTML report"),
):
    """Run a dealer ring simulation."""
    from bilancio.dealer.simulation import DealerRingSimulation
    from bilancio.dealer.config import load_dealer_scenario

    config = load_dealer_scenario(scenario)
    config.seed = seed
    config.max_days = max_days

    sim = DealerRingSimulation(config)

    for day in range(max_days):
        sim.run_day()
        if sim.is_stable():
            break

    # Export results
    sim.export(out)
    if html:
        sim.export_html(html)
```

---

## 11. Implementation Phases

### Phase 1: Core Kernel (Week 1)

**Deliverables**:
- `dealer/models.py` - Data models (Ticket, DealerState, VBTState)
- `dealer/kernel.py` - L1 pricing kernel
- `tests/dealer/test_kernel.py` - Unit tests for kernel formulas

**Acceptance Criteria**:
- All kernel formulas match specification exactly
- Capacity, layoff probability, inside width compute correctly
- Guard regime activates at M <= M_min

### Phase 2: Trading Mechanics (Week 2)

**Deliverables**:
- `dealer/trading.py` - Trade execution logic
- `dealer/assertions.py` - C1-C6 invariant checks
- `tests/dealer/test_trading.py` - Trading tests

**Acceptance Criteria**:
- Interior and passthrough trades execute correctly
- Double-entry accounting preserved
- Assertions pass for all trade types

### Phase 3: Event Loop (Week 3)

**Deliverables**:
- `dealer/simulation.py` - Full event loop
- `dealer/events.py` - Event logging
- `tests/dealer/test_examples.py` - Worked examples as tests

**Acceptance Criteria**:
- All 12+ worked examples from specification pass
- Event log captures all required events
- Settlement with proportional recovery works

### Phase 4: Integration & Polish (Week 4)

**Deliverables**:
- `config/models.py` extensions
- `scenarios/generators/dealer_ring.py`
- `ui/cli.py` extensions
- Documentation

**Acceptance Criteria**:
- YAML configuration works
- CLI commands functional
- HTML reports generated
- README updated

---

## 12. Observability Requirements

### 12.1 Event Types to Log

| Event | Fields | When |
|-------|--------|------|
| `DayStart` | day | Start of each simulation day |
| `BucketUpdate` | ticket_id, old_bucket, new_bucket | Ticket changes bucket |
| `DealerQuote` | bucket, bid, ask, inventory, capacity, pinned_* | After each trade |
| `Trade` | side, trader_id, ticket_id, bucket, price, is_passthrough | Each trade |
| `Settlement` | issuer_id, total_paid, recovery_rate | Full payment |
| `Default` | issuer_id, recovery_rate, total_due, total_paid | Partial payment |
| `VBTAnchorUpdate` | bucket, M_old, M_new, O_old, O_new, loss_rate | After defaults |
| `Rebucket` | ticket_id, old_bucket, new_bucket, price, holder_type | Internal transfers |

### 12.2 Metrics to Compute

| Metric | Description |
|--------|-------------|
| `time_to_stability` | Day when no more trades/defaults occur |
| `total_defaults` | Count of default events |
| `total_trades` | Count of trade events |
| `avg_recovery_rate` | Mean recovery rate across defaults |
| `dealer_pnl_by_bucket` | Dealer profit/loss per bucket |
| `vbt_absorption` | Tickets absorbed by VBT via passthrough |
| `spread_earned` | Total dealer spread revenue |

### 12.3 HTML Dashboard

Generate interactive HTML report with:
- Timeline of events
- Dealer inventory charts per bucket
- Quote evolution (bid/ask over time)
- Default waterfall
- Settlement flow diagram

---

## 13. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Formula errors | Implement C1-C6 assertions, run all worked examples |
| Precision issues | Use `Decimal` throughout, not float |
| Integration conflicts | Keep dealer module isolated, minimal changes to existing code |
| Performance | Profile with 100+ traders, optimize if needed |
| Complexity | Start with simplest case (fixed anchors), add VBT updates later |

---

## 14. Open Questions

1. **Bucket boundaries**: Specification says Short={1,2,3}, Mid={4,...,8}, Long>=9. Should these be configurable?

2. **VBT anchor updates**: Enable by default or require explicit flag?

3. **Integration with existing ring**: Should dealer ring replace or extend existing `ring_explorer.py`?

4. **Multi-issuer exposure for dealers**: Specification says dealers can hold claims on multiple issuers. Do we need to track this explicitly for settlement priority?

5. **Partial recovery to dealers/VBTs**: When a trader defaults, dealers and VBTs holding their tickets get proportional recovery. This changes their inventory value - do we need to re-mark inventory?

---

## 15. Dependencies

**Python packages** (already in project):
- `pydantic` - Configuration validation
- `decimal` - Precise arithmetic
- `dataclasses` - Data models

**No new dependencies required.**

---

## 16. Success Criteria

1. **All worked examples pass** - The 15+ examples from the examples document execute without assertion failures

2. **Double-entry always balances** - C1 assertion never fails

3. **Quotes always valid** - C2 assertion never fails

4. **No "cheating"** - Implementation uses only specified formulas, no hardcoded results

5. **Observability** - Can reconstruct any example step-by-step from event log

6. **Performance** - 100 traders, 30 days completes in <10 seconds
