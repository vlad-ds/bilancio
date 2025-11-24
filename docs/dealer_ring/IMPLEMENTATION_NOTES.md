# Dealer Ring Implementation Notes

## What’s in place (feature/dealer-ring-module)
- **Core module scaffolding**: `src/bilancio/modules/dealer_ring/`
  - `kernel.py`: DealerBucket (L1 kernel) with capacity, λ, inside width, midline, clipping, commit-to-quote, pass-through pins to VBT. Tracks dealer_id/vbt_id for ticket ops.
  - `vbt.py`: VBTBucket (infinite depth assumption) with loss-based anchor updates and outside quotes; can buy/sell at bid/ask (inventory can go negative).
  - `ticket_ops.py`: Moves concrete tickets on trades, enforces single-issuer constraint on buys (sets issuer_asset on first buy), supports pass-through and rebucketing relabel for traders.
  - `event_loop.py`: Period skeleton: rebucket by τ ranges; pre-loop dealer/VBT updates; randomized arrivals with bucket selection policies; settlement with proportional recovery; VBT anchor update; dealer mids/spreads synced.
  - `settlement.py`: Settle maturing tickets per bucket with proportional recovery; returns bucket loss rate ℓ.
  - `policy.py`: Eligibility (shortfall→SELL; investable cash/horizon→BUY); bucket selectors (SELL shortest τ / highest bid; BUY Short→Mid→Long skipping pinned asks when possible).
  - `assertions.py`: C1/C2/C4-style helpers (cash/ticket conservation, quote bounds, pass-through invariant) – stubs to be wired.
  - `config.py`, `models.py`, `agents.py`, `tickets.py`: scaffolding types, exports.
- **Core ledger wiring**:
  - New agent kinds `dealer`, `vbt` registered (config/apply + AgentKind + policy issuers/holders/mop_rank).
  - New instrument `Ticket` (issuer, owner, face, maturity_time, bucket_id, serial). Policy allows dealers/VBTs/traders to hold tickets; issuers are agents.
  - `System` helpers: `create_ticket`, `transfer_ticket`, `rebucket_ticket`, `tickets_of`.
- **CLI fix unrelated**: analysis day inference now uses union of due days and settlement days.

## Open docs/resources
- Specs/examples in `docs/dealer_ring/`:
  - `dealer_specification.pdf` (core spec)
  - `dealer_examples.pdf` (worked examples + assertions C1–C6)
  - `dealer_implementation_readiness.pdf` (summary + defaults)
  - Conversations: `docs/dealer_ring/conversations/*.txt`

## What’s missing / next steps
1) **Initialization**
   - Ticketize payables with bucket_id from τ; allocate ~25% dealer / 50% VBT / 25% traders; seed dealer/VBT cash/inventory at mid-shelf (X*target) per spec.
   - Set bucket params (M0/O0, ϕM/ϕO, guard, clip) and build bucket_ranges for rebucketing.
2) **Full period loop polish**
   - Add precompute of dealer quotes at start-of-period (currently implicit via recompute calls).
   - Wire C1–C6 assertions after events (trades, settlement, rebucketing, pass-through).
   - Enrich arrival logging/results with invariants and quote state.
3) **Rebucketing correctness**
   - Done: updates bucket_id on dealer/VBT internal sale; confirm mid-price transfer events/logging; maybe emit explicit events.
4) **Eligibility/bucket policies**
   - DONE: SELL shortest τ/highest bid; BUY Short→Mid→Long skipping pinned asks. Consider skip if dealer ask pinned to outside? Currently handled.
5) **Issuer constraint**
   - DONE via TicketOps on buys. Ensure agent.issuer_asset is initialized/used in trader model.
6) **Settlement/anchors**
   - DONE for proportional recovery + ℓ; VBT anchor update applied; dealer mids/spreads synced. Need to ensure quotes recompute after anchor change.
7) **CLI/config path**
   - Add dealer-ring YAML schema and CLI entry/flag to run this engine (keep legacy RTGS path intact). Include bucket ranges, X*target, order-flow params, guard/clip.
8) **Tests mirroring examples**
   - Capacity jumps, clipping toggle, pass-through invariants, partial-recovery default, order-flow harness (fallback/no-feasible retention), guard M≤M_min, ticket-transfer determinism, rebucketing internal sale, C1–C6.
9) **Logging/events**
   - Add rich events for trades, pass-through, rebucketing, settlement, anchor update to aid tests/HTML.

## Branch
- Working branch: `feature/dealer-ring-module` (pushed).

## Suggested immediate actions
- Implement init pipeline for dealer-ring scenarios (ticketize, allocate, seed dealers/VBTs, bucket params).
- Add CLI entry to run dealer-ring engine with new config model.
- Wire C1–C6 checks in the loop and add unit tests from `dealer_examples.pdf`.
- Add events/logging for internal rebucketing and pass-through for traceability.
