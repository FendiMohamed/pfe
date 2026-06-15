from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_r8_optimization_aware_diagnostics.py"
    spec = importlib.util.spec_from_file_location("build_r8_optimization_aware_diagnostics", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_optimization_aware_diagnostic_keeps_current_artifact_report_only() -> None:
    diagnostic = load_script()

    payload = diagnostic.build_payload(
        phase4_json=ROOT
        / "data"
        / "results"
        / "experiments"
        / "r8-phase4-scoped-experiment-diagnostics.json",
        phase5_validation_json=ROOT
        / "data"
        / "results"
        / "experiments"
        / "r8-phase5-trigger-control-validation.json",
        phase5_report_json=ROOT
        / "data"
        / "results"
        / "experiments"
        / "r8-phase5-report-evidence"
        / "summary.json",
    )

    assert payload["verdict"] == "r8-optimization-aware-keep-report-only"
    assert (
        payload["recommendation"]
        == "keep-optimization-aware-logic-diagnostic-only-and-improve-confidence-policy"
    )
    assert payload["summary"]["phase4_controlled_regression_blockers"] == 6
    assert payload["summary"]["phase4_real_regression_blockers"] == 30
    assert payload["summary"]["phase5_target_improvements_kept"] == 4
    assert payload["summary"]["report_default_selection_changes"] == 0
    assert payload["summary"]["failed_gates"] == 0


def test_optimization_aware_diagnostic_blocks_dirty_report_boundary(tmp_path: Path) -> None:
    diagnostic = load_script()
    paths = write_minimal_inputs(tmp_path, default_selection_changes=1)

    payload = diagnostic.build_payload(**paths)

    assert payload["verdict"] == "r8-optimization-aware-diagnostic-incomplete"
    failed = {gate["gate"] for gate in payload["gates"] if gate["status"] == "fail"}
    assert "phase5-report-boundary-clean" in failed


def write_minimal_inputs(tmp_path: Path, *, default_selection_changes: int) -> dict[str, Path]:
    phase4_json = tmp_path / "phase4.json"
    phase5_validation_json = tmp_path / "phase5-validation.json"
    phase5_report_json = tmp_path / "phase5-report.json"
    write_json(
        phase4_json,
        {
            "verdict": "phase4-scoped-diagnostic-reject-global-promotion",
            "summary": {
                "controlled_cases": 24,
                "real_component_rows": 262,
                "category_counts": [
                    {
                        "category": "r8-shrink",
                        "outcomes": {"regression-risk-do-not-promote": 2},
                    }
                ],
                "phase5_candidate_scan": {
                    "candidate_improvements": [{"case": "sample"}],
                    "controlled_regression_count": 1,
                    "real_regression_count": 1,
                    "clean_real_regression_count": 1,
                    "top_blocking_coordinates": [
                        {"coordinate": "example:lib", "regressions": 2}
                    ],
                },
            },
        },
    )
    write_json(
        phase5_validation_json,
        {
            "verdict": "phase5-trigger-current-control-clean-experiment-only",
            "summary": {
                "rows_evaluated": 286,
                "triggered_rows": 4,
                "target_improvements_kept": 4,
                "triggered_regressions": 0,
                "triggered_conflicts": 0,
                "failed_gates": 0,
            },
            "production_imports": [],
            "triggered_rows": [],
        },
    )
    write_json(
        phase5_report_json,
        {
            "verdict": "phase5-report-evidence-clean-experiment-only",
            "summary": {
                "reports": 4,
                "phase5_suggestions": 4,
                "report_only_suggestions": 4,
                "default_selection_changes": default_selection_changes,
            },
            "rows": [],
        },
    )
    return {
        "phase4_json": phase4_json,
        "phase5_validation_json": phase5_validation_json,
        "phase5_report_json": phase5_report_json,
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")
