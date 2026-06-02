"""Join OSV findings with source-validation results for thesis-safe triage."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_APK_TYPE_EVALUATION = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_JSON_OUTPUT = Path("data/results/evaluation/osv-source-validation-triage.json")
DEFAULT_MARKDOWN_OUTPUT = Path("docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an OSV/source-validation triage table for real APK reports."
    )
    parser.add_argument(
        "--apk-type-evaluation",
        type=Path,
        default=DEFAULT_APK_TYPE_EVALUATION,
        help="APK type evaluation JSON produced by build_apk_type_evaluation.py.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=DEFAULT_JSON_OUTPUT,
        help="Path for structured JSON output.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=DEFAULT_MARKDOWN_OUTPUT,
        help="Path for Markdown output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    apk_type = load_json(args.apk_type_evaluation)
    rows = build_rows(apk_type.get("real_cases", []))
    summary = build_summary(apk_type.get("real_cases", []), rows)
    payload = {
        "schema_version": 1,
        "source": str(args.apk_type_evaluation),
        "summary": summary,
        "rows": rows,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(build_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "doc": str(args.markdown_output),
                "json": str(args.json_output),
                "component_rows": len(rows),
                "source_confirmed_advisories": summary["source_confirmed_advisories"],
                "source_mismatch_advisories": summary["source_mismatch_advisories"],
            },
            indent=2,
        )
    )


def build_rows(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        raw_report_path = case.get("report_path")
        if not raw_report_path:
            continue
        report_path = Path(raw_report_path)
        osv_path = report_path.with_name("osv-vulnerabilities.json")
        if not osv_path.exists():
            continue
        osv = load_json(osv_path)
        validation_results = load_validation_results(case.get("validation_path"))
        for result in osv.get("results", []):
            vulnerabilities = result.get("vulnerabilities") or []
            if not vulnerabilities:
                continue
            coordinate = str(result.get("coordinate") or "")
            validation = validation_results.get(coordinate, {})
            rows.append(
                {
                    "case_id": case.get("case_id"),
                    "case": case.get("name"),
                    "role": case.get("role"),
                    "coordinate": coordinate,
                    "reported_version": str(result.get("version") or ""),
                    "source_versions": validation.get("source_versions", []),
                    "validation_status": validation.get("status") or "not-source-validated",
                    "triage": triage_status(validation.get("status"), case.get("role")),
                    "finding_confidence": result.get("finding_confidence"),
                    "advisory_count": len(vulnerabilities),
                    "advisories": advisory_ids(vulnerabilities),
                    "highest_severity": highest_severity(vulnerabilities),
                    "report_path": str(report_path),
                    "osv_path": str(osv_path),
                    "validation_path": case.get("validation_path"),
                }
            )
    return rows


def load_validation_results(path_value: Any) -> dict[str, dict[str, Any]]:
    if not path_value:
        return {}
    path = Path(path_value)
    if not path.exists():
        return {}
    data = load_json(path)
    results: dict[str, dict[str, Any]] = {}
    for row in data.get("results", []):
        coordinate = str(row.get("coordinate") or "")
        if coordinate:
            results[coordinate] = row
    return results


def triage_status(validation_status: Any, role: Any) -> str:
    if validation_status == "confirmed":
        return "source-confirmed"
    if validation_status == "version-mismatch":
        return "source-version-mismatch"
    if validation_status == "missing":
        return "source-missing"
    if role in {"source-linked-blocked", "limitation-native-heavy", "limitation-obfuscation"}:
        return "report-only"
    return "not-source-validated"


def advisory_ids(vulnerabilities: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for vulnerability in vulnerabilities:
        aliases = vulnerability.get("aliases") or []
        if aliases:
            ids.extend(str(alias) for alias in aliases)
        elif vulnerability.get("id"):
            ids.append(str(vulnerability["id"]))
    return ids


def highest_severity(vulnerabilities: list[dict[str, Any]]) -> str:
    order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}
    severities = [str(v.get("severity") or "UNKNOWN").upper() for v in vulnerabilities]
    if not severities:
        return "UNKNOWN"
    return max(severities, key=lambda severity: order.get(severity, 0))


def build_summary(cases: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = len({row["case_id"] for row in rows})
    row_counts = Counter(row["triage"] for row in rows)
    vuln_counts: Counter[str] = Counter()
    for row in rows:
        vuln_counts[row["triage"]] += int(row["advisory_count"])
    return {
        "real_cases_scanned": len(cases),
        "cases_with_osv_findings": case_count,
        "finding_rows": len(rows),
        "advisory_count": sum(int(row["advisory_count"]) for row in rows),
        "source_confirmed_rows": row_counts.get("source-confirmed", 0),
        "source_mismatch_rows": row_counts.get("source-version-mismatch", 0),
        "source_missing_rows": row_counts.get("source-missing", 0),
        "report_only_rows": row_counts.get("report-only", 0),
        "not_source_validated_rows": row_counts.get("not-source-validated", 0),
        "source_confirmed_advisories": vuln_counts.get("source-confirmed", 0),
        "source_mismatch_advisories": vuln_counts.get("source-version-mismatch", 0),
        "source_missing_advisories": vuln_counts.get("source-missing", 0),
        "report_only_advisories": vuln_counts.get("report-only", 0),
        "not_source_validated_advisories": vuln_counts.get("not-source-validated", 0),
        "triage_counts": dict(sorted(row_counts.items())),
        "advisory_counts_by_triage": dict(sorted(vuln_counts.items())),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = payload["rows"]
    lines = [
        "# OSV Source Validation Triage",
        "",
        "Generated by `scripts/build_osv_source_validation_triage.py`.",
        "",
        "This table joins OSV findings from generated reports with source dependency validation. It is a triage aid: it does not change matcher output, and it does not suppress report-side findings.",
        "",
        "## Summary",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Real cases scanned | {summary['real_cases_scanned']} |",
        f"| Cases with OSV findings | {summary['cases_with_osv_findings']} |",
        f"| Vulnerable component rows | {summary['finding_rows']} |",
        f"| Advisory count | {summary['advisory_count']} |",
        f"| Source-confirmed advisories | {summary['source_confirmed_advisories']} |",
        f"| Source-version-mismatch advisories | {summary['source_mismatch_advisories']} |",
        f"| Source-missing advisories | {summary['source_missing_advisories']} |",
        f"| Report-only advisories | {summary['report_only_advisories']} |",
        f"| Not-source-validated advisories | {summary['not_source_validated_advisories']} |",
        "",
        "## Triage Rules",
        "",
        "- `source-confirmed`: the reported Maven coordinate and version are present in the resolved source dependency tree.",
        "- `source-version-mismatch`: the coordinate is present, but the reported vulnerable version differs from the resolved source version.",
        "- `source-missing`: the reported Maven coordinate is absent from the resolved source dependency tree.",
        "- `report-only`: the case has no resolved source-validation result or is outside the source-validated accuracy slice.",
        "- `not-source-validated`: the report has OSV findings but no validation row or boundary role explaining the absence.",
        "",
        "## Findings",
        "",
    ]
    if not rows:
        lines.append("No OSV findings were present in the scanned real-APK reports.")
        return "\n".join(lines) + "\n"
    lines.extend(
        [
            "| Case | Triage | Component | Reported version | Source versions | Advisories | Severity |",
            "|---|---|---|---:|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            f"{escape_md(row['case'])} | "
            f"`{row['triage']}` | "
            f"`{row['coordinate']}` | "
            f"{escape_md(row['reported_version'])} | "
            f"{format_versions(row['source_versions'])} | "
            f"{escape_md(', '.join(row['advisories']))} | "
            f"{escape_md(row['highest_severity'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Source-confirmed rows can be discussed as source-validated vulnerability evidence for emitted Maven components. Source-version-mismatch rows should be presented as scanner triage findings tied to APK-selected versions, not as clean source-confirmed vulnerabilities. Report-only rows remain useful for demo or boundary evidence, but they stay outside source-validated accuracy claims.",
        ]
    )
    return "\n".join(lines) + "\n"


def format_versions(versions: Any) -> str:
    if not versions:
        return "n/a"
    return ", ".join(f"`{version}`" for version in versions)


def escape_md(value: Any) -> str:
    return str(value).replace("|", "\\|")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
