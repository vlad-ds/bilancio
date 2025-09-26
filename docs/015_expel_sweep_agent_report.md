# Experiment 015 – Expel-Agent Ring Sweep Report

## 1. Data validation
- Source tables: `out/experiments/expel_ring_sweep/aggregate/day_metrics_enriched.pkl`, `results.csv`, `global_counts.csv`.
- Core checks succeeded. Dues stayed within `[0, 499]`, settlement shares satisfied `0 ≤ φ_t ≤ 1`, arrears matched `δ_t = 1 − φ_t`, and when `M^peak_t > 0` the replayed velocity identity `v_t · M^peak_t = gross_settled_t` held.
- No negative liquidity gaps were observed. Each run’s `time_to_stability ≤ 3` days, matching the final simulated day.
- Default audit: 422 `AgentDefaulted` events appeared across 125 runs; every scenario triggered at least one expulsion and 76 runs expelled the full four debtors after the first day.

## 2. Global settlement outcomes
- Out of 266 day-level records with defined settlement share `φ_t`, 57% showed zero settlement, 40% were partial, and only seven days achieved full settlement. Median `φ_t` was 0, while the 90th percentile reached 0.62.
- Liquidity gaps (`G_t`) appeared in 18% of recorded days; when present their median size was 109 and the 90th percentile 246, signalling severe shortages before expulsion finished purging the ring.
- Intraday liquidity (`M^peak_t`) was deployed on 41% of days. Most sequences ran at unit velocity, yet top-performing runs achieved `v_t ≈ 3`, meaning the same cash recycled three times in a day before the final debtor failed.
- Every run reached the quiet-period stopping rule, but only 11 runs produced zero aggregate settlement; the rest captured partial value before the last agents were expelled.

## 3. Control-axis effects
### Debt scale κ (total obligations)
- Light leverage (κ ≤ 1) produced no liquidity-short days and average `φ_total ≈ 0.20`. Increasing κ to 2 created liquidity gaps in 28% of day-records, while κ = 4 pushed that share to 64% and cut mean settlement to ≈0.10 (see `aggregate/summary_debt_scale.csv`).
- Larger κ leaves more principal stranded once a default occurs; expelling the debtor converts that stranded obligation into a permanent loss before downstream creditors can recycle funds.

### Dirichlet concentration c (payable inequality)
- Unequal due profiles (c = 0.2) yielded high average settlement (≈0.22) because one or two claims could clear before the weakest debtor was expelled, but the same scenarios sustained large liquidity gaps (`G_mean ≈ 35`, `HHI^+ = 1`).
- As c increases towards 5, payables flatten: liquidity gaps shrink (`G_mean ≈ 9`), and the share of liquidity-short days drops to ≈11%, yet aggregate settlement stays around 0.19 because defaults still arrive quickly and wipe out the remaining dues.

### Maturity misalignment μ
- μ ≤ 0.25: first-day settlement survives, with mean `φ_t ≈ 0.23` and stabilization in one day.
- μ ≥ 0.5: first-day `φ_t` collapses to zero across the sweep (`summary_misalign.csv`), and the model needs the full three-day horizon to finish expelling debtors. Later maturities can still settle if surviving agents hold enough cash, but total recovery remains ≈0.16–0.22.
- The cliff between μ = 0.25 and μ = 0.5 marks the parameter region where staggered maturities allow surviving payers to operate after defaults, versus synchronized dues that force immediate contagion.

## 4. Mechanism deep dives
### Run grid_0e944bafe1a9 (κ = 0.25, c = 5.0, μ = 0.0)
- Day-one metrics (`runs/grid_0e944bafe1a9/out/metrics.csv`) show `φ₁ = 0.7369`, `G₁ = 0`, `M^peak₁ = 122`, `v₁ = 3.0`.
- Events (`…/events.jsonl`) reveal a clean relay: H1→H2→H3→H4 transfer cash across four payables before H5 partially pays H1 and defaults with a $65 shortfall. Debtor-share data highlights H5 as the sole loss absorber (`metrics_ds.csv`).
- Interpretation: equalized exposures and low leverage let liquidity circulate multiple times before the weakest debtor fails, delivering the sweep’s highest settlement ratio under expel-agent rules.

### Run grid_24e20fc157bb (κ = 2.0, c = 0.2, μ = 0.5)
- Day-one shortfall: `G₁ = 134`, `φ₁ = 0`. H2 and H5 default immediately (`events.jsonl`).
- Day two expels H3 after a small payable matures; day three sees the surviving bank (H1) settle its deferred obligation, giving `φ₃ ≈ 0.98` for the residual dues but only 0.22 of the original total.
- Debtor-share tables show the loss burden shifting from expelled agents on day one to H1 on day three, illustrating how expulsion can preserve later maturities once fragile nodes are removed, yet leaves the aggregate recovery capped by the remaining network size.

### Run grid_d9a8f05bde19 (κ = 4.0, c = 0.2, μ = 1.0)
- Heavy leverage plus staggered long maturities yields immediate contagion: `G₁ = 356`, `φ₁ = 0`, no intraday flow.
- H2 and H5 default on day one with zero payments; later days expel H4 and H3 when their obligations mature. No positive transfers occur (`metrics_intraday.csv` empty), so the ring ends with `φ_total = 0` despite completing the run.
- Mechanism: once upstream deficits exceed available cash, expulsions cascade through the remaining due schedule, freezing the system before any liquidity can circulate.

## 5. Key takeaways and next steps
- Expel-agent mode quarantines contagion but does not guarantee liquidity relief: once a debtor is expelled, any unpaid obligations become irrevocable losses unless maturities stagger sufficiently for survivors to operate later.
- κ and μ interact sharply: high leverage or synchronized maturities create instant zero-settlement states, while lower κ and staggered dues permit partial circulation and even high-velocity loops before the final expulsion.
- Unequal payables (low c) allow a few creditors to get paid before defaults, but concentrate liquidity gaps and leave the rest of the ring with nothing once the main debtor is removed.

Recommended follow-ups:
1. Insert additional μ grid points between 0.25 and 0.5 (at multiple κ values) to localize the on-time settlement cliff and test whether small timing adjustments avert mass expulsions.
2. Re-run a representative subset with policy overrides (e.g., alternate means-of-payment rankings or targeted reserve seeding in Phase A) to evaluate how liquidity support interacts with expulsion enforcement.
3. Compare against a control sweep without expulsion to quantify how much of the lost settlement is due to the expel rule versus pure liquidity scarcity, using the existing metrics exporters for a controlled diff.
