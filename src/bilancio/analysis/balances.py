"""Balance analysis functions for the bilancio system."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict

from bilancio.engines.system import System


@dataclass
class AgentBalance:
    """Balance sheet summary for a specific agent."""
    agent_id: str
    assets_by_kind: Dict[str, int]
    liabilities_by_kind: Dict[str, int]
    total_financial_assets: int
    total_financial_liabilities: int
    net_financial: int


@dataclass
class TrialBalance:
    """System-wide balance sheet summary."""
    assets_by_kind: Dict[str, int]
    liabilities_by_kind: Dict[str, int]
    total_financial_assets: int
    total_financial_liabilities: int


def agent_balance(system: System, agent_id: str) -> AgentBalance:
    """Calculate balance sheet for a specific agent.
    
    Args:
        system: The bilancio system
        agent_id: ID of the agent to analyze
        
    Returns:
        AgentBalance with calculated totals and breakdowns by instrument kind
    """
    agent = system.state.agents[agent_id]
    
    assets_by_kind = defaultdict(int)
    liabilities_by_kind = defaultdict(int)
    total_financial_assets = 0
    total_financial_liabilities = 0
    
    # Sum up assets
    for contract_id in agent.asset_ids:
        contract = system.state.contracts[contract_id]
        assets_by_kind[contract.kind] += contract.amount
        
        # Check if it's financial (use getattr with default lambda)
        is_financial_func = getattr(contract, 'is_financial', lambda: True)
        if is_financial_func():
            total_financial_assets += contract.amount
    
    # Sum up liabilities
    for contract_id in agent.liability_ids:
        contract = system.state.contracts[contract_id]
        liabilities_by_kind[contract.kind] += contract.amount
        
        # Check if it's financial (use getattr with default lambda)
        is_financial_func = getattr(contract, 'is_financial', lambda: True)
        if is_financial_func():
            total_financial_liabilities += contract.amount
    
    net_financial = total_financial_assets - total_financial_liabilities
    
    return AgentBalance(
        agent_id=agent_id,
        assets_by_kind=dict(assets_by_kind),
        liabilities_by_kind=dict(liabilities_by_kind),
        total_financial_assets=total_financial_assets,
        total_financial_liabilities=total_financial_liabilities,
        net_financial=net_financial
    )


def system_trial_balance(system: System) -> TrialBalance:
    """Calculate system-wide trial balance.
    
    Args:
        system: The bilancio system
        
    Returns:
        TrialBalance with system-wide totals and breakdowns by instrument kind
    """
    assets_by_kind = defaultdict(int)
    liabilities_by_kind = defaultdict(int)
    total_financial_assets = 0
    total_financial_liabilities = 0
    
    # Walk all contracts once and sum by kind for both sides
    for contract in system.state.contracts.values():
        # Asset side
        assets_by_kind[contract.kind] += contract.amount
        
        # Liability side  
        liabilities_by_kind[contract.kind] += contract.amount
        
        # Check if it's financial (use getattr with default lambda)
        is_financial_func = getattr(contract, 'is_financial', lambda: True)
        if is_financial_func():
            total_financial_assets += contract.amount
            total_financial_liabilities += contract.amount
    
    return TrialBalance(
        assets_by_kind=dict(assets_by_kind),
        liabilities_by_kind=dict(liabilities_by_kind),
        total_financial_assets=total_financial_assets,
        total_financial_liabilities=total_financial_liabilities
    )


def as_rows(system: System) -> list[dict]:
    """Convert system balances to list of rows for tabular display.
    
    Args:
        system: The bilancio system
        
    Returns:
        List of dicts, one per agent plus a SYSTEM summary row
    """
    rows = []
    
    # Add row for each agent
    for agent_id in system.state.agents.keys():
        balance = agent_balance(system, agent_id)
        row = {
            'agent_id': agent_id,
            'total_financial_assets': balance.total_financial_assets,
            'total_financial_liabilities': balance.total_financial_liabilities,
            'net_financial': balance.net_financial,
            **{f'assets_{kind}': amount for kind, amount in balance.assets_by_kind.items()},
            **{f'liabilities_{kind}': amount for kind, amount in balance.liabilities_by_kind.items()}
        }
        rows.append(row)
    
    # Add SYSTEM summary row
    trial_balance = system_trial_balance(system)
    system_row = {
        'agent_id': 'SYSTEM',
        'total_financial_assets': trial_balance.total_financial_assets,
        'total_financial_liabilities': trial_balance.total_financial_liabilities,
        'net_financial': 0,  # Should always be zero for system-wide view
        **{f'assets_{kind}': amount for kind, amount in trial_balance.assets_by_kind.items()},
        **{f'liabilities_{kind}': amount for kind, amount in trial_balance.liabilities_by_kind.items()}
    }
    rows.append(system_row)
    
    return rows