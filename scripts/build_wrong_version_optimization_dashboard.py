from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_MISSES_CSV = Path("data/results/evaluation/real-apk-source-validation-dashboard-misses.csv")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/wrong-version-optimization-dashboard.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md")

RESEARCH_BACKED_POLICY = [
    "Treat wrong-version rows as evidence problems, not as proof that a global newer-version rule is safe.",
    "Promote source-used reference versions only through isolated experiments plus current-control comparison.",
    "Use stronger per-family signals for near ties: literals/class summaries, call/dependency context, opcode/basic-block diagnostics, and R8-aware call-chain evidence.",
    "Preserve ambiguity or report-only annotations when adjacent versions cannot be separated without control regressions.",
    "Keep CVE-sensitive families on source-confirmed versions only; do not turn weak near-ties into confirmed vulnerability claims.",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a dashboard-ready queue for emitted wrong-version source-validation rows.",
    )
    parser.add_argument("--misses-csv", default=str(DEFAULT_MISSES_CSV))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    misses_path = Path(args.misses_csv)
    rows = read_wrong_version_rows(misses_path)
    payload = build_payload(rows, misses_path=misses_path)

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
                "emitted_wrong_version_rows": payload["summary"]["emitted_wrong_version_rows"],
                "unique_coordinates": payload["summary"]["unique_coordinates"],
                "unique_cases": payload["summary"]["unique_cases"],
                "top_family": payload["family_buckets"][0]["family"] if payload["family_buckets"] else "",
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def read_wrong_version_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [
            row
            for row in reader
            if is_true(row.get("emitted_component"))
            and row.get("miss_class") == "emitted-wrong-version"
        ]


def build_payload(rows: list[dict[str, str]], *, misses_path: Path) -> dict[str, Any]:
    enriched = [enrich_row(row) for row in rows]
    summary = build_summary(enriched)
    return {
        "schema_version": 1,
        "sources": {
            "misses_csv": normalize_path(misses_path),
            "source_validation_dashboard": "docs/evaluation/REAL_APK_SOURCE_VALIDATION_DASHBOARD_REPORT.md",
            "optimization_plan": "docs/planning/RESEARCH_BACKED_REAL_APK_OPTIMIZATION_PLAN.md",
            "guarded_promotion_workflow": "docs/evaluation/GUARDED_REFERENCE_DB_PROMOTION_WORKFLOW.md",
            "version_tie_diagnostics": "docs/evaluation/VERSION_TIE_RERANKER_DIAGNOSTICS.md",
            "pom_coherence_diagnostics": "docs/evaluation/POM_COHERENCE_DIAGNOSTICS.md",
            "artifact_family_diagnostics": "docs/evaluation/ARTIFACT_FAMILY_DIAGNOSTICS.md",
            "opcode_api_signal_diagnostics": "docs/evaluation/OPCODE_API_SIGNAL_DIAGNOSTICS.md",
        },
        "policy": RESEARCH_BACKED_POLICY,
        "summary": summary,
        "family_buckets": build_family_buckets(enriched),
        "top_coordinates": build_top_coordinates(enriched, limit=25),
        "top_source_version_pairs": build_top_source_pairs(enriched, limit=25),
        "top_selected_to_source_pairs": build_top_selected_source_pairs(enriched, limit=25),
        "case_queue": build_case_queue(enriched),
        "priority_lanes": build_priority_lanes(enriched),
        "verdict": verdict(summary),
        "conclusion": (
            "The wrong-version backlog is concentrated enough to attack with guarded family lanes: "
            "Kotlin/coroutines and AndroidX version-band families first, then CVE-sensitive "
            "networking and JSON libraries. No shared reference DB, matcher scoring, SBOM output, "
            "or vulnerability labels should change until an isolated lane passes current controls."
        ),
    }


