# RITHM-2.7 P25 — Stage-Legal Human Information, Repeated Choice and Welfare-Sign Ambiguity

**2026-10-13 · current RITHM-2.7 mainline · original-human-data exploratory reanalysis.** Predecessor RITHM-2.6 remains CLOSED by Flowing handoff; its entire positive/negative research inheritance stays in 2.7.

## Source and design

Original [Wijayaratna et al. (2017)](https://doi.org/10.1371/journal.pone.0184191) and [author S2 supplement](https://doi.org/10.1371/journal.pone.0184191.s002), previously original-source-verified [24 panel packed routes](../data/rithm23_wijayaratna2017_routes.csv). Six laboratory sessions / 144 humans / 480 group rounds and 5,760 final human routes. P25 fit/scored periods 2–20: 5,472 person rounds and 3,332 observed A–C entrants; 3,511 including period 1. Original six raw participant-cost versus theoretical group-cost discrepancies untouched. Current cost-history proxy is **computed from published cost geometry**, NOT original raw participant Cost.

**Exposure authority:** accident cannot be observed before upstream A choice; only online-information condition *at node C* offers current incident information to actually eligible A–C entrants. Information being *offered* does not verify reading, trust, compliance or individual causal uptake. After every round, participants saw prior individual/network conditions. Experimenter 4-of-20 incident quota hazard is not necessarily participant knowledge. These records and 2025 Seoul sensors are NOT a joint causal cohort.

## Six session-held-out rivals (exploratory; source has been repeatedly reused)

Fixed penalized logistic C=1; stage-A binary entry and conditional stage-C choice; use past actual history only, and integrate the experimenter finite incident hazard to predict theoretical collective cost **before current shock**. Group cost forecast uses individual conditional independence and hypothetical unobserved stage-C responses. All scores are fold means; lower is better.

| Model | Full-route logloss | Preincident group-cost MAE |
|---|---:|---:|
| CLOCK: time/arm/prior group signals | 1.043914 | 16.622649 |
| STABLE: older participant preference | .994021 | 16.403906 |
| HISTORY: recent actual branch and last eligible C | .978078 | 16.341043 |
| HISTORY_COST: previous theoretical cost/regret | .978054 | 16.213001 |
| LEGAL_EXPOSURE: current z only at offered node-C | **.929157** | 12.804076 |
| LEGAL_COST: legal exposure plus prior cost | .929842 | **12.652082** |

LEGAL_EXPOSURE vs HISTORY: full-route logloss reduction .048921, group-cost MAE reduction 3.536966, and actual-C-stage logloss reduction .080354, each improves in all 6 folds. History-cost incremental full-route gain only .000024 (4/6), too small for general novelty. **Illegal negative controls**: current accident fed upstream A worsens full-route score by .000455; accident supplied to blind-C mildly helps logloss by .000223 but worsens welfare MAE, and is unimplementable under the source clock. **Not a best benchmark:** older P6 with train-only joint residual correction gave lower group MAE in a related comparison (12.375989). The source experiment is not untouched independent confirmation.

Observed conditional C–B rates (periods 2–20): blind no accident 292/1222=23.895%, incident 105/341=30.792%; information condition no accident 869/1399=62.116%, incident 7/370=1.892%. Six session-specific descriptive information-versus-blind incident contrasts are negative (unweighted mean −.670335); conditioning on C entry creates selection concerns. Actual descriptive mean theoretical group cost: **210.629167 blind** vs **219.162500 info** (difference +8.533333), as in the prior experiment and 2.6 audit. NOT a new identified mediation or welfare intervention effect.

## Exact source-conditioned welfare-reachability check

On **all 480 ACTUAL observed human route allocations**, after upstream A choice fix q=n2+n3 and incident z; imagine an **additional** unobserved stage-C guidance changing at most k already eligible C branches. Enumerate all attainable downstream n2' in max(0,n2−k)..min(q,n2+k), including no change, and cost C=264−24n1−9n2+2n1²+2n1n2+n2²+19zn2.

With **k=1**, both favorable and adverse counterfactual cost changes are feasible in **369/480** observed group-round states (76.875%); some worsening in 472/480, some improvement in 376/480 (overlapping). Average *separate roundwise* sharp lower/upper gain endpoints −10.6458/+6.8458 group-cost units. With k=2, the ambiguous-sign count stays 369/480; average local endpoints −22.2/+11.3667. These do not establish a single feasible dynamic guidance policy across rounds or an observed intervention. This extends P24's selected synthetic witness to all historically observed real-human source states under explicit hypothetical branch-response restrictions.

## Verdict and next question

**PASS:** exact source timing/route reanalysis, exploratory staged prediction, source-conditioned finite welfare ambiguity. **Negative:** elaborate previous cost has negligible additional personal logloss gain, and illegal upstream current-incident leakage does not generalize better. **HOLD:** actual individual receipt/reading/trust, causal route habit, new advice compliance, genuine independent group policy-welfare effect, transfer to 2025 field sensors and novelty beyond classical response/partial-ID methods. Preserve all inherited 2.6 failures, six recorded-cost anomalies and prior-touched-data warning.

**Next within 2.7:** independent human experiment/person-by-period advice and actual node-C exposure, cluster-level randomized assignment or defensible interference-aware variation, independent route-specific experienced travel costs; compare frozen HISTORY, LEGAL_EXPOSURE and older P6 calibrated rivals *before* promoting a causal social-welfare claim. Otherwise present an assumption-conditional identified set, not a point estimate.

[2.7 live Notion](https://app.notion.com/p/3f8ef561cf9281829b60c1085605448d) · [2.6 historical source log](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021). A larger P25 chat-local reproducibility ZIP contains the executed model source, per-session JSON results, finite bounds and nine offline source/moment tests; GitHub Actions was not invoked.
