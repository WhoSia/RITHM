"""Exact source-clock-aware integer identification bounds for a 10-minute pair.

Hypothetical reconstruction only. Sensor error has NOT been independently measured.
"""
from math import ceil, floor, isfinite


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError("counts must be nonnegative integers")
    return value


def minimal_balancing_transfer(even, odd):
    """Fewest INTEGER crossings to make latent 5min halves differ by <=1.

    Assumes exact source 10min conservation and a near-flat latent world.
    Does not estimate actual error, or assert that traffic was near-flat.
    """
    _count(even)
    _count(odd)
    return abs(odd - even) // 2


def feasible_latent_first_bin(observed_even, observed_odd,
                              source_error_bound=None,
                              reference_even=None, reference_odd=None,
                              reference_error_bound=None):
    """Sharp integer Q_even interval conditional on explicit source/reference bounds.

    Y=Q+M, M_even+M_odd=0. Optional source |M|<=b. Independent (in
    provenance, not assumed by code) Z_even,Z_odd approximate Q with |Z-Q|<=eps.
    If all bounds absent, Q_even=0..Y_even+Y_odd are observationally equivalent.
    """
    _count(observed_even)
    _count(observed_odd)
    total = observed_even + observed_odd
    low, high = 0, total
    if source_error_bound is not None:
        _count(source_error_bound)
        low = max(low, observed_even - source_error_bound)
        high = min(high, observed_even + source_error_bound)
    if (reference_even is None) != (reference_odd is None):
        raise ValueError("both independent five-minute reference readings required")
    if reference_even is not None:
        eps = reference_error_bound
        if not isinstance(eps, (int, float)) or not isfinite(eps) or eps < 0:
            raise ValueError("reference error must be finite and nonnegative")
        for z in (reference_even, reference_odd):
            if not isinstance(z, (int, float)) or not isfinite(z) or z < 0:
                raise ValueError("reference readings must be finite nonnegative")
        low = max(low, ceil(reference_even-eps), ceil(total-reference_odd-eps))
        high = min(high, floor(reference_even+eps), floor(total-reference_odd+eps))
    if low > high:
        return dict(compatible=False, total=total, range=None,
                    source_faithful_compatible=False, near_flat_compatible=False)
    return dict(compatible=True, total=total, range=[low, high],
                source_faithful_compatible=low <= observed_even <= high,
                near_flat_compatible=any(low <= x <= high
                                         for x in (total//2, (total+1)//2)),
                sharp_integer_range=True)
