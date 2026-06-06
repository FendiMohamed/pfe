from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_DIAGNOSTIC_JSON = Path(
    "data/results/experiments/version-unique-literal-context-diagnostics.json"
)
DEFAULT_PROMOTION_JSON = Path(
    "data/results/experiments/version-unique-literal-context-promotion-candidate.json"
)
DEFAULT_CONTROL_VALIDATION_JSON = Path(
    "data/results/experiments/"
    "version-unique-literal-context-current-control-validation.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/"
    "version-unique-literal-context-default-promotion-readiness.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/"
    "VERSION_UNIQUE_LITERAL_CONTEXT_DEFAULT_PROMOTION_READINESS.md"
)
MIN_BROAD_CONTROLLED_ROWS = 24
MIN_BROAD_REAL_ROWS = 224


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Combine broad diagnostics and report/source-validation controls into "
            "a default-promotion readiness gate for the version-unique "
            "literal/context reranker."
        )
    )
    parser.add_argument("--diagnostic-json", default=str(DEFAULT_DIAGNOSTIC_JSON))
    parser.add_argument("--promotion-json", default=str(DEFAULT_PROMOTION_JSON))
    parser.add_argument(
        "--control-validation-json",
        default=str(DEFAULT_CONTROL_VALIDATION_JSON),
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        diagnostic_json=Path(args.diagnostic_json),
        promotion_json=Path(args.promotion_json),
        control_validation_json=Path(args.control_validation_json),
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
    diagnostic_json: Path = DEFAULT_DIAGNOSTIC_JSON,
    promotion_json: Path = DEFAULT_PROMOTION_JSON,
    control_validation_json: Path = DEFAULT_CONTROL_VALIDATION_JSON,
    min_controlled_rows: int = MIN_BROAD_CONTROLLED_ROWS,
    min_real_rows: int = MIN_BROAD_REAL_ROWS,
) -> dict[str, Any]:
    diagnostic = read_json(diagnostic_json)
    promotion = read_json(promotion_json)
    control_validation = read_json(control_validation_json)
    gates = build_gates(
        diagnostic,
        promotion,
        control_validation,
        min_controlled_rows=min_controlled_rows,
        min_real_rows=min_real_rows,
    )
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    diagnostic_summary = diagnostic.get("summary", {})
    promotion_summary = promotion.get("summary", {})
    control_summary = control_validation.get("summary", {})
    summary = {
        "broad_rows_inspected": int(diagnostic_summary.get("rows_inspected", 0)),
        "broad_controlled_rows": int(
            diagnostic_summary.get("controlled_rows_inspected", 0)
        ),
        "broad_real_source_validated_rows": int(
            diagnostic_summary.get("real_source_validated_rows_inspected", 0)
        ),
        "broad_one_match_suggestions": int(
            diagnostic_summary.get("version_unique_literal_context_suggestions", 0)
        ),
        "broad_regression_risks": int(diagnostic_summary.get("regression_risks", 0)),
        "minimum_kept_unique_literal_context_matches": int(
            promotion_summary.get("minimum_unique_literal_context_matches", 0)
        ),
        "kept_replacement_suggestions": int(
            promotion_summary.get("kept_replacement_suggestions", 0)
        ),
        "filtered_low_support_suggestions": int(
            promotion_summary.get("filtered_low_support_suggestions", 0)
        ),
        "kept_potential_target_improvements": int(
            promotion_summary.get("potential_target_improvements", 0)
        ),
        "kept_regression_risks": int(promotion_summary.get("regression_risks", 0)),
        "report_validation_cases": int(control_summary.get("cases_evaluated", 0)),
        "report_validation_changed_rows": int(control_summary.get("changed_rows", 0)),
        "report_validation_confirmed_delta": int(
            control_summary.get("confirmed_delta", 0)
        ),
        "report_validation_mismatch_delta": int(
            control_summary.get("version_mismatch_delta", 0)
        ),
        "report_validation_missing_delta": int(control_summary.get("missing_delta", 0)),
        "failed_gates": len(failed_gates),
    }
    return {
        "schema_version": 1,
        "verdict": verdict(failed_gates),
        "recommendation": recommendation(failed_gates),
        "scope": (
            "Pre-promotion evidence for changing the guarded version-unique "
            "literal/context reranker from explicit opt-in to default behavior. "
            "This artifact does not change the default itself; it records whether "
            "the broad diagnostic matrix and real report/source-validation slice "
            "support that next step."
        ),
        "sources": {
            "diagnostic_json": normalize_path(diagnostic_json),
            "promotion_json": normalize_path(promotion_json),
            "control_validation_json": normalize_path(control_validation_json),
        },
        "summary": summary,
        "diagnostic_verdict": diagnostic.get("verdict"),
        "promotion_verdict": promotion.get("verdict"),
        "control_validation_verdict": control_validation.get("verdict"),
        "kept_rows": promotion.get("kept_rows", []),
        "filtered_rows": promotion.get("filtered_rows", []),
        "report_validation_changed_rows": control_validation.get("changed_rows", []),
        "gates": gates,
    }


