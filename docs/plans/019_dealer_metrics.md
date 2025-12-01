# Plan 019: Dealer Metrics for Functional Dealer Analysis

## Overview

This plan implements the measurement framework defined in Section 8 of the "New Kalecki Ring with Dealers" specification. The goal is to add comprehensive metrics to evaluate whether the dealer satisfies the "functional dealer" criteria (D1-D3) and requirements (R1-R6).

## Background

The current comparison experiments measure only global default metrics (δ_t, φ_t) and relief ratios. However, to evaluate the functional dealer specification, we need:

1. **Dealer P&L dynamics** - Is the dealer non-loss-making?
2. **Trader investment returns** - Do traders have realistic earning opportunities?
3. **Repayment-priority compliance** - Do traders invest only when safe to do so?
4. **Liquidity channel usage** - Are securities used as liquidity buffers?

## Requirements from PDF Section 8

### 8.1 Run-level Structure and Trade Log

For each simulation run, we require:

**Ring-level state (already exists):**
- Aggregate ring metrics per period: S_t, M̄_t, M_t, v_t, φ_t, δ_t
- Counts and sizes of defaults
- Distribution of recovery rates across issuers

**Dealer and VBT state per maturity bucket b:**
- Dealer inventory a_t^(b) (tickets)
- Dealer cash C_t^(b)
- Outside mid M_t^(b) and spread O_t^(b) from VBT
- Inside bid/ask quotes b_t^(b)(x), a_t^(b)(x)
- Mark-to-mid equity: E_t^(b) = C_t^(b) + M_t^(b) * a_t^(b)
- Equity increments: ΔE_t^(b) := E_t^(b) - E_{t-1}^(b)

**Trader-level state for each agent i:**
- Cash C_i(t)
- Set of tickets held (issuer, face, maturity)
- Schedule of future obligations (tickets where i is issuer)
- Default indicator and recovery received

**Trade log - for each dealer trade:**
- time t
- bucket b
- side ∈ {BUY, SELL}
- agent i
- price p
- issuer
- maturity

### 8.2 Dealer and VBT Profitability

Define for bucket b in run r:
- P&L: Π_r^(b) := E_T^(b) - E_0^(b)
- Return: π_r^(b) := Π_r^(b) / E_0^(b) (when E_0^(b) > 0)

A dealer is empirically sustainable if:
- Mean Π_r^(b) >= 0 across runs
- Π_r^(b) >= 0 on a large majority of runs

**P&L Decomposition:**
- Inside spread income (difference between dealer buy and sell prices)
- Outside layoff costs at VBT quotes
- Mark-to-mid revaluation of inventory between periods

### 8.3 Trader Investment Returns and Liquidity Use

**Ticket-level realized return:**
For trader i and ticket τ purchased at price p_buy, realized payoff X_τ is:
- Coupon payments received while holding
- Settlement amount at maturity (if held)
- Resale price if sold to dealer

Return: R_τ := (X_τ - p_buy) / p_buy

**Trader investment performance:**
R_i := (1/|T_i|) * Σ R_τ for all tickets τ purchased by i

Track:
- Distribution of {R_i} across traders
- Fraction of traders with R_i > 0

**Liquidity-driven sales and "rescues":**
A sale is liquidity-motivated when the seller has a shortfall in current obligations.

Track:
- Number of liquidity-driven sales
- Number of "rescue events" (obligations that would have defaulted but were met after such sales)

### 8.4 Repayment-Priority Diagnostics

Define safety margin for trader i at time t:
- A_i(t) := C_i(t) + Σ b_t^(τ) * S_τ (cash + saleable securities at bid)
- D_i(t) := Σ S_τ (remaining nominal obligations)
- m_i(t) := A_i(t) - D_i(t) (deterministic safety margin)

When trader i buys a ticket, record m_i(t-) and m_i(t+) (before and after).

