# Plan 022: Enhanced Instrumentation for Dealer Ring Experiments

**Reference**: Conversation 20251205.txt
**Status**: Draft
**Goal**: Add detailed logging to understand *why* dealers help (or don't help) reduce defaults

---

## Context

We've run 250 simulation pairs comparing passive (C) vs active (D) regimes. Results show:
- Some parameter combinations show improvement with trading
- 108 pairs show NO difference between active/passive
- We don't understand *why* - need detailed logs to diagnose

## What We Have vs What We Need

### Already Implemented
- ✅ `outside_mid_ratio` as a sweep parameter (1.5 - DONE)
- ✅ Basic trade records in memory (`TradeRecord` class)
- ✅ Dealer snapshots (`DealerSnapshot` class)
- ✅ C vs D comparison infrastructure

### Need to Implement

| Item | Output File | Purpose |
|------|-------------|---------|
| 1.1 | `trades.csv` | Per-trade log with run_id, regime, VBT trigger flag |
| 1.2 | `repayment_events.csv` | Link trader liabilities to trading strategies and outcomes |
| 1.3 | `inventory_timeseries.csv` | Dealer capacity utilization over time |
| 1.4 | `system_state_timeseries.csv` | Total debt/money evolution |

---

## Phase 1: Enhanced Trade Logging (1.1)

### Goal
Write a `trades.csv` per run with ALL the fields needed for analysis.

### Changes Required

#### 1.1.1 Extend `TradeRecord` (in `dealer/metrics.py`)
Add fields:
```python
run_id: str = ""              # e.g., "grid_abc123"
regime: str = ""              # "passive" or "active"
outside_mid: Decimal = Decimal(0)  # VBT mid price at trade time
dealer_mid: Decimal = Decimal(0)   # Dealer midline at trade time
hit_inventory_limit: bool = False  # Was VBT used because dealer at limit?
```

Note: `hit_inventory_limit` is different from `is_passthrough`:
- `is_passthrough=True` means trade went to VBT
- `hit_inventory_limit=True` means VBT was used *because* dealer was at capacity

#### 1.1.2 Update trade execution (in `dealer/trading.py`)
When executing a trade, detect if dealer is at capacity:
- For SELL: dealer at max inventory
- For BUY: dealer at 0 inventory

Set `hit_inventory_limit=True` when this causes VBT routing.

#### 1.1.3 Write `trades.csv` after each run
In the experiment runner, call:
```python
metrics.to_trade_log_csv(run_dir / "trades.csv")
```

Already exists: `RunMetrics.to_trade_log_csv()` - just need to ensure it's called.

### Fields in trades.csv
```
run_id, regime, day, bucket, side, trader_id, ticket_id, issuer_id,
maturity_day, face_value, price, unit_price, is_passthrough,
outside_mid, dealer_mid, dealer_inventory_before, dealer_inventory_after,
hit_inventory_limit, trader_cash_before, trader_cash_after,
trader_safety_margin_before, trader_safety_margin_after,
is_liquidity_driven, reduces_margin_below_zero
```

---

## Phase 2: Repayment Events Tracking (1.2)

### Goal
For each (trader, liability) pair, track how trading affected the outcome.

### New Data Structure

#### 2.1 Create `RepaymentEvent` dataclass (in `dealer/metrics.py`)
```python
@dataclass
class RepaymentEvent:
    """Track how a trader managed a specific liability."""
    run_id: str
    regime: str
    trader_id: str
    liability_id: str          # Ticket ID representing the debt
    maturity_day: int
    face_value: Decimal

    # Outcome
    outcome: str               # "repaid" | "defaulted"

    # Trading activity with dealer BEFORE this maturity
    buy_count: int = 0         # Number of BUY trades
    sell_count: int = 0        # Number of SELL trades
    net_cash_pnl: Decimal = Decimal(0)  # Net cash from trading

    # Strategy classification
    held_matching_maturity: bool = False  # Ever held security maturing same day?
    strategy: str = ""         # "hold_to_maturity" | "sell_before" | "round_trip" | "no_trade"
```

#### 2.2 Populate during simulation
In the settlement phase, for each liability:
1. Look up all trades by this trader before this maturity day
2. Count buys/sells
3. Check if they ever held a matching-maturity ticket
4. Classify strategy
5. Record outcome (repaid/defaulted)

#### 2.3 Write `repayment_events.csv`
New method: `RunMetrics.to_repayment_events_csv()`

### Strategy Classification Logic
```python
def classify_strategy(buy_count, sell_count, held_matching):
    if buy_count == 0 and sell_count == 0:
        return "no_trade"
    elif held_matching and sell_count == 0:
        return "hold_to_maturity"
    elif buy_count > 0 and sell_count > 0:
        if sell_count >= buy_count:
            return "round_trip"
        else:
            return "sell_before"
    elif sell_count > 0:
        return "sell_before"
    else:
        return "hold_to_maturity"
```

---

## Phase 3: Inventory Timeseries (1.3)

### Goal
Track dealer capacity utilization over time to see "emptying out" dynamics.

### Changes Required

#### 3.1 Extend `DealerSnapshot` (in `dealer/metrics.py`)
Add fields:
```python
max_capacity: int = 0         # K* - max inventory
capacity_pct: Decimal = Decimal(0)  # inventory / max_capacity
is_at_zero: bool = False      # inventory == 0?
hit_vbt_this_step: bool = False  # Did we route to VBT this step?
total_system_face: Decimal = Decimal(0)  # Total face value in system
dealer_share_pct: Decimal = Decimal(0)  # % held by dealer/VBT
```

#### 3.2 Compute these during snapshot creation
In `dealer/simulation.py` where snapshots are created, add:
- Query dealer state for K* (max capacity)
- Compute % utilized
- Track VBT routing events per step
- Query total outstanding debt

#### 3.3 Write `inventory_timeseries.csv`
New method: `RunMetrics.to_inventory_timeseries_csv()`

### Fields in inventory_timeseries.csv
```
run_id, regime, day, bucket,
dealer_inventory, max_capacity, capacity_pct,
is_at_zero, hit_vbt_this_step,
total_system_face, dealer_share_pct
```

---

## Phase 4: System State Timeseries (1.4)

### Goal
Track how total debt/money evolves over time (not just initial).

### New Data Structure

#### 4.1 Create `SystemStateSnapshot` (in `dealer/metrics.py`)
```python
@dataclass
class SystemStateSnapshot:
    """System-level state at a point in time."""
    run_id: str
    regime: str
    day: int

    # Total face value outstanding
    total_face_value: Decimal        # All maturities
    face_by_bucket: Dict[str, Decimal]  # Per bucket

    # Total cash in system
    total_cash: Decimal

    # Ratio
    debt_to_money: Decimal
```

#### 4.2 Capture at end of each day
In the simulation event loop, after all phases complete for a day:
1. Sum all outstanding ticket face values
2. Sum all agent cash holdings
3. Create snapshot

#### 4.3 Write `system_state_timeseries.csv`
New method: `RunMetrics.to_system_state_csv()`

### Fields in system_state_timeseries.csv
```
run_id, regime, day,
total_face_value, face_bucket_short, face_bucket_mid, face_bucket_long,
total_cash, debt_to_money
```

---

## Phase 5: Integration with Experiment Runner

### 5.1 Pass run_id and regime to simulation
The experiment runner knows the run_id and regime ("passive"/"active").
Pass these to the simulation so they can be recorded in all metrics.

### 5.2 Enable detailed logging via config flag
Add to `BalancedComparisonConfig`:
```python
detailed_logging: bool = False  # Enable trades.csv, repayment_events.csv, etc.
```

When enabled, write all the CSV files per run.

### 5.3 Update `BalancedComparisonRunner` to write CSVs
After each run completes, if `detailed_logging=True`:
```python
metrics.to_trade_log_csv(run_dir / "trades.csv")
metrics.to_repayment_events_csv(run_dir / "repayment_events.csv")
metrics.to_inventory_timeseries_csv(run_dir / "inventory_timeseries.csv")
metrics.to_system_state_csv(run_dir / "system_state_timeseries.csv")
```

---

## Implementation Order

| Priority | Task | Complexity | Dependencies |
|----------|------|------------|--------------|
| 1 | Phase 1: Enhanced trade logging | Medium | None |
| 2 | Phase 3: Inventory timeseries | Medium | None |
| 3 | Phase 4: System state timeseries | Low | None |
| 4 | Phase 5: Integration | Low | Phases 1, 3, 4 |
| 5 | Phase 2: Repayment events | High | Most complex - do last |

Phases 1, 3, 4 can be done in parallel. Phase 2 is most complex because it requires linking trades to liabilities.

---

## Testing

1. **Unit tests** for new dataclasses and methods
2. **Integration test**: Run a small sweep with `detailed_logging=True`, verify all CSVs written correctly
3. **Validation**: Check that `trades.csv` has expected number of rows (matches trade count in metrics)

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/bilancio/dealer/metrics.py` | Add fields to TradeRecord, DealerSnapshot; add RepaymentEvent, SystemStateSnapshot; add export methods |
| `src/bilancio/dealer/trading.py` | Set `hit_inventory_limit` flag on trades |
| `src/bilancio/dealer/simulation.py` | Capture system state snapshots; pass run_id/regime |
| `src/bilancio/experiments/balanced_comparison.py` | Add `detailed_logging` config; write CSV files |
| `tests/dealer/test_metrics.py` | Test new dataclasses and export methods |

---

## After Implementation: Analysis Tasks (Section 2)

Once logging is in place, these Python/notebook tasks become possible:

1. **Explain "no difference" cases**: Check if traders who default ever traded with dealer
2. **Quantify horizons**: Plot dealer inventory vs remaining debt stock
3. **Characterize strategies**: Classify by hold-to-maturity vs sell-before vs round-trip
4. **Relate to initial conditions**: Bucket traders by initial cash/debt ratio

These are post-processing tasks on the CSV files - no code changes needed.
