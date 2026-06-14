from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apk_sbom.report import generate_final_report
from apk_sbom.source_validation import (
    parse_gradle_dependency_tree,
    write_source_validation_report,
)


DEFAULT_SOURCE_DASHBOARD_JSON = Path(
    "data/results/evaluation/real-apk-source-validation-dashboard.json"
)
DEFAULT_REFERENCE_DB = Path("data/reference_db/reference_features_large_combined.sqlite")
DEFAULT_OUTPUT_ROOT = Path(
    "data/results/experiments/real-apk-large-combined-source-version"
)
DEFAULT_OUTPUT_DASHBOARD_JSON = Path(
    "data/results/evaluation/real-apk-large-combined-source-version-dashboard.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/LARGE_COMBINED_SOURCE_VERSION_EVALUATION.md"
)
DEFAULT_OUTPUT_ROWS_CSV = Path(
    "data/results/evaluation/real-apk-large-combined-source-version-rows.csv"
)
DEFAULT_OUTPUT_GAPS_CSV = Path(
    "data/results/evaluation/real-apk-large-combined-source-version-gaps.csv"
)


@dataclass(frozen=True)
class SourceCoordinateSlice:
    db_path: Path
    source_coordinates: int
    kept_coordinates: int
    kept_components: int
    missing_source_coordinates: list[str]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluation-only rerun for the large combined reference DB. For each "
            "source-validated APK, build a temporary reference DB slice containing "
            "all large-DB versions for coordinates present in that APK's resolved "
            "Gradle dependency tree, then run the normal report/source-validation "
            "pipeline against the slice."
        )
    )
    parser.add_argument("--source-dashboard-json", default=str(DEFAULT_SOURCE_DASHBOARD_JSON))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--output-dashboard-json", default=str(DEFAULT_OUTPUT_DASHBOARD_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--output-rows-csv", default=str(DEFAULT_OUTPUT_ROWS_CSV))
    parser.add_argument("--output-gaps-csv", default=str(DEFAULT_OUTPUT_GAPS_CSV))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--force-slices", action="store_true")
    parser.add_argument(
        "--slice-mode",
        choices=("source-version", "source-coordinate"),
        default="source-version",
        help=(
            "source-version keeps only exact versions from the resolved source tree "
            "(upper-bound coverage run). source-coordinate keeps every large-DB "
            "version for source coordinates (version-selection oracle, slower)."
        ),
    )
    parser.add_argument("--min-score", type=float, default=0.05)
    parser.add_argument("--query-osv", action="store_true")
    parser.add_argument("--enrich-vulnerabilities", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_dashboard_path = Path(args.source_dashboard_json)
    reference_db = Path(args.reference_db)
    output_root = Path(args.output_root)
    output_dashboard_path = Path(args.output_dashboard_json)
    output_doc = Path(args.output_doc)
    output_rows_csv = Path(args.output_rows_csv)
    output_gaps_csv = Path(args.output_gaps_csv)

    dashboard = read_json(source_dashboard_path)
    cases = runnable_cases(dashboard)
    selected = cases[args.offset :]
    if args.limit is not None:
        selected = selected[: args.limit]

    results = []
    for case in selected:
        results.append(
            run_case(
                case,
                output_root=output_root,
                reference_db=reference_db,
                force=args.force,
                force_slices=args.force_slices,
                min_score=args.min_score,
                query_osv=args.query_osv,
                enrich_vulnerabilities=args.enrich_vulnerabilities,
                slice_mode=args.slice_mode,
            )
        )

    updated_dashboard = build_dashboard(
        source_dashboard=dashboard,
        output_root=output_root,
        reference_db=reference_db,
        output_dashboard_json=output_dashboard_path,
        output_rows_csv=output_rows_csv,
        output_gaps_csv=output_gaps_csv,
        slice_mode=args.slice_mode,
    )
    output_dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    output_dashboard_path.write_text(
        json.dumps(updated_dashboard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(updated_dashboard), encoding="utf-8")

    print(
        json.dumps(
            {
                "evaluation_mode": evaluation_mode(args.slice_mode),
                "source_dashboard_json": normalize_path(source_dashboard_path),
                "output_dashboard_json": normalize_path(output_dashboard_path),
                "output_doc": normalize_path(output_doc),
                "output_root": normalize_path(output_root),
                "reference_db": normalize_path(reference_db),
                "runnable_cases": len(cases),
                "selected_cases": len(selected),
                "completed_cases": updated_dashboard["summary"]["completed_cases"],
                "results": results,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def runnable_cases(dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    cases = []
    for case in dashboard.get("cases", []):
        report_path = ((case.get("paths") or {}).get("report")) or ""
        dependency_tree_path = ((case.get("validation_stats") or {}).get("dependency_tree_path")) or ""
        old_report = read_json_if_exists(report_path)
        apk_path = (((old_report or {}).get("apk") or {}).get("apk_path")) or ""
        if apk_path and dependency_tree_path and Path(apk_path).exists() and Path(dependency_tree_path).exists():
            cases.append(case)
    return cases


def run_case(
    case: dict[str, Any],
    *,
    output_root: Path,
    reference_db: Path,
    force: bool,
    force_slices: bool,
    min_score: float,
    query_osv: bool,
    enrich_vulnerabilities: bool,
    slice_mode: str,
) -> dict[str, Any]:
    case_id = str(case["case_id"])
    old_report = read_json((case.get("paths") or {})["report"])
    apk_path = Path(old_report["apk"]["apk_path"])
    dependency_tree_path = Path((case.get("validation_stats") or {})["dependency_tree_path"])
    report_dir = output_root / f"report-real-{case_id}"
    validation_dir = output_root / "source-validation" / case_id
    slice_db = output_root / "reference-dbs" / f"{case_id}.sqlite"
    report_json = report_dir / "report.json"
    validation_json = validation_dir / "source-validation.json"

    source_dependencies = parse_gradle_dependency_tree(
        dependency_tree_path.read_text(encoding="utf-8")
    )
    source_coordinates = sorted(source_dependencies)
    slice_info = build_source_coordinate_slice(
        source_db=reference_db,
        output_db=slice_db,
        source_coordinates=source_coordinates,
        source_versions_by_coordinate={
            coordinate: entry.resolved_versions
            for coordinate, entry in source_dependencies.items()
        },
        slice_mode=slice_mode,
        force=force_slices or force,
    )

    if force or not report_json.exists():
        generate_final_report(
            apk_path,
            output_dir=report_dir,
            db_path=slice_db,
            min_score=min_score,
            enable_reference_package_prefilter=False,
            query_osv=query_osv,
            enrich_vulnerabilities=enrich_vulnerabilities,
        )

    sbom_path = report_dir / "sbom.cdx.json"
    if force or not validation_json.exists():
        write_source_validation_report(
            sbom_path,
            dependency_tree_path,
            output_dir=validation_dir,
        )

    validation = read_json(validation_json)
    return {
        "case_id": case_id,
        "apk_path": normalize_path(apk_path),
        "slice_db": normalize_path(slice_db),
        "report_json": normalize_path(report_json),
        "validation_json": normalize_path(validation_json),
        "source_coordinates": slice_info.source_coordinates,
        "kept_coordinates": slice_info.kept_coordinates,
        "kept_components": slice_info.kept_components,
        "missing_source_coordinates": len(slice_info.missing_source_coordinates),
        "checked": validation.get("sbom_components"),
        "confirmed": validation.get("confirmed"),
        "version_mismatches": validation.get("version_mismatches"),
        "missing": validation.get("missing"),
    }


def build_source_coordinate_slice(
    *,
    source_db: Path,
    output_db: Path,
    source_coordinates: list[str],
    source_versions_by_coordinate: dict[str, list[str]],
    slice_mode: str,
    force: bool,
) -> SourceCoordinateSlice:
    if force or not output_db.exists():
        output_db.parent.mkdir(parents=True, exist_ok=True)
        if output_db.exists():
            output_db.unlink()
        copy_coordinate_slice(
            source_db=source_db,
            output_db=output_db,
            source_coordinates=source_coordinates,
            source_versions_by_coordinate=source_versions_by_coordinate,
            slice_mode=slice_mode,
        )

    with sqlite3.connect(output_db) as connection:
        kept_components, kept_coordinates = connection.execute(
            "SELECT COUNT(*), COUNT(DISTINCT coordinate) FROM components"
        ).fetchone()
        available_coordinates = {
            str(row[0]) for row in connection.execute("SELECT DISTINCT coordinate FROM components")
        }
    missing = sorted(set(source_coordinates) - available_coordinates)
    return SourceCoordinateSlice(
        db_path=output_db,
        source_coordinates=len(source_coordinates),
        kept_coordinates=int(kept_coordinates),
        kept_components=int(kept_components),
        missing_source_coordinates=missing,
    )


def copy_coordinate_slice(
    *,
    source_db: Path,
    output_db: Path,
    source_coordinates: list[str],
    source_versions_by_coordinate: dict[str, list[str]],
    slice_mode: str,
) -> None:
    source_db = source_db.resolve()
    keep = sorted(set(source_coordinates))
    coordinate_placeholders = ",".join("?" for _ in keep)
    coordinate_filter = f"WHERE coordinate IN ({coordinate_placeholders})" if keep else "WHERE 0"
    version_pairs = sorted(
        {
            (coordinate, version)
            for coordinate, versions in source_versions_by_coordinate.items()
            for version in versions
        }
    )
    version_conditions = " OR ".join("(coordinate = ? AND version = ?)" for _ in version_pairs)
    version_filter = f"WHERE {version_conditions}" if version_conditions else "WHERE 0"

    with sqlite3.connect(output_db) as connection:
        connection.execute(f"ATTACH DATABASE ? AS src", (str(source_db),))
        create_reference_schema(connection)
        connection.execute("CREATE TEMP TABLE keep_component_ids (id INTEGER PRIMARY KEY)")
        connection.execute(
            f"""
            INSERT INTO keep_component_ids(id)
            SELECT MIN(id)
            FROM src.components
            {coordinate_filter if slice_mode == "source-coordinate" else version_filter}
            GROUP BY coordinate, version
            """,
            tuple(keep)
            if slice_mode == "source-coordinate"
            else tuple(value for pair in version_pairs for value in pair),
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO components
            SELECT *
            FROM src.components
            WHERE id IN (SELECT id FROM keep_component_ids)
            """
        )
        connection.execute(
            """
            DELETE FROM keep_component_ids
            WHERE id NOT IN (SELECT id FROM components)
            """
        )
        for table in component_tables(connection, schema="src"):
            quoted = quote_identifier(table)
            connection.execute(
                f"""
                INSERT OR IGNORE INTO {quoted}
                SELECT *
                FROM src.{quoted}
                WHERE component_id IN (SELECT id FROM keep_component_ids)
                """
            )
        create_reference_indexes(connection)
        connection.commit()
        connection.execute("DETACH DATABASE src")


def create_reference_schema(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT type, name, sql
        FROM src.sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    for _, _, sql in rows:
        if sql:
            connection.execute(str(sql))


def create_reference_indexes(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT sql
        FROM src.sqlite_master
        WHERE type = 'index'
          AND sql IS NOT NULL
        ORDER BY name
        """
    ).fetchall()
    for (sql,) in rows:
        connection.execute(str(sql))


def component_tables(connection: sqlite3.Connection, *, schema: str = "main") -> list[str]:
    rows = connection.execute(
        f"""
        SELECT name
        FROM {quote_identifier(schema)}.sqlite_master
        WHERE type = 'table'
          AND name != 'components'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    tables = []
    for (table_name,) in rows:
        columns = {
            str(row[1])
            for row in connection.execute(
                f"PRAGMA {quote_identifier(schema)}.table_info({quote_identifier(str(table_name))})"
            )
        }
        if "component_id" in columns:
            tables.append(str(table_name))
    return tables


def build_dashboard(
    *,
    source_dashboard: dict[str, Any],
    output_root: Path,
    reference_db: Path,
    output_dashboard_json: Path,
    output_rows_csv: Path,
    output_gaps_csv: Path,
    slice_mode: str,
) -> dict[str, Any]:
    cases = []
    rows = []
    gaps = []
    for case in runnable_cases(source_dashboard):
        case_id = str(case["case_id"])
        report_path = output_root / f"report-real-{case_id}" / "report.json"
        validation_path = output_root / "source-validation" / case_id / "source-validation.json"
        slice_db = output_root / "reference-dbs" / f"{case_id}.sqlite"
        if not validation_path.exists() or not report_path.exists():
            cases.append(
                case_dashboard_row(
                    case,
                    status="pending",
                    report_path=report_path,
                    validation_path=validation_path,
                    slice_db=slice_db,
                )
            )
            continue

        validation = read_json(validation_path)
        source_dependencies = parse_gradle_dependency_tree(
            Path(validation["dependency_tree_path"]).read_text(encoding="utf-8")
        )
        case_row = case_dashboard_row(
            case,
            status="complete",
            report_path=report_path,
            validation_path=validation_path,
            slice_db=slice_db,
            validation=validation,
            source_dependencies=source_dependencies,
        )
        cases.append(case_row)
        for result in validation.get("results", []):
            if result.get("kind") != "sbom-component":
                continue
            rows.append(
                {
                    "case_id": case_id,
                    "app": case_name(case),
                    "coordinate": result.get("coordinate"),
                    "detected_version": result.get("version"),
                    "source_versions": ";".join(result.get("source_versions") or []),
                    "status": result.get("status"),
                    "confidence": result.get("confidence"),
                    "match_type": result.get("match_type"),
                    "purl": result.get("purl"),
                    "evidence_line": result.get("evidence_line") or "",
                }
            )

        emitted_coordinates = {
            result.get("coordinate")
            for result in validation.get("results", [])
            if result.get("kind") == "sbom-component"
        }
        with sqlite3.connect(reference_db) as connection:
            reference_versions = load_reference_versions(connection, set(source_dependencies))
        for coordinate, entry in source_dependencies.items():
            versions = reference_versions.get(coordinate, [])
            exact_versions = sorted(set(entry.resolved_versions) & set(versions))
            if coordinate in emitted_coordinates:
                continue
            gaps.append(
                {
                    "case_id": case_id,
                    "app": case_name(case),
                    "coordinate": coordinate,
                    "source_versions": ";".join(entry.resolved_versions),
                    "reference_versions": ";".join(versions),
                    "exact_source_version_in_large_db": bool(exact_versions),
                    "classification": (
                        "source-coordinate-present-not-emitted"
                        if versions
                        else "source-coordinate-missing-from-large-db"
                    ),
                }
            )

    write_csv(output_rows_csv, rows)
    write_csv(output_gaps_csv, gaps)
    summary = summarize_cases(cases, rows, gaps)
    return {
        "evaluation_mode": evaluation_mode(slice_mode),
        "policy": evaluation_policy(slice_mode),
        "reference_db": normalize_path(reference_db),
        "output_root": normalize_path(output_root),
        "output_dashboard_json": normalize_path(output_dashboard_json),
        "rows_csv": normalize_path(output_rows_csv),
        "gaps_csv": normalize_path(output_gaps_csv),
        "summary": summary,
        "cases": cases,
    }


def case_dashboard_row(
    case: dict[str, Any],
    *,
    status: str,
    report_path: Path,
    validation_path: Path,
    slice_db: Path,
    validation: dict[str, Any] | None = None,
    source_dependencies: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stats = validation or {}
    source_dependencies = source_dependencies or {}
    return {
        "case_id": case.get("case_id"),
        "app": case_name(case),
        "version": (case.get("apk_metadata") or {}).get("version_name"),
        "category": case.get("category"),
        "status": status,
        "source_coordinates": len(source_dependencies),
        "checked": stats.get("sbom_components", 0),
        "confirmed": stats.get("confirmed", 0),
        "version_mismatches": stats.get("version_mismatches", 0),
        "missing": stats.get("missing", 0),
        "confirmation_rate": safe_ratio(stats.get("confirmed", 0), stats.get("sbom_components", 0)),
        "paths": {
            "report": normalize_path(report_path),
            "validation": normalize_path(validation_path),
            "slice_db": normalize_path(slice_db),
        },
    }


def summarize_cases(
    cases: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> dict[str, Any]:
    completed = [case for case in cases if case["status"] == "complete"]
    checked = sum(int(case["checked"]) for case in completed)
    confirmed = sum(int(case["confirmed"]) for case in completed)
    mismatches = sum(int(case["version_mismatches"]) for case in completed)
    missing = sum(int(case["missing"]) for case in completed)
    return {
        "total_cases": len(cases),
        "completed_cases": len(completed),
        "pending_cases": len(cases) - len(completed),
        "checked": checked,
        "confirmed": confirmed,
        "version_mismatches": mismatches,
        "missing": missing,
        "confirmation_rate": safe_ratio(confirmed, checked),
        "confirmation_rate_percent": round(100.0 * safe_ratio(confirmed, checked), 1),
        "row_csv_rows": len(rows),
        "source_gap_rows": len(gaps),
        "source_gap_with_coordinate_in_large_db": sum(
            1 for row in gaps if row["classification"] == "source-coordinate-present-not-emitted"
        ),
        "source_gap_missing_from_large_db": sum(
            1 for row in gaps if row["classification"] == "source-coordinate-missing-from-large-db"
        ),
    }


def load_reference_versions(
    connection: sqlite3.Connection,
    coordinates: set[str],
) -> dict[str, list[str]]:
    if not coordinates:
        return {}
    placeholders = ",".join("?" for _ in coordinates)
    rows = connection.execute(
        f"""
        SELECT coordinate, version
        FROM components
        WHERE coordinate IN ({placeholders})
        ORDER BY coordinate, version
        """,
        tuple(sorted(coordinates)),
    ).fetchall()
    versions: dict[str, list[str]] = {}
    for coordinate, version in rows:
        versions.setdefault(str(coordinate), []).append(str(version))
    return versions


def build_markdown(dashboard: dict[str, Any]) -> str:
    summary = dashboard["summary"]
    lines = [
        "# Large Combined Source-Constrained Evaluation",
        "",
        "## Policy",
        "",
        dashboard["policy"],
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Completed cases | {summary['completed_cases']} / {summary['total_cases']} |",
        f"| Pending cases | {summary['pending_cases']} |",
        f"| Checked emitted rows | {summary['checked']} |",
        f"| Confirmed exact rows | {summary['confirmed']} |",
        f"| Version mismatches | {summary['version_mismatches']} |",
        f"| Missing emitted coordinates | {summary['missing']} |",
        f"| Confirmation rate | {summary['confirmation_rate_percent']}% |",
        f"| Source gap rows | {summary['source_gap_rows']} |",
        f"| Source gaps with coordinate in large DB | {summary['source_gap_with_coordinate_in_large_db']} |",
        f"| Source gaps missing from large DB | {summary['source_gap_missing_from_large_db']} |",
        "",
        "## Outputs",
        "",
        f"- Dashboard JSON: `{dashboard['output_dashboard_json']}`",
        f"- Row CSV: `{dashboard['rows_csv']}`",
        f"- Source gap CSV: `{dashboard['gaps_csv']}`",
        "",
        "## Case Progress",
        "",
        "| Case | App | Status | Checked | Exact | Wrong version | Missing | Confirmation |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for case in dashboard["cases"]:
        lines.append(
            "| "
            f"{escape_md(str(case['case_id']))} | "
            f"{escape_md(str(case.get('app') or ''))} | "
            f"{case['status']} | "
            f"{case['checked']} | "
            f"{case['confirmed']} | "
            f"{case['version_mismatches']} | "
            f"{case['missing']} | "
            f"{round(100.0 * case['confirmation_rate'], 1)}% |"
        )
    lines.append("")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def safe_ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def evaluation_mode(slice_mode: str) -> str:
    if slice_mode == "source-coordinate":
        return "source-coordinate-constrained"
    return "source-version-constrained"


def evaluation_policy(slice_mode: str) -> str:
    if slice_mode == "source-coordinate":
        return (
            "This is an evaluation-only oracle/source-coordinate constrained run. "
            "Each APK is matched only against large-DB coordinates that appear in "
            "its resolved source dependency tree, while retaining all available "
            "versions for those coordinates. It measures reference coverage and "
            "version selection under known source coordinates; it is not a "
            "production APK-only detection result."
        )
    return (
        "This is an evaluation-only oracle/source-version constrained run. "
        "Each APK is matched only against exact coordinate+version rows that "
        "appear in its resolved source dependency tree. It measures an upper "
        "bound for bytecode recognition and reference coverage when the correct "
        "source versions are known; it must not be reported as production "
        "APK-only version-selection accuracy."
    )


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_json_if_exists(path: str | Path) -> dict[str, Any] | None:
    if not path:
        return None
    candidate = Path(path)
    if not candidate.exists():
        return None
    return read_json(candidate)


def normalize_path(path: str | Path) -> str:
    return Path(path).as_posix()


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def case_name(case: dict[str, Any]) -> str:
    return str(case.get("name") or case.get("app") or case.get("case_id") or "")


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


if __name__ == "__main__":
    raise SystemExit(main())
