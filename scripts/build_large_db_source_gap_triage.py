from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_GAPS_CSV = Path(
    "data/results/evaluation/real-apk-large-combined-source-version-gaps.csv"
)
DEFAULT_ROWS_CSV = Path(
    "data/results/evaluation/real-apk-large-combined-source-version-rows.csv"
)
DEFAULT_REFERENCE_DB = Path("data/reference_db/reference_features_large_combined.sqlite")
DEFAULT_OUTPUT_JSON = Path(
    "data/results/evaluation/large-db-source-gap-triage.json"
)
DEFAULT_OUTPUT_CSV = Path(
    "data/results/evaluation/large-db-source-gap-triage.csv"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/LARGE_DB_SOURCE_GAP_TRIAGE.md"
)
DEFAULT_MISSING_CONFIG = Path(
    "configs/libraries.large_db_source_gap_missing_reference_candidates.json"
)

METADATA_ARTIFACT_TOKENS = (
    "bom",
    "platform",
    "gradle-plugin",
    "compiler",
    "compiler-hosted",
    "lint",
    "lint-checks",
    "lint-api",
    "lint-model",
    "annotation",
    "annotations",
    "jspecify",
    "error_prone_annotations",
    "checker-qual",
)
METADATA_COORDINATES = {
    "com.google.guava:listenablefuture",
    "org.jetbrains:annotations",
    "org.jspecify:jspecify",
}
COMMON_SOURCE_SUFFIXES = (
    "-common",
    "-metadata",
    "-wasm",
    "-js",
    "-linuxx64",
    "-macosx64",
    "-mingwx64",
)
JVM_FACADE_SUFFIXES = ("-jdk7", "-jdk8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Classify source-version constrained large-DB source-gap rows into "
            "honest action buckets for MVP/demo readiness."
        )
    )
    parser.add_argument("--gaps-csv", default=str(DEFAULT_GAPS_CSV))
    parser.add_argument("--rows-csv", default=str(DEFAULT_ROWS_CSV))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--missing-config", default=str(DEFAULT_MISSING_CONFIG))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    gaps = read_csv(Path(args.gaps_csv))
    emitted_rows = read_csv(Path(args.rows_csv))
    reference = load_reference_index(Path(args.reference_db))
    emitted_by_case = build_emitted_index(emitted_rows)
    classified = [
        classify_row(row, reference=reference, emitted_by_case=emitted_by_case)
        for row in gaps
    ]
    payload = build_payload(
        classified,
        gaps_csv=Path(args.gaps_csv),
        rows_csv=Path(args.rows_csv),
        reference_db=Path(args.reference_db),
    )
    write_csv(Path(args.output_csv), classified)
    write_json(Path(args.output_json), payload)
    write_json(
        Path(args.missing_config),
        {"libraries": build_missing_reference_config(classified)},
    )
    Path(args.output_doc).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_doc).write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(Path(args.output_doc)),
                "json": normalize_path(Path(args.output_json)),
                "csv": normalize_path(Path(args.output_csv)),
                "missing_config": normalize_path(Path(args.missing_config)),
                "total_rows": payload["summary"]["total_rows"],
                "actionable_rows": payload["summary"]["actionable_rows"],
                "explained_or_boundary_rows": payload["summary"]["explained_or_boundary_rows"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def classify_row(
    row: dict[str, str],
    *,
    reference: dict[str, set[str]],
    emitted_by_case: dict[str, dict[str, set[str]]],
) -> dict[str, Any]:
    coordinate = row["coordinate"]
    group, artifact = split_coordinate(coordinate)
    version = first_value(row.get("source_versions", ""))
    case_id = row.get("case_id", "")
    emitted = emitted_by_case.get(case_id, {})
    row_classification = row.get("classification", "")
    exact_in_large_db = row.get("exact_source_version_in_large_db", "").lower() == "true"

    target_alias = target_artifact_alias(coordinate, version, reference)
    emitted_alias = emitted_alias_for_case(coordinate, version, emitted)
    if is_project_module_coordinate(coordinate, version):
        bucket = "project-module-boundary"
        action = "document-project-module-boundary"
        reason = "The Gradle dependency row describes an internal project/module-style dependency, not a Maven artifact version to add to the reference DB."
    elif is_relocated_version_value(version):
        bucket = "relocated-coordinate-boundary"
        action = "map-relocated-source-coordinate-for-reporting"
        reason = "The resolved value is another Maven coordinate or module path, so this row is a Gradle relocation/alias boundary rather than a downloadable version."
        if not target_alias:
            target_alias = relocated_coordinate(version)
    elif is_metadata_coordinate(coordinate):
        bucket = "metadata-or-source-only-boundary"
        action = "document-no-apk-bytecode-expected"
        reason = "BOM, annotation, compiler, lint, or source-only helper coordinates are common in Gradle trees but normally do not contribute distinct APK runtime bytecode."
    elif target_alias:
        bucket = "target-artifact-alias-boundary"
        action = "map-source-coordinate-to-bytecode-target-for-reporting"
        reason = f"The source coordinate has a bytecode target alias in the large DB: {target_alias}."
    elif emitted_alias:
        bucket = "already-covered-by-emitted-sibling"
        action = "map-source-coordinate-to-emitted-sibling-for-reporting"
        reason = f"The APK already emitted a related sibling coordinate: {emitted_alias}."
    elif is_common_source_coordinate(group, artifact):
        bucket = "common-source-or-platform-boundary"
        action = "document-source-module-boundary"
        reason = "Common/platform source coordinates often resolve to JVM or Android target artifacts before APK packaging."
    elif row_classification == "source-coordinate-missing-from-large-db" or not exact_in_large_db:
        bucket = "missing-reference-candidate"
        action = "add-or-retry-reference-version-if-bytecode-bearing"
        reason = "The source coordinate/version is not exactly represented in the large DB after safe alias and metadata checks."
    else:
        bucket = "matcher-recall-candidate"
        action = "investigate-matcher-threshold-or-feature-recall"
        reason = "The exact coordinate/version exists in the large DB but was not emitted and no safe metadata/alias explanation matched."

    return {
        **row,
        "source_version": version,
        "triage_bucket": bucket,
        "next_action": action,
        "triage_reason": reason,
        "target_alias": target_alias,
        "emitted_alias": emitted_alias,
    }


def is_metadata_coordinate(coordinate: str) -> bool:
    if coordinate in METADATA_COORDINATES:
        return True
    _, artifact = split_coordinate(coordinate)
    normalized = artifact.lower()
    return any(token in normalized for token in METADATA_ARTIFACT_TOKENS)


def is_common_source_coordinate(group: str, artifact: str) -> bool:
    if artifact.endswith(COMMON_SOURCE_SUFFIXES):
        return True
    if artifact.endswith(JVM_FACADE_SUFFIXES):
        return True
    if group.startswith("org.jetbrains.kotlin") and artifact in {
        "kotlin-stdlib-common",
        "kotlin-stdlib-jdk7",
        "kotlin-stdlib-jdk8",
    }:
        return True
    return False


def is_relocated_version_value(version: str) -> bool:
    return ":" in version


def is_project_module_coordinate(coordinate: str, version: str) -> bool:
    group, _ = split_coordinate(coordinate)
    return group in {"feature", "shared", "app", "core", "library"} or version.endswith(":api")


def relocated_coordinate(version: str) -> str:
    parts = version.split(":")
    return ":".join(parts[:2]) if len(parts) >= 2 else ""


def target_artifact_alias(
    coordinate: str,
    version: str,
    reference: dict[str, set[str]],
) -> str:
    group, artifact = split_coordinate(coordinate)
    candidates = [
        f"{group}:{artifact}-android",
        f"{group}:{artifact}-jvm",
    ]
    if artifact.endswith("-ktx"):
        candidates.append(f"{group}:{artifact.removesuffix('-ktx')}")
    if artifact.endswith("-core"):
        candidates.append(f"{group}:{artifact}-jvm")
    for candidate in candidates:
        if version and version in reference.get(candidate, set()):
            return candidate
    return ""


def emitted_alias_for_case(
    coordinate: str,
    version: str,
    emitted: dict[str, set[str]],
) -> str:
    group, artifact = split_coordinate(coordinate)
    candidates = [
        f"{group}:{artifact}-android",
        f"{group}:{artifact}-jvm",
    ]
    if artifact.endswith("-ktx"):
        candidates.append(f"{group}:{artifact.removesuffix('-ktx')}")
    if artifact.endswith("-common"):
        candidates.append(f"{group}:{artifact.removesuffix('-common')}")
    for candidate in candidates:
        versions = emitted.get(candidate, set())
        if version in versions or versions:
            return candidate
    return ""


def build_payload(
    rows: list[dict[str, Any]],
    *,
    gaps_csv: Path,
    rows_csv: Path,
    reference_db: Path,
) -> dict[str, Any]:
    bucket_counts = Counter(row["triage_bucket"] for row in rows)
    action_counts = Counter(row["next_action"] for row in rows)
    classification_counts = Counter(row["classification"] for row in rows)
    actionable_buckets = {"missing-reference-candidate", "matcher-recall-candidate"}
    actionable_rows = sum(count for bucket, count in bucket_counts.items() if bucket in actionable_buckets)
    summary = {
        "total_rows": len(rows),
        "actionable_rows": actionable_rows,
        "explained_or_boundary_rows": len(rows) - actionable_rows,
        "triage_bucket_counts": dict(sorted(bucket_counts.items())),
        "next_action_counts": dict(sorted(action_counts.items())),
        "source_gap_input_counts": dict(sorted(classification_counts.items())),
    }
    return {
        "schema_version": 1,
        "sources": {
            "gaps_csv": normalize_path(gaps_csv),
            "emitted_rows_csv": normalize_path(rows_csv),
            "reference_db": normalize_path(reference_db),
        },
        "policy": (
            "This triage does not claim every Gradle source dependency should be "
            "emitted as an APK SBOM component. It separates likely metadata/source "
            "boundaries and source-to-bytecode artifact aliases from rows that "
            "need reference growth or matcher recall work."
        ),
        "summary": summary,
        "top_coordinates_by_bucket": top_coordinates_by_bucket(rows),
        "top_cases_by_actionable_rows": top_cases_by_actionable_rows(rows),
        "missing_reference_config_libraries": len(build_missing_reference_config(rows)),
        "missing_reference_config_slots": sum(
            len(item["versions"]) for item in build_missing_reference_config(rows)
        ),
        "rows": rows,
    }


def build_missing_reference_config(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    for row in rows:
        if row["triage_bucket"] != "missing-reference-candidate":
            continue
        group, artifact = split_coordinate(row["coordinate"])
        version = str(row.get("source_version") or "")
        if not group or not artifact or not version:
            continue
        if is_relocated_version_value(version) or is_project_module_coordinate(row["coordinate"], version):
            continue
        packaging = default_packaging(group, artifact)
        repository_url = default_repository_url(group)
        grouped[(group, artifact, packaging, repository_url)].add(version)
    libraries = [
        {
            "group": group,
            "artifact": artifact,
            "packaging": packaging,
            "repository_url": repository_url,
            "versions": sorted(versions, key=version_sort_key),
        }
        for (group, artifact, packaging, repository_url), versions in grouped.items()
    ]
    libraries.sort(key=lambda item: (item["repository_url"], item["group"], item["artifact"]))
    return libraries


def default_packaging(group: str, artifact: str) -> str:
    if group.startswith("androidx.") or group.startswith("com.android.support"):
        return "aar"
    if group.startswith("com.google.android.material"):
        return "aar"
    if group.startswith("com.google.android.gms") or group.startswith("com.google.firebase"):
        return "aar"
    if artifact.endswith("-android") or artifact.endswith("-ktx") or artifact.startswith("material"):
        return "aar"
    return "jar"


def default_repository_url(group: str) -> str:
    if (
        group.startswith("androidx.")
        or group.startswith("com.android.support")
        or group.startswith("com.google.android.")
        or group.startswith("com.google.firebase")
    ):
        return "https://dl.google.com/dl/android/maven2"
    return "https://repo1.maven.org/maven2"


def version_sort_key(version: str) -> tuple[tuple[int, Any], ...]:
    parts: list[tuple[int, Any]] = []
    token = ""
    for char in version:
        if char.isdigit():
            if token and not token[-1].isdigit():
                parts.append((1, token))
                token = ""
            token += char
        else:
            if token and token[-1].isdigit():
                parts.append((0, int(token)))
                token = ""
            token += char
    if token:
        parts.append((0, int(token)) if token.isdigit() else (1, token))
    return tuple(parts)


def top_coordinates_by_bucket(rows: list[dict[str, Any]], limit: int = 20) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[row["triage_bucket"]][row["coordinate"]] += 1
    return {
        bucket: [
            {"coordinate": coordinate, "rows": count}
            for coordinate, count in counter.most_common(limit)
        ]
        for bucket, counter in sorted(grouped.items())
    }


def top_cases_by_actionable_rows(rows: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
    actionable = {"missing-reference-candidate", "matcher-recall-candidate"}
    counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        if row["triage_bucket"] in actionable:
            counts[(row.get("case_id", ""), row.get("app", ""))] += 1
    return [
        {"case_id": case_id, "app": app, "rows": count}
        for (case_id, app), count in counts.most_common(limit)
    ]


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Large DB Source Gap Triage",
        "",
        "Generated by `scripts/build_large_db_source_gap_triage.py`.",
        "",
        "## Policy",
        "",
        payload["policy"],
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Total source-gap rows | {summary['total_rows']} |",
        f"| Explained/boundary rows | {summary['explained_or_boundary_rows']} |",
        f"| Actionable rows | {summary['actionable_rows']} |",
        f"| Missing-reference config libraries | {payload['missing_reference_config_libraries']} |",
        f"| Missing-reference config slots | {payload['missing_reference_config_slots']} |",
        "",
        "## Triage Buckets",
        "",
        "| Bucket | Rows |",
        "|---|---:|",
    ]
    for bucket, count in summary["triage_bucket_counts"].items():
        lines.append(f"| `{bucket}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
            "| Action | Rows |",
            "|---|---:|",
        ]
    )
    for action, count in summary["next_action_counts"].items():
        lines.append(f"| `{action}` | {count} |")
    lines.extend(
        [
            "",
            "## Top Actionable Cases",
            "",
            "| Case | App | Rows |",
            "|---|---|---:|",
        ]
    )
    for row in payload["top_cases_by_actionable_rows"]:
        lines.append(f"| `{row['case_id']}` | {escape_md(row['app'])} | {row['rows']} |")
    lines.extend(
        [
            "",
            "## Top Coordinates By Bucket",
            "",
        ]
    )
    for bucket, bucket_rows in payload["top_coordinates_by_bucket"].items():
        lines.extend(
            [
                f"### {bucket}",
                "",
                "| Coordinate | Rows |",
                "|---|---:|",
            ]
        )
        for row in bucket_rows:
            lines.append(f"| `{row['coordinate']}` | {row['rows']} |")
        lines.append("")
    return "\n".join(lines)


def load_reference_index(path: Path) -> dict[str, set[str]]:
    with sqlite3.connect(path) as connection:
        rows = connection.execute("SELECT coordinate, version FROM components").fetchall()
    output: dict[str, set[str]] = defaultdict(set)
    for coordinate, version in rows:
        output[str(coordinate)].add(str(version))
    return output


def build_emitted_index(rows: list[dict[str, str]]) -> dict[str, dict[str, set[str]]]:
    output: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in rows:
        case_id = row.get("case_id", "")
        coordinate = row.get("coordinate", "")
        version = row.get("detected_version", "")
        if case_id and coordinate and version:
            output[case_id][coordinate].add(version)
    return output


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def split_coordinate(coordinate: str) -> tuple[str, str]:
    group, _, artifact = coordinate.partition(":")
    return group, artifact


def first_value(value: str) -> str:
    return value.split(";")[0] if value else ""


def normalize_path(path: Path) -> str:
    return path.as_posix()


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
