"""Tests for deliverable valuation functionality."""

import pytest
from decimal import Decimal
from bilancio.engines.system import System
from bilancio.domain.agents.household import Household
from bilancio.domain.agents.treasury import Treasury
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.core.errors import ValidationError
from bilancio.analysis.balances import agent_balance, system_trial_balance


def test_create_deliverable_with_unit_price():
    """Test creating a deliverable with a unit price."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    # Create deliverable with unit price
    widget_id = sys.create_deliverable(
        issuer_id="H1",
        holder_id="H1", 
        sku="WIDGET",
        quantity=10,
        unit_price=Decimal("5.50")
    )
    
    # Check the deliverable
    widget = sys.state.contracts[widget_id]
    assert widget.amount == 10
    assert widget.unit_price == Decimal("5.50")
    assert widget.valued_amount == Decimal("55.00")


def test_create_deliverable_without_unit_price():
    """Test creating a deliverable without a unit price (backward compatibility)."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    # Create deliverable without unit price
    widget_id = sys.create_deliverable(
        issuer_id="H1",
        holder_id="H1",
        sku="WIDGET", 
        quantity=10
    )
    
    # Check the deliverable
    widget = sys.state.contracts[widget_id]
    assert widget.amount == 10
    assert widget.unit_price is None
    assert widget.valued_amount is None


def test_update_deliverable_price():
    """Test updating the price of an existing deliverable."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    # Create deliverable without price
    widget_id = sys.create_deliverable(
        issuer_id="H1",
        holder_id="H1",
        sku="WIDGET",
        quantity=10
    )
    
    widget = sys.state.contracts[widget_id]
    assert widget.unit_price is None
    assert widget.valued_amount is None
    
    # Update price
    sys.update_deliverable_price(widget_id, Decimal("7.25"))
    
    # Check updated price
    widget = sys.state.contracts[widget_id]
    assert widget.unit_price == Decimal("7.25")
    assert widget.valued_amount == Decimal("72.50")
    
    # Clear price
    sys.update_deliverable_price(widget_id, None)
    
    # Check cleared price
    widget = sys.state.contracts[widget_id]
    assert widget.unit_price is None
    assert widget.valued_amount is None


def test_update_deliverable_price_errors():
    """Test error cases for update_deliverable_price."""
    sys = System()
    cb = CentralBank(id="CB", name="CB", kind="central_bank")
    h1 = Household(id="H1", name="H1", kind="household")
    sys.bootstrap_cb(cb)
    sys.add_agent(h1)
    
    # Create a cash instrument (not a deliverable)
    sys.mint_cash("H1", 100)
    cash_id = list(h1.asset_ids)[0]
    
    # Try to update price on non-deliverable
    with pytest.raises(ValidationError, match="not a deliverable"):
        sys.update_deliverable_price(cash_id, Decimal("5"))
    
    # Try to update price on non-existent instrument
    with pytest.raises(ValidationError, match="instrument not found"):
        sys.update_deliverable_price("INVALID_ID", Decimal("5"))


def test_agent_balance_with_valued_deliverables():
    """Test agent balance calculation with valued deliverables."""
    sys = System()
    cb = CentralBank(id="CB", name="CB", kind="central_bank")
    h1 = Household(id="H1", name="H1", kind="household")
    t1 = Treasury(id="T1", name="T1", kind="treasury")
    sys.bootstrap_cb(cb)
    sys.add_agent(h1)
    sys.add_agent(t1)
    
    # Give household some cash
    sys.mint_cash("H1", 1000)
    
    # Create valued deliverable (household has groceries)
    sys.create_deliverable(
        issuer_id="T1",
        holder_id="H1",
        sku="GROCERIES",
        quantity=20,
        unit_price=Decimal("3.50")
    )
    
    # Create unvalued deliverable (household has unpriced service)
    sys.create_deliverable(
        issuer_id="T1",
        holder_id="H1",
        sku="SERVICE",
        quantity=5
    )
    
    # Check household balance
    balance = agent_balance(sys, "H1")
    
    assert balance.total_financial_assets == 1000
    assert balance.total_nonfinancial_value == Decimal("70.00")  # 20 * 3.50
    
    # Check non-financial assets details
    assert "GROCERIES" in balance.nonfinancial_assets_by_kind
    assert balance.nonfinancial_assets_by_kind["GROCERIES"]["quantity"] == 20
    assert balance.nonfinancial_assets_by_kind["GROCERIES"]["value"] == Decimal("70.00")
    
    assert "SERVICE" in balance.nonfinancial_assets_by_kind
    assert balance.nonfinancial_assets_by_kind["SERVICE"]["quantity"] == 5
    assert balance.nonfinancial_assets_by_kind["SERVICE"]["value"] is None


def test_system_trial_balance_with_valued_deliverables():
    """Test system-wide trial balance with valued deliverables."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    t1 = Treasury(id="T1", name="T1", kind="treasury")
    sys.add_agent(h1)
    sys.add_agent(h2)
    sys.add_agent(t1)
    
    # Create multiple valued deliverables
    sys.create_deliverable(
        issuer_id="T1",
        holder_id="H1",
        sku="PRODUCT_A",
        quantity=10,
        unit_price=Decimal("15.00")
    )
    
    sys.create_deliverable(
        issuer_id="T1", 
        holder_id="H2",
        sku="PRODUCT_B",
        quantity=5,
        unit_price=Decimal("25.00")
    )
    
    # Create unvalued deliverable
    sys.create_deliverable(
        issuer_id="H1",
        holder_id="H2",
        sku="UNPRICED",
        quantity=100
    )
    
    # Check system trial balance
    trial_balance = system_trial_balance(sys)
    
    # Total non-financial value should be sum of valued deliverables
    assert trial_balance.total_nonfinancial_value == Decimal("275.00")  # 150 + 125
    
    # Check details
    assert "PRODUCT_A" in trial_balance.nonfinancial_assets_by_kind
    assert trial_balance.nonfinancial_assets_by_kind["PRODUCT_A"]["quantity"] == 10
    assert trial_balance.nonfinancial_assets_by_kind["PRODUCT_A"]["value"] == Decimal("150.00")
    
    assert "PRODUCT_B" in trial_balance.nonfinancial_assets_by_kind
    assert trial_balance.nonfinancial_assets_by_kind["PRODUCT_B"]["quantity"] == 5
    assert trial_balance.nonfinancial_assets_by_kind["PRODUCT_B"]["value"] == Decimal("125.00")
    
    assert "UNPRICED" in trial_balance.nonfinancial_assets_by_kind
    assert trial_balance.nonfinancial_assets_by_kind["UNPRICED"]["quantity"] == 100
    assert trial_balance.nonfinancial_assets_by_kind["UNPRICED"]["value"] is None


