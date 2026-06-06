from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
import re
from typing import Any, Sequence

from apk_sbom.composite_family_shortlist_simulation import (
    PROFILES,
    RECOMMENDED_PROFILE_ID,
    RECOMMENDED_RESCUE_POLICY,
    composite_score,
    should_rescue,
)
from apk_sbom.dex_analyzer import analyze_apk_dex
from apk_sbom.matcher import (
    DEFAULT_API_REFERENCE_WEIGHT,
    DEFAULT_CLASS_WEIGHT,
    DEFAULT_DEPENDENCY_WEIGHT,
    DEFAULT_LITERAL_WEIGHT,
    DEFAULT_METHOD_WEIGHT,
    DEFAULT_OPCODE_NGRAM_WEIGHT,
    DEFAULT_OPCODE_WEIGHT,
    DEFAULT_PACKAGE_WEIGHT,
    DEFAULT_UNIQUE_VERSION_WEIGHT,
    FeatureSet,
    MatchCandidate,
    ReferenceComponentFeatures,
    VersionDecision,
    _dependency_shape_similarity,
    build_version_decisions,
    feature_set_from_apk_analysis,
    load_reference_components,
    reportable_version_decisions,
    score_reference_component,
)


DEFAULT_DIAGNOSTIC_JSON = Path("data/results/experiments/coarse-to-fine-pruning-diagnostics.json")
DEFAULT_REFERENCE_DB = Path(
    "data/reference_db/reference_features_phase4_multiscale_calibrated_combined.sqlite"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/composite-family-shortlist-live-validation.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_LIVE_VALIDATION.md")
DEFAULT_CACHE_DIR = Path(
    "data/results/experiments/composite-family-shortlist-live-validation-cases"
)
DEFAULT_MARGIN = 0.10
DEFAULT_MIN_SCORE = 0.05
CACHE_SCHEMA_VERSION = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Recompute APK features and validate the balanced composite family "
            "shortlist against the current full matcher without production wiring."
        )
    )
    parser.add_argument("--diagnostic-json", default=str(DEFAULT_DIAGNOSTIC_JSON))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--case-id", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        diagnostic_json=Path(args.diagnostic_json),
        reference_db=Path(args.reference_db),
        cache_dir=Path(args.cache_dir) if args.cache_dir else None,
        use_cache=not args.no_cache,
        limit=args.limit,
        case_ids=args.case_id,
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
    reference_db: Path = DEFAULT_REFERENCE_DB,
    cache_dir: Path | None = DEFAULT_CACHE_DIR,
    use_cache: bool = True,
    limit: int | None = None,
    case_ids: Sequence[str] = (),
) -> dict[str, Any]:
    diagnostic = read_json(diagnostic_json)
    inventory = build_inventory(diagnostic.get("rows", []))
    if case_ids:
        requested = set(case_ids)
        inventory = [item for item in inventory if item["case_id"] in requested]
    if limit is not None:
        inventory = inventory[: max(limit, 0)]
    references = load_references(reference_db)
    case_rows = []
    total = len(inventory)
    for index, item in enumerate(inventory, start=1):
        case_rows.append(
            validate_case_cached(
                item,
                references=references,
                reference_db=reference_db,
                cache_dir=cache_dir,
                use_cache=use_cache,
                index=index,
                total=total,
            )
        )
    summary = summarize(case_rows, references)
    gates = build_gates(case_rows, summary)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    summary["failed_gates"] = len(failed_gates)
    return {
        "schema_version": 1,
        "verdict": verdict(failed_gates),
        "recommendation": recommendation(failed_gates),
        "scope": (
            "Live offline validation only. This experiment analyzes each APK once, "
            "computes the balanced package/class/method/dependency/literal family "
            "shortlist before full scoring, retains every reference version inside "
            "kept coordinates, and compares the current full matcher decisions with "
            "the shortlist-filtered decisions. It does not change match-apk defaults, "
            "selected versions, SBOM output, vulnerability labels, or source-validation metrics."
        ),
        "sources": {
            "diagnostic_json": normalize_path(diagnostic_json),
            "reference_db": normalize_path(reference_db),
            "case_cache_dir": normalize_path(cache_dir) if cache_dir else None,
        },
        "configuration": {
            "profile_id": RECOMMENDED_PROFILE_ID,
            "rescue_policy": RECOMMENDED_RESCUE_POLICY,
            "margin": DEFAULT_MARGIN,
            "min_score": DEFAULT_MIN_SCORE,
            "weights": profile_weights(),
            "dependency_signal": (
                "The live shortlist uses the matcher's exact dependency blend: "
                "0.65 dependency-edge coverage plus 0.35 dependency-shape similarity."
            ),
        },
        "policy": [
            "Analyze APK features once and keep the live validation lane separate from production matching.",
            "Retain complete coordinate version bands; never prune individual near versions.",
            "Reject promotion on any tracked source-family loss or tracked source-selection regression.",
            "Reject promotion when reportable selected versions change, even if source tracking remains clean.",
            "Treat reference-row reduction as potential avoided full scoring work, not as a benchmarked speedup.",
        ],
        "summary": summary,
        "gates": gates,
        "cases": case_rows,
    }


