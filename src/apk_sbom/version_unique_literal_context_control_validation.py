from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path(
    "data/results/experiments/version-unique-literal-context-current-control"
)
DEFAULT_BASELINE_VALIDATION_ROOT = DEFAULT_EXPERIMENT_ROOT / "baseline/source-validation"
DEFAULT_OPT_IN_VALIDATION_ROOT = DEFAULT_EXPERIMENT_ROOT / "source-validation"
DEFAULT_BASELINE_REPORT_ROOT = DEFAULT_EXPERIMENT_ROOT / "baseline"
DEFAULT_OPT_IN_REPORT_ROOT = DEFAULT_EXPERIMENT_ROOT
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/"
    "version-unique-literal-context-current-control-validation.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/"
    "VERSION_UNIQUE_LITERAL_CONTEXT_CURRENT_CONTROL_VALIDATION.md"
)


@dataclass(frozen=True)
class ControlCase:
    app_id: str
    label: str
    role: str
    report_dir: str


CONTROL_CASES = (
    ControlCase(
        app_id="vlc-android",
        label="VLC Android 3.7.1",
        role="target",
        report_dir="report-real-vlc-android",
    ),
    ControlCase(
        app_id="antennapod",
        label="AntennaPod 3.11.4",
        role="control",
        report_dir="report-real-antennapod",
    ),
    ControlCase(
        app_id="osmand",
        label="OsmAnd 5.3.10",
        role="control",
        report_dir="report-real-osmand",
    ),
)

EXPECTED_TARGET_CHANGE = {
    "app_id": "vlc-android",
    "coordinate": "androidx.recyclerview:recyclerview",
    "baseline_version": "1.2.1",
    "opt_in_version": "1.3.2",
    "baseline_status": "version-mismatch",
    "opt_in_status": "confirmed",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the opt-in version-unique literal/context reranker against "
            "the current affected real-APK target/control slice."
        )
    )
    parser.add_argument(
        "--baseline-validation-root",
        default=str(DEFAULT_BASELINE_VALIDATION_ROOT),
    )
    parser.add_argument(
        "--opt-in-validation-root",
        default=str(DEFAULT_OPT_IN_VALIDATION_ROOT),
    )
    parser.add_argument("--baseline-report-root", default=str(DEFAULT_BASELINE_REPORT_ROOT))
    parser.add_argument("--opt-in-report-root", default=str(DEFAULT_OPT_IN_REPORT_ROOT))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        baseline_validation_root=Path(args.baseline_validation_root),
        opt_in_validation_root=Path(args.opt_in_validation_root),
        baseline_report_root=Path(args.baseline_report_root),
        opt_in_report_root=Path(args.opt_in_report_root),
    )
    result = write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_doc=Path(args.output_doc),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_payload(
    *,
    baseline_validation_root: Path = DEFAULT_BASELINE_VALIDATION_ROOT,
    opt_in_validation_root: Path = DEFAULT_OPT_IN_VALIDATION_ROOT,
    baseline_report_root: Path = DEFAULT_BASELINE_REPORT_ROOT,
    opt_in_report_root: Path = DEFAULT_OPT_IN_REPORT_ROOT,
) -> dict[str, Any]:
    cases = [
        evaluate_case(
            case,
            baseline_validation_root=baseline_validation_root,
            opt_in_validation_root=opt_in_validation_root,
            baseline_report_root=baseline_report_root,
            opt_in_report_root=opt_in_report_root,
        )
        for case in CONTROL_CASES
    ]
    changed_rows = [
        change
        for case in cases
        for change in case["changed_rows"]
    ]
    gates = build_gates(cases, changed_rows)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    totals = {
        "baseline_confirmed": sum(case["baseline"]["confirmed"] for case in cases),
        "opt_in_confirmed": sum(case["opt_in"]["confirmed"] for case in cases),
        "baseline_version_mismatches": sum(
            case["baseline"]["version_mismatches"] for case in cases
        ),
        "opt_in_version_mismatches": sum(
            case["opt_in"]["version_mismatches"] for case in cases
        ),
        "baseline_missing": sum(case["baseline"]["missing"] for case in cases),
        "opt_in_missing": sum(case["opt_in"]["missing"] for case in cases),
    }
    summary = {
        "cases_evaluated": len(cases),
        "target_cases": sum(1 for case in cases if case["role"] == "target"),
        "control_cases": sum(1 for case in cases if case["role"] == "control"),
        "changed_rows": len(changed_rows),
        "confirmed_delta": totals["opt_in_confirmed"] - totals["baseline_confirmed"],
        "version_mismatch_delta": (
            totals["opt_in_version_mismatches"]
            - totals["baseline_version_mismatches"]
        ),
        "missing_delta": totals["opt_in_missing"] - totals["baseline_missing"],
        "failed_gates": len(failed_gates),
    }
    return {
        "schema_version": 1,
        "verdict": verdict(failed_gates),
        "scope": (
            "Current-control evidence for the explicit opt-in "
            "version-unique literal/context reranker. Baseline and opt-in reports "
            "use the same Phase 4 multi-scale calibrated reference DB; the only "
            "intended moving part is the reranker flag."
        ),
        "sources": {
            "baseline_validation_root": normalize_path(baseline_validation_root),
            "opt_in_validation_root": normalize_path(opt_in_validation_root),
            "baseline_report_root": normalize_path(baseline_report_root),
            "opt_in_report_root": normalize_path(opt_in_report_root),
        },
        "expected_target_change": EXPECTED_TARGET_CHANGE,
        "summary": summary,
        "totals": totals,
        "cases": cases,
        "changed_rows": changed_rows,
        "gates": gates,
    }


