# RITHM-2.10 P3-R15 — Joint-Event Calibration and Micro-to-Macro Research Decision

2026-11-05 KST. Original-data exploratory analysis; all causal, novel-mechanism and external-validity claims HOLD.

## Dataset, estimand and procedures
Reused the author-approved Drive original ZIP, with the extracted experimental CSV SHA-256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb` verified in the local runtime. 24 sessions, 5,616 filtered six-person group transitions. The fixed historical target is Full-information treatment, current efficient A-occupancy n=4, early periods1–10 (N154) and late30–39 (N257), 411 groups. The current-n4 conditioning is observational. Model probabilities exclude entire heldout sessions from fitting (six folds of 20 train/4 heldout). The fixed epoch-conditioned independent actor model uses actor's treatment, information, previous route, personally experienced cost, training-only epoch frequencies and alpha20 shrinkage. Compare with the previous simple actor Markov. Within-source model design has already used this experimental record repeatedly, so holdout does not imply pristine prospective replication.

Use independent Poisson-binomial convolution for U=B→A and D=A→B, and the *joint* (U,D) logloss, *next occupancy* logloss, P(no gross switch), P(U=D>0), and respective Brier scores. Source-bearing subject-level rows are not committed publicly. Source-free Ruby checks verify convolution normalization, exactly computable cancellation and conditional expected next-cost.

## Main findings

| Metric | Markov early | Epoch-indep early | Markov late | Epoch-indep late |
|---|---:|---:|---:|---:|
| Joint U,D logloss (lower better) | 2.151071 | 2.015505 | 1.430521 | 1.356560 |
| Next-occupancy logloss | 1.419512 | 1.378187 | 1.059308 | 1.007047 |
| No-switch forecast | .364838 | .205616 | .365254 | .531107 |
| No-switch empirical rate | .220779 | .220779 | .583658 | .583658 |
| Opposing cancellation forecast | .114636 | .178766 | .114431 | .060264 |
| Opposing cancellation empirical rate | .155844 | .155844 | .077821 | .077821 |
| No-switch Brier | .194323 | .173781 | .291703 | .246843 |
| Cancellation Brier | .133419 | .132374 | .073406 | .072273 |

The epoch-independent model improves all four reported mean logloss cells, but not every metric and not every epoch equivalently. It overpredicts early cancellation and underpredicts late cancellation. For selected groups, early average gross-switch *absolute error* slightly worsens (.851442→.870721) even though the *aggregate average gross forecast* improved in P3-R14. Therefore mean calibration, event-score improvement and individual group error are different estimands.

20,000 paired **whole-session bootstrap reweightings** (seed20261105) conditional on the already-fitted CV predictions yield epoch-minus-Markov differences:
- Early joint logloss -0.135566, exploratory percentile95 [-.256205,-.024879].
- Late joint logloss -0.073962, exploratory percentile95 [-.150763,+.026849].
- Early next-occupancy logloss -0.041325, CI [-.093727,+.004888].
- Late next-occupancy logloss -0.052261, CI [-.092744,+.000075].
- Early no-switch Brier delta -.020542, CI [-.047729,+.009627].
- Late no-switch Brier delta -.044860, CI [-.076152,-.005000].
These intervals omit refitting uncertainty and do not correct for repeated study/data-dependent target/model selection. They are NOT confirmatory independent tests.

## Calibration-dependence identification boundary
For any admissible information set H, let q_i=E[Y_i|H], predicted p_i, and conditional bias b_i=q_i-p_i. For i≠j:
E[(Y_i-p_i)(Y_j-p_j)|H] = Cov(Y_i,Y_j|H) + b_i b_j.
Hence a nonzero residual cross-product can arise with conditionally independent decisions when the individual conditional probabilities are misspecified, even if marginal mean calibration is excellent. Also, Cov(Y_i,Y_j|H) can arise from a latent common shock, without causal peer influence. The opposing-route residual sign in R14 thus does not identify strategy, intentional cancellation or communication.

The R13 exact welfare identity remains true observation-wise, but its four components are a **diagnostic attribution** and are not uniquely causal effects. The strong epoch-independent baseline's substantial predictive success is evidence against over-interpreting the earlier simple Markov's error as group coordination.

## Directional decision: original RITHM mission over leaderboard
Main question: **Under information actually accessible to individual actors, what experimentally distinguishable learning and update-clock mechanisms generate group occupancy, hidden opposing turnover, recovery after disturbances, and cumulative finite-horizon congestion welfare?**

The separate RITHM-2.10 identifiability and joint-switch prediction modules remain supporting methods. Avoid a paper centered on a tiny logloss gain, a mechanical algebraic decomposition, or an existing result that asynchronous play converges but synchronous play can cycle. Historical P3-R9/R10 reference-clock models are useful precisely as counterexamples and for intervention design, not human-identified models.

Proposed next gates:
1. **R16:** score a precommitted, genuinely information-feasible individual learner against fixed independent alternatives on all occupancy states, not only selected n4. Include joint (U,D), zero/cancellation events, and 40-period welfare trajectories. Train-only tuning, nested session folds where possible; report conditional vs global diagnostics.
2. **R17:** derive separable information-update-clock intervention contrasts on a finite-state process with actual legal information timing, and identify what extra observations/randomization make these contrasts estimable.
3. **R18:** independent experiment, data source, or prospective randomized manipulation of signal quality and adjustment scheduling; use the above predictions without tuning on final evaluation sessions.
4. Keep previous P3-R12/R13/R14 research and counterexamples intact. Promote specific publication claims only after strong prior-art and external evidence reviews.

## Implementation and evidence
- [Source-independent joint diagnostics](p3/joint_epoch_diagnostics.rb)
- [Synthetic tests](p3/test_joint_epoch_diagnostics.rb)
- [P3-R14 actor independent epoch model](p3/epoch_independent_welfare.rb)
- [R14 original-byte-sealed report](https://drive.google.com/file/d/1Z4AJpuWyAuyHh93Ob2XY-p19FH93EpjN/view)
- Synthetic local Ruby tests of the source-equivalent algorithm: 3 tests, 11 assertions, no failures.
- Original source was run in the current local runtime for the 411 selected groups and 20,000 reweighted samples, with aggregate-only report.
- **HOLD:** exact final GitHub checked-out-SHA execution, remote Actions PASS, new external data, prospective causal identification, originality certification. CI workflow is read-only and `github-actions[bot]` author/committer is forbidden.
