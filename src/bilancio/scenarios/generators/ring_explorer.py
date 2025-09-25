"""Ring explorer scenario generator."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from bilancio.config.models import (
    RingExplorerGeneratorConfig,
    RingExplorerParamsModel,
)

# Ensure ample precision for Decimal arithmetic when scaling Dirichlet weights
getcontext().prec = 28


@dataclass
class LiquiditySpec:
    total: Decimal
    mode: str
    agent: Optional[str]
    vector: Optional[List[Decimal]]


@dataclass
class InequalitySpec:
    concentration: Decimal


@dataclass
class MaturitySpec:
    days: int
    mode: str
    mu: Decimal


@dataclass
class RingExplorerParams:
    n_agents: int
    seed: int
    kappa: Decimal
    Q_total: Decimal
    liquidity: LiquiditySpec
    inequality: InequalitySpec
    maturity: MaturitySpec
    currency: str
    policy_overrides: Optional[Dict[str, Any]]

    @classmethod
    def from_model(cls, model: RingExplorerParamsModel) -> "RingExplorerParams":
        Q_total = model.Q_total
        liquidity_total = model.liquidity.total

        if Q_total is None and liquidity_total is None:
            raise ValueError("Either params.Q_total or params.liquidity.total must be provided")

        if liquidity_total is None and Q_total is not None:
            liquidity_total = (Q_total / model.kappa)
        elif Q_total is None and liquidity_total is not None:
            Q_total = (model.kappa * liquidity_total)

        if Q_total is None or liquidity_total is None:
            raise ValueError("Failed to resolve Q_total and liquidity total from parameters")

        if liquidity_total <= 0 or Q_total <= 0:
            raise ValueError("Derived Q_total and liquidity must be positive")

        liquidity_spec = LiquiditySpec(
            total=liquidity_total,
            mode=model.liquidity.allocation.mode,
            agent=model.liquidity.allocation.agent,
            vector=[Decimal(str(v)) for v in (model.liquidity.allocation.vector or [])] or None,
        )
        inequality_spec = InequalitySpec(concentration=model.inequality.concentration)
        maturity_spec = MaturitySpec(
            days=model.maturity.days,
            mode=model.maturity.mode,
            mu=model.maturity.mu,
        )

        policy_overrides = None
        if model.policy_overrides is not None:
            policy_overrides = model.policy_overrides.model_dump(exclude_none=True)

        return cls(
            n_agents=model.n_agents,
            seed=model.seed,
            kappa=model.kappa,
            Q_total=Q_total,
            liquidity=liquidity_spec,
            inequality=inequality_spec,
            maturity=maturity_spec,
            currency=model.currency,
            policy_overrides=policy_overrides,
        )


def compile_ring_explorer(
    config: RingExplorerGeneratorConfig,
    *,
    source_path: Optional[Path] = None,
) -> Dict[str, Any]:
    params = RingExplorerParams.from_model(config.params)

    payable_amounts = _draw_payables(params.n_agents, params.inequality.concentration, params.Q_total, params.seed)
    liquidity_amounts = _allocate_liquidity(params)
    due_days = _build_due_days(params.n_agents, params.maturity.days, params.maturity.mu)

    agents = _build_agents(params.n_agents)
    initial_actions = []

    # Seed cash liquidity per allocation plan
    for idx, amount in enumerate(liquidity_amounts):
        if amount <= 0:
            continue
        agent_id = f"H{idx + 1}"
        initial_actions.append({
            "mint_cash": {
                "to": agent_id,
                "amount": amount,
                "alias": f"LIQ_{agent_id}",
            }
        })

    # Create ring payables
    for idx, amount in enumerate(payable_amounts):
        from_agent = f"H{idx + 1}"
        to_agent = f"H{(idx + 1) % params.n_agents + 1}"
        due_day = due_days[idx]
        initial_actions.append({
            "create_payable": {
                "from": from_agent,
                "to": to_agent,
                "amount": amount,
                "due_day": due_day,
                "alias": f"P_{from_agent}_{to_agent}",
            }
        })

    scenario_name = _render_scenario_name(config.name_prefix, params)
    description = _render_description(params)

    scenario: Dict[str, Any] = {
        "version": 1,
        "name": scenario_name,
        "description": description,
        "policy_overrides": params.policy_overrides,
        "agents": agents,
        "initial_actions": initial_actions,
        "scheduled_actions": [],
        "run": {
            "mode": "until_stable",
            "max_days": max(30, params.maturity.days + 5),
            "quiet_days": 2,
            "show": {
                "balances": [agent["id"] for agent in agents if agent["id"].startswith("H")],
                "events": "detailed",
            },
            "export": {
                "balances_csv": "out/balances.csv",
                "events_jsonl": "out/events.jsonl",
            },
        },
    }

    if config.compile.emit_yaml:
        _emit_yaml(
            scenario,
            config,
            source_path=source_path,
        )

    return scenario


def _draw_payables(n: int, concentration: Decimal, total: Decimal, seed: int) -> List[Decimal]:
    rng = random.Random(seed)
    alpha = float(concentration)
    if alpha <= 0:
        raise ValueError("Dirichlet concentration must be positive")

    weights = [rng.gammavariate(alpha, 1.0) for _ in range(n)]
    weight_sum = sum(weights)
    if weight_sum <= 0:
        raise ValueError("Failed to draw positive Dirichlet weights")

    decimals = [Decimal(str(w)) for w in weights]
    weight_total = sum(decimals)

    amounts: List[Decimal] = []
    running = Decimal("0")
    for idx, weight in enumerate(decimals):
        if idx == n - 1:
            amount = total - running
        else:
            amount = (total * weight) / weight_total
            running += amount
        amounts.append(amount)
    return amounts


def _allocate_liquidity(params: RingExplorerParams) -> List[Decimal]:
    total = params.liquidity.total
    n = params.n_agents
    mode = params.liquidity.mode

    if mode == "uniform":
        share = total / Decimal(n)
        return [share] * n
    if mode == "single_at":
        target = params.liquidity.agent or "H1"
        values = []
        for idx in range(n):
            agent_id = f"H{idx + 1}"
            values.append(total if agent_id == target else Decimal("0"))
        if all(v == 0 for v in values):
            raise ValueError(f"liquidity allocation agent '{target}' not in ring")
        return values
    if mode == "vector":
        vector = params.liquidity.vector
        if not vector or len(vector) != n:
            raise ValueError("liquidity.vector must have length equal to n_agents")
        weight_total = sum(vector)
        if weight_total <= 0:
            raise ValueError("liquidity.vector must sum to a positive value")
        scaled: List[Decimal] = []
        running = Decimal("0")
        for idx, weight in enumerate(vector):
            if idx == n - 1:
                amount = total - running
            else:
                amount = (total * weight) / weight_total
                running += amount
            scaled.append(amount)
        return scaled

    raise ValueError(f"Unsupported liquidity allocation mode '{mode}'")


def _build_due_days(n: int, days: int, mu: Decimal) -> List[int]:
    if days <= 1:
        return [1] * n
    max_shift = days - 1
    lead_steps = int(round(float(mu) * max_shift))
    lead_steps = max(0, min(max_shift, lead_steps))
    if lead_steps == 0:
        return [1] * n
    cycle = max_shift + 1
    step = max(lead_steps, 1)
    due_days: List[int] = []
    for idx in range(n):
        phase = (idx * step) % cycle
        offset = (cycle + phase - lead_steps) % cycle
        due_days.append(int(offset + 1))
    return due_days


def _build_agents(n: int) -> List[Dict[str, Any]]:
    agents: List[Dict[str, Any]] = [
        {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
    ]
    agents.extend({
        "id": f"H{idx}",
        "kind": "household",
        "name": f"Agent {idx}",
    } for idx in range(1, n + 1))
    return agents


def _render_scenario_name(prefix: str, params: RingExplorerParams) -> str:
    kappa_str = _fmt_decimal(params.kappa)
    conc_str = _fmt_decimal(params.inequality.concentration)
    mu_str = _fmt_decimal(params.maturity.mu)
    return f"{prefix} (n={params.n_agents}, kappa={kappa_str}, c={conc_str}, mu={mu_str})"


def _render_description(params: RingExplorerParams) -> str:
    parts = [
        f"Ring of {params.n_agents} agents with total dues S1={_fmt_decimal(params.Q_total)}",
        f"initial liquidity L0={_fmt_decimal(params.liquidity.total)} (kappa={_fmt_decimal(params.kappa)})",
        f"Dirichlet concentration c={_fmt_decimal(params.inequality.concentration)}",
        f"maturity mu={_fmt_decimal(params.maturity.mu)} over {params.maturity.days} day horizon",
    ]
    return "; ".join(parts)


def _fmt_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral_value():
        return str(int(normalized))
    return format(normalized, "f").rstrip("0").rstrip(".")


def _emit_yaml(scenario: Dict[str, Any], config: RingExplorerGeneratorConfig, source_path: Optional[Path]) -> None:
    base_dir = None
    if config.compile.out_dir:
        out_dir = Path(config.compile.out_dir)
        if not out_dir.is_absolute() and source_path is not None:
            base_dir = source_path.parent / out_dir
        else:
            base_dir = out_dir
    elif source_path is not None:
        base_dir = source_path.parent
    else:
        return

    base_dir.mkdir(parents=True, exist_ok=True)

    slug = _slugify(scenario.get("name", "scenario"))
    target = base_dir / f"{slug}.yaml"

    dumpable = _to_yaml_ready(scenario)
    with target.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(dumpable, fh, sort_keys=False, allow_unicode=False)


def _slugify(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", name)
    slug = slug.strip("_")
    return slug.lower() or "scenario"


def _to_yaml_ready(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _to_yaml_ready(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_to_yaml_ready(v) for v in obj]
    if isinstance(obj, Decimal):
        normalized = obj.normalize()
        if normalized == normalized.to_integral_value():
            return int(normalized)
        return float(normalized)
    return obj


__all__ = ["compile_ring_explorer"]
