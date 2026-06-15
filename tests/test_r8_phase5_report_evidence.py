from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_report_evidence_script():
    path = ROOT / "scripts" / "build_r8_phase5_report_evidence.py"
    spec = importlib.util.spec_from_file_location("build_r8_phase5_report_evidence", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_report(path: Path, *, component_version: str = "1.0.0", report_only: bool = True) -> None:
    path.parent.mkdir(parents=True)
    payload = {
        "detected_components": [
            {
                "group": "androidx.viewpager2",
                "artifact": "viewpager2",
                "version": component_version,
            }
        ],
        "artifacts": {"sbom_json": str(path.with_name("sbom.cdx.json"))},
        "r8_phase5_experiment": {
            "report_only": report_only,
            "matching_triggered_rows": [
                {
                    "case": "sample",
                    "coordinate": "androidx.viewpager2:viewpager2",
                    "baseline_selected_version": "1.0.0",
                    "diagnostic_selected_version": "1.1.0",
                    "source_versions": ["1.1.0"],
                    "trigger_outcome": "target_improvement",
                    "trigger_decision": {"profile_id": "androidx-version-drift"},
                }
            ],
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_report_evidence_summary_accepts_clean_report_only_rows(tmp_path):
    evidence = load_report_evidence_script()
    reports = [tmp_path / "one" / "report.json", tmp_path / "two" / "report.json"]
    for report in reports:
        write_report(report)

    payload = evidence.build_payload(reports)

    assert payload["verdict"] == "phase5-report-evidence-clean-experiment-only"
    assert payload["summary"]["reports"] == 2
    assert payload["summary"]["reports_with_matching_suggestions"] == 2
    assert payload["summary"]["phase5_suggestions"] == 2
    assert payload["summary"]["default_selection_changes"] == 0
    assert all(row["mvp_selected_version"] == "1.0.0" for row in payload["rows"])
    assert all(row["phase5_suggestion"] == "1.1.0" for row in payload["rows"])


def test_report_evidence_summary_fails_when_default_selection_changes(tmp_path):
    evidence = load_report_evidence_script()
    report = tmp_path / "changed" / "report.json"
    write_report(report, component_version="1.1.0")

    payload = evidence.build_payload([report])

    assert payload["verdict"] == "phase5-report-evidence-failed-default-selection-changed"
    assert payload["summary"]["default_selection_changes"] == 1


def test_report_evidence_summary_fails_when_rows_are_not_report_only(tmp_path):
    evidence = load_report_evidence_script()
    report = tmp_path / "not-report-only" / "report.json"
    write_report(report, report_only=False)

    payload = evidence.build_payload([report])

    assert payload["verdict"] == "phase5-report-evidence-failed-non-report-only-suggestion"
    assert payload["summary"]["report_only_suggestions"] == 0
