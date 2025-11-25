# Dealer Ring Examples

This folder contains example scripts demonstrating the dealer ring simulation from the specification. The examples correspond to those in `docs/dealer_ring/dealer_examples.pdf`.

## Examples

### Example 1: Selling a Migrating Claim (PDF Section 2)

**File:** `example1_migrating_claim.py`

Demonstrates:
- Trader selling a ticket to the Long dealer at bid price
- Ticket maturity crossing the Long->Mid bucket boundary
- Internal dealer-to-dealer rebucketing at receiving bucket's mid anchor M

```bash
uv run python examples/dealer_ring/example1_migrating_claim.py
```

### Example 2: Maturing Debt and Cross-Bucket Reallocation (PDF Section 3)

**File:** `example2_cross_bucket.py`

Demonstrates:
- Three dealers (Short, Mid, Long) each starting with a=1, C=1
- Short ticket matures and repays in full
- Cross-bucket trades: Short dealer buys from Mid, Mid dealer buys from Long
- Kernel independence: cross-bucket holdings don't affect home-bucket kernel

```bash
uv run python examples/dealer_ring/example2_cross_bucket.py
```

### Example 3: Outside-Bid Clipping Toggle (PDF Section 4)

**File:** `example3_clip_toggle.py`

Demonstrates:
- Default with partial recovery (R=1/3, loss rate=2/3)
- VBT anchor update: M decreases, O increases after losses
- Variant A: No clip (B can be negative)
- Variant B: With clip (B >= 0)

```bash
uv run python examples/dealer_ring/example3_clip_toggle.py
```

### Example 4: Dealer Reaches Inventory Limit and VBT Layoff (PDF Section 5)

**File:** `example4_vbt_layoff.py`

Demonstrates:
- Dealer starts at x=2 on ladder {0,1,2,3,4}
- Two interior BUYs move dealer to x=0
- Third BUY triggers VBT passthrough at outside ask A=1.15
- Dealer state (x, C) unchanged by passthrough

```bash
uv run python examples/dealer_ring/example4_vbt_layoff.py
```

### Example 5: Dealer Earns Over Time (PDF Section 6)

**File:** `example5_dealer_earns.py`

Demonstrates:
- Three trades: SELL, BUY, SELL
- Dealer earns through bid-ask spread
- Equity grows from 4.00 to 4.04
- Invariant checks (E = C + M*a) at each step

```bash
uv run python examples/dealer_ring/example5_dealer_earns.py
```

### Example 6: Bid-Side Pass-Through (PDF Section 7)

**File:** `example6_bid_passthrough.py`

Demonstrates:
- Dealer at capacity boundary (x = X*)
- Customer SELL cannot be absorbed (capacity + cash constraints)
- Trade routed to VBT at outside bid B=0.85
- Dealer state unchanged by passthrough (Event 9)

```bash
uv run python examples/dealer_ring/example6_bid_passthrough.py
```

### Example 7: Edge Rung Without Interior Clipping (PDF Section 8)

**File:** `example7_no_interior_clipping.py`

Demonstrates:
- Interior quotes always strictly inside outside quotes (a(x) < A, b(x) > B)
- Gaps to outside quotes at edge rungs x=1 and x=X*-1
- Boundary pins only at x=0 (BUY->A) and x=X* (SELL->B)

```bash
uv run python examples/dealer_ring/example7_no_interior_clipping.py
```

### Example 8: Guard at Very Low Mid M (PDF Section 9)

**File:** `example8_guard_low_M.py`

Demonstrates:
- Guard regime activation when M <= M_min (0.02)
- X* = 0, all trades route to VBT
- SELL executes at outside bid B, BUY at outside ask A
- Dealer state (x, C) unchanged by both trades

```bash
uv run python examples/dealer_ring/example8_guard_low_M.py
```

### Example 9: Partial-Recovery Default R=0.375 (PDF Section 10)

**File:** `example9_partial_recovery.py`

Demonstrates:
- Single issuer with partial recovery (R = 3/8 = 0.375)
- Holder composition: q_D=3 (dealer), q_V=2 (VBT), q_K=3 (trader)
- Total 8 maturing tickets, issuer cash C=3
- Each receives proportional payout: q * S * R
- Ticket deletion and issuer cash to zero

```bash
uv run python examples/dealer_ring/example9_partial_recovery.py
```

### Example 10: Trader-Held Rebucketing (PDF Section 11)

**File:** `example10_trader_rebucket.py`

Demonstrates:
- Trader holds ticket that crosses bucket boundary (Long->Mid)
- Only bucket_id changes, no cash movement
- Contrast with Event 11 (dealer-held triggers internal sale)
- Dealer states unchanged

```bash
uv run python examples/dealer_ring/example10_trader_rebucket.py
```

### Example 11: Partial-Recovery Default R=0.6 (PDF Section 12)

**File:** `example11_partial_recovery.py`

Demonstrates:
- Single issuer with partial recovery (R = 3/5 = 0.6)
- Holder composition: q_D=2 (dealer), q_VBT=2 (VBT), q_K=1 (trader)
- Total 5 maturing tickets, issuer cash C=3
- Each receives proportional payout: q * S * R
- Bucket loss rate = 1 - R = 0.4

```bash
uv run python examples/dealer_ring/example11_partial_recovery.py
```

### Example 12: Capacity Integer Crossing (PDF Section 13)

**File:** `example12_capacity_crossing.py`

Demonstrates:
- Case A: Up-jump K* : 3 -> 4 after interior BUY
- Case B: Down-jump K* : 4 -> 3 after interior SELL
- Discrete jumps in lambda and inside width I
- Width tightens as capacity increases, widens as it decreases

```bash
uv run python examples/dealer_ring/example12_capacity_crossing.py
```

### Example 13: Minimal Event-Loop Harness (PDF Section 14)

**File:** `example13_event_loop.py`

Demonstrates:
- Eligibility set discipline: once agent executes, removed from set
- Fallback behavior: if preferred side (SELL) empty, process BUY side
- No-feasible retention: if agent can't afford, stays in set
- Three arrivals: SELL executes, BUY fails (poor), BUY executes (rich)

```bash
uv run python examples/dealer_ring/example13_event_loop.py
```

### Example 14: Ticket-Level Transfer (PDF Section 15)

**File:** `example14_ticket_transfer.py`

Demonstrates:
- No generic ticket materialization - specific IDs transferred
- Case A: Interior BUY transfers k2 from dealer (lowest maturity tie-breaker)
- Case B: Passthrough BUY transfers v2 from VBT
- Ownership conservation: ticket IDs preserved under trading

```bash
uv run python examples/dealer_ring/example14_ticket_transfer.py
```

## Output Folder

The `out/` folder contains generated HTML reports. These are gitignored and can be regenerated by running the example scripts.

## Verification

Each example script includes assertions that verify the simulation output matches the specification exactly. Run any example and look for "All Example N checks passed!" at the end.

## Running All Examples

To run all examples and verify they pass:

```bash
for i in {1..14}; do
  uv run python examples/dealer_ring/example${i}_*.py 2>&1 | tail -1
done
```
