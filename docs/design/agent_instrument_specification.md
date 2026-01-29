# Agent-Instrument Specification Framework

When introducing a new **agent type** or **instrument type** to the bilancio system, you must systematically define all relationships. This document provides a checklist and template for ensuring completeness.

## Core Principle

Every (Agent, Instrument) pair must be explicitly specified:
- Can this agent hold this instrument? As asset or liability?
- How does the agent acquire/create it?
- What happens during the holding period?
- What happens at maturity/settlement?
- How does this instrument affect the agent's decision-making?

---

## Part 1: Introducing a New Agent Type

### 1.1 Agent Definition

```yaml
agent:
  name: [AgentTypeName]
  description: [Economic role and purpose]

  # Core state
  state:
    - field_name: [type, description]

  # What bank (if any) does this agent use?
  banking_relationship:
    has_bank_account: [true/false]
    bank_assignment_rule: [how assigned to a bank]
```

### 1.2 Instrument Relationship Matrix

For EACH existing instrument, specify:

| Instrument | Position | Can Create? | Can Hold? | Can Transfer? | Settlement Role |
|------------|----------|-------------|-----------|---------------|-----------------|
| Payable    | A/L/NA   | Y/N         | Y/N       | Y/N           | Issuer/Holder/NA |
| Deposit    | A/L/NA   | Y/N         | Y/N       | Y/N           | Depositor/Bank/NA |
| Loan       | A/L/NA   | Y/N         | Y/N       | Y/N           | Borrower/Lender/NA |
| Reserve    | A/L/NA   | Y/N         | Y/N       | Y/N           | ... |
| [etc.]     | ...      | ...         | ...       | ...           | ... |

Where:
- **Position**: A = Asset, L = Liability, NA = Not Applicable
- **Settlement Role**: What role does this agent play when the instrument settles?

### 1.3 Decision-Making Specification

For each decision the agent makes, specify:

```yaml
decisions:
  - name: [decision_name]
    trigger: [when is this decision made?]
    inputs:
      - [list of state variables considered]
    instruments_considered:
      - instrument: [name]
        how_used: [what role does this instrument play in the decision?]
    outputs:
      - [action taken]

  # Example:
  - name: cover_shortfall
    trigger: "shortfall > 0 at start of trading phase"
    inputs:
      - deposits_available
      - obligations_due_today
      - tickets_owned
    instruments_considered:
      - instrument: Payable (owned)
        how_used: "Can sell to raise liquidity; compare EV vs bid"
      - instrument: Loan
        how_used: "Can borrow to cover gap; compare interest cost vs sell cost"
      - instrument: Deposit
        how_used: "Source of funds; compare deposit rate vs payable yield"
    outputs:
      - SELL ticket(s) and/or
      - BORROW from bank and/or
      - DEFAULT if still short
```

### 1.4 Lifecycle Events

For each lifecycle event, specify what happens to this agent:

```yaml
lifecycle_events:
  day_start:
    - [actions at start of day]

  interest_accrual:
    - instrument: [which instruments accrue interest?]
      direction: [pay/receive]
      timing: [when does accrual happen?]

  trading_phase:
    - eligibility: [when is agent eligible to trade?]
      sell_criteria: [...]
      buy_criteria: [...]

  settlement_phase:
    - as_issuer: [what happens when agent's liabilities mature?]
      as_holder: [what happens when agent's assets mature?]

  default:
    - trigger: [what causes default?]
      waterfall: [priority of claims]
      recovery: [how are assets liquidated?]
```

---

## Part 2: Introducing a New Instrument Type

### 2.1 Instrument Definition

```yaml
instrument:
  name: [InstrumentName]
  description: [Economic purpose]

  # Core attributes
  attributes:
    - face_value: [principal amount]
    - maturity: [when does it settle?]
    - rate: [interest/yield rate, if any]
    - issuer: [who creates the liability?]
    - holder: [who owns the asset?]

  # Classification
  classification:
    tradeable: [true/false - can it be sold in secondary market?]
    interest_bearing: [true/false]
    secured: [true/false - is there collateral?]
```

### 2.2 Agent Relationship Matrix

For EACH existing agent type, specify:

| Agent Type | Can Issue? | Can Hold? | Balance Sheet Entry | Settlement Action |
|------------|------------|-----------|---------------------|-------------------|
| Trader     | Y/N        | Y/N       | Asset/Liability/NA  | [what happens]    |
| Bank       | Y/N        | Y/N       | Asset/Liability/NA  | [what happens]    |
| Dealer     | Y/N        | Y/N       | Asset/Liability/NA  | [what happens]    |
| VBT        | Y/N        | Y/N       | Asset/Liability/NA  | [what happens]    |
| CentralBank| Y/N        | Y/N       | Asset/Liability/NA  | [what happens]    |

