"""Utilities for running Kalecki ring experiment sweeps."""

from __future__ import annotations

import csv
import uuid
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import random

from bilancio.analysis.loaders import read_balances_csv, read_events_jsonl
from bilancio.analysis.report import (
    compute_day_metrics,
    summarize_day_metrics,
    write_day_metrics_csv,
    write_day_metrics_json,
    write_debtor_shares_csv,
    write_intraday_csv,
    write_metrics_html,
)
from bilancio.config.models import RingExplorerGeneratorConfig
from bilancio.scenarios.generators.ring_explorer import compile_ring_explorer
from bilancio.ui.run import run_scenario


@dataclass
class RingRunSummary:
    run_id: str
    phase: str
    kappa: Decimal
    concentration: Decimal
    mu: Decimal
    delta_total: Optional[Decimal]
    phi_total: Optional[Decimal]
    time_to_stability: int


def _decimal_list(spec: str) -> List[Decimal]:
    out: List[Decimal] = []
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        out.append(Decimal(part))
    return out


def _to_yaml_ready(obj: Any) -> Any:
    from decimal import Decimal as _D

    if isinstance(obj, dict):
        return {k: _to_yaml_ready(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_to_yaml_ready(v) for v in obj]
    if isinstance(obj, _D):
        norm = obj.normalize()
        if norm == norm.to_integral_value():
            return int(norm)
        return float(norm)
    return obj


class RingSweepRunner:
    """Coordinator for running Kalecki ring experiments."""

    REGISTRY_FIELDS = [
        "run_id",
        "phase",
        "seed",
        "n_agents",
        "kappa",
        "concentration",
        "mu",
        "maturity_days",
        "Q_total",
        "S1",
        "L0",
        "scenario_yaml",
        "events_jsonl",
        "balances_csv",
        "metrics_csv",
        "metrics_html",
        "run_html",
        "default_handling",
        "status",
        "time_to_stability",
        "phi_total",
        "delta_total",
        "error",
    ]

    def __init__(
        self,
        out_dir: Path,
        *,
        name_prefix: str,
        n_agents: int,
        maturity_days: int,
        Q_total: Decimal,
        liquidity_mode: str,
        liquidity_agent: Optional[str],
        base_seed: int,
        default_handling: str = "fail-fast",
    ) -> None:
        self.base_dir = out_dir
        self.registry_dir = self.base_dir / "registry"
        self.runs_dir = self.base_dir / "runs"
        self.aggregate_dir = self.base_dir / "aggregate"
        self.name_prefix = name_prefix
        self.n_agents = n_agents
        self.maturity_days = maturity_days
        self.Q_total = Q_total
        self.liquidity_mode = liquidity_mode
        self.liquidity_agent = liquidity_agent
        self.seed_counter = base_seed
        self.default_handling = default_handling
        self.registry_rows: List[Dict[str, Any]] = []

        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.aggregate_dir.mkdir(parents=True, exist_ok=True)

        self.registry_path = self.registry_dir / "experiments.csv"
        if self.registry_path.exists():
            with self.registry_path.open("r", newline="") as fh:
                reader = csv.DictReader(fh)
                self.registry_rows = list(reader)
        else:
            self._write_registry()

    def _next_seed(self) -> int:
        value = self.seed_counter
        self.seed_counter += 1
        return value

    def _write_registry(self) -> None:
        with self.registry_path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.REGISTRY_FIELDS)
            writer.writeheader()
            for row in self.registry_rows:
                writer.writerow({field: row.get(field, "") for field in self.REGISTRY_FIELDS})

    def _upsert_registry(self, row: Dict[str, Any]) -> None:
        for existing in self.registry_rows:
            if existing.get("run_id") == row.get("run_id"):
                existing.update(row)
                break
        else:
            self.registry_rows.append(row)
        self._write_registry()

    def run_grid(self, kappas: Sequence[Decimal], concentrations: Sequence[Decimal], mus: Sequence[Decimal]) -> List[RingRunSummary]:
        summaries: List[RingRunSummary] = []
        for kappa in kappas:
            for concentration in concentrations:
                for mu in mus:
                    seed = self._next_seed()
                    summaries.append(self._execute_run("grid", kappa, concentration, mu, seed))
        return summaries

    def run_lhs(
        self,
        count: int,
        *,
        kappa_range: Tuple[Decimal, Decimal],
        concentration_range: Tuple[Decimal, Decimal],
        mu_range: Tuple[Decimal, Decimal],
    ) -> List[RingRunSummary]:
        if count <= 0:
            return []
        rng = random.Random(self.seed_counter + 7919)
        kappas = self._lhs_axis(count, kappa_range, rng)
        concentrations = self._lhs_axis(count, concentration_range, rng)
        mus = self._lhs_axis(count, mu_range, rng)
        rng.shuffle(concentrations)
        rng.shuffle(mus)
        summaries: List[RingRunSummary] = []
        for idx in range(count):
            seed = self._next_seed()
            summaries.append(
                self._execute_run(
                    "lhs",
                    kappas[idx],
                    concentrations[idx],
                    mus[idx],
                    seed,
                )
            )
        return summaries

    def _lhs_axis(self, count: int, bounds: Tuple[Decimal, Decimal], rng: random.Random) -> List[Decimal]:
        low, high = bounds
        samples: List[Decimal] = []
        for stratum in range(count):
            a = Decimal(stratum) / Decimal(count)
            b = Decimal(stratum + 1) / Decimal(count)
            u = Decimal(str(rng.random()))
            frac = a + (b - a) * u
            samples.append(low + (high - low) * frac)
        rng.shuffle(samples)
        return samples

    def run_frontier(
        self,
        concentrations: Sequence[Decimal],
        mus: Sequence[Decimal],
        *,
        kappa_low: Decimal,
        kappa_high: Decimal,
        tolerance: Decimal,
        max_iterations: int,
    ) -> List[RingRunSummary]:
        summaries: List[RingRunSummary] = []
        for concentration in concentrations:
            for mu in mus:
                summaries.extend(
                    self._run_frontier_cell(
                        concentration,
                        mu,
                        kappa_low,
                        kappa_high,
                        tolerance,
                        max_iterations,
                    )
                )
        return summaries

    def _run_frontier_cell(
        self,
        concentration: Decimal,
        mu: Decimal,
        kappa_low: Decimal,
        kappa_high: Decimal,
        tolerance: Decimal,
        max_iterations: int,
    ) -> List[RingRunSummary]:
        runs: List[RingRunSummary] = []

        low_summary = self._execute_run("frontier", kappa_low, concentration, mu, self._next_seed(), label="low")
        runs.append(low_summary)
        if low_summary.delta_total is not None and low_summary.delta_total <= tolerance:
            return runs

        hi_kappa = kappa_high
        hi_summary = self._execute_run("frontier", hi_kappa, concentration, mu, self._next_seed(), label="high")
        runs.append(hi_summary)

        while (hi_summary.delta_total is None or hi_summary.delta_total > tolerance) and hi_kappa < kappa_high * 4:
            hi_kappa = hi_kappa * Decimal("1.5")
            hi_summary = self._execute_run("frontier", hi_kappa, concentration, mu, self._next_seed(), label="high")
            runs.append(hi_summary)
            if hi_kappa > Decimal("128"):
                break

        if hi_summary.delta_total is None or hi_summary.delta_total > tolerance:
            return runs

        low = low_summary.kappa
        high = hi_summary.kappa
        best = hi_summary

        for _ in range(max_iterations):
            if high - low <= tolerance:
                break
            mid = (low + high) / 2
            mid_summary = self._execute_run("frontier", mid, concentration, mu, self._next_seed(), label="mid")
            runs.append(mid_summary)
            delta = mid_summary.delta_total
            if delta is None:
                low = mid
                continue
            if delta <= tolerance:
                best = mid_summary
                high = mid
            else:
                low = mid

        return runs

    def _execute_run(
        self,
        phase: str,
        kappa: Decimal,
        concentration: Decimal,
        mu: Decimal,
        seed: int,
        *,
        label: Optional[str] = None,
    ) -> RingRunSummary:
        run_uuid = uuid.uuid4().hex[:12]
        run_id = f"{phase}_{label}_{run_uuid}" if label else f"{phase}_{run_uuid}"
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        out_dir = run_dir / "out"
        out_dir.mkdir(parents=True, exist_ok=True)

        scenario_path = run_dir / "scenario.yaml"
        run_html_path = run_dir / "run.html"
        balances_path = out_dir / "balances.csv"
        events_path = out_dir / "events.jsonl"
        metrics_csv_path = out_dir / "metrics.csv"
        metrics_json_path = out_dir / "metrics.json"
        ds_csv_path = out_dir / "metrics_ds.csv"
        intraday_csv_path = out_dir / "metrics_intraday.csv"
        metrics_html_path = out_dir / "metrics.html"

        registry_entry = {
            "run_id": run_id,
            "phase": phase,
            "seed": str(seed),
            "n_agents": str(self.n_agents),
            "kappa": str(kappa),
            "concentration": str(concentration),
            "mu": str(mu),
            "maturity_days": str(self.maturity_days),
            "Q_total": str(self.Q_total),
            "default_handling": self.default_handling,
            "status": "running",
        }
        self._upsert_registry(registry_entry)

        generator_data = {
            "version": 1,
            "generator": "ring_explorer_v1",
            "name_prefix": self.name_prefix,
            "params": {
                "n_agents": self.n_agents,
                "seed": seed,
                "kappa": str(kappa),
                "Q_total": str(self.Q_total),
                "inequality": {
                    "scheme": "dirichlet",
                    "concentration": str(concentration),
                },
                "maturity": {
                    "days": self.maturity_days,
                    "mode": "lead_lag",
                    "mu": str(mu),
                },
                "liquidity": {
                    "allocation": self._liquidity_allocation_dict(),
                },
            },
            "compile": {"emit_yaml": False},
        }

        generator_config = RingExplorerGeneratorConfig.model_validate(generator_data)
        scenario = compile_ring_explorer(generator_config, source_path=None)

        if self.default_handling:
            scenario_run = scenario.setdefault("run", {})
            scenario_run["default_handling"] = self.default_handling

        with scenario_path.open("w", encoding="utf-8") as fh:
            import yaml

            yaml.safe_dump(_to_yaml_ready(scenario), fh, sort_keys=False, allow_unicode=False)

        S1 = Decimal("0")
        L0 = Decimal("0")
        for action in scenario.get("initial_actions", []):
            if "create_payable" in action:
                S1 += action["create_payable"]["amount"]
            if "mint_cash" in action:
                L0 += action["mint_cash"]["amount"]

        try:
            run_scenario(
                path=scenario_path,
                mode="until_stable",
                max_days=scenario["run"].get("max_days", 90),
                quiet_days=scenario["run"].get("quiet_days", 2),
                show=scenario["run"].get("show", {}).get("events", "detailed"),
                agent_ids=scenario["run"].get("show", {}).get("balances"),
                check_invariants="daily",
                export={
                    "balances_csv": str(balances_path),
                    "events_jsonl": str(events_path),
                },
                html_output=run_html_path,
                t_account=False,
                default_handling=self.default_handling,
            )
        except Exception as exc:
            registry_entry.update({
                "status": "failed",
                "error": str(exc),
                "S1": str(S1),
                "L0": str(L0),
                "scenario_yaml": self._rel_path(scenario_path),
                "run_html": self._rel_path(run_html_path),
            })
            self._upsert_registry(registry_entry)
            return RingRunSummary(run_id, phase, kappa, concentration, mu, None, None, 0)

        events = list(read_events_jsonl(events_path))
        balances_rows = read_balances_csv(balances_path) if balances_path.exists() else None
        bundle = compute_day_metrics(events, balances_rows)

        write_day_metrics_csv(metrics_csv_path, bundle["day_metrics"])
        write_day_metrics_json(metrics_json_path, bundle["day_metrics"])
        write_debtor_shares_csv(ds_csv_path, bundle["debtor_shares"])
        write_intraday_csv(intraday_csv_path, bundle["intraday"])
        write_metrics_html(metrics_html_path, bundle["day_metrics"], bundle["debtor_shares"], bundle["intraday"])

        summary = summarize_day_metrics(bundle["day_metrics"])
        delta_total = summary.get("delta_total")
        phi_total = summary.get("phi_total")
        time_to_stability = int(summary.get("max_day") or 0)

        registry_entry.update({
            "status": "completed",
            "S1": str(S1),
            "L0": str(L0),
            "scenario_yaml": self._rel_path(scenario_path),
            "events_jsonl": self._rel_path(events_path),
            "balances_csv": self._rel_path(balances_path),
            "metrics_csv": self._rel_path(metrics_csv_path),
            "metrics_html": self._rel_path(metrics_html_path),
            "run_html": self._rel_path(run_html_path),
            "time_to_stability": str(time_to_stability),
            "phi_total": str(phi_total) if phi_total is not None else "",
            "delta_total": str(delta_total) if delta_total is not None else "",
            "error": "",
        })
        self._upsert_registry(registry_entry)

        return RingRunSummary(run_id, phase, kappa, concentration, mu, delta_total, phi_total, time_to_stability)

    def _rel_path(self, absolute: Path) -> str:
        try:
            return str(Path("..").joinpath(absolute.relative_to(self.base_dir)))
        except ValueError:
            return str(absolute)

    def _liquidity_allocation_dict(self) -> Dict[str, Any]:
        allocation: Dict[str, Any] = {"mode": self.liquidity_mode}
        if self.liquidity_mode == "single_at" and self.liquidity_agent:
            allocation["agent"] = self.liquidity_agent
        return allocation


__all__ = [
    "RingSweepRunner",
    "RingRunSummary",
    "_decimal_list",
]
