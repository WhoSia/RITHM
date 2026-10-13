# RITHM-2.7 P28 — person-linked twenty-round partial welfare bounds

**No raw new advice compliance or causal policy welfare data are claimed.** The original 2017 S2 source (24 compact group-treatment records) and public external 2022 GPS GeoJSON are not included. Public provider links and exact source SHA values are preserved in the scientific report and JSON manifests. Research result files are aggregated only.

## Developer primary stack: Go · C++17 · Ruby · Rust · R

From this package directory (without altering global compilers), bring the exact prior [WhoSia/RITHM 24-panel input](https://github.com/WhoSia/RITHM/blob/main/data/rithm23_wijayaratna2017_routes.csv) to a local path `original_compact.csv` and verify SHA256 `5926158a1a83172b1a4e119eb369140299a43fbceb2b1ba0321710c0f6723484`.

```sh
cp original_compact.csv source_routes_compact_LOCAL_ONLY.csv
GO111MODULE=off go test ./go/p28 -v
# all three policy families and six person-lifetime budgets
go run ./go/p28/long_run.go source_routes_compact_LOCAL_ONLY.csv > results/p28_go.json
# independent C++17 source decode/DP cross-check
g++ -std=c++17 -O2 -Wall -Wextra -Werror cpp/long_run.cpp -o /tmp/rithm28_cpp
/tmp/rithm28_cpp source_routes_compact_LOCAL_ONLY.csv > results/p28_cpp.csv
# Ruby checks all 18 cross-language exact totals and source matched 288 original subject-treatment slots
ruby ruby/crosscheck_long_run.rb results/p28_go.json results/p28_cpp.csv results/p28_panel_bounds.csv
ruby ruby/audit_human_history.rb source_routes_compact_LOCAL_ONLY.csv > results/p28_history_audit.json
```

The Go standalone source test will use its adjacent original CSV when present; in the cloned GitHub repository, it will fall back to `data/rithm23_wijayaratna2017_routes.csv`. `GO111MODULE=off` permits tests without any external module downloads.

Rust and R code is **provided but has NOT been compiled or executed** in the current tool container because rustc and Rscript were not installed:

```sh
rustc --test rust/long_run.rs -o /tmp/rithm28_rust_test && /tmp/rithm28_rust_test
rustc -O rust/long_run.rs -o /tmp/rithm28_rust && /tmp/rithm28_rust source_routes_compact_LOCAL_ONLY.csv
Rscript R/session_audit.R results/p28_panel_bounds.csv
```

Results included: `results/p28_go.json`, `p28_cpp.csv`, `p28_panel_bounds.csv` (432 aggregate group-treatment-policy-budget rows), `p28_history_audit.json`, and `p28_external_evidence_gate.json`. The Go/C++/Ruby positive verification is source-derived **counterfactual constrained mathematics**, not a measured new treatment. No person-linked GPS coordinates or original human individual XLSX redistributed.
