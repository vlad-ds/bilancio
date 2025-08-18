"""Display utilities for Bilancio CLI."""

from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bilancio.engines.system import System
from bilancio.analysis.visualization import (
    display_agent_balance_table,
    display_multiple_agent_balances,
    display_events,
    display_events_for_day
)
from bilancio.analysis.balances import system_trial_balance
from bilancio.core.errors import DefaultError, ValidationError


console = Console()


def show_scenario_header(name: str, description: Optional[str] = None) -> None:
    """Display scenario header.
    
    Args:
        name: Scenario name
        description: Optional scenario description
    """
    header = Text(name, style="bold cyan")
    if description:
        header.append(f"\n{description}", style="dim")
    
    console.print(Panel(
        header,
        title="Bilancio Scenario",
        border_style="cyan"
    ))


def show_day_summary(
    system: System,
    agent_ids: Optional[List[str]] = None,
    event_mode: str = "detailed",
    day: Optional[int] = None
) -> None:
    """Display summary for a simulation day.
    
    Args:
        system: System instance
        agent_ids: Agent IDs to show balances for
        event_mode: "summary" or "detailed"
        day: Day number to display events for (None for all)
    """
    # Show events
    if day is not None:
        # Show events for specific day
        events_for_day = [e for e in system.state.events if e.get("day") == day]
        if events_for_day:
            console.print("\n[bold]Events:[/bold]")
            if event_mode == "detailed":
                display_events(events_for_day, format="detailed")
            else:
                # Summary mode - just count by type
                event_counts = {}
                for event in events_for_day:
                    event_type = event.get("kind", event.get("type", "Unknown"))
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                for event_type, count in sorted(event_counts.items()):
                    console.print(f"  • {event_type}: {count}")
    else:
        # Show all recent events
        if system.state.events:
            console.print("\n[bold]Events:[/bold]")
            display_events(system.state.events, format="detailed")
    
    # Show balances
    if agent_ids:
        console.print("\n[bold]Balances:[/bold]")
        if len(agent_ids) == 1:
            # Single agent - show detailed balance
            display_agent_balance_table(system, agent_ids[0], format="rich")
        else:
            # Multiple agents - show side by side
            display_multiple_agent_balances(system, agent_ids, format="rich")
    else:
        # Show system trial balance
        console.print("\n[bold]System Trial Balance:[/bold]")
        trial_bal = system_trial_balance(system)
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Metric")
        table.add_column("Value", justify="right")
        
        total_assets = trial_bal.total_financial_assets
        total_liabilities = trial_bal.total_financial_liabilities
        
        table.add_row("Total Assets", f"{total_assets:,.2f}")
        table.add_row("Total Liabilities", f"{total_liabilities:,.2f}")
        table.add_row("Total Equity", f"{total_assets - total_liabilities:,.2f}")
        
        # Check if balanced
        diff = abs(total_assets - total_liabilities)
        if diff < 0.01:
            table.add_row("Status", "[green]✓ Balanced[/green]")
        else:
            table.add_row("Status", f"[red]✗ Imbalanced ({diff:,.2f})[/red]")
        
        console.print(table)


def show_simulation_summary(system: System) -> None:
    """Display final simulation summary.
    
    Args:
        system: System instance
    """
    console.print(Panel(
        f"[bold]Final State[/bold]\n"
        f"Day: {system.state.day}\n"
        f"Total Events: {len(system.state.events)}\n"
        f"Active Agents: {len(system.state.agents)}\n"
        f"Active Contracts: {len(system.state.contracts)}\n"
        f"Stock Lots: {len(system.state.stocks)}",
        title="Summary",
        border_style="green"
    ))


def show_error_panel(
    error: Exception,
    phase: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Display error in a formatted panel.
    
    Args:
        error: Exception that occurred
        phase: Phase where error occurred (setup, day_N, simulation)
        context: Additional context information
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Build error content
    content = Text()
    content.append(f"Type: {error_type}\n", style="red bold")
    content.append(f"Message: {error_msg}\n", style="red")
    
    if context:
        content.append("\nContext:\n", style="yellow")
        for key, value in context.items():
            content.append(f"  • {key}: {value}\n", style="dim")
    
    # Add helpful hints based on error type
    if isinstance(error, DefaultError):
        content.append("\n💡 ", style="yellow")
        content.append("This usually means a debtor lacks sufficient funds or assets to settle an obligation.\n", style="dim")
        content.append("Check the agent's balance sheet and available means of payment.", style="dim")
        
    elif isinstance(error, ValidationError):
        content.append("\n💡 ", style="yellow")
        content.append("This indicates a system invariant violation.\n", style="dim")
        content.append("Common causes: duplicate IDs, negative balances, or mismatched references.", style="dim")
    
    # Display the panel
    console.print(Panel(
        content,
        title=f"Error in {phase}",
        border_style="red",
        expand=False
    ))
    
    # Log the error as an event
    if context and "scenario" in context:
        console.print(f"[dim]Error logged to simulation events[/dim]")