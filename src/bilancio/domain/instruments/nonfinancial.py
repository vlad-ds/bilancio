from dataclasses import dataclass
from decimal import Decimal

from .base import Instrument


@dataclass
class Deliverable(Instrument):
    sku: str = "GENERIC"
    divisible: bool = True  # if False, amount must be whole and only full transfers allowed
    unit_price: Decimal | None = None  # per-unit monetary value
    def __post_init__(self):
        self.kind = "deliverable"
    
    def is_financial(self) -> bool:
        return False
    
    @property
    def valued_amount(self) -> Decimal | None:
        """Returns the monetary value (amount * unit_price) when price is set, or None if no price."""
        if self.unit_price is None:
            return None
        return self.amount * self.unit_price
    
    def validate_type_invariants(self) -> None:
        # Override parent validation - non-financial assets can have same holder and issuer
        assert self.amount >= 0, "amount must be non-negative"
