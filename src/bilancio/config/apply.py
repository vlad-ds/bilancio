"""Apply configuration to a Bilancio system."""

from typing import Dict, Any
from decimal import Decimal

from bilancio.engines.system import System
from bilancio.domain.agents import Bank, Household, Firm, CentralBank, Treasury
from bilancio.ops.banking import deposit_cash, withdraw_cash, client_payment
from bilancio.domain.instruments.credit import Payable
from bilancio.core.errors import ValidationError

from .models import ScenarioConfig, AgentSpec
from .loaders import parse_action


def create_agent(spec: AgentSpec) -> Any:
    """Create an agent from specification.
    
    Args:
        spec: Agent specification
        
    Returns:
        Created agent instance
        
    Raises:
        ValueError: If agent kind is unknown
    """
    agent_classes = {
        "central_bank": CentralBank,
        "bank": Bank,
        "household": Household,
        "firm": Firm,
        "treasury": Treasury
    }
    
    agent_class = agent_classes.get(spec.kind)
    if not agent_class:
        raise ValueError(f"Unknown agent kind: {spec.kind}")
    
    # Create agent with id, name, and kind
    # Note: The agent classes set their own kind in __post_init__, but we pass it anyway
    # for compatibility with the base Agent class
    return agent_class(id=spec.id, name=spec.name, kind=spec.kind)


def apply_policy_overrides(system: System, overrides: Dict[str, Any]) -> None:
    """Apply policy overrides to the system.
    
    Args:
        system: System instance
        overrides: Policy override configuration
    """
    if not overrides:
        return
    
    # Apply MOP rank overrides
    if "mop_rank" in overrides and overrides["mop_rank"]:
        for agent_kind, mop_list in overrides["mop_rank"].items():
            system.policy.mop_rank[agent_kind] = mop_list


def apply_action(system: System, action_dict: Dict[str, Any], agents: Dict[str, Any]) -> None:
    """Apply a single action to the system.
    
    Args:
        system: System instance
        action_dict: Action dictionary from config
        agents: Dictionary of agent_id -> agent instance
        
    Raises:
        ValueError: If action cannot be applied
        ValidationError: If action violates system invariants
    """
    # Parse the action
    action = parse_action(action_dict)
    action_type = action.action
    
    try:
        if action_type == "mint_reserves":
            system.mint_reserves(
                to_bank_id=action.to,
                amount=action.amount
            )
            
        elif action_type == "mint_cash":
            system.mint_cash(
                to_agent_id=action.to,
                amount=action.amount
            )
            
        elif action_type == "transfer_reserves":
            system.transfer_reserves(
                from_bank_id=action.from_bank,
                to_bank_id=action.to_bank,
                amount=action.amount
            )
            
        elif action_type == "transfer_cash":
            system.transfer_cash(
                from_agent_id=action.from_agent,
                to_agent_id=action.to_agent,
                amount=action.amount
            )
            
        elif action_type == "deposit_cash":
            deposit_cash(
                system=system,
                customer_id=action.customer,
                bank_id=action.bank,
                amount=action.amount
            )
            
        elif action_type == "withdraw_cash":
            withdraw_cash(
                system=system,
                customer_id=action.customer,
                bank_id=action.bank,
                amount=action.amount
            )
            
        elif action_type == "client_payment":
            # Need to determine banks for payer and payee
            payer = agents.get(action.payer)
            payee = agents.get(action.payee)
            
            if not payer or not payee:
                raise ValueError(f"Unknown agent in client_payment: {action.payer} or {action.payee}")
            
            # Find bank relationships (simplified - assumes first deposit)
            payer_bank = None
            payee_bank = None
            
            # Check for existing deposits to determine banks
            for bank_id in [a.id for a in agents.values() if a.kind == "bank"]:
                if system.deposit_ids(action.payer, bank_id):
                    payer_bank = bank_id
                if system.deposit_ids(action.payee, bank_id):
                    payee_bank = bank_id
            
            if not payer_bank or not payee_bank:
                raise ValueError(f"Cannot determine banks for client_payment from {action.payer} to {action.payee}")
            
            client_payment(
                system=system,
                payer_id=action.payer,
                payer_bank=payer_bank,
                payee_id=action.payee,
                payee_bank=payee_bank,
                amount=action.amount
            )
            
        elif action_type == "create_stock":
            system.create_stock(
                owner_id=action.owner,
                sku=action.sku,
                quantity=action.quantity,
                unit_price=action.unit_price
            )
            
        elif action_type == "transfer_stock":
            # Find stock with matching SKU owned by from_agent
            stocks = [s for s in system.state.stocks.values() 
                     if s.owner_id == action.from_agent and s.sku == action.sku]
            
            if not stocks:
                raise ValueError(f"No stock with SKU {action.sku} owned by {action.from_agent}")
            
            # Transfer from first matching stock
            stock = stocks[0]
            if stock.quantity < action.quantity:
                raise ValueError(f"Insufficient stock: {stock.quantity} < {action.quantity}")
            
            system.transfer_stock(
                stock_id=stock.id,
                from_owner=action.from_agent,
                to_owner=action.to_agent,
                quantity=action.quantity if action.quantity < stock.quantity else None
            )
            
        elif action_type == "create_delivery_obligation":
            system.create_delivery_obligation(
                from_agent=action.from_agent,
                to_agent=action.to_agent,
                sku=action.sku,
                quantity=action.quantity,
                unit_price=action.unit_price,
                due_day=action.due_day
            )
            
        elif action_type == "create_payable":
            # Create a Payable instrument
            # Payable uses asset_holder_id (creditor) and liability_issuer_id (debtor)
            payable = Payable(
                id=system.new_contract_id("PAY"),
                kind="payable",  # Will be set by __post_init__ but required by dataclass
                amount=int(action.amount),  # Convert to int (minor units)
                denom="X",  # Default denomination
                asset_holder_id=action.to_agent,  # creditor holds the asset
                liability_issuer_id=action.from_agent,  # debtor issues the liability
                due_day=action.due_day
            )
            system.add_contract(payable)
            
        else:
            raise ValueError(f"Unknown action type: {action_type}")
            
    except Exception as e:
        # Add context to the error
        raise ValueError(f"Failed to apply {action_type}: {e}")


def apply_to_system(config: ScenarioConfig, system: System) -> None:
    """Apply a scenario configuration to a system.
    
    This function:
    1. Creates and adds all agents
    2. Applies policy overrides
    3. Executes all initial actions within System.setup()
    4. Optionally validates invariants
    
    Args:
        config: Scenario configuration
        system: System instance to configure
        
    Raises:
        ValueError: If configuration cannot be applied
        ValidationError: If system invariants are violated
    """
    agents = {}
    
    # Use setup context for all initialization
    with system.setup():
        # Create and add agents
        for agent_spec in config.agents:
            agent = create_agent(agent_spec)
            system.add_agent(agent)
            agents[agent.id] = agent
        
        # Apply policy overrides
        if config.policy_overrides:
            apply_policy_overrides(system, config.policy_overrides.model_dump())
        
        # Execute initial actions
        for action_dict in config.initial_actions:
            apply_action(system, action_dict, agents)
            
            # Optional: check invariants after each action for debugging
            # system.assert_invariants()
    
    # Final invariant check outside of setup
    system.assert_invariants()