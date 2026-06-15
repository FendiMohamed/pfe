from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from statistics import mean
from typing import Any

from apk_sbom.apk_extractor import ApkInspection
from apk_sbom.dex_analyzer import ApkDexAnalysis
from apk_sbom.models import DetectedLibrary


@dataclass(frozen=True)
class R8ObfuscationDiagnostics:
    report_only: bool
    short_name_density: dict[str, Any]
    package_flattening_or_repackaging: dict[str, Any]
    class_method_coverage_loss: dict[str, Any]
    low_structural_coverage: dict[str, Any]
    low_confidence_component_ratio: dict[str, Any]
    nonstandard_dex_or_protector_hints: dict[str, Any]
    resource_shrinking_symptoms: dict[str, Any]
    method_inlining_or_class_merging_indicators: dict[str, Any]
    component_diagnostics: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_obfuscation_diagnostics(
    apk: ApkInspection,
    *,
    dex_analysis: ApkDexAnalysis | None = None,
    match_summary: object | None = None,
    components: list[DetectedLibrary] | None = None,
) -> R8ObfuscationDiagnostics:
    decisions = list(getattr(match_summary, "decisions", []) or [])
    component_list = components if components is not None else []
    coverage_rows = _coverage_rows(decisions)
    structural_rows = _structural_rows(decisions)
    inlining_rows = _inlining_rows(decisions)
    notes = [
        "Diagnostics are report-only and do not change matcher scores, selected versions, SBOM components, or vulnerability labels."
    ]
    if dex_analysis is None:
        notes.append("DEX member-name diagnostics were not evaluated for this report.")

    return R8ObfuscationDiagnostics(
        report_only=True,
        short_name_density=_short_name_density(dex_analysis),
        package_flattening_or_repackaging=_package_flattening_or_repackaging(dex_analysis),
        class_method_coverage_loss=_class_method_coverage_loss(coverage_rows, decisions),
        low_structural_coverage=_low_structural_coverage(structural_rows, decisions),
        low_confidence_component_ratio=_low_confidence_component_ratio(component_list, components is not None),
        nonstandard_dex_or_protector_hints=_nonstandard_dex_or_protector_hints(apk),
        resource_shrinking_symptoms=_resource_shrinking_symptoms(apk),
        method_inlining_or_class_merging_indicators=_method_inlining_or_class_merging_indicators(
            inlining_rows,
            decisions,
        ),
        component_diagnostics=_component_diagnostics(coverage_rows, structural_rows, inlining_rows),
        notes=notes,
    )


def _short_name_density(dex_analysis: ApkDexAnalysis | None) -> dict[str, Any]:
    if dex_analysis is None:
        return _signal(
            "not-evaluated",
            None,
            {},
            "DEX member analysis was not provided, so name-density ratios were not computed.",
        )

    package_segments = [
        segment
        for package_name in dex_analysis.packages
        for segment in package_name.split(".")
        if segment
    ]
    class_names = [
        _class_simple_name(descriptor)
        for dex_file in dex_analysis.dex_files
        for descriptor in dex_file.class_descriptors
    ]
    method_names = [
        name
        for dex_file in dex_analysis.dex_files
        for signature in dex_file.method_signatures
        if (name := _method_name(signature)) not in {"<init>", "<clinit>", ""}
    ]
    field_names = [
        name
        for dex_file in dex_analysis.dex_files
        for signature in getattr(dex_file, "field_signatures", [])
        if (name := _field_name(signature))
    ]
    density_metrics = {
        "package_segment_one_or_two_char_ratio": _short_ratio(package_segments, max_length=2),
        "package_segment_one_char_ratio": _short_ratio(package_segments, max_length=1),
        "class_one_or_two_char_ratio": _short_ratio(class_names, max_length=2),
        "class_one_char_ratio": _short_ratio(class_names, max_length=1),
        "method_one_or_two_char_ratio": _short_ratio(method_names, max_length=2),
        "method_one_char_ratio": _short_ratio(method_names, max_length=1),
        "field_one_or_two_char_ratio": _short_ratio(field_names, max_length=2),
        "field_one_char_ratio": _short_ratio(field_names, max_length=1),
        "package_segments": len(package_segments),
        "classes": len(class_names),
        "methods": len(method_names),
        "fields": len(field_names),
    }
    ratios = [
        value
        for key, value in density_metrics.items()
        if key.endswith("_ratio") and isinstance(value, float)
    ]
    overall = round(mean(ratios), 3) if ratios else None
    status = "not-detected"
    if overall is not None and overall >= 0.45:
        status = "warning"
    elif overall is not None and overall >= 0.25:
        status = "info"

    return _signal(
        status,
        overall,
        density_metrics,
        "High short-name density can indicate R8/ProGuard renaming or repackaging.",
    )


