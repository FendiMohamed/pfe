from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_PHASE4_JSON = Path("data/results/experiments/r8-phase4-scoped-experiment-diagnostics.json")
DEFAULT_PHASE5_VALIDATION_JSON = Path(
    "data/results/experiments/r8-phase5-trigger-control-validation.json"
)
DEFAULT_PHASE5_REPORT_JSON = Path(
    "data/results/experiments/r8-phase5-report-evidence/summary.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/r8-optimization-aware-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_OPTIMIZATION_AWARE_DIAGNOSTICS.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a limited optimization-aware R8/minified diagnostic without "
            "changing default matcher, report, SBOM, or vulnerability behavior."
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
    summary = build_summary(phase4, phase5_validation, phase5_report)
    gates = build_gates(summary, phase5_validation, phase5_report)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    summary["failed_gates"] = len(failed_gates)
    policy_decisions = build_policy_decisions(summary)
    return {
        "schema_version": 1,
        "verdict": verdict(summary, failed_gates),
        "recommendation": recommendation(summary, failed_gates),
        "scope": (
            "Limited optimization-aware diagnostic only. This artifact combines "
            "the expanded R8 Phase 4 diagnostic, Phase 5 scoped trigger control "
            "validation, and Phase 5 report-only evidence to decide whether any "
            "R8/minified optimization-aware default behavior is justified. It "
            "does not change matcher scoring, selected versions, SBOM output, "
            "vulnerability labels, or source-validation metrics."
        ),
        "sources": {
            "phase4_json": normalize_path(phase4_json),
            "phase5_validation_json": normalize_path(phase5_validation_json),
            "phase5_report_json": normalize_path(phase5_report_json),
        },
        "policy": [
            "Global multi-scale scoring remains rejected when controlled or real source-validated regression blockers exist.",
            "A scoped R8 trigger can remain experiment-only only if controls pass and default report/SBOM selections do not change.",
            "Brittle name/package/class/method signals should affect confidence and explanation first, not selected versions.",
            "Any future optimization-aware default change must rerun controlled R8, clean real, partial real, and boundary controls.",
        ],
        "summary": summary,
        "policy_decisions": policy_decisions,
        "risk_patterns": build_risk_patterns(phase4, phase5_validation),
        "target_suggestions": phase5_validation.get("triggered_rows", []),
        "report_only_rows": phase5_report.get("rows", []),
        "gates": gates,
    }


def build_summary(
    phase4: dict[str, Any],
    phase5_validation: dict[str, Any],
    phase5_report: dict[str, Any],
) -> dict[str, Any]:
    phase4_summary = phase4.get("summary", {})
    candidate_scan = phase4_summary.get("phase5_candidate_scan", {})
    validation_summary = phase5_validation.get("summary", {})
    report_summary = phase5_report.get("summary", {})
    controlled_regressions = int(candidate_scan.get("controlled_regression_count") or 0)
    real_regressions = int(candidate_scan.get("real_regression_count") or 0)
    clean_real_regressions = int(candidate_scan.get("clean_real_regression_count") or 0)
    target_improvements = len(candidate_scan.get("candidate_improvements", []))
    regression_blockers = controlled_regressions + real_regressions
    return {
        "phase4_verdict": phase4.get("verdict"),
        "phase4_rows_evaluated": int(phase4_summary.get("controlled_cases") or 0)
        + int(phase4_summary.get("real_component_rows") or 0),
        "phase4_controlled_regression_blockers": controlled_regressions,
        "phase4_real_regression_blockers": real_regressions,
        "phase4_clean_real_regression_blockers": clean_real_regressions,
        "phase4_total_regression_blockers": regression_blockers,
        "phase4_target_improvements": target_improvements,
        "phase5_validation_verdict": phase5_validation.get("verdict"),
        "phase5_rows_evaluated": int(validation_summary.get("rows_evaluated") or 0),
        "phase5_triggered_rows": int(validation_summary.get("triggered_rows") or 0),
        "phase5_target_improvements_kept": int(
            validation_summary.get("target_improvements_kept") or 0
        ),
        "phase5_triggered_regressions": int(validation_summary.get("triggered_regressions") or 0),
        "phase5_triggered_conflicts": int(validation_summary.get("triggered_conflicts") or 0),
        "phase5_failed_gates": int(validation_summary.get("failed_gates") or 0),
        "phase5_production_imports": len(phase5_validation.get("production_imports", [])),
        "report_evidence_verdict": phase5_report.get("verdict"),
        "report_evidence_reports": int(report_summary.get("reports") or 0),
        "report_evidence_suggestions": int(report_summary.get("phase5_suggestions") or 0),
        "report_only_suggestions": int(report_summary.get("report_only_suggestions") or 0),
        "report_default_selection_changes": int(
            report_summary.get("default_selection_changes") or 0
        ),
    }


def build_policy_decisions(summary: dict[str, Any]) -> list[dict[str, Any]]:
    global_scoring_safe = summary["phase4_total_regression_blockers"] == 0
    phase5_report_safe = (
        summary["phase5_failed_gates"] == 0
        and summary["phase5_triggered_regressions"] == 0
        and summary["phase5_triggered_conflicts"] == 0
        and summary["report_default_selection_changes"] == 0
    )
    return [
        {
            "decision": "global-multiscale-default-scoring",
            "status": "rejected" if not global_scoring_safe else "needs-fresh-controls",
            "evidence": (
                f"{summary['phase4_controlled_regression_blockers']} controlled and "
                f"{summary['phase4_real_regression_blockers']} real regression blockers."
            ),
        },
        {
            "decision": "scoped-r8-trigger-default-promotion",
            "status": "deferred",
            "evidence": (
                f"{summary['phase5_target_improvements_kept']} target improvements kept "
                f"with {summary['phase5_triggered_regressions']} triggered regressions, "
                "but the current surface is validated only as experiment/report-only."
            ),
        },
        {
            "decision": "report-only-phase5-suggestions",
            "status": "allowed" if phase5_report_safe else "blocked",
            "evidence": (
                f"{summary['report_evidence_suggestions']} suggestions, "
                f"{summary['report_default_selection_changes']} default selection changes."
            ),
        },
        {
            "decision": "confidence-and-ambiguity-policy",
            "status": "next-diagnostic",
            "evidence": (
                "Use shrink/inlining and brittle-signal indicators to explain uncertainty "
                "before changing selected versions."
            ),
        },
    ]


def build_risk_patterns(
    phase4: dict[str, Any],
    phase5_validation: dict[str, Any],
) -> dict[str, Any]:
    category_counts = phase4.get("summary", {}).get("category_counts", [])
    risky_categories = []
    for row in category_counts:
        outcomes = row.get("outcomes", {})
        regressions = int(outcomes.get("regression-risk-do-not-promote") or 0)
        if regressions:
            risky_categories.append(
                {
                    "category": row.get("category"),
                    "regression_risks": regressions,
                    "outcomes": outcomes,
                }
            )
    blocked_reasons = phase5_validation.get("summary", {}).get("triggered_outcomes", {})
    phase5_source = read_phase5_block_reasons(phase5_validation)
    top_blockers = (
        phase4.get("summary", {})
        .get("phase5_candidate_scan", {})
        .get("top_blocking_coordinates", [])
    )
    return {
        "risky_controlled_categories": risky_categories,
        "top_blocking_coordinates": top_blockers,
        "triggered_outcomes": blocked_reasons,
        "blocked_reason_counts": phase5_source,
    }


def read_phase5_block_reasons(phase5_validation: dict[str, Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in phase5_validation.get("triggered_rows", []):
        for reason in row.get("trigger_decision", {}).get("blocked_by", []):
            counts[str(reason)] += 1
    if counts:
        return dict(sorted(counts.items()))
    # The validation artifact stores only triggered rows; use gate evidence as the stable public summary.
    return {}


def build_gates(
    summary: dict[str, Any],
    phase5_validation: dict[str, Any],
    phase5_report: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        gate(
            "phase4-global-scoring-blockers-visible",
            fail_count=0 if summary["phase4_total_regression_blockers"] > 0 else 1,
            evidence=(
                f"{summary['phase4_total_regression_blockers']} Phase 4 regression "
                "blockers keep global scoring diagnostic-only."
            ),
        ),
        gate(
            "phase5-current-controls-clean",
            fail_count=0
            if phase5_validation.get("verdict")
            == "phase5-trigger-current-control-clean-experiment-only"
            and summary["phase5_failed_gates"] == 0
            and summary["phase5_triggered_regressions"] == 0
            and summary["phase5_triggered_conflicts"] == 0
            else 1,
            evidence=(
                f"Phase 5 verdict={phase5_validation.get('verdict')}; "
                f"{summary['phase5_failed_gates']} failed gates."
            ),
        ),
        gate(
            "phase5-report-boundary-clean",
            fail_count=0
            if phase5_report.get("verdict") == "phase5-report-evidence-clean-experiment-only"
            and summary["report_default_selection_changes"] == 0
            else 1,
            evidence=(
                f"Report evidence verdict={phase5_report.get('verdict')}; "
                f"{summary['report_default_selection_changes']} default selection changes."
            ),
        ),
        gate(
            "production-default-not-wired",
            fail_count=summary["phase5_production_imports"],
            evidence=f"{summary['phase5_production_imports']} production imports of the scoped R8 trigger.",
        ),
        gate(
            "target-improvements-remain-experiment-only",
            fail_count=0 if summary["phase5_target_improvements_kept"] >= 4 else 1,
            evidence=(
                f"{summary['phase5_target_improvements_kept']} Phase 5 target improvements "
                "remain available as experiment-only evidence."
            ),
        ),
    ]


def verdict(summary: dict[str, Any], failed_gates: list[dict[str, Any]]) -> str:
    if failed_gates:
        return "r8-optimization-aware-diagnostic-incomplete"
    if summary["phase4_total_regression_blockers"] > 0:
        return "r8-optimization-aware-keep-report-only"
    return "r8-optimization-aware-candidate-needs-fresh-controls"


def recommendation(summary: dict[str, Any], failed_gates: list[dict[str, Any]]) -> str:
    if failed_gates:
        return "fix-r8-diagnostic-inputs-before-policy-change"
    if summary["phase4_total_regression_blockers"] > 0:
        return "keep-optimization-aware-logic-diagnostic-only-and-improve-confidence-policy"
    return "run-fresh-optimization-aware-default-promotion-controls"


def gate(gate_id: str, *, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


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
        "recommendation": payload["recommendation"],
        **payload["summary"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# R8 Optimization-Aware Diagnostics",
        "",
        "Generated by `scripts/build_r8_optimization_aware_diagnostics.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        f"Recommendation: `{payload['recommendation']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Phase 4 rows evaluated: `{summary['phase4_rows_evaluated']}`",
        f"- Phase 4 target improvements: `{summary['phase4_target_improvements']}`",
        f"- Controlled regression blockers: `{summary['phase4_controlled_regression_blockers']}`",
        f"- Real regression blockers: `{summary['phase4_real_regression_blockers']}`",
        f"- Clean-real regression blockers: `{summary['phase4_clean_real_regression_blockers']}`",
        f"- Phase 5 rows evaluated: `{summary['phase5_rows_evaluated']}`",
        f"- Phase 5 target improvements kept: `{summary['phase5_target_improvements_kept']}`",
        f"- Phase 5 triggered regressions/conflicts: `{summary['phase5_triggered_regressions']}` / `{summary['phase5_triggered_conflicts']}`",
        f"- Report-only suggestions: `{summary['report_only_suggestions']}`",
        f"- Report default selection changes: `{summary['report_default_selection_changes']}`",
        f"- Production scoped-trigger imports: `{summary['phase5_production_imports']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        "",
        "## Policy Decisions",
        "",
        "| Decision | Status | Evidence |",
        "|---|---|---|",
    ]
    for item in payload["policy_decisions"]:
        lines.append(
            "| "
            f"`{md(item['decision'])}` | "
            f"`{md(item['status'])}` | "
            f"{md(item['evidence'])} |"
        )
    lines.extend(
        [
            "",
            "## Risk Patterns",
            "",
            "### Controlled Categories With Regression Risk",
            "",
            "| Category | Regression risks | Outcomes |",
            "|---|---:|---|",
        ]
    )
    for item in payload["risk_patterns"]["risky_controlled_categories"]:
        outcomes = ", ".join(f"{key}={value}" for key, value in item["outcomes"].items())
        lines.append(
            "| "
            f"`{md(item['category'])}` | "
            f"{item['regression_risks']} | "
            f"{md(outcomes)} |"
        )
    if not payload["risk_patterns"]["risky_controlled_categories"]:
        lines.append("| none | 0 |  |")
    lines.extend(
        [
            "",
            "### Top Blocking Coordinates",
            "",
            "| Coordinate | Regressions |",
            "|---|---:|",
        ]
    )
    for item in payload["risk_patterns"]["top_blocking_coordinates"][:12]:
        lines.append(f"| `{md(item.get('coordinate'))}` | {item.get('regressions', 0)} |")
    if not payload["risk_patterns"]["top_blocking_coordinates"]:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Experiment-Only Target Suggestions",
            "",
            "| Case | Coordinate | Baseline | Suggestion | Source |",
            "|---|---|---:|---:|---|",
        ]
    )
    for row in payload["target_suggestions"]:
        source_versions = row.get("source_versions")
        if isinstance(source_versions, list):
            source_text = ", ".join(str(item) for item in source_versions)
        else:
            source_text = str(source_versions or "")
        lines.append(
            "| "
            f"{md(row.get('case'))} | "
            f"`{md(row.get('coordinate'))}` | "
            f"{md(row.get('baseline_selected_version'))} | "
            f"{md(row.get('diagnostic_selected_version'))} | "
            f"{md(source_text)} |"
        )
    if not payload["target_suggestions"]:
        lines.append("| none |  |  |  |  |")
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


def conclusion(payload: dict[str, Any]) -> str:
    if payload["summary"]["failed_gates"]:
        return "Fix the diagnostic inputs before making an optimization-aware policy decision."
    return (
        "Keep optimization-aware R8/minified logic diagnostic/report-only for now. "
        "Phase 5 keeps four useful target suggestions with clean experiment-only "
        "controls, but the broader Phase 4 multi-scale signal still has controlled "
        "and real regression blockers. The next safe work is confidence and "
        "ambiguity policy for minified rows, not a default selected-version change."
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
