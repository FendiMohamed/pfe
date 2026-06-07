from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_DASHBOARD_JSON = Path(
    "data/results/evaluation/real-apk-source-validation-dashboard.json"
)
DEFAULT_REFERENCE_DB = Path("data/reference_db/reference_features_calibrated_combined.sqlite")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/reference-db-coverage-first-dashboard.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md")
DEFAULT_CASES_CSV = Path("data/results/evaluation/reference-db-coverage-first-cases.csv")
DEFAULT_GAPS_CSV = Path("data/results/evaluation/reference-db-coverage-first-gaps.csv")

GRADLE_MODULE_RE = re.compile(
    r"(?P<group>[A-Za-z0-9_.-]+):"
    r"(?P<artifact>[A-Za-z0-9_.-]+):"
    r"(?P<requested>[^\s()]+)"
    r"(?:\s+->\s+(?P<resolved>[^\s()]+))?"
)
RICH_GRADLE_MODULE_RE = re.compile(
    r"(?P<group>[A-Za-z0-9_.-]+):"
    r"(?P<artifact>[A-Za-z0-9_.-]+):"
    r"\{(?P<constraint>[^}]+)\}"
    r"\s+->\s+(?P<resolved>[^\s()]+)"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build source-dependency/reference-DB coverage metrics before version "
            "optimization. This uses saved Gradle runtime dependency trees as the "
            "source denominator."
        ),
    )
    parser.add_argument("--source-dashboard-json", default=str(DEFAULT_SOURCE_DASHBOARD_JSON))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--cases-csv", default=str(DEFAULT_CASES_CSV))
    parser.add_argument("--gaps-csv", default=str(DEFAULT_GAPS_CSV))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_dashboard_path = Path(args.source_dashboard_json)
    reference_db_path = Path(args.reference_db)

    payload = build_payload(
        read_json(source_dashboard_path),
        reference_db_path=reference_db_path,
        source_dashboard_path=source_dashboard_path,
    )

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    write_cases_csv(Path(args.cases_csv), payload["cases"])
    write_gaps_csv(Path(args.gaps_csv), payload["gap_rows"])

    print(
        json.dumps(
            {
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "cases_csv": normalize_path(Path(args.cases_csv)),
                "gaps_csv": normalize_path(Path(args.gaps_csv)),
                "source_tree_cases": payload["summary"]["source_tree_cases"],
                "source_dependency_pairs": payload["summary"]["source_dependency_pairs"],
                "reference_exact_version_coverage_percent": payload["summary"][
                    "reference_exact_version_coverage_percent"
                ],
                "end_to_end_exact_source_recall_percent": payload["summary"][
                    "end_to_end_exact_source_recall_percent"
                ],
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    source_dashboard: dict[str, Any],
    *,
    reference_db_path: Path,
    source_dashboard_path: Path,
) -> dict[str, Any]:
    reference = load_reference_index(reference_db_path)
    cases = []
    gap_rows = []
    catalog_entries: dict[str, dict[str, Any]] = {}
    skipped_cases = []

    for case in source_dashboard.get("cases", []):
        dependency_tree_value = str(
            (case.get("validation_stats") or {}).get("dependency_tree_path") or ""
        )
        if not dependency_tree_value:
            skipped_cases.append(skipped_case(case, "no dependency tree path"))
            continue
        dependency_tree_path = Path(dependency_tree_value)
        if not dependency_tree_path.exists():
            skipped_cases.append(skipped_case(case, "dependency tree path missing on disk"))
            continue

        case_payload = build_case_payload(case, dependency_tree_path, reference)
        cases.append(case_payload)
        gap_rows.extend(case_payload["gap_rows"])
        for row in case_payload["source_rows"]:
            entry = catalog_entries.setdefault(
                row["coordinate"],
                {
                    "coordinate": row["coordinate"],
                    "source_versions": set(),
                    "cases": set(),
                    "roles": set(),
                    "coordinate_in_reference_db": row["coordinate_in_reference_db"],
                    "reference_versions": set(reference["versions_by_coordinate"].get(row["coordinate"], set())),
                },
            )
            entry["source_versions"].add(row["source_version"])
            entry["cases"].add(case_payload["case_id"])
            entry["roles"].add(case_payload["role"])

    summary = build_summary(source_dashboard, reference, cases, gap_rows, skipped_cases)
    observed_source_catalog = [
        {
            "coordinate": entry["coordinate"],
            "source_versions": sorted(entry["source_versions"]),
            "source_version_count": len(entry["source_versions"]),
            "case_count": len(entry["cases"]),
            "roles": sorted(entry["roles"]),
            "coordinate_in_reference_db": entry["coordinate_in_reference_db"],
            "reference_versions": sorted(entry["reference_versions"]),
            "reference_version_count": len(entry["reference_versions"]),
        }
        for entry in catalog_entries.values()
    ]
    observed_source_catalog.sort(
        key=lambda item: (
            item["coordinate_in_reference_db"],
            -item["case_count"],
            item["coordinate"],
        )
    )

    return {
        "schema_version": 1,
        "sources": {
            "source_validation_dashboard": normalize_path(source_dashboard_path),
            "reference_db": normalize_path(reference_db_path),
            "source_denominator": "Saved Gradle runtime dependency-tree files linked from source validation.",
        },
        "verdict": verdict(summary),
        "methodology": methodology(),
        "summary": summary,
        "top_reference_coordinate_gaps": top_coordinate_gaps(gap_rows, "coordinate-absent-from-reference-db"),
        "top_reference_version_gaps": top_coordinate_gaps(gap_rows, "version-absent-from-reference-db"),
        "top_detection_gaps_despite_db": top_coordinate_gaps(
            gap_rows,
            {
                "source-present-not-emitted-despite-exact-reference",
                "source-present-wrong-version-despite-exact-reference",
            },
        ),
        "observed_source_catalog": observed_source_catalog,
        "cases": cases,
        "gap_rows": gap_rows,
        "skipped_cases": skipped_cases,
    }


def build_case_payload(
    case: dict[str, Any],
    dependency_tree_path: Path,
    reference: dict[str, Any],
) -> dict[str, Any]:
    source_dependencies = parse_gradle_dependency_tree(dependency_tree_path.read_text(encoding="utf-8"))
    validation = read_json_if_exists((case.get("paths") or {}).get("validation"))
    emitted_by_coordinate = emitted_component_index(validation)
    source_rows = []
    gap_rows = []

    for coordinate, entry in sorted(source_dependencies.items()):
        for source_version in entry["resolved_versions"]:
            row = build_source_row(
                case,
                coordinate,
                source_version,
                entry,
                emitted_by_coordinate,
                reference,
                dependency_tree_path,
            )
            source_rows.append(row)
            if row["gap_class"] != "covered-and-emitted-exact":
                gap_rows.append(row)

    counters = Counter(row["gap_class"] for row in source_rows)
    emitted_counters = Counter(row["emitted_status"] for row in source_rows)
    db_coord_covered = sum(1 for row in source_rows if row["coordinate_in_reference_db"])
    db_exact_covered = sum(1 for row in source_rows if row["exact_version_in_reference_db"])
    emitted_exact = emitted_counters["emitted-exact"]
    source_pairs = len(source_rows)

    return {
        "case_id": case.get("case_id"),
        "name": case.get("name"),
        "role": case.get("role"),
        "metric_bucket": case.get("metric_bucket"),
        "counted_in_emitted_accuracy": bool(case.get("counted_in_100_source_validated_real_apks")),
        "dependency_tree_path": normalize_path(dependency_tree_path),
        "report_path": normalize_path((case.get("paths") or {}).get("report")),
        "validation_path": normalize_path((case.get("paths") or {}).get("validation")),
        "source_dependency_pairs": source_pairs,
        "source_coordinates": len(source_dependencies),
        "reference_coordinate_covered_pairs": db_coord_covered,
        "reference_exact_version_covered_pairs": db_exact_covered,
        "reference_coordinate_coverage_percent": percent(db_coord_covered, source_pairs),
        "reference_exact_version_coverage_percent": percent(db_exact_covered, source_pairs),
        "source_dependencies_emitted_exact": emitted_exact,
        "source_dependencies_emitted_wrong_version": emitted_counters[
            "emitted-coordinate-wrong-version"
        ],
        "source_dependencies_not_emitted": emitted_counters["not-emitted"],
        "end_to_end_exact_source_recall_percent": percent(emitted_exact, source_pairs),
        "gap_counts": dict(sorted(counters.items())),
        "source_rows": source_rows,
        "gap_rows": gap_rows,
    }


def build_source_row(
    case: dict[str, Any],
    coordinate: str,
    source_version: str,
    entry: dict[str, Any],
    emitted_by_coordinate: dict[str, list[dict[str, Any]]],
    reference: dict[str, Any],
    dependency_tree_path: Path,
) -> dict[str, Any]:
    reference_versions = reference["versions_by_coordinate"].get(coordinate, set())
    emitted_results = emitted_by_coordinate.get(coordinate, [])
    emitted_versions = sorted({str(result.get("version") or "") for result in emitted_results if result.get("version")})
    emitted_status = emitted_status_for_version(source_version, emitted_versions)
    coordinate_in_reference_db = bool(reference_versions)
    exact_version_in_reference_db = source_version in reference_versions
    gap_class = classify_gap(
        coordinate_in_reference_db=coordinate_in_reference_db,
        exact_version_in_reference_db=exact_version_in_reference_db,
        emitted_status=emitted_status,
    )

    return {
        "case_id": case.get("case_id"),
        "case_name": case.get("name"),
        "case_role": case.get("role"),
        "coordinate": coordinate,
        "source_version": source_version,
        "source_requested_versions": sorted(entry["requested_versions"]),
        "evidence_line": evidence_line_for_version(entry["occurrences"], source_version),
        "coordinate_in_reference_db": coordinate_in_reference_db,
        "exact_version_in_reference_db": exact_version_in_reference_db,
        "reference_versions": sorted(reference_versions),
        "emitted_status": emitted_status,
        "emitted_versions": emitted_versions,
        "gap_class": gap_class,
        "dependency_tree_path": normalize_path(dependency_tree_path),
        "validation_path": normalize_path((case.get("paths") or {}).get("validation")),
        "report_path": normalize_path((case.get("paths") or {}).get("report")),
    }


def build_summary(
    source_dashboard: dict[str, Any],
    reference: dict[str, Any],
    cases: list[dict[str, Any]],
    gap_rows: list[dict[str, Any]],
    skipped_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    source_pairs = sum(case["source_dependency_pairs"] for case in cases)
    source_coordinates = {row["coordinate"] for case in cases for row in case["source_rows"]}
    source_exact_pairs = {
        f"{row['coordinate']}@{row['source_version']}" for case in cases for row in case["source_rows"]
    }
    source_case_roles = Counter(str(case["role"]) for case in cases)
    db_coord_covered = sum(case["reference_coordinate_covered_pairs"] for case in cases)
    db_exact_covered = sum(case["reference_exact_version_covered_pairs"] for case in cases)
    emitted_exact = sum(case["source_dependencies_emitted_exact"] for case in cases)
    emitted_wrong = sum(case["source_dependencies_emitted_wrong_version"] for case in cases)
    not_emitted = sum(case["source_dependencies_not_emitted"] for case in cases)
    gap_classes = Counter(row["gap_class"] for row in gap_rows)
    emitted_stats = (source_dashboard.get("summary") or {}).get(
        "emitted_version_stats_for_counted_apks",
        {},
    )

    return {
        "source_tree_cases": len(cases),
        "source_tree_case_roles": dict(sorted(source_case_roles.items())),
        "skipped_cases": len(skipped_cases),
        "source_dependency_pairs": source_pairs,
        "unique_source_coordinates": len(source_coordinates),
        "unique_source_coordinate_version_pairs": len(source_exact_pairs),
        "reference_db_components": reference["component_count"],
        "reference_db_coordinates": len(reference["versions_by_coordinate"]),
        "reference_db_coordinate_version_pairs": reference["pair_count"],
        "reference_coordinate_covered_source_pairs": db_coord_covered,
        "reference_coordinate_coverage_percent": percent(db_coord_covered, source_pairs),
        "reference_exact_version_covered_source_pairs": db_exact_covered,
        "reference_exact_version_coverage_percent": percent(db_exact_covered, source_pairs),
        "source_dependencies_emitted_exact": emitted_exact,
        "source_dependencies_emitted_wrong_version": emitted_wrong,
        "source_dependencies_not_emitted": not_emitted,
        "end_to_end_exact_source_recall_percent": percent(emitted_exact, source_pairs),
        "gap_class_counts": dict(sorted(gap_classes.items())),
        "emitted_component_accuracy_denominator": {
            "checked": emitted_stats.get("checked"),
            "confirmed": emitted_stats.get("confirmed"),
            "version_mismatches": emitted_stats.get("version_mismatches"),
            "missing_from_source_tree": emitted_stats.get("missing_from_source_tree"),
            "confirmation_rate_percent": emitted_stats.get("confirmation_rate_percent"),
            "warning": (
                "This is emitted-component accuracy only; it is not full source dependency recall."
            ),
        },
        "coverage_first_next_step": (
            "Build a broad evaluation-only reference DB for every source-observed "
            "coordinate and every Maven/Google-published version that can produce "
            "bytecode, then evaluate source dependency recall before optimizing "
            "exact-version selection."
        ),
    }


def parse_gradle_dependency_tree(text: str) -> dict[str, dict[str, Any]]:
    occurrences_by_coordinate: dict[str, list[dict[str, str]]] = defaultdict(list)
    for raw_line in text.splitlines():
        rich_match = RICH_GRADLE_MODULE_RE.search(raw_line)
        if rich_match:
            coordinate = f"{rich_match.group('group')}:{rich_match.group('artifact')}"
            requested_version = "{" + rich_match.group("constraint").strip() + "}"
            resolved_version = rich_match.group("resolved").strip()
            occurrences_by_coordinate[coordinate].append(
                {
                    "requested_version": requested_version,
                    "resolved_version": resolved_version,
                    "line": raw_line.strip(),
                }
            )
            continue

        match = GRADLE_MODULE_RE.search(raw_line)
        if not match:
            continue
        coordinate = f"{match.group('group')}:{match.group('artifact')}"
        requested_version = match.group("requested").strip()
        resolved_version = (match.group("resolved") or requested_version).strip()
        occurrences_by_coordinate[coordinate].append(
            {
                "requested_version": requested_version,
                "resolved_version": resolved_version,
                "line": raw_line.strip(),
            }
        )

    return {
        coordinate: {
            "requested_versions": sorted({item["requested_version"] for item in occurrences}),
            "resolved_versions": sorted({item["resolved_version"] for item in occurrences}),
            "occurrences": occurrences,
        }
        for coordinate, occurrences in occurrences_by_coordinate.items()
    }


def load_reference_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"reference DB does not exist: {path}")
    versions_by_coordinate: dict[str, set[str]] = defaultdict(set)
    status_counts: Counter[str] = Counter()
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            "select coordinate, version, conversion_status from components"
        ).fetchall()
    for coordinate, version, status in rows:
        versions_by_coordinate[str(coordinate)].add(str(version))
        status_counts[str(status or "unknown")] += 1
    return {
        "component_count": len(rows),
        "pair_count": sum(len(versions) for versions in versions_by_coordinate.values()),
        "versions_by_coordinate": versions_by_coordinate,
        "status_counts": dict(sorted(status_counts.items())),
    }


def emitted_component_index(validation: dict[str, Any] | None) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not validation:
        return output
    for result in validation.get("results", []):
        if result.get("kind") != "sbom-component":
            continue
        coordinate = result.get("coordinate")
        if coordinate:
            output[str(coordinate)].append(result)
    return output


def emitted_status_for_version(source_version: str, emitted_versions: list[str]) -> str:
    if not emitted_versions:
        return "not-emitted"
    if source_version in emitted_versions:
        return "emitted-exact"
    return "emitted-coordinate-wrong-version"


def classify_gap(
    *,
    coordinate_in_reference_db: bool,
    exact_version_in_reference_db: bool,
    emitted_status: str,
) -> str:
    if not coordinate_in_reference_db:
        return "coordinate-absent-from-reference-db"
    if not exact_version_in_reference_db:
        return "version-absent-from-reference-db"
    if emitted_status == "not-emitted":
        return "source-present-not-emitted-despite-exact-reference"
    if emitted_status == "emitted-coordinate-wrong-version":
        return "source-present-wrong-version-despite-exact-reference"
    return "covered-and-emitted-exact"


def evidence_line_for_version(occurrences: list[dict[str, str]], source_version: str) -> str:
    for occurrence in occurrences:
        if occurrence["resolved_version"] == source_version:
            return occurrence["line"]
    return occurrences[0]["line"] if occurrences else ""


def top_coordinate_gaps(
    rows: list[dict[str, Any]],
    gap_class: str | set[str],
    *,
    limit: int = 25,
) -> list[dict[str, Any]]:
    classes = {gap_class} if isinstance(gap_class, str) else gap_class
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["gap_class"] in classes:
            grouped[row["coordinate"]].append(row)

    output = []
    for coordinate, coord_rows in grouped.items():
        output.append(
            {
                "coordinate": coordinate,
                "rows": len(coord_rows),
                "cases": len({row["case_id"] for row in coord_rows}),
                "source_versions": [
                    {"version": version, "rows": count}
                    for version, count in Counter(
                        row["source_version"] for row in coord_rows
                    ).most_common(8)
                ],
                "gap_classes": dict(
                    sorted(Counter(row["gap_class"] for row in coord_rows).items())
                ),
                "sample_cases": sorted({str(row["case_id"]) for row in coord_rows})[:8],
            }
        )
    return sorted(output, key=lambda item: (-item["rows"], item["coordinate"]))[:limit]


def methodology() -> list[str]:
    return [
        (
            "Report emitted-component version confirmation separately from full "
            "source dependency recall."
        ),
        (
            "Use the resolved Gradle runtime dependency tree as the denominator "
            "for source dependency coverage."
        ),
        (
            "Measure reference DB coverage twice: coordinate present, and exact "
            "source coordinate+version present."
        ),
        (
            "Grow a broad evaluation-only DB for source-observed TPLs first; "
            "shared calibrated DB promotion remains separate."
        ),
        (
            "After coverage is visible, optimize version selection and confidence "
            "without hiding missing TPLs or missing versions."
        ),
    ]


def verdict(summary: dict[str, Any]) -> str:
    if summary["source_dependency_pairs"] == 0:
        return "reference-db-coverage-dashboard-empty"
    return "reference-db-coverage-first-required"


def write_cases_csv(path: Path, cases: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "name",
        "role",
        "metric_bucket",
        "counted_in_emitted_accuracy",
        "source_dependency_pairs",
        "source_coordinates",
        "reference_coordinate_covered_pairs",
        "reference_exact_version_covered_pairs",
        "reference_coordinate_coverage_percent",
        "reference_exact_version_coverage_percent",
        "source_dependencies_emitted_exact",
        "source_dependencies_emitted_wrong_version",
        "source_dependencies_not_emitted",
        "end_to_end_exact_source_recall_percent",
        "dependency_tree_path",
        "report_path",
        "validation_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            writer.writerow({field: case.get(field, "") for field in fieldnames})


def write_gaps_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "case_name",
        "case_role",
        "coordinate",
        "source_version",
        "source_requested_versions",
        "gap_class",
        "coordinate_in_reference_db",
        "exact_version_in_reference_db",
        "reference_versions",
        "emitted_status",
        "emitted_versions",
        "evidence_line",
        "dependency_tree_path",
        "report_path",
        "validation_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    field: csv_value(row.get(field, ""))
                    for field in fieldnames
                }
            )


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Reference DB Coverage-First Dashboard",
        "",
        "Generated by `scripts/build_reference_db_coverage_dashboard.py`.",
        "",
        "This dashboard exists to prevent a misleading accuracy story. The old emitted-component metric remains useful, but it only asks whether emitted Maven components are correct. This artifact asks the harder question: out of the resolved source runtime dependencies, what is covered by the reference DB and what did the tool actually emit?",
        "",
        "## Verdict",
        "",
        f"`{payload['verdict']}`",
        "",
        "Do not optimize wrong-version rows as the next main lane until the reference DB coverage denominator is visible. The honest order is: source dependency denominator, broad evaluation-only DB coverage for source-observed TPLs and versions, then version-selection optimization.",
        "",
        "## Current Coverage Truth",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Source-tree cases inspected | {summary['source_tree_cases']} |",
        f"| Source dependency coordinate+version rows | {summary['source_dependency_pairs']} |",
        f"| Unique source coordinates | {summary['unique_source_coordinates']} |",
        f"| Unique source coordinate+version pairs | {summary['unique_source_coordinate_version_pairs']} |",
        f"| Current shared reference DB components | {summary['reference_db_components']} |",
        f"| Current shared reference DB coordinates | {summary['reference_db_coordinates']} |",
        f"| Source rows with coordinate in DB | {summary['reference_coordinate_covered_source_pairs']} ({format_percent(summary['reference_coordinate_coverage_percent'])}) |",
        f"| Source rows with exact version in DB | {summary['reference_exact_version_covered_source_pairs']} ({format_percent(summary['reference_exact_version_coverage_percent'])}) |",
        f"| Source rows emitted with exact version | {summary['source_dependencies_emitted_exact']} ({format_percent(summary['end_to_end_exact_source_recall_percent'])}) |",
        f"| Source rows emitted with wrong version | {summary['source_dependencies_emitted_wrong_version']} |",
        f"| Source rows not emitted | {summary['source_dependencies_not_emitted']} |",
        "",
        "## Why This Changes The Method",
        "",
        "| Metric | Meaning | Use it for |",
        "|---|---|---|",
        "| Emitted-component confirmation | Of the Maven components the tool emitted, how many match source? | Precision/version-quality of emitted SBOM rows. |",
        "| Reference DB coverage | Of the source runtime dependencies, how many coordinates and exact versions exist in the DB? | Whether the reference database is large enough to be a fair search space. |",
        "| End-to-end exact source recall | Of the source runtime dependencies, how many were emitted with the exact source version? | Honest full-pipeline recall after coverage is considered. |",
        "",
        "Current emitted-component metric from the existing dashboard:",
        "",
        "| Checked emitted rows | Confirmed | Wrong version | Missing from source | Confirmation rate |",
        "|---:|---:|---:|---:|---:|",
        (
            f"| {summary['emitted_component_accuracy_denominator']['checked']} | "
            f"{summary['emitted_component_accuracy_denominator']['confirmed']} | "
            f"{summary['emitted_component_accuracy_denominator']['version_mismatches']} | "
            f"{summary['emitted_component_accuracy_denominator']['missing_from_source_tree']} | "
            f"{format_percent(summary['emitted_component_accuracy_denominator']['confirmation_rate_percent'])} |"
        ),
        "",
        "That row must be described as emitted Maven version confirmation, not full dependency recall.",
        "",
        "## Gap Classes",
        "",
        "| Gap class | Rows | Meaning |",
        "|---|---:|---|",
    ]
    gap_explanations = {
        "coordinate-absent-from-reference-db": "The source TPL coordinate is not in the shared DB at all.",
        "version-absent-from-reference-db": "The coordinate exists, but the source-resolved version is absent.",
        "source-present-not-emitted-despite-exact-reference": "The exact source version exists in the DB, but the tool did not emit that coordinate.",
        "source-present-wrong-version-despite-exact-reference": "The exact source version exists in the DB, but the tool selected another version.",
    }
    for gap_class, count in summary["gap_class_counts"].items():
        lines.append(
            f"| `{gap_class}` | {count} | {gap_explanations.get(gap_class, '')} |"
        )

    lines.extend(
        [
            "",
            "## Coverage-First Method",
            "",
        ]
    )
    for index, step in enumerate(payload["methodology"], start=1):
        lines.append(f"{index}. {step}")
    lines.extend(
        [
            "",
            "The feasible interpretation of \"add every version\" is not all of Maven Central. It is every published version for every TPL coordinate that appears in the source-validated runtime dependency trees, with bytecode-bearing Android/JVM artifacts built into an evaluation-only DB first.",
            "",
            "## Top Coordinates Missing Entirely From The Reference DB",
            "",
        ]
    )
    lines.extend(top_gap_table(payload["top_reference_coordinate_gaps"]))
    lines.extend(
        [
            "",
            "## Top Source Versions Missing From Existing Coordinates",
            "",
        ]
    )
    lines.extend(top_gap_table(payload["top_reference_version_gaps"]))
    lines.extend(
        [
            "",
            "## Top Detection Gaps Despite Exact DB Coverage",
            "",
        ]
    )
    lines.extend(top_gap_table(payload["top_detection_gaps_despite_db"]))
    lines.extend(
        [
            "",
            "## Dashboard Files",
            "",
            "| File | Purpose |",
            "|---|---|",
            "| `data/results/evaluation/reference-db-coverage-first-dashboard.json` | Full payload with per-case rows, gap rows, and source-observed catalog. |",
            "| `data/results/evaluation/reference-db-coverage-first-cases.csv` | One row per source-tree case for dashboard cards. |",
            "| `data/results/evaluation/reference-db-coverage-first-gaps.csv` | One row per source dependency that is not fully covered and exactly emitted. |",
            "",
            "## Next Evaluation Lane",
            "",
            "1. Build a source-observed reference catalog from this dashboard.",
            "2. Fetch Maven/Google metadata for each source-observed coordinate.",
            "3. Build every bytecode-bearing published version into a broad evaluation-only DB, recording metadata-only/no-bytecode skips honestly.",
            "4. Rerun the source-dependency coverage dashboard and real-APK emitted/source validation against that broad DB.",
            "5. Only then optimize exact-version selection, confidence, ambiguity, and CVE claim policy.",
            "",
        ]
    )
    return "\n".join(lines)


