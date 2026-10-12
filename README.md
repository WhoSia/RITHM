# RITHM — Route-choice Inertia and Traffic Hysteresis Modeling

**Research status: RITHM-2.6 OPEN · P17 phase-robust mesoscopic externalities (real source proxy / synthetic traffic game).**

How do human route-choice persistence, information clocks, congestion feedback and social welfare interact? Human causal state dependence and interventions remain **unidentified**. Separate observational urban sensor dynamics from actual group travel-time welfare.

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
