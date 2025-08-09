from dataclasses import dataclass
from typing import Optional
from .base import Instrument

@dataclass
class Cash(Instrument):
    # bearer CB liability; issuer is CB; holder can be anyone per policy
    def __post_init__(self):
        self.kind = "cash"

@dataclass
class BankDeposit(Instrument):
    # liability of a commercial bank; holder is typically household/firm
    def __post_init__(self):
        self.kind = "bank_deposit"

@dataclass
class ReserveDeposit(Instrument):
    # liability of the central bank; holders are banks/treasury per policy
    def __post_init__(self):
        self.kind = "reserve_deposit"