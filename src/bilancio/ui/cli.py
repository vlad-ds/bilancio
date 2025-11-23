"""Command-line interface for Bilancio."""

import click
from pathlib import Path
from typing import Optional, List
import sys

from rich.console import Console
from rich.panel import Panel

from .run import run_scenario
from .wizard import create_scenario_wizard
from bilancio.analysis.loaders import read_events_jsonl, read_balances_csv
from bilancio.analysis.metrics import (
    dues_for_day,
    net_vectors,
    raw_minimum_liquidity,
    size_and_bunching,
    phi_delta,
    replay_intraday_peak,
    velocity,
    creditor_hhi_plus,
    debtor_shortfall_shares,
    start_of_day_money,
    liquidity_gap,
    alpha as alpha_fn,
)
from bilancio.analysis.report import (
    write_day_metrics_csv,
    write_day_metrics_json,
    write_debtor_shares_csv,
    write_intraday_csv,
    write_metrics_html,
)


console = Console()


@click.group()
def cli():
    """Bilancio - Economic simulation framework."""
    pass


@cli.command()
@click.argument('scenario_file', type=click.Path(exists=True, path_type=Path))
@click.option('--mode', type=click.Choice(['step', 'until-stable']), 
              default='until-stable', help='Simulation run mode')
@click.option('--max-days', type=int, default=90, 
              help='Maximum days to simulate')
@click.option('--quiet-days', type=int, default=2,
              help='Required quiet days for stable state')
@click.option('--show', type=click.Choice(['summary', 'detailed', 'table']),
              default='detailed', help='Event display mode')
@click.option('--agents', type=str, default=None,
              help='Comma-separated list of agent IDs to show balances for')
@click.option('--check-invariants', 
              type=click.Choice(['setup', 'daily', 'none']),
              default='setup',
              help='When to check system invariants')
@click.option('--export-balances', type=click.Path(path_type=Path),
              default=None, help='Path to export balances CSV')
@click.option('--export-events', type=click.Path(path_type=Path),
              default=None, help='Path to export events JSONL')
@click.option('--html', type=click.Path(path_type=Path),
              default=None, help='Path to export colored output as HTML')
