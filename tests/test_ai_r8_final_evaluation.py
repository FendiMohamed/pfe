from __future__ import annotations

from scripts.build_ai_r8_final_evaluation import build_final_evaluation, build_markdown


def test_final_evaluation_combines_ml_dl_and_report_only_guardrail():
    payload = build_final_evaluation(
        ai_summary={
            "model": {
                "status": "trained",
                "model_type": "RandomForestClassifier",
                "model_version": "ai-r8-assistant-v1",
                "test_macro_f1": 0.7,
                "majority_baseline_test_accuracy": 0.3,
                "score_threshold_baseline_test_accuracy": 0.2,
                "top_feature_importance": [
                    {"feature": "identity_confidence", "importance": 0.5}
                ],
                "ablation_study": {
                    "all_features": {
                        "feature_count": 17,
                        "test_macro_f1": 0.7,
                        "test_accuracy": 0.69,
                    }
                },
            },
            "dataset": {
                "rows": 10,
                "labels": {"risk_only": 5},
            },
            "suggestions": {"suggestion_rows": 4},
        },
        ai_metrics={"test": {"accuracy": 0.69}},
        dl_metrics={
            "status": "trained",
            "model_type": "torch.nn.TransformerEncoder",
            "task": "multiclass identity-risk classification",
            "dataset": {
                "rows": 10,
                "vocab_size": 20,
                "splits": {"train": 7, "validation": 1, "test": 2},
            },
            "validation": {"macro_f1": 0.8},
            "test": {
                "macro_f1": 0.9,
                "accuracy": 0.95,
                "per_class": {
                    "risk_only": {
                        "precision": 1.0,
                        "recall": 0.5,
                        "f1": 0.66,
                        "support": 2,
                    }
                },
            },
        },
        report_only_demo={
            "ai_report": {
                "report_only": True,
                "ai_section_present": True,
                "matching_rows": 2,
                "matching_recommendation_counts": {"risk_only": 2},
            },
            "comparison": {
                "detected_components_unchanged": True,
                "sbom_semantic_content_unchanged": True,
                "vulnerability_labels_unchanged": True,
            },
        },
        sources={"unit": "test"},
    )
    markdown = build_markdown(payload)

    assert payload["report_only"] is True
    assert payload["report_only_proof"]["guardrail_passed"] is True
    assert payload["phase6a_ml"]["test_macro_f1"] == 0.7
    assert payload["phase6b_dl"]["test_macro_f1"] == 0.9
    assert "Phase 6A: Classical ML" in markdown
    assert "Phase 6B: DL Prototype" in markdown
    assert "Guardrail passed" in markdown
