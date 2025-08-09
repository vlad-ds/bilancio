"""Financial metrics calculation functions."""


# TODO: Import CashFlow and Money from appropriate modules once defined
# from bilancio.domain.instruments import CashFlow
# from bilancio.core.money import Money


def calculate_npv(flows: list["CashFlow"], rate: float) -> "Money":
    """Calculate Net Present Value of cash flows.
    
    Args:
        flows: List of cash flows to analyze
        rate: Discount rate to use for NPV calculation
        
    Returns:
        The net present value as a Money object
        
    TODO: Implement NPV calculation logic
    """
    raise NotImplementedError("NPV calculation not yet implemented")


def calculate_irr(flows: list["CashFlow"]) -> float:
    """Calculate Internal Rate of Return for cash flows.
    
    Args:
        flows: List of cash flows to analyze
        
    Returns:
        The internal rate of return as a float
        
    TODO: Implement IRR calculation logic
    """
    raise NotImplementedError("IRR calculation not yet implemented")
