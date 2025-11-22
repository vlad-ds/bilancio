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
from bilancio.domain.instruments.ticket import Ticket
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

    # ---- ticket operations
    def create_ticket(self, issuer_id: AgentId, owner_id: AgentId, face: int, maturity_time: int, bucket_id: str, serial: str | None = None) -> str:
        """Create a ticket (face = amount) with issuer and owner."""
        instr_id = self.new_contract_id("T")
        t = Ticket(
            id=instr_id,
            kind="ticket",
            amount=face,
            denom="X",
            asset_holder_id=owner_id,
            liability_issuer_id=issuer_id,
            maturity_time=maturity_time,
            bucket_id=bucket_id,
            serial=serial,
        )
        with atomic(self):
            self.add_contract(t)
            self.log("TicketCreated", issuer=issuer_id, owner=owner_id, face=face, maturity_time=maturity_time, bucket_id=bucket_id, ticket_id=instr_id, serial=serial)
        return instr_id

    def transfer_ticket(self, ticket_id: InstrId, from_agent_id: AgentId, to_agent_id: AgentId) -> None:
        """Transfer ownership of a single ticket."""
        if from_agent_id == to_agent_id:
            return
        instr = self.state.contracts.get(ticket_id)
        if instr is None or instr.kind != "ticket":
            raise ValidationError(f"ticket not found: {ticket_id}")
        if instr.asset_holder_id != from_agent_id:
            raise ValidationError(f"ticket {ticket_id} not owned by {from_agent_id}")
        with atomic(self):
            self.state.agents[from_agent_id].asset_ids.remove(ticket_id)
            self.state.agents[to_agent_id].asset_ids.append(ticket_id)
            instr.asset_holder_id = to_agent_id
            self.log("TicketTransferred", ticket_id=ticket_id, frm=from_agent_id, to=to_agent_id, face=instr.amount, bucket_id=getattr(instr, "bucket_id", None), maturity_time=getattr(instr, "maturity_time", None))

    def rebucket_ticket(self, ticket_id: InstrId, new_bucket_id: str) -> None:
        """Update a ticket's bucket label (used when remaining_tau crosses a boundary)."""
        instr = self.state.contracts.get(ticket_id)
        if instr is None or instr.kind != "ticket":
            raise ValidationError(f"ticket not found: {ticket_id}")
        instr.bucket_id = new_bucket_id
        self.log("TicketRebucketed", ticket_id=ticket_id, bucket_id=new_bucket_id)

    def tickets_of(self, owner_id: AgentId, bucket_id: str | None = None, issuer_id: AgentId | None = None) -> list[InstrId]:
        """List ticket ids held by owner, with optional bucket/issuer filters."""
        result: list[InstrId] = []
        for cid in self.state.agents[owner_id].asset_ids:
            instr = self.state.contracts.get(cid)
            if not instr or instr.kind != "ticket":
                continue
            if bucket_id is not None and getattr(instr, "bucket_id", None) != bucket_id:
                continue
            if issuer_id is not None and instr.liability_issuer_id != issuer_id:
                continue
            result.append(cid)
        return result

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
