from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_source_observed_failed_download_retry_plan import (
    GOOGLE_MAVEN,
    JITPACK,
    classify,
    parse_coordinate_version_alias,
    version_key,
)


DEFAULT_CATALOG_JSON = Path("data/results/evaluation/real-apk-priority-reference-catalog.json")
DEFAULT_ARTIFACT_ROOT = Path("data/reference_db/artifacts_real_apk_priority_versions")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/real-apk-priority-failed-download-retry-plan.json")
DEFAULT_OUTPUT_MD = Path("docs/evaluation/REAL_APK_PRIORITY_FAILED_DOWNLOAD_RETRY_PLAN.md")
DEFAULT_ALT_PACKAGING_CONFIG = Path("configs/libraries.real_apk_priority_failed_retry_alt_packaging.json")
DEFAULT_DEFAULT_AAR_CONFIG = Path("configs/libraries.real_apk_priority_failed_retry_default_aar.json")
DEFAULT_ALIAS_NORMALIZED_CONFIG = Path("configs/libraries.real_apk_priority_failed_retry_alias_normalized.json")
DEFAULT_ALIAS_NORMALIZED_ALT_CONFIG = Path(
    "configs/libraries.real_apk_priority_failed_retry_alias_normalized_alt_packaging.json"
)
DEFAULT_ALT_RETRY_ARTIFACT_ROOT = Path(
    "data/reference_db/artifacts_real_apk_priority_failed_retry_alt_packaging"
)
DEFAULT_DEFAULT_AAR_RETRY_ARTIFACT_ROOT = Path(
    "data/reference_db/artifacts_real_apk_priority_failed_retry_default_aar"
)
DEFAULT_ALT_RETRY_DEX_ROOT = Path(
    "data/reference_db/dex_real_apk_priority_failed_retry_alt_packaging"
)
DEFAULT_DEFAULT_AAR_RETRY_DEX_ROOT = Path(
    "data/reference_db/dex_real_apk_priority_failed_retry_default_aar"
)
DEFAULT_PRIORITY_DB = Path("data/reference_db/reference_features_real_apk_priority_versions.sqlite")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Classify failed real-APK priority reference downloads and build retry configs "
            "ranked by APK support/occurrence evidence."
        )
    )
    parser.add_argument("--catalog-json", default=str(DEFAULT_CATALOG_JSON))
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--alt-packaging-config", default=str(DEFAULT_ALT_PACKAGING_CONFIG))
    parser.add_argument("--default-aar-config", default=str(DEFAULT_DEFAULT_AAR_CONFIG))
    parser.add_argument("--alias-normalized-config", default=str(DEFAULT_ALIAS_NORMALIZED_CONFIG))
    parser.add_argument("--alias-normalized-alt-config", default=str(DEFAULT_ALIAS_NORMALIZED_ALT_CONFIG))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_retry_plan(
        catalog_json=Path(args.catalog_json),
        artifact_root=Path(args.artifact_root),
        alt_packaging_config_path=Path(args.alt_packaging_config),
        default_aar_config_path=Path(args.default_aar_config),
        alias_normalized_config_path=Path(args.alias_normalized_config),
        alias_normalized_alt_config_path=Path(args.alias_normalized_alt_config),
    )
    write_json(Path(args.output_json), payload)
    write_markdown(Path(args.output_md), payload)
    write_json(Path(args.alt_packaging_config), payload["retry_configs"]["alt_packaging"])
    write_json(Path(args.default_aar_config), payload["retry_configs"]["default_aar"])
    write_json(Path(args.alias_normalized_config), payload["retry_configs"]["alias_normalized"])
    write_json(Path(args.alias_normalized_alt_config), payload["retry_configs"]["alias_normalized_alt_packaging"])
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


