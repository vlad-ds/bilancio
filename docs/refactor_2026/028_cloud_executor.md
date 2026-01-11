# Plan 028: Cloud Executor with Modal

**Date:** January 2026
**Branch:** `feature/cloud-executor`
**Depends on:** Plan 026 (storage abstractions), Plan 027 (executor separation)
**Risk Level:** Medium
**Estimated Effort:** 3-4 days

---

## Overview

Implement a `CloudExecutor` that runs bilancio simulations on Modal's serverless cloud infrastructure. This enables:
- Parallel execution of large parameter sweeps (100s-1000s of runs)
- Execution without tying up local machine
- Potential GPU acceleration for future ML-based analysis
- Reproducible cloud environments

---

## Prerequisites

### Modal Setup (Completed)
- [x] Modal dependency added: `modal>=1.3.0.post1`
- [x] Authentication: `python -m modal setup`
- [x] Credentials stored in `~/.modal.toml`
- [x] `.modal.toml` added to `.gitignore`

### Abstraction Layer (Completed - Plans 026/027)
- [x] `SimulationExecutor` protocol in `runners/protocols.py`
- [x] `ExecutionResult` dataclass in `runners/models.py`
- [x] `RunOptions` dataclass in `runners/models.py`
- [x] `LocalExecutor` reference implementation
- [x] `ArtifactLoader` protocol for retrieving results

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  RingSweepRunner / ComparisonSweepRunner                                │
│  ↓                                                                      │
│  executor.execute(scenario, run_id, output_dir, options)                │
│  ↓                                                                      │
│  ┌────────────────────┐  OR  ┌────────────────────────────────────────┐ │
│  │ LocalExecutor      │      │ CloudExecutor                          │ │
│  │ - In-process       │      │ - Submits to Modal                     │ │
│  │ - Files on disk    │      │ - Waits for completion                 │ │
│  │ - Immediate result │      │ - Downloads artifacts to local disk    │ │
│  └────────────────────┘      └────────────────────────────────────────┘ │
│                                        ↓                                │
│                              ┌─────────────────────────┐                │
│                              │ Modal Cloud             │                │
│                              │ ┌─────────────────────┐ │                │
│                              │ │ run_simulation()    │ │                │
│                              │ │ - Runs in container │ │                │
│                              │ │ - Saves to Volume   │ │                │
│                              │ └─────────────────────┘ │                │
│                              │ ┌─────────────────────┐ │                │
│                              │ │ Modal Volume        │ │                │
│                              │ │ - events.jsonl      │ │                │
│                              │ │ - balances.csv      │ │                │
│                              │ │ - run.html          │ │                │
│                              │ └─────────────────────┘ │                │
│                              └─────────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Part A: Modal App Definition

Create `src/bilancio/cloud/__init__.py` and `src/bilancio/cloud/modal_app.py`:

```python
# src/bilancio/cloud/modal_app.py
"""Modal app definition for cloud simulation execution."""

import modal

# Define the Modal app
app = modal.App("bilancio-simulations")

# Create a persistent volume for storing results
# Results persist across function invocations
results_volume = modal.Volume.from_name(
    "bilancio-results",
    create_if_missing=True
)

# Define the container image with all bilancio dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scipy>=1.10.0",
        "pydantic>=2.0.0",
        "networkx>=3.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
    )
    # Install bilancio from the current source
    .pip_install_from_pyproject(".")
)

# Alternative: Install from PyPI (once published)
# image = modal.Image.debian_slim().pip_install("bilancio>=0.1.0")
```

### Part B: Remote Simulation Function

