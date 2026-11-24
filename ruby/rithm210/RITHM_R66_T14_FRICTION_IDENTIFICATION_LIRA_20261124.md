# RITHM-2.10 R66-T14 — Endogenous Information Acquisition, Persistent Friction and LIRA/JEV Audit

2026-11-24 KST. Native Ruby / Minitest, main only. No original participant rows, new human recruitment or independent causal claim.

## 1. Research director judgment
T13 varied exogenous attention and thresholds; T14 uses explicitly optimal one-shot information acquisition under a specified subjective prior. It is not a fitted rational-inattention model, nor a dynamic Bayesian equilibrium. The repeated model holds beliefs fixed, ignores strategic anticipation and learning, and assumes conditional unilateral gain at old occupancy. A common occupancy prior puts 19/20 extra mass on n=4 plus a uniform 1/20 over n=0..6. Conditional own-route beliefs are obtained by size-biasing by n or 6-n. Expected uninformed gains A=-155/79, B=-20/41; perfect-information values A=29/553, B=132/287.

Cognitive friction model: independently drawn private costs 0 or 2, equal probability, to reveal n. Cheap types buy the signal, expensive types stay; all choose strictly positive myopic net gain if informed. Switching friction model: n already known, private switching thresholds 0 or 12 with equal probability. Under baseline both models flip with conditional probability 1/2 given strictly positive unilateral gain and eligibility, else 0. Exact full conditional labeled flip laws, all 7-state rows, and every finite occupancy trajectory law coincide under identical opportunity schedules and freshly independent types. Free disclosure breaks equivalence for cognitive friction; threshold removal breaks it for switching friction. This is a constructive nonidentification result under the stated class, not a new universal theorem or evidence of actual human mechanisms.

## 2. Exact congestion counterfactual
Initial A=5; H=40; original congestion excess 3(n-4)^2. Same per-actor eligibility 1/2.

| Schedule | baseline either mechanism | free disclosure to cognitive | free disclosure to switching |
|---|---:|---:|---:|
| common |55.879793|1164.000000|55.879793|
| independent |10.631263|27.995469|10.631263|
| fixed 3 |7.971241|18.999997|7.971241|

Partial independent disclosure among eligible actors at 0, .25, .5, .75, 1: common costs 55.879793,104.708207,211.378076,500.162621,1164.000000. Independent: 10.631263,12.767467,16.091045,20.966447,27.995469. Fixed 3: 7.971241,9.083509,11.065442,14.220418,18.999997. Not monotonicity proof on full continuum. Full disclosure common clock traps occupancy in closed class {0,6} after leaving 5; finite-horizon terminal optimum mass 0. Extreme values are intentionally pathological, not estimates. Partial disclosure also raises cost in this grid.

## 3. Persistent versus refreshed private types
Freeze initial independent high-cost types rather than refreshing them. Conditional on ha and hb immobile actors on A and B, track only mobile A count j; high types never move; low types deterministically revise if eligible and gain positive. Exact mixture over ha,hb. First-transition distributions match the refreshed model for every n0 and all three schedules. H40 at A5:

| Schedule | refreshed congestion | persistent congestion | refreshed terminal n4 mass | persistent mass |
|---|---:|---:|---:|---:|
| common |55.879793|325.218750|.997650369|.156250000|
| independent |10.631263|13.169985|.999999995|.968749956|
| fixed 3 |7.971241|10.765802|.9999999999|.968749995|

Permanent cost type is NOT acquired habit or dynamic learning. With all five initial A actors immobile (probability 1/32), A5 never corrects, regardless of clock. First-step equivalence does not guarantee full baseline equivalence between refreshed and persistent populations; repeated histories are informative.

## 4. Resource accounting (not full utility welfare)
Physical per-switch fee f>=0 and per-free-offer fee h>=0 added ex post: L_total=congestion+f*expected switches+h*expected offers. Fee does not enter individual choices here. Across common/independent/fixed3, baseline switch counts 8.204227/2.775297/2.431697; free disclosure counts 116/8.221196/7.666665; each full-disclosure policy offers 117 times. Thus the higher modeled resource loss under disclosure persists for any nonnegative f,h at this A5/H40 grid. Private effort, reference-dependent utility, transfers and the welfare value of information are not fully measured; cannot assert all welfare worsens.

## 5. LIRA/JEV operational decision
L = .25 B (bottleneck)+.25 D (discrimination)+.20 W (micro-macro welfare)+.15 F (feasibility)+.15 R (reusability); E=.30 directness+.20 independence+.20 reproducibility+.20 falsification+.10 scope. Claim support C and generalization G recorded separately. Scores are revisable judgments, not calibrated probabilities. READY/PREPARE/BLOCKED/DONE gates override L. Exact ledger R66_T14_PRIORITY_LEDGER.csv. Initial A .9525, B .8790, independent witness search .8550, Ruby regression .8330, papers .8290, repeated old-cohort tuning .6945. A/B/resource accounting DONE. T15-A actual habit vs fixed type .9230 READY. T15-B external witness integration .9255 PREPARE: do not duplicate authorized separate work. T15-C adaptive prior/feedback .8990 READY. CI .8405, literature .8290, reused-cohort tuning .6945. Conditional construction support C=1, E=.847 (direct 1, independence .35, reproducibility .96, falsification .95, scope .95), G=.30 for human-world applicability. Persistent-type result E=.827 (direct .98, independence .35, reproducibility .94, falsification .90, scope .95), C=1 within model, G=.25. These are provisional research judgments.

## 6. External witness and intake gate
Read existing Ashraf 2023 S01 qualification and reauthorization court (Drive docs 1Cy56fY_wkJP8GKiSf4-MFJA6nyHbXSExyO-KV7Lujws and 1SrjUsMbmltbM5eVGn4uBLfmT9zaWqvkTbWcz-EDNj7w). Study2 TAMU randomized 42 partial vs 49 control; subject 305 ends after period 65; frozen balanced windows P37-50/P52-65, excludes P51; prerecorded other players, not interactive welfare. Only M05.137 authorized; separate recourt required. No new replay here, no new causal estimate, no unauthorized successor. 00 contains 11 files with unrelated medical/literary/other titles; not moved. Prior 10 targeted missing paper candidates unchanged; no exhaustive re-audit.

## 7. Verification
Ruby 3.3.8. T14 29 tests/131 assertions; T13+T14 63 tests/200 assertions, all local PASS. GitHub code committed directly to main, no new branches. Exact remote CI completion not verified. Next: habituation vs persistent private costs with own-history state, then legal adaptive beliefs; independent evidence via existing authorized route only.
