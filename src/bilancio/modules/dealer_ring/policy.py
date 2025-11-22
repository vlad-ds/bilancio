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


def bucket_pref(agent_id: str, bucket_ids: List[str], side: str) -> str:
    """Bucket selection policy stub: pick the first bucket. Extend with shortest maturity/highest bid."""
    return bucket_ids[0]
