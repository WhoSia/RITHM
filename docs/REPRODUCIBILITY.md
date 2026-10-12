# Reproducibility & data authority — RITHM

**Current P16 / 2026-10-12.** Previously top-level `README_REPRO.md` covered only the historical 2.3 court and is replaced by this complete project guide. [Verbatim historical README](PROJECT_HISTORY_20261012.md) preserves older source-era instructions and receipts.

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

## Critical interpretive restrictions

`VOL` and `SPD` are source sensor measurements and can share an unverified data-processing pipeline. Even independent ten-minute totals do not identify how a ten-minute flow was allocated to two five-minute bins. P16 operator bounds condition on hypothetical *certified independent five-minute count* error bounds, which have NOT been supplied. `q/speed` is a source congestion proxy, not true individual travel-time welfare; detector behavior and human guidance effects remain unproven.

`RITHM-2.6 OPEN`; passing source/schema/math tests ≠ causal traffic result.
