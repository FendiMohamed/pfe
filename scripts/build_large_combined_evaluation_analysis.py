from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_DASHBOARD_JSON = Path(
    "data/results/evaluation/real-apk-source-validation-dashboard.json"
)
DEFAULT_COVERAGE_JSON = Path(
    "data/results/evaluation/reference-db-coverage-large-combined-dashboard.json"
)
DEFAULT_COMBINED_DB_BUILD_JSON = Path(
    "data/results/evaluation/large-combined-reference-db-build.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/large-combined-real-apk-analysis.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/LARGE_COMBINED_REAL_APK_ANALYSIS.md")
DEFAULT_PER_APK_CSV = Path("data/results/evaluation/large-combined-real-apk-per-apk.csv")
DEFAULT_VERSION_ROWS_CSV = Path("data/results/evaluation/large-combined-real-apk-version-rows.csv")
DEFAULT_SOURCE_GAPS_CSV = Path("data/results/evaluation/large-combined-real-apk-source-gaps.csv")
DEFAULT_VULNERABILITY_ROWS_CSV = Path(
    "data/results/evaluation/large-combined-real-apk-vulnerability-rows.csv"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build detailed analysis artifacts for the large combined reference DB using "
            "the current source-validation dashboard and combined coverage dashboard."
        )
    )
    parser.add_argument("--source-dashboard-json", default=str(DEFAULT_SOURCE_DASHBOARD_JSON))
    parser.add_argument("--coverage-json", default=str(DEFAULT_COVERAGE_JSON))
    parser.add_argument("--combined-db-build-json", default=str(DEFAULT_COMBINED_DB_BUILD_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--per-apk-csv", default=str(DEFAULT_PER_APK_CSV))
    parser.add_argument("--version-rows-csv", default=str(DEFAULT_VERSION_ROWS_CSV))
    parser.add_argument("--source-gaps-csv", default=str(DEFAULT_SOURCE_GAPS_CSV))
    parser.add_argument("--vulnerability-rows-csv", default=str(DEFAULT_VULNERABILITY_ROWS_CSV))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_dashboard_path = Path(args.source_dashboard_json)
    coverage_path = Path(args.coverage_json)
    db_build_path = Path(args.combined_db_build_json)
    payload = build_payload(
        source_dashboard=read_json(source_dashboard_path),
        coverage=read_json(coverage_path),
        db_build=read_json_if_exists(db_build_path),
        source_dashboard_path=source_dashboard_path,
        coverage_path=coverage_path,
        db_build_path=db_build_path,
    )

    write_json(Path(args.output_json), payload)
    Path(args.output_doc).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_doc).write_text(build_markdown(payload), encoding="utf-8")
    write_csv(Path(args.per_apk_csv), payload["per_apk_rows"])
    write_csv(Path(args.version_rows_csv), payload["version_rows"])
    write_csv(Path(args.source_gaps_csv), payload["source_gap_rows"])
    write_csv(Path(args.vulnerability_rows_csv), payload["vulnerability_rows"])

    print(
        json.dumps(
            {
                "doc": normalize_path(Path(args.output_doc)),
                "json": normalize_path(Path(args.output_json)),
                "per_apk_csv": normalize_path(Path(args.per_apk_csv)),
                "version_rows_csv": normalize_path(Path(args.version_rows_csv)),
                "source_gaps_csv": normalize_path(Path(args.source_gaps_csv)),
                "vulnerability_rows_csv": normalize_path(Path(args.vulnerability_rows_csv)),
                "counted_cases": payload["summary"]["counted_source_validated_real_apks"],
                "version_rows": len(payload["version_rows"]),
                "source_gap_rows": len(payload["source_gap_rows"]),
                "vulnerability_rows": len(payload["vulnerability_rows"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    *,
    source_dashboard: dict[str, Any],
    coverage: dict[str, Any],
    db_build: dict[str, Any] | None,
    source_dashboard_path: Path,
    coverage_path: Path,
    db_build_path: Path,
) -> dict[str, Any]:
    coverage_cases = {case["case_id"]: case for case in coverage.get("cases", [])}
    counted_cases = [
        case
        for case in source_dashboard.get("cases", [])
        if case.get("counted_in_100_source_validated_real_apks")
    ]
    per_apk_rows = [build_per_apk_row(case, coverage_cases.get(case["case_id"])) for case in counted_cases]
    version_rows = []
    vulnerability_rows = []
    for case in counted_cases:
        validation = read_json_if_exists((case.get("paths") or {}).get("validation"))
        report = read_json_if_exists((case.get("paths") or {}).get("report"))
        if validation:
            version_rows.extend(build_version_rows(case, validation))
        if report:
            vulnerability_rows.extend(build_vulnerability_rows(case, report))

    source_gap_rows = [
        build_source_gap_row(row)
        for row in coverage.get("gap_rows", [])
        if row.get("case_role") in {"clean-source-validated", "source-validated-partial"}
    ]
    summary = build_summary(source_dashboard, coverage, db_build, per_apk_rows, version_rows, source_gap_rows)
    return {
        "schema_version": 1,
        "sources": {
            "source_dashboard": normalize_path(source_dashboard_path),
            "coverage_dashboard": normalize_path(coverage_path),
            "combined_db_build": normalize_path(db_build_path) if db_build else "",
        },
        "summary": summary,
        "direct_large_db_rerun_status": {
            "status": "blocked-by-runtime",
            "evidence": (
                "A one-case direct report/source-validation rerun against "
                "reference_features_large_combined.sqlite timed out after 30 minutes. "
                "A 1000-component package-overlap cap also timed out after 30 minutes. "
                "A 100-component cap finished in about 5 minutes but regressed F-Droid to "
                "6 confirmed / 1 wrong / 6 missing, and a 300-component cap finished in about "
                "14 minutes but still regressed F-Droid to 6 confirmed / 6 wrong / 6 missing. "
                "A coordinate-preserving top-5-per-coordinate cap finished in about 26 minutes "
                "but emitted 35 confirmed / 64 wrong / 19 missing-source rows. A stricter "
                "minimum-overlap 5, top-3-per-coordinate cap finished in about 7 minutes but "
                "still regressed F-Droid to 10 confirmed / 17 wrong / 9 missing; raising "
                "min-score to 0.75 still produced only 7 confirmed / 4 wrong / 6 missing. "
                "Therefore the detailed analysis below uses the current source-validation baseline "
                "plus large-combined reference coverage until a stricter large-DB matcher shortlist is added."
            ),
        },
        "per_apk_rows": per_apk_rows,
        "version_rows": version_rows,
        "source_gap_rows": source_gap_rows,
        "vulnerability_rows": vulnerability_rows,
        "top_wrong_versions": top_rows(version_rows, "wrong-version"),
        "top_false_positive_coordinates": top_rows(version_rows, "false-positive-extra-emission"),
        "top_false_negative_coordinates": top_gap_rows(source_gap_rows, "source-present-not-emitted-despite-exact-reference"),
        "top_reference_missing_coordinates": top_gap_rows(
            source_gap_rows,
            {"coordinate-absent-from-reference-db", "version-absent-from-reference-db"},
        ),
    }


def build_per_apk_row(case: dict[str, Any], coverage_case: dict[str, Any] | None) -> dict[str, Any]:
    stats = case.get("validation_stats") or {}
    row = {
        "case_id": case.get("case_id", ""),
        "name": case.get("name", ""),
        "role": case.get("role", ""),
        "metric_bucket": case.get("metric_bucket", ""),
        "checked_emitted_components": stats.get("checked", 0),
        "confirmed_exact": stats.get("confirmed", 0),
        "wrong_version": stats.get("version_mismatches", 0),
        "false_positive_extra_emissions": stats.get("missing", 0),
        "confirmation_rate_percent": stats.get("confirmation_rate_percent", 0),
        "report_path": (case.get("paths") or {}).get("report", ""),
        "validation_path": (case.get("paths") or {}).get("validation", ""),
        "dependency_tree_path": stats.get("dependency_tree_path", ""),
    }
    if coverage_case:
        row.update(
            {
                "source_dependency_pairs": coverage_case.get("source_dependency_pairs", 0),
                "source_dependencies_emitted_exact": coverage_case.get("source_dependencies_emitted_exact", 0),
                "source_dependencies_emitted_wrong_version": coverage_case.get(
                    "source_dependencies_emitted_wrong_version",
                    0,
                ),
                "source_dependencies_not_emitted": coverage_case.get("source_dependencies_not_emitted", 0),
                "reference_coordinate_coverage_percent": coverage_case.get(
                    "reference_coordinate_coverage_percent",
                    0,
                ),
                "reference_exact_version_coverage_percent": coverage_case.get(
                    "reference_exact_version_coverage_percent",
                    0,
                ),
                "end_to_end_exact_source_recall_percent": coverage_case.get(
                    "end_to_end_exact_source_recall_percent",
                    0,
                ),
            }
        )
    return row


def build_version_rows(case: dict[str, Any], validation: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for result in validation.get("results", []):
        if result.get("kind") != "sbom-component":
            continue
        status = result.get("status", "")
        if status == "confirmed":
            analysis_class = "true-positive-exact-version"
        elif status == "version-mismatch":
            analysis_class = "wrong-version"
        else:
            analysis_class = "false-positive-extra-emission"
        rows.append(
            {
                "case_id": case.get("case_id", ""),
                "case_name": case.get("name", ""),
                "case_role": case.get("role", ""),
                "analysis_class": analysis_class,
                "status": status,
                "coordinate": result.get("coordinate", ""),
                "tool_selected_version": result.get("version", ""),
                "correct_source_versions": ";".join(result.get("source_versions") or []),
                "source_requested_versions": ";".join(result.get("source_requested_versions") or []),
                "purl": result.get("purl", ""),
                "confidence": result.get("confidence", 0),
                "match_type": result.get("match_type", ""),
                "evidence_line": result.get("evidence_line", ""),
            }
        )
    return rows


def build_source_gap_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": row.get("case_id", ""),
        "case_name": row.get("case_name", ""),
        "case_role": row.get("case_role", ""),
        "gap_class": row.get("gap_class", ""),
        "coordinate": row.get("coordinate", ""),
        "source_version": row.get("source_version", ""),
        "emitted_status": row.get("emitted_status", ""),
        "emitted_versions": ";".join(row.get("emitted_versions") or []),
        "coordinate_in_reference_db": row.get("coordinate_in_reference_db", False),
        "exact_version_in_reference_db": row.get("exact_version_in_reference_db", False),
        "reference_versions": ";".join(row.get("reference_versions") or []),
        "source_requested_versions": ";".join(row.get("source_requested_versions") or []),
        "evidence_line": row.get("evidence_line", ""),
        "dependency_tree_path": row.get("dependency_tree_path", ""),
    }


def build_vulnerability_rows(case: dict[str, Any], report: dict[str, Any]) -> list[dict[str, Any]]:
    osv = report.get("osv")
    if not isinstance(osv, dict):
        return [
            {
                "case_id": case.get("case_id", ""),
                "case_name": case.get("name", ""),
                "case_role": case.get("role", ""),
                "osv_status": "not-queried",
                "coordinate": "",
                "version": "",
                "purl": "",
                "vulnerability_id": "",
                "severity": "",
                "finding_confidence": "",
                "finding_reason": "",
            }
        ]
    rows = []
    for result in osv.get("results", []):
        vulnerabilities = result.get("vulnerabilities") or []
        if not vulnerabilities:
            rows.append(
                vulnerability_row(case, result, vulnerability=None, osv_status="queried-no-finding")
            )
            continue
        for vulnerability in vulnerabilities:
            rows.append(vulnerability_row(case, result, vulnerability=vulnerability, osv_status="finding"))
    return rows


def vulnerability_row(
    case: dict[str, Any],
    result: dict[str, Any],
    *,
    vulnerability: dict[str, Any] | None,
    osv_status: str,
) -> dict[str, Any]:
    vulnerability = vulnerability or {}
    severity = vulnerability.get("database_specific", {}).get("severity") or vulnerability.get("severity") or ""
    return {
        "case_id": case.get("case_id", ""),
        "case_name": case.get("name", ""),
        "case_role": case.get("role", ""),
        "osv_status": osv_status,
        "coordinate": result.get("coordinate", ""),
        "version": result.get("version", ""),
        "purl": result.get("purl", ""),
        "vulnerability_id": vulnerability.get("id", ""),
        "severity": severity,
        "finding_confidence": result.get("finding_confidence", ""),
        "finding_reason": result.get("finding_reason", ""),
    }


def build_summary(
    source_dashboard: dict[str, Any],
    coverage: dict[str, Any],
    db_build: dict[str, Any] | None,
    per_apk_rows: list[dict[str, Any]],
    version_rows: list[dict[str, Any]],
    source_gap_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    version_counts = Counter(row["analysis_class"] for row in version_rows)
    gap_counts = Counter(row["gap_class"] for row in source_gap_rows)
    summary = source_dashboard.get("summary", {})
    coverage_summary = coverage.get("summary", {})
    return {
        "counted_source_validated_real_apks": summary.get("counted_source_validated_real_apks", 0),
        "clean_source_validated_real_apks": summary.get("clean_source_validated_real_apks", 0),
        "partial_source_validated_real_apks": summary.get("partial_source_validated_real_apks", 0),
        "baseline_emitted_checked": summary.get("emitted_version_stats_for_counted_apks", {}).get("checked", 0),
        "baseline_emitted_confirmed": summary.get("emitted_version_stats_for_counted_apks", {}).get("confirmed", 0),
        "baseline_emitted_wrong_version": summary.get("emitted_version_stats_for_counted_apks", {}).get(
            "version_mismatches",
            0,
        ),
        "baseline_false_positive_extra_emissions": summary.get("emitted_version_stats_for_counted_apks", {}).get(
            "missing_from_source_tree",
            0,
        ),
        "baseline_emitted_confirmation_rate_percent": summary.get(
            "emitted_version_stats_for_counted_apks",
            {},
        ).get("confirmation_rate_percent", 0),
        "large_combined_reference_components": coverage_summary.get("reference_db_components", 0),
        "large_combined_reference_coordinates": coverage_summary.get("reference_db_coordinates", 0),
        "large_combined_exact_source_version_coverage_percent": coverage_summary.get(
            "reference_exact_version_coverage_percent",
            0,
        ),
        "large_combined_coordinate_coverage_percent": coverage_summary.get(
            "reference_coordinate_coverage_percent",
            0,
        ),
        "source_dependency_pairs": coverage_summary.get("source_dependency_pairs", 0),
        "source_dependencies_emitted_exact": coverage_summary.get("source_dependencies_emitted_exact", 0),
        "source_dependencies_emitted_wrong_version": coverage_summary.get(
            "source_dependencies_emitted_wrong_version",
            0,
        ),
        "source_dependencies_not_emitted": coverage_summary.get("source_dependencies_not_emitted", 0),
        "end_to_end_exact_source_recall_percent": coverage_summary.get(
            "end_to_end_exact_source_recall_percent",
            0,
        ),
        "version_row_counts": dict(sorted(version_counts.items())),
        "source_gap_counts": dict(sorted(gap_counts.items())),
        "combined_db_build_after": (db_build or {}).get("after", {}),
        "combined_db_insert_sources": (db_build or {}).get("sources", []),
        "per_apk_rows": len(per_apk_rows),
        "version_rows": len(version_rows),
        "source_gap_rows": len(source_gap_rows),
    }


def top_rows(rows: list[dict[str, Any]], analysis_class: str, limit: int = 20) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        if row.get("analysis_class") == analysis_class:
            counts[(row.get("coordinate", ""), row.get("tool_selected_version", ""))] += 1
    return [
        {"coordinate": coordinate, "tool_selected_version": version, "rows": count}
        for (coordinate, version), count in counts.most_common(limit)
    ]


def top_gap_rows(
    rows: list[dict[str, Any]],
    gap_class: str | set[str],
    limit: int = 20,
) -> list[dict[str, Any]]:
    accepted = {gap_class} if isinstance(gap_class, str) else gap_class
    counts: Counter[tuple[str, str, str]] = Counter()
    for row in rows:
        if row.get("gap_class") in accepted:
            counts[(row.get("gap_class", ""), row.get("coordinate", ""), row.get("source_version", ""))] += 1
    return [
        {"gap_class": cls, "coordinate": coordinate, "source_version": version, "rows": count}
        for (cls, coordinate, version), count in counts.most_common(limit)
    ]


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Large Combined Real APK Analysis",
        "",
        "Generated by `scripts/build_large_combined_evaluation_analysis.py`.",
        "",
        "This report separates three things: current emitted-SBOM source validation, large-combined reference DB coverage, and direct large-DB rerun status. The direct rerun is not counted as complete because one case timed out after 30 minutes.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Counted source-validated real APKs | {summary['counted_source_validated_real_apks']} |",
        f"| Clean / partial APKs | {summary['clean_source_validated_real_apks']} / {summary['partial_source_validated_real_apks']} |",
        f"| Current emitted components checked | {summary['baseline_emitted_checked']} |",
        f"| Current emitted exact versions | {summary['baseline_emitted_confirmed']} |",
        f"| Current emitted wrong versions | {summary['baseline_emitted_wrong_version']} |",
        f"| Current false-positive extra emissions | {summary['baseline_false_positive_extra_emissions']} |",
        f"| Current emitted confirmation rate | {summary['baseline_emitted_confirmation_rate_percent']}% |",
        f"| Large combined DB components | {summary['large_combined_reference_components']} |",
        f"| Large combined DB coordinates | {summary['large_combined_reference_coordinates']} |",
        f"| Large combined exact source-version coverage | {summary['large_combined_exact_source_version_coverage_percent']}% |",
        f"| Large combined coordinate coverage | {summary['large_combined_coordinate_coverage_percent']}% |",
        f"| Source dependency rows | {summary['source_dependency_pairs']} |",
        f"| Source rows emitted exact / wrong / not emitted | {summary['source_dependencies_emitted_exact']} / {summary['source_dependencies_emitted_wrong_version']} / {summary['source_dependencies_not_emitted']} |",
        f"| End-to-end exact source recall | {summary['end_to_end_exact_source_recall_percent']}% |",
        "",
        "## Direct Large-DB Rerun Status",
        "",
        f"- Status: `{payload['direct_large_db_rerun_status']['status']}`",
        f"- Evidence: {payload['direct_large_db_rerun_status']['evidence']}",
        "",
        "## Output Files",
        "",
        "- `data/results/evaluation/large-combined-real-apk-per-apk.csv`",
        "- `data/results/evaluation/large-combined-real-apk-version-rows.csv`",
        "- `data/results/evaluation/large-combined-real-apk-source-gaps.csv`",
        "- `data/results/evaluation/large-combined-real-apk-vulnerability-rows.csv`",
        "",
        "## Top Wrong Versions",
        "",
        "| Coordinate | Tool version | Rows |",
        "|---|---|---:|",
    ]
    lines.extend(
        f"| `{row['coordinate']}` | `{row['tool_selected_version']}` | {row['rows']} |"
        for row in payload["top_wrong_versions"][:20]
    )
    lines.extend(
        [
            "",
            "## Top False Negatives Despite Exact Reference",
            "",
            "| Coordinate | Source version | Rows |",
            "|---|---|---:|",
        ]
    )
    lines.extend(
        f"| `{row['coordinate']}` | `{row['source_version']}` | {row['rows']} |"
        for row in payload["top_false_negative_coordinates"][:20]
    )
    lines.extend(
        [
            "",
            "## Top Remaining Reference Gaps",
            "",
            "| Gap class | Coordinate | Source version | Rows |",
            "|---|---|---|---:|",
        ]
    )
    lines.extend(
        f"| `{row['gap_class']}` | `{row['coordinate']}` | `{row['source_version']}` | {row['rows']} |"
        for row in payload["top_reference_missing_coordinates"][:20]
    )
    lines.append("")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_exists(path: str | Path) -> dict[str, Any] | None:
    if not path:
        return None
    candidate = Path(path)
    if not candidate.exists():
        return None
    return read_json(candidate)


def normalize_path(path: Path) -> str:
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
