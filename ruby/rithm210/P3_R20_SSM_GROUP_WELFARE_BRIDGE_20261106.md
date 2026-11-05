# RITHM-2.10 P3-R20 — Six-Actor SSM-to-Welfare Bridge

2026-11-06 KST. **Original human source reanalysis; exploratory predictive comparison, not a causal or autonomous 40-round welfare finding.** Full original Markdown report in [Drive](https://drive.google.com/file/d/1N7b7IhldapzqTWHUC_qvp2S4IIPQaOll/view?usp=drivesdk); authenticated download exact SHA256 `585b3e8150b04815b722c8324b0124b51f396539594c952ec8ec7337410cda88` (6,289 bytes). Source ZIP and individual participants' rows are NOT committed.

## What advanced

Use the original author-approved CSV whose SHA256 is `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. From 24 experimental sessions across no/partial/full information, validate **5760 complete six-player group-period observations**, **1920 per treatment**. Reconstruct each actor's prior-only model probability and convolve six Bernoulli choices into the full seven-point next-route-occupancy distribution. Score multinomial log loss, Brier, and the one-step *expected total cost* C(n)=n²+2(6−n)². All six group forecasts are computed before period-t outcomes or payoffs update histories. This predicts current-period route occupancy from prior-period behavior, not a 40-period autonomous simulation.

Candidate models: per-actor Bayesian-smoothed own-route frequency Beta(1,1), actor-specific online two-state Markov switch-frequency Beta(1,4), existing R19 exact q SSM uniform mixture, R19 persistent actor-q posterior (lapse .02). Neither q<=3 nor its fixed lapse is asserted to be original authors' fully fitted SSM.

## Actual original-data results, q=1..3, occupancy logloss (lower better)

| Treatment | Own frequency | Online actor Markov | Persistent q SSM | Uniform q SSM |
| --- | ---: | ---: | ---: | ---: |
| No info | **1.45280** | 1.48005 | 1.64393 | 1.65658 |
| Partial | **1.43441** | 1.48299 | 1.62235 | 1.64101 |
| Full | **1.44283** | 1.47804 | 1.91065 | 1.96018 |

Full info group Brier: own frequency 0.71894, Markov **0.71705**, persistent q 0.76638, uniform q 0.78409. The Markov improvement over own-frequency in Brier does not carry over to log loss or mean absolute forecast error of group cost. For full-information group-cost expected-value MAE, own frequency 3.01051, Markov 3.06128, persistent q 4.29225, uniform q 4.60881.

Using 24 whole sessions as paired units, 20k resamples on the average session logloss, full-information persistent-q minus own-frequency mean **+0.48957** with exploratory percentile95 **[+0.37821,+0.61696]**. Repeated model development using the same data and no independently unused confirmation set remains a serious limitation.

## Second bridge: exact one-step welfare-error identity

For observed occupancy n, independent actor probability vector p, μ=Σp and v=Σp(1−p):

`C(n)−E_ind[C(N)]=6(μ−4)(n−μ)+3[(n−μ)²−v]`.

The identity separates a mean/position component from a dispersion component, but neither is a causal identification of peer coordination. For Full info with **q<=2 only** (different from q<=3 scoreboard), mean components across 1920 groups: own frequency −0.726, actor Markov −1.599, persistent q −3.785, uniform q −4.433. Dispersion components are +0.079,+0.888,+1.405,+1.505 respectively. The full cost errors are −0.647,−0.711,−2.380,−2.929. Never combine q<=2 components with q<=3 model scores as though fitted under one setting.

## Implementation and external tools

- [Bridge source](p3/r20_group_bridge.rb), [source-free tests](p3/test_r20_group_bridge.rb).
- [Paired session bootstrap](p3/r20_session_contrast.rb), [source-free tests](p3/test_r20_session_contrast.rb). Proper-score win counts include only logloss, Brier and absolute expected-cost error; **signed cost bias is deliberately excluded** following Ponytail-style minimal-diff adversarial review.
- CI read-only test workflow adds both suites, no bot-authored commits. Local Ruby3.3.8 functionally equivalent code **11 tests / 76 assertions / zero failures**; original CSV SHA-sealed q<=2 and q<=3 group-score replays succeeded. Final posted GitHub SHA itself and GitHub Actions PASS are still unverified.
- **Actual connected MCP-Hub tool calls:** `hub_discover_reviewed_skills` (code and testing), `hub_plan_public_skill_bundle` (review-only), `hub_analyze_public_unified_diff` (public synthetic diff); Ponytail v5.3.3 original `skills/ponytail/SKILL.md` read through GitHub from pinned `DietrichGebert/ponytail@7801d061...`. No Ponytail installation, autonomous agent run, private Gateway call or install approval. Its code-review practice was applied manually.

## Immediate R21 step, not an audit

Challenge the latest findings using the **actual original author SSM q up to 9, strong fitted EWA and participant-history logit** under the same information timing and independent-session evaluation; distinguish per-period group scoring from true 40-period autonomous welfare. Until those rivals are reconstructed, the narrower R20 SSM failure is a **conditional negative benchmark**, not a refutation of SSM or a publication novelty claim.
