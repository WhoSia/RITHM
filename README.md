# RITHM — Route-choice Inertia and Traffic Hysteresis Modeling

**Research status: RITHM-2.6 OPEN · P20 source publication-delay robustness (real 2025 sensor exposure / unmeasured provider delay / welfare HOLD).**

How do human route-choice persistence, information clocks, congestion feedback and social welfare interact? Human causal state dependence and interventions remain **unidentified**. Separate observational urban sensor dynamics from actual group travel-time welfare.

## P21 — Publication-bound policy switching and nonuniform operational admissibility (2026-10-13)

**Real exposed 2025 original data, reproduced on the current 38-shard/P20 common source clock:** 18,420,707 reported five-minute source rows, 178 links, **2,121,699 strictly matched ten-minute future bins** (P20 canonical source-replayed cohort, NOT 2,123,227 user-pasted different-mask result). Days1–14 seasonal training; days15–21 validation-only link-vs-calendar arbitration; days22–28 evaluation. For assumed delay 0/10/20/30/40/50/60min, fixed .75 mixture source MAE **34.249/44.955/53.927/61.715/68.998/75.721/82.417**, validation-only per-link switched MAE **34.249/45.957/52.653/55.887/58.128/60.165/61.849** vehicles/10minutes. At lag2 policy **loses**, and at lag4 March source gate deteriorates +24.68 against fixed mix. Month bootstrap of 30min average mix-minus-gate contrast includes zero; no uniform temporal guarantee. Delay lag7 source gate improves aggregate and yet loses to calendar in May and November. **All provider-publication delays remain UNMEASURED SCENARIOS.** A certified upper bound D would license a conservative pair lag j(D), but no actual provider certificate or independent real receipt audit exists. Real welfare, independent sensor calibration and human advice causality remain HOLD.

[Full P21 scientific court](docs/rithm26_p21_publication_bound_arbitration_20261013.md) · [replay](tools/traffic_sources/p21_trainval_switch.py) · [release-time authority](tools/traffic_sources/p21_latency_authority.py) · [offline tests](tests/test_p21_latency_authority.py). Full local 25-test original-source research package SHA256 `7bab6187ae460e856c4b540259cc186712ea2d2d855627bc73e242c955de816a`. P20 & earlier results preserved. **RITHM-2.6 OPEN.**

## P20 — Observation-delay robust source forecasting, not yet deployable (2026-10-13)

Re-read **all 38 SHA-matched UTF8 original owner shards** and **18,420,707** 2025 five-minute SOURCE observations. Hypothesized post-interval public release delay Δ changes the latest legal ten-minute count from lag1 (Δ=0) to lag2 (5–10 min), lag4 (30 min), lag5 (40 min) and lag7 (60 min). All source delay scenarios compared on the **same 2,121,699** real future source ten-minute target bins, stricter than the 2,136,298 original P19 mask. Source MAE for fixed posthoc .75 mixer: **34.249** (Δ=0), **44.955** (5–10 min), **61.715** (30 min), **68.998** (40 min), **82.417** (60 min), vs train-only calendar **66.649**. Thus aggregate crossover in this retrospective source cohort between Δ=30 and40, but at 30 min the mixer wins only **4/12 months**, with month-bootstrap improvement interval across zero. **Actual per-bin provider publish delay has NOT been measured**; official file publication is historical/nonperiodic and cannot certify real-time deployment. Bayes information dominance applies to optimized predictors, not individual fixed lag rules. Independent 5-min calibrated physical source and human policy welfare remain **UNIDENTIFIED**. [P20 research court](docs/rithm26_p20_observation_delay_authority_welfare_20261013.md) · [actual source-derived result](docs/data/rithm26_p20_latency_source_2025.json) · [portable replay](tools/traffic_sources/p20_latency_court.py) · [conditional bounds and 13 offline tests](tests/test_p20_latency_authority.py). Earlier P1–P19 history and P19 negative freedom comparison preserved.

## P19 — Train-only vs fixed mixing of conserved 10-minute source flow (2026-10-13)

**New exploratory adversarial test after the already-present P18 source results:** on the same **2,136,298 actual 2025 future 10min source bins**, P18 previous-ten-minute persistence MAE **34.9002** vehicles/10min, simple fixed 75:25 mix with preceding-two-bin average **34.5601**, and link-wise train-only five-point mixing **34.5178**. The fixed mix was introduced as a **post-result simplicity challenge**, not a prospective prespecified competitor. Extra link fitting over fixed mix is only **0.0424** vehicles/10min, 12-month resampling band for the *relative* additional effect **−0.143% to +0.315%** includes zero. No independent physical source/human group welfare success. [Scientific P19 court](docs/rithm26_p19_train_only_phase_mixer_20261013.md) · [actual engine](tools/traffic_sources/p19_train_only_phase_mixer.py) · [compact data](docs/data/rithm26_p19_mixer_real_2025.json). Prior P13–P18 findings below remain authoritative, not overwritten.

