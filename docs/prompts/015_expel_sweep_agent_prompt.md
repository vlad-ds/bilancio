# Prompt: Analyze Kalecki Ring Sweep (Expel-Agent Mode)

You are an analysis agent coming in fresh—assume no prior knowledge of previous runs or write-ups. Your job is to examine the **expel-agent** sweep located at `out/experiments/expel_ring_sweep/`, understand how defaults propagate, and communicate the results clearly and intuitively.

## Context
- Experiment 015 sweeps a Kalecki ring with 5 agents across a grid of **debt scale κ**, **Dirichlet concentration c** (inequality of payables), and **maturity misalignment μ**.
- Every scenario was generated via `ring_explorer_v1` with total dues `S₁ = 500` and run using **default-handling = expel-agent** (the engine expels an agent after it defaults but keeps the simulation running).
- The sweep command already produced all artifacts under `out/experiments/expel_ring_sweep/`:
  - `registry/experiments.csv`: metadata for each run.
  - `runs/<run_id>/out/*.{csv,json,html}`: per-run events, balances, day metrics, debtor shares, intraday traces, dashboards.
  - `aggregate/results.csv`: one row per run with summary metrics.
  - `aggregate/dashboard.html`: aggregate visualization.
  - `aggregate/day_metrics.pkl` & `day_metrics_enriched.pkl`: pickled day-level tables (each day per run) with derived flags (stress ratio, bins, etc.).
  - `aggregate/summary_*.csv`, `pairwise_boundaries.csv`: helper summaries already computed, but you may recompute or validate them if useful.

## Tasks
1. **Load & Validate Data**
   - Use the aggregate outputs to build a clean day-level dataframe. Confirm key constraints: non-negative dues, `0 ≤ φ_t ≤ 1`, `δ_t = 1 − φ_t`, velocity identity when `M^peak_t > 0`.
   - Note how many defaults occur (count `AgentDefaulted` events) and confirm the system reaches stability in each run.

2. **Global Overview**
   - Quantify settlement outcomes under expel mode: distribution of `φ_t`, prevalence of liquidity gaps (`G_t > 0`), share of days with partial vs zero settlement, intraday activity (`M^peak_t > 0`, `v_t`).
- Present the global settlement patterns using only the expel-agent measurements in this sweep; avoid speculating about other modes unless you can infer contrasts from the provided data alone.

3. **Control Axes Analysis**
   - For each of κ, c, and μ, analyze how on-time settlement, liquidity gaps, and creditor concentration behave. Use the provided summaries or recompute medians/means per value.
   - Identify any thresholds or notable non-linearities (e.g., κ ranges where `φ_t` drops sharply, c values that change HHI⁺ patterns, μ levels where settlement collapses).

4. **Mechanism Deep Dives**
   - Pick at least three representative runs illustrating distinct behaviors (e.g., structural shortfall, partial settlement before expulsion, successful high-velocity clearance).
   - For each run, read its HTML dashboard and supporting CSVs to explain: who defaulted, which transfers occurred before expulsion, and what the key metrics (φ_t, G_t, HHI⁺, DS shares, intraday trace) reveal.

5. **Synthesize Findings**
   - Produce a human-friendly report that explains the results to someone new to the project. Define metrics inline so readers don’t need to know internal jargon.
   - Focus on intuition: why do certain parameter combinations succeed or fail under expel-agent rules? How does expelling debtors reshape settlement compared to pure liquidity shortage scenarios?
   - Suggest concrete next steps for future experiments (e.g., finer κ grid, alternative settlement priorities, maturity smoothing), grounding each suggestion in observations from this sweep.

## Deliverables
- A clear narrative (Markdown or plain text) covering the sections above.
- Any tables or charts can be referenced by path; avoid embedding large dumps, but summarize key numbers.
- Keep the analysis self-contained—no assumptions about previous write-ups or the fail-fast mode.

You have full read access within this repository. Use Python (via the existing virtualenv at `.venv/`) or other tooling as needed. When in doubt, prefer direct measurements from `out/experiments/expel_ring_sweep/` over derived assumptions.
