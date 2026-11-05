# P3-R16 Ponytail Ruby input-domain correction — exact source verification (2026-11-05)

## Finding and limited scientific meaning

The historical RITHM six-actor occupancy-churn benchmark in `occupancy_churn_bounds.rb` calculates sharp switching-count bounds from observed occupancy. The finite, nonnegative *real* per-switch resource cost `k` belongs to its declared domain; it is not a behavioral psychology parameter.

The earlier guard checked only `k.is_a?(Numeric) && k >= 0` and let `Float::INFINITY` through. For an observed `[4,4]` path this produces a mathematically non-finite cost rather than a valid identified interval. `Complex(1,0)` failed with a Ruby comparison exception before meaningful domain validation.

Applied the original upstream pinned [Ponytail v5.3.3](https://github.com/DietrichGebert/ponytail/tree/7801d061243d7b753bad0e0b3c057cd250b11755) guidance as **review instructions**, not as an independently installed MCP or separate agent:
- [Production one-line condition change](https://github.com/WhoSia/RITHM/commit/5742953e7b21f39ca09c369dab38f30978d2fc33): `k.is_a?(Numeric) && k.real? && k.finite? && k >= 0`.
- [Boundary assertions](https://github.com/WhoSia/RITHM/commit/d79f4bd6fda6477562da38f797d5fd5edef3e7f0): Infinity, NaN, Complex(1,0) rejection; rational 1/3 preservation.
- One production line modified, four assertions added, zero new dependencies.

## Newly completed exact-file verification

The *two exact current GitHub `main` file contents* were fetched using the connected GitHub integration and reproduced byte-for-byte in a local Ruby 3.3.8 directory. Their actual Git blob SHA-1 were computed with `git hash-object`:

| File | Git blob SHA-1 (matched GitHub) |
|---|---|
| `ruby/rithm210/p3/occupancy_churn_bounds.rb` | `2a52f8c850a6eabab47aea1ac6b92d449d8fa7ae` |
| `ruby/rithm210/p3/test_occupancy_churn_bounds.rb` | `e23aaf2566835fca828ff917d0d35a67267532ee` |

Command run against the exact pair: `ruby test_occupancy_churn_bounds.rb`.

**Result:** 4 runs, **1,148 assertions**, zero failures/errors/skips (Ruby 3.3.8). This supersedes the earlier structural-reimplementation-only 858-assertion evidence for this test pair. It does **not** prove that every other test in RITHM passes, or that a remote GitHub Actions run passed at that SHA. In particular, do not claim reproduction of private empirical CSV data or independent generalization.

Additional direct boundary replay on the same matched files: `Float::INFINITY`, `Float::NAN` and `Complex(1,0)` all raise `ArgumentError`; `Rational(1,3)` returns exact maximum cost `4/3`.

This is evidence of a fixed domain-validation bug and regression-free **tested cases**, not of a new welfare theorem, independent strategic behavior, causal intervention effect, or a quantitatively proven Ponytail-vs-baseline efficiency gain.

## Independent cross-tool mathematical check

The connected Wolfram MCP (Wolfram Language evaluation, separate from Ruby) was used to enumerate every binary assignment of six or fewer actors and, more generally, all `n=1..8` occupancies. For each `(n,a,b)`, brute-force actor assignments were compared with the exact predicted feasible gross switch sequence

```
Abs[b-a], Abs[b-a]+2, ..., Min[a+b,2*n-a-b].
```

Wolfram returned **284 occupancy parameter cases, zero mismatches**. This independently checks the existing formula across finite `n<=8` and reinforces the Ruby `possible_gross` tests. It is **not** a formal proof for arbitrary `n`, and it does not involve experimental participant data, stochastic behavior calibration, or novel mathematics.

## Research-operation boundaries

No original participant rows, researcher tokens, source archives or new datasets have been committed. GitHub Actions must not create bot-authored commits. A larger Ponytail evaluation would require randomly assigned comparable public Ruby defects, a baseline arm, an independent tester, and verification of exact test results on both arms.
