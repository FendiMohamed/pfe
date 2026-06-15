from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.composite_family_shortlist_default_promotion import build_payload


def test_default_promotion_readiness_passes_clean_gate_chain(tmp_path: Path) -> None:
    paths = write_inputs(tmp_path)

    payload = build_payload(**paths)

    assert payload["verdict"] == "composite-family-shortlist-default-promotion-ready"
    assert (
        payload["recommendation"]
        == "safe-to-attempt-default-promotion-with-disable-flag-and-regression-tests"
    )
    assert payload["summary"]["failed_gates"] == 0
    assert payload["summary"]["live_cases_evaluated"] == 81
    assert payload["summary"]["opt_in_control_cases_evaluated"] == 81
    assert payload["summary"]["reference_rows_removed"] == 1347


def test_default_promotion_readiness_rejects_reportable_drift(tmp_path: Path) -> None:
    paths = write_inputs(tmp_path, opt_in_reportable_changes=1)

    payload = build_payload(**paths)

    assert payload["verdict"] == "composite-family-shortlist-default-promotion-not-ready"
    failed = {gate["gate"] for gate in payload["gates"] if gate["status"] == "fail"}
    assert "no-reportable-selected-version-drift" in failed


def test_default_promotion_readiness_requires_all_case_opt_in(tmp_path: Path) -> None:
    paths = write_inputs(tmp_path, case_set="broad", opt_in_cases=66, opt_in_real=4)

    payload = build_payload(**paths)

    assert payload["verdict"] == "composite-family-shortlist-default-promotion-not-ready"
    failed = {gate["gate"] for gate in payload["gates"] if gate["status"] == "fail"}
    assert "full-opt-in-control-inventory-covered" in failed
    assert "controlled-and-real-coverage" in failed
    assert "all-case-opt-in-control-clean" in failed


def write_inputs(
    tmp_path: Path,
    *,
    case_set: str = "all",
    opt_in_cases: int = 81,
    opt_in_real: int = 19,
    opt_in_reportable_changes: int = 0,
) -> dict[str, Path]:
    live_validation_json = tmp_path / "live-validation.json"
    opt_in_json = tmp_path / "opt-in.json"
    write_json(
        live_validation_json,
        {
            "verdict": "composite-family-shortlist-live-validation-clean-opt-in-candidate",
            "summary": {
                "cases_evaluated": 81,
                "cases_requested": 81,
                "controlled_cases_evaluated": 62,
                "real_cases_evaluated": 19,
                "failed_gates": 0,
                "reference_rows_before": 8100,
                "reference_rows_retained": 6753,
                "reference_rows_removed": 1347,
                "reference_row_reduction_ratio": 0.166296,
                "tracked_source_family_rows": 286,
                "source_family_losses": 0,
                "source_selection_regressions": 0,
                "source_selection_improvements": 0,
                "reportable_selected_version_changes": 0,
            },
            "gates": [],
        },
    )
    write_json(
        opt_in_json,
        {
            "case_set": case_set,
            "verdict": "composite-family-shortlist-opt-in-matcher-experiment-ready",
            "summary": {
                "control_cases_evaluated": opt_in_cases,
                "requested_control_cases": opt_in_cases,
                "controlled_cases_evaluated": 62,
                "real_cases_evaluated": opt_in_real,
                "default_disabled_cases": opt_in_cases,
                "opt_in_enabled_cases": opt_in_cases,
                "reference_rows_removed": 1347,
                "reportable_selected_version_changes": opt_in_reportable_changes,
                "failed_gates": 0,
                "case_cache_hits": opt_in_cases,
                "case_cache_misses": 0,
            },
            "gates": [],
        },
    )
    return {
        "live_validation_json": live_validation_json,
        "opt_in_json": opt_in_json,
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")
