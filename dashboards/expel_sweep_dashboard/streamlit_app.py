"""Streamlit dashboard for experiment 015 expel-agent sweep."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Dict, Iterable, List

import altair as alt
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SWEEP_ROOT = PROJECT_ROOT / "out" / "experiments" / "expel_ring_sweep"
AGGREGATE_DIR = SWEEP_ROOT / "aggregate"

RUNS_DIR = SWEEP_ROOT / "runs"

METRIC_GLOSSARY = {
    "φ_total / φ_t": "Share of dues settled within a day (φ_t) or across the full run (φ_total); values lie between 0 and 1.",
    "δ_t": "Arrears share remaining after settlement; by construction δ_t = 1 − φ_t.",
    "G_t": "Liquidity gap in monetary units, capturing unsatisfied cash demand once clearing pauses.",
    "M_t": "Gross settlement volume processed during the day across all channels.",
    "M̄_t": "Batched liquidity requirement from the LSM phase (if present).",
    "M^peak_t": "Operational peak liquidity observed when replaying intraday transfers (RTGS).",
    "gross_settled_t": "Total currency settled intraday when replaying the sequence (used with M^peak_t).",
    "v_t": "Intraday velocity = gross_settled_t / M^peak_t when M^peak_t > 0.",
    "α_t": "Share of dues that settled during the LSM batch before RTGS replay.",
    "HHI⁺": "Adjusted Herfindahl index measuring creditor concentration among unsettled claims.",
    "defaults": "Count of AgentDefaulted events; equals the number of expelled agents in a run.",
    "time_to_stability": "Simulation days consumed before meeting the quiet-days stability criterion.",
    "DS_t": "Debtor-share attribution for losses after defaults expel an agent.",
}

@st.cache_data(show_spinner=False)
def load_results() -> pd.DataFrame:
    """Load per-run summary metrics."""
    results_path = AGGREGATE_DIR / "results.csv"
    df = pd.read_csv(results_path)
    numeric_cols = [
        "phi_total",
        "delta_total",
        "max_G_t",
        "alpha_1",
        "Mpeak_1",
        "v_1",
        "HHIplus_1",
        "time_to_stability",
        "kappa",
        "concentration",
        "mu",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_day_metrics() -> pd.DataFrame:
    """Load day-level metrics for the sweep."""
    path = AGGREGATE_DIR / "day_metrics_enriched.pkl"
    with path.open("rb") as fh:
        df = pickle.load(fh)
    df = df.copy()
    numeric_cols = [
        "day",
        "S_t",
        "phi_t",
        "delta_t",
        "G_t",
        "M_t",
        "Mbar_t",
        "Mpeak_t",
        "gross_settled_t",
        "alpha_t",
        "HHIplus_t",
        "v_t",
        "kappa",
        "concentration",
        "mu",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_summary_table(name: str) -> pd.DataFrame:
    path = AGGREGATE_DIR / name
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df


@st.cache_data(show_spinner=False)
def load_run_metrics(run_id: str) -> pd.DataFrame:
    path = RUNS_DIR / run_id / "out" / "metrics.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce") if col not in {"notes"} else df[col]
    return df


@st.cache_data(show_spinner=False)
def load_run_csv(run_id: str, filename: str) -> pd.DataFrame:
    path = RUNS_DIR / run_id / "out" / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce") if col not in {"agent", "payee", "payer"} else df[col]
    return df


@st.cache_data(show_spinner=False)
def load_run_events(run_id: str) -> List[dict]:
    path = RUNS_DIR / run_id / "out" / "events.jsonl"
    events: List[dict] = []
    if not path.exists():
        return events
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    return events


def compute_phi_display(results: pd.DataFrame, day_metrics: pd.DataFrame) -> pd.Series:
    day_metrics_sorted = day_metrics.sort_values(["run_id", "day"])
    phi_first = (
        day_metrics_sorted.groupby("run_id")["phi_t"]
        .apply(lambda s: s.dropna().iloc[0] if (s.dropna().size > 0) else float("nan"))
    )
    return results.set_index("run_id")["phi_total"].fillna(phi_first).fillna(0)



def render_glossary() -> None:
    """Display a glossary of key metrics used in the dashboard."""
    with st.expander("Metrics glossary", expanded=False):
        for metric, description in METRIC_GLOSSARY.items():
            st.markdown(f"**{metric}** – {description}")


def compute_default_counts(run_ids: Iterable[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for run_id in run_ids:
        defaults = sum(1 for event in load_run_events(run_id) if event.get("kind") == "AgentDefaulted")
        counts[run_id] = defaults
    return counts


def make_scatter(df: pd.DataFrame) -> alt.Chart:
    if df.empty:
        return alt.Chart(pd.DataFrame({"kappa": [], "phi": []}))
    data = df.copy()
    data["μ"] = data["mu"].astype(str)
    chart = (
        alt.Chart(data)
        .mark_circle(size=80, opacity=0.7)
        .encode(
            x=alt.X("kappa:Q", title="Debt scale κ"),
            y=alt.Y("phi_total_display:Q", title="Settlement share φ"),
            color=alt.Color("μ:N", title="μ"),
            tooltip=["run_id", "kappa", "concentration", "mu", "phi_total_display", "defaults"],
        )
        .properties(height=360)
    )
    return chart




def make_heatmap(df: pd.DataFrame, x: str, y: str, value: str, title: str) -> alt.Chart | None:
    if df.empty:
        return None
    data = df[[x, y, value]].dropna()
    if data.empty:
        return None
    return (
        alt.Chart(data)
        .mark_rect()
        .encode(
            x=alt.X(f"{x}:O", title=x),
            y=alt.Y(f"{y}:O", title=y),
            color=alt.Color(f"{value}:Q", title=value, scale=alt.Scale(scheme="blues")),
            tooltip=[x, y, value],
        )
        .properties(title=title, height=260)
    )


def events_table(events: List[dict], kind: str, columns: Dict[str, str]) -> pd.DataFrame:
    rows = []
    for e in events:
        if e.get("kind") != kind:
            continue
        row = {label: e.get(src) for label, src in columns.items()}
        rows.append(row)
    return pd.DataFrame(rows)


def render_run_detail(run_id: str, day_metrics: pd.DataFrame) -> None:
    st.subheader(f"Run detail: {run_id}")
    metrics = load_run_metrics(run_id)
    if not metrics.empty:
        st.markdown("**Run metrics (per day)**")
        st.dataframe(metrics)
    run_days = day_metrics[day_metrics["run_id"] == run_id]
    if not run_days.empty:
        st.markdown("**Aggregate day metrics**")
        st.dataframe(run_days)
    intraday = load_run_csv(run_id, "metrics_intraday.csv")
    if not intraday.empty:
        st.markdown("**Intraday replay**")
        st.dataframe(intraday)
    debtor_share = load_run_csv(run_id, "metrics_ds.csv")
    if not debtor_share.empty:
        st.markdown("**Debtor share (DSₜ)**")
        st.dataframe(debtor_share)

    events = load_run_events(run_id)
    if events:
        defaults = events_table(
            events,
            "AgentDefaulted",
            {"day": "day", "agent": "agent", "shortfall": "shortfall", "trigger": "trigger_contract"},
        )
        if not defaults.empty:
            st.markdown("**Agent defaults**")
            st.dataframe(defaults)
        settlements = events_table(
            events,
            "PayableSettled",
            {"day": "day", "debtor": "debtor", "creditor": "creditor", "amount": "amount"},
        )
        partials = events_table(
            events,
            "PartialSettlement",
            {"day": "day", "debtor": "debtor", "creditor": "creditor", "paid": "amount_paid", "shortfall": "shortfall"},
        )
        if not settlements.empty or not partials.empty:
            st.markdown("**Settlements**")
            if not settlements.empty:
                st.dataframe(settlements)
            if not partials.empty:
                st.dataframe(partials)
    else:
        st.info("No events available for this run.")


def main() -> None:
    st.set_page_config(page_title="Expel-agent sweep", layout="wide")
    st.title("Experiment 015 – Expel-agent Sweep Explorer")
    render_glossary()

    results = load_results()
    day_metrics = load_day_metrics()

    results = results.copy()
    results["phi_total_display"] = compute_phi_display(results, day_metrics).values
    default_counts = compute_default_counts(results["run_id"].tolist())
    results["defaults"] = results["run_id"].map(default_counts)

    st.sidebar.header("Filters")
    kappa_options = sorted(results["kappa"].dropna().unique())
    conc_options = sorted(results["concentration"].dropna().unique())
    mu_options = sorted(results["mu"].dropna().unique())

    selected_kappa = st.sidebar.multiselect("Debt scale κ", kappa_options, default=kappa_options)
    selected_conc = st.sidebar.multiselect("Dirichlet concentration c", conc_options, default=conc_options)
    selected_mu = st.sidebar.multiselect("Maturity misalignment μ", mu_options, default=mu_options)
    phi_min = st.sidebar.slider("Minimum φ", 0.0, 1.0, 0.0, 0.01)

    filtered = results[
        results["kappa"].isin(selected_kappa)
        & results["concentration"].isin(selected_conc)
        & results["mu"].isin(selected_mu)
        & (results["phi_total_display"] >= phi_min)
    ]

    st.markdown("### Aggregate overview")
    cols = st.columns(4)
    cols[0].metric("Runs", value=len(filtered))
    cols[1].metric("Mean φ", value=f"{filtered['phi_total_display'].mean():.3f}" if not filtered.empty else "–")
    cols[2].metric(
        "Median defaults",
        value=f"{filtered['defaults'].median():.0f}" if not filtered.empty else "–",
    )
    cols[3].metric(
        "Mean liquidity gap",
        value=f"{filtered['max_G_t'].mean():.1f}" if not filtered.empty else "–",
    )

    st.altair_chart(make_scatter(filtered), use_container_width=True)

    # Aggregate heatmaps for quick comparison across controls
    heatmap_cols = st.columns(2)
    heat_kappa_mu = (
        filtered.groupby(["kappa", "mu"])["phi_total_display"].mean().reset_index()
        if not filtered.empty
        else pd.DataFrame(columns=["kappa", "mu", "phi_total_display"])
    )
    heat_conc_mu = (
        filtered.groupby(["concentration", "mu"])["phi_total_display"].mean().reset_index()
        if not filtered.empty
        else pd.DataFrame(columns=["concentration", "mu", "phi_total_display"])
    )

    heat1 = make_heatmap(heat_kappa_mu, "kappa", "mu", "phi_total_display", "Mean φ by κ × μ")
    heat2 = make_heatmap(heat_conc_mu, "concentration", "mu", "phi_total_display", "Mean φ by c × μ")

    if heat1 is not None:
        heatmap_cols[0].altair_chart(heat1, use_container_width=True)
    if heat2 is not None:
        heatmap_cols[1].altair_chart(heat2, use_container_width=True)

    st.markdown("### Runs table")
    st.dataframe(
        filtered[
            [
                "run_id",
                "kappa",
                "concentration",
                "mu",
                "phi_total_display",
                "max_G_t",
                "defaults",
                "time_to_stability",
                "Mpeak_1",
                "v_1",
            ]
        ].rename(columns={"phi_total_display": "phi_total"})
    )

    st.download_button(
        label="Download filtered results as CSV",
        data=filtered.to_csv(index=False),
        file_name="expel_sweep_filtered.csv",
    )

    st.markdown("---")
    st.markdown("### Run drill-down")
    if filtered.empty:
        st.info("Adjust filters to select at least one run.")
        return

    selected_run = st.selectbox("Choose a run", filtered["run_id"].tolist())
    if selected_run:
        render_run_detail(selected_run, day_metrics)


if __name__ == "__main__":
    main()
