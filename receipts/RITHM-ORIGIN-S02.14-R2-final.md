# RITHM-ORIGIN-S02.14-R2 — Final Resource-Authority Receipt

**Stage:** `RITHM-ORIGIN-S02.14-R2 — TNEG Compute-Resource Authority, Deterministic Checkpoint/Resume Feasibility, Walltime-Censoring Localization & Frozen-Parameter Re-Execution Authorization Court`

**Final verdict:** `PASS-RESOURCE-AUTHORITY / DEFEAT-DETERMINISTIC-CHECKPOINT-RESUME / AUTHORIZE-LONGER-UNINTERRUPTED-REEXECUTION-ONLY`

## Inherited state

- Parent E3: `HOLD-EXECUTION / TNEG-NONMATERIALIZED`
- E3 TNEG target remained unread: `B_NEG=null / R_B_NEG=null / C_B_NEG=null`
- E2 remains valid only under canonical `time-to-teleport=120`
- No teleport-robustness claim is licensed.

## Exact SUMO v1.14.0 checkpoint authority

The exact v1.14.0 documentation states that save/load exists, but:
- RNG state is not saved unless `--save-state.rng` is enabled;
- transportables require explicit preservation;
- undeployed vehicles require the original route inputs;
- internal lane-change state is not saved;
- internal car-follow state is not fully saved for all models.

MoST uses lateral-resolution, lane-changing behavior and stochastic vehicle/car-follow parameters, so checkpoint exactness was prospectively treated as an empirical and constitutional question rather than assumed from API availability.

## Adversarial checkpoint-resume probe

GitHub Actions run: `35411046590`  
Workflow head: `abcb8c0bf26441ef6f07ec6eabb9025715d7348d`  
Artifact: `s02-14-r2-checkpoint-audit` / ID `10574432934` / SHA-256 `7cf51a0949871c2abed5a7d63ebbcb23f0a80cc48545e25563d4134e81277741`

The probe used only the already-observed **T120 p100 control**, never the TNEG target. It used exact SUMO 1.14.0, exact MoST commit, exact S02.14 p100 cohort, RNG-state saving, transportable-state saving, rail-constraint saving, and save-state precision 16.

Diagnostic:
- uninterrupted terminal state at simulation time `16200`
- resume from checkpoint `15000` to the same terminal state
- resume from checkpoint `15600` to the same terminal state

Results:
- uninterrupted terminal-state SHA-256: `41e95b723b34b33629fa61d18f13feb7c1354b301020290f7fc11a9390e278af`
- resume-15000 SHA-256: `f77df42c6b3668d1461cf2540c08ba3bd7610cac4cd18dbf8ea7c4b9bcf7258d`
- resume-15600 SHA-256: `34544de40b052b5cc84f8f73aa50d1e3761ab03b0cf3c6ee0ab281e6f9eb317b`
- checkpoint 15000: raw unequal; ordered XML-record unequal; `1088` record mismatches; continuous record count `1096`, resumed `1085`
- checkpoint 15600: raw unequal; ordered XML-record unequal; `1083` record mismatches; continuous record count `1096`, resumed `1095`
- differences already appear in saved/restored RNG bookkeeping and propagate through the terminal state.

Therefore:
`DEFEAT-DETERMINISTIC-CHECKPOINT-RESUME / CHECKPOINT-EXACT-AUTHORITY=FALSE / TNEG-CHECKPOINT-STITCHING=PROHIBITED`

No `B_NEG`, `R_B_NEG`, or `C_B_NEG` was computed or read.

## Walltime localization

E3's four cells each exhausted the presealed 345-minute process budget with exit `124`. This is a shared external execution boundary, not a traffic observable and not gridlock evidence.

GitHub-hosted runners impose a six-hour per-job execution ceiling, so ordinary or larger GitHub-hosted runners do not remove the relevant walltime boundary. A longer uninterrupted execution surface is therefore the admissible infrastructure candidate.

## Frozen-parameter re-execution authority

R2 **authorizes a fresh entire four-cell TNEG re-execution only as uninterrupted processes** on a compute surface that can exceed the hosted six-hour ceiling.

Authorization conditions:

1. Use the exact E3 SUMO 1.14.0 Linux x86_64 binary whenever possible: SHA-256 `75c5556e52dd48953a7b6b75c3bb508df89a1e5690f7e32c962eac4587da864b`.
2. Exact MoST commit: `b29b2f65f1096a9c69a601ec62a724815cb4a43f`.
3. Exact eligible-frame SHA-256: `e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293`.
4. Exact nested cohort SHA-256 values from S02.14.
5. Scientific configuration unchanged from E3: `time-to-teleport=-1`, begin/end `14400/50400`, step `0.25`, seed `42`, `max-depart-delay=900`, global rerouting probability `0`, explicit nested cohorts, rerouting period/pre-period `300/300`, output-prefix-aware TripInfo custody, write-unfinished enabled.
6. **No `--load-state`, checkpoint stitching, state migration, or segmented scientific execution.**
7. No cell mean or curvature score until all four fresh cells complete and materialize the full 45,822-row frame-complete receipts.
8. Any runtime/custody failure remains `HOLD-EXECUTION`; it is not scientific evidence.
9. Compute-surface migration is infrastructure-only and must be separately receipted before target exposure.
10. No E3 partial TripInfo or cell output may be mixed into the new four-cell score.

## Final seal

`PASS-RESOURCE-AUTHORITY / DEFEAT-DETERMINISTIC-CHECKPOINT-RESUME / CHECKPOINT-STITCHING=PROHIBITED / WALLTIME-CENSORING=EXTERNAL-INFRASTRUCTURE / TIMEOUT≠GRIDLOCK-EVIDENCE / AUTHORIZE-FRESH-FOUR-CELL-UNINTERRUPTED-TNEG-REEXECUTION / EXACT-E3-BINARY-PREFERRED / SCIENTIFIC-PARAMETERS-FROZEN / COMPLETE-SET-ONLY / TARGET-UNREAD-IN-R2 / NO-POST-REVEAL-RETUNING`
