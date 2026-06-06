from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.version_unique_literal_context_default_promotion import build_payload


def test_default_promotion_readiness_passes_clean_gate_chain(tmp_path) -> None:
    paths = write_inputs(tmp_path)

    payload = build_payload(
        **paths,
        min_controlled_rows=24,
        min_real_rows=224,
    )

    assert payload["verdict"] == "version-unique-literal-context-default-promotion-ready"
    assert payload["recommendation"] == "safe-to-attempt-default-promotion-with-regression-tests"
    assert payload["summary"]["failed_gates"] == 0
    assert payload["summary"]["broad_controlled_rows"] == 24
    assert payload["summary"]["broad_real_source_validated_rows"] == 224
    assert payload["summary"]["report_validation_confirmed_delta"] == 1


def test_default_promotion_readiness_rejects_controlled_kept_row(tmp_path) -> None:
    paths = write_inputs(tmp_path, kept_row_type="controlled")

    payload = build_payload(
        **paths,
        min_controlled_rows=24,
        min_real_rows=224,
    )

    assert payload["verdict"] == "version-unique-literal-context-default-promotion-not-ready"
    failed = {gate["gate"] for gate in payload["gates"] if gate["status"] == "fail"}
    assert "no-controlled-kept-replacements" in failed


def write_inputs(tmp_path: Path, *, kept_row_type: str = "real-source-validated") -> dict:
    diagnostic_json = tmp_path / "diagnostic.json"
    promotion_json = tmp_path / "promotion.json"
    control_validation_json = tmp_path / "control-validation.json"
    write_json(
        diagnostic_json,
        {
            "verdict": "version-unique-literal-context-rejected-regression-risk",
            "summary": {
                "rows_inspected": 248,
                "controlled_rows_inspected": 24,
                "real_source_validated_rows_inspected": 224,
                "version_unique_literal_context_suggestions": 4,
                "potential_target_improvements": 2,
                "regression_risks": 2,
            },
        },
    )
    write_json(
        promotion_json,
        {
            "verdict": "version-unique-literal-context-opt-in-candidate-clean-diagnostic-matrix",
            "summary": {
                "source_replacement_suggestions": 4,
                "minimum_unique_literal_context_matches": 2,
                "kept_replacement_suggestions": 1,
                "filtered_low_support_suggestions": 3,
                "potential_target_improvements": 1,
                "regression_risks": 0,
            },
            "kept_rows": [
                suggestion_row(
                    row_type=kept_row_type,
                    classification="potential-target-improvement-needs-control-matrix",
                    matches=7,
                )
            ],
            "filtered_rows": [
                suggestion_row(
                    row_type="real-source-validated",
                    classification="regression-risk-do-not-promote",
                    matches=1,
                )
            ],
        },
    )
    write_json(
        control_validation_json,
        {
            "verdict": "version-unique-literal-context-current-control-opt-in-pass",
            "summary": {
                "cases_evaluated": 3,
                "changed_rows": 1,
                "confirmed_delta": 1,
                "version_mismatch_delta": -1,
                "missing_delta": 0,
                "failed_gates": 0,
            },
            "changed_rows": [
                {
                    "app_id": "vlc-android",
                    "coordinate": "androidx.recyclerview:recyclerview",
                    "baseline_version": "1.2.1",
                    "opt_in_version": "1.3.2",
                    "baseline_status": "version-mismatch",
                    "opt_in_status": "confirmed",
                    "source_versions": ["1.3.2"],
                }
            ],
        },
    )
    return {
        "diagnostic_json": diagnostic_json,
        "promotion_json": promotion_json,
        "control_validation_json": control_validation_json,
    }


def suggestion_row(*, row_type: str, classification: str, matches: int) -> dict:
    return {
        "case_id": "vlc-android",
        "coordinate": "androidx.recyclerview:recyclerview",
        "baseline_selected_version": "1.2.1",
        "row_type": row_type,
        "source_versions": ["1.3.2"],
        "version_unique_literal_context_decision": {
            "classification": classification,
            "suggested_version": "1.3.2",
            "suggested_unique_literal_context_matches": matches,
        },
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
