"""Deterministic R59 source-free archive builder, SHA manifest and privacy gate."""
from pathlib import Path
import hashlib
import json
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

BASE=Path(__file__).parent
ZIP_PATH=BASE.parent/'RITHM_R59_20261121_REPRODUCER.zip'
MEMBERS=(
    'r54_original_batch_clock.py','r56_joint_flow_cv.py','r57_history_cv.py',
    'r58_author_rivals.py','r58_matched_cv.py','r58_provenance.py',
    'test_r58_author_rivals.py','test_r58_matched_cv.py',
    'test_r58_provenance.py','test_r58_welfare.py',
    'r59_closed_loop.py','r59_transport_counterexample.py',
    'build_r59_archive.py',
    'r59_prior_exposure.py','r59_independent_replay.py','r59_results.py',
    'r59_run.py','test_r59_closed_loop.py','test_r59_prior_exposure.py',
    'test_r59_results.py','requirements-r59.txt','REPRODUCE.md',
    'RITHM_R59_20261121.md','r59_results.json',
    'r59_observed_primary.json','r59_fair_primary.json',
    'r59_observed_seed2_32.json','r59_fair_seed2_32.json',
    'r59_fair_fresh.json','r59_fair_raw_ssm.json',
    'r59_prior_exposure_results.json','r59_original_source_parity.json',
)


def run():
    manifest={'title':'RITHM R59 source-free exact evidence archive',
              'restricted_source_is_excluded':True,'members':{}}
    for name in MEMBERS:
        if '/' in name or name.startswith('.') or 'original.zip' in name or 'rererequest' in name:
            raise ValueError('possible prohibited raw-source member')
        path=BASE/name
        blob=path.read_bytes()
        manifest['members'][name]={
            'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob)}
    manifest['original_human_source_sha256_reference_only']='e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'
    text=json.dumps(manifest,indent=2,sort_keys=True)+'\n'
    (BASE/'SHA256_MANIFEST.json').write_text(text,encoding='utf-8')
    with ZipFile(ZIP_PATH,'w',compression=ZIP_DEFLATED,compresslevel=9) as arc:
        for name in sorted([*MEMBERS,'SHA256_MANIFEST.json']):
            info=ZipInfo(name,date_time=(2026,11,21,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=(0o644 & 0xffff)<<16
            arc.writestr(info,(BASE/name).read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
    with ZipFile(ZIP_PATH) as arc:
        if arc.testzip():raise IOError('corrupt archive')
        m=json.loads(arc.read('SHA256_MANIFEST.json'))
        for name,x in m['members'].items():
            blob=arc.read(name)
            assert len(blob)==x['bytes'] and hashlib.sha256(blob).hexdigest()==x['sha256']
        assert len(arc.namelist())==len(MEMBERS)+1
    return ZIP_PATH,manifest


if __name__=='__main__':
    name,manifest=run()
    print('ARCHIVE',name,'BYTES',name.stat().st_size)
    print('SHA256',hashlib.sha256(name.read_bytes()).hexdigest())
    print('MEMBERS',len(manifest['members']))
