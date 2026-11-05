# RITHM-2.10 P3-R11 — Occupancy-Only Observation Cannot Identify Gross Human Reallocation

**2026-11-05.** Exact 6-person combinatorial identification result. This is a *sharp finite-state observation theorem*, NOT yet a new general economic theorem, and NOT a fitted behavioral model.

## Observed macro versus latent micro
If the analyst only sees the number `n` of users on A before, and `m` after one simultaneous six-person choice, define `U` for B→A switches, `D` for A→B switches, and `G=U+D` for gross movements. Mass balance implies `U−D=m−n=δ`. Feasibility requires `0≤U≤6−n`, `0≤D≤n`. Therefore `U` ranges over all INTEGERS

```
max(0,δ) ≤ U ≤ min(6−n,m),  D=U−δ.
```

The **sharp identified set** for gross movements is

```
G ∈ {|δ|, |δ|+2, ..., 2 min(6−n,m)−δ}.
```

Every element is **constructively realizable** by selecting exactly U actors previously on B and D previously on A to switch. The endpoints are attained, not merely loose inequalities.

At the Nash-optimal occupancy `n=m=4`, the possible gross switches are `{0,2,4}`. All of these have the same aggregate occupancy and same pre/post congestion cost `C(4)=24`, and hence the same next group social excess cost `L(4)=0`. Two worlds with the same aggregate occupancy path may thus have arbitrarily different G, realized cancellation and unmeasured privately incurred effort. For a macro time series of occupancies `n_0,...,n_T`, the pathwise total gross movement is bounded sharply by the sums of each transition's two endpoints. The bounds remain attainable with individual route identities consistently assigned across all periods; the construction can use the newly constructed profile as the subsequent previous profile. Recording more periods of occupancy data ALONE does not resolve the ambiguity.

This is a precise **structural non-identification result** for pure aggregate observational data. If a physical switching cost θ per moved actor were **externally specified**, it would imply sharp switching-cost bounds θ times the range. The original experiment does NOT measure any such real-resource θ, and a subjective switching-disutility coefficient cannot silently be treated as social monetary waste.

## Crucial identification consequence
P3-R10's oracle-clock theorem says a nonoptimal-state aggregate count transition reveals the selected schedule type because the pure model's synchronous and asynchronous transition supports are disjoint. But this relies on **no spontaneous learning errors or mixed actions**. Once additional private belief changes permit gross opposing switches at fixed aggregate occupancy, an observed `n_{t+1}=n_t` no longer implies an absence of adjustment, and that support-based identification may disappear. Future structurally identified RITHM models should distinguish:
1. public occupancies and route costs;
2. person-identifiable A/B choices at both periods, yielding U and D;
3. exogenously randomized or logged decision timing;
4. each individual's available payoff/route signals;
5. actual real resource cost of switching, if measuring total welfare including adjustment costs.

Public cost/occupancy data alone cannot recover these microscopic objects. The authors' original participant-level CSV actually contains individual actions, so the observational restriction is a **measurement-design counterfactual**, not an excuse to ignore the microdata that are available.

## Ruby source and falsification
[Sharp identified-set Ruby](p3/occupancy_equivalence.rb) · [exhaustive all 49 pairs and constructive tests](p3/test_occupancy_equivalence.rb). Source-only CI test added. This is a pure combinatorial claim and its elementary proof does not depend on any fitted parameters, period order, SSM assumptions, EWA, latent state choices, or inferential significance.
**CI remote run PASS and exact SHA local test execution remain HOLD unless separately verified.**

## Distinguishing scientific hypothesis
It may be new to show that some experimentally identifiable features of **turnover composition** distinguish otherwise observationally equivalent macro congestion paths under FI/PI histories, and that they predict the persistence of shocks. But no originality follows from the combinatorial identified set itself; sharp bounds on hidden flows and partial identification are already a substantial existing literature. The contribution must be a nontrivial predictive restriction or identification theorem for an information-feasible learning-and-activation mechanism, plus external experimental validation.

