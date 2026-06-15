from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_source_observed_failed_download_retry_plan import version_key


DEFAULT_TRIAGE_CSV = Path("data/results/evaluation/demo-final-large-source-gap-triage.csv")
DEFAULT_SOURCE_CONFIG = Path(
    "configs/libraries.demo_final_large_remaining_missing_reference_candidates.json"
)
DEFAULT_REFERENCE_DB = Path("data/reference_db/reference_features_demo_final_large.sqlite")
DEFAULT_ARTIFACT_ROOT = Path("data/reference_db/artifacts_large_db_source_gap_missing")
DEFAULT_DEX_ROOT = Path("data/reference_db/dex_large_db_source_gap_missing")
DEFAULT_OUTPUT_CONFIG = Path("configs/libraries.demo_final_fixable_missing_reference_retry.json")
DEFAULT_OUTPUT_JSON = Path(
    "data/results/evaluation/demo-final-fixable-reference-retry-plan.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_RETRY_PLAN.md")

JITPACK = "https://jitpack.io"
GOOGLE_MAVEN = "https://dl.google.com/dl/android/maven2"

PSEUDO_GROUPS = {"legacy", "mail", "net", "plugins"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a small retry config from demo-final missing-reference gaps, "
            "excluding already-proven no-bytecode/source-boundary rows."
        )
    )
    parser.add_argument("--triage-csv", default=str(DEFAULT_TRIAGE_CSV))
    parser.add_argument("--source-config", default=str(DEFAULT_SOURCE_CONFIG))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    parser.add_argument("--dex-root", default=str(DEFAULT_DEX_ROOT))
    parser.add_argument("--output-config", default=str(DEFAULT_OUTPUT_CONFIG))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_retry_plan(
        triage_csv=Path(args.triage_csv),
        source_config=Path(args.source_config),
        reference_db=Path(args.reference_db),
        artifact_root=Path(args.artifact_root),
        dex_root=Path(args.dex_root),
        output_config=Path(args.output_config),
    )
    write_json(Path(args.output_json), payload)
    write_json(Path(args.output_config), payload["retry_config"])
    Path(args.output_doc).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_doc).write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


def build_retry_plan(
    *,
    triage_csv: Path,
    source_config: Path,
    reference_db: Path,
    artifact_root: Path,
    dex_root: Path,
    output_config: Path,
) -> dict[str, Any]:
    triage_rows = read_csv(triage_csv)
    missing_rows = [
        row for row in triage_rows if row.get("triage_bucket") == "missing-reference-candidate"
    ]
    slot_rows = rows_by_slot(missing_rows)
    db_slots = load_db_slots(reference_db)
    source_slots = load_source_slots(source_config)
    artifact_metadata = load_artifact_metadata(artifact_root)
    conversion_metadata = load_conversion_metadata(dex_root)

    classified = []
    retry_rows = []
    for slot, rows in sorted(slot_rows.items()):
        coordinate, version = slot
        group, artifact = coordinate.split(":", maxsplit=1)
        source = source_slots.get(slot, {})
        conversion = conversion_metadata.get(slot)
        artifact_record = artifact_metadata.get(slot)
        row_count = len(rows)
        case_ids = sorted({row.get("case_id", "") for row in rows if row.get("case_id")})

        retry_class = "fixable-retry"
        reason = "No previous artifact metadata exists; retry the source-observed coordinate/version."
        repository_url = source.get("repository_url")
        packaging = source.get("packaging") or "jar"
        include = True

        if slot in db_slots:
            retry_class = "already-in-demo-final-db"
            reason = "The exact coordinate/version already exists in the demo-final DB."
            include = False
        elif conversion and conversion.get("status") == "skipped":
            retry_class = "proven-no-bytecode"
            reason = conversion.get("error") or "Previous conversion produced no dex/classes."
            include = False
        elif conversion and conversion.get("status") == "converted":
            retry_class = "converted-not-in-demo-final-db"
            reason = "A previous conversion succeeded but the component is not present in the selected DB."
            include = True
        elif artifact_record and not conversion:
            retry_class = "downloaded-needs-conversion"
            reason = "Artifact metadata exists but no conversion metadata was found."
            include = True
        elif group in PSEUDO_GROUPS or "." not in group:
            retry_class = "source-pseudo-coordinate-boundary"
            reason = "The group looks like a Gradle/module pseudo-coordinate rather than a public Maven group."
            include = False
        elif group.startswith("com.github."):
            retry_class = "jitpack-repository-fix"
            reason = "GitHub-style Maven coordinates often resolve through JitPack, not Maven Central."
            repository_url = JITPACK
            include = True
        elif group.startswith("androidx.") and repository_url != GOOGLE_MAVEN:
            retry_class = "google-maven-repository-fix"
            reason = "AndroidX coordinates should be retried through Google Maven."
            repository_url = GOOGLE_MAVEN
            include = True
        elif group.startswith("org.jetbrains.compose") or group.startswith("org.jetbrains.androidx"):
            retry_class = "jetbrains-compose-central-retry"
            reason = "No previous artifact metadata exists; keep the source catalog repository for a bounded retry."
            include = True

        item = {
            "coordinate": coordinate,
            "group": group,
            "artifact": artifact,
            "version": version,
            "row_count": row_count,
            "case_count": len(case_ids),
            "case_ids": case_ids,
            "packaging": packaging,
            "repository_url": repository_url,
            "retry_class": retry_class,
            "reason": reason,
            "previous_artifact_metadata": bool(artifact_record),
            "previous_conversion_status": (conversion or {}).get("status", ""),
            "previous_conversion_error": (conversion or {}).get("error", ""),
            "included_in_retry_config": include,
        }
        classified.append(item)
        if include:
            retry_rows.append(item)

    retry_libraries = build_libraries(retry_rows)
    summary = {
        "triage_csv": normalize_path(triage_csv),
        "source_config": normalize_path(source_config),
        "reference_db": normalize_path(reference_db),
        "artifact_root": normalize_path(artifact_root),
        "dex_root": normalize_path(dex_root),
        "output_config": normalize_path(output_config),
        "missing_reference_rows": len(missing_rows),
        "missing_reference_slots": len(slot_rows),
        "retry_slots": sum(len(library["versions"]) for library in retry_libraries),
        "retry_libraries": len(retry_libraries),
        "retry_rows_covered": sum(row["row_count"] for row in retry_rows),
        "classification_counts": dict(
            sorted(Counter(row["retry_class"] for row in classified).items())
        ),
        "retry_packaging_counts": dict(
            sorted(Counter(row["packaging"] for row in retry_rows).items())
        ),
        "retry_repository_counts": dict(
            sorted(Counter(row.get("repository_url") or "default" for row in retry_rows).items())
        ),
        "top_retry_coordinates": [
            {"coordinate": coordinate, "rows": rows, "slots": slots}
            for coordinate, rows, slots in top_coordinates(retry_rows)[:25]
        ],
    }
    return {
        "summary": summary,
        "slots": classified,
        "retry_config": {"libraries": retry_libraries},
    }


