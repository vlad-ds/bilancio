# Plan: Deploy Cloud Metrics to Supabase

## Overview

This plan deploys changes that allow Modal cloud simulations to compute metrics and save them directly to Supabase, eliminating the need to download artifacts locally.

## Branch

```bash
git fetch origin claude/slack-analyze-bilancio-sweep-zrC3y
git checkout claude/slack-analyze-bilancio-sweep-zrC3y
```

## Step 1: Create job_metrics Table in Supabase

Run this SQL in Supabase SQL Editor (https://supabase.com/dashboard/project/vghchkriceqqitbpevtz/sql):

```sql
CREATE TABLE IF NOT EXISTS job_metrics (
    id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    n_comparisons INTEGER,
    n_pairs INTEGER,
    mean_trading_effect DOUBLE PRECISION,
    min_trading_effect DOUBLE PRECISION,
    max_trading_effect DOUBLE PRECISION,
    std_trading_effect DOUBLE PRECISION,
    positive_effects INTEGER,
    negative_effects INTEGER,
    neutral_effects INTEGER,
    mean_delta_passive DOUBLE PRECISION,
    mean_delta_active DOUBLE PRECISION,
    mean_phi_passive DOUBLE PRECISION,
    mean_phi_active DOUBLE PRECISION,
    raw_summary JSONB,
    UNIQUE(job_id)
);

CREATE INDEX IF NOT EXISTS idx_job_metrics_job_id ON job_metrics(job_id);
```

## Step 2: Verify Modal Secret

Ensure the Modal secret named `supabase` exists with these keys:
- `BILANCIO_SUPABASE_URL`
- `BILANCIO_SUPABASE_ANON_KEY`

Check at: https://modal.com/secrets

## Step 3: Deploy Modal App

```bash
uv run modal deploy src/bilancio/cloud/modal_app.py
```

Expected output should show:
- `run_simulation` function deployed
- `compute_aggregate_metrics` function deployed
- `health_check` function deployed

## Step 4: Test with a Small Sweep

Run a quick test sweep (5 pairs = 10 runs):

```bash
uv run bilancio sweep balanced --cloud \
  --out-dir out/experiments/test-metrics \
  --n-agents 50 \
  --maturity-days 10 \
  --kappas "0.5,1.0" \
  --concentrations "1.0" \
  --mus "0.5" \
  --outside-mid-ratios "1.0"
```

Estimated: ~2 minutes, ~$0.003

## Step 5: Verify Results in Supabase

After the sweep completes, check:

```bash
# Check job was created
uv run bilancio jobs ls --cloud

# Check job_metrics table
uv run python -c "
from bilancio.storage.supabase_client import get_supabase_client
client = get_supabase_client()
result = client.table('job_metrics').select('*').order('created_at', desc=True).limit(5).execute()
for row in result.data:
    print(f\"{row['job_id']}: mean_effect={row['mean_trading_effect']}, +={row['positive_effects']}, -={row['negative_effects']}\")
"
```

## What Changed

### New Architecture

```
Modal (per run)                    Supabase
───────────────                    ────────
1. Run simulation
2. Compute metrics (δ, φ)
3. Save run + metrics ──────────> runs, metrics tables
4. After all runs:
   compute_aggregate_metrics ───> job_metrics table
```

### Key Files Modified

- `src/bilancio/cloud/modal_app.py` - Metrics computation and Supabase save
- `src/bilancio/runners/cloud_executor.py` - Pass params, call aggregate
- `src/bilancio/runners/models.py` - Add metrics field to ExecutionResult
- `src/bilancio/experiments/ring.py` - Pass run params to RunOptions
- `src/bilancio/experiments/balanced_comparison.py` - Call aggregate after sweep

### New Modal Functions

1. `run_simulation` - Now computes metrics and saves to Supabase
2. `compute_aggregate_metrics` - Computes sweep-level stats, saves to job_metrics

## Troubleshooting

### Modal connection issues
If Modal commands fail, ensure you're authenticated:
```bash
uv run modal token new
```

### Supabase table doesn't exist
Run the SQL from Step 1 in Supabase dashboard.

### Secret not found
Create the secret in Modal dashboard with exact name `supabase`.
