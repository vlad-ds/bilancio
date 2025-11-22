"""Dealer-ring module scaffolding (dealer + VBT for ticketized Kalecki ring)."""

# Re-export key types for convenience
from .config import DealerRingConfig  # noqa: F401
from .models import DealerBucketState, VBTBucketState  # noqa: F401
from .tickets import Ticket  # noqa: F401
from .vbt import VBTBucket  # noqa: F401
