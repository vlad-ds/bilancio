"""Tests for dealer metrics (Section 8 of the functional dealer specification).

Tests verify the metrics tracking infrastructure for:
- Trade log with pre/post state (8.1)
- Dealer P&L and profitability (8.2)
- Trader investment returns and liquidity use (8.3)
- Repayment-priority diagnostics (8.4)
"""

import pytest
from decimal import Decimal

from bilancio.engines.system import System
from bilancio.domain.agents import Household, CentralBank
from bilancio.domain.instruments.credit import Payable
from bilancio.engines.dealer_integration import (
    initialize_dealer_subsystem,
    run_dealer_trading_phase,
)
from bilancio.dealer.simulation import DealerRingConfig
from bilancio.dealer.models import DEFAULT_BUCKETS
from bilancio.dealer.metrics import (
    RunMetrics,
    TradeRecord,
    DealerSnapshot,
    TraderSnapshot,
    TicketOutcome,
    compute_safety_margin,
)


def create_test_system_with_ring():
    """Create a test system with a Kalecki ring of debts.

    Creates 5 households with:
    - 100 cash each
    - Ring of debts: h0->h1->h2->h3->h4->h0 (50 each, due day 5)
    """
    sys = System()

    # Add central bank
    cb = CentralBank(id="CB", name="Central Bank", kind="central_bank")
    sys.add_agent(cb)

    # Create households
    households = []
    for i in range(5):
        h = Household(id=f"h{i}", name=f"Household {i}", kind="household")
        sys.add_agent(h)
        sys.mint_cash(h.id, 100)
        households.append(h)

    # Create ring of debt (each owes 50 to the next)
    for i in range(5):
        creditor_id = households[(i + 1) % 5].id
        debtor_id = households[i].id

        p_id = sys.new_contract_id("P")
        payable = Payable(
            id=p_id,
            kind="payable",
            amount=50,
            denom="USD",
            asset_holder_id=creditor_id,
            liability_issuer_id=debtor_id,
            due_day=5,
        )
        sys.add_contract(payable)

    return sys, households


def create_dealer_config():
    """Create a test dealer configuration."""
    return DealerRingConfig(
        ticket_size=Decimal(1),
        buckets=list(DEFAULT_BUCKETS),
        dealer_share=Decimal("0.25"),
        vbt_share=Decimal("0.50"),
        vbt_anchors={
            "short": (Decimal("1.0"), Decimal("0.20")),
            "mid": (Decimal("1.0"), Decimal("0.30")),
            "long": (Decimal("1.0"), Decimal("0.40")),
        },
        phi_M=Decimal("0.1"),
        phi_O=Decimal("0.1"),
        clip_nonneg_B=True,
        seed=42,
    )


class TestMetricsInitialization:
    """Test metrics are properly initialized."""

    def test_initial_equity_captured(self):
        """Test that initial equity is captured for each bucket."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)

        # Should have initial equity for each bucket
        assert len(subsystem.metrics.initial_equity_by_bucket) == 3
        assert "short" in subsystem.metrics.initial_equity_by_bucket
        assert "mid" in subsystem.metrics.initial_equity_by_bucket
        assert "long" in subsystem.metrics.initial_equity_by_bucket

        # Initial equity should be positive (dealer has cash)
        for bucket_id, equity in subsystem.metrics.initial_equity_by_bucket.items():
            assert equity > 0, f"Initial equity for {bucket_id} should be positive"

    def test_metrics_object_created(self):
        """Test that RunMetrics object is created."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)

        assert subsystem.metrics is not None
        assert isinstance(subsystem.metrics, RunMetrics)
        assert len(subsystem.metrics.trades) == 0  # No trades yet
        assert len(subsystem.metrics.dealer_snapshots) == 0  # No snapshots yet


class TestTradeLogging:
    """Test trade log captures (Section 8.1)."""

    def test_dealer_snapshots_captured_each_day(self):
        """Test dealer snapshots are captured each trading day."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)

        # Run trading for 3 days
        for day in range(1, 4):
            run_dealer_trading_phase(subsystem, sys, current_day=day)

        # Should have 3 snapshots per bucket (3 buckets * 3 days = 9)
        assert len(subsystem.metrics.dealer_snapshots) == 9

        # Each snapshot should have correct structure
        for snapshot in subsystem.metrics.dealer_snapshots:
            assert isinstance(snapshot, DealerSnapshot)
            assert snapshot.day >= 1
            assert snapshot.bucket in ["short", "mid", "long"]
            assert snapshot.inventory >= 0
            assert snapshot.cash >= 0

    def test_trader_snapshots_captured_each_day(self):
        """Test trader snapshots are captured each trading day."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)

        # Run trading for 2 days
        for day in range(1, 3):
            run_dealer_trading_phase(subsystem, sys, current_day=day)

        # Should have snapshots for each trader each day (5 traders * 2 days = 10)
        assert len(subsystem.metrics.trader_snapshots) == 10

        # Each snapshot should have correct structure
        for snapshot in subsystem.metrics.trader_snapshots:
            assert isinstance(snapshot, TraderSnapshot)
            assert snapshot.trader_id.startswith("h")
            assert snapshot.cash >= 0