def build_inventory(rows: Sequence[Any]) -> list[dict[str, Any]]:
    by_report: dict[str, dict[str, Any]] = {}
    for raw_row in rows:
        if not isinstance(raw_row, dict):
            continue
        report_path = normalize_path(raw_row.get("report_path") or "")
        if not report_path:
            continue
        item = by_report.setdefault(
            report_path,
            {
                "dataset_layer": str(raw_row.get("dataset_layer") or "unknown"),
                "case_id": str(raw_row.get("case_id") or report_path),
                "case_name": str(raw_row.get("case_name") or raw_row.get("case_id") or report_path),
                "report_path": report_path,
                "source_versions_by_coordinate": {},
            },
        )
        coordinate = str(raw_row.get("coordinate") or "")
        source_versions = [
            str(version) for version in raw_row.get("source_versions", []) if version
        ]
        if coordinate and source_versions:
            item["source_versions_by_coordinate"][coordinate] = source_versions
    return sorted(
        by_report.values(),
        key=lambda item: (item["dataset_layer"], item["case_id"], item["report_path"]),
    )


def load_references(reference_db: Path) -> list[ReferenceComponentFeatures]:
    if not reference_db.exists():
        raise FileNotFoundError(f"Reference feature DB not found: {reference_db}")
    with sqlite3.connect(reference_db) as connection:
        return load_reference_components(connection)


def validate_case(
    item: dict[str, Any],
    *,
    references: list[ReferenceComponentFeatures],
) -> dict[str, Any]:
    row = {
        "dataset_layer": item["dataset_layer"],
        "case_id": item["case_id"],
        "case_name": item["case_name"],
        "report_path": item["report_path"],
        "source_versions_by_coordinate": item["source_versions_by_coordinate"],
    }
    report_path = Path(item["report_path"])
    if not report_path.exists():
        return {**row, "status": "missing-report", "apk_path": ""}
    report = read_json(report_path)
    apk_path = Path(str(report.get("match_summary", {}).get("apk_path") or ""))
    if not apk_path.exists():
        return {**row, "status": "missing-apk", "apk_path": normalize_path(apk_path)}

    apk_features = feature_set_from_apk_analysis(
        analyze_apk_dex(apk_path, include_members=True)
    )
    shortlist = build_family_shortlist(apk_features, references)
    baseline_candidates = score_references(apk_features, references)
    filtered_candidates = [
        candidate
        for candidate in baseline_candidates
        if candidate.coordinate in shortlist["retained_coordinates"]
    ]
    baseline_decisions = build_version_decisions(baseline_candidates)
    filtered_decisions = build_version_decisions(filtered_candidates)
    comparison = compare_decisions(
        baseline_decisions,
        filtered_decisions,
        source_versions_by_coordinate=item["source_versions_by_coordinate"],
    )
    return {
        **row,
        "status": "evaluated",
        "apk_path": normalize_path(apk_path),
        "apk_feature_counts": {
            "packages": apk_features.packages_count,
            "classes": apk_features.classes_count,
            "methods": apk_features.methods_count,
            "dependency_edges": apk_features.dependency_edges_count,
            "string_literals": apk_features.string_literals_count,
        },
        "reference_rows_before": len(references),
        "reference_rows_retained": shortlist["reference_rows_retained"],
        "reference_rows_removed": len(references) - shortlist["reference_rows_retained"],
        "retained_coordinate_count": len(shortlist["retained_coordinates"]),
        "removed_coordinate_count": len(shortlist["removed_coordinates"]),
        "rescued_coordinate_count": len(shortlist["rescued_coordinates"]),
        "baseline_candidate_slots": len(baseline_candidates),
        "filtered_candidate_slots": len(filtered_candidates),
        "candidate_slots_removed": len(baseline_candidates) - len(filtered_candidates),
        **comparison,
    }


