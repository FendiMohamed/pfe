from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from apk_sbom.composite_family_shortlist_simulation import should_rescue


DEFAULT_DIAGNOSTIC_JSON = Path(
    "data/results/experiments/coarse-to-fine-pruning-diagnostics.json"
)
DEFAULT_COMPOSITE_JSON = Path(
    "data/results/experiments/composite-family-shortlist-simulation.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/class-correspondence-pruning-diagnostics.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/CLASS_CORRESPONDENCE_PRUNING_DIAGNOSTICS.md")
DEFAULT_MARGINS = (0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 1.0)
PROFILES: tuple[dict[str, Any], ...] = (
    {
        "profile_id": "class-only",
        "weights": {"class_score": 1.0},
    },
    {
        "profile_id": "class-method-correspondence",
        "weights": {"class_score": 0.70, "method_score": 0.30},
    },
    {
        "profile_id": "package-class-method-correspondence",
        "weights": {"package_score": 0.15, "class_score": 0.60, "method_score": 0.25},
    },
)
RESCUE_POLICIES = ("none", "independent-support-rescue")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare class-subset/class-correspondence pruning proxies against "
            "the promoted composite family shortlist."
        )
    )
    parser.add_argument("--diagnostic-json", default=str(DEFAULT_DIAGNOSTIC_JSON))
    parser.add_argument("--composite-json", default=str(DEFAULT_COMPOSITE_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        diagnostic_json=Path(args.diagnostic_json),
        composite_json=Path(args.composite_json),
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
    diagnostic_json: Path = DEFAULT_DIAGNOSTIC_JSON,
    composite_json: Path = DEFAULT_COMPOSITE_JSON,
    margins: Sequence[float] = DEFAULT_MARGINS,
    profiles: Sequence[dict[str, Any]] = PROFILES,
) -> dict[str, Any]:
    diagnostic = read_json(diagnostic_json)
    composite = read_json(composite_json)
    rows = [row for row in diagnostic.get("rows", []) if isinstance(row, dict)]
    promoted = promoted_composite_configuration(composite)
    configurations = [
        evaluate_configuration(
            rows,
            profile=profile,
            rescue_policy=rescue_policy,
            margin=round(float(margin), 6),
        )
        for profile in profiles
        for rescue_policy in RESCUE_POLICIES
        for margin in margins
    ]
    safe_reducing = [
        configuration
        for configuration in configurations
        if configuration["tracked_source_family_losses"] == 0
        and configuration["candidate_version_slots_removed"] > 0
    ]
    strict_reducing = [
        configuration
        for configuration in configurations
        if configuration["rescue_policy"] == "none"
        and configuration["candidate_version_slots_removed"] > 0
    ]
    strict_clean_reducing = [
        configuration
        for configuration in strict_reducing
        if configuration["tracked_source_family_losses"] == 0
    ]
    best_safe = max(
        safe_reducing,
        key=lambda item: (
            item["candidate_version_slots_removed"],
            item["family_rows_removed"],
            -item["margin"],
        ),
        default=None,
    )
    gates = build_gates(rows, promoted, configurations)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    summary = build_summary(
        rows,
        configurations,
        promoted,
        safe_reducing,
        strict_reducing,
        strict_clean_reducing,
        best_safe,
        failed_gates,
    )
    return {
        "schema_version": 1,
        "verdict": verdict(summary, failed_gates),
        "recommendation": recommendation(summary, failed_gates),
        "scope": (
            "Diagnostic only. This artifact tests whether class-subset or "
            "class/method-correspondence family pruning adds safe pruning evidence "
            "beyond the already-promoted balanced composite family shortlist. It "
            "uses existing report-backed decision rows, retains complete version "
            "bands for kept coordinate families, and does not change matcher "
            "scoring, selected versions, SBOM output, vulnerability labels, or "
            "source-validation metrics."
        ),
        "sources": {
            "diagnostic_json": normalize_path(diagnostic_json),
            "composite_json": normalize_path(composite_json),
        },
        "profiles": list(profiles),
        "rescue_policies": {
            "none": "Use only class/package/method correspondence scores.",
            "independent-support-rescue": (
                "Also retain a family with dependency-edge support, two literal "
                "matches, or class overlap plus method/dependency/literal support."
            ),
        },
        "policy": [
            "A retained coordinate family keeps every version candidate.",
            "Any tracked controlled or real source-family loss rejects a configuration as a production candidate.",
            "A rescued class-correspondence lane must outperform the promoted composite shortlist before it is worth live validation.",
            "If strict class correspondence is unsafe and rescued correspondence underperforms the promoted shortlist, stop the P2 pruning lane and move to optimization-aware diagnostics.",
        ],
        "summary": summary,
        "promoted_composite_configuration": promoted,
        "best_safe_configuration": best_safe,
        "strict_class_correspondence_summary": summarize_strict_configs(strict_reducing),
        "configurations": configurations,
        "gates": gates,
    }


def promoted_composite_configuration(composite: dict[str, Any]) -> dict[str, Any] | None:
    value = composite.get("recommended_configuration")
    if not isinstance(value, dict):
        return None
    return {
        "profile_id": value.get("profile_id"),
        "rescue_policy": value.get("rescue_policy"),
        "margin": value.get("margin"),
        "candidate_version_slots_removed": int(
            value.get("candidate_version_slots_removed") or 0
        ),
        "family_rows_removed": int(value.get("family_rows_removed") or 0),
        "tracked_source_family_losses": int(
            value.get("tracked_source_family_losses") or 0
        ),
    }


def evaluate_configuration(
    rows: list[dict[str, Any]],
    *,
    profile: dict[str, Any],
    rescue_policy: str,
    margin: float,
) -> dict[str, Any]:
    retained_rows: list[dict[str, Any]] = []
    dropped_rows: list[dict[str, Any]] = []
    rescued_rows: list[dict[str, Any]] = []
    by_report: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_report.setdefault(str(row.get("report_path") or ""), []).append(row)
    for report_rows in by_report.values():
        best_score = max(
            (correspondence_score(row, profile["weights"]) for row in report_rows),
            default=0.0,
        )
        for row in report_rows:
            margin_keep = correspondence_score(row, profile["weights"]) + margin >= best_score
            rescued = should_rescue(row, rescue_policy)
            if margin_keep or rescued:
                retained_rows.append(row)
                if rescued and not margin_keep:
                    rescued_rows.append(row)
            else:
                dropped_rows.append(row)
    tracked_losses = [row for row in dropped_rows if row.get("source_versions")]
    candidate_slots_before = sum(candidate_slots(row) for row in rows)
    candidate_slots_after = sum(candidate_slots(row) for row in retained_rows)
    return {
        "profile_id": str(profile["profile_id"]),
        "rescue_policy": rescue_policy,
        "margin": margin,
        "classification": (
            "tracked-source-family-clean"
            if not tracked_losses
            else "tracked-source-family-loss-do-not-use"
        ),
        "family_rows_before": len(rows),
        "family_rows_retained": len(retained_rows),
        "family_rows_removed": len(dropped_rows),
        "family_rows_rescued": len(rescued_rows),
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
            compact_loss_row(row, profile["weights"]) for row in tracked_losses[:50]
        ],
    }


