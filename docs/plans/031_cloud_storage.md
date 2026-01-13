# Plan 031: Cloud Storage Layer

**Status**: Implemented
**Goal**: Implement a modular, independent cloud storage layer for persistent job/run/metrics storage accessible by AI agents and humans

---

## What Was Implemented

### Storage Layer (keeps local as default, Supabase optional)

**Supabase Client** (`src/bilancio/storage/supabase_client.py`):
- Singleton client with lazy initialization
- `is_supabase_configured()` to check if env vars are set
- `get_supabase_client()` to get configured client
- Custom `SupabaseConfigError` for missing credentials

**SupabaseJobStore** (`src/bilancio/jobs/supabase_store.py`):
- `save_job(job)` - Persists job to `jobs` table
- `save_event(event)` - Logs events to `job_events` table
- `get_job(job_id)` - Retrieves job from Supabase
- `list_jobs(status, limit)` - Lists jobs with filtering
- `update_status(job_id, status)` - Updates job status
- `get_events(job_id)` - Gets all events for a job

**SupabaseRegistryStore** (`src/bilancio/storage/supabase_registry.py`):
- Implements `RegistryStore` protocol for Supabase
- `upsert(entry)` - Saves run to `runs` and metrics to `metrics` tables
- `get(experiment_id, run_id)` - Gets a specific run
- `list_runs(experiment_id)` - Lists all runs for a job
- `get_completed_keys(...)` - For sweep resumption
- `query(experiment_id, filters)` - Query runs with filters

**JobManager Integration** (`src/bilancio/jobs/manager.py`):
- Added optional `cloud_store` parameter
- `create_job_manager(jobs_dir, cloud=True)` factory function
- Saves to both local filesystem AND Supabase when cloud enabled
- Events saved to both local (in job manifest) and Supabase (job_events table)

**CLI Commands** (`src/bilancio/ui/cli/jobs.py`):
- `bilancio jobs ls --cloud` - List jobs from Supabase
- `bilancio jobs get <job_id> --cloud` - Get job details
- `bilancio jobs runs <job_id> --cloud` - List runs for a job
- `bilancio jobs metrics <job_id> --cloud` - Show aggregate metrics

**Modal Volume cleanup** (`src/bilancio/ui/cli/volume.py`):
- `bilancio volume ls` - List experiments
- `bilancio volume cleanup --older-than N` - Delete old experiments
- `bilancio volume rm <id>` - Delete specific experiment

### Database Schema (`supabase/migrations/20260112_initial_schema.sql`)

```sql
CREATE TABLE jobs (job_id, created_at, status, description, sweep_type, n_agents, kappas[], ...);
CREATE TABLE runs (run_id, job_id, status, kappa, concentration, mu, ...);
CREATE TABLE metrics (run_id, job_id, delta_total, phi_total, raw_metrics JSONB, ...);
CREATE TABLE job_events (job_id, event_type, timestamp, details JSONB);
```

### Configuration

```bash
# .env file
BILANCIO_SUPABASE_URL=https://xxxx.supabase.co
BILANCIO_SUPABASE_ANON_KEY=eyJ...
```

**Skipped (for now):**
- Cloudflare R2 - No hard spending limits, only alerts
- Artifacts stored in Modal Volume (accessed via CLI)

---

## Problem Statement

Currently, simulation results are stored in:
1. **Local disk** - Lost when conversation ends (Claude Code web)
2. **Modal Volume** - Accessible only via Modal CLI, not queryable, ephemeral

