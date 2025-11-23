"""CLI entry for dealer-ring scenarios (config-driven)."""

from pathlib import Path
from typing import List

import click
import yaml
from pydantic import BaseModel, ValidationError
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


class AgentGroup(BaseModel):
    kind: str
    count: int
    id_prefix: str
    name_prefix: str


class BucketCfg(BaseModel):
    name: str
    tau_range: List[int | None]
    M0: float
    O0: float
    phi_M: float = 1.0
    phi_O: float = 0.6
    guard_M_min: float = 0.0
    clip_nonneg_bid: bool = True
    Xstar_target: int = 4


class SharesCfg(BaseModel):
    dealer: float = 0.25
    vbt: float = 0.5


class FlowCfg(BaseModel):
    pi_sell: float = 0.5
    N_max: int = 3
    invest_horizon: int = 3
    cash_buffer: int = 1


class DealerRingConfig(BaseModel):
    version: int = 1
    name: str
    description: str | None = None
    ticket_size: int = 1
    agents: List[dict] = []
    agent_groups: List[AgentGroup] = []
    initial_actions: List[dict] = []
    buckets: List[BucketCfg]
    dealers: List[str]
    vbts: List[str]
    shares: SharesCfg = SharesCfg()
    flow: FlowCfg = FlowCfg()


def _load_config(path: Path) -> DealerRingConfig:
    data = yaml.safe_load(path.read_text())
    try:
        return DealerRingConfig(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid dealer-ring config: {e}")


def _expand_agents(cfg: DealerRingConfig) -> List[dict]:
    out = list(cfg.agents)
    for grp in cfg.agent_groups:
        for i in range(1, grp.count + 1):
            out.append({
                "id": f"{grp.id_prefix}{i}",
                "kind": grp.kind,
                "name": f"{grp.name_prefix}{i}",
            })
    return out


def _expand_actions(cfg: DealerRingConfig) -> List[dict]:
    actions = []
    for act in cfg.initial_actions:
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


def _validate_counts(system: System, cfg: DealerRingConfig, trader_min: int = 100):
    dealers = [a.id for a in system.state.agents.values() if a.kind == "dealer"]
    vbts = [a.id for a in system.state.agents.values() if a.kind == "vbt"]
    traders = [a.id for a in system.state.agents.values() if a.kind == "household"]
    if dealers != cfg.dealers:
        raise ValueError(f"Dealers mismatch: expected {cfg.dealers}, found {dealers}")
    if vbts != cfg.vbts:
        raise ValueError(f"VBTs mismatch: expected {cfg.vbts}, found {vbts}")
    if len(traders) < trader_min:
        raise ValueError(f"Expected at least {trader_min} traders, found {len(traders)}")


@click.command()
@click.argument('config_file', type=click.Path(exists=True, path_type=Path))
@click.option('--days', type=int, default=5, help='Number of periods to run')
def cli(config_file: Path, days: int):
    """Run a dealer-ring scenario using a config file."""
    cfg = _load_config(config_file)
    ticket_size = cfg.ticket_size

    system = System()

    # Agents
    for agent_dict in _expand_agents(cfg):
        spec = AgentSpec(**agent_dict)
        agent_obj = create_agent(spec)
        system.add_agent(agent_obj)

    # Initial actions
    for act in _expand_actions(cfg):
        apply_action(system, act, system.state.agents)

    # Validate counts/ids
    _validate_counts(system, cfg)

    # Buckets
    bucket_ranges = []
    buckets = {}
    vbts = {}
    for i, b in enumerate(cfg.buckets):
        tau = b.tau_range
        lo = int(tau[0])
        hi = int(tau[1]) if len(tau) > 1 and tau[1] is not None else None
        bucket_ranges.append((b.name, lo, hi))
        dealer_id = cfg.dealers[i]
        vbt_id = cfg.vbts[i]
        buckets[b.name] = DealerBucket(
            bucket=b.name,
            ticket_size=ticket_size,
            mid=b.M0,
            spread=b.O0,
            cash=0.0,
            inventory=0.0,
            guard_m_min=b.guard_M_min,
            vbt=None,
            dealer_id=dealer_id,
            vbt_id=vbt_id,
        )
        vbts[b.name] = VBTBucket(
            bucket=b.name,
            ticket_size=ticket_size,
            mid=b.M0,
            spread=b.O0,
            phi_M=b.phi_M,
            phi_O=b.phi_O,
            guard_M_min=b.guard_M_min,
            clip_nonneg_bid=b.clip_nonneg_bid,
        )

    ticket_ops = TicketOps(system)

    # Ticketize payables
    ticketize_payables(system, bucket_ranges=bucket_ranges, ticket_size=ticket_size, remove_payables=True)

    # Seed cash/inventory
    for b in cfg.buckets:
        seed_dealer_vbt_cash(system, dealer_id=buckets[b.name].dealer_id, vbt_id=vbts[b.name].bucket, mid=b.M0, X_target=b.Xstar_target, ticket_size=ticket_size)

    # Allocate tickets
    for b in cfg.buckets:
        allocate_tickets(system, bucket_id=b.name, dealer_id=buckets[b.name].dealer_id, vbt_id=vbts[b.name].bucket, dealer_share=cfg.shares.dealer, vbt_share=cfg.shares.vbt)

    # Run
    for _ in range(days):
        run_period(
            system=system,
            buckets=buckets,
            vbts=vbts,
            ticket_ops=ticket_ops,
            pi_sell=cfg.flow.pi_sell,
            N_max=cfg.flow.N_max,
            eligible_fn=lambda sys: default_eligibility(sys, cash_buffer=cfg.flow.cash_buffer, horizon=cfg.flow.invest_horizon),
            bucket_selector=None,
            ticket_size=ticket_size,
            bucket_ranges=bucket_ranges,
            post_trade_hook=None,
        )
        system.state.day += 1

    console.print("[green]✓[/green] Dealer-ring run complete.")


if __name__ == "__main__":
    cli()
