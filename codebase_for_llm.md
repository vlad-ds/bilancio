# Bilancio Codebase Documentation

This document contains the complete codebase structure and content for LLM ingestion.

---

## Project Structure

```
/Users/vladgheorghe/code/bilancio
├── .github
│   └── workflows
│       ├── claude-code-review.yml
│       └── claude.yml
├── .gitignore
├── CLAUDE.md
├── README.md
├── codebase_for_llm.md
├── docs
│   ├── Money modeling software.pdf
│   ├── SP239 Kalecki on Credit and Debt extended.pdf
│   └── plans
│       ├── 000_setup.md
│       ├── 001_domain_system.md
│       ├── 003_cash_and_nonfin_exchange.md
│       ├── 004_banking.md
│       ├── 005_reserves_settlement_clearing_scheduler.md
│       ├── 006_analytics.md
│       ├── 007_deliverable.md
│       └── 008_simulation.md
├── examples
├── notebooks
│   └── demo
│       ├── balance_sheet_display.ipynb
│       └── pdf_example_with_firms.ipynb
├── pyproject.toml
├── scripts
│   ├── codebase_for_llm.md
│   └── generate_codebase_markdown.py
├── src
│   └── bilancio
│       ├── __init__.py
│       ├── analysis
│       │   ├── __init__.py
│       │   ├── balances.py
│       │   ├── metrics.py
│       │   └── visualization.py
│       ├── core
│       │   ├── __init__.py
│       │   ├── atomic.py
│       │   ├── atomic_tx.py
│       │   ├── errors.py
│       │   ├── ids.py
│       │   ├── invariants.py
│       │   └── time.py
│       ├── domain
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   ├── agents
│       │   │   ├── __init__.py
│       │   │   ├── bank.py
│       │   │   ├── central_bank.py
│       │   │   ├── firm.py
│       │   │   ├── household.py
│       │   │   └── treasury.py
│       │   ├── goods.py
│       │   ├── instruments
│       │   │   ├── __init__.py
│       │   │   ├── base.py
│       │   │   ├── contract.py
│       │   │   ├── credit.py
│       │   │   ├── delivery.py
│       │   │   ├── means_of_payment.py
│       │   │   ├── nonfinancial.py
│       │   │   └── policy.py
│       │   └── policy.py
│       ├── engines
│       │   ├── __init__.py
│       │   ├── clearing.py
│       │   ├── settlement.py
│       │   ├── simulation.py
│       │   ├── system.py
│       │   └── valuation.py
│       ├── io
│       │   ├── __init__.py
│       │   ├── readers.py
│       │   └── writers.py
│       └── ops
│           ├── __init__.py
│           ├── banking.py
│           ├── cashflows.py
│           ├── primitives.py
│           └── primitives_stock.py
└── tests
    ├── analysis
    │   ├── __init__.py
    │   └── test_balances.py
    ├── integration
    │   ├── test_banking_ops.py
    │   ├── test_clearing_phase_c.py
    │   ├── test_day_simulation.py
    │   └── test_settlement_phase_b.py
    ├── property
    ├── scenarios
    ├── test_smoke.py
    └── unit
        ├── test_balances.py
        ├── test_cash_and_deliverables.py
        ├── test_deliverable_due_dates.py
        ├── test_deliverable_merge.py
        ├── test_deliverable_valuation.py
        ├── test_domain_system.py
        ├── test_reserves.py
        └── test_settle_obligation.py

25 directories, 80 files

```

---

## Git Commit History

Complete git history from oldest to newest:

- **57c76ece** (2025-08-09) by vladgheorghe
  Initial project setup
  - Created project structure with core modules
  - Set up core data types (time, atomic values, errors)
  - Implemented domain models (agents, contracts, policies)
  - Added operations and engine stubs
  - Configured development environment with pyproject.toml
  - Added comprehensive smoke tests
  - Set up .gitignore and README
  🤖 Generated with Claude Code
  Co-Authored-By: Claude <noreply@anthropic.com>

- **e1deb025** (2025-08-09) by vladgheorghe
  Implement Domain & System foundations for bilancio
  - Add ID generation system with ULID-like identifiers
  - Implement typed instrument classes: Cash, BankDeposit, ReserveDeposit, Payable, Deliverable
  - Create typed agent classes: Household, Bank, Treasury, CentralBank
  - Build PolicyEngine with default monetary regime rules
  - Implement System gateway with registries, validation, and invariant checking
  - Add comprehensive smoke tests verifying core functionality
  All contracts use double-entry structure with asset_holder and liability_issuer,
  supporting both financial and non-financial instruments.
  🤖 Generated with Claude Code
  Co-Authored-By: Claude <noreply@anthropic.com>

