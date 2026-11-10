# RITHM-2.10 P3-R27-R5 — Equal-Budget Adaptation, Hazard Selection Reversal and Screening-Cost Bound

**2026-11-10 · Status: synthetic exact numerical witness + prior-work consistency; NOT an observational finding or a deployable policy.**

## 1. Why this unit was needed — audit of R27-R4

R27-R3 showed that adding **actual resource switching cost** can lower congestion in a synchronous response family, but cost itself must enter welfare. R27-R4 instead imposed independent *revision eligibility* `E_{i,t}`, with `h_i(X_t)=rho` or gain-dependent `rho sigmoid(lambda*g_{i,t})`, making `P(A|history)=(1-h_i)y_{i,t-1}+h_i q_i`. The R27-R4 paper compared equal **maximum** revision probabilities `rho`, not equal **realized** numbers of opportunities. This makes claims that targeting is better fundamentally confounded by different eligibility budgets. R27-R5 corrects that comparison rather than hiding or reinterpreting it.

**No new human data were fit in this unit.** R27-R4's state-dependent gain signal uses *counterfactual unilateral next-route costs* given previous group occupancy; the experiment supplied full-information previous route counts, but did not directly reveal the human computation of `g_i`. Therefore a targeted hazard requires a **screening/calculation mechanism** before eligibility can be selected; its cost and the constraint on choice rights are omitted from the initial synthetic benchmark. This is not evidence that real people can achieve targeted low-cost updating.

## 2. Constructed state, costs and probability law

Six labelled binary road users, state `X_t=(Y_{t-1},N_{t-2})`: 64×7=448 states. At each period each agent gets a state-dependent revision opportunity; independent Bernoulli if `tau=0`. If ineligible, previous route is held. If eligible, follow the same individual R27-R3 unilateral-improvement logit. Compare uniform eligibility `h_i=u` against gain-adaptive `h_i=rho_max sigmoid(lambda*g_i)` with `lambda=3`. The optional fair binary R26 group shock is a valid probability mixture and preserves individual marginals but for main paired comparisons `tau=0`.

`g_i` is predicted *net private unilateral improvement* computed using last occupancy and last personal route, not realized general equilibrium benefit. Travel costs: `c_A(n)=n`, `c_B(n)=2(6-n)`, social congestion `C(n)=24+3(n-4)^2`. Starting distribution uniform on last actor-choice 64 masks, second lag initialized equal to last occupancy. All 40-period trajectories are propagated by a 448×448 transition matrix, no Monte Carlo draws. `s=0,w=0,tau=0` for the main comparison; thus social cost is just congestion and no scheduled review/agency cost is included.

## 3. Two different budget-matching contracts

**A. Equal *review opportunities*:** the adaptive policy endogenously visits certain states, resulting in `R_a=(1/H)sum_t E_a[sum_i h_i(X_t)]`. Since the **uniform** hazard produces exactly `6u` expected opportunities regardless of the state law, set `u=R_a/6`. This makes `R_u=R_a` to numerical precision over the entire H=40 horizon, but it DOES NOT match each individual period, actor, social cost, or number of actual switches.

**B. Equal *actual switches*:** choose uniform `u` by a numerically checked monotone bisection so that `S_u=(1/H)sum E_u[# switches]=S_a` to 5e-6. This does **not** match the number of review opportunities; its definition differs from A. Report both rather than conflating their apparent gains.

## 4. Result: equal-budget advantage and its reversal

With `beta=.6` and `lambda=3`:

| Adaptive max rho | Adaptive R: mean opportunities/group/round | Adaptive S: mean actual switches/group/round | Adaptive cost | Matched opportunity *uniform* cost | Matched actual switches *uniform* cost |
|---:|---:|---:|---:|---:|---:|
| .10 | .057451 | .041604 | **24.635574** | 28.865031 | 27.831920 |
| .30 | .118230 | .077936 | **24.250374** | 27.526784 | 26.678462 |
| .50 | .229298 | .154207 | **24.347731** | 26.511964 | 25.977972 |
| 1.00 | 4.487571 | 4.212247 | **43.077965** | 30.165666 | 40.536922 |

**Critical negative control / reversal:** the gain-targeted hazard is better under both matching protocols for rho_max=.1,.3,.5 but **worse** under both for rho_max=1. At rho=1, equal-opportunity target minus uniform cost = **+12.912299** and equal-switch target minus uniform cost = **+2.541043** per group/period. In the 12-pair parameter grid beta∈{.3,.6,1}, max chance∈{.1,.3,.5,1}, each of the lower three maxima improves cost, and all three beta conditions at rho=1 worsen cost. The direction is **not monotone and not a universal theorem**; it changes with model parameters, opportunity constraints and information processing assumptions.

The numerical exactness is the forward propagation conditional on specified parameters and state prior, **not exact knowledge of human behavior**. `rho_max` is a hazard cap, not the aggregate realized opportunity rate. A low realized review budget is much smaller than six agents per period: e.g. at rho=.3 the adaptive scheme grants 0.11823 reviews per group-period on average, implying roughly 4.73 group reviews across 40 periods.

## 5. Hidden screening cost and agency—explicit welfare boundary

A gain-dependent eligibility schedule implicitly knows or calculates `g_i` **even for those who will not review**. If it costs `c` resource units per actor-period to perform the prescreening for all six actors (and a uniform schedule has no such prescreening cost), then adaptive-social-cost extra `6c` must be included. For beta=.6,maxrho=.3 in the equal-review comparison the saving was `27.5267844544 - 24.2503738959 = 3.2764105585` per group-period; hence the break-even prescreening unit cost is