Track:
- Fraction of BUY trades that reduce m_i(t) below zero
- Distribution of m_i(t) at time of default for agents that eventually default
- Distribution of m_i(t) when agents liquidate for liquidity reasons

### 8.5 Experiment-Level Summary Statistics

Each parameter triple (κ, c, μ) generates:
- Default-relief statistic R
- Dealer/VBT profitability indicators (mean and dispersion of Π_r^(b) and π_r^(b))
- Trader investment performance (distribution of R_i)
- Repayment-priority compliance (frequency of safety-margin violations at BUY)
- Usage of liquidity channel (counts of rescue events)

## Implementation Plan

### Phase 1: Data Structures (8.1)

#### 1.1 Create DealerMetrics Module

**File:** `src/bilancio/dealer/metrics.py` (NEW)

```python
@dataclass
class TradeRecord:
    """Record of a single dealer trade."""
    day: int
    bucket: str
    side: str  # "BUY" or "SELL"
    trader_id: str
    ticket_id: str
    issuer_id: str
    maturity: int
    face_value: Decimal
    price: Decimal
    unit_price: Decimal  # price / face_value
    is_passthrough: bool

    # Pre-trade state
    dealer_inventory_before: int
    dealer_cash_before: Decimal
    trader_cash_before: Decimal
    trader_safety_margin_before: Decimal

    # Post-trade state
    dealer_inventory_after: int
    dealer_cash_after: Decimal
    trader_cash_after: Decimal
    trader_safety_margin_after: Decimal

    # Flags
    is_liquidity_driven: bool  # Seller had shortfall

@dataclass
class DealerSnapshot:
    """Snapshot of dealer state at a point in time."""
    day: int
    bucket: str
    inventory: int
    cash: Decimal
    bid: Decimal
    ask: Decimal
    midline: Decimal
    vbt_mid: Decimal
    vbt_spread: Decimal
    mark_to_mid_equity: Decimal  # cash + vbt_mid * inventory * S

@dataclass
class TraderSnapshot:
    """Snapshot of trader state at a point in time."""
    day: int
    trader_id: str
    cash: Decimal
    tickets_held: List[str]  # ticket IDs
    total_face_held: Decimal
    obligations_remaining: Decimal
    safety_margin: Decimal

@dataclass
class TicketOutcome:
    """Final outcome of a ticket (for return calculation)."""
    ticket_id: str
    issuer_id: str
    maturity: int
    face_value: Decimal

    # Purchase info (if bought from dealer)
    purchased_from_dealer: bool
    purchase_day: Optional[int]
    purchase_price: Optional[Decimal]
    purchaser_id: Optional[str]

    # Sale info (if sold to dealer)
    sold_to_dealer: bool
    sale_day: Optional[int]
    sale_price: Optional[Decimal]
    seller_id: Optional[str]

    # Settlement info
    settled: bool
    settlement_day: Optional[int]
    recovery_rate: Optional[Decimal]
    settlement_amount: Optional[Decimal]

@dataclass
class RunMetrics:
    """All metrics for a single simulation run."""
    # Trade log
    trades: List[TradeRecord]

    # Daily snapshots
    dealer_snapshots: List[DealerSnapshot]
    trader_snapshots: List[TraderSnapshot]

    # Ticket outcomes
    ticket_outcomes: Dict[str, TicketOutcome]

    # Computed metrics
    def dealer_pnl_by_bucket(self) -> Dict[str, Decimal]: ...
    def dealer_return_by_bucket(self) -> Dict[str, Decimal]: ...
    def trader_returns(self) -> Dict[str, Decimal]: ...
    def liquidity_driven_sales(self) -> int: ...
    def rescue_events(self) -> int: ...
    def safety_margin_violations(self) -> int: ...
```

#### 1.2 Extend DealerSubsystem

**File:** `src/bilancio/engines/dealer_integration.py`

