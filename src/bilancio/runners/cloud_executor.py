"""Cloud executor using Modal for remote simulation execution."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from bilancio.runners.models import ExecutionResult, RunOptions
from bilancio.storage.models import RunStatus


class CloudExecutor:
    """Execute simulations on Modal cloud infrastructure.

    Results are stored on a Modal Volume and optionally downloaded to local disk
    after execution completes.

    This executor implements the SimulationExecutor protocol from
    bilancio.runners.protocols.

    Example:
        executor = CloudExecutor(experiment_id="my_sweep")
        result = executor.execute(
            scenario_config=scenario,
            run_id="run_001",
            output_dir=Path("./output"),
            options=RunOptions(max_days=30),
        )
    """

    def __init__(
        self,
        experiment_id: str,
        download_artifacts: bool = True,
        local_output_dir: Optional[Path] = None,
        volume_name: str = "bilancio-results",
    ):
        """Initialize cloud executor.

        Args:
            experiment_id: Identifier for this experiment (groups runs together).
            download_artifacts: Whether to download results to local disk after execution.
            local_output_dir: Where to download artifacts. Defaults to
                out/experiments/{experiment_id}.
            volume_name: Name of the Modal Volume for result storage.
        """
        self.experiment_id = experiment_id
        self.download_artifacts = download_artifacts
        self.local_output_dir = local_output_dir or Path(
            f"out/experiments/{experiment_id}"
        )
        self.volume_name = volume_name
        self.app_name = "bilancio-simulations"

        # Lazy reference to deployed function
        self._run_simulation = None

    def _get_run_simulation(self):
        """Get reference to the deployed Modal function.

        Uses Function.from_name() to reference the deployed function,
        which allows calling it from outside the Modal app context.
        """
        if self._run_simulation is None:
            import modal

            self._run_simulation = modal.Function.from_name(
                self.app_name, "run_simulation"
            )
        return self._run_simulation

    def execute(
        self,
        scenario_config: Dict[str, Any],
        run_id: str,
        output_dir: Path,
        options: RunOptions,
    ) -> ExecutionResult:
        """Execute simulation on Modal cloud.

        Args:
            scenario_config: Full scenario configuration dict.
            run_id: Unique run identifier.
            output_dir: Local directory for results (used if download_artifacts=True).
            options: Simulation run options.

        Returns:
            ExecutionResult with status and artifact references.
        """
        run_simulation = self._get_run_simulation()

        # Convert options to dict for serialization
        options_dict = self._options_to_dict(options)

        # Execute remotely (blocks until complete)
        result = run_simulation.remote(
            scenario_config=scenario_config,
            run_id=run_id,
            experiment_id=self.experiment_id,
            options=options_dict,
        )

        # Download artifacts if requested and determine storage location
        if self.download_artifacts and result["status"] == "completed":
            self._download_run_artifacts(run_id, output_dir, result["artifacts"])
            # When downloading, the storage_base should be the local path
            storage_type = "local"
            storage_base = str(output_dir.resolve())
        else:
            # When not downloading, keep the modal_volume reference
            storage_type = result["storage_type"]
            storage_base = result["storage_base"]

        return ExecutionResult(
            run_id=result["run_id"],
            status=(
                RunStatus.COMPLETED
                if result["status"] == "completed"
                else RunStatus.FAILED
            ),
            storage_type=storage_type,
            storage_base=storage_base,
            artifacts=result["artifacts"],
            error=result.get("error"),
            execution_time_ms=result.get("execution_time_ms"),
        )

    def execute_batch(
        self,
        runs: List[Tuple[Dict[str, Any], str, RunOptions]],
        max_parallel: int = 50,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[ExecutionResult]:
        """Execute multiple simulations in parallel on Modal.

        Modal handles parallelization automatically. This method provides
        a convenient interface for batch execution.

        Args:
            runs: List of (scenario_config, run_id, options) tuples.
            max_parallel: Maximum concurrent Modal function calls (unused,
                Modal handles this internally).
            progress_callback: Called with (completed, total) after each completion.

        Returns:
            List of ExecutionResult in same order as input.
        """
        run_simulation = self._get_run_simulation()

        total = len(runs)
        results: List[Optional[ExecutionResult]] = [None] * total

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

            # Download artifacts if requested
            if self.download_artifacts and result["status"] == "completed":
                output_dir = self.local_output_dir / "runs" / run_id
                self._download_run_artifacts(run_id, output_dir, result["artifacts"])

            results[idx] = ExecutionResult(
                run_id=result["run_id"],
                status=(
                    RunStatus.COMPLETED
                    if result["status"] == "completed"
                    else RunStatus.FAILED
                ),
                storage_type=result["storage_type"],
                storage_base=result["storage_base"],
                artifacts=result["artifacts"],
                error=result.get("error"),
                execution_time_ms=result.get("execution_time_ms"),
            )

            completed += 1
            if progress_callback:
                progress_callback(completed, total)

        return results  # type: ignore

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
            "regime": options.regime or "",
        }

    def _download_run_artifacts(
        self,
        run_id: str,
        output_dir: Path,
        artifacts: Dict[str, str],
    ) -> None:
        """Download artifacts from Modal Volume to local disk.

        Args:
            run_id: The run identifier.
            output_dir: Local directory to download to.
            artifacts: Dict mapping artifact names to relative paths.
        """
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

            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Use Modal CLI to download
            try:
                subprocess.run(
                    [
                        "modal",
                        "volume",
                        "get",
                        self.volume_name,
                        remote_path,
                        str(local_path),
                        "--force",  # Overwrite existing files
                    ],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                # Log but don't fail - artifact might be optional
                print(
                    f"Warning: Failed to download {artifact_name}: {e.stderr.decode()}"
                )
