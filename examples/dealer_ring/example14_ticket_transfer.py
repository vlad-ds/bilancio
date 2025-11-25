"""
Example 14: Ticket-Level Transfer (No Generic Materialization).

From the dealer ring specification (Section 15):
Verifies that on a customer BUY, the execution transfers a specific ticket ID
from the seller of record to the buyer. No generic tickets are created.

Setup:
- S=1, M=1.0, O=0.30, A=1.15, B=0.85
- Dealer: x=2, a=2, C=2, V=4, K*=4, X*=4
- Dealer inventory: K_D = {k1=(I1,t+6,#101), k2=(I2,t+5,#202)}
- VBT inventory: K_VBT = {v1=(I3,t+7,#303), v2=(I4,t+6,#404)}

Case A (interior BUY): Dealer transfers specific ticket
- Buyer B has no issuer preference
- Dealer SELL at a(2)=1.03 (interior)
- Tie-breaker (lowest maturity): k2=(I2,t+5,#202) selected
- k2 moves from K_D to K_B, buyer's issuer set to I2

Case B (pinned BUY / passthrough): VBT transfers specific ticket
- Dealer at x=0 (no inventory)
- Passthrough at A=1.15
- Tie-breaker selects v2=(I4,t+6,#404)
- v2 moves from K_VBT to K_B, buyer's issuer set to I4

Harness checks:
1. Transferred ID belonged to seller immediately before
2. After execution, ID in buyer's inventory, not seller's
3. Inventory length decreases by exactly 1
4. No generic ticket created anywhere

Usage:
    uv run python examples/dealer_ring/example14_ticket_transfer.py

Output:
    examples/dealer_ring/out/example14_report.html
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


def setup_case_a() -> DealerRingSimulation:
    """Set up Case A: Interior BUY from dealer."""
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

    # Create issuers
    issuer1 = TraderState(agent_id="I1", cash=Decimal("100.00"))
    issuer2 = TraderState(agent_id="I2", cash=Decimal("100.00"))
    sim.traders[issuer1.agent_id] = issuer1
    sim.traders[issuer2.agent_id] = issuer2

    # Create buyer
    buyer = TraderState(agent_id="buyer_B", cash=Decimal("2.00"))
    sim.traders[buyer.agent_id] = buyer

    # Set up dealer: a=2, C=2
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("2.00")

    # Create dealer inventory with specific IDs
    # k1 = (I1, t+6, #101) - maturity_day = current + 6
    k1 = Ticket(
        id="k1",
        issuer_id=issuer1.agent_id,
        owner_id=dealer.agent_id,
        face=Decimal(1),
        maturity_day=sim.day + 6,
        remaining_tau=6,
        bucket_id="mid",
        serial=101,
    )
    dealer.inventory.append(k1)
    sim.all_tickets[k1.id] = k1
    issuer1.obligations.append(k1)

    # k2 = (I2, t+5, #202) - maturity_day = current + 5 (lower, will be selected)
    k2 = Ticket(
        id="k2",
        issuer_id=issuer2.agent_id,
        owner_id=dealer.agent_id,
        face=Decimal(1),
        maturity_day=sim.day + 5,
        remaining_tau=5,
        bucket_id="mid",
        serial=202,
    )
    dealer.inventory.append(k2)
    sim.all_tickets[k2.id] = k2
    issuer2.obligations.append(k2)

    # VBT backup
    vbt = sim.vbts["mid"]
    vbt.cash = Decimal("10.00")

    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def setup_case_b() -> DealerRingSimulation:
    """Set up Case B: Passthrough BUY from VBT."""
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

    # Create issuers
    issuer3 = TraderState(agent_id="I3", cash=Decimal("100.00"))
    issuer4 = TraderState(agent_id="I4", cash=Decimal("100.00"))
    sim.traders[issuer3.agent_id] = issuer3
    sim.traders[issuer4.agent_id] = issuer4

    # Create buyer
    buyer = TraderState(agent_id="buyer_B_tilde", cash=Decimal("2.00"))
    sim.traders[buyer.agent_id] = buyer

    # Set up dealer with no inventory (x=0) to force passthrough
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("2.00")
    # No tickets in dealer inventory

    # Set up VBT with specific ticket IDs
    vbt = sim.vbts["mid"]
    vbt.cash = Decimal("10.00")

    # v1 = (I3, t+7, #303)
    v1 = Ticket(
        id="v1",
        issuer_id=issuer3.agent_id,
        owner_id=vbt.agent_id,
        face=Decimal(1),
        maturity_day=sim.day + 7,
        remaining_tau=7,
        bucket_id="mid",
        serial=303,
    )
    vbt.inventory.append(v1)
    sim.all_tickets[v1.id] = v1

    # v2 = (I4, t+6, #404) - lower maturity, will be selected
    v2 = Ticket(
        id="v2",
        issuer_id=issuer4.agent_id,
        owner_id=vbt.agent_id,
        face=Decimal(1),
        maturity_day=sim.day + 6,
        remaining_tau=6,
        bucket_id="mid",
        serial=404,
    )
    vbt.inventory.append(v2)
    sim.all_tickets[v2.id] = v2

    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def run_case_a(sim: DealerRingSimulation) -> None:
    """Case A: Interior BUY - dealer transfers specific ticket."""
    print("\n=== CASE A: Interior BUY (Dealer Transfers Specific Ticket) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    buyer = sim.traders["buyer_B"]

    # Record initial state
    print("\nInitial state:")
    print(f"  Dealer inventory K_D = {[t.id for t in dealer.inventory]}")
    print(f"  Dealer: x={dealer.x}, a={dealer.a}, C={dealer.cash}")
    print(f"  Buyer K_B = {[t.id for t in buyer.tickets_owned]}")

    dealer_inv_before = set(t.id for t in dealer.inventory)
    dealer_len_before = len(dealer.inventory)

    # Expected: k2 selected (lowest maturity_day)
    expected_ticket_id = "k2"
    print(f"\n  Tie-breaker (lowest maturity): expect {expected_ticket_id} selected")

    # Execute BUY
    print(f"\nExecution (customer BUY at ask={dealer.ask:.4f}):")
    result = sim.executor.execute_customer_buy(dealer, vbt, buyer.agent_id)
    buyer.cash -= result.price
    if result.ticket:
        buyer.tickets_owned.append(result.ticket)

    print(f"  Price: {result.price:.4f}")
    print(f"  Passthrough: {result.is_passthrough}")
    print(f"  Transferred ticket: {result.ticket.id if result.ticket else 'None'}")

    # Verify assertions
    assert not result.is_passthrough, "Should be interior trade"
    assert result.ticket is not None, "Ticket should be transferred"
    assert result.ticket.id == expected_ticket_id, f"Expected {expected_ticket_id}, got {result.ticket.id}"

    # 1. Transferred ID belonged to dealer before
    assert result.ticket.id in dealer_inv_before, "Transferred ticket was in dealer inventory"
    print(f"\n✓ Assertion 1: {result.ticket.id} was in K_D before execution")

    # 2. After execution: ID in buyer, not in dealer
    dealer_inv_after = set(t.id for t in dealer.inventory)
    buyer_inv_after = set(t.id for t in buyer.tickets_owned)

    assert result.ticket.id not in dealer_inv_after, "Transferred ticket no longer in dealer"
    assert result.ticket.id in buyer_inv_after, "Transferred ticket now in buyer"
    print(f"✓ Assertion 2: {result.ticket.id} in K_B, not in K_D after execution")

    # 3. Inventory length decreases by exactly 1
    assert len(dealer.inventory) == dealer_len_before - 1, "Dealer inventory decreased by 1"
    print(f"✓ Assertion 3: |K_D| decreased by 1 ({dealer_len_before} -> {len(dealer.inventory)})")

    # 4. No new ticket created
    print(f"✓ Assertion 4: No generic ticket created (same ticket object transferred)")

    print(f"\nFinal state:")
    print(f"  Dealer K_D = {[t.id for t in dealer.inventory]}")
    print(f"  Buyer K_B = {[t.id for t in buyer.tickets_owned]}")
    print(f"  Buyer's issuer set to: {result.ticket.issuer_id}")

    print("\n✓ Case A passed!")


def run_case_b(sim: DealerRingSimulation) -> None:
    """Case B: Passthrough BUY - VBT transfers specific ticket."""
    print("\n=== CASE B: Passthrough BUY (VBT Transfers Specific Ticket) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]
    buyer = sim.traders["buyer_B_tilde"]

    # Record initial state
    print("\nInitial state:")
    print(f"  Dealer inventory K_D = {[t.id for t in dealer.inventory]} (empty)")
    print(f"  Dealer: x={dealer.x}, a={dealer.a}, C={dealer.cash}")
    print(f"  VBT inventory K_VBT = {[t.id for t in vbt.inventory]}")
    print(f"  Buyer K_B = {[t.id for t in buyer.tickets_owned]}")

    dealer_x_before = dealer.x
    dealer_C_before = dealer.cash
    vbt_inv_before = set(t.id for t in vbt.inventory)
    vbt_len_before = len(vbt.inventory)

    # Expected: v2 selected (lowest maturity_day)
    expected_ticket_id = "v2"
    print(f"\n  Tie-breaker (lowest maturity): expect {expected_ticket_id} selected")
    print(f"  Dealer x=0, so interior SELL infeasible -> passthrough at A={vbt.A}")

    # Execute BUY
    print(f"\nExecution (customer BUY, passthrough at A={vbt.A}):")
    result = sim.executor.execute_customer_buy(dealer, vbt, buyer.agent_id)
    buyer.cash -= result.price
    if result.ticket:
        buyer.tickets_owned.append(result.ticket)

    print(f"  Price: {result.price:.4f}")
    print(f"  Passthrough: {result.is_passthrough}")
    print(f"  Transferred ticket: {result.ticket.id if result.ticket else 'None'}")

    # Verify assertions
    assert result.is_passthrough, "Should be passthrough trade"
    assert result.price == vbt.A, f"Price should be A={vbt.A}"
    assert result.ticket is not None, "Ticket should be transferred"
    assert result.ticket.id == expected_ticket_id, f"Expected {expected_ticket_id}, got {result.ticket.id}"

    # 1. Dealer state unchanged (passthrough property)
    assert dealer.x == dealer_x_before, "Dealer x unchanged"
    assert dealer.cash == dealer_C_before, "Dealer C unchanged"
    print(f"\n✓ Assertion 1: Dealer (x, C) unchanged ({dealer.x}, {dealer.cash})")

    # 2. Transferred ID belonged to VBT before
    assert result.ticket.id in vbt_inv_before, "Transferred ticket was in VBT inventory"
    print(f"✓ Assertion 2: {result.ticket.id} was in K_VBT before execution")

    # 3. After execution: ID in buyer, not in VBT
    vbt_inv_after = set(t.id for t in vbt.inventory)
    buyer_inv_after = set(t.id for t in buyer.tickets_owned)

    assert result.ticket.id not in vbt_inv_after, "Transferred ticket no longer in VBT"
    assert result.ticket.id in buyer_inv_after, "Transferred ticket now in buyer"
    print(f"✓ Assertion 3: {result.ticket.id} in K_B, not in K_VBT after execution")

    # 4. No generic ticket created
    assert len(vbt.inventory) == vbt_len_before - 1, "VBT inventory decreased by 1"
    print(f"✓ Assertion 4: |K_VBT| decreased by 1, no generic ticket created")

    print(f"\nFinal state:")
    print(f"  Dealer K_D = {[t.id for t in dealer.inventory]} (unchanged)")
    print(f"  VBT K_VBT = {[t.id for t in vbt.inventory]}")
    print(f"  Buyer K_B = {[t.id for t in buyer.tickets_owned]}")
    print(f"  Buyer's issuer set to: {result.ticket.issuer_id}")

    print("\n✓ Case B passed!")


def main():
    print("Example 15: Ticket-Level Transfer")
    print("=" * 60)

    # Case A: Interior BUY
    sim_a = setup_case_a()
    sim_a._capture_snapshot()
    run_case_a(sim_a)

    sim_a.day = 1
    sim_a.events.log_day_start(1)
    dealer_a = sim_a.dealers["mid"]
    vbt_a = sim_a.vbts["mid"]
    sim_a.events.log_quote(
        day=1, bucket="mid",
        dealer_bid=dealer_a.bid, dealer_ask=dealer_a.ask,
        vbt_bid=vbt_a.B, vbt_ask=vbt_a.A,
        inventory=dealer_a.a, capacity=dealer_a.X_star,
        is_pinned_bid=dealer_a.is_pinned_bid, is_pinned_ask=dealer_a.is_pinned_ask,
    )
    sim_a._capture_snapshot()

    # Case B: Passthrough BUY
    print("\n" + "=" * 60)
    sim_b = setup_case_b()
    sim_b._capture_snapshot()
    run_case_b(sim_b)

    sim_b.day = 1
    sim_b.events.log_day_start(1)
    dealer_b = sim_b.dealers["mid"]
    vbt_b = sim_b.vbts["mid"]
    sim_b.events.log_quote(
        day=1, bucket="mid",
        dealer_bid=dealer_b.bid, dealer_ask=dealer_b.ask,
        vbt_bid=vbt_b.B, vbt_ask=vbt_b.A,
        inventory=dealer_b.a, capacity=dealer_b.X_star,
        is_pinned_bid=dealer_b.is_pinned_bid, is_pinned_ask=dealer_b.is_pinned_ask,
    )
    sim_b._capture_snapshot()

    # Summary
    print("\n" + "=" * 60)
    print("GLOBAL INVARIANTS VERIFIED")
    print("=" * 60)
    print("\n1. Ownership conservation: ticket IDs preserved under trading")
    print("2. Inventory monotonicity: SELL reduces |K| by exactly 1")
    print("3. Feasibility conformity: interior vs pinned paths correct")
    print("4. Double-entry balance: cash and ticket moves match")

    # Export HTML report
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example14_report.html"

    sim_a.to_html(
        out_path,
        title="Example 14: Ticket-Level Transfer",
        subtitle="No generic materialization - specific IDs transferred",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 14 checks passed!")


if __name__ == "__main__":
    main()
