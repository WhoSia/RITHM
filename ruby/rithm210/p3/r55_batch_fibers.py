"""RITHM R55: original-source, identity-aware six-actor batch switching fibers.

Never prints participant- or session-level data. Original ZIP stays private.
Synthetic tests can call analyze_rows(..., require_original=False).
"""
from collections import Counter, defaultdict
from fractions import Fraction
from math import comb
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from random import Random
from zipfile import ZipFile

from r54_original_batch_clock import (
    APPROVED_ZIP_SHA256, EXCLUDED_SESSIONS, SOURCE_NAME, audit_rows,
)


def fiber(a: int, b: int):
    """Feasible gross actor switching counts for an a -> b occupancy transition."""
    if type(a) is not int or type(b) is not int or not (0 <= a <= 6 and 0 <= b <= 6):
        raise ValueError("occupancies must be integers between zero and six")
    minimum = abs(b - a)
    maximum = min(a + b, 12 - a - b)
    return tuple(range(minimum, maximum + 1, 2))


def uniform_label_kernel(a: int, b: int):
    """P(G=g | a,b) if all next-period b-subsets of six actors are equiprobable.

    This is an explicit identity-randomizing counterfactual, NOT the observed
    people's choice law or a model of randomized treatment assignment.
    """
    choices = fiber(a, b)
    denominator = comb(6, b)
    distribution = {}
    for g in choices:
        down = (g - (b - a)) // 2
        up = (g + (b - a)) // 2
        ways = comb(a, down) * comb(6-a, up)
        distribution[g] = Fraction(ways, denominator)
    if sum(distribution.values()) != 1:
        raise ArithmeticError("hypergeometric occupancy fiber does not normalize")
    mean = sum((g*p for g, p in distribution.items()), Fraction())
    expected = Fraction(a*(6-b) + (6-a)*b, 6)
    if mean != expected:
        raise ArithmeticError("uniform-label conditional expectation mismatch")
    return distribution


def _numeric_field(row, name):
    try:
        return int(row[name])
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("invalid source field " + name) from exc


def _group_sections(rows):
    """Load locked R54 population at one actor-period grain; never export IDs."""
    grouped = defaultdict(lambda: defaultdict(dict))
    for row in rows:
        session = _numeric_field(row, "session")
        treatment = _numeric_field(row, "trt")
        period = _numeric_field(row, "Period")
        if session in EXCLUDED_SESSIONS or treatment not in (1,2,3) or period < 1:
            continue
        section = _numeric_field(row, "section")
        if section not in (2,3,4):
            raise ValueError("unexpected source section")
        key = (session, section, _numeric_field(row, "Group"), treatment)
        actor = _numeric_field(row, "ID")
        current = grouped[key][period]
        if actor in current:
            raise ValueError("duplicate actor-period row")
        route = _numeric_field(row, "RouteA")
        if route not in (0,1) or _numeric_field(row, "RouteB") != 1-route:
            raise ValueError("nonbinary route")
        current[actor] = (route,
                          _numeric_field(row, "NumA"),
                          _numeric_field(row, "NumB"),
                          Fraction(row["Cost"]))
    for sections in grouped.values():
        actors = set(sections[1])
        if len(actors) != 6 or sorted(sections) != list(range(1,len(sections)+1)):
            raise ValueError("broken six-seat history")
        for period, state in sections.items():
            if set(state) != actors:
                raise ValueError("broken actor identity")
            occupied = sum(item[0] for item in state.values())
            for route, na, nb, cost in state.values():
                expected = occupied if route else 2*(6-occupied)
                if (na, nb, cost) != (occupied, 6-occupied, expected):
                    raise ValueError("source occupancy or actual individual cost mismatch")
    return grouped


