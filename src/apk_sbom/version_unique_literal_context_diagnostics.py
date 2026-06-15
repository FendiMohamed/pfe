from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any, Sequence

from apk_sbom.dex_analyzer import analyze_apk_dex
from apk_sbom.matcher import (
    FeatureSet,
    ReferenceComponentFeatures,
    feature_set_from_apk_analysis,
    load_reference_components,
)


DEFAULT_PHASE4_JSON = Path("data/results/experiments/r8-phase4-scoped-experiment-diagnostics.json")
DEFAULT_REFERENCE_DB = Path(
    "data/reference_db/reference_features_phase4_multiscale_calibrated_combined.sqlite"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/version-unique-literal-context-diagnostics.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DIAGNOSTICS.md")
MIN_UNIQUE_LITERAL_CONTEXT_SCORE = 0.10
MIN_UNIQUE_LITERAL_CONTEXT_ADVANTAGE = 0.05
MIN_UNIQUE_LITERAL_CONTEXT_MATCHES = 1
REPLACEMENT_CLASSIFICATIONS = {
    "alternate-source-version",
    "conflicting-mismatch-do-not-promote",
    "potential-target-improvement-needs-control-matrix",
    "regression-risk-do-not-promote",
}


@dataclass(frozen=True)
class VersionUniqueLiteralContextDecision:
    classification: str
    selected_version: str | None
    suggested_version: str | None
    source_versions: tuple[str, ...]
    selected_unique_literal_context_score: float | None
    suggested_unique_literal_context_score: float | None
    next_unique_literal_context_score: float | None
    unique_literal_context_advantage: float | None
    selected_unique_literal_context_matches: int | None
    suggested_unique_literal_context_matches: int | None
    suggested_reference_unique_literal_context_features: int | None
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate version-unique literal/context feature evidence as a "
            "diagnostic-only version tie-breaker."
        )
    )
    parser.add_argument("--phase4-json", default=str(DEFAULT_PHASE4_JSON))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        phase4_json=Path(args.phase4_json),
        reference_db=Path(args.reference_db),
    )
    result = write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_doc=Path(args.output_doc),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_payload(*, phase4_json: Path, reference_db: Path) -> dict[str, Any]:
    phase4 = json.loads(phase4_json.read_text(encoding="utf-8"))
    references_by_coordinate = load_references_by_coordinate(reference_db)
    feature_cache: dict[str, FeatureSet | None] = {}

    controlled_rows = [
        evaluate_phase4_row(
            row_type="controlled",
            row=row,
            source_versions=[str(row.get("expected_version") or "")],
            references_by_coordinate=references_by_coordinate,
            feature_cache=feature_cache,
        )
        for row in phase4.get("controlled_cases", [])
        if row.get("expected_version")
    ]
    real_rows = [
        evaluate_phase4_row(
            row_type="real-source-validated",
            row=row,
            source_versions=[str(version) for version in row.get("source_versions", [])],
            references_by_coordinate=references_by_coordinate,
            feature_cache=feature_cache,
        )
        for row in phase4.get("real_component_rows", [])
        if row.get("source_versions")
    ]
    rows = [*controlled_rows, *real_rows]
    classification_counts = Counter(
        row["version_unique_literal_context_decision"]["classification"]
        for row in rows
    )
    suggested_rows = [
        row
        for row in rows
        if row["version_unique_literal_context_decision"]["suggested_version"]
        and row["version_unique_literal_context_decision"]["suggested_version"]
        != row["baseline_selected_version"]
        and row["version_unique_literal_context_decision"]["classification"]
        in REPLACEMENT_CLASSIFICATIONS
    ]
    regression_rows = [
        row
        for row in suggested_rows
        if row["version_unique_literal_context_decision"]["classification"]
        == "regression-risk-do-not-promote"
    ]
    improvement_rows = [
        row
        for row in suggested_rows
        if row["version_unique_literal_context_decision"]["classification"]
        == "potential-target-improvement-needs-control-matrix"
    ]
    summary = {
        "rows_inspected": len(rows),
        "controlled_rows_inspected": len(controlled_rows),
        "real_source_validated_rows_inspected": len(real_rows),
        "version_unique_literal_context_suggestions": len(suggested_rows),
        "potential_target_improvements": len(improvement_rows),
        "regression_risks": len(regression_rows),
        "classification_counts": dict(sorted(classification_counts.items())),
    }
    return {
        "schema_version": 1,
        "sources": {
            "phase4_json": normalize_path(phase4_json),
            "reference_db": normalize_path(reference_db),
        },
        "verdict": verdict(summary),
        "scope": (
            "Diagnostic only. This artifact evaluates literal/context features "
            "that are unique to one reference version within the same coordinate, "
            "but does not change matcher scoring, selected versions, SBOM "
            "components, vulnerability labels, or source-validation metrics."
        ),
        "policy": [
            "Version-unique literal/context evidence is diagnostic-only until it passes current controls.",
            "Any suggested replacement must improve a source-validated target and avoid all controlled or real source-validated regressions.",
            "Regression-risk rows block production promotion even when target rows improve.",
            "Rows with no unique feature match or too small a margin remain ambiguous rather than becoming exact-version claims.",
        ],
        "thresholds": {
            "minimum_unique_literal_context_score": MIN_UNIQUE_LITERAL_CONTEXT_SCORE,
            "minimum_unique_literal_context_advantage": MIN_UNIQUE_LITERAL_CONTEXT_ADVANTAGE,
            "minimum_unique_literal_context_matches": MIN_UNIQUE_LITERAL_CONTEXT_MATCHES,
        },
        "summary": summary,
        "suggested_rows": suggested_rows,
        "regression_rows": regression_rows,
        "improvement_rows": improvement_rows,
    }


