# Plan 018: Dealer Comparison Experiments

**Status**: IN PROGRESS
**Date**: 2025-11-28
**Goal**: Run comparative experiments measuring the effect of dealer-mediated secondary markets on default rates in Kalecki ring simulations.

---

## Executive Summary

With the dealer integration complete (Plan 016), we can now run controlled experiments comparing:
- **Control**: 100-agent Kalecki ring WITHOUT dealer (baseline)
- **Treatment**: Same 100-agent Kalecki ring WITH dealer enabled

The key outcome is the **delta in defaults** (`delta_total`) between conditions, answering: "Does the dealer reduce defaults, and by how much?"

---

## Requirements (from conversation 20251127)

| Requirement | Source | Notes |
|-------------|--------|-------|
| 100 agents | "we said that we want a hundred" (line 84) | Scale up from 5-agent examples |
| Control = no dealer | "control is that you have 100 agents without dealer or VBT" (line 93) | Baseline measurement |
| Treatment = with dealer | "same exact thing, but with the dealer" (line 105-111) | Same grid, same agents |
| Same grid exploration | "we still do all the variables" (line 104) | κ, c, μ parameters |
| Delta in defaults | "the amount of default compared to the previous case is less or more" (line 81) | Primary outcome variable |
| Natural termination | "when the maturity ends, the debts end" (line 125-129) | Run until all maturities resolve |
| C1-C6 verification | "the checks run continuously" (line 141-150) | Dealer assertions from PDF |

---

## Metrics (consistent with existing code)

Using the same metric names from `bilancio.analysis.report`:

| Metric | Meaning | Source |
|--------|---------|--------|
| `phi_t` | Settlement rate for day t (% of dues settled on time) | `analysis/metrics.py` |
| `delta_t` | Default rate for day t = 1 - phi_t | `analysis/metrics.py` |
| `phi_total` | Weighted average settlement rate across all days | `analysis/report.py` |
| `delta_total` | Weighted average default rate across all days | `analysis/report.py` |
| `S_t` | Total dues on day t | existing |
| `G_t` | Liquidity gap on day t | existing |
| `alpha_t` | Netting efficiency | existing |

**Comparison metrics** (new, derived from existing):

| Metric | Formula | Meaning |
|--------|---------|---------|
| `delta_control` | delta_total from control run | Baseline default rate |
| `delta_treatment` | delta_total from treatment run | Default rate with dealer |
| `delta_reduction` | delta_control - delta_treatment | Absolute reduction in defaults |
| `relief_ratio` | delta_reduction / delta_control | Percentage reduction (when delta_control > 0) |

---

## Architecture

### Experiment Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    PARAMETER GRID                                │
│         κ × c × μ (same as Plan 014)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
   ┌─────────────────┐       ┌─────────────────┐
   │    CONTROL      │       │   TREATMENT     │
   │  (no dealer)    │       │  (with dealer)  │
   │                 │       │                 │
   │  n_agents: 100  │       │  n_agents: 100  │
   │  dealer: false  │       │  dealer: true   │
   │  same seed      │       │  same seed      │
   └────────┬────────┘       └────────┬────────┘
            │                         │
            ▼                         ▼
   ┌─────────────────┐       ┌─────────────────┐
   │ delta_control   │       │ delta_treatment │
   │ phi_control     │       │ phi_treatment   │
   └────────┬────────┘       └────────┬────────┘
            │                         │
            └───────────┬─────────────┘
                        ▼
   ┌─────────────────────────────────────────┐
   │         COMPARISON RESULTS              │
   │                                         │
   │  delta_reduction = δ_ctrl - δ_treat     │
   │  relief_ratio = reduction / δ_ctrl      │
   └─────────────────────────────────────────┘
```

### Folder Structure

```
out/experiments/<timestamp>_dealer_comparison/
├── registry.csv                    # All runs with condition column
├── control/
│   └── runs/
│       └── grid_<hash>/
│           ├── scenario.yaml
│           ├── run.html
│           └── out/
│               ├── events.jsonl
│               ├── balances.csv
│               └── metrics.csv
├── treatment/
│   └── runs/
│       └── grid_<hash>/           # Same hash = same parameters
│           ├── scenario.yaml
│           ├── run.html
│           └── out/
│               ├── events.jsonl
│               ├── balances.csv
│               ├── metrics.csv
│               └── dealer_events.jsonl
└── aggregate/
    ├── comparison.csv             # Side-by-side metrics per grid point
    └── summary.json               # Aggregate statistics
