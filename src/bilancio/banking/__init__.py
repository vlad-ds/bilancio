"""
Banking kernel module for Banks-as-Dealers with deposits on demand.

This module implements the pricing and balance sheet mechanics from
"Banks-as-Dealers with deposits on demand" (December 2025).

Key components:
- BankDealerState: Complete balance sheet state with cohort tracking
- PricingKernel: Treynor-style dealer pricing on 2-day funding plane
- TicketProcessor: Process client tickets one by one
- ReserveProjection: 10-day reserve path for cash-tightness calculation
"""

from bilancio.banking.types import (
    TicketType,
    Ticket,
    DepositCohort,
    LoanCohort,
    CBBorrowingCohort,
    Quote,
)
from bilancio.banking.state import BankDealerState, CentralBankParams
from bilancio.banking.pricing_kernel import PricingParams, compute_quotes
from bilancio.banking.reserve_projection import project_reserves, compute_cash_tightness
from bilancio.banking.ticket_processor import (
    TicketProcessor,
    TicketResult,
    process_inter_bank_payment,
    process_intra_bank_payment,
)
from bilancio.banking.day_runner import DayRunner, DayResult, MultiBankDayRunner

__all__ = [
    # Types
    "TicketType",
    "Ticket",
    "DepositCohort",
    "LoanCohort",
    "CBBorrowingCohort",
    "Quote",
    # State
    "BankDealerState",
    "CentralBankParams",
    # Pricing
    "PricingParams",
    "compute_quotes",
    # Projection
    "project_reserves",
    "compute_cash_tightness",
    # Ticket processing
    "TicketProcessor",
    "TicketResult",
    "process_inter_bank_payment",
    "process_intra_bank_payment",
    # Day runner
    "DayRunner",
    "DayResult",
    "MultiBankDayRunner",
]
