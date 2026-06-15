from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "evaluate_low_risk_source_versions.py"


def load_module():
    spec = importlib.util.spec_from_file_location("evaluate_low_risk_source_versions", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_select_cases_filters_targets() -> None:
    module = load_module()

    cases = module.select_cases(None, ["target"])

    assert {case.case_id for case in cases} == {"stopwatch", "bubble", "audio-source"}


def test_build_markdown_marks_improvements_and_regressions() -> None:
    module = load_module()
    summary = {
        "experiment_title": "Demo",
        "db_path": "demo.sqlite",
        "candidate_versions": ["androidx.core:core:1.3.0"],
        "rows": [
            {
                "case_id": "target",
                "role": "target",
                "detected_components": 1,
                "confirmed": 1,
                "version_mismatches": 0,
                "missing": 0,
                "delta_confirmed": 1,
                "delta_version_mismatches": -1,
                "delta_missing": 0,
                "improved_vs_baseline": True,
                "regressed_vs_baseline": False,
                "mismatches": [],
            },
            {
                "case_id": "control",
                "role": "control-clean",
                "detected_components": 1,
                "confirmed": 0,
                "version_mismatches": 1,
                "missing": 0,
                "delta_confirmed": -1,
                "delta_version_mismatches": 1,
                "delta_missing": 0,
                "improved_vs_baseline": False,
                "regressed_vs_baseline": True,
                "mismatches": [
                    {
                        "coordinate": "androidx.core:core",
                        "version": "1.3.0",
                        "source_versions": "1.9.0",
                        "status": "version-mismatch",
                    }
                ],
            },
        ],
    }

    doc = module.build_markdown(summary)

    assert "| target | target | 1 | 1 | 0 | 0 | +1 confirmed, -1 mismatches, +0 missing | improved |" in doc
    assert "| control | control-clean | 1 | 0 | 1 | 0 | -1 confirmed, +1 mismatches, +0 missing | regressed |" in doc
    assert "androidx.core:core" in doc
