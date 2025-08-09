# Stage 2 — Cash & Non‑financial exchange + split/merge (pre‑banking)

This stage recreates the “cash + goods” behavior from the old `money-modeling/` repo, but cleaner. We’ll let the central bank create cash, hand it to agents, agents pass cash around, and agents transfer deliverables (non‑financial assets). Along the way we implement **split/merge/consume** for fungible instruments. This sets the table for banking ops later.

---

## Scope (Definition of Done)

* Central bank can **mint** and **retire** cash via the `System` gateway.
* Agents can **transfer cash** between themselves.
* Agents can **create/receive/transfer** non‑financial deliverables, including **partial quantity transfers** when divisible.
* Generic **split**, **merge**, and **consume** primitives for fungible instruments (cash now; bank deposits will reuse them later).
* Event log entries for the above.
* Invariants extended to include **CB cash outstanding** equals the **sum of all Cash liabilities**.
* Tests proving the flows work and invariants hold.

---

## Design notes (how we’ll model it)

* **Cash representation:** keep each holding as a `Cash` contract (CB liability ↔ holder asset). To mirror the “single number at CB” from the old project, track an **aggregate counter** `cb_cash_outstanding` in `System.state`. Invariants assert it equals `sum(c.amount for c in contracts if c.kind=="cash")`.
* **Fungibility:** add a tiny helper `fungible_key(instr)` that returns a tuple describing when two instruments can merge. For MVP: `(instr.kind, instr.denom, instr.liability_issuer_id, instr.asset_holder_id)`. Cash is **divisible** (any integer amount). Deliverables can be **divisible** (widget units) or **indivisible** (a car) based on a flag.
* **Split/Merge semantics:** split produces a new instrument with the same attributes except a new id and the requested amount; merge deletes B and adds its amount to A (A keeps the id) when keys match.

---

## API surface (what ops will look like)

* `system.mint_cash(to_agent_id, amount) -> instr_id`
* `system.retire_cash(from_agent_id, amount)`
* `system.transfer_cash(from_agent_id, to_agent_id, amount)`
* `system.create_deliverable(issuer_id, holder_id, sku, quantity, divisible: bool) -> instr_id`
* `system.transfer_deliverable(instr_id, from_agent_id, to_agent_id, quantity=None)`
  If `quantity` is `None`, transfer whole thing; if set, require `divisible=True` and do a split first.
* Internal primitives (used by the methods above):

  * `split(instr_id, amount) -> new_instr_id`
  * `merge(instr_id_a, instr_id_b) -> instr_id_a`
  * `consume(instr_id, amount)` (reduces amount, deleting at zero)

All of these are **mutations through `System`**, and you’ll wrap multi‑step ones in the `atomic` snapshot context so any failure reverts.

---

## Implementation steps (files & key snippets)

### 1) Extend `Deliverable` to support divisibility and SKU

`src/bilancio/domain/instruments/nonfinancial.py`

```python
from dataclasses import dataclass
from .base import Instrument

@dataclass
class Deliverable(Instrument):
    sku: str = "GENERIC"
    divisible: bool = True  # if False, amount must be whole and only full transfers allowed
    def __post_init__(self):
        self.kind = "deliverable"
    def is_financial(self) -> bool:
        return False
```

### 2) Add cash outstanding to system state

`src/bilancio/engines/system.py`

```python
@dataclass
class State:
    agents: Dict[AgentId, Agent] = field(default_factory=dict)
    contracts: Dict[InstrId, Instrument] = field(default_factory=dict)
    events: List[dict] = field(default_factory=list)
    day: int = 0
    cb_cash_outstanding: int = 0
```

### 3) Fungibility helpers

`src/bilancio/ops/primitives.py` (top of file)

```python
from typing import Tuple
from bilancio.domain.instruments.base import Instrument

def fungible_key(instr: Instrument) -> Tuple:
    # Same type, denomination, issuer, holder → can merge
    return (instr.kind, instr.denom, instr.liability_issuer_id, instr.asset_holder_id)

def is_divisible(instr: Instrument) -> bool:
    # Cash and bank deposits are divisible; deliverables depend on flag
    if instr.kind in ("cash", "bank_deposit", "reserve_deposit"): return True
    if instr.kind == "deliverable": return getattr(instr, "divisible", False)
    return False
```

### 4) Split / merge / consume primitives

Still in `ops/primitives.py`:

