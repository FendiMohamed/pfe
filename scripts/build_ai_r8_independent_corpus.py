from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_TRAINING_DATASET_JSON = Path(
    "data/results/experiments/ai-r8-assistant/training-dataset.json"
)
DEFAULT_ROUTER_JSON = Path("data/results/evaluation/hybrid-matcher-router-v1.json")
DEFAULT_STRUCTURAL_GATE_JSON = Path(
    "data/results/experiments/r8-apk-structural-promotion-gate.json"
)
DEFAULT_LARGE_ANALYSIS_JSON = Path(
    "data/results/evaluation/large-combined-real-apk-analysis.json"
)
DEFAULT_FINAL_SMOKE_JSON = Path(
    "data/results/evaluation/final-hybrid-ai-demo-smoke.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/ai-r8-independent-corpus/independent-corpus.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/AI_R8_INDEPENDENT_CORPUS.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a larger AI/R8 corpus manifest from existing project evidence "
            "lanes. The output separates trainable project-evidence rows from "
            "heldout/report-only validation lanes and does not change matcher, "
            "SBOM, or CVE behavior."
        )
    )
    parser.add_argument("--training-dataset-json", default=str(DEFAULT_TRAINING_DATASET_JSON))
    parser.add_argument("--router-json", default=str(DEFAULT_ROUTER_JSON))
    parser.add_argument("--structural-gate-json", default=str(DEFAULT_STRUCTURAL_GATE_JSON))
    parser.add_argument("--large-analysis-json", default=str(DEFAULT_LARGE_ANALYSIS_JSON))
    parser.add_argument("--final-smoke-json", default=str(DEFAULT_FINAL_SMOKE_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        training_dataset_json=args.training_dataset_json,
        router_json=args.router_json,
        structural_gate_json=args.structural_gate_json,
        large_analysis_json=args.large_analysis_json,
        final_smoke_json=args.final_smoke_json,
    )
    result = write_outputs(payload, output_json=args.output_json, output_doc=args.output_doc)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_payload(
    *,
    training_dataset_json: str | Path = DEFAULT_TRAINING_DATASET_JSON,
    router_json: str | Path = DEFAULT_ROUTER_JSON,
    structural_gate_json: str | Path = DEFAULT_STRUCTURAL_GATE_JSON,
    large_analysis_json: str | Path = DEFAULT_LARGE_ANALYSIS_JSON,
    final_smoke_json: str | Path = DEFAULT_FINAL_SMOKE_JSON,
) -> dict[str, Any]:
    training = read_json(training_dataset_json)
    router = read_json(router_json)
    structural_gate = read_json(structural_gate_json)
    large_analysis = read_json(large_analysis_json)
    final_smoke = read_json(final_smoke_json)

    rows: list[dict[str, Any]] = []
    rows.extend(training_rows(training))
    rows.extend(router_rows(router))
    rows.extend(structural_gate_rows(structural_gate))
    rows.extend(source_validation_control_rows(large_analysis))
    rows.extend(final_smoke_rows(final_smoke))

    partition_counts = Counter(row["partition"] for row in rows)
    label_counts = Counter(row["label"] for row in rows)
    trainable_rows = sum(1 for row in rows if row["training_eligible"])
    heldout_rows = len(rows) - trainable_rows
    case_ids = {row["case_id"] for row in rows if row.get("case_id")}
    coordinates = {row["coordinate"] for row in rows if row.get("coordinate")}
    rows_by_case_role = Counter(row.get("case_role") or "unknown" for row in rows)

    return {
        "schema_version": "ai-r8-independent-corpus-v1",
        "report_only": True,
        "default_matcher_unchanged": True,
        "production_wiring": "disabled",
        "scope": (
            "Larger AI/R8 corpus manifest built from distinct project evidence lanes. "
            "Only the original Phase 6A rows are marked training-eligible; router, "
            "structural gate, final smoke, and source-validation controls are heldout "
            "or report-only analysis lanes."
        ),
        "sources": {
            "training_dataset_json": normalize_path(training_dataset_json),
            "router_json": normalize_path(router_json),
            "structural_gate_json": normalize_path(structural_gate_json),
            "large_analysis_json": normalize_path(large_analysis_json),
            "final_smoke_json": normalize_path(final_smoke_json),
        },
        "summary": {
            "rows": len(rows),
            "training_eligible_rows": trainable_rows,
            "heldout_or_report_only_rows": heldout_rows,
            "partitions": dict(sorted(partition_counts.items())),
            "labels": dict(sorted(label_counts.items())),
            "unique_case_ids": len(case_ids),
            "unique_coordinates": len(coordinates),
            "case_roles": dict(sorted(rows_by_case_role.items())),
            "independence_level": "project-heldout-evidence-lanes",
            "external_corpus": False,
            "production_effect": "none",
        },
        "policy": [
            "Do not train production SBOM decisions from heldout report-only lanes.",
            "Use the heldout lanes for ablation, drift checks, smoke checks, and thesis transparency.",
            "Treat source-version fields as labels/evaluation evidence, not APK-only decision evidence.",
            "A truly external independent corpus remains future data-collection work.",
            "This artifact does not change matcher scoring, selected versions, SBOM output, vulnerability labels, or source-validation metrics.",
        ],
        "partition_descriptions": partition_descriptions(),
        "top_coordinates": top_counts(Counter(row["coordinate"] for row in rows if row.get("coordinate"))),
        "top_cases": top_counts(Counter(row["case_id"] for row in rows if row.get("case_id"))),
        "rows": rows,
    }


def training_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, row in enumerate(payload.get("rows", [])):
        rows.append(
            base_row(
                row_id=row.get("row_id") or f"training:{index}",
                partition="phase6a_training_dataset",
                source_artifact="ai-r8-assistant-training-dataset",
                case_id=row.get("case_id"),
                coordinate=row.get("coordinate"),
                label=row.get("label") or "unlabeled",
                candidate_version=row.get("candidate_version"),
                source_version=row.get("source_version"),
                row_source=row.get("row_source"),
                case_role=row.get("context", {}).get("role") or row.get("context", {}).get("row_type"),
                features=row.get("features", {}),
                training_eligible=True,
                recommended_use="train-or-cross-validate-phase6a-model",
                context=row.get("context", {}),
            )
        )
    return rows


def router_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, row in enumerate(payload.get("rows", [])):
        label = str(row.get("recommended_profile") or "unrouted")
        rows.append(
            base_row(
                row_id=row.get("row_id") or f"router:{index}",
                partition="heldout_hybrid_router",
                source_artifact="hybrid-matcher-router-v1",
                case_id=row.get("case_id"),
                coordinate=row.get("coordinate"),
                label=label,
                candidate_version=row.get("candidate_version"),
                source_version=row.get("source_version"),
                row_source=row.get("row_source"),
                case_role=row.get("priority"),
                features=row.get("evidence", {}),
                training_eligible=False,
                recommended_use="heldout-router-ablation-and-priority-analysis",
                context={
                    "recommended_profile": row.get("recommended_profile"),
                    "secondary_profiles": row.get("secondary_profiles", []),
                    "reason_codes": row.get("reason_codes", []),
                    "priority": row.get("priority"),
                },
            )
        )
    return rows


def structural_gate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, row in enumerate(payload.get("rows", [])):
        features = dict(row.get("features", {}))
        features.update(
            {
                "apk_only_gate_passes": bool(row.get("apk_only_gate", {}).get("passes")),
                "production_promotion_candidate": bool(
                    row.get("production_promotion_candidate")
                ),
                "control_risk_rows": row.get("control_context", {}).get(
                    "control_risk_rows",
                    0,
                ),
                "exact_controls": row.get("control_context", {}).get("exact_controls", 0),
            }
        )
        rows.append(
            base_row(
                row_id=row.get("row_id") or f"structural-gate:{index}",
                partition="heldout_apk_only_structural_gate",
                source_artifact="r8-apk-structural-promotion-gate",
                case_id=row.get("case_id"),
                coordinate=row.get("coordinate"),
                label=row.get("classification") or "unclassified",
                candidate_version=row.get("candidate_version"),
                source_version=row.get("source_version"),
                row_source="r8-apk-structural-promotion-gate",
                case_role=row.get("priority"),
                features=features,
                training_eligible=False,
                recommended_use="heldout-apk-only-promotion-gate-analysis",
                context={
                    "classification_reason": row.get("classification_reason"),
                    "gate_decision": row.get("apk_only_gate", {}).get("decision"),
                    "source_evaluation": row.get("source_evaluation", {}).get(
                        "classification"
                    ),
                },
            )
        )
    return rows


def source_validation_control_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, row in enumerate(payload.get("version_rows", [])):
        rows.append(
            base_row(
                row_id=(
                    f"source-control:{row.get('case_id')}:"
                    f"{row.get('coordinate')}:{row.get('tool_selected_version')}:{index}"
                ),
                partition="heldout_106apk_emitted_controls",
                source_artifact="large-combined-real-apk-analysis",
                case_id=row.get("case_id"),
                coordinate=row.get("coordinate"),
                label=row.get("analysis_class") or row.get("status") or "unclassified",
                candidate_version=row.get("tool_selected_version"),
                source_version=row.get("correct_source_versions")
                or row.get("source_requested_versions"),
                row_source="source-validation-emitted-control",
                case_role=row.get("case_role"),
                features={"confidence": row.get("confidence")},
                training_eligible=False,
                recommended_use="heldout-control-matrix-and-regression-analysis",
                context={
                    "match_type": row.get("match_type"),
                    "status": row.get("status"),
                    "case_name": row.get("case_name"),
                },
            )
        )
    return rows


def final_smoke_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, target in enumerate(payload.get("targets", [])):
        comparison = target.get("comparison", {})
        summary = target.get("hybrid_section_summary", {})
        label = "hybrid-report-visible-and-output-unchanged"
        if not comparison.get("unchanged"):
            label = "hybrid-report-output-changed"
        elif not target.get("hybrid_section_visible"):
            label = "hybrid-report-section-missing"
        rows.append(
            base_row(
                row_id=target.get("case_id") or f"final-smoke:{index}",
                partition="heldout_final_hybrid_ai_smoke",
                source_artifact="final-hybrid-ai-demo-smoke",
                case_id=target.get("case_id"),
                coordinate="",
                label=label,
                candidate_version="",
                source_version="",
                row_source="final-demo-smoke",
                case_role=target.get("role"),
                features={
                    "default_component_count": comparison.get("default_component_count"),
                    "hybrid_component_count": comparison.get("hybrid_component_count"),
                    "router_matching_rows": summary.get("router_matching_rows"),
                    "ml_matching_rows": summary.get("ml_matching_rows"),
                    "structural_gate_matching_rows": summary.get(
                        "structural_gate_matching_rows"
                    ),
                    "structural_gate_promotion_candidates": summary.get(
                        "structural_gate_promotion_candidates"
                    ),
                },
                training_eligible=False,
                recommended_use="heldout-demo-smoke-and-report-only-regression-proof",
                context={
                    "apk_path": target.get("apk_path"),
                    "label": target.get("label"),
                    "hybrid_section_visible": target.get("hybrid_section_visible"),
                    "hybrid_section_report_only": target.get(
                        "hybrid_section_report_only"
                    ),
                },
            )
        )
    return rows


def base_row(
    *,
    row_id: object,
    partition: str,
    source_artifact: str,
    case_id: object,
    coordinate: object,
    label: object,
    candidate_version: object,
    source_version: object,
    row_source: object,
    case_role: object,
    features: dict[str, Any],
    training_eligible: bool,
    recommended_use: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "row_id": str(row_id or ""),
        "partition": partition,
        "source_artifact": source_artifact,
        "case_id": str(case_id or ""),
        "coordinate": str(coordinate or ""),
        "label": str(label or "unlabeled"),
        "candidate_version": str(candidate_version or ""),
        "source_version": str(source_version or ""),
        "row_source": str(row_source or ""),
        "case_role": str(case_role or ""),
        "features": sanitize_features(features),
        "training_eligible": training_eligible,
        "recommended_use": recommended_use,
        "report_only": True,
        "context": context or {},
    }


def sanitize_features(features: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, value in sorted((features or {}).items()):
        if isinstance(value, (str, int, float, bool)) or value is None:
            clean[str(key)] = value
    return clean


def partition_descriptions() -> dict[str, str]:
    return {
        "phase6a_training_dataset": (
            "Original Phase 6A row-level ML dataset. This is the only "
            "training-eligible partition in this manifest."
        ),
        "heldout_hybrid_router": (
            "Report-only hybrid matcher strategy rows used for planning and "
            "ablation, not direct model authority."
        ),
        "heldout_apk_only_structural_gate": (
            "APK-only structural gate rows for hard R8 recall promotion analysis."
        ),
        "heldout_106apk_emitted_controls": (
            "Source-validation emitted-version controls from the 106-APK v2/large "
            "analysis lane."
        ),
        "heldout_final_hybrid_ai_smoke": (
            "Final real APK smoke checks proving opt-in hybrid/AI reporting is visible "
            "while report outputs remain unchanged."
        ),
    }


def write_outputs(
    payload: dict[str, Any],
    *,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_doc: str | Path = DEFAULT_OUTPUT_DOC,
) -> dict[str, Any]:
    output_json = Path(output_json)
    output_doc = Path(output_doc)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    summary = payload["summary"]
    return {
        "json": normalize_path(output_json),
        "doc": normalize_path(output_doc),
        "rows": summary["rows"],
        "training_eligible_rows": summary["training_eligible_rows"],
        "heldout_or_report_only_rows": summary["heldout_or_report_only_rows"],
        "partitions": summary["partitions"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# AI R8 Independent Corpus",
        "",
        "Generated by `scripts/build_ai_r8_independent_corpus.py`.",
        "",
        "This artifact turns the larger-corpus future-work point into a concrete, reusable corpus manifest. It is intentionally honest: it is a larger project-heldout corpus, not an external internet-scale corpus.",
        "",
        "## Summary",
        "",
        f"- Total rows: `{summary['rows']}`",
        f"- Training-eligible rows: `{summary['training_eligible_rows']}`",
        f"- Heldout/report-only rows: `{summary['heldout_or_report_only_rows']}`",
        f"- Unique case IDs: `{summary['unique_case_ids']}`",
        f"- Unique coordinates: `{summary['unique_coordinates']}`",
        f"- External corpus: `{str(summary['external_corpus']).lower()}`",
        f"- Production effect: `{summary['production_effect']}`",
        "",
        "## Partitions",
        "",
        "| Partition | Rows | Use |",
        "|---|---:|---|",
    ]
    for partition, count in summary["partitions"].items():
        description = payload["partition_descriptions"].get(partition, "")
        lines.append(f"| `{partition}` | {count} | {description} |")
    lines.extend(
        [
            "",
            "## Labels",
            "",
            "| Label | Rows |",
            "|---|---:|",
        ]
    )
    for label, count in sorted(summary["labels"].items(), key=lambda item: (-item[1], item[0]))[:30]:
        lines.append(f"| `{label}` | {count} |")
    lines.extend(
        [
            "",
            "## Top Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    append_top(lines, payload["top_coordinates"])
    lines.extend(
        [
            "",
            "## Top Cases",
            "",
            "| Case | Rows |",
            "|---|---:|",
        ]
    )
    append_top(lines, payload["top_cases"])
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["policy"])
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


def append_top(lines: list[str], rows: list[dict[str, Any]]) -> None:
    if not rows:
        lines.append("| none | 0 |")
        return
    for row in rows:
        lines.append(f"| `{row['value']}` | {row['rows']} |")


def top_counts(counter: Counter, *, limit: int = 20) -> list[dict[str, Any]]:
    return [
        {"value": str(value), "rows": count}
        for value, count in counter.most_common(limit)
    ]


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_path(path: str | Path) -> str:
    return Path(path).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
