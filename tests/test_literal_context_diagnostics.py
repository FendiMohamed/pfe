from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.cli import main
from apk_sbom.literal_context_diagnostics import (
    build_payload,
    classify_literal_context_row,
)


ROOT = Path(__file__).resolve().parents[1]
PHASE4_JSON = (
    ROOT
    / "data"
    / "results"
    / "experiments"
    / "r8-phase4-scoped-experiment-diagnostics.json"
)


def candidate(version: str, literal_context_score: float, diagnostic_score: float = 0.0) -> dict:
    return {
        "version": version,
        "diagnostic_score": diagnostic_score,
        "feature_scores": {
            "literal_context_features": literal_context_score,
        },
    }


def test_literal_context_classifier_blocks_source_validated_regression() -> None:
    decision = classify_literal_context_row(
        selected_version="1.0.0",
        source_versions=["1.0.0"],
        candidates=[
            candidate("1.1.0", 0.60),
            candidate("1.0.0", 0.40),
        ],
    )

    assert decision.classification == "regression-risk-do-not-promote"
    assert decision.suggested_version == "1.1.0"


def test_literal_context_classifier_marks_source_validated_target_improvement() -> None:
    decision = classify_literal_context_row(
        selected_version="1.0.0",
        source_versions=["1.1.0"],
        candidates=[
            candidate("1.1.0", 0.60),
            candidate("1.0.0", 0.40),
        ],
    )

    assert decision.classification == "potential-target-improvement-needs-control-matrix"
    assert decision.suggested_version == "1.1.0"


def test_saved_fixture_rejects_raw_literal_context_reranking() -> None:
    payload = build_payload(PHASE4_JSON)

    assert payload["verdict"] == "literal-context-raw-score-rejected-regression-risk"
    assert payload["summary"]["literal_context_suggestions"] == 2
    assert payload["summary"]["potential_target_improvements"] == 0
    assert payload["summary"]["regression_risks"] == 2


def test_cli_writes_opt_in_literal_context_diagnostics(tmp_path, capsys) -> None:
    output_json = tmp_path / "literal-context.json"
    output_doc = tmp_path / "literal-context.md"

    exit_code = main(
        [
            "literal-context-experiment",
            "--input-json",
            str(PHASE4_JSON),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["verdict"] == "literal-context-raw-score-rejected-regression-risk"
    assert output_doc.exists()
    console = json.loads(capsys.readouterr().out)
    assert console["json"].endswith("literal-context.json")


def test_default_matcher_and_report_do_not_import_literal_context_diagnostics() -> None:
    matcher_text = (ROOT / "src/apk_sbom/matcher.py").read_text(encoding="utf-8")
    report_text = (ROOT / "src/apk_sbom/report.py").read_text(encoding="utf-8")

    assert "literal_context_diagnostics" not in matcher_text
    assert "from apk_sbom.literal_context_diagnostics" not in report_text
