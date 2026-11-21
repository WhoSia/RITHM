"""RITHM R62: predecision legal own-payoff and route-tenure diagnostics.

Uninformed actors NEVER receive observed group occupancy or other actors'
rewards; source-stored profit from *own* prior t−1 play only. The source
private rows are never exported. Distinct from analyst-only A4 oracle.
"""
from collections import defaultdict
from io import StringIO
from pathlib import Path
from hashlib import sha256
import csv,zipfile
import numpy as np
from statistics import mean
from r54_original_batch_clock import APPROVED_ZIP_SHA256
from r61_adaptive_prior import summarize_session_bases,base_without,get_pbase,adaptive_probability,get_predictions
from r62_batch import prepare,batch_law
from r62_statecal import fit_logit_shift,sigmoid
from r62_collective import aggregate

MODELS=('payoff_3','tenure_3','payoff_tenure_9')


def attach_legal_features(events,source):
    if sha256(Path(source).read_bytes()).hexdigest()!=APPROVED_ZIP_SHA256:
        raise ValueError('approved source SHA required')
    seen={}
    with zipfile.ZipFile(source) as z:
        for row in csv.DictReader(StringIO(z.read('data_task_all_switch_230705.csv').decode('utf-8-sig'))):
            s,sec,period=map(int,(row['session'],row['section'],row['Period']))
            if s in (2,101) or sec not in (3,4) or period not in range(1,41):continue
            key=(s,sec,int(row['Group']),int(row['ID']),period)
            if key in seen:raise ValueError('duplicate source personal clock')
            seen[key]=(int(row['RouteA']),float(row['profit']),int(row['Informed']),int(row['trt']))
    if len(seen)!=96*40*6:raise ValueError('wrong original target cohort')
    enriched=[]
    for e in events:
        x=dict(e)
        s,sec,g,i,t=e['session'],e['section'],e['group'],e['actor'],e['period']
        previous=seen[s,sec,g,i,t-1]
        if previous[0]!=e['previous_route'] or previous[2]!=e['info'] or previous[3]!=e['treatment']:
            raise AssertionError('inconsistent legal own payoff/time/mask')
        streak=1
        for k in range(t-2,0,-1):
            if seen[s,sec,g,i,k][0]==previous[0]:streak+=1
            else:break
        x['lagged_own_payoff']=previous[1]
        x['legal_route_streak']=streak
        enriched.append(x)
    if len(enriched)!=len(events):raise ValueError('actor decision mismatch')
    return enriched


def stratum(e,model):
    if model not in MODELS:raise ValueError('unknown legal competitor')
    z=e['lagged_own_payoff']
    profit=0 if z<4 else (1 if z<8 else 2)
    st=e['legal_route_streak']
    tenure=0 if st==1 else (1 if st<=3 else 2)
    if model=='payoff_3':return profit
    if model=='tenure_3':return tenure
    return profit*3+tenure


def score_legal(events,*,base_mode='current_only',bootstrap=2000,seed=20261121):
    """Whole-session outer holdout; legal personal feedback only and predecision."""
    if base_mode not in ('current_only','nested_adaptive'):raise ValueError('bad base mode')
    D=prepare(events)
    y=np.array([[e['flip'] for e in group] for _,group,_,_,_ in D['items']],dtype=int)
    sids=sorted(set(D['session']))
    if len(sids)!=24:raise ValueError('expected 24 sessions')
    bases=summarize_session_bases(events)
    tau={s:0 for s in sids}
    if base_mode=='nested_adaptive':_,tau,_=get_predictions(events)
    result={m:defaultdict(list) for m in MODELS}
    fitted={m:[] for m in MODELS}
    for held in sids:
        base=base_without(bases,{held})
        p=np.array([[adaptive_probability(e,get_pbase(e,base),tau[held]) for e in group]
                     for _,group,_,_,_ in D['items']])
        train=D['session']!=held;test=~train
        for m in MODELS:
            state=np.array([[stratum(e,m) for e in group] for _,group,_,_,_ in D['items']])
            adj=np.zeros_like(p)
            deltas={}
            for stratum_id in range(9 if m=='payoff_tenure_9' else 3):
                mask=np.repeat(train[:,None],6,axis=1)&(state==stratum_id)
                if np.count_nonzero(mask)<10:delta=0.
                else:delta=fit_logit_shift(p[mask],y[mask])
                deltas[stratum_id]=delta
                adj[state==stratum_id]=delta
            fitted[m].append(deltas)
            calibrated=sigmoid(np.log(p/(1-p))+adj)
            val,pzero=batch_law(D['old'][test],calibrated[test],D['u'][test],D['d'][test],D['period'][test],'independent',0)
            for j,i in enumerate(np.where(test)[0]):
                result[m][held].append((held,int(D['period'][i]),int(D['old'][i].sum()),float(-np.log(val[j])),float(pzero[j]),int(D['u'][i]==0 and D['d'][i]==0),float(calibrated[i].sum()),int(D['u'][i]+D['d'][i])))
    summaries={}
    for m in MODELS:
        score=aggregate({'independent':result[m]},{},bootstrap=bootstrap,seed=seed)['scores']['independent']
        score['allowed_own_predecision_feedback_only']=True
        summaries[m]=score
    return {'model_scores':summaries,'conditions':{'sessions':24,'evaluated_group_transitions':len(D['items']),'no_analyst_occupancy_in_personal_probability':True,'lagged_reward_and_streak_from_observed_prefix':True}}
