from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.cli import main
from apk_sbom.lifecycle_family_diagnostics import build_payload
from apk_sbom.lifecycle_family_experiment import classify_lifecycle_public_overlap


ROOT = Path(__file__).resolve().parents[1]


def decision(coordinate: str, version: str, score: float, alternatives: list[dict] | None = None) -> dict:
    return {
        "coordinate": coordinate,
        "selected_version": version,
        "score": score,
        "alternatives": alternatives or [],
    }


def test_source_version_backed_target_variant_downgrades_public_claim() -> None:
    result = classify_lifecycle_public_overlap(
        coordinate="androidx.lifecycle:lifecycle-runtime",
        selected_version="2.6.2",
        source_versions=["2.9.0"],
        sibling_decisions=[
            decision("androidx.lifecycle:lifecycle-runtime-android", "2.9.0", 0.41),
        ],
    )

    assert result.classification == "source-version-backed-target-family-evidence"
    assert result.downgrade_public_claim is True


def test_family_anchors_downgrade_public_claim_without_forcing_replacement() -> None:
    result = classify_lifecycle_public_overlap(
        coordinate="androidx.lifecycle:lifecycle-runtime",
        selected_version="2.6.2",
        source_versions=["2.8.7"],
        sibling_decisions=[
            decision("androidx.lifecycle:lifecycle-runtime-android", "2.8.7", 0.68),
            decision("androidx.lifecycle:lifecycle-viewmodel-android", "2.8.7", 0.81),
            decision("androidx.lifecycle:lifecycle-livedata", "2.8.7", 0.58),
        ],
    )

    assert result.classification == "source-version-backed-target-family-evidence"
    assert result.downgrade_public_claim is True


def test_patch_near_tie_stays_ambiguous() -> None:
    result = classify_lifecycle_public_overlap(
        coordinate="androidx.lifecycle:lifecycle-runtime",
        selected_version="2.6.2",
        source_versions=["2.9.4"],
        sibling_decisions=[
            decision(
                "androidx.lifecycle:lifecycle-runtime-android",
                "2.9.0",
                0.400626,
                alternatives=[{"version": "2.9.4", "score": 0.400602}],
            ),
        ],
    )

    assert result.classification == "target-patch-near-tie-keep-ambiguous"
    assert result.downgrade_public_claim is False


def test_saved_fixture_lifecycle_diagnostic_preserves_target_rows() -> None:
    payload = build_payload(
        ROOT / "data" / "results" / "experiments" / "low-risk-version-band-diagnostics.json"
    )

    assert payload["summary"]["introduced_lifecycle_rows"] == 5
    assert payload["summary"]["public_claim_downgrade_candidates"] == 2
    assert payload["summary"]["resolved_target_rows_blocked"] == 0
    assert payload["verdict"] == "lifecycle-family-separation-promising-not-promoted"


def test_cli_writes_opt_in_lifecycle_family_experiment(tmp_path, capsys) -> None:
    output_json = tmp_path / "lifecycle.json"
    output_doc = tmp_path / "lifecycle.md"

    exit_code = main(
        [
            "lifecycle-family-experiment",
            "--input-json",
            str(ROOT / "data" / "results" / "experiments" / "low-risk-version-band-diagnostics.json"),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["verdict"] == "lifecycle-family-separation-promising-not-promoted"
    assert payload["summary"]["resolved_target_rows_blocked"] == 0
    console = json.loads(capsys.readouterr().out)
    assert console["json"].endswith("lifecycle.json")


def test_default_matcher_and_report_do_not_import_lifecycle_family_experiment() -> None:
    matcher_text = (ROOT / "src/apk_sbom/matcher.py").read_text(encoding="utf-8")
    report_text = (ROOT / "src/apk_sbom/report.py").read_text(encoding="utf-8")

    assert "lifecycle_family_experiment" not in matcher_text
    assert "lifecycle_family_diagnostics" not in matcher_text
    assert "from apk_sbom.lifecycle_family_experiment" not in report_text
    assert "from apk_sbom.lifecycle_family_diagnostics" not in report_text
