# RITHM-2.10 P3-R17 — Mechanism-Explicit Information Refresh × Adjustment Clock

Date 2026-11-05 KST. **Scientific status:** fully source-free synthetic exact counterexample and randomization design; new human behavioral causal result, originality and journal claim HOLD.

## Original motivation and prior art
P3-R16E/F showed that improved one-step choice event logloss did not imply better 40-round cumulative welfare mean absolute error. Existing [Qi et al. Part I (2023)](https://drive.google.com/file/d/1r2M3lM2DHKD1MvPE_5iWg489fVzwdZVk/view), [Part II (2024)](https://drive.google.com/file/d/1sC_O0U_T90IdUeHXA400sgQJn1mAl4ar/view), Cantarella & Watling 2016 and other day-to-day route-choice work already cover route inertia, day-to-day stochastic flows and clock-dependent stability. **Do not assert that asynchronous decisions stabilize congestion as an original RITHM theorem**. Our next question is the design of an exogenously randomized, information-feasible experiment identifying welfare effects of information refresh and the schedule of action opportunities.

## R17A: equal opportunity exact labelled-player factorial
Six users have two routes; C(n)=n²+2(6−n)²=24+3(n−4)², n=number choosing A. Using publicly perceived occupancy n*: for an incumbent A, own unilateral switch gain is 3n*−14; incumbent B gain is 11−3n*. A *stipulated*, non-estimated synthetic decision rule picks p(switch)=1−epsilon if positive gain, otherwise epsilon. Main witness epsilon=1/10.

Each participant gets exactly ONE chance to switch per macro-round, avoiding the earlier one-agent-per-period versus all-agents-per-period unequal adjustment opportunity comparison. Two schedules: simultaneous decisions based on a snapshot versus uniformly random serial permutation. Two microtime information schedules: frozen report available at start, or updated current occupancy between sequential actor decisions. At a simultaneous decision, refreshed and frozen current snapshots coincide if they begin with correct current n. This makes the nominal information × clock factorial partly degenerate; any interaction identifies the *within-round applicability of new information*, NOT an independent universal main effect of both mechanisms. In an actual experiment an older truthful previous-period signal can make both simultaneous information arms differ too; these are separate designs and require exact signal timing.

Source-free Ruby enumerates the 64 labelled route masks and dynamic programs over already-updated actor-ID subsets; probabilities remain exact rational values, selecting each actor once in random order without replacement. Every occupancy kernel sums to one and preserves E[C−24]=3(Var(N)+(E N−4)²).

At initial n=4, epsilon=.1:
| Protocol | Mean next n | Expected next excess |
|---|---:|---:|
| simultaneous, frozen | 3.80000 | 1.7400000 |
| simultaneous, refreshed | 3.80000 | 1.7400000 |
| sequential, frozen | 3.80000 | 1.7400000 |
| sequential, refreshed | 3.88544 | 0.6297984 |

The exact 1-step protocol interaction is −1.1102016 cost units under this model. **This is synthetic and conditional on its response law, not a human policy causal effect.**

## R17B: finite-horizon distributional outcome
Compute all 7 occupancy-specific transition rows by exact six-bit enumeration and then autonomously propagate a 7-state distribution for 40 periods, starting n1=4, no human feedback, no intervening observed states, with 6 opportunities per macro-round and macro-round initial true n updated at each period. Accumulate expected excess C(n)−24 of the 40 occupancy states. Simultaneous frozen/refreshed and sequential frozen coincide at **705.2720417084** expected cumulative excess units. Sequential refreshed yields **24.2885730094**. Interaction −680.9834686989. This dramatic synthetic contrast results from a near-greedy discontinuous response and within-round negative feedback. It is NOT an empirically estimated effect and does NOT establish a general theorem. At initial n4 and epsilon=0 all protocols remain at exact equilibrium and yield 0 excess (boundary falsifier to unconditional strict-effect claims).

## R17C: randomized experimental estimand and status
Define potential outcome Y_g(c,s) as cluster g's 40-round excess cost under protocol c,s. Target factorial interaction:
tau=E[Y(seq,refreshed)−Y(seq,frozen)−Y(sim,refreshed)+Y(sim,frozen)].
Randomize **independent groups/sessions**, rather than strategically interacting individual players, to the 4 arms in a balanced manner, with one full group/same fixed six opportunities per macro-round. If 24 independent clusters are available, example allocation is 6 clusters per arm (**illustrative only; no power analysis or trial conducted**). Their observed arm-mean interaction contrast is unbiased in expectation over the balanced randomization for a fixed finite population of potential outcomes, assuming no intercluster spillover, truthful signal delivery, protocol adherence and no differential attrition. Within-group interference is allowed. Exact 24-permutation test for four distinct toy clusters confirms this design property; does NOT identify psychology. Behavior can jointly respond to signal timing, salience, peer behavior and forecast beliefs, so even valid randomization alone does not uniquely distinguish cognitive learning from social response.

## R17D: strictly finite sensitivity grid, not a theorem
For epsilon in {0,.01,.05,.10,.20,.30,.40,.50}, initial n in 0..6 (56 cells), the exact 1-step interaction is negative 48 times, zero 8 times, positive 0. At epsilon=.5 information carries no choice sensitivity; at n4 epsilon=0 all players optimally stay. This is only a prelisted rational-parameter grid for ONE decision law, NOT a universal sign claim for other learning agents, hidden types, information misreporting, clock protocols or true human subjects.

## Reproduction, custody, next gates
- [R17A exact rational six-player microstate](p3/update_clock_signal_factorial.rb) · [tests](p3/test_update_clock_signal_factorial.rb): locally 5 tests/54 assertions.
- [R17B autonomous 40-round welfare chain](p3/update_clock_welfare_rollout.rb) · [tests](p3/test_update_clock_welfare_rollout.rb): 4 tests/99 assertions.
- [R17C randomized session estimator](p3/factorial_session_randomization.rb) · [tests](p3/test_factorial_session_randomization.rb): 4 tests/13 assertions.
- [R17D sensitivity grid](p3/update_clock_sensitivity.rb) · [tests](p3/test_update_clock_sensitivity.rb): 3 tests/10 assertions.
- Total **16 local tests, 176 assertions, zero failures** on local source-equivalent Ruby 3.3.8. CI has been augmented with source-free read-only checks. Container public GitHub raw download failed because DNS is disabled. Final byte-identical GitHub checkout integrated tests and remote Actions PASS remain HOLD. GitHub commits are human authored; github-actions[bot] cannot be a contributor. No private subject-level CSV or source article bytes are committed.
- Full raw-byte-verified [Google Drive report](https://drive.google.com/file/d/1YBZPkXK_WFpanueWrz2mHmdRELa_9dSx/view?usp=drivesdk) under shared drive → doing → 20261105 김우준의 사유. SHA256 **bbec4f45f48f6efbd4d906b80ad33572ae06cd459c70bc5aa3cbeb3c46c0cee2** verified after authenticated re-download. That report contains R17A-C; R17D finite-grid check is added here.

**Next decisions:** R17E must test smooth choice-response and group heterogeneity negative controls, then ensure treatment assignment and signal ages can be independently manipulated; R18 needs power, truthful information display, protocol compliance and truly new randomized group data. The original SSM/EWA comparison remains outstanding. **No causal or publication novelty claim is promoted.**
