# RITHM-2.10 P3-R7 — Original Small Sample Simulation Replication and Conditional Stability Failure
**Research date:** 2026-11-04 (KST)  
**Status:** independent rule-based replication and exploratory diagnostic; causal mechanism and theory novelty NOT established.

## Primary-source custody
Noussair & Qiao, *Congestion Information and Efficiency: An Experiment*, author working-paper revision **2026-07-24**, Appendix B.1 Table 12, Appendix B.2 Table 7, held in [Research OS Google Drive](https://drive.google.com/file/d/1rTL9qTpYV6zwee6pC3nZy64H07oSWzlK/view). Original six-person experimental CSV, sealed SHA-256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`, retained privately in [Drive ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view). **No original individual row published.**

## 1. What was actually replicated
A full **autonomous, forty-period, six-actor generative Ruby model**, rather than feeding the model realized participant histories. Each trial has simultaneous choices. At the first trial each person chooses randomly; values are independent `Uniform[6,16]`, and actual route costs are A=`n_A`, B=`2(6-n_A)`. Informed agents observe both chosen and unchosen-route profits from prior realized other-player route choices; uninformed agents observe their chosen-route profits only. Subsequent decisions draw earlier experiences WITH replacement. SSM5 uses 5 trials per comparison; SSM1–9 assigns each actor one permanent `q_i ~ UniformInteger(1..9)` for the 40-period simulation. No treatment has 0 informed players; Partial has 3; Full has 6. When payoff sample means tie, choose either route with probability 1/2 (an explicit implementation convention, not a verified original RNG implementation). Authors' original code/random stream not available, so exact byte-level simulation equivalence is not asserted.

Two independent seeds with **10,000 complete 40-period simulations for each model×treatment** reproduce 24 reported Table 7 means and 24 reported standard deviations. Maximum absolute divergence for seed 20261104: **mean 0.012915; SD 0.009128**. Seed 20261105: **mean 0.01193; SD 0.009284**. Table 7 reports only two decimal places.

| Model/treatment | Authors cost early | Ruby cost early | Authors cost late | Ruby cost late |
| --- | ---: | ---: | ---: | ---: |
| SSM5 No | 4.66 | 4.66308 | 4.29 | 4.29437 |
| SSM5 Partial | 4.61 | 4.60178 | 4.35 | 4.33709 |
| SSM5 Full | 4.87 | 4.85888 | 4.49 | 4.48541 |
| SSM1–9 No | 4.67 | 4.67220 | 4.33 | 4.32680 |
| SSM1–9 Partial | 4.61 | 4.60239 | 4.37 | 4.36715 |
| SSM1–9 Full | 4.82 | 4.82393 | 4.46 | 4.45240 |

[Original-rule autonomous Ruby](p3/ssm_generative.rb) · [activity extension](p3/ssm_activity.rb) · [48-value original Table 7 reproduction test](p3/test_ssm_table7_replication.rb). The 10,000-game test ran locally on Ruby 3.3.8 and passed **1 test / 48 assertions** with tolerance 0.03 on each published mean/SD; two other local model tests: 7 tests / 91 assertions / zero failures. The 10,000-game original paper comparison is rule-level numerical replication, not model explanatory novelty.

## 2. Scientific discriminator: optimal-state persistence
Use each fully *simulated* game's transition from period t to t+1, conditional on `n_A(t)=4`, and ask whether **all six actors retained exactly their previous choices**. Early means t=1..10 and late t=30..39; this aligns to the experimental switching-response period labels. Original experimental Full observed early `34/154=0.22077922`, late `150/257=0.58365759`; observed late−early **+0.36287837**.

Independent Ruby 10,000-group simulations, seed 20261104:
| model Full | simulated early P(no gross switch | n=4) | simulated late | late−early |
| --- | ---: | ---: | ---: |
| SSM5 | 0.60177773 | 0.50317535 | **−0.09860239** |
| SSM1–9 | 0.58837994 | 0.49650935 | **−0.09187059** |
| ACTUAL experiment | **0.22077922** | **0.58365759** | **+0.36287837** |

The independent 20261105 random seed yielded SSM5 0.60077260→0.50157793, and SSM1–9 0.59823106→0.50566844, still opposite to the observed temporal direction. Importantly, the original Table7 level statistics can match closely while this **conditional turnover statistic fails**. The previously attempted `ssm5_conditioned.rb` was a DIFFERENT observed-history teacher-forced diagnostic; do not confuse its ~0.138 late forecast with the new correct **free-running** SSM5 ~0.50 late rate.

The SSM5 observed-minus-simulated **change in rates** is **+0.46148075**. Repeated sampling of all **24 source sessions as blocks** (20,000 draws; seed 20261104) yields exploratory percentile 95% **[0.31841961,0.58837208]**, conditional on the fixed estimated 10,000-game model output. The interval excludes simulation Monte Carlo uncertainty, non-preregistered moment selection and actual experimental assignment/order confounding. It is a **diagnostic calibration gap**, not a confirmatory test rejecting an identified psychological mechanism.

## 3. Falsification attempt: varying SSM sample size q
Before claiming SSM cannot generate later stable groups, vary the **fixed informed SSM sample size** q. Exploratory independent self-generated 40-period Full games, **5000 groups per q** (seed 20261104; q drawn from preselected set 1,2,3,5,9,15,30):
| q | simulated early optimal-state no-switch | simulated late |
| ---: | ---: | ---: |
| 1 | 0.59057 | 0.49992 |
| 2 | 0.57522 | 0.49305 |
| 3 | 0.58442 | 0.49983 |
| 5 | 0.59012 | 0.48908 |
| 9 | 0.60949 | 0.52320 |
| 15 | 0.65908 | 0.64846 |
| 30 | 0.70963 | 0.81854 |
Increasing q **can reverse the temporal direction** of no-switch persistence: q30 shows more late stability than early, so the universal claim “Small Sample learning cannot create rising stability” is FALSE. However q30 greatly OVERpredicts early no-switch versus the observed 0.22078. Under the extra exploratory grid q=1..30, 1000 groups per value (same seed), the smallest simulated early no-switch fraction was **0.5820**, far from observed 0.2208. This demonstrates failure across this CHECKED finite grid to fit both early and late levels, not a formal impossibility result for every sample-rule variant or continuous parameter.

[Sample-size sensitivity Ruby](p3/ssm_q_sensitivity.rb), [synthetic tests](p3/test_ssm_q_sensitivity.rb). Simulation sampling uncertainty, common-random-number choices and multiple post-hoc q comparisons remain limitations.

## 4. Interpretation and program direction
**Actual scholarly result supported so far:** A faithful public-description implementation independently reproduces the original published gross cost and average occupancy patterns, but the SAME model gives a sharply different conditional transition behavior at the socially efficient occupancy. Existing published paper already identified various dynamic mismatches; our candidate increment is the **specific optimal-state activity moment tied to next-period welfare**, not the authors' short-run/long-run information result or a new universal theorem. Identifying any genuinely novel cognitive or strategic mechanism requires formal prior-art contrast and external / prospective tests.

Distinguish three predictions:
1. `P(n_t)` average occupancy and distribution;
2. `P(U_t,D_t | n_t=4, information,t)`, especially no gross movement;
3. `E[L(n_{t+1}) | n_t=4,...]`, where `L=3(n-4)^2`.

A model can fit (1) and fail (2)/(3). Retain behavioral model heterogeneity, group uncertainty, adaptation clocks and genuine information availability as competitors. Do NOT fit a post-hoc 'stickiness' feature and declare it a psychological law from the same 24 sessions.

## 5. Verification and provenance
Code commits have human author/committer `WhoSia`; GitHub Actions tests are **read-only, no bot-written source**. New CI jobs execute [basic SSM tests](p3/test_ssm_generative.rb), [activity tests](p3/test_ssm_activity.rb), [q sensitivity tests](p3/test_ssm_q_sensitivity.rb), [48-stat Table7 replication](p3/test_ssm_table7_replication.rb), and [session/bootstrap gap tests](p3/test_ssm_observed_activity_gap.rb).
Local 10,000-run replication passed 48 checks, and 7 local generative/activity tests passed 91 assertions. Published GitHub tests are slightly refactored relative to earlier local tests; full checked-out HEAD SHA replay and remote GitHub Actions run ID/job success are **not verified**: do not assert remote CI PASS. Github combined status and workflow runs queries returned empty arrays as of this research.
Simulation aggregate results are reproducible by Ruby standard library code and fixed seeds; original human participant observations are not published.
The next discriminating research unit should derive a theory for the *hazard of exiting an efficient allocation* and explicitly compare (a) individual retrospective sampling, (b) strategic anticipation and (c) group-specific latent regime adaptation, then assess real congestion and separate switching resource costs, with the original 24 sessions providing only exploratory constraints.
