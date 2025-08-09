from contextlib import contextmanager
import copy

@contextmanager
def atomic(system):
    """Context manager for atomic operations - rollback on failure"""
    snapshot = copy.deepcopy(system.state)
    try:
        yield
    except Exception as e:
        system.state = snapshot
        raise