# RITHM-2.10 P3-R17E/F and R18-P0 — Robustness Counterexamples, Identifiability Repair, and Cluster Power Reality Check

Date: 2026-11-05 KST. **Status: local synthetic tests and SHA-verified historical planning summary; human causal intervention, external validation, originality and final GitHub Actions PASS HOLD.**

## What changed scientifically
P3-R17A–D's huge information-refresh advantage relied on a discontinuous synthetic near-greedy actor law, and its nominal 2×2 combined a partly degenerate simultaneous-refreshed arm. R17E actively challenges those claims with smooth responses, labelled actor heterogeneity and common shocks. R17F proposes a *different, executable 2×2 for sequential clocks only*: truthful previous versus current occupancy at the initial report crossed with within-round refresh allowed or not. R18-P0 checks feasibility against the authentic source's session-level welfare spread, not against a six-player/48-path pseudo-sample.

## R17E.1 Smooth response: signs can flip
Define individual switch probability at perceived n*:
p_i=epsilon+(1-2epsilon)*sigmoid(k*Delta_i(n*)+b_i+z).
Here Delta_A=3n*−14 and Delta_B=11−3n*. Each actor gets one switch opportunity, and selected actors in sequential mode are a uniformly random order without replacement. With epsilon=.10, zero biases/shared shock, k=.05, the 1-step information×sequential interaction in expected EXCESS group cost is:
- initial nA=0: **+0.25715826** (information refresh makes 1-step welfare worse);
- initial nA=2: **−0.16831995**;
- initial nA=4: **−0.97811787**;
- initial nA=6: **−2.16662067**.
This explicitly falsifies an unqualified nonpositive-effect inference from R17D's finite grid of the OTHER threshold law.

At the same k=.05 and nA=0, a 7-state, 40-period AUTONOMOUS smooth Markov rollout gives frozen cumulative excess **302.84628**, sequential refreshed **277.19629**, difference **−25.64999**. Thus a short-term increase can coexist with a lower long-term excess. At k=0 no information-responsive difference is possible.

## R17E.2 Persistent actor identity invalidates occupancy-only Markov closure
Under homogeneous exchangeable responses, 64-mask labelled dynamics exactly agree with the 7-occupancy-state 40-period rollout. With fixed six actor biases [2,0,0,0,0,0], k=.7, epsilon=.1, initial masks 15 versus 30 both have nA=4 but have one distinctive actor on opposite routes. The next n distribution total-variation distance is **0.26319224**. Exact 64-state 40-period frozen/simultaneous expected cumulative EXCESS cost is **548.08110** versus **547.82038**. The 7-state kernel implementation refuses persistent nonexchangeable biases; a marked-identity or otherwise history-augmented state is required to make long-rollout claims. This illustrates classical strong lumpability failure, NOT a newly proven general theorem.

## R17E.3 Common shocks reproduce negative signed welfare-pair effects without peer causation
Let an unobserved binary group shock z=±2 with equal probability shift all individual logit switch probabilities; six switches remain INDEPENDENT conditional on z. With initial A mask15, epsilon=.05,k=.7,bias_i=0:
Cov(Y_i,Y_j|current group)= (p_i^+−p_i^-)*(p_j^+−p_j^-)/4.
Mean within-route pair covariance **+0.08041559**, opposing-route pair covariance **+0.08978344**; opposing-route switches enter occupancy with opposite signs. Relative to independent Bernoullis with the EXACT SAME individual marginal p_i, the binary-shock mixture changes expected next excess welfare by
6 sum_{i<j} s_i s_j Cov(Y_i,Y_j) = **−0.93215051**;
mixture **4.21674339**, independent **5.14889390**. This is a direct synthetic negative control against interpreting the R13–R15 opposing-route residual component as directed strategic coordination. It does not establish the actual original experiment's latent group-shock process.

## R17F — Nondegenerate sequential-only 2×2 (truthful timestamped signals)
Fix RANDOM-ORDER SEQUENTIAL clock for all four arms; every person still receives exactly one opportunity per round. Independently assign:
factor 1: initial report is actual last-period A occupancy n_prev (timestamped lagged) versus actual current n (timestamped current);
factor 2: after each microaction, publish the current actual n before the next decision or keep the original report fixed throughout.
All occupancy reports are truthful at their labelled times. For a synthetic path with current n=4, actual previous n=2, epsilon=.1,k=.3, no heterogeneity/shock, one-round excess forecasts:

