Here’s a concrete, “paste‑into‑Jira” style plan for the next milestone. It assumes you’ll remove the duplicate Agent root first, and keeps everything MVP‑simple while laying clean seams for later upgrades.

# Stage 3 — Reserves, Payable Settlement (Phase B), Interbank Clearing (Phase C), Scheduler

## Context

`bilancio` now has a clean System gateway, typed instruments/agents, policy checks, cash & deliverable flows, and basic banking ops (deposit/withdraw/client payment). Next we’ll add central‑bank reserves and the day/phase mechanics so cross‑bank flows become economically correct. Keep snapshot rollback (`atomic`) for multi‑step writes, no persistent indices, and derive interbank nets from the event log.

---

# 0) Pre‑flight cleanup (1 PR)

* Remove the protocol duplicate in `domain/agents/agent.py` (or rename it to `AgentProto`) and keep `domain/agent.py:Agent` as the single base. Re‑export if needed so existing imports don’t break.

**DoD:** `ripgrep "from bilancio.domain.agents.agent"` returns nothing; tests still pass.

---

# 1) Reserves plumbing (CB liabilities held by banks/treasury)

### 1.1 Add CB reserves outstanding counter

`src/bilancio/engines/system.py` → `State`

```python
cb_cash_outstanding: int = 0      # already present
cb_reserves_outstanding: int = 0  # new
```

### 1.2 Reserve helpers on System

`src/bilancio/engines/system.py`

```python
from bilancio.domain.instruments.means_of_payment import ReserveDeposit
from bilancio.core.atomic_tx import atomic            # use your tx module

def _central_bank_id(self) -> str:
    for aid, a in self.state.agents.items():
        if a.kind == "central_bank":
            return aid
    raise ValidationError("CentralBank must exist")

def mint_reserves(self, to_bank_id: str, amount: int, denom="X") -> str:
    cb_id = self._central_bank_id()
    instr_id = self.new_contract_id("R")
    r = ReserveDeposit(
        id=instr_id, kind="reserve_deposit", amount=amount, denom=denom,
        asset_holder_id=to_bank_id, liability_issuer_id=cb_id
    )
    with atomic(self):
        self.add_contract(r)
        self.state.cb_reserves_outstanding += amount
        self.log("ReservesMinted", to=to_bank_id, amount=amount, instr_id=instr_id)
    return instr_id

def transfer_reserves(self, from_bank_id: str, to_bank_id: str, amount: int) -> None:
    if from_bank_id == to_bank_id:
        raise ValidationError("no-op reserves transfer")
    with atomic(self):
        remaining = amount
        # greedy over from_bank's reserve instruments
        res_ids = [cid for cid in self.state.agents[from_bank_id].asset_ids
                   if self.state.contracts[cid].kind == "reserve_deposit"]
        for cid in list(res_ids):
            instr = self.state.contracts[cid]
            take = min(instr.amount, remaining)
            if take == 0: continue
            if instr.amount > take:
                cid = split(self, cid, take)
                instr = self.state.contracts[cid]
            # move holder
            self.state.agents[from_bank_id].asset_ids.remove(cid)
            self.state.agents[to_bank_id].asset_ids.append(cid)
            instr.asset_holder_id = to_bank_id
            self.log("ReservesMoved", frm=from_bank_id, to=to_bank_id, amount=take, instr_id=cid)
            remaining -= take
            if remaining == 0: break
        if remaining != 0:
            raise ValidationError("insufficient reserves")

        # coalesce at receiver (optional)
        rx = [cid for cid in self.state.agents[to_bank_id].asset_ids
              if self.state.contracts[cid].kind == "reserve_deposit"]
        seen = {}
        for cid in rx:
            k = (self.state.contracts[cid].denom, self.state.contracts[cid].liability_issuer_id)
            keep = seen.get(k)
            if keep and keep != cid:
                merge(self, keep, cid)
            else:
                seen[k] = cid

def convert_reserves_to_cash(self, bank_id: str, amount: int) -> None:
    """CB exchanges reserves for cash: bank loses reserves, gains cash; CB swaps liabilities."""
    cb_id = self._central_bank_id()
    with atomic(self):
        self.transfer_reserves(bank_id, cb_id, amount)   # bank→CB (holder becomes CB)
        # retire the CB-held reserve instruments we just received
        remaining = amount
        res_ids = [cid for cid in list(self.state.agents[cb_id].asset_ids)
                   if self.state.contracts[cid].kind == "reserve_deposit"]
        for cid in res_ids:
            instr = self.state.contracts[cid]
            take = min(instr.amount, remaining)
            consume(self, cid, take)
            self.state.cb_reserves_outstanding -= take
            remaining -= take
            if remaining == 0: break
        # mint cash to the bank
        self.mint_cash(bank_id, amount)  # updates cb_cash_outstanding

def convert_cash_to_reserves(self, bank_id: str, amount: int) -> None:
    """Bank returns cash to CB and receives reserves."""
    with atomic(self):
        self.retire_cash(bank_id, amount)                 # reduces cb_cash_outstanding
        self.mint_reserves(bank_id, amount)               # increases cb_reserves_outstanding
```

