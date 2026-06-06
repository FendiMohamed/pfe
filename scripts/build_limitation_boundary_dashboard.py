from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_DASHBOARD_JSON = Path("data/results/evaluation/real-apk-source-validation-dashboard.json")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/limitation-boundary-dashboard.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/LIMITATION_BOUNDARY_DASHBOARD.md")

DETAIL_DOCS = {
    "Organic Maps 2026.05.08-4": "docs/evaluation/REAL_APK_CURRENT_BATCH_RESULTS.md",
    "Termux 0.119.0-beta.3": "docs/evaluation/REAL_APK_CURRENT_BATCH_RESULTS.md",
    "Hidden DEX loader fixture": "docs/evaluation/HIDDEN_DEX_LIMITATION_FIXTURE.md",
    "Simplify obfuscated sample": "docs/evaluation/SIMPLIFY_OBFUSCATED_LIMITATION.md",
    "Jitsi Meet 26.0.0": "docs/evaluation/JITSI_MEET_PROOF_BUNDLE.md",
}

BOUNDARY_POLICIES = [
    "Limitation/boundary rows are excluded from Maven precision, recall, and emitted-version confirmation metrics.",
    "Native `.so` payloads are represented as CycloneDX file/hash evidence, not native package/version claims.",
    "Hidden, packed, or dynamic-code evidence should raise risk and avoid unsupported Maven claims.",
    "Normal-layout obfuscated samples may emit low-confidence Maven candidates, but remain outside accuracy metrics unless source validation exists.",
    "Hybrid framework rows can count source-validated Maven components while keeping framework/native payloads hash-only.",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build dashboard-ready limitation and boundary evidence summary.",
    )
    parser.add_argument("--dashboard-json", default=str(DEFAULT_DASHBOARD_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    dashboard_path = Path(args.dashboard_json)
    payload = build_payload(read_json(dashboard_path), dashboard_path=dashboard_path)

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
                "limitation_cases": payload["summary"]["limitation_cases"],
                "hybrid_boundary_cases": payload["summary"]["hybrid_boundary_cases"],
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(dashboard: dict[str, Any], *, dashboard_path: Path) -> dict[str, Any]:
    cases = dashboard.get("cases", [])
    limitation_cases = [
        build_case_row(case)
        for case in cases
        if case.get("metric_bucket") == "limitation-boundary"
    ]
    hybrid_cases = [
        build_hybrid_row(case)
        for case in cases
        if is_hybrid_boundary_case(case)
    ]
    summary = build_summary(limitation_cases, hybrid_cases)
    return {
        "schema_version": 1,
        "sources": {
            "dashboard": normalize_path(dashboard_path),
            "native_boundary": "docs/evaluation/NATIVE_BOUNDARY_DIAGNOSTICS.md",
            "hidden_dex": "docs/evaluation/HIDDEN_DEX_DIAGNOSTICS.md",
        },
        "policy": BOUNDARY_POLICIES,
        "summary": summary,
        "limitation_cases": limitation_cases,
        "hybrid_boundary_cases": hybrid_cases,
        "verdict": verdict(summary),
        "conclusion": (
            "Boundary evidence is complete enough for the current Maven/DEX MVP: explicit "
            "limitation rows stay outside accuracy metrics, and hybrid source-validated "
            "framework/native rows keep Maven validation separate from native/hash-only scope."
        ),
    }


def build_case_row(case: dict[str, Any]) -> dict[str, Any]:
    metadata = case.get("apk_metadata", {})
    validation_stats = case.get("validation_stats", {})
    description = case.get("description", {})
    classification = case.get("classification", {})
    return {
        "name": case.get("name"),
        "case_id": case.get("case_id"),
        "role": case.get("role"),
        "boundary_type": boundary_type(case),
        "counted_in_accuracy": bool(case.get("counted_in_100_source_validated_real_apks")),
        "maven_components": int(metadata.get("maven_components") or 0),
        "native_files": int(metadata.get("native_so_files") or 0),
        "dex_count": int(metadata.get("dex_count") or 0),
        "feature_labels": classification.get("feature_labels", []),
        "interpretation": description.get("interpretation"),
        "safe_action": safe_action(case),
        "report": normalize_path(case.get("paths", {}).get("report")),
        "proof": normalize_path(case.get("paths", {}).get("proof") or DETAIL_DOCS.get(case.get("name", ""), "")),
        "validation_checked": int(validation_stats.get("checked") or 0),
    }


def build_hybrid_row(case: dict[str, Any]) -> dict[str, Any]:
    metadata = case.get("apk_metadata", {})
    validation_stats = case.get("validation_stats", {})
    description = case.get("description", {})
    return {
        "name": case.get("name"),
        "case_id": case.get("case_id"),
        "role": case.get("role"),
        "counted_maven_components": bool(case.get("counted_in_100_source_validated_real_apks")),
        "maven_validation": (
            f"{validation_stats.get('confirmed', 0)}/{validation_stats.get('checked', 0)}"
        ),
        "maven_components": int(metadata.get("maven_components") or 0),
        "native_files": int(metadata.get("native_so_files") or 0),
        "dex_count": int(metadata.get("dex_count") or 0),
        "boundary_type": "framework-native-hybrid",
        "interpretation": description.get("interpretation"),
        "safe_action": (
            "Count only source-validated Maven components; keep React Native/WebRTC/Hermes "
            "native payloads as hash-only boundary evidence."
        ),
        "report": normalize_path(case.get("paths", {}).get("report")),
        "proof": normalize_path(case.get("paths", {}).get("proof") or DETAIL_DOCS.get(case.get("name", ""), "")),
    }


def build_summary(
    limitation_cases: list[dict[str, Any]],
    hybrid_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    boundary_type_counts: dict[str, int] = {}
    for row in limitation_cases:
        boundary_type_counts[row["boundary_type"]] = boundary_type_counts.get(row["boundary_type"], 0) + 1
    return {
        "limitation_cases": len(limitation_cases),
        "limitation_cases_counted_in_accuracy": sum(
            1 for row in limitation_cases if row["counted_in_accuracy"]
        ),
        "native_heavy_limitation_cases": boundary_type_counts.get("native-heavy", 0),
        "obfuscation_limitation_cases": boundary_type_counts.get("obfuscation", 0),
        "hybrid_boundary_cases": len(hybrid_cases),
        "limitation_maven_components_visible_but_not_counted": sum(
            row["maven_components"] for row in limitation_cases
        ),
        "limitation_native_files_hash_only": sum(row["native_files"] for row in limitation_cases),
        "hybrid_native_files_hash_only": sum(row["native_files"] for row in hybrid_cases),
        "boundary_type_counts": boundary_type_counts,
        "metric_changes": 0,
    }


def is_hybrid_boundary_case(case: dict[str, Any]) -> bool:
    labels_text = " ".join(str(label) for label in case.get("classification", {}).get("feature_labels", []))
    return bool(
        case.get("counted_in_100_source_validated_real_apks")
        and (
            "React Native/framework boundary" in labels_text
            or "native-heavy boundary" in labels_text
        )
        and str(case.get("name")) == "Jitsi Meet 26.0.0"
    )


def boundary_type(case: dict[str, Any]) -> str:
    role = str(case.get("role") or "")
    labels = set(case.get("classification", {}).get("feature_labels", []))
    if role == "limitation-native-heavy" or "native-heavy boundary" in labels:
        return "native-heavy"
    if role == "limitation-obfuscation" or "hidden/protector-style code boundary" in labels:
        return "obfuscation"
    return "boundary"


def safe_action(case: dict[str, Any]) -> str:
    name = str(case.get("name") or "")
    if name == "Organic Maps 2026.05.08-4":
        return "Keep as native-heavy maps boundary; do not claim native package/version recovery."
    if name == "Termux 0.119.0-beta.3":
        return "Keep as native/bootstrap boundary; native payloads are hash-only file evidence."
    if name == "Hidden DEX loader fixture":
        return "Keep as hidden/dynamic-code boundary; raise risk and avoid Maven claims."
    if name == "Simplify obfuscated sample":
        return "Keep as obfuscated normal-layout limitation; candidate Maven rows are not source-confirmed."
    return "Keep outside Maven accuracy metrics unless source-visible Maven ground truth exists."


def verdict(summary: dict[str, Any]) -> str:
    if summary["limitation_cases_counted_in_accuracy"] or summary["metric_changes"]:
        return "boundary-dashboard-policy-violation"
    if summary["limitation_cases"] >= 4 and summary["hybrid_boundary_cases"] >= 1:
        return "boundary-dashboard-ready"
    return "boundary-dashboard-incomplete"


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Limitation Boundary Dashboard",
        "",
        "Generated by `scripts/build_limitation_boundary_dashboard.py`.",
        "",
        payload["conclusion"],
        "",
        "## Summary",
        "",
        f"- Verdict: `{payload['verdict']}`",
        f"- Explicit limitation/boundary cases: `{summary['limitation_cases']}`",
        f"- Limitation cases counted in accuracy: `{summary['limitation_cases_counted_in_accuracy']}`",
        f"- Native-heavy limitation cases: `{summary['native_heavy_limitation_cases']}`",
        f"- Obfuscation limitation cases: `{summary['obfuscation_limitation_cases']}`",
        f"- Hybrid source-validated boundary cases: `{summary['hybrid_boundary_cases']}`",
        f"- Visible limitation Maven components not counted: `{summary['limitation_maven_components_visible_but_not_counted']}`",
        f"- Limitation native files hash-only: `{summary['limitation_native_files_hash_only']}`",
        f"- Hybrid native files hash-only: `{summary['hybrid_native_files_hash_only']}`",
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Explicit Limitation Cases",
            "",
            "| Case | Type | Maven visible | Native files | DEX | Counted | Safe action | Evidence |",
            "|---|---|---:|---:|---:|---|---|---|",
        ]
    )
    for row in payload["limitation_cases"]:
        lines.append(
            "| "
            f"{md(row['name'])} | "
            f"`{row['boundary_type']}` | "
            f"{row['maven_components']} | "
            f"{row['native_files']} | "
            f"{row['dex_count']} | "
            f"`{row['counted_in_accuracy']}` | "
            f"{md(row['safe_action'])} | "
            f"{evidence_links(row)} |"
        )
    lines.extend(
        [
            "",
            "## Hybrid Boundary Case",
            "",
            "| Case | Maven validation | Native files | Boundary | Safe action | Evidence |",
            "|---|---:|---:|---|---|---|",
        ]
    )
    for row in payload["hybrid_boundary_cases"]:
        lines.append(
            "| "
            f"{md(row['name'])} | "
            f"{row['maven_validation']} | "
            f"{row['native_files']} | "
            f"`{row['boundary_type']}` | "
            f"{md(row['safe_action'])} | "
            f"{evidence_links(row)} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep all explicit limitation rows out of emitted Maven version accuracy metrics.",
            "- Use Jitsi as a hybrid example: Maven dependency evidence can be source-validated while native/framework payloads remain hash-only boundary evidence.",
            "- Move next to wrong-version rows only after preserving these boundary fields in the dashboard design.",
            "",
        ]
    )
    return "\n".join(lines)


def evidence_links(row: dict[str, Any]) -> str:
    parts = []
    if row.get("report"):
        parts.append(f"`report`: `{row['report']}`")
    if row.get("proof"):
        parts.append(f"`proof`: `{row['proof']}`")
    return "<br>".join(parts) if parts else "n/a"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