def _session_bootstrap(arm_session, primary=1, secondary=3, *, draws=8000, seed=20261121):
    """Diagnostic whole-session resampling; no randomized-population confidence claim."""
    sessions = sorted(set(s for s,t in arm_session))
    if len(sessions) < 2:
        return None
    if set(arm_session) != {(s,t) for s in sessions for t in (1,2,3)}:
        return None
    if any(len({arm_session[(s,t)]["group_sections"] for t in (1,2,3)}) != 1
           for s in sessions):
        raise ValueError("non-matched group section support within session")
    metrics = ("gross", "minimum", "excess_pairs", "congestion_excess", "uniform_numerator")
    rng = Random(seed)
    bands = {}
    for metric in metrics:
        # Each session has the same number of groups across arms, but across
        # sessions it can have 1, 2, or 3 per treatment: cluster-bootstrap
        # must sample entire sessions and weight by their group counts.
        numerators = [arm_session[(s,secondary)][metric] - arm_session[(s,primary)][metric]
                      for s in sessions]
        weights = [arm_session[(s,primary)]["group_sections"] for s in sessions]
        unit = 6 if metric == "uniform_numerator" else 1
        mean = Fraction(sum(numerators), sum(weights)*unit)
        draws_sorted = []
        for _ in range(draws):
            picks = [rng.randrange(len(sessions)) for _ in sessions]
            sampled = Fraction(sum(numerators[i] for i in picks),
                               sum(weights[i] for i in picks)*unit)
            draws_sorted.append(sampled)
        draws_sorted.sort()
        bands[metric] = {
            "paired_pooled_difference_per_group_section": round(float(mean),6),
            "resampled_2p5": round(float(draws_sorted[int(draws*0.025)]),6),
            "resampled_97p5": round(float(draws_sorted[min(draws-1,int(draws*0.975))]),6),
        }
    return {"arm_contrast": f"{secondary}-minus-{primary}", "sessions": len(sessions),
            "draws": draws, "seed": seed, "metric_differences_per_group_section": bands,
            "interpretation":"Descriptive paired-session sensitivity, not a causal or sampling CI."}


