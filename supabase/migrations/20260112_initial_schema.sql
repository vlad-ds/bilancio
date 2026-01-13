-- Bilancio Cloud Storage Schema
-- Jobs, Runs, and Metrics for simulation tracking

-- Jobs table (top-level experiment tracking)
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pending',
    description TEXT,

    -- Configuration
    sweep_type TEXT NOT NULL,
    n_agents INTEGER NOT NULL,
    maturity_days INTEGER NOT NULL DEFAULT 5,
    kappas DECIMAL[] NOT NULL,
    concentrations DECIMAL[] NOT NULL,
    mus DECIMAL[] NOT NULL,
    outside_mid_ratios DECIMAL[] DEFAULT '{1}',
    seeds INTEGER[] DEFAULT '{42}',
    cloud BOOLEAN DEFAULT FALSE,

    -- Results summary
    total_runs INTEGER,
    completed_runs INTEGER DEFAULT 0,
    failed_runs INTEGER DEFAULT 0,
    error TEXT,
    notes TEXT,

    -- Link to Modal Volume path
    modal_experiment_id TEXT,

    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);

-- Runs table (individual simulation runs)
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    job_id TEXT REFERENCES jobs(job_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pending',

    -- Parameters for this specific run
    kappa DECIMAL NOT NULL,
    concentration DECIMAL NOT NULL,
    mu DECIMAL NOT NULL,
    outside_mid_ratio DECIMAL DEFAULT 1,
    seed INTEGER DEFAULT 42,
    regime TEXT,

    -- Execution details
    execution_time_ms INTEGER,
    modal_call_id TEXT,
    error TEXT,

    -- Modal Volume path (artifacts stored there)
    modal_volume_path TEXT,

    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);

-- Metrics table (queryable numeric results)
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    run_id TEXT REFERENCES runs(run_id) ON DELETE CASCADE,
    job_id TEXT REFERENCES jobs(job_id) ON DELETE CASCADE,

    -- Key metrics
    delta_total DECIMAL,
    phi_total DECIMAL,
    n_defaults INTEGER,
    n_clears INTEGER,
    time_to_stability INTEGER,

    -- Dealer metrics (for balanced comparison)
    trading_effect DECIMAL,
    total_trades INTEGER,
    total_trade_volume DECIMAL,

    -- Raw metrics JSON (for flexibility)
    raw_metrics JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Job events table (lifecycle logging)
CREATE TABLE IF NOT EXISTS job_events (
    id SERIAL PRIMARY KEY,
    job_id TEXT REFERENCES jobs(job_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    details JSONB DEFAULT '{}'
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_job_id ON runs(job_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_metrics_job_id ON metrics(job_id);
CREATE INDEX IF NOT EXISTS idx_metrics_run_id ON metrics(run_id);
CREATE INDEX IF NOT EXISTS idx_metrics_delta ON metrics(delta_total);
CREATE INDEX IF NOT EXISTS idx_job_events_job ON job_events(job_id);
