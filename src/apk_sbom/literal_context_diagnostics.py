from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Sequence


DEFAULT_INPUT_JSON = Path("data/results/experiments/r8-phase4-scoped-experiment-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/literal-context-version-tie-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/LITERAL_CONTEXT_VERSION_TIE_DIAGNOSTICS.md")
MIN_LITERAL_CONTEXT_SCORE = 0.10
MIN_LITERAL_CONTEXT_ADVANTAGE = 0.05
REPLACEMENT_CLASSIFICATIONS = {
    "alternate-source-version",
    "conflicting-mismatch-do-not-promote",
    "potential-target-improvement-needs-control-matrix",
    "regression-risk-do-not-promote",
}


@dataclass(frozen=True)
class LiteralContextDecision:
    classification: str
    selected_version: str | None
    suggested_version: str | None
    source_versions: tuple[str, ...]
    selected_literal_context_score: float | None
    suggested_literal_context_score: float | None
    next_literal_context_score: float | None
    literal_context_advantage: float | None
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate raw literal/context feature ranking as a diagnostic-only "
            "version tie-breaker."
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
    rows = [
        evaluate_row(row)
        for row in source.get("real_component_rows", [])
        if row.get("source_versions")
    ]
    outcome_counts = Counter(
        row["literal_context_decision"]["classification"]
        for row in rows
    )
    suggested_rows = [
        row
        for row in rows
        if row["literal_context_decision"]["suggested_version"]
        and row["literal_context_decision"]["suggested_version"] != row["baseline_selected_version"]
        and row["literal_context_decision"]["classification"] in REPLACEMENT_CLASSIFICATIONS
    ]
    regression_rows = [
        row
        for row in suggested_rows
        if row["literal_context_decision"]["classification"] == "regression-risk-do-not-promote"
    ]
    improvement_rows = [
        row
        for row in suggested_rows
        if row["literal_context_decision"]["classification"]
        == "potential-target-improvement-needs-control-matrix"
    ]
    summary = {
        "source_validated_rows_inspected": len(rows),
        "literal_context_suggestions": len(suggested_rows),
        "potential_target_improvements": len(improvement_rows),
        "regression_risks": len(regression_rows),
        "classification_counts": dict(sorted(outcome_counts.items())),
    }
    return {
        "schema_version": 1,
        "source": normalize_path(input_json),
        "verdict": verdict(summary),
        "scope": (
            "Diagnostic only. This artifact evaluates raw literal/context feature "
            "ranking as a possible version tie-breaker, but does not change matcher "
            "scoring, selected versions, SBOM components, vulnerability labels, or "
            "source-validation metrics."
        ),
        "policy": [
            "Raw literal/context score is not a production reranker.",
            "Any suggested replacement must improve a source-validated target and avoid all current-control regressions.",
            "Regression-risk rows block promotion even when some target rows improve.",
            "Use this artifact to decide whether a narrower version-unique literal/context experiment is justified.",
        ],
        "thresholds": {
            "minimum_literal_context_score": MIN_LITERAL_CONTEXT_SCORE,
            "minimum_literal_context_advantage": MIN_LITERAL_CONTEXT_ADVANTAGE,
        },
        "summary": summary,
        "suggested_rows": suggested_rows,
        "regression_rows": regression_rows,
        "improvement_rows": improvement_rows,
    }


def evaluate_row(row: dict[str, Any]) -> dict[str, Any]:
    decision = classify_literal_context_row(
        selected_version=str(row.get("baseline_selected_version") or ""),
        source_versions=[str(version) for version in row.get("source_versions", [])],
        candidates=row.get("top_diagnostic_versions", []),
    )
    return {
        "case_id": row.get("case_id"),
        "case_name": row.get("case_name"),
        "role": row.get("role"),
        "coordinate": row.get("coordinate"),
        "baseline_selected_version": row.get("baseline_selected_version"),
        "source_versions": row.get("source_versions", []),
        "validation_status": row.get("validation_status"),
        "literal_context_decision": decision.to_dict(),
    }


