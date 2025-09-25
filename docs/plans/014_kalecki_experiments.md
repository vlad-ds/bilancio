Below is a concrete plan to standardize the 3 variables, generate ring scenarios at scale, export metrics, and aggregate results for pattern-finding. It fits v1.0 concepts (agents as balance sheets, time-steps, settle-or-default) and the current CLI, exports, and Kalecki metrics already present in the codebase.     

---

## 0) Outcomes

* One YAML “generator” spec for ring experiments.
* A deterministic scenario compiler that emits runnable YAMLs.
* A sweep runner with experiment registry and reproducible folder layout.
* Per-scenario exports: events.jsonl, balances.csv, metrics.json/csv, metrics.html.
* A single aggregated CSV and HTML report across all runs.

---

## Implementation Notes (2024)

- `ring_explorer_v1` generator lives in `src/bilancio/scenarios/generators/ring_explorer.py` and is wired through the config loader. Generator specs compile automatically when used as `scenario_file`.
- `bilancio sweep ring` drives grid/frontier/LHS sweeps, writing outputs under `out/experiments/<timestamp>_ring/` and aggregating to `results.csv`/`dashboard.html`.
- Registry + dashboard helpers sit in `bilancio.analysis.report` alongside existing metrics writers.

---

## 1) Standardize the three variables

Define canonical, dimensionless controls:

1. **Debt vs Liquidity ratio** `κ`
   `κ = S₁ / L₀`, where `S₁` is total dues on Day 1 and `L₀` is initial cash in system. Target by scaling Q or L₀. Metrics use `S_t` and liquidity gap already. 

2. **Distribution inequality** `ι`
   Use Dirichlet concentration `c` for the vector of ring payables `{Q_i}` with `sum Q_i = S₁`. Small `c` ⇒ high inequality; large `c` ⇒ near-equal. Optionally back-calculate and record realized HHI⁺ for creditors. 

3. **Maturity misalignment** `μ`
   Normalized lead–lag between each agent’s outbound payable and inbound receivable. Implement by due-day offsets around the ring:

* `μ=0`: all due Day 1 (aligned).
* `μ∈(0,1]`: spread inbound vs outbound over days 1..D so outbound leads inbound by a controlled offset distribution.

Keep the current settlement loop and default handling as in the baseline until policy work. (Baseline Kalecki ring exists at `examples/kalecki/kalecki_ring_baseline.yaml`.) 

---

## 2) Generator spec (YAML)

Add a “meta-generator” that compiles to standard scenario YAML before run.

```yaml
version: 1
generator: ring_explorer_v1
name_prefix: "Kalecki Ring Sweep"
params:
  n_agents: 5                  # ring size
  seed: 42
  # Variable 1: debt–liquidity
  kappa: 1.25                  # target κ = S1 / L0
  liquidity:
    allocation: {mode: "single_at", agent: "H1"}  # or "uniform"|"vector"
  # Variable 2: inequality
  inequality:
    scheme: "dirichlet"
    concentration: 0.6         # c
  # Variable 3: misalignment
  maturity:
    days: 3                    # horizon
    mode: "lead_lag"
    mu: 0.5                    # normalized misalignment
  # Fixed domain details
  currency: "USD"
  Q_total: 500                 # optional if solving from κ and L0
  policy_overrides: {}         # keep empty for baseline
compile:
  out_dir: "out/experiments/2025-09-17_ring"
  emit_yaml: true
```

**Compiler rules**

* Choose `Q_total` and `L0` to hit `κ`. If `Q_total` omitted, derive from chosen `L0` and `κ`.
* Draw `{Q_i}` from Dirichlet(c) and scale to `Q_total`.
* Place initial cash per `allocation`.
* Assign due days by a ring-consistent lead–lag kernel parameterized by `μ` over `1..days`.
* Emit a canonical scenario YAML with `initial_actions`, `create_payable` rows, and `run: {mode: until_stable, ...}`. Use the existing export knobs so balances CSV and events JSONL are produced. 

---

## 3) Orchestration and outputs

**CLI flow per scenario**

1. `bilancio run <scenario.yaml> --html <run.html>` to execute and export balances CSV and events JSONL (already wired). 
2. `bilancio analyze --events <events.jsonl> --balances <balances.csv> --out <metrics.csv> --html <metrics.html>` to compute Kalecki metrics per day and summary. (Analyze subcommand and metrics exist: `S_t, \u0305M_t, α, φ/δ, M^peak, v_t, HHI⁺, DS shares, G_t`.)  

**Experiment registry**

