# Plan 024: Dealer Simulation Design Changes

## Overview

This plan redesigns the dealer simulation to create a setup where the presence of the dealer (and VBT) is both (a) realistically scaled relative to the market and (b) meaningfully comparable to a pure passive baseline. The changes respect the original version 1.0/1.5 design principle that agents are balance sheets whose actions are driven by settlement constraints, without introducing ad hoc mechanisms that force trading or special pricing regimes.

## Key Changes

### 1. Balanced Initial Balance Sheets for Passive vs Active Regimes

We want a clean "control vs treatment" design where the only difference between passive and active runs is whether the large holders are allowed to act as dealers/VBTs and whether traders are allowed to trade.

For each maturity bucket m ∈ {short, mid, long}:
- A large **VBT-like** passive holder with approximately **25%** of total claims of maturity m and an equal value of money (cash)
- A large **dealer-like** passive holder with approximately **12.5%** of total claims of maturity m and an equal value of money (cash)

In the **passive regime**, these entities are simply large passive holders that never trade.

In the **active regime**, the same balance sheets are reused, but:
- The 25% blocks become Value-Based Traders (VBTs)
- The 12.5% blocks become Dealers

**Important**: Passive and active runs start from identical balance sheets; we only switch on/off behaviour.

### 2. Many-Trader Environment

Instead of a very small number of traders (e.g., a ring of 5 households), we move to a setting with a larger population of traders: **N = 100**.

- The dealer and VBT become "large but few" agents in a market populated by many smaller traders
- The ratio of trader count to dealer/VBT agents more closely resembles a realistic market structure

This avoids artefacts where each dealer effectively intermediates a negligible or excessively concentrated part of the system.

### 3. Default-Avoidance Trading as the Sole Driver of Trades

Trader behaviour in the active regime is driven explicitly by default avoidance rather than by generic or random strategy tags.

Each trader:
1. Evaluates a forward-looking liquidity gap over horizon H (e.g., up to the longest maturity)
2. If projected cash inflows + current cash are insufficient to meet upcoming liabilities within horizon H, attempts to sell assets to close this gap
3. Traders without a projected shortfall do not trade in this baseline version

This keeps trading tightly linked to the original goal of version 1.0: meeting payment requirements in time.

### 4. Continuous Issuance via Rollover

To avoid a one-shot cohort where longer-maturity claims simply disappear as time passes, we introduce simple rollover:

- Each liability/claim pair records its original maturity distance ΔT (e.g., 1, 5, 10)
- When a claim is repaid at time t, the borrower immediately issues a new claim of the same size and maturity distance ΔT to the same holder, maturing at t + ΔT
- If a claim defaults, it is not rolled over; the corresponding relationship disappears

This produces an approximately stationary environment in which each maturity bucket remains active over time.

### 5. Pairwise Run-by-Run Comparison

We keep the paired experiment structure from earlier work, but emphasise strict comparability:

For each parameter set and random seed:
1. Build a single initial state and run it twice:
   - **Passive regime**: no trading by traders, large holders remain purely passive
   - **Active regime**: trading enabled for traders, large holders act as dealers/VBTs
2. Compare outcomes run-by-run (e.g., defaulted face value, default rates, distribution of defaults)

The presence or absence of dealers/VBTs is evaluated as the difference between these paired runs.

### 6. No Structural Forcing of Flow or Special Pricing

We explicitly avoid:
- Exogenous quotas or structural rules that "force" some fixed share of debt to trade through the dealer
- Ad hoc rescue pricing regimes where near-default trades get different spreads than others

Dealer pricing remains whatever baseline bid/ask rule the model uses; dealer activity increases only because it has a realistic balance sheet and traders genuinely need liquidity.

---

## Implementation Details

### 1. Balanced Dealer/VBT Initialization

**Files**: `src/bilancio/experiments/balanced_comparison.py`, `src/bilancio/scenarios/generators/ring_explorer.py`

Changes:
- Set `dealer_share = 0.125` (12.5% of total face value per maturity)
- Set `vbt_share = 0.25` (25% of total face value per maturity)
- Create separate dealer and VBT entities per bucket with proper inventory

### 2. Many-Trader Ring Scenario

**File**: `src/bilancio/experiments/balanced_comparison.py`

Changes:
- `n_agents = 100` (already default, confirm active)
- Ring or network structure over 100 traders
- Liabilities assigned with maturity structure (short/mid/long buckets)

### 3. Default-Avoidance Strategy

**File**: `src/bilancio/dealer/simulation.py`

New strategy module for trader agents:
- At each time step t, evaluate forward liquidity gap over configurable horizon H
- Compare projected cash inflows to projected payment obligations up to t + H
- If negative liquidity gap exceeds threshold:
  - Compute required cash to close gap
  - Translate to required face value to sell at current mid prices
  - Submit SELL orders to dealer/VBT subsystem
- No structural quota forcing trading; orders treated normally

### 4. Continuous Issuance via Rollover

**Files**: `src/bilancio/domain/instruments/credit.py`, `src/bilancio/engines/settlement.py`

Changes:
- Add `original_maturity_distance` field to Payable
- After successful settlement, create new payable with same debtor/creditor/amount
- New due_day = current_day + original_maturity_distance
- Defaulted liabilities are NOT rolled over

### 5. Sweep Parameters

For the parameter sweep:
- N = 100 agents
- Maturity days = 10
- κ: 0.25, 0.5, 1, 2, 4
- c: 0.2, 0.5, 1, 2, 5
- μ: 0, 0.25, 0.5, 0.75, 1
- outside_mid_ratio: 1.0, 0.9, 0.8, 0.75, 0.5
- dealer_share: 0.125
- vbt_share: 0.25
- 625 total parameter combinations

---

## Files Modified

1. `src/bilancio/experiments/balanced_comparison.py` - Update dealer/VBT shares
2. `src/bilancio/scenarios/generators/ring_explorer.py` - Add dealer/VBT entity initialization
3. `src/bilancio/dealer/simulation.py` - Add default-avoidance trading strategy
4. `src/bilancio/domain/instruments/credit.py` - Add original_maturity_distance field
5. `src/bilancio/engines/settlement.py` - Add rollover logic after settlement

---

## Expected Outcomes

1. **Realistic dealer presence**: Dealer has meaningful inventory (12.5%) rather than acting as pure passthrough
2. **Active VBT**: VBT holds 25% of claims and provides meaningful liquidity
3. **Default-driven trading**: Trading occurs only when agents face liquidity constraints
4. **Stationary environment**: Rollover maintains active maturity buckets over time
5. **Clean comparison**: Passive and active runs differ only in behaviour, not initial state
