# RITHM-2.10 — Scientific Self-Audit and Return to the Original Micro→Macro Thesis
**Date:** 2026-11-04 KST. **Status:** Research-direction decision, not manuscript or novelty certification.

## 0. Verdict
RITHM has become substantially more discriminating about claims, but its scientific target has narrowed. The original program asks how small behavioral, cognitive, procedural and informational frictions, through repetition and endogenous interaction, produce macroscopic congestion, long-lived inefficiency, inequality, institutional lock-in and policy nonreach. Recent 2.9/2.10 empirical work instead centers on individual switch prediction, joint-turnover forecasting and identification of latent correlation. This is a **necessary middle layer, not the principal explanandum**. We should retain 2.10's identification court but make the micro-to-macro generative and welfare problem the principal research spine immediately, without inventing a new generation or prematurely declaring novelty.

## 1. Scientific achievements, not software deliverables
- **Exact observational equivalence:** A latent common shock with conditionally independent individual actions and an SCM with a directed U→D link can generate the same complete P(U,D), but have different do(U) distributions. This is a valid constructive *application* of standard causal nonidentification, not an established novel theorem.
- **Correct falsification boundary:** Positive group turnover residuals, including a within-group excess over between-group residual correlation, do not identify strategic coordination because local shared hidden factors can reproduce the signature.
- **Empirical competing-explanation evidence:** Original repeated-choice data under fixed 24-session heldout splits show online own-history adaptation reduces joint U,D logloss from ~1.98098 to ~1.93512 (lambda 20, within current section) and shrinks positive residual cross-moment from +0.05124 to ~+0.01820. Reusing history across section changes is less predictive at equal lambda; adding a fixed gamma=.30 group shock now worsens joint prediction. These results favor investigating short-horizon actor adaptation as a competing predictor, but **do not isolate causal learning, friction, individual heterogeneity, strategic dynamics or social welfare**. The candidate models/hyperparameter sets were devised on this same source, and the exact committed GitHub SHA/remote CI run evidence is incomplete.
- Original causal questions remain unresolved: microeconomic friction has not been identified; macro-level social costs have not been inferred from experimental forecasts.

## 2. Structural deficiencies
1. **Target substitution:** Losses, residuals and switch counts replaced macro welfare, persistence and intervention response as center of inquiry.
2. **No justified aggregation operator:** The mapping from individual conditional choice probability to endogenous network capacity, congestion feedback, social cost and dynamic resource reallocation is not established or validated.
3. **Dynamic horizon mismatch:** 24 original experiment sessions × 39 rounds per section are insufficient by themselves to establish decades-long institutional lock-in or urban hysteresis. One needs a separately justified dynamic physical/economic model and a transfer domain.
4. **Nonunique psychology:** A predictor with history is not evidence for a psychological learning law. Unobserved actor traits, regime changes and hidden group shocks remain rivals.
5. **Novelty overlap:** Indifference bands, inertial user equilibrium, boundedly rational day-to-day dynamics, dynamic-choice identification, information heterogeneity and welfare paradoxes already have substantial literatures. Claiming novelty from a two-link threshold example would be inaccurate.
6. **Resource economics missing:** Information cost, decision complexity, habit, switching cost and real resource cost cannot be silently identified with one calibrated lambda. The conditions under which individual welfare changes translate to aggregate externalities are unspecified.
7. **Evidence governance:** Local original-data results vs GitHub published source vs actual CI run; prior model modifications not fully frozen prospectively. Do not promote exploratory bootstrap intervals to a preregistered causal claim.

## 3. Revised RITHM program (same 2.10, changed priority)
The primary question is: **Which minimal micro-level frictions and adaptation clocks produce discontinuous, persistent or sign-reversing macro welfare and policy responses, and under what observation/intervention conditions can the responsible mechanism be inferred?**

