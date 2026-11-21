"""R59 matched-session autonomous 40-period route trajectories.

Synthetic simulations use only preceding generated choices/payoffs, with the
*exogenous* observed individual Value tape as a fixed, after-choice shock. The
original human source stays private and cannot be exported by this module.

This is a model diagnostic, not an estimate of policy counterfactual effects.
"""
from collections import defaultdict
from math import exp, sqrt
from random import Random
from statistics import mean, variance

from r58_author_rivals import (actor_rows_sealed, ewa_path_differences,
                              other_route_belief)
from r58_matched_cv import fitted_ewa_lambda, legal_training, legal_predict
from r57_history_cv import load_history_events

MODELS=('private_history', 'private_route', 'ewa_lite', 'ssm5', 'ssm1_9')


class EWAState:
    """Source-aligned streaming Appendix A update; initial N=1,A_B=A_A=1."""
    def __init__(self, information):
        if len(information)!=6 or any(x not in (0,1) for x in information):
            raise ValueError('six static binary informed masks required')
        self.information=tuple(information)
        self.seen=[[0.0]*6 for _ in range(6)]
        self.n=[1.0]*6
        self.attractions=[[1.0,1.0] for _ in range(6)]
        self.period=0

    def probabilities(self, lam):
        if not 0<=lam<=3:
            raise ValueError('heldout-trained lambda outside documented range')
        return tuple(1/(1+exp(-lam*(a[1]-a[0])))
                     for a in self.attractions)

    def update(self, frame):
        if len(frame)!=6:
            raise ValueError('frame must have six simultaneous actors')
        self.period+=1
        t=self.period
        next_attr=[]
        for seat,(route, info, group_a,profit) in enumerate(frame):
            if info!=self.information[seat]:
                raise ValueError('informed status changed during rollout')
            k=group_a-route
            if not 0<=k<=5:raise ValueError('impossible others occupancy')
            belief=(tuple(float(j==k) for j in range(6)) if info else
                    other_route_belief(route,profit))
            for j in range(6):self.seen[seat][j]+=belief[j]
            avg=[x/t for x in self.seen[seat]]
            surprise=sum((avg[j]-belief[j])**2 for j in range(6))
            phi=max(0.0,min(1.0,1-0.5*surprise))
            expected_k=sum(j*b for j,b in enumerate(belief))
            alt_profit=profit + ((3*expected_k-11) if route else (11-3*expected_k))
            addon=[0.0,0.0];addon[route]=profit
            if alt_profit>=profit-1e-10:addon[1-route]=alt_profit
            n_next=phi*self.n[seat]+1
            next_attr.append([(phi*self.n[seat]*self.attractions[seat][r]+addon[r])/n_next
                             for r in (0,1)])
            self.n[seat]=n_next
        self.attractions=next_attr


class SSMState:
    """Source Appendix B's *sampling algorithm*, not one-step posterior fitting.

    Each actor's sample size is fixed across periods in the q-or-less model.
    No foregone payoffs can enter an uninformed actor's two experienced pools.
    """
    def __init__(self, information, *, fixed_q, rng, lapse=0.02):
        if len(information)!=6 or any(x not in (0,1) for x in information):
            raise ValueError('six informed flags')
        if not 0<=lapse<1:raise ValueError('lapse must lie in [0,1)')
        if fixed_q not in (5, '1_9'):raise ValueError('unsupported SSM q')
        self.information=tuple(information)
        self.q=tuple([5]*6 if fixed_q==5 else [rng.randint(1,9) for _ in range(6)])
        self.a=[[] for _ in range(6)]
        self.b=[[] for _ in range(6)]
        self.diff=[[] for _ in range(6)]
        self.rng=rng
        self.lapse=lapse

    def choose(self, i):
        rng=self.rng
        if rng.random()<self.lapse:
            return rng.randrange(2)
        q=self.q[i]
        if self.information[i]:
            hist=self.diff[i]
            if not hist:return rng.randrange(2)
            d=sum(rng.choice(hist) for _ in range(q))
        else:
            a,b=self.a[i],self.b[i]
            if not a or not b:return rng.randrange(2)
            d=sum(rng.choice(a)-rng.choice(b) for _ in range(q))
        return 1 if d>0 else 0 if d<0 else rng.randrange(2)

    def update(self, frame):
        if len(frame)!=6:raise ValueError('six frame actors')
        for i,(route,info,n_a,profit) in enumerate(frame):
            if info!=self.information[i]:raise ValueError('information mask drift')
            self.diff[i].append(10*(11-3*(n_a-route)))
            (self.a if route else self.b)[i].append(int(round(profit*10)))


