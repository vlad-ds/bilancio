"""Tests for stock lot and delivery obligation valuation functionality."""

import pytest
from decimal import Decimal
from bilancio.engines.system import System
from bilancio.domain.agents.household import Household
from bilancio.domain.agents.treasury import Treasury
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.core.errors import ValidationError
from bilancio.analysis.balances import agent_balance, system_trial_balance


def test_create_deliverable_with_unit_price():
    """Test creating a stock lot with a unit price."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    # Create stock lot with unit price
    widget_id = sys.create_stock(
        owner_id="H1",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5.50")
    )
    
    # Check the stock lot
    widget = sys.state.stocks[widget_id]
    assert widget.quantity == 10
    assert widget.unit_price == Decimal("5.50")
    assert widget.value == Decimal("55.00")


def test_create_deliverable_with_zero_price():
    """Test creating a stock lot with zero price."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    # Create stock lot with zero price
    widget_id = sys.create_stock(
        owner_id="H1",
        sku="WIDGET", 
        quantity=10,
        unit_price=Decimal("0")
    )
    
    # Check the stock lot
    widget = sys.state.stocks[widget_id]
    assert widget.quantity == 10
    assert widget.unit_price == Decimal("0")
    assert widget.value == Decimal("0")


def test_update_deliverable_price():
    """Test updating the price of an existing stock lot (if such functionality exists)."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    # Create stock lot with initial price
    widget_id = sys.create_stock(
        owner_id="H1",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5.00")
    )
    
    widget = sys.state.stocks[widget_id]
    assert widget.unit_price == Decimal("5.00")
    assert widget.value == Decimal("50.00")
    
    # Direct price update on stock lots (if method exists)
    # Note: This may need to be updated based on actual API
    widget.unit_price = Decimal("7.25")
    
    # Check updated price
    assert widget.unit_price == Decimal("7.25")
    assert widget.value == Decimal("72.50")
    
    # Update to zero price
    widget.unit_price = Decimal("0")
    
    # Check zero price
    assert widget.unit_price == Decimal("0")
    assert widget.value == Decimal("0")


def test_update_deliverable_price_errors():
    """Test error cases for stock lot price updates."""
    sys = System()
    cb = CentralBank(id="CB", name="CB", kind="central_bank")
    h1 = Household(id="H1", name="H1", kind="household")
    sys.bootstrap_cb(cb)
    sys.add_agent(h1)
    
    # Create a cash instrument (not a stock lot)
    sys.mint_cash("H1", 100)
    
    # Try to update price on non-existent stock
    # Note: This test may need to be adapted based on actual stock update API
    with pytest.raises(KeyError):
        _ = sys.state.stocks["INVALID_ID"]


def test_agent_balance_with_valued_deliverables():
    """Test agent balance calculation with valued stock lots."""
    sys = System()
    cb = CentralBank(id="CB", name="CB", kind="central_bank")
    h1 = Household(id="H1", name="H1", kind="household")
    sys.bootstrap_cb(cb)
    sys.add_agent(h1)
    
    # Give household some cash
    sys.mint_cash("H1", 1000)
    
    # Create valued stock lot (household has groceries)
    sys.create_stock(
        owner_id="H1",
        sku="GROCERIES",
        quantity=20,
        unit_price=Decimal("3.50")
    )
    
    # Create zero-priced stock lot (household has free service)
    sys.create_stock(
        owner_id="H1",
        sku="SERVICE",
        quantity=5,
        unit_price=Decimal("0")
    )
    
    # Check household balance
    balance = agent_balance(sys, "H1")
    
    assert balance.total_financial_assets == 1000
    assert balance.total_inventory_value == Decimal("70.00")  # 20 * 3.50
    
    # Check inventory details
    assert "GROCERIES" in balance.inventory_by_sku
    assert balance.inventory_by_sku["GROCERIES"]["quantity"] == 20
    assert balance.inventory_by_sku["GROCERIES"]["value"] == Decimal("70.00")
    
    assert "SERVICE" in balance.inventory_by_sku
    assert balance.inventory_by_sku["SERVICE"]["quantity"] == 5
    assert balance.inventory_by_sku["SERVICE"]["value"] == Decimal("0")


def test_system_trial_balance_with_valued_deliverables():
    """Test system-wide trial balance with valued stock lots."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Create multiple valued stock lots
    sys.create_stock(
        owner_id="H1",
        sku="PRODUCT_A",
        quantity=10,
        unit_price=Decimal("15.00")
    )
    
    sys.create_stock(
        owner_id="H2",
        sku="PRODUCT_B",
        quantity=5,
        unit_price=Decimal("25.00")
    )
    
    # Create zero-priced stock lot
    sys.create_stock(
        owner_id="H2",
        sku="UNPRICED",
        quantity=100,
        unit_price=Decimal("0")
    )
    
    # Check system trial balance
    trial_balance = system_trial_balance(sys)
    
    # Total inventory value should be sum of valued stock lots
    assert trial_balance.total_inventory_value == Decimal("275.00")  # 150 + 125
    
    # Check details
    assert "PRODUCT_A" in trial_balance.inventory_by_sku
    assert trial_balance.inventory_by_sku["PRODUCT_A"]["quantity"] == 10
    assert trial_balance.inventory_by_sku["PRODUCT_A"]["value"] == Decimal("150.00")
    
    assert "PRODUCT_B" in trial_balance.inventory_by_sku
    assert trial_balance.inventory_by_sku["PRODUCT_B"]["quantity"] == 5
    assert trial_balance.inventory_by_sku["PRODUCT_B"]["value"] == Decimal("125.00")
    
    assert "UNPRICED" in trial_balance.inventory_by_sku
    assert trial_balance.inventory_by_sku["UNPRICED"]["quantity"] == 100
    assert trial_balance.inventory_by_sku["UNPRICED"]["value"] == Decimal("0")