We need persistent storage that:
- **Survives across conversations** - Results from Job A accessible in future conversations
- **Is queryable** - "Show me all jobs with kappa < 0.5 and delta > 0.1"
- **Is accessible to AI agents** - REST API for programmatic access
- **Is accessible to humans** - Web UI or simple download mechanism
- **Is modular** - Independent of compute layer (Modal), swappable
- **Is free or nearly free** - Budget-constrained project

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       CURRENT STATE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   User Request                                                  │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────┐                                                  │
│   │  CLI     │                                                  │
│   └────┬─────┘                                                  │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────────────────────────────────────────┐              │
│   │           Modal Cloud Executor               │              │
│   │  ┌────────────────────────────────────────┐  │              │
│   │  │     Modal Volume (bilancio-results)    │  │              │
│   │  │  ┌─────────────────────────────────┐   │  │              │
│   │  │  │ <job_id>/                       │   │  │              │
│   │  │  │   job_manifest.json             │   │  │              │
│   │  │  │   runs/                         │   │  │              │
│   │  │  │     <run_id>/                   │   │  │              │
│   │  │  │       scenario.yaml             │   │  │              │
│   │  │  │       run.html                  │   │  │              │
│   │  │  │       out/                      │   │  │              │
│   │  │  │         events.jsonl            │   │  │              │
│   │  │  │         balances.csv            │   │  │              │
│   │  │  └─────────────────────────────────┘   │  │              │
│   │  └────────────────────────────────────────┘  │              │
│   └──────────────────────────────────────────────┘              │
│        │                                                        │
│        ▼                                                        │
│   Local disk copy (via `modal volume get`)                      │
│   ❌ Lost when conversation ends                                │
│   ❌ Not queryable                                              │
│   ❌ Only accessible via Modal CLI                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       PROPOSED STATE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    STORAGE LAYER                        │   │
│   │  (Independent, Modular, Accessible)                     │   │
│   │                                                         │   │
│   │   ┌─────────────────────┐   ┌────────────────────────┐  │   │
│   │   │   Supabase (Free)   │   │   Cloudflare R2 (Free) │  │   │
│   │   │   PostgreSQL DB     │   │   S3-Compatible Blobs  │  │   │
│   │   │                     │   │                        │  │   │
│   │   │   • jobs            │   │   • events.jsonl       │  │   │
│   │   │   • runs            │   │   • balances.csv       │  │   │
│   │   │   • metrics         │   │   • run.html           │  │   │
│   │   │   • events          │   │   • metrics.html       │  │   │
│   │   │                     │   │   • scenario.yaml      │  │   │
│   │   │   REST API          │   │   Signed URLs          │  │   │
│   │   │   Web Dashboard     │   │   Direct Download      │  │   │
│   │   └─────────────────────┘   └────────────────────────┘  │   │
│   │                                                         │   │
│   │               StorageClient Protocol                    │   │
│   │   ┌───────────────────────────────────────────────────┐ │   │
│   │   │  save_job()  |  save_run()  |  save_metrics()     │ │   │
│   │   │  get_job()   |  get_run()   |  query_runs()       │ │   │
│   │   │  upload_artifact()  |  get_artifact_url()         │ │   │
│   │   └───────────────────────────────────────────────────┘ │   │
│   └─────────────────────────────────────────────────────────┘   │
│                             ▲                                   │
│                             │                                   │
│   ┌─────────────────────────┴───────────────────────────────┐   │
│   │                    COMPUTE LAYER                        │   │
│   │                                                         │   │
│   │   ┌───────────────┐    ┌────────────────────────────┐   │   │
│   │   │  Modal Cloud  │    │  Local Executor            │   │   │
│   │   │               │    │                            │   │   │
│   │   │ Run simulation│───▶│ Save results via           │   │   │
│   │   │ Return results│    │ StorageClient              │   │   │
│   │   └───────────────┘    └────────────────────────────┘   │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Recommendations

### For Structured Data: **Supabase** (Recommended)

| Aspect | Details |
|--------|---------|
| **Free Tier** | 500MB database, 1GB file storage, 2GB bandwidth |
| **Database** | PostgreSQL (full SQL support) |
| **API** | Auto-generated REST API + SDK |
| **Auth** | Built-in (optional, can use public tables) |
| **Dashboard** | Web UI for browsing data |
| **Why** | Most generous free tier, PostgreSQL is queryable, REST API for AI agents |

**Alternatives considered:**
- **Neon**: Serverless PostgreSQL, good free tier, but less features than Supabase
- **Turso**: SQLite-based, very fast, but less ecosystem support
- **PlanetScale**: No free tier anymore ($39/month minimum)

### For Artifacts/Blobs: **Cloudflare R2** (Recommended)

| Aspect | Details |
|--------|---------|
| **Free Tier** | 10GB storage, 1M writes/month, 10M reads/month |
| **Egress** | **Free** (unlike S3!) |
| **API** | Full S3-compatible API |
| **Access** | Signed URLs, public buckets, or authenticated |
| **Why** | Zero egress fees means free downloads, S3-compatible |

**Alternatives considered:**
- **Backblaze B2**: Cheaper storage ($0.006/GB), but egress costs unless via Cloudflare
- **Modal Volume**: Already have it, but not directly accessible, not queryable
- **Supabase Storage**: 1GB free limit too small for many runs

---

## Data Model

### PostgreSQL Schema (Supabase)

