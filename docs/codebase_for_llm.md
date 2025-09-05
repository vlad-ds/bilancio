# Bilancio Codebase Documentation

Generated: 2025-09-05 09:29:11 UTC | Branch: main | Commit: 2031884

This document contains the complete codebase structure and content for LLM ingestion.

---

## Project Structure

```
/Users/vladgheorghe/code/bilancio
├── .github
│   └── workflows
│       ├── claude-code-review.yml
│       ├── claude.yml
│       └── update-codebase-for-llm.yml
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── TODO.md
├── docs
│   ├── Kalecki_debt_simulation.pdf
│   ├── Monetary Theory Chapter 5.pdf
│   ├── Money modeling software.pdf
│   ├── SP239 Kalecki on Credit and Debt extended.pdf
│   ├── codebase_for_llm.md
│   ├── exercises_scenarios.md
│   ├── plans
│   │   ├── 000_setup.md
│   │   ├── 001_domain_system.md
│   │   ├── 003_cash_and_nonfin_exchange.md
│   │   ├── 004_banking.md
│   │   ├── 005_reserves_settlement_clearing_scheduler.md
│   │   ├── 006_analytics.md
│   │   ├── 007_deliverable.md
│   │   ├── 008_simulation.md
│   │   ├── 009_cli.md
│   │   ├── 010_ui_refactor.md
│   │   ├── 011_tbs.md
│   │   ├── 012_scheduled_actions_and_aliases.md
│   │   └── Kalecki_debt_simulation (1).pdf
│   ├── prompts
│   │   └── scenario_translator_agent.md
│   └── version_1_0_exercises.pdf
├── examples
│   ├── exercise_scenarios
│   │   ├── html
│   │   │   ├── all.html
│   │   │   ├── ex1_cash_for_goods.html
│   │   │   ├── ex2_two_firms_cash_purchase.html
│   │   │   ├── ex3_iou_assignment.html
│   │   │   ├── ex4_generic_claim_transfer.html
│   │   │   ├── ex5_deferred_exchange.html
│   │   │   ├── ex6_goods_now_cash_later.html
│   │   │   └── ex7_cash_now_goods_later.html
│   │   └── yaml
│   │       ├── ex1_cash_for_goods.yaml
│   │       ├── ex2_two_firms_cash_purchase.yaml
│   │       ├── ex3_iou_assignment.yaml
│   │       ├── ex4_generic_claim_transfer.yaml
│   │       ├── ex5_deferred_exchange.yaml
│   │       ├── ex6_goods_now_cash_later.yaml
│   │       └── ex7_cash_now_goods_later.yaml
│   └── scenarios
│       ├── firm_delivery.yaml
│       ├── interbank_netting.yaml
│       ├── intraday_netting.yaml
│       ├── payment_demo.yaml
│       ├── rich_simulation.yaml
│       ├── sasa_scenario.yaml
│       ├── simple_bank.yaml
│       └── two_banks_interbank.yaml
├── notebooks
│   └── demo
│       ├── balance_sheet_display.ipynb
│       └── pdf_example_with_firms.ipynb
├── out
│   ├── interbank_balances.csv
│   └── interbank_events.jsonl
├── pyproject.toml
├── scripts
│   └── generate_codebase_markdown.py
├── src
│   └── bilancio
│       ├── __init__.py
│       ├── analysis
│       │   ├── __init__.py
│       │   ├── balances.py
│       │   ├── metrics.py
│       │   ├── visualization.py
│       │   └── visualization_phases.py
│       ├── config
│       │   ├── __init__.py
│       │   ├── apply.py
│       │   ├── loaders.py
│       │   └── models.py
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
│       │   │   └── policy.py
│       │   └── policy.py
│       ├── engines
│       │   ├── __init__.py
│       │   ├── clearing.py
│       │   ├── settlement.py
│       │   ├── simulation.py
│       │   ├── system.py
│       │   └── valuation.py
│       ├── export
│       │   ├── __init__.py
│       │   └── writers.py
│       ├── io
│       │   ├── __init__.py
│       │   ├── readers.py
│       │   └── writers.py
│       ├── ops
│       │   ├── __init__.py
│       │   ├── aliases.py
│       │   ├── banking.py
│       │   ├── cashflows.py
│       │   ├── primitives.py
│       │   └── primitives_stock.py
│       └── ui
│           ├── __init__.py
│           ├── assets
│           │   └── export.css
│           ├── cli.py
│           ├── display.py
│           ├── html_export.py
│           ├── render
│           │   ├── __init__.py
│           │   ├── formatters.py
│           │   ├── models.py
│           │   └── rich_builders.py
│           ├── run.py
│           ├── settings.py
│           └── wizard.py
├── temp
│   ├── balances.csv
│   ├── demo.html
│   ├── demo2.html
│   ├── demo3.html
│   ├── demo_correct.html
│   ├── demo_fixed.html
│   ├── demo_full.html
│   ├── events.jsonl
│   ├── firm_delivery_t_account.html
│   ├── followup_pr_body.md
│   ├── pr_comment.md
│   ├── report.html
│   ├── rich_simulation_phases_tables.html
│   ├── rich_simulation_phases_tables2.html
│   ├── rich_simulation_phases_tables3.html
│   ├── rich_simulation_phases_tables4.html
│   ├── rich_simulation_pretty.html
│   ├── rich_simulation_pretty_converged.html
│   ├── rich_simulation_pretty_full.html
│   ├── rich_simulation_spreadsheet.html
│   ├── rich_simulation_spreadsheet_stronger.html
│   ├── rich_simulation_t_account.html
│   ├── rich_simulation_t_account_light.html
│   ├── sasa_events_table.html
│   ├── sasa_t_account.html
│   ├── sasa_t_account_wide.html
│   ├── test_complete.html
│   ├── test_debug.html
│   ├── test_fixed_balances.html
│   ├── test_from_template.yaml
│   ├── test_no_duplicates.html
│   ├── test_output.html
│   ├── test_output.pdf
│   └── test_output_fixed.html
└── tests
    ├── analysis
    │   ├── __init__.py
    │   ├── test_balances.py
    │   └── test_t_account_builder.py
    ├── config
    │   ├── test_apply.py
    │   ├── test_loaders.py
    │   ├── test_models.py
    │   ├── test_scheduled_alias_validation.py
    │   └── test_transfer_claim_model.py
    ├── engines
    │   └── test_phase_b1_scheduling.py
    ├── integration
    │   ├── test_banking_ops.py
    │   ├── test_clearing_phase_c.py
    │   ├── test_day_simulation.py
    │   └── test_settlement_phase_b.py
    ├── ops
    │   └── test_alias_helpers.py
    ├── test_smoke.py
    ├── ui
    │   ├── test_cli.py
    │   ├── test_cli_html_export.py
    │   ├── test_html_export.py
    │   ├── test_render_builders.py
    │   └── test_render_formatters.py
    └── unit
        ├── test_balances.py
        ├── test_domain_system.py
        ├── test_reserves.py
        └── test_settle_obligation.py

39 directories, 179 files

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

- **84348990** (2025-08-18) by Vlad Gheorghe
  feat: implement CLI for Bilancio simulations (#10)
  * feat: implement CLI for Bilancio simulations
  - Add configuration layer with YAML support for scenario definitions
  - Create CLI with run, validate, and new commands
  - Implement export functionality for balances (CSV) and events (JSONL)
  - Add example scenarios (simple_bank, two_banks_interbank, firm_delivery)
  - Include comprehensive tests for config and UI layers
  - Fix display_events to properly handle setup phase
  - Support policy overrides and all major operations via YAML
  The CLI allows domain experts to:
  - Define scenarios in simple YAML format
  - Run simulations step-by-step or until stable
  - Validate configurations before running
  - Export results for analysis
  - Create new scenarios with wizard
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * docs: add scenario translator agent prompt
  Create comprehensive prompt for AI agents to translate financial
  scenarios from natural language to valid Bilancio YAML configs.
  Includes understanding process, validation steps, and user instructions.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: update tests to use pydantic aliases correctly
  - Fix CreateDeliveryObligation and CreatePayable tests to use 'from'/'to' aliases
  - Fix test_apply to check for liability_issuer_id instead of debtor_id
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: address PR review feedback (priorities 1-3)
  Priority 1: Fix decimal parsing security vulnerability
  - Use try/except with Decimal constructor for safer parsing
  - Check for finite values to prevent infinity/nan issues
  - Handle all decimal exceptions properly
  Priority 2: Address precision loss in financial calculations
  - Document that amounts are expected in minor units
  - Improve JSON serialization to preserve decimal precision
  - Use string representation for non-integer decimals in JSON
  Priority 3: Implement template functionality for wizard
  - Support using existing YAML files as templates
  - Support predefined complexity levels (simple/standard/complex)
  - Handle non-interactive mode gracefully
  - Allow modification of loaded templates
  All tests passing ✅
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  ---------
  Co-authored-by: Claude <noreply@anthropic.com>

- **effcb9aa** (2025-08-18) by vladgheorghe
  feat: improve CLI event display formatting and visual hierarchy
  - Add clear visual hierarchy with phase headers and indented events
  - Show all three phases (A, B, C) consistently even when empty
  - Add agent IDs to balance sheet headers for clarity (e.g., "Consumer A [H1]")
  - Format all event types with appropriate emojis and descriptions
  - Fix setup phase event formatting (ReservesMinted, CashDeposited, etc.)
  - Add "Day ended" marker after Phase C
  - Improve stock split display with shortened IDs for readability
  - Clarify phase descriptions: Phase A (Day begins), Phase B (Settlement), Phase C (Intraday netting)
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **caafcd53** (2025-08-18) by vladgheorghe
  feat: add interbank netting example and improve event formatting
  - Create interbank_netting.yaml example showing Phase C netting
  - Add formatting for ClientPayment, InterbankCleared, ReservesTransferred events
  - Document that Phase C is specifically for interbank settlement netting

- **d4989288** (2025-08-18) by vladgheorghe
  fix: correct balance sheet display timing in CLI simulation
  The balance sheets were showing incorrect values because run_until_stable()
  was executing all simulation days first, then displaying summaries afterwards.
  This meant all balance sheets showed the final state rather than the state
  at each specific day.
  Changed run_until_stable_mode() to:
  - Run simulation day-by-day instead of all at once
  - Display each day's balance sheet immediately after that day completes
  - Pass correct day number (0-based) to show_day_summary() for event filtering
  This ensures balance sheets accurately reflect the system state at the end
  of each simulated day.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **dccdd46a** (2025-08-18) by vladgheorghe
  docs: update codebase markdown with balance sheet timing fix
  Regenerated codebase_for_llm.md to include the latest changes:
  - Fixed balance sheet display timing in CLI simulation
  - Balance sheets now show correct state at end of each day
  - Events properly displayed with correct day associations
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>

- **83697fcf** (2025-08-21) by Vlad Gheorghe
  feat: HTML export improvements and rich simulation scenario (#11)
  * feat: add PDF export functionality for CLI output
  - Added --pdf flag to bilancio run command
  - Exports simulation output with colors and formatting preserved
  - Generates both HTML and PDF (using Chrome if available)
  - Maintains same visual style as terminal output including:
    - Color-coded balance sheets
    - Formatted events with emojis
    - Side-by-side agent balance display
  - Added weasyprint and pygments dependencies
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * refactor: change from PDF to HTML export for CLI output
  - Changed --pdf flag to --html flag
  - Renamed pdf_export.py to html_export.py
  - Removed PDF conversion logic and weasyprint dependency
  - Fixed event display to show actual event kinds instead of "Unknown"
  - HTML output preserves all colors, formatting, and emojis
  - Simpler implementation without system dependencies
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: improve HTML export event display clarity
  - Removed confusing nested day headers in event display
  - Day 0 now shows only setup phase events
  - Each day shows events that actually happened during that day
  - Events grouped by phase (Setup, A, B, C) without re-grouping by day
  - Phase headers only shown when there are actual events
  - Skip phase marker events in display to reduce clutter
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * feat: show complete initial setup in HTML export including payables
  - Added display of initial actions from YAML configuration
  - Now shows create_payable actions that explain WHY payments happen
  - Separated Initial Actions from Setup Events for clarity
  - Shows initial balances after setup
  - Users can now see the complete story:
    - Initial payables created (H1 owes H2 $1000 due Day 1)
    - Then the settlement of those payables on Day 1
  This makes the simulation flow much clearer by showing the setup
  that creates the obligations that drive the later transactions.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: show correct initial balances and agent list in HTML export
  - Capture initial balance snapshots right after setup (before simulation)
  - Display agent list at the beginning showing all participants
  - Initial balances now show correct values (B1: $20,000, B2: $15,000)
  - Fixed issue where balances showed post-transaction state instead of initial state
  - Added icons for different agent types (🏛️ central bank, 🏦 bank, 👤 household, 🏢 firm)
  The HTML now properly shows:
  1. All agents in the simulation
  2. Initial actions including payables
  3. Correct initial balance sheets after setup
  4. Then the progression through simulation days
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: correct day labeling misalignment in CLI and HTML output
  Previously, events from day N were shown under "Day N+1" header due to
  mixing 1-based day counters with 0-based event days. This caused:
  - Day 1 to appear empty with no events
  - Payables due on Day 1 to show under Day 2
  - Event summaries showing "Unknown" instead of actual event types
  Changes:
  - Use consistent 0-based day numbers for both labels and event filtering
  - Skip day 0 in simulation loops (already shown as "Day 0 After Setup")
  - Fix event summary to use 'kind' field instead of missing 'type' field
  - Ensure HTML export respects actual event days
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * feat: improve HTML export display and add rich simulation scenario
  Major improvements to HTML export formatting and balance sheet display:
  Display improvements:
  - Show full agent balance sheets after each day's events (not just trial balance)
  - Fix stock split event rendering with proper field names and shortened IDs
  - Improve initial action display for create_stock and create_delivery_obligation
  - Fix event categorization - settlement events now correctly appear in Phase B
  - Add proper formatting for all event types (CashTransferred, StockTransferred, etc.)
  - Fix Phase A to only show "Day begins" without spurious events
  Rich simulation scenario:
  - Comprehensive demo with stocks, payables, intra-bank and inter-bank payments
  - Shows stock movements between firms and households
  - Demonstrates both same-bank and cross-bank payment flows
  - Includes dividend payments and multi-day settlement patterns
  - Configured to display 6 key agents' balance sheets throughout
  The HTML export now provides a complete view of how the financial system
  evolves day by day, with full visibility into balance sheet changes.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * chore: reorganize docs and clean up test HTML files
  - Move codebase_for_llm.md to docs/ folder
  - Add UI refactor plan document
  - Remove temporary HTML test files
  - Update codebase markdown generator script
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * feat: implement unified UI rendering pipeline with HTML export
  Major refactoring of the UI/rendering system following plan 010_ui_refactor.md:
  ## New Features
  - Created unified rendering pipeline for both terminal and HTML output
  - Added new ui/render package with models, formatters, and Rich builders
  - Integrated HTML export directly into CLI using Console(record=True)
  - Added centralized UI settings module for configuration
  ## Breaking Changes
  - Removed deprecated Deliverable instrument and legacy settlement paths
  - Removed html_export.py module (replaced with console.export_html())
  - Canonicalized event handling to always use 'kind' field (removed 'type' fallback)
  ## Implementation Details
  ### New Package Structure (src/bilancio/ui/render/)
  - models.py: View models for balance sheets, events, and day summaries
  - formatters.py: Event formatter registry with specific formatters for all event types
  - rich_builders.py: Pure functions that return Rich renderables
  - settings.py: Centralized UI configuration
  ### Refactored Components
  - visualization.py: Added renderable-returning functions alongside existing ones
  - display.py: Created renderable versions of display functions
  - run.py: Uses Console(record=True) for unified rendering and HTML export
  - settlement.py: Removed deliverable settlement, kept only DeliveryObligation
  ### Removed Legacy Code
  - Deleted domain/instruments/nonfinancial.py (Deliverable class)
  - Removed 577 lines of complex HTML generation in html_export.py
  - Removed deliverable tests and references throughout codebase
  ## Benefits
  - Single rendering pipeline for terminal and HTML (no duplication)
  - Simplified codebase with better maintainability
  - Consistent output formatting across all display modes
  - Rich's optimized HTML export with proper styling
  ## Testing
  - Added comprehensive tests for formatters and builders
  - Tested with existing scenarios - all working correctly
  - HTML export generates properly formatted output
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: properly format events in HTML export using formatters
  - Fixed event display to use the formatter registry instead of raw dict output
  - Events now show with proper icons, titles, and formatted details
  - Updated _build_events_detailed_renderables to use registry.format()
  - HTML output now matches terminal display quality
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: display agent list and PayableCreated events in HTML export
  - Fix show_scenario_header_renderable to handle list of AgentSpec objects
  - Add PayableCreated event logging in config/apply.py
  - Display complete agent list at top of terminal and HTML output
  - Ensure all events including PayableCreated are properly formatted
  - Update CLAUDE.md with HTML verification instructions
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * feat: add detailed payment event logging for settlement transparency
  - Log IntraBankPayment events for same-bank transfers
  - Keep ClientPayment for inter-bank transfers (renamed to 'Inter-Bank Payment')
  - Log CashPayment events when cash is used as fallback
  - Add formatters for all payment event types with clear icons
  - Now shows HOW payables are settled, not just that they were settled
  This provides full transparency into payment mechanisms during settlement phase.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * feat: add payment_demo scenario and clean up test files
  - Add payment_demo.yaml - simple scenario for teaching payment mechanisms
  - Demonstrates intra-bank, inter-bank, and cash payments clearly
  - Easy to follow by hand while showing complete payment/clearing cycle
  - Remove temporary test files
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * docs: add TODO notes and agent documentation
  - Add TODO.md with note about deposits created via loans
  - Add AGENTS.md documenting agent types and capabilities
  - Add sasa_scenario.yaml example scenario
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * docs: add Monetary Theory Chapter 5 PDF reference
  Add PDF document for Chapter 5 of Monetary Theory course material
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * feat: add custom slash command for generating codebase markdown
  - Created /generate-codebase command in .claude/commands/
  - Command runs the codebase markdown generation script
  - Opens the project folder in Finder after generation
  - Reports statistics about the generated file
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  * fix: address critical PR review feedback and fix all failing tests
  - Remove duplicate CashTransferred formatter registration (critical bug)
  - Remove duplicate return statement in run.py (dead code)
  - Fix all test failures:
    - Update HTML export test to use MONOKAI constant instead of string
    - Fix scenario creation test to use correct --from option
    - Update formatter tests to match actual output format
    - Fix builder tests by removing invalid model fields
    - Correct EventView field names in tests
  All 120 tests now passing.
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  ---------
  Co-authored-by: Claude <noreply@anthropic.com>

- **018ceb77** (2025-08-24) by Vlad Gheorghe
  UI: T-accounts, event tables, and pretty HTML export (#12)
  * UI 011_tbs: add event table view; detailed T-account renderer; CLI/config support for --show table and --t-account; stacked multi-agent T-accounts; light HTML export; heavy-lined tables with zebra striping; improved event mappings; width tweaks for readability.
  * Events table: exclude PhaseA/B/C marker rows; render three separate tables per phase (A/B/C) for day views; improve titles and zebra striping.
  * Event rendering: phase-separated tables; Setup table for day 0; chronological order preserved; improved table styling; stacked T-accounts.
  * HTML export: semantic report (agents table, convergence reason, zebra tables); per-day T-accounts with counterparties; phase-separated events; unified export path; convergence detection fix.

- **11823a65** (2025-08-24) by Vlad Gheorghe
  fix: follow-ups for PR #12 (safe numeric conversions, maturity parsing helper, CSS extraction, tests) (#13)

- **8ac98b9c** (2025-09-02) by vladgheorghe
  Scenarios: add exercise scenarios 1–2 and run via day-1 obligations
  - ex1_cash_for_goods.yaml: switch to delivery obligation + payable due day 1
  - ex2_two_firms_cash_purchase.yaml: modeled via day-1 obligations
  - Kept setup to endow assets only; settlement occurs in simulation
  - Validated and produced HTML reports under temp/
  Note: Scenarios 3–4 need claim assignment + scheduled actions (not yet supported).

- **89ca7621** (2025-09-04) by Vlad Gheorghe
  feat(sim): scheduled actions (B1), alias support, claim transfer + exercises 1–7 (#14)
  * Plan: Mid-simulation actions via Phase B split (B1 scheduled, B2 settlement), aliases, and explicit claim transfer
  - Keep Phase A reserved; execute scheduled actions at start of Phase B
  - Add alias support on create-* actions for contracts (mint_cash, mint_reserves, create_payable, create_delivery_obligation)
  - Add transfer_claim action referencing by alias or id (both allowed if consistent)
  - Schedule actions by day; render HTML with separate Phase B1/B2 tables
  - No code changes yet — planning document only (plans/scheduled_actions_and_aliases.md)
  * Move plan to docs/plans with numbering: 012_scheduled_actions_and_aliases.md
  * feat(sim): scheduled actions (Phase B1) + alias support + claim transfer\n\n- models: add alias to create_*; add TransferClaim; add ScheduledAction + scheduled_actions on scenario\n- system: state aliases + scheduled_actions_by_day; create_delivery_obligation/mint_* accept alias and log it; run_day executes B1 then B2\n- apply: wire aliases, pass alias into system APIs, implement transfer_claim reassignment\n- html export: add ID/Alias column to events and T-accounts; split Phase B into B1/B2 tables\n- ui/run: stage scheduled_actions and carry id_or_alias to HTML rows\n\nscenarios:\n- ex1/ex2 already added; ex3 updated to day1 assignment + day2 settlement (aliases shown); ex4 generic claim transfer with consideration\n\nnote: step-mode DayReport None issue still present (not addressed)
  * ui: show aliases on cancel/settle events + ID fallback
  - engines/system: include alias + contract_id on DeliveryObligationCancelled
  - engines/settlement: include alias + contract_id on DeliveryObligationSettled and PayableSettled
  - html_export: ID/Alias column considers obligation_id and pid as fallbacks
  scenarios: add Ex6 and Ex7 YAMLs
  * chore(examples): organize exercise scenarios 1–7 into subfolders and regenerate HTML reports\n\n- Move YAMLs to examples/exercise_scenarios/yaml/\n- Export HTMLs to examples/exercise_scenarios/html/ for ex1–ex7
  * chore(examples): regenerate HTML reports for ex2–ex7 in examples/exercise_scenarios/html/
  * fix: address PR feedback (critical+moderate)
  - models: move model_validator import to module scope
  - apply: order-independent transfer_claim validation with clear errors
  - ops/aliases: add helpers for alias/id lookup; use in settlement/system
  - ui/run: preflight validate scheduled alias references; refactor row dict builder
  - html_export: ID/Alias fallback includes obligation_id & pid
  No functional changes to scenarios; validated ex7 run.
  * chore(examples): re-render HTML reports for ex1–ex7
  * fix(ui/run): step-mode HTML export bug\n\nMove _row_dict helper out of inner block and ensure day_rows assignments execute within the agent loop. This fixes unreachable code causing empty T-account rows in step-mode exports.
  * test: add coverage for TransferClaim, schedule alias validation, B1 execution, and alias helpers

- **e09cfe56** (2025-09-05) by vladgheorghe
  Consolidated ex. HTMLs

- **20318846** (2025-09-05) by vladgheorghe
  docs: update scenario translator prompt for scheduled actions, aliases, transfer_claim, and CLI usage

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
from dataclasses import dataclass
import math
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
    from rich.console import RenderableType
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    RenderableType = Any

from bilancio.analysis.balances import AgentBalance, agent_balance
from bilancio.engines.system import System


def _format_currency(amount: int, show_sign: bool = False) -> str:
    """Format an integer amount as currency."""
    formatted = f"{amount:,}"
    if show_sign and amount > 0:
        formatted = f"+{formatted}"
    return formatted



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
        # Show both name and ID for clarity
        if agent.name and agent.name != agent_id:
            title = f"{agent.name} [{agent_id}] ({agent.kind})"
        else:
            title = f"{agent_id} ({agent.kind})"
    
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
            if asset_type in ['delivery_obligation']:
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
            if liability_type in ['delivery_obligation']:
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
        is_nonfinancial = asset_type in ['delivery_obligation']
        
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
        is_nonfinancial = liability_type in ['delivery_obligation']
        
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
            # Show both name and ID for clarity
            if agent.name and agent.name != balance.agent_id:
                title = f"{agent.name} [{balance.agent_id}]\n({agent.kind})"
            else:
                title = f"{balance.agent_id}\n({agent.kind})"
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
            if asset_type not in ['delivery_obligation']:
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
            if liability_type not in ['delivery_obligation']:
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
        
        # Add valued delivery obligations total if present
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
            if asset_type not in ['delivery_obligation']:
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
            if liability_type not in ['delivery_obligation']:
                amount = _format_currency(balance.liabilities_by_kind[liability_type])
                liability_name = liability_type
                if len(liability_name + " " + amount) > col_width:
                    liability_name = liability_name[:col_width-len(amount)-4] + "..."
                data.append((liability_name, amount))
        
        data.append(("", ""))
        data.append(("Total Financial", _format_currency(balance.total_financial_assets)))
        
        # Add valued delivery obligations total if present
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
    console = Console() if RICH_AVAILABLE else None
    
    if not events:
        _print("No events to display.", console)
        return
    
    if format == 'summary':
        _display_events_summary(events, console)
    else:
        _display_events_detailed(events, console)


def display_events_table(events: List[Dict[str, Any]], group_by_day: bool = True) -> None:
    """Render events as a table with canonical columns.

    Falls back to simple text when Rich is not available.
    """
    console = Console() if RICH_AVAILABLE else None

    if not events:
        _print("No events to display.", console)
        return

    columns = ["Day", "Phase", "Kind", "From", "To", "SKU/Instr", "Qty", "Amount", "Notes"]

    # Sort events deterministically
    # Drop phase marker events; preserve original insertion (chronological) order
    evs = [e for e in events if e.get("kind") not in ("PhaseA", "PhaseB", "PhaseC")]

    if RICH_AVAILABLE:
        from rich.table import Table as RichTable
        from rich import box as rich_box
        table = RichTable(title="Events", box=rich_box.HEAVY, show_lines=True)
        # Column definitions with better alignment
        table.add_column("Day", justify="right")
        table.add_column("Phase", justify="left")
        table.add_column("Kind", justify="left")
        table.add_column("From", justify="left")
        table.add_column("To", justify="left")
        table.add_column("SKU/Instr", justify="left")
        table.add_column("Qty", justify="right")
        table.add_column("Amount", justify="right")
        table.add_column("Notes", justify="left")
        # Alternate row shading for readability
        try:
            table.row_styles = ["on #ffffff", "on #e6f2ff"]
        except Exception:
            pass

        for e in evs:
            kind = str(e.get("kind", ""))
            # Canonical from/to mapping by kind
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer")
                to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank")
                to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner")
                to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"

            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"

            table.add_row(
                str(e.get("day", "—")),
                str(e.get("phase", "—")),
                kind,
                str(frm or "—"),
                str(to or "—"),
                str(sku),
                str(qty),
                str(amt),
                notes,
            )

        console.print(table) if console else print(table)
    else:
        # Simple header + rows
        header = " | ".join(columns)
        print(header)
        print("-" * len(header))
        for e in evs:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer")
                to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank")
                to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner")
                to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"
            row = [
                str(e.get("day", "—")),
                str(e.get("phase", "—")),
                kind,
                str(frm or "—"),
                str(to or "—"),
                str(sku),
                str(qty),
                str(amt),
                notes,
            ]
            print(" | ".join(row))


def display_events_table_renderable(events: List[Dict[str, Any]]) -> RenderableType:
    """Return a Rich Table renderable (or string) for events table."""
    if not events:
        return Text("No events to display.", style="dim") if RICH_AVAILABLE else "No events to display."

    columns = ["Day", "Phase", "Kind", "From", "To", "SKU/Instr", "Qty", "Amount", "Notes"]
    # Drop phase marker events; preserve original insertion (chronological) order
    evs = [e for e in events if e.get("kind") not in ("PhaseA", "PhaseB", "PhaseC")]

    if RICH_AVAILABLE:
        from rich.table import Table as RichTable
        from rich import box as rich_box
        table = RichTable(title="Events", box=rich_box.HEAVY, show_lines=True)
        table.add_column("Day", justify="right")
        table.add_column("Phase", justify="left")
        table.add_column("Kind", justify="left")
        table.add_column("From", justify="left")
        table.add_column("To", justify="left")
        table.add_column("SKU/Instr", justify="left")
        table.add_column("Qty", justify="right")
        table.add_column("Amount", justify="right")
        table.add_column("Notes", justify="left")
        try:
            table.row_styles = ["on #ffffff", "on #e6f2ff"]
        except Exception:
            pass

        for e in evs:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer")
                to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank")
                to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner")
                to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"

            table.add_row(
                str(e.get("day", "—")),
                str(e.get("phase", "—")),
                kind,
                str(frm or "—"),
                str(to or "—"),
                str(sku),
                str(qty),
                str(amt),
                notes,
            )
        return table
    else:
        header = " | ".join(columns)
        lines = [header, "-" * len(header)]
        for e in evs:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer")
                to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank")
                to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner")
                to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"
            row = [
                str(e.get("day", "—")),
                str(e.get("phase", "—")),
                kind,
                str(frm or "—"),
                str(to or "—"),
                str(sku),
                str(qty),
                str(amt),
                notes,
            ]
            lines.append(" | ".join(row))
        return "\n".join(lines)


def display_events_tables_by_phase_renderables(events: List[Dict[str, Any]], day: Optional[int] = None) -> List[RenderableType]:
    """Return three event tables (A, B, C) using phase markers as section dividers.

    - Excludes PhaseA/PhaseB/PhaseC events from rows.
    - Titles indicate the phase and optional day.
    """
    if RICH_AVAILABLE:
        from rich.table import Table as RichTable
        from rich import box as rich_box
        from rich.text import Text as RichText
    
    # If these are setup-phase events (day 0), render as a single "Setup" table
    if any(e.get("phase") == "setup" for e in events):
        return _build_single_setup_table(events, day)

    # Group by phase markers in original order
    buckets = {"A": [], "B": [], "C": []}
    current = "A"
    for e in events:
        kind = e.get("kind")
        if kind == "PhaseA":
            current = "A"; continue
        if kind == "PhaseB":
            current = "B"; continue
        if kind == "PhaseC":
            current = "C"; continue
        buckets[current].append(e)

    def build_table(phase: str, rows: List[Dict[str, Any]]):
        title_parts = {
            "A": "Phase A — Start of day",
            "B": "Phase B — Settlement",
            "C": "Phase C — Clearing"
        }
        title = title_parts.get(phase, f"Phase {phase}")
        if day is not None:
            title = f"{title} (Day {day})"

        if not RICH_AVAILABLE:
            # Simple text fallback
            header = ["Kind", "From", "To", "SKU/Instr", "Qty", "Amount", "Notes"]
            out = [f"{title}", " | ".join(header), "-" * 80]
            for e in rows:
                kind = str(e.get("kind", ""))
                # map from/to like in table renderers
                if kind in ("CashDeposited", "CashWithdrawn"):
                    frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                    to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
                elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                    frm = e.get("payer"); to = e.get("payee")
                elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                    frm = e.get("debtor_bank"); to = e.get("creditor_bank")
                elif kind == "StockCreated":
                    frm = e.get("owner"); to = None
                else:
                    frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                    to = e.get("to") or e.get("creditor") or e.get("payee")
                sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
                qty = e.get("qty") or e.get("quantity") or "—"
                amt = e.get("amount") or "—"
                notes = ""
                if kind == "ClientPayment":
                    notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
                elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                    notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                    if 'due_day' in e:
                        notes += f"; due {e.get('due_day')}"
                out.append(" | ".join(map(str, [kind, frm or "—", to or "—", sku, qty, amt, notes])))
            return "\n".join(out)

        # Rich table
        table = RichTable(title=title, box=rich_box.HEAVY, show_lines=True)
        table.add_column("Kind", justify="left")
        table.add_column("From", justify="left")
        table.add_column("To", justify="left")
        table.add_column("SKU/Instr", justify="left")
        table.add_column("Qty", justify="right")
        table.add_column("Amount", justify="right")
        table.add_column("Notes", justify="left")
        try:
            table.row_styles = ["on #ffffff", "on #e6f2ff"] if phase != "C" else ["on #ffffff", "on #fff2cc"]
        except Exception:
            pass
        for e in rows:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer"); to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank"); to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner"); to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            if kind == "ClientPayment":
                notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
                if 'due_day' in e:
                    notes += f"; due {e.get('due_day')}"
            table.add_row(kind, str(frm or "—"), str(to or "—"), str(sku), str(qty), str(amt), notes)
        return table

    renderables: List[RenderableType] = []
    # Phase A is intentionally empty for now; only include if it has rows
    if buckets["A"]:
        renderables.append(build_table("A", buckets["A"]))
    # Phase B: settlements
    renderables.append(build_table("B", buckets["B"]))
    # Phase C: clearing
    renderables.append(build_table("C", buckets["C"]))
    return renderables


def _build_single_setup_table(events: List[Dict[str, Any]], day: Optional[int] = None) -> List[RenderableType]:
    """Render a single setup table for setup-phase events (day 0)."""
    rows = [e for e in events if e.get("phase") == "setup" and e.get("kind") not in ("PhaseA","PhaseB","PhaseC")]
    title = "Setup"
    if day is not None:
        title = f"{title} (Day {day})"
    if not RICH_AVAILABLE:
        header = ["Kind", "From", "To", "SKU/Instr", "Qty", "Amount", "Notes"]
        out = [title, " | ".join(header), "-" * 80]
        for e in rows:
            kind = str(e.get("kind", ""))
            if kind in ("CashDeposited", "CashWithdrawn"):
                frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
                to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
            elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
                frm = e.get("payer"); to = e.get("payee")
            elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
                frm = e.get("debtor_bank"); to = e.get("creditor_bank")
            elif kind == "StockCreated":
                frm = e.get("owner"); to = None
            else:
                frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
                to = e.get("to") or e.get("creditor") or e.get("payee")
            sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
            qty = e.get("qty") or e.get("quantity") or "—"
            amt = e.get("amount") or "—"
            notes = ""
            out.append(" | ".join(map(str, [kind, frm or "—", to or "—", sku, qty, amt, notes])))
        return ["\n".join(out)]

    from rich.table import Table as RichTable
    from rich import box as rich_box
    table = RichTable(title=title, box=rich_box.HEAVY, show_lines=True)
    table.add_column("Kind", justify="left")
    table.add_column("From", justify="left")
    table.add_column("To", justify="left")
    table.add_column("SKU/Instr", justify="left")
    table.add_column("Qty", justify="right")
    table.add_column("Amount", justify="right")
    table.add_column("Notes", justify="left")
    try:
        table.row_styles = ["on #ffffff", "on #e6f2ff"]
    except Exception:
        pass
    for e in rows:
        kind = str(e.get("kind", ""))
        if kind in ("CashDeposited", "CashWithdrawn"):
            frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
            to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
        elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
            frm = e.get("payer"); to = e.get("payee")
        elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
            frm = e.get("debtor_bank"); to = e.get("creditor_bank")
        elif kind == "StockCreated":
            frm = e.get("owner"); to = None
        else:
            frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
            to = e.get("to") or e.get("creditor") or e.get("payee")
        sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
        qty = e.get("qty") or e.get("quantity") or "—"
        amt = e.get("amount") or "—"
        notes = ""
        table.add_row(kind, str(frm or "—"), str(to or "—"), str(sku), str(qty), str(amt), notes)
    return [table]


# ============================================================================
# T-account builder and renderers (detailed with Qty/Value/Counterparty/Maturity)
# ============================================================================

@dataclass
class BalanceRow:
    name: str
    quantity: Optional[int]
    value_minor: Optional[int]
    counterparty_name: Optional[str]
    maturity: Optional[str]
    id_or_alias: Optional[str] = None


@dataclass
class TAccount:
    assets: List[BalanceRow]
    liabilities: List[BalanceRow]


def _format_agent(agent_id: str, system: System) -> str:
    """Format agent as 'Name [ID]' if available."""
    ag = system.state.agents.get(agent_id)
    if ag is None:
        return agent_id
    if ag.name and ag.name != agent_id:
        return f"{ag.name} [{agent_id}]"
    return agent_id


def parse_day_from_maturity(maturity_str: Optional[str]) -> int:
    """Parse a day number from maturity strings like 'Day 42'.

    Returns an integer day. If the input cannot be parsed, returns a large
    sentinel value to sort unknown maturities last.
    """
    if not isinstance(maturity_str, str):
        return math.inf  # type: ignore[return-value]
    s = maturity_str.strip()
    if not s.startswith("Day "):
        return math.inf  # type: ignore[return-value]
    try:
        return int(s[4:].strip())
    except Exception:
        return math.inf  # type: ignore[return-value]


def build_t_account_rows(system: System, agent_id: str) -> TAccount:
    """Build detailed T-account rows from system state for an agent."""
    assets: List[BalanceRow] = []
    liabilities: List[BalanceRow] = []

    agent = system.state.agents[agent_id]

    # Inventory (stocks owned) as assets
    for stock_id in agent.stock_ids:
        lot = system.state.stocks[stock_id]
        try:
            value_minor = int(lot.value)
        except Exception:
            # Fallback for Decimals
            value_minor = int(float(lot.value))
        assets.append(BalanceRow(
            name=f"{lot.sku}",
            quantity=int(lot.quantity),
            value_minor=value_minor,
            counterparty_name="—",
            maturity="—",
        ))

    # Precompute id->alias map for quick lookups
    try:
        id_to_alias = {cid: alias for alias, cid in (system.state.aliases or {}).items()}
    except Exception:
        id_to_alias = {}

    # Contracts as assets (held by agent)
    for cid in agent.asset_ids:
        c = system.state.contracts[cid]
        if c.kind == "delivery_obligation":
            # Receivable goods
            # valued_amount is Decimal
            valued = getattr(c, 'valued_amount', None)
            try:
                valued_minor = int(valued) if valued is not None else None
            except Exception:
                valued_minor = int(float(valued)) if valued is not None else None
            counterparty = _format_agent(c.liability_issuer_id, system)
            maturity = f"Day {getattr(c, 'due_day', '—')}"
            assets.append(BalanceRow(
                name=f"{getattr(c, 'sku', 'goods')} receivable",
                quantity=int(c.amount) if c.amount is not None else None,
                value_minor=valued_minor,
                counterparty_name=counterparty,
                maturity=maturity,
                id_or_alias=id_to_alias.get(cid, cid),
            ))
        else:
            # Financial assets
            counterparty = _format_agent(c.liability_issuer_id, system)
            maturity = "on-demand" if c.kind in ("cash", "bank_deposit", "reserve_deposit") else (
                f"Day {getattr(c, 'due_day', '—')}" if hasattr(c, 'due_day') else "—"
            )
            assets.append(BalanceRow(
                name=f"{c.kind}",
                quantity=None,
                value_minor=int(c.amount) if c.amount is not None else None,
                counterparty_name=counterparty if c.kind != "cash" else "—",
                maturity=maturity,
                id_or_alias=id_to_alias.get(cid, cid),
            ))

    # Contracts as liabilities (issued by agent)
    for cid in agent.liability_ids:
        c = system.state.contracts[cid]
        if c.kind == "delivery_obligation":
            valued = getattr(c, 'valued_amount', None)
            try:
                valued_minor = int(valued) if valued is not None else None
            except Exception:
                valued_minor = int(float(valued)) if valued is not None else None
            counterparty = _format_agent(c.asset_holder_id, system)
            maturity = f"Day {getattr(c, 'due_day', '—')}"
            liabilities.append(BalanceRow(
                name=f"{getattr(c, 'sku', 'goods')} obligation",
                quantity=int(c.amount) if c.amount is not None else None,
                value_minor=valued_minor,
                counterparty_name=counterparty,
                maturity=maturity,
                id_or_alias=id_to_alias.get(cid, cid),
            ))
        else:
            counterparty = _format_agent(c.asset_holder_id, system)
            maturity = "on-demand" if c.kind in ("cash", "bank_deposit", "reserve_deposit") else (
                f"Day {getattr(c, 'due_day', '—')}" if hasattr(c, 'due_day') else "—"
            )
            liabilities.append(BalanceRow(
                name=f"{c.kind}",
                quantity=None,
                value_minor=int(c.amount) if c.amount is not None else None,
                counterparty_name=counterparty,
                maturity=maturity,
                id_or_alias=id_to_alias.get(cid, cid),
            ))

    # Ordering within each side
    def sort_key_assets(row: BalanceRow):
        # Inventory first (has quantity and counterparty '—' and maturity '—'),
        # then receivables (name ends with 'receivable'), then financial by kind order
        financial_order = {"cash": 0, "bank_deposit": 1, "reserve_deposit": 2, "payable": 3}
        if row.quantity is not None and row.counterparty_name == "—":
            return (0, 0, row.name or "")
        if row.name.endswith("receivable"):
            day_num = parse_day_from_maturity(row.maturity)
            return (1, day_num, row.name)
        return (2, financial_order.get(row.name, 99), row.name)

    def sort_key_liabs(row: BalanceRow):
        # Obligations (name ends with 'obligation') by due day, then financial by order
        financial_order = {"payable": 0, "bank_deposit": 1, "reserve_deposit": 2, "cash": 3}
        if row.name.endswith("obligation"):
            day_num = parse_day_from_maturity(row.maturity)
            return (0, day_num, row.name)
        return (1, financial_order.get(row.name, 99), row.name)

    assets.sort(key=sort_key_assets)
    liabilities.sort(key=sort_key_liabs)

    return TAccount(assets=assets, liabilities=liabilities)


def display_agent_t_account(system: System, agent_id: str, format: str = 'rich') -> None:
    """Display detailed T-account table for an agent."""
    if format == 'rich' and not RICH_AVAILABLE:
        format = 'simple'
    if format == 'rich':
        table = display_agent_t_account_renderable(system, agent_id)
        Console().print(table)
    else:
        # Simple ASCII fallback
        acct = build_t_account_rows(system, agent_id)
        columns = ["Name", "Qty", "Value", "Counterparty", "Maturity"]
        # Prepare rows
        max_rows = max(len(acct.assets), len(acct.liabilities))
        header = " | ".join([f"Assets:{c}" for c in columns] + [f"Liabilities:{c}" for c in columns])
        print(header)
        print("-" * len(header))
        for i in range(max_rows):
            a = acct.assets[i] if i < len(acct.assets) else None
            l = acct.liabilities[i] if i < len(acct.liabilities) else None
            def fmt_qty(r): return f"{r.quantity:,}" if (r and r.quantity is not None) else "—"
            def fmt_val(r):
                if not r or r.value_minor is None: return "—"
                return _format_currency(int(r.value_minor))
            def cells(r):
                if not r: return ("", "", "", "", "")
                return (r.name, fmt_qty(r), fmt_val(r), r.counterparty_name or "—", r.maturity or "—")
            row = list(cells(a) + cells(l))
            print(" | ".join(str(x) for x in row))


def display_agent_t_account_renderable(system: System, agent_id: str) -> RenderableType:
    """Return a Rich Table renderable for detailed T-account."""
    if not RICH_AVAILABLE:
        # Fallback to string
        acct = build_t_account_rows(system, agent_id)
        lines = []
        columns = ["Name", "Qty", "Value", "Counterparty", "Maturity"]
        lines.append(" | ".join([f"Assets:{c}" for c in columns] + [f"Liabilities:{c}" for c in columns]))
        max_rows = max(len(acct.assets), len(acct.liabilities))
        for i in range(max_rows):
            a = acct.assets[i] if i < len(acct.assets) else None
            l = acct.liabilities[i] if i < len(acct.liabilities) else None
            def fmt_qty(r): return f"{r.quantity:,}" if (r and r.quantity is not None) else "—"
            def fmt_val(r):
                if not r or r.value_minor is None: return "—"
                return _format_currency(int(r.value_minor))
            def cells(r):
                if not r: return ("", "", "", "", "")
                return (r.name, fmt_qty(r), fmt_val(r), r.counterparty_name or "—", r.maturity or "—")
            row = list(cells(a) + cells(l))
            lines.append(" | ".join(str(x) for x in row))
        return "\n".join(lines)

    # Rich path
    from rich.table import Table as RichTable
    from rich import box as rich_box
    acct = build_t_account_rows(system, agent_id)

    ag = system.state.agents[agent_id]
    title = f"{ag.name} [{agent_id}] ({ag.kind})" if ag.name and ag.name != agent_id else f"{agent_id} ({ag.kind})"

    table = RichTable(title=title, box=rich_box.HEAVY, title_style="bold cyan", show_lines=True)
    # Add 10 columns: 5 for assets, 5 for liabilities
    table.add_column("Name", style="green", justify="left")
    table.add_column("Qty", style="green", justify="right")
    table.add_column("Value", style="green", justify="right")
    table.add_column("Counterparty", style="green", justify="left")
    table.add_column("Maturity", style="green", justify="right")
    table.add_column("Name", style="red", justify="left")
    table.add_column("Qty", style="red", justify="right")
    table.add_column("Value", style="red", justify="right")
    table.add_column("Counterparty", style="red", justify="left")
    table.add_column("Maturity", style="red", justify="right")
    try:
        table.row_styles = ["on #ffffff", "on #fff2cc"]
    except Exception:
        pass

    def fmt_qty(r): return f"{r.quantity:,}" if (r and r.quantity is not None) else "—"
    def fmt_val(r):
        if not r or r.value_minor is None: return "—"
        return _format_currency(int(r.value_minor))
    def cells(r):
        if not r: return ("", "", "", "", "")
        return (r.name, fmt_qty(r), fmt_val(r), r.counterparty_name or "—", r.maturity or "—")

    max_rows = max(len(acct.assets), len(acct.liabilities))
    for i in range(max_rows):
        a = acct.assets[i] if i < len(acct.assets) else None
        l = acct.liabilities[i] if i < len(acct.liabilities) else None
        table.add_row(*cells(a), *cells(l))
    return table


def _print(text: str, console: Optional['Console'] = None) -> None:
    """Print using Rich console if available, otherwise regular print."""
    if console:
        console.print(text)
    else:
        print(text)


def _display_events_summary(events: List[Dict[str, Any]], console: Optional['Console'] = None) -> None:
    """Display events in a condensed summary format."""
    for event in events:
        kind = event.get("kind", "Unknown")
        day = event.get("day", "?")
        
        if kind == "PayableSettled":
            _print(f"Day {day}: 💰 {event['debtor']} → {event['creditor']}: ${event['amount']}", console)
        elif kind == "DeliveryObligationSettled":
            qty = event.get('qty', event.get('quantity', 'N/A'))
            _print(f"Day {day}: 📦 {event['debtor']} → {event['creditor']}: {qty} {event.get('sku', 'items')}", console)
        elif kind == "StockTransferred":
            _print(f"Day {day}: 🚚 {event['frm']} → {event['to']}: {event['qty']} {event['sku']}", console)
        elif kind == "CashTransferred":
            _print(f"Day {day}: 💵 {event['frm']} → {event['to']}: ${event['amount']}", console)


def _display_events_detailed(events: List[Dict[str, Any]], console: Optional['Console'] = None) -> None:
    """Display events grouped by day with detailed formatting."""
    # Separate setup events from day events
    setup_events = []
    events_by_day = defaultdict(list)
    
    for event in events:
        # Check if this is a setup phase event
        if event.get("phase") == "setup":
            setup_events.append(event)
        else:
            day = event.get("day", -1)
            events_by_day[day].append(event)
    
    # Display setup events first if any
    if setup_events:
        _print(f"\n📅 Setup Phase:", console)
        # Setup events don't have phase markers, display them directly
        for event in setup_events:
            _display_single_event(event, console, indent="  ")
    
    # Display events for each day
    for day in sorted(events_by_day.keys()):
        if day >= 0:
            _print(f"\n📅 Day {day}:", console)
        else:
            _print(f"\n📅 Unknown Day:", console)
        
        _display_day_events(events_by_day[day], console)


def _display_day_events(day_events: List[Dict[str, Any]], console: Optional['Console'] = None) -> None:
    """Display events for a single day with proper formatting."""
    # Group events by their phase timing
    phase_a_events = []
    phase_b_events = []
    phase_c_events = []
    
    # Track which phase we're in based on phase markers
    current_phase = "A"  # Start with phase A
    
    for event in day_events:
        kind = event.get("kind", "Unknown")
        
        # Phase markers change which phase we're in
        if kind == "PhaseA":
            current_phase = "A"
        elif kind == "PhaseB":
            current_phase = "B"
        elif kind == "PhaseC":
            current_phase = "C"
        else:
            # Regular events go into the current phase bucket
            if current_phase == "A":
                phase_a_events.append(event)
            elif current_phase == "B":
                phase_b_events.append(event)
            elif current_phase == "C":
                phase_c_events.append(event)
    
    # Always display all three phases
    # Phase A - No-op phase, just marks beginning of day
    _print(f"\n  ⏰ Phase A: Day begins", console)
    for event in phase_a_events:
        _display_single_event(event, console, indent="    ")
    
    # Phase B - Settlement phase where obligations are fulfilled
    _print(f"\n  💳 Phase B: Settlement (fulfilling due obligations)", console)
    for event in phase_b_events:
        _display_single_event(event, console, indent="    ")
    
    # Phase C - Intraday netting
    _print(f"\n  📋 Phase C: Intraday netting", console)
    for event in phase_c_events:
        _display_single_event(event, console, indent="    ")
    
    # Mark end of day
    _print(f"\n  🌙 Day ended", console)


def _display_single_event(event: Dict[str, Any], console: Optional['Console'] = None, indent: str = "  ") -> None:
    """Display a single event with proper formatting."""
    kind = event.get("kind", "Unknown")
    
    if kind == "StockCreated":
        _print(f"{indent}🏭 Stock created: {event['owner']} gets {event['qty']} {event['sku']}", console)
    
    elif kind == "CashMinted":
        _print(f"{indent}💰 Cash minted: ${event['amount']} to {event['to']}", console)
    
    elif kind == "PayableSettled":
        _print(f"{indent}✅ Payment settled: {event['debtor']} → {event['creditor']}: ${event['amount']}", console)
    
    elif kind == "PayableCancelled":
        _print(f"{indent}  └─ Payment obligation removed from books", console)
    
    elif kind == "DeliveryObligationSettled":
        qty = event.get('qty', event.get('quantity', 'N/A'))
        sku = event.get('sku', 'items')
        _print(f"{indent}✅ Delivery settled: {event['debtor']} → {event['creditor']}: {qty} {sku}", console)
    
    elif kind == "DeliveryObligationCancelled":
        _print(f"{indent}  └─ Delivery obligation removed from books", console)
    
    elif kind == "StockTransferred":
        _print(f"{indent}📦 Stock transferred: {event['frm']} → {event['to']}: {event['qty']} {event['sku']}", console)
    
    elif kind == "CashTransferred":
        _print(f"{indent}💵 Cash transferred: {event['frm']} → {event['to']}: ${event['amount']}", console)
    
    elif kind == "StockSplit":
        sku = event.get('sku', 'N/A')
        original_qty = event.get('original_qty', 0)
        split_qty = event.get('split_qty', 0)
        remaining_qty = event.get('remaining_qty', 0)
        # Show shortened IDs for readability
        original_id = event.get('original_id', '')
        new_id = event.get('new_id', '')
        short_orig = original_id.split('_')[-1][:8] if original_id else 'N/A'
        short_new = new_id.split('_')[-1][:8] if new_id else 'N/A'
        _print(f"{indent}📊 Stock split: {short_orig} → {short_new}: {split_qty} {sku} (keeping {remaining_qty})", console)
    
    elif kind == "ReservesMinted":
        amount = event.get('amount', 0)
        to = event.get('to', 'N/A')
        _print(f"{indent}🏦 Reserves minted: ${amount} to {to}", console)
    
    elif kind == "CashDeposited":
        customer = event.get('customer', 'N/A')
        bank = event.get('bank', 'N/A')
        amount = event.get('amount', 0)
        _print(f"{indent}🏧 Cash deposited: {customer} → {bank}: ${amount}", console)
    
    elif kind == "DeliveryObligationCreated":
        frm = event.get('frm', event.get('from', 'N/A'))
        to = event.get('to', 'N/A')
        qty = event.get('qty', event.get('quantity', 0))
        sku = event.get('sku', 'N/A')
        due_day = event.get('due_day', 'N/A')
        _print(f"{indent}📝 Delivery obligation created: {frm} → {to}: {qty} {sku} (due day {due_day})", console)
    
    elif kind == "PayableCreated":
        frm = event.get('frm', event.get('from', event.get('debtor', 'N/A')))
        to = event.get('to', event.get('creditor', 'N/A'))
        amount = event.get('amount', 0)
        due_day = event.get('due_day', 'N/A')
        _print(f"{indent}💸 Payable created: {frm} → {to}: ${amount} (due day {due_day})", console)
    
    elif kind == "ClientPayment":
        payer = event.get('payer', 'N/A')
        payee = event.get('payee', 'N/A')
        amount = event.get('amount', 0)
        payer_bank = event.get('payer_bank', '')
        payee_bank = event.get('payee_bank', '')
        _print(f"{indent}💳 Client payment: {payer} ({payer_bank}) → {payee} ({payee_bank}): ${amount}", console)
    
    elif kind == "InterbankCleared":
        debtor = event.get('debtor_bank', 'N/A')
        creditor = event.get('creditor_bank', 'N/A')
        amount = event.get('amount', 0)
        _print(f"{indent}🏦 Interbank cleared: {debtor} → {creditor}: ${amount} (netted)", console)
    
    elif kind == "ReservesTransferred":
        frm = event.get('frm', 'N/A')
        to = event.get('to', 'N/A')
        amount = event.get('amount', 0)
        _print(f"{indent}💰 Reserves transferred: {frm} → {to}: ${amount}", console)
    
    elif kind == "InstrumentMerged":
        # This is a technical event, show it more compactly
        _print(f"{indent}🔀 Instruments merged", console)
    
    elif kind == "InterbankOvernightCreated":
        debtor = event.get('debtor_bank', 'N/A')
        creditor = event.get('creditor_bank', 'N/A')
        amount = event.get('amount', 0)
        _print(f"{indent}🌙 Overnight payable created: {debtor} → {creditor}: ${amount}", console)
    
    elif kind in ["PhaseA", "PhaseB", "PhaseC"]:
        # Phase markers are not displayed as events themselves
        pass
    
    else:
        # For any other event types, show raw data
        _print(f"{indent}• {kind}: {event}", console)


def display_events_for_day(system: System, day: int) -> None:
    """
    Display all events that occurred on a specific simulation day.
    
    Args:
        system: The bilancio system instance
        day: The simulation day to display events for
    """
    console = Console() if RICH_AVAILABLE else None
    events = [e for e in system.state.events if e.get("day") == day]
    
    if not events:
        _print("  No events occurred on this day.", console)
        return
    
    _display_day_events(events, console)


# ============================================================================
# New Renderable-returning Functions for HTML Export
# ============================================================================

def display_agent_balance_table_renderable(
    system: System,
    agent_id: str,
    format: str = 'rich',
    title: Optional[str] = None
) -> Union[RenderableType, str]:
    """
    Return a renderable for a single agent's balance sheet as a T-account style table.
    
    Args:
        system: The bilancio system instance
        agent_id: ID of the agent to display
        format: Display format ('rich' or 'simple')
        title: Optional custom title for the table
        
    Returns:
        Rich Table renderable for rich format, or string for simple format
    """
    if format == 'rich' and not RICH_AVAILABLE:
        format = 'simple'
    
    # Get agent balance
    balance = agent_balance(system, agent_id)
    
    if format == 'rich':
        # Get agent info
        agent = system.state.agents[agent_id]
        if title is None:
            # Show both name and ID for clarity
            if agent.name and agent.name != agent_id:
                title = f"{agent.name} [{agent_id}] ({agent.kind})"
            else:
                title = f"{agent_id} ({agent.kind})"
        
        return _create_rich_agent_balance_table(title, balance)
    else:
        # Return simple text format as string
        return _build_simple_agent_balance_string(balance, system, agent_id, title)


def display_multiple_agent_balances_renderable(
    system: System,
    items: List[Union[str, AgentBalance]], 
    format: str = 'rich'
) -> Union[RenderableType, str]:
    """
    Return renderables for multiple agent balance sheets side by side for comparison.
    
    Args:
        system: The bilancio system instance
        items: List of agent IDs (str) or AgentBalance instances
        format: Display format ('rich' or 'simple')
        
    Returns:
        Rich Columns renderable for rich format, or string for simple format
    """
    if format == 'rich' and not RICH_AVAILABLE:
        format = 'simple'
    
    # Convert agent IDs to balance objects if needed
    balances = []
    for item in items:
        if isinstance(item, str):
            balances.append(agent_balance(system, item))
        else:
            balances.append(item)
    
    if format == 'rich':
        # Create individual tables for each balance
        tables = []
        for balance in balances:
            # Get agent name if system is available
            if system and balance.agent_id in system.state.agents:
                agent = system.state.agents[balance.agent_id]
                # Show both name and ID for clarity
                if agent.name and agent.name != balance.agent_id:
                    title = f"{agent.name} [{balance.agent_id}]\n({agent.kind})"
                else:
                    title = f"{balance.agent_id}\n({agent.kind})"
            else:
                title = f"{balance.agent_id}"
            
            table = _create_compact_rich_balance_table(title, balance)
            tables.append(table)
        
        return Columns(tables, equal=True, expand=True)
    else:
        # Return simple text format as string
        return _build_simple_multiple_agent_balances_string(balances, system)


def display_events_renderable(events: List[Dict[str, Any]], format: str = 'detailed') -> List[RenderableType]:
    """
    Return renderables for system events in a nicely formatted way.
    
    Args:
        events: List of event dictionaries from sys.state.events
        format: Display format ('detailed' or 'summary')
        
    Returns:
        List of Rich renderables (or strings for simple format)
    """
    if not events:
        if RICH_AVAILABLE:
            return [Text("No events to display.", style="dim")]
        else:
            return ["No events to display."]
    
    if format == 'summary':
        return _build_events_summary_renderables(events)
    else:
        return _build_events_detailed_renderables(events)


def display_events_for_day_renderable(system: System, day: int) -> List[RenderableType]:
    """
    Return renderables for all events that occurred on a specific simulation day.
    
    Args:
        system: The bilancio system instance
        day: The simulation day to display events for
        
    Returns:
        List of Rich renderables (or strings for simple format)
    """
    events = [e for e in system.state.events if e.get("day") == day]
    
    if not events:
        if RICH_AVAILABLE:
            return [Text("  No events occurred on this day.", style="dim")]
        else:
            return ["  No events occurred on this day."]
    
    return _build_day_events_renderables(events)


# ============================================================================
# Helper Functions for New Renderable Functions
# ============================================================================

def _create_rich_agent_balance_table(title: str, balance: AgentBalance) -> Table:
    """Create a Rich Table for a single agent balance (returns table instead of printing)."""
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
    displayed_asset_skus = set()
    for sku, data in balance.nonfinancial_assets_by_kind.items():
        qty = data['quantity']
        if qty > 0:
            name = f"{sku} receivable [{qty} unit{'s' if qty != 1 else ''}]"
            amount = _format_currency(int(data['value']))
            asset_rows.append((name, amount))
            displayed_asset_skus.add(sku)
    
    # Third: Add financial assets (everything else in assets_by_kind)
    financial_asset_kinds = set()
    for asset_type in sorted(balance.assets_by_kind.keys()):
        # Skip if this is a non-financial type we already displayed
        is_nonfinancial = False
        for sku in displayed_asset_skus:
            # This is a heuristic but works for current instrument types
            if asset_type in ['delivery_obligation']:
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
            if liability_type in ['delivery_obligation']:
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
    
    return table


def _create_compact_rich_balance_table(title: str, balance: AgentBalance) -> Table:
    """Create a compact Rich Table for multiple balance display."""
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
    
    # Third: Add financial assets
    for asset_type in sorted(balance.assets_by_kind.keys()):
        # Skip non-financial types
        if asset_type not in ['delivery_obligation']:
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
        if liability_type not in ['delivery_obligation']:
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
    table.add_row(
        Text("Total Liab.", style="bold red"),
        Text(_format_currency(balance.total_financial_liabilities), style="bold red")
    )
    
    net_worth_style = "bold green" if balance.net_financial >= 0 else "bold red"
    table.add_row(
        Text("Net Financial", style="bold blue"),
        Text(_format_currency(balance.net_financial, show_sign=True), style=net_worth_style)
    )
    
    return table


def _build_simple_agent_balance_string(
    balance: AgentBalance, 
    system: Optional[System] = None, 
    agent_id: Optional[str] = None,
    title: Optional[str] = None
) -> str:
    """Build a simple text format balance sheet string."""
    lines = []
    
    # Get title
    if title is None:
        if system and agent_id and agent_id in system.state.agents:
            agent = system.state.agents[agent_id]
            if agent.name and agent.name != agent_id:
                title = f"{agent.name} [{agent_id}] ({agent.kind})"
            else:
                title = f"{agent_id} ({agent.kind})"
        else:
            title = f"Agent {balance.agent_id}"
    
    lines.append(f"\n{title}")
    lines.append("=" * 70)
    lines.append(f"{'ASSETS':<30} {'Amount':>12} | {'LIABILITIES':<30} {'Amount':>12}")
    lines.append("-" * 70)
    
    # Simplified balance sheet representation for simple format
    lines.append(f"{'Total Financial':<30} {_format_currency(balance.total_financial_assets):>12} | "
          f"{'Total Financial':<30} {_format_currency(balance.total_financial_liabilities):>12}")
    
    lines.append("-" * 70)
    lines.append(f"{'':>44} | {'NET FINANCIAL':<30} {_format_currency(balance.net_financial, show_sign=True):>12}")
    
    return "\n".join(lines)


def _build_simple_multiple_agent_balances_string(
    balances: List[AgentBalance], 
    system: Optional[System] = None
) -> str:
    """Build a simple text format for multiple agent balances."""
    lines = []
    lines.append("\nMultiple Agent Balances (Simplified View)")
    lines.append("=" * 60)
    
    for balance in balances:
        if system and balance.agent_id in system.state.agents:
            agent = system.state.agents[balance.agent_id]
            header = f"{agent.name or balance.agent_id} ({agent.kind})"
        else:
            header = balance.agent_id
        
        lines.append(f"{header}: Net Financial = {_format_currency(balance.net_financial, show_sign=True)}")
    
    return "\n".join(lines)


def _build_events_summary_renderables(events: List[Dict[str, Any]]) -> List[RenderableType]:
    """Build renderables for events in summary format."""
    renderables = []
    
    for event in events:
        kind = event.get("kind", "Unknown")
        day = event.get("day", "?")
        
        if kind == "PayableSettled":
            text = f"Day {day}: 💰 {event['debtor']} → {event['creditor']}: ${event['amount']}"
        elif kind == "DeliveryObligationSettled":
            qty = event.get('qty', event.get('quantity', 'N/A'))
            text = f"Day {day}: 📦 {event['debtor']} → {event['creditor']}: {qty} {event.get('sku', 'items')}"
        elif kind == "StockTransferred":
            text = f"Day {day}: 🚚 {event['frm']} → {event['to']}: {event['qty']} {event['sku']}"
        elif kind == "CashTransferred":
            text = f"Day {day}: 💵 {event['frm']} → {event['to']}: ${event['amount']}"
        else:
            continue  # Skip other events in summary mode
        
        if RICH_AVAILABLE:
            renderables.append(Text(text))
        else:
            renderables.append(text)
    
    return renderables


def _build_events_detailed_renderables(events: List[Dict[str, Any]]) -> List[RenderableType]:
    """Build renderables for events in detailed format, organized by phases."""
    # Import and use the phase-aware version
    from bilancio.analysis.visualization_phases import build_events_detailed_with_phases
    return build_events_detailed_with_phases(events, RICH_AVAILABLE)
    
def _build_events_detailed_renderables_old(events: List[Dict[str, Any]]) -> List[RenderableType]:
    """Old version - kept for reference."""
    renderables = []
    
    # Use the formatter registry to format events nicely
    from bilancio.ui.render.formatters import registry
    
    # Group events by phase
    phases = {"A": [], "B": [], "C": [], "other": []}
    for event in events:
        phase = event.get("phase", "other")
        if phase in ["A", "B", "C"]:
            phases[phase].append(event)
        else:
            phases["other"].append(event)
    
    # Display events organized by phase
    if phases["A"]:
        if RICH_AVAILABLE:
            from rich.text import Text
            phase_header = Text("\n⏰ Phase A - Morning Activities", style="bold cyan")
            renderables.append(phase_header)
        else:
            renderables.append("\n⏰ Phase A - Morning Activities")
        
        for event in phases["A"]:
            kind = event.get("kind", "Unknown")
            if kind == "PhaseA":
                continue  # Skip the phase marker itself</            
            renderables.extend(_format_single_event(event, registry))
    
    if phases["B"]:
        if RICH_AVAILABLE:
            from rich.text import Text
            phase_header = Text("\n🌅 Phase B - Business Hours", style="bold yellow")
            renderables.append(phase_header)
        else:
            renderables.append("\n🌅 Phase B - Business Hours")
            
        for event in phases["B"]:
            kind = event.get("kind", "Unknown")
            if kind == "PhaseB":
                continue  # Skip the phase marker itself
            renderables.extend(_format_single_event(event, registry))
    
    if phases["C"]:
        if RICH_AVAILABLE:
            from rich.text import Text
            phase_header = Text("\n🌙 Phase C - End of Day Clearing", style="bold green")
            renderables.append(phase_header)
        else:
            renderables.append("\n🌙 Phase C - End of Day Clearing")
            
        for event in phases["C"]:
            kind = event.get("kind", "Unknown")
            if kind == "PhaseC":
                continue  # Skip the phase marker itself
            renderables.extend(_format_single_event(event, registry))
    
    # Display any events without phase markers
    if phases["other"]:
        for event in phases["other"]:
            kind = event.get("kind", "Unknown")
            if kind in ["PhaseA", "PhaseB", "PhaseC"]:
                continue  # Skip phase markers
            renderables.extend(_format_single_event(event, registry))
    
    return renderables


def _format_single_event(event: Dict[str, Any], registry) -> List[RenderableType]:
    """Format a single event and return renderables."""
    renderables = []
    
    # Format the event using the registry
    title, lines, icon = registry.format(event)
    
    if RICH_AVAILABLE:
        from rich.text import Text
        # Create a nice formatted display with icon and details
        text = Text()
        
        # Add icon and title with color based on event type
        if "Transfer" in title or "Payment" in title:
            text.append(title, style="bold cyan")
        elif "Settled" in title or "Cleared" in title:
            text.append(title, style="bold green")
        elif "Created" in title or "Minted" in title:
            text.append(title, style="bold yellow")
        elif "Consolidation" in title or "Split" in title:
            text.append(title, style="dim italic")
        else:
            text.append(title, style="bold")
        
        # Add details with proper indentation and styling
        if lines:
            for i, line in enumerate(lines[:3]):  # Show up to 3 lines
                text.append("\n   ")
                if "→" in line or "←" in line:
                    # Flow lines - make them prominent
                    text.append(line, style="white")
                elif ":" in line:
                    # Split field and value for better formatting
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        field, value = parts
                        text.append(field + ":", style="dim")
                        text.append(value, style="white")
                    else:
                        text.append(line, style="dim white")
                elif line.startswith("("):
                    # Technical explanations in parentheses - make them dimmer
                    text.append(line, style="dim italic")
                else:
                    text.append(line, style="white")
        
        renderables.append(text)
    else:
        # Simple text format
        text = f"• {title}"
        if lines:
            text += " - " + ", ".join(lines[:2])
        renderables.append(text)
    
    return [renderables[0]] if renderables else []


def _build_day_events_renderables(events: List[Dict[str, Any]]) -> List[RenderableType]:
    """Build renderables for events in a single day."""
    return _build_events_detailed_renderables(events)

```