def validate_case_cached(
    item: dict[str, Any],
    *,
    references: list[ReferenceComponentFeatures],
    reference_db: Path,
    cache_dir: Path | None,
    use_cache: bool,
    index: int,
    total: int,
) -> dict[str, Any]:
    signature = case_cache_signature(item, reference_db=reference_db, references=references)
    cache_path = case_cache_path(cache_dir, item) if cache_dir else None
    if use_cache and cache_path and cache_path.exists():
        cached = read_cached_case(cache_path, signature)
        if cached is not None:
            print(
                f"[{index}/{total}] cache hit {item['case_id']}",
                flush=True,
            )
            return {**cached, "cache_status": "hit"}

    print(f"[{index}/{total}] validating {item['case_id']}", flush=True)
    row = validate_case(item, references=references)
    row = {
        **row,
        "cache_status": "miss",
        "cache_signature": signature,
    }
    if use_cache and cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return row


def case_cache_signature(
    item: dict[str, Any],
    *,
    reference_db: Path,
    references: Sequence[ReferenceComponentFeatures],
) -> dict[str, Any]:
    return {
        "schema_version": CACHE_SCHEMA_VERSION,
        "profile_id": RECOMMENDED_PROFILE_ID,
        "rescue_policy": RECOMMENDED_RESCUE_POLICY,
        "margin": DEFAULT_MARGIN,
        "min_score": DEFAULT_MIN_SCORE,
        "reference_db": normalize_path(reference_db),
        "reference_count": len(references),
        "report_path": item["report_path"],
        "case_id": item["case_id"],
    }


def case_cache_path(cache_dir: Path | None, item: dict[str, Any]) -> Path:
    if cache_dir is None:
        raise ValueError("cache_dir is required")
    raw = f"{item['dataset_layer']}-{item['case_id']}"
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-").lower()[:90]
    digest = hashlib.sha1(str(item["report_path"]).encode("utf-8")).hexdigest()[:10]
    return cache_dir / f"{slug}-{digest}.json"


def read_cached_case(
    path: Path,
    signature: dict[str, Any],
) -> dict[str, Any] | None:
    try:
        cached = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    if cached.get("cache_signature") != signature:
        return None
    if cached.get("status") == "missing-apk" and Path(str(cached.get("apk_path") or "")).exists():
        return None
    if cached.get("status") == "missing-report" and Path(str(cached.get("report_path") or "")).exists():
        return None
    return cached


def build_family_shortlist(
    apk_features: FeatureSet,
    references: Sequence[ReferenceComponentFeatures],
    *,
    margin: float = DEFAULT_MARGIN,
) -> dict[str, Any]:
    by_coordinate: dict[str, list[ReferenceComponentFeatures]] = {}
    for reference in references:
        by_coordinate.setdefault(reference.coordinate, []).append(reference)

    family_rows = []
    for coordinate, family_references in by_coordinate.items():
        evidence_rows = [
            build_family_reference_evidence(apk_features, reference)
            for reference in family_references
        ]
        family_rows.append(
            {
                "coordinate": coordinate,
                "reference_versions": len(family_references),
                "composite_score": max(
                    (row["composite_score"] for row in evidence_rows),
                    default=0.0,
                ),
                "rescued": any(row["rescued"] for row in evidence_rows),
            }
        )
    best_score = max((row["composite_score"] for row in family_rows), default=0.0)
    retained = [
        row
        for row in family_rows
        if row["composite_score"] + margin >= best_score or row["rescued"]
    ]
    removed = [row for row in family_rows if row not in retained]
    retained_coordinates = {row["coordinate"] for row in retained}
    return {
        "best_composite_score": round(best_score, 6),
        "retained_coordinates": retained_coordinates,
        "removed_coordinates": {row["coordinate"] for row in removed},
        "rescued_coordinates": {
            row["coordinate"] for row in retained if row["rescued"]
        },
        "reference_rows_retained": sum(
            len(family_references)
            for coordinate, family_references in by_coordinate.items()
            if coordinate in retained_coordinates
        ),
    }


