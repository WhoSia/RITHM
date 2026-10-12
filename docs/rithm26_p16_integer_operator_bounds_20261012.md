# RITHM-2.6 P16 — Integer-Constrained Observation-Operator Inversion & Minimum Conserved Reallocation

**2026-10-12 · source original 2025 Seoul six-day audit and exact integer partial-identification witness. RITHM-2.6 OPEN.**

**Relation:** [P15 original evidence](rithm26_p15_observation_operator_phase_20261012.md) already established observed 10-minute source phase alternation, full-year 38-shard integrity, cross-route synchrony, 32 retrospective alarm dates and unresolved physical cause. P16 does **not** newly claim origin discovery, sensor malfunction or human behavior causal effect. [P16 original source-derived compact results](data/rithm26_p16_integer_operator_budget_20261012.json).

## Mathematical distinction: integer conservation is stronger than real-valued flattening

Let observed 5-minute nonnegative integer counts be `(y_even, y_odd)`, `T=y_even+y_odd`. Under a **hypothetical** exactly conserved 10-minute count and integer latent physical counts `(q_even,q_odd)` satisfying `q_even+q_odd=T`, suppose a rival measurement-allocation model insists latent physical flow is as flat as integer arithmetic permits, `|q_even-q_odd| <= 1`.

Then **the least possible cross-bin reassignment** is precisely

`m_min(y_even,y_odd)=floor(abs(y_odd-y_even)/2)`.

Proof: the only near-flat integer pair is `(floor(T/2),ceil(T/2))` or its reverse. Source-to-latent correction has zero sum, and moving one counted passage between bins reduces the signed difference by two; the nearer orientation requires `floor(|y_odd-y_even|/2)` moves. If T is odd, exact continuous flattening `(T/2,T/2)` violates integer traffic, unlike the earlier P15 continuous witness. This is *elementary integer arithmetic*, not a new universal theorem. It gives a **conditional model burden**, not a lower bound on every possible sensor error mechanism.

## New actual-source six-day falsification budget

| Date (2025) | Matched link × 10min pairs | Original section-passage counts | Hypothetical minimal count reassignments | Share |
|---|---:|---:|---:|---:|
| Feb 12 | 25,632 | 12,106,016 | 215,731 | 1.782% |
| Mar 23 | 25,596 | 9,285,542 | 789,180 | 8.499% |
| Apr 16 | 25,209 | 11,035,175 | 973,384 | 8.821% |
| **Apr 18** | **25,384** | **11,126,802** | **1,169,133** | **10.507%** |
| Apr 19 | 25,624 | 10,713,400 | 1,101,039 | 10.277% |
| Apr 21 | 25,632 | 13,281,989 | 229,771 | 1.730% |

Read source CSV rows from 2025 H1 parts 005,009,011,012; select only original days, retain observed nonmissing q pairs and source ROUTE_ID + LINK_ID identity; never interpolate count or treat absent values as zeros. The total is **section-passage occurrences** across links, not unique motorists or an inferred fraction of sensor corruption. The P16 analysis is source-EXPOSED and retrospectively selected dates, not a blind holdout.

Independent 2025 Apr 18 direction-group aggregation of odd-even 5minute difference: 16/16 groups have the earlier 5minute bin higher in clock hours 08,09,10; 16/16 groups have the later 5minute bin higher at 11 and 12. Agrees with P15 network sign inversion, still single same-publisher reporting system. This could be genuine common physical flow + processing jointly; not exclusive H1/H2/H3.

## Which new measurement would actually distinguish worlds?

Suppose **the same real, spatially aligned five-minute physical counts** from a source with independently verified sensing/processing provenance can be measured as `Z_even,Z_odd` with a defensible maximum error `eps`, and optionally the publisher source counts have a defensible unknown-alias per-half bound `b` under pair conservation. A sharp *integer* `Q_even` identified interval is the intersection of:

`[0,T] ∩ [y_even-b,y_even+b] ∩ [ceil(Z_even-eps), floor(Z_even+eps)] ∩ [ceil(T-Z_odd-eps), floor(T-Z_odd+eps)]`.

Exclude the `b` interval if `b` unknown; exclude reference intervals if no independently calibrated five-minute reference. The range is sharp under these specified local assumptions: every integer Q in it yields complementary Q_odd and admissible zero-sum source error and reference residuals. Empty range means the **combined assumptions** are inconsistent, not which sensor is wrong.

**Synthetic witness:** observed (315,557), T=872. Unbounded source alias leaves Q_even 0..872. A genuinely independent (hypothetical) reference `Z=(436,436)` with each max error 4 reduces range to [432,440], rejecting the source-faithful latent world (315,557). Conversely an assumed source alias bound `b=100` excludes near-flat physical counts because the minimal required integer correction is 121. Neither reference nor bound has been observed/validated for Seoul in P16.

**Original-source constraints:** SPD/OCC columns share publisher lineage and cannot be promoted to independent co-located vehicle counts. One independent 10minute sum still leaves the 5minute null-space unresolved; independent 5minute measurements with proved geometry and bounded error could separate alternative allocations.

## Executable audit and test status

- Exact pure source-independent bounds: [`src/rithm/observation.py`](../src/rithm/observation.py).
- Publisher-source original day scanner: [`tools/traffic_sources/phase_budget_audit.py`](../tools/traffic_sources/phase_budget_audit.py). Run **after** verifying all source shards against their two manifests using the P15 source integrity gate. The earlier P16 local source scan read targeted 2025 actual parts and generated the compact output; no deleted CP949 original rehash is claimed.
- Six source-independent original contract tests with integer exhaustive 0..12 counts, absent-reference and inconsistent-reference guards: [`tests/test_observation_operator_bounds.py`](../tests/test_observation_operator_bounds.py). Local standalone copy was run **6/6 PASS**; GitHub Actions were not run for this research step, and this repository commit is marked `[skip ci]`.
- Repo cleanup landed in [structural refactor](https://github.com/WhoSia/RITHM/commit/247c1a4edc530303fe9a11c02e28f3beb866b355), moving 9 old root scripts without deletion to `src/rithm/legacy` and archiving the original full README to `docs/PROJECT_HISTORY_20261012.md`.

**P16 verdict:** EXACT INTEGER BOUND PASS; HISTORICAL SOURCE SIX-DATE RECONSTRUCTION PASS; COMMON 16-DIRECTION SIGN INVERSION RECONFIRMED; SOURCE ERROR MAGNITUDE NOT ESTIMATED; CROSS-PROVENANCE CALIBRATED REFERENCE ABSENT; CAUSAL SENSOR/PHYSICAL MECHANISM HOLD; TRUE DRIVER GROUP WELFARE HOLD. **RITHM-2.6 OPEN.**
