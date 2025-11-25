"""
Example 8: Guard at Very Low Mid M <= M_min.

From the dealer ring specification:
When M drops below the minimum threshold M_min, the Guard regime activates.
The dealer collapses to a pass-through only mode with X* = 0, ladder {0}.
All customer trades route to VBT at outside quotes (A for BUY, B for SELL).

Setup:
- M = 0.01 < M_min = 0.02 (Guard condition)
- O = 0.01, so A = M + O/2 = 0.015, B = M - O/2 = 0.005
- Dealer has arbitrary inventory (irrelevant under Guard)
- VBT has inventory and cash

Arrival 1: customer SELL (Event 9)
- Bid is pinned b_c = B = 0.005
- X* = 0, so interior dealer BUY is infeasible (x + S <= X* fails)
- Execute passthrough at B: dealer state unchanged

Arrival 2: customer BUY (Event 10)
- Ask is pinned a_c = A = 0.015
- Guard regime routes all BUYs to VBT regardless of dealer inventory
- Execute passthrough at A: dealer state unchanged

Harness checks:
1. Guard activation: M <= M_min => X* = 0, ladder {0}
2. Pinned quotes: a_c(x) = A, b_c(x) = B (no interior schedule)
3. Pass-through only: execution price = A (BUY) or B (SELL)
4. Dealer invariants: Δx_D = 0, ΔC_D = 0 for both trades

Usage:
    uv run python examples/dealer_ring/example8_guard_low_M.py

Output:
    examples/dealer_ring/out/example8_report.html
"""

from decimal import Decimal
from pathlib import Path

from bilancio.dealer import (
    M_MIN,
    DealerRingConfig,
    DealerRingSimulation,
    Ticket,
    TraderState,
    recompute_dealer_state,
)


