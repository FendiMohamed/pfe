from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.cli import main
from apk_sbom.no_maven_fork_family_experiment import build_payload


ROOT = Path(__file__).resolve().parents[1]


def candidate(
    coordinate: str,
    version: str,
    score: float,
    *,
    package_score: float = 1.0,
    opcode_score: float = 0.91,
    literal_score: float = 0.65,
) -> dict:
    return {
        "coordinate": coordinate,
        "version": version,
        "score": score,
        "evidence": {
            "package_score": package_score,
            "class_score": 0.01,
            "method_score": 0.02,
            "opcode_score": opcode_score,
            "literal_score": literal_score,
            "api_reference_score": 0.30,
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
                        candidate("androidx.recyclerview:recyclerview", "1.2.1", 0.28),
                        candidate("androidx.viewpager2:viewpager2", "1.0.0", 0.24),
                        candidate(
                            "com.google.code.gson:gson",
                            "2.8.9",
                            0.26,
                            package_score=0.33,
                            opcode_score=0.95,
                            literal_score=0.94,
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
                "+--- me.grishka.litex:recyclerview:1.2.1.1",
                "+--- me.grishka.litex:viewpager2:1.0.0",
                "+--- me.grishka.litex:swiperefreshlayout:1.2.0-beta01",
                "\\--- com.google.code.gson:gson:2.8.9",
            ]
        ),
        encoding="utf-8",
    )
    payload = {
        "schema_version": 1,
        "cases": [
            {
                "apk": "Mastodon 2.12.3",
                "classification": "forked-library-boundary",
                "dependency_tree": str(tree),
                "report": str(report),
                "source_candidate_overlap_coordinates": [
                    "com.google.code.gson:gson",
                ],
            },
            {
                "apk": "Privacy Browser 3.20.1",
                "classification": "identity-coverage-miss",
                "dependency_tree": str(tree),
                "report": str(report),
            },
        ],
    }
    input_json = tmp_path / "no-maven.json"
    input_json.write_text(json.dumps(payload), encoding="utf-8")
    return input_json


def test_mastodon_fork_family_audit_surfaces_fork_and_direct_candidates(
    tmp_path: Path,
) -> None:
    payload = build_payload(write_case_files(tmp_path))

    assert payload["verdict"] == "mastodon-fork-family-report-only-promising-not-promoted"
    assert payload["summary"]["litex_report_only_suggestions"] == 2
    assert payload["summary"]["litex_rows_kept_suppressed"] == 1
    assert payload["summary"]["direct_report_only_suggestions"] == 1
    assert payload["summary"]["default_selection_changes"] == 0
    assert payload["summary"]["sbom_component_changes"] == 0
    assert payload["summary"]["source_validation_metric_changes"] == 0


def test_cli_writes_mastodon_fork_family_audit(tmp_path: Path, capsys) -> None:
    output_json = tmp_path / "fork-family.json"
    output_doc = tmp_path / "fork-family.md"

    exit_code = main(
        [
            "no-maven-fork-family-experiment",
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
    assert payload["summary"]["litex_report_only_suggestions"] == 2
    assert payload["summary"]["direct_report_only_suggestions"] == 1
    assert output_doc.exists()
    console = json.loads(capsys.readouterr().out)
    assert console["json"].endswith("fork-family.json")


def test_default_matcher_and_report_do_not_import_no_maven_fork_family_experiment() -> None:
    matcher_text = (ROOT / "src/apk_sbom/matcher.py").read_text(encoding="utf-8")
    report_text = (ROOT / "src/apk_sbom/report.py").read_text(encoding="utf-8")

    assert "no_maven_fork_family_experiment" not in matcher_text
    assert "no_maven_fork_family_experiment" not in report_text
