from __future__ import annotations

import argparse
import json
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


DEFAULT_PLAN = Path(
    "data/results/evaluation/real-apk-priority-failed-download-retry-plan.json"
)
DEFAULT_TARGET_DB = Path(
    "data/reference_db/reference_features_real_apk_priority_versions.sqlite"
)
DEFAULT_SOURCE_DB = Path(
    "data/reference_db/reference_features_demo_final_large_v2.sqlite"
)
DEFAULT_OUTPUT = Path(
    "data/results/evaluation/real-apk-priority-existing-db-recovery.json"
)
DEFAULT_RETRY_ARTIFACT_ROOTS = (
    Path("data/reference_db/artifacts_real_apk_priority_failed_retry_alt_packaging"),
    Path("data/reference_db/artifacts_real_apk_priority_failed_retry_default_aar"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Recover still-unrecovered real-APK priority coordinate-version rows "
            "from an existing evaluation feature DB."
        )
    )
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--target-db", default=str(DEFAULT_TARGET_DB))
    parser.add_argument("--source-db", default=str(DEFAULT_SOURCE_DB))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = recover(
        plan_path=Path(args.plan),
        target_db=Path(args.target_db),
        source_db=Path(args.source_db),
    )
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def recover(
    *,
    plan_path: Path,
    target_db: Path,
    source_db: Path,
) -> dict[str, Any]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    retry_downloaded = set()
    for root in DEFAULT_RETRY_ARTIFACT_ROOTS:
        retry_downloaded.update(downloaded_keys(root))

    still_unrecovered = [
        row
        for row in plan["failed_downloads"]
        if (row["group"], row["artifact"], row["version"]) not in retry_downloaded
    ]
    wanted = {
        (str(row["coordinate"]), str(row["version"])): row
        for row in still_unrecovered
    }
    before = db_counts(target_db)
    inserted: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []

    with sqlite3.connect(target_db) as target:
        target.execute("PRAGMA foreign_keys = ON")
        target.execute("PRAGMA synchronous = OFF")
        target.execute("PRAGMA temp_store = MEMORY")
        target.execute("ATTACH DATABASE ? AS source", (str(source_db),))
        try:
            source_tables = set(list_tables(target, "source"))
            target_tables = set(list_tables(target, "main"))
            for (coordinate, version), evidence in sorted(
                wanted.items(),
                key=lambda item: (
                    -int(item[1].get("apk_support_count", 0)),
                    -int(item[1].get("occurrence_count", 0)),
                    item[0],
                ),
            ):
                if target.execute(
                    """
                    SELECT 1 FROM main.components
                    WHERE coordinate = ? AND version = ?
                    """,
                    (coordinate, version),
                ).fetchone():
                    continue
                source_row = target.execute(
                    """
                    SELECT id FROM source.components
                    WHERE coordinate = ? AND version = ?
                    """,
                    (coordinate, version),
                ).fetchone()
                if not source_row:
                    unavailable.append(
                        {
                            "coordinate": coordinate,
                            "version": version,
                            "apk_support_count": evidence.get("apk_support_count", 0),
                            "occurrence_count": evidence.get("occurrence_count", 0),
                            "retry_class": evidence.get("retry_class"),
                        }
                    )
                    continue
                source_component_id = int(source_row[0])
                target_component_id = copy_component(
                    target,
                    "source",
                    source_component_id,
                )
                for table in sorted(
                    (source_tables & target_tables) - {"components"}
                ):
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
                        "apk_support_count": evidence.get("apk_support_count", 0),
                        "occurrence_count": evidence.get("occurrence_count", 0),
                        "retry_class": evidence.get("retry_class"),
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
        "plan": normalize_path(plan_path),
        "target_db": normalize_path(target_db),
        "source_db": normalize_path(source_db),
        "still_unrecovered_before_local_recovery": len(still_unrecovered),
        "inserted_count": len(inserted),
        "inserted": inserted,
        "not_available_in_source_db_count": len(unavailable),
        "not_available_in_source_db": unavailable,
        "before": before,
        "after": db_counts(target_db),
    }


def downloaded_keys(root: Path) -> set[tuple[str, str, str]]:
    keys: set[tuple[str, str, str]] = set()
    if not root.exists():
        return keys
    for path in root.rglob("metadata.json"):
        try:
            metadata = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        group = metadata.get("group")
        artifact = metadata.get("artifact")
        version = metadata.get("version")
        if group and artifact and version:
            keys.add((str(group), str(artifact), str(version)))
    return keys


if __name__ == "__main__":
    raise SystemExit(main())
