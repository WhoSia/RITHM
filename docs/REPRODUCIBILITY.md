> **CURRENT HEAD NOTE (2026-10-18):** RITHM-2.8 P1 is the sole open scientific mainline. The sections below preserve earlier 2.6/2.7 commands and their then-current labels verbatim; references to 2.6 or 2.7 as CURRENT/OPEN are historical, not current authority. For modern Ruby-first and Go-independent reproducibility, use [root README](../README.md) and [Ruby–Go certificate workflow](../.github/workflows/rithm-ruby-go.yml). P1-P18's new shared-capacity Ruby probe is synthetic and P2/2.9 promotion remains HOLD. Some P28 specialist crosschecks were [verbatim archived to Drive](https://docs.google.com/document/d/1_9rW5-XEOLtzeM7SXzC97O952Frqsi2ARGd-aQJmLfo/edit) and are not runnable from the current checkout without restoration.

# Reproducibility & data authority — RITHM

**CURRENT P28 science reproduction:** [P28 Ruby/Rust/Go/C++/R replay](rithm27_p28_replay.md) is now the current multi-round source-conditional protocol, using a distinct `go/p28` package to avoid conflicting with legacy `go/bounds.go`. Executed Go 4/4 tests, C++17 independent 18/18, Ruby independent 18/18; Rust/R source authored NOT executed, Actions unrun. Original human S2/2022 GPS data are sourced separately, not pooled. Historic commands and dependencies below remain for earlier stages only.\n\n**Active research implementation:** Ruby, Rust, Go, C++ and R — not Python-first. [P27 exact-network five-language reference](RITHM_P27_MULTILANGUAGE_REPLAY.md). P27 Ruby, Go and C++ were independently executed on original-source-derived 480 group states; Rust and R **not executed** due to missing runtime in the current analysis environment. Existing Python commands below reproduce HISTORICAL stages only; do not represent the new recommended architecture. All original source data and original compiler versions preserved without globally modifying any server.


**CURRENT: RITHM-2.7 OPEN; RITHM-2.6 CLOSED by Flowing handoff on 2026-10-13.** Original P1–P24 scripts/tests/data custody and prior HOLDs continue in the single 2.7 mainline. [Full scientific transfer](rithm27_flowing_transition_20261013.md). Historical P17 and older commands below remain reproducible and labeled by their original stage. Previously top-level `README_REPRO.md` covered only the historical 2.3 court and is replaced by this complete project guide. [Verbatim historical README](PROJECT_HISTORY_20261012.md) preserves older source-era instructions and receipts.

## Python quick start

Python 3.12. Run from the repository root:

```bash
python -m pip install numpy pandas
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m rithm.legacy.rithm20 tests/fixtures/study1-mini.csv
PYTHONPATH=src python -m rithm.legacy.rithm24_identification
python tools/traffic_sources/p15_phase_operator.py
python tools/traffic_sources/p15_source_manifest_gate.py --shards-dir /path/to/shards --h1-manifest /path/to/H1/manifest.json --h2-manifest /path/to/H2/manifest.json
```

On PowerShell use `$env:PYTHONPATH = "src"` before the Python commands. The 2.3 welfare accounting and source decoder additionally require `pandas`; their original public derivative data live in `data/`. Run generated-output scripts in a scratch working directory, not from the repository root. The archived RITHM 2.2 audit additionally needs SciPy and the original Ashraf study CSV.

## Data hierarchy and provenance

