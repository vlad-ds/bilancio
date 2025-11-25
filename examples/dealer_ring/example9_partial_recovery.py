"""
Example 9: Partial-Recovery Default with Multiple Claimant Types (R=0.375).

From the dealer ring specification (Section 10):
A single issuer I with tickets maturing at period t. The maturing cohort is
held by three distinct claimant types: dealer D, VBT, and trader K.

Primitives:
- Ticket size (face): S = 1
- Total maturing tickets on I: N_I(t) = 8, so D_I(t) = 8
- Issuer cash before settlement: C_I(t) = 3
- Recovery rate: R_I(t) = 3/8 = 0.375 (partial recovery)

Holder composition:
- q_D = 3 (dealer holds 3 tickets)
- q_V = 2 (VBT holds 2 tickets)
- q_K = 3 (trader K holds 3 tickets)
- Total: q_D + q_V + q_K = 8

Payouts (each holder receives q * S * R):
- Dealer D: 3 * 1 * 0.375 = 1.125
- VBT: 2 * 1 * 0.375 = 0.75
- Trader K: 3 * 1 * 0.375 = 1.125

Checks:
1. Cash conservation: 1.125 + 0.75 + 1.125 = 3 (equals issuer outflow)
2. Ticket deletion: all 8 maturing tickets removed
3. Issuer cash to zero: C_I(t+) = 0 (partial recovery)
4. Type symmetry: all holders receive same per-ticket payout S*R

Usage:
    uv run python examples/dealer_ring/example9_partial_recovery.py

Output:
    examples/dealer_ring/out/example9_report.html
"""

from decimal import Decimal
from pathlib import Path

from bilancio.dealer import (
    DealerRingConfig,
    DealerRingSimulation,
    Ticket,
    TraderState,
    recompute_dealer_state,
)


