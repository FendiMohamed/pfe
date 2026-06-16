from __future__ import annotations

import json

from apk_sbom.cli import main
from apk_sbom.version_band_apk_reranker import build_payload


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def make_inputs(tmp_path):
    report = write_json(
        tmp_path / "report.json",
        {
            "match_summary": {
                "decisions": [
                    {
                        "coordinate": "androidx.core:core",
                        "selected_version": "1.15.0",
                        "score": 0.90,
                        "alternatives": [
                            {
                                "version": "1.16.0",
                                "score": 0.88,
                                "purl": "pkg:maven/androidx.core/core@1.16.0",
                            }
                        ],
                    },
                    {
                        "coordinate": "androidx.core:core-ktx",
                        "selected_version": "1.16.0",
                        "score": 0.92,
                        "alternatives": [],
                    },
                    {
                        "coordinate": "androidx.core:core-viewtree",
                        "selected_version": "1.16.0",
                        "score": 0.91,
                        "alternatives": [],
                    },
                    {
                        "coordinate": "androidx.activity:activity",
                        "selected_version": "1.10.1",
                        "score": 0.91,
                        "alternatives": [],
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
                    "recommended_profile": "version-band-rerank",
                    "coordinate": "androidx.core:core",
                },
                {
                    "recommended_profile": "version-band-rerank",
                    "coordinate": "androidx.activity:activity",
                },
            ]
        },
    )
    analysis = write_json(
        tmp_path / "analysis.json",
        {
            "summary": {"baseline_emitted_wrong_version": 1},
            "per_apk_rows": [
                {
                    "case_id": "sample",
                    "report_path": str(report),
                }
            ],
            "version_rows": [
                {
                    "analysis_class": "wrong-version",
                    "case_id": "sample",
                    "case_name": "Sample",
                    "case_role": "source-validated-partial",
                    "coordinate": "androidx.core:core",
                    "tool_selected_version": "1.15.0",
                    "correct_source_versions": "1.16.0",
                    "confidence": 0.90,
                },
                {
                    "analysis_class": "true-positive-exact-version",
                    "case_id": "sample",
                    "case_name": "Sample",
                    "case_role": "source-validated-partial",
                    "coordinate": "androidx.activity:activity",
                    "tool_selected_version": "1.10.1",
                    "correct_source_versions": "1.10.1",
                    "confidence": 0.91,
                },
            ],
        },
    )
    return router, analysis


def test_apk_only_reranker_uses_sibling_anchors_without_source_for_decision(tmp_path):
    router, analysis = make_inputs(tmp_path)

    payload = build_payload(
        router_json=router,
        large_analysis_json=analysis,
        max_score_drop=0.05,
        min_sibling_era_anchors=2,
    )

    wrong = next(row for row in payload["rows"] if row["analysis_class"] == "wrong-version")
    assert payload["summary"]["apk_only_wrong_version_fixes"] == 1
    assert payload["verdict"] == "apk-only-reranker-promising-needs-expanded-controls"
    assert wrong["apk_only_decision"]["would_change"] is True
    assert wrong["apk_only_decision"]["suggested_version"] == "1.16.0"
    assert wrong["evaluation"]["classification"] == "apk-only-rerank-would-fix"
    assert wrong["evaluation"]["uses_source_for_decision"] is False


def test_apk_only_reranker_blocks_without_enough_sibling_anchors(tmp_path):
    router, analysis = make_inputs(tmp_path)

    payload = build_payload(
        router_json=router,
        large_analysis_json=analysis,
        max_score_drop=0.05,
        min_sibling_era_anchors=3,
    )

    wrong = next(row for row in payload["rows"] if row["analysis_class"] == "wrong-version")
    assert payload["summary"]["apk_only_reranker_changes"] == 0
    assert wrong["apk_only_decision"]["would_change"] is False
    assert wrong["apk_only_decision"]["reason"] == "insufficient-sibling-era-anchors"


def test_apk_only_reranker_cli_writes_outputs(tmp_path, capsys):
    router, analysis = make_inputs(tmp_path)
    output_json = tmp_path / "apk-reranker.json"
    output_doc = tmp_path / "apk-reranker.md"

    exit_code = main(
        [
            "version-band-apk-reranker",
            "--router-json",
            str(router),
            "--large-analysis-json",
            str(analysis),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )
    stdout = json.loads(capsys.readouterr().out)
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert stdout["apk_only_wrong_version_fixes"] == 1
    assert payload["default_matcher_unchanged"] is True
    assert "APK-Only Version-Band Reranker V2" in output_doc.read_text(encoding="utf-8")
