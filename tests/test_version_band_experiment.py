from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.cli import main
from apk_sbom.version_band_experiment import should_downgrade_old_version_steal
from apk_sbom.version_band_trigger_diagnostics import build_payload


ROOT = Path(__file__).resolve().parents[1]


def sibling(coordinate: str, version: str, score: float) -> dict:
    return {"coordinate": coordinate, "selected_version": version, "score": score}


def test_old_appcompat_steal_is_flagged_by_two_newer_apk_anchors() -> None:
    decision = should_downgrade_old_version_steal(
        coordinate="androidx.appcompat:appcompat",
        selected_version="1.2.0",
        sibling_decisions=[
            sibling("androidx.fragment:fragment", "1.8.9", 0.78),
            sibling("androidx.recyclerview:recyclerview", "1.4.0", 0.79),
        ],
    )

    assert decision.apply is True
    assert decision.reason_codes == (
        "scoped-old-version-steal-profile",
        "multiple-higher-band-apk-anchors",
        "diagnostic-downgrade-only",
    )


def test_coherent_legacy_appcompat_is_not_flagged() -> None:
    decision = should_downgrade_old_version_steal(
        coordinate="androidx.appcompat:appcompat",
        selected_version="1.2.0",
        sibling_decisions=[
            sibling("androidx.core:core", "1.3.0", 0.99),
            sibling("androidx.lifecycle:lifecycle-runtime", "2.1.0", 0.98),
            sibling("androidx.fragment:fragment", "1.3.6", 0.62),
        ],
    )

    assert decision.apply is False
    assert decision.blocked_by == ("insufficient-higher-band-apk-anchors",)


def test_lifecycle_stays_out_of_scoped_trigger() -> None:
    decision = should_downgrade_old_version_steal(
        coordinate="androidx.lifecycle:lifecycle-runtime",
        selected_version="2.6.2",
        sibling_decisions=[
            sibling("androidx.lifecycle:lifecycle-runtime-android", "2.9.0", 0.41),
            sibling("androidx.recyclerview:recyclerview", "1.4.0", 0.58),
        ],
    )

    assert decision.apply is False
    assert decision.blocked_by == ("coordinate-not-in-scoped-profile",)


def test_saved_fixture_diagnostic_preserves_resolved_targets() -> None:
    payload = build_payload(
        ROOT / "data" / "results" / "experiments" / "low-risk-version-band-diagnostics.json"
    )

    assert payload["summary"]["introduced_mismatches_flagged"] >= 1
    assert payload["summary"]["resolved_target_rows_blocked"] == 0
    assert payload["verdict"] == "scoped-downgrade-experiment-promising-not-promoted"


def test_cli_writes_opt_in_version_band_experiment(tmp_path, capsys) -> None:
    output_json = tmp_path / "version-band.json"
    output_doc = tmp_path / "version-band.md"

    exit_code = main(
        [
            "version-band-experiment",
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
    assert payload["verdict"] == "scoped-downgrade-experiment-promising-not-promoted"
    assert payload["summary"]["resolved_target_rows_blocked"] == 0
    console = json.loads(capsys.readouterr().out)
    assert console["json"].endswith("version-band.json")


def test_default_matcher_and_report_do_not_import_version_band_experiment() -> None:
    matcher_text = (ROOT / "src/apk_sbom/matcher.py").read_text(encoding="utf-8")
    report_text = (ROOT / "src/apk_sbom/report.py").read_text(encoding="utf-8")

    assert "version_band_experiment" not in matcher_text
    assert "version_band_trigger_diagnostics" not in matcher_text
    assert "from apk_sbom.version_band_experiment" not in report_text
    assert "from apk_sbom.version_band_trigger_diagnostics" not in report_text
