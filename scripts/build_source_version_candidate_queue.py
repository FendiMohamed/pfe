from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_VERSION_TIES_JSON = Path("data/results/experiments/version-band-tie-evidence.json")
DEFAULT_DIAGNOSTICS_JSON = Path("data/results/experiments/version-tie-reranker-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/source-version-candidate-queue.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/SOURCE_VERSION_CANDIDATE_QUEUE.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a guarded source-version candidate queue from version-band evidence.",
    )
    parser.add_argument("--version-ties-json", default=str(DEFAULT_VERSION_TIES_JSON))
    parser.add_argument("--diagnostics-json", default=str(DEFAULT_DIAGNOSTICS_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ties_path = Path(args.version_ties_json)
    diagnostics_path = Path(args.diagnostics_json)
    payload = build_payload(
        read_json(ties_path),
        read_json(diagnostics_path),
        ties_path=ties_path,
        diagnostics_path=diagnostics_path,
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
                "candidates": len(payload["candidates"]),
                "status_counts": payload["status_counts"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    version_ties: dict[str, Any],
    diagnostics: dict[str, Any],
    *,
    ties_path: Path,
    diagnostics_path: Path,
) -> dict[str, Any]:
    diagnostic_by_key = {
        row_key(row): row for row in diagnostics.get("rows", []) if row.get("source_versions")
    }
    by_candidate: dict[tuple[str, str], dict[str, Any]] = {}
    for row in version_ties.get("rows", []):
        coordinate = str(row.get("coordinate", ""))
        for version in row.get("source_versions", []):
            key = (coordinate, str(version))
            candidate = by_candidate.setdefault(
                key,
                {
                    "coordinate": coordinate,
                    "source_version": str(version),
                    "affected_cases": [],
                    "known_regressed_cases": [],
                    "queue_status": "",
                    "promotion_decision": "",
                    "next_action": "",
                },
            )
            diag = diagnostic_by_key.get(row_key(row), {})
            candidate["affected_cases"].append(
                {
                    "case_id": row.get("case_id"),
                    "selected_version": row.get("selected_version"),
                    "classification": row.get("classification"),
                    "diagnostic_verdict": diag.get("diagnostic_verdict"),
                    "safe_action": diag.get("safe_action"),
                }
            )

    candidates = []
    for candidate in by_candidate.values():
        candidate.update(classify_candidate(candidate))
        candidates.append(candidate)
    candidates.sort(key=lambda item: (status_rank(item["queue_status"]), item["coordinate"], item["source_version"]))

    status_counts: dict[str, int] = {}
    for candidate in candidates:
        status_counts[candidate["queue_status"]] = status_counts.get(candidate["queue_status"], 0) + 1

    return {
        "schema_version": 1,
        "sources": {
            "version_ties": normalize_path(ties_path),
            "diagnostics": normalize_path(diagnostics_path),
        },
        "policy": [
            "This queue does not promote versions by itself.",
            "A candidate can move from experiment-only to promotable only after a fresh current-control regression matrix.",
            "Known regressing candidates remain rejected globally even if they improve one target app.",
        ],
        "status_counts": status_counts,
        "candidates": candidates,
    }


def classify_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    affected = candidate["affected_cases"]
    verdicts = {case.get("diagnostic_verdict") for case in affected}
    known_regressions = known_regressed_cases(candidate["coordinate"], candidate["source_version"])
    classifications = {case.get("classification") for case in affected}

    if known_regressions or "known-regression-risk-do-not-promote" in verdicts:
        status = "rejected-global-known-regression"
        decision = "Do not promote to the shared calibrated DB."
        next_action = "Keep as experiment evidence unless a future scoped/app-specific mode is designed."
    elif "do-not-rerank-bytecode-prefers-selected" in verdicts:
        status = "hold-bytecode-prefers-current"
        decision = "Do not promote or rerank based on current evidence."
        next_action = "Keep ambiguity/limitation reporting unless a new independent signal appears."
    elif "artifact-family-review" in verdicts:
        status = "coordinate-family-review"
        decision = "Resolve coordinate-family semantics before any version action."
        next_action = "Review source coordinate versus bytecode-bearing Android target artifact."
    elif "coverage-gap-reference-needed" in verdicts or "source-version-not-in-reference-db" in classifications:
        status = "experiment-only-coverage-gap"
        decision = "May be tested in an isolated reference coverage experiment."
        next_action = "Add only to an experiment DB first, then compare against current controls."
    elif "conflicting-signals-keep-ambiguous" in verdicts:
        status = "hold-conflicting-signals"
        decision = "Do not promote or force; current evidence conflicts."
        next_action = "Keep structured ambiguity and revisit only with a stronger independent signal."
    elif "ambiguity-only-no-independent-signal" in verdicts:
        status = "hold-ambiguity-only"
        decision = "Do not promote or force; no independent signal supports the source version."
        next_action = "Keep structured ambiguity."
    else:
        status = "needs-manual-review"
        decision = "Review manually before any experiment."
        next_action = "Inspect proof bundle and candidate evidence."

    return {
        "known_regressed_cases": known_regressions,
        "queue_status": status,
        "promotion_decision": decision,
        "next_action": next_action,
    }


def known_regressed_cases(coordinate: str, version: str) -> list[str]:
    if coordinate == "androidx.activity:activity" and version == "1.6.0":
        return ["antennapod"]
    if coordinate == "androidx.activity:activity" and version == "1.9.2":
        return ["fdroid"]
    if coordinate == "androidx.concurrent:concurrent-futures" and version == "1.0.0":
        return [
            "fdroid",
            "opentracks",
            "newpipe",
            "antennapod",
            "kde-connect",
            "wikipedia-android",
            "aegis-authenticator",
        ]
    if coordinate == "androidx.viewpager2:viewpager2" and version == "1.1.0-beta02":
        return ["newpipe", "antennapod"]
    return []


def row_key(row: dict[str, Any]) -> tuple[Any, Any]:
    return row.get("case_id"), row.get("coordinate")


def status_rank(status: str) -> int:
    order = {
        "rejected-global-known-regression": 0,
        "hold-bytecode-prefers-current": 1,
        "hold-conflicting-signals": 2,
        "hold-ambiguity-only": 3,
        "experiment-only-coverage-gap": 4,
        "coordinate-family-review": 5,
        "needs-manual-review": 6,
    }
    return order.get(status, 99)


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Source-Version Candidate Queue",
        "",
        "Generated by `scripts/build_source_version_candidate_queue.py`.",
        "",
        "This queue records source-used versions that appeared in version-band mismatch evidence. It is a guardrail for future reference DB work: a candidate here is not automatically safe to promote.",
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {line}" for line in payload["policy"])
    lines.extend(
        [
            "",
            "## Status Counts",
            "",
            "| Status | Count |",
            "|---|---:|",
        ]
    )
    for status, count in sorted(payload["status_counts"].items()):
        lines.append(f"| `{status}` | {count} |")

    lines.extend(
        [
            "",
            "## Queue",
            "",
            "| Coordinate | Source version | Status | Affected cases | Known regressed controls | Promotion decision | Next action |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for candidate in payload["candidates"]:
        affected = ", ".join(
            f"{case['case_id']} ({case['selected_version']} -> {candidate['source_version']})"
            for case in candidate["affected_cases"]
        )
        regressions = ", ".join(candidate["known_regressed_cases"]) or "none"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{candidate['coordinate']}`",
                    f"`{candidate['source_version']}`",
                    f"`{candidate['queue_status']}`",
                    md(affected),
                    md(regressions),
                    md(candidate["promotion_decision"]),
                    md(candidate["next_action"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Details",
            "",
        ]
    )
    for candidate in payload["candidates"]:
        lines.extend(
            [
                f"### `{candidate['coordinate']}` @ `{candidate['source_version']}`",
                "",
                f"- Status: `{candidate['queue_status']}`",
                f"- Known regressed controls: `{', '.join(candidate['known_regressed_cases']) or 'none'}`",
                f"- Promotion decision: {candidate['promotion_decision']}",
                f"- Next action: {candidate['next_action']}",
                "- Affected cases:",
            ]
        )
        for case in candidate["affected_cases"]:
            lines.append(
                f"  - `{case['case_id']}` selected `{case['selected_version']}`; "
                f"classification `{case['classification']}`; diagnostic `{case.get('diagnostic_verdict')}`."
            )
        lines.append("")
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