## Current evidence

- **P18 source-clock-legal 10-minute forecasting, after P17 phase algebra:** [real 2025 12-month empirical source court](docs/rithm26_p18_tenminute_phase_invariant_forecast_20261012.md), [portable executable](tools/traffic_sources/p18_tenmin_source_forecast.py), [compact source scores](docs/data/rithm26_p18_tenmin_full_2025.json). 38/38 source shard SHA passes; 18,420,707 five-minute readings, 361 observed calendar dates; 9,196,409 complete ten-minute source pairs. On strictly matched 2,136,298 ten-minute future target cells, previous **complete ten-minute total** MAE **34.900** source vehicles/10min, versus **39.270** for 2 × last observed five-minute source count and **67.649** for train-only seasonal calendar. Twelve of twelve exposed-source monthly windows favor pair aggregation. This is source-count forecasting, **NOT independent physical truth, route-choice habit, or driver social welfare**.
- **P13 complementary 12-month sensor nowcasting audit:** [full-year annual results and identifiability notes](docs/rithm26_p18_tenminute_phase_invariant_forecast_20261012.md) include 4,287,316 paired future-bin source readings: speed 2.686 km/h MAE last5 versus 6.531 seasonal; volume 21.993 versus 36.966; 75:25 fixed blend worsens speed (3.018) but marginally improves count (21.882). Prior P13-R3/P14 already had more extensive weekwise tests; this is another transparent retrospective mask, **not** untouched confirmation.

- **2025 Seoul 5-minute sensor source:** 18,420,707 previously verified shard observations, 178 links, four network blackout days. Strong observed March–April odd/even 5-minute *volume* phase alternation; the underlying physical cause is unresolved.
- **P15:** [operator nonidentification, common network phase, negative controls and 32 retrospective candidate days](docs/rithm26_p15_observation_operator_phase_20261012.md).
- **P16:** [integer-constrained phase-reallocation budget and independent-reference partial-identification criteria](docs/rithm26_p16_integer_operator_bounds_20261012.md). On 2025-04-18 source measurements, a hypothetical near-flat within-10-minute latent count would require 10.51% of observed section-passage counts to be reassigned between successive 5-minute bins, **not** a measured error rate.
- **P17:** [phase-robust 10-minute conserved proxy bounds, 2025 six-day source audit, exact Braess/dispersion mathematical tests and CPU-local marginal updates](docs/rithm26_p17_phase_robust_mesoscopic_externalities_20261012.md). On 2025-04-18 a deliberately hypothetical P16-scale redistribution budget permits a fixed-source-speed **proxy** interval −3.64% to +3.91%; not an observed sensor error, driver's actual time or a policy benefit. Static 40-car Braess model separate from Seoul source; [six-day compact result](docs/data/rithm26_p17_source_phase_sensitivity_20261012.json).
- **Earlier source courts:** [P14 network aliasing](docs/rithm26_p14_network_coherent_aliasing_20261012.md), [P13-R3 independent replication](docs/rithm26_p13_r3_clock_parity_independent_replication_20261012.md), [2017 choice/welfare reconstruction](docs/rithm23_origin_to_welfare_bridge.md).

## Repository navigation

```text
src/rithm/legacy/         Historical human traffic games (previous root Python)
tools/traffic_sources/    Source validators, forward prediction, phase diagnostics
tests/                   Offline mathematical/source-contract regressions
data/                    Small licensed derivative inputs and source provenance
docs/                    Scientific reports, data/ compact results, reproducibility
R/                       Independent R-language baseline check
.github/workflows/        Python and R checks
```

**Start here:** [Reproducibility & source custody](docs/REPRODUCIBILITY.md) · [Full original research-history README, preserved verbatim](docs/PROJECT_HISTORY_20261012.md).

## Limits

The 2025 traffic counts and reported speeds are *measurements*, not directly the physical latent five-minute passage process, independent detector outputs, individual trips or welfare. The 10-minute-source-conserving null space admits distinct latent worlds. Retrospectively chosen thresholds and exposed repeated sessions cannot be described as untouched prospective confirmation.

The 38 original source shards stay in the user's [RITHM Drive data collection](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30), **not in GitHub**. Prior CP949 full files were deleted by the data owner after sharding; only extant shard bytes can be rehashed.