```sql
-- Jobs table (top-level experiment tracking)
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,           -- e.g., "castle-river-mountain"
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, running, completed, failed
    description TEXT,

    -- Configuration
    sweep_type TEXT NOT NULL,          -- ring, balanced, single
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
    completed_runs INTEGER,
    failed_runs INTEGER,
    error TEXT,
    notes TEXT,

    -- Metadata
    modal_experiment_id TEXT,          -- Link to Modal Volume path

    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);

-- Runs table (individual simulation runs)
CREATE TABLE runs (
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
    regime TEXT,                       -- 'passive', 'active', etc.

    -- Execution details
    execution_time_ms INTEGER,
    modal_call_id TEXT,
    error TEXT,

    -- Artifact URLs (Cloudflare R2)
    scenario_yaml_url TEXT,
    events_jsonl_url TEXT,
    balances_csv_url TEXT,
    run_html_url TEXT,
    metrics_html_url TEXT,

    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);

-- Metrics table (queryable numeric results)
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    run_id TEXT REFERENCES runs(run_id) ON DELETE CASCADE,
    job_id TEXT REFERENCES jobs(job_id) ON DELETE CASCADE,

    -- Key metrics
    delta_total DECIMAL,               -- Default rate
    phi_total DECIMAL,                 -- Clearing rate
    n_defaults INTEGER,
    n_clears INTEGER,
    time_to_stability INTEGER,

    -- Dealer metrics (for balanced comparison)
    trading_effect DECIMAL,            -- delta_passive - delta_active
    total_trades INTEGER,
    total_trade_volume DECIMAL,

    -- Raw metrics JSON (for flexibility)
    raw_metrics JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Job events table (lifecycle logging)
CREATE TABLE job_events (
    id SERIAL PRIMARY KEY,
    job_id TEXT REFERENCES jobs(job_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,          -- created, started, progress, completed, failed
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    details JSONB DEFAULT '{}'
);

-- Indexes for common queries
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created ON jobs(created_at DESC);
CREATE INDEX idx_runs_job_id ON runs(job_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_metrics_job_id ON metrics(job_id);
CREATE INDEX idx_metrics_run_id ON metrics(run_id);
CREATE INDEX idx_metrics_delta ON metrics(delta_total);
CREATE INDEX idx_job_events_job ON job_events(job_id);
```

### Cloudflare R2 Structure

```
bilancio-artifacts/
├── {job_id}/
│   ├── job_manifest.json           # Full job metadata (backup)
│   └── runs/
│       └── {run_id}/
│           ├── scenario.yaml
│           ├── events.jsonl
│           ├── balances.csv
│           ├── run.html
│           └── metrics.html
```

---

## Implementation

### New Module: `src/bilancio/cloud/storage/`

```
src/bilancio/cloud/storage/
├── __init__.py
├── protocol.py           # CloudStorageClient protocol
├── supabase_client.py    # Supabase implementation
├── r2_client.py          # Cloudflare R2 implementation
└── composite_client.py   # Combines both (Supabase + R2)
```

### Storage Protocol

```python
# src/bilancio/cloud/storage/protocol.py

from typing import Protocol, Optional, List
from datetime import datetime
from decimal import Decimal

@runtime_checkable
class CloudStorageClient(Protocol):
    """Protocol for cloud storage operations."""

    # Job operations
    def save_job(self, job: Job) -> None:
        """Save or update a job record."""
        ...

    def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by ID."""
        ...

    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Job]:
        """List jobs with optional filtering."""
        ...

    # Run operations
    def save_run(self, run: RunRecord) -> None:
        """Save or update a run record."""
        ...

    def get_run(self, run_id: str) -> Optional[RunRecord]:
        """Retrieve a run by ID."""
        ...

    def list_runs(
        self,
        job_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[RunRecord]:
        """List runs with optional filtering."""
        ...

    # Metrics operations
    def save_metrics(self, run_id: str, metrics: Metrics) -> None:
        """Save metrics for a run."""
        ...

    def query_metrics(
        self,
        job_id: Optional[str] = None,
        min_delta: Optional[Decimal] = None,
        max_delta: Optional[Decimal] = None,
        regime: Optional[str] = None,
    ) -> List[Metrics]:
        """Query metrics with filters."""
        ...

    # Artifact operations
    def upload_artifact(
        self,
        job_id: str,
        run_id: str,
        name: str,
        content: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload artifact, return URL."""
        ...

    def get_artifact_url(
        self,
        job_id: str,
        run_id: str,
        name: str,
        expires_in: int = 3600
    ) -> str:
        """Get signed URL for artifact download."""
        ...

    # Event logging
    def log_event(
        self,
        job_id: str,
        event_type: str,
        details: dict
    ) -> None:
        """Log a job lifecycle event."""
        ...
```

