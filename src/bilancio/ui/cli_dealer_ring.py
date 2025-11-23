"""CLI entry for dealer-ring scenarios (config-driven, alpha)."""

from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console

from bilancio.engines.system import System
from bilancio.config.apply import create_agent, apply_action
from bilancio.config.models import AgentSpec
from bilancio.modules.dealer_ring import (
    ticketize_payables,
    allocate_tickets,
    seed_dealer_vbt_cash,
    DealerBucket,
    VBTBucket,
    TicketOps,
    run_period,
    default_eligibility,
)

console = Console()


def _load_dealer_ring_config(path: Path) -> dict:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Dealer-ring config must be a mapping")
    return data


def _expand_agents(config: dict) -> list[dict]:
    agents = []
    for entry in config.get("agents", []):
        if "count" in entry and entry.get("id_prefix"):
            count = int(entry["count"])
            prefix = entry["id_prefix"]
            name_prefix = entry.get("name_prefix", prefix)
            kind = entry["kind"]
            for i in range(1, count + 1):
                agents.append({"id": f"{prefix}{i}", "kind": kind, "name": f"{name_prefix}{i}"})
        else:
            agents.append(entry)
    return agents


def _expand_initial_actions(config: dict) -> list[dict]:
    actions = []
    for act in config.get("initial_actions", []):
        if "create_ring_payables" in act:
            params = act["create_ring_payables"]
            count = int(params["count"])
            amount = params["amount"]
            due_day = params["due_day"]
            from_prefix = params.get("from_prefix", "T")
            to_prefix = params.get("to_prefix", "T")
            for i in range(1, count):
                actions.append({"create_payable": {"from": f"{from_prefix}{i}", "to": f"{to_prefix}{i+1}", "amount": amount, "due_day": due_day}})
            actions.append({"create_payable": {"from": f"{from_prefix}{count}", "to": f"{to_prefix}1", "amount": amount, "due_day": due_day}})
        else:
            actions.append(act)
    return actions


def _validate_ids_exist(required_ids, agents_map):
    missing = [aid for aid in required_ids if aid not in agents_map]
    if missing:
        raise ValueError(f"Missing agents: {missing}")


def _validate_counts(system: System, trader_min: int = 100, dealers_expected: int = 3, vbts_expected: int = 3):
    dealers = [a.id for a in system.state.agents.values() if a.kind == "dealer"]
    vbts = [a.id for a in system.state.agents.values() if a.kind == "vbt"]
    traders = [a.id for a in system.state.agents.values() if a.kind == "household"]
    if len(dealers) != dealers_expected:
        raise ValueError(f"Expected {dealers_expected} dealers, found {len(dealers)}: {dealers}")
    if len(vbts) != vbts_expected:
        raise ValueError(f"Expected {vbts_expected} VBTs, found {len(vbts)}: {vbts}")
    if len(traders) < trader_min:
        raise ValueError(f"Expected at least {trader_min} traders, found {len(traders)}")


def _validate_buckets(buckets_cfg: list, dealer_ids: list, vbt_ids: list):
    if len(buckets_cfg) != len(dealer_ids) or len(buckets_cfg) != len(vbt_ids):
        raise ValueError("Buckets, dealers, and VBTs must have the same length")
    names = [b["name"] for b in buckets_cfg]
    if len(set(names)) != len(names):
        raise ValueError("Bucket names must be unique")


