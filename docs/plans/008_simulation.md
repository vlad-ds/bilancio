## TL;DR (what to change)

1. **Introduce a “setup stage”** (phase flag on the system) so bootstrapping actions (mint cash, create stocks, seed obligations) are logged as **setup**, not as “day 0” simulation activity.
2. **Settle “today”, not “tomorrow”.** Change `run_day()` so Phase B and Phase C operate on **current\_day**, then increment the day counter. This removes the offset and makes due dates intuitive.
3. **Add a one‑button runner**: `run_until_stable(system, ...)` that advances days until no obligations remain (and no interbank nets to clear).
4. **Update the notebook** to: (a) build initial conditions inside `with system.setup(): ...`, (b) set due days literally (0 = today, 1 = tomorrow, …), (c) call `run_until_stable(system)`.

Everything below is the implementation plan your coding agent can follow.

---

## Where you are now (and why the confusion exists)

* `run_day()` currently **settles and clears for `next_day`**, then increments the clock. That’s why events for “Day 1” appear stamped under day 0, and the visualization works around it with text like “Day N (Day N+1 Settlements)”. See the current `run_day` body and the comment in the events viewer about “logged with the previous day's number.”&#x20;

  * `engines/simulation.py::run_day` settles `next_day` and clears `next_day`.&#x20;
  * `analysis/visualization.py::display_events_for_day` explicitly notes the “previous day” logging offset.&#x20;

* Settlement Phase B and clearing Phase C are already solid and modular:

  * `settle_due(system, day)` pays **payables** and **delivery obligations** where `due_day == day` (and handles fallback order by policy).&#x20;
  * `compute_intraday_nets` and `settle_intraday_nets` net **same‑day** `ClientPayment` events and move **reserves** or create **overnight payables** due the next day.&#x20;
  * `client_payment` logs `ClientPayment` for cross‑bank flows (the input to Phase C).&#x20;

* Non‑financial modeling is clean after your refactor:

  * **Inventory** is `StockLot` owned by an agent (no counterparty).
  * **Promises to deliver** are `DeliveryObligation` (bilateral, valued, with `due_day`).
  * Settlement moves **stock lots** FIFO and cancels the obligation.&#x20;

This is all the right machinery — the remaining work is about **time semantics**, **setup separation**, and an **independent runner**.

---

## Decision: settle **today** (current\_day), not “tomorrow”

**Why:**

* Due dates become literal and intuitive: an instrument with `due_day=7` is settled during **Day 7’s** run.
* Clearing uses the `ClientPayment` events **created today** (already stamped with `system.state.day`) — so Phase C should run on **current\_day**. This also aligns with how `compute_intraday_nets` filters events by the provided `day`.&#x20;
* It removes the need for visualization hacks like “Day N (Day N+1 Settlements)”.&#x20;

**Effect on overnight:** If Phase C creates an **overnight payable** due `current_day+1`, it will naturally be processed by Phase B **tomorrow** when `current_day` advances — exactly what we want.&#x20;

---

## Change set for your coding agent

### 1) Add a **setup phase** to the system (no breaking changes)

**Goal:** clean separation of *initial conditions* vs *simulation days* without changing your op APIs.

**Implementation (minimal):**

* Extend `State` with a phase flag:

  ```python
  # engines/system.py
  @dataclass
  class State:
      ...
      phase: str = "simulation"  # "setup" | "simulation"
  ```

* Add a context manager on `System`:

  ```python
  # engines/system.py (inside class System)
  from contextlib import contextmanager

  @contextmanager
  def setup(self):
      old = self.state.phase
      try:
          self.state.phase = "setup"
          yield
      finally:
          self.state.phase = old
  ```

* Tag events with phase in `System.log`:

  ```python
  def log(self, kind: str, **payload) -> None:
      self.state.events.append({
          "kind": kind,
          "day": self.state.day,
          "phase": self.state.phase,
          **payload
      })
  ```

  (Current `log` already stamps `day` from `state.day`; this change only adds `"phase"`.)&#x20;