def build_gates(
    diagnostic: dict[str, Any],
    promotion: dict[str, Any],
    control_validation: dict[str, Any],
    *,
    min_controlled_rows: int,
    min_real_rows: int,
) -> list[dict[str, Any]]:
    diagnostic_summary = diagnostic.get("summary", {})
    promotion_summary = promotion.get("summary", {})
    control_summary = control_validation.get("summary", {})
    kept_rows = rows(promotion, "kept_rows")
    filtered_rows = rows(promotion, "filtered_rows")
    kept_non_improvements = [
        row
        for row in kept_rows
        if decision(row).get("classification")
        != "potential-target-improvement-needs-control-matrix"
    ]
    controlled_kept = [
        row for row in kept_rows if str(row.get("row_type")) == "controlled"
    ]
    low_support_regressions = [
        row
        for row in filtered_rows
        if decision(row).get("classification") == "regression-risk-do-not-promote"
    ]
    one_match_kept = [
        row
        for row in kept_rows
        if int(decision(row).get("suggested_unique_literal_context_matches") or 0)
        < int(promotion_summary.get("minimum_unique_literal_context_matches") or 0)
    ]
    return [
        gate(
            "broad-diagnostic-coverage",
            fail_count=coverage_fail_count(
                diagnostic_summary,
                min_controlled_rows=min_controlled_rows,
                min_real_rows=min_real_rows,
            ),
            evidence=(
                f"{diagnostic_summary.get('controlled_rows_inspected', 0)} controlled "
                f"and {diagnostic_summary.get('real_source_validated_rows_inspected', 0)} "
                "real source-validated rows inspected."
            ),
        ),
        gate(
            "broad-one-match-signal-rejected",
            fail_count=0
            if int(diagnostic_summary.get("regression_risks", 0)) > 0
            and str(diagnostic.get("verdict", "")).endswith("regression-risk")
            else 1,
            evidence=(
                f"{diagnostic_summary.get('version_unique_literal_context_suggestions', 0)} "
                "one-match-or-better suggestions produced "
                f"{diagnostic_summary.get('regression_risks', 0)} regression risks."
            ),
        ),
        gate(
            "minimum-support-gate-clean",
            fail_count=0
            if int(promotion_summary.get("regression_risks", 0)) == 0
            and int(promotion_summary.get("potential_target_improvements", 0)) >= 1
            else 1,
            evidence=(
                f"{promotion_summary.get('kept_replacement_suggestions', 0)} kept, "
                f"{promotion_summary.get('filtered_low_support_suggestions', 0)} filtered, "
                f"{promotion_summary.get('regression_risks', 0)} kept regression risks."
            ),
        ),
        gate(
            "low-support-regressions-filtered",
            fail_count=0 if low_support_regressions else 1,
            evidence=f"{len(low_support_regressions)} filtered rows are regression risks.",
        ),
        gate(
            "no-controlled-kept-replacements",
            fail_count=len(controlled_kept),
            evidence=f"{len(controlled_kept)} controlled rows kept for replacement.",
        ),
        gate(
            "only-target-improvements-kept",
            fail_count=len(kept_non_improvements) + len(one_match_kept),
            evidence=(
                f"{len(kept_non_improvements)} kept rows are not target improvements; "
                f"{len(one_match_kept)} kept rows are below the minimum support threshold."
            ),
        ),
        gate(
            "report-source-validation-slice-clean",
            fail_count=0
            if control_validation.get("verdict")
            == "version-unique-literal-context-current-control-opt-in-pass"
            and int(control_summary.get("failed_gates", 1)) == 0
            else 1,
            evidence=(
                f"{control_summary.get('cases_evaluated', 0)} report/source-validation "
                f"cases, {control_summary.get('failed_gates', 0)} failed gates."
            ),
        ),
        gate(
            "report-source-validation-counts-nonregressive",
            fail_count=0
            if int(control_summary.get("confirmed_delta", 0)) >= 0
            and int(control_summary.get("version_mismatch_delta", 0)) <= 0
            and int(control_summary.get("missing_delta", 0)) <= 0
            else 1,
            evidence=(
                f"confirmed delta={control_summary.get('confirmed_delta', 0)}, "
                f"mismatch delta={control_summary.get('version_mismatch_delta', 0)}, "
                f"missing delta={control_summary.get('missing_delta', 0)}."
            ),
        ),
    ]


