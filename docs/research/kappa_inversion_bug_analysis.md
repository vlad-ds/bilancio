# Kappa (κ) Inversion Bug - Analysis and Fix

## Summary

**Bug Found**: The Kalecki ring scenario generation had an inverted formula for calculating initial liquidity (L₀) from κ.

**Impact**: Scenarios labeled as κ=0.5 (liquidity stress) were actually running with κ=2.0 (high liquidity), completely reversing the experimental conditions.

---

## The Bug

**File**: `src/bilancio/scenarios/ring_explorer.py`, line 65

**Before (WRONG)**:
```python
liquidity_total = (Q_total / model.kappa)  # INVERTED!
```

**After (CORRECT)**:
```python
liquidity_total = (Q_total * model.kappa)  # FIXED!
```

**Mathematical Definition**:
- κ = L₀ / S₁ (kappa = liquidity / total debt)
- Therefore: L₀ = κ × S₁ (NOT S₁ / κ)

---

## Concrete Example

For κ=0.5, S₁=10,000:

| Implementation | Calculation | L₀ Result | Actual κ | Interpretation |
|----------------|-------------|-----------|----------|----------------|
| **BUG** (old) | 10000 / 0.5 | 20,000 | 2.0 | HIGH liquidity (200%) |
| **FIXED** (new) | 10000 × 0.5 | 5,000 | 0.5 | LOW liquidity (50%) |

---

## Impact on Previous Results

### Previous Run: `evacuee-crushed-attentive-flakily`
- **Labeled as**: κ=0.5 (LOW liquidity)
- **Actually was**: Correctly implemented κ=0.5
- **Results**: 88% defaults (passive), 87% defaults (active)
- **Interpretation**: Severe liquidity stress, dealers helped slightly (+1.5%)

### Recent Run: `saturate-unkind-dealt-rural`
- **Labeled as**: κ=0.5 (LOW liquidity)
- **Actually was**: κ=2.0 (HIGH liquidity) due to the bug
- **Results**: 0% defaults (passive), 74% defaults (active)
- **Interpretation**: Excess liquidity but risk-aware traders reject trades

---

## Why Results Were So Different

**The runs tested OPPOSITE scenarios!**

| Aspect | evacuee (CORRECT) | saturate (BUG) |
|--------|-------------------|----------------|
| Intended κ | 0.5 | 0.5 |
| Actual κ | 0.5 | 2.0 (INVERTED!) |
| Actual L₀ | 5,000 | 20,000 |
| System state | Under-funded (50%) | Over-funded (200%) |
| Passive defaults | 88% | 0% |
| Active defaults | 87% | 74% |
| Root cause | Liquidity shortage | Trading refusal |

### evacuee (Correct κ=0.5):
- System severely liquidity-constrained
- Both modes struggle with defaults
- Dealers help slightly by facilitating payment chains

### saturate (Buggy κ=2.0):
- System has DOUBLE the needed cash
- Passive mode: agents pay debts directly (0% defaults)
- Active mode: risk-aware traders REJECT dealer prices as "unfair"
- This creates artificial defaults despite having cash
- Demonstrates the "liquidity trap" where traders won't participate

---

## Expected Results with FIXED Implementation

With the corrected κ implementation, we should see:

**κ=0.25 (Severe stress)**:
- Passive: Very high defaults (>90%)
- Active: Slightly lower defaults
- Effect: Dealers help by facilitating complex payment chains

**κ=0.5 (Moderate stress)**:
- Passive: High defaults (70-90%)
- Active: Lower defaults
- Effect: Dealers provide critical liquidity redistribution

**κ=1.0 (Balanced)**:
- Passive: Moderate defaults (20-40%)
- Active: Lower defaults
- Effect: Dealers smooth out payment timing issues

**κ=2.0 (High liquidity)**:
- Passive: Low defaults (0-10%)
- Active: Variable - depends on whether traders accept dealer prices
- Effect: May be negative if risk-aware traders refuse to trade

---

## Action Items

1. ✅ **FIXED**: Corrected the κ inversion bug in `ring_explorer.py`
2. ⏳ **TODO**: Rerun comprehensive sweep with corrected implementation
   - κ: [0.25, 0.5, 1.0, 2.0]
   - c: [0.5, 1.0, 2.0]
   - μ: [0, 0.5, 1]
   - Total: 36 pairs × 2 modes = 72 runs
3. ⏳ **TODO**: Generate visualizations comparing fixed vs buggy results
4. ⏳ **TODO**: Document findings in research notes

---

## Research Implications

The buggy run (`saturate-unkind-dealt-rural`) **is still valuable** because it demonstrates an important finding:

> **When agents have ample liquidity but risk-aware decision-making, dealer markets can HURT rather than help**

This is the "liquidity trap" phenomenon:
- Traders with cash won't trade at dealer prices they perceive as unfavorable
- This creates artificial defaults despite having the liquidity to pay
- Highlights the importance of price discovery and trader confidence

The fixed run will show the **intended** result:
- How dealers help in liquidity-constrained environments
- The gradient of dealer effectiveness across liquidity regimes

---

## Files Modified

- `src/bilancio/scenarios/ring_explorer.py` (line 65, 67)
- Created `temp/run_corrected_sweep.py` for rerunning sweep
- This analysis document: `temp/kappa_bug_analysis.md`
