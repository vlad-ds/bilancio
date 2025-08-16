import pytest
from decimal import Decimal
from bilancio.engines.system import System
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.household import Household
from bilancio.core.errors import ValidationError

def test_mint_and_retire_cash_roundtrip():
    """Test minting cash to an agent and then retiring it."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    sys.add_agent(cb)
    sys.add_agent(h1)
    
    # Mint 150 units of cash to H1
    cash_id = sys.mint_cash("H1", 150)
    
    # Check CB outstanding
    assert sys.state.cb_cash_outstanding == 150
    
    # Check H1 has the cash
    assert cash_id in h1.asset_ids
    cash_instr = sys.state.contracts[cash_id]
    assert cash_instr.amount == 150
    assert cash_instr.asset_holder_id == "H1"
    assert cash_instr.liability_issuer_id == "CB1"
    
    # Retire 80 units
    sys.retire_cash("H1", 80)
    
    # Check remaining
    assert sys.state.cb_cash_outstanding == 70
    
    # Check H1 still has 70 (may be split across instruments)
    h1_cash_total = sum(
        sys.state.contracts[cid].amount 
        for cid in h1.asset_ids 
        if sys.state.contracts[cid].kind == "cash"
    )
    assert h1_cash_total == 70
    
    # Invariants should hold
    sys.assert_invariants()

def test_transfer_cash_with_split_and_merge():
    """Test transferring cash between agents with automatic split and merge."""
    sys = System()
    cb = CentralBank(id="CB1", name="CB", kind="central_bank")
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Mint 100 to H1 as one instrument
    sys.mint_cash("H1", 100)
    
    # Transfer 30 to H2 (should split)
    sys.transfer_cash("H1", "H2", 30)
    
    # H1 should have 70, H2 should have 30
    h1_cash = sum(sys.state.contracts[cid].amount for cid in h1.asset_ids 
                  if sys.state.contracts[cid].kind == "cash")
    h2_cash = sum(sys.state.contracts[cid].amount for cid in h2.asset_ids 
                  if sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 70
    assert h2_cash == 30
    
    # Transfer remaining 70 to H2
    sys.transfer_cash("H1", "H2", 70)
    
    # H1 should have 0, H2 should have 100
    h1_cash = sum(sys.state.contracts[cid].amount for cid in h1.asset_ids 
                  if sys.state.contracts[cid].kind == "cash")
    h2_cash = sum(sys.state.contracts[cid].amount for cid in h2.asset_ids 
                  if sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 0
    assert h2_cash == 100
    
    # H2 should ideally have just one cash instrument after merge
    h2_cash_instruments = [cid for cid in h2.asset_ids 
                           if sys.state.contracts[cid].kind == "cash"]
    assert len(h2_cash_instruments) == 1
    assert sys.state.contracts[h2_cash_instruments[0]].amount == 100
    
    sys.assert_invariants()

def test_create_and_transfer_divisible_deliverable():
    """Test creating and transferring divisible stock lots."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Create divisible widgets stock
    widget_id = sys.create_stock("H1", "WIDGET", 10, Decimal("0"), divisible=True)
    
    # Check creation
    widget = sys.state.stocks[widget_id]
    assert widget.quantity == 10
    assert widget.sku == "WIDGET"
    assert widget.divisible == True
    assert widget.owner_id == "H1"
    
    # Transfer 3 widgets to H2
    transferred_id = sys.transfer_stock(widget_id, "H1", "H2", quantity=3)
    
    # H1 should keep 7, H2 should have 3
    original = sys.state.stocks[widget_id]
    transferred = sys.state.stocks[transferred_id]
    assert original.quantity == 7
    assert transferred.quantity == 3
    assert transferred.owner_id == "H2"
    
    # Full transfer of remaining
    sys.transfer_stock(widget_id, "H1", "H2")
    
    # H1 should have none, H2 should have all
    h1_widgets = [sid for sid in sys.state.stocks.keys() 
                  if sys.state.stocks[sid].owner_id == "H1" and 
                  sys.state.stocks[sid].sku == "WIDGET"]
    assert len(h1_widgets) == 0
    
    h2_widget_total = sum(
        sys.state.stocks[sid].quantity 
        for sid in sys.state.stocks.keys() 
        if sys.state.stocks[sid].owner_id == "H2" and sys.state.stocks[sid].sku == "WIDGET"
    )
    assert h2_widget_total == 10
    
    sys.assert_invariants()

