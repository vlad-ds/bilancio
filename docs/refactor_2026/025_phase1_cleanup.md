# Plan 025: Phase 1 Codebase Cleanup & Restructuring

**Date:** January 2026
**Branch:** `refactor/phase-1-cleanup`
**Risk Level:** Medium
**Estimated Effort:** 2-3 days

## Overview

This plan addresses all structural issues identified in the 2026 codebase analysis:
- Remove dead code
- Split large files into focused modules
- Add test coverage for critical untested code
- Consolidate overlapping modules

## Pre-Implementation Baseline

Before making any changes, establish a baseline:

```bash
# 1. Run full test suite and record results
uv run pytest tests/ -v 2>&1 | tee baseline_tests.txt
uv run pytest tests/ --collect-only | grep "test session starts" -A 5

# 2. Record coverage baseline
uv run pytest tests/ --cov=bilancio --cov-report=term-missing > baseline_coverage.txt

# 3. Verify clean git status
git status
```

**Expected baseline:** 276 tests passing, 53% coverage.

---

## Part A: Remove Dead Code

### A1. Delete `modules/dealer_ring/`

**Problem:** Empty directory with only `__pycache__` artifacts, no source files.

**Evidence:**
```bash
ls -laR src/bilancio/modules/  # Only __pycache__
grep -r "from bilancio.modules" src/  # Zero matches
```

**Action:**
```bash
rm -rf src/bilancio/modules/
```

### A2. Delete `io/` Module

**Problem:** Stub module with functions that only raise `NotImplementedError`. Never imported.

**Evidence:**
```bash
cat src/bilancio/io/readers.py  # Just raises NotImplementedError
cat src/bilancio/io/writers.py  # Just raises NotImplementedError
grep -r "from bilancio.io" src/  # Zero matches
```

**Action:**
```bash
rm -rf src/bilancio/io/
```

### A3. Archive Stale `TODO.md`

**Problem:** Single stale item with no context.

**Action:**
```bash
mkdir -p docs/archive
mv TODO.md docs/archive/TODO_2025.md
```

### A4. Verification

```bash
uv run pytest tests/ -v
uv run python -c "import bilancio; print('OK')"
```

---

## Part B: Split Large Files

### B1. Split `ui/cli.py` (1,100+ lines)

**Problem:** Mixes sweep commands, run logic, and display formatting in one file.

**Current structure:**
```
ui/cli.py  # 1,100+ lines, 34% test coverage
```

**Target structure:**
```
ui/cli/
├── __init__.py      # Main CLI entry point, click group
├── run.py           # `bilancio run` command
├── sweep.py         # `bilancio sweep` commands (ring, comparison)
└── utils.py         # Shared utilities (output formatting, etc.)
```

**Implementation steps:**

1. Create `ui/cli/` directory structure
2. Extract `run` command and related functions to `run.py`
3. Extract `sweep` commands to `sweep.py`
4. Keep main click group and shared utilities in `__init__.py`
5. Update imports in `__init__.py` to re-export commands
6. Verify CLI still works: `uv run bilancio --help`

**Key functions to move:**

To `run.py`:
- `run()` command
- `_run_scenario()`
- `_display_results()`
- Related helper functions

To `sweep.py`:
- `sweep()` group
- `sweep_ring()` command
- `sweep_comparison()` command
- Related configuration handling

### B2. Split `analysis/visualization.py` (2,200+ lines)

**Problem:** Balance display, event display, and phase visualization all in one massive file. Only 13% test coverage.

**Current structure:**
```
analysis/visualization.py  # 2,200+ lines, 13% coverage
```

**Target structure:**
```
analysis/visualization/
├── __init__.py           # Re-exports public API
├── balances.py           # T-account and balance sheet display
├── events.py             # Event table formatting
├── phases.py             # Phase summary visualization
└── common.py             # Shared utilities (formatting, styles)
```

**Implementation steps:**

1. Create `analysis/visualization/` directory
2. Identify logical groupings in existing file:
   - Balance-related: `display_agent_balance_table`, `build_t_account_rows`, etc.
   - Event-related: `display_events`, `display_events_for_day`, `build_event_rows`, etc.
   - Phase-related: `display_events_tables_by_phase_renderables`, etc.
