# Core Concepts

This document explains the fundamental concepts of the Bilancio framework. It is intended for researchers and practitioners new to the framework who want to understand the domain model before running simulations.

---

## Agents

Agents are the economic actors in a Bilancio simulation. Each agent maintains a balance sheet with assets and liabilities, and can participate in payment transactions. The framework models a hierarchical monetary system where different agent types have different roles and capabilities.

### CentralBank

The **CentralBank** is the monetary authority at the apex of the payment system. It:

- Issues two forms of money: **Cash** (physical currency) and **ReserveDeposits** (electronic balances)
- Provides the ultimate settlement medium for interbank payments
- Cannot default (it is the issuer of the base money)
- Typically has ID `CB` in scenarios

The central bank's balance sheet expansion creates money - when it mints cash or reserves, its liabilities increase while the recipient's assets increase. This is the fundamental mechanism of money creation in the simulation.

### Bank

A **Bank** is a commercial bank that intermediates between the central bank and the real economy. Banks:

- Hold reserve accounts at the central bank (assets)
- Issue deposit liabilities to clients (households and firms)
- Process client payments by debiting payer deposits and crediting payee deposits
- Settle interbank obligations using reserves or overnight credit

When two clients at different banks transact, the banks must settle the net position between them. This creates the interbank payment flows that drive much of the system's dynamics.

### Firm

A **Firm** represents a business entity that participates in economic transactions. Firms can:

- Hold cash and bank deposits (assets)
- Issue and receive **Payables** (trade credit)
- Own and transfer inventory (**StockLots**)
- Create and settle **DeliveryObligations**

In the Kalecki ring model, firms are arranged in a circular payment network where each firm owes its successor, creating a chain of interdependent obligations.

### Household

A **Household** is a consumer agent that:

- Holds cash and bank deposits
- Can receive payables (as a creditor)
- Participates in economic transactions

In many scenarios, households are used as generic economic agents in the ring structure, even when they represent firms conceptually. The distinction affects policy rules but not basic mechanics.

### Dealer

A **Dealer** is a secondary market maker that provides liquidity to the payment system. Dealers:

- Maintain bid/ask quotes for payables (credit instruments)
- Buy payables from agents who need immediate liquidity
- Sell payables to agents seeking investment returns
- Adjust quotes based on inventory levels using the kernel pricing formula

Dealers operate within maturity buckets (short, mid, long) and can execute trades either internally or route them to the VBT when their capacity is exhausted.

### VBT (Value-Based Trader)

The **VBT** (Value-Based Trader) represents outside liquidity providers who trade based on fundamental value. VBTs:

- Provide anchor prices (M for mid, O for spread) that bound dealer quotes
- Absorb excess supply or demand when dealers cannot execute internally
- Have effectively unlimited capacity, ensuring market continuity
- Represent the broader market's valuation of credit instruments

The VBT's role is to prevent the dealer system from collapsing under stress by providing a "lender of last resort" function in the secondary market.

### Treasury

The **Treasury** is a government fiscal agent that:

- Can hold reserve deposits at the central bank
- May issue government obligations
- Participates in monetary operations with the central bank

---

## Financial Instruments

Instruments are the assets and liabilities that appear on agent balance sheets. Each instrument has an **issuer** (liability side) and a **holder** (asset side).

### Cash

**Cash** is physical currency issued by the central bank. Properties:

- **Issuer**: Always the CentralBank
- **Holder**: Any non-bank agent (banks hold reserves, not cash)
- **Settlement**: Universal means of payment, always accepted
- Bearer instrument - ownership transfers by possession

Cash is created when the central bank "mints" it to an agent, increasing both CB liabilities and the recipient's assets.

### BankDeposit

A **BankDeposit** is a liability of a commercial bank representing a customer's balance. Properties:

- **Issuer**: The commercial bank
- **Holder**: A client (firm, household)
- **Settlement**: Primary means of payment for non-cash transactions

When a firm pays another firm via bank transfer, the payer's deposit decreases while the payee's deposit increases. If the parties bank at different institutions, an interbank settlement is required.

