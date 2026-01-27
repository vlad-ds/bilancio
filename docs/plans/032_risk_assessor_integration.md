# Plan 032: RiskAssessor Integration

## Overview

Integrate the existing `RiskAssessor` module into the dealer trading flow to enable rational trader decision-making based on default probabilities and expected values.

**Current State**: The `RiskAssessor` class exists in `src/bilancio/dealer/risk_assessment.py` with full implementation and tests, but is not wired into the simulation.

**Goal**: Traders will use risk assessment to decide whether to accept dealer prices, rather than blindly executing all eligible trades.

---

## Integration Points

### 1. Initialization (DealerSubsystem)

**File**: `src/bilancio/engines/dealer_integration.py`

**Changes**:
- Add `risk_assessor: RiskAssessor | None` field to `DealerSubsystem` dataclass
- Add `risk_params: RiskAssessmentParams | None` parameter to `initialize_dealer_subsystem()`
- Instantiate `RiskAssessor` during subsystem initialization

```python
# In DealerSubsystem dataclass (line ~95)
risk_assessor: RiskAssessor | None = None

# In initialize_dealer_subsystem() (line ~113)
def initialize_dealer_subsystem(
    ...
    risk_params: RiskAssessmentParams | None = None,
) -> DealerSubsystem:
    ...
    risk_assessor = RiskAssessor(risk_params) if risk_params else None
    return DealerSubsystem(..., risk_assessor=risk_assessor)
```

### 2. History Updates (Settlement Phase)

**File**: `src/bilancio/dealer/simulation.py`

**Location**: `_settle_issuer()` method (lines ~1012-1107)

**Changes**: After each settlement, call `risk_assessor.update_history()` to record the outcome.

```python
# After determining recovery_rate and processing settlement:
if self.risk_assessor:
    defaulted = recovery_rate < Decimal(1)
    self.risk_assessor.update_history(
        day=self.day,
        issuer_id=issuer_id,
        defaulted=defaulted
    )
```

**Note**: Must be called for ALL settlements (both successful and defaults) to maintain accurate statistics.

### 3. SELL Decision Logic

**File**: `src/bilancio/dealer/simulation.py`

**Location**: `_process_sell()` method (lines ~804-861)

**Current behavior**: Trader with shortfall sells ticket at whatever price dealer offers.

**New behavior**: Trader evaluates whether dealer's bid price is acceptable given:
- Expected value of holding ticket to maturity
- Liquidity urgency (shortfall relative to wealth)
- Risk premium threshold

```python
def _process_sell(self, trader: TraderState) -> TradeResult | None:
    ticket = self._select_ticket_to_sell(trader)
    bucket_id = self._get_bucket_for_ticket(ticket)
    dealer = self.dealers[bucket_id]

    # NEW: Risk-based decision
    if self.risk_assessor:
        asset_value = sum(
            self.risk_assessor.expected_value(t, self.day)
            for t in trader.tickets_owned
        )
        if not self.risk_assessor.should_sell(
            ticket=ticket,
            dealer_bid=dealer.bid,
            current_day=self.day,
            trader_cash=trader.cash,
            trader_shortfall=trader.shortfall(self.day),
            trader_asset_value=asset_value,
        ):
            # Trader rejects price - log event and return None
            self._log_rejected_sell(trader, ticket, dealer.bid)
            return None

    # Execute trade (existing code)
    result = self.executor.execute_customer_sell(...)
    ...
```

### 4. BUY Decision Logic

**File**: `src/bilancio/dealer/simulation.py`

**Location**: `_process_buy()` method (lines ~862-927)

**Current behavior**: Trader with cash buffer buys at whatever price dealer asks.

**New behavior**: Trader evaluates whether dealer's ask price is acceptable given expected value.

