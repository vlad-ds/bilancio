"""Tests for deliverable instruments with due dates."""

import pytest
from decimal import Decimal

from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.household import Household
from bilancio.engines.system import System
from bilancio.engines.settlement import settle_due, settle_due_deliverables
from bilancio.core.errors import DefaultError


def test_deliverable_with_due_day():
    """Test that deliverables can have due_day field."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Create deliverable with due_day using system method
    deliverable_id = system.create_deliverable(
        issuer_id="supplier",
        holder_id="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    deliverable = system.state.contracts[deliverable_id]
    assert deliverable.due_day == 1
    assert deliverable.sku == "WIDGET"
    assert deliverable.amount == 10


def test_settle_deliverables_due_today():
    """Test settling deliverables that are due."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier some widgets to deliver
    system.create_deliverable(
        issuer_id="supplier",
        holder_id="supplier",
        sku="WIDGET",
        quantity=20,
        unit_price=Decimal("5")
    )
    
    # Create deliverable obligation due on day 1
    obligation_id = system.create_deliverable(
        issuer_id="supplier",  # Supplier must deliver
        holder_id="customer",  # Customer has claim to receive
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    # Settle deliverables due on day 1
    settle_due_deliverables(system, day=1)
    
    # Check that obligation is settled
    assert obligation_id not in system.state.contracts
    
    # Check that customer received the widgets
    customer_widgets = [c for c in system.state.contracts.values() 
                        if c.asset_holder_id == "customer" and c.kind == "deliverable"]
    assert len(customer_widgets) == 1
    assert customer_widgets[0].amount == 10
    assert customer_widgets[0].sku == "WIDGET"
    
    # Check that supplier's stock is reduced
    supplier_widgets = [c for c in system.state.contracts.values()
                        if c.asset_holder_id == "supplier" and c.kind == "deliverable"]
    assert len(supplier_widgets) == 1
    assert supplier_widgets[0].amount == 10  # 20 - 10 delivered


def test_settle_deliverables_insufficient_goods():
    """Test that DefaultError is raised when insufficient goods to deliver."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier only 5 widgets
    system.create_deliverable(
        issuer_id="supplier",
        holder_id="supplier",
        sku="WIDGET",
        quantity=5,
        unit_price=Decimal("5")
    )
    
    # Create deliverable obligation for 10 widgets due on day 1
    system.create_deliverable(
        issuer_id="supplier",
        holder_id="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    # Should raise DefaultError due to insufficient widgets
    with pytest.raises(DefaultError) as exc_info:
        settle_due_deliverables(system, day=1)
    
    assert "Insufficient deliverables" in str(exc_info.value)
    assert "5 units of WIDGET still owed" in str(exc_info.value)


def test_settle_deliverables_wrong_sku():
    """Test that deliverables with wrong SKU are not used for settlement."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier gadgets instead of widgets
    system.create_deliverable(
        issuer_id="supplier",
        holder_id="supplier",
        sku="GADGET",
        quantity=20,
        unit_price=Decimal("5")
    )
    
    # Create deliverable obligation for widgets due on day 1
    system.create_deliverable(
        issuer_id="supplier",
        holder_id="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    # Should raise DefaultError because supplier has no widgets
    with pytest.raises(DefaultError) as exc_info:
        settle_due_deliverables(system, day=1)
    
    assert "Insufficient deliverables" in str(exc_info.value)


def test_settle_deliverables_not_due():
    """Test that deliverables not due today are not settled."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier widgets
    widgets_id = system.create_deliverable(
        issuer_id="supplier",
        holder_id="supplier",
        sku="WIDGET",
        quantity=20,
        unit_price=Decimal("5")
    )
    
    # Create deliverable obligation due on day 2 (not today)
    obligation_id = system.create_deliverable(
        issuer_id="supplier",
        holder_id="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=2  # Due on day 2, not day 1
    )
    
    # Settle deliverables due on day 1 (should do nothing)
    settle_due_deliverables(system, day=1)
    
    # Check that obligation is still there
    assert obligation_id in system.state.contracts
    
    # Check that no widgets were transferred (exclude the obligation itself)
    customer_widgets = [c for c in system.state.contracts.values()
                        if c.asset_holder_id == "customer" and c.kind == "deliverable" 
                        and c.id != obligation_id]
    assert len(customer_widgets) == 0
    
    # Supplier still has all widgets
    assert system.state.contracts[widgets_id].amount == 20


def test_deliverables_without_due_day_not_settled():
    """Test that deliverables without due_day are not affected by settlement."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier widgets
    system.create_deliverable(
        issuer_id="supplier",
        holder_id="supplier",
        sku="WIDGET",
        quantity=20,
        unit_price=Decimal("5")
    )
    
    # Create deliverable obligation WITHOUT due_day
    obligation_id = system.create_deliverable(
        issuer_id="supplier",
        holder_id="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5")
        # Note: no due_day specified
    )
    
    # Settle deliverables for any day - should not affect this obligation
    settle_due_deliverables(system, day=1)
    settle_due_deliverables(system, day=100)
    
    # Check that obligation is still there (not settled)
    assert obligation_id in system.state.contracts
    
    # Check that no widgets were transferred
    customer_widgets = [c for c in system.state.contracts.values()
                        if c.asset_holder_id == "customer" and c.kind == "deliverable" 
                        and c.id != obligation_id]
    assert len(customer_widgets) == 0
    
    # Supplier still has all widgets
    supplier_widgets = [c for c in system.state.contracts.values()
                        if c.asset_holder_id == "supplier" and c.kind == "deliverable"
                        and c.liability_issuer_id == "supplier"]
    assert len(supplier_widgets) == 1
    assert supplier_widgets[0].amount == 20


def test_negative_due_day_validation():
    """Test that negative due_day values are rejected."""
    system = System()
    
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # This should work (non-negative)
    deliverable_id = system.create_deliverable(
        issuer_id="supplier",
        holder_id="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=0  # Zero is valid
    )
    assert system.state.contracts[deliverable_id].due_day == 0


def test_settle_due_handles_both_payables_and_deliverables():
    """Test that settle_due handles both payables and deliverables."""
    system = System()
    
    # Create agents including banks for payables
    bank = Bank(id="bank", name="Bank", kind="bank")
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(bank)
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier widgets
    system.create_deliverable(
        issuer_id="supplier",
        holder_id="supplier",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5")
    )
    
    # Create deliverable obligation due on day 1
    deliverable_obligation_id = system.create_deliverable(
        issuer_id="supplier",
        holder_id="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    # Run the main settle_due function
    settle_due(system, day=1)
    
    # Check that deliverable obligation is settled
    assert deliverable_obligation_id not in system.state.contracts
    
    # Check that customer received the widgets
    customer_widgets = [c for c in system.state.contracts.values()
                        if c.asset_holder_id == "customer" and c.kind == "deliverable"]
    assert len(customer_widgets) == 1
    assert customer_widgets[0].amount == 10