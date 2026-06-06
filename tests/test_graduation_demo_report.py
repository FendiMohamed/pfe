from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "run_graduation_demo_report.py"
)
SPEC = importlib.util.spec_from_file_location("run_graduation_demo_report", SCRIPT_PATH)
assert SPEC is not None
demo_report = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(demo_report)


def test_classifies_apk_only_sbom_evidence() -> None:
    payload = _payload(
        components=[
            {
                "group": "com.squareup.okio",
                "artifact": "okio",
                "version": "2.8.0",
                "version_status": "exact",
                "version_confidence_label": "high",
            }
        ]
    )

    result = demo_report.classify_report(
        payload,
        query_osv=False,
        source_validation_present=False,
    )

    assert result["classification"] == "apk-only-sbom-evidence"
    assert result["counts"]["maven_components"] == 1
    assert result["component_status_counts"]["exact"] == 1


def test_source_validation_claim_is_only_added_when_artifact_is_present() -> None:
    payload = _payload(
        components=[
            {
                "group": "androidx.core",
                "artifact": "core",
                "version": "1.12.0",
                "version_status": "likely",
                "version_confidence_label": "medium",
            }
        ]
    )

    result = demo_report.classify_report(
        payload,
        query_osv=False,
        source_validation_present=True,
    )

    assert result["classification"] == "source-validation-aware-report"


def test_framework_hint_becomes_boundary_when_maven_signal_is_thin() -> None:
    payload = _payload(
        native_libraries=[
            {"filename": "libflutter.so", "path": "lib/arm64-v8a/libflutter.so"}
        ]
    )

    result = demo_report.classify_report(
        payload,
        query_osv=False,
        source_validation_present=False,
    )

    assert result["classification"] == "framework-boundary"
    assert result["framework_hints"] == ["Flutter"]


def test_high_obfuscation_risk_takes_priority() -> None:
    payload = _payload(
        components=[
            {
                "group": "com.example",
                "artifact": "demo",
                "version": "1.0.0",
                "version_status": "candidate",
                "version_confidence_label": "low",
            }
        ],
        obfuscation_level="high",
    )

    result = demo_report.classify_report(
        payload,
        query_osv=False,
        source_validation_present=False,
    )

    assert result["classification"] == "obfuscation-risk-boundary"
    assert result["counts"]["uncertain_or_candidate_components"] == 1


def test_medium_obfuscation_with_only_uncertain_components_is_boundary() -> None:
    payload = _payload(
        components=[
            {
                "group": "androidx.core",
                "artifact": "core",
                "version": "1.0.0",
                "version_status": "uncertain",
                "version_confidence_label": "low",
            }
        ],
        obfuscation_level="medium",
    )

    result = demo_report.classify_report(
        payload,
        query_osv=False,
        source_validation_present=False,
    )

    assert result["classification"] == "obfuscation-risk-boundary"


def test_failure_summary_is_presentable() -> None:
    summary = demo_report.build_failure_summary(
        apk_path="demo.apk",
        output_dir="data/results/graduation-demo/demo",
        db_path="data/reference_db/reference_features.sqlite",
        query_osv=False,
        source_validation_json=None,
        error=FileNotFoundError("APK not found"),
    )

    markdown = demo_report.render_readiness_markdown(summary)

    assert summary["classification"] == "failed-before-report"
    assert "APK not found" in markdown
    assert "No SBOM or match report should be claimed" in markdown


def test_source_validation_counts_are_rendered(tmp_path: Path) -> None:
    validation_json = tmp_path / "source-validation.json"
    validation_json.write_text(
        json.dumps(
            {
                "sbom_components": 7,
                "confirmed": 5,
                "version_mismatches": 2,
                "missing": 0,
            }
        ),
        encoding="utf-8",
    )
    payload = _payload(
        components=[
            {
                "group": "androidx.core",
                "artifact": "core",
                "version": "1.12.0",
                "version_status": "likely",
                "version_confidence_label": "medium",
            }
        ]
    )

    summary = demo_report.build_demo_readiness(
        payload,
        apk_path="demo.apk",
        output_dir="data/results/graduation-demo/demo",
        db_path="data/reference_db/reference_features.sqlite",
        artifacts={},
        query_osv=False,
        source_validation_json=str(validation_json),
    )
    markdown = demo_report.render_readiness_markdown(summary)

    assert summary["classification"] == "source-validation-aware-report"
    assert summary["source_validation"]["confirmed"] == 5
    assert "5/7 confirmed, 2 mismatches, 0 missing" in markdown


def test_failure_exit_is_demo_safe_by_default(
    tmp_path: Path, monkeypatch
) -> None:
    def raise_report_error(*args, **kwargs):
        raise RuntimeError("bad apk")

    monkeypatch.setattr(demo_report, "generate_final_report", raise_report_error)

    output_dir = tmp_path / "demo"
    exit_code = demo_report.main(["missing.apk", "--output-dir", str(output_dir)])

    readiness = json.loads((output_dir / "demo-readiness.json").read_text())
    assert exit_code == 0
    assert readiness["classification"] == "failed-before-report"
    assert readiness["demo_outcome"] == "presentable-failure-summary"


def test_strict_exit_preserves_failure_code(
    tmp_path: Path, monkeypatch
) -> None:
    def raise_report_error(*args, **kwargs):
        raise RuntimeError("bad apk")

    monkeypatch.setattr(demo_report, "generate_final_report", raise_report_error)

    output_dir = tmp_path / "demo"
    exit_code = demo_report.main(
        ["missing.apk", "--output-dir", str(output_dir), "--strict-exit"]
    )

    assert exit_code == 1
    assert (output_dir / "demo-readiness.md").exists()


def _payload(
    *,
    components: list[dict] | None = None,
    native_libraries: list[dict] | None = None,
    obfuscation_level: str = "low",
) -> dict:
    return {
        "apk": {
            "dex_files": ["classes.dex"],
            "native_libraries": native_libraries or [],
            "manifest_metadata": {
                "package_name": "org.example.demo",
                "version_name": "1.0",
                "version_code": "1",
            },
            "forensic_summary": {
                "extraction_risk": "low",
            },
        },
        "match_summary": {
            "dex_files_analyzed": 1,
            "dex_files_failed": 0,
        },
        "obfuscation_risk": {
            "level": obfuscation_level,
            "score": 0.0,
        },
        "detected_components": components or [],
        "osv": None,
    }