def _package_flattening_or_repackaging(dex_analysis: ApkDexAnalysis | None) -> dict[str, Any]:
    if dex_analysis is None:
        return _signal(
            "not-evaluated",
            None,
            {},
            "DEX class/package analysis was not provided, so package flattening was not computed.",
        )

    class_packages = [
        _class_package(descriptor)
        for dex_file in dex_analysis.dex_files
        for descriptor in dex_file.class_descriptors
    ]
    if not class_packages:
        return _signal(
            "not-detected",
            False,
            {"classes": 0, "packages": len(dex_analysis.packages)},
            "No class descriptors were available for package-depth analysis.",
        )

    depth_values = [_package_depth(package_name) for package_name in class_packages]
    shallow_classes = sum(1 for depth in depth_values if depth <= 2)
    default_package_classes = sum(1 for package_name in class_packages if not package_name)
    root_counter = Counter(
        package_name.split(".", maxsplit=1)[0] if package_name else ""
        for package_name in class_packages
    )
    top_root, top_root_count = root_counter.most_common(1)[0]
    shallow_ratio = round(shallow_classes / len(class_packages), 3)
    default_ratio = round(default_package_classes / len(class_packages), 3)
    top_root_ratio = round(top_root_count / len(class_packages), 3)
    average_depth = round(mean(depth_values), 3)
    flagged = (
        default_ratio >= 0.20
        or (shallow_ratio >= 0.85 and average_depth <= 2.0)
        or (top_root_ratio >= 0.90 and len(top_root) <= 2)
    )
    status = "warning" if flagged else "not-detected"
    return _signal(
        status,
        flagged,
        {
            "classes": len(class_packages),
            "packages": len(set(class_packages) - {""}),
            "average_package_depth": average_depth,
            "shallow_class_ratio": shallow_ratio,
            "default_package_class_ratio": default_ratio,
            "top_root_package": top_root or "<default>",
            "top_root_class_ratio": top_root_ratio,
        },
        "Package-depth collapse or short root concentration can indicate package flattening or repackaging.",
    )


def _class_method_coverage_loss(
    rows: list[dict[str, Any]],
    decisions: list[object],
) -> dict[str, Any]:
    if not decisions:
        return _signal(
            "not-evaluated",
            None,
            {},
            "No matcher decisions were available, so reference coverage loss was not computed.",
        )

    class_losses = [row["class_loss_ratio"] for row in rows if row["class_loss_ratio"] is not None]
    method_losses = [row["method_loss_ratio"] for row in rows if row["method_loss_ratio"] is not None]
    max_class_loss = max(class_losses) if class_losses else None
    max_method_loss = max(method_losses) if method_losses else None
    flagged = any(
        (row["class_loss_ratio"] is not None and row["class_loss_ratio"] >= 0.70)
        or (row["method_loss_ratio"] is not None and row["method_loss_ratio"] >= 0.70)
        for row in rows
    )
    status = "warning" if flagged else "not-detected"
    return _signal(
        status,
        flagged,
        {
            "decisions": len(decisions),
            "max_class_loss_ratio": _round_optional(max_class_loss),
            "max_method_loss_ratio": _round_optional(max_method_loss),
            "average_class_loss_ratio": _rounded_mean(class_losses),
            "average_method_loss_ratio": _rounded_mean(method_losses),
        },
        "Large class or method coverage gaps can indicate shrink/optimize evidence loss versus the reference.",
    )


def _low_structural_coverage(
    rows: list[dict[str, Any]],
    decisions: list[object],
) -> dict[str, Any]:
    if not decisions:
        return _signal(
            "not-evaluated",
            None,
            {},
            "No matcher decisions were available, so structural coverage was not computed.",
        )

    averages = [row["structural_average"] for row in rows if row["structural_average"] is not None]
    low_rows = [row for row in rows if row["structural_average"] is not None and row["structural_average"] < 0.25]
    flagged = bool(low_rows)
    status = "warning" if flagged else "not-detected"
    return _signal(
        status,
        flagged,
        {
            "decisions": len(decisions),
            "low_structural_decisions": len(low_rows),
            "average_structural_score": _rounded_mean(averages),
            "minimum_structural_score": _round_optional(min(averages) if averages else None),
        },
        "Low class/method/CDG/literal coverage keeps R8 suspicion visible without changing the selected version.",
    )