3. Move functions to appropriate files
4. Create `__init__.py` that re-exports all public functions (preserve API)
5. Update internal imports
6. Verify: `uv run python -c "from bilancio.analysis.visualization import display_agent_balance_table"`

### B3. Split `experiments/ring.py` (680+ lines)

**Problem:** Runner logic mixed with three different sampling strategies.

**Current structure:**
```
experiments/ring.py  # 680+ lines, 25% coverage
```

**Target structure:**
```
experiments/
├── ring.py              # RingSweepRunner (slimmed down)
├── sampling/
│   ├── __init__.py      # Re-exports
│   ├── grid.py          # Grid/Cartesian product sampling
│   ├── lhs.py           # Latin Hypercube Sampling
│   └── frontier.py      # Frontier/binary search sampling
```

**Implementation steps:**

1. Create `experiments/sampling/` directory
2. Extract `_generate_grid_params()` → `sampling/grid.py`
3. Extract `_generate_lhs_params()` → `sampling/lhs.py`
4. Extract `_generate_frontier_params()` → `sampling/frontier.py`
5. Update imports in `ring.py`
6. Verify sweep commands still work

### B4. Consolidate `ui/render/` with `analysis/visualization/`

**Problem:** Overlapping rendering logic in two places.

**Analysis needed:** Determine if `ui/render/` should:
- Be merged into `analysis/visualization/`
- Stay separate (UI-specific vs analysis-specific)

**Current `ui/render/` contents:**
```
ui/render/
├── formatters.py      # HTML formatters
├── models.py          # Render data models
└── rich_builders.py   # Rich table builders
```

**Decision:** Keep separate for now. The `ui/render/` module is specifically for HTML/Rich output formatting, while `analysis/visualization/` is for higher-level visualization logic. Document this distinction in module docstrings.

### B5. Verification After Splits

```bash
# Full test suite
uv run pytest tests/ -v

# Verify all imports work
uv run python -c "
from bilancio.ui.cli import main
from bilancio.analysis.visualization import display_agent_balance_table
from bilancio.experiments.ring import RingSweepRunner
from bilancio.experiments.sampling import grid, lhs, frontier
print('All imports OK')
"

# Verify CLI works
uv run bilancio --help
uv run bilancio run examples/scenarios/simple_bank.yaml --max-days 3 --quiet

# Verify sweep works
uv run bilancio sweep ring --help
```

---

## Part C: Add Test Coverage

### C1. Add Tests for `experiments/` Framework (Currently 0-25%)

**Priority:** HIGH - This drives research, must be tested.

**Target files:**
- `experiments/ring.py` - 25% → 70%
- `experiments/comparison.py` - 0% → 60%
- `experiments/balanced_comparison.py` - 0% → 60%

**Test file:** `tests/experiments/test_sweep_runners.py`

**Tests to add:**

```python
# test_sweep_runners.py

class TestRingSweepRunner:
    def test_grid_sweep_small(self, tmp_path):
        """Test grid sweep with 2x2 parameter grid."""
        # 2 kappas × 2 concentrations = 4 runs

    def test_lhs_sampling(self, tmp_path):
        """Test LHS generates correct number of samples."""

    def test_registry_created(self, tmp_path):
        """Test that registry CSV is created and populated."""

    def test_resume_from_registry(self, tmp_path):
        """Test sweep can resume from partial registry."""

class TestComparisonSweepRunner:
    def test_paired_runs(self, tmp_path):
        """Test control/treatment pairs have same seed."""

    def test_comparison_metrics(self, tmp_path):
        """Test delta_reduction and relief_ratio computed."""

class TestBalancedComparisonRunner:
    def test_passive_vs_active(self, tmp_path):
        """Test C vs D comparison runs."""
```

### C2. Add Tests for `analysis/visualization/` (Currently 13%)

**Priority:** Medium - UI-facing but not critical path.

**Target:** 13% → 50%

**Test file:** `tests/analysis/test_visualization.py`

**Tests to add:**

