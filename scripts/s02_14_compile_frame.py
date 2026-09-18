#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET
import hashlib, json, math, collections, argparse

BEGIN=14400.0
END=50400.0
FILES=[
    ('bus','most.buses.flows.xml',False),
    ('commercial','most.commercial.rou.xml',True),
    ('highway','most.highway.flows.xml',True),
    ('pedestrian','most.pedestrian.rou.xml',True),
    ('special','most.special.rou.xml',True),
    ('train','most.trains.flows.xml',False),
]
EXPECTED_FAMILY={'bus':960,'commercial':3500,'highway':1560,'pedestrian':39262,'special':1500,'train':60}
EXPECTED_ALL_N=46842
EXPECTED_ELIGIBLE_N=45822
EXPECTED_SHA={
    'frame':'ad718af789d1402b2d809bbf0c0fa2b5786c71675a4c81ebf91bcd03a957022d',
    'eligible':'e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293',
    'p000':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    'p030':'1b9fba0675825b770afe24159fc39c4ba12b6f78fa05e432d77ad8e7556f83f5',
    'p070':'f4855d4965e9d7268f97a2d0c90f11b4d9632cd6cd8d22ff2d15ed4804cd9270',
    'p100':'21d0db278e7c39d9403520b10ab471470a03c30cd908c587677a1d5249f8f634',
}

def ffloat(v):
    try:
        return float(v)
    except Exception:
        return None

