# RITHM-2.10 P3-R28 — Anchored Human-Source Cohort Replication, Identifiability Obstruction and Prior-Theorem Audit

**2026-11-10 · CORE RESEARCH GATE: source-replay numerical PASS (local equivalent evaluator); human cognitive-friction identification HOLD; independently verified GitHub clean checkout/remote Actions PASS HOLD.**

## 1. Research origin and source authority

The RITHM question concerns whether individual adjustment effort, inertia and information update influence repeated route decisions and aggregate economic cost. This audit directly follows the midterm P1 discovery that published-paper restricted **24 sessions**, optional **25 sessions** including 101 but excluding pilot 2, and literal-author-R-filter **26 sessions** are different source populations. Treat the author manuscript's section 4 (24 experimental sessions), the R preparation script's prose (sessions 1 and 2 pilot), and the literal script predicate (excludes 1 but leaves 2, includes 101 in trt 3) as distinct sources. Do not collapse them or pretend the author's apparent predicate discrepancy was resolved.

Private author source: `data_task_all_switch_230705.csv`, SHA-256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. Treatment 3 Full: previous-period route-A and route-B counts were disclosed to all participants; older disclosed count was once available but recall/use is not observed. No participant row or ZIP source file was committed.

## 2. Anchored sixfold: same assignment for all common sessions

Retained the previously published 24-session sixfold assignment exactly (4 heldout sessions per fold). For the larger populations, assign session 101 to fold 0 and session 2 to fold 1, **without changing any common session's fold**. Repeat the same 48 pre-enumerated prior-only candidates, with separate independent tau=0 and latent tau>0 train-only joint-logloss selection per outer fold. Each session receives equal final weight irrespective of its 2/3 groups. For 25/26 cohorts, training sizes change to 20–21/21–22, hence this is same fold assignment and model-selection logic, **not an equal training-set size experiment**.

| Cohort and meaning | Sessions | 6-actor groups | t=3..40 group-period predictions | Independent six-mask joint logloss | Latent six-mask joint logloss | Latent−independent joint loss | Latent−independent occupancy loss | Latent−independent cost MAE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Published-paper-restricted 24 | 24 | 48 | 1824 | 3.294912942 | 3.272754373 | −0.022158569 | −0.011109460 | **+0.125484603** |
| Pilot-2 excluded +101 included 25 | 25 | 51 | 1938 | 3.301185994 | 3.280837051 | −0.020348943 | −0.010944350 | **+0.128965182** |
| Literal R source-predicate 26 | 26 | 53 | 2014 | 3.299834874 | 3.280153477 | −0.019681398 | −0.011010499 | **+0.130132951** |

The original restricted 24 sixfold result matches previously archived R27-R2 numbers within floating-point precision. In **all** sixfold cohorts, joint/occupancy log scores improve slightly but cost-MAE gets worse. The model selected for EVERY common 24-session heldout fold is unchanged when adding session 101 and/or pilot 2; thus the *common* session heldout contrast is exactly the old −0.022158569 in all three cohorts. This is a concrete train-selected model stability result for THIS grid, not universal behavior. Additional sessions alter the weighted summary:

- Session **101** alone: latent-minus-independent joint logloss **+0.023082103**, occupancy logloss −0.006981695, cost MAE +0.212499062. Its joint score is **worse**, not better.
- Session **2** alone: joint logloss −0.002992775, occupancy logloss −0.012664231, cost MAE +0.159327182.

The separately conducted 25-session 5fold study had a different joint delta (−0.030479419), which cannot be causally ascribed to including session 101 because fold assignments and training-selection outcomes change simultaneously. No new external validation or treatment inference; all three are reused original-source exploratory comparisons. Heldout session means are independent *under assumed sessions-as-clusters* for summarizing uncertainty but reuse of data across historical studies prohibits treating them as independent confirmatory evidence.

Source code: [anchored evaluator](p3/r28_anchored_source_cv.py) · [source-free fold/selection tests](p3/test_r28_anchored_source_cv.py) · [explicit 24/25/26 cohort census](p3/r27_audit_population_contracts.py) · [sealed aggregate results](P3_R28_ANCHORED_POPULATION_AND_COST_IDENTIFICATION_20261110.json).

## 3. New structural identification result: own experienced cost is already a function of full-information signals

For six actors, own realized congestion cost at time t, given own route `y_t=1` for A and group A occupancy `n_t`, is

```text
c_i,t = y_i,t * n_t + (1-y_i,t)*2*(6-n_t)
      = 12 - 12*y_i,t - 2*n_t + 3*(y_i,t*n_t).
```

