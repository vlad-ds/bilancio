"""Event formatting registry for Bilancio UI components."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Callable


class EventFormatterRegistry:
    """Registry for event formatters that converts events to display format."""
    
    def __init__(self) -> None:
        self._formatters: Dict[str, Callable[[Dict[str, Any]], Tuple[str, List[str], str]]] = {}
    
    def register(self, kind: str) -> Callable:
        """Decorator to register a formatter for a specific event kind."""
        def decorator(func: Callable[[Dict[str, Any]], Tuple[str, List[str], str]]) -> Callable:
            self._formatters[kind] = func
            return func
        return decorator
    
    def format(self, event: Dict[str, Any]) -> Tuple[str, List[str], str]:
        """Format an event, returning (title, lines, icon).
        
        Args:
            event: Event dictionary with 'kind' and other properties
            
        Returns:
            Tuple of (title, description_lines, icon)
        """
        kind = event.get("kind", "Unknown")
        formatter = self._formatters.get(kind, self._generic_formatter)
        return formatter(event)
    
    def _generic_formatter(self, event: Dict[str, Any]) -> Tuple[str, List[str], str]:
        """Fallback formatter for unknown event kinds."""
        kind = event.get("kind", "Unknown")
        title = f"{kind} Event"
        
        lines = []
        for key, value in event.items():
            if key not in ["kind", "day", "phase"]:
                lines.append(f"{key}: {value}")
        
        return title, lines, "❓"


# Create global registry instance
registry = EventFormatterRegistry()


# Register specific formatters for common event kinds

@registry.register("CashTransferred")
def format_cash_transferred(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format cash transfer events."""
    amount = event.get("amount", 0)
    frm = event.get("frm", "Unknown")
    to = event.get("to", "Unknown")
    
    title = f"Cash Transfer: {amount:,}"
    lines = [
        f"From: {frm}",
        f"To: {to}",
        f"Amount: {amount:,}"
    ]
    
    return title, lines, "💰"


