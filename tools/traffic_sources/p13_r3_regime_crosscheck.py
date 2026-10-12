#!/usr/bin/env python3
"""P13-R3 compact observational source-summary validator. No raw data in GitHub.

Full 38-shard forensic source reader, diagnostics and test suite are in the P13-R3
conversation archive. This smaller script verifies their *exported aggregate*
contracts and never claims that summaries alone revalidate source CSV hashes.
"""
import argparse
import json
from pathlib import Path

def check(weekly, periodicity, daily, cross_sensor):
    w = json.loads(Path(weekly).read_text(encoding="utf-8"))
    p = json.loads(Path(periodicity).read_text(encoding="utf-8"))
    d = json.loads(Path(daily).read_text(encoding="utf-8"))
    c = json.loads(Path(cross_sensor).read_text(encoding="utf-8"))
    passed = [r for r in w if r.get("status")=="PASS"]
    rejected = [r for r in w if r.get("status")!="PASS"]
    if len(passed)!=41 or len(rejected)!=8:
        raise ValueError("Expected 41 source-admitted, 8 blackout-rejected weeks")
    if len({r["test_start"] for r in w})!=49:
        raise ValueError("Duplicate weekly train/test clock")
    n = sum(r["matched_lag_120_cohort_n"] for r in passed)
    if n!=14493248:
        raise ValueError("Source common 5-120min target cohort changed")
    parity = {r["window"]:r for r in p["cases"]}
    if parity["april"]["odd_minus_even_mean_mae"]<=20:
        raise ValueError("April 10-minute parity observation not reproduced")
    if parity["ordinary_feb"]["odd_minus_even_mean_mae"]>=0:
        raise ValueError("Normal February negative-control not reproduced")
    if parity["april"]["lag10_beats_lag5_links"]!=177:
        raise ValueError("Original-link April cohort changed")
    controls={r["window"]:r for r in c["windows"]}
    if abs(controls["apr16"]["corr_dq5_dv5"])>.02:
        raise ValueError("Source speed negative-control drift")
    if d["days_with_source_at_least_10"]!=360:
        raise ValueError("Source date coverage changed")
    top=d["top_12_source_days"][0]
    if top["date"]!="2025-04-19" or top["flow_ratio_5_over_10"]<3:
        raise ValueError("Daily source regime event changed")
    return {
        "status":"SOURCE_AGGREGATE_CONTRACT_PASS_NOT_NEW_SOURCE_READ",
        "weeks":41,"blackout_windows":8,"common_lag_target_rows":n,
        "april_odd_even_parity_mae":parity["april"]["odd_minus_even_mean_mae"],
        "ordinary_feb_odd_even_parity_mae":parity["ordinary_feb"]["odd_minus_even_mean_mae"],
        "april_link_lag10_wins":177,
        "april_corr_five_min_d_volume_d_speed":controls["apr16"]["corr_dq5_dv5"],
        "daily_source_regime_events":d["exploratory_retrospectively_detected_flow_ratio_gt_1point2_periods"],
        "original_cp949_rehash":False,
        "physical_sensor_production_cause_identified":False,
        "individual_human_welfare_identified":False,
        "causal_information_effect_identified":False
    }

if __name__=="__main__":
    a=argparse.ArgumentParser()
    for key in ("weekly","periodicity","daily","cross-sensor","out"):
        a.add_argument("--"+key,required=True,type=Path)
    p=a.parse_args()
    result=check(p.weekly,p.periodicity,p.daily,p.cross_sensor)
    p.out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(result["status"])
