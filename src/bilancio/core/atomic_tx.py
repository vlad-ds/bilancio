import copy
from contextlib import contextmanager


@contextmanager
def atomic(system):
    """Context manager for atomic operations - rollback on failure"""
    snapshot = copy.deepcopy(system.state)
    try:
        yield
    except Exception:
        system.state = snapshot
        raise