def setup_example9() -> DealerRingSimulation:
    """Set up Example 9: Partial-recovery default with R=0.375."""
    config = DealerRingConfig(
        dealer_share=Decimal("1.0"),
        vbt_share=Decimal("0.0"),
        N_max=0,
        max_days=2,
        seed=42,
        vbt_anchors={
            "short": (Decimal("1.00"), Decimal("0.30")),
            "mid": (Decimal("1.00"), Decimal("0.30")),
            "long": (Decimal("1.00"), Decimal("0.30")),
        },
    )

    sim = DealerRingSimulation(config)

    # Create issuer I with limited cash (C=3, but owes 8)
    issuer = TraderState(agent_id="issuer_I", cash=Decimal("3.00"))
    sim.traders[issuer.agent_id] = issuer

    # Create trader K who holds 3 tickets
    trader_k = TraderState(agent_id="trader_K", cash=Decimal("0.00"))
    sim.traders[trader_k.agent_id] = trader_k

    # Set up dealer D with 3 maturing tickets
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("10.00")  # Starting cash

    # Create 3 tickets for dealer (q_D = 3)
    for i in range(3):
        ticket = Ticket(
            id=f"T_D{i}",
            issuer_id=issuer.agent_id,
            owner_id=dealer.agent_id,
            face=Decimal(1),
            maturity_day=sim.day + 1,  # Matures tomorrow
            remaining_tau=1,
            bucket_id="mid",
            serial=100 + i,
        )
        dealer.inventory.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

    # Set up VBT with 2 maturing tickets (q_V = 2)
    vbt = sim.vbts["mid"]
    vbt.cash = Decimal("5.00")

    for i in range(2):
        ticket = Ticket(
            id=f"T_V{i}",
            issuer_id=issuer.agent_id,
            owner_id=vbt.agent_id,
            face=Decimal(1),
            maturity_day=sim.day + 1,  # Matures tomorrow
            remaining_tau=1,
            bucket_id="mid",
            serial=200 + i,
        )
        vbt.inventory.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

    # Create 3 tickets for trader K (q_K = 3)
    for i in range(3):
        ticket = Ticket(
            id=f"T_K{i}",
            issuer_id=issuer.agent_id,
            owner_id=trader_k.agent_id,
            face=Decimal(1),
            maturity_day=sim.day + 1,  # Matures tomorrow
            remaining_tau=1,
            bucket_id="mid",
            serial=300 + i,
        )
        trader_k.tickets_owned.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def verify_initial_state(sim: DealerRingSimulation) -> dict:
    """Verify initial state and record values."""
    print("\n=== Initial State (Before Settlement) ===")

    issuer = sim.traders["issuer_I"]
    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    trader_k = sim.traders["trader_K"]

    # Count tickets
    dealer_tickets = [t for t in dealer.inventory if t.issuer_id == issuer.agent_id]
    vbt_tickets = [t for t in vbt.inventory if t.issuer_id == issuer.agent_id]
    trader_tickets = trader_k.tickets_owned

    print(f"Issuer I: cash={issuer.cash}, obligations={len(issuer.obligations)}")
    print(f"Dealer D: cash={dealer.cash}, tickets on I = {len(dealer_tickets)}")
    print(f"VBT: cash={vbt.cash}, tickets on I = {len(vbt_tickets)}")
    print(f"Trader K: cash={trader_k.cash}, tickets on I = {len(trader_tickets)}")

    total_tickets = len(dealer_tickets) + len(vbt_tickets) + len(trader_tickets)
    print(f"\nTotal maturing tickets: N_I(t) = {total_tickets}")
    print(f"Total due: D_I(t) = {total_tickets} (face S=1)")

    # Expected recovery
    R = issuer.cash / Decimal(total_tickets)
    print(f"Recovery rate: R_I(t) = {issuer.cash}/{total_tickets} = {R}")

    assert len(dealer_tickets) == 3, f"Dealer should have 3 tickets, got {len(dealer_tickets)}"
    assert len(vbt_tickets) == 2, f"VBT should have 2 tickets, got {len(vbt_tickets)}"
    assert len(trader_tickets) == 3, f"Trader K should have 3 tickets, got {len(trader_tickets)}"
    assert total_tickets == 8, f"Total should be 8 tickets, got {total_tickets}"
    assert issuer.cash == Decimal("3.00"), f"Issuer cash should be 3, got {issuer.cash}"

    print("\n✓ Initial state verified!")

    return {
        "issuer_cash": issuer.cash,
        "dealer_cash": dealer.cash,
        "vbt_cash": vbt.cash,
        "trader_cash": trader_k.cash,
        "dealer_tickets": len(dealer_tickets),
        "vbt_tickets": len(vbt_tickets),
        "trader_tickets": len(trader_tickets),
        "total_tickets": total_tickets,
        "recovery_rate": R,
    }


def run_settlement(sim: DealerRingSimulation) -> None:
    """Run settlement by advancing the day."""
    print("\n=== Settlement Phase ===")

    # Advance to day 1 (maturity day)
    sim.day = 1
    sim.events.log_day_start(1)
    sim._update_maturities()
    sim._rebucket_tickets()

    # Process settlements
    sim._settle_maturing_debt()

    print("Settlement processed.")


