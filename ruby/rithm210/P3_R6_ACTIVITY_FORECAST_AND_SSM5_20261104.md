# RITHM-2.10 P3-R6 — Behavioral Explanation Court for Group Stability
**2026-11-04 KST | Status:** original-source matched observation-based predictions; not a validated causal model. Original free-running SSM5 replication is not yet done.

## Scientific target
In the real six-person route experiment, the Full-information group at exactly efficient starting occupancy n_t=4 is much more likely to exhibit zero actual route changes in late rather than early periods (22.08% to 58.37%), with lower next-period welfare loss. A strong behavioral theory should explain that CONDITIONAL persistence, not just full-sample (U,D) likelihood or mean occupancy.

## Data / custody
Original author-approved Noussair–Qiao ZIP in [Google Drive](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view). Extracted `data_task_all_switch_230705.csv`, SHA-256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`.
24 sessions, 5,616 six-person group transitions, 33,696 actor rows, trt1–3, sessions2/101 excluded, periods1–39. Data never uploaded to public GitHub.
Original-author paper in [private Drive, July 24 2026 revision](https://drive.google.com/file/d/1rTL9qTpYV6zwee6pC3nZy64H07oSWzlK/view); peer-reviewed [Management Science article](https://doi.org/10.1287/mnsc.2023.00056), published online Nov 6 2025, volume72(7) 2026.

## P3-R6a — First matched one-step activity forecast: analytical Bernoulli convolution
Take published RITHM-2.10 actor Markov model, alpha20 train-only session fold, conditioning each actor on treatment/informed, OWN previous route and OWN experienced cost. Sixfold sorted session-ID mod6; train on 20 sessions, score 4 heldout. Within the heldout experiment a person's current-section prior switch history updates strictly AFTER that period's prediction. Online strength20/80 are previous chosen regularizers from P2, not reselected on this holdout.
For actor i predict switching probability p_i. Poisson-binomial probabilities for U and D derive from disjoint previous-B and previous-A actor sets, independently under baseline. Define:
P(no actual switch)=P(U=0,D=0)=P(U=0)P(D=0).
P(opposing cancellation)=P(U=D>0)=Σ_{k=1}^{min(n,6−n)} P(U=k)P(D=k).
For realized binary outcomes use Brier and Bernoulli proper logarithmic scores, preserving individual switch-count information. Next-period cost mean computed exactly from P(U,D): E[3(n+U−D−4)²]. All calculations are ANALYST-level and do not imply an uninformed player sees six histories.

Original-source *local* Ruby3.3.8 matched results (n=5616):
| model | no-switch Brier | cancellation Brier | next-welfare mean MSE |
| baseline | .1423782298 | .1182403917 | 18.07549273 |
| online20 | .1352588932 | .1161822703 | 18.31503316 |
| online80 | .1384064236 | .1169852965 | 18.05059677 |

20,000 whole-session transition-weighted paired bootstrap seed20261104 exploratory 95% for online minus baseline:
- online20 no-switch Brier delta -0.00711934, interval [-0.01349298,-0.00233068], 19/24 sessions improve.
- online20 cancellation Brier delta -0.00205812, [-0.00318624,-0.00102984], 19/24 improve.
- online20 next-welfare expected MSE +0.23954043, [+0.01385365,+0.46229543], 4/24 improve.
- online80 no-switch Brier delta -0.00397181, [-0.00651474,-0.00193608]; online80 cancellation Brier -0.00125510, [-0.00179937,-0.00077188], but welfare MSE -0.02489597, [-0.10061005,+0.0443288].
All exploratory: same original source, no independent prospective validation or pre-registration; model families came from research on this dataset.

**Crucial conditional failure at socially optimal starting occupancy n=4, Full treatment:**
- EARLY (154 transitions): observed P(no switch)=0.22077922. Predicted baseline0.36483815; online20 0.31865990; online80 0.34985755.
- LATE (257 transitions): observed P(no switch)=0.58365759. Predicted baseline0.36525382; online20 0.27469162; online80 0.31718877.
The baseline and history models fail to capture late no-switch behavior despite improving proper scores averaged over all group periods. Selection of groups conditioning on n=4 may affect group composition, and treatments rotate by section: this failure is an OUT-OF-FOLD PREDICTIVE diagnostic, not an identified mechanism or causal information effect.

[GitHub Ruby source](p3/activity_event_cv.rb) · [Minitest](p3/test_activity_event_cv.rb). Local version with same formulas and dependencies functionally reproduced the numerical result (3 tests, 7 assertions, no failures), but exact final GitHub checked-out SHA execution with original source remains unverified.

## P3-R6b — Recovery of authors' original Small Sample rules, then a separately named CONDITIONAL diagnostic
The **actual original author working paper** was found in Research OS Drive, July24 2026 revision. Appendix B §B.1 Table12 defines:
- SSM5 sample size q=5 (with replacement) from past plays each trial; first choice random.
- Informed actor: sample q earlier trials (each reveals both chosen and unchosen-route counterfactual payoff), compare sample average payoffs of the two routes.
- Uninformed: if only one action ever used, choose randomly; else independently sample q observed payoff records from the periods in which each route was actually chosen; compare sample averages.
- SSM1–9: actor-specific q_i sampled uniformly from 1..9 (original model), not implemented here.
- Original paper performs FREE-RUNNING forty-period agent simulations; its Table7 simulation outcome should NOT be claimed reproduced by a teacher-forced regression on observed history.

Ruby `ssm5_conditioned.rb` uses observed individual histories of periods up to and including t to forecast next route at t+1; counterfactual forgone payoff is computed from realized other-user count ONLY for originally informed actors. The uninformed actor samples only their actually experienced profits for each chosen route, never counterfactuals. An analyst combines the six conditionally predicted next-route probabilities to forecast gross U,D and next welfare, assuming conditional independence. For the known SSM5 sampling randomness, each actor/period propensity is approximated by 128 independent q=5 Monte Carlo draws; ties split 50/50. Repeated with independent seeds 20261104 and 20261105 to check sensitivity.

Two seeds yielded:
- Overall no-switch forecast 0.07186399 and 0.07186412 vs realized 0.18857.
- Full early current n=4 predicted 0.21625 / 0.21070 vs realized 0.22078 (n=154).
- Full late current n=4 predicted 0.13834 / 0.13888 vs realized 0.58366 (n=257).
- Overall binary no-switch Brier approx 0.16089 / 0.16079, cancellation Brier 0.12585 / 0.12613, next welfare expected MSE 42.9153 / 42.9236.
That is poor conditional forecast under THIS OBSERVED-HISTORY EVALUATION. It does NOT invalidate authors' paper, their original free-running simulations, or the broader Small Sample mechanism. The conditional evaluator is a distinct statistical object. Tie handling and Monte Carlo error remain modeling choices; finite 128-draw probability estimation itself introduces additional noise. The simulations restart histories by section, as the paper models a single 40-trial segment.

[Conditional SSM5 Ruby](p3/ssm5_conditioned.rb) · [tests](p3/test_ssm5_conditioned.rb): local independent implementation 4 tests/5 assertions, zero failures. Note exact published source dependency path differs from local prototype; a checked-out SHA replay and 10k-trial original model simulation remain OPEN.

## Mechanism and academic novelty gate
The original authors already acknowledge a key discrepancy between Small Sample predictions and data, including information-dependent long-run efficiency; our conditional P(no-switch) contrast is a sharper welfare-linked TARGET, not a demonstrated new scientific mechanism. The human data cannot alone establish cognitive adjustment cost or long-term urban welfare.

Next concrete steps: (1) fully recreate free-running SSM5 and SSM1–9 under the exact original game/values/partial information assignment, replicate Table7 outcomes before a fair model competition; (2) obtain 24-session bootstrap of Full n=4 calibration gap and evaluate fixed-state activity-conditional score, (3) test nested treatment-epoch interactions and P(no switch) calibration after adding actual activity persistence; (4) connect the resulting changes in *true churn* to a separately justified real resource cost θ and welfare, not claim θ measured in the laboratory.
No GitHub bot authorship. GitHub Actions read-only unit gates added. CI remote PASS, exact repository SHA original-data replay, and full original author model reproduction are **HOLD**. 