def source_value_tape(rec):
    """Immutable exogenous 0.1-resolution Value tape, revealed after each draw."""
    out=[]
    periods=rec['periods']
    if len(periods)!=40:raise ValueError('missing 40 original exogenous draws')
    for frame in periods:
        n=sum(x[0] for x in frame)
        if any(x[2]!=n for x in frame):raise ValueError('source occupancy mismatch')
        values=tuple(round(10*(profit+(n if route else 2*(6-n))))/10
                     for route,_,_,profit in frame)
        if any(not 6-1e-8<=v<=16+1e-8 for v in values):
            raise ValueError('implausible exogenous value')
        out.append(values)
    return out


def initial_routes(rec, rng, init):
    if init=='observed':return [x[0] for x in rec['periods'][0]]
    if init=='fair':return [rng.randrange(2) for _ in range(6)]
    raise ValueError('initial condition must be fair or observed')


def model_seed(seed,session_index,group_index,model_index,rep):
    # Source session ID is neither published nor used in the random seed.
    return seed+session_index*100000003+group_index*1000003+model_index*12347+rep*173


def simulate(rec,*,model,lambda_ewa=0.3,trained_legal=None,init='observed',
             seed=20261121,lapse=0.02,shocks='tape'):
    """Simultaneous choices made BEFORE any current profit/congestion is shown.

    This is a true autonomous route/payoff feedback rollout. It does NOT imply
    an autonomous exogenous value process when shocks='tape': the authorized
    heldout individual's Value(t) is replayed as an independent shock, only
    disclosed after the route decision.
    """
    if model not in MODELS:raise ValueError('unknown simulation model')
    if shocks not in ('tape','fresh_uniform'):raise ValueError('invalid shocks')
    rng=Random(seed)
    informed=[x[1] for x in rec['periods'][0]]
    if any(tuple(x[1] for x in frame)!=tuple(informed) for frame in rec['periods']):
        raise ValueError('informed assignment changed')
    values=source_value_tape(rec) if shocks=='tape' else None
    ewa=EWAState(informed) if model=='ewa_lite' else None
    ssm=(SSMState(informed,fixed_q=(5 if model=='ssm5' else '1_9'),rng=rng,lapse=lapse)
         if model.startswith('ssm') else None)
    routes=[]; streak=[1]*6; pastprofit=[None]*6
    stages=[];tape=[]
    for time in range(40):
        if time==0:
            next_routes=initial_routes(rec,rng,init)
        elif ssm:
            next_routes=[ssm.choose(i) for i in range(6)]
        elif ewa:
            probs=ewa.probabilities(lambda_ewa)
            next_routes=[int(rng.random()<p) for p in probs]
        else:
            if trained_legal is None:raise ValueError('missing trained session-exclusive law')
            event={'trt':rec['treatment'],
                   'actors':tuple((routes[i],streak[i],pastprofit[i],informed[i]) for i in range(6))}
            probs=legal_predict(event,trained_legal,refined=(model=='private_history'))
            next_routes=[int(rng.random()<(1-p if routes[i] else p)) for i,p in enumerate(probs)]
        if len(next_routes)!=6 or any(x not in (0,1) for x in next_routes):
            raise AssertionError('invalid route result')
        n=sum(next_routes)
        switches=sum(x!=y for x,y in zip(next_routes,routes)) if time else 0
        excess=3*(n-4)**2
        # Values are revealed after all current choices have been frozen.
        tape_values=(values[time] if values is not None else
                     [rng.randint(60,160)/10 for _ in range(6)])
        frame=[]
        for i,route in enumerate(next_routes):
            cost=n if route else 2*(6-n)
            profit=tape_values[i]-cost
            frame.append((route,informed[i],n,profit))
        if ewa:ewa.update(frame)
        if ssm:ssm.update(frame)
        if time>0:
            streak=[streak[i]+1 if next_routes[i]==routes[i] else 1 for i in range(6)]
        routes=next_routes
        pastprofit=[x[3] for x in frame]
        stages.append((excess,switches,n))
        tape.append(tuple(next_routes))
    return {'costs':stages,'routes':tape,
            'total_excess':sum(z[0] for z in stages),
            'total_gross':sum(z[1] for z in stages),
            'early_excess':sum(z[0] for z in stages[:10]),
            'late_excess':sum(z[0] for z in stages[-10:]),
            'early_gross':sum(z[1] for z in stages[1:10]),
            'late_gross':sum(z[1] for z in stages[-10:])}


