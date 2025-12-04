# Plan 021: Balanced Dealer Comparison (C & D Implementation)

## Overview

This plan implements the three-way comparison framework from Section 9.3 of the specification, based on Alex's feedback (2025-12-04). The goal is to create a fair comparison between:

- **C (Mimic/Passive)**: Big entities holding securities + cash but NOT trading
- **D (Dealer/Active)**: Same starting position but WITH trading enabled

The key insight: comparing dealers vs no-big-entities is "apples and oranges" because the structure of holdings differs. The proper comparison is passive holders vs active dealers, with identical starting balance sheets.

## Requirements from Alex's Feedback

### 1. Face Value and Outside Mid

**Face value = 20** (configurable ticket size as cashflow at maturity)

**Outside mid M** is a percentage of face value:
- M = 20 → 100% of face value (at par)
- M = 18 → 90% of face value (10% discount)
- M = 16 → 80% of face value (20% discount)
- M = 15 → 75% of face value (25% discount)
- M = 10 → 50% of face value (50% discount)

### 2. How Securities Are Allocated to Big Entities

Alex's approach: "Each trader has an additional percent of debt liabilities given its debt in no big entities case, the claim on that debt is held by relevant big entity."

**Translation:**
- In baseline (no big entities): Each trader has debt D_i and cash C_i
- In C/D scenarios: Each trader issues ADDITIONAL debt (e.g., 25% more)
- The claims on this additional debt go to big entities
- Traders also get more cash to preserve their original cash-to-debt ratio

### 3. Balanced Position for Big Entities

Big entities (dealers/mimics) are "balanced":
- Cash = Market value of securities held
- If they hold N tickets and M = 15: Cash = N × 15

### 4. Comparison Structure

| Comparison | Purpose |
|------------|---------|
| Passive holders vs Active dealers | **Main comparison**: Effect of market-making |
| Passive holders vs No big entities | Secondary: Effect of loss absorption |
| Dealers vs No big entities | NOT recommended (confounded by holdings structure) |

## Design

### Key Parameters

```yaml
# New configuration parameters
balanced_dealer:
  enabled: true
  face_value: 20              # S = cashflow at maturity
  outside_mid_ratio: 0.75     # M/S ratio (0.5 to 1.0)
  big_entity_share: 0.25      # Fraction of total debt held by big entities
  mode: "passive" | "active"  # C = passive, D = active
```

### Scenario Generation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    BASELINE SCENARIO                             │
│  (No big entities - reference for ratios)                       │
│                                                                  │
│  100 traders with:                                              │
│  - Total debt: Q_total                                          │
│  - Total cash: L_total = Q_total / kappa                        │
│  - Each trader i: debt D_i, cash C_i                            │
│  - Original cash/debt ratio: r_i = C_i / D_i                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               C/D SCENARIO GENERATION                            │
│                                                                  │
│  For each trader i:                                             │
│  1. Original debt: D_i                                          │
│  2. Additional debt for big entities: D_i × big_entity_share    │
│  3. New total debt: D_i × (1 + big_entity_share)                │
│  4. Additional cash to preserve ratio: C_i × big_entity_share   │
│  5. New total cash: C_i × (1 + big_entity_share)                │
│                                                                  │
│  Big entity holdings:                                           │
│  - Securities: sum of all additional debts                      │
│  - Cash: securities × outside_mid                               │
│  - (This makes them "balanced")                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │    C (PASSIVE)  │   │    D (ACTIVE)   │
    │                 │   │                 │
    │  Big entities:  │   │  Big entities:  │
    │  - Hold tickets │   │  - Hold tickets │
    │  - Hold cash    │   │  - Hold cash    │
    │  - NO trading   │   │  - CAN trade    │
    │                 │   │                 │
    │  Can absorb     │   │  Active market  │
    │  defaults but   │   │  making with    │
    │  don't trade    │   │  spread quotes  │
    └─────────────────┘   └─────────────────┘
