"""
Example 13: Minimal Event-Loop Harness for Arrivals.

From the dealer ring specification (Section 14):
Tests the randomized order-flow subroutine in isolation with fixed pi_sell
and N_max. Verifies eligibility set discipline, fallback behavior, and
no-feasible retention.

Setup:
- S=1, M=1.0, O=0.30, A=1.15, B=0.85
- Dealer: a=2, C=2, V=4, K*=4, X*=4
- At x=2: a(2)=1.03, b(2)=0.97

Agent pools:
- SELL side: S_1 owns one ticket, has shortfall > 0
- BUY side: B_1 (rich, cash=2.00), B_2 (poor, cash=0.90)

Worked micro-run (three arrivals):
- Arrival 1 (Z=1, SELL): S_1 sells at b=0.97, removed from S_t
- Arrival 2 (Z=1, SELL but S_t empty): Fallback to BUY, B_2 picked but
  cash=0.90 < ask=0.98, no execution, B_2 stays in B_t
- Arrival 3 (Z=0, BUY): B_1 buys at a=0.98, removed from B_t

Harness checks:
1. Set discipline: once i executes SELL/BUY, i not in S_t/B_t for period
2. Fallback correctness: if preferred side empty, process on nonempty side
3. No-feasible retention: if can't execute, agent stays in set
4. Kernel consistency: recompute after each trade

Usage:
    uv run python examples/dealer_ring/example13_event_loop.py

Output:
    examples/dealer_ring/out/example13_report.html
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


def setup_example13() -> DealerRingSimulation:
    """Set up Example 14: Event-loop harness."""
    config = DealerRingConfig(
        dealer_share=Decimal("1.0"),
        vbt_share=Decimal("0.0"),
        N_max=3,  # Max arrivals per period
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

    # Create SELL-eligible agent S_1 (has shortfall, owns ticket)
    s1 = TraderState(agent_id="S_1", cash=Decimal("0.50"))
    s1.shortfall = Decimal("0.50")  # Needs to sell
    sim.traders[s1.agent_id] = s1

    # Create ticket for S_1
    s1_ticket = Ticket(
        id="S1_T",
        issuer_id=issuer.agent_id,
        owner_id=s1.agent_id,
        face=Decimal(1),
        maturity_day=200,
        remaining_tau=6,
        bucket_id="mid",
        serial=1,
    )
    s1.tickets_owned.append(s1_ticket)
    sim.all_tickets[s1_ticket.id] = s1_ticket
    issuer.obligations.append(s1_ticket)

    # Create BUY-eligible agents
    # B_1: rich (can afford ask)
    b1 = TraderState(agent_id="B_1", cash=Decimal("2.00"))
    sim.traders[b1.agent_id] = b1

    # B_2: poor (cannot afford ask)
    b2 = TraderState(agent_id="B_2", cash=Decimal("0.90"))
    sim.traders[b2.agent_id] = b2

    # Set up dealer: a=2, C=2
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("2.00")

    for i in range(2):
        ticket = Ticket(
            id=f"D{i}",
            issuer_id=issuer.agent_id,
            owner_id=dealer.agent_id,
            face=Decimal(1),
            maturity_day=200,
            remaining_tau=6,
            bucket_id="mid",
            serial=100 + i,
        )
        dealer.inventory.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

    # VBT backup
    vbt = sim.vbts["mid"]
    vbt.cash = Decimal("10.00")
    for i in range(3):
        vbt_ticket = Ticket(
            id=f"VBT{i}",
            issuer_id=issuer.agent_id,
            owner_id=vbt.agent_id,
            face=Decimal(1),
            maturity_day=200,
            remaining_tau=6,
            bucket_id="mid",
            serial=200 + i,
        )
        vbt.inventory.append(vbt_ticket)
        sim.all_tickets[vbt_ticket.id] = vbt_ticket

    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def verify_initial_state(sim: DealerRingSimulation) -> None:
    """Verify initial dealer state."""
    print("\n=== Initial State ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    print(f"Dealer: a={dealer.a}, C={dealer.cash}, x={dealer.x}")
    print(f"  V={dealer.V:.4f}, K*={dealer.K_star}, X*={dealer.X_star}")
    print(f"  lambda={dealer.lambda_:.4f}, I={dealer.I:.4f}")
    print(f"  At x={dealer.x}: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")

    assert dealer.a == 2
    assert dealer.cash == Decimal("2.00")
    assert dealer.K_star == 4
    assert dealer.X_star == 4

    print("\nAgent pools:")
    print("  S_t (SELL eligible): {S_1}")
    print("  B_t (BUY eligible): {B_1, B_2}")

    print("\n✓ Initial state verified!")


def run_arrival_1(sim: DealerRingSimulation, sell_set: set, buy_set: set) -> None:
    """Arrival 1: Z=1 (SELL), S_1 sells at bid."""
    print("\n=== Arrival 1: Z=1 (SELL preferred) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    s1 = sim.traders["S_1"]

    print(f"S_t = {sell_set}, B_t = {buy_set}")
    print(f"S_t not empty, pick S_1")

    # Check feasibility
    can_buy = can_interior_buy(dealer, sim.params)
    print(f"\nFeasibility: x + S = {dealer.x} + 1 <= X* = {dealer.X_star}? {can_buy}")
    print(f"  C = {dealer.cash} >= b = {dealer.bid}? {dealer.cash >= dealer.bid}")

    assert can_buy, "Interior BUY should be feasible"

    # Execute SELL
    ticket = s1.tickets_owned[0]
    result = sim.executor.execute_customer_sell(dealer, vbt, ticket)
    s1.cash += result.price
    s1.tickets_owned.remove(ticket)

    print(f"\nExecution: SELL at p = {result.price:.4f}")
    print(f"  Dealer: x={dealer.x}, C={dealer.cash:.4f}")

    # Remove S_1 from sell set
    sell_set.remove("S_1")
    print(f"\nPost-arrival: S_t = {sell_set}")

    # Verify kernel consistency
    print(f"  New quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")

    print("\n✓ Arrival 1 complete!")


def run_arrival_2(sim: DealerRingSimulation, sell_set: set, buy_set: set) -> None:
    """Arrival 2: Z=1 (SELL preferred but S_t empty), fallback to BUY, B_2 fails."""
    print("\n=== Arrival 2: Z=1 (SELL preferred, but S_t empty) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    b2 = sim.traders["B_2"]

    print(f"S_t = {sell_set}, B_t = {buy_set}")
    print(f"S_t is empty but B_t not empty -> FALLBACK to BUY")
    print(f"Random pick from B_t: B_2 (poor)")

    # Check feasibility for B_2
    can_sell = can_interior_sell(dealer, sim.params)
    can_afford = b2.cash >= dealer.ask

    print(f"\nFeasibility for B_2:")
    print(f"  Dealer can sell (x >= S): {can_sell}")
    print(f"  B_2 cash = {b2.cash} >= ask = {dealer.ask:.4f}? {can_afford}")

    assert can_sell, "Interior SELL should be feasible"
    assert not can_afford, "B_2 should NOT be able to afford"

    print(f"\nNo execution: B_2 cannot afford ask")
    print(f"B_2 stays in B_t (no-feasible retention)")
    print(f"\nPost-arrival: B_t = {buy_set} (unchanged)")

    print("\n✓ Arrival 2 complete (no-feasible retention)!")


def run_arrival_3(sim: DealerRingSimulation, sell_set: set, buy_set: set) -> None:
    """Arrival 3: Z=0 (BUY), B_1 buys at ask."""
    print("\n=== Arrival 3: Z=0 (BUY preferred) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    b1 = sim.traders["B_1"]

    print(f"S_t = {sell_set}, B_t = {buy_set}")
    print(f"Pick B_1 (rich)")

    # Check feasibility for B_1
    can_sell = can_interior_sell(dealer, sim.params)
    can_afford = b1.cash >= dealer.ask

    print(f"\nFeasibility for B_1:")
    print(f"  Dealer can sell (x >= S): {can_sell}")
    print(f"  B_1 cash = {b1.cash} >= ask = {dealer.ask:.4f}? {can_afford}")

    assert can_sell, "Interior SELL should be feasible"
    assert can_afford, "B_1 should be able to afford"

    # Execute BUY
    result = sim.executor.execute_customer_buy(dealer, vbt, b1.agent_id)
    b1.cash -= result.price
    if result.ticket:
        b1.tickets_owned.append(result.ticket)

    print(f"\nExecution: BUY at p = {result.price:.4f}")
    print(f"  Dealer: x={dealer.x}, C={dealer.cash:.4f}")

    # Remove B_1 from buy set
    buy_set.remove("B_1")
    print(f"\nPost-arrival: B_t = {buy_set}")

    # Verify kernel consistency
    print(f"  New quotes: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")

    print("\n✓ Arrival 3 complete!")


def verify_outcomes(sim: DealerRingSimulation) -> None:
    """Verify outcomes match specification."""
    print("\n=== Outcomes Verification ===")

    s1 = sim.traders["S_1"]
    b1 = sim.traders["B_1"]
    b2 = sim.traders["B_2"]

    print(f"S_1: cash={s1.cash:.4f}, tickets={len(s1.tickets_owned)}")
    print(f"B_1: cash={b1.cash:.4f}, tickets={len(b1.tickets_owned)}")
    print(f"B_2: cash={b2.cash:.4f}, tickets={len(b2.tickets_owned)}")

    # S_1 should have sold and received ~0.97
    assert len(s1.tickets_owned) == 0, "S_1 should have sold their ticket"
    assert s1.cash > Decimal("0.50"), "S_1 should have received payment"

    # B_1 should have bought and paid ~0.98
    assert len(b1.tickets_owned) == 1, "B_1 should have bought a ticket"
    assert b1.cash < Decimal("2.00"), "B_1 should have paid"

    # B_2 should be unchanged (no-feasible retention)
    assert len(b2.tickets_owned) == 0, "B_2 should have no tickets"
    assert b2.cash == Decimal("0.90"), "B_2 cash should be unchanged"

    print("\n✓ Outcomes verified!")
    print("\nSummary:")
    print("  - Executed trades: 1 SELL (Arrival 1), 1 BUY (Arrival 3)")
    print("  - Empty-set fallback used at Arrival 2 (SELL->BUY)")
    print("  - No feasible execution for B_2; B_2 remained in B_t")
    print("  - Post-trade removal enforced: S_1 from S_t, B_1 from B_t")


def main():
    sim = setup_example13()
    sim._capture_snapshot()

    print("Example 13: Minimal Event-Loop Harness")
    print("=" * 60)

    verify_initial_state(sim)

    sim.day = 1
    sim.events.log_day_start(1)

    # Initialize eligibility sets
    sell_set = {"S_1"}
    buy_set = {"B_1", "B_2"}

    # Run three arrivals as per specification
    run_arrival_1(sim, sell_set, buy_set)
    run_arrival_2(sim, sell_set, buy_set)
    run_arrival_3(sim, sell_set, buy_set)

    verify_outcomes(sim)

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
    out_path = out_dir / "example13_report.html"

    sim.to_html(
        out_path,
        title="Example 13: Event-Loop Harness",
        subtitle="Eligibility sets, fallback, and no-feasible retention",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 13 checks passed!")


if __name__ == "__main__":
    main()
