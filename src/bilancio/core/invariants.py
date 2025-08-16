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
