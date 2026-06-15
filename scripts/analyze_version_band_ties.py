from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONTROL_ROOT = Path("data/results/experiments/markor-core-1-9-0-experiment")
DEFAULT_EXPERIMENT_ROOT = Path("data/results/experiments/markor-coverage-gaps-experiment")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/version-band-tie-evidence.json")
DEFAULT_OUTPUT_MARKDOWN = Path("docs/evaluation/VERSION_BAND_TIE_EVIDENCE.md")
DEFAULT_COMPARISON_PATHS = (
    Path("data/results/experiments/app-era-coherence-activity-only-vs-current-control.json"),
    Path("data/results/experiments/app-era-coherence-viewpager-beta-only-vs-current-control.json"),
    Path("data/results/experiments/markor-coverage-gaps-vs-current-control.json"),
    Path("data/results/experiments/markor-core-1-9-0-vs-current-control.json"),
)

RISKY_COORDINATES = {
    "androidx.activity:activity",
    "androidx.concurrent:concurrent-futures",
    "androidx.core:core",
    "androidx.lifecycle:lifecycle-runtime-android",
    "androidx.startup:startup-runtime",
    "androidx.swiperefreshlayout:swiperefreshlayout",
    "androidx.viewpager2:viewpager2",
    "com.squareup.okhttp3:okhttp-android",
    "com.squareup.okio:okio-jvm",
}


