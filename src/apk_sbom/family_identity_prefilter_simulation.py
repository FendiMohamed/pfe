from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


DEFAULT_DIAGNOSTIC_JSON = Path("data/results/experiments/coarse-to-fine-pruning-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/family-identity-prefilter-simulation.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/FAMILY_IDENTITY_PREFILTER_SIMULATION.md")
DEFAULT_MARGINS = (0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 1.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a report-backed offline family-identity prefilter margin sweep "
            "without changing production matching."
        )
    )
    parser.add_argument("--diagnostic-json", default=str(DEFAULT_DIAGNOSTIC_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(diagnostic_json=Path(args.diagnostic_json))
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
    margins: Sequence[float] = DEFAULT_MARGINS,
) -> dict[str, Any]:
    diagnostic = read_json(diagnostic_json)
    rows = [row for row in diagnostic.get("rows", []) if isinstance(row, dict)]
    configurations = [
        evaluate_margin(rows, margin=round(float(margin), 6))
        for margin in margins
    ]
    safe_reducing = [
        configuration
        for configuration in configurations
        if configuration["tracked_source_family_losses"] == 0
        and configuration["candidate_version_slots_removed"] > 0
    ]
    recommended = max(
        safe_reducing,
        key=lambda item: (
            item["candidate_version_slots_removed"],
            item["family_rows_removed"],
            -item["margin"],
        ),
        default=None,
    )
    gates = build_gates(rows, recommended)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    return {
        "schema_version": 1,
        "verdict": verdict(recommended, failed_gates),
        "recommendation": (
            "run-live-offline-prefilter-validation-before-production-wiring"
            if recommended
            else "keep-diagnostic-only-and-design-stronger-family-signal"
        ),
        "scope": (
            "Offline report-backed proxy simulation only. The sweep uses each "
            "existing decision row's package/class family-identity proxy score, "
            "retains complete version bands for kept coordinate families, and "
            "measures candidate-slot reduction against tracked controlled and real "
            "source-family retention. It does not change production matching."
        ),
        "sources": {"diagnostic_json": normalize_path(diagnostic_json)},
        "policy": [
            "A retained coordinate family keeps every version candidate; the proxy never prunes inside a close version band.",
            "Any tracked controlled or real source-family loss rejects that margin.",
            "This report-backed proxy is a design gate, not production validation.",
            "A live offline rerun must recompute the cheap family score before expensive scoring and compare final selected versions before any wiring.",
        ],
        "family_identity_proxy": {
            "formula": "(0.35 * package_score) + (0.65 * class_score)",
            "meaning": "Cheap coordinate-family identity approximation from already-recorded overlap evidence.",
        },
        "summary": build_summary(rows, configurations, recommended, failed_gates),
        "configurations": configurations,
        "recommended_configuration": recommended,
        "gates": gates,
    }


def evaluate_margin(rows: list[dict[str, Any]], *, margin: float) -> dict[str, Any]:
    retained_rows: list[dict[str, Any]] = []
    dropped_rows: list[dict[str, Any]] = []
    by_report: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_report.setdefault(str(row.get("report_path") or ""), []).append(row)
    for report_rows in by_report.values():
        best_score = max(
            (float(row.get("family_identity_proxy_score") or 0.0) for row in report_rows),
            default=0.0,
        )
        for row in report_rows:
            score = float(row.get("family_identity_proxy_score") or 0.0)
            if score + margin >= best_score:
                retained_rows.append(row)
            else:
                dropped_rows.append(row)
    tracked_losses = [row for row in dropped_rows if row.get("source_versions")]
    candidate_slots_before = sum(candidate_slots(row) for row in rows)
    candidate_slots_after = sum(candidate_slots(row) for row in retained_rows)
    return {
        "margin": margin,
        "classification": (
            "tracked-source-family-clean"
            if not tracked_losses
            else "tracked-source-family-loss-do-not-use"
        ),
        "family_rows_before": len(rows),
        "family_rows_retained": len(retained_rows),
        "family_rows_removed": len(dropped_rows),
        "candidate_version_slots_before": candidate_slots_before,
        "candidate_version_slots_retained": candidate_slots_after,
        "candidate_version_slots_removed": candidate_slots_before - candidate_slots_after,
        "candidate_slot_reduction_ratio": safe_divide(
            candidate_slots_before - candidate_slots_after,
            candidate_slots_before,
        ),
        "tracked_source_family_rows": sum(1 for row in rows if row.get("source_versions")),
        "tracked_source_family_losses": len(tracked_losses),
        "controlled_tracked_source_family_losses": sum(
            1 for row in tracked_losses if row.get("dataset_layer") == "controlled-generated"
        ),
        "real_tracked_source_family_losses": sum(
            1 for row in tracked_losses if row.get("dataset_layer") == "real-apk"
        ),
        "top_dropped_coordinates": summarize_dropped_coordinates(dropped_rows)[:15],
        "tracked_source_family_loss_rows": [
            {
                "dataset_layer": row.get("dataset_layer"),
                "case_id": row.get("case_id"),
                "coordinate": row.get("coordinate"),
                "source_versions": row.get("source_versions", []),
                "family_identity_proxy_score": row.get("family_identity_proxy_score"),
            }
            for row in tracked_losses[:50]
        ],
    }


def build_summary(
    rows: list[dict[str, Any]],
    configurations: list[dict[str, Any]],
    recommended: dict[str, Any] | None,
    failed_gates: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = {
        "family_rows": len(rows),
        "candidate_version_slots": sum(candidate_slots(row) for row in rows),
        "tracked_source_family_rows": sum(1 for row in rows if row.get("source_versions")),
        "margins_evaluated": len(configurations),
        "tracked-clean-reducing_margins": sum(
            1
            for configuration in configurations
            if configuration["tracked_source_family_losses"] == 0
            and configuration["candidate_version_slots_removed"] > 0
        ),
        "failed_gates": len(failed_gates),
    }
    if recommended:
        summary.update(
            {
                "recommended_margin": recommended["margin"],
                "recommended_family_rows_removed": recommended["family_rows_removed"],
                "recommended_candidate_version_slots_removed": recommended[
                    "candidate_version_slots_removed"
                ],
                "recommended_candidate_slot_reduction_ratio": recommended[
                    "candidate_slot_reduction_ratio"
                ],
                "recommended_tracked_source_family_losses": recommended[
                    "tracked_source_family_losses"
                ],
            }
        )
    return summary


def summarize_dropped_coordinates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    slots: Counter[str] = Counter()
    for row in rows:
        coordinate = str(row.get("coordinate") or "")
        counts[coordinate] += 1
        slots[coordinate] += candidate_slots(row)
    return [
        {
            "coordinate": coordinate,
            "family_rows_removed": counts[coordinate],
            "candidate_version_slots_removed": slots[coordinate],
        }
        for coordinate in sorted(
            counts,
            key=lambda coordinate: (slots[coordinate], counts[coordinate], coordinate),
            reverse=True,
        )
    ]


def build_gates(
    rows: list[dict[str, Any]],
    recommended: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    tracked_layers = {
        str(row.get("dataset_layer"))
        for row in rows
        if row.get("source_versions")
    }
    return [
        gate(
            "diagnostic-rows-present",
            fail_count=0 if rows else 1,
            evidence=f"{len(rows)} family decision rows loaded.",
        ),
        gate(
            "controlled-and-real-source-tracking-present",
            fail_count=0 if {"controlled-generated", "real-apk"} <= tracked_layers else 1,
            evidence=f"Tracked source-family layers: {', '.join(sorted(tracked_layers)) or 'none'}.",
        ),
        gate(
            "tracked-clean-reducing-margin-found",
            fail_count=0 if recommended else 1,
            evidence=(
                "At least one margin reduces candidate slots without tracked source-family loss."
                if recommended
                else "No reducing margin preserves every tracked source family."
            ),
        ),
        gate(
            "recommended-margin-keeps-complete-version-bands",
            fail_count=0,
            evidence="Simulation drops or retains whole coordinate families only.",
        ),
    ]


def gate(gate_id: str, *, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


def verdict(
    recommended: dict[str, Any] | None,
    failed_gates: list[dict[str, Any]],
) -> str:
    if failed_gates or not recommended:
        return "family-identity-prefilter-proxy-no-safe-reduction"
    return "family-identity-prefilter-proxy-candidate-needs-live-offline-validation"


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
        "# Family-Identity Prefilter Proxy Simulation",
        "",
        "Generated by `scripts/build_family_identity_prefilter_simulation.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        f"Recommendation: `{payload['recommendation']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Family decision rows: `{summary['family_rows']}`",
        f"- Candidate-version slots: `{summary['candidate_version_slots']}`",
        f"- Tracked controlled/real source-family rows: `{summary['tracked_source_family_rows']}`",
        f"- Margins evaluated: `{summary['margins_evaluated']}`",
        f"- Tracked-clean reducing margins: `{summary['tracked-clean-reducing_margins']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
    ]
    recommended = payload.get("recommended_configuration")
    if recommended:
        lines.extend(
            [
                f"- Recommended proxy margin: `{recommended['margin']}`",
                f"- Recommended family rows removed: `{recommended['family_rows_removed']}`",
                f"- Recommended candidate-version slots removed: `{recommended['candidate_version_slots_removed']}`",
                f"- Recommended candidate-slot reduction ratio: `{recommended['candidate_slot_reduction_ratio']}`",
                f"- Recommended tracked source-family losses: `{recommended['tracked_source_family_losses']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Family Proxy",
            "",
            f"- Formula: `{payload['family_identity_proxy']['formula']}`",
            f"- Meaning: {payload['family_identity_proxy']['meaning']}",
            "",
            "## Margin Sweep",
            "",
            "| Margin | Label | Family rows removed | Candidate slots removed | Reduction ratio | Tracked losses | Controlled losses | Real losses |",
            "|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["configurations"]:
        lines.append(
            "| "
            f"{row['margin']} | "
            f"`{md(row['classification'])}` | "
            f"{row['family_rows_removed']} | "
            f"{row['candidate_version_slots_removed']} | "
            f"{row['candidate_slot_reduction_ratio']} | "
            f"{row['tracked_source_family_losses']} | "
            f"{row['controlled_tracked_source_family_losses']} | "
            f"{row['real_tracked_source_family_losses']} |"
        )
    lines.extend(
        [
            "",
            "## Recommended Dropped Coordinates",
            "",
            "| Coordinate | Family rows removed | Candidate slots removed |",
            "|---|---:|---:|",
        ]
    )
    for row in (recommended or {}).get("top_dropped_coordinates", []):
        lines.append(
            "| "
            f"`{md(row['coordinate'])}` | "
            f"{row['family_rows_removed']} | "
            f"{row['candidate_version_slots_removed']} |"
        )
    if not recommended:
        lines.append("| none | 0 | 0 |")
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
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
            conclusion(payload),
            "",
        ]
    )
    return "\n".join(lines)


def conclusion(payload: dict[str, Any]) -> str:
    if payload.get("recommended_configuration"):
        return (
            "This proxy simulation is useful only as a design gate. The next step "
            "is a live offline implementation that computes the cheap family "
            "score before expensive version scoring, keeps all versions inside "
            "retained families, and reruns controlled plus real source-validation "
            "checks before any production wiring."
        )
    return (
        "Reject this simple package/class family proxy. Every reducing margin "
        "drops tracked source families; only the no-pruning margin stays clean. "
        "The next diagnostic should test a stronger family signal with additional "
        "dependency or literal support before any live prefilter implementation."
    )


def candidate_slots(row: dict[str, Any]) -> int:
    return int(row.get("reference_versions_considered") or 0)


def safe_divide(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
