# Default Handling Modalities

Status: proposal
Owner: Codex implementation plan

## Objectives

- Support two default-handling modes selectable per simulation: the current fail-fast behavior and a new "expel on default" mode that removes the defaulting agent while allowing the run to continue.
- When the new mode is active and an agent fails to fully settle an obligation, mark the agent as defaulted, perform any partial payment that was possible, and cleanly unwind the agent from the system so remaining obligations are written off for all parties.
- Provide clear event logging (partial payment, default declaration, write-offs) and surface the agent's removal in exported reports and UI summaries.
- Preserve backward compatibility for existing scenarios and CLI usage that expect fail-fast semantics.

## User Stories

- *Scenario authors* choose whether a single default should abort the run or be absorbed while other agents continue.
- *Risk analysts* can inspect partial payments and the resulting write-offs in event logs and exported reports.
- *Simulation operators* see that defaulted agents disappear from balances, scheduled actions, and future settlement attempts.

## Configuration Schema & CLI

1. **Scenario Config**: add `run.default_handling: Literal["fail-fast", "expel-agent"]` (default to `"fail-fast"`). Update `RunConfig` in `src/bilancio/config/models.py` and ensure YAML loader (`config/loaders.py`) and validators accept the new field.
2. **CLI Overrides**: extend `bilancio.ui.cli.run` to accept `--default-handling {fail-fast,expel-agent}`. Pass the override through to the run configuration applied to the system.
3. **Backward Compatibility**: when the field is absent, treat it as `fail-fast`. Document the new option in scenario cheat sheets and CLI help.

## System State Extensions

1. Add `defaulted_agent_ids: set[str]` (or list) to `SystemState` (`src/bilancio/engines/system.py`) to track agents that have defaulted.
2. Introduce `default_mode` attribute on `System` (populated from config) so settlement logic can branch without repeatedly consulting config objects.
3. Consider an `AgentStatus` enum or flag on `Agent` objects to mark `defaulted=True`, aiding filters in analysis layers.

## Core Workflow Changes

### Default Trigger Points

- `settle_due(...)` in `src/bilancio/engines/settlement.py` currently raises `DefaultError` when a payable cannot be fully paid.
- `settle_due_delivery_obligations(...)` raises `DefaultError` when stock is insufficient.
- Other operations that raise `DefaultError` (e.g., manual transfers) should also respect the new mode; evaluate call sites that catch/raise `DefaultError`.

### Handler Abstraction

1. Introduce `handle_default(system, *, debtor_id: str, contract_id: str, kind: Literal["payable","delivery"], amount_due: Decimal, amount_paid: Decimal, shortfall: Decimal)` in settlement module (or a dedicated `defaults.py`).
2. This helper performs the expel flow when `system.default_mode == "expel-agent"`; otherwise it re-raises `DefaultError` to preserve fail-fast behavior.

### Partial Payment Recording

- Modify `_pay_with_*` helpers to return both amount paid and a structured log of what was transferred so we can report partial settlement.
- When default occurs with some `amount_paid > 0`, emit a `PartialSettlement` event with fields: `debtor`, `creditor`, `contract_id`, `amount_paid`, `shortfall`, `means_used`.
- Ensure the payable/delivery contract is removed even if not fully satisfied (so it disappears from balance sheets). Attach metadata (e.g., `written_off=True`) to events for downstream analytics rather than mutating removed contracts.

### Agent Expulsion Flow

When expelling:
1. Record the default in state: add agent id to `defaulted_agent_ids` and optionally mark on the `Agent` object.
2. Emit `AgentDefaulted` event capturing reason (`contract_id`, `shortfall`, `day`, `phase`).
3. Remove the agent from `system.state.agents` (or mark inactive) and detach from all registries:
   - Iterate through `asset_ids`, `liability_ids`, and `stock_ids`, removing any associated contracts/stocks from the system state.
   - For each counterparty affected by these write-offs, remove the contract references from their asset/liability lists and log `ObligationWrittenOff` events (include `counterparty`, `contract_id`, `amount`, `direction`).
4. Handle scheduled actions: purge any future `scheduled_actions_by_day` entries that reference the defaulted agent to avoid executing actions for an absent agent (log `ScheduledActionCancelled` events as needed).
5. Ensure aliases referencing removed contracts are deleted.

### Continuing the Simulation

- After handling the default, ensure settlement loops skip the remaining logic (since contract already removed) but do *not* raise an exception so the day completes.
- Update `run_day` / `run_until_stable` loops to detect `default_mode == "expel-agent"` and adjust messaging: warn that a default occurred but continue processing subsequent days.
- For `fail-fast`, behavior remains unchanged.

## Event & Reporting Updates

1. Extend event schema (where we log dicts) to include new kinds: `PartialSettlement`, `AgentDefaulted`, `ObligationWrittenOff`, `ScheduledActionCancelled`.
2. Update HTML/console renderers to display these events with clear styling and narrative (e.g., highlight partial vs. full settlements).
3. Ensure exports (CSV/JSONL) include the new event kinds and fields; update `decimal_default`/serialization if necessary.
4. Analytics helpers (`analysis/balances.py`, visualization) must ignore removed agents and not expect obligations to be present.

## Policy Engine Considerations

- When an agent defaults, the policy engine should no longer attempt settlements or clearings for that agent. Ensure `settle_due` iterates over due contracts snapshot before modifications, and post-expulsion the agent is excluded from subsequent cycles.
- If the defaulted agent is a bank or central bank, assess systemic implications; document assumptions and add guardrails if we elect to forbid certain kinds from defaulting in the expel mode.

## Tests

1. Unit tests for `handle_default` covering both modes (fail-fast raising vs. expel continuing).
2. Scenario-style tests simulating:
   - Payable default with partial payment.
   - Delivery obligation default with zero partial fulfillment.
   - Multiple defaults across days ensuring other agents continue operating.
   - Scheduled action referencing defaulted agent verifying cancellation.
3. Regression tests for exports and UI renderers (snapshot tests for new event kinds if feasible).

## Documentation & Samples

- Update scenario cheat sheet and README to describe the new `default_handling` option and behavioral differences.
- Provide example scenario under `examples/scenarios/` demonstrating expel mode (e.g., firm default leading to write-offs but continued operation for others).
- Extend `docs/exercises_scenarios.md` or a new tutorial to walk through analyzing defaults with the new events.

## Migration & Deployment

- No data migration required; the config field defaults preserve existing behavior.
- Communicate change in release notes; highlight that defaulting agents now generate explicit events.

## Open Questions

- Should assets owned by the defaulted agent be seized/redistributed or simply removed? (Plan assumes removal; confirm with stakeholders.)
- Do we need to reflect residual losses (e.g., negative equity) somewhere, or is removing contracts sufficient?
- How should interbank reserve positions be handled when a bank defaults mid-day? Need rules for clearing outstanding reserve contracts.

