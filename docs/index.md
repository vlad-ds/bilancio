# Bilancio

A Python framework for simulating multi-agent payment systems and settlement dynamics.

## Overview

Bilancio is designed for research on financial microstructure, specifically studying how liquidity constraints and secondary market dealers affect payment settlement in interconnected financial systems. The framework enables rigorous simulation experiments with configurable agent networks, credit instruments, and settlement mechanisms.

## What is Bilancio?

Bilancio models payment systems as networks of heterogeneous agents exchanging financial instruments over time. Each simulation day progresses through defined settlement phases, allowing researchers to study:

- How liquidity propagates (or fails to propagate) through payment networks
- The impact of dealer intermediation on settlement outcomes
- Default cascades and systemic risk under various stress conditions
- Netting efficiency and clearing dynamics

The framework is particularly suited for analyzing **Kalecki ring** structures - circular payment networks where firms owe each other in a chain, creating interdependent liquidity requirements.

## Core Concepts

### Agents

Bilancio supports multiple agent types, each with distinct roles:

| Agent | Role |
|-------|------|
| **CentralBank** | Issues reserves, provides ultimate settlement medium |
| **Bank** | Holds reserve accounts, provides deposits to clients |
| **Firm** | Economic entity that issues and receives payables |
| **Household** | Consumer agent, holds deposits |
| **Dealer** | Secondary market maker, buys/sells payables for liquidity provision |
| **VBT** | Value-based trader, trades based on fundamental value |
| **Treasury** | Government fiscal agent |

### Instruments

Financial instruments tracked on agent balance sheets:

| Instrument | Description |
|------------|-------------|
| **Cash** | Physical currency |
| **BankDeposit** | Deposit liability of a bank |
| **ReserveDeposit** | Central bank liability held by banks |
| **Payable** | Credit obligation with maturity date and debtor/creditor |
| **DeliveryObligation** | Obligation to deliver goods or assets |
| **StockLot** | Equity holdings |

### Settlement Phases

Each simulation day proceeds through structured phases:

| Phase | Name | Activity |
|-------|------|----------|
| **A** | Day Start | Initialize day, compute dues |
| **B1** | Scheduled Actions | Execute pre-scheduled transactions |
| **B** | Dealer Trading | Dealers quote and trade payables |
| **B2** | Settle Dues | Attempt to settle maturing obligations |
| **C** | Interbank Netting | Multilateral netting of interbank positions |

### Key Parameters

When configuring Kalecki ring experiments, three parameters control system dynamics:

| Parameter | Symbol | Description | Range |
|-----------|--------|-------------|-------|
| **Liquidity Ratio** | kappa | Initial liquidity relative to total dues (L0/S1) | 0.1 - 5.0 |
| **Concentration** | c | Dirichlet parameter controlling debt distribution inequality | 0.1 - 10.0 |
| **Maturity Skew** | mu | When debts mature (0=early, 1=late) | 0.0 - 1.0 |

**Parameter Intuition:**

- **Low kappa (< 0.5)**: Severely liquidity-constrained system, expect defaults
- **Low concentration (< 0.5)**: Unequal debt distribution, some agents owe much more
- **Low mu (near 0)**: Front-loaded payment pressure, stress occurs early

## Metrics

Bilancio computes settlement metrics to evaluate system performance:

| Metric | Symbol | Description |
|--------|--------|-------------|
| **Settlement Ratio** | phi_t | Fraction of dues settled on time |
| **Default Rate** | delta_t | Fraction of dues that default (1 - phi_t) |
| **Liquidity Gap** | G_t | Shortfall between required and available liquidity |
| **Netting Potential** | alpha_t | Efficiency of multilateral netting |

## Key Features

- **YAML-based scenarios**: Define agent networks, initial balances, and payment schedules declaratively
- **Interactive CLI**: Step through simulations or run to stability
- **HTML visualization**: Rich reports showing events, balance sheets, and metrics
- **Parameter sweeps**: Explore behavior across kappa, concentration, and mu grids
- **Cloud execution**: Run large sweep experiments on Modal
- **Analytics pipeline**: Compute day-level and aggregate metrics automatically

## Use Cases

Bilancio is designed for:

- **Payment systems research**: Study settlement dynamics, liquidity requirements, and default cascades
- **Dealer impact analysis**: Measure how secondary market makers affect settlement outcomes
- **Stress testing**: Explore system behavior under liquidity constraints
- **Netting efficiency studies**: Analyze multilateral clearing mechanisms
- **Financial microstructure education**: Demonstrate payment system concepts interactively

## Quick Navigation

- [Installation](installation.md) - Set up Bilancio locally
- [Quick Start](quickstart.md) - Run your first simulation
- [CLI Reference](cli.md) - Command-line interface documentation
- [Kalecki Ring Sweeps](guides/kalecki_ring_sweep.md) - Parameter exploration guide
- [Contributing](contributing.md) - How to contribute
- [Changelog](changelog.md) - Version history

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vlad-ds/bilancio/blob/main/LICENSE) file for details.

## Citation

If you use Bilancio in your research, please cite:

```bibtex
@software{bilancio,
  author = {Gheorghe, Vlad},
  title = {Bilancio: A Framework for Multi-Agent Payment System Simulation},
  url = {https://github.com/vlad-ds/bilancio}
}
```
