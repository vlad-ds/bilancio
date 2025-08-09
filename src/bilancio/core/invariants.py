def assert_cb_cash_matches_outstanding(system):
    total = sum(c.amount for c in system.state.contracts.values() if c.kind == "cash")
    assert total == system.state.cb_cash_outstanding, "CB cash mismatch"