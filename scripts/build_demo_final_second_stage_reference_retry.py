from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_source_observed_failed_download_retry_plan import version_key


DEFAULT_PRIMARY_CONFIG = Path("configs/libraries.demo_final_fixable_missing_reference_retry.json")
DEFAULT_PRIMARY_ARTIFACT_ROOT = Path("data/reference_db/artifacts_demo_final_fixable_retry")
DEFAULT_OUTPUT_CONFIG = Path(
    "configs/libraries.demo_final_fixable_missing_reference_retry_stage2.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/evaluation/demo-final-fixable-reference-retry-stage2-plan.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_RETRY_STAGE2_PLAN.md"
)

MAVEN_CENTRAL = "https://repo1.maven.org/maven2"
GOOGLE_MAVEN = "https://dl.google.com/dl/android/maven2"
JITPACK = "https://jitpack.io"
JETBRAINS_COMPOSE = "https://maven.pkg.jetbrains.space/public/p/compose/dev"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a second-stage retry config for demo-final missing-reference "
            "slots that failed the first fixable retry."
        )
    )
    parser.add_argument("--primary-config", default=str(DEFAULT_PRIMARY_CONFIG))
    parser.add_argument("--primary-artifact-root", default=str(DEFAULT_PRIMARY_ARTIFACT_ROOT))
    parser.add_argument("--output-config", default=str(DEFAULT_OUTPUT_CONFIG))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_plan(
        primary_config=Path(args.primary_config),
        primary_artifact_root=Path(args.primary_artifact_root),
        output_config=Path(args.output_config),
    )
    write_json(Path(args.output_json), payload)
    write_json(Path(args.output_config), payload["retry_config"])
    Path(args.output_doc).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_doc).write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


def build_plan(
    *,
    primary_config: Path,
    primary_artifact_root: Path,
    output_config: Path,
) -> dict[str, Any]:
    primary_slots = load_config_slots(primary_config)
    downloaded = load_artifact_metadata(primary_artifact_root)
    failed_rows = [
        row for row in primary_slots if (row["coordinate"], row["version"]) not in downloaded
    ]

    classified = [classify_second_stage(row) for row in failed_rows]
    retry_rows = [row for row in classified if row["included_in_retry_config"]]
    retry_config = {"libraries": build_libraries(retry_rows)}
    summary = {
        "primary_config": normalize_path(primary_config),
        "primary_artifact_root": normalize_path(primary_artifact_root),
        "output_config": normalize_path(output_config),
        "primary_retry_slots": len(primary_slots),
        "primary_downloaded_slots": len(downloaded),
        "primary_failed_slots": len(failed_rows),
        "second_stage_retry_slots": sum(
            len(library["versions"]) for library in retry_config["libraries"]
        ),
        "second_stage_retry_libraries": len(retry_config["libraries"]),
        "classification_counts": dict(
            sorted(Counter(row["retry_class"] for row in classified).items())
        ),
        "retry_repository_counts": dict(
            sorted(Counter(row["repository_url"] for row in retry_rows).items())
        ),
        "retry_packaging_counts": dict(
            sorted(Counter(row["packaging"] for row in retry_rows).items())
        ),
        "top_retry_coordinates": [
            {"coordinate": coordinate, "slots": slots}
            for coordinate, slots in Counter(row["coordinate"] for row in retry_rows).most_common(25)
        ],
    }
    return {
        "summary": summary,
        "failed_slots": classified,
        "retry_config": retry_config,
    }


