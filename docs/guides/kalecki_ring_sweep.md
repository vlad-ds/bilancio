# Kalecki Ring Sweep CLI

The `bilancio sweep ring` command compiles Kalecki ring scenarios across grids, frontier searches, and Latin Hypercube samples, then runs analytics for each case.

## Quick Start

```bash
# default grid only
PYTHONPATH=src .venv/bin/python -m bilancio.ui.cli sweep ring

# grid + LHS + frontier search with custom bounds
PYTHONPATH=src .venv/bin/python -m bilancio.ui.cli sweep ring \
  --lhs 25 \
  --kappa-min 0.2 --kappa-max 6 \
  --c-min 0.1 --c-max 4 \
  --mu-min 0.0 --mu-max 1.0 \
  --frontier
```

Outputs land under `out/experiments/<timestamp>_ring/`:

- `registry/experiments.csv`: run metadata, results, error states.
- `runs/<run_id>/`: scenario yaml, run HTML transcript, events/balances/metrics exports.
- `aggregate/results.csv`: per-run summary metrics (phi_total, delta_total, max G_t...).
- `aggregate/dashboard.html`: lightweight dashboard summarizing the sweep.

## Key Flags

- `--grid/--no-grid`: enable the coarse grid (`kappa`, `c`, `mu` sets from plan).
- `--lhs N`: add `N` Latin Hypercube samples across specified ranges.
- `--frontier`: bisection per (`c`, `μ`) cell to bracket minimal liquidity.
- `--monotonicities`: comma-separated bias values for the payable ordering (`-1` asc, `0` random, `1` desc). Use `--monotonicity-min`/`--monotonicity-max` to span a range in LHS mode.
- `--q-total`: fix day-1 dues (`S1`) for all generated scenarios.
- `--liquidity-mode`: choose `single_at` (default, seeded at one agent) or `uniform`.
- `--config PATH`: load sweep settings from a YAML file. Explicit CLI flags override YAML values.

Each run uses the ring generator (`ring_explorer_v1`) so scenarios stay reproducible. Metrics bundle reuses the day-level analytics (`write_day_metrics_*`, `write_metrics_html`).

## YAML configs

Keep sweep options in a YAML file when sharing setups or rerunning the same experiment:

```bash
PYTHONPATH=src .venv/bin/python -m bilancio.ui.cli sweep ring \
  --config examples/kalecki/ring_sweep_config.yaml
```

Example `examples/kalecki/ring_sweep_config.yaml`:

```yaml
version: 1
out_dir: "out/experiments/expel_ring_sweep"
runner:
  name_prefix: "Kalecki Ring Sweep"
  n_agents: 5
  maturity_days: 5
  q_total: 500
  liquidity_mode: single_at
  liquidity_agent: H1
  base_seed: 42
  default_handling: expel-agent
grid:
  enabled: true
  kappas: [0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 6]
  concentrations: [0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 2, 3, 5]
  mus: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
  monotonicities: [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
lhs:
  count: 0
  kappa_range: [0.1, 6.0]
  concentration_range: [0.1, 6.0]
  mu_range: [0.0, 1.0]
  monotonicity_range: [-1.0, 1.0]
frontier:
  enabled: false
  kappa_low: 0.1
  kappa_high: 4.0
  tolerance: 0.02
  max_iterations: 6
```

Omit fields you do not need—the CLI will fall back to its defaults. Passing a flag on the command line always overrides the YAML value for that parameter.

### Monotonicity control

The `ring_explorer_v1` generator now accepts an optional Dirichlet ordering bias:

```yaml
params:
  inequality:
    scheme: dirichlet
    concentration: 1.0
    monotonicity: 0.75  # 1 → strictly descending, 0 → random, -1 → ascending
```

This `monotonicity` scalar only reorders the sampled payables; it does not alter the Dirichlet weights themselves. Use the Streamlit helper at `dashboards/monotonicity_demo/` to inspect how different values reshape the ring before wiring it into sweep configs.
