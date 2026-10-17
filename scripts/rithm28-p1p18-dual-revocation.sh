#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
go build -o "$tmp/verify" "$repo/go/rithm28/p1p18/verify.go"
ruby "$repo/ruby/rithm28/p1p18/test_dynamic.rb"
ruby -rjson -e '
 d=ARGV.fetch(0)
 configs={
  "h5_upper"=>[5,1,0,1,6,6],"h5_lower"=>[5,0,0,1,6,6],
  "h5_revoked_upper"=>[5,2,0,1,0,6],"h5_revoked_lower"=>[5,1,0,1,0,6],
  "h6_upper"=>[6,0,0,1,7,7],"h6_revoked_lower"=>[6,0,0,1,0,7],
  "h5_restored_upper"=>[5,1,0,1,0,4],"h5_restore_too_late_lower"=>[5,1,0,1,0,5]
 }
 configs.each do |name,(h,b,c,delay,r,s)|
  File.write("#{d}/#{name}.json",JSON.generate({horizon:h,budget:b,probe_cost:c,delay:delay,revoke_at:r,restore_at:s}))
 end
' "$tmp"
for name in h5_upper h5_lower h5_revoked_upper h5_revoked_lower h6_upper h6_revoked_lower h5_restored_upper h5_restore_too_late_lower;do
 ruby "$repo/ruby/rithm28/p1p18/dynamic.rb" "$tmp/$name.json" "$tmp/$name.cert.json"
 "$tmp/verify" "$tmp/$name.cert.json"
done
ruby -rjson -e '
 d=ARGV[0]
 win=JSON.parse(File.read("#{d}/h5_upper.cert.json"))
 lose=JSON.parse(File.read("#{d}/h5_lower.cert.json"))
 def save(d,n,doc);File.write("#{d}/#{n}.json",JSON.pretty_generate(doc));end
 v=Marshal.load(Marshal.dump(win));v.fetch("nodes").fetch(v.fetch("root")).fetch("children").pop;save(d,"bad_missing_branch",v)
 v=Marshal.load(Marshal.dump(win));v.fetch("nodes").fetch(v.fetch("root"))["action"]=[0,5,1];save(d,"bad_budget",v)
 v=Marshal.load(Marshal.dump(win));v.fetch("nodes").fetch(v.fetch("root")).fetch("children").fetch(0)["key"]="[]";save(d,"bad_successor",v)
 v=Marshal.load(Marshal.dump(lose));v.fetch("nodes").fetch(v.fetch("root")).fetch("counterexamples").pop;save(d,"bad_unanswered_action",v)
 v=Marshal.load(Marshal.dump(lose));v.fetch("nodes").fetch(v.fetch("root")).fetch("counterexamples").fetch(0)["observation"]=77;save(d,"bad_forged_counter",v)
 v=Marshal.load(Marshal.dump(win));v.fetch("nodes")["never-visited"]={"action"=>[0,0,0],"children"=>[]};save(d,"bad_excess_node",v)
 v=Marshal.load(Marshal.dump(win));v["real_world_welfare_verified"]=true;save(d,"bad_welfare_claim",v)
 v=Marshal.load(Marshal.dump(win));v.fetch("config")["revoke_at"]=0;save(d,"bad_revocation_claim",v)
 File.write("#{d}/bad_duplicate.json",File.read("#{d}/h5_upper.cert.json").sub(/\A\{/,"{\"schema\":\"duplicate\","))
 File.write("#{d}/bad_trailing.json",File.read("#{d}/h5_upper.cert.json")+"{}")
' "$tmp"
for issue in bad_missing_branch bad_budget bad_successor bad_unanswered_action bad_forged_counter bad_excess_node bad_welfare_claim bad_revocation_claim bad_duplicate bad_trailing;do
 if "$tmp/verify" "$tmp/$issue.json" >/dev/null 2>&1;then
  echo "FAIL accepted mutation $issue";exit 1
 fi
 echo "PASS REJECT $issue"
done
echo 'PASS Ruby dual-witness synthesis, Go independent replay and parser mutations'
