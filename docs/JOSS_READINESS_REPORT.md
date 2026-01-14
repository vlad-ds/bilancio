# Bilancio JOSS Readiness Assessment

Generated: 2026-01-14

This report assesses the current state of the Bilancio repository for JOSS (Journal of Open Source Software) submission readiness.

---

## 1. Repository Structure

```
bilancio/
├── src/bilancio/           # Main source package
│   ├── analysis/           # Analytics and metrics computation
│   │   └── visualization/  # Display and visualization tools
│   ├── cloud/              # Modal cloud execution support
│   ├── config/             # YAML configuration parsing
│   ├── core/               # Core types (atomic values, errors, ids)
│   ├── dealer/             # L1 dealer pricing kernel and models
│   ├── domain/             # Domain models
│   │   ├── agents/         # Agent types (Bank, Firm, Household, etc.)
│   │   └── instruments/    # Financial instruments (contracts, credit)
│   ├── engines/            # Simulation and settlement engines
│   ├── experiments/        # Parameter sweep and experiment runners
│   │   └── sampling/       # Sampling strategies
│   ├── export/             # Export utilities
│   ├── jobs/               # Job management system
│   ├── ops/                # Operations on domain objects
│   ├── runners/            # Local and cloud execution runners
│   ├── scenarios/          # Scenario generation (ring topology)
│   ├── storage/            # Storage backends (file, Supabase)
│   └── ui/                 # User interface
│       ├── cli/            # Command-line interface
│       └── render/         # HTML/text rendering
├── tests/                  # Test suites
│   ├── analysis/           # Analytics tests
│   ├── cloud/              # Cloud execution tests
│   ├── config/             # Configuration tests
│   ├── dealer/             # Dealer system tests
│   ├── engines/            # Engine tests
│   ├── experiments/        # Experiment runner tests
│   ├── integration/        # Integration tests
│   ├── ops/                # Operations tests
│   ├── runners/            # Runner tests
│   ├── scenarios/          # Scenario tests
│   ├── storage/            # Storage tests
│   ├── ui/                 # UI/CLI tests
│   └── unit/               # Unit tests
├── examples/               # Example scenarios and scripts
│   ├── dealer_ring/        # Dealer ring worked examples (14 examples)
│   ├── exercise_scenarios/ # Tutorial exercise scenarios (7 examples)
│   ├── kalecki/            # Kalecki ring scenarios
│   └── scenarios/          # Various demo scenarios
├── notebooks/              # Jupyter notebooks
│   └── demo/               # Demo notebooks
├── docs/                   # Documentation (internal)
│   ├── dealer_ring/        # Dealer specification documents
│   ├── guides/             # Usage guides
│   ├── plans/              # Implementation plans
│   ├── prompts/            # Agent prompts
│   └── refactor_2026/      # Refactoring documentation
├── supabase/               # Supabase migrations
└── scripts/                # Utility scripts
```

---

## 2. README.md

**Status:** EXISTS - Comprehensive

The README.md (286 lines) includes:
- Project overview and features
- Installation instructions
- Project structure diagram
- Quick start code example
- Development guide (tests, code quality, pre-commit hooks)
- CLI documentation with examples
- Simulation configuration details
- Analytics metrics explanation
- Scheduling and phases documentation
- Default-handling modes

**Gaps identified:**
- Repository URL is placeholder: `https://github.com/yourusername/bilancio`
- Documentation URL may be non-functional: `https://bilancio.readthedocs.io/`
- No citation information (CITATION.cff)

---

## 3. Installation/Setup Files

### pyproject.toml
**Status:** EXISTS - Well-configured

**Key details:**
- Package name: `bilancio`
- Version: `0.1.0`
- Python requirement: `>=3.11`
- License: MIT (declared in metadata)
- Build system: setuptools

**Dependencies (production):**
- numpy, pandas, scipy (scientific computing)
- pydantic (data validation)
- networkx (graph structures)
- matplotlib, seaborn, plotly, altair (visualization)
- streamlit (web UI)
- pyyaml, click, rich (CLI/config)
- jupyter, notebook (notebooks)
- modal (cloud execution)
- supabase (cloud storage)

**Optional dependencies:**
- `dev`: pytest, hypothesis, mypy, black, ruff, isort, pre-commit
- `docs`: sphinx, sphinx-rtd-theme, myst-parser
- `examples`: jupyter, notebook

**Tool configurations included:**
- pytest (with coverage settings)
- mypy (strict mode)
- ruff (linting)
- black (formatting)
- isort (import sorting)

**Missing files:**
- `setup.py` - Not present (not required with pyproject.toml)
- `requirements.txt` - Not present (dependencies in pyproject.toml)
- `environment.yml` - Not present (conda not used)

---

## 4. Documentation State

### docs/ Folder
**Status:** EXISTS - Contains internal documentation

