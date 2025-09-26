# Kalecki Ring Sweep Findings (Experiment 015)

Experiment 015 now covers the Kalecki ring under two default regimes. We previously inspected the fail-fast grid run (`out/experiments/20250925_163435_ring/`). This note refreshes the analysis after re-running the same 125-point grid with the new expel-and-continue mode.

## What Changed
- Added a `--default-handling` switch to the sweep command so we can pick `expel-agent` at runtime (`src/bilancio/ui/cli.py:45-88`).
- Propagated the choice through the sweep runner—scenarios now write `run.default_handling`, registry rows log the mode, and `run_scenario` receives the override (`src/bilancio/experiments/ring.py:95-386`).
- Launched the new grid with: 
  ```bash
  PYTHONPATH=src .venv/bin/python -m bilancio.ui.cli \
    sweep ring --out-dir out/experiments/expel_ring_sweep \
    --default-handling expel-agent
  ```
- Parsed the exports under `out/experiments/expel_ring_sweep/`, mirroring the workflow in `docs/plans/015_kalecki_experiments_analysis.md`.

## Metric Cheat Sheet
**S_t** — total dues on day *t*.

**\bar M_t** — minimum net liquidity if all flows could net. Shows structural need.

**M_t** — start-of-day money (cash + deposits + reserves).

**G_t = max(0, \bar M_t − M_t)** — liquidity gap that must be filled externally.

**α_t = 1 − \bar M_t / S_t** — share of dues clearable by circulation.

**M^peak_t** — maximum prefix liquidity observed in the realized settlement path.

**v_t = gross_settled_t / M^peak_t** — intraday velocity once a path exists.

**φ_t** — on-time settlement share; **δ_t = 1 − φ_t**.

**HHI^+_t** — Herfindahl of positive net creditor balances (concentration of inflows).

**DS_t(i)** — debtor i’s share of \bar M_t, highlighting who needs cash.

The control knobs remain **κ** (debt scale = S₁ / L₀), **c** (Dirichlet concentration), and **μ** (maturity misalignment).

## Data Health & Mode Comparison
- 275 day-level rows survived dedupe and all metric invariants held (no negative dues, `φ_t, δ_t ∈ [0,1]`, velocity identity respected).
- Liquidity stress: 50 days with `G_t > 0`, identical to the fail-fast run; all of them sit at κ ≥ 2 and show debtor HHI ≈ 1.
- Defaults now continue instead of aborting: we observed 422 `AgentDefaulted` events across the 125 runs (median 4 per run), yet the simulator reached a quiet state every time because expelled agents stop scheduling new actions.
- Settlement lift is material: average `φ_t` jumps from 0.032 in fail-fast to **0.170** with expulsion (`out/experiments/expel_ring_sweep/aggregate/day_metrics_enriched.pkl`), and 114/275 day-rows achieve `φ_t > 0` (previously 11/275).
- Non-zero intraday peaks appear on 41% of days (vs 14% before) because partial settlements now execute before debtors are removed.

Global tally: `out/experiments/expel_ring_sweep/aggregate/global_counts.csv` records 259 days with `φ_t < 1` (down from 265) and 259 with gross settlements below dues.

## Global Patterns Under Expulsion
- **Partial settlement dominates.** Once a debtor runs out of cash the engine logs a partial payment, writes off the residue, and expels the agent. That conversion of “all-or-nothing” failures into partial clears is what raises `φ_t`.
- **Liquidity cliffs remain.** κ ≳ 3.2 still guarantees `G_t > 0`, even though some dues settle before default (`pairwise_boundaries.csv`).
- **Velocity stays modest.** Most settlement paths recycle liquidity once (`v_t ≈ 1`), with a single high-velocity run at `v_t = 3.0` when liquidity dwarfs dues.

## One-Axis Sweeps (median φ still 0, but means shift)
- **Debt scale κ (`summary_debt_scale.csv`).** Means hover around 0.18 for κ ≤ 2 because several payments clear before debtors fail; κ = 4 collapses to 0.096 as the first big debtor wipes out liquidity. Liquidity gaps emerge for κ ≥ 2 in 27% of days, the same threshold as fail-fast.
- **Inequality c (`summary_ineq.csv`).** Counter-intuitively, the lowest concentration (c = 0.2, HHI⁺ ≈1) now yields the *highest* φ_mean (0.22) because the dominant creditor is paid first before the payer is expelled. High-c spreads the receipts, lowering HHI⁺ to ~0.55 and keeping φ_mean ≈0.16. Expulsion exposes the sequencing of who gets paid before the crash.
- **Maturity misalignment μ (`summary_misalign.csv`).** Median φ stays positive for μ ≤ 0.25 (0.08–0.21) and drops to zero once outbound dues significantly lead inbound cash. Means remain ≈0.16 even for μ ≥ 0.5 because residual obligations on calmer days still settle after the worst offenders are removed.

## Mechanism Snapshots
- **Structural shortfall persists — `grid_7ede287eda4a` day 2 (κ = 4, c = 0.2, μ = 0.75).** `S_t = 482`, `M_t = 125`, gap `G_t = 357`, DS mass on H1, HHI⁺ = 1. Expulsion removes the debtor but no settlement occurs (`out/experiments/expel_ring_sweep/runs/grid_7ede287eda4a/out/metrics.html`). Same verdict as fail-fast: only extra liquidity would help.
- **Liquidity triage before failure — `grid_0f03d3bdc6c1` day 1 (κ = 0.25, c = 0.2, μ = 0).** With `M_t = 250` against `\bar M_t = 382`, the ring delivers one $167 transfer (`metrics_intraday.csv`) before H2 and H5 default. φ jumps to 0.33 even though the gap remains `G_t = 132`.
- **Cascading defaults but late settlement — `grid_f56c164e8cae` (κ = 0.25, c = 0.5, μ = 0.5).** H2, H5, H3 each default on days 1–2, the system keeps running, and day 3 still clears a $7 payable from H1 to the expelled H2 (`events.jsonl`). The pipeline records a non-zero `φ_t = 0.7` on day 3.
- **High-velocity success remains — `grid_0e944bafe1a9` day 1 (κ = 0.25, c = 5, μ = 0).** Identical to the baseline best case: `α = 0.87`, `M^peak = 122`, `v_t = 3.0`, and φ = 0.74, showing that generous liquidity plus diversified creditors still dominate outcomes.

## Takeaways
- **Expulsion salvages partial throughput** without altering the structural liquidity frontier. For policy experiments, κ thresholds still identify when outside funding is mandatory.
- **Creditor order matters.** Under expulsion the first recipient in line captures the remaining cash. Varying payment priority could be as impactful as adding liquidity; testing alternate settlement orders is a natural next step.
- **Maturity smoothing still helps.** Even with expulsion, clustered dues (μ ≥ 0.5) leave φ medians at zero. Staggering maturities or adding small buffers to every agent remains the cleanest route to higher φ.

All artifacts referenced above live under `out/experiments/expel_ring_sweep/`. Re-running other slices (e.g., finer κ near 1–2 or a Latin Hypercube) will automatically honor the chosen default-handling mode via the new CLI flag.