@dataclass(frozen=True)
class ExperimentPaths:
    root: Path
    report_dir_prefix: str = "report-real-"

    def report_json(self, case_id: str) -> Path:
        return self.root / f"{self.report_dir_prefix}{case_id}" / "report.json"

    def validation_json(self, case_id: str) -> Path:
        return self.root / "source-validation" / case_id / "source-validation.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize source-validation version mismatches with matcher candidate "
            "evidence, so risky AndroidX/Okio version-band ties can be triaged."
        )
    )
    parser.add_argument("--control-root", default=str(DEFAULT_CONTROL_ROOT))
    parser.add_argument("--experiment-root", default=str(DEFAULT_EXPERIMENT_ROOT))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-markdown", default=str(DEFAULT_OUTPUT_MARKDOWN))
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include all mismatches, not only the current risky coordinate list.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    control = ExperimentPaths(Path(args.control_root))
    experiment = ExperimentPaths(Path(args.experiment_root))
    rows = collect_rows(
        control,
        experiment if experiment.root.exists() else None,
        include_all=args.include_all,
    )
    summary = {
        "control_root": str(control.root),
        "experiment_root": str(experiment.root) if experiment.root.exists() else None,
        "row_count": len(rows),
        "rows": rows,
        "classification_counts": classification_counts(rows),
        "isolated_experiment_comparisons": read_comparisons(DEFAULT_COMPARISON_PATHS),
    }

    output_json = Path(args.output_json)
    output_markdown = Path(args.output_markdown)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_markdown.write_text(build_markdown(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "rows": len(rows),
                "output_json": str(output_json),
                "output_markdown": str(output_markdown),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def collect_rows(
    control: ExperimentPaths,
    experiment: ExperimentPaths | None,
    *,
    include_all: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for validation_path in sorted((control.root / "source-validation").glob("*/source-validation.json")):
        case_id = validation_path.parent.name
        validation = read_json(validation_path)
        report = read_json(control.report_json(case_id))
        experiment_report = (
            read_json(experiment.report_json(case_id))
            if experiment is not None and experiment.report_json(case_id).exists()
            else None
        )
        for result in validation.get("results", []):
            if result.get("kind") != "sbom-component":
                continue
            if result.get("status") not in {"version-mismatch", "missing"}:
                continue
            coordinate = str(result.get("coordinate"))
            if not include_all and coordinate not in RISKY_COORDINATES:
                continue
            rows.append(
                build_row(
                    case_id=case_id,
                    result=result,
                    control_report=report,
                    experiment_report=experiment_report,
                )
            )
    return rows


def build_row(
    *,
    case_id: str,
    result: dict[str, Any],
    control_report: dict[str, Any],
    experiment_report: dict[str, Any] | None,
) -> dict[str, Any]:
    coordinate = str(result.get("coordinate"))
    source_versions = [str(item) for item in result.get("source_versions", [])]
    selected_version = str(result.get("version"))
    decision = find_decision(control_report, coordinate)
    candidates = find_candidates(control_report, coordinate)
    source_candidate = first_source_candidate(candidates, source_versions)
    nearest_source_gap = (
        round(float(candidates[0]["score"]) - float(source_candidate["score"]), 6)
        if candidates and source_candidate is not None
        else None
    )
    experiment_decision = (
        find_decision(experiment_report, coordinate) if experiment_report is not None else None
    )
    experiment_candidates = (
        find_candidates(experiment_report, coordinate) if experiment_report is not None else []
    )
    experiment_source_candidate = first_source_candidate(experiment_candidates, source_versions)

    row = {
        "case_id": case_id,
        "coordinate": coordinate,
        "status": str(result.get("status")),
        "selected_version": selected_version,
        "source_versions": source_versions,
        "selected_score": maybe_round(decision.get("score") if decision else result.get("confidence")),
        "gap_to_next": maybe_round(decision.get("gap_to_next") if decision else None),
        "version_status": decision.get("version_status") if decision else None,
        "version_selection_reason": decision.get("version_selection_reason") if decision else None,
        "source_version_in_control_candidates": source_candidate is not None,
        "nearest_source_gap": nearest_source_gap,
        "top_candidates": summarize_candidates(candidates, source_versions),
        "experiment_selected_version": (
            experiment_decision.get("selected_version") if experiment_decision else None
        ),
        "experiment_selected_score": maybe_round(
            experiment_decision.get("score") if experiment_decision else None
        ),
        "experiment_source_version_in_candidates": experiment_source_candidate is not None,
        "experiment_top_candidates": summarize_candidates(experiment_candidates, source_versions),
    }
    row["classification"] = classify_row(row)
    row["next_action"] = recommend_action(row)
    return row


def classify_row(row: dict[str, Any]) -> str:
    if not row["source_versions"]:
        return "artifact-family-or-source-coordinate-nuance"
    if not row["source_version_in_control_candidates"]:
        if row["experiment_source_version_in_candidates"]:
            if row["experiment_selected_version"] in row["source_versions"]:
                return "missing-reference-coverage-helped-in-experiment"
            return "missing-reference-coverage-but-bytecode-prefers-other-version"
        return "source-version-not-in-reference-db"
    if is_feature_equivalent_tie(row["top_candidates"], row["source_versions"]):
        return "feature-equivalent-version-tie"
    if row["nearest_source_gap"] is not None and row["nearest_source_gap"] <= 0.01:
        return "near-tie-with-source-candidate"
    return "bytecode-evidence-prefers-selected-version"


def recommend_action(row: dict[str, Any]) -> str:
    classification = row["classification"]
    coordinate = row["coordinate"]
    source_versions = set(row.get("source_versions", []))
    if coordinate == "androidx.activity:activity" and "1.6.0" in source_versions:
        return "do not promote globally; Markor coverage-gap experiment regressed AntennaPod"
    if coordinate == "androidx.concurrent:concurrent-futures" and "1.0.0" in source_versions:
        return "do not promote globally; Markor coverage-gap experiment regressed multiple controls"
    if coordinate == "androidx.activity:activity" and "1.9.2" in source_versions:
        return "do not promote globally; Activity-only experiment regressed F-Droid"
    if coordinate == "androidx.viewpager2:viewpager2" and "1.1.0-beta02" in source_versions:
        return "do not promote globally; ViewPager2 beta experiment regressed NewPipe and AntennaPod"
    if classification == "missing-reference-coverage-helped-in-experiment":
        return "candidate for guarded promotion only if full current-control regression stays clean"
    if classification == "missing-reference-coverage-but-bytecode-prefers-other-version":
        return "do not promote alone; source version exists but matcher evidence still prefers another version"
    if classification == "feature-equivalent-version-tie":
        return "consider an ambiguity downgrade or independent dependency/app-era support, not a version force"
    if classification == "near-tie-with-source-candidate":
        return "needs independent evidence; generic recency would regress other cases"
    if classification == "artifact-family-or-source-coordinate-nuance":
        return "handle as coordinate-family/reporting nuance before version calibration"
    if coordinate.startswith("androidx.") or coordinate.startswith("com.squareup.okio"):
        return "keep as documented limitation unless a family-specific signal is found"
    return "outside current risky-tie scope"


def is_feature_equivalent_tie(
    candidates: list[dict[str, Any]],
    source_versions: list[str],
) -> bool:
    if len(candidates) < 2:
        return False
    leader = candidates[0]
    for candidate in candidates[1:4]:
        if candidate["version"] not in source_versions:
            continue
        if abs(float(leader["score"]) - float(candidate["score"])) > 0.001:
            continue
        comparable_fields = [
            "class_score",
            "method_score",
            "dependency_score",
            "literal_score",
            "api_reference_score",
            "unique_version_score",
        ]
        if all(
            abs(float(leader.get(field) or 0.0) - float(candidate.get(field) or 0.0))
            <= 0.001
            for field in comparable_fields
        ):
            return True
    return False


def find_decision(report: dict[str, Any] | None, coordinate: str) -> dict[str, Any] | None:
    if report is None:
        return None
    for decision in report.get("match_summary", {}).get("decisions", []):
        if decision.get("coordinate") == coordinate:
            return decision
    return None


def find_candidates(report: dict[str, Any] | None, coordinate: str) -> list[dict[str, Any]]:
    if report is None:
        return []
    raw_candidates = [
        candidate
        for candidate in report.get("match_summary", {}).get("candidates", [])
        if candidate.get("coordinate") == coordinate
    ]
    candidates_by_version = {
        str(candidate.get("version")): dict(candidate)
        for candidate in raw_candidates
    }
    decision = find_decision(report, coordinate)
    if decision is not None:
        selected_version = str(decision.get("selected_version"))
        candidates_by_version.setdefault(
            selected_version,
            decision_candidate(
                version=selected_version,
                score=decision.get("score"),
                purl=decision.get("purl"),
                evidence=decision.get("evidence"),
            ),
        )
        for alternative in decision.get("alternatives", []):
            version = str(alternative.get("version"))
            candidates_by_version.setdefault(
                version,
                decision_candidate(
                    version=version,
                    score=alternative.get("score"),
                    purl=alternative.get("purl"),
                    evidence=None,
                ),
            )
    return sorted(
        candidates_by_version.values(),
        key=lambda item: float(item.get("score", 0.0)),
        reverse=True,
    )


def decision_candidate(
    *,
    version: str,
    score: Any,
    purl: Any,
    evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "version": version,
        "score": score,
        "purl": purl,
        "evidence": evidence or {},
    }


def first_source_candidate(
    candidates: list[dict[str, Any]],
    source_versions: list[str],
) -> dict[str, Any] | None:
    source_set = set(source_versions)
    for candidate in candidates:
        if str(candidate.get("version")) in source_set:
            return candidate
    return None


def summarize_candidates(
    candidates: list[dict[str, Any]],
    source_versions: list[str],
    *,
    limit: int = 4,
) -> list[dict[str, Any]]:
    source_set = set(source_versions)
    rows = []
    for candidate in candidates[:limit]:
        evidence = candidate.get("evidence", {})
        rows.append(
            {
                "version": str(candidate.get("version")),
                "score": maybe_round(candidate.get("score")),
                "is_source_version": str(candidate.get("version")) in source_set,
                "class_score": maybe_round(evidence.get("class_score")),
                "method_score": maybe_round(evidence.get("method_score")),
                "dependency_score": maybe_round(evidence.get("dependency_score")),
                "literal_score": maybe_round(evidence.get("literal_score")),
                "api_reference_score": maybe_round(evidence.get("api_reference_score")),
                "unique_version_score": maybe_round(evidence.get("unique_version_score")),
                "matched_unique_features": int(evidence.get("matched_unique_classes", 0))
                + int(evidence.get("matched_unique_methods", 0))
                + int(evidence.get("matched_unique_literals", 0)),
            }
        )
    return rows


def classification_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        classification = str(row["classification"])
        counts[classification] = counts.get(classification, 0) + 1
    return dict(sorted(counts.items()))


def read_comparisons(paths: tuple[Path, ...]) -> list[dict[str, Any]]:
    comparisons = []
    for path in paths:
        if not path.exists():
            continue
        data = read_json(path)
        comparisons.append(
            {
                "path": str(path),
                "experiment_label": data.get("experiment_label"),
                "regressed_cases": data.get("regressed_cases", []),
                "improved_cases": data.get("improved_cases", []),
            }
        )
    return comparisons


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Version-Band Tie Evidence",
        "",
        "This audit summarizes current source-validation mismatches for risky AndroidX/Okio "
        "version bands. It is evidence for future matcher rules; it is not source-result "
        "forcing.",
        "",
        f"Control root: `{summary['control_root']}`",
        f"Comparison experiment root: `{summary['experiment_root']}`",
        "",
        "## Classification Counts",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    for classification, count in summary["classification_counts"].items():
        lines.append(f"| {classification} | {count} |")

    if summary.get("isolated_experiment_comparisons"):
        lines.extend(
            [
                "",
                "## Isolated Experiment Results",
                "",
                "| Experiment | Regressed cases | Improved cases | Evidence |",
                "|---|---|---|---|",
            ]
        )
        for comparison in summary["isolated_experiment_comparisons"]:
            lines.append(
                "| "
                f"{comparison['experiment_label']} | "
                f"{', '.join(comparison['regressed_cases']) or 'none'} | "
                f"{', '.join(comparison['improved_cases']) or 'none'} | "
                f"`{comparison['path']}` |"
            )

    lines.extend(
        [
            "",
            "## Mismatch Evidence",
            "",
            "| Case | Coordinate | MVP | Source | Gap | Classification | Next action |",
            "|---|---|---:|---|---:|---|---|",
        ]
    )
    for row in summary["rows"]:
        lines.append(
            "| "
            f"{row['case_id']} | "
            f"`{row['coordinate']}` | "
            f"{row['selected_version']} | "
            f"{', '.join(row['source_versions']) or 'not found'} | "
            f"{format_optional(row['nearest_source_gap'])} | "
            f"{row['classification']} | "
            f"{row['next_action']} |"
        )

    lines.extend(["", "## Candidate Details", ""])
    for row in summary["rows"]:
        lines.extend(
            [
                f"### {row['case_id']} - `{row['coordinate']}`",
                "",
                f"- Current selected: `{row['selected_version']}` "
                f"(score {format_optional(row['selected_score'])}, "
                f"status {row['version_status'] or 'unknown'})",
                f"- Source version(s): `{', '.join(row['source_versions']) or 'not found'}`",
                f"- Classification: {row['classification']}",
                f"- Next action: {row['next_action']}",
                "",
                "| Version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |",
                "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for candidate in row["top_candidates"]:
            lines.append(candidate_markdown_row(candidate))
        if row["experiment_top_candidates"]:
            lines.extend(
                [
                    "",
                    f"Full experiment selected: `{row['experiment_selected_version']}` "
                    f"(score {format_optional(row['experiment_selected_score'])})",
                    "",
                    "| Experiment version | Score | Source? | Class | Method | Dependency | Literal | API | Unique | Matched unique |",
                    "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
                ]
            )
            for candidate in row["experiment_top_candidates"]:
                lines.append(candidate_markdown_row(candidate))
        lines.append("")
    return "\n".join(lines)


def candidate_markdown_row(candidate: dict[str, Any]) -> str:
    return (
        "| "
        f"{candidate['version']} | "
        f"{format_optional(candidate['score'])} | "
        f"{'yes' if candidate['is_source_version'] else 'no'} | "
        f"{format_optional(candidate['class_score'])} | "
        f"{format_optional(candidate['method_score'])} | "
        f"{format_optional(candidate['dependency_score'])} | "
        f"{format_optional(candidate['literal_score'])} | "
        f"{format_optional(candidate['api_reference_score'])} | "
        f"{format_optional(candidate['unique_version_score'])} | "
        f"{candidate['matched_unique_features']} |"
    )


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def maybe_round(value: Any) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def format_optional(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
