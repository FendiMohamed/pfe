from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_COVERAGE_JSON = Path("data/results/evaluation/reference-db-coverage-first-dashboard.json")
DEFAULT_POPULAR_CATALOG = Path("configs/popular_android_maven_catalog.json")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/source-observed-reference-catalog.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/SOURCE_OBSERVED_REFERENCE_CATALOG.md")
DEFAULT_OUTPUT_CSV = Path("data/results/evaluation/source-observed-reference-catalog.csv")
DEFAULT_OUTPUT_CATALOG = Path("configs/source_observed_reference_catalog.json")
DEFAULT_OUTPUT_SOURCE_VERSIONS_CONFIG = Path("configs/libraries.source_observed_versions.json")

GOOGLE_MAVEN_URL = "https://dl.google.com/dl/android/maven2"
MAVEN_CENTRAL_URL = "https://repo1.maven.org/maven2"

GOOGLE_MAVEN_GROUP_PREFIXES = (
    "androidx.",
    "com.android.",
    "com.google.android.",
    "com.google.firebase",
    "com.google.mlkit",
    "com.google.accompanist",
)

ANDROIDX_JAR_GROUPS = {
    "androidx.annotation",
    "androidx.arch.core",
    "androidx.collection",
}

ANDROIDX_JAR_ARTIFACTS = {
    "lifecycle-common",
    "lifecycle-common-java8",
    "paging-common",
    "room-common",
}

