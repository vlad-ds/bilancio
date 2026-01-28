# Banks + Dealers Integration Specification

## Overview

This document specifies the integration of the BankDealer module with the dealer ring simulation.
The goal is to replace the current "cash" abstraction with bank deposits, enabling:
- Interest-bearing deposits
- Bank lending to cover shortfalls
- Interbank settlement of payments
- Rate-sensitive trader decision-making

## Architecture

### Bank Structure

| Bank | Role | Clients |
|------|------|---------|
| Bank 1 | Trader bank | Traders H1, H4, H7, H10, ... |
| Bank 2 | Trader bank | Traders H2, H5, H8, H11, ... |
| Bank 3 | Trader bank | Traders H3, H6, H9, H12, ... |
| Bank 4 | Dealer bank | All Dealers, all VBTs |

**Trader assignment rule**: `H_i → Bank ((i-1) mod 3) + 1`

This maximizes inter-bank payments (consecutive traders are at different banks).

### Elimination of Cash

- Traders hold **deposits** at their assigned bank, not cash
- All payments flow through deposits
- Deposits earn interest (after 2-day grace period)
- Interest rate locked at deposit time

### Central Bank Corridor

```
CB lending rate (r_ceiling)     ─────────────────
       ↑
       │  Bank loan rates
       │
       │  Interbank rate
       │
       │  Bank deposit rates
       ↓
CB deposit rate (r_floor)       ─────────────────
```

Banks earn on excess reserves at `r_floor`, borrow from CB at `r_ceiling`.

## Trader Decision-Making

### Eligibility Categories

1. **Distress Sell**: Has shortfall AND has tickets → must liquidate
2. **Borrow Eligible**: Has shortfall, prefers borrowing over selling
3. **Yield Sell**: No shortfall, but deposit yield > payable yield → liquidate
4. **Yield Buy**: No shortfall, payable yield > deposit yield → invest
5. **Deposit Eligible**: Excess cash should go to deposits

### Decision Logic

#### Has Shortfall (payment due today)

```
shortfall = payment_due - deposit_balance

If has_tickets:
    sell_cost = E[payoff] - bid  # opportunity cost of selling
    borrow_cost = shortfall × r_loan × τ  # interest cost

    If borrow_cost < sell_cost: BORROW
    Else: SELL
Else:
    BORROW (or DEFAULT if no credit)
```

#### No Shortfall, Has Payables

```
For each payable with τ days to maturity:
    hold_value = (1 - P_default) × face
    sell_deposit_value = bid × (1 + r_deposit)^τ

    If sell_deposit_value > hold_value: SELL (yield-based)
```

#### No Shortfall, Has Excess Deposits

```
surplus = deposits - buffer - near_term_obligations

For available payables at ask price:
    buy_value = (1 - P_default) × face
    hold_deposit_value = ask × (1 + r_deposit)^τ

    If buy_value > hold_deposit_value: BUY (yield-based)
```

## Loan Mechanics

### Loan Parameters
- **Tenor**: Fixed = max payable maturity in system
- **Credit limit**: Purpose-bound (≤ shortfall amount)
- **No refinancing**: Must repay at maturity

### Loan Lifecycle
1. Trader requests loan for shortfall amount
2. Bank credits deposit (loan-origin cohort)
3. Loan matures at fixed tenor
4. Repayment: principal × (1 + r_loan)
5. Reserves flow: borrower's bank → lender's bank

## Deposit Mechanics

### Deposit Parameters
- **Interest accrual**: After 2-day grace period
- **Rate lock**: Rate at deposit time applies for life of deposit
- **On-demand**: Withdrawable anytime for payments

### Interest Calculation
```
If deposit_age >= 2 days:
    interest = principal × stamped_rate
    Credited every 2 days
```

## Interbank Settlement

### During Day
When H1 (Bank1) pays H4 (Bank2):
1. Bank1 debits H1's deposit
2. Bank2 credits H4's deposit
3. Bank1 records payable to Bank2
4. Bank2 records receivable from Bank1

### End of Day Settlement
```
For each bank pair (Bi, Bj) where i < j:
    net = Bi.owes(Bj) - Bj.owes(Bi)

    If net > 0:
        Bi.reserves -= net
        Bj.reserves += net
    Elif net < 0:
        Bj.reserves -= |net|
        Bi.reserves += |net|

    Clear bilateral positions
```

