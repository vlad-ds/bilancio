"""
Specification validation framework for agents and instruments.

This module provides:
- Data structures for defining agent and instrument specifications
- Registry for tracking all agents and instruments
- Completeness checkers to validate specifications
- Relationship matrix validation

Usage:
    from bilancio.specification import (
        AgentSpec, InstrumentSpec, SpecificationRegistry,
        validate_agent_completeness, validate_instrument_completeness,
    )
"""

from .models import (
    AgentSpec,
    InstrumentSpec,
    InstrumentRelation,
    AgentRelation,
    DecisionSpec,
    LifecycleSpec,
    BalanceSheetPosition,
)
from .registry import SpecificationRegistry
from .validators import (
    validate_agent_completeness,
    validate_instrument_completeness,
    validate_all_relationships,
    ValidationResult,
    ValidationError,
)

__all__ = [
    # Models
    "AgentSpec",
    "InstrumentSpec",
    "InstrumentRelation",
    "AgentRelation",
    "DecisionSpec",
    "LifecycleSpec",
    "BalanceSheetPosition",
    # Registry
    "SpecificationRegistry",
    # Validators
    "validate_agent_completeness",
    "validate_instrument_completeness",
    "validate_all_relationships",
    "ValidationResult",
    "ValidationError",
]
