from dataclasses import dataclass

from .base import Instrument


@dataclass
class Payable(Instrument):
    due_day: int | None = None
    def __post_init__(self):
        self.kind = "payable"
    def validate_type_invariants(self) -> None:
        super().validate_type_invariants()
        assert self.due_day is not None and self.due_day >= 0, "payable must have due_day"
