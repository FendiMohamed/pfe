from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_APK_TYPE_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/thesis-evaluation-tables.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/THESIS_EVALUATION_TABLES.md")


SOURCE_VALIDATED_ROLES = {"clean-source-validated", "source-validated-partial"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate thesis-ready evaluation tables from APK-type evaluation evidence.",
    )
    parser.add_argument("--apk-type-json", default=str(DEFAULT_APK_TYPE_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    apk_type_path = Path(args.apk_type_json)
    payload = build_tables(read_json(apk_type_path), apk_type_path=apk_type_path)

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
                "source_validated_real_cases": payload["summary"]["source_validated_real_cases"],
                "overall_confirmed_versions": payload["summary"]["source_validated_versions"]["confirmed"],
                "overall_checked_versions": payload["summary"]["source_validated_versions"]["checked"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_tables(apk_type: dict[str, Any], *, apk_type_path: Path) -> dict[str, Any]:
    cases = apk_type.get("real_cases", [])
    groups = apk_type.get("groups", [])
    controlled = controlled_totals(groups)
    source_validated = [case for case in cases if case.get("role") in SOURCE_VALIDATED_ROLES]
    clean = [case for case in cases if case.get("role") == "clean-source-validated"]
    partial = [case for case in cases if case.get("role") == "source-validated-partial"]
    blocked = [case for case in cases if case.get("role") == "source-linked-blocked"]
    limitations = [case for case in cases if str(case.get("role", "")).startswith("limitation")]

    summary = {
        "apk_type_source": normalize_path(apk_type_path),
        "controlled_fixtures": controlled,
        "source_validated_real_cases": len(source_validated),
        "clean_source_validated_real_cases": len(clean),
        "partial_source_validated_real_cases": len(partial),
        "blocked_source_linked_cases": len(blocked),
        "limitation_cases": len(limitations),
        "source_validated_versions": validation_totals(source_validated),
        "clean_versions": validation_totals(clean),
        "partial_versions": validation_totals(partial),
    }

    return {
        "schema_version": 1,
        "summary": summary,
        "claim_table": build_claim_table(summary),
        "metric_table": build_metric_table(summary),
        "case_table": build_case_table(cases),
        "limitation_table": build_limitation_table(blocked, limitations),
        "writing_guidance": build_writing_guidance(),
    }


def controlled_totals(groups: list[dict[str, Any]]) -> dict[str, Any]:
    controlled_groups = [group for group in groups if group.get("group_id", "").startswith("controlled")]
    case_count = sum(int(group.get("case_count", 0)) for group in controlled_groups)
    expected = 0
    confirmed = 0
    for group in controlled_groups:
        totals = parse_controlled_result(group.get("result_summary", ""))
        expected += totals.get("expected", 0)
        confirmed += totals.get("confirmed", 0)
    return {
        "cases": case_count,
        "expected_components": expected,
        "confirmed_versions": confirmed,
        "rate": safe_rate(confirmed, expected),
    }


def parse_controlled_result(text: str) -> dict[str, int]:
    # The generated text starts with "<matched>/<expected> expected components matched".
    first = text.split(" ", 1)[0]
    if "/" not in first:
        return {"confirmed": 0, "expected": 0}
    left, right = first.split("/", 1)
    return {"confirmed": int(left), "expected": int(right)}


def validation_totals(cases: list[dict[str, Any]]) -> dict[str, Any]:
    confirmed = 0
    checked = 0
    mismatches = 0
    missing = 0
    for case in cases:
        validation = case.get("validation") or {}
        confirmed += int(validation.get("confirmed", 0))
        checked += int(validation.get("checked_components", 0))
        mismatches += int(validation.get("version_mismatches", 0))
        missing += int(validation.get("missing", 0))
    return {
        "cases": len(cases),
        "confirmed": confirmed,
        "checked": checked,
        "mismatches": mismatches,
        "missing_or_nuance": missing,
        "rate": safe_rate(confirmed, checked),
    }


def build_claim_table(summary: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "claim": "The MVP can recover exact Maven component versions on controlled APKs.",
            "evidence": (
                f"{summary['controlled_fixtures']['confirmed_versions']}/"
                f"{summary['controlled_fixtures']['expected_components']} expected controlled versions confirmed."
            ),
            "scope": "Controlled generated fixture set with known ground truth, including clear, R8 rename, R8 shrink, R8 optimize, shrink+optimize, package flattening/repackaging, inline-like call-site stress, and multidex/multi-library cases.",
            "limitation": "Not a claim of perfect real-world APK coverage.",
        },
        {
            "claim": "The MVP can produce exact emitted Maven versions for clean source-validated real APKs.",
            "evidence": (
                f"{summary['clean_versions']['confirmed']}/"
                f"{summary['clean_versions']['checked']} emitted Maven versions confirmed across "
                f"{summary['clean_versions']['cases']} clean real APKs."
            ),
            "scope": "F-Droid, OpenTracks, Tusky, Daily Dozen, and QuickDic; Tusky, Daily Dozen, and QuickDic are clean but sparse.",
            "limitation": "Clean cases should not be used alone as the global real-world score.",
        },
        {
            "claim": "Harder APK families remain useful partial results, not total failures.",
            "evidence": (
                f"{summary['partial_versions']['confirmed']}/"
                f"{summary['partial_versions']['checked']} emitted Maven versions confirmed across "
                f"{summary['partial_versions']['cases']} partial source-validated APKs."
            ),
            "scope": "Modern AndroidX/Kotlin, R8/minified, email/security, old-dependency, native-heavy media, and large dependency-tree APKs.",
            "limitation": "Remaining mismatches are reported as version-band, artifact-family, or reference-coverage limitations.",
        },
        {
            "claim": "The evaluation separates source validation from report-only and boundary evidence.",
            "evidence": (
                f"{summary['blocked_source_linked_cases']} source-linked blocked APKs and "
                f"{summary['limitation_cases']} limitation/boundary cases are excluded from accuracy metrics."
            ),
            "scope": "K-9 is now source-validated partial; Organic Maps, Termux, Jitsi Meet's native files, the hidden-DEX fixture, and the Simplify obfuscated sample define native/hidden-code/obfuscation boundaries.",
            "limitation": "Native package/version identification is outside the MVP; native files are hash-only SBOM file components.",
        },
    ]


def build_metric_table(summary: dict[str, Any]) -> list[dict[str, str]]:
    rows = [
        {
            "dataset_slice": "Controlled APKs",
            "cases": str(summary["controlled_fixtures"]["cases"]),
            "checked_versions": str(summary["controlled_fixtures"]["expected_components"]),
            "confirmed": str(summary["controlled_fixtures"]["confirmed_versions"]),
            "mismatches": "0",
            "missing_or_nuance": "0",
            "rate": percent(summary["controlled_fixtures"]["rate"]),
            "interpretation": "Known ground truth; validates matcher mechanics and confidence handling.",
        },
        {
            "dataset_slice": "Clean source-validated real APKs",
            "cases": str(summary["clean_versions"]["cases"]),
            "checked_versions": str(summary["clean_versions"]["checked"]),
            "confirmed": str(summary["clean_versions"]["confirmed"]),
            "mismatches": str(summary["clean_versions"]["mismatches"]),
            "missing_or_nuance": str(summary["clean_versions"]["missing_or_nuance"]),
            "rate": percent(summary["clean_versions"]["rate"]),
            "interpretation": "Strongest exact-version real APK evidence.",
        },
        {
            "dataset_slice": "Partial source-validated real APKs",
            "cases": str(summary["partial_versions"]["cases"]),
            "checked_versions": str(summary["partial_versions"]["checked"]),
            "confirmed": str(summary["partial_versions"]["confirmed"]),
            "mismatches": str(summary["partial_versions"]["mismatches"]),
            "missing_or_nuance": str(summary["partial_versions"]["missing_or_nuance"]),
            "rate": percent(summary["partial_versions"]["rate"]),
            "interpretation": "Hard APK-family evidence; report by type, not as failure.",
        },
        {
            "dataset_slice": "All source-validated real APKs",
            "cases": str(summary["source_validated_versions"]["cases"]),
            "checked_versions": str(summary["source_validated_versions"]["checked"]),
            "confirmed": str(summary["source_validated_versions"]["confirmed"]),
            "mismatches": str(summary["source_validated_versions"]["mismatches"]),
            "missing_or_nuance": str(summary["source_validated_versions"]["missing_or_nuance"]),
            "rate": percent(summary["source_validated_versions"]["rate"]),
            "interpretation": "Overall emitted-version confirmation rate; use with the clean/partial split.",
        },
    ]
    return rows


def build_case_table(cases: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for case in cases:
        validation = case.get("validation") or {}
        checked = int(validation.get("checked_components", 0))
        confirmed = int(validation.get("confirmed", 0))
        rows.append(
            {
                "case": str(case.get("name")),
                "role": str(case.get("role")),
                "tags": ", ".join(case.get("tags", [])),
                "maven": none_as_na(case.get("maven_components")),
                "native": none_as_na(case.get("native_files")),
                "dex": none_as_na(case.get("dex_count")),
                "confirmed": f"{confirmed}/{checked}" if checked else "not counted",
                "rate": percent(safe_rate(confirmed, checked)) if checked else "n/a",
                "interpretation": str(case.get("interpretation", "")),
            }
        )
    return rows


def build_limitation_table(
    blocked: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rows = []
    for case in blocked:
        rows.append(
            {
                "case": str(case.get("name")),
                "category": "source-linked blocked",
                "why_not_accuracy": "Resolved dependency tree is not available yet.",
                "use_in_thesis": "Dataset diversity and blocker evidence only.",
            }
        )
    for case in limitations:
        role = str(case.get("role", "limitation")).replace("limitation-", "")
        rows.append(
            {
                "case": str(case.get("name")),
                "category": role,
                "why_not_accuracy": "Outside exact Maven version claim.",
                "use_in_thesis": "Scope boundary and limitation evidence.",
            }
        )
    return rows


def build_writing_guidance() -> list[str]:
    return [
        "Use 'emitted Maven version confirmation rate' for source-validated real APKs; do not call it full dependency recall.",
        "Use `docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md` for full source dependency recall and reference DB coverage claims.",
        "Always show clean and partial real APK rows separately before giving the overall source-validated number.",
        "Mention that native .so files are included as hash-only CycloneDX file components, not Maven package versions.",
        "Describe unresolved AndroidX version-band cases as limitations supported by evidence, not as hidden failures.",
        "Describe K-9 as source-validated partial via a validation-only included-build rescue, not as clean evidence.",
    ]


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Thesis Evaluation Tables",
        "",
        "Generated by `scripts/build_thesis_evaluation_tables.py` from `data/results/evaluation/apk-type-evaluation.json`.",
        "",
        "This file packages the current MVP evidence into thesis-ready claims and tables. It deliberately separates controlled fixtures, clean real APKs, partial real APKs, blocked cases, and limitation cases.",
        "",
        "## Main Numbers",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Controlled fixtures | {summary['controlled_fixtures']['cases']} |",
        f"| Controlled expected Maven versions | {summary['controlled_fixtures']['expected_components']} |",
        f"| Controlled exact confirmations | {summary['controlled_fixtures']['confirmed_versions']} |",
        f"| Clean source-validated real APKs | {summary['clean_source_validated_real_cases']} |",
        f"| Partial source-validated real APKs | {summary['partial_source_validated_real_cases']} |",
        f"| All source-validated real APKs | {summary['source_validated_real_cases']} |",
        f"| Blocked source-linked APKs | {summary['blocked_source_linked_cases']} |",
        f"| Limitation/boundary cases | {summary['limitation_cases']} |",
        "",
        "## Thesis Claim Table",
        "",
        "| Claim | Evidence | Scope | Limitation |",
        "|---|---|---|---|",
    ]
    for row in payload["claim_table"]:
        lines.append(
            f"| {md(row['claim'])} | {md(row['evidence'])} | {md(row['scope'])} | {md(row['limitation'])} |"
        )

    lines.extend(
        [
            "",
            "## Metric Table",
            "",
            "| Dataset slice | Cases | Checked emitted versions | Confirmed | Mismatches | Missing/nuance | Rate | Interpretation |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in payload["metric_table"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["dataset_slice"]),
                    row["cases"],
                    row["checked_versions"],
                    row["confirmed"],
                    row["mismatches"],
                    row["missing_or_nuance"],
                    row["rate"],
                    md(row["interpretation"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Per-APK Table",
            "",
            "| APK | Role | Tags | Maven | Native | DEX | Confirmed | Rate | Interpretation |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in payload["case_table"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["case"]),
                    md(row["role"]),
                    md(row["tags"]),
                    row["maven"],
                    row["native"],
                    row["dex"],
                    row["confirmed"],
                    row["rate"],
                    md(row["interpretation"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Excluded From Accuracy Metrics",
            "",
            "| Case | Category | Why not accuracy | Thesis use |",
            "|---|---|---|---|",
        ]
    )
    for row in payload["limitation_table"]:
        lines.append(
            f"| {md(row['case'])} | {md(row['category'])} | {md(row['why_not_accuracy'])} | {md(row['use_in_thesis'])} |"
        )

    lines.extend(
        [
            "",
            "## Writing Guidance",
            "",
        ]
    )
    for item in payload["writing_guidance"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def safe_rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def none_as_na(value: Any) -> str:
    if value is None:
        return "n/a"
    return str(value)


def md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Path | str) -> str:
    return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
