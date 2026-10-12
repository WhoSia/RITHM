#!/usr/bin/env python3
"""P18 original 2025 Seoul 10-minute SOURCE count forecast. Not human welfare.
Runtime: Python>=3.10, numpy, pandas. Rehash original 38 shards first with
tools/traffic_sources/p15_source_manifest_gate.py. Only counts on complete
same-link adjacent even/odd pairs; source 10min total is phase-invariant.
Usage: python tools/traffic_sources/p18_tenmin_source_forecast.py \
 --shards-dir /path/to/38-csvs \
 --h1-manifest /path/to/H1/manifest.json \
 --h2-manifest /path/to/H2/manifest.json \
 --output /tmp/p18_results.json
"""
import argparse
import csv
import datetime as dt
import json
import pathlib
import numpy as np
import pandas as pd

HEADER=["DATE_CD","ROUTE_ID","ROUTE_NAME","LINK_ID","ROAD_NAME",
        "HH5M_CD","VOL","SPD","OCC"]

def invariant_sum(even, odd, transfer=0):
    """Exactly conserved source 10min count, if both reallocated bins valid."""
    if min(even+transfer, odd-transfer) < 0:
        raise ValueError("negative reassigned source flow")
    return even + odd

def score_month(month, records):
    d=pd.DataFrame.from_records(records,
        columns=["link","day","slot","q","spd"]).astype({
        "link":"int16","day":"int8","slot":"int16",
        "q":"float32","spd":"float32"})
    if d.duplicated(["link","day","slot"]).any():
        raise ValueError("duplicate source 5min key")
    d=d.sort_values(["link","day","slot"])
    key=d.link.astype("int64")*1000000+d.day.astype("int64")*288+d.slot.astype("int64")
    a=key.to_numpy(); slots=d.slot.to_numpy()
    ix=np.where((slots[:-1]%2==0)&(a[1:]==a[:-1]+1))[0]
    ix=ix[(d.link.to_numpy()[ix]==d.link.to_numpy()[ix+1])&
          (d.day.to_numpy()[ix]==d.day.to_numpy()[ix+1])]
    even=d.iloc[ix];odd=d.iloc[ix+1]
    p=pd.DataFrame({"link":even.link.to_numpy(),"day":even.day.to_numpy(),
        "slot10":even.slot.to_numpy()//2,
        "q0":even.q.to_numpy(),"q1":odd.q.to_numpy()})
    p["total"]=p.q0+p.q1
    p["absbin"]=np.array([(dt.date(2025,month,int(day))-dt.date(2025,1,1)).days*144
       for day in p.day],dtype="int32")+p.slot10
    p["dow"]=np.array([dt.date(2025,month,int(day)).weekday()
       for day in p.day],dtype="int8")
    tr=p[p.day<=21];te=p[p.day.between(22,28)].copy()
    ntr=tr.groupby("link").size();nte=te.groupby("link").size()
    eligible=ntr[ntr>=1512].index.intersection(nte[nte>=504].index)
    tr=tr[tr.link.isin(eligible)];te=te[te.link.isin(eligible)].copy()
    med=tr.groupby(["link","dow","slot10"]).total.median()
    te["cal"]=np.asarray(pd.MultiIndex.from_frame(
        te[["link","dow","slot10"]]).map(med),dtype="float64")
    if te.cal.isna().any():
        fallback=tr.groupby(["link","slot10"]).total.median()
        te.cal=te.cal.fillna(pd.Series(np.asarray(
            pd.MultiIndex.from_frame(te[["link","slot10"]]).map(fallback),
            dtype="float64"),index=te.index))
    if te.cal.isna().any():
        te.cal=te.cal.fillna(te.link.map(tr.groupby("link").total.median()))
    p=p[p.link.isin(eligible)].sort_values(["link","absbin"])
    p["lagbin"]=p.groupby("link").absbin.shift(1)
    p["lag2bin"]=p.groupby("link").absbin.shift(2)
    p["last10"]=p.groupby("link").total.shift(1)
    p["lastodd5"]=p.groupby("link").q1.shift(1)
    p["last20avg"]=(p.last10+p.groupby("link").total.shift(2))/2
    p.loc[p.absbin-p.lagbin!=1,["last10","lastodd5","last20avg"]]=np.nan
    p.loc[p.absbin-p.lag2bin!=2,"last20avg"]=np.nan
    past=p[p.day.between(22,28)][
        ["link","absbin","last10","lastodd5","last20avg"]]
    te=te.merge(past,on=["link","absbin"],how="left",validate="one_to_one")
    te["twice_last5"]=2*te.lastodd5
    te=te.dropna(subset=["total","cal","last10","twice_last5","last20avg"])
    candidates=["cal","last10","twice_last5","last20avg"]
    errors={k:float((te.total-te[k]).abs().mean()) for k in candidates}
    return {"month":month,"source_five_min_rows":len(records),
       "complete_10min_pairs":len(ix),"n_month_test":len(te),
       "eligible_links":len(eligible),
       "model_source_10min_count_MAE":errors,
       "last10_better_than_twice_last5":errors["last10"]<errors["twice_last5"]}

