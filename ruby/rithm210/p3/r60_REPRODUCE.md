# RITHM-2.10 R60 — source-free bundle, original data excluded

This bundle is an audit of a historical human dataset; it does not include individual human choices, participant IDs, original session rosters, Value tapes or source CSV/ZIP. The original-author-approved source remains in the owner's private Drive. The public aggregate JSON was computed locally with that private source and an exact SHA-256 prerequisite; GitHub Actions verifies **source-free contracts**, not an original-data replay.

## Install / test

Requires Python 3.11+ standard library, no third-party dependencies.

```bash
python -m unittest discover -s . -p 'test_r60_*.py' -v
python r60_latent_rival.py
```

Source-free tests use entirely synthetic 24-session fixtures. `r60_results.json` and `r60_identity_placebo.json` are anonymous whole-population **aggregates only**, not raw experimental observations. `RITHM_2_10_ACHIEVEMENTS_AUDIT_20261121.md` reviews the 2.10 program's entire research arc in connection to `RITHM_R60_20261121.md`.

## Recompute original human source locally (only with owner-approved archive)

The original authorized ZIP has SHA256:

`e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953`

No code path permits using another blob for an original-human result without explicitly changing the hash contract. Run only on an access-controlled computer; output to an existing separate folder:

```bash
python r60_run.py /private/path/to/author-approved-original.zip /private/path/to/aggregate-output-dir
```

The operator writes exactly `r60_results.json`, `r60_identity_placebo.json` (no rows/identifiers) and emits their SHA256. R60 has 24 heldout sessions, 576 prior→subsequent actor links, 22,464 next-actor decisions and 3,744 joint group-transition targets.

**Predetermined parameters:** Beta(.5,.5) smoothing of train-only conditional hazard; fixed exposure shrink 20 pseudo-observations, 5/80 as sensitivity; whole-session nonparametric descriptive resampling (2,000), same-group label permutation (2,000), deterministic seeds. The time strata 2–6, 7–20, 21–40 and alternatives were explored on the same data; not externally prespecified verification.

The original author experiment employs simultaneous six-person revision each period. Do not mistakenly apply the single-person-per-step synthetic interventions directly to its actual group costs.
