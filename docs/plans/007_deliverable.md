Great—since we’re allowed to break things, here’s an “ideal‑state” refactor plan focused only on fixing the conceptual conflation between **the thing (goods)**, **who owns it (inventory)**, and **a promise to deliver it (obligation)**. This plan intentionally removes the current “self‑issued deliverable” pattern and replaces it with a clean split of concepts. It’s scoped so an advanced coding agent can implement it end‑to‑end without preserving backward compatibility.

> Why this matters: the current `Deliverable` class is used for both inventory and delivery promises (including a `due_day`). It forces awkward self‑issued contracts for inventory and brittle settlement that “searches” for a matching SKU to honor a promise. We want:
> **(1) a real stock/inventory object; (2) a separate delivery contract; (3) deterministic linkage at settlement.**&#x20;
> This also better matches the “Temporal transformation of a balance sheet system” section in your PDF: non‑financial **things** (machines) exist and move; **promises** to deliver them exist and are executed at their timepoints.&#x20;

---

## A. Target mental model (post‑refactor)

* **StockLot** (non‑financial): a batch of goods the agent *owns* (e.g., 10 machines @ price P). Not anyone’s liability.
* **DeliveryObligation** (contract): a bilateral promise that *Agent X will deliver* Q units of SKU to *Agent Y* by `due_day`. This is a receivable for Y and a payable (non‑monetary) for X, and it **is not** the goods themselves.
* **Settlement**: when `due_day` arrives, the engine **moves StockLots** from X’s inventory to Y in the promised quantity, then **extinguishes the DeliveryObligation**.

This aligns with your Version 1.0 description of executing balance‑sheet entries point‑in‑time and then moving to the next timepoint.&#x20;

---

## B. API & data‑model changes (breaking)

### B1. New types (domain)

**`bilancio/domain/goods.py` (new)**

```python
# non-financial; not a liability of anyone
from dataclasses import dataclass
from decimal import Decimal
from bilancio.core.ids import InstrId, AgentId

StockId = InstrId  # reuse ID machinery

@dataclass
class StockLot:
    id: StockId
    kind: str          # fixed: "stock_lot"
    sku: str
    quantity: int
    unit_price: Decimal
    owner_id: AgentId
    divisible: bool = True

    @property
    def value(self) -> Decimal:
        return Decimal(str(self.quantity)) * self.unit_price
```

**`bilancio/domain/instruments/delivery.py` (new)**

```python
from dataclasses import dataclass
from decimal import Decimal
from bilancio.domain.instruments.base import Instrument

@dataclass
class DeliveryObligation(Instrument):
    # amount = quantity promised (rename for clarity at call sites)
    sku: str
    unit_price: Decimal
    due_day: int

    def __post_init__(self):
        self.kind = "delivery_obligation"

    def is_financial(self) -> bool:
        # Shows up in balance analysis as non-financial (valued) obligation
        return False

    @property
    def valued_amount(self) -> Decimal:
        from decimal import Decimal as D
        return D(str(self.amount)) * self.unit_price
```

> Notes
> • Inventory is no longer an `Instrument` and carries **no `liability_issuer_id`**—because nobody owes goods to the current owner just because the owner has them.
> • The delivery promise remains an `Instrument` so the system keeps **proper bilateral asset/liability references** for the claim vs. obligation.&#x20;

### B2. System state & registries

**`engines/system.py` — `State` gets a dedicated store for inventory; `Agent` tracks owned stock**

* `State.stocks: dict[StockId, StockLot] = field(default_factory=dict)`
* Extend `Agent` with `stock_ids: list[StockId] = field(default_factory=list)` (place in `domain/agent.py`).

**Remove** all uses of *self‑issued* `Deliverable`. We will delete `domain/instruments/nonfinancial.Deliverable` and replace with these two classes. (We’ll also remove its type‑invariant override that allowed same holder/issuer, which was a smell.)&#x20;

### B3. System methods (public API)

Add **explicit inventory APIs** and **explicit obligation APIs**. Remove the old mixed ones.

**Inventory (goods)**

* `create_stock(owner_id, sku, quantity, unit_price, divisible=True) -> StockId`
* `split_stock(stock_id, quantity) -> StockId` (creates a twin lot; mirrors `ops.primitives.split`, but for stock)
* `merge_stock(stock_id_keep, stock_id_into) -> StockId` (same constraints as fungibility rules)
* `transfer_stock(stock_id, from_owner, to_owner, quantity=None) -> StockId`

**Delivery contracts**

* `create_delivery_obligation(from_agent, to_agent, sku, quantity, unit_price, due_day) -> InstrId`
* `cancel_delivery_obligation(obligation_id)` (generic extinguisher, used only by the engine after fulfillment)

