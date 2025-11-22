"""Dealer pricing kernel and execution logic (per bucket)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .vbt import VBTBucket


def outside_quotes(mid: float, spread: float) -> Tuple[float, float]:
    """Return (ask, bid) from mid/spread."""
    ask = mid + 0.5 * spread
    bid = mid - 0.5 * spread
    return ask, bid


@dataclass
class DealerQuotes:
    """Computed quotes and ladder stats."""

    capacity: float
    lambda_layoff: float
    inside_width: float
    midline: float
    ask: float
    bid: float
    pinned_ask: bool
    pinned_bid: bool
    outside_ask: float
    outside_bid: float


class DealerBucket:
    """Dealer state and commit-to-quote logic for a single bucket (L1 kernel)."""

    def __init__(
        self,
        bucket: str,
        ticket_size: float,
        mid: float,
        spread: float,
        cash: float,
        inventory: float,
        guard_m_min: float = 0.0,
        vbt: Optional[VBTBucket] = None,
        dealer_id: Optional[str] = None,
        vbt_id: Optional[str] = None,
    ):
        self.bucket = bucket
        self.S = float(ticket_size)
        self.mid = float(mid)
        self.spread = float(spread)
        self.cash = float(cash)
        self.inventory = float(inventory)  # face units (tickets * S)
        self.guard_m_min = float(guard_m_min)
        self.vbt = vbt
        self.dealer_id = dealer_id or bucket
        self.vbt_id = vbt_id or (vbt.bucket if vbt else None)

        # derived at recompute
        self.quotes_cache: Optional[DealerQuotes] = None

    # ---- core computations ----
    def _capacity_and_quotes(self) -> DealerQuotes:
        """Compute capacity, ladder, and inside quotes with clipping."""
        outside_ask, outside_bid = outside_quotes(self.mid, self.spread)

        # Guard: collapse to outside pins if mid too low or non-positive capacity.
        if self.mid <= self.guard_m_min:
            return DealerQuotes(
                capacity=0.0,
                lambda_layoff=1.0,
                inside_width=self.spread,
                midline=self.mid,
                ask=outside_ask,
                bid=outside_bid,
                pinned_ask=True,
                pinned_bid=True,
                outside_ask=outside_ask,
                outside_bid=outside_bid,
            )

        # Securities count (a) in tickets; inventory is face units
        a = self.inventory / self.S
        V = self.mid * a + self.cash
        K_star = int(V // self.mid)
        X_star = self.S * K_star  # one-sided capacity in face units

        if X_star <= 0:
            return DealerQuotes(
                capacity=0.0,
                lambda_layoff=1.0,
                inside_width=self.spread,
                midline=self.mid,
                ask=outside_ask,
                bid=outside_bid,
                pinned_ask=True,
                pinned_bid=True,
                outside_ask=outside_ask,
                outside_bid=outside_bid,
            )

        lam = self.S / (X_star + self.S)  # layoff probability
        inside_width = lam * self.spread

        # midline slope uses ghost points one step beyond edges
        slope = self.spread / (X_star + 2 * self.S)
        midline = self.mid - slope * (self.inventory - X_star / 2.0)

        ask = midline + 0.5 * inside_width
        bid = midline - 0.5 * inside_width

        # clipping to outside
        pinned_ask = False
        pinned_bid = False
        if ask > outside_ask:
            ask = outside_ask
            pinned_ask = True
        if bid < outside_bid:
            bid = outside_bid
            pinned_bid = True

        return DealerQuotes(
            capacity=X_star,
            lambda_layoff=lam,
            inside_width=inside_width,
            midline=midline,
            ask=ask,
            bid=bid,
            pinned_ask=pinned_ask,
            pinned_bid=pinned_bid,
            outside_ask=outside_ask,
            outside_bid=outside_bid,
        )

    def recompute(self) -> DealerQuotes:
        self.quotes_cache = self._capacity_and_quotes()
        return self.quotes_cache

    @property
    def quotes(self) -> DealerQuotes:
        if self.quotes_cache is None:
            return self.recompute()
        return self.quotes_cache

    # ---- feasibility ----
    def can_sell_one(self) -> bool:
        """Dealer sells one ticket to customer (customer BUY)."""
        q = self.quotes
        return q.capacity > 0 and self.inventory >= self.S

    def can_buy_one(self) -> bool:
        """Dealer buys one ticket from customer (customer SELL)."""
        q = self.quotes
        return q.capacity > 0 and (self.inventory + self.S) <= q.capacity and self.cash >= q.bid

    # ---- executions ----
    def execute_customer_buy(
        self,
        customer_id: str | None = None,
        dealer_id: str | None = None,
        vbt_id: str | None = None,
        bucket_id: str | None = None,
        ticket_ops=None,
    ) -> Tuple[float, bool]:
        """Customer BUYs one ticket from dealer. Returns (price, pinned).

        If ticket_ops and ids are provided, moves a concrete ticket:
        - interior: dealer -> customer
        - pass-through: VBT -> customer
        """
        q = self.recompute()

        if self.can_sell_one():
            price = q.ask
            self.inventory -= self.S
            self.cash += price
            if ticket_ops and customer_id and dealer_id and bucket_id:
                ticket_ops.customer_buy_from_dealer(customer_id, dealer_id, bucket_id)
            return price, q.pinned_ask

        # pass-through at outside ask
        price = q.outside_ask
        if self.vbt:
            self.vbt.sell_one()
        target_vbt = vbt_id or self.vbt_id
        if ticket_ops and customer_id and target_vbt and bucket_id:
            ticket_ops.pass_through_buy_from_vbt(customer_id, target_vbt, bucket_id)
        return price, True

    def execute_customer_sell(
        self,
        customer_id: str | None = None,
        dealer_id: str | None = None,
        vbt_id: str | None = None,
        bucket_id: str | None = None,
        ticket_ops=None,
    ) -> Tuple[float, bool]:
        """Customer SELLs one ticket to dealer. Returns (price, pinned).

        If ticket_ops and ids are provided, moves a concrete ticket:
        - interior: customer -> dealer
        - pass-through: customer -> VBT
        """
        q = self.recompute()

        if self.can_buy_one():
            price = q.bid
            self.inventory += self.S
            self.cash -= price
            if ticket_ops and customer_id and dealer_id and bucket_id:
                ticket_ops.customer_sell_to_dealer(customer_id, dealer_id, bucket_id)
            return price, q.pinned_bid

        # pass-through at outside bid
        price = q.outside_bid
        if self.vbt:
            self.vbt.buy_one()
        target_vbt = vbt_id or self.vbt_id
        if ticket_ops and customer_id and target_vbt and bucket_id:
            ticket_ops.pass_through_sell_to_vbt(customer_id, target_vbt, bucket_id)
        return price, True

    # ---- helpers for inventory/cash inspection ----
    def state(self) -> dict:
        q = self.quotes
        return {
            "bucket": self.bucket,
            "mid": self.mid,
            "spread": self.spread,
            "cash": self.cash,
            "inventory": self.inventory,
            "capacity": q.capacity,
            "lambda": q.lambda_layoff,
            "inside_width": q.inside_width,
            "midline": q.midline,
            "ask": q.ask,
            "bid": q.bid,
            "pinned_ask": q.pinned_ask,
            "pinned_bid": q.pinned_bid,
        }
