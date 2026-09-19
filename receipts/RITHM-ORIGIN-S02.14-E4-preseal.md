# RITHM-ORIGIN-S02.14-E4 — Pre-Execution Seal

**Stage:** `RITHM-ORIGIN-S02.14-E4 — Exact-E3-Binary Long-Walltime Uninterrupted TNEG Four-Cell Re-Execution, Complete-Set Burden Materialization & Teleport-Regularization Closure Court`

**Status:** `PASS-E4-PRESEAL / EXECUTION-NOT-YET-LAUNCHED`

## Authorized execution surface

- repository: `WhoSia/RITHM`
- branch: `main` only
- workflow: `.github/workflows/s02-14-e4.yml`
- workflow commit: `7cde09d971e464f54db9dec59affaf56e7ed4b16`
- runner: repository-level GitHub self-hosted runner
- required labels: `self-hosted, linux, x64, rithm-e4`
- host environment: dedicated Ubuntu 22.04 x86_64 WSL distro
- matrix execution: `p000 → p030 → p070 → p100`, `max-parallel: 1`
- per-cell job ceiling: `900 minutes`
- each scientific cell is one uninterrupted SUMO process from begin to end
- checkpoint/save-load stitching and segmented scientific execution are prohibited

## Exact frozen authority

- exact E3 SUMO runtime source: run `35307642604`, artifact `10532337458`
- exact SUMO binary SHA-256: `75c5556e52dd48953a7b6b75c3bb508df89a1e5690f7e32c962eac4587da864b`
- exact MoST commit: `b29b2f65f1096a9c69a601ec62a724815cb4a43f`
- exact eligible-frame SHA-256: `e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293`
- exact nested cohort hashes inherited from S02.14
- `time-to-teleport=-1`
- begin/end `14400/50400`
- step `0.25`
- seed `42`
- `max-depart-delay=900`
- rerouting probability `0`
- explicit nested cohorts
- rerouting period/pre-period `300/300`
- canonical output prefix `most.`
- TripInfo write-unfinished `true`
- frame-complete burden definition and `epsilon=0.005` unchanged

## Firewall

No E3 partial TripInfo/output may enter E4 scoring. No cell mean or TNEG curvature may be computed until all four fresh E4 cells have exited successfully and each has a valid 45,822-row frame-complete receipt.

If any cell times out, is interrupted, loses power/sleep custody, fails runtime verification, or otherwise does not materialize, E4 returns only:

`HOLD-EXECUTION / TNEG-NONMATERIALIZED / B_NEG=null / R_B_NEG=null / C_B_NEG=null`

Execution failure is not traffic/gridlock evidence.

## Launch condition

Do not dispatch E4 until:
1. the self-hosted runner is online with label `rithm-e4`;
2. Ubuntu `22.04` and x86_64 are verified;
3. required E3 runtime libraries resolve without `not found`;
4. the machine will remain awake and powered for the run;
5. no registration token or credential has been written to GitHub or Notion.

## Preseal

`PASS-E4-PRESEAL / WSL-UBUNTU22.04-SELF-HOSTED / EXACT-E3-BINARY-REQUIRED / FOUR-FRESH-CELLS / MAX-PARALLEL=1 / PER-CELL-CEILING=900MIN / CHECKPOINTS=PROHIBITED / COMPLETE-SET-ONLY / TARGET=CLOSED / RUNNER-REGISTRATION-PENDING`