def build_family_reference_evidence(
    apk_features: FeatureSet,
    reference: ReferenceComponentFeatures,
) -> dict[str, Any]:
    package_matches = apk_features.packages & reference.features.packages
    class_matches = apk_features.classes & reference.features.classes
    method_matches = apk_features.methods & reference.features.methods
    dependency_matches = apk_features.class_dependencies & reference.features.class_dependencies
    literal_matches = apk_features.string_literals & reference.features.string_literals
    dependency_edge_score = coverage_score(
        dependency_matches,
        reference.features.class_dependencies,
    )
    dependency_score = (
        0.65 * dependency_edge_score
        + 0.35 * _dependency_shape_similarity(apk_features, reference.features)
    )
    row = {
        "package_score": coverage_score(package_matches, reference.features.packages),
        "class_score": coverage_score(class_matches, reference.features.classes),
        "method_score": coverage_score(method_matches, reference.features.methods),
        "dependency_score": dependency_score,
        "literal_score": coverage_score(literal_matches, reference.features.string_literals),
        "matched_classes": len(class_matches),
        "matched_methods": len(method_matches),
        "matched_dependency_edges": len(dependency_matches),
        "matched_string_literals": len(literal_matches),
    }
    return {
        **row,
        "composite_score": composite_score(row, profile_weights()),
        "rescued": should_rescue(row, RECOMMENDED_RESCUE_POLICY),
    }


def score_references(
    apk_features: FeatureSet,
    references: Sequence[ReferenceComponentFeatures],
    *,
    min_score: float = DEFAULT_MIN_SCORE,
) -> list[MatchCandidate]:
    by_coordinate: dict[str, list[ReferenceComponentFeatures]] = {}
    for reference in references:
        by_coordinate.setdefault(reference.coordinate, []).append(reference)
    candidates = [
        score_reference_component(
            apk_features,
            reference,
            sibling_features=[
                sibling.features
                for sibling in by_coordinate[reference.coordinate]
                if sibling.component_id != reference.component_id
            ],
            package_weight=DEFAULT_PACKAGE_WEIGHT,
            class_weight=DEFAULT_CLASS_WEIGHT,
            method_weight=DEFAULT_METHOD_WEIGHT,
            opcode_weight=DEFAULT_OPCODE_WEIGHT,
            dependency_weight=DEFAULT_DEPENDENCY_WEIGHT,
            literal_weight=DEFAULT_LITERAL_WEIGHT,
            unique_version_weight=DEFAULT_UNIQUE_VERSION_WEIGHT,
            api_reference_weight=DEFAULT_API_REFERENCE_WEIGHT,
            opcode_ngram_weight=DEFAULT_OPCODE_NGRAM_WEIGHT,
        )
        for reference in references
    ]
    candidates = [candidate for candidate in candidates if candidate.score >= min_score]
    candidates.sort(key=candidate_sort_key, reverse=True)
    return candidates


def candidate_sort_key(candidate: MatchCandidate) -> tuple[Any, ...]:
    evidence = candidate.evidence
    return (
        candidate.score,
        evidence.class_score,
        evidence.method_score,
        evidence.dependency_score,
        evidence.unique_version_score,
        evidence.literal_score,
        evidence.opcode_score,
        evidence.package_score,
        candidate.coordinate,
        candidate.version,
    )


def compare_decisions(
    baseline: Sequence[VersionDecision],
    filtered: Sequence[VersionDecision],
    *,
    source_versions_by_coordinate: dict[str, list[str]],
) -> dict[str, Any]:
    baseline_selected = {item.coordinate: item.selected_version for item in baseline}
    filtered_selected = {item.coordinate: item.selected_version for item in filtered}
    selected_comparison = compare_selected_versions(
        baseline_selected,
        filtered_selected,
        source_versions_by_coordinate=source_versions_by_coordinate,
    )
    baseline_reportable = selected_versions(
        decision for decision, _ in reportable_version_decisions(list(baseline))
    )
    filtered_reportable = selected_versions(
        decision for decision, _ in reportable_version_decisions(list(filtered))
    )
    reportable_changes = changed_selected_versions(baseline_reportable, filtered_reportable)
    return {
        "baseline_decision_rows": len(baseline),
        "filtered_decision_rows": len(filtered),
        "decision_rows_removed": len(baseline) - len(filtered),
        **selected_comparison,
        "reportable_selected_version_changes": reportable_changes,
        "reportable_selected_version_change_count": len(reportable_changes),
    }


