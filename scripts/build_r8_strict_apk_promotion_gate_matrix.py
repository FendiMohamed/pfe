from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.r8_apk_structural_promotion_gate import (  # noqa: E402
    DEFAULT_AI_SUGGESTIONS_JSON,
    DEFAULT_LARGE_ANALYSIS_JSON,
    DEFAULT_ROUTER_JSON,
    build_payload,
)


DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/r8-strict-apk-promotion-gate-matrix.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_STRICT_APK_PROMOTION_GATE_MATRIX.md")


STRICT_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "name": "baseline-apk-only-gate",
        "min_opcode_score": 0.90,
        "min_literal_score": 0.50,
        "min_dependency_score": 0.30,
        "max_name_score": 0.30,
        "min_identity_confidence": 0.0,
        "min_exact_controls": 1,
        "min_control_cases": 1,
        "max_control_risk_rows": 0,
        "require_posthoc_source_exact": True,
    },
    {
        "name": "high-confidence-apk-only",
        "min_opcode_score": 0.94,
        "min_literal_score": 0.60,
        "min_dependency_score": 0.45,
        "max_name_score": 0.25,
        "min_identity_confidence": 0.35,
        "min_exact_controls": 1,
        "min_control_cases": 1,
        "max_control_risk_rows": 0,
        "require_posthoc_source_exact": True,
    },
    {
        "name": "representative-controls",
        "min_opcode_score": 0.95,
        "min_literal_score": 0.65,
        "min_dependency_score": 0.50,
        "max_name_score": 0.22,
        "min_identity_confidence": 0.40,
        "min_exact_controls": 2,
        "min_control_cases": 2,
        "max_control_risk_rows": 0,
        "require_posthoc_source_exact": True,
    },
    {
        "name": "promotion-ready-v1",
        "min_opcode_score": 0.97,
        "min_literal_score": 0.70,
        "min_dependency_score": 0.60,
        "max_name_score": 0.18,
        "min_identity_confidence": 0.50,
        "min_exact_controls": 3,
        "min_control_cases": 3,
        "max_control_risk_rows": 0,
        "require_posthoc_source_exact": True,
    },
    {
        "name": "cve-sensitive-zero-risk",
        "min_opcode_score": 0.98,
        "min_literal_score": 0.75,
        "min_dependency_score": 0.65,
        "max_name_score": 0.15,
        "min_identity_confidence": 0.55,
        "min_exact_controls": 3,
        "min_control_cases": 3,
        "max_control_risk_rows": 0,
        "require_posthoc_source_exact": True,
    },
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a stricter APK-only promotion-gate matrix for the R8 structural "
            "lane. The matrix remains report-only and does not promote matcher, "
            "SBOM, or vulnerability behavior."
        )
    )
    parser.add_argument("--router-json", default=str(DEFAULT_ROUTER_JSON))
    parser.add_argument("--large-analysis-json", default=str(DEFAULT_LARGE_ANALYSIS_JSON))
    parser.add_argument("--ai-suggestions-json", default=str(DEFAULT_AI_SUGGESTIONS_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_matrix(
        router_json=args.router_json,
        large_analysis_json=args.large_analysis_json,
        ai_suggestions_json=args.ai_suggestions_json,
    )
    result = write_outputs(payload, output_json=args.output_json, output_doc=args.output_doc)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_matrix(
    *,
    router_json: str | Path = DEFAULT_ROUTER_JSON,
    large_analysis_json: str | Path = DEFAULT_LARGE_ANALYSIS_JSON,
    ai_suggestions_json: str | Path = DEFAULT_AI_SUGGESTIONS_JSON,
    profiles: tuple[dict[str, Any], ...] = STRICT_PROFILES,
) -> dict[str, Any]:
    rows = [
        evaluate_profile(
            profile,
            router_json=router_json,
            large_analysis_json=large_analysis_json,
            ai_suggestions_json=ai_suggestions_json,
        )
        for profile in profiles
    ]
    best = max(rows, key=lambda row: row["eligible_rows_after_strict_controls"], default=None)
    verdict = "do-not-promote-strict-apk-gates-have-zero-candidates"
    if best and best["eligible_rows_after_strict_controls"]:
        verdict = "strict-apk-gate-candidates-need-live-default-regression-suite"
    return {
        "schema_version": "r8-strict-apk-promotion-gate-matrix-v1",
        "report_only": True,
        "default_matcher_unchanged": True,
        "production_promotion": False,
        "verdict": verdict,
        "scope": (
            "Strict APK-only promotion matrix for the R8 structural recall lane. "
            "Each profile first applies source-free APK evidence thresholds, then "
            "uses source truth only for evaluation and control-risk accounting."
        ),
        "sources": {
            "router_json": normalize_path(router_json),
            "large_analysis_json": normalize_path(large_analysis_json),
            "ai_suggestions_json": normalize_path(ai_suggestions_json),
        },
        "policy": [
            "No profile can promote a row with same-coordinate wrong-version or false-positive controls.",
            "No profile can promote a row without representative exact emitted controls.",
            "Source truth is used only after the APK-only gate fires to grade the candidate.",
            "Even nonzero candidates would still require a live default matcher regression suite before production.",
            "This matrix does not change matcher scoring, selected versions, SBOM output, vulnerability labels, or source-validation metrics.",
        ],
        "summary": {
            "profiles": len(rows),
            "total_gate_pass_rows_across_profiles": sum(row["gate_pass_rows"] for row in rows),
            "total_eligible_rows_after_strict_controls": sum(
                row["eligible_rows_after_strict_controls"] for row in rows
            ),
            "best_profile": best["name"] if best else "",
            "best_profile_candidates": best["eligible_rows_after_strict_controls"]
            if best
            else 0,
            "production_effect": "none",
        },
        "profiles": rows,
    }


def evaluate_profile(
    profile: dict[str, Any],
    *,
    router_json: str | Path,
    large_analysis_json: str | Path,
    ai_suggestions_json: str | Path,
) -> dict[str, Any]:
    payload = build_payload(
        router_json=router_json,
        large_analysis_json=large_analysis_json,
        ai_suggestions_json=ai_suggestions_json,
        min_opcode_score=profile["min_opcode_score"],
        min_literal_score=profile["min_literal_score"],
        min_dependency_score=profile["min_dependency_score"],
        max_name_score=profile["max_name_score"],
        min_identity_confidence=profile["min_identity_confidence"],
    )
    gate_pass_rows = [row for row in payload["rows"] if row["apk_only_gate"]["passes"]]
    blockers = Counter()
    eligible = []
    for row in gate_pass_rows:
        row_blockers = strict_blockers(row, profile)
        blockers.update(row_blockers)
        if not row_blockers:
            eligible.append(row)
    exact_gate_pass_rows = [
        row
        for row in gate_pass_rows
        if row["source_evaluation"].get("candidate_matches_source")
    ]
    return {
        "name": profile["name"],
        "thresholds": {
            key: profile[key]
            for key in (
                "min_opcode_score",
                "min_literal_score",
                "min_dependency_score",
                "max_name_score",
                "min_identity_confidence",
            )
        },
        "control_requirements": {
            key: profile[key]
            for key in (
                "min_exact_controls",
                "min_control_cases",
                "max_control_risk_rows",
                "require_posthoc_source_exact",
            )
        },
        "router_r8_structural_rows": payload["summary"]["router_r8_structural_rows"],
        "gate_pass_rows": len(gate_pass_rows),
        "gate_pass_coordinates": len({row["coordinate"] for row in gate_pass_rows}),
        "posthoc_source_exact_gate_pass_rows": len(exact_gate_pass_rows),
        "eligible_rows_after_strict_controls": len(eligible),
        "eligible_coordinates_after_strict_controls": len(
            {row["coordinate"] for row in eligible}
        ),
        "blocker_counts": dict(sorted(blockers.items())),
        "top_gate_pass_coordinates": top_counts(
            Counter(row["coordinate"] for row in gate_pass_rows),
            limit=10,
        ),
        "top_eligible_coordinates": top_counts(
            Counter(row["coordinate"] for row in eligible),
            limit=10,
        ),
    }


def strict_blockers(row: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    controls = row.get("control_context", {})
    if profile["require_posthoc_source_exact"] and not row["source_evaluation"].get(
        "candidate_matches_source"
    ):
        blockers.append("posthoc-source-mismatch")
    if int(controls.get("control_risk_rows", 0) or 0) > int(
        profile["max_control_risk_rows"]
    ):
        blockers.append("same-coordinate-control-risk")
    if int(controls.get("exact_controls", 0) or 0) < int(profile["min_exact_controls"]):
        blockers.append("insufficient-exact-controls")
    if len(controls.get("case_ids", []) or []) < int(profile["min_control_cases"]):
        blockers.append("insufficient-control-case-support")
    if row.get("ai_summary", {}).get("suppress_uncertain"):
        blockers.append("ai-suppress-uncertain")
    return blockers


def write_outputs(
    payload: dict[str, Any],
    *,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_doc: str | Path = DEFAULT_OUTPUT_DOC,
) -> dict[str, Any]:
    output_json = Path(output_json)
    output_doc = Path(output_doc)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    return {
        "json": normalize_path(output_json),
        "doc": normalize_path(output_doc),
        "verdict": payload["verdict"],
        "profiles": payload["summary"]["profiles"],
        "best_profile_candidates": payload["summary"]["best_profile_candidates"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# R8 Strict APK Promotion Gate Matrix",
        "",
        "Generated by `scripts/build_r8_strict_apk_promotion_gate_matrix.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Profiles evaluated: `{summary['profiles']}`",
        f"- Total gate-pass rows across profiles: `{summary['total_gate_pass_rows_across_profiles']}`",
        f"- Total eligible rows after strict controls: `{summary['total_eligible_rows_after_strict_controls']}`",
        f"- Best profile: `{summary['best_profile']}`",
        f"- Best-profile candidates: `{summary['best_profile_candidates']}`",
        f"- Production effect: `{summary['production_effect']}`",
        "",
        "## Matrix",
        "",
        "| Profile | Gate pass rows | Gate pass coordinates | Posthoc source-exact passes | Eligible rows after strict controls | Eligible coordinates | Main blockers |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["profiles"]:
        blockers = ", ".join(
            f"{key}={value}" for key, value in sorted(row["blocker_counts"].items())
        )
        lines.append(
            "| "
            f"`{row['name']}` | "
            f"{row['gate_pass_rows']} | "
            f"{row['gate_pass_coordinates']} | "
            f"{row['posthoc_source_exact_gate_pass_rows']} | "
            f"{row['eligible_rows_after_strict_controls']} | "
            f"{row['eligible_coordinates_after_strict_controls']} | "
            f"{blockers or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Profile Requirements",
            "",
            "| Profile | Opcode | Literal | Dependency | Max name | Identity | Exact controls | Control cases | Max risk |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["profiles"]:
        thresholds = row["thresholds"]
        controls = row["control_requirements"]
        lines.append(
            "| "
            f"`{row['name']}` | "
            f"{thresholds['min_opcode_score']} | "
            f"{thresholds['min_literal_score']} | "
            f"{thresholds['min_dependency_score']} | "
            f"{thresholds['max_name_score']} | "
            f"{thresholds['min_identity_confidence']} | "
            f"{controls['min_exact_controls']} | "
            f"{controls['min_control_cases']} | "
            f"{controls['max_control_risk_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Promotion Decision",
            "",
            "The matrix makes the future production bar explicit. Passing a structural APK-only score threshold is not enough. A row also needs clean same-coordinate controls, representative exact emitted controls, and then a live default matcher regression suite. The current artifact remains report-only.",
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for key, value in sorted(payload["sources"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def top_counts(counter: Counter, *, limit: int) -> list[dict[str, Any]]:
    return [
        {"coordinate": str(coordinate), "rows": count}
        for coordinate, count in counter.most_common(limit)
    ]


def normalize_path(path: str | Path) -> str:
    return Path(path).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