```python
# src/bilancio/cloud/modal_app.py (continued)

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

RESULTS_MOUNT_PATH = "/results"

@app.function(
    image=image,
    volumes={RESULTS_MOUNT_PATH: results_volume},
    timeout=600,  # 10 minutes max per simulation
    retries=modal.Retries(max_retries=2, backoff_coefficient=2.0),
    memory=2048,  # 2GB RAM
)
def run_simulation(
    scenario_config: Dict[str, Any],
    run_id: str,
    experiment_id: str,
    options: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run a single simulation in the cloud.

    Args:
        scenario_config: Full scenario YAML as dict
        run_id: Unique identifier for this run
        experiment_id: Groups related runs together
        options: RunOptions as dict (mode, max_days, quiet_days, etc.)

    Returns:
        Dict with status, artifact paths (relative to volume), metrics, error
    """
    import time
    from pathlib import Path

    start_time = time.time()

    # Create output directory on the volume
    run_dir = Path(RESULTS_MOUNT_PATH) / experiment_id / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    out_dir = run_dir / "out"
    out_dir.mkdir(exist_ok=True)

    # Write scenario YAML
    scenario_path = run_dir / "scenario.yaml"
    scenario_path.write_text(yaml.dump(scenario_config, default_flow_style=False))

    try:
        # Import bilancio inside the function (container context)
        from bilancio.ui.run import run_scenario

        # Execute simulation
        run_scenario(
            path=scenario_path,
            mode=options.get("mode", "until_stable"),
            max_days=options.get("max_days", 90),
            quiet_days=options.get("quiet_days", 2),
            check_invariants=options.get("check_invariants", "daily"),
            default_handling=options.get("default_handling", "fail-fast"),
            export={
                "balances_csv": str(out_dir / "balances.csv"),
                "events_jsonl": str(out_dir / "events.jsonl"),
            },
            html_output=str(run_dir / "run.html"),
            metrics_csv=str(out_dir / "metrics.csv"),
            metrics_json=str(out_dir / "metrics.json"),
            quiet=True,
        )

        # Commit changes to volume
        results_volume.commit()

        execution_time_ms = int((time.time() - start_time) * 1000)

        return {
            "run_id": run_id,
            "status": "completed",
            "storage_type": "modal_volume",
            "storage_base": f"{experiment_id}/runs/{run_id}",
            "artifacts": {
                "scenario_yaml": "scenario.yaml",
                "events_jsonl": "out/events.jsonl",
                "balances_csv": "out/balances.csv",
                "metrics_csv": "out/metrics.csv",
                "metrics_json": "out/metrics.json",
                "run_html": "run.html",
            },
            "execution_time_ms": execution_time_ms,
            "error": None,
        }

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Still commit to preserve any partial output
        results_volume.commit()

        return {
            "run_id": run_id,
            "status": "failed",
            "storage_type": "modal_volume",
            "storage_base": f"{experiment_id}/runs/{run_id}",
            "artifacts": {},
            "execution_time_ms": execution_time_ms,
            "error": str(e),
        }
```

### Part C: CloudExecutor Class

```python
# src/bilancio/runners/cloud_executor.py
"""Cloud executor using Modal for remote simulation execution."""

from pathlib import Path
from typing import Dict, Any, Optional
import json

from .models import RunOptions, ExecutionResult
from ..storage.models import RunStatus


class CloudExecutor:
    """
    Execute simulations on Modal cloud infrastructure.

    Results are stored on a Modal Volume and downloaded to local disk
    after execution completes.
    """

    def __init__(
        self,
        experiment_id: str,
        download_artifacts: bool = True,
        local_output_dir: Optional[Path] = None,
    ):
        """
        Initialize cloud executor.

        Args:
            experiment_id: Identifier for this experiment (groups runs)
            download_artifacts: Whether to download results to local disk
            local_output_dir: Where to download artifacts (default: out/experiments/{experiment_id})
        """
        self.experiment_id = experiment_id
        self.download_artifacts = download_artifacts
        self.local_output_dir = local_output_dir or Path(f"out/experiments/{experiment_id}")

        # Import Modal components (lazy import to avoid issues when Modal not configured)
        from bilancio.cloud.modal_app import run_simulation, results_volume
        self._run_simulation = run_simulation
        self._results_volume = results_volume

    def execute(
        self,
        scenario_config: Dict[str, Any],
        run_id: str,
        output_dir: Path,
        options: RunOptions,
    ) -> ExecutionResult:
        """
        Execute simulation on Modal cloud.

        Args:
            scenario_config: Full scenario configuration
            run_id: Unique run identifier
            output_dir: Local directory for results (used if download_artifacts=True)
            options: Simulation run options

        Returns:
            ExecutionResult with status and artifact references
        """
        # Convert options to dict for serialization
        options_dict = {
            "mode": options.mode,
            "max_days": options.max_days,
            "quiet_days": options.quiet_days,
            "check_invariants": options.check_invariants,
            "default_handling": options.default_handling,
            "show_events": options.show_events,
            "t_account": options.t_account,
            "detailed_dealer_logging": options.detailed_dealer_logging,
        }

        # Execute remotely (blocks until complete)
        result = self._run_simulation.remote(
            scenario_config=scenario_config,
            run_id=run_id,
            experiment_id=self.experiment_id,
            options=options_dict,
        )

        # Download artifacts if requested
        if self.download_artifacts and result["status"] == "completed":
            self._download_run_artifacts(run_id, output_dir, result["artifacts"])

        return ExecutionResult(
            run_id=result["run_id"],
            status=RunStatus.COMPLETED if result["status"] == "completed" else RunStatus.FAILED,
            storage_type=result["storage_type"],
            storage_base=result["storage_base"],
            artifacts=result["artifacts"],
            error=result.get("error"),
            execution_time_ms=result.get("execution_time_ms"),
        )

    def _download_run_artifacts(
        self,
        run_id: str,
        output_dir: Path,
        artifacts: Dict[str, str],
    ) -> None:
        """Download artifacts from Modal Volume to local disk."""
        import subprocess

        output_dir.mkdir(parents=True, exist_ok=True)
        out_subdir = output_dir / "out"
        out_subdir.mkdir(exist_ok=True)

        remote_base = f"{self.experiment_id}/runs/{run_id}"

        for artifact_name, artifact_path in artifacts.items():
            remote_path = f"{remote_base}/{artifact_path}"

            if artifact_path.startswith("out/"):
                local_path = output_dir / artifact_path
            else:
                local_path = output_dir / artifact_path

            # Use Modal CLI to download
            subprocess.run(
                ["modal", "volume", "get", "bilancio-results", remote_path, str(local_path)],
                check=True,
                capture_output=True,
            )
```

