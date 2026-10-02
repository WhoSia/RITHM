# RITHM-ORIGIN-S02.16 — Preseal

**Stage:** Stable-Compute Full-Horizon TNEG Burden Materialization, Canonical-T120 Reuse, Four-Cell Curvature Re-estimation, Teleport-Mediated Sensitivity Decomposition & Regularization-Dependence Adjudication

## Scientific target
Determine whether the canonical E2 T120 rerouting-penetration curvature survives full-horizon `time-to-teleport=-1`.

## Canonical baseline reused
- B120(0) = 6744.900342630178
- B120(.30) = 6552.030105626119
- B120(.70) = 6531.009995198813
- B120(1) = 6528.603536510846
- C120 = 0.028238190134892482
- epsilon = 0.005

## Fresh execution set
Only four fresh TNEG cells:
- p000
- p030
- p070
- p100

No T120 rerun. No threshold sweep. No checkpoint/resume. No reuse of E3/E4 partials.

## Frozen authority
- SUMO 1.14.0 exact E3 binary SHA-256: `75c5556e52dd48953a7b6b75c3bb508df89a1e5690f7e32c962eac4587da864b`
- MoST commit: `b29b2f65f1096a9c69a601ec62a724815cb4a43f`
- eligible frame: 45,822 rows, SHA-256 `e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293`
- begin/end/step: 14400 / 50400 / 0.25
- seed: 42
- max-depart-delay: 900
- rerouting period/pre-period: 300/300
- global rerouting probability: 0
- `time-to-teleport=-1`

## Complete-set firewall
No B_NEG, R_B_NEG, C_B_NEG, delta-B, delta-R or delta-C is computed until all four fresh cells:
1. exit 0;
2. custody complete TripInfo;
3. materialize exactly 45,822 frame-complete burden rows;
4. seal `scientific_cell_receipt_valid=true`.

Any execution/custody failure => HOLD-EXECUTION, not scientific evidence.

## Decision grammar
`R_NEG(p)=B_NEG(p)/B_NEG(0)-1`

`C_NEG=[R_NEG(1)-R_NEG(.70)]-[R_NEG(.30)-R_NEG(0)]`

- C_NEG > +0.005 => PASS-TNEG-CURVATURE / PASS-TELEPORT-ROBUST
- C_NEG < -0.005 => DEFEAT-TNEG-CURVATURE / REGULARIZATION-SENSITIVE
- otherwise => UNRESOLVED-TNEG-CURVATURE / REGULARIZATION-SENSITIVE

## Execution-surface rules
Forbidden:
- personal-laptop long compute;
- GitHub-hosted 6h full-horizon cells;
- checkpoint/resume or segmented scientific continuation.

Required:
- stable Linux x86_64 host;
- uninterrupted walltime beyond the slowest cell;
- exact E3 binary compatibility;
- independent artifact custody.

## Materialized executor
- `scripts/s02_16_cell.py`
- `scripts/s02_16_score.py`
- `scripts/s02_16_cloud_run.sh`

The executor can run the four independent SUMO cells in parallel and opens the target only after 4/4 valid receipts. Optional evidence upload uses a GitHub release bundle after completion.

**State:** `PRESEALED / EXECUTOR-MATERIALIZED / STABLE-COMPUTE-PROVISIONING-PENDING`