def load_references_by_coordinate(
    reference_db: Path,
) -> dict[str, list[ReferenceComponentFeatures]]:
    if not reference_db.exists():
        return {}
    with sqlite3.connect(reference_db) as connection:
        references = load_reference_components(connection)
    grouped: dict[str, list[ReferenceComponentFeatures]] = {}
    for reference in references:
        grouped.setdefault(reference.coordinate, []).append(reference)
    return grouped


def evaluate_phase4_row(
    *,
    row_type: str,
    row: dict[str, Any],
    source_versions: Sequence[str],
    references_by_coordinate: dict[str, list[ReferenceComponentFeatures]],
    feature_cache: dict[str, FeatureSet | None],
) -> dict[str, Any]:
    coordinate = str(row.get("coordinate") or "")
    apk_path = Path(str(row.get("apk_path") or ""))
    baseline_selected = str(row.get("baseline_selected_version") or "")
    references = references_by_coordinate.get(coordinate, [])
    candidates: list[dict[str, Any]] = []
    has_apk_features = False

    if apk_path.exists():
        feature_key = normalize_path(apk_path)
        if feature_key not in feature_cache:
            feature_cache[feature_key] = feature_set_for_apk(apk_path)
        apk_features = feature_cache[feature_key]
        has_apk_features = apk_features is not None
        if apk_features is not None:
            candidates = rank_version_unique_literal_context_candidates(
                apk_features,
                references,
            )

    decision = classify_version_unique_literal_context_row(
        selected_version=baseline_selected,
        source_versions=source_versions,
        candidates=candidates,
        reference_count=len(references),
        has_apk_features=has_apk_features,
    )
    return {
        "row_type": row_type,
        "case_id": row.get("case_id") or row.get("slug"),
        "case_name": row.get("case_name"),
        "role": row.get("role") or row.get("category"),
        "coordinate": coordinate,
        "apk_path": normalize_path(apk_path),
        "baseline_selected_version": baseline_selected or None,
        "source_versions": [str(version) for version in source_versions],
        "phase4_outcome": row.get("outcome"),
        "reference_versions_available": len(references),
        "version_unique_literal_context_decision": decision.to_dict(),
        "top_version_unique_literal_context_versions": candidates[:3],
    }


def feature_set_for_apk(apk_path: Path) -> FeatureSet | None:
    if not apk_path.exists():
        return None
    analysis = analyze_apk_dex(apk_path, include_members=True)
    return feature_set_from_apk_analysis(analysis)


