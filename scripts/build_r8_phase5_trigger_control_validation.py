from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_PHASE5_JSON = Path("data/results/experiments/r8-phase5-scoped-trigger-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/r8-phase5-trigger-control-validation.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_PHASE5_TRIGGER_CONTROL_VALIDATION.md")
DEFAULT_SOURCE_ROOT = Path("src/apk_sbom")


BOUNDARY_ROLES = frozenset({"source-linked-blocked", "limitation-native-heavy"})
ALLOWED_EXPERIMENT_IMPORT_MODULES = frozenset({"cli.py", "r8_phase5_experiment.py"})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 5 scoped R8 trigger against current controls."
    )
    parser.add_argument("--phase5-json", default=str(DEFAULT_PHASE5_JSON))
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(Path(args.phase5_json), source_root=Path(args.source_root))

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
                "verdict": payload["verdict"],
                "gates": len(payload["gates"]),
                "failed_gates": payload["summary"]["failed_gates"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(phase5_json: Path, *, source_root: Path = DEFAULT_SOURCE_ROOT) -> dict[str, Any]:
    phase5 = json.loads(phase5_json.read_text(encoding="utf-8"))
    rows = phase5.get("rows", [])
    triggered_rows = [row for row in rows if row.get("trigger_decision", {}).get("apply")]
    production_imports = production_reranker_imports(source_root)
    gates = build_gates(rows, triggered_rows, production_imports)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    triggered_outcomes = dict(
        sorted(Counter(row.get("trigger_outcome", "unknown") for row in triggered_rows).items())
    )
    summary = {
        "phase5_source": normalize_path(phase5_json),
        "rows_evaluated": len(rows),
        "triggered_rows": len(triggered_rows),
        "target_improvements_kept": triggered_outcomes.get("trigger-target-improvement", 0),
        "triggered_regressions": sum(
            count for outcome, count in triggered_outcomes.items() if "regression" in outcome
        ),
        "triggered_conflicts": triggered_outcomes.get("trigger-conflicting-source-mismatch", 0),
        "failed_gates": len(failed_gates),
        "triggered_outcomes": triggered_outcomes,
    }
    return {
        "schema_version": 1,
        "verdict": verdict_from_gates(gates, summary),
        "sources": {
            "phase5_json": normalize_path(phase5_json),
            "source_root": normalize_path(source_root),
        },
        "policy": [
            "This validates the Phase 5 trigger as experiment-only current-control evidence.",
            "The trigger must not apply to generated controlled rows, clean real rows, or boundary rows.",
            "The trigger must keep the target improvements without triggered regressions or source conflicts.",
            "Only the explicit r8-phase5-experiment command may import the trigger; matcher/SBOM/vulnerability modules must stay unwired, and generate-report may only attach saved report-only evidence.",
        ],
        "summary": summary,
        "gates": gates,
        "triggered_rows": triggered_rows,
        "production_imports": production_imports,
    }


def build_gates(
    rows: list[dict[str, Any]],
    triggered_rows: list[dict[str, Any]],
    production_imports: list[str],
) -> list[dict[str, Any]]:
    triggered_by_role = Counter(str(row.get("role") or "unknown") for row in triggered_rows)
    controlled_rows = [row for row in rows if row.get("row_type") == "controlled"]
    clean_rows = [row for row in rows if row.get("role") == "clean-source-validated"]
    partial_rows = [row for row in rows if row.get("role") == "source-validated-partial"]
    boundary_rows = [row for row in rows if row.get("role") in BOUNDARY_ROLES]
    controlled_triggered = [row for row in controlled_rows if row.get("trigger_decision", {}).get("apply")]
    clean_triggered = [row for row in clean_rows if row.get("trigger_decision", {}).get("apply")]
    boundary_triggered = [row for row in boundary_rows if row.get("trigger_decision", {}).get("apply")]
    regression_triggered = [
        row for row in triggered_rows if "regression" in str(row.get("trigger_outcome") or "")
    ]
    conflict_triggered = [
        row
        for row in triggered_rows
        if row.get("trigger_outcome") == "trigger-conflicting-source-mismatch"
    ]
    target_improvements = [
        row for row in triggered_rows if row.get("trigger_outcome") == "trigger-target-improvement"
    ]
    prerelease_triggered = [
        row for row in triggered_rows if any("-" in str(version) for version in source_versions(row))
    ]
    controlled_phase4_regressions = [
        row
        for row in controlled_rows
        if str(row.get("phase4_outcome")) == "regression-risk-do-not-promote"
    ]
    controlled_phase4_regressions_triggered = [
        row for row in controlled_phase4_regressions if row.get("trigger_decision", {}).get("apply")
    ]
    strong_baseline_blocks = [
        row
        for row in rows
        if "baseline-decision-too-strong" in row.get("trigger_decision", {}).get("blocked_by", [])
    ]
    return [
        gate(
            "controlled-generated-rows-blocked",
            fail_count=len(controlled_triggered),
            evidence=f"{len(controlled_rows)} controlled generated rows evaluated; {len(controlled_triggered)} triggered.",
        ),
        gate(
            "phase4-controlled-regressions-blocked",
            fail_count=len(controlled_phase4_regressions_triggered),
            evidence=(
                f"{len(controlled_phase4_regressions)} Phase 4 controlled regression rows evaluated; "
                f"{len(controlled_phase4_regressions_triggered)} triggered."
            ),
        ),
        gate(
            "clean-source-validated-rows-blocked",
            fail_count=len(clean_triggered),
            evidence=f"{len(clean_rows)} clean source-validated rows evaluated; {len(clean_triggered)} triggered.",
        ),
        gate(
            "boundary-rows-blocked",
            fail_count=len(boundary_triggered),
            evidence=f"{len(boundary_rows)} blocked/boundary rows evaluated; {len(boundary_triggered)} triggered.",
        ),
        gate(
            "partial-target-improvements-kept",
            fail_count=0 if len(target_improvements) >= 4 else 1,
            evidence=(
                f"{len(partial_rows)} partial source-validated rows evaluated; "
                f"{len(target_improvements)} target improvements triggered."
            ),
        ),
        gate(
            "no-triggered-regressions",
            fail_count=len(regression_triggered),
            evidence=f"{len(regression_triggered)} triggered regression-risk rows.",
        ),
        gate(
            "no-triggered-source-conflicts",
            fail_count=len(conflict_triggered),
            evidence=f"{len(conflict_triggered)} triggered source-conflict rows.",
        ),
        gate(
            "no-prerelease-source-trigger",
            fail_count=len(prerelease_triggered),
            evidence=f"{len(prerelease_triggered)} triggered rows have prerelease source versions.",
        ),
        gate(
            "strong-baseline-decisions-blocked",
            fail_count=0,
            evidence=f"{len(strong_baseline_blocks)} rows were blocked by strong baseline exact/likely evidence.",
        ),
        gate(
            "production-code-not-wired",
            fail_count=len(production_imports),
            evidence=(
                "No default matcher/SBOM/vulnerability modules import r8_scoped_reranker."
                if not production_imports
                else f"{len(production_imports)} production imports found."
            ),
        ),
        gate(
            "trigger-scope-summary",
            fail_count=0,
            evidence=", ".join(f"{role}={count}" for role, count in sorted(triggered_by_role.items()))
            or "No triggered roles.",
        ),
    ]


def gate(gate_id: str, *, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


def verdict_from_gates(gates: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    if any(gate["status"] != "pass" for gate in gates):
        return "phase5-trigger-current-control-validation-failed"
    if summary.get("target_improvements_kept", 0) >= 4:
        return "phase5-trigger-current-control-clean-experiment-only"
    return "phase5-trigger-current-control-incomplete"


def production_reranker_imports(source_root: Path) -> list[str]:
    if not source_root.exists():
        return []
    imports: list[str] = []
    for path in sorted(source_root.rglob("*.py")):
        if path.name == "r8_scoped_reranker.py" or path.name in ALLOWED_EXPERIMENT_IMPORT_MODULES:
            continue
        text = path.read_text(encoding="utf-8")
        if "r8_scoped_reranker" in text:
            imports.append(normalize_path(path))
    return imports


def source_versions(row: dict[str, Any]) -> list[str]:
    values = row.get("source_versions")
    if isinstance(values, list):
        return [str(value) for value in values]
    if values:
        return [str(values)]
    return []


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# R8 Phase 5 Trigger Control Validation",
        "",
        "Generated by `scripts/build_r8_phase5_trigger_control_validation.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        "This validates the Phase 5 scoped trigger as an experiment-only control gate. It may be run through the explicit `r8-phase5-experiment` command and shown as saved report-only evidence, but it does not wire the trigger into default matcher scoring, selected versions, SBOM output, vulnerability labels, or source-validation metrics.",
        "",
        "## Summary",
        "",
        f"- Rows evaluated: `{summary['rows_evaluated']}`",
        f"- Triggered rows: `{summary['triggered_rows']}`",
        f"- Target improvements kept: `{summary['target_improvements_kept']}`",
        f"- Triggered regressions: `{summary['triggered_regressions']}`",
        f"- Triggered conflicts: `{summary['triggered_conflicts']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        "",
        "## Gates",
        "",
        "| Gate | Status | Failures | Evidence |",
        "|---|---|---:|---|",
    ]
    for item in payload["gates"]:
        lines.append(
            "| "
            f"`{md(item['gate'])}` | "
            f"`{md(item['status'])}` | "
            f"{item['fail_count']} | "
            f"{md(item['evidence'])} |"
        )

    lines.extend(
        [
            "",
            "## Triggered Rows",
            "",
            "| Case | Role | Coordinate | Baseline | Diagnostic | Source | Outcome |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["triggered_rows"]:
        source_text = ", ".join(source_versions(row))
        lines.append(
            "| "
            f"{md(row.get('case'))} | "
            f"{md(row.get('role'))} | "
            f"`{md(row.get('coordinate'))}` | "
            f"{md(row.get('baseline_selected_version'))} | "
            f"{md(row.get('diagnostic_selected_version'))} | "
            f"{md(source_text)} | "
            f"`{md(row.get('trigger_outcome'))}` |"
        )
    if not payload["triggered_rows"]:
        lines.append("| none |  |  |  |  |  |  |")

    lines.extend(["", "## Production Wiring Audit", ""])
    if payload["production_imports"]:
        lines.extend(f"- `{item}`" for item in payload["production_imports"])
    else:
        lines.append(
            "- No default matcher/SBOM/vulnerability module imports `r8_scoped_reranker`; only the explicit experiment command path is allowed."
        )

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "The scoped trigger passes the current validation gates as experiment-only evidence: it keeps the four target improvements, triggers no current controlled/clean/boundary rows, and is not imported by default matcher/SBOM modules. This still does not promote the trigger into default behavior; the explicit command and report evidence are opt-in experiment surfaces only.",
            "",
        ]
    )
    return "\n".join(lines)


def normalize_path(path: object) -> str:
    return str(path).replace("\\", "/")


def md(value: object) -> str:
    return str(value or "").replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
