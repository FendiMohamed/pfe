from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any


DEFAULT_ROUTER_JSON = Path("data/results/evaluation/hybrid-matcher-router-v1.json")
DEFAULT_LARGE_ANALYSIS_JSON = Path(
    "data/results/evaluation/large-combined-real-apk-analysis.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/version-band-apk-reranker-v2.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/VERSION_BAND_APK_RERANKER_V2.md")
DEFAULT_MAX_SCORE_DROP = 0.05
DEFAULT_MIN_SIBLING_ERA_ANCHORS = 2


def build_payload(
    *,
    router_json: str | Path = DEFAULT_ROUTER_JSON,
    large_analysis_json: str | Path = DEFAULT_LARGE_ANALYSIS_JSON,
    max_score_drop: float = DEFAULT_MAX_SCORE_DROP,
    min_sibling_era_anchors: int = DEFAULT_MIN_SIBLING_ERA_ANCHORS,
) -> dict[str, Any]:
    router = _load_json(router_json)
    analysis = _load_json(large_analysis_json)
    report_cache = load_report_decisions(analysis)

    version_band_coordinates = {
        str(row.get("coordinate") or "")
        for row in router.get("rows", [])
        if row.get("recommended_profile") == "version-band-rerank"
        and row.get("coordinate")
    }
    rows = [
        evaluate_version_row(
            row,
            report_cache=report_cache,
            max_score_drop=max_score_drop,
            min_sibling_era_anchors=min_sibling_era_anchors,
        )
        for row in analysis.get("version_rows", [])
        if str(row.get("coordinate") or "") in version_band_coordinates
    ]
    summary = summarize_rows(rows, analysis=analysis, version_band_coordinates=version_band_coordinates)
    return {
        "schema_version": "version-band-apk-reranker-v2",
        "report_only": True,
        "default_matcher_unchanged": True,
        "verdict": verdict(summary),
        "scope": (
            "APK-only report-only prototype. It uses only baseline APK report "
            "decisions, same-coordinate alternatives, and sibling version-era "
            "anchors to decide whether a version-band rerank would fire. Source "
            "versions are used only after the decision to label fixes and regressions."
        ),
        "thresholds": {
            "max_score_drop": max_score_drop,
            "min_sibling_era_anchors": min_sibling_era_anchors,
            "requires_unique_dominant_sibling_era": True,
        },
        "policy": [
            "Do not use source versions to choose a rerank candidate.",
            "Only consider same-coordinate alternatives already exposed by the baseline APK report.",
            "Require a unique dominant sibling version era before changing the selected version.",
            "Reject the prototype if any exact source-validated control would regress.",
            "Keep false-positive extra emissions as blocking controls because version reranking cannot create source evidence.",
            "This artifact does not change matcher scoring, selected versions, SBOM output, CVE labels, or source-validation metrics.",
        ],
        "sources": {
            "router_json": normalize_path(router_json),
            "large_analysis_json": normalize_path(large_analysis_json),
        },
        "summary": summary,
        "top_change_coordinates": _top_counts(
            Counter(row["coordinate"] for row in rows if row["apk_only_decision"]["would_change"]),
            limit=20,
        ),
        "top_source_candidate_available_coordinates": _top_counts(
            Counter(
                row["coordinate"]
                for row in rows
                if row["analysis_class"] == "wrong-version"
                and row["evaluation"]["source_version_in_baseline_alternatives"]
            ),
            limit=20,
        ),
        "classification_counts": dict(
            sorted(Counter(row["evaluation"]["classification"] for row in rows).items())
        ),
        "rows": rows,
    }


