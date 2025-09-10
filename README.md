# Bilancio

A financial modeling framework for multi-agent economic systems.

## Overview

Bilancio is a Python framework designed for modeling complex financial systems with multiple interacting agents. It provides tools for:

- **Multi-agent modeling**: Define agents with various roles and behaviors
- **Financial instruments**: Model contracts, policies, and other financial instruments
- **Cash flow analysis**: Track and analyze cash flows between agents
- **Valuation engines**: Built-in support for various valuation methodologies
- **Simulation capabilities**: Monte Carlo and other simulation techniques
- **Time-aware computations**: Sophisticated time modeling for financial calculations

## Installation

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bilancio.git
cd bilancio
```

2. Create and activate a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package in development mode:
```bash
uv pip install -e ".[dev]"
```

## Project Structure

```
bilancio/
├── src/bilancio/
│   ├── core/           # Core data structures and utilities
│   │   ├── time.py     # Time modeling
│   │   ├── atomic.py   # Atomic values (Money, Quantity, Rate)
│   │   └── errors.py   # Exception hierarchy
│   ├── domain/         # Domain models
│   │   ├── agents/     # Agent definitions
│   │   └── instruments/# Financial instruments
│   ├── ops/            # Operations on domain objects
│   │   └── cashflows.py# Cash flow operations
│   ├── engines/        # Computation engines
│   │   ├── valuation.py# Valuation engines
│   │   └── simulation.py# Simulation engines
│   ├── analysis/       # Analysis & analytics tools
│   │   ├── loaders.py  # Analytics loaders (events JSONL, balances CSV)
│   │   ├── metrics.py  # Analytics for settlement microstructure + placeholders (NPV/IRR)
│   │   └── report.py   # Analytics reporting (CSV / JSON / HTML)
│   └── io/             # Input/output utilities
│       ├── readers.py  # Data readers
│       └── writers.py  # Data writers
├── tests/              # Test suites
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   ├── property/      # Property-based tests
│   └── scenarios/     # Scenario tests
└── examples/          # Example notebooks and scripts
```

## Quick Start

```python
from bilancio.core.time import TimeCoordinate, now
from bilancio.core.atomic import Money
from decimal import Decimal

# Create a time point
t0 = now()
t1 = TimeCoordinate(1.0)  # 1 time unit in the future

# Create money values
payment = Money(Decimal("1000.00"), "USD")
print(f"Payment: {payment.amount} {payment.currency}")
```

## Development

### Running Tests

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=bilancio --cov-report=term-missing
```

### Code Quality

Format code:
```bash
black src tests
isort src tests
```

Run linter:
```bash
ruff check src tests
```

Type checking:
```bash
mypy src
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pre-commit install
```

## Documentation