> Uses existing `split/merge/consume` primitives; all within `with atomic(self)`.

### 1.3 Invariant: CB reserves sum

`src/bilancio/core/invariants.py`

```python
def assert_cb_reserves_match(system):
    total = sum(c.amount for c in system.state.contracts.values()
                if c.kind == "reserve_deposit")
    assert total == system.state.cb_reserves_outstanding, "CB reserves mismatch"
```

Wire it into `System.assert_invariants()` alongside the cash check.

### 1.4 Tests

* `tests/unit/test_reserves.py`

  * mint\_reserves to B1; assert holder/issuer and CB counter; transfer to B2; invariants.
  * convert\_reserves\_to\_cash and convert\_cash\_to\_reserves round‑trip; both CB counters update appropriately; bank balances change as expected.
  * negative path: transfer more than available → `ValidationError`.

---

# 2) Settlement engine (Phase B) — settle `Payable`s due today

### 2.1 Settlement selection via policy

`domain/policy.py` already exposes `settlement_order(agent) -> list[str]`. Use it to drive payment method choice. For banks, it returns `["reserve_deposit"]`.

### 2.2 Implement the engine

`src/bilancio/engines/settlement.py`

```python
from bilancio.core.errors import DefaultError, ValidationError

def due_payables(system, day: int):
    # MVP scan: no indices
    for c in system.state.contracts.values():
        if c.kind == "payable" and getattr(c, "due_day", None) == day:
            yield c

def settle_due(system, day: int):
    """
    For each payable (debtor -> creditor) due today:
      - If debtor has means (per policy ranking), pay deterministically.
      - If cross-bank deposit is used, log ClientPayment and defer reserves to Phase C.
      - If insufficient across all allowed means, raise DefaultError (halt).
    """
    for p in list(due_payables(system, day)):
        debtor = system.state.agents[p.liability_issuer_id]
        creditor = system.state.agents[p.asset_holder_id]
        order = system.policy.settlement_order(debtor)

        paid = 0
        remaining = p.amount

        with atomic(system):
            for method in order:
                if remaining == 0: break
                if method == "bank_deposit":
                    # same-bank vs cross-bank logic via existing helpers
                    paid_now = _pay_with_deposits(system, debtor.id, creditor.id, remaining)
                    remaining -= paid_now
                elif method == "cash":
                    paid_now = _pay_with_cash(system, debtor.id, creditor.id, remaining)
                    remaining -= paid_now
                elif method == "reserve_deposit":
                    paid_now = _pay_bank_to_bank_with_reserves(system, debtor.id, creditor.id, remaining)
                    remaining -= paid_now
                else:
                    raise ValidationError(f"unknown payment method {method}")

            if remaining != 0:
                # fail whole block for MVP; v1.0 requirement is to stop on default
                raise DefaultError(f"Insufficient funds to settle payable {p.id}")

            # fully settled: remove payable
            _remove_contract(system, p.id)
            system.log("PayableSettled", pid=p.id, debtor=debtor.id, creditor=creditor.id, amount=p.amount)
```

