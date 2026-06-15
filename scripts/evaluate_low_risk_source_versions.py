from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apk_sbom.report import generate_final_report
from apk_sbom.source_validation import write_source_validation_report


DEFAULT_DB_PATH = Path("data/reference_db/reference_features_low_risk_source_experiment.sqlite")
DEFAULT_OUTPUT_ROOT = Path("data/results/experiments/low-risk-source-versions")
DEFAULT_EXPERIMENT_TITLE = "Low-risk source-used version reference experiment"
DEFAULT_SUMMARY_STEM = "low-risk-source-versions-summary"


@dataclass(frozen=True)
class RegressionCase:
    case_id: str
    apk_path: str
    dependency_tree: str
    baseline_validation: str
    role: str


CASES = (
    RegressionCase(
        case_id="stopwatch",
        apk_path="data/test_apks/real/stopwatch/stopwatch.apk",
        dependency_tree=(
            "data/results/source-validation/low-risk-real-apk-batch/"
            "stopwatch/root1-app-dependencies-releaseRuntimeClasspath.txt"
        ),
        baseline_validation=(
            "data/results/source-validation/low-risk-real-apk-batch/"
            "stopwatch/source-validation/source-validation.json"
        ),
        role="target",
    ),
    RegressionCase(
        case_id="bubble",
        apk_path="data/test_apks/real/bubble/bubble.apk",
        dependency_tree=(
            "data/results/source-validation/low-risk-real-apk-batch/"
            "bubble/root1-app-dependencies-releaseRuntimeClasspath.txt"
        ),
        baseline_validation=(
            "data/results/source-validation/low-risk-real-apk-batch/"
            "bubble/source-validation/source-validation.json"
        ),
        role="target",
    ),
    RegressionCase(
        case_id="audio-source",
        apk_path="data/test_apks/real/audio-source/audio-source.apk",
        dependency_tree=(
            "data/results/source-validation/low-risk-real-apk-batch/"
            "audio-source/root1-app-dependencies-releaseRuntimeClasspath.txt"
        ),
        baseline_validation=(
            "data/results/source-validation/low-risk-real-apk-batch/"
            "audio-source/source-validation/source-validation.json"
        ),
        role="target",
    ),
    RegressionCase(
        case_id="blue-square-speedometer",
        apk_path="data/test_apks/real/blue-square-speedometer/blue-square-speedometer.apk",
        dependency_tree=(
            "data/results/source-validation/low-risk-real-apk-batch/"
            "blue-square-speedometer/root1-app-dependencies-releaseRuntimeClasspath.txt"
        ),
        baseline_validation=(
            "data/results/source-validation/low-risk-real-apk-batch/"
            "blue-square-speedometer/source-validation/source-validation.json"
        ),
        role="target-no-maven-signal",
    ),
    RegressionCase(
        case_id="fdroid",
        apk_path="data/test_apks/real/F-Droid.apk",
        dependency_tree="data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/fdroid-final-demo-osv/source-validation.json",
        role="control-clean",
    ),
    RegressionCase(
        case_id="opentracks",
        apk_path="data/test_apks/real/opentracks/opentracks.apk",
        dependency_tree="data/results/source-validation/opentracks/fullReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/opentracks-calibrated-db/source-validation.json",
        role="control-clean",
    ),
    RegressionCase(
        case_id="tusky",
        apk_path="data/test_apks/real/tusky/tusky.apk",
        dependency_tree="data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/tusky-calibrated-db/source-validation.json",
        role="control-clean-sparse",
    ),
    RegressionCase(
        case_id="newpipe",
        apk_path="data/test_apks/real/newpipe/newpipe.apk",
        dependency_tree="data/results/source-validation/newpipe/releaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/newpipe-calibrated-db/source-validation.json",
        role="control-partial",
    ),
    RegressionCase(
        case_id="antennapod",
        apk_path="data/test_apks/real/antennapod/antennapod.apk",
        dependency_tree="data/results/source-validation/antennapod/freeReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/antennapod-report-validation/source-validation.json",
        role="control-partial",
    ),
    RegressionCase(
        case_id="kde-connect",
        apk_path="data/test_apks/real/kde-connect/kde-connect.apk",
        dependency_tree="data/results/source-validation/kde-connect/releaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/kde-connect-validation/source-validation.json",
        role="control-partial",
    ),
    RegressionCase(
        case_id="aegis-authenticator",
        apk_path="data/test_apks/real/aegis-authenticator/aegis-authenticator.apk",
        dependency_tree="data/results/source-validation/aegis-authenticator/releaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/aegis-authenticator-report-validation/source-validation.json",
        role="control-partial",
    ),
    RegressionCase(
        case_id="markor",
        apk_path="data/test_apks/real/markor/markor.apk",
        dependency_tree="data/results/source-validation/markor/flavorDefaultReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/markor-report-validation/source-validation.json",
        role="control-partial",
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the low-risk source-used version reference DB experiment.",
    )
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--min-score", type=float, default=0.05)
    parser.add_argument("--case", action="append", help="Run only this case id. Can be repeated.")
    parser.add_argument("--role", action="append", help="Run only cases with this role. Can be repeated.")
    parser.add_argument("--experiment-title", default=DEFAULT_EXPERIMENT_TITLE)
    parser.add_argument("--summary-stem", default=DEFAULT_SUMMARY_STEM)
    parser.add_argument("--reuse-existing", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cases = select_cases(args.case, args.role)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for case in cases:
        print(f"running {case.case_id}")
        rows.append(
            run_case(
                case,
                db_path=args.db_path,
                output_root=output_root,
                top=args.top,
                min_score=args.min_score,
                reuse_existing=args.reuse_existing,
            )
        )

    summary = {
        "db_path": args.db_path,
        "experiment_title": args.experiment_title,
        "case_count": len(rows),
        "candidate_versions": candidate_versions(),
        "rows": rows,
        "regressed_cases": [row["case_id"] for row in rows if row["regressed_vs_baseline"]],
        "improved_cases": [row["case_id"] for row in rows if row["improved_vs_baseline"]],
    }
    json_path = output_root / f"{args.summary_stem}.json"
    markdown_path = output_root / f"{args.summary_stem}.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "summary_json": str(json_path), "summary_markdown": str(markdown_path)}, indent=2, sort_keys=True))
    return 0


def select_cases(case_ids: list[str] | None, roles: list[str] | None) -> list[RegressionCase]:
    selected_ids = set(case_ids or [])
    selected_roles = set(roles or [])
    cases = [
        case
        for case in CASES
        if (not selected_ids or case.case_id in selected_ids)
        and (not selected_roles or case.role in selected_roles)
    ]
    if selected_ids:
        known = {case.case_id for case in CASES}
        missing = sorted(selected_ids - known)
        if missing:
            raise SystemExit(f"unknown case id(s): {', '.join(missing)}")
    if not cases:
        raise SystemExit("no cases selected")
    return cases


def run_case(
    case: RegressionCase,
    *,
    db_path: str,
    output_root: Path,
    top: int,
    min_score: float,
    reuse_existing: bool,
) -> dict[str, Any]:
    report_dir = output_root / f"report-real-{case.case_id}"
    validation_dir = output_root / "source-validation" / case.case_id
    report_json = report_dir / "report.json"
    validation_json = validation_dir / "source-validation.json"
    if not reuse_existing or not report_json.exists():
        artifacts = generate_final_report(
            case.apk_path,
            output_dir=report_dir,
            db_path=db_path,
            top=top,
            min_score=min_score,
            query_osv=False,
        )
        report_json = artifacts.report_json
    if not reuse_existing or not validation_json.exists():
        sbom_json = report_dir / "sbom.cdx.json"
        validation_artifacts = write_source_validation_report(
            sbom_json,
            case.dependency_tree,
            output_dir=validation_dir,
        )
        validation_json = validation_artifacts.validation_json

    report = read_json(report_json)
    validation = read_json(validation_json)
    baseline = read_json(case.baseline_validation)
    row = {
        "case_id": case.case_id,
        "role": case.role,
        "detected_components": len(report.get("detected_components", [])),
        "confirmed": validation["confirmed"],
        "version_mismatches": validation["version_mismatches"],
        "missing": validation["missing"],
        "baseline_confirmed": baseline["confirmed"],
        "baseline_version_mismatches": baseline["version_mismatches"],
        "baseline_missing": baseline["missing"],
        "delta_confirmed": validation["confirmed"] - baseline["confirmed"],
        "delta_version_mismatches": validation["version_mismatches"] - baseline["version_mismatches"],
        "delta_missing": validation["missing"] - baseline["missing"],
        "mismatches": summarize_results(validation, {"version-mismatch", "missing"}),
        "baseline_mismatches": summarize_results(baseline, {"version-mismatch", "missing"}),
        "report_dir": str(report_dir),
        "validation_dir": str(validation_dir),
    }
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
    return row


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


def candidate_versions() -> list[str]:
    return [
        "androidx.appcompat:appcompat:1.2.0",
        "androidx.appcompat:appcompat:1.6.1",
        "androidx.core:core:1.3.0",
        "androidx.fragment:fragment:1.3.6",
        "androidx.lifecycle:lifecycle-runtime:2.1.0",
        "androidx.lifecycle:lifecycle-runtime:2.5.1",
        "androidx.lifecycle:lifecycle-viewmodel:2.5.1",
        "androidx.recyclerview:recyclerview:1.0.0",
        "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.1",
        "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.4",
    ]


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"# {summary['experiment_title']}",
        "",
        f"DB: `{summary['db_path']}`",
        "",
        "## Candidate Versions",
        "",
    ]
    lines.extend(f"- `{version}`" for version in summary["candidate_versions"])
    lines.extend(
        [
            "",
            "## Case Results",
            "",
            "| Case | Role | Components | Confirmed | Mismatches | Missing | Delta vs baseline | Status |",
            "|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in summary["rows"]:
        status = "regressed" if row["regressed_vs_baseline"] else "unchanged"
        if row["improved_vs_baseline"] and not row["regressed_vs_baseline"]:
            status = "improved"
        delta = (
            f"{row['delta_confirmed']:+d} confirmed, "
            f"{row['delta_version_mismatches']:+d} mismatches, "
            f"{row['delta_missing']:+d} missing"
        )
        lines.append(
            "| "
            f"{row['case_id']} | "
            f"{row['role']} | "
            f"{row['detected_components']} | "
            f"{row['confirmed']} | "
            f"{row['version_mismatches']} | "
            f"{row['missing']} | "
            f"{delta} | "
            f"{status} |"
        )
    lines.extend(["", "## Remaining Mismatches", ""])
    for row in summary["rows"]:
        if not row["mismatches"]:
            continue
        lines.extend([f"### {row['case_id']}", ""])
        lines.extend(["| Component | MVP version | Source versions | Status |", "|---|---:|---|---|"])
        for mismatch in row["mismatches"]:
            lines.append(
                "| "
                f"`{mismatch['coordinate']}` | "
                f"{mismatch['version']} | "
                f"{mismatch['source_versions']} | "
                f"{mismatch['status']} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


if __name__ == "__main__":
    raise SystemExit(main())
