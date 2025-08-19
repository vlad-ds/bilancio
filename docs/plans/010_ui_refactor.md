Perfect—here’s a **single-pass, greenfield refactor plan** that (1) unifies terminal + HTML rendering on one set of functions, (2) removes hard‑coding and duplication, (3) tightens error handling, and (4) lands complete tests. I’ve mapped the plan directly to your current tree so it’s easy to implement.&#x20;

---

## Goals

* **One rendering pipeline** used by both the CLI and HTML export (no forked logic).
* **No legacy/shims/back-compat**: remove deprecated deliverable paths and any dual-field event handling.
* **No duplication**: factor shared logic for balance tables, event formatting, and day summaries.
* **Tunable, not magic**: extract widths, thresholds, and labels into config.
* **Deterministic, tested output**: snapshot tests (“goldens”) for renderables + HTML.

---

## New presentation architecture (terminal & HTML share the same code)

> Replace “print inside functions” with “build renderables and return them.” CLI prints them; HTML export captures them with a `Console(record=True)` and calls `export_html()`. The same builder functions are used in both paths.

### 1) Introduce a small “view model + renderer” layer

**New package:** `src/bilancio/ui/render/`

* `models.py`

  * `AgentBalanceView`, `DayEventsView`, `DaySummaryView`
  * These are thin data holders (no Rich imports), built from domain/analysis.
* `formatters.py`

  * `EventFormatterRegistry`: `register(kind)(fn)` and `format(event) -> tuple[title:str, lines:list[str], icon:str]`
  * Canonicalizes **event.kind** (no `type` fallbacks). Unknown kinds use a safe generic formatter. This replaces the big conditional in event rendering. Your current display code already knows the shapes of events—encode them here once.&#x20;
* `rich_builders.py`

  * Pure functions that take the view models and **return** Rich renderables (`Table`, `Panel`, `Columns`, etc.). No console side effects.
  * Builders:

    * `build_agent_balance_table(balance_view) -> Table`
    * `build_multiple_agent_balances(balances) -> Columns`
    * `build_events_panel(day_events_view) -> Panel`
    * `build_day_summary(view) -> List[Renderable]`

**Why this works now:** your current Rich helpers in `analysis/visualization.py` **print directly** to a `Console` and internally juggle both “simple” and “rich” modes; that makes HTML capture harder and causes duplication in `html_export.py`. Switching to “return renderables” removes that duplication.&#x20;

### 2) Convert existing display helpers to return renderables

Refactor `src/bilancio/analysis/visualization.py`:

* Change:

  * `display_agent_balance_table(...)`
  * `display_multiple_agent_balances(...)`
  * `display_events(...)`
  * `display_events_for_day(...)`

From **print/side-effect** → **return renderables** (and provide tiny wrappers that still print for REPL convenience). Under the hood, these call the new `ui/render/rich_builders.py`. This removes duplication with `ui/html_export.py` entirely.&#x20;

### 3) Collapse HTML export into the CLI run path

* **Remove** `src/bilancio/ui/html_export.py` completely.
* In `src/bilancio/ui/run.py` (and/or `cli.py` command), create a **single** `Console(record=True, width=Settings.console_width)` instance.
* Use the new builders to get renderables; `console.print(...)` them once for terminal output.
* If `--html` was passed, finish by calling `console.export_html(inline_styles=True)` and write the string to the target file. This preserves all colors/emojis/styles without re-rendering logic. Your CLI already has the `--html` option; we just change **who** builds the content and **how** it is captured.&#x20;

---

## Greenfield cleanup (remove legacy and inconsistencies)

### 4) Remove deprecated “Deliverable” instrument and legacy settlement path

* Delete `src/bilancio/domain/instruments/nonfinancial.py` and all references to the `Deliverable` class.
* In `src/bilancio/engines/settlement.py`:

  * Remove `due_deliverables()` and `settle_due_deliverables()` and any calls to them.
  * Keep only `DeliveryObligation` + `StockLot` flow (already the preferred model). Today both flows exist; we keep the stock+delivery obligation path and delete the old one.&#x20;
* In `src/bilancio/domain/policy.py`:

  * Remove `Deliverable` entries from `issuers`/`holders`. Only `DeliveryObligation` remains for non-financial promises; inventory is `StockLot`.&#x20;
* In `src/bilancio/ops/primitives.py`:

  * Remove deliverable-specific keys from `fungible_key()` (SKU/unit\_price add-ons for `deliverable`), because `deliverable` is gone. Stocks are handled in `ops/primitives_stock.py`.&#x20;
