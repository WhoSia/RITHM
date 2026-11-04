# RITHM-2.10 P3: Micro-friction to observed group welfare
2026-11-04. Research status: exact identities plus exploratory original-human-data analysis; novelty and causal transport remain unverified.

## 1. Exact nonlinear dynamics: not claimed novel
Two parallel routes, route A fraction x, costs cA=x and cB=1-x, switching threshold kappa and synchronous adjusting fraction rho. Interior stationary states form [(1-kappa)/2,(1+kappa)/2], and maximum stationary excess social travel cost is kappa^2/2. There is an exact locally attracting two-cycle when kappa < rho/(2-rho): x_low=(1-rho)/(2-rho), x_high=1/(2-rho), two-step contraction (1-rho)^2 and each-period excess rho^2/[2(2-rho)^2]. At rho=1/8, kappa=0 the cycle is 7/15 <-> 8/15, excess 1/450. Compare kappa=1/5: same no-policy history at x=1/2 and same response to temporary signal h=2/5 leads to permanent x=7/16 and excess 1/128, versus subsequent two-cycle with excess 1/450 in kappa=0 world. Gap is 161/28800. This is weak equivalence along a particular pre-policy path, not full distributions. Existing hysteresis and day-to-day adaptation literature precedes it. Source: p3/adaptation_cycle.rb, p3/policy_welfare_equivalence.rb and unit tests.

## 2. Recover actual group welfare law from original experiment
Source: author-approved Noussair-Qiao original ZIP preserved in Drive, https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view . Extracted CSV SHA256 d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb. Eligible 24 sessions, 5,616 6-person group-periods, 33,696 participant-period observations (treatments 1-3, exclude sessions 2 and 101, periods 1-39).
A route chosen cost = n (A users). B route chosen cost = 2*(6-n). Thus group cost C(n)=n*n+2*(6-n)^2=24+3*(n-4)^2; unique social congestion optimum n=4, C=24, excess L(n)=3*(n-4)^2. All 5,616 raw group cost sums equal the formula and each participant profit equals Value-Cost. Next occupancy NumAnext equals realized NumA in the next period for all 5,616 transitions including 39->40. Exact values are group-size-six experimental congestion cost, NOT urban-scale welfare estimates.
Recorded excess mean by treatment and epoch:
No early 3.231250, middle 3.032895, late 3.100000;
Partial early 3.200000, middle 3.115132, late 2.525000;
Full early 4.112500, middle 2.871711, late 2.093750.
The original source paper itself reports full-information short-run disadvantage and long-run advantage; RITHM cannot claim novelty for this established empirical finding.

## 3. Bias-versus-variance welfare identity
Across observed groups/periods within each treatment epoch, E[L(n)] = 3*((E[n]-4)^2+Var(n)). Full early has E[n]=3.9875, squared-mean-bias contribution 0.00046875, dispersion contribution 4.11203125, total 4.11250000. Full late E[n]=4.00625, bias 0.0001171875, dispersion 2.0936328125, total 2.09375000. Cost reduction 2.01875 is nearly entirely a dispersion reduction 2.0183984375; bias contribution 0.0003515625.
20,000 resamples of 24 whole sessions with original group weights, seed 20261104: Full dispersion decline 95% exploratory percentile [1.3623958,2.6721741], Full total decline [1.3604651,2.6750], Full-versus-No decline contrast 1.8875 [1.0102,2.76346]. An EQUAL-session-weighted within-session contrast is a different estimand: 2.03333 [1.1625,2.93125]. Dispersion is pooled across individuals, groups, sessions and periods; it is not proof of coordination or a particular causal learning mechanism.

## 4. Exact joint-turnover covariance contribution
For current occupancy n, upward switches U and downward D, next n'=n+U-D. Expected next excess cost equals 3*[(n+EU-ED-4)^2+Var(U)+Var(D)-2Cov(U,D)]. Conditional on equal means and marginal variances, positive covariance reduces future congestion-cost variance, because simultaneous opposite-direction switches cancel in the net occupancy. Constructed binary-turnover couplings at n=4, EU=ED=1/2, each variance1/4: fully positive cov1/4 -> expected excess0; independent cov0 ->1.5; maximally negative cov-1/4 ->3. Thus positive joint residual association is NOT itself evidence of macro inefficiency. This is algebraic, not a novel theorem. Rational Ruby: p3/experimental_welfare.rb and test_experimental_welfare.rb.

