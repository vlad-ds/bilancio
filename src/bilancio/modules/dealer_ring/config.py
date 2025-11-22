"""Config models for the dealer-ring module."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class BucketConfig(BaseModel):
    """Per-bucket parameters."""

    name: str = Field(..., description="Bucket label, e.g., short/mid/long")
    tau_range: List[int] = Field(..., description="Inclusive remaining tau range for the bucket")
    M0: float = Field(..., description="Initial mid price")
    O0: float = Field(..., description="Initial spread")
    phi_M: float = Field(..., description="Loss sensitivity for mid")
    phi_O: float = Field(..., description="Loss sensitivity for spread")
    guard_M_min: float = Field(0.0, description="Guard threshold for pinning quotes")
    clip_nonneg_bid: bool = Field(True, description="Clip outside bid to non-negative")
    Xstar_target: int = Field(0, description="Target one-sided capacity at init")


class DealerRingConfig(BaseModel):
    """Top-level dealer-ring configuration."""

    ticket_size: float = Field(1.0, description="Standard ticket face value")
    seed: int = Field(0, description="Random seed for order flow")
    buckets: List[BucketConfig] = Field(..., description="Ordered list of maturity buckets")
    pi_sell: float = Field(0.5, description="Probability an arrival is SELL side")
    N_max: int = Field(3, description="Max arrivals per period")
    invest_horizon: int = Field(3, description="Min horizon before investing (H)")
    cash_buffer: float = Field(1.0, description="Min cash buffer before investing")
    dealer_share: float = Field(0.25, description="Initial share of tickets to dealers")
    vbt_share: float = Field(0.5, description="Initial share of tickets to VBTs")
    trader_share: float = Field(0.25, description="Initial share of tickets to traders")
    stop_on_default: bool = Field(False, description="Optional stop flag on first default")
    html_export: Optional[str] = Field(None, description="Optional HTML export path")
