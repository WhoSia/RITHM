"""RITHM P3-R57: fully source-verified, predecision-legal history stratification.

The sealed, authorized original source is private.  Output contains ONLY cohort
aggregates.  Session-heldout one-step predictions use observed history through
t-1; none of t's outcome, payoff, occupancy or treatment changes leaks to fit.

This is a descriptive predictive audit, NOT a causal cognition/coordination test.
"""
from collections import Counter, defaultdict
import csv
from io import StringIO
import json
from math import log
from pathlib import Path
from random import Random
from statistics import mean
from zipfile import ZipFile

from r54_original_batch_clock import SOURCE_NAME, audit_zip
from r56_joint_flow_cv import infer_laws, train_counts, loss, flow_support

# All bins, priors and models are *frozen before* evaluation.  No heldout tuning.
SHRINK = 20
MODELS = ('state_independent', 'tenure', 'received_profit', 'tenure_profit',
          'informed', 'tenure_profit_informed')


def tenure_bin(streak):
    if type(streak) is not int or streak < 1:
        raise ValueError('streak must be a positive integer from the observed prefix')
    return 0 if streak == 1 else (1 if streak <= 3 else 2)


def profit_bin(profit):
    x = float(profit)
    return 0 if x < 4 else (1 if x < 8 else 2)


def actor_cell(a, actor, name):
    """An actor is (previous route, lagged tenure, lagged realized profit, informed)."""
    route, tenure, profit, informed = actor
    prefix = (a, route)
    if name == 'state_independent':
        return prefix
    attrs = {'tenure': (tenure_bin(tenure),),
             'received_profit': (profit_bin(profit),),
             'tenure_profit': (tenure_bin(tenure), profit_bin(profit)),
             'informed': (informed,),
             'tenure_profit_informed': (tenure_bin(tenure), profit_bin(profit), informed)}
    if name not in attrs:
        raise ValueError('unrecognized feature model')
    return prefix + attrs[name]


def load_history_events(source):
    """Return private in-memory group rows; audit original ZIP first and export none."""
    audit = audit_zip(source, require_original=True)
    groups = defaultdict(lambda: defaultdict(dict))
    treatment = {}
    with ZipFile(source) as z:
        raw = z.read(SOURCE_NAME).decode('utf-8-sig')
    for row in csv.DictReader(StringIO(raw)):
        s, section, trt, t = (int(row[k]) for k in ('session','section','trt','Period'))
        if s in (2,101) or trt not in (1,2,3) or t < 1:
            continue
        key = (s, section, int(row['Group']))
        if key in treatment and treatment[key] != trt:
            raise ValueError('treatment changed inside group')
        treatment[key] = trt
        actor = int(row['ID'])
        if actor in groups[key][t]:
            raise ValueError('duplicate actor')
        r = int(row['RouteA'])
        a = int(row['NumA'])
        info = int(row['Informed'])
        val = float(row['Value'])
        profit = float(row['profit'])
        cost = float(row['Cost'])
        if info not in (0,1) or r not in (0,1) or abs(cost - (a if r else 2*(6-a))) > 1e-6:
            raise ValueError('invalid info, route or deterministic route cost')
        if abs(profit - (val-cost)) > 1e-6:
            raise ValueError('received payoff is not the realized value minus route cost')
        groups[key][t][actor] = (r, profit, cost, info, a)

    events=[]
    for key, periods in sorted(groups.items()):
        if sorted(periods) != list(range(1,41)):
            raise ValueError('nonconsecutive time series')
        actors = sorted(periods[1])
        if len(actors) != 6 or any(sorted(periods[t]) != actors for t in range(1,41)):
            raise ValueError('invalid six-seat actor support')
        streak = {i:1 for i in actors}
        trt = treatment[key]
        for t in range(2,41):
            past, current = periods[t-1], periods[t]
            a = sum(past[i][0] for i in actors)
            if any(past[i][4] != a for i in actors):
                raise ValueError('source previous occupancy mismatch')
            # Only prior period values enter predictor; t's values are touched
            # below solely to form the outcome labels and update next prefix.
            past_features = tuple((past[i][0], streak[i], past[i][1], past[i][3])
                                  for i in actors)
            switched = tuple(int(past[i][0] != current[i][0]) for i in actors)
            u = sum(past_features[k][0] == 0 and switched[k] for k in range(6))
            d = sum(past_features[k][0] == 1 and switched[k] for k in range(6))
            events.append({'session':key[0], 'trt':trt, 'period':t, 'a':a,
                           'actors':past_features, 'flips':switched, 'ud':(u,d)})
            for i in actors:
                streak[i] = streak[i] + 1 if past[i][0] == current[i][0] else 1
    if len(events) != audit['group_period_transitions']:
        raise AssertionError('history event count differs from source audit')
    return events