def in_window(x):
    return x is not None and BEGIN <= x < END

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--demand-dir',default='demand')
    ap.add_argument('--out-dir',default='seal')
    args=ap.parse_args()
    demand=Path(args.demand_dir)
    out=Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)

    report={
        'seal':'S02.14 SOURCE-ONLY FRAME RECONSTRUCTION FOR E3',
        'most_commit':'b29b2f65f1096a9c69a601ec62a724815cb4a43f',
        'window':[BEGIN,END],
        'target_outcome_read':False,
        'historical_result_artifacts_read':False,
        'source_files':{},
        'frame':{},
    }
    all_entries=[]
    unsupported=[]

    for family,fn,treat_eligible in FILES:
        p=demand/fn
        counts=collections.Counter()
        flow_attrsets=collections.Counter()
        flows=[]
        numeric=[]
        triggered=[]
        person_depart={}
        depart_tokens=collections.Counter()
        samples=[]

        for _,e in ET.iterparse(p,events=('end',)):
            tag=e.tag.split('}')[-1]
            if tag in {'vehicle','trip','flow','person','personFlow'}:
                counts[tag]+=1
            if tag=='person':
                pid=e.attrib.get('id','')
                dep=ffloat(e.attrib.get('depart'))
                if pid and dep is not None:
                    person_depart[pid]=dep
                if len(samples)<12:
                    samples.append({'tag':tag,**dict(e.attrib)})
            elif tag in {'vehicle','trip'}:
                vid=e.attrib.get('id','')
                rawdep=e.attrib.get('depart')
                dep=ffloat(rawdep)
                depart_tokens[str(rawdep)]+=1
                if len(samples)<12:
                    samples.append({'tag':tag,**dict(e.attrib)})
                if dep is not None:
                    if in_window(dep):
                        numeric.append((vid,dep,e.attrib.get('type',''),tag,'numeric-depart'))
                elif rawdep=='triggered':
                    triggered.append((vid,e.attrib.get('type',''),tag))
                else:
                    unsupported.append([fn,tag,vid,'unsupported-depart',rawdep])
            elif tag=='flow':
                a=dict(e.attrib)
                flow_attrsets[tuple(sorted(a.keys()))]+=1
                flows.append(a)
            e.clear()

        entries=[]
        for vid,dep,vtype,kind,clock in numeric:
            if not vid:
                unsupported.append([fn,kind,'missing-id'])
            else:
                entries.append({
                    'id':vid,'activation_time':dep,'family':family,
                    'source_kind':kind,'clock':clock,'vtype':vtype
                })

        triggered_linked=0
        triggered_outside=0
        for vid,vtype,kind in triggered:
            if family!='pedestrian':
                unsupported.append([fn,kind,vid,'triggered-outside-pedestrian-family'])
                continue
            if not vid.endswith('_tr'):
                unsupported.append([fn,kind,vid,'triggered-id-without-_tr'])
                continue
            pid=vid[:-3]
            if pid not in person_depart:
                unsupported.append([fn,kind,vid,'missing-corresponding-person',pid])
                continue
            dep=person_depart[pid]
            triggered_linked+=1
            if in_window(dep):
                entries.append({
                    'id':vid,'activation_time':dep,'family':family,
                    'source_kind':'vehicle-triggered-by-person',
                    'clock':'linked-person-depart','vtype':vtype
                })
            else:
                triggered_outside+=1

        flow_summary=[]
        for a in flows:
            fid=a.get('id','')
            begin=ffloat(a.get('begin'))
            end=ffloat(a.get('end'))
            period=ffloat(a.get('period'))
            number=a.get('number')
            probability=a.get('probability')
            vehsph=a.get('vehsPerHour')
            flow_summary.append({
                'id':fid,'begin':begin,'end':end,'period':period,
                'number':number,'probability':probability,
                'vehsPerHour':vehsph,'type':a.get('type','')
            })
            if period is None or begin is None or end is None or number is not None or probability is not None or vehsph is not None:
                unsupported.append([
                    fn,'flow',fid,
                    {'begin':begin,'end':end,'period':period,'number':number,
                     'probability':probability,'vehsPerHour':vehsph}
                ])
                continue
            k=0
            dep=begin
            while dep < end and dep < END:
                if dep >= BEGIN:
                    entries.append({
                        'id':f'{fid}.{k}','activation_time':dep,'family':family,
                        'source_kind':'flow-period','clock':'scheduled-flow-depart',
                        'vtype':a.get('type','')
                    })
                k+=1
                dep=begin+k*period

        ids=[x['id'] for x in entries]
        dup=[x for x,c in collections.Counter(ids).items() if c>1]
        if dup:
            unsupported.append([fn,'duplicate-ids',dup[:20],len(dup)])

        report['source_files'][fn]={
            'family':family,
            'eligible_for_treatment':treat_eligible,
            'tag_counts':dict(counts),
            'flow_attribute_sets':{','.join(k):v for k,v in flow_attrsets.items()},
            'flow_summaries':flow_summary,
            'compiled_n':len(entries),
            'numeric_vehicle_trip_n':len(numeric),
            'triggered_vehicle_n':len(triggered),
            'triggered_linked_n':triggered_linked,
            'triggered_linked_outside_window_n':triggered_outside,
            'person_numeric_depart_n':len(person_depart),
            'duplicate_id_n':len(dup),
            'depart_token_top':depart_tokens.most_common(12),
            'sample_attrs':samples,
        }
        all_entries.extend(entries)

    eligible_entries=[x for x in all_entries if x['family'] in {'commercial','highway','pedestrian','special'}]
    background_entries=[x for x in all_entries if x['family'] in {'bus','train'}]
    elig_ids=sorted(x['id'] for x in eligible_entries)
    all_ids=sorted(x['id'] for x in all_entries)

    if len(elig_ids)!=len(set(elig_ids)):
        unsupported.append(['eligible','duplicate-id'])
    if len(all_ids)!=len(set(all_ids)):
        unsupported.append(['all','duplicate-id'])

    ped=report['source_files']['most.pedestrian.rou.xml']
    if ped['triggered_vehicle_n'] != 39262 or ped['triggered_linked_n'] != 39262 or ped['triggered_linked_outside_window_n'] != 0:
        unsupported.append([
            'pedestrian-linkage-count-mismatch',
            ped['triggered_vehicle_n'],ped['triggered_linked_n'],
            ped['triggered_linked_outside_window_n']
        ])

    family_counts=dict(collections.Counter(x['family'] for x in all_entries))
    if family_counts != EXPECTED_FAMILY:
        unsupported.append(['family-count-mismatch',family_counts,EXPECTED_FAMILY])
    if len(all_entries) != EXPECTED_ALL_N:
        unsupported.append(['all-frame-count-mismatch',len(all_entries),EXPECTED_ALL_N])
    if len(eligible_entries) != EXPECTED_ELIGIBLE_N:
        unsupported.append(['eligible-frame-count-mismatch',len(eligible_entries),EXPECTED_ELIGIBLE_N])

    ranked=sorted(
        elig_ids,
        key=lambda v:(hashlib.sha256(('RITHM-S02.14|'+v).encode()).hexdigest(),v)
    )
    n=len(ranked)
    cohorts={
        'p000':[],
        'p030':ranked[:math.floor(.30*n)],
        'p070':ranked[:math.floor(.70*n)],
        'p100':ranked,
    }
    assert set(cohorts['p030']) <= set(cohorts['p070']) <= set(cohorts['p100'])
    assert [len(cohorts[k]) for k in ['p000','p030','p070','p100']] == [0,13746,32075,45822]

    order=lambda z:(z['activation_time'],z['id'])
    def row(x):
        return f"{x['id']}\t{x['activation_time']:.3f}\t{x['family']}\t{x['source_kind']}\t{x['clock']}\t{x['vtype']}"

    frame_path=out/'s02-14-demand-frame.tsv'
    eligible_path=out/'s02-14-eligible-frame.tsv'
    frame_path.write_text(
        'id\tactivation_time\tfamily\tsource_kind\tclock\tvtype\n'
        +'\n'.join(row(x) for x in sorted(all_entries,key=order))+'\n'
    )
    eligible_path.write_text(
        'id\tactivation_time\tfamily\tsource_kind\tclock\tvtype\n'
        +'\n'.join(row(x) for x in sorted(eligible_entries,key=order))+'\n'
    )
    cohort_paths={}
    for k,v in cohorts.items():
        cp=out/f's02-14-{k}-explicit.txt'
        cp.write_text('\n'.join(v)+('\n' if v else ''))
        cohort_paths[k]=cp

    hashes={
        'frame':sha(frame_path),
        'eligible':sha(eligible_path),
        **{k:sha(p) for k,p in cohort_paths.items()}
    }
    mismatches={k:{'actual':hashes[k],'expected':EXPECTED_SHA[k]} for k in EXPECTED_SHA if hashes[k]!=EXPECTED_SHA[k]}
    if mismatches:
        unsupported.append(['frozen-hash-mismatch',mismatches])

    report['frame']={
        'all_n':len(all_entries),
        'eligible_n':len(eligible_entries),
        'background_n':len(background_entries),
        'family_counts':family_counts,
        'compiler_rule':'exact source bytes only; numeric vehicle/trip depart; deterministic period-flow expansion; triggered pedestrian-linked vehicle ID *_tr inherits corresponding person ID numeric depart as ex-ante activation clock',
        'activation_clock_semantics':'demand activation clock, not realized vehicle insertion time',
        'eligibility_rule':'commercial|highway|pedestrian-linked|special eligible; bus|train background-only',
        'unsupported_constructs':unsupported,
        'hashes':hashes,
        'expected_hashes':EXPECTED_SHA,
        'cohort_sizes':{k:len(v) for k,v in cohorts.items()},
        'nested_exact':True,
        'ranking_rule':'ascending SHA256("RITHM-S02.14|" + vehicleID), tie vehicleID; first floor(.30N), first floor(.70N), all N',
    }
    report['admission']='PASS-STATIC-COMPILER' if not unsupported else 'HOLD-UNSUPPORTED-OR-HASH-MISMATCH'
    (out/'s02-14-frame-reconstruction.json').write_text(json.dumps(report,indent=2,sort_keys=True))
    print(json.dumps(report,indent=2,sort_keys=True))
    if unsupported:
        raise SystemExit(2)

if __name__=='__main__':
    main()
