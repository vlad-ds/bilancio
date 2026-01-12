"""Modal app definition for cloud simulation execution.

This module defines the Modal app, container image, volume, and remote
function for running bilancio simulations in the cloud.
"""

from __future__ import annotations

import modal

# Define the Modal app
app = modal.App("bilancio-simulations")

# Create a persistent volume for storing results
# Results persist across function invocations
results_volume = modal.Volume.from_name(
    "bilancio-results",
    create_if_missing=True,
)

# Define the container image with all bilancio dependencies
# We add the local source code to the image
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
        "jinja2>=3.0",
        "click>=8.0",
        "xkcdpass>=1.19.0",
    )
    .add_local_python_source("bilancio")
)

RESULTS_MOUNT_PATH = "/results"


@app.function(
    image=image,
    volumes={RESULTS_MOUNT_PATH: results_volume},
    timeout=600,  # 10 minutes max per simulation
    memory=2048,  # 2GB RAM
)
def run_simulation(
    scenario_config: dict,
    run_id: str,
    experiment_id: str,
    options: dict,
    job_id: str = "",
) -> dict:
    """Run a single simulation in the cloud.

    Args:
        scenario_config: Full scenario YAML as dict
        run_id: Unique identifier for this run
        experiment_id: Groups related runs together
        options: RunOptions as dict (mode, max_days, quiet_days, etc.)
        job_id: Bilancio job ID (for logging/tracking)

    Returns:
        Dict with status, artifact paths (relative to volume), metrics, error
    """
    import time
    from pathlib import Path

    import yaml

    start_time = time.time()

    # Log job info prominently at the start (visible in Modal logs)
    import sys
    modal_call_id = modal.current_function_call_id()
    print("=" * 60, flush=True)
    print(f"BILANCIO SIMULATION", flush=True)
    print(f"  Job ID:      {job_id or 'N/A'}", flush=True)
    print(f"  Run ID:      {run_id}", flush=True)
    print(f"  Experiment:  {experiment_id}", flush=True)
    print(f"  Modal Call:  {modal_call_id}", flush=True)
    print("=" * 60, flush=True)
    sys.stdout.flush()

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
            show=options.get("show_events", "detailed"),
            check_invariants=options.get("check_invariants", "daily"),
            default_handling=options.get("default_handling", "fail-fast"),
            export={
                "balances_csv": str(out_dir / "balances.csv"),
                "events_jsonl": str(out_dir / "events.jsonl"),
            },
            html_output=run_dir / "run.html",
            t_account=options.get("t_account", False),
            detailed_dealer_logging=options.get("detailed_dealer_logging", False),
            run_id=run_id,
            regime=options.get("regime", ""),
        )

        # Commit changes to volume
        results_volume.commit()

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Build artifact paths (relative to run directory within volume)
        artifacts = {
            "scenario_yaml": "scenario.yaml",
            "events_jsonl": "out/events.jsonl",
            "balances_csv": "out/balances.csv",
            "run_html": "run.html",
        }

        return {
            "run_id": run_id,
            "status": "completed",
            "storage_type": "modal_volume",
            "storage_base": f"{experiment_id}/runs/{run_id}",
            "artifacts": artifacts,
            "execution_time_ms": execution_time_ms,
            "error": None,
            "modal_call_id": modal_call_id,
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
            "modal_call_id": modal_call_id,
        }


@app.function(
    image=image,
    timeout=60,
    memory=256,
)
def health_check() -> dict:
    """Simple health check to verify Modal deployment.

    Returns:
        Dict with status and bilancio version info.
    """
    try:
        import bilancio

        return {
            "status": "ok",
            "bilancio_available": True,
            "version": getattr(bilancio, "__version__", "unknown"),
        }
    except ImportError as e:
        return {
            "status": "error",
            "bilancio_available": False,
            "error": str(e),
        }


# Local entrypoint for testing
@app.local_entrypoint()
def main():
    """Test the Modal deployment with a health check."""
    print("Running health check...")
    result = health_check.remote()
    print(f"Health check result: {result}")

    if result["status"] == "ok":
        print("Modal deployment is healthy!")
    else:
        print(f"Modal deployment has issues: {result.get('error', 'unknown')}")
