# Bilancio — rebuild plan (MVP, scalable later)

## Context (read me first)

We’re rebooting our money‑modeling simulator into a clean library called **bilancio**. The previous exploratory codebase lives in the `money-modeling/` directory; keep it around for reference but do not copy over design debt. The MVP focuses on clarity and determinism: agents + contracts, IDs over pointers at the API boundary, validate‑then‑apply writes, daily phases A→B→C (prepare/trade → client settlement → interbank). Atomicity is MVP‑simple (snapshot rollback); indices are optional and can be on‑demand scans for now.

## Principles we’re baking in

All mutations go through `System`. Operations accept IDs, resolve via the current `System`, and write in one block after validation. A single contract object represents an asset/liability pair (per branch). Policy rules sit in a `PolicyEngine`; instruments keep type invariants. Settlement is deterministic; banks settle in reserves; cross‑bank client payments create day‑local interbank nets handled in phase C. Event log per op, with an easy `System.fork()` later for alternate histories.

## Tooling

Use **uv** (Astral) for Python envs and running tools. Target Python ≥ 3.12. If `uv --version` fails, install uv via your OS package manager or Astral’s installer, then continue.

---

# Step‑by‑step setup

## 1) Create the repo next to the old one

```bash
# from the directory that already contains money-modeling/
mkdir -p bilancio && cd bilancio
git init -b main
```

## 2) Create the project layout (subpackages from day one)

```bash
mkdir -p src/bilancio/{core,domain/{agents,instruments},ops,engines,analysis,io} tests/{unit,integration,property,scenarios} examples
touch src/bilancio/__init__.py
touch src/bilancio/core/{__init__.py,ids.py,time.py,errors.py,events.py,invariants.py,atomic.py}
touch src/bilancio/domain/{__init__.py,agent.py,contract.py,policy.py}
touch src/bilancio/domain/agents/{__init__.py,bank.py,central_bank.py,household.py,treasury.py}
touch src/bilancio/domain/instruments/{__init__.py,base.py,means_of_payment.py,credit.py,nonfinancial.py}
touch src/bilancio/ops/{__init__.py,base.py,primitives.py,banking.py,composites.py}
touch src/bilancio/engines/{__init__.py,system.py,settlement.py,clearing.py,valuation.py,simulation.py}
touch src/bilancio/analysis/{__init__.py,balance_sheet.py,payment_funding.py,risk.py,valuation_report.py,flux_reflux.py}
touch src/bilancio/io/{__init__.py,schema.py,loader.py,export.py,visualize.py}
touch tests/unit/test_smoke.py examples/{simple_same_bank.yaml,simple_cross_bank.yaml} .gitignore README.md
```

## 3) Minimal `pyproject.toml` (package + dev extras)

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "bilancio"
version = "0.0.1"
description = "Deterministic balance-sheet financial simulation engine"
readme = "README.md"
requires-python = ">=3.12"
authors = [{ name = "Vlad", email = "devnull@example.com" }]
license = { text = "MIT" }
dependencies = []