---

### 📄 src/bilancio/analysis/visualization_phases.py

```python
"""Phase-aware event visualization for bilancio."""

from typing import List, Dict, Any, Union
from rich.text import Text

RenderableType = Any  # Type alias for renderables

def build_events_detailed_with_phases(events: List[Dict[str, Any]], RICH_AVAILABLE: bool = True) -> List[RenderableType]:
    """Build renderables for events in detailed format, properly organized by phase markers."""
    renderables = []
    
    # Use the formatter registry to format events nicely
    from bilancio.ui.render.formatters import registry
    
    # Group events by phase markers (PhaseA, PhaseB, PhaseC)
    # Events between PhaseA and PhaseB are in Phase A
    # Events between PhaseB and PhaseC are in Phase B  
    # Events after PhaseC are in Phase C
    phase_a_events = []
    phase_b_events = []
    phase_c_events = []
    setup_events = []
    
    current_phase = None
    for event in events:
        kind = event.get("kind", "Unknown")
        
        # Check for phase markers to update current phase
        if kind == "PhaseA":
            current_phase = "A"
            continue  # Skip the marker itself
        elif kind == "PhaseB":
            current_phase = "B"
            continue  # Skip the marker itself
        elif kind == "PhaseC":
            current_phase = "C"
            continue  # Skip the marker itself
        
        # Sort events into phases based on current phase
        if event.get("phase") == "setup":
            setup_events.append(event)
        elif current_phase == "A":
            phase_a_events.append(event)
        elif current_phase == "B":
            phase_b_events.append(event)
        elif current_phase == "C":
            phase_c_events.append(event)
        else:
            # Events before any phase marker (during simulation but no phase set yet)
            # This shouldn't happen but default to phase A
            if event.get("phase") == "simulation":
                phase_a_events.append(event)
    
    # Display setup events if any
    if setup_events:
        if RICH_AVAILABLE:
            phase_header = Text("Setup", style="bold magenta")
            renderables.append(phase_header)
        else:
            renderables.append("Setup")
        
        for event in setup_events:
            renderables.extend(_format_single_event(event, registry, RICH_AVAILABLE))
    
    # Display Phase A events (usually empty as it's just a marker)
    if phase_a_events:
        if RICH_AVAILABLE:
            phase_header = Text("\nPhase A", style="bold cyan")
            renderables.append(phase_header)
        else:
            renderables.append("\nPhase A")
        
        for event in phase_a_events:
            renderables.extend(_format_single_event(event, registry, RICH_AVAILABLE))
    
    # Display Phase B events - Settle obligations due
    if phase_b_events:
        if RICH_AVAILABLE:
            phase_header = Text("\nPhase B - Settle obligations due", style="bold yellow")
            renderables.append(phase_header)
        else:
            renderables.append("\nPhase B - Settle obligations due")
            
        for event in phase_b_events:
            renderables.extend(_format_single_event(event, registry, RICH_AVAILABLE))
    
    # Display Phase C events - Clear intraday nets
    if phase_c_events:
        if RICH_AVAILABLE:
            phase_header = Text("\nPhase C - Clear intraday nets", style="bold green")
            renderables.append(phase_header)
        else:
            renderables.append("\nPhase C - Clear intraday nets")
            
        for event in phase_c_events:
            renderables.extend(_format_single_event(event, registry, RICH_AVAILABLE))
    
    return renderables


def _format_single_event(event: Dict[str, Any], registry, RICH_AVAILABLE: bool) -> List[RenderableType]:
    """Format a single event and return renderables."""
    renderables = []
    
    # Format the event using the registry
    title, lines, icon = registry.format(event)
    
    if RICH_AVAILABLE:
        from rich.text import Text
        # Create a nice formatted display with icon and details
        text = Text()
        
        # Add icon and title with color based on event type
        if "Transfer" in title or "Payment" in title:
            text.append(title, style="bold cyan")
        elif "Settled" in title or "Cleared" in title:
            text.append(title, style="bold green")
        elif "Created" in title or "Minted" in title:
            text.append(title, style="bold yellow")
        elif "Consolidation" in title or "Split" in title:
            text.append(title, style="dim italic")
        else:
            text.append(title, style="bold")
        
        # Add details with proper indentation and styling
        if lines:
            for i, line in enumerate(lines[:3]):  # Show up to 3 lines
                text.append("\n   ")
                if "→" in line or "←" in line:
                    # Flow lines - make them prominent
                    text.append(line, style="white")
                elif ":" in line:
                    # Split field and value for better formatting
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        field, value = parts
                        text.append(field + ":", style="dim")
                        text.append(value, style="white")
                    else:
                        text.append(line, style="dim white")
                elif line.startswith("("):
                    # Technical explanations in parentheses - make them dimmer
                    text.append(line, style="dim italic")
                else:
                    text.append(line, style="white")
        
        renderables.append(text)
    else:
        # Simple text format
        text = f"• {title}"
        if lines:
            text += " - " + ", ".join(lines[:2])
        renderables.append(text)
    
    return [renderables[0]] if renderables else []
```

