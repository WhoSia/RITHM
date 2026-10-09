# RITHM-2.3 — Past experienced route cost and the limits of learning inference

**Status:** exploratory mechanism test, not a paper freeze or causal discovery. Stage 2.3 remains OPEN.

**Original human evidence:** Wijayaratna et al. (2017), [PLOS ONE paper](https://doi.org/10.1371/journal.pone.0184191), [S2 original 2017 workbook](https://doi.org/10.1371/journal.pone.0184191.s002), CC BY 4.0. Original 144 people ×40 observations in 12 groups, 6 shared-incident laboratory sessions. The source-derived route choices and individual experienced costs are in [data/rithm23_wijayaratna2017_routes.csv](../data/rithm23_wijayaratna2017_routes.csv) and [data/rithm23_wijayaratna2017_costs_packed.csv](../data/rithm23_wijayaratna2017_costs_packed.csv); [decoding instructions](../data/README_RITHM23_2017.md).

**Exact source-custody validation:** 24/24 source group-stage cost totals and independent FNV character fingerprints match the S2 author appendix; 5,760 costs. Of 1,346 occupied group×round×route cells, 3 contain internally inconsistent participant recorded costs (author-source values; do not overwrite). Run `python rithm23_cost_contract.py data/rithm23_wijayaratna2017_routes.csv data/rithm23_wijayaratna2017_costs_packed.csv`.

**Primary test:** No-information treatment only, 2,736 individual next-route forecasts and 228 group-round forecasts; six **entire lab sessions** are held out one at a time. Only personally **experienced** path cost through t−1 enters the next-period predictor. No unchosen road costs or currently hidden incident are presented as a participant's observed information.

| Smoothed categorical rival | Individual logloss ↓ | Independently combined 3-route occupancy logscore ↓ |
|---|---:|---:|
| Previous route + coarse period | .952583 | 2.993890 |
| Previous route + period + switch history | **.938176** | 3.018461 |
| Period + previous own experienced cost | .955739 | 2.984541 |
| Period + history + previous experienced cost | .944384 | **3.004360** |
| Period + history + last-four own average cost | .943727 | 3.021751 |

Compared with history alone, adding previous actual cost **worsens** average personal logloss by .006207 (only 1/6 sessions improves), while the fitted independent group occupancy logscore improves by .014101 (6/6; exploratory six-session t5 95% interval +.006678 to +.021524). This is a score-layer discrepancy, not robust evidence of a cognitive reward-learning mechanism or welfare improvement. Regularization/pseudocount and family-search sensitivity are retained.

**Continuous regression rival:** Converged multinomial L2=.001 logistic with route/time/history: personal logloss .949441 and group logscore 2.974968. Adding last experienced cost: .949935 / 2.970914. Adding last cost plus recent average: .949526 / 2.969038. Personal signal again fails to establish independent benefit; aggregate changes are small with 6-session intervals crossing zero.

**Observed switch-rate gradient, not causal:** Within the same previous route, high versus low previously experienced costs associate with more switching for route 1 (52.50% vs 41.98%) and route 3 (51.60% vs 42.62%). Costs are endogenous to own road and group traffic; this does not identify reward-based adjustment or distinguish it from remembered congestion.

**Separate interacting groups negative control:** Person-time-demeaned across-group residual alignment in NoInfo: route-only +1.368; route+time +.861; history+time +.940; history+cost+time +.946. The latter remains exploratory positive under 3,000 whole-series circular shifts (two-sided p≈.0033). Observed personal reward history does **not** explain this residual common time alignment. Common room/timing/learning and probability calibration remain alternatives.

**Preserves:** RITHM-2.2 independent aggregation welfare FAIL; current 2.3 causal coordination and welfare benefits HOLD; no new RITHM-2.4, manuscript freeze, GitHub Actions automation or experimental branch. Full three-script exploratory reproducibility archive maintained separately alongside the 2.3 Notion record.
