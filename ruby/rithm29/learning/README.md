# RITHM-2.9: Information-filtration-safe learning histories

## Source-of-truth

Noussair & Qiao, *Congestion Information and Efficiency: An Experiment*, **Online Appendices** (September 18, 2025), Drive https://drive.google.com/file/d/1xwIj82h_LTrgffv2w4XtJs2KDc8980RW/view, Appendix A (EWA-lite), B (Small Sample Models), J (instructions). Main paper: https://drive.google.com/file/d/1rTL9qTpYV6zwee6pC3nZy64H07oSWzlK/view.

Informed participants receive historical congestion/number on each route. Uninformed participants know their own choices and received payoffs, not realized route occupancy or a uniquely identified cost from their own payoff alone (random trip values conceal it).

## Corrected Ruby API

`RithmLearning.features(rows, informed: true)` expects chronological `:period, :route_a, :num_a, :cost`; its experienced occupancy/cost quantities are available to informed participants.

`RithmLearning.features(rows, informed: false)` expects `:period, :route_a, :payoff`. It **never reads** `:num_a` or `:cost`, not even when those keys are present. It exposes `:previous_mean_feedback` as realized **payoff**, never as route cost. Both variants use only prior observations and own route-switch history.

Do NOT concatenate the two types' `previous_mean_feedback` as if one common-scale feature: one is cost and the other is payoff. Normalize/encode by informational treatment in downstream fitting. In particular, occupancy familiarity and realized relative costs are undefined as participant-accessible variables for uninformed players.

### Tests

`ruby ruby/rithm29/learning/test_history_features.rb` (Ruby stdlib Minitest): no future leakage, informed histories, hidden occupancy invariance under stripping hidden fields, payoff requirement, invalid route rejection.

## Author learning models are richer

EWA-lite Appendix A:
(N_i(t)=\phi_i(t)N_i(t-1)+1);
(A_i^j(t)=[\phi_i(t)N_i(t-1)A_i^j(t-1)+\delta_i^j(t)\hat\pi_i^j(t)]/N_i(t)).
Uninformed agents' expected foregone payoff uses **uniform beliefs over compatible unseen counts**, conditional on observed payoff and own route, not realized hidden counts. The change detector uses type-specific observational beliefs. A full reproduction requires actual payoff-support rules, parameters and sequence logic.

SSM5: informed samples 5 past trials where both realized/foregone payoffs can be inferred from occupancy. Uninformed samples separately within **trials actually choosing each route**. If only one route has ever been sampled, random choice. SSM1–9 uses uniformly chosen sample size 1 through 9. This Ruby feature module is **not** a simulation of EWA-lite or SSM.

## Previous CV caveat

The earlier GroupKFold scores 0.5930/0.5281/0.5097/0.5091 were produced by a separate exploratory Python predictor using realized congestion features for all rows. They describe an **oracle-data prediction benchmark** and must not be treated as information-feasible participant decision models. They have NOT been re-estimated after this information-set correction. No inference about psychology or causal mechanisms follows from their scores.

## Theoretical purpose

Compare (a) self-confirming learning under partial feedback, (b) satisficing/aspiration rules, and (c) strategic forecasting from information actually seen. A good next experiment varies feedback scope, exogenous shock response, and elicited expectations.
