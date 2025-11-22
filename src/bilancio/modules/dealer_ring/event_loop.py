"""Per-period event loop for dealer ring (rebucket -> quotes -> arrivals -> settlement -> anchors)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, List, Optional, Callable

from .kernel import DealerBucket
from .vbt import VBTBucket
from .ticket_ops import TicketOps
from .settlement import settle_bucket_maturities
from .policy import Eligibility


@dataclass
class ArrivalResult:
    executed: bool
    side: str
    price: Optional[float] = None
    pinned: bool = False
    agent_id: Optional[str] = None
    bucket: Optional[str] = None


@dataclass
class Eligibility:
    sellers: list[str]
    buyers: list[str]


def run_period(
    system: Any,
    buckets: dict[str, DealerBucket],
    vbts: dict[str, VBTBucket],
    ticket_ops: TicketOps,
    pi_sell: float,
    N_max: int,
    eligible_fn: Callable[[Any], Eligibility],
    bucket_selector: Callable[[str, list[str], str], str] | None = None,
    ticket_size: int = 1,
) -> List[ArrivalResult]:
    """Run a single period: rebucket -> arrivals -> settlement -> anchor update.

    - eligible_fn(system) -> Eligibility lists of seller/buyer agent ids
    - buckets: dealer bucket objects keyed by bucket name
    - vbts: VBT bucket objects keyed by bucket name
    """
    arrivals: List[ArrivalResult] = []
    sellers = list(eligible_fn(system).sellers)
    buyers = list(eligible_fn(system).buyers)

    n = 1
    while n <= N_max and (sellers or buyers):
        z = random.random() < pi_sell
        side = "SELL" if z else "BUY"

        if side == "SELL":
            if sellers:
                agent_id = random.choice(sellers)
                bucket_id = bucket_selector(agent_id, list(buckets.keys()), "SELL") if bucket_selector else next(iter(buckets.keys()))
                dealer = buckets[bucket_id]
                vbt = vbts[bucket_id]
                price, pinned = dealer.execute_customer_sell(
                    customer_id=agent_id,
                    dealer_id=dealer.bucket,
                    vbt_id=vbt.bucket,
                    bucket_id=bucket_id,
                    ticket_ops=ticket_ops,
                )
                arrivals.append(ArrivalResult(True, "SELL", price, pinned, agent_id, bucket_id))
                sellers = [s for s in sellers if s != agent_id]
            elif buyers:
                # fallback to BUY
                side = "BUY"
            else:
                break

        if side == "BUY":
            if buyers:
                agent_id = random.choice(buyers)
                bucket_id = bucket_selector(agent_id, list(buckets.keys()), "BUY") if bucket_selector else next(iter(buckets.keys()))
                dealer = buckets[bucket_id]
                vbt = vbts[bucket_id]
                price, pinned = dealer.execute_customer_buy(
                    customer_id=agent_id,
                    dealer_id=dealer.bucket,
                    vbt_id=vbt.bucket,
                    bucket_id=bucket_id,
                    ticket_ops=ticket_ops,
                )
                arrivals.append(ArrivalResult(True, "BUY", price, pinned, agent_id, bucket_id))
                buyers = [b for b in buyers if b != agent_id]
            elif sellers:
                # fallback to SELL
                continue
            else:
                break

        n += 1

    # Settlement with proportional recovery per bucket
    loss_rates: dict[str, float] = {}
    for bucket_id in buckets.keys():
        loss_rates[bucket_id] = settle_bucket_maturities(system, bucket_id=bucket_id, ticket_face=ticket_size)

    # VBT anchor updates using bucket loss rates
    for bucket_id, vbt in vbts.items():
        lr = loss_rates.get(bucket_id, 0.0)
        vbt.update_anchors(lr)
        # sync dealer outside quotes from VBT mid/spread
        if bucket_id in buckets:
            dealer = buckets[bucket_id]
            dealer.mid = vbt.mid
            dealer.spread = vbt.spread
            dealer.recompute()

    return arrivals