### ReserveDeposit

A **ReserveDeposit** is a central bank liability held by commercial banks. Properties:

- **Issuer**: Always the CentralBank
- **Holder**: Banks and Treasury
- **Settlement**: Used for interbank clearing and settlement

Reserves are the settlement medium between banks. When Bank A owes Bank B, the obligation is settled by transferring reserves from A's account to B's account at the central bank.

### Payable

A **Payable** is a credit obligation representing a promise to pay in the future. Properties:

- **Issuer** (debtor): The agent who owes the amount
- **Holder** (creditor): The agent who will receive payment
- **due_day**: When the obligation must be settled
- **holder_id**: Secondary market holder (if transferred)
- **maturity_distance**: Original time to maturity (for rollover)

Payables are the primary instrument for studying settlement dynamics. When a payable matures (day equals due_day), the system attempts to settle it using the debtor's available means of payment.

**Secondary Market Trading**: Payables can be sold to dealers before maturity. The `holder_id` field tracks the current holder, who receives payment at settlement (rather than the original creditor).

### DeliveryObligation

A **DeliveryObligation** represents a promise to deliver physical goods. Properties:

- **Issuer** (debtor): The agent who must deliver
- **Holder** (creditor): The agent who will receive goods
- **sku**: Stock-keeping unit identifier
- **quantity**: Number of units to deliver
- **unit_price**: Value per unit for accounting purposes
- **due_day**: When delivery must occur

Delivery obligations are settled by transferring StockLots from debtor to creditor.

### StockLot

A **StockLot** represents physical inventory. Properties:

- **owner_id**: The agent who owns the stock
- **sku**: Stock-keeping unit identifier
- **quantity**: Number of units
- **unit_price**: Valuation per unit
- **divisible**: Whether partial transfers are allowed

StockLots are not financial instruments (no counterparty) but appear on balance sheets as assets.

---

## Simulation Phases

Each simulation day in Bilancio proceeds through a structured sequence of phases. This models the real-world settlement cycle where different activities occur at different times.

### Phase A: Day Marker

**Purpose**: Initialize the day and prepare for processing.

Phase A marks the beginning of a new simulation day. The system logs a `PhaseA` event and sets up internal state for the day's activities. No economic transactions occur in this phase.

### Phase B1: Scheduled Actions

**Purpose**: Execute pre-programmed transactions.

Scheduled actions are transactions defined in the scenario YAML that should occur on specific days. Examples include:

- Minting new money
- Creating new payables
- Transferring assets between agents

Actions are executed in the order they appear in the schedule. If an action fails (e.g., insufficient funds), error handling depends on the system's default mode.

### Phase B (Dealer Trading)

**Purpose**: Allow secondary market trading of payables.

When dealers are enabled, this phase runs between scheduled actions and settlement. The dealer trading phase:

1. Identifies agents who may want to trade (sellers need liquidity, buyers have excess)
2. Matches traders with appropriate dealers by maturity bucket
3. Executes trades, transferring payables and cash
4. Updates dealer quotes based on new inventory positions

Dealer trading is optional and controlled by the `enable_dealer` flag.

### Phase B2: Settlement

**Purpose**: Settle obligations that mature today.

This is the core settlement phase where due payables and delivery obligations are processed:

1. **Identify dues**: Find all payables and delivery obligations with `due_day == current_day`
2. **Attempt settlement**: For each obligation, try to pay using available means
3. **Handle failures**: If settlement fails, either raise an error (fail-fast) or mark the agent as defaulted (expel-agent)
4. **Log outcomes**: Record settlement or default events

**Settlement Order**: The system tries payment methods in priority order:
- Bank deposits first (preferred)
- Cash second
- Reserves (for bank-to-bank only)

### Phase C: Interbank Netting

**Purpose**: Clear net positions between banks.

After client payments, banks may have bilateral obligations to each other. Phase C computes net positions and settles them:

