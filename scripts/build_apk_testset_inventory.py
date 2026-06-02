from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


DEFAULT_GROUND_TRUTH_DIR = Path("data/test_apks")
DEFAULT_LIMITATION_DIR = Path("data/test_apks/limitation")
DEFAULT_REPORTS_DIR = Path("data/results")
DEFAULT_OUTPUT_DIR = Path("data/results/evaluation")
DEFAULT_DOC_PATH = Path("docs/evaluation/APK_TESTSET_INVENTORY.md")
DEFAULT_FDROID_REPORT = Path("data/results/report-real-f-droid-final-demo-osv/report.json")
DEFAULT_FDROID_VALIDATION = Path(
    "data/results/source-validation/fdroid-final-demo-osv/source-validation.json"
)
DEFAULT_OPENTRACKS_REPORT = Path(
    "data/results/report-real-opentracks-calibrated-db/report.json"
)
DEFAULT_OPENTRACKS_VALIDATION = Path(
    "data/results/source-validation/opentracks-calibrated-db/source-validation.json"
)
DEFAULT_TUSKY_REPORT = Path("data/results/report-real-tusky-calibrated-db/report.json")
DEFAULT_TUSKY_VALIDATION = Path(
    "data/results/source-validation/tusky-calibrated-db/source-validation.json"
)
DEFAULT_CONVERSATIONS_REPORT = Path("data/results/report-real-conversations/report.json")
DEFAULT_CONVERSATIONS_VALIDATION = Path(
    "data/results/source-validation/conversations-report-validation/source-validation.json"
)

LIBRARY_PROFILES = {
    "com.fasterxml.jackson.core:jackson-databind": {
        "language": "Java",
        "framework": "Jackson JSON databinding",
        "family": "JSON",
        "androidx_usage": "none",
        "kmp_artifacts": "none",
        "overlap_family": "none",
        "vulnerable_expected": "yes",
        "notes": "Known vulnerable controlled fixture for OSV positive demo.",
    },
    "com.google.code.gson:gson": {
        "language": "Java",
        "framework": "Gson JSON serialization",
        "family": "JSON",
        "androidx_usage": "none",
        "kmp_artifacts": "none",
        "overlap_family": "none",
        "vulnerable_expected": "no",
        "notes": "Used for clear and R8 variants.",
    },
    "com.squareup.okhttp3:okhttp": {
        "language": "Kotlin/Java",
        "framework": "OkHttp HTTP client",
        "family": "networking",
        "androidx_usage": "none",
        "kmp_artifacts": "none",
        "overlap_family": "OkHttp/Okio transitive family",
        "vulnerable_expected": "no for current fixture version",
        "notes": "Common Android networking library.",
    },
    "com.squareup.okio:okio-jvm": {
        "language": "Kotlin/Java",
        "framework": "Okio I/O primitives",
        "family": "networking/IO",
        "androidx_usage": "none",
        "kmp_artifacts": "JVM target artifact",
        "overlap_family": "OkHttp/Okio transitive family",
        "vulnerable_expected": "no for current fixture version",
        "notes": "Common transitive dependency for OkHttp-family fixtures.",
    },
    "com.squareup.retrofit2:retrofit": {
        "language": "Java/Kotlin",
        "framework": "Retrofit HTTP API client",
        "family": "networking",
        "androidx_usage": "none",
        "kmp_artifacts": "none",
        "overlap_family": "OkHttp/Retrofit transitive family",
        "vulnerable_expected": "no",
        "notes": "Common Android networking abstraction.",
    },
    "commons-codec:commons-codec": {
        "language": "Java",
        "framework": "Apache Commons Codec utilities",
        "family": "encoding/utility",
        "androidx_usage": "none",
        "kmp_artifacts": "none",
        "overlap_family": "none",
        "vulnerable_expected": "no for current fixture version",
        "notes": "Used for clear and R8 variants.",
    },
}