def coverage_fail_count(
    summary: dict[str, Any],
    *,
    min_controlled_rows: int,
    min_real_rows: int,
) -> int:
    failures = 0
    if int(summary.get("controlled_rows_inspected", 0)) < min_controlled_rows:
        failures += 1
    if int(summary.get("real_source_validated_rows_inspected", 0)) < min_real_rows:
        failures += 1
    return failures


def gate(gate_id: str, *, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


def verdict(failed_gates: list[dict[str, Any]]) -> str:
    if failed_gates:
        return "version-unique-literal-context-default-promotion-not-ready"
    return "version-unique-literal-context-default-promotion-ready"


def recommendation(failed_gates: list[dict[str, Any]]) -> str:
    if failed_gates:
        return "keep-opt-in-and-tighten-gates"
    return "safe-to-attempt-default-promotion-with-regression-tests"


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
        "# Version-Unique Literal-Context Default-Promotion Readiness",
        "",
        "Generated by `scripts/build_version_unique_literal_context_default_promotion_readiness.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        f"Recommendation: `{payload['recommendation']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Broad diagnostic rows inspected: `{summary['broad_rows_inspected']}` "
        f"(`{summary['broad_controlled_rows']}` controlled, "
        f"`{summary['broad_real_source_validated_rows']}` real source-validated)",
        f"- Broad one-match-or-better suggestions: `{summary['broad_one_match_suggestions']}`",
        f"- Broad regression risks before the stricter gate: `{summary['broad_regression_risks']}`",
        f"- Minimum matched unique literal/context features kept: "
        f"`{summary['minimum_kept_unique_literal_context_matches']}`",
        f"- Kept replacement suggestions: `{summary['kept_replacement_suggestions']}`",
        f"- Filtered low-support suggestions: `{summary['filtered_low_support_suggestions']}`",
        f"- Kept target improvements: `{summary['kept_potential_target_improvements']}`",
        f"- Kept regression risks: `{summary['kept_regression_risks']}`",
        f"- Report/source-validation cases: `{summary['report_validation_cases']}`",
        f"- Report/source-validation changed rows: `{summary['report_validation_changed_rows']}`",
        f"- Report/source-validation confirmed delta: `{summary['report_validation_confirmed_delta']}`",
        f"- Report/source-validation mismatch delta: `{summary['report_validation_mismatch_delta']}`",
        f"- Report/source-validation missing delta: `{summary['report_validation_missing_delta']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        "",
        "## Verdict Chain",
        "",
        "| Artifact | Verdict |",
        "|---|---|",
        f"| Broad diagnostic | `{md(payload['diagnostic_verdict'])}` |",
        f"| Promotion candidate | `{md(payload['promotion_verdict'])}` |",
        f"| Report/source-validation slice | `{md(payload['control_validation_verdict'])}` |",
        "",
        "## Kept Rows",
        "",
        "| Case | Coordinate | Current | Suggested | Source | Matches | Classification |",
        "|---|---|---:|---:|---|---:|---|",
    ]
    for row in payload["kept_rows"]:
        item = decision(row)
        lines.append(
            "| "
            f"{md(row.get('case_id'))} | "
            f"`{md(row.get('coordinate'))}` | "
            f"{md(row.get('baseline_selected_version'))} | "
            f"{md(item.get('suggested_version'))} | "
            f"{md(', '.join(row.get('source_versions') or []))} | "
            f"{md(item.get('suggested_unique_literal_context_matches'))} | "
            f"`{md(item.get('classification'))}` |"
        )
    if not payload["kept_rows"]:
        lines.append("| none |  |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Filtered Low-Support Rows",
            "",
            "| Case | Coordinate | Current | Suggested | Source | Matches | Classification |",
            "|---|---|---:|---:|---|---:|---|",
        ]
    )
    for row in payload["filtered_rows"]:
        item = decision(row)
        lines.append(
            "| "
            f"{md(row.get('case_id'))} | "
            f"`{md(row.get('coordinate'))}` | "
            f"{md(row.get('baseline_selected_version'))} | "
            f"{md(item.get('suggested_version'))} | "
            f"{md(', '.join(row.get('source_versions') or []))} | "
            f"{md(item.get('suggested_unique_literal_context_matches'))} | "
            f"`{md(item.get('classification'))}` |"
        )
    if not payload["filtered_rows"]:
        lines.append("| none |  |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Report Validation Changed Rows",
            "",
            "| App | Coordinate | Baseline | Opt-in | Source versions |",
            "|---|---|---|---|---|",
        ]
    )
    for change in payload["report_validation_changed_rows"]:
        lines.append(
            "| "
            f"`{md(change.get('app_id'))}` | "
            f"`{md(change.get('coordinate'))}` | "
            f"{md(change.get('baseline_version'))} / `{md(change.get('baseline_status'))}` | "
            f"{md(change.get('opt_in_version'))} / `{md(change.get('opt_in_status'))}` | "
            f"{md(', '.join(change.get('source_versions') or []))} |"
        )
    if not payload["report_validation_changed_rows"]:
        lines.append("| none |  |  |  |  |")

    lines.extend(["", "## Gates", "", "| Gate | Status | Evidence |", "|---|---|---|"])
    for item in payload["gates"]:
        lines.append(
            "| "
            f"`{md(item['gate'])}` | "
            f"`{md(item['status'])}` | "
            f"{md(item['evidence'])} |"
        )

    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "The stricter version-unique literal/context gate is ready for an "
            "explicit default-promotion attempt: the broad diagnostic matrix "
            "filters the one-match regressions, and the real report/source-validation "
            "slice improves only the VLC RecyclerView row. If promoted, keep a "
            "disable flag for pre-promotion baseline reproduction and run focused "
            "plus full regression tests after the code change.",
            "",
        ]
    )
    return "\n".join(lines)


def rows(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key, [])
    return [row for row in value if isinstance(row, dict)]


def decision(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("version_unique_literal_context_decision")
    return value if isinstance(value, dict) else {}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
