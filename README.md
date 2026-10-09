# RITHM

**RITHM — Route-choice Inertia and Traffic Hysteresis Modeling** is the dedicated execution and provenance repository for the RITHM research program.

## Repository role

This repository is the canonical code/execution surface for reproducible RITHM computational world-contact. Scientific constitutions, authority decisions, and long-form reasoning remain separately preserved in the Research OS / Notion record; this repository stores executable compilers, workflows, frozen parameter receipts, and machine-verifiable artifacts.

## Governance

- `main` is the canonical branch. RITHM does not depend on unrelated development repositories.
- Scientific parameters are frozen prospectively before target exposure.
- Execution failure is not scientific defeat or support.
- Infrastructure changes may not silently alter a frozen scientific estimand.
- Partial-cell results are not aggregated when the constitution requires complete-set admission.
- Generated summaries and derived receipts do not replace primary source bytes.
- External runner timeout is a resource boundary, not evidence of traffic gridlock.

## Current active lineage

`RITHM-ORIGIN-S02.14-E3 — Teleport-Absent TNEG Execution Preseal, Frame-Complete Burden Replay, Runtime-Censoring Separation & Regularization-Sensitivity Closure`

E3 inherits S02.14 and the successful E2 frame-complete T120 result. It changes only SUMO `time-to-teleport` from `120` to `-1` for the scientific TNEG comparison. Exact frame, treatment cohorts, model bytes, simulated horizon, burden functional, and frozen decision threshold remain unchanged.

## Frozen external authorities

- MoST scenario commit: `b29b2f65f1096a9c69a601ec62a724815cb4a43f`
- SUMO: `1.14.0`, source commit `58abfe34cdaf638c696ebd4d3660934f061ad94a`
- Eligible source-derived frame: `N=45,822`
- Nested explicit cohorts: `0 / 13,746 / 32,075 / 45,822`
- S02.14 eligible-frame SHA-256: `e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293`
- Cohort SHA-256:
  - p000: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
  - p030: `1b9fba0675825b770afe24159fc39c4ba12b6f78fa05e432d77ad8e7556f83f5`
  - p070: `f4855d4965e9d7268f97a2d0c90f11b4d9632cd6cd8d22ff2d15ed4804cd9270`
  - p100: `21d0db278e7c39d9403520b10ab471470a03c30cd908c587677a1d5249f8f634`

## Historical repository boundary

Earlier S02.13/S02.14 exploratory workflows were mistakenly executed in `WhoSia/ChatGPT-Web-HWPX-MCP`, an unrelated MCP-development repository. That dependency is retired. Historical commit/run identifiers remain provenance references only; no new RITHM writes belong there.

## S02.16 execution recovery and isolated runner prototype (2026-10-09)

Three of four cells (p030, p070, p100) have full native runner receipts and independently verified eligible-frame IDs, hashes and numerical burden arithmetic. The remaining p000 reached `Simulation ended at time: 50400.00`; raw TripInfo SHA-256 `0f5b52d154d51e0269e3bb08670da5b71077703c6fefcb3cf9a515f9602af65c` and whole XML parse passed. An independent read-only reconstruction matched 45,822 eligible IDs (39,068 eligible XML tripinfos, 6,754 absent, 21,768 unfinished/invalid arrivals mapped to horizon). Parent PID 420832 was intentionally stopped; its zombie child PID 420845 had Linux wait status 0. Native p000 `status.json`, `exitcode.txt`, and `framecomplete.tsv` have not been created; kernel child exit evidence does not authorize fabricating these files.

**Science gate:** 4/4 native scientific admission and curvature score remain on HOLD. Never resume PID 420832, relaunch a finished cell, open the score, or overwrite frozen results as a side effect of engineering tests.

`experimental/resilient_parallel.py` is a **disposable test-only** POSIX job coordinator. It has detached workers, bounded launches, exclusive dispatcher flock and conservative LAUNCHING/RUNNING/UNKNOWN no-retry semantics. `experimental/tests/test_runner.py` has seven disposable local tests (manager returns, worker completion, nonzero failure, worker SIGKILL, fail-closed unresolved state, unsafe job name, no duplicate restarts). These tests are **not** proof of power-loss durability, exact native SUMO checkpoint resume, nor owner-approved elastic scaling. Run with `python3 -m unittest discover -s experimental/tests -v`. The prototype is not part of a scientific runner and must not be deployed onto Sean's live host.

Source and test ZIP backups are kept in Google Drive folder `RITHM_Code_Backups_2026` (v1 original and v2 with tests); historical frozen original scripts remain unchanged. Commits are to be authored by WhoSia, never `github-actions[bot]`; CI should only execute read-only tests and upload artifacts, not author commits.