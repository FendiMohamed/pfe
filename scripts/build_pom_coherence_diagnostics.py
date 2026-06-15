from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


DEFAULT_VERSION_TIES_JSON = Path("data/results/experiments/version-band-tie-evidence.json")
DEFAULT_APK_TYPE_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_DB_PATH = Path("data/reference_db/reference_features_calibrated_combined.sqlite")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/pom-coherence-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/POM_COHERENCE_DIAGNOSTICS.md")

POM_COHERENCE_SCORE_MARGIN = 0.06
POM_COHERENCE_MIN_RAW_SCORE = 0.35
POM_COHERENCE_MAX_RAW_SCORE = 0.75
CASE_ID_ALIASES = {
    "aegis-authenticator": "aegis",
    "nextcloud-android": "nextcloud",
    "wikipedia-android": "wikipedia",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate diagnostic-only POM/dependency-coherence evidence for version ties.",
    )
    parser.add_argument("--version-ties-json", default=str(DEFAULT_VERSION_TIES_JSON))
    parser.add_argument("--apk-type-json", default=str(DEFAULT_APK_TYPE_JSON))
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ties_path = Path(args.version_ties_json)
    apk_type_path = Path(args.apk_type_json)
    db_path = Path(args.db_path)
    payload = build_payload(
        read_json(ties_path),
        read_json(apk_type_path),
        db_path=db_path,
        ties_path=ties_path,
        apk_type_path=apk_type_path,
    )

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "rows": len(payload["rows"]),
                "verdict_counts": payload["verdict_counts"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    version_ties: dict[str, Any],
    apk_type: dict[str, Any],
    *,
    db_path: Path,
    ties_path: Path,
    apk_type_path: Path,
) -> dict[str, Any]:
    report_paths = {
        str(case.get("case_id")): str(case.get("report_path") or "")
        for case in apk_type.get("real_cases", [])
    }
    for alias, canonical in CASE_ID_ALIASES.items():
        if canonical in report_paths:
            report_paths[alias] = report_paths[canonical]
    with sqlite3.connect(db_path) as connection:
        rows = [
            diagnose_row(row, connection, report_paths.get(str(row.get("case_id")), ""))
            for row in version_ties.get("rows", [])
        ]

    verdict_counts: dict[str, int] = {}
    for row in rows:
        verdict_counts[row["pom_verdict"]] = verdict_counts.get(row["pom_verdict"], 0) + 1

    return {
        "schema_version": 1,
        "sources": {
            "version_ties": normalize_path(ties_path),
            "apk_type": normalize_path(apk_type_path),
            "reference_db": normalize_path(db_path),
        },
        "scope": "Diagnostic only; this artifact does not change matcher output or promote versions.",
        "policy": [
            "POM coherence is allowed only as a conservative tie-breaker.",
            "The raw leader must be between 0.35 and 0.75, alternatives must be within 0.06 score, and the alternative must have more independently selected runtime POM dependency support.",
            "Metadata alone is not APK evidence; unsupported or source-only dependency metadata stays diagnostic.",
        ],
        "thresholds": {
            "score_margin": POM_COHERENCE_SCORE_MARGIN,
            "min_raw_score": POM_COHERENCE_MIN_RAW_SCORE,
            "max_raw_score": POM_COHERENCE_MAX_RAW_SCORE,
        },
        "verdict_counts": verdict_counts,
        "rows": rows,
    }


def diagnose_row(
    row: dict[str, Any],
    connection: sqlite3.Connection,
    report_path: str,
) -> dict[str, Any]:
    candidates = row.get("top_candidates") or []
    selected = find_candidate(candidates, row.get("selected_version")) or (candidates[0] if candidates else {})
    source = find_source_candidate(candidates, row.get("source_versions", []))
    report_components = load_report_components(report_path)
    selected_support = dependency_support(
        connection,
        str(row.get("coordinate", "")),
        str(row.get("selected_version", "")),
        report_components,
    )
    source_support = (
        dependency_support(
            connection,
            str(row.get("coordinate", "")),
            str(source.get("version", "")),
            report_components,
        )
        if source
        else None
    )
    selected_deps = load_runtime_dependencies(
        connection,
        str(row.get("coordinate", "")),
        str(row.get("selected_version", "")),
    )
    source_deps = (
        load_runtime_dependencies(connection, str(row.get("coordinate", "")), str(source.get("version", "")))
        if source
        else []
    )
    verdict, reason = classify_pom_verdict(
        selected,
        source,
        selected_support,
        source_support,
        selected_deps,
        source_deps,
    )
    return {
        "case_id": row.get("case_id"),
        "coordinate": row.get("coordinate"),
        "classification": row.get("classification"),
        "selected_version": row.get("selected_version"),
        "source_versions": row.get("source_versions", []),
        "selected_score": selected.get("score"),
        "source_candidate_present": bool(source),
        "source_candidate_version": source.get("version") if source else None,
        "source_candidate_score": source.get("score") if source else None,
        "selected_runtime_dependency_count": len(selected_deps),
        "source_runtime_dependency_count": len(source_deps),
        "selected_supported_dependencies": selected_support["supported"],
        "selected_unsupported_dependencies": selected_support["unsupported"],
        "source_supported_dependencies": source_support["supported"] if source_support else [],
        "source_unsupported_dependencies": source_support["unsupported"] if source_support else [],
        "pom_verdict": verdict,
        "reason": reason,
        "safe_action": safe_action(verdict),
    }


