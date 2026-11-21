"""RITHM R61: evaluate same nested private-memory policy as an autonomous rollout.

Two distinct estimands: conditional on observed first target-period routes, and
fair 50:50 first-period routes. Both use *only* prior-section histories and
simulated prior target-section choices, never observed target t>=2 choices.
Personal original source is used privately for observed *scores* and allowed
period-1 starting routes; no participant route histories are exported.
"""
from collections import defaultdict
from math import inf
from random import Random
from statistics import mean
from r61_adaptive_prior import (adaptive_probability,base_without,get_pbase,
                                summarize_session_bases,MODELS,bootstrap_comparison)

RIVALS=('current_only','static_prior','nested_adaptive','fixed_tau_8')

def collect_groups(events):
    roster=defaultdict(lambda:defaultdict(list))
    for e in events:roster[e['session'],e['section'],e['group']][e['actor']].append(e)
    result=[]
    for (s,sec,g),persons in sorted(roster.items()):
        if len(persons)!=6:raise ValueError('bad group')
        persons_sorted=[]
        for actor,hist in sorted(persons.items()):
            z=sorted(hist,key=lambda e:e['period'])
            if [e['period'] for e in z]!=list(range(2,41)):
                raise ValueError('actor timeline missing')
            if any(row['own_count']!=z[0]['own_count'] or
                   row['info']!=z[0]['info'] or row['treatment']!=z[0]['treatment'] for row in z):
                raise ValueError('group participant history changed')
            persons_sorted.append(z)
        realized_congestion=0.;realized_switches=0
        initial_route=[z[0]['target_initial_route'] for z in persons_sorted]
        old=initial_route
        realized_congestion+=3*(sum(old)-4)**2
        for t in range(2,41):
            rows=[z[t-2] for z in persons_sorted]
            if [e['previous_route'] for e in rows]!=old:
                raise ValueError('source route continuity lost')
            next_route=[old[i]^rows[i]['flip'] for i in range(6)]
            realized_switches+=sum(e['flip'] for e in rows)
            realized_congestion+=3*(sum(next_route)-4)**2
            old=next_route
        result.append({'session':s,'section':sec,'group':g,'actors':persons_sorted,
                       'initial_route':initial_route,'target_congestion':realized_congestion,
                       'target_gross':realized_switches})
    if len(result)!=96:raise ValueError('96 linked target group-sections required')
    return result


def rollout_one(group,trained,tau,mode,coins,*,first='observed',trace=False):
    if mode not in RIVALS:raise ValueError('unknown candidate')
    if first not in ('observed','fair'):raise ValueError('unknown start rule')
    if len(coins)!=40 or any(len(c)!=6 for c in coins):
        raise ValueError('fixed 40x6 uniforms required')
    routes=group['initial_route'][:] if first=='observed' else [int(coins[0][i]<.5) for i in range(6)]
    count=[0]*6;cost=3*(sum(routes)-4)**2;gross=0;trajectory=[(sum(routes),0)] if trace else None
    for t in range(2,41):
        flips=[]
        for j in range(6):
            old_e=group['actors'][j][0]
            # The current *simulated* route and count replace the observed target states.
            e={'treatment':old_e['treatment'],'info':old_e['info'],
               'previous_route':routes[j],'own_count':old_e['own_count'],
               'current_exposure':t-2,'current_count':count[j]}
            base=get_pbase(e,trained)
            decay={'current_only':0,'static_prior':inf,'nested_adaptive':tau,'fixed_tau_8':8}[mode]
            p=adaptive_probability(e,base,decay)
            flips.append(int(coins[t-1][j]<p))
        # All six actors make choices before any new group state is visible.
        routes=[routes[j]^flips[j] for j in range(6)]
        count=[count[j]+flips[j] for j in range(6)]
        gross+=sum(flips)
        cost+=3*(sum(routes)-4)**2
        if trace:trajectory.append((sum(routes),sum(flips)))
    return (cost,gross,trajectory) if trace else (cost,gross)


