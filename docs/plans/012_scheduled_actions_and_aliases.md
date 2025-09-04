# Minimal Mid‑Simulation Actions: Scheduled B1 + Settlement B2, Aliases, and Claim Transfer

Status: proposal
Owner: Codex implementation plan

## Objectives

- Enable deterministic mid‑simulation actions while preserving current phase semantics.
- Keep Phase A reserved (unchanged). Execute user‑authored actions at the start of Phase B.
- Split Phase B into two subphases for clarity:
  - B1: scheduled actions (explicit, author‑driven)
  - B2: automated settlements (payables and delivery obligations)
- Add explicit claim reassignment via `transfer_claim`, referencing contracts by alias or ID.
- Distinguish B1 and B2 in the rendered HTML (separate tables and headers).

## Phase Model (no change to A/C)

- Phase A: reserved (no scheduled actions here).
- Phase B1: execute scheduled actions for the current day.
- Phase B2: run automated settlements for obligations due that day.
- Phase C: intraday clearing (unchanged).

Implementation in `run_day(system)`:
- Log `PhaseA` (unchanged).
- Log `PhaseB` (start of Phase B bucket, unchanged).
- Log `SubphaseB1`, then execute scheduled actions for the day.
- Log `SubphaseB2`, then call `settle_due(system, current_day)`.
- Log `PhaseC`, then call `settle_intraday_nets(system, current_day)`.

## Configuration Schema Changes (Pydantic)

1) Aliases on created contracts (minimal surface, via small mixin or inheritance if convenient):
- Actions that create entries in `System.state.contracts` get an optional `alias: str`:
  - `mint_cash` (creates Cash instrument)
  - `mint_reserves` (creates ReserveDeposit instrument)
  - `create_payable`
  - `create_delivery_obligation`
- Optional (future): `create_stock` may accept a `stock_alias: str` mapped separately (stocks live in `state.stocks`, not `contracts`). Not required for claim transfer.

2) New action: `transfer_claim`
- Shape:
  - `action: "transfer_claim"`
  - `contract_alias: Optional[str] = None`
  - `contract_id: Optional[str] = None`
  - `to_agent: str`
- Validation rules:
  - At least one of `contract_alias` or `contract_id` must be provided.
  - If both are provided, they must resolve to the same contract (error if mismatch).
  - No selector/disambiguation: explicit reference only.

3) Scheduled actions list
- Add `scheduled_actions: [{ day: int (>=1), action: { <one action dict> } }]` to `ScenarioConfig`.
- Days align with settlement semantics (same indexing as `due_day`).

Notes:
- Keep `initial_actions` behavior unchanged (applied during setup only).

## Loader Changes

- `parse_action(...)`: recognize and parse `transfer_claim`.
- `load_yaml(...)`: preprocess `scheduled_actions` like `initial_actions` (e.g., Decimal conversion), but leave parsing to apply‑time.

## Engine State Changes

- `System.State` additions:
  - `aliases: dict[str, str]`  // alias → contract_id (for instruments in `state.contracts`)
  - `scheduled_actions_by_day: dict[int, list[dict]]`  // day → list of raw action dicts
  - (Optional/future) `stock_aliases: dict[str, str]` for `state.stocks` if we later alias stocks

## Apply / Execution Changes

- When handling create actions that accept `alias`:
  - After instrument creation (have the real id), store `system.state.aliases[alias] = instrument_id`.
  - Error on duplicate alias.

- `transfer_claim` behavior:
  - Resolve `contract_id`:
    - If `contract_alias` given: look up in `system.state.aliases`.
    - If `contract_id` given: use as‑is.
    - If both provided: ensure they resolve to the same id.
  - Reassign holder:
    - Remove the id from current holder’s `asset_ids`, add to `to_agent`’s `asset_ids`.
    - Update `instrument.asset_holder_id = to_agent`.
  - Log `ClaimTransferred` with: `contract_id`, `from`, `to`, `kind`, and key attributes (`amount`, `due_day`, `sku` when present).

- `apply_to_system(config, system)`:
  - Existing setup/apply for `initial_actions` remains, inside `system.setup()`.
  - After setup: translate `config.scheduled_actions` into `system.state.scheduled_actions_by_day[day].append(action_dict)` in insertion order.

## Simulation Loop Changes (B1/B2)

- `run_day(system)` updates:
  1. `system.log("PhaseA")` (unchanged)
  2. `system.log("PhaseB")` (unchanged)
  3. `system.log("SubphaseB1")`; execute all scheduled actions for `current_day` via `apply_action(...)`.
  4. `system.log("SubphaseB2")`; call `settle_due(system, current_day)`.
  5. `system.log("PhaseC")`; call `settle_intraday_nets(system, current_day)`.

## UI / HTML Export

- Keep console display unchanged initially (Phase A/B/C tables). Focus change on HTML export.
- `html_export.py`:
  - After we bucket events by A/B/C per day, split Phase B events into B1/B2 using the `SubphaseB1`/`SubphaseB2` markers:
    - New helper `_split_phase_b_into_subphases(events_B: List[dict]) -> (List[dict], List[dict])`.
    - Exclude `SubphaseB1`/`SubphaseB2` marker events from the tables.
  - Render three tables per day section:
    - `Phase B1 — Scheduled Actions`
    - `Phase B2 — Settlement`
    - `Phase C — Clearing`
  - Keep Day 0 (Setup) section unchanged.

## Error Handling

- Alias creation: raise if alias already exists.
- Alias lookup: raise if alias unknown.
- For `transfer_claim`, if both `contract_alias` and `contract_id` are provided, they must resolve to the same instrument; otherwise raise a clear error.
- `scheduled_actions[].day` must be >= 1.

## Backward Compatibility

- If `scheduled_actions` and aliases are not used, behavior is unchanged.
- Existing scenarios run as before; CLI flags unaffected.

## Rollout Steps

1. Add schema changes (models, loaders) with optional alias mixin for create‑actions.
2. Extend `System.State` with `aliases` and `scheduled_actions_by_day`.
3. Update `apply_action` for alias capture and `transfer_claim`.
4. Update `apply_to_system` to stage `scheduled_actions_by_day`.
5. Update `run_day` with B1/B2 subphase markers and execution order.
6. Update HTML export to render B1/B2 separately; exclude subphase markers from rows.
7. Author sample scenario (assignment at Day 2) to validate Phase B1 ordering; export HTML.
8. Docs: brief section on scheduled actions, aliases, and claim transfer.

## Future (Out of Scope Here)

- Interactive (REPL) step mode to enter actions at runtime, with transcript recorder that can emit `scheduled_actions` YAML.
- Stock aliases and stock‑level operations beyond delivery obligations.

