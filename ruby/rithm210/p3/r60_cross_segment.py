"""RITHM P3-R60: source-sealed, actor-linked cross-segment prediction audit.

This file NEVER exports participant-, session- or group-level rows. The only
human-source input is the owner's SHA-256 pinned original ZIP. The scored task
is the next observed *individual* change within subsequent segments 3 and 4,
with the previous segment's choice history and t-1 of the target observed.
This is a descriptive heldout forecast, not causal identification of memory.
"""
from collections import defaultdict
from math import log
from random import Random
from statistics import mean
import json
from r59_prior_exposure import parse_source_section_histories
from r54_original_batch_clock import APPROVED_ZIP_SHA256

SOURCE_NOTE='strict 24-session R54/R59 sample; target sections 3/4, periods 2..40'
STRENGTHS=(5,20,80)
MODELS=('base','other_five_prior','own_prior','current_only','own_prior_plus_current','recent_prior')


def events_from_histories(people):
    """One row per person-period (t>=2 of sections 3/4), private in memory."""
    sessions=sorted({s for s,sec,i in people})
    if len(sessions)!=24: raise ValueError('expected 24 independent sessions')
    events=[]; by_group=defaultdict(list)
    for (s,sec,i),past in people.items():
        if sec not in (2,3,4):raise ValueError('invalid source section')
        if sec==2:continue
        earlier=people.get((s,sec-1,i))
        if earlier is None:raise ValueError('no matched earlier participant')
        previous_flips=[int(earlier[t][0]!=earlier[t-1][0]) for t in range(2,41)]
        own_count=sum(previous_flips)
        recent_count=sum(previous_flips[-10:])
        g=past[1][3]
        if any(past[t][3]!=g for t in range(1,41)) or earlier[40][3]!=g:
            raise ValueError('actor group changed')
        # This is the *other five* previous-section count: no identity self-leak.
        other=[]
        for (ss,previous_sec,otherid),hist in people.items():
            if ss==s and previous_sec==sec-1 and otherid!=i and hist[1][3]==g:
                other.append(sum(hist[t][0]!=hist[t-1][0] for t in range(2,41)))
        if len(other)!=5:raise ValueError('not five same-group peers')
        info=past[1][1];trt=past[1][2]
        current_count=0
        for t in range(2,41):
            prior=past[t-1][0]
            flip=int(prior!=past[t][0])
            e={'session':s,'section':sec,'group':g,'period':t,'actor':i,
               'treatment':trt,'info':info,'info_changed':int(earlier[40][1]!=info),
               'previous_route':prior,'prior_terminal_route':earlier[40][0],
               'target_initial_route':past[1][0], 'flip':flip,
               'own_count':own_count,'recent_count':recent_count,'other_count':sum(other),
               'current_count':current_count,'current_exposure':t-2}
            events.append(e)
            by_group[(s,sec,g,t)].append(e)
            current_count+=flip
    if len(events)!=576*39 or len(by_group)!=96*39:
        raise ValueError(f'incorrect source-derived target support {len(events)} {len(by_group)}')
    if any(len(x)!=6 for x in by_group.values()):raise ValueError('bad group size')
    return events,by_group


def fit_training_base(events,held):
    """No test-session rows in base; fallback and local bins are beta(.5,.5)."""
    cnt=defaultdict(lambda:[0,0])
    for e in events:
        if e['session']==held:continue
        keys=[(),(e['treatment'],),(e['treatment'],e['info']),
              (e['treatment'],e['info'],e['previous_route'])]
        for key in keys:
            cnt[key][0]+=e['flip'];cnt[key][1]+=1
    if not cnt[()][1]:raise ValueError('empty training fold')
    return cnt


def pbase(e,model):
    key=(e['treatment'],e['info'],e['previous_route'])
    if key not in model or model[key][1]<5:
        key=(e['treatment'],e['info'])
    flip,n=model[key]
    return (flip+.5)/(n+1)


def prob(e,fit,name,strength=20):
    if name not in MODELS:raise ValueError('unregistered alternative')
    if type(strength) is not int or strength<=0:raise ValueError('invalid shrink')
    base=pbase(e,fit)
    if name=='base':return base
    if name=='other_five_prior':c,n=e['other_count'],195
    elif name=='own_prior':c,n=e['own_count'],39
    elif name=='current_only':c,n=e['current_count'],e['current_exposure']
    elif name=='own_prior_plus_current':c,n=e['own_count']+e['current_count'],39+e['current_exposure']
    elif name=='recent_prior':c,n=e['recent_count'],10
    else:raise AssertionError('should not reach')
    p=(c+strength*base)/(n+strength)
    if not 0<p<1:raise AssertionError('smoothed rate outside open probability interval')
    return p


def poisson_binomial(ps):
    coeff=[1.]
    for p in ps:
        new=[0.]*(len(coeff)+1)
        for k,m in enumerate(coeff):
            new[k]+=(1-p)*m;new[k+1]+=p*m
        coeff=new
    return coeff


def group_flow_law(g,ps):
    if len(g)!=6 or len(ps)!=6:raise ValueError('not a six-actor group')
    ps_u=[p for e,p in zip(g,ps) if not e['previous_route']]
    ps_d=[p for e,p in zip(g,ps) if e['previous_route']]
    u=poisson_binomial(ps_u);d=poisson_binomial(ps_d)
    return {(a,b):u[a]*d[b] for a in range(len(u)) for b in range(len(d))}


