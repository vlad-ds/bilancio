Alright—time to wire up banking. Here’s a tight, build-ready plan for **Stage 3: Banking operations (pre-clearing)**. We’ll implement deposits, withdrawals, and client payments. We’ll log cross-bank payments as day-local interbank flows but **defer** phase-C clearing (reserves vs overnight) to the next stage.

# Stage 3 — Banking operations (deposits, withdrawals, client payments)

## Context

We just finished cash + deliverables + split/merge. Now we let customers hold **bank deposits** and move money via **deposit/withdraw** and **client payments**. For cross-bank payments we do not move reserves yet; we log an **intraday interbank IOU** event for phase-C clearing in the next stage.

## Definition of done

* `deposit_cash(customer, bank, amount)` — moves **cash** from customer → bank; credits/creates a **BankDeposit** (bank liability to customer).
* `withdraw_cash(customer, bank, amount)` — debits **BankDeposit**; moves **cash** bank → customer; MVP requires the bank to have enough cash on hand (no auto cash↔reserves conversion yet).
* `client_payment(payer, payer_bank, payee, payee_bank, amount, allow_cash_fallback=False)` — debits payer’s **deposit at payer\_bank**; credits payee’s **deposit at payee\_bank**. If banks differ, emit a **ClientPayment** event capturing an intraday interbank flow; no reserves move yet.
* Event log entries for each op.
* Invariants continue to hold (double-entry; CB cash outstanding).
* Tests cover happy paths and key failures (insufficient funds, wrong bank, etc.).

## Design decisions

* One customer may hold multiple deposit instruments at the same bank (from earlier actions). We’ll **coalesce** after writes so the balance collapses to a single instrument per `(customer, bank)`.
* We keep a **helper** `get_or_create_deposit(bank_id, customer_id) -> deposit_id` that either returns an existing instrument (merging duplicates) or creates a zero-balance deposit.
* For MVP, **payments are deposit-only** (no automatic cash fallback). You can enable a fallback path later by setting `allow_cash_fallback=True`, which will transfer physical cash payer→payee and (optionally) auto-deposit for the payee.
* Interbank flows are recorded as **events**; phase-C netting/settlement will read today’s events to compute nets (next stage).

---

## Implementation steps

### 1) Small helpers (ops-agnostic)

`src/bilancio/engines/system.py` — add lightweight queries:

```python
def deposit_ids(self, customer_id: str, bank_id: str) -> list[str]:
    # filter customer assets for bank_deposit issued by bank_id
    out = []
    for cid in self.state.agents[customer_id].asset_ids:
        c = self.state.contracts[cid]
        if c.kind == "bank_deposit" and c.liability_issuer_id == bank_id:
            out.append(cid)
    return out

def total_deposit(self, customer_id: str, bank_id: str) -> int:
    return sum(self.state.contracts[cid].amount for cid in self.deposit_ids(customer_id, bank_id))
```

`src/bilancio/ops/primitives.py` — add **coalesce** for deposits (we already have `merge`):

```python
def coalesce_deposits(system, customer_id: str, bank_id: str) -> str:
    ids = system.deposit_ids(customer_id, bank_id)
    if not ids:
        # create a zero-balance deposit instrument
        from bilancio.domain.instruments.means_of_payment import BankDeposit
        dep_id = system.new_contract_id("D")
        dep = BankDeposit(
            id=dep_id, kind="bank_deposit", amount=0, denom="X",
            asset_holder_id=customer_id, liability_issuer_id=bank_id
        )
        system.add_contract(dep)
        return dep_id
    # merge all into the first
    keep = ids[0]
    for other in ids[1:]:
        merge(system, keep, other)
    return keep
```

### 2) Banking operations

`src/bilancio/ops/banking.py`