* (Optional) Let visualization filter or group by `phase` (“Setup” vs “Simulation”). Update `display_events_detailed` to show “Setup” events in their own section; remove the “previous day” note (see section 3).&#x20;

**Notebook usage:**

```python
sys = System()
with sys.setup():
    # bootstrap agents, mint cash, create stocks, seed obligations, etc.
    sys.bootstrap_cb(CB(...))
    sys.add_agents([...])
    sys.mint_cash(hh.id, 10_000)
    sys.create_stock(firm.id, "MACHINE", 10, Decimal("1000"))
    sys.create_delivery_obligation(firm.id, hh.id, "MACHINE", 2, Decimal("1000"), due_day=0)
# From here on, phase = "simulation"
```

### 2) Fix `run_day()` time semantics (settle and clear **current\_day**)

**Change:**

```diff
# engines/simulation.py
-def run_day(system):
-    current_day = system.state.day
-    next_day = current_day + 1
-    system.log("PhaseA", day=current_day)
-    settle_due(system, next_day)
-    settle_intraday_nets(system, next_day)
-    system.state.day += 1
+def run_day(system):
+    current_day = system.state.day
+    system.log("PhaseA")
+    system.log("PhaseB")  # optional: helps timeline
+    settle_due(system, current_day)             # ✅ settle TODAY
+    system.log("PhaseC")  # optional: helps timeline
+    settle_intraday_nets(system, current_day)   # ✅ clear TODAY’S nets
+    system.state.day += 1
```

* Rationale: `settle_due` explicitly looks for `due_day == day` and `compute_intraday_nets` scans `ClientPayment` events whose `day` equals the passed day. Align both to `current_day`.&#x20;

**Knock‑ons to visualization:** remove the “Day N (Day N+1 Settlements)” labeling since it’s no longer true. See Section 3.&#x20;

### 3) Make event displays literal (no offset)

* In `analysis/visualization.py`:

  * Replace the special headings in `_display_events_detailed`:

    * For day 0: `📅 Day 0`
    * For day > 0: `📅 Day {day}`
  * Remove the docstring note in `display_events_for_day` about “events are logged with the previous day's number,” because it will no longer be correct after Step 2.&#x20;

### 4) Add a simple **independent runner**: `run_until_stable`

**File:** `engines/simulation.py`

**Design:** minimal API that loops days until stability:

```python
from dataclasses import dataclass

IMPACT_EVENTS = {
    "PayableSettled",
    "DeliveryObligationSettled",
    "InterbankCleared",
    "InterbankOvernightCreated",
    # (Optionally) cash/stock movements if you want them to count
}

@dataclass
class DayReport:
    day: int
    impacted: int
    notes: str = ""

def _impacted_today(system, day: int) -> int:
    return sum(1 for e in system.state.events if e.get("day") == day and e.get("kind") in IMPACT_EVENTS)

def _has_open_obligations(system) -> bool:
    for c in system.state.contracts.values():
        if c.kind in ("payable", "delivery_obligation"):
            return True
    return False

def run_until_stable(system, max_days: int = 365, quiet_days: int = 2) -> list[DayReport]:
    """
    Advance day by day until the system is stable:
    - No impactful events happen for `quiet_days` consecutive days, AND
    - No outstanding payables or delivery obligations remain.
    """
    reports = []
    consecutive_quiet = 0
    start_day = system.state.day

    for _ in range(max_days):
        day_before = system.state.day
        run_day(system)
        impacted = _impacted_today(system, day_before)
        reports.append(DayReport(day=day_before, impacted=impacted))

        if impacted == 0:
            consecutive_quiet += 1
        else:
            consecutive_quiet = 0

        if consecutive_quiet >= quiet_days and not _has_open_obligations(system):
            break

    return reports
```

* Why `quiet_days=2` by default? If Day *t* creates an **overnight** payable (Phase C), you want to give the system the next day for it to be settled before declaring “stable”. This rule handles that without inspecting due dates directly.

### 5) Notebook updates (so it “still works correctly”)

