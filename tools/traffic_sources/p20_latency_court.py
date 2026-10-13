#!/usr/bin/env python3
"""RITHM-2.6 P20: 2025 SOURCE ten-minute delay-scenario forecast.
Public-release latency is NOT observed; these are hypothetical delayed filtrations.
Requires numpy/pandas; SHA-checks surviving 38 owner shards. No source raw redistribution.
"""
import argparse
import hashlib
import json
import datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd

COLUMNS=["DATE_CD","ROUTE_ID","ROUTE_NAME","LINK_ID","ROAD_NAME","HH5M_CD","VOL","SPD","OCC"]
DELAYS=(0,5,10,15,20,30,40,50,60)
def required_lag(minutes):
    if not isinstance(minutes,int) or minutes<0:
        raise ValueError("delay must be nonnegative whole minutes")
    return 1+(minutes+9)//10

def sha(path):
    digest=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(8*1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()

def load_source(shards_dir,h1,h2,workspace):
    paths={p.name:p for p in shards_dir.rglob("*__part_*.csv")}
    if len(paths)!=38:raise ValueError("38 unique original shard names required")
    expected={}
    for path in (h1,h2):
        m=json.loads(path.read_text(encoding="utf-8-sig"))
        if m["header"]!=COLUMNS or m["part_count"]!=19:raise ValueError("manifest mismatch")
        expected.update({x["file"]:x for x in m["parts_in_order"]})
    if set(expected)!=set(paths):raise ValueError("unmatched shard families")
    if sum(x["rows"] for x in expected.values())!=18420707:raise ValueError("wrong original row census")
    for name,e in expected.items():
        f=paths[name]
        if f.stat().st_size!=e["bytes"] or sha(f)!=e["sha256"]:
            raise ValueError("unverified original shard "+name)
    ordered=sorted(paths.values(),key=lambda p:("하반기" in p.name,p.name))
    probe=pd.read_csv(ordered[0],encoding="utf-8-sig",usecols=["ROUTE_ID","LINK_ID"],dtype=str)
    ids=sorted(map(tuple,probe[["ROUTE_ID","LINK_ID"]].drop_duplicates().to_numpy()))
    if len(ids)!=178:raise ValueError("source link identity census changed")
    lookup={k:i for i,k in enumerate(ids)}
    workspace.mkdir(parents=True,exist_ok=True)
    q=np.memmap(workspace/"source_q5_2025.f4",mode="w+",dtype="float32",shape=(365,178,288))
    q[:]=np.nan
    present=np.zeros((365,178,288),dtype=np.bool_)
    rows=0;na=0
    for path in ordered:
        n=0
        for part in pd.read_csv(path,encoding="utf-8-sig",chunksize=170000,
            usecols=["DATE_CD","ROUTE_ID","LINK_ID","HH5M_CD","VOL"],
            dtype={"DATE_CD":"int32","ROUTE_ID":"string","LINK_ID":"string",
                   "HH5M_CD":"int16","VOL":"float32"}):
            n+=len(part)
            dates=pd.to_datetime(part.DATE_CD.astype(str),format="%Y%m%d")
            if not (dates.dt.year==2025).all():raise ValueError("out-of-year source")
            day=dates.dt.dayofyear.to_numpy()-1
            hhmm=part.HH5M_CD.to_numpy();hh=hhmm//100;mi=hhmm%100
            if not ((hh>=0)&(hh<24)&(mi<60)&(mi%5==0)).all():
                raise ValueError("invalid five-minute clock")
            slot=hh*12+mi//5
            link=np.fromiter((lookup.get((a,b),-1) for a,b in zip(part.ROUTE_ID,part.LINK_ID)),
                             dtype=np.int32,count=len(part))
            if (link<0).any():raise ValueError("unregistered source link")
            key=(day.astype("int64")*178+link)*288+slot
            if len(np.unique(key))!=len(key) or present[day,link,slot].any():
                raise ValueError("duplicate real source timestamp")
            present[day,link,slot]=True
            counts=part.VOL.to_numpy()
            if not (np.isnan(counts)|(np.isfinite(counts)&(counts>=0))).all():
                raise ValueError("invalid original source volume")
            q[day,link,slot]=counts
            na+=int(np.isnan(counts).sum())
            rows+=len(part)
        if n!=expected[path.name]["rows"]:raise ValueError("per-shard row count mismatch")
    if rows!=18420707 or na!=152:raise ValueError("real 2025 source changed")
    q.flush()
    return q,{"source_rows":rows,"missing_volume_cells":na,"verified_shards":38,
       "directed_links":len(ids),"source_days":int(present.any(axis=(1,2)).sum()),
       "source_not_same_as_independent_physical_flow":True}

def run_forecast(q):
    counts=np.where(np.isfinite(q[:,:,::2])&np.isfinite(q[:,:,1::2]),
                    q[:,:,::2]+q[:,:,1::2],np.nan).transpose(1,0,2).reshape(178,-1)
    months=[]
    maxlag=max(required_lag(d) for d in DELAYS)
    for month in range(1,13):
        start=(dt.date(2025,month,1)-dt.date(2025,1,1)).days
        totals={}
        n=0;links=0
        for li in range(178):
            row=counts[li]
            training=row[start*144:(start+21)*144].reshape(21,144)
            target=row[(start+21)*144:(start+28)*144]
            if np.isfinite(training).sum()<1512 or np.isfinite(target).sum()<504:
                continue
            with np.errstate(all="ignore"):
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore",RuntimeWarning)
                    cal=np.nanmedian(training.reshape(3,7,144),axis=0)
                    fallback=np.nanmedian(training,axis=0)
                    overall=np.nanmedian(training)
            cal=np.where(np.isfinite(cal),cal,fallback)
            cal=np.where(np.isfinite(cal),cal,overall).reshape(-1)
            indexes=np.arange((start+21)*144,(start+28)*144)
            valid=np.isfinite(target)&np.isfinite(cal)
            prediction={"calendar":cal}
            for lag in range(1,maxlag+1):
                recent=row[indexes-lag]
                older=row[indexes-lag-1]
                prediction[f"lag{lag}"]=recent
                prediction[f"mix75_lag{lag}"]=0.75*recent+0.125*(recent+older)
                valid &= np.isfinite(recent)&np.isfinite(older)
            if not valid.any():continue
            links+=1
            n+=int(valid.sum())
            for name,pred in prediction.items():
                totals[name]=totals.get(name,0)+float(
                    np.abs(target[valid]-pred[valid]).sum(dtype=np.float64))
        if not n:raise ValueError("no source-true heldout cohort")
        months.append({"month":month,"n":n,"links":links,
                       "mae":{k:v/n for k,v in totals.items()}})
    N=sum(m["n"] for m in months)
    aggregate={name:sum(m["mae"][name]*m["n"] for m in months)/N
               for name in months[0]["mae"]}
    return {"status":"P20_2025_EXPOSED_SOURCE_LATENCY_SCENARIOS",
        "n_same_future_targets":N,"link_ids":178,"training":"first 21 days/month",
        "heldout":"days22..28, exact 10min complete pairs",
        "delay_is_observed":False,"delay_scenarios":{str(d):required_lag(d) for d in DELAYS},
        "source_mae_vehicle_per_10min":aggregate,"monthly":months,
        "original_cp949_files_deleted":True,"human_welfare":"NOT_IDENTIFIED",
        "independent_physical_sensor":"NOT_CERTIFIED",
        "real_time_deployability":"NOT_CERTIFIED",
        "guidance_causal_effect":"NOT_IDENTIFIED",
        "inference":"Repeatedly examined 2025 source; descriptive only"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--shards-dir",type=Path,required=True)
    p.add_argument("--h1-manifest",type=Path,required=True)
    p.add_argument("--h2-manifest",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    q,c=load_source(a.shards_dir,a.h1_manifest,a.h2_manifest,a.output_dir)
    result=run_forecast(q)
    result["source_census"]=c
    (a.output_dir/"p20_source_delay_results.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(result["n_same_future_targets"])
