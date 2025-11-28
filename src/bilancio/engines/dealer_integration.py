"""
Dealer subsystem integration for the main simulation engine.

This module provides a bridge between the main bilancio simulation engine
(System/Payables) and the dealer module (Tickets/States). It wraps the dealer
module's components to provide a clean interface for:

1. Converting Payables to Tickets for trading
2. Running dealer trading phases within the main simulation loop
3. Syncing trade results back to the main system

Architecture:
    Main System (Payables) <--> DealerSubsystem <--> Dealer Module (Tickets)

    - DealerSubsystem: Maintains parallel state (tickets, trader states)
    - Bridge functions: Convert between Payable and Ticket representations
    - Integration functions: Initialize, run trading, sync results

The dealer subsystem operates as a secondary market where agents can trade
their existing claims (Payables) to manage liquidity needs. Trades are
executed at market-determined prices through a dealer ring with value-based
traders (VBTs) providing outside liquidity.

References:
    - Dealer module docs: docs/dealer_ring.md
    - Dealer specification: Full specification document
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional, Any
import random

from bilancio.core.ids import AgentId, InstrId
from bilancio.dealer.models import (
    DealerState,
    VBTState,
    TraderState,
    Ticket,
    BucketConfig,
    DEFAULT_BUCKETS,
    TicketId,
)
from bilancio.dealer.kernel import KernelParams, recompute_dealer_state
from bilancio.dealer.trading import TradeExecutor
from bilancio.dealer.simulation import DealerRingConfig


@dataclass
class DealerSubsystem:
    """
    Wrapper that adapts dealer module for main simulation engine.

    This dataclass maintains all state needed for dealer trading operations,
    providing a clean boundary between the main simulation and the dealer
    subsystem.

    State Management:
        - Tickets: Tradable representations of Payables
        - Dealers: Per-bucket market makers with inventory and quotes
        - VBTs: Per-bucket outside liquidity providers
        - Traders: Per-agent trading states with single-issuer constraint

    Mapping Tables:
        - ticket_to_payable: Links tickets back to their source Payables
        - payable_to_ticket: Links Payables to their tradable tickets

    Trading Infrastructure:
        - executor: Handles trade execution and balance sheet updates
        - params: Kernel parameters for pricing computations
        - bucket_configs: Maturity-based grouping definitions

    Attributes:
        dealers: Per-bucket dealer states (bucket_id -> DealerState)
        vbts: Per-bucket VBT states (bucket_id -> VBTState)
        traders: Per-agent trader states (agent_id -> TraderState)
        tickets: All tradable tickets (ticket_id -> Ticket)
        ticket_to_payable: Mapping from ticket IDs to Payable contract IDs
        payable_to_ticket: Mapping from Payable contract IDs to ticket IDs
        bucket_configs: Maturity bucket configurations
        params: Kernel parameters for dealer pricing
        executor: Trade execution engine
        enabled: Whether dealer trading is active
        rng: Random number generator for order flow
    """

    dealers: Dict[str, DealerState] = field(default_factory=dict)
    vbts: Dict[str, VBTState] = field(default_factory=dict)
    traders: Dict[AgentId, TraderState] = field(default_factory=dict)
    tickets: Dict[TicketId, Ticket] = field(default_factory=dict)
    ticket_to_payable: Dict[TicketId, InstrId] = field(default_factory=dict)
    payable_to_ticket: Dict[InstrId, TicketId] = field(default_factory=dict)
    bucket_configs: List[BucketConfig] = field(default_factory=lambda: list(DEFAULT_BUCKETS))
    params: KernelParams = field(default_factory=lambda: KernelParams())
    executor: Optional[TradeExecutor] = None
    enabled: bool = True
    rng: random.Random = field(default_factory=lambda: random.Random(42))


def initialize_dealer_subsystem(
    system,
    dealer_config: DealerRingConfig,
    current_day: int = 0
) -> DealerSubsystem:
    """
    Initialize dealer subsystem from system state and configuration.

    This function performs the initial setup of the dealer subsystem:

    1. Create dealer/VBT agents in main system:
       - Add actual Household agents for each dealer and VBT
       - This allows proper ownership tracking in the main system

    2. Convert existing Payables to Tickets:
       - Extract all payables from system contracts
       - Create corresponding Ticket objects with maturity info
       - Assign tickets to maturity buckets
       - Build bidirectional mappings

    3. Initialize market makers:
       - Create DealerState for each bucket with initial capital
       - Create VBTState for each bucket with anchors
       - Allocate initial ticket inventory based on dealer_share/vbt_share

    4. Initialize traders:
       - Create TraderState for each household agent
       - Set initial cash from agent balance sheets
       - Link tickets to trader ownership

    5. Compute initial quotes:
       - Run kernel computation for each dealer
       - Generate initial bid/ask spreads

    Capital Allocation (NEW OUTSIDE MONEY):
        dealer_share: Fraction of system cash injected as dealer capital (e.g., 0.25)
        vbt_share: Fraction of system cash injected as VBT capital (e.g., 0.50)
        NOTE: Traders keep 100% of their tickets. Dealer/VBT start with EMPTY
              inventory and build it by BUYING from traders who want to sell.
              This is NEW MONEY from outside the system, not taken from traders.

    Args:
        system: Main System instance with agents and contracts
        dealer_config: Configuration for dealer subsystem
        current_day: Current simulation day for maturity calculations

    Returns:
        Initialized DealerSubsystem ready for trading

    Raises:
        ValueError: If configuration is invalid or system state inconsistent

    Example:
        >>> system = System()
        >>> # ... set up agents and create payables ...
        >>> config = DealerRingConfig(
        ...     ticket_size=Decimal(1),
        ...     dealer_share=Decimal("0.25"),
        ...     vbt_share=Decimal("0.50"),
        ... )
        >>> subsystem = initialize_dealer_subsystem(system, config)
        >>> # Now ready for run_dealer_trading_phase()
    """
    from bilancio.domain.agents import Dealer, VBT

    subsystem = DealerSubsystem(
        bucket_configs=dealer_config.buckets,
        params=KernelParams(S=dealer_config.ticket_size),
        rng=random.Random(dealer_config.seed),
    )

    # Step 0: Create dealer/VBT agents in main system
    # These agents allow proper ownership tracking when claims transfer to dealers
    for bucket_config in dealer_config.buckets:
        bucket_id = bucket_config.name
        dealer_agent_id = f"dealer_{bucket_id}"
        vbt_agent_id = f"vbt_{bucket_id}"

        # Create dealer agent if not exists
        if dealer_agent_id not in system.state.agents:
            dealer_agent = Dealer(
                id=dealer_agent_id,
                name=f"Dealer ({bucket_id})",
            )
            system.state.agents[dealer_agent_id] = dealer_agent

        # Create VBT agent if not exists
        if vbt_agent_id not in system.state.agents:
            vbt_agent = VBT(
                id=vbt_agent_id,
                name=f"VBT ({bucket_id})",
            )
            system.state.agents[vbt_agent_id] = vbt_agent

    # Initialize trade executor
    subsystem.executor = TradeExecutor(subsystem.params, subsystem.rng)

    # Step 1: Convert Payables to Tickets
    from bilancio.domain.instruments.credit import Payable

    serial_counter = 0
    for contract_id, contract in system.state.contracts.items():
        if not isinstance(contract, Payable):
            continue

        # Create ticket from payable
        ticket_id = f"TKT_{contract_id}"
        remaining_tau = max(0, contract.due_day - current_day)

        ticket = Ticket(
            id=ticket_id,
            issuer_id=contract.liability_issuer_id,  # Debtor
            owner_id=contract.effective_creditor,    # Current creditor
            face=Decimal(contract.amount),
            maturity_day=contract.due_day,
            remaining_tau=remaining_tau,
            bucket_id="",  # Will be assigned below
            serial=serial_counter,
        )
        serial_counter += 1

        # Assign to bucket
        ticket.bucket_id = _assign_bucket(ticket.remaining_tau, subsystem.bucket_configs)

        # Register ticket
        subsystem.tickets[ticket_id] = ticket
        subsystem.ticket_to_payable[ticket_id] = contract_id
        subsystem.payable_to_ticket[contract_id] = ticket_id

    # Step 2: Calculate total system cash for capital allocation
    # Dealer and VBT get NEW CASH from outside the system (not taken from traders)
    total_system_cash = Decimal(0)
    for agent_id, agent in system.state.agents.items():
        # Skip dealer/VBT agents we just created
        if agent.kind in ("dealer", "vbt"):
            continue
        total_system_cash += _get_agent_cash(system, agent_id)

    # Calculate dealer and VBT capital (NEW outside money)
    # Split evenly across buckets
    num_buckets = len(subsystem.bucket_configs)
    dealer_capital_per_bucket = (total_system_cash * dealer_config.dealer_share) / num_buckets
    vbt_capital_per_bucket = (total_system_cash * dealer_config.vbt_share) / num_buckets

    # Step 3: Initialize market makers
    for bucket_config in subsystem.bucket_configs:
        bucket_id = bucket_config.name

        # Get anchor prices from config
        M, O = dealer_config.vbt_anchors.get(
            bucket_id,
            (Decimal(1), Decimal("0.30"))
        )

        # Create dealer state with NEW capital (no inventory yet)
        dealer = DealerState(
            bucket_id=bucket_id,
            agent_id=f"dealer_{bucket_id}",
            inventory=[],  # Empty! Dealers build inventory by buying from traders
            cash=dealer_capital_per_bucket,  # NEW outside money
        )
        subsystem.dealers[bucket_id] = dealer

        # Create VBT state with NEW capital (no inventory yet)
        vbt = VBTState(
            bucket_id=bucket_id,
            agent_id=f"vbt_{bucket_id}",
            M=M,
            O=O,
            phi_M=dealer_config.phi_M,
            phi_O=dealer_config.phi_O,
            clip_nonneg_B=dealer_config.clip_nonneg_B,
            inventory=[],  # Empty! VBTs build inventory by buying from traders
            cash=vbt_capital_per_bucket,  # NEW outside money
        )
        vbt.recompute_quotes()
        subsystem.vbts[bucket_id] = vbt

        # NOTE: Traders keep 100% of their tickets (no allocation to dealer/VBT)
        # Dealer/VBT will acquire inventory by buying from traders during trading

        # Run kernel to compute initial quotes
        recompute_dealer_state(dealer, vbt, subsystem.params)

    # Step 3: Initialize traders (households only for now)
    for agent_id, agent in system.state.agents.items():
        if agent.kind != "household":
            continue

        # Calculate trader's cash from their cash holdings in main system
        trader_cash = _get_agent_cash(system, agent_id)

        trader = TraderState(
            agent_id=agent_id,
            cash=trader_cash,
            tickets_owned=[],
            obligations=[],
            asset_issuer_id=None,
        )

        # Link trader to their tickets
        for ticket in subsystem.tickets.values():
            if ticket.owner_id == agent_id:
                trader.tickets_owned.append(ticket)
                # Set asset_issuer_id based on first ticket held
                if trader.asset_issuer_id is None:
                    trader.asset_issuer_id = ticket.issuer_id

            if ticket.issuer_id == agent_id:
                trader.obligations.append(ticket)

        subsystem.traders[agent_id] = trader

    return subsystem


def _get_agent_cash(system, agent_id: str) -> Decimal:
    """
    Get total cash balance for an agent from the main system.

    Sums all cash contracts where the agent is the asset holder.

    Args:
        system: Main System instance
        agent_id: Agent ID to get cash for

    Returns:
        Total cash balance as Decimal
    """
    agent = system.state.agents.get(agent_id)
    if not agent:
        return Decimal(0)

    total_cash = Decimal(0)
    for contract_id in agent.asset_ids:
        contract = system.state.contracts.get(contract_id)
        if contract and contract.kind == "cash":
            total_cash += Decimal(contract.amount)

    return total_cash


def run_dealer_trading_phase(
    subsystem: DealerSubsystem,
    system,
    current_day: int
) -> List[dict]:
    """
    Execute one dealer trading phase for the current day.

    This function orchestrates a complete trading period:

    Phase 1: Update maturities
        - Increment day counters
        - Update remaining_tau for all tickets
        - Reassign tickets to buckets based on new maturities

    Phase 2: Recompute dealer quotes
        - Run kernel for each dealer based on new inventory
        - Update bid/ask prices

    Phase 3: Build eligibility sets
        - Identify traders with shortfalls (need cash)
        - Identify traders with surplus (can invest)
        - Apply policy constraints (single-issuer, horizon)

    Phase 4: Randomized order flow
        - Generate random order of eligible traders
        - Process sell orders (traders need cash)
        - Process buy orders (traders want to invest)
        - Execute trades through dealers or VBTs

    Phase 5: Record events
        - Log all trades with prices and counterparties
        - Track interior vs passthrough execution
        - Record dealer quote evolution

    Note: This is a simplified implementation. The full dealer simulation
    includes settlement, default handling, and VBT anchor updates which
    may be added in future iterations.

    Args:
        subsystem: Dealer subsystem state
        system: Main System instance (for accessing agent cash balances)
        current_day: Current simulation day

    Returns:
        List of trade event dictionaries for logging

    Example:
        >>> events = run_dealer_trading_phase(subsystem, system, day=5)
        >>> for event in events:
        ...     print(f"Trade: {event['trader']} {event['side']} at {event['price']}")
    """
    if not subsystem.enabled:
        return []

    events = []

    # Phase 0: Sync trader cash from main system
    # This ensures traders have up-to-date cash balances for eligibility checks
    for trader_id, trader in subsystem.traders.items():
        trader.cash = _get_agent_cash(system, trader_id)

    # Phase 0.5: Clean up tickets whose payables were removed
    # This can happen when agents default and get expelled (expel-agent mode)
    from bilancio.domain.instruments.credit import Payable
    orphaned_ticket_ids = []
    for ticket_id, payable_id in subsystem.ticket_to_payable.items():
        payable = system.state.contracts.get(payable_id)
        if payable is None or not isinstance(payable, Payable):
            orphaned_ticket_ids.append(ticket_id)

    for ticket_id in orphaned_ticket_ids:
        ticket = subsystem.tickets.get(ticket_id)
        if ticket:
            # Remove from inventories
            bucket = ticket.bucket_id
            dealer = subsystem.dealers.get(bucket)
            vbt = subsystem.vbts.get(bucket)
            if dealer and ticket in dealer.inventory:
                dealer.inventory.remove(ticket)
            if vbt and ticket in vbt.inventory:
                vbt.inventory.remove(ticket)
            # Remove from trader holdings
            for trader in subsystem.traders.values():
                if ticket in trader.tickets_owned:
                    trader.tickets_owned.remove(ticket)
                if ticket in trader.obligations:
                    trader.obligations.remove(ticket)
            # Remove ticket
            del subsystem.tickets[ticket_id]

        # Clean up mappings
        payable_id = subsystem.ticket_to_payable.pop(ticket_id, None)
        if payable_id:
            subsystem.payable_to_ticket.pop(payable_id, None)

    # Phase 1: Update ticket maturities and buckets
    # Collect matured tickets to remove after iteration
    matured_ticket_ids = []

    for ticket in subsystem.tickets.values():
        # Update remaining maturity
        old_bucket = ticket.bucket_id
        ticket.remaining_tau = max(0, ticket.maturity_day - current_day)

        # Mark matured tickets for cleanup (remaining_tau = 0 means due today or past)
        if ticket.remaining_tau == 0:
            matured_ticket_ids.append(ticket.id)
            # Remove from inventories before deletion
            old_dealer = subsystem.dealers.get(old_bucket)
            old_vbt = subsystem.vbts.get(old_bucket)
            if old_dealer and ticket in old_dealer.inventory:
                old_dealer.inventory.remove(ticket)
            if old_vbt and ticket in old_vbt.inventory:
                old_vbt.inventory.remove(ticket)
            # Remove from trader holdings
            for trader in subsystem.traders.values():
                if ticket in trader.tickets_owned:
                    trader.tickets_owned.remove(ticket)
                if ticket in trader.obligations:
                    trader.obligations.remove(ticket)
            continue

        new_bucket = _assign_bucket(ticket.remaining_tau, subsystem.bucket_configs)

        # If bucket changed, move ticket to new dealer/VBT inventory
        if new_bucket != old_bucket:
            # Remove from old bucket's inventories
            old_dealer = subsystem.dealers.get(old_bucket)
            old_vbt = subsystem.vbts.get(old_bucket)
            if old_dealer and ticket in old_dealer.inventory:
                old_dealer.inventory.remove(ticket)
            if old_vbt and ticket in old_vbt.inventory:
                old_vbt.inventory.remove(ticket)

            # Add to new bucket's appropriate inventory
            ticket.bucket_id = new_bucket
            new_dealer = subsystem.dealers.get(new_bucket)
            new_vbt = subsystem.vbts.get(new_bucket)

            # Assign to dealer or VBT based on current owner
            if new_dealer and ticket.owner_id == f"dealer_{old_bucket}":
                ticket.owner_id = f"dealer_{new_bucket}"
                new_dealer.inventory.append(ticket)
            elif new_vbt and ticket.owner_id == f"vbt_{old_bucket}":
                ticket.owner_id = f"vbt_{new_bucket}"
                new_vbt.inventory.append(ticket)

    # Clean up matured tickets to prevent unbounded memory growth
    for ticket_id in matured_ticket_ids:
        del subsystem.tickets[ticket_id]

    # Phase 2: Recompute dealer quotes for all buckets
    for bucket_id, dealer in subsystem.dealers.items():
        vbt = subsystem.vbts[bucket_id]
        recompute_dealer_state(dealer, vbt, subsystem.params)

    # Phase 3: Build eligibility sets (simplified)
    # Traders who need cash (have shortfall coming in next few days)
    eligible_sellers = []
    horizon = 10  # Look ahead this many days for upcoming obligations
    for trader_id, trader in subsystem.traders.items():
        # Check for shortfall on any of the next 'horizon' days
        upcoming_shortfall = Decimal(0)
        for day_offset in range(horizon + 1):
            upcoming_shortfall = max(upcoming_shortfall, trader.shortfall(current_day + day_offset))
        if upcoming_shortfall > 0 and trader.tickets_owned:
            eligible_sellers.append(trader_id)

    # Traders who can buy (have surplus cash beyond needs)
    # DISABLED for now: Buying can hurt by reducing liquidity of potential payers.
    # The primary purpose of the dealer is to provide liquidity to sellers.
    eligible_buyers = []
    # Only allow buying if trader has significant surplus above obligations
    # for trader_id, trader in subsystem.traders.items():
    #     max_upcoming_dues = Decimal(0)
    #     for day_offset in range(horizon + 1):
    #         max_upcoming_dues = max(max_upcoming_dues, trader.dues_on_day(current_day + day_offset))
    #     surplus = trader.cash - max_upcoming_dues
    #     if surplus > Decimal(500):  # Only if significant surplus
    #         eligible_buyers.append(trader_id)

    # Phase 4: Randomized order flow (simplified)
    # Process sellers first (they have urgent needs)
    subsystem.rng.shuffle(eligible_sellers)
    for trader_id in eligible_sellers[:10]:  # Process up to 10 sellers per phase
        trader = subsystem.traders[trader_id]
        if not trader.tickets_owned:
            continue

        # Select ticket to sell (first in list for simplicity)
        ticket = trader.tickets_owned[0]
        bucket_id = ticket.bucket_id
        dealer = subsystem.dealers[bucket_id]
        vbt = subsystem.vbts[bucket_id]

        # Execute customer sell
        result = subsystem.executor.execute_customer_sell(
            dealer, vbt, ticket, check_assertions=False
        )

        if result.executed:
            # Scale price by ticket face value
            # The dealer module returns unit price (per S=1), but our tickets have actual face values
            scaled_price = result.price * ticket.face

            # Update trader state
            trader.tickets_owned.remove(ticket)
            trader.cash += scaled_price

            events.append({
                "kind": "dealer_trade",
                "day": current_day,
                "phase": "simulation",
                "trader": trader_id,
                "side": "sell",
                "ticket_id": ticket.id,
                "bucket": bucket_id,
                "price": float(scaled_price),
                "unit_price": float(result.price),
                "face": float(ticket.face),
                "is_passthrough": result.is_passthrough,
            })

    # Process buyers (simplified: fewer trades)
    subsystem.rng.shuffle(eligible_buyers)
    for trader_id in eligible_buyers[:1]:  # Very limited buying for now
        trader = subsystem.traders[trader_id]

        # Try to buy from first available bucket
        for bucket_id, dealer in subsystem.dealers.items():
            vbt = subsystem.vbts[bucket_id]

            # Check if dealer or VBT has inventory
            if not dealer.inventory and not vbt.inventory:
                continue

            # Execute customer buy
            result = subsystem.executor.execute_customer_buy(
                dealer, vbt, trader_id, check_assertions=False
            )

            if result.executed and result.ticket:
                # Scale price by ticket face value
                scaled_price = result.price * result.ticket.face

                # Update trader state
                trader.tickets_owned.append(result.ticket)
                trader.cash -= scaled_price

                # Update asset issuer if first ticket
                if trader.asset_issuer_id is None:
                    trader.asset_issuer_id = result.ticket.issuer_id

                events.append({
                    "kind": "dealer_trade",
                    "day": current_day,
                    "phase": "simulation",
                    "trader": trader_id,
                    "side": "buy",
                    "ticket_id": result.ticket.id,
                    "bucket": bucket_id,
                    "price": float(scaled_price),
                    "unit_price": float(result.price),
                    "face": float(result.ticket.face),
                    "is_passthrough": result.is_passthrough,
                })
                break  # One buy per trader per phase

    return events


def sync_dealer_to_system(
    subsystem: DealerSubsystem,
    system
) -> None:
    """
    Sync dealer trade results back to main system state.

    This function bridges the dealer subsystem state back to the main
    simulation system, updating:

    1. Payable ownership:
       - Update Payable.asset_holder_id for transferred claims
       - Update agent.asset_ids lists (remove from old holder, add to new)
       - Maintain double-entry consistency

    2. Agent cash balances:
       - Apply cash changes from trader.cash to agent balance sheets
       - Update Cash contract amounts in system.state.contracts

    3. Consistency checks:
       - Verify ticket ownership matches payable asset_holder_id
       - Ensure cash changes sum to zero (closed system)

    Implementation approach:
        - Use ticket_to_payable mapping to find contracts
        - Update asset_holder_id based on ticket.owner_id
        - Calculate cash deltas by comparing trader.cash to agent balance

    Note: This is a simplified implementation. A full version would:
        - Handle cash contract splits/merges atomically
        - Track exact cash changes through trade history
        - Support rollback on validation failures
        - Log all sync operations for audit trail

    Args:
        subsystem: Dealer subsystem with updated state
        system: Main System instance to update

    Raises:
        ValidationError: If sync would violate system invariants

    Example:
        >>> # After trading phase
        >>> events = run_dealer_trading_phase(subsystem, system, day=5)
        >>> # Sync results back to main system
        >>> sync_dealer_to_system(subsystem, system)
        >>> # Now system.state reflects all trades
    """
    from bilancio.domain.instruments.credit import Payable

    # Step 1: Update Payable ownership for transferred claims
    # Note: Payable has two holder fields:
    # - asset_holder_id: original creditor (from base Instrument class)
    # - holder_id: secondary market holder (specific to Payable)
    # Settlement uses effective_creditor which returns holder_id if set, else asset_holder_id
    for ticket_id, ticket in subsystem.tickets.items():
        # Get corresponding payable
        payable_id = subsystem.ticket_to_payable.get(ticket_id)
        if not payable_id:
            continue

        payable = system.state.contracts.get(payable_id)
        if not isinstance(payable, Payable):
            continue

        # Check if ownership changed (compare with effective_creditor)
        current_holder = payable.effective_creditor
        new_holder = ticket.owner_id

        if current_holder != new_holder:
            # Update agent asset_ids lists
            old_holder_agent = system.state.agents.get(current_holder)
            new_holder_agent = system.state.agents.get(new_holder)

            if old_holder_agent and payable_id in old_holder_agent.asset_ids:
                old_holder_agent.asset_ids.remove(payable_id)

            if new_holder_agent and payable_id not in new_holder_agent.asset_ids:
                new_holder_agent.asset_ids.append(payable_id)

            # Update payable's holder_id (secondary market holder)
            # Keep asset_holder_id as the original creditor
            payable.holder_id = new_holder

            # Log the transfer
            system.log(
                "ClaimTransferredDealer",
                payable_id=payable_id,
                from_holder=current_holder,
                to_holder=new_holder,
                amount=payable.amount,
                due_day=payable.due_day
            )

    # Step 2: Sync trader cash balances
    # Compare trader.cash in dealer subsystem to actual cash in main system
    # and apply the delta as minting (if trader gained) or burning (if trader paid)
    for trader_id, trader in subsystem.traders.items():
        main_system_cash = _get_agent_cash(system, trader_id)
        dealer_cash = trader.cash
        delta = dealer_cash - main_system_cash

        if delta > 0:
            # Trader gained cash from selling tickets - mint cash to them
            # This represents money coming from outside the system (dealer/VBT)
            system.mint_cash(to_agent_id=trader_id, amount=round(delta))
        elif delta < 0:
            # Trader spent cash buying tickets - need to reduce their cash
            # Find and reduce their cash contracts
            agent = system.state.agents.get(trader_id)
            if agent:
                remaining_to_burn = abs(delta)
                for contract_id in list(agent.asset_ids):
                    if remaining_to_burn <= 0:
                        break
                    contract = system.state.contracts.get(contract_id)
                    if contract and contract.kind == "cash":
                        if contract.amount <= remaining_to_burn:
                            # Remove entire contract
                            remaining_to_burn -= contract.amount
                            agent.asset_ids.remove(contract_id)
                            del system.state.contracts[contract_id]
                        else:
                            # Reduce contract amount
                            contract.amount -= round(remaining_to_burn)
                            remaining_to_burn = 0


def _assign_bucket(remaining_tau: int, bucket_configs: List[BucketConfig]) -> str:
    """
    Assign a ticket to a maturity bucket based on remaining tau.

    Args:
        remaining_tau: Days remaining until maturity
        bucket_configs: List of bucket definitions

    Returns:
        Bucket name (e.g., "short", "mid", "long")

    Example:
        >>> _assign_bucket(2, DEFAULT_BUCKETS)
        'short'
        >>> _assign_bucket(15, DEFAULT_BUCKETS)
        'long'
    """
    for bucket in bucket_configs:
        if remaining_tau < bucket.tau_min:
            continue
        if bucket.tau_max is None or remaining_tau <= bucket.tau_max:
            return bucket.name

    # Default to last bucket (usually "long")
    return bucket_configs[-1].name if bucket_configs else "default"
