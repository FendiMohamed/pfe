from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path("configs/real_apk_candidates.json")
DEFAULT_OUTPUT_ROOT = Path("data/results/evaluation/real-apk-proof")
DEFAULT_DOC_PATH = Path("docs/evaluation/REAL_APK_PROOF_BUNDLE_PLAN.md")


CHECKLIST = [
    "Verify package name on the APK source page.",
    "Choose the exact APK version and record versionName/versionCode.",
    "Download the APK and record SHA-256.",
    "Download or checkout the matching source tag, commit, or F-Droid source tarball.",
    "Compare APK manifest versionName/versionCode with source metadata.",
    "Generate the Gradle dependency tree for the release/runtime configuration.",
    "Generate the MVP APK-to-SBOM report.",
    "Run source dependency validation against the generated SBOM.",
    "Update candidate config, dataset inventory, and evaluation notes.",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create proof-bundle checklists for real APK dataset candidates.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--doc-path", default=str(DEFAULT_DOC_PATH))
    parser.add_argument(
        "--candidate",
        action="append",
        help="Candidate id to scaffold. Defaults to first-batch ids from the config.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    matrix = read_json(Path(args.config))
    selected = select_candidates(matrix, args.candidate)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    proof_bundles = [build_proof_bundle(candidate) for candidate in selected]
    for bundle in proof_bundles:
        bundle_dir = output_root / bundle["candidate_id"]
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "proof-checklist.json").write_text(
            json.dumps(bundle, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (bundle_dir / "proof-checklist.md").write_text(
            build_bundle_markdown(bundle),
            encoding="utf-8",
        )

    index_payload = {
        "schema_version": 1,
        "candidate_ids": [bundle["candidate_id"] for bundle in proof_bundles],
        "bundles": proof_bundles,
    }
    (output_root / "index.json").write_text(
        json.dumps(index_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "index.md").write_text(
        build_index_markdown(proof_bundles, output_root),
        encoding="utf-8",
    )

    doc_path = Path(args.doc_path)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(build_index_markdown(proof_bundles, output_root), encoding="utf-8")

    print(
        json.dumps(
            {
                "bundles": len(proof_bundles),
                "candidate_ids": [bundle["candidate_id"] for bundle in proof_bundles],
                "doc": normalize_path(str(doc_path)),
                "output_root": normalize_path(str(output_root)),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def select_candidates(matrix: dict[str, Any], requested: list[str] | None) -> list[dict[str, Any]]:
    by_id = {candidate["id"]: candidate for candidate in matrix["candidates"]}
    ids = requested or matrix.get("first_batch_ids", [])
    missing = [item for item in ids if item not in by_id]
    if missing:
        raise ValueError(f"unknown candidate id(s): {', '.join(missing)}")
    return [by_id[item] for item in ids]


def build_proof_bundle(candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_id = candidate["id"]
    source_suffix = safe_path_segment(candidate.get("latest_fdroid_version") or "version-or-tag")
    return {
        "candidate_id": candidate_id,
        "app": candidate["app"],
        "package_name": candidate["package_name"],
        "target_layer": candidate["target_layer"],
        "validation_level": candidate["validation_level"],
        "priority": candidate["priority"],
        "proof_status": candidate.get("proof_status", "pending"),
        "fdroid_package_url": candidate.get("fdroid_package_url"),
        "source_repo": candidate["source_repo"],
        "source_tag_or_commit": candidate.get("source_tag_or_commit", "to verify"),
        "latest_fdroid_version": candidate.get("latest_fdroid_version"),
        "latest_fdroid_version_code": candidate.get("latest_fdroid_version_code"),
        "latest_fdroid_added": candidate.get("latest_fdroid_added"),
        "latest_fdroid_apk_size": candidate.get("latest_fdroid_apk_size"),
        "criteria": candidate.get("criteria", []),
        "reason": candidate["reason"],
        "planned_paths": {
            "apk": f"data/test_apks/real/{candidate_id}/{candidate_id}.apk",
            "apk_metadata": f"data/test_apks/real/{candidate_id}/metadata.json",
            "source": f"data/source/{candidate_id}-{source_suffix}",
            "dependency_tree": (
                f"data/results/source-validation/{candidate_id}/"
                "fullReleaseRuntimeClasspath.txt"
            ),
            "report_dir": f"data/results/report-real-{candidate_id}",
            "source_validation_dir": f"data/results/source-validation/{candidate_id}",
        },
        "proof_artifacts": candidate.get("proof_artifacts", {}),
        "proof_notes": candidate.get("proof_notes", []),
        "checklist": build_checklist(candidate.get("proof_checklist_status", {})),
    }


def build_bundle_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        f"# Proof Bundle Checklist: {bundle['app']}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Candidate id | `{bundle['candidate_id']}` |",
        f"| Package | `{bundle['package_name']}` |",
        f"| Target layer | {bundle['target_layer']} |",
        f"| Validation level | {bundle['validation_level']} |",
        f"| F-Droid package | `{bundle.get('fdroid_package_url') or 'to verify'}` |",
        f"| Source repo | `{bundle['source_repo']}` |",
        f"| Source tag/commit | {bundle['source_tag_or_commit']} |",
        f"| Latest F-Droid version | {bundle.get('latest_fdroid_version') or 'to verify'} ({bundle.get('latest_fdroid_version_code') or 'code to verify'}) |",
        f"| Added | {bundle.get('latest_fdroid_added') or 'to verify'} |",
        f"| APK size | {bundle.get('latest_fdroid_apk_size') or 'to verify'} |",
        f"| Criteria | {', '.join(bundle['criteria'])} |",
        f"| Reason | {bundle['reason']} |",
        "",
        "## Planned Paths",
        "",
        "| Artifact | Path |",
        "|---|---|",
    ]
    for name, path in bundle["planned_paths"].items():
        lines.append(f"| {name.replace('_', ' ')} | `{path}` |")
    if bundle.get("proof_artifacts"):
        lines.extend(["", "## Current Proof Artifacts", "", "| Artifact | Path / Value |", "|---|---|"])
        for name, value in bundle["proof_artifacts"].items():
            lines.append(f"| {name.replace('_', ' ')} | `{value}` |")
    if bundle.get("proof_notes"):
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in bundle["proof_notes"])
    lines.extend(["", "## Checklist", ""])
    for item in bundle["checklist"]:
        lines.append(f"- [{_checkbox(item['status'])}] {item['task']}")
    lines.append("")
    return "\n".join(lines)


def build_index_markdown(bundles: list[dict[str, Any]], output_root: Path) -> str:
    lines = [
        "# Real APK Proof Bundle Plan",
        "",
        "This file is generated by `scripts/scaffold_real_apk_proof.py`.",
        "It lists the proof bundle required before a candidate APK can move from candidate status to source-validated dataset status.",
        "",
        "## Selected Candidates",
        "",
        "| Candidate | Package | Version target | Proof status | Source | Main criteria | Proof checklist |",
        "|---|---|---|---|---|---|---|",
    ]
    for bundle in bundles:
        checklist_path = normalize_path(
            str(output_root / bundle["candidate_id"] / "proof-checklist.md")
        )
        version = bundle.get("latest_fdroid_version") or "to verify"
        code = bundle.get("latest_fdroid_version_code") or "code to verify"
        lines.append(
            "| "
            f"{bundle['app']} | "
            f"`{bundle['package_name']}` | "
            f"{version} ({code}) | "
            f"{bundle.get('proof_status', 'unknown')} | "
            f"`{bundle['source_repo']}` | "
            f"{', '.join(bundle['criteria'])} | "
            f"`{checklist_path}` |"
        )
    lines.extend(
        [
            "",
            "## Admission Rule",
            "",
            "Do not count a candidate as source-validated until APK/source version matching, dependency-tree generation, report generation, and source validation are complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _checkbox(status: str) -> str:
    return "x" if status == "done" else " "


def build_checklist(status_overrides: dict[str, str]) -> list[dict[str, str]]:
    return [
        {"status": status_overrides.get(item, "pending"), "task": item}
        for item in CHECKLIST
    ]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def safe_path_segment(value: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    return "".join(char if char in allowed else "-" for char in value).strip("-") or "version-or-tag"


if __name__ == "__main__":
    raise SystemExit(main())
