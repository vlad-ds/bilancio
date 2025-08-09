from dataclasses import dataclass
from bilancio.domain.agent import Agent

@dataclass
class CentralBank(Agent):
    def __post_init__(self):
        self.kind = "central_bank"