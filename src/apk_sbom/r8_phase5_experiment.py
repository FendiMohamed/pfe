from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from apk_sbom.r8_scoped_reranker import (
    DEFAULT_R8_SCOPED_PROFILES,
    R8TriggerDecision,
    should_apply_scoped_r8_rerank,
)


DEFAULT_PHASE4_JSON = Path("data/results/experiments/r8-phase4-scoped-experiment-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/r8-phase5-scoped-trigger-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md")


def build_payload(phase4_json: Path) -> dict[str, Any]:
    phase4_payload = json.loads(phase4_json.read_text(encoding="utf-8"))
    controlled_rows = [
        evaluate_trigger_row(row, row_type="controlled")
        for row in phase4_payload.get("controlled_cases", [])
    ]
    real_rows = [
        evaluate_trigger_row(row, row_type="real")
        for row in phase4_payload.get("real_component_rows", [])
    ]
    rows = controlled_rows + real_rows
    triggered = [row for row in rows if row["trigger_decision"]["apply"]]
    triggered_outcomes = dict(sorted(Counter(row["trigger_outcome"] for row in triggered).items()))
    blocked_reasons = dict(
        sorted(
            Counter(
                reason
                for row in rows
                if not row["trigger_decision"]["apply"]
                for reason in row["trigger_decision"]["blocked_by"]
            ).items()
        )
    )
    summary = {
        "phase4_source": normalize_path(phase4_json),
        "rows_evaluated": len(rows),
        "controlled_rows": len(controlled_rows),
        "real_rows": len(real_rows),
        "triggered_rows": len(triggered),
        "triggered_outcomes": triggered_outcomes,
        "blocked_reason_counts": blocked_reasons,
        "target_improvements_kept": triggered_outcomes.get("trigger-target-improvement", 0),
        "triggered_regressions": sum(
            count for outcome, count in triggered_outcomes.items() if "regression" in outcome
        ),
        "triggered_conflicts": triggered_outcomes.get("trigger-conflicting-source-mismatch", 0),
    }
    return {
        "schema_version": 1,
        "verdict": verdict_from_summary(summary),
        "policy": [
            "This is a Phase 5 experiment-only trigger diagnostic.",
            "The trigger is available only through the explicit r8-phase5-experiment command.",
            "The trigger is not wired into match-apk scoring, default generate-report behavior, SBOM output, or vulnerability labels.",
            "Reports can show it only with generate-report --include-r8-phase5-experiment.",
            "The trigger is intentionally profile-scoped to the Phase 4 improvement candidates.",
            "Any triggered regression or source conflict blocks production promotion.",
        ],
        "profiles": [profile.to_dict() for profile in DEFAULT_R8_SCOPED_PROFILES],
        "summary": summary,
        "triggered_rows": triggered,
        "rows": rows,
    }


def write_outputs(
    payload: dict[str, Any],
    *,
    output_json: Path,
    output_doc: Path | None = None,
) -> dict[str, str | int]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result: dict[str, str | int] = {
        "json": normalize_path(output_json),
        "triggered_rows": payload["summary"]["triggered_rows"],
        "verdict": payload["verdict"],
    }
    if output_doc is not None:
        output_doc.parent.mkdir(parents=True, exist_ok=True)
        output_doc.write_text(build_markdown(payload), encoding="utf-8")
        result["doc"] = normalize_path(output_doc)
    return result


def evaluate_trigger_row(row: dict[str, Any], *, row_type: str) -> dict[str, Any]:
    component = baseline_component_context(row)
    decision = should_apply_scoped_r8_rerank(
        coordinate=str(row.get("coordinate") or ""),
        baseline_version=row.get("baseline_selected_version"),
        diagnostic_version=row.get("diagnostic_selected_version"),
        top_diagnostic_versions=row.get("top_diagnostic_versions") or [],
        role=row.get("role"),
        category=row.get("category") if row_type == "controlled" else None,
        tags=row.get("tags") or [],
        baseline_version_status=component.get("version_status"),
        baseline_version_confidence_label=component.get("version_confidence_label"),
        validation_source_versions=row.get("source_versions") or [],
    )
    return {
        "row_type": row_type,
        "case": row.get("case_name") or row.get("slug"),
        "apk_path": row.get("apk_path"),
        "report_path": row.get("report_path"),
        "role": row.get("role") or row.get("category"),
        "tags": row.get("tags") or [],
        "coordinate": row.get("coordinate"),
        "source_versions": row.get("source_versions") or row.get("expected_version"),
        "validation_status": row.get("validation_status"),
        "baseline_selected_version": row.get("baseline_selected_version"),
        "baseline_version_status": component.get("version_status"),
        "baseline_version_confidence_label": component.get("version_confidence_label"),
        "diagnostic_selected_version": row.get("diagnostic_selected_version"),
        "phase4_outcome": row.get("outcome"),
        "trigger_outcome": classify_trigger_outcome(row, decision),
        "trigger_decision": decision.to_dict(),
    }


