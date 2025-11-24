"""
Dealer module for the Kalecki ring simulation.

This module implements a secondary market dealer system that provides liquidity
to ring agents through market-making. The dealer quotes bid/ask prices and
absorbs customer flow, routing to VBTs (value-based traders) when capacity
is exhausted.

Components:
- models: Data models (Ticket, DealerState, VBTState, TraderState)
- kernel: L1 dealer pricing kernel
- assertions: C1-C6 programmatic invariant checks
- trading: Trade execution logic (TODO)
- events: Event logging system (TODO)
- simulation: Dealer ring event loop (TODO)

References:
- Specification of the Dealer Module for the Kalecki Ring (Bilancio Simulation)
- Examples Document with programmatic assertions
"""

from .models import (
    TicketId,
    BucketConfig,
    DEFAULT_BUCKETS,
    Ticket,
    DealerState,
    VBTState,
    TraderState,
)

from .kernel import (
    M_MIN,
    KernelParams,
    ExecutionResult,
    recompute_dealer_state,
    can_interior_buy,
    can_interior_sell,
)

from .assertions import (
    EPSILON_CASH,
    EPSILON_QTY,
    assert_c1_double_entry,
    assert_c2_quote_bounds,
    assert_c3_feasibility,
    assert_c4_passthrough_invariant,
    assert_c5_equity_basis,
    assert_c6_anchor_timing,
    run_all_assertions,
)

__all__ = [
    # Models
    "TicketId",
    "BucketConfig",
    "DEFAULT_BUCKETS",
    "Ticket",
    "DealerState",
    "VBTState",
    "TraderState",
    # Kernel
    "M_MIN",
    "KernelParams",
    "ExecutionResult",
    "recompute_dealer_state",
    "can_interior_buy",
    "can_interior_sell",
    # Assertions
    "EPSILON_CASH",
    "EPSILON_QTY",
    "assert_c1_double_entry",
    "assert_c2_quote_bounds",
    "assert_c3_feasibility",
    "assert_c4_passthrough_invariant",
    "assert_c5_equity_basis",
    "assert_c6_anchor_timing",
    "run_all_assertions",
]
