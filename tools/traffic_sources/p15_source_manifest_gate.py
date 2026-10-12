#!/usr/bin/env python3
"""Independent rehash of uploaded 2025 source shards against manifest files.
Does not claim deleted pre-transcoded CP949 original bytes were rehashed.
"""
import argparse,csv,hashlib,json
from pathlib import Path

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(8*1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def validate(source_dir,manifest_paths):
    source_dir=Path(source_dir)
    checked=[];rows=0
    for path in manifest_paths:
        manifest=json.loads(Path(path).read_text(encoding="utf-8"))
        if manifest["format"]!="RITHM_SOURCE_CSV_SHARDS_V1":raise ValueError("Manifest schema")
        if manifest["part_count"]!=19:raise ValueError("Part count")
        subtotal=0
        for ix,part in enumerate(manifest["parts_in_order"],1):
            if f"part_{ix:03d}.csv" not in part["file"]:raise ValueError("Part order broken")
            f=source_dir/part["file"]
            if f.stat().st_size!=part["bytes"] or sha(f)!=part["sha256"]:
                raise ValueError(f"SHA or byte size mismatch: {f}")
            # Source-independent 5min row count; no implicit newline counts:
            with f.open("r",encoding="utf-8-sig",newline="") as stream:
                reader=csv.reader(stream,strict=True)
                if next(reader)!=manifest["header"]:raise ValueError("Source header mismatch")
                n=sum(1 for row in reader if len(row)==len(manifest["header"]))
            if n!=part["rows"]:raise ValueError("Manifest row count mismatch")
            subtotal+=n;checked.append(part["file"])
        if subtotal!=manifest["record_count"]:raise ValueError("Half-year row count mismatch")
        rows+=subtotal
    if len(checked)!=38 or rows!=18420707:raise ValueError("Source total mismatch")
    return {"status":"CURRENT_UTF8_SHARDS_VERIFIED", "parts":len(checked),
            "rows":rows,"original_CP949_deleted_file_rehashed":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--shards-dir",required=True)
    p.add_argument("--h1-manifest",required=True)
    p.add_argument("--h2-manifest",required=True)
    a=p.parse_args()
    print(json.dumps(validate(a.shards_dir,[a.h1_manifest,a.h2_manifest]),indent=2))
