# RITHM-2.10 R64 — Prospective Identification Design: Stable Group States or Merely Miscalibrated Individuals?

**2026-11-21 · DESIGN ONLY, no recruitment, no new participant experiment, no power calculation or identified causal result.** Any human experiment requires the relevant institutional ethics review, consent procedures and data protection approval before implementation. This is a methodological proposal, not permission to begin.

## Reviewer-facing causal question

Among six simultaneous route choosers, does providing **truthful common information about last-period route occupancy**, in addition to each person's own realized payoff, change the persistence of an efficient 4:2 state, beyond changes attributable to each person's marginal switching propensity?

A second question is whether the intervention changes 40-period collective congestion efficiency, independently of one-step prediction fit. R63B/C are incapable of identifying this question from the repeatedly explored original sample, because information mask and treatment context are intertwined and the all-stay residual depends on marginal calibration.

## Proposed randomized experiment: avoid treating 22,464 decisions as independent

Independent **six-person groups** are randomized, not individual decisions.

| Factor | Level 0 | Level 1 | Purpose |
|---|---|---|---|
| **Pre-intervention initial occupancy** | nonoptimal A3 | efficient A4 | Direct baseline-state contrast, assigned before information exposure |
| **Group information policy** | every participant receives only their own previous realized payoff | everyone receives own payoff AND truthful prior A occupancy, announced concurrently | Randomized common information exposure |

All choosers see their own prior route and payoff. They are never shown invented group states or other persons' rewards. Six-person actions are simultaneous. Payoff functions and the distribution of exogenous private values must be the SAME across randomization arms; exclude any design where the information signal silently changes the payoff rule. Groups must not communicate across conditions. Treatment assignment occurs at the **whole-group** level and remains fixed for the 40-round primary horizon to avoid unmodeled within-group crossover.

**Important**: forcing the initial occupancy is itself a treatment. Blocking initial A3/A4 and reporting both factorial effects is necessary; results from artificially seeded A4 cannot automatically generalize to naturally reached A4 later.

## Pre-specify causally valid estimands BEFORE observing outcomes

1. **Primary A4 transition**: among groups RANDOMLY assigned A4 at time 1, compare the probability that all six remain on their original route at the first post-information decision (t=2). This conditions only on a **pre-intervention random assignment**.
2. **Unconditional 40-round system outcome**: difference in expected sum of 40 round excess congestion costs between randomized information arms, analyzed at group level and stratified by assigned initial state. Report uncertainty and initial state interaction; avoid unit-of-analysis pseudo-replication.
3. **Behavioral secondary outcomes**: total gross switches, share of periods in efficient A4, first exit time from the assigned efficient state, frequency/duration of return to A4 and group-level transition distribution. Pre-define the cost function and resource switching parameter as separate; do not assume actual time/resource cost from a route switch without a calibrated empirical measure.
4. **Model diagnostic, not causal proof**: out-of-sample calibration of individual switch probabilities based on each participant's legal prior information; compare observed group no-change frequency with the product of calibrated independent probabilities. Even a residual need not mean strategic coordination: shared unmeasured payoffs, risk or individual-type heterogeneity are rivals.

**Selection trap**: do NOT compare P(all stay | group was A4 at t=21, information arm) as a direct randomized causal effect. Being A4 at t=21 is a post-treatment state; conditioning on it can induce selection/collider bias. Use this measure as a descriptive state-specific diagnostic, or estimate it with an explicitly justified longitudinal intervention method. The primary clean A4 effect uses randomized t1 A4 state and t2 outcome.

## Intervention and outcome checks

- Register randomization, permitted information fields, payoff formulas, all decision clocks, sample exclusions, simulation plan and primary test BEFORE any participant decisions.
- Check whether the information treatment truly makes each public signal visible at the intended time, without revealing future or counterfactual rewards.
- Independently pilot experimental software using synthetic agents for t1/t2 timing and incentive accounting. Do not count synthetic agent performance as human validation.
- Recruit enough independent six-person groups for a group-cluster power simulation based on the smallest worthwhile effect, plausible intragroup dependence and attrition. **No numerical sample size is certified yet**; estimate budget and power before promising a result.
- Pre-register independent baseline contenders: original authors' Small Sample, legal-information EWA, simple payoff-logit, a route-streak hazard, calibrated independent group law and a constrained group-state rival.
- Fix hyperparameters within training groups; analyze a fully sequestered set of new groups. Keep participant identities, financial details and raw choices privately protected with restricted permissions.
- Where feasible, validate in another occupancy size or network topology; efficiency A4 and its raw cost units are specific to the original six-person game.

## Discriminating outcomes / falsification

- If legal individual calibration explains A4 persistence and no group residual survives independent evaluation, **stop** strategic group-coupling claims. Negative outcome is publishable only when power/benchmarks and preregistration are adequate.
- If common information changes group stability, but individual switching propensities change correspondingly and explain it, claim **information affects individual adaptation**, not collective strategic coordination.
- If the randomized intervention induces a reproducible residual covariance beyond calibrated individuals, that supports **information-conditioned statistical dependence**, not by itself intentional coordination; belief elicitation or additional perturbations will be needed for a cognitive interpretation.
- If the effect appears only on the repeatedly explored original cohort or only with post hoc metric selection, stop confirmatory/promotional claims.
- If a robust new effect does survive strong baselines, repeat it in independently randomized groups and a distinct game parameterization before broad welfare generalization.

## Practical publication track

**Track A (available without new human data)**: fully reproducible benchmark/replication note — original Small Sample vs EWA vs legal-feedback models, equal sample sizes, honest source reuse, matched group-macro diagnostics. Likely a narrower methods/replication target; no new causation claim.

**Track B (requires independent experimental capacity)**: pre-registered factorial information experiment, state-stability mechanism differentiation and group-level causal outcomes. May support a substantive novel behavioral operations paper, but **value and feasibility remain uncertain**.

**Track C (only if a true theory gap is found)**: precise theorem with assumptions, nontrivial strengthening beyond classical distribution shift, Fréchet bounds, Wardrop convergence and standard Markov coupling. Otherwise do not spend another R-version restating existing proofs.

**Stop/Go:** R64 is the admission court. No R65 latent-state proliferation solely for lower in-sample or same-cohort one-step loss.