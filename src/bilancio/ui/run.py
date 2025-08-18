"""Orchestration logic for running Bilancio simulations."""

from pathlib import Path
from typing import Optional, List, Dict, Any
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from bilancio.engines.system import System
from bilancio.engines.simulation import run_day, run_until_stable
from bilancio.core.errors import ValidationError, DefaultError
from bilancio.config import load_yaml, apply_to_system
from bilancio.export.writers import write_balances_csv, write_events_jsonl

from .display import (
    show_scenario_header,
    show_day_summary,
    show_simulation_summary,
    show_error_panel
)


console = Console()


def run_scenario(
    path: Path,
    mode: str = "until_stable",
    max_days: int = 90,
    quiet_days: int = 2,
    show: str = "detailed",
    agent_ids: Optional[List[str]] = None,
    check_invariants: str = "setup",
    export: Optional[Dict[str, str]] = None
) -> None:
    """Run a Bilancio simulation scenario.
    
    Args:
        path: Path to scenario YAML file
        mode: "step" or "until_stable"
        max_days: Maximum days to simulate
        quiet_days: Required quiet days for stable state
        show: "summary" or "detailed" for event display
        agent_ids: List of agent IDs to show balances for
        check_invariants: "setup", "daily", or "none"
        export: Dictionary with export paths (balances_csv, events_jsonl)
    """
    # Load configuration
    console.print("[dim]Loading scenario...[/dim]")
    config = load_yaml(path)
    
    # Create and configure system
    system = System()
    
    # Apply configuration
    try:
        apply_to_system(config, system)
        
        if check_invariants in ("setup", "daily"):
            system.assert_invariants()
            
    except (ValidationError, ValueError) as e:
        show_error_panel(
            error=e,
            phase="setup",
            context={"scenario": config.name}
        )
        sys.exit(1)
    
    # Use config settings unless overridden by CLI
    if agent_ids is None and config.run.show.balances:
        agent_ids = config.run.show.balances
    
    if export is None:
        export = {}
    
    # Use config export settings if not overridden
    if not export.get('balances_csv') and config.run.export.balances_csv:
        export['balances_csv'] = config.run.export.balances_csv
    if not export.get('events_jsonl') and config.run.export.events_jsonl:
        export['events_jsonl'] = config.run.export.events_jsonl
    
    # Show scenario header
    show_scenario_header(config.name, config.description)
    
    # Show initial state
    console.print("\n[bold cyan]📅 Day 0 (After Setup)[/bold cyan]")
    show_day_summary(system, agent_ids, show)
    
    if mode == "step":
        run_step_mode(
            system=system,
            max_days=max_days,
            show=show,
            agent_ids=agent_ids,
            check_invariants=check_invariants,
            scenario_name=config.name
        )
    else:
        run_until_stable_mode(
            system=system,
            max_days=max_days,
            quiet_days=quiet_days,
            show=show,
            agent_ids=agent_ids,
            check_invariants=check_invariants,
            scenario_name=config.name
        )
    
    # Export results if requested
    if export.get('balances_csv'):
        export_path = Path(export['balances_csv'])
        export_path.parent.mkdir(parents=True, exist_ok=True)
        write_balances_csv(system, export_path)
        console.print(f"[green]✓[/green] Exported balances to {export_path}")
    
    if export.get('events_jsonl'):
        export_path = Path(export['events_jsonl'])
        export_path.parent.mkdir(parents=True, exist_ok=True)
        write_events_jsonl(system, export_path)
        console.print(f"[green]✓[/green] Exported events to {export_path}")


