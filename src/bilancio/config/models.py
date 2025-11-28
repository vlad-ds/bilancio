"""Pydantic models for Bilancio scenario configuration."""

from typing import Literal, Optional, Union, List, Dict, Any, Annotated
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator


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
    default_handling: Literal["fail-fast", "expel-agent"] = Field(
        "fail-fast",
        description="How the engine reacts when an agent defaults"
    )
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


class DealerBucketConfig(BaseModel):
    """Configuration for a dealer ring bucket."""
    tau_min: int = Field(..., description="Minimum remaining maturity (inclusive)")
    tau_max: int = Field(..., description="Maximum remaining maturity (inclusive), use 999 for unbounded")
    M: Decimal = Field(Decimal("1.0"), description="Mid anchor price")
    O: Decimal = Field(Decimal("0.30"), description="Spread")

    @field_validator("tau_min", "tau_max")
    @classmethod
    def maturity_positive(cls, v):
        if v < 1:
            raise ValueError("Maturity bounds must be positive")
        return v

    @field_validator("M")
    @classmethod
    def mid_price_positive(cls, v):
        if v <= 0:
            raise ValueError("Mid price M must be positive")
        return v

    @field_validator("O")
    @classmethod
    def spread_positive(cls, v):
        if v <= 0:
            raise ValueError("Spread O must be positive")
        return v

    @model_validator(mode="after")
    def validate_maturity_range(self):
        if self.tau_min > self.tau_max:
            raise ValueError("tau_min must be <= tau_max")
        return self


class DealerOrderFlowConfig(BaseModel):
    """Configuration for dealer order flow arrival process."""
    pi_sell: Decimal = Field(Decimal("0.5"), description="Probability of SELL vs BUY (0-1)")
    N_max: int = Field(3, description="Max trades per arrival")

    @field_validator("pi_sell")
    @classmethod
    def pi_sell_valid(cls, v):
        if not (0 <= v <= 1):
            raise ValueError("pi_sell must be between 0 and 1")
        return v

    @field_validator("N_max")
    @classmethod
    def n_max_positive(cls, v):
        if v < 1:
            raise ValueError("N_max must be positive")
        return v


class DealerTraderPolicyConfig(BaseModel):
    """Configuration for dealer trader policy parameters."""
    horizon_H: int = Field(3, description="Trading horizon (days ahead to consider shortfall)")
    buffer_B: Decimal = Field(Decimal("1.0"), description="Liquidity buffer multiplier")

    @field_validator("horizon_H")
    @classmethod
    def horizon_positive(cls, v):
        if v < 1:
            raise ValueError("horizon_H must be positive")
        return v

    @field_validator("buffer_B")
    @classmethod
    def buffer_positive(cls, v):
        if v < 0:
            raise ValueError("buffer_B cannot be negative")
        return v


class DealerConfig(BaseModel):
    """Configuration for dealer subsystem."""
    enabled: bool = Field(False, description="Whether dealer subsystem is active")
    ticket_size: Decimal = Field(Decimal("1"), description="Face value of tickets")
    buckets: Optional[Dict[str, DealerBucketConfig]] = Field(
        None,
        description="Bucket configurations by name (short, mid, long)"
    )
    dealer_share: Decimal = Field(Decimal("0.25"), description="Fraction of system value for dealer capital")
    vbt_share: Decimal = Field(Decimal("0.50"), description="Fraction for VBT capital")
    order_flow: DealerOrderFlowConfig = Field(
        default_factory=DealerOrderFlowConfig,
        description="Order flow arrival configuration"
    )
    trader_policy: DealerTraderPolicyConfig = Field(
        default_factory=DealerTraderPolicyConfig,
        description="Trader policy configuration"
    )

    @field_validator("ticket_size")
    @classmethod
    def ticket_size_positive(cls, v):
        if v <= 0:
            raise ValueError("ticket_size must be positive")
        return v

    @field_validator("dealer_share", "vbt_share")
    @classmethod
    def share_valid(cls, v):
        if not (0 <= v <= 1):
            raise ValueError("Share values must be between 0 and 1")
        return v

    @model_validator(mode="after")
    def set_default_buckets(self):
        if self.buckets is None:
            self.buckets = {
                "short": DealerBucketConfig(
                    tau_min=1,
                    tau_max=3,
                    M=Decimal("1.0"),
                    O=Decimal("0.20")
                ),
                "mid": DealerBucketConfig(
                    tau_min=4,
                    tau_max=8,
                    M=Decimal("1.0"),
                    O=Decimal("0.30")
                ),
                "long": DealerBucketConfig(
                    tau_min=9,
                    tau_max=999,
                    M=Decimal("1.0"),
                    O=Decimal("0.40")
                ),
            }
        return self