```python
def _process_buy(self, trader: TraderState, bucket_id: BucketId) -> TradeResult | None:
    dealer = self.dealers[bucket_id]

    # NEW: Pre-check risk assessment (approximate - actual ticket unknown until execution)
    if self.risk_assessor:
        # Use VBT mid as proxy for expected face value
        expected_face = Decimal(1)  # Normalized
        approx_ev = (Decimal(1) - self.risk_assessor.estimate_default_prob(
            issuer_id=None,  # System-wide rate
            current_day=self.day
        )) * expected_face

        # Quick reject if ask price is clearly too high
        if dealer.ask > approx_ev * (Decimal(1) + self.risk_assessor.params.base_risk_premium):
            # May still proceed - final check after knowing actual ticket
            pass

    # Execute trade (existing code)
    result = self.executor.execute_customer_buy(...)

    # NEW: Post-execution validation
    if result and result.ticket and self.risk_assessor:
        asset_value = sum(
            self.risk_assessor.expected_value(t, self.day)
            for t in trader.tickets_owned
        )
        if not self.risk_assessor.should_buy(
            ticket=result.ticket,
            dealer_ask=result.price / result.ticket.face,  # Unit price
            current_day=self.day,
            trader_cash=trader.cash,
            trader_shortfall=trader.shortfall(self.day),
            trader_asset_value=asset_value,
        ):
            # Trader rejects - must reverse transaction
            self._reverse_buy(result, trader, dealer)
            self._log_rejected_buy(trader, result.ticket, result.price)
            return None

    return result
```

**Alternative approach**: Pre-filter eligible buyers more strictly to avoid transaction reversal.

### 5. Simulation Class Updates

**File**: `src/bilancio/dealer/simulation.py`

**Changes to `DealerRingSimulation.__init__()`**:
- Accept optional `risk_assessor: RiskAssessor` parameter
- Store as instance attribute

```python
def __init__(
    self,
    ...
    risk_assessor: RiskAssessor | None = None,
):
    ...
    self.risk_assessor = risk_assessor
```

### 6. Event Logging

**File**: `src/bilancio/dealer/events.py`

**New event types**:
- `EventType.SELL_REJECTED` - trader rejected dealer bid
- `EventType.BUY_REJECTED` - trader rejected dealer ask

```python
class EventType(Enum):
    ...
    SELL_REJECTED = 21  # Trader rejected sell at dealer bid
    BUY_REJECTED = 22   # Trader rejected buy at dealer ask
```

**Event payload**:
```python
{
    "trader_id": str,
    "bucket_id": str,
    "offered_price": float,
    "expected_value": float,
    "threshold": float,
    "reason": "price_below_ev" | "premium_too_low",
}
```

---

## Configuration

### New Parameters

Add to scenario YAML schema:

```yaml
dealer:
  risk_assessment:
    enabled: true
    lookback_window: 5        # Days of history to consider
    smoothing_alpha: 1.0      # Laplace smoothing (higher = more conservative)
    base_risk_premium: 0.02   # 2% minimum premium to trade
    urgency_sensitivity: 0.10 # How much shortfall reduces threshold
    use_issuer_specific: false # Per-issuer vs system-wide rates
    buy_premium_multiplier: 2.0 # Buyers require higher premium
```

### Default Behavior

- If `risk_assessment.enabled: false` or section omitted: current behavior (all eligible trades execute)
- If `risk_assessment.enabled: true`: traders use risk assessment for decisions

---

## Implementation Order

### Phase 1: Core Integration (Low Risk)

1. **Add RiskAssessor to DealerSubsystem** (`dealer_integration.py`)
   - Add field and parameter
   - Pass through to simulation

2. **Wire history updates** (`simulation.py`)
   - Call `update_history()` in `_settle_issuer()`
   - Verify history accumulates correctly

3. **Add unit tests** for history tracking

### Phase 2: Sell Decision Logic

4. **Implement SELL filtering** (`simulation.py`)
   - Add `should_sell()` check in `_process_sell()`
   - Add rejection event logging
   - Handle edge cases (no risk assessor, first day with no history)

5. **Add unit tests** for sell decisions

### Phase 3: Buy Decision Logic

6. **Implement BUY filtering** (`simulation.py`)
   - Add `should_buy()` check in `_process_buy()`
   - Implement transaction reversal OR pre-filtering
   - Add rejection event logging

7. **Add unit tests** for buy decisions

### Phase 4: Configuration & Polish

8. **Add YAML configuration** support
   - Parse `risk_assessment` section
   - Validate parameters

9. **Add integration tests**
   - Full simulation with risk assessment enabled
   - Compare outcomes vs disabled

---

## Testing Strategy

### Unit Tests

**File**: `tests/dealer/test_risk_integration.py` (new)

#### Test Cases: History Tracking

```python
def test_history_updated_on_settlement():
    """RiskAssessor.update_history() called after each settlement."""

def test_history_updated_on_default():
    """Defaults are recorded with defaulted=True."""

def test_history_not_updated_when_disabled():
    """No calls when risk_assessor is None."""
```

#### Test Cases: Sell Decisions

