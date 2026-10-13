#!/usr/bin/env python3
"""RITHM P21: 14d train / 7d choose / 7d source-exposed delayed forecast.
Import P20's SHA-verified original 38-shard loader; no raw in Git.
The full tested standalone instrument and detailed link-month cases are in P21 ZIP.
"""
import argparse, datetime as dt, json, warnings
from pathlib import Path
import numpy as np
from p20_latency_court import load_source

LAGS=(1,2,3,4,5,6,7)
DELAY={0:1,5:2,10:2,15:3,20:3,30:4,40:5,50:6,60:7}

def seasonal(train):
    if train.ndim!=2 or train.shape[1]!=144 or len(train)%7:
        raise ValueError("Training must be full seven-day weeks of 10-minute source counts")
    weeks=len(train)//7
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",RuntimeWarning)
        clock=np.nanmedian(train.reshape(weeks,7,144),axis=0)
        fallback=np.nanmedian(train,axis=0)
        overall=np.nanmedian(train)
    return np.where(np.isfinite(clock),clock,
        np.where(np.isfinite(fallback),fallback,overall)).reshape(-1)

def mix(row, indices, lag):
    return .875*row[indices-lag]+.125*row[indices-lag-1]

def run(q):
    if q.shape!=(365,178,288):
        raise ValueError("P20 canonical real 2025 source tensor required")
    a=q[:,:,::2];b=q[:,:,1::2]
    pair=np.where(np.isfinite(a)&np.isfinite(b),a+b,np.nan)
    data=pair.transpose(1,0,2).reshape(178,365*144)
    months=[]
    for month in range(1,13):
        start=(dt.date(2025,month,1)-dt.date(2025,1,1)).days*144
        score={lag:{k:0. for k in ("calendar","mix","network_switch","link_switch","test_oracle_ILLEGAL")} for lag in LAGS}
        cache={l:[] for l in LAGS}
        valid_total=0;val_totals={l:[0.,0.,0] for l in LAGS}
        for li in range(178):
            row=data[li]
            train14=row[start:start+14*144].reshape(14,144)
            train21=row[start:start+21*144].reshape(21,144)
            val_idx=np.arange(start+14*144,start+21*144)
            test_idx=np.arange(start+21*144,start+28*144)
            if np.isfinite(train21).sum()<1512 or np.isfinite(row[test_idx]).sum()<504:
                continue
            cv=seasonal(train14);ct=seasonal(train21)
            y=row[test_idx];take=np.isfinite(y)&np.isfinite(ct)
            for age in range(1,9):
                take &= np.isfinite(row[test_idx-age])
            if not take.any():
                continue
            n=int(take.sum());valid_total+=n
            cal_e=float(np.abs(y[take]-ct[take]).sum(dtype=np.float64))
            vy=row[val_idx]
            for lag in LAGS:
                mix_e=float(np.abs(y[take]-mix(row,test_idx,lag)[take]).sum(dtype=np.float64))
                vmask=np.isfinite(vy)&np.isfinite(cv)
                vmask &= np.isfinite(row[val_idx-lag])&np.isfinite(row[val_idx-lag-1])
                if vmask.sum()>=504:
                    val_c=float(np.abs(vy[vmask]-cv[vmask]).sum(dtype=np.float64))
                    val_m=float(np.abs(vy[vmask]-mix(row,val_idx,lag)[vmask]).sum(dtype=np.float64))
                    choose=val_m<val_c
                    val_totals[lag][0]+=val_c
                    val_totals[lag][1]+=val_m
                    val_totals[lag][2]+=int(vmask.sum())
                else: choose=False
                cache[lag].append((cal_e,mix_e,choose))
        if not valid_total:raise ValueError("No admissible month-level source cohort")
        switched={}
        for lag in LAGS:
            network_choose=(val_totals[lag][2]>0 and val_totals[lag][1]<val_totals[lag][0])
            switched[str(lag)]={"network_choose_mix":network_choose,
                "links_choose_mix":sum(t[2] for t in cache[lag])}
            for c,m,selected in cache[lag]:
                score[lag]["calendar"]+=c
                score[lag]["mix"]+=m
                score[lag]["network_switch"]+=m if network_choose else c
                score[lag]["link_switch"]+=m if selected else c
                score[lag]["test_oracle_ILLEGAL"]+=min(c,m)
            for k in score[lag]:
                score[lag][k]/=valid_total
        months.append({"month":month,"n":valid_total,
            "lags":{str(k):v for k,v in score.items()},"switches":switched})
    N=sum(m["n"] for m in months)
    if N!=2121699:raise ValueError("Matched P20 source mask changed")
    result={str(lag):{k:sum(m["n"]*m["lags"][str(lag)][k] for m in months)/N
        for k in months[0]["lags"][str(lag)]} for lag in LAGS}
    return {"status":"EXPOSED_2025_SOURCE_NOT_REAL_PROVIDER_DELAY",
        "matched_source_bins":N,"source_study_days":"1..14 fit, 15..21 choose, 22..28 evaluate",
        "assumed_delay_to_required_lag":{str(k):v for k,v in DELAY.items()},
        "actual_release_delay_measured":False,
        "independent_sensor_and_human_welfare":False,
        "source_MAE_vehicles_per_10min":result,"months":months}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--shards-dir",required=True,type=Path)
    p.add_argument("--h1-manifest",required=True,type=Path)
    p.add_argument("--h2-manifest",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    source,census=load_source(a.shards_dir,a.h1_manifest,a.h2_manifest,a.output_dir)
    result=run(source);result["source_census"]=census
    (a.output_dir/"p21_link_switch_2025.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("matched source bins",result["matched_source_bins"])
