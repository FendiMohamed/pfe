from __future__ import annotations

from apk_sbom.composite_family_shortlist_opt_in_verification import (
    DEFAULT_BROAD_REAL_CASE_IDS,
    DEFAULT_SMOKE_CASE_IDS,
    build_gates,
    select_case_ids,
)


def test_select_case_ids_supports_smoke_broad_and_all_sets() -> None:
    live_validation = {
        "cases": [
            {"case_id": "controlled-a", "dataset_layer": "controlled-generated", "status": "evaluated"},
            {"case_id": "controlled-b", "dataset_layer": "controlled-generated", "status": "evaluated"},
            {"case_id": "aegis", "dataset_layer": "real-apk", "status": "evaluated"},
            {"case_id": "termux", "dataset_layer": "real-apk", "status": "evaluated"},
            {"case_id": "missing-real", "dataset_layer": "real-apk", "status": "missing-apk"},
        ]
    }

    assert select_case_ids(live_validation, "smoke", ()) == list(DEFAULT_SMOKE_CASE_IDS)
    assert select_case_ids(live_validation, "all", ()) == [
        "controlled-a",
        "controlled-b",
        "aegis",
        "termux",
    ]
    broad = select_case_ids(live_validation, "broad", ())
    assert broad[:2] == ["controlled-a", "controlled-b"]
    assert broad[2:] == [
        case_id
        for case_id in DEFAULT_BROAD_REAL_CASE_IDS
        if case_id in {"aegis", "termux"}
    ]


def test_build_gates_passes_clean_control_summary() -> None:
    summary = {
        "live_validation_verdict": "composite-family-shortlist-live-validation-clean-opt-in-candidate",
        "live_validation_failed_gates": 0,
        "requested_control_cases": 2,
        "control_cases_evaluated": 2,
        "missing_control_cases": 0,
        "default_disabled_cases": 2,
        "opt_in_enabled_cases": 2,
        "reference_rows_removed": 3,
        "reportable_selected_version_changes": 0,
    }

    assert {gate["status"] for gate in build_gates(summary)} == {"pass"}
