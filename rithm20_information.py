#!/usr/bin/env python3
"""RITHM 2.0: human live-group information-onset and welfare DESCRIPTION.

Treatments are pre-period switching-frequency-selected in arms 3/4. The
session contrasts below are descriptive, not causal or powered statistics.
"""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from rithm20 import analyze, mean, welfare

TREATMENTS = {1: "Control", 2: "All", 3: "Frequent-4", 4: "Infrequent-4"}
EXPECTED = {1: 2, 2: 2, 3: 3, 4: 3}


def popvar(values):
    m = mean(values)
    return mean([(x - m) ** 2 for x in values])


def selection_check(treatment, pre_switches, informed):
    """Check rank boundaries; ties at the selection boundary are admissible."""
    if treatment == 3 and min(pre_switches[x] for x in informed) < max(
            pre_switches[x] for x in pre_switches if x not in informed):
        raise ValueError("Frequent-4 allocation contradicts pre-period rank")
    if treatment == 4 and max(pre_switches[x] for x in informed) > min(
            pre_switches[x] for x in pre_switches if x not in informed):
        raise ValueError("Infrequent-4 allocation contradicts pre-period rank")


def describe(csv_path, strict=False):
    # Canonical reconstruction validates source rows and the exact group-payoff
    # identity before the additional behavioral/assignment checks.
    base = analyze(csv_path, strict=strict)
    groups, persons = defaultdict(list), defaultdict(list)
    with Path(csv_path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            session = int(row["Session"])
            period = int(row["Period"])
            subject = int(row["Subject"])
            treatment = int(row["Treatment"])
            if treatment not in TREATMENTS:
                raise ValueError("Unknown treatment code")
            info = int(row["infotreat"])
            switch = row["switch"].strip()
            if switch not in ("", "0", "1"):
                raise ValueError("Nonbinary switch coding")
            item = {"session": session, "period": period, "subject": subject,
                    "treatment": treatment, "side": int(row["S"]),
                    "info": info, "switch": int(switch) if switch else 0}
            groups[(session, period)].append(item)
            persons[(session, subject)].append(item)
    session_rows = defaultdict(list)
    for (session, period), records in sorted(groups.items()):
        if len(records) != 18 or len({x["treatment"] for x in records}) != 1:
            raise ValueError("Invalid session/group")
        t = records[0]["treatment"]
        num_info = sum(x["info"] for x in records)
        expected = 0 if period <= 50 else {1: 0, 2: 18, 3: 4, 4: 4}[t]
        if num_info != expected:
            raise ValueError("Information onset or dose mismatch")
        side = records[0]["side"]
        session_rows[session].append({
            "period": period, "side": side, "welfare": welfare(side),
            "switches": sum(x["switch"] for x in records),
            "info": num_info, "treatment": t,
        })
    summaries = []
    for session, period_rows in sorted(session_rows.items()):
        period_rows.sort(key=lambda x: x["period"])
        if strict and [x["period"] for x in period_rows] != list(range(1, 101)):
            raise ValueError("Not 100 complete session periods")
        treatment = period_rows[0]["treatment"]
        participants = {sub: sorted(v, key=lambda x: x["period"])
                        for (ss, sub), v in persons.items() if ss == session}
        if len(participants) != 18:
            raise ValueError("Participant count changed")
        first = [x for x in period_rows if x["period"] <= 50]
        last = [x for x in period_rows if x["period"] > 50]
        if not first or not last:
            raise ValueError("Missing pre/post information epoch")
        pre_sw = {sub: sum(x["switch"] for x in v if x["period"] <= 50)
                  for sub, v in participants.items()}
        treated = set()
        for sub, history in participants.items():
            post = [x for x in history if x["period"] > 50]
            count = sum(x["info"] for x in post)
            if count not in (0, len(post)):
                raise ValueError("Participant information changed within post half")
            if count:
                treated.add(sub)
        n_treated = {1: 0, 2: 18, 3: 4, 4: 4}[treatment]
        if len(treated) != n_treated:
            raise ValueError("Number of informed subjects is wrong")
        if treatment in (3, 4):
            selection_check(treatment, pre_sw, treated)
        pre_w, post_w = [x["welfare"] for x in first], [x["welfare"] for x in last]
        pre_s, post_s = [x["side"] for x in first], [x["side"] for x in last]
        # Period 1 contains no prior route to switch FROM; compare 49 vs 50
        # explicitly, rather than treating the initial absent switch as zero.
        pre_switches = [x["switches"] for x in first if x["period"] >= 2]
        post_switches = [x["switches"] for x in last]
        summaries.append({
            "session": session, "treatment": treatment,
            "label": TREATMENTS[treatment], "n_informed": len(treated),
            "pre_welfare": mean(pre_w), "post_welfare": mean(post_w),
            "delta_welfare": mean(post_w) - mean(pre_w),
            "pre_side_variance": popvar(pre_s),
            "post_side_variance": popvar(post_s),
            "delta_side_variance": popvar(post_s) - popvar(pre_s),
            "pre_mean_side": mean(pre_s), "post_mean_side": mean(post_s),
            "pre_mean_switches_49_transitions": mean(pre_switches),
            "post_mean_switches_50_transitions": mean(post_switches),
            "informed_pre_switch_mean": (
                mean([pre_sw[k] for k in treated]) if treated else None),
            "not_informed_pre_switch_mean": (
                mean([pre_sw[k] for k in pre_sw if k not in treated])
                if len(treated) < len(pre_sw) else None)
        })
    sizes = Counter(s["treatment"] for s in summaries)
    if strict and dict(sizes) != EXPECTED:
        raise ValueError("Treatment-session counts differ from paper")
    arms = []
    control = mean([s["delta_welfare"] for s in summaries
                    if s["treatment"] == 1])
    for treatment in sorted(sizes):
        data = [s for s in summaries if s["treatment"] == treatment]
        dw = mean([s["delta_welfare"] for s in data])
        arms.append({"treatment": treatment, "label": TREATMENTS[treatment],
                     "n_sessions": len(data), "mean_pre_post_delta_welfare": dw,
                     "descriptive_delta_vs_control": dw - control,
                     "mean_change_side_variance":
                         mean([s["delta_side_variance"] for s in data])})
    return {"version": "RITHM-2.0", "status": "DESCRIPTIVE_NOT_CAUSAL",
            "input_sha256": base["input_sha256"],
            "sessions": summaries, "treatment_summaries": arms,
            "group_rounds": base["group_round_count"],
            "independent_session_units": base["session_count"],
            "limits": ["Group information regimens differ by whole session",
                       "Four-person assignment is selected by prior switching",
                       "No session-level randomization test is claimed",
                       "Study 2 fixed-opponent effects cannot be transferred",
                       "Ten sessions are not 18000 independent replicates"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("study1_csv", type=Path)
    p.add_argument("--strict-source", action="store_true")
    args = p.parse_args()
    print(json.dumps(describe(args.study1_csv, strict=args.strict_source),
                     indent=2, sort_keys=True))
