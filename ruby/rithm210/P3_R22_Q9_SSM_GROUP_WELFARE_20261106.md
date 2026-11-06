# RITHM-2.10 P3-R22 — Full q≤9 SSM Source Replay and Welfare Metrics

**2026-11-06 KST — exploratory real historical-source analysis.** Exact Korean evidence and metadata record: [dated Google Drive report](https://drive.google.com/file/d/1eF07J8uEDFR3tFvfR3jDLfuCXYyHfzET/view?usp=drivesdk), 6,950 bytes; original and authenticated Drive re-download SHA256 `4b092870f704aa2a6453cb6d7772ea8511bcf3b0f04b670a25fa809d70569f70` verified. No human participant rows on GitHub.

## Original-source invariant and mathematical acceleration

Author-approved CSV `data_task_all_switch_230705.csv` exact SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. **24 sessions, three treatments, 5,760 six-person group-period observations, 1,920/treatment.** Each actor prediction strictly uses only prior periods of the same section; predict all six route probabilities before updating any one actor with the current group's chosen actions and payoffs. Conditioned on personal forecasts, independent Bernoulli composition is an **assumption**.

The R19 uninformed SSM's independent samples-with-replacement compare `sum X_k` to `sum Y_k` with fair ties. Since the two draw sequences are independent, `sum(X_k-Y_k)` has the EXACT same law. The same q-step convolution of the empirical pair-difference pool yields all q=1..9 predictions. [Rational exact code](p3/r22_ssm_exact_series.rb), [legacy R19 parity test](p3/test_r22_ssm_exact_series.rb): local Ruby 4 runs, **106 assertions**, 0 failures. This is computational equivalence, **not a novel mathematical theorem**.

For fast q9 source replay use double precision distribution FFT; exact sampling law but **not exact arithmetic**. [Float Ruby q-series](p3/r22_ssm_float_series.rb), [parity tests](p3/test_r22_ssm_float_series.rb) local 2 runs/**1,442 assertions** /0 failures. [Python NumPy FFT source driver](p3/r22_ssm_q9_fft_cv.py), [random integer-pool test](p3/test_r22_ssm_q9_fft_cv.py): local 500 random payoff pools × 9 q = **4,500 exact-enumeration comparisons** within tolerance 1e-10. Local completed complete-source FFT in ~6.6s, maximum RSS ~139MB. Legacy Ruby rational source replay at full 24 sessions did not finish within configured time; tested exact series against original R19 q calculations and validated one source session's q3/q9 aggregate with the FFT. **No claim of an exact-rational 24-session replay.**

## Complete historical outcomes, pooled equal group weights

Group occupancy mean logloss (lower better). SSM persistent actor-specific q weights use uniform initial q prior, online Bayes updating, and lapse 0.02; uniform q is a separate equal-q average. Neither reconstructs the full fitted author SSM.

| Treatment | Own-route frequency | Persistent q≤3 | Persistent q≤9 | Uniform q≤3 | Uniform q≤9 |
|---|---:|---:|---:|---:|---:|
| No information | **1.452795** | 1.643932 | 1.651073 | 1.656577 | 1.699659 |
| Partial | **1.434414** | 1.622345 | 1.635053 | 1.641006 | 1.703142 |
| Full | **1.442832** | 1.910648 | 1.939014 | 1.960184 | 2.081315 |

All q≤9 occupancy logloss scores were higher than q≤3 and own-frequency in this particular SSM configuration. **That does not reject all SSM versions, memory size theory, or original authors' parameter fit.**

### Nonlinear welfare metric changes the direction of some comparisons

Full information group-occupancy Brier and expected one-period group cost (not teacher-forcing-free 40-period forecast):

| Model | Occupancy logloss | Occupancy Brier | Absolute expected-cost error | Signed predicted−actual cost |
|---|---:|---:|---:|---:|
| Own frequency | **1.442832** | **0.718944** | **3.010507** | +0.647486 |
| Persistent q≤3 | 1.910648 | 0.766378 | 4.292247 | +2.305141 |
| Persistent q≤9 | 1.939014 | 0.771853 | **4.165037** | +2.047161 |
| Uniform q≤3 | 1.960184 | 0.784085 | 4.608812 | +2.715157 |
| Uniform q≤9 | 2.081315 | 0.818633 | 4.608657 | +2.646146 |

**The q9 persistent model has worse group logloss/Brier yet lower expected-cost absolute error than q3.** This makes clear that fidelity of the full occupancy distribution and welfare under quadratic group congestion are not interchangeable forecast objectives. Signed cost bias is not itself a lower-is-better proper score.

## Paired 24-session uncertainty (exploratory, not confirmatory)

20,000 whole-session bootstrap draws, equal weight per session, distinct from equal-weight per group table above; same 24 sessions have been used repeatedly to design competing models.

- No-information persistent q9−own-frequency logloss **+0.186030**, exploratory 95% **[+0.114507,+0.262322]**, q9 better in 4/24 sessions.
- Partial-information persistent q9−own-frequency **+0.170409**, 95% **[+0.110514,+0.231806]**, better in 3/24.
- Full-information persistent q9−own-frequency **+0.526866**, 95% **[+0.411871,+0.657963]**, better in 0/24.
- Full-information persistent q9−q3 **+0.037300**, 95% **[+0.014958,+0.059261]**, q9 better in 7/24.

[Source-free 24-session paired bootstrap](p3/r22_q9_session_contrast.rb) and [tests](p3/test_r22_q9_session_contrast.rb) enforce consistent sessions/group counts, no pseudoreplication, reproducible seeds. Read-only GitHub CI now includes Ruby exact, float and session-pair tests. Python/NumPy must be installed separately to run the FFT source driver; never put raw human source data in public CI.

## Decisions

R22 provides a **full q9 conditional negative benchmark** and a computationally efficient, exact-law but floating-point method; it does not establish author EWA/SSM failure, psychological mechanism or novel welfare identification. Next R23 must test meaningful changes in the personal choice information set/forgetting/inertia and stronger fitted original EWA or SSM against own-frequency, online Markov and autonomous finite-horizon welfare. Do not overstate retrospective heldout CV as independent pre-registered validation. New human recruitment remains out of scope.

**Verification HOLD:** remote GitHub Actions PASS and independent byte-identical final GitHub-HEAD integrated replay were not established in this turn. Local Ruby exact/float parity and Python numeric source aggregate replay completed.