**Remove/rename (breaking)**

* `create_deliverable(...)` → delete
* `transfer_deliverable(...)` → `transfer_stock(...)`

### B4. Policy engine

No change needed for inventory (non‑instrument). For `DeliveryObligation`, the **issuer/holder rules** remain “any agent can issue/hold” (like Payable), so keep it listed in `PolicyEngine.issuers/holders` under the new class.

---

## C. Engine changes

### C1. Settlement (Phase B) for delivery obligations

**`engines/settlement.py`**

* Replace `due_deliverables()` with `due_delivery_obligations()` scanning `kind == "delivery_obligation"`.
* Replace `_deliver_goods(...)` to operate on **StockLots**:

  1. Gather debtor’s `StockLot`s matching SKU.
  2. Greedy allocate by policy (default **FIFO by creation id/time** for determinism).
  3. If partial lot needed, call `split_stock`.
  4. Call `transfer_stock` for each piece.
* After goods fully transferred, call `cancel_delivery_obligation(obligation_id)` and log `DeliveryObligationSettled`.

**Events to log (observability)**

* `DeliveryObligationCreated {id, from, to, sku, qty, due_day, unit_price}`
* `StockCreated {id, owner, sku, qty, unit_price}`
* `StockTransferred {id, from, to, sku, qty}`
* `DeliveryObligationSettled {obligation_id, debtor, creditor, sku, qty}`
* (Optional) `StockSplit`, `StockMerged`

> This exactly mirrors the “t₁ transfer 10 machines; extinguish claim/promise” rhythm the PDF describes.&#x20;

---

## D. Ops & primitives

### D1. New stock primitives (separate from financial `Instrument` primitives)

**`ops/primitives_stock.py` (new)**

* `stock_fungible_key(lot) -> tuple`: `(kind, sku, owner_id, unit_price)`; include price so lots with different valuation don’t merge by accident (mirrors current deliverable merge tests intent).&#x20;
* `split_stock(system, stock_id, quantity) -> StockId`
* `merge_stock(system, keep_id, remove_id) -> StockId` (requires same `stock_fungible_key`)
* `consume_stock(...)` if you need destruction in future (not required for delivery settlement).

**Why separate file?** Keeps non‑financial stock ops isolated from financial `Instrument` ops (`ops/primitives.py`).&#x20;

---

## E. Analysis layer changes

### E1. AgentBalance / TrialBalance accounting

**Goal:** Financial trial balance remains double‑entry and balanced, while non‑financial *inventory* appears in “nonfinancial assets” and *delivery obligations* appear in “nonfinancial liabilities” (valued). This preserves clear separation and fixes earlier “count deliverables as both inventory and promises” confusion.

**`analysis/balances.py`**

* When computing **financial** totals, **ignore** `StockLot` entirely (it’s not an `Instrument`).
* For **non‑financial assets by SKU**: iterate `agent.stock_ids` and aggregate `quantity` and `value`.
* For **non‑financial liabilities by SKU**: iterate contracts of `kind == "delivery_obligation"` on the liability side; sum quantities and `valued_amount`.
* Keep the existing valued totals (`total_nonfinancial_value` and `total_nonfinancial_liability_value`) but compute them from *stocks* and *delivery obligations* respectively.

> This changes prior behavior where `Deliverable` doubled as both inventory and obligation and was scanned in `contracts` alone. After the refactor, inventory lives in `stocks`; obligations live in `contracts`. Update the display code that shows deliverables to read from these two sources.&#x20;

---

## F. Invariants

**`core/invariants.py`**

* Keep all current financial invariants for `contracts` intact. They should never consider `StockLot`.&#x20;
* Add:

  * `assert_all_stock_ids_owned(system)`: every `StockLot` id found in exactly one agent’s `stock_ids` and `stocks` registry.
  * `assert_no_negative_stocks(system)`: `quantity >= 0`.
  * `assert_no_duplicate_stock_refs(system)`: no duplicates in `stock_ids`.

---

## G. File‑by‑file implementation checklist

1. **Delete old non‑financial instrument**

   * Remove `src/bilancio/domain/instruments/nonfinancial.py::Deliverable` and its imports.
   * Remove code paths that create “self‑issued deliverable”.&#x20;

2. **Add new domain types**

   * `domain/goods.py::StockLot` (new)
   * `domain/instruments/delivery.py::DeliveryObligation` (new)

3. **Extend Agent & State**

   * `domain/agent.py`: add `stock_ids: list[InstrId]`
   * `engines/system.py: State`: add `stocks: dict[StockId, StockLot]`

