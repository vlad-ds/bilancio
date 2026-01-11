"""Tests for LocalExecutor simulation execution.

This module tests:
- Basic execution and result handling
- Output file creation
- Metrics extraction
- Error handling
- Parameter extraction
- Directory management
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import pytest

from bilancio.runners.local_executor import LocalExecutor
from bilancio.storage.models import RunResult, RunStatus, RunArtifacts


# Minimal scenario configuration for testing
MINIMAL_SCENARIO: Dict[str, Any] = {
    "version": 1,
    "name": "Test Scenario",
    "description": "Minimal test scenario",
    "agents": [
        {"id": "bank", "kind": "bank", "name": "Test Bank"},
        {"id": "firm1", "kind": "firm", "name": "Test Firm 1"},
        {"id": "firm2", "kind": "firm", "name": "Test Firm 2"},
    ],
    "initial_actions": [],
    "run": {"max_days": 5},
}

# Scenario with activity that produces metrics
SCENARIO_WITH_ACTIVITY: Dict[str, Any] = {
    "version": 1,
    "name": "Activity Test Scenario",
    "description": "Scenario with payment activity to generate metrics",
    "agents": [
        {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
        {"id": "bank", "kind": "bank", "name": "Test Bank"},
        {"id": "firm1", "kind": "firm", "name": "Test Firm 1"},
        {"id": "firm2", "kind": "firm", "name": "Test Firm 2"},
    ],
    "initial_actions": [
        {"mint_reserves": {"to": "bank", "amount": 10000}},
        {"mint_cash": {"to": "firm1", "amount": 2000}},
        {"mint_cash": {"to": "firm2", "amount": 1500}},
        {"deposit_cash": {"customer": "firm1", "bank": "bank", "amount": 1800}},
        {"deposit_cash": {"customer": "firm2", "bank": "bank", "amount": 1000}},
        {"create_payable": {"from": "firm1", "to": "firm2", "amount": 500, "due_day": 1}},
    ],
    "run": {"max_days": 10},
}


class TestLocalExecutorBasicExecution:
    """Tests for basic LocalExecutor.execute functionality."""

    @pytest.mark.slow
    def test_execute_returns_run_result(self, tmp_path: Path):
        """execute() returns a RunResult object."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_basic_001",
            output_dir=str(tmp_path),
        )

        assert isinstance(result, RunResult)
        assert result.run_id == "test_basic_001"

    @pytest.mark.slow
    def test_execute_simple_scenario_returns_completed_status(self, tmp_path: Path):
        """execute() with valid scenario returns COMPLETED status."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_completed_001",
            output_dir=str(tmp_path),
        )

        assert result.status == RunStatus.COMPLETED
        assert result.error is None

    @pytest.mark.slow
    def test_execute_populates_execution_time(self, tmp_path: Path):
        """execute() populates execution_time_ms."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_time_001",
            output_dir=str(tmp_path),
        )

        assert result.execution_time_ms is not None
        assert result.execution_time_ms > 0


