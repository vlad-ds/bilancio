"""
Example 3: Outside-Bid Clipping Toggle (A/B).

From the dealer ring specification:
Tests the VBT anchor update after defaults and the optional B >= 0 clip.

Setup:
- At t0: M=1.0, O=0.30, A=1.15, B=0.85
- Dealer holds a=3 tickets (all maturing at t1), C=1
- At t1: 1 ticket repays (full), 2 tickets default (zero recovery)
- Loss rate l = 2/3

Anchor update (phi_M=1.0, phi_O=0.6):
- M_t2 = M_t1 - phi_M * l = 1 - 1*2/3 = 1/3 ≈ 0.3333
- O_t2 = O_t1 + phi_O * l = 0.30 + 0.6*2/3 = 0.70

Raw outside quotes for t2:
- A_t2 = M_t2 + O_t2/2 = 1/3 + 0.35 = 0.6833
- B_t2 = M_t2 - O_t2/2 = 1/3 - 0.35 = -0.0167

Dealer state at t2: a=0, C=2
- X*_t2 = floor(2 / (1/3)) = 6
- λ_t2 = 1/7, I_t2 = λ_t2 * O_t2 = 0.10
- At x=0: p(0) ≈ 0.5958, a(0) ≈ 0.6458, b(0) ≈ 0.5458

Variant A (no clip): B_t2 = -0.0167
Variant B (with clip): B_t2 = max{0, -0.0167} = 0

Note: Interior quotes don't depend on B until a pin is hit.
Both variants have identical interior quotes at x=0.

Usage:
    uv run python examples/dealer_ring/example3_clip_toggle.py

Output:
    examples/dealer_ring/out/example3_report.html
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


def setup_example3(clip_nonneg_B: bool) -> DealerRingSimulation:
    """
    Set up Example 3 scenario: default and VBT anchor update.

    Uses a single issuer with partial recovery (R = 1/3) so loss rate = 2/3.

    Args:
        clip_nonneg_B: Whether to clip B to non-negative
    """
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
        # phi_M=1.0 and phi_O=0.6 are defaults
        phi_M=Decimal("1.0"),
        phi_O=Decimal("0.6"),
        clip_nonneg_B=clip_nonneg_B,
        enable_vbt_anchor_updates=True,
    )

    sim = DealerRingSimulation(config)

    # Create single issuer with cash=1 (partial recovery on 3 tickets)
    # R = cash/due = 1/3, loss_rate = 1 - R = 2/3
    issuer = TraderState(
        agent_id="issuer",
        cash=Decimal("1.00"),  # Only enough to repay 1/3 of obligations
    )
    sim.traders[issuer.agent_id] = issuer

    # Set up dealer with a=3, C=1 (using mid bucket)
    dealer = sim.dealers["mid"]
    dealer.cash = Decimal("1.00")

    # Create 3 tickets from same issuer (all mature at t1 with partial recovery)
    for i in range(3):
        ticket = Ticket(
            id=f"T{i}",
            issuer_id=issuer.agent_id,
            owner_id=dealer.agent_id,
            face=Decimal(1),
            maturity_day=1,  # Matures at t1
            remaining_tau=6,
            bucket_id="mid",
            serial=i,
        )
        dealer.inventory.append(ticket)
        sim.all_tickets[ticket.id] = ticket
        issuer.obligations.append(ticket)

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

    # Recompute dealer state
    recompute_dealer_state(dealer, vbt, sim.params)

    return sim


def verify_initial_state(sim: DealerRingSimulation) -> None:
    """Verify initial state at t0."""
    print("\n=== Initial State (t0) ===")

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    print(f"Dealer: a={dealer.a}, C={dealer.cash}, x={dealer.x}")
    print(f"VBT: M={vbt.M}, O={vbt.O}, A={vbt.A}, B={vbt.B}")
    print(f"  clip_nonneg_B={vbt.clip_nonneg_B}")

    assert dealer.a == 3, f"a should be 3, got {dealer.a}"
    assert dealer.cash == Decimal("1.00"), f"C should be 1, got {dealer.cash}"

    assert vbt.M == Decimal("1.00"), f"M should be 1.00, got {vbt.M}"
    assert vbt.O == Decimal("0.30"), f"O should be 0.30, got {vbt.O}"
    assert vbt.A == Decimal("1.15"), f"A should be 1.15, got {vbt.A}"
    assert vbt.B == Decimal("0.85"), f"B should be 0.85, got {vbt.B}"

    print("✓ Initial state verified!")


def run_settlement_and_update(sim: DealerRingSimulation, clip_nonneg_B: bool) -> None:
    """Run settlement with defaults and VBT anchor update."""
    print("\n=== Day 1: Settlement and Anchor Update ===")

    sim.day = 1
    sim.events.log_day_start(1)

    dealer = sim.dealers["mid"]
    vbt = sim.vbts["mid"]

    # Run settlement (single issuer with partial recovery R=1/3)
    print("\nSettlement:")
    print("  Single issuer: cash=1, due=3, R=1/3, loss_rate=2/3")
    print("  Dealer receives 3 * 1/3 = 1 in recovery")
    sim._settle_maturing_debt()

    # Compute expected loss rate
    # Total face = 3, recovered = 1 (from A) + 0 (from B) = 1
    # Loss = 2/3
    print(f"\nExpected loss rate: 2/3 ≈ {Decimal(2)/Decimal(3):.4f}")

    # Update VBT anchors
    print("\nVBT anchor update (phi_M=1, phi_O=0.6):")
    sim._update_vbt_anchors()

    # Expected values after update:
    # M_new = 1 - 1*2/3 = 1/3
    # O_new = 0.30 + 0.6*2/3 = 0.70
    M_expected = Decimal(1) - Decimal(1) * (Decimal(2) / Decimal(3))
    O_expected = Decimal("0.30") + Decimal("0.6") * (Decimal(2) / Decimal(3))

    print(f"  M_new = 1 - 1*2/3 = {M_expected:.4f}")
    print(f"  O_new = 0.30 + 0.6*2/3 = {O_expected:.4f}")

    # Raw quotes
    A_raw = M_expected + O_expected / 2
    B_raw = M_expected - O_expected / 2

    print(f"\nRaw outside quotes:")
    print(f"  A = M + O/2 = {A_raw:.4f}")
    print(f"  B = M - O/2 = {B_raw:.4f}")

    # Check actual VBT values
    print(f"\nActual VBT state:")
    print(f"  M = {vbt.M:.4f}")
    print(f"  O = {vbt.O:.4f}")
    print(f"  A = {vbt.A:.4f}")
    print(f"  B = {vbt.B:.4f}")

    # Verify M and O
    assert abs(vbt.M - M_expected) < Decimal("0.0001"), f"M off: {vbt.M} vs {M_expected}"
    assert abs(vbt.O - O_expected) < Decimal("0.0001"), f"O off: {vbt.O} vs {O_expected}"

    # Verify A
    assert abs(vbt.A - A_raw) < Decimal("0.0001"), f"A off: {vbt.A} vs {A_raw}"

    # Verify B based on clip setting
    if clip_nonneg_B:
        B_expected = max(Decimal(0), B_raw)
        print(f"\n  With clip: B = max(0, {B_raw:.4f}) = {B_expected}")
    else:
        B_expected = B_raw
        print(f"\n  Without clip: B = {B_expected:.4f} (can be negative)")

    assert abs(vbt.B - B_expected) < Decimal("0.0001"), f"B off: {vbt.B} vs {B_expected}"

    # Verify dealer state after settlement
    print(f"\nDealer after settlement: a={dealer.a}, C={dealer.cash}")
    print(f"  Expected: a=0, C=2 (received 1 from repayment)")

    # Dealer should have a=0 (all tickets settled) and C=2 (original 1 + 1 repayment)
    assert dealer.a == 0, f"a should be 0, got {dealer.a}"
    assert abs(dealer.cash - Decimal("2.00")) < Decimal("0.0001"), f"C should be 2, got {dealer.cash}"

    # Recompute dealer state with new anchors
    recompute_dealer_state(dealer, vbt, sim.params)

    # Verify dealer kernel at t2
    # X* = floor(2 / (1/3)) = floor(6) = 6
    # λ = 1/(6+1) = 1/7
    # I = λ*O = 1/7 * 0.70 = 0.10
    print(f"\nDealer kernel at t2:")
    print(f"  X* = {dealer.X_star} (expected: 6)")
    print(f"  λ = {dealer.lambda_:.4f} (expected: 0.1429)")
    print(f"  I = {dealer.I:.4f} (expected: 0.10)")

    # At x=0:
    # p(0) = M - O/(X*+2S) * (0 - X*/2) = 1/3 - 0.70/8 * (-3) = 1/3 + 0.2625 ≈ 0.5958
    # a(0) = p(0) + I/2 ≈ 0.6458
    # b(0) = p(0) - I/2 ≈ 0.5458
    print(f"  At x=0: ask={dealer.ask:.4f}, bid={dealer.bid:.4f}")
    print(f"  Expected: ask≈0.6458, bid≈0.5458")

    # Log quotes
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

    print("\n✓ Settlement and anchor update verified!")


def main():
    print("Example 3: Outside-Bid Clipping Toggle")
    print("=" * 60)

    # Run Variant A (no clip)
    print("\n" + "=" * 60)
    print("VARIANT A: No outside-bid clip (B can be negative)")
    print("=" * 60)

    sim_a = setup_example3(clip_nonneg_B=False)
    sim_a._capture_snapshot()
    verify_initial_state(sim_a)
    run_settlement_and_update(sim_a, clip_nonneg_B=False)
    sim_a._capture_snapshot()

    vbt_a = sim_a.vbts["mid"]
    print(f"\nVariant A result: B = {vbt_a.B:.4f} (negative allowed)")

    # Run Variant B (with clip)
    print("\n" + "=" * 60)
    print("VARIANT B: With outside-bid clip (B >= 0)")
    print("=" * 60)

    sim_b = setup_example3(clip_nonneg_B=True)
    sim_b._capture_snapshot()
    verify_initial_state(sim_b)
    run_settlement_and_update(sim_b, clip_nonneg_B=True)
    sim_b._capture_snapshot()

    vbt_b = sim_b.vbts["mid"]
    print(f"\nVariant B result: B = {vbt_b.B:.4f} (clipped to 0)")

    # Summary
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"\nBoth variants have identical M={vbt_a.M:.4f}, O={vbt_a.O:.4f}, A={vbt_a.A:.4f}")
    print(f"\nDifference in B:")
    print(f"  Variant A (no clip):   B = {vbt_a.B:.4f}")
    print(f"  Variant B (with clip): B = {vbt_b.B:.4f}")

    dealer_a = sim_a.dealers["mid"]
    dealer_b = sim_b.dealers["mid"]
    print(f"\nInterior quotes are identical at x=0:")
    print(f"  Variant A: ask={dealer_a.ask:.4f}, bid={dealer_a.bid:.4f}")
    print(f"  Variant B: ask={dealer_b.ask:.4f}, bid={dealer_b.bid:.4f}")

    # Export HTML report (using Variant B for cleaner display)
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "example3_report.html"

    sim_b.to_html(
        out_path,
        title="Example 3: VBT Anchor Update with Clipping",
        subtitle="Default triggers anchor update, B clipped to 0",
    )

    print(f"\nReport saved to: {out_path}")
    print("\n✓ All Example 3 checks passed!")


if __name__ == "__main__":
    main()