4. **System APIs**

   * Implement inventory methods: `create_stock`, `split_stock`, `merge_stock`, `transfer_stock`
   * Implement obligation methods: `create_delivery_obligation`, `cancel_delivery_obligation`
   * Remove `create_deliverable` / `transfer_deliverable`

5. **Settlement phase B**

   * Replace “due deliverables” pipeline with “due delivery obligations” pipeline using stock ops

6. **Analysis**

   * Update `analysis/balances.py` to read stocks for non‑financial assets and delivery obligations for non‑financial liabilities (valued)

7. **Primitives**

   * Add `ops/primitives_stock.py`; do **not** overload `ops/primitives.py` (financial only)

8. **Events**

   * Add the new event kinds listed in C1 and update any notebook logging cells

9. **Policy**

   * Add `DeliveryObligation` to `PolicyEngine.issuers/holders` maps; no entry for StockLot (not an instrument)

10. **Visualization**

* `analysis/visualization.py`: show **inventory** rows from stocks and **obligation** rows from delivery obligations. (Rename label text from “deliverable” to “inventory” and “delivery obligation” where appropriate.)

---

## H. Test plan (new semantics; expect breaks)

> We’re intentionally breaking behavior; update tests accordingly.

* **Unit: stock operations**

  * create/split/merge/transfer StockLots; merging only when `(sku, owner, unit_price, divisible)` match
* **Unit: delivery obligation**

  * create/cancel; valued amount; due day validation
* **Settlement:**

  * When due, transfer FIFO lots until the obligation quantity is satisfied; obligation extinguished; events emitted; raise `DefaultError` if not enough stock
  * Wrong SKU: no delivery; `DefaultError`
* **Analysis:**

  * Inventory value shows as non‑financial asset by SKU; delivery obligations show as non‑financial liabilities by SKU; financial trial balance remains balanced (unchanged)
* **Regression (PDF example)**

  * Recreate the “machines” scenario (Agents 1–4) with explicit `StockLot` and `DeliveryObligation`, and verify the t₁/t₂/t₃ transformations and extinguishments match the narrative.&#x20;

---

## I. Migration guide for notebooks (single pass edits)

Replace patterns:

| Old (conflated)                                                                                       | New (separated)                                                                                                     |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `create_deliverable(issuer=me, holder=me, sku=..., quantity=..., unit_price=..., due_day=None)`       | `create_stock(owner_id=me, sku=..., quantity=..., unit_price=...)`                                                  |
| `create_deliverable(issuer=supplier, holder=buyer, sku=..., quantity=..., unit_price=..., due_day=t)` | `create_delivery_obligation(from_agent=supplier, to_agent=buyer, sku=..., quantity=..., unit_price=..., due_day=t)` |
| `transfer_deliverable(deliverable_id, from, to, qty)`                                                 | `transfer_stock(stock_id, from, to, qty)`                                                                           |
| “value of deliverables on asset side”                                                                 | “value of inventory (stocks); value of delivery obligations (liability side)”                                       |

---

## J. Acceptance criteria

1. **No self‑issued deliverables anywhere.** Inventory has no counterparty.
2. **Obligation and thing are distinct:** `DeliveryObligation` can exist without immediately pointing to a lot; settlement allocates lots deterministically by SKU.
3. **Settlement is deterministic & auditable:** Given the same starting state, day t settlement yields the same list of `StockTransferred` events and fully extinguishes matched obligations.
4. **Analysis shows the split:** financial trial balance still balances; inventory value shows under non‑financial assets; delivery obligations under non‑financial liabilities (both broken out by SKU).
5. **PDF example reproduces cleanly** with explicit goods movement and obligation extinguishment at each timepoint.&#x20;

---

## K. Optional (Stage 2, after green tests)

* **Reservation link (nice‑to‑have):** Add an optional `reserved_stock_id` (or list) on `DeliveryObligation` to lock specific lots at creation; the engine then uses reserved first, then free stock.
* **Stock allocation policies:** parameterize FIFO/LIFO/weighted‑average for partial lot allocation.
* **Richer observability:** include `allocation_plan` in `DeliveryObligationSettled` events (list of (stock\_id, qty) used).

---

### Why this solves the core issue

* It **eliminates** the conceptual bug (inventory was masquerading as a bilateral contract).
* It **simplifies settlement** (no magic reconstruction of “the same” deliverable; just move goods).
* It **clarifies reporting** (inventory vs. promises are separated in analytics).
* It **matches** your design goals for time‑based execution of entries and clean extinguishment of matched items across timepoints.&#x20;

If you’d like, I can next produce concrete file diffs/skeletons for the key modules (`system.py`, `settlement.py`, `balances.py`) following the checklist above.
