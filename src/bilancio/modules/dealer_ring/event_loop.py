"""Per-period event loop for dealer ring (rebucket -> quotes -> arrivals -> settlement -> anchors)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, List, Optional, Callable

from .kernel import DealerBucket
from .vbt import VBTBucket
from .ticket_ops import TicketOps
from .settlement import settle_bucket_maturities
from .policy import Eligibility, bucket_pref_sell, bucket_pref_buy


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
    bucket_ranges: list[tuple[str, int, int | None]] | None = None,
) -> List[ArrivalResult]:
    """Run a single period: rebucket -> arrivals -> settlement -> anchor update.

    - eligible_fn(system) -> Eligibility lists of seller/buyer agent ids
    - buckets: dealer bucket objects keyed by bucket name
    - vbts: VBT bucket objects keyed by bucket name
    """
    arrivals: List[ArrivalResult] = []

    # Rebucketing step: move tickets to new bucket by remaining tau
    if bucket_ranges:
        day = system.state.day
        # build lookup by bucket_id -> (min,max)
        ranges = bucket_ranges
        def _find_bucket(tau: int) -> str | None:
            for bid, lo, hi in ranges:
                if tau >= lo and (hi is None or tau <= hi):
                    return bid
            return None

        for cid, instr in list(system.state.contracts.items()):
            if getattr(instr, "kind", None) != "ticket":
                continue
            tau = instr.maturity_time - day if instr.maturity_time is not None else None
            if tau is None:
                continue
            new_bucket = _find_bucket(tau)
            if new_bucket is None or new_bucket == instr.bucket_id:
                continue
            owner = instr.asset_holder_id
            owner_kind = system.state.agents[owner].kind
            # dealer/VBT internal sale at new bucket mid
            if owner_kind == "dealer":
                old_dealer = buckets.get(instr.bucket_id)
                new_dealer = buckets.get(new_bucket)
                if old_dealer and new_dealer:
                    mid_price = new_dealer.mid
                    old_dealer.cash += mid_price
                    old_dealer.inventory -= ticket_size
                    new_dealer.cash -= mid_price
                    new_dealer.inventory += ticket_size
                    ticket_ops.system.transfer_ticket(cid, owner, new_dealer.dealer_id)
            elif owner_kind == "vbt":
                old_vbt = vbts.get(instr.bucket_id)
                new_vbt = vbts.get(new_bucket)
                if old_vbt and new_vbt:
                    mid_price = new_vbt.mid
                    old_vbt.cash += mid_price
                    old_vbt.inventory -= 1.0
                    new_vbt.cash -= mid_price
                    new_vbt.inventory += 1.0
                    ticket_ops.system.transfer_ticket(cid, owner, new_vbt.bucket)
            else:
                # trader: relabel only
                ticket_ops.system.rebucket_ticket(cid, new_bucket_id=new_bucket)
    sellers = list(eligible_fn(system).sellers)
    buyers = list(eligible_fn(system).buyers)

    n = 1
    while n <= N_max and (sellers or buyers):
        z = random.random() < pi_sell
        side = "SELL" if z else "BUY"

        if side == "SELL":
            if sellers:
                agent_id = random.choice(sellers)
                if bucket_selector:
                    bucket_id = bucket_selector(agent_id, list(buckets.keys()), "SELL")
                else:
                    bucket_id = bucket_pref_sell(system, agent_id, list(buckets.keys()), buckets)
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
                if bucket_selector:
                    bucket_id = bucket_selector(agent_id, list(buckets.keys()), "BUY")
                else:
                    bucket_id = bucket_pref_buy(system, agent_id, list(buckets.keys()), buckets)
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