def classify_second_stage(row: dict[str, Any]) -> dict[str, Any]:
    group = row["group"]
    artifact = row["artifact"]
    original_packaging = row["packaging"]
    original_repository = row.get("repository_url") or MAVEN_CENTRAL
    packaging = opposite_packaging(original_packaging)
    repository_url = original_repository
    retry_class = "alternate-packaging"
    reason = "First retry did not download; try the opposite JAR/AAR packaging at the same repository."
    include = True

    if group.startswith("androidx."):
        repository_url = GOOGLE_MAVEN
        packaging = opposite_packaging(original_packaging)
        retry_class = "androidx-alternate-packaging"
        reason = "AndroidX source row failed as the first artifact type; retry against Google Maven with the opposite JAR/AAR packaging."
    elif group == "com.google.accompanist":
        repository_url = GOOGLE_MAVEN
        packaging = "aar"
        retry_class = "accompanist-google-aar"
        reason = "Accompanist Android UI artifacts are commonly AARs on Google Maven; the first pass used Maven Central JARs."
    elif group.startswith("org.jetbrains.compose") or group.startswith("org.jetbrains.androidx"):
        repository_url = JETBRAINS_COMPOSE
        packaging = "jar" if original_packaging == "aar" else original_packaging
        retry_class = "jetbrains-compose-repository"
        reason = "Compose Multiplatform rows may live in JetBrains Compose dev Maven rather than Maven Central."
    elif group.startswith("com.github."):
        repository_url = JITPACK
        packaging = opposite_packaging(original_packaging)
        retry_class = "jitpack-alternate-packaging"
        reason = "JitPack exact coordinate/tag failed as the first artifact type; retry only the opposite package type."
    elif group in {"org.apache.commons"} and artifact.endswith("-parent"):
        retry_class = "pom-parent-boundary"
        reason = "Parent POM coordinates do not provide bytecode to add to the reference DB."
        include = False
    elif group.startswith("com.facebook.react"):
        retry_class = "react-native-source-boundary"
        reason = "React Native Android artifacts often resolve from project-local/node module Maven repositories; do not guess a public coordinate."
        include = False
    elif group == "com.facebook.fresco" and artifact == "soloader":
        retry_class = "relocated-coordinate-boundary"
        reason = "The bytecode-bearing SoLoader coordinate is a different Maven group; keep this exact source row as an alias/boundary."
        include = False
    elif group.startswith("net.i2p"):
        retry_class = "special-repository-boundary"
        reason = "I2P rows likely require a project-specific repository; keep explicit boundary instead of guessing."
        include = False
    elif group.startswith("org.videolan"):
        retry_class = "special-repository-boundary"
        reason = "VideoLAN rows likely require an upstream-specific repository; keep explicit boundary instead of guessing."
        include = False

    return {
        **row,
        "packaging": packaging,
        "repository_url": repository_url,
        "retry_class": retry_class,
        "reason": reason,
        "original_packaging": original_packaging,
        "original_repository_url": original_repository,
        "included_in_retry_config": include,
    }


def load_config_slots(path: Path) -> list[dict[str, Any]]:
    config = read_json(path)
    rows = []
    for library in config.get("libraries", []):
        coordinate = f"{library['group']}:{library['artifact']}"
        for version in library.get("versions", []):
            rows.append(
                {
                    "coordinate": coordinate,
                    "group": library["group"],
                    "artifact": library["artifact"],
                    "version": version,
                    "packaging": library.get("packaging", "jar"),
                    "repository_url": library.get("repository_url") or MAVEN_CENTRAL,
                }
            )
    return rows


def load_artifact_metadata(root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    metadata = {}
    if not root.exists():
        return metadata
    for path in root.rglob("metadata.json"):
        record = read_json(path)
        coordinate = record.get("coordinate")
        version = record.get("version")
        if coordinate and version:
            metadata[(str(coordinate), str(version))] = record
    return metadata


def build_libraries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for row in rows:
        grouped[
            (
                row["group"],
                row["artifact"],
                row["repository_url"],
                row["packaging"],
            )
        ].append(row["version"])

    libraries = []
    for (group, artifact, repository_url, packaging), versions in sorted(grouped.items()):
        libraries.append(
            {
                "group": group,
                "artifact": artifact,
                "versions": sorted(set(versions), key=version_key),
                "packaging": packaging,
                "repository_url": repository_url,
                "notes": "Second-stage demo-final retry from first-stage failed slots; alternate packaging or repository only.",
            }
        )
    return libraries


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Demo Final Fixable Reference Retry Stage 2 Plan",
        "",
        "Generated by `scripts/build_demo_final_second_stage_reference_retry.py`.",
        "",
        "## Policy",
        "",
        "This second-stage retry only targets first-stage failed slots where an alternate artifact packaging or well-known repository switch is plausible. Rows that look like POM parents, relocated coordinates, React Native project-local artifacts, or special upstream repositories stay explicit boundaries.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Primary retry slots | {summary['primary_retry_slots']} |",
        f"| Primary downloaded slots | {summary['primary_downloaded_slots']} |",
        f"| Primary failed slots | {summary['primary_failed_slots']} |",
        f"| Stage 2 retry libraries | {summary['second_stage_retry_libraries']} |",
        f"| Stage 2 retry slots | {summary['second_stage_retry_slots']} |",
        "",
        "## Slot Classification",
        "",
        "| Class | Slots |",
        "|---|---:|",
    ]
    for key, value in summary["classification_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Retry Repositories", "", "| Repository | Slots |", "|---|---:|"])
    for key, value in summary["retry_repository_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Top Retry Coordinates", "", "| Coordinate | Slots |", "|---|---:|"])
    for row in summary["top_retry_coordinates"]:
        lines.append(f"| `{row['coordinate']}` | {row['slots']} |")
    lines.extend(["", f"- Retry config: `{summary['output_config']}`", ""])
    return "\n".join(lines)


def opposite_packaging(packaging: str) -> str:
    return "jar" if packaging == "aar" else "aar"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_path(path: Path) -> str:
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
