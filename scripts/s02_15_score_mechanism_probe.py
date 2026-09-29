#!/usr/bin/env python3
"""Adjudicate the bounded S02.15 p0/p1 T120↔TNEG mechanism probe.

No S02.14 burden target is read or computed here.
"""
from __future__ import annotations
import argparse, json, re, xml.etree.ElementTree as ET
from pathlib import Path

START_RE=re.compile(
    r"^Warning: Teleporting vehicle '([^']+)'; waited too long \(([^)]+)\), "
    r"lane='([^']+)', time=([0-9.]+)\.$"
)
ANCHORS={
    "000":{"id":"pedestrian_1-2_3883_tr","reason":"yield","lane":"152672#2_1","time":19705.25},
    "100":{"id":"special_1-3_53","reason":"yield","lane":"152672#2_1","time":19791.00},
}
SUMMARY_KEYS=("loaded","inserted","running","waiting","ended","halting","teleports","meanSpeed")

def starts(path:Path):
    out=[]
    for line in path.read_text(errors="replace").splitlines():
        m=START_RE.match(line)
        if m:
            out.append({"id":m.group(1),"reason":m.group(2),"lane":m.group(3),"time":float(m.group(4))})
    return out

def summary(path:Path):
    root=ET.parse(path).getroot()
    return {float(e.get("time")):{k:e.get(k) for k in SUMMARY_KEYS} for e in root.findall("step")}

def queue(path:Path):
    root=ET.parse(path).getroot()
    out={}
    for data in root.findall("data"):
        t=float(data.get("timestep"))
        lanes=data.find("lanes")
        vals=[]
        if lanes is not None:
            for e in lanes.findall("lane"):
                vals.append((e.get("id"),float(e.get("queueing_length","0") or 0)))
        out[t]={
            "queued_lanes":sum(v>0 for _,v in vals),
            "total_queue_length":sum(v for _,v in vals),
            "max_queue_length":max((v for _,v in vals),default=0.0),
        }
    return out

def eq_before(a,b,tau):
    times=sorted(set(a)&set(b))
    bad=[]
    for t in times:
        if t>=tau: continue
        for k in SUMMARY_KEYS:
            if a[t].get(k)!=b[t].get(k):
                bad.append({"time":t,"key":k,"t120":a[t].get(k),"tneg":b[t].get(k)})
                if len(bad)>=20:return bad
    return bad

def num(v):
    try:return float(v)
    except:return None

def post_delta(a,b,tau,end):
    rows=[]
    for t in sorted(set(a)&set(b)):
        if tau<=t<=end:
            row={"time":t}
            for k in ("running","waiting","ended","halting","teleports","meanSpeed"):
                x,y=num(a[t].get(k)),num(b[t].get(k))
                row[k]=None if x is None or y is None else x-y
            rows.append(row)
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cells",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result={
        "schema":"rithm-s02.15-bounded-mechanism-probe.v1",
        "stage":"RITHM-ORIGIN-S02.15",
        "target_aggregation_opened":False,
        "B":None,"R_B":None,"C_B":None,
        "cells":{},"pairs":{}
    }
    all_valid=True
    for p in ("000","100"):
        runs={}
        for regime in ("t120","tneg"):
            d=args.cells/f"s02-15-{p}-{regime}"
            status=json.loads((d/"status.json").read_text())
            err=d/"stderr.txt"
            sm=d/"summary.xml"
            qu=d/"queue.xml"
            ss=starts(err)
            runs[regime]={"status":status,"starts":ss,"summary":summary(sm),"queue":queue(qu)}
            result["cells"][f"{p}-{regime}"]={
                **status,
                "timeout_teleport_start_count":len(ss),
                "first_timeout_teleport":ss[0] if ss else None
            }
            all_valid &= bool(status.get("execution_valid"))
        t120,tneg=runs["t120"],runs["tneg"]
        anchor=ANCHORS[p]
        first=t120["starts"][0] if t120["starts"] else None
        anchor_exact=bool(first and first==anchor)
        tneg_zero=len(tneg["starts"])==0
        tau=anchor["time"]
        pre_bad=eq_before(t120["summary"],tneg["summary"],tau)
        post_end=min(tau+900,21600)
        deltas=post_delta(t120["summary"],tneg["summary"],tau,post_end)
        qt=max([t for t in set(t120["queue"])&set(tneg["queue"]) if t<=post_end],default=None)
        qlast=None
        if qt is not None:
            qa,qb=t120["queue"][qt],tneg["queue"][qt]
            qlast={
                "time":qt,
                "queued_lanes_delta_t120_minus_tneg":qa["queued_lanes"]-qb["queued_lanes"],
                "total_queue_length_delta_t120_minus_tneg":qa["total_queue_length"]-qb["total_queue_length"],
                "max_queue_length_delta_t120_minus_tneg":qa["max_queue_length"]-qb["max_queue_length"],
            }
        slast=deltas[-1] if deltas else None
        persistent=bool(slast and any(abs(slast[k] or 0)>0 for k in ("running","waiting","ended","halting","meanSpeed")))
        result["pairs"][p]={
            "historical_first_event_anchor":anchor,
            "t120_anchor_exact_reproduction":anchor_exact,
            "tneg_timeout_starts_zero":tneg_zero,
            "pre_tau_summary_exact":len(pre_bad)==0,
            "pre_tau_mismatches":pre_bad,
            "window":{"begin":tau-300,"tau":tau,"end":post_end},
            "summary_delta_at_window_end_t120_minus_tneg":slast,
            "queue_delta_at_last_sample_t120_minus_tneg":qlast,
            "persistent_global_aggregate_footprint_at_window_end":persistent,
            "post_window_summary_deltas":deltas,
        }
        all_valid &= anchor_exact and tneg_zero and len(pre_bad)==0
    result["admission_pass"]=all_valid
    if not all_valid:
        result["verdict"]="HOLD-MECHANISM-PROBE-ADMISSION"
    elif any(v["persistent_global_aggregate_footprint_at_window_end"] for v in result["pairs"].values()):
        result["verdict"]="PASS-PERSISTENT-REGULARIZATION-FOOTPRINT"
    else:
        result["verdict"]="NO-GLOBAL-AGGREGATE-PERSISTENCE-MICROSTATE-UNRESOLVED"
    result["next_authority"]="Return to Chat/RAVEL; no automatic full TNEG burden rerun."
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

if __name__=="__main__":
    main()
