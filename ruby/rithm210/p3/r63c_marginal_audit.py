"""R63C-P0: original-source aggregate-only A4 marginal vs dependence diagnostic.

Analyst-only A4 occupancy is allowed solely for diagnostic marginal calibration,
NOT for an uninformed participant's decision. Zero actor-level output.
"""
from collections import defaultdict
from math import log,log1p
from pathlib import Path
import argparse,json
from statistics import mean
from fractions import Fraction
from r63b_legal_bridge import (APPROVED_SHA,load_private_events,fit_model,predict,
     calibrate_shift,sigmoid,group_joint,bootstrap_diff)


def frechet_all_stay_bounds(ps):
    """Sharp all-zero probability bounds given only Bernoulli switch marginals."""
    if not ps or any(not 0<=p<=1 for p in ps):raise ValueError('valid marginals required')
    return max(0.,1.-sum(ps)),1.-max(ps)



def rational_sharp_coupling(ps, *, kind):
    """Exact rational 64-mask witness of each Frechet endpoint; existing math."""
    p=[Fraction(v) for v in ps]
    if len(p)!=6 or any(x<0 or x>1 for x in p) or kind not in ('upper','lower'):
        raise ValueError('six rational Bernoulli marginals and endpoint kind required')
    intervals=[];start=Fraction(0)
    for x in p:
        if kind=='upper':
            spans=[(Fraction(0),x)] if x else []
        else:
            end=start+x
            spans=[(start,min(Fraction(1),end))] if x else []
            if end>1:spans.append((Fraction(0),end-1))
            start=end%1
        intervals.append([(a,b) for a,b in spans if a<b])
    points={Fraction(0),Fraction(1)}
    for spans in intervals:
        for a,b in spans:points.update((a,b))
    grid=sorted(points);masses=defaultdict(Fraction)
    for left,right in zip(grid,grid[1:]):
        middle=(left+right)/2
        key=tuple(int(any(a<=middle<b for a,b in spans)) for spans in intervals)
        masses[key]+=right-left
    if sum(masses.values())!=1:raise AssertionError('joint law does not normalize')
    for j,prob in enumerate(p):
        if sum(v for mask,v in masses.items() if mask[j])!=prob:
            raise AssertionError('marginal coupling mismatch')
    zero=masses[tuple([0]*6)]
    lower,upper=max(Fraction(0),1-sum(p)),1-max(p)
    if zero!=(upper if kind=='upper' else lower):
        raise AssertionError('Frechet endpoint not saturated')
    return {'all_zero':zero,'marginals':tuple(p),'joint_masks':len(masses)}


def apply_oracle_delta(p,delta):
    if not 0<p<1:raise ValueError('open marginal required')
    return sigmoid(log(p/(1-p))+delta)


def score_group(g,p):
    joint,p0=group_joint(g,p)
    zero=int(not any(e['flip'] for e in g))
    return {'joint':joint,'brier0':(p0-zero)**2,'p0':p0,'zero':zero,
            'gross_predict':sum(p),'gross_observed':sum(e['flip'] for e in g)}


def run(events,by_group,*,bootstrap=4000):
    partial_a4=defaultdict(list)
    for key,g in by_group.items():
        if g[0]['treatment']==2 and sum(e['previous_route'] for e in g)==4:
            partial_a4[key[0]].append(g)
    if len(partial_a4)!=17:raise ValueError('expected 17 partial-bearing original sessions')
    all_sessions=sorted({e['session'] for e in events})
    per={'bridge':{},'analyst_A4_marginal_oracle':{}}
    support=[];deltas=[]
    for held in all_sessions:
        if held not in partial_a4:continue
        no=fit_model(events,held,lambda e:e['treatment']==1 and e['info']==0)
        full=fit_model(events,held,lambda e:e['treatment']==3 and e['info']==1)
        def ps(g):return [predict(e,no if not e['info'] else full) for e in g]
        source_groups=[g for sid,gg in partial_a4.items() if sid!=held for g in gg]
        cal=[(p,e['flip']) for g in source_groups for e,p in zip(g,ps(g))]
        delta=calibrate_shift(cal)
        deltas.append(delta)
        vals={model:defaultdict(float) for model in per}
        for g in partial_a4[held]:
            base=ps(g);lo,hi=frechet_all_stay_bounds(base)
            support.append((lo,hi))
            oracle=[apply_oracle_delta(p,delta) for p in base]
            for model,pred in (('bridge',base),('analyst_A4_marginal_oracle',oracle)):
                v=score_group(g,pred)
                for k,x in v.items():vals[model][k]+=x
                vals[model]['n']+=1
        for model in per:
            per[model][held]=dict(vals[model])
    summary={}
    for model,grouped in per.items():
        agg=defaultdict(float)
        for v in grouped.values():
            for k,x in v.items():agg[k]+=x
        n=agg['n'];summary[model]={'old_A4_group_transitions':int(n),
             'joint_U_D_logloss_equal_session':mean(v['joint']/v['n'] for v in grouped.values()),
             'P0_Brier_equal_session':mean(v['brier0']/v['n'] for v in grouped.values()),
             'P0_empirical':agg['zero']/n,'P0_predicted':agg['p0']/n,
             'gross_switches_empirical_per_old_A4':agg['gross_observed']/n,
             'gross_switches_predicted_per_old_A4':agg['gross_predict']/n}
    paired=sorted(per['bridge'])
    contrasts={}
    for key,i in [('P0_Brier','brier0'),('joint_U_D_logloss','joint')]:
        contrasts[key]=bootstrap_diff([
           per['analyst_A4_marginal_oracle'][s][i]/per['analyst_A4_marginal_oracle'][s]['n'] -
           per['bridge'][s][i]/per['bridge'][s]['n'] for s in paired],
           seed=20261131 if i=='joint' else 20261130,reps=bootstrap)
    return {'scope':'AGGREGATE ONLY: same original 24 sessions, 17 Partial-bearing, analyst-only A4 diagnostic, NO causal claim',
            'source_sha256':APPROVED_SHA,'target':{'old_A4_partial_transitions':sum(len(v) for v in partial_a4.values()),
            'target_bearing_sessions':len(partial_a4)},
            'all_zero_sharp_marginal_bounds':{'mean_lower':mean(x[0] for x in support),'mean_upper':mean(x[1] for x in support),
                'explanation':'Sharp Frechet bounds assuming the forecast individual switch marginals are exact; do NOT certify model marginals.'},
            'oracle_shift_summary':{'minimum':min(deltas),'maximum':max(deltas),'mean':mean(deltas),
                'source':'fit on other-session Partial old-A4 actor switches; researcher occupancy NOT actor legal'},
            'models':summary,'oracle_minus_bridge':contrasts}


def main():
    parser=argparse.ArgumentParser(description='Private-source A4 diagnostic -> aggregate-only JSON')
    parser.add_argument('approved_zip');parser.add_argument('aggregate_json')
    a=parser.parse_args()
    events,groups=load_private_events(a.approved_zip)
    out=run(events,groups)
    Path(a.aggregate_json).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':'aggregate_only','old_A4_events':out['target']['old_A4_partial_transitions']}))

if __name__=='__main__':main()
