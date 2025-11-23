"""Bootstrap helpers: ticketize payables, allocate holdings, seed dealer/VBT cash."""

from __future__ import annotations

import random
from typing import Iterable, List, Tuple

from bilancio.engines.system import System
from bilancio.core.errors import ValidationError


def compute_bucket_id(tau: int, bucket_ranges: List[Tuple[str, int, int | None]]) -> str | None:
    for bid, lo, hi in bucket_ranges:
        if tau >= lo and (hi is None or tau <= hi):
            return bid
    return None


def ticketize_payables(
    system: System,
    bucket_ranges: List[Tuple[str, int, int | None]],
    ticket_size: int,
    remove_payables: bool = False,
) -> List[str]:
    """
    Convert payables into tickets by bucket; returns created ticket IDs.

    - bucket_ranges: list of (bucket_id, tau_min, tau_max or None)
    - ticket_size: face per ticket (must divide payable amount)
    """
    created: List[str] = []
    day = system.state.day
    for cid, instr in list(system.state.contracts.items()):
        if getattr(instr, "kind", None) != "payable":
            continue
        amount = instr.amount
        if amount % ticket_size != 0:
            raise ValidationError(f"payable {cid} amount {amount} not divisible by ticket_size {ticket_size}")
        n = amount // ticket_size
        tau = instr.due_day - day if getattr(instr, "due_day", None) is not None else 0
        bucket_id = compute_bucket_id(tau, bucket_ranges)
        if bucket_id is None:
            raise ValidationError(f"no bucket for tau={tau}")
        for _ in range(n):
            tid = system.create_ticket(
                issuer_id=instr.liability_issuer_id,
                owner_id=instr.asset_holder_id,
                face=ticket_size,
                maturity_time=instr.due_day,
                bucket_id=bucket_id,
            )
            created.append(tid)
        if remove_payables:
            # remove payable contract
            holder = system.state.agents[instr.asset_holder_id]
            issuer = system.state.agents[instr.liability_issuer_id]
            if cid in holder.asset_ids:
                holder.asset_ids.remove(cid)
            if cid in issuer.liability_ids:
                issuer.liability_ids.remove(cid)
            system.state.contracts.pop(cid, None)
    return created


def allocate_tickets(
    system: System,
    bucket_id: str,
    dealer_id: str,
    vbt_id: str,
    dealer_share: float = 0.25,
    vbt_share: float = 0.5,
) -> None:
    """Reassign tickets in a bucket: dealer_share to dealer, vbt_share to VBT, remainder stays."""
    tids = sorted(
        [cid for cid, instr in system.state.contracts.items() if getattr(instr, "kind", None) == "ticket" and getattr(instr, "bucket_id", None) == bucket_id]
    )
    total = len(tids)
    n_dealer = int(total * dealer_share)
    n_vbt = int(total * vbt_share)
    dealer_tids = tids[:n_dealer]
    vbt_tids = tids[n_dealer:n_dealer + n_vbt]
    for tid in dealer_tids:
        owner = system.state.contracts[tid].asset_holder_id
        if owner != dealer_id:
            system.transfer_ticket(tid, from_agent_id=owner, to_agent_id=dealer_id)
    for tid in vbt_tids:
        owner = system.state.contracts[tid].asset_holder_id
        if owner != vbt_id:
            system.transfer_ticket(tid, from_agent_id=owner, to_agent_id=vbt_id)


def seed_dealer_vbt_cash(
    system: System,
    dealer_id: str,
    vbt_id: str,
    mid: float,
    X_target: int,
    ticket_size: int,
    cb_id: str | None = None,
) -> None:
    """Seed dealer and VBT with mid-shelf cash matching inventory target (X_target/2)."""
    cb = cb_id or next((aid for aid, a in system.state.agents.items() if a.kind == "central_bank"), None)
    if not cb:
        raise ValidationError("CentralBank must exist to mint cash")
    half_inventory_tickets = X_target // 2
    cash_needed = int(mid * half_inventory_tickets * ticket_size)
    for agent_id in (dealer_id, vbt_id):
        if cash_needed > 0:
            system.mint_cash(agent_id, cash_needed)
