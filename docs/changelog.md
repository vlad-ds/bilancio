# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-21

### Added

#### Core Framework
- Multi-agent balance sheet system with double-entry bookkeeping invariants
- Agent types: CentralBank, Bank, Household, Firm, Dealer, Treasury, VBT
- Financial instruments: Cash, BankDeposit, ReserveDeposit, Payable, DeliveryObligation
- Policy engine for controlling instrument holding/issuing permissions
- Atomic transaction support with rollback on failure

#### Simulation Engine
- Day-by-day simulation with configurable phases (A/B/C)
- Settlement engine with means-of-payment ranking
- Two default handling modes: `fail-fast` and `expel-agent`
- YAML-based scenario configuration
- Run modes: `until_stable`, `fixed_days`

#### Dealer Module
- L1 dealer pricing formulas (bid/ask quotes)
- Virtual Balance Theorem (VBT) implementation
- Secondary market trading for payables
- Dealer state management and inventory tracking

#### Analysis & Metrics
- Balance sheet analysis (`agent_balance`, `system_trial_balance`)
- Settlement microstructure metrics (phi, delta, velocity, liquidity gap)
- Day-level and aggregate metric computation
- Interactive visualizations with Plotly

#### Cloud Execution
- Modal cloud integration for parallel sweep execution
- Supabase persistence for jobs, runs, and metrics
- Job ID system with memorable passphrases
- Progress tracking and event logging

#### CLI Interface
- `bilancio run` - Execute scenarios
- `bilancio validate` - Validate scenario files
- `bilancio analyze` - Analyze simulation results
- `bilancio sweep` - Run parameter sweeps (ring, balanced)
- `bilancio jobs` - Query cloud job storage
- `bilancio volume` - Manage Modal volume artifacts

#### Examples
- Kalecki ring scenarios (baseline, varied parameters)
- Bank intermediation examples
- Dealer trading scenarios
- Parameter sweep experiments

### Infrastructure
- Comprehensive test suite (585 tests, 61% coverage)
- CI/CD with GitHub Actions
- Development tooling with uv package manager

## [Unreleased]

### Planned
- API documentation (ReadTheDocs)
- Additional agent behaviors
- Extended settlement algorithms

---

For detailed commit history, see the [GitHub repository](https://github.com/vlad-ds/bilancio).
