from dataclasses import dataclass

from bilancio.domain.agent import Agent


@dataclass
class Dealer(Agent):
    """Dealer agent stub; dealer-ring logic sits in modules/dealer_ring."""

    def __post_init__(self):
        self.kind = "dealer"
