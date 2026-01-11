"""Protocol definitions for simulation executors."""

from __future__ import annotations

from typing import Protocol, Optional, Dict, Any, Callable, runtime_checkable

# Import from storage to avoid circular imports at runtime
from bilancio.storage.models import RunResult, RunStatus


@runtime_checkable
class SimulationExecutor(Protocol):
    """Protocol for synchronous simulation execution."""

    def execute(
        self,
        scenario_config: Dict[str, Any],
        run_id: str,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> RunResult:
        """Execute a simulation, return result."""
        ...


@runtime_checkable
class JobExecutor(Protocol):
    """Protocol for async/distributed job execution (future use)."""

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