Add to DealerSubsystem:
- `metrics: RunMetrics` - accumulated metrics for current run
- `_capture_dealer_snapshot()` - capture dealer state at end of each day
- `_capture_trader_snapshots()` - capture trader states
- `_compute_safety_margin(trader_id)` - compute m_i(t) for a trader
- `_is_liquidity_driven(trader_id)` - check if trade is liquidity-motivated

Modify `run_dealer_trading_phase()`:
- Before each trade, compute pre-trade safety margin
- After each trade, compute post-trade safety margin
- Log extended TradeRecord to metrics

#### 1.3 Extend Trade Executor

**File:** `src/bilancio/dealer/trading.py`

Modify ExecutionResult to include:
- `dealer_inventory_before`, `dealer_inventory_after`
- `dealer_cash_before`, `dealer_cash_after`

### Phase 2: Profitability Metrics (8.2)

#### 2.1 Dealer Equity Tracking

Add to DealerSnapshot:
```python
mark_to_mid_equity: Decimal  # E_t^(b) = C_t^(b) + M_t^(b) * a_t^(b) * S
```

Compute at end of each day after dealer phase.

#### 2.2 P&L Computation

Add methods to RunMetrics:
```python
def dealer_pnl_by_bucket(self) -> Dict[str, Decimal]:
    """Compute Π_r^(b) = E_T^(b) - E_0^(b) for each bucket."""

def dealer_return_by_bucket(self) -> Dict[str, Decimal]:
    """Compute π_r^(b) = Π_r^(b) / E_0^(b) for each bucket."""
```

#### 2.3 P&L Decomposition

Add to TradeRecord:
```python
spread_income: Decimal  # Contribution to spread income
layoff_cost: Decimal  # Cost if passthrough
```

Add aggregation methods:
```python
def spread_income_total(self) -> Decimal: ...
def layoff_costs_total(self) -> Decimal: ...
def mark_to_mid_change_total(self) -> Decimal: ...
```

### Phase 3: Trader Returns (8.3)

#### 3.1 Ticket Outcome Tracking

Track in TicketOutcome:
- Who bought from dealer, when, at what price
- Who sold to dealer, when, at what price
- Final settlement outcome

#### 3.2 Return Calculation

```python
def ticket_realized_return(outcome: TicketOutcome) -> Optional[Decimal]:
    """Compute R_τ for a ticket purchased from dealer."""
    if not outcome.purchased_from_dealer:
        return None

    X = Decimal(0)  # Total payoff
    if outcome.sold_to_dealer:
        X = outcome.sale_price
    elif outcome.settled:
        X = outcome.settlement_amount
    else:
        X = Decimal(0)  # Still held, mark to current bid?

    p_buy = outcome.purchase_price
    return (X - p_buy) / p_buy

def trader_investment_return(trader_id: str, outcomes: Dict) -> Decimal:
    """Compute R_i = mean of R_τ for all tickets bought by trader i."""
```

#### 3.3 Liquidity-Driven Sales

A sale is liquidity-driven if the seller would have a shortfall for obligations due today without selling.

Track in TradeRecord:
- `is_liquidity_driven: bool`

Add metrics:
- Count of liquidity-driven sales
- "Rescue events": obligations met after liquidity-driven sales that would have defaulted otherwise

### Phase 4: Repayment Priority (8.4)

#### 4.1 Safety Margin Computation

```python
def compute_safety_margin(
    trader_id: str,
    cash: Decimal,
    tickets_held: List[Ticket],
    obligations: List[Payable],
    dealers: Dict[str, DealerState],
    ticket_size: Decimal
) -> Decimal:
    """
    Compute m_i(t) = A_i(t) - D_i(t)
    where:
    A_i(t) = cash + sum of (bid_price * face_value) for held tickets
    D_i(t) = sum of face values of remaining obligations
    """
```

#### 4.2 Track Margin Changes on BUY