**Contents:**
- `codebase_for_llm.md` - LLM-focused codebase summary
- `exercises_scenarios.md` - Exercise documentation
- `version_1_0_exercises.pdf` - PDF exercises
- **PDF theory documents:**
  - `Kalecki_debt_simulation.pdf`
  - `Monetary Theory Chapter 5.pdf`
  - `Money modeling software.pdf`
  - Various specification documents

**Subfolders:**
- `analysis/` - Analysis reports
- `dealer_ring/` - Dealer specification PDFs and conversations
- `guides/` - Usage guides (e.g., `kalecki_ring_sweep.md`)
- `plans/` - Implementation plans (31 planning documents)
- `prompts/` - Agent prompt templates
- `refactor_2026/` - Refactoring documentation

### API Documentation
**Status:** NOT PRESENT

No generated API documentation (Sphinx/ReadTheDocs). The `docs` optional dependency includes Sphinx but no `docs/source/` or `docs/conf.py` exists.

### Docstrings
**Status:** PRESENT - Good coverage in core modules

**Sample from `src/bilancio/dealer/kernel.py`:**
```python
"""
L1 dealer pricing kernel.

This module implements the core L1 dealer pricing formulas from Section 8
of the specification. It computes all derived dealer quantities from the
current inventory and VBT anchor prices.

The kernel is the mathematical heart of the dealer system, computing:
- Capacity: Maximum fundable buy tickets (K*, X*)
- Layoff probability: Risk-neutral hedging probability (λ)
- Inside width: Competitive equilibrium spread (I)
- Midline: Inventory-sensitive mid price p(x)
- Clipped quotes: Final bid/ask quotes b_c(x), a_c(x)

All arithmetic uses Decimal for precision - never float.
"""
```

**Sample from `src/bilancio/core/atomic.py`:**
```python
@dataclass
class Money:
    """Represents a monetary amount with currency."""
    amount: Decimal
    currency: str

    @property
    def value(self) -> Decimal:
        """Return the monetary amount as the atomic value."""
        return self.amount
```

**Sample from `src/bilancio/engines/simulation.py`:**
```python
class SimulationEngine(Protocol):
    """Protocol for simulation engines that can run financial scenarios."""

    def run(self, scenario: Any) -> Any:
        """
        Run a simulation for a given scenario.

        Args:
            scenario: The scenario to simulate

        Returns:
            Simulation results
        """
        ...
```

---

## 5. Tests

### Test Structure
**Status:** EXISTS - Comprehensive test suite

**Framework:** pytest (with pytest-cov, pytest-asyncio, hypothesis)

**Test organization:**
```
tests/
├── analysis/          (5 test files)
├── cloud/             (2 test files)
├── config/            (5 test files)
├── dealer/            (5 test files)
├── engines/           (3 test files)
├── experiments/       (1 test file)
├── integration/       (5 test files)
├── ops/               (1 test file)
├── runners/           (3 test files)
├── scenarios/         (1 test file)
├── storage/           (3 test files)
├── ui/                (6 test files)
├── unit/              (5 test files)
└── test_smoke.py      (1 smoke test)
```

**Total:** ~53 test files, ~13,522 lines of test code

