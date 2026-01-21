# Quick Start

This guide will help you run your first Bilancio simulation in minutes.

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

For detailed installation instructions, see [Installation](installation.md).

## Running Your First Simulation

Bilancio uses YAML files to define economic scenarios. Run an example scenario:

```bash
uv run bilancio run examples/scenarios/simple_bank.yaml --max-days 5 --html temp/result.html
```

This runs a simple banking scenario with:
- A central bank (CB)
- A commercial bank (B1)
- Two households (H1, H2) with deposits and a payment obligation

Open `temp/result.html` in your browser to see the simulation results.

## Understanding the Output

### HTML Report

The HTML report shows:

- **Scenario overview** - Name, description, and list of agents
- **Day-by-day events** - Setup actions, payments, settlements, and any defaults
- **Balance sheets** - T-account style view of each agent's assets and liabilities after each day

### Data Exports

Export structured data for further analysis:

```bash
uv run bilancio run examples/scenarios/simple_bank.yaml \
  --max-days 5 \
  --export-events temp/events.jsonl \
  --export-balances temp/balances.csv
```

**events.jsonl** - One JSON object per line, each representing an event:
```json
{"kind": "CashMinted", "day": 0, "phase": "setup", "to": "H1", "amount": 2000}
{"kind": "PayableSettled", "day": 1, "phase": "simulation", "debtor": "H1", "creditor": "H2", "amount": 500}
```

**balances.csv** - End-of-simulation balance sheet snapshot for all agents.

## Creating a Simple Scenario

Create a minimal scenario with a central bank, one bank, and two firms:

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

  # Give firms some cash
  - mint_cash: {to: F1, amount: 1000}
  - mint_cash: {to: F2, amount: 500}

  # F1 deposits cash at the bank
  - deposit_cash: {customer: F1, bank: B1, amount: 800}

  # F2 deposits cash at the bank
  - deposit_cash: {customer: F2, bank: B1, amount: 400}

  # Create a payment obligation: F1 owes F2 $300, due on day 1
  - create_payable: {from: F1, to: F2, amount: 300, due_day: 1}

run:
  mode: until_stable
  max_days: 10
  quiet_days: 2
  show:
    balances: [CB, B1, F1, F2]
    events: detailed
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

### Common Actions

| Action | Description |
|--------|-------------|
| `mint_reserves` | Central bank creates reserves for a bank |
| `mint_cash` | Central bank creates cash for an agent |
| `deposit_cash` | Agent deposits cash at a bank |
| `create_payable` | Create a payment obligation between two agents |

## Running a Parameter Sweep

Explore how system behavior changes across different parameter values:

```bash
uv run bilancio sweep ring \
  --n-agents 20 \
  --kappas "0.5,1,2" \
  --maturity-days 10 \
  --out-dir out/my_sweep
```

This runs a "ring" experiment where agents are arranged in a circle of debt obligations. The sweep tests different values of kappa (liquidity ratio).

Key parameters:

| Parameter | Description |
|-----------|-------------|
| `--n-agents` | Number of agents in the ring |
| `--kappas` | Liquidity ratios to test (lower = more stressed) |
| `--maturity-days` | Payment horizon in days |
| `--out-dir` | Directory for results |

Results are saved to `out/my_sweep/` with individual run outputs and aggregate metrics.

## Next Steps

- **[CLI Reference](cli.md)** - Full documentation of all commands and options
- **[Installation](installation.md)** - Detailed setup instructions
- **[Examples](https://github.com/vlad-ds/bilancio/tree/main/examples/scenarios)** - More scenario examples
