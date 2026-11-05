# P3-R17 — Ponytail-guided Ruby fix: mutation sensitivity audit (2026-11-05)

## Research question

After a minimal patch tightened `resource_bounds(k:)` to accept only finite, real nonnegative costs, do existing regression tests actually detect nearby incorrect implementations? This measures **test sensitivity to selected faults**, not a causal productivity advantage from Ponytail.

## Exact source evidence

On Ruby 3.3.8, the two exact GitHub `main` source/test files were checked via `git hash-object`:

- `occupancy_churn_bounds.rb` -> `2a52f8c850a6eabab47aea1ac6b92d449d8fa7ae`
- `test_occupancy_churn_bounds.rb` -> `e23aaf2566835fca828ff917d0d35a67267532ee`

Baseline `ruby test_occupancy_churn_bounds.rb`: **4 runs, 1,148 assertions, 0 failures/errors/skips**.

## Four fixed deliberate mutations

The audited [`mutation_sensitivity_review.rb`](mutation_sensitivity_review.rb) copies each implementation into a temporary directory, substitutes exactly one fixed source expression, runs the unchanged test suite via `Open3.capture3(RbConfig.ruby, ...)`, then removes the temporary directory. The original repository source/test files are never rewritten, the subprocess uses no shell, and no real research participants or private data are accessed.

| Mutation | Scientific/engineering failure modeled | Outcome |
| --- | --- | --- |
| `finite_guard_removed` | Permit infinite cost and lose real-number domain guarantee | Detected |
| `minimum_signed` | Replace `|b-a|` by `b-a` | Detected |
| `maximum_inverted` | Choose larger instead of smaller feasible gross bound | Detected |
| `max_cost_uses_min` | Use lower gross switch bound for upper resource cost | Detected |

**Observed: 4/4 mutants killed**, each subprocess returned an unsuccessful test exit code. Baseline source remained 1,148/1,148 assertions PASS.

This is a **deliberately selected four-mutant set**, not a representative fault distribution. Therefore 100% here must not be interpreted as a general mutation score, a novel economic identification result, or an experimentally established Ponytail-vs-no-Ponytail uplift.

## Reproduction

```sh
ruby ruby/rithm210/p3/test_occupancy_churn_bounds.rb
ruby ruby/rithm210/p3/mutation_sensitivity_review.rb
```

The RITHM P3 read-only GitHub Actions workflow is updated to include this script; its remote Actions execution status must be checked independently before declaring CI PASS.

## Engineering interpretation

The case supports retaining the one-line guard patch and its bounded tests: the test suite detects selected changes in **domain correctness and interval arithmetic**. Further evaluation should use a preregistered set of bugs, independent blinded baseline/Ponytail reviewers, equal tool/time budgets, and explicit failure reporting.
