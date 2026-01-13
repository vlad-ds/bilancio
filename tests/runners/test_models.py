"""Tests for runner data models."""

import pytest

from bilancio.runners.models import RunOptions, ExecutionResult
from bilancio.storage.models import RunStatus


class TestRunOptionsDefaults:
    """Tests for RunOptions default values."""

    def test_mode_defaults_to_until_stable(self):
        """mode defaults to 'until_stable'."""
        options = RunOptions()
        assert options.mode == "until_stable"

    def test_max_days_defaults_to_90(self):
        """max_days defaults to 90."""
        options = RunOptions()
        assert options.max_days == 90

    def test_quiet_days_defaults_to_2(self):
        """quiet_days defaults to 2."""
        options = RunOptions()
        assert options.quiet_days == 2

    def test_check_invariants_defaults_to_daily(self):
        """check_invariants defaults to 'daily'."""
        options = RunOptions()
        assert options.check_invariants == "daily"

    def test_default_handling_defaults_to_fail_fast(self):
        """default_handling defaults to 'fail-fast'."""
        options = RunOptions()
        assert options.default_handling == "fail-fast"

    def test_show_events_defaults_to_detailed(self):
        """show_events defaults to 'detailed'."""
        options = RunOptions()
        assert options.show_events == "detailed"

    def test_show_balances_defaults_to_none(self):
        """show_balances defaults to None."""
        options = RunOptions()
        assert options.show_balances is None

    def test_t_account_defaults_to_false(self):
        """t_account defaults to False."""
        options = RunOptions()
        assert options.t_account is False

    def test_detailed_dealer_logging_defaults_to_false(self):
        """detailed_dealer_logging defaults to False."""
        options = RunOptions()
        assert options.detailed_dealer_logging is False

    def test_run_id_defaults_to_none(self):
        """run_id defaults to None."""
        options = RunOptions()
        assert options.run_id is None

    def test_regime_defaults_to_none(self):
        """regime defaults to None."""
        options = RunOptions()
        assert options.regime is None


class TestRunOptionsCustomization:
    """Tests for customizing RunOptions."""

    def test_mode_can_be_customized(self):
        """mode can be set to custom value."""
        options = RunOptions(mode="fixed_days")
        assert options.mode == "fixed_days"

    def test_max_days_can_be_customized(self):
        """max_days can be set to custom value."""
        options = RunOptions(max_days=30)
        assert options.max_days == 30

    def test_quiet_days_can_be_customized(self):
        """quiet_days can be set to custom value."""
        options = RunOptions(quiet_days=5)
        assert options.quiet_days == 5

    def test_check_invariants_can_be_customized(self):
        """check_invariants can be set to custom value."""
        options = RunOptions(check_invariants="end")
        assert options.check_invariants == "end"

    def test_default_handling_can_be_customized(self):
        """default_handling can be set to custom value."""
        options = RunOptions(default_handling="continue")
        assert options.default_handling == "continue"

    def test_show_events_can_be_customized(self):
        """show_events can be set to custom value."""
        options = RunOptions(show_events="summary")
        assert options.show_events == "summary"

    def test_show_balances_can_be_customized(self):
        """show_balances can be set to list of agent names."""
        options = RunOptions(show_balances=["Bank1", "Firm1"])
        assert options.show_balances == ["Bank1", "Firm1"]

    def test_t_account_can_be_customized(self):
        """t_account can be set to True."""
        options = RunOptions(t_account=True)
        assert options.t_account is True

    def test_detailed_dealer_logging_can_be_customized(self):
        """detailed_dealer_logging can be set to True."""
        options = RunOptions(detailed_dealer_logging=True)
        assert options.detailed_dealer_logging is True

    def test_run_id_can_be_customized(self):
        """run_id can be set to custom value."""
        options = RunOptions(run_id="custom_run_001")
        assert options.run_id == "custom_run_001"

    def test_regime_can_be_customized(self):
        """regime can be set to custom value."""
        options = RunOptions(regime="baseline")
        assert options.regime == "baseline"

    def test_multiple_options_can_be_customized(self):
        """Multiple options can be customized at once."""
        options = RunOptions(
            mode="continuous",
            max_days=100,
            quiet_days=3,
            check_invariants="never",
            default_handling="continue",
            show_events="none",
            show_balances=["Bank1"],
            t_account=True,
            detailed_dealer_logging=True,
            run_id="test_run",
            regime="treatment",
        )

        assert options.mode == "continuous"
        assert options.max_days == 100
        assert options.quiet_days == 3
        assert options.check_invariants == "never"
        assert options.default_handling == "continue"
        assert options.show_events == "none"
        assert options.show_balances == ["Bank1"]
        assert options.t_account is True
        assert options.detailed_dealer_logging is True
        assert options.run_id == "test_run"
        assert options.regime == "treatment"


