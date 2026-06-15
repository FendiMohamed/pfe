from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_REPORTS = (
    Path("data/results/experiments/r8-phase5-report-evidence/report-real-antennapod/report.json"),
    Path("data/results/experiments/r8-phase5-report-evidence/report-real-wikipedia-android/report.json"),
    Path("data/results/experiments/r8-phase5-report-evidence/report-real-aegis-authenticator/report.json"),
    Path("data/results/experiments/r8-phase5-report-evidence/report-real-nextcloud-android/report.json"),
)
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/r8-phase5-report-evidence/summary.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize opt-in report-only Phase 5 evidence from generated reports."
    )
    parser.add_argument(
        "--report",
        action="append",
        default=[],
        help="Report JSON path. Can be repeated. Defaults to the four current Phase 5 target reports.",
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
                "suggestions": payload["summary"]["phase5_suggestions"],
                "default_selection_changes": payload["summary"]["default_selection_changes"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(report_paths: list[Path]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    missing_phase5 = []
    for report_path in report_paths:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        experiment = report.get("r8_phase5_experiment")
        if not experiment:
            missing_phase5.append(normalize_path(report_path))
            continue
        for row in experiment.get("matching_triggered_rows", []):
            coordinate = str(row.get("coordinate") or "")
            component = component_by_coordinate(report, coordinate)
            mvp_version = component.get("version") if component else None
            baseline_version = row.get("baseline_selected_version")
            phase5_version = row.get("diagnostic_selected_version")
            rows.append(
                {
                    "report": normalize_path(report_path),
                    "case": row.get("case"),
                    "coordinate": coordinate,
                    "mvp_selected_version": mvp_version,
                    "phase5_baseline_version": baseline_version,
                    "phase5_suggestion": phase5_version,
                    "source_versions": row.get("source_versions") or [],
                    "trigger_outcome": row.get("trigger_outcome"),
                    "profile_id": row.get("trigger_decision", {}).get("profile_id"),
                    "report_only": bool(experiment.get("report_only")),
                    "default_selection_changed": mvp_version != baseline_version,
                    "detected_components": len(report.get("detected_components", [])),
                    "sbom": report.get("artifacts", {}).get("sbom_json"),
                }
            )
    outcome_counts = Counter(str(row["trigger_outcome"]) for row in rows)
    reports_with_rows = {row["report"] for row in rows}
    summary = {
        "reports": len(report_paths),
        "reports_with_phase5_evidence": len(report_paths) - len(missing_phase5),
        "reports_with_matching_suggestions": len(reports_with_rows),
        "reports_with_sbom": sum(1 for row in rows if row.get("sbom")),
        "phase5_suggestions": len(rows),
        "report_only_suggestions": sum(1 for row in rows if row["report_only"]),
        "default_selection_changes": sum(1 for row in rows if row["default_selection_changed"]),
        "trigger_outcomes": dict(sorted(outcome_counts.items())),
        "missing_phase5_reports": missing_phase5,
    }
    return {
        "schema_version": 1,
        "verdict": verdict_from_summary(summary),
        "summary": summary,
        "policy": [
            "This summarizes opt-in report-only Phase 5 evidence.",
            "The report section surfaces research-backed suggestions but does not change detected components, selected versions, SBOM output, vulnerability labels, or source-validation metrics.",
            "A nonzero default_selection_changes count would mean the report-only boundary was violated.",
        ],
        "rows": rows,
    }


def verdict_from_summary(summary: dict[str, Any]) -> str:
    if summary["default_selection_changes"]:
        return "phase5-report-evidence-failed-default-selection-changed"
    if summary["missing_phase5_reports"]:
        return "phase5-report-evidence-incomplete-missing-report-evidence"
    if summary["phase5_suggestions"] == 0:
        return "phase5-report-evidence-incomplete-no-suggestions"
    if summary["report_only_suggestions"] != summary["phase5_suggestions"]:
        return "phase5-report-evidence-failed-non-report-only-suggestion"
    return "phase5-report-evidence-clean-experiment-only"


def component_by_coordinate(report: dict[str, Any], coordinate: str) -> dict[str, Any] | None:
    for component in report.get("detected_components", []):
        if f"{component.get('group')}:{component.get('artifact')}" == coordinate:
            return component
    return None


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# R8 Phase 5 Report Evidence",
        "",
        "Generated by `scripts/build_r8_phase5_report_evidence.py`.",
        "",
        "This artifact summarizes the opt-in `generate-report --include-r8-phase5-experiment` evidence for the four current Phase 5 target APKs.",
        "",
        "## Summary",
        "",
        f"- Verdict: `{payload['verdict']}`",
        f"- Reports checked: `{summary['reports']}`",
        f"- Reports with Phase 5 evidence: `{summary['reports_with_phase5_evidence']}`",
        f"- Reports with matching suggestions: `{summary['reports_with_matching_suggestions']}`",
        f"- Reports with SBOM artifacts: `{summary['reports_with_sbom']}`",
        f"- Phase 5 suggestions surfaced: `{summary['phase5_suggestions']}`",
        f"- Report-only suggestions: `{summary['report_only_suggestions']}`",
        f"- Default selection changes: `{summary['default_selection_changes']}`",
        "",
        "## Suggestions",
        "",
        "| Case | Coordinate | MVP selected | Phase 5 suggestion | Source version | Outcome | Profile | Report |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]
    for row in payload["rows"]:
        source_versions = row.get("source_versions") or []
        if isinstance(source_versions, list):
            source_text = ", ".join(str(item) for item in source_versions)
        else:
            source_text = str(source_versions)
        lines.append(
            "| "
            f"{md(row.get('case'))} | "
            f"`{row.get('coordinate')}` | "
            f"{md(row.get('mvp_selected_version'))} | "
            f"{md(row.get('phase5_suggestion'))} | "
            f"{md(source_text)} | "
            f"`{row.get('trigger_outcome')}` | "
            f"`{row.get('profile_id')}` | "
            f"`{row.get('report')}` |"
        )
    if not payload["rows"]:
        lines.append("| none |  |  |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Policy",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The four current target reports surface one Phase 5 suggestion each, and default selection changes remain `0`. This confirms the report-only evidence path is useful for dataset growth while preserving the MVP SBOM boundary.",
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
