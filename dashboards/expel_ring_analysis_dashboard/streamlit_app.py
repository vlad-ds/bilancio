"""Streamlit dashboard for extended analysis of the expel-agent ring sweep."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import altair as alt
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SWEEP_DIR = PROJECT_ROOT / "out" / "experiments" / "expel_ring_sweep_clean"


@st.cache_data(show_spinner=False)
def load_results(sweep_dir: Path) -> pd.DataFrame:
    """Load and clean the aggregate results CSV."""
    results_path = sweep_dir / "aggregate" / "results.csv"
    if not results_path.exists():
        raise FileNotFoundError(
            f"Could not find aggregated results at {results_path}. "
            "Run the sweep or point the dashboard to the correct directory."
        )

    df = pd.read_csv(results_path)

    numeric_cols = [
        "kappa",
        "concentration",
        "mu",
        "S1",
        "L0",
        "phi_total",
        "delta_total",
        "max_G_t",
        "alpha_1",
        "Mpeak_1",
        "v_1",
        "HHIplus_1",
        "time_to_stability",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["kappa"] = df["kappa"].astype(float)
    df["concentration"] = df["concentration"].astype(float)
    df["mu"] = df["mu"].astype(float)

    return df


def format_summary(value: Optional[float], suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "–"
    return f"{value:.2f}{suffix}"


def make_heatmap(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    tooltip_label: str,
) -> alt.Chart:
    heatmap_data = (
        df.groupby(["mu", "kappa"], as_index=False)[value_col]
        .mean()
        .rename(columns={value_col: "metric"})
    )

    return (
        alt.Chart(heatmap_data)
        .mark_rect()
        .encode(
            x=alt.X("kappa:O", title="κ (Debt / Liquidity)", sort="ascending"),
            y=alt.Y("mu:O", title="μ (Maturity Misalignment)", sort="ascending"),
            color=alt.Color(
                "metric:Q",
                title=tooltip_label,
                scale=alt.Scale(scheme="blues" if value_col == "phi_total" else "reds"),
            ),
            tooltip=[
                alt.Tooltip("kappa:Q", title="κ"),
                alt.Tooltip("mu:Q", title="μ"),
                alt.Tooltip("metric:Q", title=tooltip_label, format=".3f"),
            ],
        )
        .properties(title=title)
    )


def make_line(df: pd.DataFrame, value_col: str, title: str, y_title: str) -> alt.Chart:
    line_data = (
        df.groupby(["kappa", "mu"], as_index=False)[value_col]
        .mean()
        .rename(columns={value_col: "metric"})
    )

    return (
        alt.Chart(line_data)
        .mark_line(point=True)
        .encode(
            x=alt.X("kappa:Q", title="κ"),
            y=alt.Y("metric:Q", title=y_title),
            color=alt.Color("mu:N", title="μ", scale=alt.Scale(scheme="viridis")),
            tooltip=[
                alt.Tooltip("kappa:Q", title="κ"),
                alt.Tooltip("mu:Q", title="μ"),
                alt.Tooltip("metric:Q", title=y_title, format=".3f"),
            ],
        )
        .properties(title=title)
    )


def make_scatter(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_circle(opacity=0.7, size=120)
        .encode(
            x=alt.X("max_G_t:Q", title="Max liquidity gap Gₜ"),
            y=alt.Y("phi_total:Q", title="φ_total (Share Settled)"),
            color=alt.Color("kappa:Q", title="κ", scale=alt.Scale(scheme="plasma")),
            size=alt.Size("time_to_stability:Q", title="Time to stability", scale=alt.Scale(range=[50, 400])),
            tooltip=[
                alt.Tooltip("run_id:N", title="Run"),
                alt.Tooltip("kappa:Q", title="κ"),
                alt.Tooltip("concentration:Q", title="α (Dirichlet)"),
                alt.Tooltip("mu:Q", title="μ"),
                alt.Tooltip("phi_total:Q", title="φ_total", format=".3f"),
                alt.Tooltip("max_G_t:Q", title="Max Gₜ", format=".1f"),
                alt.Tooltip("time_to_stability:Q", title="Time to stability"),
            ],
        )
        .properties(title="Liquidity gaps vs settlement performance")
    )


def show_explanation():
    st.markdown(
        """
        ### How to read these metrics
        * **κ (kappa)** &mdash; Debt-to-liquidity ratio. Lower values mean more cash seeded on Day 0 (abundant liquidity); higher values mean stressed liquidity.
        * **Dirichlet concentration α** &mdash; Controls payable inequality. α < 1 concentrates dues in a few agents; α > 1 flattens them.
        * **μ (mu)** &mdash; Maturity misalignment. μ = 0 bunches every payable on Day 1; larger values stagger dues across the 3-day horizon.
        * **φ_total** &mdash; Share of original dues that settled before the simulation reached the quiet-days stability rule. (1 = full settlement.)
        * **Time to stability** &mdash; Last day that saw activity. The engine still waits two additional quiet days, but the summary reports the final busy day (0–3 in this sweep).
        * **Gₜ, Mpeak, v₁** &mdash; Day-level liquidity diagnostics. Gₜ > 0 indicates a structural cash shortfall; Mpeak is the intraday liquidity spike; v₁ shows how often the same cash recycled on Day 1.
        """
    )


def main():
    st.set_page_config(page_title="Expel-agent Ring Sweep Analysis", layout="wide")
    st.title("Expel-agent Ring Sweep &mdash; Extended Analysis")
    st.caption("Inspect how κ, Dirichlet α, and μ shape settlement outcomes under expel-agent handling.")

    with st.sidebar:
        st.header("Configuration")
        base_dir_input = st.text_input(
            "Sweep directory",
            value=str(DEFAULT_SWEEP_DIR),
            help="Point to a sweep folder containing aggregate/results.csv",
        )
        sweep_dir = Path(base_dir_input).expanduser().resolve()

        try:
            df = load_results(sweep_dir)
        except FileNotFoundError as err:
            st.error(str(err))
            st.stop()

        concentrations = sorted(df["concentration"].dropna().unique())
        concentration_filter = st.multiselect(
            "Dirichlet α (inequality)",
            options=concentrations,
            default=concentrations,
        )

        mu_values = sorted(df["mu"].dropna().unique())
        mu_filter = st.multiselect(
            "μ (maturity misalignment)",
            options=mu_values,
            default=mu_values,
        )

        kappa_values = sorted(df["kappa"].dropna().unique())
        kappa_filter = st.multiselect(
            "κ (debt/liquidity)",
            options=kappa_values,
            default=kappa_values,
        )

    filtered = df[
        df["concentration"].isin(concentration_filter)
        & df["mu"].isin(mu_filter)
        & df["kappa"].isin(kappa_filter)
    ].copy()

    if filtered.empty:
        st.warning("No scenarios match the current filters.")
        st.stop()

    show_explanation()

    st.subheader("Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean φ_total", format_summary(filtered["phi_total"].mean()))
    c2.metric("Runs with φ_total = 0", f"{(filtered['phi_total'] == 0).mean():.0%}")
    c3.metric("Mean time to stability", format_summary(filtered["time_to_stability"].mean(), " days"))
    c4.metric("Runs with liquidity gap", f"{(filtered['max_G_t'] > 0).mean():.0%}")

    st.subheader("Individual effects")
    col_a, col_b = st.columns(2)
    with col_a:
        st.altair_chart(
            make_line(filtered, "phi_total", "φ_total vs κ (lines by μ)", "Mean φ_total"),
            use_container_width=True,
        )
    with col_b:
        st.altair_chart(
            make_line(filtered, "time_to_stability", "Time to stability vs κ (lines by μ)", "Mean time to stability"),
            use_container_width=True,
        )

    st.subheader("Interactions of κ and μ")
    col_c, col_d = st.columns(2)
    with col_c:
        st.altair_chart(
            make_heatmap(filtered, "phi_total", "Mean φ_total heatmap", "Mean φ_total"),
            use_container_width=True,
        )
    with col_d:
        st.altair_chart(
            make_heatmap(filtered, "time_to_stability", "Mean time to stability heatmap", "Mean time to stability"),
            use_container_width=True,
        )

    st.subheader("Liquidity vs settlement")
    st.altair_chart(make_scatter(filtered), use_container_width=True)

    st.subheader("Pivot table")
    pivot = (
        filtered
        .groupby(["kappa", "concentration", "mu"], as_index=False)[["phi_total", "time_to_stability", "max_G_t"]]
        .mean()
        .sort_values(["phi_total", "time_to_stability"], ascending=[False, True])
    )
    st.dataframe(pivot, hide_index=True)

    st.caption(
        "Per-run day metrics live next to each scenario under runs/<run_id>/out/metrics.csv if you need deeper dives."
    )


if __name__ == "__main__":
    main()
