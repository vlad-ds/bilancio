"""Data models for storage abstractions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class RunStatus(Enum):
    """Status of a simulation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RunArtifacts:
    """References to simulation output artifacts."""
    scenario_yaml: Optional[str] = None
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
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: RunArtifacts = field(default_factory=RunArtifacts)
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None


@dataclass
class RegistryEntry:
    """Metadata for registry storage."""
    run_id: str
    experiment_id: str
    status: RunStatus
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifact_paths: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