def enrich_row(row: dict[str, str]) -> dict[str, Any]:
    coordinate = row.get("coordinate", "")
    selected_version = row.get("tool_selected_version", "")
    source_version = source_version_from_row(row)
    relation = version_relation(selected_version, source_version)
    return {
        "case_id": row.get("case_id", ""),
        "case_name": row.get("case_name", ""),
        "case_role": row.get("case_role", ""),
        "coordinate": coordinate,
        "tool_selected_version": selected_version,
        "source_version": source_version,
        "source_versions": row.get("source_versions", ""),
        "source_requested_versions": row.get("source_requested_versions", ""),
        "real_package_and_version": row.get("real_package_and_version", ""),
        "confidence": to_float(row.get("confidence")),
        "match_type": row.get("match_type", ""),
        "purl": row.get("purl", ""),
        "report_path": normalize_path(row.get("report_path")),
        "validation_path": normalize_path(row.get("validation_path")),
        "family": family_bucket(coordinate),
        "relation": relation,
        "root_cause_hint": root_cause_hint(coordinate, relation),
        "safe_next_action": safe_next_action(coordinate, relation),
        "priority": priority_level(coordinate),
    }


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    relations = Counter(row["relation"] for row in rows)
    priorities = Counter(row["priority"] for row in rows)
    return {
        "emitted_wrong_version_rows": len(rows),
        "unique_coordinates": len({row["coordinate"] for row in rows}),
        "unique_cases": len({row["case_id"] for row in rows}),
        "source_present_identity_rows": len(rows),
        "source_linked_blocked_rows_in_scope": 0,
        "metric_changes": 0,
        "relation_counts": dict(sorted(relations.items())),
        "priority_counts": dict(sorted(priorities.items())),
    }


def build_family_buckets(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["family"]].append(row)
    buckets = []
    for family, family_rows in grouped.items():
        buckets.append(
            {
                "family": family,
                "rows": len(family_rows),
                "unique_coordinates": len({row["coordinate"] for row in family_rows}),
                "unique_cases": len({row["case_id"] for row in family_rows}),
                "top_coordinates": [
                    {"coordinate": coordinate, "rows": count}
                    for coordinate, count in Counter(row["coordinate"] for row in family_rows).most_common(5)
                ],
                "dominant_relation": Counter(row["relation"] for row in family_rows).most_common(1)[0][0],
                "safe_next_action": family_action(family),
            }
        )
    return sorted(buckets, key=lambda item: (-item["rows"], item["family"]))


def build_top_coordinates(rows: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["coordinate"]].append(row)
    output = []
    for coordinate, coord_rows in grouped.items():
        output.append(
            {
                "coordinate": coordinate,
                "rows": len(coord_rows),
                "family": family_bucket(coordinate),
                "unique_cases": len({row["case_id"] for row in coord_rows}),
                "top_source_versions": [
                    {"source_version": version, "rows": count}
                    for version, count in Counter(row["source_version"] for row in coord_rows).most_common(5)
                ],
                "top_selected_versions": [
                    {"tool_selected_version": version, "rows": count}
                    for version, count in Counter(row["tool_selected_version"] for row in coord_rows).most_common(5)
                ],
                "dominant_relation": Counter(row["relation"] for row in coord_rows).most_common(1)[0][0],
                "priority": priority_level(coordinate),
                "safe_next_action": safe_next_action(
                    coordinate,
                    Counter(row["relation"] for row in coord_rows).most_common(1)[0][0],
                ),
            }
        )
    return sorted(output, key=lambda item: (-item["rows"], item["coordinate"]))[:limit]


def build_top_source_pairs(rows: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["coordinate"], row["source_version"])].append(row)
    output = []
    for (coordinate, source_version), pair_rows in grouped.items():
        output.append(
            {
                "coordinate": coordinate,
                "source_version": source_version,
                "rows": len(pair_rows),
                "unique_cases": len({row["case_id"] for row in pair_rows}),
                "selected_versions": [
                    {"tool_selected_version": version, "rows": count}
                    for version, count in Counter(row["tool_selected_version"] for row in pair_rows).most_common(5)
                ],
                "family": family_bucket(coordinate),
                "safe_next_action": safe_next_action(
                    coordinate,
                    Counter(row["relation"] for row in pair_rows).most_common(1)[0][0],
                ),
            }
        )
    return sorted(output, key=lambda item: (-item["rows"], item["coordinate"], item["source_version"]))[:limit]