def _low_confidence_component_ratio(
    components: list[DetectedLibrary],
    evaluated: bool,
) -> dict[str, Any]:
    if not evaluated:
        return _signal(
            "not-evaluated",
            None,
            {},
            "Detected components were not provided, so the low-confidence ratio was not computed.",
        )
    low_components = [
        component
        for component in components
        if str(component.version_status).lower() in {"candidate", "uncertain"}
        or str(component.version_confidence_label).lower() in {"low", "uncertain"}
    ]
    ratio = round(len(low_components) / len(components), 3) if components else 0.0
    flagged = bool(components) and ratio >= 0.50
    return _signal(
        "warning" if flagged else "not-detected",
        ratio,
        {
            "components": len(components),
            "low_confidence_components": len(low_components),
        },
        "A high ratio of candidate/uncertain components is reported as an app-level R8/obfuscation symptom.",
    )


def _nonstandard_dex_or_protector_hints(apk: ApkInspection) -> dict[str, Any]:
    indicators = apk.forensic_summary.indicators
    codes = [indicator.code for indicator in indicators]
    relevant_codes = [
        code
        for code in codes
        if code
        in {
            "nonstandard-dex",
            "protector-name-hint",
            "tiny-primary-dex",
            "large-opaque-assets",
            "native-heavy",
        }
    ]
    flagged = bool(apk.forensic_summary.nonstandard_dex_files) or "protector-name-hint" in codes
    status = "warning" if flagged else ("info" if relevant_codes else "not-detected")
    return _signal(
        status,
        flagged,
        {
            "standard_dex_files": len(apk.forensic_summary.standard_dex_files),
            "nonstandard_dex_files": list(apk.forensic_summary.nonstandard_dex_files),
            "indicator_codes": relevant_codes,
            "extraction_risk": apk.forensic_summary.extraction_risk,
        },
        "Nonstandard DEX placement and protector-like file names are boundary warnings, not matcher filters.",
    )


def _resource_shrinking_symptoms(apk: ApkInspection) -> dict[str, Any]:
    resource_count = apk.forensic_summary.resource_entry_count
    asset_count = apk.forensic_summary.asset_entry_count
    has_resource_table = apk.resources_arsc_present
    sparse_resources = has_resource_table and resource_count <= 1
    missing_resources = not has_resource_table and resource_count == 0
    status = "info" if sparse_resources or missing_resources else "not-detected"
    return _signal(
        status,
        sparse_resources or missing_resources,
        {
            "resources_arsc_present": has_resource_table,
            "resource_entry_count": resource_count,
            "asset_entry_count": asset_count,
        },
        "Sparse or missing resource entries are exposed as weak symptoms only; they can be normal for controlled fixtures.",
    )


def _method_inlining_or_class_merging_indicators(
    rows: list[dict[str, Any]],
    decisions: list[object],
) -> dict[str, Any]:
    if not decisions:
        return _signal(
            "not-evaluated",
            None,
            {},
            "No matcher decisions were available, so inlining/class-merging indicators were not computed.",
        )

    inlining_rows = [row for row in rows if row["method_collapse_indicator"]]
    merging_rows = [row for row in rows if row["class_merging_indicator"]]
    flagged = bool(inlining_rows or merging_rows)
    return _signal(
        "warning" if flagged else "not-detected",
        flagged,
        {
            "decisions": len(decisions),
            "method_collapse_decisions": len(inlining_rows),
            "class_merging_decisions": len(merging_rows),
            "large_caller_method_concentration": None,
        },
        "Method coverage collapse or class-boundary mismatch can indicate inlining/class merging, but this phase remains diagnostic only.",
    )