def load_report_decisions(analysis: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    reports: dict[str, list[dict[str, Any]]] = {}
    for case in analysis.get("per_apk_rows", []):
        case_id = str(case.get("case_id") or "")
        report_path = Path(str(case.get("report_path") or ""))
        if not case_id or not report_path.exists():
            continue
        report = _load_json(report_path)
        reports[case_id] = report.get("match_summary", {}).get("decisions", [])
    return reports


def evaluate_version_row(
    row: dict[str, Any],
    *,
    report_cache: dict[str, list[dict[str, Any]]],
    max_score_drop: float,
    min_sibling_era_anchors: int,
) -> dict[str, Any]:
    case_id = str(row.get("case_id") or "")
    coordinate = str(row.get("coordinate") or "")
    decisions = report_cache.get(case_id, [])
    baseline_decision = find_decision(decisions, coordinate)
    apk_only_decision = build_apk_only_decision(
        coordinate=coordinate,
        baseline_decision=baseline_decision,
        sibling_decisions=decisions,
        max_score_drop=max_score_drop,
        min_sibling_era_anchors=min_sibling_era_anchors,
    )
    source_available = source_version_in_baseline_alternatives(row, baseline_decision)
    return {
        "case_id": row.get("case_id"),
        "case_name": row.get("case_name"),
        "case_role": row.get("case_role"),
        "analysis_class": row.get("analysis_class"),
        "coordinate": coordinate,
        "baseline_selected_version": row.get("tool_selected_version"),
        "source_versions": split_versions(row.get("correct_source_versions")),
        "baseline_confidence": row.get("confidence"),
        "apk_only_decision": apk_only_decision,
        "evaluation": evaluate_apk_only_decision(
            row,
            apk_only_decision,
            source_version_in_baseline_alternatives=source_available,
        ),
        "report_only": True,
        "production_promotion": False,
    }


def build_apk_only_decision(
    *,
    coordinate: str,
    baseline_decision: dict[str, Any] | None,
    sibling_decisions: list[dict[str, Any]],
    max_score_drop: float,
    min_sibling_era_anchors: int,
) -> dict[str, Any]:
    if not baseline_decision:
        return no_change("no-baseline-decision")

    selected_version = str(baseline_decision.get("selected_version") or "")
    selected_era = version_era(selected_version)
    family = family_key(coordinate)
    sibling_eras = [
        version_era(decision.get("selected_version"))
        for decision in sibling_decisions
        if decision.get("coordinate") != coordinate
        and family_key(str(decision.get("coordinate") or "")) == family
    ]
    era_counts = Counter(era for era in sibling_eras if era)
    if not era_counts:
        return no_change("no-sibling-era-anchors", selected_version=selected_version)

    dominant_era, dominant_count = era_counts.most_common(1)[0]
    second_count = era_counts.most_common(2)[1][1] if len(era_counts) > 1 else 0
    if dominant_count < min_sibling_era_anchors:
        return no_change(
            "insufficient-sibling-era-anchors",
            selected_version=selected_version,
            sibling_era_counts=era_counts,
            dominant_era=dominant_era,
        )
    if dominant_count == second_count:
        return no_change(
            "no-unique-dominant-sibling-era",
            selected_version=selected_version,
            sibling_era_counts=era_counts,
            dominant_era=dominant_era,
        )
    if selected_era == dominant_era:
        return no_change(
            "selected-version-already-matches-dominant-era",
            selected_version=selected_version,
            sibling_era_counts=era_counts,
            dominant_era=dominant_era,
        )

    selected_score = _float(baseline_decision.get("score"))
    candidates: list[dict[str, Any]] = []
    for alternative in baseline_decision.get("alternatives", []):
        alternative_version = str(alternative.get("version") or "")
        alternative_score = _float(alternative.get("score"))
        score_drop = selected_score - alternative_score
        if version_era(alternative_version) != dominant_era:
            continue
        if score_drop > max_score_drop:
            continue
        candidates.append(
            {
                "version": alternative_version,
                "score": _round(alternative_score),
                "score_drop": _round(score_drop),
                "purl": alternative.get("purl"),
            }
        )

    if not candidates:
        return no_change(
            "no-baseline-alternative-matches-dominant-era-within-score-drop",
            selected_version=selected_version,
            sibling_era_counts=era_counts,
            dominant_era=dominant_era,
        )

    candidate = max(candidates, key=lambda item: float(item["score"] or 0.0))
    return {
        "would_change": True,
        "reason": "sibling-era-anchor-rerank",
        "selected_version": selected_version,
        "suggested_version": candidate["version"],
        "selected_era": selected_era,
        "suggested_era": dominant_era,
        "dominant_sibling_era": dominant_era,
        "sibling_era_counts": dict(sorted(era_counts.items())),
        "candidate": candidate,
        "reason_codes": [
            "source-free-sibling-era-anchor",
            "same-coordinate-baseline-alternative",
            "within-score-drop-threshold",
        ],
    }


def evaluate_apk_only_decision(
    row: dict[str, Any],
    apk_only_decision: dict[str, Any],
    *,
    source_version_in_baseline_alternatives: bool,
) -> dict[str, Any]:
    analysis_class = str(row.get("analysis_class") or "")
    source_versions = set(split_versions(row.get("correct_source_versions")))
    suggested = str(apk_only_decision.get("suggested_version") or "")
    if not apk_only_decision.get("would_change"):
        if analysis_class == "wrong-version":
            classification = "wrong-version-no-apk-only-change"
        elif analysis_class == "true-positive-exact-version":
            classification = "exact-control-stays-unchanged"
        elif analysis_class == "false-positive-extra-emission":
            classification = "false-positive-control-stays-unchanged"
        else:
            classification = "unchanged-other"
    elif analysis_class == "wrong-version" and suggested in source_versions:
        classification = "apk-only-rerank-would-fix"
    elif analysis_class == "wrong-version":
        classification = "apk-only-rerank-wrong-to-wrong"
    elif analysis_class == "true-positive-exact-version" and suggested in source_versions:
        classification = "apk-only-rerank-control-still-source"
    elif analysis_class == "true-positive-exact-version":
        classification = "apk-only-rerank-regresses-exact-control"
    elif analysis_class == "false-positive-extra-emission":
        classification = "apk-only-rerank-changes-false-positive-control"
    else:
        classification = "apk-only-rerank-other"

    return {
        "classification": classification,
        "source_version_in_baseline_alternatives": source_version_in_baseline_alternatives,
        "uses_source_for_decision": False,
    }


def source_version_in_baseline_alternatives(
    row: dict[str, Any],
    baseline_decision: dict[str, Any] | None,
) -> bool:
    source_versions = set(split_versions(row.get("correct_source_versions")))
    if not source_versions or not baseline_decision:
        return False
    return any(
        str(alternative.get("version") or "") in source_versions
        for alternative in baseline_decision.get("alternatives", [])
    )


def summarize_rows(
    rows: list[dict[str, Any]],
    *,
    analysis: dict[str, Any],
    version_band_coordinates: set[str],
) -> dict[str, Any]:
    classes = Counter(row["analysis_class"] for row in rows)
    evaluations = Counter(row["evaluation"]["classification"] for row in rows)
    changed_rows = [row for row in rows if row["apk_only_decision"]["would_change"]]
    wrong_rows = [row for row in rows if row["analysis_class"] == "wrong-version"]
    source_available = [
        row
        for row in wrong_rows
        if row["evaluation"]["source_version_in_baseline_alternatives"]
    ]
    return {
        "version_band_coordinates": len(version_band_coordinates),
        "rows_evaluated": len(rows),
        "row_class_counts": dict(sorted(classes.items())),
        "classification_counts": dict(sorted(evaluations.items())),
        "apk_only_reranker_changes": len(changed_rows),
        "apk_only_wrong_version_fixes": evaluations.get("apk-only-rerank-would-fix", 0),
        "apk_only_wrong_to_wrong_changes": evaluations.get(
            "apk-only-rerank-wrong-to-wrong",
            0,
        ),
        "apk_only_exact_control_regressions": evaluations.get(
            "apk-only-rerank-regresses-exact-control",
            0,
        ),
        "apk_only_false_positive_control_changes": evaluations.get(
            "apk-only-rerank-changes-false-positive-control",
            0,
        ),
        "wrong_version_rows_in_scope": len(wrong_rows),
        "wrong_version_rows_with_source_in_baseline_alternatives": len(source_available),
        "wrong_version_source_candidate_availability_percent": _percent(
            len(source_available),
            len(wrong_rows),
        ),
        "total_baseline_wrong_version_rows": int(
            analysis.get("summary", {}).get("baseline_emitted_wrong_version") or 0
        ),
        "report_only": True,
        "production_promotion": False,
    }


def verdict(summary: dict[str, Any]) -> str:
    if summary["apk_only_exact_control_regressions"]:
        return "reject-apk-only-reranker-regresses-exact-controls"
    if summary["apk_only_false_positive_control_changes"]:
        return "reject-apk-only-reranker-changes-false-positive-controls"
    if summary["apk_only_wrong_version_fixes"]:
        return "apk-only-reranker-promising-needs-expanded-controls"
    return "reject-apk-only-reranker-no-safe-fixes"


def write_outputs(
    payload: dict[str, Any],
    *,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_doc: str | Path = DEFAULT_OUTPUT_DOC,
) -> dict[str, Any]:
    json_path = Path(output_json)
    doc_path = Path(output_doc)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(build_markdown(payload), encoding="utf-8")
    summary = payload["summary"]
    return {
        "json": normalize_path(json_path),
        "doc": normalize_path(doc_path),
        "verdict": payload["verdict"],
        "apk_only_reranker_changes": summary["apk_only_reranker_changes"],
        "apk_only_wrong_version_fixes": summary["apk_only_wrong_version_fixes"],
        "apk_only_exact_control_regressions": summary[
            "apk_only_exact_control_regressions"
        ],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# APK-Only Version-Band Reranker V2",
        "",
        "Generated by `apk-sbom version-band-apk-reranker` or `scripts/build_version_band_apk_reranker.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Guardrails",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Thresholds",
            "",
            f"- Maximum allowed score drop: `{payload['thresholds']['max_score_drop']}`",
            f"- Minimum sibling era anchors: `{payload['thresholds']['min_sibling_era_anchors']}`",
            "- Requires unique dominant sibling era: `true`",
            "",
            "## Summary",
            "",
            f"- Rows evaluated: `{summary['rows_evaluated']}`",
            f"- Version-band coordinates: `{summary['version_band_coordinates']}`",
            f"- Row classes: `{json.dumps(summary['row_class_counts'], sort_keys=True)}`",
            f"- APK-only reranker changes: `{summary['apk_only_reranker_changes']}`",
            f"- APK-only wrong-version fixes: `{summary['apk_only_wrong_version_fixes']}`",
            f"- APK-only wrong-to-wrong changes: `{summary['apk_only_wrong_to_wrong_changes']}`",
            f"- APK-only exact-control regressions: `{summary['apk_only_exact_control_regressions']}`",
            f"- APK-only false-positive control changes: `{summary['apk_only_false_positive_control_changes']}`",
            f"- Wrong-version rows with source in baseline alternatives: `{summary['wrong_version_rows_with_source_in_baseline_alternatives']}` / `{summary['wrong_version_rows_in_scope']}` (`{summary['wrong_version_source_candidate_availability_percent']}%`)",
            "",
            "## Classification Counts",
            "",
            "| Classification | Rows |",
            "|---|---:|",
        ]
    )
    for key, value in summary["classification_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Top Changed Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    for row in payload["top_change_coordinates"]:
        lines.append(f"| `{row['key']}` | {row['rows']} |")
    if not payload["top_change_coordinates"]:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Top Source-Candidate-Available Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    for row in payload["top_source_candidate_available_coordinates"]:
        lines.append(f"| `{row['key']}` | {row['rows']} |")
    if not payload["top_source_candidate_available_coordinates"]:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The source-known experiment showed a large opportunity, but this APK-only prototype does not safely capture it. With the current baseline reports, most wrong-version rows do not expose the source version as an APK-only same-coordinate alternative, and the strict sibling-era heuristic does not have enough independent support to fire safely.",
            "",
            "The honest next step is not promotion. The next matcher-improvement work should expand independent same-coordinate candidate evidence and add stronger features, such as version-unique literals, dependency-era coherence, and structural similarity, before retrying APK-only reranking.",
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for key, value in sorted(payload["sources"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def find_decision(
    decisions: list[dict[str, Any]],
    coordinate: str,
) -> dict[str, Any] | None:
    for decision in decisions:
        if decision.get("coordinate") == coordinate:
            return decision
    return None


def no_change(
    reason: str,
    *,
    selected_version: str | None = None,
    sibling_era_counts: Counter | None = None,
    dominant_era: str | None = None,
) -> dict[str, Any]:
    return {
        "would_change": False,
        "reason": reason,
        "selected_version": selected_version,
        "suggested_version": None,
        "dominant_sibling_era": dominant_era,
        "sibling_era_counts": dict(sorted((sibling_era_counts or Counter()).items())),
        "reason_codes": [reason],
    }


def family_key(coordinate: str) -> str:
    group = coordinate.split(":", 1)[0]
    if group.startswith("androidx."):
        return group
    if group in {"org.jetbrains.kotlin", "org.jetbrains.kotlinx"}:
        return group
    if group.startswith("com.google.android.material"):
        return group
    if group.startswith("com.squareup."):
        return group
    return group


def version_era(version: Any) -> str | None:
    numbers = re.findall(r"\d+", str(version or ""))[:2]
    if not numbers:
        return None
    return ".".join((numbers + ["0", "0"])[:2])


def split_versions(value: Any) -> list[str]:
    return [
        version.strip()
        for version in str(value or "").replace(",", ";").split(";")
        if version.strip()
    ]


def _load_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        return {}
    return json.loads(source.read_text(encoding="utf-8"))


def _top_counts(counter: Counter, *, limit: int) -> list[dict[str, Any]]:
    return [
        {"key": str(key), "rows": count}
        for key, count in counter.most_common(limit)
    ]


def _float(value: Any) -> float:
    try:
        if value in (None, ""):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _round(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return round(float(value), 6)
    except (TypeError, ValueError):
        return None


def _percent(part: int, whole: int) -> float:
    if not whole:
        return 0.0
    return round((part / whole) * 100, 1)


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")
