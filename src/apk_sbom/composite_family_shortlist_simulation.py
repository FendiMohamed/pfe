from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


DEFAULT_DIAGNOSTIC_JSON = Path("data/results/experiments/coarse-to-fine-pruning-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/composite-family-shortlist-simulation.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_SIMULATION.md")
DEFAULT_MARGINS = (0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 1.0)
RECOMMENDED_PROFILE_ID = "balanced-context"
RECOMMENDED_RESCUE_POLICY = "independent-support-rescue"

PROFILES: tuple[dict[str, Any], ...] = (
    {
        "profile_id": "balanced-context",
        "weights": {
            "package_score": 0.15,
            "class_score": 0.30,
            "method_score": 0.20,
            "dependency_score": 0.20,
            "literal_score": 0.15,
        },
    },
    {
        "profile_id": "structural",
        "weights": {
            "package_score": 0.10,
            "class_score": 0.35,
            "method_score": 0.25,
            "dependency_score": 0.20,
            "literal_score": 0.10,
        },
    },
    {
        "profile_id": "context-heavy",
        "weights": {
            "package_score": 0.10,
            "class_score": 0.20,
            "method_score": 0.10,
            "dependency_score": 0.35,
            "literal_score": 0.25,
        },
    },
)
RESCUE_POLICIES = ("none", "independent-support-rescue")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a report-backed composite family-shortlist sweep with independent "
            "support rescue before any live prefilter implementation."
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
    profiles: Sequence[dict[str, Any]] = PROFILES,
) -> dict[str, Any]:
    diagnostic = read_json(diagnostic_json)
    rows = [row for row in diagnostic.get("rows", []) if isinstance(row, dict)]
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
    recommended_candidates = [
        configuration
        for configuration in safe_reducing
        if configuration["profile_id"] == RECOMMENDED_PROFILE_ID
        and configuration["rescue_policy"] == RECOMMENDED_RESCUE_POLICY
    ]
    recommended = max(
        recommended_candidates,
        key=lambda item: (
            item["candidate_version_slots_removed"],
            item["margin"],
        ),
        default=None,
    )
    gates = build_gates(rows, safe_reducing, recommended)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    return {
        "schema_version": 1,
        "verdict": verdict(recommended, failed_gates),
        "recommendation": (
            "advance-balanced-composite-shortlist-to-live-offline-validation"
            if recommended
            else "keep-diagnostic-only-and-strengthen-family-signal"
        ),
        "scope": (
            "Offline report-backed composite shortlist simulation only. It uses "
            "package, class, method, dependency, and literal overlap evidence "
            "already recorded in current report decisions. It retains complete "
            "version bands for kept coordinate families, optionally rescues "
            "families with concrete independent support, and measures tracked "
            "controlled/real source-family retention. It does not change "
            "production matching, selected versions, or SBOM output."
        ),
        "sources": {"diagnostic_json": normalize_path(diagnostic_json)},
        "profiles": list(profiles),
        "rescue_policies": {
            "none": "Keep only families within the profile margin.",
            "independent-support-rescue": (
                "Also keep a family when it has a dependency-edge match, at least "
                "two literal matches, or class overlap plus method/dependency/literal support."
            ),
        },
        "policy": [
            "A retained coordinate family keeps every version candidate; never prune inside a close version band.",
            "Any tracked controlled or real source-family loss rejects a configuration.",
            "Use the balanced-context profile for the next live offline validation lane; alternative profiles remain comparison evidence.",
            "This report-backed simulation is a design gate only. Production wiring still requires a live offline recomputation and selected-version regression checks.",
        ],
        "summary": build_summary(rows, configurations, safe_reducing, recommended, failed_gates),
        "configurations": configurations,
        "recommended_configuration": recommended,
        "gates": gates,
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
            (composite_score(row, profile["weights"]) for row in report_rows),
            default=0.0,
        )
        for row in report_rows:
            margin_keep = composite_score(row, profile["weights"]) + margin >= best_score
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
            compact_row(row, profile["weights"]) for row in tracked_losses[:50]
        ],
    }


def composite_score(row: dict[str, Any], weights: dict[str, float]) -> float:
    return round(
        sum(float(row.get(key) or 0.0) * float(weight) for key, weight in weights.items()),
        6,
    )


