# APK-to-SBOM Maven Evidence Recovery

This repository contains the implementation, experiments, evaluation records, theses, and paper materials for a master's project on recovering Maven component and version evidence from compiled Android APKs.

The project is an evidence-aware static-analysis MVP. It separates component-family identity, exact-version evidence, ambiguity, native-file boundaries, and downstream CycloneDX/OSV interpretation.

## What the tool does

The pipeline:

1. Inspects APK metadata, accessible DEX files, and native libraries.
2. Extracts package, class, method, opcode, dependency, literal, and structural evidence.
3. Compares APK evidence with versioned Maven reference profiles stored in SQLite.
4. Shortlists component families and ranks candidate releases with normalized weighted evidence.
5. Keeps identity confidence separate from version confidence and preserves close alternatives.
6. Emits CycloneDX 1.5 component records with evidence properties.
7. Represents native .so files as hash-identified file components.
8. Optionally queries OSV using the reported component/version evidence.

The ordinary APK-only matcher does not use source dependency versions as candidate hints. Source dependency trees are used for explicit validation and separate source-constrained analyses.

## Implementation

The Python package is apk-sbom-mvp version 0.1.0 and requires Python 3.12 or newer.

| Area | Main modules |
|---|---|
| APK and DEX analysis | src/apk_sbom/apk_extractor.py, dex_analyzer.py |
| Maven/reference preparation | maven_downloader.py, reference_converter.py, reference_features.py |
| Matching and version decisions | matcher.py, models.py |
| Reports and SBOM | report.py, sbom.py |
| Vulnerability interpretation | vulnerability.py |
| Source validation | source_validation.py |
| AI/R8 report-only assistance | ai_r8_assistant.py, ai_r8_final_evaluation.py, ai_r8_mvp_integration_gate.py |

The default matcher uses guarded promotion gates for the composite family shortlist and version-unique literal/context reranking. Broader R8 blending, AI suggestions, and additional structural experiments remain diagnostic or report-only; they cannot change selected versions, CycloneDX components, OSV labels, or source-validation metrics.

## Recorded evaluation snapshot

The paper freezes the retained PFE evaluation snapshot associated with the 20 June 2026 evidence package and implementation commit 2983d54. These are documented historical results; the current checkout does not contain every original row-level export, generated fixture APK, database snapshot, hash manifest, or run manifest required to independently recalculate every aggregate.

| Evaluation lane | Result | Interpretation |
|---|---:|---|
| Controlled fixtures | 84/84 expected rows across 72 fixtures | Controlled confirmation only |
| Clean source-validated APKs | 47/47 across 5 APKs | Emitted-version agreement in a small clean stratum |
| Partial source-validated APKs | 880/1,790 across 97 APKs | Emitted-version agreement on harder real cases |
| Combined source-validated APKs | 927/1,837 across 102 APKs | Emitted-version confirmation, not full dependency recall |
| Full source denominator | 927/12,082 across 106 source-tree cases | Source-denominator coverage |
| Source-version-constrained lane | 6,772/6,772 across 106 cases | Upper-bound recognition using source-known candidate slices |

The 30-fixture/35-component count is an earlier checkpoint. Later priority reference-recovery records use a different evaluation-only database and are not merged into the paper's matcher results.

## R8 and AI experiments

R8 stress fixtures cover rename, shrink, optimize, shrink-plus-optimize, package flattening/repackaging, inline-like call-site behavior, and multidex. The broader Phase-4 R8 blend was rejected after control and real-app regressions. The narrower Phase-5 trigger remains experiment-only and report-only.

The AI path is also report-only. Its project-derived structured dataset has 20,523 rows grouped into 149 case identifiers. A Random Forest and structured-token Transformer were evaluated for evidence/risk triage, while a raw-opcode Transformer was tested as a research prototype. These models do not determine Maven versions, modify SBOM components, or change vulnerability labels.

Detailed records:

- docs/thesis/PFE_CHAPTER3_AI_EVIDENCE_SNAPSHOT_2026-06-20.md
- docs/evaluation/AI_R8_ASSISTANT_DIAGNOSTICS.md
- docs/thesis/EXPERIMENT_DECISION_LEDGER.md
- docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md

## Repository layout

    src/apk_sbom/       implementation
    tests/              unit and promotion-gate tests
    configs/            reference and experiment configurations
    data/               source-validation and test inputs
    docs/               architecture, evaluation, and research records
    papers/             manuscript, audits, references, and supervisor briefing
    thesis/             PFE and master thesis sources and archives
    ressources/         reviewed research papers and resources
    scripts/            evaluation and report-generation utilities
    output/pdf/         generated paper PDF
    work/               technical notes and state-of-the-art documents

## Installation

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -e ".[dev]"

For report-only model experiments:

    python -m pip install -e ".[dev,ml,dl]"

## Main commands

    apk-sbom inspect-apk
    apk-sbom analyze-apk
    apk-sbom generate-report
    apk-sbom download-references
    apk-sbom convert-references
    apk-sbom extract-reference-features
    apk-sbom validate-source-deps
    apk-sbom r8-phase5-experiment
    apk-sbom ai-r8-build-dataset
    apk-sbom ai-r8-train
    apk-sbom ai-r8-suggest
    apk-sbom ai-r8-integration-gate

Run apk-sbom command --help for arguments. The exact database and configuration used for historical evaluation must be retained with its matching run manifest.

## Paper materials

- papers/INTEGRATED_MANUSCRIPT_DRAFT.md — source manuscript
- papers/MANUSCRIPT_TWO_COLUMN.tex — LaTeX source
- output/pdf/MANUSCRIPT_TWO_COLUMN.pdf — formatted PDF
- papers/PAPER_SECTION_EXPLANATION_FOR_SUPERVISOR.md — supervisor briefing
- papers/PAPER_FINAL_CONSISTENCY_REFERENCE_AUDIT.md — final audit

Paper structure:

1. Abstract
2. Introduction
3. State of the Art
4. Proposed Approach
5. Implementation and Experimental Evaluation
6. Conclusion

## Scope and limitations

The MVP does not claim universal Android dependency recovery, complete packaged-code recall, calibrated probabilities, native package/version attribution, or vulnerability precision/recall. Native-heavy applications, dynamic loading, encrypted or hidden DEX, commercial protectors, parser failures, absent reference versions, and adjacent releases with similar bytecode remain explicit limitations.

Source dependency trees are validation proxies rather than perfect packaged-code ground truth. OSV results are qualified by component/version evidence and are not independent proof of component presence or exploitability.

## Reproducibility

The repository contains the implementation, documentation, experiment decisions, and recorded results used for the theses and paper. Some original machine-readable inputs and run metadata are not in the current archive, so the paper reports documented evaluation snapshots and identifies their provenance instead of claiming a fresh complete rerun.


