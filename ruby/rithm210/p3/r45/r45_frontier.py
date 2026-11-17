"""Aggregate correlated-equilibrium frontier with fixed route-class marginals."""
import argparse
import json
from fractions import Fraction
from itertools import product
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from r45_certificate import CEILINGS, exact_cost, restore_four_at_five, verify


def problem(start, marginals):
    """Build the exact affine right hand side for a six-person congestion game."""
    p = list(map(Fraction, marginals))
    if start not in range(1, 6) or len(p) != 6 or not all(0 <= x <= 1 for x in p):
        raise ValueError("expected six probabilities and both initial routes")
    if len(set(p[:start])) != 1 or len(set(p[start:])) != 1:
        raise ValueError("each initial route must have a common marginal")
    initial_b = 6-start
    counts = tuple(product(range(start+1), range(initial_b+1)))
    moments = (Fraction(1), sum(p[:start]), sum(p[start:]))
    moves_a = start-moments[1]
    moves_b = moments[2]
    # Each row sums the recommendation's gross private gain over one initial route.
    # Recommending a move requires gross >= s*volume. Staying requires gross >= -s*volume.
    gross = tuple(zip(*(
        (x*(14-3*(x+y)), (start-x)*(3*(x+y)-11),
         y*(14-3*(x+y)), (initial_b-y)*(3*(x+y)-11))
        for x, y in counts
    ), strict=True))
    slopes = (-moments[1], moves_a, moves_b, -(initial_b-moves_b))
    eq = (tuple(1 for _ in counts), tuple(x for x, _ in counts), tuple(y for _, y in counts))
    cost = tuple(3*(x+y-4)**2 for x, y in counts)
    return counts, eq, moments, gross, slopes, cost


def solve(data, burden=None):
    counts, eq, moments, gross, slopes, cost = data
    matrix = -np.asarray(gross, dtype=float)
    if burden is None:
        result = linprog([0.]*len(counts)+[-1.], A_eq=np.c_[eq, np.zeros(3)],
                         b_eq=np.asarray(moments, float), A_ub=np.c_[matrix, np.asarray(slopes, float)],
                         b_ub=np.zeros(4), method="highs")
    else:
        result = linprog(cost, A_eq=eq, b_eq=np.asarray(moments, float), A_ub=matrix,
                         b_ub=-float(burden)*np.asarray(slopes, float), method="highs")
    if result.status not in (0, 2):
        raise ArithmeticError(result.message)
    return result



def publicly_disclosed_feasible(data, burden):
    """Can a recommendation law be obeyed if its proposed final count is disclosed?"""
    counts, eq, moments, gross, slopes, cost = data
    start = max(x for x, _ in counts)
    eligible = []
    for (x, y), gains in zip(counts, zip(*gross), strict=True):
        volumes = (x, start-x, y, 6-start-y)
        signs = (-1, 1, 1, -1)
        eligible.append(all(gain >= burden*size*sign
                            for gain, size, sign in zip(gains, volumes, signs, strict=True)))
    if not any(eligible):
        return False
    result = linprog(cost, A_eq=eq, b_eq=np.asarray(moments, float),
                     bounds=[(0, None) if ok else (0, 0) for ok in eligible], method="highs")
    if result.status not in (0, 2):
        raise ArithmeticError(result.message)
    return result.success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("r43_summary", type=Path)
    parser.add_argument("--burden", type=Fraction, action="append", default=[])
    args = parser.parse_args()
    table = json.loads(args.r43_summary.read_text())
    output = {}
    for label, row in table.items():
        data = problem(int(label), row["marginals"])
        start = int(label)
        verify(data, start, row["marginals"])
        ceiling = solve(data)
        if not ceiling.success or abs(ceiling.x[-1]-float(CEILINGS[start])) > 1e-8:
            raise ArithmeticError("LP and ceiling certificate disagree")
        samples = {}
        for burden in args.burden:
            if burden < 0:
                raise ValueError("burden must be nonnegative")
            result = solve(data, burden)
            certified = exact_cost(start, burden)
            # At a rational endpoint the certificate decides feasibility even when
            # a tolerance-based solver accepts a nearly infeasible input.
            if certified is not None and (not result.success or abs(result.fun-float(certified)) > 1e-8):
                raise ArithmeticError("LP and minimum-cost certificate disagree")
            samples[str(burden)] = ({"feasible": True, "minimum": str(certified)}
                                    if certified is not None else {"feasible": False})
        # Mean < 4 forces positive mass at n<=3. There at least one B can
        # improve by >=2, more than the private ceiling. Above the private
        # ceiling, public disclosure cannot rescue feasibility.
        if sum(data[2][1:]) >= 4 or CEILINGS[start] >= 2:
            raise ArithmeticError("public-disclosure proof assumptions fail")
        output[label] = {"ceiling": str(CEILINGS[start]), "exact_certificate": True,
                         "public_final_count_has_any_feasible_burden": False, "samples": samples}
    output["relaxed_marginals_start_5_at_burden_1"] = restore_four_at_five(Fraction(1))
    print(json.dumps(output, indent=2, allow_nan=False))
