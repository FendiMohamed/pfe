from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

from apk_sbom.dex_analyzer import analyze_apk_dex
from apk_sbom.matcher import (
    FeatureSet,
    ReferenceComponentFeatures,
    feature_set_from_apk_analysis,
    load_reference_components,
    match_apk_to_reference_db,
)


DEFAULT_APK_ROOT = Path("data/test_apks")
DEFAULT_REFERENCE_DB = Path(
    "data/reference_db/reference_features_phase4_multiscale_calibrated_combined.sqlite"
)
DEFAULT_APK_TYPE_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/r8-phase4-scoped-experiment-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md")

FEATURE_WEIGHTS: list[dict[str, str | float]] = [
    {
        "key": "call_chain_opcode_fingerprints",
        "label": "Call-chain opcode fingerprints",
        "weight": 0.25,
    },
    {
        "key": "basic_block_opcode_fingerprints",
        "label": "Basic-block opcode fingerprints",
        "weight": 0.25,
    },
    {
        "key": "class_neighbor_summaries",
        "label": "Class-neighbor summaries",
        "weight": 0.20,
    },
    {
        "key": "field_operation_sequences",
        "label": "Field-operation sequences",
        "weight": 0.15,
    },
    {
        "key": "literal_context_features",
        "label": "Literal/context features",
        "weight": 0.15,
    },
]

CONTROLLED_R8_CASES: list[dict[str, str]] = [
    {
        "slug": "generated-gson-2-8-9-r8-rename",
        "category": "r8-rename",
        "coordinate": "com.google.code.gson:gson",
        "expected_version": "2.8.9",
    },
    {
        "slug": "generated-gson-2-8-9-r8-shrink",
        "category": "r8-shrink",
        "coordinate": "com.google.code.gson:gson",
        "expected_version": "2.8.9",
    },
    {
        "slug": "generated-commons-codec-1-16-1-r8-rename",
        "category": "r8-rename",
        "coordinate": "commons-codec:commons-codec",
        "expected_version": "1.16.1",
    },
    {
        "slug": "generated-commons-codec-1-16-1-r8-shrink",
        "category": "r8-shrink",
        "coordinate": "commons-codec:commons-codec",
        "expected_version": "1.16.1",
    },
]