* In `src/bilancio/analysis/balances.py`:

  * Keep `inventory_by_sku` and non-financial **liabilities** via `DeliveryObligation`.
  * For non-financial **assets**, keep the “claim to receive goods” side (that’s the asset-holder side of `DeliveryObligation`). Ensure the code stops heuristically checking `'deliverable'` kinds. It already key-paths via `is_financial()` and `valued_amount`; just ensure only `delivery_obligation` flows through this branch.&#x20;

### 5) Canonicalize events

* **Always** emit `kind` in `System.log()` (already true) and stop any code that falls back to `type`: remove `event.get("kind", event.get("type", ...))` variants in visualization and elsewhere. One field = fewer bugs. Your `System.log` writes `{"kind": kind, "day":..., "phase":...}` consistently; rely on it.&#x20;
* Standardize event payload keys used by formatters (e.g., `frm`, `to`, `amount`, `sku`, `qty`, etc.) to match what `engines/system.py`, `ops/banking.py`, and `ops/primitives_stock.py` currently log. Where short IDs are needed (e.g., stock split), perform safe shortening **in the formatter** with robust checks.&#x20;

---

## De-duplication & function boundaries

### 6) Balance table creation: one utility

Create `analysis/balance_views.py` (or extend `analysis/balances.py`) to expose a **single** function:

* `build_agent_balance_view(system, agent_id) -> AgentBalanceView`

Then all renderers (terminal/HTML) use this view. Your current `analysis/visualization.py` reconstructs table rows in multiple places; move that logic into a reusable view model builder.&#x20;

### 7) Day/event grouping: one place

Create `ui/render/events.py`:

* `group_events_by_day_and_phase(events) -> dict[day, dict[phase, list[event]]]`
* `build_day_events_view(system, day) -> DayEventsView`

This replaces the parallel grouping logic found in the current detailed display functions and anything that existed in `html_export.py`.&#x20;

---

## Remove magic numbers and hard-coding

### 8) Centralize UI settings

New `src/bilancio/ui/settings.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    console_width: int = 100        # used by Console(width=...) universally
    currency_denom: str = "X"       # default denomination
    html_inline_styles: bool = True
```

* Replace hard-coded widths like `width=120` in visualization/simple printing paths with `Settings.console_width`. The simple-print fallback in `analysis/visualization.py` includes `console_width = 120`; remove that magic number.&#x20;
* Any numeric thresholds previously buried in `html_export.py` (e.g., “0.01 tolerance”) are removed or made explicit constants in `settings.py`.

---

## Error handling & consistency

### 9) Narrow exceptions & make failures explicit

* Replace generic `except Exception` in UI layers with specific `ValueError`, `ValidationError`, etc., already defined under `core/errors.py`. The CLI already does specific panels for `FileNotFoundError`, config `ValueError`, etc.; extend the same style for render/export failures.&#x20;
* In event formatters, validate required keys and degrade gracefully with generic rendering if they’re missing.

---

## Performance & memory

### 10) Cheap caching (balance snapshots per day)

* In `ui/run.py` (or a new `ui/session.py`), after each day finishes, collect **lightweight** `AgentBalanceView` snapshots for agents being displayed and reuse them for both terminal print and HTML capture. No global `days_data` stuffing of full state copies.&#x20;

---

## File-by-file changes summary

* **Remove**: `src/bilancio/ui/html_export.py` (all HTML is produced by `Console(record=True)` capture).&#x20;
* **New**:

  * `src/bilancio/ui/render/models.py`
  * `src/bilancio/ui/render/formatters.py`
  * `src/bilancio/ui/render/rich_builders.py`
  * `src/bilancio/ui/settings.py`
* **Refactor**:

  * `src/bilancio/analysis/visualization.py`: return renderables; delegate to `rich_builders`. Remove printing-only pathways.&#x20;
  * `src/bilancio/ui/run.py`: single `Console(record=True)`; print once; export HTML if requested. (CLI already passes `--html`; just wire to exported string.)&#x20;
  * `src/bilancio/engines/settlement.py`: delete deliverable path; keep delivery obligations + stocks only.&#x20;
  * `src/bilancio/domain/policy.py`: drop `Deliverable` issuer/holder lines.&#x20;
  * `src/bilancio/ops/primitives.py`: remove deliverable branch in `fungible_key`.&#x20;
  * `src/bilancio/analysis/balances.py`: stop referencing `'deliverable'` by name; rely on `is_financial()` and the actual `DeliveryObligation` types for non-financial assets/liabilities; keep inventory via `StockLot`.&#x20;

---

## Tests to add (end-to-end and unit)

> Use pytest; include “golden” snapshots for Rich renderables and exported HTML.

