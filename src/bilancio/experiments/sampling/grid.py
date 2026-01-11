"""Grid/Cartesian product parameter sampling strategy."""

from __future__ import annotations

from decimal import Decimal
from typing import Iterator, Sequence, Tuple


def generate_grid_params(
    kappas: Sequence[Decimal],
    concentrations: Sequence[Decimal],
    mus: Sequence[Decimal],
    monotonicities: Sequence[Decimal],
) -> Iterator[Tuple[Decimal, Decimal, Decimal, Decimal]]:
    """
    Generate parameter combinations using Cartesian product (grid sampling).

    Args:
        kappas: Sequence of kappa values
        concentrations: Sequence of concentration values
        mus: Sequence of mu values
        monotonicities: Sequence of monotonicity values

    Yields:
        Tuples of (kappa, concentration, mu, monotonicity)
    """
    for kappa in kappas:
        for concentration in concentrations:
            for mu in mus:
                for monotonicity in monotonicities:
                    yield (kappa, concentration, mu, monotonicity)
