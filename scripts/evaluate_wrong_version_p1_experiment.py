from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apk_sbom.report import generate_final_report
from apk_sbom.source_validation import write_source_validation_report


DEFAULT_DASHBOARD_JSON = Path("data/results/evaluation/real-apk-source-validation-dashboard.json")
DEFAULT_MISSES_CSV = Path("data/results/evaluation/real-apk-source-validation-dashboard-misses.csv")
DEFAULT_DB_PATH = Path("data/reference_db/reference_features_wrong_version_coroutines_android_1_6_4.sqlite")
DEFAULT_OUTPUT_ROOT = Path("data/results/experiments/wrong-version-p1-coroutines-android-1-6-4")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/WRONG_VERSION_P1_COROUTINES_ANDROID_1_6_4_EXPERIMENT.md")

DEFAULT_PARTIAL_CONTROLS = (
    "newpipe",
    "antennapod",
    "kde-connect",
    "wikipedia-android",
    "conversations",
    "aegis-authenticator",
    "markor",
    "nextcloud-android",
)

DEFAULT_CONTROLLED_CONTROLS = (
    "data/test_apks/controlled-com-google-code-gson-gson-2.8.9-clear.apk",
    "data/test_apks/controlled-com-google-code-gson-gson-2.8.9-r8-shrink.apk",
    "data/test_apks/controlled-commons-codec-commons-codec-1.16.1-r8-shrink.apk",
    "data/test_apks/controlled-multi-gson-2-8-9-commons-codec-1-16-1-clear-multidex.apk",
    "data/test_apks/generated-okhttp-4-10-0-r8-shrink-optimize.apk",
    "data/test_apks/generated-multi-ktor-okhttp-jvm-2-3-12-stack-clear-multidex.apk",
)

DEFAULT_CONTROLLED_EVALUATION_JSON = Path("data/results/evaluation/controlled-evaluation.json")


