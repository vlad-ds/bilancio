"""Settlement engine (Phase B) for settling payables due today."""

from bilancio.core.atomic_tx import atomic
from bilancio.core.errors import DefaultError, ValidationError
from bilancio.ops.banking import client_payment


def due_payables(system, day: int):
    """Scan contracts for payables with due_day == day."""
    for c in system.state.contracts.values():
        if c.kind == "payable" and getattr(c, "due_day", None) == day:
            yield c


def due_delivery_obligations(system, day: int):
    """Scan contracts for delivery obligations with due_day == day."""
    for c in system.state.contracts.values():
        if c.kind == "delivery_obligation" and getattr(c, "due_day", None) == day:
            yield c


def _pay_with_deposits(system, debtor_id, creditor_id, amount) -> int:
    """Pay using bank deposits. Returns amount actually paid."""
    # Find debtor's bank deposits
    debtor_deposit_ids = []
    for cid in system.state.agents[debtor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "bank_deposit":
            debtor_deposit_ids.append(cid)

    if not debtor_deposit_ids:
        return 0

    # Calculate available deposit amount
    available = sum(system.state.contracts[cid].amount for cid in debtor_deposit_ids)
    if available == 0:
        return 0

    pay_amount = min(amount, available)

    # Find debtor's and creditor's banks
    debtor_bank_id = None
    creditor_bank_id = None

    # Find debtor's bank from their first deposit
    if debtor_deposit_ids:
        debtor_bank_id = system.state.contracts[debtor_deposit_ids[0]].liability_issuer_id

    # Find creditor's bank - check if they have deposits, otherwise use debtor's bank
    creditor_deposit_ids = []
    for cid in system.state.agents[creditor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "bank_deposit":
            creditor_deposit_ids.append(cid)

    if creditor_deposit_ids:
        creditor_bank_id = system.state.contracts[creditor_deposit_ids[0]].liability_issuer_id
    else:
        # If creditor has no deposits, use debtor's bank for same-bank payment
        creditor_bank_id = debtor_bank_id

    if not debtor_bank_id or not creditor_bank_id:
        return 0

    # Use existing client_payment function which handles both same-bank and cross-bank cases
    try:
        client_payment(system, debtor_id, debtor_bank_id, creditor_id, creditor_bank_id, pay_amount)
        return pay_amount
    except ValidationError:
        return 0


def _pay_with_cash(system, debtor_id, creditor_id, amount) -> int:
    """Pay using cash. Returns amount actually paid."""
    # Find available cash
    debtor_cash_ids = []
    for cid in system.state.agents[debtor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "cash":
            debtor_cash_ids.append(cid)

    if not debtor_cash_ids:
        return 0

    available = sum(system.state.contracts[cid].amount for cid in debtor_cash_ids)
    if available == 0:
        return 0

    pay_amount = min(amount, available)

    try:
        system.transfer_cash(debtor_id, creditor_id, pay_amount)
        return pay_amount
    except ValidationError:
        return 0


def _pay_bank_to_bank_with_reserves(system, debtor_bank_id, creditor_bank_id, amount) -> int:
    """Pay using reserves between banks. Returns amount actually paid."""
    if debtor_bank_id == creditor_bank_id:
        return 0  # Same bank, no reserves needed

    # Find available reserves
    debtor_reserve_ids = []
    for cid in system.state.agents[debtor_bank_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "reserve_deposit":
            debtor_reserve_ids.append(cid)

    if not debtor_reserve_ids:
        return 0

    available = sum(system.state.contracts[cid].amount for cid in debtor_reserve_ids)
    if available == 0:
        return 0

    pay_amount = min(amount, available)

    try:
        system.transfer_reserves(debtor_bank_id, creditor_bank_id, pay_amount)
        return pay_amount
    except ValidationError:
        return 0


def _deliver_stock(system, debtor_id, creditor_id, sku: str, required_quantity: int) -> int:
    """
    Transfer stock lots from debtor to creditor by SKU using FIFO allocation.
    Returns the quantity actually delivered.
    """
    # Find available stock lots with matching SKU
    available_stocks = []
    for stock_id in system.state.agents[debtor_id].stock_ids:
        stock = system.state.stocks[stock_id]
        if stock.sku == sku:
            available_stocks.append((stock_id, stock.quantity))
    
    if not available_stocks:
        return 0
    
    # Calculate total available quantity
    total_available = sum(quantity for _, quantity in available_stocks)
    if total_available == 0:
        return 0
    
    deliver_quantity = min(required_quantity, total_available)
    remaining_to_deliver = deliver_quantity
    
    # Sort by stock ID for FIFO (deterministic) behavior
    available_stocks.sort(key=lambda x: x[0])
    
    try:
        # Transfer stock from available lots
        for stock_id, stock_quantity in available_stocks:
            if remaining_to_deliver == 0:
                break
                
            transfer_qty = min(remaining_to_deliver, stock_quantity)
            
            # Use the internal method to avoid nested atomic
            system._transfer_stock_internal(stock_id, debtor_id, creditor_id, transfer_qty)
            
            remaining_to_deliver -= transfer_qty
        
        return deliver_quantity
    except ValidationError:
        return 0




def _remove_contract(system, contract_id):
    """Remove contract from system and update agent registries."""
    contract = system.state.contracts[contract_id]

    # Remove from asset holder
    asset_holder = system.state.agents[contract.asset_holder_id]
    if contract_id in asset_holder.asset_ids:
        asset_holder.asset_ids.remove(contract_id)

    # Remove from liability issuer
    liability_issuer = system.state.agents[contract.liability_issuer_id]
    if contract_id in liability_issuer.liability_ids:
        liability_issuer.liability_ids.remove(contract_id)

    # Remove from contracts registry
    del system.state.contracts[contract_id]


def settle_due_delivery_obligations(system, day: int):
    """
    Settle all delivery obligations due today using stock operations.
    
    For each delivery obligation due today:
    - Get debtor and creditor agents
    - Check if debtor has sufficient stock with matching SKU
    - Transfer the stock to the creditor using FIFO allocation
    - Remove the delivery obligation when fully settled
    - Raise DefaultError if insufficient stock
    - Log DeliveryObligationSettled event
    """
    for obligation in list(due_delivery_obligations(system, day)):
        debtor = system.state.agents[obligation.liability_issuer_id]
        creditor = system.state.agents[obligation.asset_holder_id]
        required_sku = obligation.sku
        required_quantity = obligation.amount

        with atomic(system):
            # Try to deliver the required stock
            delivered_quantity = _deliver_stock(system, debtor.id, creditor.id, required_sku, required_quantity)
            
            if delivered_quantity != required_quantity:
                # Cannot deliver fully - raise default error
                shortage = required_quantity - delivered_quantity
                raise DefaultError(f"Insufficient stock to settle delivery obligation {obligation.id}: {shortage} units of {required_sku} still owed")
            
            # Fully settled: cancel the delivery obligation and log with alias/contract_id
            system._cancel_delivery_obligation_internal(obligation.id)
            alias = None
            try:
                for a, cid in (system.state.aliases or {}).items():
                    if cid == obligation.id:
                        alias = a
                        break
            except Exception:
                alias = None
            system.log("DeliveryObligationSettled", 
                      obligation_id=obligation.id,
                      contract_id=obligation.id,
                      alias=alias, 
                      debtor=debtor.id, 
                      creditor=creditor.id, 
                      sku=required_sku, 
                      qty=required_quantity)


def settle_due(system, day: int):
    """
    Settle all obligations due today (payables and delivery obligations).
    
    For each payable due today:
    - Get debtor and creditor agents
    - Use policy.settlement_order to determine payment methods
    - Try each method in order until paid or all methods exhausted
    - Raise DefaultError if insufficient funds across all methods
    - Remove payable when fully settled
    - Log PayableSettled event
    
    For each delivery obligation due today:
    - Get debtor and creditor agents
    - Check if debtor has sufficient stock with matching SKU
    - Transfer the stock to the creditor using FIFO allocation
    - Remove the delivery obligation when fully settled
    - Raise DefaultError if insufficient stock
    - Log DeliveryObligationSettled event
    """
    # First settle payables
    for payable in list(due_payables(system, day)):
        debtor = system.state.agents[payable.liability_issuer_id]
        creditor = system.state.agents[payable.asset_holder_id]
        order = system.policy.settlement_order(debtor)

        remaining = payable.amount

        with atomic(system):
            for method in order:
                if remaining == 0:
                    break

                if method == "bank_deposit":
                    paid_now = _pay_with_deposits(system, debtor.id, creditor.id, remaining)
                    remaining -= paid_now
                elif method == "cash":
                    paid_now = _pay_with_cash(system, debtor.id, creditor.id, remaining)
                    remaining -= paid_now
                elif method == "reserve_deposit":
                    paid_now = _pay_bank_to_bank_with_reserves(system, debtor.id, creditor.id, remaining)
                    remaining -= paid_now
                else:
                    raise ValidationError(f"unknown payment method {method}")

            if remaining != 0:
                # Cannot settle fully - raise default error
                raise DefaultError(f"Insufficient funds to settle payable {payable.id}: {remaining} still owed")

            # Fully settled: remove payable and log with alias/contract_id
            _remove_contract(system, payable.id)
            alias = None
            try:
                for a, cid in (system.state.aliases or {}).items():
                    if cid == payable.id:
                        alias = a
                        break
            except Exception:
                alias = None
            system.log("PayableSettled", pid=payable.id, contract_id=payable.id, alias=alias,
                       debtor=debtor.id, creditor=creditor.id, amount=payable.amount)
    
    # Settle delivery obligations
    settle_due_delivery_obligations(system, day)
