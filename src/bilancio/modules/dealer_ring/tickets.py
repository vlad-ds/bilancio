"""Ticket instrument scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Ticket:
    """Standardized zero-coupon ticket for dealer-ring trading."""

    id: str
    issuer: str
    owner: str
    face: float
    maturity_time: int
    remaining_tau: int
    bucket_id: str
    serial: Optional[str] = None