def train_histories(events):
    """Training-only (n, flips) in strata; no fitting from held session."""
    n=defaultdict(lambda: defaultdict(Counter))
    for e in events:
        for model in MODELS[1:]:
            for a, flip in zip(e['actors'], e['flips']):
                n[model][(e['trt'],)+actor_cell(e['a'],a,model)]+=Counter({'n':1,'y':flip})
    return n


def fitted_laws(train):
    tuples = [(e['session'],e['trt'],e['a'],*e['ud']) for e in train]
    counts = train_counts(tuples)
    return {trt:infer_laws(counts,trt)['state_independent'] for trt in (1,2,3)}


def flip_probability(e, actor, model, base, trained, *, shrink=SHRINK):
    if type(shrink) is not int or shrink < 1:
        raise ValueError('positive fixed pseudo-exposure required')
    a = e['a']
    prev_a = actor[0]
    pbase = sum((d if prev_a else u)*p for (u,d),p in base[e['trt']][a].items())
    pbase /= (a if prev_a else (6-a))
    if not 0 < pbase < 1:
        raise ArithmeticError('improper baseline Bernoulli')
    if model == 'state_independent':
        return pbase
    key=(e['trt'],)+actor_cell(a,actor,model)
    count=trained[model].get(key, Counter())  # read-only on an unseen heldout stratum
    return (count['y'] + shrink*pbase)/(count['n'] + shrink)


def poisson_binomial(ps):
    coeff = [1.0]
    for p in ps:
        if not 0 < p < 1:
            raise ValueError('all transition probabilities must be strictly positive')
        next_coeff=[0.0]*(len(coeff)+1)
        for k,mass in enumerate(coeff):
            next_coeff[k] += mass*(1-p)
            next_coeff[k+1] += mass*p
        coeff=next_coeff
    return coeff


def actor_probabilities(e, model, base, trained, *, shrink=SHRINK):
    return tuple(flip_probability(e, actor, model, base, trained, shrink=shrink)
                 for actor in e['actors'])


def flow_from_probabilities(e, probabilities):
    a=e['a']
    down = poisson_binomial([p for p,act in zip(probabilities,e['actors']) if act[0]])
    up = poisson_binomial([p for p,act in zip(probabilities,e['actors']) if not act[0]])
    if len(down)!=a+1 or len(up)!=7-a:
        raise AssertionError('wrong directional exposure')
    law={(u,d):up[u]*down[d] for u,d in flow_support(a)}
    if abs(sum(law.values())-1)>1e-11:
        raise ArithmeticError('invalid Poisson-binomial flow law')
    return law


def forecast_flow(e, model, base, trained, *, shrink=SHRINK):
    return flow_from_probabilities(e, actor_probabilities(e,model,base,trained,shrink=shrink))


def actor_scores(e, probabilities):
    """Joint individual scores and exact *within-route* outcome-permutation mean.

    This is a one-step conditional diagnostic, NOT a physical trajectory.
    Permuting flipped identities within each previous route preserves (U,D)
    exactly but removes which within-route covariate received the flip.
    """
    if len(probabilities)!=6 or len(e['actors'])!=6 or len(e['flips'])!=6:
        raise ValueError('requires full six-seat actor observation')
    observed=expected=observed_brier=expected_brier=0.0
    for route in (0,1):
        idx=[i for i,act in enumerate(e['actors']) if act[0]==route]
        q=sum(e['flips'][i] for i in idx)/len(idx) if idx else 0.0
        for i in idx:
            p=probabilities[i]
            y=e['flips'][i]
            observed-=y*log(p)+(1-y)*log(1-p)
            expected-=q*log(p)+(1-q)*log(1-p)
            observed_brier+=(p-y)**2
            expected_brier+=q*(1-p)**2+(1-q)*p*p
    return {'actor_logloss':observed/6,
            'route_permutation_expected_actor_logloss':expected/6,
            'actor_brier':observed_brier/6,
            'route_permutation_expected_actor_brier':expected_brier/6}


