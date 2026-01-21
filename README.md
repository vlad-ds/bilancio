# Bilancio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Documentation Status](https://readthedocs.org/projects/bilancio/badge/?version=latest)](https://bilancio.readthedocs.io/en/latest/?badge=latest)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/vlad-ds/bilancio/releases/tag/v0.1.0)

A Python framework for simulating multi-agent payment systems and settlement dynamics. Bilancio is designed for research on financial microstructure, particularly studying how liquidity constraints and secondary market dealers affect payment settlement in economic networks.

## Key Features

- **Multi-agent payment simulation** - Model agents (Firms, Banks, Dealers, Central Bank, Households) interacting in payment networks with balance sheet accounting
- **Settlement engine** - Day-by-day simulation with settlement phases, configurable default handling (fail-fast, expel-agent), and invariant checking
- **Kalecki ring scenarios** - Circular payment flows through firm networks with configurable parameters:
  - `kappa` (liquidity ratio L/S)
  - `concentration` (debt distribution inequality)
  - `mu` (maturity timing skew)
- **Secondary market dealers** - Market makers that trade payables, providing liquidity to constrained agents through bid/ask pricing
- **Rich analytics** - Settlement metrics including phi/delta rates (clearing/default), liquidity gaps, netting potential, and intraday velocity
- **Cloud execution** - Run parameter sweeps on Modal with automatic result aggregation
- **YAML-based scenarios** - Declarative scenario configuration with scheduled actions and contract aliases

## Quick Start

Run a simple scenario:

```bash
uv run bilancio run examples/scenarios/simple_dealer.yaml --max-days 5 --html output.html
```

Run a parameter sweep comparing passive vs active dealer regimes:

```bash
uv run bilancio sweep balanced --cloud \
  --n-agents 50 --kappas "0.3,0.5,1" --concentrations "1" \
  --out-dir out/experiments/my_sweep
```

## Installation

```bash
git clone https://github.com/vlad-ds/bilancio.git
cd bilancio
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Documentation

Full documentation is available at [https://bilancio.readthedocs.io/](https://bilancio.readthedocs.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
