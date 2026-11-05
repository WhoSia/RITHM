# RITHM-2.10 P3-R16D — Qi Model A Equation Transfer and Paired Full-Information Test

2026-11-05 KST. Source-verified transfer to another experiment; not an independent replication of Qi paper's original dataset.

## Primary original-source derivation and rival novelty

Qi et al. (2023), *Investigating Day-to-Day Route Choices Based on Multi-Scenario Laboratory Experiments, Part I: Route-Dependent Attraction and Its Modeling*, arXiv 2303.04088v1, [canonical original PDF](https://drive.google.com/file/d/1r2M3lM2DHKD1MvPE_5iWg489fVzwdZVk/view) §4.2 Eq. (3)–(6), §5.1 Model A: the probability that a current-route-i user changes to j != i equals
`p_{i->j}=P_i exp(-theta C_j) / sum_k exp(-theta C_k)`.
The two behavioral parameters are not arbitrary separate coefficients in *Model A*; rather `P_i=1-eta_i`, `C_i=(1-eta_i)c_i`. Stayers include reconsidering the same route. Qi et al. (2024), *Part II: Route-Dependent Attraction-Based Stochastic Process Model*, [canonical PDF](https://drive.google.com/file/d/1sC_O0U_T90IdUeHXA400sgQJn1mAl4ar/view), Eq. (3)–(4) aggregates conditional independent individual choices as binomial switches and finite-state stochastic flows. The preceding P3-R16C route-gap logistic is a cost-responsive negative control, **not this exact model**.

For the two-route six-person Noussair–Qiao game with full contemporaneous cost information, `c_A(n)=n` and `c_B(n)=2(6-n)`, the **literal Qi Part I Model A specialization** is
`p(A->B|n)=(1-eta_A)*sigmoid(theta*((1-eta_A)*n-(1-eta_B)*2*(6-n)))`;
`p(B->A|n)=(1-eta_B)*sigmoid(theta*((1-eta_B)*2*(6-n)-(1-eta_A)*n))`.
This is the exact Model A functional form but **estimated afresh on a different research experiment, not Qi paper's own fitted parameters or its original data/reproduction**. Restrict to Full-information treatment 3; alternative route cost is not available to uninformed players in other treatments.

## Real-data identification and evaluation
Original author-approved [experimental source ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view), CSV SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb` checked before execution. All 24 original sessions, Full treatment3: **1,872 group transitions / 11,232 individual Bernoulli switch observations**, 6 folds of 20 training and 4 heldout sessions sorted modulo6. Train-only 3-parameter likelihood fit for eta_A∈(0,1), eta_B∈(0,1), theta>0 using a deterministic bounded multi-start coordinate optimization. Each fold's maximum-likelihood candidates were cross-checked to SciPy L-BFGS-B up to reported precision; fitted parameters stable: eta_A approx 0.607–0.630, eta_B 0.433–0.468, theta 0.406–0.464. Scores are **one-step observed-state** independent Bernoulli U,D Poisson-binomial logloss and expected quadratic next congestion cost, not an unconstrained generative 40-period path.

| Full-information period | Groups | Markov joint LL | Epoch20 joint LL | Qi Model A transferred joint LL |
| --- | ---: | ---: | ---: | ---: |
| Early 1–10 | 480 | 2.148221 | **2.103428** | 2.164320 |
| Middle 11–29 | 912 | 1.875955 | **1.874984** | 1.914675 |
| Late 30–39 | 480 | 1.666227 | **1.633371** | 1.796694 |
| All periods | **1,872** | 1.891990 | **1.871607** | 1.948435 |

Qi transferred next-occupancy LL: early 1.535910, middle 1.378807, late 1.266049; predicted excess next cost early 3.216071 vs observed 4.0125; middle 3.125976 vs 2.838816; late 3.076566 vs observed 2.06875. These are not evaluations of other Qi model variants B/C and should not be treated as an external validation of our own theory.

## Paired conditional session bootstrap
For each group, same heldout source event and two fixed forecasts from fully independent train folds: paired difference `Qi transfer joint LL - epoch20 joint LL`. 24 whole-session units drawn 20,000 times with replacement (seed20261105). The fitting is **not rerun in bootstrap**, data repeatedly inspected, and model selection not adjusted.

| Selection | Groups | Qi minus Epoch20 mean joint LL | Exploratory 95% percentile interval |
| --- | ---: | ---: | ---: |
| Full, all n and periods | 1,872 | +0.076827 | [+0.041809,+0.112764] |
| Full, early all n | 480 | +0.060892 | [+0.022800,+0.100204] |
| Full, late all n | 480 | +0.163323 | [+0.060053,+0.261713] |

Within THIS author-approved historical experiment, time-conditioned individual probabilities fit the target U,D groups more closely than the newly transferred Qi Model A using only cost and previous route, at the specified information constraint. This may reflect distinct experiment populations, time dynamics not in Qi Model A, unobserved personal effects, miscalibration or repeated source-driven choice of model; it is **not evidence that the original Qi theory is invalid, that group strategic dependence exists, or that we have identified a causal learning mechanism**. Qi's model had different experimental scenarios, calibration scope and observables.

## Repository and manuscript gate
- [Literal Qi Model A formula and train-only MLE Ruby](p3/qi_model_a_transfer.rb).
- [Synthetic equation/heldout tests](p3/test_qi_model_a_transfer.rb): local Ruby source-equivalent 5 tests, 14 assertions, no errors.
- [Paired 24-session source-sealed bootstrap](p3/qi_model_a_paired_bootstrap.rb) and [source-free tests](p3/test_qi_model_a_paired_bootstrap.rb).
- [Previous simplistic cost-gap comparator](p3/full_info_route_gap_logit.rb) is deliberately distinguished from literal Qi equation.
- Source original and individual rows stay only in private Drive; only aggregates, code and non-sensitive mathematical findings go to GitHub.
- Not yet done: Qi original Table1 parameter estimation and reproduction on Qi's own 312-subject eight-scenario experiment; official SSM models, EWA strong benchmark, proper new independent dataset, 40-period generative rollout from legal history, and remotely checked GitHub Actions PASS; **all HOLD**.
- Valuable conclusion for RITHM is a **stronger prior-art firewall**: route-attraction, independent stochastic group transitions, stationary flow distributions and model-transfer explanations are already in literature. A publishable contribution must distinguish information and adjustment-clock interventions and their finite-horizon welfare with falsifiable observations and, if causal claims are made, new identification.