def rows_by_slot(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        version = row.get("source_version") or first_value(row.get("source_versions", ""))
        if not row.get("coordinate") or not version:
            continue
        grouped[(row["coordinate"], version)].append(row)
    return grouped


def load_db_slots(path: Path) -> set[tuple[str, str]]:
    if not path.exists():
        return set()
    with sqlite3.connect(path) as connection:
        return {
            (str(coordinate), str(version))
            for coordinate, version in connection.execute(
                "SELECT coordinate, version FROM components"
            )
        }


def load_source_slots(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    config = read_json(path)
    slots = {}
    for library in config.get("libraries", []):
        coordinate = f"{library['group']}:{library['artifact']}"
        for version in library.get("versions", []):
            slots[(coordinate, version)] = library
    return slots


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


def load_conversion_metadata(root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    metadata = {}
    if not root.exists():
        return metadata
    for path in root.rglob("conversion.json"):
        record = read_json(path)
        coordinate = record.get("coordinate")
        version = record.get("version")
        if coordinate and version:
            metadata[(str(coordinate), str(version))] = record
    return metadata


def build_libraries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[
            (
                row["group"],
                row["artifact"],
                row.get("repository_url") or "",
                row.get("packaging") or "jar",
            )
        ].append(row)

    libraries = []
    for (group, artifact, repository_url, packaging), grouped_rows in sorted(
        grouped.items(),
        key=lambda item: (
            -sum(row["row_count"] for row in item[1]),
            item[0][0],
            item[0][1],
        ),
    ):
        library: dict[str, Any] = {
            "group": group,
            "artifact": artifact,
            "versions": sorted({row["version"] for row in grouped_rows}, key=version_key),
            "packaging": packaging,
            "notes": "Demo-final fixable missing-reference retry; excludes proven no-bytecode rows.",
        }
        if repository_url:
            library["repository_url"] = repository_url
        libraries.append(library)
    return libraries


def top_coordinates(rows: list[dict[str, Any]]) -> list[tuple[str, int, int]]:
    row_counts: Counter[str] = Counter()
    slot_counts: Counter[str] = Counter()
    for row in rows:
        row_counts[row["coordinate"]] += row["row_count"]
        slot_counts[row["coordinate"]] += 1
    return sorted(
        ((coordinate, rows, slot_counts[coordinate]) for coordinate, rows in row_counts.items()),
        key=lambda item: (-item[1], -item[2], item[0]),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Demo Final Fixable Reference Retry Plan",
        "",
        "Generated by `scripts/build_demo_final_fixable_reference_retry.py`.",
        "",
        "## Policy",
        "",
        "This plan grows the reference DB only from rows that can plausibly add bytecode-backed components. Rows already proven to contain no dex/classes are documented as boundaries instead of being forced into the DB.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Missing-reference rows | {summary['missing_reference_rows']} |",
        f"| Missing-reference exact slots | {summary['missing_reference_slots']} |",
        f"| Retry config libraries | {summary['retry_libraries']} |",
        f"| Retry config slots | {summary['retry_slots']} |",
        f"| Source-gap rows covered by retry slots | {summary['retry_rows_covered']} |",
        "",
        "## Slot Classification",
        "",
        "| Class | Slots |",
        "|---|---:|",
    ]
    for key, value in summary["classification_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Retry Repositories",
            "",
            "| Repository | Slots |",
            "|---|---:|",
        ]
    )
    for key, value in summary["retry_repository_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Top Retry Coordinates",
            "",
            "| Coordinate | Rows | Slots |",
            "|---|---:|---:|",
        ]
    )
    for row in summary["top_retry_coordinates"]:
        lines.append(f"| `{row['coordinate']}` | {row['rows']} | {row['slots']} |")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Retry config: `{summary['output_config']}`",
            f"- Source triage CSV: `{summary['triage_csv']}`",
            f"- Reference DB baseline: `{summary['reference_db']}`",
            "",
        ]
    )
    return "\n".join(lines)


def first_value(value: str) -> str:
    return value.split(";")[0].strip() if value else ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
