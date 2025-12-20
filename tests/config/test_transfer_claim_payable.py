"""Tests for transfer_claim action with payables.

Verifies that transfer_claim correctly uses holder_id for Payables
(secondary market transfer pattern) instead of modifying asset_holder_id.
This is consistent with dealer_integration.py behavior.
"""

import pytest

from bilancio.engines.system import System
from bilancio.config.apply import apply_action
from bilancio.domain.agents import CentralBank, Firm, Household
from bilancio.domain.instruments.credit import Payable
from bilancio.domain.instruments.delivery import DeliveryObligation


def _make_system_with_agents():
    """Create a system with standard test agents."""
    system = System()
    cb = CentralBank(id="CB", name="Central Bank", kind="central_bank")
    f1 = Firm(id="F1", name="Firm 1", kind="firm")
    f2 = Firm(id="F2", name="Firm 2", kind="firm")
    f3 = Firm(id="F3", name="Firm 3", kind="firm")
    system.add_agent(cb)
    system.add_agent(f1)
    system.add_agent(f2)
    system.add_agent(f3)
    return system


def _apply_action(system, action_dict):
    """Helper to apply an action to the system."""
    apply_action(system, action_dict, system.state.agents)


class TestTransferClaimPayable:
    """Test transfer_claim for Payable instruments."""

    def test_transfer_claim_payable_uses_holder_id(self):
        """When transferring a payable, holder_id should be set (not asset_holder_id).

        This keeps asset_holder_id as the original creditor, consistent with
        the secondary market pattern in dealer_integration.py.
        """
        system = _make_system_with_agents()

        # Create a payable: F1 owes F2
        payable = Payable(
            id=system.new_contract_id("PAY"),
            kind="payable",
            amount=100,
            denom="X",
            asset_holder_id="F2",  # Original creditor
            liability_issuer_id="F1",  # Debtor
            due_day=5,
        )
        system.add_contract(payable)
        system.state.aliases["TEST_PAY"] = payable.id

        # Transfer claim from F2 to F3
        action_dict = {"transfer_claim": {"contract_alias": "TEST_PAY", "to_agent": "F3"}}
        _apply_action(system, action_dict)

        # Verify: asset_holder_id should remain unchanged (original creditor)
        assert payable.asset_holder_id == "F2", \
            "asset_holder_id should remain as original creditor"

        # Verify: holder_id should be set to the new holder
        assert payable.holder_id == "F3", \
            "holder_id should be set to new holder for secondary market transfer"

        # Verify: effective_creditor should return the new holder
        assert payable.effective_creditor == "F3", \
            "effective_creditor should return holder_id when set"

        # Verify: registry updated - payable moved from F2 to F3
        assert payable.id in system.state.agents["F3"].asset_ids
        assert payable.id not in system.state.agents["F2"].asset_ids

    def test_transfer_claim_payable_chained_transfers(self):
        """Test that multiple transfers correctly chain holder_id updates."""
        system = _make_system_with_agents()

        payable = Payable(
            id=system.new_contract_id("PAY"),
            kind="payable",
            amount=50,
            denom="X",
            asset_holder_id="F1",
            liability_issuer_id="CB",
            due_day=3,
        )
        system.add_contract(payable)
        system.state.aliases["CHAIN_PAY"] = payable.id

        # First transfer: F1 -> F2
        _apply_action(system, {"transfer_claim": {"contract_alias": "CHAIN_PAY", "to_agent": "F2"}})

        assert payable.asset_holder_id == "F1", "Original creditor unchanged"
        assert payable.holder_id == "F2", "First transfer sets holder_id"
        assert payable.id in system.state.agents["F2"].asset_ids

        # Second transfer: F2 -> F3
        _apply_action(system, {"transfer_claim": {"contract_alias": "CHAIN_PAY", "to_agent": "F3"}})

        assert payable.asset_holder_id == "F1", "Original creditor still unchanged"
        assert payable.holder_id == "F3", "Second transfer updates holder_id"
        assert payable.effective_creditor == "F3"
        assert payable.id in system.state.agents["F3"].asset_ids
        assert payable.id not in system.state.agents["F2"].asset_ids

    def test_transfer_claim_payable_preserves_maturity_distance(self):
        """Transfer should preserve maturity_distance for rollover support."""
        system = _make_system_with_agents()

        payable = Payable(
            id=system.new_contract_id("PAY"),
            kind="payable",
            amount=100,
            denom="X",
            asset_holder_id="F2",
            liability_issuer_id="F1",
            due_day=10,
            maturity_distance=7,  # Original maturity for rollover
        )
        system.add_contract(payable)
        system.state.aliases["MAT_PAY"] = payable.id

        _apply_action(system, {"transfer_claim": {"contract_alias": "MAT_PAY", "to_agent": "F3"}})

        # maturity_distance should be preserved
        assert payable.maturity_distance == 7, "maturity_distance should be preserved"
        # due_day should be preserved
        assert payable.due_day == 10, "due_day should be preserved"


class TestTransferClaimDeliveryObligation:
    """Test transfer_claim for DeliveryObligation instruments."""

    def test_transfer_claim_delivery_uses_asset_holder_id(self):
        """For non-Payable instruments, asset_holder_id should be modified."""
        system = _make_system_with_agents()

        obligation = DeliveryObligation(
            id=system.new_contract_id("DEL"),
            kind="delivery_obligation",
            amount=10,  # quantity of items to deliver
            denom="X",
            asset_holder_id="F2",  # Recipient of delivery
            liability_issuer_id="F1",  # Obligated to deliver
            sku="WIDGET",
            unit_price=100,
            due_day=5,
        )
        system.add_contract(obligation)
        system.state.aliases["TEST_DEL"] = obligation.id

        # Transfer the obligation to F3
        _apply_action(system, {"transfer_claim": {"contract_alias": "TEST_DEL", "to_agent": "F3"}})

        # For DeliveryObligation, asset_holder_id should be modified
        # (no secondary market pattern for delivery obligations)
        assert obligation.asset_holder_id == "F3", \
            "DeliveryObligation should update asset_holder_id directly"
        assert obligation.id in system.state.agents["F3"].asset_ids
        assert obligation.id not in system.state.agents["F2"].asset_ids


class TestTransferClaimEvents:
    """Test that transfer_claim logs correct events."""

    def test_claim_transferred_event_logged(self):
        """Verify ClaimTransferred event is logged with correct details."""
        system = _make_system_with_agents()

        payable = Payable(
            id=system.new_contract_id("PAY"),
            kind="payable",
            amount=200,
            denom="USD",
            asset_holder_id="F1",
            liability_issuer_id="CB",
            due_day=3,
        )
        system.add_contract(payable)
        system.state.aliases["EVENT_PAY"] = payable.id

        _apply_action(system, {"transfer_claim": {"contract_alias": "EVENT_PAY", "to_agent": "F2"}})

        # Find the ClaimTransferred event
        events = [e for e in system.state.events if e.get("kind") == "ClaimTransferred"]
        assert len(events) == 1, "Should log exactly one ClaimTransferred event"

        event = events[0]
        assert event["contract_id"] == payable.id
        assert event["frm"] == "F1"  # Original holder
        assert event["to"] == "F2"
        assert event["contract_kind"] == "payable"
        assert event["amount"] == 200
        assert event["alias"] == "EVENT_PAY"
