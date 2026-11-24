# RITHM-2.10 R66-T15 — Exposure-indexed Frailty, Renewal, and Prior-Sensitivity Court

2026-11-24 KST. Native Ruby, main only. Synthetic model; no new human recruitment, no participant rows, no new causal estimate.

## First-spell equivalence, cross-spell discriminator
At each observed eligible profitable opportunity, fixed independent fair type P is 1/4 or 3/4. Survival after k failures is S(k)=((3/4)^k+(1/4)^k)/2. A history-dependent renewal model with hazard h(k)=1-S(k+1)/S(k) has exactly this survival by telescoping, and resets k=0 at a switch. This is reduced-form duration dependence, not established psychological habit. Fixed-type posterior after k failures and a success has next hazard h_fixed(k,1) versus 1/2 after renewal. At k=0: 5/8 vs 1/2; k=1: 1/2 vs 1/2 (a negative-control stratum); k=2: 3/8 vs 1/2; k=3: 3/10 vs 1/2. Condition on eligible profitable exposures, not elapsed calendar time; actual eligibility and perceived gain may be latent in human data. This is standard frailty-mixture arithmetic applied to RITHM, not a new general duration theorem.

## 84-state exact group model
Four counts [A slow,A fast,B slow,B fast] sum to six. Initial types are independent fair draws. Positive unilateral gain determines favorable direction; all other actors stay. Only eligible favorable actors flip with type-specific probability. On successful switch, independently redraw that actor's type with probability r, otherwise retain it. No redraw on stay. At r=1 this represents the exposure-indexed renewal law given complete opportunity/choice histories. With incomplete observations it need not be identifiable. All initial occupancy first-step distributions are equal at endpoints, and n=4 is absorbing. The first-step equivalence does not imply identical multi-period paths. Exact hypergeometric activation counts checked against labelled opportunity mask enumeration, not a full independent transition oracle.

At n0=5,H=40 cumulative congestion excess L(n)=3(n-4)^2:
| r | common | independent | fixed three |
|---:|---:|---:|---:|
| 0 |68.201584|10.238257|7.723954|
| .25 |56.485161|10.279595|7.776946|
| .50 |51.544761|10.351713|7.843843|
| .75 |48.863304|10.447711|7.922252|
| 1 |47.319603|10.564976|8.011285|

The effect of resetting responsiveness changes sign by schedule. This is a five-point sensitivity grid, not a continuum monotonicity theorem. Partial renewal is a chosen mechanism, not a structural fit or actual information-policy effect. No private cognitive cost counted as physical welfare.

## T14 prior robustness correction
Prior pi_lambda(n)=lambda*1[n=4]+(1-lambda)/7, size-biased by own route. Expected prior gain A=(-3-5lambda)/(3+lambda); B=(18-20lambda)/(3-lambda). EVSI A=29(1-lambda)/(7(3+lambda)); B=132(1-lambda)/(7(3-lambda))-max(E[g_B],0). For lambda<1 both information values are strictly positive and below 2 (B EVSI below 1); A EVSI bounded by 29/21. Under T14's costs 0/2 versus switching thresholds 0/12, strict positive-gain and strict information-purchase tie conventions, the ALL physically feasible state/route response function equivalence holds exactly for .9<=lambda<1. Below .9, B expensive information types switch on their positive prior even in unfavorable actual states. At lambda=1, EVSI=0 and costly-info model stays; equivalence fails as an off-support response-function comparison, but on the sole prior-supported n=4 both stay. This is a boundary for the specified family, not an identification theorem for arbitrary priors. No claim about actual Bayesian updating yet.

## Priorities and evidence
T15-A .9230, T15-G .9285, T15-H .9355 DONE. T16-A lawful adaptive beliefs .9370 READY; T16-B Ashraf existing authorized outcomes/authority .9255 PREPARE; T16-C full independent transition oracle and habit rival .8885 READY; CI .8405; literature .8290; old-cohort tuning .6945. Scores computed by prior exact T14 weights; no automatic promotion based on score. JEV evidence vectors direct/independent/reproducible/falsification/scope: spell [1,.40,.98,.96,.97] E=.865; group [1,.40,.98,.94,.94] E=.858; prior [1,.40,.98,.99,.98] E=.872. Conditional claim support C=1 for exact model; generalization G=.30/.25/.25 provisional judgments, not probabilities. No fresh external empirical evaluation. The S01 existing court permits only its authorized next work; no duplicate or unauthorized execution.

## Verification
Ruby 3.3.8: new T15 16 tests, 2233 assertions; combined T13–T15 79 tests, 2433 assertions, zero failures/errors/skips. Six new Ruby blobs read back at commit 911861b5b74ddee40c7be5317180ab628bc20529 and matched the exact local tested files. Remote CI remains unverified. Source-free archive includes inherited dependencies; source data excluded. Next: compare legal own-payoff Bayesian beliefs to fixed prior and explicit habit/frailty rivals without tuning repeatedly on old human cohort.
