from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any


DEFAULT_ROUTER_JSON = Path("data/results/evaluation/hybrid-matcher-router-v1.json")
DEFAULT_LARGE_ANALYSIS_JSON = Path(
    "data/results/evaluation/large-combined-real-apk-analysis.json"
)
DEFAULT_V2_DASHBOARD_JSON = Path(
    "data/results/evaluation/real-apk-demo-final-large-v2-source-version-dashboard.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/version-band-rerank-experiment.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/VERSION_BAND_RERANK_EXPERIMENT.md")


def build_payload(
    *,
    router_json: str | Path = DEFAULT_ROUTER_JSON,
    large_analysis_json: str | Path = DEFAULT_LARGE_ANALYSIS_JSON,
    v2_dashboard_json: str | Path = DEFAULT_V2_DASHBOARD_JSON,
) -> dict[str, Any]:
    router = _load_json(router_json)
    analysis = _load_json(large_analysis_json)
    v2_dashboard = _load_json(v2_dashboard_json)
    v2_reports = _load_v2_reports(v2_dashboard)

    router_rows = [
        row
        for row in router.get("rows", [])
        if row.get("recommended_profile") == "version-band-rerank"
    ]
    version_band_coordinates = {
        str(row.get("coordinate") or "")
        for row in router_rows
        if row.get("coordinate")
    }

    wrong_rows: list[dict[str, Any]] = []
    exact_control_rows: list[dict[str, Any]] = []
    false_positive_control_rows: list[dict[str, Any]] = []
    for row in analysis.get("version_rows", []):
        if str(row.get("coordinate") or "") not in version_band_coordinates:
            continue
        analysis_class = row.get("analysis_class")
        if analysis_class == "wrong-version":
            wrong_rows.append(
                evaluate_wrong_version_row(row, v2_reports=v2_reports)
            )
        elif analysis_class == "true-positive-exact-version":
            exact_control_rows.append(
                evaluate_exact_control_row(row, v2_reports=v2_reports)
            )
        elif analysis_class == "false-positive-extra-emission":
            false_positive_control_rows.append(evaluate_false_positive_control_row(row))

    matcher_recall_rows = [
        summarize_router_row(row)
        for row in router_rows
        if row.get("row_source") == "matcher-recall"
    ]
    source_gap_rows = [
        summarize_router_row(row)
        for row in router_rows
        if row.get("row_source") == "source-gap"
    ]
    wrong_router_rows = [
        summarize_router_row(row)
        for row in router_rows
        if str(row.get("row_source") or "").startswith("wrong-version")
    ]
    summary = build_summary(
        router_rows=router_rows,
        version_band_coordinates=version_band_coordinates,
        wrong_rows=wrong_rows,
        exact_control_rows=exact_control_rows,
        false_positive_control_rows=false_positive_control_rows,
        matcher_recall_rows=matcher_recall_rows,
        source_gap_rows=source_gap_rows,
        wrong_router_rows=wrong_router_rows,
        total_wrong_rows=int(
            analysis.get("summary", {}).get("baseline_emitted_wrong_version") or 0
        ),
    )
    return {
        "schema_version": "version-band-rerank-experiment-v1",
        "report_only": True,
        "default_matcher_unchanged": True,
        "verdict": verdict(summary),
        "scope": (
            "Report-only source-known version-band rerank experiment. It inspects "
            "current wrong-version rows and source-known v2 controls, but does not "
            "change matcher scoring, selected versions, SBOM output, vulnerability "
            "labels, or source-validation metrics."
        ),
        "policy": [
            "Use the Hybrid Matcher Router version-band profile as the experiment queue.",
            "Treat source-known v2 corrections as an upper-bound signal, not APK-only production accuracy.",
            "A candidate fix is counted only when the normal baseline selected a wrong version and the v2 source-known slice selected the source version.",
            "Exact emitted controls must stay exact in the v2 source-known slice.",
            "False-positive extra emissions stay blocking controls because a version reranker cannot invent missing source evidence.",
            "Promotion requires a future full-DB/APK-only reranker with clean controls; this artifact does not promote it.",
        ],
        "sources": {
            "router_json": normalize_path(router_json),
            "large_analysis_json": normalize_path(large_analysis_json),
            "v2_dashboard_json": normalize_path(v2_dashboard_json),
        },
        "summary": summary,
        "top_fixable_coordinates": _top_counts(
            Counter(
                row["coordinate"]
                for row in wrong_rows
                if row["classification"] == "source-known-rerank-would-fix"
            ),
            limit=20,
        ),
        "top_blocked_coordinates": _top_counts(
            Counter(
                row["coordinate"]
                for row in wrong_rows
                if row["classification"] != "source-known-rerank-would-fix"
            ),
            limit=20,
        ),
        "router_top_coordinates": _top_counts(
            Counter(row["coordinate"] for row in router_rows),
            limit=20,
        ),
        "wrong_version_rows": wrong_rows,
        "exact_control_rows": exact_control_rows,
        "false_positive_control_rows": false_positive_control_rows,
        "matcher_recall_rows": matcher_recall_rows,
        "source_gap_rows": source_gap_rows,
        "wrong_router_rows": wrong_router_rows,
    }


