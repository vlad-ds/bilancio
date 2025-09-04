"""Pydantic models for Bilancio scenario configuration."""

from typing import Literal, Optional, Union, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class PolicyOverrides(BaseModel):
    """Policy configuration overrides."""
    mop_rank: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Override default settlement order per agent kind"
    )


class AgentSpec(BaseModel):
    """Specification for an agent in the scenario."""
    id: str = Field(..., description="Unique identifier for the agent")
    kind: Literal["central_bank", "bank", "household", "firm", "treasury"] = Field(
        ..., description="Type of agent"
    )
    name: str = Field(..., description="Human-readable name for the agent")


class MintReserves(BaseModel):
    """Action to mint reserves to a bank."""
    action: Literal["mint_reserves"] = "mint_reserves"
    to: str = Field(..., description="Target bank ID")
    amount: Decimal = Field(..., description="Amount to mint")
    alias: Optional[str] = Field(
        None,
        description="Optional alias to reference the created reserve_deposit contract later"
    )
    
    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class MintCash(BaseModel):
    """Action to mint cash to an agent."""
    action: Literal["mint_cash"] = "mint_cash"
    to: str = Field(..., description="Target agent ID")
    amount: Decimal = Field(..., description="Amount to mint")
    alias: Optional[str] = Field(
        None,
        description="Optional alias to reference the created cash contract later"
    )
    
    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class TransferReserves(BaseModel):
    """Action to transfer reserves between banks."""
    action: Literal["transfer_reserves"] = "transfer_reserves"
    from_bank: str = Field(..., description="Source bank ID")
    to_bank: str = Field(..., description="Target bank ID")
    amount: Decimal = Field(..., description="Amount to transfer")
    
    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class TransferCash(BaseModel):
    """Action to transfer cash between agents."""
    action: Literal["transfer_cash"] = "transfer_cash"
    from_agent: str = Field(..., description="Source agent ID")
    to_agent: str = Field(..., description="Target agent ID")
    amount: Decimal = Field(..., description="Amount to transfer")
    
    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class DepositCash(BaseModel):
    """Action to deposit cash at a bank."""
    action: Literal["deposit_cash"] = "deposit_cash"
    customer: str = Field(..., description="Customer agent ID")
    bank: str = Field(..., description="Bank ID")
    amount: Decimal = Field(..., description="Amount to deposit")
    
    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class WithdrawCash(BaseModel):
    """Action to withdraw cash from a bank."""
    action: Literal["withdraw_cash"] = "withdraw_cash"
    customer: str = Field(..., description="Customer agent ID")
    bank: str = Field(..., description="Bank ID")
    amount: Decimal = Field(..., description="Amount to withdraw")
    
    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class ClientPayment(BaseModel):
    """Action for client payment between bank accounts."""
    action: Literal["client_payment"] = "client_payment"
    payer: str = Field(..., description="Payer agent ID")
    payee: str = Field(..., description="Payee agent ID")
    amount: Decimal = Field(..., description="Payment amount")
    
    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class CreateStock(BaseModel):
    """Action to create stock inventory."""
    action: Literal["create_stock"] = "create_stock"
    owner: str = Field(..., description="Owner agent ID")
    sku: str = Field(..., description="Stock keeping unit identifier")
    quantity: int = Field(..., description="Quantity of items")
    unit_price: Decimal = Field(..., description="Price per unit")
    
    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v
    
    @field_validator("unit_price")
    @classmethod
    def price_non_negative(cls, v):
        if v < 0:
            raise ValueError("Unit price cannot be negative")
        return v


class TransferStock(BaseModel):
    """Action to transfer stock between agents."""
    action: Literal["transfer_stock"] = "transfer_stock"
    from_agent: str = Field(..., description="Source agent ID")
    to_agent: str = Field(..., description="Target agent ID")
    sku: str = Field(..., description="Stock keeping unit identifier")
    quantity: int = Field(..., description="Quantity to transfer")
    
    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v


class CreateDeliveryObligation(BaseModel):
    """Action to create a delivery obligation."""
    action: Literal["create_delivery_obligation"] = "create_delivery_obligation"
    from_agent: str = Field(..., description="Delivering agent ID", alias="from")
    to_agent: str = Field(..., description="Receiving agent ID", alias="to")
    sku: str = Field(..., description="Stock keeping unit identifier")
    quantity: int = Field(..., description="Quantity to deliver")
    unit_price: Decimal = Field(..., description="Price per unit")
    due_day: int = Field(..., description="Day when delivery is due")
    alias: Optional[str] = Field(
        None,
        description="Optional alias to reference the created delivery obligation later"
    )
    
    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v
    
    @field_validator("unit_price")
    @classmethod
    def price_non_negative(cls, v):
        if v < 0:
            raise ValueError("Unit price cannot be negative")
        return v
    
    @field_validator("due_day")
    @classmethod
    def due_day_non_negative(cls, v):
        if v < 0:
            raise ValueError("Due day cannot be negative")
        return v


