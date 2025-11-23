"""CLI entry for dealer-ring scenarios (config-driven, alpha)."""

from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console

from bilancio.engines.system import System
from bilancio.config import load_yaml, apply_to_system
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
    base_path = Path(cfg["base_scenario"])
    ticket_size = int(cfg.get("ticket_size", 1))
    buckets_cfg = cfg["buckets"]
    dealer_ids = cfg["dealers"]
    vbt_ids = cfg["vbts"]
    shares = cfg.get("shares", {})
    dealer_share = float(shares.get("dealer", 0.25))
    vbt_share = float(shares.get("vbt", 0.5))
    flow = cfg.get("flow", {})
    pi_sell = float(flow.get("pi_sell", 0.5))
    N_max = int(flow.get("N_max", 3))
    invest_horizon = int(flow.get("invest_horizon", 3))
    cash_buffer = int(flow.get("cash_buffer", 1))

    # Load base scenario and apply to system
    config = load_yaml(base_path)
    system = System()
    apply_to_system(config, system)

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
