from __future__ import annotations

import json

from apk_sbom.ai_r8_assistant import (
    build_ai_r8_suggestions,
    build_training_dataset,
    normalize_features,
    optional_ml_status,
    write_training_dataset,
)
from apk_sbom.models import DetectedLibrary
from apk_sbom.report import build_html_report, build_json_report, build_markdown_report
from test_report import make_apk, make_artifacts, make_match_summary


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def make_training_inputs(tmp_path):
    matcher = write_json(
        tmp_path / "matcher.json",
        {
            "rows": [
                {
                    "app": "Sample App",
                    "case_id": "sample",
                    "coordinate": "androidx.core:core",
                    "source_version": "1.16.0",
                    "best_version": "1.16.0",
                    "best_score": "0.91",
                    "score_gap_to_best": "",
                    "source_rank": "1",
                    "identity_confidence": "0.9",
                    "package_score": "0.8",
                    "class_score": "0.7",
                    "method_score": "0.6",
                    "opcode_score": "0.5",
                    "literal_score": "",
                    "dependency_score": "",
                    "matched_packages": "4",
                    "matched_classes": "5",
                    "matched_methods": "6",
                    "recall_status": "report-only-source-context-suggestion",
                    "next_action": "surface-as-source-context-report-only-suggestion",
                }
            ]
        },
    )
    transparency = write_json(
        tmp_path / "transparency.json",
        {
            "dataset_cases": [
                {
                    "case_id": "sample",
                    "role": "source-validated-partial",
                    "r8_obfuscation_profile": "R8/minified signal",
                    "obfuscation_risk": "medium",
                    "dataset_classification": "complete-and-counted",
                }
            ],
            "emitted_result_rows": [
                {
                    "app": "Sample App",
                    "case_id": "sample",
                    "coordinate": "com.google.code.gson:gson",
                    "source_versions": "2.8.9",
                    "detected_version": "2.8.9",
                    "confidence": "0.95",
                    "match_type": "hybrid-exact",
                    "result_class": "exact-confirmed",
                }
            ],
            "source_dependency_rows": [
                {
                    "app": "Sample App",
                    "case_id": "sample",
                    "coordinate": "com.example:metadata-only",
                    "source_version": "1.0.0",
                    "coverage_class": "metadata-only",
                    "reason_label": "metadata/source-only",
                    "triage_bucket": "metadata-or-source-only-boundary",
                }
            ],
        },
    )
    phase5 = write_json(
        tmp_path / "phase5.json",
        {
            "rows": [
                {
                    "case": "Sample App",
                    "role": "source-validated-partial",
                    "row_type": "real",
                    "coordinate": "androidx.core:core",
                    "baseline_selected_version": "1.15.0",
                    "diagnostic_selected_version": "1.16.0",
                    "source_versions": ["1.16.0"],
                    "trigger_outcome": "trigger-target-improvement",
                    "phase4_outcome": "real-potential-target-improvement",
                    "trigger_decision": {
                        "apply": True,
                        "top_score": "0.87",
                        "score_margin": "0.01",
                        "supporting_feature_families": 4,
                        "reason_codes": ["phase4-improvement-profile"],
                    },
                }
            ]
        },
    )
    return matcher, transparency, phase5


def test_dataset_builder_constructs_rows_and_maps_labels(tmp_path):
    matcher, transparency, phase5 = make_training_inputs(tmp_path)

    payload = build_training_dataset(
        matcher_recall_json=matcher,
        transparency_json=transparency,
        phase5_json=phase5,
        r8_obfuscation_json=tmp_path / "missing-r8.json",
    )

    labels = {row["label"] for row in payload["rows"]}
    assert "suggest_report_only" in labels
    assert "confirmed_exact" in labels
    assert "boundary_do_not_suggest" in labels
    assert payload["summary"]["rows"] == 4
    matcher_row = next(row for row in payload["rows"] if row["row_source"] == "matcher-recall")
    assert matcher_row["features"]["literal_score"] == 0.0
    assert matcher_row["features"]["dependency_score"] == 0.0
    assert matcher_row["features"]["is_r8_or_minified"] is True
    assert matcher_row["features"]["is_partial_real"] is True