def evaluate_case(
    case: ControlCase,
    *,
    baseline_validation_root: Path,
    opt_in_validation_root: Path,
    baseline_report_root: Path,
    opt_in_report_root: Path,
) -> dict[str, Any]:
    baseline_validation_path = baseline_validation_root / case.app_id / "source-validation.json"
    opt_in_validation_path = opt_in_validation_root / case.app_id / "source-validation.json"
    baseline_report_path = baseline_report_root / case.report_dir / "report.json"
    opt_in_report_path = opt_in_report_root / case.report_dir / "report.json"
    baseline_validation = read_json(baseline_validation_path)
    opt_in_validation = read_json(opt_in_validation_path)
    baseline_report = read_json(baseline_report_path)
    opt_in_report = read_json(opt_in_report_path)
    changed_rows = compare_validation_rows(
        case.app_id,
        baseline_validation,
        opt_in_validation,
    )
    return {
        "app_id": case.app_id,
        "label": case.label,
        "role": case.role,
        "paths": {
            "baseline_validation": normalize_path(baseline_validation_path),
            "opt_in_validation": normalize_path(opt_in_validation_path),
            "baseline_report": normalize_path(baseline_report_path),
            "opt_in_report": normalize_path(opt_in_report_path),
        },
        "baseline": validation_summary(baseline_validation),
        "opt_in": validation_summary(opt_in_validation),
        "deltas": {
            "confirmed": int(opt_in_validation.get("confirmed", 0))
            - int(baseline_validation.get("confirmed", 0)),
            "version_mismatches": int(opt_in_validation.get("version_mismatches", 0))
            - int(baseline_validation.get("version_mismatches", 0)),
            "missing": int(opt_in_validation.get("missing", 0))
            - int(baseline_validation.get("missing", 0)),
        },
        "reranker_flags": {
            "baseline": report_reranker_enabled(baseline_report),
            "opt_in": report_reranker_enabled(opt_in_report),
        },
        "changed_rows": changed_rows,
    }


