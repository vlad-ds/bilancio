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

Each run uses the ring generator (`ring_explorer_v1`) so scenarios stay reproducible. Metrics bundle reuses the day-level analytics (`write_day_metrics_*`, `write_metrics_html`).