def leave_one_session_out(events, *, bootstrap=2000, seed=20261121, shrink=SHRINK):
    sessions=sorted({e['session'] for e in events})
    if len(sessions)<3: raise ValueError('at least three distinct sessions required')
    bysession=defaultdict(list)
    for e in events:
        bysession[e['session']].append(e)
    scores=[]
    # Heldout sessions are *never* used for fitting the baseline or extra strata.
    for held in sessions:
        training=[e for s, items in bysession.items() if s!=held for e in items]
        base=fitted_laws(training)
        extra=train_histories(training)
        ses_scores={name:[] for name in MODELS}
        ses_actor={name:[] for name in MODELS}
        ses_arm={trt:{name:[] for name in MODELS} for trt in (1,2,3)}
        ses_phase={phase:{name:[] for name in MODELS} for phase in ('early','late')}
        for e in bysession[held]:
            for model in MODELS:
                p=actor_probabilities(e,model,base,extra,shrink=shrink)
                law=flow_from_probabilities(e,p)
                pair=loss(law,e['ud'])
                ses_scores[model].append(pair)
                ses_arm[e['trt']][model].append(pair)
                ses_phase['early' if e['period']<=20 else 'late'][model].append(pair)
                ses_actor[model].append(actor_scores(e,p))
        row={name:(mean(x[0] for x in pts),mean(x[1] for x in pts))
             for name,pts in ses_scores.items()}
        row['actor']={name:{metric:mean(x[metric] for x in entries)
                            for metric in entries[0]}
                      for name,entries in ses_actor.items()}
        row['by_treatment']={str(trt):{name:mean(z[0] for z in ses_arm[trt][name])
                                      for name in MODELS} for trt in (1,2,3)}
        row['by_phase']={phase:{name:mean(z[0] for z in ses_phase[phase][name])
                                for name in MODELS} for phase in ('early','late')}
        row['count']=len(bysession[held])
        scores.append(row)
    if type(bootstrap) is not int or bootstrap < 1:
        raise ValueError('positive bootstrap integer required')
    summary={name:{'equal_session_logloss_nats':mean(r[name][0] for r in scores),
                   'equal_session_brier':mean(r[name][1] for r in scores),
                   'transition_equal_logloss_nats':sum(r[name][0]*r['count'] for r in scores)/len(events)}
             for name in MODELS}
    actors={name:{metric:mean(r['actor'][name][metric] for r in scores)
                   for metric in scores[0]['actor'][name]}
            for name in MODELS}
    for name in MODELS:
        actors[name]['route_permutation_actor_logloss_skill']=(
            actors[name]['route_permutation_expected_actor_logloss'] -
            actors[name]['actor_logloss'])
        actors[name]['route_permutation_actor_brier_skill']=(
            actors[name]['route_permutation_expected_actor_brier'] -
            actors[name]['actor_brier'])
    conditional={
        'by_treatment':{str(trt):{name:mean(r['by_treatment'][str(trt)][name] for r in scores)
                                  for name in MODELS} for trt in (1,2,3)},
        'by_phase':{phase:{name:mean(r['by_phase'][phase][name] for r in scores)
                           for name in MODELS} for phase in ('early','late')},
    }
    rng=Random(seed)
    differences={}
    for name in MODELS[1:]:
        diffs=[r[name][0]-r['state_independent'][0] for r in scores]
        draws=sorted(mean(diffs[rng.randrange(len(scores))] for _ in scores)
                     for _ in range(bootstrap))
        differences[name]={'minus_baseline_equal_session_logloss':mean(diffs),
                           'session_bootstrap_95_percentile':[draws[int(0.025*bootstrap)],
                                                                draws[min(bootstrap-1,int(0.975*bootstrap))]],
                           'sessions_improved':sum(d<0 for d in diffs)}
    incremental_contrasts={}
    for alternative,baseline in (('tenure_profit','tenure'),
                                 ('tenure_profit_informed','tenure_profit')):
        delta=[r[alternative][0]-r[baseline][0] for r in scores]
        draws=sorted(mean(delta[rng.randrange(len(scores))] for _ in scores)
                     for _ in range(bootstrap))
        incremental_contrasts[alternative+'_minus_'+baseline]={
            'mean_difference':mean(delta),
            'session_bootstrap_95_percentile':[draws[int(0.025*bootstrap)],
                                                 draws[min(bootstrap-1,int(0.975*bootstrap))]],
            'sessions_improved':sum(d<0 for d in delta)}
    permutation_skill={}
    for name in MODELS:
        per_session=[r['actor'][name]['route_permutation_expected_actor_logloss']-
                     r['actor'][name]['actor_logloss'] for r in scores]
        draws=sorted(mean(per_session[rng.randrange(len(scores))] for _ in scores)
                     for _ in range(bootstrap))
        permutation_skill[name]={
            'observed_actor_assignment_advantage':mean(per_session),
            'session_bootstrap_95_percentile':[draws[int(0.025*bootstrap)],
                                                 draws[min(bootstrap-1,int(0.975*bootstrap))]],
        }
    return {'session_count':len(sessions),'transition_count':len(events),'models':summary,
            'actor_level':actors, 'stratified':conditional,
            'within_route_assignment_diagnostic':permutation_skill,
            'incremental_feature_contrasts':incremental_contrasts,
            'differences':differences, 'fixed_shrinkage_pseudoexposure':shrink,
            'endpoint':'joint simultaneous (B-to-A, A-to-B) change counts',
            'filtration':'only actual histories at and before t-1; treatment and analyst-known old occupancy',
            'scope':'exploratory descriptive heldout prediction; not mechanism or causal identification'}


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('approved_zip',type=Path)
    ap.add_argument('--bootstrap',type=int,default=2000)
    args=ap.parse_args()
    print(json.dumps(leave_one_session_out(load_history_events(args.approved_zip),
                                          bootstrap=args.bootstrap),indent=2,sort_keys=True))
