# RITHM-2.10 — P3-R27-R4: Asynchronous Revision, State-Dependent Hazards & Congestion Welfare

**2026-11-10 · STUDY / SYNTHETIC EXACT DYNAMICS · NO HUMAN CAUSAL CLAIM.**

## Origin and comparison

The motivating chain is personal frictions (real switching cost, inertia, cognitive effort) → asynchronous or simultaneous choice revision → dynamic group congestion → expected total welfare. R27-R3 compared positive **actual resource** switching cost with zero. A serious rival is to change the timing of revision rather than charge a cost. R27-R4 is a *source-free conditional counterexample*, motivated by Horowitz (1984), Smith (1984), Caballero & Engel (1993), and the not-yet-obtained Marden & Shamma (2012). No claim of new original theorem or that information restriction is an available free policy.

## Mathematical specification and exact 40-period evaluator

Six labelled agents, binary routes A/B; past state `X_t=(Y_(t-1), N_(t-2))` in 64×7=448 labelled histories. A user's time-t revision of their route, if eligible, follows the R27-R3 logit conditional on information disclosed and the **unilateral** hypothetical congestion improvement. Not all users revise simultaneously. Conditional on previous state, independent review availability `E_i~Bernoulli(h(g_i))`; if `E_i=0`, preserve prior individual route. If `E_i=1`, choose A using the previous R27-R3 logit `q_i`. The exact A probability, prior A indicator y_i, is `p_i=(1-h_i)y_i+h_i*q_i`.

Compare uniform revision `h_i=rho` with payoff-dependent revision `h_i=rho sigmoid(lambda*(g_i-c))`, where `g_i` is the individual's modeled unilateral gain from switching (already net of the REAL resource friction s). `rho∈[0,1]`, `lambda≥0`, and `lambda=0` **by definition** denotes uniform hazard rather than sigmoid half-rate. The revision opportunity itself has zero resource cost in the comparison; this is an idealized **benchmark assumption**, not a feasible intervention warrant.

With R26 fair signed previous-route latent joint shock tau, mix two independent Bernoulli product laws for plus/minus shock; conditional individual marginals stay exactly `p_i`. Exact labelled 448-state probability distribution propagated H=40 without Monte Carlo. Social cost `C(N_t)+s*(number of real individual switches)`; `C(n)=24+3(n-4)^2` and its feasible per-period minimum is 24. Initial last-route masks uniformly distributed, older N equal last N; all interventions use the same prior.

## 40-period outcome, beta=.6, s=0, memory=0, tau=0

| Review opportunity rho | Constant hazard social cost | State dependent hazard lambda=3 social cost | lambda=3 mean switches per group |
|---:|---:|---:|---:|
| .10 | 25.805452 | 24.635574 | .041604 |
| .30 | 25.950964 | **24.250374** | .077936 |
| .50 | 26.851133 | 24.347731 | .154207 |
| 1.00 | 47.559294 | 43.077965 | 4.212247 |

Full nominal opportunity rho=1 with uniform hazard returns the R27-R3 zero-friction model: cost 47.559294. With fixed independent probability rho=.1 (zero charge) cost 25.805452; with rho=.3 and state-dependent hazard lambda=3 cost 24.250374, close to theoretical one-period planner minimum C(4)=24. The beta=.6, rho=.3 uniform-hazard-to-state-dependent gain is −1.700590 in mean cost; **NOT a causal human effect or general inequality.**

In the exploratory 32-combination grid beta in {.15,.3,.6,1.0}, rho in {.1,.3,.5,1.0}, and hazard slope lambda in {0,3}, all 16 matched state-dependent hazard comparisons show lower cost, but selection is a grid result, not a universal theorem; at rho=1, beta=.6, gain-dependence alone still leaves very high cost **43.077965**, so asynchronous opportunity restriction and revision heterogeneity interact. Histories with extreme congestion can still provoke synchronous switches; a hazard is not a stability guarantee.

**Crucial inversion:** The R27-R3 positive friction result need not imply that society should introduce real resource costs. Revising how/when agents respond can reduce congestion while avoiding the resource cost. Yet revision scheduling/withholding is not free in real humans; agency, information access, foregone individual utility, lost option value and design costs must be considered. Our social objective omits these. This does not establish rho=.3 as globally optimal or beta=.6 as human behavior.