```python
# test_visualization.py

class TestBalanceDisplay:
    def test_display_agent_balance_table_rich(self, sample_system):
        """Test rich format balance display."""

    def test_display_agent_balance_table_simple(self, sample_system):
        """Test simple format balance display."""

    def test_display_multiple_agents(self, sample_system):
        """Test multi-agent balance comparison."""

class TestEventDisplay:
    def test_display_events_filtering(self, sample_system):
        """Test event filtering by kind."""

    def test_display_events_for_day(self, sample_system):
        """Test day-specific event display."""

class TestBuildFunctions:
    def test_build_t_account_rows(self, sample_system):
        """Test T-account row generation."""

    def test_build_event_rows(self, sample_system):
        """Test event row formatting."""
```

### C3. Add Tests for `ui/cli/` (Currently 34%)

**Priority:** Medium - User-facing entry point.

**Target:** 34% → 60%

**Test file:** `tests/ui/test_cli_integration.py`

**Tests to add:**

```python
# test_cli_integration.py

class TestRunCommand:
    def test_run_simple_scenario(self, tmp_path):
        """Test basic scenario execution."""

    def test_run_with_html_output(self, tmp_path):
        """Test HTML export flag."""

    def test_run_with_max_days(self, tmp_path):
        """Test max-days limit."""

class TestSweepCommands:
    def test_sweep_ring_help(self):
        """Test sweep ring --help works."""

    def test_sweep_ring_dry_run(self, tmp_path):
        """Test sweep with minimal config."""
```

### C4. Coverage Verification

After adding tests:

```bash
# Run with coverage
uv run pytest tests/ --cov=bilancio --cov-report=term-missing

# Check specific modules improved
uv run pytest tests/experiments/ --cov=bilancio.experiments --cov-report=term-missing
uv run pytest tests/analysis/ --cov=bilancio.analysis --cov-report=term-missing
uv run pytest tests/ui/ --cov=bilancio.ui --cov-report=term-missing
```

**Target coverage:**
- Overall: 53% → 60%
- `experiments/`: 0-25% → 60%+
- `analysis/visualization`: 13% → 50%
- `ui/cli`: 34% → 60%

---

## Part D: Flatten `scenarios/generators/`

### D1. Analysis

**Current structure:**
```
scenarios/
├── __init__.py
└── generators/
    ├── __init__.py        # Exports compile_generator
    └── ring_explorer.py   # Main generator
```

**Imports to update:**
```python
# config/loaders.py:178
from bilancio.scenarios.generators import compile_generator

# experiments/ring.py:28
from bilancio.scenarios.generators.ring_explorer import compile_ring_explorer

# experiments/ring.py:533
from bilancio.scenarios.generators.ring_explorer import compile_ring_explorer_balanced
```

### D2. Target Structure

```
scenarios/
├── __init__.py           # Re-exports compile_generator, compile_ring_explorer
└── ring_explorer.py      # Moved up from generators/
```

### D3. Implementation

1. Move `generators/ring_explorer.py` to `scenarios/ring_explorer.py`
2. Move exports from `generators/__init__.py` to `scenarios/__init__.py`
3. Delete `generators/` directory
4. Update imports in `config/loaders.py` and `experiments/ring.py`
5. Add backwards-compatible re-exports in `scenarios/__init__.py`

### D4. Backwards Compatibility

To avoid breaking any external code, add deprecation shim:

```python
# scenarios/__init__.py
from .ring_explorer import compile_ring_explorer, compile_ring_explorer_balanced

def compile_generator(config, *, source_path=None):
    """Compile a generator specification into a scenario dictionary."""
    from bilancio.config.models import RingExplorerGeneratorConfig
    if isinstance(config, RingExplorerGeneratorConfig):
        return compile_ring_explorer(config, source_path=source_path)
    raise ValueError(f"Unsupported generator '{getattr(config, 'generator', 'unknown')}'")

__all__ = ["compile_generator", "compile_ring_explorer", "compile_ring_explorer_balanced"]

# Backwards compatibility - keep generators as alias
# TODO: Remove in next major version
try:
    from . import generators  # Will fail after removal, that's OK
except ImportError:
    pass
```

---

## Implementation Order

Execute in this order to minimize risk:

