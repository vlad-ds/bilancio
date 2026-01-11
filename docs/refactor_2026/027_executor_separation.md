# Plan 027: Executor Separation of Concerns

**Date:** January 2026
**Status:** Implemented ✅
**Depends on:** Plan 026 (Phase 4 abstractions)

## Implementation Summary

Implemented January 2026. Key changes:

- **`RunOptions`** and **`ExecutionResult`** dataclasses in `src/bilancio/runners/models.py`
- **`ArtifactLoader`** protocol and **`LocalArtifactLoader`** in `src/bilancio/storage/artifact_loaders.py`
- **`MetricsComputer`** class in `src/bilancio/analysis/metrics_computer.py`
- **`LocalExecutor`** refactored to only run simulation (no metrics computation)
- **`RingSweepRunner`** updated to use executor + MetricsComputer pattern

All 527 tests pass. Verified with control/treatment sweeps.

---

## Problem Statement

The current `LocalExecutor` conflates two concerns:
1. **Execution** - Running the simulation (heavy compute)
2. **Metrics computation** - Computing derived metrics from raw outputs

For cloud execution to work cleanly, we need clear separation:
- **Executor**: Runs simulation, returns raw outputs, reports where results are stored
- **Runner**: Computes metrics locally from raw outputs

---

## Design Principles

1. **Executor is swappable** - LocalExecutor and CloudExecutor should be interchangeable
2. **Executor reports storage location** - Results may be local files or cloud storage (S3, GCS)
3. **Metrics computation is always local** - Happens in the runner after fetching raw outputs
4. **Raw outputs are the contract** - `events.jsonl`, `balances.csv`, `run.html`, `dealer_metrics.json`

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  RingSweepRunner                                                │
│  ┌───────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │ Generate      │ -> │ Executor     │ -> │ Compute Metrics │  │
│  │ Scenario      │    │ .execute()   │    │ (local)         │  │
│  └───────────────┘    └──────────────┘    └─────────────────┘  │
│                              │                     │            │
│                              v                     v            │
│                       ExecutionResult        RegistryStore      │
│                       (paths/URIs)           .upsert()          │
└─────────────────────────────────────────────────────────────────┘

Executor implementations:
┌─────────────────────┐    ┌─────────────────────┐
│ LocalExecutor       │    │ CloudExecutor       │
│ - Runs in-process   │    │ - Submits to worker │
│ - Files on disk     │    │ - Results in S3/GCS │
│ - storage: "local"  │    │ - storage: "s3://…" │
└─────────────────────┘    └─────────────────────┘
```

---

## Data Models

### RunOptions

Configuration for `run_scenario()` that the executor passes through:

```python
@dataclass
class RunOptions:
    """Options passed to run_scenario()."""
    mode: str = "until_stable"
    max_days: int = 90
    quiet_days: int = 2
    check_invariants: str = "daily"
    default_handling: str = "fail-fast"

    # Display options (for HTML report)
    show_events: str = "detailed"
    show_balances: Optional[List[str]] = None
    t_account: bool = False

    # Dealer options
    detailed_dealer_logging: bool = False
    run_id: Optional[str] = None
    regime: Optional[str] = None
```

### ExecutionResult

What the executor returns:

```python
@dataclass
class ExecutionResult:
    """Result of simulation execution."""
    run_id: str
    status: RunStatus  # COMPLETED, FAILED

    # Storage location
    storage_type: str  # "local", "s3", "gcs"
    storage_base: str  # "/path/to/run" or "s3://bucket/prefix"

    # Artifact references (relative to storage_base)
    artifacts: Dict[str, str]  # {"events_jsonl": "out/events.jsonl", ...}

    # Error info if failed
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
```

### ArtifactLoader Protocol

For fetching artifacts regardless of storage location:

```python
class ArtifactLoader(Protocol):
    """Load artifacts from any storage backend."""

    def load_bytes(self, reference: str) -> bytes:
        """Load artifact as bytes."""
        ...

    def load_text(self, reference: str) -> str:
        """Load artifact as text."""
        ...

    def exists(self, reference: str) -> bool:
        """Check if artifact exists."""
        ...


class LocalArtifactLoader:
    """Load artifacts from local filesystem."""

    def __init__(self, base_path: Path):
        self.base_path = base_path


class S3ArtifactLoader:
    """Load artifacts from S3 (future)."""

    def __init__(self, bucket: str, prefix: str):
        self.bucket = bucket
        self.prefix = prefix
```

---

## Implementation Plan

### Part A: Simplify LocalExecutor

Remove metrics computation from `LocalExecutor`. It should only:
1. Write scenario YAML
2. Call `run_scenario()` with provided options
3. Return `ExecutionResult` with artifact paths

```python
class LocalExecutor:
    def execute(
        self,
        scenario_config: Dict[str, Any],
        run_id: str,
        output_dir: Path,
        options: RunOptions,
    ) -> ExecutionResult:
        # Write scenario
        scenario_path = output_dir / "scenario.yaml"
        scenario_path.write_text(yaml.dump(scenario_config))

        # Run simulation
        run_scenario(
            path=scenario_path,
            mode=options.mode,
            max_days=options.max_days,
            quiet_days=options.quiet_days,
            # ... all options
            export={
                "balances_csv": str(output_dir / "out/balances.csv"),
                "events_jsonl": str(output_dir / "out/events.jsonl"),
            },
            html_output=output_dir / "run.html",
        )

        # Return result (NO metrics computation)
        return ExecutionResult(
            run_id=run_id,
            status=RunStatus.COMPLETED,
            storage_type="local",
            storage_base=str(output_dir),
            artifacts={
                "scenario_yaml": "scenario.yaml",
                "events_jsonl": "out/events.jsonl",
                "balances_csv": "out/balances.csv",
                "run_html": "run.html",
                "dealer_metrics_json": "out/dealer_metrics.json",
            },
        )
