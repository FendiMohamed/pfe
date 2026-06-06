from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from typing import Any


DEFAULT_INPUT_JSON = Path("data/results/evaluation/no-maven-signal-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/no-maven-androidx-report-only-experiment.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/NO_MAVEN_ANDROIDX_REPORT_ONLY_EXPERIMENT.md")

MIN_REPORT_ONLY_SCORE = 0.30
MIN_PACKAGE_SCORE = 0.50
MIN_OPCODE_SCORE = 0.70

COORD_RE = re.compile(
    r"(?P<group>[A-Za-z0-9_.-]+(?:\.[A-Za-z0-9_.-]+)+):"
    r"(?P<artifact>[A-Za-z0-9_.-]+):"
    r"(?P<version>[A-Za-z0-9_.+\-\[\](),]+)"
    r"(?:\s*->\s*(?P<resolved>[A-Za-z0-9_.+\-\[\](),]+))?"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate source-backed AndroidX candidates for no-Maven reports.",
    )
    parser.add_argument("--input-json", default=str(DEFAULT_INPUT_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(Path(args.input_json))
    result = write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_doc=Path(args.output_doc),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_payload(input_json: Path) -> dict[str, Any]:
    source = read_json(input_json)
    evaluated_rows: list[dict[str, Any]] = []
    blocked_cases: list[dict[str, Any]] = []

    for case in source.get("cases", []):
        if case.get("classification") != "identity-coverage-miss":
            blocked_cases.append(block_case(case, "classification-outside-androidx-identity-lane"))
            continue
        report = read_json(Path(case["report"]))
        candidates = report.get("match_summary", {}).get("candidates", [])
        source_versions = parse_source_versions(Path(case["dependency_tree"]))
        for coordinate in case.get("source_candidate_overlap_coordinates", []):
            if not str(coordinate).startswith("androidx."):
                evaluated_rows.append(
                    blocked_coordinate(case, coordinate, "coordinate-outside-androidx-scope")
                )
                continue
            evaluated_rows.append(
                evaluate_coordinate(
                    case=case,
                    coordinate=str(coordinate),
                    candidates=candidates,
                    source_versions=source_versions,
                )
            )

    summary = build_summary(evaluated_rows, blocked_cases)
    return {
        "schema_version": 1,
        "verdict": verdict(summary),
        "scope": (
            "Experiment only. This artifact surfaces source-backed AndroidX candidates "
            "for no-Maven reports without changing matcher scoring, selected versions, "
            "SBOM components, vulnerability labels, source-validation metrics, or the shared DB."
        ),
        "policy": [
            "Evaluate only no-Maven rows already classified as AndroidX identity-coverage misses.",
            "Require source runtime dependency overlap and an exact source-version candidate in the report.",
            f"Require score >= {MIN_REPORT_ONLY_SCORE}, package score >= {MIN_PACKAGE_SCORE}, and opcode score >= {MIN_OPCODE_SCORE}.",
            "Surface matching rows only as report-only coordinate/version candidates.",
            "Keep forked-library cases such as Mastodon outside this AndroidX experiment.",
            "Require a fresh control matrix before any matcher, DB, SBOM, or dashboard metric promotion.",
        ],
        "source": normalize_path(input_json),
        "summary": summary,
        "candidate_rows": evaluated_rows,
        "blocked_cases": blocked_cases,
    }


def evaluate_coordinate(
    *,
    case: dict[str, Any],
    coordinate: str,
    candidates: list[dict[str, Any]],
    source_versions: dict[str, list[str]],
) -> dict[str, Any]:
    versions = source_versions.get(coordinate, [])
    coordinate_candidates = [
        candidate for candidate in candidates if candidate.get("coordinate") == coordinate
    ]
    exact_candidates = [
        candidate
        for candidate in coordinate_candidates
        if normalize_version(str(candidate.get("version") or "")) in versions
    ]
    selected = max(exact_candidates or coordinate_candidates, key=candidate_score, default={})
    evidence = selected.get("evidence", {}) if selected else {}
    action, reason_codes, blocked_by = classify_candidate(
        selected=selected,
        exact_source_version_candidate=bool(exact_candidates),
        source_versions=versions,
    )
    return {
        "apk": case["apk"],
        "coordinate": coordinate,
        "source_versions": versions,
        "candidate_version": selected.get("version"),
        "candidate_score": selected.get("score"),
        "exact_source_version_candidate": bool(exact_candidates),
        "policy_action": action,
        "reason_codes": reason_codes,
        "blocked_by": blocked_by,
        "evidence": {
            "package_score": evidence.get("package_score"),
            "class_score": evidence.get("class_score"),
            "method_score": evidence.get("method_score"),
            "opcode_score": evidence.get("opcode_score"),
            "literal_score": evidence.get("literal_score"),
            "api_reference_score": evidence.get("api_reference_score"),
        },
        "report": case["report"],
        "dependency_tree": case["dependency_tree"],
    }


def classify_candidate(
    *,
    selected: dict[str, Any],
    exact_source_version_candidate: bool,
    source_versions: list[str],
) -> tuple[str, list[str], list[str]]:
    blocked_by: list[str] = []
    reason_codes: list[str] = []
    if not source_versions:
        blocked_by.append("coordinate-not-in-source-runtime-tree")
    if not selected:
        blocked_by.append("coordinate-not-in-report-candidates")
    if selected and not exact_source_version_candidate:
        blocked_by.append("source-version-not-in-report-candidates")
    if selected and float(selected.get("score") or 0.0) < MIN_REPORT_ONLY_SCORE:
        blocked_by.append("candidate-score-below-report-only-floor")
    evidence = selected.get("evidence", {}) if selected else {}
    if selected and float(evidence.get("package_score") or 0.0) < MIN_PACKAGE_SCORE:
        blocked_by.append("package-score-below-report-only-floor")
    if selected and float(evidence.get("opcode_score") or 0.0) < MIN_OPCODE_SCORE:
        blocked_by.append("opcode-score-below-report-only-floor")

    if not blocked_by:
        reason_codes = [
            "source-runtime-overlap",
            "exact-source-version-candidate",
            "diagnostic-score-floor-met",
            "report-only-no-sbom-change",
        ]
        return "surface-report-only-source-backed-candidate", reason_codes, blocked_by

    return "keep-suppressed", reason_codes, blocked_by


def blocked_coordinate(case: dict[str, Any], coordinate: str, reason: str) -> dict[str, Any]:
    return {
        "apk": case["apk"],
        "coordinate": coordinate,
        "source_versions": [],
        "candidate_version": None,
        "candidate_score": None,
        "exact_source_version_candidate": False,
        "policy_action": "keep-out-of-androidx-experiment",
        "reason_codes": [],
        "blocked_by": [reason],
        "evidence": {},
        "report": case["report"],
        "dependency_tree": case["dependency_tree"],
    }


def block_case(case: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "apk": case["apk"],
        "classification": case.get("classification"),
        "recommended_lane": case.get("recommended_lane"),
        "blocked_by": reason,
    }


def parse_source_versions(path: Path) -> dict[str, list[str]]:
    versions: dict[str, set[str]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = COORD_RE.search(line)
        if not match:
            continue
        coordinate = f"{match.group('group')}:{match.group('artifact')}"
        version = normalize_version(match.group("resolved") or match.group("version"))
        versions.setdefault(coordinate, set()).add(version)
    return {coordinate: sorted(values) for coordinate, values in sorted(versions.items())}


def build_summary(
    evaluated_rows: list[dict[str, Any]],
    blocked_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    actions = Counter(row["policy_action"] for row in evaluated_rows)
    return {
        "androidx_identity_cases": len({row["apk"] for row in evaluated_rows}),
        "blocked_non_androidx_cases": len(blocked_cases),
        "candidate_rows_evaluated": len(evaluated_rows),
        "source_backed_exact_candidate_rows": sum(
            1 for row in evaluated_rows if row["exact_source_version_candidate"]
        ),
        "report_only_suggestions": actions.get(
            "surface-report-only-source-backed-candidate", 0
        ),
        "kept_suppressed_rows": actions.get("keep-suppressed", 0)
        + actions.get("keep-out-of-androidx-experiment", 0),
        "policy_action_counts": dict(sorted(actions.items())),
        "default_selection_changes": 0,
        "sbom_component_changes": 0,
        "source_validation_metric_changes": 0,
    }


def verdict(summary: dict[str, Any]) -> str:
    if (
        summary["default_selection_changes"]
        or summary["sbom_component_changes"]
        or summary["source_validation_metric_changes"]
    ):
        return "no-maven-androidx-report-only-boundary-violated"
    if summary["report_only_suggestions"]:
        return "no-maven-androidx-report-only-promising-not-promoted"
    return "no-safe-no-maven-androidx-suggestions"


def write_outputs(
    payload: dict[str, Any],
    *,
    output_json: Path,
    output_doc: Path,
) -> dict[str, Any]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    return {
        "doc": normalize_path(output_doc),
        "json": normalize_path(output_json),
        "verdict": payload["verdict"],
        **payload["summary"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    suggestions = [
        row
        for row in payload["candidate_rows"]
        if row["policy_action"] == "surface-report-only-source-backed-candidate"
    ]
    suppressed = [
        row
        for row in payload["candidate_rows"]
        if row["policy_action"] != "surface-report-only-source-backed-candidate"
    ]
    lines = [
        "# No-Maven AndroidX Report-Only Experiment",
        "",
        "Generated by `apk-sbom no-maven-androidx-experiment`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- AndroidX identity cases inspected: `{summary['androidx_identity_cases']}`",
        f"- Candidate overlap rows evaluated: `{summary['candidate_rows_evaluated']}`",
        f"- Exact source-version candidate rows: `{summary['source_backed_exact_candidate_rows']}`",
        f"- Report-only suggestions: `{summary['report_only_suggestions']}`",
        f"- Kept suppressed rows: `{summary['kept_suppressed_rows']}`",
        f"- Default selection changes: `{summary['default_selection_changes']}`",
        f"- SBOM component changes: `{summary['sbom_component_changes']}`",
        f"- Source-validation metric changes: `{summary['source_validation_metric_changes']}`",
        "",
        "## Report-Only Suggestions",
        "",
        "| APK | Coordinate | Source version | Candidate version | Score | Evidence |",
        "|---|---|---|---|---:|---|",
    ]
    for row in suggestions:
        lines.append(
            "| "
            f"{md(row['apk'])} | "
            f"`{row['coordinate']}` | "
            f"{md(', '.join(row['source_versions']))} | "
            f"{md(row['candidate_version'])} | "
            f"{float(row['candidate_score']):.6f} | "
            f"{md(evidence_summary(row['evidence']))} |"
        )
    if not suggestions:
        lines.append("| none |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Kept Suppressed",
            "",
            "| APK | Coordinate | Source versions | Candidate | Score | Blocked by |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for row in suppressed:
        score = row["candidate_score"]
        score_text = f"{float(score):.6f}" if score is not None else "n/a"
        lines.append(
            "| "
            f"{md(row['apk'])} | "
            f"`{row['coordinate']}` | "
            f"{md(', '.join(row['source_versions']))} | "
            f"{md(row['candidate_version'] or 'none')} | "
            f"{score_text} | "
            f"{md(', '.join(row['blocked_by']))} |"
        )

    lines.extend(["", "## Blocked Cases", ""])
    lines.extend(["| APK | Classification | Lane | Blocked by |", "|---|---|---|---|"])
    for case in payload["blocked_cases"]:
        lines.append(
            "| "
            f"{md(case['apk'])} | "
            f"`{case['classification']}` | "
            f"{md(case['recommended_lane'])} | "
            f"{md(case['blocked_by'])} |"
        )
    if not payload["blocked_cases"]:
        lines.append("| none |  |  |  |")

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "The AndroidX no-Maven lane has source-backed candidates worth surfacing as diagnostics, but not as SBOM components. The low class/method identity coverage remains the key reason to keep this report-only until a broader control matrix proves that candidate promotion does not add false Maven components.",
            "",
        ]
    )
    return "\n".join(lines)


def evidence_summary(evidence: dict[str, Any]) -> str:
    return (
        f"pkg={evidence.get('package_score')}; "
        f"class={evidence.get('class_score')}; "
        f"method={evidence.get('method_score')}; "
        f"opcode={evidence.get('opcode_score')}; "
        f"literal={evidence.get('literal_score')}"
    )


def candidate_score(candidate: dict[str, Any]) -> float:
    return float(candidate.get("score") or 0.0)


def normalize_version(version: str) -> str:
    return version.strip().strip("[](),")


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
