from dataclasses import dataclass
from bilancio.domain.agent import Agent

@dataclass
class Treasury(Agent):
    def __post_init__(self):
        self.kind = "treasury"