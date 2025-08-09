from dataclasses import dataclass
from .base import Instrument

@dataclass
class Deliverable(Instrument):
    # non-financial deliverable; still modeled as a contract for uniformity
    def __post_init__(self):
        self.kind = "deliverable"
    def is_financial(self) -> bool:
        return False