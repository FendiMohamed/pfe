from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path("configs/libraries.source_observed_versions.json")
DEFAULT_ARTIFACT_ROOT = Path("data/reference_db/artifacts_source_observed_versions")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/source-observed-failed-download-retry-plan.json")
DEFAULT_OUTPUT_MD = Path("docs/evaluation/SOURCE_OBSERVED_FAILED_DOWNLOAD_RETRY_PLAN.md")
DEFAULT_ALT_PACKAGING_CONFIG = Path("configs/libraries.source_observed_failed_retry_alt_packaging.json")
DEFAULT_DEFAULT_AAR_CONFIG = Path("configs/libraries.source_observed_failed_retry_default_aar.json")
DEFAULT_ALIAS_NORMALIZED_CONFIG = Path("configs/libraries.source_observed_failed_retry_alias_normalized.json")
GOOGLE_MAVEN = "https://dl.google.com/dl/android/maven2"
JITPACK = "https://jitpack.io"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify source-observed Maven download failures and build retry configs.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--alt-packaging-config", default=str(DEFAULT_ALT_PACKAGING_CONFIG))
    parser.add_argument("--default-aar-config", default=str(DEFAULT_DEFAULT_AAR_CONFIG))
    parser.add_argument("--alias-normalized-config", default=str(DEFAULT_ALIAS_NORMALIZED_CONFIG))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_retry_plan(
        config_path=Path(args.config),
        artifact_root=Path(args.artifact_root),
        alt_packaging_config_path=Path(args.alt_packaging_config),
        default_aar_config_path=Path(args.default_aar_config),
        alias_normalized_config_path=Path(args.alias_normalized_config),
    )
    write_json(Path(args.output_json), payload)
    write_markdown(Path(args.output_md), payload)
    write_json(Path(args.alt_packaging_config), payload["retry_configs"]["alt_packaging"])
    write_json(Path(args.default_aar_config), payload["retry_configs"]["default_aar"])
    write_json(Path(args.alias_normalized_config), payload["retry_configs"]["alias_normalized"])
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


def build_retry_plan(
    *,
    config_path: Path,
    artifact_root: Path,
    alt_packaging_config_path: Path,
    default_aar_config_path: Path,
    alias_normalized_config_path: Path,
) -> dict[str, Any]:
    config = read_json(config_path)
    downloaded = downloaded_keys(artifact_root)
    failed = reconstruct_failed_entries(config, downloaded)
    classified = [classify(entry) for entry in failed]
    alt_packaging_libraries = build_alt_packaging_config(classified)
    default_aar_libraries = build_default_aar_config(classified)
    alias_normalized_libraries = build_alias_normalized_config(classified)
    category_counts = Counter(row["retry_class"] for row in classified)
    repository_counts = Counter(row["repository_url"] or "default" for row in classified)
    packaging_counts = Counter(row["packaging"] for row in classified)
    group_counts = Counter(row["group"] for row in classified)
    summary = {
        "source_config": normalize_path(config_path),
        "artifact_root": normalize_path(artifact_root),
        "attempted_source_versions": sum(len(lib.get("versions", [])) for lib in config["libraries"]),
        "downloaded_artifact_metadata_records": len(downloaded),
        "failed_downloads_reconstructed": len(classified),
        "retry_classes": dict(sorted(category_counts.items())),
        "repositories": dict(sorted(repository_counts.items())),
        "packaging": dict(sorted(packaging_counts.items())),
        "alt_packaging_retry_versions": sum(len(lib["versions"]) for lib in alt_packaging_libraries),
        "alt_packaging_retry_config": normalize_path(alt_packaging_config_path),
        "default_aar_retry_versions": sum(len(lib["versions"]) for lib in default_aar_libraries),
        "default_aar_retry_config": normalize_path(default_aar_config_path),
        "alias_normalized_retry_versions": sum(len(lib["versions"]) for lib in alias_normalized_libraries),
        "alias_normalized_retry_config": normalize_path(alias_normalized_config_path),
        "top_failed_groups": group_counts.most_common(25),
    }
    return {
        "summary": summary,
        "failed_downloads": classified,
        "retry_configs": {
            "alt_packaging": {
                "libraries": alt_packaging_libraries,
            },
            "default_aar": {
                "libraries": default_aar_libraries,
            },
            "alias_normalized": {
                "libraries": alias_normalized_libraries,
            },
        },
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
    config: dict[str, Any],
    downloaded: set[tuple[str, str, str]],
) -> list[dict[str, Any]]:
    failed: list[dict[str, Any]] = []
    for library in config["libraries"]:
        for version in library.get("versions", []):
            key = (library["group"], library["artifact"], version)
            if key in downloaded:
                continue
            failed.append(
                {
                    "group": library["group"],
                    "artifact": library["artifact"],
                    "version": version,
                    "packaging": library.get("packaging", "jar"),
                    "repository_url": library.get("repository_url"),
                    "category": library.get("category"),
                    "notes": library.get("notes"),
                }
            )
    return failed


