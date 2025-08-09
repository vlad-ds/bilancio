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