### Part D: Batch/Parallel Execution

For large sweeps, execute multiple simulations in parallel:

```python
# src/bilancio/runners/cloud_executor.py (continued)

from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


class CloudExecutor:
    # ... previous methods ...

    def execute_batch(
        self,
        runs: List[Tuple[Dict[str, Any], str, RunOptions]],  # (config, run_id, options)
        max_parallel: int = 50,
        progress_callback: Optional[callable] = None,
    ) -> List[ExecutionResult]:
        """
        Execute multiple simulations in parallel on Modal.

        Modal automatically handles parallelization, but this method
        provides a convenient interface for batch execution.

        Args:
            runs: List of (scenario_config, run_id, options) tuples
            max_parallel: Maximum concurrent Modal function calls
            progress_callback: Called with (completed, total) after each completion

        Returns:
            List of ExecutionResult in same order as input
        """
        from bilancio.cloud.modal_app import run_simulation

        total = len(runs)
        results = [None] * total

        # Submit all jobs to Modal (Modal handles queuing)
        futures = []
        for idx, (config, run_id, options) in enumerate(runs):
            options_dict = self._options_to_dict(options)

            # .spawn() returns a FunctionCall that we can await later
            future = run_simulation.spawn(
                scenario_config=config,
                run_id=run_id,
                experiment_id=self.experiment_id,
                options=options_dict,
            )
            futures.append((idx, run_id, future))

        # Collect results as they complete
        completed = 0
        for idx, run_id, future in futures:
            result = future.get()  # Blocks until this specific run completes

            results[idx] = ExecutionResult(
                run_id=result["run_id"],
                status=RunStatus.COMPLETED if result["status"] == "completed" else RunStatus.FAILED,
                storage_type=result["storage_type"],
                storage_base=result["storage_base"],
                artifacts=result["artifacts"],
                error=result.get("error"),
                execution_time_ms=result.get("execution_time_ms"),
            )

            completed += 1
            if progress_callback:
                progress_callback(completed, total)

        return results

    def _options_to_dict(self, options: RunOptions) -> Dict[str, Any]:
        """Convert RunOptions to serializable dict."""
        return {
            "mode": options.mode,
            "max_days": options.max_days,
            "quiet_days": options.quiet_days,
            "check_invariants": options.check_invariants,
            "default_handling": options.default_handling,
            "show_events": options.show_events,
            "t_account": options.t_account,
            "detailed_dealer_logging": options.detailed_dealer_logging,
        }
```

