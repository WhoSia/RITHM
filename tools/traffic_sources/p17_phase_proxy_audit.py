#!/usr/bin/env python3
"""Rehash & audit P17 six 2025 Seoul days; exact conditional proxy envelopes.

No original 2025 data embedded here. Four original H1 source shards 005, 009,
011, 012 are required; *never* infer missing 5-minute counts as zero.
Usage:
 PYTHONPATH=src python tools/traffic_sources/p17_phase_proxy_audit.py \
 --input /seoul-shards --output /tmp/p17_phase.json
"""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from rithm.phase_externality import Pair,phase_envelope,balanced_reallocation_proxy

EXPECTED={
"005":("e38583144a80e6bdca6a82e8dda71cc1a7934c511fffcdc7d5e1538ab8c5012a",506040),
"009":("2c038c023661077ce40eb1b155f152f1f9af4c7f0cca576fdf2a562488c142f4",506747),
"011":("310ca5d177fae9950a48c0de1913ae62197853f480086039e1baaf03c5759226",506939),
"012":("c16deb323367c225f35fecf5dce7421d0a0a2a6ad59a30a2c0378618e2f2c224",508189)
}
DAYS=["20250212","20250323","20250416","20250418","20250419","20250421"]
HEADER=["DATE_CD","ROUTE_ID","ROUTE_NAME","LINK_ID","ROAD_NAME",
        "HH5M_CD","VOL","SPD","OCC"]


def audit(directory):
    days=set(DAYS)
    source=defaultdict(dict)
    authenticated={}
    for part,(sha,expected_rows) in EXPECTED.items():
        matches=list(Path(directory).glob(f"*상반기__part_{part}.csv"))
        if len(matches)!=1:
            raise ValueError(f"one original source part {part} required")
        f=matches[0]
        h=hashlib.sha256()
        with f.open("rb") as stream:
            for chunk in iter(lambda:stream.read(8*1024*1024),b""):
                h.update(chunk)
        if h.hexdigest()!=sha:
            raise ValueError(f"source SHA mismatch: {f}")
        n=0
        matched=0
        with f.open("r",encoding="utf-8-sig",newline="") as stream:
            rd=csv.DictReader(stream)
            if rd.fieldnames!=HEADER:
                raise ValueError("unexpected original Seoul source schema")
            for x in rd:
                n+=1
                date=x["DATE_CD"]
                if date not in days:
                    continue
                matched+=1
                clock=x["HH5M_CD"].zfill(4)
                if (len(clock)!=4 or not clock.isdigit() or
                    int(clock[:2])>=24 or int(clock[2:])>=60 or
                    int(clock[2:])%5):
                    raise ValueError("invalid 5-minute clock")
                slot=int(clock[:2])*12+int(clock[2:])//5
                identity=(date,x["ROUTE_ID"],x["LINK_ID"])
                if slot in source[identity]:
                    raise ValueError("duplicate source link-date-clock")
                q=int(x["VOL"]) if x["VOL"].strip() else None
                s=float(x["SPD"]) if x["SPD"].strip() else None
                if q is not None and q<0:
                    raise ValueError("negative source count")
                source[identity][slot]=(q,s)
        if n!=expected_rows:
            raise ValueError(f"source row mismatch for {part}")
        authenticated[part]={"sha256":sha,"rows":n,"target_day_rows":matched}

    results={}
    for date in DAYS:
        pairs=[]
        tenminute=defaultdict(list)
        original_count_pairs=original_counts=bad_speed=0
        for (d,route,link), slots in source.items():
            if d!=date:
                continue
            for k in range(144):
                if 2*k not in slots or 2*k+1 not in slots:
                    continue
                (a,s0)=slots[2*k]
                (b,s1)=slots[2*k+1]
                if a is None or b is None:
                    continue
                original_count_pairs+=1
                original_counts+=a+b
                tenminute[k].append(a+b)
                if s0 is None or s1 is None or s0<=0 or s1<=0:
                    bad_speed+=1
                    continue
                pairs.append(Pair(a,b,s0,s1))
        if not pairs:
            raise ValueError(f"no valid source count+speed pairs for {date}")
        balanced=balanced_reallocation_proxy(pairs)
        B=balanced["minimum_nearflat_integer_reassignments"]
        bounds=phase_envelope(pairs,global_budget=B)
        cv2=[]
        eligible_link_counts=[]
        for bin_index, values in sorted(tenminute.items()):
            if len(values)<2 or sum(values)==0:
                continue
            mu=sum(values)/len(values)
            cv2.append(sum((q-mu)**2 for q in values)/len(values)/(mu*mu))
            eligible_link_counts.append(len(values))
        results[date]={
            "source_matched_count_pairs":original_count_pairs,
            "source_matched_section_passages":original_counts,
            "proxy_eligible_pairs":len(pairs),
            "excluded_incompatible_speed":bad_speed,
            "balanced_integer_witness":balanced,
            "sharp_global_budget_proxy":bounds,
            "nearflat_proxy_change_pct":
              100*(balanced["nearflat_proxy"]/balanced["source_proxy"]-1),
            "tenminute_phase_invariant_mean_spatial_cv2":sum(cv2)/len(cv2),
            "tenminute_bins":len(cv2),
            "mean_source_links_per_tenminute":sum(eligible_link_counts)/len(eligible_link_counts),
            "not_human_welfare":True
        }
    return {"source":"2025 Seoul urban-expressway original four H1 shards",
            "source_shards":authenticated,"source_days":results,
            "original_deleted_CP949_not_rehashed":True,
            "source_speed_held_fixed_scenario":True,
            "physical_cause_identified":False,
            "human_travel_time_welfare_identified":False}


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    result=audit(a.input)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    for d,v in result["source_days"].items():
        env=v["sharp_global_budget_proxy"]
        base=env["source_proxy"]
        print(d,v["proxy_eligible_pairs"],
              round(100*(env["min_proxy"]/base-1),3),
              round(100*(env["max_proxy"]/base-1),3))
