# File and Proof Index

## Current status

| Question | File |
|---|---|
| What is currently done or blocked? | [TASKS.md](../../../TASKS.md) |
| What must a continuing agent know? | [CODEX_CONTEXT.md](../../codex/CODEX_CONTEXT.md) |
| What is the final demo flow? | [FINAL_DEMO_RUNBOOK_V2.md](../../evaluation/FINAL_DEMO_RUNBOOK_V2.md) |
| What should be claimed in the defense? | [DEFENSE_PRESENTATION_GUIDE.md](../../thesis/DEFENSE_PRESENTATION_GUIDE.md) |

## Architecture and implementation

| Topic | Primary source |
|---|---|
| Architecture | [MVP_ARCHITECTURE.md](../../architecture/MVP_ARCHITECTURE.md) |
| Decisions | [DECISIONS_LOG.md](../../architecture/DECISIONS_LOG.md) |
| APK extraction | [apk_extractor.py](../../../src/apk_sbom/apk_extractor.py) |
| DEX analysis | [dex_analyzer.py](../../../src/apk_sbom/dex_analyzer.py) |
| Maven download | [maven_downloader.py](../../../src/apk_sbom/maven_downloader.py) |
| D8 conversion | [reference_converter.py](../../../src/apk_sbom/reference_converter.py) |
| SQLite reference features | [reference_features.py](../../../src/apk_sbom/reference_features.py) |
| Matching | [matcher.py](../../../src/apk_sbom/matcher.py) |
| Detection models | [models.py](../../../src/apk_sbom/models.py) |
| CycloneDX | [sbom.py](../../../src/apk_sbom/sbom.py) |
| OSV/CVE mapping | [vulnerability.py](../../../src/apk_sbom/vulnerability.py) |
| Source validation | [source_validation.py](../../../src/apk_sbom/source_validation.py) |
| Reports | [report.py](../../../src/apk_sbom/report.py) |
| CLI parser | [cli.py](../../../src/apk_sbom/cli.py) |

## Research proof

| Topic | File |
|---|---|
| All paper summaries | [papers_overview.json](../../../papers/data/papers_overview.json) |
| Tool comparison | [SBOM_Tools_Synthesis_Table.md](../../../papers/data/SBOM_Tools_Synthesis_Table.md) |
| Adopt/adapt/reject decisions | [impact_on_project.md](../../../papers/data/impact_on_project.md) |
| Paper-to-code mapping | [PAPER_TO_IMPLEMENTATION_TRACEABILITY.md](../../thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md) |
| Experiment decisions | [EXPERIMENT_DECISION_LEDGER.md](../../thesis/EXPERIMENT_DECISION_LEDGER.md) |
| AI/R8 method choice | [AI_R8_ASSISTED_METHOD_SELECTION.md](../../research/AI_R8_ASSISTED_METHOD_SELECTION.md) |

## Evaluation proof

| Claim | File |
|---|---|
| `84/84`, `47/47`, `880/1790`, `927/1837` | [THESIS_EVALUATION_TABLES.md](../../evaluation/THESIS_EVALUATION_TABLES.md) |
| Metric interpretation | [THESIS_EVALUATION_CHAPTER_DRAFT.md](../../evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md) |
| Source validation by APK | [REAL_APK_SOURCE_VALIDATION_DASHBOARD_REPORT.md](../../evaluation/REAL_APK_SOURCE_VALIDATION_DASHBOARD_REPORT.md) |
| Shared DB coverage denominator | [REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md](../../evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md) |
| Source-known `6772/6772` lane | [DEMO_FINAL_V2_PACKAGE.md](../../evaluation/DEMO_FINAL_V2_PACKAGE.md) |
| Final thesis wording | [FINAL_V2_RESULTS_SECTION.md](../../thesis/FINAL_V2_RESULTS_SECTION.md) |
| AI/R8 complete evidence | [AI_R8_FINAL_EVALUATION.md](../../evaluation/AI_R8_FINAL_EVALUATION.md) |
| AI authority verdict | [AI_R8_MVP_INTEGRATION_GATE.md](../../evaluation/AI_R8_MVP_INTEGRATION_GATE.md) |
| Raw-opcode negative result | [AI_R8_RAW_OPCODE_TRANSFORMER.md](../../evaluation/AI_R8_RAW_OPCODE_TRANSFORMER.md) |

## Latest reference DB proof

| Topic | File |
|---|---|
| Priority catalog and reconciliation | [REAL_APK_PRIORITY_REFERENCE_CATALOG.md](../../evaluation/REAL_APK_PRIORITY_REFERENCE_CATALOG.md) |
| Lightweight recovery | [REAL_APK_PRIORITY_LIGHTWEIGHT_RECOVERY_RESULT.md](../../evaluation/REAL_APK_PRIORITY_LIGHTWEIGHT_RECOVERY_RESULT.md) |
| `79.9%`/`89.1%` coverage | [REFERENCE_DB_COVERAGE_PRIORITY_DASHBOARD.md](../../evaluation/REFERENCE_DB_COVERAGE_PRIORITY_DASHBOARD.md) |
| Failed production preflight | [REAL_APK_PRIORITY_TARGET_CONTROL_PREFLIGHT.md](../../evaluation/REAL_APK_PRIORITY_TARGET_CONTROL_PREFLIGHT.md) |
| Fragment 1.6.2 experiment | [WRONG_VERSION_P1_FRAGMENT_1_6_2_PREFLIGHT.md](../../evaluation/WRONG_VERSION_P1_FRAGMENT_1_6_2_PREFLIGHT.md) |

## Generated data

Human-readable Markdown should normally have a corresponding JSON, CSV, or
SQLite artifact under:

- `data/results/evaluation/`
- `data/results/experiments/`
- `data/reference_db/`

When auditing a claim, prefer the generated machine-readable artifact and its
builder script, then use the Markdown as interpretation.

## Tests

Unit and integration tests live in `tests/`. Run:

```powershell
docker compose run --rm apk-sbom pytest -q
```

For a behavior change, identify the relevant test and the generated
target/control evidence. Passing unit tests alone does not justify a matcher
promotion.