### Part E: Modal Volume Artifact Loader

```python
# src/bilancio/storage/modal_artifact_loader.py
"""Artifact loader for Modal Volume storage."""

from pathlib import Path
from typing import Optional
import subprocess
import tempfile

from .artifact_loaders import ArtifactLoader


class ModalVolumeArtifactLoader:
    """
    Load artifacts from a Modal Volume.

    Uses the Modal CLI to download files on demand.
    Implements caching to avoid repeated downloads.
    """

    def __init__(
        self,
        volume_name: str = "bilancio-results",
        base_path: str = "",
        cache_dir: Optional[Path] = None,
    ):
        """
        Initialize loader.

        Args:
            volume_name: Name of the Modal Volume
            base_path: Base path within the volume (e.g., "experiment_001/runs/run_001")
            cache_dir: Local directory for caching downloads
        """
        self.volume_name = volume_name
        self.base_path = base_path
        self.cache_dir = cache_dir or Path(tempfile.mkdtemp(prefix="modal_cache_"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_bytes(self, reference: str) -> bytes:
        """Load artifact as bytes."""
        local_path = self._ensure_downloaded(reference)
        return local_path.read_bytes()

    def load_text(self, reference: str) -> str:
        """Load artifact as text."""
        local_path = self._ensure_downloaded(reference)
        return local_path.read_text()

    def exists(self, reference: str) -> bool:
        """Check if artifact exists on volume."""
        remote_path = f"{self.base_path}/{reference}" if self.base_path else reference

        result = subprocess.run(
            ["modal", "volume", "ls", self.volume_name, remote_path],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _ensure_downloaded(self, reference: str) -> Path:
        """Download artifact if not already cached."""
        # Create cache path maintaining directory structure
        cache_path = self.cache_dir / reference

        if cache_path.exists():
            return cache_path

        # Ensure parent directory exists
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Download from Modal Volume
        remote_path = f"{self.base_path}/{reference}" if self.base_path else reference

        subprocess.run(
            ["modal", "volume", "get", self.volume_name, remote_path, str(cache_path)],
            check=True,
            capture_output=True,
        )

        return cache_path
```

### Part F: CLI Integration

Add `--cloud` flag to sweep commands:

```python
# src/bilancio/ui/cli/sweep.py (modifications)

@sweep.command("ring")
@click.option("--cloud", is_flag=True, help="Run simulations on Modal cloud")
@click.option("--cloud-parallel", type=int, default=50, help="Max parallel cloud runs")
# ... existing options ...
def sweep_ring(cloud: bool, cloud_parallel: int, ...):
    """Run ring topology parameter sweep."""

    if cloud:
        from bilancio.runners.cloud_executor import CloudExecutor
        executor = CloudExecutor(
            experiment_id=experiment_name,
            download_artifacts=True,
            local_output_dir=output_dir,
        )
    else:
        from bilancio.runners.local_executor import LocalExecutor
        executor = LocalExecutor()

    runner = RingSweepRunner(
        config=sweep_config,
        executor=executor,
        # ... other params
    )

    runner.run_sweep()
```

### Part G: Update RingSweepRunner for Executor Injection

```python
# src/bilancio/experiments/ring.py (modifications)

from bilancio.runners.protocols import SimulationExecutor
from bilancio.runners.local_executor import LocalExecutor


class RingSweepRunner:
    def __init__(
        self,
        config: RingSweepConfig,
        executor: Optional[SimulationExecutor] = None,
        # ... existing params
    ):
        self.config = config
        self.executor = executor or LocalExecutor()
        # ... rest of init

    def _execute_run(self, ...) -> RingRunSummary:
        # Use injected executor instead of calling run_scenario directly
        result = self.executor.execute(
            scenario_config=scenario,
            run_id=run_id,
            output_dir=run_dir,
            options=run_options,
        )

        if result.status == RunStatus.FAILED:
            return self._handle_failed_run(result)

        # Compute metrics locally (executor only returns raw outputs)
        loader = self._get_artifact_loader(result)
        computer = MetricsComputer(loader)
        metrics = computer.compute(result.artifacts)

        # ... rest of processing
```

---

## Part H: Cloud-to-Cloud Deployment

### Token Authentication