1. **Separate setup from simulation:**

   ```python
   sys = System()
   with sys.setup():
       # add CB, banks, firms/households
       sys.bootstrap_cb(CentralBank(...))
       sys.add_agents([Bank(...), Bank(...), Household(...), Firm(...)])
       # endow agents, seed inventory and obligations
       sys.mint_cash("HH1", 2000)
       sys.create_stock("FIRM1", "MACHINE", 10, Decimal("1000"))
       sys.create_delivery_obligation("FIRM1", "HH1", "MACHINE", 2, Decimal("1000"), due_day=0)
   ```

2. **Use literal due days** (`0 = today`, `1 = tomorrow`, …). Stop offsetting or “pretending tomorrow” in the notebook cells.

3. **Advance the simulation** either one day at a time:

   ```python
   from bilancio.engines.simulation import run_day
   run_day(sys)  # settles due today, clears today's nets
   ```

   …or until stable:

   ```python
   from bilancio.engines.simulation import run_until_stable
   report = run_until_stable(sys)
   ```

4. **Event display**: after Step 2 above, the helper now shows the real day; remove any “+1 day” explanations in markdown.

   ```python
   from bilancio.analysis.visualization import display_events, display_events_for_day
   display_events(sys.state.events, format="detailed")
   # or show a specific day literally:
   display_events_for_day(sys, day=0)  # shows what happened on day 0
   ```

5. **If the notebook still uses old `Deliverable` instruments**, replace with **stock + delivery obligations** as per refactor:

   * Create inventory with `create_stock(...)`
   * Create promises with `create_delivery_obligation(...)`
   * Let settlement move the stock and cancel the obligation automatically.&#x20;

---

## Tests to add or adjust

1. **Day semantics** (update if they assume “next day”):

   * A payable with `due_day = system.state.day` must be gone after **one** `run_day`.
   * `ClientPayment` made before `run_day` should be cleared (or overnighted) **that same day**.
     (Both mirror your existing integration tests but for the corrected timing.)&#x20;

2. **Setup phase tagging**:

   * Operations inside `with sys.setup():` log events with `phase="setup"`; outside, `phase="simulation"`.
   * Setup events should not affect day counters (which already holds).

3. **Runner stability**:

   * Scenario that requires an overnight on Day 0 should settle by Day 1, and `run_until_stable(..., quiet_days=2)` should stop on Day 2 (after two quiet days and no outstanding obligations).

4. **Visualization**:

   * Ensure no “previous day” language remains and days are shown literally.

---

## Why this meets V1.0

* **Temporal transformation** works end‑to‑end: obligations and deliveries settle on the due day; interbank nets clear the day they occur; overnights roll to the next day.&#x20;
* **Setup is cleanly separated** (no more “minting is a day‑1 event” confusion).
* **Independent runner** makes the project demo and automation easy: “run until nothing more happens.”
* **Accounting and invariants** remain intact (you already have strong checks, including stock ownership invariants).&#x20;

---

## References to the code you already have (for the agent)

* `engines/simulation.py::run_day` — change to settle/clear **current\_day**.&#x20;
* `engines/settlement.py::settle_due` and the `due_*` scanners — they operate on `== day`. Keep as is.&#x20;
* `engines/clearing.py::compute_intraday_nets/settle_intraday_nets` — they key off **event.day == day**. Keep as is; feed **current\_day**.&#x20;
* `ops/banking.py::client_payment` — logs `ClientPayment` for cross‑bank flows (Phase C input).&#x20;
* `domain/goods.py::StockLot` + `domain/instruments/delivery.py::DeliveryObligation` — non‑financial refactor you should rely on in the notebook.&#x20;
* `analysis/visualization.py` — remove offseted day language and (optionally) group by `phase`.&#x20;

---

## Nice‑to‑have (not required for V1.0)

* Return a **DayReport** from `run_day` (counts of settled items, overnights created, etc.) so notebooks can print a concise daily ledger.
* Add `PhaseB` / `PhaseC` logs (optional) for readability (the code above shows where).

---

If you want, I can draft the exact patch diffs for `run_day`, the setup context & event tagging, the runner function, and the visualization text tweaks; but the outline above is sufficient for your coding agent to implement quickly.
