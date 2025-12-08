# Plan 023: Default-Aware Repayment Events & Strategy Analysis Scripts

**Reference**: Instructions_on_instrumentation_improvement.pdf
**Status**: Complete
**Goal**: Fix instrumentation to capture defaulted liabilities and add analysis scripts to explain dealer effectiveness

---

## Context

We have 625 simulation pairs comparing passive vs active dealer regimes. While we can see aggregate default rates, we lack liability-level insight into:

1. **Why** some runs show no difference between active/passive
2. **Which** trading strategies succeed or fail
3. **Whether** defaulted traders ever used the dealer

### Current State

**What we have:**
- `repayment_events.csv` generated per active run (Plan 022)
- `build_repayment_events()` function in `dealer/metrics.py:1199-1304`
- `comparison.csv` with run-level delta metrics in `aggregate/`

**Problem:**
The current `build_repayment_events()` only captures liabilities that appear in explicit events (`PayableSettled` or `ObligationDefaulted`). However:
- Not all defaulted liabilities emit an `ObligationDefaulted` event
- The simulation may end with unsettled liabilities that weren't explicitly recorded
- We're missing rows for liabilities that matured but were never settled

### What We Need

**Part A**: Fix `repayment_events.csv` to include ALL liabilities:
- Build a liability map from `PayableCreated` events
- Mark as settled/defaulted based on `PayableSettled` events
- Any liability that matured but wasn't settled = "defaulted"

**Part B**: Add analysis scripts that aggregate across runs:
- `build_strategy_outcomes.py` → explains strategy success/failure rates
- `build_dealer_usage_summary.py` → explains why dealers have no effect in some runs

---

## Part A: Default-Aware repayment_events.csv

### A.1 Desired Schema

One row per liability that matures during the simulation:

| Column | Type | Description |
|--------|------|-------------|
| run_id | str | Run identifier (e.g., "balanced_active_abc123") |
| regime | str | "passive" or "active" |
| trader_id | str | Debtor agent ID (e.g., "H1") |
| liability_id | str | Payable ID (e.g., "PAY_xyz789") |
| maturity_day | int | Due day of the liability |
| face_value | Decimal | Amount owed |
| outcome | str | "repaid" or "defaulted" |
| buy_count | int | Number of BUY trades by trader before maturity |
| sell_count | int | Number of SELL trades by trader before maturity |
| net_cash_pnl | Decimal | Net cash from trading (sells - buys) |
| strategy | str | "no_trade", "hold_to_maturity", "sell_before", "round_trip" |

### A.2 Implementation

#### A.2.1 New Function: `build_liability_map()`

Location: `src/bilancio/dealer/metrics.py`

```python
@dataclass
class LiabilityInfo:
    """Information about a single liability from events.jsonl."""
    trader_id: str
    liability_id: str
    maturity_day: int
    face_value: Decimal
    settled: bool = False
    settled_day: int | None = None


def build_liability_map(events: List[Dict[str, Any]]) -> tuple[dict[str, LiabilityInfo], int]:
    """
    Build a map of all liabilities and their settlement status.

    Scans events for:
    - PayableCreated: Register liability with debtor, maturity, face value
    - PayableSettled: Mark liability as settled

    Args:
        events: List of event dictionaries from system.state.events or events.jsonl

    Returns:
        (liabilities_map, final_day) where:
        - liabilities_map: {liability_id -> LiabilityInfo}
        - final_day: Last day seen in events
    """
    liabilities: dict[str, LiabilityInfo] = {}
    final_day = 0

    for event in events:
        day = event.get("day", 0)
        final_day = max(final_day, day)
        kind = event.get("kind", "")

        if kind == "PayableCreated":
            lid = event.get("payable_id", "")
            liabilities[lid] = LiabilityInfo(
                trader_id=event.get("debtor", ""),
                liability_id=lid,
                maturity_day=event.get("due_day", 0),
                face_value=Decimal(str(event.get("amount", 0))),
            )
        elif kind == "PayableSettled":
            lid = event.get("pid") or event.get("contract_id", "")
            if lid in liabilities:
                liabilities[lid].settled = True
                liabilities[lid].settled_day = day

    return liabilities, final_day
```

