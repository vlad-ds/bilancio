# Kalecki Ring Sweep — Expel-Agent Mode

Experiment 015 explores a 5-agent Kalecki ring where debt size (κ), payable inequality (Dirichlet concentration *c*), and maturity misalignment (μ) vary across a 5×5×5 grid. Every scenario was run with **default-handling = expel-agent**, meaning a debtor that cannot finish a payment sequence is expelled, its remaining obligations are written off, and the simulation continues.

Outputs live under `out/experiments/expel_ring_sweep/`: per-run artifacts in `runs/`, a registry at `registry/experiments.csv`, and aggregates in `aggregate/` (CSV tables, dashboard, pickled data used below).

## Workflow Recap
- Generated 125 scenarios via `ring_explorer_v1` with S₁ = 500, liquidity seeded according to κ, and maturities spread over three days.
- Ran the grid sweep with: `bilancio.ui.cli sweep ring --default-handling expel-agent --out-dir out/experiments/expel_ring_sweep`.
- Exported day metrics (`metrics.csv`), debtor shares (`metrics_ds.csv`), intraday traces, and HTML dashboards; aggregated them using the built-in report pipeline.

## Metric Reference
- **S_t** — dues maturing on day *t*.
- **\bar M_t** — minimum net liquidity required if all flows net: \bar M_t = Σ_i max(0, outbound_i − inbound_i).
- **M_t** — start-of-day money (cash + deposits + reserves).
- **G_t = max(0, \bar M_t − M_t)** — liquidity gap that must be filled externally.
- **α_t = 1 − \bar M_t / S_t** — share of dues that can clear through circulation alone.
- **M^peak_t** — maximum prefix liquidity observed in the realized settlement sequence.
- **v_t = gross_settled_t / M^peak_t** (defined when M^peak_t > 0) — intraday velocity of money.
- **φ_t** — on-time settlement share; **δ_t = 1 − φ_t**.
- **HHI^+_t** — Herfindahl index over positive net creditor balances (creditor concentration).
- **DS_t(i)** — debtor i’s share of \bar M_t, highlighting who needs liquidity injections.
- Controls repeated across the grid: **κ = S₁ / L₀**, **c** (Dirichlet concentration for payables), **μ** (normalized maturity misalignment).

## Data Quality Checks
- 275 `(run_id, day)` rows; no duplicates after grouping.
- Constraints hold: `S_t ≥ 0`, `φ_t, δ_t ∈ [0,1]`, `δ_t = 1 − φ_t`, and whenever `M^peak_t > 0`, the velocity identity `v_t = gross_settled_t / M^peak_t` is satisfied.
- Stress ratios `\bar M_t / M_t` span `[0, 3.856]`, matching the expected κ-driven limits.
- The registry logs 422 `AgentDefaulted` events (median 4 per run). Expulsion never halted the simulator; every run reached a quiet state after defaults propagated.

## Global Patterns (Expel Mode)
- **Partial settlement becomes common.** Average day-level `φ_t` = **0.170** (median 0.0, 75th percentile 0.26). 114 of 275 day-rows show `φ_t > 0`, compared with complete collapse in strict fail-fast runs.
- **Liquidity cliffs persist.** 50 days exhibit `G_t > 0`, all within κ bins `(2.4, 4.0]` regardless of *c* or μ. Expulsion cannot conjure liquidity once structural shortfalls appear.
- **Default sequencing matters.** Pairwise binning shows φ falls below 0.9 as soon as κ crosses ~0.35 (bin `(0.249, 0.45]`) for moderate inequality, while liquidity gaps first appear when κ enters `(2.4, 4.0]` (`aggregate/pairwise_boundaries.csv`).
- **Intraday activity.** 41% of day-rows have `M^peak_t > 0` (money actually circulates before defaults); non-null velocities cluster near 1.09, with a single outlier at 3.0 when liquidity is abundant.

## One-Axis Sweeps
- **Debt scale κ** (`summary_debt_scale.csv`):
  - φ_mean hovers around 0.18 for κ ≤ 2 as a handful of payments clear before debtors fail.
  - κ = 4 drops φ_mean to 0.096 and pushes liquidity gaps on 64% of days; defaults quickly expel the main payer, freezing further settlement.
- **Inequality c** (`summary_ineq.csv`):
  - Low concentration (c = 0.2) yields φ_mean ≈ 0.22 despite HHI⁺ = 1.0, because the dominant creditor is serviced first while the key debtor still has cash.
  - High concentration (c = 5.0) reduces HHI⁺ to 0.55 but also lowers φ_mean to 0.16; spreading claims dilutes priority for early payments.
- **Misalignment μ** (`summary_misalign.csv`):
  - μ ≤ 0.25 keeps median φ above zero (0.08–0.21) and stress ratios high (≈0.8) because dues land when cash is available.
  - μ ≥ 0.5 produces φ_median = 0; even with expulsion, outbound dues lead inbound receipts, so the first debtor drained still defaults before their own payee cycle completes.

## Mechanism Snapshots
- **Liquidity triage before expulsion** — `grid_0f03d3bdc6c1` day 1 (`κ = 0.25`, `c = 0.2`, `μ = 0`). With only `M_t = 250` against `\bar M_t = 382`, the ring processes one $167 transfer before H2 and H5 default. Outcome: `φ_t = 0.33`, `G_t = 132`, and partial settlement logged (`runs/grid_0f03d3bdc6c1/out/metrics.html`, `metrics_intraday.csv`).
- **Cascade defaults with late settlement** — `grid_f56c164e8cae` (κ = 0.25, c = 0.5, μ = 0.5). H2, H5, and H3 default on days 1–2, yet day 3 still clears a $7 payable (φ = 0.7) before expelling H4. Expulsion keeps the simulator alive long enough for small obligations to finish (`runs/grid_f56c164e8cae/out/events.jsonl`).
- **Structural failure unchanged** — `grid_7ede287eda4a` day 2 (`κ = 4`, `c = 0.2`, `μ = 0.75`). `S_t = 482`, `M_t = 125`, gap `G_t = 357`; DS shows H1 bearing the entire shortfall, and HHI⁺ = 1. Expulsion logs the default but settles nothing: only supplemental liquidity would avert the wipeout (`runs/grid_7ede287eda4a/out/metrics.html`).
- **High-velocity clearance** — `grid_0e944bafe1a9` day 1 (`κ = 0.25`, `c = 5`, `μ = 0`). `α = 0.87`, `M^peak_t = 122`, `v_t = 3.0`; the ring recycles the same cash through all counterparties and lands φ = 0.74. Expulsion never triggers because cash suffices (`runs/grid_0e944bafe1a9/out/metrics_intraday.csv`).

## Takeaways for Expel-Agent Mode
1. **Partial settlement is the primary benefit.** Expulsion converts binary defaults into “pay what you can” events, lifting φ but leaving aggregate liquidity constraints untouched.
2. **Creditor order becomes a policy lever.** With expulsion, the earliest creditor in the queue captures remaining liquidity before the debtor is removed, making settlement priority and credit concentration crucial design choices.
3. **Maturity smoothing still matters.** When μ ≥ 0.5, settlements collapse despite expulsion. Staggering due dates or providing small inbound buffers remains essential if the goal is to sustain φ near 1 without external funding.

Next ideas: probe κ in finer increments around 1–2 under expel mode, experiment with alternative settlement orders, or add intraday credit lines to see whether partial settlements can cascade into full clearance without increasing cash.