def classify(entry: dict[str, Any]) -> dict[str, Any]:
    group = entry["group"]
    artifact = entry["artifact"]
    version = entry["version"]
    repository = entry.get("repository_url")
    retry_class = "manual-repository-or-unavailable"
    retry_reason = "Not enough signal for an automatic retry other than all-versions metadata expansion."
    retry_action = "Keep as attempted-failed unless a repository alias or source-specific repository is identified."

    if group in {"feature", "core"}:
        retry_class = "source-module-alias"
        retry_reason = "Source dependency tree contains a Gradle module-like coordinate, not a public Maven group."
        retry_action = "Do not retry as Maven; keep as source-observed module alias."
    elif ":" in version or version in {artifact, group.rsplit(".", maxsplit=1)[-1]}:
        retry_class = "bad-source-version-string"
        retry_reason = "The version value looks like a coordinate, module name, or alias rather than a Maven version."
        retry_action = "Normalize from source metadata if possible; otherwise keep as attempted-failed."
    elif group == "com.android.support":
        retry_class = "legacy-support-alias"
        retry_reason = "Legacy support-library coordinates often appear with AndroidX-era source versions."
        retry_action = "Map to AndroidX replacement only as a report-only/reference-growth note, not as the same Maven coordinate."
    elif group.startswith("com.github."):
        retry_class = "jitpack-candidate"
        retry_reason = "GitHub-style group may exist only on JitPack or under a different Maven coordinate."
        retry_action = f"Retry via {JITPACK}; if absent, keep explicit JitPack/source-tag boundary."
    elif repository == GOOGLE_MAVEN:
        retry_class = "google-alt-packaging"
        retry_reason = "Google Maven row may have been attempted with the wrong artifact packaging."
        retry_action = "Retry the same coordinate/version with the opposite JAR/AAR packaging."
    elif group.startswith("androidx."):
        retry_class = "androidx-repository-or-packaging"
        retry_reason = "AndroidX row failed despite source-observed evidence; repository or packaging may be wrong."
        retry_action = "Retry against Google Maven and alternate packaging."
    elif group.startswith("org.jetbrains.kotlin"):
        retry_class = "kotlin-artifact-boundary"
        retry_reason = "Kotlin compiler/plugin artifacts may be metadata-only, relocated, or not Android bytecode references."
        retry_action = "Retry alternate packaging only for library-like artifacts; otherwise keep as toolchain boundary."
    elif group.startswith("org.videolan"):
        retry_class = "special-repository-candidate"
        retry_reason = "VideoLAN artifacts are often published outside Maven Central/Google Maven."
        retry_action = "Check upstream repository coordinates before retrying."

    row = dict(entry)
    row.update(
        {
            "retry_class": retry_class,
            "retry_reason": retry_reason,
            "retry_action": retry_action,
        }
    )
    return row