#### A.2.2 Refactor `build_repayment_events()`

Replace the current event-scanning approach with liability-map based approach:

```python
def build_repayment_events(
    event_log: List[Dict[str, Any]],
    trades: List[TradeRecord],
    run_id: str = "",
    regime: str = "",
) -> List[RepaymentEvent]:
    """
    Build RepaymentEvent objects for ALL liabilities that matured.

    Uses liability map approach:
    1. Build map of all PayableCreated liabilities
    2. Mark settled liabilities from PayableSettled events
    3. For each liability that matured by final_day:
       - Compute trading stats from trades
       - Classify strategy
       - Set outcome based on settled status

    This captures BOTH repaid and defaulted liabilities.
    """
    # Build liability map
    liabilities, final_day = build_liability_map(event_log)

    # Build trading stats by trader
    trading_stats = compute_trading_stats_by_trader(trades)

    repayment_events: List[RepaymentEvent] = []

    for lid, info in liabilities.items():
        # Only include liabilities that have matured
        if info.maturity_day > final_day:
            continue

        # Get trading stats for this trader BEFORE this maturity
        trader_stats = get_trades_before_day(
            trading_stats.get(info.trader_id, []),
            info.maturity_day
        )

        buy_count = trader_stats.get("buy_count", 0)
        sell_count = trader_stats.get("sell_count", 0)
        net_cash_pnl = trader_stats.get("net_cash_pnl", Decimal(0))

        # Classify strategy
        strategy = classify_trading_strategy(buy_count, sell_count)

        # Determine outcome
        outcome = "repaid" if info.settled else "defaulted"

        repayment_events.append(RepaymentEvent(
            run_id=run_id,
            regime=regime,
            trader_id=info.trader_id,
            liability_id=lid,
            maturity_day=info.maturity_day,
            face_value=info.face_value,
            outcome=outcome,
            buy_count=buy_count,
            sell_count=sell_count,
            net_cash_pnl=net_cash_pnl,
            strategy=strategy,
        ))

    return repayment_events
```

#### A.2.3 New Helper: `compute_trading_stats_by_trader()`

```python
def compute_trading_stats_by_trader(
    trades: List[TradeRecord]
) -> Dict[str, List[Dict]]:
    """
    Group trades by trader_id with trade details.

    Returns:
        {trader_id: [{"day": d, "side": s, "price": p}, ...]}
    """
    by_trader: Dict[str, List[Dict]] = {}

    for trade in trades:
        trader_id = trade.trader_id
        if trader_id not in by_trader:
            by_trader[trader_id] = []
        by_trader[trader_id].append({
            "day": trade.day,
            "side": trade.side,
            "price": trade.price,
        })

    return by_trader


def get_trades_before_day(
    trader_trades: List[Dict],
    maturity_day: int
) -> Dict:
    """
    Compute trading stats for trades BEFORE a given maturity day.

    Returns:
        {"buy_count": N, "sell_count": N, "net_cash_pnl": Decimal}
    """
    buy_count = 0
    sell_count = 0
    net_cash_pnl = Decimal(0)

    for t in trader_trades:
        if t["day"] < maturity_day:
            if t["side"] == "BUY":
                buy_count += 1
                net_cash_pnl -= Decimal(str(t["price"]))
            elif t["side"] == "SELL":
                sell_count += 1
                net_cash_pnl += Decimal(str(t["price"]))

    return {
        "buy_count": buy_count,
        "sell_count": sell_count,
        "net_cash_pnl": net_cash_pnl,
    }
```

### A.3 Apply to Passive Runs

For passive runs:
- `trades.csv` will be absent or empty
- All trading stats will be zeros
- All strategies will be "no_trade"
- Still emit `repayment_events.csv` for comparison

This makes active vs passive comparisons symmetric.

### A.4 Testing

1. **Run with known defaults** (e.g., delta_active > 0):
   - Verify `repayment_events.csv` contains both "repaid" and "defaulted" outcomes
   - Check that sum of defaulted face values matches metrics

2. **Run with no defaults** (delta_active = 0):
   - Verify all rows have outcome = "repaid"

3. **Spot-check strategies**: Verify "no_trade" liabilities show buy_count=sell_count=0

---

