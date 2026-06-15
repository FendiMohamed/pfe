from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apk_sbom.report import generate_final_report
from apk_sbom.source_validation import (
    parse_maven_component_spec,
    write_source_validation_report,
)


DEFAULT_DB_PATH = Path("data/reference_db/reference_features_nextcloud_experiment_combined.sqlite")
DEFAULT_OUTPUT_ROOT = Path("data/results/experiments/nextcloud-source-versions")
DEFAULT_EXPERIMENT_TITLE = "Nextcloud source-used version experiment"
DEFAULT_SUMMARY_STEM = "nextcloud-source-versions-summary"


@dataclass(frozen=True)
class RegressionCase:
    case_id: str
    apk_path: str
    dependency_tree: str
    baseline_validation: str
    extra_candidates: tuple[str, ...] = ()


CASES = (
    RegressionCase(
        case_id="fdroid",
        apk_path="data/test_apks/real/F-Droid.apk",
        dependency_tree="data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/fdroid-final-demo-osv/source-validation.json",
        extra_candidates=("com.squareup.okio:okio@2.8.0",),
    ),
    RegressionCase(
        case_id="opentracks",
        apk_path="data/test_apks/real/opentracks/opentracks.apk",
        dependency_tree="data/results/source-validation/opentracks/fullReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/opentracks-calibrated-db/source-validation.json",
    ),
    RegressionCase(
        case_id="tusky",
        apk_path="data/test_apks/real/tusky/tusky.apk",
        dependency_tree="data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/tusky-calibrated-db/source-validation.json",
    ),
    RegressionCase(
        case_id="newpipe",
        apk_path="data/test_apks/real/newpipe/newpipe.apk",
        dependency_tree="data/results/source-validation/newpipe/releaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/newpipe-calibrated-db/source-validation.json",
    ),
    RegressionCase(
        case_id="antennapod",
        apk_path="data/test_apks/real/antennapod/antennapod.apk",
        dependency_tree="data/results/source-validation/antennapod/freeReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/antennapod-report-validation/source-validation.json",
    ),
    RegressionCase(
        case_id="kde-connect",
        apk_path="data/test_apks/real/kde-connect/kde-connect.apk",
        dependency_tree="data/results/source-validation/kde-connect/releaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/kde-connect-validation/source-validation.json",
    ),
    RegressionCase(
        case_id="wikipedia-android",
        apk_path="data/test_apks/real/wikipedia-android/wikipedia-android.apk",
        dependency_tree="data/results/source-validation/wikipedia-android/fdroidReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/wikipedia-android-report-validation/source-validation.json",
    ),
    RegressionCase(
        case_id="conversations",
        apk_path="data/test_apks/real/conversations/conversations.apk",
        dependency_tree=(
            "data/results/source-validation/conversations/"
            "conversationsFreeReleaseRuntimeClasspath.txt"
        ),
        baseline_validation="data/results/source-validation/conversations-report-validation/source-validation.json",
    ),
    RegressionCase(
        case_id="aegis-authenticator",
        apk_path="data/test_apks/real/aegis-authenticator/aegis-authenticator.apk",
        dependency_tree="data/results/source-validation/aegis-authenticator/releaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/aegis-authenticator-report-validation/source-validation.json",
    ),
    RegressionCase(
        case_id="markor",
        apk_path="data/test_apks/real/markor/markor.apk",
        dependency_tree="data/results/source-validation/markor/flavorDefaultReleaseRuntimeClasspath.txt",
        baseline_validation="data/results/source-validation/markor-report-validation/source-validation.json",
    ),
    RegressionCase(
        case_id="nextcloud-android",
        apk_path="data/test_apks/real/nextcloud-android/nextcloud.apk",
        dependency_tree=(
            "data/results/source-validation/nextcloud-android/"
            "genericReleaseRuntimeClasspath.txt"
        ),
        baseline_validation=(
            "data/results/source-validation/nextcloud-android-report-validation/"
            "source-validation.json"
        ),
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a guarded regression experiment for the Nextcloud source-used "
            "version reference DB."
        ),
    )
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--min-score", type=float, default=0.05)
    parser.add_argument("--case", action="append", help="Run only this case id. Can be repeated.")
    parser.add_argument(
        "--experiment-title",
        default=DEFAULT_EXPERIMENT_TITLE,
        help="Title used in the generated Markdown summary.",
    )
    parser.add_argument(
        "--summary-stem",
        default=DEFAULT_SUMMARY_STEM,
        help="Filename stem for the generated JSON and Markdown summary files.",
    )
    parser.add_argument(
        "--reuse-existing",
        action="store_true",
        help="Reuse existing report/source-validation JSON files when present.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    selected = set(args.case or [])
    cases = [case for case in CASES if not selected or case.case_id in selected]
    if selected and len(cases) != len(selected):
        known = {case.case_id for case in CASES}
        missing = sorted(selected - known)
        raise SystemExit(f"unknown case id(s): {', '.join(missing)}")

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
        "rows": rows,
    }
    json_path = output_root / f"{args.summary_stem}.json"
    markdown_path = output_root / f"{args.summary_stem}.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(build_markdown(summary), encoding="utf-8")

    print(
        json.dumps(
            {
                "rows": len(rows),
                "summary_json": str(json_path),
                "summary_markdown": str(markdown_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def run_case(
    case: RegressionCase,
    *,
    db_path: str,
    output_root: Path,
    top: int,
    min_score: float,
    reuse_existing: bool = False,
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
        extra_candidates = [
            parse_maven_component_spec(candidate)
            for candidate in case.extra_candidates
        ]
        validation_artifacts = write_source_validation_report(
            sbom_json,
            case.dependency_tree,
            output_dir=validation_dir,
            extra_candidates=extra_candidates,
        )
        validation_json = validation_artifacts.validation_json
    report = read_json(report_json)
    validation = read_json(validation_json)
    baseline = read_json(case.baseline_validation)
    return {
        "case_id": case.case_id,
        "detected_components": len(report.get("detected_components", [])),
        "confirmed": validation["confirmed"],
        "version_mismatches": validation["version_mismatches"],
        "missing": validation["missing"],
        "candidate_version_mismatches": validation["candidate_version_mismatches"],
        "baseline_confirmed": baseline["confirmed"],
        "baseline_version_mismatches": baseline["version_mismatches"],
        "baseline_missing": baseline["missing"],
        "delta_confirmed": validation["confirmed"] - baseline["confirmed"],
        "delta_version_mismatches": (
            validation["version_mismatches"] - baseline["version_mismatches"]
        ),
        "delta_missing": validation["missing"] - baseline["missing"],
        "mismatches": summarize_results(validation, {"version-mismatch", "missing"}),
        "baseline_mismatches": summarize_results(baseline, {"version-mismatch", "missing"}),
        "report_dir": str(report_dir),
        "validation_dir": str(validation_dir),
    }


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


def build_markdown(summary: dict[str, Any]) -> str:
    title = summary.get("experiment_title") or DEFAULT_EXPERIMENT_TITLE
    lines = [
        f"# {title}",
        "",
        f"DB: `{summary['db_path']}`",
        "",
        "| Case | Components | Confirmed | Mismatches | Missing | Delta |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in summary["rows"]:
        delta = (
            f"{row['delta_confirmed']:+d} confirmed, "
            f"{row['delta_version_mismatches']:+d} mismatches, "
            f"{row['delta_missing']:+d} missing"
        )
        lines.append(
            "| "
            f"{row['case_id']} | "
            f"{row['detected_components']} | "
            f"{row['confirmed']} | "
            f"{row['version_mismatches']} | "
            f"{row['missing']} | "
            f"{delta} |"
        )

    lines.extend(["", "## Remaining Mismatches", ""])
    for row in summary["rows"]:
        if not row["mismatches"]:
            continue
        lines.extend([f"### {row['case_id']}", ""])
        lines.extend(
            [
                "| Component | MVP version | Source versions | Status |",
                "|---|---:|---|---|",
            ]
        )
        for mismatch in row["mismatches"]:
            lines.append(
                "| "
                f"`{mismatch['coordinate']}` | "
                f"{mismatch['version']} | "
                f"{mismatch['source_versions']} | "
                f"{mismatch['status']} |"
            )
        lines.append("")
    return "\n".join(lines)


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


if __name__ == "__main__":
    raise SystemExit(main())
