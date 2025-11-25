"""
Example 12: One-Ticket Trade Pushes Capacity Across an Integer.

From the dealer ring specification (Section 13):
Demonstrates how a single trade can cause K* (and hence X*, lambda, I) to
jump discretely when V crosses an integer boundary.

Setup:
- S=1, M=1.0, O=0.30, A=1.15, B=0.85
- Kernel formulas: V=Ma+C, K*=floor(V/M), X*=SK*, lambda=S/(X*+S), I=lambda*O

Case A: Up-jump K* : 3 -> 4 after one interior BUY
- Initial: a=2, C=1.97 => V=3.97, K*=3, X*=3
- x=2, lambda=1/4=0.25, I=0.075
- p(2)=0.97, b(2)=0.9325
- Interior BUY feasible: x+S=3 <= X*=3, C=1.97 >= b=0.9325
- After BUY: x=3, C=1.0375, V=4.0375, K*=4, X*=4
- lambda: 0.25 -> 0.20, I: 0.075 -> 0.06

Case B: Down-jump K* : 4 -> 3 after one interior SELL
- Initial: a=4, C=0.02 => V=4.02, K*=4, X*=4
- x=4, lambda=1/5=0.20, I=0.06
- p(4)=0.90, a(4)=0.93
- Interior SELL feasible: x=4 >= S=1
- After SELL: x=3, C=0.95, V=3.95, K*=3, X*=3
- lambda: 0.20 -> 0.25, I: 0.06 -> 0.075

Harness checks:
1. Capacity jump: K* changes by exactly ±1
2. Width jump: lambda and I change discretely
3. Feasibility: trades satisfy interior conditions
4. No clipping/passthrough: trades execute at interior quotes

Usage:
    uv run python examples/dealer_ring/example12_capacity_crossing.py

Output:
    examples/dealer_ring/out/example12_report.html
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


def setup_case_a() -> DealerRingSimulation:
    """Set up Case A: Up-jump K* : 3 -> 4."""
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

    # Create seller
    seller = TraderState(agent_id="seller", cash=Decimal("0.00"))
    sim.traders[seller.agent_id] = seller

    # Set up dealer: a=2, C=1.97 => V=3.97, K*=3
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("1.97")

    for i in range(2):
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

    # Create ticket for seller
    sell_ticket = Ticket(
        id="SELL1",
        issuer_id=issuer.agent_id,
        owner_id=seller.agent_id,
        face=Decimal(1),
        maturity_day=200,
        remaining_tau=6,
        bucket_id="mid",
        serial=10,
    )
    seller.tickets_owned.append(sell_ticket)
    sim.all_tickets[sell_ticket.id] = sell_ticket
    issuer.obligations.append(sell_ticket)

    # VBT needs inventory (backup)
    vbt = sim.vbts["mid"]
    vbt.cash = Decimal("10.00")

    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def setup_case_b() -> DealerRingSimulation:
    """Set up Case B: Down-jump K* : 4 -> 3."""
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

    # Create buyer
    buyer = TraderState(agent_id="buyer", cash=Decimal("10.00"))
    sim.traders[buyer.agent_id] = buyer

    # Set up dealer: a=4, C=0.02 => V=4.02, K*=4
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("0.02")

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

    # VBT (backup)
    vbt = sim.vbts["mid"]
    vbt.cash = Decimal("10.00")

    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def run_case_a(sim: DealerRingSimulation) -> None:
    """Case A: Up-jump K* : 3 -> 4 after one interior BUY."""
    print("\n=== CASE A: Up-Jump K* : 3 -> 4 ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    seller = sim.traders["seller"]
    ticket = seller.tickets_owned[0]

    # Verify initial state
    print("\nInitial state (just below integer boundary):")
    print(f"  a={dealer.a}, C={dealer.cash}")
    print(f"  V={dealer.V:.4f}, K*={dealer.K_star}, X*={dealer.X_star}")
    print(f"  x={dealer.x}, lambda={dealer.lambda_:.4f}, I={dealer.I:.4f}")
    print(f"  p(x)={dealer.midline:.4f}, b(x)={dealer.bid:.4f}")

    assert dealer.a == 2, f"a should be 2, got {dealer.a}"
    assert dealer.cash == Decimal("1.97"), f"C should be 1.97"
    assert dealer.K_star == 3, f"K* should be 3, got {dealer.K_star}"
    assert dealer.X_star == 3, f"X* should be 3, got {dealer.X_star}"
    assert abs(dealer.lambda_ - Decimal("0.25")) < Decimal("0.001"), f"lambda should be 0.25"
    assert abs(dealer.I - Decimal("0.075")) < Decimal("0.001"), f"I should be 0.075"

    # Verify feasibility
    can_buy = can_interior_buy(dealer, sim.params)
    print(f"\nFeasibility check:")
    print(f"  x + S = {dealer.x} + 1 = {dealer.x + 1} <= X* = {dealer.X_star}? {dealer.x + 1 <= dealer.X_star}")
    print(f"  C = {dealer.cash} >= b = {dealer.bid}? {dealer.cash >= dealer.bid}")
    print(f"  Interior BUY feasible: {can_buy}")
    assert can_buy, "Interior BUY should be feasible"

    # Record state before
    K_star_before = dealer.K_star
    lambda_before = dealer.lambda_
    I_before = dealer.I

    # Execute customer SELL (dealer BUYs)
    print(f"\nExecution (customer SELL; dealer BUYs at b={dealer.bid:.4f}):")
    result = sim.executor.execute_customer_sell(dealer, vbt, ticket)
    seller.cash += result.price
    seller.tickets_owned.remove(ticket)

    print(f"  Price: {result.price:.4f}")
    print(f"  Passthrough: {result.is_passthrough}")

    assert not result.is_passthrough, "Should be interior trade"
    assert abs(result.price - Decimal("0.9325")) < Decimal("0.001"), f"Price should be ~0.9325"

    # Verify post-trade state
    print(f"\nPost-trade state:")
    print(f"  a={dealer.a}, C={dealer.cash:.4f}")
    print(f"  V={dealer.V:.4f}, K*={dealer.K_star}, X*={dealer.X_star}")
    print(f"  x={dealer.x}, lambda={dealer.lambda_:.4f}, I={dealer.I:.4f}")

    # Verify capacity jump
    assert dealer.K_star == 4, f"K* should be 4 after trade, got {dealer.K_star}"
    assert dealer.X_star == 4, f"X* should be 4 after trade"
    print(f"\n✓ Capacity jump: K* {K_star_before} -> {dealer.K_star}")

    # Verify width jump
    assert abs(dealer.lambda_ - Decimal("0.20")) < Decimal("0.001"), f"lambda should be 0.20"
    assert abs(dealer.I - Decimal("0.06")) < Decimal("0.001"), f"I should be 0.06"
    print(f"✓ Width jump: lambda {lambda_before:.4f} -> {dealer.lambda_:.4f}, I {I_before:.4f} -> {dealer.I:.4f}")

    # Verify post-trade quotes
    # p(3) = 1 - 0.30/(4+2) * (3-2) = 1 - 0.05 = 0.95
    expected_midline = Decimal("0.95")
    assert abs(dealer.midline - expected_midline) < Decimal("0.001"), f"midline should be ~0.95"
    print(f"✓ New quotes at x={dealer.x}: p={dealer.midline:.4f}, a={dealer.ask:.4f}, b={dealer.bid:.4f}")

    print("\n✓ Case A passed!")


def run_case_b(sim: DealerRingSimulation) -> None:
    """Case B: Down-jump K* : 4 -> 3 after one interior SELL."""
    print("\n=== CASE B: Down-Jump K* : 4 -> 3 ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    buyer = sim.traders["buyer"]

    # Verify initial state
    print("\nInitial state (just above integer boundary):")
    print(f"  a={dealer.a}, C={dealer.cash}")
    print(f"  V={dealer.V:.4f}, K*={dealer.K_star}, X*={dealer.X_star}")
    print(f"  x={dealer.x}, lambda={dealer.lambda_:.4f}, I={dealer.I:.4f}")
    print(f"  p(x)={dealer.midline:.4f}, a(x)={dealer.ask:.4f}")

    assert dealer.a == 4, f"a should be 4, got {dealer.a}"
    assert dealer.cash == Decimal("0.02"), f"C should be 0.02"
    assert dealer.K_star == 4, f"K* should be 4, got {dealer.K_star}"
    assert dealer.X_star == 4, f"X* should be 4, got {dealer.X_star}"
    assert abs(dealer.lambda_ - Decimal("0.20")) < Decimal("0.001"), f"lambda should be 0.20"
    assert abs(dealer.I - Decimal("0.06")) < Decimal("0.001"), f"I should be 0.06"

    # Verify p(4) = 0.90
    # p(4) = 1 - 0.30/(4+2) * (4-2) = 1 - 0.05*2 = 0.90
    assert abs(dealer.midline - Decimal("0.90")) < Decimal("0.001"), f"p(4) should be 0.90"

    # Verify feasibility
    can_sell = can_interior_sell(dealer, sim.params)
    print(f"\nFeasibility check:")
    print(f"  x = {dealer.x} >= S = 1? {dealer.x >= 1}")
    print(f"  Interior SELL feasible: {can_sell}")
    assert can_sell, "Interior SELL should be feasible"

    # Record state before
    K_star_before = dealer.K_star
    lambda_before = dealer.lambda_
    I_before = dealer.I

    # Execute customer BUY (dealer SELLs)
    print(f"\nExecution (customer BUY; dealer SELLs at a={dealer.ask:.4f}):")
    result = sim.executor.execute_customer_buy(dealer, vbt, buyer.agent_id)
    buyer.cash -= result.price
    if result.ticket:
        buyer.tickets_owned.append(result.ticket)

    print(f"  Price: {result.price:.4f}")
    print(f"  Passthrough: {result.is_passthrough}")

    assert not result.is_passthrough, "Should be interior trade"
    assert abs(result.price - Decimal("0.93")) < Decimal("0.001"), f"Price should be ~0.93"

    # Verify post-trade state
    print(f"\nPost-trade state:")
    print(f"  a={dealer.a}, C={dealer.cash:.4f}")
    print(f"  V={dealer.V:.4f}, K*={dealer.K_star}, X*={dealer.X_star}")
    print(f"  x={dealer.x}, lambda={dealer.lambda_:.4f}, I={dealer.I:.4f}")

    # Verify capacity jump
    assert dealer.K_star == 3, f"K* should be 3 after trade, got {dealer.K_star}"
    assert dealer.X_star == 3, f"X* should be 3 after trade"
    print(f"\n✓ Capacity jump: K* {K_star_before} -> {dealer.K_star}")

    # Verify width jump (widens because capacity decreased)
    assert abs(dealer.lambda_ - Decimal("0.25")) < Decimal("0.001"), f"lambda should be 0.25"
    assert abs(dealer.I - Decimal("0.075")) < Decimal("0.001"), f"I should be 0.075"
    print(f"✓ Width jump: lambda {lambda_before:.4f} -> {dealer.lambda_:.4f}, I {I_before:.4f} -> {dealer.I:.4f}")

    # Verify post-trade quotes
    # p(3) = 1 - 0.30/(3+2) * (3 - 1.5) = 1 - 0.06 * 1.5 = 0.91
    expected_midline = Decimal("0.91")
    assert abs(dealer.midline - expected_midline) < Decimal("0.001"), f"midline should be ~0.91"
    print(f"✓ New quotes at x={dealer.x}: p={dealer.midline:.4f}, a={dealer.ask:.4f}, b={dealer.bid:.4f}")

    print("\n✓ Case B passed!")


def main():
    print("Example 11: Capacity Integer Crossing")
    print("=" * 60)

    # Case A: Up-jump
    sim_a = setup_case_a()
    sim_a._capture_snapshot()
    run_case_a(sim_a)

    # Log final state
    dealer_a = sim_a.dealers["mid"]
    vbt_a = sim_a.vbts["mid"]
    sim_a.day = 1
    sim_a.events.log_day_start(1)
    sim_a.events.log_quote(
        day=1,
        bucket="mid",
        dealer_bid=dealer_a.bid,
        dealer_ask=dealer_a.ask,
        vbt_bid=vbt_a.B,
        vbt_ask=vbt_a.A,
        inventory=dealer_a.a,
        capacity=dealer_a.X_star,
        is_pinned_bid=dealer_a.is_pinned_bid,
        is_pinned_ask=dealer_a.is_pinned_ask,
    )
    sim_a._capture_snapshot()

    # Case B: Down-jump
    print("\n" + "=" * 60)
    sim_b = setup_case_b()
    sim_b._capture_snapshot()
    run_case_b(sim_b)

    # Log final state
    dealer_b = sim_b.dealers["mid"]
    vbt_b = sim_b.vbts["mid"]
    sim_b.day = 1
    sim_b.events.log_day_start(1)
    sim_b.events.log_quote(
        day=1,
        bucket="mid",
        dealer_bid=dealer_b.bid,
        dealer_ask=dealer_b.ask,
        vbt_bid=vbt_b.B,
        vbt_ask=vbt_b.A,
        inventory=dealer_b.a,
        capacity=dealer_b.X_star,
        is_pinned_bid=dealer_b.is_pinned_bid,
        is_pinned_ask=dealer_b.is_pinned_ask,
    )
    sim_b._capture_snapshot()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nCase A (Up-jump):")
    print("  Before: K*=3, X*=3, lambda=0.25, I=0.075")
    print("  After:  K*=4, X*=4, lambda=0.20, I=0.06")
    print("  (Width tightens as capacity increases)")
    print("\nCase B (Down-jump):")
    print("  Before: K*=4, X*=4, lambda=0.20, I=0.06")
    print("  After:  K*=3, X*=3, lambda=0.25, I=0.075")
    print("  (Width widens as capacity decreases)")

    # Export HTML report (use Case A for report)
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example12_report.html"

    sim_a.to_html(
        out_path,
        title="Example 12: Capacity Integer Crossing",
        subtitle="K* jumps discretely when V crosses integer boundary",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 12 checks passed!")


if __name__ == "__main__":
    main()