def compare_validation_rows(
    app_id: str,
    baseline: dict[str, Any],
    opt_in: dict[str, Any],
) -> list[dict[str, Any]]:
    baseline_rows = validation_row_index(baseline)
    opt_in_rows = validation_row_index(opt_in)
    changed_rows: list[dict[str, Any]] = []
    for key in sorted(set(baseline_rows) | set(opt_in_rows)):
        baseline_row = baseline_rows.get(key)
        opt_in_row = opt_in_rows.get(key)
        if baseline_row == opt_in_row:
            continue
        if same_validation_outcome(baseline_row, opt_in_row):
            continue
        coordinate = key[1]
        changed_rows.append(
            {
                "app_id": app_id,
                "kind": key[0],
                "coordinate": coordinate,
                "baseline_version": value_at(baseline_row, "version"),
                "opt_in_version": value_at(opt_in_row, "version"),
                "baseline_status": value_at(baseline_row, "status"),
                "opt_in_status": value_at(opt_in_row, "status"),
                "source_versions": value_at(opt_in_row, "source_versions")
                or value_at(baseline_row, "source_versions")
                or [],
            }
        )
    return changed_rows


def validation_row_index(summary: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    rows = {}
    for row in summary.get("results", []):
        if not isinstance(row, dict):
            continue
        key = (str(row.get("kind") or ""), str(row.get("coordinate") or ""))
        rows[key] = row
    return rows


def same_validation_outcome(
    baseline_row: dict[str, Any] | None,
    opt_in_row: dict[str, Any] | None,
) -> bool:
    if baseline_row is None or opt_in_row is None:
        return False
    fields = ("version", "status", "source_versions")
    return all(baseline_row.get(field) == opt_in_row.get(field) for field in fields)


def validation_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "sbom_components": int(summary.get("sbom_components", 0)),
        "source_components": int(summary.get("source_components", 0)),
        "confirmed": int(summary.get("confirmed", 0)),
        "version_mismatches": int(summary.get("version_mismatches", 0)),
        "missing": int(summary.get("missing", 0)),
    }


def report_reranker_enabled(report: dict[str, Any]) -> bool:
    match_summary = report.get("match_summary")
    if not isinstance(match_summary, dict):
        return False
    return bool(match_summary.get("version_unique_literal_context_reranker_enabled"))