1. **Compute nets**: Sum all client payments by bank pair
2. **Net off**: Calculate the net amount owed between each pair
3. **Settle**: Transfer reserves for the net amount, or create overnight payables if reserves are insufficient

This multilateral netting reduces the total settlement volume compared to gross settlement.

---

## Settlement Engine

The settlement engine is responsible for converting obligations into completed payments. Understanding its behavior is crucial for interpreting simulation results.

### Settlement Process

When a payable matures, the engine:

1. **Checks debtor status**: Skip if debtor has already defaulted
2. **Identifies means of payment**: Lists available cash, deposits, reserves
3. **Attempts payment**: Tries each method in priority order until the full amount is paid
4. **Records outcome**: Logs settlement success or default

### Means of Payment Priority

The settlement order is determined by policy but typically follows:

1. **Bank Deposits**: Debiting the payer's deposit account (most common)
2. **Cash**: Transferring physical currency
3. **Reserves**: Direct reserve transfer (banks only)

If all methods are exhausted without fully paying, the remaining amount is a shortfall.

### Default Handling Modes

The system supports two default handling modes:

**fail-fast** (default): Any settlement failure immediately raises a `DefaultError`, halting the simulation. Use this for strict analysis where any default is considered a critical failure.

**expel-agent**: Settlement failures mark the debtor as defaulted and write off remaining obligations, but the simulation continues. This allows studying cascade effects where one default leads to others.

When an agent is expelled:
- All their outstanding liabilities are written off
- Future scheduled actions involving them are cancelled
- Other agents may then default due to lost expected inflows

---

## The Kalecki Ring

The Kalecki ring is the primary experimental structure in Bilancio, modeling circular payment dependencies.

### What It Is

A Kalecki ring is a circular network of N agents where:
- Agent 1 owes Agent 2
- Agent 2 owes Agent 3
- ...
- Agent N owes Agent 1

This creates a payment chain where each agent's ability to pay depends on receiving payment from their predecessor. The structure highlights how liquidity propagates (or fails to propagate) through interconnected systems.

### Why It Matters

The ring structure is useful for studying:

- **Liquidity propagation**: How cash flows through the network
- **Coordination failures**: Why systems fail even with "sufficient" aggregate liquidity
- **Timing effects**: How payment order affects outcomes
- **Dealer impact**: Whether secondary markets improve settlement rates

The ring is a minimal model that captures essential payment system dynamics while remaining tractable for analysis.

### Key Parameters

Three parameters control ring behavior:

#### Kappa (liquidity ratio)

**Definition**: Initial system liquidity (L0) divided by total obligations due (S1)

**Interpretation**:
- kappa < 1: System has less cash than debts (liquidity-constrained)
- kappa = 1: Cash exactly equals debts
- kappa > 1: System has excess liquidity

**Typical values**:
- kappa = 0.3: Severely stressed, high default rates expected
- kappa = 0.5: Moderately stressed
- kappa = 1.0: Balanced
- kappa = 2.0: Abundant liquidity, few defaults

#### Concentration (c)

**Definition**: Dirichlet distribution parameter controlling debt inequality

**Interpretation**:
- Low c (< 0.5): Highly unequal, some agents owe much more than others
- c = 1.0: Moderate variation
- High c (> 2.0): More equal distribution

Unequal distributions create "critical nodes" that, if they fail, can cause cascading defaults.

#### Mu (maturity timing)

**Definition**: Parameter controlling when debts mature within the simulation horizon

**Interpretation**:
- mu = 0: Debts mature early (front-loaded stress)
- mu = 0.5: Debts mature evenly across the period
- mu = 1.0: Debts mature late (back-loaded stress)

Timing affects whether agents receive inflows before they must pay outflows.

---

## Dealers and Secondary Markets

The dealer system enables secondary market trading of payables, providing an alternative to waiting for maturity.

### How Dealers Provide Liquidity

Dealers allow agents to convert future claims into immediate cash:

