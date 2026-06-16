from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any


DEFAULT_ROUTER_JSON = Path("data/results/evaluation/hybrid-matcher-router-v1.json")
DEFAULT_LARGE_ANALYSIS_JSON = Path(
    "data/results/evaluation/large-combined-real-apk-analysis.json"
)
DEFAULT_AI_SUGGESTIONS_JSON = Path(
    "data/results/experiments/ai-r8-assistant/suggestions.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/r8-structural-recall-experiment.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_STRUCTURAL_RECALL_EXPERIMENT.md")

DEFAULT_STRONG_OPCODE_THRESHOLD = 0.75
DEFAULT_WEAK_NAME_THRESHOLD = 0.30
DEFAULT_DEPENDENCY_SUPPORT_THRESHOLD = 0.30
DEFAULT_LITERAL_SUPPORT_THRESHOLD = 0.50
DEFAULT_HIGH_OPCODE_THRESHOLD = 0.85


def build_payload(
    *,
    router_json: str | Path = DEFAULT_ROUTER_JSON,
    large_analysis_json: str | Path = DEFAULT_LARGE_ANALYSIS_JSON,
    ai_suggestions_json: str | Path = DEFAULT_AI_SUGGESTIONS_JSON,
    strong_opcode_threshold: float = DEFAULT_STRONG_OPCODE_THRESHOLD,
    weak_name_threshold: float = DEFAULT_WEAK_NAME_THRESHOLD,
    dependency_support_threshold: float = DEFAULT_DEPENDENCY_SUPPORT_THRESHOLD,
    literal_support_threshold: float = DEFAULT_LITERAL_SUPPORT_THRESHOLD,
    high_opcode_threshold: float = DEFAULT_HIGH_OPCODE_THRESHOLD,
) -> dict[str, Any]:
    router = _load_json(router_json)
    analysis = _load_json(large_analysis_json)
    ai_suggestions = _load_json(ai_suggestions_json)

    router_rows = [
        row
        for row in router.get("rows", [])
        if row.get("recommended_profile") == "r8-structural-recall"
    ]
    structural_coordinates = {
        str(row.get("coordinate") or "")
        for row in router_rows
        if row.get("coordinate")
    }
    controls = build_control_index(
        analysis.get("version_rows", []),
        structural_coordinates=structural_coordinates,
    )
    ai_index = build_ai_index(ai_suggestions.get("suggestions", []))
    evaluated_rows = [
        evaluate_router_row(
            row,
            ai_rows=ai_index.get(_row_key(row), []),
            controls=controls.get(str(row.get("coordinate") or ""), {}),
            thresholds={
                "strong_opcode": strong_opcode_threshold,
                "weak_name": weak_name_threshold,
                "dependency_support": dependency_support_threshold,
                "literal_support": literal_support_threshold,
                "high_opcode": high_opcode_threshold,
            },
        )
        for row in router_rows
    ]
    summary = build_summary(
        router_rows=router_rows,
        evaluated_rows=evaluated_rows,
        structural_coordinates=structural_coordinates,
        controls=controls,
    )
    return {
        "schema_version": "r8-structural-recall-experiment-v1",
        "report_only": True,
        "default_matcher_unchanged": True,
        "verdict": verdict(summary),
        "scope": (
            "Report-only R8 structural recall experiment. It evaluates the Hybrid "
            "Matcher Router rows where opcode/dependency/literal evidence is strong "
            "while package/class/method names are weak. It can recommend source-context "
            "report wording, but it does not emit SBOM components or versions."
        ),
        "thresholds": {
            "strong_opcode": strong_opcode_threshold,
            "weak_name": weak_name_threshold,
            "dependency_support": dependency_support_threshold,
            "literal_support": literal_support_threshold,
            "high_opcode": high_opcode_threshold,
        },
        "policy": [
            "Use the Hybrid Matcher Router r8-structural-recall profile as the experiment queue.",
            "A candidate must already be a source-context report-only suggestion; this experiment does not invent source evidence.",
            "Structural support can prioritize report wording and matcher-recall investigation only.",
            "The current weighted matcher remains the SBOM authority.",
            "Exact, wrong-version, and false-positive controls in the same coordinate space are counted before any promotion discussion.",
            "Do not promote automatic SBOM emission while wrong-version and false-positive controls remain in scope.",
            "This artifact does not change matcher scoring, selected versions, SBOM output, vulnerability labels, or source-validation metrics.",
        ],
        "sources": {
            "router_json": normalize_path(router_json),
            "large_analysis_json": normalize_path(large_analysis_json),
            "ai_suggestions_json": normalize_path(ai_suggestions_json),
        },
        "summary": summary,
        "classification_counts": dict(
            sorted(Counter(row["classification"] for row in evaluated_rows).items())
        ),
        "top_candidate_coordinates": _top_counts(
            Counter(
                row["coordinate"]
                for row in evaluated_rows
                if row["classification"] == "report-only-structural-recall-candidate"
            ),
            limit=20,
        ),
        "top_blocked_coordinates": _top_counts(
            Counter(
                row["coordinate"]
                for row in evaluated_rows
                if row["classification"] != "report-only-structural-recall-candidate"
            ),
            limit=20,
        ),
        "top_control_risk_coordinates": control_risk_top_counts(controls, limit=20),
        "rows": evaluated_rows,
    }


