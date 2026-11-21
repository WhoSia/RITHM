# RITHM R62 — Independent reproduction, exact source boundary

## Private original input (never stored in GitHub or reproducer)

Use the original, author-approved `rererequestforpermissiontouseexperimentalroutechoi.zip` available separately in the user's restricted Research OS. SHA256 must be exactly:

`e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953`

Do not publish CSV rows, participant identifiers, session- or group-level trajectories, or Value tape. The cohort selection and source provenance are enforced by the imported `r59_prior_exposure.py`, `r60_cross_segment.py`, `r61_adaptive_prior.py`, `r54_original_batch_clock.py`.

## Environment

Python 3.11 or newer, NumPy >=2.2 and <2.3. All `r62_*` source and source-free tests plus five earlier prebuilt dependency modules are included in the ZIP. From the extracted directory:

```bash
python -m pip install -r requirements-r62.txt
python -m unittest discover -s . -p 'test_r62_*.py' -v
```

All **36** source-free unit tests should pass even when the restricted human ZIP is absent. These prove arithmetic/invariants/tested implementation structure only, **not** replay against the real-source original.

## Real-data replay (separately authorized original ZIP)

```bash
python r62_run.py APPROVED_PRIVATE_ZIP r62_one_step_results.json
python r62_legal_run.py APPROVED_PRIVATE_ZIP r62_legal_one_step_results.json
python r62_rollout_run.py APPROVED_PRIVATE_ZIP r62_rollout_observed.json observed 20261121
python r62_rollout_run.py APPROVED_PRIVATE_ZIP r62_rollout_fair.json fair 20261121
python r62_rollout_run.py APPROVED_PRIVATE_ZIP r62_rollout_seed2.json observed 20261123
python r62_legal_rollout_run.py APPROVED_PRIVATE_ZIP r62_legal_rollout_observed.json observed 20261121
python r62_legal_rollout_run.py APPROVED_PRIVATE_ZIP r62_legal_rollout_fair.json fair 20261121
python r62_legal_rollout_run.py APPROVED_PRIVATE_ZIP r62_legal_rollout_seed2.json observed 20261123
```

**Do not conflate**: the main original-source 24-session actor decision evaluation is different from the 96 group-sections' autonomous 40-round cost forecasts. Source Value(t) for legal feedback is exposed only *after* the generated choice at t; treatment-aware uninformed actors do not receive analyst-visible previous complete group occupancy.

The result JSONs are **only aggregated** and contain no original participant, session, group or trajectory rows. For exact byte reproduction ensure the Python/NumPy versions, command seeds, source SHA, and JSON dump settings match; float rounding can vary across versions even when numerical results agree. Archived file SHA256s protect the publicly delivered implementation, not the owner-authorized external human source.

## Verification layers

1. Source-free synthetic mathematics and adversarial timing/filtration tests.
2. Original-human source SHA and precise 24-session cohort audit.
3. Matched outer-session heldout one-step likelihood and MSE checks.
4. 64-repeat autonomous simulation with coupled random streams, alternate start and seed.
5. Repository blob SHA verification, read-only GitHub Actions, Drive byte-custody verification and Notion scientific verdict.

No source-free GitHub CI should ever claim to have run real-human source replay.