* `experiments.csv` with columns: run_id, seed, n_agents, κ, c, μ, realized_HHI_plus, realized_S1, L0, outputs paths, status.
* `results.csv` joined on run_id with key outcome metrics: `φ_total`, `δ_total`, `max_G_t`, `α_1`, `M^peak_1`, `v_1`, time-to-stability, etc. 

**Folder layout**

```
out/experiments/2025-09-17_ring/
  registry/experiments.csv
  runs/<uuid>/
    scenario.yaml
    run.html
    out/
      balances.csv
      events.jsonl
      metrics.csv
      metrics.html
aggregate/
  results.csv
  dashboard.html
```

A sample metrics HTML already exists for the baseline; match that style. 

---

## 4) Sampling design

**Phase 1: coarse grid**

* κ ∈ {0.25, 0.5, 1, 2, 4}
* c ∈ {0.2, 0.5, 1, 2, 5}
* μ ∈ {0, 0.25, 0.5, 0.75, 1}
  Run 125 points. Record day‑1 and run‑end metrics.

**Phase 2: frontier search**

* For each (c, μ) cell, bisection on κ to bracket minimal liquidity for full settlement (`κ*` where `δ_total` flips from 0 to >0; compare with `\u0305M_t`). Output `κ*` surface and gap to measured `\u0305M_1 / L0`. 

**Phase 3: space‑filling**

* Latin Hypercube, N=100 across [κ_min, κ_max] × [c_min, c_max] × [μ_min, μ_max].
* Rank “interesting” runs by large `α_1`, high `v_1`, near‑zero `φ_total` cliffs, or maximal `G_t`. 

---

## 5) Code placement and tasks

**A. Scenario generation**

* `src/bilancio/scenarios/generators/ring_explorer.py`

  * `RingExplorerParams` dataclass with (n_agents, κ, liquidity, inequality(c), maturity(μ, days), seed).
  * `compile(params) -> ScenarioConfig`.
* `src/bilancio/config/models.py`

  * Add `GeneratorConfig` union and schema.
* `src/bilancio/config/loaders.py`

  * Detect `generator:` and route to compiler, then return a regular `ScenarioConfig`.
* `tests/scenarios/test_ring_explorer.py` with deterministic seeds.

**B. CLI**

* `bilancio sweep ring --grid ...` and `--lhs N`

  * Generates run set, writes registry, executes `run` then `analyze` per row, captures paths and exit status.
* `bilancio analyze` already exists; just reuse. 

**C. Metrics aggregation**

* `src/bilancio/analysis/report.py`

  * `aggregate_runs(registry.csv) -> results.csv`
  * `render_dashboard(results.csv) -> dashboard.html`
    Use existing visualization primitives. 

**D. Exports**

* Reuse current exporters for balances CSV and events JSONL from the run UI. 

---

## 6) Validation and invariants

* Sanity: totals match, number of payables = n_agents, ring connectivity preserved.
* Targets: realized `κ` within tolerance; Dirichlet draw recorded; realized HHI⁺ computed. 
* Time semantics: set literal due days and use `run_until_stable`. 

---

## 7) Runbook (example)

1. **Compile grid**

```
bilancio sweep ring \
  --out out/experiments/2025-09-17_ring \
  --grid "kappa=0.25,0.5,1,2,4" \
  --grid "c=0.2,0.5,1,2,5" \
  --grid "mu=0,0.25,0.5,0.75,1" \
  --n-agents 5 --seed 42
```

2. **Analyze and aggregate**

```
bilancio sweep aggregate --root out/experiments/2025-09-17_ring
```

Produces `aggregate/results.csv` and `aggregate/dashboard.html`.

(Command names shown as desired interface; implement via the sweep CLI noted above. The underlying `run` and `analyze` pieces already exist.)  

---

## 8) What to inspect

* `φ_total` vs κ at fixed (c, μ) to estimate `κ*` curves; compare to `\u0305M_1 / L0`.
* Regions of high `α_1` and high `v_1` with low `M^peak_1` (efficient netting).
* Stress corners: high κ, low c, high μ → defaults and large `G_t`. 

---

## 9) Alignment with v1.0

This stays within v1.0: agents and entries, timepoints, activation, settlement or default, plus analysis outputs. Later policy toggles can be layered on top. 

---

## 10) Acceptance criteria

* Given a seed and (κ, c, μ), the compiler emits a valid ring YAML.
* Running it yields balances.csv, events.jsonl, metrics.csv/html per scenario.
* The sweep registry and aggregated CSV exist with all variables and outcomes joined.
* Re-running with same seed reproduces metrics within tolerance.
* A baseline run reproduces existing Kalecki ring metrics outputs. 

If you want, I can draft the exact `RingExplorerParams` dataclass, the compiler pseudocode, and the registry schema next.