def classify_literal_context_row(
    *,
    selected_version: str,
    source_versions: Sequence[str],
    candidates: Sequence[dict[str, Any]],
) -> LiteralContextDecision:
    source_version_set = {str(version) for version in source_versions}
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            literal_context_score(candidate),
            float(candidate.get("diagnostic_score") or 0.0),
            str(candidate.get("version") or ""),
        ),
        reverse=True,
    )
    selected = find_candidate(ranked, selected_version)
    if len(ranked) < 2:
        return make_decision(
            "not-rankable",
            selected_version=selected_version,
            source_versions=source_versions,
            selected=selected,
            suggested=None,
            next_candidate=None,
            reason_codes=("fewer-than-two-reference-versions",),
        )

    suggested = ranked[0]
    next_candidate = ranked[1]
    suggested_score = literal_context_score(suggested)
    next_score = literal_context_score(next_candidate)
    advantage = round(suggested_score - next_score, 6)

    if suggested_score < MIN_LITERAL_CONTEXT_SCORE:
        return make_decision(
            "no-usable-literal-context-signal",
            selected_version=selected_version,
            source_versions=source_versions,
            selected=selected,
            suggested=suggested,
            next_candidate=next_candidate,
            reason_codes=("below-minimum-literal-context-score",),
        )
    if advantage < MIN_LITERAL_CONTEXT_ADVANTAGE:
        return make_decision(
            "literal-context-margin-too-small",
            selected_version=selected_version,
            source_versions=source_versions,
            selected=selected,
            suggested=suggested,
            next_candidate=next_candidate,
            reason_codes=("literal-context-advantage-too-small",),
        )
    if str(suggested.get("version") or "") == selected_version:
        return make_decision(
            "literal-context-supports-current-selection",
            selected_version=selected_version,
            source_versions=source_versions,
            selected=selected,
            suggested=suggested,
            next_candidate=next_candidate,
            reason_codes=("suggested-version-is-current-selection",),
        )

    suggested_version = str(suggested.get("version") or "")
    selected_is_source = selected_version in source_version_set
    suggested_is_source = suggested_version in source_version_set
    if not selected_is_source and suggested_is_source:
        classification = "potential-target-improvement-needs-control-matrix"
        reason_codes = ("source-version-has-stronger-literal-context-score",)
    elif selected_is_source and not suggested_is_source:
        classification = "regression-risk-do-not-promote"
        reason_codes = ("literal-context-would-replace-source-confirmed-version",)
    elif not selected_is_source and not suggested_is_source:
        classification = "conflicting-mismatch-do-not-promote"
        reason_codes = ("literal-context-suggests-non-source-version",)
    else:
        classification = "alternate-source-version"
        reason_codes = ("literal-context-suggests-another-source-version",)
    return make_decision(
        classification,
        selected_version=selected_version,
        source_versions=source_versions,
        selected=selected,
        suggested=suggested,
        next_candidate=next_candidate,
        reason_codes=reason_codes,
    )


def make_decision(
    classification: str,
    *,
    selected_version: str,
    source_versions: Sequence[str],
    selected: dict[str, Any] | None,
    suggested: dict[str, Any] | None,
    next_candidate: dict[str, Any] | None,
    reason_codes: Sequence[str],
) -> LiteralContextDecision:
    suggested_score = literal_context_score(suggested) if suggested else None
    next_score = literal_context_score(next_candidate) if next_candidate else None
    advantage = (
        round(suggested_score - next_score, 6)
        if suggested_score is not None and next_score is not None
        else None
    )
    return LiteralContextDecision(
        classification=classification,
        selected_version=selected_version or None,
        suggested_version=str(suggested.get("version") or "") if suggested else None,
        source_versions=tuple(str(version) for version in source_versions),
        selected_literal_context_score=(
            literal_context_score(selected) if selected else None
        ),
        suggested_literal_context_score=suggested_score,
        next_literal_context_score=next_score,
        literal_context_advantage=advantage,
        reason_codes=tuple(reason_codes),
    )


def literal_context_score(candidate: dict[str, Any] | None) -> float:
    if candidate is None:
        return 0.0
    features = candidate.get("feature_scores") or {}
    return round(float(features.get("literal_context_features") or 0.0), 6)


def find_candidate(
    candidates: Sequence[dict[str, Any]],
    version: str,
) -> dict[str, Any] | None:
    for candidate in candidates:
        if str(candidate.get("version") or "") == version:
            return candidate
    return None


def verdict(summary: dict[str, Any]) -> str:
    if summary["regression_risks"]:
        return "literal-context-raw-score-rejected-regression-risk"
    if summary["potential_target_improvements"]:
        return "literal-context-raw-score-candidate-needs-control-matrix"
    return "literal-context-raw-score-no-safe-promotion"


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
    thresholds = payload["thresholds"]
    lines = [
        "# Literal-Context Version-Tie Diagnostics",
        "",
        "Generated by `apk-sbom literal-context-experiment` or "
        "`scripts/build_literal_context_version_tie_diagnostics.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Source-validated rows inspected: `{summary['source_validated_rows_inspected']}`",
        f"- Literal-context replacement suggestions: `{summary['literal_context_suggestions']}`",
        f"- Potential target improvements: `{summary['potential_target_improvements']}`",
        f"- Regression risks: `{summary['regression_risks']}`",
        f"- Minimum literal/context score: `{thresholds['minimum_literal_context_score']}`",
        f"- Minimum literal/context advantage: `{thresholds['minimum_literal_context_advantage']}`",
        "",
        "## Classification Counts",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    for classification, count in summary["classification_counts"].items():
        lines.append(f"| `{classification}` | {count} |")

    lines.extend(
        [
            "",
            "## Suggested Replacement Rows",
            "",
            "| Case | Role | Coordinate | Current | Suggested | Source | Classification | Advantage |",
            "|---|---|---|---:|---:|---|---|---:|",
        ]
    )
    for row in payload["suggested_rows"]:
        decision = row["literal_context_decision"]
        lines.append(
            "| "
            f"{md(row.get('case_id'))} | "
            f"{md(row.get('role'))} | "
            f"`{md(row.get('coordinate'))}` | "
            f"{md(row.get('baseline_selected_version'))} | "
            f"{md(decision.get('suggested_version'))} | "
            f"{md(', '.join(row.get('source_versions') or []))} | "
            f"`{md(decision.get('classification'))}` | "
            f"{md(decision.get('literal_context_advantage'))} |"
        )
    if not payload["suggested_rows"]:
        lines.append("| none |  |  |  |  |  |  |  |")

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Raw literal/context scoring is useful evidence, but this diagnostic does not justify "
            "production promotion. At the current thresholds it produces regression-risk rows, "
            "so the next safe step is a narrower version-unique literal/context experiment or "
            "another scoped signal with a fresh current-control matrix.",
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