## Related direct reading 2026-11-05, confirmed primary Google Drive originals
- Jiang, Wang, Yan, Li & Wu (2026), *Inertia-Based Strategy Updating Rule Design for Congestion Games and Its Application to NFV Networks*, *Information Sciences* 755, 123817, [Drive original](https://drive.google.com/file/d/1iQa3upEAAmugxZJS3ADxZ6NFtgETl_T5/view): Algorithm 2 forecasts congestion from finite histories, combines time-varying inertia with best response. **Theorem 1 establishes almost-sure convergence** to Nash set under that precise updating rule; Theorem 2 specifies inertia-based reaching-stage conditions. The file reports **available online 2026-06-24**, not first published 2026-11-05; prior chat's new-publication date was corrected.
- Heinrich et al. (2023), *Best-Response Dynamics, Playing Sequences, and Convergence to Equilibrium in Random Games*, *IJGT* 52, 703–735, [Drive](https://drive.google.com/file/d/1JIN6h5tQf75Y-e4HENYpgHEccml83-2F/view): random-game asymptotics distinguish prescribed cyclic playing order from randomized sequences; the random-games ensemble is NOT our one congestion game.
- Ackermann & Röglin, arXiv:0805.1130v1 (posted 2008; manuscript PDF prints 2018), *On the Convergence Time of the Best Response Dynamics in Player-Specific Congestion Games*, [Drive](https://drive.google.com/file/d/1xWTPXUM_oZ7visIGUv0mN3VC__JeyXNM/view): Theorem 2 bounds schedules in player-specific tree congestion games, special cases for cycle games and expected time. Do NOT apply generic player-specific-game cycling as evidence against exact Rosenthal potential in our standard atomic game.
- Srinivasan & Guo (2004), *Day-to-Day Evolution of Network Flows Under Route-Choice Dynamics in Commuter Decisions*, [Drive](https://drive.google.com/file/d/1x_zH2w3xQlzuiv_zrtYhfuwxDb19ILck/view): simulation of information availability, daily network evolution, and travel-time reliability/stability tradeoff. Early time-series instability is known prior art.

Original four PDF **file IDs preserved**, metadata normalized and moved from 00_INTAKE to 10_PAPERS on 2026-11-05 with successful Drive update replies. No raw PDF copy or redistribution in public GitHub.

## P3-R11b: Full source-session bootstrap and heterogeneity counterexample (2026-11-05)

An independently executed **Ruby 3.3.8** program parsed the SHA-256-sealed original CSV (5,616 group transitions, 24 sessions), filtered Full-information current optimum n=4 (early 154 and late 257 group transitions), and generated 20,000 **whole-session** bootstrap samples (seed 20261105). At each resample the homogeneous independent switch parameter epsilon was **re-estimated from that resample's mean gross changes**, rather than treated as known. The remaining three moments are out-of-model restrictions but **not out-of-sample predictions**.

| Era | epsilon from gross | P0 actual / model | cancellation actual / model | next group congestion excess actual / model |
|---|---:|---:|---:|---:|
| Full early n4 | .22619048 | .22077922 / .21468635 | .15584416 / .15615300 | 3.01948052 / 3.76445578 |
| Full late n4 | .09727626 | .58365759 / .54116434 | .07782101 / .05070947 | 1.33073930 / 1.69419673 |

Exploratory 95% percentile whole-session bootstrap intervals for **observed minus model**:
- early P0 +.006093, CI **[-.044596,+.058383]**; cancellation -.000309, CI **[-.053124,+.053452]**; next-excess cost **-.744975**, CI **[-1.330757,-.070015]**;
- late P0 +.042493, CI **[+.009824,+.070334]**; cancellation +.027112, CI **[-.000922,+.053584]**; next-excess cost **-.363457**, CI **[-.669958,-.096365]**.
The gross error is zero by construction. Confidence intervals are exploratory and based on *same-data moment fitting*, source is extensively reused, and no multiplicity or prospective design adjustment is applied. The result is a failure of **homogeneous independent Bernoulli switching**, NOT a test against arbitrary independence or causal strategic dependence. Source code [original-data cluster audit](p3/independent_churn_cluster.rb), [source-free synthetic tests](p3/test_independent_churn_cluster.rb); local original CSV program used equivalent code and completed 20,000 bootstrap draws. The original individual CSV is NOT placed on GitHub.

**Critical heterogeneous-independent counterexample.** For actor-specific switch probabilities `p_1,...,p_6`, each actor switching *independently*, write `U~PoissonBinomial(p_B)`, `D~PoissonBinomial(p_A)`. At n=4,
```
E[3(U−D)^2] = 3{(sum_B p_i−sum_A p_i)^2 + sum_i p_i(1−p_i)}.
```
A concrete independent distribution with `p_A=(1,0,0,0)`, `p_B=(1,0)` produces **two gross route changes with certainty**, but `U=D=1` and **zero next excess congestion**. In contrast, six i.i.d. switches with the same E[G]=2 have epsilon=1/3 and mean next excess **16/3≈5.333**, despite BOTH being mutually independent at the actor level. A nondegenerate independent case `p_A=(.8,0,0,0)`, `p_B=(.8,0)` yields E[G]=1.6, P0=.04, cancellation=.64, next cost=.96. Therefore **lower-than-homogeneous predicted welfare loss is not evidence of actor-level dependence**. At minimum compare against actor-specific independently predicted probabilities and validate their calibration/heldout performance.

[Heterogeneous Poisson-binomial Ruby](p3/heterogeneous_independence.rb) · [synthetic restriction/counterexample tests](p3/test_heterogeneous_independence.rb).

## Next methodological gate
Use an original-source out-of-fold predictor for each ACTOR'S time-t switch probability (including route, experience, knowledge condition, and session), combine the six probabilities under independent Poisson-binomial, and examine the **heldout residual covariance of actual actor switches conditional on their probabilities**; account for shared group cost information and non-exchangeable agents. The present gross-calibrated homogeneous benchmark provides motivation but cannot identify common shocks, strategic expectations or real social switching costs. Follow with external sessions/experiments under randomized information and adjustment timing to distinguish the effects.
