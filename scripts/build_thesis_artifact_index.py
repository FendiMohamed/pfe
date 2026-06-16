from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_APK_TYPE_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_THESIS_TABLES_JSON = Path("data/results/evaluation/thesis-evaluation-tables.json")
DEFAULT_REFERENCE_COVERAGE_JSON = Path(
    "data/results/evaluation/reference-db-coverage-first-dashboard.json"
)
DEFAULT_SOURCE_OBSERVED_CATALOG_JSON = Path(
    "data/results/evaluation/source-observed-reference-catalog.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/thesis-artifact-index.json")
DEFAULT_OUTPUT_DOC = Path("docs/thesis/THESIS_ARTIFACT_INDEX.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a thesis artifact index that maps claims to evidence files.",
    )
    parser.add_argument("--apk-type-json", default=str(DEFAULT_APK_TYPE_JSON))
    parser.add_argument("--thesis-tables-json", default=str(DEFAULT_THESIS_TABLES_JSON))
    parser.add_argument("--reference-coverage-json", default=str(DEFAULT_REFERENCE_COVERAGE_JSON))
    parser.add_argument(
        "--source-observed-catalog-json",
        default=str(DEFAULT_SOURCE_OBSERVED_CATALOG_JSON),
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    apk_type_path = Path(args.apk_type_json)
    thesis_tables_path = Path(args.thesis_tables_json)
    reference_coverage_path = Path(args.reference_coverage_json)
    source_observed_catalog_path = Path(args.source_observed_catalog_json)
    payload = build_index(
        read_json(apk_type_path),
        read_json(thesis_tables_path),
        read_json_if_exists(reference_coverage_path),
        read_json_if_exists(source_observed_catalog_path),
        apk_type_path=apk_type_path,
        thesis_tables_path=thesis_tables_path,
        reference_coverage_path=reference_coverage_path,
        source_observed_catalog_path=source_observed_catalog_path,
    )

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "claims": len(payload["claim_evidence"]),
                "case_artifacts": len(payload["case_artifacts"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_index(
    apk_type: dict[str, Any],
    thesis_tables: dict[str, Any],
    reference_coverage: dict[str, Any] | None,
    source_observed_catalog: dict[str, Any] | None,
    *,
    apk_type_path: Path,
    thesis_tables_path: Path,
    reference_coverage_path: Path,
    source_observed_catalog_path: Path,
) -> dict[str, Any]:
    summary = thesis_tables["summary"]
    coverage_summary = (reference_coverage or {}).get("summary", {})
    source_observed_summary = (source_observed_catalog or {}).get("summary", {})
    return {
        "schema_version": 1,
        "sources": {
            "apk_type": normalize_path(apk_type_path),
            "thesis_tables": normalize_path(thesis_tables_path),
            "reference_coverage": normalize_path(reference_coverage_path)
            if reference_coverage
            else "",
            "source_observed_catalog": normalize_path(source_observed_catalog_path)
            if source_observed_catalog
            else "",
        },
        "summary": {
            "controlled": (
                f"{summary['controlled_fixtures']['confirmed_versions']}/"
                f"{summary['controlled_fixtures']['expected_components']} "
                f"expected versions across {summary['controlled_fixtures']['cases']} fixtures"
            ),
            "clean_real": (
                f"{summary['clean_versions']['confirmed']}/"
                f"{summary['clean_versions']['checked']} emitted Maven versions across "
                f"{summary['clean_versions']['cases']} APKs"
            ),
            "partial_real": (
                f"{summary['partial_versions']['confirmed']}/"
                f"{summary['partial_versions']['checked']} emitted Maven versions across "
                f"{summary['partial_versions']['cases']} APKs"
            ),
            "overall_real": (
                f"{summary['source_validated_versions']['confirmed']}/"
                f"{summary['source_validated_versions']['checked']} emitted Maven versions across "
                f"{summary['source_validated_versions']['cases']} APKs"
            ),
            "source_denominator_recall": format_reference_coverage_summary(coverage_summary),
            "source_observed_reference_inputs": format_source_observed_catalog_summary(
                source_observed_summary,
            ),
        },
        "claim_evidence": build_claim_evidence(thesis_tables),
        "table_sources": build_table_sources(),
        "figure_plan": build_figure_plan(),
        "case_artifacts": build_case_artifacts(apk_type.get("real_cases", [])),
        "demo_package": build_demo_package(),
        "writing_guardrails": thesis_tables.get("writing_guidance", []),
        "final_report_checklist": build_final_report_checklist(),
    }


def build_claim_evidence(thesis_tables: dict[str, Any]) -> list[dict[str, Any]]:
    shared_artifacts = [
        "docs/evaluation/THESIS_EVALUATION_TABLES.md",
        "docs/evaluation/APK_TYPE_EVALUATION.md",
        "docs/evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md",
    ]
    extra_by_prefix = {
        "The MVP can recover exact": [
            "docs/evaluation/CONTROLLED_EVALUATION.md",
            "data/results/evaluation/controlled-evaluation.md",
            "data/results/evaluation/generated-apk-category-batch.md",
        ],
        "The MVP can produce exact": [
            "docs/evaluation/MVP_RESULTS_SUMMARY.md",
            "data/results/source-validation/fdroid-final-demo-osv/source-validation.md",
            "data/results/source-validation/opentracks-calibrated-db/source-validation.md",
            "data/results/source-validation/tusky-calibrated-db/source-validation.md",
        ],
        "Harder APK families": [
            "docs/evaluation/VERSION_BAND_TIE_EVIDENCE.md",
            "docs/evaluation/REAL_APK_CURRENT_BATCH_RESULTS.md",
            "docs/evaluation/NEXTCLOUD_ANDROID_PROOF_BUNDLE.md",
            "docs/evaluation/MARKOR_PROOF_BUNDLE.md",
        ],
        "The evaluation separates": [
            "docs/evaluation/K9_THUNDERBIRD_PROOF_BUNDLE.md",
            "docs/evaluation/HIDDEN_DEX_LIMITATION_FIXTURE.md",
            "docs/evaluation/APK_TESTSET_INVENTORY.md",
        ],
    }

    rows = []
    for row in thesis_tables.get("claim_table", []):
        artifacts = list(shared_artifacts)
        for prefix, extra in extra_by_prefix.items():
            if row["claim"].startswith(prefix):
                artifacts.extend(extra)
                break
        rows.append(
            {
                "claim": row["claim"],
                "evidence": row["evidence"],
                "scope": row["scope"],
                "limitation": row["limitation"],
                "artifacts": unique(artifacts),
            }
        )
    return rows


def build_table_sources() -> list[dict[str, str]]:
    return [
        {
            "table": "Main evaluation metrics",
            "source": "docs/evaluation/THESIS_EVALUATION_TABLES.md",
            "use": "Copy into the evaluation chapter and presentation results slide.",
        },
        {
            "table": "Per-APK role and rate table",
            "source": "docs/evaluation/THESIS_EVALUATION_TABLES.md",
            "use": "Use as appendix evidence or shortened in the main evaluation chapter.",
        },
        {
            "table": "APK family grouping",
            "source": "docs/evaluation/APK_TYPE_EVALUATION.md",
            "use": "Explain why clean, partial, blocked, and limitation cases are separate.",
        },
        {
            "table": "Real APK source-validation dashboard seed",
            "source": "docs/evaluation/REAL_APK_SOURCE_VALIDATION_DASHBOARD_REPORT.md",
            "use": "Use as the dashboard-ready per-APK classification, wrong-version, missing-package, and DB-growth-candidate source.",
        },
        {
            "table": "Reference DB coverage-first dashboard",
            "source": "docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md",
            "use": "Use to separate emitted-component confirmation from full source dependency recall, reference DB coordinate coverage, and exact-version coverage.",
        },
        {
            "table": "Source-observed reference catalog",
            "source": "docs/evaluation/SOURCE_OBSERVED_REFERENCE_CATALOG.md",
            "use": "Use to explain the missing-TPL/missing-version growth inputs, buildable bytecode coordinates, source-version slots, and metadata-only skips before any shared DB promotion.",
        },
        {
            "table": "Source-observed reference DB batch log",
            "source": "docs/evaluation/SOURCE_OBSERVED_REFERENCE_DB_BATCH_LOG.md",
            "use": "Use to show that the evaluation-only DB build has started with recorded download, DEX conversion, and feature-extraction counts while shared DB claims remain unchanged.",
        },
        {
            "table": "Real-APK priority reference catalog",
            "source": "docs/evaluation/REAL_APK_PRIORITY_REFERENCE_CATALOG.md",
            "use": "Use to explain the deadline-focused exact-version DB built only from versions observed in the 102 real APK source-validation dependency trees.",
        },
        {
            "table": "Real-APK priority failed-slot retry plan",
            "source": "docs/evaluation/REAL_APK_PRIORITY_FAILED_DOWNLOAD_RETRY_PLAN.md",
            "use": "Use to show the transparent retry of failed priority slots, the recovered artifact/feature counts, and the remaining unrecovered boundary.",
        },
        {
            "table": "Priority reference DB coverage dashboard",
            "source": "docs/evaluation/REFERENCE_DB_COVERAGE_PRIORITY_DASHBOARD.md",
            "use": "Use to separate DB coverage growth from emitted-version accuracy: exact source-version coverage improves while matcher output remains a separate rerun step.",
        },
        {
            "table": "Large combined reference DB coverage dashboard",
            "source": "docs/evaluation/REFERENCE_DB_COVERAGE_LARGE_COMBINED_DASHBOARD.md",
            "use": "Use to show the combined evaluation-only DB component count, coordinate coverage, exact-version coverage, and remaining reference gaps.",
        },
        {
            "table": "Large combined real APK analysis",
            "source": "docs/evaluation/LARGE_COMBINED_REAL_APK_ANALYSIS.md",
            "use": "Use as the detailed analysis entry point for per-APK rows, wrong-version rows with correct source versions, source false negatives, false-positive extra emissions, vulnerabilities, and the current large-DB runtime blocker.",
        },
        {
            "table": "Demo-final fixable reference retry plan",
            "source": "docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_RETRY_PLAN.md",
            "use": "Use to show how the remaining missing-reference rows were filtered into fixable retry, no-bytecode, and source-boundary slots before growing the DB.",
        },
        {
            "table": "Demo-final fixable reference retry stage 2 plan",
            "source": "docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_RETRY_STAGE2_PLAN.md",
            "use": "Use to show the bounded alternate-packaging/repository retry for first-stage failed slots and which rows were kept as boundaries.",
        },
        {
            "table": "Demo-final fixable reference growth result",
            "source": "docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_GROWTH_RESULT.md",
            "use": "Use to show the 24 recovered bytecode-bearing components, the v2 DB component count, the no-bytecode rows, and the attempted-but-unavailable boundary rows.",
        },
        {
            "table": "Demo-final v2 package",
            "source": "docs/evaluation/DEMO_FINAL_V2_PACKAGE.md",
            "use": "Use as the current index for the v2 source-version constrained evaluation, gap triage, matcher recall diagnostic, and transparency export.",
        },
        {
            "table": "Demo-final v2 source-version evaluation",
            "source": "docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_VERSION_EVALUATION.md",
            "use": "Use to report the 106-case v2 rerun with exact emitted rows, zero wrong-version emitted rows, and the remaining source-gap denominator.",
        },
        {
            "table": "Demo-final v2 source-gap triage",
            "source": "docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_GAP_TRIAGE.md",
            "use": "Use to separate v2 source gaps into metadata/source-only, alias/boundary, missing-reference, and matcher-recall buckets.",
        },
        {
            "table": "Demo-final v2 matcher recall diagnostics",
            "source": "docs/evaluation/DEMO_FINAL_V2_MATCHER_RECALL_DIAGNOSTICS.md",
            "use": "Use to show which exact source-version gaps can be surfaced only as report-only source-context suggestions.",
        },
        {
            "table": "Demo-final transparency export",
            "source": "docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md",
            "use": "Use as the row-level JSON/CSV export index for dataset roles, source coverage classes, emitted result classes, version mismatch reasons, and vulnerability claim strength.",
        },
        {
            "table": "Final v2 thesis results section",
            "source": "docs/thesis/FINAL_V2_RESULTS_SECTION.md",
            "use": "Use as thesis-ready prose that separates the normal emitted-version metric from the v2 source-known upper-bound lane.",
        },
        {
            "table": "Final v2 demo runbook",
            "source": "docs/evaluation/FINAL_DEMO_RUNBOOK_V2.md",
            "use": "Use for the final supervisor/defense demo flow, exact opening wording, artifact order, and hard-question answers.",
        },
        {
            "table": "Final demo checklist",
            "source": "docs/evaluation/FINAL_DEMO_CHECKLIST.md",
            "use": "Use as the day-of-defense checklist for deck path, opening artifacts, exact numbers, and commands to avoid live.",
        },
        {
            "table": "Final report readiness package",
            "source": "docs/thesis/FINAL_REPORT_READINESS_PACKAGE.md",
            "use": "Use for final report assembly, figure placement, screenshot selection, wording guardrails, and submission checks.",
        },
        {
            "table": "Post-100 real APK optimization plan",
            "source": "docs/planning/RESEARCH_BACKED_REAL_APK_OPTIMIZATION_PLAN.md",
            "use": "Use as the research-backed execution roadmap for coverage-first reference DB growth, wrong-version rows, missing-source rows, guarded promotion, and dashboard improvement.",
        },
        {
            "table": "No-Maven-signal audit",
            "source": "docs/evaluation/NO_MAVEN_SIGNAL_AUDIT.md",
            "use": "Use to explain why the four no-Maven rows stay outside accuracy metrics and how AndroidX identity misses differ from Mastodon's fork-family boundary.",
        },
        {
            "table": "No-Maven AndroidX report-only experiment",
            "source": "docs/evaluation/NO_MAVEN_ANDROIDX_REPORT_ONLY_EXPERIMENT.md",
            "use": "Use as dashboard seed evidence for six source-backed AndroidX report-only candidates with zero SBOM or source-validation metric changes.",
        },
        {
            "table": "Mastodon fork-family report-only audit",
            "source": "docs/evaluation/MASTODON_FORK_FAMILY_REPORT_ONLY_AUDIT.md",
            "use": "Use as dashboard seed evidence for `me.grishka.litex:*` fork-family candidates and weak direct Gson evidence without converting them into SBOM claims.",
        },
        {
            "table": "Limitation boundary dashboard",
            "source": "docs/evaluation/LIMITATION_BOUNDARY_DASHBOARD.md",
            "use": "Use as the dashboard-ready summary separating explicit limitation rows from hybrid source-validated framework/native boundary evidence.",
        },
        {
            "table": "Wrong-version optimization dashboard",
            "source": "docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md",
            "use": "Use as the ranked, research-backed queue for the 636 emitted wrong-version rows, grouped by APK, coordinate family, source version, and guarded next action.",
        },
        {
            "table": "Wrong-version P1 coroutines experiment",
            "source": "docs/evaluation/WRONG_VERSION_P1_COROUTINES_ANDROID_1_6_4_EXPERIMENT.md",
            "use": "Use as the guarded-source-version example where 20 target rows improve but shared DB promotion is rejected because current controls regress.",
        },
        {
            "table": "Dataset coverage matrix",
            "source": "docs/evaluation/DATASET_COVERAGE_MATRIX.md",
            "use": "Justify APK selection by classification instead of convenience.",
        },
        {
            "table": "Next real APK growth queue",
            "source": "docs/evaluation/NEXT_REAL_APK_GROWTH_QUEUE.md",
            "use": "Justify why the next real APK batch must be selected by class balance before Phase 6 or ML experiments.",
        },
        {
            "table": "Real APK growth batch V2",
            "source": "docs/evaluation/REAL_APK_GROWTH_BATCH_V2.md",
            "use": "Show the 8-app category-balanced smoke/report batch while keeping it separate from source-validated accuracy claims.",
        },
        {
            "table": "Controlled generated batch",
            "source": "data/results/evaluation/generated-apk-category-batch.md",
            "use": "Show controlled coverage by clear/R8/multidex category.",
        },
        {
            "table": "Paper-to-implementation traceability",
            "source": "docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md",
            "use": "Justify each MVP feature as a paper-backed adaptation with implementation and evaluation evidence.",
        },
        {
            "table": "Paper-backed improvement notes",
            "source": "docs/thesis/PAPER_BACKED_MVP_IMPROVEMENT_NOTES.md",
            "use": "Preserve current cons, improvement policies, and thesis framing for uncertainty.",
        },
        {
            "table": "Experiment decision ledger",
            "source": "docs/thesis/EXPERIMENT_DECISION_LEDGER.md",
            "use": "Use as the central paper-ready ledger for accepted, rejected, disabled, blocked, and deferred methods.",
        },
        {
            "table": "MVP cons and improvement plan",
            "source": "docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md",
            "use": "Use as the operational plan for weak points, safe next actions, blocked work, and rejected global changes.",
        },
        {
            "table": "R8 obfuscation method selection",
            "source": "docs/research/R8_OBFUSCATION_METHOD_SELECTION.md",
            "use": "Use as the research gate for the final R8/obfuscation con and as the justification for classifier-first, evaluation-first integration.",
        },
        {
            "table": "R8 obfuscation execution plan",
            "source": "docs/planning/R8_OBFUSCATION_CON_EXECUTION_PLAN.md",
            "use": "Use as the implementation roadmap for the best-of-tools R8 layer, from report-only classifier fields to scoped scoring.",
        },
        {
            "table": "R8 obfuscation diagnostics",
            "source": "docs/evaluation/R8_OBFUSCATION_DIAGNOSTICS.md",
            "use": "Use as the scoring-unchanged diagnostic summary of controlled R8 coverage, real R8/minified partial cases, hidden-code boundaries, and classifier gaps.",
        },
        {
            "table": "AI-assisted R8 method selection",
            "source": "docs/research/AI_R8_ASSISTED_METHOD_SELECTION.md",
            "use": "Use as the Phase 6 research gate explaining why ML/DL assistance is report-only and not exact SBOM/version/CVE authority.",
        },
        {
            "table": "AI R8 assistant diagnostics",
            "source": "docs/evaluation/AI_R8_ASSISTANT_DIAGNOSTICS.md",
            "use": "Use as the Phase 6A dataset, model-status, suggestion, and limitation artifact for the classical ML report-only assistant.",
        },
        {
            "table": "AI R8 assistant compact summary",
            "source": "docs/evaluation/AI_R8_ASSISTANT_SUMMARY.md",
            "use": "Use as the compact thesis/demo export for AI R8 dataset size, model metrics, baselines, suggestions, and guardrails.",
        },
        {
            "table": "AI R8 final evaluation",
            "source": "docs/evaluation/AI_R8_FINAL_EVALUATION.md",
            "use": "Use as the single Phase 6 ML/DL evidence entry point combining RandomForest metrics, ablation, Transformer prototype metrics, and the report-only guardrail proof.",
        },
        {
            "table": "AI R8 report-only demo",
            "source": "docs/evaluation/AI_R8_REPORT_ONLY_DEMO.md",
            "use": "Use as the opt-in report proof that AI suggestions add a report section while preserving detected components and normalized SBOM content.",
        },
        {
            "table": "Hybrid AI production reporting",
            "source": "docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md",
            "use": "Use as the production report-only integration proof for `generate-report --include-hybrid-ai-assistance`, combining router, RandomForest, and Transformer-status evidence without changing matcher/SBOM/CVE outputs.",
        },
        {
            "table": "AI R8 DL prototype",
            "source": "docs/evaluation/AI_R8_DL_PROTOTYPE.md",
            "use": "Use as the Phase 6B LibAttention-inspired trained Transformer prototype, isolated from production reports.",
        },
        {
            "table": "Hybrid matcher router",
            "source": "docs/evaluation/HYBRID_MATCHER_ROUTER_V1.md",
            "use": "Use as the report-only comparison between the current matcher and research tool-family strategies, with current hard rows routed to safe experiment profiles.",
        },
        {
            "table": "Version-band rerank experiment",
            "source": "docs/evaluation/VERSION_BAND_RERANK_EXPERIMENT.md",
            "use": "Use as the first router-driven report-only rerank experiment: source-known fixability for wrong-version rows, exact controls, and false-positive controls.",
        },
        {
            "table": "APK-only version-band reranker v2",
            "source": "docs/evaluation/VERSION_BAND_APK_RERANKER_V2.md",
            "use": "Use as the promotion-blocking APK-only reranker diagnostic showing source-free candidate visibility and strict sibling-era gating results.",
        },
        {
            "table": "Version-band candidate expansion v3",
            "source": "docs/evaluation/VERSION_BAND_CANDIDATE_EXPANSION_V3.md",
            "use": "Use as the promotion-gate artifact combining source-known opportunity, APK-only rejection, and deep same-coordinate candidate-expansion pilot evidence.",
        },
        {
            "table": "R8 structural recall experiment",
            "source": "docs/evaluation/R8_STRUCTURAL_RECALL_EXPERIMENT.md",
            "use": "Use as the router-driven hard-R8/matcher-recall lane showing source-context structural recall candidates, same-coordinate controls, and why the result stays report-only.",
        },
        {
            "table": "R8 APK-only structural promotion gate",
            "source": "docs/evaluation/R8_APK_STRUCTURAL_PROMOTION_GATE.md",
            "use": "Use as the APK-only evidence gate showing that strong structural rows exist, but zero rows satisfy production promotion controls today.",
        },
        {
            "table": "R8 multi-scale feature diagnostics",
            "source": "docs/evaluation/R8_MULTISCALE_FEATURE_DIAGNOSTICS.md",
            "use": "Use as the Phase 3 proof that call-chain, basic-block, class-neighbor, field-operation, and literal/context features are extracted and reportable while scoring remains unchanged.",
        },
        {
            "table": "R8 Phase 4 scoped experiment diagnostics",
            "source": "docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md",
            "use": "Use as the Phase 4 proof that the offline multi-scale blend stays diagnostic-only because controlled and real source-validated rows would regress.",
        },
        {
            "table": "R8 Phase 5 scoped trigger diagnostics",
            "source": "docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md",
            "use": "Use as the Phase 5 experiment-only proof that a narrow trigger keeps four target improvements without triggered regressions in the current artifact, while default scoring remains unchanged.",
        },
        {
            "table": "R8 Phase 5 trigger control validation",
            "source": "docs/evaluation/R8_PHASE5_TRIGGER_CONTROL_VALIDATION.md",
            "use": "Use as the current-control gate showing the scoped trigger blocks controlled, clean, and boundary rows and is not wired into production code.",
        },
        {
            "table": "R8 Phase 5 report evidence",
            "source": "docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md",
            "use": "Use as the opt-in report-surface proof that four target suggestions remain separate from official MVP selected versions and SBOM artifacts.",
        },
        {
            "table": "R8 optimization-aware diagnostics",
            "source": "docs/evaluation/R8_OPTIMIZATION_AWARE_DIAGNOSTICS.md",
            "use": "Use as the decision gate showing why optimization-aware R8/minified logic stays diagnostic/report-only and why confidence/ambiguity policy is the next safe step.",
        },
        {
            "table": "R8 minified confidence policy diagnostics",
            "source": "docs/evaluation/R8_MINIFIED_CONFIDENCE_POLICY_DIAGNOSTICS.md",
            "use": "Use as the report-only policy gate classifying minified/R8 ambiguity labels without changing selected versions, SBOM components, vulnerability labels, or source-validation metrics.",
        },
        {
            "table": "R8 minified confidence report evidence",
            "source": "docs/evaluation/R8_MINIFIED_CONFIDENCE_REPORT_EVIDENCE.md",
            "use": "Use as the generated-report proof that minified/R8 confidence labels surface only as report-only wording while preserving official selected versions and SBOM artifacts.",
        },
        {
            "table": "Version uncertainty reporting",
            "source": "docs/evaluation/VERSION_UNCERTAINTY_REPORTING.md",
            "use": "Use as the report-output proof that near-tie, low-confidence, and single-reference boundary rows are explained without changing selected versions or SBOM components.",
        },
        {
            "table": "R8 obfuscation continuation prompt",
            "source": "docs/codex/R8_OBFUSCATION_CON_CONTINUATION_PROMPT.md",
            "use": "Use to resume the con in a later Codex session without losing the paper-backed plan or guardrails.",
        },
        {
            "table": "Version-tie reranker diagnostics",
            "source": "docs/evaluation/VERSION_TIE_RERANKER_DIAGNOSTICS.md",
            "use": "Use as diagnostic no-change evidence for the current AndroidX/Kotlin version-band ties.",
        },
        {
            "table": "POM coherence diagnostics",
            "source": "docs/evaluation/POM_COHERENCE_DIAGNOSTICS.md",
            "use": "Use as diagnostic no-change evidence for dependency metadata and POM coherence ties.",
        },
        {
            "table": "Artifact-family diagnostics",
            "source": "docs/evaluation/ARTIFACT_FAMILY_DIAGNOSTICS.md",
            "use": "Use as no-new-rule evidence for scoped Okio, OkHttp, and Lifecycle family handling.",
        },
        {
            "table": "Opcode/API signal diagnostics",
            "source": "docs/evaluation/OPCODE_API_SIGNAL_DIAGNOSTICS.md",
            "use": "Use as no-global-weight evidence for API/member-reference and opcode tri-gram signals.",
        },
        {
            "table": "Native boundary diagnostics",
            "source": "docs/evaluation/NATIVE_BOUNDARY_DIAGNOSTICS.md",
            "use": "Use as hash-only file-component evidence for native .so scope boundaries.",
        },
        {
            "table": "K-9 blocker diagnostics",
            "source": "docs/evaluation/K9_BLOCKER_DIAGNOSTICS.md",
            "use": "Use as K-9 rescue evidence: failed included-build attempts, plugin-lite dependency-tree capture, and source-validated partial admission.",
        },
        {
            "table": "Hidden DEX diagnostics",
            "source": "docs/evaluation/HIDDEN_DEX_DIAGNOSTICS.md",
            "use": "Use as limitation evidence for nonstandard DEX and dynamic-loading boundaries.",
        },
        {
            "table": "OSV source-validation triage",
            "source": "docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md",
            "use": "Use to separate source-confirmed vulnerability evidence from source-version-mismatch and report-only OSV findings.",
        },
        {
            "table": "External scanner validation status",
            "source": "docs/evaluation/EXTERNAL_SCANNER_VALIDATION_STATUS.md",
            "use": "Use as generated readiness evidence for optional cyclonedx-cli, Trivy, Grype, Syft, and cdxgen validation.",
        },
        {
            "table": "External scanner validation results",
            "source": "docs/evaluation/EXTERNAL_SCANNER_VALIDATION.md",
            "use": "Use as Grype/Trivy comparison evidence for clean, vulnerable, and partial SBOM targets.",
        },
        {
            "table": "Source-version candidate queue",
            "source": "docs/evaluation/SOURCE_VERSION_CANDIDATE_QUEUE.md",
            "use": "Use before any future reference DB experiment to track target benefit, control regressions, and promotion decisions.",
        },
        {
            "table": "Guarded reference-DB promotion workflow",
            "source": "docs/evaluation/GUARDED_REFERENCE_DB_PROMOTION_WORKFLOW.md",
            "use": "Use as the generated policy table for isolated candidate-version comparisons, singleton-safe promotions, bundle-scoped evidence, and app-specific regression guardrails.",
        },
        {
            "table": "Coarse-to-fine candidate-pruning diagnostics",
            "source": "docs/evaluation/COARSE_TO_FINE_PRUNING_DIAGNOSTICS.md",
            "use": "Use as diagnostic-only evidence for pre-reportability candidate pressure and the next offline family-identity prefilter simulation.",
        },
        {
            "table": "Family-identity prefilter proxy simulation",
            "source": "docs/evaluation/FAMILY_IDENTITY_PREFILTER_SIMULATION.md",
            "use": "Use as rejected-simple-proxy evidence: package/class family pruning loses tracked source families at every reducing margin, so a stronger offline signal is required.",
        },
        {
            "table": "Composite family-shortlist proxy simulation",
            "source": "docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_SIMULATION.md",
            "use": "Use as pre-production proxy evidence for the balanced dependency/literal-aware shortlist candidate and its required live offline validation gate.",
        },
        {
            "table": "Composite family-shortlist live validation",
            "source": "docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_LIVE_VALIDATION.md",
            "use": "Use as clean live recomputation evidence for the balanced shortlist opt-in candidate; default production matching remains unchanged until a separate opt-in matcher experiment passes fresh controls.",
        },
        {
            "table": "Composite family-shortlist opt-in matcher experiment",
            "source": "docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_OPT_IN_MATCHER_EXPERIMENT.md",
            "use": "Use as full all-case opt-in control evidence that the shortlist is default-off, opt-in-only, and reportable-output-clean across controlled and real APK cases.",
        },
        {
            "table": "Composite family-shortlist default-promotion readiness",
            "source": "docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_READINESS.md",
            "use": "Use as readiness evidence for promoting the shortlist only after full live and opt-in controls pass without reportable selected-version drift.",
        },
        {
            "table": "Composite family-shortlist default-promotion verification",
            "source": "docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_VERIFICATION.md",
            "use": "Use as the post-promotion proof that the shortlist is now default-on, the disable flag reproduces the baseline, and regression checks passed.",
        },
        {
            "table": "Class-correspondence pruning diagnostics",
            "source": "docs/evaluation/CLASS_CORRESPONDENCE_PRUNING_DIAGNOSTICS.md",
            "use": "Use as diagnostic-only evidence that class/package/method correspondence does not add a safer or stronger pruning lane beyond the promoted composite shortlist.",
        },
        {
            "table": "Assembled final report draft",
            "source": "docs/thesis/PFE_FINAL_REPORT_ASSEMBLED.md",
            "use": "Use as the main university-report starting point before applying the final template.",
        },
        {
            "table": "Presentation deck script",
            "source": "docs/thesis/PRESENTATION_DECK_SCRIPT.md",
            "use": "Use as the slide-by-slide defense script with claims, proof objects, and speaker notes.",
        },
        {
            "table": "Editable defense deck",
            "source": "outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/output/apk-sbom-defense-deck.pptx",
            "use": "Use as the current editable PPTX defense deck before applying any university template.",
        },
        {
            "table": "Defense deck QA scorecard",
            "source": "outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/qa/comeback-scorecard.txt",
            "use": "Keep the rendered-deck QA notes and runtime caveat with the generated deck artifact.",
        },
    ]


def build_figure_plan() -> list[dict[str, str]]:
    return [
        {
            "figure": "System architecture pipeline",
            "source": "docs/architecture/MVP_ARCHITECTURE.md",
            "caption": "Static APK-to-SBOM pipeline from APK extraction to CycloneDX and OSV reporting.",
        },
        {
            "figure": "Evaluation layer diagram",
            "source": "docs/evaluation/DATASET_DESIGN.md",
            "caption": "Controlled, source-validated, smoke, and limitation layers with allowed metrics.",
        },
        {
            "figure": "Generated report screenshot",
            "source": "data/results/report-real-f-droid-final-demo-osv/report.html",
            "caption": "Example report showing detected Maven components, confidence, evidence, native files, and OSV result.",
        },
        {
            "figure": "Clean and vulnerable OSV examples",
            "source": "docs/dev/RUNBOOK.md",
            "caption": "Negative OSV result on calibrated F-Droid and positive HIGH advisories on controlled Jackson Databind.",
        },
        {
            "figure": "Real APK OSV triage",
            "source": "docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md",
            "caption": "Real APK OSV findings grouped by source-confirmed, source-version-mismatch, and report-only evidence strength.",
        },
        {
            "figure": "Final v2 package table",
            "source": "docs/evaluation/DEMO_FINAL_V2_PACKAGE.md",
            "caption": "Source-version constrained v2 evaluation metrics and transparent remaining gap categories.",
        },
        {
            "figure": "Defense deck contact sheet",
            "source": "outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/preview/contact-sheet.png",
            "caption": "Visual overview of the final 12-slide defense deck.",
        },
    ]


def build_case_artifacts(cases: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for case in cases:
        validation = case.get("validation") or {}
        checked = int(validation.get("checked_components") or 0)
        confirmed = int(validation.get("confirmed") or 0)
        case_id = str(case.get("case_id", ""))
        rows.append(
            {
                "case": str(case.get("name", "")),
                "role": str(case.get("role", "")),
                "confirmed": f"{confirmed}/{checked}" if checked else "not counted",
                "report": normalize_path(case.get("report_path", "")),
                "validation": normalize_path(case.get("validation_path", "")),
                "proof": resolve_proof_path(case_id, case.get("proof_path", "")),
                "interpretation": str(case.get("interpretation", "")),
            }
        )
    return rows


def resolve_proof_path(case_id: str, path: Any) -> str:
    normalized = normalize_path(path)
    if normalized and Path(normalized).exists():
        return normalized
    checklist = Path("data/results/evaluation/real-apk-proof") / case_id / "proof-checklist.md"
    if checklist.exists():
        return normalize_path(checklist)
    current_batch_checklist = (
        Path("data/results/evaluation/real-apk-proof-current-batch")
        / case_id
        / "proof-checklist.md"
    )
    if current_batch_checklist.exists():
        return normalize_path(current_batch_checklist)
    return normalized


def build_demo_package() -> list[dict[str, str]]:
    return [
        {
            "item": "Clean real APK report",
            "path": "data/results/report-real-f-droid-final-demo-osv/report.html",
            "talking_point": "Calibrated real APK, source-confirmed emitted versions, OSV returns 0 vulnerabilities.",
        },
        {
            "item": "Clean real APK SBOM",
            "path": "data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json",
            "talking_point": "CycloneDX JSON with Maven PURLs and evidence/confidence properties.",
        },
        {
            "item": "Clean source validation",
            "path": "data/results/source-validation/fdroid-final-demo-osv/source-validation.md",
            "talking_point": "23/23 emitted Maven versions confirmed against the source dependency tree.",
        },
        {
            "item": "Vulnerable controlled report",
            "path": "data/results/demo-osv-vulnerable-jackson-databind/report.html",
            "talking_point": "Controlled vulnerable Jackson Databind fixture with 3 confirmed HIGH advisories.",
        },
        {
            "item": "Real APK OSV triage",
            "path": "docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md",
            "talking_point": "Current real APK OSV findings are separated into source-confirmed, source-version-mismatch, and report-only evidence.",
        },
        {
            "item": "Source-aware real APK vulnerability report",
            "path": "data/results/report-real-osmand/report.html",
            "talking_point": "OsmAnd report shows Jackson/Gson OSV advisories as potential source-version-mismatch findings after applying source validation.",
        },
        {
            "item": "Evaluation tables",
            "path": "docs/evaluation/THESIS_EVALUATION_TABLES.md",
            "talking_point": "Clean/partial/blocked/limitation split and emitted Maven version confirmation rate.",
        },
        {
            "item": "Demo-final v2 package",
            "path": "docs/evaluation/DEMO_FINAL_V2_PACKAGE.md",
            "talking_point": "Current v2 source-version constrained package: 106/106 cases, 6772/6772 exact emitted rows, 0 wrong-version emitted rows, and explicit gap/recall transparency.",
        },
        {
            "item": "Demo-final transparency export",
            "path": "data/results/evaluation/demo-final-transparency-export.json",
            "talking_point": "Row-level JSON for exporting dataset roles, source coverage classes, emitted result classes, and vulnerability claim strength.",
        },
        {
            "item": "Final v2 results thesis section",
            "path": "docs/thesis/FINAL_V2_RESULTS_SECTION.md",
            "talking_point": "Copy-ready thesis wording for the v2 upper-bound lane, with explicit warnings against calling it APK-only accuracy.",
        },
        {
            "item": "Final v2 demo runbook",
            "path": "docs/evaluation/FINAL_DEMO_RUNBOOK_V2.md",
            "talking_point": "Defense flow that shows APK-to-SBOM, CVE lookup, normal emitted-version metrics, v2 upper-bound results, and transparency gaps.",
        },
        {
            "item": "Final demo checklist",
            "path": "docs/evaluation/FINAL_DEMO_CHECKLIST.md",
            "talking_point": "Day-of-defense checklist with the deck path, exact numbers, safe commands, and commands to avoid live.",
        },
        {
            "item": "Hybrid matcher router",
            "path": "docs/evaluation/HYBRID_MATCHER_ROUTER_V1.md",
            "talking_point": "Report-only comparison of matcher strategies from the literature and row-level routing of current hard cases to scoped experiment profiles.",
        },
        {
            "item": "Hybrid AI production reporting",
            "path": "docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md",
            "talking_point": "Production `generate-report --include-hybrid-ai-assistance` wiring that surfaces the router, ML suggestions, and DL status as report-only evidence while keeping matcher/SBOM/CVE behavior unchanged.",
        },
        {
            "item": "Version-band rerank experiment",
            "path": "docs/evaluation/VERSION_BAND_RERANK_EXPERIMENT.md",
            "talking_point": "First router-driven source-known rerank experiment: 565 scoped wrong-version rows are fixable in the source-known lane while exact and false-positive controls stay visible.",
        },
        {
            "item": "APK-only version-band reranker v2",
            "path": "docs/evaluation/VERSION_BAND_APK_RERANKER_V2.md",
            "talking_point": "Source-free reranker prototype that blocks promotion today: 0 safe fixes and only 44/582 scoped wrong-version rows with the source version visible as a baseline alternative.",
        },
        {
            "item": "Version-band candidate expansion v3",
            "path": "docs/evaluation/VERSION_BAND_CANDIDATE_EXPANSION_V3.md",
            "talking_point": "Promotion-gate diagnostic showing that even deep same-coordinate candidate expansion selected an old wrong Activity version, so version-band reranking stays unpromoted.",
        },
        {
            "item": "R8 structural recall experiment",
            "path": "docs/evaluation/R8_STRUCTURAL_RECALL_EXPERIMENT.md",
            "talking_point": "Router-driven R8 structural recall lane: 1,000 source-context report-only candidates are useful for transparency, while 814 same-coordinate control-risk rows block automatic SBOM promotion.",
        },
        {
            "item": "Final report readiness package",
            "path": "docs/thesis/FINAL_REPORT_READINESS_PACKAGE.md",
            "talking_point": "Final report assembly checklist with figure placement, screenshot plan, wording guardrails, and submission checks.",
        },
    ]


def build_final_report_checklist() -> list[dict[str, str]]:
    return [
        {
            "section": "Introduction",
            "status": "ready",
            "next_action": "Start from `docs/thesis/PFE_FINAL_REPORT_ASSEMBLED.md`, then adapt wording to the university template and add local motivation if required.",
        },
        {
            "section": "State of the art",
            "status": "ready-source-material",
            "next_action": "Condense `papers/data/state_of_the_art.md`, `docs/research/EVIDENCE_MAP.md`, and `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md` into the final chapter.",
        },
        {
            "section": "Architecture and implementation",
            "status": "ready",
            "next_action": "Use `docs/architecture/MVP_ARCHITECTURE.md`, the implementation map in `docs/thesis/PFE_REPORT_DRAFT.md`, and the traceability matrix.",
        },
        {
            "section": "Evaluation",
            "status": "ready",
            "next_action": "Use `docs/evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md` for the normal clean/partial split, then add `docs/thesis/FINAL_V2_RESULTS_SECTION.md` as the final source-known upper-bound addendum.",
        },
        {
            "section": "Limitations",
            "status": "ready",
            "next_action": "Use `docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md` and keep native-heavy, hidden-DEX, scanner-tool, and K-9 validation-copy caveats visible.",
        },
        {
            "section": "Presentation",
            "status": "editable-deck-ready",
            "next_action": "Use `outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/output/apk-sbom-defense-deck.pptx`, then apply university template details, names, screenshots, and the v2 result wording from `docs/evaluation/FINAL_DEMO_RUNBOOK_V2.md`.",
        },
        {
            "section": "Final packaging",
            "status": "ready-for-template",
            "next_action": "Use `docs/thesis/FINAL_REPORT_READINESS_PACKAGE.md` to fill cover fields, insert figures/screenshots, check wording guardrails, and export the final university document.",
        },
    ]


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Thesis Artifact Index",
        "",
        "Generated by `scripts/build_thesis_artifact_index.py`.",
        "",
        "This file maps thesis claims to concrete project artifacts. Use it while writing the final report, preparing slides, or answering supervisor questions about evidence.",
        "",
        "## Current Numbers",
        "",
        "| Slice | Result |",
        "|---|---|",
        f"| Controlled APKs | {payload['summary']['controlled']} |",
        f"| Clean source-validated real APKs | {payload['summary']['clean_real']} |",
        f"| Partial source-validated real APKs | {payload['summary']['partial_real']} |",
        f"| All source-validated real APKs | {payload['summary']['overall_real']} |",
        f"| Full source dependency denominator | {payload['summary']['source_denominator_recall']} |",
        f"| Source-observed reference growth inputs | {payload['summary']['source_observed_reference_inputs']} |",
        "",
        "## Claim Evidence",
        "",
        "| Claim | Evidence | Scope | Limitation | Key artifacts |",
        "|---|---|---|---|---|",
    ]
    for row in payload["claim_evidence"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["claim"]),
                    md(row["evidence"]),
                    md(row["scope"]),
                    md(row["limitation"]),
                    "<br>".join(f"`{artifact}`" for artifact in row["artifacts"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Table Sources",
            "",
            "| Table | Source | Use |",
            "|---|---|---|",
        ]
    )
    for row in payload["table_sources"]:
        lines.append(f"| {md(row['table'])} | `{row['source']}` | {md(row['use'])} |")

    lines.extend(
        [
            "",
            "## Figure Plan",
            "",
            "| Figure | Source | Caption |",
            "|---|---|---|",
        ]
    )
    for row in payload["figure_plan"]:
        lines.append(f"| {md(row['figure'])} | `{row['source']}` | {md(row['caption'])} |")

    lines.extend(
        [
            "",
            "## Per-APK Evidence",
            "",
            "| Case | Role | Confirmed | Report | Validation | Proof | Interpretation |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for row in payload["case_artifacts"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["case"]),
                    md(row["role"]),
                    row["confirmed"],
                    optional_path(row["report"]),
                    optional_path(row["validation"]),
                    optional_path(row["proof"]),
                    md(row["interpretation"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Demo Package",
            "",
            "| Item | Path | Talking point |",
            "|---|---|---|",
        ]
    )
    for row in payload["demo_package"]:
        lines.append(f"| {md(row['item'])} | `{row['path']}` | {md(row['talking_point'])} |")

    lines.extend(
        [
            "",
            "## Writing Guardrails",
            "",
        ]
    )
    for item in payload["writing_guardrails"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Final Report Checklist",
            "",
            "| Section | Status | Next action |",
            "|---|---|---|",
        ]
    )
    for row in payload["final_report_checklist"]:
        lines.append(f"| {md(row['section'])} | {md(row['status'])} | {md(row['next_action'])} |")

    lines.append("")
    return "\n".join(lines)


def optional_path(path: str) -> str:
    return f"`{path}`" if path else "n/a"


def unique(values: list[str]) -> list[str]:
    seen = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return seen


def normalize_path(value: Any) -> str:
    if not value:
        return ""
    return str(value).replace("\\", "/")


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def format_reference_coverage_summary(summary: dict[str, Any]) -> str:
    if not summary:
        return "n/a"
    return (
        f"{summary['source_dependencies_emitted_exact']}/"
        f"{summary['source_dependency_pairs']} source dependency coordinate+version rows "
        f"emitted exactly ({summary['end_to_end_exact_source_recall_percent']}%); "
        f"shared DB exact-version coverage is "
        f"{summary['reference_exact_version_covered_source_pairs']}/"
        f"{summary['source_dependency_pairs']} "
        f"({summary['reference_exact_version_coverage_percent']}%)"
    )


def format_source_observed_catalog_summary(summary: dict[str, Any]) -> str:
    if not summary:
        return "n/a"
    return (
        f"{summary['source_observed_coordinates']} coordinates / "
        f"{summary['source_version_slots']} source-version slots; "
        f"{summary['buildable_coordinates']} buildable coordinates / "
        f"{summary['buildable_source_version_slots']} buildable source-version slots; "
        f"{summary['skipped_non_bytecode_coordinates']} metadata-only skips"
    )


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return read_json(path)


if __name__ == "__main__":
    raise SystemExit(main())
