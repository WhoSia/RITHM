# RITHM-2.10 R66-T7 — Source-free Moment-Welfare Lab

This folder contains **13 narrowly scoped Python research modules**, **13 paired test files**, plus a mathematical report, 23-entry missing-paper registry and reproducible CI. It is isolated from the user's parallel low-cost Windows Work session.

## Run locally

```bash
python -m pip install scipy
python -m unittest discover -s . -p 'test_r66_t7_*.py' -v
```

All tests are deterministic; 52 tests passed locally on 2026-11-21. Binary masks are at most 6 for tested exact sharp moment LP; the general distribution helper deliberately rejects n>12 for combinatorial safety.

## A principled evidence ladder

1. Mathematical identity: Möbius expansion and exact low-order moment criterion.
2. Exact sharp synthetic identification: rational primal + dual certificates for n=3..6.
3. Synthetic parity and recovery counterexamples: NOT human behavioral evidence.
4. Original-paper aggregate tail counts (from R66-T6): poor support for human third-order estimates.
5. No causal external information treatment claim and no unapproved original human-source redistribution.

## Integration order

`distribution.py` → `moments.py`/`mobius.py` → `sufficiency.py` → `parity.py`/`recovery.py`/`triple.py` → `bounds.py`/`dual.py` → `transfer.py`/`resource_fee.py`/`policy.py` → `empirical_contract.py`.

All files use prefix `r66_t7_` to avoid collisions with separate Work. The private original author ZIP is excluded from this repository and all shipped artifacts.

Use the R66-T7 research report for complete assumptions and hypotheses; do not treat the sharp LP interval as a confidence interval or a 24-session bootstrap result.
