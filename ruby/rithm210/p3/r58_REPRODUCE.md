# R58 reproduction · exact cohort and legal filtration

## Source-free checks

The enclosed archive contains **no source human participant rows, group identifiers or private 24-session ZIP**. Requires Python 3.11+ and numpy==2.2.6 (Python 3.13/local numpy 2.3.5 was also tested separately). Do not install numpy in the unrelated RITHM legacy jobs.

```bash
python -m pip install -r requirements-r58.txt
python -m unittest discover -s . -p 'test_r58*.py' -v
```

These tests verify the mechanics of the original Appendix A/B payoff-belief rules, source hash rejection, time filtration, SSM exact convolution, q posterior, full six-seat flow normalization and symbolic welfare-score algebra. The tests alone **do not verify source-derived numbers**.

## Authorized source reconstruction

```bash
python run_r58.py /path/to/author-approved-source.zip --bootstrap 4000 --lapse 0.02 --output recalculated.json
```

The original `rererequestforpermissiontouseexperimentalroutechoi.zip` must have SHA-256 `e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953`. The program verifies this **before** reading actor rows; only a cohort-aggregate JSON may be published. A full-source rerun requires permissions to the original ZIP, which is not enclosed here. Recomputed scores may have insignificant platform-level floating-point differences (FFT / BLAS), so compare with numeric tolerance rather than byte equality.

### Primary settings

- original author sample: 24 sessions, treatments No/Partial/Full, groups 144, periods 1..40, exactly 5,616 group transitions and 33,696 scored individual next choices
- heldout split: 24 nonoverlapping whole-session exclusions, exact same fold target and session-equal aggregation for all eight models
- EWA fitted response λ separately for each treatment on 23 training sessions with bound [0,3]; author Appendix A.2 uninformed belief tables encoded from received profit
- fixed-q SSM5 and fixed-individual-type SSM1–9 following Appendix B Table 4, with **extra evaluator-imposed** 2% lapse to make a proper finite actor logscore; run epsilon=0.005 and 0.05 separately to reproduce provided sensitivity JSON
- participant-legal private-route baseline does **not** access prior full occupancy, unlike R57 diagnostic oracle; no heldout period-t choice enters any predictor at t
- cost-forecast polynomial is explicitly **not** a causal welfare comparison; true resource cost coefficient κ remains externally unidentified

### Outputs

`r58_results.json`, `r58_lapse_sensitivity.json` include only whole-cohort and No/Partial/Full aggregates; `RITHM_R58_20261121.md` records source and causal limits.
