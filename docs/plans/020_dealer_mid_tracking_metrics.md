# Plan 020: Dealer Mid Tracking and Debt-to-Money Metrics

## Overview

This plan adds three new metric categories to the dealer ring simulation:

1. **Mid price time series** (A.2): Track dealer midline and VBT mid (M) across all timepoints
2. **Discount/premium vs face value** (A.3): Measure how far current mids are from par (face value = 1)
3. **Debt-to-money ratio** (B): System-level control variable measuring total debt vs total money at simulation start

## Motivation

The existing metrics (Section 8) focus on P&L, trader returns, and safety margins. These new metrics provide:

- **Price discovery visibility**: See how dealer and VBT mids evolve over the simulation
- **Valuation context**: Understand whether securities trade at discount or premium to par
- **Liquidity control**: The debt-to-money ratio is a key control variable - results only make sense given this ratio. More money relative to debt means fewer expected defaults.

## Implementation Plan

### Phase 1: Extend DealerSnapshot with Premium/Discount

The `DealerSnapshot` dataclass already captures `midline` and `vbt_mid` at each day. We need to add computed properties for discount/premium.

**File:** `src/bilancio/dealer/metrics.py`

Add to `DealerSnapshot`:
```python
@property
def dealer_premium_vs_face(self) -> Decimal:
    """
    Dealer midline premium/discount vs face value (par = 1).

    Returns (midline - 1) as percentage.
    Positive = premium, Negative = discount.
    """
    return self.midline - Decimal(1)

@property
def dealer_premium_pct(self) -> Decimal:
    """Premium/discount as percentage: ((midline - 1) / 1) * 100"""
    return (self.midline - Decimal(1)) * 100

@property
def vbt_premium_vs_face(self) -> Decimal:
    """VBT mid premium/discount vs face value (par = 1)."""
    return self.vbt_mid - Decimal(1)

@property
def vbt_premium_pct(self) -> Decimal:
    """VBT premium/discount as percentage."""
    return (self.vbt_mid - Decimal(1)) * 100
```

Update `DealerSnapshot.to_dict()` to include these new fields.

### Phase 2: Add Debt-to-Money Ratio to RunMetrics

**File:** `src/bilancio/dealer/metrics.py`

Add new fields to `RunMetrics`:
```python
@dataclass
class RunMetrics:
    # ... existing fields ...

    # System-level initial state (Phase B metric)
    initial_total_debt: Decimal = Decimal(0)      # Sum of all payable amounts at t=0
    initial_total_money: Decimal = Decimal(0)     # Sum of all cash holdings at t=0

    @property
    def debt_to_money_ratio(self) -> Decimal:
        """
        Debt-to-money ratio at simulation start.

        This is a key control variable: results only make sense
        given the same ratio. More money = fewer expected defaults.

        Returns:
            total_debt / total_money (or 0 if no money)
        """
        if self.initial_total_money > 0:
            return self.initial_total_debt / self.initial_total_money
        return Decimal(0)
```

### Phase 3: Capture Initial Debt/Money at Initialization

**File:** `src/bilancio/engines/dealer_integration.py`

In `initialize_dealer_subsystem()`, after initializing the subsystem, compute and store initial system state:

```python
def initialize_dealer_subsystem(...) -> DealerSubsystem:
    # ... existing initialization ...

    # Phase B: Compute initial debt-to-money ratio
    # Sum all payable amounts (total debt in system)
    total_debt = Decimal(0)
    for contract in system.state.contracts.values():
        if isinstance(contract, Payable):
            total_debt += Decimal(contract.amount)

    # Sum all cash holdings (total money in system)
    total_money = Decimal(0)
    for agent_id, agent in system.state.agents.items():
        if agent.kind not in ("dealer", "vbt"):
            total_money += _get_agent_cash(system, agent_id)

    # Store in metrics
    subsystem.metrics.initial_total_debt = total_debt
    subsystem.metrics.initial_total_money = total_money

    return subsystem
```

### Phase 4: Add Mid Time Series to Summary Output

**File:** `src/bilancio/dealer/metrics.py`

Add methods to `RunMetrics` for extracting mid time series:

