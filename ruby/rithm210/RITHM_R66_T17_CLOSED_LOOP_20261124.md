# RITHM R66-T17 — Closed-loop Belief Dynamics, Disclosure and Inefficient Absorption

2026-11-24 KST. Ruby 3.3.8; main-only. Synthetic, not a human-data estimate. No new participant recruitment or raw data included.

## Design and boundaries
Six labeled actors, actual n determined by simultaneous decisions; each observes own payoff and optionally last occupancy. Travel values represented by 10 equally weighted unit-interval midpoints, exact for the ideal continuous uniform emission's posterior support because route costs are integers. Subjective K transition is T(k,j)=rho*1[k=j]+(1-rho)*Binomial(5,2/3)[j], NOT the actual endogenous game transition or a rational-expectations equilibrium. Each actor has its own prior and posterior. Payoff precedes disclosure, update and next choice. Disclosure is independently drawn per actor per transition, including ineligible actors. Opportunity marginal 1/2 in all three clocks; execution probability conditional on positive expected gain above threshold is exogenous. No execution if indifferent. No lapse. Real resource loss beyond congestion not counted here. Simulation uses floats and tie tolerance 1e-12; rho<1 to preserve full predictive support. First-step exact Rational oracle integrates 10 payoff intervals then enumerates labelled activation and flip masks. Under full disclosure the true process is seven-state Markov, so exact H40 oracle is available.

## Paired grid and counterexample
n0=5,H=40, 400 tapes (seeds 170000..170399) per cell; 3 rho values x 3 clocks x 2 response rates x 3 disclosure levels = 54 cells, 21600 simulated trajectories. Shared random tape across policies; Monte Carlo SE is from paired differences, NOT uncertainty about actual humans. rho=.8:

| clock | response | none | half | full | full-none mean (MC SE) |
|---|---:|---:|---:|---:|---:|
| common | .4 |78.075|45.6525|36.270|-41.805 (2.736)|
| common | 1 |119.9175|473.0175|1165.0125|1045.095 (7.185)|
| independent | .4 |70.0275|25.4175|9.225|-60.8025 (1.558)|
| independent | 1 |77.850|44.5875|26.565|-51.285 (1.808)|
| fixed three | .4 |68.160|21.900|7.5825|-60.5775 (1.353)|
| fixed three | 1 |74.6175|35.415|19.485|-55.1325 (1.278)|

Full-disclosure exact expectations at rho=.8, response .4: 35.636532,9.672203,7.641180; response 1: 1164,27.995469,18.999997. The common response=1 law enters closed class {0,6} when it leaves n=5; full disclosure at rho=.8 reproduces a familiar T14 high-response pathology, not an independent new general theorem. At rho=.5 common response=1, half disclosure increases cost (282.375 versus no disclosure 199.02) but full disclosure yields 120 by trapping n=5. At rho=.2, no-disclosure mean costs exceed 420 across clocks while full disclosure yields 120. This can coexist with zero private value under T16's stationary-prior model because weak-sign ties can change actions and the realized state dynamics differ from subjective prediction.

## Exact inefficient absorption interval
At n=5 a remaining A actor faces K=4 and B actor K=5. Full previous-state disclosure gives next expected gains 2rho-1 and 1-5rho. With threshold kappa>=0 and strict switch rule, n=5 is absorbing exactly when max(0,(1-kappa)/5)<=rho<=min(1,(1+kappa)/2), assuming positive response and positive marginal eligibility. This includes strict interior (.2,.5) when kappa=0. No actual rational-expectations equilibrium claim: the misspecified reset predictor can disagree with the realized process. H40 congestion cost exactly 120. Tests compare 132 cases with labelled oracle. Widening with kappa is a conditional mathematical result, not a real-policy welfare estimate.

## Memory rival
400 different tapes (180000..180399) per cell, rho=.8,response=.4. Reset prior before every observation versus retain predicted belief. At q=0 reset/filter common 160.4925/80.9925, independent 160.815/70.8825, fixed-three 161.0625/66.2775; q=.5 67.65/47.46,44.505/22.4775,41.6025/19.3725; q=1 identical paths under same tapes. Memory can substitute for disclosure in this model; not a theorem of universal welfare improvement. For current model, no habit or stable private type added. This is an ablation, not causal discrimination of observed humans.

## Reproduction and gate
Run ruby r66_t17_experiment.rb 400 and ruby r66_t17_memory.rb 400. Run tests using Ruby -I. -e 'Dir["test_r66_t1[3-7]_*.rb"].sort.each { |f| require_relative f }'. T17 10 tests/1661 assertions; T13-T17 105/4441, zero failures. First-step float decisions matched rational across 720 configurations, 1500 samples per clock/disclosure cell tested against exact first-step distribution. Memory replay JSON byte-identical. Partial-disclosure long-horizon results are MC not exact. Source-free. No claim of remote CI. T18 priority: learn subjective persistence or transition from permitted signals, compare calibrated predictions against actual closed-loop dynamics and rival habits/frailty. Avoid equating calibration with causal mechanism. Ashraf PREPARE; no unauthorized successor. LIRA scores in CSV; E/C/G are provisional judgments, not probabilities: closed-loop .82/.90/.25; exact absorption .90/1/.25; memory .81/.90/.25. No human-data claims.