class TestLocalExecutorOutputFiles:
    """Tests for output file creation."""

    @pytest.mark.slow
    def test_execute_creates_scenario_yaml(self, tmp_path: Path):
        """execute() creates scenario.yaml file."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_yaml_001",
            output_dir=str(tmp_path),
        )

        scenario_path = tmp_path / "scenario.yaml"
        assert scenario_path.exists()
        assert result.artifacts.scenario_yaml == str(scenario_path)

    @pytest.mark.slow
    def test_execute_creates_exports_directory(self, tmp_path: Path):
        """execute() creates out/ exports directory."""
        executor = LocalExecutor()
        executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_exports_001",
            output_dir=str(tmp_path),
        )

        exports_dir = tmp_path / "out"
        assert exports_dir.exists()
        assert exports_dir.is_dir()

    @pytest.mark.slow
    def test_execute_creates_balances_csv(self, tmp_path: Path):
        """execute() creates balances.csv file."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_balances_001",
            output_dir=str(tmp_path),
        )

        balances_path = tmp_path / "out" / "balances.csv"
        assert balances_path.exists()
        assert result.artifacts.balances_csv == str(balances_path)

    @pytest.mark.slow
    def test_execute_creates_events_jsonl(self, tmp_path: Path):
        """execute() creates events.jsonl file."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_events_001",
            output_dir=str(tmp_path),
        )

        events_path = tmp_path / "out" / "events.jsonl"
        assert events_path.exists()
        assert result.artifacts.events_jsonl == str(events_path)

    @pytest.mark.slow
    def test_execute_creates_metrics_json(self, tmp_path: Path):
        """execute() creates metrics.json file when scenario has activity."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=SCENARIO_WITH_ACTIVITY,
            run_id="test_metrics_json_001",
            output_dir=str(tmp_path),
        )

        metrics_path = tmp_path / "out" / "metrics.json"
        assert metrics_path.exists()
        assert result.artifacts.metrics_json == str(metrics_path)

    @pytest.mark.slow
    def test_execute_creates_metrics_csv(self, tmp_path: Path):
        """execute() creates metrics.csv file when scenario has activity."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=SCENARIO_WITH_ACTIVITY,
            run_id="test_metrics_csv_001",
            output_dir=str(tmp_path),
        )

        metrics_path = tmp_path / "out" / "metrics.csv"
        assert metrics_path.exists()
        assert result.artifacts.metrics_csv == str(metrics_path)

    @pytest.mark.slow
    def test_execute_creates_run_html(self, tmp_path: Path):
        """execute() creates run.html file."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_html_001",
            output_dir=str(tmp_path),
        )

        html_path = tmp_path / "run.html"
        assert html_path.exists()
        assert result.artifacts.run_html == str(html_path)


