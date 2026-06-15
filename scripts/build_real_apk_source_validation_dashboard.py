from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_APK_TYPE_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/real-apk-source-validation-dashboard.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/REAL_APK_SOURCE_VALIDATION_DASHBOARD_REPORT.md")
DEFAULT_CASES_CSV = Path("data/results/evaluation/real-apk-source-validation-dashboard-cases.csv")
DEFAULT_MISSES_CSV = Path("data/results/evaluation/real-apk-source-validation-dashboard-misses.csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build dashboard-ready real APK classification and source-validation miss report.",
    )
    parser.add_argument("--apk-type-json", default=str(DEFAULT_APK_TYPE_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--cases-csv", default=str(DEFAULT_CASES_CSV))
    parser.add_argument("--misses-csv", default=str(DEFAULT_MISSES_CSV))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    apk_type_path = Path(args.apk_type_json)
    payload = build_dashboard(read_json(apk_type_path), apk_type_path=apk_type_path)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    write_cases_csv(Path(args.cases_csv), payload["cases"])
    write_misses_csv(Path(args.misses_csv), payload["miss_rows"])

    print(
        json.dumps(
            {
                "cases": len(payload["cases"]),
                "counted_source_validated_real_apks": payload["summary"][
                    "counted_source_validated_real_apks"
                ],
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "cases_csv": normalize_path(Path(args.cases_csv)),
                "misses_csv": normalize_path(Path(args.misses_csv)),
                "miss_rows": len(payload["miss_rows"]),
                "source_linked_blocked_cases": payload["summary"]["source_linked_blocked_cases"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_dashboard(apk_type: dict[str, Any], *, apk_type_path: Path) -> dict[str, Any]:
    cases = [build_case(case) for case in apk_type.get("real_cases", [])]
    miss_rows = [miss for case in cases for miss in case["miss_rows"]]
    summary = build_summary(apk_type.get("summary", {}), cases, miss_rows)
    return {
        "schema_version": 1,
        "sources": {
            "apk_type": normalize_path(apk_type_path),
            "note": "Generated from apk-type evaluation, report JSON files, and source-validation JSON files.",
        },
        "summary": summary,
        "aggregate_misses": aggregate_misses(miss_rows),
        "cases": cases,
        "miss_rows": miss_rows,
    }


def build_case(case: dict[str, Any]) -> dict[str, Any]:
    report = read_json_if_exists(case.get("report_path"))
    validation = read_json_if_exists(case.get("validation_path"))
    tags = [str(tag) for tag in case.get("tags", [])]
    manifest = ((report or {}).get("apk") or {}).get("manifest_metadata") or {}
    apk_info = (report or {}).get("apk") or {}

    validation_summary = validation_counts(case, validation)
    feature_labels = build_feature_labels(case, report, tags, manifest)
    miss_rows = build_miss_rows(case, validation)
    uncertainty = build_uncertainty_summary(report)

    return {
        "case_id": case.get("case_id"),
        "name": case.get("name"),
        "role": case.get("role"),
        "metric_bucket": metric_bucket(case.get("role")),
        "counted_in_100_source_validated_real_apks": case.get("role")
        in {"clean-source-validated", "source-validated-partial"},
        "source_validation_gate": source_validation_gate(case.get("role")),
        "classification": {
            "feature_labels": feature_labels,
            "classification_summary": classification_summary(case, feature_labels),
            "release_profile": release_profile(tags, manifest),
            "framework_profile": framework_profile(tags),
            "r8_obfuscation_profile": r8_obfuscation_profile(tags, report),
            "native_profile": native_profile(case),
            "dex_profile": dex_profile(case, apk_info),
        },
        "apk_metadata": {
            "package_name": manifest.get("package_name"),
            "version_name": manifest.get("version_name"),
            "version_code": manifest.get("version_code"),
            "min_sdk": manifest.get("min_sdk"),
            "target_sdk": manifest.get("target_sdk"),
            "apk_sha256": apk_info.get("apk_sha256"),
            "apk_size": apk_info.get("apk_size"),
            "dex_count": case.get("dex_count"),
            "native_so_files": case.get("native_files"),
            "maven_components": case.get("maven_components"),
            "extraction_risk": case.get("extraction_risk"),
            "obfuscation_risk": case.get("obfuscation_risk"),
        },
        "validation_stats": validation_summary,
        "miss_stats": summarize_misses(miss_rows),
        "uncertainty_summary": uncertainty,
        "miss_rows": miss_rows,
        "description": {
            "expected_difficulty": case.get("expected_difficulty"),
            "interpretation": case.get("interpretation"),
            "next_improvement": case.get("next_improvement"),
        },
        "tags": tags,
        "paths": {
            "report": case.get("report_path"),
            "validation": case.get("validation_path"),
            "proof": case.get("proof_path"),
        },
    }


def validation_counts(case: dict[str, Any], validation: dict[str, Any] | None) -> dict[str, Any]:
    compact = case.get("validation") or {}
    if validation:
        confirmed = int(validation.get("confirmed", compact.get("confirmed") or 0))
        mismatches = int(
            validation.get("version_mismatches", compact.get("version_mismatches") or 0)
        )
        missing = int(validation.get("missing", compact.get("missing") or 0))
        candidate_mismatches = int(validation.get("candidate_version_mismatches", 0))
        candidate_missing = int(validation.get("candidate_missing", 0))
        checked = confirmed + mismatches + missing
        source_components = validation.get("source_components")
        dependency_tree = validation.get("dependency_tree_path")
    elif compact:
        confirmed = int(compact.get("confirmed") or 0)
        mismatches = int(compact.get("version_mismatches") or 0)
        missing = int(compact.get("missing") or 0)
        candidate_mismatches = 0
        candidate_missing = int(compact.get("candidate_issues") or 0)
        checked = int(compact.get("checked_components") or confirmed + mismatches + missing)
        source_components = None
        dependency_tree = None
    else:
        confirmed = mismatches = missing = candidate_mismatches = candidate_missing = checked = 0
        source_components = None
        dependency_tree = None

    rate = confirmed / checked if checked else None
    return {
        "confirmed": confirmed,
        "checked": checked,
        "version_mismatches": mismatches,
        "missing": missing,
        "candidate_version_mismatches": candidate_mismatches,
        "candidate_missing": candidate_missing,
        "candidate_issues": candidate_mismatches + candidate_missing,
        "source_components": source_components,
        "dependency_tree_path": dependency_tree,
        "confirmation_rate": rate,
        "confirmation_rate_percent": round(rate * 100, 1) if rate is not None else None,
    }


def build_feature_labels(
    case: dict[str, Any],
    report: dict[str, Any] | None,
    tags: list[str],
    manifest: dict[str, Any],
) -> list[str]:
    labels: list[str] = []
    role = str(case.get("role") or "")
    if role == "clean-source-validated":
        labels.append("clean source-validated")
    elif role == "source-validated-partial":
        labels.append("partial source-validated")
    elif role == "source-validated-no-maven-signal":
        labels.append("source-validated no-Maven-signal")
    elif role == "source-linked-blocked":
        labels.append("source-linked blocked")
    elif role.startswith("limitation"):
        labels.append("limitation/boundary")

    dex = case.get("dex_count")
    if isinstance(dex, int) and dex > 1:
        labels.append("multidex")
    elif isinstance(dex, int):
        labels.append("single-dex")

    native_files = case.get("native_files")
    if isinstance(native_files, int) and native_files > 0:
        labels.append("native .so files")
    elif isinstance(native_files, int):
        labels.append("no native .so files")

    labels.append(release_profile(tags, manifest))

    framework = framework_profile(tags)
    if framework != "standard Android/Gradle":
        labels.append(framework)

    r8_profile = r8_obfuscation_profile(tags, report)
    if r8_profile != "low/no obfuscation signal":
        labels.append(r8_profile)

    for tag in tags:
        if tag in {
            "security",
            "email",
            "messaging",
            "media",
            "multimedia",
            "maps",
            "cloud-storage",
            "file-transfer",
            "weather",
            "browser",
            "education",
            "productivity",
            "health",
            "vpn-security",
            "native-heavy",
            "older-dependency-profile",
            "legacy-jcenter",
            "strict-module-rescue",
            "strict-flavor-rescue",
            "validation-copy",
        }:
            labels.append(tag.replace("-", " "))

    return sorted(unique(labels))


def classification_summary(case: dict[str, Any], labels: list[str]) -> str:
    interpretation = str(case.get("interpretation") or "").rstrip(".")
    prefix = ", ".join(labels[:8])
    if interpretation:
        return f"{prefix}. {interpretation}."
    return prefix


def metric_bucket(role: str | None) -> str:
    if role in {"clean-source-validated", "source-validated-partial"}:
        return "counted-source-validated"
    if role == "source-validated-no-maven-signal":
        return "source-validated-no-maven-signal"
    if role == "source-linked-blocked":
        return "source-linked-blocked"
    if role and role.startswith("limitation"):
        return "limitation-boundary"
    return "other"


def source_validation_gate(role: str | None) -> str:
    if role in {"clean-source-validated", "source-validated-partial"}:
        return "complete-and-counted"
    if role == "source-validated-no-maven-signal":
        return "complete-but-not-counted-no-maven-signal"
    if role == "source-linked-blocked":
        return "blocked-before-dependency-tree"
    if role and role.startswith("limitation"):
        return "limitation-not-counted"
    return "unknown"


def release_profile(tags: list[str], manifest: dict[str, Any]) -> str:
    lowered = set(tags)
    if lowered & {
        "legacy-gradle",
        "legacy-jcenter",
        "older-dependency-profile",
        "older-profile",
        "older-long-lived",
        "jdk11",
    }:
        return "older/legacy dependency or toolchain"
    target_sdk = int_or_none(manifest.get("target_sdk"))
    if target_sdk is None:
        return "target SDK unknown"
    if target_sdk >= 35:
        return "modern target SDK"
    if target_sdk >= 31:
        return "recent target SDK"
    return "older target SDK"


def framework_profile(tags: list[str]) -> str:
    tagset = set(tags)
    frameworks = []
    if "react-native" in tagset:
        frameworks.append("React Native/framework boundary")
    if "cordova" in tagset:
        frameworks.append("Cordova")
    if "compose" in tagset:
        frameworks.append("Jetpack Compose")
    if "androidx-kmp" in tagset:
        frameworks.append("AndroidX/KMP")
    if "native-heavy" in tagset:
        frameworks.append("native-heavy boundary")
    if "framework-boundary" in tagset and not frameworks:
        frameworks.append("framework boundary")
    return ", ".join(frameworks) if frameworks else "standard Android/Gradle"


def r8_obfuscation_profile(tags: list[str], report: dict[str, Any] | None) -> str:
    tagset = set(tags)
    if "hidden-dex" in tagset or "protector-style" in tagset:
        return "hidden/protector-style code boundary"
    if "obfuscated" in tagset:
        return "obfuscated sample"
    if "r8-minified" in tagset or "r8-shrink" in tagset:
        return "R8/minified evidence"
    risk = ((report or {}).get("obfuscation_risk") or {}).get("level")
    if risk and risk not in {"low", "none"}:
        return f"{risk} obfuscation risk"
    return "low/no obfuscation signal"


def native_profile(case: dict[str, Any]) -> str:
    native_files = case.get("native_files")
    if isinstance(native_files, int) and native_files > 0:
        return f"native .so present ({native_files})"
    if isinstance(native_files, int):
        return "no native .so files"
    return "native status unknown"


def dex_profile(case: dict[str, Any], apk_info: dict[str, Any]) -> str:
    dex_count = case.get("dex_count")
    has_multidex = apk_info.get("has_multidex")
    if isinstance(dex_count, int) and dex_count > 1:
        return f"multidex ({dex_count} DEX files)"
    if has_multidex:
        return "multidex"
    if isinstance(dex_count, int):
        return f"single-dex ({dex_count} DEX file)"
    return "DEX profile unknown"


def build_miss_rows(case: dict[str, Any], validation: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not validation:
        return []
    rows = []
    for row in validation.get("results", []):
        status = str(row.get("status") or "")
        if status == "confirmed":
            continue
        kind = str(row.get("kind") or "")
        emitted = kind == "sbom-component"
        rows.append(
            {
                "case_id": case.get("case_id"),
                "case_name": case.get("name"),
                "case_role": case.get("role"),
                "kind": kind,
                "emitted_component": emitted,
                "status": status,
                "miss_class": miss_class(status, emitted),
                "coordinate": row.get("coordinate"),
                "tool_selected_version": row.get("version"),
                "source_versions": [str(v) for v in row.get("source_versions") or []],
                "source_requested_versions": [
                    str(v) for v in row.get("source_requested_versions") or []
                ],
                "real_package_and_version": real_package_and_version(row),
                "confidence": row.get("confidence"),
                "match_type": row.get("match_type"),
                "evidence_line": row.get("evidence_line"),
                "purl": row.get("purl"),
                "report_path": case.get("report_path"),
                "validation_path": case.get("validation_path"),
            }
        )
    return rows


def miss_class(status: str, emitted: bool) -> str:
    prefix = "emitted" if emitted else "candidate"
    if status == "version-mismatch":
        return f"{prefix}-wrong-version"
    if status == "missing":
        return f"{prefix}-package-missing-from-source-tree"
    return f"{prefix}-{status or 'unknown'}"


def real_package_and_version(row: dict[str, Any]) -> str:
    coordinate = str(row.get("coordinate") or "")
    versions = [str(v) for v in row.get("source_versions") or []]
    if versions:
        return ", ".join(f"{coordinate}@{version}" for version in versions)
    if row.get("status") == "missing":
        return "absent from resolved source dependency tree"
    return "unknown"


def summarize_misses(rows: list[dict[str, Any]]) -> dict[str, int]:
    emitted = [row for row in rows if row["emitted_component"]]
    candidate = [row for row in rows if not row["emitted_component"]]
    return {
        "emitted_wrong_version": sum(1 for row in emitted if row["status"] == "version-mismatch"),
        "emitted_missing_from_source_tree": sum(1 for row in emitted if row["status"] == "missing"),
        "candidate_wrong_version": sum(
            1 for row in candidate if row["status"] == "version-mismatch"
        ),
        "candidate_missing_from_source_tree": sum(1 for row in candidate if row["status"] == "missing"),
        "all_miss_rows": len(rows),
    }


def build_uncertainty_summary(report: dict[str, Any] | None) -> dict[str, Any]:
    summary = ((report or {}).get("version_uncertainty_summary") or {}).get("summary") or {}
    category_counts = summary.get("category_counts") or {}
    return {
        "uncertainty_rows": int(summary.get("uncertainty_rows") or 0),
        "version_decisions": int(summary.get("version_decisions") or 0),
        "low_confidence": int(category_counts.get("low-confidence-version") or 0),
        "near_tie": int(category_counts.get("near-tie") or 0),
        "single_reference_boundary": int(category_counts.get("single-reference-boundary") or 0),
        "explicit_version_ambiguity": int(category_counts.get("explicit-version-ambiguity") or 0),
        "uncertain_version": int(category_counts.get("uncertain-version") or 0),
    }


def build_summary(
    apk_summary: dict[str, Any],
    cases: list[dict[str, Any]],
    miss_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    role_counts = Counter(case["role"] for case in cases)
    counted = [
        case for case in cases if case["counted_in_100_source_validated_real_apks"]
    ]
    validation = [case["validation_stats"] for case in counted]
    confirmed = sum(item["confirmed"] for item in validation)
    checked = sum(item["checked"] for item in validation)
    mismatches = sum(item["version_mismatches"] for item in validation)
    missing = sum(item["missing"] for item in validation)
    return {
        "dashboard_cases": len(cases),
        "counted_source_validated_real_apks": len(counted),
        "clean_source_validated_real_apks": role_counts.get("clean-source-validated", 0),
        "partial_source_validated_real_apks": role_counts.get("source-validated-partial", 0),
        "source_validated_no_maven_signal_cases": role_counts.get(
            "source-validated-no-maven-signal", 0
        ),
        "source_linked_blocked_cases": role_counts.get("source-linked-blocked", 0),
        "limitation_boundary_cases": sum(
            count for role, count in role_counts.items() if str(role).startswith("limitation")
        ),
        "reported_apk_type_summary": apk_summary,
        "emitted_version_stats_for_counted_apks": {
            "confirmed": confirmed,
            "checked": checked,
            "version_mismatches": mismatches,
            "missing_from_source_tree": missing,
            "confirmation_rate": confirmed / checked if checked else None,
            "confirmation_rate_percent": round((confirmed / checked) * 100, 1)
            if checked
            else None,
        },
        "miss_row_counts": {
            "emitted_wrong_version": sum(
                1
                for row in miss_rows
                if row["emitted_component"] and row["status"] == "version-mismatch"
            ),
            "emitted_missing_from_source_tree": sum(
                1
                for row in miss_rows
                if row["emitted_component"] and row["status"] == "missing"
            ),
            "candidate_wrong_version": sum(
                1
                for row in miss_rows
                if not row["emitted_component"] and row["status"] == "version-mismatch"
            ),
            "candidate_missing_from_source_tree": sum(
                1
                for row in miss_rows
                if not row["emitted_component"] and row["status"] == "missing"
            ),
        },
    }


def aggregate_misses(miss_rows: list[dict[str, Any]]) -> dict[str, Any]:
    mismatch_coordinates: dict[str, Counter[str]] = defaultdict(Counter)
    mismatch_selected: dict[str, Counter[str]] = defaultdict(Counter)
    missing_coordinates: Counter[str] = Counter()
    db_growth: Counter[tuple[str, str]] = Counter()
    cases_by_coordinate: dict[str, set[str]] = defaultdict(set)

    for row in miss_rows:
        coordinate = str(row.get("coordinate") or "")
        if not coordinate:
            continue
        cases_by_coordinate[coordinate].add(str(row.get("case_id") or ""))
        if row.get("status") == "version-mismatch":
            selected = str(row.get("tool_selected_version") or "")
            if selected:
                mismatch_selected[coordinate][selected] += 1
            for source_version in row.get("source_versions") or []:
                mismatch_coordinates[coordinate][str(source_version)] += 1
                db_growth[(coordinate, str(source_version))] += 1
        elif row.get("status") == "missing":
            missing_coordinates[coordinate] += 1

    mismatch_rows = [
        {
            "coordinate": coordinate,
            "count": sum(source_versions.values()),
            "cases": sorted(cases_by_coordinate[coordinate]),
            "source_versions": dict(source_versions.most_common()),
            "tool_selected_versions": dict(mismatch_selected[coordinate].most_common()),
        }
        for coordinate, source_versions in mismatch_coordinates.items()
    ]
    missing_rows = [
        {
            "coordinate": coordinate,
            "count": count,
            "cases": sorted(cases_by_coordinate[coordinate]),
        }
        for coordinate, count in missing_coordinates.items()
    ]
    db_rows = [
        {
            "coordinate": coordinate,
            "source_version": source_version,
            "mismatch_count": count,
            "interpretation": (
                "Source-resolved version that the tool did not select in one or more APKs; "
                "consider reference coverage or scoped disambiguation, then rerun controls."
            ),
        }
        for (coordinate, source_version), count in db_growth.items()
    ]
    return {
        "version_mismatch_coordinates": sorted(
            mismatch_rows, key=lambda item: (-item["count"], item["coordinate"])
        ),
        "missing_from_source_tree_coordinates": sorted(
            missing_rows, key=lambda item: (-item["count"], item["coordinate"])
        ),
        "db_growth_candidates_from_source_versions": sorted(
            db_rows, key=lambda item: (-item["mismatch_count"], item["coordinate"])
        ),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    version_stats = summary["emitted_version_stats_for_counted_apks"]
    lines = [
        "# Real APK Source-Validation Dashboard Report",
        "",
        "Generated by `scripts/build_real_apk_source_validation_dashboard.py`.",
        "",
        "This report is meant as a dashboard seed: the Markdown is human-readable, while the JSON and CSV outputs contain the row-level details for filtering, charts, and database-growth planning.",
        "",
        "## Current Truth",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Counted source-validated real APKs | {summary['counted_source_validated_real_apks']} |",
        f"| Clean source-validated APKs | {summary['clean_source_validated_real_apks']} |",
        f"| Partial source-validated APKs | {summary['partial_source_validated_real_apks']} |",
        f"| Source-validated no-Maven-signal APKs | {summary['source_validated_no_maven_signal_cases']} |",
        f"| Current source-linked blocked APKs | {summary['source_linked_blocked_cases']} |",
        f"| Limitation/boundary cases | {summary['limitation_boundary_cases']} |",
        f"| Confirmed emitted Maven versions | {version_stats['confirmed']}/{version_stats['checked']} |",
        f"| Emitted wrong-version rows | {version_stats['version_mismatches']} |",
        f"| Emitted package-missing rows | {version_stats['missing_from_source_tree']} |",
        f"| Confirmation rate | {version_stats['confirmation_rate_percent']}% |",
        "",
        "Important: the counted source-validated real APK total is clean plus partial rows only. No-Maven-signal, source-linked blocked, smoke-only, and limitation rows stay outside emitted-version accuracy metrics until their proof gates qualify them.",
        "",
        "## Dashboard Files",
        "",
        "| File | Purpose |",
        "|---|---|",
        "| `data/results/evaluation/real-apk-source-validation-dashboard.json` | Full nested dashboard payload, including every case and every miss row. |",
        "| `data/results/evaluation/real-apk-source-validation-dashboard-cases.csv` | One row per APK/case for dashboard cards and filters. |",
        "| `data/results/evaluation/real-apk-source-validation-dashboard-misses.csv` | One row per wrong-version or missing-package source-validation result. |",
        "",
        "## Per-APK Classification Table",
        "",
        "| APK | Bucket | Classification | Validation | Wrong version | Missing package | Uncertainty | Evidence |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for case in payload["cases"]:
        stats = case["validation_stats"]
        misses = case["miss_stats"]
        uncertainty = case["uncertainty_summary"]
        validation_text = (
            f"{stats['confirmed']}/{stats['checked']}"
            if stats["checked"]
            else "not counted"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    md(str(case["name"])),
                    md(str(case["metric_bucket"])),
                    md(case["classification"]["classification_summary"]),
                    validation_text,
                    str(misses["emitted_wrong_version"]),
                    str(misses["emitted_missing_from_source_tree"]),
                    str(uncertainty["uncertainty_rows"]),
                    evidence_links(case),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Top Wrong-Version Coordinates",
            "",
            "| Coordinate | Count | Source versions seen | Tool-selected versions seen |",
            "|---|---:|---|---|",
        ]
    )
    for row in payload["aggregate_misses"]["version_mismatch_coordinates"][:30]:
        lines.append(
            f"| `{md(row['coordinate'])}` | {row['count']} | "
            f"{md(format_counter(row['source_versions']))} | "
            f"{md(format_counter(row['tool_selected_versions']))} |"
        )

    lines.extend(
        [
            "",
            "## Top Missing-From-Source Coordinates",
            "",
            "These are emitted or candidate coordinates that did not appear in the resolved source dependency tree. Treat them as over-emission/pruning evidence, not as database-growth targets unless a separate source check proves the package really should be present.",
            "",
            "| Coordinate | Count | Cases |",
            "|---|---:|---|",
        ]
    )
    for row in payload["aggregate_misses"]["missing_from_source_tree_coordinates"][:30]:
        lines.append(
            f"| `{md(row['coordinate'])}` | {row['count']} | {md(', '.join(row['cases']))} |"
        )

    lines.extend(
        [
            "",
            "## Top DB Growth Candidates From Source Versions",
            "",
            "These rows are source-resolved versions observed in wrong-version results. They are useful leads for expanding references or designing scoped disambiguation, but each candidate still needs guarded controls before changing the shared DB or scorer.",
            "",
            "| Coordinate | Source version | Mismatch count |",
            "|---|---|---:|",
        ]
    )
    for row in payload["aggregate_misses"]["db_growth_candidates_from_source_versions"][:40]:
        lines.append(
            f"| `{md(row['coordinate'])}` | `{md(row['source_version'])}` | {row['mismatch_count']} |"
        )

    lines.extend(
        [
            "",
            "## Metric Rules",
            "",
            "- Counted source-validated APKs require APK report, source artifact, runtime dependency tree, and `validate-source-deps` output.",
            "- Wrong-version rows mean the coordinate exists in source but the selected version differs; the report gives the real source version(s).",
            "- Missing-package rows mean the emitted coordinate was absent from the resolved source dependency tree; there is no real package/version to list for that coordinate in that source tree.",
            "- Source-linked blocked, no-Maven-signal, and limitation rows stay out of emitted-version accuracy metrics.",
            "",
        ]
    )
    return "\n".join(lines)


def write_cases_csv(path: Path, cases: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "case_id",
        "name",
        "role",
        "metric_bucket",
        "counted_in_100_source_validated_real_apks",
        "package_name",
        "version_name",
        "version_code",
        "min_sdk",
        "target_sdk",
        "dex_count",
        "native_so_files",
        "maven_components",
        "classification_summary",
        "feature_labels",
        "release_profile",
        "framework_profile",
        "r8_obfuscation_profile",
        "confirmed",
        "checked",
        "version_mismatches",
        "missing",
        "candidate_issues",
        "confirmation_rate_percent",
        "uncertainty_rows",
        "report_path",
        "validation_path",
        "proof_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            metadata = case["apk_metadata"]
            validation = case["validation_stats"]
            classification = case["classification"]
            writer.writerow(
                {
                    "case_id": case["case_id"],
                    "name": case["name"],
                    "role": case["role"],
                    "metric_bucket": case["metric_bucket"],
                    "counted_in_100_source_validated_real_apks": case[
                        "counted_in_100_source_validated_real_apks"
                    ],
                    "package_name": metadata.get("package_name"),
                    "version_name": metadata.get("version_name"),
                    "version_code": metadata.get("version_code"),
                    "min_sdk": metadata.get("min_sdk"),
                    "target_sdk": metadata.get("target_sdk"),
                    "dex_count": metadata.get("dex_count"),
                    "native_so_files": metadata.get("native_so_files"),
                    "maven_components": metadata.get("maven_components"),
                    "classification_summary": classification["classification_summary"],
                    "feature_labels": "; ".join(classification["feature_labels"]),
                    "release_profile": classification["release_profile"],
                    "framework_profile": classification["framework_profile"],
                    "r8_obfuscation_profile": classification["r8_obfuscation_profile"],
                    "confirmed": validation["confirmed"],
                    "checked": validation["checked"],
                    "version_mismatches": validation["version_mismatches"],
                    "missing": validation["missing"],
                    "candidate_issues": validation["candidate_issues"],
                    "confirmation_rate_percent": validation["confirmation_rate_percent"],
                    "uncertainty_rows": case["uncertainty_summary"]["uncertainty_rows"],
                    "report_path": case["paths"]["report"],
                    "validation_path": case["paths"]["validation"],
                    "proof_path": case["paths"]["proof"],
                }
            )


def write_misses_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "case_id",
        "case_name",
        "case_role",
        "kind",
        "emitted_component",
        "status",
        "miss_class",
        "coordinate",
        "tool_selected_version",
        "source_versions",
        "source_requested_versions",
        "real_package_and_version",
        "confidence",
        "match_type",
        "evidence_line",
        "purl",
        "report_path",
        "validation_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "source_versions": "; ".join(row.get("source_versions") or []),
                    "source_requested_versions": "; ".join(
                        row.get("source_requested_versions") or []
                    ),
                }
            )


def evidence_links(case: dict[str, Any]) -> str:
    links = []
    for label, key in (("report", "report"), ("validation", "validation"), ("proof", "proof")):
        path = case["paths"].get(key)
        if path:
            links.append(f"`{label}`")
    return ", ".join(links) if links else "none"


def format_counter(counter: dict[str, int]) -> str:
    return ", ".join(f"{key} ({value})" for key, value in counter.items())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_exists(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    candidate = Path(path)
    if not candidate.exists():
        return None
    return read_json(candidate)


def normalize_path(path: Path) -> str:
    return path.as_posix()


def int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def unique(values: list[str]) -> list[str]:
    result = []
    seen = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def md(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\n", " ")
        .replace("\r", " ")
    )


if __name__ == "__main__":
    raise SystemExit(main())
