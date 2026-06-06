from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.family_identity_prefilter_simulation import build_payload


def test_prefilter_proxy_finds_tracked_clean_reducing_margin(tmp_path) -> None:
    diagnostic = tmp_path / "diagnostic.json"
    write_json(
        diagnostic,
        {
            "rows": [
                row("controlled", "expected:library", score=0.9, slots=3, source=["1.0.0"]),
                row("controlled", "noise:library", score=0.1, slots=4),
                row("real", "real:library", score=0.8, slots=2, source=["2.0.0"]),
                row("real", "other:library", score=0.4, slots=5),
            ]
        },
    )

    payload = build_payload(diagnostic_json=diagnostic, margins=(0.0, 0.5, 1.0))

    assert (
        payload["verdict"]
        == "family-identity-prefilter-proxy-candidate-needs-live-offline-validation"
    )
    recommended = payload["recommended_configuration"]
    assert recommended["margin"] == 0.0
    assert recommended["candidate_version_slots_removed"] == 9
    assert recommended["tracked_source_family_losses"] == 0


def test_prefilter_proxy_rejects_reducing_margins_with_source_losses(tmp_path) -> None:
    diagnostic = tmp_path / "diagnostic.json"
    write_json(
        diagnostic,
        {
            "rows": [
                row("controlled", "noise:library", score=0.9, slots=4),
                row("controlled", "expected:library", score=0.1, slots=3, source=["1.0.0"]),
                row("real", "real:library", score=0.8, slots=2, source=["2.0.0"]),
            ]
        },
    )

    payload = build_payload(diagnostic_json=diagnostic, margins=(0.0, 1.0))

    assert payload["verdict"] == "family-identity-prefilter-proxy-no-safe-reduction"
    assert payload["recommended_configuration"] is None
    assert payload["configurations"][0]["tracked_source_family_losses"] == 1


def row(
    report: str,
    coordinate: str,
    *,
    score: float,
    slots: int,
    source: list[str] | None = None,
) -> dict:
    return {
        "report_path": f"{report}.json",
        "dataset_layer": "controlled-generated" if report == "controlled" else "real-apk",
        "case_id": report,
        "coordinate": coordinate,
        "family_identity_proxy_score": score,
        "reference_versions_considered": slots,
        "source_versions": source or [],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
