#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, math, xml.etree.ElementTree as ET
from pathlib import Path

SUMO_SHA="75c5556e52dd48953a7b6b75c3bb508df89a1e5690f7e32c962eac4587da864b"
MOST_COMMIT="b29b2f65f1096a9c69a601ec62a724815cb4a43f"
COHORTS={
    "000":("s02-14-p000-explicit.txt",0,"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    "030":("s02-14-p030-explicit.txt",13746,"1b9fba0675825b770afe24159fc39c4ba12b6f78fa05e432d77ad8e7556f83f5"),
    "070":("s02-14-p070-explicit.txt",32075,"f4855d4965e9d7268f97a2d0c90f11b4d9632cd6cd8d22ff2d15ed4804cd9270"),
    "100":("s02-14-p100-explicit.txt",45822,"21d0db278e7c39d9403520b10ab471470a03c30cd908c587677a1d5249f8f634"),
}
FRAME_SHA="e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293"

def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def setv(parent,name,value):
    e=parent.find(name)
    if e is None: e=ET.SubElement(parent,name)
    e.set("value",str(value))

def prepare(label:str, seal:Path, runtime:Path, most:Path, out:Path):
    cohort_file, cohort_n, cohort_sha=COHORTS[label]
    assert sha256(runtime/"bin/sumo")==SUMO_SHA
    assert sha256(seal/"s02-14-eligible-frame.tsv")==FRAME_SHA
    assert sha256(seal/cohort_file)==cohort_sha
    cohort=[x for x in (seal/cohort_file).read_text().splitlines() if x]
    assert len(cohort)==cohort_n and len(set(cohort))==cohort_n

    tree=ET.parse(most/"scenario/most.sumocfg"); root=tree.getroot()
    routing=root.find("routing"); output=root.find("output"); proc=root.find("processing")
    time=root.find("time"); rnd=root.find("random_number")
    assert all(x is not None for x in (routing,output,proc,time,rnd))
    assert output.find("output-prefix").get("value")=="most."
    assert float(proc.find("max-depart-delay").get("value"))==900.0
    assert float(time.find("begin").get("value"))==14400.0
    assert float(time.find("end").get("value"))==50400.0
    assert float(time.find("step-length").get("value"))==0.25
    assert int(rnd.find("seed").get("value"))==42

    setv(routing,"device.rerouting.probability","0")
    setv(routing,"device.rerouting.period","300")
    setv(routing,"device.rerouting.pre-period","300")
    old=routing.find("device.rerouting.explicit")
    if old is not None: routing.remove(old)
    if cohort:
        e=ET.SubElement(routing,"device.rerouting.explicit")
        e.set("value",",".join(cohort))
    setv(proc,"time-to-teleport","-1")
    setv(output,"tripinfo-output",f"s02-16-p{label}-tripinfo.xml")
    setv(output,"tripinfo-output.write-unfinished","true")

    cfg=most/"scenario"/f"s02-16-p{label}.sumocfg"
    tree.write(cfg,encoding="utf-8",xml_declaration=True)
    rec={
        "stage":"RITHM-ORIGIN-S02.16","label":label,"cohort_n":cohort_n,
        "time_to_teleport":-1,"begin":14400,"end":50400,"step":0.25,"seed":42,
        "max_depart_delay":900,"global_probability":0,"period":300,"pre_period":300,
        "sumo_binary_sha256":SUMO_SHA,"most_commit":MOST_COMMIT,
        "frame_sha256":FRAME_SHA,"cohort_sha256":cohort_sha,
        "config_sha256":sha256(cfg),"checkpoint_or_load_state_allowed":False,
        "target_aggregation_opened":False
    }
    out.mkdir(parents=True,exist_ok=True)
    (out/"config-receipt.json").write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
    return cfg

def burden(label:str, seal:Path, trip:Path, out:Path):
    H=50400.0
    frame={}
    with (seal/"s02-14-eligible-frame.tsv").open(newline="") as f:
        for row in csv.DictReader(f,delimiter="\t"):
            frame[row["id"]]=float(row["activation_time"])
    assert len(frame)==45822
    arrivals={}; duplicates=[]
    for _,e in ET.iterparse(trip,events=("end",)):
        if e.tag.split("}")[-1]!="tripinfo":
            e.clear(); continue
        vid=e.attrib.get("id")
        if vid not in frame:
            e.clear(); continue
        if vid in arrivals: duplicates.append(vid)
        try: a=float(e.attrib.get("arrival","-1"))
        except Exception: a=-1.0
        arrivals[vid]=a if math.isfinite(a) and 0<=a<=H else H
        e.clear()
    assert not duplicates, duplicates[:20]
    fp=out/"framecomplete.tsv"
    with fp.open("w",newline="") as f:
        w=csv.writer(f,delimiter="\t")
        w.writerow(["id","activation_time","completion_clock","burden","status"])
        for vid,s in frame.items():
            if vid in arrivals: A=arrivals[vid]; status="materialized"
            else: A=H; status="absent"
            b=A-s; assert b>=-1e-9
            w.writerow([vid,s,A,b,status])
    assert sum(1 for _ in fp.open())-1==45822
    return fp

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("mode",choices=["prepare","burden"])
    ap.add_argument("--label",required=True,choices=sorted(COHORTS))
    ap.add_argument("--seal",type=Path,required=True)
    ap.add_argument("--runtime",type=Path)
    ap.add_argument("--most",type=Path)
    ap.add_argument("--trip",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    if a.mode=="prepare":
        assert a.runtime and a.most
        prepare(a.label,a.seal,a.runtime,a.most,a.out)
    else:
        assert a.trip
        burden(a.label,a.seal,a.trip,a.out)

if __name__=="__main__": main()
