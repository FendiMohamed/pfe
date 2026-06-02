from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_APK_TYPE_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_VERSION_TIES_JSON = Path("data/results/experiments/version-band-tie-evidence.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/artifact-family-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/ARTIFACT_FAMILY_DIAGNOSTICS.md")

FAMILY_RULES = {
    "com.squareup.okio:okio": "com.squareup.okio:okio-family",
    "com.squareup.okio:okio-jvm": "com.squareup.okio:okio-family",
    "com.squareup.okhttp3:okhttp": "com.squareup.okhttp3:okhttp-family",
    "com.squareup.okhttp3:okhttp-android": "com.squareup.okhttp3:okhttp-family",
    "androidx.lifecycle:lifecycle-runtime": "androidx.lifecycle:lifecycle-runtime-family",
    "androidx.lifecycle:lifecycle-runtime-android": "androidx.lifecycle:lifecycle-runtime-family",
    "androidx.lifecycle:lifecycle-viewmodel": "androidx.lifecycle:lifecycle-viewmodel-family",
    "androidx.lifecycle:lifecycle-viewmodel-android": "androidx.lifecycle:lifecycle-viewmodel-family",
}

CASE_ID_ALIASES = {
    "aegis-authenticator": "aegis",
    "nextcloud-android": "nextcloud",
    "wikipedia-android": "wikipedia",
}

