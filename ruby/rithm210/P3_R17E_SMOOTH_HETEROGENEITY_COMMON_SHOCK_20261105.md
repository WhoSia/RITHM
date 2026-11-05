# RITHM-2.10 P3-R17E — Smooth Response, Non-Lumpable Heterogeneity and Latent Shock Negative Controls

Date: 2026-11-05 KST. **Status: synthetic numerical counterexamples and exact model identities; NO new human experiment, causal mechanism or paper novelty claim.**

## Motivation and baseline
[P3-R17A–D](P3_R17_INFORMATION_CLOCK_FACTORIAL_WELFARE_20261105.md) found large effects of within-round information refresh using a discontinuous near-greedy six-agent response law. A 56-cell finite rational tremble×initial-occupancy grid gave negative or zero signed one-step interaction. This is not a universal theorem. To attempt falsification, replace the threshold response with a smooth logistic law and permit persistent actor heterogeneity and a round-common unobserved shock. Preserve **six per-person modification opportunities per macro round**.

With incumbent route s_i, publicly perceived A occupancy n*, unilateral improvement Δ_i(n*) equals 3n*−14 for an A user and 11−3n* for a B user. Define, for ε∈[0,0.5], slope k≥0, fixed actor bias b_i, common shock z,
p_i(switch|n*,z)=ε+(1−2ε) σ(kΔ_i(n*)+b_i+z),
σ(x)=1/(1+e^(−x)).
The common shock uses a binary draw ±h once per macro round; individual Bernoulli decisions are **conditionally independent given z**. The frozen protocol has identical full 64-bit outcome probabilities for simultaneous and uniform-random sequential scheduling even with biases and common shock: signal remains fixed and each person acts once.

## R17E.1 — One-step sign reversal with a smooth and homogeneous response
At ε=.1, b_i=z=0, initial nA=0, k=.05, signed interaction
(E excess(seq,refreshed)−E excess(seq,frozen))−(E excess(sim,refreshed)−E excess(sim,frozen))
= **+0.25715826**.
At initial nA=4 with the same parameters the interaction is **−0.97811787**; nA=2 gives −0.16831995, nA=6 gives −2.16662067. Increasing k to .20 at n4 gives −2.44906445. Consequently the R17D nonpositive finite-grid finding does not extend to all smooth response families or initial states. This is a finite exact-DP-in-probabilities, double-precision numerical counterexample, not a novel general result.

## R17E.2 — Horizon-dependent sign
For a HOMOGENEOUS response we independently compute seven occupancy transition kernels from the full labelled 6-bit DP, then propagate the predicted 7-state chain for 40 rounds (start occupancy n1 and 39 further states; ε=.1, k=.05). Starting n1=0, a one-step sequential-refresh intervention can INCREASE expected excess next cost relative to frozen by +0.25715826, while the 40-period cumulative interaction is **−25.64999** cost units (frozen ~302.84628 versus sequential refreshed ~277.19629). The one-step versus multi-step sign difference arises from future state redistribution; treating short-term policy harm as evidence of long-run harm would be wrong. All effects are fully synthetic.

## R17E.3 — Occupancy-state lumpability FAILURE with fixed actor types
The original seven-state macro chain assumes permutation exchangeability of six agents, conditional on occupancy. With persistent actor biases it is generally invalid.

Take six actors, ε=.1, k=.7, b_0=+2, b_1..b_5=0; compare labelled initial route masks 15 (binary 001111) and 30 (binary 011110), each nA=4 but with the special actor 0 on a different route. Both start with identical total congestion C(4)=24. Their **one-period next occupancy distributions differ by total variation ~0.26319224** under a frozen/simultaneous protocol. Thus nA alone is not a Markov sufficient state for this heterogeneous agent law. Exact 64-state autonomous 40-period welfare forecasts differ: expected cumulative excess **548.08110 versus 547.82038** respectively. By contrast, with all biases zero the model is exchangeable: a 64-state labelled rollout equals an independent seven-state macro rollout at 40 periods to numerical precision.

This is a straightforward known consequence of Markov state aggregation/lumpability, not original by itself. It is nonetheless a crucial MODEL VALIDITY gate for RITHM: a fitted actor-specific history model cannot simply be treated as a seven-state n-only transition kernel without retaining or marginalizing over persistent actor composition in a history-consistent way. A mixture of hidden actor identities generally produces memory at the occupancy level.

## R17E.4 — Common-shock residual pairs without direct peer response
Set initial mask 15, ε=.05,k=.7, b_i=0, and a single equally likely shared shock z∈{−2,+2} drawn before six independent decisions. For distinct actor switch indicators Y_i,Y_j and their conditional shock-specific probabilities p_i^±, p_j^±:
Cov(Y_i,Y_j | initial group state) = ((p_i^+−p_i^−)(p_j^+−p_j^−))/4,
even though Cov(Y_i,Y_j|z,initial state)=0.

Numerical example: average same-route pair switch covariance **+0.08041559**, average opposing-route covariance **+0.08978344**. With route displacement signs s_i=−1 for A→B and +1 for B→A, the *expected excess-welfare difference* between true binary-shock mixture and independent actor Bernoullis fitted to the SAME marginal switch rates is
6Σ_{i<j} s_i s_j Cov(Y_i,Y_j)= **−0.93215051**.
Indeed, mixture next excess cost **4.21674339**, independent marginals **5.14889390**, matching the exact quadratic identity. The negative opposing-route welfare-residual contribution exists with **ZERO peer-to-peer causation**.

Therefore the signed pair residual from historical R13–R15 could have arisen from shared group uncertainty, even with individually correct marginal probabilities. This synthetic witness is not evidence that the original experiment *actually* had this shock; identifying its source needs new measurements/interventions.

## Audit and follow-up
Code:
- [Smooth labelled six-person transition DP](p3/smooth_signal_clock.rb)
- [Exchangeable-only seven-occupancy 40-step welfare chain](p3/smooth_clock_welfare_rollout.rb)
- [Non-exchangeable 64-state 40-step welfare chain](p3/labeled_smooth_welfare_rollout.rb)
- [Common-shock signed residual counterexample](p3/latent_shock_residual_counterexample.rb)
- Four source-free Ruby minitest suites and read-only CI integration.

A separate local Ruby 3.3.8 source-equivalent implementation passed **14 tests / 421 assertions / 0 failures**. The committed GitHub tests are related but not byte-identical to all local fixtures; thus final checked-out SHA source test, actual GitHub Actions PASS and additional testing on non-synthetic human data remain **HOLD**. No personal data, original paper bytes or downloaded ZIP are committed.

Scientific direction:
1. R17F should remove the partially degenerate simultaneous-refreshed factorial by distinguishing **truthful previous-period disclosure versus truthful current-period disclosure** and a separately randomized **within-round feedback switch** when all actors act sequentially. Timestamp every report and hold six opportunity slots constant.
2. R18 should pre-specify session-cluster outcomes (40-period welfare, signed pair residual, occupancy-state insufficiency), randomization and power, and collect genuinely new participant data before causal mechanism claims.
3. Compare original Noussair–Qiao SSM/EWA and strongest feasible actor-learning baselines; what is already known in stochastic adjustment, Poisson-binomial switching and lumpability must not be promoted as new theory.