def historical_outcome(rec):
    periods=rec['periods']
    old=None;stages=[]
    for frame in periods:
        curr=[x[0] for x in frame]
        n=sum(curr)
        switches=sum(a!=b for a,b in zip(old,curr)) if old is not None else 0
        stages.append((3*(n-4)**2,switches,n))
        old=curr
    return {k:(sum(x[0] for x in stages) if k=='total_excess' else
               sum(x[1] for x in stages) if k=='total_gross' else
               sum(x[0] for x in stages[:10]) if k=='early_excess' else
               sum(x[0] for x in stages[-10:]) if k=='late_excess' else
               sum(x[1] for x in stages[1:10]) if k=='early_gross' else
               sum(x[1] for x in stages[-10:]))
            for k in ('total_excess','total_gross','early_excess','late_excess',
                      'early_gross','late_gross')}


def fit_folds(source):
    """Each heldout session's λ and private hazards fit ONLY to other sessions."""
    tracks=actor_rows_sealed(source)
    events=load_history_events(source)
    bysession=defaultdict(list);byevents=defaultdict(list)
    for rec in tracks:
        rec['ewa']=ewa_path_differences(rec['periods'])
        bysession[rec['session']].append(rec)
    for e in events:byevents[e['session']].append(e)
    sessions=sorted(bysession)
    if len(sessions)!=24 or sessions!=sorted(byevents):
        raise ValueError('not the approved 24-session source')
    fits={}
    for held in sessions:
        train=[rec for s in sessions if s!=held for rec in bysession[s]]
        legal=legal_training([e for s in sessions if s!=held for e in byevents[s]])
        lam={}
        for trt in (1,2,3):
            x=[];y=[]
            for rec in train:
                if rec['treatment']!=trt:continue
                for t in range(1,40):
                    x.extend(rec['ewa'][t]);y.extend(rec['periods'][t][i][0] for i in range(6))
            lam[trt]=fitted_ewa_lambda(x,y)
        fits[held]={'lambda':lam,'legal':legal}
    return sessions,bysession,fits


