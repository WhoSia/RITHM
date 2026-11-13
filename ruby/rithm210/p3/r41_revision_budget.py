"""Six opportunities per block, with frozen or refreshed congestion signals."""
import argparse
import json
from collections import defaultdict

import numpy as np
from scipy.optimize import linprog
from scipy.special import expit

from r37_ssm_source_cv import COST, SOURCE_SHA, source_groups

STARTS = (3, 4, 5)
HORIZONS = (1, 5, 39)
EXCESS = COST - 24


def switch_probability(n, on_a, beta, penalty):
    gain = 3*n-14 if on_a else 11-3*n
    return float(expit(beta*gain-penalty))


def kernel(beta, penalty, refresh):
    """Return the occupancy kernel and expected switches by initial occupancy."""
    matrix = np.zeros((7, 7))
    switches = np.zeros(7)
    for start in range(7):
        # State: current A count, uncalled initial-A actors, uncalled initial-B actors.
        states = {(start, start, 6-start): 1.}
        for remaining in range(6, 0, -1):
            next_states = defaultdict(float)
            for (n, a, b), mass in states.items():
                for on_a, available, da, db, step in ((True, a, 1, 0, -1), (False, b, 0, 1, 1)):
                    if not available:
                        continue
                    chosen = mass*available/remaining
                    probability = switch_probability(n if refresh else start, on_a, beta, penalty)
                    move = chosen*probability
                    next_states[n+step, a-da, b-db] += move
                    next_states[n, a-da, b-db] += chosen*(1-probability)
                    switches[start] += move
            states = next_states
        for (n, _, _), mass in states.items():
            matrix[start, n] += mass
    return matrix, switches


def evaluate(matrix, switches, start):
    mass = np.eye(7)[start]
    cumulative_cost = cumulative_switches = 0.
    results = {}
    for t in range(1, max(HORIZONS)+1):
        cumulative_switches += float(mass @ switches)
        mass = mass @ matrix
        cumulative_cost += float(mass @ EXCESS)
        if t in HORIZONS:
            results[str(t)] = {"cost": cumulative_cost, "switches": cumulative_switches,
                               "efficient_at_end": float(mass[4])}
    return results


def switch_account(n, up, down):
    """Return sum of unilateral social-cost changes and their joint remainder."""
    net = up-down
    gross = up+down
    return 6*(n-4)*net+3*gross, 3*(net*net-gross)


def welfare_bounds(probabilities):
    """Sharp one-period bounds conditional on six A-choice marginals."""
    p = np.sort(np.asarray(probabilities, dtype=float))
    if p.shape != (6,) or not np.all(np.isfinite(p) & (p >= 0) & (p <= 1)):
        raise ValueError("expected six probabilities in [0,1]")
    mean = float(p.sum())
    fraction = mean-np.floor(mean)
    widths = np.diff(np.r_[0., p, 1.])
    return {"minimum": float(3*((mean-4)**2+fraction*(1-fraction))),
            "independent": float(3*((mean-4)**2+np.sum(p*(1-p)))),
            "maximum": float(widths @ EXCESS[::-1])}


def same_marginal_example():
    """At n=5, all five A actors have switch probability 1/5, B stays."""
    d = np.arange(6)
    independent = np.asarray([1024, 1280, 640, 160, 20, 1], dtype=float) / 3125
    # Coefficients of (4 + z)^5.
    cases = {"one_uniform_switcher": np.eye(6)[1],
             "independent": independent,
             "all_or_none": np.array([.8, 0, 0, 0, 0, .2])}
    return {name: {"expected_switches": float(p @ d),
                   "expected_excess": float(p @ (3*(1-d)**2))}
            for name, p in cases.items()}