Modal supports two authentication methods:
1. **Local file:** `~/.modal.toml` (created by `modal setup`)
2. **Environment variables:** `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`

Environment variables take precedence, making it possible to trigger Modal jobs from any cloud environment.

### Deployment Scenarios

#### Scenario 1: Local Development
```
┌──────────────────┐         ┌─────────────────┐
│ Developer Laptop │ ──────► │ Modal Cloud     │
│ ~/.modal.toml    │         │ (runs sims)     │
└──────────────────┘         └─────────────────┘
```

#### Scenario 2: Cloud Orchestrator (Recommended for Large Sweeps)
```
┌──────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Cloud VM / CI    │ ──────► │ Modal Cloud     │ ──────► │ Modal Volume    │
│ (orchestrator)   │         │ (runs 100s of   │         │ (stores results)│
│ env: TOKEN_ID,   │         │  simulations)   │         │                 │
│      TOKEN_SECRET│         └─────────────────┘         └─────────────────┘
└──────────────────┘                                              │
         │                                                        │
         └────────────────────────────────────────────────────────┘
                          Download results when done
```

**Why use a cloud orchestrator?**
- Long-running sweeps don't tie up your laptop
- Can run overnight / over weekends
- Cheaper VM (just orchestrating) + Modal (actual compute)
- Better reliability (won't fail if laptop sleeps)

### Setting Up Cloud Orchestrator

#### Option A: GitHub Actions

```yaml
# .github/workflows/sweep.yml
name: Run Parameter Sweep

on:
  workflow_dispatch:
    inputs:
      config_file:
        description: 'Sweep configuration file'
        required: true
        default: 'sweeps/large_sweep.yaml'

jobs:
  sweep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .

      - name: Run sweep on Modal
        env:
          MODAL_TOKEN_ID: ${{ secrets.MODAL_TOKEN_ID }}
          MODAL_TOKEN_SECRET: ${{ secrets.MODAL_TOKEN_SECRET }}
        run: |
          python -m bilancio sweep ring \
            --config ${{ inputs.config_file }} \
            --cloud \
            --cloud-parallel 100

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: sweep-results
          path: out/experiments/
```

**Setup:**
1. Go to repo Settings → Secrets → Actions
2. Add `MODAL_TOKEN_ID` = your token ID from `~/.modal.toml`
3. Add `MODAL_TOKEN_SECRET` = your token secret from `~/.modal.toml`

#### Option B: Cheap Cloud VM (EC2, GCP, DigitalOcean)

```bash
# On a $5/month VM:

# 1. Clone repo
git clone https://github.com/vlad-ds/bilancio.git
cd bilancio

# 2. Install
pip install -e .

# 3. Set Modal credentials
export MODAL_TOKEN_ID=ak-xxxxx
export MODAL_TOKEN_SECRET=as-xxxxx

# 4. Run sweep (VM just orchestrates, Modal does compute)
nohup python -m bilancio sweep ring \
  --config sweeps/large_sweep.yaml \
  --cloud \
  --cloud-parallel 100 \
  > sweep.log 2>&1 &

# 5. Check progress
tail -f sweep.log
```

#### Option C: Modal Secrets (Most Secure)

Store external API keys in Modal Secrets for the simulation functions:

```python
# If simulations need external APIs (e.g., data feeds)
from modal import Secret

@app.function(
    image=image,
    secrets=[Secret.from_name("external-api-keys")],
)
def run_simulation(...):
    import os
    api_key = os.environ["EXTERNAL_API_KEY"]  # Injected by Modal
    ...
```

### Creating a Separate Token for Cloud Use

For security, create a separate Modal token for cloud environments:

```bash
# On your local machine:
modal token new --name "cloud-orchestrator"

# This creates a new token you can use in cloud environments
# without exposing your personal development token
```

### Environment Variables

```bash
# .env (gitignored)
# Modal uses ~/.modal.toml for auth, but can override:
MODAL_TOKEN_ID=ak-xxxxx
MODAL_TOKEN_SECRET=as-xxxxx

# Optional: Custom volume name
BILANCIO_MODAL_VOLUME=bilancio-results

# Optional: Default cloud settings
BILANCIO_CLOUD_TIMEOUT=600
BILANCIO_CLOUD_MEMORY=2048
BILANCIO_CLOUD_MAX_PARALLEL=50
```

### Config Dataclass

```python
# src/bilancio/cloud/config.py
from dataclasses import dataclass, field
from typing import Optional
import os


@dataclass
class CloudConfig:
    """Configuration for cloud execution."""

    volume_name: str = field(
        default_factory=lambda: os.getenv("BILANCIO_MODAL_VOLUME", "bilancio-results")
    )
    timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("BILANCIO_CLOUD_TIMEOUT", "600"))
    )
    memory_mb: int = field(
        default_factory=lambda: int(os.getenv("BILANCIO_CLOUD_MEMORY", "2048"))
    )
    max_parallel: int = field(
        default_factory=lambda: int(os.getenv("BILANCIO_CLOUD_MAX_PARALLEL", "50"))
    )

    # GPU configuration (for future ML workloads)
    gpu: Optional[str] = None  # e.g., "T4", "A10G", "A100"
```

---

## Part I: Testing

### Unit Tests

```python
# tests/cloud/test_cloud_executor.py
import pytest
from unittest.mock import Mock, patch

from bilancio.runners.cloud_executor import CloudExecutor
from bilancio.runners.models import RunOptions, ExecutionResult
from bilancio.storage.models import RunStatus


class TestCloudExecutor:
    """Unit tests for CloudExecutor (mocked Modal)."""

    @patch("bilancio.cloud.modal_app.run_simulation")
    def test_execute_success(self, mock_run_simulation):
        """Test successful cloud execution."""
        mock_run_simulation.remote.return_value = {
            "run_id": "test_001",
            "status": "completed",
            "storage_type": "modal_volume",
            "storage_base": "exp/runs/test_001",
            "artifacts": {"events_jsonl": "out/events.jsonl"},
            "execution_time_ms": 5000,
            "error": None,
        }

        executor = CloudExecutor(experiment_id="exp", download_artifacts=False)
        result = executor.execute(
            scenario_config={"agents": []},
            run_id="test_001",
            output_dir=Path("/tmp/test"),
            options=RunOptions(),
        )

        assert result.status == RunStatus.COMPLETED
        assert result.run_id == "test_001"

    @patch("bilancio.cloud.modal_app.run_simulation")
    def test_execute_failure(self, mock_run_simulation):
        """Test failed cloud execution."""
        mock_run_simulation.remote.return_value = {
            "run_id": "test_001",
            "status": "failed",
            "storage_type": "modal_volume",
            "storage_base": "exp/runs/test_001",
            "artifacts": {},
            "execution_time_ms": 1000,
            "error": "Simulation diverged",
        }

        executor = CloudExecutor(experiment_id="exp", download_artifacts=False)
        result = executor.execute(...)

        assert result.status == RunStatus.FAILED
        assert result.error == "Simulation diverged"
```

### Integration Tests (requires Modal auth)

```python
# tests/cloud/test_cloud_integration.py
import pytest
from pathlib import Path

from bilancio.runners.cloud_executor import CloudExecutor
from bilancio.runners.models import RunOptions


@pytest.mark.slow
@pytest.mark.cloud
class TestCloudIntegration:
    """Integration tests that run actual Modal functions."""

    def test_simple_scenario_cloud(self, tmp_path):
        """Run a simple scenario on Modal cloud."""
        scenario = {
            "agents": [
                {"id": "bank", "type": "Bank"},
                {"id": "alice", "type": "Household"},
            ],
            "setup": [
                {"op": "open_account", "agent": "alice", "at": "bank", "balance": 1000},
            ],
            "run": {"max_days": 5},
        }

        executor = CloudExecutor(
            experiment_id="test_integration",
            download_artifacts=True,
            local_output_dir=tmp_path,
        )

        result = executor.execute(
            scenario_config=scenario,
            run_id="integration_test_001",
            output_dir=tmp_path / "run_001",
            options=RunOptions(max_days=5),
        )

        assert result.status == RunStatus.COMPLETED
        assert (tmp_path / "run_001" / "out" / "events.jsonl").exists()
```

---

## Part J: Monitoring and Cost Management

### Usage Tracking

```python
# src/bilancio/cloud/usage.py
"""Track Modal usage and costs."""

import modal
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class UsageRecord:
    """Record of a Modal function execution."""
    run_id: str
    function_name: str
    started_at: datetime
    ended_at: datetime
    duration_seconds: float
    memory_mb: int
    gpu: Optional[str]
    cost_estimate_usd: float


def get_recent_usage(limit: int = 100) -> List[UsageRecord]:
    """Get recent Modal usage for cost tracking."""
    # Modal provides usage APIs - implementation depends on Modal SDK version
    pass


def estimate_sweep_cost(
    num_runs: int,
    avg_duration_seconds: float = 30,
    memory_mb: int = 2048,
    gpu: Optional[str] = None,
) -> float:
    """Estimate cost of a parameter sweep."""
    # Modal pricing (as of 2026):
    # - CPU: $0.000014/second per vCPU
    # - Memory: $0.000001/second per MB
    # - GPU: varies by type

    cpu_cost = num_runs * avg_duration_seconds * 0.000014
    memory_cost = num_runs * avg_duration_seconds * memory_mb * 0.000001

    return cpu_cost + memory_cost
```

### CLI Status Command

```python
# src/bilancio/ui/cli/sweep.py

@sweep.command("status")
@click.argument("experiment_id")
def sweep_status(experiment_id: str):
    """Check status of a cloud sweep."""
    from bilancio.cloud.modal_app import results_volume

    # List runs on volume
    # Show completed/failed/pending counts
    # Show estimated cost
    pass
```

---

## File Changes Summary

**New files:**
- `src/bilancio/cloud/__init__.py`
- `src/bilancio/cloud/modal_app.py` - Modal app, image, remote function
- `src/bilancio/cloud/config.py` - Cloud configuration
- `src/bilancio/cloud/usage.py` - Usage tracking
- `src/bilancio/runners/cloud_executor.py` - CloudExecutor class
- `src/bilancio/storage/modal_artifact_loader.py` - Modal Volume loader
- `tests/cloud/__init__.py`
- `tests/cloud/test_cloud_executor.py`
- `tests/cloud/test_cloud_integration.py`
- `tests/cloud/test_modal_artifact_loader.py`

**Modified files:**
- `src/bilancio/ui/cli/sweep.py` - Add `--cloud` flag
- `src/bilancio/experiments/ring.py` - Accept injected executor
- `src/bilancio/experiments/comparison.py` - Accept injected executor
- `src/bilancio/experiments/balanced_comparison.py` - Accept injected executor
- `.gitignore` - Already updated with `.modal.toml`

---

## Deployment Steps

1. **First deploy** (creates Volume and registers function):
   ```bash
   uv run modal deploy src/bilancio/cloud/modal_app.py
   ```

2. **Test deployment**:
   ```bash
   uv run modal run src/bilancio/cloud/modal_app.py::run_simulation \
     --scenario-config '{"agents": [...]}' \
     --run-id test001 \
     --experiment-id test
   ```

3. **Run sweep on cloud**:
   ```bash
   uv run bilancio sweep ring \
     --config sweeps/my_sweep.yaml \
     --cloud \
     --cloud-parallel 100
   ```

---

## Success Criteria

1. [ ] `CloudExecutor` implements `SimulationExecutor` protocol
2. [ ] Simple scenario runs successfully on Modal
3. [ ] Results download correctly to local disk
4. [ ] Batch execution with 50+ parallel runs works
5. [ ] `RingSweepRunner` works with cloud executor
6. [ ] CLI `--cloud` flag works for all sweep commands
7. [ ] Unit tests pass (mocked Modal)
8. [ ] Integration tests pass (real Modal, marked slow)
9. [ ] Cost estimation available before running sweeps

---

## Future Extensions (Out of Scope)

- **GPU acceleration** - For ML-based analysis on simulation outputs
- **Async execution** - Non-blocking sweep with webhook notifications
- **S3 integration** - Store results on S3 instead of Modal Volume
- **Dashboard** - Web UI for monitoring sweep progress
- **Spot instances** - Use preemptible compute for cost savings
- **Multi-region** - Run closer to data sources

---

## Rollback Plan

If cloud execution has issues:
1. Remove `--cloud` flag usage
2. `RingSweepRunner` falls back to `LocalExecutor` (default)
3. No changes to core simulation logic

Cloud execution is purely additive - local execution remains unchanged.
