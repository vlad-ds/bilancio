"""Dealer-ring eligibility and bucket-selection policies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from bilancio.engines.system import System


@dataclass
class Eligibility:
    sellers: List[str]
    buyers: List[str]


def default_eligibility(system: System, cash_buffer: int = 1, horizon: int = 3) -> Eligibility:
    """Compute SELL/BUY eligibility per spec (liquidity shortfall vs. investable cash).

    SELL: shortfall > 0 and owns at least one ticket.
    BUY: earliest liability at least horizon away and cash > buffer.
    """
    sellers: List[str] = []
    buyers: List[str] = []
    day = system.state.day
    for aid, agent in system.state.agents.items():
        # tickets held?
        ticket_ids = [cid for cid in agent.asset_ids if system.state.contracts.get(cid, None) and system.state.contracts[cid].kind == "ticket"]

        # shortfall = dues today - cash
        dues_today = sum(
            c.amount for c in system.state.contracts.values()
            if getattr(c, "kind", None) == "ticket"
            and c.liability_issuer_id == aid
            and getattr(c, "maturity_time", None) == day
        )
        cash_amt = sum(
            c.amount for c in system.state.contracts.values()
            if getattr(c, "kind", None) == "cash" and c.asset_holder_id == aid
        )
        shortfall = max(0, dues_today - cash_amt)

        if shortfall > 0 and ticket_ids:
            sellers.append(aid)
        else:
            # investment check: nearest liability
            future_dues = [
                c.maturity_time for c in system.state.contracts.values()
                if getattr(c, "kind", None) == "ticket"
                and c.liability_issuer_id == aid
                and c.maturity_time is not None
                and c.maturity_time > day
            ]
            earliest = min(future_dues) if future_dues else None
            if (earliest is None or earliest - day >= horizon) and cash_amt > cash_buffer:
                buyers.append(aid)

    return Eligibility(sellers=sellers, buyers=buyers)


def bucket_pref_sell(system: System, agent_id: str, bucket_ids: List[str], buckets) -> str:
    """SELL: pick ticket with shortest remaining τ; tie-break on highest dealer bid."""
    best_bucket = None
    best_tau = None
    best_bid = None
    for bid in bucket_ids:
        tids = system.tickets_of(agent_id, bucket_id=bid)
        for tid in tids:
            instr = system.state.contracts.get(tid)
            if not instr or instr.maturity_time is None:
                continue
            tau = instr.maturity_time - system.state.day
            dealer_bid = buckets[bid].quotes.bid
            if best_tau is None or tau < best_tau or (tau == best_tau and dealer_bid > (best_bid or -1)):
                best_tau = tau
                best_bucket = bid
                best_bid = dealer_bid
    return best_bucket or bucket_ids[0]


def bucket_pref_buy(system: System, agent_id: str, ordered_buckets: List[str], buckets, vbts) -> str:
    """BUY: prefer Short->Mid->Long; skip buckets pinned ask or with no dealer/VBT inventory if possible."""
    for bid in ordered_buckets:
        dq = buckets[bid].quotes
        inv_ok = buckets[bid].inventory > 0 or vbts[bid].inventory > 0
        if not dq.pinned_ask and inv_ok:
            return bid
    # fallback any with inventory
    for bid in ordered_buckets:
        inv_ok = buckets[bid].inventory > 0 or vbts[bid].inventory > 0
        if inv_ok:
            return bid
    return ordered_buckets[0]