class TestLocalExecutorMetrics:
    """Tests for metrics extraction from simulation results."""

    @pytest.mark.slow
    def test_execute_populates_metrics_from_simulation(self, tmp_path: Path):
        """execute() extracts metrics from simulation output."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_metrics_001",
            output_dir=str(tmp_path),
        )

        # Metrics should be populated (may be None if simulation has no defaults)
        assert isinstance(result.metrics, dict)
        # The metrics dict should have the expected keys (may be None values)
        assert "phi_total" in result.metrics or result.metrics == {}
        assert "delta_total" in result.metrics or result.metrics == {}

    @pytest.mark.slow
    def test_execute_metrics_reflect_simulation_state(self, tmp_path: Path):
        """execute() metrics should reflect actual simulation results."""
        executor = LocalExecutor()
        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_metrics_reflect_001",
            output_dir=str(tmp_path),
        )

        # With a minimal scenario (no setup events), there should be no defaults
        # phi_total and delta_total should be 0 or very small
        if result.metrics:
            if "phi_total" in result.metrics and result.metrics["phi_total"] is not None:
                assert result.metrics["phi_total"] >= 0
            if "delta_total" in result.metrics and result.metrics["delta_total"] is not None:
                assert result.metrics["delta_total"] >= 0


class TestLocalExecutorErrorHandling:
    """Tests for error handling in LocalExecutor."""

    @pytest.mark.slow
    def test_execute_returns_failed_status_on_invalid_scenario(self, tmp_path: Path):
        """execute() returns FAILED status when scenario is invalid."""
        executor = LocalExecutor()

        # Invalid scenario - missing required fields
        invalid_scenario: Dict[str, Any] = {
            "agents": "not_a_list",  # Should be a list
            "setup": [],
        }

        result = executor.execute(
            scenario_config=invalid_scenario,
            run_id="test_failed_001",
            output_dir=str(tmp_path),
        )

        assert result.status == RunStatus.FAILED

    @pytest.mark.slow
    def test_execute_returns_error_message_on_failure(self, tmp_path: Path):
        """execute() includes error message when simulation fails."""
        executor = LocalExecutor()

        # Invalid scenario configuration
        invalid_scenario: Dict[str, Any] = {
            "agents": [{"id": "bank"}],  # Missing 'kind'
            "setup": [],
        }

        result = executor.execute(
            scenario_config=invalid_scenario,
            run_id="test_error_msg_001",
            output_dir=str(tmp_path),
        )

        assert result.status == RunStatus.FAILED
        assert result.error is not None
        assert len(result.error) > 0

    @pytest.mark.slow
    def test_execute_records_execution_time_on_failure(self, tmp_path: Path):
        """execute() records execution_time_ms even on failure."""
        executor = LocalExecutor()

        invalid_scenario: Dict[str, Any] = {
            "agents": "invalid",
            "setup": [],
        }

        result = executor.execute(
            scenario_config=invalid_scenario,
            run_id="test_time_fail_001",
            output_dir=str(tmp_path),
        )

        assert result.execution_time_ms is not None
        assert result.execution_time_ms >= 0


class TestLocalExecutorParameterExtraction:
    """Tests for _extract_parameters method."""

    def test_extract_parameters_extracts_agent_count(self):
        """_extract_parameters extracts n_agents from scenario config."""
        executor = LocalExecutor()

        config: Dict[str, Any] = {
            "agents": [
                {"id": "a1", "kind": "bank"},
                {"id": "a2", "kind": "firm"},
                {"id": "a3", "kind": "firm"},
                {"id": "a4", "kind": "household"},
            ],
            "setup": [],
        }

        params = executor._extract_parameters(config)

        assert params["n_agents"] == 4

    def test_extract_parameters_extracts_dealer_enabled_true(self):
        """_extract_parameters extracts dealer_enabled when true."""
        executor = LocalExecutor()

        config: Dict[str, Any] = {
            "agents": [{"id": "bank", "kind": "bank"}],
            "setup": [],
            "dealer": {"enabled": True},
        }

        params = executor._extract_parameters(config)

        assert params["dealer_enabled"] is True

    def test_extract_parameters_extracts_dealer_enabled_false(self):
        """_extract_parameters extracts dealer_enabled when false."""
        executor = LocalExecutor()

        config: Dict[str, Any] = {
            "agents": [{"id": "bank", "kind": "bank"}],
            "setup": [],
            "dealer": {"enabled": False},
        }

        params = executor._extract_parameters(config)

        assert params["dealer_enabled"] is False

    def test_extract_parameters_dealer_defaults_to_false(self):
        """_extract_parameters defaults dealer_enabled to False when not specified."""
        executor = LocalExecutor()

        config: Dict[str, Any] = {
            "agents": [{"id": "bank", "kind": "bank"}],
            "setup": [],
        }

        params = executor._extract_parameters(config)

        assert params["dealer_enabled"] is False

    def test_extract_parameters_extracts_max_days(self):
        """_extract_parameters extracts max_days from run config."""
        executor = LocalExecutor()

        config: Dict[str, Any] = {
            "agents": [{"id": "bank", "kind": "bank"}],
            "setup": [],
            "run": {"max_days": 30},
        }

        params = executor._extract_parameters(config)

        assert params["max_days"] == 30

    def test_extract_parameters_handles_empty_config(self):
        """_extract_parameters handles empty config gracefully."""
        executor = LocalExecutor()

        config: Dict[str, Any] = {}

        params = executor._extract_parameters(config)

        # Should not have n_agents key if no agents
        assert "n_agents" not in params
        # dealer_enabled should default to False
        assert params["dealer_enabled"] is False

    def test_extract_parameters_handles_missing_run_config(self):
        """_extract_parameters handles missing run config."""
        executor = LocalExecutor()

        config: Dict[str, Any] = {
            "agents": [{"id": "bank", "kind": "bank"}],
            "setup": [],
        }

        params = executor._extract_parameters(config)

        # max_days should not be in params if not specified
        assert "max_days" not in params


class TestLocalExecutorDirectoryManagement:
    """Tests for output directory management."""

    @pytest.mark.slow
    def test_output_dir_parameter_is_respected(self, tmp_path: Path):
        """execute() uses provided output_dir."""
        executor = LocalExecutor()
        custom_dir = tmp_path / "custom_output"
        custom_dir.mkdir()

        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_custom_dir_001",
            output_dir=str(custom_dir),
        )

        # Artifacts should be in the custom directory
        assert result.artifacts.scenario_yaml is not None
        assert str(custom_dir) in result.artifacts.scenario_yaml

    @pytest.mark.slow
    def test_temp_directory_created_when_output_dir_is_none(self):
        """execute() creates temp directory when output_dir is None."""
        executor = LocalExecutor()

        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_temp_dir_001",
            output_dir=None,
        )

        # Artifacts should exist in a temp directory
        assert result.artifacts.scenario_yaml is not None
        assert Path(result.artifacts.scenario_yaml).exists()
        # The path should contain 'bilancio_run' (the temp dir prefix)
        assert "bilancio_run" in result.artifacts.scenario_yaml

    @pytest.mark.slow
    def test_output_dir_created_if_not_exists(self, tmp_path: Path):
        """execute() creates output_dir if it doesn't exist."""
        executor = LocalExecutor()
        new_dir = tmp_path / "new_output_dir"

        # Directory should not exist yet
        assert not new_dir.exists()

        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_create_dir_001",
            output_dir=str(new_dir),
        )

        # Directory should now exist
        assert new_dir.exists()
        assert result.status == RunStatus.COMPLETED

    @pytest.mark.slow
    def test_nested_output_dir_created(self, tmp_path: Path):
        """execute() creates nested output directories."""
        executor = LocalExecutor()
        nested_dir = tmp_path / "level1" / "level2" / "level3"

        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id="test_nested_dir_001",
            output_dir=str(nested_dir),
        )

        assert nested_dir.exists()
        assert result.status == RunStatus.COMPLETED


