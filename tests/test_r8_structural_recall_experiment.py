from __future__ import annotations

import json

from apk_sbom.cli import main
from apk_sbom.r8_structural_recall_experiment import build_payload


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
                    "reason_codes": ["strong-opcode-weak-class-method-signal"],
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
                    "reason_codes": ["strong-opcode-weak-class-method-signal"],
                    "evidence": {
                        "class_score": 0.1,
                        "method_score": 0.1,
                        "opcode_score": 0.88,
                        "literal_score": 0.3,
                        "dependency_score": 0.4,
                        "recall_status": "suppressed-uncertain",
                        "next_action": "inspect-report-filter-or-family-suppression",
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
                    "coordinate": "androidx.core:core",
                },
                {
                    "analysis_class": "wrong-version",
                    "case_id": "sample",
                    "coordinate": "androidx.core:core",
                },
                {
                    "analysis_class": "false-positive-extra-emission",
                    "case_id": "sample",
                    "coordinate": "androidx.core:core",
                },
                {
                    "analysis_class": "wrong-version",
                    "case_id": "sample",
                    "coordinate": "com.example:outside",
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
                    "recommendation": "suggest_report_only",
                    "confidence": 0.99,
                },
                {
                    "case_id": "sample",
                    "coordinate": "androidx.loader:loader",
                    "source_version": "1.1.0",
                    "candidate_version": "1.1.0",
                    "recommendation": "suppress_uncertain",
                    "confidence": 0.98,
                },
            ]
        },
    )
    return router, analysis, ai


def test_r8_structural_recall_payload_counts_candidates_and_controls(tmp_path):
    router, analysis, ai = make_inputs(tmp_path)

    payload = build_payload(
        router_json=router,
        large_analysis_json=analysis,
        ai_suggestions_json=ai,
    )

    summary = payload["summary"]
    assert payload["report_only"] is True
    assert payload["default_matcher_unchanged"] is True
    assert payload["verdict"] == "report-only-structural-recall-useful-not-promoted"
    assert summary["router_r8_structural_rows"] == 2
    assert summary["report_only_structural_recall_candidates"] == 1
    assert summary["blocked_rows"] == 1
    assert summary["exact_control_rows_in_scope"] == 1
    assert summary["wrong_version_control_rows_in_scope"] == 1
    assert summary["false_positive_control_rows_in_scope"] == 1
    candidate = payload["rows"][0]
    assert candidate["classification"] == "report-only-structural-recall-candidate"
    assert candidate["production_promotion"] is False
    assert "strong-opcode" in candidate["structural_signals"]
    assert "weak-class-method-names" in candidate["structural_signals"]


def test_r8_structural_recall_cli_writes_outputs(tmp_path, capsys):
    router, analysis, ai = make_inputs(tmp_path)
    output_json = tmp_path / "experiment.json"
    output_doc = tmp_path / "experiment.md"

    exit_code = main(
        [
            "r8-structural-recall-experiment",
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
    assert stdout["report_only_structural_recall_candidates"] == 1
    assert payload["default_matcher_unchanged"] is True
    assert "R8 Structural Recall Experiment" in output_doc.read_text(encoding="utf-8")