```

### Mathematics

**Given baseline scenario:**
- Total debt: Q
- Total cash: L = Q / κ
- Trader i debt: D_i (from Dirichlet)
- Trader i cash: C_i (from allocation)

**Augmented scenario (C or D):**
- Big entity share: β (e.g., 0.25)
- Face value: S (e.g., 20)
- Outside mid ratio: ρ (e.g., 0.75)
- Outside mid: M = ρ × S

**New allocations:**
- Trader i debt: D_i × (1 + β)
- Trader i cash: C_i × (1 + β)
- Big entity securities value: β × Q × (M/S) = β × Q × ρ
- Big entity cash: β × Q × ρ (to be balanced)
- Total new cash in system: L × (1 + β) + β × Q × ρ

**Preservation of kappa:**
The original κ = Q / L. In augmented scenario:
- Total debt: Q × (1 + β)
- Trader cash: L × (1 + β)
- κ_traders = Q × (1 + β) / (L × (1 + β)) = κ ✓

Big entities hold additional capital (β × Q × ρ) but this is balanced against their securities holdings.

## Implementation Plan

### Phase 1: Configuration Extensions

**File:** `src/bilancio/config/models.py`

Add new configuration models:

```python
class BalancedDealerConfig(BaseModel):
    """Configuration for balanced dealer/mimic scenarios (C & D)."""

    enabled: bool = False
    face_value: Decimal = Field(
        default=Decimal("20"),
        description="Face value S - cashflow at maturity"
    )
    outside_mid_ratio: Decimal = Field(
        default=Decimal("0.75"),
        description="M/S ratio - outside mid as fraction of face value"
    )
    big_entity_share: Decimal = Field(
        default=Decimal("0.25"),
        description="Fraction of trader debt allocated to big entities"
    )
    mode: Literal["passive", "active"] = Field(
        default="active",
        description="passive = C (mimics), active = D (dealers)"
    )
