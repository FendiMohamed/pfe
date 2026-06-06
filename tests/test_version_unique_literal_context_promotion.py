from __future__ import annotations

import json

from apk_sbom.version_unique_literal_context_promotion import build_payload


def row(case: str, classification: str, matches: int) -> dict:
    return {
        "case_id": case,
        "coordinate": "androidx.example:example",
        "baseline_selected_version": "1.0.0",
        "source_versions": ["1.1.0"],
        "version_unique_literal_context_decision": {
            "classification": classification,
            "suggested_version": "1.1.0",
            "suggested_unique_literal_context_matches": matches,
            "suggested_unique_literal_context_score": 0.5,
        },
    }


def test_promotion_candidate_filters_one_match_regressions(tmp_path) -> None:
    source = tmp_path / "diagnostic.json"
    source.write_text(
        json.dumps(
            {
                "verdict": "version-unique-literal-context-rejected-regression-risk",
                "suggested_rows": [
                    row("kept", "potential-target-improvement-needs-control-matrix", 7),
                    row("filtered", "regression-risk-do-not-promote", 1),
                ],
            }
        ),
        encoding="utf-8",
    )

    payload = build_payload(source)

    assert (
        payload["verdict"]
        == "version-unique-literal-context-opt-in-candidate-clean-diagnostic-matrix"
    )
    assert payload["summary"]["kept_replacement_suggestions"] == 1
    assert payload["summary"]["filtered_low_support_suggestions"] == 1
    assert payload["summary"]["regression_risks"] == 0