```python
from bilancio.core.atomic import atomic
from bilancio.core.errors import ValidationError
from bilancio.ops.primitives import split, merge, consume, coalesce_deposits
from bilancio.domain.instruments.means_of_payment import BankDeposit
from bilancio.domain.instruments.means_of_payment import Cash

def deposit_cash(system, customer_id: str, bank_id: str, amount: int) -> str:
    if amount <= 0: raise ValidationError("amount must be positive")
    # collect payer cash, splitting as needed
    with atomic(system):
        remaining = amount
        cash_ids = [cid for cid in list(system.state.agents[customer_id].asset_ids)
                    if system.state.contracts[cid].kind == "cash"]
        moved_piece_ids = []
        for cid in cash_ids:
            instr = system.state.contracts[cid]
            if instr.amount > remaining:
                cid = split(system, cid, remaining)
                instr = system.state.contracts[cid]
            # move holder to bank (issuer CB unchanged)
            system.state.agents[customer_id].asset_ids.remove(cid)
            system.state.agents[bank_id].asset_ids.append(cid)
            instr.asset_holder_id = bank_id
            moved_piece_ids.append(cid)
            remaining -= instr.amount
            if remaining == 0: break
        if remaining != 0:
            raise ValidationError("insufficient cash for deposit")

        # credit/ensure deposit
        dep_id = coalesce_deposits(system, customer_id, bank_id)
        system.state.contracts[dep_id].amount += amount
        system.log("CashDeposited", customer=customer_id, bank=bank_id, amount=amount,
                   cash_piece_ids=moved_piece_ids, deposit_id=dep_id)
        return dep_id

def withdraw_cash(system, customer_id: str, bank_id: str, amount: int) -> str:
    if amount <= 0: raise ValidationError("amount must be positive")
    with atomic(system):
        # 1) debit deposit
        dep_ids = system.deposit_ids(customer_id, bank_id)
        if not dep_ids: raise ValidationError("no deposit at this bank")
        remaining = amount
        for dep_id in dep_ids:
            dep = system.state.contracts[dep_id]
            take = min(dep.amount, remaining)
            dep.amount -= take
            remaining -= take
            if dep.amount == 0 and take > 0:
                # remove empty instrument
                holder = system.state.agents[customer_id]
                issuer = system.state.agents[bank_id]
                holder.asset_ids.remove(dep_id)
                issuer.liability_ids.remove(dep_id)
                del system.state.contracts[dep_id]
            if remaining == 0: break
        if remaining != 0:
            raise ValidationError("insufficient deposit balance")

        # 2) move cash from bank vault → customer (require sufficient cash on hand)
        bank_cash_ids = [cid for cid in list(system.state.agents[bank_id].asset_ids)
                         if system.state.contracts[cid].kind == "cash"]
        remaining = amount
        moved_piece_ids = []
        for cid in bank_cash_ids:
            instr = system.state.contracts[cid]
            if instr.amount > remaining:
                cid = split(system, cid, remaining)
                instr = system.state.contracts[cid]
            system.state.agents[bank_id].asset_ids.remove(cid)
            system.state.agents[customer_id].asset_ids.append(cid)
            instr.asset_holder_id = customer_id
            moved_piece_ids.append(cid)
            remaining -= instr.amount
            if remaining == 0: break
        if remaining != 0:
            raise ValidationError("bank has insufficient cash on hand (MVP: no auto conversion from reserves)")

        system.log("CashWithdrawn", customer=customer_id, bank=bank_id, amount=amount, cash_piece_ids=moved_piece_ids)
        # 3) coalesce customer cash if you want tidy balances (optional)
        return "ok"

def client_payment(system, payer_id: str, payer_bank: str, payee_id: str, payee_bank: str,
                   amount: int, allow_cash_fallback: bool=False) -> str:
    if amount <= 0: raise ValidationError("amount must be positive")
    with atomic(system):
        # 1) debit payer's deposit at payer_bank
        dep_ids = system.deposit_ids(payer_id, payer_bank)
        remaining = amount
        for dep_id in dep_ids:
            dep = system.state.contracts[dep_id]
            take = min(dep.amount, remaining)
            dep.amount -= take
            remaining -= take
            if dep.amount == 0 and take > 0:
                holder = system.state.agents[payer_id]
                issuer = system.state.agents[payer_bank]
                holder.asset_ids.remove(dep_id)
                issuer.liability_ids.remove(dep_id)
                del system.state.contracts[dep_id]
            if remaining == 0: break

        # Optional fallback: use payer's cash for the remainder (real-world “pay cash”)
        if remaining and allow_cash_fallback:
            cash_ids = [cid for cid in list(system.state.agents[payer_id].asset_ids)
                        if system.state.contracts[cid].kind == "cash"]
            for cid in cash_ids:
                instr = system.state.contracts[cid]
                if instr.amount > remaining:
                    cid = split(system, cid, remaining)
                    instr = system.state.contracts[cid]
                # move payer cash → payee (physical cash handover)
                system.state.agents[payer_id].asset_ids.remove(cid)
                system.state.agents[payee_id].asset_ids.append(cid)
                instr.asset_holder_id = payee_id
                remaining -= instr.amount
                if remaining == 0: break

        if remaining != 0:
            raise ValidationError("insufficient funds for payment")

        # 2) credit payee's deposit at payee_bank (if paying in cash fallback, you might auto-deposit)
        dep_rx = coalesce_deposits(system, payee_id, payee_bank)
        system.state.contracts[dep_rx].amount += amount

        # 3) record event for cross-bank intraday flow (no reserves move yet)
        if payer_bank != payee_bank:
            system.log("ClientPayment", payer=payer_id, payer_bank=payer_bank,
                       payee=payee_id, payee_bank=payee_bank, amount=amount)

        return dep_rx
```

