from __future__ import annotations

import json

from apk_sbom.cli import main
from apk_sbom.version_band_rerank_experiment import build_payload


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def make_inputs(tmp_path):
    v2_report = write_json(
        tmp_path / "v2-report.json",
        {
            "match_summary": {
                "decisions": [
                    {
                        "coordinate": "androidx.core:core",
                        "selected_version": "1.16.0",
                        "score": 0.91,
                        "gap_to_next": 0.04,
                    },
                    {
                        "coordinate": "androidx.activity:activity",
                        "selected_version": "1.10.1",
                        "score": 0.88,
                    },
                ]
            }
        },
    )
    router = write_json(
        tmp_path / "router.json",
        {
            "rows": [
                {
                    "row_id": "wrong-version-coordinate:androidx.core",
                    "row_source": "wrong-version-coordinate",
                    "recommended_profile": "version-band-rerank",
                    "coordinate": "androidx.core:core",
                    "priority": "P1",
                    "reason_codes": ["same-major-band-drift"],
                    "evidence": {},
                },
                {
                    "row_id": "matcher-recall:androidx.activity",
                    "row_source": "matcher-recall",
                    "recommended_profile": "version-band-rerank",
                    "case_id": "sample",
                    "coordinate": "androidx.activity:activity",
                    "source_version": "1.10.1",
                    "candidate_version": "1.10.1",
                    "priority": "P1",
                    "reason_codes": ["version-band-or-adjacent-version-family"],
                    "evidence": {
                        "source_score": 0.4,
                        "best_score": 0.4,
                        "score_gap_to_best": 0,
                    },
                },
            ]
        },
    )
    large_analysis = write_json(
        tmp_path / "large-analysis.json",
        {
            "summary": {"baseline_emitted_wrong_version": 2},
            "version_rows": [
                {
                    "analysis_class": "wrong-version",
                    "case_id": "sample",
                    "case_name": "Sample",
                    "case_role": "source-validated-partial",
                    "coordinate": "androidx.core:core",
                    "tool_selected_version": "1.15.0",
                    "correct_source_versions": "1.16.0",
                    "confidence": 0.9,
                    "match_type": "hybrid-exact",
                },
                {
                    "analysis_class": "true-positive-exact-version",
                    "case_id": "sample",
                    "case_name": "Sample",
                    "case_role": "source-validated-partial",
                    "coordinate": "androidx.activity:activity",
                    "tool_selected_version": "1.10.1",
                    "correct_source_versions": "1.10.1",
                    "confidence": 0.88,
                    "match_type": "hybrid-exact",
                },
                {
                    "analysis_class": "false-positive-extra-emission",
                    "case_id": "sample",
                    "case_name": "Sample",
                    "case_role": "source-validated-partial",
                    "coordinate": "androidx.core:core",
                    "tool_selected_version": "1.15.0",
                },
                {
                    "analysis_class": "wrong-version",
                    "case_id": "sample",
                    "coordinate": "com.example:outside",
                    "tool_selected_version": "1.0.0",
                    "correct_source_versions": "2.0.0",
                },
            ],
        },
    )
    dashboard = write_json(
        tmp_path / "v2-dashboard.json",
        {
            "cases": [
                {
                    "case_id": "sample",
                    "paths": {"report": str(v2_report)},
                }
            ]
        },
    )
    return router, large_analysis, dashboard


def test_version_band_rerank_payload_counts_source_known_fix_and_controls(tmp_path):
    router, large_analysis, dashboard = make_inputs(tmp_path)

    payload = build_payload(
        router_json=router,
        large_analysis_json=large_analysis,
        v2_dashboard_json=dashboard,
    )

    summary = payload["summary"]
    assert payload["report_only"] is True
    assert payload["verdict"] == "source-known-rerank-promising-report-only-not-promoted"
    assert summary["baseline_wrong_version_rows_in_scope"] == 1
    assert summary["source_known_fixable_wrong_version_rows"] == 1
    assert summary["exact_control_rows_in_scope"] == 1
    assert summary["exact_control_classification_counts"] == {"control-stays-exact": 1}
    assert summary["false_positive_extra_control_rows_in_scope"] == 1
    assert summary["matcher_recall_router_rows"] == 1
    wrong = payload["wrong_version_rows"][0]
    assert wrong["classification"] == "source-known-rerank-would-fix"
    assert wrong["production_promotion"] is False


def test_version_band_rerank_cli_writes_outputs(tmp_path, capsys):
    router, large_analysis, dashboard = make_inputs(tmp_path)
    output_json = tmp_path / "experiment.json"
    output_doc = tmp_path / "experiment.md"

    exit_code = main(
        [
            "version-band-rerank-experiment",
            "--router-json",
            str(router),
            "--large-analysis-json",
            str(large_analysis),
            "--v2-dashboard-json",
            str(dashboard),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )
    stdout = json.loads(capsys.readouterr().out)
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert stdout["source_known_fixable_wrong_version_rows"] == 1
    assert payload["default_matcher_unchanged"] is True
    assert "Version-Band Rerank Experiment" in output_doc.read_text(encoding="utf-8")