def classify_pom_verdict(
    selected: dict[str, Any],
    source: dict[str, Any] | None,
    selected_support: dict[str, list[str]],
    source_support: dict[str, list[str]] | None,
    selected_deps: list[dict[str, Any]],
    source_deps: list[dict[str, Any]],
) -> tuple[str, str]:
    if not selected:
        return "no-selected-candidate", "No selected candidate was available in the tie evidence."
    selected_score = float(selected.get("score") or 0.0)
    if selected_score < POM_COHERENCE_MIN_RAW_SCORE:
        return "raw-score-too-low", "The raw leader is below the minimum score for a metadata tie-breaker."
    if selected_score >= POM_COHERENCE_MAX_RAW_SCORE:
        return "raw-score-too-high", "The raw leader is already too strong for metadata to override."
    if source is None:
        return "source-candidate-not-in-reference", "The source version is not present in the candidate list/reference DB."

    source_score = float(source.get("score") or 0.0)
    if selected_score - source_score > POM_COHERENCE_SCORE_MARGIN:
        return "source-outside-score-margin", "The source candidate is outside the allowed POM coherence score margin."
    if not selected_deps and not source_deps:
        return "no-runtime-pom-dependencies", "Neither selected nor source candidate has usable runtime POM dependencies in the reference DB."
    if source_support is None:
        return "source-support-unavailable", "Source candidate support could not be computed."

    selected_count = len(selected_support["supported"])
    source_count = len(source_support["supported"])
    if source_count > selected_count:
        return (
            "source-has-more-pom-support",
            "The source candidate has more independently selected runtime dependency support; this remains diagnostic until a control matrix passes.",
        )
    if selected_count > source_count:
        return "selected-has-more-pom-support", "The selected candidate has more independently selected runtime dependency support."
    if source_deps and source_count == 0:
        return "source-pom-unsupported", "The source candidate has POM dependencies, but none are independently selected in the APK report."
    if selected_deps and selected_count == 0:
        return "selected-pom-unsupported", "The selected candidate has POM dependencies, but none are independently selected in the APK report."
    return "no-extra-pom-support", "POM metadata does not separate the selected and source candidates."


def load_report_components(report_path: str) -> dict[str, dict[str, Any]]:
    path = Path(report_path)
    if not report_path or not path.exists():
        return {}
    report = read_json(path)
    components: dict[str, dict[str, Any]] = {}
    for component in report.get("detected_components", []):
        coordinate = f"{component.get('group')}:{component.get('artifact')}"
        components[coordinate] = {
            "version": str(component.get("version") or ""),
            "identity_status": str(component.get("identity_status") or ""),
            "version_status": str(component.get("version_status") or ""),
            "identity_confidence_label": str(component.get("identity_confidence_label") or ""),
            "version_confidence_label": str(component.get("version_confidence_label") or ""),
        }
    return components


def dependency_support(
    connection: sqlite3.Connection,
    coordinate: str,
    version: str,
    report_components: dict[str, dict[str, Any]],
) -> dict[str, list[str]]:
    supported: list[str] = []
    unsupported: list[str] = []
    for dependency in load_runtime_dependencies(connection, coordinate, version):
        selected = report_components.get(dependency["coordinate"])
        label = f"{dependency['coordinate']}@{dependency['version']}"
        if selected and selected["version"] == dependency["version"] and is_independent_support(selected):
            supported.append(label)
        else:
            unsupported.append(label)
    return {
        "supported": supported,
        "unsupported": unsupported[:8],
    }