def analyze_rows(rows, *, require_original=False, source_sha256=None,
                 bootstrap_draws=8000):
    if type(bootstrap_draws) is not int or bootstrap_draws < 20:
        raise ValueError("positive bootstrap draw count >=20 required")
    rows = list(rows)
    baseline = audit_rows(rows, require_original=require_original,
                          source_sha256=source_sha256)
    grouped = _group_sections(rows)
    totals = Counter()
    arms = defaultdict(Counter)
    arm_sessions = defaultdict(Counter)
    occupancies = defaultdict(Counter)
    # Stable internal information; only aggregate counts ever returned.
    for key, periods in grouped.items():
        session, section, group, treatment = key
        acc = Counter(group_sections=1)
        for period in sorted(periods):
            n = sum(v[0] for v in periods[period].values())
            acc["periods"] += 1
            acc["congestion_excess"] += 3*(n-4)**2
        for period in range(2, len(periods)+1):
            before, after = periods[period-1], periods[period]
            a = sum(v[0] for v in before.values())
            b = sum(v[0] for v in after.values())
            up = sum(before[i][0] == 0 and after[i][0] == 1 for i in before)
            down = sum(before[i][0] == 1 and after[i][0] == 0 for i in before)
            gross = up+down
            possible = fiber(a,b)
            if gross not in possible:
                raise AssertionError("observed actor switches violate occupancy fiber")
            base = possible[0]
            uniform = Fraction(a*(6-b)+(6-a)*b,6)
            acc["transitions"] += 1
            acc["gross"] += gross
            acc["minimum"] += base
            acc["maximum"] += possible[-1]
            acc["excess_pairs"] += (gross - base)//2
            acc["extra_gross"] += gross-base
            acc["fiber_ambiguous"] += len(possible) > 1
            # Mean of uniform relabeling in 1/6 switch units for integer output.
            acc["uniform_numerator"] += 6*uniform
            occupancies[(a,b)][gross] += 1
        totals.update(acc)
        arms[treatment].update(acc)
        arm_sessions[(session,treatment)].update(acc)
    for key in ("gross", "transitions", "congestion_excess", "minimum", "maximum"):
        if key == "gross" and totals[key] != baseline["recorded_gross_switches"]:
            raise AssertionError("mismatched R54 gross identity")
        if key == "transitions" and totals[key] != baseline["group_period_transitions"]:
            raise AssertionError("mismatched R54 transition population")
    if totals["extra_gross"] != 2*totals["excess_pairs"]:
        raise AssertionError("turnover pair decomposition failed")
    if require_original:
        if len(arm_sessions) != 72 or set(arms) != {1,2,3}:
            raise ValueError("unbalanced 24-session treatment schedule")
        if any(arm_sessions[key]["group_sections"] not in (1,2,3) for key in arm_sessions):
            raise ValueError("unexpected group-section count per session")
        if any(len({arm_sessions[(session,t)]["group_sections"] for t in (1,2,3)}) != 1
               for session in {k[0] for k in arm_sessions}):
            raise ValueError("unmatched within-session treatment group sections")
        if any(arms[t]["group_sections"] != 48 or arms[t]["transitions"] != 1872
               or arms[t]["periods"] != 1920 for t in (1,2,3)):
            raise ValueError("treatment-period population differs from historical contract")
    summary = {
        "scope": (
            "Original 24-session observational descriptive cohort; treatment differences "
            "do NOT identify causal effects. Uniform relabeling is hypothetical, "
            "not an observed mechanism or an alternative original experiment."
        ),
        "source_zip_sha256": source_sha256,
        "source_contract": {
            "retained_R_script_filter": "9 exp_data_Part1_adjustment behavior.R and 102 exp_data_s123_plot and test_nocolor.R",
            "other_R_script_nonidentical": "0 data preparation.R applies a different session-101 and pilot exclusion; not interchangeable",
            "source_NumSwitch_mismatch_rows": baseline["source_declared_switch_mismatches"],
            "source_NumA_NumB_and_Cost_mismatch_rows": 0,
        },
        "population": {"sessions": baseline["sessions"],
                       "group_sections": len(grouped),
                       "actor_decisions": baseline["individual_choices"],
                       "group_period_transitions": totals["transitions"]},
        "switches": {
            "minimum_given_occupancy": totals["minimum"],
            "observed_actor_changes": totals["gross"],
            "extra_cancelling_pairs": totals["excess_pairs"],
            "extra_beyond_occupancy_minimum": totals["extra_gross"],
            "maximum_given_occupancy": totals["maximum"],
            "uniform_identity_expected_switches_exact": (
                f"{Fraction(totals['uniform_numerator'],6)}"),
            "transitions_with_multiple_feasible_gross_counts": totals["fiber_ambiguous"],
        },
        "treatments": {
            str(t): {"label": {1:"No",2:"Partial",3:"Full"}[t],
                     "group_sections": arms[t]["group_sections"],
                     "periods": arms[t]["periods"],
                     "transitions": arms[t]["transitions"],
                     "congestion_excess_40_periods": arms[t]["congestion_excess"],
                     "gross_switches_39_transitions": arms[t]["gross"],
                     "occupancy_minimum": arms[t]["minimum"],
                     "extra_switches": arms[t]["extra_gross"],
                     "opposing_direction_pairs": arms[t]["excess_pairs"],
                     "uniform_identity_expected_switches_exact": str(Fraction(arms[t]["uniform_numerator"],6))}
            for t in sorted(arms)
        },
    }
    c = occupancies.get((4,4), Counter())
    n_44=sum(c.values())
    if n_44:
        summary["four_to_four_occupancy_fiber"] = {
            "transitions":n_44,
            "observed_gross_count_distribution":{str(g):c[g] for g in fiber(4,4)},
            "uniform_label_probability_exact":{str(g):str(p) for g,p in uniform_label_kernel(4,4).items()},
        }
    if set(arms)=={1,2,3}:
        base = arms[1]
        summary["observed_aggregate_welfare_contrasts"] = {
            "Partial_minus_No": {
                "congestion_excess_difference_per_group_section": str(Fraction(arms[2]["congestion_excess"]-base["congestion_excess"],arms[2]["group_sections"])),
                "gross_switch_difference_per_group_section": str(Fraction(arms[2]["gross"]-base["gross"],arms[2]["group_sections"])),
                "switch_price_crossover_exact_if_nonnegative": (
                    str(Fraction(base["congestion_excess"]-arms[2]["congestion_excess"],
                                 arms[2]["gross"]-base["gross"]))
                    if arms[2]["congestion_excess"] < base["congestion_excess"]
                    and arms[2]["gross"] > base["gross"] else None),
            },
            "Full_minus_No": {
                "congestion_excess_difference_per_group_section": str(Fraction(arms[3]["congestion_excess"]-base["congestion_excess"],arms[3]["group_sections"])),
                "gross_switch_difference_per_group_section":str(Fraction(arms[3]["gross"]-base["gross"],arms[3]["group_sections"])),
            },
        }
        summary["session_arm_group_section_count_distribution"] = {
            str(n):count for n,count in sorted(Counter(
                record["group_sections"] for record in arm_sessions.values()).items())
        }
        summary["descriptive_session_resampling"] = [
            _session_bootstrap(arm_sessions,primary=1,secondary=2,draws=bootstrap_draws,seed=20261121),
            _session_bootstrap(arm_sessions,primary=1,secondary=3,draws=bootstrap_draws,seed=20261122)]
    return summary


def analyze_zip(path, *, bootstrap_draws=8000):
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != APPROVED_ZIP_SHA256:
        raise ValueError("original research ZIP SHA-256 mismatch")
    with ZipFile(io.BytesIO(raw)) as z:
        if SOURCE_NAME not in z.namelist():
            raise ValueError("missing original source table")
        rows = csv.DictReader(io.TextIOWrapper(z.open(SOURCE_NAME),encoding="utf-8-sig",newline=""))
        return analyze_rows(rows,require_original=True,source_sha256=digest,
                            bootstrap_draws=bootstrap_draws)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("approved_source_zip",type=Path)
    p.add_argument("--bootstrap-draws",type=int,default=8000)
    args=p.parse_args()
    print(json.dumps(analyze_zip(args.approved_source_zip,
                                 bootstrap_draws=args.bootstrap_draws),indent=2,sort_keys=True))
