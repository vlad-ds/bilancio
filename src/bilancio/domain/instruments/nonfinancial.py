from dataclasses import dataclass
from decimal import Decimal

from .base import Instrument


@dataclass
class Deliverable(Instrument):
    sku: str = "GENERIC"
    divisible: bool = True  # if False, amount must be whole and only full transfers allowed
    unit_price: Decimal = Decimal("0")  # Required monetary value per unit
    due_day: int | None = None  # Optional temporal obligation: day when deliverable must be transferred to creditor. 
                                # When set, the settlement engine will automatically transfer goods on the specified day.
                                # Must be non-negative. None means no temporal obligation.
    
    def __post_init__(self):
        self.kind = "deliverable"
        # Ensure unit_price is a Decimal
        if not isinstance(self.unit_price, Decimal):
            self.unit_price = Decimal(str(self.unit_price))
    
    def is_financial(self) -> bool:
        return False
    
    @property
    def valued_amount(self) -> Decimal:
        """Returns the monetary value (amount * unit_price)."""
        return Decimal(str(self.amount)) * self.unit_price
    
    def validate_type_invariants(self) -> None:
        # Override parent validation - non-financial assets can have same holder and issuer
        assert self.amount >= 0, "amount must be non-negative"
        assert self.unit_price >= 0, "unit_price must be non-negative"
        # Validate due_day if provided
        if self.due_day is not None:
            assert self.due_day >= 0, "due_day must be non-negative if provided"
