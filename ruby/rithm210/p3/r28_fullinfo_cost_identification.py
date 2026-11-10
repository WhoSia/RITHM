"""RITHM R28: exact within-treatment identification obstruction.

In the six-person two-route design, own realized route cost c is an EXACT
deterministic function of own route y and publicly disclosed route-A count n:
    c = 12 - 12*y - 2*n + 3*y*n.
Therefore, among Full-information actors with known prior y,n, adding
prior experienced c to a linear model that already includes 1,y,n,y*n
cannot identify an independent coefficient. This is an algebraic property,
not an estimated causal effect. Original-author CSV is private and never
committed. For uninformed arms this *public information* equivalence does
not hold, although the payoff/feedback contract needs separate checking.
"""
from __future__ import annotations
import csv,hashlib
from collections import Counter
from pathlib import Path

SHA="d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb"


def route_cost(route_a:int,number_a:int)->int:
    if type(route_a) is not int or route_a not in (0,1):
        raise ValueError("binary route required")
    if type(number_a) is not int or not 0<=number_a<=6:
        raise ValueError("six-actor occupancy required")
    if (route_a==1 and number_a==0) or (route_a==0 and number_a==6):
        raise ValueError("own chosen route inconsistent with group count")
    return number_a if route_a else 2*(6-number_a)


def algebraic_cost(route_a:int,number_a:int)->int:
    return 12-12*route_a-2*number_a+3*route_a*number_a


def exact_enumeration()->dict:
    states=0
    for y in (0,1):
        for n in range(7):
            if (y==1 and n==0) or (y==0 and n==6):
                continue
            if route_cost(y,n)!=algebraic_cost(y,n):
                raise ArithmeticError("cost identity broken")
            states+=1
    return dict(feasible_person_route_count_states=states,
                dependent_feature="Cost = 12*Intercept - 12*RouteA - 2*NumA + 3*(RouteA*NumA)",
                rank_bound=4,columns=5)


def private_csv_audit(path)->dict:
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("author source byte SHA mismatch")
    counts=Counter();mismatches=Counter()
    with Path(path).open(newline="",encoding="utf-8-sig") as stream:
        for r in csv.DictReader(stream):
            trt=int(r["trt"])
            y=int(r["RouteA"])
            n=int(r["NumA"])
            actual=float(r["Cost"])
            counts[trt]+=1
            if abs(actual-route_cost(y,n))>1e-10:
                mismatches[trt]+=1
    return dict(source_sha256=SHA,actor_rows_by_treatment=dict(sorted(counts.items())),
                cost_identity_violations_by_treatment=dict(sorted(mismatches.items())),
                interpretation="algebraic collinearity in Full only conditional on disclosed count and own past route; no psychological mechanism identified")


if __name__=="__main__":
    import json,sys
    if len(sys.argv)!=2:raise SystemExit("usage: python r28_fullinfo_cost_identification.py ORIGINAL_PRIVATE_CSV")
    print(json.dumps(dict(theorem=exact_enumeration(),source=private_csv_audit(sys.argv[1])),indent=2))