| Initial signal | Frozen within round | Refresh after microstep |
| --- | ---: | ---: |
| Truthful previous n=2 | **4.90508370** | **2.55405273** |
| Truthful current n=4 | **5.59504063** | **2.88221577** |

Interaction of initial signal freshness with feedback **−0.36179390**; both marginal contrasts are nontrivial. This resolves the earlier mechanical degeneracy but does **not** independently identify the simultaneous-vs-sequential clock effect. Such a clock contrast requires an additional separately defined treatment or a distinct study. If previous/current occupancy are actually equal, initial signal age has no difference—important positivity/target-population restriction. The past signal must be the group's REAL last occupancy, never a fabricated misleading current signal. Pre-registered experimental assignment must account for true state transitions and spillover.

## R18-P0 — Historical variance and basic feasibility
The original [author-approved ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view) supplies CSV SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. The new read-only planning module extracts **48 complete 40-round Full-treatment group paths**, with verified 39 transition continuity, in **24 sessions**. Crucial irregular cluster size: 4 sessions have 1 path, 16 have 2, 4 have 3—not 2 each. The group path cumulative total group cost mean is **1078.6875** (consistent with R16F); group-level sample SD **44.77563749**; SD across 24 **session-level unweighted mean path costs = 29.58918599**. Do not treat 48 group paths as 48 independent sessions.

For a future balanced 4-arm cluster experiment interaction tau=(mu_current,refresh−mu_current,frozen)−(mu_lagged,refresh−mu_lagged,frozen), independent clusters with equal variance sigma² and m clusters per arm, Var(tau_hat)=4*sigma²/m. Nominal 2-sided alpha=.05 and power=.80 *normal approximation* gives
m >= ceil(4*(z_.975+z_.80)^2*(sigma/delta)^2).
If one VERY TENTATIVELY plugs the OLD Full-treatment historical session-mean SD 29.589 into a hypothetical new design:
- target |tau|=10 total-cost units → **275 sessions/arm**, 1100 total.
- |tau|=20 → **69/arm**, 276 total.
- |tau|=30 → **31/arm**, 124 total.
- |tau|=40 → **18/arm**, 72 total.
- |tau|=50 → **11/arm**, 44 total.
- |tau|=70 → **6/arm**, 24 total.
At 6/arm, the nominal minimum detectable contrast is **67.6848 total-cost units**, not the small 1-period synthetic effects. THIS IS NOT a validated prospective power study: novel treatments may change residual outcome variance, no attrition, cluster imbalance, repeated within-session interference, finite-sample t critical values, or estimated covariates are accounted for. Participant count and 40-period duration are additional resource constraints. Collect independent pilot variance or use pre-specified blocking/ANCOVA to plan feasibility.

## Software, evidence, claims
New source:
- [R17E smooth response](p3/smooth_signal_clock.rb), [tests](p3/test_smooth_signal_clock.rb).
- [R17E exchangeable 7-state](p3/smooth_clock_welfare_rollout.rb), [tests](p3/test_smooth_clock_welfare_rollout.rb).
- [R17E heterogeneous 64-state](p3/labeled_smooth_welfare_rollout.rb), [tests](p3/test_labeled_smooth_welfare_rollout.rb).
- [R17E shock non-identification](p3/latent_shock_residual_counterexample.rb), [tests](p3/test_latent_shock_residual_counterexample.rb).
- [R17F truthful sequential factorial](p3/lagged_feedback_factorial.rb), [tests](p3/test_lagged_feedback_factorial.rb).
- [R18-P0 SHA-sealed planning](p3/r18_cluster_power_gate.rb), [tests](p3/test_r18_cluster_power_gate.rb).

Local Ruby3.3.8 analogue source: **21 tests / 570 assertions, zero failures**; the published GitHub tests are functionally matched but are not yet proven byte-identical to the local runs. Read-only GitHub CI references all six new synthetic suites, with no GitHub Actions bot-authored commits. Real participant rows, source CSV and downloaded prior-art PDFs remain outside public code.

Scientific verdict: these are *negative controls, identification repairs and feasibility analysis*, not human causal discoveries. Classical hidden-Markov and lumpability prior art remains a novelty firewall. Next must include credible SSM/EWA baselines, pilot-validated independent-cluster variance, truthful signal-age compliance, a power-feasible pre-registered new experiment and independent analysis before promoting an original publication claim. Avoid offering an impractical 24-session confirmatory trial for moderate effects.
