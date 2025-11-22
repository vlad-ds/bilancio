"""Assertion helpers (C1–C6) from dealer spec."""

from __future__ import annotations

from typing import Iterable

from bilancio.engines.system import System


def assert_double_entry_cash(system: System, party_ids: Iterable[str], eps: float = 1e-10) -> None:
    """C1: sum of cash deltas across parties ~= 0."""
    total = 0.0
    for pid in party_ids:
        cash = sum(c.amount for c in system.state.contracts.values() if c.kind == "cash" and c.asset_holder_id == pid)
        total += cash
    if abs(total) > eps:
        raise AssertionError(f"Cash not conserved across parties {party_ids}: total={total}")


def assert_ticket_conservation(system: System, party_ids: Iterable[str], bucket_id: str, eps: float = 0.0) -> None:
    """C1: sum of ticket counts across parties ~= 0 (by bucket)."""
    total = 0
    for pid in party_ids:
        total += len(system.tickets_of(pid, bucket_id=bucket_id))
    if abs(total) > eps:
        raise AssertionError(f"Tickets not conserved for bucket={bucket_id}, parties={party_ids}: total={total}")


def assert_quotes_within_bounds(bid: float, ask: float, outside_bid: float, outside_ask: float) -> None:
    """C2: bid>=B, ask<=A."""
    if bid < outside_bid - 1e-12:
        raise AssertionError(f"Bid below outside bid: {bid} < {outside_bid}")
    if ask > outside_ask + 1e-12:
        raise AssertionError(f"Ask above outside ask: {ask} > {outside_ask}")


def assert_pass_through_state(dealer_cash: float, dealer_inv: float, dealer_cash_after: float, dealer_inv_after: float) -> None:
    """C4: pass-through leaves dealer state unchanged."""
    if abs(dealer_cash_after - dealer_cash) > 1e-12 or abs(dealer_inv_after - dealer_inv) > 1e-12:
        raise AssertionError("Dealer state changed on pass-through pin")
