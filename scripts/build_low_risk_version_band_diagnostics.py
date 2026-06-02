from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_TARGET_SUMMARY = Path(
    "data/results/experiments/low-risk-source-versions-target/target-summary.json"
)
DEFAULT_CONTROL_SUMMARY = Path(
    "data/results/experiments/low-risk-source-versions-controls/controls-summary.json"
)
DEFAULT_RECYCLERVIEW_TARGET_SUMMARY = Path(
    "data/results/experiments/low-risk-source-versions-recyclerview-target/target-summary.json"
)
DEFAULT_RECYCLERVIEW_CONTROL_SUMMARY = Path(
    "data/results/experiments/low-risk-source-versions-recyclerview-controls/controls-summary.json"
)
DEFAULT_LIFECYCLE_TARGET_SUMMARY = Path(
    "data/results/experiments/low-risk-source-versions-lifecycle-runtime-2-1-0-target/target-summary.json"
)
DEFAULT_LIFECYCLE_CONTROL_SUMMARY = Path(
    "data/results/experiments/low-risk-source-versions-lifecycle-runtime-2-1-0-controls/controls-summary.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/low-risk-version-band-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/LOW_RISK_VERSION_BAND_DIAGNOSTICS.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate diagnostic-only version-band evidence for the low-risk APK experiment.",
    )
    parser.add_argument("--target-summary", default=str(DEFAULT_TARGET_SUMMARY))
    parser.add_argument("--control-summary", default=str(DEFAULT_CONTROL_SUMMARY))
    parser.add_argument("--recyclerview-target-summary", default=str(DEFAULT_RECYCLERVIEW_TARGET_SUMMARY))
    parser.add_argument("--recyclerview-control-summary", default=str(DEFAULT_RECYCLERVIEW_CONTROL_SUMMARY))
    parser.add_argument("--lifecycle-target-summary", default=str(DEFAULT_LIFECYCLE_TARGET_SUMMARY))
    parser.add_argument("--lifecycle-control-summary", default=str(DEFAULT_LIFECYCLE_CONTROL_SUMMARY))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        full_target=read_json(Path(args.target_summary)),
        full_control=read_json(Path(args.control_summary)),
        recyclerview_target=read_json(Path(args.recyclerview_target_summary)),
        recyclerview_control=read_json(Path(args.recyclerview_control_summary)),
        lifecycle_target=read_json(Path(args.lifecycle_target_summary)),
        lifecycle_control=read_json(Path(args.lifecycle_control_summary)),
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
                "full_new_mismatch_rows": len(payload["full_experiment"]["introduced_mismatches"]),
                "full_resolved_rows": len(payload["full_experiment"]["resolved_target_mismatches"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    *,
    full_target: dict[str, Any],
    full_control: dict[str, Any],
    recyclerview_target: dict[str, Any],
    recyclerview_control: dict[str, Any],
    lifecycle_target: dict[str, Any],
    lifecycle_control: dict[str, Any],
) -> dict[str, Any]:
    full = summarize_experiment("full-10-version-expansion", full_target, full_control)
    narrow = [
        summarize_experiment("recyclerview-1.0.0-only", recyclerview_target, recyclerview_control),
        summarize_experiment("lifecycle-runtime-2.1.0-only", lifecycle_target, lifecycle_control),
    ]
    return {
        "schema_version": 1,
        "scope": "Diagnostic only; this artifact does not change matcher scoring or promote reference versions.",
        "policy": (
            "Keep the shared calibrated DB unchanged. New source-used versions need a scoped "
            "version-band discriminator and a zero-regression current-control matrix before promotion."
        ),
        "full_experiment": full,
        "narrow_experiments": narrow,
        "coordinate_summary": summarize_coordinates(full),
    }


def summarize_experiment(
    experiment_id: str,
    target_summary: dict[str, Any],
    control_summary: dict[str, Any],
) -> dict[str, Any]:
    target_rows = target_summary.get("rows", [])
    control_rows = control_summary.get("rows", [])
    return {
        "experiment_id": experiment_id,
        "db_path": target_summary.get("db_path") or control_summary.get("db_path"),
        "candidate_versions": target_summary.get("candidate_versions", []),
        "improved_target_cases": sorted(
            row["case_id"] for row in target_rows if row.get("improved_vs_baseline")
        ),
        "regressed_target_cases": sorted(
            row["case_id"] for row in target_rows if row.get("regressed_vs_baseline")
        ),
        "regressed_control_cases": sorted(
            row["case_id"] for row in control_rows if row.get("regressed_vs_baseline")
        ),
        "resolved_target_mismatches": collect_changes(target_rows, kind="resolved"),
        "introduced_target_mismatches": collect_changes(target_rows, kind="introduced"),
        "introduced_mismatches": collect_changes([*target_rows, *control_rows], kind="introduced"),
        "decision": promotion_decision(target_rows, control_rows),
    }


def collect_changes(rows: list[dict[str, Any]], *, kind: str) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for row in rows:
        baseline = mismatch_map(row.get("baseline_mismatches", []))
        experiment = mismatch_map(row.get("mismatches", []))
        before = baseline if kind == "resolved" else experiment
        after = experiment if kind == "resolved" else baseline
        for coordinate, mismatch in sorted(before.items()):
            if coordinate in after:
                continue
            changes.append(
                {
                    "case_id": str(row.get("case_id")),
                    "role": str(row.get("role")),
                    "coordinate": coordinate,
                    "selected_version": mismatch["version"],
                    "source_versions": mismatch["source_versions"],
                    "change": kind,
                }
            )
    return changes


def mismatch_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    return {str(row["coordinate"]): row for row in rows}


def promotion_decision(target_rows: list[dict[str, Any]], control_rows: list[dict[str, Any]]) -> str:
    regressed_targets = [row for row in target_rows if row.get("regressed_vs_baseline")]
    regressed_controls = [row for row in control_rows if row.get("regressed_vs_baseline")]
    if regressed_targets or regressed_controls:
        return "keep-experiment-only-regressions-detected"
    if any(row.get("improved_vs_baseline") for row in target_rows):
        return "candidate-for-guarded-promotion"
    return "keep-experiment-only-no-target-benefit"


def summarize_coordinates(full: dict[str, Any]) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for change_type, source_rows in (
        ("resolved_target_cases", full["resolved_target_mismatches"]),
        ("new_mismatch_cases", full["introduced_mismatches"]),
    ):
        for item in source_rows:
            coordinate = item["coordinate"]
            row = rows.setdefault(
                coordinate,
                {
                    "coordinate": coordinate,
                    "resolved_target_cases": [],
                    "new_mismatch_cases": [],
                    "diagnostic_verdict": "needs-scoped-version-band-discriminator",
                },
            )
            row[change_type].append(item["case_id"])
    for row in rows.values():
        row["resolved_target_cases"] = sorted(set(row["resolved_target_cases"]))
        row["new_mismatch_cases"] = sorted(set(row["new_mismatch_cases"]))
        if row["resolved_target_cases"] and row["new_mismatch_cases"]:
            row["diagnostic_verdict"] = "benefit-and-regression-conflict"
        elif row["new_mismatch_cases"]:
            row["diagnostic_verdict"] = "regression-risk"
        else:
            row["diagnostic_verdict"] = "target-benefit-needs-isolated-control-matrix"
    return sorted(rows.values(), key=lambda row: row["coordinate"])


def build_markdown(payload: dict[str, Any]) -> str:
    full = payload["full_experiment"]
    lines = [
        "# Low-Risk Version-Band Diagnostics",
        "",
        "Generated by `scripts/build_low_risk_version_band_diagnostics.py`.",
        "",
        "This is a diagnostic-only artifact. It does not change matcher scoring and does not promote reference versions.",
        "",
        "## Decision",
        "",
        f"- Policy: {payload['policy']}",
        f"- Full expansion verdict: `{full['decision']}`",
        f"- Improved targets: `{', '.join(full['improved_target_cases']) or 'none'}`",
        f"- Regressed controls: `{', '.join(full['regressed_control_cases']) or 'none'}`",
        "",
        "## Coordinate Evidence",
        "",
        "| Coordinate | Resolved target cases | New mismatch cases | Diagnostic verdict |",
        "|---|---|---|---|",
    ]
    for row in payload["coordinate_summary"]:
        lines.append(
            "| "
            f"`{row['coordinate']}` | "
            f"{md(', '.join(row['resolved_target_cases']) or 'none')} | "
            f"{md(', '.join(row['new_mismatch_cases']) or 'none')} | "
            f"`{row['diagnostic_verdict']}` |"
        )

    lines.extend(
        [
            "",
            "## Narrow Checks",
            "",
            "| Experiment | Improved targets | Regressed targets | Regressed controls | Decision |",
            "|---|---|---|---|---|",
        ]
    )
    for experiment in payload["narrow_experiments"]:
        lines.append(
            "| "
            f"`{experiment['experiment_id']}` | "
            f"{md(', '.join(experiment['improved_target_cases']) or 'none')} | "
            f"{md(', '.join(experiment['regressed_target_cases']) or 'none')} | "
            f"{md(', '.join(experiment['regressed_control_cases']) or 'none')} | "
            f"`{experiment['decision']}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The full expansion proves that source-used reference coverage is useful, but it also exposes older AndroidX versions as attractive false selections for newer apps. AppCompat, Core, and Lifecycle rows show the clearest cross-app conflicts.",
            "",
            "The narrow RecyclerView and Lifecycle Runtime experiments are also rejected because each regresses established controls. Future work should test a scoped discriminator that can distinguish version bands without changing the default matcher until a fresh zero-regression control matrix passes.",
            "",
        ]
    )
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
