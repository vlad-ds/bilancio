"""Streamlit app to explore the ring monotonicity parameter."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Tuple

import pandas as pd
import streamlit as st

from bilancio.scenarios.ring_explorer import _draw_payables


st.set_page_config(page_title="Ring Monotonicity Explorer", layout="wide")
st.title("Ring Monotonicity Explorer")
st.markdown(
    """
Interactively inspect how the monotonicity parameter shapes the payable ordering
in the Kalecki ring generator. Move the slider to bias the ring toward descending
(`1.0`), random (`0.0`), or ascending (`-1.0`) chains and redraw samples to verify
the effect.
"""
)


@dataclass
class SampleResult:
    sample_id: int
    seed: int
    amounts: List[float]
    score: float


def _to_decimal(value: float) -> Decimal:
    return Decimal(str(value))


def _monotonicity_score(amounts: List[float]) -> float:
    n = len(amounts)
    if n < 2:
        return 0.0
    inversions = 0
    total_pairs = n * (n - 1) // 2
    for i in range(n):
        for j in range(i + 1, n):
            if amounts[i] < amounts[j]:
                inversions += 1
    return 1.0 - 2.0 * inversions / total_pairs


def draw_samples(
    *,
    n_agents: int,
    concentration: float,
    monotonicity: float,
    total: float,
    base_seed: int,
    count: int,
) -> Tuple[pd.DataFrame, List[SampleResult]]:
    totals = []
    samples: List[SampleResult] = []

    for idx in range(count):
        seed = base_seed + idx
        amounts_dec = _draw_payables(
            n_agents,
            _to_decimal(concentration),
            _to_decimal(monotonicity),
            _to_decimal(total),
            seed,
        )
        amounts = [float(value) for value in amounts_dec]
        score = _monotonicity_score(amounts)
        samples.append(SampleResult(sample_id=idx, seed=seed, amounts=amounts, score=score))
        for edge_idx, amount in enumerate(amounts):
            totals.append({
                "sample": idx,
                "seed": seed,
                "edge": f"H{edge_idx + 1}->H{(edge_idx + 1) % n_agents + 1}",
                "amount": amount,
            })

    return pd.DataFrame(totals), samples


with st.sidebar:
    st.header("Generator controls")
    n_agents = st.slider("Ring agents", min_value=3, max_value=12, value=5, step=1)
    total = st.number_input("Total payable (S1)", min_value=10.0, value=500.0, step=10.0)
    concentration = st.slider("Dirichlet concentration", min_value=0.2, max_value=5.0, value=1.0, step=0.05)
    monotonicity = st.slider("Monotonicity bias", min_value=-1.0, max_value=1.0, value=0.0, step=0.05)
    sample_count = st.slider("Samples", min_value=1, max_value=10, value=3, step=1)
    base_seed = st.number_input("Base seed", min_value=0, value=42, step=1)
    if "sample_offset" not in st.session_state:
        st.session_state["sample_offset"] = 0
    if st.button("Draw new samples"):
        st.session_state["sample_offset"] += sample_count

offset_seed = base_seed + st.session_state["sample_offset"]
data_frame, sample_results = draw_samples(
    n_agents=n_agents,
    concentration=concentration,
    monotonicity=monotonicity,
    total=total,
    base_seed=offset_seed,
    count=sample_count,
)

if sample_results:
    summary_records = [
        {
            "sample": result.sample_id,
            "seed": result.seed,
            "score": round(result.score, 3),
            "max_amount": max(result.amounts),
            "min_amount": min(result.amounts),
        }
        for result in sample_results
    ]
    summary_df = pd.DataFrame(summary_records)

    st.subheader("Sample summary")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    selected_sample_ids = [result.sample_id for result in sample_results]
    chosen_sample = st.selectbox("Select sample", options=selected_sample_ids, index=0)

    current = next(result for result in sample_results if result.sample_id == chosen_sample)
    edge_df = data_frame[data_frame["sample"] == chosen_sample].copy()
    edge_df = edge_df.set_index("edge")

    col_chart, col_metrics = st.columns([2, 1])
    with col_chart:
        st.subheader("Payable amounts")
        st.bar_chart(edge_df["amount"], use_container_width=True)
    with col_metrics:
        st.subheader("Monotonicity score")
        st.metric("Descending bias", f"{current.score:.3f}")
        st.caption(
            "Score = 1.0 for strictly descending, -1.0 for strictly ascending, 0 ≈ random ordering."
        )

    st.subheader("Raw amounts")
    st.dataframe(edge_df.reset_index(), use_container_width=True, hide_index=True)
else:
    st.info("Adjust the parameters or increase the sample count to generate payables.")
