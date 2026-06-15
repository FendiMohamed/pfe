from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

from apk_sbom.reference_features import extract_reference_features_to_db, load_conversion_result


DEFAULT_MISSING_JSON = Path(
    "data/results/evaluation/source-observed-all-versions-missing-extraction-rows.json"
)
DEFAULT_DB_PATH = Path("data/reference_db/reference_features_source_observed_all_versions.sqlite")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extract only the source-observed all-versions conversion rows that are still "
            "missing from the DB. The missing list is generated from the conversion ledger "
            "and avoids reprocessing already-stored coordinate-version rows."
        )
    )
    parser.add_argument("--missing-json", default=str(DEFAULT_MISSING_JSON))
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--coordinate")
    parser.add_argument(
        "--exclude-coordinate",
        action="append",
        default=[],
        help="Coordinate to skip. May be supplied multiple times.",
    )
    parser.add_argument(
        "--max-dex-bytes",
        type=int,
        help="Only process rows whose converted DEX files total at most this many bytes.",
    )
    parser.add_argument(
        "--sort-by-dex-size",
        action="store_true",
        help="Process smaller converted DEX rows first.",
    )
    parser.add_argument("--quiet", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    missing_path = Path(args.missing_json)
    db_path = Path(args.db_path)
    payload = read_json(missing_path)
    rows = list(payload.get("missing_rows", []))
    rows = skip_currently_stored(rows, db_path)
    if args.coordinate:
        rows = [row for row in rows if row.get("coordinate") == args.coordinate]
    excluded = set(args.exclude_coordinate or [])
    if excluded:
        rows = [row for row in rows if row.get("coordinate") not in excluded]
    if args.max_dex_bytes is not None or args.sort_by_dex_size:
        rows = attach_dex_sizes(rows)
    if args.max_dex_bytes is not None:
        rows = [row for row in rows if int(row.get("dex_size", 0)) <= args.max_dex_bytes]
    if args.sort_by_dex_size:
        rows.sort(
            key=lambda row: (
                int(row.get("dex_size", 0)),
                str(row.get("coordinate")),
                str(row.get("version")),
            )
        )
    selected_rows = rows[args.offset :]
    if args.limit is not None:
        selected_rows = selected_rows[: args.limit]

    before = db_counts(db_path)
    conversions = [load_conversion_result(row["conversion"]) for row in selected_rows]
    summary = extract_reference_features_to_db(conversions, db_path=db_path, reset=False)
    after = db_counts(db_path)
    result_statuses = Counter(result.status for result in summary.results)
    result = {
        "db_path": normalize_path(db_path),
        "missing_json": normalize_path(missing_path),
        "coordinate_filter": args.coordinate or "",
        "offset": args.offset,
        "limit": args.limit,
        "available_rows_after_filter": len(rows),
        "selected_rows": len(selected_rows),
        "selected_dex_bytes": sum(int(row.get("dex_size", 0)) for row in selected_rows),
        "before": before,
        "after": after,
        "net_new_components": after["components"] - before["components"],
        "result_statuses": dict(sorted(result_statuses.items())),
        "failed_rows": [
            result.to_dict()
            for result in summary.results
            if result.status == "failed"
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["failed_rows"] else 0


def attach_dex_sizes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sized_rows = []
    for row in rows:
        conversion = read_json(Path(row["conversion"]))
        dex_size = sum(int(item.get("size", 0)) for item in conversion.get("dex_files", []))
        sized_rows.append({**row, "dex_size": dex_size})
    return sized_rows


def skip_currently_stored(rows: list[dict[str, Any]], db_path: Path) -> list[dict[str, Any]]:
    if not db_path.exists():
        return rows
    with sqlite3.connect(db_path) as conn:
        stored = set(conn.execute("select coordinate, version from components").fetchall())
    return [
        row
        for row in rows
        if (str(row.get("coordinate")), str(row.get("version"))) not in stored
    ]


def db_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"components": 0, "coordinates": 0}
    with sqlite3.connect(path) as conn:
        components = conn.execute("select count(*) from components").fetchone()[0]
        coordinates = conn.execute(
            "select count(distinct group_id || ':' || artifact_id) from components"
        ).fetchone()[0]
    return {"components": int(components), "coordinates": int(coordinates)}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Path) -> str:
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