def build_top_selected_source_pairs(rows: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["coordinate"], row["tool_selected_version"], row["source_version"])].append(row)
    output = []
    for (coordinate, selected_version, source_version), pair_rows in grouped.items():
        output.append(
            {
                "coordinate": coordinate,
                "tool_selected_version": selected_version,
                "source_version": source_version,
                "rows": len(pair_rows),
                "unique_cases": len({row["case_id"] for row in pair_rows}),
                "relation": Counter(row["relation"] for row in pair_rows).most_common(1)[0][0],
                "safe_next_action": safe_next_action(
                    coordinate,
                    Counter(row["relation"] for row in pair_rows).most_common(1)[0][0],
                ),
            }
        )
    return sorted(
        output,
        key=lambda item: (-item["rows"], item["coordinate"], item["tool_selected_version"], item["source_version"]),
    )[:limit]


def build_case_queue(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["case_id"]].append(row)
    output = []
    for case_id, case_rows in grouped.items():
        output.append(
            {
                "case_id": case_id,
                "case_name": case_rows[0]["case_name"],
                "case_role": case_rows[0]["case_role"],
                "wrong_version_rows": len(case_rows),
                "unique_coordinates": len({row["coordinate"] for row in case_rows}),
                "priority_rows": sum(1 for row in case_rows if row["priority"] == "P1"),
                "top_families": [
                    {"family": family, "rows": count}
                    for family, count in Counter(row["family"] for row in case_rows).most_common(4)
                ],
                "top_coordinates": [
                    {"coordinate": coordinate, "rows": count}
                    for coordinate, count in Counter(row["coordinate"] for row in case_rows).most_common(5)
                ],
                "recommended_lane": case_recommended_lane(case_rows),
                "report_path": first_non_empty(row["report_path"] for row in case_rows),
                "validation_path": first_non_empty(row["validation_path"] for row in case_rows),
            }
        )
    return sorted(output, key=lambda item: (-item["wrong_version_rows"], item["case_name"]))


def build_priority_lanes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    family_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        family_rows[row["family"]].append(row)

    lanes = [
        (
            "P1 Kotlin and coroutines source-version lane",
            ["kotlin-stdlib", "kotlinx-coroutines"],
            "High volume repeated era drift. Start with isolated source-used Kotlin/coroutines references and current-control comparison.",
        ),
        (
            "P1 AndroidX core/activity/fragment/lifecycle lane",
            ["androidx-core", "androidx-activity", "androidx-fragment", "androidx-lifecycle"],
            "High volume adjacent AndroidX version-band drift. Prefer per-coordinate tie evidence over global app-era rules.",
        ),
        (
            "P2 ViewPager2 and AndroidX support lane",
            ["androidx-viewpager2", "androidx-recyclerview", "androidx-swiperefreshlayout", "androidx-appcompat", "androidx-other"],
            "Known beta/stable and support-library near ties. Keep ambiguous rows report-only unless controls pass.",
        ),
        (
            "P2 CVE-sensitive networking and JSON lane",
            ["okhttp", "okio", "gson", "jackson"],
            "Lower volume but higher vulnerability impact. Exact source-confirmed versions matter before CVE claims.",
        ),
        (
            "P3 residual family lane",
            ["other"],
            "Use after repeated high-volume families are handled; avoid optimizing one-off rows first.",
        ),
    ]

    output = []
    for name, families, rationale in lanes:
        lane_rows = [row for family in families for row in family_rows.get(family, [])]
        output.append(
            {
                "lane": name,
                "families": families,
                "rows": len(lane_rows),
                "unique_coordinates": len({row["coordinate"] for row in lane_rows}),
                "unique_cases": len({row["case_id"] for row in lane_rows}),
                "top_coordinates": [
                    {"coordinate": coordinate, "rows": count}
                    for coordinate, count in Counter(row["coordinate"] for row in lane_rows).most_common(8)
                ],
                "rationale": rationale,
                "acceptance_gate": (
                    "Promote only after target rows improve and controlled, clean, partial, boundary, "
                    "and no-Maven controls show no new selected-version or source-validation regressions."
                ),
            }
        )
    return output


def source_version_from_row(row: dict[str, str]) -> str:
    real_package = row.get("real_package_and_version", "")
    if "@" in real_package:
        return real_package.rsplit("@", 1)[1].strip()
    source_versions = [part.strip() for part in row.get("source_versions", "").split(";") if part.strip()]
    return source_versions[-1] if source_versions else ""


