from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.coarse_to_fine_pruning_diagnostics import build_payload


def test_pruning_diagnostics_measure_controlled_and_real_pressure(tmp_path) -> None:
    controlled_report = tmp_path / "controlled-report.json"
    real_report = tmp_path / "real-report.json"
    write_report(
        controlled_report,
        [
            decision("example:single", width=1, gap=0.8),
            decision("example:wide", width=4, gap=0.01),
        ],
    )
    write_report(
        real_report,
        [decision("example:near-tie", width=3, gap=0.005)],
    )
    generated_batch = tmp_path / "generated.json"
    write_json(
        generated_batch,
        {
            "fixtures": [
                {
                    "name": "controlled",
                    "category": "clear",
                    "coordinate": "example:wide",
                    "version": "1.0.0",
                    "report_path": str(controlled_report),
                }
            ]
        },
    )
    phase4 = tmp_path / "phase4.json"
    write_json(
        phase4,
        {
            "real_component_rows": [
                {
                    "case_id": "real",
                    "case_name": "Real APK",
                    "role": "source-validated-partial",
                    "coordinate": "example:near-tie",
                    "source_versions": ["2.0.0"],
                    "report_path": str(real_report),
                },
                {
                    "case_id": "real",
                    "case_name": "Real APK",
                    "role": "source-validated-partial",
                    "coordinate": "example:other",
                    "source_versions": ["3.0.0"],
                    "report_path": str(real_report),
                },
            ]
        },
    )

    payload = build_payload(
        generated_batch_json=generated_batch,
        phase4_json=phase4,
    )

    assert payload["verdict"] == "coarse-to-fine-pruning-diagnostic-family-first-next"
    assert payload["summary"]["reports_loaded"] == 2
    assert payload["summary"]["decision_rows"] == 3
    assert payload["summary"]["candidate_version_slots"] == 8
    assert payload["summary"]["wide_version_family_rows"] == 2
    assert payload["summary"]["close_band_rows"] == 2
    assert payload["summary"]["near_tie_rows"] == 1
    by_coordinate = {row["coordinate"]: row for row in payload["rows"]}
    assert by_coordinate["example:near-tie"]["selected_matches_source"] is True
    assert by_coordinate["example:near-tie"]["family_identity_proxy_score"] == 0.0
    assert by_coordinate["example:near-tie"]["dependency_score"] == 0.0


def test_pruning_diagnostics_preserve_missing_report_evidence(tmp_path) -> None:
    generated_batch = tmp_path / "generated.json"
    write_json(
        generated_batch,
        {
            "fixtures": [
                {
                    "name": "missing",
                    "category": "clear",
                    "coordinate": "example:missing",
                    "version": "1.0.0",
                    "report_path": str(tmp_path / "missing-report.json"),
                }
            ]
        },
    )
    phase4 = tmp_path / "phase4.json"
    write_json(phase4, {"real_component_rows": []})

    payload = build_payload(
        generated_batch_json=generated_batch,
        phase4_json=phase4,
    )

    assert payload["verdict"] == "coarse-to-fine-pruning-diagnostic-incomplete"
    assert payload["summary"]["missing_reports"] == 1
    assert payload["missing_reports"][0]["case_id"] == "missing"


def decision(coordinate: str, *, width: int, gap: float) -> dict:
    return {
        "coordinate": coordinate,
        "selected_version": "2.0.0",
        "reference_versions_considered": width,
        "gap_to_next": gap,
        "version_status": "candidate",
        "identity_status": "confirmed",
        "alternatives": [],
    }


def write_report(path: Path, decisions: list[dict]) -> None:
    write_json(path, {"match_summary": {"decisions": decisions}})


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