### 2.3 Lifecycle Specification

```yaml
lifecycle:
  creation:
    trigger: [what causes this instrument to be created?]
    issuer_effect:
      balance_sheet: [+/- which entries]
      cash_flow: [immediate cash effect?]
    holder_effect:
      balance_sheet: [+/- which entries]
      cash_flow: [immediate cash effect?]

  holding_period:
    interest_accrual:
      timing: [when does interest accrue?]
      rate_source: [where does the rate come from?]
      issuer_effect: [interest expense]
      holder_effect: [interest income]

    transferability:
      can_transfer: [true/false]
      market: [where is it traded?]
      price_discovery: [how is price determined?]
      transfer_effect:
        seller: [balance sheet changes]
        buyer: [balance sheet changes]
        intermediary: [dealer/market maker effects]

  maturity:
    trigger: [what defines maturity?]
    full_settlement:
      issuer_action: [pay principal + interest]
      holder_action: [receive payment]
      instrument_disposition: [removed from system?]

    partial_settlement:
      trigger: [when does partial occur?]
      recovery_rate: [how computed?]
      distribution: [how allocated among holders?]

    rollover:
      trigger: [when does rollover occur?]
      new_instrument: [what is created?]
      terms: [how are new terms set?]
```

### 2.4 Default Handling

```yaml
default:
  definition: [what constitutes default on this instrument?]

  priority:
    rank: [where in the claim hierarchy?]
    pari_passu_with: [which other instruments rank equally?]
    senior_to: [which instruments are junior?]
    junior_to: [which instruments are senior?]

  recovery:
    collateral: [is there collateral?]
    liquidation_price: [how is recovery value determined?]
    distribution_rule: [pro-rata, waterfall, etc.]
```

### 2.5 Interaction with Other Instruments

For each OTHER instrument, specify:

```yaml
instrument_interactions:
  - other_instrument: [name]
    relationship: [substitutes/complements/independent]
    decision_tradeoff: |
      [When would an agent choose this instrument over the other?
       What are the comparative costs/benefits?]

    example:
      scenario: [concrete example]
      choice_logic: [how agent decides]
```

---

## Part 3: Complete Example - Bank Loan

### 3.1 Instrument Definition

```yaml
instrument:
  name: BankLoan
  description: "Credit extended by a bank to a trader, creating money via deposit"

  attributes:
    - principal: Decimal  # Amount borrowed
    - rate: Decimal       # Interest rate (locked at issuance)
    - issuance_day: int   # When loan was issued
    - maturity_day: int   # When repayment is due
    - issuer: Bank        # The lending bank
    - borrower: Trader    # The borrowing trader

  classification:
    tradeable: false      # Loans stay on bank's books
    interest_bearing: true
    secured: false        # Unsecured in current implementation
```

### 3.2 Agent Relationship Matrix

| Agent Type  | Can Issue? | Can Hold? | Balance Sheet Entry | Settlement Action |
|-------------|------------|-----------|---------------------|-------------------|
| Trader      | N (borrows)| Y (liability) | Liability: loans[] | Repay principal+interest |
| Bank        | Y (lends)  | Y (asset)  | Asset: loans_outstanding | Receive repayment |
| Dealer      | N          | N          | NA                  | NA |
| VBT         | N          | N          | NA                  | NA |
| CentralBank | N          | N          | NA                  | NA |

### 3.3 Lifecycle

```yaml
lifecycle:
  creation:
    trigger: "Trader requests loan to cover shortfall"
    issuer_effect:  # Bank
      balance_sheet:
        - loans_outstanding: +principal
        - deposits (to borrower): +principal  # Money creation!
      cash_flow: none (endogenous money)
    holder_effect:  # Trader (as borrower)
      balance_sheet:
        - loans: +principal (liability)
        - deposits: +principal (asset)
      cash_flow: net zero

  holding_period:
    interest_accrual:
      timing: "At loan maturity (simple interest)"
      rate_source: "Bank's loan rate at issuance (locked)"
      issuer_effect: "Interest income = principal × rate"
      holder_effect: "Interest expense = principal × rate"

    transferability:
      can_transfer: false
      rationale: "Loans stay on originating bank's books"

  maturity:
    trigger: "current_day == maturity_day"
    full_settlement:
      issuer_action: "Bank receives principal + interest"
      holder_action: "Trader pays from deposits"
      instrument_disposition: "Loan removed from both balance sheets"

    partial_settlement:
      trigger: "Trader deposits < repayment amount"
      recovery_rate: "Part of default waterfall"
      distribution: "Bank is a creditor in waterfall"

    rollover:
      trigger: "Not implemented - loans don't roll over"
```