```

---

## Implementation Steps

### Phase 1: Extend Sweep Runner for Paired Runs

**Goal**: Modify `RingSweepRunner` to run control/treatment pairs.

#### 1.1 Add Comparison Mode to Config

```python
# In experiments/ring.py or new experiments/comparison.py

class ComparisonSweepConfig(BaseModel):
    """Configuration for dealer comparison experiments."""

    # Base sweep settings (shared between control/treatment)
    n_agents: int = 100
    maturity_days: int = 10  # 10 days of maturity
    Q_total: Decimal = Decimal("10000")
    base_seed: int = 42

    # Grid parameters
    kappas: List[Decimal]
    concentrations: List[Decimal]
    mus: List[Decimal]

    # Dealer configuration for treatment runs
    dealer_ticket_size: Decimal = Decimal("1")
    dealer_share: Decimal = Decimal("0.25")
    vbt_share: Decimal = Decimal("0.50")

    # Output
    out_dir: Path
```

#### 1.2 Create `ComparisonSweepRunner`

```python
# New file: src/bilancio/experiments/comparison.py

class ComparisonSweepRunner:
    """
    Runs paired control/treatment experiments for dealer comparison.

    For each parameter combination (κ, c, μ):
    1. Generate scenario YAML (same for both conditions)
    2. Run WITHOUT dealer -> control metrics
    3. Run WITH dealer -> treatment metrics
    4. Log results to registry
    """

    def run_all(self) -> None:
        """Execute all control/treatment pairs."""
        for params in self._generate_grid():
            self._run_pair(params)

    def _run_pair(self, params: Dict) -> Tuple[Dict, Dict]:
        """Run one control/treatment pair."""
        # Control run
        control_result = self._run_single(params, dealer_enabled=False)

        # Treatment run (same scenario, dealer enabled)
        treatment_result = self._run_single(params, dealer_enabled=True)

        # Log comparison
        self._log_comparison(params, control_result, treatment_result)

        return control_result, treatment_result
```

### Phase 2: Scale to 100 Agents

**Goal**: Ensure infrastructure handles 100-agent rings.

#### 2.1 Verify Ring Explorer Generator

The existing `ring_explorer.py` should handle 100 agents. Verify:
- Dirichlet with 100 components works
- 100 scheduled payables created
- Performance acceptable

#### 2.2 Simulation Duration

With `maturity_days: 10`, ensure simulation runs long enough:

```python
# In scenario generation or run config
run:
  mode: until_stable
  max_days: 15  # Buffer beyond max maturity
```

### Phase 3: Dealer Assertions Integration

**Goal**: Run C1-C6 checks during treatment runs.

```python
# In engines/dealer_integration.py - already exists, ensure enabled

def run_dealer_trading_phase(
    system: System,
    subsystem: DealerSubsystem,
    current_day: int,
) -> List[Dict]:
    # ... trading logic ...

    # Run C1-C6 assertions (already in place from Plan 016)
    # These will raise if violated
```

### Phase 4: Comparison Aggregation

**Goal**: Compute and output comparison metrics.

#### 4.1 Registry Schema

```csv
# registry.csv columns:
run_id,condition,kappa,concentration,mu,seed,phi_total,delta_total,max_G_t,alpha_1,time_to_stability,status
```

#### 4.2 Comparison Output

```csv
# comparison.csv columns:
kappa,concentration,mu,seed,delta_control,delta_treatment,delta_reduction,relief_ratio,phi_control,phi_treatment
```

#### 4.3 Summary Statistics

```json
// summary.json
{
  "total_runs": 250,
  "control_runs": 125,
  "treatment_runs": 125,
  "mean_delta_control": 0.15,
  "mean_delta_treatment": 0.08,
  "mean_relief_ratio": 0.47,
  "grid_points_with_improvement": 98,
  "grid_points_no_change": 27
}
```

### Phase 5: CLI Extension

**Goal**: Add `bilancio sweep comparison` command.

```python
@sweep.command("comparison")
@click.option('--out-dir', type=click.Path(path_type=Path), required=True)
@click.option('--n-agents', type=int, default=100)
@click.option('--maturity-days', type=int, default=10)
@click.option('--kappas', type=str, default="0.25,0.5,1,2,4")
@click.option('--concentrations', type=str, default="0.2,0.5,1,2,5")
@click.option('--mus', type=str, default="0,0.25,0.5,0.75,1")
@click.option('--base-seed', type=int, default=42)
def sweep_comparison(...):
    """
    Run dealer comparison experiments.

    For each parameter combination, runs control (no dealer) and
    treatment (with dealer), outputting comparison metrics.
    """