def run(shards_dir,h1,h2):
    results=[];records=[];current=None;links={}
    for manifest_file in (h1,h2):
        manifest=json.loads(manifest_file.read_text(encoding="utf-8-sig"))
        if manifest["header"]!=HEADER or manifest["part_count"]!=19:
            raise ValueError("source manifest/header mismatch")
        total=0
        for item in manifest["parts_in_order"]:
            n=0
            with (shards_dir/item["file"]).open(
                "r",encoding="utf-8-sig",newline="") as f:
                reader=csv.reader(f,strict=True)
                if next(reader)!=HEADER:raise ValueError("shard header mismatch")
                for r in reader:
                    if len(r)!=9:raise ValueError("invalid row width")
                    month=int(r[0][4:6])
                    if current is None:current=month
                    if month!=current:
                        if month!=current+1:raise ValueError("source clock gap")
                        results.append(score_month(current,records))
                        records=[];current=month
                    key=(r[1],r[3])
                    if key not in links:links[key]=len(links)
                    tm=r[5]
                    if len(tm)!=4 or not tm.isdigit():raise ValueError("bad clock")
                    hh,mm=int(tm[:2]),int(tm[2:])
                    if not(0<=hh<24 and 0<=mm<60 and mm%5==0):
                        raise ValueError("non-5minute input clock")
                    records.append((links[key],int(r[0][-2:]),
                      hh*12+mm//5,float(r[6]) if r[6] else np.nan,
                      float(r[7]) if r[7] else np.nan))
                    n+=1
            if n!=item["rows"]:raise ValueError("shard row count mismatch")
            total+=n
        if total!=manifest["record_count"]:
            raise ValueError("half-year record count mismatch")
    if records:results.append(score_month(current,records))
    n=sum(x["n_month_test"] for x in results)
    modes=["cal","last10","twice_last5","last20avg"]
    aggregate={m:sum(x["n_month_test"]*
         x["model_source_10min_count_MAE"][m] for x in results)/n
         for m in modes}
    return {"status":"EXPLORATORY source-exposed 2025, not independent physical or human welfare",
       "source_link_route_pairs":len(links),"n_months":len(results),
       "ten_minute_matched_target_rows":n,
       "weighted_MAE_source_vehicles_per_10min":aggregate,
       "monthly":results,
       "operator":"T(q0,q1)=q0+q1, invariant under (+delta,-delta)",
       "information_clock":"train days1..21 per month; test days22..28; lag1 is exact observed prior 10min; teacher-forced",
       "scope_restrictions":["Same-publisher sensor measurement only",
           "No physical source correction, individual travel time or VMS treatment",
           "Original CP949 files were deleted; rehash 38 surviving shards only"]}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--shards-dir",type=pathlib.Path,required=True)
    p.add_argument("--h1-manifest",type=pathlib.Path,required=True)
    p.add_argument("--h2-manifest",type=pathlib.Path,required=True)
    p.add_argument("--output",type=pathlib.Path,required=True)
    a=p.parse_args()
    result=run(a.shards_dir,a.h1_manifest,a.h2_manifest)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(result["weighted_MAE_source_vehicles_per_10min"])
