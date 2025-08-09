from dataclasses import dataclass

from .base import Instrument


@dataclass
class Deliverable(Instrument):
    sku: str = "GENERIC"
    divisible: bool = True  # if False, amount must be whole and only full transfers allowed
    def __post_init__(self):
        self.kind = "deliverable"
    def is_financial(self) -> bool:
        return False
    def validate_type_invariants(self) -> None:
        # Override parent validation - non-financial assets can have same holder and issuer
        assert self.amount >= 0, "amount must be non-negative"
