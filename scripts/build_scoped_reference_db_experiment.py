from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any

from build_large_combined_reference_db import (
    copy_child_rows,
    copy_component,
    db_counts,
    list_tables,
    normalize_path,
    quote_identifier,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Copy a base reference DB and append only explicitly selected "
            "coordinate-version rows from another reference DB."
        )
    )
    parser.add_argument("--base-db", required=True)
    parser.add_argument("--source-db", required=True)
    parser.add_argument("--output-db", required=True)
    parser.add_argument(
        "--include",
        action="append",
        required=True,
        metavar="GROUP:ARTIFACT:VERSION",
    )
    parser.add_argument("--output-json")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    base_db = Path(args.base_db)
    source_db = Path(args.source_db)
    output_db = Path(args.output_db)
    includes = [parse_component_spec(spec) for spec in args.include]

    if not base_db.exists():
        raise FileNotFoundError(base_db)
    if not source_db.exists():
        raise FileNotFoundError(source_db)
    if output_db.exists():
        if not args.force:
            raise FileExistsError(f"{output_db} exists; pass --force to rebuild")
        output_db.unlink()

    output_db.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(base_db, output_db)
    payload = append_selected_components(
        output_db=output_db,
        source_db=source_db,
        includes=includes,
    )
    payload["base_db"] = normalize_path(base_db)
    payload["output_db"] = normalize_path(output_db)
    payload["source_db"] = normalize_path(source_db)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        payload["output_json"] = normalize_path(output_json)

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def append_selected_components(
    *,
    output_db: Path,
    source_db: Path,
    includes: list[tuple[str, str]],
) -> dict[str, Any]:
    before = db_counts(output_db)
    inserted: list[dict[str, Any]] = []
    duplicates: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []

    with sqlite3.connect(output_db) as target:
        target.execute("PRAGMA foreign_keys = ON")
        target.execute("PRAGMA synchronous = OFF")
        target.execute("ATTACH DATABASE ? AS source", (str(source_db),))
        try:
            source_tables = set(list_tables(target, "source"))
            target_tables = set(list_tables(target, "main"))
            for coordinate, version in includes:
                existing = target.execute(
                    """
                    SELECT id FROM main.components
                    WHERE coordinate = ? AND version = ?
                    """,
                    (coordinate, version),
                ).fetchone()
                if existing:
                    duplicates.append(
                        {"coordinate": coordinate, "version": version}
                    )
                    continue

                source_row = target.execute(
                    """
                    SELECT id FROM source.components
                    WHERE coordinate = ? AND version = ?
                    """,
                    (coordinate, version),
                ).fetchone()
                if not source_row:
                    missing.append({"coordinate": coordinate, "version": version})
                    continue

                source_component_id = int(source_row[0])
                target_component_id = copy_component(
                    target,
                    "source",
                    source_component_id,
                )
                child_tables = sorted(
                    (source_tables & target_tables) - {"components"}
                )
                for table in child_tables:
                    copy_child_rows(
                        target,
                        "source",
                        table,
                        source_component_id,
                        target_component_id,
                    )
                inserted.append(
                    {
                        "coordinate": coordinate,
                        "version": version,
                        "source_component_id": source_component_id,
                        "target_component_id": target_component_id,
                    }
                )
            target.commit()
        finally:
            target.commit()
            target.execute(f"DETACH DATABASE {quote_identifier('source')}")

    return {
        "schema_version": 1,
        "requested": len(includes),
        "inserted": inserted,
        "duplicates": duplicates,
        "missing": missing,
        "before": before,
        "after": db_counts(output_db),
    }


def parse_component_spec(spec: str) -> tuple[str, str]:
    parts = spec.split(":")
    if len(parts) < 3:
        raise SystemExit(
            f"invalid component spec {spec!r}; expected GROUP:ARTIFACT:VERSION"
        )
    coordinate = ":".join(parts[:2])
    version = ":".join(parts[2:])
    if not coordinate or not version:
        raise SystemExit(
            f"invalid component spec {spec!r}; expected GROUP:ARTIFACT:VERSION"
        )
    return coordinate, version


if __name__ == "__main__":
    raise SystemExit(main())
