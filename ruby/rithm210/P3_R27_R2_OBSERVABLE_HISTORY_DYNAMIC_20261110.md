# RITHM-2.10 P3-R27-R2 — Observable-History Feedback, Exact 40-Period Welfare & Stronger Independent Rivals

**Research date 2026-11-10 · original-author SHA checked / exploratory real-source forecasts + exact source-free synthetic dynamic test.**

## Origin, prior work, and epistemic status

R23 memory/inertia forecast occupancy better than own-frequency but not necessarily one-period cost; R24 showed pair residuals can be produced by misspecified independent actor probabilities; R25 corrected individual propensity using train-only calibration; R26 showed exploratory occupancy-only gains from a marginal-preserving shared group shock with ambiguous joint and welfare improvements; R27-R1 supplied exact six-actor occupancy-fiber counterexample and a toy labelled-memory 2-period welfare transition. R27-R2 resumes the original RITHM question: how repeated reactions to past information, persistence, and shocks alter stability and long-run congestion.

**Evidence classes:** (A) controlled synthetic mathematical model, exact 448-state probability propagation over 40 future rounds; (B) 24 original historical sessions with train-selected source forecasts for 1,824 *trt=3 only* six-person group-period observations (periods 3–40). Data were repeatedly used to develop models; even session-level bootstrap intervals are exploration, not confirmatory independent evidence. The original author manuscript (2026-07-24, section 4.1) explicitly states Full-treatment drivers received previous-period numbers on each route after each round. Thus the last occupancy is information-admissible for trt=3; an earlier lag was available historically but participants' actual recall/use and latent cognitive state remain unobserved.

## Mathematical state and transition

Full decision state `X_t=(Y_(t-1),N_(t-2))`: previous **labelled** six binary choices and second-lagged occupancy (64×7=448 states). Define per-route congestion costs `c_A(n)=n`, `c_B(n)=2(6-n)`, total cost `C(n)=24+3(n-4)^2`. Define lagged cost signal `D(n)=12−3n`; individual logit `logit(p_i)=beta*((1-w)*D(N_(t-1))+w*D(N_(t-2))) + kappa*(2Y_(i,t-1)−1)+bias` (`beta>=0, kappa>=0, 0<=w<=1`). `w` is an explicit finite-observation memory weight, **not identified individual cognition**.

`tau=0`: conditionally independent Bernoulli actors. `tau>0`: draw fair Z=±1 and use `p_i(Z)=p_i+Z*tau*(2Y_(i,t-1)−1)*min(p_i,1−p_i)`; each conditional actor marginal after mixing Z is EXACTLY `p_i`. The signed shock changes the conditional six-actor joint law and thus its endogenous successor-state distribution, but is not identified strategic coordination.

State transition `K((mask_new,popcount(mask_old))|(mask_old,older_occupancy))=P(Y_t=mask_new|X_t)`; all other transitions have zero mass. Fair prior over previous labelled masks, older occupancy initialized to previous occupancy; same prior across parameters. 40-step exact propagation, no sampling variance.

## Synthetic findings (parameters NOT fitted)

| beta | kappa | w | tau | 40-period mean C | mean absolute period-to-period change in N |
|---:|---:|---:|---:|---:|---:|
| .05 | 0 | 0 | 0 | 30.6784 | 1.5422 |
| .05 | 1 | 0 | 0 | 29.6119 | 1.0369 |
| .15 | 0 | 0 | 0 | 31.5839 | 2.1471 |
| .15 | 1 | 0 | 0 | 28.4317 | 1.2650 |
| .30 | 0 | 0 | 0 | 39.8951 | 3.9452 |
| .30 | 1 | 0 | 0 | 30.2166 | 2.0093 |
| .30 | 1 | .5 | 0 | 29.1582 | 1.4370 |
| .30 | 1 | .5 | .6 | 30.7614 | 1.5525 |
| .60 | 0 | 0 | 0 | 51.7291 | 5.6918 |
| .60 | 1 | 0 | 0 | 48.1407 | 5.2549 |
| .60 | 1 | .5 | 0 | 34.6529 | 2.4629 |
| .60 | 1 | .5 | .6 | 36.8130 | 2.6505 |

The tradeoff is parameter-dependent. In this synthetic family strong reaction can create repeated group-level over-correction, and persistence/older-signal weighting can reduce it; shared shock can increase expected costs despite each actor's same conditionally forecast probability. These are *not* universal normative policy claims.

