"""R61 exact-byte deterministic source-free ZIP and individual member integrity."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import json

ROOT=Path(__file__).parent
ALLOWED=(
 'REPRODUCE_R61.md','RITHM_R61_20261121.md',
 'r54_original_batch_clock.py','r59_prior_exposure.py',
 'r60_cross_segment.py','r60_identity_placebo.py',
 'r61_adaptive_prior.py','r61_matched_identity.py','r61_closed_loop.py',
 'r61_macro_diagnostics.py','r61_three_segment_rival.py','r61_subgroups.py',
 'r61_run.py','r61_build_archive.py',
 'test_r61_adaptive_prior.py','test_r61_rollout_and_mechanism.py','test_r61_macro_diagnostics.py',
 'r61_results.json','r61_identity_null.json','r61_subgroups.json',
 'r61_three_segment_results.json','r61_rollout_observed.json',
 'r61_rollout_fair.json','r61_rollout_seed2.json',
 'r61_macro_diagnostics.json','R61_SOURCE_REPLAY_SHA256.json'
)
FORBIDDEN={'rererequestforpermissiontouseexperimentalroutechoi.zip',
           'data_task_all_230705.csv','data_task_all_switch_230705.csv'}
if len(set(ALLOWED))!=len(ALLOWED):raise AssertionError('duplicate member')
if set(ALLOWED)&FORBIDDEN:raise AssertionError('private human source in publish set')


def build(destination):
    seen={}
    for name in ALLOWED:
        p=ROOT/name
        if not p.is_file():raise FileNotFoundError(name)
        raw=p.read_bytes()
        if not raw:raise ValueError('empty archived member '+name)
        seen[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    manifest={'research':'RITHM P3-R61',
              'source_sha256_only':'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953',
              'private_human_zip_excluded':True,'source_free_test_count':29,
              'allowed_members':seen,'member_count':len(seen)+1,
              'original_human_replay_only_local':'Remote CI tests run on synthetic source-free data, not human rows.'}
    mb=(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
    dest=Path(destination)
    with ZipFile(dest,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
        for name in (*ALLOWED,'SHA256_MANIFEST.json'):
            info=ZipInfo(name,date_time=(2026,11,21,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o100644<<16
            data=mb if name=='SHA256_MANIFEST.json' else (ROOT/name).read_bytes()
            z.writestr(info,data,compress_type=ZIP_DEFLATED,compresslevel=9)
    with ZipFile(dest) as z:
        if set(z.namelist())!=set(ALLOWED)|{'SHA256_MANIFEST.json'}:
            raise AssertionError('member selection mismatch')
        for name,val in seen.items():
            if sha256(z.read(name)).hexdigest()!=val['sha256']:
                raise AssertionError('member digest mismatch '+name)
        if FORBIDDEN&set(z.namelist()):raise AssertionError('sensitive source release')
    (ROOT/'SHA256_MANIFEST.json').write_bytes(mb)
    return {'zip_sha256':sha256(dest.read_bytes()).hexdigest(),
            'zip_bytes':dest.stat().st_size,'members':len(ALLOWED)+1,
            'source_free_only':True}


if __name__=='__main__':
    print(json.dumps(build('/mnt/data/RITHM_R61_20261121_REPRODUCER.zip'),indent=2))