class TestExecutionResultCreation:
    """Tests for ExecutionResult creation."""

    def test_creation_with_all_required_fields(self):
        """ExecutionResult can be created with all required fields."""
        result = ExecutionResult(
            run_id="run_001",
            status=RunStatus.COMPLETED,
            storage_type="local",
            storage_base="/path/to/run",
        )

        assert result.run_id == "run_001"
        assert result.status == RunStatus.COMPLETED
        assert result.storage_type == "local"
        assert result.storage_base == "/path/to/run"

    def test_creation_with_failed_status(self):
        """ExecutionResult can be created with FAILED status."""
        result = ExecutionResult(
            run_id="run_fail",
            status=RunStatus.FAILED,
            storage_type="local",
            storage_base="/path/to/run",
            error="Simulation diverged",
        )

        assert result.status == RunStatus.FAILED
        assert result.error == "Simulation diverged"

    def test_creation_with_all_fields(self):
        """ExecutionResult can be created with all fields."""
        result = ExecutionResult(
            run_id="run_002",
            status=RunStatus.COMPLETED,
            storage_type="s3",
            storage_base="s3://bucket/prefix",
            artifacts={
                "events_jsonl": "out/events.jsonl",
                "balances_csv": "out/balances.csv",
            },
            error=None,
            execution_time_ms=5000,
        )

        assert result.run_id == "run_002"
        assert result.status == RunStatus.COMPLETED
        assert result.storage_type == "s3"
        assert result.storage_base == "s3://bucket/prefix"
        assert result.artifacts["events_jsonl"] == "out/events.jsonl"
        assert result.artifacts["balances_csv"] == "out/balances.csv"
        assert result.error is None
        assert result.execution_time_ms == 5000


class TestExecutionResultDefaults:
    """Tests for ExecutionResult default values."""

    def test_artifacts_defaults_to_empty_dict(self):
        """artifacts defaults to empty dict."""
        result = ExecutionResult(
            run_id="run_001",
            status=RunStatus.COMPLETED,
            storage_type="local",
            storage_base="/path",
        )
        assert result.artifacts == {}

    def test_error_defaults_to_none(self):
        """error defaults to None."""
        result = ExecutionResult(
            run_id="run_001",
            status=RunStatus.COMPLETED,
            storage_type="local",
            storage_base="/path",
        )
        assert result.error is None

    def test_execution_time_ms_defaults_to_none(self):
        """execution_time_ms defaults to None."""
        result = ExecutionResult(
            run_id="run_001",
            status=RunStatus.COMPLETED,
            storage_type="local",
            storage_base="/path",
        )
        assert result.execution_time_ms is None


class TestExecutionResultArtifacts:
    """Tests for ExecutionResult artifacts handling."""

    def test_artifacts_can_store_multiple_paths(self):
        """artifacts can store multiple artifact paths."""
        artifacts = {
            "scenario_yaml": "scenario.yaml",
            "events_jsonl": "out/events.jsonl",
            "balances_csv": "out/balances.csv",
            "run_html": "run.html",
            "metrics_csv": "out/metrics.csv",
        }

        result = ExecutionResult(
            run_id="run_001",
            status=RunStatus.COMPLETED,
            storage_type="local",
            storage_base="/path",
            artifacts=artifacts,
        )

        assert len(result.artifacts) == 5
        assert result.artifacts["scenario_yaml"] == "scenario.yaml"
        assert result.artifacts["events_jsonl"] == "out/events.jsonl"

    def test_artifacts_can_be_modified(self):
        """artifacts dict can be modified after creation."""
        result = ExecutionResult(
            run_id="run_001",
            status=RunStatus.COMPLETED,
            storage_type="local",
            storage_base="/path",
        )

        result.artifacts["new_artifact"] = "path/to/artifact"
        assert result.artifacts["new_artifact"] == "path/to/artifact"


class TestExecutionResultStorageTypes:
    """Tests for ExecutionResult storage type variants."""

    def test_local_storage_type(self):
        """ExecutionResult supports 'local' storage type."""
        result = ExecutionResult(
            run_id="run_001",
            status=RunStatus.COMPLETED,
            storage_type="local",
            storage_base="/Users/test/experiments/run_001",
        )
        assert result.storage_type == "local"

    def test_s3_storage_type(self):
        """ExecutionResult supports 's3' storage type."""
        result = ExecutionResult(
            run_id="run_001",
            status=RunStatus.COMPLETED,
            storage_type="s3",
            storage_base="s3://my-bucket/experiments/run_001",
        )
        assert result.storage_type == "s3"

    def test_gcs_storage_type(self):
        """ExecutionResult supports 'gcs' storage type."""
        result = ExecutionResult(
            run_id="run_001",
            status=RunStatus.COMPLETED,
            storage_type="gcs",
            storage_base="gs://my-bucket/experiments/run_001",
        )
        assert result.storage_type == "gcs"
