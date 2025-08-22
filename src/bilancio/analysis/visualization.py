"""Balance sheet visualization utilities for the bilancio system."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
    from rich.console import RenderableType
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    RenderableType = Any

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
            if asset_type in ['delivery_obligation']:
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
            if liability_type in ['delivery_obligation']:
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
        is_nonfinancial = asset_type in ['delivery_obligation']
        
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
        is_nonfinancial = liability_type in ['delivery_obligation']
        
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
            if asset_type not in ['delivery_obligation']:
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
            if liability_type not in ['delivery_obligation']:
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
        
        # Add valued delivery obligations total if present
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
            if asset_type not in ['delivery_obligation']:
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
            if liability_type not in ['delivery_obligation']:
                amount = _format_currency(balance.liabilities_by_kind[liability_type])
                liability_name = liability_type
                if len(liability_name + " " + amount) > col_width:
                    liability_name = liability_name[:col_width-len(amount)-4] + "..."
                data.append((liability_name, amount))
        
        data.append(("", ""))
        data.append(("Total Financial", _format_currency(balance.total_financial_assets)))
        
        # Add valued delivery obligations total if present
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


def display_events_table(events: List[Dict[str, Any]], group_by_day: bool = True) -> None:
    """Render events as a table with canonical columns.

    Falls back to simple text when Rich is not available.
    """
    console = Console() if RICH_AVAILABLE else None

    if not events:
        _print("No events to display.", console)
        return

    columns = ["Day", "Phase", "Kind", "From", "To", "SKU/Instr", "Qty", "Amount", "Notes"]

    # Sort events deterministically
    # Drop phase marker events; preserve original insertion (chronological) order
    evs = [e for e in events if e.get("kind") not in ("PhaseA", "PhaseB", "PhaseC")]

    if RICH_AVAILABLE:
        from rich.table import Table as RichTable
        from rich import box as rich_box
        table = RichTable(title="Events", box=rich_box.HEAVY, show_lines=True)
        # Column definitions with better alignment
        table.add_column("Day", justify="right")
        table.add_column("Phase", justify="left")
        table.add_column("Kind", justify="left")
        table.add_column("From", justify="left")
        table.add_column("To", justify="left")
        table.add_column("SKU/Instr", justify="left")
        table.add_column("Qty", justify="right")
        table.add_column("Amount", justify="right")
        table.add_column("Notes", justify="left")
        # Alternate row shading for readability
        try:
            table.row_styles = ["on #ffffff", "on #e6f2ff"]
        except Exception:
            pass

        for e in evs:
            kind = str(e.get("kind", ""))
            # Canonical from/to mapping by kind
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer")
                to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank")
                to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner")
                to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"

            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"

            table.add_row(
                str(e.get("day", "—")),
                str(e.get("phase", "—")),
                kind,
                str(frm or "—"),
                str(to or "—"),
                str(sku),
                str(qty),
                str(amt),
                notes,
            )

        console.print(table) if console else print(table)
    else:
        # Simple header + rows
        header = " | ".join(columns)
        print(header)
        print("-" * len(header))
        for e in evs:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer")
                to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank")
                to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner")
                to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"
            row = [
                str(e.get("day", "—")),
                str(e.get("phase", "—")),
                kind,
                str(frm or "—"),
                str(to or "—"),
                str(sku),
                str(qty),
                str(amt),
                notes,
            ]
            print(" | ".join(row))


def display_events_table_renderable(events: List[Dict[str, Any]]) -> RenderableType:
    """Return a Rich Table renderable (or string) for events table."""
    if not events:
        return Text("No events to display.", style="dim") if RICH_AVAILABLE else "No events to display."

    columns = ["Day", "Phase", "Kind", "From", "To", "SKU/Instr", "Qty", "Amount", "Notes"]
    # Drop phase marker events; preserve original insertion (chronological) order
    evs = [e for e in events if e.get("kind") not in ("PhaseA", "PhaseB", "PhaseC")]

    if RICH_AVAILABLE:
        from rich.table import Table as RichTable
        from rich import box as rich_box
        table = RichTable(title="Events", box=rich_box.HEAVY, show_lines=True)
        table.add_column("Day", justify="right")
        table.add_column("Phase", justify="left")
        table.add_column("Kind", justify="left")
        table.add_column("From", justify="left")
        table.add_column("To", justify="left")
        table.add_column("SKU/Instr", justify="left")
        table.add_column("Qty", justify="right")
        table.add_column("Amount", justify="right")
        table.add_column("Notes", justify="left")
        try:
            table.row_styles = ["on #ffffff", "on #e6f2ff"]
        except Exception:
            pass

        for e in evs:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer")
                to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank")
                to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner")
                to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"

            table.add_row(
                str(e.get("day", "—")),
                str(e.get("phase", "—")),
                kind,
                str(frm or "—"),
                str(to or "—"),
                str(sku),
                str(qty),
                str(amt),
                notes,
            )
        return table
    else:
        header = " | ".join(columns)
        lines = [header, "-" * len(header)]
        for e in evs:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer")
                to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank")
                to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner")
                to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"
            row = [
                str(e.get("day", "—")),
                str(e.get("phase", "—")),
                kind,
                str(frm or "—"),
                str(to or "—"),
                str(sku),
                str(qty),
                str(amt),
                notes,
            ]
            lines.append(" | ".join(row))
        return "\n".join(lines)


def display_events_tables_by_phase_renderables(events: List[Dict[str, Any]], day: Optional[int] = None) -> List[RenderableType]:
    """Return three event tables (A, B, C) using phase markers as section dividers.

    - Excludes PhaseA/PhaseB/PhaseC events from rows.
    - Titles indicate the phase and optional day.
    """
    if RICH_AVAILABLE:
        from rich.table import Table as RichTable
        from rich import box as rich_box
        from rich.text import Text as RichText
    
    # If these are setup-phase events (day 0), render as a single "Setup" table
    if any(e.get("phase") == "setup" for e in events):
        return _build_single_setup_table(events, day)

    # Group by phase markers in original order
    buckets = {"A": [], "B": [], "C": []}
    current = "A"
    for e in events:
        kind = e.get("kind")
        if kind == "PhaseA":
            current = "A"; continue
        if kind == "PhaseB":
            current = "B"; continue
        if kind == "PhaseC":
            current = "C"; continue
        buckets[current].append(e)

    def build_table(phase: str, rows: List[Dict[str, Any]]):
        title_parts = {
            "A": "Phase A — Start of day",
            "B": "Phase B — Settlement",
            "C": "Phase C — Clearing"
        }
        title = title_parts.get(phase, f"Phase {phase}")
        if day is not None:
            title = f"{title} (Day {day})"

        if not RICH_AVAILABLE:
            # Simple text fallback
            header = ["Kind", "From", "To", "SKU/Instr", "Qty", "Amount", "Notes"]
            out = [f"{title}", " | ".join(header), "-" * 80]
            for e in rows:
                kind = str(e.get("kind", ""))
                # map from/to like in table renderers
                if kind in ("CashDeposited", "CashWithdrawn"):
                    frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                    to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
                elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                    frm = e.get("payer"); to = e.get("payee")
                elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                    frm = e.get("debtor_bank"); to = e.get("creditor_bank")
                elif kind == "StockCreated":
                    frm = e.get("owner"); to = None
                else:
                    frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                    to = e.get("to") or e.get("creditor") or e.get("payee")
                sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
                qty = e.get("qty") or e.get("quantity") or "—"
                amt = e.get("amount") or "—"
                notes = ""
                if kind == "ClientPayment":
                    notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
                elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                    notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                    if 'due_day' in e:
                        notes += f"; due {e.get('due_day')}"
                out.append(" | ".join(map(str, [kind, frm or "—", to or "—", sku, qty, amt, notes])))
            return "\n".join(out)

        # Rich table
        table = RichTable(title=title, box=rich_box.HEAVY, show_lines=True)
        table.add_column("Kind", justify="left")
        table.add_column("From", justify="left")
        table.add_column("To", justify="left")
        table.add_column("SKU/Instr", justify="left")
        table.add_column("Qty", justify="right")
        table.add_column("Amount", justify="right")
        table.add_column("Notes", justify="left")
        try:
            table.row_styles = ["on #ffffff", "on #e6f2ff"] if phase != "C" else ["on #ffffff", "on #fff2cc"]
        except Exception:
            pass
        for e in rows:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer"); to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank"); to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner"); to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"
            table.add_row(kind, str(frm or "—"), str(to or "—"), str(sku), str(qty), str(amt), notes)
        return table

    renderables: List[RenderableType] = []
    # Phase A is intentionally empty for now; only include if it has rows
    if buckets["A"]:
        renderables.append(build_table("A", buckets["A"]))
    # Phase B: settlements
    renderables.append(build_table("B", buckets["B"]))
    # Phase C: clearing
    renderables.append(build_table("C", buckets["C"]))
    return renderables


def _build_single_setup_table(events: List[Dict[str, Any]], day: Optional[int] = None) -> List[RenderableType]:
    """Render a single setup table for setup-phase events (day 0)."""
    rows = [e for e in events if e.get("phase") == "setup" and e.get("kind") not in ("PhaseA","PhaseB","PhaseC")]
    title = "Setup"
    if day is not None:
        title = f"{title} (Day {day})"
    if not RICH_AVAILABLE:
        header = ["Kind", "From", "To", "SKU/Instr", "Qty", "Amount", "Notes"]
        out = [title, " | ".join(header), "-" * 80]
        for e in rows:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer"); to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank"); to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner"); to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            out.append(" | ".join(map(str, [kind, frm or "—", to or "—", sku, qty, amt, notes])))
        return ["\n".join(out)]

    from rich.table import Table as RichTable
    from rich import box as rich_box
    table = RichTable(title=title, box=rich_box.HEAVY, show_lines=True)
    table.add_column("Kind", justify="left")
    table.add_column("From", justify="left")
    table.add_column("To", justify="left")
    table.add_column("SKU/Instr", justify="left")
    table.add_column("Qty", justify="right")
    table.add_column("Amount", justify="right")
    table.add_column("Notes", justify="left")
    try:
        table.row_styles = ["on #ffffff", "on #e6f2ff"]
    except Exception:
        pass
    for e in rows:
        kind = str(e.get("kind", ""))
        if kind in ("CashDeposited", "CashWithdrawn"):
            frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
            to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
        elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
            frm = e.get("payer"); to = e.get("payee")
        elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
            frm = e.get("debtor_bank"); to = e.get("creditor_bank")
        elif kind == "StockCreated":
            frm = e.get("owner"); to = None
        else:
            frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
            to = e.get("to") or e.get("creditor") or e.get("payee")
        sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
        qty = e.get("qty") or e.get("quantity") or "—"
        amt = e.get("amount") or "—"
        notes = ""
        table.add_row(kind, str(frm or "—"), str(to or "—"), str(sku), str(qty), str(amt), notes)
    return [table]


# ============================================================================
# T-account builder and renderers (detailed with Qty/Value/Counterparty/Maturity)
# ============================================================================

@dataclass
class BalanceRow:
    name: str
    quantity: Optional[int]
    value_minor: Optional[int]
    counterparty_name: Optional[str]
    maturity: Optional[str]


@dataclass
class TAccount:
    assets: List[BalanceRow]
    liabilities: List[BalanceRow]


def _format_agent(agent_id: str, system: System) -> str:
    """Format agent as 'Name [ID]' if available."""
    ag = system.state.agents.get(agent_id)
    if ag is None:
        return agent_id
    if ag.name and ag.name != agent_id:
        return f"{ag.name} [{agent_id}]"
    return agent_id


def build_t_account_rows(system: System, agent_id: str) -> TAccount:
    """Build detailed T-account rows from system state for an agent."""
    assets: List[BalanceRow] = []
    liabilities: List[BalanceRow] = []

    agent = system.state.agents[agent_id]

    # Inventory (stocks owned) as assets
    for stock_id in agent.stock_ids:
        lot = system.state.stocks[stock_id]
        try:
            value_minor = int(lot.value)
        except Exception:
            # Fallback for Decimals
            value_minor = int(float(lot.value))
        assets.append(BalanceRow(
            name=f"{lot.sku}",
            quantity=int(lot.quantity),
            value_minor=value_minor,
            counterparty_name="—",
            maturity="—",
        ))

    # Contracts as assets (held by agent)
    for cid in agent.asset_ids:
        c = system.state.contracts[cid]
        if c.kind == "delivery_obligation":
            # Receivable goods
            # valued_amount is Decimal
            valued = getattr(c, 'valued_amount', None)
            try:
                valued_minor = int(valued) if valued is not None else None
            except Exception:
                valued_minor = int(float(valued)) if valued is not None else None
            counterparty = _format_agent(c.liability_issuer_id, system)
            maturity = f"Day {getattr(c, 'due_day', '—')}"
            assets.append(BalanceRow(
                name=f"{getattr(c, 'sku', 'goods')} receivable",
                quantity=int(c.amount) if c.amount is not None else None,
                value_minor=valued_minor,
                counterparty_name=counterparty,
                maturity=maturity,
            ))
        else:
            # Financial assets
            counterparty = _format_agent(c.liability_issuer_id, system)
            maturity = "on-demand" if c.kind in ("cash", "bank_deposit", "reserve_deposit") else (
                f"Day {getattr(c, 'due_day', '—')}" if hasattr(c, 'due_day') else "—"
            )
            assets.append(BalanceRow(
                name=f"{c.kind}",
                quantity=None,
                value_minor=int(c.amount) if c.amount is not None else None,
                counterparty_name=counterparty if c.kind != "cash" else "—",
                maturity=maturity,
            ))

    # Contracts as liabilities (issued by agent)
    for cid in agent.liability_ids:
        c = system.state.contracts[cid]
        if c.kind == "delivery_obligation":
            valued = getattr(c, 'valued_amount', None)
            try:
                valued_minor = int(valued) if valued is not None else None
            except Exception:
                valued_minor = int(float(valued)) if valued is not None else None
            counterparty = _format_agent(c.asset_holder_id, system)
            maturity = f"Day {getattr(c, 'due_day', '—')}"
            liabilities.append(BalanceRow(
                name=f"{getattr(c, 'sku', 'goods')} obligation",
                quantity=int(c.amount) if c.amount is not None else None,
                value_minor=valued_minor,
                counterparty_name=counterparty,
                maturity=maturity,
            ))
        else:
            counterparty = _format_agent(c.asset_holder_id, system)
            maturity = "on-demand" if c.kind in ("cash", "bank_deposit", "reserve_deposit") else (
                f"Day {getattr(c, 'due_day', '—')}" if hasattr(c, 'due_day') else "—"
            )
            liabilities.append(BalanceRow(
                name=f"{c.kind}",
                quantity=None,
                value_minor=int(c.amount) if c.amount is not None else None,
                counterparty_name=counterparty,
                maturity=maturity,
            ))

    # Ordering within each side
    def sort_key_assets(row: BalanceRow):
        # Inventory first (has quantity and counterparty '—' and maturity '—'),
        # then receivables (name ends with 'receivable'), then financial by kind order
        financial_order = {"cash": 0, "bank_deposit": 1, "reserve_deposit": 2, "payable": 3}
        if row.quantity is not None and row.counterparty_name == "—":
            return (0, 0, row.name or "")
        if row.name.endswith("receivable"):
            # try to parse maturity day number
            mat = row.maturity or ""
            day_num = 10**9
            if isinstance(mat, str) and mat.startswith("Day "):
                try:
                    day_num = int(mat.split(" ")[1])
                except Exception:
                    pass
            return (1, day_num, row.name)
        return (2, financial_order.get(row.name, 99), row.name)

    def sort_key_liabs(row: BalanceRow):
        # Obligations (name ends with 'obligation') by due day, then financial by order
        financial_order = {"payable": 0, "bank_deposit": 1, "reserve_deposit": 2, "cash": 3}
        if row.name.endswith("obligation"):
            mat = row.maturity or ""
            day_num = 10**9
            if isinstance(mat, str) and mat.startswith("Day "):
                try:
                    day_num = int(mat.split(" ")[1])
                except Exception:
                    pass
            return (0, day_num, row.name)
        return (1, financial_order.get(row.name, 99), row.name)

    assets.sort(key=sort_key_assets)
    liabilities.sort(key=sort_key_liabs)

    return TAccount(assets=assets, liabilities=liabilities)


def display_agent_t_account(system: System, agent_id: str, format: str = 'rich') -> None:
    """Display detailed T-account table for an agent."""
    if format == 'rich' and not RICH_AVAILABLE:
        format = 'simple'
    if format == 'rich':
        table = display_agent_t_account_renderable(system, agent_id)
        Console().print(table)
    else:
        # Simple ASCII fallback
        acct = build_t_account_rows(system, agent_id)
        columns = ["Name", "Qty", "Value", "Counterparty", "Maturity"]
        # Prepare rows
        max_rows = max(len(acct.assets), len(acct.liabilities))
        header = " | ".join([f"Assets:{c}" for c in columns] + [f"Liabilities:{c}" for c in columns])
        print(header)
        print("-" * len(header))
        for i in range(max_rows):
            a = acct.assets[i] if i < len(acct.assets) else None
            l = acct.liabilities[i] if i < len(acct.liabilities) else None
            def fmt_qty(r): return f"{r.quantity:,}" if (r and r.quantity is not None) else "—"
            def fmt_val(r):
                if not r or r.value_minor is None: return "—"
                return _format_currency(int(r.value_minor))
            def cells(r):
                if not r: return ("", "", "", "", "")
                return (r.name, fmt_qty(r), fmt_val(r), r.counterparty_name or "—", r.maturity or "—")
            row = list(cells(a) + cells(l))
            print(" | ".join(str(x) for x in row))


def display_agent_t_account_renderable(system: System, agent_id: str) -> RenderableType:
    """Return a Rich Table renderable for detailed T-account."""
    if not RICH_AVAILABLE:
        # Fallback to string
        acct = build_t_account_rows(system, agent_id)
        lines = []
        columns = ["Name", "Qty", "Value", "Counterparty", "Maturity"]
        lines.append(" | ".join([f"Assets:{c}" for c in columns] + [f"Liabilities:{c}" for c in columns]))
        max_rows = max(len(acct.assets), len(acct.liabilities))
        for i in range(max_rows):
            a = acct.assets[i] if i < len(acct.assets) else None
            l = acct.liabilities[i] if i < len(acct.liabilities) else None
            def fmt_qty(r): return f"{r.quantity:,}" if (r and r.quantity is not None) else "—"
            def fmt_val(r):
                if not r or r.value_minor is None: return "—"
                return _format_currency(int(r.value_minor))
            def cells(r):
                if not r: return ("", "", "", "", "")
                return (r.name, fmt_qty(r), fmt_val(r), r.counterparty_name or "—", r.maturity or "—")
            row = list(cells(a) + cells(l))
            lines.append(" | ".join(str(x) for x in row))
        return "\n".join(lines)

    # Rich path
    from rich.table import Table as RichTable
    from rich import box as rich_box
    acct = build_t_account_rows(system, agent_id)

    ag = system.state.agents[agent_id]
    title = f"{ag.name} [{agent_id}] ({ag.kind})" if ag.name and ag.name != agent_id else f"{agent_id} ({ag.kind})"

    table = RichTable(title=title, box=rich_box.HEAVY, title_style="bold cyan", show_lines=True)
    # Add 10 columns: 5 for assets, 5 for liabilities
    table.add_column("Name", style="green", justify="left")
    table.add_column("Qty", style="green", justify="right")
    table.add_column("Value", style="green", justify="right")
    table.add_column("Counterparty", style="green", justify="left")
    table.add_column("Maturity", style="green", justify="right")
    table.add_column("Name", style="red", justify="left")
    table.add_column("Qty", style="red", justify="right")
    table.add_column("Value", style="red", justify="right")
    table.add_column("Counterparty", style="red", justify="left")
    table.add_column("Maturity", style="red", justify="right")
    try:
        table.row_styles = ["on #ffffff", "on #fff2cc"]
    except Exception:
        pass

    def fmt_qty(r): return f"{r.quantity:,}" if (r and r.quantity is not None) else "—"
    def fmt_val(r):
        if not r or r.value_minor is None: return "—"
        return _format_currency(int(r.value_minor))
    def cells(r):
        if not r: return ("", "", "", "", "")
        return (r.name, fmt_qty(r), fmt_val(r), r.counterparty_name or "—", r.maturity or "—")

    max_rows = max(len(acct.assets), len(acct.liabilities))
    for i in range(max_rows):
        a = acct.assets[i] if i < len(acct.assets) else None
        l = acct.liabilities[i] if i < len(acct.liabilities) else None
        table.add_row(*cells(a), *cells(l))
    return table


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


# ============================================================================
# New Renderable-returning Functions for HTML Export
# ============================================================================

def display_agent_balance_table_renderable(
    system: System,
    agent_id: str,
    format: str = 'rich',
    title: Optional[str] = None
) -> Union[RenderableType, str]:
    """
    Return a renderable for a single agent's balance sheet as a T-account style table.
    
    Args:
        system: The bilancio system instance
        agent_id: ID of the agent to display
        format: Display format ('rich' or 'simple')
        title: Optional custom title for the table
        
    Returns:
        Rich Table renderable for rich format, or string for simple format
    """
    if format == 'rich' and not RICH_AVAILABLE:
        format = 'simple'
    
    # Get agent balance
    balance = agent_balance(system, agent_id)
    
    if format == 'rich':
        # Get agent info
        agent = system.state.agents[agent_id]
        if title is None:
            # Show both name and ID for clarity
            if agent.name and agent.name != agent_id:
                title = f"{agent.name} [{agent_id}] ({agent.kind})"
            else:
                title = f"{agent_id} ({agent.kind})"
        
        return _create_rich_agent_balance_table(title, balance)
    else:
        # Return simple text format as string
        return _build_simple_agent_balance_string(balance, system, agent_id, title)


def display_multiple_agent_balances_renderable(
    system: System,
    items: List[Union[str, AgentBalance]], 
    format: str = 'rich'
) -> Union[RenderableType, str]:
    """
    Return renderables for multiple agent balance sheets side by side for comparison.
    
    Args:
        system: The bilancio system instance
        items: List of agent IDs (str) or AgentBalance instances
        format: Display format ('rich' or 'simple')
        
    Returns:
        Rich Columns renderable for rich format, or string for simple format
    """
    if format == 'rich' and not RICH_AVAILABLE:
        format = 'simple'
    
    # Convert agent IDs to balance objects if needed
    balances = []
    for item in items:
        if isinstance(item, str):
            balances.append(agent_balance(system, item))
        else:
            balances.append(item)
    
    if format == 'rich':
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
            
            table = _create_compact_rich_balance_table(title, balance)
            tables.append(table)
        
        return Columns(tables, equal=True, expand=True)
    else:
        # Return simple text format as string
        return _build_simple_multiple_agent_balances_string(balances, system)


def display_events_renderable(events: List[Dict[str, Any]], format: str = 'detailed') -> List[RenderableType]:
    """
    Return renderables for system events in a nicely formatted way.
    
    Args:
        events: List of event dictionaries from sys.state.events
        format: Display format ('detailed' or 'summary')
        
    Returns:
        List of Rich renderables (or strings for simple format)
    """
    if not events:
        if RICH_AVAILABLE:
            return [Text("No events to display.", style="dim")]
        else:
            return ["No events to display."]
    
    if format == 'summary':
        return _build_events_summary_renderables(events)
    else:
        return _build_events_detailed_renderables(events)


def display_events_for_day_renderable(system: System, day: int) -> List[RenderableType]:
    """
    Return renderables for all events that occurred on a specific simulation day.
    
    Args:
        system: The bilancio system instance
        day: The simulation day to display events for
        
    Returns:
        List of Rich renderables (or strings for simple format)
    """
    events = [e for e in system.state.events if e.get("day") == day]
    
    if not events:
        if RICH_AVAILABLE:
            return [Text("  No events occurred on this day.", style="dim")]
        else:
            return ["  No events occurred on this day."]
    
    return _build_day_events_renderables(events)


# ============================================================================
# Helper Functions for New Renderable Functions
# ============================================================================

def _create_rich_agent_balance_table(title: str, balance: AgentBalance) -> Table:
    """Create a Rich Table for a single agent balance (returns table instead of printing)."""
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
    displayed_asset_skus = set()
    for sku, data in balance.nonfinancial_assets_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} receivable [{qty} unit{'s' if qty != 1 else ''}]"
            amount = _format_currency(int(data['value']))
            asset_rows.append((name, amount))
            displayed_asset_skus.add(sku)
    
    # Third: Add financial assets (everything else in assets_by_kind)
    financial_asset_kinds = set()
    for asset_type in sorted(balance.assets_by_kind.keys()):
        # Skip if this is a non-financial type we already displayed
        is_nonfinancial = False
        for sku in displayed_asset_skus:
            # This is a heuristic but works for current instrument types
            if asset_type in ['delivery_obligation']:
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
            if liability_type in ['delivery_obligation']:
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
    
    return table


def _create_compact_rich_balance_table(title: str, balance: AgentBalance) -> Table:
    """Create a compact Rich Table for multiple balance display."""
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
    
    # Third: Add financial assets
    for asset_type in sorted(balance.assets_by_kind.keys()):
        # Skip non-financial types
        if asset_type not in ['delivery_obligation']:
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
        if liability_type not in ['delivery_obligation']:
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
    table.add_row(
        Text("Total Liab.", style="bold red"),
        Text(_format_currency(balance.total_financial_liabilities), style="bold red")
    )
    
    net_worth_style = "bold green" if balance.net_financial >= 0 else "bold red"
    table.add_row(
        Text("Net Financial", style="bold blue"),
        Text(_format_currency(balance.net_financial, show_sign=True), style=net_worth_style)
    )
    
    return table


def _build_simple_agent_balance_string(
    balance: AgentBalance, 
    system: Optional[System] = None, 
    agent_id: Optional[str] = None,
    title: Optional[str] = None
) -> str:
    """Build a simple text format balance sheet string."""
    lines = []
    
    # Get title
    if title is None:
        if system and agent_id and agent_id in system.state.agents:
            agent = system.state.agents[agent_id]
            if agent.name and agent.name != agent_id:
                title = f"{agent.name} [{agent_id}] ({agent.kind})"
            else:
                title = f"{agent_id} ({agent.kind})"
        else:
            title = f"Agent {balance.agent_id}"
    
    lines.append(f"\n{title}")
    lines.append("=" * 70)
    lines.append(f"{'ASSETS':<30} {'Amount':>12} | {'LIABILITIES':<30} {'Amount':>12}")
    lines.append("-" * 70)
    
    # Simplified balance sheet representation for simple format
    lines.append(f"{'Total Financial':<30} {_format_currency(balance.total_financial_assets):>12} | "
          f"{'Total Financial':<30} {_format_currency(balance.total_financial_liabilities):>12}")
    
    lines.append("-" * 70)
    lines.append(f"{'':>44} | {'NET FINANCIAL':<30} {_format_currency(balance.net_financial, show_sign=True):>12}")
    
    return "\n".join(lines)


def _build_simple_multiple_agent_balances_string(
    balances: List[AgentBalance], 
    system: Optional[System] = None
) -> str:
    """Build a simple text format for multiple agent balances."""
    lines = []
    lines.append("\nMultiple Agent Balances (Simplified View)")
    lines.append("=" * 60)
    
    for balance in balances:
        if system and balance.agent_id in system.state.agents:
            agent = system.state.agents[balance.agent_id]
            header = f"{agent.name or balance.agent_id} ({agent.kind})"
        else:
            header = balance.agent_id
        
        lines.append(f"{header}: Net Financial = {_format_currency(balance.net_financial, show_sign=True)}")
    
    return "\n".join(lines)


def _build_events_summary_renderables(events: List[Dict[str, Any]]) -> List[RenderableType]:
    """Build renderables for events in summary format."""
    renderables = []
    
    for event in events:
        kind = event.get("kind", "Unknown")
        day = event.get("day", "?")
        
        if kind == "PayableSettled":
            text = f"Day {day}: 💰 {event['debtor']} → {event['creditor']}: ${event['amount']}"
        elif kind == "DeliveryObligationSettled":
            qty = event.get('qty', event.get('quantity', 'N/A'))
            text = f"Day {day}: 📦 {event['debtor']} → {event['creditor']}: {qty} {event.get('sku', 'items')}"
        elif kind == "StockTransferred":
            text = f"Day {day}: 🚚 {event['frm']} → {event['to']}: {event['qty']} {event['sku']}"
        elif kind == "CashTransferred":
            text = f"Day {day}: 💵 {event['frm']} → {event['to']}: ${event['amount']}"
        else:
            continue  # Skip other events in summary mode
        
        if RICH_AVAILABLE:
            renderables.append(Text(text))
        else:
            renderables.append(text)
    
    return renderables


def _build_events_detailed_renderables(events: List[Dict[str, Any]]) -> List[RenderableType]:
    """Build renderables for events in detailed format, organized by phases."""
    # Import and use the phase-aware version
    from bilancio.analysis.visualization_phases import build_events_detailed_with_phases
    return build_events_detailed_with_phases(events, RICH_AVAILABLE)
    
def _build_events_detailed_renderables_old(events: List[Dict[str, Any]]) -> List[RenderableType]:
    """Old version - kept for reference."""
    renderables = []
    
    # Use the formatter registry to format events nicely
    from bilancio.ui.render.formatters import registry
    
    # Group events by phase
    phases = {"A": [], "B": [], "C": [], "other": []}
    for event in events:
        phase = event.get("phase", "other")
        if phase in ["A", "B", "C"]:
            phases[phase].append(event)
        else:
            phases["other"].append(event)
    
    # Display events organized by phase
    if phases["A"]:
        if RICH_AVAILABLE:
            from rich.text import Text
            phase_header = Text("\n⏰ Phase A - Morning Activities", style="bold cyan")
            renderables.append(phase_header)
        else:
            renderables.append("\n⏰ Phase A - Morning Activities")
        
        for event in phases["A"]:
            kind = event.get("kind", "Unknown")
            if kind == "PhaseA":
                continue  # Skip the phase marker itself</            
            renderables.extend(_format_single_event(event, registry))
    
    if phases["B"]:
        if RICH_AVAILABLE:
            from rich.text import Text
            phase_header = Text("\n🌅 Phase B - Business Hours", style="bold yellow")
            renderables.append(phase_header)
        else:
            renderables.append("\n🌅 Phase B - Business Hours")
            
        for event in phases["B"]:
            kind = event.get("kind", "Unknown")
            if kind == "PhaseB":
                continue  # Skip the phase marker itself
            renderables.extend(_format_single_event(event, registry))
    
    if phases["C"]:
        if RICH_AVAILABLE:
            from rich.text import Text
            phase_header = Text("\n🌙 Phase C - End of Day Clearing", style="bold green")
            renderables.append(phase_header)
        else:
            renderables.append("\n🌙 Phase C - End of Day Clearing")
            
        for event in phases["C"]:
            kind = event.get("kind", "Unknown")
            if kind == "PhaseC":
                continue  # Skip the phase marker itself
            renderables.extend(_format_single_event(event, registry))
    
    # Display any events without phase markers
    if phases["other"]:
        for event in phases["other"]:
            kind = event.get("kind", "Unknown")
            if kind in ["PhaseA", "PhaseB", "PhaseC"]:
                continue  # Skip phase markers
            renderables.extend(_format_single_event(event, registry))
    
    return renderables


def _format_single_event(event: Dict[str, Any], registry) -> List[RenderableType]:
    """Format a single event and return renderables."""
    renderables = []
    
    # Format the event using the registry
    title, lines, icon = registry.format(event)
    
    if RICH_AVAILABLE:
        from rich.text import Text
        # Create a nice formatted display with icon and details
        text = Text()
        
        # Add icon and title with color based on event type
        if "Transfer" in title or "Payment" in title:
            text.append(title, style="bold cyan")
        elif "Settled" in title or "Cleared" in title:
            text.append(title, style="bold green")
        elif "Created" in title or "Minted" in title:
            text.append(title, style="bold yellow")
        elif "Consolidation" in title or "Split" in title:
            text.append(title, style="dim italic")
        else:
            text.append(title, style="bold")
        
        # Add details with proper indentation and styling
        if lines:
            for i, line in enumerate(lines[:3]):  # Show up to 3 lines
                text.append("\n   ")
                if "→" in line or "←" in line:
                    # Flow lines - make them prominent
                    text.append(line, style="white")
                elif ":" in line:
                    # Split field and value for better formatting
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        field, value = parts
                        text.append(field + ":", style="dim")
                        text.append(value, style="white")
                    else:
                        text.append(line, style="dim white")
                elif line.startswith("("):
                    # Technical explanations in parentheses - make them dimmer
                    text.append(line, style="dim italic")
                else:
                    text.append(line, style="white")
        
        renderables.append(text)
    else:
        # Simple text format
        text = f"• {title}"
        if lines:
            text += " - " + ", ".join(lines[:2])
        renderables.append(text)
    
    return [renderables[0]] if renderables else []


def _build_day_events_renderables(events: List[Dict[str, Any]]) -> List[RenderableType]:
    """Build renderables for events in a single day."""
    return _build_events_detailed_renderables(events)