## Part B: Cross-Run Analysis Scripts

These scripts operate on experiment output files to answer key questions.

### B.1 Script: `build_strategy_outcomes.py`

**Location**: `src/bilancio/analysis/strategy_outcomes.py`

**Purpose**: For each run, summarize how many liabilities used each strategy, and how often those liabilities defaulted.

#### B.1.1 Output: `strategy_outcomes_by_run.csv`

One row per run with:

| Column | Description |
|--------|-------------|
| run_id | Run identifier |
| kappa, concentration, mu, outside_mid_ratio | Parameters |
| seed, face_value | Run config |
| delta_passive, delta_active, trading_effect | From comparison.csv |
| total_liabilities | Count of liabilities in run |
| total_face_value | Sum of all face values |
| default_face_total | Sum of defaulted face values |
| default_rate_total | default_face_total / total_face_value |
| count_{strategy} | Count of liabilities using strategy |
| face_{strategy} | Face value sum for strategy |
| default_count_{strategy} | Defaulted count for strategy |
| default_face_{strategy} | Defaulted face value for strategy |
| default_rate_{strategy} | default_face / face for strategy |

Where `{strategy}` ∈ {no_trade, hold_to_maturity, sell_before, round_trip}

#### B.1.2 Output: `strategy_outcomes_overall.csv`

Aggregate across runs, one row per (kappa, concentration, mu, outside_mid_ratio, strategy):

| Column | Description |
|--------|-------------|
| strategy | Strategy name |
| kappa, concentration, mu, outside_mid_ratio | Parameters |
| total_face | Sum of face values across runs |
| default_face | Sum of defaulted face values |
| default_rate | default_face / total_face |
| runs_using_strategy | Count of runs where strategy was used |
| mean_trading_effect | Mean trading effect for these runs |

#### B.1.3 Implementation Sketch

```python
def build_strategy_outcomes_by_run(experiment_root: Path) -> pd.DataFrame:
    """Build strategy outcomes for each run."""
    comp = pd.read_csv(experiment_root / "aggregate" / "comparison.csv")
    rows = []

    for _, row in comp.iterrows():
        run_id = row["active_run_id"]
        run_dir = experiment_root / "active" / "runs" / run_id
        rep_path = run_dir / "out" / "repayment_events.csv"

        if not rep_path.exists():
            continue

        rep = pd.read_csv(rep_path)

        # Compute strategy metrics
        total_face = rep["face_value"].sum()
        total_liab = len(rep)
        default_face_total = rep.loc[rep["outcome"] == "defaulted", "face_value"].sum()

        strat_metrics = {}
        for strat in ["no_trade", "hold_to_maturity", "sell_before", "round_trip"]:
            strat_rows = rep[rep["strategy"] == strat]
            face_strat = strat_rows["face_value"].sum()
            default_rows = strat_rows[strat_rows["outcome"] == "defaulted"]

            strat_metrics[f"count_{strat}"] = len(strat_rows)
            strat_metrics[f"face_{strat}"] = face_strat
            strat_metrics[f"default_count_{strat}"] = len(default_rows)
            strat_metrics[f"default_face_{strat}"] = default_rows["face_value"].sum()
            strat_metrics[f"default_rate_{strat}"] = (
                default_rows["face_value"].sum() / face_strat if face_strat > 0 else 0
            )

        row_out = {
            "run_id": run_id,
            "kappa": row["kappa"],
            "concentration": row["concentration"],
            "mu": row["mu"],
            "outside_mid_ratio": row["outside_mid_ratio"],
            "seed": row["seed"],
            "face_value": row["face_value"],
            "delta_passive": row["delta_passive"],
            "delta_active": row["delta_active"],
            "trading_effect": row["trading_effect"],
            "trading_relief_ratio": row["trading_relief_ratio"],
            "total_liabilities": total_liab,
            "total_face_value": total_face,
            "default_face_total": default_face_total,
            "default_rate_total": default_face_total / total_face if total_face > 0 else 0,
            **strat_metrics,
        }
        rows.append(row_out)

    return pd.DataFrame(rows)
```

### B.2 Script: `build_dealer_usage_summary.py`

**Location**: `src/bilancio/analysis/dealer_usage_summary.py`

