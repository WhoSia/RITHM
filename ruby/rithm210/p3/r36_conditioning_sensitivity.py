"""R36: source-verified conditioning-sensitivity falsification.
No original actor rows or travel values are emitted; private CSV is local-only.
This utility does not turn a post hoc negative-control p-value into causality.
"""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np

SHA="d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb"

def load_rows(path):
    p=Path(path)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=SHA:
        raise ValueError("unverified original source")
    registry={}
    with p.open(encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f):
            sid=int(row["session"]);t=int(row["Period"])
            if sid in (2,101) or int(row["trt"])!=2:continue
            k=(sid,int(row["section"]),int(row["Group"]),int(row["ID"]),t)
            if k in registry:raise ValueError("duplicate person-time")
            registry[k]=(int(row["RouteA"]),int(row["Informed"]),float(row["Value"]))
    out=[]
    for (sid,sec,g,actor,t),(route,inf,v) in registry.items():
        if t<2 or t>39:continue
        prev=registry.get((sid,sec,g,actor,t-1))
        nxt=registry.get((sid,sec,g,actor,t+1))
        if prev is None or nxt is None:raise ValueError("missing past/future choice")
        if route not in (0,1) or inf not in (0,1) or not 6<=v<=16:raise ValueError("invalid source")
        out.append(dict(session=sid,section=sec,group=g,actor=actor,t=t,
                        route=route,prior_route=prev[0],info=inf,value=v,
                        already_decided=int(route!=prev[0]),next_switch=int(route!=nxt[0])))
    if len(out)!=24*48//24*6*38:raise ValueError("unexpected source census")
    return out

def partition(rows,kind):
    if kind not in ("current","prior","both","informed","route_only"):
        raise ValueError("unknown registered sensitivity")
    groups=defaultdict(list)
    for z in rows:
        k=(z["session"],z["section"],z["group"],z["t"])
        k+= {"current":(z["route"],z["info"]),
             "prior":(z["prior_route"],z["info"]),
             "both":(z["route"],z["prior_route"],z["info"]),
             "informed":(z["info"],),
             "route_only":(z["route"],)}[kind]
        groups[k].append(z)
    return {key:val for key,val in groups.items() if len(val)>=2}

def statistic(cells,outcome):
    num=den=0.;n=0
    for vals in cells.values():
        x=np.array([z["value"] for z in vals],dtype=float)
        y=np.array([z[outcome] for z in vals],dtype=float)
        x-=x.mean();y-=y.mean()
        num+=float(x@y);den+=float(x@x);n+=len(vals)
    if den<=0:raise ValueError("no within-cell randomized value variance")
    return num/den,n

def permutation_p(cells,outcome,observed,reps=999,seed=20261111):
    rng=np.random.default_rng(seed)
    numer=np.zeros(reps);denom=0.
    for vals in cells.values():
        x=np.array([z["value"] for z in vals],float)
        y=np.array([z[outcome] for z in vals],float)
        x-=x.mean();y-=y.mean();denom+=float(x@x)
        pick=np.argsort(rng.random((reps,len(x))),axis=1)
        numer+=x[pick]@y
    return float((1+np.count_nonzero(abs(numer/denom)>=abs(observed)))/(1+reps))

def audit(path):
    rows=load_rows(path)
    result={}
    for method in ("current","prior","both","informed","route_only"):
        cells=partition(rows,method)
        records={}
        for outcome in ("next_switch","already_decided"):
            b,n=statistic(cells,outcome)
            records[outcome]={"slope":b,"n":n,"cells":len(cells),
                              "p_999":permutation_p(cells,outcome,b)}
        result[method]=records
    return {"study":"R36 post hoc sensitivity of R35 predecision placebo",
            "source_sha256":SHA,"periods":"2..39",
            "methods":result,
            "warning":"When both prior and current route are fixed, already_decided is a constant by definition. p=1 is NOT placebo validation; populations differ between methods. Causal HOLD."}

if __name__=="__main__":
    import sys
    if len(sys.argv)!=2:raise SystemExit("usage: python r36_conditioning_sensitivity.py PRIVATE_SOURCE.csv")
    print(json.dumps(audit(sys.argv[1]),indent=2))
