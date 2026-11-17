"""One-round recommendation programs with individual burdens and resource costs."""

import numpy as np
from scipy.optimize import linprog


def solve(start, burden, resource, baseline, *, public=False, target=None,
          minimize_change=False, max_change=None):
    """Return an optimum over obeyed recommendations on six labeled actors.

    Cell masses are P(N=n) and P(N=n, recommendation_i=A/B). To recover
    a joint law at n, decompose the conditional A marginals in the
    convex hull of binary vectors with exactly n ones.
    """
    if start not in range(1, 6) or target not in (None, *range(7)):
        raise ValueError("invalid initial or target occupancy")
    burden, resource, baseline = map(
        lambda values: np.asarray(values, dtype=float), (burden, resource, baseline)
    )
    if any(values.shape != (6,) or not np.isfinite(values).all()
           for values in (burden, resource, baseline)):
        raise ValueError("expected six finite values for each input")
    if (burden < 0).any() or (resource < 0).any() or ((baseline < 0) | (baseline > 1)).any():
        raise ValueError("invalid burden, cost, or baseline probability")
    if max_change is not None and (not np.isfinite(max_change) or max_change < 0):
        raise ValueError("invalid change budget")

    levels = tuple(range(7)) if target is None else (target,)
    width = 13 * len(levels) + 6
    masses = np.arange(13 * len(levels)).reshape(-1, 13)
    count, route_a, route_b = masses[:, 0], masses[:, 1:7], masses[:, 7:13]
    change = np.arange(width - 6, width)
    initial_a = np.arange(6) < start
    objective = np.zeros(width)
    objective[count] = [3 * (n - 4)**2 for n in levels]
    objective[route_a] = np.where(initial_a, 0, resource)
    objective[route_b] = np.where(initial_a, resource, 0)
    welfare_objective = objective.copy()
    if minimize_change:
        objective[:] = 0
        objective[change] = 1

    equality, equality_rhs = [], []
    normalizer = np.zeros(width)
    normalizer[count] = 1
    equality.append(normalizer)
    equality_rhs.append(1)
    for j, n in enumerate(levels):
        occupancy = np.zeros(width)
        occupancy[route_a[j]] = 1
        occupancy[count[j]] = -n
        equality.append(occupancy)
        equality_rhs.append(0)
        for a, b in zip(route_a[j], route_b[j], strict=True):
            link = np.zeros(width)
            link[[a, b]] = 1
            link[count[j]] = -1
            equality.append(link)
            equality_rhs.append(0)

    inequality, inequality_rhs = [], []
    gain_a = (14 - 3 * np.asarray(levels))[:, None] + np.where(initial_a, burden, -burden)
    gain_b = (3 * np.asarray(levels) - 11)[:, None] + np.where(initial_a, -burden, burden)
    bounds = [(0, None)] * width
    for route, gain in ((route_a, gain_a), (route_b, gain_b)):
        for i in range(6):
            if public:
                for cell in route[:, i][gain[:, i] < 0]:
                    bounds[cell] = (0, 0)
            else:
                obedience = np.zeros(width)
                obedience[route[:, i]] = -gain[:, i]
                inequality.append(obedience)
                inequality_rhs.append(0)
    for i in range(6):
        for sign in (1, -1):
            deviation = np.zeros(width)
            deviation[route_a[:, i]] = sign
            deviation[change[i]] = -1
            inequality.append(deviation)
            inequality_rhs.append(sign * baseline[i])
    if max_change is not None:
        budget = np.zeros(width)
        budget[change] = 1
        inequality.append(budget)
        inequality_rhs.append(max_change)

    result = linprog(objective, A_eq=equality, b_eq=equality_rhs,
                     A_ub=inequality, b_ub=inequality_rhs, bounds=bounds, method="highs")
    if result.status == 2:
        return None
    if not result.success:
        raise ArithmeticError(result.message)
    marginals = result.x[route_a].sum(axis=0)
    return {"cost": float(welfare_objective @ result.x),
            "change": float(np.abs(marginals - baseline).sum()),
            "marginals": marginals.tolist(),
            "occupancy": dict(zip(levels, result.x[count].tolist(), strict=True))}