def build_control_index(
    version_rows: list[dict[str, Any]],
    *,
    structural_coordinates: set[str],
) -> dict[str, dict[str, Any]]:
    controls: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "exact_controls": 0,
            "wrong_version_controls": 0,
            "false_positive_controls": 0,
            "case_ids": set(),
        }
    )
    for row in version_rows:
        coordinate = str(row.get("coordinate") or "")
        if coordinate not in structural_coordinates:
            continue
        bucket = controls[coordinate]
        analysis_class = row.get("analysis_class")
        if analysis_class == "true-positive-exact-version":
            bucket["exact_controls"] += 1
        elif analysis_class == "wrong-version":
            bucket["wrong_version_controls"] += 1
        elif analysis_class == "false-positive-extra-emission":
            bucket["false_positive_controls"] += 1
        if row.get("case_id"):
            bucket["case_ids"].add(str(row.get("case_id")))
    return {
        coordinate: {
            **values,
            "case_ids": sorted(values["case_ids"]),
            "control_risk_rows": values["wrong_version_controls"]
            + values["false_positive_controls"],
        }
        for coordinate, values in controls.items()
    }


def build_ai_index(suggestions: list[dict[str, Any]]) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    index: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in suggestions:
        key = (
            str(row.get("case_id") or ""),
            str(row.get("coordinate") or ""),
            str(row.get("source_version") or ""),
        )
        if key[0] and key[1] and key[2]:
            index[key].append(row)
    return dict(index)


def evaluate_router_row(
    row: dict[str, Any],
    *,
    ai_rows: list[dict[str, Any]],
    controls: dict[str, Any],
    thresholds: dict[str, float],
) -> dict[str, Any]:
    evidence = row.get("evidence", {})
    opcode_score = _float(evidence.get("opcode_score"))
    dependency_score = _float(evidence.get("dependency_score"))
    literal_score = _float(evidence.get("literal_score"))
    class_score = _float(evidence.get("class_score"))
    method_score = _float(evidence.get("method_score"))
    package_score = _float(evidence.get("package_score"))
    identity_confidence = _float(evidence.get("identity_confidence"))
    best_score = _float(evidence.get("best_score"))
    source_score = _float(evidence.get("source_score"))
    score_gap_to_best = _float(evidence.get("score_gap_to_best"))

    ai_recommendations = sorted(
        {
            str(ai_row.get("recommendation") or "")
            for ai_row in ai_rows
            if ai_row.get("recommendation")
        }
    )
    ai_confidence = max((_float(ai_row.get("confidence")) for ai_row in ai_rows), default=0.0)
    structural_signals = structural_signal_codes(
        opcode_score=opcode_score,
        dependency_score=dependency_score,
        literal_score=literal_score,
        class_score=class_score,
        method_score=method_score,
        thresholds=thresholds,
    )
    recall_status = str(evidence.get("recall_status") or "")
    next_action = str(evidence.get("next_action") or "")
    source_version = str(row.get("source_version") or "")
    candidate_version = str(row.get("candidate_version") or "")
    source_context_ready = (
        next_action == "surface-as-source-context-report-only-suggestion"
        and recall_status.startswith("report-only")
    )
    candidate_matches_source = bool(source_version and source_version == candidate_version)
    has_ai_suggest = "suggest_report_only" in ai_recommendations
    has_ai_suppress = "suppress_uncertain" in ai_recommendations
    strong_structural = "strong-opcode" in structural_signals and "weak-class-method-names" in structural_signals

    if not source_context_ready:
        classification = "blocked-suppressed-or-filtered"
        recommendation = "inspect-filter-or-family-suppression"
        reason = "router row is still suppressed/inspection-only, not a source-context report suggestion"
    elif not candidate_matches_source:
        classification = "blocked-candidate-version-not-source"
        recommendation = "block"
        reason = "candidate version does not match the source-context version"
    elif has_ai_suppress:
        classification = "blocked-ai-suppressed"
        recommendation = "block"
        reason = "AI assistant recommends suppressing this uncertain row"
    elif not strong_structural:
        classification = "blocked-insufficient-structural-support"
        recommendation = "block"
        reason = "structural signal does not satisfy the scoped R8 recall profile"
    elif has_ai_suggest:
        classification = "report-only-structural-recall-candidate"
        recommendation = "surface_report_only_structural_recall"
        reason = "source-context row has strong structural evidence and AI report-only support"
    else:
        classification = "report-only-structural-recall-candidate"
        recommendation = "surface_report_only_structural_recall_with_manual_review"
        reason = "source-context row has strong structural evidence; AI did not provide an explicit suppress signal"

    return {
        "row_id": row.get("row_id"),
        "case_id": row.get("case_id"),
        "app": row.get("app"),
        "coordinate": row.get("coordinate"),
        "source_version": source_version,
        "candidate_version": candidate_version,
        "priority": row.get("priority"),
        "classification": classification,
        "recommendation": recommendation,
        "reason": reason,
        "source_context_ready": source_context_ready,
        "candidate_matches_source": candidate_matches_source,
        "structural_signals": structural_signals,
        "ai_recommendations": ai_recommendations,
        "ai_max_confidence": _round(ai_confidence),
        "control_context": {
            "exact_controls": int(controls.get("exact_controls", 0) or 0),
            "wrong_version_controls": int(controls.get("wrong_version_controls", 0) or 0),
            "false_positive_controls": int(controls.get("false_positive_controls", 0) or 0),
            "control_risk_rows": int(controls.get("control_risk_rows", 0) or 0),
        },
        "evidence": {
            "best_score": _round(best_score),
            "source_score": _round(source_score),
            "score_gap_to_best": _round(score_gap_to_best),
            "identity_confidence": _round(identity_confidence),
            "package_score": _round(package_score),
            "class_score": _round(class_score),
            "method_score": _round(method_score),
            "opcode_score": _round(opcode_score),
            "literal_score": _round(literal_score),
            "dependency_score": _round(dependency_score),
            "recall_status": recall_status,
            "next_action": next_action,
            "r8_obfuscation_profile": evidence.get("r8_obfuscation_profile"),
        },
        "report_only": True,
        "production_promotion": False,
    }


