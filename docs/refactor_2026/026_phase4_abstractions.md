# Plan 026: Phase 4 - Storage and Runner Abstractions

**Date:** January 2026
**Branch:** `refactor/phase-4-abstractions`
**Goal:** Create abstraction layers to enable swapping file storage for database storage and local execution for cloud execution

---

## Background

The bilancio codebase currently:
- Stores all results as files (CSV, JSON, YAML, HTML)
- Runs simulations in-process via `run_scenario()`
- Uses CSV registry files to track experiment runs
- Has three experiment runners: `RingSweepRunner`, `ComparisonSweepRunner`, `BalancedComparisonRunner`

This works well for local development but creates friction for:
- Cloud execution (need to collect results from remote workers)
- Database storage (querying past experiments, dashboards)
- Parallel/distributed execution (coordination across workers)

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  RingSweepRunner / ComparisonSweepRunner / BalancedComparison │
│  ↓                                                           │
│  Generates scenario configs                                  │
│  ↓                                                           │
│  Calls run_scenario() directly (in-process)                  │
│  ↓                                                           │
│  Writes files to disk (CSV, JSON, HTML)                      │
│  ↓                                                           │
│  Updates registry CSV                                        │
└─────────────────────────────────────────────────────────────┘
```

**Key files currently produced per run:**
- `scenario.yaml` - Input configuration
- `events.jsonl` - Full event log
- `balances.csv` - Balance snapshots
- `metrics.csv` / `metrics.json` - Day-by-day metrics
- `run.html` - Visual report
- `dealer_metrics.json` - Dealer summary (if enabled)

**Registry format:** CSV with fields like `run_id`, `phase`, `seed`, `kappa`, `phi_total`, `delta_total`, `status`, `error`, plus file paths.

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  RingSweepRunner / ComparisonSweepRunner / BalancedComparison │
│  ↓                                                           │
│  Generates scenario configs                                  │
│  ↓                                                           │
│  SimulationExecutor.execute(config) → RunResult              │
│  ↓                                                           │
│  ResultStore.save_run(result)                                │
│  ResultStore.save_registry_entry(metadata)                   │
└─────────────────────────────────────────────────────────────┘

Implementations:
┌─────────────────────┐    ┌─────────────────────┐
│ LocalExecutor       │    │ CloudExecutor       │
│ (current behavior)  │    │ (AWS/GCP, future)   │
└─────────────────────┘    └─────────────────────┘

┌─────────────────────┐    ┌─────────────────────┐
│ FileResultStore     │    │ DatabaseResultStore │
│ (current behavior)  │    │ (PostgreSQL, future)│
└─────────────────────┘    └─────────────────────┘
```

---

## Implementation Plan

### Part A: Define Core Models and Protocols

Create `src/bilancio/storage/models.py`:

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path
from enum import Enum

class RunStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class RunArtifacts:
    """References to simulation output artifacts."""
    scenario_yaml: Optional[str] = None      # Path or blob key
    events_jsonl: Optional[str] = None
    balances_csv: Optional[str] = None
    metrics_csv: Optional[str] = None
    metrics_json: Optional[str] = None
    run_html: Optional[str] = None
    dealer_metrics_json: Optional[str] = None
    trades_csv: Optional[str] = None
    repayment_events_csv: Optional[str] = None

@dataclass
class RunResult:
    """Complete result of a single simulation run."""
    run_id: str
    status: RunStatus
    parameters: Dict[str, Any]           # Input parameters (seed, kappa, etc.)
    metrics: Dict[str, Any]              # Output metrics (phi_total, delta_total, etc.)
    artifacts: RunArtifacts              # References to output files
    error: Optional[str] = None          # Error message if failed
    execution_time_ms: Optional[int] = None

@dataclass
class RegistryEntry:
    """Metadata for registry storage."""
    run_id: str
    experiment_id: str                   # Groups runs into experiments
    status: RunStatus
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    artifact_paths: Dict[str, str]       # Artifact name -> path/key mapping
    error: Optional[str] = None