### Composite Client (Recommended)

```python
# src/bilancio/cloud/storage/composite_client.py

class CompositeStorageClient:
    """Combines Supabase (structured) + R2 (blobs)."""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        r2_account_id: str,
        r2_access_key: str,
        r2_secret_key: str,
        r2_bucket: str = "bilancio-artifacts"
    ):
        self.db = SupabaseClient(supabase_url, supabase_key)
        self.blobs = R2Client(r2_account_id, r2_access_key, r2_secret_key, r2_bucket)

    def save_job(self, job: Job) -> None:
        self.db.save_job(job)

    def upload_artifact(self, job_id: str, run_id: str, name: str, content: bytes, content_type: str) -> str:
        url = self.blobs.upload(f"{job_id}/runs/{run_id}/{name}", content, content_type)
        return url

    # ... etc
```

---

## Integration Points

### 1. Cloud Executor Integration

Modify `CloudExecutor` to persist to cloud storage after Modal execution:

```python
# src/bilancio/runners/cloud_executor.py

class CloudExecutor:
    def __init__(
        self,
        storage_client: Optional[CloudStorageClient] = None,  # NEW
        ...
    ):
        self.storage = storage_client

    def execute(self, prepared_run: PreparedRun) -> RunResult:
        # Run on Modal
        result = run_simulation.remote(...)

        # Persist to cloud storage if configured
        if self.storage:
            self._persist_to_cloud(prepared_run, result)

        return result

    def _persist_to_cloud(self, prepared_run, result):
        # Save run record
        self.storage.save_run(RunRecord(
            run_id=result.run_id,
            job_id=prepared_run.job_id,
            status=result.status,
            ...
        ))

        # Upload artifacts from Modal Volume to R2
        for name, path in result.artifacts.items():
            content = self._download_from_modal(result.storage_base, path)
            url = self.storage.upload_artifact(
                job_id=prepared_run.job_id,
                run_id=result.run_id,
                name=name,
                content=content
            )
```

### 2. CLI Integration

Add storage configuration to CLI:

```bash
# Via environment variables
export BILANCIO_SUPABASE_URL="https://xxx.supabase.co"
export BILANCIO_SUPABASE_KEY="eyJ..."
export BILANCIO_R2_ACCOUNT_ID="..."
export BILANCIO_R2_ACCESS_KEY="..."
export BILANCIO_R2_SECRET_KEY="..."

# Run with cloud storage
uv run bilancio sweep balanced --cloud --persist ...
```

### 3. Query Interface

New CLI commands for querying stored results:

```bash
# List recent jobs
uv run bilancio jobs list --limit 10

# Get job details
uv run bilancio jobs show castle-river-mountain

# Query metrics
uv run bilancio metrics query --job castle-river-mountain --format csv
uv run bilancio metrics query --min-delta 0.1 --regime passive

# Download artifacts
uv run bilancio artifacts download castle-river-mountain --run all --output ./results/
```

---

## Access Patterns

### For AI Agents (Claude Code)

```python
# Query via Supabase REST API
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/jobs?job_id=eq.{job_id}",
    headers={"apikey": SUPABASE_KEY}
)
job = response.json()[0]

# Get metrics
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/metrics?job_id=eq.{job_id}",
    headers={"apikey": SUPABASE_KEY}
)
metrics = response.json()
```

### For Humans

1. **Supabase Dashboard**: Browse jobs/runs/metrics tables directly
2. **CLI tools**: `bilancio jobs list`, `bilancio metrics query`
3. **Direct download**: Signed URLs from R2 (valid for 1 hour)

---

## Cost Analysis

### Supabase (Free Tier)

| Resource | Limit | Our Usage (est.) | OK? |
|----------|-------|------------------|-----|
| Database | 500MB | ~50MB (1000 jobs × 50KB) | ✅ |
| File Storage | 1GB | Not used (R2 for blobs) | ✅ |
| Bandwidth | 2GB | ~200MB/month | ✅ |
| API Requests | Unlimited | N/A | ✅ |

### Cloudflare R2 (Free Tier)

