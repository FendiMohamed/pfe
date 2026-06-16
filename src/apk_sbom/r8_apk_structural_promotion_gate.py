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
    "data/results/experiments/r8-apk-structural-promotion-gate.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_APK_STRUCTURAL_PROMOTION_GATE.md")

DEFAULT_MIN_OPCODE_SCORE = 0.90
DEFAULT_MIN_LITERAL_SCORE = 0.50
DEFAULT_MIN_DEPENDENCY_SCORE = 0.30
DEFAULT_MAX_NAME_SCORE = 0.30
DEFAULT_MIN_IDENTITY_CONFIDENCE = 0.0

THRESHOLD_SWEEP_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "name": "balanced-apk-only",
        "min_opcode_score": 0.90,
        "min_literal_score": 0.50,
        "min_dependency_score": 0.30,
        "max_name_score": 0.30,
        "min_identity_confidence": 0.0,
    },
    {
        "name": "literal-dependency-strict",
        "min_opcode_score": 0.90,
        "min_literal_score": 0.60,
        "min_dependency_score": 0.40,
        "max_name_score": 0.30,
        "min_identity_confidence": 0.0,
    },
    {
        "name": "very-high-opcode",
        "min_opcode_score": 0.95,
        "min_literal_score": 0.50,
        "min_dependency_score": 0.30,
        "max_name_score": 0.30,
        "min_identity_confidence": 0.0,
    },
    {
        "name": "triple-strict",
        "min_opcode_score": 0.92,
        "min_literal_score": 0.60,
        "min_dependency_score": 0.40,
        "max_name_score": 0.25,
        "min_identity_confidence": 0.0,
    },
)


