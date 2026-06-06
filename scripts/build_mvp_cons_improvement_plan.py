from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_THESIS_TABLES_JSON = Path("data/results/evaluation/thesis-evaluation-tables.json")
DEFAULT_VERSION_TIES_JSON = Path("data/results/experiments/version-band-tie-evidence.json")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/mvp-cons-improvement-plan.json")
DEFAULT_OUTPUT_DOC = Path("docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md")


PLAN_ITEMS: list[dict[str, Any]] = [
    {
        "priority": 1,
        "weak_point": "Nearby AndroidX/Kotlin version bands are fragile.",
        "evidence": "The diagnostic reranker report inspects 19 risky version-band tie rows and finds no clean independent signal that justifies a global matcher scoring change. Later opt-in diagnostics add narrower evidence: AppCompat/Core flags 7/13 newly introduced low-risk experiment mismatch rows for confidence downgrade while blocking 0/9 resolved target rows, and Lifecycle family separation marks 2/5 introduced Lifecycle public-coordinate claims as downgrade candidates while keeping the NewPipe patch near-tie ambiguous. Both remain experiment-only.",
        "paper_basis": "SAD, LibMD, TPL-Benchmark, LibHunter, LibAttention, and ObfDetector all support treating exact version recovery as harder than identity recovery.",
        "current_policy": "Keep identity and version confidence separate, export ambiguous version sets, and avoid generic newer-version rules.",
        "safe_next_action": "Completed for the current MVP: keep the diagnostic reports and opt-in report-only annotations as no-change evidence; require a fresh current-control matrix before any scoped scorer change.",
        "status": "completed",
        "global_promotion": "not allowed without a fresh current-control matrix",
        "artifacts": [
            "docs/evaluation/VERSION_BAND_TIE_EVIDENCE.md",
            "docs/evaluation/VERSION_TIE_RERANKER_DIAGNOSTICS.md",
            "data/results/experiments/version-band-tie-evidence.json",
            "data/results/experiments/version-tie-reranker-diagnostics.json",
            "docs/evaluation/LOW_RISK_VERSION_BAND_TRIGGER_DIAGNOSTICS.md",
            "data/results/experiments/low-risk-version-band-trigger-diagnostics.json",
            "docs/evaluation/LIFECYCLE_FAMILY_SEPARATION_DIAGNOSTICS.md",
            "data/results/experiments/lifecycle-family-separation-diagnostics.json",
            "src/apk_sbom/version_band_experiment.py",
            "src/apk_sbom/lifecycle_family_experiment.py",
            "src/apk_sbom/report.py",
            "src/apk_sbom/sbom.py",
            "src/apk_sbom/matcher.py",
        ],
    },
    {
        "priority": 1,
        "weak_point": "Reference DB coverage strongly controls exact version recovery.",
        "evidence": "The source-version candidate queue records 13 earlier source-used candidates with target cases, known regressed controls, and promotion decisions: 4 rejected global regressions, 4 hold bytecode-prefers-current, 1 hold conflicting signals, 2 hold ambiguity-only, and 2 experiment-only coverage gaps. The low-risk APK follow-up adds a separate 10-version source-used experiment DB: it resolves 9 target mismatch rows but introduces 13 new mismatch rows elsewhere. Narrow checks keep `androidx.recyclerview:recyclerview@1.0.0` and `androidx.lifecycle:lifecycle-runtime@2.1.0` experiment-only because they regress NewPipe and F-Droid/NewPipe/KDE Connect/Aegis respectively.",
        "paper_basis": "LibScout-style reference profiles require coverage; TPL-Benchmark warns against overfitted datasets and cherry-picked results.",
        "current_policy": "Promote only source-used versions that improve a target and do not regress current controls.",
        "safe_next_action": "Completed for the current MVP guardrail: keep the queue regenerated after new proof bundles and test only experiment-only gaps in isolated DBs before any shared promotion.",
        "status": "completed",
        "global_promotion": "guarded only",
        "artifacts": [
            "docs/evaluation/SOURCE_VERSION_CANDIDATE_QUEUE.md",
            "data/results/experiments/source-version-candidate-queue.json",
            "configs/libraries.calibration.json",
            "scripts/filter_reference_db.py",
            "scripts/compare_experiment_summaries.py",
            "docs/evaluation/LOW_RISK_SOURCE_VERSION_EXPERIMENT.md",
            "docs/evaluation/LOW_RISK_VERSION_BAND_DIAGNOSTICS.md",
            "data/results/experiments/low-risk-version-band-diagnostics.json",
            "scripts/evaluate_low_risk_source_versions.py",
            "scripts/build_low_risk_version_band_diagnostics.py",
        ],
    },
    {
        "priority": 1,
        "weak_point": "App-specific calibration can be unsafe globally.",
        "evidence": "Activity 1.9.2 and ViewPager2 1.1.0-beta02 improve Nextcloud but regress control apps; generic newer-near-tie selection also creates false flips.",
        "paper_basis": "Systematic Assessment and TPL-Benchmark support cross-app validation rather than single-app success stories.",
        "current_policy": "Preserve app-specific wins as experiments, not official shared DB behavior, unless controls stay clean.",
        "safe_next_action": "Keep rejected or experiment-only candidates in the evidence docs so the thesis can show why they were not hidden or forced.",
        "status": "guardrail",
        "global_promotion": "rejected for known regressing candidates",
        "artifacts": [
            "docs/evaluation/VERSION_BAND_TIE_EVIDENCE.md",
            "data/results/experiments/app-era-coherence-activity-only-vs-current-control.json",
            "data/results/experiments/app-era-coherence-viewpager-beta-only-vs-current-control.json",
        ],
    },
    {
        "priority": 2,
        "weak_point": "Overlapping public, Android-target, and KMP artifact families are hard to resolve.",
        "evidence": "The artifact-family diagnostic found 41 existing scoped disambiguation evidence rows and reviewed 4 risky family/tie rows; all 4 are covered by existing scoped rules, so no new global artifact-family rule is justified. The low-risk Lifecycle separation diagnostic adds report-only evidence for 2 public-coordinate downgrade candidates, 1 patch near-tie, and 2 insufficient-evidence rows without forcing replacement versions.",
        "paper_basis": "LibMD motivates combining bytecode and dependency graph evidence; SBOM/PURL workflows require careful coordinate mapping.",
        "current_policy": "Prefer bytecode-bearing Android target artifacts only when validated, and suppress overlapping family duplicates cautiously.",
        "safe_next_action": "Completed for the current MVP: keep existing scoped Okio, OkHttp, Lifecycle, and Compose handling; require proof-bundle evidence plus a current-control matrix before any new family rule.",
        "status": "completed",
        "global_promotion": "scoped rules only",
        "artifacts": [
            "src/apk_sbom/matcher.py",
            "docs/evaluation/ARTIFACT_FAMILY_DIAGNOSTICS.md",
            "data/results/experiments/artifact-family-diagnostics.json",
            "docs/evaluation/LIFECYCLE_FAMILY_SEPARATION_DIAGNOSTICS.md",
            "data/results/experiments/lifecycle-family-separation-diagnostics.json",
            "docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md",
        ],
    },
    {
        "priority": 2,
        "weak_point": "Dependency metadata helps, but metadata alone is not APK evidence.",
        "evidence": "The POM coherence diagnostic inspects 19 risky version-tie rows: 8 raw-score-too-high, 7 source-pom-unsupported, 3 source-candidate-not-in-reference, and 1 no-extra-pom-support. No row currently justifies a metadata-driven scorer change.",
        "paper_basis": "LibMD dependency-graph ideas support coherence, while SBOM tooling shows metadata should not replace observed APK evidence.",
        "current_policy": "Use POM coherence only as a conservative tie-breaker with independently selected APK-side support.",
        "safe_next_action": "Completed for the current MVP: keep POM coherence diagnostic-only unless a future row has stronger independently selected APK-side dependency support and passes a current-control matrix.",
        "status": "completed",
        "global_promotion": "diagnostic before scoring changes",
        "artifacts": [
            "docs/evaluation/POM_COHERENCE_DIAGNOSTICS.md",
            "data/results/experiments/pom-coherence-diagnostics.json",
            "src/apk_sbom/maven_downloader.py",
            "src/apk_sbom/reference_features.py",
            "src/apk_sbom/matcher.py",
        ],
    },
    {
        "priority": 2,
        "weak_point": "Opcode/API signals can regress if globally weighted.",
        "evidence": "The opcode/API diagnostic consolidates both signal experiments: API-reference weight 0.05 changed no source-validation metrics across 5 cases, while opcode tri-gram weight 0.02 regressed OpenTracks and Conversations across 11 cases with no confirmed-version improvement.",
        "paper_basis": "ATVHunter, LibScan, LibID, SAD, and LibHunter justify opcode/API features, but not unguarded global weights.",
        "current_policy": "Keep global API-reference and opcode tri-gram weights disabled by default.",
        "safe_next_action": "Completed for the current MVP: keep both weights disabled by default and revisit only as a scoped per-coordinate experiment with a fresh current-control matrix.",
        "status": "completed",
        "global_promotion": "rejected for current global weights",
        "artifacts": [
            "docs/evaluation/OPCODE_API_SIGNAL_DIAGNOSTICS.md",
            "data/results/experiments/opcode-api-signal-diagnostics.json",
            "data/results/experiments/api-reference-weight/api-reference-weight-summary.md",
            "data/results/experiments/opcode-ngram-weight/opcode-ngram-weight-summary.md",
            "data/reference_db/reference_features_calibrated_combined_api_refs.sqlite",
            "data/reference_db/reference_features_calibrated_combined_opcode_ngrams.sqlite",
        ],
    },
    {
        "priority": 3,
        "weak_point": "Native libraries are outside Maven version recovery.",
        "evidence": "The native-boundary diagnostic covers 21 native APK cases with 170 native .so files represented as hash-only file components; 17 cases are source-validated native APKs and 4 are boundary or blocked native cases.",
        "paper_basis": "CycloneDX supports file components; native identity/version recovery is a separate research area from DEX Maven TPL detection.",
        "current_policy": "Report .so files as hash-only CycloneDX file components and exclude them from Maven-version accuracy.",
        "safe_next_action": "Completed for the current MVP: keep native-heavy cases as limitation/stress evidence and do not claim native package/version recovery without a separate native-analysis module.",
        "status": "completed",
        "global_promotion": "not applicable",
        "artifacts": [
            "docs/evaluation/NATIVE_BOUNDARY_DIAGNOSTICS.md",
            "data/results/evaluation/native-boundary-diagnostics.json",
            "docs/evaluation/THESIS_EVALUATION_TABLES.md",
            "src/apk_sbom/apk_extractor.py",
            "src/apk_sbom/sbom.py",
        ],
    },
    {
        "priority": 3,
        "weak_point": "K-9 / Thunderbird Android needed a validation-only included-build rescue.",
        "evidence": "K-9 blocker diagnostics now record the bounded failed Gradle attempts plus the successful 2026-06-05 plugin-lite validation copy: fossReleaseRuntimeClasspath was generated and source validation confirmed 5/11 emitted Maven versions, with 6 mismatches and 0 missing.",
        "paper_basis": "Evaluation methodology papers support keeping blocked cases separate from validated accuracy cases.",
        "current_policy": "Count K-9 as source-validated partial, not clean evidence, because the dependency tree came from a validation-only build-system reduction.",
        "safe_next_action": "Completed for the current MVP: preserve the K-9 blocker diagnostics as rescue evidence and use the source-validation JSON for thesis metrics.",
        "status": "completed",
        "global_promotion": "not applicable",
        "artifacts": [
            "docs/evaluation/K9_BLOCKER_DIAGNOSTICS.md",
            "data/results/source-validation/k9-thunderbird-android/k9-blocker-diagnostics.json",
            "docs/evaluation/K9_THUNDERBIRD_PROOF_BUNDLE.md",
            "data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.md",
            "data/results/source-validation/k9-thunderbird-android/fossReleaseRuntimeClasspath.plugin-lite-runtimegraph-composefix.txt",
        ],
    },
    {
        "priority": 3,
        "weak_point": "CVE matching can mislead when version evidence is uncertain.",
        "evidence": "A wrong exact version can create a wrong vulnerability conclusion even when OSV matching works; the real-APK OSV triage and regenerated OsmAnd report show source-version mismatches now downgrade advisories to potential.",
        "paper_basis": "ATVHunter, LibMD, CycloneDX, PURL, and OSV all depend on accurate component/version evidence.",
        "current_policy": "High-confidence exact version findings are confirmed only when source validation does not contradict the APK-selected version; source-version mismatches and report-only findings are potential until validated.",
        "safe_next_action": "Completed for the MVP: `generate-report --source-validation-json ...` writes source-confirmed/source-version-mismatch/source-missing labels into OSV JSON, Markdown, and HTML report output.",
        "status": "completed",
        "global_promotion": "not applicable",
        "artifacts": [
            "src/apk_sbom/vulnerability.py",
            "src/apk_sbom/report.py",
            "src/apk_sbom/cli.py",
            "data/results/demo-osv-vulnerable-jackson-databind/report.html",
            "docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md",
            "data/results/report-real-osmand/report.md",
        ],
    },
    {
        "priority": 3,
        "weak_point": "External SBOM scanner validation needed a reproducible local toolchain.",
        "evidence": "The Docker runtime now has CycloneDX CLI, Trivy, Grype, Syft, cdxgen, node, and npm available. External scanner validation completed 6/6 Grype/Trivy runs and 6/6 CycloneDX schema-validation runs across the clean F-Droid, controlled vulnerable Jackson, and OsmAnd partial SBOM targets.",
        "paper_basis": "CycloneDX, OSV, Trivy, Grype, Syft, and cdxgen motivate interoperable validation and scanner comparison.",
        "current_policy": "Use OSV-first/source-validation-aware vulnerability labels as thesis authority, and treat external scanner results as interoperability comparison evidence.",
        "safe_next_action": "Completed: keep `docs/evaluation/EXTERNAL_SCANNER_VALIDATION.md` regenerated when scanner inputs or scanner versions change.",
        "status": "completed",
        "global_promotion": "not applicable",
        "artifacts": [
            "Dockerfile",
            "docs/dev/RUNBOOK.md",
            "docs/codex/CODEX_CONTEXT.md",
            "docs/evaluation/EXTERNAL_SCANNER_VALIDATION_STATUS.md",
            "docs/evaluation/EXTERNAL_SCANNER_VALIDATION.md",
            "data/results/evaluation/external-scanner-validation-status.json",
            "data/results/evaluation/external-scanner-validation.json",
        ],
    },
    {
        "priority": 3,
        "weak_point": "Dataset size should grow by APK family, not convenience.",
        "evidence": "Material Files 1.7.4 remains source-validated partial native-JNI evidence. The category-driven smoke/report batch then adds 8 SHA-256-verified F-Droid APKs: LocalSend, OpenVPN for Android, KeePassDX, Gadgetbridge, DAVx5, Shelter, TheXTech, and Fennec F-Droid. Four rows from that smoke batch are now promoted to source-validated partial evidence: DAVx5 confirms 3/5 emitted Maven versions, OpenVPN confirms 13/20 through a no-native validation copy, Gadgetbridge confirms 17/21 after deriving the matching F-Droid source tarball, and Shelter confirms 3/3 through a documented app-only/toolchain-compatibility validation copy. A follow-up low-risk preflight batch deliberately chooses no-native, small, modern-Gradle apps that return dependency trees quickly: Stopwatch confirms 4/5 emitted Maven versions, Bubble confirms 1/7, and Audio Source confirms 0/3. Blue Square Speedometer passes source/build/report validation but emits 0 Maven components, so it is recorded as a no-Maven-signal control rather than accuracy evidence. LocalSend, KeePassDX, TheXTech, and Fennec F-Droid remain excluded from accuracy metrics until their proof bundles are complete.",
        "paper_basis": "TPL-Benchmark and Systematic Assessment show realistic datasets expose lower and more useful performance than polished single-score evaluations.",
        "current_policy": "Add APKs to cover classification gaps, then validate with source proof before counting them in accuracy metrics.",
        "safe_next_action": "Use the four promoted rows as partial source-validated family coverage, keep the four blocked/framework rows as smoke or limitation evidence, and acquire a legal protected/packed real APK separately as limitation evidence.",
        "status": "completed",
        "global_promotion": "not applicable",
        "artifacts": [
            "docs/evaluation/DATASET_DESIGN.md",
            "docs/evaluation/APK_TESTSET_INVENTORY.md",
            "docs/evaluation/REAL_APK_CANDIDATES.md",
            "docs/evaluation/NEXT_REAL_APK_GROWTH_QUEUE.md",
            "docs/evaluation/REAL_APK_GROWTH_BATCH_V2.md",
            "docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md",
            "docs/evaluation/MATERIAL_FILES_PROOF_BUNDLE.md",
            "data/results/report-real-material-files/report.md",
            "data/results/source-validation/material-files-report-validation/source-validation.md",
        ],
    },
    {
        "priority": 4,
        "weak_point": "Hidden DEX, packed payloads, and dynamic loading can hide code from static extraction.",
        "evidence": "The hidden-DEX diagnostic confirms the limitation fixture raises medium extraction risk, high obfuscation risk, nonstandard/protector indicators, 0 Maven components, and 1 hash-only native file component.",
        "paper_basis": "Obfuscation studies and systematic assessments identify packing and dynamic loading as static-analysis boundaries.",
        "current_policy": "Raise extraction and obfuscation risk instead of producing unsupported Maven claims.",
        "safe_next_action": "Completed for the current MVP limitation set: keep hidden-code cases excluded from accuracy metrics and add future hidden-code work only as evaluation expansion before stronger recovery claims.",
        "status": "completed",
        "global_promotion": "not applicable",
        "artifacts": [
            "docs/evaluation/HIDDEN_DEX_DIAGNOSTICS.md",
            "data/results/evaluation/hidden-dex-diagnostics.json",
            "docs/evaluation/HIDDEN_DEX_LIMITATION_FIXTURE.md",
            "data/results/report-limitation-hidden-dex-loader/report.json",
        ],
    },
    {
        "priority": 4,
        "weak_point": "R8, shrinking, inlining, and obfuscation reduce stable bytecode evidence.",
        "evidence": "Phase 1 adds report-only R8/obfuscation diagnostics to inspect-apk and generate-report. Phase 2 expands the controlled generated matrix to clear, rename, shrink, optimize, shrink+optimize, package flattening/repackaging, inline-like call-site stress, and multidex/multi-library controls. Phase 3 adds inert call-chain, basic-block, class-neighbor, field-operation, and literal/context feature availability, with matcher scoring unchanged. The expanded Phase 4 layered diagnostic checks 24 controlled R8 cases plus 262 real APK component rows on a calibrated multi-scale DB. It finds 4 real source-validated improvement candidates, but also 6 controlled regressions, 30 real source-validated regressions, and 8 clean-real regressions. The Phase 5 scoped trigger diagnostic then limits the trigger to those improvement profiles and applies to 4 target rows with 0 triggered regressions/conflicts across 286 rows. The explicit r8-phase5-experiment command exposes this path as an opt-in diagnostic, and generate-report can attach it as report-only evidence with --include-r8-phase5-experiment. The Phase 5 trigger control validation passes 11 gates: 24 controlled rows blocked, 43 clean rows blocked, 36 boundary rows blocked, 4 target improvements kept, and 0 triggered regressions/conflicts. The generated report-evidence summary validates 4 target APK reports with 4 separate suggestions, 4 SBOM artifacts, and 0 default selection changes.",
        "paper_basis": "Android R8 documentation, LibHunter, SAD, ATVHunter, LibAttention, LibMD, ObfDetector, TPL-Benchmark, and Systematic Assessment support an evaluation-first design: classifier and controlled matrix first, then inert call-chain/basic-block/field-operation evidence, then scoped inlining-aware scoring only if controls stay clean.",
        "current_policy": "Treat obfuscation as confidence-affecting. Use lower confidence, ambiguity, or risk warnings when package names, methods, literals, or DEX structure are unstable.",
        "safe_next_action": "Keep the rejected Phase 4 global blend disabled and the explicit r8-phase5-experiment command plus optional report evidence diagnostic-only. Any future production scorer must be off by default, narrower than the global blend, and verified with its own regression tests.",
        "status": "phase-5-scoped-trigger-diagnostic-clean-not-promoted",
        "global_promotion": "rejected for current multi-scale blend",
        "artifacts": [
            "docs/research/R8_OBFUSCATION_METHOD_SELECTION.md",
            "docs/planning/R8_OBFUSCATION_CON_EXECUTION_PLAN.md",
            "docs/codex/R8_OBFUSCATION_CON_CONTINUATION_PROMPT.md",
            "data/results/evaluation/r8-obfuscation-method-selection.json",
            "scripts/build_r8_obfuscation_method_selection.py",
            "docs/evaluation/R8_OBFUSCATION_DIAGNOSTICS.md",
            "data/results/evaluation/r8-obfuscation-diagnostics.json",
            "docs/evaluation/R8_MULTISCALE_FEATURE_DIAGNOSTICS.md",
            "data/results/evaluation/r8-multiscale-feature-diagnostics.json",
            "docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md",
            "data/results/experiments/r8-phase4-scoped-experiment-diagnostics.json",
            "scripts/build_r8_phase4_scoped_experiment_diagnostics.py",
            "docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md",
            "data/results/experiments/r8-phase5-scoped-trigger-diagnostics.json",
            "scripts/build_r8_phase5_scoped_trigger_diagnostics.py",
            "docs/evaluation/R8_PHASE5_TRIGGER_CONTROL_VALIDATION.md",
            "data/results/experiments/r8-phase5-trigger-control-validation.json",
            "scripts/build_r8_phase5_trigger_control_validation.py",
            "docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md",
            "data/results/experiments/r8-phase5-report-evidence/summary.json",
            "scripts/build_r8_phase5_report_evidence.py",
            "src/apk_sbom/r8_scoped_reranker.py",
            "src/apk_sbom/r8_phase5_experiment.py",
            "scripts/build_r8_multiscale_feature_diagnostics.py",
            "data/reference_db/reference_features_phase3_multiscale_gson.sqlite",
            "data/results/report-generated-gson-2-8-9-r8-inline-stress-phase3/report.json",
            "data/results/evaluation/generated-apk-category-batch.json",
            "data/results/evaluation/generated-apk-category-batch.md",
            "scripts/build_r8_obfuscation_diagnostics.py",
            "docs/evaluation/DATASET_DESIGN.md",
            "docs/evaluation/HIDDEN_DEX_LIMITATION_FIXTURE.md",
            "scripts/run_generated_apk_batch.py",
            "scripts/build_controlled_apk.py",
            "src/apk_sbom/obfuscation.py",
            "src/apk_sbom/dex_analyzer.py",
            "src/apk_sbom/report.py",
            "src/apk_sbom/cli.py",
            "data/results/report-gson-r8-shrink/report.json",
            "data/results/report-limitation-hidden-dex-loader/report.json",
        ],
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the MVP cons and paper-backed improvement plan.",
    )
    parser.add_argument("--thesis-tables-json", default=str(DEFAULT_THESIS_TABLES_JSON))
    parser.add_argument("--version-ties-json", default=str(DEFAULT_VERSION_TIES_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    thesis_path = Path(args.thesis_tables_json)
    ties_path = Path(args.version_ties_json)
    payload = build_payload(
        read_json(thesis_path),
        read_json(ties_path),
        thesis_path=thesis_path,
        ties_path=ties_path,
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
                "plan_items": len(payload["plan_items"]),
                "safe_next_items": len(
                    [item for item in payload["plan_items"] if item["status"] == "safe-next"]
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    thesis_tables: dict[str, Any],
    version_ties: dict[str, Any],
    *,
    thesis_path: Path,
    ties_path: Path,
) -> dict[str, Any]:
    summary = thesis_tables.get("summary", {})
    return {
        "schema_version": 1,
        "sources": {
            "thesis_tables": normalize_path(thesis_path),
            "version_ties": normalize_path(ties_path),
            "reranker_diagnostics": "docs/evaluation/VERSION_TIE_RERANKER_DIAGNOSTICS.md",
            "source_version_queue": "docs/evaluation/SOURCE_VERSION_CANDIDATE_QUEUE.md",
            "paper_backed_notes": "docs/thesis/PAPER_BACKED_MVP_IMPROVEMENT_NOTES.md",
            "traceability": "docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md",
            "r8_phase4": "docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md",
        },
        "current_evaluation": build_current_evaluation(summary),
        "version_tie_audit": {
            "row_count": version_ties.get("row_count", 0),
            "classification_counts": version_ties.get("classification_counts", {}),
            "isolated_experiment_comparisons": version_ties.get(
                "isolated_experiment_comparisons", []
            ),
        },
        "decision_policy": [
            "Improve the tool when evidence supports the change.",
            "Do not hide partial, blocked, or limitation cases to create a perfect-looking score.",
            "Do not promote a global rule or reference version without a fresh current-control regression matrix.",
            "Prefer diagnostic artifacts before scoring changes for risky AndroidX/Kotlin version-band ties.",
            "Keep source-validated accuracy metrics separate from report-only and boundary evidence.",
        ],
        "plan_items": PLAN_ITEMS,
        "recommended_next_batch": [
        {
            "step": 1,
            "task": "Keep the Phase 4 multi-scale blend disabled and the Phase 5 command experiment-only.",
            "why": "The reviewed r8-phase5-experiment command is opt-in and profile-scoped; generate-report may surface it only as report-only evidence, and it must stay separate from default matcher/SBOM behavior.",
        },
        {
            "step": 2,
            "task": "Document accepted, rejected, disabled, and deferred methods in the experiment decision ledger.",
            "why": "Negative experiments are thesis evidence and show why the MVP avoids overfit exact-version claims.",
        },
        {
            "step": 3,
            "task": "Consider production scorer wiring only after fresh flag-specific regression evidence.",
            "why": "The project guardrail is no default scoring, SBOM, vulnerability, or source-validation metric change without fresh regression evidence.",
        },
        ],
    }


def build_current_evaluation(summary: dict[str, Any]) -> dict[str, str]:
    controlled = summary.get("controlled_fixtures", {})
    clean = summary.get("clean_versions", {})
    partial = summary.get("partial_versions", {})
    overall = summary.get("source_validated_versions", {})
    return {
        "controlled": format_fraction(
            controlled.get("confirmed_versions"), controlled.get("expected_components")
        ),
        "clean_real": format_fraction(clean.get("confirmed"), clean.get("checked")),
        "partial_real": format_fraction(partial.get("confirmed"), partial.get("checked")),
        "overall_real": format_fraction(overall.get("confirmed"), overall.get("checked")),
        "blocked_cases": str(summary.get("blocked_source_linked_cases", 0)),
        "limitation_cases": str(summary.get("limitation_cases", 0)),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    current = payload["current_evaluation"]
    lines = [
        "# MVP Cons And Improvement Plan",
        "",
        "Generated by `scripts/build_mvp_cons_improvement_plan.py`.",
        "",
        "This file turns the saved cons/improvement notes into an operational plan. It is intentionally not a perfect-score plan: every improvement must either be regression-guarded, diagnostic-only, blocked, or a clearly documented boundary.",
        "",
        "Companion notes:",
        "",
        "- `docs/thesis/PAPER_BACKED_MVP_IMPROVEMENT_NOTES.md`",
        "- `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`",
        "- `docs/evaluation/VERSION_BAND_TIE_EVIDENCE.md`",
        "",
        "## Current Evidence Snapshot",
        "",
        "| Slice | Result |",
        "|---|---:|",
        f"| Controlled fixtures | {current['controlled']} |",
        f"| Clean source-validated real APKs | {current['clean_real']} |",
        f"| Partial source-validated real APKs | {current['partial_real']} |",
        f"| Overall source-validated real APKs | {current['overall_real']} |",
        f"| Source-linked blocked cases | {current['blocked_cases']} |",
        f"| Limitation/boundary cases | {current['limitation_cases']} |",
        "",
        "Use these as emitted Maven version confirmation counts, not full dependency recall.",
        "",
        "## Version-Band Audit Snapshot",
        "",
        f"Risky tie rows audited: {payload['version_tie_audit']['row_count']}",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    counts = payload["version_tie_audit"]["classification_counts"]
    for key in sorted(counts):
        lines.append(f"| `{key}` | {counts[key]} |")

    lines.extend(
        [
            "",
            "## Decision Policy",
            "",
        ]
    )
    lines.extend(f"- {line}" for line in payload["decision_policy"])

    lines.extend(
        [
            "",
            "## Prioritized Plan",
            "",
            "| Priority | Status | Weak point | Safe next action | Promotion rule |",
            "|---:|---|---|---|---|",
        ]
    )
    for item in payload["plan_items"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item["priority"]),
                    f"`{item['status']}`",
                    md(item["weak_point"]),
                    md(item["safe_next_action"]),
                    md(item["global_promotion"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Detailed Items",
            "",
        ]
    )
    for item in payload["plan_items"]:
        lines.extend(
            [
                f"### P{item['priority']} - {item['weak_point']}",
                "",
                f"- Status: `{item['status']}`",
                f"- Evidence: {item['evidence']}",
                f"- Paper/tool basis: {item['paper_basis']}",
                f"- Current policy: {item['current_policy']}",
                f"- Safe next action: {item['safe_next_action']}",
                f"- Global promotion rule: {item['global_promotion']}",
                "- Artifacts: " + ", ".join(f"`{artifact}`" for artifact in item["artifacts"]),
                "",
            ]
        )

    lines.extend(
        [
            "## Recommended Next Batch",
            "",
            "| Step | Task | Why |",
            "|---:|---|---|",
        ]
    )
    for row in payload["recommended_next_batch"]:
        lines.append(f"| {row['step']} | {md(row['task'])} | {md(row['why'])} |")

    lines.extend(
        [
            "",
            "## What Not To Do",
            "",
            "- Do not treat K-9 as clean evidence; keep the validation-only plugin-lite rescue caveat visible.",
            "- Do not promote Activity `1.9.2`, ViewPager2 `1.1.0-beta02`, Concurrent Futures, or Okio-JVM changes globally without a clean control matrix.",
            "- Do not turn API-reference or opcode tri-gram signals on globally based only on feature availability.",
            "- Do not promote the Phase 4 multi-scale blend globally or the Phase 5 scoped trigger by default without a fresh control-clean pass.",
            "- Do not collapse clean, partial, blocked, and limitation rows into one polished score.",
            "",
        ]
    )
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def format_fraction(confirmed: Any, checked: Any) -> str:
    if confirmed is None or checked is None:
        return "n/a"
    return f"{confirmed}/{checked}"


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