@registry.register("ReservesTransferred") 
def format_reserves_transferred(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format reserves transfer events."""
    amount = event.get("amount", 0)
    frm = event.get("frm", "Unknown")
    to = event.get("to", "Unknown")
    
    title = f"Reserves Transfer: {amount:,}"
    lines = [
        f"From Bank: {frm}",
        f"To Bank: {to}",
        f"Amount: {amount:,}"
    ]
    
    return title, lines, "🏦"


@registry.register("StockTransferred")
def format_stock_transferred(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format stock transfer events."""
    sku = event.get("sku", "Unknown")
    quantity = event.get("qty", 0)
    frm = event.get("frm", "Unknown") 
    to = event.get("to", "Unknown")
    
    title = f"Stock Transfer: {sku}"
    lines = [
        f"From: {frm}",
        f"To: {to}",
        f"SKU: {sku}",
        f"Quantity: {quantity}"
    ]
    
    return title, lines, "📦"


@registry.register("DeliveryObligationCreated")
def format_delivery_obligation_created(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format delivery obligation creation events."""
    sku = event.get("sku", "Unknown")
    quantity = event.get("quantity", 0)
    frm = event.get("frm", "Unknown")
    to = event.get("to", "Unknown")
    due_day = event.get("due_day", "Unknown")
    
    title = f"Delivery Obligation: {sku}"
    lines = [
        f"From: {frm}",
        f"To: {to}",
        f"SKU: {sku}",
        f"Quantity: {quantity}",
        f"Due Day: {due_day}"
    ]
    
    return title, lines, "📋"


@registry.register("DeliveryObligationSettled")
def format_delivery_obligation_settled(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format delivery obligation settlement events."""
    obligation_id = event.get("obligation_id", "Unknown")
    sku = event.get("sku", "Unknown")
    quantity = event.get("quantity", 0)
    debtor = event.get("debtor", "Unknown")
    creditor = event.get("creditor", "Unknown")
    
    title = f"Delivery Settled: {sku}"
    lines = [
        f"Obligation ID: {obligation_id}",
        f"Debtor: {debtor}",
        f"Creditor: {creditor}",
        f"SKU: {sku}",
        f"Quantity: {quantity}"
    ]
    
    return title, lines, "✅"


@registry.register("CashDeposited")
def format_cash_deposited(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format cash deposit events."""
    customer = event.get("customer", "Unknown")
    bank = event.get("bank", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"Cash Deposit: {amount:,}"
    lines = [
        f"Customer: {customer}",
        f"Bank: {bank}",
        f"Amount: {amount:,}"
    ]
    
    return title, lines, "🏧"


@registry.register("CashWithdrawn")
def format_cash_withdrawn(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format cash withdrawal events."""
    customer = event.get("customer", "Unknown")
    bank = event.get("bank", "Unknown") 
    amount = event.get("amount", 0)
    
    title = f"Cash Withdrawal: {amount:,}"
    lines = [
        f"Customer: {customer}",
        f"Bank: {bank}",
        f"Amount: {amount:,}"
    ]
    
    return title, lines, "💸"


@registry.register("ClientPayment")
def format_client_payment(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format client payment events."""
    payer = event.get("payer", "Unknown")
    payee = event.get("payee", "Unknown")
    amount = event.get("amount", 0)
    payer_bank = event.get("payer_bank", "Unknown")
    payee_bank = event.get("payee_bank", "Unknown")
    
    title = f"Client Payment: {amount:,}"
    lines = [
        f"Payer: {payer} (via {payer_bank})",
        f"Payee: {payee} (via {payee_bank})",
        f"Amount: {amount:,}"
    ]
    
    return title, lines, "💳"


@registry.register("InterbankCleared")
def format_interbank_cleared(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format interbank clearing events."""
    debtor_bank = event.get("debtor_bank", "Unknown")
    creditor_bank = event.get("creditor_bank", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"Interbank Clearing: {amount:,}"
    lines = [
        f"Debtor Bank: {debtor_bank}",
        f"Creditor Bank: {creditor_bank}",
        f"Amount: {amount:,}"
    ]
    
    return title, lines, "🔄"


@registry.register("CashMinted")
def format_cash_minted(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format cash minting events."""
    to = event.get("to", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"Cash Minted: {amount:,}"
    lines = [
        f"To: {to}",
        f"Amount: {amount:,}"
    ]
    
    return title, lines, "🖨️"


@registry.register("ReservesMinted")
def format_reserves_minted(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format reserves minting events."""
    to = event.get("to", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"Reserves Minted: {amount:,}"
    lines = [
        f"To Bank: {to}",
        f"Amount: {amount:,}"
    ]
    
    return title, lines, "🏛️"


@registry.register("StockCreated")
def format_stock_created(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format stock creation events."""
    owner = event.get("owner", "Unknown")
    sku = event.get("sku", "Unknown")
    qty = event.get("qty", 0)
    unit_price = event.get("unit_price", 0)
    
    title = f"Stock Created: {sku}"
    lines = [
        f"Owner: {owner}",
        f"SKU: {sku}",
        f"Quantity: {qty}",
        f"Unit Price: {unit_price}"
    ]
    
    return title, lines, "📋"


@registry.register("PayableSettled")
def format_payable_settled(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format payable settlement events."""
    debtor = event.get("debtor", "Unknown")
    creditor = event.get("creditor", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"Payable Settled: {amount:,}"
    lines = [
        f"Debtor: {debtor}",
        f"Creditor: {creditor}",
        f"Amount: {amount:,}"
    ]
    
    return title, lines, "💰"


@registry.register("PhaseA")
def format_phase_a(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format phase A events."""
    return "Phase A: Market Operations", ["Market transactions and operations"], "🌅"


@registry.register("PhaseB") 
def format_phase_b(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format phase B events."""
    return "Phase B: Settlement", ["Settlement of due obligations"], "⚖️"


@registry.register("PhaseC")
def format_phase_c(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format phase C events."""
    return "Phase C: Clearing", ["Intraday netting and clearing"], "🔄"