```

### Part B: Create MetricsComputer

Extract metrics computation into a separate class:

```python
class MetricsComputer:
    """Compute derived metrics from raw simulation outputs."""

    def __init__(self, artifact_loader: ArtifactLoader):
        self.loader = artifact_loader

    def compute(self, artifacts: Dict[str, str]) -> MetricsBundle:
        """Compute all metrics from artifacts."""
        # Load raw data
        events = self._load_events(artifacts["events_jsonl"])
        balances = self._load_balances(artifacts.get("balances_csv"))

        # Compute metrics
        bundle = compute_day_metrics(events, balances)

        return MetricsBundle(
            day_metrics=bundle["day_metrics"],
            debtor_shares=bundle["debtor_shares"],
            intraday=bundle["intraday"],
            summary=summarize_day_metrics(bundle["day_metrics"]),
        )

    def write_outputs(
        self,
        bundle: MetricsBundle,
        output_dir: Path,
    ) -> Dict[str, Path]:
        """Write computed metrics to files."""
        paths = {}
        paths["metrics_csv"] = output_dir / "metrics.csv"
        write_day_metrics_csv(paths["metrics_csv"], bundle.day_metrics)
        # ... etc
        return paths
```

### Part C: Refactor RingSweepRunner

Update `_execute_run()` to use the executor and metrics computer:

```python
def _execute_run(self, ...) -> RingRunSummary:
    # 1. Generate scenario config (unchanged)
    scenario = self._generate_scenario(kappa, concentration, ...)

    # 2. Execute simulation via executor
    run_options = RunOptions(
        max_days=scenario["run"].get("max_days", 90),
        quiet_days=scenario["run"].get("quiet_days", 2),
        default_handling=self.default_handling,
        detailed_dealer_logging=self.detailed_dealer_logging,
        run_id=run_id,
        regime="active" if self.dealer_enabled else "passive",
    )

    result = self.executor.execute(
        scenario_config=scenario,
        run_id=run_id,
        output_dir=run_dir,
        options=run_options,
    )

    if result.status == RunStatus.FAILED:
        # Handle failure...
        return RingRunSummary(...)

    # 3. Compute metrics locally
    loader = LocalArtifactLoader(Path(result.storage_base))
    computer = MetricsComputer(loader)
    metrics = computer.compute(result.artifacts)
    computer.write_outputs(metrics, run_dir / "out")

    # 4. Update registry (unchanged)
    self._upsert_registry(...)

    return RingRunSummary(...)
```

### Part D: Update Tests

1. Update `LocalExecutor` tests to verify it does NOT compute metrics
2. Add tests for `MetricsComputer`
3. Update `RingSweepRunner` tests to verify integration

---

## File Changes

**Modified:**
- `src/bilancio/runners/local_executor.py` - Simplify, add RunOptions
- `src/bilancio/runners/protocols.py` - Update protocol with new signature
- `src/bilancio/experiments/ring.py` - Use executor + metrics computer
- `tests/runners/test_local_executor.py` - Update tests

**New:**
- `src/bilancio/runners/models.py` - RunOptions, ExecutionResult
- `src/bilancio/analysis/metrics_computer.py` - MetricsComputer class
- `src/bilancio/storage/artifact_loaders.py` - ArtifactLoader protocol + LocalArtifactLoader
- `tests/analysis/test_metrics_computer.py`

---

## Future: CloudExecutor

With this separation, `CloudExecutor` becomes straightforward:

```python
class CloudExecutor:
    def __init__(self, api_endpoint: str, storage_bucket: str):
        self.api = api_endpoint
        self.bucket = storage_bucket

    def execute(
        self,
        scenario_config: Dict[str, Any],
        run_id: str,
        output_dir: Path,  # Ignored for cloud
        options: RunOptions,
    ) -> ExecutionResult:
        # 1. Upload scenario to cloud storage
        # 2. Submit job to cloud worker
        # 3. Wait for completion (or return job_id for async)
        # 4. Return ExecutionResult with S3 paths

        return ExecutionResult(
            run_id=run_id,
            status=RunStatus.COMPLETED,
            storage_type="s3",
            storage_base=f"s3://{self.bucket}/runs/{run_id}",
            artifacts={...},
        )
```

The runner doesn't change - it just uses `S3ArtifactLoader` instead of `LocalArtifactLoader` to fetch results for metrics computation.

---

## Success Criteria

1. `LocalExecutor` only runs simulation, returns artifact paths
2. Metrics computation extracted to `MetricsComputer`
3. `RingSweepRunner` works with refactored components
4. All existing tests pass
5. Integration test: run sweep, verify metrics computed correctly
6. Clear path for `CloudExecutor` implementation

---

## Out of Scope

- Actual `CloudExecutor` implementation (separate plan)
- `S3ArtifactLoader` implementation (separate plan)
- Async/job-based execution (separate plan)
