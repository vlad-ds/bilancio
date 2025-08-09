awesome — first task should be the **Domain & System foundations**. Once these are solid, adding `ops` is trivial. Here’s a detailed, copy‑pasteable plan for a smart coding agent to implement in one pass.

# Task 1 — Build the Domain & System foundations (MVP, scalable later)

## Context

We’re rebooting the previous `money-modeling/` prototype into `bilancio/`. The MVP will model agents and contracts (single contract object with two “views”: asset holder and liable issuer), use IDs everywhere, centralize rules in a `PolicyEngine`, and enforce invariants via the `System` gateway. Atomicity is snapshot‑based for now; indices are derived on demand later.

## Goal (Definition of Done)

* Typed **instrument classes** for: `Cash`, `BankDeposit`, `ReserveDeposit`, `Payable`, and `Deliverable`.
* Typed **agent classes** for: `Household`, `Bank`, `Treasury`, `CentralBank`.
* `PolicyEngine` with default rules for who may **hold / issue / settle** and **means‑of‑payment ranking** (deterministic).
* `System` as the single gateway with:

  * registries for agents and contracts,
  * ID generation,
  * helpers to register agents and attach contracts,
  * a minimal event log,
  * invariant checks (double‑entry, no orphans, policy respected).
* Smoke tests proving we can: create CB, create Bank & Household, issue deposit (bank liability / HH asset), mint cash, create a payable with due day, and pass invariants.

---

## Work plan (step‑by‑step)

### 0) Conventions (put in code comments)

* **Amounts:** integers (minor units). No floats.
* **Currency/denomination:** single‑currency MVP; keep a `denom: str = "X"` field for future use.
* **IDs:** string ULID/UUID‑like; generated centrally in `core/ids.py`.
* **Mutations:** only through `System` methods (gateway rule).
* **Validation:** instrument “type invariants” live on the class; **policy** is centralized in `domain/policy.py`.

---

### 1) Implement IDs and Time scaffolding

`src/bilancio/core/ids.py`

```python
import uuid
from typing import Literal

def new_id(prefix: str = "x") -> str:
    # short, sortable-ish id; fine for MVP
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

AgentId = str
InstrId = str
OpId = str
```

`src/bilancio/core/time.py` already exists; ensure `Day = int`, `Phase` enum and `Timepoint` are present (as in your skeleton).

---

### 2) Define base Instrument & concrete instruments

`src/bilancio/domain/instruments/base.py`

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from bilancio.core.ids import InstrId, AgentId

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

`src/bilancio/domain/instruments/means_of_payment.py`

```python
from dataclasses import dataclass
from typing import Optional
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

`src/bilancio/domain/instruments/credit.py`

```python
from dataclasses import dataclass
from typing import Optional
from .base import Instrument

@dataclass
class Payable(Instrument):
    due_day: Optional[int] = None
    def __post_init__(self):
        self.kind = "payable"
    def validate_type_invariants(self) -> None:
        super().validate_type_invariants()
        assert self.due_day is not None and self.due_day >= 0, "payable must have due_day"
```

`src/bilancio/domain/instruments/nonfinancial.py`

```python
from dataclasses import dataclass
from .base import Instrument

@dataclass
class Deliverable(Instrument):
    # non-financial deliverable; still modeled as a contract for uniformity
    def __post_init__(self):
        self.kind = "deliverable"
    def is_financial(self) -> bool:
        return False
```

---

### 3) Base Agent & typed Agents

`src/bilancio/domain/agent.py`

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from bilancio.core.ids import AgentId, InstrId

@dataclass
class Agent:
    id: AgentId
    name: str
    kind: str
    asset_ids: List[InstrId] = field(default_factory=list)
    liability_ids: List[InstrId] = field(default_factory=list)
```

`src/bilancio/domain/agents/{bank.py,central_bank.py,household.py,treasury.py}`

```python
# bank.py
from dataclasses import dataclass
from bilancio.domain.agent import Agent
@dataclass
class Bank(Agent):
    def __post_init__(self): self.kind = "bank"

# central_bank.py
from dataclasses import dataclass
from bilancio.domain.agent import Agent
@dataclass
class CentralBank(Agent):
    def __post_init__(self): self.kind = "central_bank"

# household.py
from dataclasses import dataclass
from bilancio.domain.agent import Agent
@dataclass
class Household(Agent):
    def __post_init__(self): self.kind = "household"

# treasury.py
from dataclasses import dataclass
from bilancio.domain.agent import Agent
@dataclass
class Treasury(Agent):
    def __post_init__(self): self.kind = "treasury"
```

---

### 4) PolicyEngine (default regime rules)