def compare_selected_versions(
    baseline_selected: dict[str, str],
    filtered_selected: dict[str, str],
    *,
    source_versions_by_coordinate: dict[str, list[str]],
) -> dict[str, Any]:
    source_family_losses = []
    source_selection_regressions = []
    source_selection_improvements = []
    for coordinate, source_versions in sorted(source_versions_by_coordinate.items()):
        baseline_version = baseline_selected.get(coordinate)
        filtered_version = filtered_selected.get(coordinate)
        if filtered_version is None:
            source_family_losses.append(
                comparison_row(coordinate, baseline_version, filtered_version, source_versions)
            )
        baseline_matches = baseline_version in source_versions
        filtered_matches = filtered_version in source_versions
        if baseline_matches and not filtered_matches:
            source_selection_regressions.append(
                comparison_row(coordinate, baseline_version, filtered_version, source_versions)
            )
        elif not baseline_matches and filtered_matches:
            source_selection_improvements.append(
                comparison_row(coordinate, baseline_version, filtered_version, source_versions)
            )
    selected_changes = changed_selected_versions(baseline_selected, filtered_selected)
    return {
        "tracked_source_family_rows": len(source_versions_by_coordinate),
        "source_family_losses": source_family_losses,
        "source_family_loss_count": len(source_family_losses),
        "source_selection_regressions": source_selection_regressions,
        "source_selection_regression_count": len(source_selection_regressions),
        "source_selection_improvements": source_selection_improvements,
        "source_selection_improvement_count": len(source_selection_improvements),
        "selected_version_changes": selected_changes,
        "selected_version_change_count": len(selected_changes),
    }


def selected_versions(decisions: Sequence[VersionDecision] | Any) -> dict[str, str]:
    return {item.coordinate: item.selected_version for item in decisions}


def changed_selected_versions(
    baseline_selected: dict[str, str],
    filtered_selected: dict[str, str],
) -> list[dict[str, Any]]:
    return [
        {
            "coordinate": coordinate,
            "baseline_selected_version": baseline_selected.get(coordinate),
            "filtered_selected_version": filtered_selected.get(coordinate),
        }
        for coordinate in sorted(set(baseline_selected) | set(filtered_selected))
        if baseline_selected.get(coordinate) != filtered_selected.get(coordinate)
    ]


def comparison_row(
    coordinate: str,
    baseline_version: str | None,
    filtered_version: str | None,
    source_versions: Sequence[str],
) -> dict[str, Any]:
    return {
        "coordinate": coordinate,
        "source_versions": list(source_versions),
        "baseline_selected_version": baseline_version,
        "filtered_selected_version": filtered_version,
    }


def summarize(
    cases: Sequence[dict[str, Any]],
    references: Sequence[ReferenceComponentFeatures],
) -> dict[str, Any]:
    evaluated = [row for row in cases if row["status"] == "evaluated"]
    return {
        "cases_requested": len(cases),
        "cases_evaluated": len(evaluated),
        "controlled_cases_evaluated": sum(
            row["dataset_layer"] == "controlled-generated" for row in evaluated
        ),
        "real_cases_evaluated": sum(row["dataset_layer"] == "real-apk" for row in evaluated),
        "missing_input_cases": len(cases) - len(evaluated),
        "reference_rows_per_case": len(references),
        "reference_rows_before": sum(row["reference_rows_before"] for row in evaluated),
        "reference_rows_retained": sum(row["reference_rows_retained"] for row in evaluated),
        "reference_rows_removed": sum(row["reference_rows_removed"] for row in evaluated),
        "reference_row_reduction_ratio": safe_divide(
            sum(row["reference_rows_removed"] for row in evaluated),
            sum(row["reference_rows_before"] for row in evaluated),
        ),
        "candidate_slots_before": sum(row["baseline_candidate_slots"] for row in evaluated),
        "candidate_slots_retained": sum(row["filtered_candidate_slots"] for row in evaluated),
        "candidate_slots_removed": sum(row["candidate_slots_removed"] for row in evaluated),
        "candidate_slot_reduction_ratio": safe_divide(
            sum(row["candidate_slots_removed"] for row in evaluated),
            sum(row["baseline_candidate_slots"] for row in evaluated),
        ),
        "tracked_source_family_rows": sum(row["tracked_source_family_rows"] for row in evaluated),
        "source_family_losses": sum(row["source_family_loss_count"] for row in evaluated),
        "source_selection_regressions": sum(
            row["source_selection_regression_count"] for row in evaluated
        ),
        "source_selection_improvements": sum(
            row["source_selection_improvement_count"] for row in evaluated
        ),
        "selected_version_changes": sum(row["selected_version_change_count"] for row in evaluated),
        "reportable_selected_version_changes": sum(
            row["reportable_selected_version_change_count"] for row in evaluated
        ),
        "case_cache_hits": sum(row.get("cache_status") == "hit" for row in cases),
        "case_cache_misses": sum(row.get("cache_status") == "miss" for row in cases),
    }