def evaluate_wrong_version_row(
    row: dict[str, Any],
    *,
    v2_reports: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    source_versions = split_versions(row.get("correct_source_versions"))
    selected = str(row.get("tool_selected_version") or "")
    v2_decision = find_v2_decision(v2_reports, row)
    v2_selected = str(v2_decision.get("selected_version") or "") if v2_decision else ""

    if len(source_versions) != 1:
        classification = "ambiguous-source-version-blocked"
        recommendation = "block"
        reason = "requires exactly one source version for this experiment"
    elif not v2_decision:
        classification = "no-v2-source-decision-blocked"
        recommendation = "block"
        reason = "v2 source-known report has no decision for this coordinate"
    elif v2_selected in source_versions:
        classification = "source-known-rerank-would-fix"
        recommendation = "suggest_report_only_source_known_rerank"
        reason = "baseline selected a wrong version and v2 source-known slice selected the source version"
    else:
        classification = "v2-source-known-still-not-source-blocked"
        recommendation = "block"
        reason = "source-known slice still selected a non-source version"

    return {
        "case_id": row.get("case_id"),
        "case_name": row.get("case_name"),
        "case_role": row.get("case_role"),
        "coordinate": row.get("coordinate"),
        "baseline_selected_version": selected,
        "source_versions": source_versions,
        "baseline_confidence": row.get("confidence"),
        "match_type": row.get("match_type"),
        "v2_selected_version": v2_selected or None,
        "v2_score": _round(v2_decision.get("score")) if v2_decision else None,
        "v2_gap_to_next": _round(v2_decision.get("gap_to_next")) if v2_decision else None,
        "classification": classification,
        "recommendation": recommendation,
        "reason": reason,
        "production_promotion": False,
    }


def evaluate_exact_control_row(
    row: dict[str, Any],
    *,
    v2_reports: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    source_versions = split_versions(row.get("correct_source_versions"))
    selected = str(row.get("tool_selected_version") or "")
    v2_decision = find_v2_decision(v2_reports, row)
    v2_selected = str(v2_decision.get("selected_version") or "") if v2_decision else ""
    if v2_decision and v2_selected in source_versions and selected in source_versions:
        classification = "control-stays-exact"
    elif not v2_decision:
        classification = "control-no-v2-decision"
    else:
        classification = "control-regression-risk"
    return {
        "case_id": row.get("case_id"),
        "case_name": row.get("case_name"),
        "case_role": row.get("case_role"),
        "coordinate": row.get("coordinate"),
        "baseline_selected_version": selected,
        "source_versions": source_versions,
        "v2_selected_version": v2_selected or None,
        "classification": classification,
        "production_promotion": False,
    }


def evaluate_false_positive_control_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": row.get("case_id"),
        "case_name": row.get("case_name"),
        "case_role": row.get("case_role"),
        "coordinate": row.get("coordinate"),
        "baseline_selected_version": row.get("tool_selected_version"),
        "classification": "false-positive-extra-emission-control",
        "recommendation": "block-reranker-cannot-create-source-evidence",
        "production_promotion": False,
    }


def summarize_router_row(row: dict[str, Any]) -> dict[str, Any]:
    evidence = row.get("evidence", {})
    return {
        "row_id": row.get("row_id"),
        "row_source": row.get("row_source"),
        "case_id": row.get("case_id"),
        "app": row.get("app"),
        "coordinate": row.get("coordinate"),
        "source_version": row.get("source_version"),
        "candidate_version": row.get("candidate_version"),
        "priority": row.get("priority"),
        "reason_codes": row.get("reason_codes", []),
        "source_score": evidence.get("source_score"),
        "best_score": evidence.get("best_score"),
        "score_gap_to_best": evidence.get("score_gap_to_best"),
        "next_action": evidence.get("next_action"),
        "recall_status": evidence.get("recall_status"),
    }


def build_summary(
    *,
    router_rows: list[dict[str, Any]],
    version_band_coordinates: set[str],
    wrong_rows: list[dict[str, Any]],
    exact_control_rows: list[dict[str, Any]],
    false_positive_control_rows: list[dict[str, Any]],
    matcher_recall_rows: list[dict[str, Any]],
    source_gap_rows: list[dict[str, Any]],
    wrong_router_rows: list[dict[str, Any]],
    total_wrong_rows: int,
) -> dict[str, Any]:
    wrong_counts = Counter(row["classification"] for row in wrong_rows)
    exact_counts = Counter(row["classification"] for row in exact_control_rows)
    false_positive_counts = Counter(
        row["classification"] for row in false_positive_control_rows
    )
    fixable = wrong_counts.get("source-known-rerank-would-fix", 0)
    return {
        "router_version_band_rows": len(router_rows),
        "router_version_band_coordinates": len(version_band_coordinates),
        "router_row_source_counts": dict(
            sorted(Counter(row["row_source"] for row in router_rows).items())
        ),
        "total_baseline_wrong_version_rows": total_wrong_rows,
        "baseline_wrong_version_rows_in_scope": len(wrong_rows),
        "baseline_wrong_version_scope_percent": _percent(len(wrong_rows), total_wrong_rows),
        "source_known_fixable_wrong_version_rows": fixable,
        "source_known_fixable_scope_percent": _percent(fixable, len(wrong_rows)),
        "source_known_blocked_wrong_version_rows": len(wrong_rows) - fixable,
        "wrong_version_classification_counts": dict(sorted(wrong_counts.items())),
        "exact_control_rows_in_scope": len(exact_control_rows),
        "exact_control_classification_counts": dict(sorted(exact_counts.items())),
        "false_positive_extra_control_rows_in_scope": len(false_positive_control_rows),
        "false_positive_control_classification_counts": dict(
            sorted(false_positive_counts.items())
        ),
        "matcher_recall_router_rows": len(matcher_recall_rows),
        "source_gap_router_rows": len(source_gap_rows),
        "wrong_version_router_rows": len(wrong_router_rows),
        "report_only": True,
        "production_promotion": False,
    }


def verdict(summary: dict[str, Any]) -> str:
    if summary["exact_control_classification_counts"].get("control-regression-risk", 0):
        return "reject-control-regression-risk"
    if summary["source_known_fixable_wrong_version_rows"]:
        return "source-known-rerank-promising-report-only-not-promoted"
    return "no-source-known-rerank-benefit"


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
        "source_known_fixable_wrong_version_rows": summary[
            "source_known_fixable_wrong_version_rows"
        ],
        "baseline_wrong_version_rows_in_scope": summary[
            "baseline_wrong_version_rows_in_scope"
        ],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Version-Band Rerank Experiment",
        "",
        "Generated by `apk-sbom version-band-rerank-experiment` or `scripts/build_version_band_rerank_experiment.py`.",
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
            f"- Router version-band rows: `{summary['router_version_band_rows']}`",
            f"- Router version-band coordinates: `{summary['router_version_band_coordinates']}`",
            f"- Router row sources: `{json.dumps(summary['router_row_source_counts'], sort_keys=True)}`",
            f"- Baseline wrong-version rows in scope: `{summary['baseline_wrong_version_rows_in_scope']}` / `{summary['total_baseline_wrong_version_rows']}` (`{summary['baseline_wrong_version_scope_percent']}%`)",
            f"- Source-known fixable wrong-version rows: `{summary['source_known_fixable_wrong_version_rows']}` (`{summary['source_known_fixable_scope_percent']}%` of scoped wrong-version rows)",
            f"- Source-known blocked wrong-version rows: `{summary['source_known_blocked_wrong_version_rows']}`",
            f"- Exact control rows in scope: `{summary['exact_control_rows_in_scope']}`",
            f"- False-positive extra-emission controls in scope: `{summary['false_positive_extra_control_rows_in_scope']}`",
            "",
            "## Wrong-Version Classifications",
            "",
            "| Classification | Rows |",
            "|---|---:|",
        ]
    )
    for key, value in summary["wrong_version_classification_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Exact Control Classifications",
            "",
            "| Classification | Rows |",
            "|---|---:|",
        ]
    )
    for key, value in summary["exact_control_classification_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Top Source-Known Fixable Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    for row in payload["top_fixable_coordinates"]:
        lines.append(f"| `{row['key']}` | {row['rows']} |")
    lines.extend(
        [
            "",
            "## Top Router Version-Band Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    for row in payload["router_top_coordinates"]:
        lines.append(f"| `{row['key']}` | {row['rows']} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This is a useful result, but it is deliberately not a production matcher result. The source-known v2 slice proves that many wrong-version rows have a correct same-coordinate source version that can be selected when the candidate space is constrained. It does not prove that the unconstrained APK-only matcher can safely find that version without new false positives.",
            "",
            "The next technical step is a real full-DB APK-only reranker using independent evidence, such as dependency-era coherence, version-unique literals, and structural similarity, followed by the same exact-control and false-positive controls recorded here.",
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for key, value in sorted(payload["sources"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def find_v2_decision(
    v2_reports: dict[str, list[dict[str, Any]]],
    row: dict[str, Any],
) -> dict[str, Any] | None:
    case_id = str(row.get("case_id") or "")
    coordinate = str(row.get("coordinate") or "")
    for decision in v2_reports.get(case_id, []):
        if decision.get("coordinate") == coordinate:
            return decision
    return None


def split_versions(value: Any) -> list[str]:
    return [
        version.strip()
        for version in str(value or "").replace(",", ";").split(";")
        if version.strip()
    ]


def _load_v2_reports(v2_dashboard: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    reports: dict[str, list[dict[str, Any]]] = {}
    for case in v2_dashboard.get("cases", []):
        case_id = str(case.get("case_id") or "")
        report_path = Path(str(case.get("paths", {}).get("report") or ""))
        if not case_id or not report_path.exists():
            continue
        report = _load_json(report_path)
        reports[case_id] = report.get("match_summary", {}).get("decisions", [])
    return reports


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


def _round(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return round(float(value), 6)
    except (TypeError, ValueError):
        return None


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")
