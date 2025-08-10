"""Tests for balance analysis functionality."""

import pytest

from bilancio.analysis.balances import AgentBalance, TrialBalance, agent_balance, as_rows, system_trial_balance
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.household import Household
from bilancio.engines.system import System


class TestAgentBalance:
    """Test agent balance calculations."""
    
    def test_agent_balance_with_financial_instruments(self):
        """Test agent balance calculation with financial instruments."""
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        hh = Household(id="HH01", name="Household", kind="household")
        
        system.bootstrap_cb(cb)
        system.add_agent(hh)
        
        # Mint cash to household
        system.mint_cash("HH01", 1000)
        
        # Check household balance
        balance = agent_balance(system, "HH01")
        assert balance.agent_id == "HH01"
        assert balance.total_financial_assets == 1000
        assert balance.total_financial_liabilities == 0
        assert balance.net_financial == 1000
        assert balance.assets_by_kind == {"cash": 1000}
        assert balance.liabilities_by_kind == {}
        
        # Check central bank balance
        cb_balance = agent_balance(system, "CB01")
        assert cb_balance.agent_id == "CB01"
        assert cb_balance.total_financial_assets == 0
        assert cb_balance.total_financial_liabilities == 1000
        assert cb_balance.net_financial == -1000
        assert cb_balance.assets_by_kind == {}
        assert cb_balance.liabilities_by_kind == {"cash": 1000}
    
    def test_agent_balance_with_mixed_instruments(self):
        """Test agent balance calculation with both financial and non-financial instruments."""
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        hh2 = Household(id="HH02", name="Household 2", kind="household")
        
        system.bootstrap_cb(cb)
        system.add_agent(hh1)
        system.add_agent(hh2)
        
        # Mint cash (financial)
        system.mint_cash("HH01", 1000)
        
        # Create deliverable (non-financial)
        system.create_deliverable("HH01", "HH02", "APPLES", 50)
        
        # Check HH01 balance (has financial assets, non-financial liabilities)
        hh1_balance = agent_balance(system, "HH01")
        assert hh1_balance.total_financial_assets == 1000  # Only cash
        assert hh1_balance.total_financial_liabilities == 0  # Deliverable liability is non-financial
        assert hh1_balance.net_financial == 1000
        assert hh1_balance.assets_by_kind == {"cash": 1000}
        assert hh1_balance.liabilities_by_kind == {"deliverable": 50}
        
        # Check HH02 balance (has non-financial assets only)
        hh2_balance = agent_balance(system, "HH02")
        assert hh2_balance.total_financial_assets == 0  # Deliverable asset is non-financial
        assert hh2_balance.total_financial_liabilities == 0
        assert hh2_balance.net_financial == 0
        assert hh2_balance.assets_by_kind == {"deliverable": 50}
        assert hh2_balance.liabilities_by_kind == {}


class TestSystemTrialBalance:
    """Test system-wide trial balance calculations."""
    
    def test_system_trial_balance_balances(self):
        """Test that system trial balance shows equal assets and liabilities."""
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        hh = Household(id="HH01", name="Household", kind="household")
        
        system.bootstrap_cb(cb)
        system.add_agent(hh)
        
        # Mint cash
        system.mint_cash("HH01", 1000)
        
        trial = system_trial_balance(system)
        assert trial.total_financial_assets == trial.total_financial_liabilities == 1000
        assert trial.assets_by_kind == trial.liabilities_by_kind == {"cash": 1000}
    
    def test_system_trial_balance_with_mixed_instruments(self):
        """Test system trial balance with financial and non-financial instruments."""
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        hh2 = Household(id="HH02", name="Household 2", kind="household")
        
        system.bootstrap_cb(cb)
        system.add_agent(hh1)
        system.add_agent(hh2)
        
        # Create mixed instruments
        system.mint_cash("HH01", 1000)
        system.create_deliverable("HH01", "HH02", "APPLES", 50)
        
        trial = system_trial_balance(system)
        assert trial.total_financial_assets == trial.total_financial_liabilities == 1000
        assert trial.assets_by_kind == {"cash": 1000, "deliverable": 50}
        assert trial.liabilities_by_kind == {"cash": 1000, "deliverable": 50}


class TestAsRows:
    """Test as_rows function for tabular output."""
    
    def test_as_rows_format(self):
        """Test as_rows returns correct format."""
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        hh = Household(id="HH01", name="Household", kind="household")
        
        system.bootstrap_cb(cb)
        system.add_agent(hh)
        system.mint_cash("HH01", 1000)
        
        rows = as_rows(system)
        assert len(rows) == 3  # CB, HH, SYSTEM
        
        # Check agent rows exist
        agent_ids = {row["agent_id"] for row in rows}
        assert agent_ids == {"CB01", "HH01", "SYSTEM"}
        
        # Check SYSTEM row has zero net financial (should always balance)
        system_row = next(row for row in rows if row["agent_id"] == "SYSTEM")
        assert system_row["net_financial"] == 0
        assert system_row["total_financial_assets"] == system_row["total_financial_liabilities"]
        
        # Check individual agent rows have proper totals
        hh_row = next(row for row in rows if row["agent_id"] == "HH01")
        assert hh_row["total_financial_assets"] == 1000
        assert hh_row["total_financial_liabilities"] == 0
        assert hh_row["net_financial"] == 1000
        assert hh_row["assets_cash"] == 1000
        
        cb_row = next(row for row in rows if row["agent_id"] == "CB01")
        assert cb_row["total_financial_assets"] == 0
        assert cb_row["total_financial_liabilities"] == 1000
        assert cb_row["net_financial"] == -1000
        assert cb_row["liabilities_cash"] == 1000