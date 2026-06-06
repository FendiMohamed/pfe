from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_REPORTS = (
    Path(
        "data/results/experiments/r8-minified-confidence-report-evidence/"
        "report-real-antennapod/report.json"
    ),
    Path(
        "data/results/experiments/r8-minified-confidence-report-evidence/"
        "report-real-wikipedia-android/report.json"
    ),
    Path(
        "data/results/experiments/r8-minified-confidence-report-evidence/"
        "report-real-aegis-authenticator/report.json"
    ),
    Path(
        "data/results/experiments/r8-minified-confidence-report-evidence/"
        "report-real-nextcloud-android/report.json"
    ),
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/r8-minified-confidence-report-evidence/summary.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_MINIFIED_CONFIDENCE_REPORT_EVIDENCE.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize opt-in report-only R8 minified confidence policy evidence "
            "from generated reports."
        )
    )
    parser.add_argument(
        "--report",
        action="append",
        default=[],
        help="Report JSON path. Can be repeated. Defaults to the four current target reports.",
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report_paths = [Path(path) for path in args.report] if args.report else list(DEFAULT_REPORTS)
    payload = build_payload(report_paths)

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
                "reports": payload["summary"]["reports"],
                "suggestions": payload["summary"]["report_only_suggestions"],
                "blocked_rows": payload["summary"]["blocked_regression_risk_rows"],
                "default_selection_changes": payload["summary"][
                    "default_selection_changes"
                ],
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(report_paths: list[Path]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    missing_policy: list[str] = []
    for report_path in report_paths:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        evidence = report.get("r8_minified_confidence_policy")
        if not evidence:
            missing_policy.append(normalize_path(report_path))
            continue
        for row_type, rows_key in (
            ("report-only-suggestion", "matching_report_only_suggestions"),
            ("blocked-regression-risk", "matching_blocked_regression_risks"),
        ):
            for row in evidence.get(rows_key, []):
                coordinate = str(row.get("coordinate") or "")
                component = component_by_coordinate(report, coordinate)
                mvp_version = component.get("version") if component else None
                baseline_version = row.get("baseline_selected_version")
                rows.append(
                    {
                        "report": normalize_path(report_path),
                        "row_type": row_type,
                        "case": row.get("case"),
                        "coordinate": coordinate,
                        "mvp_selected_version": mvp_version,
                        "baseline_selected_version": baseline_version,
                        "diagnostic_selected_version": row.get(
                            "diagnostic_selected_version"
                        ),
                        "confidence_label": row.get("confidence_label"),
                        "policy_action": row.get("policy_action"),
                        "report_only": bool(evidence.get("report_only")),
                        "default_selection_changed": mvp_version != baseline_version,
                        "detected_components": len(report.get("detected_components", [])),
                        "sbom": report.get("artifacts", {}).get("sbom_json"),
                    }
                )
    report_only_suggestions = [
        row for row in rows if row["row_type"] == "report-only-suggestion"
    ]
    blocked = [row for row in rows if row["row_type"] == "blocked-regression-risk"]
    reports_with_suggestions = {row["report"] for row in report_only_suggestions}
    reports_with_blocked = {row["report"] for row in blocked}
    summary = {
        "reports": len(report_paths),
        "reports_with_policy_evidence": len(report_paths) - len(missing_policy),
        "reports_with_matching_suggestions": len(reports_with_suggestions),
        "reports_with_blocked_rows": len(reports_with_blocked),
        "reports_with_sbom": len({row["report"] for row in rows if row.get("sbom")}),
        "matching_rows": len(rows),
        "report_only_suggestions": len(report_only_suggestions),
        "blocked_regression_risk_rows": len(blocked),
        "default_selection_changes": sum(
            1 for row in rows if row["default_selection_changed"]
        ),
        "non_report_only_rows": sum(1 for row in rows if not row["report_only"]),
        "missing_policy_reports": missing_policy,
    }
    return {
        "schema_version": 1,
        "verdict": verdict_from_summary(summary),
        "summary": summary,
        "policy": [
            "This summarizes opt-in report-only minified/R8 confidence policy evidence.",
            "The report section surfaces confidence/ambiguity wording and source-backed diagnostic suggestions without changing detected components, selected versions, SBOM output, vulnerability labels, or source-validation metrics.",
            "A nonzero default_selection_changes count would mean the report-only boundary was violated.",
        ],
        "rows": rows,
    }


def verdict_from_summary(summary: dict[str, Any]) -> str:
    if summary["default_selection_changes"]:
        return "r8-minified-confidence-report-evidence-failed-default-selection-changed"
    if summary["non_report_only_rows"]:
        return "r8-minified-confidence-report-evidence-failed-non-report-only-row"
    if summary["missing_policy_reports"]:
        return "r8-minified-confidence-report-evidence-incomplete-missing-policy"
    if summary["report_only_suggestions"] == 0:
        return "r8-minified-confidence-report-evidence-incomplete-no-suggestions"
    return "r8-minified-confidence-report-evidence-clean-report-only"


def component_by_coordinate(report: dict[str, Any], coordinate: str) -> dict[str, Any] | None:
    for component in report.get("detected_components", []):
        if f"{component.get('group')}:{component.get('artifact')}" == coordinate:
            return component
    return None


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# R8 Minified Confidence Report Evidence",
        "",
        "Generated by `scripts/build_r8_minified_confidence_report_evidence.py`.",
        "",
        "This artifact summarizes the opt-in `generate-report --include-r8-minified-confidence-policy` evidence for the four current minified/R8 target APKs.",
        "",
        "## Summary",
        "",
        f"- Verdict: `{payload['verdict']}`",
        f"- Reports checked: `{summary['reports']}`",
        f"- Reports with policy evidence: `{summary['reports_with_policy_evidence']}`",
        f"- Reports with matching suggestions: `{summary['reports_with_matching_suggestions']}`",
        f"- Reports with blocked rows: `{summary['reports_with_blocked_rows']}`",
        f"- Reports with SBOM artifacts: `{summary['reports_with_sbom']}`",
        f"- Matching rows surfaced: `{summary['matching_rows']}`",
        f"- Report-only suggestions: `{summary['report_only_suggestions']}`",
        f"- Blocked regression-risk rows: `{summary['blocked_regression_risk_rows']}`",
        f"- Default selection changes: `{summary['default_selection_changes']}`",
        "",
        "## Surfaced Rows",
        "",
        "| Type | Case | Coordinate | MVP selected | Diagnostic | Confidence | Policy | Report |",
        "|---|---|---|---:|---:|---|---|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            f"`{md(row.get('row_type'))}` | "
            f"{md(row.get('case'))} | "
            f"`{row.get('coordinate')}` | "
            f"{md(row.get('mvp_selected_version'))} | "
            f"{md(row.get('diagnostic_selected_version'))} | "
            f"`{md(row.get('confidence_label'))}` | "
            f"`{md(row.get('policy_action'))}` | "
            f"`{md(row.get('report'))}` |"
        )
    if not payload["rows"]:
        lines.append("| none |  |  |  |  |  |  |  |")
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The four target reports surface confidence/ambiguity wording while preserving the official MVP selected versions. The report-only suggestions remain separate diagnostic alternatives, and blocked rows explain why broader optimization-aware selection changes remain unsafe.",
            "",
        ]
    )
    return "\n".join(lines)


def normalize_path(path: object) -> str:
    return str(path).replace("\\", "/")


def md(value: object) -> str:
    return str(value or "").replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
