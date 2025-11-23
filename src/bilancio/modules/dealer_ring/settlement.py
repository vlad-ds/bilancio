"""Settlement for ticket maturities with proportional recovery and loss-rate calc."""

from __future__ import annotations

from collections import defaultdict
from typing import Tuple

from bilancio.core.atomic_tx import atomic
from bilancio.core.errors import ValidationError
from bilancio.engines.system import System


def _cash_available(system: System, agent_id: str) -> int:
    """Sum cash held by an agent (minor units)."""
    total = 0
    for cid in system.state.agents[agent_id].asset_ids:
        instr = system.state.contracts.get(cid)
        if instr and instr.kind == "cash":
            total += instr.amount
    return total


def settle_bucket_maturities(system: System, bucket_id: str, ticket_face: int) -> float:
    """Settle all tickets maturing today in a bucket. Returns loss_rate in [0,1]."""
    day = system.state.day
    # group matured tickets by issuer
    matured_by_issuer: dict[str, list[str]] = defaultdict(list)
    for cid, instr in list(system.state.contracts.items()):
        if getattr(instr, "kind", None) != "ticket":
            continue
        if getattr(instr, "bucket_id", None) != bucket_id:
            continue
        if getattr(instr, "maturity_time", None) != day:
            continue
        matured_by_issuer[instr.liability_issuer_id].append(cid)

    if not matured_by_issuer:
        return 0.0

    total_tickets = 0
    total_loss = 0.0

    for issuer, ticket_ids in matured_by_issuer.items():
        n = len(ticket_ids)
        total_due = ticket_face * n
        avail = _cash_available(system, issuer)
        R = min(1.0, avail / total_due) if total_due > 0 else 1.0

        # pay each holder proportionally; delete tickets
        with atomic(system):
            cash_before = {issuer: _cash_available(system, issuer)}
            for tid in ticket_ids:
                instr = system.state.contracts.get(tid)
                if instr is None:
                    continue
                holder = instr.asset_holder_id
                pay = int(ticket_face * R)
                if pay > 0:
                    try:
                        system.transfer_cash(issuer, holder, pay)
                    except ValidationError:
                        # if transfer fails, skip; this is a safeguard
                        pass
                # remove ticket
                if tid in system.state.agents[holder].asset_ids:
                    system.state.agents[holder].asset_ids.remove(tid)
                if tid in system.state.agents[issuer].liability_ids:
                    system.state.agents[issuer].liability_ids.remove(tid)
                system.state.contracts.pop(tid, None)
            system.log("Settlement", issuer=issuer, bucket=bucket_id, recovery=R, tickets=n, due=total_due)
            # if default, set issuer cash to zero (consume remaining cash)
            if R < 1.0:
                remaining = _cash_available(system, issuer)
                if remaining > 0:
                    try:
                        system.retire_cash(issuer, remaining)
                    except ValidationError:
                        # best effort
                        pass
            cash_after = _cash_available(system, issuer)
            # C1 cash conservation within issuer+holders on this cohort
            paid_out = sum(int(ticket_face * R) for _ in ticket_ids)
            cash_delta = (cash_after - cash_before[issuer]) + paid_out
            if abs(cash_delta) > 1e-9:
                raise AssertionError(f"Cash not conserved in settlement issuer={issuer}: delta={cash_delta}")
        total_tickets += n
        total_loss += n * (1.0 - R)

    loss_rate = total_loss / total_tickets if total_tickets else 0.0
    return loss_rate