@dataclass(frozen=True)
class MatrixCase:
    case_id: str
    name: str
    case_kind: str
    role: str
    lane_role: str
    apk_path: str
    dependency_tree_path: str
    baseline_report_path: str
    baseline_validation_path: str
    expected_components: tuple[dict[str, str], ...] = ()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a guarded P1 wrong-version source-version experiment against "
            "target rows and current controls."
        ),
    )
    parser.add_argument("--dashboard-json", default=str(DEFAULT_DASHBOARD_JSON))
    parser.add_argument("--misses-csv", default=str(DEFAULT_MISSES_CSV))
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument(
        "--experiment-name",
        default="wrong-version-p1-coroutines-android-1.6.4",
    )
    parser.add_argument(
        "--title",
        default="Wrong-Version P1 Coroutines Android 1.6.4 Experiment",
    )
    parser.add_argument(
        "--candidate-reference",
        action="append",
        help="Reference added to the isolated experiment DB. Can be repeated.",
    )
    parser.add_argument(
        "--finding",
        action="append",
        help="Interpretation finding to include in the generated evidence. Can be repeated.",
    )
    parser.add_argument("--coordinate", default="org.jetbrains.kotlinx:kotlinx-coroutines-android")
    parser.add_argument("--tool-selected-version", default="1.7.3")
    parser.add_argument("--source-version", default="1.6.4")
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--min-score", type=float, default=0.05)
    parser.add_argument("--case", action="append", help="Run only this case id. Can be repeated.")
    parser.add_argument("--controlled-evaluation-json", default=str(DEFAULT_CONTROLLED_EVALUATION_JSON))
    parser.add_argument(
        "--controlled-control",
        action="append",
        help="Controlled APK path to include as a ground-truth control.",
    )
    parser.add_argument(
        "--partial-control",
        action="append",
        help="Partial control case id. Defaults to the established current-control slice.",
    )
    parser.add_argument("--reuse-existing", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    dashboard = read_json(args.dashboard_json)
    target_case_ids = matching_target_case_ids(
        Path(args.misses_csv),
        coordinate=args.coordinate,
        selected_version=args.tool_selected_version,
        source_version=args.source_version,
    )
    cases = build_matrix_cases(
        dashboard,
        target_case_ids=target_case_ids,
        partial_controls=tuple(args.partial_control or DEFAULT_PARTIAL_CONTROLS),
        controlled_evaluation_json=Path(args.controlled_evaluation_json),
        controlled_controls=tuple(args.controlled_control or DEFAULT_CONTROLLED_CONTROLS),
    )
    if args.case:
        selected = set(args.case)
        cases = [case for case in cases if case.case_id in selected]
        missing = selected - {case.case_id for case in cases}
        if missing:
            raise SystemExit(f"unknown selected case id(s): {', '.join(sorted(missing))}")
    if not cases:
        raise SystemExit("no cases selected")

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    rows = [
        run_case(
            case,
            db_path=args.db_path,
            output_root=output_root,
            top=args.top,
            min_score=args.min_score,
            coordinate=args.coordinate,
            source_version=args.source_version,
            reuse_existing=args.reuse_existing,
        )
        for case in cases
    ]
    summary = build_summary(
        rows,
        db_path=args.db_path,
        coordinate=args.coordinate,
        selected_version=args.tool_selected_version,
        source_version=args.source_version,
        target_case_ids=target_case_ids,
        experiment_name=args.experiment_name,
        title=args.title,
        candidate_references=tuple(
            args.candidate_reference
            or (f"{args.coordinate}@{args.source_version}",)
        ),
        findings=tuple(args.finding or ()),
    )

    summary_json = output_root / "summary.json"
    summary_md = output_root / "summary.md"
    summary["artifacts"] = {
        "summary_json": normalize_path(summary_json),
        "summary_markdown": normalize_path(summary_md),
        "output_doc": normalize_path(args.output_doc),
    }
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_md.write_text(build_markdown(summary), encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(summary, tracked_doc=True), encoding="utf-8")

    print(
        json.dumps(
            {
                "summary_json": normalize_path(summary_json),
                "summary_markdown": normalize_path(summary_md),
                "output_doc": normalize_path(output_doc),
                "cases": len(rows),
                "target_cases": summary["summary"]["target_cases"],
                "target_improved": summary["summary"]["target_improved_cases"],
                "control_regressions": summary["summary"]["control_regressed_cases"],
                "verdict": summary["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def matching_target_case_ids(
    misses_csv: Path,
    *,
    coordinate: str,
    selected_version: str,
    source_version: str,
) -> set[str]:
    wanted_package = f"{coordinate}@{source_version}"
    case_ids: set[str] = set()
    with misses_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if not is_true(row.get("emitted_component")):
                continue
            if row.get("miss_class") != "emitted-wrong-version":
                continue
            if row.get("coordinate") != coordinate:
                continue
            if row.get("tool_selected_version") != selected_version:
                continue
            if row.get("real_package_and_version") != wanted_package:
                continue
            case_ids.add(str(row["case_id"]))
    return case_ids


def build_matrix_cases(
    dashboard: dict[str, Any],
    *,
    target_case_ids: set[str],
    partial_controls: tuple[str, ...],
    controlled_evaluation_json: Path,
    controlled_controls: tuple[str, ...],
) -> list[MatrixCase]:
    cases_by_id = {case["case_id"]: case for case in dashboard.get("cases", [])}
    selected_ids: list[tuple[str, str, str]] = []
    selected_ids.extend((case_id, "target", "source-validation") for case_id in sorted(target_case_ids))
    for case in dashboard.get("cases", []):
        if case.get("role") == "clean-source-validated":
            selected_ids.append((case["case_id"], "control-clean", "source-validation"))
    for case in dashboard.get("cases", []):
        if case.get("role") == "source-validated-no-maven-signal":
            selected_ids.append((case["case_id"], "control-no-maven", "source-validation"))
    for case in dashboard.get("cases", []):
        if str(case.get("role", "")).startswith("limitation-"):
            selected_ids.append((case["case_id"], "control-boundary", "report-only"))
    selected_ids.extend((case_id, "control-partial", "source-validation") for case_id in partial_controls)

    rows: list[MatrixCase] = []
    seen: set[str] = set()
    for case_id, lane_role, case_kind in selected_ids:
        if case_id in seen:
            continue
        seen.add(case_id)
        case = cases_by_id.get(case_id)
        if not case:
            continue
        if case_kind == "report-only":
            rows.append(build_report_only_case(case, lane_role=lane_role))
        else:
            rows.append(build_source_validation_case(case, lane_role=lane_role))
    rows.extend(build_controlled_cases(controlled_evaluation_json, controlled_controls))
    return rows


def build_source_validation_case(case: dict[str, Any], *, lane_role: str) -> MatrixCase:
    paths = case.get("paths", {})
    report_path = require_path(paths.get("report"), f"{case['case_id']} report")
    validation_path = require_path(paths.get("validation"), f"{case['case_id']} validation")
    report = read_json(report_path)
    validation = read_json(validation_path)
    apk_path = require_path(report.get("apk", {}).get("apk_path"), f"{case['case_id']} apk")
    dependency_tree_path = require_path(
        validation.get("dependency_tree_path"),
        f"{case['case_id']} dependency tree",
    )
    return MatrixCase(
        case_id=str(case["case_id"]),
        name=str(case.get("name", case["case_id"])),
        case_kind="source-validation",
        role=str(case.get("role", "")),
        lane_role=lane_role,
        apk_path=apk_path,
        dependency_tree_path=dependency_tree_path,
        baseline_report_path=report_path,
        baseline_validation_path=validation_path,
    )


def build_report_only_case(case: dict[str, Any], *, lane_role: str) -> MatrixCase:
    paths = case.get("paths", {})
    report_path = require_path(paths.get("report"), f"{case['case_id']} report")
    report = read_json(report_path)
    apk_path = require_path(report.get("apk", {}).get("apk_path"), f"{case['case_id']} apk")
    return MatrixCase(
        case_id=str(case["case_id"]),
        name=str(case.get("name", case["case_id"])),
        case_kind="report-only",
        role=str(case.get("role", "")),
        lane_role=lane_role,
        apk_path=apk_path,
        dependency_tree_path="",
        baseline_report_path=report_path,
        baseline_validation_path="",
    )


def build_controlled_cases(
    controlled_evaluation_json: Path,
    controlled_controls: tuple[str, ...],
) -> list[MatrixCase]:
    evaluation = read_json(controlled_evaluation_json)
    report_paths_by_apk: dict[str, str] = {}
    for row in evaluation.get("rows", []):
        apk_path = normalize_path(row.get("apk_path"))
        report_path = row.get("report_path")
        if apk_path and report_path and apk_path not in report_paths_by_apk:
            report_paths_by_apk[apk_path] = str(report_path)

    cases: list[MatrixCase] = []
    for apk_path in controlled_controls:
        normalized_apk = normalize_path(apk_path)
        baseline_report_path = require_path(
            report_paths_by_apk.get(normalized_apk),
            f"{normalized_apk} controlled baseline report",
        )
        truth_path = Path(normalized_apk).with_suffix(".ground-truth.json")
        truth = read_json(require_path(truth_path, f"{normalized_apk} ground truth"))
        expected = tuple(expected_components_from_truth(truth))
        cases.append(
            MatrixCase(
                case_id=Path(normalized_apk).stem,
                name=Path(normalized_apk).stem,
                case_kind="controlled",
                role="controlled-ground-truth",
                lane_role="control-controlled",
                apk_path=require_path(normalized_apk, f"{normalized_apk} apk"),
                dependency_tree_path="",
                baseline_report_path=baseline_report_path,
                baseline_validation_path="",
                expected_components=expected,
            )
        )
    return cases


def run_case(
    case: MatrixCase,
    *,
    db_path: str,
    output_root: Path,
    top: int,
    min_score: float,
    coordinate: str,
    source_version: str,
    reuse_existing: bool,
) -> dict[str, Any]:
    print(f"running {case.case_id} ({case.lane_role})")
    if case.case_kind == "controlled":
        return run_controlled_case(
            case,
            db_path=db_path,
            output_root=output_root,
            top=top,
            min_score=min_score,
            reuse_existing=reuse_existing,
        )
    if case.case_kind == "report-only":
        return run_report_only_case(
            case,
            db_path=db_path,
            output_root=output_root,
            top=top,
            min_score=min_score,
            reuse_existing=reuse_existing,
        )

    report_dir = output_root / f"report-real-{case.case_id}"
    validation_dir = output_root / "source-validation" / case.case_id
    report_json = report_dir / "report.json"
    validation_json = validation_dir / "source-validation.json"
    report_json = generate_or_reuse_report(
        case.apk_path,
        report_dir=report_dir,
        report_json=report_json,
        db_path=db_path,
        top=top,
        min_score=min_score,
        reuse_existing=reuse_existing,
    )
    if not reuse_existing or not validation_json.exists():
        validation_artifacts = write_source_validation_report(
            report_dir / "sbom.cdx.json",
            case.dependency_tree_path,
            output_dir=validation_dir,
        )
        validation_json = validation_artifacts.validation_json

    baseline = read_json(case.baseline_validation_path)
    validation = read_json(validation_json)
    report = read_json(report_json)
    row = {
        "case_id": case.case_id,
        "name": case.name,
        "case_kind": case.case_kind,
        "role": case.role,
        "lane_role": case.lane_role,
        "baseline_components": int(baseline.get("sbom_components", 0)),
        "components": len(report.get("detected_components", [])),
        "baseline_confirmed": int(baseline.get("confirmed", 0)),
        "confirmed": int(validation.get("confirmed", 0)),
        "baseline_version_mismatches": int(baseline.get("version_mismatches", 0)),
        "version_mismatches": int(validation.get("version_mismatches", 0)),
        "baseline_missing": int(baseline.get("missing", 0)),
        "missing": int(validation.get("missing", 0)),
        "target_before": find_component_result(baseline, coordinate),
        "target_after": find_component_result(validation, coordinate),
        "report_dir": normalize_path(report_dir),
        "validation_dir": normalize_path(validation_dir),
        "baseline_report_path": normalize_path(case.baseline_report_path),
        "baseline_validation_path": normalize_path(case.baseline_validation_path),
    }
    row["delta_components"] = row["components"] - row["baseline_components"]
    row["delta_confirmed"] = row["confirmed"] - row["baseline_confirmed"]
    row["delta_version_mismatches"] = (
        row["version_mismatches"] - row["baseline_version_mismatches"]
    )
    row["delta_missing"] = row["missing"] - row["baseline_missing"]
    row["regressed_vs_baseline"] = (
        row["delta_confirmed"] < 0
        or row["delta_version_mismatches"] > 0
        or row["delta_missing"] > 0
    )
    row["improved_vs_baseline"] = (
        row["delta_confirmed"] > 0
        or row["delta_version_mismatches"] < 0
        or row["delta_missing"] < 0
    )
    row["target_fixed"] = target_fixed(row["target_after"], source_version)
    row["remaining_mismatches"] = summarize_results(validation, {"version-mismatch", "missing"})
    return row


def run_controlled_case(
    case: MatrixCase,
    *,
    db_path: str,
    output_root: Path,
    top: int,
    min_score: float,
    reuse_existing: bool,
) -> dict[str, Any]:
    report_dir = output_root / "controlled" / f"report-{case.case_id}"
    report_json = report_dir / "report.json"
    report_json = generate_or_reuse_report(
        case.apk_path,
        report_dir=report_dir,
        report_json=report_json,
        db_path=db_path,
        top=top,
        min_score=min_score,
        reuse_existing=reuse_existing,
    )
    baseline = read_json(case.baseline_report_path)
    report = read_json(report_json)
    baseline_eval = evaluate_controlled_report(baseline, case.expected_components)
    experiment_eval = evaluate_controlled_report(report, case.expected_components)
    row = build_report_comparison_row(
        case,
        baseline,
        report,
        report_dir=report_dir,
        report_json=report_json,
        baseline_eval=baseline_eval,
        experiment_eval=experiment_eval,
    )
    row["regressed_vs_baseline"] = (
        row["delta_confirmed"] < 0
        or row["delta_version_mismatches"] > 0
        or row["delta_missing"] > 0
        or row["controlled_false_positive_components"] > row["baseline_controlled_false_positive_components"]
    )
    row["improved_vs_baseline"] = (
        row["delta_confirmed"] > 0
        or row["delta_version_mismatches"] < 0
        or row["delta_missing"] < 0
    )
    row["target_fixed"] = False
    row["remaining_mismatches"] = []
    return row


def run_report_only_case(
    case: MatrixCase,
    *,
    db_path: str,
    output_root: Path,
    top: int,
    min_score: float,
    reuse_existing: bool,
) -> dict[str, Any]:
    report_dir = output_root / "boundary" / f"report-{case.case_id}"
    report_json = report_dir / "report.json"
    report_json = generate_or_reuse_report(
        case.apk_path,
        report_dir=report_dir,
        report_json=report_json,
        db_path=db_path,
        top=top,
        min_score=min_score,
        reuse_existing=reuse_existing,
    )
    baseline = read_json(case.baseline_report_path)
    report = read_json(report_json)
    baseline_components = maven_component_set(baseline)
    experiment_components = maven_component_set(report)
    changed = baseline_components != experiment_components
    row = {
        "case_id": case.case_id,
        "name": case.name,
        "case_kind": case.case_kind,
        "role": case.role,
        "lane_role": case.lane_role,
        "baseline_components": len(baseline_components),
        "components": len(experiment_components),
        "baseline_confirmed": 0,
        "confirmed": 0,
        "baseline_version_mismatches": 0,
        "version_mismatches": 0,
        "baseline_missing": 0,
        "missing": 0,
        "target_before": None,
        "target_after": None,
        "report_dir": normalize_path(report_dir),
        "validation_dir": "",
        "baseline_report_path": normalize_path(case.baseline_report_path),
        "baseline_validation_path": "",
        "baseline_maven_components": sorted(baseline_components),
        "maven_components": sorted(experiment_components),
        "report_only_added_components": sorted(experiment_components - baseline_components),
        "report_only_removed_components": sorted(baseline_components - experiment_components),
        "report_only_component_set_changed": changed,
    }
    row["delta_components"] = row["components"] - row["baseline_components"]
    row["delta_confirmed"] = 0
    row["delta_version_mismatches"] = 0
    row["delta_missing"] = 0
    row["regressed_vs_baseline"] = changed
    row["improved_vs_baseline"] = False
    row["target_fixed"] = False
    row["remaining_mismatches"] = []
    return row


def generate_or_reuse_report(
    apk_path: str,
    *,
    report_dir: Path,
    report_json: Path,
    db_path: str,
    top: int,
    min_score: float,
    reuse_existing: bool,
) -> Path:
    if reuse_existing and report_json.exists():
        return report_json
    artifacts = generate_final_report(
        apk_path,
        output_dir=report_dir,
        db_path=db_path,
        top=top,
        min_score=min_score,
        query_osv=False,
    )
    return artifacts.report_json


def build_report_comparison_row(
    case: MatrixCase,
    baseline: dict[str, Any],
    report: dict[str, Any],
    *,
    report_dir: Path,
    report_json: Path,
    baseline_eval: dict[str, int],
    experiment_eval: dict[str, int],
) -> dict[str, Any]:
    row = {
        "case_id": case.case_id,
        "name": case.name,
        "case_kind": case.case_kind,
        "role": case.role,
        "lane_role": case.lane_role,
        "baseline_components": len(maven_component_set(baseline)),
        "components": len(maven_component_set(report)),
        "baseline_confirmed": baseline_eval["confirmed"],
        "confirmed": experiment_eval["confirmed"],
        "baseline_version_mismatches": baseline_eval["version_mismatches"],
        "version_mismatches": experiment_eval["version_mismatches"],
        "baseline_missing": baseline_eval["missing"],
        "missing": experiment_eval["missing"],
        "baseline_controlled_false_positive_components": baseline_eval["false_positives"],
        "controlled_false_positive_components": experiment_eval["false_positives"],
        "target_before": None,
        "target_after": None,
        "report_dir": normalize_path(report_dir),
        "validation_dir": "",
        "baseline_report_path": normalize_path(case.baseline_report_path),
        "baseline_validation_path": "",
        "report_json": normalize_path(report_json),
    }
    row["delta_components"] = row["components"] - row["baseline_components"]
    row["delta_confirmed"] = row["confirmed"] - row["baseline_confirmed"]
    row["delta_version_mismatches"] = (
        row["version_mismatches"] - row["baseline_version_mismatches"]
    )
    row["delta_missing"] = row["missing"] - row["baseline_missing"]
    return row


def build_summary(
    rows: list[dict[str, Any]],
    *,
    db_path: str,
    coordinate: str,
    selected_version: str,
    source_version: str,
    target_case_ids: set[str],
    experiment_name: str = "wrong-version-p1-coroutines-android-1.6.4",
    title: str = "Wrong-Version P1 Coroutines Android 1.6.4 Experiment",
    candidate_references: tuple[str, ...] = (),
    findings: tuple[str, ...] = (),
) -> dict[str, Any]:
    target_rows = [row for row in rows if row["lane_role"] == "target"]
    control_rows = [row for row in rows if row["lane_role"].startswith("control")]
    target_improved = [
        row["case_id"]
        for row in target_rows
        if row["target_fixed"] or (row["improved_vs_baseline"] and not row["regressed_vs_baseline"])
    ]
    regressed_controls = [row["case_id"] for row in control_rows if row["regressed_vs_baseline"]]
    regressed_targets = [row["case_id"] for row in target_rows if row["regressed_vs_baseline"]]
    summary = {
        "cases": len(rows),
        "target_cases": len(target_rows),
        "control_cases": len(control_rows),
        "target_fixed_cases": sum(1 for row in target_rows if row["target_fixed"]),
        "target_improved_cases": len(target_improved),
        "target_regressed_cases": len(regressed_targets),
        "control_regressed_cases": len(regressed_controls),
        "no_maven_control_regressed_cases": sum(
            1
            for row in control_rows
            if row["lane_role"] == "control-no-maven" and row["regressed_vs_baseline"]
        ),
        "boundary_control_regressed_cases": sum(
            1
            for row in control_rows
            if row["lane_role"] == "control-boundary" and row["regressed_vs_baseline"]
        ),
        "controlled_control_regressed_cases": sum(
            1
            for row in control_rows
            if row["lane_role"] == "control-controlled" and row["regressed_vs_baseline"]
        ),
        "clean_control_regressed_cases": sum(
            1
            for row in control_rows
            if row["lane_role"] == "control-clean" and row["regressed_vs_baseline"]
        ),
    }
    return {
        "schema_version": 1,
        "experiment": experiment_name,
        "title": title,
        "db_path": normalize_path(db_path),
        "candidate": {
            "coordinate": coordinate,
            "source_version": source_version,
            "baseline_selected_version": selected_version,
            "candidate_version": f"{coordinate}@{source_version}",
            "candidate_references": list(
                candidate_references or (f"{coordinate}@{source_version}",)
            ),
        },
        "target_case_ids_from_dashboard": sorted(target_case_ids),
        "summary": summary,
        "findings": list(findings),
        "rows": rows,
        "verdict": verdict(summary),
        "decision": decision(summary),
        "policy": [
            "Experiment-only: do not change the shared calibrated DB from this artifact alone.",
            "Promote only if target rows improve and controlled, clean, partial, no-Maven, and boundary controls do not regress.",
            "Reject or keep app-specific if the candidate creates new version mismatches or missing-source rows in controls.",
        ],
    }


def verdict(summary: dict[str, int]) -> str:
    if summary["control_regressed_cases"] or summary["target_regressed_cases"]:
        return "wrong-version-p1-experiment-rejected-regressions"
    if summary["target_fixed_cases"] or summary["target_improved_cases"]:
        return "wrong-version-p1-experiment-promotion-candidate"
    return "wrong-version-p1-experiment-no-target-benefit"


def decision(summary: dict[str, int]) -> str:
    if summary["control_regressed_cases"]:
        return "Keep experiment-only; control regressions block shared DB promotion."
    if summary["target_regressed_cases"]:
        return "Keep experiment-only; target regressions block shared DB promotion."
    if summary["target_fixed_cases"] or summary["target_improved_cases"]:
        return "Candidate is clean in this matrix; split/expand controls before any shared DB promotion."
    return "No target benefit; do not promote."


def build_markdown(summary: dict[str, Any], *, tracked_doc: bool = False) -> str:
    counts = summary["summary"]
    candidate = summary["candidate"]
    lines = [
        f"# {summary.get('title', 'Wrong-Version P1 Experiment')}",
        "",
        "Generated by `scripts/evaluate_wrong_version_p1_experiment.py`.",
        "",
        f"Verdict: `{summary['verdict']}`.",
        "",
        summary["decision"],
        "",
        "## Scope",
        "",
        f"- Candidate: `{candidate['candidate_version']}`",
        "- Isolated DB additions: "
        + ", ".join(
            f"`{item}`" for item in candidate.get("candidate_references", [])
        ),
        f"- Baseline selected version: `{candidate['baseline_selected_version']}`",
        f"- Experiment DB: `{summary['db_path']}`",
        f"- Target cases from dashboard: `{counts['target_cases']}`",
        f"- Control cases: `{counts['control_cases']}`",
        f"- Target fixed cases: `{counts['target_fixed_cases']}`",
        f"- Target improved cases: `{counts['target_improved_cases']}`",
        f"- Target regressed cases: `{counts['target_regressed_cases']}`",
        f"- Control regressed cases: `{counts['control_regressed_cases']}`",
        f"- Controlled control regressions: `{counts['controlled_control_regressed_cases']}`",
        f"- Clean control regressions: `{counts['clean_control_regressed_cases']}`",
        f"- No-Maven control regressions: `{counts['no_maven_control_regressed_cases']}`",
        f"- Boundary control regressions: `{counts['boundary_control_regressed_cases']}`",
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in summary["policy"])
    if summary.get("findings"):
        lines.extend(
            [
                "",
                "## Interpretation",
                "",
            ]
        )
        lines.extend(f"- {item}" for item in summary["findings"])
    lines.extend(
        [
            "",
            "## Matrix Results",
            "",
            "| Case | Lane | Baseline | Experiment | Delta | Target before | Target after | Status |",
            "|---|---|---:|---:|---|---|---|---|",
        ]
    )
    for row in summary["rows"]:
        status = "regressed" if row["regressed_vs_baseline"] else "unchanged"
        if row["improved_vs_baseline"] and not row["regressed_vs_baseline"]:
            status = "improved"
        if row["target_fixed"]:
            status = "target-fixed"
        lines.append(
            "| "
            f"{md(row['name'])} | "
            f"`{md(row['lane_role'])}` | "
            f"{row['baseline_confirmed']}/{row['baseline_components']} | "
            f"{row['confirmed']}/{row['components']} | "
            f"{row['delta_confirmed']:+d} confirmed, {row['delta_version_mismatches']:+d} mismatches, {row['delta_missing']:+d} missing | "
            f"{component_cell(row['target_before'])} | "
            f"{component_cell(row['target_after'])} | "
            f"`{status}` |"
        )
    regressed = [row for row in summary["rows"] if row["regressed_vs_baseline"]]
    if regressed:
        lines.extend(
            [
                "",
                "## Regression Details",
                "",
                "| Case | Lane | Reason |",
                "|---|---|---|",
            ]
        )
        for row in regressed:
            lines.append(
                "| "
                f"{md(row['name'])} | "
                f"`{md(row['lane_role'])}` | "
                f"{regression_reason(row)} |"
            )
    if tracked_doc:
        artifacts = summary.get("artifacts", {})
        lines.extend(
            [
                "",
                "## Generated Evidence",
                "",
                f"- JSON summary: `{artifacts.get('summary_json', '')}`",
                f"- Markdown summary: `{artifacts.get('summary_markdown', '')}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def find_component_result(validation: dict[str, Any], coordinate: str) -> dict[str, Any] | None:
    for result in validation.get("results", []):
        if result.get("kind") == "sbom-component" and result.get("coordinate") == coordinate:
            return {
                "version": str(result.get("version", "")),
                "status": str(result.get("status", "")),
                "source_versions": result.get("source_versions", []),
                "confidence": result.get("confidence"),
                "match_type": result.get("match_type"),
            }
    return None


def evaluate_controlled_report(
    report: dict[str, Any],
    expected_components: tuple[dict[str, str], ...],
) -> dict[str, int]:
    components = report.get("detected_components", [])
    expected_coordinates = {component["coordinate"] for component in expected_components}
    confirmed = 0
    version_mismatches = 0
    missing = 0
    for expected in expected_components:
        coordinate = expected["coordinate"]
        expected_version = expected["version"]
        matching = [
            component
            for component in components
            if component.get("group")
            and component.get("artifact")
            and f"{component['group']}:{component['artifact']}" == coordinate
        ]
        if not matching:
            missing += 1
        elif any(component.get("version") == expected_version for component in matching):
            confirmed += 1
        else:
            version_mismatches += 1
    false_positives = len(
        {
            f"{component.get('group')}:{component.get('artifact')}"
            for component in components
            if component.get("group")
            and component.get("artifact")
            and f"{component['group']}:{component['artifact']}" not in expected_coordinates
        }
    )
    return {
        "confirmed": confirmed,
        "version_mismatches": version_mismatches,
        "missing": missing,
        "false_positives": false_positives,
    }


def expected_components_from_truth(truth: dict[str, Any]) -> list[dict[str, str]]:
    components = truth.get("expected_components")
    if components:
        return [
            {
                "coordinate": str(component["coordinate"]),
                "version": str(component["version"]),
            }
            for component in components
        ]
    return [{"coordinate": str(truth["coordinate"]), "version": str(truth["version"])}]


def maven_component_set(report: dict[str, Any]) -> set[str]:
    components: set[str] = set()
    for component in report.get("detected_components", []):
        group = component.get("group")
        artifact = component.get("artifact")
        if group and artifact:
            components.add(f"{group}:{artifact}@{component.get('version')}")
    return components


def target_fixed(result: dict[str, Any] | None, source_version: str) -> bool:
    return bool(result and result.get("version") == source_version and result.get("status") == "confirmed")


def summarize_results(validation: dict[str, Any], statuses: set[str]) -> list[dict[str, str]]:
    rows = []
    for result in validation.get("results", []):
        if result.get("kind") != "sbom-component":
            continue
        if result.get("status") not in statuses:
            continue
        rows.append(
            {
                "coordinate": str(result.get("coordinate")),
                "version": str(result.get("version")),
                "source_versions": ", ".join(result.get("source_versions", [])) or "not found",
                "status": str(result.get("status")),
            }
        )
    return rows


def component_cell(result: dict[str, Any] | None) -> str:
    if not result:
        return "not emitted"
    source_versions = ", ".join(result.get("source_versions") or [])
    if source_versions:
        return f"`{md(result['version'])}` / `{md(result['status'])}` / source `{md(source_versions)}`"
    return f"`{md(result['version'])}` / `{md(result['status'])}`"


def regression_reason(row: dict[str, Any]) -> str:
    if row.get("case_kind") == "report-only":
        added = row.get("report_only_added_components") or []
        removed = row.get("report_only_removed_components") or []
        parts = []
        if added:
            parts.append("added " + "<br>".join(f"`{md(item)}`" for item in added))
        if removed:
            parts.append("removed " + "<br>".join(f"`{md(item)}`" for item in removed))
        return "; ".join(parts) or "report-only component set changed"
    details = []
    if row.get("delta_confirmed", 0) < 0:
        details.append(f"{row['delta_confirmed']:+d} confirmed")
    if row.get("delta_version_mismatches", 0) > 0:
        details.append(f"{row['delta_version_mismatches']:+d} mismatches")
    if row.get("delta_missing", 0) > 0:
        details.append(f"{row['delta_missing']:+d} missing")
    target_after = component_cell(row.get("target_after"))
    if target_after != "not emitted":
        details.append(f"target after {target_after}")
    return "; ".join(details) or "control gate regressed"


def require_path(path: Any, label: str) -> str:
    if not path:
        raise SystemExit(f"missing {label}")
    normalized = str(path)
    if not Path(normalized).exists():
        raise SystemExit(f"{label} not found: {normalized}")
    return normalized


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def is_true(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