### Settlement Order
1. Bank1 ↔ Bank2
2. Bank2 ↔ Bank3
3. Bank3 ↔ Bank4 (dealer bank)
4. Bank1 ↔ Bank3
5. Bank1 ↔ Bank4
6. Bank2 ↔ Bank4

### CB as Lender of Last Resort
If bank short on reserves after netting:
```
shortfall = required_transfer - reserves
If shortfall > 0:
    CB creates reserves: bank.reserves += shortfall
    Bank records CB borrowing cohort at r_ceiling
```

## Default Procedure

### Trigger
Trader cannot meet obligations (after trading and borrowing attempts).

### Waterfall

1. **Liquidate assets**: Sell all held payables to dealer/VBT at bid
2. **Pool proceeds**: liquidation_proceeds + remaining_deposits
3. **List all claims**:
   - Bank loans maturing today
   - Payable obligations maturing today
4. **Weight by maturity**: `w_i = 1 / (days_to_maturity + 1)`
   - Claims due today: weight = 1.0
   - Claims due in 5 days: weight = 0.167
5. **Distribute pro-rata within weights**:
   ```
   claim_i.payment = (w_i / Σw) × pool
   ```

### Equal Treatment
- Loans and payables with same maturity rank equally
- Share pro-rata within maturity tier

## Day Loop (Integrated)

```
Day N:
  Phase 1: Update maturities (existing)

  Phase 2: Dealer pre-computation (existing)

  Phase 3: Interest accrual
    - Credit deposit interest (2-day cohorts)
    - Accrue loan interest

  Phase 4: Loan maturities
    - Process loan repayments due today
    - Reserves flow between banks

  Phase 5: Compute eligibility (with rates)
    - distress_sell, borrow_eligible, yield_sell, yield_buy

  Phase 6: Banking operations
    - Process borrow_eligible → create loans
    - (Deposits happen implicitly via payments)

  Phase 7: Trading order flow (existing + modifications)
    - Sellers = distress_sell ∪ yield_sell
    - Buyers = yield_buy
    - Order crossing, then residual flow

  Phase 8: Settlement
    - Pay obligations from deposits
    - Handle defaults with waterfall

  Phase 9: Interbank settlement
    - Net bilateral positions
    - Transfer reserves
    - CB borrowing if needed

  Phase 10: VBT anchor update (existing)
```

## Data Model Changes

### TraderState Extensions
```python
@dataclass
class TraderState:
    # Existing
    agent_id: AgentId
    tickets_owned: list[Ticket]
    obligations: list[Ticket]

    # New
    bank_id: str  # Which bank holds deposits
    deposit_balance: Decimal  # Replaces cash
    outstanding_loans: list[Loan]  # Loans from bank

    # Remove
    # cash: Decimal  # Eliminated
```

### New Loan Type
```python
@dataclass
class TraderLoan:
    loan_id: str
    borrower_id: AgentId
    bank_id: str
    principal: Decimal
    rate: Decimal  # Locked at issuance
    issuance_day: int
    maturity_day: int  # = issuance + max_payable_tenor
```

### Bank State Extensions
```python
@dataclass
class IntegratedBankState(BankDealerState):
    # New: interbank positions
    interbank_payables: dict[str, Decimal]  # bank_id → amount owed
    interbank_receivables: dict[str, Decimal]  # bank_id → amount due

    # New: client tracking
    client_deposits: dict[AgentId, Decimal]  # client → total balance
    client_loans: dict[AgentId, list[TraderLoan]]  # client → loans
```

## Configuration

```python
@dataclass
class BankDealerRingConfig(DealerRingConfig):
    # Bank structure
    n_trader_banks: int = 3

    # CB corridor
    cb_deposit_rate: Decimal  # r_floor
    cb_lending_rate: Decimal  # r_ceiling

    # Loan parameters
    loan_tenor_days: int  # Fixed = max_payable_maturity

    # Interest
    deposit_grace_period: int = 2  # Days before interest accrues

    # Bank internal
    reserve_target_ratio: Decimal  # R^tar / total_deposits
    symmetric_capacity_ratio: Decimal  # X* / R^tar
```

## Metrics Extensions

New metrics to track:
- Total bank lending volume
- Interbank settlement volume
- CB borrowing (LOLR usage)
- Interest income/expense by trader
- Borrow vs sell decisions
- Yield-based trading volume