Full documentation is available at [https://bilancio.readthedocs.io/](https://bilancio.readthedocs.io/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Bilancio is inspired by financial modeling best practices and builds upon the Python scientific computing ecosystem.

## Scenarios and CLI

Bilancio ships with a simple CLI to run scenarios, validate YAML, scaffold new scenarios, and analyze results.

- `run`: Execute a scenario YAML.
- `validate`: Check a scenario file without running it.
- `new`: Create a new scenario from a template (interactive).
- `analyze`: Compute day‑level metrics and optional intraday diagnostics from exported events/balances.

Basic usage (from repo root):

```bash
# 1) Run a scenario and export HTML + data
PYTHONPATH=src .venv/bin/python -m bilancio.ui.cli \
  run examples/kalecki/kalecki_ring_baseline.yaml \
  --max-days 5 \
  --check-invariants daily \
  --html temp/kalecki_ring_baseline.html

# 2) Analyze day-level metrics and produce an HTML analytics report
PYTHONPATH=src .venv/bin/python -m bilancio.ui.cli \
  analyze \
  --events out/kalecki_ring_baseline_events.jsonl \
  --balances out/kalecki_ring_baseline_balances.csv \
  --days 1 \
  --html out/kalecki_ring_baseline_metrics.html
```

### `run` command (selected options)

- `--mode step|until-stable`: Interactive step‑by‑step or auto until quiet days.
- `--max-days N`: Cap simulation days.
- `--quiet-days N`: Required consecutive quiet days for stability.
- `--check-invariants setup|daily|none`: When to check invariants.
- `--agents CB,B1,...`: Select agents to display in the UI.
- `--export-balances PATH`, `--export-events PATH`: Override YAML export paths.
- `--html PATH`: Save a pretty simulation report.

### `analyze` command (selected options)

- `--events PATH`: Events JSONL exported by `run` (required).
- `--balances PATH`: Balances CSV (optional; improves liquidity gap `G_t`).
- `--days 1,2-4`: Days to analyze (list/range). Default: infer from data.
- `--out-csv PATH`, `--out-json PATH`: Day‑level metrics exports.
- `--intraday-csv PATH`: Optional intraday P(s) diagnostics per step.
- `--html PATH`: Self‑contained analytics HTML with explanations.

Outputs are written alongside the inputs by default, or to paths you provide.

### Analytics metrics (day‑level)

- `S_t`: Total dues maturing on day t.
- `Mbar_t`: Minimum net liquidity (sum of debtor shortfalls max(0, F_i − I_i)).
- `M_t`: Start‑of‑day money (means‑of‑payment). When `--balances` is given, computed from balances.
- `G_t`: Liquidity gap = max(0, Mbar_t − M_t).
- `alpha_t`: Netting potential = 1 − Mbar_t / S_t.
- `Mpeak_t`: Operational peak from realized settlement sequence (RTGS replay).
- `gross_settled_t`: Gross value settled on day t.
- `v_t`: Intraday velocity = gross_settled_t / Mpeak_t.
- `phi_t`: On‑time settlement ratio (dues with due_day=t that settle on day t).
- `delta_t`: 1 − phi_t.
- `HHIplus_t`: Concentration of positive net creditor positions.
- `DS_t(i)`: Debtor shortfall shares per agent (only when net debtors exist).

Intraday diagnostics export a prefix‑liquidity series `P_prefix` over settlement steps, so you can visualize how much money is “out in the circuit” at each step and where the peak occurs.

Example scenario: `examples/kalecki/kalecki_ring_baseline.yaml` demonstrates a 5‑agent ring where a quantity `Q` circulates and clears intraday. After running, open:

- Simulation report: `temp/kalecki_ring_baseline.html`
- Analytics report: `out/kalecki_ring_baseline_metrics.html`

## Scheduling, Phases, and Mid‑Simulation Actions

Bilancio runs each simulation day in phases:

- Phase A: reserved (start of day marker, currently no activity)
- Phase B: business logic split into two subphases
  - B1 — Scheduled Actions: user‑authored actions (from YAML) that mutate state for this day
  - B2 — Automated Settlements: engine settles all obligations due today
- Phase C: intraday clearing (e.g., interbank nets from today’s client payments)

This ordering ensures that any mid‑day changes you schedule are visible to settlement and clearing in the same day. In other words, B1 applies first, then B2 settles using the updated state, then C clears.

### Scheduling actions in YAML

Alongside `initial_actions` (applied during setup), scenarios may include `scheduled_actions`, which are executed on the specific `day` during Phase B1 in the order provided. Example:

```yaml
scheduled_actions:
  - day: 1
    action:
      create_delivery_obligation: {from: F1, to: H1, sku: CHAIR, quantity: 1, unit_price: "100", due_day: 2, alias: F1_chair_D2}
  - day: 1
    action:
      create_payable: {from: H1, to: F1, amount: 100, due_day: 2, alias: H1_pay_100_D2}
```

### Aliases and contract references

Creation actions can carry an optional `alias`, which you can reference later without knowing the runtime contract ID:

- `create_payable` / `create_delivery_obligation` support `alias`
- `mint_cash` / `mint_reserves` also accept `alias` (for completeness)
- A new `transfer_claim` action allows reassigning a claim by `contract_alias` or `contract_id`:

```yaml
scheduled_actions:
  - day: 2
    action:
      transfer_claim: {contract_alias: H1_pay_100_D2, to_agent: F3}
```

The UI displays a unified “ID/Alias” column in both events and balances (T‑accounts) so you can track the same contract across the lifecycle.

### Conflicts to avoid (B1 vs B2)

The B1 → B2 split is safe: B1 mutates state, then B2 settles based on that state. Typical coincidences work as expected (e.g., transferring a claim on its due day—B2 will pay the new holder). A few caveats:

- Manual delivery vs. delivery obligation due: If you transfer the same stock in B1 that a due delivery obligation expects to deliver in B2, settlement may fail (debtor no longer owns the stock). Prefer the obligation and let B2 deliver it.
- Manual cash transfer vs. payable due: If you send cash in B1 while a payable remains outstanding, B2 will still attempt to pay and may double‑pay or fail. Today, only B2 extinguishes payables.
- Ordering within B1 matters: Scheduled actions run top‑to‑bottom. Moving assets away before a same‑day settlement can cause failures—write actions in an order that matches your intent.

If you need to extinguish/cancel manually in B1, consider adding explicit actions (e.g., `settle_payable`, `cancel_delivery_obligation`) so B1 can fully settle/cancel without B2 duplicating the work.