METADATA_ONLY_MARKERS = (
    "-bom",
    "_bom",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate source-observed reference catalog/config artifacts from the "
            "coverage-first dashboard."
        ),
    )
    parser.add_argument("--coverage-json", default=str(DEFAULT_COVERAGE_JSON))
    parser.add_argument("--popular-catalog", default=str(DEFAULT_POPULAR_CATALOG))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-catalog", default=str(DEFAULT_OUTPUT_CATALOG))
    parser.add_argument(
        "--output-source-versions-config",
        default=str(DEFAULT_OUTPUT_SOURCE_VERSIONS_CONFIG),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    coverage_path = Path(args.coverage_json)
    popular_catalog_path = Path(args.popular_catalog)
    payload = build_payload(
        read_json(coverage_path),
        popular_catalog=read_catalog_if_exists(popular_catalog_path),
        coverage_path=coverage_path,
        popular_catalog_path=popular_catalog_path,
    )

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    write_catalog(Path(args.output_catalog), payload["buildable_catalog_entries"])
    write_source_versions_config(
        Path(args.output_source_versions_config),
        payload["buildable_catalog_entries"],
    )
    write_csv(Path(args.output_csv), payload["entries"])

    print(
        json.dumps(
            {
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "csv": normalize_path(Path(args.output_csv)),
                "catalog": normalize_path(Path(args.output_catalog)),
                "source_versions_config": normalize_path(Path(args.output_source_versions_config)),
                "source_observed_coordinates": payload["summary"]["source_observed_coordinates"],
                "buildable_coordinates": payload["summary"]["buildable_coordinates"],
                "source_version_slots": payload["summary"]["source_version_slots"],
                "buildable_source_version_slots": payload["summary"][
                    "buildable_source_version_slots"
                ],
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    coverage: dict[str, Any],
    *,
    popular_catalog: dict[str, dict[str, Any]],
    coverage_path: Path,
    popular_catalog_path: Path,
) -> dict[str, Any]:
    source_row_counts = source_row_counts_by_coordinate(coverage)
    gap_counts = gap_counts_by_coordinate(coverage.get("gap_rows", []))
    entries = [
        build_entry(row, popular_catalog, source_row_counts, gap_counts)
        for row in coverage.get("observed_source_catalog", [])
    ]
    entries.sort(key=lambda item: (-item["source_row_count"], item["coordinate"]))
    buildable_entries = [entry for entry in entries if entry["buildable"]]
    skipped_entries = [entry for entry in entries if not entry["buildable"]]
    summary = build_summary(coverage, entries, buildable_entries, skipped_entries)
    return {
        "schema_version": 1,
        "sources": {
            "coverage_dashboard": normalize_path(coverage_path),
            "popular_catalog": normalize_path(popular_catalog_path),
        },
        "verdict": "source-observed-reference-catalog-ready",
        "summary": summary,
        "top_missing_coordinates": top_entries(
            [entry for entry in entries if not entry["coordinate_in_reference_db"]],
        ),
        "top_missing_versions_for_known_coordinates": top_entries(
            [
                entry
                for entry in entries
                if entry["coordinate_in_reference_db"]
                and entry["source_versions_missing_from_reference_db"]
            ],
        ),
        "skipped_non_bytecode_entries": skipped_entries,
        "entries": entries,
        "buildable_catalog_entries": buildable_entries,
    }


def build_entry(
    row: dict[str, Any],
    popular_catalog: dict[str, dict[str, Any]],
    source_row_counts: dict[str, int],
    gap_counts: dict[str, Counter[str]],
) -> dict[str, Any]:
    coordinate = str(row["coordinate"])
    group, artifact = coordinate.split(":", maxsplit=1)
    known = popular_catalog.get(coordinate, {})
    packaging = str(known.get("packaging") or infer_packaging(group, artifact))
    repository_url = known.get("repository_url") or infer_repository_url(group)
    category = str(known.get("category") or infer_category(group, artifact))
    source_versions = sorted(str(version) for version in row.get("source_versions", []))
    reference_versions = sorted(str(version) for version in row.get("reference_versions", []))
    source_missing_reference = [
        version for version in source_versions if version not in set(reference_versions)
    ]
    buildable, skip_reason = classify_buildable(group, artifact, packaging)
    gap_counter = gap_counts.get(coordinate, Counter())
    return {
        "coordinate": coordinate,
        "group": group,
        "artifact": artifact,
        "packaging": packaging,
        "category": category,
        "repository_url": repository_url,
        "source_versions": source_versions,
        "source_version_count": len(source_versions),
        "case_count": int(row.get("case_count", 0)),
        "source_row_count": source_row_counts.get(coordinate, 0),
        "roles": sorted(str(role) for role in row.get("roles", [])),
        "coordinate_in_reference_db": bool(row.get("coordinate_in_reference_db")),
        "reference_versions": reference_versions,
        "reference_version_count": len(reference_versions),
        "source_versions_missing_from_reference_db": source_missing_reference,
        "source_version_missing_count": len(source_missing_reference),
        "gap_counts": dict(sorted(gap_counter.items())),
        "known_in_popular_catalog": bool(known),
        "buildable": buildable,
        "skip_reason": skip_reason,
        "notes": build_notes(row, known, source_missing_reference, buildable, skip_reason),
    }


def source_row_counts_by_coordinate(coverage: dict[str, Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for case in coverage.get("cases", []):
        for row in case.get("source_rows", []):
            counts[str(row["coordinate"])] += 1
    return dict(counts)


def gap_counts_by_coordinate(rows: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[str(row["coordinate"])][str(row["gap_class"])] += 1
    return grouped


def build_summary(
    coverage: dict[str, Any],
    entries: list[dict[str, Any]],
    buildable_entries: list[dict[str, Any]],
    skipped_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    source_version_slots = sum(len(entry["source_versions"]) for entry in entries)
    buildable_source_version_slots = sum(
        len(entry["source_versions"]) for entry in buildable_entries
    )
    coordinate_gap_count = sum(1 for entry in entries if not entry["coordinate_in_reference_db"])
    version_gap_count = sum(
        1
        for entry in entries
        if entry["coordinate_in_reference_db"]
        and entry["source_versions_missing_from_reference_db"]
    )
    packaging_counts = Counter(entry["packaging"] for entry in entries)
    category_counts = Counter(entry["category"] for entry in entries)
    repository_counts = Counter(entry["repository_url"] or MAVEN_CENTRAL_URL for entry in entries)
    skip_counts = Counter(entry["skip_reason"] for entry in skipped_entries)
    return {
        "source_observed_coordinates": len(entries),
        "source_observed_rows": (coverage.get("summary") or {}).get("source_dependency_pairs"),
        "source_version_slots": source_version_slots,
        "buildable_coordinates": len(buildable_entries),
        "buildable_source_version_slots": buildable_source_version_slots,
        "skipped_non_bytecode_coordinates": len(skipped_entries),
        "coordinate_absent_from_reference_db": coordinate_gap_count,
        "known_coordinate_with_missing_source_versions": version_gap_count,
        "known_in_popular_catalog": sum(1 for entry in entries if entry["known_in_popular_catalog"]),
        "new_to_popular_catalog": sum(1 for entry in entries if not entry["known_in_popular_catalog"]),
        "packaging_counts": dict(sorted(packaging_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "repository_counts": dict(sorted(repository_counts.items())),
        "skip_reason_counts": dict(sorted(skip_counts.items())),
        "shared_db_coordinate_coverage_percent": (coverage.get("summary") or {}).get(
            "reference_coordinate_coverage_percent"
        ),
        "shared_db_exact_version_coverage_percent": (coverage.get("summary") or {}).get(
            "reference_exact_version_coverage_percent"
        ),
        "end_to_end_exact_source_recall_percent": (coverage.get("summary") or {}).get(
            "end_to_end_exact_source_recall_percent"
        ),
    }


def infer_repository_url(group: str) -> str | None:
    if group.startswith(GOOGLE_MAVEN_GROUP_PREFIXES):
        return GOOGLE_MAVEN_URL
    return None


def infer_packaging(group: str, artifact: str) -> str:
    if is_metadata_only_artifact(group, artifact):
        return "jar"
    if group in ANDROIDX_JAR_GROUPS:
        return "jar"
    if group.startswith("androidx.") and artifact in ANDROIDX_JAR_ARTIFACTS:
        return "jar"
    if group.startswith("androidx."):
        return "aar"
    if group == "com.google.android.material":
        return "aar"
    if group.startswith(("com.google.android.", "com.google.firebase", "com.google.mlkit")):
        return "aar"
    return "jar"


def infer_category(group: str, artifact: str) -> str:
    if is_metadata_only_artifact(group, artifact):
        return "metadata-only"
    if group.startswith("androidx.compose"):
        return "compose"
    if group.startswith("androidx.lifecycle"):
        return "androidx-lifecycle"
    if group.startswith("androidx."):
        return "androidx"
    if group.startswith(("org.jetbrains.kotlin", "org.jetbrains.kotlinx")):
        return "kotlin"
    if group.startswith("com.squareup.okhttp3") or group.startswith("com.squareup.okio"):
        return "networking"
    if group.startswith("com.fasterxml.jackson") or group.startswith("com.google.code.gson"):
        return "serialization"
    if group.startswith("com.google.firebase"):
        return "firebase"
    if group.startswith("com.google.android.gms"):
        return "google-play-services"
    return "source-observed"


def classify_buildable(group: str, artifact: str, packaging: str) -> tuple[bool, str]:
    if is_metadata_only_artifact(group, artifact):
        return False, "metadata-only-bom"
    if packaging not in {"jar", "aar"}:
        return False, f"unsupported-packaging-{packaging}"
    return True, ""


def is_metadata_only_artifact(group: str, artifact: str) -> bool:
    lowered = artifact.lower()
    return lowered == "bom" or any(lowered.endswith(marker) for marker in METADATA_ONLY_MARKERS)


def build_notes(
    row: dict[str, Any],
    known: dict[str, Any],
    source_missing_reference: list[str],
    buildable: bool,
    skip_reason: str,
) -> str:
    pieces = [
        f"source cases={row.get('case_count', 0)}",
        f"source versions={', '.join(str(version) for version in row.get('source_versions', []))}",
    ]
    if source_missing_reference:
        pieces.append(f"missing from shared DB={', '.join(source_missing_reference)}")
    if known.get("notes"):
        pieces.append(f"popular catalog note={known['notes']}")
    if not buildable:
        pieces.append(f"not in bytecode build config={skip_reason}")
    return "; ".join(pieces)


def top_entries(entries: list[dict[str, Any]], *, limit: int = 25) -> list[dict[str, Any]]:
    return [
        {
            "coordinate": entry["coordinate"],
            "source_row_count": entry["source_row_count"],
            "case_count": entry["case_count"],
            "source_versions": entry["source_versions"],
            "source_versions_missing_from_reference_db": entry[
                "source_versions_missing_from_reference_db"
            ],
            "packaging": entry["packaging"],
            "repository_url": entry["repository_url"],
            "buildable": entry["buildable"],
            "skip_reason": entry["skip_reason"],
        }
        for entry in sorted(entries, key=lambda item: (-item["source_row_count"], item["coordinate"]))[
            :limit
        ]
    ]


def write_catalog(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "libraries": [
            catalog_entry(entry)
            for entry in sorted(entries, key=lambda item: item["coordinate"])
        ]
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def catalog_entry(entry: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "group": entry["group"],
        "artifact": entry["artifact"],
        "packaging": entry["packaging"],
        "category": entry["category"],
        "notes": entry["notes"],
    }
    if entry["repository_url"]:
        payload["repository_url"] = entry["repository_url"]
    return payload


def write_source_versions_config(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "libraries": [
            source_version_config_entry(entry)
            for entry in sorted(entries, key=lambda item: item["coordinate"])
        ]
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_version_config_entry(entry: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "group": entry["group"],
        "artifact": entry["artifact"],
        "packaging": entry["packaging"],
        "versions": entry["source_versions"],
    }
    if entry["repository_url"]:
        payload["repository_url"] = entry["repository_url"]
    return payload


def write_csv(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "coordinate",
        "group",
        "artifact",
        "packaging",
        "category",
        "repository_url",
        "source_row_count",
        "case_count",
        "source_versions",
        "source_version_count",
        "coordinate_in_reference_db",
        "reference_versions",
        "source_versions_missing_from_reference_db",
        "source_version_missing_count",
        "known_in_popular_catalog",
        "buildable",
        "skip_reason",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in sorted(entries, key=lambda item: (-item["source_row_count"], item["coordinate"])):
            writer.writerow({field: csv_value(entry.get(field, "")) for field in fieldnames})


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Source-Observed Reference Catalog",
        "",
        "Generated by `scripts/build_source_observed_reference_catalog.py`.",
        "",
        "This artifact starts the actual missing-TPL/missing-version lane. It converts the coverage-first source denominator into reference DB build inputs, without changing the shared calibrated DB.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Source-observed coordinates | {summary['source_observed_coordinates']} |",
        f"| Source-observed coordinate+version slots | {summary['source_version_slots']} |",
        f"| Buildable coordinates | {summary['buildable_coordinates']} |",
        f"| Buildable source-version slots | {summary['buildable_source_version_slots']} |",
        f"| Skipped non-bytecode coordinates | {summary['skipped_non_bytecode_coordinates']} |",
        f"| Coordinates absent from shared DB | {summary['coordinate_absent_from_reference_db']} |",
        f"| Known coordinates with missing source versions | {summary['known_coordinate_with_missing_source_versions']} |",
        f"| Existing popular-catalog coordinates reused | {summary['known_in_popular_catalog']} |",
        f"| New coordinates added to source-observed catalog | {summary['new_to_popular_catalog']} |",
        f"| Current shared DB coordinate coverage | {summary['shared_db_coordinate_coverage_percent']}% |",
        f"| Current shared DB exact-version coverage | {summary['shared_db_exact_version_coverage_percent']}% |",
        f"| Current end-to-end exact source recall | {summary['end_to_end_exact_source_recall_percent']}% |",
        "",
        "## Generated Files",
        "",
        "| File | Purpose |",
        "|---|---|",
        "| `configs/source_observed_reference_catalog.json` | Buildable source-observed coordinate catalog for metadata expansion. Use it with `expand-reference-config --all-versions`. |",
        "| `configs/libraries.source_observed_versions.json` | Downloader-compatible config pinned to versions already observed in source trees. This is the first batch-build input. |",
        "| `docs/evaluation/SOURCE_OBSERVED_REFERENCE_DB_BATCH_LOG.md` | Evaluation-only DB batch progress log for download, DEX conversion, and feature extraction. |",
        "| `data/results/evaluation/source-observed-reference-catalog.json` | Full machine-readable catalog, including skipped metadata-only entries and gap counts. |",
        "| `data/results/evaluation/source-observed-reference-catalog.csv` | Flat catalog for filtering and dashboard work. |",
        "",
        "## How To Use This Honestly",
        "",
        "1. Build `configs/libraries.source_observed_versions.json` into an evaluation-only DB first. This adds the versions we already know are used by the source-validated APKs.",
        "2. Expand `configs/source_observed_reference_catalog.json` with `apk-sbom expand-reference-config --all-versions` to enumerate every metadata-published version for these TPLs.",
        "3. Build that all-version config in batches as a broad evaluation-only DB. Record download, conversion, and no-bytecode skips instead of hiding them.",
        "4. Rerun the coverage-first dashboard and source-validation comparison against the broad DB before changing the shared calibrated DB.",
        "",
        "Recommended metadata-expansion command:",
        "",
        "```powershell",
        "docker compose run --rm apk-sbom python -m apk_sbom.cli expand-reference-config --catalog configs/source_observed_reference_catalog.json --output configs/libraries.source_observed_all_versions.json --all-versions --include-prerelease --summary-output data/results/evaluation/source-observed-all-versions-expansion-summary.json",
        "```",
        "",
        "Recommended first source-version build batch:",
        "",
        "```powershell",
        "docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven --config configs/libraries.source_observed_versions.json --output-root data/reference_db/artifacts_source_observed_versions --limit 25 --offset 0 --quiet",
        "docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex --artifact-root data/reference_db/artifacts_source_observed_versions --output-root data/reference_db/dex_source_observed_versions --limit 25 --offset 0 --quiet",
        "docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features --dex-root data/reference_db/dex_source_observed_versions --db-path data/reference_db/reference_features_source_observed_versions.sqlite --reset --quiet",
        "```",
        "",
        "For later batches, increase the download/convert offset and omit `--reset` after the first feature extraction.",
        "",
        "## Top Coordinates Missing Entirely From The Shared DB",
        "",
    ]
    lines.extend(top_table(payload["top_missing_coordinates"]))
    lines.extend(
        [
            "",
            "## Top Known Coordinates Missing Source Versions",
            "",
        ]
    )
    lines.extend(top_table(payload["top_missing_versions_for_known_coordinates"]))
    lines.extend(
        [
            "",
            "## Non-Bytecode / Metadata-Only Skips",
            "",
        ]
    )
    if payload["skipped_non_bytecode_entries"]:
        lines.extend(
            [
                "| Coordinate | Source versions | Reason |",
                "|---|---|---|",
            ]
        )
        for entry in payload["skipped_non_bytecode_entries"][:25]:
            lines.append(
                f"| `{escape_cell(entry['coordinate'])}` | "
                f"{escape_cell(', '.join(entry['source_versions']))} | "
                f"{escape_cell(entry['skip_reason'])} |"
            )
    else:
        lines.append("No metadata-only coordinates were skipped.")
    lines.append("")
    return "\n".join(lines)


def top_table(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No rows.", ""]
    lines = [
        "| Coordinate | Source rows | Cases | Source versions | Packaging | Buildable | Repository / skip |",
        "|---|---:|---:|---|---|---|---|",
    ]
    for row in rows:
        repository_or_skip = row["repository_url"] or MAVEN_CENTRAL_URL
        if not row["buildable"]:
            repository_or_skip = row["skip_reason"]
        lines.append(
            f"| `{escape_cell(row['coordinate'])}` | {row['source_row_count']} | "
            f"{row['case_count']} | {escape_cell(', '.join(row['source_versions'][:8]))} | "
            f"{row['packaging']} | {row['buildable']} | {escape_cell(repository_or_skip)} |"
        )
    return lines


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_catalog_if_exists(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = read_json(path)
    output = {}
    for entry in payload.get("libraries", []):
        coordinate = f"{entry.get('group')}:{entry.get('artifact')}"
        output[coordinate] = entry
    return output


def normalize_path(value: str | Path | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\\", "/")


def csv_value(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)


def escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
