from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

from apk_sbom.dex_analyzer import analyze_apk_dex
from apk_sbom.matcher import (
    build_version_decisions,
    feature_set_from_apk_analysis,
    identity_confidence_score,
    load_reference_components,
    reportable_version_decisions,
    score_reference_component,
)


DEFAULT_TRIAGE_CSV = Path("data/results/evaluation/demo-final-large-source-gap-triage.csv")
DEFAULT_DASHBOARD_JSON = Path(
    "data/results/evaluation/real-apk-demo-final-large-source-version-dashboard.json"
)
DEFAULT_REFERENCE_DB = Path("data/reference_db/reference_features_demo_final_large.sqlite")
DEFAULT_OUTPUT_JSON = Path(
    "data/results/evaluation/demo-final-matcher-recall-diagnostics.json"
)
DEFAULT_OUTPUT_CSV = Path(
    "data/results/evaluation/demo-final-matcher-recall-diagnostics.csv"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/DEMO_FINAL_MATCHER_RECALL_DIAGNOSTICS.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Score exact source-version matcher-recall gaps against the final demo "
            "large DB and classify report-only recall opportunities."
        )
    )
    parser.add_argument("--triage-csv", default=str(DEFAULT_TRIAGE_CSV))
    parser.add_argument("--dashboard-json", default=str(DEFAULT_DASHBOARD_JSON))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--limit-cases", type=int)
    parser.add_argument("--case-id")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    triage_rows = [
        row
        for row in read_csv(Path(args.triage_csv))
        if row.get("triage_bucket") == "matcher-recall-candidate"
    ]
    if args.case_id:
        triage_rows = [row for row in triage_rows if row.get("case_id") == args.case_id]

    case_ids = sorted({row["case_id"] for row in triage_rows})
    if args.limit_cases is not None:
        selected_cases = set(case_ids[: args.limit_cases])
        triage_rows = [row for row in triage_rows if row["case_id"] in selected_cases]

    dashboard = read_json(Path(args.dashboard_json))
    case_paths = paths_by_case(dashboard)

    output_rows = score_gap_rows(
        triage_rows,
        case_paths=case_paths,
        reference_db=Path(args.reference_db),
    )
    payload = build_payload(
        output_rows,
        triage_csv=Path(args.triage_csv),
        dashboard_json=Path(args.dashboard_json),
        reference_db=Path(args.reference_db),
    )

    write_csv(Path(args.output_csv), output_rows)
    write_json(Path(args.output_json), payload)
    Path(args.output_doc).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_doc).write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(Path(args.output_doc)),
                "json": normalize_path(Path(args.output_json)),
                "csv": normalize_path(Path(args.output_csv)),
                "rows": payload["summary"]["rows"],
                "report_only_suggestions": payload["summary"]["report_only_suggestions"],
                "cases": payload["summary"]["cases"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def score_gap_rows(
    triage_rows: list[dict[str, str]],
    *,
    case_paths: dict[str, dict[str, Path]],
    reference_db: Path,
) -> list[dict[str, Any]]:
    rows_by_case_coordinate: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in triage_rows:
        rows_by_case_coordinate[(row["case_id"], row["coordinate"])].append(row)

    output: list[dict[str, Any]] = []
    for case_id in sorted({case_id for case_id, _ in rows_by_case_coordinate}):
        paths = case_paths.get(case_id) or {}
        apk_path = paths.get("apk")
        db_path = paths.get("slice_db") or reference_db
        if not apk_path or not apk_path.exists() or not db_path.exists():
            for (row_case, coordinate), rows in rows_by_case_coordinate.items():
                if row_case == case_id:
                    output.extend(missing_apk_rows(rows, coordinate=coordinate))
            continue

        apk_features = feature_set_from_apk_analysis(
            analyze_apk_dex(apk_path, include_members=True)
        )
        with sqlite3.connect(db_path) as connection:
            case_coordinates = sorted(
                coordinate
                for row_case, coordinate in rows_by_case_coordinate
                if row_case == case_id
            )
            for coordinate in case_coordinates:
                source_rows = rows_by_case_coordinate[(case_id, coordinate)]
                references = load_reference_components(connection, coordinate=coordinate)
                references_by_component = {reference.component_id: reference for reference in references}
                candidates = []
                for reference in references:
                    siblings = [
                        item.features
                        for item in references
                        if item.component_id != reference.component_id
                    ]
                    candidates.append(
                        score_reference_component(
                            apk_features,
                            reference,
                            sibling_features=siblings,
                        )
                    )
                candidates.sort(key=lambda item: item.score, reverse=True)
                decisions = build_version_decisions(candidates)
                reportable = {decision.coordinate for decision, _ in reportable_version_decisions(decisions)}
                decision_by_version = {decision.selected_version: decision for decision in decisions}
                candidate_by_version = {candidate.version: candidate for candidate in candidates}

                for row in source_rows:
                    version = row["source_version"]
                    candidate = candidate_by_version.get(version)
                    decision = decision_by_version.get(version)
                    if candidate is None:
                        output.append(
                            diagnostic_row(
                                row,
                                status="reference-not-loaded",
                                coordinate_rank="",
                                source_score=0.0,
                                best_score=candidates[0].score if candidates else 0.0,
                                best_version=candidates[0].version if candidates else "",
                                identity_confidence=0.0,
                                decision_status="",
                                evidence={},
                            )
                        )
                        continue
                    source_rank = 1 + sorted(
                        [item.score for item in candidates],
                        reverse=True,
                    ).index(candidate.score)
                    identity = identity_confidence_score(candidate)
                    status = classify_recall_status(
                        candidate_score=candidate.score,
                        identity_confidence=identity,
                        decision_status=decision.version_decision if decision else "",
                        coordinate_reportable=coordinate in reportable,
                    )
                    output.append(
                        diagnostic_row(
                            row,
                            status=status,
                            coordinate_rank=source_rank,
                            source_score=candidate.score,
                            best_score=candidates[0].score if candidates else 0.0,
                            best_version=candidates[0].version if candidates else "",
                            identity_confidence=identity,
                            decision_status=decision.version_decision if decision else "",
                            evidence=asdict(candidate.evidence),
                        )
                    )
    return output


def classify_recall_status(
    *,
    candidate_score: float,
    identity_confidence: float,
    decision_status: str,
    coordinate_reportable: bool,
) -> str:
    if candidate_score < 0.01:
        return "no-bytecode-signal"
    if candidate_score < 0.05:
        if identity_confidence >= 0.20:
            return "report-only-weak-source-context-suggestion"
        return "below-threshold"
    if decision_status == "uncertain":
        if identity_confidence >= 0.20:
            return "report-only-uncertain-source-context-suggestion"
        return "suppressed-uncertain"
    if not coordinate_reportable:
        return "suppressed-family-or-report-filter"
    if identity_confidence >= 0.20:
        return "report-only-source-context-suggestion"
    return "low-identity-signal"


def diagnostic_row(
    row: dict[str, str],
    *,
    status: str,
    coordinate_rank: int | str,
    source_score: float,
    best_score: float,
    best_version: str,
    identity_confidence: float,
    decision_status: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_id": row.get("case_id", ""),
        "app": row.get("app", ""),
        "coordinate": row.get("coordinate", ""),
        "source_version": row.get("source_version", ""),
        "recall_status": status,
        "source_rank": coordinate_rank,
        "source_score": round(float(source_score), 6),
        "best_version": best_version,
        "best_score": round(float(best_score), 6),
        "score_gap_to_best": round(max(0.0, float(best_score) - float(source_score)), 6),
        "identity_confidence": round(float(identity_confidence), 6),
        "decision_status": decision_status,
        "package_score": evidence.get("package_score", 0.0),
        "class_score": evidence.get("class_score", 0.0),
        "method_score": evidence.get("method_score", 0.0),
        "opcode_score": evidence.get("opcode_score", 0.0),
        "dependency_score": evidence.get("dependency_score", 0.0),
        "literal_score": evidence.get("literal_score", 0.0),
        "matched_classes": evidence.get("matched_classes", 0),
        "matched_methods": evidence.get("matched_methods", 0),
        "matched_packages": evidence.get("matched_packages", 0),
        "next_action": next_action_for_status(status),
    }


def next_action_for_status(status: str) -> str:
    if status.startswith("report-only"):
        return "surface-as-source-context-report-only-suggestion"
    if status == "below-threshold":
        return "needs-more-matcher-signal-or-lower-threshold-with-controls"
    if status == "no-bytecode-signal":
        return "likely-not-packaged-or-feature-blind"
    if status.startswith("suppressed"):
        return "inspect-report-filter-or-family-suppression"
    return "manual-review"


def missing_apk_rows(rows: list[dict[str, str]], *, coordinate: str) -> list[dict[str, Any]]:
    return [
        diagnostic_row(
            row,
            status="apk-path-missing",
            coordinate_rank="",
            source_score=0.0,
            best_score=0.0,
            best_version="",
            identity_confidence=0.0,
            decision_status="",
            evidence={},
        )
        for row in rows
    ]


def build_payload(
    rows: list[dict[str, Any]],
    *,
    triage_csv: Path,
    dashboard_json: Path,
    reference_db: Path,
) -> dict[str, Any]:
    status_counts = Counter(row["recall_status"] for row in rows)
    action_counts = Counter(row["next_action"] for row in rows)
    report_only_statuses = {
        "report-only-source-context-suggestion",
        "report-only-uncertain-source-context-suggestion",
        "report-only-weak-source-context-suggestion",
    }
    report_only = [row for row in rows if row["recall_status"] in report_only_statuses]
    return {
        "schema_version": 1,
        "sources": {
            "triage_csv": normalize_path(triage_csv),
            "dashboard_json": normalize_path(dashboard_json),
            "reference_db": normalize_path(reference_db),
        },
        "policy": (
            "This diagnostic is report-only. It scores exact source-version rows "
            "that were not emitted by the final source-version constrained run, "
            "and identifies source-context suggestions without changing SBOM "
            "components, vulnerability labels, or APK-only accuracy metrics."
        ),
        "summary": {
            "rows": len(rows),
            "cases": len({row["case_id"] for row in rows}),
            "coordinates": len({row["coordinate"] for row in rows}),
            "report_only_suggestions": len(report_only),
            "recall_status_counts": dict(sorted(status_counts.items())),
            "next_action_counts": dict(sorted(action_counts.items())),
        },
        "top_report_only_coordinates": top_coordinates(report_only),
        "top_no_signal_coordinates": top_coordinates(
            [row for row in rows if row["recall_status"] == "no-bytecode-signal"]
        ),
        "top_below_threshold_coordinates": top_coordinates(
            [row for row in rows if row["recall_status"] == "below-threshold"]
        ),
        "rows": rows,
    }


def top_coordinates(rows: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter(row["coordinate"] for row in rows)
    return [
        {"coordinate": coordinate, "rows": count}
        for coordinate, count in counts.most_common(limit)
    ]


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Demo Final Matcher Recall Diagnostics",
        "",
        "Generated by `scripts/build_demo_final_matcher_recall_diagnostics.py`.",
        "",
        "## Policy",
        "",
        payload["policy"],
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Rows scored | {summary['rows']} |",
        f"| Cases | {summary['cases']} |",
        f"| Coordinates | {summary['coordinates']} |",
        f"| Report-only source-context suggestions | {summary['report_only_suggestions']} |",
        "",
        "## Recall Status Counts",
        "",
        "| Status | Rows |",
        "|---|---:|",
    ]
    for status, count in summary["recall_status_counts"].items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(
        [
            "",
            "## Top Report-Only Suggestion Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    for row in payload["top_report_only_coordinates"]:
        lines.append(f"| `{row['coordinate']}` | {row['rows']} |")
    lines.extend(
        [
            "",
            "## Top No-Signal Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    for row in payload["top_no_signal_coordinates"]:
        lines.append(f"| `{row['coordinate']}` | {row['rows']} |")
    lines.extend(
        [
            "",
            "## Top Below-Threshold Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    for row in payload["top_below_threshold_coordinates"]:
        lines.append(f"| `{row['coordinate']}` | {row['rows']} |")
    lines.append("")
    return "\n".join(lines)


def paths_by_case(dashboard: dict[str, Any]) -> dict[str, dict[str, Path]]:
    output: dict[str, dict[str, Path]] = {}
    for case in dashboard.get("cases", []):
        case_id = str(case.get("case_id") or "")
        report_path = Path(((case.get("paths") or {}).get("report")) or "")
        if not case_id or not report_path.exists():
            continue
        report = read_json(report_path)
        apk_path = (((report.get("apk") or {}).get("apk_path")) or "")
        if apk_path:
            output[case_id] = {
                "apk": Path(apk_path),
                "slice_db": Path(((case.get("paths") or {}).get("slice_db")) or ""),
            }
    return output


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_path(path: Path) -> str:
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