@click.command()
@click.argument('config_file', type=click.Path(exists=True, path_type=Path))
@click.option('--days', type=int, default=5, help='Number of periods to run')
def cli(config_file: Path, days: int):
    """Run a dealer-ring scenario using a config file.

    Config schema (YAML):
      base_scenario: path to base YAML (agents, payables)
      ticket_size: int
      buckets:
        - name: Short
          tau_range: [1,3]
          M0: 1.0
          O0: 0.20
          phi_M: 1.0
          phi_O: 0.6
          guard_M_min: 0.0
          clip_nonneg_bid: true
          Xstar_target: 4
      dealers: [D_short, D_mid, D_long]
      vbts:    [V_short, V_mid, V_long]
      shares: {dealer: 0.25, vbt: 0.5}
      flow: {pi_sell: 0.5, N_max: 3, invest_horizon: 3, cash_buffer: 1}
    """
    cfg = _load_dealer_ring_config(config_file)
    ticket_size = int(cfg.get("ticket_size", 1))
    buckets_cfg = cfg["buckets"]
    dealer_ids = cfg["dealers"]
    vbt_ids = cfg["vbts"]
    _validate_buckets(buckets_cfg, dealer_ids, vbt_ids)
    shares = cfg.get("shares", {})
    dealer_share = float(shares.get("dealer", 0.25))
    vbt_share = float(shares.get("vbt", 0.5))
    flow = cfg.get("flow", {})
    pi_sell = float(flow.get("pi_sell", 0.5))
    N_max = int(flow.get("N_max", 3))
    invest_horizon = int(flow.get("invest_horizon", 3))
    cash_buffer = int(flow.get("cash_buffer", 1))

    system = System()

    # Expand dealer-ring agents/actions and apply
    expanded_agents = _expand_agents(cfg)
    for agent_spec in expanded_agents:
        spec = AgentSpec(**agent_spec)
        agent_obj = create_agent(spec)
        system.add_agent(agent_obj)

    expanded_actions = _expand_initial_actions(cfg)
    agents_map = system.state.agents
    for act in expanded_actions:
        apply_action(system, act, agents_map)

    # Validate required ids present
    _validate_ids_exist(dealer_ids + vbt_ids, system.state.agents)
    _validate_counts(system)

    # Build bucket_ranges and dealer/VBT objects
    bucket_ranges = []
    buckets = {}
    vbts = {}
    for i, b in enumerate(buckets_cfg):
        name = b["name"]
        tau_range = b["tau_range"]
        lo = int(tau_range[0])
        hi = int(tau_range[1]) if len(tau_range) > 1 and tau_range[1] is not None else None
        bucket_ranges.append((name, lo, hi))
        dealer_id = dealer_ids[i]
        vbt_id = vbt_ids[i]
        buckets[name] = DealerBucket(
            bucket=name,
            ticket_size=ticket_size,
            mid=float(b["M0"]),
            spread=float(b["O0"]),
            cash=0.0,
            inventory=0.0,
            guard_m_min=float(b.get("guard_M_min", 0.0)),
            vbt=None,
            dealer_id=dealer_id,
            vbt_id=vbt_id,
        )
        vbts[name] = VBTBucket(
            bucket=name,
            ticket_size=ticket_size,
            mid=float(b["M0"]),
            spread=float(b["O0"]),
            phi_M=float(b.get("phi_M", 1.0)),
            phi_O=float(b.get("phi_O", 0.6)),
            guard_M_min=float(b.get("guard_M_min", 0.0)),
            clip_nonneg_bid=bool(b.get("clip_nonneg_bid", True)),
        )

    ticket_ops = TicketOps(system)

    # Ticketize payables
    ticketize_payables(system, bucket_ranges=bucket_ranges, ticket_size=ticket_size, remove_payables=False)

    # Seed cash/inventory mid-shelf per bucket
    for name, dealer in buckets.items():
        seed_dealer_vbt_cash(system, dealer_id=dealer.dealer_id, vbt_id=vbts[name].bucket, mid=dealer.mid, X_target=buckets_cfg[[b["name"] for b in buckets_cfg].index(name)].get("Xstar_target", 4), ticket_size=ticket_size)

    # Allocate tickets to dealer/VBT shares
    for name in buckets.keys():
        allocate_tickets(system, bucket_id=name, dealer_id=buckets[name].dealer_id, vbt_id=vbts[name].bucket, dealer_share=dealer_share, vbt_share=vbt_share)

    # Run periods
    for _ in range(days):
        run_period(
            system=system,
            buckets=buckets,
            vbts=vbts,
            ticket_ops=ticket_ops,
            pi_sell=pi_sell,
            N_max=N_max,
            eligible_fn=lambda sys: default_eligibility(sys, cash_buffer=cash_buffer, horizon=invest_horizon),
            bucket_selector=None,
            ticket_size=ticket_size,
            bucket_ranges=bucket_ranges,
            post_trade_hook=None,
        )
        system.state.day += 1

    console.print("[green]✓[/green] Dealer-ring run complete.")


if __name__ == "__main__":
    cli()
