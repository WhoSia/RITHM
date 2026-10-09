#!/usr/bin/env python3
"""RITHM-2.0: original human group-route-choice welfare, descriptive only."""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

N = 18

def pay_main(s):
    return 40 - (6 + 2 * (N-s))

def pay_side(s):
    return 40 - (12 + 3*s)

def welfare(s):
    if type(s) is not int or not 0 <= s <= N:
        raise ValueError("Invalid side-road occupancy")
    return (N-s)*pay_main(s) + s*pay_side(s)

def nash_side_counts():
    return [s for s in range(N+1)
            if (s == N or pay_main(s) >= pay_side(s+1))
            and (s == 0 or pay_side(s) >= pay_main(s-1))]

def mean(a):
    return math.fsum(a)/len(a)

def analyze(csv_path, strict=False):
    p = Path(csv_path)
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    group, person, seen = defaultdict(list), defaultdict(list), set()
    required = {"Period","Subject","Profit","LaneM","LaneS","S","M",
                "Session","Treatment","switch","infotreat"}
    with p.open(newline="", encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)
        if not required.issubset(rows.fieldnames or []):
            raise ValueError("Study 1 schema mismatch")
        for r in rows:
            sess,period,subject = (int(r[k]) for k in ("Session","Period","Subject"))
            s,m,ls,lm,profit,info,tr = (int(r[k]) for k in
                ("S","M","LaneS","LaneM","Profit","infotreat","Treatment"))
            if not (1 <= period <= 100 and 0 <= s <= N and s+m == N
                    and ls+lm == 1 and info in (0,1)):
                raise ValueError("Invalid occupancy, choice, period or information")
            if profit != (pay_side(s) if ls else pay_main(s)):
                raise ValueError("Individual source payoff mismatch")
            key = (sess,period,subject)
            if key in seen: raise ValueError("Duplicate subject decision")
            seen.add(key)
            group[(sess,period)].append((subject,s,m,ls,profit,tr,info))
            person[(sess,subject)].append((period,ls,r["switch"]))
    if not seen: raise ValueError("Empty source")
    rounds, per_session = [], defaultdict(list)
    for (sess,period),g in sorted(group.items()):
        if (len(g)!=N or len({(x[1],x[2],x[5]) for x in g})!=1
                or sum(x[3] for x in g)!=g[0][1]
                or len({x[0] for x in g})!=N):
            raise ValueError("Group-round occupancy or IDs fail")
        s = g[0][1]
        if sum(x[4] for x in g)!=welfare(s):
            raise ValueError("Group payoff sum mismatch")
        out = {"session":sess,"period":period,"side":s,"w":welfare(s),
               "info":sum(x[6] for x in g),"treatment":g[0][5]}
        rounds.append(out);per_session[sess].append(out)
    if strict and not (len(seen)==18000 and len(group)==1000
                       and len(per_session)==10 and len(person)==180
                       and all(len(g)==100 for g in per_session.values())
                       and all(len(v)==100 for v in person.values())):
        raise ValueError("Original source universe mismatch")
    by_group = defaultdict(int)
    checked = 0
    for (sess,sub),series in person.items():
        series.sort()
        for old,new in zip(series,series[1:]):
            if new[0]!=old[0]+1: raise ValueError("Nonconsecutive participant history")
            switch = int(old[1]!=new[1])
            if new[2].strip() and int(new[2])!=switch:
                raise ValueError("Author switch variable not aligned")
            by_group[(sess,new[0])]+=switch
            checked+=1
    trans=[]
    for sess,series in per_session.items():
        series.sort(key=lambda x:x["period"])
        for prev,nxt in zip(series,series[1:]):
            trans.append((prev,nxt,by_group[(sess,nxt["period"])]))
    sides=[r["side"] for r in rounds]
    avg_s=mean(sides)
    var_s=mean([(s-avg_s)**2 for s in sides])
    avg_w=mean([r["w"] for r in rounds])
    optimum=max(welfare(s) for s in range(N+1))
    opt_s=[s for s in range(N+1) if welfare(s)==optimum]
    w_at_avg=-36+66*avg_s-5*avg_s*avg_s
    allocation=optimum-w_at_avg
    dispersion=5*var_s
    gap=optimum-avg_w
    if not math.isclose(gap,allocation+dispersion,abs_tol=1e-8):
        raise AssertionError("Quadratic welfare identity failed")
    return {
      "version":"RITHM-2.0",
      "status":"EXPLORATORY_DESCRIPTIVE_NOT_CAUSAL",
      "input_sha256":sha,"individual_decisions":len(seen),
      "session_count":len(per_session),"group_round_count":len(rounds),
      "mean_side_count":avg_s,"side_count_population_variance":var_s,
      "mean_group_welfare":avg_w,"integer_optimum_side_count":opt_s,
      "integer_optimum_welfare":optimum,"pure_nash_side_counts":nash_side_counts(),
      "mean_optimum_shortfall":gap,"mean_allocation_component":allocation,
      "mean_dispersion_component":dispersion,
      "dispersion_share":dispersion/gap if gap else None,
      "rounds_at_optimum":sum(r["side"] in opt_s for r in rounds),
      "person_transition_checks":checked,
      "group_transitions":len(trans),
      "mean_gross_switches":mean([x[2] for x in trans]) if trans else None,
      "net_count_unchanged_but_gross_switches":sum(x[0]["side"]==x[1]["side"] and x[2]>0 for x in trans),
      "welfare_decline_transitions":sum(x[1]["w"]<x[0]["w"] for x in trans),
      "optimum_start_transitions":sum(x[0]["side"] in opt_s for x in trans),
      "optimum_abandoned_transitions":sum(x[0]["side"] in opt_s and x[1]["side"] not in opt_s for x in trans),
      "session_summaries":[{
          "session":sid,"treatment":series[0]["treatment"],
          "mean_welfare":mean([r["w"] for r in series]),
          "pre_post_difference_descriptive":(
              mean([r["w"] for r in series if r["period"]>50])
              -mean([r["w"] for r in series if r["period"]<=50])
              if any(r["period"]>50 for r in series)
              and any(r["period"]<=50 for r in series) else None)
          } for sid,series in sorted(per_session.items())],
      "limits":[
          "10 live human groups are the possible independent units, not 18000 rows",
          "No randomized information-to-welfare causal effect established",
          "No identified causal habit, memory or trust mechanism",
          "Study 2 replays historical opponents and is a different causal ecology"
      ]
    }

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("study1_csv", type=Path)
    a.add_argument("--strict-source", action="store_true")
    v=a.parse_args()
    print(json.dumps(analyze(v.study1_csv,strict=v.strict_source),indent=2,sort_keys=True))