def build_alt_packaging_config(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str | None, str, str | None], list[str]] = defaultdict(list)
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
        grouped[(row["group"], row["artifact"], repository_url, retry_packaging, row.get("category"))].append(row["version"])
    libraries = []
    for (group, artifact, repository_url, packaging, category), versions in sorted(grouped.items()):
        library: dict[str, Any] = {
            "group": group,
            "artifact": artifact,
            "versions": sorted(set(versions), key=version_key),
            "packaging": packaging,
        }
        if repository_url:
            library["repository_url"] = repository_url
        if category:
            library["category"] = category
        library["notes"] = "Retry config generated from source-observed failed downloads; uses alternate packaging or repository."
        libraries.append(library)
    return libraries


def build_default_aar_config(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str | None], list[str]] = defaultdict(list)
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
        grouped[(row["group"], row["artifact"], row.get("category"))].append(row["version"])
    libraries = []
    for (group, artifact, category), versions in sorted(grouped.items()):
        library: dict[str, Any] = {
            "group": group,
            "artifact": artifact,
            "versions": sorted(set(versions), key=version_key),
            "packaging": "aar",
            "notes": "Retry config generated from failed source-observed Maven Central JAR downloads; tries AAR packaging.",
        }
        if category:
            library["category"] = category
        libraries.append(library)
    return libraries


def build_alias_normalized_config(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str | None], list[str]] = defaultdict(list)
    for row in rows:
        if row["retry_class"] != "bad-source-version-string":
            continue
        parsed = parse_coordinate_version_alias(row["version"])
        if parsed is None:
            continue
        group, artifact, version = parsed
        repository_url = GOOGLE_MAVEN if group.startswith("androidx.") else row.get("repository_url")
        grouped[(group, artifact, repository_url or "", row.get("category"))].append(version)
    libraries = []
    for (group, artifact, repository_url, category), versions in sorted(grouped.items()):
        packaging = "aar" if group.startswith("androidx.") or group == "com.facebook.react" else "jar"
        library: dict[str, Any] = {
            "group": group,
            "artifact": artifact,
            "versions": sorted(set(versions), key=version_key),
            "packaging": packaging,
            "notes": "Retry config generated by normalizing source rows whose version field contained another Maven coordinate.",
        }
        if repository_url:
            library["repository_url"] = repository_url
        if category:
            library["category"] = category
        libraries.append(library)
    return libraries


def parse_coordinate_version_alias(value: str) -> tuple[str, str, str] | None:
    parts = value.split(":")
    if len(parts) != 3:
        return None
    group, artifact, version = parts
    if not group or not artifact or not version:
        return None
    return group, artifact, version


def version_key(value: str) -> tuple:
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in value.replace("-", ".").split(".")
    )


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Source-Observed Failed Download Retry Plan",
        "",
        "Generated by `scripts/build_source_observed_failed_download_retry_plan.py`.",
        "",
        "This plan reconstructs failed source-observed downloads from the source-version config minus downloaded artifact metadata. It does not change the shared calibrated DB, matcher scoring, SBOM output, vulnerability labels, or source-validation metrics.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Attempted source-version slots | {summary['attempted_source_versions']} |",
        f"| Downloaded artifact metadata records | {summary['downloaded_artifact_metadata_records']} |",
        f"| Reconstructed failed downloads | {summary['failed_downloads_reconstructed']} |",
        f"| Alt-packaging/repository retry versions | {summary['alt_packaging_retry_versions']} |",
        f"| Maven Central AAR retry versions | {summary['default_aar_retry_versions']} |",
        f"| Normalized alias retry versions | {summary['alias_normalized_retry_versions']} |",
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
            "## Top Failed Groups",
            "",
            "| Group | Rows |",
            "|---|---:|",
        ]
    )
    for group, count in summary["top_failed_groups"][:20]:
        lines.append(f"| `{group}` | {count} |")
    lines.extend(
        [
            "",
            "## Retry Configs",
            "",
            f"- Alt packaging/repository retry config: `{summary['alt_packaging_retry_config']}`",
            f"- Maven Central AAR retry config: `{summary['default_aar_retry_config']}`",
            f"- Normalized alias retry config: `{summary['alias_normalized_retry_config']}`",
            "",
            "## Next Step",
            "",
            "Run the retry config into a separate artifact root first, then convert/extract only the rows that actually download. Keep unresolved rows in this plan as attempted-failed evidence.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_path(path: Path) -> str:
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