def test_transfer_deliverable_preserves_unit_price():
    """Test that transferring a deliverable preserves its unit price."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Create valued deliverable
    widget_id = sys.create_deliverable(
        issuer_id="H1",
        holder_id="H1",
        sku="WIDGET",
        quantity=10,
        divisible=True,
        unit_price=Decimal("5.00")
    )
    
    # Transfer part of it
    transferred_id = sys.transfer_deliverable(widget_id, "H1", "H2", quantity=3)
    
    # Check both parts retain the unit price
    original = sys.state.contracts[widget_id]
    transferred = sys.state.contracts[transferred_id]
    
    assert original.amount == 7
    assert original.unit_price == Decimal("5.00")
    assert original.valued_amount == Decimal("35.00")
    
    assert transferred.amount == 3
    assert transferred.unit_price == Decimal("5.00")
    assert transferred.valued_amount == Decimal("15.00")


def test_deliverable_with_zero_price():
    """Test deliverable with zero unit price."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    # Create deliverable with zero price (free item)
    free_id = sys.create_deliverable(
        issuer_id="H1",
        holder_id="H1",
        sku="FREE_SAMPLE",
        quantity=100,
        unit_price=Decimal("0")
    )
    
    # Check the deliverable
    free_item = sys.state.contracts[free_id]
    assert free_item.amount == 100
    assert free_item.unit_price == Decimal("0")
    assert free_item.valued_amount == Decimal("0")
    
    # Check balance shows zero value
    balance = agent_balance(sys, "H1")
    assert balance.total_nonfinancial_value == Decimal("0")


def test_mixed_valued_and_unvalued_deliverables():
    """Test system with mix of valued and unvalued deliverables."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    # Create multiple deliverables with different pricing
    sys.create_deliverable(
        issuer_id="H1", holder_id="H1",
        sku="PRICED_A", quantity=5, unit_price=Decimal("10")
    )
    
    sys.create_deliverable(
        issuer_id="H1", holder_id="H1",
        sku="UNPRICED", quantity=20
    )
    
    sys.create_deliverable(
        issuer_id="H1", holder_id="H1",
        sku="PRICED_B", quantity=3, unit_price=Decimal("15.50")
    )
    
    sys.create_deliverable(
        issuer_id="H1", holder_id="H1",
        sku="FREE", quantity=100, unit_price=Decimal("0")
    )
    
    # Check balance
    balance = agent_balance(sys, "H1")
    
    # Total should only include priced items (not free or unpriced)
    expected_value = Decimal("50") + Decimal("46.50")  # PRICED_A + PRICED_B
    assert balance.total_nonfinancial_value == expected_value
    
    # Check individual items
    assert len(balance.nonfinancial_assets_by_kind) == 4
    assert balance.nonfinancial_assets_by_kind["PRICED_A"]["value"] == Decimal("50")
    assert balance.nonfinancial_assets_by_kind["UNPRICED"]["value"] is None
    assert balance.nonfinancial_assets_by_kind["PRICED_B"]["value"] == Decimal("46.50")
    assert balance.nonfinancial_assets_by_kind["FREE"]["value"] == Decimal("0")