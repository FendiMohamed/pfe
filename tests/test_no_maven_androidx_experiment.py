from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.cli import main
from apk_sbom.no_maven_androidx_experiment import build_payload


ROOT = Path(__file__).resolve().parents[1]


def candidate(
    coordinate: str,
    version: str,
    score: float,
    *,
    package_score: float = 1.0,
    opcode_score: float = 0.8,
) -> dict:
    return {
        "coordinate": coordinate,
        "version": version,
        "score": score,
        "evidence": {
            "package_score": package_score,
            "class_score": 0.05,
            "method_score": 0.20,
            "opcode_score": opcode_score,
            "literal_score": 0.5,
            "api_reference_score": 0.25,
        },
    }


def write_case_files(tmp_path: Path) -> Path:
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps(
            {
                "detected_components": [],
                "match_summary": {
                    "candidates": [
                        candidate("androidx.startup:startup-runtime", "1.1.1", 0.35),
                        candidate(
                            "androidx.lifecycle:lifecycle-runtime",
                            "2.6.2",
                            0.26,
                        ),
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    tree = tmp_path / "deps.txt"
    tree.write_text(
        "\n".join(
            [
                "+--- androidx.startup:startup-runtime:1.1.1",
                "\\--- androidx.lifecycle:lifecycle-runtime:2.6.2",
            ]
        ),
        encoding="utf-8",
    )
    payload = {
        "schema_version": 1,
        "cases": [
            {
                "apk": "Tiny AndroidX 1.0",
                "classification": "identity-coverage-miss",
                "dependency_tree": str(tree),
                "report": str(report),
                "source_candidate_overlap_coordinates": [
                    "androidx.startup:startup-runtime",
                    "androidx.lifecycle:lifecycle-runtime",
                ],
            },
            {
                "apk": "Forked Mastodon 1.0",
                "classification": "forked-library-boundary",
                "dependency_tree": str(tree),
                "recommended_lane": "fork audit",
                "report": str(report),
                "source_candidate_overlap_coordinates": ["com.google.code.gson:gson"],
            },
        ],
    }
    input_json = tmp_path / "no-maven.json"
    input_json.write_text(json.dumps(payload), encoding="utf-8")
    return input_json


def test_no_maven_androidx_experiment_surfaces_source_backed_candidate(tmp_path: Path) -> None:
    payload = build_payload(write_case_files(tmp_path))

    assert payload["verdict"] == "no-maven-androidx-report-only-promising-not-promoted"
    assert payload["summary"]["report_only_suggestions"] == 1
    assert payload["summary"]["kept_suppressed_rows"] == 1
    assert payload["summary"]["blocked_non_androidx_cases"] == 1
    assert payload["summary"]["default_selection_changes"] == 0
    assert payload["summary"]["sbom_component_changes"] == 0
    assert payload["summary"]["source_validation_metric_changes"] == 0
    suggested = [
        row
        for row in payload["candidate_rows"]
        if row["policy_action"] == "surface-report-only-source-backed-candidate"
    ]
    assert suggested[0]["coordinate"] == "androidx.startup:startup-runtime"


def test_cli_writes_no_maven_androidx_experiment(tmp_path: Path, capsys) -> None:
    output_json = tmp_path / "experiment.json"
    output_doc = tmp_path / "experiment.md"

    exit_code = main(
        [
            "no-maven-androidx-experiment",
            "--input-json",
            str(write_case_files(tmp_path)),
            "--output-json",
            str(output_json),
            "--output-doc",
            str(output_doc),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["summary"]["report_only_suggestions"] == 1
    assert output_doc.exists()
    console = json.loads(capsys.readouterr().out)
    assert console["json"].endswith("experiment.json")


def test_default_matcher_and_report_do_not_import_no_maven_androidx_experiment() -> None:
    matcher_text = (ROOT / "src/apk_sbom/matcher.py").read_text(encoding="utf-8")
    report_text = (ROOT / "src/apk_sbom/report.py").read_text(encoding="utf-8")

    assert "no_maven_androidx_experiment" not in matcher_text
    assert "no_maven_androidx_experiment" not in report_text
