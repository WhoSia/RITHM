# RITHM-2.10 P3-R16E/F — Exact Qi A/B/C Structural Ablations and Teacher-Forcing-Free 40-Round Welfare

Date: 2026-11-05 KST. **Original-source exploratory study; independent external replication, causal mechanisms and manuscript novelty HOLD.**

## I. Input custody and precise rival hypotheses

Original author-approved [Noussair–Qiao source ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view); derived original CSV SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb` checked before execution. Exactly 24 valid sessions, 5,616 group transitions overall. **Only Full-information treatment 3 is eligible** for direct observed cost-pair-based Qi theory: 1,872 group transitions / 11,232 six-person choices; 48 complete group trajectories with 40 occupations (periods 1–39 current n plus period 39 next n). This retains original group/section/session identity and checks continuity. Fold assignment is ordered-session modulo 6; 20 sessions train / 4 sessions held out per fold. All model selection and hyperparameter questions reflect repeated exploratory access to this same historical source.

Primary theory: [Qi et al. Part I](https://drive.google.com/file/d/1r2M3lM2DHKD1MvPE_5iWg489fVzwdZVk/view), §5.1 three explicit hypotheses:
- **A**, route-specific inertial reconsideration `P_i=1-eta_i`, route-preference-adjusted costs `C_i=(1-eta_i)c_i`, 3 fitted coefficients `etaA,etaB,theta`.
- **B**, common inertia `P_i=1-eta`, *unmodified route costs* `C_i=c_i`, 2 fitted coefficients `eta,theta`.
- **C**, route-specific inertia `P_i=1-eta_i`, *unmodified route costs* `C_i=c_i`, 3 coefficients `etaA,etaB,theta`.
All use `p(switch i->other)=P_i * exp(-theta*C_other)/sum_j exp(-theta*C_j)` and independent individual Bernoulli aggregation, consistent with [Qi et al. Part II](https://drive.google.com/file/d/1sC_O0U_T90IdUeHXA400sgQJn1mAl4ar/view). For this distinct experiment `cA=n`, `cB=2(6-n)`; this is **a functional-form transfer with freshly fitted parameters, NOT a reproduction of Qi's original 312-participant 8-scenario experiment**.

Structural nesting: B is exactly nested in C via etaA=etaB. When A has etaA=etaB=eta, it equals B after replacing thetaB=thetaA(1−eta). A generally departs from C because A rescales each route's costs, shifting the logit's indifference occupancy threshold away from n=4. These mathematical equivalences are implementation tests, not new theorems.

## II. R16E — Full-information 1-step event scoring (observed state supplied each period)

Sixfold out-of-session probabilities, 1,872 group transitions. Independent Python SciPy L-BFGS-B fits with multi-start numerical optimization; Ruby uses deterministic bounded multi-start coordinate search. The measured Python coefficients were stable within folds:
- A etaA roughly 0.607–0.630, etaB 0.433–0.468, theta 0.406–0.464.
- B eta 0.558–0.585, theta 0.231–0.250.
- C etaA 0.656–0.677, etaB 0.372–0.410, theta 0.208–0.226.
These are calibrated parameters in the *new* experiment and have no causal/psychological identification by themselves.

| Full-information U,D joint mean logloss ↓ | All 1,872 groups | Early 480 | Late 480 |
|---|---:|---:|---:|
| Qi A | 1.948435 | 2.164320 | 1.796694 |
| Qi B | 2.035737 | 2.284395 | 1.874553 |
| Qi C | 1.948884 | 2.166421 | 1.795346 |
| Train-only epoch20 independent | **1.871607** | **2.103428** | **1.633371** |

Same-source paired whole-session (24 units, 20,000 draws, deterministic seed) **exploratory** comparisons of fixed fold-specific one-step forecasts:
- A−C = **−0.000450**, percentile 95% approximately **[−0.00399, +0.00355]**.
- B−C = **+0.086852**, 95% approximately **[+0.07160, +0.10102]**.
- B−A = **+0.087302**, 95% approximately **[+0.07111, +0.10201]**.
The C vs A difference cannot be distinguished from zero at this sample/methodological resolution. B's larger loss is descriptive evidence that route-specific inertia improves this particular model class, but does not identify individual psychological reasons. Note Qi Part I itself reports nearly indistinguishable A/C performance in two-route cases; we are **not first to discover that**.

## III. R16F — 40-round autonomous forecast; no repeated observed occupancy injection

For each of 48 complete Full-treatment group paths, hold the group-specific initial occupancy `n1` fixed and generate a distribution over `n2,...,n40` with **39 recursive 7-state Markov transitions**, derived exactly by convolving the independent n A->B and (6−n) B->A switches, where transition probabilities are recomputed from the **model-generated n**. For Qi A/B/C, every row kernel is time homogeneous. For actor Markov and train-only epoch20, calculate route-specific probabilities from trained actor-key counts using only group state n, information=Full, actual cost function cA(n)=n/cB(n)=2(6−n); epoch20 additionally uses the publicly known current period (early/middle/late), not actual subsequent n. Never update a future transition with observed human states, costs or y. Compute exact distributional expectation over every one of 40 rounds for `C(n)=n²+2(6−n)²`, rather than inserting observational one-step forecast costs into a purported counterfactual.

For the actual path target, use original observed n for periods 1..39 and n40 from final source `NumAnext`, enforce `NumAnext(t)=NumA(t+1)`; 48 complete 40-period paths. Each source group includes between one and three full trajectories per original session; **session is the resampling cluster**, not the 48 paths.

| Model | Mean predicted 40-period total cost | Observed mean total | Mean abs error ↓ | Mean squared error ↓ | Terminal n40 logloss ↓ |
|---|---:|---:|---:|---:|---:|
| Qi A | 1086.6845 | 1078.6875 | 36.4762 | 2017.5884 | 1.27460 |
| Qi B | 1120.0556 | 1078.6875 | 50.3705 | 3674.2860 | 1.40381 |
| Qi C | 1086.6123 | 1078.6875 | 36.4456 | 2017.1801 | 1.27418 |
| Actor Markov | 1084.5354 | 1078.6875 | **36.0455** | **1982.0330** | 1.26092 |
| Epoch20 independent | 1084.9109 | 1078.6875 | 36.2070 | 1992.7462 | **1.23037** |

Caution: low average error can mask opposing group errors, hence MAE and squared errors. The metric *terminal* n40 is one snapshot and does not measure the full joint 40-step trajectory likelihood. The two-step outcome hierarchy is deliberately distinguished: (i) forced observed-state individual switch and joint U,D score, versus (ii) from-initial group forward 40-round distributional welfare / terminal score. Both on repeatedly analyzed same experimental data.

Paired **24 complete-session block** bootstrap, 20,000 draws on the 48 path-level outcomes, fixed fitted models, exploratory percentile95:
- 40-round MAE epoch20−Markov = **+0.16148**, 95% **[−0.01102,+0.33351]**.
- 40-round MAE epoch20−Qi A = **−0.26926**, 95% **[−0.73088,+0.21530]**.
- 40-round MAE Qi C−Qi A = **−0.03066**, 95% **[−0.08762,+0.02440]**.
- 40-round MAE Qi B−Qi C = **+13.92493**, 95% **[+5.81643,+21.11598]**.
- Terminal n40 logloss epoch20−Markov = **−0.03055**, 95% **[−0.06841,+0.01068]**; includes zero.
- Terminal n40 logloss Qi B−Qi C = **+0.12964**, exploratory95 **[+0.00265,+0.24271]**.

**The central negative result:** the large one-step advantage of epoch20 versus Qi A/C does NOT translate into a comparably large or robust 40-period MAE advantage; actor Markov is marginally ahead on observed absolute total welfare error, while epoch20 is ahead on final-state logloss. Strongest evidence within this comparison is loss of route-specific structure in Qi B; no positive identification of an independent mechanism or a causal intervention.

## IV. Code provenance, limits, next gates

Committed as discrete human-authored GitHub units:
- [Qi A/B/C likelihood and transfer](p3/qi_abc_transfer.rb); [unit tests](p3/test_qi_abc_transfer.rb).
- [Paired A/B/C source contrast](p3/qi_abc_session_contrast.rb); [unit tests](p3/test_qi_abc_session_contrast.rb).
- [Unconditional 40-period 7-state chain](p3/qi_abc_forward_trajectory.rb); [unit tests](p3/test_qi_abc_forward_trajectory.rb).
- [Forward path cluster bootstrap](p3/qi_abc_forward_bootstrap.rb); [synthetic tests](p3/test_qi_abc_forward_bootstrap.rb).
- All registered in read-only GitHub CI; **remote Actions PASS and byte-identical GitHub HEAD Ruby integrated original-CSV replay still HOLD**. Local source-equivalent A/B/C test ran 3 runs / 38 assertions / zero failures, and original A test 5 / 14; all published numerical A/B/C transfer, 40-step outcomes and bootstrap contrasts independently calculated in local Python/SciPy with original CSV SHA verified. Actual full emitted GitHub Ruby driver source and its 24-session bootstrap numerical parity not yet independently checked on a final checked-out HEAD.

No raw participant rows or derived per-group predictions published. Private original CSV and per-group predictions remain local/Drive only. No new raw public PDF copies or GitHub bot-authored commits.

**Research-manager verdict:** R16E/F meaningful competitive stress test and negative-generalization result, but **not yet a stand-alone publishable novel causal discovery**. R17 must derive a discriminating experiment involving exogenously randomized information delivery and adjustment clocks, separating personal learning from common group signals and direct strategic dependence. Before concluding, compare actual original author SSM and EWA policies, and challenge the 40-step models with exogenous sessions. Strict prospective frozen model choice (not endless same-data tuning) is the primary verification gate.