def test_feature_normalization_converts_blank_numeric_values_to_zero():
    features = normalize_features(
        {
            "best_score": "",
            "source_rank": "",
            "matched_classes": None,
            "is_r8_or_minified": "yes",
        }
    )

    assert features["best_score"] == 0.0
    assert features["source_rank"] == 0
    assert features["matched_classes"] == 0
    assert features["is_r8_or_minified"] is True


def test_boundary_rows_are_labeled_unsafe(tmp_path):
    matcher, transparency, phase5 = make_training_inputs(tmp_path)

    payload = build_training_dataset(
        matcher_recall_json=matcher,
        transparency_json=transparency,
        phase5_json=phase5,
        r8_obfuscation_json=tmp_path / "missing-r8.json",
    )
    boundary = next(row for row in payload["rows"] if row["row_source"] == "boundary")

    assert boundary["label"] == "boundary_do_not_suggest"
    assert boundary["features"]["is_boundary_or_limitation"] is True


def test_optional_ml_dependency_guard_is_non_throwing():
    status = optional_ml_status()

    assert isinstance(status.available, bool)
    assert isinstance(status.missing, list)


def test_suggestion_json_schema_without_optional_model(tmp_path):
    matcher, transparency, phase5 = make_training_inputs(tmp_path)
    dataset = build_training_dataset(
        matcher_recall_json=matcher,
        transparency_json=transparency,
        phase5_json=phase5,
        r8_obfuscation_json=tmp_path / "missing-r8.json",
    )
    dataset_path = tmp_path / "dataset.json"
    write_training_dataset(dataset, json_path=dataset_path, csv_path=tmp_path / "dataset.csv")

    suggestions = build_ai_r8_suggestions(
        dataset_json=dataset_path,
        model_path=tmp_path / "missing-model.joblib",
        metrics_json=tmp_path / "missing-metrics.json",
        output_json=tmp_path / "suggestions.json",
    )

    assert suggestions["schema_version"] == "ai-r8-suggestions-v1"
    assert suggestions["report_only"] is True
    assert suggestions["summary"]["suggestion_rows"] >= 1
    assert {
        "row_id",
        "recommendation",
        "forbidden_effects",
    } <= set(suggestions["suggestions"][0])


def test_report_integration_is_opt_in_and_keeps_components_unchanged():
    component = DetectedLibrary(
        group="androidx.core",
        artifact="core",
        version="1.15.0",
        confidence=0.55,
        match_type="hybrid-candidate",
        evidence=[],
    )
    ai_evidence = {
        "enabled": True,
        "report_only": True,
        "source": "data/results/experiments/ai-r8-assistant/suggestions.json",
        "model_type": "RandomForestClassifier",
        "model_version": "ai-r8-assistant-v1",
        "status": "heuristic-label-fallback",
        "summary": {
            "suggestion_rows": 1,
            "matching_rows": 1,
            "matching_recommendation_counts": {"suggest_report_only": 1},
        },
        "matching_rows": [
            {
                "case_id": "sample",
                "coordinate": "androidx.core:core",
                "source_version": "1.16.0",
                "candidate_version": "1.16.0",
                "recommendation": "suggest_report_only",
                "confidence": 0.6,
            }
        ],
    }

    default_payload = build_json_report(
        make_apk(),
        make_match_summary(),
        [component],
        None,
        make_artifacts(),
    )
    payload = build_json_report(
        make_apk(),
        make_match_summary(),
        [component],
        None,
        make_artifacts(),
        ai_r8_assistance=ai_evidence,
    )
    markdown = build_markdown_report(
        make_apk(),
        make_match_summary(),
        [component],
        None,
        make_artifacts(),
        ai_r8_assistance=ai_evidence,
    )
    html = build_html_report(
        make_apk(),
        make_match_summary(),
        [component],
        None,
        make_artifacts(),
        ai_r8_assistance=ai_evidence,
    )

    assert "ai_r8_assistance" not in default_payload
    assert payload["detected_components"][0]["version"] == "1.15.0"
    assert payload["ai_r8_assistance"]["report_only"] is True
    assert "AI-Assisted R8 Suggestions" in markdown
    assert "does not change detected components" in markdown
    assert "AI-Assisted R8 Suggestions" in html
