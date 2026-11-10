"""RITHM interim audit: reproducible, explicitly named Full-treatment cohorts.

The author paper (§4) says 24 experimental sessions; the author R script
'0 data preparation.R' comments that sessions 1 and 2 are pilot sessions,
but its literal Boolean predicate actually excludes only session 1 and
retains session 2; session 101 is excluded only for treatment 1.

Three DIFFERENT populations are therefore retained as separate contracts.
No raw human rows are ever emitted. This module calculates a cohort census,
not a new predictive performance estimate.
"""
from __future__ import annotations
import csv,hashlib,json,sys
from collections import defaultdict
from pathlib import Path

SOURCE_SHA256="d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb"
CONTRACTS=("published_main_24","exclude_pilot2_include101_25",
           "literal_author_R_filter_26")
EXPECTED={"published_main_24":(24,48,1824),
          "exclude_pilot2_include101_25":(25,51,1938),
          "literal_author_R_filter_26":(26,53,2014)}


def included(session:int,treatment:int,period:int,contract:str)->bool:
    if contract not in CONTRACTS:raise ValueError("unknown population contract")
    if type(session) is not int or type(treatment) is not int or type(period) is not int:
        raise ValueError("invalid source key")
    if treatment!=3 or not 1<=period<=40:return False
    if contract=="published_main_24":return session not in (1,2,101)
    if contract=="exclude_pilot2_include101_25":return session not in (1,2)
    # This exactly implements the R script's Boolean session predicate
    # for treatment 3, not its contradicted prose comment.
    return session != 1


def census(path,contract):
    p=Path(path)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=SOURCE_SHA256:
        raise ValueError("original-author source SHA256 mismatch")
    groups=defaultdict(lambda:defaultdict(dict))
    with p.open(newline="",encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            sid=int(row["session"]);trt=int(row["trt"]);t=int(row["Period"])
            if not included(sid,trt,t,contract):continue
            key=(sid,int(row["section"]),int(row["Group"]))
            aid=int(row["ID"])
            if aid in groups[key][t]:raise ValueError("duplicate group-actor-period")
            groups[key][t][aid]=(int(row["RouteA"]),int(row["NumA"]))
    sessions=set()
    for key,periods in groups.items():
        sessions.add(key[0])
        if set(periods)!=set(range(1,41)):raise ValueError("incomplete group")
        persons=set(periods[1])
        if len(persons)!=6:raise ValueError("not six people")
        for t,people in periods.items():
            if set(people)!=persons:raise ValueError("actor set drift")
            route=[x[0] for x in people.values()]
            if any(x not in (0,1) for x in route):raise ValueError("nonbinary route")
            n=sum(route)
            if any(x[1]!=n for x in people.values()):raise ValueError("NumA mismatch")
    totals=(len(sessions),len(groups),38*len(groups))
    if totals!=EXPECTED[contract]:raise ValueError(f"unexpected cohort census {totals}")
    return dict(contract=contract,sessions=totals[0],groups=totals[1],
                scored_group_periods=totals[2],source_sha256=SOURCE_SHA256,
                label="cohort census only; no model fitting or inference")


if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python r27_audit_population_contracts.py ORIGINAL_PRIVATE_CSV")
    print(json.dumps([census(sys.argv[1],contract) for contract in CONTRACTS],indent=2))
