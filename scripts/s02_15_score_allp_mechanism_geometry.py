#!/usr/bin/env python3
"""Adjudicate S02.15 all-penetration T120↔TNEG event-local mechanism geometry.

Reuses already-admitted p=0 and p=1 bounded-probe artifacts and adds fresh
p=.30 and p=.70 pairs. It never reads or computes the S02.14 burden target.
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
    "030":{"id":"pedestrian_1-1-pt_8611_tr","reason":"yield","lane":"152672#2_1","time":19467.00},
    "070":{"id":"pedestrian_1-GW1_458_tr","reason":"wrong lane","lane":"152399#3_2","time":19030.00},
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

def num(v):
    try:return float(v)
    except:return None

def exact_before(a,b,tau):
    mismatches=[]
    for t in sorted(set(a)&set(b)):
        if t>=tau: continue
        for k in SUMMARY_KEYS:
            if a[t].get(k)!=b[t].get(k):
                mismatches.append({"time":t,"key":k,"t120":a[t].get(k),"tneg":b[t].get(k)})
                if len(mismatches)>=20:return mismatches
    return mismatches

def sdelta(a,b,t):
    if t not in a or t not in b:return None
    row={"time":t}
    for k in ("running","waiting","ended","halting","teleports","meanSpeed"):
        x,y=num(a[t].get(k)),num(b[t].get(k))
        row[k]=None if x is None or y is None else x-y
    return row

def qdelta(a,b,t):
    if t not in a or t not in b:return None
    return {
        "time":t,
        "queued_lanes":a[t]["queued_lanes"]-b[t]["queued_lanes"],
        "total_queue_length":a[t]["total_queue_length"]-b[t]["total_queue_length"],
        "max_queue_length":a[t]["max_queue_length"]-b[t]["max_queue_length"],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cells",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()

    result={
        "schema":"rithm-s02.15-allp-event-local-geometry.v1",
        "stage":"RITHM-ORIGIN-S02.15",
        "target_aggregation_opened":False,
        "B":None,"R_B":None,"C_B":None,
        "pairs":{}
    }
    admission=True
    persistent=[]

    for p in ("000","030","070","100"):
        runs={}
        for regime in ("t120","tneg"):
            d=args.cells/f"s02-15-{p}-{regime}"
            status=json.loads((d/"status.json").read_text())
            runs[regime]={
                "status":status,
                "starts":starts(d/"stderr.txt"),
                "summary":summary(d/"summary.xml"),
                "queue":queue(d/"queue.xml"),
            }
            admission &= bool(status.get("execution_valid"))
        a,b=runs["t120"],runs["tneg"]
        anchor=ANCHORS[p]
        first=a["starts"][0] if a["starts"] else None
        anchor_ok=first==anchor
        tneg_zero=len(b["starts"])==0
        pre_bad=exact_before(a["summary"],b["summary"],anchor["time"])
        tau=anchor["time"]; end=min(tau+900,21600.0)

        stimes=[t for t in set(a["summary"])&set(b["summary"]) if tau<=t<=end]
        qtimes=[t for t in set(a["queue"])&set(b["queue"]) if tau<=t<=end]
        send=max(stimes) if stimes else None
        qend=max(qtimes) if qtimes else None
        sd=sdelta(a["summary"],b["summary"],send) if send is not None else None
        qd=qdelta(a["queue"],b["queue"],qend) if qend is not None else None

        sdiv=0
        for t in stimes:
            d=sdelta(a["summary"],b["summary"],t)
            if d and any(abs(d[k] or 0)>0 for k in ("running","waiting","ended","halting","meanSpeed")):
                sdiv+=1
        qdiv=0
        for t in qtimes:
            d=qdelta(a["queue"],b["queue"],t)
            if d and any(abs(d[k])>1e-12 for k in ("queued_lanes","total_queue_length","max_queue_length")):
                qdiv+=1

        persist=bool(
            (sd and any(abs(sd[k] or 0)>0 for k in ("running","waiting","ended","halting","meanSpeed")))
            or (qd and any(abs(qd[k])>1e-12 for k in ("queued_lanes","total_queue_length","max_queue_length")))
        )
        persistent.append(persist)
        result["pairs"][p]={
            "historical_first_event_anchor":anchor,
            "t120_anchor_exact_reproduction":anchor_ok,
            "tneg_timeout_starts_zero":tneg_zero,
            "pre_tau_summary_exact":len(pre_bad)==0,
            "pre_tau_mismatches":pre_bad,
            "window":{"tau":tau,"end":end},
            "summary_delta_at_window_end_t120_minus_tneg":sd,
            "queue_delta_at_last_sample_t120_minus_tneg":qd,
            "summary_divergence_occupancy":sdiv/len(stimes) if stimes else None,
            "queue_divergence_occupancy":qdiv/len(qtimes) if qtimes else None,
            "persistent_event_local_footprint":persist,
            "t120_timeout_start_count_within_diagnostic_horizon":len(a["starts"]),
            "tneg_timeout_start_count_within_diagnostic_horizon":len(b["starts"]),
        }
        admission &= anchor_ok and tneg_zero and len(pre_bad)==0

    result["admission_pass"]=admission
    if not admission:
        result["verdict"]="HOLD-ALLP-MECHANISM-GEOMETRY-ADMISSION"
    elif all(persistent):
        result["verdict"]="PASS-ALLP-PERSISTENT-REGULARIZATION-FOOTPRINT"
    else:
        result["verdict"]="PARTIAL-PENETRATION-LOCALIZED-REGULARIZATION-FOOTPRINT"
    result["next_authority"]="RAVEL reassessment of threshold sweep versus full-horizon burden sensitivity; no automatic target opening."
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

if __name__=="__main__":
    main()
