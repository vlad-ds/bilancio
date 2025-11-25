"""
Example 5: Dealer Earns Over Time and Inventory Grows.

From the dealer ring specification:
- One bucket with dealer and VBT
- M=1.0, O=0.30, A=1.15, B=0.85
- Initial: a=2, C=2 → V=4, K*=4, X*=4, x=2
- λ=1/5=0.20, I=0.06, p(x)=1-0.05(x-2)
- At x=2: a(2)=1.03, b(2)=0.97
- Invariant: E = C + M*a = 4

Trade path (three trades):

Trade 1: Customer SELL (dealer buys) at b(2)=0.97
- x: 2→3, C: 2→1.03
- p(3)=0.95, a(3)=0.98, b(3)=0.92
- E = 1.03 + 3 = 4.03

Trade 2: Customer BUY (dealer sells) at a(3)=0.98
- x: 3→2, C: 1.03→2.01
- p(2)=1, a(2)=1.03, b(2)=0.97
- E = 2.01 + 2 = 4.01

Trade 3: Customer SELL (dealer buys) at b(2)=0.97
- x: 2→3, C: 2.01→1.04
- p(3)=0.95, a(3)=0.98, b(3)=0.92
- E = 1.04 + 3 = 4.04

Outcome: (a, C, E) goes from (2, 2, 4) to (3, 1.04, 4.04)
- Inventory grows 2→3
- Equity grows 4→4.04 (dealer earns through bid-ask spread)

Invariant checks at each step:
- E = C + M*a equals computed V
- a(x) >= b(x)
- B <= b(x) <= a(x) <= A (no outside breach)

Usage:
    uv run python examples/dealer_ring/example5_dealer_earns.py

Output:
    examples/dealer_ring/out/example5_report.html
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


def setup_example5() -> DealerRingSimulation:
    """Set up Example 5 scenario: dealer earning through trades."""
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
    issuer = TraderState(
        agent_id="issuer",
        cash=Decimal("100.00"),
    )
    sim.traders[issuer.agent_id] = issuer

    # Create sellers (for SELL trades)
    seller1 = TraderState(agent_id="seller_1", cash=Decimal("0.00"))
    seller2 = TraderState(agent_id="seller_2", cash=Decimal("0.00"))

    # Create buyer (for BUY trade)
    buyer = TraderState(agent_id="buyer_1", cash=Decimal("10.00"))

    sim.traders[seller1.agent_id] = seller1
    sim.traders[seller2.agent_id] = seller2
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
            remaining_tau=6,
            bucket_id="mid",
            serial=i,
        )
        dealer.inventory.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

    # Create tickets for sellers to sell
    sell_ticket1 = Ticket(
        id="S1",
        issuer_id=issuer.agent_id,
        owner_id=seller1.agent_id,
        face=Decimal(1),
        maturity_day=200,
        remaining_tau=6,
        bucket_id="mid",
        serial=10,
    )
    seller1.tickets_owned.append(sell_ticket1)
    sim.all_tickets[sell_ticket1.id] = sell_ticket1
    issuer.obligations.append(sell_ticket1)

    sell_ticket2 = Ticket(
        id="S2",
        issuer_id=issuer.agent_id,
        owner_id=seller2.agent_id,
        face=Decimal(1),
        maturity_day=200,
        remaining_tau=6,
        bucket_id="mid",
        serial=11,
    )
    seller2.tickets_owned.append(sell_ticket2)
    sim.all_tickets[sell_ticket2.id] = sell_ticket2
    issuer.obligations.append(sell_ticket2)

    # Create VBT inventory (backup)
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


def check_invariants(dealer, vbt, label: str) -> None:
    """Check invariants after each trade."""
    M = vbt.M
    E = dealer.cash + M * dealer.a

    print(f"  Invariants ({label}):")
    print(f"    E = C + M*a = {dealer.cash:.4f} + {M}*{dealer.a} = {E:.4f}")
    print(f"    V = {dealer.V:.4f} (should equal E)")
    print(f"    a(x) >= b(x): {dealer.ask:.4f} >= {dealer.bid:.4f} = {dealer.ask >= dealer.bid}")
    print(f"    B <= b(x) <= a(x) <= A: {vbt.B} <= {dealer.bid:.4f} <= {dealer.ask:.4f} <= {vbt.A}")

    assert abs(E - dealer.V) < Decimal("0.0001"), f"E != V: {E} != {dealer.V}"
    assert dealer.ask >= dealer.bid, "ask < bid"
    assert dealer.bid >= vbt.B, f"bid < B: {dealer.bid} < {vbt.B}"
    assert dealer.ask <= vbt.A, f"ask > A: {dealer.ask} > {vbt.A}"

    print("    ✓ All invariants hold")


def verify_initial_state(sim: DealerRingSimulation) -> None:
    """Verify initial state."""
    print("\n=== Initial State ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    print(f"Dealer: a={dealer.a}, C={dealer.cash}, x={dealer.x}")
    print(f"  Quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print(f"  Expected: a=2, C=2, x=2, ask=1.03, bid=0.97")

    assert dealer.a == 2
    assert dealer.cash == Decimal("2.00")
    assert abs(dealer.ask - Decimal("1.03")) < Decimal("0.001")
    assert abs(dealer.bid - Decimal("0.97")) < Decimal("0.001")

    check_invariants(dealer, vbt, "initial")
    print("✓ Initial state verified!")


def run_trade1(sim: DealerRingSimulation) -> None:
    """Trade 1: Customer SELL (dealer buys) at b(2)=0.97."""
    print("\n=== Trade 1: Customer SELL at bid 0.97 ===")

    sim.day = 1
    sim.events.log_day_start(1)

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    seller = sim.traders["seller_1"]
    ticket = seller.tickets_owned[0]

    bid_before = dealer.bid
    print(f"Bid before: {bid_before:.4f}, expected: 0.97")
    assert abs(bid_before - Decimal("0.97")) < Decimal("0.001")

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

    print(f"Executed at: {result.price:.4f}, passthrough: {result.is_passthrough}")
    print(f"Dealer after: a={dealer.a}, x={dealer.x}, C={dealer.cash:.4f}")
    print(f"  Quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print(f"  Expected: x=3, C=1.03, ask=0.98, bid=0.92")

    assert not result.is_passthrough
    assert dealer.x == 3
    assert abs(dealer.cash - Decimal("1.03")) < Decimal("0.001")
    assert abs(dealer.ask - Decimal("0.98")) < Decimal("0.001")
    assert abs(dealer.bid - Decimal("0.92")) < Decimal("0.001")

    check_invariants(dealer, vbt, "after Trade 1")
    print("✓ Trade 1 verified!")


def run_trade2(sim: DealerRingSimulation) -> None:
    """Trade 2: Customer BUY (dealer sells) at a(3)=0.98."""
    print("\n=== Trade 2: Customer BUY at ask 0.98 ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    buyer = sim.traders["buyer_1"]

    ask_before = dealer.ask
    print(f"Ask before: {ask_before:.4f}, expected: 0.98")
    assert abs(ask_before - Decimal("0.98")) < Decimal("0.001")

    # Execute BUY
    result = sim.executor.execute_customer_buy(
        dealer=dealer,
        vbt=vbt,
        buyer_id=buyer.agent_id,
    )

    # Update buyer
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
    print(f"Dealer after: a={dealer.a}, x={dealer.x}, C={dealer.cash:.4f}")
    print(f"  Quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print(f"  Expected: x=2, C=2.01, ask=1.03, bid=0.97")

    assert not result.is_passthrough
    assert dealer.x == 2
    assert abs(dealer.cash - Decimal("2.01")) < Decimal("0.001")
    assert abs(dealer.ask - Decimal("1.03")) < Decimal("0.001")
    assert abs(dealer.bid - Decimal("0.97")) < Decimal("0.001")

    check_invariants(dealer, vbt, "after Trade 2")
    print("✓ Trade 2 verified!")


def run_trade3(sim: DealerRingSimulation) -> None:
    """Trade 3: Customer SELL (dealer buys) at b(2)=0.97."""
    print("\n=== Trade 3: Customer SELL at bid 0.97 ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    seller = sim.traders["seller_2"]
    ticket = seller.tickets_owned[0]

    bid_before = dealer.bid
    print(f"Bid before: {bid_before:.4f}, expected: 0.97")
    assert abs(bid_before - Decimal("0.97")) < Decimal("0.001")

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

    print(f"Executed at: {result.price:.4f}, passthrough: {result.is_passthrough}")
    print(f"Dealer after: a={dealer.a}, x={dealer.x}, C={dealer.cash:.4f}")
    print(f"  Quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print(f"  Expected: x=3, C=1.04, ask=0.98, bid=0.92")

    assert not result.is_passthrough
    assert dealer.x == 3
    assert abs(dealer.cash - Decimal("1.04")) < Decimal("0.001")
    assert abs(dealer.ask - Decimal("0.98")) < Decimal("0.001")
    assert abs(dealer.bid - Decimal("0.92")) < Decimal("0.001")

    check_invariants(dealer, vbt, "after Trade 3")
    print("✓ Trade 3 verified!")


def main():
    sim = setup_example5()
    sim._capture_snapshot()

    print("Example 5: Dealer Earns Over Time and Inventory Grows")
    print("=" * 60)

    verify_initial_state(sim)
    run_trade1(sim)
    run_trade2(sim)
    run_trade3(sim)

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
    print(f"Initial: (a, C, E) = (2, 2, 4)")
    E_final = dealer.cash + vbt.M * dealer.a
    print(f"Final:   (a, C, E) = ({dealer.a}, {dealer.cash:.4f}, {E_final:.4f})")
    print(f"\nDealer earned: E_final - E_initial = {E_final - 4:.4f}")
    print("This profit comes from the bid-ask spread (buy at 0.97, sell at 0.98).")

    # Export HTML report
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example5_report.html"

    sim.to_html(
        out_path,
        title="Example 5: Dealer Earns Over Time",
        subtitle="Inventory grows and equity increases through bid-ask spread",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 5 checks passed!")


if __name__ == "__main__":
    main()
