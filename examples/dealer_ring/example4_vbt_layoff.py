"""
Example 4: Dealer Reaches Inventory Limit and VBT Layoff Occurs.

From the dealer ring specification:
- One bucket with dealer and VBT
- M=1.0, O=0.30, A=1.15, B=0.85
- Initial: a=2, C=2 → V=4, K*=4, X*=4, x=2
- λ=1/5=0.2, I=0.06, p(x)=1-0.05(x-2)
- At x=2: a(2)=1.03, b(2)=0.97

Step 1: Customer BUY (interior) at ask a(2)=1.03
- x: 2→1, C: 2→3.03
- p(1)=1.05, a(1)=1.08, b(1)=1.02

Step 2: Second BUY (interior) at ask a(1)=1.08
- x: 1→0, C: 3.03→4.11
- Counterfactual quotes at x=0: p(0)=1.10, a(0)=1.13, b(0)=1.07

Step 3: Third BUY (VBT layoff) at ask A=1.15
- x=0, so interior SELL is infeasible
- Pin to A=1.15 and passthrough to VBT
- x stays 0, C stays 4.11 (dealer state unchanged)

Key insight: At x=0 boundary, operational ask pins to A=1.15 and
the trade routes to VBT. Dealer's (x, C) are unchanged by passthrough.

Usage:
    uv run python examples/dealer_ring/example4_vbt_layoff.py

Output:
    examples/dealer_ring/out/example4_report.html
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


def setup_example4() -> DealerRingSimulation:
    """Set up Example 4 scenario: dealer inventory limit and VBT layoff."""
    config = DealerRingConfig(
        dealer_share=Decimal("1.0"),   # All flow to dealer
        vbt_share=Decimal("0.0"),      # No VBT flow initially
        N_max=0,                        # Disable random order flow
        max_days=1,
        seed=42,
        # VBT anchors: M=1.0, O=0.30 for mid bucket (we'll use mid)
        vbt_anchors={
            "short": (Decimal("1.00"), Decimal("0.30")),
            "mid": (Decimal("1.00"), Decimal("0.30")),
            "long": (Decimal("1.00"), Decimal("0.30")),
        },
    )

    sim = DealerRingSimulation(config)

    # Create issuer for dealer tickets
    issuer = TraderState(
        agent_id="issuer",
        cash=Decimal("100.00"),
    )
    sim.traders[issuer.agent_id] = issuer

    # Create 3 buyers that will execute the BUYs
    for i in range(1, 4):
        buyer = TraderState(
            agent_id=f"buyer_{i}",
            cash=Decimal("10.00"),  # Plenty of cash
        )
        sim.traders[buyer.agent_id] = buyer

    # Set up dealer with a=2, C=2 (using mid bucket)
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("2.00")

    # Create 2 tickets for dealer inventory
    for i in range(2):
        ticket = Ticket(
            id=f"D{i}",
            issuer_id=issuer.agent_id,
            owner_id=dealer.agent_id,
            face=Decimal(1),
            maturity_day=200,
            remaining_tau=6,  # Mid bucket
            bucket_id="mid",
            serial=i,
        )
        dealer.inventory.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

    # Create VBT inventory (needed for passthrough)
    vbt = sim.vbts["mid"]
    vbt_ticket = Ticket(
        id="VBT0",
        issuer_id=issuer.agent_id,
        owner_id=vbt.agent_id,
        face=Decimal(1),
        maturity_day=200,
        remaining_tau=6,
        bucket_id="mid",
        serial=100,
    )
    vbt.inventory.append(vbt_ticket)
    sim.all_tickets[vbt_ticket.id] = vbt_ticket
    issuer.obligations.append(vbt_ticket)

    # Recompute dealer state
    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def verify_initial_state(sim: DealerRingSimulation) -> None:
    """Verify initial state matches specification."""
    print("\n=== Initial State (t0) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    print(f"Dealer: a={dealer.a}, C={dealer.cash}, x={dealer.x}")
    print(f"  V={dealer.V}, K*={dealer.K_star}, X*={dealer.X_star}")
    print(f"  λ={dealer.lambda_:.4f}, I={dealer.I:.4f}")
    print(f"  Quotes at x={dealer.x}: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print(f"  Expected: a=2, C=2, x=2, X*=4, λ=0.20, I=0.06, ask=1.03, bid=0.97")

    print(f"\nVBT: M={vbt.M}, O={vbt.O}, A={vbt.A}, B={vbt.B}")

    # Assertions
    assert dealer.a == 2, f"a should be 2, got {dealer.a}"
    assert dealer.cash == Decimal("2.00"), f"C should be 2, got {dealer.cash}"
    assert dealer.x == 2, f"x should be 2, got {dealer.x}"
    assert dealer.X_star == 4, f"X* should be 4, got {dealer.X_star}"
    assert abs(dealer.lambda_ - Decimal("0.20")) < Decimal("0.001"), f"λ off: {dealer.lambda_}"
    assert abs(dealer.I - Decimal("0.06")) < Decimal("0.001"), f"I off: {dealer.I}"
    assert abs(dealer.ask - Decimal("1.03")) < Decimal("0.001"), f"ask off: {dealer.ask}"
    assert abs(dealer.bid - Decimal("0.97")) < Decimal("0.001"), f"bid off: {dealer.bid}"

    # VBT assertions
    assert vbt.A == Decimal("1.15"), f"VBT A should be 1.15, got {vbt.A}"
    assert vbt.B == Decimal("0.85"), f"VBT B should be 0.85, got {vbt.B}"

    print("✓ Initial state verified!")


def run_step1(sim: DealerRingSimulation) -> None:
    """Step 1: First customer BUY (interior) at ask a(2)=1.03."""
    print("\n=== Step 1: First BUY (interior) ===")

    sim.day = 1
    sim.events.log_day_start(1)

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    buyer = sim.traders["buyer_1"]

    ask_before = dealer.ask
    print(f"Ask before: {ask_before:.4f}, expected: 1.03")
    assert abs(ask_before - Decimal("1.03")) < Decimal("0.001")

    # Execute BUY
    result = sim.executor.execute_customer_buy(
        dealer=dealer,
        vbt=vbt,
        buyer_id=buyer.agent_id,
    )

    # Update buyer's cash
    buyer.cash -= result.price

    # Link ticket to buyer
    buyer.tickets_owned.append(result.ticket)

    # Log trade
    sim.events.log_trade(
        day=1,
        side="BUY",
        trader_id=buyer.agent_id,
        ticket_id=result.ticket.id,
        bucket="mid",
        price=result.price,
        is_passthrough=result.is_passthrough,
    )

    print(f"Executed at: {result.price:.4f}, passthrough: {result.is_passthrough}")
    print(f"Dealer after: x={dealer.x}, C={dealer.cash:.4f}")
    print(f"  Quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print(f"  Expected: x=1, C=3.03, ask=1.08, bid=1.02")

    # Assertions
    assert not result.is_passthrough, "Should be interior trade"
    assert abs(result.price - Decimal("1.03")) < Decimal("0.001"), f"price off: {result.price}"
    assert dealer.x == 1, f"x should be 1, got {dealer.x}"
    assert abs(dealer.cash - Decimal("3.03")) < Decimal("0.001"), f"C off: {dealer.cash}"
    assert abs(dealer.ask - Decimal("1.08")) < Decimal("0.001"), f"ask off: {dealer.ask}"
    assert abs(dealer.bid - Decimal("1.02")) < Decimal("0.001"), f"bid off: {dealer.bid}"

    print("✓ Step 1 verified!")


def run_step2(sim: DealerRingSimulation) -> None:
    """Step 2: Second customer BUY (interior to boundary) at ask a(1)=1.08."""
    print("\n=== Step 2: Second BUY (interior to boundary) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    buyer = sim.traders["buyer_2"]

    ask_before = dealer.ask
    print(f"Ask before: {ask_before:.4f}, expected: 1.08")
    assert abs(ask_before - Decimal("1.08")) < Decimal("0.001")

    # Execute BUY
    result = sim.executor.execute_customer_buy(
        dealer=dealer,
        vbt=vbt,
        buyer_id=buyer.agent_id,
    )

    # Update buyer's cash
    buyer.cash -= result.price
    buyer.tickets_owned.append(result.ticket)

    # Log trade
    sim.events.log_trade(
        day=1,
        side="BUY",
        trader_id=buyer.agent_id,
        ticket_id=result.ticket.id,
        bucket="mid",
        price=result.price,
        is_passthrough=result.is_passthrough,
    )

    print(f"Executed at: {result.price:.4f}, passthrough: {result.is_passthrough}")
    print(f"Dealer after: x={dealer.x}, C={dealer.cash:.4f}")
    print(f"  Quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print(f"  Expected: x=0, C=4.11, ask=1.13 (counterfactual), bid=1.07")

    # Assertions
    assert not result.is_passthrough, "Should be interior trade"
    assert abs(result.price - Decimal("1.08")) < Decimal("0.001"), f"price off: {result.price}"
    assert dealer.x == 0, f"x should be 0, got {dealer.x}"
    assert abs(dealer.cash - Decimal("4.11")) < Decimal("0.001"), f"C off: {dealer.cash}"
    # At x=0, quotes are counterfactual (not executable without inventory)
    assert abs(dealer.ask - Decimal("1.13")) < Decimal("0.001"), f"ask off: {dealer.ask}"
    assert abs(dealer.bid - Decimal("1.07")) < Decimal("0.001"), f"bid off: {dealer.bid}"

    print("✓ Step 2 verified!")


def run_step3(sim: DealerRingSimulation) -> None:
    """Step 3: Third customer BUY (VBT layoff at the boundary) at A=1.15."""
    print("\n=== Step 3: Third BUY (VBT layoff) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    buyer = sim.traders["buyer_3"]

    # Store dealer state before
    x_before = dealer.x
    C_before = dealer.cash
    print(f"Dealer before: x={x_before}, C={C_before:.4f}")
    print(f"VBT A (outside ask): {vbt.A}")

    # Execute BUY - should trigger passthrough
    result = sim.executor.execute_customer_buy(
        dealer=dealer,
        vbt=vbt,
        buyer_id=buyer.agent_id,
    )

    # Update buyer's cash
    buyer.cash -= result.price
    buyer.tickets_owned.append(result.ticket)

    # Log trade
    sim.events.log_trade(
        day=1,
        side="BUY",
        trader_id=buyer.agent_id,
        ticket_id=result.ticket.id,
        bucket="mid",
        price=result.price,
        is_passthrough=result.is_passthrough,
    )

    print(f"Executed at: {result.price}, passthrough: {result.is_passthrough}")
    print(f"Dealer after: x={dealer.x}, C={dealer.cash:.4f}")
    print(f"  Expected: x=0 (unchanged), C=4.11 (unchanged), price=A=1.15")

    # Assertions
    assert result.is_passthrough, "Should be passthrough trade at boundary"
    assert result.price == vbt.A, f"price should be A=1.15, got {result.price}"
    assert dealer.x == x_before, f"x should be unchanged, was {x_before}, got {dealer.x}"
    assert dealer.cash == C_before, f"C should be unchanged, was {C_before}, got {dealer.cash}"

    print("✓ Step 3 verified!")


def main():
    # Set up scenario
    sim = setup_example4()

    # Capture Day 0 snapshot
    sim._capture_snapshot()

    print("Example 4: Dealer Reaches Inventory Limit and VBT Layoff")
    print("=" * 60)

    # Verify initial state
    verify_initial_state(sim)

    # Run the three steps
    run_step1(sim)
    run_step2(sim)
    run_step3(sim)

    # Log final quotes
    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
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

    # Capture Day 1 snapshot
    sim._capture_snapshot()

    # Final summary
    print("\n=== Final Summary ===")
    print(f"Dealer: a={dealer.a}, x={dealer.x}, C={dealer.cash:.4f}")
    print(f"  Quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print("  Note: At x=0, interior quotes are counterfactual only.")
    print("        Operational ask pins to A=1.15 for passthrough.")

    # Export HTML report
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example4_report.html"

    sim.to_html(
        out_path,
        title="Example 4: VBT Layoff at Inventory Limit",
        subtitle="Dealer runs out of inventory, trades route to VBT at outside ask",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 4 checks passed!")


if __name__ == "__main__":
    main()
