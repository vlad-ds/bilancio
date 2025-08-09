def assert_cb_cash_matches_outstanding(system):
    total = sum(c.amount for c in system.state.contracts.values() if c.kind == "cash")
    assert total == system.state.cb_cash_outstanding, "CB cash mismatch"

def assert_no_negative_balances(system):
    for c in system.state.contracts.values():
        if c.kind in ("bank_deposit", "cash", "reserve_deposit") and c.amount < 0:
            raise AssertionError("negative balance detected")