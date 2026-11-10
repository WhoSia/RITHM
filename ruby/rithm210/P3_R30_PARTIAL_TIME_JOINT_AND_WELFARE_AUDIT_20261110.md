# RITHM-2.10 P3-R30 — Information-Time Interactions, Joint Choice Correlation & Welfare Forecast Boundary

**2026-11-10 · Evidence:** historical original-author Partial treatment (trt=2), 24 manuscript-main sessions, original CSV exact SHA verified; 6-fold within-source exploratory predictions, **not external confirmation nor behavioral-friction causality**.

## 1. Question and unit

R29 established that in Partial 3 of 6 actors received prior public occupancy and all observed own realized payoff. R29's last-route+payoff+legally disclosed public occupancy logistic baseline improved legal individual route forecasts. R29 also showed informed-versus-uninformed route switching rates diverging descriptively across early versus late periods, but no causal difference-in-differences could be claimed because six-person congestion creates within-group interference, treatment sequence crosses over within the same humans, and early/late periods are dynamic.

R30 asks: **Does a prespecified late-period interaction improve out-of-session choice forecasting? Can a marginal-preserving correlated six-choice law improve joint route prediction without improving count or welfare forecasts?** This is exactly the micro→macro prediction question rather than another claim about an unobserved psychological laziness parameter.

## 2. Strict source filtration and statistical design

Original 24 paper-main sessions, 48 stable 6-actor Partial groups, 39 t=2..40 scored periods per group: **1,872 group-period forecasts / 11,232 actor choices**. Each group has exactly three permanently informed actors, three uninformed actors. For everyone inputs use only previous own route, previous **observed payoff**, and known period index t. Previous public occupancy is multiplied by the actual informed flag and is consequently **never exposed to uninformed actors**. Neither experimenter-visible previous true `Cost` nor hidden `Value` is introduced as a known cognitive signal. No period-t outcomes or future `switchWill` enter input features.

R29 baseline predictor is logistic with own route, informed flag, prior payoff and their interactions, plus public previous occupancy among informed actors. R30 temporal rival includes prespecified `late=1(t≥21)` interactions with those features; period t is known to the actor. All coefficients are estimated within each fold's 20 training sessions (L2 ridge=.02 fixed); 4 heldout sessions are not inspected for fitting. Original 24-session sixfold deterministic session assignment and equal-session final metric weighting retained. The training-only **common-shock** parameter is selected on **training session six-choice joint logloss** among `τ∈{0,.2,.4,.6}` per fold, then scored on the untouched four heldout sessions.

For actor A marginals `p_i` and their previous observed route `y_{i,t-1}`, build two equiprobable conditional product distributions with `p_i^{±}=p_i±τ(2y_{i,t-1}−1)min(p_i,1−p_i)`. This preserves each individual marginal **exactly**, while modifying the six-bit joint law and seven-count occupancy distribution. This is an R26-style predictive construction **not direct evidence of an observed real-world common shock or deliberate coordinated switching**. The `τ` symbol denotes latent correlation strength, not Marden–Shamma's log-linear temperature.

## 3. Source replay and full prediction comparison

| Full 24-session Partial heldout model | Actor logloss ↓ | Six-mask joint logloss ↓ | Seven-count logloss ↓ | Cost MAE ↓ |
|---|---:|---:|---:|---:|
| R29 baseline, independent | 0.563752746 | 3.382516478 | 1.417192590 | 2.967388130 |
| Baseline + selected common shock | 0.563752746 | 3.376854255 | 1.417439673 | 2.966580741 |
| Baseline + observed late-period interactions | 0.563141526 | 3.378849156 | 1.415706186 | **2.948600099** |
| Late-period interactions + selected common shock | 0.563141526 | **3.373260550** | 1.416027124 | 2.949209115 |

Every one of the six fold-specific train-only choices for both base and late-interaction families selected `τ=.2` from the prespecified four-value grid. On the baseline, latent shock changes joint logloss **−0.005662223**, count logloss **+0.000247083**, cost-MAE **−0.000807389**. On the late-interaction model, changes **−0.005588606**, **+0.000320938**, **+0.000609016**. Thus a joint-likelihood improvement need not improve the count distribution or welfare forecast. Actor logloss remains unchanged by construction. Temporal interactions vs fixed R29 independent baseline improved joint logloss **−0.003667322**, actor logloss **−0.000611220**, group-cost MAE **−0.018788031**.

