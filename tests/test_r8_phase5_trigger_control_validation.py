from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validation_script():
    path = ROOT / "scripts" / "build_r8_phase5_trigger_control_validation.py"
    spec = importlib.util.spec_from_file_location("build_r8_phase5_trigger_control_validation", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase5_trigger_control_validation_passes_current_artifact():
    validation = load_validation_script()
    payload = validation.build_payload(
        ROOT / "data" / "results" / "experiments" / "r8-phase5-scoped-trigger-diagnostics.json",
        source_root=ROOT / "src" / "apk_sbom",
    )

    assert payload["verdict"] == "phase5-trigger-current-control-clean-experiment-only"
    assert payload["summary"]["target_improvements_kept"] == 4
    assert payload["summary"]["triggered_regressions"] == 0
    assert payload["summary"]["triggered_conflicts"] == 0
    assert payload["summary"]["failed_gates"] == 0


def test_phase5_trigger_control_validation_fails_on_production_wiring(tmp_path):
    validation = load_validation_script()
    source_root = tmp_path / "apk_sbom"
    source_root.mkdir()
    (source_root / "matcher.py").write_text(
        "from apk_sbom.r8_scoped_reranker import should_apply_scoped_r8_rerank\n",
        encoding="utf-8",
    )
    payload = validation.build_payload(
        ROOT / "data" / "results" / "experiments" / "r8-phase5-scoped-trigger-diagnostics.json",
        source_root=source_root,
    )

    assert payload["verdict"] == "phase5-trigger-current-control-validation-failed"
    assert any(gate["gate"] == "production-code-not-wired" for gate in payload["gates"])


def test_verdict_from_gates_reports_incomplete_when_targets_missing():
    validation = load_validation_script()

    assert (
        validation.verdict_from_gates(
            [validation.gate("example", fail_count=0, evidence="ok")],
            {"target_improvements_kept": 3},
        )
        == "phase5-trigger-current-control-incomplete"
    )