def build_retry_plan(
    *,
    catalog_json: Path,
    artifact_root: Path,
    alt_packaging_config_path: Path,
    default_aar_config_path: Path,
    alias_normalized_config_path: Path,
    alias_normalized_alt_config_path: Path,
) -> dict[str, Any]:
    catalog = read_json(catalog_json)
    downloaded = downloaded_keys(artifact_root)
    failed = reconstruct_failed_entries(catalog, downloaded)
    classified = [classify(entry) for entry in failed]
    classified.sort(key=priority_key)

    retry_configs = {
        "alt_packaging": {
            "libraries": build_alt_packaging_config(classified),
        },
        "default_aar": {
            "libraries": build_default_aar_config(classified),
        },
        "alias_normalized": {
            "libraries": build_alias_normalized_config(classified),
        },
        "alias_normalized_alt_packaging": {
            "libraries": build_alias_normalized_config(classified, alternate_packaging=True),
        },
    }

    category_counts = Counter(row["retry_class"] for row in classified)
    tier_counts = Counter(row["tier"] for row in classified)
    group_counts = Counter(row["group"] for row in classified)
    repeated_failed = [row for row in classified if row["apk_support_count"] >= 2]
    automatic_classes = {
        "androidx-repository-or-packaging",
        "google-alt-packaging",
        "jitpack-candidate",
        "manual-repository-or-unavailable",
    }
    automatic_retry_rows = [
        row
        for row in classified
        if row["retry_class"] in automatic_classes
        or parse_coordinate_version_alias(row["version"]) is not None
    ]
    summary = {
        "priority_catalog": normalize_path(catalog_json),
        "artifact_root": normalize_path(artifact_root),
        "attempted_priority_slots": len(catalog.get("entries", [])),
        "downloaded_artifact_metadata_records": len(downloaded),
        "failed_downloads_reconstructed": len(classified),
        "failed_repeated_rows": len(repeated_failed),
        "failed_single_rows": len(classified) - len(repeated_failed),
        "top_failed_apk_support_count": classified[0]["apk_support_count"] if classified else 0,
        "top_failed_occurrence_count": classified[0]["occurrence_count"] if classified else 0,
        "retry_classes": dict(sorted(category_counts.items())),
        "tiers": dict(sorted(tier_counts.items())),
        "top_failed_groups": group_counts.most_common(25),
        "automatic_retry_candidate_rows": len(automatic_retry_rows),
        "alt_packaging_retry_versions": count_versions(retry_configs["alt_packaging"]),
        "alt_packaging_retry_config": normalize_path(alt_packaging_config_path),
        "default_aar_retry_versions": count_versions(retry_configs["default_aar"]),
        "default_aar_retry_config": normalize_path(default_aar_config_path),
        "alias_normalized_retry_versions": count_versions(retry_configs["alias_normalized"]),
        "alias_normalized_retry_config": normalize_path(alias_normalized_config_path),
        "alias_normalized_alt_retry_versions": count_versions(retry_configs["alias_normalized_alt_packaging"]),
        "alias_normalized_alt_retry_config": normalize_path(alias_normalized_alt_config_path),
    }
    return {
        "summary": summary,
        "failed_downloads": classified,
        "top_failed_downloads": classified[:100],
        "retry_configs": retry_configs,
    }


def downloaded_keys(root: Path) -> set[tuple[str, str, str]]:
    keys: set[tuple[str, str, str]] = set()
    for path in root.rglob("metadata.json"):
        metadata = read_json(path)
        group = metadata.get("group")
        artifact = metadata.get("artifact")
        version = metadata.get("version")
        if group and artifact and version:
            keys.add((group, artifact, version))
    return keys


