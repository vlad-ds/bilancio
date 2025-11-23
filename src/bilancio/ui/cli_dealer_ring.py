"""CLI entry for dealer-ring scenarios (alpha)."""

from pathlib import Path
from typing import Optional

import click

from rich.console import Console

from bilancio.engines.system import System
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


@click.command()
@click.argument('scenario_file', type=click.Path(exists=True, path_type=Path))
@click.option('--days', type=int, default=5, help='Number of periods to run')
def cli(scenario_file: Path, days: int):
    """Run a dealer-ring scenario (placeholder: assumes payables already in system)."""
    # TODO: load a dealer-ring specific YAML; for now reuse existing config loader
    from bilancio.config import load_yaml, apply_to_system

    config = load_yaml(scenario_file)
    system = System()
    apply_to_system(config, system)

    # Hard-coded bucket ranges and params (placeholder)
    bucket_ranges = [("Short", 1, 3), ("Mid", 4, 8), ("Long", 9, None)]
    ticket_size = 1

    # Ticketize payables, allocate holdings, seed cash (placeholder IDs)
    ticketize_payables(system, bucket_ranges=bucket_ranges, ticket_size=ticket_size, remove_payables=False)

    # Create dealers/VBTs if not present
    dealer_ids = [a.id for a in system.state.agents.values() if a.kind == "dealer"]
    vbt_ids = [a.id for a in system.state.agents.values() if a.kind == "vbt"]
    if len(dealer_ids) < 3 or len(vbt_ids) < 3:
        console.print("[red]Need three dealers and three VBTs in config for this placeholder runner.[/red]")
        return

    buckets = {
        "Short": DealerBucket("Short", ticket_size, 1.0, 0.20, cash=0.0, inventory=0.0, dealer_id=dealer_ids[0], vbt_id=vbt_ids[0]),
        "Mid": DealerBucket("Mid", ticket_size, 1.0, 0.30, cash=0.0, inventory=0.0, dealer_id=dealer_ids[1], vvt_id=vbt_ids[1]) if False else DealerBucket("Mid", ticket_size, 1.0, 0.30, cash=0.0, inventory=0.0, dealer_id=dealer_ids[1], vbt_id=vbt_ids[1]),
        "Long": DealerBucket("Long", ticket_size, 1.0, 0.40, cash=0.0, inventory=0.0, dealer_id=dealer_ids[2], vbt_id=vbt_ids[2]),
    }
    vbts = {
        "Short": VBTBucket("Short", ticket_size, 1.0, 0.20, phi_M=1.0, phi_O=0.6),
        "Mid": VBTBucket("Mid", ticket_size, 1.0, 0.30, phi_M=1.0, phi_O=0.6),
        "Long": VBTBucket("Long", ticket_size, 1.0, 0.40, phi_M=1.0, phi_O=0.6),
    }

    # Seed cash/inventory mid-shelf
    for bname, dealer in buckets.items():
        seed_dealer_vbt_cash(system, dealer_id=dealer.dealer_id, vbt_id=vbts[bname].bucket, mid=dealer.mid, X_target=4, ticket_size=ticket_size)

    ticket_ops = TicketOps(system)

    # Allocate tickets to dealer/VBT shares
    for bname in buckets.keys():
        allocate_tickets(system, bucket_id=bname, dealer_id=buckets[bname].dealer_id, vbt_id=vbts[bname].bucket, dealer_share=0.25, vbt_share=0.5)

    for t in range(days):
        console.print(f"[cyan]Period {t}[/cyan]")
        run_period(
            system=system,
            buckets=buckets,
            vbts=vbts,
            ticket_ops=ticket_ops,
            pi_sell=0.5,
            N_max=3,
            eligible_fn=lambda sys: default_eligibility(sys, cash_buffer=1, horizon=3),
            bucket_selector=None,
            ticket_size=ticket_size,
            bucket_ranges=bucket_ranges,
            post_trade_hook=None,
        )
        system.state.day += 1


if __name__ == "__main__":
    cli()