def build_gates(cases: Sequence[dict[str, Any]], summary: dict[str, Any]) -> list[dict[str, Any]]:
    missing_tracked_cases = [
        row
        for row in cases
        if row["status"] != "evaluated" and row.get("source_versions_by_coordinate")
    ]
    return [
        gate(
            "all-requested-inputs-present",
            summary["missing_input_cases"],
            f"{summary['cases_evaluated']}/{summary['cases_requested']} cases evaluated.",
        ),
        gate(
            "all-tracked-source-inputs-present",
            len(missing_tracked_cases),
            f"{len(missing_tracked_cases)} missing cases contain tracked source-version rows.",
        ),
        gate(
            "controlled-and-real-cases-evaluated",
            0
            if summary["controlled_cases_evaluated"] and summary["real_cases_evaluated"]
            else 1,
            (
                f"{summary['controlled_cases_evaluated']} controlled and "
                f"{summary['real_cases_evaluated']} real cases evaluated."
            ),
        ),
        gate(
            "shortlist-removes-reference-rows",
            0 if summary["reference_rows_removed"] else 1,
            (
                f"{summary['reference_rows_removed']}/{summary['reference_rows_before']} "
                "reference rows removed before full scoring."
            ),
        ),
        gate(
            "no-tracked-source-family-losses",
            summary["source_family_losses"],
            f"{summary['source_family_losses']} tracked source-family losses.",
        ),
        gate(
            "no-tracked-source-selection-regressions",
            summary["source_selection_regressions"],
            f"{summary['source_selection_regressions']} tracked source-selection regressions.",
        ),
        gate(
            "no-reportable-selected-version-changes",
            summary["reportable_selected_version_changes"],
            f"{summary['reportable_selected_version_changes']} reportable selected-version changes.",
        ),
    ]


