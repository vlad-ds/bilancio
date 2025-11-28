# Plan 016: Integrate Dealer Module with Kalecki Ring Simulation

**Status**: IN_PROGRESS
**Date**: 2025-11-25
**Goal**: Unify the standalone dealer ring implementation with the main Bilancio simulation engine to enable full Kalecki simulations with dealer-mediated secondary markets.

---

## Executive Summary

The dealer module (`src/bilancio/dealer/`) is a complete, verified implementation of the dealer specification (3,661 lines, 14 worked examples, all assertions passing). However, it operates as a **standalone** system separate from the main Bilancio simulation engine that runs YAML-based Kalecki ring scenarios.

This plan outlines the steps to integrate these two systems, enabling scenarios like:
- "Run a 100-agent Kalecki ring with a secondary debt market"
- "Compare default rates with and without dealer intermediation"
- "Sweep parameters (κ, ι, μ) with dealer-enabled simulations"

---

## Current State Analysis

### What Exists: Dealer Module (`src/bilancio/dealer/`)

| File | Lines | Purpose |
|------|-------|---------|
| `models.py` | 318 | Ticket, DealerState, VBTState, TraderState, BucketConfig |
| `kernel.py` | 234 | L1 dealer formulas: V, K*, X*, λ, I, p(x), quotes, Guard |
| `trading.py` | 398 | TradeExecutor for customer buy/sell + passthrough |
| `simulation.py` | 1225 | Full event loop per Section 11 |
| `events.py` | 414 | Event logging and serialization |
| `assertions.py` | 332 | C1-C6 programmatic checks |
| `report.py` | 635 | HTML report generation |

**Verification**: 14 worked examples in `examples/dealer_ring/` pass, all matching PDF specification.

### What Exists: Main Simulation Engine

| Module | Purpose |
|--------|---------|
| `engines/simulation.py` | Phase A/B/C day runner for YAML scenarios |
| `engines/settlement.py` | Payable settlement with default handling |
| `scenarios/generators/ring_explorer.py` | κ-ι-μ parameterized ring generator |
| `experiments/ring.py` | Grid/LHS sweep infrastructure |
| `domain/agents/` | Bank, Household, Firm, CentralBank, Treasury |
| `domain/instruments/credit.py` | Payable contracts |

### The Gap: Two Separate Worlds

| Aspect | Dealer Module | Main Bilancio |
|--------|---------------|---------------|
| Agent Model | `TraderState`, `DealerState`, `VBTState` | `Agent` with subtypes |
| Debt Instrument | `Ticket` (face, maturity, bucket) | `Payable` (contract-based) |
| Simulation Loop | `DealerRingSimulation.run_day()` | `engines.simulation.run_day()` |
| Configuration | Python `DealerRingConfig` | YAML scenarios |
| Event Loop | 6 phases (maturity, quotation, eligibility, trading, settlement, VBT update) | 3 phases (A: marker, B: settlement, C: clearing) |

---

## Integration Architecture

### Option A: Adapter Pattern (Recommended)

Create an adapter layer that allows the main engine to optionally invoke dealer mechanics without rewriting either system.

```
┌─────────────────────────────────────────────────────────┐
│                    YAML Scenario                         │
│  (agents, payables, dealer_config?, scheduled_actions)   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              System + State                              │
│  - agents: Dict[AgentId, Agent]                         │
│  - contracts: Dict[ContractId, Contract]                │
│  - dealer_subsystem?: DealerSubsystem (optional)        │
└────────────────────────┬────────────────────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌────────┐        ┌────────────┐       ┌─────────────┐
│Phase A │        │  Phase B    │       │  Phase C    │
│(marker)│        │ B1: actions │       │ (clearing)  │
└────────┘        │ B2: settle  │       └─────────────┘
                  │ B3: dealer? │
                  └─────────────┘
```

**New Phase B3**: If dealer subsystem is enabled, execute dealer trading loop between B1 (scheduled actions) and B2 (settlement).

### Option B: Full Rewrite

Rewrite the main engine to natively understand tickets, dealers, and VBTs. More invasive, higher risk.

**Recommendation**: Option A - lower risk, preserves both systems' integrity, easier to verify.

---

## Implementation Steps

### Phase 1: Contract-to-Ticket Bridge (Week 1)

**Goal**: Enable conversion between Bilancio's `Payable` contracts and dealer module's `Ticket` objects.

#### 1.1 Create `dealer/bridge.py`