For each BUY trade:
- Compute m_i(t-) before trade
- Compute m_i(t+) after trade
- Flag if m_i(t+) < 0

Track:
- Fraction of BUYs with m_i(t+) < 0
- Distribution of margin changes

#### 4.3 Margin at Default

For each agent that defaults:
- Record m_i(t) at time of default
- Track distribution

### Phase 5: Experiment-Level Aggregation (8.5)

#### 5.1 Extend Comparison Framework

**File:** `src/bilancio/experiments/comparison.py`

Add to comparison results:
```python
@dataclass
class EnrichedComparisonResult:
    # Existing
    kappa: float
    c: float
    mu: float
    delta_control: float
    delta_treatment: float
    phi_control: float
    phi_treatment: float
    relief_ratio: float

    # New: Dealer profitability
    dealer_pnl_by_bucket: Dict[str, float]
    dealer_return_by_bucket: Dict[str, float]
    dealer_total_pnl: float
    dealer_profitable: bool

    # New: Trader returns
    mean_trader_return: float
    fraction_profitable_traders: float
    trader_return_distribution: List[float]

    # New: Repayment priority
    fraction_unsafe_buys: float  # BUYs reducing margin below 0
    mean_margin_at_default: float

    # New: Liquidity channel
    liquidity_driven_sales: int
    rescue_events: int
```

#### 5.2 Sweep Aggregation

Extend sweep results to include:
- Mean dealer profitability across parameter space
- Correlation of dealer profitability with relief ratio
- Parameter regions where trader returns are positive
- Parameter regions with frequent margin violations

### Phase 6: Output and Reporting

#### 6.1 Metrics CSV Export

Add to report generation:
- `dealer_metrics.csv`: Per-day dealer state
- `trader_metrics.csv`: Per-day trader state
- `trade_log.csv`: All trades with enriched data
- `ticket_outcomes.csv`: Realized returns per ticket

#### 6.2 HTML Report Extension

Add sections to HTML report:
- Dealer P&L chart over time
- Spread income vs layoff cost breakdown
- Trader return distribution histogram
- Safety margin distribution
- Rescue event timeline

#### 6.3 Aggregate Dashboard

For sweeps, add:
- Heatmap of dealer profitability vs parameters
- Scatter plot: relief ratio vs dealer P&L
- Box plots of trader returns by parameter region

## File Changes Summary

### New Files
- `src/bilancio/dealer/metrics.py` - Core metric data structures and computations

### Modified Files
- `src/bilancio/engines/dealer_integration.py` - Add metrics tracking
- `src/bilancio/dealer/trading.py` - Extend ExecutionResult
- `src/bilancio/experiments/comparison.py` - Enriched comparison results
- `src/bilancio/analysis/report.py` - Export metrics to CSV/HTML

### Test Files
- `tests/dealer/test_metrics.py` - Unit tests for metrics computation
- `tests/integration/test_dealer_metrics.py` - Integration tests

## Implementation Order

1. **Phase 1.1**: Create metrics.py with data structures
2. **Phase 1.2**: Add metrics tracking to DealerSubsystem
3. **Phase 2**: Implement dealer P&L computation
4. **Phase 3**: Implement trader return tracking
5. **Phase 4**: Implement safety margin diagnostics
6. **Phase 5**: Extend comparison framework
7. **Phase 6**: Add reporting/export

## Success Criteria

1. For any dealer simulation run, we can extract:
   - Complete trade log with before/after state
   - Dealer P&L and return by bucket
   - Trader realized returns
   - Safety margin violations
   - Liquidity-driven sales count

2. For comparison experiments:
   - Enriched results include all Section 8 metrics
   - Can filter parameter regions by dealer profitability
   - Can identify "functional dealer" configurations (R > 0, Π >= 0, positive trader returns)

3. Dashboard shows:
   - Whether dealer is non-loss-making
   - Whether traders have earning opportunities
   - Whether repayment priority is respected