def gate(gate_id: str, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


def verdict(failed_gates: Sequence[dict[str, Any]]) -> str:
    if not failed_gates:
        return "composite-family-shortlist-live-validation-clean-opt-in-candidate"
    if missing_untracked_input_only(failed_gates):
        return "composite-family-shortlist-live-validation-partial-clean-missing-untracked-input"
    return "composite-family-shortlist-live-validation-reject-production-promotion"


def recommendation(failed_gates: Sequence[dict[str, Any]]) -> str:
    if not failed_gates:
        return "advance-shortlist-to-explicit-opt-in-matcher-experiment"
    if missing_untracked_input_only(failed_gates):
        return "restore-missing-apk-or-document-exclusion-before-opt-in-promotion"
    return "keep-shortlist-offline-and-investigate-live-regressions"


def missing_untracked_input_only(failed_gates: Sequence[dict[str, Any]]) -> bool:
    return [gate["gate"] for gate in failed_gates] == ["all-requested-inputs-present"]


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
        "# Composite Family-Shortlist Live Offline Validation",
        "",
        "Generated by `scripts/build_composite_family_shortlist_live_validation.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        f"Recommendation: `{payload['recommendation']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Cases evaluated: `{summary['cases_evaluated']}/{summary['cases_requested']}`",
        f"- Controlled / real cases: `{summary['controlled_cases_evaluated']}` / `{summary['real_cases_evaluated']}`",
        f"- Reference rows removed before full scoring: `{summary['reference_rows_removed']}/{summary['reference_rows_before']}` (`{summary['reference_row_reduction_ratio']}`)",
        f"- Post-threshold candidate slots removed: `{summary['candidate_slots_removed']}/{summary['candidate_slots_before']}` (`{summary['candidate_slot_reduction_ratio']}`)",
        f"- Tracked source-family rows: `{summary['tracked_source_family_rows']}`",
        f"- Tracked source-family losses: `{summary['source_family_losses']}`",
        f"- Tracked source-selection regressions / improvements: `{summary['source_selection_regressions']}` / `{summary['source_selection_improvements']}`",
        f"- Selected-version changes: `{summary['selected_version_changes']}`",
        f"- Reportable selected-version changes: `{summary['reportable_selected_version_changes']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        f"- Case cache hits / misses: `{summary['case_cache_hits']}` / `{summary['case_cache_misses']}`",
        "",
        "## Configuration",
        "",
        f"- Profile: `{payload['configuration']['profile_id']}`",
        f"- Rescue policy: `{payload['configuration']['rescue_policy']}`",
        f"- Margin: `{payload['configuration']['margin']}`",
        f"- Minimum full-score threshold: `{payload['configuration']['min_score']}`",
        f"- Dependency signal: {payload['configuration']['dependency_signal']}",
        "",
        "## Guardrails",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(["", "## Gates", "", "| Gate | Status | Evidence |", "|---|---|---|"])
    for item in payload["gates"]:
        lines.append(
            f"| `{md(item['gate'])}` | `{md(item['status'])}` | {md(item['evidence'])} |"
        )
    lines.extend(
        [
            "",
            "## Case Summary",
            "",
            "| Layer | Case | Status | Ref rows removed | Candidate slots removed | Source family losses | Source regressions | Reportable changes |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["cases"]:
        lines.append(
            "| "
            f"`{md(row['dataset_layer'])}` | "
            f"`{md(row['case_id'])}` | "
            f"`{md(row['status'])}` | "
            f"{row.get('reference_rows_removed', 0)} | "
            f"{row.get('candidate_slots_removed', 0)} | "
            f"{row.get('source_family_loss_count', 0)} | "
            f"{row.get('source_selection_regression_count', 0)} | "
            f"{row.get('reportable_selected_version_change_count', 0)} |"
        )
    missing = [row for row in payload["cases"] if row["status"] != "evaluated"]
    if missing:
        lines.extend(
            [
                "",
                "## Missing Inputs",
                "",
                "| Layer | Case | Status | APK path | Tracked source rows |",
                "|---|---|---|---|---:|",
            ]
        )
        for row in missing:
            lines.append(
                "| "
                f"`{md(row['dataset_layer'])}` | "
                f"`{md(row['case_id'])}` | "
                f"`{md(row['status'])}` | "
                f"`{md(row.get('apk_path', ''))}` | "
                f"{len(row.get('source_versions_by_coordinate', {}))} |"
            )
    lines.extend(["", "## Conclusion", "", conclusion(payload), ""])
    return "\n".join(lines)


def conclusion(payload: dict[str, Any]) -> str:
    if (
        payload["verdict"]
        == "composite-family-shortlist-live-validation-partial-clean-missing-untracked-input"
    ):
        return (
            "The live recomputation is source-clean and report-output-clean for every "
            "available tracked case, but it is not a full promotion gate because one "
            "untracked real APK input is missing. Restore the missing APK or document "
            "an explicit exclusion, then rerun from cache before any opt-in matcher work."
        )
    if payload["summary"]["failed_gates"]:
        return (
            "Keep the composite family shortlist offline. Live APK recomputation found "
            "at least one gate failure, so production promotion is not justified."
        )
    return (
        "The live offline recomputation preserves tracked source families and reportable "
        "selected versions while removing reference rows before full scoring. Advance "
        "only to an explicit opt-in matcher experiment with fresh regression checks."
    )


def profile_weights() -> dict[str, float]:
    return next(
        dict(profile["weights"])
        for profile in PROFILES
        if profile["profile_id"] == RECOMMENDED_PROFILE_ID
    )


def coverage_score(matches: set[Any], reference_values: set[Any]) -> float:
    return len(matches) / len(reference_values) if reference_values else 0.0


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