def reconstruct_failed_entries(
    catalog: dict[str, Any],
    downloaded: set[tuple[str, str, str]],
) -> list[dict[str, Any]]:
    failed: list[dict[str, Any]] = []
    for entry in catalog.get("entries", []):
        key = (entry["group"], entry["artifact"], entry["version"])
        if key in downloaded:
            continue
        failed.append(
            {
                "group": entry["group"],
                "artifact": entry["artifact"],
                "version": entry["version"],
                "packaging": entry.get("packaging", "jar"),
                "repository_url": entry.get("repository_url"),
                "category": entry.get("tier"),
                "notes": (
                    f"Priority retry row; apk_support={entry.get('apk_support_count', 0)}, "
                    f"occurrences={entry.get('occurrence_count', 0)}"
                ),
                "coordinate": entry["coordinate"],
                "tier": entry.get("tier"),
                "apk_support_count": entry.get("apk_support_count", 0),
                "occurrence_count": entry.get("occurrence_count", 0),
                "apk_support": entry.get("apk_support", []),
            }
        )
    return failed


def build_alt_packaging_config(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str | None, str, str | None], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["retry_class"] not in {
            "google-alt-packaging",
            "androidx-repository-or-packaging",
            "jitpack-candidate",
        }:
            continue
        repository_url = row.get("repository_url")
        if row["retry_class"] == "androidx-repository-or-packaging":
            repository_url = GOOGLE_MAVEN
        if row["retry_class"] == "jitpack-candidate":
            repository_url = JITPACK
        retry_packaging = "aar" if row["packaging"] == "jar" else "jar"
        grouped[(row["group"], row["artifact"], repository_url, retry_packaging, row.get("category"))].append(row)
    return build_libraries(grouped, "Priority failed-download retry; alternate packaging or repository.")


def build_default_aar_config(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str | None, str, str | None], list[dict[str, Any]]] = defaultdict(list)
    excluded = {
        "bad-source-version-string",
        "source-module-alias",
        "kotlin-artifact-boundary",
        "legacy-support-alias",
    }
    for row in rows:
        if row["retry_class"] in excluded:
            continue
        if row.get("repository_url") or row["packaging"] != "jar":
            continue
        grouped[(row["group"], row["artifact"], None, "aar", row.get("category"))].append(row)
    return build_libraries(grouped, "Priority failed-download retry; Maven Central AAR fallback.")


def build_alias_normalized_config(
    rows: list[dict[str, Any]],
    *,
    alternate_packaging: bool = False,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str | None, str, str | None], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        parsed = parse_coordinate_version_alias(row["version"])
        if parsed is None:
            continue
        group, artifact, version = parsed
        repository_url = GOOGLE_MAVEN if group.startswith("androidx.") else row.get("repository_url")
        base_packaging = "aar" if group.startswith("androidx.") or group == "com.facebook.react" else "jar"
        packaging = "jar" if base_packaging == "aar" and alternate_packaging else base_packaging
        if base_packaging == "jar" and alternate_packaging:
            packaging = "aar"
        normalized = dict(row)
        normalized.update({"group": group, "artifact": artifact, "version": version})
        grouped[(group, artifact, repository_url, packaging, row.get("category"))].append(normalized)
    note = (
        "Priority failed-download retry; normalized coordinate-like version strings with alternate packaging."
        if alternate_packaging
        else "Priority failed-download retry; normalized coordinate-like version strings."
    )
    return build_libraries(grouped, note)


def build_libraries(
    grouped: dict[tuple[str, str, str | None, str, str | None], list[dict[str, Any]]],
    note: str,
) -> list[dict[str, Any]]:
    libraries = []
    ordered_groups = sorted(
        grouped.items(),
        key=lambda item: (
            -max(row["apk_support_count"] for row in item[1]),
            -sum(row["occurrence_count"] for row in item[1]),
            item[0][0],
            item[0][1],
        ),
    )
    for (group, artifact, repository_url, packaging, category), rows in ordered_groups:
        versions = sorted({row["version"] for row in rows}, key=version_key)
        library: dict[str, Any] = {
            "group": group,
            "artifact": artifact,
            "versions": versions,
            "packaging": packaging,
            "notes": note,
        }
        if repository_url:
            library["repository_url"] = repository_url
        if category:
            library["category"] = category
        libraries.append(library)
    return libraries