def rollout_score(events,selected,*,reps=64,seed=20261121,start='observed'):
    if not isinstance(reps,int) or reps<1:raise ValueError('repetitions must be positive')
    if start not in ('observed','fair'):raise ValueError('bad start')
    groups=collect_groups(events)
    totals=summarize_session_bases(events)
    train={s:base_without(totals,{s}) for s in selected}
    rng=Random(seed)
    errors=defaultdict(lambda:{name:[0.,0.,0.,0.,0.,0.] for name in RIVALS})
    cohort_observed=defaultdict(lambda:[0.,0.,0])
    cohort_predicted=defaultdict(lambda:{n:[0.,0.,0] for n in RIVALS})
    for g in groups:
        s=g['session'];trt=g['actors'][0][0]['treatment']
        if s not in selected:raise ValueError('missing nested hyperparameter')
        sums={n:[0.,0.] for n in RIVALS}
        for _ in range(reps):
            coins=[[rng.random() for i in range(6)] for t in range(40)]
            for name in RIVALS:
                c,m=rollout_one(g,train[s],selected[s],name,coins,first=start)
                sums[name][0]+=c;sums[name][1]+=m
        obsC,obsG=g['target_congestion'],g['target_gross']
        cohort_observed[trt][0]+=obsC;cohort_observed[trt][1]+=obsG;cohort_observed[trt][2]+=1
        for name in RIVALS:
            expectedC,expectedG=[x/reps for x in sums[name]]
            eC=expectedC-obsC;eG=expectedG-obsG
            A=errors[s][name]
            A[0]+=eC*eC; A[1]+=eG*eG;A[2]+=2*eC*eG;A[3]+=1
            A[4]+=expectedC;A[5]+=expectedG
            cohort_predicted[trt][name][0]+=expectedC
            cohort_predicted[trt][name][1]+=expectedG
            cohort_predicted[trt][name][2]+=1
    scores={}
    for name in RIVALS:
        scores[name]={
          'congestion_group_total_mse':mean(x[name][0]/x[name][3] for x in errors.values()),
          'gross_switch_group_total_mse':mean(x[name][1]/x[name][3] for x in errors.values()),
          'resource_mse_kappa_polynomial':{
            'A':mean(x[name][0]/x[name][3] for x in errors.values()),
            'B':mean(x[name][2]/x[name][3] for x in errors.values()),
            'D':mean(x[name][1]/x[name][3] for x in errors.values())}}
    by_treatment={}
    for trt in sorted(cohort_observed):
        obs=cohort_observed[trt];by_treatment[str(trt)]={
          'observed_mean_congestion_40periods':obs[0]/obs[2],
          'observed_mean_gross_switches_39transitions':obs[1]/obs[2],
          'group_sections':obs[2],
          'predicted_mean_congestion_40periods':{name:cohort_predicted[trt][name][0]/cohort_predicted[trt][name][2] for name in RIVALS}}
    def comparison(a,b,metric='congestion',boots=2000):
        k=0 if metric=='congestion' else 1
        values=[(errors[s][a][k]-errors[s][b][k])/errors[s][a][3] for s in sorted(errors)]
        rnd=Random(seed+len(start)+k+len(a));sampling=sorted(mean(values[rnd.randrange(len(values))] for _ in values) for _ in range(boots))
        return {'alternative':a,'baseline':b,'metric':metric,
            'MSE_difference':mean(values),'session_resampling_95_descriptive':[sampling[int(.025*boots)],sampling[int(.975*boots)]]}
    return {'start':start,'MonteCarlo_reps_per_group':reps,'seed':seed,
            'group_sections':len(groups),'model_scores':scores,'by_treatment':by_treatment,
            'nested_vs_online_congestion':comparison('nested_adaptive','current_only'),
            'nested_vs_static_congestion':comparison('nested_adaptive','static_prior'),
            'scope':'40-period group-total prediction error conditional on observed prior section; no policy causal effect'}