def load_runtime_dependencies(
    connection: sqlite3.Connection,
    coordinate: str,
    version: str,
) -> list[dict[str, str]]:
    rows = connection.execute(
        """
        SELECT d.coordinate, d.version, d.scope, d.optional
        FROM maven_dependencies d
        JOIN components c ON c.id = d.component_id
        WHERE c.coordinate = ? AND c.version = ?
        ORDER BY d.coordinate, d.version
        """,
        (coordinate, version),
    ).fetchall()
    dependencies = []
    for dep_coordinate, dep_version, scope, optional in rows:
        if not dep_version or str(dep_version).startswith("${"):
            continue
        if int(optional or 0):
            continue
        if str(scope or "") in {"test", "provided"}:
            continue
        dependencies.append(
            {
                "coordinate": str(dep_coordinate),
                "version": str(dep_version),
                "scope": str(scope or ""),
            }
        )
    return dependencies


def is_independent_support(component: dict[str, Any]) -> bool:
    return (
        component.get("identity_status") != "uncertain"
        and component.get("version_status") != "uncertain"
        and component.get("identity_confidence_label") in {"high", "medium", "low"}
        and component.get("version_confidence_label") in {"high", "medium", "low"}
    )


def find_candidate(candidates: list[dict[str, Any]], version: Any) -> dict[str, Any] | None:
    for candidate in candidates:
        if str(candidate.get("version")) == str(version):
            return candidate
    return None


def find_source_candidate(candidates: list[dict[str, Any]], source_versions: list[Any]) -> dict[str, Any] | None:
    source_version_set = {str(version) for version in source_versions}
    for candidate in candidates:
        if candidate.get("is_source_version") or str(candidate.get("version")) in source_version_set:
            return candidate
    return None


def safe_action(verdict: str) -> str:
    actions = {
        "no-selected-candidate": "Regenerate tie evidence before using POM diagnostics.",
        "raw-score-too-low": "Do not use metadata to rescue a weak bytecode candidate.",
        "raw-score-too-high": "Do not override strong APK bytecode evidence with metadata.",
        "source-candidate-not-in-reference": "Treat as reference coverage gap; test source version only in an isolated DB.",
        "source-outside-score-margin": "Do not override the selected candidate with metadata.",
        "no-runtime-pom-dependencies": "Keep normal ambiguity or mismatch reporting.",
        "source-support-unavailable": "Regenerate with source candidate present before scoring changes.",
        "source-has-more-pom-support": "Run an isolated experiment and current-control matrix before any matcher change.",
        "selected-has-more-pom-support": "Keep selected candidate; POM support does not justify the source version.",
        "source-pom-unsupported": "Keep mismatch/ambiguity visible; metadata lacks APK-side support.",
        "selected-pom-unsupported": "Keep diagnostic only; metadata lacks APK-side support.",
        "no-extra-pom-support": "Keep diagnostic only; POM metadata does not separate versions.",
    }
    return actions[verdict]


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# POM Coherence Diagnostics",
        "",
        "Generated by `scripts/build_pom_coherence_diagnostics.py`.",
        "",
        "This is diagnostic-only evidence. It explains why dependency metadata did or did not support current version ties; it does not change matcher output or promote versions.",
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Verdict Counts",
            "",
            "| Verdict | Count |",
            "|---|---:|",
        ]
    )
    for verdict, count in sorted(payload["verdict_counts"].items()):
        lines.append(f"| `{verdict}` | {count} |")

    lines.extend(
        [
            "",
            "## Diagnostic Table",
            "",
            "| Case | Coordinate | Selected | Source | POM support selected/source | Verdict | Reason | Safe action |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["rows"]:
        selected_support = len(row["selected_supported_dependencies"])
        source_support = len(row["source_supported_dependencies"])
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["case_id"]),
                    f"`{row['coordinate']}`",
                    md(row["selected_version"]),
                    md(", ".join(str(v) for v in row["source_versions"]) or "n/a"),
                    f"{selected_support}/{source_support}",
                    f"`{row['pom_verdict']}`",
                    md(row["reason"]),
                    md(row["safe_action"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Row Details", ""])
    for row in payload["rows"]:
        lines.extend(
            [
                f"### {row['case_id']} - `{row['coordinate']}`",
                "",
                f"- Selected version: `{row['selected_version']}`; source version(s): `{', '.join(str(v) for v in row['source_versions']) or 'n/a'}`",
                f"- Selected/source candidate scores: `{row['selected_score']}` / `{row['source_candidate_score']}`",
                f"- Runtime POM dependency counts, selected/source: `{row['selected_runtime_dependency_count']}` / `{row['source_runtime_dependency_count']}`",
                f"- Supported dependencies, selected: `{', '.join(row['selected_supported_dependencies']) or 'none'}`",
                f"- Supported dependencies, source: `{', '.join(row['source_supported_dependencies']) or 'none'}`",
                f"- Unsupported source dependencies sampled: `{', '.join(row['source_unsupported_dependencies']) or 'none'}`",
                f"- Verdict: `{row['pom_verdict']}` - {row['reason']}",
                "",
            ]
        )
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
