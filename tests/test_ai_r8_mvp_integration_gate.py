from __future__ import annotations

import json

from apk_sbom.ai_r8_mvp_integration_gate import build_markdown, build_payload
from scripts.build_ai_r8_token_corpus import build_corpus, row_to_tokens


def test_mvp_safe_token_profile_removes_source_shortcuts():
    row = {
        "row_id": "r1",
        "case_id": "case-a",
        "coordinate": "com.google.code.gson:gson",
        "source_version": "2.8.9",
        "candidate_version": "2.8.9",
        "row_source": "matcher-recall",
        "label": "suggest_report_only",
        "features": {
            "best_score": 0.9,
            "source_rank": 1,
            "is_boundary_or_limitation": True,
            "is_partial_real": True,
        },
        "context": {
            "reason_label": "source-context-report-only",
            "next_action": "surface-as-source-context-report-only-suggestion",
        },
    }

    full_tokens = row_to_tokens(row)
    safe_tokens = row_to_tokens(row, profile="mvp-safe")

    assert "source-version:raw:2.8.9" in full_tokens
    assert "source-version:raw:2.8.9" not in safe_tokens
    assert "candidate-version:raw:2.8.9" not in safe_tokens
    assert "coordinate:com.google.code.gson:gson" not in safe_tokens
    assert "feature:source_rank:one-or-more" not in safe_tokens
    assert "feature:is_partial_real:true" not in safe_tokens
    assert not any(token.startswith("context:") for token in safe_tokens)
    assert "candidate-version:major-band:two-three" in safe_tokens


def test_mvp_safe_corpus_marks_profile_and_policy():
    dataset = {
        "rows": [
            {
                "row_id": "r1",
                "case_id": "case-a",
                "coordinate": "com.example:lib",
                "source_version": "1.0.0",
                "candidate_version": "1.0.0",
                "row_source": "emitted-result",
                "label": "confirmed_exact",
                "features": {"best_score": 1.0},
                "context": {},
            }
        ],
        "sources": {},
    }

    corpus = build_corpus(dataset, max_sequence_length=16, profile="mvp-safe")

    assert corpus["profile"] == "mvp-safe"
    assert corpus["mvp_safe"] is True
    assert "source-version tokens" in corpus["excluded_from_mvp_safe_profile"]
    assert corpus["summary"]["rows"] == 1


def test_integration_gate_keeps_report_only_and_blocks_matcher_authority():
    payload = build_payload(
        ai_metrics={
            "status": "trained",
            "model_type": "RandomForestClassifier",
            "dataset": {"rows": 20523},
            "test": {"macro_f1": 0.71},
            "ablation_study": {
                "all_features": {"test_accuracy": 0.69, "test_macro_f1": 0.71}
            },
            "baseline_comparison": {
                "majority_class": {"test_accuracy": 0.38},
                "score_threshold_rule": {"test_accuracy": 0.16},
            },
            "feature_importance": [{"feature": "identity_confidence", "importance": 0.2}],
        },
        ai_suggestions={
            "summary": {
                "suggestion_rows": 13736,
                "recommendation_counts": {"risk_only": 100},
            }
        },
        structured_dl_metrics={
            "status": "trained",
            "model_type": "torch.nn.TransformerEncoder",
            "dataset": {"rows": 20523, "vocab_size": 5000},
            "test": {"macro_f1": 0.97, "accuracy": 0.99},
            "validation": {"macro_f1": 0.98},
            "production_wiring": "disabled",
        },
        mvp_safe_dl_metrics={
            "status": "trained",
            "model_type": "torch.nn.TransformerEncoder",
            "dataset": {
                "rows": 20523,
                "vocab_size": 1000,
                "profile": "mvp-safe",
                "mvp_safe": True,
            },
            "test": {"macro_f1": 0.65, "accuracy": 0.7},
            "validation": {"macro_f1": 0.66},
            "production_wiring": "disabled",
        },
        raw_opcode_dl_metrics={
            "status": "trained",
            "model_type": "torch.nn.TransformerEncoder",
            "dataset": {"method_sequence_rows": 1680, "apks_analyzed": 14},
            "test": {"macro_f1": 0.11, "accuracy": 0.14},
            "baseline_comparison": {
                "best_baseline": "opcode_count_logistic_regression",
                "best_baseline_test_macro_f1": 0.12,
                "delta_vs_best_baseline": -0.01,
                "verdict": "raw-opcode-transformer-research-only-not-promotable",
            },
        },
        independent_corpus={
            "summary": {
                "rows": 31589,
                "training_eligible_rows": 20523,
                "heldout_or_report_only_rows": 11066,
                "unique_case_ids": 150,
                "unique_coordinates": 1370,
                "external_corpus": False,
                "independence_level": "project-heldout-evidence-lanes",
            }
        },
        hybrid_production={
            "report_only": True,
            "default_matcher_unchanged": True,
            "verdict": "promoted-to-production-report-only-not-matcher-authority",
        },
        final_smoke={
            "summary": {
                "all_outputs_unchanged": True,
                "all_hybrid_sections_visible": True,
                "targets": 2,
            }
        },
        strict_gate_matrix={
            "production_promotion": False,
            "default_matcher_unchanged": True,
            "profiles": [
                {
                    "gate_pass_rows": 219,
                    "eligible_rows_after_strict_controls": 0,
                }
            ],
        },
        sources={"unit": "test"},
    )
    markdown = build_markdown(payload)

    assert payload["mvp_integration"]["report_only_ready"] is True
    assert payload["mvp_integration"]["matcher_authority_ready"] is False
    assert (
        payload["model_decisions"]["matcher_or_sbom_authority"]["decision"]
        == "blocked-keep-deterministic-matcher-authority"
    )
    assert "MVP report-only integration ready" in markdown
    assert "automatic CycloneDX SBOM component or version changes" in markdown


def test_integration_gate_payload_is_json_serializable():
    payload = build_payload(
        ai_metrics={},
        ai_suggestions={},
        structured_dl_metrics={},
        mvp_safe_dl_metrics={},
        raw_opcode_dl_metrics={},
        independent_corpus={},
        hybrid_production={},
        final_smoke={},
        strict_gate_matrix={},
    )

    json.dumps(payload)
