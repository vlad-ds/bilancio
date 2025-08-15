"""Settlement engine (Phase B) for settling payables due today."""

from bilancio.core.atomic_tx import atomic
from bilancio.core.errors import DefaultError, ValidationError
from bilancio.ops.banking import client_payment


def due_payables(system, day: int):
    """Scan contracts for payables with due_day == day."""
    for c in system.state.contracts.values():
        if c.kind == "payable" and getattr(c, "due_day", None) == day:
            yield c


def due_deliverables(system, day: int):
    """Scan contracts for deliverables with due_day == day."""
    for c in system.state.contracts.values():
        if c.kind == "deliverable" and getattr(c, "due_day", None) == day:
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


def _deliver_goods(system, debtor_id, creditor_id, sku: str, required_quantity: int) -> int:
    """
    Transfer deliverable goods from debtor to creditor by SKU.
    Returns the quantity actually delivered.
    """
    # Find available deliverable assets with matching SKU
    available_assets = []
    for cid in system.state.agents[debtor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "deliverable" and getattr(contract, "sku", None) == sku:
            available_assets.append((cid, contract.amount))
    
    if not available_assets:
        return 0
    
    # Calculate total available quantity
    total_available = sum(quantity for _, quantity in available_assets)
    if total_available == 0:
        return 0
    
    deliver_quantity = min(required_quantity, total_available)
    remaining_to_deliver = deliver_quantity
    
    # Sort by contract ID for deterministic behavior
    available_assets.sort(key=lambda x: x[0])
    
    try:
        # Transfer goods from available assets
        for asset_id, asset_quantity in available_assets:
            if remaining_to_deliver == 0:
                break
                
            transfer_qty = min(remaining_to_deliver, asset_quantity)
            
            # Use the system's transfer_deliverable method
            if transfer_qty == asset_quantity:
                # Transfer the entire asset
                system.transfer_deliverable(asset_id, debtor_id, creditor_id)
            else:
                # Transfer partial quantity (will split the asset)
                system.transfer_deliverable(asset_id, debtor_id, creditor_id, transfer_qty)
            
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


def settle_due_deliverables(system, day: int):
    """
    Settle all deliverables due today.
    
    For each deliverable due today:
    - Get debtor and creditor agents
    - Check if debtor has sufficient deliverable assets with matching SKU
    - Transfer the goods to the creditor
    - Remove the deliverable obligation when fully settled
    - Raise DefaultError if insufficient deliverables
    - Log DeliverableSettled event
    """
    for deliverable in list(due_deliverables(system, day)):
        debtor = system.state.agents[deliverable.liability_issuer_id]
        creditor = system.state.agents[deliverable.asset_holder_id]
        required_sku = getattr(deliverable, "sku", "GENERIC")
        required_quantity = deliverable.amount

        with atomic(system):
            # Try to deliver the required goods
            delivered_quantity = _deliver_goods(system, debtor.id, creditor.id, required_sku, required_quantity)
            
            if delivered_quantity != required_quantity:
                # Cannot deliver fully - raise default error
                shortage = required_quantity - delivered_quantity
                raise DefaultError(f"Insufficient deliverables to settle obligation {deliverable.id}: {shortage} units of {required_sku} still owed")
            
            # Fully settled: remove deliverable obligation and log
            _remove_contract(system, deliverable.id)
            system.log("DeliverableSettled", did=deliverable.id, debtor=debtor.id, creditor=creditor.id, 
                      sku=required_sku, quantity=required_quantity)


def settle_due(system, day: int):
    """
    Settle all obligations due today (both payables and deliverables).
    
    For each payable due today:
    - Get debtor and creditor agents
    - Use policy.settlement_order to determine payment methods
    - Try each method in order until paid or all methods exhausted
    - Raise DefaultError if insufficient funds across all methods
    - Remove payable when fully settled
    - Log PayableSettled event
    
    For each deliverable due today:
    - Get debtor and creditor agents
    - Check if debtor has sufficient deliverable assets with matching SKU
    - Transfer the goods to the creditor
    - Remove the deliverable obligation when fully settled
    - Raise DefaultError if insufficient deliverables
    - Log DeliverableSettled event
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

            # Fully settled: remove payable and log
            _remove_contract(system, payable.id)
            system.log("PayableSettled", pid=payable.id, debtor=debtor.id, creditor=creditor.id, amount=payable.amount)
    
    # Then settle deliverables
    settle_due_deliverables(system, day)
