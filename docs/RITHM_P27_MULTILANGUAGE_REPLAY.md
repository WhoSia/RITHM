# RITHM-2.7 P27 — Ruby / Rust / Go / C++ / R human-welfare response envelope

The P27 research question is whether observed historical human C-stage profiles + explicitly stated *hypothetical* response restrictions can fix the **sign** of additional guidance's group cost change. **No new advice policy was observed.** Original S2 human experiment source must remain separate from 2025 Seoul sensors.

## Active languages (Python is NOT the lead)

| Lead role | Language | File | Executed in this tool environment? |
|---|---|---|---|
| Source custody and replay orchestration | **Ruby** | `ruby/derive_group_states.rb`, `ruby/verify_envelopes.rb` | YES, PASS |
| Canonical zero-dependency exact bound kernel candidate | **Rust** | `rust/exact_bounds.rs` | NO: `rustc` not installed; source authored, tests provided |
| Executed typed source checker / policy enumeration | **Go** | `go/bounds.go`, `go/bounds_test.go` | YES, 4/4 Go tests PASS |
| Independent low-level enumeration | **C++17** | `cpp/exact_bounds.cpp` | YES, compiled and crosschecked 9/9 |
| Session-aware statistical audit | **R** | `R/validate_group_welfare.R` | NO: R not installed; source authored |
| Historical model replay only | Python | P25/P26 existing archives, NOT this code path | no new Python research program |

## Run in this order

From package root (no Python needed):

```sh
# Historical author-S2 human routes converted earlier to 24 de-identified compact records.
# This input is NOT distributed in the ZIP: use verified RITHM GitHub source.
ruby ruby/derive_group_states.rb /path/to/rithm23_wijayaratna2017_routes.csv results/2017_group_states_derived.csv

GO111MODULE=off go test ./go -v
go run ./go/bounds.go results/2017_group_states_derived.csv > results/bounds_go.json

g++ -std=c++17 -O2 -Wall -Wextra -Werror cpp/exact_bounds.cpp -o /tmp/rithm_p27_cpp
/tmp/rithm_p27_cpp results/2017_group_states_derived.csv > results/bounds_cpp.csv
ruby ruby/verify_envelopes.rb results/bounds_go.json results/bounds_cpp.csv

# On machines with properly installed Rust and R:
rustc --test rust/exact_bounds.rs -o /tmp/rithm_p27_rust_tests && /tmp/rithm_p27_rust_tests
rustc -O rust/exact_bounds.rs -o /tmp/rithm_p27_rust && /tmp/rithm_p27_rust results/2017_group_states_derived.csv
Rscript R/validate_group_welfare.R results/2017_group_states_derived.csv results/bounds_cpp.csv
```

Go/C++/Ruby computations already executed against the derived 480 original group-round states. Their saved outputs are included. Rust/R **not** executed in the tool container; future successful execution is not implied. Runtime installation on the user's friend's server is outside scope and should never modify global versions/settings without owner's permission.

Research note: `docs/P27_SCIENTIFIC_REPORT.md`. Source panels copyright/copyleft credit: Wijayaratna et al 2017 PLOS ONE, CC BY. Only derived group aggregates (not personal data or original copyrighted paper/full workbook) provided.