```python
from bilancio.core.ids import new_id
from bilancio.core.errors import ValidationError

def split(system, instr_id: str, amount: int) -> str:
    instr = system.state.contracts[instr_id]
    if amount <= 0 or amount > instr.amount:
        raise ValidationError("invalid split amount")
    if not is_divisible(instr):
        raise ValidationError("instrument is not divisible")
    # reduce original
    instr.amount -= amount
    # create twin
    twin_id = new_id("C")
    twin = type(instr)(
        id=twin_id,
        kind=instr.kind,
        amount=amount,
        denom=instr.denom,
        asset_holder_id=instr.asset_holder_id,
        liability_issuer_id=instr.liability_issuer_id,
        **{k: getattr(instr, k) for k in ("due_day","sku","divisible") if hasattr(instr, k)}
    )
    system.add_contract(twin)  # attaches to holder/issuer lists too
    return twin_id

def merge(system, a_id: str, b_id: str) -> str:
    if a_id == b_id: return a_id
    a = system.state.contracts[a_id]; b = system.state.contracts[b_id]
    if fungible_key(a) != fungible_key(b):
        raise ValidationError("instruments are not fungible-compatible")
    a.amount += b.amount
    # detach b from registries
    holder = system.state.agents[b.asset_holder_id]
    issuer = system.state.agents[b.liability_issuer_id]
    holder.asset_ids.remove(b_id)
    issuer.liability_ids.remove(b_id)
    del system.state.contracts[b_id]
    system.log("InstrumentMerged", keep=a_id, removed=b_id)
    return a_id

def consume(system, instr_id: str, amount: int) -> None:
    instr = system.state.contracts[instr_id]
    if amount <= 0 or amount > instr.amount:
        raise ValidationError("invalid consume amount")
    instr.amount -= amount
    if instr.amount == 0:
        holder = system.state.agents[instr.asset_holder_id]
        issuer = system.state.agents[instr.liability_issuer_id]
        holder.asset_ids.remove(instr_id)
        issuer.liability_ids.remove(instr_id)
        del system.state.contracts[instr_id]
```

### 5) Cash ops on `System`

`src/bilancio/engines/system.py` (inside `System`):

```python
from bilancio.domain.instruments.means_of_payment import Cash
from bilancio.core.atomic import atomic
from bilancio.ops.primitives import split, merge, consume
from bilancio.core.errors import ValidationError

def mint_cash(self, to_agent_id: AgentId, amount: int, denom="X") -> str:
    cb_id = next((aid for aid,a in self.state.agents.items() if a.kind == "central_bank"), None)
    assert cb_id, "CentralBank must exist"
    instr_id = self.new_contract_id("C")
    c = Cash(
        id=instr_id, kind="cash", amount=amount, denom=denom,
        asset_holder_id=to_agent_id, liability_issuer_id=cb_id
    )
    with atomic(self):
        self.add_contract(c)
        self.state.cb_cash_outstanding += amount
        self.log("CashMinted", to=to_agent_id, amount=amount, instr_id=instr_id)
    return instr_id

def retire_cash(self, from_agent_id: AgentId, amount: int) -> None:
    # pull from holder's cash instruments (simple greedy)
    with atomic(self):
        remaining = amount
        cash_ids = [cid for cid in self.state.agents[from_agent_id].asset_ids
                    if self.state.contracts[cid].kind == "cash"]
        for cid in list(cash_ids):
            instr = self.state.contracts[cid]
            take = min(instr.amount, remaining)
            consume(self, cid, take)
            remaining -= take
            if remaining == 0: break
        if remaining != 0:
            raise ValidationError("insufficient cash to retire")
        self.state.cb_cash_outstanding -= amount
        self.log("CashRetired", frm=from_agent_id, amount=amount)

def transfer_cash(self, from_agent_id: AgentId, to_agent_id: AgentId, amount: int) -> str:
    if from_agent_id == to_agent_id:
        raise ValidationError("no-op transfer")
    with atomic(self):
        remaining = amount
        # collect cash pieces and split as needed
        for cid in list(self.state.agents[from_agent_id].asset_ids):
            instr = self.state.contracts[cid]
            if instr.kind != "cash": continue
            piece_id = cid
            if instr.amount > remaining:
                piece_id = split(self, cid, remaining)
            piece = self.state.contracts[piece_id]
            # move holder
            self.state.agents[from_agent_id].asset_ids.remove(piece_id)
            self.state.agents[to_agent_id].asset_ids.append(piece_id)
            piece.asset_holder_id = to_agent_id
            self.log("CashTransferred", frm=from_agent_id, to=to_agent_id, amount=min(remaining, piece.amount), instr_id=piece_id)
            remaining -= piece.amount
            if remaining == 0: break
        if remaining != 0:
            raise ValidationError("insufficient cash")
        # optional coalesce at receiver (merge duplicates)
        rx_ids = [cid for cid in self.state.agents[to_agent_id].asset_ids
                  if self.state.contracts[cid].kind == "cash"]
        # naive coalesce: pairwise merge same-key
        seen = {}
        for cid in rx_ids:
            k = (self.state.contracts[cid].denom, self.state.contracts[cid].liability_issuer_id)
            keep = seen.get(k)
            if keep and keep != cid:
                merge(self, keep, cid)
            else:
                seen[k] = cid
    return "ok"
```

