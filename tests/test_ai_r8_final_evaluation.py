from __future__ import annotations

import json

from apk_sbom.cli import main
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


def test_cli_writes_final_ai_r8_evaluation(tmp_path, capsys):
    ai_summary = tmp_path / "ai-summary.json"
    ai_metrics = tmp_path / "ai-metrics.json"
    dl_metrics = tmp_path / "dl-metrics.json"
    report_only_demo = tmp_path / "report-only-demo.json"
    output_json = tmp_path / "final.json"
    output_doc = tmp_path / "final.md"
    write_json(
        ai_summary,
        {
            "model": {
                "status": "trained",
                "model_type": "RandomForestClassifier",
                "model_version": "ai-r8-assistant-v1",
                "test_macro_f1": 0.7,
                "majority_baseline_test_accuracy": 0.3,
                "score_threshold_baseline_test_accuracy": 0.2,
                "ablation_study": {
                    "all_features": {
                        "feature_count": 17,
                        "test_macro_f1": 0.7,
                        "test_accuracy": 0.69,
                    }
                },
            },
            "dataset": {"rows": 10},
            "suggestions": {"suggestion_rows": 4},
        },
    )
    write_json(ai_metrics, {"test": {"accuracy": 0.69}})
    write_json(
        dl_metrics,
        {
            "status": "trained",
            "model_type": "torch.nn.TransformerEncoder",
            "dataset": {"rows": 10, "vocab_size": 20},
            "validation": {"macro_f1": 0.8},
            "test": {"macro_f1": 0.9, "accuracy": 0.95, "per_class": {}},
        },
    )
    write_json(
        report_only_demo,
        {
            "ai_report": {"report_only": True, "ai_section_present": True},
            "comparison": {
                "detected_components_unchanged": True,
                "sbom_semantic_content_unchanged": True,
                "vulnerability_labels_unchanged": True,
            },
        },
    )

    exit_code = main(
        [
            "ai-r8-final-eval",
            "--ai-summary-json",
            str(ai_summary),
            "--ai-metrics-json",
            str(ai_metrics),
            "--dl-metrics-json",
            str(dl_metrics),
            "--report-only-demo-json",
            str(report_only_demo),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )
    stdout = json.loads(capsys.readouterr().out)
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert stdout["report_only_guardrail_passed"] is True
    assert payload["phase6b_dl"]["test_macro_f1"] == 0.9
    assert "AI R8 Final Evaluation" in output_doc.read_text(encoding="utf-8")


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