def correspondence_score(row: dict[str, Any], weights: dict[str, float]) -> float:
    return round(
        sum(float(row.get(key) or 0.0) * float(weight) for key, weight in weights.items()),
        6,
    )


def build_summary(
    rows: list[dict[str, Any]],
    configurations: list[dict[str, Any]],
    promoted: dict[str, Any] | None,
    safe_reducing: list[dict[str, Any]],
    strict_reducing: list[dict[str, Any]],
    strict_clean_reducing: list[dict[str, Any]],
    best_safe: dict[str, Any] | None,
    failed_gates: list[dict[str, Any]],
) -> dict[str, Any]:
    promoted_removed = (
        int(promoted.get("candidate_version_slots_removed") or 0) if promoted else 0
    )
    best_safe_removed = (
        int(best_safe.get("candidate_version_slots_removed") or 0) if best_safe else 0
    )
    return {
        "family_rows": len(rows),
        "candidate_version_slots": sum(candidate_slots(row) for row in rows),
        "tracked_source_family_rows": sum(1 for row in rows if row.get("source_versions")),
        "configurations_evaluated": len(configurations),
        "safe_reducing_configurations": len(safe_reducing),
        "strict_reducing_configurations": len(strict_reducing),
        "strict_clean_reducing_configurations": len(strict_clean_reducing),
        "strict_reducing_configurations_with_source_loss": sum(
            1 for item in strict_reducing if item["tracked_source_family_losses"] > 0
        ),
        "promoted_composite_candidate_version_slots_removed": promoted_removed,
        "best_safe_candidate_version_slots_removed": best_safe_removed,
        "best_safe_outperforms_promoted_composite": (
            best_safe_removed > promoted_removed if best_safe else False
        ),
        "best_safe_candidate_slot_delta_vs_promoted": best_safe_removed - promoted_removed,
        "failed_gates": len(failed_gates),
    }


