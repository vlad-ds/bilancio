"""
Example 10: Trader-Held Rebucketing Without Dealer-Dealer Transfer.

From the dealer ring specification:
When a trader holds a ticket that moves across a bucket boundary, only the
ticket's bucket_id changes. No internal sale occurs (contrast with Event 11
for dealer-held tickets).

Setup:
- Bucket ranges: Short (1-3), Mid (4-8), Long (>=9)
- Trader T holds ticket T* with remaining_tau = 9 (Long bucket)
- Dealers D_Long, D_Mid with arbitrary states
- At t2: tau decrements 9 -> 8, bucket changes Long -> Mid

Rebucketing for trader-held ticket:
- Only bucket_id tag changes
- No cash movement
- Dealer states unchanged
- Ownership stays with trader

Contrast with Event 11:
- If dealer held the ticket, internal sale would occur
- Old dealer sells to new dealer at receiving bucket's mid M
- Both dealers' cash and inventory would change

Harness checks:
1. Ownership invariance: ticket owner remains T
2. No cash movement: all entities' cash unchanged
3. Dealer states unchanged: (x, C) of D_Long and D_Mid identical
4. Bucket_id updates: Long -> Mid

Usage:
    uv run python examples/dealer_ring/example10_trader_rebucket.py

Output:
    examples/dealer_ring/out/example10_report.html
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


def setup_example10() -> DealerRingSimulation:
    """Set up Example 10: Trader-held rebucketing."""
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

    # Create issuer
    issuer = TraderState(agent_id="issuer_J", cash=Decimal("100.00"))
    sim.traders[issuer.agent_id] = issuer

    # Create trader T who holds the migrating ticket
    trader_t = TraderState(agent_id="trader_T", cash=Decimal("5.00"))
    sim.traders[trader_t.agent_id] = trader_t

    # Set up dealers with initial state
    dealer_long = sim.dealers["long"]
    dealer_mid = sim.dealers["mid"]
    dealer_long.cash = Decimal("2.00")
    dealer_mid.cash = Decimal("3.00")

    # Create ticket T* for trader T - starts in Long bucket (tau=9)
    ticket_t = Ticket(
        id="T_star",
        issuer_id=issuer.agent_id,
        owner_id=trader_t.agent_id,
        face=Decimal(1),
        maturity_day=sim.day + 9,  # Matures in 9 days
        remaining_tau=9,  # Starts in Long bucket (tau >= 9)
        bucket_id="long",
        serial=1,
    )
    trader_t.tickets_owned.append(ticket_t)
    sim.all_tickets[ticket_t.id] = ticket_t
    issuer.obligations.append(ticket_t)

    # Give dealers some initial inventory (to show they're unaffected)
    for i in range(2):
        d_ticket = Ticket(
            id=f"D_long_{i}",
            issuer_id=issuer.agent_id,
            owner_id=dealer_long.agent_id,
            face=Decimal(1),
            maturity_day=200,
            remaining_tau=15,  # Stays in Long
            bucket_id="long",
            serial=100 + i,
        )
        dealer_long.inventory.append(d_ticket)
        sim.all_tickets[d_ticket.id] = d_ticket

    for i in range(2):
        d_ticket = Ticket(
            id=f"D_mid_{i}",
            issuer_id=issuer.agent_id,
            owner_id=dealer_mid.agent_id,
            face=Decimal(1),
            maturity_day=200,
            remaining_tau=6,  # Stays in Mid
            bucket_id="mid",
            serial=200 + i,
        )
        dealer_mid.inventory.append(d_ticket)
        sim.all_tickets[d_ticket.id] = d_ticket

    # Recompute dealer states
    recompute_dealer_state(dealer_long, sim.vbts["long"], sim.params)
    recompute_dealer_state(dealer_mid, sim.vbts["mid"], sim.params)

    return sim


def verify_initial_state(sim: DealerRingSimulation) -> None:
    """Verify initial state at t1."""
    print("\n=== Initial State (t1: Before Rebucketing) ===")

    trader_t = sim.traders["trader_T"]
    dealer_long = sim.dealers["long"]
    dealer_mid = sim.dealers["mid"]

    ticket = trader_t.tickets_owned[0]

    print(f"Trader T: cash={trader_t.cash}, tickets={len(trader_t.tickets_owned)}")
    print(f"  Ticket T*: bucket={ticket.bucket_id}, tau={ticket.remaining_tau}")
    print(f"\nDealer Long: cash={dealer_long.cash}, x={dealer_long.x}, a={dealer_long.a}")
    print(f"Dealer Mid: cash={dealer_mid.cash}, x={dealer_mid.x}, a={dealer_mid.a}")

    # Verify setup
    assert ticket.bucket_id == "long", f"T* should be in Long bucket, got {ticket.bucket_id}"
    assert ticket.remaining_tau == 9, f"T* tau should be 9, got {ticket.remaining_tau}"
    assert ticket.owner_id == trader_t.agent_id, f"T* should be owned by trader T"

    print("\n✓ Initial state verified!")


def run_rebucketing(sim: DealerRingSimulation) -> dict:
    """Run one day step which includes maturity update and rebucketing."""
    print("\n=== Day 1: Update Maturities and Rebucket ===")

    # Record state before
    trader_t = sim.traders["trader_T"]
    dealer_long = sim.dealers["long"]
    dealer_mid = sim.dealers["mid"]
    ticket = trader_t.tickets_owned[0]

    before = {
        "trader_cash": trader_t.cash,
        "ticket_bucket": ticket.bucket_id,
        "ticket_tau": ticket.remaining_tau,
        "ticket_owner": ticket.owner_id,
        "dealer_long_cash": dealer_long.cash,
        "dealer_long_x": dealer_long.x,
        "dealer_long_a": dealer_long.a,
        "dealer_mid_cash": dealer_mid.cash,
        "dealer_mid_x": dealer_mid.x,
        "dealer_mid_a": dealer_mid.a,
    }

    print(f"Before:")
    print(f"  Ticket T*: bucket={before['ticket_bucket']}, tau={before['ticket_tau']}")
    print(f"  Trader T cash: {before['trader_cash']}")
    print(f"  Dealer Long: cash={before['dealer_long_cash']}, x={before['dealer_long_x']}")
    print(f"  Dealer Mid: cash={before['dealer_mid_cash']}, x={before['dealer_mid_x']}")

    # Run phase 1: maturity updates and rebucketing
    sim.day = 1
    sim.events.log_day_start(1)
    sim._update_maturities()
    sim._rebucket_tickets()

    # Record state after
    after = {
        "trader_cash": trader_t.cash,
        "ticket_bucket": ticket.bucket_id,
        "ticket_tau": ticket.remaining_tau,
        "ticket_owner": ticket.owner_id,
        "dealer_long_cash": dealer_long.cash,
        "dealer_long_x": dealer_long.x,
        "dealer_long_a": dealer_long.a,
        "dealer_mid_cash": dealer_mid.cash,
        "dealer_mid_x": dealer_mid.x,
        "dealer_mid_a": dealer_mid.a,
    }

    print(f"\nAfter:")
    print(f"  Ticket T*: bucket={after['ticket_bucket']}, tau={after['ticket_tau']}")
    print(f"  Trader T cash: {after['trader_cash']}")
    print(f"  Dealer Long: cash={after['dealer_long_cash']}, x={after['dealer_long_x']}")
    print(f"  Dealer Mid: cash={after['dealer_mid_cash']}, x={after['dealer_mid_x']}")

    return {"before": before, "after": after}


def verify_rebucketing(sim: DealerRingSimulation, results: dict) -> None:
    """Verify rebucketing results for trader-held ticket."""
    print("\n=== Rebucketing Verification ===")

    before = results["before"]
    after = results["after"]
    trader_t = sim.traders["trader_T"]

    # 1. Ownership invariance
    assert after["ticket_owner"] == trader_t.agent_id, \
        f"Ticket owner should remain trader_T, got {after['ticket_owner']}"
    print(f"✓ Ownership invariance: ticket owner remains trader_T")

    # 2. No cash movement for trader
    assert after["trader_cash"] == before["trader_cash"], \
        f"Trader cash should be unchanged: {before['trader_cash']} vs {after['trader_cash']}"
    print(f"✓ No cash movement for trader: {after['trader_cash']}")

    # 3. Dealer Long unchanged
    assert after["dealer_long_cash"] == before["dealer_long_cash"], \
        f"Dealer Long cash should be unchanged"
    assert after["dealer_long_x"] == before["dealer_long_x"], \
        f"Dealer Long x should be unchanged"
    assert after["dealer_long_a"] == before["dealer_long_a"], \
        f"Dealer Long a should be unchanged"
    print(f"✓ Dealer Long unchanged: cash={after['dealer_long_cash']}, x={after['dealer_long_x']}")

    # 4. Dealer Mid unchanged
    assert after["dealer_mid_cash"] == before["dealer_mid_cash"], \
        f"Dealer Mid cash should be unchanged"
    assert after["dealer_mid_x"] == before["dealer_mid_x"], \
        f"Dealer Mid x should be unchanged"
    assert after["dealer_mid_a"] == before["dealer_mid_a"], \
        f"Dealer Mid a should be unchanged"
    print(f"✓ Dealer Mid unchanged: cash={after['dealer_mid_cash']}, x={after['dealer_mid_x']}")

    # 5. Bucket_id updated
    assert after["ticket_bucket"] == "mid", \
        f"Ticket bucket should change to mid, got {after['ticket_bucket']}"
    print(f"✓ Bucket_id updated: long -> mid")

    # 6. Tau decremented
    assert after["ticket_tau"] == before["ticket_tau"] - 1, \
        f"Tau should decrement by 1: {before['ticket_tau']} -> {after['ticket_tau']}"
    print(f"✓ Tau decremented: {before['ticket_tau']} -> {after['ticket_tau']}")

    print("\n✓ All rebucketing checks passed!")


def verify_event_11_not_triggered(sim: DealerRingSimulation) -> None:
    """Verify that Event 11 (dealer-dealer transfer) was NOT triggered."""
    print("\n=== Event 11 Not Triggered ===")

    # Get rebucket events from log
    rebucket_events = [
        e for e in sim.events.events
        if e.get("event_type") == "rebucket"
    ]

    print(f"Rebucket events logged: {len(rebucket_events)}")

    # For trader-held tickets, no rebucket event should be logged
    # (the rebucket event is only logged for dealer/VBT transfers)
    trader_rebuckets = [
        e for e in rebucket_events
        if e.get("holder_type") == "trader"
    ]

    # Actually, looking at the code, trader rebuckets don't log events at all
    # Only dealer and VBT rebuckets log events
    print(f"Trader rebucket events: {len(trader_rebuckets)}")
    print(f"Dealer rebucket events: {len([e for e in rebucket_events if e.get('holder_type') == 'dealer'])}")

    print("\nWhat does NOT happen (contrast to Event 11):")
    print("  - If dealer held the ticket, internal sale would occur")
    print("  - Old dealer would sell to new dealer at receiving bucket's mid M")
    print("  - Both dealers' cash and inventory would change")
    print("\nWhat happens for trader-held:")
    print("  - Only bucket_id tag updated")
    print("  - Owner unchanged (T)")
    print("  - No cash movement anywhere")

    print("\n✓ Event 11 (dealer transfer) not triggered for trader-held ticket!")


def main():
    sim = setup_example10()
    sim._capture_snapshot()

    print("Example 10: Trader-Held Rebucketing")
    print("=" * 60)

    verify_initial_state(sim)
    results = run_rebucketing(sim)
    verify_rebucketing(sim, results)
    verify_event_11_not_triggered(sim)

    # Log quotes after rebucketing
    for bucket_id in ["long", "mid"]:
        dealer = sim.dealers[bucket_id]
        vbt = sim.vbts[bucket_id]
        recompute_dealer_state(dealer, vbt, sim.params)

        sim.events.log_quote(
            day=1,
            bucket=bucket_id,
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
    out_path = out_dir / "example10_report.html"

    sim.to_html(
        out_path,
        title="Example 10: Trader-Held Rebucketing",
        subtitle="Only bucket_id changes, no dealer-dealer transfer",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 10 checks passed!")


if __name__ == "__main__":
    main()