```

### Phase 2: Ring Generator Extension

**File:** `src/bilancio/scenarios/generators/ring_explorer.py`

Extend `compile_ring_explorer()` to support balanced dealer scenarios:

```python
def compile_ring_explorer_balanced(
    config: RingExplorerGeneratorConfig,
    balanced_config: BalancedDealerConfig,
    *,
    source_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Generate a ring scenario with balanced big entities (C or D).

    The scenario augments the base ring with:
    1. Additional debt per trader (held by big entities)
    2. Additional cash per trader (preserves cash/debt ratio)
    3. Big entities initialized with securities + matching cash
    """
```

Key changes:
1. Scale up trader debts by (1 + big_entity_share)
2. Scale up trader cash by (1 + big_entity_share)
3. Create payables from traders to big entities for the additional debt
4. Initialize big entities with matching cash

### Phase 3: Big Entity Initialization

**File:** `src/bilancio/engines/dealer_integration.py`

Create new initialization path for balanced scenarios:

```python
def initialize_balanced_dealer_subsystem(
    system: System,
    payables: List[Payable],
    dealer_config: DealerConfig,
    balanced_config: BalancedDealerConfig,
    current_day: int,
) -> DealerSubsystem:
    """
    Initialize dealer subsystem with pre-allocated securities.

    Unlike the standard initialization (dealers start empty):
    - Big entities start WITH securities (claims on additional trader debt)
    - Big entities have cash = market value of securities
    - This creates "balanced" starting positions

    For mode="passive": Disable all trading (big entities just hold)
    For mode="active": Enable trading as normal
    """
```

Key differences from current `initialize_dealer_subsystem()`:
1. Big entities start with inventory > 0
2. Initial cash calculated as: inventory × M × S
3. For passive mode: set trading capacity to 0

### Phase 4: Passive Holder Logic

**File:** `src/bilancio/engines/dealer_integration.py`

For passive holders (mode="passive"):

```python
def run_dealer_trading_phase_passive(
    system: System,
    subsystem: DealerSubsystem,
    current_day: int,
) -> List[Dict]:
    """
    "Trading" phase for passive holders - NO trades occur.

    Big entities:
    - Still compute mark-to-market (for metrics)
    - Still absorb losses if their securities default
    - But never buy or sell
    """
    # Update metrics/snapshots only, no actual trades
    return []
```

### Phase 5: Comparison Experiment Framework

**File:** `src/bilancio/experiments/balanced_comparison.py` (NEW)

Create new comparison runner:

```python
class BalancedComparisonConfig(BaseModel):
    """Configuration for C vs D balanced comparison experiments."""

    # Ring parameters (same as ComparisonSweepConfig)
    n_agents: int = 100
    maturity_days: int = 10
    Q_total: Decimal = Decimal("10000")
    base_seed: int = 42

    # Grid parameters
    kappas: List[Decimal]
    concentrations: List[Decimal]
    mus: List[Decimal]

    # Balanced dealer parameters
    face_value: Decimal = Decimal("20")
    outside_mid_ratios: List[Decimal]  # e.g., [1.0, 0.9, 0.8, 0.75, 0.5]
    big_entity_share: Decimal = Decimal("0.25")


class BalancedComparisonRunner:
    """
    Runs C vs D comparison experiments.

    For each parameter combination (κ, c, μ, ρ):
    1. Run C (passive): Big entities hold but don't trade
    2. Run D (active): Big entities can trade
    3. Compute comparison metrics

    Outputs:
    - passive/: All passive holder runs
    - active/: All active dealer runs
    - aggregate/comparison.csv: C vs D metrics
    """
```

### Phase 6: New Comparison Metrics

**File:** `src/bilancio/experiments/balanced_comparison.py`

```python
@dataclass
class BalancedComparisonResult:
    """Result of a single C vs D comparison."""

    # Parameters
    kappa: Decimal
    concentration: Decimal
    mu: Decimal
    outside_mid_ratio: Decimal
    face_value: Decimal

    # C (Passive) metrics
    delta_passive: Decimal
    phi_passive: Decimal
    big_entity_loss_passive: Decimal  # Losses from defaults

    # D (Active) metrics
    delta_active: Decimal
    phi_active: Decimal
    big_entity_pnl_active: Decimal  # P&L from trading + losses

    # Comparison
    @property
    def trading_effect(self) -> Decimal:
        """Effect of trading = delta_passive - delta_active"""
        return self.delta_passive - self.delta_active

    @property
    def trading_relief_ratio(self) -> Decimal:
        """Percentage reduction in defaults from trading"""
        if self.delta_passive == 0:
            return Decimal(0)
        return self.trading_effect / self.delta_passive
```

### Phase 7: CLI Extension

**File:** `src/bilancio/ui/cli.py`

Add new sweep command:

```python
@sweep.command("balanced")
@click.option('--out-dir', type=click.Path(path_type=Path), required=True)
@click.option('--face-value', type=Decimal, default=Decimal("20"))
@click.option('--outside-mid-ratios', type=str, default="1.0,0.9,0.8,0.75,0.5")
@click.option('--big-entity-share', type=Decimal, default=Decimal("0.25"))
# ... other options
def sweep_balanced(...):
    """
    Run balanced C vs D comparison experiments.

    Compares passive holders (C) against active dealers (D) with
    identical starting balance sheets.
    """
```

### Phase 8: Tests

**File:** `tests/experiments/test_balanced_comparison.py`

```python
def test_balanced_initialization_creates_inventory():
    """Big entities start with securities in balanced mode."""

def test_balanced_traders_preserve_ratio():
    """Trader cash/debt ratio is preserved after augmentation."""

def test_passive_mode_no_trades():
    """Passive holders never execute trades."""

def test_active_mode_allows_trades():
    """Active dealers can trade normally."""

def test_outside_mid_affects_valuation():
    """Lower M means lower cash for balanced position."""

def test_face_value_scaling():
    """Face value S scales all prices correctly."""
```

## File Changes Summary

### New Files
| File | Purpose |
|------|---------|
| `src/bilancio/experiments/balanced_comparison.py` | C vs D comparison framework |
| `tests/experiments/test_balanced_comparison.py` | Tests for balanced comparison |

### Modified Files
| File | Changes |
|------|---------|
| `src/bilancio/config/models.py` | Add `BalancedDealerConfig` |
| `src/bilancio/scenarios/generators/ring_explorer.py` | Add balanced scenario generation |
| `src/bilancio/engines/dealer_integration.py` | Add balanced initialization + passive mode |
| `src/bilancio/ui/cli.py` | Add `sweep balanced` command |

## Implementation Order

1. **Phase 1**: Configuration extensions (BalancedDealerConfig)
2. **Phase 2**: Ring generator extension (augmented scenarios)
3. **Phase 3**: Balanced initialization (big entities with inventory)
4. **Phase 4**: Passive holder logic (no-trade mode)
5. **Phase 5**: Comparison framework (BalancedComparisonRunner)
6. **Phase 6**: New metrics (trading_effect, big_entity_pnl)
7. **Phase 7**: CLI extension (sweep balanced)
8. **Phase 8**: Tests

## Example Usage

```bash
# Run C vs D comparison with varying outside mid
uv run bilancio sweep balanced \
  --out-dir out/experiments/balanced_comparison \
  --n-agents 100 \
  --face-value 20 \
  --outside-mid-ratios "20,19,18,15,10" \
  --big-entity-share 0.25 \
  --kappas "0.5,1,2" \
  --concentrations "1,2" \
  --mus "0.25,0.5,0.75"

# View results
cat out/experiments/balanced_comparison/aggregate/comparison.csv
```

## Success Criteria

1. **Balanced initialization**: Big entities start with securities + matching cash
2. **Ratio preservation**: Trader cash/debt ratio unchanged from baseline
3. **Passive mode**: No trades occur in C scenarios
4. **Active mode**: Normal dealer trading in D scenarios
5. **Fair comparison**: C and D have identical starting positions
6. **Variable outside mid**: M can be set to any fraction of face value
7. **Metrics**: Trading effect clearly measured as D - C

## Related: A.1 Off-Balance Metric (Clarified)

Alex confirmed the meaning of A.1 "off-balance" metric:

> "This is correct - just how far it is from midpoint in inventory"

This means tracking how far the dealer's inventory is from the "midpoint" or neutral position. This should be added to the metrics:

```python
@property
def inventory_imbalance(self) -> int:
    """
    How far dealer inventory is from midpoint (neutral position).

    In the kernel, midpoint is typically 0 (dealer starts empty and
    builds inventory by buying). Positive = long, Negative = short.
    """
    return self.inventory  # Midpoint is 0
```

This metric helps understand:
- How "off-balance" the dealer becomes over time
- Whether dealer accumulates too much inventory (can't resell)
- Correlation between imbalance and P&L

---

## Open Questions

1. **VBT in balanced mode**: Should VBT also start with securities, or remain as outside liquidity provider only?
   - Current thinking: VBT remains as outside anchor, only dealer/mimics hold securities

2. **Multiple big entities**: Should we have separate mimic per bucket (short, mid, long)?
   - Current thinking: Yes, mirror the existing bucket structure

3. **Settlement of big entity claims**: When trader defaults, how is recovery allocated to big entity?
   - This should work automatically via existing settlement logic (big entity is holder of the claim)

4. **Initial inventory for balanced dealers**: In D mode, dealers start with securities. What's their "midpoint"?
   - Could redefine midpoint as initial inventory (so imbalance = current - initial)
   - Or keep midpoint at 0 and track absolute inventory level
