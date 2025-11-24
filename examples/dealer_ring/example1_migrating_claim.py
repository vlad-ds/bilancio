"""
Example 1: Selling a Migrating Claim and Dealer Rebucketing.

From the dealer ring specification:
- Trader A1 sells ticket T* to Long dealer at bid ~0.95
- T* migrates Long -> Mid when tau crosses bucket boundary
- Internal dealer sale occurs at receiving bucket's mid M

This script generates an HTML report of the simulation.

Usage:
    uv run python examples/dealer_ring/example1_migrating_claim.py

Output:
    examples/dealer_ring/out/example1_report.html
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


def setup_example1() -> DealerRingSimulation:
    """Set up Example 1 scenario: migrating claim and rebucketing."""
    config = DealerRingConfig(
        dealer_share=Decimal("1.0"),   # All customer flow to dealer
        vbt_share=Decimal("0.0"),      # No VBT flow
        N_max=0,                        # Disable random order flow
        max_days=1,
        seed=42,
    )

    sim = DealerRingSimulation(config)

    # Set VBT anchors to match Example 1
    # Long: M=1.00, O=0.30 -> A=1.15, B=0.85
    # Mid: M=1.00, O=0.20 -> A=1.10, B=0.90
    sim.vbts["long"].M = Decimal("1.00")
    sim.vbts["long"].O = Decimal("0.30")
    sim.vbts["long"].recompute_quotes()

    sim.vbts["mid"].M = Decimal("1.00")
    sim.vbts["mid"].O = Decimal("0.20")
    sim.vbts["mid"].recompute_quotes()

    sim.vbts["short"].M = Decimal("1.00")
    sim.vbts["short"].O = Decimal("0.20")
    sim.vbts["short"].recompute_quotes()

    # Create trader A1 (holds T*)
    trader_a1 = TraderState(
        agent_id="A1_trader",
        cash=Decimal("1.05"),
    )

    # Create issuer A2 (who issued T*)
    issuer_a2 = TraderState(
        agent_id="A2_issuer",
        cash=Decimal("10.00"),
    )

    # Create ticket T* - held by A1, issued by A2
    # tau=9 is Long bucket, will become tau=8 (Mid) after day 1
    ticket_tstar = Ticket(
        id="T_star",
        issuer_id=issuer_a2.agent_id,
        owner_id=trader_a1.agent_id,
        face=Decimal(1),
        maturity_day=100,
        remaining_tau=9,   # Long bucket initially (9 > 8)
        bucket_id="long",
        serial=0,
    )

    # Set up dealers with initial inventory: a=1, C=1 each
    sim.dealers["long"].cash = Decimal("1.00")
    sim.dealers["mid"].cash = Decimal("1.00")

    # Add background ticket to Long dealer
    long_ticket = Ticket(
        id="L0",
        issuer_id="other_issuer",
        owner_id=sim.dealers["long"].agent_id,
        face=Decimal(1),
        maturity_day=200,
        remaining_tau=15,  # Stays in Long
        bucket_id="long",
        serial=1,
    )

    # Add background ticket to Mid dealer
    mid_ticket = Ticket(
        id="M0",
        issuer_id="other_issuer",
        owner_id=sim.dealers["mid"].agent_id,
        face=Decimal(1),
        maturity_day=200,
        remaining_tau=6,   # Stays in Mid
        bucket_id="mid",
        serial=2,
    )

    sim.dealers["long"].inventory.append(long_ticket)
    sim.dealers["mid"].inventory.append(mid_ticket)
    sim.all_tickets["L0"] = long_ticket
    sim.all_tickets["M0"] = mid_ticket

    # Recompute dealer states to get quotes
    for bucket_id in sim.dealers:
        recompute_dealer_state(
            sim.dealers[bucket_id],
            sim.vbts[bucket_id],
            sim.params,
        )

    # Register traders and T* with simulation
    sim.traders[trader_a1.agent_id] = trader_a1
    sim.traders[issuer_a2.agent_id] = issuer_a2
    sim.all_tickets[ticket_tstar.id] = ticket_tstar

    # Link T* to A1's assets (as receivable from A2)
    trader_a1.tickets_owned.append(ticket_tstar)

    # Link T* to A2's obligations
    issuer_a2.obligations.append(ticket_tstar)

    return sim


def run_example1_trade(sim: DealerRingSimulation) -> None:
    """Execute the Example 1 trade: A1 sells T* to Long dealer."""
    trader_a1 = sim.traders["A1_trader"]
    ticket_tstar = sim.all_tickets["T_star"]
    long_dealer = sim.dealers["long"]
    long_vbt = sim.vbts["long"]

    # Get bid price
    bid_price = long_dealer.bid

    # Execute trade: A1 sells T* to Long dealer
    trader_a1.cash += bid_price
    trader_a1.tickets_owned.remove(ticket_tstar)

    long_dealer.cash -= bid_price
    long_dealer.inventory.append(ticket_tstar)
    ticket_tstar.owner_id = long_dealer.agent_id

    # Recompute dealer state
    recompute_dealer_state(long_dealer, long_vbt, sim.params)

    # Log the trade
    sim.events.log_trade(
        day=1,
        side="SELL",
        trader_id=trader_a1.agent_id,
        ticket_id=ticket_tstar.id,
        bucket="long",
        price=bid_price,
        is_passthrough=False,
    )


def main():
    # Set up scenario
    sim = setup_example1()

    # Capture Day 0 snapshot (initial state)
    sim._capture_snapshot()

    print("Example 1: Selling a Migrating Claim")
    print("=" * 50)
    print(f"\nDay 0 State:")
    print(f"  Long dealer: a=1, C={sim.dealers['long'].cash}, bid={sim.dealers['long'].bid}")
    print(f"  Mid dealer:  a=1, C={sim.dealers['mid'].cash}")
    print(f"  A1: cash={sim.traders['A1_trader'].cash}, owns T* (tau=9)")

    # Start Day 1
    sim.day = 1
    sim.events.log_day_start(1)

    # Execute trade
    run_example1_trade(sim)

    print(f"\nAfter trade (Day 1):")
    print(f"  Long dealer: a={sim.dealers['long'].a}, C={sim.dealers['long'].cash}")
    print(f"  A1: cash={sim.traders['A1_trader'].cash}")

    # Run maturity update (decrements tau) then rebucket
    sim._update_maturities()
    sim._rebucket_tickets()

    # Log quote updates
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

    print(f"\nAfter rebucket (Day 1 end):")
    print(f"  Long dealer: a={sim.dealers['long'].a}, C={sim.dealers['long'].cash}")
    print(f"  Mid dealer:  a={sim.dealers['mid'].a}, C={sim.dealers['mid'].cash}")
    print(f"  T* bucket: {sim.all_tickets['T_star'].bucket_id}")

    # Verify equity conservation
    long_equity = sim.dealers['long'].cash + sim.vbts['long'].M * sim.dealers['long'].a
    mid_equity = sim.dealers['mid'].cash + sim.vbts['mid'].M * sim.dealers['mid'].a
    print(f"\nEquity check:")
    print(f"  Long E = C + M*a = {long_equity}")
    print(f"  Mid E = C + M*a = {mid_equity}")

    # Export HTML report
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example1_report.html"

    sim.to_html(
        out_path,
        title="Example 1: Selling a Migrating Claim",
        subtitle="Dealer rebucketing when T* crosses Long->Mid boundary",
    )

    print(f"\nReport saved to: {out_path}")


if __name__ == "__main__":
    main()
