#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
dir="$(mktemp -d)";trap 'rm -rf "$dir"' EXIT
ruby "$root/ruby/rithm28/p1p11/emit_linked.rb" "$dir/valid.json"
go run "$root/go/rithm28/p1p11/verify_linked.go" "$dir/valid.json" | grep -q 'synthetic_linked_delivery=true'
for mutation in wrong_parent signed_other_person signed_other_episode signed_early_delivery duplicate_event forged_outcome wrong_role; do
 ruby -rjson -ropenssl -e '
  doc=JSON.parse(File.read(ARGV[0]));events=doc.fetch("evidence");r=events[0];d=events[1]
  mutation=ARGV[2]
  case mutation
  when "wrong_parent" then d["parent_event_id"]="receipt-other"
  when "signed_other_person" then d["person"]="A1"
  when "signed_other_episode" then d["episode"]="B2:unrelated"
  when "signed_early_delivery" then d["occurred"]=1
  when "duplicate_event" then d["event_id"]=r["event_id"]
  when "forged_outcome" then d["outcome"]="not_delivered"
  when "wrong_role" then d["domain"]="client_receipt"
  end
  keys={"receipt-test-v2"=>"synthetic-receipt-role-secret","delivery-test-v2"=>"synthetic-delivery-role-secret"}
  fields=%w[domain issuer person episode event_id parent_event_id occurred published received outcome]
  d["mac"]=OpenSSL::HMAC.hexdigest("sha256",keys.fetch(d.fetch("key_id")),fields.map{|k|JSON.generate(d.fetch(k))}.join("|"))
  File.write(ARGV[1],JSON.generate(doc))
 ' "$dir/valid.json" "$dir/$mutation.json" "$mutation"
 if go run "$root/go/rithm28/p1p11/verify_linked.go" "$dir/$mutation.json" >/dev/null 2>&1; then
  echo "FAIL: accepted $mutation";exit 1
 fi
 echo "PASS rejected $mutation"
done
ruby -rjson -e 'x=JSON.parse(File.read(ARGV[0]));x["evidence"].pop;File.write(ARGV[1],JSON.generate(x))' "$dir/valid.json" "$dir/receipt_only.json"
go run "$root/go/rithm28/p1p11/verify_linked.go" "$dir/receipt_only.json" | grep -q 'synthetic_linked_delivery=false'
echo "PASS Ruby->Go typed ancestry verifier"
