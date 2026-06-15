from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_source_observed_reference_catalog import (
    infer_packaging,
    infer_repository_url,
    normalize_path,
)


DEFAULT_SOURCE_ROOT = Path("data/results/source-validation")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/real-apk-priority-reference-catalog.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/REAL_APK_PRIORITY_REFERENCE_CATALOG.md")
DEFAULT_OUTPUT_CONFIG = Path("configs/libraries.real_apk_priority_versions.json")

DEPENDENCY_RE = re.compile(
    r"(?P<group>[A-Za-z0-9_.-]+):(?P<artifact>[A-Za-z0-9_.-]+):(?P<version>[A-Za-z0-9_.+\\-]+)"
    r"(?:\s*->\s*(?P<resolved>[A-Za-z0-9_.+\\-]+))?"
)

METADATA_ONLY_ARTIFACT_MARKERS = ("-bom", "_bom", "gradle-plugin")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deadline-friendly reference DB catalog from versions actually "
            "observed in real-APK source dependency trees."
        )
    )
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--output-config", default=str(DEFAULT_OUTPUT_CONFIG))
    parser.add_argument(
        "--min-apk-support",
        type=int,
        default=2,
        help="Minimum distinct source-validation tree folders supporting tier-1 entries.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_root = Path(args.source_root)
    payload = build_payload(source_root, min_apk_support=args.min_apk_support)

    output_json = Path(args.output_json)
    output_doc = Path(args.output_doc)
    output_config = Path(args.output_config)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_config.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    output_config.write_text(
        json.dumps({"libraries": payload["download_config_libraries"]}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "json": normalize_path(output_json),
                "doc": normalize_path(output_doc),
                "config": normalize_path(output_config),
                **payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(source_root: Path, *, min_apk_support: int) -> dict[str, Any]:
    tree_paths = sorted(
        path
        for path in source_root.rglob("*.txt")
        if path.is_file() and is_runtime_dependency_tree(path)
    )
    occurrences: Counter[tuple[str, str]] = Counter()
    apk_support: dict[tuple[str, str], set[str]] = defaultdict(set)
    coordinate_versions: dict[str, set[str]] = defaultdict(set)
    coordinate_apks: dict[str, set[str]] = defaultdict(set)

    for tree_path in tree_paths:
        apk_id = apk_id_for_path(source_root, tree_path)
        seen_in_tree: set[tuple[str, str]] = set()
        for coordinate, version in parse_dependency_tree(tree_path):
            if is_metadata_only(coordinate):
                continue
            key = (coordinate, version)
            occurrences[key] += 1
            seen_in_tree.add(key)
            coordinate_versions[coordinate].add(version)
            coordinate_apks[coordinate].add(apk_id)
        for key in seen_in_tree:
            apk_support[key].add(apk_id)

    entries = []
    for (coordinate, version), occurrence_count in occurrences.items():
        group, artifact = coordinate.split(":", maxsplit=1)
        support = sorted(apk_support[(coordinate, version)])
        tier = classify_tier(len(support), occurrence_count, min_apk_support)
        entries.append(
            {
                "coordinate": coordinate,
                "group": group,
                "artifact": artifact,
                "version": version,
                "apk_support_count": len(support),
                "occurrence_count": occurrence_count,
                "apk_support": support,
                "tier": tier,
                "packaging": infer_packaging(group, artifact),
                "repository_url": infer_repository_url(group),
            }
        )

    entries.sort(
        key=lambda item: (
            tier_order(item["tier"]),
            -item["apk_support_count"],
            -item["occurrence_count"],
            item["coordinate"],
            item["version"],
        )
    )

    libraries = build_download_config(entries)
    return {
        "schema_version": 1,
        "purpose": "deadline-prioritized reference expansion from real APK source dependency trees",
        "sources": {
            "source_root": normalize_path(source_root),
            "tree_count": len(tree_paths),
        },
        "policy": [
            "This is an evaluation-only priority DB lane.",
            "It prioritizes exact versions observed in the real APK source-validation corpus.",
            "It does not replace the full 60979-slot all-versions transparency lane.",
            "No shared calibrated DB, matcher scoring, SBOM emission, or vulnerability labels are changed by this catalog.",
        ],
        "summary": {
            "dependency_tree_files": len(tree_paths),
            "unique_coordinate_versions": len(entries),
            "unique_coordinates": len(coordinate_versions),
            "tier1_repeated_coordinate_versions": sum(
                1 for item in entries if item["tier"] == "tier1-repeated-real-apk-version"
            ),
            "tier2_single_observed_coordinate_versions": sum(
                1 for item in entries if item["tier"] == "tier2-single-real-apk-version"
            ),
            "download_libraries": len(libraries),
            "download_slots": sum(len(item["versions"]) for item in libraries),
            "min_apk_support": min_apk_support,
        },
        "top_repeated_versions": entries[:50],
        "entries": entries,
        "download_config_libraries": libraries,
    }


def parse_dependency_tree(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if "project " in line or "---" not in line and "\\---" not in line:
            continue
        for match in DEPENDENCY_RE.finditer(line):
            group = match.group("group")
            artifact = match.group("artifact")
            version = match.group("resolved") or match.group("version")
            version = version.rstrip(".,;)")
            if version and not version.endswith("(c)"):
                rows.append((f"{group}:{artifact}", version))
    return rows


def apk_id_for_path(source_root: Path, tree_path: Path) -> str:
    relative = tree_path.relative_to(source_root)
    return relative.parts[0] if relative.parts else tree_path.stem


def is_runtime_dependency_tree(path: Path) -> bool:
    name = path.name.lower()
    if "runtimeclasspath" in name:
        return True
    if name in {"dependencies.txt", "dependency-tree.txt"}:
        return True
    return False


def classify_tier(apk_count: int, occurrence_count: int, min_apk_support: int) -> str:
    if apk_count >= min_apk_support:
        return "tier1-repeated-real-apk-version"
    return "tier2-single-real-apk-version"


def tier_order(tier: str) -> int:
    if tier.startswith("tier1"):
        return 0
    if tier.startswith("tier2"):
        return 1
    return 2


def is_metadata_only(coordinate: str) -> bool:
    artifact = coordinate.split(":", maxsplit=1)[1]
    return any(marker in artifact for marker in METADATA_ONLY_ARTIFACT_MARKERS)


def build_download_config(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        coordinate = entry["coordinate"]
        group, artifact = coordinate.split(":", maxsplit=1)
        item = grouped.setdefault(
            coordinate,
            {
                "group": group,
                "artifact": artifact,
                "packaging": entry["packaging"],
                "repository_url": entry["repository_url"],
                "versions": set(),
            },
        )
        item["versions"].add(entry["version"])
    libraries = []
    for coordinate in sorted(grouped):
        item = grouped[coordinate]
        libraries.append(
            {
                "group": item["group"],
                "artifact": item["artifact"],
                "packaging": item["packaging"],
                "repository_url": item["repository_url"],
                "versions": sorted(item["versions"]),
            }
        )
    return libraries


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Real APK Priority Reference Catalog",
        "",
        "This is the deadline-friendly reference expansion lane. It keeps the full all-versions lane honest, but prioritizes exact versions that actually appear in the real APK source-validation dependency trees.",
        "",
        "## Summary",
        "",
        f"- Dependency tree files scanned: `{summary['dependency_tree_files']}`",
        f"- Unique coordinates: `{summary['unique_coordinates']}`",
        f"- Unique coordinate-version slots: `{summary['unique_coordinate_versions']}`",
        f"- Tier 1 repeated real-APK versions: `{summary['tier1_repeated_coordinate_versions']}`",
        f"- Tier 2 single real-APK versions: `{summary['tier2_single_observed_coordinate_versions']}`",
        f"- Download config libraries: `{summary['download_libraries']}`",
        f"- Download config slots: `{summary['download_slots']}`",
        "",
        "## Policy",
        "",
    ]
    for item in payload["policy"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Top Repeated Versions",
            "",
            "| Rank | Tier | Coordinate | Version | APK support | Occurrences |",
            "|---:|---|---|---|---:|---:|",
        ]
    )
    for index, entry in enumerate(payload["top_repeated_versions"][:30], start=1):
        lines.append(
            f"| {index} | {entry['tier']} | `{entry['coordinate']}` | `{entry['version']}` | "
            f"{entry['apk_support_count']} | {entry['occurrence_count']} |"
        )
    lines.extend(
        [
            "",
            "## Next Commands",
            "",
            "```powershell",
            "python scripts\\build_real_apk_priority_reference_catalog.py",
            "docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven --config configs/libraries.real_apk_priority_versions.json --output-root data/reference_db/artifacts_real_apk_priority_versions --limit 500 --offset 0 --quiet",
            "docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex --artifact-root data/reference_db/artifacts_real_apk_priority_versions --output-root data/reference_db/dex_real_apk_priority_versions --limit 250 --offset 0 --quiet",
            "docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features --dex-root data/reference_db/dex_real_apk_priority_versions --db-path data/reference_db/reference_features_real_apk_priority_versions.sqlite --reset --quiet",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
