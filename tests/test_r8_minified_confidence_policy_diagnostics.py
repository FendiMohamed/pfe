from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_r8_minified_confidence_policy_diagnostics.py"
    spec = importlib.util.spec_from_file_location(
        "build_r8_minified_confidence_policy_diagnostics", path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_minified_confidence_policy_keeps_current_artifact_report_only() -> None:
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

    assert payload["verdict"] == "r8-minified-confidence-policy-report-only-ready"
    assert (
        payload["recommendation"]
        == "document-minified-confidence-labels-without-changing-default-selection"
    )
    assert payload["summary"]["rows_classified"] == 286
    assert payload["summary"]["regression_rows_blocked"] == 36
    assert payload["summary"]["phase5_report_only_suggestions"] == 4
    assert payload["summary"]["source_backed_report_only_suggestions"] == 4
    assert payload["summary"]["report_default_selection_changes"] == 0
    assert payload["summary"]["failed_gates"] == 0
    assert payload["summary"]["policy_action_counts"]["surface-report-only-suggestion"] == 4
    assert payload["summary"]["policy_action_counts"]["do-not-change-selected-version"] == 36
    assert all(gate["status"] == "pass" for gate in payload["gates"])


def test_minified_confidence_policy_blocks_dirty_report_boundary(tmp_path: Path) -> None:
    diagnostic = load_script()
    paths = write_minimal_inputs(tmp_path, default_selection_changes=1)

    payload = diagnostic.build_payload(**paths)

    assert payload["verdict"] == "r8-minified-confidence-policy-diagnostic-incomplete"
    failed = {gate["gate"] for gate in payload["gates"] if gate["status"] == "fail"}
    assert "phase5-report-boundary-clean" in failed


def test_minified_confidence_policy_requires_source_backed_suggestions(tmp_path: Path) -> None:
    diagnostic = load_script()
    paths = write_minimal_inputs(tmp_path, diagnostic_source_version="1.0.0")

    payload = diagnostic.build_payload(**paths)

    assert payload["verdict"] == "r8-minified-confidence-policy-diagnostic-incomplete"
    assert payload["summary"]["phase5_report_only_suggestions"] == 1
    assert payload["summary"]["source_backed_report_only_suggestions"] == 0
    failed = {gate["gate"] for gate in payload["gates"] if gate["status"] == "fail"}
    assert "phase5-suggestions-source-backed-report-only" in failed


def write_minimal_inputs(
    tmp_path: Path,
    *,
    default_selection_changes: int = 0,
    diagnostic_source_version: str = "2.0.0",
) -> dict[str, Path]:
    phase4_json = tmp_path / "phase4.json"
    phase5_validation_json = tmp_path / "phase5-validation.json"
    phase5_report_json = tmp_path / "phase5-report.json"
    write_json(
        phase4_json,
        {
            "controlled_cases": [
                {
                    "slug": "generated-lib-r8-shrink",
                    "category": "r8-shrink",
                    "coordinate": "example:lib",
                    "baseline_selected_version": "1.0.0",
                    "diagnostic_selected_version": "2.0.0",
                    "expected_version": "1.0.0",
                    "outcome": "regression-risk-do-not-promote",
                    "top_diagnostic_versions": [
                        diagnostic_row("2.0.0", 0.7000, literal_context=0.0),
                        diagnostic_row("1.0.0", 0.6999, literal_context=0.0),
                    ],
                }
            ],
            "real_component_rows": [
                {
                    "case_name": "Real App",
                    "coordinate": "androidx.core:core",
                    "role": "source-validated-partial",
                    "tags": ["real", "partial", "source-validated", "modern-androidx"],
                    "baseline_selected_version": "1.0.0",
                    "diagnostic_selected_version": "2.0.0",
                    "source_versions": [diagnostic_source_version],
                    "outcome": "real-potential-target-improvement",
                    "top_diagnostic_versions": [
                        diagnostic_row("2.0.0", 0.8500, literal_context=0.30),
                        diagnostic_row("1.0.0", 0.8495, literal_context=0.25),
                    ],
                }
            ],
        },
    )
    write_json(
        phase5_validation_json,
        {
            "verdict": "phase5-trigger-current-control-clean-experiment-only",
            "summary": {"triggered_rows": 1},
            "production_imports": [],
            "triggered_rows": [
                {
                    "case": "Real App",
                    "coordinate": "androidx.core:core",
                    "baseline_selected_version": "1.0.0",
                    "diagnostic_selected_version": "2.0.0",
                    "baseline_version_confidence_label": "low",
                    "trigger_decision": {"profile_id": "sample-profile"},
                }
            ],
        },
    )
    write_json(
        phase5_report_json,
        {
            "verdict": "phase5-report-evidence-clean-experiment-only",
            "summary": {
                "default_selection_changes": default_selection_changes,
            },
        },
    )
    return {
        "phase4_json": phase4_json,
        "phase5_validation_json": phase5_validation_json,
        "phase5_report_json": phase5_report_json,
    }


def diagnostic_row(version: str, score: float, *, literal_context: float) -> dict:
    return {
        "coordinate": "example:lib",
        "version": version,
        "diagnostic_score": score,
        "feature_scores": {
            "basic_block_opcode_fingerprints": 0.8,
            "call_chain_opcode_fingerprints": 0.9,
            "class_neighbor_summaries": 0.8,
            "field_operation_sequences": 0.9,
            "literal_context_features": literal_context,
        },
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")
