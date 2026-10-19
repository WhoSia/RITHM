#!/usr/bin/env bash
set -euo pipefail
r=$(mktemp); g=$(mktemp)
trap 'rm -f "$r" "$g"' EXIT
ruby ruby/rithm29/p1/test_dynamic_court.rb
ruby ruby/rithm29/p1/export.rb > "$r"
go run go/rithm29/p1/independent.go > "$g"
python3 - "$r" "$g" <<'PY'
import json,sys
a,b=[json.load(open(x)) for x in sys.argv[1:]]
assert a==b, {"ruby":a,"go":b}
print("P1 independent Ruby-Go 12 public-memory state Nash certificates MATCH")
PY
