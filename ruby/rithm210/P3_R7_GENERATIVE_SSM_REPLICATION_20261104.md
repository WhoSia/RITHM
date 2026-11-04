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

