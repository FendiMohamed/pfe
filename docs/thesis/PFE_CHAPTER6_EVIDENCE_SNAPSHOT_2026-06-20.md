# PFE Chapter 6 Evidence Snapshot

## Snapshot Identity

- Frozen for writing on: `2026-06-20`
- Repository commit inspected: `2983d54`
- Branch: `codex/publish-r8-real-apk-checkpoint`
- Purpose: authoritative numerical and interpretation baseline for PFE Chapter
  6.

This snapshot freezes thesis-facing claims, not the whole repository. If a
generated evaluation artifact changes later, Chapter 6 must be re-audited
before its numbers are reused.

## Evidence Priority

The chapter uses the following order:

1. generated JSON evaluation artifacts;
2. generated dashboards and thesis tables;
3. current implementation and tests;
4. explanatory project documents.

Older narrative documents may contain historical dataset sizes. For example,
`docs/evaluation/CONTROLLED_EVALUATION.md` still describes an earlier
30-fixture/35-component stage. The current generated thesis source is
`data/results/evaluation/thesis-evaluation-tables.json`, which records 72
fixtures and 84 expected versions.

## Frozen Main Results

| Evidence class | Cases | Numerator / denominator | Rate | Permitted interpretation |
|---|---:|---:|---:|---|
| Controlled ground truth | 72 | 84 / 84 expected Maven versions | 100.0% | Pipeline mechanics succeed on the controlled fixture inventory. This is not real-world accuracy. |
| Clean source-validated real APKs | 5 | 47 / 47 emitted Maven versions | 100.0% | Strong exact-version evidence for emitted rows; three clean cases are sparse. |
| Partial source-validated real APKs | 97 | 880 / 1790 emitted Maven versions | 49.2% | Hard real-APK behavior with visible mismatches and missing/nuanced rows. |
| All source-validated real APKs | 102 | 927 / 1837 emitted Maven versions | 50.5% | Emitted Maven version confirmation rate, not full dependency recall. |
| Limitation/boundary cases | 4 | excluded | n/a | Native-heavy, hidden-code, and obfuscation boundaries; not accuracy failures. |

Primary artifacts:

- `data/results/evaluation/thesis-evaluation-tables.json`
- `docs/evaluation/THESIS_EVALUATION_TABLES.md`
- `docs/evaluation/APK_TYPE_EVALUATION.md`

## Full Source-Denominator Results

| Metric | Value |
|---|---:|
| Source-tree cases | 106 |
| Source dependency coordinate+version rows | 12082 |
| Unique source coordinates | 1370 |
| Unique source coordinate+version pairs | 3391 |
| Shared-DB coordinate-covered rows | 2220 / 12082 (18.4%) |
| Shared-DB exact-version-covered rows | 1231 / 12082 (10.2%) |
| End-to-end exact source rows emitted | 927 / 12082 (7.7%) |

Interpretation:

- `927/1837` measures version quality among emitted Maven rows.
- `927/12082` measures exact end-to-end recall against the full resolved source
  dependency denominator.
- These metrics answer different questions and must never be merged.

Primary artifact:

- `data/results/evaluation/reference-db-coverage-first-dashboard.json`
- `docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md`

## Source-Known V2 Upper-Bound Lane

| Metric | Value |
|---|---:|
| V2 reference DB components | 10517 |
| Completed source-tree cases | 106 / 106 |
| Emitted rows checked | 6772 |
| Exact confirmations | 6772 |
| Wrong-version emitted rows | 0 |
| Missing emitted rows | 0 |
| Remaining source-gap rows | 5238 |

The v2 lane constrains each APK's reference slice to exact coordinate+version
rows from its source dependency tree. It measures recognition under
source-known constraints. It is not unconstrained APK-only accuracy.

Remaining source-gap interpretation:

- 2281 matcher-recall candidates;
- 442 missing-reference candidates;
- the remaining rows are metadata/source-only, alias, project-module,
  relocated-coordinate, or other source boundaries.

Primary artifacts:

