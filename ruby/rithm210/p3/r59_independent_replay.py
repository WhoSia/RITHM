"""Independent un-enriched CSV replay of R59's 24-session source cohort.

The author ZIP contains an *extra* 20-period session-1 pilot in the un-enriched
CSV but not the enriched switch CSV. An independent verifier must require that
exact population intersection instead of claiming every original file has the
same selection. No private rows or ids are returned to the caller.
"""
import csv
from collections import defaultdict
from io import StringIO
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256

from r54_original_batch_clock import APPROVED_ZIP_SHA256

BASE='data_task_all_230705.csv'
ENRICH='data_task_all_switch_230705.csv'
COMMON=('session','section','trt','Period','ID','Group','Informed','Value',
        'Cost','RouteA','RouteB','NumA','NumB','profit')


def _selection(row):
    return (int(row['trt']) in (1,2,3) and
            int(row['session']) not in (2,101) and
            int(row['section']) in (2,3,4) and
            int(row['Period'])>=1)


def _key(row):return tuple(row[k] for k in ('session','section','Period','ID'))


def source_parity_aggregate(path):
    if sha256(Path(path).read_bytes()).hexdigest()!=APPROVED_ZIP_SHA256:
        raise ValueError('wrong approved author ZIP raw SHA256')
    with ZipFile(path) as z:
        if BASE not in z.namelist() or ENRICH not in z.namelist():
            raise ValueError('missing independent source tables')
        one=[r for r in csv.DictReader(StringIO(z.read(BASE).decode('utf-8-sig')))
             if _selection(r)]
        two=[r for r in csv.DictReader(StringIO(z.read(ENRICH).decode('utf-8-sig')))
             if _selection(r)]
    supported={int(r['session']) for r in two}
    original=[r for r in one if int(r['session']) in supported]
    omitted=[r for r in one if int(r['session']) not in supported]
    if len(two)!=34560 or len(original)!=34560 or len(omitted)!=360:
        raise ValueError('un-enriched and enriched source population disagreement')
    a={_key(r):r for r in original}
    b={_key(r):r for r in two}
    if len(a)!=len(original) or len(b)!=len(two) or set(a)!=set(b):
        raise ValueError('original actor-period identities differ across source variants')
    if any(any(a[k][field]!=b[k][field] for field in COMMON) for k in a):
        raise ValueError('source column-level parity mismatch')
    participants=defaultdict(dict)
    gross=0
    for r in original:
        key=(int(r['session']),int(r['section']),int(r['ID']))
        t=int(r['Period'])
        if t in participants[key]:raise ValueError('duplicate original actor-period')
        participants[key][t]=(int(r['RouteA']),int(r['Group']))
    for hist in participants.values():
        if sorted(hist)!=list(range(1,41)):
            raise ValueError('not 40 periods for original retained actor')
        gross+=sum(hist[t][0]!=hist[t-1][0] for t in range(2,41))
    if gross!=8909:raise ValueError('original raw 8,909 gross switches mismatch')
    actorlinks=0;group_changes=0
    for (s,section,actor),hist in participants.items():
        if section not in (2,3):continue
        partner=participants.get((s,section+1,actor))
        if partner is None:raise ValueError('actor not carried into next section')
        actorlinks+=1
        group_changes+=int(hist[40][1]!=partner[1][1])
    if actorlinks!=576 or group_changes:
        raise ValueError('original group or person roster mismatch across sections')
    # All outputs are cohort-level aggregates. No identifying fields disclosed.
    return {'source_sha256':APPROVED_ZIP_SHA256,
            'un_enriched_preintersection_rows':len(one),
            'un_enriched_extra_20_period_pilot_rows':len(omitted),
            'selected_enriched_40_period_rows':len(two),
            'identical_common_cells':len(two)*len(COMMON),
            'un_enriched_actor_gross_switches':gross,
            'adjacent_section_matched_person_links':actorlinks,
            'cross_section_group_changes':group_changes,
            'selection_warning':(
               'Un-enriched table includes an additional 20-period pilot '+
               'session; R59 follows the 24-session enriched analysis cohort. No '+
               'unreported original table is equivalent by default.'),
           }


if __name__=='__main__':
    import json,sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r59_independent_replay.py original.zip')
    print(json.dumps(source_parity_aggregate(sys.argv[1]),indent=2,sort_keys=True))