class CreatePayable(BaseModel):
    """Action to create a payable obligation."""
    action: Literal["create_payable"] = "create_payable"
    from_agent: str = Field(..., description="Debtor agent ID", alias="from")
    to_agent: str = Field(..., description="Creditor agent ID", alias="to")
    amount: Decimal = Field(..., description="Amount to pay")
    due_day: int = Field(..., description="Day when payment is due")
    alias: Optional[str] = Field(
        None,
        description="Optional alias to reference the created payable later"
    )
    
    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @field_validator("due_day")
    @classmethod
    def due_day_non_negative(cls, v):
        if v < 0:
            raise ValueError("Due day cannot be negative")
        return v


# Union type for all actions
class TransferClaim(BaseModel):
    """Action to transfer (assign) a claim to a new creditor.

    References a specific contract by alias or by ID. Both may be provided, but
    if both are present they must refer to the same contract.
    """
    action: Literal["transfer_claim"] = "transfer_claim"
    contract_alias: Optional[str] = Field(None, description="Alias of the contract to transfer")
    contract_id: Optional[str] = Field(None, description="Explicit contract ID to transfer")
    to_agent: str = Field(..., description="New creditor (asset holder) agent ID")

    @field_validator("to_agent")
    @classmethod
    def non_empty_agent(cls, v):
        if not v:
            raise ValueError("to_agent is required")
        return v

    # Cross-field validation
    from pydantic import model_validator

    @model_validator(mode="after")
    def validate_reference(self):
        if not self.contract_alias and not self.contract_id:
            raise ValueError("Either contract_alias or contract_id must be provided")
        return self


class ScheduledAction(BaseModel):
    """A user-scheduled action to run at a specific day (Phase B1)."""
    day: int = Field(..., description="Day index (>= 1) to execute this action")
    action: Dict[str, Any] = Field(..., description="Single action dictionary to execute on that day")

    @field_validator("day")
    @classmethod
    def day_positive(cls, v):
        if v < 1:
            raise ValueError("Scheduled action day must be >= 1")
        return v


Action = Union[
    MintReserves,
    MintCash,
    TransferReserves,
    TransferCash,
    DepositCash,
    WithdrawCash,
    ClientPayment,
    CreateStock,
    TransferStock,
    CreateDeliveryObligation,
    CreatePayable,
    TransferClaim,
]


class ShowConfig(BaseModel):
    """Display configuration for the run."""
    balances: Optional[List[str]] = Field(
        None,
        description="Agent IDs to show balances for"
    )
    events: Literal["summary", "detailed", "table"] = Field(
        "detailed",
        description="Event display mode"
    )


class ExportConfig(BaseModel):
    """Export configuration for simulation results."""
    balances_csv: Optional[str] = Field(
        None,
        description="Path to export balances CSV"
    )
    events_jsonl: Optional[str] = Field(
        None,
        description="Path to export events JSONL"
    )


class RunConfig(BaseModel):
    """Run configuration for the simulation."""
    mode: Literal["step", "until_stable"] = Field(
        "until_stable",
        description="Simulation run mode"
    )
    max_days: int = Field(90, description="Maximum days to simulate")
    quiet_days: int = Field(2, description="Required quiet days for stable state")
    show: ShowConfig = Field(default_factory=ShowConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)
    
    @field_validator("max_days")
    @classmethod
    def max_days_positive(cls, v):
        if v <= 0:
            raise ValueError("Max days must be positive")
        return v
    
    @field_validator("quiet_days")
    @classmethod
    def quiet_days_non_negative(cls, v):
        if v < 0:
            raise ValueError("Quiet days cannot be negative")
        return v


class ScenarioConfig(BaseModel):
    """Complete scenario configuration."""
    version: int = Field(1, description="Configuration version")
    name: str = Field(..., description="Scenario name")
    description: Optional[str] = Field(None, description="Scenario description")
    policy_overrides: Optional[PolicyOverrides] = Field(
        None,
        description="Policy engine overrides"
    )
    agents: List[AgentSpec] = Field(..., description="Agents in the scenario")
    initial_actions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Actions to execute during setup"
    )
    scheduled_actions: List[ScheduledAction] = Field(
        default_factory=list,
        description="Actions to execute during simulation (Phase B1) by day"
    )
    run: RunConfig = Field(default_factory=RunConfig)
    
    @field_validator("version")
    @classmethod
    def version_supported(cls, v):
        if v != 1:
            raise ValueError(f"Unsupported configuration version: {v}")
        return v
    
    @field_validator("agents")
    @classmethod
    def agents_unique_ids(cls, v):
        ids = [agent.id for agent in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Agent IDs must be unique")
        return v