Direct inspection of the author-source CSV gave `trt 1=12000`, `trt 2=12720`, `trt 3=12720`, `trt 4=12720` actor-period rows and **zero cost-identity violations in all treatments**. Specifically in the restricted 24-session Full cohort, **11,520 actor-period rows** obey the identity with zero arithmetic error. In the 5-column feature matrix with columns `(1, y_(t-1), n_(t-1), y_(t-1)*n_(t-1), c_(t-1))`, the exact null vector is

```text
(-12, 12, 2, -3, 1).
```

Consequently this matrix cannot have column rank 5; empirical restricted Full singular values were approximately `[742.44,217.38,109.03,25.72,2.46e-13]`, so **rank = 4 at numerical tolerance**. This does **not** mean human experienced cost has no behavioral effect. It means that in Full-information subjects, including a fully interacted previous `y,n` basis and own previous realized cost makes separate linear coefficients **exactly non-identifiable**. An observational model can estimate their *combined predictive function* but cannot isolate independent psychological effects of cost versus disclosed crowding without additional assumptions/interventions.

Formally, replacing coefficients as `beta_c'=beta_c+delta`, `beta_0'=beta_0-12delta`, `beta_y'=beta_y+12delta`, `beta_n'=beta_n+2delta`, `beta_yn'=beta_yn-3delta` leaves every linear predictor exactly unchanged. This is a theorem about the given cost schedule and covariates, not a newly discovered empirical parameter.

**Impact:** the proposed 'private experienced-cost versus public previous occupancy' *separate causal influence test within Full* is not identified by a flexible past-route-and-crowding model. A safer next test is cross-treatment information observability with explicit utility/payoff disclosure checks, or a narrowly constrained rival model identified by additional exclusion restrictions, with honest assumptions. Because No/Partial arms have different information filtrations, no identical private/public information model can be imposed on all treatment subjects without checking disclosure and group treatment coding.

Source-free exact enumerator and private SHA-checked validator: [identification module](p3/r28_fullinfo_cost_identification.py) · [null-vector tests](p3/test_r28_fullinfo_cost_identification.py).

## 4. Primary-literature theorem-level audit (Drive full text, not merely title)

