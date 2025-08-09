from abc import ABC, abstractmethod
from typing import Any, Protocol


class Policy(Protocol):
    """Protocol defining the interface for policies."""

    def evaluate(self, context: dict[str, Any]) -> Any:
        """Evaluate the policy given the provided context."""
        ...


class BasePolicy(ABC):
    """Abstract base class implementing the Policy protocol."""

    @abstractmethod
    def evaluate(self, context: dict[str, Any]) -> Any:
        """Evaluate the policy given the provided context."""
        pass