def run_step_mode(
    system: System,
    max_days: int,
    show: str,
    agent_ids: Optional[List[str]],
    check_invariants: str,
    scenario_name: str
) -> None:
    """Run simulation in step-by-step mode.
    
    Args:
        system: Configured system
        max_days: Maximum days to simulate
        show: Event display mode
        agent_ids: Agent IDs to show balances for
        check_invariants: Invariant checking mode
        scenario_name: Name of the scenario for error context
    """
    day = 0
    
    while day < max_days:
        # Prompt to continue
        console.print()
        if not Confirm.ask(f"[cyan]Run day {day + 1}?[/cyan]", default=True):
            console.print("[yellow]Simulation stopped by user[/yellow]")
            break
        
        try:
            # Run the next day
            day_report = run_day(system)
            day += 1
            
            # Check invariants if requested
            if check_invariants == "daily":
                system.assert_invariants()
            
            # Show day summary
            console.print(f"\n[bold cyan]📅 Day {day}[/bold cyan]")
            show_day_summary(system, agent_ids, show)
            
            # Check if we've reached a stable state
            if day_report.quiet and not day_report.has_open_obligations:
                console.print("[green]✓[/green] System reached stable state")
                break
                
        except DefaultError as e:
            show_error_panel(
                error=e,
                phase=f"day_{day + 1}",
                context={
                    "scenario": scenario_name,
                    "day": day + 1,
                    "phase": system.state.phase
                }
            )
            break
            
        except ValidationError as e:
            show_error_panel(
                error=e,
                phase=f"day_{day + 1}",
                context={
                    "scenario": scenario_name,
                    "day": day + 1,
                    "phase": system.state.phase
                }
            )
            break
            
        except Exception as e:
            show_error_panel(
                error=e,
                phase=f"day_{day + 1}",
                context={
                    "scenario": scenario_name,
                    "day": day + 1
                }
            )
            break
    
    # Show final summary
    console.print("\n[bold]Simulation Complete[/bold]")
    show_simulation_summary(system)


def run_until_stable_mode(
    system: System,
    max_days: int,
    quiet_days: int,
    show: str,
    agent_ids: Optional[List[str]],
    check_invariants: str,
    scenario_name: str
) -> None:
    """Run simulation until stable state is reached.
    
    Args:
        system: Configured system
        max_days: Maximum days to simulate
        quiet_days: Required quiet days for stable state
        show: Event display mode
        agent_ids: Agent IDs to show balances for
        check_invariants: Invariant checking mode
        scenario_name: Name of the scenario for error context
    """
    console.print(f"\n[dim]Running simulation until stable (max {max_days} days)...[/dim]\n")
    
    try:
        # Run until stable
        reports = run_until_stable(
            system=system,
            max_days=max_days,
            quiet_days=quiet_days
        )
        
        # Show progress for each day
        for i, report in enumerate(reports, 1):
            console.print(f"[bold cyan]📅 Day {i}[/bold cyan]")
            
            # Check invariants if requested
            if check_invariants == "daily":
                try:
                    system.assert_invariants()
                except Exception as e:
                    console.print(f"[yellow]⚠ Invariant check failed: {e}[/yellow]")
            
            # Show events and balances
            show_day_summary(system, agent_ids, show, day=i)
            
            # Show activity summary
            if report.impacted > 0:
                console.print(f"[dim]Activity: {report.impacted} impactful events[/dim]")
            else:
                console.print("[dim]→ Quiet day (no activity)[/dim]")
            
            if report.notes:
                console.print(f"[dim]Note: {report.notes}[/dim]")
            
            console.print()
        
        # Check final state
        final_report = reports[-1] if reports else None
        # A day is quiet if it has 0 impacted events
        # Check if there are open obligations
        has_open = any(c.kind in ("payable", "delivery_obligation") 
                      for c in system.state.contracts.values())
        
        if final_report and final_report.impacted == 0 and not has_open:
            console.print("[green]✓[/green] System reached stable state")
        else:
            console.print("[yellow]⚠[/yellow] Maximum days reached without stable state")
        
    except DefaultError as e:
        show_error_panel(
            error=e,
            phase="simulation",
            context={
                "scenario": scenario_name,
                "day": system.state.day,
                "phase": system.state.phase
            }
        )
        
    except ValidationError as e:
        show_error_panel(
            error=e,
            phase="simulation",
            context={
                "scenario": scenario_name,
                "day": system.state.day,
                "phase": system.state.phase
            }
        )
        
    except Exception as e:
        show_error_panel(
            error=e,
            phase="simulation",
            context={
                "scenario": scenario_name,
                "day": system.state.day
            }
        )
    
    # Show final summary
    console.print("\n[bold]Simulation Complete[/bold]")
    show_simulation_summary(system)