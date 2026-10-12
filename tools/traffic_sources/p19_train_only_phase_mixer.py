#!/usr/bin/env python3
"""RITHM P19: train-only link-wise mixing of SOURCE 10min traffic counts.
Runs on the presence-aware memmap created by the executed P13 ingestion in the
conversation research ZIP. NOT driver-level observed welfare or road actuation.
Example:
 python tools/traffic_sources/p19_train_only_phase_mixer.py \
   --workspace /path/to/p13_full_workspace --output /tmp/p19_full.json
"""
import argparse
import collections
import datetime
import json
import warnings
from pathlib import Path
import numpy as np

GRID=np.asarray([0., .25, .5, .75, 1.], dtype=np.float32)
D,L,B=365,512,288

def train_only_weight(train):
    """Minimize historical MAE; never see held-out future targets."""
    y=train.reshape(-1)
    lag=np.r_[np.nan,y[:-1]]
    lag2=np.r_[np.nan,np.nan,y[:-2]]
    valid=np.isfinite(y)&np.isfinite(lag)&np.isfinite(lag2)
    if valid.sum()<100:
        return 1.
    target=y[valid];a=lag[valid];b=(lag[valid]+lag2[valid])/2
    error=np.asarray([np.abs(target-(x*a+(1-x)*b)).mean()
                      for x in GRID])
    winners=np.where(np.isclose(error,error.min(),atol=1e-9,rtol=1e-7))[0]
    return float(GRID[winners[-1]])

def score_workspace(workspace: Path):
    census=json.loads((workspace/"p13_full_census.json").read_text("utf-8"))
    if census["source_rows"]!=18420707 or census["source_unique_link_ids"]!=178:
        raise ValueError("Unverified source census; no 2025 score allowed")
    src=np.memmap(workspace/"native.f4",dtype=np.float32,mode="r",
                  shape=(3,D,L,B))
    results=[]; diagnostics=[]
    for month in range(1,13):
        start=(datetime.date(2025,month,1)-datetime.date(2025,1,1)).days
        nsum=0;links=0;loss=collections.defaultdict(float)
        chosen=collections.Counter()
        for link in range(census["source_unique_link_ids"]):
            observed=src[0,:,link,:]
            ev=observed[:,::2];odd=observed[:,1::2]
            ten=np.where(np.isfinite(ev)&np.isfinite(odd)&
                         (ev>=0)&(odd>=0),ev+odd,np.nan)
            training=ten[start:start+21]
            test=ten[start+21:start+28]
            if np.isfinite(training).sum()<1512 or np.isfinite(test).sum()<504:
                continue
            alpha=train_only_weight(training)
            chosen[str(alpha)]+=1
            with warnings.catch_warnings():
                warnings.simplefilter("ignore",RuntimeWarning)
                calendar=np.nanmedian(training.reshape(3,7,144),axis=0)
                fallback=np.nanmedian(training,axis=0)
                overall=np.nanmedian(training)
            calendar=np.where(np.isfinite(calendar),calendar,fallback)
            calendar=np.where(np.isfinite(calendar),calendar,overall)
            test_clock=calendar[(np.arange(21,28)%7)].reshape(-1)
            dates=np.arange((start+21)*144,(start+28)*144)
            flat=ten.reshape(-1)
            y=test.reshape(-1)
            last=flat[dates-1]
            old2=flat[dates-2]
            mean2=(last+old2)/2
            doubled=2*odd.reshape(-1)[dates-1]
            learned=alpha*last+(1-alpha)*mean2
            variants={
                "calendar":test_clock,"last10":last,
                "last20avg":mean2,"twice_last5":doubled,
                "fixed_mix75":.75*last+.25*mean2,
                "fixed_mix50":.5*last+.5*mean2,
                "train_only_adaptive":learned
            }
            keep=np.isfinite(y)
            for pred in variants.values():
                keep &= np.isfinite(pred)
            if not keep.any():
                continue
            links+=1;n=int(keep.sum());nsum+=n
            err={}
            for name,pred in variants.items():
                total=float(np.abs(y[keep]-pred[keep]).sum(dtype=np.float64))
                loss[name]+=total
                err[name]=total/n
            diagnostics.append({"month":month,"source_link_index":link,
                "train_only_alpha":alpha,"matched_10min_bins":n,
                "adaptive_minus_last10_MAE":err["train_only_adaptive"]-err["last10"]})
        if not nsum:
            raise ValueError("No admissible original 10min test source")
        record={"month":month,"matched_10min_bins":nsum,"links":links,
            "source_train_alpha_counts":dict(chosen),
            "MAE_vehicles_per_10min":{k:total/nsum for k,total in loss.items()}}
        results.append(record)
    n=sum(r["matched_10min_bins"] for r in results)
    aggregate={name:sum(r["MAE_vehicles_per_10min"][name]*
                        r["matched_10min_bins"] for r in results)/n
               for name in results[0]["MAE_vehicles_per_10min"]}
    return {"status":"EXPLORATORY_REPEATED_2025_SOURCE",
        "matched_10min_test_bins":n,
        "baseline_source_MAE":aggregate,"monthly":results,
        "link_month_alpha_diagnostics":diagnostics,
        "source_original_cp949_deleted":True,
        "human_group_welfare":"NOT_IDENTIFIED",
        "source_5min_alias_mechanism":"HOLD",
        "info_guidance_causality":"NOT_ESTIMATED",
        "source_clock":"first21 days train, days22..28 test, exact observed 10min previous bins",
        "treatment":"NONE"}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--workspace",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=score_workspace(args.workspace)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),
                           encoding="utf-8")
    print(json.dumps({"n":result["matched_10min_test_bins"],
                      "MAE":result["baseline_source_MAE"]},ensure_ascii=False))