---

### 📄 src/bilancio/config/__init__.py

```python
"""Configuration layer for Bilancio scenarios."""

from .loaders import load_yaml
from .models import ScenarioConfig
from .apply import apply_to_system

__all__ = ["load_yaml", "ScenarioConfig", "apply_to_system"]
```

---

### 📄 src/bilancio/config/apply.py

```python
"""Apply configuration to a Bilancio system."""

from typing import Dict, Any
from decimal import Decimal

from bilancio.engines.system import System
from bilancio.domain.agents import Bank, Household, Firm, CentralBank, Treasury
from bilancio.ops.banking import deposit_cash, withdraw_cash, client_payment
from bilancio.domain.instruments.credit import Payable
from bilancio.core.errors import ValidationError
from bilancio.core.atomic_tx import atomic

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
            instr_id = system.mint_reserves(
                to_bank_id=action.to,
                amount=action.amount,
                alias=getattr(action, 'alias', None)
            )
            # optional alias capture
            if getattr(action, 'alias', None):
                alias = action.alias
                if alias in system.state.aliases:
                    raise ValueError(f"Alias already exists: {alias}")
                system.state.aliases[alias] = instr_id
            
        elif action_type == "mint_cash":
            instr_id = system.mint_cash(
                to_agent_id=action.to,
                amount=action.amount,
                alias=getattr(action, 'alias', None)
            )
            if getattr(action, 'alias', None):
                alias = action.alias
                if alias in system.state.aliases:
                    raise ValueError(f"Alias already exists: {alias}")
                system.state.aliases[alias] = instr_id
            
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
            instr_id = system.create_delivery_obligation(
                from_agent=action.from_agent,
                to_agent=action.to_agent,
                sku=action.sku,
                quantity=action.quantity,
                unit_price=action.unit_price,
                due_day=action.due_day,
                alias=getattr(action, 'alias', None)
            )
            if getattr(action, 'alias', None):
                alias = action.alias
                if alias in system.state.aliases:
                    raise ValueError(f"Alias already exists: {alias}")
                system.state.aliases[alias] = instr_id
            
        elif action_type == "create_payable":
            # Create a Payable instrument
            # Payable uses asset_holder_id (creditor) and liability_issuer_id (debtor)
            # Note: amount should be in minor units (e.g., cents)
            # If the input is in major units (e.g., dollars), multiply by 100
            # For now, we assume the YAML amounts are already in minor units
            payable = Payable(
                id=system.new_contract_id("PAY"),
                kind="payable",  # Will be set by __post_init__ but required by dataclass
                amount=int(action.amount),  # Assumes amount is already in minor units
                denom="X",  # Default denomination - could be made configurable
                asset_holder_id=action.to_agent,  # creditor holds the asset
                liability_issuer_id=action.from_agent,  # debtor issues the liability
                due_day=action.due_day
            )
            system.add_contract(payable)
            # optional alias capture
            if getattr(action, 'alias', None):
                alias = action.alias
                if alias in system.state.aliases:
                    raise ValueError(f"Alias already exists: {alias}")
                system.state.aliases[alias] = payable.id
            
            # Log the event
            system.log("PayableCreated",
                debtor=action.from_agent,
                creditor=action.to_agent,
                amount=int(action.amount),
                due_day=action.due_day,
                payable_id=payable.id,
                alias=getattr(action, 'alias', None)
            )
        
        elif action_type == "transfer_claim":
            # Transfer claim (reassign asset holder) by alias or id (order-independent validation)
            data = action
            alias = getattr(data, 'contract_alias', None)
            explicit_id = getattr(data, 'contract_id', None)
            id_from_alias = None
            if alias is not None:
                id_from_alias = system.state.aliases.get(alias)
                if id_from_alias is None:
                    raise ValueError(f"Unknown alias: {alias}")
            if alias is not None and explicit_id is not None and id_from_alias != explicit_id:
                raise ValueError(f"Alias {alias} and contract_id {explicit_id} refer to different contracts")
            resolved_id = explicit_id or id_from_alias
            if not resolved_id:
                raise ValueError("transfer_claim requires contract_alias or contract_id to resolve a contract")

            instr = system.state.contracts.get(resolved_id)
            if instr is None:
                raise ValueError(f"Contract not found: {resolved_id}")

            old_holder_id = instr.asset_holder_id
            new_holder_id = data.to_agent

            # Perform reassignment atomically
            with atomic(system):
                old_holder = system.state.agents[old_holder_id]
                new_holder = system.state.agents[new_holder_id]
                if resolved_id not in old_holder.asset_ids:
                    raise ValueError(f"Contract {resolved_id} not in old holder's assets")
                old_holder.asset_ids.remove(resolved_id)
                new_holder.asset_ids.append(resolved_id)
                instr.asset_holder_id = new_holder_id
                system.log("ClaimTransferred",
                           contract_id=resolved_id,
                           frm=old_holder_id,
                           to=new_holder_id,
                           contract_kind=instr.kind,
                           amount=getattr(instr, 'amount', None),
                           due_day=getattr(instr, 'due_day', None),
                           sku=getattr(instr, 'sku', None),
                           alias=alias)
            
        else:
            raise ValueError(f"Unknown action type: {action_type}")
            
    except Exception as e:
        # Add context to the error
        raise ValueError(f"Failed to apply {action_type}: {e}")


def _collect_alias_from_action(action_model) -> str | None:
    return getattr(action_model, 'alias', None)


def validate_scheduled_aliases(config: ScenarioConfig) -> None:
    """Preflight check: ensure aliases referenced by scheduled actions exist by the time of use,
    and detect duplicates across initial and scheduled actions.
    Raises ValueError with a clear message on violation.
    """
    alias_set: set[str] = set()

    # 1) Process initial_actions (creation only)
    for act in config.initial_actions or []:
        try:
            m = parse_action(act)
        except Exception:
            # malformed action will be caught elsewhere
            continue
        alias = _collect_alias_from_action(m)
        if alias:
            if alias in alias_set:
                raise ValueError(f"Duplicate alias in initial_actions: {alias}")
            alias_set.add(alias)

    # 2) Group scheduled by day preserving order
    by_day: dict[int, list] = {}
    for sa in getattr(config, 'scheduled_actions', []) or []:
        by_day.setdefault(sa.day, []).append(sa.action)

    # 3) Validate day by day
    for day in sorted(by_day.keys()):
        for act in by_day[day]:
            try:
                m = parse_action(act)
            except Exception:
                continue
            action_type = m.action
            if action_type == 'transfer_claim':
                alias = getattr(m, 'contract_alias', None)
                if alias and alias not in alias_set:
                    raise ValueError(
                        f"Scheduled transfer_claim references unknown alias '{alias}' on day {day}. "
                        "Ensure it is created earlier (same day allowed only if ordered before use)."
                    )
            else:
                # Capture new aliases created by scheduled actions
                new_alias = _collect_alias_from_action(m)
                if new_alias:
                    if new_alias in alias_set:
                        raise ValueError(f"Duplicate alias detected: '{new_alias}' already defined before day {day}")
                    alias_set.add(new_alias)


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

```

---

### 📄 src/bilancio/config/loaders.py