for _slug, _coordinate, _version in [
    ("gson", "com.google.code.gson:gson", "2.8.9"),
    ("jackson-databind", "com.fasterxml.jackson.core:jackson-databind", "2.13.5"),
    ("okhttp", "com.squareup.okhttp3:okhttp", "4.10.0"),
    ("retrofit", "com.squareup.retrofit2:retrofit", "2.8.1"),
    ("commons-codec", "commons-codec:commons-codec", "1.16.1"),
]:
    for _variant, _category in [
        ("r8-optimize", "r8-optimize"),
        ("r8-shrink-optimize", "r8-shrink-optimize"),
        ("r8-repackage", "r8-package-flattening"),
        ("r8-inline-stress", "r8-inline-stress"),
    ]:
        CONTROLLED_R8_CASES.append(
            {
                "slug": f"generated-{_slug}-{_version.replace('.', '-')}-{_variant}",
                "category": _category,
                "coordinate": _coordinate,
                "expected_version": _version,
            }
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Phase 4 scoped R8 multi-scale diagnostics without changing scoring.",
    )
    parser.add_argument("--apk-root", default=str(DEFAULT_APK_ROOT))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--apk-type-json", default=str(DEFAULT_APK_TYPE_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        apk_root=Path(args.apk_root),
        reference_db=Path(args.reference_db),
        apk_type_json=Path(args.apk_type_json),
    )

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "controlled_cases": len(payload["controlled_cases"]),
                "real_component_rows": len(payload["real_component_rows"]),
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(*, apk_root: Path, reference_db: Path, apk_type_json: Path) -> dict[str, Any]:
    references_by_coordinate = load_references_by_coordinate(reference_db)
    controlled_cases = [
        evaluate_case(
            case,
            apk_root=apk_root,
            reference_db=reference_db,
            references=references_by_coordinate.get(case["coordinate"], []),
        )
        for case in CONTROLLED_R8_CASES
    ]
    real_component_rows = evaluate_real_layer_cases(
        apk_type_json=apk_type_json,
        references_by_coordinate=references_by_coordinate,
    )
    outcome_counts = dict(
        sorted(
            Counter(
                [
                    *(case["outcome"] for case in controlled_cases),
                    *(row["outcome"] for row in real_component_rows),
                ]
            ).items()
        )
    )
    controlled_outcome_counts = dict(
        sorted(Counter(case["outcome"] for case in controlled_cases).items())
    )
    real_outcome_counts = dict(
        sorted(Counter(row["outcome"] for row in real_component_rows).items())
    )
    category_counts = summarize_by_category(controlled_cases)
    real_layer_counts = summarize_real_layers(real_component_rows)
    return {
        "schema_version": 1,
        "sources": {
            "apk_root": normalize_path(apk_root),
            "reference_db": normalize_path(reference_db),
            "apk_type_json": normalize_path(apk_type_json),
        },
        "verdict": verdict_from_outcomes(outcome_counts),
        "policy": [
            "This is a Phase 4 diagnostic experiment only.",
            "The offline multi-scale rank is not used by match-apk, generate-report, SBOM output, or vulnerability labeling.",
            "Any regression-risk row blocks global promotion of these signals.",
            "A future scoped scorer must improve target cases and pass fresh clean/partial source-validated controls.",
        ],
        "feature_weights": FEATURE_WEIGHTS,
        "summary": {
            "controlled_cases": len(controlled_cases),
            "real_component_rows": len(real_component_rows),
            "outcome_counts": outcome_counts,
            "controlled_outcome_counts": controlled_outcome_counts,
            "real_outcome_counts": real_outcome_counts,
            "category_counts": category_counts,
            "real_layer_counts": real_layer_counts,
            "phase5_candidate_scan": phase5_candidate_scan(controlled_cases, real_component_rows),
        },
        "controlled_cases": controlled_cases,
        "real_component_rows": real_component_rows,
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


def evaluate_case(
    case: dict[str, str],
    *,
    apk_root: Path,
    reference_db: Path,
    references: list[ReferenceComponentFeatures],
) -> dict[str, Any]:
    apk_path = apk_root / f"{case['slug']}.apk"
    if not apk_path.exists():
        return {
            **case,
            "apk_path": normalize_path(apk_path),
            "baseline_selected_version": None,
            "diagnostic_selected_version": None,
            "outcome": "missing-apk",
            "top_diagnostic_versions": [],
        }

    baseline_selected = baseline_selected_version(
        apk_path,
        reference_db=reference_db,
        coordinate=case["coordinate"],
    )
    analysis = analyze_apk_dex(apk_path, include_members=True)
    apk_features = feature_set_from_apk_analysis(analysis)
    ranked = rank_reference_versions(apk_features, references)
    diagnostic_selected = ranked[0]["version"] if ranked else None
    outcome = classify_experiment_row(
        expected_version=case["expected_version"],
        baseline_selected_version=baseline_selected,
        diagnostic_selected_version=diagnostic_selected,
    )
    return {
        **case,
        "apk_path": normalize_path(apk_path),
        "baseline_selected_version": baseline_selected,
        "diagnostic_selected_version": diagnostic_selected,
        "outcome": outcome,
        "parse_errors": [error.dex_file for error in analysis.parse_errors],
        "top_diagnostic_versions": ranked[:3],
    }


def baseline_selected_version(
    apk_path: Path,
    *,
    reference_db: Path,
    coordinate: str,
) -> str | None:
    summary = match_apk_to_reference_db(
        apk_path,
        db_path=reference_db,
        coordinate=coordinate,
        top=10,
        min_score=0.0,
    )
    decision = next(
        (item for item in summary.decisions if item.coordinate == coordinate),
        None,
    )
    return decision.selected_version if decision else None


def rank_reference_versions(
    apk_features: FeatureSet,
    references: list[ReferenceComponentFeatures],
) -> list[dict[str, Any]]:
    rows = []
    for reference in references:
        feature_scores = multiscale_feature_scores(apk_features, reference.features)
        rows.append(
            {
                "version": reference.version,
                "coordinate": reference.coordinate,
                "diagnostic_score": round(weighted_multiscale_score(feature_scores), 6),
                "feature_scores": {
                    key: round(value, 6) for key, value in sorted(feature_scores.items())
                },
            }
        )
    return sorted(
        rows,
        key=lambda item: (item["diagnostic_score"], item["version"]),
        reverse=True,
    )


def evaluate_real_layer_cases(
    *,
    apk_type_json: Path,
    references_by_coordinate: dict[str, list[ReferenceComponentFeatures]],
) -> list[dict[str, Any]]:
    if not apk_type_json.exists():
        return []
    payload = json.loads(apk_type_json.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    feature_cache: dict[str, FeatureSet | None] = {}
    for real_case in payload.get("real_cases", []):
        report_path = Path(str(real_case.get("report_path") or ""))
        if not report_path.exists():
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        apk_path = Path(str(report.get("apk", {}).get("apk_path") or ""))
        detected_by_coordinate = detected_components_by_coordinate(report)
        validation_path_value = str(real_case.get("validation_path") or "")
        validation_by_coordinate = (
            validation_results_by_coordinate(Path(validation_path_value))
            if validation_path_value
            else {}
        )
        covered_coordinates = sorted(
            coordinate
            for coordinate in detected_by_coordinate
            if coordinate in references_by_coordinate
        )
        if not covered_coordinates:
            continue
        feature_key = normalize_path(apk_path)
        if feature_key not in feature_cache:
            feature_cache[feature_key] = feature_set_for_apk(apk_path)
        apk_features = feature_cache[feature_key]
        for coordinate in covered_coordinates:
            references = references_by_coordinate.get(coordinate, [])
            detected = detected_by_coordinate[coordinate]
            validation = validation_by_coordinate.get(coordinate)
            ranked = rank_reference_versions(apk_features, references) if apk_features else []
            diagnostic_selected = ranked[0]["version"] if ranked else None
            source_versions = validation.get("source_versions", []) if validation else []
            validation_status = validation.get("status") if validation else None
            baseline_selected = str(detected.get("version") or "")
            outcome = classify_real_experiment_row(
                baseline_selected_version=baseline_selected,
                diagnostic_selected_version=diagnostic_selected,
                source_versions=source_versions,
                validation_status=validation_status,
                reference_count=len(references),
                has_apk_features=apk_features is not None,
            )
            rows.append(
                {
                    "case_id": real_case.get("case_id"),
                    "case_name": real_case.get("name"),
                    "role": real_case.get("role"),
                    "tags": real_case.get("tags", []),
                    "apk_path": normalize_path(apk_path),
                    "report_path": normalize_path(report_path),
                    "validation_path": normalize_path(real_case.get("validation_path") or ""),
                    "coordinate": coordinate,
                    "baseline_selected_version": baseline_selected or None,
                    "diagnostic_selected_version": diagnostic_selected,
                    "source_versions": source_versions,
                    "validation_status": validation_status,
                    "reference_versions_available": len(references),
                    "outcome": outcome,
                    "top_diagnostic_versions": ranked[:3],
                }
            )
    return rows


def feature_set_for_apk(apk_path: Path) -> FeatureSet | None:
    if not apk_path.exists():
        return None
    analysis = analyze_apk_dex(apk_path, include_members=True)
    return feature_set_from_apk_analysis(analysis)


def detected_components_by_coordinate(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    detected: dict[str, dict[str, Any]] = {}
    for component in report.get("detected_components", []):
        group = component.get("group")
        artifact = component.get("artifact")
        if not group or not artifact:
            continue
        coordinate = f"{group}:{artifact}"
        detected.setdefault(coordinate, component)
    return detected


def validation_results_by_coordinate(validation_path: Path) -> dict[str, dict[str, Any]]:
    if not str(validation_path):
        return {}
    if not validation_path.exists():
        return {}
    if validation_path.is_dir():
        return {}
    payload = json.loads(validation_path.read_text(encoding="utf-8"))
    results: dict[str, dict[str, Any]] = {}
    for row in payload.get("results", []):
        if row.get("kind") != "sbom-component":
            continue
        coordinate = row.get("coordinate")
        if not coordinate:
            continue
        results.setdefault(str(coordinate), row)
    return results


def multiscale_feature_scores(left: FeatureSet, right: FeatureSet) -> dict[str, float]:
    return {
        "call_chain_opcode_fingerprints": cosine_similarity(
            left.call_chain_opcode_fingerprints,
            right.call_chain_opcode_fingerprints,
        ),
        "basic_block_opcode_fingerprints": cosine_similarity(
            left.basic_block_opcode_fingerprints,
            right.basic_block_opcode_fingerprints,
        ),
        "class_neighbor_summaries": cosine_similarity(
            left.class_neighbor_summaries,
            right.class_neighbor_summaries,
        ),
        "field_operation_sequences": cosine_similarity(
            left.field_operation_sequences,
            right.field_operation_sequences,
        ),
        "literal_context_features": set_coverage_score(
            left.literal_context_features,
            right.literal_context_features,
        ),
    }


def weighted_multiscale_score(feature_scores: dict[str, float]) -> float:
    total = 0.0
    weight_total = 0.0
    for item in FEATURE_WEIGHTS:
        key = str(item["key"])
        weight = float(item["weight"])
        total += feature_scores.get(key, 0.0) * weight
        weight_total += weight
    if weight_total == 0:
        return 0.0
    return total / weight_total


def classify_experiment_row(
    *,
    expected_version: str,
    baseline_selected_version: str | None,
    diagnostic_selected_version: str | None,
) -> str:
    if diagnostic_selected_version is None:
        return "missing-diagnostic-rank"
    baseline_correct = baseline_selected_version == expected_version
    diagnostic_correct = diagnostic_selected_version == expected_version
    if baseline_correct and diagnostic_correct:
        return "aligned-control-clean"
    if not baseline_correct and diagnostic_correct:
        return "potential-target-improvement"
    if baseline_correct and not diagnostic_correct:
        return "regression-risk-do-not-promote"
    if baseline_selected_version == diagnostic_selected_version:
        return "unchanged-mismatch"
    return "conflicting-mismatch"


def classify_real_experiment_row(
    *,
    baseline_selected_version: str | None,
    diagnostic_selected_version: str | None,
    source_versions: list[str],
    validation_status: str | None,
    reference_count: int,
    has_apk_features: bool,
) -> str:
    if not has_apk_features:
        return "real-missing-apk-or-features"
    if reference_count <= 1:
        return "real-single-reference-not-rankable"
    if diagnostic_selected_version is None:
        return "real-missing-diagnostic-rank"
    if not source_versions:
        return "real-layer-covered-unvalidated"
    baseline_correct = validation_status == "confirmed" or baseline_selected_version in source_versions
    diagnostic_correct = diagnostic_selected_version in source_versions
    if baseline_correct and diagnostic_correct:
        return "real-aligned-source-clean"
    if not baseline_correct and diagnostic_correct:
        return "real-potential-target-improvement"
    if baseline_correct and not diagnostic_correct:
        return "real-regression-risk-do-not-promote"
    if baseline_selected_version == diagnostic_selected_version:
        return "real-unchanged-source-mismatch"
    return "real-conflicting-source-mismatch"


def verdict_from_outcomes(outcome_counts: dict[str, int]) -> str:
    if outcome_counts.get("regression-risk-do-not-promote", 0) or outcome_counts.get(
        "real-regression-risk-do-not-promote", 0
    ):
        return "phase4-scoped-diagnostic-reject-global-promotion"
    if outcome_counts.get("potential-target-improvement", 0) or outcome_counts.get(
        "real-potential-target-improvement", 0
    ):
        return "phase4-scoped-diagnostic-candidate-needs-real-controls"
    if outcome_counts.get("missing-apk", 0) or outcome_counts.get("missing-diagnostic-rank", 0):
        return "phase4-scoped-diagnostic-incomplete"
    return "phase4-scoped-diagnostic-no-scoring-change"


def summarize_by_category(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_category: dict[str, Counter[str]] = {}
    for case in cases:
        by_category.setdefault(case["category"], Counter())[case["outcome"]] += 1
    return [
        {"category": category, "outcomes": dict(sorted(counter.items()))}
        for category, counter in sorted(by_category.items())
    ]


def summarize_real_layers(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_role: dict[str, Counter[str]] = {}
    for row in rows:
        role = str(row.get("role") or "unknown")
        by_role.setdefault(role, Counter())[str(row.get("outcome") or "unknown")] += 1
    return [
        {"role": role, "outcomes": dict(sorted(counter.items()))}
        for role, counter in sorted(by_role.items())
    ]


def phase5_candidate_scan(
    controlled_cases: list[dict[str, Any]],
    real_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    improvements = [
        {
            "case": row.get("case_name") or row.get("case_id"),
            "role": row.get("role"),
            "coordinate": row.get("coordinate"),
            "source_versions": row.get("source_versions", []),
            "baseline_selected": row.get("baseline_selected_version"),
            "diagnostic_selected": row.get("diagnostic_selected_version"),
        }
        for row in real_rows
        if row.get("outcome") == "real-potential-target-improvement"
    ]
    controlled_regressions = [
        {
            "case": row.get("slug"),
            "category": row.get("category"),
            "coordinate": row.get("coordinate"),
            "expected": row.get("expected_version"),
            "baseline_selected": row.get("baseline_selected_version"),
            "diagnostic_selected": row.get("diagnostic_selected_version"),
        }
        for row in controlled_cases
        if row.get("outcome") == "regression-risk-do-not-promote"
    ]
    real_regressions = [
        {
            "case": row.get("case_name") or row.get("case_id"),
            "role": row.get("role"),
            "coordinate": row.get("coordinate"),
            "source_versions": row.get("source_versions", []),
            "baseline_selected": row.get("baseline_selected_version"),
            "diagnostic_selected": row.get("diagnostic_selected_version"),
        }
        for row in real_rows
        if row.get("outcome") == "real-regression-risk-do-not-promote"
    ]
    blockers_by_coordinate = Counter(
        [
            *(str(row.get("coordinate")) for row in controlled_regressions),
            *(str(row.get("coordinate")) for row in real_regressions),
        ]
    )
    return {
        "candidate_improvements": improvements,
        "controlled_regression_count": len(controlled_regressions),
        "real_regression_count": len(real_regressions),
        "clean_real_regression_count": sum(
            1 for row in real_regressions if row.get("role") == "clean-source-validated"
        ),
        "top_blocking_coordinates": [
            {"coordinate": coordinate, "regressions": count}
            for coordinate, count in blockers_by_coordinate.most_common(10)
        ],
        "controlled_regressions": controlled_regressions,
        "real_regressions": real_regressions,
    }


def cosine_similarity(left: dict[str, int], right: dict[str, int]) -> float:
    if not left or not right:
        return 0.0
    if len(left) <= len(right):
        shared = set(left) & set(right)
    else:
        shared = set(right) & set(left)
    numerator = sum(left[key] * right[key] for key in shared)
    left_norm = sum(value * value for value in left.values())
    right_norm = sum(value * value for value in right.values())
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / ((left_norm**0.5) * (right_norm**0.5))


def set_coverage_score(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(right)


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# R8 Phase 4 Scoped Experiment Diagnostics",
        "",
        "Generated by `scripts/build_r8_phase4_scoped_experiment_diagnostics.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        "This is an offline diagnostic experiment. It ranks controlled R8 cases with the Phase 3 multi-scale features, but does not change matcher scoring, selected versions, SBOM components, or vulnerability labels.",
        "",
        "## Summary",
        "",
        f"- Controlled cases: `{payload['summary']['controlled_cases']}`",
        f"- Real APK component rows covered by the Phase 4 multi-scale DB: `{payload['summary']['real_component_rows']}`",
        "- Outcome counts: "
        + ", ".join(
            f"`{key}`={value}"
            for key, value in payload["summary"]["outcome_counts"].items()
        ),
        "",
            "## Controlled Category Outcomes",
            "",
            "| Category | Outcomes |",
            "|---|---|",
    ]
    for row in payload["summary"]["category_counts"]:
        outcomes = ", ".join(f"`{key}`={value}" for key, value in row["outcomes"].items())
        lines.append(f"| {md(row['category'])} | {outcomes} |")

    lines.extend(
        [
            "",
            "## Controlled Case Results",
            "",
            "| Case | Category | Expected | Baseline selected | Diagnostic selected | Outcome |",
            "|---|---|---|---|---|---|",
        ]
    )
    for case in payload["controlled_cases"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{md(case['slug'])}`",
                    md(case["category"]),
                    md(case["expected_version"]),
                    md(case.get("baseline_selected_version") or "none"),
                    md(case.get("diagnostic_selected_version") or "none"),
                    f"`{md(case['outcome'])}`",
                ]
            )
            + " |"
        )

    scan = payload["summary"]["phase5_candidate_scan"]
    lines.extend(
        [
            "",
            "## Phase 5 Candidate Scan",
            "",
            f"- Potential real source-validated improvements: `{len(scan['candidate_improvements'])}`",
            f"- Controlled regression blockers: `{scan['controlled_regression_count']}`",
            f"- Real source-validated regression blockers: `{scan['real_regression_count']}`",
            f"- Clean real regression blockers: `{scan['clean_real_regression_count']}`",
            "",
            "| Candidate improvement | Coordinate | Source version(s) | Baseline | Diagnostic |",
            "|---|---|---|---|---|",
        ]
    )
    for row in scan["candidate_improvements"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["case"]),
                    md(row["coordinate"]),
                    md(", ".join(row.get("source_versions") or [])),
                    md(row.get("baseline_selected") or "none"),
                    md(row.get("diagnostic_selected") or "none"),
                ]
            )
            + " |"
        )
    if not scan["candidate_improvements"]:
        lines.append("| none | none | none | none | none |")

    lines.extend(
        [
            "",
            "| Blocking coordinate | Regression rows |",
            "|---|---:|",
        ]
    )
    for row in scan["top_blocking_coordinates"]:
        lines.append(f"| {md(row['coordinate'])} | {row['regressions']} |")

    lines.extend(
        [
            "",
            "## Real APK Layer Outcomes",
            "",
            "These rows use existing real APK reports and source-validation artifacts where available. A row is included only when the Phase 4 multi-scale reference DB has the emitted coordinate, so this is a coverage-aware diagnostic rather than a full real-APK rerun.",
            "",
            "| Role | Outcomes |",
            "|---|---|",
        ]
    )
    for row in payload["summary"]["real_layer_counts"]:
        outcomes = ", ".join(f"`{key}`={value}" for key, value in row["outcomes"].items())
        lines.append(f"| {md(row['role'])} | {outcomes} |")

    lines.extend(
        [
            "",
            "## Real APK Component Rows",
            "",
            "| Case | Role | Coordinate | Source version(s) | Baseline selected | Diagnostic selected | Outcome |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["real_component_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row.get("case_name") or row.get("case_id")),
                    md(row.get("role")),
                    md(row["coordinate"]),
                    md(", ".join(row.get("source_versions") or []) or "not validated"),
                    md(row.get("baseline_selected_version") or "none"),
                    md(row.get("diagnostic_selected_version") or "none"),
                    f"`{md(row['outcome'])}`",
                ]
            )
            + " |"
        )

    lines.extend(["", "## Feature Blend", "", "| Feature | Weight |", "|---|---:|"])
    for item in payload["feature_weights"]:
        lines.append(f"| {md(item['label'])} | {float(item['weight']):.2f} |")

    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Do not promote these multi-scale signals into default scoring from this diagnostic alone. The expanded layered pass finds a few real source-validated improvement candidates, but it also contains controlled, clean-real, and partial-real regression-risk rows. A scorer change still needs a narrower trigger and fresh clean/partial source-validation controls.",
            "",
        ]
    )
    return "\n".join(lines)


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
