"""R62: legal previous-own payoff/streak under fully generated 40-round choices.

The original exogenous individual Value(t) is read privately and disclosed only
AFTER a simulated choice each period, as an environmental shock tape. The
person's unchosen payoff and other participants' occupancy are NOT actor inputs.
"""
from collections import defaultdict
import csv,zipfile
from io import StringIO
from hashlib import sha256
from pathlib import Path
from random import Random
from statistics import mean
from math import log,exp
import numpy as np
from r54_original_batch_clock import APPROVED_ZIP_SHA256
from r61_closed_loop import collect_groups
from r62_legal_joint import fit_legal_by_held
from r62_batch import batch_law
from r62_collective import GRID
from r62_legal_feedback import stratum
from r61_adaptive_prior import get_pbase,adaptive_probability
from r62_statecal import sigmoid

MODELS=('r61_current_only','legal_independent','legal_pause_stability','legal_common_shock_joint')


def source_values(source):
    if sha256(Path(source).read_bytes()).hexdigest()!=APPROVED_ZIP_SHA256:
        raise ValueError('original restricted source SHA mismatch')
    values={}
    with zipfile.ZipFile(source) as z:
        for row in csv.DictReader(StringIO(z.read('data_task_all_switch_230705.csv').decode('utf-8-sig'))):
            s,sec,t=(int(row[x]) for x in ('session','section','Period'))
            if s in (2,101) or sec not in (3,4) or t not in range(1,41):continue
            key=(s,sec,int(row['Group']),int(row['ID']))
            values.setdefault(key,{})[t]=(float(row['Value']),float(row['profit']),int(row['RouteA']))
    if len(values)!=96*6 or any(len(x)!=40 for x in values.values()):raise ValueError('original values cohort mismatch')
    return values


def legal_rollout(group,trained,tau,offsets,model,q,coins,value_by_actor,*,start='observed'):
    if model not in MODELS or len(coins)!=40 or len(value_by_actor)!=6:raise ValueError('bad model support')
    if start not in ('observed','fair'):raise ValueError('bad starting rule')
    routes=group['initial_route'][:] if start=='observed' else [int(x<.5) for x in coins[0][1]]
    a=sum(routes);C=3*(a-4)**2;G=0;trajectory=[(a,0)]
    counts=[0]*6;tenure=[1]*6
    prev_payoffs=[]
    for j in range(6):
        value,old_profit,old_route=value_by_actor[j][1]
        if start=='observed' and old_route!=routes[j]:raise AssertionError('wrong initial source route')
        cost=a if routes[j] else 2*(6-a)
        profit=value-cost
        if start=='observed' and abs(profit-old_profit)>1e-9:raise AssertionError('wrong original first reward')
        prev_payoffs.append(profit)
    base=[x[0] for x in group['actors']]
    for t in range(2,41):
        probabilities=[]
        for j in range(6):
            e={'treatment':base[j]['treatment'],'info':base[j]['info'],
               'previous_route':routes[j],'current_exposure':t-2,
               'current_count':counts[j], 'own_count':base[j]['own_count']}
            p=adaptive_probability(e,get_pbase(e,trained),tau)
            if model!='r61_current_only':
                pbin=0 if prev_payoffs[j]<4 else (1 if prev_payoffs[j]<8 else 2)
                tbin=0 if tenure[j]==1 else (1 if tenure[j]<=3 else 2)
                shift=offsets[pbin*3+tbin]
                p=1/(1+exp(-(log(p/(1-p))+shift)))
            probabilities.append(p)
        z,actor_coins=coins[t-1]
        if model=='legal_pause_stability':
            qq=min(q,(1-max(probabilities))*.999999) if a==4 else 0.
            effective=[0.]*6 if z<qq else [p/(1-qq) for p in probabilities]
        elif model=='legal_common_shock_joint':
            sign=-1 if z<.5 else 1
            effective=[p+sign*q*min(p,1-p) for p in probabilities]
        else:effective=probabilities
        switches=[int(actor_coins[j]<effective[j]) for j in range(6)]
        routes=[route^sw for route,sw in zip(routes,switches)]
        counts=[counts[j]+switches[j] for j in range(6)]
        tenure=[1 if switches[j] else tenure[j]+1 for j in range(6)]
        G+=sum(switches)
        a=sum(routes);C+=3*(a-4)**2
        trajectory.append((a,sum(switches)))
        prev_payoffs=[value_by_actor[j][t][0]-(a if routes[j] else 2*(6-a)) for j in range(6)]
    return C,G,trajectory


