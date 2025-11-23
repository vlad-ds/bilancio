"""Value-based trader (VBT) anchor logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


def _clip_zero(x: float) -> float:
    return x if x >= 0 else 0.0


@dataclass
class VBTBucket:
    """Per-bucket value-based trader with outside quotes and loss-based anchor updates.

    The VBT provides effectively infinite depth at its outside bid/ask. Inventory is tracked
    but not used for feasibility; it can go negative if we choose to allow unlimited supply.
    """

    bucket: str
    ticket_size: float
    mid: float
    spread: float
    phi_M: float
    phi_O: float
    guard_M_min: float = 0.0
    clip_nonneg_bid: bool = True
    cash: float = 0.0
    inventory: float = 0.0  # measured in tickets (face units / ticket_size)
    agent_id: str | None = None

    def quotes(self) -> Tuple[float, float]:
        """Return (ask, bid) applying optional non-negative bid clip."""
        ask = self.mid + 0.5 * self.spread
        bid = self.mid - 0.5 * self.spread
        if self.clip_nonneg_bid and bid < 0:
            bid = 0.0
        return ask, bid

    def update_anchors(self, loss_rate: float) -> None:
        """Apply the loss-based rule M_{t+1}, O_{t+1} from the spec."""
        # Guard: keep loss_rate in [0,1]
        lr = max(0.0, min(1.0, loss_rate))
        self.mid = max(self.guard_M_min, self.mid - self.phi_M * lr)
        self.spread = self.spread + self.phi_O * lr
        # No O_min here; clip non-negative bid via quotes() if enabled

    def buy_one(self) -> float:
        """VBT buys one ticket at its outside bid; returns executed price."""
        ask, bid = self.quotes()
        price = bid
        self.cash -= price
        self.inventory += 1.0
        return price

    def sell_one(self) -> float:
        """VBT sells one ticket at its outside ask; returns executed price."""
        ask, bid = self.quotes()
        price = ask
        self.cash += price
        self.inventory -= 1.0
        return price
