from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.cli import main
from apk_sbom.matcher import FeatureSet, ReferenceComponentFeatures
from apk_sbom.version_unique_literal_context_diagnostics import (
    classify_version_unique_literal_context_row,
    rank_version_unique_literal_context_candidates,
)


ROOT = Path(__file__).resolve().parents[1]


def reference(version: str, literal_context_features: set[str], component_id: int) -> ReferenceComponentFeatures:
    return ReferenceComponentFeatures(
        component_id=component_id,
        coordinate="com.example:library",
        group_id="com.example",
        artifact_id="library",
        version=version,
        purl=f"pkg:maven/com.example/library@{version}",
        features=FeatureSet(
            packages=set(),
            classes=set(),
            methods=set(),
            literal_context_features=literal_context_features,
        ),
    )


def candidate(version: str, score: float, matches: int, unique_features: int = 10) -> dict:
    return {
        "version": version,
        "coordinate": "com.example:library",
        "unique_literal_context_score": score,
        "matched_unique_literal_context_features": matches,
        "reference_unique_literal_context_features": unique_features,
    }


def test_rank_uses_only_version_unique_literal_context_features() -> None:
    apk_features = FeatureSet(
        packages=set(),
        classes=set(),
        methods=set(),
        literal_context_features={"ctx:common", "ctx:v2-only"},
    )
    ranked = rank_version_unique_literal_context_candidates(
        apk_features,
        [
            reference("1.0.0", {"ctx:common", "ctx:v1-only"}, 1),
            reference("1.1.0", {"ctx:common", "ctx:v2-only", "ctx:v2-missing"}, 2),
        ],
    )

    assert ranked[0]["version"] == "1.1.0"
    assert ranked[0]["matched_unique_literal_context_features"] == 1
    assert ranked[0]["reference_unique_literal_context_features"] == 2
    assert ranked[0]["unique_literal_context_score"] == 0.5
    assert ranked[1]["unique_literal_context_score"] == 0.0


def test_classifier_blocks_source_validated_regression() -> None:
    decision = classify_version_unique_literal_context_row(
        selected_version="1.0.0",
        source_versions=["1.0.0"],
        reference_count=2,
        candidates=[
            candidate("1.1.0", 0.60, 3),
            candidate("1.0.0", 0.40, 2),
        ],
    )

    assert decision.classification == "regression-risk-do-not-promote"
    assert decision.suggested_version == "1.1.0"


def test_classifier_marks_source_validated_target_improvement() -> None:
    decision = classify_version_unique_literal_context_row(
        selected_version="1.0.0",
        source_versions=["1.1.0"],
        reference_count=2,
        candidates=[
            candidate("1.1.0", 0.60, 3),
            candidate("1.0.0", 0.40, 2),
        ],
    )

    assert decision.classification == "potential-target-improvement-needs-control-matrix"
    assert decision.suggested_version == "1.1.0"


def test_classifier_rejects_zero_match_exact_claim() -> None:
    decision = classify_version_unique_literal_context_row(
        selected_version="1.0.0",
        source_versions=["1.1.0"],
        reference_count=2,
        candidates=[
            candidate("1.1.0", 0.60, 0),
            candidate("1.0.0", 0.40, 0),
        ],
    )

    assert decision.classification == "no-version-unique-literal-context-match"


def test_cli_writes_opt_in_version_unique_literal_context_diagnostics(tmp_path, capsys) -> None:
    phase4_json = tmp_path / "phase4.json"
    output_json = tmp_path / "version-unique-context.json"
    output_doc = tmp_path / "version-unique-context.md"
    phase4_json.write_text(
        json.dumps({"controlled_cases": [], "real_component_rows": []}),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "version-unique-literal-context-experiment",
            "--phase4-json",
            str(phase4_json),
            "--reference-db",
            str(tmp_path / "missing.sqlite"),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["verdict"] == "version-unique-literal-context-no-safe-promotion"
    assert payload["summary"]["rows_inspected"] == 0
    assert output_doc.exists()
    console = json.loads(capsys.readouterr().out)
    assert console["json"].endswith("version-unique-context.json")


def test_default_matcher_and_report_do_not_import_version_unique_context_diagnostics() -> None:
    matcher_text = (ROOT / "src/apk_sbom/matcher.py").read_text(encoding="utf-8")
    report_text = (ROOT / "src/apk_sbom/report.py").read_text(encoding="utf-8")

    assert "version_unique_literal_context_diagnostics" not in matcher_text
    assert "from apk_sbom.version_unique_literal_context_diagnostics" not in report_text
