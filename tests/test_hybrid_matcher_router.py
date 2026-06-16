from __future__ import annotations

import json

from apk_sbom.cli import main
from apk_sbom.hybrid_matcher_router import (
    build_payload,
    route_matcher_recall_row,
    route_source_gap_row,
    route_wrong_version_pair,
)


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_r8_structural_recall_profile_for_strong_opcode_weak_names():
    routed = route_matcher_recall_row(
        {
            "case_id": "r8-case",
            "coordinate": "com.example:r8-lib",
            "source_version": "1.0.0",
            "best_version": "1.0.0",
            "recall_status": "below-threshold",
            "next_action": "investigate-matcher-threshold-or-feature-recall",
            "opcode_score": "0.91",
            "class_score": "0.10",
            "method_score": "0.12",
            "score_gap_to_best": "0.02",
        },
        index=0,
        case_meta={"r8_obfuscation_profile": "R8/minified"},
        ai_suggestion={"recommendation": "risk_only"},
    )

    assert routed["recommended_profile"] == "r8-structural-recall"
    assert "ai-report-only-triage" in routed["secondary_profiles"]
    assert "case-has-r8-or-minified-profile" in routed["reason_codes"]
    assert routed["report_only"] is True


def test_no_bytecode_signal_is_not_promoted_by_blank_score_gap():
    routed = route_matcher_recall_row(
        {
            "case_id": "boundary",
            "coordinate": "androidx.annotation:annotation",
            "source_version": "1.8.0",
            "best_version": "",
            "recall_status": "no-bytecode-signal",
            "score_gap_to_best": "",
            "opcode_score": "",
            "class_score": "",
            "method_score": "",
        },
        index=0,
        case_meta={},
        ai_suggestion=None,
    )

    assert routed["recommended_profile"] == "boundary-hash-only"
    assert routed["priority"] == "P3"
    assert "no-bytecode-signal" in routed["reason_codes"]


def test_source_gap_add_retry_routes_to_reference_growth_first():
    routed = route_source_gap_row(
        {
            "case_id": "sample",
            "coordinate": "com.squareup.okhttp3:okhttp",
            "source_version": "4.12.0",
            "next_action": "add-or-retry-reference-version-if-bytecode-bearing",
        },
        index=0,
        case_meta={},
    )

    assert routed["recommended_profile"] == "reference-growth-first"
    assert routed["priority"] == "P1"
    assert "vulnerability-focused-review" in routed["secondary_profiles"]


def test_wrong_version_pair_routes_to_version_band_rerank():
    routed = route_wrong_version_pair(
        {
            "coordinate": "androidx.core:core",
            "tool_selected_version": "1.15.0",
            "source_version": "1.16.0",
            "relation": "old-version-steal",
            "rows": 20,
        },
        index=0,
    )

    assert routed["recommended_profile"] == "version-band-rerank"
    assert routed["priority"] == "P1"
    assert "metadata-coherence-rerank" in routed["secondary_profiles"]


def test_build_payload_combines_router_sources(tmp_path):
    matcher = write_json(
        tmp_path / "matcher.json",
        {
            "rows": [
                {
                    "app": "Sample",
                    "case_id": "sample",
                    "coordinate": "androidx.core:core",
                    "source_version": "1.16.0",
                    "best_version": "1.15.0",
                    "recall_status": "below-threshold",
                    "next_action": "investigate-matcher-threshold-or-feature-recall",
                    "score_gap_to_best": "0.003",
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
                    "name": "Sample",
                    "r8_obfuscation_profile": "clean",
                }
            ]
        },
    )
    source_gap = write_json(
        tmp_path / "source-gap.json",
        {
            "rows": [
                {
                    "case_id": "sample",
                    "coordinate": "com.example:missing",
                    "source_version": "2.0.0",
                    "next_action": "add-or-retry-reference-version-if-bytecode-bearing",
                }
            ]
        },
    )
    wrong_version = write_json(
        tmp_path / "wrong-version.json",
        {
            "top_selected_to_source_pairs": [
                {
                    "coordinate": "androidx.core:core",
                    "tool_selected_version": "1.15.0",
                    "source_version": "1.16.0",
                    "relation": "old-version-steal",
                    "rows": 3,
                }
            ],
            "top_coordinates": [
                {
                    "coordinate": "com.google.code.gson:gson",
                    "family": "json",
                    "dominant_relation": "near-version",
                    "rows": 2,
                }
            ],
        },
    )
    ai_suggestions = write_json(
        tmp_path / "ai-suggestions.json",
        {
            "summary": {"recommendation_counts": {"risk_only": 1}},
            "suggestions": [
                {
                    "case_id": "sample",
                    "coordinate": "androidx.core:core",
                    "source_version": "1.16.0",
                    "recommendation": "risk_only",
                }
            ],
        },
    )

    payload = build_payload(
        matcher_recall_json=matcher,
        transparency_json=transparency,
        source_gap_json=source_gap,
        wrong_version_json=wrong_version,
        ai_suggestions_json=ai_suggestions,
    )

    assert payload["schema_version"] == "hybrid-matcher-router-v1"
    assert payload["default_matcher_unchanged"] is True
    assert payload["summary"]["router_rows"] == 4
    assert payload["summary"]["profile_counts"]["version-band-rerank"] >= 2
    assert payload["summary"]["profile_counts"]["reference-growth-first"] == 1
    assert payload["summary"]["ai_recommendation_counts"] == {"risk_only": 1}


def test_cli_writes_hybrid_matcher_router_outputs(tmp_path, capsys):
    matcher = write_json(tmp_path / "matcher.json", {"rows": []})
    transparency = write_json(tmp_path / "transparency.json", {"dataset_cases": []})
    source_gap = write_json(tmp_path / "source-gap.json", {"rows": []})
    wrong_version = write_json(
        tmp_path / "wrong-version.json",
        {
            "top_selected_to_source_pairs": [],
            "top_coordinates": [],
        },
    )
    ai_suggestions = write_json(
        tmp_path / "ai-suggestions.json",
        {"summary": {}, "suggestions": []},
    )
    output_json = tmp_path / "router.json"
    output_doc = tmp_path / "router.md"

    exit_code = main(
        [
            "hybrid-matcher-router",
            "--matcher-recall-json",
            str(matcher),
            "--transparency-json",
            str(transparency),
            "--source-gap-json",
            str(source_gap),
            "--wrong-version-json",
            str(wrong_version),
            "--ai-suggestions-json",
            str(ai_suggestions),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )
    stdout = json.loads(capsys.readouterr().out)
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert stdout["router_rows"] == 0
    assert payload["report_only"] is True
    assert "Hybrid Matcher Router V1" in output_doc.read_text(encoding="utf-8")
