from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from apk_sbom.report import generate_final_report
from apk_sbom.source_validation import write_source_validation_report


DEFAULT_SOURCE_DASHBOARD_JSON = Path(
    "data/results/evaluation/real-apk-source-validation-dashboard.json"
)
DEFAULT_REFERENCE_DB = Path("data/reference_db/reference_features_real_apk_priority_versions.sqlite")
DEFAULT_OUTPUT_ROOT = Path("data/results/experiments/real-apk-priority-reference-db")
DEFAULT_OUTPUT_DASHBOARD_JSON = Path(
    "data/results/evaluation/real-apk-priority-source-validation-dashboard.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Rerun source-validated real APK reports against the real-APK priority "
            "reference DB, preserving the original dashboard shape for coverage comparison."
        )
    )
    parser.add_argument("--source-dashboard-json", default=str(DEFAULT_SOURCE_DASHBOARD_JSON))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--output-dashboard-json", default=str(DEFAULT_OUTPUT_DASHBOARD_JSON))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--query-osv",
        action="store_true",
        help="Query OSV while generating reports. Default is off for fast reference-DB comparison runs.",
    )
    parser.add_argument(
        "--enrich-vulnerabilities",
        action="store_true",
        help="Fetch enriched vulnerability details when --query-osv is enabled.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_dashboard_path = Path(args.source_dashboard_json)
    reference_db = Path(args.reference_db)
    output_root = Path(args.output_root)
    output_dashboard_path = Path(args.output_dashboard_json)

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
                query_osv=args.query_osv,
                enrich_vulnerabilities=args.enrich_vulnerabilities,
            )
        )

    updated_dashboard = rewrite_dashboard_paths(dashboard, output_root=output_root)
    output_dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    output_dashboard_path.write_text(
        json.dumps(updated_dashboard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "source_dashboard_json": normalize_path(source_dashboard_path),
                "output_dashboard_json": normalize_path(output_dashboard_path),
                "output_root": normalize_path(output_root),
                "reference_db": normalize_path(reference_db),
                "runnable_cases": len(cases),
                "selected_cases": len(selected),
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
    query_osv: bool,
    enrich_vulnerabilities: bool,
) -> dict[str, Any]:
    case_id = str(case["case_id"])
    old_report = read_json((case.get("paths") or {})["report"])
    apk_path = Path(old_report["apk"]["apk_path"])
    dependency_tree_path = Path((case.get("validation_stats") or {})["dependency_tree_path"])
    report_dir = output_root / f"report-real-{case_id}"
    validation_dir = output_root / "source-validation" / case_id
    report_json = report_dir / "report.json"
    validation_json = validation_dir / "source-validation.json"

    if force or not report_json.exists():
        report_artifacts = generate_final_report(
            apk_path,
            output_dir=report_dir,
            db_path=reference_db,
            enable_reference_package_prefilter=True,
            query_osv=query_osv,
            enrich_vulnerabilities=enrich_vulnerabilities,
        )
    else:
        report_artifacts = None

    sbom_path = report_dir / "sbom.cdx.json"
    if force or not validation_json.exists():
        validation_artifacts = write_source_validation_report(
            sbom_path,
            dependency_tree_path,
            output_dir=validation_dir,
        )
    else:
        validation_artifacts = None

    validation = read_json(validation_json)
    return {
        "case_id": case_id,
        "apk_path": normalize_path(apk_path),
        "report_json": normalize_path(report_json),
        "validation_json": normalize_path(validation_json),
        "report_generated": report_artifacts is not None,
        "validation_generated": validation_artifacts is not None,
        "confirmed": validation.get("confirmed"),
        "version_mismatches": validation.get("version_mismatches"),
        "missing": validation.get("missing"),
        "checked": validation.get("sbom_components"),
    }


def rewrite_dashboard_paths(dashboard: dict[str, Any], *, output_root: Path) -> dict[str, Any]:
    updated = json.loads(json.dumps(dashboard))
    for case in updated.get("cases", []):
        case_id = str(case.get("case_id"))
        report_path = output_root / f"report-real-{case_id}" / "report.json"
        validation_path = output_root / "source-validation" / case_id / "source-validation.json"
        if report_path.exists():
            case.setdefault("paths", {})["report"] = normalize_path(report_path)
        if validation_path.exists():
            case.setdefault("paths", {})["validation"] = normalize_path(validation_path)
            validation = read_json(validation_path)
            stats = case.setdefault("validation_stats", {})
            stats["checked"] = validation.get("sbom_components", 0)
            stats["confirmed"] = validation.get("confirmed", 0)
            stats["version_mismatches"] = validation.get("version_mismatches", 0)
            stats["missing"] = validation.get("missing", 0)
            stats["confirmation_rate"] = safe_ratio(stats["confirmed"], stats["checked"])
            stats["confirmation_rate_percent"] = round(100.0 * stats["confirmation_rate"], 1)
    return updated


def safe_ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


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


if __name__ == "__main__":
    raise SystemExit(main())