```python
# New file: src/bilancio/dealer/bridge.py

def payables_to_tickets(
    system: System,
    ticket_size: Decimal = Decimal(1),
) -> Dict[TicketId, Ticket]:
    """
    Convert outstanding Payable contracts to tradeable Tickets.

    - Each payable is "ticketized" into face/S tickets
    - Assigns bucket based on remaining days to maturity
    - Returns ticket registry for dealer subsystem
    """

def apply_ticket_trades_to_system(
    system: System,
    trades: List[TradeResult],
) -> None:
    """
    Apply dealer trade results back to main system.

    - Update agent cash balances
    - Update contract ownership (new: track holder != original creditor)
    """
```

#### 1.2 Extend Payable Model

Add optional `holder_id` field to track secondary market transfers:

```python
# In domain/instruments/credit.py

@dataclass
class Payable(Contract):
    # ... existing fields ...
    holder_id: Optional[AgentId] = None  # Current holder (if transferred)

    @property
    def effective_creditor(self) -> AgentId:
        return self.holder_id or self.creditor_id
```

### Phase 2: Dealer Subsystem Integration (Week 2)

**Goal**: Enable optional dealer subsystem in main simulation.

#### 2.1 Create `DealerSubsystem` Wrapper

```python
# New file: src/bilancio/engines/dealer_integration.py

@dataclass
class DealerSubsystem:
    """Wrapper that adapts dealer module for main engine."""

    dealers: Dict[str, DealerState]  # bucket -> dealer
    vbts: Dict[str, VBTState]
    params: KernelParams
    executor: TradeExecutor
    config: DealerRingConfig

    @classmethod
    def from_system(cls, system: System, config: dict) -> "DealerSubsystem":
        """Initialize dealer subsystem from system state."""

    def run_trading_phase(
        self,
        system: System,
        current_day: int,
    ) -> List[dict]:
        """
        Execute one dealer trading phase.

        1. Update ticket maturities/buckets
        2. Recompute dealer quotes
        3. Build eligibility sets from agent shortfalls
        4. Run randomized order flow
        5. Return trade events
        """
```

#### 2.2 Modify `run_day()` to Support Dealers

```python
# In engines/simulation.py

def run_day(system, enable_dealer: bool = False):
    current_day = system.state.day

    # Phase A: Log marker
    system.log("PhaseA")

    # Phase B: Actions + Dealer Trading + Settlement
    system.log("PhaseB")

    # B1: Scheduled actions
    system.log("SubphaseB1")
    _execute_scheduled_actions(system, current_day)

    # B2 (NEW): Dealer trading phase
    if enable_dealer and hasattr(system.state, 'dealer_subsystem'):
        system.log("SubphaseB2_Dealer")
        events = system.state.dealer_subsystem.run_trading_phase(system, current_day)
        for event in events:
            system.state.events.append(event)

    # B3: Settlement (was B2)
    system.log("SubphaseB3")
    settle_due(system, current_day)

    # Phase C: Clearing
    system.log("PhaseC")
    settle_intraday_nets(system, current_day)

    system.state.day += 1
```

### Phase 3: YAML Configuration Extension (Week 2-3)

**Goal**: Allow YAML scenarios to specify dealer configuration.

#### 3.1 Extend Scenario Schema

```yaml
# Example: scenarios/kalecki_with_dealer.yaml
version: 1
name: "Kalecki Ring with Dealer"

# Dealer configuration (optional)
dealer:
  enabled: true
  ticket_size: 1
  buckets:
    short: { tau_min: 1, tau_max: 3, M: 1.0, O: 0.20 }
    mid: { tau_min: 4, tau_max: 8, M: 1.0, O: 0.30 }
    long: { tau_min: 9, tau_max: 999, M: 1.0, O: 0.40 }
  dealer_share: 0.25
  vbt_share: 0.50
  order_flow:
    pi_sell: 0.5
    N_max: 3
  trader_policy:
    horizon_H: 3
    buffer_B: 1.0

# Agents (100+ for meaningful market)
agents:
  - id: H1
    kind: household
  # ... generated by ring_explorer
```

#### 3.2 Update Config Loader

```python
# In config/loaders.py

def _load_dealer_config(dealer_dict: dict) -> Optional[DealerRingConfig]:
    if not dealer_dict.get("enabled", False):
        return None
    return DealerRingConfig(
        ticket_size=Decimal(str(dealer_dict.get("ticket_size", 1))),
        # ... map all fields
    )
```

### Phase 4: Experiment Infrastructure Update (Week 3)

**Goal**: Enable parameter sweeps with dealer-enabled simulations.