- **Theory spine / macro outcome first:** Define actors i, actions a_i,t, private/observed information I_i,t, cognitive resource effort e_i,t, physical congestion state q_t, institution or platform policy p_t, switching cost κ_i,t, social objective W_T=Σ_t β^t[network travel cost + real resource costs + congestion externalities]. Clarify benefit/cost units. Specify dynamic updates for both human choice and physical network response.
- **Mechanism court:** Historical 2.10 P0–P2 models test equivalence and credible discriminators *for a particular welfare or persistence proposition*, not as an infinite standalone search for new predictive regressors.
- **Counterfactual court:** Predict duration of inefficiency, multiplicity of invariant distributions/stable sets, welfare reversal under more information, delayed policy afterlife. Require a proof/counterexample plus independent simulation and a causal identification argument or explicit partial identification set.
- **Empirical bridge:** The Noussair–Qiao 24-session data can constrain specific switching kernels and near-term predictions. They do **not** directly establish long-run urban-level welfare. Transfer requires structural assumptions and robustness bounds, not rhetorical extrapolation.
- **Novelty gate:** Defeat a well-chosen strongest precedent model on distinct theory predictions, empirical calibration and policy counterfactuals. Otherwise label as replication, application or didactic example.

## 4. First exact Ruby *reference example* — not novelty
Two nonatomic parallel routes, share x on A; c_A(x)=x, c_B(x)=1-x, no exogenous bias at final evaluation. Myopic switch only if current cost saving strictly exceeds κ∈[0,1]. Both groups present:
  x stationary iff (1−κ)/2 ≤ x ≤ (1+κ)/2.
Mean social travel cost W(x)=x²+(1−x)²=1/2+2(x−1/2)².
Thus stationary excess travel cost lies in [0,κ²/2]. It is *not* an estimate from original human data. With κ=1/5, static stationary x=2/5 and x=3/5 cost 13/25=0.52 versus optimum 1/2=0.50, excess 1/50.
A path-dependent pulse: start x=1/2, κ=1/5, limited daily adjusting fraction ρ=1/8, a temporary A-cost bias h=2/5 causes x→7/16, then h returns to 0. Since 7/16 lies in the no-bias stationary band [2/5,3/5], the departure persists even as the external parameter returns. No-pulse path remains x=1/2. Long-run (stationary) travel cost is 65/128 vs 1/2, persistent excess **1/128**. This demonstrates the logical micro→macro connection but is a standard indifference-band phenomenon; no original result or physical congestion dynamics beyond the simple two-link model are claimed. Real transition switching costs are excluded from stationary travel cost (zero switches at stationarity); transitory resource costs would need inclusion in a finite-horizon welfare comparison.
Local Ruby 3.3.8: 5 tests, 22 assertions, zero failures, all Rational.

[Source](p3/friction_welfare.rb) · [tests](p3/test_friction_welfare.rb). Workflow `.github/workflows/rithm29-ruby-research.yml` includes read-only source-free tests; no bot commit steps, no confirmed remote run PASS.

## 5. Specific strong precedent / novelty firewall
- Srinivasan & Mahmassani (1999), dynamic congestion and information effects, calibrated indifference bands: https://doi.org/10.3141/1676-06
- Cantillo, Ortúzar & Williams (2007), inertia and serially correlated unobservables: https://doi.org/10.1287/trsc.1060.0178
- Abbring (2010), dynamic discrete-choice identification: https://doi.org/10.1146/annurev.economics.102308.124349
- Modeling route choice inertia in network equilibrium with heterogeneous prevailing choice sets: https://www.sciencedirect.com/science/article/pii/S0968090X1500220X
- Guo (2026), heterogeneous information, day-to-day congestion and policy: https://www.sciencedirect.com/science/article/pii/S136655452600102X
- Handel (2013), removing individual inertia can worsen aggregate welfare via adverse selection: https://doi.org/10.1257/aer.103.7.2643
- Tump et al. (2024), linking individual cognition, collective decisions and reciprocal social feedback: https://doi.org/10.1177/17456916231186964

## 6. Decision / next experiment
Keep RITHM-2.10 OPEN; do NOT open 2.11 as a cosmetic response. Reframe the current 2.10 title as the **identification subprogram**, not the full RITHM statement of aims. Next: formalize a small endogenous information-and-network feedback game with explicit welfare and adaptation timescale; prove a threshold or policy-welfare reversal conditional on bounded cognition/switching friction; immediately compare with strongest papers. Then determine whether original 24-session switching data can restrict the effect size without illicit extrapolation. If no genuinely discriminating theorem or credible welfare outcome is produced, retain the old predictive work as a methods/empirical appendix rather than calling it an ambitious new theory.