`src/bilancio/domain/policy.py`

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Type, Sequence, Dict, List
from bilancio.domain.agent import Agent
from bilancio.domain.agents.bank import Bank
from bilancio.domain.agents.central_bank import CentralBank
from bilancio.domain.agents.household import Household
from bilancio.domain.agents.treasury import Treasury
from bilancio.domain.instruments.base import Instrument
from bilancio.domain.instruments.means_of_payment import Cash, BankDeposit, ReserveDeposit
from bilancio.domain.instruments.credit import Payable
from bilancio.domain.instruments.nonfinancial import Deliverable

AgentType = Type[Agent]
InstrType = Type[Instrument]

@dataclass
class PolicyEngine:
    # who may issue / hold each instrument type (MVP: static sets)
    issuers: Dict[InstrType, Sequence[AgentType]]
    holders: Dict[InstrType, Sequence[AgentType]]
    # means-of-payment ranking per agent kind (least-preferred to keep first)
    mop_rank: Dict[str, List[str]]

    @classmethod
    def default(cls) -> "PolicyEngine":
        return cls(
            issuers={
                Cash:        (CentralBank,),
                BankDeposit: (Bank,),
                ReserveDeposit: (CentralBank,),
                Payable:     (Agent,),            # any agent can issue a payable
                Deliverable: (Agent,),
            },
            holders={
                Cash:            (Agent,),
                BankDeposit:     (Household, Treasury, Bank),  # banks may hold but not for interbank settlement
                ReserveDeposit:  (Bank, Treasury),
                Payable:         (Agent,),
                Deliverable:     (Agent,),
            },
            mop_rank={
                "household":     ["bank_deposit", "cash"],     # use deposit first, then cash
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

### 5) System gateway, registries, helpers, and invariants

`src/bilancio/engines/system.py`

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from bilancio.core.ids import AgentId, InstrId, new_id
from bilancio.domain.agent import Agent
from bilancio.domain.instruments.base import Instrument
from bilancio.domain.policy import PolicyEngine
from bilancio.core.errors import ValidationError

@dataclass
class State:
    agents: Dict[AgentId, Agent] = field(default_factory=dict)
    contracts: Dict[InstrId, Instrument] = field(default_factory=dict)
    events: List[dict] = field(default_factory=list)
    day: int = 0

class System:
    def __init__(self, policy: PolicyEngine | None = None):
        self.policy = policy or PolicyEngine.default()
        self.state = State()

    # ---- ID helpers
    def new_agent_id(self, prefix="A") -> AgentId: return new_id(prefix)
    def new_contract_id(self, prefix="C") -> InstrId: return new_id(prefix)

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
        self.state.events.append({"kind": kind, "day": self.state.day, **payload})

    # ---- invariants (MVP)
    def assert_invariants(self) -> None:
        for cid, c in self.state.contracts.items():
            assert cid in self.state.agents[c.asset_holder_id].asset_ids, f"{cid} missing on asset holder"
            assert cid in self.state.agents[c.liability_issuer_id].liability_ids, f"{cid} missing on issuer"
```

---

### 6) Minimal Central Bank bootstrap helper (optional but handy)

Add to `System`:

```python
def bootstrap_cb(self, cb: Agent) -> None:
    self.add_agent(cb)
    self.log("BootstrapCB", cb_id=cb.id)
```

You’ll use this in examples/tests to create the CB and then banks/households.

---

### 7) Tests (smoke + policy)

`tests/unit/test_domain_system.py`

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
    sys.add_contract(ReserveDeposit(id="r", kind="reserve_deposit", amount=5, denom="X",
                                    asset_holder_id="B1", liability_issuer_id="CB1"))

    # Any agent can issue a payable in MVP
    sys.add_contract(Payable(id="p", kind="payable", amount=7, denom="X",
                             asset_holder_id="B1", liability_issuer_id="H1", due_day=0))
    sys.assert_invariants()
```

Run:

```bash
uv run pytest -q
```

---

## Notes for future steps (so the coding agent leaves clean seams)

* **Operations** next: `ops.base` (`Operation` with `plan()`/`validate()`/`apply()`), then `ops.banking` for `DepositCash`, `ClientPayment`. These will only use the public `System` gateway and the `PolicyEngine`.
* **Atomicity**: wrap `System` writes in `core.atomic.atomic(system)` (snapshot rollback) when you add ops; tests will simulate failure to confirm rollback.
* **Settlement**: once `Payable` exists, `engines.settlement` can scan by due day (use a simple generator now, index later).
* **Interbank**: derive intraday nets from same‑day `log()` events in phase C (no persistent index in MVP).