```

Create `src/bilancio/storage/protocols.py`:

```python
from typing import Protocol, Optional, List, Dict, Any, BinaryIO
from .models import RunResult, RegistryEntry, RunArtifacts

class ResultStore(Protocol):
    """Protocol for storing simulation results."""

    def save_artifact(
        self,
        experiment_id: str,
        run_id: str,
        name: str,
        content: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Save an artifact, return its reference (path or key)."""
        ...

    def save_run(self, experiment_id: str, result: RunResult) -> None:
        """Save a complete run result."""
        ...

    def load_run(self, experiment_id: str, run_id: str) -> Optional[RunResult]:
        """Load a run result by ID."""
        ...

    def load_artifact(self, reference: str) -> bytes:
        """Load artifact content by reference."""
        ...

class RegistryStore(Protocol):
    """Protocol for experiment registry storage."""

    def upsert(self, entry: RegistryEntry) -> None:
        """Insert or update a registry entry."""
        ...

    def get(self, experiment_id: str, run_id: str) -> Optional[RegistryEntry]:
        """Get a specific registry entry."""
        ...

    def list_runs(self, experiment_id: str) -> List[str]:
        """List all run IDs for an experiment."""
        ...

    def get_completed_keys(self, experiment_id: str) -> set:
        """Get set of completed parameter keys for resumption."""
        ...

    def query(
        self,
        experiment_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RegistryEntry]:
        """Query registry entries with optional filters."""
        ...
```

Create `src/bilancio/runners/protocols.py`:

```python
from typing import Protocol, Optional, Dict, Any, Callable
from ..storage.models import RunResult, RunStatus

class SimulationExecutor(Protocol):
    """Protocol for executing simulations."""

    def execute(
        self,
        scenario_config: Dict[str, Any],
        run_id: str,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> RunResult:
        """Execute a simulation, return result."""
        ...

class JobExecutor(Protocol):
    """Protocol for async/distributed job execution (future)."""

    def submit(self, scenario_config: Dict[str, Any], run_id: str) -> str:
        """Submit job, return job_id."""
        ...

    def status(self, job_id: str) -> RunStatus:
        """Check job status."""
        ...

    def result(self, job_id: str) -> Optional[RunResult]:
        """Get result if completed."""
        ...

    def cancel(self, job_id: str) -> bool:
        """Cancel a pending/running job."""
        ...
```

### Part B: Implement FileResultStore

Create `src/bilancio/storage/file_store.py`:

```python
"""File-based result storage (current behavior wrapped in protocol)."""

import json
import csv
from pathlib import Path
from typing import Optional, List, Dict, Any

from .models import RunResult, RegistryEntry, RunArtifacts, RunStatus
from .protocols import ResultStore, RegistryStore

class FileResultStore:
    """Store results as files on local filesystem."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _run_dir(self, experiment_id: str, run_id: str) -> Path:
        return self.base_dir / experiment_id / "runs" / run_id

    def save_artifact(
        self,
        experiment_id: str,
        run_id: str,
        name: str,
        content: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Save artifact to file, return relative path."""
        run_dir = self._run_dir(experiment_id, run_id)
        run_dir.mkdir(parents=True, exist_ok=True)

        # Determine subdirectory based on artifact type
        if name in ("scenario.yaml",):
            path = run_dir / name
        else:
            out_dir = run_dir / "out"
            out_dir.mkdir(exist_ok=True)
            path = out_dir / name

        path.write_bytes(content)
        return str(path.relative_to(self.base_dir))

    def save_run(self, experiment_id: str, result: RunResult) -> None:
        """Save run result (artifacts should already be saved)."""
        run_dir = self._run_dir(experiment_id, result.run_id)
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save result metadata as JSON
        meta_path = run_dir / "result.json"
        meta = {
            "run_id": result.run_id,
            "status": result.status.value,
            "parameters": result.parameters,
            "metrics": result.metrics,
            "artifacts": {
                k: v for k, v in vars(result.artifacts).items() if v is not None
            },
            "error": result.error,
            "execution_time_ms": result.execution_time_ms,
        }
        meta_path.write_text(json.dumps(meta, indent=2))

    def load_run(self, experiment_id: str, run_id: str) -> Optional[RunResult]:
        """Load run result from file."""
        meta_path = self._run_dir(experiment_id, run_id) / "result.json"
        if not meta_path.exists():
            return None

        meta = json.loads(meta_path.read_text())
        return RunResult(
            run_id=meta["run_id"],
            status=RunStatus(meta["status"]),
            parameters=meta["parameters"],
            metrics=meta["metrics"],
            artifacts=RunArtifacts(**meta.get("artifacts", {})),
            error=meta.get("error"),
            execution_time_ms=meta.get("execution_time_ms"),
        )

    def load_artifact(self, reference: str) -> bytes:
        """Load artifact content by path."""
        path = self.base_dir / reference
        return path.read_bytes()


class FileRegistryStore:
    """Store registry as CSV file (current behavior)."""

    FIELDS = [
        "run_id", "experiment_id", "status", "error",
        # Parameters (extensible)
        "seed", "n_agents", "kappa", "concentration", "mu", "monotonicity",
        "maturity_days", "Q_total", "dealer_enabled",
        # Metrics (extensible)
        "phi_total", "delta_total", "time_to_stability",
        # Artifact paths
        "scenario_yaml", "events_jsonl", "balances_csv", "metrics_csv", "run_html",
    ]

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)

    def _registry_path(self, experiment_id: str) -> Path:
        return self.base_dir / experiment_id / "registry" / "experiments.csv"

    def upsert(self, entry: RegistryEntry) -> None:
        """Insert or update registry entry."""
        registry_path = self._registry_path(entry.experiment_id)
        registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing entries
        entries = {}
        if registry_path.exists():
            with open(registry_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entries[row["run_id"]] = row

        # Build row from entry
        row = {
            "run_id": entry.run_id,
            "experiment_id": entry.experiment_id,
            "status": entry.status.value,
            "error": entry.error or "",
        }
        row.update(entry.parameters)
        row.update(entry.metrics)
        row.update(entry.artifact_paths)

        entries[entry.run_id] = row

        # Write back
        fieldnames = list(self.FIELDS)
        # Add any extra fields from entries
        for r in entries.values():
            for k in r.keys():
                if k not in fieldnames:
                    fieldnames.append(k)

        with open(registry_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in entries.values():
                writer.writerow(r)

    def get(self, experiment_id: str, run_id: str) -> Optional[RegistryEntry]:
        """Get registry entry by ID."""
        registry_path = self._registry_path(experiment_id)
        if not registry_path.exists():
            return None

        with open(registry_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["run_id"] == run_id:
                    return self._row_to_entry(row)
        return None

    def list_runs(self, experiment_id: str) -> List[str]:
        """List all run IDs."""
        registry_path = self._registry_path(experiment_id)
        if not registry_path.exists():
            return []

        with open(registry_path, "r") as f:
            reader = csv.DictReader(f)
            return [row["run_id"] for row in reader]

    def get_completed_keys(self, experiment_id: str) -> set:
        """Get completed parameter keys for resumption."""
        registry_path = self._registry_path(experiment_id)
        if not registry_path.exists():
            return set()

        completed = set()
        with open(registry_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("status") == "completed":
                    # Build key from parameters
                    key = (
                        int(row.get("seed", 0)),
                        float(row.get("kappa", 0)),
                        float(row.get("concentration", 0)),
                    )
                    completed.add(key)
        return completed

    def query(
        self,
        experiment_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RegistryEntry]:
        """Query registry with filters."""
        registry_path = self._registry_path(experiment_id)
        if not registry_path.exists():
            return []

        results = []
        with open(registry_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if filters:
                    match = all(
                        str(row.get(k)) == str(v)
                        for k, v in filters.items()
                    )
                    if not match:
                        continue
                results.append(self._row_to_entry(row))
        return results

    def _row_to_entry(self, row: Dict[str, str]) -> RegistryEntry:
        """Convert CSV row to RegistryEntry."""
        # Separate parameters, metrics, and artifact paths
        param_keys = {"seed", "n_agents", "kappa", "concentration", "mu",
                      "monotonicity", "maturity_days", "Q_total", "dealer_enabled"}
        metric_keys = {"phi_total", "delta_total", "time_to_stability"}
        artifact_keys = {"scenario_yaml", "events_jsonl", "balances_csv",
                        "metrics_csv", "run_html"}

        parameters = {k: row[k] for k in param_keys if k in row and row[k]}
        metrics = {k: row[k] for k in metric_keys if k in row and row[k]}
        artifact_paths = {k: row[k] for k in artifact_keys if k in row and row[k]}

        return RegistryEntry(
            run_id=row["run_id"],
            experiment_id=row.get("experiment_id", ""),
            status=RunStatus(row.get("status", "completed")),
            parameters=parameters,
            metrics=metrics,
            artifact_paths=artifact_paths,
            error=row.get("error") or None,
        )
```

### Part C: Implement LocalExecutor

Create `src/bilancio/runners/local_executor.py`:

```python
"""Local synchronous simulation executor."""

import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from ..storage.models import RunResult, RunArtifacts, RunStatus

class LocalExecutor:
    """Execute simulations locally and synchronously."""

    def execute(
        self,
        scenario_config: Dict[str, Any],
        run_id: str,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> RunResult:
        """Execute simulation, return result."""
        from bilancio.ui.run import run_scenario
        from bilancio.config.loaders import load_yaml
        import tempfile
        import yaml

        start_time = time.time()

        # Create output directory
        if output_dir:
            out_path = Path(output_dir)
        else:
            out_path = Path(tempfile.mkdtemp())
        out_path.mkdir(parents=True, exist_ok=True)

        # Write scenario YAML
        scenario_path = out_path / "scenario.yaml"
        scenario_path.write_text(yaml.dump(scenario_config, default_flow_style=False))

        # Set up export paths
        exports_dir = out_path / "out"
        exports_dir.mkdir(exist_ok=True)

        balances_path = exports_dir / "balances.csv"
        events_path = exports_dir / "events.jsonl"
        metrics_csv_path = exports_dir / "metrics.csv"
        metrics_json_path = exports_dir / "metrics.json"
        run_html_path = out_path / "run.html"

        try:
            # Run simulation
            run_scenario(
                path=scenario_path,
                mode="until_stable",
                max_days=scenario_config.get("run", {}).get("max_days", 90),
                export={
                    "balances_csv": str(balances_path),
                    "events_jsonl": str(events_path),
                },
                html_output=str(run_html_path),
                metrics_csv=str(metrics_csv_path),
                metrics_json=str(metrics_json_path),
                quiet=True,
            )

            # Extract metrics from metrics.json if it exists
            metrics = {}
            if metrics_json_path.exists():
                import json
                metrics_data = json.loads(metrics_json_path.read_text())
                if metrics_data:
                    last = metrics_data[-1] if isinstance(metrics_data, list) else metrics_data
                    metrics = {
                        "phi_total": last.get("phi_total"),
                        "delta_total": last.get("delta_total"),
                        "time_to_stability": last.get("day"),
                    }

            execution_time_ms = int((time.time() - start_time) * 1000)

            return RunResult(
                run_id=run_id,
                status=RunStatus.COMPLETED,
                parameters=self._extract_parameters(scenario_config),
                metrics=metrics,
                artifacts=RunArtifacts(
                    scenario_yaml=str(scenario_path),
                    events_jsonl=str(events_path) if events_path.exists() else None,
                    balances_csv=str(balances_path) if balances_path.exists() else None,
                    metrics_csv=str(metrics_csv_path) if metrics_csv_path.exists() else None,
                    metrics_json=str(metrics_json_path) if metrics_json_path.exists() else None,
                    run_html=str(run_html_path) if run_html_path.exists() else None,
                ),
                execution_time_ms=execution_time_ms,
            )

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return RunResult(
                run_id=run_id,
                status=RunStatus.FAILED,
                parameters=self._extract_parameters(scenario_config),
                metrics={},
                artifacts=RunArtifacts(),
                error=str(e),
                execution_time_ms=execution_time_ms,
            )

    def _extract_parameters(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key parameters from scenario config."""
        params = {}

        # From scenario config
        if "agents" in config:
            params["n_agents"] = len(config["agents"])

        # From run config
        run_cfg = config.get("run", {})
        params["max_days"] = run_cfg.get("max_days", 90)

        # From dealer config
        dealer_cfg = config.get("dealer", {})
        params["dealer_enabled"] = dealer_cfg.get("enabled", False)

        return params
```

### Part D: Create Module Structure

```
src/bilancio/
├── storage/
│   ├── __init__.py          # Re-exports
│   ├── models.py            # RunResult, RegistryEntry, etc.
│   ├── protocols.py         # ResultStore, RegistryStore protocols
│   └── file_store.py        # FileResultStore, FileRegistryStore
│
└── runners/
    ├── __init__.py          # Re-exports
    ├── protocols.py         # SimulationExecutor, JobExecutor protocols
    └── local_executor.py    # LocalExecutor implementation
```

### Part E: Add Tests

Create `tests/storage/test_file_store.py`:
- Test FileResultStore save/load artifacts
- Test FileResultStore save/load runs
- Test FileRegistryStore upsert/query
- Test resumption with get_completed_keys

Create `tests/runners/test_local_executor.py`:
- Test LocalExecutor with simple scenario
- Test error handling for failed simulations
- Test parameter extraction

### Part F: Integration (Future)

In a follow-up PR, refactor `RingSweepRunner` to optionally use the new abstractions:

```python
class RingSweepRunner:
    def __init__(
        self,
        config: RingSweepConfig,
        executor: Optional[SimulationExecutor] = None,
        result_store: Optional[ResultStore] = None,
        registry_store: Optional[RegistryStore] = None,
    ):
        self.config = config
        self.executor = executor or LocalExecutor()
        self.result_store = result_store
        self.registry_store = registry_store
        # ... existing init
```

This allows gradual adoption - existing code continues to work, new code can inject dependencies.

---

## File Changes Summary

**New files:**
- `src/bilancio/storage/__init__.py`
- `src/bilancio/storage/models.py`
- `src/bilancio/storage/protocols.py`
- `src/bilancio/storage/file_store.py`
- `src/bilancio/runners/__init__.py`
- `src/bilancio/runners/protocols.py`
- `src/bilancio/runners/local_executor.py`
- `tests/storage/__init__.py`
- `tests/storage/test_file_store.py`
- `tests/runners/__init__.py`
- `tests/runners/test_local_executor.py`

**No existing files modified** - this is purely additive.

---

## Success Criteria

1. All new code has tests with >80% coverage
2. Existing tests still pass (no regressions)
3. Can store/retrieve run results via FileResultStore
4. Can execute simulations via LocalExecutor
5. Registry operations (upsert, query, resume) work correctly

---

## Future Extensions (Out of Scope)

- `DatabaseResultStore` - PostgreSQL/SQLite implementation
- `S3ResultStore` - AWS S3 blob storage
- `CloudExecutor` - AWS Batch / GCP Cloud Run
- Refactoring existing runners to use abstractions
- API layer for remote access

These will be separate plans once the foundation is in place.