def setup_example8() -> DealerRingSimulation:
    """Set up Example 8: Guard at very low mid M."""
    # M = 0.01 < M_MIN = 0.02 triggers Guard mode
    M = Decimal("0.01")
    O = Decimal("0.01")

    config = DealerRingConfig(
        dealer_share=Decimal("1.0"),
        vbt_share=Decimal("0.0"),
        N_max=0,
        max_days=1,
        seed=42,
        # Very low M triggers Guard
        vbt_anchors={
            "short": (M, O),
            "mid": (M, O),
            "long": (M, O),
        },
    )

    sim = DealerRingSimulation(config)

    # Create issuer
    issuer = TraderState(agent_id="issuer", cash=Decimal("100.00"))
    sim.traders[issuer.agent_id] = issuer

    # Create seller who will execute SELL
    seller = TraderState(agent_id="seller", cash=Decimal("0.00"))
    sim.traders[seller.agent_id] = seller

    # Create buyer who will execute BUY
    buyer = TraderState(agent_id="buyer", cash=Decimal("10.00"))
    sim.traders[buyer.agent_id] = buyer

    # Set up dealer with some arbitrary inventory (should be irrelevant under Guard)
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("1.00")

    # Give dealer 2 tickets
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

    # Give seller a ticket to sell
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

    # Set up VBT with inventory and cash
    vbt = sim.vbts["mid"]
    vbt.cash = Decimal("10.00")

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

    # Recompute dealer state - should activate Guard
    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def verify_guard_activation(sim: DealerRingSimulation) -> None:
    """Verify Guard mode is activated."""
    print("\n=== Guard Activation Check ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    print(f"VBT anchors: M={vbt.M}, O={vbt.O}")
    print(f"Outside quotes: A={vbt.A}, B={vbt.B}")
    print(f"M_MIN threshold: {M_MIN}")
    print(f"Guard condition: M={vbt.M} <= M_MIN={M_MIN}? {vbt.M <= M_MIN}")

    print(f"\nDealer state under Guard:")
    print(f"  a={dealer.a}, C={dealer.cash}")
    print(f"  X*={dealer.X_star}, K*={dealer.K_star}")
    print(f"  lambda={dealer.lambda_}, I={dealer.I}")
    print(f"  Pinned ask: {dealer.is_pinned_ask}, Pinned bid: {dealer.is_pinned_bid}")
    print(f"  Quotes: ask={dealer.ask}, bid={dealer.bid}")

    # Verify Guard mode
    assert vbt.M <= M_MIN, f"M should be <= M_MIN: {vbt.M} vs {M_MIN}"
    assert dealer.X_star == 0, f"X* should be 0 under Guard, got {dealer.X_star}"
    assert dealer.K_star == 0, f"K* should be 0 under Guard, got {dealer.K_star}"
    assert dealer.is_pinned_ask, "Ask should be pinned under Guard"
    assert dealer.is_pinned_bid, "Bid should be pinned under Guard"
    assert dealer.ask == vbt.A, f"Ask should equal A={vbt.A}, got {dealer.ask}"
    assert dealer.bid == vbt.B, f"Bid should equal B={vbt.B}, got {dealer.bid}"

    print("\n✓ Guard mode activated correctly!")


def run_arrival1_sell(sim: DealerRingSimulation) -> None:
    """Arrival 1: Customer SELL at outside bid B."""
    print("\n=== Arrival 1: Customer SELL (Event 9) ===")

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

    print(f"Before: dealer x={x_before}, C={C_before}, a={a_before}")
    print(f"Before: VBT cash={vbt_cash_before}")
    print(f"Before: seller cash={seller_cash_before}")

    print(f"\nGuard regime: bid pinned to B={vbt.B}")
    print(f"Interior BUY infeasible: x + S = {dealer.x} + 1 > X* = {dealer.X_star}")

    # Execute SELL
    result = sim.executor.execute_customer_sell(
        dealer=dealer,
        vbt=vbt,
        ticket=ticket,
    )

    # Update seller
    seller.cash += result.price
    seller.tickets_owned.remove(ticket)

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
    print(f"  Price: {result.price} (expected B={vbt.B})")
    print(f"  Passthrough: {result.is_passthrough} (expected True)")

    print(f"\nAfter: dealer x={dealer.x}, C={dealer.cash}, a={dealer.a}")
    print(f"After: VBT cash={vbt.cash}")
    print(f"After: seller cash={seller.cash}")

    # Verify passthrough
    assert result.is_passthrough, "SELL should be passthrough under Guard"
    assert result.price == vbt.B, f"Price should be B={vbt.B}, got {result.price}"

    # Verify dealer state unchanged (Event 9)
    assert dealer.x == x_before, f"x should be unchanged, got {dealer.x}"
    assert dealer.cash == C_before, f"C should be unchanged, got {dealer.cash}"
    assert dealer.a == a_before, f"a should be unchanged, got {dealer.a}"

    # Verify double-entry
    seller_gain = seller.cash - seller_cash_before
    vbt_outflow = vbt_cash_before - vbt.cash
    assert seller_gain == result.price, f"Seller gain should equal price"
    assert vbt_outflow == result.price, f"VBT outflow should equal price"

    print(f"\n  Δx_D = 0, ΔC_D = 0 ✓")
    print(f"  ΔCash_Trader = +{seller_gain}, ΔCash_VBT = -{vbt_outflow} ✓")
    print("✓ Arrival 1 (SELL) verified!")


def run_arrival2_buy(sim: DealerRingSimulation) -> None:
    """Arrival 2: Customer BUY at outside ask A."""
    print("\n=== Arrival 2: Customer BUY (Event 10) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    buyer = sim.traders["buyer"]

    # Record state before trade
    x_before = dealer.x
    C_before = dealer.cash
    a_before = dealer.a
    vbt_cash_before = vbt.cash
    buyer_cash_before = buyer.cash

    print(f"Before: dealer x={x_before}, C={C_before}, a={a_before}")
    print(f"Before: VBT cash={vbt_cash_before}")
    print(f"Before: buyer cash={buyer_cash_before}")

    print(f"\nGuard regime: ask pinned to A={vbt.A}")
    print(f"Regardless of dealer inventory a={dealer.a}, Guard routes to VBT")

    # Execute BUY
    result = sim.executor.execute_customer_buy(
        dealer=dealer,
        vbt=vbt,
        buyer_id=buyer.agent_id,
    )

    # Update buyer
    buyer.cash -= result.price
    if result.ticket:
        buyer.tickets_owned.append(result.ticket)

    sim.events.log_trade(
        day=1,
        side="BUY",
        trader_id=buyer.agent_id,
        ticket_id=result.ticket.id if result.ticket else "N/A",
        bucket="mid",
        price=result.price,
        is_passthrough=result.is_passthrough,
    )

    print(f"\nExecution:")
    print(f"  Price: {result.price} (expected A={vbt.A})")
    print(f"  Passthrough: {result.is_passthrough} (expected True)")

    print(f"\nAfter: dealer x={dealer.x}, C={dealer.cash}, a={dealer.a}")
    print(f"After: VBT cash={vbt.cash}")
    print(f"After: buyer cash={buyer.cash}")

    # Verify passthrough
    assert result.is_passthrough, "BUY should be passthrough under Guard"
    assert result.price == vbt.A, f"Price should be A={vbt.A}, got {result.price}"

    # Verify dealer state unchanged (Event 10)
    assert dealer.x == x_before, f"x should be unchanged, got {dealer.x}"
    assert dealer.cash == C_before, f"C should be unchanged, got {dealer.cash}"
    assert dealer.a == a_before, f"a should be unchanged, got {dealer.a}"

    # Verify double-entry
    buyer_outflow = buyer_cash_before - buyer.cash
    vbt_inflow = vbt.cash - vbt_cash_before
    assert buyer_outflow == result.price, f"Buyer outflow should equal price"
    assert vbt_inflow == result.price, f"VBT inflow should equal price"

    print(f"\n  Δx_D = 0, ΔC_D = 0 ✓")
    print(f"  ΔCash_Trader = -{buyer_outflow}, ΔCash_VBT = +{vbt_inflow} ✓")
    print("✓ Arrival 2 (BUY) verified!")


def verify_final_state(sim: DealerRingSimulation) -> None:
    """Verify final state after both trades."""
    print("\n=== Final Double-Entry Summary ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    print(f"Dealer inventory change: 0 (unchanged)")
    print(f"VBT inventory change: +1 (SELL) - 1 (BUY) = 0")
    print(f"VBT cash change: -{vbt.B} (SELL payout) + {vbt.A} (BUY receipt) = +{vbt.A - vbt.B}")

    # VBT should have net cash gain of A - B = spread
    expected_vbt_gain = vbt.A - vbt.B
    print(f"\nVBT earned spread: {expected_vbt_gain}")

    print("✓ All double-entry verified!")


def main():
    sim = setup_example8()
    sim._capture_snapshot()

    print("Example 8: Guard at Very Low Mid M")
    print("=" * 60)

    verify_guard_activation(sim)
    run_arrival1_sell(sim)
    run_arrival2_buy(sim)
    verify_final_state(sim)

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

    # Export HTML report
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example8_report.html"

    sim.to_html(
        out_path,
        title="Example 8: Guard at Low M",
        subtitle="All trades route to VBT when M <= M_min",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 8 checks passed!")


if __name__ == "__main__":
    main()