SELECTED_RE = re.compile(r"Selected (?P<selected>\S+) for (?P<family>[^;]+);")
SUPPRESSED_RE = re.compile(r"suppressed overlapping candidate\(s\): (?P<suppressed>.+?)\. Reason:")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate diagnostic evidence for scoped artifact-family handling.",
    )
    parser.add_argument("--apk-type-json", default=str(DEFAULT_APK_TYPE_JSON))
    parser.add_argument("--version-ties-json", default=str(DEFAULT_VERSION_TIES_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    apk_type_path = Path(args.apk_type_json)
    ties_path = Path(args.version_ties_json)
    payload = build_payload(
        read_json(apk_type_path),
        read_json(ties_path),
        apk_type_path=apk_type_path,
        ties_path=ties_path,
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
                "handled_rows": len(payload["handled_rows"]),
                "review_rows": len(payload["review_rows"]),
                "verdict_counts": payload["verdict_counts"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    apk_type: dict[str, Any],
    version_ties: dict[str, Any],
    *,
    apk_type_path: Path,
    ties_path: Path,
) -> dict[str, Any]:
    report_paths = report_paths_by_case(apk_type)
    handled_rows = []
    for case_id, report_path in sorted(report_paths.items()):
        handled_rows.extend(extract_handled_rows(case_id, report_path))

    handled_keys = {
        (row["case_id"], row["family_id"])
        for row in handled_rows
    }
    handled_keys.update(alias_handled_keys(handled_rows))
    review_rows = [
        diagnose_tie_row(row, handled_keys)
        for row in version_ties.get("rows", [])
        if row.get("coordinate") in FAMILY_RULES
    ]

    verdict_counts: dict[str, int] = {}
    for row in review_rows:
        verdict_counts[row["verdict"]] = verdict_counts.get(row["verdict"], 0) + 1

    return {
        "schema_version": 1,
        "sources": {
            "apk_type": normalize_path(apk_type_path),
            "version_ties": normalize_path(ties_path),
        },
        "scope": "Diagnostic only; this artifact does not change matcher output or add artifact-family rules.",
        "policy": [
            "Artifact-family handling must stay scoped to known overlapping Maven families.",
            "A new rule is allowed only when proof-bundle evidence and a current-control regression matrix support it.",
            "Source dependency coordinates can differ from bytecode-bearing Android/JVM target artifacts; these remain reporting nuances unless source validation and controls support a change.",
        ],
        "family_rules": sorted(set(FAMILY_RULES.values())),
        "handled_rows": handled_rows,
        "review_rows": review_rows,
        "verdict_counts": verdict_counts,
        "conclusion": (
            "Current evidence supports the existing scoped family rules, but does not justify a new global "
            "artifact-family rule. Remaining rows are source-coordinate/reporting nuances or reference-coverage "
            "gaps."
        ),
    }


def report_paths_by_case(apk_type: dict[str, Any]) -> dict[str, str]:
    return {
        str(case.get("case_id")): str(case.get("report_path") or "")
        for case in apk_type.get("real_cases", [])
        if case.get("report_path")
    }


def alias_handled_keys(handled_rows: list[dict[str, Any]]) -> set[tuple[str, str]]:
    keys = set()
    canonical_to_aliases: dict[str, list[str]] = {}
    for alias, canonical in CASE_ID_ALIASES.items():
        canonical_to_aliases.setdefault(canonical, []).append(alias)
    for row in handled_rows:
        for alias in canonical_to_aliases.get(str(row["case_id"]), []):
            keys.add((alias, row["family_id"]))
    return keys


def extract_handled_rows(case_id: str, report_path: str) -> list[dict[str, Any]]:
    path = Path(report_path)
    if not path.exists():
        return []
    report = read_json(path)
    rows = []
    for component in report.get("detected_components", []):
        for evidence in component.get("evidence", []):
            if evidence.get("source") != "artifact-family-disambiguation":
                continue
            detail = str(evidence.get("detail") or "")
            selected_match = SELECTED_RE.search(detail)
            suppressed_match = SUPPRESSED_RE.search(detail)
            coordinate = f"{component.get('group')}:{component.get('artifact')}"
            rows.append(
                {
                    "case_id": case_id,
                    "coordinate": coordinate,
                    "selected": selected_match.group("selected") if selected_match else "",
                    "family_id": selected_match.group("family") if selected_match else FAMILY_RULES.get(coordinate, ""),
                    "suppressed": suppressed_match.group("suppressed") if suppressed_match else "",
                    "confidence": component.get("confidence"),
                    "identity_status": component.get("identity_status"),
                    "version_status": component.get("version_status"),
                    "report_path": normalize_path(path),
                    "detail": detail,
                }
            )
    return rows


def diagnose_tie_row(row: dict[str, Any], handled_keys: set[tuple[str, str]]) -> dict[str, Any]:
    case_id = str(row.get("case_id") or "")
    coordinate = str(row.get("coordinate") or "")
    family_id = FAMILY_RULES.get(coordinate, "")
    source_versions = [str(version) for version in row.get("source_versions", [])]
    classification = str(row.get("classification") or "")
    if (case_id, family_id) in handled_keys:
        verdict = "covered-by-existing-scoped-rule"
        action = "Keep existing scoped family handling; do not add a broader rule."
    elif classification == "artifact-family-or-source-coordinate-nuance":
        verdict = "reporting-coordinate-nuance"
        action = "Document as source-coordinate versus bytecode-target nuance; do not change scoring."
    elif classification == "source-version-not-in-reference-db":
        verdict = "reference-coverage-gap"
        action = "Treat as reference coverage only; test source version in an isolated DB before promotion."
    else:
        verdict = "no-family-rule-change"
        action = "Keep existing ambiguity or mismatch reporting."
    return {
        "case_id": case_id,
        "coordinate": coordinate,
        "family_id": family_id,
        "selected_version": row.get("selected_version"),
        "source_versions": source_versions,
        "classification": classification,
        "source_candidate_present": bool(row.get("experiment_source_version_in_candidates")),
        "score": row.get("experiment_selected_score"),
        "verdict": verdict,
        "safe_action": action,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Artifact-Family Diagnostics",
        "",
        "Generated by `scripts/build_artifact_family_diagnostics.py`.",
        "",
        "This diagnostic checks current Okio, OkHttp, and Lifecycle family ambiguity. It does not change matcher output or add rules.",
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Existing scoped disambiguation rows found in reports: {len(payload['handled_rows'])}",
            f"- Risky family/tie rows reviewed: {len(payload['review_rows'])}",
            f"- Conclusion: {payload['conclusion']}",
            "",
            "## Review Verdicts",
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
            "## Existing Scoped Handling",
            "",
            "| Case | Family | Selected | Suppressed | Status |",
            "|---|---|---|---|---|",
        ]
    )
    for row in payload["handled_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["case_id"]),
                    f"`{row['family_id']}`",
                    f"`{row['selected']}`",
                    md(row["suppressed"] or "n/a"),
                    md(f"{row['identity_status']}/{row['version_status']}"),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Risky Family Rows",
            "",
            "| Case | Coordinate | Family | Selected | Source | Classification | Verdict | Safe action |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["review_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["case_id"]),
                    f"`{row['coordinate']}`",
                    f"`{row['family_id']}`",
                    md(row["selected_version"]),
                    md(", ".join(row["source_versions"]) or "n/a"),
                    f"`{row['classification']}`",
                    f"`{row['verdict']}`",
                    md(row["safe_action"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- No new artifact-family rule is justified by the current evidence.",
            "- Keep existing scoped Okio, OkHttp, Lifecycle, and Compose handling as guarded behavior.",
            "- Treat remaining rows as reporting/source-coordinate nuance or reference-coverage work unless a future proof bundle plus current-control matrix supports a narrower change.",
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
