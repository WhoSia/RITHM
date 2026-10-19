#!/usr/bin/env bash
set -euo pipefail
ruby ruby/rithm29/p2/test_correspondence.rb
go run go/rithm29/p2/independent.go >/tmp/rithm29p2-go.json
ruby -rjson -r./ruby/rithm29/p2/correspondence -e 'r=Rithm29Correspondence.enumerate(horizon:3);puts JSON.generate({"counts"=>r[:branch_counts],"welfare"=>r[:welfare_values].to_h{|q|[q.denominator==1 ? q.numerator.to_s : q.to_s,true]}})' >/tmp/rithm29p2-ruby.json
python3 - <<'PY'
import json
a=json.load(open('/tmp/rithm29p2-go.json')); b=json.load(open('/tmp/rithm29p2-ruby.json'))
assert a==b,(a,b)
print('P2 independent Go all continuation branches and initial welfare values MATCH')
PY
rm -f /tmp/rithm29p2-go.json /tmp/rithm29p2-ruby.json
