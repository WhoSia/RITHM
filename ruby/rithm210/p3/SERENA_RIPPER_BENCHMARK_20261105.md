# P3 Ruby semantic-navigation baseline for Serena — 2026-11-05

## Goal

Test whether a symbol-aware coding MCP (Serena) adds useful information to real RITHM Ruby work compared with ordinary text search. **Do not** claim Serena improved accuracy before an original isolated Serena process has performed real `find_symbol` calls.

## Actual current RITHM source inventory (GitHub `main` readback)

| Module | Expected method names | Definitions |
| --- | --- | ---: |
| `occupancy_churn_bounds.rb` | `check!`, `possible_pairs`, `gross_range`, `possible_gross`, `resource_bounds`, `congestion_cost` | 6 |
| `friction_welfare.rb` | `rational`, `validate`, `stationary?`, `interior_stationary_band`, `social_cost`, `excess_at_zero_bias`, `inertia_bound`, `step`, `pulse_example` | 9 |
| `turnover_coupling_witness.rb` | `distributions`, `summarize`, `witness` | 3 |
| **Total** | | **18** |

The expected names were cross-checked using GitHub source text with simple anchored `def` matching; full source AST results are to be independently verified in the GitHub Ruby workflow. Source blob IDs: `2a52f8c850a6eabab47aea1ac6b92d449d8fa7ae`, `6dbd5613206b412d8df660ee4ccf5b6a96b59303`, `b3fe44af62f840272c1fe94cea47e455b0a053c8`, respectively.

## Experiment 1 — AST vs naive lexical search

A small public synthetic Ruby snippet has one comment that resembles a method definition, one string containing `def`, a real instance method and a real singleton method. The naive regular expression `/\\bdef\\s+[\\w!?.]+/` reports **four** matches (two false positives); Ruby 3.3.8 `Ripper.sexp` reports **two real methods**, at lines 4 and 5. Local test subset: **3 runs, 6 assertions, 0 errors or failures**. This is a toy false-positive comparison, not a general empirical superiority claim.

The new `readonly_symbol_inventory.rb` uses the standard-library AST, rejects parse errors and over-64KiB snippets, and returns symbol names and line numbers without executing source. `test_readonly_symbol_inventory.rb` compares the actual three local RITHM module files against the fixed 18-name gold standard. This full exact-file test was committed to GitHub but its **new CI run result is not yet confirmed**.

## Experiment 2 — original Serena MCP (staged, separate repository)

The MCP-Hub branch now contains a fixed **public synthetic** Serena Ruby project and the original pinned `oraios/serena@ede329aaf0c824bea75455a2926f01420d7aa620` invocation. It explicitly asks for only `find_symbol`, prevents source-body return, and removes inherited credentials and writes. It requires a real MCP `tools/list` and two actual `find_symbol` calls for `resource_bounds` and `gross_range`; the original integration workflow uses a disposable CI runner and must be observed PASS before promotion.

Potential benefit: richer name-path and symbol-reference retrieval over naive text search. This is a hypothesis pending an original provider test and broader task sample. The read-only project is not a proof of OS-level sandbox isolation: test it only in a disposable runner without private mounted paths or secrets.

## Scientific and operational limits

- No participant records, original empirical CSVs, local research drive or authentication tokens are read.
- No claim of a new combinatorial theorem, causal welfare effect or superiority in productivity.
- Ruby standard-library baseline code and test may be kept even if Serena's original CI fails; no external runtime dependency is required.
- The `.github/workflows/rithm-p3-readonly-symbol-baseline.yml` is read-only and never creates a `github-actions[bot]` commit.
- Exact RITHM original occupancy cost test still separately passed in the prior Git blob-matched local run (4 runs/1,148 assertions). This new semantic baseline adds different tests; **their remote CI results remain a separate gate**.