def test_indivisible_deliverable():
    """Test that indivisible stock lots cannot be partially transferred."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Create indivisible item with quantity > 1 to test partial transfer
    item_id = sys.create_stock("H1", "MACHINE", 5, Decimal("0"), divisible=False)
    
    # Partial transfer should fail
    with pytest.raises(ValidationError, match="not divisible"):
        sys.transfer_stock(item_id, "H1", "H2", quantity=3)
    
    # Full transfer should work (quantity=None means full transfer)
    sys.transfer_stock(item_id, "H1", "H2")
    
    # Item should now belong to H2
    item = sys.state.stocks[item_id]
    assert item.owner_id == "H2"
    
    sys.assert_invariants()

def test_insufficient_cash_errors():
    """Test error handling for insufficient cash."""
    sys = System()
    cb = CentralBank(id="CB1", name="CB", kind="central_bank")
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Mint 50 to H1
    sys.mint_cash("H1", 50)
    
    # Try to retire more than available
    with pytest.raises(ValidationError, match="insufficient"):
        sys.retire_cash("H1", 100)
    
    # Try to transfer more than available
    with pytest.raises(ValidationError, match="insufficient"):
        sys.transfer_cash("H1", "H2", 100)
    
    # State should be unchanged after failures
    assert sys.state.cb_cash_outstanding == 50
    # Get the agent from system state (not the local variable)
    h1_from_sys = sys.state.agents["H1"]
    h1_cash = sum(sys.state.contracts[cid].amount for cid in h1_from_sys.asset_ids 
                  if sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 50
    
    sys.assert_invariants()

def test_deliverable_holder_mismatch():
    """Test error when trying to transfer stock from wrong owner."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    h3 = Household(id="H3", name="H3", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    sys.add_agent(h3)
    
    # Create stock for H1
    widget_id = sys.create_stock("H1", "WIDGET", 5, Decimal("0"))
    
    # H2 cannot transfer H1's widget
    with pytest.raises(ValidationError, match="owner"):
        sys.transfer_stock(widget_id, "H2", "H3")
    
    sys.assert_invariants()

def test_multiple_cash_instruments_coalesce():
    """Test that multiple cash transfers result in proper coalescing."""
    sys = System()
    cb = CentralBank(id="CB1", name="CB", kind="central_bank")
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Mint cash to H1 in multiple chunks
    sys.mint_cash("H1", 20)
    sys.mint_cash("H1", 30)
    sys.mint_cash("H1", 50)
    
    # H1 has 3 cash instruments totaling 100
    h1_cash_ids = [cid for cid in h1.asset_ids 
                   if sys.state.contracts[cid].kind == "cash"]
    assert len(h1_cash_ids) == 3
    assert sum(sys.state.contracts[cid].amount for cid in h1_cash_ids) == 100
    
    # Transfer all to H2 in parts
    sys.transfer_cash("H1", "H2", 25)
    sys.transfer_cash("H1", "H2", 25)
    sys.transfer_cash("H1", "H2", 50)
    
    # H2 should have merged cash instruments
    h2_cash_ids = [cid for cid in h2.asset_ids 
                   if sys.state.contracts[cid].kind == "cash"]
    # Should be consolidated to fewer instruments (ideally 1)
    assert len(h2_cash_ids) <= 3
    assert sum(sys.state.contracts[cid].amount for cid in h2_cash_ids) == 100
    
    sys.assert_invariants()