from dataclasses import dataclass

from bilancio.domain.agent import Agent


@dataclass
class VBT(Agent):
    """Value-based trader agent stub; anchors live in modules/dealer_ring."""

    def __post_init__(self):
        self.kind = "vbt"
