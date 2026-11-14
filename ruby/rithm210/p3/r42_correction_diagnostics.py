"""Replay simultaneous transitions and compute exact six-opportunity pilot contrasts."""
import argparse
import json
from collections import Counter, defaultdict

import numpy as np

from r37_ssm_source_cv import SOURCE_SHA, source_groups
from r41_revision_budget import kernel, switch_probability

CLASSES = ("short_of_target", "target", "past_target")


def classify(start, end):
    if end == 4:
        return "target"
    return "short_of_target" if (start-4)*(end-4) > 0 else "past_target"


def outcomes(start, distribution):
    out = {name: {"probability": 0., "weighted_cost": 0.} for name in CLASSES}
    for n, mass in enumerate(distribution):
        row = out[classify(start, n)]
        row["probability"] += float(mass)
        row["weighted_cost"] += float(mass*3*(n-4)**2)
    return out


def replay(path):
    counts = {n: Counter() for n in (3, 5)}
    clusters = {n: defaultdict(Counter) for n in counts}
    for sid, _, _, actors, periods in source_groups(path):
        for t in range(1, 40):
            previous = [periods[t][actor][0] for actor in actors]
            start = sum(previous)
            if start not in counts:
                continue
            next_choices = [periods[t+1][actor][0] for actor in actors]
            up = sum(a < b for a, b in zip(previous, next_choices, strict=True))
            down = sum(a > b for a, b in zip(previous, next_choices, strict=True))
            counts[start][up, down] += 1
            clusters[start][sid][up, down] += 1
    result = {}
    for start, pairs in counts.items():
        total = pairs.total()
        n_dist = np.zeros(7)
        opportunities = sum((u if start == 3 else d)*c for (u, d), c in pairs.items())
        raw_no = sum(c for (u, d), c in pairs.items() if (u if start == 3 else d) == 0)
        raw_many = sum(c for (u, d), c in pairs.items() if (u if start == 3 else d) >= 2)
        for (u, d), count in pairs.items():
            n_dist[start+u-d] += count/total
        result[str(start)] = {
            "transitions": total,
            "sessions_with_start": len(clusters[start]),
            "corrective_direction_switches": opportunities,
            "zero_corrective_direction_switches": raw_no,
            "multiple_corrective_direction_switches": raw_many,
            "final_occupancy_classes": outcomes(start, n_dist),
            "transition_histogram_U_D": {f"{u},{d}": c for (u, d), c in sorted(pairs.items())},
        }
    return result


def first_block(start, beta, penalty, refresh):
    # State remembers current count, actors left from each starting route and first target turn.
    states = {(start, start, 6-start, 0): 1.}
    for remaining in range(6, 0, -1):
        after = defaultdict(float)
        for (n, a, b, first), mass in states.items():
            for on_a, available, na, nb, sign in ((True, a, a-1, b, -1), (False, b, a, b-1, 1)):
                if not available:
                    continue
                p = switch_probability(n if refresh else start, on_a, beta, penalty)
                event = mass*available/remaining
                after[n, na, nb, first] += event*(1-p)
                new_n = n+sign
                hit = first or (7-remaining if new_n == 4 else 0)
                after[new_n, na, nb, hit] += event*p
        states = after
    distribution = np.zeros(7)
    hits = np.zeros(7)
    lost = 0.
    for (n, _, _, first), mass in states.items():
        distribution[n] += mass
        hits[first] += mass
        if first and n != 4:
            lost += mass
    expected = kernel(beta, penalty, refresh)[0][start]
    np.testing.assert_allclose(distribution, expected, atol=1e-14)
    return {"final_occupancy_classes": outcomes(start, distribution),
            "first_target_turn_counts_probability": hits.tolist(),
            "hit_then_lost": float(lost),
            "end_excess": float(sum(distribution[n]*3*(n-4)**2 for n in range(7)))}


def run(path):
    result = {
        "synthetic": {str(start): {
            f"{signal}_d{penalty:g}": first_block(start, 1.5, penalty, refresh)
            for signal, refresh in (("fixed", False), ("live", True))
            for penalty in (0., .5)} for start in (3, 5)}
    }
    if path:
        result.update(source_sha256=SOURCE_SHA, observed=replay(path))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_csv", nargs="?")
    print(json.dumps(run(parser.parse_args().private_csv), indent=2, allow_nan=False))