VARIANT_PROFILES = {
    "clear": {
        "r8": "no",
        "r8_status": "none",
        "r8_mode": "none",
        "obfuscation": "none",
        "obfuscation_level": "none",
        "resource_shrinking": "no",
        "details": "D8 conversion only; library names and structure are preserved.",
    },
    "r8-rename": {
        "r8": "yes",
        "r8_status": "R8",
        "r8_mode": "rename",
        "obfuscation": "rename/minify only",
        "obfuscation_level": "light",
        "resource_shrinking": "no",
        "details": "R8 renames classes and members without shrinking or optimization.",
    },
    "r8-shrink": {
        "r8": "yes",
        "r8_status": "R8",
        "r8_mode": "shrink",
        "obfuscation": "rename plus shrinking",
        "obfuscation_level": "moderate",
        "resource_shrinking": "yes",
        "details": "R8 keeps only public/API-reachable pieces according to fixture rules.",
    },
    "r8-optimize": {
        "r8": "yes",
        "r8_status": "R8",
        "r8_mode": "optimize",
        "obfuscation": "optimization without renaming",
        "obfuscation_level": "moderate",
        "resource_shrinking": "no",
        "details": "R8 optimization is enabled while names and reachable library structure are preserved.",
    },
    "r8-shrink-optimize": {
        "r8": "yes",
        "r8_status": "R8",
        "r8_mode": "shrink+optimize",
        "obfuscation": "shrinking plus optimization",
        "obfuscation_level": "high",
        "resource_shrinking": "yes",
        "details": "R8 can remove unused code and optimize surviving classes/methods.",
    },
    "r8-repackage": {
        "r8": "yes",
        "r8_status": "R8",
        "r8_mode": "package flattening/repackaging",
        "obfuscation": "rename/minify plus package repackaging",
        "obfuscation_level": "high",
        "resource_shrinking": "no",
        "details": "R8 moves obfuscated classes into a flattened synthetic package namespace.",
    },
    "r8-inline-stress": {
        "r8": "yes",
        "r8_status": "R8",
        "r8_mode": "optimize with inline-like call-site stress",
        "obfuscation": "optimization and call-site stress",
        "obfuscation_level": "moderate",
        "resource_shrinking": "no",
        "details": "Fixture source adds app-side helper call chains so R8 optimization can stress call-site structure.",
    },
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an APK testset inventory with ground truth and current results.",
    )
    parser.add_argument("--ground-truth-dir", default=str(DEFAULT_GROUND_TRUTH_DIR))
    parser.add_argument("--limitation-dir", default=str(DEFAULT_LIMITATION_DIR))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--doc-path", default=str(DEFAULT_DOC_PATH))
    parser.add_argument("--fdroid-report", default=str(DEFAULT_FDROID_REPORT))
    parser.add_argument("--fdroid-validation", default=str(DEFAULT_FDROID_VALIDATION))
    parser.add_argument("--opentracks-report", default=str(DEFAULT_OPENTRACKS_REPORT))
    parser.add_argument("--opentracks-validation", default=str(DEFAULT_OPENTRACKS_VALIDATION))
    parser.add_argument("--tusky-report", default=str(DEFAULT_TUSKY_REPORT))
    parser.add_argument("--tusky-validation", default=str(DEFAULT_TUSKY_VALIDATION))
    parser.add_argument("--conversations-report", default=str(DEFAULT_CONVERSATIONS_REPORT))
    parser.add_argument(
        "--conversations-validation",
        default=str(DEFAULT_CONVERSATIONS_VALIDATION),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    reports = load_reports(Path(args.reports_dir))
    controlled = build_controlled_inventory(Path(args.ground_truth_dir), reports)
    limitations = build_limitation_inventory(Path(args.limitation_dir), reports)
    real = [
        *build_fdroid_inventory(Path(args.fdroid_report), Path(args.fdroid_validation)),
        *build_opentracks_inventory(
            Path(args.opentracks_report),
            Path(args.opentracks_validation),
        ),
        *build_tusky_inventory(Path(args.tusky_report), Path(args.tusky_validation)),
        *build_conversations_inventory(
            Path(args.conversations_report),
            Path(args.conversations_validation),
        ),
    ]
    inventory = build_inventory(controlled, real, limitations)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "apk-testset-inventory.json"
    json_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    doc_path = Path(args.doc_path)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(build_markdown(inventory), encoding="utf-8")

    print(
        json.dumps(
            {
                "controlled_apks": len(controlled),
                "doc": normalize_path(str(doc_path)),
                "json": normalize_path(str(json_path)),
                "limitation_apks": len(limitations),
                "real_apks": len(real),
                "summary": inventory["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_inventory(
    controlled: list[dict[str, Any]],
    real: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
) -> dict[str, Any]:
    controlled_expected = sum(len(item["expected_components"]) for item in controlled)
    controlled_detected = sum(len(item["detected_components"]) for item in controlled)
    controlled_fp = sum(len(item["comparison"]["false_positive_components"]) for item in controlled)
    controlled_fn = sum(len(item["comparison"]["false_negative_components"]) for item in controlled)
    controlled_version_mismatches = sum(
        len(item["comparison"]["version_mismatches"]) for item in controlled
    )

    fdroid = real[0] if real else {}
    fdroid_validation = fdroid.get("source_validation", {})
    return {
        "schema_version": 1,
        "purpose": (
            "Describe the APKs used to test the MVP and make expected-vs-detected "
            "comparison explicit for false-positive and false-negative analysis."
        ),
        "summary": {
            "controlled_apks": len(controlled),
            "controlled_expected_components": controlled_expected,
            "controlled_detected_components": controlled_detected,
            "controlled_false_positive_components": controlled_fp,
            "controlled_false_negative_components": controlled_fn,
            "controlled_version_mismatches": controlled_version_mismatches,
            "real_apks": len(real),
            "limitation_apks": len(limitations),
            "fdroid_source_components_total": fdroid_validation.get("source_components"),
            "fdroid_evaluated_sbom_components": fdroid_validation.get("sbom_components"),
            "fdroid_confirmed_versions": fdroid_validation.get("confirmed"),
            "fdroid_version_mismatches": fdroid_validation.get("version_mismatches"),
            "fdroid_missing_coordinates": fdroid_validation.get("missing"),
            "source_validated_real_apks": sum(
                1 for item in real if item.get("source_validation_status") == "complete"
            ),
            "partial_source_validated_real_apks": sum(
                1
                for item in real
                if item.get("source_validation_status") == "partial-version-mismatch"
            ),
            "real_evaluated_sbom_components": sum(
                int(item.get("source_validation", {}).get("sbom_components") or 0)
                for item in real
            ),
            "real_confirmed_versions": sum(
                int(item.get("source_validation", {}).get("confirmed") or 0)
                for item in real
            ),
            "real_version_mismatches": sum(
                int(item.get("source_validation", {}).get("version_mismatches") or 0)
                for item in real
            ),
            "real_missing_coordinates": sum(
                int(item.get("source_validation", {}).get("missing") or 0)
                for item in real
            ),
        },
        "ground_truth_policy": {
            "controlled": (
                "Exact by construction: each controlled APK records one or more "
                "expected Maven artifacts in its .ground-truth.json file."
            ),
            "real_fdroid": (
                "Exact for evaluated components by source validation: the emitted "
                "SBOM components are compared with F-Droid's resolved Gradle "
                "dependency tree. The full dependency tree has more components than "
                "the current calibrated MVP reference scope."
            ),
            "real_source_validated": (
                "Exact for emitted components when the APK is linked to source and a "
                "resolved Gradle dependency tree; this now includes F-Droid, OpenTracks, "
                "Tusky, and partial-version-mismatch cases such as Conversations."
            ),
            "limitation": (
                "Not used for precision/recall: limitation APKs exercise forensic warnings "
                "and unsupported dynamic/protected packaging behavior."
            ),
        },
        "controlled_apks": controlled,
        "real_apks": real,
        "limitation_apks": limitations,
    }


def build_controlled_inventory(
    ground_truth_dir: Path,
    reports: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for truth_path in sorted(ground_truth_dir.glob("*.ground-truth.json")):
        truth = read_json(truth_path)
        apk_path = normalize_path(truth["apk_path"])
        report = reports.get(apk_path)
        expected_components = expected_components_from_truth(truth, truth_path)
        apk_info = inspect_apk(Path(truth["apk_path"]))
        variant = truth.get("variant", "unknown")
        variant_profile = VARIANT_PROFILES.get(
            variant,
            {
                "r8": "unknown",
                "r8_status": "unknown",
                "r8_mode": "unknown",
                "obfuscation": "unknown",
                "obfuscation_level": "unknown",
                "resource_shrinking": "unknown",
                "details": "Unknown fixture variant.",
            },
        )
        detected_components = detected_components_from_report(report)
        comparison = compare_components(expected_components, detected_components)
        decisions = [
            find_decision(report, component["coordinate"])
            for component in expected_components
        ]
        osv = osv_summary_from_report(report)
        profile = aggregate_library_profile(expected_components)
        rows.append(
            {
                "id": Path(apk_path).stem,
                "dataset_layer": "controlled",
                "validation_level": "L1 controlled ground truth",
                "metrics_allowed": [
                    "precision",
                    "recall",
                    "F1",
                    "version accuracy",
                    "obfuscation robustness",
                ],
                "apk_path": apk_path,
                "apk_sha256": apk_info["sha256"],
                "apk_size": apk_info["size"],
                "app_package": "com.example.fixture",
                "package_name": "com.example.fixture",
                "download_source": "generated by project fixture builder",
                "release_era": "controlled synthetic",
                "build_type": "controlled fixture",
                "source_type": "controlled synthetic APK",
                "source_validation_status": "complete by construction",
                "source_proof": normalize_path(str(truth_path)),
                "fixture_mode": truth.get("fixture_mode", "unknown"),
                "fixture_builder": truth.get("builder", "unknown"),
                "generated_batch": truth.get("generated_batch"),
                "generated_phase": truth.get("generated_phase"),
                "evaluation_category": truth.get("evaluation_category"),
                "classification_tags": truth.get("classification_tags", []),
                "primary_language": profile["language"],
                "language": profile["language"],
                "framework_type": "Android controlled fixture",
                "framework_or_library_type": profile["framework"],
                "main_library_families": profile["families"],
                "androidx_jetpack_usage": profile["androidx_usage"],
                "kotlin_kmp_artifacts": profile["kmp_artifacts"],
                "expected_third_party_dependency_count": len(expected_components),
                "transitive_dependency_complexity": "medium"
                if len(expected_components) > 1
                else "low",
                "overlapping_artifact_families": profile["overlap_family"],
                "known_vulnerable_dependency_expected": profile["vulnerable_expected"],
                "library_notes": profile["notes"],
                "variant": variant,
                "r8_used": variant_profile["r8"],
                "r8_proguard_status": variant_profile["r8_status"],
                "r8_mode": variant_profile["r8_mode"],
                "obfuscation": variant_profile["obfuscation"],
                "obfuscation_level": variant_profile["obfuscation_level"],
                "obfuscation_details": variant_profile["details"],
                "minification_evidence": f"controlled fixture variant `{variant}`",
                "resource_shrinking": variant_profile["resource_shrinking"],
                "packer_protector_indicators": "none",
                "dynamic_loading_indicators": "none",
                "dex_files": apk_info["dex_files"],
                "dex_count": len(apk_info["dex_files"]),
                "multidex": apk_info["multidex"],
                "native_libraries": apk_info["native_libraries"],
                "native_so_count": len(apk_info["native_libraries"]),
                "native_abi_list": native_abi_list(apk_info["native_libraries"]),
                "manifest_metadata_available": apk_info["manifest_present"],
                "resources_available": apk_info["resources_arsc_present"],
                "expected_components": expected_components,
                "detected_components": detected_components,
                "comparison": comparison,
                "truth_decision": decisions[0] if decisions else {},
                "truth_decisions": decisions,
                "osv": osv,
                "report_path": normalize_path(report.get("_report_path", "")) if report else None,
            }
        )
    return rows


def expected_components_from_truth(
    truth: dict[str, Any],
    truth_path: Path,
) -> list[dict[str, Any]]:
    components = truth.get("expected_components")
    if components:
        return [
            {
                "coordinate": component["coordinate"],
                "version": component["version"],
                "purl": component["purl"],
                "source": normalize_path(str(truth_path)),
            }
            for component in components
        ]
    return [
        {
            "coordinate": truth["coordinate"],
            "version": truth["version"],
            "purl": truth["purl"],
            "source": normalize_path(str(truth_path)),
        }
    ]


def aggregate_library_profile(expected_components: list[dict[str, Any]]) -> dict[str, Any]:
    profiles = [
        LIBRARY_PROFILES.get(component["coordinate"], unknown_library_profile())
        for component in expected_components
    ]
    return {
        "language": join_unique(profile["language"] for profile in profiles),
        "framework": join_unique(profile["framework"] for profile in profiles),
        "families": sorted({profile["family"] for profile in profiles}),
        "androidx_usage": join_unique(profile["androidx_usage"] for profile in profiles),
        "kmp_artifacts": join_unique(profile["kmp_artifacts"] for profile in profiles),
        "overlap_family": join_unique(profile["overlap_family"] for profile in profiles),
        "vulnerable_expected": join_unique(profile["vulnerable_expected"] for profile in profiles),
        "notes": join_unique(profile["notes"] for profile in profiles),
    }


def join_unique(values: Any) -> str:
    seen = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.append(text)
    return "; ".join(seen)


def build_limitation_inventory(
    limitation_dir: Path,
    reports: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metadata_path in sorted(limitation_dir.glob("*.limitation.json")):
        metadata = read_json(metadata_path)
        apk_path = normalize_path(metadata["apk_path"])
        report = reports.get(apk_path)
        apk = report.get("apk", {}) if report else {}
        apk_info = inspect_apk(Path(metadata["apk_path"]))
        forensic = apk.get("forensic_summary", {})
        manifest = apk.get("manifest_metadata", {})
        obfuscation_risk = report.get("obfuscation_risk", {}) if report else {}
        match_summary = report.get("match_summary", {}) if report else {}
        native_libraries = apk.get("native_libraries") or apk_info["native_libraries"]
        dex_files = apk.get("dex_files") or apk_info["dex_files"]
        detected_components = detected_components_from_report(report)

        expected_behavior = metadata.get("expected_behavior", {})
        obfuscation_details = metadata.get(
            "obfuscation_details",
            (
                "Synthetic fixture with tiny primary DEX, hidden DEX-like asset, "
                "protector-like file names, and opaque asset payload."
            ),
        )
        rows.append(
            {
                "id": Path(apk_path).stem,
                "dataset_layer": metadata.get("dataset_layer", "limitation"),
                "validation_level": metadata.get("validation_level", "L3 limitation fixture"),
                "metrics_allowed": metadata.get(
                    "metrics_allowed",
                    ["forensic warning quality", "limitation behavior"],
                ),
                "apk_path": apk_path,
                "apk_sha256": apk.get("apk_sha256") or apk_info["sha256"],
                "apk_size": apk.get("apk_size") or apk_info["size"],
                "app_package": manifest.get("package_name") or metadata.get("package_name"),
                "package_name": manifest.get("package_name") or metadata.get("package_name"),
                "version_name": manifest.get("version_name"),
                "version_code": manifest.get("version_code"),
                "download_source": metadata.get(
                    "download_source",
                    "generated by project limitation fixture builder",
                ),
                "release_era": metadata.get("release_era", "controlled synthetic"),
                "build_type": metadata.get("build_type", "controlled limitation fixture"),
                "source_type": metadata.get("source_type", "controlled synthetic APK"),
                "source_validation_status": metadata.get(
                    "source_validation_status",
                    "limitation only",
                ),
                "source_proof": normalize_path(str(metadata_path)),
                "fixture_mode": metadata.get(
                    "fixture_mode",
                    "synthetic hidden DEX/protector indicator",
                ),
                "fixture_builder": metadata.get("builder", "unknown"),
                "primary_language": metadata.get("primary_language", "not applicable"),
                "language": metadata.get("language", "not applicable"),
                "framework_type": metadata.get("framework_type", "Android limitation fixture"),
                "framework_or_library_type": metadata.get(
                    "framework_or_library_type",
                    "dynamic-code/protector-style packaging",
                ),
                "main_library_families": metadata.get("main_library_families", ["none"]),
                "androidx_jetpack_usage": metadata.get("androidx_jetpack_usage", "none"),
                "kotlin_kmp_artifacts": metadata.get("kotlin_kmp_artifacts", "none"),
                "expected_third_party_dependency_count": metadata.get(
                    "expected_third_party_dependency_count",
                    0,
                ),
                "transitive_dependency_complexity": metadata.get(
                    "transitive_dependency_complexity",
                    "not applicable",
                ),
                "overlapping_artifact_families": metadata.get(
                    "overlapping_artifact_families",
                    "none",
                ),
                "known_vulnerable_dependency_expected": metadata.get(
                    "known_vulnerable_dependency_expected",
                    "no",
                ),
                "library_notes": expected_behavior.get(
                    "reporting_expectation",
                    "Limitation fixture for forensic warning behavior.",
                ),
                "variant": metadata.get("variant", "hidden-dex-loader-limitation"),
                "r8_used": metadata.get("r8_used", "not applicable"),
                "r8_proguard_status": metadata.get("r8_proguard_status", "not applicable"),
                "r8_mode": metadata.get("r8_mode", "not applicable"),
                "obfuscation": metadata.get(
                    "obfuscation",
                    "protected/dynamic-code-style packaging",
                ),
                "obfuscation_level": metadata.get("obfuscation_level", "heavy"),
                "obfuscation_details": obfuscation_details,
                "minification_evidence": metadata.get(
                    "minification_evidence",
                    "APK-side forensic indicators",
                ),
                "resource_shrinking": metadata.get("resource_shrinking", "not applicable"),
                "packer_protector_indicators": indicator_summary(forensic),
                "dynamic_loading_indicators": metadata.get(
                    "dynamic_loading_indicators",
                    "suspected: nonstandard DEX-like file outside top-level classes*.dex layout",
                ),
                "dex_files": dex_files,
                "dex_count": len(dex_files),
                "multidex": apk.get("has_multidex", apk_info["multidex"]),
                "native_libraries": native_libraries,
                "native_so_count": len(native_libraries),
                "native_abi_list": native_abi_list(native_libraries),
                "manifest_metadata_available": apk.get(
                    "manifest_present",
                    apk_info["manifest_present"],
                ),
                "resources_available": apk.get(
                    "resources_arsc_present",
                    apk_info["resources_arsc_present"],
                ),
                "expected_components": [],
                "detected_components": detected_components,
                "comparison": {
                    "component_true_positives": [],
                    "version_true_positives": [],
                    "version_mismatches": [],
                    "false_positive_components": [
                        component.get("coordinate") for component in detected_components
                    ],
                    "false_negative_components": [],
                },
                "truth_decision": None,
                "osv": osv_summary_from_report(report),
                "report_path": normalize_path(report.get("_report_path", "")) if report else None,
                "forensic_summary": forensic,
                "obfuscation_risk": obfuscation_risk,
                "dex_files_analyzed": match_summary.get("dex_files_analyzed"),
                "dex_files_failed": match_summary.get("dex_files_failed"),
            }
        )
    return rows


def build_fdroid_inventory(report_path: Path, validation_path: Path) -> list[dict[str, Any]]:
    if not report_path.exists() or not validation_path.exists():
        return []

    report = read_json(report_path)
    validation = read_json(validation_path)
    apk = report.get("apk", {})
    manifest = apk.get("manifest_metadata", {})
    forensic = apk.get("forensic_summary", {})
    match_summary = report.get("match_summary", {})
    osv = report.get("osv")
    expected_components = [
        {
            "coordinate": result["coordinate"],
            "version": result["version"],
            "purl": result["purl"],
            "status": result["status"],
            "match_type": result.get("match_type"),
            "confidence": result.get("confidence"),
            "evidence_line": result.get("evidence_line"),
        }
        for result in validation.get("results", [])
        if result.get("kind") == "sbom-component"
    ]
    extra_candidates = [
        {
            "coordinate": result["coordinate"],
            "version": result["version"],
            "purl": result["purl"],
            "status": result["status"],
            "source_versions": result.get("source_versions", []),
        }
        for result in validation.get("results", [])
        if result.get("kind") == "candidate"
    ]
    return [
        {
            "id": "real-fdroid-1.23.2",
            "dataset_layer": "source-validated-real",
            "validation_level": "L2 source validated",
            "metrics_allowed": [
                "version correctness",
                "emitted-component source confirmation",
                "emitted-component false positives",
                "candidate mismatch analysis",
                "reference-scope recall only after expected DB-intersection is computed",
            ],
            "apk_path": normalize_path(apk.get("apk_path", "")),
            "apk_sha256": apk.get("apk_sha256"),
            "apk_size": apk.get("apk_size"),
            "download_source": "F-Droid package repository",
            "release_era": "modern",
            "source_type": "real APK with source dependency-tree validation",
            "app_package": manifest.get("package_name"),
            "package_name": manifest.get("package_name"),
            "version_name": manifest.get("version_name"),
            "version_code": manifest.get("version_code"),
            "min_sdk": manifest.get("min_sdk"),
            "target_sdk": manifest.get("target_sdk"),
            "primary_language": "Java and Kotlin",
            "language": "Java and Kotlin",
            "source_language_counts": count_fdroid_source_files(Path("data/source/fdroidclient-1.23.2")),
            "framework_type": "Android Gradle / Jetpack",
            "framework_or_library_type": (
                "Android Gradle app using AndroidX/Jetpack, Compose, Ktor, OkHttp, "
                "and native AndroidX graphics path libraries"
            ),
            "source_repository": "https://gitlab.com/fdroid/fdroidclient",
            "source_reference": "data/source/fdroidclient-1.23.2",
            "source_tag_or_commit": "1.23.2",
            "apk_source_version_match": "yes: APK versionName 1.23.2 and versionCode 1023052 match the source release metadata",
            "build_system": "Gradle Android",
            "dependency_tree_path": "data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt",
            "dependency_tree_configuration": ":app:fullReleaseRuntimeClasspath",
            "source_validation_status": "complete",
            "source_validation_basis": (
                "Gradle :app:fullReleaseRuntimeClasspath dependency tree for F-Droid "
                "version 1.23.2 / versionCode 1023052."
            ),
            "r8_used": "yes, according to app/build.gradle minifyEnabled true",
            "r8_proguard_status": "R8/minification enabled by Android Gradle build config",
            "r8_mode": "release minification plus resource shrinking; exact optimizer details are treated as source-level evidence",
            "obfuscation": "release minification and resource shrinking enabled",
            "obfuscation_level": match_summary.get("obfuscation_risk", {}).get("level", "low"),
            "obfuscation_details": (
                "Source build config enables minifyEnabled and shrinkResources for all "
                "build types; the APK-side report still classifies matching risk as low."
            ),
            "minification_evidence": "source build config plus APK-side forensic report",
            "resource_shrinking": "yes, according to source build config",
            "packer_protector_indicators": indicator_summary(forensic),
            "dynamic_loading_indicators": "none confirmed; nonstandard DEX list is tracked by APK forensic summary",
            "dex_files": apk.get("dex_files", []),
            "dex_count": len(apk.get("dex_files", [])),
            "multidex": apk.get("has_multidex"),
            "native_libraries": apk.get("native_libraries", []),
            "native_so_count": len(apk.get("native_libraries", [])),
            "native_abi_list": native_abi_list(apk.get("native_libraries", [])),
            "manifest_metadata_available": bool(manifest.get("package_name")),
            "resources_available": apk.get("resources_arsc_present"),
            "forensic_summary": forensic,
            "androidx_jetpack_usage": "heavy",
            "kotlin_kmp_artifacts": "present: Ktor/Compose/Android target variants appear in the calibrated DB",
            "main_library_families": [
                "AndroidX/Jetpack",
                "Compose",
                "Kotlin/Ktor",
                "networking",
                "native hash-only files",
            ],
            "expected_third_party_dependency_count": validation.get("source_components"),
            "transitive_dependency_complexity": "high",
            "overlapping_artifact_families": "Okio/Okio-JVM and AndroidX/KMP target variants",
            "known_vulnerable_dependency_expected": "no confirmed vulnerability in current calibrated OSV result",
            "expected_components": expected_components,
            "detected_components": detected_components_from_report(report),
            "source_validation": {
                "source_components": validation.get("source_components"),
                "sbom_components": validation.get("sbom_components"),
                "confirmed": validation.get("confirmed"),
                "version_mismatches": validation.get("version_mismatches"),
                "missing": validation.get("missing"),
                "extra_candidates": validation.get("extra_candidates"),
                "candidate_version_mismatches": validation.get("candidate_version_mismatches"),
            },
            "extra_candidates_checked": extra_candidates,
            "osv": summarize_osv(osv),
            "report_path": normalize_path(str(report_path)),
            "source_validation_path": normalize_path(str(validation_path)),
        }
    ]


def build_opentracks_inventory(report_path: Path, validation_path: Path) -> list[dict[str, Any]]:
    if not report_path.exists() or not validation_path.exists():
        return []

    report = read_json(report_path)
    validation = read_json(validation_path)
    apk = report.get("apk", {})
    manifest = apk.get("manifest_metadata", {})
    forensic = apk.get("forensic_summary", {})
    match_summary = report.get("match_summary", {})
    osv = report.get("osv")
    source_root = Path(
        "data/source/opentracks-v4.27.0irreproducible/source/"
        "de.dennisguse.opentracks_6653_src.tar.gz"
    )
    expected_components = [
        {
            "coordinate": result["coordinate"],
            "version": result["version"],
            "purl": result["purl"],
            "status": result["status"],
            "match_type": result.get("match_type"),
            "confidence": result.get("confidence"),
            "evidence_line": result.get("evidence_line"),
        }
        for result in validation.get("results", [])
        if result.get("kind") == "sbom-component"
    ]
    extra_candidates = [
        {
            "coordinate": result["coordinate"],
            "version": result["version"],
            "purl": result["purl"],
            "status": result["status"],
            "source_versions": result.get("source_versions", []),
        }
        for result in validation.get("results", [])
        if result.get("kind") == "candidate"
    ]
    return [
        {
            "id": "real-opentracks-v4.27.0irreproducible",
            "dataset_layer": "source-validated-real",
            "validation_level": "L2 source validated",
            "metrics_allowed": [
                "version correctness",
                "emitted-component source confirmation",
                "emitted-component false positives",
                "reference-scope recall only after expected DB-intersection is computed",
            ],
            "apk_path": normalize_path(apk.get("apk_path", "")),
            "apk_sha256": apk.get("apk_sha256"),
            "apk_size": apk.get("apk_size"),
            "download_source": "F-Droid package repository",
            "release_era": "modern",
            "source_type": "real APK with source dependency-tree validation",
            "app_package": manifest.get("package_name"),
            "package_name": manifest.get("package_name"),
            "version_name": manifest.get("version_name"),
            "version_code": manifest.get("version_code"),
            "min_sdk": manifest.get("min_sdk"),
            "target_sdk": manifest.get("target_sdk"),
            "primary_language": "Java",
            "language": "Java",
            "source_language_counts": count_source_files(source_root),
            "framework_type": "Android Gradle / AndroidX",
            "framework_or_library_type": (
                "Android Gradle app using AndroidX, Material Components, Kotlin "
                "runtime libraries, and WorkManager"
            ),
            "source_repository": "https://codeberg.org/OpenTracksApp/OpenTracks",
            "source_reference": normalize_path(str(source_root)),
            "source_tag_or_commit": "f143aabfbf77d1b71864042fe4f0bbf2b4174f4f",
            "apk_source_version_match": (
                "yes: APK versionName v4.27.0irreproducible and versionCode 6653 "
                "match the F-Droid metadata/source build evidence"
            ),
            "build_system": "Gradle Android",
            "dependency_tree_path": (
                "data/results/source-validation/opentracks/fullReleaseRuntimeClasspath.txt"
            ),
            "dependency_tree_configuration": "irreproducibleReleaseRuntimeClasspath",
            "source_validation_status": "complete",
            "source_validation_basis": (
                "Gradle irreproducibleReleaseRuntimeClasspath dependency tree for "
                "OpenTracks versionCode 6653 from the F-Droid source tarball."
            ),
            "r8_used": "no, according to source build.gradle minifyEnabled false",
            "r8_proguard_status": "R8/minification disabled by release build config",
            "r8_mode": "none",
            "obfuscation": "no source-level minification evidence for this release build",
            "obfuscation_level": match_summary.get("obfuscation_risk", {}).get("level", "low"),
            "obfuscation_details": (
                "Source build.gradle sets release minifyEnabled false; APK-side "
                "forensic/matching risk is low."
            ),
            "minification_evidence": "source build.gradle plus APK-side forensic report",
            "resource_shrinking": "no source-level evidence in current proof bundle",
            "packer_protector_indicators": indicator_summary(forensic),
            "dynamic_loading_indicators": "none confirmed; nonstandard DEX list is tracked by APK forensic summary",
            "dex_files": apk.get("dex_files", []),
            "dex_count": len(apk.get("dex_files", [])),
            "multidex": apk.get("has_multidex"),
            "native_libraries": apk.get("native_libraries", []),
            "native_so_count": len(apk.get("native_libraries", [])),
            "native_abi_list": native_abi_list(apk.get("native_libraries", [])),
            "manifest_metadata_available": bool(manifest.get("package_name")),
            "resources_available": apk.get("resources_arsc_present"),
            "forensic_summary": forensic,
            "androidx_jetpack_usage": "heavy",
            "kotlin_kmp_artifacts": (
                "present as overlapping AndroidX Lifecycle public/Android target variants"
            ),
            "main_library_families": [
                "AndroidX/Jetpack",
                "Material Components",
                "Kotlin coroutines/runtime",
                "WorkManager",
                "location/maps support",
            ],
            "expected_third_party_dependency_count": validation.get("source_components"),
            "transitive_dependency_complexity": "medium",
            "overlapping_artifact_families": (
                "AndroidX Lifecycle public coordinates and Android target variants"
            ),
            "known_vulnerable_dependency_expected": "no confirmed vulnerability in current calibrated OSV result",
            "expected_components": expected_components,
            "detected_components": detected_components_from_report(report),
            "source_validation": {
                "source_components": validation.get("source_components"),
                "sbom_components": validation.get("sbom_components"),
                "confirmed": validation.get("confirmed"),
                "version_mismatches": validation.get("version_mismatches"),
                "missing": validation.get("missing"),
                "extra_candidates": validation.get("extra_candidates"),
                "candidate_version_mismatches": validation.get("candidate_version_mismatches"),
            },
            "extra_candidates_checked": extra_candidates,
            "osv": summarize_osv(osv),
            "report_path": normalize_path(str(report_path)),
            "source_validation_path": normalize_path(str(validation_path)),
        }
    ]


def build_tusky_inventory(report_path: Path, validation_path: Path) -> list[dict[str, Any]]:
    if not report_path.exists() or not validation_path.exists():
        return []

    report = read_json(report_path)
    validation = read_json(validation_path)
    apk = report.get("apk", {})
    manifest = apk.get("manifest_metadata", {})
    forensic = apk.get("forensic_summary", {})
    match_summary = report.get("match_summary", {})
    osv = report.get("osv")
    source_root = Path("data/source/tusky-32.2/source/com.keylesspalace.tusky_142_src.tar.gz")
    expected_components = [
        {
            "coordinate": result["coordinate"],
            "version": result["version"],
            "purl": result["purl"],
            "status": result["status"],
            "match_type": result.get("match_type"),
            "confidence": result.get("confidence"),
            "evidence_line": result.get("evidence_line"),
        }
        for result in validation.get("results", [])
        if result.get("kind") == "sbom-component"
    ]
    extra_candidates = [
        {
            "coordinate": result["coordinate"],
            "version": result["version"],
            "purl": result["purl"],
            "status": result["status"],
            "source_versions": result.get("source_versions", []),
        }
        for result in validation.get("results", [])
        if result.get("kind") == "candidate"
    ]
    return [
        {
            "id": "real-tusky-32.2",
            "dataset_layer": "source-validated-real",
            "validation_level": "L2 source validated",
            "metrics_allowed": [
                "version correctness for emitted components",
                "emitted-component source confirmation",
                "emitted-component false positives",
                "sparse-detection limitation discussion",
                "reference-scope recall only after expected DB-intersection is computed",
            ],
            "apk_path": normalize_path(apk.get("apk_path", "")),
            "apk_sha256": apk.get("apk_sha256"),
            "apk_size": apk.get("apk_size"),
            "download_source": "F-Droid package repository",
            "release_era": "modern",
            "source_type": "real APK with source dependency-tree validation",
            "app_package": manifest.get("package_name"),
            "package_name": manifest.get("package_name"),
            "version_name": manifest.get("version_name"),
            "version_code": manifest.get("version_code"),
            "min_sdk": manifest.get("min_sdk"),
            "target_sdk": manifest.get("target_sdk"),
            "primary_language": "Kotlin and Java",
            "language": "Kotlin and Java",
            "source_language_counts": count_source_files(source_root),
            "framework_type": "Android Gradle / Kotlin AndroidX",
            "framework_or_library_type": (
                "Android Gradle social client using Kotlin, AndroidX, Retrofit, "
                "OkHttp, Moshi, Coil, Glide, and native image/security libraries"
            ),
            "source_repository": "https://codeberg.org/tusky/Tusky",
            "source_reference": normalize_path(str(source_root)),
            "source_tag_or_commit": "ff0c9f58874fafc72a53789f079ce0dc1a7e9207",
            "apk_source_version_match": (
                "yes: APK versionName 32.2 and versionCode 142 match the F-Droid "
                "metadata/source build evidence"
            ),
            "build_system": "Gradle Android",
            "dependency_tree_path": "data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt",
            "dependency_tree_configuration": "blueReleaseRuntimeClasspath",
            "source_validation_status": "complete",
            "source_validation_basis": (
                "Gradle blueReleaseRuntimeClasspath dependency tree for Tusky "
                "versionCode 142 from the F-Droid source tarball."
            ),
            "r8_used": "yes, according to app/build.gradle release minifyEnabled true",
            "r8_proguard_status": "R8/minification enabled by release build config",
            "r8_mode": "release minification plus resource shrinking",
            "obfuscation": "release minification and resource shrinking enabled",
            "obfuscation_level": match_summary.get("obfuscation_risk", {}).get("level", "low"),
            "obfuscation_details": (
                "Source build.gradle sets release minifyEnabled true and shrinkResources true; "
                "the APK-side report still classifies matching risk as low, but emitted "
                "Maven recovery is sparse."
            ),
            "minification_evidence": "source build.gradle plus APK-side forensic report",
            "resource_shrinking": "yes, according to source build.gradle",
            "packer_protector_indicators": indicator_summary(forensic),
            "dynamic_loading_indicators": "none confirmed; nonstandard DEX list is tracked by APK forensic summary",
            "dex_files": apk.get("dex_files", []),
            "dex_count": len(apk.get("dex_files", [])),
            "multidex": apk.get("has_multidex"),
            "native_libraries": apk.get("native_libraries", []),
            "native_so_count": len(apk.get("native_libraries", [])),
            "native_abi_list": native_abi_list(apk.get("native_libraries", [])),
            "manifest_metadata_available": bool(manifest.get("package_name")),
            "resources_available": apk.get("resources_arsc_present"),
            "forensic_summary": forensic,
            "androidx_jetpack_usage": "heavy",
            "kotlin_kmp_artifacts": "present in the source tree through modern AndroidX/Kotlin dependencies",
            "main_library_families": [
                "AndroidX/Jetpack",
                "networking",
                "Retrofit/OkHttp",
                "Moshi",
                "image loading",
                "native hash-only files",
            ],
            "expected_third_party_dependency_count": validation.get("source_components"),
            "transitive_dependency_complexity": "high",
            "overlapping_artifact_families": "Retrofit/OkHttp/Okio and AndroidX/KMP target variants",
            "known_vulnerable_dependency_expected": "no confirmed vulnerability in current calibrated OSV result",
            "expected_components": expected_components,
            "detected_components": detected_components_from_report(report),
            "source_validation": {
                "source_components": validation.get("source_components"),
                "sbom_components": validation.get("sbom_components"),
                "confirmed": validation.get("confirmed"),
                "version_mismatches": validation.get("version_mismatches"),
                "missing": validation.get("missing"),
                "extra_candidates": validation.get("extra_candidates"),
                "candidate_version_mismatches": validation.get("candidate_version_mismatches"),
            },
            "extra_candidates_checked": extra_candidates,
            "osv": summarize_osv(osv),
            "report_path": normalize_path(str(report_path)),
            "source_validation_path": normalize_path(str(validation_path)),
        }
    ]


def build_conversations_inventory(report_path: Path, validation_path: Path) -> list[dict[str, Any]]:
    if not report_path.exists() or not validation_path.exists():
        return []

    report = read_json(report_path)
    validation = read_json(validation_path)
    apk = report.get("apk", {})
    manifest = apk.get("manifest_metadata", {})
    forensic = apk.get("forensic_summary", {})
    match_summary = report.get("match_summary", {})
    osv = report.get("osv")
    source_root = Path(
        "data/source/conversations/extracted/eu.siacs.conversations_4217704_src.tar.gz"
    )
    expected_components = [
        {
            "coordinate": result["coordinate"],
            "version": result["version"],
            "purl": result["purl"],
            "status": result["status"],
            "match_type": result.get("match_type"),
            "confidence": result.get("confidence"),
            "evidence_line": result.get("evidence_line"),
        }
        for result in validation.get("results", [])
        if result.get("kind") == "sbom-component"
    ]
    extra_candidates = [
        {
            "coordinate": result["coordinate"],
            "version": result["version"],
            "purl": result["purl"],
            "status": result["status"],
            "source_versions": result.get("source_versions", []),
        }
        for result in validation.get("results", [])
        if result.get("kind") == "candidate"
    ]
    return [
        {
            "id": "real-conversations-2.20.0-free",
            "dataset_layer": "source-validated-real-partial",
            "validation_level": "L2 source validated partial mismatch",
            "metrics_allowed": [
                "version correctness for emitted components",
                "emitted-component source confirmation",
                "near-version mismatch analysis",
                "artifact-family limitation discussion",
                "reference-scope recall only after expected DB-intersection is computed",
            ],
            "apk_path": normalize_path(apk.get("apk_path", "")),
            "apk_sha256": apk.get("apk_sha256"),
            "apk_size": apk.get("apk_size"),
            "download_source": "F-Droid package repository",
            "release_era": "modern app with older codebase history",
            "source_type": "real APK with source dependency-tree validation",
            "app_package": manifest.get("package_name"),
            "package_name": manifest.get("package_name"),
            "version_name": manifest.get("version_name"),
            "version_code": manifest.get("version_code"),
            "min_sdk": manifest.get("min_sdk"),
            "target_sdk": manifest.get("target_sdk"),
            "primary_language": "Java",
            "language": "Java",
            "source_language_counts": count_source_files(source_root),
            "framework_type": "Android Gradle / AndroidX",
            "framework_or_library_type": (
                "Android messaging/security app using AndroidX, Retrofit, OkHttp, "
                "Gson, Conscrypt, WebRTC, Bouncy Castle, and XMPP libraries"
            ),
            "source_repository": "https://codeberg.org/iNPUTmice/Conversations",
            "source_reference": normalize_path(str(source_root)),
            "source_tag_or_commit": "7346a14dcedb155762133ea3ec512fdf34b57876",
            "apk_source_version_match": (
                "yes: APK versionName 2.20.0+free and versionCode 4217704 "
                "match the F-Droid metadata/source build evidence"
            ),
            "build_system": "Gradle Android",
            "dependency_tree_path": (
                "data/results/source-validation/conversations/"
                "conversationsFreeReleaseRuntimeClasspath.txt"
            ),
            "dependency_tree_configuration": "conversationsFreeReleaseRuntimeClasspath",
            "source_validation_status": "partial-version-mismatch",
            "source_validation_basis": (
                "Gradle conversationsFreeReleaseRuntimeClasspath dependency tree for "
                "Conversations versionCode 4217704 from the F-Droid source archive."
            ),
            "r8_used": "yes, according to build.gradle release minifyEnabled true",
            "r8_proguard_status": "R8/minification enabled by release build config",
            "r8_mode": "release minification plus resource shrinking",
            "obfuscation": "release minification and resource shrinking enabled",
            "obfuscation_level": match_summary.get("obfuscation_risk", {}).get("level", "low"),
            "obfuscation_details": (
                "Source build.gradle sets release minifyEnabled true and shrinkResources true; "
                "the APK-side report classifies extraction risk and matching risk as low."
            ),
            "minification_evidence": "source build.gradle plus APK-side forensic report",
            "resource_shrinking": "yes, according to source build.gradle",
            "packer_protector_indicators": indicator_summary(forensic),
            "dynamic_loading_indicators": "none confirmed; nonstandard DEX list is tracked by APK forensic summary",
            "dex_files": apk.get("dex_files", []),
            "dex_count": len(apk.get("dex_files", [])),
            "multidex": apk.get("has_multidex"),
            "native_libraries": apk.get("native_libraries", []),
            "native_so_count": len(apk.get("native_libraries", [])),
            "native_abi_list": native_abi_list(apk.get("native_libraries", [])),
            "manifest_metadata_available": bool(manifest.get("package_name")),
            "resources_available": apk.get("resources_arsc_present"),
            "forensic_summary": forensic,
            "androidx_jetpack_usage": "heavy",
            "kotlin_kmp_artifacts": "present through OkHttp/Okio and AndroidX target-variant overlap",
            "main_library_families": [
                "AndroidX/Jetpack",
                "networking",
                "Retrofit/OkHttp",
                "Gson",
                "security/crypto",
                "native WebRTC/Conscrypt files",
            ],
            "expected_third_party_dependency_count": validation.get("source_components"),
            "transitive_dependency_complexity": "high",
            "overlapping_artifact_families": (
                "AndroidX near-version ties and Lifecycle public/Android target variants"
            ),
            "known_vulnerable_dependency_expected": "no confirmed vulnerability in current calibrated OSV result",
            "expected_components": expected_components,
            "detected_components": detected_components_from_report(report),
            "source_validation": {
                "source_components": validation.get("source_components"),
                "sbom_components": validation.get("sbom_components"),
                "confirmed": validation.get("confirmed"),
                "version_mismatches": validation.get("version_mismatches"),
                "missing": validation.get("missing"),
                "extra_candidates": validation.get("extra_candidates"),
                "candidate_version_mismatches": validation.get("candidate_version_mismatches"),
            },
            "extra_candidates_checked": extra_candidates,
            "osv": summarize_osv(osv),
            "report_path": normalize_path(str(report_path)),
            "source_validation_path": normalize_path(str(validation_path)),
        }
    ]


def load_reports(root: Path) -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for report_path in sorted(root.glob("**/report.json")):
        try:
            payload = read_json(report_path)
        except json.JSONDecodeError:
            continue
        apk_path = payload.get("apk", {}).get("apk_path")
        if not apk_path:
            continue
        payload["_report_path"] = str(report_path)
        key = normalize_path(apk_path)
        existing = reports.get(key)
        if existing is None or report_preference(report_path) > report_preference(Path(existing["_report_path"])):
            reports[key] = payload
    return reports


def report_preference(path: Path) -> tuple[int, float]:
    text = normalize_path(str(path))
    score = 0
    if "demo-osv" in text:
        score += 30
    if "final-demo" in text:
        score += 20
    if "calibrated" in text:
        score += 10
    return score, path.stat().st_mtime


def inspect_apk(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        dex_files = sorted(name for name in names if name.endswith(".dex"))
        native_libraries = sorted(
            name for name in names if name.startswith("lib/") and name.endswith(".so")
        )
        return {
            "sha256": digest.hexdigest(),
            "size": path.stat().st_size,
            "dex_files": dex_files,
            "multidex": len([name for name in dex_files if Path(name).name.startswith("classes")]) > 1,
            "native_libraries": native_libraries,
            "manifest_present": "AndroidManifest.xml" in names,
            "resources_arsc_present": "resources.arsc" in names,
            "zip_entries": len(names),
        }


def unknown_library_profile() -> dict[str, str]:
    return {
        "language": "unknown",
        "framework": "unknown",
        "family": "unknown",
        "androidx_usage": "unknown",
        "kmp_artifacts": "unknown",
        "overlap_family": "unknown",
        "vulnerable_expected": "unknown",
        "notes": "",
    }


def native_abi_list(native_libraries: list[Any]) -> list[str]:
    abis: set[str] = set()
    for item in native_libraries:
        path = item.get("path") if isinstance(item, dict) else str(item)
        parts = str(path).split("/")
        if len(parts) >= 3 and parts[0] == "lib":
            abis.add(parts[1])
        elif isinstance(item, dict) and item.get("abi"):
            abis.add(str(item["abi"]))
    return sorted(abis)


def indicator_summary(forensic: dict[str, Any]) -> str:
    indicators = forensic.get("indicators", []) if isinstance(forensic, dict) else []
    if not indicators:
        return "none"
    labels = []
    for indicator in indicators:
        if isinstance(indicator, dict):
            labels.append(
                str(
                    indicator.get("code")
                    or indicator.get("kind")
                    or indicator.get("message")
                    or indicator
                )
            )
        else:
            labels.append(str(indicator))
    return "; ".join(labels)


def count_fdroid_source_files(source_root: Path) -> dict[str, int]:
    roots = [source_root / "app" / "src"]
    libs_root = source_root / "libs"
    if libs_root.exists():
        roots.extend(path / "src" for path in sorted(libs_root.iterdir()) if (path / "src").exists())
    return {
        "java": count_files(roots, "*.java"),
        "kotlin": count_files(roots, "*.kt"),
        "xml": count_files(roots, "*.xml"),
        "gradle_files": count_files([source_root], "*.gradle") + count_files([source_root], "*.gradle.kts"),
    }


def count_source_files(source_root: Path) -> dict[str, int]:
    roots = [source_root]
    return {
        "java": count_files(roots, "*.java"),
        "kotlin": count_files(roots, "*.kt"),
        "xml": count_files(roots, "*.xml"),
        "gradle_files": count_files(roots, "*.gradle")
        + count_files(roots, "*.gradle.kts"),
    }


def count_files(roots: list[Path], pattern: str) -> int:
    return sum(1 for root in roots if root.exists() for _ in root.rglob(pattern))


def detected_components_from_report(report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not report:
        return []
    components: list[dict[str, Any]] = []
    for component in report.get("detected_components", []):
        group = component.get("group")
        artifact = component.get("artifact")
        if not group or not artifact:
            continue
        components.append(
            {
                "coordinate": f"{group}:{artifact}",
                "version": component.get("version"),
                "purl": component.get("purl"),
                "match_type": component.get("match_type"),
                "identity_status": component.get("identity_status"),
                "version_status": component.get("version_status"),
                "confidence": component.get("confidence"),
                "identity_confidence": component.get("identity_confidence"),
                "version_confidence": component.get("version_confidence"),
            }
        )
    return components


def compare_components(
    expected_components: list[dict[str, Any]],
    detected_components: list[dict[str, Any]],
) -> dict[str, Any]:
    expected_coordinates = {item["coordinate"] for item in expected_components}
    expected_pairs = {(item["coordinate"], item["version"]) for item in expected_components}
    detected_coordinates = {item["coordinate"] for item in detected_components}
    detected_pairs = {(item["coordinate"], item.get("version")) for item in detected_components}
    version_mismatches = [
        item
        for item in detected_components
        if item["coordinate"] in expected_coordinates
        and (item["coordinate"], item.get("version")) not in expected_pairs
    ]
    return {
        "component_true_positives": sorted(expected_coordinates & detected_coordinates),
        "version_true_positives": sorted(
            f"{coordinate}@{version}"
            for coordinate, version in expected_pairs & detected_pairs
        ),
        "false_positive_components": [
            item for item in detected_components if item["coordinate"] not in expected_coordinates
        ],
        "false_negative_components": [
            item for item in expected_components if item["coordinate"] not in detected_coordinates
        ],
        "version_mismatches": version_mismatches,
        "false_negative_versions": [
            item for item in expected_components if (item["coordinate"], item["version"]) not in detected_pairs
        ],
    }


def find_decision(report: dict[str, Any] | None, coordinate: str) -> dict[str, Any] | None:
    if not report:
        return None
    for decision in report.get("match_summary", {}).get("decisions", []):
        if decision.get("coordinate") == coordinate:
            return {
                "selected_version": decision.get("selected_version"),
                "version_decision": decision.get("version_decision"),
                "confidence_label": decision.get("confidence_label"),
                "score": decision.get("score"),
                "gap_to_next": decision.get("gap_to_next"),
            }
    return None


def osv_summary_from_report(report: dict[str, Any] | None) -> dict[str, Any]:
    if not report:
        return {"status": "not run"}
    return summarize_osv(report.get("osv"))


def summarize_osv(osv: dict[str, Any] | None) -> dict[str, Any]:
    if not osv:
        return {"status": "not run"}
    advisories = []
    for result in osv.get("results", []):
        for vulnerability in result.get("vulnerabilities", []):
            advisories.append(
                {
                    "coordinate": result.get("coordinate"),
                    "version": result.get("version"),
                    "id": vulnerability.get("id"),
                    "aliases": vulnerability.get("aliases", []),
                    "severity": vulnerability.get("severity"),
                    "summary": vulnerability.get("summary"),
                    "finding_confidence": result.get("finding_confidence"),
                }
            )
    return {
        "status": "ok",
        "components": osv.get("components"),
        "vulnerable_components": osv.get("vulnerable_components"),
        "vulnerabilities": osv.get("vulnerabilities"),
        "confirmed_vulnerabilities": osv.get("confirmed_vulnerabilities"),
        "potential_vulnerabilities": osv.get("potential_vulnerabilities"),
        "severity_counts": osv.get("severity_counts", {}),
        "advisories": advisories,
    }


def build_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# APK Testset Inventory And Ground Truth",
        "",
        "This file describes the APKs used to test the MVP and how their expected contents are known.",
        "It is meant to support false-positive and false-negative discussion in the thesis and supervisor demo.",
        "",
        "## Ground Truth Policy",
        "",
        f"- Controlled APKs: {inventory['ground_truth_policy']['controlled']}",
        f"- Real F-Droid APK: {inventory['ground_truth_policy']['real_fdroid']}",
        f"- Source-validated real APKs: {inventory['ground_truth_policy']['real_source_validated']}",
        f"- Limitation APKs: {inventory['ground_truth_policy']['limitation']}",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
    ]
    for key, value in inventory["summary"].items():
        lines.append(f"| {key.replace('_', ' ')} | {value} |")

    layer_counts: dict[str, int] = {}
    all_items = [
        *inventory["controlled_apks"],
        *inventory["real_apks"],
        *inventory.get("limitation_apks", []),
    ]
    for item in all_items:
        layer = item.get("dataset_layer", "unknown")
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    lines.extend(
        [
            "",
            "## Dataset Classification Coverage",
            "",
            "The dataset follows the criteria defined in `docs/evaluation/DATASET_DESIGN.md`.",
            "",
            "| Layer | APKs | Validation level | Metrics allowed |",
            "|---|---:|---|---|",
        ]
    )
    for layer, count in sorted(layer_counts.items()):
        sample = next(
            item
            for item in all_items
            if item.get("dataset_layer") == layer
        )
        lines.append(
            "| "
            f"{layer} | "
            f"{count} | "
            f"{sample.get('validation_level', 'unknown')} | "
            f"{', '.join(sample.get('metrics_allowed', []))} |"
        )

    lines.extend(
        [
            "",
            "## Controlled APK Fixtures",
            "",
            "Controlled fixtures use package `com.example.fixture`, declare exact expected Maven components in `.ground-truth.json`, and currently include both single-DEX/single-library APKs and multi-library multidex APKs. They include no native `.so` files.",
            "",
            "| APK | Expected component | Library / language | Variant | R8 mode | Obfuscation | DEX | Native | Current result | FP | FN | OSV |",
            "|---|---|---|---|---|---|---:|---:|---|---:|---:|---|",
        ]
    )
    for item in inventory["controlled_apks"]:
        expected_components = item["expected_components"]
        decisions = item.get("truth_decisions") or [item.get("truth_decision") or {}]
        expected_label = "<br>".join(
            f"`{component['coordinate']}@{component['version']}`"
            for component in expected_components
        )
        result = "missing"
        if len(item["comparison"]["version_true_positives"]) == len(expected_components):
            labels = sorted(
                {
                    f"{decision.get('version_decision', 'detected')}/"
                    f"{decision.get('confidence_label', 'unknown')}"
                    for decision in decisions
                    if decision
                }
            )
            result = ", ".join(labels) if labels else "detected"
            if len(expected_components) > 1:
                result = f"all matched: {result}"
        elif item["comparison"]["version_true_positives"]:
            result = "partial version match"
        elif item["comparison"]["component_true_positives"]:
            result = "component only"
        fp = len(item["comparison"]["false_positive_components"])
        fn = len(item["comparison"]["false_negative_components"])
        osv = item["osv"]
        osv_text = "not run"
        if osv.get("status") == "ok":
            osv_text = f"{osv.get('vulnerabilities', 0)} vulns"
        lines.append(
            "| "
            f"`{Path(item['apk_path']).name}` | "
            f"{expected_label} | "
            f"{item['framework_or_library_type']} / {item['language']} | "
            f"{item['variant']} | "
            f"{item['r8_mode']} | "
            f"{item['obfuscation_level']} | "
            f"{len(item['dex_files'])} | "
            f"{item['native_so_count']} | "
            f"{result} | "
            f"{fp} | "
            f"{fn} | "
            f"{osv_text} |"
        )

    if inventory.get("limitation_apks"):
        lines.extend(
            [
                "",
                "## Limitation APK Fixtures",
                "",
                "Limitation fixtures are not used for precision/recall. They test whether the MVP reports unsupported dynamic/protected packaging cautiously.",
                "",
                "| APK | Limitation type | Extraction risk | Obfuscation risk | DEX analyzed/failed | Indicators | Components | Report |",
                "|---|---|---|---|---:|---|---:|---|",
            ]
        )
        for item in inventory["limitation_apks"]:
            forensic = item.get("forensic_summary", {})
            risk = item.get("obfuscation_risk", {})
            indicators = indicator_summary(forensic)
            lines.append(
                "| "
                f"`{Path(item['apk_path']).name}` | "
                f"{item['framework_or_library_type']} | "
                f"{forensic.get('extraction_risk', 'unknown')} | "
                f"{risk.get('level', 'unknown')} | "
                f"{item.get('dex_files_analyzed', 0)}/{item.get('dex_files_failed', 0)} | "
                f"{indicators} | "
                f"{len(item.get('detected_components', []))} | "
                f"`{item.get('report_path') or ''}` |"
            )

    lines.extend(
        [
            "",
            "## Real APK Case Study",
            "",
        ]
    )
    for item in inventory["real_apks"]:
        validation = item["source_validation"]
        osv = item["osv"]
        source_counts = item.get("source_language_counts", {})
        lines.extend(
            [
                f"### {item['id']}",
                "",
                "| Field | Value |",
                "|---|---|",
                f"| Dataset layer | {item['dataset_layer']} |",
                f"| Validation level | {item['validation_level']} |",
                f"| APK | `{item['apk_path']}` |",
                f"| APK SHA-256 | `{item['apk_sha256']}` |",
                f"| Download source | {item['download_source']} |",
                f"| Package | `{item['app_package']}` |",
                f"| Version | `{item['version_name']}` / code `{item['version_code']}` |",
                f"| Release era | {item['release_era']} |",
                f"| Language/framework | {item['framework_or_library_type']} |",
                f"| Main library families | {', '.join(item['main_library_families'])} |",
                f"| AndroidX/Jetpack usage | {item['androidx_jetpack_usage']} |",
                f"| Kotlin/KMP artifacts | {item['kotlin_kmp_artifacts']} |",
                f"| Source files counted | {source_counts.get('java', 0)} Java, {source_counts.get('kotlin', 0)} Kotlin, {source_counts.get('xml', 0)} XML, {source_counts.get('gradle_files', 0)} Gradle files |",
                f"| Source repository | `{item['source_repository']}` |",
                f"| Source reference | `{item['source_reference']}` |",
                f"| Source tag/commit | `{item['source_tag_or_commit']}` |",
                f"| APK/source version match | {item['apk_source_version_match']} |",
                f"| Build system | {item['build_system']} |",
                f"| Dependency tree | `{item['dependency_tree_path']}` |",
                f"| Dependency tree configuration | `{item['dependency_tree_configuration']}` |",
                f"| DEX files | {len(item['dex_files'])} ({', '.join(item['dex_files'])}) |",
                f"| Multidex | {str(item['multidex']).lower()} |",
                f"| Native files | {item['native_so_count']} hash-only components |",
                f"| Native ABIs | {', '.join(item['native_abi_list']) or 'none'} |",
                f"| R8/minification | {item['r8_proguard_status']} |",
                f"| R8 mode | {item['r8_mode']} |",
                f"| Resource shrinking | {item['resource_shrinking']} |",
                f"| Obfuscation assessment | {item['obfuscation_level']} risk |",
                f"| Packer/protector indicators | {item['packer_protector_indicators']} |",
                f"| Dynamic loading indicators | {item['dynamic_loading_indicators']} |",
                f"| Dependency complexity | {item['transitive_dependency_complexity']} ({item['expected_third_party_dependency_count']} source Maven entries parsed) |",
                f"| Overlapping artifact families | {item['overlapping_artifact_families']} |",
                f"| Vulnerable dependency expected | {item['known_vulnerable_dependency_expected']} |",
                f"| OSV result | {osv.get('vulnerabilities', 0)} vulnerabilities across {osv.get('vulnerable_components', 0)} vulnerable components |",
                f"| Source validation | {validation.get('confirmed')}/{validation.get('sbom_components')} confirmed, {validation.get('version_mismatches')} mismatches, {validation.get('missing')} missing |",
                f"| Full source dependency tree size | {validation.get('source_components')} Maven entries parsed |",
                "",
                "### Source-Confirmed Components",
                "",
                "| Component | Version | Match type | APK confidence | Source status |",
                "|---|---:|---|---:|---|",
            ]
        )
        for component in item["expected_components"]:
            confidence = component.get("confidence")
            confidence_text = f"{confidence:.3f}" if isinstance(confidence, (float, int)) else ""
            lines.append(
                "| "
                f"`{component['coordinate']}` | "
                f"{component['version']} | "
                f"{component.get('match_type', '')} | "
                f"{confidence_text} | "
                f"{component.get('status', '')} |"
            )
        if item["extra_candidates_checked"]:
            lines.extend(
                [
                    "",
                    "### Extra Candidate Check",
                    "",
                    "| Candidate | MVP version | Source versions | Status |",
                    "|---|---:|---|---|",
                ]
            )
            for candidate in item["extra_candidates_checked"]:
                lines.append(
                    "| "
                    f"`{candidate['coordinate']}` | "
                    f"{candidate['version']} | "
                    f"{', '.join(candidate.get('source_versions', []))} | "
                    f"{candidate['status']} |"
                )

    lines.extend(
        [
            "",
            "## Interpretation For FP/FN Analysis",
            "",
            "- On controlled APKs, false positives and false negatives can be measured directly because each APK contains exactly one known Maven component/version.",
            "- On the calibrated F-Droid APK, the current thesis-grade claim is version correctness for the 23 emitted SBOM components, validated against source. It is not a claim that all 203 source dependency-tree entries are recovered.",
            "- On the calibrated OpenTracks APK, the claim is version correctness for the 19 emitted SBOM components, validated against the resolved Gradle dependency tree.",
            "- On the calibrated Tusky APK, the one emitted Maven component is source-confirmed after adding the source-used Retrofit 3.0.0 reference. Treat it as a sparse source-validated case, not a broad recall result.",
            "- The full expanded F-Droid smoke test is useful as a stress test because it intentionally shows how latest-only broad references can introduce version mismatches.",
            "",
            "## Regeneration Command",
            "",
            "```powershell",
            "python scripts/build_apk_testset_inventory.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
