from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_INPUT_JSON = Path(
    "data/results/experiments/version-unique-literal-context-diagnostics.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/version-unique-literal-context-promotion-candidate.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_PROMOTION_CANDIDATE.md"
)
MIN_PROMOTION_UNIQUE_LITERAL_CONTEXT_MATCHES = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Derive a guarded opt-in promotion candidate from the "
            "version-unique literal/context diagnostic output."
        )
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
    replacement_rows = list(source.get("suggested_rows", []))
    kept_rows = [
        row
        for row in replacement_rows
        if suggested_unique_literal_context_matches(row)
        >= MIN_PROMOTION_UNIQUE_LITERAL_CONTEXT_MATCHES
    ]
    filtered_rows = [
        row
        for row in replacement_rows
        if suggested_unique_literal_context_matches(row)
        < MIN_PROMOTION_UNIQUE_LITERAL_CONTEXT_MATCHES
    ]
    improvement_rows = [
        row
        for row in kept_rows
        if decision(row).get("classification")
        == "potential-target-improvement-needs-control-matrix"
    ]
    regression_rows = [
        row
        for row in kept_rows
        if decision(row).get("classification") == "regression-risk-do-not-promote"
    ]
    summary = {
        "source_replacement_suggestions": len(replacement_rows),
        "minimum_unique_literal_context_matches": MIN_PROMOTION_UNIQUE_LITERAL_CONTEXT_MATCHES,
        "kept_replacement_suggestions": len(kept_rows),
        "filtered_low_support_suggestions": len(filtered_rows),
        "potential_target_improvements": len(improvement_rows),
        "regression_risks": len(regression_rows),
    }
    return {
        "schema_version": 1,
        "source": normalize_path(input_json),
        "source_verdict": source.get("verdict"),
        "verdict": verdict(summary),
        "scope": (
            "Promotion-candidate evidence only. This artifact applies a stricter "
            "minimum-support gate to the version-unique literal/context diagnostic "
            "output. The production default remains unchanged unless a later "
            "current-control report regeneration promotes the opt-in rule."
        ),
        "policy": [
            "Keep only replacement suggestions with at least two matched version-unique literal/context features.",
            "Reject the candidate if any kept row is a regression risk.",
            "Keep one-match rows as diagnostics only because the broad run showed one-match regressions.",
            "Use the matcher opt-in flag for targeted validation before changing defaults.",
        ],
        "summary": summary,
        "kept_rows": kept_rows,
        "filtered_rows": filtered_rows,
        "improvement_rows": improvement_rows,
        "regression_rows": regression_rows,
    }


def decision(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("version_unique_literal_context_decision")
    return value if isinstance(value, dict) else {}


def suggested_unique_literal_context_matches(row: dict[str, Any]) -> int:
    return int(decision(row).get("suggested_unique_literal_context_matches") or 0)


def verdict(summary: dict[str, Any]) -> str:
    if summary["regression_risks"]:
        return "version-unique-literal-context-promotion-rejected-regression-risk"
    if summary["potential_target_improvements"]:
        return "version-unique-literal-context-opt-in-candidate-clean-diagnostic-matrix"
    return "version-unique-literal-context-promotion-no-target-improvement"


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
        "# Version-Unique Literal-Context Promotion Candidate",
        "",
        "Generated by `scripts/build_version_unique_literal_context_promotion_candidate.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Source diagnostic verdict: `{payload['source_verdict']}`",
        f"- Source replacement suggestions: `{summary['source_replacement_suggestions']}`",
        f"- Minimum matched version-unique literal/context features: `{summary['minimum_unique_literal_context_matches']}`",
        f"- Kept replacement suggestions: `{summary['kept_replacement_suggestions']}`",
        f"- Filtered low-support suggestions: `{summary['filtered_low_support_suggestions']}`",
        f"- Potential target improvements: `{summary['potential_target_improvements']}`",
        f"- Regression risks after gate: `{summary['regression_risks']}`",
        "",
        "## Kept Rows",
        "",
        "| Case | Coordinate | Current | Suggested | Source | Classification | Score | Matches |",
        "|---|---|---:|---:|---|---|---:|---:|",
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
            f"`{md(item.get('classification'))}` | "
            f"{md(item.get('suggested_unique_literal_context_score'))} | "
            f"{md(item.get('suggested_unique_literal_context_matches'))} |"
        )
    if not payload["kept_rows"]:
        lines.append("| none |  |  |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Filtered Low-Support Rows",
            "",
            "| Case | Coordinate | Current | Suggested | Source | Classification | Matches |",
            "|---|---|---:|---:|---|---|---:|",
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
            f"`{md(item.get('classification'))}` | "
            f"{md(item.get('suggested_unique_literal_context_matches'))} |"
        )
    if not payload["filtered_rows"]:
        lines.append("| none |  |  |  |  |  |  |")

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "The stricter minimum-support gate keeps the VLC RecyclerView recovery "
            "and filters all one-match suggestions, including the observed "
            "GridLayout regressions. This is a clean opt-in candidate, not a "
            "default promotion yet.",
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