**Internal helpers** (same file or `ops/banking.py`):

* `_pay_with_deposits(system, debtor_id, creditor_id, amount) -> int`
  Debit debtor’s deposit at their bank; credit creditor’s deposit at their bank.
  If banks differ, use your existing `client_payment` (which logs `ClientPayment` event) for the amount and return the amount paid.
  If same bank, use split/consume/merge on `BankDeposit` objects and return the amount paid.

* `_pay_with_cash(system, debtor_id, creditor_id, amount) -> int`
  `system.transfer_cash(debtor, creditor, min(available_cash, amount))`.

* `_pay_bank_to_bank_with_reserves(system, debtor_bank_id, creditor_bank_id, amount) -> int`
  For bank‑to‑bank obligations (e.g., interbank overnight), try `transfer_reserves`. If not enough, return `0` so the caller continues to next method (there won’t be one for banks, so it will default).

* `_remove_contract(system, contract_id)`
  Remove from registries and both agents’ id lists (you already do this pattern in `consume` when amount hits zero).

**Note:** For v1.0, do **all‑or‑nothing** within the `with atomic()` block (no partial settle that leaves a reduced payable). Keep it deterministic.

### 2.3 Tests

* `tests/integration/test_settlement_phase_b.py`

  * Same‑bank: H1\@B1 owes H2\@B1; deposits only → payable removed; deposits adjusted; invariants.
  * Cross‑bank: H1\@B1 owes H2\@B2; debtor pays from deposits → `ClientPayment` event logged; payable removed; no reserves moved yet.
  * Cash fallback: Settle with cash if deposit insufficient and policy order includes cash; payable removed.
  * Default: Neither deposits nor cash available → `DefaultError` raised and system unchanged (atomic rollback).

---

# 3) Interbank clearing engine (Phase C)

### 3.1 Build nets from today’s events

`src/bilancio/engines/clearing.py`

```python
from collections import defaultdict
from typing import Dict, Tuple

Pair = Tuple[str, str]  # (payer_bank, payee_bank) in a fixed lexical order

def compute_intraday_nets(system, day: int) -> Dict[Pair, int]:
    nets = defaultdict(int)
    for ev in system.state.events:
        if ev.get("day") != day: continue
        if ev.get("kind") != "ClientPayment": continue
        pb = ev["payer_bank"]; rb = ev["payee_bank"]; amt = ev["amount"]
        if pb == rb: continue
        a, b = sorted([pb, rb])
        sign = amt if (pb, rb) == (a, b) else -amt
        nets[(a, b)] += sign
    # Drop zeros
    return {k: v for k, v in nets.items() if v}
```

By convention, `nets[(a,b)] > 0` means **a owes b** at end of day.

### 3.2 Settle nets deterministically

Same file:

```python
from bilancio.core.atomic_tx import atomic

def settle_intraday_nets(system, day: int):
    nets = compute_intraday_nets(system, day)
    for (a, b), net in nets.items():
        if net == 0: continue
        payer, payee, amount = (a, b, net) if net > 0 else (b, a, -net)
        with atomic(system):
            try:
                system.transfer_reserves(payer, payee, amount)
                system.log("InterbankCleared", day=day, payer=payer, payee=payee, amount=amount, mode="reserves")
            except ValidationError:
                # Not enough reserves → create overnight payable due tomorrow
                pid = system.new_contract_id("P")
                p = Payable(id=pid, kind="payable", amount=amount, denom="X",
                            asset_holder_id=payee, liability_issuer_id=payer, due_day=day+1)
                system.add_contract(p)
                system.log("InterbankOvernightCreated", day=day, payer=payer, payee=payee, amount=amount, pid=pid)
```

