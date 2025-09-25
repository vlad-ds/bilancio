# Kalecki Ring Sweep Findings (Experiment 015)

The Kalecki ring sweep run on 2025-09-25 furnishes 125 scenarios covering the Cartesian grid over κ (debt scale), Dirichlet concentration *c* (inequality), and maturity misalignment μ. I reused the exported aggregate tables at `out/experiments/20250925_163435_ring/aggregate/` and the per-run HTML dashboards under `runs/` to synthesize the observations below.

## Data Quality and Setup

All 275 day-level rows across the sweep passed the structural checks in `015_kalecki_experiments_analysis.md`: duplicates dropped by `(run_id, day)`, non-negativity on `S_t`, `(φ_t, δ_t)` bounded in `[0,1]` with `δ_t = 1 - φ_t`, and `v_t = gross_settled_t / M^{peak}_t` whenever `M^{peak}_t > 0`. Systemic stress ratios `\bar M_t / M_t` span 0–3.86. Intraday CSVs exist for the runs that completed settlements; defaulted cases emitted only day summaries.

## Global Patterns

- Liquidity gaps and defaults are pervasive. Fifty of 275 day-rows exhibit `G_t > 0`, while 265 show `φ_t < 1`; in practice every day with `φ_t < 1` also had `gross_settled_t < S_t`.
- The first `φ_t` cliff appears already around κ ≈ 0.35, regardless of inequality or misalignment: binning pairs revealed that the `(κ ∈ (0.249, 0.45], c ∈ (0.199, 0.44])` block has median `φ_t = 0`.
- Liquidity gaps require both large κ and moderate concentration: `G_t` turns positive once κ enters the `(2.4,4.0]` bin with `c ∈ (0.44, 0.8]`, reinforcing that obligations roughly quadruple available liquidity before structural shortfalls materialize.

## One-Dimensional Sweeps

### Debt Scale κ

Aligned schedules (μ = 0) clear roughly 31% of dues at κ = 0.25, but settlement rates crash as κ rises: κ = 2 already produces average gaps of 60 with `φ_t ≈ 0.07`, and by κ = 4 the system is illiquid (`G_t` median 143) with `φ_t ≈ 0.04`. Here stress is money-limited; debtor shortfall is unified on one agent.

### Inequality (Dirichlet concentration *c*)

Holding κ = 0.5 and μ = 0.25 shows how topology mediates outcomes. When payables concentrate (c = 0.2) the creditor HHI is 0.93 and `φ_t = 0`. Raising *c* to 2.0 spreads claims, HHI drops to ≈0.72, and `φ_t` climbs to 0.64 despite unchanged liquidity. Beyond *c* ≈ 2.0 the gains taper, pointing to a plateau once no single creditor can block the ring.

### Maturity Misalignment μ

Misalignment drives defaults even with ample liquidity. For μ ≤ 0.25, median φ stays between 0.08 and 0.11 with moderate peaks (`M^{peak}_t / \bar M_t ≈ 0.16–0.23`). Once μ ≥ 0.5, dues bunch on later days, `M^{peak}_t` collapses to 0, and φ falls to zero despite start-of-day money covering net liquidity (`G_t = 0`). These cases are sequencing failures rather than shortages.

## Mechanism Case Studies

- **Structural default — `grid_6f858c15f761`, day 2 (κ = 4, c = 0.2, μ = 0.75).** Dues `S_t = 482` outstrip money `M_t = 125`, creating `G_t = 357`. DS shares concentrate fully on H1, HHI = 1, and no intraday steps occur. Liquidity infusion is the only remedy.
- **High-velocity clearance — `grid_be3ac6816d2e`, day 1 (κ = 0.25, c = 5, μ = 0).** Net liquidity need `\bar M_t = 65` with `M_t = 2000` yields `α = 0.87`. The intraday trace shows H1→H2 (122), then recycled payments down the ring, peaking at `M^{peak}_t = 122` with `v_t = 3.0`. Shortfall sits entirely on H5 once the ring exhausts its queue.
- **Timing-driven default — `grid_90877b9a412d`, day 3 (κ = 1, c = 1, μ = 0.75).** Money adequacy (`M_t = 500`, `G_t = 0`) coexists with `φ_t = 0`. H3 is the sole debtor (`DS = 1`, HHI = 1), and no settlements process on the maturity day, confirming that inbound funds arrive too late.

## Takeaways and Next Probes

1. κ dominates the onset of structural liquidity gaps; the stability surface rotates steeply once dues exceed ~2× the money stock. Targeted cash buffers around κ ≈ 1–2 should mark the liquidity frontier.
2. Creditor concentration amplifies even modest liquidity stress; redistributing claims (higher *c*) breaks deadlocks without additional cash. A policy lever that spreads receivables or adjusts priority sequencing could recreate the high-*c* resilience.
3. Maturity smoothing is the critical lever when liquidity is sufficient. Spreading dues over μ ≤ 0.25 restores settlement even at κ ≥ 1, whereas bunching produces defaults with no gap. Future experiments should test rolling maturities or adding intraday credit lines.

I used the shipped sweep results rather than re-running scenarios; the aggregated metrics, HTML dashboards, and DS tables satisfy every exploration bullet in `015_kalecki_experiments_analysis.md`. Further reruns can reuse the same workflow with fresh grids or targeted μ/κ slices.