def replay(path):
    groups = source_groups(path)
    by_start = defaultdict(list)
    for _, _, _, actors, periods in groups:
        for t in range(1, 40):
            previous = [periods[t][a][0] for a in actors]
            current = [periods[t+1][a][0] for a in actors]
            n = sum(previous)
            up = sum(a < b for a, b in zip(previous, current, strict=True))
            down = sum(a > b for a, b in zip(previous, current, strict=True))
            unilateral, joint = switch_account(n, up, down)
            actual = COST[n+up-down]-COST[n]
            if actual != unilateral+joint:
                raise ArithmeticError("cost-account identity failed")
            by_start[n].append([up+down, unilateral, joint, actual, joint > 0, up, down,
                                EXCESS[n+up-down]])
    summary = {}
    for n, values in sorted(by_start.items()):
        keys = ("gross_switches", "unilateral", "joint", "actual", "positive_joint_share",
                "up", "down", "next_excess")
        row = dict(zip(keys, np.mean(values, axis=0).tolist(), strict=True), transitions=len(values))
        # Pooled, route-exchangeable descriptive marginals within each initial n.
        probabilities = ([1-row["down"]/n]*n if n else []) + (
            [row["up"]/(6-n)]*(6-n) if n < 6 else [])
        row["pooled_marginal_bounds"] = welfare_bounds(probabilities)
        summary[str(n)] = row
    return summary


def dynamic_bounds(beta, penalty):
    """Sharp finite-horizon costs across couplings with fixed route-wise marginals."""
    problems = []
    for n in range(7):
        up, down = np.asarray([(u, d) for u in range(7-n) for d in range(n+1)]).T
        rhs = (1, (6-n)*switch_probability(n, False, beta, penalty),
               n*switch_probability(n, True, beta, penalty))
        problems.append((n+up-down, np.vstack((np.ones(up.size), up, down)), rhs))
    results = {}
    for label, sign in (("minimum", 1), ("maximum", -1)):
        value = np.zeros(7)
        for horizon in range(1, max(HORIZONS)+1):
            next_value = []
            for destinations, constraints, rhs in problems:
                result = linprog(sign*(EXCESS+value)[destinations], A_eq=constraints,
                                 b_eq=rhs, method="highs")
                if not result.success:
                    raise ArithmeticError(result.message)
                next_value.append(sign*result.fun)
            value = np.asarray(next_value)
            if horizon in HORIZONS:
                results.setdefault(str(horizon), {})[label] = value.tolist()
    return results


def comparison(beta, penalty):
    outputs = {}
    for name, refresh in (("frozen", False), ("refreshed", True)):
        base, base_moves = kernel(beta, 0., refresh)
        treated, treated_moves = kernel(beta, penalty, refresh)
        starts = {}
        for n in STARTS:
            control = evaluate(base, base_moves, n)
            treatment = evaluate(treated, treated_moves, n)
            starts[str(n)] = {
                h: {"control": control[h], "treatment": treatment[h],
                    "delta_congestion": treatment[h]["cost"]-control[h]["cost"],
                    "delta_if_resource_cost": treatment[h]["cost"]-control[h]["cost"]
                    + penalty/beta*treatment[h]["switches"]}
                for h in control
            }
        outputs[name] = starts
    return outputs


def run(path=None):
    grid = [{"beta": beta, "default_log_odds": d, "comparison": comparison(beta, d)}
            for beta in (.3, .6, 1., 1.5, 2.) for d in (.25, .5, 1., 2.)]
    examples = {str(s): comparison(50, 50*s) for s in (.5, 1.5, 2.5)}
    out = {"grid": grid, "near_deterministic_resource_equivalent": examples,
           "same_marginal_example": same_marginal_example(),
           "fixed_marginals_beta_1_5": {str(d): dynamic_bounds(1.5, d) for d in (0., .5)}}
    if path:
        out["source_sha256"] = SOURCE_SHA
        out["observed_partial"] = replay(path)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_csv", nargs="?")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    results = run(args.private_csv)
    if args.summary:
        results["grid"] = [
            {"beta": row["beta"], "default_log_odds": row["default_log_odds"],
             "cost_deltas": {name: [[round(starts[str(n)][str(h)]["delta_congestion"], 9)
                                     for n in STARTS] for h in HORIZONS]
                             for name, starts in row["comparison"].items()}}
            for row in results["grid"]
        ]
        results["grid_axes"] = {"starts": STARTS, "horizons": HORIZONS}
    print(json.dumps(results, indent=2, allow_nan=False))
