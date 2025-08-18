"""Balance sheet visualization utilities for the bilancio system."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

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


def _format_deliverable_amount(valued_amount: Decimal) -> str:
    """Format deliverable monetary value."""
    # Convert Decimal to int for currency formatting (assuming cents precision)
    return _format_currency(int(valued_amount))


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
        # Show both name and ID for clarity
        if agent.name and agent.name != agent_id:
            title = f"{agent.name} [{agent_id}] ({agent.kind})"
        else:
            title = f"{agent_id} ({agent.kind})"
    
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
    
    # Create the main table with wider columns to avoid truncation
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan")
    table.add_column("ASSETS", style="green", width=35, no_wrap=False)
    table.add_column("Amount", justify="right", style="green", width=15, no_wrap=True)
    table.add_column("LIABILITIES", style="red", width=35, no_wrap=False)
    table.add_column("Amount", justify="right", style="red", width=15, no_wrap=True)
    
    asset_rows = []
    
    # First: Add inventory (stocks owned) - these are physical assets
    if hasattr(balance, 'inventory_by_sku'):
        for sku, data in balance.inventory_by_sku.items():
            qty = data['quantity']
            if qty > 0:
                name = f"{sku} [{qty} unit{'s' if qty != 1 else ''}]"
                amount = _format_currency(int(data['value']))
                asset_rows.append((name, amount))
    
    # Second: Add non-financial assets (rights to receive goods)
    # Track which SKUs we've already displayed
    displayed_asset_skus = set()
    for sku, data in balance.nonfinancial_assets_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} receivable [{qty} unit{'s' if qty != 1 else ''}]"
            amount = _format_currency(int(data['value']))
            asset_rows.append((name, amount))
            displayed_asset_skus.add(sku)
    
    # Third: Add financial assets (everything else in assets_by_kind)
    # These are guaranteed to be financial since non-financial are already handled
    financial_asset_kinds = set()
    for asset_type in sorted(balance.assets_by_kind.keys()):
        # Skip if this is a non-financial type we already displayed
        # We identify non-financial by checking if its SKU was in nonfinancial_assets_by_kind
        is_nonfinancial = False
        for sku in displayed_asset_skus:
            # This is a heuristic but works for current instrument types
            if asset_type in ['deliverable', 'delivery_obligation']:
                is_nonfinancial = True
                break
        
        if not is_nonfinancial and asset_type not in financial_asset_kinds:
            name = asset_type
            amount = _format_currency(balance.assets_by_kind[asset_type])
            asset_rows.append((name, amount))
            financial_asset_kinds.add(asset_type)
    
    liability_rows = []
    
    # First: Add non-financial liabilities (obligations to deliver goods)
    displayed_liability_skus = set()
    for sku, data in balance.nonfinancial_liabilities_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} obligation [{qty} unit{'s' if qty != 1 else ''}]"
            amount = _format_currency(int(data['value']))
            liability_rows.append((name, amount))
            displayed_liability_skus.add(sku)
    
    # Second: Add financial liabilities (everything else in liabilities_by_kind)
    financial_liability_kinds = set()
    for liability_type in sorted(balance.liabilities_by_kind.keys()):
        # Skip if this is a non-financial type we already displayed
        is_nonfinancial = False
        for sku in displayed_liability_skus:
            if liability_type in ['deliverable', 'delivery_obligation']:
                is_nonfinancial = True
                break
        
        if not is_nonfinancial and liability_type not in financial_liability_kinds:
            name = liability_type
            amount = _format_currency(balance.liabilities_by_kind[liability_type])
            liability_rows.append((name, amount))
            financial_liability_kinds.add(liability_type)
    
    # Determine the maximum number of rows needed
    max_rows = max(len(asset_rows), len(liability_rows), 1)
    
    for i in range(max_rows):
        asset_name, asset_amount = asset_rows[i] if i < len(asset_rows) else ("", "")
        liability_name, liability_amount = liability_rows[i] if i < len(liability_rows) else ("", "")
        
        table.add_row(asset_name, asset_amount, liability_name, liability_amount)
    
    # Add separator and totals
    table.add_row("", "", "", "", end_section=True)
    table.add_row(
        Text("TOTAL FINANCIAL", style="bold green"),
        Text(_format_currency(balance.total_financial_assets), style="bold green"),
        Text("TOTAL FINANCIAL", style="bold red"),
        Text(_format_currency(balance.total_financial_liabilities), style="bold red")
    )
    
    # Add valued non-financial total if present
    if balance.total_nonfinancial_value is not None and balance.total_nonfinancial_value > 0:
        table.add_row(
            Text("TOTAL VALUED DELIV.", style="bold green"),
            Text(_format_currency(int(balance.total_nonfinancial_value)), style="bold green"),
            "",
            ""
        )
        total_assets = balance.total_financial_assets + int(balance.total_nonfinancial_value)
        table.add_row(
            Text("TOTAL ASSETS", style="bold green"),
            Text(_format_currency(total_assets), style="bold green"),
            "",
            ""
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
    print("=" * 70)
    print(f"{'ASSETS':<30} {'Amount':>12} | {'LIABILITIES':<30} {'Amount':>12}")
    print("-" * 70)
    
    asset_rows = []
    
    # First: Add inventory (stocks owned)
    if hasattr(balance, 'inventory_by_sku'):
        for sku, data in balance.inventory_by_sku.items():
            qty = data['quantity']
            if qty > 0:
                name = f"{sku} [{qty} unit{'s' if qty != 1 else ''}]"
                if len(name) > 29:
                    name = name[:26] + "..."
                amount = _format_currency(int(data['value']))
                asset_rows.append((name, amount))
    
    # Second: Add non-financial assets (rights to receive goods)
    displayed_asset_skus = set()
    for sku, data in balance.nonfinancial_assets_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} receivable [{qty} unit{'s' if qty != 1 else ''}]"
            if len(name) > 29:
                name = name[:26] + "..."
            amount = _format_currency(int(data['value']))
            asset_rows.append((name, amount))
            displayed_asset_skus.add(sku)
    
    # Third: Add financial assets
    financial_asset_kinds = set()
    for asset_type in sorted(balance.assets_by_kind.keys()):
        # Skip non-financial types
        is_nonfinancial = asset_type in ['deliverable', 'delivery_obligation']
        
        if not is_nonfinancial and asset_type not in financial_asset_kinds:
            name = asset_type
            if len(name) > 29:
                name = name[:26] + "..."
            amount = _format_currency(balance.assets_by_kind[asset_type])
            asset_rows.append((name, amount))
            financial_asset_kinds.add(asset_type)
    
    liability_rows = []
    
    # First: Add non-financial liabilities (obligations to deliver goods)
    displayed_liability_skus = set()
    for sku, data in balance.nonfinancial_liabilities_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} obligation [{qty} unit{'s' if qty != 1 else ''}]"
            if len(name) > 29:
                name = name[:26] + "..."
            amount = _format_currency(int(data['value']))
            liability_rows.append((name, amount))
            displayed_liability_skus.add(sku)
    
    # Second: Add financial liabilities
    financial_liability_kinds = set()
    for liability_type in sorted(balance.liabilities_by_kind.keys()):
        # Skip non-financial types
        is_nonfinancial = liability_type in ['deliverable', 'delivery_obligation']
        
        if not is_nonfinancial and liability_type not in financial_liability_kinds:
            name = liability_type
            if len(name) > 29:
                name = name[:26] + "..."
            amount = _format_currency(balance.liabilities_by_kind[liability_type])
            liability_rows.append((name, amount))
            financial_liability_kinds.add(liability_type)
    
    # Determine the maximum number of rows needed
    max_rows = max(len(asset_rows), len(liability_rows), 1)
    
    for i in range(max_rows):
        asset_name, asset_amount = asset_rows[i] if i < len(asset_rows) else ("", "")
        liability_name, liability_amount = liability_rows[i] if i < len(liability_rows) else ("", "")
        
        print(f"{asset_name:<30} {asset_amount:>12} | {liability_name:<30} {liability_amount:>12}")
    
    print("-" * 70)
    print(f"{'TOTAL FINANCIAL':<30} {_format_currency(balance.total_financial_assets):>12} | "
          f"{'TOTAL FINANCIAL':<30} {_format_currency(balance.total_financial_liabilities):>12}")
    
    # Add valued non-financial total if present
    if balance.total_nonfinancial_value is not None and balance.total_nonfinancial_value > 0:
        print(f"{'TOTAL VALUED DELIV.':<30} {_format_currency(int(balance.total_nonfinancial_value)):>12} | {'':>43}")
        total_assets = balance.total_financial_assets + int(balance.total_nonfinancial_value)
        print(f"{'TOTAL ASSETS':<30} {_format_currency(total_assets):>12} | {'':>43}")
    
    print("-" * 70)
    print(f"{'':>44} | {'NET FINANCIAL':<30} {_format_currency(balance.net_financial, show_sign=True):>12}")


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
            # Show both name and ID for clarity
            if agent.name and agent.name != balance.agent_id:
                title = f"{agent.name} [{balance.agent_id}]\n({agent.kind})"
            else:
                title = f"{balance.agent_id}\n({agent.kind})"
        else:
            title = f"{balance.agent_id}"
        
        # Create table for this balance sheet
        table = Table(title=title, box=box.ROUNDED, title_style="bold cyan", width=35)
        table.add_column("Item", style="white", width=20)
        table.add_column("Amount", justify="right", style="white", width=12)
        
        # Add assets
        table.add_row(Text("ASSETS", style="bold green underline"), "")
        
        # First: Add inventory (stocks owned)
        if hasattr(balance, 'inventory_by_sku'):
            for sku, data in balance.inventory_by_sku.items():
                qty = data['quantity']
                if qty > 0:
                    name = f"{sku} [{qty}]"
                    if len(name) > 19:
                        name = name[:16] + "..."
                    amount = _format_currency(int(data['value']))
                    table.add_row(
                        Text(name, style="green"),
                        Text(amount, style="green")
                    )
        
        # Second: Add non-financial assets (rights to receive goods)
        displayed_asset_skus = set()
        for sku, data in balance.nonfinancial_assets_by_kind.items():
            qty = data['quantity']
            if qty > 0:
                name = f"{sku} recv [{qty}]"
                if len(name) > 19:
                    name = name[:16] + "..."
                amount = _format_currency(int(data['value']))
                table.add_row(
                    Text(name, style="green"),
                    Text(amount, style="green")
                )
                displayed_asset_skus.add(sku)
        
        # Third: Add financial assets
        for asset_type in sorted(balance.assets_by_kind.keys()):
            # Skip non-financial types
            if asset_type not in ['deliverable', 'delivery_obligation']:
                name = asset_type
                if len(name) > 19:
                    name = name[:16] + "..."
                table.add_row(
                    Text(name, style="green"),
                    Text(_format_currency(balance.assets_by_kind[asset_type]), style="green")
                )
        
        table.add_row("", "", end_section=True)
        
        # Add liabilities
        table.add_row(Text("LIABILITIES", style="bold red underline"), "")
        
        # First: Add non-financial liabilities (obligations to deliver goods)
        for sku, data in balance.nonfinancial_liabilities_by_kind.items():
            qty = data['quantity']
            if qty > 0:
                name = f"{sku} oblig [{qty}]"
                if len(name) > 19:
                    name = name[:16] + "..."
                amount = _format_currency(int(data['value']))
                table.add_row(
                    Text(name, style="red"),
                    Text(amount, style="red")
                )
        
        # Second: Add financial liabilities
        for liability_type in sorted(balance.liabilities_by_kind.keys()):
            # Skip non-financial types
            if liability_type not in ['deliverable', 'delivery_obligation']:
                name = liability_type
                if len(name) > 19:
                    name = name[:16] + "..."
                table.add_row(
                    Text(name, style="red"),
                    Text(_format_currency(balance.liabilities_by_kind[liability_type]), style="red")
                )
        
        # Add totals and net worth
        table.add_row("", "", end_section=True)
        table.add_row(
            Text("Total Financial", style="bold green"),
            Text(_format_currency(balance.total_financial_assets), style="bold green")
        )
        
        # Add valued deliverables total if present
        if balance.total_nonfinancial_value is not None and balance.total_nonfinancial_value > 0:
            table.add_row(
                Text("Total Valued", style="bold green"),
                Text(_format_currency(int(balance.total_nonfinancial_value)), style="bold green")
            )
            total_assets = balance.total_financial_assets + int(balance.total_nonfinancial_value)
            table.add_row(
                Text("Total Assets", style="bold green"),
                Text(_format_currency(total_assets), style="bold green")
            )
        
        # Add total liabilities (financial + valued non-financial)
        if balance.total_nonfinancial_liability_value is not None and balance.total_nonfinancial_liability_value > 0:
            table.add_row(
                Text("Total Fin. Liab.", style="bold red"),
                Text(_format_currency(balance.total_financial_liabilities), style="bold red")
            )
            table.add_row(
                Text("Total Valued Liab.", style="bold red"),
                Text(_format_currency(int(balance.total_nonfinancial_liability_value)), style="bold red")
            )
            total_liab = balance.total_financial_liabilities + int(balance.total_nonfinancial_liability_value)
            table.add_row(
                Text("Total Liab.", style="bold red"),
                Text(_format_currency(total_liab), style="bold red")
            )
        else:
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
        
        # First: Add inventory (stocks owned)
        if hasattr(balance, 'inventory_by_sku'):
            for sku, inv_data in balance.inventory_by_sku.items():
                qty = inv_data['quantity']
                if qty > 0:
                    name = f"{sku} [{qty}]"
                    amount = _format_currency(int(inv_data['value']))
                    if len(name + " " + amount) > col_width:
                        name = name[:col_width-len(amount)-4] + "..."
                    data.append((name, amount))
        
        # Second: Add non-financial assets (rights to receive goods)
        for sku, asset_data in balance.nonfinancial_assets_by_kind.items():
            qty = asset_data['quantity']
            if qty > 0:
                name = f"{sku} recv [{qty}]"
                amount = _format_currency(int(asset_data['value']))
                if len(name + " " + amount) > col_width:
                    name = name[:col_width-len(amount)-4] + "..."
                data.append((name, amount))
        
        # Third: Add financial assets
        for asset_type in sorted(balance.assets_by_kind.keys()):
            # Skip non-financial types
            if asset_type not in ['deliverable', 'delivery_obligation']:
                amount = _format_currency(balance.assets_by_kind[asset_type])
                asset_name = asset_type
                if len(asset_name + " " + amount) > col_width:
                    asset_name = asset_name[:col_width-len(amount)-4] + "..."
                data.append((asset_name, amount))
        
        data.append(("", ""))
        data.append(("LIABILITIES", ""))
        
        # First: Add non-financial liabilities (obligations to deliver goods)
        for sku, liability_data in balance.nonfinancial_liabilities_by_kind.items():
            qty = liability_data['quantity']
            if qty > 0:
                name = f"{sku} oblig [{qty}]"
                amount = _format_currency(int(liability_data['value']))
                if len(name + " " + amount) > col_width:
                    name = name[:col_width-len(amount)-4] + "..."
                data.append((name, amount))
        
        # Second: Add financial liabilities
        for liability_type in sorted(balance.liabilities_by_kind.keys()):
            # Skip non-financial types
            if liability_type not in ['deliverable', 'delivery_obligation']:
                amount = _format_currency(balance.liabilities_by_kind[liability_type])
                liability_name = liability_type
                if len(liability_name + " " + amount) > col_width:
                    liability_name = liability_name[:col_width-len(amount)-4] + "..."
                data.append((liability_name, amount))
        
        data.append(("", ""))
        data.append(("Total Financial", _format_currency(balance.total_financial_assets)))
        
        # Add valued deliverables total if present
        if balance.total_nonfinancial_value is not None and balance.total_nonfinancial_value > 0:
            data.append(("Total Valued", _format_currency(int(balance.total_nonfinancial_value))))
            total_assets = balance.total_financial_assets + int(balance.total_nonfinancial_value)
            data.append(("Total Assets", _format_currency(total_assets)))
        
        # Add total liabilities
        if balance.total_nonfinancial_liability_value is not None and balance.total_nonfinancial_liability_value > 0:
            data.append(("Total Valued Liab.", _format_currency(int(balance.total_nonfinancial_liability_value))))
            total_liab = balance.total_financial_liabilities + int(balance.total_nonfinancial_liability_value)
            data.append(("Total Liab.", _format_currency(total_liab)))
        else:
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


def display_events(events: List[Dict[str, Any]], format: str = 'detailed') -> None:
    """
    Display system events in a nicely formatted way.
    
    Args:
        events: List of event dictionaries from sys.state.events
        format: Display format ('detailed' or 'summary')
    """
    console = Console() if RICH_AVAILABLE else None
    
    if not events:
        _print("No events to display.", console)
        return
    
    if format == 'summary':
        _display_events_summary(events, console)
    else:
        _display_events_detailed(events, console)


def _print(text: str, console: Optional['Console'] = None) -> None:
    """Print using Rich console if available, otherwise regular print."""
    if console:
        console.print(text)
    else:
        print(text)


def _display_events_summary(events: List[Dict[str, Any]], console: Optional['Console'] = None) -> None:
    """Display events in a condensed summary format."""
    for event in events:
        kind = event.get("kind", "Unknown")
        day = event.get("day", "?")
        
        if kind == "PayableSettled":
            _print(f"Day {day}: 💰 {event['debtor']} → {event['creditor']}: ${event['amount']}", console)
        elif kind == "DeliveryObligationSettled":
            qty = event.get('qty', event.get('quantity', 'N/A'))
            _print(f"Day {day}: 📦 {event['debtor']} → {event['creditor']}: {qty} {event.get('sku', 'items')}", console)
        elif kind == "StockTransferred":
            _print(f"Day {day}: 🚚 {event['frm']} → {event['to']}: {event['qty']} {event['sku']}", console)
        elif kind == "CashTransferred":
            _print(f"Day {day}: 💵 {event['frm']} → {event['to']}: ${event['amount']}", console)


def _display_events_detailed(events: List[Dict[str, Any]], console: Optional['Console'] = None) -> None:
    """Display events grouped by day with detailed formatting."""
    # Separate setup events from day events
    setup_events = []
    events_by_day = defaultdict(list)
    
    for event in events:
        # Check if this is a setup phase event
        if event.get("phase") == "setup":
            setup_events.append(event)
        else:
            day = event.get("day", -1)
            events_by_day[day].append(event)
    
    # Display setup events first if any
    if setup_events:
        _print(f"\n📅 Setup Phase:", console)
        # Setup events don't have phase markers, display them directly
        for event in setup_events:
            _display_single_event(event, console, indent="  ")
    
    # Display events for each day
    for day in sorted(events_by_day.keys()):
        if day >= 0:
            _print(f"\n📅 Day {day}:", console)
        else:
            _print(f"\n📅 Unknown Day:", console)
        
        _display_day_events(events_by_day[day], console)


def _display_day_events(day_events: List[Dict[str, Any]], console: Optional['Console'] = None) -> None:
    """Display events for a single day with proper formatting."""
    # Group events by their phase timing
    phase_a_events = []
    phase_b_events = []
    phase_c_events = []
    
    # Track which phase we're in based on phase markers
    current_phase = "A"  # Start with phase A
    
    for event in day_events:
        kind = event.get("kind", "Unknown")
        
        # Phase markers change which phase we're in
        if kind == "PhaseA":
            current_phase = "A"
        elif kind == "PhaseB":
            current_phase = "B"
        elif kind == "PhaseC":
            current_phase = "C"
        else:
            # Regular events go into the current phase bucket
            if current_phase == "A":
                phase_a_events.append(event)
            elif current_phase == "B":
                phase_b_events.append(event)
            elif current_phase == "C":
                phase_c_events.append(event)
    
    # Always display all three phases
    # Phase A - No-op phase, just marks beginning of day
    _print(f"\n  ⏰ Phase A: Day begins", console)
    for event in phase_a_events:
        _display_single_event(event, console, indent="    ")
    
    # Phase B - Settlement phase where obligations are fulfilled
    _print(f"\n  💳 Phase B: Settlement (fulfilling due obligations)", console)
    for event in phase_b_events:
        _display_single_event(event, console, indent="    ")
    
    # Phase C - Intraday netting
    _print(f"\n  📋 Phase C: Intraday netting", console)
    for event in phase_c_events:
        _display_single_event(event, console, indent="    ")
    
    # Mark end of day
    _print(f"\n  🌙 Day ended", console)


def _display_single_event(event: Dict[str, Any], console: Optional['Console'] = None, indent: str = "  ") -> None:
    """Display a single event with proper formatting."""
    kind = event.get("kind", "Unknown")
    
    if kind == "StockCreated":
        _print(f"{indent}🏭 Stock created: {event['owner']} gets {event['qty']} {event['sku']}", console)
    
    elif kind == "CashMinted":
        _print(f"{indent}💰 Cash minted: ${event['amount']} to {event['to']}", console)
    
    elif kind == "PayableSettled":
        _print(f"{indent}✅ Payment settled: {event['debtor']} → {event['creditor']}: ${event['amount']}", console)
    
    elif kind == "PayableCancelled":
        _print(f"{indent}  └─ Payment obligation removed from books", console)
    
    elif kind == "DeliveryObligationSettled":
        qty = event.get('qty', event.get('quantity', 'N/A'))
        sku = event.get('sku', 'items')
        _print(f"{indent}✅ Delivery settled: {event['debtor']} → {event['creditor']}: {qty} {sku}", console)
    
    elif kind == "DeliveryObligationCancelled":
        _print(f"{indent}  └─ Delivery obligation removed from books", console)
    
    elif kind == "StockTransferred":
        _print(f"{indent}📦 Stock transferred: {event['frm']} → {event['to']}: {event['qty']} {event['sku']}", console)
    
    elif kind == "CashTransferred":
        _print(f"{indent}💵 Cash transferred: {event['frm']} → {event['to']}: ${event['amount']}", console)
    
    elif kind == "StockSplit":
        sku = event.get('sku', 'N/A')
        original_qty = event.get('original_qty', 0)
        split_qty = event.get('split_qty', 0)
        remaining_qty = event.get('remaining_qty', 0)
        # Show shortened IDs for readability
        original_id = event.get('original_id', '')
        new_id = event.get('new_id', '')
        short_orig = original_id.split('_')[-1][:8] if original_id else 'N/A'
        short_new = new_id.split('_')[-1][:8] if new_id else 'N/A'
        _print(f"{indent}📊 Stock split: {short_orig} → {short_new}: {split_qty} {sku} (keeping {remaining_qty})", console)
    
    elif kind == "ReservesMinted":
        amount = event.get('amount', 0)
        to = event.get('to', 'N/A')
        _print(f"{indent}🏦 Reserves minted: ${amount} to {to}", console)
    
    elif kind == "CashDeposited":
        customer = event.get('customer', 'N/A')
        bank = event.get('bank', 'N/A')
        amount = event.get('amount', 0)
        _print(f"{indent}🏧 Cash deposited: {customer} → {bank}: ${amount}", console)
    
    elif kind == "DeliveryObligationCreated":
        frm = event.get('frm', event.get('from', 'N/A'))
        to = event.get('to', 'N/A')
        qty = event.get('qty', event.get('quantity', 0))
        sku = event.get('sku', 'N/A')
        due_day = event.get('due_day', 'N/A')
        _print(f"{indent}📝 Delivery obligation created: {frm} → {to}: {qty} {sku} (due day {due_day})", console)
    
    elif kind == "PayableCreated":
        frm = event.get('frm', event.get('from', event.get('debtor', 'N/A')))
        to = event.get('to', event.get('creditor', 'N/A'))
        amount = event.get('amount', 0)
        due_day = event.get('due_day', 'N/A')
        _print(f"{indent}💸 Payable created: {frm} → {to}: ${amount} (due day {due_day})", console)
    
    elif kind == "ClientPayment":
        payer = event.get('payer', 'N/A')
        payee = event.get('payee', 'N/A')
        amount = event.get('amount', 0)
        payer_bank = event.get('payer_bank', '')
        payee_bank = event.get('payee_bank', '')
        _print(f"{indent}💳 Client payment: {payer} ({payer_bank}) → {payee} ({payee_bank}): ${amount}", console)
    
    elif kind == "InterbankCleared":
        debtor = event.get('debtor_bank', 'N/A')
        creditor = event.get('creditor_bank', 'N/A')
        amount = event.get('amount', 0)
        _print(f"{indent}🏦 Interbank cleared: {debtor} → {creditor}: ${amount} (netted)", console)
    
    elif kind == "ReservesTransferred":
        frm = event.get('frm', 'N/A')
        to = event.get('to', 'N/A')
        amount = event.get('amount', 0)
        _print(f"{indent}💰 Reserves transferred: {frm} → {to}: ${amount}", console)
    
    elif kind == "InstrumentMerged":
        # This is a technical event, show it more compactly
        _print(f"{indent}🔀 Instruments merged", console)
    
    elif kind == "InterbankOvernightCreated":
        debtor = event.get('debtor_bank', 'N/A')
        creditor = event.get('creditor_bank', 'N/A')
        amount = event.get('amount', 0)
        _print(f"{indent}🌙 Overnight payable created: {debtor} → {creditor}: ${amount}", console)
    
    elif kind in ["PhaseA", "PhaseB", "PhaseC"]:
        # Phase markers are not displayed as events themselves
        pass
    
    else:
        # For any other event types, show raw data
        _print(f"{indent}• {kind}: {event}", console)


def display_events_for_day(system: System, day: int) -> None:
    """
    Display all events that occurred on a specific simulation day.
    
    Args:
        system: The bilancio system instance
        day: The simulation day to display events for
    """
    console = Console() if RICH_AVAILABLE else None
    events = [e for e in system.state.events if e.get("day") == day]
    
    if not events:
        _print("  No events occurred on this day.", console)
        return
    
    _display_day_events(events, console)