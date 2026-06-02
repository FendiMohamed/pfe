from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from apk_sbom.cli import main
from apk_sbom.r8_scoped_reranker import should_apply_scoped_r8_rerank


ROOT = Path(__file__).resolve().parents[1]


def load_phase5_script():
    path = ROOT / "scripts" / "build_r8_phase5_scoped_trigger_diagnostics.py"
    spec = importlib.util.spec_from_file_location("build_r8_phase5_scoped_trigger_diagnostics", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scoped_trigger_applies_to_low_confidence_phase4_target():
    decision = should_apply_scoped_r8_rerank(
        coordinate="androidx.viewpager2:viewpager2",
        baseline_version="1.0.0",
        diagnostic_version="1.1.0",
        top_diagnostic_versions=[
            {
                "diagnostic_score": 0.643486,
                "feature_scores": {
                    "basic_block_opcode_fingerprints": 0.51,
                    "call_chain_opcode_fingerprints": 0.70,
                    "class_neighbor_summaries": 0.55,
                    "field_operation_sequences": 0.82,
                    "literal_context_features": 0.0,
                },
            },
            {"diagnostic_score": 0.625250, "feature_scores": {}},
        ],
        role="source-validated-partial",
        tags=["real", "partial", "source-validated", "security", "androidx"],
        baseline_version_status="candidate",
        baseline_version_confidence_label="low",
        validation_source_versions=["1.1.0"],
    )

    assert decision.apply is True
    assert decision.profile_id == "androidx-viewpager2-1.1.0-modern-or-security-low-confidence"


def test_scoped_trigger_blocks_strong_baseline_even_for_target_profile():
    decision = should_apply_scoped_r8_rerank(
        coordinate="androidx.viewpager2:viewpager2",
        baseline_version="1.0.0",
        diagnostic_version="1.1.0",
        top_diagnostic_versions=[
            {
                "diagnostic_score": 0.833288,
                "feature_scores": {
                    "basic_block_opcode_fingerprints": 0.90,
                    "call_chain_opcode_fingerprints": 0.90,
                    "class_neighbor_summaries": 0.90,
                    "field_operation_sequences": 0.90,
                },
            },
            {"diagnostic_score": 0.818126, "feature_scores": {}},
        ],
        role="source-validated-partial",
        tags=["real", "partial", "source-validated", "native-heavy", "maps"],
        baseline_version_status="exact",
        baseline_version_confidence_label="high",
        validation_source_versions=["1.0.0"],
    )

    assert decision.apply is False
    assert "baseline-decision-too-strong" in decision.blocked_by
    assert "blocked-context-tag" in decision.blocked_by


def test_scoped_trigger_blocks_generated_controls():
    decision = should_apply_scoped_r8_rerank(
        coordinate="commons-codec:commons-codec",
        baseline_version="1.16.1",
        diagnostic_version="1.16.0",
        top_diagnostic_versions=[{"diagnostic_score": 0.82956, "feature_scores": {}}],
        category="r8-rename",
        baseline_version_status="candidate",
        baseline_version_confidence_label="low",
    )

    assert decision.apply is False
    assert "controlled-generated-row" in decision.blocked_by


def test_phase5_payload_keeps_targets_without_triggering_regressions():
    phase5 = load_phase5_script()
    payload = phase5.build_payload(
        ROOT / "data" / "results" / "experiments" / "r8-phase4-scoped-experiment-diagnostics.json"
    )

    assert payload["summary"]["target_improvements_kept"] == 4
    assert payload["summary"]["triggered_regressions"] == 0
    assert payload["summary"]["triggered_conflicts"] == 0
    assert payload["summary"]["triggered_outcomes"] == {"trigger-target-improvement": 4}
    assert payload["verdict"] == "phase5-scoped-trigger-experiment-clean-not-promoted"


def test_phase5_experiment_cli_writes_opt_in_json_only(tmp_path, capsys):
    output_json = tmp_path / "phase5.json"

    exit_code = main(
        [
            "r8-phase5-experiment",
            "--phase4-json",
            str(ROOT / "data" / "results" / "experiments" / "r8-phase4-scoped-experiment-diagnostics.json"),
            "--output-json",
            str(output_json),
            "--json-only",
        ]
    )

    assert exit_code == 0
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["verdict"] == "phase5-scoped-trigger-experiment-clean-not-promoted"
    assert payload["summary"]["target_improvements_kept"] == 4
    assert (
        "The trigger is available only through the explicit r8-phase5-experiment command."
        in payload["policy"]
    )
    console = json.loads(capsys.readouterr().out)
    assert console["json"].endswith("phase5.json")
    assert console["triggered_rows"] == 4
