# CLI Reference

Bilancio provides a command-line interface for running simulations and analyzing results.

## Commands

### `run`

Execute a scenario YAML file.

```bash
uv run bilancio run <scenario.yaml> [OPTIONS]
```

**Options:**

- `--mode step|until-stable`: Interactive step-by-step or auto until quiet days
- `--max-days N`: Cap simulation days
- `--quiet-days N`: Required consecutive quiet days for stability
- `--check-invariants setup|daily|none`: When to check invariants
- `--agents CB,B1,...`: Select agents to display in the UI
- `--export-balances PATH`: Override balances export path
- `--export-events PATH`: Override events export path
- `--html PATH`: Save an HTML simulation report

### `validate`

Check a scenario file without running it.

```bash
uv run bilancio validate <scenario.yaml>
```

### `new`

Create a new scenario from a template (interactive).

```bash
uv run bilancio new
```

### `analyze`

Compute day-level metrics and optional intraday diagnostics.

```bash
uv run bilancio analyze [OPTIONS]
```

**Options:**

- `--events PATH`: Events JSONL file (required)
- `--balances PATH`: Balances CSV file (optional)
- `--days 1,2-4`: Days to analyze
- `--out-csv PATH`: Day-level metrics CSV output
- `--out-json PATH`: Day-level metrics JSON output
- `--intraday-csv PATH`: Intraday diagnostics output
- `--html PATH`: Self-contained analytics HTML report

## Analytics Metrics

The analyze command computes the following metrics:

| Metric | Description |
|--------|-------------|
| `S_t` | Total dues maturing on day t |
| `Mbar_t` | Minimum net liquidity |
| `M_t` | Start-of-day money |
| `G_t` | Liquidity gap |
| `alpha_t` | Netting potential |
| `phi_t` | On-time settlement ratio |
| `delta_t` | Default rate (1 - phi_t) |