```python
def dealer_mid_timeseries(self) -> Dict[int, Dict[str, Decimal]]:
    """
    Extract dealer midline time series by bucket.

    Returns:
        {day: {bucket_id: midline_value}}
    """
    result: Dict[int, Dict[str, Decimal]] = {}
    for snap in self.dealer_snapshots:
        if snap.day not in result:
            result[snap.day] = {}
        result[snap.day][snap.bucket] = snap.midline
    return result

def vbt_mid_timeseries(self) -> Dict[int, Dict[str, Decimal]]:
    """
    Extract VBT mid (M) time series by bucket.

    Returns:
        {day: {bucket_id: M_value}}
    """
    result: Dict[int, Dict[str, Decimal]] = {}
    for snap in self.dealer_snapshots:
        if snap.day not in result:
            result[snap.day] = {}
        result[snap.day][snap.bucket] = snap.vbt_mid
    return result

def dealer_premium_timeseries(self) -> Dict[int, Dict[str, Decimal]]:
    """
    Extract dealer premium/discount vs face time series.

    Returns:
        {day: {bucket_id: premium_pct}}
    """
    result: Dict[int, Dict[str, Decimal]] = {}
    for snap in self.dealer_snapshots:
        if snap.day not in result:
            result[snap.day] = {}
        result[snap.day][snap.bucket] = snap.dealer_premium_pct
    return result

def vbt_premium_timeseries(self) -> Dict[int, Dict[str, Decimal]]:
    """
    Extract VBT premium/discount vs face time series.

    Returns:
        {day: {bucket_id: premium_pct}}
    """
    result: Dict[int, Dict[str, Decimal]] = {}
    for snap in self.dealer_snapshots:
        if snap.day not in result:
            result[snap.day] = {}
        result[snap.day][snap.bucket] = snap.vbt_premium_pct
    return result
```

### Phase 5: Update Summary Output

**File:** `src/bilancio/dealer/metrics.py`

Update `RunMetrics.summary()` to include new metrics:

```python
def summary(self) -> Dict[str, Any]:
    """Generate summary statistics for experiment-level aggregation."""
    return {
        # ... existing metrics ...

        # NEW: System-level control variable (Phase B)
        "initial_total_debt": float(self.initial_total_debt),
        "initial_total_money": float(self.initial_total_money),
        "debt_to_money_ratio": float(self.debt_to_money_ratio),

        # NEW: Mid price summary stats (Phase A.2, A.3)
        "dealer_mid_final": self._final_dealer_mids(),
        "vbt_mid_final": self._final_vbt_mids(),
        "dealer_premium_final_pct": self._final_dealer_premiums(),
        "vbt_premium_final_pct": self._final_vbt_premiums(),
    }

def _final_dealer_mids(self) -> Dict[str, float]:
    """Get final dealer midline by bucket."""
    result = {}
    for bucket_id in set(s.bucket for s in self.dealer_snapshots):
        bucket_snaps = [s for s in self.dealer_snapshots if s.bucket == bucket_id]
        if bucket_snaps:
            final = max(bucket_snaps, key=lambda s: s.day)
            result[bucket_id] = float(final.midline)
    return result

def _final_vbt_mids(self) -> Dict[str, float]:
    """Get final VBT mid by bucket."""
    result = {}
    for bucket_id in set(s.bucket for s in self.dealer_snapshots):
        bucket_snaps = [s for s in self.dealer_snapshots if s.bucket == bucket_id]
        if bucket_snaps:
            final = max(bucket_snaps, key=lambda s: s.day)
            result[bucket_id] = float(final.vbt_mid)
    return result

def _final_dealer_premiums(self) -> Dict[str, float]:
    """Get final dealer premium % by bucket."""
    result = {}
    for bucket_id in set(s.bucket for s in self.dealer_snapshots):
        bucket_snaps = [s for s in self.dealer_snapshots if s.bucket == bucket_id]
        if bucket_snaps:
            final = max(bucket_snaps, key=lambda s: s.day)
            result[bucket_id] = float(final.dealer_premium_pct)
    return result

def _final_vbt_premiums(self) -> Dict[str, float]:
    """Get final VBT premium % by bucket."""
    result = {}
    for bucket_id in set(s.bucket for s in self.dealer_snapshots):
        bucket_snaps = [s for s in self.dealer_snapshots if s.bucket == bucket_id]
        if bucket_snaps:
            final = max(bucket_snaps, key=lambda s: s.day)
            result[bucket_id] = float(final.vbt_premium_pct)
    return result
```

