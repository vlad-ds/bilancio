# Quick Start

This guide will help you run your first Bilancio simulation and understand the results. By the end, you'll know how to:

- Run pre-built scenarios
- Understand the key metrics
- Enable dealer secondary markets
- Run parameter sweeps to study system behavior

## Prerequisites

- **Python 3.11+**
- **uv package manager** - Install from [astral.sh/uv](https://astral.sh/uv)

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/vlad-ds/bilancio.git
cd bilancio
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Your First Simulation

Run a simple banking scenario:

```bash
uv run bilancio run examples/scenarios/simple_bank.yaml --max-days 5 --html temp/result.html
open temp/result.html  # macOS
```

This simulates a central bank, a commercial bank, and two households with deposits and a payment obligation.

### Understanding the Output

The HTML report shows:

- **Scenario overview** - Name, description, and list of agents
- **Day-by-day events** - Setup actions, payments, settlements, and defaults
- **Balance sheets** - T-account style view of each agent's assets and liabilities

---

## The Kalecki Ring: Core Experiment Structure

The primary research use case for Bilancio is studying **circular payment dependencies** using the Kalecki ring model.

### What is the Kalecki Ring?

A Kalecki ring is a circular network where:
- Agent 1 owes Agent 2
- Agent 2 owes Agent 3
- ...
- Agent N owes Agent 1

Each agent's ability to pay depends on receiving payment from their predecessor. This creates the payment system dynamics that drive the research questions.

### Run a Ring Scenario

```bash
uv run bilancio run examples/scenarios/simple_dealer.yaml --max-days 5 --html temp/ring.html
```

This runs a 3-agent ring with:
- **kappa = 0.5** (liquidity-constrained: cash is half of total debt)
- **Dealers enabled** (secondary market trading)

### Key Parameters

| Parameter | Meaning | Effect |
|-----------|---------|--------|
| `kappa` (κ) | Liquidity ratio (L₀/S₁) | Lower = more stressed, higher default risk |
| `concentration` (c) | Debt distribution inequality | Lower = more unequal, fragile system |
| `mu` (μ) | Maturity timing skew | 0 = early due dates, 1 = late |

**Typical values:**
- κ = 0.3: Severely stressed
- κ = 1.0: Balanced (cash equals debt)
- κ = 2.0: Abundant liquidity

---

## Understanding Metrics

Every simulation produces key metrics that measure settlement performance:

### phi (φ) - Settlement Rate

**What it measures:** Fraction of obligations that settled successfully.

```
φ = 1.0  →  All payments settled (perfect)
φ = 0.8  →  80% settled, 20% defaulted
φ = 0.0  →  Complete system failure
```

### delta (δ) - Default Rate

**What it measures:** Fraction of obligations that defaulted (δ = 1 - φ).

```
δ = 0.0  →  No defaults
δ = 0.2  →  20% default rate
δ = 1.0  →  All obligations defaulted
```

### Example Output

When you run a simulation, you'll see metrics like:

```
Settlement Metrics:
  phi_total: 0.85    # 85% of obligations settled
  delta_total: 0.15  # 15% defaulted
  time_to_stability: 3
```

---

## Dealer Secondary Markets

The key innovation in Bilancio is modeling **secondary markets** where agents can trade their credit claims before maturity.

### Why Dealers Matter

Without dealers:
- An agent who needs cash today but holds a claim due tomorrow **cannot pay**
- Result: defaults cascade through the ring

With dealers:
- Agent can **sell the claim** to the dealer for immediate cash
- Result: liquidity mismatch is resolved, fewer defaults

### Run a Dealer Scenario

```bash
uv run bilancio run examples/scenarios/kalecki_with_dealer.yaml --max-days 5 --html temp/dealer.html
```

This shows a 5-agent Kalecki ring with dealer trading enabled. Check the HTML output to see:
- **PhaseB events**: Dealer trading occurs after scheduled actions
- **Trade events**: Which agents sold claims and at what price
- **Settlement outcomes**: Compare to a non-dealer scenario

### How Dealer Pricing Works

Dealers quote bid/ask prices that depend on:
- **VBT anchor prices** (M for mid, O for spread)
- **Current inventory** (dealers adjust prices as they accumulate tickets)
- **Maturity bucket** (short/mid/long term claims priced differently)

---

## Parameter Sweeps

To study how system behavior changes across conditions, run parameter sweeps.

### Ring Sweep (Basic)

Test different liquidity ratios:

```bash
uv run bilancio sweep ring \
  --n-agents 20 \
  --kappas "0.3,0.5,1,2" \
  --concentrations "1" \
  --maturity-days 10 \
  --out-dir out/my_sweep
```

Results are saved to `out/my_sweep/` with:
- Individual run outputs
- Aggregate metrics CSV
- Summary statistics

### Balanced Sweep (Compare Dealer Impact)

The most important experiment: compare **passive** (no dealers) vs **active** (dealers enabled) regimes:

```bash
uv run bilancio sweep balanced \
  --n-agents 50 \
  --kappas "0.3,0.5,1" \
  --concentrations "1" \
  --mus "0,0.5" \
  --out-dir out/dealer_comparison
```

This runs each parameter combination twice:
1. **Passive regime**: No secondary market trading
2. **Active regime**: Dealer trading enabled

The output includes `comparison.csv` showing the **trading effect**:

```
trading_effect = δ_passive - δ_active
```

A positive trading effect means dealers reduced the default rate.

---

## Cloud Execution

For large sweeps, run on Modal cloud for parallel execution:

```bash
uv run bilancio sweep balanced --cloud \
  --n-agents 100 \
  --kappas "0.25,0.5,1,2" \
  --concentrations "0.5,1,2" \
  --out-dir out/cloud_sweep
```

The `--cloud` flag runs simulations in parallel on Modal. You'll receive a **Job ID** like `castle-river-mountain` to track and retrieve results:

```bash
# Check job status
uv run bilancio jobs ls --cloud

# Get job details
uv run bilancio jobs get castle-river-mountain --cloud
```

See [CLI Reference](cli.md) for full cloud execution documentation.

---

## Export Data for Analysis

Export simulation data for further analysis:

```bash
uv run bilancio run examples/scenarios/kalecki_with_dealer.yaml \
  --max-days 5 \
  --export-events temp/events.jsonl \
  --export-balances temp/balances.csv
```

**events.jsonl** - One JSON object per line:
```json
{"kind": "PayableSettled", "day": 1, "phase": "simulation", "debtor": "H1", "creditor": "H2", "amount": 500}
{"kind": "DealerTrade", "day": 1, "phase": "dealer", "seller": "H3", "buyer": "D1", "price": 95}
```

**balances.csv** - End-of-simulation balance sheet snapshot.

---

## Creating Custom Scenarios

Create a scenario file with agents and payment obligations:

```yaml
# my_scenario.yaml
version: 1
name: "My First Scenario"
description: "Two firms with a payment obligation"

agents:
  - id: CB
    kind: central_bank
    name: Central Bank
  - id: B1
    kind: bank
    name: Commercial Bank
  - id: F1
    kind: firm
    name: Acme Corp
  - id: F2
    kind: firm
    name: Widget Inc

initial_actions:
  # Give the bank reserves
  - mint_reserves: {to: B1, amount: 5000}

  # Give firms some cash and deposits
  - mint_cash: {to: F1, amount: 200}
  - mint_cash: {to: F2, amount: 100}
  - deposit_cash: {customer: F1, bank: B1, amount: 800}
  - deposit_cash: {customer: F2, bank: B1, amount: 400}

  # Create a payment: F1 owes F2 $300, due on day 1
  - create_payable: {from: F1, to: F2, amount: 300, due_day: 1}

run:
  mode: until_stable
  max_days: 10
```

Run it:

```bash
uv run bilancio run my_scenario.yaml --html temp/my_result.html
```

### Agent Types

| Kind | Description |
|------|-------------|
| `central_bank` | Issues reserves and cash |
| `bank` | Holds reserves, accepts deposits, facilitates payments |
| `firm` | Business entity, can hold deposits and cash |
| `household` | Consumer entity, similar to firm |
| `dealer` | Secondary market maker (auto-created when enabled) |

### Common Actions

| Action | Description |
|--------|-------------|
| `mint_reserves` | Central bank creates reserves for a bank |
| `mint_cash` | Central bank creates cash for an agent |
| `deposit_cash` | Agent deposits cash at a bank |
| `create_payable` | Create a payment obligation between agents |

---

## Next Steps

- **[Core Concepts](concepts.md)** - Deep dive into agents, instruments, and settlement mechanics
- **[CLI Reference](cli.md)** - Full documentation of all commands
- **[Examples](https://github.com/vlad-ds/bilancio/tree/main/examples/scenarios)** - More scenario files
