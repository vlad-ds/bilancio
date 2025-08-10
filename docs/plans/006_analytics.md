awesome — I reviewed the codebase you sent. You’ve already shipped reserves, Phase B settlement, Phase C clearing, and a simple day scheduler with good tests. The next bite‑sized, high‑leverage step is: **add balance‑sheet / trial‑balance analytics** (read‑only), plus a tiny invariant hardening. This adds immediate observability without touching core flows.

# Next Step (single PR): Balance‑Sheet & Trial‑Balance Analytics (+ tiny invariant)

## Why this now

* You already have a complete day loop (A→B→C) and events; analysis is the missing “dashboard” to understand states after each step. The `analysis` package is a placeholder today.&#x20;
* System invariants are good (presence on both sides, CB counters, non‑negatives), but there’s no **balance‑sheet view per agent** or a **trial balance** across the system, and we aren’t guarding against **duplicate instrument IDs** in agent lists yet.&#x20;

---

# Scope (Definition of Done)

1. New module `analysis/balances.py` with:

   * `agent_balance(system, agent_id) -> AgentBalance`
   * `system_trial_balance(system) -> TrialBalance`
   * `as_rows(system) -> list[dict]` (optional) to render a tidy, testable table.

2. Add **one** new invariant: `assert_no_duplicate_refs(system)` (no duplicate contract IDs in any agent’s `asset_ids` / `liability_ids`), called from `System.assert_invariants()`.

3. Tests that:

   * Validate per‑agent balance sheets in simple scenarios (cash, deposits, reserves).
   * Validate trial balance equals CB counters for cash and reserves, and that assets==liabilities system‑wide (financial only).
   * Hit the duplicate‑ID guard with a crafted (small) scenario.

No changes to existing behavior, events, or policy.

---

# Files to add / change

## 1) `src/bilancio/analysis/balances.py` (new)

```python
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, Iterable

# Light dataclasses for structured outputs
@dataclass
class AgentBalance:
    agent_id: str
    assets_by_kind: Dict[str, int]
    liabilities_by_kind: Dict[str, int]
    total_financial_assets: int
    total_financial_liabilities: int
    net_financial: int

@dataclass
class TrialBalance:
    assets_by_kind: Dict[str, int]
    liabilities_by_kind: Dict[str, int]
    total_financial_assets: int
    total_financial_liabilities: int

def _iter_instruments(system, ids: Iterable[str]):
    for cid in ids:
        c = system.state.contracts.get(cid)
        if c is not None:
            yield c

def agent_balance(system, agent_id: str) -> AgentBalance:
    agent = system.state.agents[agent_id]
    a_by, l_by = defaultdict(int), defaultdict(int)

    # Sum only financial instruments; deliverables are tracked elsewhere
    for c in _iter_instruments(system, agent.asset_ids):
        if getattr(c, "is_financial", lambda: True)():
            a_by[c.kind] += c.amount
    for c in _iter_instruments(system, agent.liability_ids):
        if getattr(c, "is_financial", lambda: True)():
            l_by[c.kind] += c.amount

    tfa = sum(a_by.values())
    tfl = sum(l_by.values())
    return AgentBalance(
        agent_id=agent_id,
        assets_by_kind=dict(a_by),
        liabilities_by_kind=dict(l_by),
        total_financial_assets=tfa,
        total_financial_liabilities=tfl,
        net_financial=tfa - tfl,
    )

def system_trial_balance(system) -> TrialBalance:
    a_by, l_by = defaultdict(int), defaultdict(int)

    # Walk all contracts once; add to both sides by kind
    for c in system.state.contracts.values():
        if getattr(c, "is_financial", lambda: True)():
            a_by[c.kind] += c.amount      # appears once as someone's asset
            l_by[c.kind] += c.amount      # and once as someone's liability

    tfa = sum(a_by.values())
    tfl = sum(l_by.values())
    return TrialBalance(
        assets_by_kind=dict(a_by),
        liabilities_by_kind=dict(l_by),
        total_financial_assets=tfa,
        total_financial_liabilities=tfl,
    )

def as_rows(system) -> list[dict]:
    """Tabular view: one row per agent, plus a 'SYSTEM' summary row."""
    rows = []
    for aid in system.state.agents:
        ab = agent_balance(system, aid)
        row = {
            "agent": aid,
            "assets_total": ab.total_financial_assets,
            "liabilities_total": ab.total_financial_liabilities,
            "net_financial": ab.net_financial,
            **{f"A_{k}": v for k, v in ab.assets_by_kind.items()},
            **{f"L_{k}": v for k, v in ab.liabilities_by_kind.items()},
        }
        rows.append(row)

    tb = system_trial_balance(system)
    rows.append({
        "agent": "SYSTEM",
        "assets_total": tb.total_financial_assets,
        "liabilities_total": tb.total_financial_liabilities,
        "net_financial": tb.total_financial_assets - tb.total_financial_liabilities,
        **{f"A_{k}": v for k, v in tb.assets_by_kind.items()},
        **{f"L_{k}": v for k, v in tb.liabilities_by_kind.items()},
    })
    return rows
```

