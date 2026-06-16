from __future__ import annotations

import json

from apk_sbom.cli import main
from apk_sbom.r8_apk_structural_promotion_gate import build_payload


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def make_inputs(tmp_path):
    router = write_json(
        tmp_path / "router.json",
        {
            "rows": [
                {
                    "row_id": "matcher-recall:sample:androidx.core:core:1.16.0",
                    "row_source": "matcher-recall",
                    "recommended_profile": "r8-structural-recall",
                    "case_id": "sample",
                    "app": "Sample",
                    "coordinate": "androidx.core:core",
                    "source_version": "1.16.0",
                    "candidate_version": "1.16.0",
                    "priority": "P1",
                    "evidence": {
                        "best_score": 0.42,
                        "source_score": 0.42,
                        "score_gap_to_best": 0.0,
                        "identity_confidence": 0.41,
                        "package_score": 0.55,
                        "class_score": 0.12,
                        "method_score": 0.18,
                        "opcode_score": 0.91,
                        "literal_score": 0.61,
                        "dependency_score": 0.35,
                        "recall_status": "report-only-uncertain-source-context-suggestion",
                        "next_action": "surface-as-source-context-report-only-suggestion",
                        "ai_recommendation": "risk_only",
                    },
                },
                {
                    "row_id": "matcher-recall:sample:androidx.appcompat:appcompat:1.7.1",
                    "row_source": "matcher-recall",
                    "recommended_profile": "r8-structural-recall",
                    "case_id": "sample",
                    "app": "Sample",
                    "coordinate": "androidx.appcompat:appcompat",
                    "source_version": "1.7.1",
                    "candidate_version": "1.7.1",
                    "priority": "P1",
                    "evidence": {
                        "identity_confidence": 0.52,
                        "class_score": 0.10,
                        "method_score": 0.12,
                        "opcode_score": 0.95,
                        "literal_score": 0.7,
                        "dependency_score": 0.5,
                        "ai_recommendation": "risk_only",
                    },
                },
                {
                    "row_id": "matcher-recall:sample:androidx.media3:media3-ui:1.8.0",
                    "row_source": "matcher-recall",
                    "recommended_profile": "r8-structural-recall",
                    "case_id": "sample",
                    "app": "Sample",
                    "coordinate": "androidx.media3:media3-ui",
                    "source_version": "1.8.0",
                    "candidate_version": "1.8.0",
                    "priority": "P1",
                    "evidence": {
                        "identity_confidence": 0.50,
                        "class_score": 0.10,
                        "method_score": 0.12,
                        "opcode_score": 0.93,
                        "literal_score": 0.7,
                        "dependency_score": 0.5,
                    },
                },
                {
                    "row_id": "matcher-recall:sample:androidx.loader:loader:1.1.0",
                    "row_source": "matcher-recall",
                    "recommended_profile": "r8-structural-recall",
                    "case_id": "sample",
                    "app": "Sample",
                    "coordinate": "androidx.loader:loader",
                    "source_version": "1.1.0",
                    "candidate_version": "1.1.0",
                    "priority": "P1",
                    "evidence": {
                        "class_score": 0.1,
                        "method_score": 0.1,
                        "opcode_score": 0.88,
                        "literal_score": 0.3,
                        "dependency_score": 0.4,
                    },
                },
                {
                    "row_id": "matcher-recall:sample:outside:1.0.0",
                    "row_source": "matcher-recall",
                    "recommended_profile": "coarse-to-fine-recall",
                    "case_id": "sample",
                    "coordinate": "com.example:outside",
                    "source_version": "1.0.0",
                    "candidate_version": "1.0.0",
                    "priority": "P2",
                    "evidence": {},
                },
            ]
        },
    )
    analysis = write_json(
        tmp_path / "analysis.json",
        {
            "version_rows": [
                {
                    "analysis_class": "true-positive-exact-version",
                    "case_id": "sample",
                    "case_role": "partial-source-validated",
                    "coordinate": "androidx.core:core",
                },
                {
                    "analysis_class": "wrong-version",
                    "case_id": "sample",
                    "case_role": "partial-source-validated",
                    "coordinate": "androidx.appcompat:appcompat",
                },
                {
                    "analysis_class": "false-positive-extra-emission",
                    "case_id": "sample",
                    "case_role": "partial-source-validated",
                    "coordinate": "androidx.appcompat:appcompat",
                },
            ]
        },
    )
    ai = write_json(
        tmp_path / "ai.json",
        {
            "suggestions": [
                {
                    "case_id": "sample",
                    "coordinate": "androidx.core:core",
                    "source_version": "1.16.0",
                    "candidate_version": "1.16.0",
                    "recommendation": "risk_only",
                    "confidence": 0.99,
                }
            ]
        },
    )
    return router, analysis, ai


def test_r8_apk_structural_gate_separates_promotion_candidates_and_blockers(tmp_path):
    router, analysis, ai = make_inputs(tmp_path)

    payload = build_payload(
        router_json=router,
        large_analysis_json=analysis,
        ai_suggestions_json=ai,
    )

    summary = payload["summary"]
    assert payload["report_only"] is True
    assert payload["default_matcher_unchanged"] is True
    assert payload["verdict"] == "apk-only-structural-promotion-candidates-need-live-controls"
    assert summary["router_r8_structural_rows"] == 4
    assert summary["gate_pass_rows"] == 3
    assert summary["promotion_candidates"] == 1
    assert summary["blocked_same_coordinate_control_risk"] == 1
    assert summary["blocked_no_representative_exact_control"] == 1
    assert summary["blocked_apk_only_evidence"] == 1
    assert payload["classification_counts"]["promotion-candidate-needs-live-default-test"] == 1
    exact_candidate = [
        row
        for row in payload["rows"]
        if row["classification"] == "promotion-candidate-needs-live-default-test"
    ][0]
    assert exact_candidate["apk_only_gate"]["uses_source_for_decision"] is False
    assert exact_candidate["source_evaluation"]["uses_source_for_gate_decision"] is False
    assert exact_candidate["production_promotion"] is False
    assert exact_candidate["production_promotion_candidate"] is True


def test_r8_apk_structural_gate_cli_writes_outputs(tmp_path, capsys):
    router, analysis, ai = make_inputs(tmp_path)
    output_json = tmp_path / "gate.json"
    output_doc = tmp_path / "gate.md"

    exit_code = main(
        [
            "r8-apk-structural-promotion-gate",
            "--router-json",
            str(router),
            "--large-analysis-json",
            str(analysis),
            "--ai-suggestions-json",
            str(ai),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )
    stdout = json.loads(capsys.readouterr().out)
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert stdout["gate_pass_rows"] == 3
    assert stdout["promotion_candidates"] == 1
    assert payload["summary"]["same_coordinate_control_risk_rows"] == 2
    assert "R8 APK-Only Structural Promotion Gate" in output_doc.read_text(encoding="utf-8")