def rank_version_unique_literal_context_candidates(
    apk_features: FeatureSet,
    references: Sequence[ReferenceComponentFeatures],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for reference in references:
        sibling_features = [
            sibling.features
            for sibling in references
            if sibling.component_id != reference.component_id
        ]
        unique_features = version_unique_literal_context_features(
            reference.features,
            sibling_features,
        )
        matches = apk_features.literal_context_features & unique_features
        score = coverage_score(matches, unique_features)
        rows.append(
            {
                "version": reference.version,
                "coordinate": reference.coordinate,
                "unique_literal_context_score": round(score, 6),
                "matched_unique_literal_context_features": len(matches),
                "reference_unique_literal_context_features": len(unique_features),
            }
        )
    return sorted(
        rows,
        key=lambda item: (
            float(item["unique_literal_context_score"]),
            int(item["matched_unique_literal_context_features"]),
            str(item["version"]),
        ),
        reverse=True,
    )


def version_unique_literal_context_features(
    reference_features: FeatureSet,
    sibling_features: Sequence[FeatureSet],
) -> set[str]:
    if not sibling_features:
        return set()
    sibling_literal_context = set().union(
        *(features.literal_context_features for features in sibling_features)
    )
    return reference_features.literal_context_features - sibling_literal_context


def classify_version_unique_literal_context_row(
    *,
    selected_version: str,
    source_versions: Sequence[str],
    candidates: Sequence[dict[str, Any]],
    reference_count: int,
    has_apk_features: bool = True,
) -> VersionUniqueLiteralContextDecision:
    source_version_set = {str(version) for version in source_versions}
    selected = find_candidate(candidates, selected_version)
    if not has_apk_features:
        return make_decision(
            "missing-apk-or-features",
            selected_version=selected_version,
            source_versions=source_versions,
            selected=selected,
            suggested=None,
            next_candidate=None,
            reason_codes=("missing-apk-or-feature-extraction-failed",),
        )
    if reference_count <= 1 or len(candidates) < 2:
        return make_decision(
            "not-rankable",
            selected_version=selected_version,
            source_versions=source_versions,
            selected=selected,
            suggested=None,
            next_candidate=None,
            reason_codes=("fewer-than-two-reference-versions",),
        )

    suggested = candidates[0]
    next_candidate = candidates[1]
    suggested_score = unique_literal_context_score(suggested)
    next_score = unique_literal_context_score(next_candidate)
    advantage = round(suggested_score - next_score, 6)
    suggested_matches = int(suggested.get("matched_unique_literal_context_features") or 0)

    if suggested_matches < MIN_UNIQUE_LITERAL_CONTEXT_MATCHES:
        return make_decision(
            "no-version-unique-literal-context-match",
            selected_version=selected_version,
            source_versions=source_versions,
            selected=selected,
            suggested=suggested,
            next_candidate=next_candidate,
            reason_codes=("below-minimum-unique-literal-context-matches",),
        )
    if suggested_score < MIN_UNIQUE_LITERAL_CONTEXT_SCORE:
        return make_decision(
            "no-usable-version-unique-literal-context-signal",
            selected_version=selected_version,
            source_versions=source_versions,
            selected=selected,
            suggested=suggested,
            next_candidate=next_candidate,
            reason_codes=("below-minimum-unique-literal-context-score",),
        )
    if advantage < MIN_UNIQUE_LITERAL_CONTEXT_ADVANTAGE:
        return make_decision(
            "version-unique-literal-context-margin-too-small",
            selected_version=selected_version,
            source_versions=source_versions,
            selected=selected,
            suggested=suggested,
            next_candidate=next_candidate,
            reason_codes=("unique-literal-context-advantage-too-small",),
        )
    if str(suggested.get("version") or "") == selected_version:
        return make_decision(
            "version-unique-literal-context-supports-current-selection",
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
        reason_codes = ("source-version-has-stronger-version-unique-literal-context",)
    elif selected_is_source and not suggested_is_source:
        classification = "regression-risk-do-not-promote"
        reason_codes = ("version-unique-context-would-replace-source-confirmed-version",)
    elif not selected_is_source and not suggested_is_source:
        classification = "conflicting-mismatch-do-not-promote"
        reason_codes = ("version-unique-context-suggests-non-source-version",)
    else:
        classification = "alternate-source-version"
        reason_codes = ("version-unique-context-suggests-another-source-version",)
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
) -> VersionUniqueLiteralContextDecision:
    suggested_score = unique_literal_context_score(suggested) if suggested else None
    next_score = unique_literal_context_score(next_candidate) if next_candidate else None
    advantage = (
        round(suggested_score - next_score, 6)
        if suggested_score is not None and next_score is not None
        else None
    )
    return VersionUniqueLiteralContextDecision(
        classification=classification,
        selected_version=selected_version or None,
        suggested_version=str(suggested.get("version") or "") if suggested else None,
        source_versions=tuple(str(version) for version in source_versions),
        selected_unique_literal_context_score=(
            unique_literal_context_score(selected) if selected else None
        ),
        suggested_unique_literal_context_score=suggested_score,
        next_unique_literal_context_score=next_score,
        unique_literal_context_advantage=advantage,
        selected_unique_literal_context_matches=(
            unique_literal_context_matches(selected) if selected else None
        ),
        suggested_unique_literal_context_matches=(
            unique_literal_context_matches(suggested) if suggested else None
        ),
        suggested_reference_unique_literal_context_features=(
            int(suggested.get("reference_unique_literal_context_features") or 0)
            if suggested
            else None
        ),
        reason_codes=tuple(reason_codes),
    )


def find_candidate(
    candidates: Sequence[dict[str, Any]],
    version: str,
) -> dict[str, Any] | None:
    for candidate in candidates:
        if str(candidate.get("version") or "") == version:
            return candidate
    return None


def unique_literal_context_score(candidate: dict[str, Any] | None) -> float:
    if candidate is None:
        return 0.0
    return round(float(candidate.get("unique_literal_context_score") or 0.0), 6)


def unique_literal_context_matches(candidate: dict[str, Any] | None) -> int:
    if candidate is None:
        return 0
    return int(candidate.get("matched_unique_literal_context_features") or 0)


def coverage_score(matches: set[str], reference_values: set[str]) -> float:
    if not reference_values:
        return 0.0
    return len(matches) / len(reference_values)


def verdict(summary: dict[str, Any]) -> str:
    if summary["regression_risks"]:
        return "version-unique-literal-context-rejected-regression-risk"
    if summary["potential_target_improvements"]:
        return "version-unique-literal-context-candidate-needs-control-matrix"
    return "version-unique-literal-context-no-safe-promotion"


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
        "# Version-Unique Literal-Context Diagnostics",
        "",
        "Generated by `apk-sbom version-unique-literal-context-experiment` or "
        "`scripts/build_version_unique_literal_context_diagnostics.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Rows inspected: `{summary['rows_inspected']}`",
        f"- Controlled rows inspected: `{summary['controlled_rows_inspected']}`",
        f"- Real source-validated rows inspected: `{summary['real_source_validated_rows_inspected']}`",
        f"- Version-unique literal/context replacement suggestions: `{summary['version_unique_literal_context_suggestions']}`",
        f"- Potential target improvements: `{summary['potential_target_improvements']}`",
        f"- Regression risks: `{summary['regression_risks']}`",
        f"- Minimum version-unique literal/context score: `{thresholds['minimum_unique_literal_context_score']}`",
        f"- Minimum version-unique literal/context advantage: `{thresholds['minimum_unique_literal_context_advantage']}`",
        f"- Minimum version-unique literal/context matches: `{thresholds['minimum_unique_literal_context_matches']}`",
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
            "| Type | Case | Role | Coordinate | Current | Suggested | Source | Classification | Score | Advantage | Matches |",
            "|---|---|---|---|---:|---:|---|---|---:|---:|---:|",
        ]
    )
    for row in payload["suggested_rows"]:
        decision = row["version_unique_literal_context_decision"]
        lines.append(
            "| "
            f"{md(row.get('row_type'))} | "
            f"{md(row.get('case_id'))} | "
            f"{md(row.get('role'))} | "
            f"`{md(row.get('coordinate'))}` | "
            f"{md(row.get('baseline_selected_version'))} | "
            f"{md(decision.get('suggested_version'))} | "
            f"{md(', '.join(row.get('source_versions') or []))} | "
            f"`{md(decision.get('classification'))}` | "
            f"{md(decision.get('suggested_unique_literal_context_score'))} | "
            f"{md(decision.get('unique_literal_context_advantage'))} | "
            f"{md(decision.get('suggested_unique_literal_context_matches'))} |"
        )
    if not payload["suggested_rows"]:
        lines.append("| none |  |  |  |  |  |  |  |  |  |  |")

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            conclusion(payload),
            "",
        ]
    )
    return "\n".join(lines)


def conclusion(payload: dict[str, Any]) -> str:
    verdict_value = payload["verdict"]
    if verdict_value == "version-unique-literal-context-rejected-regression-risk":
        return (
            "Version-unique literal/context evidence is sharper than raw overlap, "
            "but this run still has regression-risk rows. Keep it diagnostic-only "
            "and do not promote it into matcher scoring."
        )
    if verdict_value == "version-unique-literal-context-candidate-needs-control-matrix":
        return (
            "This run found target improvements without immediate regression-risk "
            "rows in the inspected set. The next step is a fresh current-control "
            "comparison before any production scorer change."
        )
    return (
        "This run did not find a safe promotable replacement. Keep version-unique "
        "literal/context evidence as diagnostic support while testing narrower "
        "signals or additional source-validated controls."
    )


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
