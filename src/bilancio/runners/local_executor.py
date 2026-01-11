"""Local synchronous simulation executor."""

from __future__ import annotations

import time
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Callable

import yaml

from bilancio.storage.models import RunResult, RunArtifacts, RunStatus


class LocalExecutor:
    """Execute simulations locally and synchronously.

    This wraps the existing run_scenario() function to conform to
    the SimulationExecutor protocol.
    """

    def execute(
        self,
        scenario_config: Dict[str, Any],
        run_id: str,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> RunResult:
        """Execute simulation, return result.

        Args:
            scenario_config: Complete scenario configuration dict
            run_id: Unique identifier for this run
            output_dir: Directory for output files (temp dir if not specified)
            progress_callback: Optional callback for progress updates

        Returns:
            RunResult with status, metrics, and artifact paths
        """
        # Import here to avoid circular imports at module load time
        from bilancio.ui.run import run_scenario
        from bilancio.analysis.loaders import read_events_jsonl, read_balances_csv
        from bilancio.analysis.report import (
            compute_day_metrics,
            write_day_metrics_csv,
            write_day_metrics_json,
        )
        import json

        start_time = time.time()

        # Create output directory
        if output_dir:
            out_path = Path(output_dir)
        else:
            out_path = Path(tempfile.mkdtemp(prefix=f"bilancio_run_{run_id}_"))
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
                html_output=run_html_path,
            )

            # Generate metrics from exported events and balances
            if events_path.exists():
                events = list(read_events_jsonl(events_path))
                balances_rows = None
                if balances_path.exists():
                    balances_rows = read_balances_csv(balances_path)

                bundle = compute_day_metrics(events, balances_rows, day_list=None)
                metrics_rows = bundle.get("day_metrics", [])

                if metrics_rows:
                    write_day_metrics_csv(metrics_csv_path, metrics_rows)
                    write_day_metrics_json(metrics_json_path, metrics_rows)

            # Extract metrics from metrics.json if it exists
            metrics: Dict[str, Any] = {}
            if metrics_json_path.exists():
                metrics_data = json.loads(metrics_json_path.read_text())
                if metrics_data:
                    # metrics_data is a list of day-by-day metrics
                    if isinstance(metrics_data, list) and metrics_data:
                        last = metrics_data[-1]
                    else:
                        last = metrics_data
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
                artifacts=RunArtifacts(
                    scenario_yaml=str(scenario_path) if scenario_path.exists() else None,
                ),
                error=str(e),
                execution_time_ms=execution_time_ms,
            )

    def _extract_parameters(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key parameters from scenario config for registry."""
        params: Dict[str, Any] = {}

        # Count agents
        if "agents" in config:
            params["n_agents"] = len(config["agents"])

        # From run config
        run_cfg = config.get("run", {})
        if "max_days" in run_cfg:
            params["max_days"] = run_cfg["max_days"]

        # From dealer config
        dealer_cfg = config.get("dealer", {})
        params["dealer_enabled"] = dealer_cfg.get("enabled", False)

        return params
