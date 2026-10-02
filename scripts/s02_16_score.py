#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

LABELS=["000","030","070","100"]
E2_B={"000":6744.900342630178,"030":6552.030105626119,"070":6531.009995198813,"100":6528.603536510846}
E2_R={"000":0.0,"030":-0.02859497208358297,"070":-0.03171141700634206,"100":-0.032068198955032545}
E2_C=0.028238190134892482
EPS=.005

def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

root=Path("s02-16-results")
statuses={}
complete=True
for label in LABELS:
    d=root/f"p{label}"
    sp=d/"status.json"; fp=d/"framecomplete.tsv"; tp=d/f"most.s02-16-p{label}-tripinfo.xml"
    if not (sp.exists() and fp.exists() and tp.exists()):
        statuses[label]={"scientific_cell_receipt_valid":False,"reason":"missing-status-or-artifact"}
        complete=False
        continue
    s=json.loads(sp.read_text())
    statuses[label]=s
    if not s.get("scientific_cell_receipt_valid"): complete=False
    if sum(1 for _ in fp.open())-1 != 45822: complete=False

admission={
    "stage":"RITHM-ORIGIN-S02.16",
    "all_four_fresh_tneg_cells_valid":complete,
    "target_aggregation_permitted":complete,
    "statuses":statuses,
    "canonical_t120_reused":True,
    "checkpoint_stitching_used":False,
    "e3_or_e4_partial_output_reuse":False,
}
(root/"s02-16-admission.json").write_text(json.dumps(admission,indent=2,sort_keys=True)+"\n")

if not complete:
    final={
        "stage":"RITHM-ORIGIN-S02.16","scientific_target_observed":False,
        "B_NEG":None,"R_B_NEG":None,"C_B_NEG":None,"delta_C":None,
        "verdict":"HOLD-EXECUTION / TNEG-NONMATERIALIZED",
        "canonical_t120_reused":True,"admission":admission
    }
else:
    B={}; counts={}
    for label in LABELS:
        fp=root/f"p{label}"/"framecomplete.tsv"
        total=0.; n=mat=absent=0
        with fp.open(newline="") as f:
            for row in csv.DictReader(f,delimiter="\t"):
                total+=float(row["burden"]); n+=1
                if row["status"]=="materialized": mat+=1
                elif row["status"]=="absent": absent+=1
        assert n==45822
        B[label]=total/n
        counts[label]={"frame_n":n,"materialized_n":mat,"absent_n":absent}
    B0=B["000"]; assert B0>0
    R={k:B[k]/B0-1 for k in LABELS}
    C=(R["100"]-R["070"])-(R["030"]-R["000"])
    dB={k:B[k]-E2_B[k] for k in LABELS}
    dR={k:R[k]-E2_R[k] for k in LABELS}
    dC=C-E2_C
    if C>EPS:
        tneg="PASS-TNEG-CURVATURE"; closure="PASS-TELEPORT-ROBUST"
    elif C<-EPS:
        tneg="DEFEAT-TNEG-CURVATURE"; closure="REGULARIZATION-SENSITIVE"
    else:
        tneg="UNRESOLVED-TNEG-CURVATURE"; closure="REGULARIZATION-SENSITIVE"
    final={
        "stage":"RITHM-ORIGIN-S02.16","scientific_target_observed":True,
        "B_NEG":B,"R_B_NEG":R,"C_B_NEG":C,"epsilon":EPS,
        "B_T120":E2_B,"R_B_T120":E2_R,"C_B_T120":E2_C,
        "delta_B_NEG_minus_T120":dB,"delta_R_NEG_minus_T120":dR,"delta_C":dC,
        "counts":counts,"tneg_verdict":tneg,"closure":closure,
        "canonical_t120_reused":True,"checkpoint_stitching_used":False,
        "e3_or_e4_partial_output_reuse":False,"no_post_reveal_retuning":True,
        "admission":admission
    }
(root/"s02-16-final.json").write_text(json.dumps(final,indent=2,sort_keys=True)+"\n")
print(json.dumps(final,indent=2,sort_keys=True))