**Test commands (from CLAUDE.md):**
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=bilancio --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_balances.py -v
```

---

## 6. Examples/Notebooks

### Jupyter Notebooks
**Location:** `notebooks/demo/`

| Notebook | Description |
|----------|-------------|
| `balance_sheet_display.ipynb` | Demonstrates balance sheet visualization |
| `pdf_example_with_firms.ipynb` | PDF generation example with firm agents |

### Example Scripts and Scenarios

**Location:** `examples/`

**Dealer Ring Examples** (`examples/dealer_ring/`):
14 worked examples demonstrating dealer mechanics:
- `example1_migrating_claim.py` - Claim migration
- `example2_cross_bucket.py` - Cross-bucket operations
- `example3_clip_toggle.py` - Clip toggle behavior
- `example4_vbt_layoff.py` - VBT layoff mechanics
- `example5_dealer_earns.py` - Dealer earnings
- `example6_bid_passthrough.py` - Bid passthrough
- `example7_no_interior_clipping.py` - Interior clipping rules
- `example8_guard_low_M.py` - Guard conditions
- `example9_partial_recovery.py` - Partial recovery
- `example10_trader_rebucket.py` - Trader rebucketing
- `example11_partial_recovery.py` - Additional partial recovery
- `example12_capacity_crossing.py` - Capacity crossing
- `example13_event_loop.py` - Event loop demonstration
- `example14_ticket_transfer.py` - Ticket transfer mechanics

Each example has a corresponding HTML report in `examples/dealer_ring/reports/`.

**Exercise Scenarios** (`examples/exercise_scenarios/`):
7 tutorial scenarios with YAML + HTML:
- `ex1_cash_for_goods` - Basic cash exchange
- `ex2_two_firms_cash_purchase` - Two-firm transaction
- `ex3_iou_assignment` - IOU assignment
- `ex4_generic_claim_transfer` - Claim transfer
- `ex5_deferred_exchange` - Deferred exchange
- `ex6_goods_now_cash_later` - Credit transaction
- `ex7_cash_now_goods_later` - Prepayment transaction

**Other Scenarios** (`examples/scenarios/`):
- `simple_bank.yaml` - Simple banking scenario
- `simple_dealer.yaml` - Basic dealer scenario
- `kalecki_with_dealer.yaml` - Kalecki model with dealer
- `interbank_netting.yaml` - Interbank netting
- `firm_delivery.yaml` - Firm delivery obligations
- `default_handling_demo.yaml` - Default handling modes
- And more...

---

## 7. License

**Status:** MISSING

**Critical gap:** No LICENSE file exists in the repository root.

The `pyproject.toml` declares MIT license:
```toml
license = {text = "MIT"}
```

And the README states:
> This project is licensed under the MIT License - see the LICENSE file for details.

But the actual LICENSE file does not exist.

---

## 8. Core Module Overview

| Module | Purpose |
|--------|---------|
| `bilancio.core` | Core types: atomic values (Money, Quantity, Rate), errors, IDs, invariants, time modeling |
| `bilancio.domain` | Domain models for agents and financial instruments |
| `bilancio.domain.agents` | Agent types: Bank, CentralBank, Dealer, Firm, Household, Treasury, VBT |
| `bilancio.domain.instruments` | Financial instruments: contracts, credit, delivery obligations, means of payment, policy |
| `bilancio.config` | YAML scenario configuration parsing and validation |
| `bilancio.engines` | Simulation engines: settlement (Phase B), clearing (Phase C), day simulation |
| `bilancio.dealer` | L1 dealer pricing kernel, models, metrics, and simulation |
| `bilancio.analysis` | Analytics: metrics computation, balance analysis, visualization, reporting |
| `bilancio.experiments` | Parameter sweep runners for ring and balanced comparison experiments |
| `bilancio.scenarios` | Scenario generation (ring topology explorer, Kalecki rings) |
| `bilancio.runners` | Execution runners: local executor and cloud executor |
| `bilancio.cloud` | Modal cloud deployment and execution |
| `bilancio.storage` | Storage backends: file store, Supabase client, artifact loaders |
| `bilancio.jobs` | Job management: creation, tracking, persistence |
| `bilancio.export` | Export utilities for simulation results |
| `bilancio.ops` | Operations on domain objects (settlements, transfers, aliases) |
| `bilancio.ui.cli` | Command-line interface (run, validate, analyze, sweep commands) |
| `bilancio.ui.render` | HTML and text rendering for simulation reports |

---

## JOSS Readiness Summary

### Ready (Green)
- [x] Source code is well-organized in `src/` layout
- [x] `pyproject.toml` with proper metadata
- [x] Comprehensive README with usage examples
- [x] Test suite with pytest (~53 test files, ~13k lines)
- [x] Examples directory with worked scenarios
- [x] Jupyter notebooks for demonstration
- [x] Docstrings in core modules
- [x] CLI for running simulations
- [x] Version control (git)

### Needs Work (Yellow)
- [ ] API documentation not generated (Sphinx configured but not built)
- [ ] README has placeholder URLs (need real GitHub repo URL)
- [ ] No CITATION.cff file
- [ ] No CONTRIBUTING.md file
- [ ] No CODE_OF_CONDUCT.md file
- [ ] Author information is placeholder in pyproject.toml

### Critical Gaps (Red)
- [ ] **LICENSE file missing** (declared as MIT but file doesn't exist)
- [ ] **No published documentation** (readthedocs URL may be non-functional)
- [ ] **No paper.md** (required JOSS submission file)

---

## Recommended Actions for JOSS Submission

1. **Create LICENSE file** - Add MIT license text to repository root
2. **Create paper.md** - JOSS-format paper describing the software
3. **Create CITATION.cff** - Machine-readable citation file
4. **Update pyproject.toml** - Replace placeholder author info
5. **Update README.md** - Replace placeholder URLs with real repository URL
6. **Build API docs** - Generate Sphinx documentation
7. **Deploy documentation** - Publish to ReadTheDocs or GitHub Pages
8. **Add CONTRIBUTING.md** - Contribution guidelines
9. **Add CODE_OF_CONDUCT.md** - Community standards

---

## Quick Reference

**Repository:** (needs real URL)
**License:** MIT (needs LICENSE file)
**Python:** >=3.11
**Test command:** `uv run pytest tests/ -v`
**Run example:** `uv run bilancio run examples/scenarios/simple_bank.yaml --html temp/demo.html`
