"""HTML export functionality for Bilancio CLI output."""

from pathlib import Path
from typing import Optional, List, Dict, Any
from io import StringIO
import tempfile
import os
import base64

from rich.console import Console
from rich.terminal_theme import MONOKAI

from bilancio.engines.system import System
from bilancio.config.models import ScenarioConfig
from .display import (
    show_scenario_header,
    show_day_summary,
    show_simulation_summary
)


def export_to_html(
    output_path: Path,
    system: System,
    config: ScenarioConfig,
    days_data: List[Dict[str, Any]],
    agent_ids: Optional[List[str]] = None,
    show: str = "detailed",
    initial_balances: Optional[Dict[str, Any]] = None
) -> None:
    """Export simulation output to HTML with colors and formatting.
    
    Args:
        output_path: Path to save the HTML file
        system: The simulation system
        config: Scenario configuration
        days_data: List of day summaries with events and state
        agent_ids: Agent IDs to show balances for
        show: Event display mode
        initial_balances: Initial balance snapshots after setup
    """
    # Create a console that captures to HTML
    console = Console(
        record=True,
        force_terminal=True,
        force_jupyter=False,
        width=120,  # Fixed width for consistent formatting
        legacy_windows=False
    )
    
    # Capture the scenario header
    _capture_scenario_header(console, config.name, config.description)
    
    # Capture initial state (Day 0)
    console.print("\n[bold cyan]📅 Day 0 (Initial Setup)[/bold cyan]")
    
    # Show agents
    if config.agents:
        console.print("\n[bold]Agents:[/bold]")
        for agent in config.agents:
            icon = {"central_bank": "🏛️", "bank": "🏦", "household": "👤", "firm": "🏢"}.get(agent.kind, "📌")
            name_text = f" ({agent.name})" if agent.name else ""
            console.print(f"  {icon} {agent.id}{name_text} - {agent.kind}", style="dim")
    
    # Show initial actions from config (this is the complete story)
    if config.initial_actions:
        console.print("\n[bold]Initial Actions:[/bold]")
        _capture_initial_actions(console, config.initial_actions)
    
    # Show initial balances (use the snapshot if available)
    if initial_balances:
        console.print("\n[bold]Initial Balances:[/bold]")
        _capture_balances_from_snapshot(console, initial_balances, system)
    elif agent_ids:
        console.print("\n[bold]Initial Balances:[/bold]")
        _capture_balances(console, system, agent_ids)
    
    # Capture each day's output
    for day_data in days_data:
        day_num = day_data['day']
        
        # Skip day 0 - it's already shown as "Day 0 (Initial Setup)"
        if day_num == 0:
            continue
            
        console.print(f"\n[bold cyan]📅 Day {day_num}[/bold cyan]")
        
        # Show day events and balances
        # The events in day_data are the events that happened DURING this day
        _capture_day_summary(
            console, 
            system, 
            agent_ids, 
            show, 
            day=day_num,
            day_events=day_data.get('events', []),
            day_balances=day_data.get('balances', {})
        )
        
        # Add status messages
        if day_data.get('quiet'):
            console.print("[dim]→ Quiet day (no activity)[/dim]")
        
        if day_data.get('stable'):
            console.print("[green]✓ System reached stable state[/green]")
    
    # Add simulation complete message
    console.print("\n[bold green]Simulation Complete[/bold green]")
    _capture_simulation_summary(console, system)
    
    # Export console output to HTML
    html_content = console.export_html(
        theme=MONOKAI,
        inline_styles=True
    )
    
    # Save as HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def _capture_initial_actions(console: Console, initial_actions: List[Dict]) -> None:
    """Display initial actions from configuration."""
    for action in initial_actions:
        # Each action is a dict with one key (the action type)
        for action_type, params in action.items():
            if action_type == "mint_reserves":
                console.print(f"  🏦 Mint reserves: ${params['amount']:,} to {params['to']}", style="cyan")
            elif action_type == "mint_cash":
                console.print(f"  💰 Mint cash: ${params['amount']:,} to {params['to']}", style="green")
            elif action_type == "deposit_cash":
                console.print(f"  🏧 Deposit cash: {params['customer']} deposits ${params['amount']:,} at {params['bank']}", style="blue")
            elif action_type == "create_payable":
                due_text = f" (due Day {params['due_day']})" if 'due_day' in params else ""
                console.print(f"  📝 Create payable: {params['from']} owes {params['to']} ${params['amount']:,}{due_text}", style="magenta")
            else:
                # Generic display for unknown action types
                console.print(f"  📌 {action_type.replace('_', ' ').title()}: {params}")


