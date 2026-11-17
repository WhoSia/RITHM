"""Largest switch disutility compatible with optimal cost and fixed marginals."""
import argparse
from itertools import product
import json
from math import ceil, floor
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

STATES = np.array(list(product((0, 1), repeat=6)))
OCCUPANCY = STATES.sum(axis=1)


def maximum_disutility(probabilities, start):
    exact = list(map(Fraction, probabilities))
    p = np.asarray(exact, dtype=float)
    total = sum(exact)
    eligible = (OCCUPANCY >= floor(total)) & (OCCUPANCY <= ceil(total))
    routes, counts = STATES[eligible], OCCUPANCY[eligible]
    # Last variable is common additive utility cost of changing from the initial route.
    eq = np.column_stack((np.vstack((np.ones(len(routes)), routes.T)), np.zeros(7)))
    ub = []
    for i, p_i in enumerate(p):
        for action in (0, 1):
            others_a = counts-routes[:, i]
            gap = (2*action-1)*(11-3*others_a)
            mass = p_i if action else 1-p_i
            switched = (i < start) != bool(action)
            ub.append(np.r_[-gap*(routes[:, i] == action), mass*(1 if switched else -1)])
    fit = linprog(np.r_[np.zeros(len(routes)), -1], A_eq=eq, b_eq=np.r_[1, p],
                  A_ub=ub, b_ub=np.zeros(len(ub)), method="highs")
    if not fit.success:
        raise ArithmeticError(fit.message)
    return {"maximum_disutility": float(fit.x[-1]),
            "positive_support": {"".join(map(str, row)): float(w)
                                 for row, w in zip(routes, fit.x[:-1], strict=True) if w > 1e-10},
            "worst_obedience_constraint_error": float(max(np.asarray(ub) @ fit.x))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("r43_summary", type=Path)
    data = json.loads(parser.parse_args().r43_summary.read_text())
    print(json.dumps({n: maximum_disutility(row["marginals"], int(n)) for n, row in data.items()}, indent=2))
