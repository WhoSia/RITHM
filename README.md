# RITHM — Route-choice Inertia and Traffic Hysteresis Modeling

## Current canonical status (2026-10-18)

**RITHM-2.8 is the sole OPEN mainline; P1 OPEN.** Ruby is the primary game/synthesis implementation; Go is the independent verifier. The most recent source-evidence trust-root court is **2.8 P1-P12**; a narrower **P1-P18 R2 Ruby→Go dynamic dual-certificate experiment** (shared recovery, priced and delayed probe, synthetic revocation/restoration epochs) now has independent replay and CI. This does not promote P2, certify a real agency, or complete the still-local historical P1-P13–P1-P18 research series. P2 and 2.9 promotion **HOLD**, subject to explicit scientific evaluation.

- [P1-P12 scientific court](https://app.notion.com/p/3fcef561cf9281dead05e3697076f23e): independent **synthetic** client-log and provider roots; typed receipt→delivery links; Go checks role, identity, episode, chronology and HMAC. Public HMAC test keys **cannot attest real institutional identity**. `receipt_only_unconfirmed` and `synthetic_delivery_chain_only` never establish actual benefit receipt; `real_world_welfare_verified=false` always.
- [Ruby–Go Certificate Gate SUCCESS at commit `756cd8a2`](https://github.com/WhoSia/RITHM/actions/runs/39053196088), including P1-P18 R2: Ruby 7 tests/23 assertions, 8 Go independently checked upper/lower certificates, 10 adversarial mutations rejected. [Original P1-P12 gate](https://github.com/WhoSia/RITHM/actions/runs/39040575105) remains a historical synthetic-evidence verification run; neither attests reality.
- [Ruby P1-P12 emitter](ruby/rithm28/p1p12/emit.rb) · [Ruby tests](ruby/rithm28/p1p12/test.rb) · [Go independent verifier](go/rithm28/p1p12/verify.go).
- [P1-P9 independent policy certificate](ruby/rithm28/p1p9/export.rb) → [Go replay verifier](go/rithm28/p1p9/verify.go) · [mainline execution gate](scripts/rithm28-ruby-go-check.sh).

## Scientific spine: what survived, what did not

| Stage | Retained result | Non-claim / HOLD |
| --- | --- | --- |
| 2.5 / 2.5-D | Policy-dependent observation equivalence need not preserve intervention welfare; constructed short-/long-horizon reversals | Human habit learning was not causally established by the construction |
| 2.6 | Actual-human choice rival models, selection effects, external source admissibility; speed/volume measurement limits | No identified actual advice compliance, intervention-welfare effect or person-level observed benefit |
| 2.7 | Publication vs receipt vs observed action; frozen-original-data bounds; finite-memory partial-observation automata | Do not conflate guidance offered with viewed or complied guidance; no new human recruitment |
| 2.8 P0 | Queue/service and setup-friction models, group-to-person indexed welfare, temporal recovery properties | No automatic inference from aggregate service totals to individual rights |
| 2.8 P1–P12 | Receipt-age synthesis, Ruby→Go witness replay, trust-role separation, person/episode/parent linkage | Synthetic evidence integrity is not agency authority or real delivered welfare |

**Research synthesis rule:** a successful calculation means only that the stated finite model and stated observation contract satisfy the tested property. Source provenance, physical timestamps, individual exposure, actual delivery and causal welfare are separate obligations. Negative results and counterexamples must remain citable.

**Post-P1-P12 exploratory work (mostly local, not canonically promoted):** P1-P13–P1-P18 explore revocable trust, certificate reuse, endogenous paid observation, price–latency thresholds and dual winning/losing certificates. The [P1-P18 Ruby shared-capacity composition court](ruby/rithm28/p1p18/composition_court.rb) and [10-case regression](ruby/rithm28/p1p18/test_composition_court.rb), plus the [restricted deadline-prefix capacity bound](ruby/rithm28/p1p18/prefix_bound.rb) and its [282-case exhaustive Ruby test](ruby/rithm28/p1p18/test_prefix_bound.rb), are now committed; they are a synthetic counterexample, **not** a completed P2 theory or observed rights restoration. The [R2 Ruby certificate generator](ruby/rithm28/p1p18/dynamic.rb), [Go independent verifier](go/rithm28/p1p18/verify.go) and [CI gate](scripts/rithm28-p1p18-dual-revocation.sh) now verify a narrow **revocable-observation** game; see [Notion judgment](https://app.notion.com/p/3fcef561cf928111b863f1c9739702ba). Other local packages, actual typed institutional authority, general theorems and novelty review remain unintegrated/HOLD.

## Active reproducible Ruby/Go workflow

Run from repository root:

```sh
bash scripts/rithm28-ruby-go-check.sh
ruby ruby/rithm28/p1p12/test.rb
bash scripts/rithm28-p1p11-typed-evidence.sh
bash scripts/rithm28-p1p11-linked-evidence.sh
ruby ruby/rithm28/p1p18/test_composition_court.rb
ruby ruby/rithm28/p1p18/test_prefix_bound.rb
bash scripts/rithm28-p1p18-dual-revocation.sh
```

See [Ruby–Go gate workflow](.github/workflows/rithm-ruby-go.yml) for CI invocation and pinned runtime versions. The legacy Python/R gate [rithm20-ci.yml](.github/workflows/rithm20-ci.yml) still runs historical source/fixture checks; **do not remove its dependencies without replacing its reproducibility coverage**. Earlier work under `src/`, `tools/`, `tests/`, `R/`, `cpp/`, `rust/`, `js/`, `ruby/` and `go/` is not necessarily obsolete merely because it is outside today's Ruby/Go mainline.

## Historical preservation and navigation

**Full README snapshot before 2026-10-18 retirement**, including every historical P1-P1–P1-P12 and 2.6/2.7/P0 stage description: [Drive archival document](https://docs.google.com/document/d/19-g8WThlmE51Kg6ys11Fym50nItQtBiALDRNxamqk98/edit). Verified byte-for-byte text against the GitHub README blob `93448cfe0e30229d6f9876c53559a8d5d5724995`. The archived prose reflects its **as-of-stage** status; it does not override this current header.

**Five retired P28 specialist checks** (C++ exact long-run reconstruction, unexecuted Rust variant, Ruby crosscheck + person-history audits, and R session audit) are retained verbatim with each original blob SHA in [Drive code archive](https://docs.google.com/document/d/1_9rW5-XEOLtzeM7SXzC97O952Frqsi2ARGd-aQJmLfo/edit). See the [Drive retirement manifest](https://docs.google.com/document/d/16fSQrjVIEh9StUmmvqw88uja1aTri7qI7JTETTiTnYE/edit) for the five original paths, blob SHAs and exact deletion commits. These files are historical independent checks, not part of the 2.8 Ruby/Go CI mainline. To reconstruct those historical experiments, consult the Drive copies and [P28 replay protocol](docs/rithm27_p28_replay.md); do not silently claim an archived historical command still works from a fresh current checkout.

- [Research transition ledger](docs/rithm27_flowing_transition_20261013.md), [P29 finite-memory automata](docs/rithm27_p29_finite_memory_congestion_automata_20261013.md), [P27 original-source bounds](docs/rithm27_p27_source_conditional_welfare_bounds_20261013.md).
- [2.6 source and observation studies](docs/REPRODUCIBILITY.md), [2017 derivative data provenance](data/README_RITHM23_2017.md), [original P23/P24 bridging](docs/rithm23_origin_to_welfare_bridge.md).
- [Historical RITHM-2.0–2.7 README record](docs/PROJECT_HISTORY_20261012.md) and original repository history also preserve prior findings; neither is a license to reassert superseded stage labels.

## No-promotion and contribution guard

- **P2:** requires more than syntactic identifier mismatch; seek distinct composition failures involving contemporaneously valid independently authorized evidence and person-indexed outcomes.
- **2.9:** requires an independently checkable general theoretical result, rigorous overlap/novelty review and explicit source/field-validity boundaries; a large collection of successful synthetic tests is insufficient.
- **No new human recruitment or experiments.** Keep the original authorized observational datasets distinct from synthetic clocks and witnesses.
- CI automation is welcome for tests, but **no `github-actions[bot]` commit author/committer**. Check authored/committed identities after changes.
- **Drive is preservation; GitHub is runnable code; Notion is the judgment ledger.** Do not delete an active dependency because an implementation language has changed.