def _coverage_rows(decisions: list[object]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for decision in decisions:
        evidence = getattr(decision, "evidence", None)
        if evidence is None:
            continue
        class_coverage = _coverage(getattr(evidence, "matched_classes", 0), getattr(evidence, "reference_classes", 0))
        method_coverage = _coverage(getattr(evidence, "matched_methods", 0), getattr(evidence, "reference_methods", 0))
        rows.append(
            {
                "coordinate": getattr(decision, "coordinate", ""),
                "selected_version": getattr(decision, "selected_version", ""),
                "class_coverage": class_coverage,
                "method_coverage": method_coverage,
                "class_loss_ratio": _loss_ratio(class_coverage),
                "method_loss_ratio": _loss_ratio(method_coverage),
                "matched_classes": getattr(evidence, "matched_classes", 0),
                "reference_classes": getattr(evidence, "reference_classes", 0),
                "matched_methods": getattr(evidence, "matched_methods", 0),
                "reference_methods": getattr(evidence, "reference_methods", 0),
            }
        )
    return rows


def _structural_rows(decisions: list[object]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for decision in decisions:
        evidence = getattr(decision, "evidence", None)
        if evidence is None:
            continue
        scores = [
            getattr(evidence, "class_score", 0.0),
            getattr(evidence, "method_score", 0.0),
        ]
        if getattr(evidence, "reference_dependency_edges", 0) > 0:
            scores.append(getattr(evidence, "dependency_score", 0.0))
        if getattr(evidence, "reference_string_literals", 0) > 0:
            scores.append(getattr(evidence, "literal_score", 0.0))
        if (
            getattr(evidence, "reference_unique_classes", 0)
            + getattr(evidence, "reference_unique_methods", 0)
            + getattr(evidence, "reference_unique_literals", 0)
            > 0
        ):
            scores.append(getattr(evidence, "unique_version_score", 0.0))
        rows.append(
            {
                "coordinate": getattr(decision, "coordinate", ""),
                "selected_version": getattr(decision, "selected_version", ""),
                "structural_average": round(mean(scores), 3) if scores else None,
                "class_score": getattr(evidence, "class_score", 0.0),
                "method_score": getattr(evidence, "method_score", 0.0),
                "dependency_score": getattr(evidence, "dependency_score", 0.0),
                "literal_score": getattr(evidence, "literal_score", 0.0),
                "unique_version_score": getattr(evidence, "unique_version_score", 0.0),
            }
        )
    return rows


def _inlining_rows(decisions: list[object]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for decision in decisions:
        evidence = getattr(decision, "evidence", None)
        if evidence is None:
            continue
        class_score = getattr(evidence, "class_score", 0.0)
        method_score = getattr(evidence, "method_score", 0.0)
        opcode_score = getattr(evidence, "opcode_score", 0.0)
        dependency_score = getattr(evidence, "dependency_score", 0.0)
        method_collapse = class_score >= 0.50 and method_score <= max(0.20, class_score - 0.35)
        class_merging = class_score <= 0.35 and max(opcode_score, dependency_score) >= 0.55
        rows.append(
            {
                "coordinate": getattr(decision, "coordinate", ""),
                "selected_version": getattr(decision, "selected_version", ""),
                "method_collapse_indicator": method_collapse,
                "class_merging_indicator": class_merging,
                "class_score": class_score,
                "method_score": method_score,
                "opcode_score": opcode_score,
                "dependency_score": dependency_score,
            }
        )
    return rows


def _component_diagnostics(
    coverage_rows: list[dict[str, Any]],
    structural_rows: list[dict[str, Any]],
    inlining_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    structural_by_key = {
        (row["coordinate"], row["selected_version"]): row
        for row in structural_rows
    }
    inlining_by_key = {
        (row["coordinate"], row["selected_version"]): row
        for row in inlining_rows
    }
    components: list[dict[str, Any]] = []
    for row in coverage_rows:
        key = (row["coordinate"], row["selected_version"])
        structural = structural_by_key.get(key, {})
        inlining = inlining_by_key.get(key, {})
        components.append(
            {
                "coordinate": row["coordinate"],
                "selected_version": row["selected_version"],
                "class_coverage": row["class_coverage"],
                "method_coverage": row["method_coverage"],
                "class_loss_ratio": row["class_loss_ratio"],
                "method_loss_ratio": row["method_loss_ratio"],
                "structural_average": structural.get("structural_average"),
                "method_collapse_indicator": inlining.get("method_collapse_indicator", False),
                "class_merging_indicator": inlining.get("class_merging_indicator", False),
            }
        )
    return components


def _signal(
    status: str,
    value: Any,
    metrics: dict[str, Any],
    explanation: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "value": value,
        "metrics": metrics,
        "explanation": explanation,
    }


def _coverage(matched: int, reference: int) -> float | None:
    if reference <= 0:
        return None
    return round(matched / reference, 3)


def _loss_ratio(coverage: float | None) -> float | None:
    if coverage is None:
        return None
    return round(max(0.0, 1.0 - coverage), 3)


def _short_ratio(values: list[str], *, max_length: int) -> float | None:
    if not values:
        return None
    short = sum(1 for value in values if 0 < len(value) <= max_length)
    return round(short / len(values), 3)


def _class_simple_name(descriptor: str) -> str:
    value = descriptor[1:-1] if descriptor.startswith("L") and descriptor.endswith(";") else descriptor
    simple = value.rsplit("/", maxsplit=1)[-1]
    return simple.rsplit("$", maxsplit=1)[-1]


def _class_package(descriptor: str) -> str:
    value = descriptor[1:-1] if descriptor.startswith("L") and descriptor.endswith(";") else descriptor
    if "/" not in value:
        return ""
    return value.rsplit("/", maxsplit=1)[0].replace("/", ".")


def _package_depth(package_name: str) -> int:
    if not package_name:
        return 0
    return package_name.count(".") + 1


def _method_name(signature: str) -> str:
    if "->" not in signature:
        return ""
    return signature.split("->", maxsplit=1)[1].split("(", maxsplit=1)[0]


def _field_name(signature: str) -> str:
    if "->" not in signature:
        return ""
    return signature.split("->", maxsplit=1)[1].split(":", maxsplit=1)[0]


def _rounded_mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(mean(values), 3)


def _round_optional(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 3)
