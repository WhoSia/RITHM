#!/usr/bin/env python3
"""Recovered-evidence S02.16 court. Does not create native receipts or change original run."""
import argparse,csv,hashlib,json,math,os,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
FRAME_SHA="e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293"
TRIP000_SHA="0f5b52d154d51e0269e3bb08670da5b71077703c6fefcb3cf9a515f9602af65c"
REC000_SHA="86f2d4c58b2a7d91164f382f0abd35699428065daf6a0ed37bc2c233266459b0"
FROZEN_COMMIT="360682800b120fe0e439afa598eaa04ea0c9f42a"
E2_B={"000":6744.900342630178,"030":6552.030105626119,"070":6531.009995198813,"100":6528.603536510846}
E2_C=0.028238190134892482
LABELS=("000","030","070","100")
H=50400.0
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def reject(msg):raise RuntimeError(msg)
def main(work,outname):
 work=work.resolve(strict=True)
 if subprocess.check_output(["findmnt","-n","-o","SOURCE","-T",str(work)],text=True).strip()!="/dev/sdb1":reject("HDD_GUARD")
 if subprocess.check_output(["git","-C",str(work/"RITHM"),"rev-parse","HEAD"],text=True).strip()!=FROZEN_COMMIT:reject("FROZEN_COMMIT")
 if "/" in outname or "\\" in outname or outname in ("",".",".."):reject("INVALID_NAME")
 run=work/"runs/s02-16-zZngkjB8"
 frozen=work/"artifacts/s02-16-frozen-frame/s02-14-eligible-frame.tsv"
 if digest(frozen)!=FRAME_SHA:reject("FROZEN_FRAME_HASH")
 with frozen.open(newline="") as f:source_rows=list(csv.DictReader(f,delimiter="\t"))
 source={r["id"]:float(r["activation_time"]) for r in source_rows}
 if len(source_rows)!=45822 or len(source)!=45822:reject("FROZEN_FRAME_IDS")
 results={}
 for label in LABELS:
  native=label!="000"
  d=run/f"s02-16-results/p{label}" if native else work/"recoveries/s02-16-p000-recovery-20261009-v1"
  frame=d/"framecomplete.tsv"
  if native:
   status=json.loads((d/"status.json").read_text())
   if status.get("exit_code")!=0 or status.get("scientific_cell_receipt_valid") is not True or status.get("checkpoint_or_load_state_used") is not False or status.get("target_curvature_scored") is not False:reject(f"p{label} NATIVE_STATUS")
   trip=d/f"most.s02-16-p{label}-tripinfo.xml"
   expected=status["tripinfo_sha256"]
  else:
   status=json.loads((d/"reconstruction-manifest.json").read_text())
   if status.get("kind")!="ISOLATED_P000_RECONSTRUCTION_NOT_NATIVE_RECEIPT" or status.get("score_computed") is not False or status.get("reconstructed_frame_sha256")!=REC000_SHA:reject("p000 NONNATIVE_RECEIPT")
   if digest(frame)!=REC000_SHA:reject("p000 FRAME_HASH")
   trip=run/"work-p000/scenario/most.s02-16-p000-tripinfo.xml"
   expected=TRIP000_SHA
  if digest(trip)!=expected:reject(f"p{label} TRIPINFO_HASH")
  arrivals={}; eligible_xml=invalid_arrivals=0
  for _,elem in ET.iterparse(trip,events=("end",)):
   if elem.tag.split("}")[-1]!="tripinfo":elem.clear();continue
   vid=elem.get("id")
   if vid not in source:elem.clear();continue
   eligible_xml+=1
   if vid in arrivals:reject(f"p{label} DUPLICATE_ELIGIBLE_XML")
   try:a=float(elem.get("arrival","-1"))
   except (ValueError,TypeError):a=-1
   if not math.isfinite(a) or a<0 or a>H:a=H;invalid_arrivals+=1
   arrivals[vid]=a;elem.clear()
  seen=set();burdens=[];mat=absent=0
  with frame.open(newline="") as f:
   reader=csv.DictReader(f,delimiter="\t")
   if reader.fieldnames!=["id","activation_time","completion_clock","burden","status"]:reject(f"p{label} HEADER")
   for row in reader:
    vid=row["id"]
    if vid not in source or vid in seen:reject(f"p{label} FRAME_ID")
    seen.add(vid)
    s,a,b=map(float,(row["activation_time"],row["completion_clock"],row["burden"]))
    want=arrivals.get(vid,H)
    expstatus="materialized" if vid in arrivals else "absent"
    if not all(map(math.isfinite,(s,a,b))) or abs(s-source[vid])>1e-6 or abs(a-want)>1e-6 or abs(b-(want-s))>1e-6 or row["status"]!=expstatus:reject(f"p{label} FRAME_XML_VALUE")
    mat+=expstatus=="materialized";absent+=expstatus=="absent";burdens.append(b)
  if seen!=set(source) or len(burdens)!=45822:reject(f"p{label} FRAME_COMPLETE")
  results[label]={"mean_burden":math.fsum(burdens)/len(burdens),"rows":len(burdens),"materialized":mat,"absent":absent,"invalid_arrival_remapped":invalid_arrivals,"eligible_xml":eligible_xml,"frame_sha256":digest(frame),"tripinfo_sha256":expected,"provenance":"NATIVE" if native else "ISOLATED_RECONSTRUCTION"}
 # All primary source checks pass before evaluating target functional.
 B={k:results[k]["mean_burden"] for k in LABELS}
 R={k:B[k]/B["000"]-1.0 for k in LABELS}
 C=(R["100"]-R["070"])-(R["030"]-R["000"])
 dC=C-E2_C
 eps=.005
 verdict="PASS-TNEG-CURVATURE" if C>eps else ("DEFEAT-TNEG-CURVATURE" if C < -eps else "UNRESOLVED-TNEG-CURVATURE")
 report={"type":"RECOVERED_EVIDENCE_CONDITIONAL_COURT_NOT_NATIVE_FOUR_RECEIPTS",
  "source_code_commit":FROZEN_COMMIT,"frame_sha256":FRAME_SHA,"admission":"ALL_FOUR_XML_FRAME_INTEGRITY_PASS_WITH_ONE_NONNATIVE_P000_RECOVERY",
  "native_four_receipt_gate":False,"scientific_recovered_evidence_court":True,
  "original_supervisor_unmodified":True,"labels":results,"B_NEG":B,"R_B_NEG":R,"C_B_NEG":C,
  "C_B_T120":E2_C,"delta_C":dC,"epsilon":eps,"verdict_under_recovered_evidence":verdict,
  "no_post_reveal_retuning":True,"no_new_sumo_run":True}
 stage=work/"recoveries"
 if stage.is_symlink():reject("STAGING_SYMLINK")
 target=stage/outname
 if target.exists() or target.is_symlink():reject("TARGET_ALREADY_EXISTS")
 target.mkdir(mode=0o700)
 path=target/"recovered-evidence-court.json"
 with path.open("x") as f:json.dump(report,f,indent=2,sort_keys=True);f.write("\n");f.flush();os.fsync(f.fileno())
 print("RECOVERED_EVIDENCE_COURT_PASS")
 print("REPORT",str(path))
 print("SHA256",digest(path))
 print(json.dumps({"B_NEG":B,"R_B_NEG":R,"C_B_NEG":C,"delta_C":dC,"verdict_under_recovered_evidence":verdict,"native_four_receipt_gate":False},sort_keys=True))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--work",type=Path,required=True);p.add_argument("--name",required=True)
 a=p.parse_args();main(a.work,a.name)