def _capture_balances_from_snapshot(console: Console, initial_balances: Dict[str, Any], system: System) -> None:
    """Capture agent balances from a snapshot."""
    from rich.columns import Columns
    from rich.table import Table
    from rich import box
    
    agent_ids = list(initial_balances.keys())
    
    if len(agent_ids) == 1:
        # Single agent
        balance = initial_balances[agent_ids[0]]
        agent = system.state.agents[agent_ids[0]]
        
        # Get agent title
        if agent.name and agent.name != agent_ids[0]:
            title = f"{agent.name} [{agent_ids[0]}]\n({agent.kind})"
        else:
            title = f"{agent_ids[0]}\n({agent.kind})"
        
        # Create and display table
        table = _create_balance_table_for_console(title, balance)
        console.print(table)
    else:
        # Multiple agents - display side by side
        tables = []
        for agent_id in agent_ids:
            balance = initial_balances[agent_id]
            agent = system.state.agents[agent_id]
            
            # Get agent title
            if agent.name and agent.name != agent_id:
                title = f"{agent.name} [{agent_id}]\n({agent.kind})"
            else:
                title = f"{agent_id}\n({agent.kind})"
            
            # Create a table for this agent
            table = _create_balance_table_for_console(title, balance)
            tables.append(table)
        
        # Display tables side by side
        console.print(Columns(tables, padding=(0, 2), expand=False))


def _capture_balances(console: Console, system: System, agent_ids: List[str]) -> None:
    """Capture agent balances display."""
    from bilancio.analysis.balances import agent_balance
    from rich.columns import Columns
    from rich.table import Table
    from rich import box
    
    if len(agent_ids) == 1:
        # Single agent
        balance = agent_balance(system, agent_ids[0])
        agent = system.state.agents[agent_ids[0]]
        
        # Get agent title
        if agent.name and agent.name != agent_ids[0]:
            title = f"{agent.name} [{agent_ids[0]}]\n({agent.kind})"
        else:
            title = f"{agent_ids[0]}\n({agent.kind})"
        
        # Create and display table
        table = _create_balance_table_for_console(title, balance)
        console.print(table)
    else:
        # Multiple agents - display side by side
        tables = []
        for agent_id in agent_ids:
            balance = agent_balance(system, agent_id)
            agent = system.state.agents[agent_id]
            
            # Get agent title
            if agent.name and agent.name != agent_id:
                title = f"{agent.name} [{agent_id}]\n({agent.kind})"
            else:
                title = f"{agent_id}\n({agent.kind})"
            
            # Create a table for this agent
            table = _create_balance_table_for_console(title, balance)
            tables.append(table)
        
        # Display tables side by side
        console.print(Columns(tables, padding=(0, 2), expand=False))


def _capture_scenario_header(console: Console, name: str, description: Optional[str]) -> None:
    """Capture scenario header to console."""
    from rich.panel import Panel
    from rich.text import Text
    
    header = Text(name, style="bold cyan")
    if description:
        header.append(f"\n{description}", style="dim")
    
    console.print(Panel(
        header,
        title="Bilancio Scenario",
        border_style="cyan"
    ))


def _capture_day_summary(
    console: Console,
    system: System,
    agent_ids: Optional[List[str]],
    event_mode: str,
    day: int,
    day_events: Optional[List[Dict]] = None,
    day_balances: Optional[Dict[str, Any]] = None
) -> None:
    """Capture day summary to console."""
    from bilancio.analysis.visualization import (
        display_events,
        display_agent_balance_table,
        display_multiple_agent_balances
    )
    from bilancio.analysis.balances import system_trial_balance, agent_balance
    from rich.table import Table
    from rich.columns import Columns
    from rich import box
    from rich.text import Text
    
    # Show events
    events_to_show = day_events if day_events is not None else [
        e for e in system.state.events if e.get("day") == day
    ]
    
    if events_to_show:
        console.print("\n[bold]Events:[/bold]")
        if event_mode == "detailed":
            # Display events in detailed format
            _capture_events_to_console(console, events_to_show)
        else:
            # Summary mode
            event_counts = {}
            for event in events_to_show:
                event_type = event.get("kind", event.get("type", "Unknown"))
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            for event_type, count in sorted(event_counts.items()):
                console.print(f"  • {event_type}: {count}")
    
    # Show balances - use the snapshot if available, otherwise use current system state
    if day_balances:
        console.print("\n[bold]Balances:[/bold]")
        _capture_balances_from_snapshot(console, day_balances, system)
    elif agent_ids:
        console.print("\n[bold]Balances:[/bold]")
        if len(agent_ids) == 1:
            # Single agent - use the existing display function with our console
            balance = agent_balance(system, agent_ids[0])
            agent = system.state.agents[agent_ids[0]]
            
            # Get agent title
            if agent.name and agent.name != agent_ids[0]:
                title = f"{agent.name} [{agent_ids[0]}]\n({agent.kind})"
            else:
                title = f"{agent_ids[0]}\n({agent.kind})"
            
            # Create and display table
            table = _create_balance_table_for_console(title, balance)
            console.print(table)
        else:
            # Multiple agents - display side by side
            tables = []
            for agent_id in agent_ids:
                balance = agent_balance(system, agent_id)
                agent = system.state.agents[agent_id]
                
                # Get agent title
                if agent.name and agent.name != agent_id:
                    title = f"{agent.name} [{agent_id}]\n({agent.kind})"
                else:
                    title = f"{agent_id}\n({agent.kind})"
                
                # Create a table for this agent
                table = _create_balance_table_for_console(title, balance)
                tables.append(table)
            
            # Display tables side by side
            console.print(Columns(tables, padding=(0, 2), expand=False))
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


