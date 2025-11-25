"""
Example 11: Partial-Recovery Default with Multiple Claimant Types (R=0.6).

From the dealer ring specification (Section 12):
Tests proportional recovery settlement when a single issuer defaults and
multiple claimant types (dealer D, VBT, trader K) hold maturing tickets.

Setup:
- Ticket size S = 1
- Issuer I with N_I(t) = 5 maturing tickets, C_I(t) = 3
- Recovery rate R = C_I(t) / D_I(t) = 3/5 = 0.6
- Holder composition: q_D = 2, q_VBT = 2, q_K = 1

Settlement with proportional recovery R = 0.6:
- Dealer D: q_D * S * R = 2 * 1 * 0.6 = 1.2
- VBT: q_VBT * S * R = 2 * 1 * 0.6 = 1.2
- Trader K: q_K * S * R = 1 * 1 * 0.6 = 0.6

After settlement:
- Issuer cash: 3 - 0.6*5 = 0
- All 5 maturing tickets deleted
- Default recorded with R = 0.6

Harness checks:
1. Cash conservation: total paid = 1.2 + 1.2 + 0.6 = 3 = R * D_I(t)
2. Ticket deletion: all 5 maturing tickets removed
3. Issuer cash to zero: C_I(t+) = 0
4. Type symmetry: all holders receive same per-ticket payout S*R = 0.6

Usage:
    uv run python examples/dealer_ring/example11_partial_recovery.py

Output:
    examples/dealer_ring/out/example11_report.html
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


def setup_example11() -> DealerRingSimulation:
    """Set up Example 9: Partial-recovery default with multiple claimants."""
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
        enable_vbt_anchor_updates=False,  # Test settlement in isolation
    )

    sim = DealerRingSimulation(config)

    # Create issuer with cash = 3 (will partially default on 5 tickets)
    issuer = TraderState(
        agent_id="issuer_I",
        cash=Decimal("3.00"),
    )
    sim.traders[issuer.agent_id] = issuer

    # Create trader K
    trader_k = TraderState(
        agent_id="trader_K",
        cash=Decimal("0.00"),
    )
    sim.traders[trader_k.agent_id] = trader_k

    # Get dealer and VBT
    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    # Set up initial cash for dealer and VBT
    dealer.cash = Decimal("5.00")
    vbt.cash = Decimal("10.00")

    # Create tickets - q_D = 2 for dealer
    for i in range(2):
        ticket = Ticket(
            id=f"D{i}",
            issuer_id=issuer.agent_id,
            owner_id=dealer.agent_id,
            face=Decimal(1),
            maturity_day=1,  # Matures at day 1
            remaining_tau=6,
            bucket_id="mid",
            serial=i,
        )
        dealer.inventory.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

    # Create tickets - q_VBT = 2 for VBT
    for i in range(2):
        ticket = Ticket(
            id=f"V{i}",
            issuer_id=issuer.agent_id,
            owner_id=vbt.agent_id,
            face=Decimal(1),
            maturity_day=1,  # Matures at day 1
            remaining_tau=6,
            bucket_id="mid",
            serial=10 + i,
        )
        vbt.inventory.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

    # Create ticket - q_K = 1 for trader K
    ticket = Ticket(
        id="K0",
        issuer_id=issuer.agent_id,
        owner_id=trader_k.agent_id,
        face=Decimal(1),
        maturity_day=1,  # Matures at day 1
        remaining_tau=6,
        bucket_id="mid",
        serial=20,
    )
    trader_k.tickets_owned.append(ticket)
    sim.all_tickets[ticket.id] = ticket
    issuer.obligations.append(ticket)

    # Recompute dealer state
    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def verify_initial_state(sim: DealerRingSimulation) -> None:
    """Verify initial state before settlement."""
    print("\n=== Initial State (Before Settlement) ===")

    issuer = sim.traders["issuer_I"]
    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    trader_k = sim.traders["trader_K"]

    print(f"Issuer I: cash={issuer.cash}, obligations={len(issuer.obligations)}")
    print(f"Dealer D: cash={dealer.cash}, inventory={len(dealer.inventory)}")
    print(f"VBT: cash={vbt.cash}, inventory={len(vbt.inventory)}")
    print(f"Trader K: cash={trader_k.cash}, tickets={len(trader_k.tickets_owned)}")

    # Count maturing tickets
    maturing = [t for t in sim.all_tickets.values() if t.maturity_day == 1]
    total_due = sum(t.face for t in maturing)
    expected_R = issuer.cash / total_due

    print(f"\nMaturing at day 1:")
    print(f"  Total tickets: {len(maturing)}")
    print(f"  Total due: {total_due}")
    print(f"  Issuer cash: {issuer.cash}")
    print(f"  Recovery rate R = {issuer.cash}/{total_due} = {expected_R}")

    # Verify setup
    assert len(issuer.obligations) == 5, f"Issuer should have 5 obligations"
    assert issuer.cash == Decimal("3.00"), f"Issuer cash should be 3"
    assert len(dealer.inventory) == 2, f"Dealer should have 2 tickets"
    assert len([t for t in vbt.inventory if t.issuer_id == issuer.agent_id]) == 2, \
        f"VBT should have 2 tickets from issuer"
    assert len(trader_k.tickets_owned) == 1, f"Trader K should have 1 ticket"

    print("\n✓ Initial state verified!")


def run_settlement(sim: DealerRingSimulation) -> dict:
    """Run settlement and return results."""
    print("\n=== Settlement Phase ===")

    # Record state before settlement
    issuer = sim.traders["issuer_I"]
    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    trader_k = sim.traders["trader_K"]

    before = {
        "issuer_cash": issuer.cash,
        "dealer_cash": dealer.cash,
        "dealer_inv": len(dealer.inventory),
        "vbt_cash": vbt.cash,
        "vbt_inv": len(vbt.inventory),
        "trader_cash": trader_k.cash,
        "trader_inv": len(trader_k.tickets_owned),
        "total_tickets": len(sim.all_tickets),
    }

    print(f"Before settlement:")
    print(f"  Issuer cash: {before['issuer_cash']}")
    print(f"  Dealer: cash={before['dealer_cash']}, inv={before['dealer_inv']}")
    print(f"  VBT: cash={before['vbt_cash']}, inv={before['vbt_inv']}")
    print(f"  Trader K: cash={before['trader_cash']}, inv={before['trader_inv']}")

    # Run day 1 (includes settlement)
    sim.day = 1
    sim.events.log_day_start(1)
    sim._settle_maturing_debt()

    # Record state after settlement
    after = {
        "issuer_cash": issuer.cash,
        "dealer_cash": dealer.cash,
        "dealer_inv": len(dealer.inventory),
        "vbt_cash": vbt.cash,
        "vbt_inv": len(vbt.inventory),
        "trader_cash": trader_k.cash,
        "trader_inv": len(trader_k.tickets_owned),
        "total_tickets": len([t for t in sim.all_tickets.values() if t.maturity_day != 1]),
    }

    print(f"\nAfter settlement:")
    print(f"  Issuer cash: {after['issuer_cash']}")
    print(f"  Dealer: cash={after['dealer_cash']}, inv={after['dealer_inv']}")
    print(f"  VBT: cash={after['vbt_cash']}, inv={after['vbt_inv']}")
    print(f"  Trader K: cash={after['trader_cash']}, inv={after['trader_inv']}")

    return {"before": before, "after": after}


def verify_settlement(sim: DealerRingSimulation, results: dict) -> None:
    """Verify settlement results match specification."""
    print("\n=== Settlement Verification ===")

    before = results["before"]
    after = results["after"]

    # Expected values
    R = Decimal("0.6")  # Recovery rate = 3/5
    S = Decimal("1")    # Ticket face

    # Expected payouts
    expected_dealer_payout = 2 * S * R  # 1.2
    expected_vbt_payout = 2 * S * R     # 1.2
    expected_trader_payout = 1 * S * R  # 0.6
    expected_total_paid = 5 * S * R     # 3.0

    print(f"Expected recovery rate R = {R}")
    print(f"Expected payouts:")
    print(f"  Dealer D: q_D * S * R = 2 * 1 * 0.6 = {expected_dealer_payout}")
    print(f"  VBT: q_VBT * S * R = 2 * 1 * 0.6 = {expected_vbt_payout}")
    print(f"  Trader K: q_K * S * R = 1 * 1 * 0.6 = {expected_trader_payout}")

    # Verify issuer cash to zero
    assert after["issuer_cash"] == Decimal("0"), \
        f"Issuer cash should be 0, got {after['issuer_cash']}"
    print(f"\n✓ Issuer cash to zero: {after['issuer_cash']}")

    # Verify dealer payout
    dealer_gain = after["dealer_cash"] - before["dealer_cash"]
    assert abs(dealer_gain - expected_dealer_payout) < Decimal("0.0001"), \
        f"Dealer should gain {expected_dealer_payout}, got {dealer_gain}"
    print(f"✓ Dealer payout: +{dealer_gain} (expected {expected_dealer_payout})")

    # Verify VBT payout
    vbt_gain = after["vbt_cash"] - before["vbt_cash"]
    assert abs(vbt_gain - expected_vbt_payout) < Decimal("0.0001"), \
        f"VBT should gain {expected_vbt_payout}, got {vbt_gain}"
    print(f"✓ VBT payout: +{vbt_gain} (expected {expected_vbt_payout})")

    # Verify trader K payout
    trader_gain = after["trader_cash"] - before["trader_cash"]
    assert abs(trader_gain - expected_trader_payout) < Decimal("0.0001"), \
        f"Trader K should gain {expected_trader_payout}, got {trader_gain}"
    print(f"✓ Trader K payout: +{trader_gain} (expected {expected_trader_payout})")

    # Verify cash conservation
    total_paid = dealer_gain + vbt_gain + trader_gain
    assert abs(total_paid - expected_total_paid) < Decimal("0.0001"), \
        f"Total paid should be {expected_total_paid}, got {total_paid}"
    print(f"\n✓ Cash conservation: {total_paid} = R * D_I(t) = 0.6 * 5 = 3")

    # Verify ticket deletion
    # Dealer inventory should decrease by 2
    dealer_inv_change = after["dealer_inv"] - before["dealer_inv"]
    assert dealer_inv_change == -2, \
        f"Dealer inventory should decrease by 2, got {dealer_inv_change}"

    # VBT inventory should decrease by 2 (from issuer I)
    vbt_inv_change = after["vbt_inv"] - before["vbt_inv"]
    assert vbt_inv_change == -2, \
        f"VBT inventory should decrease by 2, got {vbt_inv_change}"

    # Trader K inventory should decrease by 1
    trader_inv_change = after["trader_inv"] - before["trader_inv"]
    assert trader_inv_change == -1, \
        f"Trader K inventory should decrease by 1, got {trader_inv_change}"

    print(f"✓ Ticket deletion: dealer -2, VBT -2, trader K -1 (all 5 deleted)")

    # Verify type symmetry (same per-ticket payout)
    per_ticket = S * R
    print(f"\n✓ Type symmetry: all holders receive S*R = {per_ticket} per ticket")

    print("\n✓ All settlement checks passed!")


def verify_loss_rate(sim: DealerRingSimulation) -> None:
    """Verify the bucket loss rate computation."""
    print("\n=== Loss Rate Verification ===")

    # Get loss rate from events
    loss_rate = sim.events.get_bucket_loss_rate(day=1, bucket_id="mid")

    # Expected: 1 - R = 1 - 0.6 = 0.4
    expected_loss = Decimal("0.4")

    print(f"Bucket loss rate: {loss_rate}")
    print(f"Expected: 1 - R = 1 - 0.6 = {expected_loss}")

    assert abs(loss_rate - expected_loss) < Decimal("0.0001"), \
        f"Loss rate should be {expected_loss}, got {loss_rate}"

    print("✓ Loss rate verified!")


def main():
    sim = setup_example11()
    sim._capture_snapshot()

    print("Example 11: Partial-Recovery Default (R=0.6)")
    print("=" * 60)

    verify_initial_state(sim)
    results = run_settlement(sim)
    verify_settlement(sim, results)
    verify_loss_rate(sim)

    # Log final quotes (after settlement)
    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    # Recompute after settlement
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
    out_path = out_dir / "example11_report.html"

    sim.to_html(
        out_path,
        title="Example 11: Partial-Recovery Default (R=0.6)",
        subtitle="Multiple claimant types receive proportional recovery",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 11 checks passed!")


if __name__ == "__main__":
    main()