**Policy note:** We choose “no partial reserves”; either settle fully in reserves or roll the full net to overnight (simpler, deterministic). You can change this rule later behind a policy flag.

### 3.3 Tests

* `tests/integration/test_clearing_phase_c.py`

  * Two banks, multiple cross‑bank client payments in both directions → after Phase C, only the **net** amount moves in reserves (or O/N is created when payer lacks reserves).
  * Overnight from Day t settles on Day t+1 if payer receives reserves in the meantime; otherwise triggers default in Phase B (see next section).

---

# 4) Day/phase scheduler

`src/bilancio/engines/simulation.py`

```python
from bilancio.core.time import Phase

def run_day(system):
    day = system.state.day

    # Phase A: prepare/trade (noop for MVP)
    system.log("PhaseA", day=day)

    # Phase B: settle due payables (may Default and halt)
    settle_due(system, day)
    system.log("PhaseB", day=day)

    # Phase C: interbank clearing for today's client payments
    settle_intraday_nets(system, day)
    system.log("PhaseC", day=day)

    system.state.day += 1
```

**Test:** simple “day in the life” scenario chaining the earlier tests: create obligations, run `run_day` twice to see an O/N created then settled.

---

# 5) Tighten invariants

`src/bilancio/core/invariants.py`

```python
def assert_double_entry_numeric(system):
    # financial contracts only (exclude deliverables)
    total = 0
    for c in system.state.contracts.values():
        if c.kind in {"deliverable"}: continue
        total += c.amount
    # In this representation, each contract's amount appears once as asset and once as liability,
    # so sum over contracts is symmetric by construction. Numeric check is mainly to catch negatives:
    assert all(c.amount >= 0 for c in system.state.contracts.values()), "negative amount found"
```

Update `System.assert_invariants()` to call:

* existing per‑contract presence checks,
* `assert_cb_cash_matches_outstanding(system)`,
* `assert_cb_reserves_match(system)`,
* `assert_double_entry_numeric(system)`.

---

# 6) Use policy for payment choice

Replace any hardcoded `allow_cash_fallback` branches with:

```python
order = system.policy.settlement_order(payer_agent)
# iterate methods in order
```

**Test:** override policy in a test to `["cash", "bank_deposit"]` for households and confirm the settlement picks cash first.

---

# 7) Tests you should add now

* `test_reserves_roundtrip_and_invariants` (Section 1.4)
* `test_phase_b_same_bank_settlement` and `test_phase_b_cross_bank_settlement_logs_client_payment`
* `test_phase_b_default_on_insufficient_means`
* `test_phase_c_netting_reserves_or_overnight`
* `test_phase_c_then_next_day_phase_b_settles_overnight_or_defaults`
* `test_policy_order_drives_payment_choice`

All tests should call `system.assert_invariants()` after each major step.

---

# 8) Documentation & tiny refactors

* In `README.md`, add “Day/Phase semantics” and “Interbank clearing rule (reserves else O/N)”.
* Consider re‑exporting `atomic` from `bilancio.core` to consolidate imports: `from bilancio.core import atomic`.

---

# 9) Suggested commit sequence

1. `refactor(agent): remove protocol duplication, keep dataclass Agent as single base`
2. `feat(reserves): add CB reserves counters, mint/transfer/convert ops + invariants`
3. `feat(settlement): phase B payable settlement with policy-driven means selection`
4. `feat(clearing): phase C interbank netting from ClientPayment events`
5. `feat(sim): add run_day scheduler (A noop → B settle → C clear)`
6. `test: add end-to-end scenarios for cross-bank payments and overnight`

---

This gives you real central bank plumbing, deterministic settlement and clearing, and a tiny scheduler to tie it together. Once this is green, you’ll have the full “day in the life” loop and can move to analytics (balance‑sheet / funding traces / flux‑reflux) without touching the core.