**Exact analytical caution:** in the homogeneous inertia-free one-lag no-shock mean-field surrogate, expected count evolves `F(n)=6 sigmoid(beta*(12−3n))`. At beta=.30 its fixed point is `n*=3.571461116976...` and `F'(n*)=-1.301014828767...`. The social instantaneous cost minimizer n=4 is **NOT** the fixed point. A numerical mean-field flip boundary occurs near beta=0.2286972582. The full stochastic finite-state process is not literally unstable at this number; for finite parameters and tau<1, the transition is an irreducible aperiodic Markov chain, and model metrics track cost/turnover rather than divergent dynamics.

## Original-source benchmark: full information only

SHA `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb` verified on authorised original participant CSV. For trt=3, actor identity and group size were checked for all 40 rounds. Score t=3..40 only, because two **past** counts are required; 24 sessions, 1,824 complete group-period rows. Each model selected 20 training sessions/4 heldout using six folds, fixed 4×2×2×3 grid of beta/inertia/w/tau, selection minimizing **joint** six-actor logloss on the 20 training sessions alone. Treatment labels and participant rows are not published. Same sessions/heldout fold for rival classes.

| Heldout per group | independently chosen tau=0 | selected tau>0 | latent − independent | exploratory whole-session bootstrap 95% |
|---|---:|---:|---:|---|
| six-actor joint logloss | 3.294913 | 3.272754 | **−0.022159** | [−0.038726, −0.007053] |
| seven-count occupancy logloss | 1.523374 | 1.512265 | **−0.011109** | [−0.017617, −0.005030] |
| one-period cost MAE | 3.800500 | 3.925985 | **+0.125485** | [+0.096735, +0.154664] |

**Interpretation:** a narrowly-defined model-selection competition in historically reused data. Better joint and occupancy logloss of this selected latent family accompanies worse cost MAE. This is not a clean direct comparison with R26 (different baseline, features, time coverage and parameter families), not an independent result, not evidence of actual strategy or recovered cognition. **Original primary-source audit:** Noussair & Qiao, *Congestion Information and Efficiency: An Experiment*, author WP dated 2026-07-24, §4.1, reports Full-treatment players all observed previous-period numbers choosing each route (at the end of each round); source in canonical Drive: https://drive.google.com/file/d/1rTL9qTpYV6zwee6pC3nZy64H07oSWzlK/view . The second lag had once been displayed but individual recollection or processing is unobserved.

## Verification and authority

- Local synthetic kernel: 448 past states×6 marginals checked, conditional mixtures normalize, tau=0 independence nested, cost identity, mean-field fixed point, and input exceptions. Local 7 tests PASS. Three additional training/heldout boundary synthetic tests PASS. Local original CSV SHA validated, actor/group-period alignment, 6-fold original-source descriptive CV executed. **Remote GitHub CI PASS, precise GitHub checked-out source replay and full original R26 nested source-model replay remain HOLD.**
- Public GitHub source: [kernel](ruby/rithm210/p3/r27_r2_observable_lag_dynamics.py), [source benchmark](ruby/rithm210/p3/r27_r2_source_cv.py), [source-free tests](ruby/rithm210/p3/test_r27_r2_observable_lag_dynamics.py), [train-only guard](ruby/rithm210/p3/test_r27_r2_source_cv.py), [aggregate-only JSON](ruby/rithm210/P3_R27_R2_OBSERVABLE_DYNAMIC_AGGREGATES_20261110.json). No raw human rows committed.
- Durable byte custody: [Google Drive original research report](https://drive.google.com/file/d/1J9K6nFzQzO9FWFl3iwIe6ekC9HhRshfr/view) and [source-free local reproducibility ZIP](https://drive.google.com/file/d/1PjQQvggdnl5yJWeEUcHO-Vx7tVK7RZ5N/view). Local ZIP prototype has earlier filename r28_* but represents the R27-R2 model; repository implementation is a separate published version and must not be called byte-identical without independent checkout verification.

## RAVEL / next decisive work

**Explanandum:** adaptive individual reaction to history -> collective feedback -> persistence, oscillation and finite-horizon welfare. **Stage type:** synthetic exact study and source-based exploratory benchmark, not Court. **Rivals:** inertia-only independent, public-lag independent, signed group shock, and private experienced-cost learning. **Attacks:** participant observability boundary, repeated-source exploration, collective-state dependence vs one-step score, mean-field vs finite stochastic stability, synthetic welfare vs causal human effects. **Decision change:** retain the newly verified Full-treatment information filtration and compare lag-count features against private experienced-cost learning and individual-history rivals, estimate and test the transition on heldout sessions, and study exact dynamic stationary/oscillatory metrics under parameter uncertainty. No new participants. Avoid endless identification-only branches; return to RITHM origin and dynamic policy question.
