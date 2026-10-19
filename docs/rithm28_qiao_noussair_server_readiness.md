# RITHM-2.8 — Qiao–Noussair authorized empirical source: HDD-only server readiness

**State:** preparation contract; NO server commands have been executed remotely. The only live artifacts are the private Google Drive source ZIP (21,150,492 bytes) plus two PDF supplements, and the read-only Ruby preflight. **Do not commit microdata into GitHub, use CI artifacts to upload raw data, or put raw files on a third-party server without independently confirming authorization and access controls.**

## Scientific fork
1. **Local/private source integrity:** the user reports that extracted CSVs look normal on Windows; an independent Drive ZIP inspection earlier found entirely NUL-valued decompressed original-experiment CSVs. These observations conflict. Do not infer a completed source repair. Run exact local hashes on the Gmail ZIP and extracted key CSVs and compare with Drive ZIP SHA-256 `a6cd28ee8a7e9aee99b7b71911e027dd28a0ddd9def08a95a45f6d7888b86a25`; compare the *same version* rather than only filenames. Keep a second original unmodified. For header check, run locally:
```powershell
Get-FileHash -Algorithm SHA256 "C:\Users\<YOUR_USER>\Downloads\Data and code files.zip"
```
```bash
ruby ruby/rithm28/source_preflight.rb "/path/to/private/data_task_all_230705.csv" "/path/to/private/data_task_all_switch_230705.csv"
```
This only prints header names, byte counts and file hashes; not participant rows. `SCHEMA_HEADER_PRESENT` validates header only, NOT rows, randomization, license or source identity. Expanding the **20+GB** simulation branch is unnecessary at this stage.

2. **Data authorization:** Qiao and Noussair authorized the specific proposed independent analysis, with citation requirement. The email does **not** expressly authorize redistribution or storage of participant microdata on someone else's machine. Keep raw experiment CSVs on a personally controlled private PC until permission, physical server access and encryption/ACL constraints are independently resolved. Put only freely redistributable code, synthetic fixtures and allowable aggregated reports on the borrowed server.

3. **HDD-only remote environment (read-only checks first):** the user previously designated Ubuntu, host `dobby`, user `sean`, i5-8500 / 32GB RAM / GTX1080Ti, with WORK *inside* `/run/media/sean/5988414b-645f-4967-9587-1c1baf95ecd9/oozoon`. The local host and path **must be rediscovered before reuse**; do not run from an unverified path. No work under SSD home for data, cache or temporary outputs; do not change global runtimes or git configuration. Work only under the assigned HDD root. Explicitly set `TMPDIR`, `XDG_CACHE_HOME`, `GOCACHE`, `GOPATH`, Ruby temp and analysis output beneath its own local analysis subtree. Do not store secrets in scripts. Avoid sustained unconstrained 100% CPU and monitor free disk space before >20GB expansion.

4. **Reproducible server bootstrap (execute only after manual path validation):**
```bash
# Check path, mount and owner. Never run with sudo.
WORK='/run/media/sean/5988414b-645f-4967-9587-1c1baf95ecd9/oozoon'
test -d "$WORK" && test -w "$WORK" || exit 1
df -h "$WORK"
findmnt -T "$WORK"
# No system-level changes; no raw human data transfer here.
mkdir -p "$WORK/rithm_source_bootstrap"/{tmp,cache,go-cache,go-path,logs,synthetic-results}
export TMPDIR="$WORK/rithm_source_bootstrap/tmp"
export XDG_CACHE_HOME="$WORK/rithm_source_bootstrap/cache"
export GOCACHE="$WORK/rithm_source_bootstrap/go-cache"
export GOPATH="$WORK/rithm_source_bootstrap/go-path"
ruby -v
go version
```
Any git checkout path must also remain under the vetted WORK. Existing global system versions, existing unrelated working dirs and data must not be modified.

## Parallel research branches (no fictional empirical success)
- **Ruby scientific reproduction:** inspect authors' documented participant/period/session/group/section grains; derive original treatment availability versus observable decision variables. Introduce strict audit first, then reproduce published descriptive outcomes with verifiable scripts.
- **Go independent audit:** verify counters and aggregate-cost construction from separate code, using the same frozen authorized input. This is not permission to upload raw input to public CI.
- **Theory:** formulate a falsifiable, group-held-out question: do route-switch inertia/learning models that best predict held-out individual decisions also best predict aggregate congestion cost? Distinguish mechanical aggregation from behaviorally transported group outcomes, and test negative cases when sufficient real data become available.
- **P1-P18 synthetic temporal dual certificates** remain an *independent* track; do not conflate their model-world outage or 'trusted' labels with real experiment instructions, witnessed information receipt or laboratory behavior.
- **P1-P19/P2/2.9:** no promotion from availability of a large ZIP, from synthetic verification or from a repaired transfer alone. Novelty + independent evidence and valid external estimands remain gates.

## Citation and project record
Noussair, C. N., & Qiao, L. (2025). *Congestion Information and Efficiency: An Experiment*. Management Science, 72(7), 6229–6250. https://doi.org/10.1287/mnsc.2023.00056. The 2025 online / 2026 issue display divergence must be retained in citation metadata.
- [Author approval and Drive custody](https://app.notion.com/p/3feef561cf9281ab9f6dfe9af767d909)
- [Dedicated citation note](https://app.notion.com/p/3feef561cf92819c8fb7fd2565eadaa6)
- [Private original source folder](https://drive.google.com/drive/folders/13_iVjJ-8R9XlDFDRrKl5r0LI_kVvqDwW)
