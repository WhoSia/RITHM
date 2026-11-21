"""Deterministic, source-free R60 archive builder; never add private original ZIP."""
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).parent
FILES=[
 'REPRODUCE_R60.md','RITHM_R60_20261121.md',
 'RITHM_2_10_ACHIEVEMENTS_AUDIT_20261121.md',
 'r54_original_batch_clock.py','r59_prior_exposure.py',
 'r60_cross_segment.py','r60_identity_placebo.py','r60_latent_rival.py',
 'r60_run.py','r60_build_archive.py',
 'r60_results.json','r60_identity_placebo.json','r60_run_sha256.json',
 'test_r60_cross_segment.py','test_r60_identity_placebo.py',
 'test_r60_results_contract.py',
]
DENY={'rererequestforpermissiontouseexperimentalroutechoi.zip',
      'data_task_all_230705.csv','data_task_all_switch_230705.csv'}
assert len(FILES)==len(set(FILES))
assert not DENY.intersection(FILES)


def build(destination):
    info={}
    for name in FILES:
        raw=(ROOT/name).read_bytes()
        info[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    manifest={
       'bundle':'RITHM 2.10 R60 exact source-free science and achievement audit',
       'member_files':info,'member_count':len(info),
       'private_author_original_zip_excluded':True,
       'private_original_sha256_only':'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953',
       'replay_status':'actual original data replay local only; CI unit tests synthetic only',
    }
    mb=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    p=Path(destination)
    with ZipFile(p,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
        for name in FILES+['SHA256_MANIFEST.json']:
            blob=mb if name=='SHA256_MANIFEST.json' else (ROOT/name).read_bytes()
            zi=ZipInfo(name,date_time=(2026,11,21,0,0,0))
            zi.compress_type=ZIP_DEFLATED
            zi.external_attr=(0o100644<<16)
            z.writestr(zi,blob,compress_type=ZIP_DEFLATED,compresslevel=9)
    with ZipFile(p) as z:
        assert set(z.namelist())==set(FILES+['SHA256_MANIFEST.json'])
        for name,expect in info.items():
            assert sha256(z.read(name)).hexdigest()==expect['sha256']
        assert all(name not in z.namelist() for name in DENY)
    return {'zip_path':str(p),'sha256':sha256(p.read_bytes()).hexdigest(),
            'bytes':p.stat().st_size,'member_files':len(FILES)+1}

if __name__=='__main__':
    print(json.dumps(build('/mnt/data/RITHM_R60_20261121_REPRODUCER.zip'),indent=2))
