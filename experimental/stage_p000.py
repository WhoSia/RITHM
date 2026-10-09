#!/usr/bin/env python3
"""Opt-in isolated p000 reconstruction. Never native receipt or score."""
import argparse,csv,hashlib,json,math,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
FRAME_SHA='e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293'
TRIP_SHA='0f5b52d154d51e0269e3bb08670da5b71077703c6fefcb3cf9a515f9602af65c'
COMMIT='360682800b120fe0e439afa598eaa04ea0c9f42a'
RUN='s02-16-zZngkjB8'
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()
def stage(work,name):
 if name in ('','.','..') or '/' in name or '\\' in name:raise RuntimeError('INVALID_STAGING_NAME')
 work=work.resolve(strict=True)
 mount=subprocess.check_output(['findmnt','-n','-o','SOURCE','-T',str(work)],text=True).strip()
 if mount!='/dev/sdb1':raise RuntimeError('HDD_MOUNT_GUARD_FAIL')
 frame=work/'artifacts/s02-16-frozen-frame/s02-14-eligible-frame.tsv'
 trip=work/'runs'/RUN/'work-p000/scenario/most.s02-16-p000-tripinfo.xml'
 script=work/'RITHM/scripts/s02_16_cell.py'
 if subprocess.check_output(['git','-C',str(work/'RITHM'),'rev-parse','HEAD'],text=True).strip()!=COMMIT:
  raise RuntimeError('FROZEN_SOURCE_COMMIT_MISMATCH')
 if digest(frame)!=FRAME_SHA or digest(trip)!=TRIP_SHA:raise RuntimeError('PRIMARY_SOURCE_HASH_MISMATCH')
 if not script.is_file():raise RuntimeError('CANONICAL_SCRIPT_MISSING')
 root=work/'recoveries'
 if root.is_symlink():raise RuntimeError('STAGING_ROOT_SYMLINK')
 root.mkdir(mode=0o700,exist_ok=True)
 out=root/name
 if out.exists() or out.is_symlink():raise RuntimeError('STAGING_ALREADY_EXISTS')
 out.mkdir(mode=0o700)
 subprocess.run([sys.executable,str(script),'burden','--label','000','--seal',str(frame.parent),
  '--trip',str(trip),'--out',str(out)],check=True)
 fp=out/'framecomplete.tsv'
 with frame.open(newline='') as f:raw=list(csv.DictReader(f,delimiter='\t'))
 source={r['id']:float(r['activation_time']) for r in raw}
 if len(raw)!=45822 or len(source)!=45822:raise RuntimeError('FRAME_COUNT_FAIL')
 arrivals={};xml_total=eligible=unfinished=0
 for _,el in ET.iterparse(trip,events=('end',)):
  if el.tag.split('}')[-1]!='tripinfo':el.clear();continue
  xml_total+=1;key=el.get('id')
  if key not in source:el.clear();continue
  eligible+=1
  if key in arrivals:raise RuntimeError('DUPLICATE_TRIPINFO')
  try:a=float(el.get('arrival','-1'))
  except (ValueError,TypeError):a=-1
  if not math.isfinite(a) or not 0<=a<=50400:a=50400;unfinished+=1
  arrivals[key]=a;el.clear()
 rows=mat=absent=0;seen=set()
 with fp.open(newline='') as f:
  reader=csv.DictReader(f,delimiter='\t')
  if reader.fieldnames!=['id','activation_time','completion_clock','burden','status']:
   raise RuntimeError('FRAME_HEADER_FAIL')
  for row in reader:
   key=row['id'];rows+=1
   if key not in source or key in seen:raise RuntimeError('FRAME_ID_FAIL')
   seen.add(key)
   s,a,b=map(float,(row['activation_time'],row['completion_clock'],row['burden']))
   want=arrivals.get(key,50400)
   if not all(map(math.isfinite,(s,a,b))) or abs(s-source[key])>1e-6 or abs(a-want)>1e-6 or abs(b-(want-s))>1e-6:
    raise RuntimeError('FRAME_VALUE_FAIL')
   expect='materialized' if key in arrivals else 'absent'
   if row['status']!=expect:raise RuntimeError('FRAME_STATUS_FAIL')
   mat+=expect=='materialized';absent+=expect=='absent'
 if rows!=45822 or seen!=set(source) or (xml_total,eligible,unfinished)!=(39746,39068,21768):
  raise RuntimeError('PINNED_ARTIFACT_EXPECTATION_FAIL')
 obj={'kind':'ISOLATED_P000_RECONSTRUCTION_NOT_NATIVE_RECEIPT','label':'000','original_run':RUN,
  'frozen_commit':COMMIT,'frame_sha256':FRAME_SHA,'tripinfo_sha256':TRIP_SHA,
  'reconstructed_frame_sha256':digest(fp),'rows':rows,'materialized':mat,'absent':absent,
  'unfinished_or_invalid_arrivals':unfinished,'native_supervisor_status_replaced':False,
  'native_exitcode_file_created':False,'score_computed':False,
  'proof_of_original_rc':'kernel child wait status 0 observed separately; not a native written receipt'}
 with (out/'reconstruction-manifest.json').open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')
 print('STAGED_RECONSTRUCTION_PASS',str(out));print(json.dumps(obj,sort_keys=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work',required=True,type=Path);p.add_argument('--name',required=True)
 a=p.parse_args();stage(a.work,a.name)
