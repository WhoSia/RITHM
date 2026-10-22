# RITHM 2.9 P19 — Ruby friction / Nash court

This is an **exact finite-game witness verifier**, not a T3 global maximum solver.

- `friction_court.rb`: exact Ruby `Rational` matrices for STOP0, STOP1, COMPUTE, separately parameterizing computational fee `F`, route-switch fee `k` and mismatch loss `L`. A *single* common four-public-state future-value map can be evaluated by exact bilateral deviation checks.
- `test_friction_court.rb`: all-horizon witness, additive state-independent continuation, rejection of invalid friction/mixed strategies, and a test that nonconstant continuation affects deviations.
- Local test command: `ruby ruby/rithm29/p19/test_friction_court.rb`; Ruby standard-library minitest, no external gems.

## Exact proof boundary

For `F=1,k=1/2,L=2`, `stationary_witness(T)` independently recomputes the all-state one-round Nash deviations and certifies *attainability* of social cost `11*T/2` for each positive integer horizon T, by state-independent continuation induction. This is a lower-bound witness only.

**Unsolved:** optimize T3 jointly over every reachable T2 continuation vector and all four public-state Nash policies, including degenerate supports and continuum families. The inherited bracket is `33/2 <= max W3(00) <= 18`. **No exact maximum or improved upper bound is claimed.** The present Ruby code does not enumerate every equilibrium.

## Empirical identification boundary

In the external Partial-information experiment, three of six group members receive information. The previous Monte Carlo label test assumes all `choose(6,3)=20` assignments are equally probable within each group. This needs confirmation against original author assignment code. Group interference means the sharp no-effects randomization test is not an individual direct-effect estimate. Previous route and cumulative switching are post-treatment.

The empirical six-person route-choice game and theoretical two-person XOR program game are different games. Experimentally randomized information access does **not** identify a fee for COMPUTE (`F`) or switching friction (`k`). New calibrated structural claims require new assumptions and tests.

## RAVEL gates

`SOURCE → MODEL CONTRACT → EXACT WITNESS → ADVERSARIAL DEVIATION TEST → CLAIM SCOPE → CI RECEIPT`.

A local PASS is not a GitHub Actions PASS. Avoid changing source CSV, inventing a verified global optimum, or promoting an untested causal mechanism. Ruby remains the primary implementation; add independent verification after the Ruby contract stabilizes.