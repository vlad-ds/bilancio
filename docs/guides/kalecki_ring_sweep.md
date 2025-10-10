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
  maturity_days: 3
  q_total: 500
  liquidity_mode: single_at
  liquidity_agent: H1
  base_seed: 42
  default_handling: expel-agent
grid:
  enabled: true
  kappas: [0.25, 0.5, 1, 2, 4]
  concentrations: [0.2, 0.5, 1, 2, 5]
  mus: [0, 0.25, 0.5, 0.75, 1]
lhs:
  count: 0
  kappa_range: [0.2, 5.0]
  concentration_range: [0.2, 5.0]
  mu_range: [0.0, 1.0]
frontier:
  enabled: false
  kappa_low: 0.1
  kappa_high: 4.0
  tolerance: 0.02
  max_iterations: 6
```

Omit fields you do not need—the CLI will fall back to its defaults. Passing a flag on the command line always overrides the YAML value for that parameter.
