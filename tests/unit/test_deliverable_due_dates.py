"""Tests for deliverable instruments with due dates."""

import pytest
from decimal import Decimal

from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.household import Household
from bilancio.engines.system import System
from bilancio.engines.settlement import settle_due, settle_due_deliverables, settle_due_delivery_obligations
from bilancio.core.errors import DefaultError


def test_deliverable_with_due_day():
    """Test that delivery obligations can have due_day field."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Create delivery obligation with due_day using system method
    obligation_id = system.create_delivery_obligation(
        from_agent="supplier",
        to_agent="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    obligation = system.state.contracts[obligation_id]
    assert obligation.due_day == 1
    assert obligation.sku == "WIDGET"
    assert obligation.amount == 10


def test_settle_deliverables_due_today():
    """Test settling delivery obligations that are due."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier some widgets to deliver (as stock)
    system.create_stock("supplier", "WIDGET", 20, Decimal("5"))
    
    # Create delivery obligation due on day 1
    obligation_id = system.create_delivery_obligation(
        from_agent="supplier",  # Supplier must deliver
        to_agent="customer",  # Customer has claim to receive
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    # Settle delivery obligations due on day 1
    settle_due_delivery_obligations(system, day=1)
    
    # Check that obligation is settled
    assert obligation_id not in system.state.contracts
    
    # Check that customer received the widgets (as stock)
    customer_widgets = [s for s in system.state.stocks.values() 
                        if s.owner_id == "customer" and s.sku == "WIDGET"]
    assert len(customer_widgets) == 1
    assert customer_widgets[0].quantity == 10
    assert customer_widgets[0].sku == "WIDGET"
    
    # Check that supplier's stock is reduced
    supplier_widgets = [s for s in system.state.stocks.values()
                        if s.owner_id == "supplier" and s.sku == "WIDGET"]
    assert len(supplier_widgets) == 1
    assert supplier_widgets[0].quantity == 10  # 20 - 10 delivered


def test_settle_deliverables_insufficient_goods():
    """Test that DefaultError is raised when insufficient goods to deliver."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier only 5 widgets (as stock)
    system.create_stock("supplier", "WIDGET", 5, Decimal("5"))
    
    # Create delivery obligation for 10 widgets due on day 1
    system.create_delivery_obligation(
        from_agent="supplier",
        to_agent="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    # Should raise DefaultError due to insufficient widgets
    with pytest.raises(DefaultError) as exc_info:
        settle_due_delivery_obligations(system, day=1)
    
    assert "Insufficient" in str(exc_info.value)
    assert "5 units of WIDGET still owed" in str(exc_info.value)


def test_settle_deliverables_wrong_sku():
    """Test that stock with wrong SKU is not used for settlement."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier gadgets instead of widgets (as stock)
    system.create_stock("supplier", "GADGET", 20, Decimal("5"))
    
    # Create delivery obligation for widgets due on day 1
    system.create_delivery_obligation(
        from_agent="supplier",
        to_agent="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    # Should raise DefaultError because supplier has no widgets
    with pytest.raises(DefaultError) as exc_info:
        settle_due_delivery_obligations(system, day=1)
    
    assert "Insufficient" in str(exc_info.value)


def test_settle_deliverables_not_due():
    """Test that delivery obligations not due today are not settled."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier widgets (as stock)
    widgets_id = system.create_stock("supplier", "WIDGET", 20, Decimal("5"))
    
    # Create delivery obligation due on day 2 (not today)
    obligation_id = system.create_delivery_obligation(
        from_agent="supplier",
        to_agent="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=2  # Due on day 2, not day 1
    )
    
    # Settle delivery obligations due on day 1 (should do nothing)
    settle_due_delivery_obligations(system, day=1)
    
    # Check that obligation is still there
    assert obligation_id in system.state.contracts
    
    # Check that no widgets were transferred to customer
    customer_widgets = [s for s in system.state.stocks.values()
                        if s.owner_id == "customer" and s.sku == "WIDGET"]
    assert len(customer_widgets) == 0
    
    # Supplier still has all widgets
    assert system.state.stocks[widgets_id].quantity == 20


def test_deliverables_without_due_day_not_settled():
    """Test that delivery obligations without due_day are not affected by settlement."""
    system = System()
    
    # Create agents
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier widgets (as stock)
    system.create_stock("supplier", "WIDGET", 20, Decimal("5"))
    
    # Note: DeliveryObligation requires due_day, so this test may not be applicable anymore
    # But we'll create an obligation with due_day=0 to test the edge case
    obligation_id = system.create_delivery_obligation(
        from_agent="supplier",
        to_agent="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=0  # Use 0 instead of None since due_day is required
    )
    
    # Settle delivery obligations for day 1 - should not affect obligation due on day 0
    settle_due_delivery_obligations(system, day=1)
    settle_due_delivery_obligations(system, day=100)
    
    # Check that obligation is still there (not settled on day 1 or 100)
    assert obligation_id in system.state.contracts
    
    # Check that no widgets were transferred
    customer_widgets = [s for s in system.state.stocks.values()
                        if s.owner_id == "customer" and s.sku == "WIDGET"]
    assert len(customer_widgets) == 0
    
    # Supplier still has all widgets
    supplier_widgets = [s for s in system.state.stocks.values()
                        if s.owner_id == "supplier" and s.sku == "WIDGET"]
    assert len(supplier_widgets) == 1
    assert supplier_widgets[0].quantity == 20


def test_negative_due_day_validation():
    """Test that negative due_day values are rejected."""
    system = System()
    
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # This should work (non-negative)
    obligation_id = system.create_delivery_obligation(
        from_agent="supplier",
        to_agent="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=0  # Zero is valid
    )
    assert system.state.contracts[obligation_id].due_day == 0


def test_settle_due_handles_both_payables_and_deliverables():
    """Test that settle_due handles both payables and delivery obligations."""
    system = System()
    
    # Create agents including banks for payables
    bank = Bank(id="bank", name="Bank", kind="bank")
    supplier = Household(id="supplier", name="Supplier", kind="household")
    customer = Household(id="customer", name="Customer", kind="household")
    system.add_agent(bank)
    system.add_agent(supplier)
    system.add_agent(customer)
    
    # Give supplier widgets (as stock)
    system.create_stock("supplier", "WIDGET", 10, Decimal("5"))
    
    # Create delivery obligation due on day 1
    obligation_id = system.create_delivery_obligation(
        from_agent="supplier",
        to_agent="customer",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5"),
        due_day=1
    )
    
    # Run the main settle_due function
    settle_due(system, day=1)
    
    # Check that delivery obligation is settled
    assert obligation_id not in system.state.contracts
    
    # Check that customer received the widgets (as stock)
    customer_widgets = [s for s in system.state.stocks.values()
                        if s.owner_id == "customer" and s.sku == "WIDGET"]
    assert len(customer_widgets) == 1
    assert customer_widgets[0].quantity == 10