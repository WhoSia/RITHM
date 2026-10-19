#!/usr/bin/env bash
set -euo pipefail
ruby ruby/rithm28/p1p19/test_route_cost_court.rb
for n in 2 3 4; do
  ruby ruby/rithm28/p1p19/route_cost_court.rb "$n" > "/tmp/rithm_ruby_court_$$.json"
  go run go/rithm28/p1p19/route_cost_court.go "$n" > "/tmp/rithm_go_court_$$.json"
  python3 - "/tmp/rithm_ruby_court_$$.json" "/tmp/rithm_go_court_$$.json" <<'PY'
import json,sys
with open(sys.argv[1]) as f: a=json.load(f)
with open(sys.argv[2]) as f: b=json.load(f)
assert a==b,(a,b)
print("Independent Ruby/Go equality:",a["cohort"],a["compared_strict_pairs"],a["rank_reversals"])
PY
  rm -f "/tmp/rithm_ruby_court_$$.json" "/tmp/rithm_go_court_$$.json"
done
