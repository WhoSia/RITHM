#!/usr/bin/env python3
"""RITHM 2.6 P13-R2b: summarize raw source-derived 21d/7d real sensor CSV weekly scores.
The input is a C++ empirical model's small aggregated CSV, not actual human welfare.
"""
import csv, json, random, sys
METHODS=("training_calendar_median","observed_previous_5min","training_estimated_linear_trend")
METRICS=("speed_mae_kmh","volume_mae_vehicles_per_5min","proxy_mae_vehicle_hour_per_km")
def summarize(rows):
    folds={}
    for row in rows:folds.setdefault(row["window"],{})[row["method"]]=row
    rolling={k:v for k,v in folds.items() if k.startswith("rolling_") and set(v)==set(METHODS)}
    if not rolling:raise ValueError("No valid rolling weeks")
    names=sorted(rolling)
    for k,v in rolling.items():
        if len({int(x["observations"]) for x in v.values()})!=1:raise ValueError("Unequal targets "+k)
        if len({(x["train_start"],x["train_end"],x["test_start"],x["test_end"]) for x in v.values()})!=1:raise ValueError("Different clocks "+k)
    def ave(sample,metric,model):
        den=sum(int(rolling[k][model]["observations"]) for k in sample)
        return sum(float(rolling[k][model][metric])*int(rolling[k][model]["observations"]) for k in sample)/den
    out={"study":"RITHM-2.6 P13-R2b","weeks":len(names),
         "paired_5min_link_observations":sum(int(rolling[k][METHODS[0]]["observations"]) for k in names),
         "causal_human_welfare":False,"seven_day_autonomous_forecast":False,
         "metrics":{}}
    for j,metric in enumerate(METRICS):
        avg={model:ave(names,metric,model) for model in METHODS}
        rng=random.Random(20261012+j);boots=[]
        for _ in range(4000):
            sample=[names[rng.randrange(len(names))] for _ in names]
            boots.append(ave(sample,metric,METHODS[1])-ave(sample,metric,METHODS[2]))
        boots.sort()
        out["metrics"][metric]={
            "weighted_mae":avg,
            "smoothing_vs_lag_gain_pct":100*(avg[METHODS[1]]-avg[METHODS[2]])/avg[METHODS[1]],
            "weeks_smoothing_beats_lag":sum(float(v[METHODS[2]][metric])<float(v[METHODS[1]][metric]) for v in rolling.values()),
            "descriptive_resampled_week_difference_interval95":[boots[99],boots[3899]]
        }
    return out
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: p13_weekly_rolling_report.py input_scores.csv output_summary.json")
    with open(sys.argv[1],newline="",encoding="utf-8") as f:out=summarize(list(csv.DictReader(f)))
    with open(sys.argv[2],"w",encoding="utf-8") as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(out["weeks"],out["paired_5min_link_observations"])
