from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_DASHBOARD_JSON = Path("data/results/evaluation/real-apk-source-validation-dashboard.json")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/no-maven-signal-diagnostics.json")
DEFAULT_OUTPUT_CSV = Path("data/results/evaluation/no-maven-signal-diagnostics.csv")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/NO_MAVEN_SIGNAL_DIAGNOSTICS.md")

COORD_RE = re.compile(
    r"(?P<group>[A-Za-z0-9_.-]+(?:\.[A-Za-z0-9_.-]+)+):"
    r"(?P<artifact>[A-Za-z0-9_.-]+):"
    r"(?P<version>[A-Za-z0-9_.+\-\[\](),]+)"
)


TREE_OVERRIDES = {
    "Privacy Browser 3.20.1": "data/results/source-validation/csv4/privacy-browser/docker-app-standardReleaseRuntimeClasspath-gradle9.5.txt",
    "Mastodon 2.12.3": "data/results/source-validation/csv7/mastodon/docker-mastodon-releaseRuntimeClasspath-gradle8.13.txt",
    "monocles browser 1.9.3": "data/results/source-validation/csv8/monocles-browser/root1-app-dependencies-standardReleaseRuntimeClasspath.txt",
    "Blue Square Speedometer 1.1.0": "data/results/source-validation/low-risk-real-apk-batch/blue-square-speedometer/root1-app-dependencies-releaseRuntimeClasspath.txt",
}