@click.option('--t-account/--no-t-account', default=False, help='Use detailed T-account layout for balances')
def run(scenario_file: Path, 
        mode: str,
        max_days: int,
        quiet_days: int,
        show: str,
        agents: Optional[str],
        check_invariants: str,
        export_balances: Optional[Path],
        export_events: Optional[Path],
        html: Optional[Path],
        t_account: bool):
    """Run a Bilancio simulation scenario.
    
    Load a scenario from a YAML file and run the simulation either
    step-by-step or until a stable state is reached.
    """
    try:
        # Parse agent list if provided
        agent_ids = None
        if agents:
            agent_ids = [a.strip() for a in agents.split(',')]
        
        # Override export paths if provided via CLI
        export = {
            'balances_csv': str(export_balances) if export_balances else None,
            'events_jsonl': str(export_events) if export_events else None
        }
        
        # Run the scenario
        run_scenario(
            path=scenario_file,
            mode=mode,
            max_days=max_days,
            quiet_days=quiet_days,
            show=show,
            agent_ids=agent_ids,
            check_invariants=check_invariants,
            export=export,
            html_output=html,
            t_account=t_account
        )
        
    except FileNotFoundError as e:
        console.print(Panel(
            f"[red]File not found:[/red] {e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except ValueError as e:
        console.print(Panel(
            f"[red]Configuration error:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except Exception as e:
        console.print(Panel(
            f"[red]Unexpected error:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


@cli.command()
@click.argument('scenario_file', type=click.Path(exists=True, path_type=Path))
def validate(scenario_file: Path):
    """Validate a Bilancio scenario configuration file.
    
    Check that a YAML configuration file is valid without running
    the simulation. Reports any errors in the configuration structure,
    agent definitions, or initial actions.
    """
    try:
        from bilancio.config import load_yaml
        from bilancio.engines.system import System
        from bilancio.config import apply_to_system
        
        # Load and parse the configuration
        console.print(f"[dim]Validating {scenario_file}...[/dim]")
        config = load_yaml(scenario_file)
        
        console.print(f"[green]✓[/green] Configuration syntax is valid")
        console.print(f"  Name: {config.name}")
        console.print(f"  Version: {config.version}")
        console.print(f"  Agents: {len(config.agents)}")
        console.print(f"  Initial actions: {len(config.initial_actions)}")
        
        # Try to apply to a test system to validate actions
        console.print("[dim]Checking if configuration can be applied...[/dim]")
        test_system = System()
        apply_to_system(config, test_system)
        
        console.print(f"[green]✓[/green] Configuration can be applied successfully")
        
        # Run invariant checks
        test_system.assert_invariants()
        console.print(f"[green]✓[/green] System invariants pass")
        
        # Summary
        console.print("\n[bold green]Configuration is valid![/bold green]")
        console.print(f"\nAgents defined:")
        for agent in config.agents:
            console.print(f"  • {agent.id} ({agent.kind}): {agent.name}")
        
        if config.run.export.balances_csv or config.run.export.events_jsonl:
            console.print(f"\nExports configured:")
            if config.run.export.balances_csv:
                console.print(f"  • Balances: {config.run.export.balances_csv}")
            if config.run.export.events_jsonl:
                console.print(f"  • Events: {config.run.export.events_jsonl}")
        
    except FileNotFoundError as e:
        console.print(Panel(
            f"[red]File not found:[/red] {e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except ValueError as e:
        console.print(Panel(
            f"[red]Configuration error:[/red]\n{e}",
            title="Validation Failed",
            border_style="red"
        ))
        sys.exit(1)
        
    except Exception as e:
        console.print(Panel(
            f"[red]Validation error:[/red]\n{e}",
            title="Validation Failed",
            border_style="red"
        ))
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


@cli.command()
@click.option('--from', 'from_template', type=str, default=None,
              help='Base template to use')
@click.option('-o', '--output', type=click.Path(path_type=Path),
              required=True, help='Output YAML file path')
def new(from_template: Optional[str], output: Path):
    """Create a new scenario configuration.
    
    Interactive wizard to create a new Bilancio scenario
    configuration file.
    """
    try:
        create_scenario_wizard(output, from_template)
        console.print(f"[green]✓[/green] Created scenario file: {output}")
        
    except Exception as e:
        console.print(Panel(
            f"[red]Failed to create scenario:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)


@cli.command()
@click.option('--events', 'events_path', type=click.Path(exists=True, path_type=Path), required=True,
              help='Path to events JSONL exported by a run')
@click.option('--balances', 'balances_path', type=click.Path(exists=False, path_type=Path), required=False,
              help='Path to balances CSV (optional, improves G_t/M_t)')
@click.option('--days', type=str, default=None,
              help='Days to analyze, e.g. "1,2-3". Default: infer from events')
@click.option('--out-csv', 'out_csv', type=click.Path(path_type=Path), default=None,
              help='Output CSV for day-level metrics')
@click.option('--out-json', 'out_json', type=click.Path(path_type=Path), default=None,
              help='Output JSON for day-level metrics')
@click.option('--intraday-csv', 'intraday_csv', type=click.Path(path_type=Path), default=None,
              help='Optional CSV for intraday P_prefix steps')
@click.option('--html', 'html_out', type=click.Path(path_type=Path), default=None,
              help='Optional HTML analytics report')
def analyze(
    events_path: Path,
    balances_path: Optional[Path],
    days: Optional[str],
    out_csv: Optional[Path],
    out_json: Optional[Path],
    intraday_csv: Optional[Path],
    html_out: Optional[Path],
):
    """Analyze a completed run and export Kalecki-style metrics.

    Produces a day-level metrics CSV/JSON, optional intraday CSV (diagnostic).
    """
    # Load inputs
    console.print(f"[dim]Reading events from {events_path}...[/dim]")
    events = list(read_events_jsonl(events_path))

    balances_rows = None
    if balances_path and balances_path.exists():
        console.print(f"[dim]Reading balances from {balances_path}...[/dim]")
        balances_rows = read_balances_csv(balances_path)

    # Parse days argument: supports comma lists and ranges like 1-3
    def parse_days_arg(s: str) -> List[int]:
        out: List[int] = []
        for part in s.split(','):
            part = part.strip()
            if '-' in part:
                a, b = part.split('-', 1)
                try:
                    start = int(a)
                    end = int(b)
                    out.extend(list(range(start, end + 1)))
                except Exception:
                    continue
            else:
                try:
                    out.append(int(part))
                except Exception:
                    continue
        return sorted(sorted(set(out)))

    if days:
        day_list = parse_days_arg(days)
    else:
        # Infer days from events: include both due_day values and actual settlement days
        due_days = {int(e["due_day"]) for e in events if e.get("kind") == "PayableCreated" and e.get("due_day") is not None}
        settled_days = {int(e["day"]) for e in events if e.get("kind") == "PayableSettled" and e.get("day") is not None}
        day_list = sorted(due_days | settled_days)
    if not day_list:
        console.print("[yellow]No days found to analyze.[/yellow]")
        return

    # Determine default output paths if not provided
    base = events_path.stem.replace("_events", "") or "metrics"
    out_dir = events_path.parent
    if not out_csv:
        out_csv = out_dir / f"{base}_metrics_day.csv"
    if not out_json:
        out_json = out_dir / f"{base}_metrics_day.json"
    if intraday_csv:
        intraday_csv.parent.mkdir(parents=True, exist_ok=True)

    metrics_rows: List[dict] = []
    ds_rows: List[dict] = []
    intraday_rows: List[dict] = []

    for t in day_list:
        # Compute core sets
        dues = dues_for_day(events, t)
        nets = net_vectors(dues)
        Mbar_t = raw_minimum_liquidity(nets)
        S_t, _ = size_and_bunching(dues)
        phi_t, delta_t = phi_delta(events, dues, t)
        Mpeak_t, steps, gross_t = replay_intraday_peak(events, t)
        v_t = velocity(gross_t, Mpeak_t)
        HHIp_t = creditor_hhi_plus(nets)
        DS = debtor_shortfall_shares(nets)
        n_debtors = sum(1 for a, v in nets.items() if v["F"] > v["I"])
        n_creditors = sum(1 for a, v in nets.items() if v["n"] > 0)

        # Money supply (optional if balances provided)
        M_t = None
        G_t = None
        if balances_rows is not None:
            M_t = start_of_day_money(balances_rows, t)
            G_t = liquidity_gap(Mbar_t, M_t)

        alpha_t = alpha_fn(Mbar_t, S_t) if S_t is not None else None

        notes: List[str] = []
        if HHIp_t is None:
            notes.append("no net creditors")
        if all(v is None for v in DS.values()):
            notes.append("no net debtors")

        metrics_rows.append(
            {
                "day": t,
                "S_t": S_t,
                "Mbar_t": Mbar_t,
                "M_t": M_t,
                "G_t": G_t,
                "alpha_t": alpha_t,
                "Mpeak_t": Mpeak_t,
                "gross_settled_t": gross_t,
                "v_t": v_t,
                "phi_t": phi_t,
                "delta_t": delta_t,
                "n_debtors": n_debtors,
                "n_creditors": n_creditors,
                "HHIplus_t": HHIp_t,
                "notes": ", ".join(notes) if notes else "",
            }
        )

        # Debtor shares (long form)
        for agent, share in DS.items():
            ds_rows.append({"day": t, "agent": agent, "DS_t": share})

        # Intraday diagnostics
        for row in steps:
            intraday_rows.append(row)

    # Write outputs
    write_day_metrics_csv(out_csv, metrics_rows)
    console.print(f"[green]✓[/green] Wrote day metrics CSV: {out_csv}")
    write_day_metrics_json(out_json, metrics_rows)
    console.print(f"[green]✓[/green] Wrote day metrics JSON: {out_json}")

    # Debtor shares and intraday are optional; only write if path provided
    base_name = out_csv.stem.replace("_metrics_day", "") if out_csv else "metrics"
    ds_path = out_csv.parent / f"{base_name}_ds.csv"
    write_debtor_shares_csv(ds_path, ds_rows)
    console.print(f"[green]✓[/green] Wrote debtor shares CSV: {ds_path}")

    if intraday_csv:
        write_intraday_csv(intraday_csv, intraday_rows)
        console.print(f"[green]✓[/green] Wrote intraday CSV: {intraday_csv}")

    if html_out:
        title = f"Bilancio Analytics — {events_path.stem.replace('_events','')}"
        subtitle = f"Events: {events_path.name}{' | Balances: ' + balances_path.name if balances_path else ''}"
        write_metrics_html(html_out, metrics_rows, ds_rows, intraday_rows, title=title, subtitle=subtitle)
        console.print(f"[green]✓[/green] Wrote HTML analytics: {html_out}")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()

# Register dealer-ring runner
from .cli_dealer_ring import cli as dealer_ring_cli  # noqa: E402
cli.add_command(dealer_ring_cli, name="dealer-ring-run")
