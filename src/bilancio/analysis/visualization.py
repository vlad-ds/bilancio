"""Balance sheet visualization utilities for the bilancio system."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Union

try:
    from rich.console import Console
    from rich.table import Table
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from bilancio.analysis.balances import AgentBalance, agent_balance
from bilancio.engines.system import System


def _format_currency(amount: int, show_sign: bool = False) -> str:
    """Format an integer amount as currency."""
    formatted = f"{amount:,}"
    if show_sign and amount > 0:
        formatted = f"+{formatted}"
    return formatted


def display_agent_balance_table(
    system: System,
    agent_id: str,
    format: str = 'rich',
    title: Optional[str] = None
) -> None:
    """
    Display a single agent's balance sheet as a T-account style table.
    
    Args:
        system: The bilancio system instance
        agent_id: ID of the agent to display
        format: Display format ('rich' or 'simple')
        title: Optional custom title for the table
    """
    if format == 'rich' and not RICH_AVAILABLE:
        print("Warning: rich library not available, falling back to simple format")
        format = 'simple'
    
    # Get agent balance
    balance = agent_balance(system, agent_id)
    
    # Get agent info
    agent = system.state.agents[agent_id]
    if title is None:
        title = f"{agent.name or agent_id} ({agent.kind})"
    
    if format == 'rich':
        _display_rich_agent_balance(title, balance)
    else:
        _display_simple_agent_balance(title, balance)


def display_agent_balance_from_balance(
    balance: AgentBalance,
    format: str = 'rich',
    title: Optional[str] = None
) -> None:
    """
    Display an agent's balance sheet from an AgentBalance object.
    
    Args:
        balance: The AgentBalance object to display
        format: Display format ('rich' or 'simple')
        title: Optional custom title for the table
    """
    if format == 'rich' and not RICH_AVAILABLE:
        print("Warning: rich library not available, falling back to simple format")
        format = 'simple'
    
    if title is None:
        title = f"Agent {balance.agent_id}"
    
    if format == 'rich':
        _display_rich_agent_balance(title, balance)
    else:
        _display_simple_agent_balance(title, balance)


def display_multiple_agent_balances(
    system: System,
    items: List[Union[str, AgentBalance]], 
    format: str = 'rich'
) -> None:
    """
    Display multiple agent balance sheets side by side for comparison.
    
    Args:
        system: The bilancio system instance
        items: List of agent IDs (str) or AgentBalance instances
        format: Display format ('rich' or 'simple')
    """
    if format == 'rich' and not RICH_AVAILABLE:
        print("Warning: rich library not available, falling back to simple format")
        format = 'simple'
    
    # Convert agent IDs to balance objects if needed
    balances = []
    for item in items:
        if isinstance(item, str):
            balances.append(agent_balance(system, item))
        else:
            balances.append(item)
    
    if format == 'rich':
        _display_rich_multiple_agent_balances(balances, system)
    else:
        _display_simple_multiple_agent_balances(balances, system)


def _display_rich_agent_balance(title: str, balance: AgentBalance) -> None:
    """Display a single agent balance using rich formatting."""
    console = Console()
    
    # Create the main table
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan")
    table.add_column("ASSETS", style="green", width=25)
    table.add_column("Amount", justify="right", style="green", width=12)
    table.add_column("LIABILITIES", style="red", width=25)
    table.add_column("Amount", justify="right", style="red", width=12)
    
    # Get all asset and liability types, sorted
    asset_types = sorted(balance.assets_by_kind.keys())
    liability_types = sorted(balance.liabilities_by_kind.keys())
    
    # Determine the maximum number of rows needed
    max_rows = max(len(asset_types), len(liability_types), 1)
    
    for i in range(max_rows):
        asset_name = asset_types[i] if i < len(asset_types) else ""
        asset_amount = _format_currency(balance.assets_by_kind[asset_name]) if asset_name else ""
        
        liability_name = liability_types[i] if i < len(liability_types) else ""
        liability_amount = _format_currency(balance.liabilities_by_kind[liability_name]) if liability_name else ""
        
        table.add_row(asset_name, asset_amount, liability_name, liability_amount)
    
    # Add separator and totals
    table.add_row("", "", "", "", end_section=True)
    table.add_row(
        Text("TOTAL FINANCIAL", style="bold green"),
        Text(_format_currency(balance.total_financial_assets), style="bold green"),
        Text("TOTAL FINANCIAL", style="bold red"),
        Text(_format_currency(balance.total_financial_liabilities), style="bold red")
    )
    
    # Add visual separation before net worth
    table.add_row("", "", "", "", end_section=True)
    
    # Add net worth with clear separation
    net_financial = balance.net_financial
    net_worth_style = "bold green" if net_financial >= 0 else "bold red"
    table.add_row(
        "",
        "",
        Text("NET FINANCIAL", style="bold blue"),
        Text(_format_currency(net_financial, show_sign=True), style=net_worth_style)
    )
    
    console.print(table)


def _display_simple_agent_balance(title: str, balance: AgentBalance) -> None:
    """Display a single agent balance using simple text formatting."""
    print(f"\n{title}")
    print("=" * 60)
    print(f"{'ASSETS':<25} {'Amount':>12} | {'LIABILITIES':<25} {'Amount':>12}")
    print("-" * 60)
    
    # Get all asset and liability types, sorted
    asset_types = sorted(balance.assets_by_kind.keys())
    liability_types = sorted(balance.liabilities_by_kind.keys())
    
    # Determine the maximum number of rows needed
    max_rows = max(len(asset_types), len(liability_types), 1)
    
    for i in range(max_rows):
        asset_name = asset_types[i] if i < len(asset_types) else ""
        asset_amount = _format_currency(balance.assets_by_kind[asset_name]) if asset_name else ""
        
        liability_name = liability_types[i] if i < len(liability_types) else ""
        liability_amount = _format_currency(balance.liabilities_by_kind[liability_name]) if liability_name else ""
        
        print(f"{asset_name:<25} {asset_amount:>12} | {liability_name:<25} {liability_amount:>12}")
    
    print("-" * 60)
    print(f"{'TOTAL FINANCIAL':<25} {_format_currency(balance.total_financial_assets):>12} | "
          f"{'TOTAL FINANCIAL':<25} {_format_currency(balance.total_financial_liabilities):>12}")
    print("-" * 60)
    print(f"{'':>39} | {'NET FINANCIAL':<25} {_format_currency(balance.net_financial, show_sign=True):>12}")


def _display_rich_multiple_agent_balances(
    balances: List[AgentBalance], 
    system: Optional[System] = None
) -> None:
    """Display multiple agent balances side by side using rich formatting."""
    console = Console()
    
    # Create individual tables for each balance
    tables = []
    for balance in balances:
        # Get agent name if system is available
        if system and balance.agent_id in system.state.agents:
            agent = system.state.agents[balance.agent_id]
            title = f"{agent.name or balance.agent_id}\n({agent.kind})"
        else:
            title = f"{balance.agent_id}"
        
        # Create table for this balance sheet
        table = Table(title=title, box=box.ROUNDED, title_style="bold cyan", width=30)
        table.add_column("Item", style="white", width=15)
        table.add_column("Amount", justify="right", style="white", width=10)
        
        # Add assets
        table.add_row(Text("ASSETS", style="bold green underline"), "")
        for asset_type in sorted(balance.assets_by_kind.keys()):
            table.add_row(
                Text(asset_type, style="green"),
                Text(_format_currency(balance.assets_by_kind[asset_type]), style="green")
            )
        
        table.add_row("", "", end_section=True)
        
        # Add liabilities
        table.add_row(Text("LIABILITIES", style="bold red underline"), "")
        for liability_type in sorted(balance.liabilities_by_kind.keys()):
            table.add_row(
                Text(liability_type, style="red"),
                Text(_format_currency(balance.liabilities_by_kind[liability_type]), style="red")
            )
        
        # Add totals and net worth
        table.add_row("", "", end_section=True)
        table.add_row(
            Text("Total Financial", style="bold green"),
            Text(_format_currency(balance.total_financial_assets), style="bold green")
        )
        table.add_row(
            Text("Total Liab.", style="bold red"),
            Text(_format_currency(balance.total_financial_liabilities), style="bold red")
        )
        
        net_worth_style = "bold green" if balance.net_financial >= 0 else "bold red"
        table.add_row(
            Text("Net Financial", style="bold blue"),
            Text(_format_currency(balance.net_financial, show_sign=True), style=net_worth_style)
        )
        
        tables.append(table)
    
    # Display tables in columns
    console.print(Columns(tables, equal=True, expand=True))


def _display_simple_multiple_agent_balances(
    balances: List[AgentBalance], 
    system: Optional[System] = None
) -> None:
    """Display multiple agent balances side by side using simple text formatting."""
    # Calculate column width based on number of balance sheets
    console_width = 120
    col_width = max(25, console_width // len(balances) - 2)
    
    # Create headers
    headers = []
    separators = []
    for balance in balances:
        if system and balance.agent_id in system.state.agents:
            agent = system.state.agents[balance.agent_id]
            header = f"{agent.name or balance.agent_id} ({agent.kind})"
        else:
            header = balance.agent_id
        
        if len(header) > col_width:
            header = header[:col_width-3] + "..."
        headers.append(header.center(col_width))
        separators.append("-" * col_width)
    
    print("\n" + " | ".join(headers))
    print(" | ".join(separators))
    
    # Collect all data for each balance sheet
    balance_data = []
    max_rows = 0
    
    for balance in balances:
        data = []
        data.append(("ASSETS", ""))
        
        for asset_type in sorted(balance.assets_by_kind.keys()):
            amount = _format_currency(balance.assets_by_kind[asset_type])
            if len(asset_type + " " + amount) > col_width:
                asset_type = asset_type[:col_width-len(amount)-4] + "..."
            data.append((asset_type, amount))
        
        data.append(("", ""))
        data.append(("LIABILITIES", ""))
        
        for liability_type in sorted(balance.liabilities_by_kind.keys()):
            amount = _format_currency(balance.liabilities_by_kind[liability_type])
            if len(liability_type + " " + amount) > col_width:
                liability_type = liability_type[:col_width-len(amount)-4] + "..."
            data.append((liability_type, amount))
        
        data.append(("", ""))
        data.append(("Total Financial", _format_currency(balance.total_financial_assets)))
        data.append(("Total Liab.", _format_currency(balance.total_financial_liabilities)))
        data.append(("Net Financial", _format_currency(balance.net_financial, show_sign=True)))
        
        balance_data.append(data)
        max_rows = max(max_rows, len(data))
    
    # Print rows
    for row_idx in range(max_rows):
        row_parts = []
        for balance_idx, data in enumerate(balance_data):
            if row_idx < len(data):
                item, amount = data[row_idx]
                if amount:
                    line = f"{item} {amount}".rjust(col_width)
                else:
                    line = item.ljust(col_width)
            else:
                line = " " * col_width
            row_parts.append(line)
        
        print(" | ".join(row_parts))