class TestDealerProfitability:
    """Test dealer profitability metrics (Section 8.2)."""

    def test_pnl_computation(self):
        """Test P&L computation after trading."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)

        # Run several trading days
        for day in range(1, 6):
            run_dealer_trading_phase(subsystem, sys, current_day=day)

        # Get P&L by bucket
        pnl = subsystem.metrics.dealer_pnl_by_bucket()

        assert isinstance(pnl, dict)
        assert "short" in pnl or "mid" in pnl or "long" in pnl

    def test_return_computation(self):
        """Test return computation after trading."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)

        # Run trading
        for day in range(1, 6):
            run_dealer_trading_phase(subsystem, sys, current_day=day)

        # Get returns by bucket
        returns = subsystem.metrics.dealer_return_by_bucket()

        assert isinstance(returns, dict)
        # Returns should be in reasonable range (-1 to +1)
        for bucket_id, ret in returns.items():
            assert ret >= -1 and ret <= 1, f"Return for {bucket_id} should be reasonable"

    def test_summary_includes_profitability(self):
        """Test summary includes profitability metrics."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)
        run_dealer_trading_phase(subsystem, sys, current_day=1)

        summary = subsystem.metrics.summary()

        assert "dealer_total_pnl" in summary
        assert "dealer_total_return" in summary
        assert "dealer_profitable" in summary
        assert "dealer_pnl_by_bucket" in summary


class TestSafetyMargin:
    """Test repayment-priority diagnostics (Section 8.4)."""

    def test_safety_margin_computation(self):
        """Test safety margin computation for a trader."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)

        # Run trading to generate snapshots
        run_dealer_trading_phase(subsystem, sys, current_day=1)

        # Check trader snapshots have safety margins
        for snapshot in subsystem.metrics.trader_snapshots:
            # Safety margin should be computed
            assert snapshot.safety_margin is not None

            # For our setup: cash=100, obligations=50
            # Safety margin = cash + saleable_value - obligations
            # Should be positive initially since cash > obligations
            assert snapshot.safety_margin > Decimal(-200)  # Reasonable lower bound

    def test_summary_includes_safety_metrics(self):
        """Test summary includes safety margin metrics."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)
        run_dealer_trading_phase(subsystem, sys, current_day=1)

        summary = subsystem.metrics.summary()

        assert "unsafe_buy_count" in summary
        assert "fraction_unsafe_buys" in summary


class TestLiquidityMetrics:
    """Test liquidity-driven sales metrics (Section 8.3)."""

    def test_liquidity_driven_flag_tracked(self):
        """Test that liquidity-driven flag is tracked on trades."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)

        # Run multiple days to potentially generate trades
        for day in range(1, 6):
            run_dealer_trading_phase(subsystem, sys, current_day=day)

        # If there are trades, check they have the flag
        for trade in subsystem.metrics.trades:
            assert hasattr(trade, "is_liquidity_driven")

    def test_summary_includes_liquidity_metrics(self):
        """Test summary includes liquidity metrics."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)
        run_dealer_trading_phase(subsystem, sys, current_day=1)

        summary = subsystem.metrics.summary()

        assert "liquidity_driven_sales" in summary
        assert "rescue_events" in summary
        assert "total_trades" in summary


class TestSummaryStatistics:
    """Test experiment-level summary statistics (Section 8.5)."""

    def test_summary_completeness(self):
        """Test that summary includes all required metrics."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)

        # Run a few days
        for day in range(1, 4):
            run_dealer_trading_phase(subsystem, sys, current_day=day)

        summary = subsystem.metrics.summary()

        # Section 8.2: Dealer profitability
        assert "dealer_total_pnl" in summary
        assert "dealer_total_return" in summary
        assert "dealer_profitable" in summary
        assert "dealer_pnl_by_bucket" in summary
        assert "dealer_return_by_bucket" in summary
        assert "spread_income_total" in summary
        assert "interior_trades" in summary
        assert "passthrough_trades" in summary

        # Section 8.3: Trader returns
        assert "mean_trader_return" in summary
        assert "fraction_profitable_traders" in summary
        assert "liquidity_driven_sales" in summary
        assert "rescue_events" in summary

        # Section 8.4: Repayment priority
        assert "unsafe_buy_count" in summary
        assert "fraction_unsafe_buys" in summary
        assert "mean_margin_at_default" in summary

        # Trade counts
        assert "total_trades" in summary
        assert "total_sell_trades" in summary
        assert "total_buy_trades" in summary

    def test_summary_values_valid(self):
        """Test that summary values are valid types."""
        sys, _ = create_test_system_with_ring()
        config = create_dealer_config()

        subsystem = initialize_dealer_subsystem(sys, config, current_day=1)
        run_dealer_trading_phase(subsystem, sys, current_day=1)

        summary = subsystem.metrics.summary()

        # All values should be JSON-serializable
        import json
        try:
            json.dumps(summary)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Summary should be JSON serializable: {e}")


class TestMarkToMidEquity:
    """Test mark-to-mid equity calculation."""

    def test_equity_calculation(self):
        """Test mark-to-mid equity is computed correctly."""
        snapshot = DealerSnapshot(
            day=1,
            bucket="short",
            inventory=10,
            cash=Decimal(100),
            bid=Decimal("0.9"),
            ask=Decimal("1.1"),
            midline=Decimal(1),
            vbt_mid=Decimal(1),
            vbt_spread=Decimal("0.2"),
            ticket_size=Decimal(1),
        )

        # E = C + M * a * S = 100 + 1 * 10 * 1 = 110
        assert snapshot.mark_to_mid_equity == Decimal(110)

    def test_equity_with_zero_inventory(self):
        """Test equity equals cash when no inventory."""
        snapshot = DealerSnapshot(
            day=1,
            bucket="short",
            inventory=0,
            cash=Decimal(100),
            bid=Decimal("0.9"),
            ask=Decimal("1.1"),
            midline=Decimal(1),
            vbt_mid=Decimal(1),
            vbt_spread=Decimal("0.2"),
            ticket_size=Decimal(1),
        )

        # E = C + M * a * S = 100 + 1 * 0 * 1 = 100
        assert snapshot.mark_to_mid_equity == Decimal(100)
