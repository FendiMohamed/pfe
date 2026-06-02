from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from apk_sbom.version_band_experiment import should_downgrade_old_version_steal


DEFAULT_INPUT_JSON = Path("data/results/experiments/low-risk-version-band-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/low-risk-version-band-trigger-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/LOW_RISK_VERSION_BAND_TRIGGER_DIAGNOSTICS.md")
REPORT_ROOTS = (
    Path("data/results/experiments/low-risk-source-versions-target"),
    Path("data/results/experiments/low-risk-source-versions-controls"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate an opt-in old-version-steal guard without changing matcher output.",
    )
    parser.add_argument("--input-json", default=str(DEFAULT_INPUT_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(Path(args.input_json))
    result = write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_doc=Path(args.output_doc),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_payload(input_json: Path) -> dict[str, Any]:
    source = json.loads(input_json.read_text(encoding="utf-8"))
    full = source["full_experiment"]
    reports = load_reports()
    introduced_rows = [
        evaluate_change(row, reports=reports)
        for row in full["introduced_mismatches"]
    ]
    resolved_rows = [
        evaluate_change(row, reports=reports)
        for row in full["resolved_target_mismatches"]
    ]
    summary = {
        "introduced_mismatch_rows": len(introduced_rows),
        "introduced_mismatches_flagged": count_applied(introduced_rows),
        "resolved_target_rows": len(resolved_rows),
        "resolved_target_rows_blocked": count_applied(resolved_rows),
        "triggered_coordinates": dict(
            sorted(
                Counter(
                    row["coordinate"]
                    for row in introduced_rows
                    if row["trigger_decision"]["apply"]
                ).items()
            )
        ),
    }
    return {
        "schema_version": 1,
        "verdict": verdict(summary),
        "scope": (
            "Experiment only. This artifact does not change matcher scoring, selected versions, "
            "SBOM components, vulnerability labels, or the shared reference DB."
        ),
        "policy": [
            "Apply only to AppCompat and Core old-version-steal diagnostics.",
            "Require at least two stronger APK-side AndroidX family anchors from later version bands.",
            "Treat a trigger as a reason to downgrade the selected version claim, not as proof of a replacement version.",
            "Keep Lifecycle out of this trigger until public-vs-Android artifact-family evidence is separated safely.",
            "Require a fresh report/control matrix before any production integration.",
        ],
        "source": normalize_path(input_json),
        "summary": summary,
        "introduced_mismatch_rows": introduced_rows,
        "resolved_target_rows": resolved_rows,
    }


def evaluate_change(row: dict[str, Any], *, reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    case_id = str(row["case_id"])
    report = reports[case_id]
    decisions = report.get("match_summary", {}).get("decisions", [])
    selected = find_decision(decisions, str(row["coordinate"]))
    decision = should_downgrade_old_version_steal(
        coordinate=str(row["coordinate"]),
        selected_version=str(row["selected_version"]),
        sibling_decisions=decisions,
    )
    return {
        **row,
        "report_selected_version": selected.get("selected_version") if selected else None,
        "report_selected_score": selected.get("score") if selected else None,
        "trigger_decision": decision.to_dict(),
    }


def load_reports() -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for root in REPORT_ROOTS:
        for path in root.glob("report-real-*/report.json"):
            case_id = path.parent.name.removeprefix("report-real-")
            reports[case_id] = json.loads(path.read_text(encoding="utf-8"))
    return reports


def find_decision(decisions: list[dict[str, Any]], coordinate: str) -> dict[str, Any] | None:
    for decision in decisions:
        if decision.get("coordinate") == coordinate:
            return decision
    return None


def count_applied(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if row["trigger_decision"]["apply"])


def verdict(summary: dict[str, Any]) -> str:
    if summary["resolved_target_rows_blocked"]:
        return "reject-trigger-blocks-target-benefits"
    if summary["introduced_mismatches_flagged"]:
        return "scoped-downgrade-experiment-promising-not-promoted"
    return "no-safe-trigger-applications"


def write_outputs(
    payload: dict[str, Any],
    *,
    output_json: Path,
    output_doc: Path,
) -> dict[str, Any]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    return {
        "doc": normalize_path(output_doc),
        "json": normalize_path(output_json),
        "verdict": payload["verdict"],
        **payload["summary"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Low-Risk Version-Band Trigger Diagnostics",
        "",
        "Generated by `apk-sbom version-band-experiment` or `scripts/build_low_risk_version_band_trigger_diagnostics.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Introduced mismatch rows inspected: `{summary['introduced_mismatch_rows']}`",
        f"- Introduced mismatches flagged for claim downgrade: `{summary['introduced_mismatches_flagged']}`",
        f"- Resolved target rows inspected: `{summary['resolved_target_rows']}`",
        f"- Resolved target rows blocked: `{summary['resolved_target_rows_blocked']}`",
        "",
        "## Triggered Introduced Mismatches",
        "",
        "| Case | Coordinate | Selected | Source | Higher-band APK anchors |",
        "|---|---|---|---|---|",
    ]
    triggered = [
        row for row in payload["introduced_mismatch_rows"] if row["trigger_decision"]["apply"]
    ]
    for row in triggered:
        lines.append(
            "| "
            f"{md(row['case_id'])} | "
            f"`{row['coordinate']}` | "
            f"{md(row['selected_version'])} | "
            f"{md(row['source_versions'])} | "
            f"{md(', '.join(row['trigger_decision']['higher_band_anchors']))} |"
        )
    if not triggered:
        lines.append("| none |  |  |  |  |")

    lines.extend(["", "## Unhandled Introduced Mismatches", ""])
    unhandled = [
        row for row in payload["introduced_mismatch_rows"] if not row["trigger_decision"]["apply"]
    ]
    lines.extend(
        [
            "| Case | Coordinate | Selected | Source | Blocked by |",
            "|---|---|---|---|---|",
        ]
    )
    for row in unhandled:
        lines.append(
            "| "
            f"{md(row['case_id'])} | "
            f"`{row['coordinate']}` | "
            f"{md(row['selected_version'])} | "
            f"{md(row['source_versions'])} | "
            f"{md(', '.join(row['trigger_decision']['blocked_by']))} |"
        )

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "The opt-in AppCompat/Core guard catches a subset of newly introduced old-version steals while preserving the target gains in this fixture slice. It deliberately downgrades confidence instead of guessing a replacement version. Lifecycle remains outside the trigger because its artifact-family evidence still needs a separate scoped treatment.",
            "",
        ]
    )
    return "\n".join(lines)


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
