# RITHM — Route-choice Inertia and Traffic Hysteresis Modeling

## Current mainline — RITHM-2.10 OPEN (2026-11-03)

**Research name:** Mechanism Identifiability in Repeated Resource Choice: Behavioral Inertia, Latent Group States and Strategic Dependence. The core research question is no longer only whether repeated choices and group turnover can be predicted, but which distinct behavioral mechanisms can generate the same observable choices and how to distinguish them. [Notion 2.10 charter](https://app.notion.com/p/40def561cf92812e9c51d5073aa70ef4) · [Ruby research charter](ruby/rithm210/RESEARCH_CHARTER.md) · [P0 exact latent-shock counterexample](ruby/rithm210/p0/latent_common_shock.rb) and [Minitest](ruby/rithm210/p0/test_latent_common_shock.rb).

**2026-11-04 scientific scope correction:** The original RITHM thesis is the generative chain **microscopic behavioral/cognitive/informational friction → repeated choice and adaptive feedback → persistent macro congestion and welfare loss / possible policy reversal**. RITHM-2.10's mechanism-identifiability and joint-turnover prediction work is a **necessary subprogram**, not a replacement for the macro-welfare question. Existing identifiability results and individual-history forecasts are valuable but do NOT yet establish causal friction or societal loss. [Self-audit and theory reprioritization](ruby/rithm210/SCIENTIFIC_SELF_AUDIT_20261104.md) · [Ruby exact micro→macro reference example](ruby/rithm210/p3/friction_welfare.rb) · [Minitest](ruby/rithm210/p3/test_friction_welfare.rb). The two-link threshold stationary-band and welfare result is **illustrative prior-art territory, not a novel theorem**; local Ruby test 5 runs/22 assertions pass, published exact-SHA/remote CI run still unverified.

**2026-11-04 P3-R5 mechanism boundary:** At *identical* current socially optimal occupancy n=4, Full-information group's next-period excess congestion cost fell descriptively from 3.01948 (early) to 1.33074 (late); true zero-gross-switch probability rose 22.08%→58.37%. A uniform common-state n∈{3,4,5} standardization likewise shows a 1.25569 next-cost decline (24-session exploratory 95% [0.65830,1.85838]). Current and next occupancy alone, however, do not reveal gross switching G=U+D: G ranges sharply over |m−n|, |m−n|+2, ... , min(n,6−m)+min(m,6−n). **Actual switching resource cost θ is NOT measured**, so no realized welfare effect may be assigned to it. [P3-R5 evidence](ruby/rithm210/P3_R5_CONDITIONAL_INSTABILITY_20261104.md), [Ruby turnover bounds](ruby/rithm210/p3/churn_welfare_bounds.rb), [Drive detailed record](https://docs.google.com/document/d/1__2ukO4WBkZNYzF82wwIfy1TAKYwBc_uNzSu6zd42BY/edit). Neither the source paper's early/late information efficiency phenomenon nor this elementary partial-identification algebra is claimed novel; causal information effects remain HOLD.

**2026-11-04 P3 welfare-first result:** The author-approved six-person congestion experiment has an **exact observed social-cost functional**: with n route-A users, raw individual Cost sums to C(n)=n²+2(6−n)²=24+3(n−4)² on all **5,616** eligible group-periods. Full-information early-to-late group excess-cost decline 4.11250→2.09375 is dominated by lower occupancy **dispersion**, not a mean shift (mean NumA 3.9875→4.00625). Strictly prior-only actor-history forecast strength20 greatly improved joint turnover logloss but **worsened squared error of expected next welfare** 18.07549→18.31503, illustrating the target mismatch; exploratory confidence intervals and source limitations documented in [P3 welfare evidence](ruby/rithm210/P3_WELFARE_BRIDGE_20261104.md). This empirical bridge is at six-person GROUP scale, not a proven universal macro welfare law, and the original Noussair–Qiao paper already reports the early/late information efficiency pattern. [Exact welfare algebra](ruby/rithm210/p3/experimental_welfare.rb) · [Original-source welfare audit](ruby/rithm210/p3/original_welfare_audit.rb) · [Welfare probability forecast](ruby/rithm210/p3/welfare_cross_validation.rb). Original human rows remain in Drive, GitHub Actions bot is not a committer, remote run PASS not asserted.

**First P0 result, exact synthetic counterexample:** with a previous A-users and 6-a previous B-users, conditionally independent switches with shared hidden fair group shock Z and individual probability p+delta*Z yield a positive unconditional residual cross-moment a(6-a)delta^2. At a=3, p=1/2, delta=3/40 the exact result is 81/1600=0.050625. This does **not** fit or explain the original human data, establish an actual group strategy, or prove novelty. The previous exploratory +0.0512449 residual estimate therefore cannot independently identify coordination. Local Ruby 3.3.8 P0 tests: 4 runs, 6 assertions, zero failures; remote GitHub Actions verification remains pending.

**Inheritance and technical debt:** RITHM-2.9 CLOSED as a research generation, not as universal proof or full validation of original-source analysis. The human-data EWA/Markov/oracle and 24-session evidence, information-set limitations, unverified prior cross-validation alignment, original Table 8 discrepancy, and CI/source SHA HOLD all transfer to 2.10. A genuine 2.9 Ruby API mismatch was identified on 2026-11-03; repair commits [b717c893](https://github.com/WhoSia/RITHM/commit/b717c8932cc37cb7967fd0df71fb6e5330b76f95), [31ceab9c](https://github.com/WhoSia/RITHM/commit/31ceab9cc7722f561ffa509c9c24c782faf625b4). This is a code-compatibility repair, not a claim that the original residual numerical result has been re-executed from the committed source. GitHub Actions are allowed to run read-only tests but github-actions[bot] MUST NOT appear as code commit author/committer. Original human data remain preserved in [Drive](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view), not re-uploaded publicly.

---

## Historical 2.9 research snapshot (2026-10-19 to 2026-11-02; superseded as mainline by 2.10)


**Formal 2.9 research name:** Resource-Bounded Strategic Agency: Costly Deliberation, Behavioral Friction, Endogenous Information & Collective Dynamics. User-authorized successor; 2.8 CLOSED as a generation, all P1–P27 proofs, corrections, source/novelty holds and historical records inherited. Existing root name, repository slug and history unchanged. [Current Notion charter](https://app.notion.com/p/3feef561cf9281bcbd77eeb6c983557e).

**First actual 2.9-P0 code:** [Ruby finite paid-instruction 2-agent game](ruby/rithm29/p0/paid_agency.rb) with [pure/mixed checks](ruby/rithm29/p0/test_paid_agency.rb). In a restricted binary parity task, agents pay for READ_X, READ_Y and XOR, then impose external congestion on each other's actions. At fee 1, error loss 2, there are two asymmetric pure Nash profiles with all-in social cost 5, and a symmetric mixed Nash with each computing at probability 1/2, social cost 11/2. It is a **toy one-round finite game**, not a repeated behavioral model, universal complexity theorem, or independent Go-verified result. Research goal: actual paid cognition in repeated joint finite-state dynamics and falsifiable cross-domain abstraction. P1/novelty and real source welfare claims HOLD.

---

## Historical 2.8 canonical snapshot (2026-10-18; superseded as mainline by 2.9)

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