Rationale: we only sum **financial** instruments; `Deliverable` overrides `is_financial()` to `False`, so it’s skipped — matching your modeling.&#x20;

---

## 2) `src/bilancio/core/invariants.py` — add duplicate‑ref guard

```python
def assert_no_duplicate_refs(system):
    """No duplicate contract IDs in any agent's asset/liability lists."""
    for aid, a in system.state.agents.items():
        assets_seen = set()
        for cid in a.asset_ids:
            if cid in assets_seen:
                raise AssertionError(f"duplicate asset ref {cid} on {aid}")
            assets_seen.add(cid)
        liabilities_seen = set()
        for cid in a.liability_ids:
            if cid in liabilities_seen:
                raise AssertionError(f"duplicate liability ref {cid} on {aid}")
            liabilities_seen.add(cid)
```

And wire it into `System.assert_invariants()` **after** the existing presence checks:

```python
from bilancio.core.invariants import (
    assert_cb_cash_matches_outstanding,
    assert_cb_reserves_match,
    assert_double_entry_numeric,
    assert_no_negative_balances,
    assert_no_duplicate_refs,   # <-- new
)
...
assert_no_duplicate_refs(self)
```

Your `System.assert_invariants()` currently calls the other checks; this simply extends it.&#x20;

---

## 3) Tests

Create `tests/analysis/test_balances.py`:

```python
from bilancio.engines.system import System
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.household import Household
from bilancio.ops.banking import deposit_cash
from bilancio.analysis.balances import agent_balance, system_trial_balance, as_rows

def test_agent_balance_simple_deposit():
    sys = System()
    cb = CentralBank(id="CB1", name="CB", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(cb); sys.add_agent(b1); sys.add_agent(h1)

    sys.mint_cash("H1", 120)
    deposit_cash(sys, "H1", "B1", 120)

    # H1: 120 deposit asset, no liabilities
    ab_h1 = agent_balance(sys, "H1")
    assert ab_h1.assets_by_kind.get("bank_deposit", 0) == 120
    assert ab_h1.total_financial_assets == 120
    assert ab_h1.total_financial_liabilities == 0
    assert ab_h1.net_financial == 120

    # B1: 120 deposit liability (to H1), cash asset 120 (vault)
    ab_b1 = agent_balance(sys, "B1")
    assert ab_b1.liabilities_by_kind.get("bank_deposit", 0) == 120
    assert ab_b1.assets_by_kind.get("cash", 0) == 120

    # Trial balance: sums match and equal on both sides
    tb = system_trial_balance(sys)
    assert tb.assets_by_kind["bank_deposit"] == 120
    assert tb.liabilities_by_kind["bank_deposit"] == 120
    assert tb.total_financial_assets == tb.total_financial_liabilities

    # Rows round-trip (smoke)
    rows = as_rows(sys)
    assert any(r["agent"] == "SYSTEM" for r in rows)
    sys.assert_invariants()

def test_trial_balance_reserves_counters_match():
    sys = System()
    cb = CentralBank(id="CB1", name="CB", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    sys.add_agent(cb); sys.add_agent(b1); sys.add_agent(b2)

    sys.mint_reserves("B1", 200)
    sys.mint_reserves("B2", 300)

    tb = system_trial_balance(sys)
    # Financial totals include reserves amounts on both sides
    assert tb.assets_by_kind.get("reserve_deposit", 0) == 500
    assert tb.liabilities_by_kind.get("reserve_deposit", 0) == 500
    # CB counters enforced elsewhere; invariants should pass
    sys.assert_invariants()
```

And a tiny test for the new invariant (optional but quick):

```python
def test_duplicate_ref_invariant():
    sys = System()
    cb = CentralBank(id="CB1", name="CB", kind="central_bank")
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(cb); sys.add_agent(h1)

    cid = sys.mint_cash("H1", 10)
    # Manually duplicate the ref to simulate a bug
    sys.state.agents["H1"].asset_ids.append(cid)
    try:
        sys.assert_invariants()
        assert False, "Expected duplicate ref assertion"
    except AssertionError as e:
        assert "duplicate asset ref" in str(e)
```

---

# Notes & compatibility

* We **don’t** modify events, policy, or ops. The analytics are read‑only.
* We **reuse** your existing modeling choices: instruments hold `amount` in minor units; `Deliverable.is_financial()==False`; CB counters live in `state`.&#x20;
* Invariants already check presence on both sides + CB cash/reserves + non‑negatives; we’re just adding a **dup‑ref** guard and using analytics to expose the same truths in a friendlier format.&#x20;

---

# How to run

```bash
uv run pytest -q
```

---

# Commit message

```
feat(analysis): add per‑agent balance sheets and system trial balance; 
chore(invariants): guard against duplicate instrument refs
```

If you like, the very next follow‑up PR can add (a) a tiny CSV writer for `as_rows(system)` into `io/writers.py`, and (b) an optional `log_balance_sheet(system, when="PhaseB")` helper that dumps a snapshot after a phase—still read‑only, still safe.
