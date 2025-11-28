# Dealer Integration Fixes (2025-11-28)

This document records the debugging session that made dealer-mediated secondary markets functional in the Kalecki ring simulations.

## Context

Plan 016 had implemented the dealer subsystem infrastructure, but when running comparison experiments (Plan 018), control and treatment runs produced identical results - the dealer wasn't actually reducing defaults.

## Issues Encountered and Fixes

### Issue 1: Trader Cash Not Synced

**Symptom:** No trades occurring despite eligible sellers existing.

**Root Cause:** In `initialize_dealer_subsystem`, trader cash was initialized to 0:
```python
trader = TraderState(agent_id=agent_id, cash=Decimal(0), ...)
```

**Fix:** Added `_get_agent_cash()` helper and sync trader cash from main system:
```python
def _get_agent_cash(system, agent_id: str) -> Decimal:
    agent = system.state.agents.get(agent_id)
    total_cash = Decimal(0)
    for contract_id in agent.asset_ids:
        contract = system.state.contracts.get(contract_id)
        if contract and contract.kind == "cash":
            total_cash += Decimal(contract.amount)
    return total_cash

# In initialize_dealer_subsystem:
trader_cash = _get_agent_cash(system, agent_id)
trader = TraderState(agent_id=agent_id, cash=trader_cash, ...)

# In run_dealer_trading_phase (start of phase):
for trader_id, trader in subsystem.traders.items():
    trader.cash = _get_agent_cash(system, trader_id)
```

### Issue 2: Wrong Attribute Name in Sync

**Symptom:** Ownership transfers not reflected in main system.

**Root Cause:** `sync_dealer_to_system` used `payable.holder_id` but the Payable class uses `asset_holder_id`:
```python
# Wrong:
payable.holder_id = ticket.owner_id
# Correct:
payable.asset_holder_id = new_holder
```

**Fix:** Use correct attribute name and also update agent `asset_ids` lists:
```python
if current_holder != new_holder:
    old_holder_agent = system.state.agents.get(current_holder)
    new_holder_agent = system.state.agents.get(new_holder)

    if old_holder_agent and payable_id in old_holder_agent.asset_ids:
        old_holder_agent.asset_ids.remove(payable_id)
    if new_holder_agent and payable_id not in new_holder_agent.asset_ids:
        new_holder_agent.asset_ids.append(payable_id)

    payable.asset_holder_id = new_holder
```

### Issue 3: Dealer/VBT Agents Not in Main System

**Symptom:** KeyError when settlement tries to look up `dealer_short` in `system.state.agents`.

**Root Cause:** When a claim transfers to dealer/VBT, the `asset_holder_id` becomes `"dealer_short"` etc., but settlement code does:
```python
asset_holder = system.state.agents[contract.asset_holder_id]  # KeyError!
```

**Fix:** Create placeholder Household agents for dealer/VBT in main system:
```python
# In initialize_dealer_subsystem:
for bucket_config in dealer_config.buckets:
    bucket_id = bucket_config.name
    dealer_agent_id = f"dealer_{bucket_id}"
    vbt_agent_id = f"vbt_{bucket_id}"

    if dealer_agent_id not in system.state.agents:
        dealer_agent = Household(id=dealer_agent_id, name=f"Dealer ({bucket_id})", kind="household")
        system.state.agents[dealer_agent_id] = dealer_agent

    if vbt_agent_id not in system.state.agents:
        vbt_agent = Household(id=vbt_agent_id, name=f"VBT ({bucket_id})", kind="household")
        system.state.agents[vbt_agent_id] = vbt_agent
```

### Issue 4: Price Not Scaled by Face Value

**Symptom:** Trades executing but `Cash Minted: $0` to seller.

**Root Cause:** Dealer module returns unit prices (e.g., B=0.85 per unit of face value), but integration layer used raw price:
```python
trader.cash += result.price  # result.price is unit price ~0.85
```

For a $4,515 face value ticket, the total price should be $4,515 × 0.85 = $3,837.75, not $0.85.

**Fix:** Scale price by ticket face value:
```python
scaled_price = result.price * ticket.face
trader.cash += scaled_price
```

### Issue 5: Initial Inventory Given to Dealer/VBT

**Symptom:** Claims transferring from `vbt_mid` to `vbt_short` at start of simulation.

**Root Cause:** CLI defaults had `dealer_share=0.25` and `vbt_share=0.50`, meaning 75% of claims were given to dealer/VBT at initialization.

**Fix:** Changed CLI defaults to 0 for fair comparison:
```python
@click.option('--dealer-share', type=float, default=0.0, ...)
@click.option('--vbt-share', type=float, default=0.0, ...)
```

### Issue 6: Too Few Trades Per Phase

**Symptom:** Only 1-3 trades across entire simulation.

**Root Cause:**
- Eligibility horizon was 3 days (too short for 10-day maturities)
- Trade limit was 3 per phase

**Fix:**
```python
horizon = 10  # Was 3
for trader_id in eligible_sellers[:10]:  # Was [:3]
```

### Issue 7: Buying Causing Problems

**Symptom:** Some scenarios showed dealer making defaults worse.

**Root Cause:** Buyers were spending cash they needed for their own settlements.

**Fix:** Disabled buying entirely (commented out buyer eligibility):
```python
eligible_buyers = []  # Disabled - buying can hurt liquidity
```

## Final Test Results

After all fixes, comprehensive test with 20 agents, 10-day maturity:

| Metric | Value |
|--------|-------|
| Mean relief ratio | 17.1% |
| Best result | 68.8% reduction (κ=1, c=2, μ=0.5) |
| Pairs improved | 11/18 (61%) |

## Files Modified

- `src/bilancio/engines/dealer_integration.py` - Main fixes
- `src/bilancio/experiments/comparison.py` - Default config values
- `src/bilancio/ui/cli.py` - CLI default values
- `docs/plans/018_dealer_comparison_experiments.md` - Updated with results

## Commits

```
1f61ae2 fix(dealer): Complete dealer integration with proper trading mechanics
c814677 docs: Update Plan 018 with test results and mark COMPLETE
```