Uncertainty: a **descriptive, 24-session resampling** 3,000-repetition interval for temporal-interactions joint-logloss delta was **[−0.008888,+0.001784]**, spans zero. For common-shock add-on, the same exploratory bootstrap intervals were [−0.011019,−0.000683] baseline and [−0.010994,−0.000566] late model; these are not new pre-registered confirmatory inference and data have been reused through R23–R29. No causal effect identified.

## 4. Exact population-count variance audit

For `N=Σ_iY_i`, `E[C(N)]=24+3[(E[N]-4)^2+Var(N)]`. With correlated actor choices `Var(N)=Σ p_i(1-p_i)+2Σ_{i<j}Cov(Y_i,Y_j)`. On R30 late-interaction model, mean expected group cost is **27.670503207** in the independent joint model and **27.673590638** after correlated shock (+0.003087431), despite improved joint log loss. The extra covariance contribution to count variance averages about **+0.001029144** and the conditional Bernoulli variance component remains identical. No actual realized observed social cost changed between forecasts; this is prediction accounting, not an implemented economic policy.

## 5. Adversarial checks and failures

- **Information leak negative control:** replacing the hidden `NumA` for uninformed actors does not change their design row in baseline or late models; informed design rows do change appropriately. Future period target `y_t` never enters design. These are exact source-free tests.
- **Probability normalization and conditional marginal:** the latent ± mixture is a normalized six-person count law and preserves conditional expected occupancy `Σp_i`; social cost identity independently checked.
- **Baseline replication:** R30 independent baseline actor score 0.563752746 reproduces R29's source replay on same 24 sessions (source SHA check).
- **Limitations:** selecting `late≥21` after seeing previous R29 descriptive results is not an independent hypothesis test; even though the cutoff was fixed before this new fit, R29 already showed period patterns. The 24 sessions are reused. Treat effects and session-bootstrap intervals as **exploratory**. Processing of group sequence/same people crossing treatments remains unresolved. Group-level common shocks are not identified psychological factors.
- **Reproducibility boundary:** Local source-free R29 12 tests + R30 6 tests = **18/18 PASS** and sealed private CSV evaluation completed. GitHub has a compact version of the evaluator; exact local source-byte identity and clean-checkout execution not yet independently verified. CI step registered, remote Actions PASS HOLD. Never equate registered workflow to a successful Actions run.

## 6. Durable paths and next unit

- [Published R30 Python evaluator](p3/r30_partial_dynamic_joint.py)
- [Published R30 invariance unit tests](p3/test_r30_partial_dynamic_joint.py)
- [Public aggregate source-replay numbers](P3_R30_PARTIAL_TIME_AND_JOINT_CV_20261110.json)
- [R29 historical source and information-permission baseline](P3_R29_PARTIAL_INFORMATION_LAWFUL_FEEDBACK_AND_SWITCHING_20261110.md)
- [Canonical experimental manuscript §4.1](https://drive.google.com/file/d/1rTL9qTpYV6zwee6pC3nZy64H07oSWzlK/view)

**R31 candidates:** (i) Within-subject segment order and prior treatment experiences to challenge alleged late-period information effect; (ii) cross-arm No/Partial/Full session-heldout legal signal models using informed flag and previous received payoff, while keeping hidden counts sealed; (iii) compare correlation law vs real group count loss and session-level proper scoring; (iv) cognitive research-level inference only after explicit costs and repeated-experiment controls; (v) test posted GitHub exact bytes in clean environment and instrument CI run evidence.

**Scientific judgment:** the strongest supported result is limited but meaningful: conditional on a lawful prior-information model, modest six-person joint-choice dependence is predictive and the late-in-treatment score adds a small amount, but these improvements do not establish welfare gains, actual group coordination, experienced cognitive friction, or novel revision dynamics.
