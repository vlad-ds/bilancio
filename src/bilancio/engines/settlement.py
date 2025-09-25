"""Settlement engine (Phase B) for settling payables due today."""

from __future__ import annotations

from bilancio.core.atomic_tx import atomic
from bilancio.core.errors import DefaultError, ValidationError
from bilancio.ops.banking import client_payment
from bilancio.ops.aliases import get_alias_for_id

DEFAULT_MODE_FAIL_FAST = "fail-fast"
DEFAULT_MODE_EXPEL = "expel-agent"

_ACTION_AGENT_FIELDS = {
    "mint_reserves": ("to",),
    "mint_cash": ("to",),
    "transfer_reserves": ("from_bank", "to_bank"),
    "transfer_cash": ("from_agent", "to_agent"),
    "deposit_cash": ("customer", "bank"),
    "withdraw_cash": ("customer", "bank"),
    "client_payment": ("payer", "payee"),
    "create_stock": ("owner",),
    "transfer_stock": ("from_agent", "to_agent"),
    "create_delivery_obligation": ("from", "from_agent", "to", "to_agent"),
    "create_payable": ("from", "from_agent", "to", "to_agent"),
    "transfer_claim": ("to_agent",),
}

_ACTION_CONTRACT_FIELDS = {
    "transfer_claim": ("contract_id", "contract_alias"),
    "mint_cash": ("alias",),
    "mint_reserves": ("alias",),
    "create_delivery_obligation": ("alias",),
    "create_payable": ("alias",),
}