### 6) Deliverable creation & transfer

Also in `System`:

```python
from bilancio.domain.instruments.nonfinancial import Deliverable

def create_deliverable(self, issuer_id: AgentId, holder_id: AgentId, sku: str, quantity: int, divisible: bool=True, denom="N/A") -> str:
    instr_id = self.new_contract_id("N")
    d = Deliverable(
        id=instr_id, kind="deliverable", amount=quantity, denom=denom,
        asset_holder_id=holder_id, liability_issuer_id=issuer_id,
        sku=sku, divisible=divisible
    )
    with atomic(self):
        self.add_contract(d)
        self.log("DeliverableCreated", issuer=issuer_id, holder=holder_id, sku=sku, qty=quantity, instr_id=instr_id)
    return instr_id

def transfer_deliverable(self, instr_id: InstrId, from_agent_id: AgentId, to_agent_id: AgentId, quantity: int | None=None) -> str:
    instr = self.state.contracts[instr_id]
    if instr.kind != "deliverable":
        raise ValidationError("not a deliverable")
    if instr.asset_holder_id != from_agent_id:
        raise ValidationError("holder mismatch")
    with atomic(self):
        moving_id = instr_id
        if quantity is not None:
            if not getattr(instr, "divisible", False):
                raise ValidationError("indivisible deliverable")
            if quantity <= 0 or quantity > instr.amount:
                raise ValidationError("invalid quantity")
            if quantity < instr.amount:
                moving_id = split(self, instr_id, quantity)
        # change owner
        self.state.agents[from_agent_id].asset_ids.remove(moving_id)
        self.state.agents[to_agent_id].asset_ids.append(moving_id)
        m = self.state.contracts[moving_id]
        m.asset_holder_id = to_agent_id
        self.log("DeliverableTransferred", frm=from_agent_id, to=to_agent_id, instr_id=moving_id, qty=m.amount, sku=getattr(m, "sku","GENERIC"))
    return moving_id
```

### 7) Invariants update

`src/bilancio/core/invariants.py`

```python
def assert_cb_cash_matches_outstanding(system):
    total = sum(c.amount for c in system.state.contracts.values() if c.kind == "cash")
    assert total == system.state.cb_cash_outstanding, "CB cash mismatch"

# call this from System.assert_invariants()
```

In `System.assert_invariants()`:

```python
from bilancio.core.invariants import assert_cb_cash_matches_outstanding
def assert_invariants(self) -> None:
    for cid, c in self.state.contracts.items():
        assert cid in self.state.agents[c.asset_holder_id].asset_ids
        assert cid in self.state.agents[c.liability_issuer_id].liability_ids
    assert_cb_cash_matches_outstanding(self)
```

---

## Tests (what to add)

* **Mint & retire cash round‑trip**
  Create CB + HH; `mint_cash(H1, 150)`; check HH assets include a cash id and CB outstanding = 150; `retire_cash(H1, 80)`; check remaining = 70; invariants hold.

* **Transfer cash with split & merge**
  Mint `100` to H1 as one instrument; `transfer_cash(H1, H2, 30)` splits 30 and moves it; `transfer_cash(H1, H2, 70)` moves the rest; H2 should end with **one** cash instrument of `100` after auto‑merge.

* **Create/transfer deliverable (divisible)**
  Create a `Deliverable(sku="WIDGET", qty=10, divisible=True)` to H1; `transfer_deliverable(id, H1, H2, quantity=3)`; expect H1 keeps 7, H2 has 3; full transfer next leaves H1 with none. Invariants hold.

* **Indivisible deliverable**
  Create `Deliverable(sku="CAR", qty=1, divisible=False)`; partial transfer should raise `ValidationError`; full transfer moves ownership.

* **Negative paths**
  Insufficient cash during `retire_cash` or `transfer_cash` raises `ValidationError`; wrong current holder raises on deliverables.

---

## Developer notes

* Keep all multi‑step ops inside `with atomic(system)` so tests can inject a failure and verify rollback restores both state and the CB counter.
* Don’t over‑optimize: no persistent indices yet. Scans are fine at this scale.
* Event log payloads are intentionally minimal; we’ll formalize `core/events.py` later when we add the settlement phases.

---

## Run & commit

```
uv run pytest -q
git add -A
git commit -m "feat(cash,deliverables): mint/retire/transfer cash, create/transfer deliverables, split/merge primitives, CB cash invariant"
```

When this is green, you’re perfectly set up to implement **banking ops** next (deposits/withdrawals/payments) reusing the same split/merge primitives and the “IDs + System gateway” discipline.
