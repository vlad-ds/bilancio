# Scenarios: Create and Run (Cheat Sheet)

Quick reference for defining a scenario YAML and running it through the Bilancio CLI.

## 1) Scenario File Location
- Put scenario files under `examples/scenarios/` with a `.yaml` extension.
- Example: `examples/scenarios/my_scenario.yaml`.

## 2) Minimal YAML Template
```yaml
version: 1
name: "My Scenario"
description: "One-line description"

# Optional: override means-of-payment preferences
# policy_overrides:
#   mop_rank:
#     firm: ["bank_deposit", "cash"]
#     household: ["bank_deposit", "cash"]

agents:
  - id: CB
    kind: central_bank
    name: Central Bank
  - id: B1
    kind: bank
    name: Bank One
  - id: F1
    kind: firm
    name: Firm One
  - id: F2
    kind: firm
    name: Firm Two

initial_actions:
  # Seed reserves and cash as needed
  - mint_reserves: {to: B1, amount: 10000}
  - mint_cash: {to: F1, amount: 500}

  # Example deposit / payable
  - deposit_cash: {customer: F1, bank: B1, amount: 400}
  - create_payable: {from: F1, to: F2, amount: 300, due_day: 1}

run:
  mode: until_stable        # or: step
  max_days: 30
  quiet_days: 2
  show:
    balances: [CB, B1, F1, F2]
    events: detailed        # summary | detailed
  export:
    # Optional: set default exports (can be overridden by CLI)
    balances_csv: "out/my_scenario_balances.csv"
    events_jsonl: "out/my_scenario_events.jsonl"
```

## 3) Common Actions (quick examples)
- Reserves: `- mint_reserves: {to: B1, amount: 1000}`
- Cash: `- mint_cash: {to: F1, amount: 200}`
- Deposit: `- deposit_cash: {customer: F1, bank: B1, amount: 100}`
- Withdraw: `- withdraw_cash: {customer: F1, bank: B1, amount: 50}`
- Client payment: `- client_payment: {payer: F1, payee: F2, amount: 75}`
- Payable: `- create_payable: {from: F1, to: F2, amount: 150, due_day: 1}`
- Delivery obligation: `- create_delivery_obligation: {from: F1, to: F2, sku: ITEM, quantity: 10, unit_price: "5", due_day: 2}`

Tip: Interbank settlement needs sufficient bank reserves. Seed banks with `mint_reserves`.

## 4) Validate the Scenario
Validate structure and that it can be applied:
```bash
PYTHONPATH=src .venv/bin/python -m bilancio.ui.cli validate examples/scenarios/my_scenario.yaml
```

## 5) Run the Scenario
Run until stable and export HTML output:
```bash
PYTHONPATH=src .venv/bin/python -m bilancio.ui.cli \
  run examples/scenarios/my_scenario.yaml \
  --max-days 30 \
  --check-invariants daily \
  --html temp/my_scenario.html
```

Useful flags:
- `--mode step` to confirm day-by-day.
- `--quiet-days 2` required quiet days for stability.
- `--agents CB,B1,F1,F2` to select balances at runtime.
- `--export-balances out/bal.csv` and `--export-events out/ev.jsonl` to override exports.

Open the HTML report from `temp/my_scenario.html`.

## 6) Example: sasa_scenario
A worked example exists at `examples/scenarios/sasa_scenario.yaml`:
- Firm A: $100 cash and $100 deposit at Bank A
- Firm B: $100 deposit at Bank B
- Payable: Firm A owes Firm B $150 (day 1)

Run it:
```bash
PYTHONPATH=src .venv/bin/python -m bilancio.ui.cli \
  run examples/scenarios/sasa_scenario.yaml \
  --max-days 5 \
  --check-invariants daily \
  --html temp/sasa_scenario.html
```

## Notes
- Config schema is defined in `src/bilancio/config/models.py`.
- The CLI entrypoint is `bilancio.ui.cli` (`run`, `validate`, `new`).
- Default means-of-payment ranking is in `src/bilancio/domain/policy.py` and can be overridden via `policy_overrides.mop_rank`.
