"""Exact occupancy propagation for a synthetic previous-route default."""
import argparse
import json
from math import comb

import numpy as np
from scipy.special import expit
from scipy.stats import norm

from r37_ssm_source_cv import COST, source_groups

HORIZONS = (1, 3, 5, 10, 20, 39)
STARTS = (3, 4, 5)
EXCESS = COST - 24


def binomial(n, p):
    return np.asarray([comb(n, k)*p**k*(1-p)**(n-k) for k in range(n+1)])


def transition(beta, default, simultaneous=1):
    """Mix simultaneous independent response and one randomly selected reviser."""
    out = []
    for n in range(7):
        # Unilateral cost gain, holding the other five choices fixed.
        leave_a = expit(beta*(3*n-14) - default)
        leave_b = expit(beta*(11-3*n) - default)
        a_stay = binomial(n, 1-leave_a)
        b_join = binomial(6-n, leave_b)
        single = np.zeros(7)
        if n:
            single[n-1] = n*leave_a/6
        if n < 6:
            single[n+1] = (6-n)*leave_b/6
        single[n] = 1-single.sum()
        out.append(simultaneous*np.convolve(a_stay, b_join)+(1-simultaneous)*single)
    return np.asarray(out)


def trajectory(matrix, start, horizon=39):
    mass = np.eye(7)[start]
    ever_hit = float(start == 4)
    surviving = mass.copy()
    surviving[4] = 0
    costs, first_hits = [], []
    for _ in range(horizon):
        mass = mass @ matrix
        costs.append(float(mass @ EXCESS))
        surviving = surviving @ matrix
        ever_hit += surviving[4]
        surviving[4] = 0
        first_hits.append(float(ever_hit))
    return np.cumsum(costs), first_hits


def synthetic_grid(simultaneous=1):
    cases = []
    for beta in (.3, .6, 1.0, 1.5, 2.0):
        base = transition(beta, 0, simultaneous)
        for default in (.25, .5, 1., 2.):
            model = transition(beta, default, simultaneous)
            differences = {}
            for start in STARTS:
                ref, _ = trajectory(base, start)
                treated, _ = trajectory(model, start)
                differences[str(start)] = {str(h): float(treated[h-1]-ref[h-1]) for h in HORIZONS}
            cases.append({"beta": beta, "default_log_odds": default, "cost_differences": differences,
                          "first_round_optimum_prob": {str(n): [float(base[n, 4]), float(model[n, 4])] for n in STARTS}})
    return cases


def source_benchmark(path):
    groups = source_groups(path)
    by_start = {n: [] for n in STARTS}
    sids, totals = [], []
    for sid, _, _, actors, periods in groups:
        counts = np.array([sum(periods[t][a][0] for a in actors) for t in range(1, 41)])
        cumulative = float(EXCESS[counts[1:]].sum())
        sids.append(sid)
        totals.append(cumulative)
        if counts[0] in by_start:
            by_start[counts[0]].append((sid, cumulative))
    def summary(values):
        return {"groups": len(values), "mean": float(np.mean(values)),
                "sd": float(np.std(values, ddof=1)) if len(values) > 1 else None} if values else {"groups": 0}
    return {"groups": summary(totals),
            "by_start": {str(n): summary([y for _, y in rows]) for n, rows in by_start.items()},
            "session_mean_sd": float(np.std([np.mean(np.asarray(totals)[np.asarray(sids) == s])
                                            for s in sorted(set(sids))], ddof=1))}


def interaction_power_table(sd):
    # 4:2 versus equal-weight mean of 3:3 and 5:1. Balanced design,
    # independent groups, common SD and a two-sided normal approximation.
    return {str(delta): int(np.ceil(3 * (norm.ppf(.975)+norm.ppf(.8))**2 * sd**2/delta**2))
            for delta in (15, 25, 40)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_csv", nargs="?")
    args = parser.parse_args()
    out = {"synthetic_grid": {str(f): synthetic_grid(f) for f in (0, .25, .5, .75, 1)}}
    if args.private_csv:
        out["source_scale"] = source_benchmark(args.private_csv)
        out["illustrative_groups_per_cell"] = interaction_power_table(out["source_scale"]["groups"]["sd"])
    print(json.dumps(out, indent=2, allow_nan=False))
