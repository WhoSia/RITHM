# RITHM-2.10 P3-R12 — Heldout Actor Heterogeneity Cannot Yet Explain Optimal-State Adaptation

**2026-11-05 KST. Research stage:** independent original-CSV replay and exploratory 24-session cluster uncertainty. **Does not demonstrate strategic dependence or identify a novel cognitive mechanism.**

## Question
In P3-R11 the six-person homogeneous independent switching benchmark, fitted within an early or late epoch using only mean gross switches, overpredicts the next conditional group congestion cost. That alone does NOT reject independent switching. Here instead evaluate the **already established actor-heterogeneous Markov models** with OUT-OF-SESSION estimation, combining their six individual predicted switching probabilities by independent Poisson-binomial convolution. The intent is not to select a new best learner from the reused source but to ask whether the already documented actor predictors capture the same early/late n4 welfare adaptation.

## Input, folds, and estimand
Original author-approved [source ZIP in Drive](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view); original extracted CSV SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. Filter treatments 1–3, sessions2/101 excluded, periods1–39; 24 sessions and 5,616 six-person group transitions. Sessions sorted by ID and assigned deterministic mod-six folds: 20 training sessions and 4 completely heldout sessions per fold. Actor switch logits/probabilities depend on route previously chosen, actual personally experienced Cost, treatment and informed status. Training uses alpha20-smoothed Bernoulli counts learned only from 20 sessions. During heldout predictions, actor identity histories (within section) are updated **only AFTER each time-t forecast**. The candidate variations are preexisting: baseline Markov, online within-section strength20 and 80 (not tuned here).

Per group, combine actor switch probabilities under conditional independence to forecast the joint U=B→A and D=A→B law. Extract four outcomes: P(U=D=0), P(U=D>0), E[U+D], E[3(n_t+U−D−4)^2]. Compare the 411 Full-information, current efficient n_t=4 group transitions, early t1–10 (154 groups) versus late t30–39 (257 groups). **Current n_t selection itself remains observational**; this is not an estimate of causal information effects.

## Original-data reproduced heldout results
| model | epoch | actual mean gross | forecast gross | observed next excess cost | forecast next excess cost | observed P0 | forecast P0 |
|---|---|---:|---:|---:|---:|---:|---:|
| actor Markov baseline | early | 1.35714 | .9113 | 3.01948 | **2.2552** | .22078 | .3648 |
| actor Markov baseline | late | .58366 | .9102 | 1.33074 | **2.2532** | .58366 | .3653 |
| online20 | early | 1.35714 | 1.0302 | 3.01948 | **2.4832** | .22078 | .3187 |
| online20 | late | .58366 | 1.1780 | 1.33074 | **2.7708** | .58366 | .2747 |
| online80 | early | 1.35714 | .9474 | 3.01948 | **2.3245** | .22078 | .3499 |
| online80 | late | .58366 | 1.0366 | 1.33074 | **2.4961** | .58366 | .3172 |

Early→late actual next cost falls **3.0195→1.3307**, yet baseline actor Markov stays about **2.255→2.253**, while within-section online actor learning 20 and 80 predicts a RISE in cost. Note that the homogeneous baseline P3-R11 had been *refit to actual gross in the very same epoch*, while these actor heterogeneous models forecast gross out-of-session and substantially underpredict early gross/overpredict late gross. This distinction is important: these experiments do NOT prove that allowing heterogeneity alone must worsen welfare.

## Exploratory 24-session paired cluster resampling
Exact source-equivalent local Ruby 3.3.8 reimplementation recorded group-by-session measured and predicted totals and drew **20,000 complete-session samples**, seed 20261105. The group histories and actor training split are held fixed; bootstrap reweights original sessions rather than re-fitting every CV fold, and thus is *conditional on the fitted predictors*. Source-equivalent local seed may not match the published refactored Ruby module's sequence of random draws, so the exact final GitHub SHA replay and bootstrap result hash are still HOLD.

Original observed−predicted mean next excess cost (exploratory percentile95):
- actor baseline EARLY **+0.7643 [+.2440,+1.4967]**, LATE **−0.9225 [−1.3121,−.4127]**;
- online20 EARLY **+.5363 [+.0129,+1.2632]**, LATE **−1.4401 [−1.8196,−.9786]**;
- online80 EARLY **+.6950 [+.1662,+1.4188]**, LATE **−1.1654 [−1.5337,−.6959]**.

Gross-switch forecast error observed−predicted:
- baseline early **+.4459 [+.2353,+.6728]**, late **−.3266 [−.4766,−.1310]**;
- online20 early **+.3269 [+.1382,+.5386]**, late **−.5943 [−.7147,−.4455]**;
- online80 early **+.4097 [+.2094,+.6279]**, late **−.4529 [−.5797,−.2820]**.

**Interpretation:** This is evidence of a stable *predictive calibration failure of these three selected models* on the same original experimental source. It is NOT confirmatory evidence for latent group dependence, individual psychological adjustment costs, or a change caused by the information policy. The model families, target and early/late grouping have been explored repeatedly; multiple-comparison and selection adjustments are absent. The important next contender is a strongly calibrated actor-specific **independent** choice process that can adapt to observed personal histories and opportunity sets. Only if it fails out of session and group residual correlations remain can a group strategic dependence hypothesis be considered.

## Execution and custody
- [Refactored GitHub Ruby P3-R12 CV](p3/actor_hetero_welfare_cv.rb), reuses previously committed [P2 actor model](p2/online_actor_history.rb) and [P3 exact joint law](p3/activity_event_cv.rb) without replacing them with new tuned coefficients.
- [Source-free synthetic Minitest](p3/test_actor_hetero_welfare_cv.rb).
- The original-data local independent Ruby replay parsed the sealed CSV, output all 411 conditioned groups, and verified current n+U−D=next n per group; 20k bootstrap was executed on original sessions. GitHub source-level tests are registered in the read-only CI workflow. **Exact merged GitHub checked-out source replay and remote GitHub Actions PASS remain unverified**.
- No private subject-level CSV or authorized original research PDF is published to GitHub.

## P3-R13 direction
Explain a mechanism that predicts, under admissible actual actor information: (a) whether any change happens, (b) U,D cancellation conditional on observed n and separate actor experiences, (c) early/late cost and group fluctuations, (d) marginal consequences of randomized decision timing or signal quality. First check calibration of each actor and independent Poisson-binomial probabilities; then check residual pair interactions and shared latent shocks. The generic statement that cognition/friction causes collective instability is existing prior art (Brock–Hommes, Yang et al., Jiang et al.). Novelty, if any, will be a **new sharp identification theorem or experimental causal prediction for finite-horizon aggregate welfare**.
