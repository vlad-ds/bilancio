Below is a concise SOP your analysis agent can follow on this sweep. It includes the required context block, the exact metric set, zoom triggers, and expected outputs.

---

## 0) Put this **Context** block at the top of your reply

* **Goal.** Explore how defaults and liquidity stress emerge in a **ring settlement** system as we vary three variables: **debt size vs liquidity**, **distribution inequality**, **maturity misalignment**. We use day-level and intraday microstructure metrics to identify stable vs unstable regions. 
* **Scenario baseline.** Kalecki-style 5-agent directed ring. Equal dues in baseline. Only H1 holds cash at Day 0. All dues initially Day 1 (baseline) unless varied by misalignment.
* **Outputs we read.** Sweep CSV with per-day metrics for each run; per-day HTML dashboards; per-day intraday step traces when available. Metrics and the analyze CLI are defined in the codebase and report exporter.
* **Metric set.** $S_t, \bar M_t, M_t, G_t, \alpha_t, M^{peak}_t, v_t, \phi_t, \delta_t, HHI^+_t, DS_t(i)$. Definitions below. 

---

## 1) Load and sanity‑check data

1. Load sweep CSV: `/mnt/data/ff2249ed-f86c-4a0b-8c68-05606037f595.csv`. Expect columns including:
   `scenario_id, day, S_t, Mbar_t, M_t, G_t, alpha_t, Mpeak_t, gross_settled_t, v_t, phi_t, delta_t, n_debtors, n_creditors, HHIplus_t` and the three control variables (names may differ; infer from headers). The day table in the exporter uses these fields. 
2. If available, also load debtor‑share table and intraday steps from the run outputs; the analyzer writes them alongside the day metrics. 
3. De‑duplicate by `(scenario_id, day)`. Drop rows with missing `day` or `S_t`.
4. Basic checks: `S_t ≥ 0`, `0 ≤ φ_t ≤ 1`, `δ_t = 1 − φ_t` if present, `v_t = gross_settled_t / Mpeak_t` when `Mpeak_t > 0`. 

---

## 2) Establish metric semantics once (don’t re-derive)

* **Total dues** $S_t$: all obligations maturing on day *t*.
* **Min net liquidity** $\bar M_t$: sum of debtor shortfalls if dues are perfectly offset.
* **Start‑of‑day money** $M_t$: cash+deposits+reserves at start of day from balances CSV when provided; else leave blank. 
* **Liquidity gap** $G_t=\max(0,\bar M_t - M_t)$.
* **Netting potential** $\alpha_t=1-\bar M_t/S_t$.
* **Operational peak** $M^{peak}_t$: max prefix liquidity during realized RTGS replay.
* **Intraday velocity** $v_t=\text{gross settled}/M^{peak}_t$.
* **On‑time share** $\phi_t$ and **deferral/default** $\delta_t=1-\phi_t$.
* **Creditor concentration** $HHI^+_t$.
* **Debtor shortfall shares** $DS_t(i)$. 

The analyzer and HTML report already compute and expose these; prefer those outputs.

---

## 3) Normalize the 3 control variables

Read from the sweep CSV; if not present, compute proxies:

* **Debt size vs liquidity.** Use `S_t / M_t` where `M_t` exists; else track `S_t` as the stress proxy. 
* **Distribution inequality.** Use the provided inequality parameter (e.g., Gini, top‑share). If missing, approximate from dues by agent and compute a concentration index for net creditor side, using `HHIplus_t` as a day outcome proxy. 
* **Maturity misalignment.** Use provided dispersion measure of `due_day` or construct one from schedule design; across-day bunching shows up directly via `S_t` profiles.

Store standardized names: `debt_scale`, `ineq`, `misalign`.

---

## 4) Global scan for instability surfaces

Across all scenarios and days:

