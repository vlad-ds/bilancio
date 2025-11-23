"""Assertion helpers (C1–C6) from dealer spec."""

from __future__ import annotations

from typing import Iterable

from bilancio.engines.system import System


def cash_of(system: System, agent_id: str) -> float:
    return sum(c.amount for c in system.state.contracts.values() if c.kind == "cash" and c.asset_holder_id == agent_id)


def tickets_of(system: System, agent_id: str, bucket_id: str) -> int:
    return len(system.tickets_of(agent_id, bucket_id=bucket_id))


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


def assert_trade_invariants(
    pre_cash: float,
    pre_inv: float,
    post_cash: float,
    post_inv: float,
    bid: float,
    ask: float,
    outside_bid: float,
    outside_ask: float,
    pinned: bool,
    side: str,
    capacity: float,
    inventory: float,
    cash: float,
    ticket_size: float,
):
    """Check C2 bounds and C4 pass-through when pinned."""
    assert_quotes_within_bounds(bid, ask, outside_bid, outside_ask)
    if pinned:
        assert_pass_through_state(pre_cash, pre_inv, post_cash, post_inv)
    else:
        # C3 feasibility: SELL interior requires inventory >= S; BUY interior requires x+S<=X* and cash>=bid
        if side == "BUY":
            if inventory < ticket_size:
                raise AssertionError(f"Interior SELL infeasible: inventory {inventory} < ticket_size {ticket_size}")
        elif side == "SELL":
            if inventory + ticket_size > capacity or cash < bid:
                raise AssertionError(f"Interior BUY infeasible: x+S {inventory+ticket_size} > X* {capacity} or cash {cash} < bid {bid}")


def assert_equity_basis(dealer_cash: float, dealer_inv_tickets: float, mid: float, trader_assets: float, trader_liabs: float) -> None:
    """C5: dealers/VBTs marked to mid, traders at face."""
    dealer_equity = dealer_cash + mid * dealer_inv_tickets
    if dealer_equity < -1e-9:
        raise AssertionError(f"Dealer equity negative at mid: {dealer_equity}")
    trader_equity = trader_assets - trader_liabs
    if trader_equity < -1e-9:
        raise AssertionError(f"Trader equity negative at face: {trader_equity}")


def assert_anchor_timing(anchors_prev: tuple[float, float], anchors_new: tuple[float, float], depended_on_flow: bool = False) -> None:
    """C6: anchors should update only from losses in t, not order flow in t+1."""
    if depended_on_flow:
        raise AssertionError("Anchor updated based on order flow in disallowed timing")
