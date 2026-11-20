"""Recompute the exact signed-payoff contrasts and dose sensitivity."""

import json
from fractions import Fraction as Q
from itertools import product

from r48.r48_credit import Pulse, run, scenario


def results():
    checkpoints = (2, 3, 5, 10, 40)
    paths = {}
    for start, two, decay in product((4, 5), (False, True), ("independent", "shared")):
        if not two and decay == "shared":
            continue
        for frame, sign in product(("route", "wallet"), (-1, 1)):
            pulse = Pulse(adjustment=Q(4*sign), route_credit=Q(int(frame == "route")))
            rows = run(*scenario(start, decay, two), pulse)
            key = f"{start}_{'two' if two else 'one'}_{decay}_{frame}_{sign:+}"
            paths[key] = [rows[t-1] for t in checkpoints]

    dose_response = {}
    for start in (4, 5):
        for dose in (Q(1), Q(2), Q(9, 4), Q(3), Q(4), Q(6), Q(8)):
            positive, negative = [run(*scenario(start), Pulse(adjustment=sign*dose))
                                  for sign in (1, -1)]
            dose_response[f"{start}_{dose}"] = {
                "first_opportunity_switch_minus_vs_plus_at_3":
                    negative[2]["switch_given_first_revision"] - positive[2]["switch_given_first_revision"],
                "congestion_minus_vs_plus_at_40":
                    negative[-1]["congestion"] - positive[-1]["congestion"],
            }
    wallet_credit_sensitivity = {}
    for start, credit in product((4, 5), (Q(0), Q(1, 4), Q(1, 2), Q(3, 4))):
        positive, negative = [run(*scenario(start), Pulse(adjustment=Q(sign*4), route_credit=credit))
                              for sign in (1, -1)]
        wallet_credit_sensitivity[f"{start}_{credit}"] = (
            negative[2]["switch_given_first_revision"] - positive[2]["switch_given_first_revision"]
        )
    return {"round2_payout_adjustment": 4, "checkpoints": checkpoints, "paths": paths,
            "dose_response": dose_response, "wallet_credit_sensitivity": wallet_credit_sensitivity}


if __name__ == "__main__":
    print(json.dumps(results(), indent=2, default=str))