[project.optional-dependencies]
dev = [
  "pytest>=8",
  "ruff>=0.5",
  "mypy>=1.10",
  "types-setuptools; python_version >= '3.12'"
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = false
warn_unused_ignores = true
```

## 4) `.gitignore`

```gitignore
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.mypy_cache/
.idea/
.vscode/
dist/
build/
```

## 5) Initialize the environment with `uv`

```bash
uv venv                   # creates .venv
source .venv/bin/activate # or: uv run <cmd> to auto-use the venv
uv pip install -e ".[dev]"
```

## 6) Fill in tiny stubs so imports & tests pass

`src/bilancio/__init__.py`

```python
__all__ = ["__version__"]
__version__ = "0.0.1"
```

`src/bilancio/core/time.py`

```python
from enum import Enum
from dataclasses import dataclass

class Phase(Enum):
    PREPARE = "A"
    CLIENT_SETTLEMENT = "B"
    INTERBANK = "C"

Day = int

@dataclass(frozen=True)
class Timepoint:
    day: Day
    phase: Phase
```

`src/bilancio/core/errors.py`

```python
class DomainError(Exception): ...
class ValidationError(DomainError): ...
class DefaultError(DomainError): ...
```

`src/bilancio/core/atomic.py`  (MVP snapshot rollback)

```python
import copy
from contextlib import contextmanager

@contextmanager
def atomic(system):
    snap = copy.deepcopy(system.state)
    try:
        yield
    except Exception:
        system.state = snap
        raise
```

`src/bilancio/domain/agent.py`

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Agent:
    id: str
    name: str
    asset_ids: List[str] = field(default_factory=list)
    liability_ids: List[str] = field(default_factory=list)
```

`src/bilancio/domain/contract.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Contract:
    id: str
    kind: str                  # "deposit", "payable", "reserve", etc.
    amount: int
    asset_holder_id: str
    liability_issuer_id: str
    due_day: Optional[int] = None
```

`src/bilancio/domain/policy.py`

```python
class PolicyEngine:
    def can_hold(self, agent, contract) -> bool: return True
    def can_issue(self, agent, instrument_cls) -> bool: return True
    def settlement_order(self, agent) -> list[str]: return ["deposit", "cash", "reserve"]
```

`src/bilancio/ops/base.py`

```python
from dataclasses import dataclass

@dataclass
class Plan:
    # placeholder for precomputed effects in the future
    ok: bool = True

class Operation:
    def plan(self, system) -> Plan:
        return Plan()
    def validate(self, system) -> None:
        pass
    def apply(self, system) -> None:
        raise NotImplementedError
```

`src/bilancio/engines/system.py`

```python
from dataclasses import dataclass, field
from typing import Dict
from bilancio.domain.agent import Agent
from bilancio.domain.contract import Contract
from bilancio.domain.policy import PolicyEngine

@dataclass
class State:
    agents: Dict[str, Agent] = field(default_factory=dict)
    contracts: Dict[str, Contract] = field(default_factory=dict)
    day: int = 0

class System:
    def __init__(self, policy: PolicyEngine | None = None):
        self.policy = policy or PolicyEngine()
        self.state = State()

    # gateway helpers (IDs, no raw pointers)
    def add_agent(self, agent: Agent) -> None:
        self.state.agents[agent.id] = agent

    def add_contract(self, c: Contract) -> None:
        self.state.contracts[c.id] = c
        self.state.agents[c.asset_holder_id].asset_ids.append(c.id)
        self.state.agents[c.liability_issuer_id].liability_ids.append(c.id)

    def assert_invariants(self) -> None:
        # very light MVP check: every financial contract appears on both sides
        for cid, c in self.state.contracts.items():
            assert cid in self.state.agents[c.asset_holder_id].asset_ids
            assert cid in self.state.agents[c.liability_issuer_id].liability_ids

    @classmethod
    def with_default_policy(cls) -> "System":
        return cls()
```

`tests/unit/test_smoke.py`

```python
from bilancio.engines.system import System
from bilancio.domain.agent import Agent
from bilancio.domain.contract import Contract

def test_imports_and_basic_invariants():
    sys = System.with_default_policy()
    a = Agent(id="H1", name="Household 1")
    b = Agent(id="B1", name="Bank 1")
    sys.add_agent(a); sys.add_agent(b)
    c = Contract(id="D1", kind="deposit", amount=100, asset_holder_id="H1", liability_issuer_id="B1")
    sys.add_contract(c)
    sys.assert_invariants()
```

## 7) First run

```bash
uv run pytest -q
uv run python -c "import bilancio; print(bilancio.__version__)"
```

You should see tests passing and the version printed.

## 8) README.md scaffold (so newcomers get the picture)

````markdown
# bilancio

Rebuild of our money-modeling simulator into a clean, deterministic library.

**Why:** the `money-modeling/` repo was an exploratory sandbox. `bilancio` is the minimal, principled core we can grow.

**MVP scope:** agents + contracts (single contract object with two views), validate→apply writes, daily phases A/B/C, deterministic settlement (banks settle in reserves), halt on default, five simple analyses later.

**Design vows:** all mutations via `System`; ops take IDs, resolve inside `System`; policy centralized; atomicity via snapshot rollback; indices optional.

## Dev quickstart

```bash
uv venv
uv pip install -e ".[dev]"
uv run pytest -q
````

````

## 9) Commit this baseline
```bash
git add .
git commit -m "feat: initialize bilancio skeleton with uv, subpackages, MVP stubs"
````