def _capture_events_to_console(console: Console, events: List[Dict]) -> None:
    """Capture events display to console with proper formatting."""
    from collections import defaultdict
    
    if not events:
        return
    
    # Don't group by day - we're already under a day section
    # Just group by simulation phase (setup, A, B, C)
    phase_groups = defaultdict(list)
    
    for event in events:
        event_phase = event.get('phase', '')
        event_kind = event.get('kind', event.get('type', ''))
        
        # Determine the phase group
        if event_phase == 'setup':
            phase = "Setup Phase"
        elif event_kind == 'PhaseA':
            phase = "Phase A"
        elif event_kind == 'PhaseB':
            phase = "Phase B"
        elif event_kind == 'PhaseC':
            phase = "Phase C"
        elif event_phase == 'simulation':
            # Determine phase based on event type
            if event_kind in ['ClientPayment', 'PayableSettled']:
                phase = "Phase B"
            elif event_kind in ['ReservesTransferred', 'InstrumentMerged', 'InterbankCleared']:
                phase = "Phase C"
            else:
                phase = "Phase A"
        else:
            phase = "Other"
        
        phase_groups[phase].append(event)
    
    # Display events grouped by phase
    phase_order = ["Setup Phase", "Phase A", "Phase B", "Phase C", "Other"]
    
    for phase in phase_order:
        if phase in phase_groups and phase_groups[phase]:
            phase_events = phase_groups[phase]
            
            # Only show phase headers if there are non-phase events
            has_content = any(e.get('kind') not in ['PhaseA', 'PhaseB', 'PhaseC'] for e in phase_events)
            
            if has_content:
                if phase == "Setup Phase":
                    console.print("\n  [bold yellow]🔧 Setup Phase:[/bold yellow]")
                elif phase == "Phase A":
                    console.print("\n  [bold yellow]⏰ Phase A: Day begins[/bold yellow]")
                elif phase == "Phase B":
                    console.print("\n  [bold green]💳 Phase B: Settlement[/bold green]")
                elif phase == "Phase C":
                    console.print("\n  [bold cyan]📋 Phase C: Intraday netting[/bold cyan]")
                
                # Display events, skipping the phase marker events
                for event in phase_events:
                    if event.get('kind') not in ['PhaseA', 'PhaseB', 'PhaseC']:
                        _display_single_event(console, event)