def version_relation(selected: str, source: str) -> str:
    if not selected or not source:
        return "unparsed-or-missing-version"
    if selected == source:
        return "same-version-unexpected"
    selected_key = version_key(selected)
    source_key = version_key(source)
    if not selected_key or not source_key:
        return "unparsed-or-missing-version"
    if selected_key[0] == source_key[0] and len(selected_key) > 1 and len(source_key) > 1 and selected_key[1] == source_key[1]:
        return "patch-or-prerelease-drift"
    if selected_key[0] == source_key[0]:
        return "same-major-band-drift"
    comparison = compare_version_keys(selected_key, source_key)
    if comparison < 0:
        return "selected-older-than-source"
    if comparison > 0:
        return "selected-newer-than-source"
    return "same-numeric-different-label"


def version_key(version: str) -> tuple[int, ...]:
    numbers = [int(match) for match in re.findall(r"\d+", version)]
    return tuple(numbers)


def compare_version_keys(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    width = max(len(left), len(right))
    left_padded = left + (0,) * (width - len(left))
    right_padded = right + (0,) * (width - len(right))
    return (left_padded > right_padded) - (left_padded < right_padded)


def family_bucket(coordinate: str) -> str:
    if coordinate.startswith("org.jetbrains.kotlin:kotlin-stdlib"):
        return "kotlin-stdlib"
    if coordinate.startswith("org.jetbrains.kotlinx:kotlinx-coroutines"):
        return "kotlinx-coroutines"
    if coordinate in {"androidx.core:core", "androidx.core:core-ktx"}:
        return "androidx-core"
    if coordinate.startswith("androidx.activity:"):
        return "androidx-activity"
    if coordinate.startswith("androidx.fragment:"):
        return "androidx-fragment"
    if coordinate.startswith("androidx.lifecycle:"):
        return "androidx-lifecycle"
    if coordinate.startswith("androidx.viewpager2:"):
        return "androidx-viewpager2"
    if coordinate.startswith("androidx.recyclerview:"):
        return "androidx-recyclerview"
    if coordinate.startswith("androidx.swiperefreshlayout:"):
        return "androidx-swiperefreshlayout"
    if coordinate.startswith("androidx.appcompat:"):
        return "androidx-appcompat"
    if coordinate.startswith("androidx."):
        return "androidx-other"
    if coordinate.startswith("com.squareup.okhttp3:"):
        return "okhttp"
    if coordinate.startswith("com.squareup.okio:"):
        return "okio"
    if coordinate == "com.google.code.gson:gson":
        return "gson"
    if coordinate.startswith("com.fasterxml.jackson."):
        return "jackson"
    return "other"


def root_cause_hint(coordinate: str, relation: str) -> str:
    family = family_bucket(coordinate)
    if family in {"kotlin-stdlib", "kotlinx-coroutines"}:
        return "toolchain-era-version-band-drift"
    if family.startswith("androidx"):
        if relation == "patch-or-prerelease-drift":
            return "adjacent-androidx-near-tie"
        return "androidx-version-band-or-app-era-drift"
    if family in {"okhttp", "okio", "gson", "jackson"}:
        return "cve-sensitive-reference-coverage-or-near-tie"
    if relation == "selected-older-than-source":
        return "source-version-coverage-gap-or-older-band-bias"
    if relation == "selected-newer-than-source":
        return "newer-band-over-selection"
    return "coordinate-specific-near-tie"


def priority_level(coordinate: str) -> str:
    family = family_bucket(coordinate)
    if family in {
        "kotlin-stdlib",
        "kotlinx-coroutines",
        "androidx-core",
        "androidx-activity",
        "androidx-fragment",
        "androidx-lifecycle",
    }:
        return "P1"
    if family in {
        "androidx-viewpager2",
        "androidx-recyclerview",
        "androidx-swiperefreshlayout",
        "androidx-appcompat",
        "okhttp",
        "okio",
        "gson",
        "jackson",
    }:
        return "P2"
    return "P3"


def safe_next_action(coordinate: str, relation: str) -> str:
    family = family_bucket(coordinate)
    if family in {"kotlin-stdlib", "kotlinx-coroutines"}:
        return "Run isolated Kotlin/coroutines source-version reference experiment plus current-control comparison."
    if family in {"androidx-core", "androidx-activity", "androidx-fragment"}:
        return "Run per-coordinate AndroidX version-band diagnostics; reject global newer-version tie rules."
    if family == "androidx-lifecycle":
        return "Run Lifecycle public-vs-target artifact-family and source-version controls before promotion."
    if family == "androidx-viewpager2":
        return "Audit beta/stable and adjacent ViewPager2 ties with source-version controls."
    if family in {"okhttp", "okio", "gson", "jackson"}:
        return "Prioritize source-confirmed CVE-sensitive version audit before vulnerability claims."
    if relation == "selected-older-than-source":
        return "Check whether the source-used version is absent from the reference DB before any promotion."
    if relation == "selected-newer-than-source":
        return "Check for over-selection and require controls that prevent false newer-version flips."
    return "Keep as queued coordinate-specific diagnostic until repeated evidence justifies a scoped experiment."


def family_action(family: str) -> str:
    if family in {"kotlin-stdlib", "kotlinx-coroutines"}:
        return "Start guarded source-version reference experiments with Kotlin-era controls."
    if family.startswith("androidx"):
        return "Use scoped AndroidX version-band diagnostics and current controls."
    if family in {"okhttp", "okio", "gson", "jackson"}:
        return "Audit as CVE-sensitive exact-version candidates."
    return "Defer until higher-volume families are reduced."


def case_recommended_lane(rows: list[dict[str, Any]]) -> str:
    priority_counts = Counter(row["priority"] for row in rows)
    family_counts = Counter(row["family"] for row in rows)
    if priority_counts.get("P1", 0) >= 3:
        return "P1 family-lane control case"
    if any(family in family_counts for family in ("okhttp", "okio", "gson", "jackson")):
        return "CVE-sensitive audit case"
    return "Residual wrong-version queue case"


def verdict(summary: dict[str, Any]) -> str:
    if summary["metric_changes"] or summary["source_linked_blocked_rows_in_scope"]:
        return "wrong-version-dashboard-policy-violation"
    if summary["emitted_wrong_version_rows"] and summary["unique_coordinates"]:
        return "wrong-version-dashboard-ready"
    return "wrong-version-dashboard-empty"


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Wrong-Version Optimization Dashboard",
        "",
        "Generated by `scripts/build_wrong_version_optimization_dashboard.py`.",
        "",
        payload["conclusion"],
        "",
        "## Summary",
        "",
        f"- Verdict: `{payload['verdict']}`",
        f"- Emitted wrong-version rows: `{summary['emitted_wrong_version_rows']}`",
        f"- Unique coordinates: `{summary['unique_coordinates']}`",
        f"- Unique APK cases: `{summary['unique_cases']}`",
        f"- Source-present identity rows: `{summary['source_present_identity_rows']}`",
        f"- Source-linked blocked rows in scope: `{summary['source_linked_blocked_rows_in_scope']}`",
        f"- Metric changes in this dashboard: `{summary['metric_changes']}`",
        "",
        "## Research-Backed Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Version Relation Counts",
            "",
            "| Relation | Rows |",
            "|---|---:|",
        ]
    )
    for relation, count in summary["relation_counts"].items():
        lines.append(f"| `{md(relation)}` | {count} |")

    lines.extend(
        [
            "",
            "## Priority Lanes",
            "",
            "| Lane | Rows | Coordinates | Cases | Rationale | Gate |",
            "|---|---:|---:|---:|---|---|",
        ]
    )
    for lane in payload["priority_lanes"]:
        lines.append(
            "| "
            f"{md(lane['lane'])} | "
            f"{lane['rows']} | "
            f"{lane['unique_coordinates']} | "
            f"{lane['unique_cases']} | "
            f"{md(lane['rationale'])} | "
            f"{md(lane['acceptance_gate'])} |"
        )

    lines.extend(
        [
            "",
            "## Family Buckets",
            "",
            "| Family | Rows | Coordinates | Cases | Dominant relation | Safe next action |",
            "|---|---:|---:|---:|---|---|",
        ]
    )
    for bucket in payload["family_buckets"]:
        lines.append(
            "| "
            f"`{md(bucket['family'])}` | "
            f"{bucket['rows']} | "
            f"{bucket['unique_coordinates']} | "
            f"{bucket['unique_cases']} | "
            f"`{md(bucket['dominant_relation'])}` | "
            f"{md(bucket['safe_next_action'])} |"
        )

    lines.extend(
        [
            "",
            "## Top Coordinates",
            "",
            "| Coordinate | Rows | Cases | Family | Top source versions | Top selected versions | Action |",
            "|---|---:|---:|---|---|---|---|",
        ]
    )
    for row in payload["top_coordinates"]:
        lines.append(
            "| "
            f"`{md(row['coordinate'])}` | "
            f"{row['rows']} | "
            f"{row['unique_cases']} | "
            f"`{md(row['family'])}` | "
            f"{version_counts(row['top_source_versions'], 'source_version')} | "
            f"{version_counts(row['top_selected_versions'], 'tool_selected_version')} | "
            f"{md(row['safe_next_action'])} |"
        )

    lines.extend(
        [
            "",
            "## Top Source-Version Pairs",
            "",
            "| Coordinate | Source version | Rows | Cases | Tool-selected versions | Action |",
            "|---|---|---:|---:|---|---|",
        ]
    )
    for row in payload["top_source_version_pairs"]:
        lines.append(
            "| "
            f"`{md(row['coordinate'])}` | "
            f"`{md(row['source_version'])}` | "
            f"{row['rows']} | "
            f"{row['unique_cases']} | "
            f"{version_counts(row['selected_versions'], 'tool_selected_version')} | "
            f"{md(row['safe_next_action'])} |"
        )

    lines.extend(
        [
            "",
            "## Top Selected-To-Source Drifts",
            "",
            "| Coordinate | Tool selected | Source version | Rows | Cases | Relation | Action |",
            "|---|---|---|---:|---:|---|---|",
        ]
    )
    for row in payload["top_selected_to_source_pairs"]:
        lines.append(
            "| "
            f"`{md(row['coordinate'])}` | "
            f"`{md(row['tool_selected_version'])}` | "
            f"`{md(row['source_version'])}` | "
            f"{row['rows']} | "
            f"{row['unique_cases']} | "
            f"`{md(row['relation'])}` | "
            f"{md(row['safe_next_action'])} |"
        )

    lines.extend(
        [
            "",
            "## APK Case Queue",
            "",
            "| APK | Role | Wrong-version rows | Coordinates | P1 rows | Top families | Recommended lane | Evidence |",
            "|---|---|---:|---:|---:|---|---|---|",
        ]
    )
    for row in payload["case_queue"]:
        lines.append(
            "| "
            f"{md(row['case_name'])} | "
            f"`{md(row['case_role'])}` | "
            f"{row['wrong_version_rows']} | "
            f"{row['unique_coordinates']} | "
            f"{row['priority_rows']} | "
            f"{family_counts(row['top_families'])} | "
            f"{md(row['recommended_lane'])} | "
            f"{evidence_links(row)} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Start with the P1 Kotlin/coroutines and AndroidX lanes because they cover the largest repeated wrong-version families.",
            "- Use this dashboard as the input queue for isolated reference DB experiments and current-control comparisons.",
            "- Do not edit shared scoring, shared reference DB contents, SBOM output, source-validation metrics, or vulnerability labels from this dashboard alone.",
            "",
        ]
    )
    return "\n".join(lines)


def version_counts(rows: list[dict[str, Any]], key: str) -> str:
    if not rows:
        return "n/a"
    return "<br>".join(f"`{md(row[key])}` ({row['rows']})" for row in rows)


def family_counts(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "n/a"
    return "<br>".join(f"`{md(row['family'])}` ({row['rows']})" for row in rows)


def evidence_links(row: dict[str, Any]) -> str:
    parts = []
    if row.get("report_path"):
        parts.append(f"`report`: `{row['report_path']}`")
    if row.get("validation_path"):
        parts.append(f"`validation`: `{row['validation_path']}`")
    return "<br>".join(parts) if parts else "n/a"


def first_non_empty(values: Any) -> str:
    for value in values:
        if value:
            return value
    return ""


def to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def is_true(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