## Primary-source adversarial read

**Smith (1984)**, *The Stability of a Dynamic Model of Traffic Assignment—An Application of a Method of Lyapunov*, `Transportation Science` 18(3) 245–252, [canonical archived scan](https://drive.google.com/file/d/1NU3HcwTiNJmV0AP6J5-udcXJMjvFzy_J/view), page 247 (PDF third page) describes a **continuous-time deterministic** route-swapping dynamic in which a link/route with higher cost loses users at a rate related to positive cost difference and existing flow. Page 249 (PDF sixth page) states a stability theorem under continuous differentiability and monotonicity of the cost-flow function, constructing nonnegative Lyapunov `V(F)=sum_(r,s) F_r (C_r(F)-C_s(F))_+^2`, zero only at equilibria. This does NOT prove stationarity/stability of our finite six-actor discrete-time random simultaneous logit game: continuous-time flow, smooth feasible domains, and cost monotonicity assumptions are different. **Scope verified by direct visual reading of the scan's actual mathematical text**, not from low-quality OCR. R27-R4 investigates this prior-art contrast, not a replacement of Smith's theorem.

**Caballero & Engel (1993)**, [canonical paper](https://drive.google.com/file/d/18SaVLo-ZIewWUrPOA0Ul4EeHbTkOwNXN/view), distinguish a state gap from the rate of adjustment and reveal dependence of macro dynamics on cross-sectional heterogeneity; R27-R4's `h(g)` is a deliberately simplified hazard-family transfer, not a replication of their econometric empirical manufacturing model. **Horowitz (1984)**, [canonical](https://drive.google.com/file/d/16HGHq4Vv8xSPMQmv1YHmqIsx6taCer8q/view), already constructs different information/experience update laws that yield convergence or persistent oscillation in a two-link traffic setting; the qualitative instability observation alone is established prior art.

**O'Donoghue & Rabin (1999)**, [canonical scan](https://drive.google.com/file/d/1UPdI1PUkuquXT_aqb0Lo26LbdnVYEBfh/view), treats present bias/procrastination, analytically different from a real resource switching cost and from externally imposed review scheduling. Whole-scan mathematical line-by-line audit remains incomplete; do not imply model equivalence.

## Implementation, checking and holds

[Exact R27-R4 kernel](p3/r27_r4_async_revision.py); [source-free synthetic regression](p3/test_r27_r4_async_revision.py); [32-grid result](P3_R27_R4_ASYNC_HAZARD_GRID_20261110.json). Local equivalent-model 7 tests PASS, including (a) rho=1 nesting original R27-R3 joint law for all 448 histories (b) rho=0 exact no-switch, (c) 448-state normalization (d) R26 fair common-shock conditional personal marginals for each of 448 histories (e) admissible rates and (f) 40-period cost. GitHub test file extends this suite to 8 tests; remote Actions PASS, independent post-checkout execution and source bytes parity remain HOLD.

**Source/authority boundary:** No human data re-fit or new participant recruitment; no identified cognitive/psychological mechanisms or social policy effects. The stochastic common-shock implementation leaves individual marginals unchanged by construction, not proof of human coordinated behavior. Controlled synthetic construction is a useful *countermodel* against the claim that resource friction must be positive to stabilize repeated choice.

## Next crucial attacks

1. **Fair comparison of adaptation protocols:** match expected number of allowed revisions, opportunity rate, or information/computation cost. In the current comparator, rho=.3 and rho=1 represent different achievable option sets.
2. **State-dependent hazard + real experienced cost source replay:** two train-only models with individual chosen-route feedback and full-information disclosed counts. Avoid selecting models using evaluation sessions.
3. **Strong rivals and policy welfare:** forced asynchronous scheduling, opt-in review, price-based corrections and shared information smoothing; count genuine costs and participant agency.
4. **Theoretical stability:** derive drift/Lyapunov conditions for full discrete-time finite stochastic chain (e.g. expected drift of occupancy dispersion), not smuggle Smith's deterministic continuous-time stability theorem into our setting.
5. **RAVEL Return:** when and why does private adjustment friction become harmful versus suppress collective overshoot? Publish neither new theory novelty nor causality until adversarial independent testing and prior-art comparison.
