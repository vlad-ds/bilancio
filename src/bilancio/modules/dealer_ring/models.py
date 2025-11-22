"""Core state models for dealers, VBTs, and buckets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DealerBucketState:
    """Dealer state for a single bucket."""

    bucket_name: str
    ticket_size: float
    mid: float
    spread: float
    inventory: float
    cash: float
    capacity: int
    lambda_layoff: float
    inside_width: float


@dataclass
class VBTBucketState:
    """Value-based trader state for a single bucket."""

    bucket_name: str
    ticket_size: float
    mid: float
    spread: float
    cash: float
    inventory: float
    phi_M: float
    phi_O: float
    guard_M_min: float
    clip_nonneg_bid: bool = True


@dataclass
class BucketConfig:
    """Runtime bucket parameters resolved from the config."""

    name: str
    tau_min: int
    tau_max: Optional[int]
    ticket_size: float