def should_rescue(row: dict[str, Any], rescue_policy: str) -> bool:
    if rescue_policy == "none":
        return False
    if rescue_policy != "independent-support-rescue":
        raise ValueError(f"unknown rescue policy: {rescue_policy}")
    matched_classes = int(row.get("matched_classes") or 0)
    matched_methods = int(row.get("matched_methods") or 0)
    matched_dependency_edges = int(row.get("matched_dependency_edges") or 0)
    matched_string_literals = int(row.get("matched_string_literals") or 0)
    return (
        matched_dependency_edges >= 1
        or matched_string_literals >= 2
        or (
            matched_classes >= 1
            and (
                matched_methods >= 1
                or matched_dependency_edges >= 1
                or matched_string_literals >= 1
            )
        )
    )


def build_summary(
    rows: list[dict[str, Any]],
    configurations: list[dict[str, Any]],
    safe_reducing: list[dict[str, Any]],
    recommended: dict[str, Any] | None,
    failed_gates: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = {
        "family_rows": len(rows),
        "candidate_version_slots": sum(candidate_slots(row) for row in rows),
        "tracked_source_family_rows": sum(1 for row in rows if row.get("source_versions")),
        "configurations_evaluated": len(configurations),
        "tracked-clean-reducing_configurations": len(safe_reducing),
        "failed_gates": len(failed_gates),
    }
    if recommended:
        summary.update(
            {
                "recommended_profile_id": recommended["profile_id"],
                "recommended_rescue_policy": recommended["rescue_policy"],
                "recommended_margin": recommended["margin"],
                "recommended_family_rows_removed": recommended["family_rows_removed"],
                "recommended_family_rows_rescued": recommended["family_rows_rescued"],
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


def compact_row(row: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    return {
        "dataset_layer": row.get("dataset_layer"),
        "case_id": row.get("case_id"),
        "coordinate": row.get("coordinate"),
        "source_versions": row.get("source_versions", []),
        "composite_score": composite_score(row, weights),
    }


def build_gates(
    rows: list[dict[str, Any]],
    safe_reducing: list[dict[str, Any]],
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
            "tracked-clean-reducing-configurations-found",
            fail_count=0 if safe_reducing else 1,
            evidence=f"{len(safe_reducing)} reducing configurations preserve every tracked source family.",
        ),
        gate(
            "balanced-independent-support-recommendation-found",
            fail_count=0 if recommended else 1,
            evidence=(
                "Balanced composite plus independent-support rescue has a tracked-clean reducing configuration."
                if recommended
                else "Balanced composite plus independent-support rescue has no tracked-clean reducing configuration."
            ),
        ),
        gate(
            "recommended-configuration-keeps-complete-version-bands",
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
        return "composite-family-shortlist-no-safe-report-backed-candidate"
    return "composite-family-shortlist-report-backed-candidate-needs-live-offline-validation"


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
    recommended = payload.get("recommended_configuration")
    lines = [
        "# Composite Family-Shortlist Proxy Simulation",
        "",
        "Generated by `scripts/build_composite_family_shortlist_simulation.py`.",
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
        f"- Configurations evaluated: `{summary['configurations_evaluated']}`",
        f"- Tracked-clean reducing configurations: `{summary['tracked-clean-reducing_configurations']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
    ]
    if recommended:
        lines.extend(
            [
                f"- Recommended profile: `{recommended['profile_id']}`",
                f"- Recommended rescue policy: `{recommended['rescue_policy']}`",
                f"- Recommended margin: `{recommended['margin']}`",
                f"- Recommended family rows removed: `{recommended['family_rows_removed']}`",
                f"- Recommended family rows rescued: `{recommended['family_rows_rescued']}`",
                f"- Recommended candidate-version slots removed: `{recommended['candidate_version_slots_removed']}`",
                f"- Recommended candidate-slot reduction ratio: `{recommended['candidate_slot_reduction_ratio']}`",
                f"- Recommended tracked source-family losses: `{recommended['tracked_source_family_losses']}`",
            ]
        )
    lines.extend(["", "## Profiles", "", "| Profile | Weights |", "|---|---|"])
    for profile in payload["profiles"]:
        weights = ", ".join(
            f"{key}={value}" for key, value in profile["weights"].items()
        )
        lines.append(f"| `{md(profile['profile_id'])}` | {md(weights)} |")
    lines.extend(
        [
            "",
            "## Configuration Sweep",
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
    if not payload.get("recommended_configuration"):
        return (
            "Keep composite family-shortlist work diagnostic-only. No balanced "
            "independent-support configuration reduces work while preserving all "
            "tracked source families."
        )
    return (
        "The balanced composite plus independent-support rescue is a report-backed "
        "candidate for live offline validation. It reduces candidate-version slots "
        "without dropping any tracked controlled or real source family in this "
        "proxy sweep, while retaining complete close-version bands. Do not wire it "
        "into production until a live recomputation confirms final selected-version "
        "and source-validation behavior."
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
