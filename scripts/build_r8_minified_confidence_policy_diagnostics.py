from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


DEFAULT_PHASE4_JSON = Path("data/results/experiments/r8-phase4-scoped-experiment-diagnostics.json")
DEFAULT_PHASE5_VALIDATION_JSON = Path(
    "data/results/experiments/r8-phase5-trigger-control-validation.json"
)
DEFAULT_PHASE5_REPORT_JSON = Path(
    "data/results/experiments/r8-phase5-report-evidence/summary.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/r8-minified-confidence-policy-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_MINIFIED_CONFIDENCE_POLICY_DIAGNOSTICS.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a report-only confidence and ambiguity policy diagnostic for "
            "R8/minified rows. This does not change matcher, SBOM, vulnerability, "
            "or source-validation behavior."
        )
    )
    parser.add_argument("--phase4-json", default=str(DEFAULT_PHASE4_JSON))
    parser.add_argument("--phase5-validation-json", default=str(DEFAULT_PHASE5_VALIDATION_JSON))
    parser.add_argument("--phase5-report-json", default=str(DEFAULT_PHASE5_REPORT_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        phase4_json=Path(args.phase4_json),
        phase5_validation_json=Path(args.phase5_validation_json),
        phase5_report_json=Path(args.phase5_report_json),
    )
    result = write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_doc=Path(args.output_doc),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_payload(
    *,
    phase4_json: Path = DEFAULT_PHASE4_JSON,
    phase5_validation_json: Path = DEFAULT_PHASE5_VALIDATION_JSON,
    phase5_report_json: Path = DEFAULT_PHASE5_REPORT_JSON,
) -> dict[str, Any]:
    phase4 = read_json(phase4_json)
    phase5_validation = read_json(phase5_validation_json)
    phase5_report = read_json(phase5_report_json)
    triggered = phase5_triggered_by_key(phase5_validation)
    controlled_rows = [
        classify_row(row, row_type="controlled", triggered={})
        for row in phase4.get("controlled_cases", [])
    ]
    real_rows = [
        classify_row(row, row_type="real", triggered=triggered)
        for row in phase4.get("real_component_rows", [])
    ]
    rows = controlled_rows + real_rows
    summary = build_summary(rows, phase4, phase5_validation, phase5_report)
    gates = build_gates(summary, rows, phase5_validation, phase5_report)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    summary["failed_gates"] = len(failed_gates)
    return {
        "schema_version": 1,
        "verdict": verdict(failed_gates),
        "recommendation": recommendation(failed_gates),
        "scope": (
            "Report-only confidence and ambiguity policy diagnostic for R8/minified "
            "rows. It classifies existing Phase 4 and Phase 5 evidence into "
            "explanation labels and policy actions, but it does not change matcher "
            "scoring, selected versions, SBOM components, vulnerability labels, or "
            "source-validation metrics."
        ),
        "sources": {
            "phase4_json": normalize_path(phase4_json),
            "phase5_validation_json": normalize_path(phase5_validation_json),
            "phase5_report_json": normalize_path(phase5_report_json),
        },
        "policy": [
            "Regression-risk rows must keep the default selected version and carry an ambiguity warning.",
            "Source-backed Phase 5 target improvements may be surfaced only as report-only suggestions.",
            "Single-reference, unvalidated, or source-mismatch rows are boundary evidence, not accuracy gains.",
            "Shrink, rename, package-flattening, low literal/context support, and narrow score margins are confidence signals, not promotion triggers.",
        ],
        "summary": summary,
        "rows": rows,
        "gates": gates,
    }


def classify_row(
    row: Mapping[str, Any],
    *,
    row_type: str,
    triggered: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    case_name = case_label(row)
    coordinate = str(row.get("coordinate") or "")
    trigger_row = triggered.get((case_name, coordinate))
    stats = multiscale_rank_stats(row.get("top_diagnostic_versions"))
    source_versions = [str(version) for version in row.get("source_versions") or []]
    baseline = str(row.get("baseline_selected_version") or "")
    diagnostic = str(row.get("diagnostic_selected_version") or "")
    outcome = str(row.get("outcome") or "")
    signals = build_signals(
        row,
        row_type=row_type,
        trigger_row=trigger_row,
        stats=stats,
        source_versions=source_versions,
        baseline=baseline,
        diagnostic=diagnostic,
    )
    policy_label, confidence_label, policy_action = classify_policy(
        outcome=outcome,
        trigger_row=trigger_row,
        signals=signals,
    )
    return {
        "row_type": row_type,
        "case": case_name,
        "coordinate": coordinate,
        "apk_path": row.get("apk_path"),
        "report_path": row.get("report_path"),
        "validation_path": row.get("validation_path"),
        "role": row.get("role"),
        "category": row.get("category"),
        "outcome": outcome,
        "baseline_selected_version": baseline or None,
        "diagnostic_selected_version": diagnostic or None,
        "source_versions": source_versions,
        "policy_label": policy_label,
        "confidence_label": confidence_label,
        "policy_action": policy_action,
        "signals": signals,
        "diagnostic_source_match": diagnostic in source_versions if source_versions else None,
        "baseline_source_match": baseline in source_versions if source_versions else None,
        "phase5_triggered": trigger_row is not None,
        "phase5_profile": (
            trigger_row.get("trigger_decision", {}).get("profile_id") if trigger_row else None
        ),
        "top_score": stats["top_score"],
        "score_margin": stats["score_margin"],
        "supporting_feature_families": stats["supporting_feature_families"],
    }


def classify_policy(
    *,
    outcome: str,
    trigger_row: Mapping[str, Any] | None,
    signals: Sequence[str],
) -> tuple[str, str, str]:
    signal_set = set(signals)
    if "regression-risk" in outcome:
        return (
            "block-default-change-regression-risk",
            "ambiguous",
            "do-not-change-selected-version",
        )
    if trigger_row is not None:
        return (
            "report-only-source-backed-low-confidence-suggestion",
            "low-confidence-source-backed",
            "surface-report-only-suggestion",
        )
    if "single-reference-not-rankable" in outcome:
        return (
            "boundary-single-reference-not-rankable",
            "unrankable",
            "keep-current-output-with-boundary-note",
        )
    if "layer-covered-unvalidated" in outcome:
        return (
            "boundary-covered-but-unvalidated",
            "unvalidated",
            "keep-current-output-with-boundary-note",
        )
    if "source-mismatch" in outcome:
        return (
            "explain-source-mismatch-boundary",
            "ambiguous",
            "keep-current-output-with-source-mismatch-note",
        )
    if "aligned" in outcome:
        if signal_set.intersection(
            {
                "near-zero-score-margin",
                "narrow-score-margin",
                "missing-literal-context",
                "weak-literal-context",
                "low-feature-family-agreement",
            }
        ):
            return (
                "stable-selection-with-ambiguity-note",
                "medium",
                "keep-current-output-with-ambiguity-note",
            )
        return ("stable-selection", "high", "keep-current-output")
    return ("unclassified-boundary", "unknown", "keep-current-output-with-boundary-note")


def build_signals(
    row: Mapping[str, Any],
    *,
    row_type: str,
    trigger_row: Mapping[str, Any] | None,
    stats: Mapping[str, Any],
    source_versions: Sequence[str],
    baseline: str,
    diagnostic: str,
) -> list[str]:
    signals: list[str] = [f"{row_type}-row"]
    category = str(row.get("category") or "")
    if category:
        signals.append(category)
        if "shrink" in category:
            signals.append("r8-shrink-signal")
        if "rename" in category:
            signals.append("r8-rename-signal")
        if "package" in category or "repackage" in category:
            signals.append("r8-package-flattening-signal")
        if "inline" in category:
            signals.append("r8-inline-signal")
        if "optimize" in category:
            signals.append("r8-optimize-signal")
    tag_set = {str(tag) for tag in row.get("tags") or []}
    for tag in ("native", "multidex", "compose", "kotlin", "large-modern-tree"):
        if tag in tag_set:
            signals.append(f"context-{tag}")
    if diagnostic and baseline and diagnostic != baseline:
        signals.append("diagnostic-changes-baseline")
    if source_versions:
        if baseline in source_versions:
            signals.append("source-confirms-baseline")
        if diagnostic in source_versions:
            signals.append("source-confirms-diagnostic")
        elif diagnostic:
            signals.append("source-rejects-diagnostic")
    if trigger_row is not None:
        signals.append("phase5-report-only-trigger")
        baseline_label = str(trigger_row.get("baseline_version_confidence_label") or "")
        if baseline_label == "low":
            signals.append("baseline-low-confidence")
    if float(stats["score_margin"]) < 0.005:
        signals.append("near-zero-score-margin")
    elif float(stats["score_margin"]) < 0.02:
        signals.append("narrow-score-margin")
    if int(stats["supporting_feature_families"]) < 3:
        signals.append("low-feature-family-agreement")
    literal_context = stats.get("leader_literal_context")
    if literal_context is not None:
        if float(literal_context) == 0.0:
            signals.append("missing-literal-context")
        elif float(literal_context) < 0.45:
            signals.append("weak-literal-context")
    return sorted(dict.fromkeys(signals))


def build_summary(
    rows: Sequence[Mapping[str, Any]],
    phase4: Mapping[str, Any],
    phase5_validation: Mapping[str, Any],
    phase5_report: Mapping[str, Any],
) -> dict[str, Any]:
    label_counts = Counter(str(row["policy_label"]) for row in rows)
    action_counts = Counter(str(row["policy_action"]) for row in rows)
    confidence_counts = Counter(str(row["confidence_label"]) for row in rows)
    signal_counts: Counter[str] = Counter()
    for row in rows:
        signal_counts.update(str(signal) for signal in row.get("signals", []))
    controlled_count = len(phase4.get("controlled_cases", []))
    real_count = len(phase4.get("real_component_rows", []))
    regression_rows = [
        row for row in rows if row["policy_label"] == "block-default-change-regression-risk"
    ]
    phase5_suggestions = [
        row
        for row in rows
        if row["policy_label"] == "report-only-source-backed-low-confidence-suggestion"
    ]
    report_summary = phase5_report.get("summary", {})
    validation_summary = phase5_validation.get("summary", {})
    return {
        "phase4_rows_evaluated": controlled_count + real_count,
        "rows_classified": len(rows),
        "controlled_rows": controlled_count,
        "real_rows": real_count,
        "regression_rows_blocked": len(regression_rows),
        "source_backed_report_only_suggestions": sum(
            1 for row in phase5_suggestions if row["diagnostic_source_match"] is True
        ),
        "phase5_report_only_suggestions": len(phase5_suggestions),
        "phase5_validation_triggered_rows": int(validation_summary.get("triggered_rows") or 0),
        "report_default_selection_changes": int(
            report_summary.get("default_selection_changes") or 0
        ),
        "phase5_production_imports": len(phase5_validation.get("production_imports", [])),
        "policy_label_counts": dict(sorted(label_counts.items())),
        "policy_action_counts": dict(sorted(action_counts.items())),
        "confidence_label_counts": dict(sorted(confidence_counts.items())),
        "top_signals": dict(signal_counts.most_common(20)),
    }


def build_gates(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    phase5_validation: Mapping[str, Any],
    phase5_report: Mapping[str, Any],
) -> list[dict[str, Any]]:
    regression_failures = [
        row
        for row in rows
        if "regression-risk" in str(row.get("outcome"))
        and row.get("policy_action") != "do-not-change-selected-version"
    ]
    suggestion_failures = [
        row
        for row in rows
        if row.get("policy_action") == "surface-report-only-suggestion"
        and not (
            row.get("phase5_triggered") is True and row.get("diagnostic_source_match") is True
        )
    ]
    return [
        gate(
            "phase4-row-coverage",
            fail_count=0
            if summary["rows_classified"] == summary["phase4_rows_evaluated"]
            else 1,
            evidence=(
                f"{summary['rows_classified']} classified / "
                f"{summary['phase4_rows_evaluated']} Phase 4 rows."
            ),
        ),
        gate(
            "regression-risk-rows-block-default-change",
            fail_count=len(regression_failures),
            evidence=(
                f"{summary['regression_rows_blocked']} regression-risk rows carry "
                "do-not-change-selected-version policy."
            ),
        ),
        gate(
            "phase5-suggestions-source-backed-report-only",
            fail_count=len(suggestion_failures),
            evidence=(
                f"{summary['source_backed_report_only_suggestions']} / "
                f"{summary['phase5_report_only_suggestions']} report-only suggestions "
                "are source-backed Phase 5 triggers."
            ),
        ),
        gate(
            "phase5-report-boundary-clean",
            fail_count=0
            if phase5_report.get("verdict") == "phase5-report-evidence-clean-experiment-only"
            and summary["report_default_selection_changes"] == 0
            else 1,
            evidence=(
                f"Report verdict={phase5_report.get('verdict')}; "
                f"{summary['report_default_selection_changes']} default selection changes."
            ),
        ),
        gate(
            "phase5-validation-controls-clean",
            fail_count=0
            if phase5_validation.get("verdict")
            == "phase5-trigger-current-control-clean-experiment-only"
            else 1,
            evidence=f"Phase 5 validation verdict={phase5_validation.get('verdict')}.",
        ),
        gate(
            "production-default-not-wired",
            fail_count=int(summary["phase5_production_imports"]),
            evidence=f"{summary['phase5_production_imports']} production imports of scoped trigger.",
        ),
    ]


def verdict(failed_gates: Sequence[Mapping[str, Any]]) -> str:
    if failed_gates:
        return "r8-minified-confidence-policy-diagnostic-incomplete"
    return "r8-minified-confidence-policy-report-only-ready"


def recommendation(failed_gates: Sequence[Mapping[str, Any]]) -> str:
    if failed_gates:
        return "fix-confidence-policy-inputs-before-documenting-report-labels"
    return "document-minified-confidence-labels-without-changing-default-selection"


def gate(gate_id: str, *, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


def phase5_triggered_by_key(
    phase5_validation: Mapping[str, Any],
) -> dict[tuple[str, str], Mapping[str, Any]]:
    rows: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in phase5_validation.get("triggered_rows", []):
        rows[(str(row.get("case") or ""), str(row.get("coordinate") or ""))] = row
    return rows


def multiscale_rank_stats(
    top_diagnostic_versions: Sequence[Mapping[str, Any]] | None,
) -> dict[str, Any]:
    if not top_diagnostic_versions:
        return {
            "top_score": 0.0,
            "score_margin": 0.0,
            "supporting_feature_families": 0,
            "leader_literal_context": None,
        }
    leader = top_diagnostic_versions[0]
    top_score = float_value(leader.get("diagnostic_score"))
    second_score = (
        float_value(top_diagnostic_versions[1].get("diagnostic_score"))
        if len(top_diagnostic_versions) > 1
        else 0.0
    )
    feature_scores = leader.get("feature_scores")
    supporting_families = 0
    literal_context = None
    if isinstance(feature_scores, Mapping):
        supporting_families = sum(1 for value in feature_scores.values() if float_value(value) >= 0.5)
        if "literal_context_features" in feature_scores:
            literal_context = float_value(feature_scores.get("literal_context_features"))
    return {
        "top_score": round(top_score, 6),
        "score_margin": round(max(0.0, top_score - second_score), 6),
        "supporting_feature_families": supporting_families,
        "leader_literal_context": literal_context,
    }


def write_outputs(
    payload: Mapping[str, Any],
    *,
    output_json: Path,
    output_doc: Path,
) -> dict[str, Any]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    summary = payload["summary"]
    return {
        "doc": normalize_path(output_doc),
        "json": normalize_path(output_json),
        "verdict": payload["verdict"],
        "recommendation": payload["recommendation"],
        "rows_classified": summary["rows_classified"],
        "regression_rows_blocked": summary["regression_rows_blocked"],
        "phase5_report_only_suggestions": summary["phase5_report_only_suggestions"],
        "failed_gates": summary["failed_gates"],
    }


def build_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# R8 Minified Confidence Policy Diagnostics",
        "",
        "Generated by `scripts/build_r8_minified_confidence_policy_diagnostics.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        f"Recommendation: `{payload['recommendation']}`.",
        "",
        str(payload["scope"]),
        "",
        "## Summary",
        "",
        f"- Phase 4 rows evaluated: `{summary['phase4_rows_evaluated']}`",
        f"- Rows classified: `{summary['rows_classified']}`",
        f"- Controlled rows: `{summary['controlled_rows']}`",
        f"- Real rows: `{summary['real_rows']}`",
        f"- Regression-risk rows blocked: `{summary['regression_rows_blocked']}`",
        f"- Source-backed report-only suggestions: `{summary['source_backed_report_only_suggestions']}`",
        f"- Phase 5 report-only suggestions: `{summary['phase5_report_only_suggestions']}`",
        f"- Report default selection changes: `{summary['report_default_selection_changes']}`",
        f"- Production scoped-trigger imports: `{summary['phase5_production_imports']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        "",
        "## Policy Labels",
        "",
        "| Label | Rows |",
        "|---|---:|",
    ]
    for label, count in summary["policy_label_counts"].items():
        lines.append(f"| `{md(label)}` | {count} |")
    lines.extend(["", "## Confidence Labels", "", "| Label | Rows |", "|---|---:|"])
    for label, count in summary["confidence_label_counts"].items():
        lines.append(f"| `{md(label)}` | {count} |")
    lines.extend(["", "## Top Signals", "", "| Signal | Rows |", "|---|---:|"])
    for signal, count in summary["top_signals"].items():
        lines.append(f"| `{md(signal)}` | {count} |")
    lines.extend(
        [
            "",
            "## Report-Only Suggestions",
            "",
            "| Case | Coordinate | Current | Suggestion | Source | Signals |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in report_only_rows(payload):
        lines.append(
            "| "
            f"{md(row.get('case'))} | "
            f"`{md(row.get('coordinate'))}` | "
            f"{md(row.get('baseline_selected_version'))} | "
            f"{md(row.get('diagnostic_selected_version'))} | "
            f"{md(', '.join(row.get('source_versions') or []))} | "
            f"{md(', '.join(row.get('signals') or []))} |"
        )
    if not report_only_rows(payload):
        lines.append("| none |  |  |  |  |  |")
    lines.extend(
        [
            "",
            "## Blocked Regression-Risk Examples",
            "",
            "| Case | Coordinate | Current | Diagnostic | Outcome | Signals |",
            "|---|---|---:|---:|---|---|",
        ]
    )
    for row in regression_rows(payload)[:12]:
        lines.append(
            "| "
            f"{md(row.get('case'))} | "
            f"`{md(row.get('coordinate'))}` | "
            f"{md(row.get('baseline_selected_version'))} | "
            f"{md(row.get('diagnostic_selected_version'))} | "
            f"`{md(row.get('outcome'))}` | "
            f"{md(', '.join(row.get('signals') or []))} |"
        )
    if not regression_rows(payload):
        lines.append("| none |  |  |  |  |  |")
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(["", "## Gates", "", "| Gate | Status | Evidence |", "|---|---|---|"])
    for item in payload["gates"]:
        lines.append(
            "| "
            f"`{md(item['gate'])}` | "
            f"`{md(item['status'])}` | "
            f"{md(item['evidence'])} |"
        )
    lines.extend(["", "## Conclusion", "", conclusion(payload), ""])
    return "\n".join(lines)


def report_only_rows(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [
        row
        for row in payload["rows"]
        if row.get("policy_action") == "surface-report-only-suggestion"
    ]


def regression_rows(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [
        row
        for row in payload["rows"]
        if row.get("policy_label") == "block-default-change-regression-risk"
    ]


def conclusion(payload: Mapping[str, Any]) -> str:
    if payload["summary"]["failed_gates"]:
        return "Fix the diagnostic inputs before using these labels in thesis-facing evidence."
    return (
        "The safe optimization is explanatory: label minified/R8 rows with clearer "
        "confidence and ambiguity policy, keep regression-risk rows blocked, and "
        "surface the four source-backed Phase 5 improvements only as report-only "
        "suggestions. Default selected versions, SBOM output, vulnerability labels, "
        "and source-validation metrics stay unchanged."
    )


def case_label(row: Mapping[str, Any]) -> str:
    return str(row.get("case_name") or row.get("case") or row.get("slug") or "")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def float_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    raise SystemExit(main())
