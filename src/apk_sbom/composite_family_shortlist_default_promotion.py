from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from apk_sbom.composite_family_shortlist_live_validation import (
    DEFAULT_OUTPUT_JSON as DEFAULT_LIVE_VALIDATION_JSON,
)
from apk_sbom.composite_family_shortlist_opt_in_verification import (
    DEFAULT_OUTPUT_JSON as DEFAULT_OPT_IN_JSON,
)


DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/"
    "composite-family-shortlist-default-promotion-readiness.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_READINESS.md"
)
MIN_CASES_EVALUATED = 81
MIN_CONTROLLED_CASES = 62
MIN_REAL_CASES = 19
MIN_REFERENCE_ROW_REDUCTION_RATIO = 0.10


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Combine full live validation and full opt-in matcher controls into "
            "a default-promotion readiness gate for the balanced composite "
            "family shortlist."
        )
    )
    parser.add_argument("--live-validation-json", default=str(DEFAULT_LIVE_VALIDATION_JSON))
    parser.add_argument("--opt-in-json", default=str(DEFAULT_OPT_IN_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        live_validation_json=Path(args.live_validation_json),
        opt_in_json=Path(args.opt_in_json),
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
    live_validation_json: Path = DEFAULT_LIVE_VALIDATION_JSON,
    opt_in_json: Path = DEFAULT_OPT_IN_JSON,
    min_cases_evaluated: int = MIN_CASES_EVALUATED,
    min_controlled_cases: int = MIN_CONTROLLED_CASES,
    min_real_cases: int = MIN_REAL_CASES,
    min_reference_row_reduction_ratio: float = MIN_REFERENCE_ROW_REDUCTION_RATIO,
) -> dict[str, Any]:
    live_validation = read_json(live_validation_json)
    opt_in = read_json(opt_in_json)
    summary = summarize(live_validation, opt_in)
    gates = build_gates(
        live_validation,
        opt_in,
        summary,
        min_cases_evaluated=min_cases_evaluated,
        min_controlled_cases=min_controlled_cases,
        min_real_cases=min_real_cases,
        min_reference_row_reduction_ratio=min_reference_row_reduction_ratio,
    )
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    summary["failed_gates"] = len(failed_gates)
    return {
        "schema_version": 1,
        "verdict": verdict(failed_gates),
        "recommendation": recommendation(failed_gates),
        "scope": (
            "Pre-promotion evidence for changing the balanced composite family "
            "shortlist from explicit opt-in to default matcher behavior. This "
            "artifact does not change the default itself; it records whether "
            "full live validation and full default-vs-opt-in matcher controls "
            "support that next step without changing reportable selected versions, "
            "SBOM output, vulnerability labels, or source-validation metrics."
        ),
        "sources": {
            "live_validation_json": normalize_path(live_validation_json),
            "opt_in_json": normalize_path(opt_in_json),
        },
        "policy": [
            "Promotion readiness is about safe candidate pruning, not improved version counts.",
            "The shortlist may remove unrelated coordinate families but must retain full version bands for any retained family.",
            "Reportable selected versions must stay unchanged across the full case inventory.",
            "A default-promotion code change still needs a disable flag and focused plus full regression tests.",
        ],
        "summary": summary,
        "live_validation_verdict": live_validation.get("verdict"),
        "opt_in_verdict": opt_in.get("verdict"),
        "live_validation_gates": live_validation.get("gates", []),
        "opt_in_gates": opt_in.get("gates", []),
        "gates": gates,
    }


def summarize(live_validation: dict[str, Any], opt_in: dict[str, Any]) -> dict[str, Any]:
    live_summary = live_validation.get("summary", {})
    opt_in_summary = opt_in.get("summary", {})
    reference_rows_before = int(live_summary.get("reference_rows_before", 0))
    reference_rows_removed = int(live_summary.get("reference_rows_removed", 0))
    return {
        "case_set": opt_in.get("case_set"),
        "live_cases_evaluated": int(live_summary.get("cases_evaluated", 0)),
        "live_cases_requested": int(live_summary.get("cases_requested", 0)),
        "live_controlled_cases_evaluated": int(
            live_summary.get("controlled_cases_evaluated", 0)
        ),
        "live_real_cases_evaluated": int(live_summary.get("real_cases_evaluated", 0)),
        "opt_in_control_cases_evaluated": int(
            opt_in_summary.get("control_cases_evaluated", 0)
        ),
        "opt_in_requested_control_cases": int(
            opt_in_summary.get("requested_control_cases", 0)
        ),
        "opt_in_controlled_cases_evaluated": int(
            opt_in_summary.get("controlled_cases_evaluated", 0)
        ),
        "opt_in_real_cases_evaluated": int(opt_in_summary.get("real_cases_evaluated", 0)),
        "default_disabled_cases": int(opt_in_summary.get("default_disabled_cases", 0)),
        "opt_in_enabled_cases": int(opt_in_summary.get("opt_in_enabled_cases", 0)),
        "reference_rows_before": reference_rows_before,
        "reference_rows_removed": reference_rows_removed,
        "reference_rows_retained": int(live_summary.get("reference_rows_retained", 0)),
        "reference_row_reduction_ratio": float(
            live_summary.get("reference_row_reduction_ratio", 0.0)
        ),
        "opt_in_reference_rows_removed": int(opt_in_summary.get("reference_rows_removed", 0)),
        "tracked_source_family_rows": int(
            live_summary.get("tracked_source_family_rows", 0)
        ),
        "source_family_losses": int(live_summary.get("source_family_losses", 0)),
        "source_selection_regressions": int(
            live_summary.get("source_selection_regressions", 0)
        ),
        "source_selection_improvements": int(
            live_summary.get("source_selection_improvements", 0)
        ),
        "live_reportable_selected_version_changes": int(
            live_summary.get("reportable_selected_version_changes", 0)
        ),
        "opt_in_reportable_selected_version_changes": int(
            opt_in_summary.get("reportable_selected_version_changes", 0)
        ),
        "live_failed_gates": int(live_summary.get("failed_gates", 1)),
        "opt_in_failed_gates": int(opt_in_summary.get("failed_gates", 1)),
        "case_cache_hits": int(opt_in_summary.get("case_cache_hits", 0)),
        "case_cache_misses": int(opt_in_summary.get("case_cache_misses", 0)),
    }


def build_gates(
    live_validation: dict[str, Any],
    opt_in: dict[str, Any],
    summary: dict[str, Any],
    *,
    min_cases_evaluated: int,
    min_controlled_cases: int,
    min_real_cases: int,
    min_reference_row_reduction_ratio: float,
) -> list[dict[str, Any]]:
    return [
        gate(
            "live-validation-clean",
            fail_count=0
            if live_validation.get("verdict")
            == "composite-family-shortlist-live-validation-clean-opt-in-candidate"
            and summary["live_failed_gates"] == 0
            else 1,
            evidence=(
                f"Live validation verdict: {live_validation.get('verdict')}; "
                f"{summary['live_failed_gates']} failed gates."
            ),
        ),
        gate(
            "full-live-inventory-covered",
            fail_count=coverage_fail_count(
                summary["live_cases_evaluated"],
                summary["live_cases_requested"],
                min_cases_evaluated,
            ),
            evidence=(
                f"{summary['live_cases_evaluated']}/{summary['live_cases_requested']} "
                "live-validation cases evaluated."
            ),
        ),
        gate(
            "full-opt-in-control-inventory-covered",
            fail_count=coverage_fail_count(
                summary["opt_in_control_cases_evaluated"],
                summary["opt_in_requested_control_cases"],
                min_cases_evaluated,
            ),
            evidence=(
                f"{summary['opt_in_control_cases_evaluated']}/"
                f"{summary['opt_in_requested_control_cases']} opt-in control cases evaluated."
            ),
        ),
        gate(
            "controlled-and-real-coverage",
            fail_count=controlled_real_fail_count(
                summary,
                min_controlled_cases=min_controlled_cases,
                min_real_cases=min_real_cases,
            ),
            evidence=(
                f"Live coverage: {summary['live_controlled_cases_evaluated']} controlled "
                f"and {summary['live_real_cases_evaluated']} real; opt-in coverage: "
                f"{summary['opt_in_controlled_cases_evaluated']} controlled and "
                f"{summary['opt_in_real_cases_evaluated']} real."
            ),
        ),
        gate(
            "all-case-opt-in-control-clean",
            fail_count=0
            if opt_in.get("verdict")
            == "composite-family-shortlist-opt-in-matcher-experiment-ready"
            and summary["case_set"] == "all"
            and summary["opt_in_failed_gates"] == 0
            else 1,
            evidence=(
                f"Opt-in verdict: {opt_in.get('verdict')}; case_set="
                f"{summary['case_set']}; {summary['opt_in_failed_gates']} failed gates."
            ),
        ),
        gate(
            "default-path-still-disabled",
            fail_count=summary["opt_in_control_cases_evaluated"]
            - summary["default_disabled_cases"],
            evidence=(
                f"{summary['default_disabled_cases']} default cases kept the "
                "shortlist disabled."
            ),
        ),
        gate(
            "opt-in-path-wired",
            fail_count=summary["opt_in_control_cases_evaluated"]
            - summary["opt_in_enabled_cases"],
            evidence=(
                f"{summary['opt_in_enabled_cases']} opt-in cases enabled the shortlist."
            ),
        ),
        gate(
            "meaningful-reference-row-pruning",
            fail_count=0
            if summary["reference_row_reduction_ratio"]
            >= min_reference_row_reduction_ratio
            and summary["reference_rows_removed"] == summary["opt_in_reference_rows_removed"]
            else 1,
            evidence=(
                f"{summary['reference_rows_removed']}/{summary['reference_rows_before']} "
                "live reference rows removed "
                f"({summary['reference_row_reduction_ratio']:.4f}); "
                f"{summary['opt_in_reference_rows_removed']} rows removed in matcher controls."
            ),
        ),
        gate(
            "tracked-source-families-preserved",
            fail_count=summary["source_family_losses"],
            evidence=(
                f"{summary['source_family_losses']} tracked source-family losses "
                f"across {summary['tracked_source_family_rows']} tracked rows."
            ),
        ),
        gate(
            "tracked-source-selection-nonregressive",
            fail_count=summary["source_selection_regressions"],
            evidence=(
                f"{summary['source_selection_regressions']} tracked source-selection "
                f"regressions; {summary['source_selection_improvements']} improvements."
            ),
        ),
        gate(
            "no-reportable-selected-version-drift",
            fail_count=summary["live_reportable_selected_version_changes"]
            + summary["opt_in_reportable_selected_version_changes"],
            evidence=(
                f"{summary['live_reportable_selected_version_changes']} live and "
                f"{summary['opt_in_reportable_selected_version_changes']} matcher "
                "reportable selected-version changes."
            ),
        ),
    ]


def coverage_fail_count(evaluated: int, requested: int, minimum: int) -> int:
    failures = 0
    if evaluated < requested:
        failures += requested - evaluated
    if evaluated < minimum:
        failures += minimum - evaluated
    return failures


def controlled_real_fail_count(
    summary: dict[str, Any],
    *,
    min_controlled_cases: int,
    min_real_cases: int,
) -> int:
    failures = 0
    if summary["live_controlled_cases_evaluated"] < min_controlled_cases:
        failures += 1
    if summary["live_real_cases_evaluated"] < min_real_cases:
        failures += 1
    if summary["opt_in_controlled_cases_evaluated"] < min_controlled_cases:
        failures += 1
    if summary["opt_in_real_cases_evaluated"] < min_real_cases:
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
        return "composite-family-shortlist-default-promotion-not-ready"
    return "composite-family-shortlist-default-promotion-ready"


def recommendation(failed_gates: list[dict[str, Any]]) -> str:
    if failed_gates:
        return "keep-opt-in-and-fix-readiness-gates"
    return "safe-to-attempt-default-promotion-with-disable-flag-and-regression-tests"


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
        "# Composite Family-Shortlist Default-Promotion Readiness",
        "",
        "Generated by `scripts/build_composite_family_shortlist_default_promotion_readiness.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        f"Recommendation: `{payload['recommendation']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Case set: `{summary['case_set']}`",
        f"- Live validation cases: `{summary['live_cases_evaluated']}/{summary['live_cases_requested']}`",
        f"- Opt-in control cases: `{summary['opt_in_control_cases_evaluated']}/{summary['opt_in_requested_control_cases']}`",
        f"- Controlled / real coverage: `{summary['live_controlled_cases_evaluated']}` / `{summary['live_real_cases_evaluated']}` live, "
        f"`{summary['opt_in_controlled_cases_evaluated']}` / `{summary['opt_in_real_cases_evaluated']}` opt-in",
        f"- Default disabled cases: `{summary['default_disabled_cases']}`",
        f"- Opt-in enabled cases: `{summary['opt_in_enabled_cases']}`",
        f"- Reference rows removed: `{summary['reference_rows_removed']}/{summary['reference_rows_before']}` "
        f"(`{summary['reference_row_reduction_ratio']:.4f}`)",
        f"- Tracked source-family rows: `{summary['tracked_source_family_rows']}`",
        f"- Source-family losses: `{summary['source_family_losses']}`",
        f"- Source-selection regressions: `{summary['source_selection_regressions']}`",
        f"- Live / matcher reportable selected-version changes: "
        f"`{summary['live_reportable_selected_version_changes']}` / "
        f"`{summary['opt_in_reportable_selected_version_changes']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        "",
        "## Guardrails",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Verdict Chain",
            "",
            "| Artifact | Verdict |",
            "|---|---|",
            f"| Live validation | `{md(payload['live_validation_verdict'])}` |",
            f"| Opt-in matcher control | `{md(payload['opt_in_verdict'])}` |",
            "",
            "## Gates",
            "",
            "| Gate | Status | Evidence |",
            "|---|---|---|",
        ]
    )
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
        return (
            "Keep the composite family shortlist behind the explicit opt-in flag "
            "until the failed readiness gates are fixed and rerun."
        )
    return (
        "The balanced composite family shortlist is ready for an explicit "
        "default-promotion attempt: full live validation and full matcher "
        "controls are clean, the default path is still unchanged, opt-in pruning "
        "removes reference rows, and no reportable selected versions drift. If "
        "promoted, keep a disable flag for pre-promotion baseline reproduction "
        "and run focused plus full regression tests after the code change."
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