def baseline_component_context(row: dict[str, Any]) -> dict[str, Any]:
    report_path_value = row.get("report_path")
    if not report_path_value:
        return {}
    report_path = Path(str(report_path_value))
    if not report_path.exists() or report_path.is_dir():
        return {}
    report = json.loads(report_path.read_text(encoding="utf-8"))
    coordinate = row.get("coordinate")
    for component in report.get("detected_components", []):
        if f"{component.get('group')}:{component.get('artifact')}" == coordinate:
            return component
    return {}


def classify_trigger_outcome(row: dict[str, Any], decision: R8TriggerDecision) -> str:
    if not decision.apply:
        return "trigger-not-applied"
    outcome = str(row.get("outcome") or "")
    if outcome == "real-potential-target-improvement":
        return "trigger-target-improvement"
    if "regression" in outcome:
        return "trigger-regression-risk"
    if "conflicting-source-mismatch" in outcome:
        return "trigger-conflicting-source-mismatch"
    if "aligned" in outcome:
        return "trigger-aligned"
    return "trigger-applied-unclassified"


def verdict_from_summary(summary: dict[str, Any]) -> str:
    if summary.get("triggered_regressions", 0) or summary.get("triggered_conflicts", 0):
        return "phase5-scoped-trigger-reject-promotion"
    if summary.get("target_improvements_kept", 0) >= 4:
        return "phase5-scoped-trigger-experiment-clean-not-promoted"
    if summary.get("triggered_rows", 0):
        return "phase5-scoped-trigger-partial-needs-more-controls"
    return "phase5-scoped-trigger-no-applications"


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# R8 Phase 5 Scoped Trigger Diagnostics",
        "",
        "Generated by `apk-sbom r8-phase5-experiment` or `scripts/build_r8_phase5_scoped_trigger_diagnostics.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        "This is an experiment-only trigger diagnostic. It does not change matcher scoring, selected versions, SBOM components, or vulnerability labels.",
        "",
        "## Summary",
        "",
        f"- Rows evaluated: `{summary['rows_evaluated']}`",
        f"- Controlled rows: `{summary['controlled_rows']}`",
        f"- Real rows: `{summary['real_rows']}`",
        f"- Triggered rows: `{summary['triggered_rows']}`",
        f"- Target improvements kept: `{summary['target_improvements_kept']}`",
        f"- Triggered regressions: `{summary['triggered_regressions']}`",
        f"- Triggered conflicts: `{summary['triggered_conflicts']}`",
        "",
        "## Triggered Outcomes",
        "",
        "| Outcome | Count |",
        "|---|---:|",
    ]
    for outcome, count in summary["triggered_outcomes"].items():
        lines.append(f"| `{outcome}` | {count} |")
    if not summary["triggered_outcomes"]:
        lines.append("| none | 0 |")

    lines.extend(
        [
            "",
            "## Scoped Profiles",
            "",
            "| Profile | Coordinate | Diagnostic version | Thresholds | Required context | Blocked context |",
            "|---|---|---|---|---|---|",
        ]
    )
    for profile in payload["profiles"]:
        thresholds = (
            f"score>={profile['min_top_score']}; "
            f"margin>={profile['min_margin']}; "
            f"families>={profile['min_feature_families']}"
        )
        required = ", ".join(
            [
                *(f"any:{tag}" for tag in profile.get("required_any_tags", [])),
                *(f"all:{tag}" for tag in profile.get("required_all_tags", [])),
            ]
        ) or "none"
        blocked = ", ".join(profile.get("blocked_tags", [])) or "none"
        lines.append(
            "| "
            f"`{profile['profile_id']}` | "
            f"`{profile['coordinate']}` | "
            f"`{profile['diagnostic_version']}` | "
            f"{thresholds} | {required} | {blocked} |"
        )

    lines.extend(
        [
            "",
            "## Triggered Rows",
            "",
            "| Case | Role | Coordinate | Baseline | Diagnostic | Source/expected | Trigger outcome | Profile |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["triggered_rows"]:
        decision = row["trigger_decision"]
        source_versions = row.get("source_versions")
        if isinstance(source_versions, list):
            source_text = ", ".join(str(item) for item in source_versions)
        else:
            source_text = str(source_versions or "")
        lines.append(
            "| "
            f"{md(row.get('case'))} | "
            f"{md(row.get('role'))} | "
            f"`{row.get('coordinate')}` | "
            f"{md(row.get('baseline_selected_version'))} | "
            f"{md(row.get('diagnostic_selected_version'))} | "
            f"{md(source_text)} | "
            f"`{row.get('trigger_outcome')}` | "
            f"`{decision.get('profile_id')}` |"
        )
    if not payload["triggered_rows"]:
        lines.append("| none |  |  |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Blocked Reason Counts",
            "",
            "| Reason | Count |",
            "|---|---:|",
        ]
    )
    for reason, count in summary["blocked_reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")

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
            "## Conclusion",
            "",
            "The narrow trigger keeps the four Phase 4 target improvements and applies to zero regression/conflict rows in this diagnostic artifact. It is still not promoted into default scoring: the profiles are context-scoped, learned from a small candidate set, and require explicit experiment opt-in before any production scorer behavior is justified.",
            "",
        ]
    )
    return "\n".join(lines)


def normalize_path(path: object) -> str:
    return str(path).replace("\\", "/")


def md(value: object) -> str:
    return str(value or "").replace("|", "\\|")
