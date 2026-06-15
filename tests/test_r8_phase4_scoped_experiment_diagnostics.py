from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_phase4_script():
    path = ROOT / "scripts" / "build_r8_phase4_scoped_experiment_diagnostics.py"
    spec = importlib.util.spec_from_file_location("build_r8_phase4_scoped_experiment_diagnostics", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase4_experiment_classification_blocks_regression_risk():
    phase4 = load_phase4_script()

    assert (
        phase4.classify_experiment_row(
            expected_version="2.8.9",
            baseline_selected_version="2.8.9",
            diagnostic_selected_version="2.8.6",
        )
        == "regression-risk-do-not-promote"
    )


def test_phase4_experiment_classification_marks_target_improvement():
    phase4 = load_phase4_script()

    assert (
        phase4.classify_experiment_row(
            expected_version="2.8.9",
            baseline_selected_version="2.8.6",
            diagnostic_selected_version="2.8.9",
        )
        == "potential-target-improvement"
    )


def test_phase4_verdict_rejects_global_promotion_on_any_regression_risk():
    phase4 = load_phase4_script()

    assert (
        phase4.verdict_from_outcomes(
            {
                "aligned-control-clean": 4,
                "potential-target-improvement": 1,
                "regression-risk-do-not-promote": 1,
            }
        )
        == "phase4-scoped-diagnostic-reject-global-promotion"
    )


def test_phase4_verdict_rejects_global_promotion_on_real_regression_risk():
    phase4 = load_phase4_script()

    assert (
        phase4.verdict_from_outcomes(
            {
                "aligned-control-clean": 4,
                "real-aligned-source-clean": 2,
                "real-regression-risk-do-not-promote": 1,
            }
        )
        == "phase4-scoped-diagnostic-reject-global-promotion"
    )


def test_real_experiment_classification_marks_source_validated_improvement():
    phase4 = load_phase4_script()

    assert (
        phase4.classify_real_experiment_row(
            baseline_selected_version="1.16.0",
            diagnostic_selected_version="1.16.1",
            source_versions=["1.16.1"],
            validation_status="version-mismatch",
            reference_count=3,
            has_apk_features=True,
        )
        == "real-potential-target-improvement"
    )


def test_real_experiment_classification_keeps_unvalidated_layers_separate():
    phase4 = load_phase4_script()

    assert (
        phase4.classify_real_experiment_row(
            baseline_selected_version="2.10.1",
            diagnostic_selected_version="2.8.9",
            source_versions=[],
            validation_status=None,
            reference_count=3,
            has_apk_features=True,
        )
        == "real-layer-covered-unvalidated"
    )


def test_multiscale_scores_are_diagnostic_math_only():
    phase4 = load_phase4_script()
    feature_scores = {
        "call_chain_opcode_fingerprints": 1.0,
        "basic_block_opcode_fingerprints": 0.5,
        "class_neighbor_summaries": 0.0,
        "field_operation_sequences": 1.0,
        "literal_context_features": 0.0,
    }

    assert phase4.weighted_multiscale_score(feature_scores) == 0.525
    assert round(phase4.cosine_similarity({"a": 1, "b": 1}, {"a": 1}), 6) == 0.707107
    assert phase4.set_coverage_score({"x", "y"}, {"x", "z"}) == 0.5