1. **Rendering contract tests**

* `tests/ui/test_render_event_registry.py`

  * Ensures every known event in system ops has a registered formatter (at least generic).
  * Property-style: random subset of fields missing → still renders (generic).
* `tests/ui/test_render_balances.py`

  * Build `AgentBalanceView` from a small system and snapshot the **stringified** Rich table via `Console().render_str(table)`. (or serialize key cells and compare)
  * Multi-agent columns rendering snapshot.

2. **HTML export path (single pipeline)**

* `tests/ui/test_cli_html.py`

  * Run a tiny scenario (use existing examples) through CLI with `--html tmp.html`; assert file exists and contains scenario header text and at least one emoji (e.g., 💵). Your CLI already supports `--html`.&#x20;

3. **Scenario coverage**

* `tests/ui/test_rich_simulation_example.py`

  * Run `examples/scenarios/rich_simulation.yaml`; assert specific expected event kinds appear and balance totals move as expected. (You already have this scenario.)&#x20;

4. **Greenfield-only assertions**

* `tests/unit/test_no_legacy_deliverable.py`

  * Importing `domain.instruments.nonfinancial` raises `ImportError`.
  * No function references to `deliverable` kind remain.

5. **Engines**

* `tests/integration/test_settlement_only_delivery_obligation.py`

  * Create stocks + delivery obligation; assert settlement moves stock and cancels obligation; no deliverable usage. Your current `settlement.py` already has this logic; test validates it after cleanup.&#x20;

6. **Event grouping**

* `tests/unit/test_group_events_by_day_phase.py`

  * Feed a synthetic event list mixing PhaseA/B/C markers and ensure grouping/view matches. Your current display code groups in `_display_day_events`; we’ll centralize that logic and test it.&#x20;

---

## Acceptance criteria (“done”)

* Running `bilancio run ... --html out.html` prints to terminal **and** produces HTML that visually matches the terminal output (colors, emojis, tables) **without** any dedicated HTML export module.&#x20;
* No references to `deliverable` instrument remain; only `StockLot` + `DeliveryObligation` for non-financial flows. Settlement code contains no deliverable branch.&#x20;
* No function relies on `event['type']`; all use `kind`. Formatters handle missing fields gracefully.&#x20;
* No magic numbers: all widths/thresholds from `ui/settings.py`.
* New tests pass; snapshot/golden tests protect tables/events and exported HTML.
* `analysis/visualization.py` holds only lightweight wrappers or calls into `ui/render/*`; it no longer prints directly or duplicates logic.&#x20;

---

## Implementation sketch (just enough for the agent)

```python
# ui/render/formatters.py
_REGISTRY = {}

def register(kind):
    def deco(fn):
        _REGISTRY[kind] = fn
        return fn
    return deco

def format_event(e):
    fn = _REGISTRY.get(e.get("kind"))
    if not fn:
        # generic fallback
        return "• Event", [str(e)], ""
    return fn(e)

@register("CashTransferred")
def _fmt_cash(e):
    t = "💵 Cash transferred"
    lines = [f"{e['frm']} → {e['to']}: ${e['amount']}"]
    return t, lines, "💵"
```

```python
# ui/render/rich_builders.py
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

def build_agent_balance_table(view):
    t = Table(...)   # fill columns
    # add rows from view
    return t

def build_events_panel(day_view):
    # compose panels/sections per phase
    return Panel(...)
```

```python
# ui/run.py (or cli path)
from rich.console import Console
from bilancio.ui.settings import Settings
from bilancio.ui.render.rich_builders import build_day_summary

console = Console(record=True, width=Settings.console_width)
for day in range(...):
    # ... simulation
    for r in build_day_summary(view):
        console.print(r)

if html_output:
    Path(html_output).write_text(console.export_html(inline_styles=Settings.html_inline_styles))
```

---

### Why this plan matches the code you have

* You already have solid balance computation (`analysis/balances.py`) and Rich-based views (`analysis/visualization.py`). The problem is **side effects + duplication**: the display functions both build and print, while `html_export.py` re-implements pieces. Returning renderables and capturing them once removes the duplication and the long, hard-coded functions identified in review.&#x20;
* The domain has already moved to **StockLot + DeliveryObligation**; removing the legacy `Deliverable` code and settlement branch aligns with the recent refactor and simplifies balances + policy.&#x20;
* The CLI already exposes `--html`; wiring it to `export_html()` unifies the output path.&#x20;

If you want, I can turn this into a ready-to-execute **checklist** (file diffs order, commits, and exact test names), but the above is the single-pass, no‑compat plan you asked for.
