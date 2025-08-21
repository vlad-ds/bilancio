"""Command-line interface for Bilancio."""

import click
from pathlib import Path
from typing import Optional, List
import sys

from rich.console import Console
from rich.panel import Panel

from .run import run_scenario
from .wizard import create_scenario_wizard


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
@click.option('--show', type=click.Choice(['summary', 'detailed']),
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
def run(scenario_file: Path, 
        mode: str,
        max_days: int,
        quiet_days: int,
        show: str,
        agents: Optional[str],
        check_invariants: str,
        export_balances: Optional[Path],
        export_events: Optional[Path],
        html: Optional[Path]):
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
            html_output=html
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


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()