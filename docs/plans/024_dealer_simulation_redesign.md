# Plan 024: Dealer Simulation Redesign

**Reference**: Instructions_for_simulation.pdf
**Status**: In Progress
**Goal**: Redesign dealer simulation for realistic dealer/VBT sizing and meaningful comparison

---

## Problem Statement

The current dealer simulation has a critical issue: dealers are too small to hold securities on their balance sheets. When trades occur, dealers immediately lay off to VBT, which impedes the dealer's ability to make markets effectively. In the last 625-run sweep:
- `dealer_empty_fraction=1.0` - dealer is **always** empty
- `dealer_active_fraction=0.0` - dealer **never** holds inventory
- Only 5 agents (too few for meaningful market structure)

## Proposed Changes (from PDF)

### 1. Balanced Initial Balance Sheets for Passive vs Active Regimes

For each maturity bucket m ∈ {short, mid, long}:
- **VBT-like passive holder**: 25% of total claims of maturity m + equal cash
- **Dealer-like passive holder**: 12.5% of total claims of maturity m + equal cash

In **passive regime**: These are large passive holders that never trade.
In **active regime**: Same balance sheets, but VBTs and dealers trade.

### 2. Many-Trader Environment

Move from N=5 to **N=100 traders**:
- Dealer and VBT become "large but few" agents
- More realistic market structure (few dealers, many traders)
- Avoids artifacts where each dealer intermediates negligible share

### 3. Default-Avoidance Trading as Sole Driver

Trader behavior driven explicitly by default avoidance:
- Each trader evaluates forward-looking liquidity gap over horizon H
- If projected shortfall exists, trader attempts to sell assets
- Traders without projected shortfall do NOT trade

### 4. Continuous Issuance via Rollover

Avoid one-shot cohort where longer-maturity claims disappear:
- Each liability records its original maturity distance ΔT
- When claim is repaid, borrower immediately issues new claim of same size/ΔT
- If claim defaults, it is NOT rolled over

### 5. Pairwise Run-by-Run Comparison

Keep paired experiment structure:
- Same initial state run twice: passive vs active
- Compare outcomes run-by-run, not just ensemble averages

### 6. No Structural Forcing

Avoid ad-hoc interventions:
- No quotas forcing debt through dealer
- No special pricing for near-default trades

---

## Implementation Plan

### Phase 1: Configuration Extensions

**File**: `src/bilancio/config/models.py`

Add new configuration for VBT/Dealer shares:

```python
class BalancedDealerConfigV2(BaseModel):
    """Configuration for balanced dealer scenarios (PDF redesign)."""

    vbt_share_per_bucket: Decimal = Field(
        default=Decimal("0.25"),
        description="VBT holds 25% of claims per maturity bucket"
    )
    dealer_share_per_bucket: Decimal = Field(
        default=Decimal("0.125"),
        description="Dealer holds 12.5% of claims per maturity bucket"
    )
    face_value: Decimal = Field(default=Decimal("20"))
    outside_mid_ratio: Decimal = Field(default=Decimal("0.75"))
    rollover_enabled: bool = Field(
        default=True,
        description="Enable continuous rollover of matured claims"
    )
```

### Phase 2: Scenario Generator Redesign

**File**: `src/bilancio/scenarios/generators/ring_explorer.py`

New function `compile_ring_explorer_v2()`:

1. Create N=100 traders with ring structure
2. For each maturity bucket m:
   - Calculate total face value Q_m for that bucket
   - Allocate 25% to VBT agent: face + matching cash
   - Allocate 12.5% to Dealer agent: face + matching cash
3. Traders keep remaining 62.5% of claims

### Phase 3: VBT/Dealer Initialization Redesign

**File**: `src/bilancio/engines/dealer_integration.py`

Modify `initialize_balanced_dealer_subsystem()`:

1. VBT starts WITH 25% of claims per bucket (not empty)
2. Dealer starts WITH 12.5% of claims per bucket (not empty)
3. Both have cash = market value of their holdings
4. This allows dealers to actually make markets

### Phase 4: Rollover Mechanism

**File**: `src/bilancio/engines/settlement_engine.py` (or new module)

Add rollover logic:
1. Track original maturity distance (ΔT) for each payable
2. When payable settles successfully:
   - Create new payable: same debtor, same creditor, same face
   - Due day = current_day + ΔT
   - Move cash from creditor to debtor (new issuance)
3. When payable defaults: NO rollover

### Phase 5: Default-Avoidance Trading Strategy

**File**: `src/bilancio/engines/dealer_integration.py`

Modify trading eligibility:
1. Remove arbitrary trading limits
2. Only traders with projected shortfall can sell
3. Compute forward liquidity gap over configurable horizon H
4. Submit SELL orders for required face amount

### Phase 6: Experiment Runner Updates

**File**: `src/bilancio/experiments/balanced_comparison.py`

Update to use new configuration:
- Default to N=100 agents
- Use new VBT/Dealer share parameters
- Enable rollover by default

---

## File Changes Summary

### Modified Files
| File | Changes |
|------|---------|
| `src/bilancio/config/models.py` | Add `BalancedDealerConfigV2` |
| `src/bilancio/scenarios/generators/ring_explorer.py` | Add `compile_ring_explorer_v2()` |
| `src/bilancio/engines/dealer_integration.py` | Redesign balanced initialization |
| `src/bilancio/engines/settlement_engine.py` | Add rollover mechanism |
| `src/bilancio/experiments/balanced_comparison.py` | Update configuration defaults |
| `src/bilancio/ui/cli.py` | Update CLI for new parameters |

### New Files
| File | Purpose |
|------|---------|
| `src/bilancio/engines/rollover.py` | Rollover mechanism (optional - could be in settlement_engine) |

---

## Success Criteria

1. **Dealer holds inventory**: `dealer_empty_fraction < 0.5` (previously was 1.0)
2. **VBT properly sized**: VBT agents start with 25% of claims per bucket
3. **N=100 traders**: Meaningful market structure
4. **Rollover works**: Claims roll over after settlement
5. **Default-avoidance trading**: Only distressed traders sell
6. **Passive vs Active comparison**: Clear measurement of trading effect

---

## Experiment Configuration

```bash
# Run the new sweep with 100 traders
uv run bilancio sweep balanced \
  --out-dir out/experiments/plan024_sweep \
  --n-agents 100 \
  --maturity-days 10 \
  --face-value 20 \
  --vbt-share 0.25 \
  --dealer-share 0.125 \
  --rollover \
  --kappas "0.25,0.5,1,2,4" \
  --concentrations "0.2,0.5,1,2,5" \
  --mus "0,0.25,0.5,0.75,1" \
  --outside-mid-ratios "1.0,0.9,0.8,0.75,0.5"
```

Total runs: 5 × 5 × 5 × 5 = 625 pairs (passive + active)
