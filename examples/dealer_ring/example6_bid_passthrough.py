"""
Example 6: Bid-Side Pass-Through (Dealer Lays Off at Outside Bid).

From the dealer ring specification:
A customer SELL arrives when the dealer cannot buy one more ticket.
Per commit-to-quote rules, dealer pins to outside bid B and executes
via atomic pass-through to VBT. Dealer's state (x, C) is unchanged.
This is Event 9 in the spec.

Subcase A: Capacity binding at the right edge (x = X*)
- S=1, a=2, C=0.10
- V=2.10, K*=2, X*=2, x=2=X*
- λ=1/3, I=0.10
- p(2) = 1 - 0.30/(2+2)*(2-1) = 0.925
- b(2) = 0.925 - 0.05 = 0.875
- b_c(2) = max{B, b(2)} = max{0.85, 0.875} = 0.875

Customer SELL:
- Interior BUY fails because x + S = 3 > X* = 2 (capacity bound)
- Also cash insufficient: C = 0.10 < b_c(2) = 0.875
- Execute passthrough at B = 0.85
- Dealer state unchanged: (x, C) = (2, 0.10)

Test assertions:
- Dealer invariants (Event 9): Δx_D = 0, ΔC_D = 0
- Clipping bound: b_c(x) >= B
- Double-entry: trader cash gain = VBT cash outflow

Usage:
    uv run python examples/dealer_ring/example6_bid_passthrough.py

Output:
    examples/dealer_ring/out/example6_report.html
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


def setup_example6() -> DealerRingSimulation:
    """Set up Example 6 scenario: bid-side passthrough."""
    config = DealerRingConfig(
        dealer_share=Decimal("1.0"),
        vbt_share=Decimal("0.0"),
        N_max=0,
        max_days=1,
        seed=42,
        # VBT anchors: M=1.0, O=0.30
        vbt_anchors={
            "short": (Decimal("1.00"), Decimal("0.30")),
            "mid": (Decimal("1.00"), Decimal("0.30")),
            "long": (Decimal("1.00"), Decimal("0.30")),
        },
    )

    sim = DealerRingSimulation(config)

    # Create issuer
    issuer = TraderState(
        agent_id="issuer",
        cash=Decimal("100.00"),
    )
    sim.traders[issuer.agent_id] = issuer

    # Create seller who will trigger the passthrough
    seller = TraderState(
        agent_id="seller",
        cash=Decimal("0.00"),
    )
    sim.traders[seller.agent_id] = seller

    # Set up dealer with a=2, C=0.10 (using mid bucket)
    # This puts dealer at x=X*=2 with insufficient cash
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("0.10")

    # Create 2 tickets for dealer inventory
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

    # Create ticket for seller to sell
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

    # VBT needs cash for passthrough (will pay B=0.85)
    vbt = sim.vbts["mid"]
    vbt.cash = Decimal("10.00")

    # Recompute dealer state
    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def verify_initial_state(sim: DealerRingSimulation) -> None:
    """Verify initial state matches specification."""
    print("\n=== Initial State (Subcase A: Capacity Binding) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    print(f"Dealer: a={dealer.a}, C={dealer.cash}, x={dealer.x}")
    print(f"  V={dealer.V:.4f}, K*={dealer.K_star}, X*={dealer.X_star}")
    print(f"  λ={dealer.lambda_:.4f}, I={dealer.I:.4f}")
    print(f"  midline p(2)={dealer.midline:.4f}")
    print(f"  Quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")

    print(f"\nVBT: M={vbt.M}, O={vbt.O}, A={vbt.A}, B={vbt.B}")
    print(f"VBT cash: {vbt.cash}")

    # Verify dealer state
    # Expected: a=2, C=0.10, x=2, X*=2
    # V = M*a + C = 1*2 + 0.10 = 2.10, K* = floor(2.10/1) = 2
    # λ = 1/(X*+1) = 1/3, I = λO = 0.10
    # p(2) = 1 - 0.30/(2+2)*(2-1) = 1 - 0.075 = 0.925
    # b(2) = p(2) - I/2 = 0.925 - 0.05 = 0.875

    assert dealer.a == 2, f"a should be 2, got {dealer.a}"
    assert dealer.cash == Decimal("0.10"), f"C should be 0.10, got {dealer.cash}"
    assert dealer.x == 2, f"x should be 2, got {dealer.x}"
    assert dealer.X_star == 2, f"X* should be 2, got {dealer.X_star}"
    assert abs(dealer.V - Decimal("2.10")) < Decimal("0.001"), f"V off: {dealer.V}"
    assert dealer.K_star == 2, f"K* should be 2, got {dealer.K_star}"

    # Check bid computation
    # b(2) = 0.875, but if clipped: b_c = max{B, b(2)} = max{0.85, 0.875} = 0.875
    expected_bid = Decimal("0.875")
    assert abs(dealer.bid - expected_bid) < Decimal("0.001"), f"bid should be ~{expected_bid}, got {dealer.bid}"

    # Verify x = X* (at capacity boundary)
    assert dealer.x == dealer.X_star, f"x should equal X* for capacity binding"

    print(f"\n  Expected: a=2, C=0.10, x=2, X*=2, bid≈0.875")
    print(f"  Note: x = X* means at capacity boundary")
    print("✓ Initial state verified!")


def run_passthrough_sell(sim: DealerRingSimulation) -> None:
    """Execute bid-side passthrough when dealer can't absorb SELL."""
    print("\n=== Bid-Side Passthrough (Event 9) ===")

    sim.day = 1
    sim.events.log_day_start(1)

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    seller = sim.traders["seller"]
    ticket = seller.tickets_owned[0]

    # Record state before trade
    x_before = dealer.x
    C_before = dealer.cash
    a_before = dealer.a
    vbt_cash_before = vbt.cash
    seller_cash_before = seller.cash

    print(f"Dealer before: x={x_before}, C={C_before}, a={a_before}")
    print(f"VBT cash before: {vbt_cash_before}")
    print(f"Seller cash before: {seller_cash_before}")

    # Check why interior BUY is infeasible:
    # 1. Capacity check: x + S = 2 + 1 = 3 > X* = 2 ❌
    # 2. Cash check: C = 0.10 < bid = 0.875 ❌
    print(f"\nFeasibility check:")
    print(f"  Capacity: x + S = {dealer.x} + 1 = {dealer.x + 1} > X* = {dealer.X_star}? {dealer.x + 1 > dealer.X_star}")
    print(f"  Cash: C = {dealer.cash} >= bid = {dealer.bid}? {dealer.cash >= dealer.bid}")
    print(f"  Interior BUY infeasible → passthrough at B = {vbt.B}")

    # Execute SELL
    result = sim.executor.execute_customer_sell(
        dealer=dealer,
        vbt=vbt,
        ticket=ticket,
    )

    # Update seller
    seller.cash += result.price
    seller.tickets_owned.remove(ticket)

    # Log trade
    sim.events.log_trade(
        day=1,
        side="SELL",
        trader_id=seller.agent_id,
        ticket_id=ticket.id,
        bucket="mid",
        price=result.price,
        is_passthrough=result.is_passthrough,
    )

    print(f"\nExecution:")
    print(f"  Price: {result.price} (should be B = {vbt.B})")
    print(f"  Passthrough: {result.is_passthrough} (should be True)")

    print(f"\nDealer after: x={dealer.x}, C={dealer.cash}, a={dealer.a}")
    print(f"VBT cash after: {vbt.cash}")
    print(f"Seller cash after: {seller.cash}")

    # Verify passthrough
    assert result.is_passthrough, "Should be passthrough trade"
    assert result.price == vbt.B, f"Price should be B={vbt.B}, got {result.price}"

    # Verify dealer state unchanged (C4 assertion)
    assert dealer.x == x_before, f"x should be unchanged: {x_before}, got {dealer.x}"
    assert dealer.cash == C_before, f"C should be unchanged: {C_before}, got {dealer.cash}"
    assert dealer.a == a_before, f"a should be unchanged: {a_before}, got {dealer.a}"

    # Verify double-entry
    seller_gain = seller.cash - seller_cash_before
    vbt_payment = vbt_cash_before - vbt.cash
    assert seller_gain == result.price, f"Seller gain should equal price"
    assert vbt_payment == result.price, f"VBT payment should equal price"

    print(f"\n  Dealer invariants: Δx=0, ΔC=0 ✓")
    print(f"  Double-entry: seller +{seller_gain}, VBT -{vbt_payment} ✓")
    print("✓ Passthrough verified!")


def main():
    sim = setup_example6()
    sim._capture_snapshot()

    print("Example 6: Bid-Side Pass-Through")
    print("=" * 60)

    verify_initial_state(sim)
    run_passthrough_sell(sim)

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

    sim._capture_snapshot()

    # Final summary
    print("\n=== Final Summary ===")
    print(f"Dealer: a={dealer.a}, x={dealer.x}, C={dealer.cash}")
    print(f"  Quotes unchanged: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print(f"VBT absorbed the ticket at outside bid B={vbt.B}")
    print(f"Dealer state (x, C) remained unchanged by passthrough.")

    # Export HTML report
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example6_report.html"

    sim.to_html(
        out_path,
        title="Example 6: Bid-Side Pass-Through",
        subtitle="Customer SELL routed to VBT when dealer at capacity",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 6 checks passed!")


if __name__ == "__main__":
    main()
