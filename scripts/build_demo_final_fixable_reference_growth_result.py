from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_TRIAGE_CSV = Path("data/results/evaluation/demo-final-large-source-gap-triage.csv")
DEFAULT_RETRY_CONFIGS = [
    Path("configs/libraries.demo_final_fixable_missing_reference_retry.json"),
    Path("configs/libraries.demo_final_fixable_missing_reference_retry_stage2.json"),
]
DEFAULT_BASE_DB = Path("data/reference_db/reference_features_demo_final_large.sqlite")
DEFAULT_V2_DB = Path("data/reference_db/reference_features_demo_final_large_v2.sqlite")
DEFAULT_ARTIFACT_ROOTS = [
    Path("data/reference_db/artifacts_demo_final_fixable_retry"),
    Path("data/reference_db/artifacts_demo_final_fixable_retry_stage2"),
]
DEFAULT_DEX_ROOTS = [
    Path("data/reference_db/dex_demo_final_fixable_retry"),
    Path("data/reference_db/dex_demo_final_fixable_retry_stage2"),
]
DEFAULT_OUTPUT_JSON = Path(
    "data/results/evaluation/demo-final-fixable-reference-growth-result.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_GROWTH_RESULT.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize the demo-final fixable reference retry DB-growth result."
    )
    parser.add_argument("--triage-csv", default=str(DEFAULT_TRIAGE_CSV))
    parser.add_argument(
        "--retry-config",
        action="append",
        dest="retry_configs",
        help="Retry config to include. May be supplied more than once.",
    )
    parser.add_argument("--base-db", default=str(DEFAULT_BASE_DB))
    parser.add_argument("--v2-db", default=str(DEFAULT_V2_DB))
    parser.add_argument(
        "--artifact-root",
        action="append",
        dest="artifact_roots",
        help="Artifact root to include. May be supplied more than once.",
    )
    parser.add_argument(
        "--dex-root",
        action="append",
        dest="dex_roots",
        help="Dex root to include. May be supplied more than once.",
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_result(
        triage_csv=Path(args.triage_csv),
        retry_configs=paths_or_defaults(args.retry_configs, DEFAULT_RETRY_CONFIGS),
        base_db=Path(args.base_db),
        v2_db=Path(args.v2_db),
        artifact_roots=paths_or_defaults(args.artifact_roots, DEFAULT_ARTIFACT_ROOTS),
        dex_roots=paths_or_defaults(args.dex_roots, DEFAULT_DEX_ROOTS),
    )
    write_json(Path(args.output_json), payload)
    Path(args.output_doc).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_doc).write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


def build_result(
    *,
    triage_csv: Path,
    retry_configs: list[Path],
    base_db: Path,
    v2_db: Path,
    artifact_roots: list[Path],
    dex_roots: list[Path],
) -> dict[str, Any]:
    retry_slots = load_config_slots(retry_configs)
    downloaded = load_artifact_metadata(artifact_roots)
    conversions = load_conversion_metadata(dex_roots)
    base_components, base_slots = load_db_slots(base_db)
    v2_components, v2_slots = load_db_slots(v2_db)
    new_slots = sorted(v2_slots - base_slots)
    new_components = load_component_details(v2_db, new_slots)
    gap_rows = load_missing_gap_rows(triage_csv)
    gap_rows_by_slot = Counter((row["coordinate"], row["source_version"]) for row in gap_rows)
    downloaded_slots = set(downloaded)
    stored_slots = set(new_slots)
    failed_slots = sorted(set(retry_slots) - downloaded_slots)
    no_bytecode_slots = {
        slot for slot, record in conversions.items() if record.get("status") == "skipped"
    }
    converted_slots = {
        slot for slot, record in conversions.items() if record.get("status") == "converted"
    }

    summary = {
        "triage_csv": normalize_path(triage_csv),
        "retry_configs": [normalize_path(path) for path in retry_configs if path.exists()],
        "base_db": normalize_path(base_db),
        "v2_db": normalize_path(v2_db),
        "artifact_roots": [normalize_path(path) for path in artifact_roots if path.exists()],
        "dex_roots": [normalize_path(path) for path in dex_roots if path.exists()],
        "retry_slots": len(retry_slots),
        "downloaded_slots": len(downloaded),
        "download_failed_or_unavailable_slots": len(failed_slots),
        "downloaded_no_bytecode_slots": len(no_bytecode_slots & set(retry_slots)),
        "converted_slots": len(converted_slots),
        "stored_new_slots": len(new_slots),
        "base_components": base_components,
        "v2_components": v2_components,
        "component_growth": v2_components - base_components,
        "source_gap_rows_now_reference_covered": sum(
            gap_rows_by_slot[slot] for slot in stored_slots
        ),
        "source_gap_rows_attempted_but_unavailable": sum(
            gap_rows_by_slot[slot] for slot in failed_slots
        ),
        "source_gap_rows_downloaded_no_bytecode": sum(
            gap_rows_by_slot[slot] for slot in no_bytecode_slots
        ),
        "new_slot_coordinate_counts": dict(
            sorted(Counter(coordinate for coordinate, _ in new_slots).items())
        ),
        "failed_coordinate_counts": dict(
            sorted(Counter(coordinate for coordinate, _ in failed_slots).items())
        ),
    }
    return {
        "summary": summary,
        "new_components": new_components,
        "downloaded_slots": [
            {"coordinate": coordinate, "version": version}
            for coordinate, version in sorted(downloaded_slots)
        ],
        "failed_or_unavailable_slots": [
            {"coordinate": coordinate, "version": version}
            for coordinate, version in failed_slots
        ],
    }


