from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from pathlib import Path


COMPONENT_TABLES = (
    "api_references",
    "class_dependencies",
    "classes",
    "dependency_shapes",
    "dex_files",
    "maven_dependencies",
    "methods",
    "opcode_ngrams",
    "opcodes",
    "packages",
    "string_literals",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy a reference-feature SQLite DB and drop exact component versions.",
    )
    parser.add_argument("--source-db", required=True)
    parser.add_argument("--output-db", required=True)
    parser.add_argument(
        "--drop",
        action="append",
        default=[],
        metavar="GROUP:ARTIFACT:VERSION",
        help="Exact component version to remove. Can be repeated.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_db = Path(args.source_db)
    output_db = Path(args.output_db)
    if not source_db.exists():
        raise SystemExit(f"source DB not found: {source_db}")

    output_db.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_db, output_db)

    drop_specs = [parse_drop_spec(spec) for spec in args.drop]
    dropped = filter_db(output_db, drop_specs)
    print(
        json.dumps(
            {
                "source_db": str(source_db),
                "output_db": str(output_db),
                "requested_drops": len(drop_specs),
                "dropped_components": dropped,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def parse_drop_spec(spec: str) -> tuple[str, str, str]:
    parts = spec.split(":")
    if len(parts) != 3 or not all(parts):
        raise SystemExit(f"invalid drop spec {spec!r}; expected GROUP:ARTIFACT:VERSION")
    return parts[0], parts[1], parts[2]


def filter_db(db_path: Path, drop_specs: list[tuple[str, str, str]]) -> int:
    with sqlite3.connect(db_path) as connection:
        component_ids = find_component_ids(connection, drop_specs)
        if not component_ids:
            return 0
        placeholders = ",".join("?" for _ in component_ids)
        for table in COMPONENT_TABLES:
            if table_exists(connection, table):
                connection.execute(
                    f"DELETE FROM {table} WHERE component_id IN ({placeholders})",
                    component_ids,
                )
        connection.execute(
            f"DELETE FROM components WHERE id IN ({placeholders})",
            component_ids,
        )
        connection.commit()
        connection.execute("VACUUM")
        return len(component_ids)


def find_component_ids(
    connection: sqlite3.Connection,
    drop_specs: list[tuple[str, str, str]],
) -> list[int]:
    ids: list[int] = []
    for group_id, artifact_id, version in drop_specs:
        rows = connection.execute(
            """
            SELECT id
            FROM components
            WHERE group_id = ? AND artifact_id = ? AND version = ?
            """,
            (group_id, artifact_id, version),
        ).fetchall()
        ids.extend(int(row[0]) for row in rows)
    return sorted(set(ids))


def table_exists(connection: sqlite3.Connection, table: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


if __name__ == "__main__":
    raise SystemExit(main())
