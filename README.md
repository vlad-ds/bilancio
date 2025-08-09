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
│   ├── analysis/       # Analysis tools
│   │   └── metrics.py  # Financial metrics (NPV, IRR, etc.)
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