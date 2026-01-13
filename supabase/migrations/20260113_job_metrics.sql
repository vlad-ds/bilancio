-- Job-level aggregate metrics table
-- Stores sweep summary statistics computed after all runs complete

CREATE TABLE IF NOT EXISTS job_metrics (
    id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Comparison counts
    n_comparisons INTEGER,
    n_pairs INTEGER,

    -- Trading effect statistics
    mean_trading_effect DOUBLE PRECISION,
    min_trading_effect DOUBLE PRECISION,
    max_trading_effect DOUBLE PRECISION,
    std_trading_effect DOUBLE PRECISION,

    -- Effect distribution
    positive_effects INTEGER,  -- Dealers help (trading_effect > 0.001)
    negative_effects INTEGER,  -- Dealers hurt (trading_effect < -0.001)
    neutral_effects INTEGER,   -- No significant effect

    -- Mean metrics by regime
    mean_delta_passive DOUBLE PRECISION,
    mean_delta_active DOUBLE PRECISION,
    mean_phi_passive DOUBLE PRECISION,
    mean_phi_active DOUBLE PRECISION,

    -- Full summary JSON for flexibility
    raw_summary JSONB,

    UNIQUE(job_id)
);

CREATE INDEX IF NOT EXISTS idx_job_metrics_job_id ON job_metrics(job_id);