`c*=3.2764105585/6 ≈0.5460684264` per actor-period.

The analogous equal-*actual-switch* savings 2.428088 gives `c*=0.4046813341`; **this assumes equal switch volume, not equal review volume**. Any cost above these simple thresholds reverses the respective *accounting* benefit. This is only a sensitivity identity under the stipulated six evaluations per round; actual computing costs, observer agency, lost option value, consent, signal quality, mechanism feasibility and fixed policy costs are unresolved. Matching an equal budget does not imply a policy mechanism that is individually incentive-compatible.

## 6. Distinguishing prior work and RITHM research contribution

- [Horowitz (1984)](https://drive.google.com/file/d/16HGHq4Vv8xSPMQmv1YHmqIsx6taCer8q/view) already established that stability of repeated traffic decisions depends on learning/information update, so oscillation per se is not new.
- [Smith (1984)](https://drive.google.com/file/d/1NU3HcwTiNJmV0AP6J5-udcXJMjvFzy_J/view) proves a Lyapunov result for **continuous deterministic** swapping dynamics under smooth monotone link costs. Its theorem does not automatically imply a drift theorem for our discrete finite stochastic 448-state process.
- [Caballero & Engel (1993)](https://drive.google.com/file/d/18SaVLo-ZIewWUrPOA0Ul4EeHbTkOwNXN/view) motivated gap-dependent lumpy adjustment hazards; RITHM's `rho sigmoid(lambda*g)` is a simplified donor mechanism, not their fitted manufacturing model.
- **Marden & Shamma (2012)** remains a high-priority search-based-missing direct rival for asynchronous log-linear learning and stochastic stability; primary full text still to intake. Claimed originality remains HOLD.

The **provisional RITHM insight** is a falsifiable mechanism boundary: holding constant endogenous review budgets or actual switch budgets is necessary, and gain-targeting plus asynchronous updating can have *opposite welfare signs* at different opportunity ceilings. This is a model-specific counterexample, **not** priority over earlier learning dynamics literature.

## 7. Code provenance, tests and next proof gate

- [R27-R5 448-state NumPy reference model](p3/r27_r5_opportunity_budget.py): 448×448 state transition, no personal rows; exact floating-point probability propagation (not rational-arithmetic theorem), separate expected reviews and realized switches, calibrated uniform opportunity baseline, bisection-based matched actual-switch baseline.
- [R27-R5 7 tests](p3/test_r27_r5_opportunity_budget.py): all 448 state transitions normalized, old R27-R4 model-output parity, no opportunities no switches, review-budget equalization, realized-switch equalization, high-opportunity welfare sign reversal, parameter exceptions. **Local equivalent-model 8/8 PASS**. Remote GitHub Actions, clean-checkout independent test and reproducibility cross-hash remain HOLD.
- [12 matched pairs / main result JSON](P3_R27_R5_MATCHED_ADAPTATION_BUDGETS_20261110.json): no original participant data.
- Core model dependencies: R27-R3 and R27-R4 Python sources in the same `ruby/rithm210/p3` folder. CI NumPy installed in existing R26 dependency step.

**Next methodological gate:** equal budget **per period**, not only horizon-averaged; alternate revised gain signals without free pre-screening; user-initiated opt-in scheduling rather than restriction; account for true cognitive costs and the individual right to choose. For formal work, derive drift of a meaningful Markov Lyapunov function and compare expected depletion of an occupancy-distance potential under conditionally independent vs correlated revisions. Reuse the original 24-session participants only to test observed-choice likelihood conditional on disclosed information; human response mechanism not identified by static source reuse.

## 8. Additional adversarial checks (2026-11-10)

A 2×3 synthetic stress grid using `memory∈{0,0.5}` and marginal-preserving common-shock `tau∈{0,0.3,0.6}`, with beta=.6 and both rho_max=.3 and 1, preserved the **sign reversal** under both budget definitions in all six stress settings: for rho=.3, the adaptive-minus-matched-uniform cost was negative; for rho=1, it was positive. For example at memory=.5,tau=.6: rho=.3 yielded **−2.333765** (equal reviews) / **−1.684826** (equal switches), whereas rho=1 yielded **+7.616303** (equal reviews) / **+3.274717** (equal switches). This is a finite numerical stress set, **not general robustness** across mechanisms.

A naive candidate `V(X)=(N_{t-1}-4)^2` fails global strict negative conditional drift because at states with `N_{t-1}=4`, `V=0` and `E[V(X_{t+1})|X_t]>0` whenever there is nondegenerate probability of a non-optimal successor count. Local 448-state conditional drift numerically confirms this. Future drift proofs should use a small set / additive-noise bound rather than transplant the deterministic continuous-time Smith Lyapunov claim.

**Local reproducibility:** a dependency-contained local source-free ZIP with exact filename and byte hashes is generated for user download; fresh extraction in a new folder ran **9/9 synthetic regression tests PASS** with NumPy. The ZIP's legacy R3/R4 scripts contain local compatibility API aliases; the package is **not falsely described as byte-identical to the GitHub R3/R4 files**. The GitHub R27-R5 source itself uses the published R3 `Params` import and its own R27-R4 regression test; remote CI/clean published dependency re-run remains HOLD.