CLASSIFICATION_OVERRIDES = {
    "Privacy Browser 3.20.1": (
        "identity-coverage-miss",
        "Browser/WebView AndroidX diagnostic",
    ),
    "Mastodon 2.12.3": (
        "forked-library-boundary",
        "me.grishka.litex fork-family/reference audit plus weak Gson check",
    ),
    "monocles browser 1.9.3": (
        "identity-coverage-miss",
        "Browser/WebView AndroidX diagnostic",
    ),
    "Blue Square Speedometer 1.1.0": (
        "identity-coverage-miss",
        "Small-app AndroidX diagnostic",
    ),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build no-Maven-signal diagnostics from source-validation and report evidence.",
    )
    parser.add_argument("--dashboard-json", default=str(DEFAULT_DASHBOARD_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    dashboard_path = Path(args.dashboard_json)
    dashboard = read_json(dashboard_path)
    rows = [
        build_row(case)
        for case in dashboard.get("cases", [])
        if case.get("role") == "source-validated-no-maven-signal"
    ]
    summary = build_summary(rows)
    payload = {
        "schema_version": 1,
        "source": normalize_path(dashboard_path),
        "summary": summary,
        "cases": rows,
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    write_csv(Path(args.output_csv), rows)

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "cases": len(rows),
                "json": normalize_path(output_json),
                "csv": normalize_path(Path(args.output_csv)),
                "doc": normalize_path(output_doc),
                **summary,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_row(case: dict[str, Any]) -> dict[str, Any]:
    name = case["name"]
    paths = case.get("paths", {})
    validation_stats = case.get("validation_stats", {})
    report_path = Path(paths["report"])
    tree_path = Path(validation_stats.get("dependency_tree_path") or TREE_OVERRIDES[name])
    report = read_json(report_path)
    candidates = report.get("match_summary", {}).get("candidates", [])
    source_coords = parse_source_coordinates(tree_path)
    candidate_coords = sorted({candidate.get("coordinate", "") for candidate in candidates})
    overlap = sorted(set(candidate_coords) & set(source_coords))
    top_candidate = max(candidates, key=lambda candidate: candidate.get("score", 0.0), default={})
    top_overlap = best_overlap_candidate(candidates, overlap)
    classification, lane = CLASSIFICATION_OVERRIDES[name]
    return {
        "apk": name,
        "classification": classification,
        "recommended_lane": lane,
        "detected_components": len(report.get("detected_components", [])),
        "report_candidate_count": len(candidates),
        "source_coordinate_count": len(source_coords),
        "candidate_coordinate_count": len(candidate_coords),
        "source_candidate_overlap_count": len(overlap),
        "source_candidate_overlap_total": len(candidate_coords),
        "source_candidate_overlap_coordinates": overlap,
        "top_candidate_coordinate": top_candidate.get("coordinate"),
        "top_candidate_version": top_candidate.get("version"),
        "top_candidate_score": top_candidate.get("score"),
        "top_overlap_coordinate": top_overlap.get("coordinate"),
        "top_overlap_version": top_overlap.get("version"),
        "top_overlap_score": top_overlap.get("score"),
        "report": normalize_path(report_path),
        "dependency_tree": normalize_path(tree_path),
    }


def parse_source_coordinates(path: Path) -> list[str]:
    coordinates: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = COORD_RE.search(line)
        if not match:
            continue
        coordinates.add(f"{match.group('group')}:{match.group('artifact')}")
    return sorted(coordinates)


def best_overlap_candidate(candidates: list[dict[str, Any]], overlap: list[str]) -> dict[str, Any]:
    overlap_set = set(overlap)
    matching = [candidate for candidate in candidates if candidate.get("coordinate") in overlap_set]
    return max(matching, key=lambda candidate: candidate.get("score", 0.0), default={})


def build_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "no_maven_signal_cases": len(rows),
        "true_no_signal_controls": sum(
            row["classification"] == "true-no-signal-control" for row in rows
        ),
        "identity_coverage_miss_controls": sum(
            row["classification"] == "identity-coverage-miss" for row in rows
        ),
        "forked_library_boundary_cases": sum(
            row["classification"] == "forked-library-boundary" for row in rows
        ),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "apk",
        "classification",
        "recommended_lane",
        "detected_components",
        "report_candidate_count",
        "source_coordinate_count",
        "candidate_coordinate_count",
        "source_candidate_overlap_count",
        "source_candidate_overlap_total",
        "top_candidate_coordinate",
        "top_candidate_version",
        "top_candidate_score",
        "top_overlap_coordinate",
        "top_overlap_version",
        "top_overlap_score",
        "report",
        "dependency_tree",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# No-Maven-Signal Diagnostics",
        "",
        f"Generated from `{payload['source']}`.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| No-Maven-signal cases | {summary['no_maven_signal_cases']} |",
        f"| True no-signal controls | {summary['true_no_signal_controls']} |",
        f"| Identity-coverage miss controls | {summary['identity_coverage_miss_controls']} |",
        f"| Forked-library boundary cases | {summary['forked_library_boundary_cases']} |",
        "",
        "## Cases",
        "",
        "| APK | Classification | Source coords | Candidate coords | Overlap | Top candidate | Top overlap | Lane |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]
    for row in payload["cases"]:
        top_candidate = format_candidate(
            row["top_candidate_coordinate"],
            row["top_candidate_version"],
            row["top_candidate_score"],
        )
        top_overlap = format_candidate(
            row["top_overlap_coordinate"],
            row["top_overlap_version"],
            row["top_overlap_score"],
        )
        lines.append(
            "| {apk} | {classification} | {source_coordinate_count} | "
            "{candidate_coordinate_count} | {source_candidate_overlap_count}/{source_candidate_overlap_total} | "
            "{top_candidate} | {top_overlap} | {recommended_lane} |".format(
                **row,
                top_candidate=top_candidate,
                top_overlap=top_overlap,
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Rows remain outside emitted-version accuracy metrics until a controlled experiment emits source-confirmed components.",
            "- Candidate overlap means the source runtime tree and APK report candidate list share a Maven coordinate family.",
            "- Mastodon is kept separate because source uses `me.grishka.litex:*` forked UI-library coordinates.",
            "",
        ]
    )
    return "\n".join(lines)


def format_candidate(coordinate: str | None, version: str | None, score: float | None) -> str:
    if not coordinate:
        return "n/a"
    return f"`{coordinate}:{version}` (`{score:.6f}`)"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Path) -> str:
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
