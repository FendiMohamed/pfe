from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path("configs/real_apk_candidates.json")
DEFAULT_DOC_PATH = Path("docs/evaluation/REAL_APK_CANDIDATES.md")
DEFAULT_OUTPUT_DIR = Path("data/results/evaluation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the real APK candidate matrix documentation and summary JSON.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--doc-path", default=str(DEFAULT_DOC_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config_path = Path(args.config)
    matrix = read_json(config_path)
    candidates = matrix["candidates"]
    summary = build_summary(matrix)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "real-apk-candidates.json"
    summary_path.write_text(
        json.dumps(
            {
                "schema_version": matrix["schema_version"],
                "source_config": normalize_path(str(config_path)),
                "summary": summary,
                "first_batch": first_batch_candidates(matrix),
                "candidates": candidates,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    doc_path = Path(args.doc_path)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(build_markdown(matrix, summary), encoding="utf-8")

    print(
        json.dumps(
            {
                "candidates": len(candidates),
                "doc": normalize_path(str(doc_path)),
                "first_batch": [item["id"] for item in first_batch_candidates(matrix)],
                "json": normalize_path(str(summary_path)),
                "summary": summary,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_summary(matrix: dict[str, Any]) -> dict[str, Any]:
    candidates = matrix["candidates"]
    priority_counts = Counter(candidate["priority"] for candidate in candidates)
    layer_counts = Counter(candidate["target_layer"] for candidate in candidates)
    criteria_counts: Counter[str] = Counter()
    for candidate in candidates:
        criteria_counts.update(candidate.get("criteria", []))
    proof_counts = Counter(candidate.get("proof_status", "unknown") for candidate in candidates)
    return {
        "total_candidates": len(candidates),
        "priority_counts": dict(sorted(priority_counts.items())),
        "target_layer_counts": dict(sorted(layer_counts.items())),
        "proof_status_counts": dict(sorted(proof_counts.items())),
        "criteria_counts": dict(sorted(criteria_counts.items())),
    }


def first_batch_candidates(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {candidate["id"]: candidate for candidate in matrix["candidates"]}
    return [by_id[item] for item in matrix.get("first_batch_ids", []) if item in by_id]


def build_markdown(matrix: dict[str, Any], summary: dict[str, Any]) -> str:
    first_batch = first_batch_candidates(matrix)
    m1_candidates = [
        candidate
        for candidate in matrix["candidates"]
        if candidate["priority"] in {"admitted", "first-batch", "M1-candidate"}
    ]
    m2_candidates = [
        candidate for candidate in matrix["candidates"] if candidate["priority"] == "M2-candidate"
    ]
    limitation_candidates = [
        candidate
        for candidate in matrix["candidates"]
        if candidate["priority"] == "limitation-candidate"
    ]
    lines = [
        "# Real APK Candidate Selection Table",
        "",
        "This file is generated from `configs/real_apk_candidates.json`.",
        "It is the working shortlist for growing the real APK dataset. An APK is not admitted to the source-validated dataset until the proof bundle is complete.",
        "",
        "## Admission Rule",
        "",
    ]
    lines.extend(f"- {item}" for item in matrix["admission_rule"])
    lines.extend(
        [
            "",
            "## Priority Status",
            "",
            "| Status | Meaning |",
            "|---|---|",
        ]
    )
    for status, meaning in matrix["priority_statuses"].items():
        lines.append(f"| {status} | {meaning} |")

    lines.extend(
        [
            "",
            "## Candidate Summary",
            "",
            "| Field | Value |",
            "|---|---:|",
            f"| Total candidates | {summary['total_candidates']} |",
        ]
    )
    for priority, count in summary["priority_counts"].items():
        lines.append(f"| Priority: {priority} | {count} |")
    for layer, count in summary["target_layer_counts"].items():
        lines.append(f"| Target layer: {layer} | {count} |")

    lines.extend(
        [
            "",
            "## First Batch Recommendation",
            "",
            "These are the first five candidates to validate after F-Droid because they cover a balanced mix of simple/medium, media/networking, Kotlin/AndroidX, older/security-sensitive, and native-heavy behavior.",
            "",
            candidate_table(first_batch),
            "",
            "## M1 Source-Validated Shortlist",
            "",
            "These APKs are the best first milestone candidates because they are open-source, Android/Gradle based, and cover different MVP criteria.",
            "",
            candidate_table(m1_candidates),
            "",
            "## M2 Expansion Pool",
            "",
            "These candidates help reach the 50 source-validated real APK target after the M1 workflow is proven.",
            "",
            candidate_table(m2_candidates),
            "",
            "## Limitation Candidate Pool",
            "",
            "These are useful even if full source validation is hard, because they test where the MVP should be cautious.",
            "",
            candidate_table(limitation_candidates),
            "",
            "## Selection Balance Targets",
            "",
            "| Criterion | Target |",
            "|---|---|",
        ]
    )
    for criterion, target in matrix["selection_balance_targets"].items():
        lines.append(f"| {criterion.replace('_', ' ')} | {target} |")

    lines.extend(
        [
            "",
            "Because one APK can cover several criteria, these targets do not add up to 50.",
            "",
            "## Next Concrete Step",
            "",
            "Create a proof folder for each first-batch candidate:",
            "",
            "```text",
            "data/test_apks/real/<app-id>/",
            "data/source/<app-id>-<version-or-tag>/",
            "data/results/source-validation/<app-id>/",
            "data/results/report-real-<app-id>/",
            "```",
            "",
            "For each candidate, verify the package name, APK version, source tag or commit, Gradle configuration, dependency tree, report, and source validation before moving its priority to `admitted`.",
            "",
        ]
    )
    return "\n".join(lines)


def candidate_table(candidates: list[dict[str, Any]]) -> str:
    lines = [
        "| Priority | App | Package / APK source to verify | Version target | Source repo to verify | Criteria covered | Why useful | Proof |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for candidate in candidates:
        lines.append(
            "| "
            f"{candidate['priority']} | "
            f"{candidate['app']} | "
            f"`{candidate['package_name']}`; {candidate['apk_source']} | "
            f"{version_target(candidate)} | "
            f"`{candidate['source_repo']}` | "
            f"{', '.join(candidate.get('criteria', []))} | "
            f"{candidate['reason']} | "
            f"{candidate.get('proof_status', 'unknown')} |"
        )
    return "\n".join(lines)


def version_target(candidate: dict[str, Any]) -> str:
    version = candidate.get("latest_fdroid_version")
    version_code = candidate.get("latest_fdroid_version_code")
    if version and version_code:
        return f"{version} ({version_code})"
    if version:
        return version
    if candidate.get("source_tag_or_commit") and candidate["source_tag_or_commit"] != "to verify":
        return candidate["source_tag_or_commit"]
    return "to verify"


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