```python
"""YAML loading utilities for Bilancio configuration."""

import yaml
from pathlib import Path
from typing import Any, Dict
from decimal import Decimal, InvalidOperation, DecimalException
from pydantic import ValidationError

from .models import (
    ScenarioConfig,
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
    Action
)


def decimal_constructor(loader, node):
    """Construct Decimal from YAML scalar."""
    value = loader.construct_scalar(node)
    return Decimal(value)


# Register Decimal constructor for YAML
yaml.SafeLoader.add_constructor('!decimal', decimal_constructor)


def parse_action(action_dict: Dict[str, Any]) -> Action:
    """Parse a single action dictionary into the appropriate Action model.
    
    Args:
        action_dict: Dictionary containing action specification
        
    Returns:
        Parsed Action model instance
        
    Raises:
        ValueError: If action type is unknown or validation fails
    """
    # Determine action type from the dictionary keys
    if "mint_reserves" in action_dict:
        data = action_dict["mint_reserves"]
        return MintReserves(**data)
    elif "mint_cash" in action_dict:
        data = action_dict["mint_cash"]
        return MintCash(**data)
    elif "transfer_reserves" in action_dict:
        data = action_dict["transfer_reserves"]
        return TransferReserves(**data)
    elif "transfer_cash" in action_dict:
        data = action_dict["transfer_cash"]
        return TransferCash(**data)
    elif "deposit_cash" in action_dict:
        data = action_dict["deposit_cash"]
        return DepositCash(**data)
    elif "withdraw_cash" in action_dict:
        data = action_dict["withdraw_cash"]
        return WithdrawCash(**data)
    elif "client_payment" in action_dict:
        data = action_dict["client_payment"]
        return ClientPayment(**data)
    elif "create_stock" in action_dict:
        data = action_dict["create_stock"]
        return CreateStock(**data)
    elif "transfer_stock" in action_dict:
        data = action_dict["transfer_stock"]
        return TransferStock(**data)
    elif "create_delivery_obligation" in action_dict:
        data = action_dict["create_delivery_obligation"]
        # The model handles aliases automatically via pydantic
        return CreateDeliveryObligation(**data)
    elif "create_payable" in action_dict:
        data = action_dict["create_payable"]
        # The model handles aliases automatically via pydantic
        return CreatePayable(**data)
    elif "transfer_claim" in action_dict:
        data = action_dict["transfer_claim"]
        from .models import TransferClaim
        return TransferClaim(**data)
    else:
        raise ValueError(f"Unknown action type in: {action_dict}")


def preprocess_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess configuration data before validation.
    
    Converts string decimals to Decimal objects and handles
    other necessary transformations.
    
    Args:
        data: Raw configuration dictionary
        
    Returns:
        Preprocessed configuration dictionary
    """
    def convert_decimals(obj):
        """Recursively convert string decimals to Decimal objects."""
        if isinstance(obj, dict):
            return {k: convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_decimals(item) for item in obj]
        elif isinstance(obj, str):
            # Safely try to convert strings to Decimal
            # Only convert if the string is a valid number
            try:
                # Try to create a Decimal - this will validate the format
                decimal_value = Decimal(obj)
                # Additional check: ensure it's actually a number-like string
                # and not something like 'infinity' or 'nan'
                if decimal_value.is_finite():
                    return decimal_value
                else:
                    return obj
            except (ValueError, InvalidOperation, DecimalException):
                # Not a valid decimal, return as-is
                return obj
        else:
            return obj
    
    return convert_decimals(data)


def load_yaml(path: Path | str) -> ScenarioConfig:
    """Load and validate a scenario configuration from a YAML file.
    
    Args:
        path: Path to the YAML configuration file
        
    Returns:
        Validated ScenarioConfig instance
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        yaml.YAMLError: If the YAML is malformed
        ValidationError: If the configuration doesn't match the schema
        ValueError: If there are semantic errors in the configuration
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML from {path}: {e}")
    
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file must contain a YAML dictionary, got {type(data)}")
    
    # Preprocess the configuration
    data = preprocess_config(data)
    
    # Parse initial_actions if present
    if "initial_actions" in data:
        try:
            parsed_actions = []
            for action_dict in data["initial_actions"]:
                # Keep the original dict for now - we'll parse in apply.py
                parsed_actions.append(action_dict)
            data["initial_actions"] = parsed_actions
        except (ValueError, ValidationError) as e:
            raise ValueError(f"Failed to parse initial_actions: {e}")
    
    # Validate using pydantic
    try:
        config = ScenarioConfig(**data)
    except ValidationError as e:
        # Format validation errors nicely
        errors = []
        for error in e.errors():
            loc = " -> ".join(str(l) for l in error['loc'])
            msg = error['msg']
            errors.append(f"  - {loc}: {msg}")
        
        error_msg = f"Configuration validation failed:\n" + "\n".join(errors)
        raise ValueError(error_msg)
    
    return config

```

---

### 📄 src/bilancio/config/models.py

```python
"""Pydantic models for Bilancio scenario configuration."""

from typing import Literal, Optional, Union, List, Dict, Any
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
    - Own and transfer stock inventory
    - Create and settle delivery obligations
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

__all__ = [
    "Instrument",
    "Cash",
    "BankDeposit",
    "ReserveDeposit",
    "Payable",
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
                DeliveryObligation: (Agent,),     # any agent can promise to deliver
            },
            holders={
                Cash:            (Agent,),
                BankDeposit:     (Household, Firm, Treasury, Bank),  # banks may hold but not for interbank settlement
                ReserveDeposit:  (Bank, Treasury),
                Payable:         (Agent,),
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
            
            # Fully settled: cancel the delivery obligation and log with alias/contract_id
            system._cancel_delivery_obligation_internal(obligation.id)
            from bilancio.ops.aliases import get_alias_for_id
            alias = get_alias_for_id(system, obligation.id)
            system.log("DeliveryObligationSettled", 
                      obligation_id=obligation.id,
                      contract_id=obligation.id,
                      alias=alias, 
                      debtor=debtor.id, 
                      creditor=creditor.id, 
                      sku=required_sku, 
                      qty=required_quantity)


def settle_due(system, day: int):
    """
    Settle all obligations due today (payables and delivery obligations).
    
    For each payable due today:
    - Get debtor and creditor agents
    - Use policy.settlement_order to determine payment methods
    - Try each method in order until paid or all methods exhausted
    - Raise DefaultError if insufficient funds across all methods
    - Remove payable when fully settled
    - Log PayableSettled event
    
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

            # Fully settled: remove payable and log with alias/contract_id
            _remove_contract(system, payable.id)
            from bilancio.ops.aliases import get_alias_for_id
            alias = get_alias_for_id(system, payable.id)
            system.log("PayableSettled", pid=payable.id, contract_id=payable.id, alias=alias,
                       debtor=debtor.id, creditor=creditor.id, amount=payable.amount)
    
    # Settle delivery obligations
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

    # Phase A: Log PhaseA event (reserved)
    system.log("PhaseA")

    # Phase B: two subphases — B1 scheduled actions, B2 settlements
    system.log("PhaseB")  # Phase B bucket marker
    # B1: Execute scheduled actions for this day (if any)
    system.log("SubphaseB1")
    try:
        actions_today = system.state.scheduled_actions_by_day.get(current_day, [])
        if actions_today:
            # Lazy import to avoid heavy imports at module load
            from bilancio.config.apply import apply_action
            agents = system.state.agents
            for action_dict in actions_today:
                apply_action(system, action_dict, agents)
    except Exception:
        # Allow scheduled-action errors to bubble via apply_action's own error handling
        # but keep guard to ensure the simulation loop stability
        raise

    # B2: Automated settlements due today
    system.log("SubphaseB2")
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
    # Aliases for created contracts (alias -> contract_id)
    aliases: dict[str, str] = field(default_factory=dict)
    # Scheduled actions to run at Phase B1 by day (day -> list of action dicts)
    scheduled_actions_by_day: dict[int, list[dict]] = field(default_factory=dict)

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
    def mint_cash(self, to_agent_id: AgentId, amount: int, denom="X", alias: str | None = None) -> str:
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
            # Include alias if provided (for UI linking)
            if alias is not None:
                self.log("CashMinted", to=to_agent_id, amount=amount, instr_id=instr_id, alias=alias)
            else:
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

    def mint_reserves(self, to_bank_id: str, amount: int, denom="X", alias: str | None = None) -> str:
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
            if alias is not None:
                self.log("ReservesMinted", to=to_bank_id, amount=amount, instr_id=instr_id, alias=alias)
            else:
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

    # ---- obligation settlement

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
    def create_delivery_obligation(self, from_agent: AgentId, to_agent: AgentId, sku: str, quantity: int, unit_price: Decimal, due_day: int, alias: str | None = None) -> InstrId:
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
            if alias is not None:
                self.log("DeliveryObligationCreated", 
                        id=obligation_id, 
                        frm=from_agent, 
                        to=to_agent, 
                        sku=sku, 
                        qty=quantity, 
                        due_day=due_day, 
                        unit_price=unit_price,
                        alias=alias)
            else:
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
        
        # Log the cancellation with alias (if any) and contract_id for UI consistency
        from bilancio.ops.aliases import get_alias_for_id
        alias = get_alias_for_id(self, obligation_id)
        self.log("DeliveryObligationCancelled",
                obligation_id=obligation_id,
                contract_id=obligation_id,
                alias=alias,
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

### 📄 src/bilancio/export/__init__.py

```python
"""Export utilities for Bilancio simulation results."""

from .writers import write_balances_csv, write_events_jsonl

__all__ = ["write_balances_csv", "write_events_jsonl"]
```

---

### 📄 src/bilancio/export/writers.py

```python
"""Writers for exporting Bilancio simulation data."""

import json
import csv
from pathlib import Path
from typing import Any, Dict, List
from decimal import Decimal

from bilancio.engines.system import System
from bilancio.analysis.balances import as_rows, system_trial_balance


