"""Independent source-side R55 aggregate verifier (no participant-level output)."""
import argparse
import csv
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

EXPECTED_SHA = 'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'


def independently_count(source_zip):
    raw=Path(source_zip).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:
        raise ValueError('source SHA256 mismatch')
    group_states=defaultdict(dict)
    with ZipFile(io.BytesIO(raw)) as z:
        reader=csv.DictReader(io.TextIOWrapper(z.open('data_task_all_switch_230705.csv'), encoding='utf-8-sig'))
        for row in reader:
            sess,trt,period=(int(row[x]) for x in ('session','trt','Period'))
            if sess in (2,101) or trt not in (1,2,3) or period<1:
                continue
            key=(sess,int(row['section']),trt,int(row['Group']))
            state=group_states[key].setdefault(period,{'seen':set(),'routeA':set(), 'numA':set(),'numB':set(),'costs':[], 'numSwitch':set()})
            ident=int(row['ID'])
            if ident in state['seen']:
                raise ValueError('duplicate actor in verifier')
            state['seen'].add(ident)
            if int(row['RouteA']):
                state['routeA'].add(ident)
            state['numA'].add(int(row['NumA']))
            state['numB'].add(int(row['NumB']))
            state['costs'].append(Fraction(row['Cost']))
            state['numSwitch'].add(int(row['NumSwitch']))
    total=Counter()
    arms=defaultdict(Counter)
    uniform_expectation=Fraction()
    for (sess,sect,trt,group),periods in group_states.items():
        previous=None
        counts=Counter(group_sections=1)
        previous_n=None
        for t in sorted(periods):
            data=periods[t]
            n=len(data['routeA'])
            if len(data['seen'])!=6 or data['numA']!={n} or data['numB']!={6-n}:
                raise ValueError('inconsistent period states')
            currentcost=n*n+2*(6-n)**2
            if sum(data['costs'])!=currentcost:
                raise ValueError('cost not physical')
            counts['periods']+=1
            counts['congestion_excess']+=currentcost-24
            if previous is not None:
                g=len(previous ^ data['routeA'])
                if data['numSwitch']!={g}:
                    raise ValueError('switch mismatch')
                a=len(previous)
                low=abs(n-a)
                high=min(a+n,12-a-n)
                exp=Fraction(a*(6-n)+(6-a)*n,6)
                counts['transitions']+=1
                counts['gross']+=g
                counts['minimum']+=low
                counts['maximum']+=high
                counts['extra_gross']+=g-low
                counts['excess_pairs']+=(g-low)//2
                counts['uniform_numerator']+=6*exp
                counts['fiber_ambiguous']+=int(low<high)
                if a==n==4:
                    counts['four_to_four_'+str(g)]+=1
            previous=data['routeA']
            previous_n=n
        total.update(counts)
        arms[trt].update(counts)
    return {'total':dict(total),'treatments':{str(k):dict(v) for k,v in arms.items()},'groups':len(group_states)}


def verify_against_result(original_zip,aggregate_json):
    independent=independently_count(original_zip)
    observed=json.loads(Path(aggregate_json).read_text(encoding='utf-8'))
    mapping={'gross':'observed_actor_changes', 'minimum':'minimum_given_occupancy',
             'maximum':'maximum_given_occupancy', 'extra_gross':'extra_beyond_occupancy_minimum',
             'excess_pairs':'extra_cancelling_pairs',
             'fiber_ambiguous':'transitions_with_multiple_feasible_gross_counts'}
    for key,field in mapping.items():
        if independent['total'][key] != observed['switches'][field]:
            raise ArithmeticError('aggregate metric divergence: '+key)
    if independent['groups'] != observed['population']['group_sections']:
        raise ArithmeticError('group-section population divergence')
    for treat, counts in independent['treatments'].items():
        arm=observed['treatments'][treat]
        for key, field in [('gross','gross_switches_39_transitions'),
                           ('minimum','occupancy_minimum'),
                           ('extra_gross','extra_switches'),
                           ('excess_pairs','opposing_direction_pairs'),
                           ('congestion_excess','congestion_excess_40_periods')]:
            if counts[key]!=arm[field]:
                raise ArithmeticError(f'arm aggregate divergence {treat}.{key}')
    return {'independent_source_verified':True, 'sealed_source':True,
            'source_row_leak':False, 'compared_transition_count':independent['total']['transitions'],
            'group_sections':independent['groups'], 'arm_aggregate_matches':True}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip',type=Path)
    p.add_argument('aggregate_json',type=Path)
    args=p.parse_args()
    print(json.dumps(verify_against_result(args.original_zip,args.aggregate_json),sort_keys=True))
