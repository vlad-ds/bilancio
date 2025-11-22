"""Ticket movement helpers for dealer/VBT trades against the System ledger."""

from __future__ import annotations

from typing import Optional

from bilancio.engines.system import System
from bilancio.core.errors import ValidationError


class TicketOps:
    """Adapter to move concrete ticket IDs on customer/dealer/VBT trades."""

    def __init__(self, system: System):
        self.system = system

    def _pick_one(self, owner: str, bucket_id: str) -> str:
        """Deterministically pick a ticket ID held by owner in the bucket."""
        tickets = sorted(self.system.tickets_of(owner, bucket_id=bucket_id))
        if not tickets:
            raise ValidationError(f"no ticket available for owner={owner} bucket={bucket_id}")
        return tickets[0]

    def customer_sell_to_dealer(self, customer_id: str, dealer_id: str, bucket_id: str) -> str:
        """Customer sells one ticket to dealer; returns ticket_id moved."""
        tid = self._pick_one(customer_id, bucket_id)
        self.system.transfer_ticket(tid, from_agent_id=customer_id, to_agent_id=dealer_id)
        return tid

    def customer_buy_from_dealer(self, customer_id: str, dealer_id: str, bucket_id: str) -> str:
        """Customer buys one ticket from dealer; returns ticket_id moved."""
        tid = self._pick_one(dealer_id, bucket_id)
        self.system.transfer_ticket(tid, from_agent_id=dealer_id, to_agent_id=customer_id)
        return tid

    def pass_through_sell_to_vbt(self, customer_id: str, vbt_id: str, bucket_id: str) -> str:
        """Dealer pins bid: customer sells, ticket goes from customer to VBT."""
        tid = self._pick_one(customer_id, bucket_id)
        self.system.transfer_ticket(tid, from_agent_id=customer_id, to_agent_id=vbt_id)
        return tid

    def pass_through_buy_from_vbt(self, customer_id: str, vbt_id: str, bucket_id: str) -> str:
        """Dealer pins ask: customer buys, ticket goes from VBT to customer."""
        tid = self._pick_one(vbt_id, bucket_id)
        self.system.transfer_ticket(tid, from_agent_id=vbt_id, to_agent_id=customer_id)
        return tid

    def rebucket_if_trader(self, ticket_id: str, new_bucket_id: str) -> None:
        """Re-label a ticket when holder is a trader (no internal dealer transfer)."""
        self.system.rebucket_ticket(ticket_id, new_bucket_id=new_bucket_id)