#### 4.1 Extend Ring Sweep Config

```python
# In experiments/ring.py

class _RingSweepConfig(BaseModel):
    # ... existing fields ...
    dealer_enabled: bool = False
    dealer_config: Optional[Dict] = None
```

#### 4.2 Add Comparative Metrics

New metrics to compare dealer vs no-dealer runs:
- `default_rate_with_dealer`
- `default_rate_without_dealer`
- `dealer_profit`
- `vbt_absorption_rate`
- `liquidity_relief_ratio`

### Phase 5: Testing and Validation (Week 4)

#### 5.1 Integration Tests

```python
# tests/integration/test_dealer_integration.py

def test_kalecki_ring_with_dealer():
    """100-agent ring with dealer should have lower defaults."""

def test_dealer_passthrough_to_vbt():
    """When dealer at capacity, trades route to VBT."""

def test_settlement_with_transferred_payables():
    """Payables transferred via dealer settle to current holder."""
```

#### 5.2 Regression Tests

Ensure existing examples still pass:
- All 14 dealer ring examples
- All existing YAML scenario tests
- Ring sweep experiments

---

## Data Model Mapping

### Agent Mapping

| Main Bilancio | Dealer Module | Integration |
|--------------|---------------|-------------|
| `Household` | `TraderState` | Households become traders in dealer subsystem |
| N/A | `DealerState` | New agent type or special entity |
| N/A | `VBTState` | New agent type or special entity |
| `Bank` | N/A | Banks unchanged (dealers don't interact) |

### Instrument Mapping

| Main Bilancio | Dealer Module | Integration |
|--------------|---------------|-------------|
| `Payable` | `Ticket` | Bridge converts payables → tickets for trading |
| `Payable.holder_id` | `Ticket.owner_id` | Track secondary market transfers |

---

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| Breaking existing tests | Run full test suite after each integration step |
| Dealer module assumptions | Document where specs differ, add compatibility checks |
| Performance with 100+ agents | Profile early, optimize eligibility set computation |
| Settlement with transferred payables | Add explicit test cases for holder != original creditor |

---

## Success Criteria

1. **Functional**: Can run `bilancio run scenarios/kalecki_with_dealer.yaml` and see dealer trades in output
2. **Comparative**: Can run same scenario with/without dealer and compare default rates
3. **Sweep**: Can run `bilancio sweep ring --dealer-enabled` for parameter exploration
4. **Verified**: All 14 dealer examples still pass
5. **Tested**: New integration tests pass

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Bridge | 3-4 days | None |
| Phase 2: Integration | 4-5 days | Phase 1 |
| Phase 3: YAML Config | 2-3 days | Phase 2 |
| Phase 4: Experiments | 2-3 days | Phase 3 |
| Phase 5: Testing | 3-4 days | Phase 4 |

**Total**: ~3 weeks of focused implementation

---

## Files to Create/Modify

### New Files

- `src/bilancio/dealer/bridge.py` - Contract-to-ticket conversion
- `src/bilancio/engines/dealer_integration.py` - Subsystem wrapper
- `tests/integration/test_dealer_integration.py` - Integration tests
- `examples/scenarios/kalecki_with_dealer.yaml` - Example scenario

### Modified Files

- `src/bilancio/domain/instruments/credit.py` - Add `holder_id`
- `src/bilancio/engines/simulation.py` - Add dealer phase
- `src/bilancio/config/loaders.py` - Load dealer config
- `src/bilancio/config/models.py` - Dealer config schema
- `src/bilancio/experiments/ring.py` - Sweep with dealer option

---

## Open Questions

1. **Dealer/VBT as Agents**: Should dealers and VBTs be represented as proper `Agent` instances in the main system, or remain as separate entities in the subsystem?

2. **Cash Flow Tracking**: When a trader sells a payable to the dealer, should we create an explicit "sale" event in the main ledger, or just track via dealer events?

3. **Default Distribution**: Current settlement distributes to payable creditors. With transfers, need to distribute to current holders (dealers, VBTs, or traders who bought).

4. **Multi-Bucket Holdings**: If a trader holds claims in multiple buckets, which to sell first? (Spec says shortest maturity, but need to implement.)

---

## References

- `docs/dealer_ring/dealer_specification.pdf` - Full specification
- `docs/dealer_ring/dealer_examples.pdf` - Worked examples
- `docs/dealer_ring/dealer_implementation_readiness.pdf` - Readiness assessment
- `docs/dealer_ring/conversations/` - Design discussions
- `examples/dealer_ring/` - 14 verified examples
