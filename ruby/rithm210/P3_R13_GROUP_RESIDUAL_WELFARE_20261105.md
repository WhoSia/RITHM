# RITHM-2.10 P3-R13 — Exact Micro-Residual Attribution of Conditional Collective Welfare Error

2026-11-05 KST | Stage: THEORY/IMPLEMENTATION COMPLETE, ORIGINAL-DATA RESULT HOLD.

## Scientific target
P3-R12 found systematic failure of three out-of-session actor-independent Markov/history models to predict the observed early-to-late fall in congestion cost at Full-information six-actor groups currently at A occupancy n=4 (154 early and 257 late transitions). This does NOT identify strategic dependence; individual calibration, shared latent shocks, and state-selection effects remain viable.

## An exact observation-wise identity
Let y_i∈{0,1} be route-switch decisions, p_i their strictly prior-information predicted switch probabilities, and s_i=+1 for B→A, −1 for A→B. Set e_i=y_i−p_i, m=Σs_i p_i, E=Σs_i e_i. The actual next excess congestion cost from n=4 is L=3(Σs_i y_i)^2, whereas the conditional-independence model forecasts L_ind=3[m²+Σp_i(1−p_i)]. Their discrepancy decomposes EXACTLY, for every realized binary y:
L−L_ind = 6mE + 3Σ[e_i²−p_i(1−p_i)] + 6Σ_(i<j)s_i s_j e_i e_j.

The final pair term is further split into same-current-route positive-sign contributions and opposite-current-route negative-sign contributions. This is a pointwise algebraic identity, not a new established causal law or a proof that a nonzero pair term must represent strategic interaction.

Under a genuinely correctly specified, history-conditional independent model, all off-diagonal conditional residual cross-products have zero conditional expectation, and the diagonal and linear terms also average to zero conditional on the model's information set. But marginal calibration alone is NOT sufficient to infer either conditional independence or correct higher moments.

## Implemented
- [Exact six-actor source-free module](p3/group_residual_welfare.rb): validates 4+2 route composition, binary outcomes, six probabilities and algebraic equality; reports welfare and signed same/opposing pair residual means.
- [64-outcome exhaustive tests](p3/test_group_residual_welfare.rb): independently checks every possible six-bit outcome for a fixed nontrivial p vector, deterministic correct prediction, directional residual signs, invalid inputs, and aggregate conservation.
- [Original-source SHA-guarded heldout analyzer](p3/group_residual_source_cv.rb): reuses P2's original 6fold session training and prior-only within-section actor-history learning for the three preexisting candidate models. Restricts to preselected Full n4 early/late 411 group transitions, computes per-group identity terms, but emits only aggregates. Provides 24-whole-session 20,000-draw exploratory bootstrap, conditional on the fitted models.
- [Synthetic bootstrap tests](p3/test_group_residual_source_cv.rb). No original human rows in the repository. The local authoring runtime passed the exact module's 5 runs/141 assertions and a separate adapter's 2 runs/5 assertions using stubbed source dependencies.

## Evidence limitations
The author-approved original experiment CSV stays in Research OS Drive, with expected SHA256 d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb. The new source adapter has **not** yet been executed against these original bytes in this P3-R13 turn, and it has not produced actual pair-component numerical estimates. Local synthetic/stub tests do not verify a full source runtime. Final merged GitHub SHA checkout and remote Actions PASS remain unverified. The original P3-R12 bootstrap is conditional on fitted models, not full retraining.

## Research decisions
1. Run the SHA-sealed original CSV on the exact final GitHub checkout. Reconcile the sum of component contributions with the existing P3-R12 gross welfare-error estimates for every model and epoch.
2. Inspect marginal calibration and grouping by actor route/treatment/time, then same- and opposite-route residual-pair terms. Check same-session temporal clustering and selection into n=4.
3. Test stronger actor-heterogeneous independent baselines with inner-fold-only calibration and historical predictors. The new residual decomposition is a diagnostic; it cannot identify direct peer influence from shared latent causes.
4. Only after confirmed predictive residual structure and independent external data / randomized information and adjustment-clock experiments should a new behavioral/causal finite-horizon welfare theorem be promoted.

Scientific ambition: information-feasible micro-learning and adjustment timing yielding testable collective welfare laws. The algebraic attribution is a stepping stone, not a replacement thesis.