def structural_signal_codes(
    *,
    opcode_score: float,
    dependency_score: float,
    literal_score: float,
    class_score: float,
    method_score: float,
    thresholds: dict[str, float],
) -> list[str]:
    signals: list[str] = []
    if opcode_score >= thresholds["strong_opcode"]:
        signals.append("strong-opcode")
    if opcode_score >= thresholds["high_opcode"]:
        signals.append("high-opcode")
    if dependency_score >= thresholds["dependency_support"]:
        signals.append("dependency-support")
    if literal_score >= thresholds["literal_support"]:
        signals.append("literal-support")
    if max(class_score, method_score) < thresholds["weak_name"]:
        signals.append("weak-class-method-names")
    return signals


def build_summary(
    *,
    router_rows: list[dict[str, Any]],
    evaluated_rows: list[dict[str, Any]],
    structural_coordinates: set[str],
    controls: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    classification_counts = Counter(row["classification"] for row in evaluated_rows)
    priority_counts = Counter(str(row.get("priority") or "") for row in evaluated_rows)
    signal_counts = Counter(
        signal for row in evaluated_rows for signal in row.get("structural_signals", [])
    )
    ai_counts = Counter(
        recommendation
        for row in evaluated_rows
        for recommendation in row.get("ai_recommendations", [])
    )
    exact_controls = sum(int(row.get("exact_controls", 0) or 0) for row in controls.values())
    wrong_controls = sum(
        int(row.get("wrong_version_controls", 0) or 0) for row in controls.values()
    )
    false_positive_controls = sum(
        int(row.get("false_positive_controls", 0) or 0) for row in controls.values()
    )
    candidates = classification_counts.get("report-only-structural-recall-candidate", 0)
    suppressed = classification_counts.get("blocked-suppressed-or-filtered", 0)
    return {
        "router_r8_structural_rows": len(router_rows),
        "router_r8_structural_coordinates": len(structural_coordinates),
        "priority_counts": dict(sorted(priority_counts.items())),
        "classification_counts": dict(sorted(classification_counts.items())),
        "report_only_structural_recall_candidates": candidates,
        "blocked_rows": len(evaluated_rows) - candidates,
        "blocked_suppressed_or_filtered_rows": suppressed,
        "ai_recommendation_counts": dict(sorted(ai_counts.items())),
        "structural_signal_counts": dict(sorted(signal_counts.items())),
        "candidate_percent": _percent(candidates, len(evaluated_rows)),
        "exact_control_rows_in_scope": exact_controls,
        "wrong_version_control_rows_in_scope": wrong_controls,
        "false_positive_control_rows_in_scope": false_positive_controls,
        "control_risk_rows_in_scope": wrong_controls + false_positive_controls,
        "report_only": True,
        "production_promotion": False,
        "promotion_blockers": [
            "r8-structural recall rows are matcher-recall/source-context rows, not emitted SBOM components",
            "wrong-version controls remain in the same coordinate space",
            "false-positive extra-emission controls remain in the same coordinate space",
            "source context is used for evaluation/report wording, not APK-only production authority",
        ],
    }


def verdict(summary: dict[str, Any]) -> str:
    if not summary["report_only_structural_recall_candidates"]:
        return "no-structural-recall-report-benefit"
    if summary["control_risk_rows_in_scope"]:
        return "report-only-structural-recall-useful-not-promoted"
    return "structural-recall-promotion-needs-full-controls"


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
        "router_r8_structural_rows": summary["router_r8_structural_rows"],
        "report_only_structural_recall_candidates": summary[
            "report_only_structural_recall_candidates"
        ],
        "control_risk_rows_in_scope": summary["control_risk_rows_in_scope"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# R8 Structural Recall Experiment",
        "",
        "Generated by `apk-sbom r8-structural-recall-experiment` or `scripts/build_r8_structural_recall_experiment.py`.",
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
            "## Summary",
            "",
            f"- Router R8 structural rows: `{summary['router_r8_structural_rows']}`",
            f"- Router R8 structural coordinates: `{summary['router_r8_structural_coordinates']}`",
            f"- Priority counts: `{json.dumps(summary['priority_counts'], sort_keys=True)}`",
            f"- Report-only structural recall candidates: `{summary['report_only_structural_recall_candidates']}` (`{summary['candidate_percent']}%`)",
            f"- Blocked rows: `{summary['blocked_rows']}`",
            f"- Exact controls in same coordinates: `{summary['exact_control_rows_in_scope']}`",
            f"- Wrong-version controls in same coordinates: `{summary['wrong_version_control_rows_in_scope']}`",
            f"- False-positive extra-emission controls in same coordinates: `{summary['false_positive_control_rows_in_scope']}`",
            f"- Control-risk rows in same coordinates: `{summary['control_risk_rows_in_scope']}`",
            "",
            "## Classifications",
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
            "## Structural Signals",
            "",
            "| Signal | Rows |",
            "|---|---:|",
        ]
    )
    for key, value in summary["structural_signal_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## AI Recommendation Overlap",
            "",
            "| Recommendation | Rows |",
            "|---|---:|",
        ]
    )
    for key, value in summary["ai_recommendation_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Top Candidate Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    for row in payload["top_candidate_coordinates"]:
        lines.append(f"| `{row['key']}` | {row['rows']} |")
    lines.extend(
        [
            "",
            "## Top Control-Risk Coordinates",
            "",
            "| Coordinate | Control-risk rows | Wrong-version | False-positive | Exact controls |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in payload["top_control_risk_coordinates"]:
        lines.append(
            "| "
            f"`{row['coordinate']}` | "
            f"{row['control_risk_rows']} | "
            f"{row['wrong_version_controls']} | "
            f"{row['false_positive_controls']} | "
            f"{row['exact_controls']} |"
        )
    lines.extend(
        [
            "",
            "## Promotion Decision",
            "",
            "This lane is useful for transparent recall reporting, not automatic production emission. The candidate rows are source-context report-only rows: they help explain hard R8/minified or structurally matched libraries that the default matcher did not emit. They do not prove that the APK-only matcher can safely add those components without source context.",
            "",
            "Promotion remains blocked because the same coordinate space still contains wrong-version and false-positive controls. A future production matcher change would need independent APK-side structural evidence, no source-context dependency, exact-control preservation, and false-positive controls at zero.",
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for key, value in sorted(payload["sources"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def control_risk_top_counts(
    controls: dict[str, dict[str, Any]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    rows = []
    for coordinate, values in controls.items():
        risk = int(values.get("control_risk_rows", 0) or 0)
        if not risk:
            continue
        rows.append(
            {
                "coordinate": coordinate,
                "control_risk_rows": risk,
                "wrong_version_controls": int(values.get("wrong_version_controls", 0) or 0),
                "false_positive_controls": int(values.get("false_positive_controls", 0) or 0),
                "exact_controls": int(values.get("exact_controls", 0) or 0),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -row["control_risk_rows"],
            -row["wrong_version_controls"],
            row["coordinate"],
        ),
    )[:limit]


def _row_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("case_id") or ""),
        str(row.get("coordinate") or ""),
        str(row.get("source_version") or ""),
    )


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


def _percent(part: int, whole: int) -> float:
    if not whole:
        return 0.0
    return round((part / whole) * 100, 1)


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


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")
