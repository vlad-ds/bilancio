# Plan 029: Job System for Claude Code Web Workflow

**Status**: Implemented (Phase 1 & 2 complete)
**Goal**: Create a job abstraction for tracking simulation runs triggered via Claude Code web interface

---

## Problem Statement

When running simulations via Claude Code on the web (claude.ai/code), we need:
1. A way to uniquely identify and reference simulation jobs
2. Logging of job events (triggered, completed, failed)
3. Job-aware simulation execution (runs know which job they belong to)
4. Easy retrieval of job results by memorable ID

Currently, simulations use auto-generated `run_id` values (e.g., `grid_adce4ba959de`) which are not memorable or easy to communicate between team members.

---

## Design

### 1. Job ID Generation

Generate memorable 4-word passphrases as job IDs:

```
castle-river-mountain-forest
bright-ocean-swift-tiger
quiet-meadow-golden-hawk
```

**Implementation:**
- Use a word list (e.g., EFF diceware short list or custom curated list)
- Generate 4 random words, joined by hyphens
- Ensure uniqueness by checking against existing jobs (optional collision check)

**Location:** `src/bilancio/jobs/job_id.py`

```python
def generate_job_id() -> str:
    """Generate a memorable 4-word job ID."""
    words = random.sample(WORD_LIST, 4)
    return "-".join(words)
```

### 2. Job Model

A Job represents a complete simulation request:

```python
@dataclass
class Job:
    job_id: str                    # e.g., "castle-river-mountain-forest"
    created_at: datetime           # When job was created
    status: JobStatus              # pending, running, completed, failed
    description: str               # User's natural language request
    config: JobConfig              # Simulation configuration
    run_ids: List[str]             # Individual run IDs within this job
    completed_at: Optional[datetime]
    error: Optional[str]
    notes: Optional[str]           # Additional context

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class JobConfig:
    sweep_type: str                # "ring", "balanced", "single"
    n_agents: int
    kappas: List[Decimal]
    concentrations: List[Decimal]
    mus: List[Decimal]
    # ... other parameters
    cloud: bool                    # Whether to run on Modal
```

**Location:** `src/bilancio/jobs/models.py`

### 3. Job Lifecycle

```
User Request
    │
    ▼
┌─────────────────┐
│  Create Job     │  ← generate_job_id(), status=PENDING
│  Log: created   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Start Job      │  ← status=RUNNING
│  Log: started   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Run Sweeps     │  ← Each run gets run_id, linked to job_id
│  Log: progress  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Complete Job   │  ← status=COMPLETED or FAILED
│  Log: completed │
└─────────────────┘
```

### 4. Job Event Log

Every job state change is logged:

```python
@dataclass
class JobEvent:
    job_id: str
    event_type: str      # "created", "started", "progress", "completed", "failed"
    timestamp: datetime
    details: dict        # Event-specific data
```

**Event types:**
- `created`: Job initialized with config
- `started`: Execution began
- `progress`: Run completed (includes run_id, metrics)
- `completed`: All runs finished successfully
- `failed`: Job failed (includes error message)

### 5. Job-Aware Execution

Modify sweep runners to accept and propagate job context:

```python
# In CLI
job = create_job(
    description="Test dealer impact in stressed system",
    config=JobConfig(sweep_type="balanced", ...)
)

runner = BalancedComparisonRunner(
    config=config,
    out_dir=out_dir,
    executor=executor,
    job_id=job.job_id,  # NEW: Pass job context
)
```

The job_id flows through to:
- Output directory naming (`out/experiments/<job_id>/`)
- Modal Volume path (`<job_id>/runs/...`)
- Run metadata (each run knows its parent job)

### 6. Job Manifest

Each job writes a `job_manifest.json` to its output directory:

```json
{
  "job_id": "castle-river-mountain-forest",
  "created_at": "2025-01-12T10:30:00Z",
  "completed_at": "2025-01-12T10:45:00Z",
  "status": "completed",
  "description": "Test dealer impact in stressed system with kappa 0.3-0.5",
  "config": {
    "sweep_type": "balanced",
    "n_agents": 50,
    "kappas": ["0.3", "0.5"],
    "concentrations": ["1"],
    "mus": ["0"],
    "cloud": true
  },
  "runs": [
    {"run_id": "balanced_passive_abc123", "status": "completed"},
    {"run_id": "balanced_active_def456", "status": "completed"}
  ],
  "summary": {
    "total_runs": 4,
    "completed_runs": 4,
    "failed_runs": 0,
    "avg_delta_passive": 0.15,
    "avg_delta_active": 0.12,
    "avg_trading_effect": 0.03
  }
}
```

---

