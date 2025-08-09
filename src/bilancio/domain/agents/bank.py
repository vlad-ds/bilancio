from dataclasses import dataclass
from bilancio.domain.agent import Agent

@dataclass
class Bank(Agent):
    def __post_init__(self):
        self.kind = "bank"