### Phase 6: Add Time Series Export

**File:** `src/bilancio/dealer/metrics.py`

Add method for full time series export:

```python
def to_mid_timeseries_csv(self, path: str) -> None:
    """
    Export mid price time series to CSV.

    Columns: day, bucket, dealer_mid, vbt_mid, dealer_premium_pct, vbt_premium_pct
    """
    import csv
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    if not self.dealer_snapshots:
        return

    fieldnames = [
        "day", "bucket",
        "dealer_midline", "vbt_mid",
        "dealer_premium_pct", "vbt_premium_pct"
    ]

    with open(path_obj, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for snap in sorted(self.dealer_snapshots, key=lambda s: (s.day, s.bucket)):
            writer.writerow({
                "day": snap.day,
                "bucket": snap.bucket,
                "dealer_midline": str(snap.midline),
                "vbt_mid": str(snap.vbt_mid),
                "dealer_premium_pct": str(snap.dealer_premium_pct),
                "vbt_premium_pct": str(snap.vbt_premium_pct),
            })
```

### Phase 7: Update Comparison Experiment Output

**File:** `src/bilancio/experiments/comparison.py`

Add new columns to `comparison.csv`:

```python
# Add to comparison result columns:
"initial_debt",
"initial_money",
"debt_to_money_ratio",
"dealer_mid_final_short",
"dealer_mid_final_mid",
"dealer_mid_final_long",
"vbt_mid_final_short",
"vbt_mid_final_mid",
"vbt_mid_final_long",
```

### Phase 8: Tests

**File:** `tests/dealer/test_metrics.py`

Add tests for new metrics:

```python
def test_dealer_premium_vs_face():
    """Test premium/discount calculation."""
    snap = DealerSnapshot(
        day=1, bucket="short", inventory=0, cash=Decimal(100),
        bid=Decimal("0.95"), ask=Decimal("1.05"), midline=Decimal("1.00"),
        vbt_mid=Decimal("0.98"), vbt_spread=Decimal("0.10"),
        ticket_size=Decimal(1)
    )
    assert snap.dealer_premium_vs_face == Decimal(0)  # At par
    assert snap.dealer_premium_pct == Decimal(0)
    assert snap.vbt_premium_vs_face == Decimal("-0.02")  # 2% discount

def test_debt_to_money_ratio():
    """Test debt-to-money ratio computation."""
    metrics = RunMetrics()
    metrics.initial_total_debt = Decimal(10000)
    metrics.initial_total_money = Decimal(5000)
    assert metrics.debt_to_money_ratio == Decimal(2)  # 2:1 debt to money
```

## File Changes Summary

### Modified Files
- `src/bilancio/dealer/metrics.py` - Add premium properties, debt-to-money fields, time series methods
- `src/bilancio/engines/dealer_integration.py` - Capture initial debt/money at init
- `src/bilancio/experiments/comparison.py` - Add new columns to comparison output

### Test Files
- `tests/dealer/test_metrics.py` - Add tests for new metrics

## Implementation Order

1. Add premium properties to `DealerSnapshot`
2. Add debt/money fields to `RunMetrics`
3. Update `initialize_dealer_subsystem()` to capture initial state
4. Add time series extraction methods
5. Update `summary()` output
6. Add CSV export for time series
7. Update comparison experiment output
8. Add tests

## Success Criteria

1. For any dealer simulation run:
   - Debt-to-money ratio is captured at simulation start
   - Dealer and VBT mid prices are tracked at every day
   - Premium/discount vs face value is computed for each snapshot

2. For comparison experiments:
   - `comparison.csv` includes `debt_to_money_ratio` column
   - Final mid prices are included for each bucket

3. New exports available:
   - `mid_timeseries.csv` with full day-by-day mid price evolution