1. **Seller need**: An agent owes money today but holds a payable maturing tomorrow
2. **Dealer bid**: The dealer quotes a price (bid) to buy the payable
3. **Trade execution**: Agent sells the payable, receiving cash now
4. **Settlement**: The dealer (or VBT) collects payment at maturity

This transforms a liquidity problem (timing mismatch) into a solvable trading opportunity.

### Bid/Ask Pricing

Dealers maintain two-sided quotes:

- **Bid** (b): Price to buy payables from customers
- **Ask** (a): Price to sell payables to customers
- **Spread**: a - b, the dealer's compensation

Quotes are computed using the L1 kernel formula, which makes prices sensitive to:
- VBT anchor prices (M for mid, O for spread)
- Current dealer inventory
- Capacity constraints

### Trading Mechanics

When a customer wants to sell a payable to a dealer:

1. **Feasibility check**: Can the dealer execute internally?
   - Inventory constraint: Room for more tickets?
   - Cash constraint: Can pay the bid price?

2. **Interior execution** (if feasible):
   - Trade at dealer's bid price
   - Dealer inventory increases
   - Customer receives cash

3. **Passthrough** (if not feasible):
   - Trade routes to VBT at outside bid (B)
   - VBT absorbs the ticket
   - Dealer position unchanged

Buying from dealers follows the reverse logic, with customers paying the ask price.

### Maturity Buckets

Dealers specialize by maturity:
- **Short** (1-3 days): Near-term obligations
- **Mid** (4-8 days): Medium-term obligations
- **Long** (9+ days): Longer-dated claims

Each bucket has its own dealer and VBT pair, allowing the market to price term structure.

---

## Metrics

Bilancio computes several metrics to evaluate settlement outcomes and system performance.

### phi_t (Settlement Ratio)

**Definition**: Fraction of dues that settled on time on day t

**Formula**: phi_t = (Amount settled on due date) / (Total amount due on day t)

**Interpretation**:
- phi_t = 1.0: All dues settled, perfect performance
- phi_t = 0.8: 80% settled, 20% defaulted
- phi_t = 0.0: Complete failure

**Usage**: Track daily settlement success. Aggregate as phi_total across all days.

### delta_t (Default Rate)

**Definition**: Fraction of dues that defaulted on day t

**Formula**: delta_t = 1 - phi_t

**Interpretation**:
- delta_t = 0.0: No defaults
- delta_t = 0.2: 20% of dues defaulted
- delta_t = 1.0: Complete failure

**Usage**: Primary outcome measure for stress testing and dealer impact analysis.

### G_t (Liquidity Gap)

**Definition**: Shortfall between required and available liquidity

**Formula**: G_t = max(0, Mbar_t - M_t)

Where:
- Mbar_t = Minimum liquidity required (sum of net outflows)
- M_t = Actual system money supply

**Interpretation**:
- G_t = 0: System has sufficient liquidity
- G_t > 0: Structural shortage of this amount

**Usage**: Diagnose whether failures stem from aggregate shortage vs. distribution problems.

### alpha_t (Netting Potential)

**Definition**: Potential efficiency gain from multilateral netting

**Formula**: alpha_t = 1 - Mbar_t / S_t

Where S_t is total gross obligations due on day t.

**Interpretation**:
- alpha_t near 0: Little netting benefit, nearly all flows are real
- alpha_t near 1: High netting potential, most flows net out

**Usage**: Measure how much of the payment volume is "circular" and could be netted.

### v_t (Velocity)

**Definition**: Settlement volume relative to peak liquidity usage

**Formula**: v_t = Gross_settled_t / Mpeak_t

**Interpretation**: Higher velocity means the money stock "works harder," turning over multiple times to settle a larger volume.

---

## Next Steps

Now that you understand the core concepts, you can:

1. **Run a scenario**: See [Quick Start](quickstart.md) for your first simulation
2. **Explore parameters**: See [Kalecki Ring Sweeps](guides/kalecki_ring_sweep.md) for systematic experiments
3. **Analyze results**: The CLI produces HTML reports with detailed metrics
4. **Extend the framework**: See [Contributing](contributing.md) for development guidance
