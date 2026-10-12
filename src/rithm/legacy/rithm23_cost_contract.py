#!/usr/bin/env python3
"""Audit person-level actually experienced route costs against source-derived routes.
Original CC BY 4.0 data: doi:10.1371/journal.pone.0184191.s002.
Run: python rithm23_cost_contract.py data/routes.csv data/costs_packed.csv
Reproduction guard, not a causal estimator.
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

DIGITS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def inspect(routes_path, costs_path):
    with Path(routes_path).open(newline='', encoding='utf-8') as f:
        routes = {(r['session'], int(r['group']), int(r['stage'])): r
                  for r in csv.DictReader(f)}
    with Path(costs_path).open(newline='', encoding='utf-8') as f:
        costs = {(r[0], int(r[1]), int(r[2])): r for r in csv.reader(f)}
    assert len(routes) == len(costs) == 24 and routes.keys() == costs.keys()
    mismatches = []
    group_round_route_cells = 0
    for key, row in sorted(routes.items()):
        encoded = costs[key]
        assert len(encoded) == 5 and len(encoded[3]) == 240
        cost = [11 + DIGITS.index(ch) for ch in encoded[3]]
        assert sum(cost) == int(encoded[4]) == int(row['group_stage_total_cost'])
        choices = []
        number = int(row['choices_base3_hex'], 16)
        for _ in range(240):
            number, digit = divmod(number, 3)
            choices.append(digit + 1)
        assert number == 0
        choices.reverse()
        bits = int(row['incident_20_bits_hex'], 16)
        assert bits.bit_count() == 4
        for t in range(20):
            ix = range(t * 12, (t + 1) * 12)
            for route in (1, 2, 3):
                values = {cost[i] for i in ix if choices[i] == route}
                if values:
                    group_round_route_cells += 1
                    if len(values) > 1:
                        mismatches.append(dict(session=key[0], group=key[1],
                                               stage=key[2], period=t + 1,
                                               route=route, observed_costs=sorted(values)))
    sessions = sorted({key[0] for key in routes})
    assert len(sessions) == 6
    result = {'n_sessions': len(sessions), 'n_group_stages': 24,
              'n_person_rounds': 24 * 240,
              'n_nonempty_route_round_cells': group_round_route_cells,
              'n_inconsistent_source_cells': len(mismatches),
              'inconsistent_source_cells': mismatches}
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('routes'); parser.add_argument('costs')
    args = parser.parse_args()
    import json
    print(json.dumps(inspect(args.routes, args.costs), indent=2))
