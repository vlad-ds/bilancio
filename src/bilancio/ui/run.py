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
    show_scenario_header_renderable,
    show_day_summary,
    show_day_summary_renderable,
    show_simulation_summary,
    show_simulation_summary_renderable,
    show_error_panel
)


console = Console(record=True, width=100)


def run_scenario(
    path: Path,
    mode: str = "until_stable",
    max_days: int = 90,
    quiet_days: int = 2,
    show: str = "detailed",
    agent_ids: Optional[List[str]] = None,
    check_invariants: str = "setup",
    export: Optional[Dict[str, str]] = None,
    html_output: Optional[Path] = None
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
        html_output: Optional path to export HTML with colored output
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
    
    # Show scenario header with agent list
    header_renderables = show_scenario_header_renderable(config.name, config.description, config.agents)
    for renderable in header_renderables:
        console.print(renderable)
    
    # Show initial state
    console.print("\n[bold cyan]📅 Day 0 (After Setup)[/bold cyan]")
    renderables = show_day_summary_renderable(system, agent_ids, show)
    for renderable in renderables:
        console.print(renderable)
    
    # Capture initial balance state for HTML export
    initial_balances = {}
    from bilancio.analysis.balances import agent_balance
    # Capture balances for all agents that we might display
    capture_ids = agent_ids if agent_ids else [a.id for a in system.state.agents.values()]
    for agent_id in capture_ids:
        initial_balances[agent_id] = agent_balance(system, agent_id)
    
    # Track day data for PDF export
    days_data = []
    
    if mode == "step":
        days_data = run_step_mode(
            system=system,
            max_days=max_days,
            show=show,
            agent_ids=agent_ids,
            check_invariants=check_invariants,
            scenario_name=config.name
        )
    else:
        days_data = run_until_stable_mode(
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
    
    # Export to HTML if requested
    if html_output:
        from rich.terminal_theme import MONOKAI
        html_output.parent.mkdir(parents=True, exist_ok=True)
        html_content = console.export_html(
            theme=MONOKAI,
            inline_styles=True
        )
        with open(html_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        console.print(f"[green]✓[/green] Exported colored output to HTML: {html_output}")


def run_step_mode(
    system: System,
    max_days: int,
    show: str,
    agent_ids: Optional[List[str]],
    check_invariants: str,
    scenario_name: str
) -> List[Dict[str, Any]]:
    """Run simulation in step-by-step mode.
    
    Args:
        system: Configured system
        max_days: Maximum days to simulate
        show: Event display mode
        agent_ids: Agent IDs to show balances for
        check_invariants: Invariant checking mode
        scenario_name: Name of the scenario for error context
    
    Returns:
        List of day data dictionaries
    """
    days_data = []
    
    for _ in range(max_days):
        # Get the current day before running 
        day_before = system.state.day
        
        # Prompt to continue (ask about the next day which is day_before + 1)
        console.print()
        if not Confirm.ask(f"[cyan]Run day {day_before + 1}?[/cyan]", default=True):
            console.print("[yellow]Simulation stopped by user[/yellow]")
            break
        
        try:
            # Run the next day
            day_report = run_day(system)
            
            # Check invariants if requested
            if check_invariants == "daily":
                system.assert_invariants()
            
            # Skip day 0 - it's already shown as "Day 0 (After Setup)"
            if day_before >= 1:
                # Show day summary
                console.print(f"\n[bold cyan]📅 Day {day_before}[/bold cyan]")
                renderables = show_day_summary_renderable(system, agent_ids, show, day=day_before)
                for renderable in renderables:
                    console.print(renderable)
                
                # Collect day data for HTML export  
                # Use the actual event day
                day_events = [e for e in system.state.events 
                             if e.get("day") == day_before and e.get("phase") == "simulation"]
                
                # Capture current balance state for this day
                day_balances = {}
                if agent_ids:
                    from bilancio.analysis.balances import agent_balance
                    for agent_id in agent_ids:
                        day_balances[agent_id] = agent_balance(system, agent_id)
                
                days_data.append({
                    'day': day_before,  # Use actual event day, not 1-based counter
                    'events': day_events,
                    'quiet': day_report.quiet,
                    'stable': day_report.quiet and not day_report.has_open_obligations,
                    'balances': day_balances
                })
            
            # Check if we've reached a stable state
            if day_report.quiet and not day_report.has_open_obligations:
                console.print("[green]✓[/green] System reached stable state")
                break
                
        except DefaultError as e:
            show_error_panel(
                error=e,
                phase=f"day_{system.state.day}",
                context={
                    "scenario": scenario_name,
                    "day": system.state.day,
                    "phase": system.state.phase
                }
            )
            break
            
        except ValidationError as e:
            show_error_panel(
                error=e,
                phase=f"day_{system.state.day}",
                context={
                    "scenario": scenario_name,
                    "day": system.state.day,
                    "phase": system.state.phase
                }
            )
            break
            
        except Exception as e:
            show_error_panel(
                error=e,
                phase=f"day_{system.state.day}",
                context={
                    "scenario": scenario_name,
                    "day": system.state.day
                }
            )
            break
    
    # Show final summary
    console.print("\n[bold]Simulation Complete[/bold]")
    console.print(show_simulation_summary_renderable(system))
    
    return days_data


def run_until_stable_mode(
    system: System,
    max_days: int,
    quiet_days: int,
    show: str,
    agent_ids: Optional[List[str]],
    check_invariants: str,
    scenario_name: str
) -> List[Dict[str, Any]]:
    """Run simulation until stable state is reached.
    
    Args:
        system: Configured system
        max_days: Maximum days to simulate
        quiet_days: Required quiet days for stable state
        show: Event display mode
        agent_ids: Agent IDs to show balances for
        check_invariants: Invariant checking mode
        scenario_name: Name of the scenario for error context
    
    Returns:
        List of day data dictionaries
    """
    console.print(f"\n[dim]Running simulation until stable (max {max_days} days)...[/dim]\n")
    
    try:
        # Run simulation day by day to capture correct balance snapshots
        from bilancio.engines.simulation import run_day, _impacted_today, _has_open_obligations
        from bilancio.analysis.balances import agent_balance
        
        reports = []
        consecutive_quiet = 0
        days_data = []
        
        for _ in range(max_days):
            # Run the next day
            day_before = system.state.day
            run_day(system)
            impacted = _impacted_today(system, day_before)
            
            # Create report
            from bilancio.engines.simulation import DayReport
            report = DayReport(day=day_before, impacted=impacted)
            reports.append(report)
            
            # Skip day 0 - it's already shown as "Day 0 (After Setup)"
            if day_before >= 1:
                # Display this day's results immediately (with correct balance state)
                console.print(f"[bold cyan]📅 Day {day_before}[/bold cyan]")
                
                # Check invariants if requested
                if check_invariants == "daily":
                    try:
                        system.assert_invariants()
                    except Exception as e:
                        console.print(f"[yellow]⚠ Invariant check failed: {e}[/yellow]")
                
                # Show events and balances for this specific day
                # Note: events are stored with 0-based day numbers
                renderables = show_day_summary_renderable(system, agent_ids, show, day=day_before)
                for renderable in renderables:
                    console.print(renderable)
                
                # Collect day data for HTML export
                # We want simulation events from the day that was just displayed
                # show_day_summary was called with day=day_before
                day_events = [e for e in system.state.events 
                             if e.get("day") == day_before and e.get("phase") == "simulation"]
                is_stable = consecutive_quiet >= quiet_days and not _has_open_obligations(system)
                
                # Capture current balance state for this day
                day_balances = {}
                if agent_ids:
                    for agent_id in agent_ids:
                        day_balances[agent_id] = agent_balance(system, agent_id)
                
                days_data.append({
                    'day': day_before,  # Use actual event day, not 1-based counter
                    'events': day_events,
                    'quiet': report.impacted == 0,
                    'stable': is_stable,
                    'balances': day_balances
                })
                
                # Show activity summary
                if report.impacted > 0:
                    console.print(f"[dim]Activity: {report.impacted} impactful events[/dim]")
                else:
                    console.print("[dim]→ Quiet day (no activity)[/dim]")
                
                if report.notes:
                    console.print(f"[dim]Note: {report.notes}[/dim]")
                
                console.print()
            
            # Check for stable state
            if impacted == 0:
                consecutive_quiet += 1
            else:
                consecutive_quiet = 0
            
            if consecutive_quiet >= quiet_days and not _has_open_obligations(system):
                console.print("[green]✓[/green] System reached stable state")
                break
        
        # If we didn't break early, check if we hit max days
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
    console.print(show_simulation_summary_renderable(system))
    
    return days_data