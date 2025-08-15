"""Tests for deliverable merge behavior with fungible_key enhancements."""
from decimal import Decimal

import pytest

from bilancio.core.errors import ValidationError
from bilancio.domain.agents import Household
from bilancio.engines.system import System
from bilancio.ops.primitives import fungible_key, merge


class TestDeliverableMerge:
    """Test that deliverables with different SKUs or prices don't merge incorrectly."""
    
    def test_deliverables_with_different_skus_dont_merge(self):
        """Deliverables with different SKUs should not be fungible."""
        system = System()
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        hh2 = Household(id="HH02", name="Household 2", kind="household")
        
        system.add_agent(hh1)
        system.add_agent(hh2)
        
        # Create two deliverables with different SKUs but same parties
        apple_id = system.create_deliverable("HH01", "HH02", "APPLES", 10, Decimal("2.00"))
        orange_id = system.create_deliverable("HH01", "HH02", "ORANGES", 10, Decimal("2.00"))
        
        apple = system.state.contracts[apple_id]
        orange = system.state.contracts[orange_id]
        
        # Verify they have different fungible keys
        assert fungible_key(apple) != fungible_key(orange)
        
        # Attempting to merge should fail
        with pytest.raises(ValidationError, match="not fungible-compatible"):
            merge(system, apple_id, orange_id)
    
    def test_deliverables_with_different_prices_dont_merge(self):
        """Deliverables with same SKU but different prices should not be fungible."""
        system = System()
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        hh2 = Household(id="HH02", name="Household 2", kind="household")
        
        system.add_agent(hh1)
        system.add_agent(hh2)
        
        # Create two deliverables with same SKU but different prices
        cheap_apple_id = system.create_deliverable("HH01", "HH02", "APPLES", 10, Decimal("1.00"))
        expensive_apple_id = system.create_deliverable("HH01", "HH02", "APPLES", 10, Decimal("3.00"))
        
        cheap_apple = system.state.contracts[cheap_apple_id]
        expensive_apple = system.state.contracts[expensive_apple_id]
        
        # Verify they have different fungible keys
        assert fungible_key(cheap_apple) != fungible_key(expensive_apple)
        
        # Attempting to merge should fail
        with pytest.raises(ValidationError, match="not fungible-compatible"):
            merge(system, cheap_apple_id, expensive_apple_id)
    
    def test_deliverables_with_same_sku_and_price_can_merge(self):
        """Deliverables with same SKU and price should be fungible."""
        system = System()
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        hh2 = Household(id="HH02", name="Household 2", kind="household")
        
        system.add_agent(hh1)
        system.add_agent(hh2)
        
        # Create two deliverables with same SKU and price
        apple1_id = system.create_deliverable("HH01", "HH02", "APPLES", 10, Decimal("2.00"))
        apple2_id = system.create_deliverable("HH01", "HH02", "APPLES", 5, Decimal("2.00"))
        
        apple1 = system.state.contracts[apple1_id]
        apple2 = system.state.contracts[apple2_id]
        
        # Verify they have the same fungible key
        assert fungible_key(apple1) == fungible_key(apple2)
        
        # Merging should succeed
        result_id = merge(system, apple1_id, apple2_id)
        assert result_id == apple1_id
        
        # Verify the merged instrument has the combined amount
        merged = system.state.contracts[apple1_id]
        assert merged.amount == 15
        assert merged.unit_price == Decimal("2.00")
        assert merged.valued_amount == Decimal("30.00")
        
        # Verify apple2 was removed
        assert apple2_id not in system.state.contracts
    
    def test_deliverables_with_different_parties_dont_merge(self):
        """Deliverables with different issuers or holders should not be fungible."""
        system = System()
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        hh2 = Household(id="HH02", name="Household 2", kind="household")
        hh3 = Household(id="HH03", name="Household 3", kind="household")
        
        system.add_agent(hh1)
        system.add_agent(hh2)
        system.add_agent(hh3)
        
        # Create deliverables with same SKU/price but different parties
        apple1_id = system.create_deliverable("HH01", "HH02", "APPLES", 10, Decimal("2.00"))
        apple2_id = system.create_deliverable("HH01", "HH03", "APPLES", 10, Decimal("2.00"))  # Different holder
        
        apple1 = system.state.contracts[apple1_id]
        apple2 = system.state.contracts[apple2_id]
        
        # Verify they have different fungible keys
        assert fungible_key(apple1) != fungible_key(apple2)
        
        # Attempting to merge should fail
        with pytest.raises(ValidationError, match="not fungible-compatible"):
            merge(system, apple1_id, apple2_id)
    
    def test_fungible_key_backwards_compatible_with_financial_instruments(self):
        """Financial instruments should maintain their original fungible key behavior."""
        from bilancio.domain.agents import Bank, CentralBank
        
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        bank = Bank(id="BK01", name="Bank", kind="bank")
        hh = Household(id="HH01", name="Household", kind="household")
        
        system.bootstrap_cb(cb)
        system.add_agent(bank)
        system.add_agent(hh)
        
        # Create cash instruments
        cash1_id = system.mint_cash("HH01", 100)
        cash2_id = system.mint_cash("HH01", 50)
        
        cash1 = system.state.contracts[cash1_id]
        cash2 = system.state.contracts[cash2_id]
        
        # Verify they have the same fungible key (no SKU/price in key)
        key1 = fungible_key(cash1)
        key2 = fungible_key(cash2)
        assert key1 == key2
        assert len(key1) == 4  # Only base attributes
        
        # Merging should succeed
        result_id = merge(system, cash1_id, cash2_id)
        merged = system.state.contracts[result_id]
        assert merged.amount == 150