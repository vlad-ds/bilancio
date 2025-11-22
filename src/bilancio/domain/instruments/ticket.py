from dataclasses import dataclass

from .base import Instrument


@dataclass
class Ticket(Instrument):
    """Standardized zero-coupon ticket for dealer-ring trading."""

    maturity_time: int | None = None
    bucket_id: str | None = None
    serial: str | None = None

    def __post_init__(self):
        self.kind = "ticket"

    def validate_type_invariants(self) -> None:
        super().validate_type_invariants()
        assert self.maturity_time is not None and self.maturity_time >= 0, "ticket must have maturity_time"
