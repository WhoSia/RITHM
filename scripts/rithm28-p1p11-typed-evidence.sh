#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
ruby "$here/ruby/rithm28/p1p11/emit.rb" "$tmp/evidence.json"
go run "$here/go/rithm28/p1p11/verify.go" "$tmp/evidence.json"
for mutation in forged_outcome replayed_id wrong_role reversed_clock swapped_person cross_subject_signed missing_delivery; do
 ruby -rjson -ropenssl -e '
  d=JSON.parse(File.read(ARGV[0])); e=d.fetch("evidence"); case ARGV[2]
  when "forged_outcome" then e[0]["outcome"]="benefit_delivered"
  when "replayed_id" then e[1]["event_id"]=e[0]["event_id"]
  when "wrong_role" then e[0]["domain"]="benefit_delivery"
  when "reversed_clock" then e[0]["received"]=0
  when "swapped_person" then e[1]["person"]="A1"
  when "cross_subject_signed" then e[1]["person"]="A1"; e[1]["mac"]=OpenSSL::HMAC.hexdigest("sha256","synthetic-delivery-only-key", %w[domain issuer person episode event_id occurred published received outcome].map{|k|JSON.generate(e[1].fetch(k))}.join("|"))
  when "missing_delivery" then e.pop
  end
  File.write(ARGV[1],JSON.generate(d))' "$tmp/evidence.json" "$tmp/$mutation.json" "$mutation"
 if [[ "$mutation" == "missing_delivery" ]]; then
   go run "$here/go/rithm28/p1p11/verify.go" "$tmp/$mutation.json" |grep -q 'synthetic_delivery_event=false'
 else
   if go run "$here/go/rithm28/p1p11/verify.go" "$tmp/$mutation.json" >/dev/null 2>&1; then echo "FAIL accepted mutation $mutation"; exit 1; fi
 fi
 echo "PASS $mutation"
done