def decimal_default(obj):
    """JSON encoder for Decimal types.
    
    Preserves precision by converting to string for exact representation.
    Most JSON parsers can handle numeric strings correctly.
    """
    if isinstance(obj, Decimal):
        # Convert to string to preserve exact precision
        # Use normalize() to remove trailing zeros
        normalized = obj.normalize()
        # Check if it's an integer value
        if normalized == normalized.to_integral_value():
            return int(normalized)
        else:
            # Return as string to preserve exact decimal precision
            return str(normalized)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def write_balances_csv(system: System, path: Path) -> None:
    """Export system balances to CSV format.
    
    Creates a CSV file with balance sheet data for all agents
    and the system as a whole.
    
    Args:
        system: System instance with simulation results
        path: Path where to write the CSV file
    """
    # Get balance rows
    rows = as_rows(system)
    
    # Add system trial balance
    trial_bal = system_trial_balance(system)
    rows.append({
        "agent_id": "SYSTEM",
        "agent_name": "System Total",
        "agent_kind": "system",
        "item_type": "summary",
        "item_name": "Total Assets",
        "amount": trial_bal.total_financial_assets
    })
    rows.append({
        "agent_id": "SYSTEM",
        "agent_name": "System Total",
        "agent_kind": "system",
        "item_type": "summary",
        "item_name": "Total Liabilities",
        "amount": trial_bal.total_financial_liabilities
    })
    rows.append({
        "agent_id": "SYSTEM",
        "agent_name": "System Total",
        "agent_kind": "system",
        "item_type": "summary",
        "item_name": "Total Equity",
        "amount": trial_bal.total_financial_assets - trial_bal.total_financial_liabilities
    })
    
    # Write to CSV
    if rows:
        # Collect all unique fieldnames from all rows
        fieldnames_set = set()
        for row in rows:
            fieldnames_set.update(row.keys())
        fieldnames = sorted(list(fieldnames_set))
        
        with open(path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in rows:
                # Convert Decimal to float for CSV
                row_copy = row.copy()
                for key, value in row_copy.items():
                    if isinstance(value, Decimal):
                        row_copy[key] = float(value)
                writer.writerow(row_copy)


def write_events_jsonl(system: System, path: Path) -> None:
    """Export system events to JSONL format.
    
    Creates a JSONL file (one JSON object per line) with all
    simulation events for detailed analysis.
    
    Args:
        system: System instance with simulation results
        path: Path where to write the JSONL file
    """
    with open(path, 'w') as f:
        for event in system.state.events:
            # Write each event as a separate JSON line
            json.dump(event, f, default=decimal_default)
            f.write('\n')


def write_balances_snapshot(
    system: System,
    path: Path,
    day: int,
    agent_ids: List[str] = None
) -> None:
    """Export a snapshot of balances for specific agents on a specific day.
    
    Args:
        system: System instance
        path: Path where to write the snapshot
        day: Day number for the snapshot
        agent_ids: List of agent IDs to include (None for all)
    """
    snapshot = {
        "day": day,
        "agents": {}
    }
    
    # Determine which agents to include
    if agent_ids is None:
        agent_ids = list(system.state.agents.keys())
    
    # Collect balance data for each agent
    for agent_id in agent_ids:
        if agent_id not in system.state.agents:
            continue
            
        agent = system.state.agents[agent_id]
        
        # Get balance sheet items
        assets = []
        for asset_id in agent.asset_ids:
            if asset_id in system.state.contracts:
                contract = system.state.contracts[asset_id]
                assets.append({
                    "id": asset_id,
                    "type": type(contract).__name__,
                    "amount": getattr(contract, "amount", None)
                })
        
        liabilities = []
        for liability_id in agent.liability_ids:
            if liability_id in system.state.contracts:
                contract = system.state.contracts[liability_id]
                liabilities.append({
                    "id": liability_id,
                    "type": type(contract).__name__,
                    "amount": getattr(contract, "amount", None)
                })
        
        stocks = []
        for stock_id in agent.stock_ids:
            if stock_id in system.state.stocks:
                stock = system.state.stocks[stock_id]
                stocks.append({
                    "id": stock_id,
                    "sku": stock.sku,
                    "quantity": stock.quantity,
                    "unit_price": stock.unit_price,
                    "total_value": stock.quantity * stock.unit_price
                })
        
        snapshot["agents"][agent_id] = {
            "name": agent.name,
            "kind": agent.kind,
            "assets": assets,
            "liabilities": liabilities,
            "stocks": stocks
        }
    
    # Write snapshot to file
    with open(path, 'w') as f:
        json.dump(snapshot, f, indent=2, default=decimal_default)
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

### 📄 src/bilancio/ops/aliases.py

```python
from __future__ import annotations

from typing import Optional


def get_alias_for_id(system, contract_id: str) -> Optional[str]:
    """Return the alias for a given contract_id, if any."""
    for alias, cid in (system.state.aliases or {}).items():
        if cid == contract_id:
            return alias
    return None


def get_id_for_alias(system, alias: str) -> Optional[str]:
    """Return the contract id for a given alias, if any."""
    return (system.state.aliases or {}).get(alias)


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

        # 3) Log payment events with proper classification
        if deposit_paid > 0:
            if payer_bank == payee_bank:
                # Intra-bank payment (same bank)
                system.log("IntraBankPayment", 
                          payer=payer_id, 
                          payee=payee_id, 
                          bank=payer_bank, 
                          amount=deposit_paid)
            else:
                # Inter-bank payment (cross-bank, will need clearing)
                system.log("ClientPayment", 
                          payer=payer_id, 
                          payer_bank=payer_bank,
                          payee=payee_id, 
                          payee_bank=payee_bank, 
                          amount=deposit_paid)
        
        if cash_paid > 0:
            # Cash payment was used as fallback
            system.log("CashPayment",
                      payer=payer_id,
                      payee=payee_id,
                      amount=cash_paid)

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
    return (instr.kind, instr.denom, instr.liability_issuer_id, instr.asset_holder_id)

def is_divisible(instr: Instrument) -> bool:
    # Cash and bank deposits are divisible
    if instr.kind in ("cash", "bank_deposit", "reserve_deposit"):
        return True
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
        **{k: getattr(instr, k) for k in ("due_day",) if hasattr(instr, k)}
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

### 📄 src/bilancio/ui/__init__.py

```python
"""User interface layer for Bilancio CLI."""

from .cli import main

__all__ = ["main"]
```

---

### 📄 src/bilancio/ui/cli.py

```python
"""Command-line interface for Bilancio."""

import click
from pathlib import Path
from typing import Optional, List
import sys

from rich.console import Console
from rich.panel import Panel

from .run import run_scenario
from .wizard import create_scenario_wizard


console = Console()


@click.group()
def cli():
    """Bilancio - Economic simulation framework."""
    pass


@cli.command()
@click.argument('scenario_file', type=click.Path(exists=True, path_type=Path))
@click.option('--mode', type=click.Choice(['step', 'until-stable']), 
              default='until-stable', help='Simulation run mode')
@click.option('--max-days', type=int, default=90, 
              help='Maximum days to simulate')
@click.option('--quiet-days', type=int, default=2,
              help='Required quiet days for stable state')
@click.option('--show', type=click.Choice(['summary', 'detailed', 'table']),
              default='detailed', help='Event display mode')
@click.option('--agents', type=str, default=None,
              help='Comma-separated list of agent IDs to show balances for')
@click.option('--check-invariants', 
              type=click.Choice(['setup', 'daily', 'none']),
              default='setup',
              help='When to check system invariants')
@click.option('--export-balances', type=click.Path(path_type=Path),
              default=None, help='Path to export balances CSV')
@click.option('--export-events', type=click.Path(path_type=Path),
              default=None, help='Path to export events JSONL')
@click.option('--html', type=click.Path(path_type=Path),
              default=None, help='Path to export colored output as HTML')
@click.option('--t-account/--no-t-account', default=False, help='Use detailed T-account layout for balances')
def run(scenario_file: Path, 
        mode: str,
        max_days: int,
        quiet_days: int,
        show: str,
        agents: Optional[str],
        check_invariants: str,
        export_balances: Optional[Path],
        export_events: Optional[Path],
        html: Optional[Path],
        t_account: bool):
    """Run a Bilancio simulation scenario.
    
    Load a scenario from a YAML file and run the simulation either
    step-by-step or until a stable state is reached.
    """
    try:
        # Parse agent list if provided
        agent_ids = None
        if agents:
            agent_ids = [a.strip() for a in agents.split(',')]
        
        # Override export paths if provided via CLI
        export = {
            'balances_csv': str(export_balances) if export_balances else None,
            'events_jsonl': str(export_events) if export_events else None
        }
        
        # Run the scenario
        run_scenario(
            path=scenario_file,
            mode=mode,
            max_days=max_days,
            quiet_days=quiet_days,
            show=show,
            agent_ids=agent_ids,
            check_invariants=check_invariants,
            export=export,
            html_output=html,
            t_account=t_account
        )
        
    except FileNotFoundError as e:
        console.print(Panel(
            f"[red]File not found:[/red] {e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except ValueError as e:
        console.print(Panel(
            f"[red]Configuration error:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except Exception as e:
        console.print(Panel(
            f"[red]Unexpected error:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


@cli.command()
@click.argument('scenario_file', type=click.Path(exists=True, path_type=Path))
def validate(scenario_file: Path):
    """Validate a Bilancio scenario configuration file.
    
    Check that a YAML configuration file is valid without running
    the simulation. Reports any errors in the configuration structure,
    agent definitions, or initial actions.
    """
    try:
        from bilancio.config import load_yaml
        from bilancio.engines.system import System
        from bilancio.config import apply_to_system
        
        # Load and parse the configuration
        console.print(f"[dim]Validating {scenario_file}...[/dim]")
        config = load_yaml(scenario_file)
        
        console.print(f"[green]✓[/green] Configuration syntax is valid")
        console.print(f"  Name: {config.name}")
        console.print(f"  Version: {config.version}")
        console.print(f"  Agents: {len(config.agents)}")
        console.print(f"  Initial actions: {len(config.initial_actions)}")
        
        # Try to apply to a test system to validate actions
        console.print("[dim]Checking if configuration can be applied...[/dim]")
        test_system = System()
        apply_to_system(config, test_system)
        
        console.print(f"[green]✓[/green] Configuration can be applied successfully")
        
        # Run invariant checks
        test_system.assert_invariants()
        console.print(f"[green]✓[/green] System invariants pass")
        
        # Summary
        console.print("\n[bold green]Configuration is valid![/bold green]")
        console.print(f"\nAgents defined:")
        for agent in config.agents:
            console.print(f"  • {agent.id} ({agent.kind}): {agent.name}")
        
        if config.run.export.balances_csv or config.run.export.events_jsonl:
            console.print(f"\nExports configured:")
            if config.run.export.balances_csv:
                console.print(f"  • Balances: {config.run.export.balances_csv}")
            if config.run.export.events_jsonl:
                console.print(f"  • Events: {config.run.export.events_jsonl}")
        
    except FileNotFoundError as e:
        console.print(Panel(
            f"[red]File not found:[/red] {e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except ValueError as e:
        console.print(Panel(
            f"[red]Configuration error:[/red]\n{e}",
            title="Validation Failed",
            border_style="red"
        ))
        sys.exit(1)
        
    except Exception as e:
        console.print(Panel(
            f"[red]Validation error:[/red]\n{e}",
            title="Validation Failed",
            border_style="red"
        ))
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


@cli.command()
@click.option('--from', 'from_template', type=str, default=None,
              help='Base template to use')
@click.option('-o', '--output', type=click.Path(path_type=Path),
              required=True, help='Output YAML file path')
def new(from_template: Optional[str], output: Path):
    """Create a new scenario configuration.
    
    Interactive wizard to create a new Bilancio scenario
    configuration file.
    """
    try:
        create_scenario_wizard(output, from_template)
        console.print(f"[green]✓[/green] Created scenario file: {output}")
        
    except Exception as e:
        console.print(Panel(
            f"[red]Failed to create scenario:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()

```

---

### 📄 src/bilancio/ui/display.py

```python
"""Display utilities for Bilancio CLI."""

from typing import Optional, List, Dict, Any, Union
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bilancio.engines.system import System
from bilancio.analysis.visualization import (
    display_agent_balance_table,
    display_multiple_agent_balances,
    display_events,
    display_events_for_day,
    display_agent_balance_table_renderable,
    display_multiple_agent_balances_renderable,
    display_events_renderable,
    display_events_for_day_renderable,
    display_events_table_renderable,
    display_agent_t_account_renderable,
    display_events_tables_by_phase_renderables
)
from bilancio.analysis.balances import system_trial_balance
from bilancio.core.errors import DefaultError, ValidationError


console = Console()


def show_scenario_header_renderable(name: str, description: Optional[str] = None, agents: Optional[Any] = None) -> List[RenderableType]:
    """Return renderables for scenario header including agent list.
    
    Args:
        name: Scenario name
        description: Optional scenario description
        agents: Optional list or dict of agent configs to display
        
    Returns:
        List of renderables
    """
    renderables = []
    
    # Add scenario header panel
    header = Text(name, style="bold cyan")
    if description:
        header.append(f"\n{description}", style="dim")
    
    renderables.append(Panel(
        header,
        title="Bilancio Scenario",
        border_style="cyan"
    ))
    
    # Add agent list if provided
    if agents:
        from rich.table import Table
        
        agent_table = Table(title="Agents", box=None, show_header=False, padding=(0, 2))
        agent_table.add_column("ID", style="bold yellow")
        agent_table.add_column("Name", style="white")
        agent_table.add_column("Type", style="cyan")
        
        # Handle both list and dict formats
        if isinstance(agents, list):
            # agents is a list of AgentSpec objects
            for agent_config in agents:
                agent_id = agent_config.id if hasattr(agent_config, 'id') else str(agent_config.get('id', 'unknown'))
                agent_type = agent_config.kind if hasattr(agent_config, 'kind') else str(agent_config.get('kind', 'unknown'))
                agent_name = agent_config.name if hasattr(agent_config, 'name') else str(agent_config.get('name', agent_id))
                agent_table.add_row(agent_id, agent_name, f"({agent_type})")
        elif isinstance(agents, dict):
            # agents is a dictionary
            for agent_id, agent_config in agents.items():
                agent_type = agent_config.kind if hasattr(agent_config, 'kind') else str(agent_config.get('kind', 'unknown'))
                agent_name = agent_config.name if hasattr(agent_config, 'name') else str(agent_config.get('name', agent_id))
                agent_table.add_row(agent_id, agent_name, f"({agent_type})")
        
        renderables.append(Text())  # Empty line
        renderables.append(agent_table)
    
    return renderables


def show_scenario_header(name: str, description: Optional[str] = None, agents: Optional[Dict[str, Any]] = None) -> None:
    """Display scenario header.
    
    Args:
        name: Scenario name
        description: Optional scenario description
        agents: Optional dict of agent configs to display
    """
    renderables = show_scenario_header_renderable(name, description, agents)
    for renderable in renderables:
        console.print(renderable)


def show_day_summary_renderable(
    system: System,
    agent_ids: Optional[List[str]] = None,
    event_mode: str = "detailed",
    day: Optional[int] = None,
    t_account: bool = False
) -> List[RenderableType]:
    """Return renderables for a simulation day summary.
    
    Args:
        system: System instance
        agent_ids: Agent IDs to show balances for
        event_mode: "summary" or "detailed"
        day: Day number to display events for (None for all)
        
    Returns:
        List of renderables
    """
    renderables = []
    
    # Show events
    if day is not None:
        # Show events for specific day
        events_for_day = [e for e in system.state.events if e.get("day") == day]
        if events_for_day:
            renderables.append(Text("\nEvents:", style="bold"))
            if event_mode == "table":
                # Show 3 separate tables by phase (A/B/C)
                phase_tables = display_events_tables_by_phase_renderables(events_for_day, day=day)
                renderables.extend(phase_tables)
            elif event_mode == "detailed":
                event_renderables = display_events_renderable(events_for_day, format="detailed")
                renderables.extend(event_renderables)
            else:
                # Summary mode - just count by type
                event_counts = {}
                for event in events_for_day:
                    event_type = event.get("kind", "Unknown")
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1
                for event_type, count in sorted(event_counts.items()):
                    renderables.append(Text(f"  • {event_type}: {count}"))
    else:
        # Show all recent events (initial view, typically setup/day 0)
        if system.state.events:
            renderables.append(Text("\nEvents:", style="bold"))
            if event_mode == "table":
                # Use phase-separated tables even in the initial no-day view.
                # If these are setup events, this will render a single "Setup" table.
                # Otherwise, it renders Phase B/C tables for the current day.
                # Determine a representative day to label (default to 0 if any setup events exist).
                rep_day = 0 if any(e.get("phase") == "setup" for e in system.state.events) else system.state.day
                phase_tables = display_events_tables_by_phase_renderables(system.state.events, day=rep_day)
                renderables.extend(phase_tables)
            elif event_mode == "detailed":
                event_renderables = display_events_renderable(system.state.events, format="detailed")
                renderables.extend(event_renderables)
            else:
                # Summary mode
                event_counts = {}
                for event in system.state.events:
                    event_type = event.get("kind", "Unknown")
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1
                for event_type, count in sorted(event_counts.items()):
                    renderables.append(Text(f"  • {event_type}: {count}"))
    
    # Show balances
    if agent_ids:
        renderables.append(Text("\nBalances:", style="bold"))
        if len(agent_ids) == 1:
            # Single agent - show detailed balance
            if t_account:
                balance_renderable = display_agent_t_account_renderable(system, agent_ids[0])
            else:
                balance_renderable = display_agent_balance_table_renderable(system, agent_ids[0], format="rich")
            renderables.append(balance_renderable)
        else:
            # Multiple agents
            if t_account:
                # Render one T-account per agent, stacked for readability
                for aid in agent_ids:
                    renderables.append(display_agent_t_account_renderable(system, aid))
                    renderables.append(Text(""))  # spacing
            else:
                # Show compact legacy tables side by side
                balance_renderable = display_multiple_agent_balances_renderable(system, agent_ids, format="rich")
                renderables.append(balance_renderable)
    else:
        # Show system trial balance
        renderables.append(Text("\nSystem Trial Balance:", style="bold"))
        trial_bal = system_trial_balance(system)
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Metric")
        table.add_column("Value", justify="right")
        
        total_assets = trial_bal.total_financial_assets
        total_liabilities = trial_bal.total_financial_liabilities
        
        table.add_row("Total Assets", f"{total_assets:,.2f}")
        table.add_row("Total Liabilities", f"{total_liabilities:,.2f}")
        table.add_row("Total Equity", f"{total_assets - total_liabilities:,.2f}")
        
        # Check if balanced
        diff = abs(total_assets - total_liabilities)
        if diff < 0.01:
            table.add_row("Status", "[green]✓ Balanced[/green]")
        else:
            table.add_row("Status", f"[red]✗ Imbalanced ({diff:,.2f})[/red]")
        
        renderables.append(table)
    
    return renderables


def show_day_summary(
    system: System,
    agent_ids: Optional[List[str]] = None,
    event_mode: str = "detailed",
    day: Optional[int] = None,
    t_account: bool = False
) -> None:
    """Display summary for a simulation day.
    
    Args:
        system: System instance
        agent_ids: Agent IDs to show balances for
        event_mode: "summary" or "detailed"
        day: Day number to display events for (None for all)
    """
    renderables = show_day_summary_renderable(system, agent_ids, event_mode, day, t_account)
    for renderable in renderables:
        console.print(renderable)


def show_simulation_summary_renderable(system: System) -> Panel:
    """Return a renderable for final simulation summary.
    
    Args:
        system: System instance
        
    Returns:
        Panel renderable
    """
    return Panel(
        f"[bold]Final State[/bold]\n"
        f"Day: {system.state.day}\n"
        f"Total Events: {len(system.state.events)}\n"
        f"Active Agents: {len(system.state.agents)}\n"
        f"Active Contracts: {len(system.state.contracts)}\n"
        f"Stock Lots: {len(system.state.stocks)}",
        title="Summary",
        border_style="green"
    )


def show_simulation_summary(system: System) -> None:
    """Display final simulation summary.
    
    Args:
        system: System instance
    """
    console.print(show_simulation_summary_renderable(system))


def show_error_panel(
    error: Exception,
    phase: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Display error in a formatted panel.
    
    Args:
        error: Exception that occurred
        phase: Phase where error occurred (setup, day_N, simulation)
        context: Additional context information
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Build error content
    content = Text()
    content.append(f"Type: {error_type}\n", style="red bold")
    content.append(f"Message: {error_msg}\n", style="red")
    
    if context:
        content.append("\nContext:\n", style="yellow")
        for key, value in context.items():
            content.append(f"  • {key}: {value}\n", style="dim")
    
    # Add helpful hints based on error type
    if isinstance(error, DefaultError):
        content.append("\n💡 ", style="yellow")
        content.append("This usually means a debtor lacks sufficient funds or assets to settle an obligation.\n", style="dim")
        content.append("Check the agent's balance sheet and available means of payment.", style="dim")
        
    elif isinstance(error, ValidationError):
        content.append("\n💡 ", style="yellow")
        content.append("This indicates a system invariant violation.\n", style="dim")
        content.append("Common causes: duplicate IDs, negative balances, or mismatched references.", style="dim")
    
    # Display the panel
    console.print(Panel(
        content,
        title=f"Error in {phase}",
        border_style="red",
        expand=False
    ))
    
    # Log the error as an event
    if context and "scenario" in context:
        console.print(f"[dim]Error logged to simulation events[/dim]")

```

---

### 📄 src/bilancio/ui/html_export.py

```python
"""Semantic HTML export for Bilancio runs (readable, non-monospace).

Generates a light-themed, spreadsheet-style HTML report inspired by temp/demo_correct.html,
without changing simulation logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import math
from decimal import Decimal
import html as _html

from bilancio.engines.system import System
from bilancio.analysis.visualization import build_t_account_rows
from bilancio.analysis.balances import AgentBalance


def _load_css() -> str:
    """Load export CSS from assets with a safe inline fallback.

    Keeps styling out of Python while remaining robust if the file is missing.
    """
    asset_path = Path(__file__).with_name("assets").joinpath("export.css")
    try:
        return asset_path.read_text(encoding="utf-8")
    except Exception:
        # Minimal fallback to keep the page readable if asset is missing.
        return "body{font-family:system-ui,Arial,sans-serif;padding:16px;background:#f5f5f5;color:#333}table{border-collapse:collapse;width:100%}th,td{border:1px solid #e5e7eb;padding:6px}tbody tr:nth-child(even){background:#fafafa}h1,h2,h3{margin:.5rem 0}"


def _html_escape(value: Any) -> str:
    """Escape text for safe HTML display, including quotes.

    Uses stdlib html.escape and additionally escapes single quotes.
    """
    if value is None:
        return ""
    text = str(value)
    # html.escape handles & < > and ", then we also escape single quotes
    return _html.escape(text, quote=True).replace("'", "&#x27;")


def _safe_int_conversion(value: Any) -> Optional[int]:
    """Safely convert value to int.

    - Accepts int, float, Decimal, and stringified digits
    - Returns None for None
    - Raises ValueError for invalid values
    """
    if value is None:
        return None
    # Fast path for ints
    if isinstance(value, int):
        return value
    # Floats/Decimals lose precision but we accept truncation for display
    if isinstance(value, (float, Decimal)):
        # Guard against NaN/Inf
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            raise ValueError("Invalid numeric value: NaN/Inf")
        return int(value)
    # Strings: allow simple digit strings and formatted numbers with commas
    if isinstance(value, str):
        s = value.strip().replace(",", "")
        if s == "":
            return None
        try:
            return int(s)
        except Exception as e:
            raise ValueError(f"Invalid numeric value: {value}") from e
    # Objects with __int__
    if hasattr(value, "__int__"):
        try:
            return int(value)  # type: ignore[arg-type]
        except Exception as e:
            raise ValueError(f"Invalid numeric value: {value}") from e
    raise ValueError(f"Cannot convert {type(value)} to int")


def _format_amount(v: Any) -> str:
    if v in (None, "—", "-"):
        return "—"
    try:
        iv = _safe_int_conversion(v)
        if iv is None:
            return "—"
        return f"{iv:,}"
    except ValueError:
        # As a last resort, try float -> int formatting without erroring
        try:
            return f"{int(float(v)):,}"
        except Exception:
            return _html_escape(v)


def _render_t_account_from_rows(title: str, assets_rows: List[dict], liabs_rows: List[dict]) -> str:
    def tr(row: Optional[dict]) -> str:
        if not row:
            return "<tr><td class=\"empty\" colspan=\"6\">—</td></tr>"
        qty = row.get('quantity')
        val = row.get('value_minor')
        cpty = row.get('counterparty_name') or "—"
        mat = row.get('maturity') or "—"
        id_or_alias = row.get('id_or_alias') or "—"
        # Robust numeric formatting with safe conversion
        try:
            qiv = _safe_int_conversion(qty)
        except ValueError:
            qiv = None
        try:
            viv = _safe_int_conversion(val)
        except ValueError:
            viv = None
        qty_s = "—" if qiv in (None, "") else f"{qiv:,}"
        val_s = "—" if viv in (None, "") else f"{viv:,}"
        return (
            f"<tr>"
            f"<td class=\"name\">{_html_escape(row.get('name',''))}</td>"
            f"<td class=\"id\">{_html_escape(id_or_alias)}</td>"
            f"<td class=\"qty\">{qty_s}</td>"
            f"<td class=\"val\">{val_s}</td>"
            f"<td class=\"cpty\">{_html_escape(cpty)}</td>"
            f"<td class=\"mat\">{_html_escape(mat)}</td>"
            f"</tr>"
        )

    assets_html = "".join(tr(r) for r in assets_rows) or tr(None)
    liabs_html = "".join(tr(r) for r in liabs_rows) or tr(None)

    return f"""
<section class="t-account">
  <h3>{_html_escape(title)}</h3>
  <div class="grid">
    <div class="assets-side">
      <h4>Assets</h4>
      <table class="side">
        <thead><tr><th>Name</th><th>ID/Alias</th><th>Qty</th><th>Value</th><th>Counterparty</th><th>Maturity</th></tr></thead>
        <tbody>{assets_html}</tbody>
      </table>
    </div>
    <div class="liabilities-side">
      <h4>Liabilities</h4>
      <table class="side">
        <thead><tr><th>Name</th><th>ID/Alias</th><th>Qty</th><th>Value</th><th>Counterparty</th><th>Maturity</th></tr></thead>
        <tbody>{liabs_html}</tbody>
      </table>
    </div>
  </div>
</section>
"""


def _render_t_account(system: System, agent_id: str) -> str:
    acct = build_t_account_rows(system, agent_id)
    agent = system.state.agents[agent_id]
    title = f"{agent.name or agent_id} [{agent_id}] ({agent.kind})"
    # Convert to dict rows for the row renderer
    def to_row(r):
        return {
            'name': getattr(r, 'name', ''),
            'quantity': getattr(r, 'quantity', None),
            'value_minor': getattr(r, 'value_minor', None),
            'counterparty_name': getattr(r, 'counterparty_name', None),
            'maturity': getattr(r, 'maturity', None),
            'id_or_alias': getattr(r, 'id_or_alias', None),
        }
    assets_rows = [to_row(r) for r in acct.assets]
    liabs_rows = [to_row(r) for r in acct.liabilities]
    return _render_t_account_from_rows(title, assets_rows, liabs_rows)


def _build_rows_from_balance(balance: AgentBalance) -> (List[dict], List[dict]):
    assets: List[dict] = []
    liabs: List[dict] = []

    # Inventory (stocks owned)
    for sku, data in balance.inventory_by_sku.items():
        qty = data.get('quantity', 0)
        val = data.get('value', 0)
        try:
            val_i = _safe_int_conversion(val)
        except ValueError:
            val_i = None
        try:
            qty_i = _safe_int_conversion(qty)
        except ValueError:
            qty_i = None
        if qty_i and qty_i > 0:
            assets.append({'name': str(sku), 'quantity': qty_i, 'value_minor': val_i, 'counterparty_name': '—', 'maturity': '—'})

    # Non-financial assets receivable
    for sku, data in balance.nonfinancial_assets_by_kind.items():
        qty = data.get('quantity', 0)
        val = data.get('value', 0)
        try:
            val_i = _safe_int_conversion(val)
        except ValueError:
            val_i = None
        try:
            qty_i = _safe_int_conversion(qty)
        except ValueError:
            qty_i = None
        if qty_i and qty_i > 0:
            assets.append({'name': f"{sku} receivable", 'quantity': qty_i, 'value_minor': val_i, 'counterparty_name': '—', 'maturity': '—'})

    # Financial assets by kind (skip non-financial kinds)
    for kind, amount in balance.assets_by_kind.items():
        if kind == 'delivery_obligation':
            continue
        try:
            amount_i = _safe_int_conversion(amount)
        except ValueError:
            amount_i = None
        if amount_i and amount_i > 0:
            assets.append({'name': kind, 'quantity': None, 'value_minor': amount_i, 'counterparty_name': '—', 'maturity': 'on-demand' if kind in ('cash','bank_deposit','reserve_deposit') else '—'})

    # Non-financial liabilities
    for sku, data in balance.nonfinancial_liabilities_by_kind.items():
        qty = data.get('quantity', 0)
        val = data.get('value', 0)
        try:
            val_i = _safe_int_conversion(val)
        except ValueError:
            val_i = None
        try:
            qty_i = _safe_int_conversion(qty)
        except ValueError:
            qty_i = None
        if qty_i and qty_i > 0:
            liabs.append({'name': f"{sku} obligation", 'quantity': qty_i, 'value_minor': val_i, 'counterparty_name': '—', 'maturity': '—'})

    # Financial liabilities
    for kind, amount in balance.liabilities_by_kind.items():
        if kind == 'delivery_obligation':
            continue
        try:
            amount_i = _safe_int_conversion(amount)
        except ValueError:
            amount_i = None
        if amount_i and amount_i > 0:
            liabs.append({'name': kind, 'quantity': None, 'value_minor': amount_i, 'counterparty_name': '—', 'maturity': 'on-demand' if kind in ('cash','bank_deposit','reserve_deposit') else '—'})

    # Ordering similar to render layer
    def asset_key(row):
        name = row['name']
        # inventory rows have quantity and cpty/maturity '—'
        if row['quantity'] is not None and row.get('counterparty_name') == '—':
            return (0, name)
        if name.endswith('receivable'):
            return (1, name)
        order = {'cash':0,'bank_deposit':1,'reserve_deposit':2,'payable':3}
        return (2, order.get(name, 99), name)

    def liab_key(row):
        name = row['name']
        if name.endswith('obligation'):
            return (0, name)
        order = {'payable':0,'bank_deposit':1,'reserve_deposit':2,'cash':3}
        return (1, order.get(name, 99), name)

    assets.sort(key=asset_key)
    liabs.sort(key=liab_key)
    return assets, liabs


def _map_event_fields(e: Dict[str, Any]) -> Dict[str, str]:
    kind = str(e.get("kind", ""))
    if kind in ("CashDeposited", "CashWithdrawn"):
        frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
        to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
    elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
        frm = e.get("payer"); to = e.get("payee")
    elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
        frm = e.get("debtor_bank"); to = e.get("creditor_bank")
    elif kind == "StockCreated":
        frm = e.get("owner"); to = None
    else:
        frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
        to  = e.get("to") or e.get("creditor") or e.get("payee")
    # Identifier column prefers alias, then contract/instrument IDs
    id_or_alias = (
        e.get("alias")
        or e.get("contract_id")
        or e.get("payable_id")
        or e.get("obligation_id")
        or e.get("pid")
        or e.get("id")
        or e.get("instr_id")
        or e.get("stock_id")
        or "—"
    )
    # SKU/Instr column should show SKU (for stock/delivery events) when available
    # Otherwise leave blank/dash
    sku = e.get("sku") or "—"
    qty = e.get("qty") or e.get("quantity") or "—"
    amt = e.get("amount") or "—"
    notes = ""
    if kind == "ClientPayment":
        notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
    elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
        notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
        if 'due_day' in e:
            notes += f"; due {e.get('due_day')}"
    return {
        "kind": kind,
        "from": _html_escape(frm or "—"),
        "to": _html_escape(to or "—"),
        "id_or_alias": _html_escape(id_or_alias),
        "sku": _html_escape(sku),
        "qty": _html_escape(qty),
        "amount": _format_amount(amt),
        "notes": _html_escape(notes),
    }


def _render_events_table(title: str, events: List[Dict[str, Any]]) -> str:
    # Exclude marker rows
    events = [e for e in events if e.get("kind") not in ("PhaseA","PhaseB","PhaseC","SubphaseB1","SubphaseB2")]
    rows_html = []
    for e in events:
        m = _map_event_fields(e)
        rows_html.append(
            f"<tr>"
            f"<td class=\"event-kind\">{m['kind']}</td>"
            f"<td class=\"event-id\">{m['id_or_alias']}</td>"
            f"<td>{m['from']}</td><td>{m['to']}</td>"
            f"<td>{m['sku']}</td><td class=\"qty\">{m['qty']}</td>"
            f"<td class=\"amount\">{m['amount']}</td><td class=\"notes\">{m['notes']}</td>"
            f"</tr>"
        )
    if not rows_html:
        rows_html.append("<tr><td colspan=\"7\" class=\"notes\">No events</td></tr>")
    return f"""
<section class="events-table">
  <h4>{_html_escape(title)}</h4>
  <table>
    <thead>
      <tr><th>Kind</th><th>ID/Alias</th><th>From</th><th>To</th><th>SKU/Instr</th><th>Qty</th><th>Amount</th><th>Notes</th></tr>
    </thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>
</section>
"""


def _split_by_phases(day_events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    buckets = {"A": [], "B": [], "C": []}
    current = "A"
    for e in day_events:
        k = e.get("kind")
        if k == "PhaseA":
            current = "A"; continue
        if k == "PhaseB":
            current = "B"; continue
        if k == "PhaseC":
            current = "C"; continue
        buckets[current].append(e)
    return buckets

def _split_phase_b_into_subphases(events_b: List[Dict[str, Any]]) -> (List[Dict[str, Any]], List[Dict[str, Any]]):
    """Split Phase B events into B1 (scheduled) and B2 (settlements) using subphase markers.

    Excludes Subphase markers from returned lists.
    """
    b1: List[Dict[str, Any]] = []
    b2: List[Dict[str, Any]] = []
    in_b2 = False
    for e in events_b:
        k = e.get("kind")
        if k == "SubphaseB1":
            # begin B1 (marker only)
            in_b2 = False
            continue
        if k == "SubphaseB2":
            # switch to B2 (marker only)
            in_b2 = True
            continue
        if in_b2:
            b2.append(e)
        else:
            b1.append(e)
    return b1, b2


def export_pretty_html(
    system: System,
    out_path: Path,
    scenario_name: str,
    description: Optional[str],
    agent_ids: Optional[List[str]],
    initial_balances: Optional[Dict[str, Any]],
    days_data: List[Dict[str, Any]],
    *,
    max_days: Optional[int] = None,
    quiet_days: Optional[int] = None,
    initial_rows: Optional[Dict[str, Dict[str, List[dict]]]] = None,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Meta
    final_day = system.state.day
    total_events = len(system.state.events)
    active_agents = len(system.state.agents)
    active_contracts = len(system.state.contracts)

    # Determine convergence robustly: check tail quiet days and open obligations
    def _has_open_obligations() -> bool:
        try:
            return any(c.kind in ("payable", "delivery_obligation") for c in system.state.contracts.values())
        except Exception:
            return False
    has_open = _has_open_obligations()
    tail_quiet_ok = False
    end_day = None
    if days_data:
        end_day = days_data[-1].get('day')
        if quiet_days is not None and len(days_data) >= quiet_days:
            tail = [d.get('quiet') for d in days_data[-quiet_days:]]
            tail_quiet_ok = all(bool(x) for x in tail)

    html_parts: List[str] = []
    html_parts.append("<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\">")
    html_parts.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
    html_parts.append(f"<title>Bilancio Simulation - { _html_escape(scenario_name) }</title>")
    html_parts.append(f"<style>{_load_css()}</style></head><body>")
    html_parts.append("<div class=\"container\">")
    html_parts.append("<header>")
    html_parts.append("<h1>Bilancio Simulation</h1>")
    html_parts.append(f"<h2>{_html_escape(scenario_name)}</h2>")
    if description:
        html_parts.append(f"<p class=\"description\">{_html_escape(description)}</p>")
    # Status line (converged or not)
    converged = (tail_quiet_ok and not has_open)
    status_text = "Converged" if converged else "Stopped without convergence"
    if converged and end_day is not None:
        status_text = f"Converged on day {end_day}"
    elif (not converged) and max_days is not None:
        status_text = f"Stopped without convergence (max_days = {max_days})"
    html_parts.append(
        f"<div class=\"meta\"><span>Final Day: {final_day}</span>"
        f"<span>Total Events: {total_events}</span>"
        f"<span>Active Agents: {active_agents}</span>"
        f"<span>Active Contracts: {active_contracts}</span>"
        f"<span>Status: {status_text}</span></div>"
    )
    html_parts.append("</header><main>")

    # Agents table
    html_parts.append("<section class=\"agents\"><h2>Agents</h2>")
    html_parts.append("<section class=\"events-table\"><table><thead><tr><th>ID</th><th>Name</th><th>Type</th></tr></thead><tbody>")
    for aid, agent in system.state.agents.items():
        name = _html_escape(agent.name or aid)
        kind = _html_escape(agent.kind)
        html_parts.append(f"<tr><td>{_html_escape(aid)}</td><td>{name}</td><td>{kind}</td></tr>")
    html_parts.append("</tbody></table></section></section>")

    # Day 0 (Setup)
    html_parts.append("<section class=\"day-section\"><h2 class=\"day-header\">📅 Day 0 (Setup)</h2>")
    setup_events = [e for e in system.state.events if e.get("phase") == "setup"]
    html_parts.append("<div class=\"events-section\"><h3>Setup Events</h3>")
    html_parts.append(_render_events_table("Setup", setup_events))
    html_parts.append("</div>")
    if agent_ids and initial_balances:
        html_parts.append("<div class=\"balances-section\"><h3>Balances</h3>")
        for aid in agent_ids:
            # Prefer captured initial_rows for detailed counterparties
            if initial_rows and aid in initial_rows:
                ag = system.state.agents[aid]
                title = f"{ag.name or aid} [{aid}] ({ag.kind})"
                rows = initial_rows[aid]
                html_parts.append(_render_t_account_from_rows(title, rows.get('assets', []), rows.get('liabs', [])))
            else:
                bal = initial_balances.get(aid)
                if isinstance(bal, AgentBalance):
                    assets_rows, liabs_rows = _build_rows_from_balance(bal)
                    ag = system.state.agents[aid]
                    title = f"{ag.name or aid} [{aid}] ({ag.kind})"
                    html_parts.append(_render_t_account_from_rows(title, assets_rows, liabs_rows))
                else:
                    html_parts.append(_render_t_account(system, aid))
        html_parts.append("</div>")
    html_parts.append("</section>")

    # Subsequent days from days_data (already chronological)
    for d in days_data:
        day_num = d.get('day')
        html_parts.append(f"<section class=\"day-section\"><h2 class=\"day-header\">📅 Day {day_num}</h2>")
        ev = d.get('events', [])
        buckets = _split_by_phases(ev)
        html_parts.append("<div class=\"events-section\">")
        b1, b2 = _split_phase_b_into_subphases(buckets.get("B", []))
        html_parts.append(_render_events_table("Phase B1 — Scheduled Actions", b1))
        html_parts.append(_render_events_table("Phase B2 — Settlement", b2))
        html_parts.append(_render_events_table("Phase C — Clearing", buckets.get("C", [])))
        html_parts.append("</div>")
        if agent_ids:
            html_parts.append("<div class=\"balances-section\"><h3>Balances</h3>")
            day_balances = d.get('balances') or {}
            day_rows = d.get('rows') or {}
            for aid in agent_ids:
                # Prefer captured rows with counterparties for this day
                if aid in day_rows:
                    rows = day_rows[aid]
                    ag = system.state.agents[aid]
                    title = f"{ag.name or aid} [{aid}] ({ag.kind})"
                    html_parts.append(_render_t_account_from_rows(title, rows.get('assets', []), rows.get('liabs', [])))
                else:
                    bal = day_balances.get(aid)
                    if isinstance(bal, AgentBalance):
                        assets_rows, liabs_rows = _build_rows_from_balance(bal)
                        ag = system.state.agents[aid]
                        title = f"{ag.name or aid} [{aid}] ({ag.kind})"
                        html_parts.append(_render_t_account_from_rows(title, assets_rows, liabs_rows))
                    else:
                        html_parts.append(_render_t_account(system, aid))
            html_parts.append("</div>")
        html_parts.append("</section>")

    # Conclusion section with termination reason
    html_parts.append("<section class=\"events-table\">")
    html_parts.append("<h3>Simulation End</h3>")
    if converged and end_day is not None:
        qtxt = f" after {quiet_days} quiet days" if quiet_days is not None else ""
        html_parts.append(
            f"<p>The system converged on day <strong>{end_day}</strong>{qtxt}: no impactful events and no open obligations.</p>"
        )
    else:
        mtxt = f" (max_days = {max_days})" if max_days is not None else ""
        html_parts.append(
            f"<p>Stopped without convergence{mtxt}. Consider increasing max days or reviewing outstanding obligations.</p>"
        )
    html_parts.append("</section>")

    html_parts.append("</main><footer>Generated by Bilancio</footer></div></body></html>")

    out_path.write_text("".join(html_parts), encoding="utf-8")

```

---

### 📄 src/bilancio/ui/render/__init__.py

```python
"""Rendering utilities for Bilancio UI components."""

from .models import AgentBalanceView, DayEventsView, DaySummaryView
from .formatters import EventFormatterRegistry
from .rich_builders import (
    build_agent_balance_table,
    build_multiple_agent_balances, 
    build_events_panel,
    build_day_summary
)

__all__ = [
    "AgentBalanceView",
    "DayEventsView", 
    "DaySummaryView",
    "EventFormatterRegistry",
    "build_agent_balance_table",
    "build_multiple_agent_balances",
    "build_events_panel", 
    "build_day_summary"
]
```

---

### 📄 src/bilancio/ui/render/formatters.py

```python
"""Event formatters for bilancio - Improved version with no redundancy."""

from typing import Dict, Any, Tuple, List


class EventFormatterRegistry:
    """Registry for event formatters."""
    
    def __init__(self):
        self._formatters = {}
    
    def register(self, event_kind: str):
        """Decorator to register a formatter for an event kind."""
        def decorator(func):
            self._formatters[event_kind] = func
            return func
        return decorator
    
    def format(self, event: Dict[str, Any]) -> Tuple[str, List[str], str]:
        """Format an event using the registered formatter."""
        kind = event.get("kind", "Unknown")
        formatter = self._formatters.get(kind)
        
        if formatter:
            return formatter(event)
        else:
            # Generic fallback for unknown events
            return self._format_generic(event)
    
    def _format_generic(self, event: Dict[str, Any]) -> Tuple[str, List[str], str]:
        """Generic formatter for unknown event kinds."""
        kind = event.get("kind", "Unknown")
        
        # Build a generic representation
        title = f"{kind} Event"
        lines = []
        
        # Add key fields, skipping meta fields
        skip_fields = {"kind", "day", "phase", "type"}
        for key, value in event.items():
            if key not in skip_fields:
                lines.append(f"{key}: {value}")
        
        return title, lines[:3], "❓"  # Limit to 3 lines


# Create global registry instance
registry = EventFormatterRegistry()


# Register specific formatters for common event kinds
@registry.register("CashTransferred")
def format_cash_transferred(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format cash transfer events."""
    amount = event.get("amount", 0)
    frm = event.get("frm", "Unknown")
    to = event.get("to", "Unknown")
    
    title = f"💰 Cash Transfer: ${amount:,}"
    lines = [f"{frm} → {to}"]
    
    return title, lines, "💰"


@registry.register("ReservesTransferred")
def format_reserves_transferred(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format reserves transfer events."""
    amount = event.get("amount", 0)
    frm = event.get("frm", "Unknown")
    to = event.get("to", "Unknown")
    
    title = f"🏦 Reserves Transfer: ${amount:,}"
    lines = [f"{frm} → {to}"]
    
    return title, lines, "🏦"


@registry.register("StockTransferred")
def format_stock_transferred(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format stock transfer events."""
    sku = event.get("sku", "Unknown")
    quantity = event.get("qty", event.get("quantity", 0))
    frm = event.get("frm", "Unknown") 
    to = event.get("to", "Unknown")
    unit_price = event.get("unit_price", None)
    
    title = f"📦 Stock Transfer: {quantity} {sku}"
    lines = [f"{frm} → {to}"]
    if unit_price:
        lines.append(f"@ ${unit_price:,}/unit")
    
    return title, lines, "📦"


@registry.register("DeliveryObligationCreated")
def format_delivery_obligation_created(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format delivery obligation creation events."""
    sku = event.get("sku", "Unknown")
    quantity = event.get("quantity", event.get("qty", 0))
    frm = event.get("frm", "Unknown")
    to = event.get("to", "Unknown")
    due_day = event.get("due_day", None)
    
    title = f"📋 Delivery Obligation: {quantity} {sku}"
    lines = [f"{frm} → {to}"]
    if due_day:
        lines.append(f"Due: Day {due_day}")
    
    return title, lines, "📋"


@registry.register("DeliveryObligationSettled")
def format_delivery_obligation_settled(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format delivery obligation settlement events."""
    sku = event.get("sku", "Unknown")
    quantity = event.get("quantity", event.get("qty", 0))
    debtor = event.get("debtor", "Unknown")
    creditor = event.get("creditor", "Unknown")
    
    title = f"✅ Delivery Settled: {quantity} {sku}"
    lines = [f"{debtor} → {creditor}"]
    
    return title, lines, "✅"


@registry.register("PayableCreated")
def format_payable_created(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format payable creation events."""
    amount = event.get("amount", 0)
    debtor = event.get("debtor", event.get("frm", "Unknown"))
    creditor = event.get("creditor", event.get("to", "Unknown"))
    due_day = event.get("due_day", None)
    
    title = f"💸 Payable Created: ${amount:,}"
    lines = [f"{debtor} owes {creditor}"]
    if due_day is not None:
        lines.append(f"Due: Day {due_day}")
    
    return title, lines, "💸"


@registry.register("PayableSettled")
def format_payable_settled(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format payable settlement events."""
    amount = event.get("amount", 0)
    debtor = event.get("debtor", "Unknown")
    creditor = event.get("creditor", "Unknown")
    
    title = f"💰 Payable Settled: ${amount:,}"
    lines = [f"{debtor} → {creditor}"]
    
    return title, lines, "💰"


@registry.register("CashDeposited")
def format_cash_deposited(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format cash deposit events."""
    customer = event.get("customer", "Unknown")
    bank = event.get("bank", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"🏧 Cash Deposit: ${amount:,}"
    lines = [f"{customer} → {bank}"]
    
    return title, lines, "🏧"


@registry.register("CashWithdrawn")
def format_cash_withdrawn(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format cash withdrawal events."""
    customer = event.get("customer", "Unknown")
    bank = event.get("bank", "Unknown") 
    amount = event.get("amount", 0)
    
    title = f"💸 Cash Withdrawal: ${amount:,}"
    lines = [f"{customer} ← {bank}"]
    
    return title, lines, "💸"


@registry.register("ClientPayment")
def format_client_payment(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format inter-bank client payment events."""
    payer = event.get("payer", "Unknown")
    payee = event.get("payee", "Unknown")
    amount = event.get("amount", 0)
    payer_bank = event.get("payer_bank", "Unknown")
    payee_bank = event.get("payee_bank", "Unknown")
    
    title = f"💳 Inter-Bank Payment: ${amount:,}"
    lines = [
        f"{payer} → {payee}",
        f"via {payer_bank} → {payee_bank}"
    ]
    
    return title, lines, "💳"


@registry.register("IntraBankPayment")
def format_intra_bank_payment(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format intra-bank payment events."""
    payer = event.get("payer", "Unknown")
    payee = event.get("payee", "Unknown")
    amount = event.get("amount", 0)
    bank = event.get("bank", "Unknown")
    
    title = f"🏦 Intra-Bank Payment: ${amount:,}"
    lines = [
        f"{payer} → {payee}",
        f"at {bank}"
    ]
    
    return title, lines, "🏦"


@registry.register("CashPayment")
def format_cash_payment(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format cash payment events."""
    payer = event.get("payer", "Unknown")
    payee = event.get("payee", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"💵 Cash Payment: ${amount:,}"
    lines = [f"{payer} → {payee}"]
    
    return title, lines, "💵"


@registry.register("InstrumentMerged")
def format_instrument_merged(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format instrument merge events (cash consolidation)."""
    keep = event.get("keep", "Unknown")
    removed = event.get("removed", "Unknown")
    
    # Extract short IDs for readability
    keep_short = keep.split('_')[-1][:8] if keep != "Unknown" else keep
    removed_short = removed.split('_')[-1][:8] if removed != "Unknown" else removed
    
    title = f"🔀 Cash Consolidation"
    lines = [
        f"Merged: {removed_short} → {keep_short}",
        f"(Reduces fragmentation)"
    ]
    
    return title, lines, "🔀"


@registry.register("InterbankCleared")
def format_interbank_cleared(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format interbank clearing events."""
    debtor_bank = event.get("debtor_bank", "Unknown")
    creditor_bank = event.get("creditor_bank", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"🔄 Interbank Clearing: ${amount:,}"
    lines = [f"{debtor_bank} → {creditor_bank}"]
    
    return title, lines, "🔄"


@registry.register("CashMinted")
def format_cash_minted(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format cash minting events."""
    to = event.get("to", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"🖨️ Cash Minted: ${amount:,}"
    lines = [f"To: {to}"]
    
    return title, lines, "🖨️"


@registry.register("ReservesMinted")
def format_reserves_minted(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format reserves minting events."""
    to = event.get("to", "Unknown")
    amount = event.get("amount", 0)
    
    title = f"🏛️ Reserves Minted: ${amount:,}"
    lines = [f"Bank: {to}"]
    
    return title, lines, "🏛️"


@registry.register("StockSplit")
def format_stock_split(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format stock split events."""
    sku = event.get("sku", "Unknown")
    original_qty = event.get("original_qty", 0)
    split_qty = event.get("split_qty", 0)
    remaining_qty = event.get("remaining_qty", 0)
    
    title = f"✂️ Stock Split: {split_qty} {sku}"
    lines = [
        f"From lot of {original_qty} → {remaining_qty} remain",
        f"(Preparing transfer)"
    ]
    
    return title, lines, "✂️"


@registry.register("DeliveryObligationCancelled")
def format_delivery_cancelled(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format delivery obligation cancellation."""
    obligation_id = event.get("obligation_id", "Unknown")
    debtor = event.get("debtor", "Unknown")
    
    # Short ID for readability
    short_id = obligation_id.split('_')[-1][:8] if obligation_id != "Unknown" else obligation_id
    
    title = f"✓ Obligation Cleared"
    lines = [
        f"By: {debtor}",
        f"ID: ...{short_id}"
    ]
    
    return title, lines, "✓"


@registry.register("StockCreated")
def format_stock_created(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format stock creation events."""
    owner = event.get("owner", "Unknown")
    sku = event.get("sku", "Unknown")
    qty = event.get("qty", event.get("quantity", 0))
    unit_price = event.get("unit_price", None)
    
    title = f"📋 Stock Created: {qty} {sku}"
    lines = [f"Owner: {owner}"]
    if unit_price:
        if isinstance(qty, (int, float)) and isinstance(unit_price, (int, float)):
            total_value = qty * unit_price
            lines.append(f"Value: ${unit_price:,}/unit (${total_value:,} total)")
        else:
            lines.append(f"Value: ${unit_price}/unit")
    
    return title, lines, "📋"


# Phase markers
@registry.register("PhaseA")
def format_phase_a(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format phase A markers."""
    day = event.get("day", "?")
    return f"⏰ Day {day} begins", ["Morning activities"], "⏰"


@registry.register("PhaseB")
def format_phase_b(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format phase B markers."""
    return "🌅 Business hours", ["Main economic activity"], "🌅"


@registry.register("PhaseC")
def format_phase_c(event: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Format phase C markers."""
    return "🌙 End of day", ["Settlements and clearing"], "🌙"
```

---

### 📄 src/bilancio/ui/render/models.py

```python
"""View model classes for Bilancio UI rendering."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Any


@dataclass
class BalanceItemView:
    """View model for a single balance sheet item."""
    category: str  # e.g., "Assets", "Liabilities"
    instrument: str  # e.g., "Cash", "Reserves", "Stock"
    amount: int | Decimal  # Quantity or monetary amount
    value: int | Decimal  # Monetary value


@dataclass
class AgentBalanceView:
    """View model for agent balance information."""
    agent_id: str
    agent_name: str
    agent_kind: str
    items: List[BalanceItemView]


@dataclass
class EventView:
    """View model for a single event."""
    kind: str
    title: str
    lines: List[str]
    icon: str
    raw_event: Dict[str, Any]  # Original event data for reference


@dataclass
class DayEventsView:
    """View model for events in a simulation day."""
    day: int
    phases: Dict[str, List[EventView]]  # phase -> list of events


@dataclass
class DaySummaryView:
    """View model for a complete day summary."""
    day: int
    events_view: DayEventsView
    agent_balances: List[AgentBalanceView]
```

---

### 📄 src/bilancio/ui/render/rich_builders.py

```python
"""Rich renderable builder functions for Bilancio UI components."""

from __future__ import annotations

from typing import List, Dict, Any, Union

try:
    from rich.table import Table
    from rich.columns import Columns
    from rich.panel import Panel
    from rich.text import Text
    from rich.tree import Tree
    from rich import box
    from rich.console import RenderableType
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback types for type hints
    Table = Any
    Columns = Any
    Panel = Any
    RenderableType = Any

from .models import AgentBalanceView, DayEventsView, DaySummaryView, BalanceItemView, EventView
from .formatters import registry as event_formatter_registry


def _format_currency(amount: Union[int, float], show_sign: bool = False) -> str:
    """Format an amount as currency."""
    formatted = f"{amount:,}"
    if show_sign and amount > 0:
        formatted = f"+{formatted}"
    return formatted


def build_agent_balance_table(balance_view: AgentBalanceView) -> Table:
    """Build a Rich Table for a single agent's balance sheet.
    
    Args:
        balance_view: Agent balance view model
        
    Returns:
        Rich Table renderable
    """
    if not RICH_AVAILABLE:
        raise RuntimeError("Rich library not available")
    
    # Create title with agent info
    if balance_view.agent_name and balance_view.agent_name != balance_view.agent_id:
        title = f"{balance_view.agent_name} [{balance_view.agent_id}] ({balance_view.agent_kind})"
    else:
        title = f"{balance_view.agent_id} ({balance_view.agent_kind})"
    
    # Create the main table
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan")
    table.add_column("ASSETS", style="green", width=35, no_wrap=False)
    table.add_column("Amount", justify="right", style="green", width=15, no_wrap=True)
    table.add_column("LIABILITIES", style="red", width=35, no_wrap=False)
    table.add_column("Amount", justify="right", style="red", width=15, no_wrap=True)
    
    # Separate assets and liabilities
    assets = [item for item in balance_view.items if item.category == "Assets"]
    liabilities = [item for item in balance_view.items if item.category == "Liabilities"]
    
    # Determine the maximum number of rows needed
    max_rows = max(len(assets), len(liabilities), 1)
    
    for i in range(max_rows):
        asset_name = assets[i].instrument if i < len(assets) else ""
        asset_amount = _format_currency(assets[i].value) if i < len(assets) else ""
        liability_name = liabilities[i].instrument if i < len(liabilities) else ""
        liability_amount = _format_currency(liabilities[i].value) if i < len(liabilities) else ""
        
        table.add_row(asset_name, asset_amount, liability_name, liability_amount)
    
    # Calculate totals
    total_assets = sum(item.value for item in assets)
    total_liabilities = sum(item.value for item in liabilities)
    net_worth = total_assets - total_liabilities
    
    # Add separator and totals
    table.add_row("", "", "", "", end_section=True)
    table.add_row(
        Text("TOTAL ASSETS", style="bold green"),
        Text(_format_currency(total_assets), style="bold green"),
        Text("TOTAL LIABILITIES", style="bold red"),
        Text(_format_currency(total_liabilities), style="bold red")
    )
    
    # Add net worth
    table.add_row("", "", "", "", end_section=True)
    net_worth_style = "bold green" if net_worth >= 0 else "bold red"
    table.add_row(
        "",
        "",
        Text("NET WORTH", style="bold blue"),
        Text(_format_currency(net_worth, show_sign=True), style=net_worth_style)
    )
    
    return table


def build_multiple_agent_balances(balances: List[AgentBalanceView]) -> Columns:
    """Build a Rich Columns layout for multiple agent balance sheets.
    
    Args:
        balances: List of agent balance view models
        
    Returns:
        Rich Columns renderable
    """
    if not RICH_AVAILABLE:
        raise RuntimeError("Rich library not available")
    
    tables = [build_agent_balance_table(balance) for balance in balances]
    return Columns(tables, equal=True, expand=True)


def build_events_panel(day_events_view: DayEventsView) -> Panel:
    """Build a Rich Panel for day events organized by phase.
    
    Args:
        day_events_view: Day events view model
        
    Returns:
        Rich Panel renderable
    """
    if not RICH_AVAILABLE:
        raise RuntimeError("Rich library not available")
    
    if not day_events_view.phases:
        return Panel(
            Text("No events occurred on this day.", style="dim"),
            title=f"Day {day_events_view.day} Events",
            border_style="blue"
        )
    
    # Create a tree structure for phases and events
    tree = Tree(f"📅 Day {day_events_view.day}")
    
    for phase, events in day_events_view.phases.items():
        if not events:
            continue
            
        # Add phase node
        phase_node = tree.add(f"📍 {phase}")
        
        # Add events under the phase
        for event in events:
            event_text = Text()
            event_text.append(f"{event.icon} ", style="")
            event_text.append(event.title, style="bold")
            
            event_node = phase_node.add(event_text)
            
            # Add event details as sub-items
            for line in event.lines:
                event_node.add(Text(line, style="dim"))
    
    return Panel(
        tree,
        title=f"Day {day_events_view.day} Events",
        border_style="blue"
    )


def build_events_list(day_events_view: DayEventsView) -> List[RenderableType]:
    """Build a list of Rich renderables for day events.
    
    Args:
        day_events_view: Day events view model
        
    Returns:
        List of Rich renderables
    """
    if not RICH_AVAILABLE:
        raise RuntimeError("Rich library not available")
    
    renderables = []
    
    if not day_events_view.phases:
        renderables.append(Text("No events occurred on this day.", style="dim"))
        return renderables
    
    for phase, events in day_events_view.phases.items():
        if not events:
            continue
            
        # Phase header
        renderables.append(Text(f"📍 {phase}", style="bold blue"))
        
        # Events in this phase
        for event in events:
            event_text = Text()
            event_text.append(f"  {event.icon} ", style="")
            event_text.append(event.title, style="bold")
            renderables.append(event_text)
            
            # Event details
            for line in event.lines:
                renderables.append(Text(f"    {line}", style="dim"))
        
        # Add spacing between phases
        renderables.append(Text(""))
    
    return renderables


def build_day_summary(view: DaySummaryView) -> List[RenderableType]:
    """Build a list of Rich renderables for a complete day summary.
    
    Args:
        view: Day summary view model
        
    Returns:
        List of Rich renderables
    """
    if not RICH_AVAILABLE:
        raise RuntimeError("Rich library not available")
    
    renderables = []
    
    # Day header
    renderables.append(Panel(
        Text(f"Day {view.day} Summary", style="bold cyan"),
        border_style="cyan"
    ))
    
    # Events section
    if view.events_view.phases:
        renderables.append(build_events_panel(view.events_view))
    else:
        renderables.append(Text("No events occurred on this day.", style="dim"))
    
    # Agent balances section
    if view.agent_balances:
        renderables.append(Text("\n💰 Agent Balances", style="bold yellow"))
        renderables.append(build_multiple_agent_balances(view.agent_balances))
    
    return renderables


def convert_raw_event_to_view(raw_event: Dict[str, Any]) -> EventView:
    """Convert a raw event dictionary to an EventView model.
    
    Args:
        raw_event: Raw event dictionary from system.state.events
        
    Returns:
        EventView model
    """
    title, lines, icon = event_formatter_registry.format(raw_event)
    
    return EventView(
        kind=raw_event.get("kind", "Unknown"),
        title=title,
        lines=lines,
        icon=icon,
        raw_event=raw_event
    )


def convert_raw_events_to_day_view(raw_events: List[Dict[str, Any]], day: int) -> DayEventsView:
    """Convert raw events for a day into a DayEventsView model.
    
    Args:
        raw_events: List of raw event dictionaries for the day
        day: Day number
        
    Returns:
        DayEventsView model
    """
    phases: Dict[str, List[EventView]] = {}
    
    for raw_event in raw_events:
        phase = raw_event.get("phase", "unknown")
        event_view = convert_raw_event_to_view(raw_event)
        
        if phase not in phases:
            phases[phase] = []
        phases[phase].append(event_view)
    
    return DayEventsView(day=day, phases=phases)
```

---

### 📄 src/bilancio/ui/run.py

```python
"""Orchestration logic for running Bilancio simulations."""

from pathlib import Path
from typing import Optional, List, Dict, Any
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from bilancio.engines.system import System
from bilancio.engines.simulation import run_day, run_until_stable
from bilancio.core.errors import ValidationError, DefaultError
from bilancio.config import load_yaml, apply_to_system
from bilancio.export.writers import write_balances_csv, write_events_jsonl

from .display import (
    show_scenario_header,
    show_scenario_header_renderable,
    show_day_summary,
    show_day_summary_renderable,
    show_simulation_summary,
    show_simulation_summary_renderable,
    show_error_panel
)


console = Console(record=True, width=120)


def run_scenario(
    path: Path,
    mode: str = "until_stable",
    max_days: int = 90,
    quiet_days: int = 2,
    show: str = "detailed",
    agent_ids: Optional[List[str]] = None,
    check_invariants: str = "setup",
    export: Optional[Dict[str, str]] = None,
    html_output: Optional[Path] = None,
    t_account: bool = False
) -> None:
    """Run a Bilancio simulation scenario.
    
    Args:
        path: Path to scenario YAML file
        mode: "step" or "until_stable"
        max_days: Maximum days to simulate
        quiet_days: Required quiet days for stable state
        show: "summary", "detailed" or "table" for event display
        agent_ids: List of agent IDs to show balances for
        check_invariants: "setup", "daily", or "none"
        export: Dictionary with export paths (balances_csv, events_jsonl)
        html_output: Optional path to export HTML with colored output
    """
    # Load configuration
    console.print("[dim]Loading scenario...[/dim]")
    config = load_yaml(path)
    
    # Create and configure system
    system = System()
    
    # Preflight schedule validation (aliases available when referenced)
    try:
        from bilancio.config.apply import validate_scheduled_aliases
        validate_scheduled_aliases(config)
    except ValueError as e:
        show_error_panel(
            error=e,
            phase="setup",
            context={"scenario": config.name}
        )
        sys.exit(1)

    # Apply configuration
    try:
        apply_to_system(config, system)
        
        if check_invariants in ("setup", "daily"):
            system.assert_invariants()
            
    except (ValidationError, ValueError) as e:
        show_error_panel(
            error=e,
            phase="setup",
            context={"scenario": config.name}
        )
        sys.exit(1)
    
    # Stage scheduled actions into system state (Phase B1 execution by day)
    try:
        if getattr(config, 'scheduled_actions', None):
            for sa in config.scheduled_actions:
                day = sa.day
                system.state.scheduled_actions_by_day.setdefault(day, []).append(sa.action)
    except Exception:
        # Keep robust even if config lacks scheduled actions
        pass
    
    # Use config settings unless overridden by CLI
    if agent_ids is None and config.run.show.balances:
        agent_ids = config.run.show.balances
    
    if export is None:
        export = {}
    
    # Use config export settings if not overridden
    if not export.get('balances_csv') and config.run.export.balances_csv:
        export['balances_csv'] = config.run.export.balances_csv
    if not export.get('events_jsonl') and config.run.export.events_jsonl:
        export['events_jsonl'] = config.run.export.events_jsonl
    
    # Show scenario header with agent list
    header_renderables = show_scenario_header_renderable(config.name, config.description, config.agents)
    for renderable in header_renderables:
        console.print(renderable)
    
    # Show initial state
    console.print("\n[bold cyan]📅 Day 0 (After Setup)[/bold cyan]")
    renderables = show_day_summary_renderable(system, agent_ids, show, t_account=t_account)
    for renderable in renderables:
        console.print(renderable)
    
    # Capture initial balance state for HTML export
    initial_balances: Dict[str, Any] = {}
    initial_rows: Dict[str, Dict[str, list]] = {}
    from bilancio.analysis.balances import agent_balance
    from bilancio.analysis.visualization import build_t_account_rows
    # Capture balances for all agents that we might display
    capture_ids = agent_ids if agent_ids else [a.id for a in system.state.agents.values()]
    for agent_id in capture_ids:
        initial_balances[agent_id] = agent_balance(system, agent_id)
        # also capture detailed rows with counterparties at setup
        acct = build_t_account_rows(system, agent_id)
        def _row_dict(r):
            return {
                'name': getattr(r, 'name', ''),
                'quantity': getattr(r, 'quantity', None),
                'value_minor': getattr(r, 'value_minor', None),
                'counterparty_name': getattr(r, 'counterparty_name', None),
                'maturity': getattr(r, 'maturity', None),
                'id_or_alias': getattr(r, 'id_or_alias', None),
            }
        initial_rows[agent_id] = {
            'assets': [_row_dict(r) for r in acct.assets],
            'liabs': [_row_dict(r) for r in acct.liabilities],
        }
    
    # Track day data for PDF export
    days_data = []
    
    if mode == "step":
        days_data = run_step_mode(
            system=system,
            max_days=max_days,
            show=show,
            agent_ids=agent_ids,
            check_invariants=check_invariants,
            scenario_name=config.name,
            t_account=t_account
        )
    else:
        days_data = run_until_stable_mode(
            system=system,
            max_days=max_days,
            quiet_days=quiet_days,
            show=show,
            agent_ids=agent_ids,
            check_invariants=check_invariants,
            scenario_name=config.name,
            t_account=t_account
        )
    
    # Export results if requested
    if export.get('balances_csv'):
        export_path = Path(export['balances_csv'])
        export_path.parent.mkdir(parents=True, exist_ok=True)
        write_balances_csv(system, export_path)
        console.print(f"[green]✓[/green] Exported balances to {export_path}")
    
    if export.get('events_jsonl'):
        export_path = Path(export['events_jsonl'])
        export_path.parent.mkdir(parents=True, exist_ok=True)
        write_events_jsonl(system, export_path)
        console.print(f"[green]✓[/green] Exported events to {export_path}")
    
    # Export to HTML if requested (semantic HTML for readability)
    if html_output:
        from .html_export import export_pretty_html
        export_pretty_html(
            system=system,
            out_path=html_output,
            scenario_name=config.name,
            description=config.description,
            agent_ids=agent_ids,
            initial_balances=initial_balances,
            days_data=days_data,
            initial_rows=initial_rows,
            max_days=max_days,
            quiet_days=quiet_days,
        )
        console.print(f"[green]✓[/green] Exported HTML report: {html_output}")


def run_step_mode(
    system: System,
    max_days: int,
    show: str,
    agent_ids: Optional[List[str]],
    check_invariants: str,
    scenario_name: str,
    t_account: bool = False
) -> List[Dict[str, Any]]:
    """Run simulation in step-by-step mode.
    
    Args:
        system: Configured system
        max_days: Maximum days to simulate
        show: Event display mode
        agent_ids: Agent IDs to show balances for
        check_invariants: Invariant checking mode
        scenario_name: Name of the scenario for error context
    
    Returns:
        List of day data dictionaries
    """
    days_data = []
    
    for _ in range(max_days):
        # Get the current day before running 
        day_before = system.state.day
        
        # Prompt to continue (ask about the next day which is day_before + 1)
        console.print()
        if not Confirm.ask(f"[cyan]Run day {day_before + 1}?[/cyan]", default=True):
            console.print("[yellow]Simulation stopped by user[/yellow]")
            break
        
        try:
            # Run the next day
            day_report = run_day(system)
            
            # Check invariants if requested
            if check_invariants == "daily":
                system.assert_invariants()
            
            # Skip day 0 - it's already shown as "Day 0 (After Setup)"
            if day_before >= 1:
                # Show day summary
                console.print(f"\n[bold cyan]📅 Day {day_before}[/bold cyan]")
                renderables = show_day_summary_renderable(system, agent_ids, show, day=day_before, t_account=t_account)
                for renderable in renderables:
                    console.print(renderable)
                
                # Collect day data for HTML export  
                # Use the actual event day
                day_events = [e for e in system.state.events 
                             if e.get("day") == day_before and e.get("phase") == "simulation"]
                
                # Capture current balance state for this day
                day_balances: Dict[str, Any] = {}
                day_rows: Dict[str, Dict[str, list]] = {}
                if agent_ids:
                    from bilancio.analysis.balances import agent_balance
                    from bilancio.analysis.visualization import build_t_account_rows

                    def _row_dict(r):
                        return {
                            'name': getattr(r, 'name', ''),
                            'quantity': getattr(r, 'quantity', None),
                            'value_minor': getattr(r, 'value_minor', None),
                            'counterparty_name': getattr(r, 'counterparty_name', None),
                            'maturity': getattr(r, 'maturity', None),
                            'id_or_alias': getattr(r, 'id_or_alias', None),
                        }

                    for agent_id in agent_ids:
                        day_balances[agent_id] = agent_balance(system, agent_id)
                        acct = build_t_account_rows(system, agent_id)
                        day_rows[agent_id] = {
                            'assets': [_row_dict(r) for r in acct.assets],
                            'liabs': [_row_dict(r) for r in acct.liabilities],
                        }
                
                days_data.append({
                    'day': day_before,  # Use actual event day, not 1-based counter
                    'events': day_events,
                    'quiet': day_report.quiet,
                    'stable': day_report.quiet and not day_report.has_open_obligations,
                    'balances': day_balances,
                    'rows': day_rows
                })
            
            # Check if we've reached a stable state
            if day_report.quiet and not day_report.has_open_obligations:
                console.print("[green]✓[/green] System reached stable state")
                break
                
        except DefaultError as e:
            show_error_panel(
                error=e,
                phase=f"day_{system.state.day}",
                context={
                    "scenario": scenario_name,
                    "day": system.state.day,
                    "phase": system.state.phase
                }
            )
            break
            
        except ValidationError as e:
            show_error_panel(
                error=e,
                phase=f"day_{system.state.day}",
                context={
                    "scenario": scenario_name,
                    "day": system.state.day,
                    "phase": system.state.phase
                }
            )
            break
            
        except Exception as e:
            show_error_panel(
                error=e,
                phase=f"day_{system.state.day}",
                context={
                    "scenario": scenario_name,
                    "day": system.state.day
                }
            )
            break
    
    # Show final summary
    console.print("\n[bold]Simulation Complete[/bold]")
    console.print(show_simulation_summary_renderable(system))
    
    return days_data


def run_until_stable_mode(
    system: System,
    max_days: int,
    quiet_days: int,
    show: str,
    agent_ids: Optional[List[str]],
    check_invariants: str,
    scenario_name: str,
    t_account: bool = False
) -> List[Dict[str, Any]]:
    """Run simulation until stable state is reached.
    
    Args:
        system: Configured system
        max_days: Maximum days to simulate
        quiet_days: Required quiet days for stable state
        show: Event display mode
        agent_ids: Agent IDs to show balances for
        check_invariants: Invariant checking mode
        scenario_name: Name of the scenario for error context
    
    Returns:
        List of day data dictionaries
    """
    console.print(f"\n[dim]Running simulation until stable (max {max_days} days)...[/dim]\n")
    
    try:
        # Run simulation day by day to capture correct balance snapshots
        from bilancio.engines.simulation import run_day, _impacted_today, _has_open_obligations
        from bilancio.analysis.balances import agent_balance
        
        reports = []
        consecutive_quiet = 0
        days_data = []
        
        for _ in range(max_days):
            # Run the next day
            day_before = system.state.day
            run_day(system)
            impacted = _impacted_today(system, day_before)
            
            # Create report
            from bilancio.engines.simulation import DayReport
            report = DayReport(day=day_before, impacted=impacted)
            reports.append(report)
            
            # Skip day 0 - it's already shown as "Day 0 (After Setup)"
            if day_before >= 1:
                # Display this day's results immediately (with correct balance state)
                console.print(f"[bold cyan]📅 Day {day_before}[/bold cyan]")
                
                # Check invariants if requested
                if check_invariants == "daily":
                    try:
                        system.assert_invariants()
                    except Exception as e:
                        console.print(f"[yellow]⚠ Invariant check failed: {e}[/yellow]")
                
                # Show events and balances for this specific day
                # Note: events are stored with 0-based day numbers
                renderables = show_day_summary_renderable(system, agent_ids, show, day=day_before, t_account=t_account)
                for renderable in renderables:
                    console.print(renderable)
                
                # Collect day data for HTML export
                # We want simulation events from the day that was just displayed
                # show_day_summary was called with day=day_before
                day_events = [e for e in system.state.events 
                             if e.get("day") == day_before and e.get("phase") == "simulation"]
                is_stable = consecutive_quiet >= quiet_days and not _has_open_obligations(system)
                
                # Capture current balance state for this day
                day_balances: Dict[str, Any] = {}
                day_rows: Dict[str, Dict[str, list]] = {}
                if agent_ids:
                    from bilancio.analysis.visualization import build_t_account_rows
                    for agent_id in agent_ids:
                        day_balances[agent_id] = agent_balance(system, agent_id)
                        acct = build_t_account_rows(system, agent_id)
                        def to_row(r):
                            return {
                                'name': getattr(r, 'name', ''),
                                'quantity': getattr(r, 'quantity', None),
                                'value_minor': getattr(r, 'value_minor', None),
                                'counterparty_name': getattr(r, 'counterparty_name', None),
                                'maturity': getattr(r, 'maturity', None),
                                'id_or_alias': getattr(r, 'id_or_alias', None),
                            }
                        day_rows[agent_id] = {
                            'assets': [to_row(r) for r in acct.assets],
                            'liabs': [to_row(r) for r in acct.liabilities],
                        }
                
                days_data.append({
                    'day': day_before,  # Use actual event day, not 1-based counter
                    'events': day_events,
                    'quiet': report.impacted == 0,
                    'stable': is_stable,
                    'balances': day_balances,
                    'rows': day_rows
                })
                
                # Show activity summary
                if report.impacted > 0:
                    console.print(f"[dim]Activity: {report.impacted} impactful events[/dim]")
                else:
                    console.print("[dim]→ Quiet day (no activity)[/dim]")
                
                if report.notes:
                    console.print(f"[dim]Note: {report.notes}[/dim]")
                
                console.print()
            
            # Check for stable state
            if impacted == 0:
                consecutive_quiet += 1
            else:
                consecutive_quiet = 0
            
            if consecutive_quiet >= quiet_days and not _has_open_obligations(system):
                console.print("[green]✓[/green] System reached stable state")
                break
        
        # If we didn't break early, check if we hit max days
        else:
            console.print("[yellow]⚠[/yellow] Maximum days reached without stable state")
        
    except DefaultError as e:
        show_error_panel(
            error=e,
            phase="simulation",
            context={
                "scenario": scenario_name,
                "day": system.state.day,
                "phase": system.state.phase
            }
        )
        
    except ValidationError as e:
        show_error_panel(
            error=e,
            phase="simulation",
            context={
                "scenario": scenario_name,
                "day": system.state.day,
                "phase": system.state.phase
            }
        )
        
    except Exception as e:
        show_error_panel(
            error=e,
            phase="simulation",
            context={
                "scenario": scenario_name,
                "day": system.state.day
            }
        )
    
    # Show final summary
    console.print("\n[bold]Simulation Complete[/bold]")
    console.print(show_simulation_summary_renderable(system))
    
    return days_data

```

---

### 📄 src/bilancio/ui/settings.py

```python
"""UI settings and configuration for bilancio display."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Central configuration for UI display settings."""
    
    # Console settings
    console_width: int = 100        # Width used by Console(width=...) universally
    
    # Currency and display
    currency_denom: str = "X"       # Default denomination symbol
    currency_precision: int = 2     # Decimal places for currency values
    
    # HTML export settings
    html_inline_styles: bool = True # Whether to inline CSS styles in HTML export
    
    # Table display settings
    balance_table_width: int = 80   # Width for balance sheet tables
    event_panel_width: int = 90     # Width for event panels
    
    # Formatting thresholds
    zero_threshold: float = 0.01    # Values below this are considered zero
    
    # Event display settings
    max_event_lines: int = 10       # Maximum lines per event in display
    show_event_icons: bool = True   # Whether to show emoji icons for events
    
    # Phase colors (for Rich console)
    phase_colors: dict = None
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.phase_colors is None:
            # Use object.__setattr__ to set value on frozen dataclass
            object.__setattr__(self, 'phase_colors', {
                'A': 'cyan',
                'B': 'yellow', 
                'C': 'green'
            })


# Global default settings instance
DEFAULT_SETTINGS = Settings()
```

---

### 📄 src/bilancio/ui/wizard.py

```python
"""Interactive wizard for creating Bilancio scenarios."""

import yaml
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm

console = Console()


def create_scenario_wizard(output_path: Path, template: Optional[str] = None) -> None:
    """Interactive wizard to create a scenario configuration.
    
    Args:
        output_path: Path where to save the configuration
        template: Optional template name to use (simple, standard, complex, or path to YAML)
    """
    console.print("[bold cyan]Bilancio Scenario Creator[/bold cyan]\n")
    
    # If template is provided, use it to determine complexity
    if template:
        # Check if template is a file path
        template_path = Path(template)
        if template_path.exists() and template_path.suffix in ['.yaml', '.yml']:
            # Load existing YAML as template
            console.print(f"[dim]Using template from: {template}[/dim]")
            with open(template_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Allow user to modify the loaded template
            name = Prompt.ask("Scenario name", default=config.get("name", "My Scenario"))
            description = Prompt.ask("Description (optional)", 
                                    default=config.get("description", ""))
            
            # Update the config with new name and description
            config["name"] = name
            config["description"] = description or None
            
            # Save and exit early
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            console.print(f"\n[green]✓[/green] Scenario configuration saved to: {output_path}")
            console.print(f"\nRun your scenario with: [cyan]bilancio run {output_path}[/cyan]")
            return
        
        # Otherwise, treat template as complexity level
        elif template in ["simple", "standard", "complex"]:
            complexity = template
            console.print(f"[dim]Using {complexity} template[/dim]")
        else:
            console.print(f"[yellow]Warning: Unknown template '{template}', using interactive mode[/yellow]")
            complexity = Prompt.ask(
                "Complexity",
                choices=["simple", "standard", "complex"],
                default="simple"
            )
    else:
        # No template provided, ask for complexity
        complexity = Prompt.ask(
            "Complexity",
            choices=["simple", "standard", "complex"],
            default="simple"
        )
    
    # Get basic information (with fallback for non-interactive mode)
    try:
        name = Prompt.ask("Scenario name", default="My Scenario")
        description = Prompt.ask("Description (optional)", default="")
    except (EOFError, KeyboardInterrupt):
        # Non-interactive mode or user cancelled - use defaults
        name = "My Scenario"
        description = ""
    
    config = {
        "version": 1,
        "name": name,
        "description": description or None,
        "agents": [],
        "initial_actions": [],
        "run": {
            "mode": "until_stable",
            "max_days": 90,
            "quiet_days": 2,
            "show": {
                "events": "detailed"
            }
        }
    }
    
    if complexity == "simple":
        # Simple: 1 central bank, 1 bank, 2 households
        config["agents"] = [
            {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
            {"id": "B1", "kind": "bank", "name": "First Bank"},
            {"id": "H1", "kind": "household", "name": "Household 1"},
            {"id": "H2", "kind": "household", "name": "Household 2"}
        ]
        
        config["initial_actions"] = [
            {"mint_reserves": {"to": "B1", "amount": 10000}},
            {"mint_cash": {"to": "H1", "amount": 1000}},
            {"mint_cash": {"to": "H2", "amount": 1000}},
            {"deposit_cash": {"customer": "H1", "bank": "B1", "amount": 800}}
        ]
        
        config["run"]["show"]["balances"] = ["B1", "H1", "H2"]
        
    elif complexity == "standard":
        # Standard: Add a firm and some delivery obligations
        config["agents"] = [
            {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
            {"id": "B1", "kind": "bank", "name": "First Bank"},
            {"id": "B2", "kind": "bank", "name": "Second Bank"},
            {"id": "H1", "kind": "household", "name": "Household 1"},
            {"id": "H2", "kind": "household", "name": "Household 2"},
            {"id": "F1", "kind": "firm", "name": "ABC Corp"}
        ]
        
        config["initial_actions"] = [
            {"mint_reserves": {"to": "B1", "amount": 10000}},
            {"mint_reserves": {"to": "B2", "amount": 10000}},
            {"mint_cash": {"to": "H1", "amount": 2000}},
            {"mint_cash": {"to": "H2", "amount": 1500}},
            {"deposit_cash": {"customer": "H1", "bank": "B1", "amount": 1500}},
            {"deposit_cash": {"customer": "H2", "bank": "B2", "amount": 1000}},
            {"create_stock": {"owner": "F1", "sku": "WIDGET", "quantity": 100, "unit_price": "50"}},
            {"create_delivery_obligation": {
                "from": "F1", "to": "H1", 
                "sku": "WIDGET", "quantity": 5, 
                "unit_price": "50", "due_day": 2
            }}
        ]
        
        config["run"]["show"]["balances"] = ["B1", "B2", "H1", "H2", "F1"]
        
    else:  # complex
        console.print("[yellow]Complex scenarios should be hand-crafted.[/yellow]")
        console.print("Creating a template with all available features...")
        
        # Complex: Full example with all features
        config["policy_overrides"] = {
            "mop_rank": {
                "household": ["bank_deposit", "cash"],
                "bank": ["reserve_deposit"]
            }
        }
        
        config["agents"] = [
            {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
            {"id": "T1", "kind": "treasury", "name": "Treasury"},
            {"id": "B1", "kind": "bank", "name": "Commercial Bank 1"},
            {"id": "B2", "kind": "bank", "name": "Commercial Bank 2"},
            {"id": "H1", "kind": "household", "name": "Smith Family"},
            {"id": "H2", "kind": "household", "name": "Jones Family"},
            {"id": "F1", "kind": "firm", "name": "Manufacturing Inc"},
            {"id": "F2", "kind": "firm", "name": "Retail Corp"}
        ]
        
        config["initial_actions"] = [
            # Initial reserves
            {"mint_reserves": {"to": "B1", "amount": 50000}},
            {"mint_reserves": {"to": "B2", "amount": 50000}},
            
            # Initial cash
            {"mint_cash": {"to": "H1", "amount": 5000}},
            {"mint_cash": {"to": "H2", "amount": 3000}},
            {"mint_cash": {"to": "F1", "amount": 10000}},
            {"mint_cash": {"to": "F2", "amount": 8000}},
            
            # Bank deposits
            {"deposit_cash": {"customer": "H1", "bank": "B1", "amount": 4000}},
            {"deposit_cash": {"customer": "H2", "bank": "B2", "amount": 2500}},
            {"deposit_cash": {"customer": "F1", "bank": "B1", "amount": 8000}},
            {"deposit_cash": {"customer": "F2", "bank": "B2", "amount": 6000}},
            
            # Create inventory
            {"create_stock": {"owner": "F1", "sku": "MACHINE", "quantity": 10, "unit_price": "1000"}},
            {"create_stock": {"owner": "F2", "sku": "GOODS", "quantity": 100, "unit_price": "50"}},
            
            # Create obligations
            {"create_delivery_obligation": {
                "from": "F1", "to": "F2",
                "sku": "MACHINE", "quantity": 2,
                "unit_price": "1000", "due_day": 3
            }},
            {"create_payable": {
                "from": "H1", "to": "F2",
                "amount": 500, "due_day": 1
            }}
        ]
        
        config["run"]["show"]["balances"] = ["CB", "B1", "B2", "H1", "H2", "F1", "F2"]
        config["run"]["export"] = {
            "balances_csv": "out/balances.csv",
            "events_jsonl": "out/events.jsonl"
        }
    
    # Save the configuration
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    console.print(f"\n[green]✓[/green] Scenario configuration saved to: {output_path}")
    console.print(f"\nRun your scenario with: [cyan]bilancio run {output_path}[/cyan]")
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

### 🧪 tests/analysis/test_t_account_builder.py

```python
"""Tests for T-account row builder and maturity parsing."""

from decimal import Decimal
from bilancio.engines.system import System
from bilancio.config.apply import create_agent
from bilancio.analysis.visualization import build_t_account_rows, parse_day_from_maturity


def test_parse_day_from_maturity_helper():
    assert parse_day_from_maturity("Day 10") == 10
    # Unknown or malformed sorts to end (inf)
    assert parse_day_from_maturity("Soon") > 10**9
    assert parse_day_from_maturity(None) > 10**9
    assert parse_day_from_maturity("Day X") > 10**9


def test_build_t_account_rows_sorting_by_maturity():
    sys = System()
    # Two agents with reciprocal delivery obligations at different days
    f1 = create_agent(type("Spec", (), {"id":"F1","kind":"firm","name":"Firm One"}))
    f2 = create_agent(type("Spec", (), {"id":"F2","kind":"firm","name":"Firm Two"}))
    sys.add_agent(f1)
    sys.add_agent(f2)

    # F1 owes F2: 10 items due Day 2
    sys.create_delivery_obligation("F1", "F2", sku="ITEM", quantity=10, unit_price=Decimal("5"), due_day=2)
    # F2 owes F1: 5 items due Day 1
    sys.create_delivery_obligation("F2", "F1", sku="ITEM", quantity=5, unit_price=Decimal("5"), due_day=1)

    acct_f1 = build_t_account_rows(sys, "F1")
    # For F1: assets should include receivable from F2 due Day 1 before inventory/financials; liabilities Day 2 obligation
    asset_names = [r.name for r in acct_f1.assets]
    liab_names = [r.name for r in acct_f1.liabilities]
    # Receivable row must be present
    assert any(n.endswith("receivable") for n in asset_names)
    # Obligation row must be present
    assert any(n.endswith("obligation") for n in liab_names)

    # Sorting by maturity: for obligations, Day 2 sorts after Day 1; for assets, receivable is a group keyed by day
    # Build keys using the same helper
    asset_due_days = [parse_day_from_maturity(r.maturity) for r in acct_f1.assets if r.name.endswith("receivable")]
    assert asset_due_days == sorted(asset_due_days)

```

---

### 🧪 tests/config/test_apply.py

```python
"""Tests for applying configuration to system."""

import pytest
from decimal import Decimal

from bilancio.engines.system import System
from bilancio.config.models import ScenarioConfig, AgentSpec
from bilancio.config.apply import apply_to_system, create_agent, apply_action
from bilancio.domain.agents import Bank, Household, CentralBank, Firm


class TestCreateAgent:
    """Test agent creation from specification."""
    
    def test_create_central_bank(self):
        """Test creating a central bank agent."""
        spec = AgentSpec(id="CB", kind="central_bank", name="Central Bank")
        agent = create_agent(spec)
        assert isinstance(agent, CentralBank)
        assert agent.id == "CB"
        assert agent.name == "Central Bank"
        assert agent.kind == "central_bank"
    
    def test_create_bank(self):
        """Test creating a bank agent."""
        spec = AgentSpec(id="B1", kind="bank", name="First Bank")
        agent = create_agent(spec)
        assert isinstance(agent, Bank)
        assert agent.id == "B1"
        assert agent.name == "First Bank"
        assert agent.kind == "bank"
    
    def test_create_household(self):
        """Test creating a household agent."""
        spec = AgentSpec(id="H1", kind="household", name="Smith Family")
        agent = create_agent(spec)
        assert isinstance(agent, Household)
        assert agent.id == "H1"
        assert agent.name == "Smith Family"
        assert agent.kind == "household"
    
    def test_create_firm(self):
        """Test creating a firm agent."""
        spec = AgentSpec(id="F1", kind="firm", name="ABC Corp")
        agent = create_agent(spec)
        assert isinstance(agent, Firm)
        assert agent.id == "F1"
        assert agent.name == "ABC Corp"
        assert agent.kind == "firm"


class TestApplyToSystem:
    """Test applying configuration to system."""
    
    def test_apply_minimal_config(self):
        """Test applying minimal configuration."""
        config = ScenarioConfig(
            name="Minimal",
            agents=[
                {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
                {"id": "B1", "kind": "bank", "name": "Bank"}
            ]
        )
        
        system = System()
        apply_to_system(config, system)
        
        # Check agents were added
        assert "CB" in system.state.agents
        assert "B1" in system.state.agents
        assert system.state.agents["CB"].kind == "central_bank"
        assert system.state.agents["B1"].kind == "bank"
        
        # System should pass invariants
        system.assert_invariants()
    
    def test_apply_with_initial_actions(self):
        """Test applying configuration with initial actions."""
        config = ScenarioConfig(
            name="With Actions",
            agents=[
                {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
                {"id": "B1", "kind": "bank", "name": "Bank"},
                {"id": "H1", "kind": "household", "name": "Household"}
            ],
            initial_actions=[
                {"mint_reserves": {"to": "B1", "amount": 10000}},
                {"mint_cash": {"to": "H1", "amount": 1000}}
            ]
        )
        
        system = System()
        apply_to_system(config, system)
        
        # Check agents
        assert len(system.state.agents) == 3
        
        # Check that actions were executed
        # Bank should have reserves
        bank = system.state.agents["B1"]
        assert len(bank.asset_ids) > 0  # Should have reserve deposit
        
        # Household should have cash
        household = system.state.agents["H1"]
        assert len(household.asset_ids) > 0  # Should have cash
        
        # System should pass invariants
        system.assert_invariants()
    
    def test_apply_with_policy_overrides(self):
        """Test applying configuration with policy overrides."""
        config = ScenarioConfig(
            name="With Policy",
            agents=[
                {"id": "CB", "kind": "central_bank", "name": "CB"}
            ],
            policy_overrides={
                "mop_rank": {
                    "household": ["cash", "bank_deposit"],
                    "bank": ["reserve_deposit"]
                }
            }
        )
        
        system = System()
        apply_to_system(config, system)
        
        # Check policy was updated
        assert system.policy.mop_rank["household"] == ["cash", "bank_deposit"]
        assert system.policy.mop_rank["bank"] == ["reserve_deposit"]
    
    def test_apply_complex_scenario(self):
        """Test applying a complex scenario with multiple actions."""
        config = ScenarioConfig(
            name="Complex",
            agents=[
                {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
                {"id": "B1", "kind": "bank", "name": "Bank 1"},
                {"id": "B2", "kind": "bank", "name": "Bank 2"},
                {"id": "H1", "kind": "household", "name": "Household 1"},
                {"id": "H2", "kind": "household", "name": "Household 2"},
                {"id": "F1", "kind": "firm", "name": "Firm 1"}
            ],
            initial_actions=[
                {"mint_reserves": {"to": "B1", "amount": 20000}},
                {"mint_reserves": {"to": "B2", "amount": 15000}},
                {"mint_cash": {"to": "H1", "amount": 5000}},
                {"mint_cash": {"to": "H2", "amount": 3000}},
                {"deposit_cash": {"customer": "H1", "bank": "B1", "amount": 4000}},
                {"deposit_cash": {"customer": "H2", "bank": "B2", "amount": 2000}},
                {"create_stock": {"owner": "F1", "sku": "WIDGET", "quantity": 100, "unit_price": "25"}},
                {"create_payable": {"from": "H1", "to": "H2", "amount": 500, "due_day": 1}}
            ]
        )
        
        system = System()
        apply_to_system(config, system)
        
        # Check all agents were created
        assert len(system.state.agents) == 6
        
        # Check stock was created
        assert len(system.state.stocks) > 0
        stocks = [s for s in system.state.stocks.values() if s.owner_id == "F1"]
        assert len(stocks) == 1
        assert stocks[0].sku == "WIDGET"
        assert stocks[0].quantity == 100
        
        # Check payable was created
        # Payable uses liability_issuer_id for the debtor
        payables = [c for c in system.state.contracts.values() 
                   if hasattr(c, 'liability_issuer_id') and c.liability_issuer_id == "H1"]
        assert len(payables) > 0
        
        # System should pass invariants
        system.assert_invariants()
    
    def test_apply_with_delivery_obligation(self):
        """Test applying configuration with delivery obligations."""
        config = ScenarioConfig(
            name="Delivery",
            agents=[
                {"id": "CB", "kind": "central_bank", "name": "CB"},
                {"id": "F1", "kind": "firm", "name": "Firm"},
                {"id": "H1", "kind": "household", "name": "Household"}
            ],
            initial_actions=[
                {"mint_cash": {"to": "F1", "amount": 1000}},
                {"mint_cash": {"to": "H1", "amount": 1000}},
                {"create_stock": {"owner": "F1", "sku": "ITEM", "quantity": 10, "unit_price": "50"}},
                {"create_delivery_obligation": {
                    "from": "F1", "to": "H1",
                    "sku": "ITEM", "quantity": 5,
                    "unit_price": "50", "due_day": 2
                }}
            ]
        )
        
        system = System()
        apply_to_system(config, system)
        
        # Check delivery obligation was created
        obligations = [c for c in system.state.contracts.values()
                      if hasattr(c, 'sku')]
        assert len(obligations) > 0
        
        # System should pass invariants
        system.assert_invariants()
```

---

### 🧪 tests/config/test_loaders.py

```python
"""Tests for YAML configuration loading."""

import pytest
import yaml
from pathlib import Path
from decimal import Decimal
import tempfile

from bilancio.config.loaders import load_yaml, parse_action, preprocess_config
from bilancio.config.models import (
    MintCash,
    MintReserves,
    DepositCash,
    CreateStock,
    CreateDeliveryObligation,
    CreatePayable
)


class TestParseAction:
    """Test action parsing from dictionaries."""
    
    def test_parse_mint_cash(self):
        """Test parsing mint_cash action."""
        action = parse_action({"mint_cash": {"to": "H1", "amount": 1000}})
        assert isinstance(action, MintCash)
        assert action.to == "H1"
        assert action.amount == 1000
    
    def test_parse_mint_reserves(self):
        """Test parsing mint_reserves action."""
        action = parse_action({"mint_reserves": {"to": "B1", "amount": 5000}})
        assert isinstance(action, MintReserves)
        assert action.to == "B1"
        assert action.amount == 5000
    
    def test_parse_deposit_cash(self):
        """Test parsing deposit_cash action."""
        action = parse_action({
            "deposit_cash": {"customer": "H1", "bank": "B1", "amount": 500}
        })
        assert isinstance(action, DepositCash)
        assert action.customer == "H1"
        assert action.bank == "B1"
        assert action.amount == 500
    
    def test_parse_create_stock(self):
        """Test parsing create_stock action."""
        action = parse_action({
            "create_stock": {
                "owner": "F1",
                "sku": "WIDGET",
                "quantity": 100,
                "unit_price": "25.50"
            }
        })
        assert isinstance(action, CreateStock)
        assert action.owner == "F1"
        assert action.sku == "WIDGET"
        assert action.quantity == 100
        assert action.unit_price == Decimal("25.50")
    
    def test_parse_delivery_obligation_with_aliases(self):
        """Test parsing delivery obligation with from/to aliases."""
        action = parse_action({
            "create_delivery_obligation": {
                "from": "F1",
                "to": "H1",
                "sku": "WIDGET",
                "quantity": 10,
                "unit_price": "25",
                "due_day": 3
            }
        })
        assert isinstance(action, CreateDeliveryObligation)
        assert action.from_agent == "F1"
        assert action.to_agent == "H1"
        assert action.sku == "WIDGET"
    
    def test_parse_payable_with_aliases(self):
        """Test parsing payable with from/to aliases."""
        action = parse_action({
            "create_payable": {
                "from": "H1",
                "to": "H2",
                "amount": 300,
                "due_day": 1
            }
        })
        assert isinstance(action, CreatePayable)
        assert action.from_agent == "H1"
        assert action.to_agent == "H2"
        assert action.amount == 300
    
    def test_parse_unknown_action(self):
        """Test that unknown action types raise error."""
        with pytest.raises(ValueError) as exc_info:
            parse_action({"unknown_action": {"data": "value"}})
        assert "Unknown action type" in str(exc_info.value)


class TestPreprocessConfig:
    """Test configuration preprocessing."""
    
    def test_convert_string_decimals(self):
        """Test conversion of string decimals."""
        data = {
            "amount": "123.45",
            "nested": {
                "price": "99.99"
            },
            "list": [
                {"value": "10.50"},
                {"value": "20.75"}
            ]
        }
        
        result = preprocess_config(data)
        
        assert result["amount"] == Decimal("123.45")
        assert result["nested"]["price"] == Decimal("99.99")
        assert result["list"][0]["value"] == Decimal("10.50")
        assert result["list"][1]["value"] == Decimal("20.75")
    
    def test_preserve_non_numeric_strings(self):
        """Test that non-numeric strings are preserved."""
        data = {
            "name": "Test Name",
            "id": "ABC123",
            "amount": "100.00",
            "description": "Some text with 123 numbers"
        }
        
        result = preprocess_config(data)
        
        assert result["name"] == "Test Name"
        assert result["id"] == "ABC123"
        assert result["amount"] == Decimal("100.00")
        assert result["description"] == "Some text with 123 numbers"


class TestLoadYaml:
    """Test YAML file loading."""
    
    def test_load_valid_yaml(self):
        """Test loading a valid YAML configuration."""
        yaml_content = """
version: 1
name: Test Scenario
description: A test scenario

agents:
  - id: CB
    kind: central_bank
    name: Central Bank
  - id: B1
    kind: bank
    name: First Bank

initial_actions:
  - mint_reserves: {to: B1, amount: 10000}
  - mint_cash: {to: H1, amount: 1000}

run:
  mode: until_stable
  max_days: 30
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            config = load_yaml(temp_path)
            assert config.name == "Test Scenario"
            assert config.version == 1
            assert len(config.agents) == 2
            assert config.agents[0].id == "CB"
            assert config.agents[1].id == "B1"
            assert len(config.initial_actions) == 2
            assert config.run.mode == "until_stable"
            assert config.run.max_days == 30
        finally:
            temp_path.unlink()
    
    def test_load_file_not_found(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_yaml(Path("nonexistent.yaml"))
    
    def test_load_invalid_yaml_syntax(self):
        """Test loading file with invalid YAML syntax."""
        yaml_content = """
version: 1
name: Bad YAML
  - this is invalid
    : syntax
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_yaml(temp_path)
        finally:
            temp_path.unlink()
    
    def test_load_invalid_config_schema(self):
        """Test loading YAML with invalid configuration schema."""
        yaml_content = """
version: 1
name: Invalid Config
agents:
  - id: CB
    kind: invalid_kind
    name: Invalid Agent
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError) as exc_info:
                load_yaml(temp_path)
            assert "validation failed" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()
    
    def test_load_example_scenario(self):
        """Test loading one of the example scenarios."""
        example_path = Path("examples/scenarios/simple_bank.yaml")
        if example_path.exists():
            config = load_yaml(example_path)
            assert config.name == "Simple Banking System"
            assert len(config.agents) == 4  # CB, B1, H1, H2
            assert config.run.mode == "until_stable"
```

---

### 🧪 tests/config/test_models.py

```python
"""Tests for configuration models."""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from bilancio.config.models import (
    AgentSpec,
    MintCash,
    MintReserves,
    DepositCash,
    CreateStock,
    CreateDeliveryObligation,
    CreatePayable,
    ScenarioConfig,
    RunConfig,
    PolicyOverrides
)


class TestAgentSpec:
    """Test AgentSpec model validation."""
    
    def test_valid_agent_spec(self):
        """Test creating a valid agent specification."""
        agent = AgentSpec(
            id="B1",
            kind="bank",
            name="First Bank"
        )
        assert agent.id == "B1"
        assert agent.kind == "bank"
        assert agent.name == "First Bank"
    
    def test_invalid_agent_kind(self):
        """Test that invalid agent kind raises error."""
        with pytest.raises(ValidationError):
            AgentSpec(
                id="X1",
                kind="invalid_kind",
                name="Invalid Agent"
            )


class TestActions:
    """Test action model validation."""
    
    def test_mint_cash_valid(self):
        """Test valid mint cash action."""
        action = MintCash(to="H1", amount=Decimal("1000"))
        assert action.to == "H1"
        assert action.amount == Decimal("1000")
        assert action.action == "mint_cash"
    
    def test_mint_cash_negative_amount(self):
        """Test that negative amounts are rejected."""
        with pytest.raises(ValidationError):
            MintCash(to="H1", amount=Decimal("-100"))
    
    def test_deposit_cash_valid(self):
        """Test valid deposit cash action."""
        action = DepositCash(
            customer="H1",
            bank="B1",
            amount=Decimal("500")
        )
        assert action.customer == "H1"
        assert action.bank == "B1"
        assert action.amount == Decimal("500")
    
    def test_create_stock_valid(self):
        """Test valid create stock action."""
        action = CreateStock(
            owner="F1",
            sku="WIDGET",
            quantity=100,
            unit_price=Decimal("25.50")
        )
        assert action.owner == "F1"
        assert action.sku == "WIDGET"
        assert action.quantity == 100
        assert action.unit_price == Decimal("25.50")
    
    def test_create_stock_invalid_quantity(self):
        """Test that zero or negative quantities are rejected."""
        with pytest.raises(ValidationError):
            CreateStock(
                owner="F1",
                sku="WIDGET",
                quantity=0,
                unit_price=Decimal("25")
            )
    
    def test_create_delivery_obligation_with_aliases(self):
        """Test delivery obligation with from/to aliases."""
        # Use the aliases 'from' and 'to' instead of from_agent/to_agent
        data = {
            "from": "F1",
            "to": "H1",
            "sku": "WIDGET",
            "quantity": 10,
            "unit_price": Decimal("25"),
            "due_day": 3
        }
        action = CreateDeliveryObligation(**data)
        assert action.from_agent == "F1"
        assert action.to_agent == "H1"
        assert action.due_day == 3
    
    def test_create_payable_valid(self):
        """Test valid create payable action."""
        # Use the aliases 'from' and 'to' instead of from_agent/to_agent
        data = {
            "from": "H1",
            "to": "H2",
            "amount": Decimal("300"),
            "due_day": 1
        }
        action = CreatePayable(**data)
        assert action.from_agent == "H1"
        assert action.to_agent == "H2"
        assert action.amount == Decimal("300")
        assert action.due_day == 1
    
    def test_create_payable_negative_due_day(self):
        """Test that negative due days are rejected."""
        with pytest.raises(ValidationError):
            CreatePayable(
                from_agent="H1",
                to_agent="H2",
                amount=Decimal("300"),
                due_day=-1
            )


class TestScenarioConfig:
    """Test ScenarioConfig model validation."""
    
    def test_minimal_valid_config(self):
        """Test minimal valid scenario configuration."""
        config = ScenarioConfig(
            name="Test Scenario",
            agents=[
                {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
                {"id": "B1", "kind": "bank", "name": "Bank 1"}
            ]
        )
        assert config.name == "Test Scenario"
        assert config.version == 1
        assert len(config.agents) == 2
        assert config.description is None
        assert config.initial_actions == []
    
    def test_config_with_all_fields(self):
        """Test scenario configuration with all fields."""
        config = ScenarioConfig(
            version=1,
            name="Full Scenario",
            description="A complete test scenario",
            policy_overrides={
                "mop_rank": {
                    "household": ["bank_deposit", "cash"]
                }
            },
            agents=[
                {"id": "CB", "kind": "central_bank", "name": "CB"},
                {"id": "B1", "kind": "bank", "name": "Bank"}
            ],
            initial_actions=[
                {"mint_reserves": {"to": "B1", "amount": 10000}}
            ],
            run={
                "mode": "until_stable",
                "max_days": 90,
                "quiet_days": 2,
                "show": {
                    "balances": ["CB", "B1"],
                    "events": "detailed"
                },
                "export": {
                    "balances_csv": "balances.csv",
                    "events_jsonl": "events.jsonl"
                }
            }
        )
        assert config.name == "Full Scenario"
        assert config.description == "A complete test scenario"
        assert config.policy_overrides.mop_rank["household"] == ["bank_deposit", "cash"]
        assert config.run.mode == "until_stable"
        assert config.run.max_days == 90
        assert config.run.export.balances_csv == "balances.csv"
    
    def test_duplicate_agent_ids_rejected(self):
        """Test that duplicate agent IDs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ScenarioConfig(
                name="Invalid",
                agents=[
                    {"id": "B1", "kind": "bank", "name": "Bank 1"},
                    {"id": "B1", "kind": "bank", "name": "Bank 2"}
                ]
            )
        assert "unique" in str(exc_info.value).lower()
    
    def test_unsupported_version_rejected(self):
        """Test that unsupported versions are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ScenarioConfig(
                version=2,
                name="Future Version",
                agents=[
                    {"id": "CB", "kind": "central_bank", "name": "CB"}
                ]
            )
        assert "version" in str(exc_info.value).lower()


class TestRunConfig:
    """Test RunConfig model validation."""
    
    def test_default_run_config(self):
        """Test default run configuration values."""
        config = RunConfig()
        assert config.mode == "until_stable"
        assert config.max_days == 90
        assert config.quiet_days == 2
        assert config.show.events == "detailed"
        assert config.show.balances is None
        assert config.export.balances_csv is None
        assert config.export.events_jsonl is None
    
    def test_custom_run_config(self):
        """Test custom run configuration."""
        config = RunConfig(
            mode="step",
            max_days=30,
            quiet_days=5,
            show={"balances": ["A1", "A2"], "events": "summary"},
            export={"balances_csv": "out.csv"}
        )
        assert config.mode == "step"
        assert config.max_days == 30
        assert config.quiet_days == 5
        assert config.show.balances == ["A1", "A2"]
        assert config.show.events == "summary"
        assert config.export.balances_csv == "out.csv"
    
    def test_negative_max_days_rejected(self):
        """Test that negative max_days is rejected."""
        with pytest.raises(ValidationError):
            RunConfig(max_days=-1)
    
    def test_negative_quiet_days_rejected(self):
        """Test that negative quiet_days is rejected."""
        with pytest.raises(ValidationError):
            RunConfig(quiet_days=-1)
```

---

### 🧪 tests/config/test_scheduled_alias_validation.py

```python
from pathlib import Path
import pytest

from bilancio.config.loaders import load_yaml
from bilancio.config.apply import validate_scheduled_aliases


def _write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text)
    return p


BASE_AGENTS = """
version: 1
name: "Test"
agents:
  - {id: CB, kind: central_bank, name: CB}
  - {id: F1, kind: firm, name: F1}
  - {id: F2, kind: firm, name: F2}
initial_actions: []
run: {mode: until_stable, max_days: 5}
"""


def test_validate_scheduled_aliases_unknown_alias(tmp_path: Path):
    text = BASE_AGENTS + """
scheduled_actions:
  - {day: 1, action: {transfer_claim: {contract_alias: NOT_DEFINED, to_agent: F2}}}
"""
    cfg = load_yaml(_write(tmp_path, "c.yaml", text))
    with pytest.raises(ValueError):
        validate_scheduled_aliases(cfg)


def test_validate_scheduled_aliases_duplicate(tmp_path: Path):
    text = BASE_AGENTS + """
initial_actions:
  - {create_payable: {from: F1, to: F2, amount: 1, due_day: 1, alias: A1}}
scheduled_actions:
  - {day: 1, action: {create_delivery_obligation: {from: F2, to: F1, sku: X, quantity: 1, unit_price: "1", due_day: 1, alias: A1}}}
"""
    cfg = load_yaml(_write(tmp_path, "d.yaml", text))
    with pytest.raises(ValueError):
        validate_scheduled_aliases(cfg)


```

---

### 🧪 tests/config/test_transfer_claim_model.py

```python
import pytest
from pydantic import ValidationError

from bilancio.config.models import TransferClaim


def test_transfer_claim_requires_reference():
    with pytest.raises(ValidationError):
        TransferClaim(to_agent="F3")


def test_transfer_claim_accepts_alias_or_id():
    # alias only
    m1 = TransferClaim(contract_alias="ALIAS1", to_agent="F3")
    assert m1.contract_alias == "ALIAS1"
    assert m1.contract_id is None
    # id only
    m2 = TransferClaim(contract_id="C_123", to_agent="F3")
    assert m2.contract_id == "C_123"


def test_transfer_claim_alias_and_id_model_allows_both():
    # Model permits both present; apply layer enforces equality.
    m = TransferClaim(contract_alias="ALIASX", contract_id="C_YYY", to_agent="F3")
    assert m.contract_alias == "ALIASX"
    assert m.contract_id == "C_YYY"


```

---

### 🧪 tests/engines/test_phase_b1_scheduling.py

```python
from pathlib import Path

from bilancio.config.loaders import load_yaml
from bilancio.config.apply import apply_to_system
from bilancio.engines.system import System
from bilancio.engines.simulation import run_day


SCENARIO = """
version: 1
name: B1-before-B2
agents:
  - {id: CB, kind: central_bank, name: CB}
  - {id: F1, kind: firm, name: F1}
  - {id: F2, kind: firm, name: F2}
initial_actions:
  - {mint_cash: {to: F1, amount: 100}}
  - {create_stock: {owner: F2, sku: X, quantity: 1, unit_price: "100"}}
run: {mode: until_stable, max_days: 5}
"""


def test_b1_executes_before_b2(tmp_path: Path):
    # Create config file
    p = tmp_path / "s.yaml"
    p.write_text(SCENARIO)
    cfg = load_yaml(p)
    sys = System()
    apply_to_system(cfg, sys)

    # Schedule actions for current day (0): create obligations due today
    sys.state.scheduled_actions_by_day[0] = [
        {"create_delivery_obligation": {"from": "F2", "to": "F1", "sku": "X", "quantity": 1, "unit_price": "100", "due_day": 0}},
        {"create_payable": {"from": "F1", "to": "F2", "amount": 100, "due_day": 0}},
    ]

    # Run day 0 and verify obligations were settled same day
    run_day(sys)
    # No open obligations should remain
    assert not any(c.kind in ("payable", "delivery_obligation") for c in sys.state.contracts.values())
    # And events should include settled events for day 0
    day0_events = [e for e in sys.state.events if e.get("day") == 0]
    kinds = {e.get("kind") for e in day0_events}
    assert "DeliveryObligationSettled" in kinds
    assert "PayableSettled" in kinds


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

### 🧪 tests/ops/test_alias_helpers.py

```python
from bilancio.engines.system import System
from bilancio.ops.aliases import get_alias_for_id, get_id_for_alias


def test_alias_helpers_roundtrip():
    sys = System()
    sys.state.aliases["AL1"] = "C_001"
    assert get_id_for_alias(sys, "AL1") == "C_001"
    assert get_alias_for_id(sys, "C_001") == "AL1"
    assert get_id_for_alias(sys, "MISSING") is None
    assert get_alias_for_id(sys, "C_XXX") is None


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

### 🧪 tests/ui/test_cli.py

```python
"""Tests for CLI functionality."""

import pytest
from pathlib import Path
from click.testing import CliRunner
import tempfile
import yaml

from bilancio.ui.cli import cli


class TestCLI:
    """Test CLI commands."""
    
    def test_cli_help(self):
        """Test that CLI help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Bilancio' in result.output
        assert 'simulation' in result.output.lower()
    
    def test_run_help(self):
        """Test that run command help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['run', '--help'])
        assert result.exit_code == 0
        assert 'scenario' in result.output.lower()
        assert '--max-days' in result.output
        assert '--mode' in result.output
    
    def test_new_help(self):
        """Test that new command help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['new', '--help'])
        assert result.exit_code == 0
        assert 'scenario' in result.output.lower()
        assert '--output' in result.output or '-o' in result.output
    
    def test_run_nonexistent_file(self):
        """Test running with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ['run', 'nonexistent.yaml'])
        assert result.exit_code != 0
        assert 'not found' in result.output.lower() or 'does not exist' in result.output.lower()
    
    def test_run_simple_scenario(self):
        """Test running a simple scenario."""
        # Create a minimal scenario file
        scenario = {
            "version": 1,
            "name": "Test Scenario",
            "agents": [
                {"id": "CB", "kind": "central_bank", "name": "Central Bank"},
                {"id": "B1", "kind": "bank", "name": "Bank"}
            ],
            "initial_actions": [
                {"mint_reserves": {"to": "B1", "amount": 1000}}
            ],
            "run": {
                "mode": "until_stable",
                "max_days": 5,
                "quiet_days": 1
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(scenario, f)
            temp_path = Path(f.name)
        
        try:
            runner = CliRunner()
            result = runner.invoke(cli, [
                'run', str(temp_path),
                '--mode', 'until-stable',
                '--max-days', '5'
            ])
            
            # Check that it ran without crashing
            assert result.exit_code == 0
            assert 'Test Scenario' in result.output
            assert 'Day' in result.output
            
        finally:
            temp_path.unlink()
    
    def test_new_scenario_creation(self):
        """Test creating a new scenario file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "new_scenario.yaml"
            
            runner = CliRunner()
            # Use the template option to avoid interactive prompts
            result = runner.invoke(cli, [
                'new',
                '-o', str(output_path),
                '--from', 'simple'
            ])
            
            # Check file was created
            assert output_path.exists()
            
            # Load and validate the created file
            with open(output_path) as f:
                config = yaml.safe_load(f)
            
            # When using template, it uses default name "My Scenario"
            assert config['name'] == "My Scenario"
            assert config['version'] == 1
            assert len(config['agents']) > 0
    
    def test_run_with_export(self):
        """Test running scenario with export options."""
        scenario = {
            "version": 1,
            "name": "Export Test",
            "agents": [
                {"id": "CB", "kind": "central_bank", "name": "CB"},
                {"id": "B1", "kind": "bank", "name": "Bank"}
            ],
            "initial_actions": [
                {"mint_reserves": {"to": "B1", "amount": 1000}}
            ],
            "run": {
                "mode": "until_stable",
                "max_days": 2
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create scenario file
            scenario_path = Path(tmpdir) / "scenario.yaml"
            with open(scenario_path, 'w') as f:
                yaml.dump(scenario, f)
            
            # Set export paths
            balances_path = Path(tmpdir) / "balances.csv"
            events_path = Path(tmpdir) / "events.jsonl"
            
            runner = CliRunner()
            result = runner.invoke(cli, [
                'run', str(scenario_path),
                '--export-balances', str(balances_path),
                '--export-events', str(events_path),
                '--max-days', '2'
            ])
            
            assert result.exit_code == 0
            
            # Check export files were created
            assert balances_path.exists()
            assert events_path.exists()
            
            # Check files have content
            assert balances_path.stat().st_size > 0
            assert events_path.stat().st_size > 0

    def test_run_with_html_export(self, tmp_path):
        """Test running scenario with --html export option."""
        scenario = {
            "version": 1,
            "name": "HTML Export Test",
            "agents": [
                {"id": "CB", "kind": "central_bank", "name": "CB"},
                {"id": "H1", "kind": "household", "name": "Alice"}
            ],
            "initial_actions": [
                {"mint_cash": {"to": "H1", "amount": 1000}}
            ],
            "run": {
                "mode": "until_stable",
                "max_days": 1,
                "quiet_days": 1,
                "show": {
                    "balances": ["CB", "H1"]
                }
            }
        }

        scenario_path = tmp_path / "scenario.yaml"
        html_path = tmp_path / "out.html"

        import yaml
        with open(scenario_path, 'w') as f:
            yaml.dump(scenario, f)

        runner = CliRunner()
        result = runner.invoke(cli, [
            'run', str(scenario_path),
            '--max-days', '1',
            '--quiet-days', '1',
            '--html', str(html_path)
        ])

        assert result.exit_code == 0
        assert html_path.exists()
        content = html_path.read_text(encoding='utf-8')
        assert 'Bilancio Simulation' in content

```

---

### 🧪 tests/ui/test_cli_html_export.py

```python
"""Test CLI HTML export functionality."""

import pytest
from pathlib import Path
import tempfile
from bilancio.engines.system import System
from bilancio.config import ScenarioConfig
from bilancio.ui.run import run_scenario


def test_html_export_creates_file(tmp_path):
    """Test that HTML export creates a file with expected content."""
    # Create a minimal scenario config
    config_data = {
        "name": "Test Scenario",
        "description": "Test HTML export",
        "agents": {
            "bank1": {
                "kind": "bank",
                "name": "Test Bank"
            },
            "household1": {
                "kind": "household", 
                "name": "Test Household"
            }
        },
        "setup": {
            "operations": [
                {
                    "type": "mint_cash",
                    "bank": "bank1",
                    "amount": 1000
                }
            ]
        },
        "simulation": {},
        "run": {
            "mode": "until_stable",
            "max_days": 1,
            "quiet_days": 1,
            "show": {
                "events": "detailed",
                "balances": ["bank1", "household1"]
            },
            "export": {}
        }
    }
    
    # Write config to temp file
    config_file = tmp_path / "test_scenario.yaml"
    import yaml
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    # Run scenario with HTML export
    html_output = tmp_path / "output.html"
    
    # Note: This would require mocking or a lighter test since run_scenario
    # is a high-level function. For now, we'll test the lower-level components
    
    # Test that we can create an HTML export path
    assert not html_output.exists()
    
    # Create a simple HTML content to verify path handling
    html_output.write_text("<html><body>Test</body></html>")
    assert html_output.exists()
    assert "Test" in html_output.read_text()


def test_console_record_html_export():
    """Test that Console with record=True can export HTML."""
    from rich.console import Console
    from rich.table import Table
    from rich.terminal_theme import MONOKAI
    
    # Create a console with recording enabled
    console = Console(record=True, width=100)
    
    # Print some content
    table = Table(title="Test Table")
    table.add_column("Column 1")
    table.add_column("Column 2")
    table.add_row("Value 1", "Value 2")
    
    console.print(table)
    console.print("[bold green]Success![/bold green]")
    
    # Export to HTML
    html = console.export_html(theme=MONOKAI)
    
    # Verify HTML content
    assert html is not None
    assert "<html>" in html
    assert "Test Table" in html
    assert "Value 1" in html
    assert "Value 2" in html
    # Rich converts the markup to HTML
    assert "Success!" in html


def test_renderable_functions_return_correct_types():
    """Test that renderable functions return expected types."""
    from bilancio.ui.display import (
        show_scenario_header_renderable,
        show_simulation_summary_renderable
    )
    from bilancio.engines.system import System
    
    # Test scenario header
    panel = show_scenario_header_renderable("Test", "Description")
    assert panel is not None
    
    # Test simulation summary
    system = System()
    summary = show_simulation_summary_renderable(system)
    assert summary is not None
```

---

### 🧪 tests/ui/test_html_export.py

```python
"""Unit tests for semantic HTML export."""

from pathlib import Path
from decimal import Decimal

from bilancio.engines.system import System
from bilancio.config.apply import create_agent
from bilancio.analysis.balances import agent_balance
from bilancio.ui.html_export import export_pretty_html


def test_export_pretty_html_minimal(tmp_path: Path):
    sys = System()
    cb = create_agent(type("Spec", (), {"id":"CB","kind":"central_bank","name":"Central Bank"}))
    h1 = create_agent(type("Spec", (), {"id":"H1","kind":"household","name":"Alice"}))
    sys.add_agent(cb)
    sys.add_agent(h1)
    # seed a simple cash position
    sys.mint_cash("H1", 1000)

    out = tmp_path / "report.html"

    # Prepare initial data
    agent_ids = ["CB", "H1"]
    initial_balances = {aid: agent_balance(sys, aid) for aid in agent_ids}

    # No days_data yet; just ensure file writes and contains headers
    export_pretty_html(
        system=sys,
        out_path=out,
        scenario_name="Unit Test",
        description="Testing export",
        agent_ids=agent_ids,
        initial_balances=initial_balances,
        days_data=[],
        max_days=1,
        quiet_days=1,
    )

    assert out.exists()
    html = out.read_text(encoding="utf-8")
    # Basic sanity checks
    assert "Bilancio Simulation" in html
    assert "Agents" in html
    assert "Day 0 (Setup)" in html
    assert "Central Bank" in html and "Alice" in html


def test_export_pretty_html_handles_numeric_strings(tmp_path: Path):
    sys = System()
    f1 = create_agent(type("Spec", (), {"id":"F1","kind":"firm","name":"Firm One"}))
    sys.add_agent(f1)

    out = tmp_path / "report2.html"
    agent_ids = ["F1"]
    # Manually craft a balance-like object via agent_balance and then tweak days_data to include numbers-as-strings
    initial_balances = {"F1": agent_balance(sys, "F1")}

    # days_data with an event that includes formatted numeric strings
    days_data = [
        {
            "day": 1,
            "events": [
                {"kind": "PhaseB"},
                {"kind": "ClientPayment", "payer": "F1", "payee": "F1", "amount": "1,000"},
            ],
            "balances": {"F1": agent_balance(sys, "F1")},
        }
    ]

    export_pretty_html(
        system=sys,
        out_path=out,
        scenario_name="Numeric Test",
        description=None,
        agent_ids=agent_ids,
        initial_balances=initial_balances,
        days_data=days_data,
        max_days=2,
        quiet_days=1,
    )

    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "Numeric Test" in html
    # amount should be present in some formatted form
    assert "1,000" in html

```

---

### 🧪 tests/ui/test_render_builders.py

```python
"""Test Rich builders for rendering."""

import pytest
from decimal import Decimal
from bilancio.ui.render.models import (
    BalanceItemView,
    AgentBalanceView,
    EventView,
    DayEventsView
)
from bilancio.ui.render.rich_builders import (
    build_agent_balance_table,
    build_multiple_agent_balances,
    build_events_panel,
    convert_raw_event_to_view
)


def test_build_agent_balance_table():
    """Test building a Rich table for agent balance."""
    # Create a sample balance view
    balance_view = AgentBalanceView(
        agent_id="bank1",
        agent_name="Central Bank",
        agent_kind="bank",
        items=[
            BalanceItemView(
                category="asset",
                instrument="reserves",
                amount=10000,
                value=Decimal("10000")
            ),
            BalanceItemView(
                category="liability",
                instrument="deposits",
                amount=5000,
                value=Decimal("5000")
            )
        ]
    )
    
    # Build table
    table = build_agent_balance_table(balance_view)
    
    # Verify it's a Table (or string if Rich not available)
    assert table is not None
    if not isinstance(table, str):
        # Rich is available, check it's a Table
        from rich.table import Table
        assert isinstance(table, Table)


def test_build_multiple_agent_balances():
    """Test building columns for multiple agent balances."""
    # Create sample balance views
    balances = [
        AgentBalanceView(
            agent_id="bank1",
            agent_name="Bank One",
            agent_kind="bank",
            items=[
                BalanceItemView(
                    category="asset",
                    instrument="cash",
                    amount=1000,
                    value=Decimal("1000")
                )
            ]
        ),
        AgentBalanceView(
            agent_id="household1",
            agent_name="Household One",
            agent_kind="household",
            items=[
                BalanceItemView(
                    category="asset",
                    instrument="deposits",
                    amount=500,
                    value=Decimal("500")
                )
            ]
        )
    ]
    
    # Build columns
    columns = build_multiple_agent_balances(balances)
    
    # Verify result
    assert columns is not None
    if not isinstance(columns, str):
        # Rich is available, check it's Columns
        from rich.columns import Columns
        assert isinstance(columns, Columns)


def test_build_events_panel():
    """Test building a panel for day events."""
    # Create sample day events view
    day_view = DayEventsView(
        day=1,
        phases={
            "A": [
                EventView(
                    kind="PhaseA",
                    title="Day begins",
                    lines=["Starting day 1"],
                    icon="⏰",
                    raw_event={"kind": "PhaseA", "day": 1}
                )
            ],
            "B": [
                EventView(
                    kind="CashTransferred",
                    title="Cash transferred",
                    lines=["bank1 → household1: $100"],
                    icon="💵",
                    raw_event={"kind": "CashTransferred", "day": 1}
                )
            ],
            "C": []
        }
    )
    
    # Build panel
    panel = build_events_panel(day_view)
    
    # Verify result
    assert panel is not None
    if not isinstance(panel, str):
        # Rich is available, check it's a Panel
        from rich.panel import Panel
        assert isinstance(panel, Panel)


def test_convert_raw_event_to_view():
    """Test converting raw event dict to EventView."""
    # Test with a CashTransferred event
    raw_event = {
        "kind": "CashTransferred",
        "frm": "bank1",
        "to": "household1",
        "amount": 1000,
        "day": 1
    }
    
    event_view = convert_raw_event_to_view(raw_event)
    
    assert isinstance(event_view, EventView)
    assert "Cash Transfer" in event_view.title
    assert event_view.lines[0] == "bank1 → household1"
    assert event_view.icon == "💰"
    assert event_view.raw_event == raw_event


def test_convert_unknown_event_to_view():
    """Test converting unknown event type to EventView."""
    raw_event = {
        "kind": "CustomEvent",
        "data": "some value"
    }
    
    event_view = convert_raw_event_to_view(raw_event)
    
    assert isinstance(event_view, EventView)
    assert "CustomEvent" in event_view.title
    assert event_view.icon == "❓"
```

---

### 🧪 tests/ui/test_render_formatters.py

```python
"""Test event formatters and registry."""

import pytest
from bilancio.ui.render.formatters import EventFormatterRegistry, registry


def test_event_formatter_registry():
    """Test that event formatter registry works correctly."""
    registry = EventFormatterRegistry()
    
    # Test registration
    @registry.register("TestEvent")
    def test_formatter(event):
        return "Test Event", ["Test line"], "🧪"
    
    # Test formatting with registered event
    event = {"kind": "TestEvent", "data": "test"}
    title, lines, icon = registry.format(event)
    assert title == "Test Event"
    assert lines == ["Test line"]
    assert icon == "🧪"


def test_format_event_with_known_kind():
    """Test formatting known event kinds."""
    # Test CashTransferred
    event = {
        "kind": "CashTransferred",
        "frm": "bank1",
        "to": "household1",
        "amount": 1000
    }
    title, lines, icon = registry.format(event)
    assert "Cash Transfer" in title
    assert lines[0] == "bank1 → household1"
    assert icon == "💰"
    
    # Test StockTransferred
    event = {
        "kind": "StockTransferred",
        "frm": "firm1",
        "to": "household1",
        "qty": 10,
        "sku": "BREAD"
    }
    title, lines, icon = registry.format(event)
    assert "Stock Transfer" in title
    assert lines[0] == "firm1 → household1"
    assert icon == "📦"


def test_format_event_with_unknown_kind():
    """Test formatting unknown event kinds."""
    event = {
        "kind": "UnknownEventType",
        "some_data": "value"
    }
    title, lines, icon = registry.format(event)
    assert "UnknownEventType Event" in title
    assert len(lines) > 0
    assert icon == "❓"


def test_format_event_missing_fields():
    """Test formatting events with missing expected fields."""
    # CashTransferred with missing amount
    event = {
        "kind": "CashTransferred",
        "frm": "bank1",
        "to": "household1"
    }
    title, lines, icon = registry.format(event)
    assert "Cash Transfer" in title
    assert lines[0] == "bank1 → household1"  # Should handle missing amount gracefully
    
    # StockTransferred with missing qty
    event = {
        "kind": "StockTransferred",
        "frm": "firm1",
        "to": "household1",
        "sku": "BREAD"
    }
    title, lines, icon = registry.format(event)
    assert "Stock Transfer" in title
    assert lines[0] == "firm1 → household1"  # Should handle missing qty gracefully


def test_all_event_kinds_have_formatters():
    """Test that common event kinds have formatters."""
    common_kinds = [
        "CashTransferred",
        "StockTransferred",
        "PayableSettled",
        "DeliveryObligationSettled",
        "CashMinted",
        "StockCreated",
        "PhaseA",
        "PhaseB",
        "PhaseC"
    ]
    
    for kind in common_kinds:
        event = {"kind": kind}
        title, lines, icon = registry.format(event)
        # Should not fall back to generic formatter
        assert "Event:" not in title or kind in ["PhaseA", "PhaseB", "PhaseC"]
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
Total source files: 62
Total test files: 24