* Compute **stress ratio** $r_t=\bar M_t / \max(1,M_t)$ where `M_t` exists; else track $\bar M_t$ alone. Mark `G_t>0` days as liquidity‑short. 
* Flag **instability** when any of: `G_t>0`, `φ_t<1`, `gross_settled_t < S_t`.
* Make 2D summaries with medians of `φ_t`, `G_t`, `v_t` over bins of each pair among `(debt_scale, ineq, misalign)` to spot threshold boundaries.

Deliver a short table: for each variable pair, the boundary bin where `φ_t` first drops below 0.9 and where `G_t` first exceeds 0.

---

## 5) One‑axis sweeps (hold two fixed)

For each variable:

1. **Debt size vs liquidity.** Track `{ debt_scale → median(φ_t), median(G_t), median(M^{peak}_t), median(v_t) }`. Look for a knee where `φ_t` falls rapidly as `G_t` turns positive.
2. **Inequality.** Compare `HHIplus_t` and `DS_t(i)` dispersion. Concentration rising with stable `S_t` but falling `φ_t` suggests payment bottlenecks driven by few creditors. 
3. **Misalignment.** Relate schedule dispersion to `{S_t}` bunching across days and to `M^{peak}_t`. Higher bunching should raise peaks and lower `v_t` under constant money. Summarize the effect size.

Report monotonic vs non‑monotonic patterns and any thresholds.

---

## 6) Zoom‑in rules (choose days to inspect in detail)

Trigger a **day zoom** when any condition holds:

* `G_t>0` or `φ_t<1` or `v_t<1.2` or `M^{peak}_t ≫ \bar M_t` (operational amplification). 
* `HHIplus_t` in top decile or single debtor accounts for `DS_t(i)>0.5`. 

For each zoomed day:

1. Open the run’s `dashboard.html` for that scenario. Read Day table, DS table, and Intraday prefix SVG for that **specific day**. 
2. Identify key agents from **DS_t(i)** (who needs liquidity) and cross‑check whether credits are concentrated via **HHI^+**. 
3. From the intraday SVG, note the step at which `P(s)` hits `M^{peak}_t`; list the obligations settled just before that step and the agents involved. This explains operational peaks. 
4. If balances CSV was part of the run, compare `M_t` against $\bar M_t$ to confirm whether the gap is structural (not enough money) or sequencing (enough money but poor path). 

Record 2–3 bullets per zoomed day answering:

* Who was short, how much, and why (DS and path)?
* Did concentration or timing drive the shortfall (HHI^+, bunching in `S_t`)?
* Would smoothing maturities or redistributing initial cash have solved it?

---

## 7) Preliminary observations template

Have the agent produce:

* **Finding A (Debt scale).** Threshold `debt_scale ≈ …` where `φ_t` drops and `G_t` turns positive; `M^{peak}_t` rises by …; `v_t` changes by ….
* **Finding B (Inequality).** As ineq ↑, creditor **HHI^+** ↑ and DS mass shifts to one debtor. Netting potential $\alpha_t$ falls by …. 
* **Finding C (Misalignment).** Extra bunching raises `S_t` on few days, increases `M^{peak}_t`, lowers `v_t`.
* **Mechanism snapshots.** 2–3 zoomed days with one‑line causal notes from intraday traces. 

End with **next probes**: e.g., try maturity smoothing, seed small cash buffers, or alter payer priority, then re‑run `analyze --html` for comparability. 

---

## 8) Metric definitions appendix (paste once if needed)

Paste the exporter’s “Metric Explanations” section to your reply if the audience needs definitions; it is already generated by the HTML report and matches the analyzer. 

---

## 9) Ground truth sources (for the agent’s own reference)

* **Analyzer and outputs:** CLI options and CSV/JSON/HTML report schema.
* **Metric meanings:** Day table + explanations used in HTML. 
* **Start‑of‑day money calculation:** balances CSV → $M_t$. 
* **Project purpose and analysis scope:** v1.0 simulation and analysis intent. 

---

This is sufficient for your agent to process the sweep, zoom on the right days, and produce a compact first read with defensible conclusions.
