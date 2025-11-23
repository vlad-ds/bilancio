"""Dealer-ring module scaffolding (dealer + VBT for ticketized Kalecki ring)."""

# Re-export key types for convenience
from .config import DealerRingConfig  # noqa: F401
from .models import DealerBucketState, VBTBucketState  # noqa: F401
from .tickets import Ticket  # noqa: F401
from .vbt import VBTBucket  # noqa: F401
from .kernel import DealerBucket  # noqa: F401
from .ticket_ops import TicketOps  # noqa: F401
from .settlement import settle_bucket_maturities  # noqa: F401
from .policy import default_eligibility, bucket_pref_sell, bucket_pref_buy, Eligibility  # noqa: F401
from .assertions import (  # noqa: F401
    assert_double_entry_cash,
    assert_ticket_conservation,
    assert_quotes_within_bounds,
    assert_pass_through_state,
)
from .bootstrap import (  # noqa: F401
    ticketize_payables,
    allocate_tickets,
    seed_dealer_vbt_cash,
    compute_bucket_id,
)
