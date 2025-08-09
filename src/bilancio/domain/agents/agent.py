from abc import ABC
from typing import Protocol


class Agent(Protocol):
    """Protocol defining the interface for agents."""
    
    @property
    def id(self) -> str:
        """Unique identifier for the agent."""
        ...
    
    @property
    def name(self) -> str:
        """Human-readable name of the agent."""
        ...


class BaseAgent(ABC):
    """Abstract base class implementing the Agent protocol."""
    
    def __init__(self, id: str, name: str):
        self._id = id
        self._name = name
    
    @property
    def id(self) -> str:
        """Unique identifier for the agent."""
        return self._id
    
    @property
    def name(self) -> str:
        """Human-readable name of the agent."""
        return self._name