**Marden & Shamma (2012)**, [canonical source](https://drive.google.com/file/d/1fQGV-IiA8fKfM89GeC01lZlCysx2IiCN/view), §4.2 Theorem 4.1: for finite weakly acyclic games under best replies with strict Nash equilibria and a **regular** revision process (positive probability that each singleton actor alone revises), the stochastically stable states for their synchronous log-linear revision scheme lie in the Nash equilibrium set. §4.3 Theorem 4.2: in finite potential games under an independent revision process, **specifically with revision probability tied to log-linear noise** `omega=(exp(-1/tau))^m` for sufficiently large m as noise tau→0, stochastic stability selects potential maximizers. Their tau is **log-linear temperature/noise**, NOT our R26 latent common-shock tau; never equate symbols.

Their theorem is NOT directly a result on finite-H=40 expected social congestion under constant `beta=.6`, arbitrary state-dependent `rho sigmoid(lambda*g)`, or positive latent correlation. It establishes serious prior-art: asynchronous/independent revision schemes and potential optimization are known; RITHM cannot claim novelty simply for proposing them.

**Sandholm (2010)**, [canonical book](https://drive.google.com/file/d/1ahyWT5wdJnYYE3qH8YmBqQg9IoKZC1cO/view), Ch.4 *Revision Protocols and Evolutionary Dynamics* treats individual revision opportunities and their aggregate population dynamics; Parts III–IV cover convergence, nonconvergence and stochastic stability. RITHM's individual revision opportunity is a known standard formalism, not a new concept. Book topical/section crossread conducted; entire monograph line-by-line audit not claimed.

**Caplin & Spulber (1987)**, [canonical NBER WP2311](https://drive.google.com/file/d/1rU4bP29fm82DBTkTcoFv6PnYTcZOINyw/view), models imperfectly synchronized endogenous price adjustment and shows possible aggregate neutrality despite micro stickiness in its monetary setting. It is NOT a traffic model and cannot confer a transport-welfare conclusion. This is a methodological donor and novelty boundary.

In RITHM's specific six-person toy congestion game, Rosenthal's cost potential
`Phi(n)=n(n+1)/2+(6-n)(7-n)`
is minimized at n=4 with Phi=16, **and** social congestion C(n) is minimized at n=4 with C=24. These minimizers happen to coincide in this instance; they need not coincide in general congestion games. Do not falsely infer RITHM's n=4 is always socially suboptimal Nash.

## 5. Operational and epistemic status

**PASS, source scope:** original exact CSV byte hash; 24/25/26 correct treatment 3 event group sizes, 24 sixfold independent reproduction, exact cost identity on actual actor rows, source-level Marden theorem quotations, prior-only structure of published code. Local source implementation of anchored 6fold executed in ~5 seconds with all three cohorts and sealed local aggregate output. Source-free tests for R28 published; remote GitHub Actions PASS and clean-checkout exact source parity NOT yet verified.

**HOLD:** human cognitive friction estimate, difference between own-cost and public-occupancy use within Full without added assumptions, experiment-wide causal treatment effect, whole-Ruby temporal leakage scan, out-of-sample replication on a new independent study, theorem of global stationary welfare, newly unique asynchrony result. Full cohort's past receipt of n is source-attested; whether users truly remembered or cognitively used n_(t-2) cannot be observed.

**NEXT:** study actual information/feedback across treatment arms; distinguish public-information redundancy from learned private information; fit train-only observational hazards conditional on legal past inputs; compare full information with no/partial treatment without claiming randomization beyond available experiment protocol; include resource cost of prescreening and rights-aware revision scheduling. Freeze all source SHA and repository code versions before treating test receipts as a clean proof of reproducibility.


## 6. Protocol correction and actual payoff-feedback benchmark (same date)

**The crucial new information-filtration correction is stronger than the algebraic collinearity result.** In the original-author manuscript §4.1 (revised July 24, 2026), **No** subjects are told their **stage-game payoff only**, not an explicit realized route cost. Their per-period randomly drawn travel value is unknown when choosing. Under **Partial**, 3/6 drivers receive both payoff and previous-route counts, while 3/6 receive payoff only; the fixed informed identities remain stable through 40 periods. Under **Full**, all six get payoff and previous-route counts. All three part-1 conditions are **within subject**, counterbalanced across segments; treatment 4 Endogenous is distinct and not pooled with 1/3 in this benchmark. Thus for no-information agents the experimenter CSV's `Cost` and `NumA` should NOT be entered as known choice predictors. Prior `profit` (the actual payoff shown) is admissible. The random travel `Value` need not be a known decision input.

A source-first minimal competitor was executed locally with SHA-verified original actor histories, **24 paper-main sessions**, separate No (trt1) and Full (trt3), both with 48 groups × 39 forecast rounds = **1,872 group-periods / 11,232 actor decisions per treatment**. All six outer folds have 20 train / 4 heldout sessions. Train-only regularized logistic estimation with pre-fixed L2 `lambda=.02`; session-equal-weight aggregate. For each six-person group, individual model forecasts were convolved into occupancy/cost distribution **assuming independence**, not a finding that people are independent.

| Prior-history candidate | No actor choice logloss | Full actor choice logloss | No occupancy logloss | Full occupancy logloss |
|---|---:|---:|---:|---:|
| Last own route alone | 0.567901442 | 0.539248966 | 1.448623884 | 1.463820908 |
| Last route + last observed payoff + interaction | **0.557733646** | 0.532315230 | **1.431844807** | 1.441974640 |
| Last route + *public previous occupancy* + interaction | **NOT admissible in No** | 0.531350489 | **NOT admissible in No** | 1.427638330 |
| Last route + previous occupancy + previous payoff | **NOT admissible in No** | **0.527677539** | **NOT admissible in No** | **1.418987098** |

Cost MAE: No last-route **3.069552062** → payoff-enhanced **2.923497391**; Full last-route **3.143417193** → full legal public-count-and-payoff **2.852162979**. These are historical within-treatment predictive associations, **NOT** causal evidence of people consciously using payoff or an induced cognitive cost; random unobserved value draws and within-subject order and group effects remain competing explanations. This baseline is also NOT model-selection-adjusted significance testing; no claims of hypothesis confirmation.

[Run script](p3/r28_payoff_filtration_cv.py) · [source-free information noninterference tests](p3/test_r28_payoff_filtration_cv.py) · [aggregate No/Full JSON](P3_R28_PROTOCOL_ADMISSIBLE_PAYOFF_CV_20261110.json). The source-free tests explicitly check that changing **hidden previous NumA** leaves the No design matrix unchanged, while the Full design can use it; they check optimizer behavior and a known Poisson-binomial case. Scipy is a new test dependency, now registered in CI. Remote GitHub clean-checkout execution and CI PASS remain HOLD; local equivalent script executed successfully on the sealed private CSV.

**Revised NEXT:** do not compare 'private experienced actual Cost' vs Full public count inside the same flexible model, and **do not assume No participants knew exact realized Cost**. Proceed with *payoff-history learning* under No and Full and explicitly group-informational Partial. Then test whether residual adaptivity/instability in the recorded decisions persists after lawful individual payoff and public count filters, with within-subject treatment order and session-level inference and R23–R26 rival forecasts. The founding behavioral-friction welfare question survives, but the empirical information filtration must be respected.
