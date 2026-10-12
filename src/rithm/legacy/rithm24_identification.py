#!/usr/bin/env python3
"""RITHM-2.4 synthetic identification and collective-welfare contracts.
Scientific status: exact mathematical counterexamples, NOT human confirmation.
"""
from fractions import Fraction
from itertools import product
from math import comb

def traffic_cost(n1, n2, z):
    if min(n1,n2)<0 or n1+n2>12 or z not in (0,1):
        raise ValueError("invalid congestion/shock state")
    n3=12-n1-n2
    directly=n1*(10+n1+n2)+n2*(13+n2+19*z)+n3*(22-n1)
    formula=264-24*n1-9*n2+2*n1*n1+2*n1*n2+n2*n2+19*z*n2
    assert directly==formula
    return formula

def exact_rank(rows):
    if not rows:return 0
    a=[[Fraction(v) for v in row] for row in rows]
    width=len(a[0])
    assert all(len(row)==width for row in a)
    pivot=0
    for j in range(width):
        first=next((r for r in range(pivot,len(a)) if a[r][j]),None)
        if first is None:continue
        a[pivot],a[first]=a[first],a[pivot]
        d=a[pivot][j]
        a[pivot]=[v/d for v in a[pivot]]
        for k in range(len(a)):
            if k!=pivot and a[k][j]:
                d=a[k][j]
                a[k]=[v-d*w for v,w in zip(a[k],a[pivot])]
        pivot+=1
        if pivot==len(a):break
    return pivot

def identification_rank():
    natural=[]
    private_feedback=[]
    for n2,z in product((0,2,5,8,12),(0,1)):
        c=13+n2+19*z
        natural.append([1,n2,z,c])
        for bonus in (0,1):
            private_feedback.append([1,n2,z,c+bonus])
    result={"natural_rank":exact_rank(natural),"natural_n_features":4,
            "random_private_feedback_rank":exact_rank(private_feedback),
            "random_private_feedback_n_features":4}
    assert (result["natural_rank"],result["random_private_feedback_rank"])==(3,4)
    return result

def execution_equivalence():
    # Toy binary symmetric implementation failure model.
    scenarios=[(Fraction(7,10),Fraction(1,1)),
               (Fraction(3,4),Fraction(9,10)),
               (Fraction(9,10),Fraction(3,4))]
    outcomes=[p*e+(1-p)*(1-e) for p,e in scenarios]
    assert all(q==Fraction(7,10) for q in outcomes)
    return {"distinct_intention_fidelity_pairs":[[str(p),str(e)] for p,e in scenarios],
            "identical_final_route1_probability":"7/10"}

def joint_cost_counterexample():
    # Same p_i=1/2 and mean n1=6 in all three non-overlapping laws.
    dist={
      "balanced":{6:Fraction(1)},
      "independent":{k:Fraction(comb(12,k),4096) for k in range(13)},
      "synchronized":{0:Fraction(1,2),12:Fraction(1,2)}
    }
    result={}
    for name,law in dist.items():
        mean=sum(k*p for k,p in law.items())
        var=sum((k-mean)**2*p for k,p in law.items())
        expected=sum(traffic_cost(k,0,0)*p for k,p in law.items())
        assert mean==6 and expected==192+2*var
        result[name]={"mean":str(mean),"variance":str(var),"expected_cost":str(expected)}
    return result

def opening_contract():
    return {"rank":identification_rank(),
      "execution_observational_equivalence":execution_equivalence(),
      "identical_person_marginals_divergent_group_cost":joint_cost_counterexample(),
      "study_status":"DESIGN_ONLY — no new independent human observation",
      "falsifiers":[
        "if human intention before advice is not measured, execution-friction causal interpretation HOLD",
        "if private payoff and public traffic information are not orthogonal, pure reward-learning HOLD",
        "if the experiment has no independently randomized interacting groups, adaptive-guidance collective welfare causal effect HOLD",
        "if current accident is unknown before the upstream fork, using it in the upstream predictor is look-ahead leakage",
        "if information changes the two-stage user interface, information-only treatment causality HOLD",
        "if persistence after policy withdrawal is unmeasured, long-run hysteresis HOLD"]}
if __name__=="__main__":
    import json
    print(json.dumps(opening_contract(),indent=2,ensure_ascii=False))
