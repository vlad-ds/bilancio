# Expel-agent Ring Sweep Analysis Dashboard

Streamlit dashboard that explores the `expel_ring_sweep_clean` grid by showing how the
independent variables (κ, Dirichlet α, μ) shape settlement outcomes under expel-agent
handling.

## Quick start

```bash
streamlit run dashboards/expel_ring_analysis_dashboard/streamlit_app.py
```

By default the app loads data from `out/experiments/expel_ring_sweep_clean/aggregate/results.csv`.
Use the sidebar to point at a different sweep directory and to filter κ, α, or μ slices.