def load_config_slots(paths: list[Path]) -> set[tuple[str, str]]:
    slots = set()
    for path in paths:
        if not path.exists():
            continue
        config = read_json(path)
        for library in config.get("libraries", []):
            coordinate = f"{library['group']}:{library['artifact']}"
            for version in library.get("versions", []):
                slots.add((coordinate, version))
    return slots


def load_artifact_metadata(roots: list[Path]) -> dict[tuple[str, str], dict[str, Any]]:
    metadata = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("metadata.json"):
            record = read_json(path)
            coordinate = record.get("coordinate")
            version = record.get("version")
            if coordinate and version:
                metadata[(str(coordinate), str(version))] = record
    return metadata


def load_conversion_metadata(roots: list[Path]) -> dict[tuple[str, str], dict[str, Any]]:
    metadata = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("conversion.json"):
            record = read_json(path)
            coordinate = record.get("coordinate")
            version = record.get("version")
            if coordinate and version:
                metadata[(str(coordinate), str(version))] = record
    return metadata


def load_db_slots(path: Path) -> tuple[int, set[tuple[str, str]]]:
    with sqlite3.connect(path) as connection:
        rows = list(connection.execute("SELECT coordinate, version FROM components"))
    return len(rows), {(str(coordinate), str(version)) for coordinate, version in rows}


def load_component_details(path: Path, slots: list[tuple[str, str]]) -> list[dict[str, Any]]:
    if not slots:
        return []
    with sqlite3.connect(path) as connection:
        details = []
        for coordinate, version in slots:
            row = connection.execute(
                """
                SELECT coordinate, version, packaging, classes_count, methods_count, artifact_path
                FROM components
                WHERE coordinate = ? AND version = ?
                """,
                (coordinate, version),
            ).fetchone()
            if row:
                details.append(
                    {
                        "coordinate": row[0],
                        "version": row[1],
                        "packaging": row[2],
                        "classes_count": row[3],
                        "methods_count": row[4],
                        "artifact_path": row[5],
                    }
                )
    return details


def load_missing_gap_rows(path: Path) -> list[dict[str, str]]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("triage_bucket") != "missing-reference-candidate":
                continue
            version = row.get("source_version") or first_value(row.get("source_versions", ""))
            if not row.get("coordinate") or not version:
                continue
            rows.append({**row, "source_version": version})
    return rows


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Demo Final Fixable Reference Growth Result",
        "",
        "Generated by `scripts/build_demo_final_fixable_reference_growth_result.py`.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Retry slots attempted | {summary['retry_slots']} |",
        f"| Downloaded slots | {summary['downloaded_slots']} |",
        f"| Download failed/unavailable slots | {summary['download_failed_or_unavailable_slots']} |",
        f"| Downloaded no-bytecode slots | {summary['downloaded_no_bytecode_slots']} |",
        f"| Converted slots | {summary['converted_slots']} |",
        f"| Stored new slots | {summary['stored_new_slots']} |",
        f"| Base DB components | {summary['base_components']} |",
        f"| V2 DB components | {summary['v2_components']} |",
        f"| Component growth | {summary['component_growth']} |",
        f"| Source-gap rows now reference-covered | {summary['source_gap_rows_now_reference_covered']} |",
        f"| Source-gap rows attempted but unavailable | {summary['source_gap_rows_attempted_but_unavailable']} |",
        f"| Source-gap rows downloaded but no-bytecode | {summary['source_gap_rows_downloaded_no_bytecode']} |",
        "",
        "## New Components",
        "",
        "| Coordinate | Version | Classes | Methods |",
        "|---|---|---:|---:|",
    ]
    for row in payload["new_components"]:
        lines.append(
            f"| `{row['coordinate']}` | `{row['version']}` | {row['classes_count']} | {row['methods_count']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The unavailable slots were attempted through the generated retry configs and did not download from the configured public repositories. Downloaded no-bytecode slots are now explicit source-wrapper/no-bytecode boundaries. Neither group is a silent omission.",
            "",
            "## Outputs",
            "",
            f"- V2 DB: `{summary['v2_db']}`",
            "- Retry configs:",
            *[f"  - `{path}`" for path in summary["retry_configs"]],
            "- Artifact roots:",
            *[f"  - `{path}`" for path in summary["artifact_roots"]],
            "- Dex roots:",
            *[f"  - `{path}`" for path in summary["dex_roots"]],
            "",
        ]
    )
    return "\n".join(lines)


def first_value(value: str) -> str:
    return value.split(";")[0].strip() if value else ""


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_path(path: Path) -> str:
    return path.as_posix()


def paths_or_defaults(values: list[str] | None, defaults: list[Path]) -> list[Path]:
    if values:
        return [Path(value) for value in values]
    return defaults


if __name__ == "__main__":
    raise SystemExit(main())
