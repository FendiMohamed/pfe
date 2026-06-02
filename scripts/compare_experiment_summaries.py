from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two source-validation experiment summary JSON files.",
    )
    parser.add_argument("--baseline-summary", required=True)
    parser.add_argument("--experiment-summary", required=True)
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--experiment-label", default="experiment")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    baseline = read_json(args.baseline_summary)
    experiment = read_json(args.experiment_summary)
    summary = compare_summaries(
        baseline,
        experiment,
        baseline_label=args.baseline_label,
        experiment_label=args.experiment_label,
    )

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"output_json": str(output_json), "output_md": str(output_md)}, indent=2))
    return 0


def compare_summaries(
    baseline: dict[str, Any],
    experiment: dict[str, Any],
    *,
    baseline_label: str,
    experiment_label: str,
) -> dict[str, Any]:
    baseline_by_case = {row["case_id"]: row for row in baseline["rows"]}
    rows = []
    for row in experiment["rows"]:
        case_id = row["case_id"]
        if case_id not in baseline_by_case:
            raise SystemExit(f"case {case_id!r} missing from baseline summary")
        control = baseline_by_case[case_id]
        compared = dict(row)
        compared["baseline_components"] = control["detected_components"]
        compared["baseline_confirmed"] = control["confirmed"]
        compared["baseline_version_mismatches"] = control["version_mismatches"]
        compared["baseline_missing"] = control["missing"]
        compared["control_delta_components"] = (
            row["detected_components"] - control["detected_components"]
        )
        compared["control_delta_confirmed"] = row["confirmed"] - control["confirmed"]
        compared["control_delta_version_mismatches"] = (
            row["version_mismatches"] - control["version_mismatches"]
        )
        compared["control_delta_missing"] = row["missing"] - control["missing"]
        compared["regressed_vs_control"] = (
            compared["control_delta_confirmed"] < 0
            or compared["control_delta_version_mismatches"] > 0
            or compared["control_delta_missing"] > 0
        )
        compared["improved_vs_control"] = (
            compared["control_delta_confirmed"] > 0
            or compared["control_delta_version_mismatches"] < 0
            or compared["control_delta_missing"] < 0
        )
        rows.append(compared)

    return {
        "baseline_label": baseline_label,
        "baseline_db_path": baseline.get("db_path"),
        "experiment_label": experiment_label,
        "experiment_db_path": experiment.get("db_path"),
        "rows": rows,
        "case_count": len(rows),
        "regressed_cases": [
            row["case_id"] for row in rows if row["regressed_vs_control"]
        ],
        "improved_cases": [
            row["case_id"] for row in rows if row["improved_vs_control"]
        ],
    }


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Source-validation experiment comparison",
        "",
        f"Baseline: {summary['baseline_label']}",
        "",
        f"Baseline DB: `{summary['baseline_db_path']}`",
        "",
        f"Experiment: {summary['experiment_label']}",
        "",
        f"Experiment DB: `{summary['experiment_db_path']}`",
        "",
        "| Case | Components | Confirmed | Mismatches | Missing | Delta vs control | Status |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in summary["rows"]:
        status = "regressed" if row["regressed_vs_control"] else "unchanged"
        if row["improved_vs_control"] and not row["regressed_vs_control"]:
            status = "improved"
        delta = (
            f"{row['control_delta_components']:+d} components, "
            f"{row['control_delta_confirmed']:+d} confirmed, "
            f"{row['control_delta_version_mismatches']:+d} mismatches, "
            f"{row['control_delta_missing']:+d} missing"
        )
        lines.append(
            "| "
            f"{row['case_id']} | "
            f"{row['detected_components']} | "
            f"{row['confirmed']} | "
            f"{row['version_mismatches']} | "
            f"{row['missing']} | "
            f"{delta} | "
            f"{status} |"
        )

    if summary["regressed_cases"]:
        lines.extend(["", "## Regressed Cases", ""])
        for case_id in summary["regressed_cases"]:
            lines.append(f"- `{case_id}`")

    if summary["improved_cases"]:
        lines.extend(["", "## Improved Cases", ""])
        for case_id in summary["improved_cases"]:
            lines.append(f"- `{case_id}`")

    return "\n".join(lines).rstrip() + "\n"


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


if __name__ == "__main__":
    raise SystemExit(main())