def build_payload(
    *,
    router_json: str | Path = DEFAULT_ROUTER_JSON,
    large_analysis_json: str | Path = DEFAULT_LARGE_ANALYSIS_JSON,
    ai_suggestions_json: str | Path = DEFAULT_AI_SUGGESTIONS_JSON,
    min_opcode_score: float = DEFAULT_MIN_OPCODE_SCORE,
    min_literal_score: float = DEFAULT_MIN_LITERAL_SCORE,
    min_dependency_score: float = DEFAULT_MIN_DEPENDENCY_SCORE,
    max_name_score: float = DEFAULT_MAX_NAME_SCORE,
    min_identity_confidence: float = DEFAULT_MIN_IDENTITY_CONFIDENCE,
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
    thresholds = {
        "min_opcode_score": min_opcode_score,
        "min_literal_score": min_literal_score,
        "min_dependency_score": min_dependency_score,
        "max_name_score": max_name_score,
        "min_identity_confidence": min_identity_confidence,
    }
    evaluated_rows = [
        evaluate_router_row(
            row,
            ai_rows=ai_index.get(_row_key(row), []),
            controls=controls.get(str(row.get("coordinate") or ""), empty_controls()),
            thresholds=thresholds,
        )
        for row in router_rows
    ]
    threshold_sweeps = [
        summarize_threshold_profile(
            router_rows,
            ai_index=ai_index,
            controls=controls,
            thresholds=profile,
        )
        for profile in THRESHOLD_SWEEP_PROFILES
    ]
    summary = build_summary(
        router_rows=router_rows,
        evaluated_rows=evaluated_rows,
        structural_coordinates=structural_coordinates,
        controls=controls,
    )
    return {
        "schema_version": "r8-apk-structural-promotion-gate-v1",
        "report_only": True,
        "default_matcher_unchanged": True,
        "production_promotion": False,
        "verdict": verdict(summary),
        "scope": (
            "APK-only structural promotion gate for the R8 structural recall lane. "
            "The candidate queue comes from source-validated matcher-recall diagnostics, "
            "but the pass/block gate uses only APK-side scores, AI triage status, and "
            "post-decision control evidence. Source versions are used only after the "
            "decision to grade whether a gated candidate would have been correct."
        ),
        "thresholds": thresholds,
        "policy": [
            "Do not use source versions to pass the APK-only structural gate.",
            "Require strong opcode evidence plus literal/dependency support while class and method names are weak.",
            "Treat AI as triage evidence only; AI cannot emit a component or confirm a version.",
            "Block production promotion when the same coordinate has wrong-version or false-positive emitted controls.",
            "Block production promotion when a zero-risk coordinate has no representative exact emitted control.",
            "Use source truth only after the gate fires to label evaluation outcomes.",
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
        "threshold_sweeps": threshold_sweeps,
        "top_gate_pass_coordinates": _top_counts(
            Counter(
                row["coordinate"]
                for row in evaluated_rows
                if row["apk_only_gate"]["passes"]
            ),
            limit=20,
        ),
        "top_control_risk_coordinates": control_risk_top_counts(controls, limit=20),
        "top_zero_risk_no_exact_control_coordinates": _top_counts(
            Counter(
                row["coordinate"]
                for row in evaluated_rows
                if row["classification"] == "blocked-no-representative-exact-control"
            ),
            limit=20,
        ),
        "rows": evaluated_rows,
    }


def build_control_index(
    version_rows: list[dict[str, Any]],
    *,
    structural_coordinates: set[str],
) -> dict[str, dict[str, Any]]:
    controls: dict[str, dict[str, Any]] = defaultdict(empty_control_accumulator)
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
        if row.get("case_role"):
            bucket["case_role_counts"][str(row.get("case_role"))] += 1
    return {
        coordinate: finalize_controls(values)
        for coordinate, values in controls.items()
    }


def empty_control_accumulator() -> dict[str, Any]:
    return {
        "exact_controls": 0,
        "wrong_version_controls": 0,
        "false_positive_controls": 0,
        "case_ids": set(),
        "case_role_counts": Counter(),
    }


def empty_controls() -> dict[str, Any]:
    return {
        "exact_controls": 0,
        "wrong_version_controls": 0,
        "false_positive_controls": 0,
        "control_risk_rows": 0,
        "case_ids": [],
        "case_role_counts": {},
    }


def finalize_controls(values: dict[str, Any]) -> dict[str, Any]:
    wrong = int(values.get("wrong_version_controls", 0) or 0)
    false_positive = int(values.get("false_positive_controls", 0) or 0)
    return {
        "exact_controls": int(values.get("exact_controls", 0) or 0),
        "wrong_version_controls": wrong,
        "false_positive_controls": false_positive,
        "control_risk_rows": wrong + false_positive,
        "case_ids": sorted(values.get("case_ids", set())),
        "case_role_counts": dict(sorted(values.get("case_role_counts", Counter()).items())),
    }


def build_ai_index(
    suggestions: list[dict[str, Any]],
) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
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
    features = extract_features(row)
    ai_summary = summarize_ai_rows(ai_rows, row)
    gate = apk_only_gate_decision(features, ai_summary, thresholds)
    source_evaluation = evaluate_source_outcome(row, gate)
    classification, promotion_candidate, reason = classify_candidate(
        gate,
        controls=controls,
        source_evaluation=source_evaluation,
    )
    return {
        "row_id": row.get("row_id"),
        "case_id": row.get("case_id"),
        "app": row.get("app"),
        "coordinate": row.get("coordinate"),
        "source_version": row.get("source_version"),
        "candidate_version": row.get("candidate_version"),
        "priority": row.get("priority"),
        "classification": classification,
        "classification_reason": reason,
        "apk_only_gate": gate,
        "source_evaluation": source_evaluation,
        "control_context": controls,
        "ai_summary": ai_summary,
        "features": features,
        "report_only": True,
        "production_promotion": False,
        "production_promotion_candidate": promotion_candidate,
    }


def extract_features(row: dict[str, Any]) -> dict[str, Any]:
    evidence = row.get("evidence", {})
    class_score = _float(evidence.get("class_score"))
    method_score = _float(evidence.get("method_score"))
    return {
        "best_score": _round(evidence.get("best_score")),
        "source_score": _round(evidence.get("source_score")),
        "score_gap_to_best": _round(evidence.get("score_gap_to_best")),
        "identity_confidence": _round(evidence.get("identity_confidence")),
        "package_score": _round(evidence.get("package_score")),
        "class_score": _round(class_score),
        "method_score": _round(method_score),
        "name_score": _round(max(class_score, method_score)),
        "opcode_score": _round(evidence.get("opcode_score")),
        "literal_score": _round(evidence.get("literal_score")),
        "dependency_score": _round(evidence.get("dependency_score")),
        "recall_status": evidence.get("recall_status"),
        "next_action": evidence.get("next_action"),
        "r8_obfuscation_profile": evidence.get("r8_obfuscation_profile"),
    }


def summarize_ai_rows(
    ai_rows: list[dict[str, Any]],
    row: dict[str, Any],
) -> dict[str, Any]:
    evidence = row.get("evidence", {})
    recommendations = {
        str(ai_row.get("recommendation") or "")
        for ai_row in ai_rows
        if ai_row.get("recommendation")
    }
    if evidence.get("ai_recommendation"):
        recommendations.add(str(evidence.get("ai_recommendation")))
    confidences = [_float(ai_row.get("confidence")) for ai_row in ai_rows]
    return {
        "recommendations": sorted(recommendations),
        "max_confidence": _round(max(confidences, default=0.0)),
        "suggest_report_only": "suggest_report_only" in recommendations,
        "risk_only": "risk_only" in recommendations,
        "suppress_uncertain": "suppress_uncertain" in recommendations,
        "report_only": True,
    }


def apk_only_gate_decision(
    features: dict[str, Any],
    ai_summary: dict[str, Any],
    thresholds: dict[str, float],
) -> dict[str, Any]:
    failures: list[str] = []
    passes: list[str] = []
    opcode = _float(features.get("opcode_score"))
    literal = _float(features.get("literal_score"))
    dependency = _float(features.get("dependency_score"))
    name_score = _float(features.get("name_score"))
    identity = _float(features.get("identity_confidence"))
    if opcode >= thresholds["min_opcode_score"]:
        passes.append("strong-opcode")
    else:
        failures.append("opcode-below-threshold")
    if literal >= thresholds["min_literal_score"]:
        passes.append("literal-support")
    else:
        failures.append("literal-below-threshold")
    if dependency >= thresholds["min_dependency_score"]:
        passes.append("dependency-support")
    else:
        failures.append("dependency-below-threshold")
    if name_score <= thresholds["max_name_score"]:
        passes.append("weak-class-method-names")
    else:
        failures.append("name-signal-too-strong-for-r8-structural-profile")
    if identity >= thresholds["min_identity_confidence"]:
        passes.append("identity-floor")
    else:
        failures.append("identity-confidence-below-floor")
    if ai_summary.get("suppress_uncertain"):
        failures.append("ai-suppress-uncertain")
    elif ai_summary.get("risk_only"):
        passes.append("ai-risk-only-warning")
    elif ai_summary.get("suggest_report_only"):
        passes.append("ai-report-only-support")
    passed = not failures
    return {
        "passes": passed,
        "uses_source_for_decision": False,
        "thresholds": thresholds,
        "passed_signals": passes,
        "failed_signals": failures,
        "decision": "pass-apk-only-structural-gate" if passed else "block-apk-only-evidence",
    }


def evaluate_source_outcome(
    row: dict[str, Any],
    gate: dict[str, Any],
) -> dict[str, Any]:
    source_versions = split_versions(row.get("source_version"))
    candidate = str(row.get("candidate_version") or "")
    matches = bool(candidate and candidate in source_versions)
    if not gate.get("passes"):
        classification = "not-evaluated-gate-blocked"
    elif matches:
        classification = "posthoc-source-exact"
    else:
        classification = "posthoc-source-mismatch"
    return {
        "classification": classification,
        "candidate_matches_source": matches,
        "candidate_version": candidate,
        "source_versions": source_versions,
        "uses_source_for_gate_decision": False,
    }


def classify_candidate(
    gate: dict[str, Any],
    *,
    controls: dict[str, Any],
    source_evaluation: dict[str, Any],
) -> tuple[str, bool, str]:
    if not gate.get("passes"):
        return (
            "blocked-apk-only-evidence",
            False,
            "APK-side evidence does not satisfy the structural gate.",
        )
    if not source_evaluation.get("candidate_matches_source"):
        return (
            "blocked-posthoc-source-mismatch",
            False,
            "The APK-only gate would have selected a candidate that disagrees with source truth.",
        )
    if int(controls.get("control_risk_rows", 0) or 0):
        return (
            "blocked-same-coordinate-control-risk",
            False,
            "Same-coordinate emitted controls still include wrong-version or false-positive rows.",
        )
    if not int(controls.get("exact_controls", 0) or 0):
        return (
            "blocked-no-representative-exact-control",
            False,
            "No same-coordinate exact emitted control exists to justify production promotion.",
        )
    return (
        "promotion-candidate-needs-live-default-test",
        True,
        "APK-only evidence passes and same-coordinate controls are clean; a live matcher change would still need full regression tests.",
    )


def summarize_threshold_profile(
    router_rows: list[dict[str, Any]],
    *,
    ai_index: dict[tuple[str, str, str], list[dict[str, Any]]],
    controls: dict[str, dict[str, Any]],
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    profile_thresholds = {
        key: float(value)
        for key, value in thresholds.items()
        if key != "name"
    }
    rows = [
        evaluate_router_row(
            row,
            ai_rows=ai_index.get(_row_key(row), []),
            controls=controls.get(str(row.get("coordinate") or ""), empty_controls()),
            thresholds=profile_thresholds,
        )
        for row in router_rows
    ]
    gate_passed = [row for row in rows if row["apk_only_gate"]["passes"]]
    classifications = Counter(row["classification"] for row in rows)
    return {
        "name": str(thresholds["name"]),
        "thresholds": profile_thresholds,
        "gate_pass_rows": len(gate_passed),
        "gate_pass_coordinates": len({row["coordinate"] for row in gate_passed}),
        "posthoc_source_exact_gate_pass_rows": sum(
            1
            for row in gate_passed
            if row["source_evaluation"]["candidate_matches_source"]
        ),
        "blocked_same_coordinate_control_risk": classifications.get(
            "blocked-same-coordinate-control-risk",
            0,
        ),
        "blocked_no_representative_exact_control": classifications.get(
            "blocked-no-representative-exact-control",
            0,
        ),
        "promotion_candidates": classifications.get(
            "promotion-candidate-needs-live-default-test",
            0,
        ),
    }


def build_summary(
    *,
    router_rows: list[dict[str, Any]],
    evaluated_rows: list[dict[str, Any]],
    structural_coordinates: set[str],
    controls: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    classifications = Counter(row["classification"] for row in evaluated_rows)
    gate_pass_rows = [row for row in evaluated_rows if row["apk_only_gate"]["passes"]]
    gate_fail_rows = [row for row in evaluated_rows if not row["apk_only_gate"]["passes"]]
    control_totals = Counter()
    for control in controls.values():
        control_totals["exact"] += int(control.get("exact_controls", 0) or 0)
        control_totals["wrong"] += int(control.get("wrong_version_controls", 0) or 0)
        control_totals["false_positive"] += int(
            control.get("false_positive_controls", 0) or 0
        )
    promotion_candidates = classifications.get(
        "promotion-candidate-needs-live-default-test",
        0,
    )
    return {
        "router_r8_structural_rows": len(router_rows),
        "router_r8_structural_coordinates": len(structural_coordinates),
        "gate_pass_rows": len(gate_pass_rows),
        "gate_fail_rows": len(gate_fail_rows),
        "gate_pass_coordinates": len({row["coordinate"] for row in gate_pass_rows}),
        "posthoc_source_exact_gate_pass_rows": sum(
            1
            for row in gate_pass_rows
            if row["source_evaluation"]["candidate_matches_source"]
        ),
        "blocked_same_coordinate_control_risk": classifications.get(
            "blocked-same-coordinate-control-risk",
            0,
        ),
        "blocked_no_representative_exact_control": classifications.get(
            "blocked-no-representative-exact-control",
            0,
        ),
        "blocked_apk_only_evidence": classifications.get(
            "blocked-apk-only-evidence",
            0,
        ),
        "blocked_posthoc_source_mismatch": classifications.get(
            "blocked-posthoc-source-mismatch",
            0,
        ),
        "promotion_candidates": promotion_candidates,
        "same_coordinate_exact_controls": control_totals["exact"],
        "same_coordinate_wrong_version_controls": control_totals["wrong"],
        "same_coordinate_false_positive_controls": control_totals["false_positive"],
        "same_coordinate_control_risk_rows": (
            control_totals["wrong"] + control_totals["false_positive"]
        ),
        "classification_counts": dict(sorted(classifications.items())),
        "report_only": True,
        "production_promotion": False,
        "candidate_pool_caveat": (
            "The row queue is built from source-validated matcher-recall diagnostics. "
            "The gate itself is source-free, but production promotion still needs an "
            "independent live matcher candidate generator."
        ),
        "promotion_blockers": promotion_blockers(classifications),
    }


def promotion_blockers(classifications: Counter) -> list[str]:
    blockers: list[str] = []
    if classifications.get("blocked-same-coordinate-control-risk", 0):
        blockers.append(
            "Same-coordinate emitted controls still contain wrong-version or false-positive rows."
        )
    if classifications.get("blocked-no-representative-exact-control", 0):
        blockers.append(
            "Many zero-risk gate passes have no representative exact emitted control."
        )
    if classifications.get("blocked-posthoc-source-mismatch", 0):
        blockers.append(
            "At least one source-graded gate pass would choose the wrong version."
        )
    if not classifications.get("promotion-candidate-needs-live-default-test", 0):
        blockers.append(
            "No row currently satisfies the full APK-only evidence plus control-support gate."
        )
    return blockers


def verdict(summary: dict[str, Any]) -> str:
    if summary["promotion_candidates"]:
        return "apk-only-structural-promotion-candidates-need-live-controls"
    if summary["gate_pass_rows"]:
        return "apk-only-structural-gate-blocked-by-controls"
    return "reject-apk-only-structural-gate-no-strong-candidates"


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
        "gate_pass_rows": summary["gate_pass_rows"],
        "promotion_candidates": summary["promotion_candidates"],
        "same_coordinate_control_risk_rows": summary[
            "same_coordinate_control_risk_rows"
        ],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# R8 APK-Only Structural Promotion Gate",
        "",
        "Generated by `apk-sbom r8-apk-structural-promotion-gate` or `scripts/build_r8_apk_structural_promotion_gate.py`.",
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
            f"- Minimum opcode score: `{payload['thresholds']['min_opcode_score']}`",
            f"- Minimum literal score: `{payload['thresholds']['min_literal_score']}`",
            f"- Minimum dependency score: `{payload['thresholds']['min_dependency_score']}`",
            f"- Maximum class/method name score: `{payload['thresholds']['max_name_score']}`",
            f"- Minimum identity confidence: `{payload['thresholds']['min_identity_confidence']}`",
            "",
            "## Summary",
            "",
            f"- Router R8 structural rows: `{summary['router_r8_structural_rows']}`",
            f"- Router R8 structural coordinates: `{summary['router_r8_structural_coordinates']}`",
            f"- APK-only gate pass rows: `{summary['gate_pass_rows']}`",
            f"- APK-only gate pass coordinates: `{summary['gate_pass_coordinates']}`",
            f"- Gate passes that are posthoc source-exact: `{summary['posthoc_source_exact_gate_pass_rows']}`",
            f"- Blocked by same-coordinate control risk: `{summary['blocked_same_coordinate_control_risk']}`",
            f"- Blocked by no representative exact control: `{summary['blocked_no_representative_exact_control']}`",
            f"- Blocked by APK-only evidence: `{summary['blocked_apk_only_evidence']}`",
            f"- Promotion candidates needing live default tests: `{summary['promotion_candidates']}`",
            f"- Same-coordinate exact controls: `{summary['same_coordinate_exact_controls']}`",
            f"- Same-coordinate wrong-version controls: `{summary['same_coordinate_wrong_version_controls']}`",
            f"- Same-coordinate false-positive controls: `{summary['same_coordinate_false_positive_controls']}`",
            f"- Same-coordinate control-risk rows: `{summary['same_coordinate_control_risk_rows']}`",
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
            "## Threshold Sweep",
            "",
            "| Profile | Gate pass rows | Gate pass coordinates | Posthoc source-exact passes | Control-risk blocks | No-exact-control blocks | Promotion candidates |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["threshold_sweeps"]:
        lines.append(
            "| "
            f"`{row['name']}` | "
            f"{row['gate_pass_rows']} | "
            f"{row['gate_pass_coordinates']} | "
            f"{row['posthoc_source_exact_gate_pass_rows']} | "
            f"{row['blocked_same_coordinate_control_risk']} | "
            f"{row['blocked_no_representative_exact_control']} | "
            f"{row['promotion_candidates']} |"
        )
    lines.extend(
        [
            "",
            "## Top Gate-Pass Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    _append_top_counts(lines, payload["top_gate_pass_coordinates"])
    lines.extend(
        [
            "",
            "## Top Same-Coordinate Control Risks",
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
    if not payload["top_control_risk_coordinates"]:
        lines.append("| none | 0 | 0 | 0 | 0 |")
    lines.extend(
        [
            "",
            "## Top Zero-Risk Rows Without Exact Controls",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    _append_top_counts(lines, payload["top_zero_risk_no_exact_control_coordinates"])
    lines.extend(
        [
            "",
            "## Promotion Decision",
            "",
            "This gate is stronger than the earlier source-context R8 structural recall report because the pass/block decision uses APK-side evidence only. However, the current result still does not justify automatic SBOM emission. The strongest rows are useful as transparent report-only evidence and as a prioritized queue for live matcher work, but production promotion remains blocked unless a future live matcher candidate generator passes the same gate and preserves the full 106-APK control matrix.",
            "",
            "Current blockers:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in summary["promotion_blockers"])
    lines.extend(
        [
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


def split_versions(value: Any) -> list[str]:
    return [
        version.strip()
        for version in str(value or "").replace(",", ";").split(";")
        if version.strip()
    ]


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


def _append_top_counts(lines: list[str], rows: list[dict[str, Any]]) -> None:
    for row in rows:
        lines.append(f"| `{row['key']}` | {row['rows']} |")
    if not rows:
        lines.append("| none | 0 |")


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
