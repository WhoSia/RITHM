#!/usr/bin/env bash
set -u

ROOT="$(pwd)"
RESULTS="$ROOT/s02-16-results"
RUNTIME="$ROOT/runtime"
SEAL="$ROOT/seal"
MOST_BASE="$ROOT/most-base"
PARALLEL="${S02_16_PARALLEL:-4}"

mkdir -p "$RESULTS"

{
  date -u +"utc=%Y-%m-%dT%H:%M:%SZ"
  uname -a
  lscpu | sed -n '1,25p'
  free -h
  df -h .
  python3 --version
  git --version
  gh --version | head -n1
} | tee "$RESULTS/environment.txt"

command -v gh >/dev/null || { echo "gh CLI required"; exit 2; }

rm -rf "$RUNTIME" "$SEAL"
gh run download 35307642604 -R WhoSia/RITHM -n s02-14-e3-sumo114-gdal-runtime -D "$RUNTIME"
gh run download 35307642604 -R WhoSia/RITHM -n s02-14-e3-frozen-frame -D "$SEAL"
chmod +x "$RUNTIME/bin/sumo"

SUMO_SHA="$(sha256sum "$RUNTIME/bin/sumo" | awk '{print $1}')"
test "$SUMO_SHA" = "75c5556e52dd48953a7b6b75c3bb508df89a1e5690f7e32c962eac4587da864b"
test "$(sha256sum "$SEAL/s02-14-eligible-frame.tsv" | awk '{print $1}')" = "e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293"

"$RUNTIME/bin/sumo" --version | tee "$RESULTS/sumo-version.txt"
ldd "$RUNTIME/bin/sumo" | tee "$RESULTS/sumo-ldd.txt"
if grep -q "not found" "$RESULTS/sumo-ldd.txt"; then
  echo "missing runtime library"; exit 3
fi

rm -rf "$MOST_BASE"
git clone --no-checkout https://github.com/lcodeca/MoSTScenario.git "$MOST_BASE"
git -C "$MOST_BASE" checkout --detach b29b2f65f1096a9c69a601ec62a724815cb4a43f
test "$(git -C "$MOST_BASE" rev-parse HEAD)" = "b29b2f65f1096a9c69a601ec62a724815cb4a43f"
test "$(git -C "$MOST_BASE" hash-object scenario/most.sumocfg)" = "03dbc535acd7057731a1de8924115a9276842426"
test "$(git -C "$MOST_BASE" hash-object scenario/in/most.net.xml)" = "6ffae75cfe63992c04a6395fbbe86cc39166140c"
test "$(git -C "$MOST_BASE" hash-object scenario/in/add/basic.vType.xml)" = "d9aebbde5cfeb8dbee6203d6c5fdf3b1f4666a21"

run_cell () {
  label="$1"
  out="$RESULTS/p$label"
  work="$ROOT/work-p$label"
  rm -rf "$out" "$work"
  mkdir -p "$out"
  cp -a "$MOST_BASE" "$work"

  python3 scripts/s02_16_cell.py prepare     --label "$label" --seal "$SEAL" --runtime "$RUNTIME" --most "$work" --out "$out"

  cfg="$work/scenario/s02-16-p$label.sumocfg"
  round="$work/scenario/s02-16-p$label.roundtrip.sumocfg"
  SUMO_HOME="$RUNTIME" "$RUNTIME/bin/sumo" -c "$cfg" -C "$round"
  test -s "$round"

  start="$(date +%s)"
  set +e
  (
    cd "$work/scenario" || exit 99
    SUMO_HOME="$RUNTIME" "$RUNTIME/bin/sumo"       -c "s02-16-p$label.sumocfg"       --no-step-log true       > "$out/stdout.txt" 2> "$out/stderr.txt"
  )
  rc=$?
  set -e
  end="$(date +%s)"
  runtime_seconds=$((end-start))
  echo "$rc" > "$out/exitcode.txt"
  echo "$runtime_seconds" > "$out/runtime-seconds.txt"

  trip="$work/scenario/most.s02-16-p$label-tripinfo.xml"
  if [ "$rc" = 0 ] && [ -s "$trip" ]; then
    cp "$trip" "$out/most.s02-16-p$label-tripinfo.xml"
    sha256sum "$out/most.s02-16-p$label-tripinfo.xml" > "$out/tripinfo.sha256"
    python3 scripts/s02_16_cell.py burden       --label "$label" --seal "$SEAL"       --trip "$out/most.s02-16-p$label-tripinfo.xml" --out "$out"
  fi

  python3 - "$label" "$rc" "$runtime_seconds" "$out" <<'PY'
import hashlib,json,sys
from pathlib import Path
label,rc,rt,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),Path(sys.argv[4])
trip=out/f"most.s02-16-p{label}-tripinfo.xml"
frame=out/"framecomplete.tsv"
valid=rc==0 and trip.exists() and trip.stat().st_size>0 and frame.exists() and sum(1 for _ in frame.open())-1==45822
obj={
  "stage":"RITHM-ORIGIN-S02.16","label":label,"exit_code":rc,
  "runtime_seconds":rt,"simulation_success":rc==0,
  "prefixed_tripinfo_custodied":trip.exists() and trip.stat().st_size>0,
  "framecomplete_materialized":frame.exists() and frame.stat().st_size>0,
  "scientific_cell_receipt_valid":valid,
  "cell_mean_computed":False,"target_curvature_scored":False,
  "execution_mode":"single uninterrupted process","checkpoint_or_load_state_used":False,
  "sumo_binary_sha256":"75c5556e52dd48953a7b6b75c3bb508df89a1e5690f7e32c962eac4587da864b"
}
if trip.exists():
  obj["tripinfo_sha256"]=hashlib.sha256(trip.read_bytes()).hexdigest()
(out/"status.json").write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
print(json.dumps(obj,indent=2,sort_keys=True))
PY
}

export -f run_cell
export ROOT RESULTS RUNTIME SEAL MOST_BASE

labels=(000 030 070 100)
running=0
overall=0
for label in "${labels[@]}"; do
  (
    set -e
    run_cell "$label"
  ) &
  running=$((running+1))
  if [ "$running" -ge "$PARALLEL" ]; then
    if ! wait -n; then overall=1; fi
    running=$((running-1))
  fi
done
while [ "$running" -gt 0 ]; do
  if ! wait -n; then overall=1; fi
  running=$((running-1))
done

python3 scripts/s02_16_score.py | tee "$RESULTS/score-console.txt"

tar -C "$ROOT" -czf "$ROOT/s02-16-results.tar.gz" s02-16-results
sha256sum "$ROOT/s02-16-results.tar.gz" | tee "$ROOT/s02-16-results.tar.gz.sha256"

if [ "${S02_16_UPLOAD_RELEASE:-0}" = "1" ]; then
  tag="${S02_16_RELEASE_TAG:-rithm-s02.16-$(date -u +%Y%m%dT%H%M%SZ)}"
  gh release create "$tag" -R WhoSia/RITHM     "$ROOT/s02-16-results.tar.gz" "$ROOT/s02-16-results.tar.gz.sha256"     --title "RITHM S02.16 stable-compute execution evidence"     --notes "S02.16 execution evidence bundle. Scientific interpretation remains in the canonical stage receipt."     --latest=false
  echo "release_tag=$tag" | tee "$RESULTS/release.txt"
fi

exit "$overall"