def summarize_strict_configs(configurations: list[dict[str, Any]]) -> dict[str, Any]:
    if not configurations:
        return {
            "configurations": 0,
            "best_reduction": 0,
            "lowest_source_losses": 0,
        }
    return {
        "configurations": len(configurations),
        "best_reduction": max(
            int(item["candidate_version_slots_removed"]) for item in configurations
        ),
        "lowest_source_losses": min(
            int(item["tracked_source_family_losses"]) for item in configurations
        ),
        "loss_by_profile": dict(
            sorted(
                Counter(
                    str(item["profile_id"])
                    for item in configurations
                    if item["tracked_source_family_losses"] > 0
                ).items()
            )
        ),
    }


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


def compact_loss_row(row: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    return {
        "dataset_layer": row.get("dataset_layer"),
        "case_id": row.get("case_id"),
        "coordinate": row.get("coordinate"),
        "source_versions": row.get("source_versions", []),
        "correspondence_score": correspondence_score(row, weights),
    }


def build_gates(
    rows: list[dict[str, Any]],
    promoted: dict[str, Any] | None,
    configurations: list[dict[str, Any]],
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
            "promoted-composite-comparison-present",
            fail_count=0 if promoted else 1,
            evidence=(
                f"Promoted composite comparison removes {promoted['candidate_version_slots_removed']} slots."
                if promoted
                else "No promoted composite comparison found."
            ),
        ),
        gate(
            "configuration-sweep-complete",
            fail_count=0 if configurations else 1,
            evidence=f"{len(configurations)} class-correspondence configurations evaluated.",
        ),
    ]


