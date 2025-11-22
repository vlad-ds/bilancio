"""Agent scaffolding for dealer-ring actors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from bilancio.domain.agent import Agent


@dataclass
class DealerAgent(Agent):
    """Dealer agent; holds only cash and bucket-eligible tickets."""

    bucket: str = ""
    cash: float = 0.0
    inventory: List[str] = field(default_factory=list)  # ticket IDs


@dataclass
class VBTAgent(Agent):
    """Value-based trader agent for a specific bucket."""

    bucket: str = ""
    cash: float = 0.0
    inventory: List[str] = field(default_factory=list)  # ticket IDs


@dataclass
class RingTraderAgent(Agent):
    """Trader in the Kalecki ring with ticket holdings and obligations."""

    issuer_asset: str | None = None
