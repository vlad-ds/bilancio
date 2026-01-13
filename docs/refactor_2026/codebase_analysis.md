# Bilancio Codebase Analysis & Refactoring Plan

**Date:** January 2026
**Purpose:** Prepare the codebase for cloud execution, database storage, and scalability

---

## Executive Summary

The bilancio codebase has evolved organically from a general balance-sheet simulator into a sophisticated financial modeling framework with dealer networks, Kalecki ring experiments, and parametric sweeps. While the architecture is fundamentally sound, some areas need cleanup before adding cloud/database capabilities.

**Key Statistics:**
- 276 tests, all passing
- 53% overall code coverage
- ~15,000 lines of core library code
- 25 development plans documented

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────┐
│  EXPERIMENTS LAYER                                      │
│  experiments/, scripts/, dashboards/                    │
│  (Sweep runners, parameter grids, comparisons)          │
├─────────────────────────────────────────────────────────┤
│  SCENARIOS LAYER                                        │
│  scenarios/generators/, examples/                       │
│  (Ring explorer, YAML configs, worked examples)         │
├─────────────────────────────────────────────────────────┤
│  ANALYSIS LAYER                                         │
│  analysis/, export/, ui/render/                         │
│  (Metrics, reports, HTML export, visualization)         │
├─────────────────────────────────────────────────────────┤
│  SIMULATION ENGINE                                      │
│  engines/ (simulation, settlement, clearing)            │
│  dealer/ (kernel, trading, simulation)                  │
├─────────────────────────────────────────────────────────┤
│  DOMAIN LAYER                                           │
│  domain/ (agents, instruments, policy)                  │
│  ops/ (banking, cashflows, primitives)                  │
├─────────────────────────────────────────────────────────┤
│  CORE LAYER                                             │
│  core/ (time, atomic, errors, ids, invariants)          │
└─────────────────────────────────────────────────────────┘
```

---

## What's Working Well

### 1. Core Domain Model (Excellent)

The Agent/Instrument/Policy separation is clean and well-tested:
- `domain/agents/`: Bank, Household, Firm, CentralBank, Dealer, VBT - all 100% coverage
- `domain/instruments/`: Credit, delivery, means of payment - clear inheritance
- `domain/policy.py`: 100% coverage, enforces who can issue/hold what

### 2. Dealer Ring Implementation (Excellent)

The most comprehensive part of the codebase:
- `dealer/kernel.py`: 97% test coverage, implements core trading algorithms
- `dealer/simulation.py`: 85% coverage, 6-phase event loop
- `dealer/metrics.py`: PnL, safety margin, liquidity tracking
- 14 worked examples in `examples/dealer_ring/` serve as living documentation

### 3. Event-Driven Design (Good)

All state changes produce immutable events:
```python
system.log(kind="PayableSettled", day=5, contract_id="P_abc123", amount=1000)
```
This enables:
- Complete audit trail
- Post-hoc analysis without re-running simulations
- Replay and debugging

### 4. Deterministic Experiments (Good)

Seed-based reproducibility enables rigorous comparisons:
- Same seed → identical scenario and outcomes
- Paired control/treatment runs with same seed, different dealer config
- Registry tracks all parameters for each run

### 5. Kalecki Metric System (Good)

Well-defined metrics from the economics literature:
- φ (phi): On-time settlement ratio
- δ (delta): Default/deferral ratio
- G_t: Liquidity gap
- Velocity, HHI, debtor shortfall shares

---

## Issues to Address

### 1. Large Files Needing Decomposition

| File | Lines | Problem |
|------|-------|---------|
| `ui/cli.py` | 1,100+ | Mixes sweep commands, run logic, display formatting |
| `analysis/visualization.py` | 2,200+ | Balance display, event display, phase visualization all in one |
| `engines/system.py` | 800+ | State management, operations, and logging interleaved |
| `experiments/ring.py` | 680+ | Runner logic mixed with 3 sampling strategies |

### 2. Test Coverage Gaps

| Module | Coverage | Impact |
|--------|----------|--------|
| `experiments/*.py` | 0-25% | **HIGH** - drives research, untested |
| `analysis/visualization.py` | 13% | Medium - UI-facing but not critical path |
| `ui/cli.py` | 34% | Medium - user-facing entry point |
| `experiments/balanced_comparison.py` | 0% | HIGH - Plan 021/024 experiments |
| `experiments/comparison.py` | 0% | HIGH - Control/treatment framework |

### 3. Structural Inconsistencies

- **`modules/dealer_ring/`**: Empty directory, duplicates `dealer/`
- **`io/` vs `export/`**: Two modules with overlapping reader/writer concerns
- **`scenarios/generators/`**: Only contains `ring_explorer.py`, overly nested
- **`ui/render/` vs `analysis/visualization.py`**: Overlapping rendering logic

### 4. Missing Abstractions for Future Requirements

Current state assessment:

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Cloud execution | Everything runs locally via subprocess | No job abstraction |
| Database storage | File-based output (CSV/JSON/HTML) | No database models |
| Parallel execution | Sequential experiment runs | No task queue |
| Remote access | CLI only | No API layer |

---

## Refactoring Plan

### Phase 1: Cleanup (Low Risk)

**Goal:** Remove dead code, fix inconsistencies, improve organization

#### 1.1 Delete Dead Code
```bash
# Remove empty module
rm -rf modules/dealer_ring/

# Merge io/ into export/
mv io/readers.py export/
rm -rf io/
```

#### 1.2 Flatten Unnecessary Nesting
```bash
# Move ring_explorer up from overly nested location
mv scenarios/generators/ring_explorer.py scenarios/
rmdir scenarios/generators/
```

#### 1.3 Update Stale Documentation
- `TODO.md` is 3 lines and outdated
- Add completion markers to plan files

### Phase 2: Split Large Files (Medium Risk)

#### 2.1 Split CLI
```
ui/cli.py → ui/cli/
              ├── __init__.py  (main entry point)
              ├── run.py       (scenario execution)
              ├── sweep.py     (experiment sweeps)
              └── display.py   (output formatting)
```

#### 2.2 Split Visualization
```
analysis/visualization.py → analysis/visualization/
                              ├── __init__.py
                              ├── balances.py   (T-account display)
                              ├── events.py     (event tables)
                              └── phases.py     (phase summaries)
```

#### 2.3 Extract Sampling Strategies
```
experiments/ring.py → experiments/
                        ├── ring.py           (RingSweepRunner only)
                        └── sampling/
                              ├── grid.py     (Cartesian product)
                              ├── lhs.py      (Latin Hypercube)
                              └── frontier.py (Binary search)
```

### Phase 3: Add Test Coverage (Medium Risk)

Priority order:

1. **Experiment framework** (highest impact):
   - Test `RingSweepRunner` with 2x2 grid
   - Test `ComparisonSweepRunner` paired runs
   - Test `BalancedComparisonRunner`

2. **CLI integration**:
   - Test `bilancio run` with sample scenario
   - Test `bilancio sweep ring --grid` with minimal config

3. **Visualization** (lower priority):
   - Test balance display formatting
   - Test HTML export edge cases

### Phase 4: Abstraction Layer for Cloud/DB (Architecture Change)

#### 4.1 Storage Abstraction

```python
# storage/base.py
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

class RunResult(BaseModel):
    run_id: str
    parameters: dict
    metrics: dict
    status: str
    output_paths: dict

class ResultStore(ABC):
    @abstractmethod
    def save_run(self, result: RunResult) -> None:
        """Persist a run result."""
        ...

    @abstractmethod
    def load_run(self, run_id: str) -> Optional[RunResult]:
        """Load a run result by ID."""
        ...

    @abstractmethod
    def query_runs(self, filters: dict) -> list[RunResult]:
        """Query runs by parameter filters."""
        ...

    @abstractmethod
    def list_runs(self, experiment_id: str) -> list[str]:
        """List all run IDs for an experiment."""
        ...
```

```python
# storage/file_store.py
class FileResultStore(ResultStore):
    """Current CSV/JSON implementation."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def save_run(self, result: RunResult) -> None:
        # Write to registry CSV + JSON files
        ...
```

```python
# storage/db_store.py (future)
class DatabaseResultStore(ResultStore):
    """PostgreSQL/SQLite implementation."""

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)

    def save_run(self, result: RunResult) -> None:
        # Insert into database
        ...
```

#### 4.2 Runner Abstraction

```python
# runners/base.py
from abc import ABC, abstractmethod
from enum import Enum

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class RunJob(BaseModel):
    job_id: str
    scenario: dict
    config: dict

class ExperimentRunner(ABC):
    @abstractmethod
    def submit(self, job: RunJob) -> str:
        """Submit a job, return job_id."""
        ...

    @abstractmethod
    def status(self, job_id: str) -> JobStatus:
        """Check job status."""
        ...

    @abstractmethod
    def result(self, job_id: str) -> Optional[RunResult]:
        """Get result if completed."""
        ...

    @abstractmethod
    def cancel(self, job_id: str) -> bool:
        """Cancel a pending/running job."""
        ...
```

```python
# runners/local_runner.py
class LocalRunner(ExperimentRunner):
    """Current subprocess-based implementation."""
    ...
```

```python
# runners/cloud_runner.py (future)
class CloudRunner(ExperimentRunner):
    """AWS Batch / GCP Cloud Run / etc."""
    ...
```

#### 4.3 Updated Experiment Runner

```python
# experiments/ring.py (refactored)
class RingSweepRunner:
    def __init__(
        self,
        runner: ExperimentRunner,  # Injected dependency
        store: ResultStore,        # Injected dependency
        config: RingSweepConfig,
    ):
        self.runner = runner
        self.store = store
        self.config = config

    def run_sweep(self) -> list[RunResult]:
        jobs = self._generate_jobs()

        # Submit all jobs (local or cloud)
        job_ids = [self.runner.submit(job) for job in jobs]

        # Wait for completion
        results = []
        for job_id in job_ids:
            while self.runner.status(job_id) == JobStatus.RUNNING:
                time.sleep(1)
            result = self.runner.result(job_id)
            self.store.save_run(result)
            results.append(result)

        return results
```

---

## Proposed File Organization

```
bilancio/
├── core/                    # KEEP AS-IS (excellent)
│   ├── time.py
│   ├── atomic.py
│   ├── errors.py
│   ├── ids.py
│   └── invariants.py
│
├── domain/                  # KEEP AS-IS (excellent)
│   ├── agents/
│   │   ├── agent.py
│   │   ├── bank.py
│   │   ├── central_bank.py
│   │   ├── dealer.py
│   │   ├── firm.py
│   │   ├── household.py
│   │   ├── treasury.py
│   │   └── vbt.py
│   ├── instruments/
│   │   ├── base.py
│   │   ├── credit.py
│   │   ├── delivery.py
│   │   └── means_of_payment.py
│   ├── policy.py
│   └── goods.py
│
├── ops/                     # KEEP AS-IS
│   ├── banking.py
│   ├── cashflows.py
│   ├── primitives.py
│   └── primitives_stock.py
│
├── engines/                 # MINOR REFACTOR
│   ├── simulation.py
│   ├── settlement.py
│   ├── clearing.py
│   ├── dealer_integration.py
│   └── system.py            # Consider splitting state.py
│
├── dealer/                  # KEEP AS-IS (excellent)
│   ├── kernel.py
│   ├── trading.py
│   ├── simulation.py
│   ├── metrics.py
│   ├── models.py
│   ├── events.py
│   ├── report.py
│   └── bridge.py
│
├── analysis/                # REFACTOR
│   ├── balances.py
│   ├── metrics.py
│   ├── report.py
│   ├── dealer_usage_summary.py
│   ├── strategy_outcomes.py
│   └── visualization/       # SPLIT from single 2200-line file
│       ├── __init__.py
│       ├── balances.py
│       ├── events.py
│       └── phases.py
│
├── experiments/             # REFACTOR
│   ├── ring.py
│   ├── comparison.py
│   ├── balanced_comparison.py
│   └── sampling/            # EXTRACT from ring.py
│       ├── __init__.py
│       ├── grid.py
│       ├── lhs.py
│       └── frontier.py
│
├── scenarios/               # SIMPLIFY
│   └── ring_explorer.py     # Move up from generators/
│
├── storage/                 # NEW
│   ├── __init__.py
│   ├── base.py              # Abstract ResultStore
│   ├── file_store.py        # Current implementation
│   └── registry.py          # CSV registry management
│
├── runners/                 # NEW
│   ├── __init__.py
│   ├── base.py              # Abstract ExperimentRunner
│   └── local_runner.py      # Current implementation
│
├── ui/
│   ├── cli/                 # SPLIT from single 1100-line file
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── run.py
│   │   └── sweep.py
│   ├── display.py
│   ├── html_export.py
│   └── render/
│       ├── formatters.py
│       ├── models.py
│       └── rich_builders.py
│
├── export/                  # CONSOLIDATE (merge io/)
│   ├── readers.py           # From io/
│   └── writers.py
│
└── config/                  # KEEP AS-IS
    ├── models.py
    ├── loaders.py
    └── apply.py
```

---

## Quick Wins (Do First)

1. **Delete `modules/dealer_ring/`** - empty and confusing
2. **Merge `io/` into `export/`** - consolidate I/O code
3. **Flatten `scenarios/generators/`** - unnecessary nesting
4. **Update `TODO.md`** - currently stale (3 lines)

---

## Migration Path for Economist User

Once abstractions are in place, the economist can:

1. **Local development**: Use `LocalRunner` + `FileResultStore` (current behavior)
2. **Cloud execution**: Swap in `CloudRunner` + `DatabaseResultStore`
3. **Results analysis**: Query database directly or via Python API

Example future workflow:
```python
from bilancio.storage import DatabaseResultStore
from bilancio.runners import CloudRunner
from bilancio.experiments import RingSweepRunner, RingSweepConfig

# Configure for cloud
store = DatabaseResultStore("postgresql://...")
runner = CloudRunner(api_key="...")

# Same experiment code works locally or in cloud
config = RingSweepConfig.from_yaml("sweep_config.yaml")
sweep = RingSweepRunner(runner=runner, store=store, config=config)
results = sweep.run_sweep()

# Query past results
past_runs = store.query_runs({"kappa": 2.0, "dealer_enabled": True})
```

---

## Next Steps

1. **Immediate**: Phase 1 cleanup (delete dead code, merge modules)
2. **Short-term**: Phase 2 file splits (CLI, visualization)
3. **Medium-term**: Phase 3 test coverage (experiments framework)
4. **Longer-term**: Phase 4 abstractions (storage, runners)

Each phase can be done incrementally without breaking existing functionality.
