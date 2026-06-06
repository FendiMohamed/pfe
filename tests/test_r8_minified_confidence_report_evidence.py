from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_r8_minified_confidence_report_evidence.py"
    spec = importlib.util.spec_from_file_location(
        "build_r8_minified_confidence_report_evidence", path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_minified_confidence_report_evidence_accepts_clean_report_only_rows(
    tmp_path: Path,
) -> None:
    diagnostic = load_script()
    report_path = write_report(tmp_path / "report.json")

    payload = diagnostic.build_payload([report_path])

    assert payload["verdict"] == "r8-minified-confidence-report-evidence-clean-report-only"
    assert payload["summary"]["reports"] == 1
    assert payload["summary"]["reports_with_policy_evidence"] == 1
    assert payload["summary"]["report_only_suggestions"] == 1
    assert payload["summary"]["blocked_regression_risk_rows"] == 1
    assert payload["summary"]["default_selection_changes"] == 0


def test_minified_confidence_report_evidence_blocks_default_selection_changes(
    tmp_path: Path,
) -> None:
    diagnostic = load_script()
    report_path = write_report(tmp_path / "report.json", component_version="1.1.0")

    payload = diagnostic.build_payload([report_path])

    assert (
        payload["verdict"]
        == "r8-minified-confidence-report-evidence-failed-default-selection-changed"
    )
    assert payload["summary"]["default_selection_changes"] == 2


def write_report(path: Path, *, component_version: str = "1.0.0") -> Path:
    path.write_text(
        json.dumps(
            {
                "artifacts": {"sbom_json": "sample/sbom.cdx.json"},
                "detected_components": [
                    {
                        "group": "androidx.viewpager2",
                        "artifact": "viewpager2",
                        "version": component_version,
                    }
                ],
                "r8_minified_confidence_policy": {
                    "report_only": True,
                    "summary": {
                        "matching_report_only_suggestions": 1,
                        "matching_blocked_regression_risks": 1,
                    },
                    "matching_report_only_suggestions": [
                        row("surface-report-only-suggestion", "1.1.0")
                    ],
                    "matching_blocked_regression_risks": [
                        row("do-not-change-selected-version", "1.2.0")
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def row(policy_action: str, diagnostic_version: str) -> dict:
    return {
        "case": "sample",
        "coordinate": "androidx.viewpager2:viewpager2",
        "baseline_selected_version": "1.0.0",
        "diagnostic_selected_version": diagnostic_version,
        "confidence_label": "low-confidence-source-backed",
        "policy_action": policy_action,
    }