## 5. Does improved micro forecasting improve downstream welfare forecasting?
Sixfold session holdout, 5,616 groups. Train-only own-route/own-cost/informed/treatment Markov base; within heldout actor own previous current-section switches used strictly before period t for online history with prior strengths20 or80. Convolve all six actor probabilities into full predicted next occupancy; map occupancies sharing same cost into a probability distribution over welfare categories.
Model | welfare-category logloss | squared error expected cost | mean predicted excess | mean observed excess
baseline: 1.00408711 | 18.07549273 | 3.31780047 | 2.99519231
online20: 1.00216262 | 18.31503316 | 3.59763388 | 2.99519231
online80: 1.00176468 | 18.05059677 | 3.42212221 | 2.99519231
Paired weighted 24-session bootstrap 20,000 resamples seed20261104, online minus baseline:
online20 welfare logloss -0.00192449, CI [-0.00924513,+0.00402548], 9/24 sessions improve;
online80 welfare logloss -0.00232243, CI [-0.00489103,-0.00018843], 15/24 improve;
online20 expected-cost MSE +0.23954043, CI [+0.01527354,+0.46165076], only 4/24 improve;
online80 MSE -0.02489597, CI [-0.10066294,+0.04552036], 12/24 improve.
Earlier online20 strongly improved JOINT UP/DOWN logloss, but fails to improve welfare expected-value MSE. Different estimands and scoring rules must not be conflated. All models/hyperparameters and welfare target analysis are exploratory on one heavily studied source; bootstrap intervals are not preregistered evidence or policy causal effects.
Source files: p3/original_welfare_audit.rb, p3/welfare_variance_bootstrap.rb, p3/welfare_probability.rb, p3/welfare_cross_validation.rb, p3/welfare_bootstrap.rb, their Minitest files. Independent local Ruby 3.3.8 original-source executions and separate rational checks performed. Exact current GitHub SHA original-data replay and confirmed remote GitHub Actions run/job logs remain HOLD. Original participant rows never uploaded to GitHub.

## Next research priority
Stop endless accuracy sweeps. Investigate what creates the dispersion change: identify within-period between-group dispersion, between-session heterogeneity, and within-group temporal fluctuations separately. Link a mechanism of individual information/friction to the downstream distribution of n, not merely its conditional mean. Compare against Noussair-Qiao's small-sample behavioral model, route-choice indifference-band and informational Braess/traffic stability work before seeking novel policy results. This is a six-person group-welfare empirical bridge; city/large-system transfer needs a distinct validated structural model.

Strong precedent sources:
Noussair/Qiao 2025 https://doi.org/10.1287/mnsc.2023.00056
Srinivasan/Mahmassani 1999 https://doi.org/10.3141/1676-06
Route-control stability/hysteresis 2015 https://doi.org/10.1016/j.trb.2015.03.012
Guo 2026 https://doi.org/10.1016/j.tre.2026.104762
Informational Braess https://doi.org/10.1287/opre.2017.1712

## Follow-up P3-R4: variance is principally within fixed six-person groups over time
The raw original CSV has stable group membership across all three sections for 48 groups. A nested law of total variance applies to each treatment×epoch because every group has exactly 10 observations in early or late windows (19 in middle): Var(n) = E_g Var_t(n|g) + Var_g E_t(n|g).

For Full information, EARLY observed group excess cost 4.112500 = 0.00046875 (squared grand-mean bias) + **3.90125000 (within-group time volatility)** + 0.21078125 (between-stable-group mean variance). LATE 2.093750 = 0.0001171875 (grand-mean bias) + **1.93187500 (within-group time volatility)** + 0.1617578125 (between-group mean variance). Of the descriptive early-to-late cost reduction 2.018750, **1.969375 (97.55%)** comes from within-stable-group temporal variability decreasing, 0.0490234375 from between-group variation, and 0.0003515625 from mean bias. This is a mathematically exact, original-source-checked decomposition of a 6-person experimental welfare outcome, NOT proof that information caused stabilization or a novel general traffic law.

[Ruby hierarchical variance audit](p3/welfare_temporal_decomposition.rb) · [synthetic tests](p3/test_welfare_temporal_decomposition.rb). Independently re-evaluated locally in Ruby 3.3.8. Full detailed record lives in [Drive P3 original](https://docs.google.com/document/d/1J1m5CiwALDaRqQG790sQLx27CJ5G-X3xhkIHdRZzX7k/edit). The next falsifying question is which dynamic information/learning process *predicts the within-group variability component*, not merely a group's average occupancy.