### 3.4 Default Handling

```yaml
default:
  definition: "Trader cannot repay loan at maturity"

  priority:
    rank: "Equal with payables of same maturity"
    pari_passu_with: [Payable (same maturity day)]
    senior_to: []
    junior_to: []

  recovery:
    collateral: none
    liquidation_price: "Trader's assets liquidated at dealer bid"
    distribution_rule: "Maturity-weighted pro-rata"
```

### 3.5 Interaction with Other Instruments

```yaml
instrument_interactions:
  - other_instrument: Payable
    relationship: complements
    decision_tradeoff: |
      Loan covers shortfall when selling payables is more expensive.
      Cost comparison:
        - Sell cost = EV - dealer_bid (opportunity cost)
        - Borrow cost = principal × rate × tenor
      Choose lower cost option.

  - other_instrument: Deposit
    relationship: created_together
    decision_tradeoff: |
      Loan creates deposit simultaneously (endogenous money).
      Deposit rate vs loan rate determines net cost of borrowing.

  - other_instrument: Reserve
    relationship: independent
    decision_tradeoff: |
      Trader loans don't directly affect reserves.
      Interbank settlement of loan-created deposits affects reserves.
```

---

## Part 4: Checklist for New Additions

### Adding a New Agent

- [ ] Define agent state (fields, types)
- [ ] For EACH existing instrument:
  - [ ] Can agent issue it? Hold it?
  - [ ] Balance sheet entry (asset/liability)
  - [ ] Settlement role
- [ ] Define decision-making:
  - [ ] What decisions does agent make?
  - [ ] What instruments are considered in each decision?
  - [ ] What is the decision logic?
- [ ] Define lifecycle events:
  - [ ] Day start actions
  - [ ] Interest accrual (pay/receive)
  - [ ] Trading eligibility
  - [ ] Settlement actions (as issuer, as holder)
  - [ ] Default trigger and waterfall position
- [ ] Update existing agents:
  - [ ] Do existing agents need to interact with new agent?
  - [ ] New decision branches?

### Adding a New Instrument

- [ ] Define instrument attributes
- [ ] For EACH existing agent:
  - [ ] Can agent issue it? Hold it?
  - [ ] Balance sheet entry
  - [ ] Settlement action
- [ ] Define lifecycle:
  - [ ] Creation trigger and effects
  - [ ] Holding period (interest, transferability)
  - [ ] Maturity (full, partial, rollover)
- [ ] Define default handling:
  - [ ] Priority/ranking
  - [ ] Recovery mechanism
- [ ] Define interactions with OTHER instruments:
  - [ ] Substitutes? Complements?
  - [ ] Decision tradeoffs
- [ ] Update existing instruments:
  - [ ] Does new instrument affect existing instrument decisions?
  - [ ] New comparison logic needed?

---

## Part 5: Current System Reference

### Agents

| Agent | Description | Bank Account? |
|-------|-------------|---------------|
| Trader | Ring participant, issues and holds payables | Yes (at trader bank) |
| Bank | Holds deposits, issues loans, settles interbank | Yes (reserves at CB) |
| Dealer | Market maker, holds inventory | Yes (at dealer bank) |
| VBT | Value-based trader, provides liquidity | No (cash only) |
| CentralBank | Lender of last resort, sets corridor | NA (issues reserves) |

### Instruments

| Instrument | Issuer | Holder | Tradeable? | Interest? |
|------------|--------|--------|------------|-----------|
| Payable (Ticket) | Trader | Trader/Dealer/VBT | Yes (dealer market) | No (discount) |
| Deposit | Bank | Trader | No | Yes (after 2 days) |
| Loan | Bank | Trader (liability) | No | Yes |
| Reserve | CentralBank | Bank | No | Yes (CB deposit rate) |
| CB Loan | CentralBank | Bank (liability) | No | Yes (CB lending rate) |

### Key Relationships Not Yet Fully Specified

1. **Trader ↔ CB Loan**: Traders don't interact with CB loans directly
2. **Dealer ↔ Deposit**: Dealer bank holds reserves, but dealer inventory is separate
3. **Payable rollover**: Currently no re-issuance after settlement
4. **Loan rollover**: Currently no rollover, just default if can't repay
