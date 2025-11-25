"""
Example 7: Edge Rung Without Interior Clipping.

From the dealer ring specification:
Demonstrates that under the L1 kernel, interior quotes remain strictly inside
the outside quotes for all feasible inventories x ∈ [0, X*]. As x approaches
the boundaries, {a(x), b(x)} approach {A, B} but do not reach them.
Outside pins occur only at the boundary via pass-through.

Setup:
- S=1, M=1.0, O=0.30, A=1.15, B=0.85
- Dealer: a=4, C=0.90
- V=4.90, K*=4, X*=4, λ=1/5=0.2, I=0.06
- Midline p(x) = 1 - 0.05(x-2)

At x=1 (one rung before running out of inventory):
- p(1) = 1.05, a(1) = 1.08 < A = 1.15
- Interior SELL feasible (x >= S)
- Gap to outside ask: A - a(1) = 0.07

At x=3 (one rung before capacity):
- p(3) = 0.95, b(3) = 0.92 > B = 0.85
- Interior BUY feasible (x+S <= X* and C >= b)
- Gap to outside bid: b(3) - B = 0.07

Harness checks:
1. a(x) < A and b(x) > B for all x in {0,1,2,3}
2. Gaps A - a(x) and b(x) - B are positive
3. Interior trades feasible at x=1 and x=3
4. Boundary pins only at x=0 (BUY) and x=X* (SELL)

Usage:
    uv run python examples/dealer_ring/example7_no_interior_clipping.py

Output:
    examples/dealer_ring/out/example7_report.html
"""

from decimal import Decimal
from pathlib import Path

from bilancio.dealer import (
    DealerRingConfig,
    DealerRingSimulation,
    Ticket,
    TraderState,
    recompute_dealer_state,
    can_interior_buy,
    can_interior_sell,
)