## Implementation Steps

### Phase 1: Core Job Abstraction

1. **Create job module structure**
   ```
   src/bilancio/jobs/
   ├── __init__.py
   ├── job_id.py      # ID generation
   ├── models.py      # Job, JobConfig, JobEvent
   └── manager.py     # Job lifecycle management
   ```

2. **Implement job ID generator**
   - Curate word list (~500 words, easy to spell/remember)
   - Generate function with optional collision check

3. **Implement Job dataclass and JobConfig**

4. **Implement JobManager**
   ```python
   class JobManager:
       def create_job(description: str, config: JobConfig) -> Job
       def start_job(job_id: str) -> None
       def record_progress(job_id: str, run_id: str, metrics: dict) -> None
       def complete_job(job_id: str, summary: dict) -> None
       def fail_job(job_id: str, error: str) -> None
       def get_job(job_id: str) -> Optional[Job]
   ```

### Phase 2: CLI Integration

5. **Add --job-id flag to sweep commands** (optional, auto-generated if not provided)

6. **Modify sweep runners to accept job_id**

7. **Write job_manifest.json on completion**

### Phase 3: Storage Layer (Future)

8. **Job registry** - Index of all jobs (JSON file or database)
9. **Job event log persistence** - Append-only log of events
10. **Query interface** - Find jobs by ID, date, status

---

## File Changes

| File | Change |
|------|--------|
| `src/bilancio/jobs/__init__.py` | New: Package init |
| `src/bilancio/jobs/job_id.py` | New: ID generation |
| `src/bilancio/jobs/models.py` | New: Job, JobConfig, JobEvent |
| `src/bilancio/jobs/manager.py` | New: JobManager |
| `src/bilancio/jobs/wordlist.py` | New: Curated word list |
| `src/bilancio/ui/cli/sweep.py` | Modify: Add job integration |
| `src/bilancio/experiments/ring.py` | Modify: Accept job_id |
| `src/bilancio/experiments/balanced_comparison.py` | Modify: Accept job_id |
| `CLAUDE.md` | Update: Document job workflow |

---

## Usage Examples

### Creating a job programmatically

```python
from bilancio.jobs import JobManager, JobConfig

manager = JobManager()
job = manager.create_job(
    description="Test dealer impact in stressed system",
    config=JobConfig(
        sweep_type="balanced",
        n_agents=50,
        kappas=[Decimal("0.3"), Decimal("0.5")],
        concentrations=[Decimal("1")],
        mus=[Decimal("0")],
        cloud=True,
    )
)
print(f"Job created: {job.job_id}")  # "castle-river-mountain-forest"
```

### CLI with job ID

```bash
# Auto-generate job ID
uv run bilancio sweep balanced --cloud --out-dir out/experiments/auto ...
# Output: Job ID: castle-river-mountain-forest

# Or specify job ID
uv run bilancio sweep balanced --cloud --job-id my-custom-job-name ...
```

### Retrieving job results

```bash
# List all jobs
uv run bilancio jobs list

# Get job details
uv run bilancio jobs show castle-river-mountain-forest

# Get job results
uv run bilancio jobs results castle-river-mountain-forest
```

---

## CLAUDE.md Documentation Update

Add to CLAUDE.md:

```markdown
## Job System

Every simulation sweep is tracked as a **Job** with a memorable ID.

### Job IDs
- Format: `word1-word2-word3-word4` (e.g., `castle-river-mountain-forest`)
- Auto-generated when you run a sweep
- Use this ID to reference results in conversations

### Job Workflow
1. Start sweep → Job ID generated and displayed
2. Runs execute → Progress tracked under job
3. Completion → job_manifest.json written with summary
4. Reference → Use job ID to query results later

### Example
User: "Run a dealer comparison with stressed liquidity"
Claude: "Starting job `bright-ocean-swift-tiger`..."
[Later]
User: "What were the results of bright-ocean-swift-tiger?"
Claude: [Retrieves and summarizes results]
```

---

## Testing

1. **Unit tests for job ID generation**
   - Uniqueness over 1000 generations
   - Format validation (4 words, hyphen-separated)

2. **Unit tests for JobManager**
   - Create/start/complete lifecycle
   - Event logging

3. **Integration test**
   - Run small sweep with job tracking
   - Verify job_manifest.json written correctly

---

## Future Enhancements

1. **Job search/filtering** - Find jobs by date range, status, parameters
2. **Job comparison** - Compare results across multiple jobs
3. **Job notifications** - Webhook/email when job completes
4. **Job resumption** - Resume failed jobs from last checkpoint
5. **External database** - Store jobs in PostgreSQL/SQLite for persistence across sessions