class TestLocalExecutorRunIdHandling:
    """Tests for run_id handling in results."""

    @pytest.mark.slow
    def test_run_id_preserved_in_result(self, tmp_path: Path):
        """execute() preserves run_id in result."""
        executor = LocalExecutor()
        custom_run_id = "unique_run_id_12345"

        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id=custom_run_id,
            output_dir=str(tmp_path),
        )

        assert result.run_id == custom_run_id

    @pytest.mark.slow
    def test_run_id_in_temp_dir_name(self):
        """execute() includes run_id in temp directory name."""
        executor = LocalExecutor()
        run_id = "my_test_run"

        result = executor.execute(
            scenario_config=MINIMAL_SCENARIO,
            run_id=run_id,
            output_dir=None,
        )

        # The temp directory path should include the run_id
        assert result.artifacts.scenario_yaml is not None
        assert run_id in result.artifacts.scenario_yaml


class TestLocalExecutorScenarioWithActivity:
    """Tests with scenarios that have actual activity."""

    @pytest.mark.slow
    def test_scenario_with_obligations_produces_metrics(self, tmp_path: Path):
        """Scenario with setup events produces meaningful metrics."""
        executor = LocalExecutor()

        result = executor.execute(
            scenario_config=SCENARIO_WITH_ACTIVITY,
            run_id="test_activity_001",
            output_dir=str(tmp_path),
        )

        assert result.status == RunStatus.COMPLETED
        # Metrics json should be created and contain data
        metrics_path = tmp_path / "out" / "metrics.json"
        assert metrics_path.exists()

        metrics_data = json.loads(metrics_path.read_text())
        assert len(metrics_data) > 0

    @pytest.mark.slow
    def test_result_artifacts_are_complete(self, tmp_path: Path):
        """execute() returns RunArtifacts with all expected fields for active scenario."""
        executor = LocalExecutor()

        result = executor.execute(
            scenario_config=SCENARIO_WITH_ACTIVITY,
            run_id="test_artifacts_001",
            output_dir=str(tmp_path),
        )

        artifacts = result.artifacts
        assert isinstance(artifacts, RunArtifacts)

        # All artifact paths should be set for a scenario with activity
        assert artifacts.scenario_yaml is not None
        assert artifacts.events_jsonl is not None
        assert artifacts.balances_csv is not None
        assert artifacts.metrics_csv is not None
        assert artifacts.metrics_json is not None
        assert artifacts.run_html is not None

        # All referenced files should exist
        assert Path(artifacts.scenario_yaml).exists()
        assert Path(artifacts.events_jsonl).exists()
        assert Path(artifacts.balances_csv).exists()
        assert Path(artifacts.metrics_csv).exists()
        assert Path(artifacts.metrics_json).exists()
        assert Path(artifacts.run_html).exists()
