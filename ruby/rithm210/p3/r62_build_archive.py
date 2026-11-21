"""Deterministic R62 source-free research reproducer with strict public allowlist.

No human original, original CSV, per-person route paths, or Value tape included.
"""
from pathlib import Path
import hashlib, json, zipfile

HERE=Path(__file__).resolve().parent
R61=HERE.parent/'rithm_r61'
MEMBERS=[
 'RITHM_R62_20261121.md','REPRODUCE_R62.md','requirements-r62.txt',
 'r62_collective.py','r62_batch.py','r62_exact_fiber.py','r62_rollout.py',
 'r62_statecal.py','r62_legal_feedback.py','r62_legal_joint.py',
 'r62_legal_rollout.py','r62_legal_rollout_run.py','r62_legal_run.py',
 'r62_rollout_run.py','r62_run.py','r62_build_archive.py',
 'test_r62_exact.py','test_r62_batch.py','test_r62_rollout.py',
 'test_r62_legal.py','test_r62_result_contract.py',
 'r62_one_step_results.json','r62_legal_one_step_results.json',
 'r62_rollout_observed.json','r62_rollout_fair.json','r62_rollout_seed2.json',
 'r62_legal_rollout_observed.json','r62_legal_rollout_fair.json',
 'r62_legal_rollout_seed2.json'
]
R61_PREREQS=['r54_original_batch_clock.py','r59_prior_exposure.py',
             'r60_cross_segment.py','r61_adaptive_prior.py','r61_closed_loop.py']
SOURCE_HASH='e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'

def build(dest):
    files={}
    for name in MEMBERS:
        if name in files:raise AssertionError('duplicate')
        files[name]=(HERE/name).read_bytes()
    for name in R61_PREREQS:
        if name in files:raise AssertionError('duplicate prior dependency')
        files[name]=(R61/name).read_bytes()
    if any(x.endswith('.csv') or x.lower().endswith('.zip') or 'value_tape' in x.lower() or 'original_human' in x.lower() for x in files):
        raise ValueError('forbidden original human source')
    manifest={'version':'R62.0','publication':'source-free reproducibility and aggregate human outcomes only',
             'original_author_approved_zip_sha256_NOT_INCLUDED':SOURCE_HASH,
             'members':{name:{'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
                        for name,value in sorted(files.items())},
             'restricted_original_human_source_included':False,
             'original_per_person_records_included':False}
    files['R62_SHA256_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode('utf8')
    dest=Path(dest)
    with zipfile.ZipFile(dest,'w') as archive:
        for name in sorted(files):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644<<16)
            archive.writestr(info,files[name],compresslevel=9)
    sha=hashlib.sha256(dest.read_bytes()).hexdigest()
    assert zipfile.ZipFile(dest).testzip() is None
    return manifest,len(files),sha

if __name__=='__main__':
    import sys
    dest=Path(sys.argv[1]) if len(sys.argv)>1 else HERE.parent/'RITHM_R62_20261121_REPRODUCER.zip'
    m,n,s=build(dest)
    (HERE/'R62_SHA256_MANIFEST.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'archive':str(dest),'members':n,'bytes':dest.stat().st_size,'sha256':s,
                      'manifest_nonprivate_members':len(m['members'])},indent=2))
