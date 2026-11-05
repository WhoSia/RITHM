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