def gate(gate_id: str, *, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


def verdict(summary: dict[str, Any], failed_gates: list[dict[str, Any]]) -> str:
    if failed_gates:
        return "class-correspondence-pruning-diagnostic-incomplete"
    if summary["best_safe_outperforms_promoted_composite"]:
        return "class-correspondence-pruning-candidate-needs-live-validation"
    return "class-correspondence-pruning-no-new-promotion"


def recommendation(summary: dict[str, Any], failed_gates: list[dict[str, Any]]) -> str:
    if failed_gates:
        return "fix-diagnostic-inputs-before-pruning-decision"
    if summary["best_safe_outperforms_promoted_composite"]:
        return "run-live-offline-class-correspondence-validation-before-wiring"
    return "keep-class-correspondence-diagnostic-only-and-move-to-optimization-aware-logic"


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
    best_safe = payload.get("best_safe_configuration")
    promoted = payload.get("promoted_composite_configuration")
    lines = [
        "# Class-Correspondence Pruning Diagnostics",
        "",
        "Generated by `scripts/build_class_correspondence_pruning_diagnostics.py`.",
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
        f"- Tracked source-family rows: `{summary['tracked_source_family_rows']}`",
        f"- Configurations evaluated: `{summary['configurations_evaluated']}`",
        f"- Safe reducing configurations: `{summary['safe_reducing_configurations']}`",
        f"- Strict reducing configurations: `{summary['strict_reducing_configurations']}`",
        f"- Strict clean reducing configurations: `{summary['strict_clean_reducing_configurations']}`",
        f"- Strict reducing configurations with source loss: `{summary['strict_reducing_configurations_with_source_loss']}`",
        f"- Promoted composite slots removed: `{summary['promoted_composite_candidate_version_slots_removed']}`",
        f"- Best safe class-correspondence slots removed: `{summary['best_safe_candidate_version_slots_removed']}`",
        f"- Best safe delta vs promoted composite: `{summary['best_safe_candidate_slot_delta_vs_promoted']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        "",
        "## Comparison",
        "",
        "| Lane | Profile | Rescue | Margin | Candidate slots removed | Tracked losses |",
        "|---|---|---|---:|---:|---:|",
    ]
    if promoted:
        lines.append(
            "| Promoted composite | "
            f"`{md(promoted.get('profile_id'))}` | "
            f"`{md(promoted.get('rescue_policy'))}` | "
            f"{promoted.get('margin')} | "
            f"{promoted.get('candidate_version_slots_removed')} | "
            f"{promoted.get('tracked_source_family_losses')} |"
        )
    if best_safe:
        lines.append(
            "| Best safe class correspondence | "
            f"`{md(best_safe.get('profile_id'))}` | "
            f"`{md(best_safe.get('rescue_policy'))}` | "
            f"{best_safe.get('margin')} | "
            f"{best_safe.get('candidate_version_slots_removed')} | "
            f"{best_safe.get('tracked_source_family_losses')} |"
        )
    lines.extend(
        [
            "",
            "## Profile Sweep",
            "",
            "| Profile | Rescue | Margin | Label | Family rows removed | Rescued rows | Candidate slots removed | Reduction ratio | Tracked losses |",
            "|---|---|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["configurations"]:
        lines.append(
            "| "
            f"`{md(row['profile_id'])}` | "
            f"`{md(row['rescue_policy'])}` | "
            f"{row['margin']} | "
            f"`{md(row['classification'])}` | "
            f"{row['family_rows_removed']} | "
            f"{row['family_rows_rescued']} | "
            f"{row['candidate_version_slots_removed']} | "
            f"{row['candidate_slot_reduction_ratio']} | "
            f"{row['tracked_source_family_losses']} |"
        )
    lines.extend(
        [
            "",
            "## Best Safe Dropped Coordinates",
            "",
            "| Coordinate | Family rows removed | Candidate slots removed |",
            "|---|---:|---:|",
        ]
    )
    for row in (best_safe or {}).get("top_dropped_coordinates", []):
        lines.append(
            "| "
            f"`{md(row['coordinate'])}` | "
            f"{row['family_rows_removed']} | "
            f"{row['candidate_version_slots_removed']} |"
        )
    if not best_safe:
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
    lines.extend(["", "## Conclusion", "", conclusion(payload), ""])
    return "\n".join(lines)


def conclusion(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    if summary["failed_gates"]:
        return "Fix the diagnostic inputs before making a pruning decision."
    if summary["best_safe_outperforms_promoted_composite"]:
        return (
            "Class-correspondence pruning has a report-backed candidate that beats "
            "the promoted composite shortlist. It still needs live offline "
            "validation before any production wiring."
        )
    return (
        "Keep class-correspondence pruning diagnostic-only. Strict class or "
        "class/method correspondence loses tracked source families at reducing "
        "margins, while the rescued variant is safe but removes fewer candidate "
        "slots than the already-promoted composite family shortlist. The P2 "
        "candidate-pruning lane is stable enough to move on to limited "
        "optimization-aware diagnostics."
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