def count_versions(config: dict[str, Any]) -> int:
    return sum(len(library["versions"]) for library in config["libraries"])


def priority_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -row["apk_support_count"],
        -row["occurrence_count"],
        row["retry_class"],
        row["coordinate"],
        version_key(row["version"]),
    )


def build_execution_update(payload: dict[str, Any]) -> dict[str, Any] | None:
    retry_roots = [
        DEFAULT_ALT_RETRY_ARTIFACT_ROOT,
        DEFAULT_DEFAULT_AAR_RETRY_ARTIFACT_ROOT,
    ]
    dex_roots = [
        DEFAULT_ALT_RETRY_DEX_ROOT,
        DEFAULT_DEFAULT_AAR_RETRY_DEX_ROOT,
    ]
    if not any(root.exists() for root in retry_roots):
        return None

    base_downloaded = downloaded_keys(Path(payload["summary"]["artifact_root"]))
    retry_downloaded_by_root = [downloaded_keys(root) if root.exists() else set() for root in retry_roots]
    retry_downloaded = set().union(*retry_downloaded_by_root)
    all_downloaded = base_downloaded | retry_downloaded
    remaining = [
        row
        for row in payload["failed_downloads"]
        if (row["group"], row["artifact"], row["version"]) not in all_downloaded
    ]
    retry_conversion_counts = [
        conversion_status_counts(root) if root.exists() else Counter() for root in dex_roots
    ]
    bytecode_rows = sum(
        counts.get("converted", 0) + counts.get("existing", 0)
        for counts in retry_conversion_counts
    )
    return {
        "alt_downloaded": len(retry_downloaded_by_root[0]),
        "default_aar_downloaded": len(retry_downloaded_by_root[1]),
        "alt_conversion": dict(sorted(retry_conversion_counts[0].items())),
        "default_aar_conversion": dict(sorted(retry_conversion_counts[1].items())),
        "net_recovered_artifacts": len(retry_downloaded),
        "net_recovered_bytecode_rows": bytecode_rows,
        "priority_db_components": count_db_components(DEFAULT_PRIORITY_DB),
        "recovered_priority_artifacts": len(all_downloaded),
        "attempted_priority_slots": payload["summary"]["attempted_priority_slots"],
        "remaining_unrecovered": len(remaining),
        "remaining_repeated": sum(1 for row in remaining if row["apk_support_count"] >= 2),
        "remaining_single": sum(1 for row in remaining if row["apk_support_count"] < 2),
    }


