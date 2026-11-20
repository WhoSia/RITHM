"""Recover first-opportunity response from the cumulative R48 probabilities."""

from fractions import Fraction as Q
from itertools import product

from r48.r48_credit import Pulse, run, scenario

HORIZONS = (3, 5, 10, 40)


def first_opportunity(rows, settlement=2):
    """Partition probability mass by the round of the first focal opportunity."""
    old_seen = old_switched = Q(0)
    result = []
    for row in rows:
        delta = row["round"] - settlement
        if delta <= 0:
            continue
        seen = row["revised_after_pulse"]
        switched = row["switched_at_first_revision_by_round"]
        weight, changed = seen - old_seen, switched - old_switched
        if not 0 <= changed <= weight or not 0 <= seen <= 1:
            raise ValueError("inconsistent first-opportunity probabilities")
        result.append({
            "lag": delta, "opportunity": weight, "switched": changed,
            "rate": changed / weight if weight else None,
        })
        old_seen, old_switched = seen, switched
    return result


def exact_signed_comparison(start, two=False, decay="independent", *, reward_retention=Q(3, 4)):
    curves = [first_opportunity(run(*scenario(start, decay, two),
                                    Pulse(adjustment=Q(sign * 4), retention=reward_retention)))
              for sign in (-1, 1)]
    lags = []
    for low, high in zip(*curves, strict=True):
        lag = low["lag"]
        expected = Q(5, 6)**(lag - 1) / 6
        if (high["lag"] != lag or low["opportunity"] != expected
                or high["opportunity"] != expected):
            raise ArithmeticError("assignment changed the revision clock")
        lags.append({
            "lag": lag, "opportunity": expected,
            "minus4": low["rate"], "plus4": high["rate"],
            "minus4_minus_plus4": low["rate"] - high["rate"],
        })
    horizons = {}
    for h in HORIZONS:
        included = lags[:h-2]
        weight = sum(row["opportunity"] for row in included)
        numerator = sum(row["opportunity"] * row["minus4_minus_plus4"] for row in included)
        horizons[h] = {
            "opportunity_by_horizon": weight,
            "difference_given_opportunity": numerator / weight,
            "difference_in_observed_switches_per_assigned_group": numerator,
        }
    return {"lag": lags, "horizon": horizons}


def results():
    cases = {
        f"{start}_{'two' if two else 'one'}_{decay}": exact_signed_comparison(start, two, decay)
        for start, (two, decay) in product((4, 5),
                                         ((False, "independent"), (True, "independent"), (True, "shared")))
    }
    sensitivity = {}
    for retention in (Q(1, 4), Q(3, 4), Q(9, 10), Q(1)):
        case = exact_signed_comparison(5, reward_retention=retention)
        sensitivity[str(retention)] = {
            "last_nonzero_lag_within_40": max(row["lag"] for row in case["lag"] if row["minus4_minus_plus4"]),
            "at_10": case["horizon"][10]["difference_given_opportunity"],
            "at_40": case["horizon"][40]["difference_given_opportunity"],
        }
    return cases, sensitivity
