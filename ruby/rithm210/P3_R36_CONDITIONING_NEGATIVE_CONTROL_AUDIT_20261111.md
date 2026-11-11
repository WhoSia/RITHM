# RITHM-2.10 P3-R36 — Conditioning sensitivity, predecision negative controls, and their noninformative degeneration

**2026-11-11 · Empirical original-source exploratory audit; CAUSAL VALUE / REWARD-LEARNING HOLD.**

## Problem

R35 found an ostensibly randomized travel value correlated with both future switching and an already decided current switch when conditioning on session×section×group×period×current route×information status. That unexpectedly significant predecision placebo is neither grounds to assert randomization misconduct nor grounds to claim a causal reward-learning effect. R36 asks whether that result is robust to different *preexisting* conditioning sets and whether some conditional placebos become tautological.

The author manuscript says Value is independently sampled per actor-period, uniform on [6,16], hidden before route selection, while the payoff is Value minus route congestion cost. The actual implementation randomization logs were not in the inspected R analysis archive. The data were privately read and SHA256 checked: `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. The original main 24-session Partial cohort excludes sessions 2 and 101; t=2..39 allows both switch_t and switch_(t+1).

## Source-replayed conditioning specifications

Cells always condition on the same session, section, six-person group, period. The table adds the following route/information strata and only retains cells with ≥2 people. Estimates use the within-cell covariance-ratio slope; p values from 999 conditionally shuffled value assignments (exploratory; non-familywise-corrected).

| Additional conditioning | Eligible actor-periods | Value vs next switch slope (p) | Value vs *predecision* switch slope (p) |
|---|---:|---:|---:|
| Current route + informed flag (R35 analogous) | 8,394 | −0.007416 (0.002) | −0.006473 (0.006) |
| **Previous route** + informed flag | 8,396 | −0.010367 (0.001) | −0.000569 (0.786) |
| Both previous and current route + informed flag | 5,906 | −0.007197 (0.009) | **0.000000 (1.000, tautology)** |
| Informed flag only | 10,944 | −0.009182 (0.001) | −0.003081 (0.077) |
| Current route only | 10,493 | −0.007548 (0.001) | −0.003110 (0.081) |

The R35 next-switch slope −0.007554 used t=1..39 and 8,619 eligible actors; this **new** comparison uses t=2..39, so the matching R35-type subset has 8,394 actors and −0.007416. Do not compare the two estimates as if they refer to the same observations.

## P1 validity insight: zero may be uninformative

Fixing both the *previous* and *current* individual route makes switch_t = 1{Y_t != Y_(t−1)} **a deterministic constant in every stratum**. There is no within-stratum variation left, so its estimated predecision slope is zero by algebra regardless of the quality of Value randomization. That is NOT a negative-control PASS. In the stricter common-eligible 5,906 actor-periods shared by all three route-conditioning designs, even the current-route-only and previous-route-only strata cannot reveal a predecision switch difference: they coincide in their effective retained cell partition. Their next-switch slope is −0.007197 (999 permutations p=.003 on this common cohort), but the predecision placebo slope is mechanically 0 in all three. This is an identifiability/overconditioning failure, not an independent reproducibility confirmation.

The two key conditioning specifications with variation—the R35-like current-route stratum and the prior-route-only stratum—disagree about the predecision placebo association. The eligible samples and conditional null hypotheses differ; the result does not prove that Value randomization was valid or invalid. Both types of results were selected after R35; their p values are exploratory.

## Methodological controls and source comparison

Lipsitch, Tchetgen Tchetgen & Cohen (2010), *Negative Controls: A Tool for Detecting Confounding and Bias in Observational Studies*, Epidemiology 21(3) 383–388, DOI 10.1097/EDE.0b013e3181d61eeb, discusses negative-control outcomes and the need for comparable bias structures. Shi, Miao & Tchetgen Tchetgen (2020), *A Selective Review of Negative Control Methods in Epidemiology*, Curr Epidemiol Rep 7:190–202, DOI 10.1007/s40471-020-00243-4, elaborates identifying assumptions. These are external sources checked through current public web and are **not yet marked as held in the private Drive corpus**. The takeaway is narrow: a negative control that is **deterministically fixed by the conditioning set** cannot independently diagnose bias. Merely adding controls without interrogating remaining outcome variation is a methodological failure.

The existing original author experiment already compares EWA-lite, SSM5, and SSM1–9. RITHM's distinct provisional task is the legally disclosed-information forecast, negative-control diagnostics and direct six-person joint score; not 'discovering reward learning' or 'inventing asynchronous revision'.

## Reproducibility and no-promotion status

- Private original source passes exact SHA; no row-level data are published.
- New independent local source-free test suite **5/5 PASS**; source data conditional sensitivity replay completed.
- Distinct complete source record vs submitted GitHub exact checkout CI should be verified separately; no remote Actions PASS claim.
- The high nominal p values after previous-route conditioning or forced conditioning are NOT proof of a causal reward effect.
- R35 original failure and R36 sensitivity results must both be preserved; **CAUSAL HOLD** is maintained.

## Next / R37

1. Inspect original experimental software or randomizer assignment logs if available, not the analysis bootstrap seeds.
2. Predefine a negative-control outcome with **nonzero within-stratum variance** and structurally comparable nuisance paths, and use cross-study/heldout validation rather than further post hoc significance hunting on the same 24 sessions.
3. Independently reproduce the authors' EWA-lite, SSM5 and SSM1–9 benchmarks under the exact same information filtration and session-fold contracts.
4. Continue independent clean GitHub repository test/CI audit, avoid `github-actions[bot]` authorship, record source and code checksums in Notion and Drive.
