# Quick Start

## Basic Usage

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

## Running a Scenario

Bilancio uses YAML files to define scenarios. Here's how to run one:

```bash
# Run a scenario and export HTML report
uv run bilancio run examples/scenarios/simple_bank.yaml \
  --max-days 5 \
  --html temp/result.html
```

## Analyzing Results

After running a simulation, you can analyze the results:

```bash
uv run bilancio analyze \
  --events out/events.jsonl \
  --balances out/balances.csv \
  --html out/metrics.html
```

## Example Scenario

See the `examples/` directory for sample scenarios demonstrating various features.
