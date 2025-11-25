"""
Example 2: Maturing Debt and Cross-Bucket Reallocation.

From the dealer ring specification:
- Three dealers (Short, Mid, Long) each start with a=1, C=1
- Short ticket S* matures and repays in full at t1 end
- At t2: D_S buys from D_M at Mid's ask, D_M buys from D_L at Long's ask
- Tests kernel independence: cross-bucket holdings don't affect home kernel

Key formulas for verification:
- VBT anchors: M=1 for all, O_S=0.20, O_M=0.30, O_L=0.40
- Initial: V=2, K*=2, X*=2, λ=1/3 for all dealers at x=1
- Short: I=λO=1/3*0.20≈0.0666, p(1)=1, a(1)≈1.0333, b(1)≈0.9667
- Mid: I=1/3*0.30=0.10, p(1)=1, a(1)=1.05, b(1)=0.95
- Long: I=1/3*0.40≈0.1333, p(1)=1, a(1)≈1.0667, b(1)≈0.9333

After t1 settlement (Short ticket repays):
- D_S: a 1→0, C 1→2, V=2 unchanged
- At x=0: p(0)=1+0.20/4*1=1.05, a(0)≈1.0833, b(0)≈1.0167

t2 trades:
1. D_S buys Mid ticket at a_M(1)=1.05
   - D_M: a 1→0, C 1→2.05
   - At x=0: p(0)=1.075, a(0)=1.125, b(0)=1.025
   - D_S: C 2→0.95
2. D_M buys Long ticket at a_L(1)≈1.0667
   - D_L: a 1→0, C 1→2.0667
   - At x=0: p(0)=1.10, a(0)≈1.1667, b(0)≈1.0333
   - D_M: C 2.05→0.9833

Usage:
    uv run python examples/dealer_ring/example2_cross_bucket.py

Output:
    examples/dealer_ring/out/example2_report.html
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


def setup_example2() -> DealerRingSimulation:
    """Set up Example 2 scenario: maturing debt and cross-bucket reallocation."""
    config = DealerRingConfig(
        dealer_share=Decimal("1.0"),   # All flow to dealer
        vbt_share=Decimal("0.0"),      # No VBT flow
        N_max=0,                        # Disable random order flow
        max_days=2,
        seed=42,
        # VBT anchors per Example 2: M=1 for all, different O values
        vbt_anchors={
            "short": (Decimal("1.00"), Decimal("0.20")),
            "mid": (Decimal("1.00"), Decimal("0.30")),
            "long": (Decimal("1.00"), Decimal("0.40")),
        },
    )

    sim = DealerRingSimulation(config)

    # Create issuer for background tickets (dummy issuer with lots of cash)
    issuer_other = TraderState(
        agent_id="issuer_other",
        cash=Decimal("100.00"),  # Enough to settle all tickets
    )

    # Create issuer for the Short ticket that will mature at t1
    issuer_short = TraderState(
        agent_id="issuer_short",
        cash=Decimal("1.00"),  # Enough to fully repay 1 ticket at face=1
    )

    sim.traders[issuer_other.agent_id] = issuer_other
    sim.traders[issuer_short.agent_id] = issuer_short

    # Set up dealers with initial inventory: a=1, C=1 each
    # Short dealer ticket - matures at day 1 (end of t1)
    short_ticket = Ticket(
        id="S_star",
        issuer_id=issuer_short.agent_id,
        owner_id=sim.dealers["short"].agent_id,
        face=Decimal(1),
        maturity_day=1,      # Matures at t1
        remaining_tau=1,      # Short bucket
        bucket_id="short",
        serial=0,
    )

    # Mid dealer ticket - doesn't mature yet
    mid_ticket = Ticket(
        id="M0",
        issuer_id=issuer_other.agent_id,
        owner_id=sim.dealers["mid"].agent_id,
        face=Decimal(1),
        maturity_day=200,
        remaining_tau=6,      # Mid bucket
        bucket_id="mid",
        serial=1,
    )

    # Long dealer ticket - doesn't mature yet
    long_ticket = Ticket(
        id="L0",
        issuer_id=issuer_other.agent_id,
        owner_id=sim.dealers["long"].agent_id,
        face=Decimal(1),
        maturity_day=200,
        remaining_tau=15,     # Long bucket
        bucket_id="long",
        serial=2,
    )

    # Register tickets
    sim.all_tickets["S_star"] = short_ticket
    sim.all_tickets["M0"] = mid_ticket
    sim.all_tickets["L0"] = long_ticket

    # Link tickets to issuers' obligations
    issuer_short.obligations.append(short_ticket)
    issuer_other.obligations.append(mid_ticket)
    issuer_other.obligations.append(long_ticket)

    # Initialize dealers with a=1, C=1 each
    for bucket_id in ["short", "mid", "long"]:
        sim.dealers[bucket_id].cash = Decimal("1.00")

    sim.dealers["short"].inventory.append(short_ticket)
    sim.dealers["mid"].inventory.append(mid_ticket)
    sim.dealers["long"].inventory.append(long_ticket)

    # Recompute dealer states to get initial quotes
    for bucket_id in sim.dealers:
        recompute_dealer_state(
            sim.dealers[bucket_id],
            sim.vbts[bucket_id],
            sim.params,
        )

    return sim


def verify_initial_quotes(sim: DealerRingSimulation) -> None:
    """Verify t1 initial quotes match specification."""
    print("\n=== Initial State (t0/t1 start) ===")

    # Short dealer: a=1, C=1, λ=1/3, I=0.0666, at x=1: a(1)≈1.0333, b(1)≈0.9667
    ds = sim.dealers["short"]
    print(f"Short dealer: a={ds.a}, C={ds.cash}, λ={ds.lambda_:.4f}, I={ds.I:.4f}")
    print(f"  Quotes at x={ds.x}: ask={ds.ask:.4f}, bid={ds.bid:.4f}")
    print(f"  Expected: a≈1.0333, b≈0.9667")
    assert ds.a == 1, f"Short a should be 1, got {ds.a}"
    assert abs(ds.ask - Decimal("1.0333")) < Decimal("0.001"), f"Short ask off: {ds.ask}"
    assert abs(ds.bid - Decimal("0.9667")) < Decimal("0.001"), f"Short bid off: {ds.bid}"

    # Mid dealer: a=1, C=1, λ=1/3, I=0.10, at x=1: a(1)=1.05, b(1)=0.95
    dm = sim.dealers["mid"]
    print(f"Mid dealer: a={dm.a}, C={dm.cash}, λ={dm.lambda_:.4f}, I={dm.I:.4f}")
    print(f"  Quotes at x={dm.x}: ask={dm.ask:.4f}, bid={dm.bid:.4f}")
    print(f"  Expected: a=1.05, b=0.95")
    assert dm.a == 1, f"Mid a should be 1, got {dm.a}"
    assert abs(dm.ask - Decimal("1.05")) < Decimal("0.001"), f"Mid ask off: {dm.ask}"
    assert abs(dm.bid - Decimal("0.95")) < Decimal("0.001"), f"Mid bid off: {dm.bid}"

    # Long dealer: a=1, C=1, λ=1/3, I=0.1333, at x=1: a(1)≈1.0667, b(1)≈0.9333
    dl = sim.dealers["long"]
    print(f"Long dealer: a={dl.a}, C={dl.cash}, λ={dl.lambda_:.4f}, I={dl.I:.4f}")
    print(f"  Quotes at x={dl.x}: ask={dl.ask:.4f}, bid={dl.bid:.4f}")
    print(f"  Expected: a≈1.0667, b≈0.9333")
    assert dl.a == 1, f"Long a should be 1, got {dl.a}"
    assert abs(dl.ask - Decimal("1.0667")) < Decimal("0.001"), f"Long ask off: {dl.ask}"
    assert abs(dl.bid - Decimal("0.9333")) < Decimal("0.001"), f"Long bid off: {dl.bid}"

    print("✓ All initial quotes verified!")


def run_t1_settlement(sim: DealerRingSimulation) -> None:
    """Run t1: Short ticket S* matures and repays in full."""
    print("\n=== End of t1: Settlement ===")

    # Start day 1
    sim.day = 1
    sim.events.log_day_start(1)

    # Execute settlement (short ticket matures)
    sim._settle_maturing_debt()

    # Recompute dealer states after settlement
    for bucket_id in sim.dealers:
        recompute_dealer_state(
            sim.dealers[bucket_id],
            sim.vbts[bucket_id],
            sim.params,
        )

    # Log quotes after settlement
    for bucket_id, dealer in sim.dealers.items():
        vbt = sim.vbts[bucket_id]
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

    # Capture Day 1 snapshot
    sim._capture_snapshot()

    # Verify Short dealer state after settlement
    ds = sim.dealers["short"]
    print(f"Short dealer after settlement: a={ds.a}, C={ds.cash}")
    print(f"  Quotes at x={ds.x}: ask={ds.ask:.4f}, bid={ds.bid:.4f}")
    print(f"  Expected: a=0, C=2, x=0, a(0)≈1.0833, b(0)≈1.0167")
    assert ds.a == 0, f"Short a should be 0 after settlement, got {ds.a}"
    assert ds.cash == Decimal("2.00"), f"Short C should be 2.00, got {ds.cash}"
    assert abs(ds.ask - Decimal("1.0833")) < Decimal("0.001"), f"Short ask off: {ds.ask}"
    assert abs(ds.bid - Decimal("1.0167")) < Decimal("0.001"), f"Short bid off: {ds.bid}"

    print("✓ Settlement verified!")


def run_t2_cross_bucket_trades(sim: DealerRingSimulation) -> None:
    """
    Run t2: Cross-bucket trades where dealers buy from other dealers.

    Trade 1: D_S (Short dealer) buys from D_M (Mid dealer) at Mid's ask
    Trade 2: D_M (Mid dealer) buys from D_L (Long dealer) at Long's ask

    Per the spec: these are dealer-as-customer trades. The buying dealer
    acts as a customer in the selling bucket.
    """
    print("\n=== Start of t2: Cross-bucket trades ===")

    # Start day 2
    sim.day = 2
    sim.events.log_day_start(2)

    ds = sim.dealers["short"]
    dm = sim.dealers["mid"]
    dl = sim.dealers["long"]
    vbt_mid = sim.vbts["mid"]
    vbt_long = sim.vbts["long"]

    # --- Trade 1: D_S buys from D_M at Mid's ask a_M(1) = 1.05 ---
    print("\nTrade 1: Short dealer buys Mid ticket at ask 1.05")

    # Get the ask price before trade
    mid_ask_before = dm.ask
    print(f"  Mid ask before: {mid_ask_before}")
    assert abs(mid_ask_before - Decimal("1.05")) < Decimal("0.001")

    # Execute: D_M sells to D_S
    # This is an interior dealer SELL at the ask
    result = sim.executor.execute_customer_buy(
        dealer=dm,
        vbt=vbt_mid,
        buyer_id=ds.agent_id,  # Short dealer is the buyer
    )

    # Update Short dealer cash (buyer pays)
    ds.cash -= result.price

    # The ticket now belongs to Short dealer (as off-bucket holding)
    # Per kernel independence: D_S's home-bucket kernel uses only (a_S, C_S)
    # The acquired Mid ticket doesn't affect Short's kernel, only cash changes

    # But the ticket should be tracked somewhere - add to a cross-bucket holdings list
    # For now, just track that Short dealer paid and Mid dealer received

    # Log the cross-bucket trade
    sim.events.log_trade(
        day=2,
        side="BUY",
        trader_id=ds.agent_id,
        ticket_id=result.ticket.id,
        bucket="mid",
        price=result.price,
        is_passthrough=result.is_passthrough,
    )

    print(f"  Executed at price: {result.price}")
    print(f"  Mid dealer after: a={dm.a}, C={dm.cash}")
    print(f"  Short dealer cash after: {ds.cash}")

    # Verify Mid dealer state after Trade 1
    print(f"  Expected Mid: a=0, C=2.05")
    assert dm.a == 0, f"Mid a should be 0, got {dm.a}"
    assert abs(dm.cash - Decimal("2.05")) < Decimal("0.001"), f"Mid C should be 2.05, got {dm.cash}"

    # Verify Short dealer cash
    print(f"  Expected Short C: 0.95")
    assert abs(ds.cash - Decimal("0.95")) < Decimal("0.001"), f"Short C should be 0.95, got {ds.cash}"

    # Verify Mid quotes at x=0
    print(f"  Mid quotes at x=0: ask={dm.ask:.4f}, bid={dm.bid:.4f}")
    print(f"  Expected: a(0)=1.125, b(0)=1.025")
    assert abs(dm.ask - Decimal("1.125")) < Decimal("0.001"), f"Mid ask off: {dm.ask}"
    assert abs(dm.bid - Decimal("1.025")) < Decimal("0.001"), f"Mid bid off: {dm.bid}"

    print("✓ Trade 1 verified!")

    # --- Trade 2: D_M buys from D_L at Long's ask a_L(1) ≈ 1.0667 ---
    print("\nTrade 2: Mid dealer buys Long ticket at ask ~1.0667")

    # Get the ask price before trade
    long_ask_before = dl.ask
    print(f"  Long ask before: {long_ask_before}")
    assert abs(long_ask_before - Decimal("1.0667")) < Decimal("0.001")

    # Execute: D_L sells to D_M
    result2 = sim.executor.execute_customer_buy(
        dealer=dl,
        vbt=vbt_long,
        buyer_id=dm.agent_id,  # Mid dealer is the buyer
    )

    # Update Mid dealer cash (buyer pays)
    dm.cash -= result2.price

    # Log the cross-bucket trade
    sim.events.log_trade(
        day=2,
        side="BUY",
        trader_id=dm.agent_id,
        ticket_id=result2.ticket.id,
        bucket="long",
        price=result2.price,
        is_passthrough=result2.is_passthrough,
    )

    print(f"  Executed at price: {result2.price}")
    print(f"  Long dealer after: a={dl.a}, C={dl.cash}")
    print(f"  Mid dealer cash after: {dm.cash}")

    # Verify Long dealer state after Trade 2
    print(f"  Expected Long: a=0, C≈2.0667")
    assert dl.a == 0, f"Long a should be 0, got {dl.a}"
    assert abs(dl.cash - Decimal("2.0667")) < Decimal("0.001"), f"Long C should be ~2.0667, got {dl.cash}"

    # Verify Mid dealer cash
    print(f"  Expected Mid C: 0.9833")
    assert abs(dm.cash - Decimal("0.9833")) < Decimal("0.001"), f"Mid C should be ~0.9833, got {dm.cash}"

    # Verify Long quotes at x=0
    print(f"  Long quotes at x=0: ask={dl.ask:.4f}, bid={dl.bid:.4f}")
    print(f"  Expected: a(0)≈1.1667, b(0)≈1.0333")
    assert abs(dl.ask - Decimal("1.1667")) < Decimal("0.001"), f"Long ask off: {dl.ask}"
    assert abs(dl.bid - Decimal("1.0333")) < Decimal("0.001"), f"Long bid off: {dl.bid}"

    print("✓ Trade 2 verified!")

    # Log quote updates for day 2
    for bucket_id, dealer in sim.dealers.items():
        vbt = sim.vbts[bucket_id]
        sim.events.log_quote(
            day=2,
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

    # Capture Day 2 snapshot
    sim._capture_snapshot()


def main():
    # Set up scenario
    sim = setup_example2()

    # Capture Day 0 snapshot (initial state)
    sim._capture_snapshot()

    print("Example 2: Maturing Debt and Cross-Bucket Reallocation")
    print("=" * 60)

    # Verify initial quotes
    verify_initial_quotes(sim)

    # Run t1 settlement
    run_t1_settlement(sim)

    # Run t2 cross-bucket trades
    run_t2_cross_bucket_trades(sim)

    # Final summary
    print("\n=== Final Summary ===")
    print(f"Short dealer: a={sim.dealers['short'].a}, C={sim.dealers['short'].cash}")
    print(f"Mid dealer:   a={sim.dealers['mid'].a}, C={sim.dealers['mid'].cash}")
    print(f"Long dealer:  a={sim.dealers['long'].a}, C={sim.dealers['long'].cash}")

    # Export HTML report
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example2_report.html"

    sim.to_html(
        out_path,
        title="Example 2: Cross-Bucket Reallocation",
        subtitle="Maturing debt and dealer-as-customer trades",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 2 checks passed!")


if __name__ == "__main__":
    main()