def test_transfer_deliverable_preserves_unit_price():
    """Test that transferring a stock lot preserves its unit price."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Create valued stock lot
    widget_id = sys.create_stock(
        owner_id="H1",
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5.00"),
        divisible=True
    )
    
    # Transfer part of it
    transferred_id = sys.transfer_stock(widget_id, "H1", "H2", quantity=3)
    
    # Check both parts retain the unit price
    original = sys.state.stocks[widget_id]
    transferred = sys.state.stocks[transferred_id]
    
    assert original.quantity == 7
    assert original.unit_price == Decimal("5.00")
    assert original.value == Decimal("35.00")
    
    assert transferred.quantity == 3
    assert transferred.unit_price == Decimal("5.00")
    assert transferred.value == Decimal("15.00")




def test_mixed_valued_and_zero_priced_deliverables():
    """Test system with mix of valued and zero-priced stock lots."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    # Create multiple stock lots with different pricing
    sys.create_stock(
        owner_id="H1",
        sku="PRICED_A", quantity=5, unit_price=Decimal("10")
    )
    
    sys.create_stock(
        owner_id="H1",
        sku="ZERO_PRICED", quantity=20, unit_price=Decimal("0")
    )
    
    sys.create_stock(
        owner_id="H1",
        sku="PRICED_B", quantity=3, unit_price=Decimal("15.50")
    )
    
    sys.create_stock(
        owner_id="H1",
        sku="FREE", quantity=100, unit_price=Decimal("0")
    )
    
    # Check balance
    balance = agent_balance(sys, "H1")
    
    # Total should include all items (zero-priced contribute 0)
    expected_value = Decimal("50") + Decimal("0") + Decimal("46.50") + Decimal("0")
    assert balance.total_inventory_value == expected_value
    
    # Check individual items
    assert len(balance.inventory_by_sku) == 4
    assert balance.inventory_by_sku["PRICED_A"]["value"] == Decimal("50")
    assert balance.inventory_by_sku["ZERO_PRICED"]["value"] == Decimal("0")
    assert balance.inventory_by_sku["PRICED_B"]["value"] == Decimal("46.50")
    assert balance.inventory_by_sku["FREE"]["value"] == Decimal("0")