def run_legal_rollouts(events,source,*,reps=64,seed=20261121,start='observed',bootstrap=2000,base_mode='nested_adaptive'):
    vals=source_values(source)
    groups=collect_groups(events)
    by_session=defaultdict(list)
    for g in groups:by_session[g['session']].append(g)
    fits={};selected={}
    for held,D,p,shifts,trained,tau in fit_legal_by_held(events,base_mode):
        train=D['session']!=held
        grid_loss=[];grid_brier=[]
        for q in GRID:
            target,z=batch_law(D['old'][train],p[train],D['u'][train],D['d'][train],D['period'][train],'common_positive',q)
            grid_loss.append(float(np.mean(-np.log(target))))
            a4=train&(D['old'].sum(axis=1)==4)
            _,za=batch_law(D['old'][a4],p[a4],D['u'][a4],D['d'][a4],D['period'][a4],'pause_at_four',q)
            actual=(D['u'][a4]==0)&(D['d'][a4]==0)
            grid_brier.append(float(np.mean((za-actual)**2)))
        fits[held]=(trained,tau,shifts)
        selected[held]={'legal_pause_stability':GRID[int(np.argmin(grid_brier))],
                        'legal_common_shock_joint':GRID[int(np.argmin(grid_loss))]}
    rng=Random(seed)
    errors={m:defaultdict(lambda:[0.,0.,0.,0]) for m in MODELS}
    counter={m:defaultdict(float) for m in MODELS}
    btr={m:defaultdict(lambda:[0.,0.]) for m in MODELS}
    original_tr=defaultdict(lambda:[0.,0.])
    for g in groups:
        s=g['session'];trt=g['actors'][0][0]['treatment']
        actors=[h[0]['actor'] for h in g['actors']]
        v=[vals[s,g['section'],g['group'],i] for i in actors]
        fitted,tau,shifts=fits[s]
        sums={m:[0.,0.] for m in MODELS}
        original_tr[trt][0]+=g['target_congestion'];original_tr[trt][1]+=1
        for _ in range(reps):
            coins=[(rng.random(),tuple(rng.random() for _ in range(6))) for _ in range(40)]
            for m in MODELS:
                q=selected[s].get(m,0.)
                c,gross,traj=legal_rollout(g,fitted,0 if m=='r61_current_only' else tau,shifts,m,q,coins,v,start=start)
                sums[m][0]+=c;sums[m][1]+=gross
                d=counter[m]
                d['total_periods']+=40
                d['optimal']+=sum(a==4 for a,_ in traj)
                d['last10_4']+=sum(a==4 for a,_ in traj[-10:]);d['last10_n']+=10
                for j in range(1,40):
                    if traj[j-1][0]==4:
                        d['previous_four']+=1
                        d['no_switch_four']+=int(traj[j][1]==0)
        for m in MODELS:
            predC,predG=[x/reps for x in sums[m]]
            eC=predC-g['target_congestion'];eG=predG-g['target_gross']
            acc=errors[m][s]
            acc[0]+=eC**2;acc[1]+=eG**2;acc[2]+=2*eC*eG;acc[3]+=1
            btr[m][trt][0]+=predC;btr[m][trt][1]+=1
    summary={}
    for m in MODELS:
        d=counter[m];err=errors[m]
        summary[m]={'group_total_congestion_MSE':mean(x[0]/x[3] for x in err.values()),
            'group_total_switch_MSE':mean(x[1]/x[3] for x in err.values()),
            'resource_cost_forecast_MSE_A_B_D':{'A':mean(x[0]/x[3] for x in err.values()),
                'B':mean(x[2]/x[3] for x in err.values()),'D':mean(x[1]/x[3] for x in err.values())},
            'optimal_4_fraction':d['optimal']/d['total_periods'],
            'late_4_fraction':d['last10_4']/d['last10_n'],
            'no_switch_given_previous_four':d['no_switch_four']/d['previous_four'],
            'mean_cost_by_treatment':{str(k):x[0]/x[1] for k,x in btr[m].items()},
            'q_histogram':{str(q):sum(selected[s].get(m,0)==q for s in selected) for q in GRID if sum(selected[s].get(m,0)==q for s in selected)}}
    session_ids=sorted(by_session)
    rng2=Random(seed+123)
    for m in MODELS:
        if m=='r61_current_only':continue
        diff=[errors[m][s][0]/errors[m][s][3]-errors['r61_current_only'][s][0]/errors['r61_current_only'][s][3] for s in session_ids]
        boot=sorted(mean(diff[rng2.randrange(24)] for _ in session_ids) for _ in range(bootstrap))
        summary[m]['congestion_MSE_minus_R61_online']={'delta':mean(diff),'cluster95_descriptive':[boot[int(.025*bootstrap)],boot[int(.975*bootstrap)]]}
    # Paired whole-session intervals for the NEW contribution beyond the
    # strong participant-information lawful own-profit/tenure comparator.
    for m in MODELS:
        if m=='legal_independent':continue
        diff=[errors[m][sid][0]/errors[m][sid][3]-errors['legal_independent'][sid][0]/errors['legal_independent'][sid][3] for sid in session_ids]
        boot=sorted(mean(diff[rng2.randrange(24)] for _ in session_ids) for _ in range(bootstrap))
        summary[m]['congestion_MSE_minus_legal_independent']={
            'delta':mean(diff),'cluster95_descriptive':[boot[int(.025*bootstrap)],boot[int(.975*bootstrap)]]}
    return {'start':start,'seed':seed,'reps':reps,'groups':len(groups),'sessions':len(by_session),
            'source_true_group_total_excess_by_treatment':{str(k):x[0]/x[1] for k,x in original_tr.items()},
            'models':summary,'source_external_value_tape':'Original individual Value(t) never used for decision at t, only payoff after simulated action',
            'scope':'Retrospective 24session descriptive; generated decisions only at t>=2 and no causal intervention or human coordination claimed.'}
