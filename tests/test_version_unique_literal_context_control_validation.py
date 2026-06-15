from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.version_unique_literal_context_control_validation import build_payload


def test_current_control_validation_accepts_expected_target_change(tmp_path) -> None:
    roots = make_roots(tmp_path)
    write_case(
        roots,
        app_id="vlc-android",
        report_dir="report-real-vlc-android",
        baseline_counts=(6, 20, 0),
        opt_in_counts=(7, 19, 0),
        baseline_rows=[
            row("androidx.recyclerview:recyclerview", "1.2.1", "version-mismatch"),
        ],
        opt_in_rows=[
            row("androidx.recyclerview:recyclerview", "1.3.2", "confirmed"),
        ],
    )
    write_unchanged_case(
        roots,
        app_id="antennapod",
        report_dir="report-real-antennapod",
        counts=(19, 1, 0),
        coordinate="androidx.core:core",
        version="1.15.0",
        status="version-mismatch",
    )
    write_unchanged_case(
        roots,
        app_id="osmand",
        report_dir="report-real-osmand",
        counts=(16, 9, 0),
        coordinate="androidx.gridlayout:gridlayout",
        version="1.0.0",
        status="confirmed",
    )

    payload = build_payload(**roots)

    assert payload["verdict"] == "version-unique-literal-context-current-control-opt-in-pass"
    assert payload["summary"]["confirmed_delta"] == 1
    assert payload["summary"]["version_mismatch_delta"] == -1
    assert payload["summary"]["failed_gates"] == 0
    assert payload["changed_rows"] == [
        {
            "app_id": "vlc-android",
            "kind": "sbom-component",
            "coordinate": "androidx.recyclerview:recyclerview",
            "baseline_version": "1.2.1",
            "opt_in_version": "1.3.2",
            "baseline_status": "version-mismatch",
            "opt_in_status": "confirmed",
            "source_versions": ["1.3.2"],
        }
    ]


def test_current_control_validation_rejects_control_change(tmp_path) -> None:
    roots = make_roots(tmp_path)
    write_case(
        roots,
        app_id="vlc-android",
        report_dir="report-real-vlc-android",
        baseline_counts=(6, 20, 0),
        opt_in_counts=(7, 19, 0),
        baseline_rows=[
            row("androidx.recyclerview:recyclerview", "1.2.1", "version-mismatch"),
        ],
        opt_in_rows=[
            row("androidx.recyclerview:recyclerview", "1.3.2", "confirmed"),
        ],
    )
    write_case(
        roots,
        app_id="antennapod",
        report_dir="report-real-antennapod",
        baseline_counts=(19, 1, 0),
        opt_in_counts=(18, 2, 0),
        baseline_rows=[row("androidx.core:core", "1.15.0", "version-mismatch")],
        opt_in_rows=[row("androidx.core:core", "1.16.0", "version-mismatch")],
    )
    write_unchanged_case(
        roots,
        app_id="osmand",
        report_dir="report-real-osmand",
        counts=(16, 9, 0),
        coordinate="androidx.gridlayout:gridlayout",
        version="1.0.0",
        status="confirmed",
    )

    payload = build_payload(**roots)

    assert payload["verdict"] == "version-unique-literal-context-current-control-failed"
    failed = {gate["gate"] for gate in payload["gates"] if gate["status"] == "fail"}
    assert "controls-unchanged" in failed
    assert "only-expected-row-changed" in failed
    assert "no-source-validation-count-regressions" in failed


def make_roots(tmp_path: Path) -> dict:
    return {
        "baseline_validation_root": tmp_path / "baseline/source-validation",
        "opt_in_validation_root": tmp_path / "opt-in/source-validation",
        "baseline_report_root": tmp_path / "baseline",
        "opt_in_report_root": tmp_path / "opt-in",
    }


def write_unchanged_case(
    roots: dict,
    *,
    app_id: str,
    report_dir: str,
    counts: tuple[int, int, int],
    coordinate: str,
    version: str,
    status: str,
) -> None:
    write_case(
        roots,
        app_id=app_id,
        report_dir=report_dir,
        baseline_counts=counts,
        opt_in_counts=counts,
        baseline_rows=[row(coordinate, version, status)],
        opt_in_rows=[row(coordinate, version, status)],
    )


def write_case(
    roots: dict,
    *,
    app_id: str,
    report_dir: str,
    baseline_counts: tuple[int, int, int],
    opt_in_counts: tuple[int, int, int],
    baseline_rows: list[dict],
    opt_in_rows: list[dict],
) -> None:
    write_json(
        roots["baseline_validation_root"] / app_id / "source-validation.json",
        validation_payload(*baseline_counts, results=baseline_rows),
    )
    write_json(
        roots["opt_in_validation_root"] / app_id / "source-validation.json",
        validation_payload(*opt_in_counts, results=opt_in_rows),
    )
    write_json(
        roots["baseline_report_root"] / report_dir / "report.json",
        report_payload(enabled=False),
    )
    write_json(
        roots["opt_in_report_root"] / report_dir / "report.json",
        report_payload(enabled=True),
    )


def validation_payload(
    confirmed: int,
    mismatches: int,
    missing: int,
    *,
    results: list[dict],
) -> dict:
    return {
        "confirmed": confirmed,
        "version_mismatches": mismatches,
        "missing": missing,
        "sbom_components": confirmed + mismatches + missing,
        "source_components": confirmed + mismatches + missing,
        "results": results,
    }


def row(coordinate: str, version: str, status: str) -> dict:
    return {
        "kind": "sbom-component",
        "coordinate": coordinate,
        "version": version,
        "status": status,
        "source_versions": ["1.3.2"]
        if coordinate == "androidx.recyclerview:recyclerview"
        else [version],
    }


def report_payload(*, enabled: bool) -> dict:
    return {
        "match_summary": {
            "version_unique_literal_context_reranker_enabled": enabled,
        }
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