```

---

## Grid Specification

### Coarse Grid (125 parameter combinations × 2 conditions = 250 runs)

| Variable | Values | Count |
|----------|--------|-------|
| κ (kappa) | 0.25, 0.5, 1, 2, 4 | 5 |
| c (concentration) | 0.2, 0.5, 1, 2, 5 | 5 |
| μ (mu) | 0, 0.25, 0.5, 0.75, 1 | 5 |

### Fixed Settings

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| n_agents | 100 | Per conversation requirement |
| Q_total | 10000 | Scale with agent count |
| maturity_days | 10 | Allow time for trading before settlement |
| max_simulation_days | 15 | Ensure all maturities resolve |
| liquidity_mode | uniform | Equal starting position |
| ticket_size | 1 | Fine granularity |
| dealer_share | 0.25 | Standard from spec |
| vbt_share | 0.50 | Standard from spec |

---

## Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `src/bilancio/experiments/comparison.py` | ComparisonSweepRunner and config |
| `tests/experiments/test_comparison.py` | Unit tests for comparison logic |

### Modified Files

| File | Changes |
|------|---------|
| `src/bilancio/ui/cli.py` | Add `sweep comparison` command |
| `src/bilancio/analysis/report.py` | Add comparison aggregation functions |

---

## Validation

### Unit Tests

```python
def test_comparison_runner_produces_paired_results():
    """Each grid point has both control AND treatment results."""

def test_delta_reduction_computed_correctly():
    """delta_reduction = delta_control - delta_treatment."""

def test_relief_ratio_handles_zero_baseline():
    """When delta_control = 0, relief_ratio = 0 (no defaults to reduce)."""

def test_100_agent_ring_completes():
    """100-agent ring runs without errors."""
```

### Integration Tests

```python
def test_full_comparison_sweep_small_grid():
    """Run 2x2x2 grid comparison and verify outputs exist."""

def test_dealer_assertions_pass():
    """C1-C6 checks pass for all treatment runs."""
```

---

## Example Usage

```bash
# Run full comparison (125 × 2 = 250 runs)
uv run bilancio sweep comparison \
  --out-dir out/experiments/dealer_comparison \
  --n-agents 100 \
  --maturity-days 10 \
  --kappas "0.25,0.5,1,2,4" \
  --concentrations "0.2,0.5,1,2,5" \
  --mus "0,0.25,0.5,0.75,1" \
  --base-seed 42

# View results
cat out/experiments/dealer_comparison/aggregate/comparison.csv
cat out/experiments/dealer_comparison/aggregate/summary.json
```

---

## Success Criteria

1. **Functional**: `bilancio sweep comparison` runs 100-agent paired experiments
2. **Correct**: C1-C6 assertions pass for all treatment runs
3. **Complete**: Comparison metrics computed for all 125 grid points
4. **Structured**: Clean CSV/JSON outputs with consistent metric names
5. **Reproducible**: Same seed produces identical results

---

## Known Limitations

### Dealer Trading Not Yet Active

The dealer subsystem is now connected to scenario loading and simulation:
- Dealer subsystem initializes when `dealer.enabled: true` in scenario YAML
- `SubphaseB_Dealer` events are generated each day
- However, **actual trades do not occur** because:
  - Trader cash is initialized to 0 in `initialize_dealer_subsystem`
  - Cash is never synced from main system agent balance sheets
  - Trading eligibility checks fail due to 0 cash

**Fix needed in `dealer_integration.py`:**
- In `initialize_dealer_subsystem`: Set `trader.cash` from agent's actual cash holdings
- In `run_dealer_trading_phase`: Sync trader cash before checking eligibility

Until this is fixed, control and treatment runs will produce identical results.

---

## References

- Plan 014: Kalecki experiments (sweep infrastructure, metric definitions)
- Plan 016: Dealer-Kalecki integration (dealer subsystem)
- `docs/dealer_ring/dealer_specification.pdf` (C1-C6 assertions)
- `src/bilancio/analysis/report.py` (existing metrics: phi_total, delta_total)
- Conversation 20251127: Requirements from Jamie/Riley discussion
