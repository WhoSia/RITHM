# RITHM-2.10 P3-R37 — Nondegenerate negative-control gates and author-model matched-source contest

**Date:** 2026-11-11  | **Source:** original author's `data_task_all_switch_230705.csv` SHA-256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. **Status:** original-source 24-session exploratory replay PASS; EWA-lite, SSM5, SSM1–9 independently reimplemented from original manuscript appendices, NOT the authors' exact program; reward-learning causal claim HOLD, external independent validation HOLD, remote Actions CI HOLD.

## 1. Competing scientific objectives

RITHM R33/R34 found predictive advantages of lawful online received-payoff and selected-route habit features. R35 showed travel Value, stated by experimenters to be independently assigned *after route choice*, correlated with both next switch and already-decided current switch under its particular group×period×current-route×information partition. R36 found that adding both past and current route into the partition makes the negative-control outcome definitionally constant and therefore unusable as a diagnostic. R37 separately (i) establishes a **nondegenerate, predecision-history conditioned** falsification gate and (ii) compares the authors' actual EWA-lite and SSM algorithms in **teacher-forced, period-by-period** prediction on the identical official-paper Partial population. These aims must not be mixed into a causal claim.

## 2. Original source and legal information filtration

Original manuscript (2026-07-24), §3, §§5.3, Appendix A.1–A.2, Appendix B.1 and Table 12. Paper-main population excludes pilot session 2 and anomalous session 101, retains 24 sessions and 48 stable Partial six-person groups, 39 next-choice forecasts per group, yielding **1,872 group-periods / 11,232 decisions**. Each group consists of three always-informed and three uninformed actors in Partial. The **actual observed previous payoff** is available to all; informed actors receive previous route counts, letting them infer previous *unilateral foregone payoffs* from own realized payoff and the known cost schedule. Uninformed subjects do not have access to private experimenter `Value`, previous exact `Cost`, previous group occupancy, or foregone payoff. Information-gated code enforces this.

Original-author small sample models are **prior art**, not models invented by RITHM:

* **SSM5:** each informed person draws 5 prior periods with replacement and compares full-information actual/foregone payoff means; each uninformed person draws 5 samples independently among periods **where that route was actually chosen**, or chooses randomly if a route was never chosen.
* **SSM1–9:** sample size `q_i ∈ {1,...,9}` is assigned per person and stays stable. R37 uses a declared **Bayesian filtering posterior over `q_i` from preceding observed choices** for conditional source-trace prediction. This posterior inference is **R37's observational implementation**, not a statement about how authors simulated q_i.
* **EWA-lite:** implement Appendix A's initial `N(0)=1, A_A(0)=A_B(0)=1`, posterior-uniform inference over feasible number of other A drivers for uninformed actors (payoff and bounded hidden Value), time-adaptive surprise-based `φ=1-S/2`, attention `δ_j=1` for chosen route or foregone payoff ≥ actual, and attraction logit `P(A)=logistic(λ(A_A−A_B))`. Estimate one nonnegative `λ` on **20 training sessions** per fold by likelihood; **four heldout sessions** remain untouched. EWA source implementation is reauthored using the manuscript; actual author's experiment execution code not present in supplied R analysis ZIP. Tests reproduce explicit Appendix A Tables 10/11 examples.

Each period is **teacher-forced**: historical choices and received payoffs are the real source histories; the model predicts only the next observed route, not a newly simulated evolving trajectory. Source-replay and 40-period generative simulation are different scientific tasks. Tie decisions in SSM are resolved 50:50 because Appendix B doesn't specify the implementation detail explicitly. No test outcomes select model tuning parameters. The six-choice joint law for the SSM/EWA contest is the **product of six actor forecasts**; dependence models such as R26 are not given to these author baselines or added silently.

## 3. Matched-source next-choice prediction (lower better)

| Model | Actor logloss | Six-person independent joint logloss | Occupancy logloss | Group congestion cost forecast MAE |
|---|---:|---:|---:|---:|
| Author Appendix B SSM5, raw | 1.147847 | 6.887084 | 2.485147 | 3.494415 |
| Author Appendix B SSM1–9 fixed-q posterior, raw | 1.037699 | 6.226193 | 2.290426 | 3.488179 |
| SSM5 **plus separately labelled train-only neutral-mix calibration** | 0.606502 | 3.639012 | 1.493325 | 3.715435 |
| SSM1–9 plus same train-only calibration | 0.595744 | 3.574463 | 1.509420 | 3.750345 |
| **EWA-lite from Appendix A, train-only λ** | **0.542202** | **3.253211** | **1.429131** | **2.899252** |
| **RITHM R33 both online choice and payoff, previously archived sixfold** | **0.512930** | **3.077581** | **1.392895** | **2.744521** |