def conversion_status_counts(root: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in root.rglob("conversion.json"):
        conversion = read_json(path)
        counts[conversion.get("status") or "unknown"] += 1
    return counts


def count_db_components(path: Path) -> int:
    if not path.exists():
        return 0
    with sqlite3.connect(path) as conn:
        row = conn.execute("select count(*) from components").fetchone()
    return int(row[0]) if row else 0


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Real APK Priority Failed Download Retry Plan",
        "",
        "Generated by `scripts/build_real_apk_priority_failed_download_retry_plan.py`.",
        "",
        "This plan reconstructs failed downloads from the real-APK priority catalog minus downloaded artifact metadata. It ranks failed rows by APK support and occurrence count, then writes retry configs for automatic packaging/repository/alias attempts. It does not change the shared calibrated DB, matcher scoring, SBOM output, vulnerability labels, or source-validation metrics.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Attempted priority slots | {summary['attempted_priority_slots']} |",
        f"| Downloaded artifact metadata records | {summary['downloaded_artifact_metadata_records']} |",
        f"| Reconstructed failed downloads | {summary['failed_downloads_reconstructed']} |",
        f"| Failed repeated rows | {summary['failed_repeated_rows']} |",
        f"| Failed single rows | {summary['failed_single_rows']} |",
        f"| Automatic retry candidate rows | {summary['automatic_retry_candidate_rows']} |",
        f"| Alt-packaging/repository retry versions | {summary['alt_packaging_retry_versions']} |",
        f"| Maven Central AAR retry versions | {summary['default_aar_retry_versions']} |",
        f"| Normalized alias retry versions | {summary['alias_normalized_retry_versions']} |",
        f"| Normalized alias alternate-packaging retry versions | {summary['alias_normalized_alt_retry_versions']} |",
        "",
        "## Retry Classes",
        "",
        "| Class | Rows |",
        "|---|---:|",
    ]
    for name, count in summary["retry_classes"].items():
        lines.append(f"| `{name}` | {count} |")
    lines.extend(
        [
            "",
            "## Top Failed Rows",
            "",
            "| Rank | Retry class | Coordinate | Version | APK support | Occurrences |",
            "|---:|---|---|---|---:|---:|",
        ]
    )
    for index, row in enumerate(payload["top_failed_downloads"][:30], start=1):
        lines.append(
            f"| {index} | `{row['retry_class']}` | `{row['coordinate']}` | `{row['version']}` | "
            f"{row['apk_support_count']} | {row['occurrence_count']} |"
        )
    lines.extend(
        [
            "",
            "## Retry Configs",
            "",
            f"- Alt packaging/repository retry config: `{summary['alt_packaging_retry_config']}`",
            f"- Maven Central AAR retry config: `{summary['default_aar_retry_config']}`",
            f"- Normalized alias retry config: `{summary['alias_normalized_retry_config']}`",
            f"- Normalized alias alternate-packaging retry config: `{summary['alias_normalized_alt_retry_config']}`",
            "",
        ]
    )
    execution_update = build_execution_update(payload)
    if execution_update:
        lines.extend(
            [
                "## Execution Update",
                "",
                "| Metric | Value |",
                "|---|---:|",
                f"| Alt-packaging/repository retry downloads | {execution_update['alt_downloaded']} |",
                f"| Maven Central AAR retry downloads | {execution_update['default_aar_downloaded']} |",
                f"| Net recovered priority artifacts across retry roots | {execution_update['net_recovered_artifacts']} |",
                f"| Net recovered bytecode-bearing priority rows | {execution_update['net_recovered_bytecode_rows']} |",
                f"| Priority DB components after retry extraction | {execution_update['priority_db_components']} |",
                f"| Recovered priority artifact metadata across base and retry roots | {execution_update['recovered_priority_artifacts']}/{execution_update['attempted_priority_slots']} |",
                f"| Remaining unrecovered priority slots | {execution_update['remaining_unrecovered']} |",
                f"| Remaining repeated unrecovered slots | {execution_update['remaining_repeated']} |",
                f"| Remaining single-observed unrecovered slots | {execution_update['remaining_single']} |",
                "",
                "Conversion status counts by retry root:",
                "",
                f"- Alt-packaging/repository: {format_counts(execution_update['alt_conversion'])}",
                f"- Maven Central AAR: {format_counts(execution_update['default_aar_conversion'])}",
                "",
                "The retry pass keeps the remaining unrecovered/source-boundary rows explicit instead of silently counting them as covered.",
                "",
            ]
        )
    if execution_update:
        next_step = (
            "Use the recovered priority DB for the source-validation/report rerun, and inspect the "
            "remaining unrecovered rows only through explicit alias/repository evidence. Do not treat "
            "the remaining source/module aliases as covered until that evidence exists."
        )
    else:
        next_step = (
            "Run the retry configs into separate artifact roots, starting with the alt-packaging/repository "
            "config because it contains the highest-priority Google/JitPack/AndroidX automatic candidates. "
            "Convert and extract only recovered bytecode-bearing rows into "
            "`data/reference_db/reference_features_real_apk_priority_versions.sqlite`, then keep unrecovered rows explicit."
        )
    lines.extend(
        [
            "## Next Step",
            "",
            next_step,
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "0 records"
    return ", ".join(f"{name}={count}" for name, count in sorted(counts.items()))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_path(path: Path) -> str:
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
