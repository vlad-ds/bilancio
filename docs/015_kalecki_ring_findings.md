# Kalecki Ring Sweep Findings (Experiment 015)

Experiment 015 asks how a five-agent Kalecki ring handles changing debt loads, payment concentration, and maturity timing. The sweep reuses the `bilancio` ring exploration stack: scenarios compiled by `ring_explorer_v1`, runs executed via `bilancio sweep ring`, and post-processing through the built-in analyzer that emits CSV, JSON, and HTML dashboards under `out/experiments/20250925_163435_ring/`.

## Experiment Workflow
- 125 scenarios span a Cartesian grid over debt scale (κ), Dirichlet concentration for due amounts (c), and maturity misalignment (μ).
- Each run exports `metrics.csv`, `metrics_ds.csv`, `metrics_intraday.csv`, and an HTML dashboard; these feed the aggregate tables in `aggregate/results.csv` and the companion `dashboard.html`.
- This report reads those shipped outputs rather than re-running simulations, following the checklist in `docs/plans/015_kalecki_experiments_analysis.md`.

## Metric Cheat Sheet
**S_t (total dues)** = sum of payment obligations maturing on day t. Intuition: workload the system must settle that day.

**\bar M_t (minimum net liquidity)** = sum over debtors of max(0, outbound − inbound) on day t. Intuition: cash the system needs even with perfect netting.

**M_t (start-of-day money)** comes from balances CSV (cash + deposits + reserves). Intuition: actual liquidity on hand when the day opens.

**G_t (liquidity gap)** = max(0, \bar M_t − M_t). Intuition: shortfall that forces default unless someone adds cash.

**α_t (netting potential)** = 1 − \bar M_t / S_t when S_t > 0. Intuition: share of dues that can clear through circulation instead of new cash.

**M^peak_t (operational peak)** = max_s P(s), where P(s) is prefix liquidity during the realized settlement replay. Intuition: worst intraday liquidity exposure.

**v_t (intraday velocity)** = gross_settled_t / M^peak_t when M^peak_t > 0. Intuition: how many times the same cash recycles intraday.

**φ_t (on-time share)** = settled_on_day_t / S_t. Intuition: fraction of dues that finish on schedule.

**δ_t (deferral/default)** = 1 − φ_t. Intuition: portion that slips or defaults.

**HHI^+_t (creditor concentration)** = Herfindahl index of positive net creditor balances. Intuition: how many creditors control incoming cash.

**DS_t(i) (debtor shortfall share)** = debtor i shortfall / \bar M_t. Intuition: which agents need liquidity injections.

**κ (debt scale)** = S_day1 / L0 in the generator. Intuition: ratio of dues to available liquidity.

**c (Dirichlet concentration)** controls how unequal dues are across the ring. Smaller c means a single creditor dominates.

**μ (maturity misalignment)** shifts when each agent’s inbound receivable arrives relative to its payable. Larger μ bunches dues on different days.

## Data Quality and Validation
- 275 day-level records entered analysis after dropping duplicates by `(run_id, day)`.
- Mandatory bounds held: `S_t ≥ 0`, `0 ≤ φ_t, δ_t ≤ 1` with `δ_t = 1 − φ_t`, and `v_t = gross_settled_t / M^peak_t` whenever `M^peak_t` was positive.
- Stress ratios `\bar M_t / M_t` range from 0.0 (ample cash) to 3.86 (money stock only a quarter of required net liquidity).
- Intraday traces exist for all settling runs; defaulted cases expose only summary tables, signaling that the simulator halted before clearing payments.

## Global Patterns
- Liquidity stress is common: 50 of 275 rows show `G_t > 0`, while 265 record `φ_t < 1`, and every late day also has `gross_settled_t < S_t`.
- The settlement cliff appears around κ ≈ 0.35: even mild debt loads can stall if topology and timing are hostile, giving median `φ_t = 0` within the `(κ ∈ (0.249, 0.45], c ∈ (0.199, 0.44])` bin.
- Structural gaps require both high κ and moderate inequality: `G_t` turns positive in the `(κ ∈ (2.4, 4.0], c ∈ (0.44, 0.8])` bin, implying dues roughly quadruple available money before the system truly runs dry.
- Intraday velocity is usually flat: 39 non-null `v_t` values cluster near 1.0, meaning money cycles once per day; only the best-funded rings reach `v_t ≈ 3`.

## Debt Scale (κ)
- Settlement success collapses once κ exceeds ~0.35; by κ = 2 the average gap is 60 and `φ_t` falls near 0.07 even with aligned maturities (μ = 0).
- κ = 4 highlights structural default: `G_t` medians reach 143 and debtor shortfall concentrates on one payer, signalling raw liquidity shortage.
- Intuition: κ measures how many dollars must clear per dollar of starting liquidity; above ~2 the ring lacks enough cash to circulate without external support.

## Inequality (Dirichlet concentration c)
- Holding κ = 0.5 and μ = 0.25, moving c from 0.2 to 2.0 drops creditor HHI from 0.93 to 0.72 and raises `φ_t` from 0.00 to 0.64.
- Gains flatten beyond c ≈ 2.0, reflecting diminishing returns once no single creditor can stall the flow.
- Intuition: spreading receivables prevents one “gatekeeper” from hoarding cash, so even modest liquidity can loop around the ring.

## Maturity Misalignment (μ)
- For μ ≤ 0.25, median φ sits between 0.08 and 0.11 with moderate peaks (`M^peak_t / \bar M_t ≈ 0.16–0.23`).
- Once μ ≥ 0.5, dues bunch on later days, `M^peak_t` collapses to 0, and φ drops to 0 despite `G_t = 0`; defaults stem from timing, not cash deficits.
- Intuition: when payers must settle before their own receivables arrive, the ring breaks even if the system has enough money in aggregate.

## Mechanism Snapshots
- **Structural default (`grid_6f858c15f761`, day 2; κ = 4, c = 0.2, μ = 0.75).** `S_t = 482` with only `M_t = 125` yields `G_t = 357`. DS shares place the entire shortfall on H1 and HHI = 1, so no settlements execute; only liquidity injections would repair the day.
- **High-velocity clearance (`grid_be3ac6816d2e`, day 1; κ = 0.25, c = 5, μ = 0).** `\bar M_t = 65` against `M_t = 2000` gives `α = 0.87`. The intraday trace shows H1→H2 (122) kicked off a cascade that recycles the same 122 units across the ring, peaking at `M^peak_t = 122` with `v_t = 3.0` before the queue empties onto H5.
- **Timing-driven default (`grid_90877b9a412d`, day 3; κ = 1, c = 1, μ = 0.75).** `M_t = 500` easily covers `\bar M_t = 104`, yet `φ_t = 0` and H3 holds DS = 1. The issue is sequencing: receivables arrive after payments fall due, so the simulator registers no settlement steps.

## Takeaways and Next Experiments
- κ sets the liquidity frontier: once dues exceed roughly twice the money stock the ring requires external funding. Next sweep: zoom κ ∈ [0.5, 2] with finer steps and optional central-bank cash buffers.
- Concentration is a topology lever: redistributing payables (higher c) or altering settlement priority should replicate the resilience seen when HHI drops below ~0.7.
- Maturity smoothing is essential when liquidity is adequate: testing staggered due dates or short intraday credit lines for μ ≥ 0.5 should reveal whether timing fixes can restore `φ_t ≈ 1` without new money.

All conclusions trace back to the archived sweep outputs in `out/experiments/20250925_163435_ring/`. Re-running the generator with new parameter slices can reuse the same validation and analysis workflow.
