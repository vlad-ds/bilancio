"""Latin Hypercube Sampling (LHS) parameter generation strategy."""

from __future__ import annotations

import random
from decimal import Decimal
from typing import Iterator, List, Tuple


def generate_lhs_params(
    count: int,
    *,
    kappa_range: Tuple[Decimal, Decimal],
    concentration_range: Tuple[Decimal, Decimal],
    mu_range: Tuple[Decimal, Decimal],
    monotonicity_range: Tuple[Decimal, Decimal],
    seed: int,
) -> Iterator[Tuple[Decimal, Decimal, Decimal, Decimal]]:
    """
    Generate parameter combinations using Latin Hypercube Sampling.

    LHS divides each parameter range into equal-probability strata and samples
    one value from each stratum, then shuffles the samples to decorrelate them.
    This ensures good coverage of the parameter space with fewer samples than
    grid sampling.

    Args:
        count: Number of parameter combinations to generate
        kappa_range: (low, high) bounds for kappa
        concentration_range: (low, high) bounds for concentration
        mu_range: (low, high) bounds for mu
        monotonicity_range: (low, high) bounds for monotonicity
        seed: Random seed for reproducibility

    Yields:
        Tuples of (kappa, concentration, mu, monotonicity)
    """
    if count <= 0:
        return

    rng = random.Random(seed + 7919)  # Add offset for variety

    # Sample each dimension using LHS
    kappas = _lhs_axis(count, kappa_range, rng)
    concentrations = _lhs_axis(count, concentration_range, rng)
    mus = _lhs_axis(count, mu_range, rng)
    monotonicities = _lhs_axis(count, monotonicity_range, rng)

    # Shuffle to decorrelate dimensions
    rng.shuffle(concentrations)
    rng.shuffle(mus)
    rng.shuffle(monotonicities)

    # Yield parameter combinations
    for idx in range(count):
        yield (kappas[idx], concentrations[idx], mus[idx], monotonicities[idx])


def _lhs_axis(count: int, bounds: Tuple[Decimal, Decimal], rng: random.Random) -> List[Decimal]:
    """
    Sample a single parameter dimension using Latin Hypercube Sampling.

    Divides the range into 'count' equal strata and samples one value uniformly
    from each stratum.

    Args:
        count: Number of strata/samples
        bounds: (low, high) bounds for the parameter
        rng: Random number generator

    Returns:
        List of sampled values (shuffled)
    """
    low, high = bounds
    samples: List[Decimal] = []

    for stratum in range(count):
        # Define stratum boundaries as fractions [0,1]
        a = Decimal(stratum) / Decimal(count)
        b = Decimal(stratum + 1) / Decimal(count)

        # Sample uniformly within stratum
        u = Decimal(str(rng.random()))
        frac = a + (b - a) * u

        # Map to parameter range
        samples.append(low + (high - low) * frac)

    # Shuffle to decorrelate from stratum order
    rng.shuffle(samples)
    return samples