def run_experiment(source,*,repetitions=32,seed=20261121,init='observed',
                   shocks='tape',lapse=.02,models=MODELS):
    """Export aggregates only. MC error reflects seed variation, not 24-session inference."""
    if not isinstance(repetitions,int) or repetitions<2:raise ValueError('>=2 MC repetitions')
    sessions,groups,fits=fit_folds(source)
    if len(sessions)!=24 or sum(len(v) for v in groups.values())!=144:
        raise ValueError("R59 source did not yield exactly 24 sessions / 144 group sections")
    model_metrics=defaultdict(lambda:defaultdict(list))
    model_session=defaultdict(lambda:defaultdict(list))
    observed=defaultdict(lambda:defaultdict(list))
    per_group={}
    for sidx,held in enumerate(sessions):
        for gidx,rec in enumerate(groups[held]):
            trt=rec['treatment']
            target=historical_outcome(rec)
            observed[trt]['all'].append(target)
            for midx,model in enumerate(models):
                rep_out=[]
                for rep in range(repetitions):
                    run=simulate(rec,model=model,
                         lambda_ewa=fits[held]['lambda'][trt],
                         trained_legal=fits[held]['legal'],init=init,
                         seed=model_seed(seed,sidx,gidx,midx,rep),
                         lapse=lapse,shocks=shocks)
                    rep_out.append({k:run[k] for k in target})
                pred={k:mean(x[k] for x in rep_out) for k in target}
                err={k:pred[k]-target[k] for k in target}
                # Within-synthetic-draw MC SE of each group predictive mean.
                se={k:sqrt(variance(x[k] for x in rep_out)/repetitions)
                    for k in target}
                model_metrics[model][trt].append({'pred':pred,'err':err,'se':se,
                                                   'target':target})
                model_session[model][held].append((trt,pred,err))
    result={'source':'author-approved SHA-sealed 24 session data',
            'source_sha256':'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953',
            'scope':'40-period generated endogenous routes; observed exogenous value tape is injected only after each simulated decision',
            'init':init,'shocks':shocks,'repetitions_per_group':repetitions,
            'groups':sum(len(v) for v in groups.values()),'sessions':len(sessions),
            'lapse':lapse,'models':{},
            'observed':{str(t):{k:mean(d[k] for d in v['all']) for k in v['all'][0]}
                        for t,v in observed.items()}}
    for model,bytrt in model_metrics.items():
        overall=[x for v in bytrt.values() for x in v]
        def summary(arr):
            metrics=arr[0]['pred']
            return {'group_sections':len(arr),
                    'predicted_mean_per_group':{k:mean(x['pred'][k] for x in arr)
                                                for k in metrics},
                    'mean_group_total_mse':{k:mean(x['err'][k]**2 for x in arr)
                                            for k in metrics},
                    'mean_prediction_bias':{k:mean(x['err'][k] for x in arr)
                                            for k in metrics},
                    'mc_se_over_groups':{k:sqrt(sum(x['se'][k]**2 for x in arr))/len(arr)
                                         for k in metrics},
                    'joint_cost_mse_polynomial':{
                      'A':mean(x['err']['total_excess']**2 for x in arr),
                      'B':2*mean(x['err']['total_excess']*x['err']['total_gross'] for x in arr),
                      'D':mean(x['err']['total_gross']**2 for x in arr)},
                   }
        result['models'][model]={'overall':summary(overall),
            'by_treatment':{str(trt):summary(arr) for trt,arr in bytrt.items()}}
    # Paired *whole-session* resampling. Group sections are clustered within
    # session and are NEVER treated as independent samples for uncertainty.
    from statistics import mean as _mean
    rng=Random(seed+77159)
    contrasts={}
    for alternative, baseline in (('ssm1_9','private_history'),
                                  ('ssm5','private_history'),
                                  ('ewa_lite','private_history'),
                                  ('private_route','private_history')):
        if alternative not in models or baseline not in models:continue
        contrasts[alternative+'--'+baseline]={}
        for estimand in ('total_excess','total_gross','resource_kappa1'):
            session_pairs=[]
            for held in sessions:
                a=model_session[alternative][held];b=model_session[baseline][held]
                if len(a)!=len(b):raise AssertionError('unpaired session predictions')
                delta=0
                for (t1,pa,ea),(t2,pb,eb) in zip(a,b):
                    if t1!=t2:raise AssertionError('mismatched group treatment')
                    if estimand=='resource_kappa1':
                        da=ea['total_excess']+ea['total_gross']
                        db=eb['total_excess']+eb['total_gross']
                    else:
                        da=ea[estimand];db=eb[estimand]
                    delta+=da*da-db*db
                session_pairs.append((delta,len(a)))
            observed_delta=sum(x[0] for x in session_pairs)/sum(x[1] for x in session_pairs)
            count=1500
            draws=[]
            for _ in range(count):
                subset=[session_pairs[rng.randrange(len(sessions))] for _ in sessions]
                draws.append(sum(x[0] for x in subset)/sum(x[1] for x in subset))
            draws.sort()
            contrasts[alternative+'--'+baseline][estimand]={
                'mean_mse_difference':observed_delta,
                'cluster_session_resampling_95_descriptive':[
                    draws[int(.025*count)],draws[int(.975*count)]]}
    result['paired_session_resampling']=contrasts
    # Do not allow matching the pooled total by reversing the actual relative
    # outcomes of the No/Partial/Full experimental arms to go unnoticed.
    treatment_diffs={}
    for alt_trt,base_trt,label in ((3,1,'full_minus_no'),
                                    (2,1,'partial_minus_no'),
                                    (3,2,'full_minus_partial')):
        historical={k:result['observed'][str(alt_trt)][k]-
                       result['observed'][str(base_trt)][k]
                    for k in ('total_excess','total_gross','early_excess','late_excess')}
        compare_models={}
        for model in models:
            generated={k:result['models'][model]['by_treatment'][str(alt_trt)]
                            ['predicted_mean_per_group'][k]-
                           result['models'][model]['by_treatment'][str(base_trt)]
                            ['predicted_mean_per_group'][k]
                       for k in historical}
            session_treat=[]
            for held in sessions:
                rows=model_session[model][held]
                buckets=defaultdict(list)
                for trt,pred,err in rows:buckets[trt].append(err)
                if not buckets[alt_trt] or not buckets[base_trt]:
                    raise AssertionError('session does not contain matched treatment arms')
                session_treat.append(buckets)
            residuals={}
            for metric in historical:
                mean_bias=generated[metric]-historical[metric]
                rng2=Random(seed+5019+alt_trt*17+base_trt*71+sum(map(ord,model))+
                            sum(map(ord,metric)))
                draws=[]
                for _ in range(1500):
                    sample=[session_treat[rng2.randrange(len(sessions))] for _ in sessions]
                    x=[r[metric] for g in sample for r in g[alt_trt]]
                    y=[r[metric] for g in sample for r in g[base_trt]]
                    draws.append(mean(x)-mean(y))
                draws.sort()
                residuals[metric]={'difference_from_observed_treatment_contrast':mean_bias,
                    'session_resampling_95_descriptive':[
                        draws[int(.025*len(draws))],draws[int(.975*len(draws))]]}
            compare_models[model]={'predicted_arm_contrast':generated,
                                   'contrast_error':residuals}
        treatment_diffs[label]={'observed_arm_contrast':historical,
                                'models':compare_models}
    result['treatment_contrasts']=treatment_diffs
    # Full source participant and session identifiers are absent from output.
    return result
