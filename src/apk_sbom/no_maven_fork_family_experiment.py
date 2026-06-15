from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from typing import Any


DEFAULT_INPUT_JSON = Path("data/results/evaluation/no-maven-signal-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/mastodon-fork-family-report-only-audit.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/MASTODON_FORK_FAMILY_REPORT_ONLY_AUDIT.md")

MIN_FORK_SCORE = 0.20
MIN_FORK_PACKAGE_SCORE = 0.50
MIN_FORK_OPCODE_SCORE = 0.85
MIN_DIRECT_SCORE = 0.20
MIN_DIRECT_OPCODE_SCORE = 0.85
MIN_DIRECT_LITERAL_SCORE = 0.60

COORD_RE = re.compile(
    r"(?P<group>[A-Za-z0-9_.-]+(?:\.[A-Za-z0-9_.-]+)+):"
    r"(?P<artifact>[A-Za-z0-9_.-]+):"
    r"(?P<version>[A-Za-z0-9_.+\-\[\](),]+)"
    r"(?:\s*->\s*(?P<resolved>[A-Za-z0-9_.+\-\[\](),]+))?"
)

LITEX_ANDROIDX_ALIASES = {
    "me.grishka.litex:browser": "androidx.browser:browser",
    "me.grishka.litex:collection": "androidx.collection:collection",
    "me.grishka.litex:concurrent": "androidx.concurrent:concurrent-futures",
    "me.grishka.litex:dynamicanimation": "androidx.dynamicanimation:dynamicanimation",
    "me.grishka.litex:palette": "androidx.palette:palette",
    "me.grishka.litex:recyclerview": "androidx.recyclerview:recyclerview",
    "me.grishka.litex:swiperefreshlayout": "androidx.swiperefreshlayout:swiperefreshlayout",
    "me.grishka.litex:viewpager": "androidx.viewpager:viewpager",
    "me.grishka.litex:viewpager2": "androidx.viewpager2:viewpager2",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate Mastodon no-Maven fork-family evidence without changing SBOM output.",
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
    fork_rows: list[dict[str, Any]] = []
    direct_rows: list[dict[str, Any]] = []
    skipped_cases: list[dict[str, Any]] = []

    for case in source.get("cases", []):
        if case.get("classification") != "forked-library-boundary":
            skipped_cases.append(
                {
                    "apk": case.get("apk"),
                    "classification": case.get("classification"),
                    "skipped_by": "classification-outside-fork-family-lane",
                }
            )
            continue
        report = read_json(Path(case["report"]))
        candidates = report.get("match_summary", {}).get("candidates", [])
        source_versions = parse_source_versions(Path(case["dependency_tree"]))
        fork_rows.extend(evaluate_litex_aliases(case, candidates, source_versions))
        direct_rows.extend(evaluate_direct_overlaps(case, candidates, source_versions))

    summary = build_summary(fork_rows, direct_rows, skipped_cases)
    return {
        "schema_version": 1,
        "verdict": verdict(summary),
        "scope": (
            "Experiment only. This artifact audits Mastodon's source-resolved forked "
            "`me.grishka.litex:*` runtime libraries and weak direct candidates without "
            "changing matcher scoring, selected versions, SBOM components, vulnerability "
            "labels, source-validation metrics, or the shared DB."
        ),
        "policy": [
            "Evaluate only rows already classified as forked-library/reference-family boundaries.",
            "Treat `me.grishka.litex:*` to AndroidX mapping as report-only fork-family evidence, not as proof that the upstream AndroidX coordinate should be emitted.",
            f"Fork-family suggestions require compatible source/candidate versions, score >= {MIN_FORK_SCORE}, package score >= {MIN_FORK_PACKAGE_SCORE}, and opcode score >= {MIN_FORK_OPCODE_SCORE}.",
            f"Direct source-coordinate suggestions require an exact source version, score >= {MIN_DIRECT_SCORE}, opcode score >= {MIN_DIRECT_OPCODE_SCORE}, and literal score >= {MIN_DIRECT_LITERAL_SCORE}.",
            "Rows without a report candidate or source-compatible version stay suppressed.",
            "Require reference DB/fork-alias design and a fresh control matrix before any production integration.",
        ],
        "source": normalize_path(input_json),
        "summary": summary,
        "fork_family_rows": fork_rows,
        "direct_candidate_rows": direct_rows,
        "skipped_cases": skipped_cases,
    }


def evaluate_litex_aliases(
    case: dict[str, Any],
    candidates: list[dict[str, Any]],
    source_versions: dict[str, list[str]],
) -> list[dict[str, Any]]:
    rows = []
    for litex_coordinate, upstream_coordinate in sorted(LITEX_ANDROIDX_ALIASES.items()):
        versions = source_versions.get(litex_coordinate, [])
        if not versions:
            continue
        upstream_candidates = [
            candidate for candidate in candidates if candidate.get("coordinate") == upstream_coordinate
        ]
        compatible_candidates = [
            candidate
            for candidate in upstream_candidates
            if any(
                versions_are_compatible(source_version, str(candidate.get("version") or ""))
                for source_version in versions
            )
        ]
        selected = max(compatible_candidates or upstream_candidates, key=candidate_score, default={})
        action, reason_codes, blocked_by = classify_fork_candidate(
            selected=selected,
            compatible_candidate=bool(compatible_candidates),
            source_versions=versions,
        )
        rows.append(
            build_fork_row(
                case=case,
                litex_coordinate=litex_coordinate,
                upstream_coordinate=upstream_coordinate,
                source_versions=versions,
                selected=selected,
                action=action,
                reason_codes=reason_codes,
                blocked_by=blocked_by,
            )
        )
    return rows


def evaluate_direct_overlaps(
    case: dict[str, Any],
    candidates: list[dict[str, Any]],
    source_versions: dict[str, list[str]],
) -> list[dict[str, Any]]:
    candidate_coordinates = {str(candidate.get("coordinate") or "") for candidate in candidates}
    direct_coordinates = sorted(
        coordinate
        for coordinate in candidate_coordinates & set(source_versions)
        if not coordinate.startswith("me.grishka.")
    )
    rows = []
    for coordinate in direct_coordinates:
        coordinate_candidates = [
            candidate for candidate in candidates if candidate.get("coordinate") == coordinate
        ]
        versions = source_versions[coordinate]
        exact_candidates = [
            candidate
            for candidate in coordinate_candidates
            if normalize_version(str(candidate.get("version") or "")) in versions
        ]
        selected = max(exact_candidates or coordinate_candidates, key=candidate_score, default={})
        action, reason_codes, blocked_by = classify_direct_candidate(
            selected=selected,
            exact_candidate=bool(exact_candidates),
            source_versions=versions,
        )
        rows.append(
            build_direct_row(
                case=case,
                coordinate=coordinate,
                source_versions=versions,
                selected=selected,
                action=action,
                reason_codes=reason_codes,
                blocked_by=blocked_by,
            )
        )
    return rows


def classify_fork_candidate(
    *,
    selected: dict[str, Any],
    compatible_candidate: bool,
    source_versions: list[str],
) -> tuple[str, list[str], list[str]]:
    blocked_by: list[str] = []
    if not source_versions:
        blocked_by.append("litex-coordinate-not-in-source-runtime-tree")
    if not selected:
        blocked_by.append("upstream-family-not-in-report-candidates")
    if selected and not compatible_candidate:
        blocked_by.append("source-version-not-compatible-with-report-family-candidate")
    if selected and float(selected.get("score") or 0.0) < MIN_FORK_SCORE:
        blocked_by.append("candidate-score-below-fork-family-floor")
    evidence = selected.get("evidence", {}) if selected else {}
    if selected and float(evidence.get("package_score") or 0.0) < MIN_FORK_PACKAGE_SCORE:
        blocked_by.append("package-score-below-fork-family-floor")
    if selected and float(evidence.get("opcode_score") or 0.0) < MIN_FORK_OPCODE_SCORE:
        blocked_by.append("opcode-score-below-fork-family-floor")

    if not blocked_by:
        return (
            "surface-report-only-fork-family-candidate",
            [
                "litex-source-runtime-coordinate",
                "compatible-upstream-androidx-candidate",
                "diagnostic-fork-family-only",
                "report-only-no-sbom-change",
            ],
            blocked_by,
        )
    return "keep-suppressed", [], blocked_by


def classify_direct_candidate(
    *,
    selected: dict[str, Any],
    exact_candidate: bool,
    source_versions: list[str],
) -> tuple[str, list[str], list[str]]:
    blocked_by: list[str] = []
    if not source_versions:
        blocked_by.append("coordinate-not-in-source-runtime-tree")
    if not selected:
        blocked_by.append("coordinate-not-in-report-candidates")
    if selected and not exact_candidate:
        blocked_by.append("source-version-not-in-report-candidates")
    if selected and float(selected.get("score") or 0.0) < MIN_DIRECT_SCORE:
        blocked_by.append("candidate-score-below-direct-floor")
    evidence = selected.get("evidence", {}) if selected else {}
    if selected and float(evidence.get("opcode_score") or 0.0) < MIN_DIRECT_OPCODE_SCORE:
        blocked_by.append("opcode-score-below-direct-floor")
    if selected and float(evidence.get("literal_score") or 0.0) < MIN_DIRECT_LITERAL_SCORE:
        blocked_by.append("literal-score-below-direct-floor")

    if not blocked_by:
        return (
            "surface-report-only-direct-source-candidate",
            [
                "source-runtime-overlap",
                "exact-source-version-candidate",
                "weak-direct-library-evidence",
                "report-only-no-sbom-change",
            ],
            blocked_by,
        )
    return "keep-suppressed", [], blocked_by


def build_fork_row(
    *,
    case: dict[str, Any],
    litex_coordinate: str,
    upstream_coordinate: str,
    source_versions: list[str],
    selected: dict[str, Any],
    action: str,
    reason_codes: list[str],
    blocked_by: list[str],
) -> dict[str, Any]:
    evidence = selected.get("evidence", {}) if selected else {}
    return {
        "apk": case["apk"],
        "source_coordinate": litex_coordinate,
        "upstream_family_coordinate": upstream_coordinate,
        "source_versions": source_versions,
        "candidate_version": selected.get("version"),
        "candidate_score": selected.get("score"),
        "policy_action": action,
        "reason_codes": reason_codes,
        "blocked_by": blocked_by,
        "evidence": compact_evidence(evidence),
        "report": case["report"],
        "dependency_tree": case["dependency_tree"],
    }


def build_direct_row(
    *,
    case: dict[str, Any],
    coordinate: str,
    source_versions: list[str],
    selected: dict[str, Any],
    action: str,
    reason_codes: list[str],
    blocked_by: list[str],
) -> dict[str, Any]:
    evidence = selected.get("evidence", {}) if selected else {}
    return {
        "apk": case["apk"],
        "coordinate": coordinate,
        "source_versions": source_versions,
        "candidate_version": selected.get("version"),
        "candidate_score": selected.get("score"),
        "policy_action": action,
        "reason_codes": reason_codes,
        "blocked_by": blocked_by,
        "evidence": compact_evidence(evidence),
        "report": case["report"],
        "dependency_tree": case["dependency_tree"],
    }


def compact_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "package_score": evidence.get("package_score"),
        "class_score": evidence.get("class_score"),
        "method_score": evidence.get("method_score"),
        "opcode_score": evidence.get("opcode_score"),
        "literal_score": evidence.get("literal_score"),
        "api_reference_score": evidence.get("api_reference_score"),
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
    fork_rows: list[dict[str, Any]],
    direct_rows: list[dict[str, Any]],
    skipped_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    fork_actions = Counter(row["policy_action"] for row in fork_rows)
    direct_actions = Counter(row["policy_action"] for row in direct_rows)
    return {
        "fork_family_cases": len({row["apk"] for row in fork_rows}),
        "skipped_non_fork_cases": len(skipped_cases),
        "litex_alias_rows_evaluated": len(fork_rows),
        "litex_report_only_suggestions": fork_actions.get(
            "surface-report-only-fork-family-candidate", 0
        ),
        "litex_rows_kept_suppressed": fork_actions.get("keep-suppressed", 0),
        "direct_candidate_rows_evaluated": len(direct_rows),
        "direct_report_only_suggestions": direct_actions.get(
            "surface-report-only-direct-source-candidate", 0
        ),
        "direct_rows_kept_suppressed": direct_actions.get("keep-suppressed", 0),
        "policy_action_counts": dict(sorted((fork_actions + direct_actions).items())),
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
        return "mastodon-fork-family-report-only-boundary-violated"
    if summary["litex_report_only_suggestions"] or summary["direct_report_only_suggestions"]:
        return "mastodon-fork-family-report-only-promising-not-promoted"
    return "no-safe-mastodon-fork-family-suggestions"


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
    fork_suggestions = [
        row
        for row in payload["fork_family_rows"]
        if row["policy_action"] == "surface-report-only-fork-family-candidate"
    ]
    fork_suppressed = [
        row
        for row in payload["fork_family_rows"]
        if row["policy_action"] != "surface-report-only-fork-family-candidate"
    ]
    direct_suggestions = [
        row
        for row in payload["direct_candidate_rows"]
        if row["policy_action"] == "surface-report-only-direct-source-candidate"
    ]
    lines = [
        "# Mastodon Fork-Family Report-Only Audit",
        "",
        "Generated by `apk-sbom no-maven-fork-family-experiment`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Fork-family cases inspected: `{summary['fork_family_cases']}`",
        f"- Litex alias rows evaluated: `{summary['litex_alias_rows_evaluated']}`",
        f"- Litex report-only suggestions: `{summary['litex_report_only_suggestions']}`",
        f"- Litex rows kept suppressed: `{summary['litex_rows_kept_suppressed']}`",
        f"- Direct candidate rows evaluated: `{summary['direct_candidate_rows_evaluated']}`",
        f"- Direct report-only suggestions: `{summary['direct_report_only_suggestions']}`",
        f"- Default selection changes: `{summary['default_selection_changes']}`",
        f"- SBOM component changes: `{summary['sbom_component_changes']}`",
        f"- Source-validation metric changes: `{summary['source_validation_metric_changes']}`",
        "",
        "## Fork-Family Suggestions",
        "",
        "| Source fork coordinate | Source version | Upstream family candidate | Candidate version | Score | Evidence |",
        "|---|---|---|---|---:|---|",
    ]
    for row in fork_suggestions:
        lines.append(
            "| "
            f"`{row['source_coordinate']}` | "
            f"{md(', '.join(row['source_versions']))} | "
            f"`{row['upstream_family_coordinate']}` | "
            f"{md(row['candidate_version'])} | "
            f"{float(row['candidate_score']):.6f} | "
            f"{md(evidence_summary(row['evidence']))} |"
        )
    if not fork_suggestions:
        lines.append("| none |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Direct Source Suggestions",
            "",
            "| Coordinate | Source version | Candidate version | Score | Evidence |",
            "|---|---|---|---:|---|",
        ]
    )
    for row in direct_suggestions:
        lines.append(
            "| "
            f"`{row['coordinate']}` | "
            f"{md(', '.join(row['source_versions']))} | "
            f"{md(row['candidate_version'])} | "
            f"{float(row['candidate_score']):.6f} | "
            f"{md(evidence_summary(row['evidence']))} |"
        )
    if not direct_suggestions:
        lines.append("| none |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Kept Suppressed Fork Rows",
            "",
            "| Source fork coordinate | Source version | Upstream family | Candidate | Score | Blocked by |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for row in fork_suppressed:
        score = row["candidate_score"]
        score_text = f"{float(score):.6f}" if score is not None else "n/a"
        lines.append(
            "| "
            f"`{row['source_coordinate']}` | "
            f"{md(', '.join(row['source_versions']))} | "
            f"`{row['upstream_family_coordinate']}` | "
            f"{md(row['candidate_version'] or 'none')} | "
            f"{score_text} | "
            f"{md(', '.join(row['blocked_by']))} |"
        )

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Mastodon is not a normal AndroidX no-Maven row. The strongest evidence is fork-family evidence: source resolves `me.grishka.litex:*`, while the APK report sees weak upstream AndroidX-looking candidates. This is useful for a future fork-alias/reference design, but it is not safe to emit upstream AndroidX components or count the row as source-validated accuracy evidence.",
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


def versions_are_compatible(source_version: str, candidate_version: str) -> bool:
    source = normalize_version(source_version)
    candidate = normalize_version(candidate_version)
    return source == candidate or source.startswith(f"{candidate}.")


def normalize_version(version: str) -> str:
    return version.strip().strip("[](),")


def candidate_score(candidate: dict[str, Any]) -> float:
    return float(candidate.get("score") or 0.0)


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
