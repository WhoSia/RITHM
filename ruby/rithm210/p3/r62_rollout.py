"""RITHM R62: fully endogenous collective-pause or shared-shock rollouts.
No future observed choice/payoff enters generated decisions. The joint latent
state is analyst-level; not alleged to be disclosed to uninformed subjects.
"""
from collections import defaultdict
from math import inf
from random import Random
from statistics import mean
from r61_closed_loop import collect_groups
from r61_adaptive_prior import summarize_session_bases,base_without,get_pbase,adaptive_probability,get_predictions
from r62_batch import full_cv_fast

MODELS=('independent','at_four_joint','at_four_stability','late_four_stability','common_shock_joint')


def forecast_step(old_routes,prior_counts,base_e,trained,t,model,q,common_random):
    """common_random=(group latent uniform,6 actor uniforms) all consumed same round."""
    if len(old_routes)!=6 or len(prior_counts)!=6:raise ValueError('six actors')
    z,coins=common_random
    if not 0<=z<1 or len(coins)!=6 or any(not 0<=c<1 for c in coins):raise ValueError('random uniforms outside [0,1)')
    ps=[]
    for j in range(6):
        b=base_e[j]
        e={'treatment':b['treatment'],'info':b['info'],'previous_route':old_routes[j],
           'current_exposure':t-2,'current_count':prior_counts[j], 'own_count':b['own_count']}
        ps.append(adaptive_probability(e,get_pbase(e,trained),0))
    if model=='independent':p=ps
    elif model=='common_shock_joint':
        sign=-1 if z<.5 else 1
        p=[x+sign*q*min(x,1-x) for x in ps]
    else:
        q=min(q,(1-max(ps))*.999999)
        if model in ('at_four_joint','at_four_stability'):
            if sum(old_routes)!=4:q=0.
        elif model=='late_four_stability':
            if sum(old_routes)!=4 or t<21:q=0.
        else:raise ValueError('unregistered model')
        p=[0.]*6 if z<q else [x/(1-q) for x in ps]
    return [int(coins[j]<p[j]) for j in range(6)]


def rollout(group,trained,model,q,uniforms,*,start='observed'):
    if len(uniforms)!=40:raise ValueError('need period-one plus 39 later rounds')
    if start not in ('observed','fair'):raise ValueError('unsupported start')
    old=group['initial_route'][:] if start=='observed' else [int(x<.5) for x in uniforms[0][1]]
    counts=[0]*6
    C=3*(sum(old)-4)**2;G=0;series=[(sum(old),0)]
    base=[x[0] for x in group['actors']]
    for t in range(2,41):
        switches=forecast_step(old,counts,base,trained,t,model,q,uniforms[t-1])
        old=[r^y for r,y in zip(old,switches)]
        counts=[x+y for x,y in zip(counts,switches)]
        s=sum(switches);G+=s
        C+=3*(sum(old)-4)**2
        series.append((sum(old),s))
    return C,G,series


def run_rollouts(events,*,reps=64,seed=20261121,start='observed',bootstrap=2000):
    if reps<1:raise ValueError('positive repetitions')
    groups=collect_groups(events)
    sid=sorted({g['session'] for g in groups})
    j,jq=full_cv_fast(events,selector='joint')
    s,sq=full_cv_fast(events,selector='a4_no_switch_brier')
    q_map={m:{} for m in MODELS}
    for pos,held in enumerate(sid):
        q_map['independent'][held]=0.
        q_map['at_four_joint'][held]=jq['pause_at_four'][pos]
        q_map['at_four_stability'][held]=sq['pause_at_four'][pos]
        q_map['late_four_stability'][held]=sq['pause_late_four'][pos]
        q_map['common_shock_joint'][held]=jq['common_positive'][pos]
    bases=summarize_session_bases(events)
    trained={sid:base_without(bases,{sid}) for sid in sid}
    rand=Random(seed)
    error={m:defaultdict(lambda:[0.,0.,0.,0.]) for m in MODELS}
    diagnostics={m:defaultdict(float) for m in MODELS}
    by_trt={m:defaultdict(lambda:[0.,0.]) for m in MODELS}
    by_obs=defaultdict(lambda:[0.,0.])
    for g in groups:
        s=g['session'];tr=g['actors'][0][0]['treatment']
        observed=(g['target_congestion'],g['target_gross'])
        by_obs[tr][0]+=observed[0];by_obs[tr][1]+=1
        totals={m:[0.,0.] for m in MODELS}
        for _ in range(reps):
            uniforms=[(rand.random(),tuple(rand.random() for _ in range(6))) for _ in range(40)]
            for m in MODELS:
                c,gross,trajectory=rollout(g,trained[s],m,q_map[m][s],uniforms,start=start)
                totals[m][0]+=c;totals[m][1]+=gross
                d=diagnostics[m]
                d['periods']+=40
                d['at_four']+=sum(a==4 for a,gr in trajectory)
                d['late_four']+=sum(a==4 for a,gr in trajectory[-10:])
                d['late_n']+=10
                for j in range(1,40):
                    if trajectory[j-1][0]==4:
                        d['prev_four']+=1
                        d['stable_four']+=int(trajectory[j][0]==4 and trajectory[j][1]==0)
                        d['return_four']+=int(trajectory[j][0]==4)
        for m in MODELS:
            predc,predg=[x/reps for x in totals[m]]
            ec=predc-observed[0];eg=predg-observed[1]
            err=error[m][s]
            err[0]+=ec*ec;err[1]+=eg*eg;err[2]+=2*ec*eg;err[3]+=1
            by_trt[m][tr][0]+=predc;by_trt[m][tr][1]+=1
    data={}
    for m in MODELS:
        e=error[m]
        d=diagnostics[m]
        data[m]={'cost_group_total_MSE':mean(x[0]/x[3] for x in e.values()),
            'gross_group_total_MSE':mean(x[1]/x[3] for x in e.values()),
            'resource_kappa_polynomial':{c:mean(x[ix]/x[3] for x in e.values()) for c,ix in [('A',0),('B',2),('D',1)]},
            'occupancy_4_fraction':d['at_four']/d['periods'],
            'late_occupancy_4_fraction':d['late_four']/d['late_n'],
            'p_no_switch_given_previous_four':d['stable_four']/d['prev_four'],
            'p_remain_four_given_previous_four':d['return_four']/d['prev_four'],
            'treatment_group_mean_excess':{str(t):r[0]/r[1] for t,r in by_trt[m].items()},
            'selected_q_histogram':{str(x):list(q_map[m].values()).count(x) for x in sorted(set(q_map[m].values()))}}
    rng=Random(seed+1337)
    for m in MODELS:
        if m=='independent':continue
        diff=[error[m][s][0]/error[m][s][3]-error['independent'][s][0]/error['independent'][s][3] for s in sid]
        drawn=sorted(mean(diff[rng.randrange(len(sid))] for _ in sid) for _ in range(bootstrap))
        data[m]['cost_MSE_minus_independent']={'delta':mean(diff), 'cluster_95_descriptive':[drawn[int(bootstrap*.025)],drawn[int(bootstrap*.975)]]}
    return {'source_groups':len(groups),'sessions':len(sid),'reps_per_group':reps,'seed':seed,'start':start,
            'observed_group_excess_by_treatment':{str(t):r[0]/r[1] for t,r in by_obs.items()},
            'model_results':data,
            'scope':'No source human actor rows; 40-period generated trajectories, original initial actor routes only when observed start; six simultaneous decisions per period.'}