```python
def test_sell_accepted_when_price_above_ev():
    """Trade executes when dealer bid >= EV + threshold."""

def test_sell_rejected_when_price_below_ev():
    """Trade rejected when dealer bid < EV + threshold."""

def test_sell_accepted_under_urgency():
    """Urgent trader accepts lower price (threshold reduced)."""

def test_sell_always_accepted_when_disabled():
    """All sells execute when risk_assessor is None."""

def test_sell_rejection_logged():
    """SELL_REJECTED event logged with correct payload."""
```

#### Test Cases: Buy Decisions

```python
def test_buy_accepted_when_ev_above_price():
    """Trade executes when EV >= price + threshold."""

def test_buy_rejected_when_ev_below_price():
    """Trade rejected when EV < price + threshold."""

def test_buy_reversal_restores_state():
    """Transaction reversal correctly restores dealer/trader state."""

def test_buy_rejection_logged():
    """BUY_REJECTED event logged with correct payload."""
```

#### Test Cases: Edge Cases

```python
def test_first_day_no_history():
    """Uses prior default rate (5%) when no history."""

def test_lookback_window_respected():
    """Only recent history within window affects estimates."""

def test_issuer_specific_mode():
    """Per-issuer tracking when enabled."""

def test_desperate_trader_accepts_any_price():
    """Threshold goes negative when wealth near zero."""
```

### Integration Tests

**File**: `tests/integration/test_risk_assessment_e2e.py` (new)

```python
def test_risk_assessment_reduces_trade_volume():
    """Fewer trades when risk assessment is enabled vs disabled."""

def test_risk_assessment_improves_trader_outcomes():
    """Traders with risk assessment have higher final wealth on average."""

def test_risk_assessment_responds_to_defaults():
    """After defaults, traders become more conservative (higher thresholds)."""

def test_full_simulation_with_risk_assessment():
    """Complete ring simulation runs without errors."""
```

### Regression Tests

**File**: `tests/dealer/test_simulation.py` (existing)

Add cases to verify existing behavior unchanged when risk assessment disabled:

```python
def test_trading_unchanged_without_risk_assessment():
    """Simulation produces identical results when risk_assessor=None."""
```

---

## QA Checklist

### Functional Verification

- [ ] RiskAssessor instantiated when config provided
- [ ] History updated after every settlement (success and default)
- [ ] `should_sell()` correctly filters trades
- [ ] `should_buy()` correctly filters trades
- [ ] Rejection events logged with correct data
- [ ] Transaction reversal (if used) correctly restores state
- [ ] Configuration parsed from YAML correctly
- [ ] Default behavior unchanged when disabled

### Edge Cases

- [ ] First simulation day (no history) uses prior rate
- [ ] Lookback window of 0 days still works
- [ ] Empty eligible sets handled gracefully
- [ ] All traders reject (zero trades) doesn't crash
- [ ] Very high/low threshold values work
- [ ] Issuer-specific mode tracks per-issuer correctly

### Performance

- [ ] No significant slowdown with risk assessment enabled
- [ ] History doesn't grow unbounded (or is pruned appropriately)
- [ ] Asset value computation (sum of EVs) is efficient

### Backwards Compatibility

- [ ] Existing scenarios without `risk_assessment` config work
- [ ] CLI commands work with/without risk assessment
- [ ] HTML output shows rejection events (if any)
- [ ] Metrics computation handles rejection events

### Documentation

- [ ] YAML config example in docs
- [ ] Parameter descriptions in docstrings
- [ ] Update CLAUDE.md if needed

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Transaction reversal is complex | Medium | Alternative: pre-filter buyers by expected value |
| All trades rejected in stressed scenarios | High | Add minimum trade guarantee or cap rejection rate |
| Performance impact from EV computation | Low | Cache EV values per day, compute once per trader |
| History growth over long simulations | Low | Prune history beyond 2x lookback window |

---

## Success Criteria

1. **Correctness**: Traders make rational decisions consistent with `should_sell()`/`should_buy()` logic
2. **Observability**: Rejection events visible in event log and HTML output
3. **Configurability**: Risk parameters tunable via YAML
4. **Backwards Compatible**: Disabled by default, existing behavior preserved
5. **Tested**: >90% coverage on new code, integration tests pass

---

## Estimated Scope

- **Files modified**: 4-5 (simulation.py, dealer_integration.py, events.py, config/loaders.py)
- **Files created**: 2-3 (test files)
- **Lines of code**: ~200-300 new lines
- **Test cases**: ~20-25 new tests