**Purpose**: Explain why so many runs show no effect from the dealer.

#### B.2.1 Output: `dealer_usage_by_run.csv`

Metrics per run from multiple sources:

**From trades.csv:**
| Column | Description |
|--------|-------------|
| dealer_trade_count | Total number of trades |
| trader_dealer_trade_count | Trades where H-entity participated |
| n_traders_using_dealer | Distinct traders who traded |
| total_face_traded | Total face value traded by traders |
| total_cash_volume | Total cash volume traded |

**From inventory_timeseries.csv:**
| Column | Description |
|--------|-------------|
| dealer_active_fraction | Fraction of days with positive inventory |
| dealer_empty_fraction | Fraction of days with all-zero inventory |
| vbt_usage_fraction | Fraction of days with VBT routing |

**From system_state_timeseries.csv:**
| Column | Description |
|--------|-------------|
| mean_debt_to_money | Mean debt/money ratio over run |
| final_debt_to_money | Final debt/money ratio |
| debt_shrink_rate | (initial - final) / initial face value |

**From repayment_events.csv (optional):**
| Column | Description |
|--------|-------------|
| frac_defaulted_that_traded | Share of defaulted face where trader used dealer |
| frac_repaid_that_traded | Share of repaid face where trader used dealer |

#### B.2.2 Implementation Sketch

```python
def build_dealer_usage_summary(experiment_root: Path) -> pd.DataFrame:
    """Build dealer usage summary for each run."""
    comp = pd.read_csv(experiment_root / "aggregate" / "comparison.csv")
    rows = []

    for _, row in comp.iterrows():
        run_id = row["active_run_id"]
        run_dir = experiment_root / "active" / "runs" / run_id
        out_dir = run_dir / "out"

        # Load files
        trades = pd.read_csv(out_dir / "trades.csv")
        inv = pd.read_csv(out_dir / "inventory_timeseries.csv")
        sys_ts = pd.read_csv(out_dir / "system_state_timeseries.csv")

        # Trade metrics
        dealer_trade_count = len(trades)
        trader_trades = trades[trades["trader_id"].str.startswith("H")]
        trader_dealer_trade_count = len(trader_trades)
        n_traders_using_dealer = trader_trades["trader_id"].nunique()
        total_face_traded = trader_trades["face_value"].sum()
        total_cash_volume = trader_trades["price"].sum()

        # Inventory metrics (aggregate by day)
        inv_by_day = inv.groupby("day").agg(
            any_positive=("dealer_inventory", lambda x: (x > 0).any()),
            any_zero=("is_at_zero", lambda x: x.all()),
            any_vbt=("hit_vbt_this_step", lambda x: x.any()),
        )
        dealer_active_fraction = inv_by_day["any_positive"].mean()
        dealer_empty_fraction = inv_by_day["any_zero"].mean()
        vbt_usage_fraction = inv_by_day["any_vbt"].mean()

        # System state metrics
        mean_debt_to_money = sys_ts["debt_to_money"].mean()
        final_debt_to_money = sys_ts["debt_to_money"].iloc[-1]
        total_face0 = sys_ts["total_face_value"].iloc[0]
        total_faceT = sys_ts["total_face_value"].iloc[-1]
        debt_shrink_rate = (total_face0 - total_faceT) / total_face0 if total_face0 > 0 else 0

        # Repayment events metrics (optional)
        rep_path = out_dir / "repayment_events.csv"
        frac_defaulted_that_traded = None
        frac_repaid_that_traded = None

        if rep_path.exists():
            rep = pd.read_csv(rep_path)
            rep["used_dealer"] = (rep["buy_count"] + rep["sell_count"]) > 0

            def frac_used(outcome):
                sub = rep[rep["outcome"] == outcome]
                if sub.empty:
                    return 0.0
                return sub.loc[sub["used_dealer"], "face_value"].sum() / sub["face_value"].sum()

            frac_defaulted_that_traded = frac_used("defaulted")
            frac_repaid_that_traded = frac_used("repaid")

        rows.append({
            "run_id": run_id,
            "kappa": row["kappa"],
            "concentration": row["concentration"],
            "mu": row["mu"],
            "outside_mid_ratio": row["outside_mid_ratio"],
            "delta_passive": row["delta_passive"],
            "delta_active": row["delta_active"],
            "trading_effect": row["trading_effect"],
            "trading_relief_ratio": row["trading_relief_ratio"],
            "dealer_trade_count": dealer_trade_count,
            "trader_dealer_trade_count": trader_dealer_trade_count,
            "n_traders_using_dealer": n_traders_using_dealer,
            "total_face_traded": total_face_traded,
            "total_cash_volume": total_cash_volume,
            "dealer_active_fraction": dealer_active_fraction,
            "dealer_empty_fraction": dealer_empty_fraction,
            "vbt_usage_fraction": vbt_usage_fraction,
            "mean_debt_to_money": mean_debt_to_money,
            "final_debt_to_money": final_debt_to_money,
            "debt_shrink_rate": debt_shrink_rate,
            "frac_defaulted_that_traded": frac_defaulted_that_traded,
            "frac_repaid_that_traded": frac_repaid_that_traded,
        })

    return pd.DataFrame(rows)
```

