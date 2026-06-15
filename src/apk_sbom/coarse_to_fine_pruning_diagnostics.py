from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_GENERATED_BATCH_JSON = Path("data/results/evaluation/generated-apk-category-batch.json")
DEFAULT_PHASE4_JSON = Path("data/results/experiments/r8-phase4-scoped-experiment-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/coarse-to-fine-pruning-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/COARSE_TO_FINE_PRUNING_DIAGNOSTICS.md")
CLOSE_BAND_MARGIN = 0.02
NEAR_TIE_MARGIN = 0.006
WIDE_VERSION_CANDIDATE_COUNT = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Measure existing generated and real report candidate pressure before "
            "attempting any coarse-to-fine matcher pruning."
        )
    )
    parser.add_argument("--generated-batch-json", default=str(DEFAULT_GENERATED_BATCH_JSON))
    parser.add_argument("--phase4-json", default=str(DEFAULT_PHASE4_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        generated_batch_json=Path(args.generated_batch_json),
        phase4_json=Path(args.phase4_json),
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
    generated_batch_json: Path = DEFAULT_GENERATED_BATCH_JSON,
    phase4_json: Path = DEFAULT_PHASE4_JSON,
) -> dict[str, Any]:
    generated_batch = read_json_if_exists(generated_batch_json)
    phase4 = read_json_if_exists(phase4_json)
    inventory = [
        *controlled_report_inventory(generated_batch),
        *real_report_inventory(phase4),
    ]
    rows: list[dict[str, Any]] = []
    missing_reports: list[dict[str, Any]] = []
    for item in inventory:
        report_path = Path(item["report_path"])
        if not report_path.exists():
            missing_reports.append(item)
            continue
        report = read_json(report_path)
        match_summary = report.get("match_summary", {})
        for decision in match_summary.get("decisions", []):
            if isinstance(decision, dict):
                rows.append(build_pressure_row(item, decision))

    rows.sort(
        key=lambda row: (
            not row["high_pressure"],
            -row["reference_versions_considered"],
            row["gap_to_next"],
            row["dataset_layer"],
            row["case_id"],
            row["coordinate"],
        )
    )
    gates = build_gates(inventory, rows, missing_reports)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    summary = summarize(inventory, rows, missing_reports, failed_gates)
    return {
        "schema_version": 1,
        "verdict": verdict(summary, failed_gates),
        "recommendation": (
            "simulate-family-identity-prefilter-offline-before-production-pruning"
        ),
        "scope": (
            "Diagnostic only. This artifact reads existing generated and real "
            "report decisions to measure version-candidate pressure after the "
            "current score threshold, including coordinates later suppressed by "
            "reportability filtering. It does not prune candidates, change "
            "matcher scoring, alter selected versions, or modify SBOM output."
        ),
        "sources": {
            "generated_batch_json": normalize_path(generated_batch_json),
            "phase4_json": normalize_path(phase4_json),
        },
        "thresholds": {
            "close_band_margin": CLOSE_BAND_MARGIN,
            "near_tie_margin": NEAR_TIE_MARGIN,
            "wide_version_candidate_count": WIDE_VERSION_CANDIDATE_COUNT,
        },
        "policy": [
            "Run family-identity pruning as an offline simulation before changing production matching.",
            "Treat decision-row pressure as pre-reportability work, not as emitted SBOM component count.",
            "Preserve every version inside close bands; ambiguity reporting is safer than forced pruning.",
            "Measure controlled and real rows together so a speed-oriented filter cannot silently remove source-correct versions.",
            "Prefer coordinate-family and class-subset shortlist experiments before adding another global score weight.",
        ],
        "next_experiment": [
            "Compute a cheap coordinate-family identity score from package and class-subset overlap.",
            "Keep every coordinate within a guarded margin of the best family score.",
            "Run full current scoring only inside the retained coordinate families.",
            "Compare retained source-correct candidates, candidate-slot reduction, controlled regressions, and real source-validated regressions before any production wiring.",
        ],
        "summary": summary,
        "layer_summary": summarize_layers(rows),
        "top_pressure_coordinates": summarize_coordinates(rows)[:20],
        "high_pressure_rows": [row for row in rows if row["high_pressure"]],
        "rows": rows,
        "missing_reports": missing_reports,
        "gates": gates,
    }


def controlled_report_inventory(generated_batch: dict[str, Any]) -> list[dict[str, Any]]:
    inventory = []
    for fixture in generated_batch.get("fixtures", []):
        report_path = fixture.get("report_path")
        if not report_path:
            continue
        inventory.append(
            {
                "dataset_layer": "controlled-generated",
                "case_id": str(fixture.get("name") or report_path),
                "case_name": str(fixture.get("name") or report_path),
                "category_or_role": str(fixture.get("category") or "unknown"),
                "report_path": normalize_path(report_path),
                "expected_coordinate": str(fixture.get("coordinate") or ""),
                "expected_versions": [str(fixture.get("version") or "")],
                "source_versions_by_coordinate": {},
            }
        )
    return deduplicate_inventory(inventory)


def real_report_inventory(phase4: dict[str, Any]) -> list[dict[str, Any]]:
    by_report: dict[str, dict[str, Any]] = {}
    for row in phase4.get("real_component_rows", []):
        report_path = normalize_path(row.get("report_path") or "")
        if not report_path:
            continue
        item = by_report.setdefault(
            report_path,
            {
                "dataset_layer": "real-apk",
                "case_id": str(row.get("case_id") or report_path),
                "case_name": str(row.get("case_name") or row.get("case_id") or report_path),
                "category_or_role": str(row.get("role") or "unknown"),
                "report_path": report_path,
                "expected_coordinate": "",
                "expected_versions": [],
                "source_versions_by_coordinate": {},
            },
        )
        coordinate = str(row.get("coordinate") or "")
        source_versions = [str(version) for version in row.get("source_versions", [])]
        if coordinate and source_versions:
            item["source_versions_by_coordinate"][coordinate] = source_versions
    return list(by_report.values())


def deduplicate_inventory(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}
    for item in inventory:
        by_path.setdefault(item["report_path"], item)
    return list(by_path.values())


def build_pressure_row(item: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    width = int(decision.get("reference_versions_considered") or 0)
    gap_to_next = round(float(decision.get("gap_to_next") or 0.0), 6)
    coordinate = str(decision.get("coordinate") or "")
    source_versions = source_versions_for_decision(item, coordinate)
    evidence = decision.get("evidence", {})
    package_score = float(evidence.get("package_score") or 0.0)
    class_score = float(evidence.get("class_score") or 0.0)
    method_score = float(evidence.get("method_score") or 0.0)
    dependency_score = float(evidence.get("dependency_score") or 0.0)
    literal_score = float(evidence.get("literal_score") or 0.0)
    close_band = width >= 2 and gap_to_next < CLOSE_BAND_MARGIN
    near_tie = width >= 2 and gap_to_next < NEAR_TIE_MARGIN
    wide = width >= WIDE_VERSION_CANDIDATE_COUNT
    return {
        "dataset_layer": item["dataset_layer"],
        "case_id": item["case_id"],
        "case_name": item["case_name"],
        "category_or_role": item["category_or_role"],
        "report_path": item["report_path"],
        "coordinate": coordinate,
        "selected_version": decision.get("selected_version"),
        "source_versions": source_versions,
        "selected_matches_source": (
            str(decision.get("selected_version") or "") in source_versions
            if source_versions
            else None
        ),
        "reference_versions_considered": width,
        "gap_to_next": gap_to_next,
        "version_status": decision.get("version_status"),
        "identity_status": decision.get("identity_status"),
        "package_score": round(package_score, 6),
        "class_score": round(class_score, 6),
        "method_score": round(method_score, 6),
        "dependency_score": round(dependency_score, 6),
        "literal_score": round(literal_score, 6),
        "matched_packages": int(evidence.get("matched_packages") or 0),
        "matched_classes": int(evidence.get("matched_classes") or 0),
        "matched_methods": int(evidence.get("matched_methods") or 0),
        "matched_dependency_edges": int(evidence.get("matched_dependency_edges") or 0),
        "matched_string_literals": int(evidence.get("matched_string_literals") or 0),
        "family_identity_proxy_score": family_identity_proxy_score(
            package_score=package_score,
            class_score=class_score,
        ),
        "close_band": close_band,
        "near_tie": near_tie,
        "wide_version_family": wide,
        "high_pressure": close_band or wide,
        "pressure_classification": pressure_classification(width, gap_to_next),
        "alternatives": decision.get("alternatives", []),
    }


def family_identity_proxy_score(*, package_score: float, class_score: float) -> float:
    return round((0.35 * package_score) + (0.65 * class_score), 6)


def source_versions_for_decision(item: dict[str, Any], coordinate: str) -> list[str]:
    source_versions = item.get("source_versions_by_coordinate", {}).get(coordinate, [])
    if source_versions:
        return [str(version) for version in source_versions]
    if coordinate == item.get("expected_coordinate"):
        return [str(version) for version in item.get("expected_versions", []) if version]
    return []


def pressure_classification(width: int, gap_to_next: float) -> str:
    if width <= 1:
        return "single-reference"
    if gap_to_next < NEAR_TIE_MARGIN:
        return "near-tie-preserve-band"
    if gap_to_next < CLOSE_BAND_MARGIN:
        return "close-band-preserve-alternatives"
    if width >= WIDE_VERSION_CANDIDATE_COUNT:
        return "wide-family-simulate-prefilter"
    return "narrow-separated"


def summarize(
    inventory: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    missing_reports: list[dict[str, Any]],
    failed_gates: list[dict[str, Any]],
) -> dict[str, Any]:
    widths = [int(row["reference_versions_considered"]) for row in rows]
    return {
        "reports_in_inventory": len(inventory),
        "reports_loaded": len(inventory) - len(missing_reports),
        "missing_reports": len(missing_reports),
        "decision_rows": len(rows),
        "candidate_version_slots": sum(widths),
        "average_candidate_versions_per_decision": round(
            sum(widths) / len(widths), 6
        )
        if widths
        else 0.0,
        "maximum_candidate_versions_in_one_decision": max(widths, default=0),
        "single_reference_rows": sum(1 for row in rows if row["reference_versions_considered"] <= 1),
        "multi_version_rows": sum(1 for row in rows if row["reference_versions_considered"] >= 2),
        "wide_version_family_rows": sum(1 for row in rows if row["wide_version_family"]),
        "close_band_rows": sum(1 for row in rows if row["close_band"]),
        "near_tie_rows": sum(1 for row in rows if row["near_tie"]),
        "high_pressure_rows": sum(1 for row in rows if row["high_pressure"]),
        "failed_gates": len(failed_gates),
    }


def summarize_layers(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    layers = sorted(set(str(row["dataset_layer"]) for row in rows))
    return [summarize_row_group(layer, [row for row in rows if row["dataset_layer"] == layer]) for layer in layers]


def summarize_coordinates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    coordinates = sorted(set(str(row["coordinate"]) for row in rows))
    summaries = [
        summarize_row_group(
            coordinate,
            [row for row in rows if row["coordinate"] == coordinate],
            key_name="coordinate",
        )
        for coordinate in coordinates
    ]
    summaries.sort(
        key=lambda row: (
            row["high_pressure_rows"],
            row["candidate_version_slots"],
            row["decision_rows"],
            row["coordinate"],
        ),
        reverse=True,
    )
    return summaries


def summarize_row_group(
    key: str,
    rows: list[dict[str, Any]],
    *,
    key_name: str = "dataset_layer",
) -> dict[str, Any]:
    widths = [int(row["reference_versions_considered"]) for row in rows]
    return {
        key_name: key,
        "decision_rows": len(rows),
        "candidate_version_slots": sum(widths),
        "average_candidate_versions": round(sum(widths) / len(widths), 6) if widths else 0.0,
        "maximum_candidate_versions": max(widths, default=0),
        "single_reference_rows": sum(1 for row in rows if row["reference_versions_considered"] <= 1),
        "wide_version_family_rows": sum(1 for row in rows if row["wide_version_family"]),
        "close_band_rows": sum(1 for row in rows if row["close_band"]),
        "near_tie_rows": sum(1 for row in rows if row["near_tie"]),
        "high_pressure_rows": sum(1 for row in rows if row["high_pressure"]),
        "pressure_classifications": dict(
            sorted(Counter(str(row["pressure_classification"]) for row in rows).items())
        ),
    }


def build_gates(
    inventory: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    missing_reports: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    layers = {str(row["dataset_layer"]) for row in rows}
    return [
        gate(
            "report-inventory-present",
            fail_count=0 if inventory else 1,
            evidence=f"{len(inventory)} report paths recorded.",
        ),
        gate(
            "report-decisions-loaded",
            fail_count=0 if rows else 1,
            evidence=f"{len(rows)} decision rows loaded.",
        ),
        gate(
            "controlled-and-real-layers-present",
            fail_count=0 if {"controlled-generated", "real-apk"} <= layers else 1,
            evidence=f"Layers loaded: {', '.join(sorted(layers)) or 'none'}.",
        ),
        gate(
            "missing-reports-preserved",
            fail_count=0,
            evidence=f"{len(missing_reports)} missing reports recorded explicitly.",
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
        return "coarse-to-fine-pruning-diagnostic-incomplete"
    if summary["high_pressure_rows"]:
        return "coarse-to-fine-pruning-diagnostic-family-first-next"
    return "coarse-to-fine-pruning-diagnostic-no-pressure-found"


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
    thresholds = payload["thresholds"]
    lines = [
        "# Coarse-to-Fine Candidate-Pruning Diagnostics",
        "",
        "Generated by `scripts/build_coarse_to_fine_pruning_diagnostics.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        f"Recommendation: `{payload['recommendation']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Reports in inventory: `{summary['reports_in_inventory']}`",
        f"- Reports loaded: `{summary['reports_loaded']}`",
        f"- Missing reports recorded: `{summary['missing_reports']}`",
        f"- Decision rows: `{summary['decision_rows']}`",
        f"- Candidate-version slots after the current score threshold: `{summary['candidate_version_slots']}`",
        f"- Average versions per decision: `{summary['average_candidate_versions_per_decision']}`",
        f"- Maximum versions in one decision: `{summary['maximum_candidate_versions_in_one_decision']}`",
        f"- Multi-version rows: `{summary['multi_version_rows']}`",
        f"- Wide version-family rows (`>= {thresholds['wide_version_candidate_count']}` versions): `{summary['wide_version_family_rows']}`",
        f"- Close-band rows (`gap < {thresholds['close_band_margin']}`): `{summary['close_band_rows']}`",
        f"- Near-tie rows (`gap < {thresholds['near_tie_margin']}`): `{summary['near_tie_rows']}`",
        f"- High-pressure rows: `{summary['high_pressure_rows']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        "",
        "## Layer Summary",
        "",
        "| Layer | Decisions | Candidate slots | Average width | Maximum width | Wide rows | Close bands | Near ties | High pressure |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["layer_summary"]:
        lines.append(
            "| "
            f"{md(row['dataset_layer'])} | "
            f"{row['decision_rows']} | "
            f"{row['candidate_version_slots']} | "
            f"{row['average_candidate_versions']} | "
            f"{row['maximum_candidate_versions']} | "
            f"{row['wide_version_family_rows']} | "
            f"{row['close_band_rows']} | "
            f"{row['near_tie_rows']} | "
            f"{row['high_pressure_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Top Pressure Coordinates",
            "",
            "| Coordinate | Decisions | Candidate slots | Average width | Maximum width | Wide rows | Close bands | Near ties | High pressure |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["top_pressure_coordinates"]:
        lines.append(
            "| "
            f"`{md(row['coordinate'])}` | "
            f"{row['decision_rows']} | "
            f"{row['candidate_version_slots']} | "
            f"{row['average_candidate_versions']} | "
            f"{row['maximum_candidate_versions']} | "
            f"{row['wide_version_family_rows']} | "
            f"{row['close_band_rows']} | "
            f"{row['near_tie_rows']} | "
            f"{row['high_pressure_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Highest-Pressure Rows",
            "",
            "| Layer | Case | Coordinate | Selected | Source or expected | Width | Gap | Classification |",
            "|---|---|---|---|---|---:|---:|---|",
        ]
    )
    for row in payload["high_pressure_rows"][:50]:
        lines.append(
            "| "
            f"{md(row['dataset_layer'])} | "
            f"{md(row['case_name'])} | "
            f"`{md(row['coordinate'])}` | "
            f"{md(row.get('selected_version') or 'none')} | "
            f"{md(', '.join(row.get('source_versions') or []) or 'not recorded')} | "
            f"{row['reference_versions_considered']} | "
            f"{row['gap_to_next']} | "
            f"`{md(row['pressure_classification'])}` |"
        )
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(["", "## Next Offline Experiment", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(payload["next_experiment"], 1))
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
            "The current matcher has enough multi-version and close-band pressure "
            "to justify an offline family-identity prefilter simulation. Keep "
            "close version bands intact, measure source-correct candidate "
            "retention, and require fresh controlled plus real source-validation "
            "regression checks before wiring any pruning into production.",
            "",
        ]
    )
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_exists(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {}


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