class ScenarioConfig(BaseModel):
    """Complete scenario configuration."""
    version: int = Field(1, description="Configuration version")
    name: str = Field(..., description="Scenario name")
    description: Optional[str] = Field(None, description="Scenario description")
    policy_overrides: Optional[PolicyOverrides] = Field(
        None,
        description="Policy engine overrides"
    )
    dealer: Optional[DealerConfig] = Field(
        None,
        description="Dealer subsystem configuration"
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


class RingExplorerLiquidityAllocation(BaseModel):
    """Liquidity seeding strategy for ring explorer generator."""

    mode: Literal["single_at", "uniform", "vector"] = Field(
        "uniform",
        description="Distribution mode for initial liquidity"
    )
    agent: Optional[str] = Field(
        None,
        description="Target agent for single_at mode"
    )
    vector: Optional[List[Decimal]] = Field(
        None,
        description="Explicit per-agent liquidity shares (length = n_agents)"
    )

    @model_validator(mode="after")
    def validate_allocation(self):
        if self.mode == "single_at" and not self.agent:
            raise ValueError("liquidity.allocation.agent is required for single_at mode")
        if self.mode == "vector":
            if not self.vector:
                raise ValueError("liquidity.allocation.vector is required for vector mode")
            if any(v <= 0 for v in self.vector):
                raise ValueError("liquidity.allocation.vector must contain positive values")
        return self


class RingExplorerLiquidityConfig(BaseModel):
    """Liquidity configuration for ring explorer generator."""

    total: Optional[Decimal] = Field(
        None,
        description="Total initial liquidity to seed",
    )
    allocation: RingExplorerLiquidityAllocation = Field(
        default_factory=RingExplorerLiquidityAllocation,
        description="Allocation strategy for initial liquidity",
    )

    @field_validator("total")
    @classmethod
    def total_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("liquidity.total must be positive when provided")
        return v


class RingExplorerInequalityConfig(BaseModel):
    """Dirichlet-based inequality controls."""

    scheme: Literal["dirichlet"] = Field(
        "dirichlet",
        description="Payable size distribution scheme"
    )
    concentration: Decimal = Field(
        Decimal("1"),
        description="Dirichlet concentration parameter (c > 0)"
    )
    monotonicity: Decimal = Field(
        Decimal("0"),
        ge=Decimal("-1"),
        le=Decimal("1"),
        description="Ordering control (-1 asc, 0 random, 1 desc)"
    )

    @field_validator("concentration")
    @classmethod
    def concentration_positive(cls, v):
        if v <= 0:
            raise ValueError("inequality.concentration must be positive")
        return v


class RingExplorerMaturityConfig(BaseModel):
    """Maturity misalignment controls."""

    days: int = Field(
        1,
        ge=1,
        description="Horizon of due days (max due_day)"
    )
    mode: Literal["lead_lag"] = Field(
        "lead_lag",
        description="Maturity offset mode"
    )
    mu: Decimal = Field(
        Decimal("0"),
        ge=Decimal("0"),
        le=Decimal("1"),
        description="Normalized lead-lag misalignment (0 <= mu <= 1)"
    )


class RingExplorerParamsModel(BaseModel):
    """Parameter block for ring explorer generator."""

    n_agents: int = Field(5, ge=3, description="Number of agents in the ring")
    seed: int = Field(42, description="PRNG seed for reproducibility")
    kappa: Decimal = Field(..., gt=0, description="Debt-to-liquidity ratio target")
    liquidity: RingExplorerLiquidityConfig = Field(
        default_factory=RingExplorerLiquidityConfig,
        description="Liquidity seeding controls"
    )
    inequality: RingExplorerInequalityConfig = Field(
        default_factory=RingExplorerInequalityConfig,
        description="Payable distribution controls"
    )
    maturity: RingExplorerMaturityConfig = Field(
        default_factory=RingExplorerMaturityConfig,
        description="Maturity misalignment controls"
    )
    currency: str = Field("USD", description="Currency label for descriptions")
    Q_total: Optional[Decimal] = Field(
        None,
        description="Total dues on day 1 (S1). Overrides derivation from liquidity when provided"
    )
    policy_overrides: Optional[PolicyOverrides] = Field(
        None,
        description="Policy overrides to apply to generated scenario"
    )


class GeneratorCompileConfig(BaseModel):
    """Common compile-time options for generators."""

    out_dir: Optional[str] = Field(
        None,
        description="Directory to emit compiled scenarios"
    )
    emit_yaml: bool = Field(
        True,
        description="Whether to write the compiled scenario to disk"
    )


class RingExplorerGeneratorConfig(BaseModel):
    """Generator definition for ring explorer sweeps."""

    version: int = Field(1, description="Configuration version")
    generator: Literal["ring_explorer_v1"] = Field(
        "ring_explorer_v1",
        description="Generator identifier"
    )
    name_prefix: str = Field(..., description="Human-readable prefix for scenario names")
    params: RingExplorerParamsModel = Field(..., description="Generator parameters")
    compile: GeneratorCompileConfig = Field(
        default_factory=GeneratorCompileConfig,
        description="Compiler output controls"
    )

    @field_validator("version")
    @classmethod
    def version_supported(cls, v):
        if v != 1:
            raise ValueError(f"Unsupported generator version: {v}")
        return v


GeneratorConfig = Annotated[
    Union[
        RingExplorerGeneratorConfig,
    ],
    Field(discriminator="generator")
]