RITHM has the best source-trace scores in this *exploratory* comparison. **This is not yet a complexity-matched or independent-data comparison:** RITHM has many learned regression coefficients, EWA only one λ and SSM fixed memory rules; the same source records were repeatedly studied during R23–R36. EWA per-fold selected λ ~0.29135–0.31302; SSM5 train-only mix with neutral 0.5 selected 0.4 all folds, SSM1–9 selected 0.2–0.3. Neutral mixing is **not the author's SSM**. This sensitivity shows uncalibrated SSM is far too sharp for logloss, but its cost-MAE may worsen under probability calibration. EWA source replay and selected λ appear plausible relative to original paper's pooled MLE ~0.27, but **do not constitute exact author-code replication**.

**If comparing to RITHM R30 joint latent-shock scores, separate that task.** This table intentionally uses the R33 independent six-mask benchmark so no model receives a latent-correlation advantage denied to others. No refitted R33 calculation was run in this particular R37 command: its values come from the earlier SHA-verified, fixed-sixfold archived R33 output and are labeled accordingly.

## 4. R37 valid-vs-degenerate predecision placebo gate

Analyzed original Partial `t=2..39` (**10,944 source actor-periods** with both earlier and next route choices), using conditional permutations of hidden current travel `V_t` within groups of >=2. Do not select stratum by its observed outcome; report predecision negative-control variation explicitly. Compare `current switch=1{Y_t!=Y_t−1}` (causally prior to drawing `V_t`) and `next switch=1{Y_t+1!=Y_t}` (potential response to feedback).

| Group×period strata also conditioned on | n eligible | Already-decided switch slope, p(999) | Next switch slope, p(999) | Negative-control power |
|---|---:|---:|---:|---|
| informed only | 10,944 | −0.003081, p≈0.078 | −0.009182, p≈0.001 | 2,143 variation-bearing cells |
| **previous route, informed** | **8,396** | **−0.000569, p≈0.780** | **−0.010367, p≈0.001** | **1,541 variation-bearing cells** |
| current route, informed | 8,394 | −0.006473, p≈0.003 | −0.007416, p≈0.003 | 1,533 variation-bearing cells |
| **previous AND current route, informed** | 5,906 | **0, p=1 by definition** | −0.007197, p≈0.007 | **0 variation-bearing cells: INVALID as an NC test** |

A more diagnostic **previous-route-only** comparison has nonzero variation in an already determined behavior and no detectable association at the current permutation resolution. However this comparison was developed **after observing R35/R36**, making the apparent success post-hoc and exploratory; it also changes the eligible source subset and can retain within-person prior history imbalance. The after-minus-before contrast in the same previous-route cells is **−0.009797** (999-permutation p≈0.001), but subtracting two outcomes doesn't automatically identify the effect of reward. Experimental `Value` allocation code/randomization logs remain unavailable. The manuscript describes independent postchoice assignment, yet the conditional randomization mechanism has not been authenticated. **No causal effect or valid IV identification is claimed.** The previous R35 warning is not deleted: it remains correct under its different conditioning rule.

A negative control can be non-associated yet uninformative because of zero variance; conversely a nondegenerate candidate can *appear* favorable when selected after many analytic attempts. A reliable R37 validity gate requires: (1) the negative-control outcome is causally prior to the current `V_t`; (2) predecision outcome variation within the conditioning cells; (3) documented randomization/exchangeability; (4) no post-hoc selection of the successful conditioning; (5) independent replication or pre-registered validation. Here (1),(2) pass under previous-route cells; (3)–(5) are HOLD.

## 5. Tests, reproducibility and publication authority

Source-free regression tests check (i) exact q=5 resampling probability, (ii) ties and absent-route policy, (iii) uninformed `NumA` leakage invariance, (iv) informed counterfactual responsiveness, (v) fixed-q posterior, (vi) manuscript Appendix A Tables 10/11 payoff intervals, (vii) six-choice and occupancy distribution normalization, (viii) nondegenerate vs vacuous placebo construction. **11/11 PASS** locally with Python 3.13, NumPy and SciPy. R37 complete raw source replay performed on the original SHA-sealed CSV using private local files. Neither a participant row nor the original CSV is bundled with this report.

Sealed source-free code and JSON report correspond to the local computations. Distinguish GitHub remotely published file SHA parity and Actions successful workflow from local tests: without a clean remote checkout and actual CI receipt, **remote CI remains HOLD**. GitHub-bot contributor is prohibited; only WhoSia author/committer is acceptable.

## 6. Novelty and R38 gates

The authors' Appendix A and Appendix B already posit that changed sensitivity to payoffs or small samples can generate under/overreaction; RITHM must not claim newness of basic payoff learning, adaptive attention, or information congestion. Genuine potential result: validated information-bound individual choice features + person-level historical memory + properly conditioned six-person joint distribution with distinct proper scoring, under an explicit negative-control power audit and a heldout predictive experiment.

**Priority R38:** (P1) obtain original randomizer/assignment timing logs and preregister a stable prior-route NC to avoid post-hoc selection; (P1) clean GitHub checkout CI and exact author EWA/SSM implementation audit; (P1) predeclare small incremental models and compare on entirely new session data; (P2) reduce model complexity via effective degrees-of-freedom/score penalty and compare against EWA; (P2) separately validate unconditional author simulations vs RITHM stochastic dynamics. Maintain two tracks: robust prediction versus still unverified causal reward effects and cognitive hassle.