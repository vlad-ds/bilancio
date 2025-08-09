from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from bilancio.core.ids import InstrId, AgentId

@dataclass
class Instrument:
    id: InstrId
    kind: str
    amount: int                    # minor units
    denom: str
    asset_holder_id: AgentId
    liability_issuer_id: AgentId

    def is_financial(self) -> bool:  # override if needed
        return True

    def validate_type_invariants(self) -> None:
        assert self.amount >= 0, "amount must be non-negative"
        assert self.asset_holder_id != self.liability_issuer_id, "self-counterparty forbidden"