def _display_single_event(console: Console, event: Dict) -> None:
    """Display a single event with appropriate formatting."""
    # Check both 'kind' and 'type' fields for compatibility
    event_type = event.get("kind", event.get("type", "Unknown"))
    
    # Map event types to display formats (using the actual event kinds from the system)
    event_formats = {
        # Setup events
        "ReservesMinted": ("🏦", "cyan", "Reserves minted: ${amount} to {to}"),
        "CashMinted": ("💰", "green", "Cash minted: ${amount} to {to}"),
        "CashDeposited": ("🏧", "blue", "Cash deposited: {customer} → {bank}: ${amount}"),
        
        # Payment events
        "ClientPayment": ("💳", "magenta", "Client payment: {payer} ({payer_bank}) → {payee} ({payee_bank}): ${amount}"),
        "PayableSettled": ("✅", "green", "Payment settled: {debtor} → {creditor}: ${amount}"),
        
        # Interbank events
        "ReservesTransferred": ("💰", "yellow", "Reserves transferred: {frm} → {to}: ${amount}"),
        "InstrumentMerged": ("🔀", "dim", "Instruments merged"),
        "InterbankCleared": ("🏦", "cyan", "Interbank cleared: {debtor_bank} → {creditor_bank}: ${amount} (netted)"),
        
        # Phase events
        "PhaseA": ("⏰", "yellow", "Phase A: Day begins"),
        "PhaseB": ("💳", "green", "Phase B: Settlement (fulfilling due obligations)"),
        "PhaseC": ("📋", "cyan", "Phase C: Intraday netting"),
        
        # Legacy/alternative names
        "reserves_minted": ("🏦", "cyan", "Reserves minted: ${amount} to {to}"),
        "cash_minted": ("💰", "green", "Cash minted: ${amount} to {to}"),
        "cash_deposited": ("🏧", "blue", "Cash deposited: {from} → {to}: ${amount}"),
        "payment_initiated": ("💳", "magenta", "Client payment: {from} ({from_bank}) → {to} ({to_bank}): ${amount}"),
        "payment_settled": ("✅", "green", "Payment settled: {from} → {to}: ${amount}"),
        "reserves_transferred": ("💰", "yellow", "Reserves transferred: {from} → {to}: ${amount}"),
        "instruments_merged": ("🔀", "dim", "Instruments merged"),
        "interbank_cleared": ("🏦", "cyan", "Interbank cleared: {from} → {to}: ${amount} (netted)"),
        "begin_day": ("⏰", "yellow", "Phase A: Day begins"),
        "day_ended": ("🌙", "dim", "Day ended"),
    }
    
    if event_type in event_formats:
        emoji, color, template = event_formats[event_type]
        if template and not template.startswith("Phase"):  # Don't show template for phase events
            # Format the template with event data
            text = template
            for key, value in event.items():
                if key == "amount":
                    text = text.replace(f"${{{key}}}", f"${value}")
                else:
                    text = text.replace(f"{{{key}}}", str(value))
            console.print(f"    {emoji} {text}", style=color)
        elif template:  # Phase events - show as is
            console.print(f"    {emoji} {template}", style=color)
    else:
        # Generic event display
        details = ""
        if "from" in event and "to" in event:
            details = f" ({event['from']} → {event['to']})"
        elif "agent" in event:
            details = f" ({event['agent']})"
        
        console.print(f"    📌 {event_type.replace('_', ' ').title()}{details}")


def _create_balance_table_for_console(title: str, balance) -> "Table":
    """Create a balance sheet table for console display."""
    from rich.table import Table
    from rich.text import Text
    from rich import box
    
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan")
    table.add_column("Item", style="white", width=25)
    table.add_column("Amount", justify="right", style="white", width=15)
    
    # Add assets section
    table.add_row(Text("ASSETS", style="bold green"), "")
    
    # Add financial assets
    for asset_type in sorted(balance.assets_by_kind.keys()):
        if balance.assets_by_kind[asset_type] > 0:
            table.add_row(
                Text(asset_type, style="green"),
                Text(f"{balance.assets_by_kind[asset_type]:,}", style="green")
            )
    
    table.add_row("", "", end_section=True)
    
    # Add liabilities section
    table.add_row(Text("LIABILITIES", style="bold red"), "")
    
    # Add financial liabilities
    for liability_type in sorted(balance.liabilities_by_kind.keys()):
        if balance.liabilities_by_kind[liability_type] > 0:
            table.add_row(
                Text(liability_type, style="red"),
                Text(f"{balance.liabilities_by_kind[liability_type]:,}", style="red")
            )
    
    table.add_row("", "", end_section=True)
    
    # Add totals
    table.add_row(
        Text("Total Financial", style="bold green"),
        Text(f"{balance.total_financial_assets:,}", style="bold green")
    )
    table.add_row(
        Text("Total Liab.", style="bold red"),
        Text(f"{balance.total_financial_liabilities:,}", style="bold red")
    )
    
    net_financial = balance.net_financial
    net_style = "bold green" if net_financial >= 0 else "bold red"
    table.add_row(
        Text("Net Financial", style="bold blue"),
        Text(f"{net_financial:+,}", style=net_style)
    )
    
    return table


def _capture_simulation_summary(console: Console, system: System) -> None:
    """Capture simulation summary to console."""
    from rich.panel import Panel
    
    console.print(Panel(
        f"[bold]Summary[/bold]\n"
        f"Final Day: {system.state.day}\n"
        f"Total Events: {len(system.state.events)}\n"
        f"Active Agents: {len(system.state.agents)}\n"
        f"Active Contracts: {len(system.state.contracts)}\n"
        f"Stock Lots: {len(system.state.stocks)}",
        title="Final State",
        border_style="green"
    ))