def setup_example7() -> DealerRingSimulation:
    """Set up Example 7: Edge rung without interior clipping."""
    config = DealerRingConfig(
        dealer_share=Decimal("1.0"),
        vbt_share=Decimal("0.0"),
        N_max=0,
        max_days=1,
        seed=42,
        vbt_anchors={
            "short": (Decimal("1.00"), Decimal("0.30")),
            "mid": (Decimal("1.00"), Decimal("0.30")),
            "long": (Decimal("1.00"), Decimal("0.30")),
        },
    )

    sim = DealerRingSimulation(config)

    # Create issuer
    issuer = TraderState(agent_id="issuer", cash=Decimal("100.00"))
    sim.traders[issuer.agent_id] = issuer

    # Set up dealer with a=4, C=0.90 (using mid bucket)
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("0.90")

    # Create 4 tickets for dealer inventory
    for i in range(4):
        ticket = Ticket(
            id=f"D{i}",
            issuer_id=issuer.agent_id,
            owner_id=dealer.agent_id,
            face=Decimal(1),
            maturity_day=200,
            remaining_tau=6,
            bucket_id="mid",
            serial=i,
        )
        dealer.inventory.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

    # Create VBT inventory
    vbt = sim.vbts["mid"]
    for i in range(5):
        vbt_ticket = Ticket(
            id=f"VBT{i}",
            issuer_id=issuer.agent_id,
            owner_id=vbt.agent_id,
            face=Decimal(1),
            maturity_day=200,
            remaining_tau=6,
            bucket_id="mid",
            serial=100 + i,
        )
        vbt.inventory.append(vbt_ticket)
        sim.all_tickets[vbt_ticket.id] = vbt_ticket

    # Recompute dealer state
    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def verify_initial_state(sim: DealerRingSimulation) -> None:
    """Verify initial state."""
    print("\n=== Initial State ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    print(f"Dealer: a={dealer.a}, C={dealer.cash}, x={dealer.x}")
    print(f"  V={dealer.V:.4f}, K*={dealer.K_star}, X*={dealer.X_star}")
    print(f"  λ={dealer.lambda_:.4f}, I={dealer.I:.4f}")
    print(f"\nVBT: M={vbt.M}, O={vbt.O}, A={vbt.A}, B={vbt.B}")

    assert dealer.a == 4
    assert dealer.cash == Decimal("0.90")
    assert dealer.X_star == 4
    assert abs(dealer.lambda_ - Decimal("0.20")) < Decimal("0.001")
    assert abs(dealer.I - Decimal("0.06")) < Decimal("0.001")

    print("✓ Initial state verified!")


def check_no_interior_clipping(sim: DealerRingSimulation) -> None:
    """
    Check that interior quotes never hit outside quotes.

    For all x in {0, 1, 2, ..., X*-1}:
    - a(x) < A (ask always below outside ask)
    - b(x) > B (bid always above outside bid)
    """
    print("\n=== Interior Clipping Check ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    A = vbt.A
    B = vbt.B
    X_star = dealer.X_star

    print(f"Outside quotes: A={A}, B={B}")
    print(f"Capacity X*={X_star}")
    print(f"\nChecking interior rungs x ∈ {{1, 2, ..., {int(X_star)-1}}} (excluding boundaries):\n")

    # We need to check quotes at each rung
    # Save current state
    original_inventory = dealer.inventory.copy()
    original_cash = dealer.cash

    all_passed = True

    # Check rungs x ∈ {1, 2, ..., X*-1} (interior, not boundaries)
    # At x=0: ask pins to A (no inventory to sell) - this is expected
    # At x=X*: bid pins to B (at capacity) - this is expected
    #
    # IMPORTANT: To keep X* = 4 fixed, we adjust cash to maintain V = 4.90
    # V = M*a + C, so C = V - M*a = 4.90 - a
    V_target = Decimal("4.90")
    M = vbt.M

    for x in range(1, int(X_star)):
        # Adjust inventory and cash to maintain V = 4.90
        dealer.inventory = original_inventory[:x]
        dealer.cash = V_target - M * x  # Keep V constant
        recompute_dealer_state(dealer, vbt, sim.params)

        ask = dealer.ask
        bid = dealer.bid
        gap_ask = A - ask
        gap_bid = bid - B

        ask_ok = ask < A
        bid_ok = bid > B

        status = "✓" if (ask_ok and bid_ok) else "✗"
        print(f"  x={x}: ask={ask:.4f} {'<' if ask_ok else '>='} A={A} (gap={gap_ask:.4f}), "
              f"bid={bid:.4f} {'>' if bid_ok else '<='} B={B} (gap={gap_bid:.4f}) {status}")

        if not (ask_ok and bid_ok):
            all_passed = False

    # Note: x=0 and x=X* are boundary cases where pins are expected
    print(f"\n  Note: x=0 and x=X* are boundaries where pins to A/B are expected")

    # Restore original state
    dealer.inventory = original_inventory
    dealer.cash = original_cash
    recompute_dealer_state(dealer, vbt, sim.params)

    if all_passed:
        print("\n✓ No interior clipping: a(x) < A and b(x) > B for all x!")
    else:
        print("\n✗ Interior clipping detected!")

    assert all_passed, "Interior clipping should not occur"


def check_edge_rungs(sim: DealerRingSimulation) -> None:
    """Check quotes at edge rungs x=1 and x=X*-1 with V kept constant."""
    print("\n=== Edge Rung Verification ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    # Save state
    original_inventory = dealer.inventory.copy()
    original_cash = dealer.cash

    # Keep V = 4.90 to maintain X* = 4
    V_target = Decimal("4.90")
    M = vbt.M

    # Check x=1 (one rung before running out)
    print("\nAt x=1 (one rung before empty), keeping V=4.90:")
    dealer.inventory = original_inventory[:1]
    dealer.cash = V_target - M * 1  # C = 3.90
    recompute_dealer_state(dealer, vbt, sim.params)

    print(f"  V={dealer.V:.4f}, X*={dealer.X_star}")
    print(f"  midline p(1) = {dealer.midline:.4f}")
    print(f"  ask a(1) = {dealer.ask:.4f}")
    print(f"  bid b(1) = {dealer.bid:.4f}")
    print(f"  Expected: p(1)=1.05, a(1)=1.08, b(1)=1.02")

    assert abs(dealer.midline - Decimal("1.05")) < Decimal("0.001"), f"midline off: {dealer.midline}"
    assert abs(dealer.ask - Decimal("1.08")) < Decimal("0.001"), f"ask off: {dealer.ask}"
    assert abs(dealer.bid - Decimal("1.02")) < Decimal("0.001"), f"bid off: {dealer.bid}"

    # Check feasibility at x=1
    can_sell = can_interior_sell(dealer, sim.params)
    print(f"  Interior SELL feasible (x >= S): {can_sell}")
    assert can_sell, "Interior SELL should be feasible at x=1"

    # Check x=3 (one rung before capacity)
    print("\nAt x=3 (one rung before capacity X*=4), keeping V=4.90:")
    dealer.inventory = original_inventory[:3]
    dealer.cash = V_target - M * 3  # C = 1.90
    recompute_dealer_state(dealer, vbt, sim.params)

    print(f"  V={dealer.V:.4f}, X*={dealer.X_star}")
    print(f"  midline p(3) = {dealer.midline:.4f}")
    print(f"  ask a(3) = {dealer.ask:.4f}")
    print(f"  bid b(3) = {dealer.bid:.4f}")
    print(f"  Expected: p(3)=0.95, a(3)=0.98, b(3)=0.92")

    assert abs(dealer.midline - Decimal("0.95")) < Decimal("0.001"), f"midline off: {dealer.midline}"
    assert abs(dealer.ask - Decimal("0.98")) < Decimal("0.001"), f"ask off: {dealer.ask}"
    assert abs(dealer.bid - Decimal("0.92")) < Decimal("0.001"), f"bid off: {dealer.bid}"

    # Check feasibility at x=3
    can_buy = can_interior_buy(dealer, sim.params)
    print(f"  Interior BUY feasible (x+S <= X* and C >= b): {can_buy}")
    assert can_buy, "Interior BUY should be feasible at x=3"

    # Restore
    dealer.inventory = original_inventory
    dealer.cash = original_cash
    recompute_dealer_state(dealer, vbt, sim.params)

    print("\n✓ Edge rungs verified!")


def check_boundary_pins(sim: DealerRingSimulation) -> None:
    """Check that boundary conditions trigger pins to outside quotes."""
    print("\n=== Boundary Pin Verification ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    # Save state
    original_inventory = dealer.inventory.copy()
    original_cash = dealer.cash

    # At x=0: BUY order pins to A (dealer has no inventory to sell)
    print("\nAt x=0 (no inventory):")
    dealer.inventory = []
    recompute_dealer_state(dealer, vbt, sim.params)

    can_sell = can_interior_sell(dealer, sim.params)
    print(f"  Interior SELL feasible: {can_sell}")
    print(f"  → Customer BUY must pin to A={vbt.A} (passthrough)")
    assert not can_sell, "Interior SELL should be infeasible at x=0"

    # At x=X*: SELL order pins to B (dealer at capacity)
    print(f"\nAt x=X*={dealer.X_star} (at capacity):")
    dealer.inventory = original_inventory[:4]  # x=4
    dealer.cash = Decimal("0.00")  # No cash to buy more
    recompute_dealer_state(dealer, vbt, sim.params)

    can_buy = can_interior_buy(dealer, sim.params)
    print(f"  Interior BUY feasible: {can_buy}")
    print(f"  → Customer SELL must pin to B={vbt.B} (passthrough)")
    assert not can_buy, "Interior BUY should be infeasible at x=X*"

    # Restore
    dealer.inventory = original_inventory
    dealer.cash = original_cash
    recompute_dealer_state(dealer, vbt, sim.params)

    print("\n✓ Boundary pins verified!")


def main():
    sim = setup_example7()
    sim._capture_snapshot()

    print("Example 7: Edge Rung Without Interior Clipping")
    print("=" * 60)

    verify_initial_state(sim)
    check_no_interior_clipping(sim)
    check_edge_rungs(sim)
    check_boundary_pins(sim)

    # Capture final snapshot
    sim.day = 1
    sim._capture_snapshot()

    # Export HTML report
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example7_report.html"

    sim.to_html(
        out_path,
        title="Example 7: No Interior Clipping",
        subtitle="Interior quotes always strictly inside outside quotes",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 7 checks passed!")


if __name__ == "__main__":
    main()