1. **Part A: Dead code removal** (10 min)
   - Lowest risk, clears clutter first
   - Run tests after

2. **Part D: Flatten scenarios/generators/** (30 min)
   - Simple move with import updates
   - Run tests after

3. **Part B1: Split ui/cli.py** (2-3 hours)
   - High value, moderate complexity
   - Run tests after

4. **Part B2: Split analysis/visualization.py** (2-3 hours)
   - Largest file, most benefit
   - Run tests after

5. **Part B3: Split experiments/ring.py** (1 hour)
   - Cleaner separation of concerns
   - Run tests after

6. **Part C: Add test coverage** (3-4 hours)
   - Add tests incrementally
   - Run full suite after each test file

---

## Verification Checklist

After each part, verify:

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] All imports work (see verification script above)
- [ ] CLI works: `uv run bilancio --help`
- [ ] Run command works: `uv run bilancio run examples/scenarios/simple_bank.yaml --max-days 3`
- [ ] Sweep help works: `uv run bilancio sweep ring --help`

---

## Final Verification

After all changes:

```bash
# 1. Full test suite
uv run pytest tests/ -v

# 2. Coverage report
uv run pytest tests/ --cov=bilancio --cov-report=html
open htmlcov/index.html

# 3. Comprehensive import check
uv run python -c "
# Core
from bilancio.core import time, atomic, errors, ids, invariants

# Domain
from bilancio.domain.agents import Agent, Bank, Household, Firm, CentralBank, Dealer
from bilancio.domain.instruments import Payable, DeliveryObligation, Cash, BankDeposit
from bilancio.domain import policy

# Engines
from bilancio.engines import simulation, settlement, clearing
from bilancio.engines.system import System

# Dealer
from bilancio.dealer import kernel, trading, metrics

# Analysis
from bilancio.analysis import balances, metrics as analysis_metrics, report
from bilancio.analysis.visualization import display_agent_balance_table, display_events

# Experiments
from bilancio.experiments.ring import RingSweepRunner
from bilancio.experiments.comparison import ComparisonSweepRunner
from bilancio.experiments.sampling import grid, lhs, frontier

# Scenarios
from bilancio.scenarios import compile_generator, compile_ring_explorer

# Config
from bilancio.config import models, loaders, apply

# Export
from bilancio.export import writers

# UI
from bilancio.ui.cli import main
from bilancio.ui import display, html_export

print('All imports successful!')
"

# 4. Run example scenario end-to-end
uv run bilancio run examples/scenarios/simple_bank.yaml --max-days 5 --html temp/final_test.html
open temp/final_test.html

# 5. Compare test count (should be higher due to new tests)
uv run pytest tests/ --collect-only | grep "test session starts" -A 5
```

---

## Rollback Plan

If any step fails catastrophically:

```bash
# Revert all uncommitted changes
git checkout -- .
git clean -fd

# Or revert to specific commit
git log --oneline -10  # Find last good commit
git reset --hard <commit-hash>
```

---

## Success Criteria

| Metric | Before | Target |
|--------|--------|--------|
| Test count | 276 | 300+ |
| Overall coverage | 53% | 60%+ |
| `experiments/` coverage | 0-25% | 60%+ |
| `visualization` coverage | 13% | 50%+ |
| `ui/cli` coverage | 34% | 60%+ |
| Largest file | 2,200 lines | <500 lines |
| Dead code modules | 2 | 0 |

---

## File Changes Summary

**Deleted:**
- `src/bilancio/modules/` (dead)
- `src/bilancio/io/` (dead stubs)
- `TODO.md` (archived)
- `src/bilancio/scenarios/generators/` (flattened)

**Split:**
- `ui/cli.py` → `ui/cli/{__init__,run,sweep,utils}.py`
- `analysis/visualization.py` → `analysis/visualization/{__init__,balances,events,phases,common}.py`
- `experiments/ring.py` → `experiments/ring.py` + `experiments/sampling/{grid,lhs,frontier}.py`

**Added:**
- `tests/experiments/test_sweep_runners.py`
- `tests/analysis/test_visualization.py`
- `tests/ui/test_cli_integration.py`
- `docs/archive/TODO_2025.md`