def score_events(events,*,strength=20,test_periods=None):
    bysession=defaultdict(list)
    for e in events:bysession[e['session']].append(e)
    sessions=sorted(bysession)
    if len(sessions)!=24:raise ValueError('expected 24 heldout sessions')
    loss={s:{name:[0.,0,0.,0] for name in MODELS} for s in sessions}
    # [person logloss sum, person Brier sum, group joint logloss sum, group count]
    for s in sessions:
        train=fit_training_base(events,s)
        group=defaultdict(list)
        for e in bysession[s]:
            if test_periods is None or e['period'] in test_periods:
                group[(e['section'],e['group'],e['period'])].append(e)
        for g in group.values():
            for name in MODELS:
                ps=[prob(e,train,name,strength) for e in g]
                personloss=sum(-log(p) if e['flip'] else -log(1-p) for e,p in zip(g,ps))
                personbrier=sum((p-e['flip'])**2 for e,p in zip(g,ps))
                law=group_flow_law(g,ps)
                outcome=(sum(e['flip'] for e in g if not e['previous_route']),
                         sum(e['flip'] for e in g if e['previous_route']))
                q=law[outcome]
                if q<=0:raise ValueError('group impossible under fitted law')
                acc=loss[s][name];acc[0]+=personloss;acc[1]+=personbrier;acc[2]+=-log(q);acc[3]+=1
        if len(group)!=(sum(1 for e in bysession[s] if test_periods is None or e['period'] in test_periods)/6):
            raise AssertionError('invalid event aggregation')
    totals={}
    for name in MODELS:
        totals[name]={
            'equal_session_actor_logloss':mean(loss[s][name][0]/(loss[s][name][3]*6) for s in sessions),
            'equal_session_actor_brier':mean(loss[s][name][1]/(loss[s][name][3]*6) for s in sessions),
            'equal_session_group_joint_logloss':mean(loss[s][name][2]/loss[s][name][3] for s in sessions),
            'pooled_actor_logloss':sum(loss[s][name][0] for s in sessions)/(6*sum(loss[s][name][3] for s in sessions)),
        }
    return totals,loss


def actor_info_status_scores(events,*,strength=20):
    """Actor-level, since filtering half of a group would invalidate (U,D)."""
    bysession=defaultdict(list)
    for e in events:bysession[e['session']].append(e)
    report={}
    for changed in (0,1):
        per_session=[]
        for session in sorted(bysession):
            fitted=fit_training_base(events,session)
            selected=[e for e in bysession[session] if e['info_changed']==changed]
            if not selected:raise ValueError('missing information-change cohort')
            rates={name:mean(-log(prob(e,fitted,name,strength)) if e['flip'] else
                                  -log(1-prob(e,fitted,name,strength)) for e in selected)
                   for name in MODELS}
            per_session.append(rates)
        report['changed' if changed else 'unchanged']={name:mean(x[name] for x in per_session)
                                                     for name in MODELS}
    return report


def percentile(x,lo=.025,hi=.975):
    y=sorted(x);return [y[int(len(y)*lo)],y[min(len(y)-1,int(len(y)*hi))]]


def _bootstrap_diffs(loss,reps,seed,reference="base"):
    if reference not in MODELS:raise ValueError("bad comparator")
    rng=Random(seed);sessions=sorted(loss);out={}
    for name in MODELS:
        if name==reference:continue
        out[name]={}
        for label,i,k in [('actor_logloss',0,6),('group_logloss',2,1)]:
            diff=[(loss[s][name][i]-loss[s][reference][i])/(loss[s][name][3]*k) for s in sessions]
            draws=[mean(diff[rng.randrange(len(sessions))] for _ in sessions) for _ in range(reps)]
            out[name][label]={'point':mean(diff),'session_resampling_95_descriptive':percentile(draws)}
    return out


def run(source,*,strengths=STRENGTHS,bootstrap=2000):
    people=parse_source_section_histories(source)
    events,_=events_from_histories(people)
    primary,loss=score_events(events,strength=20)
    sensitivity={str(k):score_events(events,strength=k)[0] for k in strengths if k!=20}
    return {'version':'R60.1','source_note':SOURCE_NOTE,'sessions':24,'original_zip_sha256':APPROVED_ZIP_SHA256,
            'linked_actor_section_pairs':576,'target_actor_decisions':len(events),
            'target_group_transitions':len(events)//6,
            'training_policy':'heldout whole session, 23 other sessions for p_base; past section actor and 5 peer histories precede next section; no t+ actor outcomes in features',
            'primary_strength':20,'model_scores':primary,
            'base_contrasts':_bootstrap_diffs(loss,bootstrap,20261121),
            'shrinkage_sensitivity':sensitivity,
            'against_current_only':_bootstrap_diffs(loss,bootstrap,20261122,reference='current_only'),
            'time_strata':{label:score_events(events,strength=20,test_periods=range(a,b+1))[0] for label,a,b in [('early_2_6',2,6),('middle_7_20',7,20),('late_21_40',21,40)]},
            'information_status_changed_scores':actor_info_status_scores(events,strength=20),
            'early_late_paired_compared_to_current':{label:_bootstrap_diffs(score_events(events,strength=20,test_periods=range(a,b+1))[1],bootstrap,20261123,reference='current_only') for label,a,b in [('early_2_6',2,6),('late_21_40',21,40)]},
            'caveats':'Retrospective descriptive conditional one-step actor and joint-flow forecasts. Full prior section record, no hidden or future target choices. NOT proof of individual inertia or cross-section learning causation. Exploratory repeated comparisons.'}


if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r60_cross_segment.py APPROVED_PRIVATE_ORIGINAL.zip')
    print(json.dumps(run(sys.argv[1]),indent=2,sort_keys=True))
