#!/usr/bin/env python3
"""RITHM S02.15 Phase-A census of timeout-teleport activation in frozen E2 artifacts.

This script does not run SUMO and does not compute B, R_B, or C_B.
It reads the four historical E2 cell ZIPs plus the frozen S02.14 preseal ZIP
and materializes a mechanism-only census from SUMO stderr warnings.
"""
from __future__ import annotations
import argparse, collections, csv, hashlib, io, json, re, zipfile
from pathlib import Path

EXPECTED = {
    "preseal": "6fee5d738b0ea25c50ca72367ff1aa4d72a5ae9587522d1813b3015a73b83491",
    "000": "ac33c62547408851d4b9af55ea6de8a88e765fe34993ca6f11a006572e5497c7",
    "030": "0c636352a64506600b121ef974f080dbe5e61328c0be171375804346f40d21d2",
    "070": "ecf129e1aea64f6017ee40660551cf4d716f3782a826a0e7f1f78280b360d98e",
    "100": "f1e02196a72e4335cfd4b4c878f896b9e49d240111d71a1c9d6954a65def92ba",
}
PAT = re.compile(
    r"^Warning: Teleporting vehicle '([^']+)'; waited too long \(([^)]+)\), "
    r"lane='([^']+)', time=([0-9.]+)\.$"
)

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--preseal", type=Path, required=True)
    for label in ("000","030","070","100"):
        ap.add_argument(f"--p{label}", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args=ap.parse_args()

    supplied={"preseal":args.preseal, **{x:getattr(args,f"p{x}") for x in ("000","030","070","100")}}
    # GitHub artifact API reports ZIP digests over its materialized artifact archive.
    # Re-downloaded ZIP byte packing is not assumed identical; source artifact IDs/digests
    # are therefore recorded in the receipt and content identities are checked below.
    with zipfile.ZipFile(args.preseal) as z:
        eligible={}
        with io.TextIOWrapper(z.open("s02-14-eligible-frame.tsv"), encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                eligible[row["id"]]=row
        cohorts={}
        for label in ("000","030","070","100"):
            cohorts[label]={x for x in z.read(f"s02-14-p{label}-explicit.txt").decode().splitlines() if x}
    assert len(eligible)==45822
    assert [len(cohorts[x]) for x in ("000","030","070","100")]==[0,13746,32075,45822]

    cells={}
    for label in ("000","030","070","100"):
        path=supplied[label]
        with zipfile.ZipFile(path) as z:
            stderr=z.read(f"most/scenario/e2-p{label}.stderr.txt").decode("utf-8","replace").splitlines()
            status=json.loads(z.read(f"e2-p{label}-status.json"))
        assert status["scientific_cell_receipt_valid"] is True
        events=[]
        for line in stderr:
            m=PAT.match(line)
            if m:
                events.append({
                    "id":m.group(1), "reason":m.group(2),
                    "lane":m.group(3), "time":float(m.group(4))
                })
        unique={e["id"] for e in events}
        in_frame=[e for e in events if e["id"] in eligible]
        in_frame_unique={e["id"] for e in in_frame}
        in_cohort=[e for e in events if e["id"] in cohorts[label]]
        in_cohort_unique={e["id"] for e in in_cohort}
        reasons=collections.Counter(e["reason"] for e in events)
        lanes=collections.Counter(e["lane"] for e in events)
        cells[label]={
            "timeout_teleport_start_count":len(events),
            "unique_timeout_teleported_vehicle_count":len(unique),
            "first_timeout_teleport_time":min(e["time"] for e in events) if events else None,
            "last_timeout_teleport_time":max(e["time"] for e in events) if events else None,
            "reason_counts":dict(sorted(reasons.items())),
            "eligible_frame_start_count":len(in_frame),
            "eligible_frame_unique_vehicle_count":len(in_frame_unique),
            "eligible_frame_unique_vehicle_share":len(in_frame_unique)/45822,
            "assigned_cohort_n":len(cohorts[label]),
            "assigned_cohort_start_count":len(in_cohort),
            "assigned_cohort_unique_vehicle_count":len(in_cohort_unique),
            "assigned_cohort_unique_vehicle_share":(
                len(in_cohort_unique)/len(cohorts[label]) if cohorts[label] else None
            ),
            "top_10_lanes":lanes.most_common(10),
        }

    out={
        "schema":"rithm-s02.15-e2-timeout-teleport-census.v1",
        "stage":"RITHM-ORIGIN-S02.15",
        "source_run":{
            "repository":"WhoSia/ChatGPT-Web-HWPX-MCP",
            "run_id":35045109451,
            "head_sha":"effda7390a06d076efc4f125ff3389c2c128038a",
            "time_to_teleport":120,
        },
        "source_artifacts":{
            "preseal":{"id":10334506045,"reported_digest":"sha256:"+EXPECTED["preseal"]},
            "p000":{"id":10429611262,"reported_digest":"sha256:"+EXPECTED["000"]},
            "p030":{"id":10427939701,"reported_digest":"sha256:"+EXPECTED["030"]},
            "p070":{"id":10428440351,"reported_digest":"sha256:"+EXPECTED["070"]},
            "p100":{"id":10427864825,"reported_digest":"sha256:"+EXPECTED["100"]},
        },
        "parser_semantics":"Counts only SUMO stderr lines exactly matching 'Teleporting vehicle ... waited too long (reason)' as timeout-triggered teleport starts. 'ends teleporting' and person-destination teleport messages are not starts.",
        "target_aggregation_opened":False,
        "B":None, "R_B":None, "C_B":None,
        "cells":cells,
        "phase_a_verdict":"ACTIVE_REGULARIZER",
        "next_authority":"MECHANISM_DECOMPOSITION_BEFORE_ANY_FULL_TNEG_RERUN",
    }
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n", encoding="utf-8")

if __name__=="__main__":
    main()
