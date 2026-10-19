#!/usr/bin/env bash
set -euo pipefail
ruby ruby/rithm29/p0/test_paid_agency.rb
ruby ruby/rithm29/p0/export_quarters.rb > /tmp/rithm29-ruby-$$.json
go run go/rithm29/p0/independent.go > /tmp/rithm29-go-$$.json
python3 - /tmp/rithm29-ruby-$$.json /tmp/rithm29-go-$$.json <<'PY'
import json,sys
with open(sys.argv[1]) as f: ruby=json.load(f)
with open(sys.argv[2]) as f: go=json.load(f)
assert ruby==go,(ruby,go)
print("RITHM-2.9 P0 independent Ruby/Go four strategy profiles MATCH")
PY
rm -f /tmp/rithm29-ruby-$$.json /tmp/rithm29-go-$$.json
