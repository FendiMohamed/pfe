from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from apk_sbom.report import generate_final_report
from apk_sbom.source_validation import (
    parse_maven_component_spec,
    write_source_validation_report,
)


DEFAULT_DB_PATH = Path("data/reference_db/reference_features_calibrated_combined_api_refs.sqlite")
DEFAULT_OUTPUT_ROOT = Path("data/results/experiments/api-reference-weight")


@dataclass(frozen=True)
class ExperimentCase:
    case_id: str
    apk_path: str
    dependency_tree: str
    extra_candidates: tuple[str, ...] = ()


CASES = (
    ExperimentCase(
        case_id="fdroid",
        apk_path="data/test_apks/real/F-Droid.apk",
        dependency_tree="data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt",
        extra_candidates=("com.squareup.okio:okio@2.8.0",),
    ),
    ExperimentCase(
        case_id="opentracks",
        apk_path="data/test_apks/real/opentracks/opentracks.apk",
        dependency_tree="data/results/source-validation/opentracks/fullReleaseRuntimeClasspath.txt",
    ),
    ExperimentCase(
        case_id="aegis-authenticator",
        apk_path="data/test_apks/real/aegis-authenticator/aegis-authenticator.apk",
        dependency_tree="data/results/source-validation/aegis-authenticator/releaseRuntimeClasspath.txt",
    ),
    ExperimentCase(
        case_id="markor",
        apk_path="data/test_apks/real/markor/markor.apk",
        dependency_tree="data/results/source-validation/markor/flavorDefaultReleaseRuntimeClasspath.txt",
    ),
    ExperimentCase(
        case_id="newpipe",
        apk_path="data/test_apks/real/newpipe/newpipe.apk",
        dependency_tree="data/results/source-validation/newpipe/releaseRuntimeClasspath.txt",
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run guarded source-validation experiments for API/member-reference weights.",
    )
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument(
        "--weights",
        nargs="+",
        type=float,
        default=[0.0, 0.05],
        help="API/member-reference weights to evaluate.",
    )
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--min-score", type=float, default=0.05)
    parser.add_argument(
        "--near-tie-threshold",
        type=float,
        default=0.001,
        help="Report version decisions with a score gap at or below this value.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for weight in args.weights:
        weight_label = format_weight_label(weight)
        for case in CASES:
            print(f"running {case.case_id} with api_reference_weight={weight}")
            row = run_case(
                case,
                weight=weight,
                weight_label=weight_label,
                db_path=args.db_path,
                output_root=output_root,
                top=args.top,
                min_score=args.min_score,
                near_tie_threshold=args.near_tie_threshold,
            )
            rows.append(row)

    summary = build_summary(rows)
    json_path = output_root / "api-reference-weight-summary.json"
    markdown_path = output_root / "api-reference-weight-summary.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(build_markdown(summary), encoding="utf-8")

    print(
        json.dumps(
            {
                "summary_json": str(json_path),
                "summary_markdown": str(markdown_path),
                "rows": len(rows),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def run_case(
    case: ExperimentCase,
    *,
    weight: float,
    weight_label: str,
    db_path: str,
    output_root: Path,
    top: int,
    min_score: float,
    near_tie_threshold: float,
) -> dict:
    report_dir = output_root / f"weight-{weight_label}" / f"report-real-{case.case_id}"
    validation_dir = output_root / f"weight-{weight_label}" / "source-validation" / case.case_id
    artifacts = generate_final_report(
        case.apk_path,
        output_dir=report_dir,
        db_path=db_path,
        top=top,
        min_score=min_score,
        query_osv=False,
        api_reference_weight=weight,
    )
    extra_candidates = [
        parse_maven_component_spec(candidate)
        for candidate in case.extra_candidates
    ]
    validation_artifacts = write_source_validation_report(
        artifacts.sbom_json,
        case.dependency_tree,
        output_dir=validation_dir,
        extra_candidates=extra_candidates,
    )
    report = read_json(artifacts.report_json)
    matches = read_json(artifacts.matches_json)
    validation = read_json(validation_artifacts.validation_json)

    return {
        "case_id": case.case_id,
        "api_reference_weight": weight,
        "detected_components": len(report.get("detected_components", [])),
        "confirmed": validation["confirmed"],
        "version_mismatches": validation["version_mismatches"],
        "missing": validation["missing"],
        "candidate_version_mismatches": validation["candidate_version_mismatches"],
        "apk_api_references": matches.get("apk_api_references", 0),
        "candidates_with_api_matches": count_candidates_with_api_matches(matches),
        "total_matched_api_references": sum_matched_api_references(matches),
        "mismatches": summarize_mismatches(validation),
        "near_ties": summarize_near_ties(report, near_tie_threshold),
        "report_dir": str(report_dir),
        "validation_dir": str(validation_dir),
    }


def build_summary(rows: list[dict]) -> dict:
    baseline_by_case = {
        row["case_id"]: row
        for row in rows
        if row["api_reference_weight"] == 0.0
    }
    enriched_rows = []
    for row in rows:
        baseline = baseline_by_case.get(row["case_id"])
        row_with_delta = dict(row)
        if baseline and row["api_reference_weight"] != 0.0:
            row_with_delta["delta_confirmed"] = row["confirmed"] - baseline["confirmed"]
            row_with_delta["delta_version_mismatches"] = (
                row["version_mismatches"] - baseline["version_mismatches"]
            )
            row_with_delta["delta_missing"] = row["missing"] - baseline["missing"]
            row_with_delta["changed_mismatches"] = row["mismatches"] != baseline["mismatches"]
        enriched_rows.append(row_with_delta)
    return {
        "rows": enriched_rows,
        "case_count": len({row["case_id"] for row in rows}),
        "weights": sorted({row["api_reference_weight"] for row in rows}),
    }


def build_markdown(summary: dict) -> str:
    lines = [
        "# API/member-reference weight experiment",
        "",
        "| Case | Weight | Components | Confirmed | Mismatches | Missing | API matched candidates | API matches | Delta |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary["rows"]:
        delta = ""
        if row["api_reference_weight"] != 0.0:
            delta = (
                f"{row.get('delta_confirmed', 0):+d} confirmed, "
                f"{row.get('delta_version_mismatches', 0):+d} mismatches, "
                f"{row.get('delta_missing', 0):+d} missing"
            )
        lines.append(
            "| "
            f"{row['case_id']} | "
            f"{row['api_reference_weight']:.3f} | "
            f"{row['detected_components']} | "
            f"{row['confirmed']} | "
            f"{row['version_mismatches']} | "
            f"{row['missing']} | "
            f"{row['candidates_with_api_matches']} | "
            f"{row['total_matched_api_references']} | "
            f"{delta} |"
        )

    lines.extend(["", "## Mismatches", ""])
    for row in summary["rows"]:
        if not row["mismatches"]:
            continue
        lines.append(f"### {row['case_id']} weight {row['api_reference_weight']:.3f}")
        for mismatch in row["mismatches"]:
            lines.append(f"- `{mismatch}`")
        lines.append("")

    lines.extend(["", "## Near-Tie Version Decisions", ""])
    for row in summary["rows"]:
        if not row["near_ties"]:
            continue
        lines.append(f"### {row['case_id']} weight {row['api_reference_weight']:.3f}")
        for tie in row["near_ties"]:
            alternatives = ", ".join(
                f"{alternative['version']}:{alternative['score']:.6f}"
                for alternative in tie["alternatives"]
            )
            lines.append(
                f"- `{tie['coordinate']}` selected `{tie['selected_version']}` "
                f"({tie['version_decision']}, score {tie['score']:.6f}, "
                f"gap {tie['gap_to_next']:.6f}); alternatives: {alternatives}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def summarize_mismatches(validation: dict) -> list[str]:
    mismatches = []
    for result in validation.get("results", []):
        if result.get("kind") != "sbom-component":
            continue
        if result.get("status") != "version-mismatch":
            continue
        source_versions = ",".join(result.get("source_versions", []))
        mismatches.append(
            f"{result['coordinate']} selected {result['version']} vs source {source_versions}"
        )
    return mismatches


def summarize_near_ties(report: dict, threshold: float) -> list[dict]:
    ties = []
    for decision in report.get("match_summary", {}).get("decisions", []):
        alternatives = decision.get("alternatives", [])
        if not alternatives:
            continue
        gap = decision.get("gap_to_next", 0.0)
        if gap > threshold:
            continue
        ties.append(
            {
                "coordinate": decision["coordinate"],
                "selected_version": decision["selected_version"],
                "version_decision": decision["version_decision"],
                "score": decision["score"],
                "gap_to_next": gap,
                "alternatives": alternatives[:3],
            }
        )
    return ties


def count_candidates_with_api_matches(matches: dict) -> int:
    return sum(
        1
        for candidate in matches.get("candidates", [])
        if candidate.get("evidence", {}).get("matched_api_references", 0) > 0
    )


def sum_matched_api_references(matches: dict) -> int:
    return sum(
        candidate.get("evidence", {}).get("matched_api_references", 0)
        for candidate in matches.get("candidates", [])
    )


def format_weight_label(weight: float) -> str:
    label = f"{weight:.3f}".rstrip("0").rstrip(".")
    return label.replace(".", "p") if label else "0"


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