### 3) Events shape (optional tidy-up)

If you want more structure, add small dataclasses/enums in `core/events.py`, but the dict log you already have is enough for MVP and phase-C netting.

### 4) Invariants (no change needed)

Double-entry and CB cash outstanding already cover these ops. You can add a quick assert that **no negative deposit balances** exist:

```python
def assert_no_negative_balances(system):
    for c in system.state.contracts.values():
        if c.kind in ("bank_deposit", "cash", "reserve_deposit") and c.amount < 0:
            raise AssertionError("negative balance detected")
```

Call it from `System.assert_invariants()`.

---

## Tests to add

`tests/integration/test_banking_ops.py`

* **Deposit cash**: CB mints cash to H1; H1 deposits 120 to B1. Assert: cash moved H1→B1, H1 has deposit 120 at B1, event logged, invariants hold.
* **Withdraw cash**: From previous state, withdraw 70. Assert: H1 deposit now 50, H1 cash +70, bank cash −70; error if bank doesn’t have cash.
* **Same-bank payment**: H1\@B1 pays H2\@B1, 40. Assert: H1 deposit −40, H2 deposit +40, no ClientPayment event.
* **Cross-bank payment**: H1\@B1 pays H3\@B2, 30. Assert: H1 deposit −30, H3 deposit +30 at B2, **ClientPayment** event recorded with payer\_bank=B1, payee\_bank=B2; reserves untouched.
* **Insufficient deposit**: payment raises `ValidationError`; re-run with `allow_cash_fallback=True` and enough payer cash → succeeds, and (optionally) auto-deposit payee cash if you choose to implement that later.
* **Coalescing**: Multiple small deposits for same `(customer, bank)` are coalesced by the helper; final state has one instrument id.

Run:

```bash
uv run pytest -q
```

---

## What we’re deferring to the **next stage (Stage 4: Clearing & Settlement)**

* Computing **interbank nets** from today’s `ClientPayment` events.
* Settling each net pair in **reserves if available; otherwise create an overnight interbank loan (Payable)** due on next day.
* Reserve transfers (`reserve_transfer(bank_a, bank_b, amount)`), which reuse the same split/merge primitives on `ReserveDeposit`.

This plan keeps banking ops simple, deterministic, and fully aligned with your MVP rules, while laying clean seams for phase-C clearing next.
