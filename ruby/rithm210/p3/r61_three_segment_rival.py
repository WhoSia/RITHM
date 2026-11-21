"""RITHM R61: three-segment exact mechanism separation and source descriptive lag audit.

A two-segment binary summary permits fixed hidden type and a Markov history
mechanism to match exactly; one more conditionally observed segment distinguishes
these *specified* rivals in principle. Historical 3-segment correlations are
shown separately and cannot causally identify either rival under changing arms.
"""
from collections import defaultdict
from fractions import Fraction as F
from random import Random
from statistics import mean
from math import sqrt
from r59_prior_exposure import parse_source_section_histories


def type_3_law():
    res={}
    for a in (0,1):
      for b in (0,1):
       for c in (0,1):
        # Hidden p selects the frequency of 1, fixed across all three sections.
        res[a,b,c]=sum(F(1,2)*(p if a else 1-p)*(p if b else 1-p)*(p if c else 1-p)
                       for p in (F(1,5),F(4,5)))
    return res


def markov_3_law():
    stay=F(17,25)
    return {(a,b,c):F(1,2)*(stay if a==b else 1-stay)*(stay if b==c else 1-stay)
            for a in (0,1) for b in (0,1) for c in (0,1)}


def exact_separation():
    typ=type_3_law();history=markov_3_law()
    def pair(law,i,j):
        out=defaultdict(F)
        for bits,p in law.items():out[bits[i],bits[j]]+=p
        return dict(out)
    if pair(typ,0,1)!=pair(history,0,1) or pair(typ,1,2)!=pair(history,1,2):
        raise AssertionError('two-adjacent-pair calibration mismatch')
    expected_static={ (0,0):F(17,50),(0,1):F(4,25),
                      (1,0):F(4,25),(1,1):F(17,50)}
    if pair(typ,0,1)!=expected_static:raise AssertionError('wrong R60 two-step law')
    def p_equal(law,i,j):return sum(p for bits,p in law.items() if bits[i]==bits[j])
    return {'same_adjacent_pair_law':{str(k):str(v) for k,v in sorted(expected_static.items())},
            'p_first_equals_third_fixed_type':str(p_equal(typ,0,2)),
            'p_first_equals_third_markov_learning':str(p_equal(history,0,2)),
            'p_all_three_equal_fixed_type':str(typ[0,0,0]+typ[1,1,1]),
            'p_all_three_equal_markov_learning':str(history[0,0,0]+history[1,1,1]),
            'total_variation_full_three_joint':str(sum(abs(typ[k]-history[k]) for k in typ)/2),
            'domain':'only three binary summary outcomes, NOT causal mechanism proof on full human choices'}


def descriptive_three_sections(people,*,reps=4000,seed=20261121):
    lines=[]
    subjects=defaultdict(dict)
    for (s,sec,actor),periods in people.items():
        if sec not in (2,3,4):raise ValueError('unsupported section')
        subjects[s,actor][sec]=sum(periods[t][0]!=periods[t-1][0] for t in range(2,41))/39
    if len(subjects)!=288:raise ValueError('expected 288 full triple actor histories')
    for (s,actor),by in subjects.items():
        if sorted(by)!=[2,3,4]:raise ValueError('broken triple')
        lines.append((s,by[2],by[3],by[4]))
    def corr(data,i,j):
        n=len(data);a=[x[i] for x in data];b=[x[j] for x in data]
        mean_a=sum(a)/n;mean_b=sum(b)/n
        cov=sum((u-mean_a)*(v-mean_b) for u,v in zip(a,b))
        sa=sum((u-mean_a)**2 for u in a);sb=sum((v-mean_b)**2 for v in b)
        if sa*sb<=0:raise ValueError('degenerate original triple correlation')
        return cov/sqrt(sa*sb)
    sessions=sorted({row[0] for row in lines})
    by_session={s:[e for e in lines if e[0]==s] for s in sessions}
    rng=Random(seed)
    observed={'2_3':corr(lines,1,2),'3_4':corr(lines,2,3),'2_4':corr(lines,1,3)}
    draws={name:[] for name in observed}
    for _ in range(reps):
        chosen=[s for _ in sessions for s in [sessions[rng.randrange(len(sessions))]]]
        d=[x for s in chosen for x in by_session[s]]
        for label,(i,j) in {'2_3':(1,2),'3_4':(2,3),'2_4':(1,3)}.items():draws[label].append(corr(d,i,j))
    return {'sessions':len(sessions),'participant_triples':len(lines),
            'mean_switch_frequency_by_segment':{str(sec):mean(x[i] for x in lines) for i,sec in enumerate([2,3,4],1)},
            'pairwise_pearson':observed,
            'session_resampling_95_descriptive':{k:[sorted(v)[int(.025*reps)],sorted(v)[int(.975*reps)]] for k,v in draws.items()},
            'causal_warning':'Treatments vary across segments and previous observations affect the later baseline; correlation is not identification of persistent type or learned carryover.'}


if __name__=='__main__':
    import json,sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r61_three_segment_rival.py PRIVATE_APPROVED_ZIP')
    data=parse_source_section_histories(sys.argv[1]);out={'synthetic_exact':exact_separation(),'original_descriptive':descriptive_three_sections(data)}
    print(json.dumps(out,indent=2,sort_keys=True))
