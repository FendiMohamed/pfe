from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "build_low_risk_version_band_diagnostics.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("build_low_risk_version_band_diagnostics", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def row(
    case_id: str,
    *,
    role: str,
    baseline_mismatches: list[dict[str, str]],
    mismatches: list[dict[str, str]],
    improved: bool = False,
    regressed: bool = False,
) -> dict:
    return {
        "case_id": case_id,
        "role": role,
        "baseline_mismatches": baseline_mismatches,
        "mismatches": mismatches,
        "improved_vs_baseline": improved,
        "regressed_vs_baseline": regressed,
    }


def mismatch(coordinate: str, version: str, source_versions: str) -> dict[str, str]:
    return {
        "coordinate": coordinate,
        "version": version,
        "source_versions": source_versions,
        "status": "version-mismatch",
    }


def test_collect_changes_separates_resolved_targets_from_introduced_mismatches() -> None:
    module = load_module()
    rows = [
        row(
            "target",
            role="target",
            baseline_mismatches=[mismatch("androidx.core:core", "1.9.0", "1.3.0")],
            mismatches=[],
            improved=True,
        ),
        row(
            "control",
            role="control-clean",
            baseline_mismatches=[],
            mismatches=[mismatch("androidx.core:core", "1.3.0", "1.15.0")],
            regressed=True,
        ),
    ]

    resolved = module.collect_changes(rows, kind="resolved")
    introduced = module.collect_changes(rows, kind="introduced")

    assert resolved == [
        {
            "case_id": "target",
            "role": "target",
            "coordinate": "androidx.core:core",
            "selected_version": "1.9.0",
            "source_versions": "1.3.0",
            "change": "resolved",
        }
    ]
    assert introduced[0]["case_id"] == "control"
    assert introduced[0]["selected_version"] == "1.3.0"


def test_coordinate_summary_marks_cross_app_conflict() -> None:
    module = load_module()
    summary = {
        "resolved_target_mismatches": [
            {"coordinate": "androidx.core:core", "case_id": "audio-source"}
        ],
        "introduced_mismatches": [
            {"coordinate": "androidx.core:core", "case_id": "fdroid"}
        ],
    }

    rows = module.summarize_coordinates(summary)

    assert rows == [
        {
            "coordinate": "androidx.core:core",
            "resolved_target_cases": ["audio-source"],
            "new_mismatch_cases": ["fdroid"],
            "diagnostic_verdict": "benefit-and-regression-conflict",
        }
    ]


def test_promotion_decision_rejects_control_regression() -> None:
    module = load_module()

    decision = module.promotion_decision(
        [row("target", role="target", baseline_mismatches=[], mismatches=[], improved=True)],
        [row("control", role="control-clean", baseline_mismatches=[], mismatches=[], regressed=True)],
    )

    assert decision == "keep-experiment-only-regressions-detected"
