#!/usr/bin/env python3
"""Split a huge CSV into header-repeating, UTF-8 BOM shards with SHA256 manifest.
No third-party packages; preserves CSV RECORD content, not original byte encoding.
Usage: python split_csv_stream.py SOURCE.csv --max-mb 45
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import time

def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def infer_encoding(path: Path) -> str:
    with path.open("rb") as f:
        start = f.read(128 * 1024)
    # Discard sample suffix after last complete line to avoid half a CP949 char.
    if b"\n" in start:
        start = start.rsplit(b"\n", 1)[0] + b"\n"
    if start.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if start.startswith(b"\xff\xfe"):
        return "utf-16"
    for enc in ("utf-8-sig", "cp949"):
        try:
            start.decode(enc, "strict")
            return enc
        except UnicodeDecodeError:
            pass
    raise ValueError("Cannot infer source encoding; pass --encoding cp949 or utf-8-sig")

def split_csv(source: Path, out_dir: Path, max_mb=45.0, encoding="auto") -> dict:
    source = source.expanduser().resolve()
    out_dir = out_dir.expanduser().resolve()
    if not source.exists() or source.suffix.lower() != ".csv":
        raise ValueError("Source must be an existing .csv file")
    if not (0.005 <= max_mb <= 10000):
        raise ValueError("max_mb outside supported range")
    if out_dir == source.parent or (out_dir.exists() and any(out_dir.iterdir())):
        raise FileExistsError("Use a separate EMPTY output directory")
    out_dir.mkdir(parents=True, exist_ok=True)
    max_bytes = round(max_mb * 1_000_000)
    source_encoding = infer_encoding(source) if encoding == "auto" else encoding
    csv.field_size_limit(2**31 - 1)
    holder = io.StringIO(newline="")
    writer = csv.writer(holder, lineterminator="\r\n")
    def encoded(row):
        holder.seek(0)
        holder.truncate(0)
        writer.writerow(row)
        return holder.getvalue().encode("utf-8")
    parts, current, current_name = [], None, None
    current_rows = current_bytes = 0
    total = 0
    def start_part(number, header):
        nonlocal current, current_name, current_rows, current_bytes
        current_name = out_dir / f"{source.stem}__part_{number:03d}.csv"
        if current_name.exists():
            raise FileExistsError(current_name)
        current = current_name.open("wb")
        hdr = b"\xef\xbb\xbf" + encoded(header)
        if len(hdr) >= max_bytes:
            raise ValueError("CSV header exceeds target shard size")
        current.write(hdr)
        current_bytes, current_rows = len(hdr), 0
    def close_part():
        nonlocal current
        if current is None:
            return
        current.close()
        parts.append({"file": current_name.name,
                      "bytes": current_name.stat().st_size,
                      "sha256": digest_file(current_name), "rows": current_rows})
        print(f"Finished {current_name.name}: {current_rows:,} records", flush=True)
        current = None
    with source.open("r", encoding=source_encoding, newline="", errors="strict") as f:
        reader = csv.reader(f, strict=True)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError("Empty input CSV") from exc
        if not header or not any(x.strip() for x in header):
            raise ValueError("Missing CSV header")
        header_bytes = len(encoded(header)) + 3
        start_part(1, header)
        for row in reader:
            if len(row) != len(header):
                raise ValueError(f"Source record {total+2}: column count mismatch")
            record = encoded(row)
            if header_bytes + len(record) > max_bytes:
                raise ValueError(f"Source record {total+2} exceeds hard shard cap")
            if current_rows and current_bytes + len(record) > max_bytes:
                close_part()
                start_part(len(parts) + 1, header)
            current.write(record)
            current_bytes += len(record)
            current_rows += 1
            total += 1
        close_part()
    manifest = {
        "format": "RITHM_SOURCE_CSV_SHARDS_V1",
        "source_file": source.name, "original_bytes": source.stat().st_size,
        "original_sha256": digest_file(source),
        "source_encoding": source_encoding, "output_encoding": "utf-8-sig",
        "header": header, "record_count": total, "part_count": len(parts),
        "max_part_bytes": max_bytes, "parts_in_order": parts,
        "meaning": "Shards are consecutive slices of one source; NOT independent datasets."
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest

def verify_parts(directory: Path):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    total = 0
    for part in manifest["parts_in_order"]:
        path = directory / part["file"]
        if path.stat().st_size != part["bytes"] or digest_file(path) != part["sha256"]:
            raise AssertionError(f"Shard integrity failed: {path}")
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = csv.reader(f, strict=True)
            if next(rows) != manifest["header"]:
                raise AssertionError(f"Header mismatch: {path}")
            n = 0
            for row in rows:
                if len(row) != len(manifest["header"]):
                    raise AssertionError(f"Column mismatch: {path}")
                n += 1
            if n != part["rows"]:
                raise AssertionError(f"Row count mismatch: {path}")
            total += n
    if total != manifest["record_count"]:
        raise AssertionError("Total row count mismatch")
    print(f"PASS: {len(manifest['parts_in_order'])} shard(s), {total:,} rows, all SHA256")
    return total

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path, nargs="?")
    p.add_argument("--out", type=Path)
    p.add_argument("--max-mb", type=float, default=45)
    p.add_argument("--encoding", default="auto")
    p.add_argument("--verify", type=Path)
    args = p.parse_args()
    if args.verify:
        verify_parts(args.verify)
        return
    if args.source is None:
        p.error("Source path required")
    out = args.out or args.source.with_name(args.source.stem + "__parts")
    started = time.monotonic()
    result = split_csv(args.source, out, args.max_mb, args.encoding)
    verify_parts(out)
    print(f"DONE: {result['record_count']:,} rows, "
          f"{result['part_count']} parts in {time.monotonic()-started:.1f}s")

if __name__ == "__main__":
    try:
        main()
    except (UnicodeError, OSError, ValueError, AssertionError, csv.Error) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
