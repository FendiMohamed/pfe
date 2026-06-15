from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_reference_db_coverage_dashboard import build_payload as build_coverage_payload
from build_reference_db_coverage_dashboard import read_json as read_dashboard_json


DEFAULT_SOURCE_DASHBOARD_JSON = Path(
    "data/results/evaluation/real-apk-source-validation-dashboard.json"
)
DEFAULT_REFERENCE_DB = Path("data/reference_db/reference_features_demo_final_large_v2.sqlite")
DEFAULT_EMITTED_ROWS_CSV = Path(
    "data/results/evaluation/real-apk-demo-final-large-v2-source-version-rows.csv"
)
DEFAULT_GAP_TRIAGE_CSV = Path(
    "data/results/evaluation/demo-final-large-v2-source-gap-triage.csv"
)
DEFAULT_MATCHER_RECALL_CSV = Path(
    "data/results/evaluation/demo-final-matcher-recall-diagnostics.csv"
)
DEFAULT_VULNERABILITY_ROWS_CSV = Path(
    "data/results/evaluation/large-combined-real-apk-vulnerability-rows.csv"
)
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/demo-final-transparency-export.json")
DEFAULT_CASES_CSV = Path("data/results/evaluation/demo-final-transparency-cases.csv")
DEFAULT_SOURCE_ROWS_CSV = Path(
    "data/results/evaluation/demo-final-transparency-source-rows.csv"
)
DEFAULT_EMITTED_EXPORT_CSV = Path(
    "data/results/evaluation/demo-final-transparency-emitted-rows.csv"
)
DEFAULT_VULNERABILITY_EXPORT_CSV = Path(
    "data/results/evaluation/demo-final-transparency-vulnerability-rows.csv"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build JSON/CSV/Markdown transparency exports that connect dataset criteria, "
            "reference coverage, matcher output, missing rows, and vulnerability claim strength."
        )
    )
    parser.add_argument("--source-dashboard-json", default=str(DEFAULT_SOURCE_DASHBOARD_JSON))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--emitted-rows-csv", default=str(DEFAULT_EMITTED_ROWS_CSV))
    parser.add_argument("--gap-triage-csv", default=str(DEFAULT_GAP_TRIAGE_CSV))
    parser.add_argument("--matcher-recall-csv", default=str(DEFAULT_MATCHER_RECALL_CSV))
    parser.add_argument("--vulnerability-rows-csv", default=str(DEFAULT_VULNERABILITY_ROWS_CSV))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--cases-csv", default=str(DEFAULT_CASES_CSV))
    parser.add_argument("--source-rows-csv", default=str(DEFAULT_SOURCE_ROWS_CSV))
    parser.add_argument("--emitted-export-csv", default=str(DEFAULT_EMITTED_EXPORT_CSV))
    parser.add_argument("--vulnerability-export-csv", default=str(DEFAULT_VULNERABILITY_EXPORT_CSV))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_export(
        source_dashboard_json=Path(args.source_dashboard_json),
        reference_db=Path(args.reference_db),
        emitted_rows_csv=Path(args.emitted_rows_csv),
        gap_triage_csv=Path(args.gap_triage_csv),
        matcher_recall_csv=Path(args.matcher_recall_csv),
        vulnerability_rows_csv=Path(args.vulnerability_rows_csv),
    )

    write_json(Path(args.output_json), payload)
    write_csv(Path(args.cases_csv), payload["dataset_cases"])
    write_csv(Path(args.source_rows_csv), payload["source_dependency_rows"])
    write_csv(Path(args.emitted_export_csv), payload["emitted_result_rows"])
    write_csv(Path(args.vulnerability_export_csv), payload["vulnerability_claims"])
    Path(args.output_doc).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_doc).write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(Path(args.output_doc)),
                "json": normalize_path(Path(args.output_json)),
                "dataset_cases": len(payload["dataset_cases"]),
                "source_dependency_rows": len(payload["source_dependency_rows"]),
                "emitted_result_rows": len(payload["emitted_result_rows"]),
                "vulnerability_claims": len(payload["vulnerability_claims"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_export(
    *,
    source_dashboard_json: Path,
    reference_db: Path,
    emitted_rows_csv: Path,
    gap_triage_csv: Path,
    matcher_recall_csv: Path,
    vulnerability_rows_csv: Path,
) -> dict[str, Any]:
    source_dashboard = read_dashboard_json(source_dashboard_json)
    coverage = build_coverage_payload(
        source_dashboard,
        reference_db_path=reference_db,
        source_dashboard_path=source_dashboard_json,
    )
    source_cases_by_id = {case["case_id"]: case for case in source_dashboard.get("cases", [])}
    dataset_cases = build_dataset_cases(source_dashboard.get("cases", []))
    gap_triage = {
        row_key(row): row for row in read_csv_if_exists(gap_triage_csv)
    }
    matcher_recall = {
        row_key(row): row for row in read_csv_if_exists(matcher_recall_csv)
    }
    source_rows = build_source_rows(
        coverage,
        gap_triage=gap_triage,
        matcher_recall=matcher_recall,
    )
    emitted_rows = build_emitted_rows(
        read_csv_if_exists(emitted_rows_csv),
        cases_by_id=source_cases_by_id,
    )
    vulnerability_claims = build_vulnerability_claims(
        read_csv_if_exists(vulnerability_rows_csv),
        emitted_rows=emitted_rows,
    )
    summary = build_summary(dataset_cases, source_rows, emitted_rows, vulnerability_claims, coverage)
    return {
        "schema_version": 1,
        "sources": {
            "source_dashboard_json": normalize_path(source_dashboard_json),
            "reference_db": normalize_path(reference_db),
            "emitted_rows_csv": normalize_path(emitted_rows_csv),
            "gap_triage_csv": normalize_path(gap_triage_csv),
            "matcher_recall_csv": normalize_path(matcher_recall_csv),
            "vulnerability_rows_csv": normalize_path(vulnerability_rows_csv),
            "emitted_rows_note": (
                "Emitted rows are from the existing final source-version constrained run. "
                "Reference coverage is recomputed against the selected reference DB."
            ),
        },
        "methodology": methodology(),
        "summary": summary,
        "dataset_cases": dataset_cases,
        "source_dependency_rows": source_rows,
        "emitted_result_rows": emitted_rows,
        "vulnerability_claims": vulnerability_claims,
    }


def build_dataset_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for case in cases:
        apk = case.get("apk_metadata") or {}
        classification = case.get("classification") or {}
        paths = case.get("paths") or {}
        validation = case.get("validation_stats") or {}
        tags = case.get("tags") or []
        output.append(
            {
                "case_id": case.get("case_id", ""),
                "name": case.get("name", ""),
                "role": case.get("role", ""),
                "metric_bucket": case.get("metric_bucket", ""),
                "counted_source_validated": bool(
                    case.get("counted_in_100_source_validated_real_apks")
                ),
                "dataset_classification": case.get("source_validation_gate", ""),
                "apk_family": family_from_tags(tags, classification),
                "feature_labels": ";".join(classification.get("feature_labels") or []),
                "framework_profile": classification.get("framework_profile", ""),
                "native_profile": classification.get("native_profile", ""),
                "r8_obfuscation_profile": classification.get("r8_obfuscation_profile", ""),
                "dex_profile": classification.get("dex_profile", ""),
                "release_profile": classification.get("release_profile", ""),
                "dependency_profile": dependency_profile(classification, tags),
                "vulnerability_profile": vulnerability_profile(case),
                "package_name": apk.get("package_name", ""),
                "version_name": apk.get("version_name", ""),
                "version_code": apk.get("version_code", ""),
                "dex_count": apk.get("dex_count", 0),
                "native_so_files": apk.get("native_so_files", 0),
                "maven_components": apk.get("maven_components", 0),
                "extraction_risk": apk.get("extraction_risk", ""),
                "obfuscation_risk": apk.get("obfuscation_risk", ""),
                "target_sdk": apk.get("target_sdk", ""),
                "dependency_tree_path": validation.get("dependency_tree_path", ""),
                "report_path": paths.get("report", ""),
                "source_validation_path": paths.get("validation", ""),
                "proof_path": paths.get("proof", ""),
            }
        )
    return sorted(output, key=lambda row: row["case_id"])


def build_source_rows(
    coverage: dict[str, Any],
    *,
    gap_triage: dict[tuple[str, str, str], dict[str, str]],
    matcher_recall: dict[tuple[str, str, str], dict[str, str]],
) -> list[dict[str, Any]]:
    output = []
    for case in coverage.get("cases", []):
        for row in case.get("source_rows", []):
            key = (
                str(case.get("case_id", "")),
                str(row.get("coordinate", "")),
                str(row.get("source_version", "")),
            )
            triage = gap_triage.get(key, {})
            recall = matcher_recall.get(key, {})
            classification = source_coverage_class(row, triage)
            output.append(
                {
                    "case_id": case.get("case_id", ""),
                    "app": case.get("name", ""),
                    "role": case.get("role", ""),
                    "coordinate": row.get("coordinate", ""),
                    "source_version": row.get("source_version", ""),
                    "coverage_class": classification,
                    "coordinate_in_reference_db": bool(row.get("coordinate_in_reference_db")),
                    "exact_version_in_reference_db": bool(row.get("exact_version_in_reference_db")),
                    "emitted_status": row.get("emitted_status", ""),
                    "gap_class": row.get("gap_class", ""),
                    "triage_bucket": triage.get("triage_bucket", ""),
                    "next_action": triage.get("next_action", ""),
                    "reason_label": source_reason_label(classification, row, triage, recall),
                    "target_alias": triage.get("target_alias", ""),
                    "emitted_alias": triage.get("emitted_alias", ""),
                    "matcher_recall_status": recall.get("recall_status", ""),
                    "matcher_next_action": recall.get("next_action", ""),
                    "matcher_best_version": recall.get("best_version", ""),
                    "matcher_source_score": recall.get("source_score", ""),
                    "matcher_best_score": recall.get("best_score", ""),
                }
            )
    return output


def build_emitted_rows(
    rows: list[dict[str, str]],
    *,
    cases_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        case = cases_by_id.get(row.get("case_id", ""), {})
        status = row.get("status", "")
        source_versions = split_semicolon(row.get("source_versions", ""))
        detected_version = row.get("detected_version", "")
        result_class = emitted_result_class(status, detected_version, source_versions)
        output.append(
            {
                "case_id": row.get("case_id", ""),
                "app": row.get("app", ""),
                "role": case.get("role", ""),
                "coordinate": row.get("coordinate", ""),
                "detected_version": detected_version,
                "source_versions": ";".join(source_versions),
                "result_class": result_class,
                "version_mismatch_reason": version_mismatch_reason(
                    detected_version, source_versions, result_class
                ),
                "confidence": row.get("confidence", ""),
                "match_type": row.get("match_type", ""),
                "purl": row.get("purl", ""),
                "evidence_line": row.get("evidence_line", ""),
            }
        )
    return output


def build_vulnerability_claims(
    rows: list[dict[str, str]],
    *,
    emitted_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    emitted_index = {
        (row["case_id"], row["coordinate"], row["detected_version"]): row
        for row in emitted_rows
    }
    output = []
    for row in rows:
        coordinate = row.get("coordinate", "")
        version = row.get("version", "")
        status = row.get("osv_status", "")
        emitted = emitted_index.get((row.get("case_id", ""), coordinate, version), {})
        claim_strength = vulnerability_claim_strength(row, emitted)
        output.append(
            {
                "case_id": row.get("case_id", ""),
                "case_name": row.get("case_name", ""),
                "case_role": row.get("case_role", ""),
                "coordinate": coordinate,
                "version": version,
                "purl": row.get("purl", ""),
                "osv_status": status,
                "vulnerability_id": row.get("vulnerability_id", ""),
                "severity": row.get("severity", ""),
                "finding_confidence": row.get("finding_confidence", ""),
                "finding_reason": row.get("finding_reason", ""),
                "claim_strength": claim_strength,
                "emitted_result_class": emitted.get("result_class", ""),
            }
        )
    return output


def source_coverage_class(row: dict[str, Any], triage: dict[str, str]) -> str:
    bucket = triage.get("triage_bucket", "")
    if bucket == "metadata-or-source-only-boundary":
        return "metadata-only"
    if bucket in {"common-source-or-platform-boundary", "project-module-boundary"}:
        return "source-boundary"
    if bucket in {"target-artifact-alias-boundary", "already-covered-by-emitted-sibling"}:
        return "artifact-family-alias"
    if bucket == "relocated-coordinate-boundary":
        return "source-boundary"
    if bucket == "missing-reference-candidate":
        return "missing-coordinate-or-version"
    if bucket == "matcher-recall-candidate":
        return "matcher-recall-gap"
    if not row.get("coordinate_in_reference_db"):
        return "missing-coordinate"
    if not row.get("exact_version_in_reference_db"):
        return "coordinate-only-in-db"
    if row.get("gap_class") == "covered-and-emitted-exact":
        return "exact-version-in-db-and-emitted"
    return "exact-version-in-db"


def source_reason_label(
    classification: str,
    row: dict[str, Any],
    triage: dict[str, str],
    recall: dict[str, str],
) -> str:
    if classification == "metadata-only":
        return "metadata/source-only"
    if classification == "source-boundary":
        return triage.get("triage_bucket", "source-boundary")
    if classification == "artifact-family-alias":
        return "artifact-family-alias"
    if classification == "matcher-recall-gap":
        return recall.get("recall_status") or "matcher-recall"
    if classification == "missing-coordinate-or-version":
        return "reference-missing"
    if classification == "coordinate-only-in-db":
        return "source-version-absent-from-db"
    if classification == "missing-coordinate":
        return "coordinate-absent-from-db"
    if row.get("gap_class") == "covered-and-emitted-exact":
        return "exact-confirmed"
    return str(row.get("gap_class") or classification)


def emitted_result_class(status: str, detected_version: str, source_versions: list[str]) -> str:
    if status == "confirmed":
        return "exact-confirmed"
    if status == "missing":
        return "false-positive-extra"
    if status == "mismatch":
        return "wrong-version"
    if source_versions and detected_version in source_versions:
        return "exact-confirmed"
    if source_versions:
        return "wrong-version"
    return "unknown-or-report-only"


def version_mismatch_reason(
    detected_version: str,
    source_versions: list[str],
    result_class: str,
) -> str:
    if result_class == "exact-confirmed":
        return "not-a-mismatch"
    if result_class == "false-positive-extra":
        return "not-in-source-tree"
    if result_class != "wrong-version" or not source_versions:
        return "unknown"
    source_version = source_versions[0]
    comparison = compare_versions(detected_version, source_version)
    if comparison < 0:
        return "older-version-selected"
    if comparison > 0:
        return "newer-version-selected"
    return "different-version-label"


def vulnerability_claim_strength(row: dict[str, str], emitted: dict[str, Any]) -> str:
    if not row.get("coordinate") and row.get("osv_status") == "not-queried":
        return "not-queried"
    reason = row.get("finding_reason", "").lower()
    confidence = row.get("finding_confidence", "").lower()
    emitted_class = str(emitted.get("result_class", ""))
    if "source-confirmed" in reason or confidence == "source-confirmed":
        return "source-confirmed"
    if emitted_class == "wrong-version" or "mismatch" in reason:
        return "source-version-mismatch"
    if emitted_class in {"unknown-or-report-only", ""}:
        return "report-only"
    return "potential"


def build_summary(
    dataset_cases: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    emitted_rows: list[dict[str, Any]],
    vulnerability_claims: list[dict[str, Any]],
    coverage: dict[str, Any],
) -> dict[str, Any]:
    return {
        "dataset_cases": len(dataset_cases),
        "dataset_roles": dict(sorted(Counter(row["role"] for row in dataset_cases).items())),
        "metric_buckets": dict(
            sorted(Counter(row["metric_bucket"] for row in dataset_cases).items())
        ),
        "source_dependency_rows": len(source_rows),
        "source_coverage_classes": dict(
            sorted(Counter(row["coverage_class"] for row in source_rows).items())
        ),
        "source_reason_labels": dict(
            sorted(Counter(row["reason_label"] for row in source_rows).items())
        ),
        "emitted_result_rows": len(emitted_rows),
        "emitted_result_classes": dict(
            sorted(Counter(row["result_class"] for row in emitted_rows).items())
        ),
        "version_mismatch_reasons": dict(
            sorted(Counter(row["version_mismatch_reason"] for row in emitted_rows).items())
        ),
        "vulnerability_claim_rows": len(vulnerability_claims),
        "vulnerability_claim_strength": dict(
            sorted(Counter(row["claim_strength"] for row in vulnerability_claims).items())
        ),
        "reference_coverage": coverage.get("summary", {}),
    }


def methodology() -> list[str]:
    return [
        "Dataset cases come from the real-APK source-validation dashboard.",
        "Reference coverage is recomputed from saved Gradle runtime dependency trees against the selected reference DB.",
        "Source dependency rows are classified before matcher claims, separating exact DB coverage, missing references, aliases, source-only boundaries, and matcher recall gaps.",
        "Emitted rows are classified from the existing final source-version constrained evaluation output.",
        "Vulnerability rows are downgraded when the emitted version is not source-confirmed.",
    ]


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Demo Final Transparency Report",
        "",
        "Generated by `scripts/build_demo_final_transparency_export.py`.",
        "",
        "## Purpose",
        "",
        "This export connects dataset selection, source dependency coverage, matcher results, missing-row reasons, and vulnerability claim strength. It is designed for thesis tables, dashboards, and defense slides.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Dataset cases | {summary['dataset_cases']} |",
        f"| Source dependency rows | {summary['source_dependency_rows']} |",
        f"| Emitted result rows | {summary['emitted_result_rows']} |",
        f"| Vulnerability claim rows | {summary['vulnerability_claim_rows']} |",
        "",
        "## Dataset Roles",
        "",
        *counter_table(summary["dataset_roles"]),
        "",
        "## Source Coverage Classes",
        "",
        *counter_table(summary["source_coverage_classes"]),
        "",
        "## Emitted Result Classes",
        "",
        *counter_table(summary["emitted_result_classes"]),
        "",
        "## Version Mismatch Reasons",
        "",
        *counter_table(summary["version_mismatch_reasons"]),
        "",
        "## Vulnerability Claim Strength",
        "",
        *counter_table(summary["vulnerability_claim_strength"]),
        "",
        "## Exported Files",
        "",
        "- `data/results/evaluation/demo-final-transparency-export.json`",
        "- `data/results/evaluation/demo-final-transparency-cases.csv`",
        "- `data/results/evaluation/demo-final-transparency-source-rows.csv`",
        "- `data/results/evaluation/demo-final-transparency-emitted-rows.csv`",
        "- `data/results/evaluation/demo-final-transparency-vulnerability-rows.csv`",
        "",
        "## Interpretation",
        "",
        "The report should not be reduced to one accuracy score. It records whether each row is a dataset boundary, reference DB coverage issue, matcher recall issue, version-selection mismatch, or vulnerability-claim confidence issue.",
        "",
    ]
    return "\n".join(lines)


def counter_table(counter: dict[str, int]) -> list[str]:
    lines = ["| Class | Rows |", "|---|---:|"]
    for key, value in counter.items():
        lines.append(f"| `{escape_md(str(key))}` | {value} |")
    return lines


def family_from_tags(tags: list[str], classification: dict[str, Any]) -> str:
    if tags:
        return ";".join(str(tag) for tag in tags)
    return classification.get("framework_profile", "")


def dependency_profile(classification: dict[str, Any], tags: list[str]) -> str:
    labels = " ".join(classification.get("feature_labels") or []) + " " + " ".join(tags)
    lowered = labels.lower()
    profiles = []
    for needle, label in [
        ("androidx", "AndroidX-heavy"),
        ("kotlin", "Kotlin-heavy"),
        ("compose", "Compose/KMP"),
        ("native", "native-heavy"),
        ("old", "older-dependency"),
        ("jcenter", "older-dependency"),
        ("react", "framework-heavy"),
    ]:
        if needle in lowered:
            profiles.append(label)
    return ";".join(sorted(set(profiles))) or "standard"


def vulnerability_profile(case: dict[str, Any]) -> str:
    description = " ".join(str(value) for value in (case.get("description") or {}).values())
    if "vulnerab" in description.lower():
        return "vulnerable-expected-or-relevant"
    return "unknown-or-clean-control"


def row_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        row.get("case_id", ""),
        row.get("coordinate", ""),
        row.get("source_version") or first_value(row.get("source_versions", "")),
    )


def split_semicolon(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def first_value(value: str) -> str:
    return split_semicolon(value)[0] if split_semicolon(value) else ""


def compare_versions(left: str, right: str) -> int:
    left_key = version_key(left)
    right_key = version_key(right)
    if left_key < right_key:
        return -1
    if left_key > right_key:
        return 1
    return 0


def version_key(value: str) -> tuple[Any, ...]:
    parts: list[Any] = []
    token = ""
    for char in value:
        if char.isdigit():
            if token and not token[-1].isdigit():
                parts.append(token)
                token = ""
            token += char
        else:
            if token and token[-1].isdigit():
                parts.append(int(token))
                token = ""
            token += char
    if token:
        parts.append(int(token) if token.isdigit() else token)
    return tuple(parts)


def read_csv_if_exists(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_path(path: Path) -> str:
    return path.as_posix()


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
