from __future__ import annotations

from dataclasses import dataclass, field

from bilancio.core.ids import AgentId, InstrId


@dataclass
class Agent:
    id: AgentId
    name: str
    kind: str
    asset_ids: list[InstrId] = field(default_factory=list)
    liability_ids: list[InstrId] = field(default_factory=list)