- `data/results/evaluation/real-apk-demo-final-large-v2-source-version-dashboard.json`
- `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_VERSION_EVALUATION.md`
- `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_GAP_TRIAGE.md`
- `docs/thesis/FINAL_V2_RESULTS_SECTION.md`

## Vulnerability Evidence

| Case | Result | Permitted interpretation |
|---|---|---|
| Calibrated F-Droid report | 23/23 emitted Maven versions source-confirmed; 0 OSV vulnerabilities | Clean negative demonstration. |
| Controlled Jackson Databind fixture | `jackson-databind@2.9.10.8`; 3 HIGH advisories | Controlled positive demonstration with exact known ground truth. |
| Real-APK OSV triage | 8 advisories across 6 component rows: 1 source-confirmed, 6 source-version-mismatch, 1 report-only | Only the source-confirmed row is source-validated vulnerability evidence; the others remain potential/report-only. |

Primary artifacts:

- `data/results/report-real-f-droid-final-demo-osv/`
- `data/results/demo-osv-vulnerable-jackson-databind/`
- `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md`

## AI/R8 Evidence

| Lane | Dataset / result | Authority |
|---|---|---|
| RandomForest assistant | 20523 rows; test macro-F1 0.708; test accuracy 0.690 | Report-only |
| Structured-token Transformer | 20523 rows; test macro-F1 0.977 | Research status only because shortcut/context risk remains |
| MVP-safe Transformer | 20523 rows; test macro-F1 0.882; accuracy 0.907 | Candidate for report-only risk triage; production wiring disabled |
| Raw-opcode Transformer | 1680 method sequences from 14 APKs; macro-F1 0.110 | Rejected for promotion; below opcode-count baseline 0.128 |
| Strict APK-only promotion matrix | 0 eligible production candidates after controls | Matcher/SBOM/CVE authority blocked |

Primary artifacts:

- `data/results/evaluation/ai-r8-final-evaluation.json`
- `data/results/evaluation/ai-r8-mvp-integration-gate.json`
- `docs/evaluation/AI_R8_FINAL_EVALUATION.md`
- `docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md`

## Failed and Non-Promoted Results Required in Chapter 6

- Global opcode tri-gram weighting: regressed controls; disabled by default.
- Global API-reference weighting: no measured guarded benefit; disabled by
  default.
- Global multi-scale R8 blend: improvements existed, but controlled and real
  regressions blocked promotion.
- Source-known version-band reranking: 565 rows appear fixable under source
  constraints, but APK-only safe fixes remain 0.
- Priority reference DB: 79.9% exact source-version coverage, but package
  shortlist preflights inflated false-positive emissions; evaluation-only.
- Fragment `1.6.2`: target and sampled controls passed, but `1.6.1/1.6.2`
  remained candidate-level near ties without version-unique APK evidence;
  experiment-only.
- Raw-opcode Transformer: below its simple baseline; research-only.

Primary artifact:

- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`
- `docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md`
- `docs/evaluation/REAL_APK_PRIORITY_TARGET_CONTROL_PREFLIGHT.md`

## Implementation Verification

Verification run on `2026-06-20`:

- project virtual environment: Python `3.12.0`;
- `python -m compileall -q src scripts tests`: passed;
- `.venv\Scripts\python.exe -m pytest -q`: `275 passed in 34.64s`;
- thesis evaluation tables regenerated successfully;
- thesis artifact index regenerated successfully.

Docker Desktop was installed, but the current sandboxed shell could not access
the Windows Docker engine pipe. This does not invalidate the saved Docker
evaluation artifacts; it means no new Docker rerun was performed during this
snapshot session.

## Frozen Writing Rules

- Always write “emitted Maven version confirmation rate” for `927/1837`.
- Never write that the system has 100% accuracy on 106 real APKs.
- Always qualify `6772/6772` as source-version constrained upper-bound
  recognition.
- Keep controlled, clean, partial, source-known, report-only, experiment-only,
  and limitation evidence separate.
- Do not describe native file hashes as native package/version identification.
- Do not describe AI output as component or version authority.
