"""R54: source-replay audit of the author's simultaneous 6-seat choice periods.

The input source remains private, original, and separate from GitHub.
This CLI prints only cohort-level aggregates, never participant rows.
"""
import argparse
from collections import Counter, defaultdict
import csv
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

SOURCE_NAME = "data_task_all_switch_230705.csv"
EXCLUDED_SESSIONS = frozenset({2, 101})


@lru_cache(None)
def minimal_order_cost_bounds(start_a, up, down):
    """Hypothetical sum of post-action excess costs, MIN/MAX over switch orders.

    Only participants who changed between periods move, exactly once each.
    This does NOT describe observed within-period welfare.
    """
    if any(type(v) is not int or v < 0 for v in (start_a, up, down)):
        raise ValueError("invalid transition count")
    if not (0 <= start_a <= 6 and down <= start_a and up <= 6-start_a):
        raise ValueError("physically impossible transition")

    @lru_cache(None)
    def calc(done_up, done_down):
        if (done_up, done_down) == (up, down):
            return (0, 0)
        choices = []
        if done_up < up:
            next_n = start_a + (done_up+1) - done_down
            lo, hi = calc(done_up+1, done_down)
            g = 3*(next_n-4)**2
            choices.append((g+lo, g+hi))
        if done_down < down:
            next_n = start_a + done_up - (done_down+1)
            lo, hi = calc(done_up, done_down+1)
            g = 3*(next_n-4)**2
            choices.append((g+lo, g+hi))
        return min(t[0] for t in choices), max(t[1] for t in choices)

    return calc(0, 0)


def audit_rows(rows, *, require_original=False, source_sha256=None):
    groups = defaultdict(dict)
    participant_count = 0
    group_treatment = {}
    for row in rows:
        try:
            session = int(row["session"])
            section = int(row["section"])
            treatment = int(row["trt"])
            period = int(row["Period"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError("invalid source identifiers") from e
        if session in EXCLUDED_SESSIONS or not 1 <= treatment <= 3 or period < 1:
            continue
        if section not in (2, 3, 4):
            raise ValueError("unexpected retained section")
        try:
            group = int(row["Group"])
            actor = int(row["ID"])
            route_a = int(row["RouteA"])
            route_b = int(row["RouteB"])
            declared_switches = int(row["NumSwitch"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError("invalid retained choice row") from e
        if route_a not in (0, 1) or route_b != 1-route_a:
            raise ValueError("invalid binary route encoding")
        key = (session, section, group)
        old_treatment = group_treatment.setdefault(key, treatment)
        if old_treatment != treatment:
            raise ValueError("treatment changed within group section")
        at_period = groups[key].setdefault(period, {})
        if actor in at_period:
            raise ValueError("duplicate actor in group period")
        at_period[actor] = (route_a, declared_switches)
        participant_count += 1

    histogram = Counter()
    n_transitions = n_multi = n_bidirectional = n_churn = n_4to4 = 0
    n_5swap = n_order_ambiguous = total_lower = total_upper = 0
    mismatch = 0
    sessions = set()
    for key, period_dict in groups.items():
        sessions.add(key[0])
        periods = sorted(period_dict)
        if len(periods) < 2 or periods != list(range(1, len(periods)+1)):
            raise ValueError("missing or nonconsecutive group period")
        actors = set(period_dict[1])
        if len(actors) != 6:
            raise ValueError("group does not have exactly six actors")
        for t in periods:
            if set(period_dict[t]) != actors:
                raise ValueError("actor changed identity within group")
        for t in periods[1:]:
            before = period_dict[t-1]
            after = period_dict[t]
            up = sum(before[a][0] == 0 and after[a][0] == 1 for a in actors)
            down = sum(before[a][0] == 1 and after[a][0] == 0 for a in actors)
            gross = up + down
            for a in actors:
                mismatch += int(after[a][1] != gross)
            start_a = sum(before[a][0] for a in actors)
            end_a = sum(after[a][0] for a in actors)
            low, high = minimal_order_cost_bounds(start_a, up, down)
            histogram[gross] += 1
            n_transitions += 1
            n_multi += int(gross >= 2)
            n_bidirectional += int(up > 0 and down > 0)
            n_churn += int(gross > 0 and start_a == end_a)
            n_4to4 += int(gross > 0 and start_a == end_a == 4)
            n_5swap += int(start_a == 5 and up == down == 1)
            n_order_ambiguous += int(low < high)
            total_lower += low
            total_upper += high
    if mismatch:
        raise ValueError(f"source NumSwitch mismatch: {mismatch} actor rows")
    if require_original and (len(sessions),participant_count,len(groups),n_transitions) != (24,34560,144,5616):
        raise ValueError("not the sealed 24-session original analysis population")
    return {
        "input_sha256": source_sha256,
        "source_name": SOURCE_NAME,
        "selection": "trt in {1,2,3}; Period>=1; exclude sessions 2 and 101; sections 2-4",
        "sessions": len(sessions), "individual_choices": participant_count,
        "six_actor_group_sections": len(groups), "group_period_transitions": n_transitions,
        "recorded_gross_switches": sum(gross*n for gross,n in histogram.items()),
        "gross_switch_histogram": dict(sorted(histogram.items())),
        "two_or_more_switches": n_multi,
        "both_direction_switches": n_bidirectional,
        "constant_occupancy_with_churn": n_churn,
        "four_to_four_with_churn": n_4to4,
        "five_to_five_one_each_direction": n_5swap,
        "unknown_order_changes_hypothetical_microcost": n_order_ambiguous,
        "hypothetical_microstep_excess_sum_range": [total_lower, total_upper],
        "source_declared_switch_mismatches": mismatch,
        "scope": "Boundary-period choices only; intermediate action order and microstep welfare are unobserved. No causal estimate.",
    }


def audit_zip(path, *, require_original=True):
    raw = Path(path).read_bytes()
    with ZipFile(io.BytesIO(raw)) as archive:
        if SOURCE_NAME not in archive.namelist():
            raise ValueError("missing source CSV")
        text = archive.read(SOURCE_NAME).decode("utf-8-sig")
    return audit_rows(csv.DictReader(io.StringIO(text)), require_original=require_original,
                      source_sha256=hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_zip", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit_zip(args.original_zip), indent=2, sort_keys=True))
