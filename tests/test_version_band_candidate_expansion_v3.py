from __future__ import annotations

import json

from apk_sbom.cli import main
from apk_sbom.version_band_candidate_expansion_v3 import (
    build_payload,
    evaluate_promotion_gate,
)


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_candidate_expansion_gate_blocks_current_apk_only_result(tmp_path):
    source_known = write_json(
        tmp_path / "source-known.json",
        {
            "summary": {
                "baseline_wrong_version_rows_in_scope": 582,
                "source_known_fixable_wrong_version_rows": 565,
                "exact_control_rows_in_scope": 820,
                "false_positive_extra_control_rows_in_scope": 120,
            }
        },
    )
    apk_only = write_json(
        tmp_path / "apk-only.json",
        {
            "summary": {
                "rows_evaluated": 1522,
                "wrong_version_rows_in_scope": 582,
                "apk_only_reranker_changes": 0,
                "apk_only_wrong_version_fixes": 0,
                "apk_only_exact_control_regressions": 0,
                "apk_only_false_positive_control_changes": 0,
                "wrong_version_rows_with_source_in_baseline_alternatives": 44,
                "wrong_version_source_candidate_availability_percent": 7.6,
            }
        },
    )

    payload = build_payload(source_known_json=source_known, apk_only_json=apk_only)

    assert payload["verdict"] == "do-not-promote-candidate-expansion-v3"
    assert payload["promotion_gate"]["promotable"] is False
    assert "APK-only reranker produced zero wrong-version fixes" in payload["promotion_gate"]["blockers"]
    assert payload["source_known_upper_bound"]["source_known_fixable_wrong_version_rows"] == 565
    assert payload["apk_only_reranker"]["apk_only_wrong_version_fixes"] == 0


def test_candidate_expansion_gate_can_identify_promotable_shape():
    gate = evaluate_promotion_gate(
        {
            "source_known_fixable_wrong_version_rows": 120,
        },
        {
            "wrong_version_rows_in_scope": 200,
            "apk_only_wrong_version_fixes": 75,
            "apk_only_exact_control_regressions": 0,
            "apk_only_false_positive_control_changes": 0,
            "wrong_version_rows_with_source_in_baseline_alternatives": 80,
        },
    )

    assert gate["promotable"] is True
    assert gate["verdict"] == "promote-version-band-reranker"


def test_candidate_expansion_cli_writes_outputs(tmp_path, capsys):
    source_known = write_json(
        tmp_path / "source-known.json",
        {"summary": {"source_known_fixable_wrong_version_rows": 1}},
    )
    apk_only = write_json(
        tmp_path / "apk-only.json",
        {
            "summary": {
                "wrong_version_rows_in_scope": 1,
                "apk_only_wrong_version_fixes": 0,
                "apk_only_exact_control_regressions": 0,
                "apk_only_false_positive_control_changes": 0,
                "wrong_version_rows_with_source_in_baseline_alternatives": 0,
            }
        },
    )
    output_json = tmp_path / "gate.json"
    output_doc = tmp_path / "gate.md"

    exit_code = main(
        [
            "version-band-candidate-expansion",
            "--source-known-json",
            str(source_known),
            "--apk-only-json",
            str(apk_only),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )
    stdout = json.loads(capsys.readouterr().out)
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert stdout["promotable"] is False
    assert payload["default_matcher_unchanged"] is True
    assert "Version-Band Candidate Expansion V3" in output_doc.read_text(encoding="utf-8")
