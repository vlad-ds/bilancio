"""Per-period event loop scaffold for the dealer ring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ArrivalResult:
    """Result of processing a single arrival."""

    executed: bool
    side: str
    price: Optional[float] = None
    pinned: bool = False


def run_period(system: Any, config: Any) -> List[ArrivalResult]:
    """Placeholder loop; to be filled with spec-compliant stages."""
    # TODO: implement stages: rebucketing, precompute, eligibility, arrivals, settlement, anchor update
    return []