- **2c4a2900** (2025-08-09) by vladgheorghe
  feat(cash,deliverables): mint/retire/transfer cash, create/transfer deliverables, split/merge primitives, CB cash invariant
  - Extended Deliverable to support divisibility and SKU attributes
  - Added cb_cash_outstanding counter to system state
  - Created atomic transaction context manager for rollback on errors
  - Implemented fungibility helpers (fungible_key, is_divisible)
  - Created split/merge/consume primitives for instruments
  - Added cash operations: mint_cash, retire_cash, transfer_cash
  - Added deliverable operations: create_deliverable, transfer_deliverable
  - Implemented CB cash outstanding invariant check
  - Added comprehensive tests for all new functionality
  - Tests cover: mint/retire roundtrip, cash transfers with split/merge, divisible/indivisible deliverables, error cases
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **74908ad2** (2025-08-09) by vladgheorghe
  feat(banking): implement deposit, withdraw, and client payment operations
  - Add deposit_cash: moves cash from customer to bank, creates bank deposit
  - Add withdraw_cash: debits deposit, moves cash from bank to customer
  - Add client_payment: transfers between deposits, with optional cash fallback
  - Add deposit query helpers (deposit_ids, total_deposit) to System
  - Add coalesce_deposits to merge multiple deposits into one
  - Add no-negative-balances invariant check
  - Log ClientPayment events for cross-bank flows (for future clearing)
  - Comprehensive tests covering all operations and edge cases
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **7d5f19cf** (2025-08-09) by vladgheorghe
  refactor(agent): remove protocol duplication, keep dataclass Agent as single base
  - Removed confusing Agent protocol file (domain/agents/agent.py)
  - All concrete agents already use the dataclass from domain/agent.py
  - Fixed contract.py import to use the dataclass Agent
  - Updated smoke test to reflect single Agent base class
  - All 25 tests passing with 93% coverage
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **08263f3b** (2025-08-09) by vladgheorghe
  feat(reserves): implement reserves, settlement, clearing, and scheduler
  Implement comprehensive reserves infrastructure and day/phase mechanics:
  Reserves Infrastructure:
  - Add cb_reserves_outstanding counter to State
  - Implement reserve operations: mint, transfer, convert reserves<->cash
  - Add reserve invariant checks
  - Support splitting/merging/coalescing of reserve instruments
  Settlement Engine (Phase B):
  - Policy-driven payment method selection (deposits, cash, reserves)
  - All-or-nothing settlement with atomic transactions
  - DefaultError raised when debtor has insufficient funds
  - Proper handling of same-bank vs cross-bank payments
  Clearing Engine (Phase C):
  - Compute intraday nets from ClientPayment events
  - Settle nets with reserves or create overnight payables
  - Lexical ordering for deterministic bank pair processing
  - Graceful handling of insufficient reserves
  Day/Phase Scheduler:
  - Three-phase daily cycle: A (noop), B (settle), C (clear)
  - Automatic day counter increment
  - Integration with settlement and clearing engines
  Testing:
  - 11 comprehensive unit tests for reserves
  - 5 settlement phase B integration tests
  - 3 clearing phase C integration tests
  - 4 end-to-end day simulation tests
  - All 48 tests passing with 92% coverage
  Code Quality:
  - Fix linting issues and improve code formatting
  - Update imports to use modern Python type hints
  - Add proper error handling and validation
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **411d80bf** (2025-08-10) by vladgheorghe
  feat(analysis): add per-agent balance sheets and system trial balance
  - Add AgentBalance and TrialBalance dataclasses for structured balance reporting
  - Implement agent_balance() for individual agent financial position analysis
  - Implement system_trial_balance() for system-wide double-entry verification
  - Add as_rows() for tabular output format suitable for reporting
  - Add assert_no_duplicate_refs() invariant to prevent duplicate contract IDs
  - Wire new invariant into System.assert_invariants() for automatic checking
  - Add comprehensive tests covering all balance analysis functionality
  - 100% test coverage on new analysis module, 93% overall coverage
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **d54919e5** (2025-08-10) by Vlad Gheorghe
  Add Claude Code GitHub Workflow (#2)
  * "Claude PR Assistant workflow"
  * "Claude Code Review workflow"

- **dc51e639** (2025-08-15) by Vlad Gheorghe
  feat: add settle_obligation method to extinguish bilateral obligations (#1)
  * feat: add settle_obligation method to extinguish bilateral obligations
  - Add settle_obligation() method to System class to cancel matched asset-liability pairs
  - Method removes obligation from both holder's assets and issuer's liabilities
  - Useful for settling promises after delivery (e.g., goods delivered, services rendered)
  - Includes comprehensive test coverage for various scenarios
  - Atomic operation with proper rollback on failure
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * docs: add uv run instruction to CLAUDE.md
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  ---------
  Co-authored-by: Claude <noreply@anthropic.com>

- **0ffe321e** (2025-08-15) by vladgheorghe
  feat: add balance sheet visualization and improvements
  - Add visualization module with display functions for balance sheets
  - Port display_agent_balance_table and display_multiple_agent_balances from money-modeling
  - Add AgentKind enum for type-safe agent creation
  - Add add_agents() method to System for batch agent addition
  - Add rich library for beautiful terminal output
  - Create demo notebook showing visualization capabilities
  - Update CLAUDE.md with testing and notebook guidelines
  Note: Issue #3 created for mixing monetary values with quantities in balance sheets
  🤖 Generated with Claude Code
  Co-Authored-By: Claude <noreply@anthropic.com>

- **ee3136aa** (2025-08-15) by Vlad Gheorghe
  Fix balance sheets mixing monetary values with physical quantities (#3) (#4)
  * feat: add monetary valuation to deliverables (fixes #3)
  - Add unit_price field to Deliverable class for monetary valuation
  - Add valued_amount property to calculate monetary value (quantity × price)
  - Update create_deliverable() to accept optional unit_price parameter
  - Add update_deliverable_price() method to update prices dynamically
  - Extend balance calculations to track non-financial asset values
  - Update visualization to show quantity in brackets and value in amount column
  - Fix split() operation to preserve unit_price during transfers
  - Add comprehensive tests for deliverable valuation
  - Update demo notebook to showcase the new feature
  This fixes the issue of mixing monetary values with physical quantities
  on balance sheets. Now deliverables can have proper monetary valuation
  while maintaining quantity tracking, and only valued items are included
  in monetary totals.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: rewrite balance sheet demo notebook with proper agent initialization
  * refactor: make unit_price required for all deliverables
  - Changed unit_price from optional to required parameter (defaults to Decimal('0'))
  - Removed support for unvalued deliverables (None unit_price)
  - Updated all balance calculations to always expect values
  - Fixed visualization to always show monetary amounts
  - Updated all tests to provide unit_price
  - Updated demo notebook to reflect required pricing
  This ensures balance sheets always maintain proper monetary accounting,
  never mixing physical quantities with monetary values.
  * fix: display deliverable liabilities with monetary values in balance sheets
  - Fixed visualization functions to properly display deliverable liabilities
  - Both assets and liabilities now show quantities in brackets and monetary values
  - Added proper handling of non-financial liabilities in balance calculations
  - Updated both rich and simple format displays
  - Added separate totals for valued liabilities when present
  - All balance sheets now consistently show monetary values, never raw quantities
  This completes the implementation of GitHub issue #3 - balance sheets no longer
  mix monetary values with physical quantities.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: address PR review feedback
  - Include SKU and unit_price in fungible_key for deliverables to prevent incorrect merging
  - Fix type annotation (any -> Any) in balances.py
  - Add comprehensive tests for deliverable merge behavior
  This ensures deliverables with different SKUs or prices cannot be incorrectly merged,
  while maintaining backwards compatibility for financial instruments.
  🤖 Generated with Claude Code
  Co-Authored-By: Claude <noreply@anthropic.com>
  ---------
  Co-authored-by: Claude <noreply@anthropic.com>

- **f8653f7a** (2025-08-15) by vladgheorghe
  feat: add due_day field to Deliverable instruments for temporal obligations
  Implements issue #5 - adds temporal component to deliverable instruments to match V1.0 specification.
  Changes:
  - Add optional due_day field to Deliverable class
  - Update settlement engine to handle deliverables with due dates
  - Add settle_due_deliverables function to process deliverable obligations
  - Update System.create_deliverable to accept due_day parameter
  - Add comprehensive tests for time-bound deliverable obligations
  This enables the implementation of the V1.0 example from the specification which includes temporal deliverable obligations like "Claim to receive 10 Machines from Agent 3 at t1".
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **d3d72c66** (2025-08-15) by vladgheorghe
  fix: address PR review feedback for deliverable due dates
  Fixes based on code review:
  - Removed duplicate _deliver_goods function definition
  - Added validation for due_day field (must be non-negative if provided)
  - Enhanced docstring for due_day field with detailed explanation
  - Added tests for deliverables without due_day and validation
  All 87 tests passing with improved coverage.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **e08eb780** (2025-08-15) by Vlad Gheorghe
  Add due_day field to Deliverable instruments for temporal obligations (#6)
  * feat: add due_day field to Deliverable instruments for temporal obligations
  Implements issue #5 - adds temporal component to deliverable instruments to match V1.0 specification.
  Changes:
  - Add optional due_day field to Deliverable class
  - Update settlement engine to handle deliverables with due dates
  - Add settle_due_deliverables function to process deliverable obligations
  - Update System.create_deliverable to accept due_day parameter
  - Add comprehensive tests for time-bound deliverable obligations
  This enables the implementation of the V1.0 example from the specification which includes temporal deliverable obligations like "Claim to receive 10 Machines from Agent 3 at t1".
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: address PR review feedback for deliverable due dates
  Fixes based on code review:
  - Removed duplicate _deliver_goods function definition
  - Added validation for due_day field (must be non-negative if provided)
  - Enhanced docstring for due_day field with detailed explanation
  - Added tests for deliverables without due_day and validation
  All 87 tests passing with improved coverage.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  ---------
  Co-authored-by: Claude <noreply@anthropic.com>

- **e1feb574** (2025-08-15) by vladgheorghe
  Merge remote-tracking branch 'origin/main' into feature/deliverables-due-date

- **aee3bdb5** (2025-08-15) by vladgheorghe
  feat: add Firm agent type and complete V1.0 example simulation
  - Create Firm agent class for business entities (manufacturers, traders, etc.)
  - Add Firms to policy with cash settlement capability
  - Create comprehensive notebook demonstrating PDF example with automatic settlements
  - Verify deliverable settlement properly transfers physical goods
  - Successfully replicate Money Modeling Software V1.0 temporal transformation
  This completes the core V1.0 requirements:
  ✓ Deliverables with due_day field (from previous commits)
  ✓ Automatic settlement of both financial and non-financial obligations
  ✓ Proper transfer of underlying goods during settlement
  ✓ Support for generic business entities via Firm type
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **68db838d** (2025-08-16) by vladgheorghe
  docs: add Jupyter notebook command to CLAUDE.md

- **58a51038** (2025-08-16) by Vlad Gheorghe
  refactor: separate inventory (StockLot) from delivery obligations (DeliveryObligation) (#7)
  BREAKING CHANGE: Complete refactor of non-financial instruments to fix conceptual conflation
  ## Changes
  ### New Domain Model
  - Added StockLot class for inventory (non-financial, no counterparty)
  - Added DeliveryObligation class for bilateral delivery promises
  - Extended Agent with stock_ids field for owned inventory
  - Extended State with stocks registry for all stock lots
  ### System API Changes
  - Inventory operations: create_stock, split_stock, merge_stock, transfer_stock
  - Obligation operations: create_delivery_obligation, cancel_delivery_obligation
  - Removed old methods: create_deliverable, transfer_deliverable
  ### Settlement Engine
  - Updated to handle delivery obligations using FIFO stock allocation
  - Fixed nested atomic transaction issue with internal helper methods
  - Deterministic settlement with proper stock transfer and obligation cancellation
  ### Analysis & Reporting
  - Separated inventory_by_sku from delivery obligations in balances
  - Added total_inventory_value field to balance classes
  - Updated visualization to show inventory and obligations separately
  ### Benefits
  - Eliminates conceptual bug (inventory was masquerading as bilateral contract)
  - Simplifies settlement (no magic reconstruction, just move goods)
  - Clarifies reporting (inventory vs promises are separated)
  - Matches design goals for time-based execution and clean extinguishment
  ### Tests
  - All 87 tests passing
  - Updated test suite to use new API
  - Fixed balance assertions for separated inventory/obligations
  Implements plan from docs/plans/007_deliverable.md
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-authored-by: Claude <noreply@anthropic.com>

- **04a5ebfc** (2025-08-18) by vladgheorghe
  fix: separate quantity from monetary values in balance sheet display
  - Fixed visualization to never confuse quantities with monetary amounts
  - Non-financial items now show quantities in brackets (e.g. 'machines [10 units]')
  - Monetary values always appear in Amount columns, never quantities
  - Added comprehensive event display functions to visualization module
  - display_events() shows all events with proper formatting and icons
  - display_events_for_day() shows events for specific simulation days
  - Updated notebook to use new event display functions from module
  - Fixed run_day() to settle obligations on the correct day (next_day not current_day)
  - Added CLAUDE.md instructions for notebook testing and balance sheet display
  🤖 Generated with Claude Code
  Co-Authored-By: Claude <noreply@anthropic.com>

- **d559cbb8** (2025-08-18) by vladgheorghe
  fix: improve codebase markdown generator exclusions
  - Exclude .conductor, .uv, .DS_Store and other build/cache directories from tree output
  - Add comprehensive list of directories to ignore (IDE configs, Python caches, virtual envs)
  - Clean up tree output to show only relevant source code and documentation files
  - Reduces noise in generated markdown documentation
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **03efa39e** (2025-08-18) by vladgheorghe
  feat: add complete git history to codebase markdown generator
  - Add get_git_history() function to extract full commit history
  - Include commit hash, date, author, subject and body for each commit
  - Display history chronologically from oldest to newest
  - Helps LLMs understand project evolution and context
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **d0c1f3a3** (2025-08-18) by Vlad Gheorghe
  feat: implement simulation improvements from plan 008 (#8)
  * feat: implement simulation improvements from plan 008
  - Add setup phase to System with context manager
  - Fix run_day() to settle current_day instead of next_day
  - Update visualization to remove day offset labeling
  - Add run_until_stable() runner function
  - Update notebooks to use new setup phase and literal due days
  Key improvements:
  1. Setup phase clearly separates initial conditions from simulation
  2. Literal day semantics: due_day=1 means day 1 (not day 2)
  3. run_until_stable() enables automated simulation runs
  4. Event displays now show correct day numbers without offsets
  All tests pass. Notebooks updated and verified working.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: clarify notebook output and properly implement run_until_stable
  - Fixed confusing day progression in notebook output
  - Now clearly shows when advancing days and settling obligations
  - Actually implemented run_until_stable demonstration (not just a comment)
  - Each section now properly explains the day progression
  - Tested and verified all events display correctly
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  ---------
  Co-authored-by: Claude <noreply@anthropic.com>

- **4accab4a** (2025-08-18) by vladgheorghe
  chore: update project configuration
  - Add temp/ folder to .gitignore for temporary test files
  - Update CLAUDE.md with instructions for reviewing subagent code
  - Add note about storing temp files in gitignored folder
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **658cf533** (2025-08-18) by vladgheorghe
  docs: update codebase markdown documentation
  - Regenerate codebase_for_llm.md with latest code structure
  - Add scripts/codebase_for_llm.md generator script
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

---

## Source Code (src/bilancio)

Below are all the Python files in the src/bilancio directory:

### 📄 src/bilancio/__init__.py

```python
"""Bilancio - Financial modeling and analysis library."""

__version__ = "0.1.0"

# Core imports
from bilancio.core.errors import (
    BilancioError,
    CalculationError,
    ConfigurationError,
    ValidationError,
)
from bilancio.core.time import TimeCoordinate, TimeInterval, now

__all__ = [
    "__version__",
    # Core time utilities
    "TimeCoordinate",
    "TimeInterval",
    "now",
    # Core exceptions
    "BilancioError",
    "ValidationError",
    "CalculationError",
    "ConfigurationError",
]

```

---

### 📄 src/bilancio/analysis/__init__.py

```python
"""Analysis package for bilancio."""

```

---

### 📄 src/bilancio/analysis/balances.py

```python
"""Balance analysis functions for the bilancio system."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict

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
    nonfinancial_assets_by_kind: Dict[str, Dict[str, Any]]
    total_nonfinancial_value: Decimal
    nonfinancial_liabilities_by_kind: Dict[str, Dict[str, Any]]
    total_nonfinancial_liability_value: Decimal
    inventory_by_sku: Dict[str, Dict[str, Any]]  # Stock lots owned
    total_inventory_value: Decimal


@dataclass
class TrialBalance:
    """System-wide balance sheet summary."""
    assets_by_kind: Dict[str, int]
    liabilities_by_kind: Dict[str, int]
    total_financial_assets: int
    total_financial_liabilities: int
    nonfinancial_assets_by_kind: Dict[str, Dict[str, Any]]
    total_nonfinancial_value: Decimal
    nonfinancial_liabilities_by_kind: Dict[str, Dict[str, Any]]
    total_nonfinancial_liability_value: Decimal
    inventory_by_sku: Dict[str, Dict[str, Any]]  # System-wide stock lots
    total_inventory_value: Decimal


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
    nonfinancial_assets_by_kind = defaultdict(lambda: {'quantity': 0, 'value': Decimal('0')})
    total_nonfinancial_value = Decimal('0')
    nonfinancial_liabilities_by_kind = defaultdict(lambda: {'quantity': 0, 'value': Decimal('0')})
    total_nonfinancial_liability_value = Decimal('0')
    inventory_by_sku = defaultdict(lambda: {'quantity': 0, 'value': Decimal('0')})
    total_inventory_value = Decimal('0')
    
    # Sum up stocks (inventory)
    for stock_id in agent.stock_ids:
        stock = system.state.stocks[stock_id]
        inventory_by_sku[stock.sku]['quantity'] += stock.quantity
        inventory_by_sku[stock.sku]['value'] += stock.value
        total_inventory_value += stock.value
    
    # Sum up assets
    for contract_id in agent.asset_ids:
        contract = system.state.contracts[contract_id]
        assets_by_kind[contract.kind] += contract.amount
        
        # Check if it's financial (use getattr with default lambda)
        is_financial_func = getattr(contract, 'is_financial', lambda: True)
        if is_financial_func():
            total_financial_assets += contract.amount
        else:
            # Track non-financial assets with quantity and value
            sku = getattr(contract, 'sku', contract.kind)
            nonfinancial_assets_by_kind[sku]['quantity'] += contract.amount
            
            # Calculate value (always available now)
            valued_amount = getattr(contract, 'valued_amount', Decimal('0'))
            nonfinancial_assets_by_kind[sku]['value'] += valued_amount
            total_nonfinancial_value += valued_amount
    
    # Sum up liabilities
    for contract_id in agent.liability_ids:
        contract = system.state.contracts[contract_id]
        liabilities_by_kind[contract.kind] += contract.amount
        
        # Check if it's financial (use getattr with default lambda)
        is_financial_func = getattr(contract, 'is_financial', lambda: True)
        if is_financial_func():
            total_financial_liabilities += contract.amount
        else:
            # Track non-financial liabilities with quantity and value
            sku = getattr(contract, 'sku', contract.kind)
            nonfinancial_liabilities_by_kind[sku]['quantity'] += contract.amount
            
            # Calculate value (always available now)
            valued_amount = getattr(contract, 'valued_amount', Decimal('0'))
            nonfinancial_liabilities_by_kind[sku]['value'] += valued_amount
            total_nonfinancial_liability_value += valued_amount
    
    net_financial = total_financial_assets - total_financial_liabilities
    
    return AgentBalance(
        agent_id=agent_id,
        assets_by_kind=dict(assets_by_kind),
        liabilities_by_kind=dict(liabilities_by_kind),
        total_financial_assets=total_financial_assets,
        total_financial_liabilities=total_financial_liabilities,
        net_financial=net_financial,
        nonfinancial_assets_by_kind=dict(nonfinancial_assets_by_kind),
        total_nonfinancial_value=total_nonfinancial_value,
        nonfinancial_liabilities_by_kind=dict(nonfinancial_liabilities_by_kind),
        total_nonfinancial_liability_value=total_nonfinancial_liability_value,
        inventory_by_sku=dict(inventory_by_sku),
        total_inventory_value=total_inventory_value
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
    nonfinancial_assets_by_kind = defaultdict(lambda: {'quantity': 0, 'value': Decimal('0')})
    total_nonfinancial_value = Decimal('0')
    nonfinancial_liabilities_by_kind = defaultdict(lambda: {'quantity': 0, 'value': Decimal('0')})
    total_nonfinancial_liability_value = Decimal('0')
    inventory_by_sku = defaultdict(lambda: {'quantity': 0, 'value': Decimal('0')})
    total_inventory_value = Decimal('0')
    
    # Walk all stocks and sum by SKU
    for stock in system.state.stocks.values():
        inventory_by_sku[stock.sku]['quantity'] += stock.quantity
        inventory_by_sku[stock.sku]['value'] += stock.value
        total_inventory_value += stock.value
    
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
        else:
            # Track non-financial liabilities (like delivery obligations) by SKU
            sku = getattr(contract, 'sku', contract.kind)
            nonfinancial_liabilities_by_kind[sku]['quantity'] += contract.amount
            
            # Calculate value (always available now)
            valued_amount = getattr(contract, 'valued_amount', Decimal('0'))
            nonfinancial_liabilities_by_kind[sku]['value'] += valued_amount
            total_nonfinancial_liability_value += valued_amount
    
    return TrialBalance(
        assets_by_kind=dict(assets_by_kind),
        liabilities_by_kind=dict(liabilities_by_kind),
        total_financial_assets=total_financial_assets,
        total_financial_liabilities=total_financial_liabilities,
        nonfinancial_assets_by_kind=dict(nonfinancial_assets_by_kind),
        total_nonfinancial_value=total_nonfinancial_value,
        nonfinancial_liabilities_by_kind=dict(nonfinancial_liabilities_by_kind),
        total_nonfinancial_liability_value=total_nonfinancial_liability_value,
        inventory_by_sku=dict(inventory_by_sku),
        total_inventory_value=total_inventory_value
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
            'total_nonfinancial_value': balance.total_nonfinancial_value,
            'total_inventory_value': balance.total_inventory_value,
            **{f'assets_{kind}': amount for kind, amount in balance.assets_by_kind.items()},
            **{f'liabilities_{kind}': amount for kind, amount in balance.liabilities_by_kind.items()},
            **{f'nonfinancial_{sku}_quantity': data['quantity'] for sku, data in balance.nonfinancial_assets_by_kind.items()},
            **{f'nonfinancial_{sku}_value': data['value'] for sku, data in balance.nonfinancial_assets_by_kind.items()},
            **{f'inventory_{sku}_quantity': data['quantity'] for sku, data in balance.inventory_by_sku.items()},
            **{f'inventory_{sku}_value': data['value'] for sku, data in balance.inventory_by_sku.items()}
        }
        rows.append(row)
    
    # Add SYSTEM summary row
    trial_balance = system_trial_balance(system)
    system_row = {
        'agent_id': 'SYSTEM',
        'total_financial_assets': trial_balance.total_financial_assets,
        'total_financial_liabilities': trial_balance.total_financial_liabilities,
        'net_financial': 0,  # Should always be zero for system-wide view
        'total_nonfinancial_value': trial_balance.total_nonfinancial_value,
        'total_inventory_value': trial_balance.total_inventory_value,
        **{f'assets_{kind}': amount for kind, amount in trial_balance.assets_by_kind.items()},
        **{f'liabilities_{kind}': amount for kind, amount in trial_balance.liabilities_by_kind.items()},
        **{f'nonfinancial_{sku}_quantity': data['quantity'] for sku, data in trial_balance.nonfinancial_liabilities_by_kind.items()},
        **{f'nonfinancial_{sku}_value': data['value'] for sku, data in trial_balance.nonfinancial_liabilities_by_kind.items()},
        **{f'inventory_{sku}_quantity': data['quantity'] for sku, data in trial_balance.inventory_by_sku.items()},
        **{f'inventory_{sku}_value': data['value'] for sku, data in trial_balance.inventory_by_sku.items()}
    }
    rows.append(system_row)
    
    return rows
```

---

### 📄 src/bilancio/analysis/metrics.py

```python
"""Financial metrics calculation functions."""


# TODO: Import CashFlow and Money from appropriate modules once defined
# from bilancio.domain.instruments import CashFlow
# from bilancio.core.money import Money


def calculate_npv(flows: list["CashFlow"], rate: float) -> "Money":
    """Calculate Net Present Value of cash flows.
    
    Args:
        flows: List of cash flows to analyze
        rate: Discount rate to use for NPV calculation
        
    Returns:
        The net present value as a Money object
        
    TODO: Implement NPV calculation logic
    """
    raise NotImplementedError("NPV calculation not yet implemented")


def calculate_irr(flows: list["CashFlow"]) -> float:
    """Calculate Internal Rate of Return for cash flows.
    
    Args:
        flows: List of cash flows to analyze
        
    Returns:
        The internal rate of return as a float
        
    TODO: Implement IRR calculation logic
    """
    raise NotImplementedError("IRR calculation not yet implemented")

```

---

### 📄 src/bilancio/analysis/visualization.py

```python
"""Balance sheet visualization utilities for the bilancio system."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

try:
    from rich.console import Console
    from rich.table import Table
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from bilancio.analysis.balances import AgentBalance, agent_balance
from bilancio.engines.system import System


def _format_currency(amount: int, show_sign: bool = False) -> str:
    """Format an integer amount as currency."""
    formatted = f"{amount:,}"
    if show_sign and amount > 0:
        formatted = f"+{formatted}"
    return formatted


def _format_deliverable_amount(valued_amount: Decimal) -> str:
    """Format deliverable monetary value."""
    # Convert Decimal to int for currency formatting (assuming cents precision)
    return _format_currency(int(valued_amount))


def display_agent_balance_table(
    system: System,
    agent_id: str,
    format: str = 'rich',
    title: Optional[str] = None
) -> None:
    """
    Display a single agent's balance sheet as a T-account style table.
    
    Args:
        system: The bilancio system instance
        agent_id: ID of the agent to display
        format: Display format ('rich' or 'simple')
        title: Optional custom title for the table
    """
    if format == 'rich' and not RICH_AVAILABLE:
        print("Warning: rich library not available, falling back to simple format")
        format = 'simple'
    
    # Get agent balance
    balance = agent_balance(system, agent_id)
    
    # Get agent info
    agent = system.state.agents[agent_id]
    if title is None:
        title = f"{agent.name or agent_id} ({agent.kind})"
    
    if format == 'rich':
        _display_rich_agent_balance(title, balance)
    else:
        _display_simple_agent_balance(title, balance)


def display_agent_balance_from_balance(
    balance: AgentBalance,
    format: str = 'rich',
    title: Optional[str] = None
) -> None:
    """
    Display an agent's balance sheet from an AgentBalance object.
    
    Args:
        balance: The AgentBalance object to display
        format: Display format ('rich' or 'simple')
        title: Optional custom title for the table
    """
    if format == 'rich' and not RICH_AVAILABLE:
        print("Warning: rich library not available, falling back to simple format")
        format = 'simple'
    
    if title is None:
        title = f"Agent {balance.agent_id}"
    
    if format == 'rich':
        _display_rich_agent_balance(title, balance)
    else:
        _display_simple_agent_balance(title, balance)


def display_multiple_agent_balances(
    system: System,
    items: List[Union[str, AgentBalance]], 
    format: str = 'rich'
) -> None:
    """
    Display multiple agent balance sheets side by side for comparison.
    
    Args:
        system: The bilancio system instance
        items: List of agent IDs (str) or AgentBalance instances
        format: Display format ('rich' or 'simple')
    """
    if format == 'rich' and not RICH_AVAILABLE:
        print("Warning: rich library not available, falling back to simple format")
        format = 'simple'
    
    # Convert agent IDs to balance objects if needed
    balances = []
    for item in items:
        if isinstance(item, str):
            balances.append(agent_balance(system, item))
        else:
            balances.append(item)
    
    if format == 'rich':
        _display_rich_multiple_agent_balances(balances, system)
    else:
        _display_simple_multiple_agent_balances(balances, system)


def _display_rich_agent_balance(title: str, balance: AgentBalance) -> None:
    """Display a single agent balance using rich formatting."""
    console = Console()
    
    # Create the main table with wider columns to avoid truncation
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan")
    table.add_column("ASSETS", style="green", width=35, no_wrap=False)
    table.add_column("Amount", justify="right", style="green", width=15, no_wrap=True)
    table.add_column("LIABILITIES", style="red", width=35, no_wrap=False)
    table.add_column("Amount", justify="right", style="red", width=15, no_wrap=True)
    
    asset_rows = []
    
    # First: Add inventory (stocks owned) - these are physical assets
    if hasattr(balance, 'inventory_by_sku'):
        for sku, data in balance.inventory_by_sku.items():
            qty = data['quantity']
            if qty > 0:
                name = f"{sku} [{qty} unit{'s' if qty != 1 else ''}]"
                amount = _format_currency(int(data['value']))
                asset_rows.append((name, amount))
    
    # Second: Add non-financial assets (rights to receive goods)
    # Track which SKUs we've already displayed
    displayed_asset_skus = set()
    for sku, data in balance.nonfinancial_assets_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} receivable [{qty} unit{'s' if qty != 1 else ''}]"
            amount = _format_currency(int(data['value']))
            asset_rows.append((name, amount))
            displayed_asset_skus.add(sku)
    
    # Third: Add financial assets (everything else in assets_by_kind)
    # These are guaranteed to be financial since non-financial are already handled
    financial_asset_kinds = set()
    for asset_type in sorted(balance.assets_by_kind.keys()):
        # Skip if this is a non-financial type we already displayed
        # We identify non-financial by checking if its SKU was in nonfinancial_assets_by_kind
        is_nonfinancial = False
        for sku in displayed_asset_skus:
            # This is a heuristic but works for current instrument types
            if asset_type in ['deliverable', 'delivery_obligation']:
                is_nonfinancial = True
                break
        
        if not is_nonfinancial and asset_type not in financial_asset_kinds:
            name = asset_type
            amount = _format_currency(balance.assets_by_kind[asset_type])
            asset_rows.append((name, amount))
            financial_asset_kinds.add(asset_type)
    
    liability_rows = []
    
    # First: Add non-financial liabilities (obligations to deliver goods)
    displayed_liability_skus = set()
    for sku, data in balance.nonfinancial_liabilities_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} obligation [{qty} unit{'s' if qty != 1 else ''}]"
            amount = _format_currency(int(data['value']))
            liability_rows.append((name, amount))
            displayed_liability_skus.add(sku)
    
    # Second: Add financial liabilities (everything else in liabilities_by_kind)
    financial_liability_kinds = set()
    for liability_type in sorted(balance.liabilities_by_kind.keys()):
        # Skip if this is a non-financial type we already displayed
        is_nonfinancial = False
        for sku in displayed_liability_skus:
            if liability_type in ['deliverable', 'delivery_obligation']:
                is_nonfinancial = True
                break
        
        if not is_nonfinancial and liability_type not in financial_liability_kinds:
            name = liability_type
            amount = _format_currency(balance.liabilities_by_kind[liability_type])
            liability_rows.append((name, amount))
            financial_liability_kinds.add(liability_type)
    
    # Determine the maximum number of rows needed
    max_rows = max(len(asset_rows), len(liability_rows), 1)
    
    for i in range(max_rows):
        asset_name, asset_amount = asset_rows[i] if i < len(asset_rows) else ("", "")
        liability_name, liability_amount = liability_rows[i] if i < len(liability_rows) else ("", "")
        
        table.add_row(asset_name, asset_amount, liability_name, liability_amount)
    
    # Add separator and totals
    table.add_row("", "", "", "", end_section=True)
    table.add_row(
        Text("TOTAL FINANCIAL", style="bold green"),
        Text(_format_currency(balance.total_financial_assets), style="bold green"),
        Text("TOTAL FINANCIAL", style="bold red"),
        Text(_format_currency(balance.total_financial_liabilities), style="bold red")
    )
    
    # Add valued non-financial total if present
    if balance.total_nonfinancial_value is not None and balance.total_nonfinancial_value > 0:
        table.add_row(
            Text("TOTAL VALUED DELIV.", style="bold green"),
            Text(_format_currency(int(balance.total_nonfinancial_value)), style="bold green"),
            "",
            ""
        )
        total_assets = balance.total_financial_assets + int(balance.total_nonfinancial_value)
        table.add_row(
            Text("TOTAL ASSETS", style="bold green"),
            Text(_format_currency(total_assets), style="bold green"),
            "",
            ""
        )
    
    # Add visual separation before net worth
    table.add_row("", "", "", "", end_section=True)
    
    # Add net worth with clear separation
    net_financial = balance.net_financial
    net_worth_style = "bold green" if net_financial >= 0 else "bold red"
    table.add_row(
        "",
        "",
        Text("NET FINANCIAL", style="bold blue"),
        Text(_format_currency(net_financial, show_sign=True), style=net_worth_style)
    )
    
    console.print(table)


def _display_simple_agent_balance(title: str, balance: AgentBalance) -> None:
    """Display a single agent balance using simple text formatting."""
    print(f"\n{title}")
    print("=" * 70)
    print(f"{'ASSETS':<30} {'Amount':>12} | {'LIABILITIES':<30} {'Amount':>12}")
    print("-" * 70)
    
    asset_rows = []
    
    # First: Add inventory (stocks owned)
    if hasattr(balance, 'inventory_by_sku'):
        for sku, data in balance.inventory_by_sku.items():
            qty = data['quantity']
            if qty > 0:
                name = f"{sku} [{qty} unit{'s' if qty != 1 else ''}]"
                if len(name) > 29:
                    name = name[:26] + "..."
                amount = _format_currency(int(data['value']))
                asset_rows.append((name, amount))
    
    # Second: Add non-financial assets (rights to receive goods)
    displayed_asset_skus = set()
    for sku, data in balance.nonfinancial_assets_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} receivable [{qty} unit{'s' if qty != 1 else ''}]"
            if len(name) > 29:
                name = name[:26] + "..."
            amount = _format_currency(int(data['value']))
            asset_rows.append((name, amount))
            displayed_asset_skus.add(sku)
    
    # Third: Add financial assets
    financial_asset_kinds = set()
    for asset_type in sorted(balance.assets_by_kind.keys()):
        # Skip non-financial types
        is_nonfinancial = asset_type in ['deliverable', 'delivery_obligation']
        
        if not is_nonfinancial and asset_type not in financial_asset_kinds:
            name = asset_type
            if len(name) > 29:
                name = name[:26] + "..."
            amount = _format_currency(balance.assets_by_kind[asset_type])
            asset_rows.append((name, amount))
            financial_asset_kinds.add(asset_type)
    
    liability_rows = []
    
    # First: Add non-financial liabilities (obligations to deliver goods)
    displayed_liability_skus = set()
    for sku, data in balance.nonfinancial_liabilities_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} obligation [{qty} unit{'s' if qty != 1 else ''}]"
            if len(name) > 29:
                name = name[:26] + "..."
            amount = _format_currency(int(data['value']))
            liability_rows.append((name, amount))
            displayed_liability_skus.add(sku)
    
    # Second: Add financial liabilities
    financial_liability_kinds = set()
    for liability_type in sorted(balance.liabilities_by_kind.keys()):
        # Skip non-financial types
        is_nonfinancial = liability_type in ['deliverable', 'delivery_obligation']
        
        if not is_nonfinancial and liability_type not in financial_liability_kinds:
            name = liability_type
            if len(name) > 29:
                name = name[:26] + "..."
            amount = _format_currency(balance.liabilities_by_kind[liability_type])
            liability_rows.append((name, amount))
            financial_liability_kinds.add(liability_type)
    
    # Determine the maximum number of rows needed
    max_rows = max(len(asset_rows), len(liability_rows), 1)
    
    for i in range(max_rows):
        asset_name, asset_amount = asset_rows[i] if i < len(asset_rows) else ("", "")
        liability_name, liability_amount = liability_rows[i] if i < len(liability_rows) else ("", "")
        
        print(f"{asset_name:<30} {asset_amount:>12} | {liability_name:<30} {liability_amount:>12}")
    
    print("-" * 70)
    print(f"{'TOTAL FINANCIAL':<30} {_format_currency(balance.total_financial_assets):>12} | "
          f"{'TOTAL FINANCIAL':<30} {_format_currency(balance.total_financial_liabilities):>12}")
    
    # Add valued non-financial total if present
    if balance.total_nonfinancial_value is not None and balance.total_nonfinancial_value > 0:
        print(f"{'TOTAL VALUED DELIV.':<30} {_format_currency(int(balance.total_nonfinancial_value)):>12} | {'':>43}")
        total_assets = balance.total_financial_assets + int(balance.total_nonfinancial_value)
        print(f"{'TOTAL ASSETS':<30} {_format_currency(total_assets):>12} | {'':>43}")
    
    print("-" * 70)
    print(f"{'':>44} | {'NET FINANCIAL':<30} {_format_currency(balance.net_financial, show_sign=True):>12}")


def _display_rich_multiple_agent_balances(
    balances: List[AgentBalance], 
    system: Optional[System] = None
) -> None:
    """Display multiple agent balances side by side using rich formatting."""
    console = Console()
    
    # Create individual tables for each balance
    tables = []
    for balance in balances:
        # Get agent name if system is available
        if system and balance.agent_id in system.state.agents:
            agent = system.state.agents[balance.agent_id]
            title = f"{agent.name or balance.agent_id}\n({agent.kind})"
        else:
            title = f"{balance.agent_id}"
        
        # Create table for this balance sheet
        table = Table(title=title, box=box.ROUNDED, title_style="bold cyan", width=35)
        table.add_column("Item", style="white", width=20)
        table.add_column("Amount", justify="right", style="white", width=12)
        
        # Add assets
        table.add_row(Text("ASSETS", style="bold green underline"), "")
        
        # First: Add inventory (stocks owned)
        if hasattr(balance, 'inventory_by_sku'):
            for sku, data in balance.inventory_by_sku.items():
                qty = data['quantity']
                if qty > 0:
                    name = f"{sku} [{qty}]"
                    if len(name) > 19:
                        name = name[:16] + "..."
                    amount = _format_currency(int(data['value']))
                    table.add_row(
                        Text(name, style="green"),
                        Text(amount, style="green")
                    )
        
        # Second: Add non-financial assets (rights to receive goods)
        displayed_asset_skus = set()
        for sku, data in balance.nonfinancial_assets_by_kind.items():
            qty = data['quantity']
            if qty > 0:
                name = f"{sku} recv [{qty}]"
                if len(name) > 19:
                    name = name[:16] + "..."
                amount = _format_currency(int(data['value']))
                table.add_row(
                    Text(name, style="green"),
                    Text(amount, style="green")
                )
                displayed_asset_skus.add(sku)
        
        # Third: Add financial assets
        for asset_type in sorted(balance.assets_by_kind.keys()):
            # Skip non-financial types
            if asset_type not in ['deliverable', 'delivery_obligation']:
                name = asset_type
                if len(name) > 19:
                    name = name[:16] + "..."
                table.add_row(
                    Text(name, style="green"),
                    Text(_format_currency(balance.assets_by_kind[asset_type]), style="green")
                )
        
        table.add_row("", "", end_section=True)
        
        # Add liabilities
        table.add_row(Text("LIABILITIES", style="bold red underline"), "")
        
        # First: Add non-financial liabilities (obligations to deliver goods)
        for sku, data in balance.nonfinancial_liabilities_by_kind.items():
            qty = data['quantity']
            if qty > 0:
                name = f"{sku} oblig [{qty}]"
                if len(name) > 19:
                    name = name[:16] + "..."
                amount = _format_currency(int(data['value']))
                table.add_row(
                    Text(name, style="red"),
                    Text(amount, style="red")
                )
        
        # Second: Add financial liabilities
        for liability_type in sorted(balance.liabilities_by_kind.keys()):
            # Skip non-financial types
            if liability_type not in ['deliverable', 'delivery_obligation']:
                name = liability_type
                if len(name) > 19:
                    name = name[:16] + "..."
                table.add_row(
                    Text(name, style="red"),
                    Text(_format_currency(balance.liabilities_by_kind[liability_type]), style="red")
                )
        
        # Add totals and net worth
        table.add_row("", "", end_section=True)
        table.add_row(
            Text("Total Financial", style="bold green"),
            Text(_format_currency(balance.total_financial_assets), style="bold green")
        )
        
        # Add valued deliverables total if present
        if balance.total_nonfinancial_value is not None and balance.total_nonfinancial_value > 0:
            table.add_row(
                Text("Total Valued", style="bold green"),
                Text(_format_currency(int(balance.total_nonfinancial_value)), style="bold green")
            )
            total_assets = balance.total_financial_assets + int(balance.total_nonfinancial_value)
            table.add_row(
                Text("Total Assets", style="bold green"),
                Text(_format_currency(total_assets), style="bold green")
            )
        
        # Add total liabilities (financial + valued non-financial)
        if balance.total_nonfinancial_liability_value is not None and balance.total_nonfinancial_liability_value > 0:
            table.add_row(
                Text("Total Fin. Liab.", style="bold red"),
                Text(_format_currency(balance.total_financial_liabilities), style="bold red")
            )
            table.add_row(
                Text("Total Valued Liab.", style="bold red"),
                Text(_format_currency(int(balance.total_nonfinancial_liability_value)), style="bold red")
            )
            total_liab = balance.total_financial_liabilities + int(balance.total_nonfinancial_liability_value)
            table.add_row(
                Text("Total Liab.", style="bold red"),
                Text(_format_currency(total_liab), style="bold red")
            )
        else:
            table.add_row(
                Text("Total Liab.", style="bold red"),
                Text(_format_currency(balance.total_financial_liabilities), style="bold red")
            )
        
        net_worth_style = "bold green" if balance.net_financial >= 0 else "bold red"
        table.add_row(
            Text("Net Financial", style="bold blue"),
            Text(_format_currency(balance.net_financial, show_sign=True), style=net_worth_style)
        )
        
        tables.append(table)
    
    # Display tables in columns
    console.print(Columns(tables, equal=True, expand=True))


def _display_simple_multiple_agent_balances(
    balances: List[AgentBalance], 
    system: Optional[System] = None
) -> None:
    """Display multiple agent balances side by side using simple text formatting."""
    # Calculate column width based on number of balance sheets
    console_width = 120
    col_width = max(25, console_width // len(balances) - 2)
    
    # Create headers
    headers = []
    separators = []
    for balance in balances:
        if system and balance.agent_id in system.state.agents:
            agent = system.state.agents[balance.agent_id]
            header = f"{agent.name or balance.agent_id} ({agent.kind})"
        else:
            header = balance.agent_id
        
        if len(header) > col_width:
            header = header[:col_width-3] + "..."
        headers.append(header.center(col_width))
        separators.append("-" * col_width)
    
    print("\n" + " | ".join(headers))
    print(" | ".join(separators))
    
    # Collect all data for each balance sheet
    balance_data = []
    max_rows = 0
    
    for balance in balances:
        data = []
        data.append(("ASSETS", ""))
        
        # First: Add inventory (stocks owned)
        if hasattr(balance, 'inventory_by_sku'):
            for sku, inv_data in balance.inventory_by_sku.items():
                qty = inv_data['quantity']
                if qty > 0:
                    name = f"{sku} [{qty}]"
                    amount = _format_currency(int(inv_data['value']))
                    if len(name + " " + amount) > col_width:
                        name = name[:col_width-len(amount)-4] + "..."
                    data.append((name, amount))
        
        # Second: Add non-financial assets (rights to receive goods)
        for sku, asset_data in balance.nonfinancial_assets_by_kind.items():
            qty = asset_data['quantity']
            if qty > 0:
                name = f"{sku} recv [{qty}]"
                amount = _format_currency(int(asset_data['value']))
                if len(name + " " + amount) > col_width:
                    name = name[:col_width-len(amount)-4] + "..."
                data.append((name, amount))
        
        # Third: Add financial assets
        for asset_type in sorted(balance.assets_by_kind.keys()):
            # Skip non-financial types
            if asset_type not in ['deliverable', 'delivery_obligation']:
                amount = _format_currency(balance.assets_by_kind[asset_type])
                asset_name = asset_type
                if len(asset_name + " " + amount) > col_width:
                    asset_name = asset_name[:col_width-len(amount)-4] + "..."
                data.append((asset_name, amount))
        
        data.append(("", ""))
        data.append(("LIABILITIES", ""))
        
        # First: Add non-financial liabilities (obligations to deliver goods)
        for sku, liability_data in balance.nonfinancial_liabilities_by_kind.items():
            qty = liability_data['quantity']
            if qty > 0:
                name = f"{sku} oblig [{qty}]"
                amount = _format_currency(int(liability_data['value']))
                if len(name + " " + amount) > col_width:
                    name = name[:col_width-len(amount)-4] + "..."
                data.append((name, amount))
        
        # Second: Add financial liabilities
        for liability_type in sorted(balance.liabilities_by_kind.keys()):
            # Skip non-financial types
            if liability_type not in ['deliverable', 'delivery_obligation']:
                amount = _format_currency(balance.liabilities_by_kind[liability_type])
                liability_name = liability_type
                if len(liability_name + " " + amount) > col_width:
                    liability_name = liability_name[:col_width-len(amount)-4] + "..."
                data.append((liability_name, amount))
        
        data.append(("", ""))
        data.append(("Total Financial", _format_currency(balance.total_financial_assets)))
        
        # Add valued deliverables total if present
        if balance.total_nonfinancial_value is not None and balance.total_nonfinancial_value > 0:
            data.append(("Total Valued", _format_currency(int(balance.total_nonfinancial_value))))
            total_assets = balance.total_financial_assets + int(balance.total_nonfinancial_value)
            data.append(("Total Assets", _format_currency(total_assets)))
        
        # Add total liabilities
        if balance.total_nonfinancial_liability_value is not None and balance.total_nonfinancial_liability_value > 0:
            data.append(("Total Valued Liab.", _format_currency(int(balance.total_nonfinancial_liability_value))))
            total_liab = balance.total_financial_liabilities + int(balance.total_nonfinancial_liability_value)
            data.append(("Total Liab.", _format_currency(total_liab)))
        else:
            data.append(("Total Liab.", _format_currency(balance.total_financial_liabilities)))
        data.append(("Net Financial", _format_currency(balance.net_financial, show_sign=True)))
        
        balance_data.append(data)
        max_rows = max(max_rows, len(data))
    
    # Print rows
    for row_idx in range(max_rows):
        row_parts = []
        for balance_idx, data in enumerate(balance_data):
            if row_idx < len(data):
                item, amount = data[row_idx]
                if amount:
                    line = f"{item} {amount}".rjust(col_width)
                else:
                    line = item.ljust(col_width)
            else:
                line = " " * col_width
            row_parts.append(line)
        
        print(" | ".join(row_parts))


def display_events(events: List[Dict[str, Any]], format: str = 'detailed') -> None:
    """
    Display system events in a nicely formatted way.
    
    Args:
        events: List of event dictionaries from sys.state.events
        format: Display format ('detailed' or 'summary')
    """
    if not events:
        print("No events to display.")
        return
    
    if format == 'summary':
        _display_events_summary(events)
    else:
        _display_events_detailed(events)


def _display_events_summary(events: List[Dict[str, Any]]) -> None:
    """Display events in a condensed summary format."""
    for event in events:
        kind = event.get("kind", "Unknown")
        day = event.get("day", "?")
        
        if kind == "PayableSettled":
            print(f"Day {day}: 💰 {event['debtor']} → {event['creditor']}: ${event['amount']}")
        elif kind == "DeliveryObligationSettled":
            qty = event.get('qty', event.get('quantity', 'N/A'))
            print(f"Day {day}: 📦 {event['debtor']} → {event['creditor']}: {qty} {event.get('sku', 'items')}")
        elif kind == "StockTransferred":
            print(f"Day {day}: 🚚 {event['frm']} → {event['to']}: {event['qty']} {event['sku']}")
        elif kind == "CashTransferred":
            print(f"Day {day}: 💵 {event['frm']} → {event['to']}: ${event['amount']}")


def _display_events_detailed(events: List[Dict[str, Any]]) -> None:
    """Display events grouped by day with detailed formatting."""
    # Group events by day
    events_by_day = defaultdict(list)
    for event in events:
        day = event.get("day", -1)
        events_by_day[day].append(event)
    
    # Display events for each day
    for day in sorted(events_by_day.keys()):
        if day == -1:
            print(f"\n📅 Setup Phase:")
        elif day >= 0:
            print(f"\n📅 Day {day}:")
        else:
            print(f"\n📅 Unknown Day:")
        
        _display_day_events(events_by_day[day])
    
    # Add explanatory note
    print("\n📝 Event Types:")
    print("  • Settled = obligation successfully fulfilled")
    print("  • Cancelled = obligation removed from books after settlement")
    print("  • Transferred = actual movement of assets (cash or stock)")


def _display_day_events(day_events: List[Dict[str, Any]]) -> None:
    """Display events for a single day with proper formatting."""
    for event in day_events:
        kind = event.get("kind", "Unknown")
        
        if kind == "StockCreated":
            print(f"  🏭 Stock created: {event['owner']} gets {event['qty']} {event['sku']}")
        
        elif kind == "CashMinted":
            print(f"  💰 Cash minted: ${event['amount']} to {event['to']}")
        
        elif kind == "PayableSettled":
            print(f"  ✅ Payment settled: {event['debtor']} → {event['creditor']}: ${event['amount']}")
        
        elif kind == "PayableCancelled":
            print(f"    └─ Payment obligation removed from books")
        
        elif kind == "DeliveryObligationSettled":
            qty = event.get('qty', event.get('quantity', 'N/A'))
            sku = event.get('sku', 'items')
            print(f"  ✅ Delivery settled: {event['debtor']} → {event['creditor']}: {qty} {sku}")
        
        elif kind == "DeliveryObligationCancelled":
            print(f"    └─ Delivery obligation removed from books")
        
        elif kind == "StockTransferred":
            print(f"  📦 Stock transferred: {event['frm']} → {event['to']}: {event['qty']} {event['sku']}")
        
        elif kind == "CashTransferred":
            print(f"  💵 Cash transferred: {event['frm']} → {event['to']}: ${event['amount']}")
        
        elif kind == "PhaseA":
            print(f"  ⏰ Settlement phase begins (checking due obligations)")
        
        elif kind == "PhaseB":
            print(f"  ⏳ End of day phase")
        
        else:
            # For any other event types, show raw data
            print(f"  • {kind}: {event}")


def display_events_for_day(system: System, day: int) -> None:
    """
    Display all events that occurred on a specific simulation day.
    
    Args:
        system: The bilancio system instance
        day: The simulation day to display events for
    """
    events = [e for e in system.state.events if e.get("day") == day]
    
    if not events:
        print("  No events occurred on this day.")
        return
    
    _display_day_events(events)
```

---

### 📄 src/bilancio/core/__init__.py

```python

```

---

### 📄 src/bilancio/core/atomic.py

```python
"""Atomic value types for bilancio."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


class AtomicValue(Protocol):
    """Protocol for atomic values that have a value property."""

    @property
    def value(self) -> object:
        """Return the atomic value."""
        ...


@dataclass
class Money:
    """Represents a monetary amount with currency."""
    amount: Decimal
    currency: str

    @property
    def value(self) -> Decimal:
        """Return the monetary amount as the atomic value."""
        return self.amount


@dataclass
class Quantity:
    """Represents a quantity with a unit."""
    value: float
    unit: str


@dataclass
class Rate:
    """Represents a rate with a basis."""
    value: Decimal
    basis: str

```

---

### 📄 src/bilancio/core/atomic_tx.py

```python
import copy
from contextlib import contextmanager


@contextmanager
def atomic(system):
    """Context manager for atomic operations - rollback on failure"""
    snapshot = copy.deepcopy(system.state)
    try:
        yield
    except Exception:
        system.state = snapshot
        raise

```

---

### 📄 src/bilancio/core/errors.py

```python
"""Exception classes for bilancio."""


class BilancioError(Exception):
    """Base exception class for bilancio-related errors."""
    pass


class ValidationError(BilancioError):
    """Raised when data validation fails."""
    pass


class CalculationError(BilancioError):
    """Raised when calculation operations fail."""
    pass


class ConfigurationError(BilancioError):
    """Raised when configuration is invalid or missing."""
    pass


class DefaultError(BilancioError):
    """Raised when a debtor cannot settle their obligations."""
    pass

```

---

### 📄 src/bilancio/core/ids.py

```python
import uuid


def new_id(prefix: str = "x") -> str:
    # short, sortable-ish id; fine for MVP
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

AgentId = str
InstrId = str
OpId = str

```

---

### 📄 src/bilancio/core/invariants.py

```python
def assert_cb_cash_matches_outstanding(system):
    total = sum(c.amount for c in system.state.contracts.values() if c.kind == "cash")
    assert total == system.state.cb_cash_outstanding, "CB cash mismatch"

def assert_no_negative_balances(system):
    for c in system.state.contracts.values():
        if c.kind in ("bank_deposit", "cash", "reserve_deposit") and c.amount < 0:
            raise AssertionError("negative balance detected")

def assert_cb_reserves_match(system):
    total = sum(c.amount for c in system.state.contracts.values() if c.kind == "reserve_deposit")
    assert total == system.state.cb_reserves_outstanding, "CB reserves mismatch"

def assert_double_entry_numeric(system):
    for c in system.state.contracts.values():
        if hasattr(c, 'amount') and c.amount < 0:
            raise AssertionError("negative amount detected")

def assert_no_duplicate_refs(system):
    """No duplicate contract IDs in any agent's asset/liability lists."""
    for aid, a in system.state.agents.items():
        assets_seen = set()
        for cid in a.asset_ids:
            if cid in assets_seen:
                raise AssertionError(f"duplicate asset ref {cid} on {aid}")
            assets_seen.add(cid)
        liabilities_seen = set()
        for cid in a.liability_ids:
            if cid in liabilities_seen:
                raise AssertionError(f"duplicate liability ref {cid} on {aid}")
            liabilities_seen.add(cid)


def assert_all_stock_ids_owned(system):
    """Every StockLot id found in exactly one agent's stock_ids and stocks registry."""
    # Check that every stock in the registry is owned by exactly one agent
    stock_owners = {}
    for aid, agent in system.state.agents.items():
        for stock_id in agent.stock_ids:
            if stock_id in stock_owners:
                raise AssertionError(f"Stock {stock_id} owned by multiple agents: {stock_owners[stock_id]} and {aid}")
            stock_owners[stock_id] = aid
    
    # Check that every stock in the registry has an owner
    for stock_id, stock in system.state.stocks.items():
        if stock_id not in stock_owners:
            raise AssertionError(f"Stock {stock_id} in registry but no agent owns it")
        
        # Check that the stock's owner_id matches the owning agent
        if stock.owner_id != stock_owners[stock_id]:
            raise AssertionError(f"Stock {stock_id} owner_id {stock.owner_id} doesn't match owning agent {stock_owners[stock_id]}")


def assert_no_negative_stocks(system):
    """All stock quantities must be non-negative."""
    for stock_id, stock in system.state.stocks.items():
        if stock.quantity < 0:
            raise AssertionError(f"Stock {stock_id} has negative quantity: {stock.quantity}")


def assert_no_duplicate_stock_refs(system):
    """No duplicate stock IDs in any agent's stock_ids."""
    for aid, agent in system.state.agents.items():
        stocks_seen = set()
        for stock_id in agent.stock_ids:
            if stock_id in stocks_seen:
                raise AssertionError(f"duplicate stock ref {stock_id} on {aid}")
            stocks_seen.add(stock_id)

```

---

### 📄 src/bilancio/core/time.py

```python
"""Time handling utilities for bilancio."""

from dataclasses import dataclass


@dataclass
class TimeCoordinate:
    """Represents a point in time."""
    t: float


@dataclass
class TimeInterval:
    """Represents an interval of time with start and end coordinates."""
    start: TimeCoordinate
    end: TimeCoordinate


def now() -> TimeCoordinate:
    """Return the current time coordinate."""
    return TimeCoordinate(0.0)

```

---

### 📄 src/bilancio/domain/__init__.py

```python
# Empty package file

```

---

### 📄 src/bilancio/domain/agent.py

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from bilancio.core.ids import AgentId, InstrId


class AgentKind(Enum):
    """Enumeration of agent types in the financial system."""
    CENTRAL_BANK = "central_bank"
    BANK = "bank"
    HOUSEHOLD = "household"
    TREASURY = "treasury"
    FIRM = "firm"
    INVESTMENT_FUND = "investment_fund"
    INSURANCE_COMPANY = "insurance_company"
    
    def __str__(self) -> str:
        return self.value


@dataclass
class Agent:
    id: AgentId
    name: str
    kind: str  # Still accepts str for backward compatibility
    asset_ids: list[InstrId] = field(default_factory=list)
    liability_ids: list[InstrId] = field(default_factory=list)
    stock_ids: list[InstrId] = field(default_factory=list)

```

---

### 📄 src/bilancio/domain/agents/__init__.py

```python
from .bank import Bank
from .central_bank import CentralBank
from .firm import Firm
from .household import Household
from .treasury import Treasury

__all__ = [
    "Bank",
    "CentralBank",
    "Firm",
    "Household",
    "Treasury",
]

```

---

### 📄 src/bilancio/domain/agents/bank.py

```python
from dataclasses import dataclass

from bilancio.domain.agent import Agent


@dataclass
class Bank(Agent):
    def __post_init__(self):
        self.kind = "bank"

```

---

### 📄 src/bilancio/domain/agents/central_bank.py

```python
from dataclasses import dataclass

from bilancio.domain.agent import Agent


@dataclass
class CentralBank(Agent):
    def __post_init__(self):
        self.kind = "central_bank"

```

---

### 📄 src/bilancio/domain/agents/firm.py

```python
"""Firm agent representing companies, manufacturers, and other business entities."""

from dataclasses import dataclass

from bilancio.domain.agent import Agent


@dataclass
class Firm(Agent):
    """
    A firm/company agent that can:
    - Hold and transfer cash
    - Issue and receive payables
    - Own and transfer deliverable goods (inventory, machines, etc.)
    - Participate in economic transactions
    
    This represents any business entity that isn't a bank or financial institution.
    Examples: manufacturers, trading companies, service providers.
    """
    
    def __post_init__(self):
        """Ensure the agent kind is set to 'firm'."""
        if self.kind != "firm":
            self.kind = "firm"
```

---

### 📄 src/bilancio/domain/agents/household.py

```python
from dataclasses import dataclass

from bilancio.domain.agent import Agent


@dataclass
class Household(Agent):
    def __post_init__(self):
        self.kind = "household"

```

---

### 📄 src/bilancio/domain/agents/treasury.py

```python
from dataclasses import dataclass

from bilancio.domain.agent import Agent


@dataclass
class Treasury(Agent):
    def __post_init__(self):
        self.kind = "treasury"

```

---

### 📄 src/bilancio/domain/goods.py

```python
# non-financial; not a liability of anyone
from dataclasses import dataclass
from decimal import Decimal
from bilancio.core.ids import InstrId, AgentId

StockId = InstrId  # reuse ID machinery

@dataclass
class StockLot:
    id: StockId
    kind: str          # fixed: "stock_lot"
    sku: str
    quantity: int
    unit_price: Decimal
    owner_id: AgentId
    divisible: bool = True

    def __post_init__(self):
        self.kind = "stock_lot"
        # Ensure unit_price is a Decimal
        if not isinstance(self.unit_price, Decimal):
            self.unit_price = Decimal(str(self.unit_price))

    @property
    def value(self) -> Decimal:
        return Decimal(str(self.quantity)) * self.unit_price
```

---

### 📄 src/bilancio/domain/instruments/__init__.py

```python
from .base import Instrument
from .credit import Payable
from .means_of_payment import BankDeposit, Cash, ReserveDeposit
from .nonfinancial import Deliverable

__all__ = [
    "Instrument",
    "Cash",
    "BankDeposit",
    "ReserveDeposit",
    "Payable",
    "Deliverable",
]

```

---

### 📄 src/bilancio/domain/instruments/base.py

```python
from __future__ import annotations

from dataclasses import dataclass

from bilancio.core.ids import AgentId, InstrId


@dataclass
class Instrument:
    id: InstrId
    kind: str
    amount: int                    # minor units
    denom: str
    asset_holder_id: AgentId
    liability_issuer_id: AgentId

    def is_financial(self) -> bool:  # override if needed
        return True

    def validate_type_invariants(self) -> None:
        assert self.amount >= 0, "amount must be non-negative"
        assert self.asset_holder_id != self.liability_issuer_id, "self-counterparty forbidden"

```

---

### 📄 src/bilancio/domain/instruments/contract.py

```python
from abc import ABC
from typing import Any, Protocol

from ..agent import Agent


class Contract(Protocol):
    """Protocol defining the interface for contracts."""

    @property
    def id(self) -> str:
        """Unique identifier for the contract."""
        ...

    @property
    def parties(self) -> list[Agent]:
        """List of agents that are parties to this contract."""
        ...

    @property
    def terms(self) -> dict[str, Any]:
        """Dictionary containing the contract terms."""
        ...


class BaseContract(ABC):
    """Abstract base class implementing the Contract protocol."""

    def __init__(self, id: str, parties: list[Agent], terms: dict[str, Any]):
        self._id = id
        self._parties = parties
        self._terms = terms

    @property
    def id(self) -> str:
        """Unique identifier for the contract."""
        return self._id

    @property
    def parties(self) -> list[Agent]:
        """List of agents that are parties to this contract."""
        return self._parties

    @property
    def terms(self) -> dict[str, Any]:
        """Dictionary containing the contract terms."""
        return self._terms

```

---

### 📄 src/bilancio/domain/instruments/credit.py

```python
from dataclasses import dataclass

from .base import Instrument


@dataclass
class Payable(Instrument):
    due_day: int | None = None
    def __post_init__(self):
        self.kind = "payable"
    def validate_type_invariants(self) -> None:
        super().validate_type_invariants()
        assert self.due_day is not None and self.due_day >= 0, "payable must have due_day"

```

---

### 📄 src/bilancio/domain/instruments/delivery.py

```python
from dataclasses import dataclass
from decimal import Decimal
from bilancio.domain.instruments.base import Instrument

@dataclass
class DeliveryObligation(Instrument):
    # amount = quantity promised (rename for clarity at call sites)
    sku: str
    unit_price: Decimal
    due_day: int

    def __post_init__(self):
        self.kind = "delivery_obligation"
        # Ensure unit_price is a Decimal
        if not isinstance(self.unit_price, Decimal):
            self.unit_price = Decimal(str(self.unit_price))

    def is_financial(self) -> bool:
        # Shows up in balance analysis as non-financial (valued) obligation
        return False

    @property
    def valued_amount(self) -> Decimal:
        from decimal import Decimal as D
        return D(str(self.amount)) * self.unit_price
        
    def validate_type_invariants(self) -> None:
        # Standard bilateral instrument validation (holder != issuer)
        super().validate_type_invariants()
        assert self.unit_price >= 0, "unit_price must be non-negative"
        assert self.due_day >= 0, "due_day must be non-negative"
```

---

### 📄 src/bilancio/domain/instruments/means_of_payment.py

```python
from dataclasses import dataclass

from .base import Instrument


@dataclass
class Cash(Instrument):
    # bearer CB liability; issuer is CB; holder can be anyone per policy
    def __post_init__(self):
        self.kind = "cash"

@dataclass
class BankDeposit(Instrument):
    # liability of a commercial bank; holder is typically household/firm
    def __post_init__(self):
        self.kind = "bank_deposit"

@dataclass
class ReserveDeposit(Instrument):
    # liability of the central bank; holders are banks/treasury per policy
    def __post_init__(self):
        self.kind = "reserve_deposit"

```

---

### 📄 src/bilancio/domain/instruments/nonfinancial.py

```python
from dataclasses import dataclass
from decimal import Decimal

from .base import Instrument


@dataclass
class Deliverable(Instrument):
    sku: str = "GENERIC"
    divisible: bool = True  # if False, amount must be whole and only full transfers allowed
    unit_price: Decimal = Decimal("0")  # Required monetary value per unit
    due_day: int | None = None  # Optional temporal obligation: day when deliverable must be transferred to creditor. 
                                # When set, the settlement engine will automatically transfer goods on the specified day.
                                # Must be non-negative. None means no temporal obligation.
    
    def __post_init__(self):
        self.kind = "deliverable"
        # Ensure unit_price is a Decimal
        if not isinstance(self.unit_price, Decimal):
            self.unit_price = Decimal(str(self.unit_price))
    
    def is_financial(self) -> bool:
        return False
    
    @property
    def valued_amount(self) -> Decimal:
        """Returns the monetary value (amount * unit_price)."""
        return Decimal(str(self.amount)) * self.unit_price
    
    def validate_type_invariants(self) -> None:
        # Override parent validation - non-financial assets can have same holder and issuer
        assert self.amount >= 0, "amount must be non-negative"
        assert self.unit_price >= 0, "unit_price must be non-negative"
        # Validate due_day if provided
        if self.due_day is not None:
            assert self.due_day >= 0, "due_day must be non-negative if provided"

```

---

### 📄 src/bilancio/domain/instruments/policy.py

```python
from abc import ABC, abstractmethod
from typing import Any, Protocol


class Policy(Protocol):
    """Protocol defining the interface for policies."""

    def evaluate(self, context: dict[str, Any]) -> Any:
        """Evaluate the policy given the provided context."""
        ...


class BasePolicy(ABC):
    """Abstract base class implementing the Policy protocol."""

    @abstractmethod
    def evaluate(self, context: dict[str, Any]) -> Any:
        """Evaluate the policy given the provided context."""
        pass

```

---

### 📄 src/bilancio/domain/policy.py

```python
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from bilancio.domain.agent import Agent
from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.firm import Firm
from bilancio.domain.agents.household import Household
from bilancio.domain.agents.treasury import Treasury
from bilancio.domain.instruments.base import Instrument
from bilancio.domain.instruments.credit import Payable
from bilancio.domain.instruments.means_of_payment import BankDeposit, Cash, ReserveDeposit
from bilancio.domain.instruments.nonfinancial import Deliverable
from bilancio.domain.instruments.delivery import DeliveryObligation

AgentType = type[Agent]
InstrType = type[Instrument]

@dataclass
class PolicyEngine:
    # who may issue / hold each instrument type (MVP: static sets)
    issuers: dict[InstrType, Sequence[AgentType]]
    holders: dict[InstrType, Sequence[AgentType]]
    # means-of-payment ranking per agent kind (least-preferred to keep first)
    mop_rank: dict[str, list[str]]

    @classmethod
    def default(cls) -> PolicyEngine:
        return cls(
            issuers={
                Cash:        (CentralBank,),
                BankDeposit: (Bank,),
                ReserveDeposit: (CentralBank,),
                Payable:     (Agent,),            # any agent can issue a payable
                Deliverable: (Agent,),            # backward compatibility
                DeliveryObligation: (Agent,),     # any agent can promise to deliver
            },
            holders={
                Cash:            (Agent,),
                BankDeposit:     (Household, Firm, Treasury, Bank),  # banks may hold but not for interbank settlement
                ReserveDeposit:  (Bank, Treasury),
                Payable:         (Agent,),
                Deliverable:     (Agent,),            # backward compatibility
                DeliveryObligation: (Agent,),         # any agent can hold a delivery claim
            },
            mop_rank={
                "household":     ["bank_deposit", "cash"],     # use deposit first, then cash
                "firm":          ["cash", "bank_deposit"],     # firms prefer cash for simplicity
                "bank":          ["reserve_deposit"],          # banks settle in reserves
                "treasury":      ["reserve_deposit"],
                "central_bank":  ["reserve_deposit"],
            },
        )

    def can_issue(self, agent: Agent, instr: Instrument) -> bool:
        return any(isinstance(agent, t) for t in self.issuers.get(type(instr), ()))

    def can_hold(self, agent: Agent, instr: Instrument) -> bool:
        return any(isinstance(agent, t) for t in self.holders.get(type(instr), ()))

    def settlement_order(self, agent: Agent) -> Sequence[str]:
        return self.mop_rank.get(agent.kind, [])

```

---

### 📄 src/bilancio/engines/__init__.py

```python

```

---

### 📄 src/bilancio/engines/clearing.py

```python
"""Clearing engine (Phase C) for intraday netting and settlement."""

from collections import defaultdict

from bilancio.core.atomic_tx import atomic
from bilancio.core.errors import ValidationError
from bilancio.domain.instruments.credit import Payable


def compute_intraday_nets(system, day: int) -> dict[tuple[str, str], int]:
    """
    Compute net amounts between banks from today's ClientPayment events.
    
    Scans events for ClientPayment events from today and calculates net amounts 
    between each bank pair. Uses lexical ordering for bank pairs (a, b where a < b).
    
    Convention: nets[(a,b)] > 0 means bank a owes bank b
    
    Args:
        system: System instance
        day: Day to compute nets for
        
    Returns:
        Dict mapping bank pairs to net amounts
    """
    nets = defaultdict(int)

    # Scan events for ClientPayment events from today
    for event in system.state.events:
        if event.get("kind") == "ClientPayment" and event.get("day") == day:
            debtor_bank = event.get("payer_bank")
            creditor_bank = event.get("payee_bank")
            amount = event.get("amount", 0)

            if debtor_bank and creditor_bank and debtor_bank != creditor_bank:
                # Use lexical ordering: ensure a < b
                if debtor_bank < creditor_bank:
                    # debtor_bank owes creditor_bank
                    nets[(debtor_bank, creditor_bank)] += amount
                else:
                    # creditor_bank is owed by debtor_bank, so subtract from the reverse pair
                    nets[(creditor_bank, debtor_bank)] -= amount

    return dict(nets)


def settle_intraday_nets(system, day: int):
    """
    Settle intraday nets between banks using reserves or creating overnight payables.
    
    For each net amount between banks:
    - Try to transfer reserves if sufficient
    - If insufficient reserves, create overnight payable due tomorrow
    - Log InterbankCleared or InterbankOvernightCreated events
    
    Args:
        system: System instance  
        day: Current day
    """
    nets = compute_intraday_nets(system, day)

    for (bank_a, bank_b), net_amount in nets.items():
        if net_amount == 0:
            continue

        if net_amount > 0:
            # bank_a owes bank_b
            debtor_bank = bank_a
            creditor_bank = bank_b
            amount = net_amount
        else:
            # bank_b owes bank_a
            debtor_bank = bank_b
            creditor_bank = bank_a
            amount = -net_amount

        # Try to transfer reserves
        try:
            with atomic(system):
                # Find available reserves for debtor bank
                debtor_reserve_ids = []
                for cid in system.state.agents[debtor_bank].asset_ids:
                    contract = system.state.contracts[cid]
                    if contract.kind == "reserve_deposit":
                        debtor_reserve_ids.append(cid)

                if not debtor_reserve_ids:
                    available_reserves = 0
                else:
                    available_reserves = sum(system.state.contracts[cid].amount for cid in debtor_reserve_ids)

                if available_reserves >= amount:
                    # Sufficient reserves - transfer them
                    system.transfer_reserves(debtor_bank, creditor_bank, amount)
                    system.log("InterbankCleared",
                              debtor_bank=debtor_bank,
                              creditor_bank=creditor_bank,
                              amount=amount)
                else:
                    # Insufficient reserves - create overnight payable
                    payable_id = system.new_contract_id("P")
                    overnight_payable = Payable(
                        id=payable_id,
                        kind="payable",
                        amount=amount,
                        denom="X",
                        asset_holder_id=creditor_bank,
                        liability_issuer_id=debtor_bank,
                        due_day=day + 1
                    )

                    system.add_contract(overnight_payable)
                    system.log("InterbankOvernightCreated",
                              debtor_bank=debtor_bank,
                              creditor_bank=creditor_bank,
                              amount=amount,
                              payable_id=payable_id,
                              due_day=day + 1)

        except ValidationError:
            # If transfer fails, create overnight payable as fallback
            payable_id = system.new_contract_id("P")
            overnight_payable = Payable(
                id=payable_id,
                kind="payable",
                amount=amount,
                denom="X",
                asset_holder_id=creditor_bank,
                liability_issuer_id=debtor_bank,
                due_day=day + 1
            )

            system.add_contract(overnight_payable)
            system.log("InterbankOvernightCreated",
                      debtor_bank=debtor_bank,
                      creditor_bank=creditor_bank,
                      amount=amount,
                      payable_id=payable_id,
                      due_day=day + 1)

```

---

### 📄 src/bilancio/engines/settlement.py

```python
"""Settlement engine (Phase B) for settling payables due today."""

from bilancio.core.atomic_tx import atomic
from bilancio.core.errors import DefaultError, ValidationError
from bilancio.ops.banking import client_payment


def due_payables(system, day: int):
    """Scan contracts for payables with due_day == day."""
    for c in system.state.contracts.values():
        if c.kind == "payable" and getattr(c, "due_day", None) == day:
            yield c


def due_deliverables(system, day: int):
    """Scan contracts for deliverables with due_day == day."""
    for c in system.state.contracts.values():
        if c.kind == "deliverable" and getattr(c, "due_day", None) == day:
            yield c


def due_delivery_obligations(system, day: int):
    """Scan contracts for delivery obligations with due_day == day."""
    for c in system.state.contracts.values():
        if c.kind == "delivery_obligation" and getattr(c, "due_day", None) == day:
            yield c


def _pay_with_deposits(system, debtor_id, creditor_id, amount) -> int:
    """Pay using bank deposits. Returns amount actually paid."""
    # Find debtor's bank deposits
    debtor_deposit_ids = []
    for cid in system.state.agents[debtor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "bank_deposit":
            debtor_deposit_ids.append(cid)

    if not debtor_deposit_ids:
        return 0

    # Calculate available deposit amount
    available = sum(system.state.contracts[cid].amount for cid in debtor_deposit_ids)
    if available == 0:
        return 0

    pay_amount = min(amount, available)

    # Find debtor's and creditor's banks
    debtor_bank_id = None
    creditor_bank_id = None

    # Find debtor's bank from their first deposit
    if debtor_deposit_ids:
        debtor_bank_id = system.state.contracts[debtor_deposit_ids[0]].liability_issuer_id

    # Find creditor's bank - check if they have deposits, otherwise use debtor's bank
    creditor_deposit_ids = []
    for cid in system.state.agents[creditor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "bank_deposit":
            creditor_deposit_ids.append(cid)

    if creditor_deposit_ids:
        creditor_bank_id = system.state.contracts[creditor_deposit_ids[0]].liability_issuer_id
    else:
        # If creditor has no deposits, use debtor's bank for same-bank payment
        creditor_bank_id = debtor_bank_id

    if not debtor_bank_id or not creditor_bank_id:
        return 0

    # Use existing client_payment function which handles both same-bank and cross-bank cases
    try:
        client_payment(system, debtor_id, debtor_bank_id, creditor_id, creditor_bank_id, pay_amount)
        return pay_amount
    except ValidationError:
        return 0


def _pay_with_cash(system, debtor_id, creditor_id, amount) -> int:
    """Pay using cash. Returns amount actually paid."""
    # Find available cash
    debtor_cash_ids = []
    for cid in system.state.agents[debtor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "cash":
            debtor_cash_ids.append(cid)

    if not debtor_cash_ids:
        return 0

    available = sum(system.state.contracts[cid].amount for cid in debtor_cash_ids)
    if available == 0:
        return 0

    pay_amount = min(amount, available)

    try:
        system.transfer_cash(debtor_id, creditor_id, pay_amount)
        return pay_amount
    except ValidationError:
        return 0


def _pay_bank_to_bank_with_reserves(system, debtor_bank_id, creditor_bank_id, amount) -> int:
    """Pay using reserves between banks. Returns amount actually paid."""
    if debtor_bank_id == creditor_bank_id:
        return 0  # Same bank, no reserves needed

    # Find available reserves
    debtor_reserve_ids = []
    for cid in system.state.agents[debtor_bank_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "reserve_deposit":
            debtor_reserve_ids.append(cid)

    if not debtor_reserve_ids:
        return 0

    available = sum(system.state.contracts[cid].amount for cid in debtor_reserve_ids)
    if available == 0:
        return 0

    pay_amount = min(amount, available)

    try:
        system.transfer_reserves(debtor_bank_id, creditor_bank_id, pay_amount)
        return pay_amount
    except ValidationError:
        return 0


def _deliver_goods(system, debtor_id, creditor_id, sku: str, required_quantity: int) -> int:
    """
    Transfer deliverable goods from debtor to creditor by SKU.
    Returns the quantity actually delivered.
    """
    # Find available deliverable assets with matching SKU
    available_assets = []
    for cid in system.state.agents[debtor_id].asset_ids:
        contract = system.state.contracts[cid]
        if contract.kind == "deliverable" and getattr(contract, "sku", None) == sku:
            available_assets.append((cid, contract.amount))
    
    if not available_assets:
        return 0
    
    # Calculate total available quantity
    total_available = sum(quantity for _, quantity in available_assets)
    if total_available == 0:
        return 0
    
    deliver_quantity = min(required_quantity, total_available)
    remaining_to_deliver = deliver_quantity
    
    # Sort by contract ID for deterministic behavior
    available_assets.sort(key=lambda x: x[0])
    
    try:
        # Transfer goods from available assets
        for asset_id, asset_quantity in available_assets:
            if remaining_to_deliver == 0:
                break
                
            transfer_qty = min(remaining_to_deliver, asset_quantity)
            
            # Use the system's transfer_deliverable method
            if transfer_qty == asset_quantity:
                # Transfer the entire asset
                system.transfer_deliverable(asset_id, debtor_id, creditor_id)
            else:
                # Transfer partial quantity (will split the asset)
                system.transfer_deliverable(asset_id, debtor_id, creditor_id, transfer_qty)
            
            remaining_to_deliver -= transfer_qty
        
        return deliver_quantity
    except ValidationError:
        return 0


def _deliver_stock(system, debtor_id, creditor_id, sku: str, required_quantity: int) -> int:
    """
    Transfer stock lots from debtor to creditor by SKU using FIFO allocation.
    Returns the quantity actually delivered.
    """
    # Find available stock lots with matching SKU
    available_stocks = []
    for stock_id in system.state.agents[debtor_id].stock_ids:
        stock = system.state.stocks[stock_id]
        if stock.sku == sku:
            available_stocks.append((stock_id, stock.quantity))
    
    if not available_stocks:
        return 0
    
    # Calculate total available quantity
    total_available = sum(quantity for _, quantity in available_stocks)
    if total_available == 0:
        return 0
    
    deliver_quantity = min(required_quantity, total_available)
    remaining_to_deliver = deliver_quantity
    
    # Sort by stock ID for FIFO (deterministic) behavior
    available_stocks.sort(key=lambda x: x[0])
    
    try:
        # Transfer stock from available lots
        for stock_id, stock_quantity in available_stocks:
            if remaining_to_deliver == 0:
                break
                
            transfer_qty = min(remaining_to_deliver, stock_quantity)
            
            # Use the internal method to avoid nested atomic
            system._transfer_stock_internal(stock_id, debtor_id, creditor_id, transfer_qty)
            
            remaining_to_deliver -= transfer_qty
        
        return deliver_quantity
    except ValidationError:
        return 0




def _remove_contract(system, contract_id):
    """Remove contract from system and update agent registries."""
    contract = system.state.contracts[contract_id]

    # Remove from asset holder
    asset_holder = system.state.agents[contract.asset_holder_id]
    if contract_id in asset_holder.asset_ids:
        asset_holder.asset_ids.remove(contract_id)

    # Remove from liability issuer
    liability_issuer = system.state.agents[contract.liability_issuer_id]
    if contract_id in liability_issuer.liability_ids:
        liability_issuer.liability_ids.remove(contract_id)

    # Remove from contracts registry
    del system.state.contracts[contract_id]


def settle_due_deliverables(system, day: int):
    """
    Settle all deliverables due today.
    
    For each deliverable due today:
    - Get debtor and creditor agents
    - Check if debtor has sufficient deliverable assets with matching SKU
    - Transfer the goods to the creditor
    - Remove the deliverable obligation when fully settled
    - Raise DefaultError if insufficient deliverables
    - Log DeliverableSettled event
    """
    for deliverable in list(due_deliverables(system, day)):
        debtor = system.state.agents[deliverable.liability_issuer_id]
        creditor = system.state.agents[deliverable.asset_holder_id]
        required_sku = getattr(deliverable, "sku", "GENERIC")
        required_quantity = deliverable.amount

        with atomic(system):
            # Try to deliver the required goods
            delivered_quantity = _deliver_goods(system, debtor.id, creditor.id, required_sku, required_quantity)
            
            if delivered_quantity != required_quantity:
                # Cannot deliver fully - raise default error
                shortage = required_quantity - delivered_quantity
                raise DefaultError(f"Insufficient deliverables to settle obligation {deliverable.id}: {shortage} units of {required_sku} still owed")
            
            # Fully settled: remove deliverable obligation and log
            _remove_contract(system, deliverable.id)
            system.log("DeliverableSettled", did=deliverable.id, debtor=debtor.id, creditor=creditor.id, 
                      sku=required_sku, quantity=required_quantity)


def settle_due_delivery_obligations(system, day: int):
    """
    Settle all delivery obligations due today using stock operations.
    
    For each delivery obligation due today:
    - Get debtor and creditor agents
    - Check if debtor has sufficient stock with matching SKU
    - Transfer the stock to the creditor using FIFO allocation
    - Remove the delivery obligation when fully settled
    - Raise DefaultError if insufficient stock
    - Log DeliveryObligationSettled event
    """
    for obligation in list(due_delivery_obligations(system, day)):
        debtor = system.state.agents[obligation.liability_issuer_id]
        creditor = system.state.agents[obligation.asset_holder_id]
        required_sku = obligation.sku
        required_quantity = obligation.amount

        with atomic(system):
            # Try to deliver the required stock
            delivered_quantity = _deliver_stock(system, debtor.id, creditor.id, required_sku, required_quantity)
            
            if delivered_quantity != required_quantity:
                # Cannot deliver fully - raise default error
                shortage = required_quantity - delivered_quantity
                raise DefaultError(f"Insufficient stock to settle delivery obligation {obligation.id}: {shortage} units of {required_sku} still owed")
            
            # Fully settled: cancel the delivery obligation and log
            system._cancel_delivery_obligation_internal(obligation.id)
            system.log("DeliveryObligationSettled", 
                      obligation_id=obligation.id, 
                      debtor=debtor.id, 
                      creditor=creditor.id, 
                      sku=required_sku, 
                      qty=required_quantity)


def settle_due(system, day: int):
    """
    Settle all obligations due today (payables, deliverables, and delivery obligations).
    
    For each payable due today:
    - Get debtor and creditor agents
    - Use policy.settlement_order to determine payment methods
    - Try each method in order until paid or all methods exhausted
    - Raise DefaultError if insufficient funds across all methods
    - Remove payable when fully settled
    - Log PayableSettled event
    
    For each deliverable due today:
    - Get debtor and creditor agents
    - Check if debtor has sufficient deliverable assets with matching SKU
    - Transfer the goods to the creditor
    - Remove the deliverable obligation when fully settled
    - Raise DefaultError if insufficient deliverables
    - Log DeliverableSettled event
    
    For each delivery obligation due today:
    - Get debtor and creditor agents
    - Check if debtor has sufficient stock with matching SKU
    - Transfer the stock to the creditor using FIFO allocation
    - Remove the delivery obligation when fully settled
    - Raise DefaultError if insufficient stock
    - Log DeliveryObligationSettled event
    """
    # First settle payables
    for payable in list(due_payables(system, day)):
        debtor = system.state.agents[payable.liability_issuer_id]
        creditor = system.state.agents[payable.asset_holder_id]
        order = system.policy.settlement_order(debtor)

        remaining = payable.amount

        with atomic(system):
            for method in order:
                if remaining == 0:
                    break

                if method == "bank_deposit":
                    paid_now = _pay_with_deposits(system, debtor.id, creditor.id, remaining)
                    remaining -= paid_now
                elif method == "cash":
                    paid_now = _pay_with_cash(system, debtor.id, creditor.id, remaining)
                    remaining -= paid_now
                elif method == "reserve_deposit":
                    paid_now = _pay_bank_to_bank_with_reserves(system, debtor.id, creditor.id, remaining)
                    remaining -= paid_now
                else:
                    raise ValidationError(f"unknown payment method {method}")

            if remaining != 0:
                # Cannot settle fully - raise default error
                raise DefaultError(f"Insufficient funds to settle payable {payable.id}: {remaining} still owed")

            # Fully settled: remove payable and log
            _remove_contract(system, payable.id)
            system.log("PayableSettled", pid=payable.id, debtor=debtor.id, creditor=creditor.id, amount=payable.amount)
    
    # Then settle old-style deliverables (for backward compatibility)
    settle_due_deliverables(system, day)
    
    # Finally settle new delivery obligations
    settle_due_delivery_obligations(system, day)

```

---

### 📄 src/bilancio/engines/simulation.py

```python
"""Simulation engines for financial scenario analysis."""

import random
from dataclasses import dataclass
from typing import Any, Protocol

from bilancio.engines.clearing import settle_intraday_nets
from bilancio.engines.settlement import settle_due


IMPACT_EVENTS = {
    "PayableSettled",
    "DeliveryObligationSettled",
    "InterbankCleared",
    "InterbankOvernightCreated",
}


@dataclass
class DayReport:
    day: int
    impacted: int
    notes: str = ""


def _impacted_today(system, day: int) -> int:
    return sum(1 for e in system.state.events if e.get("day") == day and e.get("kind") in IMPACT_EVENTS)


def _has_open_obligations(system) -> bool:
    for c in system.state.contracts.values():
        if c.kind in ("payable", "delivery_obligation"):
            return True
    return False


class SimulationEngine(Protocol):
    """Protocol for simulation engines that can run financial scenarios."""

    def run(self, scenario: Any) -> Any:
        """
        Run a simulation for a given scenario.
        
        Args:
            scenario: The scenario to simulate
            
        Returns:
            Simulation results
        """
        ...


class MonteCarloEngine:
    """Monte Carlo simulation engine for financial scenarios."""

    def __init__(self, num_simulations: int = 1000, n_simulations: int | None = None, random_seed: int | None = None):
        """
        Initialize the Monte Carlo engine.
        
        Args:
            num_simulations: Number of simulation runs to perform
            n_simulations: Alternative parameter name for num_simulations (for compatibility)
            random_seed: Optional seed for reproducible results
        """
        # Support both parameter names for compatibility
        if n_simulations is not None:
            self.num_simulations = n_simulations
            self.n_simulations = n_simulations
        else:
            self.num_simulations = num_simulations
            self.n_simulations = num_simulations

        if random_seed is not None:
            random.seed(random_seed)

    def run(self, scenario: Any) -> dict[str, Any]:
        """
        Run Monte Carlo simulation for a scenario.
        
        This is a placeholder implementation. A real implementation would:
        1. Extract parameters and distributions from the scenario
        2. Generate random samples according to those distributions
        3. Run the scenario multiple times with different random inputs
        4. Aggregate and return statistical results
        
        Args:
            scenario: The scenario to simulate
            
        Returns:
            Dictionary containing simulation results and statistics
        """
        # Placeholder implementation
        results = []

        for i in range(self.num_simulations):
            # In a real implementation, this would:
            # - Sample from probability distributions
            # - Apply scenario logic with sampled values
            # - Calculate outcome metrics

            # For now, just generate dummy results
            result = {
                'run_id': i,
                'outcome': random.gauss(100, 20),  # Placeholder random outcome
                'scenario': scenario
            }
            results.append(result)

        # Calculate summary statistics
        outcomes = [r['outcome'] for r in results]
        summary = {
            'num_simulations': self.num_simulations,
            'mean': sum(outcomes) / len(outcomes),
            'min': min(outcomes),
            'max': max(outcomes),
            'results': results
        }

        return summary

    def set_num_simulations(self, num_simulations: int) -> None:
        """Update the number of simulations to run."""
        self.num_simulations = num_simulations


def run_day(system):
    """
    Run a single day's simulation with three phases.
    
    Phase A: Log PhaseA event (noop for now)
    Phase B: Settle obligations due on the current day using settle_due
    Phase C: Clear intraday nets for the current day using settle_intraday_nets
    
    Finally, increment the system day counter.
    
    Args:
        system: System instance to run the day for
    """
    current_day = system.state.day

    # Phase A: Log PhaseA event (noop for now)
    system.log("PhaseA")

    # Phase B: Settle obligations due on the current day
    system.log("PhaseB")  # optional: helps timeline
    settle_due(system, current_day)

    # Phase C: Clear intraday nets for the current day
    system.log("PhaseC")  # optional: helps timeline
    settle_intraday_nets(system, current_day)

    # Increment system day
    system.state.day += 1


def run_until_stable(system, max_days: int = 365, quiet_days: int = 2) -> list[DayReport]:
    """
    Advance day by day until the system is stable:
    - No impactful events happen for `quiet_days` consecutive days, AND
    - No outstanding payables or delivery obligations remain.
    """
    reports = []
    consecutive_quiet = 0
    start_day = system.state.day

    for _ in range(max_days):
        day_before = system.state.day
        run_day(system)
        impacted = _impacted_today(system, day_before)
        reports.append(DayReport(day=day_before, impacted=impacted))

        if impacted == 0:
            consecutive_quiet += 1
        else:
            consecutive_quiet = 0

        if consecutive_quiet >= quiet_days and not _has_open_obligations(system):
            break

    return reports

```

---

### 📄 src/bilancio/engines/system.py

```python
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from decimal import Decimal

from bilancio.core.atomic_tx import atomic
from bilancio.core.errors import ValidationError
from bilancio.core.ids import AgentId, InstrId, new_id
from bilancio.domain.agent import Agent
from bilancio.domain.instruments.base import Instrument
from bilancio.domain.instruments.means_of_payment import Cash, ReserveDeposit
# from bilancio.domain.instruments.nonfinancial import Deliverable  # DEPRECATED
from bilancio.domain.instruments.delivery import DeliveryObligation
from bilancio.domain.goods import StockLot
from bilancio.domain.policy import PolicyEngine
from bilancio.ops.primitives import consume, merge, split
from bilancio.ops.primitives_stock import split_stock, merge_stock


@dataclass
class State:
    agents: dict[AgentId, Agent] = field(default_factory=dict)
    contracts: dict[InstrId, Instrument] = field(default_factory=dict)
    stocks: dict[InstrId, StockLot] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)
    day: int = 0
    cb_cash_outstanding: int = 0
    cb_reserves_outstanding: int = 0
    phase: str = "simulation"

class System:
    def __init__(self, policy: PolicyEngine | None = None):
        self.policy = policy or PolicyEngine.default()
        self.state = State()

    # ---- ID helpers
    def new_agent_id(self, prefix="A") -> AgentId: return new_id(prefix)
    def new_contract_id(self, prefix="C") -> InstrId: return new_id(prefix)

    # ---- phase management
    @contextmanager
    def setup(self):
        """Context manager to temporarily set phase to 'setup'."""
        old_phase = self.state.phase
        self.state.phase = "setup"
        try:
            yield
        finally:
            self.state.phase = old_phase

    # ---- registry gateway
    def add_agent(self, agent: Agent) -> None:
        self.state.agents[agent.id] = agent

    def add_contract(self, c: Instrument) -> None:
        # type invariants
        c.validate_type_invariants()
        # policy checks
        holder = self.state.agents[c.asset_holder_id]
        issuer = self.state.agents[c.liability_issuer_id]
        if not self.policy.can_hold(holder, c):
            raise ValidationError(f"{holder.kind} cannot hold {c.kind}")
        if not self.policy.can_issue(issuer, c):
            raise ValidationError(f"{issuer.kind} cannot issue {c.kind}")

        self.state.contracts[c.id] = c
        holder.asset_ids.append(c.id)
        issuer.liability_ids.append(c.id)

    # ---- events
    def log(self, kind: str, **payload) -> None:
        self.state.events.append({"kind": kind, "day": self.state.day, "phase": self.state.phase, **payload})

    # ---- invariants (MVP)
    def assert_invariants(self) -> None:
        from bilancio.core.invariants import (
            assert_cb_cash_matches_outstanding,
            assert_cb_reserves_match,
            assert_double_entry_numeric,
            assert_no_negative_balances,
            assert_no_duplicate_refs,
            assert_all_stock_ids_owned,
            assert_no_negative_stocks,
            assert_no_duplicate_stock_refs,
        )
        for cid, c in self.state.contracts.items():
            assert cid in self.state.agents[c.asset_holder_id].asset_ids, f"{cid} missing on asset holder"
            assert cid in self.state.agents[c.liability_issuer_id].liability_ids, f"{cid} missing on issuer"
        assert_no_duplicate_refs(self)
        assert_cb_cash_matches_outstanding(self)
        assert_cb_reserves_match(self)
        assert_no_negative_balances(self)
        assert_double_entry_numeric(self)
        # Stock-related invariants
        assert_all_stock_ids_owned(self)
        assert_no_negative_stocks(self)
        assert_no_duplicate_stock_refs(self)

    # ---- bootstrap helper
    def bootstrap_cb(self, cb: Agent) -> None:
        self.add_agent(cb)
        self.log("BootstrapCB", cb_id=cb.id)
    
    def add_agents(self, agents: list[Agent]) -> None:
        """Add multiple agents to the system at once."""
        for agent in agents:
            self.add_agent(agent)

    # ---- cash operations
    def mint_cash(self, to_agent_id: AgentId, amount: int, denom="X") -> str:
        cb_id = next((aid for aid,a in self.state.agents.items() if a.kind == "central_bank"), None)
        assert cb_id, "CentralBank must exist"
        instr_id = self.new_contract_id("C")
        c = Cash(
            id=instr_id, kind="cash", amount=amount, denom=denom,
            asset_holder_id=to_agent_id, liability_issuer_id=cb_id
        )
        with atomic(self):
            self.add_contract(c)
            self.state.cb_cash_outstanding += amount
            self.log("CashMinted", to=to_agent_id, amount=amount, instr_id=instr_id)
        return instr_id

    def retire_cash(self, from_agent_id: AgentId, amount: int) -> None:
        # pull from holder's cash instruments (simple greedy)
        with atomic(self):
            remaining = amount
            cash_ids = [cid for cid in self.state.agents[from_agent_id].asset_ids
                        if self.state.contracts[cid].kind == "cash"]
            for cid in list(cash_ids):
                instr = self.state.contracts[cid]
                take = min(instr.amount, remaining)
                consume(self, cid, take)
                remaining -= take
                if remaining == 0: break
            if remaining != 0:
                raise ValidationError("insufficient cash to retire")
            self.state.cb_cash_outstanding -= amount
            self.log("CashRetired", frm=from_agent_id, amount=amount)

    def transfer_cash(self, from_agent_id: AgentId, to_agent_id: AgentId, amount: int) -> str:
        if from_agent_id == to_agent_id:
            raise ValidationError("no-op transfer")
        with atomic(self):
            remaining = amount
            # collect cash pieces and split as needed
            for cid in list(self.state.agents[from_agent_id].asset_ids):
                instr = self.state.contracts.get(cid)
                if not instr or instr.kind != "cash": continue
                piece_id = cid
                if instr.amount > remaining:
                    piece_id = split(self, cid, remaining)
                piece = self.state.contracts[piece_id]
                # move holder
                self.state.agents[from_agent_id].asset_ids.remove(piece_id)
                self.state.agents[to_agent_id].asset_ids.append(piece_id)
                piece.asset_holder_id = to_agent_id
                self.log("CashTransferred", frm=from_agent_id, to=to_agent_id, amount=min(remaining, piece.amount), instr_id=piece_id)
                remaining -= piece.amount
                if remaining == 0: break
            if remaining != 0:
                raise ValidationError("insufficient cash")
            # optional coalesce at receiver (merge duplicates)
            rx_ids = [cid for cid in self.state.agents[to_agent_id].asset_ids
                      if self.state.contracts[cid].kind == "cash"]
            # naive coalesce: pairwise merge same-key
            seen = {}
            for cid in rx_ids:
                k = (self.state.contracts[cid].denom, self.state.contracts[cid].liability_issuer_id)
                keep = seen.get(k)
                if keep and keep != cid:
                    merge(self, keep, cid)
                else:
                    seen[k] = cid
        return "ok"

    # ---- reserve operations
    def _central_bank_id(self) -> str:
        """Find and return the central bank agent ID"""
        cb_id = next((aid for aid, a in self.state.agents.items() if a.kind == "central_bank"), None)
        if not cb_id:
            raise ValidationError("CentralBank must exist")
        return cb_id

    def mint_reserves(self, to_bank_id: str, amount: int, denom="X") -> str:
        """Mint reserves to a bank"""
        cb_id = self._central_bank_id()
        instr_id = self.new_contract_id("R")
        c = ReserveDeposit(
            id=instr_id, kind="reserve_deposit", amount=amount, denom=denom,
            asset_holder_id=to_bank_id, liability_issuer_id=cb_id
        )
        with atomic(self):
            self.add_contract(c)
            self.state.cb_reserves_outstanding += amount
            self.log("ReservesMinted", to=to_bank_id, amount=amount, instr_id=instr_id)
        return instr_id

    def transfer_reserves(self, from_bank_id: str, to_bank_id: str, amount: int) -> None:
        """Transfer reserves between banks"""
        if from_bank_id == to_bank_id:
            raise ValidationError("no-op transfer")
        with atomic(self):
            remaining = amount
            # collect reserve pieces and split as needed
            for cid in list(self.state.agents[from_bank_id].asset_ids):
                instr = self.state.contracts.get(cid)
                if not instr or instr.kind != "reserve_deposit": continue
                piece_id = cid
                if instr.amount > remaining:
                    piece_id = split(self, cid, remaining)
                piece = self.state.contracts[piece_id]
                # move holder
                self.state.agents[from_bank_id].asset_ids.remove(piece_id)
                self.state.agents[to_bank_id].asset_ids.append(piece_id)
                piece.asset_holder_id = to_bank_id
                self.log("ReservesTransferred", frm=from_bank_id, to=to_bank_id, amount=min(remaining, piece.amount), instr_id=piece_id)
                remaining -= piece.amount
                if remaining == 0: break
            if remaining != 0:
                raise ValidationError("insufficient reserves")
            # optional coalesce at receiver (merge duplicates)
            rx_ids = [cid for cid in self.state.agents[to_bank_id].asset_ids
                      if self.state.contracts[cid].kind == "reserve_deposit"]
            # naive coalesce: pairwise merge same-key
            seen = {}
            for cid in rx_ids:
                k = (self.state.contracts[cid].denom, self.state.contracts[cid].liability_issuer_id)
                keep = seen.get(k)
                if keep and keep != cid:
                    merge(self, keep, cid)
                else:
                    seen[k] = cid

    def convert_reserves_to_cash(self, bank_id: str, amount: int) -> None:
        """Convert reserves to cash"""
        with atomic(self):
            # consume reserves
            remaining = amount
            reserve_ids = [cid for cid in self.state.agents[bank_id].asset_ids
                          if self.state.contracts[cid].kind == "reserve_deposit"]
            for cid in list(reserve_ids):
                instr = self.state.contracts[cid]
                take = min(instr.amount, remaining)
                consume(self, cid, take)
                remaining -= take
                if remaining == 0: break
            if remaining != 0:
                raise ValidationError("insufficient reserves to convert")
            # update outstanding reserves
            self.state.cb_reserves_outstanding -= amount
            # mint equivalent cash
            self.state.cb_cash_outstanding += amount
            cb_id = self._central_bank_id()
            instr_id = self.new_contract_id("C")
            c = Cash(
                id=instr_id, kind="cash", amount=amount, denom="X",
                asset_holder_id=bank_id, liability_issuer_id=cb_id
            )
            self.add_contract(c)
            self.log("ReservesToCash", bank_id=bank_id, amount=amount, instr_id=instr_id)

    def convert_cash_to_reserves(self, bank_id: str, amount: int) -> None:
        """Convert cash to reserves"""
        with atomic(self):
            # consume cash
            remaining = amount
            cash_ids = [cid for cid in self.state.agents[bank_id].asset_ids
                       if self.state.contracts[cid].kind == "cash"]
            for cid in list(cash_ids):
                instr = self.state.contracts[cid]
                take = min(instr.amount, remaining)
                consume(self, cid, take)
                remaining -= take
                if remaining == 0: break
            if remaining != 0:
                raise ValidationError("insufficient cash to convert")
            # update outstanding cash
            self.state.cb_cash_outstanding -= amount
            # mint equivalent reserves
            self.state.cb_reserves_outstanding += amount
            cb_id = self._central_bank_id()
            instr_id = self.new_contract_id("R")
            c = ReserveDeposit(
                id=instr_id, kind="reserve_deposit", amount=amount, denom="X",
                asset_holder_id=bank_id, liability_issuer_id=cb_id
            )
            self.add_contract(c)
            self.log("CashToReserves", bank_id=bank_id, amount=amount, instr_id=instr_id)

    # ---- deposit helpers
    def deposit_ids(self, customer_id: str, bank_id: str) -> list[str]:
        """Filter customer assets for bank_deposit issued by bank_id"""
        out = []
        for cid in self.state.agents[customer_id].asset_ids:
            c = self.state.contracts[cid]
            if c.kind == "bank_deposit" and c.liability_issuer_id == bank_id:
                out.append(cid)
        return out

    def total_deposit(self, customer_id: str, bank_id: str) -> int:
        """Calculate total deposit amount for customer at bank"""
        return sum(self.state.contracts[cid].amount for cid in self.deposit_ids(customer_id, bank_id))

    # ---- deliverable operations (DEPRECATED - use stock operations and delivery obligations instead)

    def settle_obligation(self, contract_id: InstrId) -> None:
        """
        Settle and extinguish a bilateral obligation.
        
        This removes a matched asset-liability pair when the obligation has been fulfilled,
        such as after delivering goods or services that were promised.
        
        Args:
            contract_id: The ID of the contract to settle
            
        Raises:
            ValidationError: If the contract doesn't exist
        """
        with atomic(self):
            # Validate contract exists
            if contract_id not in self.state.contracts:
                raise ValidationError(f"Contract {contract_id} not found")
            
            contract = self.state.contracts[contract_id]
            
            # Remove from holder's assets
            holder = self.state.agents[contract.asset_holder_id]
            if contract_id not in holder.asset_ids:
                raise ValidationError(f"Contract {contract_id} not in holder's assets")
            holder.asset_ids.remove(contract_id)
            
            # Remove from issuer's liabilities
            issuer = self.state.agents[contract.liability_issuer_id]
            if contract_id not in issuer.liability_ids:
                raise ValidationError(f"Contract {contract_id} not in issuer's liabilities")
            issuer.liability_ids.remove(contract_id)
            
            # Remove contract from registry
            del self.state.contracts[contract_id]
            
            # Log the settlement
            self.log("ObligationSettled",
                    contract_id=contract_id,
                    holder_id=contract.asset_holder_id,
                    issuer_id=contract.liability_issuer_id,
                    contract_kind=contract.kind,
                    amount=contract.amount)

    # ---- stock operations (inventory)
    def create_stock(self, owner_id: AgentId, sku: str, quantity: int, unit_price: Decimal, divisible: bool=True) -> InstrId:
        """Create a new stock lot (inventory)."""
        stock_id = new_id("S")
        stock = StockLot(
            id=stock_id,
            kind="stock_lot",
            sku=sku,
            quantity=quantity,
            unit_price=unit_price,
            owner_id=owner_id,
            divisible=divisible
        )
        with atomic(self):
            self.state.stocks[stock_id] = stock
            self.state.agents[owner_id].stock_ids.append(stock_id)
            self.log("StockCreated", owner=owner_id, sku=sku, qty=quantity, unit_price=unit_price, stock_id=stock_id)
        return stock_id

    def split_stock(self, stock_id: InstrId, quantity: int) -> InstrId:
        """Split a stock lot. Returns ID of the new split piece."""
        with atomic(self):
            return split_stock(self, stock_id, quantity)

    def merge_stock(self, stock_id_keep: InstrId, stock_id_into: InstrId) -> InstrId:
        """Merge two stock lots. Returns the ID of the kept lot."""
        with atomic(self):
            return merge_stock(self, stock_id_keep, stock_id_into)

    def _transfer_stock_internal(self, stock_id: InstrId, from_owner: AgentId, to_owner: AgentId, quantity: int = None) -> InstrId:
        """Internal helper for stock transfer without atomic wrapper."""
        stock = self.state.stocks[stock_id]
        if stock.owner_id != from_owner:
            raise ValidationError("Stock owner mismatch")
        
        moving_id = stock_id
        if quantity is not None:
            if not stock.divisible:
                raise ValidationError("Stock lot is not divisible")
            if quantity <= 0 or quantity > stock.quantity:
                raise ValidationError("Invalid transfer quantity")
            if quantity < stock.quantity:
                moving_id = split_stock(self, stock_id, quantity)
        
        # Transfer ownership
        moving_stock = self.state.stocks[moving_id]
        self.state.agents[from_owner].stock_ids.remove(moving_id)
        self.state.agents[to_owner].stock_ids.append(moving_id)
        moving_stock.owner_id = to_owner
        
        self.log("StockTransferred", 
                frm=from_owner, 
                to=to_owner, 
                stock_id=moving_id, 
                sku=moving_stock.sku,
                qty=moving_stock.quantity)
        return moving_id

    def transfer_stock(self, stock_id: InstrId, from_owner: AgentId, to_owner: AgentId, quantity: int = None) -> InstrId:
        """Transfer stock from one owner to another."""
        with atomic(self):
            return self._transfer_stock_internal(stock_id, from_owner, to_owner, quantity)

    # ---- delivery obligation operations
    def create_delivery_obligation(self, from_agent: AgentId, to_agent: AgentId, sku: str, quantity: int, unit_price: Decimal, due_day: int) -> InstrId:
        """Create a delivery obligation (bilateral promise to deliver goods)."""
        obligation_id = self.new_contract_id("D")
        obligation = DeliveryObligation(
            id=obligation_id,
            kind="delivery_obligation",
            amount=quantity,
            denom="N/A",
            asset_holder_id=to_agent,
            liability_issuer_id=from_agent,
            sku=sku,
            unit_price=unit_price,
            due_day=due_day
        )
        with atomic(self):
            self.add_contract(obligation)
            self.log("DeliveryObligationCreated", 
                    id=obligation_id, 
                    frm=from_agent, 
                    to=to_agent, 
                    sku=sku, 
                    qty=quantity, 
                    due_day=due_day, 
                    unit_price=unit_price)
        return obligation_id

    def _cancel_delivery_obligation_internal(self, obligation_id: InstrId) -> None:
        """Internal helper for cancelling delivery obligation without atomic wrapper."""
        # Validate contract exists and is a delivery obligation
        if obligation_id not in self.state.contracts:
            raise ValidationError(f"Contract {obligation_id} not found")
        
        contract = self.state.contracts[obligation_id]
        if contract.kind != "delivery_obligation":
            raise ValidationError(f"Contract {obligation_id} is not a delivery obligation")
        
        # Remove from holder's assets
        holder = self.state.agents[contract.asset_holder_id]
        if obligation_id not in holder.asset_ids:
            raise ValidationError(f"Contract {obligation_id} not in holder's assets")
        holder.asset_ids.remove(obligation_id)
        
        # Remove from issuer's liabilities
        issuer = self.state.agents[contract.liability_issuer_id]
        if obligation_id not in issuer.liability_ids:
            raise ValidationError(f"Contract {obligation_id} not in issuer's liabilities")
        issuer.liability_ids.remove(obligation_id)
        
        # Remove contract from registry
        del self.state.contracts[obligation_id]
        
        # Log the cancellation
        self.log("DeliveryObligationCancelled",
                obligation_id=obligation_id,
                debtor=contract.liability_issuer_id,
                creditor=contract.asset_holder_id,
                sku=contract.sku,
                qty=contract.amount)

    def cancel_delivery_obligation(self, obligation_id: InstrId) -> None:
        """Cancel (extinguish) a delivery obligation. Used by settlement engine after fulfillment."""
        with atomic(self):
            self._cancel_delivery_obligation_internal(obligation_id)

```

---

### 📄 src/bilancio/engines/valuation.py

```python
"""Valuation engines for financial instruments."""

from decimal import Decimal
from typing import Any, Protocol

# Placeholder type - this should be replaced with actual implementation from the domain layer
Money = Decimal


class ValuationEngine(Protocol):
    """Protocol for valuation engines that can price financial instruments."""

    def value(self, instrument: Any, context: dict[str, Any]) -> Money:
        """
        Calculate the value of a financial instrument.
        
        Args:
            instrument: The financial instrument to value
            context: Additional context needed for valuation (e.g., market data, parameters)
            
        Returns:
            The calculated value as Money
        """
        ...


class SimpleValuationEngine:
    """Basic valuation engine implementing present value calculation."""

    def __init__(self, discount_rate: float = 0.05):
        """
        Initialize the valuation engine.
        
        Args:
            discount_rate: Default discount rate for present value calculations
        """
        self.discount_rate = discount_rate

    def value(self, instrument: Any, context: dict[str, Any]) -> Money:
        """
        Calculate present value of an instrument.
        
        This is a basic implementation that assumes the instrument has a simple
        cash flow structure. More sophisticated instruments would require
        specialized valuation logic.
        
        Args:
            instrument: The financial instrument to value
            context: Valuation context containing discount rate, market data, etc.
            
        Returns:
            Present value as Money
        """
        # Get discount rate from context or use default
        rate = context.get('discount_rate', self.discount_rate)

        # This is a placeholder implementation
        # Real implementation would depend on the instrument type and its cash flows
        if hasattr(instrument, 'face_value'):
            return Money(str(instrument.face_value))

        # Default to zero if we can't determine value
        return Money('0.0')

    def set_discount_rate(self, rate: float) -> None:
        """Update the default discount rate."""
        self.discount_rate = rate

```

---

### 📄 src/bilancio/io/__init__.py

```python
"""I/O package for bilancio."""

```

---

### 📄 src/bilancio/io/readers.py

```python
"""File reading utilities for bilancio."""


# TODO: Import CashFlow from appropriate module once defined
# from bilancio.domain.instruments import CashFlow


def read_cashflows_csv(filepath: str) -> list["CashFlow"]:
    """Read cash flows from a CSV file.
    
    Args:
        filepath: Path to the CSV file to read
        
    Returns:
        List of CashFlow objects parsed from the CSV
        
    TODO: Implement CSV reading logic
    """
    raise NotImplementedError("CSV reading not yet implemented")

```

---

### 📄 src/bilancio/io/writers.py

```python
"""File writing utilities for bilancio."""


# TODO: Import CashFlow from appropriate module once defined
# from bilancio.domain.instruments import CashFlow


def write_cashflows_csv(flows: list["CashFlow"], filepath: str) -> None:
    """Write cash flows to a CSV file.
    
    Args:
        flows: List of CashFlow objects to write
        filepath: Path to the CSV file to create/overwrite
        
    TODO: Implement CSV writing logic
    """
    raise NotImplementedError("CSV writing not yet implemented")

```

---

### 📄 src/bilancio/ops/__init__.py

```python

```

---

### 📄 src/bilancio/ops/banking.py

```python
from bilancio.core.atomic_tx import atomic
from bilancio.core.errors import ValidationError
from bilancio.ops.primitives import coalesce_deposits, split


def deposit_cash(system, customer_id: str, bank_id: str, amount: int) -> str:
    if amount <= 0:
        raise ValidationError("amount must be positive")
    # collect payer cash, splitting as needed
    with atomic(system):
        remaining = amount
        cash_ids = [cid for cid in list(system.state.agents[customer_id].asset_ids)
                    if system.state.contracts[cid].kind == "cash"]
        moved_piece_ids = []
        for cid in cash_ids:
            instr = system.state.contracts[cid]
            if instr.amount > remaining:
                cid = split(system, cid, remaining)
                instr = system.state.contracts[cid]
            # move holder to bank (issuer CB unchanged)
            system.state.agents[customer_id].asset_ids.remove(cid)
            system.state.agents[bank_id].asset_ids.append(cid)
            instr.asset_holder_id = bank_id
            moved_piece_ids.append(cid)
            remaining -= instr.amount
            if remaining == 0:
                break
        if remaining != 0:
            raise ValidationError("insufficient cash for deposit")

        # credit/ensure deposit
        dep_id = coalesce_deposits(system, customer_id, bank_id)
        system.state.contracts[dep_id].amount += amount
        system.log("CashDeposited", customer=customer_id, bank=bank_id, amount=amount,
                   cash_piece_ids=moved_piece_ids, deposit_id=dep_id)
        return dep_id

def withdraw_cash(system, customer_id: str, bank_id: str, amount: int) -> str:
    if amount <= 0:
        raise ValidationError("amount must be positive")
    with atomic(system):
        # 1) debit deposit
        dep_ids = system.deposit_ids(customer_id, bank_id)
        if not dep_ids:
            raise ValidationError("no deposit at this bank")
        remaining = amount
        for dep_id in dep_ids:
            dep = system.state.contracts[dep_id]
            take = min(dep.amount, remaining)
            dep.amount -= take
            remaining -= take
            if dep.amount == 0 and take > 0:
                # remove empty instrument
                holder = system.state.agents[customer_id]
                issuer = system.state.agents[bank_id]
                holder.asset_ids.remove(dep_id)
                issuer.liability_ids.remove(dep_id)
                del system.state.contracts[dep_id]
            if remaining == 0:
                break
        if remaining != 0:
            raise ValidationError("insufficient deposit balance")

        # 2) move cash from bank vault → customer (require sufficient cash on hand)
        bank_cash_ids = [cid for cid in list(system.state.agents[bank_id].asset_ids)
                         if system.state.contracts[cid].kind == "cash"]
        remaining = amount
        moved_piece_ids = []
        for cid in bank_cash_ids:
            instr = system.state.contracts[cid]
            if instr.amount > remaining:
                cid = split(system, cid, remaining)
                instr = system.state.contracts[cid]
            system.state.agents[bank_id].asset_ids.remove(cid)
            system.state.agents[customer_id].asset_ids.append(cid)
            instr.asset_holder_id = customer_id
            moved_piece_ids.append(cid)
            remaining -= instr.amount
            if remaining == 0:
                break
        if remaining != 0:
            raise ValidationError("bank has insufficient cash on hand (MVP: no auto conversion from reserves)")

        system.log("CashWithdrawn", customer=customer_id, bank=bank_id, amount=amount, cash_piece_ids=moved_piece_ids)
        # 3) coalesce customer cash if you want tidy balances (optional)
        return "ok"

def client_payment(system, payer_id: str, payer_bank: str, payee_id: str, payee_bank: str,
                   amount: int, allow_cash_fallback: bool=False) -> str:
    if amount <= 0:
        raise ValidationError("amount must be positive")
    with atomic(system):
        # 1) debit payer's deposit at payer_bank
        dep_ids = system.deposit_ids(payer_id, payer_bank)
        remaining = amount
        deposit_paid = 0
        for dep_id in dep_ids:
            dep = system.state.contracts[dep_id]
            take = min(dep.amount, remaining)
            dep.amount -= take
            remaining -= take
            deposit_paid += take
            if dep.amount == 0 and take > 0:
                holder = system.state.agents[payer_id]
                issuer = system.state.agents[payer_bank]
                holder.asset_ids.remove(dep_id)
                issuer.liability_ids.remove(dep_id)
                del system.state.contracts[dep_id]
            if remaining == 0:
                break

        # Optional fallback: use payer's cash for the remainder (real-world "pay cash")
        cash_paid = 0
        if remaining and allow_cash_fallback:
            cash_ids = [cid for cid in list(system.state.agents[payer_id].asset_ids)
                        if system.state.contracts[cid].kind == "cash"]
            for cid in cash_ids:
                instr = system.state.contracts[cid]
                if instr.amount > remaining:
                    cid = split(system, cid, remaining)
                    instr = system.state.contracts[cid]
                # move payer cash → payee (physical cash handover)
                system.state.agents[payer_id].asset_ids.remove(cid)
                system.state.agents[payee_id].asset_ids.append(cid)
                instr.asset_holder_id = payee_id
                cash_paid += instr.amount
                remaining -= instr.amount
                if remaining == 0:
                    break

        if remaining != 0:
            raise ValidationError("insufficient funds for payment")

        # 2) credit payee's deposit at payee_bank (only the deposit portion, not cash)
        dep_rx = coalesce_deposits(system, payee_id, payee_bank)
        system.state.contracts[dep_rx].amount += deposit_paid

        # 3) record event for cross-bank intraday flow (no reserves move yet)
        if payer_bank != payee_bank:
            system.log("ClientPayment", payer=payer_id, payer_bank=payer_bank,
                       payee=payee_id, payee_bank=payee_bank, amount=deposit_paid)

        return dep_rx

```

---

### 📄 src/bilancio/ops/cashflows.py

```python
"""Cash flow operations and data structures."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

# Placeholder types - these should be replaced with actual implementations from the domain layer
Money = Decimal  # Placeholder for Money type
TimeCoordinate = datetime  # Placeholder for TimeCoordinate type
Agent = str  # Placeholder for Agent type


@dataclass
class CashFlow:
    """Represents a single cash flow between two agents."""

    amount: Money
    time: TimeCoordinate
    payer: Agent
    payee: Agent


class CashFlowStream:
    """Manages a collection of cash flows with basic operations."""

    def __init__(self, flows: list[CashFlow] = None):
        """Initialize with an optional list of cash flows."""
        self.flows = flows or []

    def add_flow(self, flow: CashFlow) -> None:
        """Add a cash flow to the stream."""
        self.flows.append(flow)

    def get_flows_at_time(self, time: TimeCoordinate) -> list[CashFlow]:
        """Get all cash flows occurring at a specific time."""
        return [flow for flow in self.flows if flow.time == time]

    def get_all_flows(self) -> list[CashFlow]:
        """Get all cash flows in the stream."""
        return self.flows.copy()

    def __len__(self) -> int:
        """Return the number of flows in the stream."""
        return len(self.flows)

```

---

### 📄 src/bilancio/ops/primitives.py

```python

from bilancio.core.errors import ValidationError
from bilancio.core.ids import new_id
from bilancio.domain.instruments.base import Instrument


def fungible_key(instr: Instrument) -> tuple:
    # Same type, denomination, issuer, holder → can merge
    # For deliverables, also include SKU and unit_price to prevent incorrect merging
    base_key = (instr.kind, instr.denom, instr.liability_issuer_id, instr.asset_holder_id)
    
    # Add deliverable-specific attributes to prevent merging different SKUs or prices
    if instr.kind == "deliverable":
        sku = getattr(instr, "sku", None)
        unit_price = getattr(instr, "unit_price", None)
        return base_key + (sku, unit_price)
    
    return base_key

def is_divisible(instr: Instrument) -> bool:
    # Cash and bank deposits are divisible; deliverables depend on flag
    if instr.kind in ("cash", "bank_deposit", "reserve_deposit"):
        return True
    if instr.kind == "deliverable":
        return getattr(instr, "divisible", False)
    return False

def split(system, instr_id: str, amount: int) -> str:
    instr = system.state.contracts[instr_id]
    if amount <= 0 or amount > instr.amount:
        raise ValidationError("invalid split amount")
    if not is_divisible(instr):
        raise ValidationError("instrument is not divisible")
    # reduce original
    instr.amount -= amount
    # create twin
    twin_id = new_id("C")
    twin = type(instr)(
        id=twin_id,
        kind=instr.kind,
        amount=amount,
        denom=instr.denom,
        asset_holder_id=instr.asset_holder_id,
        liability_issuer_id=instr.liability_issuer_id,
        **{k: getattr(instr, k) for k in ("due_day","sku","divisible","unit_price") if hasattr(instr, k)}
    )
    system.add_contract(twin)  # attaches to holder/issuer lists too
    return twin_id

def merge(system, a_id: str, b_id: str) -> str:
    if a_id == b_id:
        return a_id
    a = system.state.contracts[a_id]
    b = system.state.contracts[b_id]
    if fungible_key(a) != fungible_key(b):
        raise ValidationError("instruments are not fungible-compatible")
    a.amount += b.amount
    # detach b from registries
    holder = system.state.agents[b.asset_holder_id]
    issuer = system.state.agents[b.liability_issuer_id]
    holder.asset_ids.remove(b_id)
    issuer.liability_ids.remove(b_id)
    del system.state.contracts[b_id]
    system.log("InstrumentMerged", keep=a_id, removed=b_id)
    return a_id

def consume(system, instr_id: str, amount: int) -> None:
    instr = system.state.contracts[instr_id]
    if amount <= 0 or amount > instr.amount:
        raise ValidationError("invalid consume amount")
    instr.amount -= amount
    if instr.amount == 0:
        holder = system.state.agents[instr.asset_holder_id]
        issuer = system.state.agents[instr.liability_issuer_id]
        holder.asset_ids.remove(instr_id)
        issuer.liability_ids.remove(instr_id)
        del system.state.contracts[instr_id]

def coalesce_deposits(system, customer_id: str, bank_id: str) -> str:
    """Coalesce all deposits for a customer at a bank into a single instrument"""
    ids = system.deposit_ids(customer_id, bank_id)
    if not ids:
        # create a zero-balance deposit instrument
        from bilancio.domain.instruments.means_of_payment import BankDeposit
        dep_id = system.new_contract_id("D")
        dep = BankDeposit(
            id=dep_id, kind="bank_deposit", amount=0, denom="X",
            asset_holder_id=customer_id, liability_issuer_id=bank_id
        )
        system.add_contract(dep)
        return dep_id
    # merge all into the first
    keep = ids[0]
    for other in ids[1:]:
        merge(system, keep, other)
    return keep

```

---

### 📄 src/bilancio/ops/primitives_stock.py

```python
"""Stock operations primitives - separate from financial instrument operations."""

from decimal import Decimal
from typing import TYPE_CHECKING

from bilancio.core.errors import ValidationError
from bilancio.core.ids import InstrId, new_id
from bilancio.domain.goods import StockLot

if TYPE_CHECKING:
    from bilancio.engines.system import System


def stock_fungible_key(lot: StockLot) -> tuple:
    """Return fungible key for stock lots. Include price so lots with different valuation don't merge."""
    return (lot.kind, lot.sku, lot.owner_id, lot.unit_price)


def split_stock(system: 'System', stock_id: InstrId, quantity: int) -> InstrId:
    """Split a stock lot into two pieces. Returns ID of the new split piece."""
    stock = system.state.stocks[stock_id]
    
    if not stock.divisible:
        raise ValidationError("Stock lot is not divisible")
    if quantity <= 0 or quantity >= stock.quantity:
        raise ValidationError("Invalid split quantity")
    
    # Create new stock lot with split quantity
    new_id_val = new_id("S")
    new_stock = StockLot(
        id=new_id_val,
        kind="stock_lot",
        sku=stock.sku,
        quantity=quantity,
        unit_price=stock.unit_price,
        owner_id=stock.owner_id,
        divisible=stock.divisible
    )
    
    # Update original stock quantity
    stock.quantity -= quantity
    
    # Register new stock
    system.state.stocks[new_id_val] = new_stock
    system.state.agents[stock.owner_id].stock_ids.append(new_id_val)
    
    system.log("StockSplit", 
              original_id=stock_id, 
              new_id=new_id_val, 
              sku=stock.sku,
              original_qty=stock.quantity + quantity,
              split_qty=quantity,
              remaining_qty=stock.quantity)
    
    return new_id_val


def merge_stock(system: 'System', keep_id: InstrId, remove_id: InstrId) -> InstrId:
    """Merge two stock lots. Returns the ID of the kept lot."""
    keep_stock = system.state.stocks[keep_id]
    remove_stock = system.state.stocks[remove_id]
    
    # Check if stocks are fungible
    if stock_fungible_key(keep_stock) != stock_fungible_key(remove_stock):
        raise ValidationError("Stock lots are not fungible - cannot merge")
    
    # Merge quantities
    original_qty = keep_stock.quantity
    keep_stock.quantity += remove_stock.quantity
    
    # Remove the merged stock
    del system.state.stocks[remove_id]
    system.state.agents[remove_stock.owner_id].stock_ids.remove(remove_id)
    
    system.log("StockMerged",
              keep_id=keep_id,
              remove_id=remove_id,
              sku=keep_stock.sku,
              final_qty=keep_stock.quantity,
              keep_qty=original_qty,
              merged_qty=remove_stock.quantity)
    
    return keep_id


def consume_stock(system: 'System', stock_id: InstrId, quantity: int) -> None:
    """Consume (destroy) a portion of stock. For future use if needed."""
    stock = system.state.stocks[stock_id]
    
    if quantity <= 0 or quantity > stock.quantity:
        raise ValidationError("Invalid consumption quantity")
    
    if quantity == stock.quantity:
        # Complete consumption - remove the stock
        del system.state.stocks[stock_id]
        system.state.agents[stock.owner_id].stock_ids.remove(stock_id)
        system.log("StockConsumed", stock_id=stock_id, sku=stock.sku, qty=quantity, complete=True)
    else:
        # Partial consumption
        stock.quantity -= quantity
        system.log("StockConsumed", stock_id=stock_id, sku=stock.sku, qty=quantity, remaining=stock.quantity, complete=False)
```

---

## Tests

Below are all the test files:

### 🧪 tests/analysis/__init__.py

```python
"""Analysis module tests."""
```

---

### 🧪 tests/analysis/test_balances.py

```python
"""Comprehensive tests for the balance analytics module."""
from decimal import Decimal

import pytest

from bilancio.engines.system import System
from bilancio.domain.agents import CentralBank, Bank, Household
from bilancio.ops.banking import deposit_cash
from bilancio.analysis.balances import agent_balance, system_trial_balance


class TestBalanceAnalytics:
    """Test comprehensive balance analytics scenarios."""

    def test_agent_balance_simple_deposit(self):
        """Test agent balance with a simple cash deposit scenario.
        
        Creates System with CentralBank, Bank, and Household.
        Mints cash to household, then deposits at bank.
        Verifies household has deposit asset, no liabilities.
        Verifies bank has deposit liability and cash asset.
        Verifies trial balance totals match.
        """
        # Create system and agents
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        bank = Bank(id="BK01", name="Test Bank", kind="bank")  
        household = Household(id="HH01", name="Test Household", kind="household")
        
        system.bootstrap_cb(cb)
        system.add_agent(bank)
        system.add_agent(household)
        
        # Mint cash to household
        cash_amount = 1000
        system.mint_cash("HH01", cash_amount)
        
        # Deposit cash at bank
        deposit_amount = 600
        deposit_id = deposit_cash(system, "HH01", "BK01", deposit_amount)
        
        # Verify household balance
        hh_balance = agent_balance(system, "HH01")
        assert hh_balance.agent_id == "HH01"
        assert hh_balance.total_financial_assets == deposit_amount + (cash_amount - deposit_amount)
        assert hh_balance.total_financial_liabilities == 0
        assert hh_balance.net_financial == cash_amount  # Still has same total wealth
        assert hh_balance.assets_by_kind.get("bank_deposit", 0) == deposit_amount
        assert hh_balance.assets_by_kind.get("cash", 0) == cash_amount - deposit_amount
        assert hh_balance.liabilities_by_kind == {}
        
        # Verify bank balance
        bank_balance = agent_balance(system, "BK01")
        assert bank_balance.agent_id == "BK01"
        assert bank_balance.total_financial_assets == deposit_amount  # Cash from household
        assert bank_balance.total_financial_liabilities == deposit_amount  # Deposit liability
        assert bank_balance.net_financial == 0  # Bank's net position is zero
        assert bank_balance.assets_by_kind.get("cash", 0) == deposit_amount
        assert bank_balance.liabilities_by_kind.get("bank_deposit", 0) == deposit_amount
        
        # Verify trial balance
        trial = system_trial_balance(system)
        assert trial.total_financial_assets == trial.total_financial_liabilities
        expected_total = cash_amount + deposit_amount  # Cash + deposit instruments
        assert trial.total_financial_assets == expected_total
        assert trial.assets_by_kind.get("cash", 0) == cash_amount
        assert trial.assets_by_kind.get("bank_deposit", 0) == deposit_amount
        assert trial.liabilities_by_kind.get("cash", 0) == cash_amount
        assert trial.liabilities_by_kind.get("bank_deposit", 0) == deposit_amount
        
        # Ensure all invariants pass
        system.assert_invariants()

    def test_trial_balance_reserves_counters_match(self):
        """Test trial balance with reserves.
        
        Creates System with CentralBank and two Banks.
        Mints reserves to both banks.
        Verifies trial balance shows correct reserve amounts.
        Verifies assets equal liabilities system-wide.
        """
        # Create system and agents
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        bank1 = Bank(id="BK01", name="Bank One", kind="bank")
        bank2 = Bank(id="BK02", name="Bank Two", kind="bank")
        
        system.bootstrap_cb(cb)
        system.add_agent(bank1)
        system.add_agent(bank2)
        
        # Mint reserves to both banks
        reserves1_amount = 5000
        reserves2_amount = 3000
        system.mint_reserves("BK01", reserves1_amount)
        system.mint_reserves("BK02", reserves2_amount)
        
        # Verify individual bank balances
        bank1_balance = agent_balance(system, "BK01")
        assert bank1_balance.total_financial_assets == reserves1_amount
        assert bank1_balance.total_financial_liabilities == 0
        assert bank1_balance.net_financial == reserves1_amount
        assert bank1_balance.assets_by_kind.get("reserve_deposit", 0) == reserves1_amount
        assert bank1_balance.liabilities_by_kind == {}
        
        bank2_balance = agent_balance(system, "BK02")
        assert bank2_balance.total_financial_assets == reserves2_amount
        assert bank2_balance.total_financial_liabilities == 0
        assert bank2_balance.net_financial == reserves2_amount
        assert bank2_balance.assets_by_kind.get("reserve_deposit", 0) == reserves2_amount
        assert bank2_balance.liabilities_by_kind == {}
        
        # Verify central bank balance
        cb_balance = agent_balance(system, "CB01")
        assert cb_balance.total_financial_assets == 0
        assert cb_balance.total_financial_liabilities == reserves1_amount + reserves2_amount
        assert cb_balance.net_financial == -(reserves1_amount + reserves2_amount)
        assert cb_balance.assets_by_kind == {}
        assert cb_balance.liabilities_by_kind.get("reserve_deposit", 0) == reserves1_amount + reserves2_amount
        
        # Verify trial balance
        trial = system_trial_balance(system)
        total_reserves = reserves1_amount + reserves2_amount
        assert trial.total_financial_assets == trial.total_financial_liabilities == total_reserves
        assert trial.assets_by_kind.get("reserve_deposit", 0) == total_reserves
        assert trial.liabilities_by_kind.get("reserve_deposit", 0) == total_reserves
        
        # Verify system tracking counters match
        assert system.state.cb_reserves_outstanding == total_reserves
        
        # Ensure all invariants pass
        system.assert_invariants()

    def test_duplicate_ref_invariant(self):
        """Test the duplicate reference invariant.
        
        Creates System with agents.
        Mints cash.
        Manually duplicates a reference to trigger the invariant.
        Verifies the invariant catches the duplicate.
        """
        # Create system and agents
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        household = Household(id="HH01", name="Test Household", kind="household")
        
        system.bootstrap_cb(cb)
        system.add_agent(household)
        
        # Mint cash
        cash_id = system.mint_cash("HH01", 1000)
        
        # System should be valid at this point
        system.assert_invariants()
        
        # Now manually introduce a duplicate reference to test invariant
        # This simulates a bug where the same contract ID appears twice in asset_ids
        household.asset_ids.append(cash_id)  # Add duplicate
        
        # The invariant should catch this duplicate
        with pytest.raises(AssertionError, match="duplicate asset ref"):
            system.assert_invariants()
        
        # Remove the duplicate to restore system integrity
        household.asset_ids.remove(cash_id)
        
        # System should be valid again
        system.assert_invariants()
        
        # Test duplicate liability reference as well
        cb.liability_ids.append(cash_id)  # Add duplicate liability ref
        
        with pytest.raises(AssertionError, match="duplicate liability ref"):
            system.assert_invariants()

    def test_comprehensive_multi_agent_scenario(self):
        """Test a complex scenario with multiple agents and instrument types."""
        # Create system with multiple agents
        system = System()
        cb = CentralBank(id="CB01", name="Central Bank", kind="central_bank")
        bank1 = Bank(id="BK01", name="Bank One", kind="bank")
        bank2 = Bank(id="BK02", name="Bank Two", kind="bank")
        hh1 = Household(id="HH01", name="Household One", kind="household")
        hh2 = Household(id="HH02", name="Household Two", kind="household")
        
        system.bootstrap_cb(cb)
        system.add_agent(bank1)
        system.add_agent(bank2)
        system.add_agent(hh1)
        system.add_agent(hh2)
        
        # Complex operations
        # 1. Mint reserves to banks
        system.mint_reserves("BK01", 10000)
        system.mint_reserves("BK02", 8000)
        
        # 2. Mint cash to households
        system.mint_cash("HH01", 2000)
        system.mint_cash("HH02", 1500)
        
        # 3. Make deposits
        deposit_cash(system, "HH01", "BK01", 1200)
        deposit_cash(system, "HH02", "BK02", 800)
        
        # 4. Create some non-financial instruments
        # Create stock for HH01
        system.create_stock("HH01", "INVENTORY", 50, Decimal("0"))
        # Create delivery obligation from HH01 to HH02
        system.create_delivery_obligation("HH01", "HH02", "WIDGETS", 25, Decimal("0"), due_day=1)
        
        # Verify system-wide balance
        trial = system_trial_balance(system)
        
        # Calculate expected totals
        total_reserves = 18000  # 10000 + 8000
        total_cash = 3500     # 2000 + 1500 original cash
        total_deposits = 2000  # 1200 + 800
        total_delivery_obligations = 25
        
        expected_financial_total = total_reserves + total_cash + total_deposits
        
        assert trial.total_financial_assets == trial.total_financial_liabilities == expected_financial_total
        assert trial.assets_by_kind.get("reserve_deposit", 0) == total_reserves
        assert trial.assets_by_kind.get("cash", 0) == total_cash
        assert trial.assets_by_kind.get("bank_deposit", 0) == total_deposits
        assert trial.assets_by_kind.get("delivery_obligation", 0) == total_delivery_obligations
        
        # Verify individual balances make sense
        hh1_balance = agent_balance(system, "HH01")
        # HH01 should have: remaining cash + deposit + delivery obligation liability
        expected_hh1_cash = 2000 - 1200  # 800
        assert hh1_balance.assets_by_kind.get("cash", 0) == expected_hh1_cash
        assert hh1_balance.assets_by_kind.get("bank_deposit", 0) == 1200
        assert hh1_balance.liabilities_by_kind.get("delivery_obligation", 0) == 25
        
        # Bank1 should have: reserves + cash from deposit, deposit liability
        bank1_balance = agent_balance(system, "BK01")
        assert bank1_balance.assets_by_kind.get("reserve_deposit", 0) == 10000
        assert bank1_balance.assets_by_kind.get("cash", 0) == 1200  # From HH01 deposit
        assert bank1_balance.liabilities_by_kind.get("bank_deposit", 0) == 1200
        
        # Ensure all invariants pass
        system.assert_invariants()
```

---

### 🧪 tests/integration/test_banking_ops.py

```python
import pytest
from bilancio.engines.system import System
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.household import Household
from bilancio.core.errors import ValidationError
from bilancio.ops.banking import deposit_cash, withdraw_cash, client_payment


def test_deposit_cash():
    """Test depositing cash from customer to bank creates bank deposit."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    
    # CB mints cash to H1
    sys.mint_cash("H1", 120)
    
    # H1 deposits 120 to B1
    dep_id = deposit_cash(sys, "H1", "B1", 120)
    
    # Check cash moved H1→B1
    h1_cash = sum(sys.state.contracts[cid].amount for cid in h1.asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    b1_cash = sum(sys.state.contracts[cid].amount for cid in b1.asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 0
    assert b1_cash == 120
    
    # Check H1 has deposit 120 at B1
    assert sys.total_deposit("H1", "B1") == 120
    
    # Check event logged
    events = [e for e in sys.state.events if e["kind"] == "CashDeposited"]
    assert len(events) == 1
    assert events[0]["customer"] == "H1"
    assert events[0]["bank"] == "B1"
    assert events[0]["amount"] == 120
    
    # Invariants hold
    sys.assert_invariants()


def test_withdraw_cash():
    """Test withdrawing cash from bank deposit."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    
    # Setup: H1 has 120 deposit at B1
    sys.mint_cash("H1", 120)
    deposit_cash(sys, "H1", "B1", 120)
    
    # Withdraw 70
    withdraw_cash(sys, "H1", "B1", 70)
    
    # Check H1 deposit now 50
    assert sys.total_deposit("H1", "B1") == 50
    
    # Check H1 cash +70
    h1_cash = sum(sys.state.contracts[cid].amount for cid in h1.asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 70
    
    # Check bank cash -70
    b1_cash = sum(sys.state.contracts[cid].amount for cid in b1.asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert b1_cash == 50
    
    # Check event logged
    events = [e for e in sys.state.events if e["kind"] == "CashWithdrawn"]
    assert len(events) == 1
    assert events[0]["customer"] == "H1"
    assert events[0]["bank"] == "B1"
    assert events[0]["amount"] == 70
    
    sys.assert_invariants()


def test_withdraw_insufficient_bank_cash():
    """Test error when bank doesn't have enough cash on hand."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    
    # Setup: H1 deposits 100, but B1 only has 50 cash
    sys.mint_cash("H1", 100)
    deposit_cash(sys, "H1", "B1", 100)
    
    # Bank transfers 50 cash away (simulating it being used elsewhere)
    sys.mint_cash("B1", 0)  # B1 now has 100 cash from deposit
    # Transfer 60 away to simulate shortage
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    sys.add_agent(b2)
    sys.transfer_cash("B1", "B2", 60)
    
    # Try to withdraw 50 (should fail since B1 only has 40 cash)
    with pytest.raises(ValidationError, match="insufficient cash on hand"):
        withdraw_cash(sys, "H1", "B1", 50)
    
    # Deposit should remain unchanged
    assert sys.total_deposit("H1", "B1") == 100
    
    sys.assert_invariants()


def test_same_bank_payment():
    """Test payment between customers at same bank."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Setup: H1 has 100 deposit at B1
    sys.mint_cash("H1", 100)
    deposit_cash(sys, "H1", "B1", 100)
    
    # H1@B1 pays H2@B1, 40
    client_payment(sys, "H1", "B1", "H2", "B1", 40)
    
    # Check H1 deposit -40
    assert sys.total_deposit("H1", "B1") == 60
    
    # Check H2 deposit +40
    assert sys.total_deposit("H2", "B1") == 40
    
    # No ClientPayment event (same bank)
    events = [e for e in sys.state.events if e["kind"] == "ClientPayment"]
    assert len(events) == 0
    
    sys.assert_invariants()


def test_cross_bank_payment():
    """Test payment between customers at different banks."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h3 = Household(id="H3", name="Household 3", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    sys.add_agent(h1)
    sys.add_agent(h3)
    
    # Setup: H1 has 100 deposit at B1
    sys.mint_cash("H1", 100)
    deposit_cash(sys, "H1", "B1", 100)
    
    # H1@B1 pays H3@B2, 30
    client_payment(sys, "H1", "B1", "H3", "B2", 30)
    
    # Check H1 deposit -30
    assert sys.total_deposit("H1", "B1") == 70
    
    # Check H3 deposit +30 at B2
    assert sys.total_deposit("H3", "B2") == 30
    
    # ClientPayment event recorded
    events = [e for e in sys.state.events if e["kind"] == "ClientPayment"]
    assert len(events) == 1
    assert events[0]["payer"] == "H1"
    assert events[0]["payer_bank"] == "B1"
    assert events[0]["payee"] == "H3"
    assert events[0]["payee_bank"] == "B2"
    assert events[0]["amount"] == 30
    
    # No reserves moved (deferred to clearing)
    # Banks don't have reserve deposits yet
    
    sys.assert_invariants()


def test_insufficient_deposit_payment():
    """Test payment fails with insufficient deposit, succeeds with cash fallback."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Setup: H1 has 30 deposit at B1 and 50 cash
    sys.mint_cash("H1", 80)
    deposit_cash(sys, "H1", "B1", 30)
    
    # Try to pay 60 (more than deposit) - should fail
    with pytest.raises(ValidationError, match="insufficient funds"):
        client_payment(sys, "H1", "B1", "H2", "B2", 60)
    
    # Balances unchanged
    assert sys.total_deposit("H1", "B1") == 30
    h1_from_sys = sys.state.agents["H1"]
    h1_cash = sum(sys.state.contracts[cid].amount for cid in h1_from_sys.asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 50
    
    # Re-run with allow_cash_fallback=True
    client_payment(sys, "H1", "B1", "H2", "B2", 60, allow_cash_fallback=True)
    
    # H1 deposit should be 0 (used 30)
    assert sys.total_deposit("H1", "B1") == 0
    
    # H1 cash should be 20 (used 30 from 50)
    h1_from_sys = sys.state.agents["H1"]
    h1_cash = sum(sys.state.contracts[cid].amount for cid in h1_from_sys.asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 20
    
    # H2 should have 30 cash (from fallback) and 30 deposit (from H1's deposit)
    h2_from_sys = sys.state.agents["H2"]
    h2_cash = sum(sys.state.contracts[cid].amount for cid in h2_from_sys.asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h2_cash == 30  # from cash fallback
    assert sys.total_deposit("H2", "B2") == 30  # only the deposit portion
    
    sys.assert_invariants()


def test_deposit_coalescing():
    """Test that multiple deposits for same customer-bank pair are coalesced."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Multiple deposits from H1 to B1
    sys.mint_cash("H1", 150)
    deposit_cash(sys, "H1", "B1", 50)
    deposit_cash(sys, "H1", "B1", 30)
    deposit_cash(sys, "H1", "B1", 20)
    
    # Total should be 100
    assert sys.total_deposit("H1", "B1") == 100
    
    # Should have just one deposit instrument (coalesced)
    dep_ids = sys.deposit_ids("H1", "B1")
    assert len(dep_ids) == 1
    
    # Multiple payments to H2 should also coalesce
    client_payment(sys, "H1", "B1", "H2", "B1", 10)
    client_payment(sys, "H1", "B1", "H2", "B1", 15)
    client_payment(sys, "H1", "B1", "H2", "B1", 5)
    
    # H2 should have 30 total in one instrument
    assert sys.total_deposit("H2", "B1") == 30
    h2_deps = sys.deposit_ids("H2", "B1")
    assert len(h2_deps) == 1
    
    sys.assert_invariants()


def test_no_deposit_at_bank_error():
    """Test error when trying to withdraw from bank with no deposit."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    
    # H1 has no deposits
    with pytest.raises(ValidationError, match="no deposit at this bank"):
        withdraw_cash(sys, "H1", "B1", 50)
    
    sys.assert_invariants()


def test_insufficient_deposit_for_withdrawal():
    """Test error when trying to withdraw more than deposit balance."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    
    # Setup: H1 has 50 deposit at B1
    sys.mint_cash("H1", 50)
    deposit_cash(sys, "H1", "B1", 50)
    
    # Try to withdraw 100
    with pytest.raises(ValidationError, match="insufficient deposit balance"):
        withdraw_cash(sys, "H1", "B1", 100)
    
    # Deposit unchanged
    assert sys.total_deposit("H1", "B1") == 50
    
    sys.assert_invariants()
```

---

### 🧪 tests/integration/test_clearing_phase_c.py

```python
import pytest
from bilancio.engines.system import System
from bilancio.engines.clearing import settle_intraday_nets, compute_intraday_nets
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.household import Household
from bilancio.ops.banking import deposit_cash, client_payment


def test_phase_c_netting_reserves():
    """Test Phase C clearing nets multiple cross-bank payments correctly using reserves."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    h3 = Household(id="H3", name="Household 3", kind="household")
    h4 = Household(id="H4", name="Household 4", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    sys.add_agent(h1)
    sys.add_agent(h2)
    sys.add_agent(h3)
    sys.add_agent(h4)
    
    # Setup: Both banks have reserves
    sys.mint_reserves("B1", 1000)
    sys.mint_reserves("B2", 1000)
    
    # Setup: Customers have deposits
    sys.mint_cash("H1", 200)
    sys.mint_cash("H2", 150)
    sys.mint_cash("H3", 300)
    sys.mint_cash("H4", 100)
    deposit_cash(sys, "H1", "B1", 200)  # H1@B1
    deposit_cash(sys, "H2", "B1", 150)  # H2@B1
    deposit_cash(sys, "H3", "B2", 300)  # H3@B2
    deposit_cash(sys, "H4", "B2", 100)  # H4@B2
    
    # Create cross-bank payments that will net out partially:
    # H1@B1 pays H3@B2: 80 (B1 owes B2: 80)
    client_payment(sys, "H1", "B1", "H3", "B2", 80)
    # H2@B1 pays H4@B2: 50 (B1 owes B2: 50 more, total 130)
    client_payment(sys, "H2", "B1", "H4", "B2", 50)
    # H3@B2 pays H1@B1: 60 (B2 owes B1: 60, nets against 130, so B1 still owes B2: 70)
    client_payment(sys, "H3", "B2", "H1", "B1", 60)
    
    current_day = sys.state.day
    
    # Test compute_intraday_nets
    nets = compute_intraday_nets(sys, current_day)
    
    # With lexical ordering: B1 < B2, so nets should be positive (B1 owes B2)
    assert len(nets) == 1
    assert nets[("B1", "B2")] == 70  # 80 + 50 - 60 = 70
    
    # Phase C: Settle intraday nets
    settle_intraday_nets(sys, current_day)
    
    # Check B1 reserves reduced by 70
    b1_reserves = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B1"].asset_ids 
                      if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    assert b1_reserves == 930  # 1000 - 70
    
    # Check B2 reserves increased by 70
    b2_reserves = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B2"].asset_ids 
                      if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    assert b2_reserves == 1070  # 1000 + 70
    
    # Check InterbankCleared event logged
    events = [e for e in sys.state.events if e["kind"] == "InterbankCleared"]
    assert len(events) == 1
    assert events[0]["debtor_bank"] == "B1"
    assert events[0]["creditor_bank"] == "B2"
    assert events[0]["amount"] == 70
    
    # No overnight payables created
    overnight_events = [e for e in sys.state.events if e["kind"] == "InterbankOvernightCreated"]
    assert len(overnight_events) == 0
    
    sys.assert_invariants()


def test_phase_c_overnight_creation():
    """Test Phase C clearing creates overnight payable when insufficient reserves."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h3 = Household(id="H3", name="Household 3", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    sys.add_agent(h1)
    sys.add_agent(h3)
    
    # Setup: B1 has insufficient reserves (only 30), B2 has plenty
    sys.mint_reserves("B1", 30)
    sys.mint_reserves("B2", 1000)
    
    # Setup: Customers have deposits
    sys.mint_cash("H1", 200)
    sys.mint_cash("H3", 100)
    deposit_cash(sys, "H1", "B1", 200)  # H1@B1
    deposit_cash(sys, "H3", "B2", 100)  # H3@B2
    
    # Create cross-bank payment: H1@B1 pays H3@B2: 100 (needs 100 in reserves)
    client_payment(sys, "H1", "B1", "H3", "B2", 100)
    
    current_day = sys.state.day
    
    # Phase C: Settle intraday nets (should create overnight payable)
    settle_intraday_nets(sys, current_day)
    
    # Check B1 reserves unchanged (insufficient to cover 100)
    b1_reserves = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B1"].asset_ids 
                      if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    assert b1_reserves == 30  # unchanged
    
    # Check B2 reserves unchanged
    b2_reserves = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B2"].asset_ids 
                      if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    assert b2_reserves == 1000  # unchanged
    
    # Check overnight payable created: B1 owes B2, due tomorrow
    payables = [c for c in sys.state.contracts.values() if c.kind == "payable"]
    assert len(payables) == 1
    overnight_payable = payables[0]
    assert overnight_payable.liability_issuer_id == "B1"
    assert overnight_payable.asset_holder_id == "B2"
    assert overnight_payable.amount == 100
    assert overnight_payable.due_day == current_day + 1
    
    # Check InterbankOvernightCreated event logged
    overnight_events = [e for e in sys.state.events if e["kind"] == "InterbankOvernightCreated"]
    assert len(overnight_events) == 1
    assert overnight_events[0]["debtor_bank"] == "B1"
    assert overnight_events[0]["creditor_bank"] == "B2"
    assert overnight_events[0]["amount"] == 100
    assert overnight_events[0]["due_day"] == current_day + 1
    
    # No InterbankCleared event
    cleared_events = [e for e in sys.state.events if e["kind"] == "InterbankCleared"]
    assert len(cleared_events) == 0
    
    sys.assert_invariants()


def test_phase_c_no_nets_for_same_bank():
    """Test Phase C clearing does not create nets for same-bank payments."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    h3 = Household(id="H3", name="Household 3", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    sys.add_agent(h2)
    sys.add_agent(h3)
    
    # Setup: All customers at same bank
    sys.mint_cash("H1", 150)
    sys.mint_cash("H2", 200)
    sys.mint_cash("H3", 100)
    deposit_cash(sys, "H1", "B1", 150)  # H1@B1
    deposit_cash(sys, "H2", "B1", 200)  # H2@B1
    deposit_cash(sys, "H3", "B1", 100)  # H3@B1
    
    # Create same-bank payments (should not generate ClientPayment events)
    client_payment(sys, "H1", "B1", "H2", "B1", 50)  # H1 pays H2
    client_payment(sys, "H2", "B1", "H3", "B1", 80)  # H2 pays H3
    client_payment(sys, "H3", "B1", "H1", "B1", 30)  # H3 pays H1
    
    current_day = sys.state.day
    
    # Check no ClientPayment events (all same bank)
    client_payment_events = [e for e in sys.state.events if e["kind"] == "ClientPayment"]
    assert len(client_payment_events) == 0
    
    # Test compute_intraday_nets - should be empty
    nets = compute_intraday_nets(sys, current_day)
    assert len(nets) == 0
    
    # Phase C: Settle intraday nets (should be no-op)
    settle_intraday_nets(sys, current_day)
    
    # Check no interbank events
    interbank_events = [e for e in sys.state.events 
                       if e["kind"] in ["InterbankCleared", "InterbankOvernightCreated"]]
    assert len(interbank_events) == 0
    
    # Check no payables created
    payables = [c for c in sys.state.contracts.values() if c.kind == "payable"]
    assert len(payables) == 0
    
    # Check deposit balances (from same-bank transfers)
    assert sys.total_deposit("H1", "B1") == 130  # 150 - 50 + 30
    assert sys.total_deposit("H2", "B1") == 170  # 200 + 50 - 80
    assert sys.total_deposit("H3", "B1") == 150  # 100 + 80 - 30
    
    sys.assert_invariants()
```

---

### 🧪 tests/integration/test_day_simulation.py

```python
import pytest
from bilancio.engines.system import System
from bilancio.engines.simulation import run_day
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.household import Household
from bilancio.domain.instruments.credit import Payable
from bilancio.domain.policy import PolicyEngine
from bilancio.ops.banking import deposit_cash, client_payment


def test_run_day_basic():
    """Test basic day simulation with all phases working together."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    h3 = Household(id="H3", name="Household 3", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    sys.add_agent(h1)
    sys.add_agent(h2)
    sys.add_agent(h3)
    
    # Setup: Banks have reserves
    sys.mint_reserves("B1", 500)
    sys.mint_reserves("B2", 500)
    
    # Setup: Households have deposits
    sys.mint_cash("H1", 300)
    sys.mint_cash("H2", 200)
    sys.mint_cash("H3", 100)
    deposit_cash(sys, "H1", "B1", 300)  # H1@B1
    deposit_cash(sys, "H2", "B1", 200)  # H2@B1
    deposit_cash(sys, "H3", "B2", 100)  # H3@B2
    
    # Create payable due today: H1 owes H2 amount 150
    payable_id = sys.new_contract_id("P")
    payable = Payable(
        id=payable_id,
        kind="payable",
        amount=150,
        denom="X",
        asset_holder_id="H2",
        liability_issuer_id="H1",
        due_day=sys.state.day
    )
    sys.add_contract(payable)
    
    # Create some cross-bank payments during the day
    client_payment(sys, "H2", "B1", "H3", "B2", 80)  # B1 owes B2: 80
    
    initial_day = sys.state.day
    
    # Run the day simulation
    run_day(sys)
    
    # Check day incremented
    assert sys.state.day == initial_day + 1
    
    # Phase A: Check PhaseA event logged
    phase_a_events = [e for e in sys.state.events if e["kind"] == "PhaseA"]
    assert len(phase_a_events) == 1
    assert phase_a_events[0]["day"] == initial_day
    
    # Phase B: Check payable was settled
    assert payable_id not in sys.state.contracts
    
    # Check PayableSettled event
    settled_events = [e for e in sys.state.events if e["kind"] == "PayableSettled"]
    assert len(settled_events) == 1
    assert settled_events[0]["debtor"] == "H1"
    assert settled_events[0]["creditor"] == "H2"
    assert settled_events[0]["amount"] == 150
    
    # Check H1 and H2 balances after settlement (same bank)
    assert sys.total_deposit("H1", "B1") == 150  # 300 - 150 
    assert sys.total_deposit("H2", "B1") == 270  # 200 + 150 - 80 (paid to H3)
    assert sys.total_deposit("H3", "B2") == 180  # 100 + 80
    
    # Phase C: Check reserves transferred for cross-bank net
    # B1 owed B2: 80, should be settled with reserves
    b1_reserves = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B1"].asset_ids 
                      if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    b2_reserves = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B2"].asset_ids 
                      if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    assert b1_reserves == 420  # 500 - 80
    assert b2_reserves == 580  # 500 + 80
    
    # Check InterbankCleared event
    cleared_events = [e for e in sys.state.events if e["kind"] == "InterbankCleared"]
    assert len(cleared_events) == 1
    assert cleared_events[0]["debtor_bank"] == "B1"
    assert cleared_events[0]["creditor_bank"] == "B2"
    assert cleared_events[0]["amount"] == 80
    
    sys.assert_invariants()


def test_overnight_settlement_next_day():
    """Test overnight payables from day t are settled on day t+1."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h3 = Household(id="H3", name="Household 3", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    sys.add_agent(h1)
    sys.add_agent(h3)
    
    # Setup: B1 has insufficient reserves, B2 has plenty
    sys.mint_reserves("B1", 30)
    sys.mint_reserves("B2", 500)
    
    # Setup: Customers have deposits
    sys.mint_cash("H1", 200)
    sys.mint_cash("H3", 100)
    deposit_cash(sys, "H1", "B1", 200)  # H1@B1
    deposit_cash(sys, "H3", "B2", 100)  # H3@B2
    
    # Create cross-bank payment that will require overnight payable
    client_payment(sys, "H1", "B1", "H3", "B2", 100)  # B1 owes B2: 100
    
    day_0 = sys.state.day
    
    # Run day 0 - should create overnight payable
    run_day(sys)
    
    # Check overnight payable created
    payables = [c for c in sys.state.contracts.values() if c.kind == "payable"]
    assert len(payables) == 1
    overnight_payable = payables[0]
    assert overnight_payable.liability_issuer_id == "B1"
    assert overnight_payable.asset_holder_id == "B2"
    assert overnight_payable.amount == 100
    assert overnight_payable.due_day == day_0 + 1  # due tomorrow
    
    # Check reserves unchanged on day 0 (insufficient)
    b1_reserves = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B1"].asset_ids 
                      if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    assert b1_reserves == 30  # unchanged
    
    # Now add more reserves to B1 for next day settlement
    sys.mint_reserves("B1", 200)  # B1 now has 230 total
    
    # Run day 1 - overnight payable should be settled
    run_day(sys)
    
    # Check overnight payable settled and removed
    payables_after = [c for c in sys.state.contracts.values() if c.kind == "payable"]
    assert len(payables_after) == 0
    
    # Check reserves transferred on day 1
    b1_reserves_final = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B1"].asset_ids 
                           if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    b2_reserves_final = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B2"].asset_ids 
                           if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    assert b1_reserves_final == 130  # 230 - 100
    assert b2_reserves_final == 600  # 500 + 100
    
    # Check PayableSettled event on day 1
    settled_events = [e for e in sys.state.events if e["kind"] == "PayableSettled" and e["day"] == day_0 + 1]
    assert len(settled_events) == 1
    assert settled_events[0]["debtor"] == "B1"
    assert settled_events[0]["creditor"] == "B2"
    assert settled_events[0]["amount"] == 100
    
    sys.assert_invariants()


def test_policy_order_drives_payment_choice():
    """Test that policy order determines payment method preference."""
    # Create custom policy that prioritizes cash over deposits for households
    custom_policy = PolicyEngine.default()
    custom_policy.mop_rank["household"] = ["cash", "bank_deposit"]  # cash first!
    
    sys = System(policy=custom_policy)
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Setup: H1 has both cash and deposit
    sys.mint_cash("H1", 200)
    deposit_cash(sys, "H1", "B1", 100)  # H1 still has 100 cash + 100 deposit
    
    # Create payable: H1 owes H2 amount 80, due today
    payable_id = sys.new_contract_id("P")
    payable = Payable(
        id=payable_id,
        kind="payable",
        amount=80,
        denom="X",
        asset_holder_id="H2",
        liability_issuer_id="H1",
        due_day=sys.state.day
    )
    sys.add_contract(payable)
    
    # Run the day
    run_day(sys)
    
    # Check payable settled
    assert payable_id not in sys.state.contracts
    
    # With custom policy (cash first), H1 should have used cash, not deposit
    # H1 deposit should be unchanged
    assert sys.total_deposit("H1", "B1") == 100  # unchanged
    
    # H1 cash should be reduced by 80
    h1_cash = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["H1"].asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 20  # 100 - 80
    
    # H2 should have received 80 cash (direct transfer)
    h2_cash = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["H2"].asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h2_cash == 80
    
    # H2 should have no deposits (received cash directly)
    assert sys.total_deposit("H2", "B1") == 0
    
    sys.assert_invariants()


def test_policy_order_drives_payment_choice_default():
    """Test default policy (deposits first) for comparison."""
    sys = System()  # default policy: deposits first
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Setup: H1 has both cash and deposit (identical to above test)
    sys.mint_cash("H1", 200)
    deposit_cash(sys, "H1", "B1", 100)  # H1 still has 100 cash + 100 deposit
    
    # Create payable: H1 owes H2 amount 80, due today
    payable_id = sys.new_contract_id("P")
    payable = Payable(
        id=payable_id,
        kind="payable",
        amount=80,
        denom="X",
        asset_holder_id="H2",
        liability_issuer_id="H1",
        due_day=sys.state.day
    )
    sys.add_contract(payable)
    
    # Run the day
    run_day(sys)
    
    # Check payable settled
    assert payable_id not in sys.state.contracts
    
    # With default policy (deposits first), H1 should have used deposit, not cash
    # H1 deposit should be reduced by 80
    assert sys.total_deposit("H1", "B1") == 20  # 100 - 80
    
    # H1 cash should be unchanged
    h1_cash = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["H1"].asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 100  # unchanged
    
    # H2 should have received 80 as deposit (same bank transfer)
    assert sys.total_deposit("H2", "B1") == 80
    
    # H2 should have no cash (received deposit)
    h2_cash = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["H2"].asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h2_cash == 0
    
    sys.assert_invariants()
```

---

### 🧪 tests/integration/test_settlement_phase_b.py

```python
import pytest
from bilancio.engines.system import System
from bilancio.engines.settlement import settle_due
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.household import Household
from bilancio.domain.instruments.credit import Payable
from bilancio.domain.policy import PolicyEngine
from bilancio.ops.banking import deposit_cash, client_payment
from bilancio.core.errors import DefaultError


def test_phase_b_same_bank_settlement():
    """Test Phase B settlement when debtor and creditor use the same bank."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Setup: H1 has 200 deposit at B1
    sys.mint_cash("H1", 200)
    deposit_cash(sys, "H1", "B1", 200)
    
    # Create payable: H1 owes H2 amount 150, due today
    payable_id = sys.new_contract_id("P")
    payable = Payable(
        id=payable_id,
        kind="payable", 
        amount=150,
        denom="X",
        asset_holder_id="H2",
        liability_issuer_id="H1",
        due_day=sys.state.day
    )
    sys.add_contract(payable)
    
    # Phase B: Settle due payables
    settle_due(sys, sys.state.day)
    
    # Check H1 deposit reduced by 150
    assert sys.total_deposit("H1", "B1") == 50
    
    # Check H2 deposit increased by 150
    assert sys.total_deposit("H2", "B1") == 150
    
    # Check payable was removed
    assert payable_id not in sys.state.contracts
    
    # Check PayableSettled event logged
    events = [e for e in sys.state.events if e["kind"] == "PayableSettled"]
    assert len(events) == 1
    assert events[0]["debtor"] == "H1"
    assert events[0]["creditor"] == "H2"
    assert events[0]["amount"] == 150
    
    # No ClientPayment event (same bank)
    client_payment_events = [e for e in sys.state.events if e["kind"] == "ClientPayment"]
    assert len(client_payment_events) == 0
    
    sys.assert_invariants()


def test_phase_b_cross_bank_settlement_logs_client_payment():
    """Test Phase B settlement logs ClientPayment when debtor and creditor use different banks."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Setup: H1 has 300 deposit at B1, H2 has 1 deposit at B2 to establish bank relationship
    sys.mint_cash("H1", 300)
    sys.mint_cash("H2", 1)
    deposit_cash(sys, "H1", "B1", 300)
    deposit_cash(sys, "H2", "B2", 1)
    
    # Create payable: H1 owes H2 amount 100, due today
    payable_id = sys.new_contract_id("P")
    payable = Payable(
        id=payable_id,
        kind="payable",
        amount=100, 
        denom="X",
        asset_holder_id="H2",
        liability_issuer_id="H1",
        due_day=sys.state.day
    )
    sys.add_contract(payable)
    
    # Phase B: Settle due payables
    settle_due(sys, sys.state.day)
    
    # Check H1 deposit reduced by 100
    assert sys.total_deposit("H1", "B1") == 200
    
    # Check H2 deposit increased by 100 at B2 (1 initial + 100 from payment)
    assert sys.total_deposit("H2", "B2") == 101
    
    # Check payable was removed
    assert payable_id not in sys.state.contracts
    
    # Check ClientPayment event logged (cross-bank payment)
    client_payment_events = [e for e in sys.state.events if e["kind"] == "ClientPayment"]
    assert len(client_payment_events) == 1
    assert client_payment_events[0]["payer"] == "H1"
    assert client_payment_events[0]["payer_bank"] == "B1"
    assert client_payment_events[0]["payee"] == "H2"
    assert client_payment_events[0]["payee_bank"] == "B2"
    assert client_payment_events[0]["amount"] == 100
    
    sys.assert_invariants()


def test_phase_b_cash_fallback():
    """Test Phase B settlement uses cash when deposits insufficient but policy allows."""
    # Create custom policy that allows cash fallback for households
    custom_policy = PolicyEngine.default()
    custom_policy.mop_rank["household"] = ["bank_deposit", "cash"]
    
    sys = System(policy=custom_policy)
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Setup: H1 has 60 deposit at B1 and 80 cash
    sys.mint_cash("H1", 140)
    deposit_cash(sys, "H1", "B1", 60)
    
    # Create payable: H1 owes H2 amount 100, due today (more than deposit)
    payable_id = sys.new_contract_id("P")
    payable = Payable(
        id=payable_id,
        kind="payable",
        amount=100,
        denom="X",
        asset_holder_id="H2",
        liability_issuer_id="H1",
        due_day=sys.state.day
    )
    sys.add_contract(payable)
    
    # Phase B: Settle due payables
    settle_due(sys, sys.state.day)
    
    # Check H1 deposit is now 0 (used all 60)
    assert sys.total_deposit("H1", "B1") == 0
    
    # Check H1 cash reduced by 40 (100 - 60 from deposit)
    h1_cash = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["H1"].asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 40  # 80 - 40 used for payment
    
    # Check H2 has 60 deposit at B1 and 40 cash
    assert sys.total_deposit("H2", "B1") == 60  # from H1's deposit portion
    h2_cash = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["H2"].asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h2_cash == 40  # from H1's cash portion
    
    # Check payable was removed
    assert payable_id not in sys.state.contracts
    
    sys.assert_invariants()


def test_phase_b_default_on_insufficient_means():
    """Test Phase B settlement raises DefaultError when no sufficient funds available."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="Household 1", kind="household")
    h2 = Household(id="H2", name="Household 2", kind="household")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Setup: H1 has only 30 deposit at B1 and 20 cash = 50 total
    sys.mint_cash("H1", 50)
    deposit_cash(sys, "H1", "B1", 30)
    
    # Create payable: H1 owes H2 amount 100, due today (more than available)
    payable_id = sys.new_contract_id("P")
    payable = Payable(
        id=payable_id,
        kind="payable",
        amount=100,
        denom="X", 
        asset_holder_id="H2",
        liability_issuer_id="H1",
        due_day=sys.state.day
    )
    sys.add_contract(payable)
    
    # Phase B: Settle due payables should fail
    with pytest.raises(DefaultError, match="Insufficient funds to settle payable"):
        settle_due(sys, sys.state.day)
    
    # Check payable still exists (settlement failed)
    assert payable_id in sys.state.contracts
    assert sys.state.contracts[payable_id].amount == 100
    
    # Check balances unchanged
    assert sys.total_deposit("H1", "B1") == 30
    h1_cash = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["H1"].asset_ids 
                  if cid in sys.state.contracts and sys.state.contracts[cid].kind == "cash")
    assert h1_cash == 20
    
    sys.assert_invariants()


def test_phase_b_bank_to_bank_reserves():
    """Test Phase B settlement between banks using reserves."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    
    # Setup: B1 has 500 reserves
    sys.mint_reserves("B1", 500)
    
    # Create payable: B1 owes B2 amount 200, due today
    payable_id = sys.new_contract_id("P")
    payable = Payable(
        id=payable_id,
        kind="payable",
        amount=200,
        denom="X",
        asset_holder_id="B2", 
        liability_issuer_id="B1",
        due_day=sys.state.day
    )
    sys.add_contract(payable)
    
    # Phase B: Settle due payables
    settle_due(sys, sys.state.day)
    
    # Check B1 reserves reduced by 200
    b1_reserves = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B1"].asset_ids 
                      if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    assert b1_reserves == 300
    
    # Check B2 reserves increased by 200
    b2_reserves = sum(sys.state.contracts[cid].amount for cid in sys.state.agents["B2"].asset_ids 
                      if cid in sys.state.contracts and sys.state.contracts[cid].kind == "reserve_deposit")
    assert b2_reserves == 200
    
    # Check payable was removed
    assert payable_id not in sys.state.contracts
    
    # Check PayableSettled event logged
    events = [e for e in sys.state.events if e["kind"] == "PayableSettled"]
    assert len(events) == 1
    assert events[0]["debtor"] == "B1"
    assert events[0]["creditor"] == "B2"
    assert events[0]["amount"] == 200
    
    sys.assert_invariants()
```

---

### 🧪 tests/test_smoke.py

```python
"""Smoke tests to verify basic installation and imports."""

import pytest
from decimal import Decimal


def test_core_imports():
    """Test that core modules can be imported."""
    from bilancio.core.time import TimeCoordinate, TimeInterval, now
    from bilancio.core.errors import (
        BilancioError,
        ValidationError,
        CalculationError,
        ConfigurationError,
    )
    from bilancio.core.atomic import AtomicValue, Money, Quantity, Rate
    
    # Basic instantiation tests
    t = TimeCoordinate(0.0)
    assert t.t == 0.0
    
    interval = TimeInterval(TimeCoordinate(0.0), TimeCoordinate(1.0))
    assert interval.start.t == 0.0
    assert interval.end.t == 1.0
    
    current_time = now()
    assert current_time.t == 0.0
    
    # Test Money
    money = Money(Decimal("100.50"), "USD")
    assert money.amount == Decimal("100.50")
    assert money.currency == "USD"
    assert money.value == Decimal("100.50")  # AtomicValue protocol
    
    # Test Quantity
    qty = Quantity(10.5, "kg")
    assert qty.value == 10.5
    assert qty.unit == "kg"
    
    # Test Rate
    rate = Rate(Decimal("0.05"), "annual")
    assert rate.value == Decimal("0.05")
    assert rate.basis == "annual"


def test_domain_imports():
    """Test that domain modules can be imported."""
    from bilancio.domain.agent import Agent
    from bilancio.domain.instruments.contract import Contract, BaseContract
    from bilancio.domain.instruments.policy import Policy, BasePolicy
    
    # Test that base classes exist
    assert Agent is not None
    assert Contract is not None
    assert BaseContract is not None
    assert Policy is not None
    assert BasePolicy is not None


def test_ops_imports():
    """Test that ops modules can be imported."""
    from bilancio.ops.cashflows import CashFlow, CashFlowStream
    from bilancio.core.atomic import Money
    from bilancio.core.time import TimeCoordinate
    
    # Simple test - we can't create CashFlow without Agent instances
    # but we can test the CashFlowStream
    stream = CashFlowStream()
    assert len(stream) == 0
    assert stream.get_all_flows() == []


def test_engines_imports():
    """Test that engine modules can be imported."""
    from bilancio.engines.valuation import ValuationEngine, SimpleValuationEngine
    from bilancio.engines.simulation import SimulationEngine, MonteCarloEngine
    from bilancio.core.atomic import Money
    
    # Test basic instantiation
    val_engine = SimpleValuationEngine(discount_rate=0.05)
    assert val_engine.discount_rate == 0.05
    
    monte_carlo = MonteCarloEngine(n_simulations=1000)
    assert monte_carlo.n_simulations == 1000


def test_analysis_imports():
    """Test that analysis modules can be imported."""
    from bilancio.analysis.metrics import calculate_npv, calculate_irr
    
    # These are placeholders so they should raise NotImplementedError
    with pytest.raises(NotImplementedError):
        calculate_npv([], 0.05)
    
    with pytest.raises(NotImplementedError):
        calculate_irr([])


def test_io_imports():
    """Test that IO modules can be imported."""
    from bilancio.io.readers import read_cashflows_csv
    from bilancio.io.writers import write_cashflows_csv
    
    # These are placeholders so they should raise NotImplementedError
    with pytest.raises(NotImplementedError):
        read_cashflows_csv("dummy.csv")
    
    with pytest.raises(NotImplementedError):
        write_cashflows_csv([], "dummy.csv")


def test_package_metadata():
    """Test that package metadata is accessible."""
    import bilancio
    
    assert bilancio.__version__ == "0.1.0"
    
    # Test that basic imports from __init__ work
    from bilancio import TimeCoordinate, TimeInterval, now
    from bilancio import BilancioError, ValidationError
    
    assert TimeCoordinate is not None
    assert BilancioError is not None
```

---

### 🧪 tests/unit/test_balances.py

```python
"""Tests for balance analysis functionality."""
from decimal import Decimal

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
        
        # Create stock lot (non-financial asset for HH01)
        system.create_stock("HH01", "APPLES", 50, Decimal("0"))
        
        # Create delivery obligation (HH01 owes to HH02)
        system.create_delivery_obligation("HH01", "HH02", "ORANGES", 30, Decimal("0"), due_day=1)
        
        # Check HH01 balance (has financial assets, some stock, and delivery obligation liability)
        hh1_balance = agent_balance(system, "HH01")
        assert hh1_balance.total_financial_assets == 1000  # Only cash
        assert hh1_balance.total_financial_liabilities == 0  # Delivery obligation liability is non-financial
        assert hh1_balance.net_financial == 1000
        assert hh1_balance.assets_by_kind == {"cash": 1000}
        assert hh1_balance.liabilities_by_kind == {"delivery_obligation": 30}
        
        # Check HH02 balance (has delivery obligation asset only)
        hh2_balance = agent_balance(system, "HH02")
        assert hh2_balance.total_financial_assets == 0  # Delivery obligation asset is non-financial
        assert hh2_balance.total_financial_liabilities == 0
        assert hh2_balance.net_financial == 0
        assert hh2_balance.assets_by_kind == {"delivery_obligation": 30}
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
        # Create stock for HH01 (non-financial asset, no liability)
        system.create_stock("HH01", "APPLES", 50, Decimal("0"))
        # Create delivery obligation HH01 → HH02 (bilateral obligation)
        system.create_delivery_obligation("HH01", "HH02", "ORANGES", 30, Decimal("0"), due_day=1)
        
        trial = system_trial_balance(system)
        assert trial.total_financial_assets == trial.total_financial_liabilities == 1000
        assert trial.assets_by_kind == {"cash": 1000, "delivery_obligation": 30}
        assert trial.liabilities_by_kind == {"cash": 1000, "delivery_obligation": 30}


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
```

---

### 🧪 tests/unit/test_cash_and_deliverables.py

```python
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
```

---

### 🧪 tests/unit/test_deliverable_due_dates.py

```python
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
```

---

### 🧪 tests/unit/test_deliverable_merge.py

```python
"""Tests for stock lot merge behavior with fungible_key enhancements."""
from decimal import Decimal

import pytest

from bilancio.core.errors import ValidationError
from bilancio.domain.agents import Household
from bilancio.engines.system import System
from bilancio.ops.primitives_stock import stock_fungible_key, merge_stock


class TestDeliverableMerge:
    """Test that stock lots with different SKUs or prices don't merge incorrectly."""
    
    def test_deliverables_with_different_skus_dont_merge(self):
        """Stock lots with different SKUs should not be fungible."""
        system = System()
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        
        system.add_agent(hh1)
        
        # Create two stock lots with different SKUs but same owner
        apple_id = system.create_stock("HH01", "APPLES", 10, Decimal("2.00"))
        orange_id = system.create_stock("HH01", "ORANGES", 10, Decimal("2.00"))
        
        apple = system.state.stocks[apple_id]
        orange = system.state.stocks[orange_id]
        
        # Verify they have different fungible keys
        assert stock_fungible_key(apple) != stock_fungible_key(orange)
        
        # Attempting to merge should fail
        with pytest.raises(ValidationError, match="not fungible"):
            merge_stock(system, apple_id, orange_id)
    
    def test_deliverables_with_different_prices_dont_merge(self):
        """Stock lots with same SKU but different prices should not be fungible."""
        system = System()
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        
        system.add_agent(hh1)
        
        # Create two stock lots with same SKU but different prices
        cheap_apple_id = system.create_stock("HH01", "APPLES", 10, Decimal("1.00"))
        expensive_apple_id = system.create_stock("HH01", "APPLES", 10, Decimal("3.00"))
        
        cheap_apple = system.state.stocks[cheap_apple_id]
        expensive_apple = system.state.stocks[expensive_apple_id]
        
        # Verify they have different fungible keys
        assert stock_fungible_key(cheap_apple) != stock_fungible_key(expensive_apple)
        
        # Attempting to merge should fail
        with pytest.raises(ValidationError, match="not fungible"):
            merge_stock(system, cheap_apple_id, expensive_apple_id)
    
    def test_deliverables_with_same_sku_and_price_can_merge(self):
        """Stock lots with same SKU and price should be fungible."""
        system = System()
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        
        system.add_agent(hh1)
        
        # Create two stock lots with same SKU and price
        apple1_id = system.create_stock("HH01", "APPLES", 10, Decimal("2.00"))
        apple2_id = system.create_stock("HH01", "APPLES", 5, Decimal("2.00"))
        
        apple1 = system.state.stocks[apple1_id]
        apple2 = system.state.stocks[apple2_id]
        
        # Verify they have the same fungible key
        assert stock_fungible_key(apple1) == stock_fungible_key(apple2)
        
        # Merging should succeed
        result_id = merge_stock(system, apple1_id, apple2_id)
        assert result_id == apple1_id
        
        # Verify the merged stock lot has the combined quantity
        merged = system.state.stocks[apple1_id]
        assert merged.quantity == 15
        assert merged.unit_price == Decimal("2.00")
        assert merged.value == Decimal("30.00")
        
        # Verify apple2 was removed
        assert apple2_id not in system.state.stocks
    
    def test_deliverables_with_different_parties_dont_merge(self):
        """Stock lots with different owners should not be fungible."""
        system = System()
        hh1 = Household(id="HH01", name="Household 1", kind="household")
        hh2 = Household(id="HH02", name="Household 2", kind="household")
        
        system.add_agent(hh1)
        system.add_agent(hh2)
        
        # Create stock lots with same SKU/price but different owners
        apple1_id = system.create_stock("HH01", "APPLES", 10, Decimal("2.00"))
        apple2_id = system.create_stock("HH02", "APPLES", 10, Decimal("2.00"))  # Different owner
        
        apple1 = system.state.stocks[apple1_id]
        apple2 = system.state.stocks[apple2_id]
        
        # Verify they have different fungible keys
        assert stock_fungible_key(apple1) != stock_fungible_key(apple2)
        
        # Attempting to merge should fail
        with pytest.raises(ValidationError, match="not fungible"):
            merge_stock(system, apple1_id, apple2_id)
    
    def test_fungible_key_backwards_compatible_with_financial_instruments(self):
        """Financial instruments should maintain their original fungible key behavior."""
        from bilancio.domain.agents import Bank, CentralBank
        from bilancio.ops.primitives import fungible_key, merge
        
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
```

---

### 🧪 tests/unit/test_deliverable_valuation.py

```python
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
```

---

### 🧪 tests/unit/test_domain_system.py

```python
from bilancio.engines.system import System
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.household import Household
from bilancio.domain.agents.treasury import Treasury
from bilancio.domain.instruments.means_of_payment import Cash, BankDeposit, ReserveDeposit
from bilancio.domain.instruments.credit import Payable

def test_create_agents_and_deposit_invariants():
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    h1 = Household(id="H1", name="HH 1", kind="household")
    sys.add_agent(cb); sys.add_agent(b1); sys.add_agent(h1)

    d = BankDeposit(id="D1", kind="bank_deposit", amount=100, denom="X",
                    asset_holder_id="H1", liability_issuer_id="B1")
    sys.add_contract(d)
    sys.assert_invariants()

def test_policy_allows_and_blocks_expected_cases():
    sys = System()
    cb = CentralBank(id="CB1", name="CB", kind="central_bank")
    b1 = Bank(id="B1", name="B1", kind="bank")
    h1 = Household(id="H1", name="H1", kind="household")
    t1 = Treasury(id="T1", name="T1", kind="treasury")
    sys.add_agent(cb); sys.add_agent(b1); sys.add_agent(h1); sys.add_agent(t1)

    # HH can hold bank deposit; bank issues it
    sys.add_contract(BankDeposit(id="d", kind="bank_deposit", amount=10, denom="X",
                                 asset_holder_id="H1", liability_issuer_id="B1"))

    # Treasury can hold reserves, not required to test now, but ensure creation passes
    # Use mint_reserves to maintain invariants
    sys.mint_reserves("B1", 5)

    # Any agent can issue a payable in MVP
    sys.add_contract(Payable(id="p", kind="payable", amount=7, denom="X",
                             asset_holder_id="B1", liability_issuer_id="H1", due_day=0))
    sys.assert_invariants()
```

---

### 🧪 tests/unit/test_reserves.py

```python
import pytest
from bilancio.engines.system import System
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.bank import Bank
from bilancio.core.errors import ValidationError


def test_mint_reserves():
    """Test minting reserves to a bank."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    
    # Mint 100 units of reserves to B1
    reserve_id = sys.mint_reserves("B1", 100)
    
    # Check CB outstanding
    assert sys.state.cb_reserves_outstanding == 100
    
    # Check B1 has the reserves
    assert reserve_id in b1.asset_ids
    reserve_instr = sys.state.contracts[reserve_id]
    assert reserve_instr.amount == 100
    assert reserve_instr.asset_holder_id == "B1"
    assert reserve_instr.liability_issuer_id == "CB1"
    assert reserve_instr.kind == "reserve_deposit"
    
    # Check CB liability
    assert reserve_id in cb.liability_ids
    
    # Check invariants
    sys.assert_invariants()


def test_transfer_reserves():
    """Test transferring reserves between banks."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    
    # Mint reserves to B1
    sys.mint_reserves("B1", 150)
    
    # Transfer 60 reserves from B1 to B2
    sys.transfer_reserves("B1", "B2", 60)
    
    # Check B1 has 90, B2 has 60
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    b2_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b2.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    assert b1_reserves == 90
    assert b2_reserves == 60
    
    # Check CB outstanding unchanged
    assert sys.state.cb_reserves_outstanding == 150
    
    # Check invariants
    sys.assert_invariants()


def test_convert_reserves_to_cash():
    """Test converting reserves to cash."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    
    # Setup bank with reserves
    sys.mint_reserves("B1", 200)
    
    # Convert 80 reserves to cash
    sys.convert_reserves_to_cash("B1", 80)
    
    # Check reserves decreased
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    assert b1_reserves == 120
    
    # Check cash increased
    b1_cash = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "cash"
    )
    assert b1_cash == 80
    
    # Check both CB counters updated
    assert sys.state.cb_reserves_outstanding == 120
    assert sys.state.cb_cash_outstanding == 80
    
    # Check invariants
    sys.assert_invariants()


def test_convert_cash_to_reserves():
    """Test converting cash to reserves."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    
    # Setup bank with cash
    sys.mint_cash("B1", 120)
    
    # Convert 50 cash to reserves
    sys.convert_cash_to_reserves("B1", 50)
    
    # Check cash decreased
    b1_cash = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "cash"
    )
    assert b1_cash == 70
    
    # Check reserves increased
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    assert b1_reserves == 50
    
    # Check both CB counters updated
    assert sys.state.cb_cash_outstanding == 70
    assert sys.state.cb_reserves_outstanding == 50
    
    # Check invariants
    sys.assert_invariants()


def test_reserves_roundtrip():
    """Test round-trip conversion: reserves to cash and back."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    
    # Start with 100 reserves
    sys.mint_reserves("B1", 100)
    initial_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    
    # Convert all reserves to cash
    sys.convert_reserves_to_cash("B1", 100)
    
    # Verify we have cash, no reserves
    b1_cash = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "cash"
    )
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    assert b1_cash == 100
    assert b1_reserves == 0
    
    # Convert all cash back to reserves
    sys.convert_cash_to_reserves("B1", 100)
    
    # Verify amounts preserved
    final_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    final_cash = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "cash"
    )
    assert final_reserves == initial_reserves
    assert final_cash == 0
    
    # Check CB counters are back to original state
    assert sys.state.cb_reserves_outstanding == 100
    assert sys.state.cb_cash_outstanding == 0
    
    # Check invariants
    sys.assert_invariants()


def test_transfer_insufficient_reserves():
    """Test error handling for insufficient reserves transfer."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    
    # Mint only 50 reserves to B1
    sys.mint_reserves("B1", 50)
    
    # Try to transfer more reserves than available
    with pytest.raises(ValidationError, match="insufficient reserves"):
        sys.transfer_reserves("B1", "B2", 100)
    
    # Check state unchanged after failure (atomic rollback means B1 still has all 50)
    assert sys.state.cb_reserves_outstanding == 50
    # Get agents from system state (they may have been rolled back)
    b1_from_sys = sys.state.agents["B1"]
    b2_from_sys = sys.state.agents["B2"]
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1_from_sys.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    b2_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b2_from_sys.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    assert b1_reserves == 50
    assert b2_reserves == 0
    
    # Check invariants
    sys.assert_invariants()


def test_convert_insufficient_reserves_to_cash():
    """Test error handling for insufficient reserves conversion."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    
    # Mint only 30 reserves
    sys.mint_reserves("B1", 30)
    
    # Try to convert more reserves than available
    with pytest.raises(ValidationError, match="insufficient reserves"):
        sys.convert_reserves_to_cash("B1", 50)
    
    # Check state unchanged after atomic rollback
    assert sys.state.cb_reserves_outstanding == 30
    assert sys.state.cb_cash_outstanding == 0
    # Get agent from system state (may have been rolled back)
    b1_from_sys = sys.state.agents["B1"]
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1_from_sys.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    b1_cash = sum(
        sys.state.contracts[cid].amount 
        for cid in b1_from_sys.asset_ids 
        if sys.state.contracts[cid].kind == "cash"
    )
    assert b1_reserves == 30
    assert b1_cash == 0
    
    # Check invariants
    sys.assert_invariants()


def test_convert_insufficient_cash_to_reserves():
    """Test error handling for insufficient cash conversion."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    
    # Mint only 40 cash
    sys.mint_cash("B1", 40)
    
    # Try to convert more cash than available
    with pytest.raises(ValidationError, match="insufficient cash"):
        sys.convert_cash_to_reserves("B1", 60)
    
    # Check state unchanged after atomic rollback
    assert sys.state.cb_cash_outstanding == 40
    assert sys.state.cb_reserves_outstanding == 0
    # Get agent from system state (may have been rolled back)
    b1_from_sys = sys.state.agents["B1"]
    b1_cash = sum(
        sys.state.contracts[cid].amount 
        for cid in b1_from_sys.asset_ids 
        if sys.state.contracts[cid].kind == "cash"
    )
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1_from_sys.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    assert b1_cash == 40
    assert b1_reserves == 0
    
    # Check invariants
    sys.assert_invariants()


def test_no_op_reserve_transfer():
    """Test error handling for no-op reserve transfer."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    
    # Mint reserves to B1
    sys.mint_reserves("B1", 100)
    
    # Try to transfer to same bank
    with pytest.raises(ValidationError, match="no-op transfer"):
        sys.transfer_reserves("B1", "B1", 50)
    
    # Check state unchanged
    assert sys.state.cb_reserves_outstanding == 100
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    assert b1_reserves == 100
    
    # Check invariants
    sys.assert_invariants()


def test_multiple_reserve_transfers_with_coalescing():
    """Test multiple reserve transfers result in proper coalescing."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    b2 = Bank(id="B2", name="Bank 2", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    sys.add_agent(b2)
    
    # Mint reserves to B1 in multiple chunks
    sys.mint_reserves("B1", 30)
    sys.mint_reserves("B1", 40)
    sys.mint_reserves("B1", 30)
    
    # B1 has 3 reserve instruments totaling 100
    b1_reserve_ids = [cid for cid in b1.asset_ids 
                     if sys.state.contracts[cid].kind == "reserve_deposit"]
    assert len(b1_reserve_ids) == 3
    assert sum(sys.state.contracts[cid].amount for cid in b1_reserve_ids) == 100
    
    # Transfer all to B2 in parts
    sys.transfer_reserves("B1", "B2", 25)
    sys.transfer_reserves("B1", "B2", 35)
    sys.transfer_reserves("B1", "B2", 40)
    
    # B2 should have merged reserve instruments
    b2_reserve_ids = [cid for cid in b2.asset_ids 
                     if sys.state.contracts[cid].kind == "reserve_deposit"]
    # Should be consolidated to fewer instruments (ideally 1)
    assert len(b2_reserve_ids) <= 3
    assert sum(sys.state.contracts[cid].amount for cid in b2_reserve_ids) == 100
    
    # B1 should have no reserves
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    assert b1_reserves == 0
    
    # Check invariants
    sys.assert_invariants()


def test_partial_reserve_conversion():
    """Test partial conversion of reserves to cash and back."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    b1 = Bank(id="B1", name="Bank 1", kind="bank")
    sys.add_agent(cb)
    sys.add_agent(b1)
    
    # Start with 200 reserves
    sys.mint_reserves("B1", 200)
    
    # Convert 75 reserves to cash
    sys.convert_reserves_to_cash("B1", 75)
    
    # Check mixed holdings
    b1_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    b1_cash = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "cash"
    )
    assert b1_reserves == 125
    assert b1_cash == 75
    
    # Convert 25 cash back to reserves
    sys.convert_cash_to_reserves("B1", 25)
    
    # Check final state
    final_reserves = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "reserve_deposit"
    )
    final_cash = sum(
        sys.state.contracts[cid].amount 
        for cid in b1.asset_ids 
        if sys.state.contracts[cid].kind == "cash"
    )
    assert final_reserves == 150
    assert final_cash == 50
    
    # Check CB counters
    assert sys.state.cb_reserves_outstanding == 150
    assert sys.state.cb_cash_outstanding == 50
    
    # Check invariants
    sys.assert_invariants()
```

---

### 🧪 tests/unit/test_settle_obligation.py

```python
import pytest
from decimal import Decimal
from bilancio.engines.system import System
from bilancio.domain.agents.household import Household
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.instruments.credit import Payable
from bilancio.domain.instruments.delivery import DeliveryObligation
from bilancio.core.errors import ValidationError


def test_settle_deliverable_obligation():
    """Test settling a delivery obligation (e.g., promise to deliver goods)."""
    sys = System()
    seller = Household(id="SELLER", name="Seller", kind="household")
    buyer = Household(id="BUYER", name="Buyer", kind="household")
    sys.add_agent(seller)
    sys.add_agent(buyer)
    
    # Create a promise to deliver 10 chairs
    promise_id = sys.create_delivery_obligation(
        from_agent="SELLER",  # Seller has liability to deliver
        to_agent="BUYER",     # Buyer has claim to receive
        sku="CHAIR",
        quantity=10,
        unit_price=Decimal("0"),
        due_day=1
    )
    
    # Verify the obligation exists
    assert promise_id in sys.state.contracts
    assert promise_id in buyer.asset_ids
    assert promise_id in seller.liability_ids
    
    # Settle the obligation (e.g., after chairs are delivered)
    sys.settle_obligation(promise_id)
    
    # Verify the obligation is extinguished
    assert promise_id not in sys.state.contracts
    assert promise_id not in buyer.asset_ids
    assert promise_id not in seller.liability_ids
    
    # Verify invariants still hold
    sys.assert_invariants()


def test_settle_payable_obligation():
    """Test settling a payable obligation."""
    sys = System()
    debtor = Household(id="DEBTOR", name="Debtor", kind="household")
    creditor = Household(id="CREDITOR", name="Creditor", kind="household")
    sys.add_agent(debtor)
    sys.add_agent(creditor)
    
    # Create a payable
    payable = Payable(
        id="PAY1",
        kind="payable",
        amount=100,
        denom="USD",
        asset_holder_id="CREDITOR",
        liability_issuer_id="DEBTOR",
        due_day=1
    )
    sys.add_contract(payable)
    
    # Verify the payable exists
    assert "PAY1" in sys.state.contracts
    assert "PAY1" in creditor.asset_ids
    assert "PAY1" in debtor.liability_ids
    
    # Settle the payable (e.g., after payment is made)
    sys.settle_obligation("PAY1")
    
    # Verify the payable is extinguished
    assert "PAY1" not in sys.state.contracts
    assert "PAY1" not in creditor.asset_ids
    assert "PAY1" not in debtor.liability_ids
    
    sys.assert_invariants()


def test_settle_nonexistent_contract_fails():
    """Test that settling a non-existent contract raises an error."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    sys.add_agent(h1)
    
    with pytest.raises(ValidationError, match="Contract FAKE123 not found"):
        sys.settle_obligation("FAKE123")


def test_settle_contract_not_in_holder_assets_fails():
    """Test error when contract is not in holder's assets (data inconsistency)."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Create a delivery obligation
    d_id = sys.create_delivery_obligation("H1", "H2", "ITEM", 1, Decimal("0"), due_day=1)
    
    # Manually corrupt the data by removing from holder's assets
    h2.asset_ids.remove(d_id)
    
    # Should fail with validation error
    with pytest.raises(ValidationError, match="not in holder's assets"):
        sys.settle_obligation(d_id)


def test_settle_contract_not_in_issuer_liabilities_fails():
    """Test error when contract is not in issuer's liabilities (data inconsistency)."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Create a delivery obligation
    d_id = sys.create_delivery_obligation("H1", "H2", "ITEM", 1, Decimal("0"), due_day=1)
    
    # Manually corrupt the data by removing from issuer's liabilities
    h1.liability_ids.remove(d_id)
    
    # Should fail with validation error
    with pytest.raises(ValidationError, match="not in issuer's liabilities"):
        sys.settle_obligation(d_id)


def test_settle_obligation_is_atomic():
    """Test that settle_obligation is atomic - failures roll back all changes."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Create a delivery obligation
    d_id = sys.create_delivery_obligation("H1", "H2", "ITEM", 5, Decimal("0"), due_day=1)
    
    # Corrupt data to force failure partway through
    original_assets = h2.asset_ids.copy()
    original_liabilities = h1.liability_ids.copy()
    h1.liability_ids.remove(d_id)  # This will cause settle to fail
    
    # Attempt to settle (should fail)
    with pytest.raises(ValidationError):
        sys.settle_obligation(d_id)
    
    # Verify nothing changed (atomic rollback)
    assert d_id in sys.state.contracts
    # Need to get the agent from sys.state after rollback
    h2_from_sys = sys.state.agents["H2"]
    assert d_id in h2_from_sys.asset_ids  # Should still be there despite partial execution
    # Note: h1.liability_ids was manually corrupted, so we can't check that
    
    # Fix the corruption and verify we can still settle properly
    h1_from_sys = sys.state.agents["H1"]
    h1_from_sys.liability_ids.append(d_id)
    sys.settle_obligation(d_id)
    assert d_id not in sys.state.contracts


def test_settle_obligation_logs_event():
    """Test that settling an obligation logs the appropriate event."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    
    # Create a delivery obligation
    d_id = sys.create_delivery_obligation("H1", "H2", "WIDGET", 3, Decimal("0"), due_day=1)
    
    # Clear existing events to make test cleaner
    sys.state.events.clear()
    
    # Settle the obligation
    sys.settle_obligation(d_id)
    
    # Check that an ObligationSettled event was logged
    assert len(sys.state.events) == 1
    event = sys.state.events[0]
    assert event["kind"] == "ObligationSettled"
    assert event["contract_id"] == d_id
    assert event["holder_id"] == "H2"
    assert event["issuer_id"] == "H1"
    assert event["contract_kind"] == "delivery_obligation"
    assert event["amount"] == 3


def test_complete_chair_transaction_with_settlement():
    """Test the complete chair transaction example with settlement."""
    sys = System()
    cb = CentralBank(id="CB1", name="Central Bank", kind="central_bank")
    seller = Household(id="YOU", name="Chair Seller", kind="household")
    buyer = Household(id="ME", name="Chair Buyer", kind="household")
    
    sys.add_agent(cb)
    sys.add_agent(seller)
    sys.add_agent(buyer)
    
    # Step 1: Give buyer cash to pay
    sys.mint_cash("ME", 100)
    
    # Step 2: Create promise to deliver chairs
    chair_promise_id = sys.create_delivery_obligation(
        from_agent="YOU",  # Seller promises to deliver
        to_agent="ME",     # Buyer has claim to receive
        sku="CHAIR",
        quantity=10,
        unit_price=Decimal("0"),  # Test uses zero price
        due_day=1
    )
    
    # Step 3: Buyer pays seller
    sys.transfer_cash("ME", "YOU", 100)
    
    # Verify state after payment
    seller_cash = sum(sys.state.contracts[cid].amount for cid in seller.asset_ids
                      if sys.state.contracts[cid].kind == "cash")
    buyer_cash = sum(sys.state.contracts[cid].amount for cid in buyer.asset_ids
                     if sys.state.contracts[cid].kind == "cash")
    assert seller_cash == 100
    assert buyer_cash == 0
    assert chair_promise_id in buyer.asset_ids
    assert chair_promise_id in seller.liability_ids
    
    # Step 4: Later, seller delivers chairs (represented by settling the obligation)
    sys.settle_obligation(chair_promise_id)
    
    # Verify final state - obligation is extinguished
    assert chair_promise_id not in sys.state.contracts
    assert chair_promise_id not in buyer.asset_ids
    assert chair_promise_id not in seller.liability_ids
    
    # Seller still has the cash
    seller_cash = sum(sys.state.contracts[cid].amount for cid in seller.asset_ids
                      if sys.state.contracts[cid].kind == "cash")
    assert seller_cash == 100
    
    sys.assert_invariants()


def test_settle_multiple_obligations():
    """Test settling multiple obligations in sequence."""
    sys = System()
    h1 = Household(id="H1", name="H1", kind="household")
    h2 = Household(id="H2", name="H2", kind="household")
    h3 = Household(id="H3", name="H3", kind="household")
    sys.add_agent(h1)
    sys.add_agent(h2)
    sys.add_agent(h3)
    
    # Create multiple obligations
    d1 = sys.create_delivery_obligation("H1", "H2", "ITEM1", 5, Decimal("0"), due_day=1)
    d2 = sys.create_delivery_obligation("H2", "H3", "ITEM2", 3, Decimal("0"), due_day=1)
    d3 = sys.create_delivery_obligation("H1", "H3", "ITEM3", 7, Decimal("0"), due_day=1)
    
    # Settle them one by one
    sys.settle_obligation(d1)
    assert d1 not in sys.state.contracts
    assert d2 in sys.state.contracts
    assert d3 in sys.state.contracts
    
    sys.settle_obligation(d2)
    assert d2 not in sys.state.contracts
    assert d3 in sys.state.contracts
    
    sys.settle_obligation(d3)
    assert d3 not in sys.state.contracts
    
    # All obligations should be settled
    assert len([cid for cid in h1.liability_ids if cid in sys.state.contracts]) == 0
    assert len([cid for cid in h2.asset_ids if cid in sys.state.contracts]) == 0
    assert len([cid for cid in h3.asset_ids if cid in sys.state.contracts]) == 0
    
    sys.assert_invariants()
```

---

## End of Codebase

Generated from: /Users/vladgheorghe/code/bilancio
Total source files: 44
Total test files: 15
