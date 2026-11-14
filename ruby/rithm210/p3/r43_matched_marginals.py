"""Construct a cost-minimizing joint choice law for R42 route-pooled marginals."""
import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


def rounded_law(probabilities):
    """Exact pair rounding of Bernoulli marginals, with floor/ceil total occupancy."""
    p = tuple(probabilities)
    if len(p) != 6 or not all(0 <= x <= 1 for x in p):
        raise ValueError("expected six probabilities in [0, 1]")
    active = {p: Fraction(1)}
    done = defaultdict(Fraction)
    while active:
        after = defaultdict(Fraction)
        for row, mass in active.items():
            fractional = [i for i, x in enumerate(row) if 0 < x < 1]
            if not fractional:
                done[tuple(map(int, row))] += mass
                continue
            i = fractional[0]
            if len(fractional) == 1:
                for value, chance in ((0, 1-row[i]), (1, row[i])):
                    result = list(row)
                    result[i] = value
                    done[tuple(map(int, result))] += mass*chance
                continue
            j = fractional[1]
            up, down = min(1-row[i], row[j]), min(row[i], 1-row[j])
            for change, chance in ((up, down/(up+down)), (-down, up/(up+down))):
                result = list(row)
                result[i] += change
                result[j] -= change
                after[tuple(result)] += mass*chance
        active = after
    return done


def benchmark(data):
    results = {}
    for start, row in data["observed"].items():
        n, total = int(start), row["transitions"]
        histogram = [(tuple(map(int, k.split(","))), c)
                     for k, c in row["transition_histogram_U_D"].items()]
        if sum(c for _, c in histogram) != total:
            raise ValueError("histogram size mismatch")
        up = sum(u*c for (u, _), c in histogram)
        down = sum(d*c for (_, d), c in histogram)
        p = [1-Fraction(down, n*total)]*n + [Fraction(up, (6-n)*total)]*(6-n)
        law = rounded_law(p)
        mean = sum(p)
        cost = lambda count: 3*(count-4)**2
        observed = Fraction(sum(cost(n+u-d)*c for (u,d), c in histogram), total)
        independent = 3*((mean-4)**2+sum(x*(1-x) for x in p))
        minimum = sum(cost(sum(routes))*mass for routes, mass in law.items())
        results[start] = {
            "marginals": [str(x) for x in p],
            "minimum": float(minimum),
            "observed": float(observed),
            "independent": float(independent),
            "constructed_law": {"".join(map(str, routes)): str(mass)
                                for routes, mass in sorted(law.items())},
        }
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("r42_aggregate", type=Path)
    data = json.loads(parser.parse_args().r42_aggregate.read_text())
    print(json.dumps(benchmark(data), indent=2, allow_nan=False))
