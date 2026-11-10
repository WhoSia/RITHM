# RITHM-2.10 — Independent Midterm Research Audit (2026-11-10)

**Research authority: diagnostic audit, not a paper acceptance. Overall: NEEDS REVISION before causal/novelty claims. Evidence slices PASS at synthetic/local-verification level.** Scope is the RITHM laboratory's R23–R27-R5 line, not every GitHub commit, paper in the Commons, or every past model.

## Executive verdict

1. **Retain mathematical constructions:** R27-R1 64-outcome observational equivalence; R27-R3 exact 6-person private-versus-social route-change wedge; R27-R4–R5 finite-state counterexamples, conditional on their explicit assumptions. Do not call them new universal theorems. Social minimum C(4)=24 differs from equilibrium dynamics.
2. **Retain, but relabel original-source evidence:** re-ran the R27-R2 model on the original-author SHA-verified CSV with 24 sessions; three model score metrics matched archival outputs. Selection is training-only within the recorded protocol but these 24 sessions were reused throughout earlier work and bootstrap intervals are exploratory.
3. **P1, source-population mismatch:** original author script `0 data preparation.R` explicitly retains session 101 outside treatment 1; R27-R2 filters out session 101 for ALL treatments. The session-101 treatment-3 block has **three complete six-actor groups**, 40 rounds, consistent actor IDs and full information access. A separate author-compatible 25-session sensitivity with 5×(20-train, 5-heldout) folds gives different but directionally same metrics. The original 24-session, 6-fold protocol stays as a documented *restricted* sensitivity; do not silently overwrite it. New [audit source](p3/r27_audit_session101_25fold.py) and [source-free tests](p3/test_r27_audit_session101.py) are separate from the historical baseline.
4. **P1, future-derived labels:** author R source `0 data preparation.R` lines 75–124 explicitly computes `switchWill`, `NumAnext`, `NumBnext`, `NumSwitchWill`, `switchAtoBWill`, `switchBtoAWill` using `Period+1` actual outcomes. The names are misleading: `switchWill` does **not** encode a contemporaneous stated intention. In privately held treatment-3 data (exclude sessions 2, 101 for this specific comparison), independently verified `switchWill` matches next-period route change on **11,232 / 11,232** eligible actor-transitions; `NumAnext` matches future count **11,232 / 11,232**; **288** period-40 actors have -1 sentinel. These are allowed forecast *targets* and retrospective labels, NEVER t-era decision predictors. Audited Python sources R23, R26, R27-R2 do not name these future fields; no demonstrated leakage in those checked files. Full Ruby/legacy and all dependent scripts **not** scanned; risk HOLD. [Source-free preventive guard](p3/r27_audit_temporal_leakage.py) and [tests](p3/test_r27_audit_temporal_leakage.py) added.
5. **P1, research interpretation:** R27-R3 switches use s as a REAL resource cost, not an empirical estimate of psychological laziness. R27-R4–R5 assume free predetermination of which participants benefit from reviewing and may restrict each agent's choice rights. Equal *horizon-average* review budgets or switch budgets are not cost, individual, or period parity. Do not turn a synthetic feedback finding into causal evidence or policy recommendation.
6. **P1, reproducibility identity:** source-free local R27-R3–R5 25/25 tests passed; actual original CSV SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb` matched. However Git blob hashes for the local R3/R4/R5 scripts differed from the public GitHub sources, so these local tests do NOT certify exact clean-checkout/remote GitHub state. Investigate version/alias differences, freeze source SHA/NumPy version, and run GitHub checkout independent tests. Remote CI PASS unverified.
7. **Prior-art correction:** newly ingested Marden & Shamma (2012) already studies relaxed synchronous updates, time-varying action sets and information restrictions in log-linear learning; Horowitz (1984) already studies oscillations in two-link route choice; Smith (1984) has continuous-time Lyapunov stability; Caballero & Engel (1993) studies state-dependent adjustment hazards. The novelty claim cannot be *oscillation*, *asynchrony*, or *hazard dependence* in isolation. RITHM's potential contribution must be a **clearly differentiated mechanism/identification/welfare result**.

## Cited source and population reconstruction

Original-author ZIP `rererequestforpermissiontouseexperimentalroutechoi.zip`; inside `0 data preparation.R`:
`(Period>=1 & session!=101 & session!=1) | (Period>=1 & session==101 & trt!=1)`.
The actual CSV's session IDs include 2 but not 1; the R script excludes session 101 **only when trt==1**. Session-101 trt=3: 3 groups × 6 people × 40 periods = 720 individual decisions and 3×38 = **114** scored 2-lag group-periods. Existing 24-session full-info analysis: 48 groups × 38 = **1,824** scored group-periods. Expanded 25-session analysis: 51 groups × 38 = **1,938**; per-session score weighting is appropriate when session is the independent unit; session 101 has a different number of groups and should not be naively row pooled. Source changes should not be treated as causality.

The empirical full-information per-group mean stage congestion in 24-session source is **26.9671875**; `C(N)=24+3(N-4)^2` agrees exactly with sum of all six actual per-person `Cost` records in every checked six-person group. Individual `profit=Value-Cost` agrees to floating-point tolerance in every observed trt=3 record. Thus at *fixed participation and exogenous value*, minimizing congestion corresponds to maximizing observed profit; R27's hypothetical switching-resource charge is NOT observed in these historical payouts.

### R27-R2 author-source sensitivity, not confirmatory evidence

| Eval | 24 sessions, 6-fold (20/4) | 25 sessions, 5-fold (20/5) |
|---|---:|---:|
| Scored group-periods | 1,824 | 1,938 |
| Independent six-choice joint logloss | 3.294912942 | 3.301773983 |
| Latent six-choice joint logloss | 3.272754373 | 3.271294564 |
| Latent minus independent joint logloss | **−0.022158569** | **−0.030479419** |
| Latent minus independent seven-count logloss | **−0.011109460** | **−0.022221884** |
| Latent minus independent one-period cost MAE | **+0.125484603** | **+0.119653742** |

The signs survive this specific source-population and fold perturbation. But changing **both** sample and split cannot isolate session-101 impact; add a common splitting-design sensitivity before causal conclusions. Values are 24/25-session historic exploratory reanalysis, not new external data.

## Synthetic transition audit / robustness

The R27-R5 original-user 6-person, 448-state, 40-round matched-**opportunity** witness was numerically independently rechecked at four representative (`beta, rho_max`) pairs with absolute deviations below **5×10⁻⁹** from the saved aggregate. The base config (`beta=.6, s=0, w=0, tau=0, lambda=3`) yields adaptive total congestion **24.2503739** vs equal-review uniform **27.5267845** at `rho_max=.3` (adaptive minus uniform **−3.2764106**), but **43.0779653** vs **30.1656660** at `rho_max=1` (**+12.9122993**). Same number of review opportunities over H=40 does not imply the same per-period/individual schedule, cognitive work, or agent autonomy. Likewise, equal actual switches differs from equal review opportunities.

Initial-distribution stress: starting with all previous masks at exactly `N=4`, the 40-round equal-review cost difference adaptive minus uniform was **−0.562020** at `rho_max=.3` and **+7.579757** at 1; all A=N=6 initialization produced **−2.947056** and **+9.320824** respectively. Thus this observed directional reversal survived those starts while the magnitude depended on the prior. Horizon stress (uniform prior): H=10/40/160/400 for `rho_max=.3` yields differences **−3.576956/−3.276411/−2.105901/−1.606336**; for `rho_max=1` **+12.383634/+12.912299/+12.496284/+12.099956**. Neither finite grid proves long-run stationary welfare or universal optimality.

**Screening-cost sensitivity:** at (`beta=.6, rho_max=.3`), prescreening all 6 actors in every period erases the 3.27641 equal-review opportunity benefit if extra real resource cost per actor-period is above **0.54607**. This is an accounting threshold under a hypothetical cost model, NOT a measured human mental cost.

The naive strict drift `V=(N-4)^2` cannot be nonincreasing at every state under nondegenerate stochastic choice, since at N=4 it is zero while expected next-step V may be positive. This is an exact counterexample to the overstrong Lyapunov proof claim, not proof that no stochastic Foster–Lyapunov condition exists.

## Original literature custody update — 00_INTAKE (verified by Drive readback)

Original-intake PDFs were bibliographically identified from their own content; moved without changed Drive IDs:
- [Marden & Shamma (2012), *Revisiting Log-Linear Learning: Asynchrony, Completeness and Payoff-Based Implementation*](https://drive.google.com/file/d/1fQGV-IiA8fKfM89GeC01lZlCysx2IiCN/view): final GEB 75(2), 788–808; now `10_PAPERS`; DOIs 10.1016/j.geb.2012.03.006. Its explicit stochastic-stability guarantees for modified log-linear learning are prior-art, but conditions differ from R27's beta-fixed joint law.
- [Caplin & Spulber (1987), *Menu Costs and the Neutrality of Money*](https://drive.google.com/file/d/1rU4bP29fm82DBTkTcoFv6PnYTcZOINyw/view): **NBER Working Paper No. 2311, July 1987**, not the QJE publisher PDF; canonical singleton in `10_PAPERS`, with this version note retained in audit metadata.
- [Sandholm (2010), *Population Games and Evolutionary Dynamics*](https://drive.google.com/file/d/1ahyWT5wdJnYYE3qH8YmBqQg9IoKZC1cO/view): MIT Press monograph, initial and contents pages confirmed; now `11_BOOKS`.
- [Dixit & Pindyck (1994), *Investment under Uncertainty*](https://drive.google.com/file/d/1qsZ_b-YATLxG4ZfyYKCeifeD6dns7I4d/view): Princeton monograph, bibliographic title/publisher/contents confirmed; now `11_BOOKS`.

All four received `Surname (Year) — Full Title.pdf` filenames under the current Research OS naming standard; move IDs and new parents re-read. These four entries must be removed from the **missing literature** list. Full line-by-line reading of both complete monographs was NOT completed; do not claim so. No other intake files changed.

## Operational quality/gates (interim inventory, not total repository)

| Gate | Result | Boundary |
|---|---|---|
| Privacy | PASS for checked new GitHub audit scripts | New scripts and checks contain no private participant rows. Raw original CSV stays local. |
| Source fixity | PASS | Original CSV SHA-256 matches; new intake exact existing Drive IDs preserved. |
| Synthetic numerical reproducibility | PASS for inspected local sources | 25 source-free tests PASS and selected grid values independently recomputed. |
| Original-data reproducibility | PASS on archived R27-R2 evaluator | Both 24- and 25-session scoring paths locally executed; NOT equivalent to confirming current GitHub clean-checkout. |
| Source eligibility | **P1 NEEDS CORRECTION** | Existing R27-R2 core excluded session101 treatment3 unnecessarily under original author data prep. |
| Future-field leakage | HOLD on full repository | Direct checked source model Python files not using future columns; author CSV names create trap for other users. |
| Scientific interpretation | **P1 HOLD** | Friction psychology unmeasured; full-information previous counts documented; sampling and method-selection reused, no policy causality. |
| Prior-art completeness | **P1 HOLD** | Marden 2012 and Sandholm 2010 just added; theorem-level comparisons not yet fully done. |
| CI / GitHub exact checkout | HOLD | Local models differ in Git blob from current GitHub for R3–R5. Remote Actions PASS not verified; CI registration is not execution. |

## Decisions and concrete follow-ups

**RETAIN:** R27-R1 exact countermodel; R27-R3 private/social wedge; R27-R4–R5 synthetic conditional sign reversals; source-verified R27-R2 forecast score directions.

**DOWNGRADE:** every statement claiming true human cognitive friction parameter estimation, experimentally demonstrated optimal nonzero friction, universal stochastic stability or new result for asynchronous learning. Exploratory bootstrap 95% intervals cannot be used as independent confirmatory inference.

**FIX NOW:** separate author-admissible 25-session fivefold source sensitivity from frozen 24-session sixfold history, explicit future-label quarantine tests and source-specific identifiers. Archive text vs live GitHub code must be compared by byte identity before claiming comprehensive reproducibility.

**NEXT:** (i) evaluate 24 and25 populations with SAME fold-comparison design and session weighting, (ii) a private-experienced-cost-only rival against revealed counts using proper t-only filtration, (iii) resource/agency cost parity and truly per-period review budgets, (iv) formal stochastic drift outside a target set, (v) source-code publication/CI independently executed, (vi) line-by-line Marden–Shamma and Sandholm prior-art mapping.

**User action:** none; more literature is now present and canonically sorted. This midterm audit does not confer paper publication readiness.