- P13–P16: Original [Seoul 2025 data publisher](https://data.seoul.go.kr/dataList/OA-22351/F/1/datasetView.do), sharded by the data owner into 38 UTF-8 BOM files, rehash against the two `RITHM_SOURCE_CSV_SHARDS_V1` manifests; this checks *current shards*, not the deleted original CP949 bytes.
- The 5-minute clock is source timestamp; missing 2025-06-09 and 2025-07-10/11/15 are **no-source blackout dates**, never impute zero traffic.
- P13/P14/P15 numerical retrospective findings are summarized in `docs/data/` and corresponding `docs/rithm26_*.md`, not generically re-certified by synthetic Actions tests. P16 source-specific six-day audit is a distinct partial-identification sensitivity analysis.
- P2.3: [Wijayaratna et al. 2017](https://doi.org/10.1371/journal.pone.0184191.s002) licensed source-derived compact route/cost tables under `data/`; original workbook is the source of record.
- P2.0/2.2: Original 2023 Ashraf individual human records are **not distributed** in GitHub; CI fixture is synthetic.


## P17 reproducible phase-proxy and micro-to-macro tests

From repo root, with no synthetic fixtures beyond tests and no source file for the pure theory:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_p17_phase_network.py' -v
```

If running the six REAL 2025 source days, FIRST verify original shard hashes against the two user-owned manifests using the P15 source gate, then:

```bash
PYTHONPATH=src python tools/traffic_sources/p17_phase_proxy_audit.py \\
  --input /local/path/to/2025-shard-csvs \\
  --output /scratch/p17_phase_proxy.json
```

This audit STRICTLY rehashes H1 parts 005,009,011,012 (not all 38 at run time), checks 2,027,915 source rows, and computes six previously P15/P16-exposed days. The phase rearrangement cap is a hypothetical sensitivity budget, **not calibrated error**. It holds source speed constant; therefore these are only source proxy envelopes, not independently measured human welfare. The independent static network externality/Braess tests NEVER act on physical Seoul traffic.

## Critical interpretive restrictions

`VOL` and `SPD` are source sensor measurements and can share an unverified data-processing pipeline. Even independent ten-minute totals do not identify how a ten-minute flow was allocated to two five-minute bins. P16 operator bounds condition on hypothetical *certified independent five-minute count* error bounds, which have NOT been supplied. `q/speed` is a source congestion proxy, not true individual travel-time welfare; detector behavior and human guidance effects remain unproven.

`RITHM-2.6 OPEN`; passing source/schema/math tests ≠ causal traffic result.


## P20 2025 source delay-scenario re-execution (new 2026-10-13)

Obtain the source-authority H1/H2 manifest JSON and all 38 unchanged UTF8 CSV shards from the user's private Drive RITHM 2025 source folder; no original CP949 files. Python 3.12+, numpy and pandas. Example:

```bash
python tools/traffic_sources/p20_latency_court.py --shards-dir /local/2025-shards --h1-manifest /local/H1/manifest.json --h2-manifest /local/H2/manifest.json --output-dir /scratch/p20
python -m unittest discover -s tests -p 'test_p20_latency_authority.py' -v
```

The actual full 2025 execution verified 38/38 original shard SHA256 and generated 2,121,699 strictly same-mask future ten-minute source outcomes. This is source information-delay SCENARIO analysis; publication latency NOT measured. The high-memory intermediate tensor belongs in scratch, NEVER GitHub. Passes on actual original 2025 source were run locally, offline test code committed with [skip ci] without CI claims. No physical sensor or human welfare identified. [P20 source report](rithm26_p20_observation_delay_authority_welfare_20261013.md).


## P23–P24: receipt evidence and exact synthetic human-welfare bridge

P23 reads 2025 Seoul measured traffic but assigns entirely **synthetic receipt events**. It does not establish actual client-source receipt authority. P24 uses the separate 2017 human experimental *cost geometry*, not a joined human/2025 sensor cohort.

```bash
python tools/traffic_sources/p24_receipt_to_welfare_bridge.py
python -m unittest discover -s tests -p 'test_p24_receipt_to_welfare_bridge.py' -v
```

In P24's three specified toy human-response worlds, a hypothetical timely receipt and upstream A-C total 8 accompany group costs 206/212/220. The restricted baseline-minus-policy cost improvement is in [-8,+6], an exact **synthetic** counterexample, not measured behavior or field welfare. GitHub Actions has not been run for this P24 commit. See [P24 note](rithm27_p24_receipt_to_response_welfare_bridge_20261013.md).