def _get_default_mode(system) -> str:
    """Return the configured default-handling mode for the system."""
    return getattr(system, "default_mode", DEFAULT_MODE_FAIL_FAST)


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
    debtor_deposit_ids = []
    for cid in system.state.agents[debtor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "bank_deposit":
            debtor_deposit_ids.append(cid)

    if not debtor_deposit_ids:
        return 0

    available = sum(system.state.contracts[cid].amount for cid in debtor_deposit_ids)
    if available == 0:
        return 0

    pay_amount = min(amount, available)

    debtor_bank_id = None
    creditor_bank_id = None

    if debtor_deposit_ids:
        debtor_bank_id = system.state.contracts[debtor_deposit_ids[0]].liability_issuer_id

    creditor_deposit_ids = []
    for cid in system.state.agents[creditor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "bank_deposit":
            creditor_deposit_ids.append(cid)

    if creditor_deposit_ids:
        creditor_bank_id = system.state.contracts[creditor_deposit_ids[0]].liability_issuer_id
    else:
        creditor_bank_id = debtor_bank_id

    if not debtor_bank_id or not creditor_bank_id:
        return 0

    try:
        client_payment(system, debtor_id, debtor_bank_id, creditor_id, creditor_bank_id, pay_amount)
        return pay_amount
    except ValidationError:
        return 0


def _pay_with_cash(system, debtor_id, creditor_id, amount) -> int:
    """Pay using cash. Returns amount actually paid."""
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
        return 0

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
    """Transfer stock lots from debtor to creditor by SKU using FIFO allocation."""
    available_stocks = []
    for stock_id in system.state.agents[debtor_id].stock_ids:
        stock = system.state.stocks[stock_id]
        if stock.sku == sku:
            available_stocks.append((stock_id, stock.quantity))

    if not available_stocks:
        return 0

    total_available = sum(quantity for _, quantity in available_stocks)
    if total_available == 0:
        return 0

    deliver_quantity = min(required_quantity, total_available)
    remaining_to_deliver = deliver_quantity

    available_stocks.sort(key=lambda x: x[0])

    try:
        for stock_id, stock_quantity in available_stocks:
            if remaining_to_deliver == 0:
                break

            transfer_qty = min(remaining_to_deliver, stock_quantity)
            system._transfer_stock_internal(stock_id, debtor_id, creditor_id, transfer_qty)
            remaining_to_deliver -= transfer_qty

        return deliver_quantity
    except ValidationError:
        return 0


def _remove_contract(system, contract_id):
    """Remove contract from system and update agent registries."""
    contract = system.state.contracts[contract_id]
    contract_kind = contract.kind
    contract_amount = getattr(contract, "amount", 0)

    asset_holder = system.state.agents[contract.asset_holder_id]
    if contract_id in asset_holder.asset_ids:
        asset_holder.asset_ids.remove(contract_id)

    liability_issuer = system.state.agents[contract.liability_issuer_id]
    if contract_id in liability_issuer.liability_ids:
        liability_issuer.liability_ids.remove(contract_id)

    del system.state.contracts[contract_id]

    if contract_kind == "cash":
        system.state.cb_cash_outstanding -= contract_amount
    elif contract_kind == "reserve_deposit":
        system.state.cb_reserves_outstanding -= contract_amount


def _action_references_agent(action_dict, agent_id: str) -> bool:
    """Return True if the scheduled action references the given agent."""
    if not isinstance(action_dict, dict) or len(action_dict) != 1:
        return False

    action_name, payload = next(iter(action_dict.items()))
    if not isinstance(payload, dict):
        return False

    for field in _ACTION_AGENT_FIELDS.get(action_name, ()): 
        value = payload.get(field)
        if isinstance(value, str) and value == agent_id:
            return True
        if isinstance(value, list) and agent_id in value:
            return True
    return False


def _cancel_scheduled_actions_for_agent(
    system,
    agent_id: str,
    cancelled_contract_ids: set[str] | None = None,
    cancelled_aliases: set[str] | None = None,
) -> None:
    """Remove and log scheduled actions that involve a defaulted agent or cancelled contracts."""
    cancelled_contract_ids = cancelled_contract_ids or set()
    cancelled_aliases = cancelled_aliases or set()
    if not system.state.scheduled_actions_by_day:
        return

    for day, actions in list(system.state.scheduled_actions_by_day.items()):
        remaining = []
        for action_dict in actions:
            if _action_references_agent(action_dict, agent_id) or _action_references_contract(action_dict, cancelled_contract_ids, cancelled_aliases):
                action_name = next(iter(action_dict.keys()), "unknown") if isinstance(action_dict, dict) else "unknown"
                system.log(
                    "ScheduledActionCancelled",
                    agent=agent_id,
                    scheduled_day=day,
                    action=action_name,
                    mode=_get_default_mode(system),
                )
                continue
            remaining.append(action_dict)
        if remaining:
            system.state.scheduled_actions_by_day[day] = remaining
        else:
            del system.state.scheduled_actions_by_day[day]


def _action_references_contract(action_dict, contract_ids: set[str], aliases: set[str]) -> bool:
    if not isinstance(action_dict, dict) or len(action_dict) != 1:
        return False
    if not contract_ids and not aliases:
        return False

    action_name, payload = next(iter(action_dict.items()))
    if not isinstance(payload, dict):
        return False

    for field in _ACTION_CONTRACT_FIELDS.get(action_name, ("contract_id", "contract_alias", "alias")):
        value = payload.get(field)
        if isinstance(value, str) and (value in contract_ids or value in aliases):
            return True

    # common fallbacks
    for key in ("contract_id", "contract_alias", "alias"):
        value = payload.get(key)
        if isinstance(value, str) and (value in contract_ids or value in aliases):
            return True

    return False


def _expel_agent(
    system,
    agent_id: str,
    *,
    trigger_contract_id: str | None = None,
    trigger_kind: str | None = None,
    trigger_shortfall: int | None = None,
    cancelled_contract_ids: set[str] | None = None,
    cancelled_aliases: set[str] | None = None,
) -> None:
    """Mark an agent as defaulted, write off obligations, and cancel future actions."""
    if _get_default_mode(system) != DEFAULT_MODE_EXPEL:
        return

    if agent_id in system.state.defaulted_agent_ids:
        return

    agent = system.state.agents.get(agent_id)
    if agent is None:
        return

    if agent.kind == "central_bank":
        raise DefaultError("Central bank cannot default")

    agent.defaulted = True
    system.state.defaulted_agent_ids.add(agent_id)

    system.log(
        "AgentDefaulted",
        agent=agent_id,
        frm=agent_id,
        trigger_contract=trigger_contract_id,
        contract_kind=trigger_kind,
        shortfall=trigger_shortfall,
        mode=_get_default_mode(system),
    )

    cancelled_contract_ids = set(cancelled_contract_ids or [])
    cancelled_aliases = set(cancelled_aliases or [])

    # Remove any aliases provided for already-cancelled contracts
    for alias in list(cancelled_aliases):
        system.state.aliases.pop(alias, None)

    for cid, contract in list(system.state.contracts.items()):
        if contract.liability_issuer_id != agent_id:
            continue
        if trigger_contract_id and cid == trigger_contract_id:
            continue

        alias = get_alias_for_id(system, cid)
        if alias:
            cancelled_aliases.add(alias)
        payload = {
            "contract_id": cid,
            "alias": alias,
            "debtor": contract.liability_issuer_id,
            "creditor": contract.asset_holder_id,
            "contract_kind": contract.kind,
            "amount": getattr(contract, "amount", None),
            "due_day": getattr(contract, "due_day", None),
        }
        if hasattr(contract, "sku"):
            payload["sku"] = getattr(contract, "sku")
        if payload.get("due_day") is None:
            payload.pop("due_day", None)

        system.log("ObligationWrittenOff", **payload)
        _remove_contract(system, cid)
        cancelled_contract_ids.add(cid)
        if alias:
            system.state.aliases.pop(alias, None)

    _cancel_scheduled_actions_for_agent(system, agent_id, cancelled_contract_ids, cancelled_aliases)

    # If every non-central-bank agent has defaulted, halt the simulation with a DefaultError.
    if all(
        (ag.kind == "central_bank") or getattr(ag, "defaulted", False)
        for ag in system.state.agents.values()
    ):
        raise DefaultError("All non-central-bank agents have defaulted")


def settle_due_delivery_obligations(system, day: int):
    """Settle all delivery obligations due today using stock operations."""
    for obligation in list(due_delivery_obligations(system, day)):
        if obligation.id not in system.state.contracts:
            continue

        debtor = system.state.agents[obligation.liability_issuer_id]
        if getattr(debtor, "defaulted", False):
            continue

        creditor = system.state.agents[obligation.asset_holder_id]
        required_sku = obligation.sku
        required_quantity = obligation.amount

        with atomic(system):
            delivered_quantity = _deliver_stock(system, debtor.id, creditor.id, required_sku, required_quantity)

            if delivered_quantity != required_quantity:
                shortage = required_quantity - delivered_quantity
                if _get_default_mode(system) == DEFAULT_MODE_FAIL_FAST:
                    raise DefaultError(
                        f"Insufficient stock to settle delivery obligation {obligation.id}: {shortage} units of {required_sku} still owed"
                    )

                alias = get_alias_for_id(system, obligation.id)
                cancelled_contract_ids = {obligation.id}
                cancelled_aliases = {alias} if alias else set()
                if delivered_quantity > 0:
                    system.log(
                        "PartialSettlement",
                        contract_id=obligation.id,
                        alias=alias,
                        debtor=debtor.id,
                        creditor=creditor.id,
                        contract_kind=obligation.kind,
                        settlement_kind="delivery",
                        delivered_quantity=delivered_quantity,
                        required_quantity=required_quantity,
                        shortfall=shortage,
                        sku=required_sku,
                    )

                system.log(
                    "ObligationDefaulted",
                    contract_id=obligation.id,
                    alias=alias,
                    debtor=debtor.id,
                    creditor=creditor.id,
                    contract_kind=obligation.kind,
                    shortfall=shortage,
                    delivered_quantity=delivered_quantity,
                    required_quantity=required_quantity,
                    sku=required_sku,
                    qty=shortage,
                )

                _remove_contract(system, obligation.id)
                _expel_agent(
                    system,
                    debtor.id,
                    trigger_contract_id=obligation.id,
                    trigger_kind=obligation.kind,
                    trigger_shortfall=shortage,
                    cancelled_contract_ids=cancelled_contract_ids,
                    cancelled_aliases=cancelled_aliases,
                )
                continue

            system._cancel_delivery_obligation_internal(obligation.id)
            alias = get_alias_for_id(system, obligation.id)
            system.log(
                "DeliveryObligationSettled",
                obligation_id=obligation.id,
                contract_id=obligation.id,
                alias=alias,
                debtor=debtor.id,
                creditor=creditor.id,
                sku=required_sku,
                qty=required_quantity,
            )


def settle_due(system, day: int):
    """Settle all obligations due today (payables and delivery obligations)."""
    for payable in list(due_payables(system, day)):
        if payable.id not in system.state.contracts:
            continue

        debtor = system.state.agents[payable.liability_issuer_id]
        if getattr(debtor, "defaulted", False):
            continue

        creditor = system.state.agents[payable.asset_holder_id]
        order = system.policy.settlement_order(debtor)

        remaining = payable.amount
        payments_summary: list[dict] = []

        with atomic(system):
            for method in order:
                if remaining == 0:
                    break

                if method == "bank_deposit":
                    paid_now = _pay_with_deposits(system, debtor.id, creditor.id, remaining)
                elif method == "cash":
                    paid_now = _pay_with_cash(system, debtor.id, creditor.id, remaining)
                elif method == "reserve_deposit":
                    paid_now = _pay_bank_to_bank_with_reserves(system, debtor.id, creditor.id, remaining)
                else:
                    raise ValidationError(f"unknown payment method {method}")

                remaining -= paid_now
                if paid_now > 0:
                    payments_summary.append({"method": method, "amount": paid_now})

            if remaining != 0:
                if _get_default_mode(system) == DEFAULT_MODE_FAIL_FAST:
                    raise DefaultError(f"Insufficient funds to settle payable {payable.id}: {remaining} still owed")

                alias = get_alias_for_id(system, payable.id)
                cancelled_contract_ids = {payable.id}
                cancelled_aliases = {alias} if alias else set()
                amount_paid = payable.amount - remaining

                if amount_paid > 0:
                    payload = {
                        "contract_id": payable.id,
                        "alias": alias,
                        "debtor": debtor.id,
                        "creditor": creditor.id,
                        "contract_kind": payable.kind,
                        "settlement_kind": "payable",
                        "amount_paid": amount_paid,
                        "shortfall": remaining,
                        "original_amount": payable.amount,
                    }
                    if payments_summary:
                        payload["distribution"] = payments_summary
                    system.log("PartialSettlement", **payload)

                system.log(
                    "ObligationDefaulted",
                    contract_id=payable.id,
                    alias=alias,
                    debtor=debtor.id,
                    creditor=creditor.id,
                    contract_kind=payable.kind,
                    shortfall=remaining,
                    amount_paid=amount_paid,
                    original_amount=payable.amount,
                    amount=remaining,
                )

                _remove_contract(system, payable.id)
                _expel_agent(
                    system,
                    debtor.id,
                    trigger_contract_id=payable.id,
                    trigger_kind=payable.kind,
                    trigger_shortfall=remaining,
                    cancelled_contract_ids=cancelled_contract_ids,
                    cancelled_aliases=cancelled_aliases,
                )
                continue

            _remove_contract(system, payable.id)
            alias = get_alias_for_id(system, payable.id)
            system.log(
                "PayableSettled",
                pid=payable.id,
                contract_id=payable.id,
                alias=alias,
                debtor=debtor.id,
                creditor=creditor.id,
                amount=payable.amount,
            )

    settle_due_delivery_obligations(system, day)