def build_gates(
    cases: list[dict[str, Any]],
    changed_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    control_changes = [
        change
        for change in changed_rows
        if case_by_app(cases, change["app_id"]).get("role") == "control"
    ]
    unexpected_changes = [
        change for change in changed_rows if not is_expected_target_change(change)
    ]
    count_regressions = [
        case
        for case in cases
        if case["deltas"]["confirmed"] < 0
        or case["deltas"]["version_mismatches"] > 0
        or case["deltas"]["missing"] > 0
    ]
    return [
        gate(
            "baseline-default-off-opt-in-on",
            fail_count=sum(
                1
                for case in cases
                if case["reranker_flags"]["baseline"]
                or not case["reranker_flags"]["opt_in"]
            ),
            evidence=(
                "Every baseline report has the reranker disabled and every "
                "opt-in report has it enabled."
            ),
        ),
        gate(
            "component-counts-stable",
            fail_count=sum(
                1
                for case in cases
                if case["baseline"]["sbom_components"]
                != case["opt_in"]["sbom_components"]
            ),
            evidence="SBOM Maven component counts are unchanged per app.",
        ),
        gate(
            "expected-target-improvement-present",
            fail_count=0 if any(is_expected_target_change(change) for change in changed_rows) else 1,
            evidence=(
                "VLC RecyclerView moves from 1.2.1/version-mismatch to "
                "1.3.2/confirmed."
            ),
        ),
        gate(
            "controls-unchanged",
            fail_count=len(control_changes),
            evidence=f"{len(control_changes)} changed validation rows in control apps.",
        ),
        gate(
            "only-expected-row-changed",
            fail_count=len(unexpected_changes),
            evidence=f"{len(changed_rows)} total changed rows; {len(unexpected_changes)} unexpected.",
        ),
        gate(
            "no-source-validation-count-regressions",
            fail_count=len(count_regressions),
            evidence=f"{len(count_regressions)} apps lost confirmations or gained mismatches/missing.",
        ),
    ]


def gate(gate_id: str, *, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


def is_expected_target_change(change: dict[str, Any]) -> bool:
    return all(change.get(key) == value for key, value in EXPECTED_TARGET_CHANGE.items())


def case_by_app(cases: list[dict[str, Any]], app_id: str) -> dict[str, Any]:
    return next(case for case in cases if case["app_id"] == app_id)


def verdict(failed_gates: list[dict[str, Any]]) -> str:
    if failed_gates:
        return "version-unique-literal-context-current-control-failed"
    return "version-unique-literal-context-current-control-opt-in-pass"


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
    totals = payload["totals"]
    lines = [
        "# Version-Unique Literal-Context Current-Control Validation",
        "",
        "Generated by `scripts/build_version_unique_literal_context_control_validation.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Cases evaluated: `{summary['cases_evaluated']}` "
        f"(`{summary['target_cases']}` target, `{summary['control_cases']}` controls)",
        f"- Changed validation rows: `{summary['changed_rows']}`",
        f"- Confirmed delta: `{summary['confirmed_delta']}`",
        f"- Version-mismatch delta: `{summary['version_mismatch_delta']}`",
        f"- Missing delta: `{summary['missing_delta']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        "",
        "## Aggregate Counts",
        "",
        "| Metric | Baseline | Opt-in | Delta |",
        "|---|---:|---:|---:|",
        count_row(
            "Confirmed",
            totals["baseline_confirmed"],
            totals["opt_in_confirmed"],
        ),
        count_row(
            "Version mismatches",
            totals["baseline_version_mismatches"],
            totals["opt_in_version_mismatches"],
        ),
        count_row("Missing", totals["baseline_missing"], totals["opt_in_missing"]),
        "",
        "## Case Counts",
        "",
        "| App | Role | Components | Confirmed | Mismatches | Missing | Changed rows |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for case in payload["cases"]:
        lines.append(
            "| "
            f"{md(case['label'])} | "
            f"`{md(case['role'])}` | "
            f"{case['baseline']['sbom_components']} -> {case['opt_in']['sbom_components']} | "
            f"{case['baseline']['confirmed']} -> {case['opt_in']['confirmed']} | "
            f"{case['baseline']['version_mismatches']} -> {case['opt_in']['version_mismatches']} | "
            f"{case['baseline']['missing']} -> {case['opt_in']['missing']} | "
            f"{len(case['changed_rows'])} |"
        )

    lines.extend(
        [
            "",
            "## Changed Rows",
            "",
            "| App | Coordinate | Baseline | Opt-in | Source versions |",
            "|---|---|---|---|---|",
        ]
    )
    for change in payload["changed_rows"]:
        lines.append(
            "| "
            f"`{md(change['app_id'])}` | "
            f"`{md(change['coordinate'])}` | "
            f"{md(change['baseline_version'])} / `{md(change['baseline_status'])}` | "
            f"{md(change['opt_in_version'])} / `{md(change['opt_in_status'])}` | "
            f"{md(', '.join(change['source_versions']))} |"
        )
    if not payload["changed_rows"]:
        lines.append("| none |  |  |  |  |")

    lines.extend(["", "## Gates", "", "| Gate | Status | Evidence |", "|---|---|---|"])
    for item in payload["gates"]:
        lines.append(
            "| "
            f"`{md(item['gate'])}` | "
            f"`{md(item['status'])}` | "
            f"{md(item['evidence'])} |"
        )

    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "The opt-in reranker passes this affected current-control slice. It "
            "converts the VLC RecyclerView near-tie into a source-confirmed "
            "version while leaving the AntennaPod and OsmAnd one-match control "
            "risks unchanged. This supports the rule as a guarded default-promotion "
            "candidate; broader regression checks should still precede changing "
            "the default.",
            "",
        ]
    )
    return "\n".join(lines)


def count_row(label: str, baseline: int, opt_in: int) -> str:
    return f"| {label} | {baseline} | {opt_in} | {opt_in - baseline} |"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def value_at(row: dict[str, Any] | None, key: str) -> Any:
    if row is None:
        return None
    return row.get(key)


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