def top_gap_table(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No rows.", ""]
    lines = [
        "| Coordinate | Rows | Cases | Source versions | Sample cases |",
        "|---|---:|---:|---|---|",
    ]
    for row in rows:
        versions = ", ".join(
            f"{item['version']} ({item['rows']})" for item in row["source_versions"]
        )
        cases = ", ".join(row["sample_cases"])
        lines.append(
            f"| `{escape_cell(row['coordinate'])}` | {row['rows']} | {row['cases']} | "
            f"{escape_cell(versions)} | {escape_cell(cases)} |"
        )
    return lines


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_exists(path_value: str | None) -> dict[str, Any] | None:
    if not path_value:
        return None
    path = Path(path_value)
    if not path.exists():
        return None
    return read_json(path)


def skipped_case(case: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "case_id": case.get("case_id"),
        "name": case.get("name"),
        "role": case.get("role"),
        "reason": reason,
    }


def normalize_path(value: str | Path | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\\", "/")


def percent(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round((numerator / denominator) * 100, 1)


def format_percent(value: Any) -> str:
    if value is None or value == "":
        return "n/a"
    return f"{float(value):.1f}%"


def csv_value(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    if isinstance(value, set):
        return "; ".join(str(item) for item in sorted(value))
    return str(value)


def escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