---

## CLI Integration

Add CLI commands to run the analysis scripts.

### Option 1: Standalone Python Script

```bash
uv run python -m bilancio.analysis.strategy_outcomes --experiment out/experiments/my_sweep
uv run python -m bilancio.analysis.dealer_usage_summary --experiment out/experiments/my_sweep
```

### Option 2: CLI Subcommand (preferred)

```bash
bilancio analyze strategy-outcomes --experiment out/experiments/my_sweep
bilancio analyze dealer-usage --experiment out/experiments/my_sweep
```

---

## Implementation Order

| Phase | Task | Complexity | Files Modified |
|-------|------|------------|----------------|
| A.1 | Add `LiabilityInfo` dataclass | Low | `dealer/metrics.py` |
| A.2 | Add `build_liability_map()` function | Medium | `dealer/metrics.py` |
| A.3 | Refactor `build_repayment_events()` | Medium | `dealer/metrics.py` |
| A.4 | Add helper functions | Low | `dealer/metrics.py` |
| A.5 | Update passive run handling | Low | `experiments/balanced_comparison.py` |
| A.6 | Test with known defaults | Medium | Manual testing |
| B.1 | Create `strategy_outcomes.py` | Medium | New file in `analysis/` |
| B.2 | Create `dealer_usage_summary.py` | Medium | New file in `analysis/` |
| B.3 | Add CLI commands | Low | `ui/cli.py` |
| B.4 | Integration test | Medium | Test with real sweep |

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/bilancio/dealer/metrics.py` | Add `LiabilityInfo`, refactor `build_repayment_events()`, add helpers |
| `src/bilancio/experiments/balanced_comparison.py` | Ensure passive runs also generate repayment_events.csv |
| `src/bilancio/analysis/strategy_outcomes.py` | **NEW** - Strategy analysis script |
| `src/bilancio/analysis/dealer_usage_summary.py` | **NEW** - Dealer usage analysis script |
| `src/bilancio/ui/cli.py` | Add `analyze` subcommands |

---

## Success Criteria

1. `repayment_events.csv` contains rows for ALL matured liabilities (repaid + defaulted)
2. Running analysis on a sweep with defaults produces:
   - `strategy_outcomes_by_run.csv` with per-strategy default rates
   - `strategy_outcomes_overall.csv` with aggregate statistics
   - `dealer_usage_by_run.csv` with trading activity metrics
3. Can answer: "Why do some runs show no dealer effect?"
   - If `frac_defaulted_that_traded` is low → traders who defaulted never used the dealer
   - If `dealer_empty_fraction` is high → dealer ran out of inventory
   - If `n_traders_using_dealer` is low → dealer not used at all

---

## Analysis Questions Enabled

Once implemented, we can answer:

1. **Strategy effectiveness**: Which strategies (hold_to_maturity, sell_before, round_trip) have lowest default rates?
2. **Dealer utilization**: In "no effect" runs, did traders actually use the dealer?
3. **Capacity constraints**: Did dealers run out of inventory when traders needed them?
4. **Parameter sensitivity**: Which parameter regions see most dealer usage?
5. **Rescue events**: What fraction of defaulted debt was from traders who tried to trade but still defaulted?
