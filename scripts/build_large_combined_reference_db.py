from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any


DEFAULT_BASE_DB = Path("data/reference_db/reference_features_source_observed_all_versions.sqlite")
DEFAULT_OUTPUT_DB = Path("data/reference_db/reference_features_large_combined.sqlite")
DEFAULT_SOURCE_DBS = [
    Path("data/reference_db/reference_features_real_apk_priority_versions.sqlite"),
    Path("data/reference_db/reference_features_source_observed_versions.sqlite"),
    Path("data/reference_db/reference_features_calibrated_combined.sqlite"),
]
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/large-combined-reference-db-build.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a large evaluation-only reference DB by copying the all-versions DB "
            "as a base and appending unique coordinate-version rows from other DBs."
        )
    )
    parser.add_argument("--base-db", default=str(DEFAULT_BASE_DB))
    parser.add_argument("--output-db", default=str(DEFAULT_OUTPUT_DB))
    parser.add_argument("--source-db", action="append", default=[str(path) for path in DEFAULT_SOURCE_DBS])
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    base_db = Path(args.base_db)
    output_db = Path(args.output_db)
    source_dbs = [Path(path) for path in args.source_db]
    output_json = Path(args.output_json)

    if not base_db.exists():
        raise FileNotFoundError(base_db)
    if output_db.exists():
        if not args.force:
            raise FileExistsError(f"{output_db} exists; pass --force to rebuild")
        output_db.unlink()

    output_db.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(base_db, output_db)

    payload: dict[str, Any] = {
        "schema_version": 1,
        "base_db": normalize_path(base_db),
        "output_db": normalize_path(output_db),
        "before": db_counts(output_db),
        "sources": [],
    }

    with sqlite3.connect(output_db) as target:
        target.execute("PRAGMA foreign_keys = ON")
        target.execute("PRAGMA synchronous = OFF")
        target.execute("PRAGMA temp_store = MEMORY")
        for index, source_db in enumerate(source_dbs):
            payload["sources"].append(append_source_db(target, source_db, alias=f"src{index}"))
        target.commit()

    payload["after"] = db_counts(output_db)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def append_source_db(target: sqlite3.Connection, source_db: Path, *, alias: str) -> dict[str, Any]:
    if not source_db.exists():
        return {
            "source_db": normalize_path(source_db),
            "missing": True,
            "inserted_components": 0,
        }

    before = db_counts_from_connection(target)
    target.execute(f"ATTACH DATABASE ? AS {quote_identifier(alias)}", (str(source_db),))
    try:
        source_tables = set(list_tables(target, alias))
        target_tables = set(list_tables(target, "main"))
        target_keys = set(
            target.execute("SELECT coordinate, version FROM main.components").fetchall()
        )
        source_components = target.execute(
            f"SELECT id, coordinate, version FROM {quote_identifier(alias)}.components ORDER BY coordinate, version"
        ).fetchall()
        inserted = 0
        skipped_duplicates = 0
        for source_component_id, coordinate, version in source_components:
            if (coordinate, version) in target_keys:
                skipped_duplicates += 1
                continue
            new_component_id = copy_component(target, alias, int(source_component_id))
            target_keys.add((coordinate, version))
            inserted += 1
            for table in sorted((source_tables & target_tables) - {"components"}):
                copy_child_rows(target, alias, table, int(source_component_id), new_component_id)
        after = db_counts_from_connection(target)
    finally:
        target.commit()
        target.execute(f"DETACH DATABASE {quote_identifier(alias)}")

    return {
        "source_db": normalize_path(source_db),
        "missing": False,
        "before": before,
        "after": after,
        "source_components": len(source_components),
        "inserted_components": inserted,
        "skipped_duplicate_components": skipped_duplicates,
    }


def copy_component(target: sqlite3.Connection, alias: str, source_component_id: int) -> int:
    columns = [
        row[1]
        for row in target.execute(f"PRAGMA {quote_identifier(alias)}.table_info(components)").fetchall()
        if row[1] != "id"
    ]
    column_sql = ", ".join(quote_identifier(column) for column in columns)
    target.execute(
        f"""
        INSERT INTO main.components ({column_sql})
        SELECT {column_sql}
        FROM {quote_identifier(alias)}.components
        WHERE id = ?
        """,
        (source_component_id,),
    )
    return int(target.execute("SELECT last_insert_rowid()").fetchone()[0])


def copy_child_rows(
    target: sqlite3.Connection,
    alias: str,
    table: str,
    source_component_id: int,
    target_component_id: int,
) -> None:
    source_columns = [
        row[1]
        for row in target.execute(f"PRAGMA {quote_identifier(alias)}.table_info({quote_identifier(table)})").fetchall()
    ]
    target_columns = [
        row[1]
        for row in target.execute(f"PRAGMA main.table_info({quote_identifier(table)})").fetchall()
    ]
    if "component_id" not in source_columns or "component_id" not in target_columns:
        return
    common_columns = [
        column
        for column in target_columns
        if column in source_columns and column not in {"id", "component_id"}
    ]
    insert_columns = ["component_id", *common_columns]
    select_columns = ["?", *[quote_identifier(column) for column in common_columns]]
    target.execute(
        f"""
        INSERT INTO main.{quote_identifier(table)} ({", ".join(quote_identifier(column) for column in insert_columns)})
        SELECT {", ".join(select_columns)}
        FROM {quote_identifier(alias)}.{quote_identifier(table)}
        WHERE component_id = ?
        """,
        (target_component_id, source_component_id),
    )


def list_tables(connection: sqlite3.Connection, schema: str) -> list[str]:
    return [
        row[0]
        for row in connection.execute(
            f"SELECT name FROM {quote_identifier(schema)}.sqlite_master WHERE type = 'table'"
        ).fetchall()
    ]


def db_counts(path: Path) -> dict[str, int]:
    with sqlite3.connect(path) as connection:
        return db_counts_from_connection(connection)


def db_counts_from_connection(connection: sqlite3.Connection) -> dict[str, int]:
    components = connection.execute("SELECT COUNT(*) FROM main.components").fetchone()[0]
    coordinates = connection.execute(
        "SELECT COUNT(DISTINCT group_id || ':' || artifact_id) FROM main.components"
    ).fetchone()[0]
    return {"components": int(components), "coordinates": int(coordinates)}


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def normalize_path(path: Path) -> str:
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
