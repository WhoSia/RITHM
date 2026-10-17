#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
ruby "$repo/ruby/rithm28/p1p9/export.rb" "$tmp/policy.json"
go run "$repo/go/rithm28/p1p9/verify.go" "$tmp/policy.json"
ruby -rjson -e 'x=JSON.parse(File.read(ARGV.fetch(0))); x.fetch("nodes").fetch(x.fetch("root")).fetch("action")[1]=4; File.write(ARGV.fetch(1),JSON.generate(x))' "$tmp/policy.json" "$tmp/invalid_budget.json"
if go run "$repo/go/rithm28/p1p9/verify.go" "$tmp/invalid_budget.json" >/dev/null 2>&1; then
  echo "FAIL budget mutation accepted"; exit 1
fi
ruby -rjson -e 'x=JSON.parse(File.read(ARGV.fetch(0))); x.fetch("nodes").fetch(x.fetch("root")).fetch("children")[0]["key"]="tampered"; File.write(ARGV.fetch(1),JSON.generate(x))' "$tmp/policy.json" "$tmp/invalid_branch.json"
if go run "$repo/go/rithm28/p1p9/verify.go" "$tmp/invalid_branch.json" >/dev/null 2>&1; then
  echo "FAIL branch mutation accepted"; exit 1
fi
echo "PASS Ruby/Go mainline and two independent negative mutation tests"
