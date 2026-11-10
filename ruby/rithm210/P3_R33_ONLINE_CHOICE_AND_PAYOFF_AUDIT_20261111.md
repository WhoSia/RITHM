# RITHM-2.10 · P3-R33 — Within-Partial Choice Habit versus Received Payoff History

2026-11-11 · Original-author 24-session exploratory source replay · NOT causal identification.

## The precise falsification question
Can a participant's within-Partial observed received-payoff history improve next-route prediction after retaining their stable pre-Partial route preference and current Part-I cumulative route-choice history?

## Source and lawful filtration
Private author's CSV SHA-256: `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`.
24 manuscript-main sessions (exclude 2,101), 48 stable six-person Partial groups, 1,872 group-periods t=2..40, 11,232 individual next-route predictions.
Every current Partial predictor is constructed online only from the participant's own already completed choices and realized **received payoff** in periods < t. Previous public occupancy is used only if Informed=1; future outcomes, experimenter-only Cost/Value, and later treatment sections are forbidden.
Prior-route preference score from completed treatments before Partial; section order and missing-prior status retained.

Four fixed logistic model families use the same L2 ridge 0.02, original session-anchored sixfold train20/test4 session holdouts, training-only R26 latent-shock tau grid {0,0.2,0.4,0.6}. Each session equally weighted.

Additional online features: (1) smoothed past Partial A-choice habit `h_t=2(2+Σ_{k<t} y_k)/(4+t-1)-1`, (2) *selected received payoff difference* `g_t=[Σ_{k<t,y_k=1} profit_k/(4+n_A) − Σ_{k<t,y_k=0} profit_k/(4+n_B)]/10`. The latter is **not a counterfactual route utility gap**; it compares payoffs conditional on actually chosen routes and mixes travel-value noise with congestion and selection.

## Held-out replay

| Model | Actor logloss | Six-person joint logloss (independent) | Seven-count logloss | Cost MAE |
|---|---:|---:|---:|---:|
| R32 prior-route preference | 0.550642233 | 3.303853398 | 1.409787813 | 2.911179426 |
| + online Partial choices | 0.518505340 | 3.111032043 | 1.398644732 | 2.777836399 |
| + online Partial received payoffs | 0.524594919 | 3.147569513 | 1.395785721 | 2.820229784 |
| + online choices and received payoffs | 0.512930144 | 3.077580862 | 1.392894981 | 2.744520743 |

Incremental past-received-payoff information beyond the online choice-habit rival: actor logloss Δ=-0.005575197, independent 6-mask joint logloss Δ=-0.033451181, occupancy logloss Δ=-0.005749751, cost MAE Δ=-0.033315656.
The 24-session exploratory resampling 95% interval for its joint logloss difference was [-0.042436503, -0.024600642]; because the same data were adaptively explored in R23–R32, this is NOT a preregistered confirmatory confidence interval.

## Interpretation and adversarial boundaries

Online past choice habit markedly improves over historical pre-Partial route propensity, consistent with dynamic participant-level dependence; it does NOT prove habit causes behavior. Received-payoff route differences provide additional out-of-session prediction even conditional on online choice habit, but are selected outcomes and therefore do NOT identify a psychological reward-learning effect or the cognitive/resource cost of deciding.
Model cost MAE is a *forecast* quality score on the fixed observed history, not an improvement in actual social congestion.
Temporal features were designed after inspecting prior R29–R32 analyses; all source-reused evaluation is exploratory.
The R26 symmetric group shock preserves individual marginals but does not identify group cognition. Full independently verified GitHub checkout CI remains HOLD until executed.

## Reproducibility and source boundaries

Local source exact-byte SHA for original CSV was checked; the historical R32 baseline individual logloss 0.55064223299 and independent joint logloss 3.30385339795 reappeared exactly.
9 source-free unit tests PASS: R32 nesting, hidden occupancy firewall, t+future outcome noninterference, feature separation, valid history requirements. Full historical source replay uses NumPy/SciPy dependencies, which must be installed separately.
All saved reports and ZIP include aggregate results and code but no participant-level original or derived records.

NEXT: use training-only hyperparameter selection for payoff-history smoothing; compare route-specific payoff against within-Partial route tendency with stronger randomized negative controls and preferably a fresh independent cohort; source-legal cross-treatment model must respect reward/public count visibility.