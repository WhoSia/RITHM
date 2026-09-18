# RITHM-ORIGIN-S02.14-E3 — Final Execution Receipt

**Verdict:** `HOLD-EXECUTION / TNEG-NONMATERIALIZED`

GitHub Actions run: `35307642604`  
Workflow head: `486eda6637fe2014963c2a88b54f427cfea50f93`  
Final artifact: `s02-14-e3-final` / ID `10543475103` / SHA-256 `1cfb2faa5415079948991c65127e636ffef807df8961f531c6dc1f41619aefd0`

## Frozen admission result

The exact SUMO 1.14.0 GDAL build and exact MoST-source frame/cohort reconstruction passed. All four fresh TNEG cells (`p=0,.30,.70,1.00`) exhausted the prospectively frozen 345-minute process budget with exit code `124`. Each produced a custodied prefixed TripInfo file, but none completed simulation successfully and none materialized the required 45,822-row frame-complete burden receipt.

Therefore:

- `all_four_fresh_e3_cells_valid=false`
- `target_aggregation_permitted=false`
- `scientific_target_observed=false`
- `B_NEG=null`
- `R_B_NEG=null`
- `C_B_NEG=null`
- no TNEG curvature verdict was scored
- timeout/runtime exhaustion is **not** gridlock evidence
- E2 remains valid only under canonical `time-to-teleport=120`
- no teleport-robustness claim is licensed
- no post-reveal scientific retuning occurred

## Cell provenance

- p000 artifact `10542410827`; exit `124`; TripInfo SHA-256 `641d9a6430d82e61f998b6b4e680ae8aae9eb59b679f1b9954f7437159c06cb0`
- p030 artifact `10542349679`; exit `124`; TripInfo SHA-256 `5553bae3f2539b002d5eb574c27acd1d60d4c638c4766cf166eca10159cc9bd7`
- p070 artifact `10542605579`; exit `124`; TripInfo SHA-256 `c266d660d676a288f3373b851614582198f34ab034b83e0d2e6ae61e47126bb5`
- p100 artifact `10542349674`; exit `124`; TripInfo SHA-256 `ef796d12d77a4b3e4ee043374754dc18104a4d50c038b68f568ad4c2c3ea3fd6`
- exact runtime artifact `10532337458`
- frozen-frame artifact `10532331823`

## Final seal

`HOLD-EXECUTION / TNEG-NONMATERIALIZED / ALL-FOUR-CELLS-EXIT-124 / TARGET-AGGREGATION-PROHIBITED / SCIENTIFIC-TARGET-OBSERVED=FALSE / TIMEOUT≠GRIDLOCK-EVIDENCE / E2-VALID-CANONICAL-T120-ONLY / NO-TELEPORT-ROBUSTNESS-CLAIM / NO-POST-REVEAL-RETUNING`
