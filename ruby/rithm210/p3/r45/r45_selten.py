"""Source-free reconstruction of Selten et al. (2007), section 5."""
import argparse
from bisect import bisect_left, bisect_right, insort
import json
from random import Random
from statistics import mean, pstdev

PROPS = (4, 3, 3, 2)


def strategy_route(strategy, previous, last_payoff, sorted_payoffs, rng):
    if strategy in (0, 1):
        return strategy
    size = len(sorted_payoffs)
    middle = (sorted_payoffs[(size-1)//2]+sorted_payoffs[size//2])/2
    if last_payoff == middle:
        below = bisect_left(sorted_payoffs, middle)
        above = size-bisect_right(sorted_payoffs, middle)
        if above == below:
            switch = bool(rng.randrange(2))
        else:
            switch = (above > below) if strategy == 2 else (below > above)
    else:
        switch = (last_payoff < middle) if strategy == 2 else (last_payoff > middle)
    return previous ^ switch


def reinforcement(weights, strategy, payoff):
    if payoff >= 0:
        weights[strategy] += payoff
    else:
        for alternative in range(len(weights)):
            if alternative != strategy:
                weights[alternative] -= payoff


def session(rng, periods=200):
    weights = [list(PROPS) for _ in range(18)]
    histories = [[] for _ in weights]
    previous = [0]*18
    last = [0]*18
    road_counts, switch_counts = [], []
    for t in range(periods):
        menu = range(2 if t == 0 else 4)
        strategies = [rng.choices(menu, weights=w[:len(menu)])[0] for w in weights]
        routes = [strategy_route(a, p, v, h, rng) for a, p, v, h in
                  zip(strategies, previous, last, histories, strict=True)]
        side = sum(routes)
        main_time, side_time = 6+2*(18-side), 12+3*side
        last = [40-(side_time if road else main_time) for road in routes]
        if t > 0:
            switch_counts.append(sum(a != b for a, b in zip(routes, previous, strict=True)))
        for w, strategy, payoff, history in zip(weights, strategies, last, histories, strict=True):
            reinforcement(w, strategy, payoff)
            insort(history, payoff)
        road_counts.append(side)
        previous = routes
    return mean(road_counts), pstdev(road_counts), mean(switch_counts)


def run(replications, seed):
    if replications <= 0:
        raise ValueError("replications must be positive")
    rng = Random(seed)
    measures = ("side_road_mean", "side_road_within_session_sd", "switches_per_transition")
    records = [session(rng) for _ in range(replications)]
    return {"seed": seed, "simulations": replications, "periods": 200, "actors": 18,
            "initial_propensities": PROPS,
            "results": dict(zip(measures, map(mean, zip(*records)), strict=True)),
            "published_table5": dict(zip(measures, (5.88, 1.65, 5.17), strict=True))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replications", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=451117)
    args = parser.parse_args()
    print(json.dumps(run(args.replications, args.seed), indent=2))