| Resource | Limit | Our Usage (est.) | OK? |
|----------|-------|------------------|-----|
| Storage | 10GB | ~5GB (1000 runs × 5MB) | ✅ |
| Class A ops (writes) | 1M/month | ~10K/month | ✅ |
| Class B ops (reads) | 10M/month | ~100K/month | ✅ |
| Egress | Free | Unlimited | ✅ |

**Total cost: $0/month** for typical academic research usage.

---

## Implementation Phases

### Phase 1: Core Infrastructure (This PR)
1. Set up Supabase project (free tier)
2. Set up Cloudflare R2 bucket
3. Create database schema
4. Implement `CloudStorageClient` protocol
5. Implement `SupabaseClient`
6. Implement `R2Client`
7. Implement `CompositeStorageClient`
8. Add configuration (env vars, config file)

### Phase 2: Integration
1. Integrate with `CloudExecutor`
2. Add `--persist` flag to CLI
3. Persist jobs/runs/metrics after cloud execution
4. Upload artifacts to R2 after Modal execution

### Phase 3: Query Interface
1. Add `bilancio jobs list/show` commands
2. Add `bilancio metrics query` command
3. Add `bilancio artifacts download` command
4. Add Supabase dashboard documentation

### Phase 4: Polish
1. Add data export (CSV, JSON)
2. Add job comparison views
3. Document for team members
4. Add cleanup/retention policies

---

## Configuration

### Environment Variables

```bash
# Supabase (required for cloud storage)
BILANCIO_SUPABASE_URL=https://xxxx.supabase.co
BILANCIO_SUPABASE_ANON_KEY=eyJhbG...

# Cloudflare R2 (required for artifact storage)
BILANCIO_R2_ACCOUNT_ID=xxxxxxxxxxxx
BILANCIO_R2_ACCESS_KEY_ID=xxxxxxxxxxxx
BILANCIO_R2_SECRET_ACCESS_KEY=xxxxxxxxxxxx
BILANCIO_R2_BUCKET=bilancio-artifacts

# Optional: Custom endpoint for R2
BILANCIO_R2_ENDPOINT=https://{account_id}.r2.cloudflarestorage.com
```

### Config File (alternative)

```yaml
# ~/.bilancio/config.yaml
storage:
  provider: supabase+r2
  supabase:
    url: https://xxxx.supabase.co
    key: eyJhbG...
  r2:
    account_id: xxxxxxxxxxxx
    access_key: xxxxxxxxxxxx
    secret_key: xxxxxxxxxxxx
    bucket: bilancio-artifacts
```

---

## Migration Path

### From Modal Volume Only → Cloud Storage

1. **No breaking changes**: Cloud storage is opt-in via `--persist` flag
2. **Modal Volume remains**: Still used as intermediate storage during execution
3. **Post-execution sync**: After Modal finishes, artifacts are copied to R2
4. **Gradual adoption**: Can run without cloud storage configured

```
Modal Execution → Modal Volume (temp) → R2 (permanent) + Supabase (metadata)
```

---

## Security Considerations

1. **Supabase Row-Level Security**: Can enable later if needed for multi-user
2. **R2 Signed URLs**: Artifacts not publicly accessible, time-limited URLs
3. **API Keys**: Stored as environment variables, not in code
4. **No secrets in artifacts**: Scenario files don't contain sensitive data

---

## Testing

1. **Unit tests**: Mock Supabase/R2 clients
2. **Integration tests**: Test with actual free tier accounts
3. **E2E test**: Run cloud sweep → verify data in Supabase + R2

---

## Future Enhancements

1. **Multi-user support**: Add user_id to jobs/runs, enable RLS
2. **Web dashboard**: Simple React app to browse results
3. **Notifications**: Webhook on job completion
4. **Data retention**: Auto-delete old artifacts after N days
5. **Alternative backends**: SQLite for local-only mode, other S3 providers

---

## Summary

| Component | Service | Cost | Purpose |
|-----------|---------|------|---------|
| Structured data | Supabase | Free | Jobs, runs, metrics (queryable) |
| Artifacts | Cloudflare R2 | Free | events.jsonl, balances.csv, HTML |
| Compute | Modal | Pay-per-use | Run simulations |

**Key benefits:**
- ✅ Modular (storage independent of compute)
- ✅ Queryable (SQL for metrics, filtering)
- ✅ Accessible (REST API, web dashboard, CLI)
- ✅ Free (within typical research usage)
- ✅ Durable (data persists across conversations)