def verify_settlement(sim: DealerRingSimulation, before: dict) -> None:
    """Verify settlement results match specification."""
    print("\n=== Settlement Verification ===")

    issuer = sim.traders["issuer_I"]
    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    trader_k = sim.traders["trader_K"]

    R = before["recovery_rate"]  # 3/8 = 0.375

    # Expected payouts
    expected_dealer_payout = 3 * 1 * R  # q_D * S * R = 1.125
    expected_vbt_payout = 2 * 1 * R      # q_V * S * R = 0.75
    expected_trader_payout = 3 * 1 * R   # q_K * S * R = 1.125

    print(f"Expected payouts (q * S * R = q * 0.375):")
    print(f"  Dealer D: 3 * 0.375 = {expected_dealer_payout}")
    print(f"  VBT: 2 * 0.375 = {expected_vbt_payout}")
    print(f"  Trader K: 3 * 0.375 = {expected_trader_payout}")

    # Actual changes
    dealer_delta = dealer.cash - before["dealer_cash"]
    vbt_delta = vbt.cash - before["vbt_cash"]
    trader_delta = trader_k.cash - before["trader_cash"]

    print(f"\nActual cash changes:")
    print(f"  Dealer D: {before['dealer_cash']} -> {dealer.cash} (delta = {dealer_delta})")
    print(f"  VBT: {before['vbt_cash']} -> {vbt.cash} (delta = {vbt_delta})")
    print(f"  Trader K: {before['trader_cash']} -> {trader_k.cash} (delta = {trader_delta})")

    # Allow small tolerance for decimal arithmetic
    tolerance = Decimal("0.0001")

    # 1. Cash conservation
    total_payout = dealer_delta + vbt_delta + trader_delta
    assert abs(total_payout - before["issuer_cash"]) < tolerance, \
        f"Total payout {total_payout} should equal issuer cash {before['issuer_cash']}"
    print(f"\n✓ Check 1: Cash conservation - total payout = {total_payout} = issuer cash outflow")

    # 2. Ticket deletion
    dealer_remaining = [t for t in dealer.inventory if t.issuer_id == issuer.agent_id and t.remaining_tau <= 0]
    vbt_remaining = [t for t in vbt.inventory if t.issuer_id == issuer.agent_id and t.remaining_tau <= 0]
    trader_remaining = [t for t in trader_k.tickets_owned if t.issuer_id == issuer.agent_id and t.remaining_tau <= 0]

    # All matured tickets should be deleted
    assert len(dealer_remaining) == 0, f"Dealer should have 0 matured tickets, got {len(dealer_remaining)}"
    assert len(vbt_remaining) == 0, f"VBT should have 0 matured tickets, got {len(vbt_remaining)}"
    assert len(trader_remaining) == 0, f"Trader should have 0 matured tickets, got {len(trader_remaining)}"
    print(f"✓ Check 2: Ticket deletion - all 8 matured tickets removed")

    # 3. Issuer cash to zero
    assert issuer.cash == Decimal("0"), f"Issuer cash should be 0 after partial recovery, got {issuer.cash}"
    print(f"✓ Check 3: Issuer cash to zero - C_I(t+) = {issuer.cash}")

    # 4. Type symmetry (per-ticket payout is same for all)
    per_ticket_dealer = dealer_delta / 3
    per_ticket_vbt = vbt_delta / 2
    per_ticket_trader = trader_delta / 3

    assert abs(per_ticket_dealer - per_ticket_vbt) < tolerance, \
        f"Per-ticket payout differs: dealer={per_ticket_dealer}, vbt={per_ticket_vbt}"
    assert abs(per_ticket_dealer - per_ticket_trader) < tolerance, \
        f"Per-ticket payout differs: dealer={per_ticket_dealer}, trader={per_ticket_trader}"
    assert abs(per_ticket_dealer - R) < tolerance, \
        f"Per-ticket payout {per_ticket_dealer} should equal R={R}"
    print(f"✓ Check 4: Type symmetry - per-ticket payout S*R = {R} for all holders")

    print("\n✓ All settlement checks passed!")


def main():
    sim = setup_example9()
    sim._capture_snapshot()

    print("Example 9: Partial-Recovery Default (R=0.375)")
    print("=" * 60)

    before = verify_initial_state(sim)
    run_settlement(sim)
    verify_settlement(sim, before)

    # Log final state
    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    recompute_dealer_state(dealer, vbt, sim.params)

    sim.events.log_quote(
        day=1,
        bucket="mid",
        dealer_bid=dealer.bid,
        dealer_ask=dealer.ask,
        vbt_bid=vbt.B,
        vbt_ask=vbt.A,
        inventory=dealer.a,
        capacity=dealer.X_star,
        is_pinned_bid=dealer.is_pinned_bid,
        is_pinned_ask=dealer.is_pinned_ask,
    )

    sim._capture_snapshot()

    # Export HTML report
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example9_report.html"

    sim.to_html(
        out_path,
        title="Example 9: Partial-Recovery Default (R=0.375)",
        subtitle="Multiple claimant types: Dealer (3), VBT (2), Trader (3)",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 9 checks passed!")


if __name__ == "__main__":
    main()
