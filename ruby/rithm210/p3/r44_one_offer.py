"""Exact one-offer stress test for the R43 matched-marginal reference."""
import argparse
import json
from fractions import Fraction as F
from math import exp
from pathlib import Path


def net_saving(other_mean, target):
    """Cost reduction when the recipient takes target instead of its opposite."""
    if target == "B":
        return 6*other_mean-21
    if target == "A":
        return 21-6*other_mean
    raise ValueError("expected route A or B")


def first_block(start, beta, extra_log_odds, refresh):
    """Enumerate an eligible first mover and five remaining random turns."""
    target = "A" if start == 3 else "B"
    first_a = target == "B"

    def probability(n, on_a, extra=0):
        gain = 3*n-14 if on_a else 11-3*n
        return 1/(1+exp(-(beta*gain+extra)))

    def remaining(n, a, b, mass, output):
        if a+b == 0:
            output[n] += mass
            return
        if a:
            share = mass*a/(a+b)
            q = probability(n if refresh else start, True)
            remaining(n-1, a-1, b, share*q, output)
            remaining(n, a-1, b, share*(1-q), output)
        if b:
            share = mass*b/(a+b)
            q = probability(n if refresh else start, False)
            remaining(n+1, a, b-1, share*q, output)
            remaining(n, a, b-1, share*(1-q), output)

    expected = []
    for follows in (False, True):
        weights = [0.]*7
        n = start + (1-2*first_a)*follows
        remaining(n, start-first_a, 6-start-(not first_a), 1., weights)
        expected.append(sum(mass*3*(count-4)**2 for count, mass in enumerate(weights)))
    p0 = probability(start, first_a)
    p1 = probability(start, first_a, extra_log_odds)
    difference = expected[0]-expected[1]
    return {"correct_without_offer": p0, "correct_with_offer": p1,
            "cost_given_first_stays": expected[0], "cost_given_first_switches": expected[1],
            "saving_per_induced_switch": difference, "saving_per_offer": (p1-p0)*difference}


def evaluate(results):
    report = {}
    for initial, row in sorted(results.items()):
        n = int(initial)
        p = [F(x) for x in row["marginals"]]
        recipient = 0 if n == 5 else n
        target = "B" if n == 5 else "A"
        m = sum(p)-p[recipient]
        natural = 1-p[recipient] if target == "B" else p[recipient]
        per_induced = net_saving(m, target)
        report[initial] = {
            "target": target,
            "expected_others_A": float(m),
            "baseline_target_probability": float(natural),
            "saving_per_induced_switch": float(per_induced),
            "gross_private_saving_per_induced_switch": float((3*m-11) if target == "B" else (11-3*m)),
            "saving_if_forced_target": float((1-natural)*per_induced),
            "saving_at_50pct_compliance_mixed_with_baseline": float((1-natural)*per_induced/2),
            "others_mean_exact": str(m),
            "saving_per_induced_switch_exact": str(per_induced),
            "synthetic_first_block_beta_0_6_offer_log_odds_1": {
                k: first_block(n, .6, 1., refresh) for k, refresh in
                (("frozen", False), ("live", True))
            },
        }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("r43_summary", type=Path)
    result = evaluate(json.loads(parser.parse_args().r43_summary.read_text()))
    print(json.dumps(result, indent=2))
