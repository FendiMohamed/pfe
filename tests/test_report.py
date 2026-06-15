from __future__ import annotations

import json

from apk_sbom.apk_extractor import ApkInspection, ManifestMetadata, NativeLibrary
from apk_sbom.matcher import (
    MatchSummary,
    OverlapEvidence,
    VersionAlternative,
    VersionDecision,
)
from apk_sbom.models import ComponentEvidence, DetectedLibrary
from apk_sbom.report import (
    ReportArtifacts,
    build_html_report,
    build_json_report,
    build_markdown_report,
    build_version_uncertainty_summary,
    generate_final_report,
)
from apk_sbom.vulnerability import OsvComponentResult, OsvScanSummary, OsvVulnerability


def make_apk() -> ApkInspection:
    return ApkInspection(
        apk_path="sample.apk",
        apk_size=123,
        apk_sha256="a" * 64,
        dex_files=["classes.dex"],
        has_multidex=False,
        manifest_present=True,
        resources_arsc_present=False,
        native_libraries=[],
        manifest_metadata=ManifestMetadata(
            package_name="com.example.app",
            version_code="42",
            version_name="1.2.3",
            min_sdk="23",
            target_sdk="35",
            permissions=["android.permission.INTERNET"],
            parse_status="parsed",
        ),
    )


def make_match_summary(decisions: list[VersionDecision] | None = None) -> MatchSummary:
    return MatchSummary(
        apk_path="sample.apk",
        db_path="reference.sqlite",
        dex_files_analyzed=1,
        dex_files_failed=0,
        apk_packages=1,
        apk_classes=2,
        apk_methods=3,
        apk_distinct_opcodes=4,
        apk_opcode_total=5,
        apk_distinct_opcode_ngrams=2,
        apk_opcode_ngram_total=3,
        apk_dependency_edges=0,
        apk_dependency_shape_bins=0,
        apk_string_literals=0,
        apk_api_references=0,
        package_weight=0.15,
        class_weight=0.45,
        method_weight=0.25,
        opcode_weight=0.15,
        dependency_weight=0.10,
        literal_weight=0.08,
        unique_version_weight=0.12,
        api_reference_weight=0.0,
        opcode_ngram_weight=0.0,
        min_score=0.05,
        candidates=[],
        decisions=decisions or [],
        inert_multiscale_features={
            "scoring_status": "disabled",
            "apk": {
                "call_chain_opcode_fingerprints": {"distinct": 1, "total": 1},
                "basic_block_opcode_fingerprints": {"distinct": 2, "total": 3},
                "class_neighbor_summaries": {"distinct": 1, "total": 2},
                "field_operation_sequences": {"distinct": 1, "total": 1},
                "literal_context_features": {"distinct": 1, "total": 1},
            },
            "reference": {
                "call_chain_opcode_fingerprints": {
                    "components_with_features": 1,
                    "distinct": 1,
                    "total": 1,
                },
                "basic_block_opcode_fingerprints": {
                    "components_with_features": 1,
                    "distinct": 2,
                    "total": 3,
                },
                "class_neighbor_summaries": {
                    "components_with_features": 1,
                    "distinct": 1,
                    "total": 2,
                },
                "field_operation_sequences": {
                    "components_with_features": 1,
                    "distinct": 1,
                    "total": 1,
                },
                "literal_context_features": {
                    "components_with_features": 1,
                    "distinct": 1,
                    "total": 1,
                },
            },
        },
    )


def make_overlap_evidence() -> OverlapEvidence:
    return OverlapEvidence(
        matched_packages=1,
        reference_packages=1,
        apk_packages=1,
        package_score=1.0,
        matched_classes=1,
        reference_classes=1,
        apk_classes=1,
        class_score=1.0,
        matched_methods=1,
        reference_methods=1,
        apk_methods=1,
        method_score=1.0,
        shared_opcodes=1,
        reference_distinct_opcodes=1,
        reference_opcode_total=1,
        apk_distinct_opcodes=1,
        apk_opcode_total=1,
        opcode_score=1.0,
        shared_opcode_ngrams=1,
        reference_distinct_opcode_ngrams=1,
        reference_opcode_ngram_total=1,
        apk_distinct_opcode_ngrams=1,
        apk_opcode_ngram_total=1,
        opcode_ngram_score=1.0,
        matched_dependency_edges=0,
        reference_dependency_edges=0,
        apk_dependency_edges=0,
        dependency_edge_score=0.0,
        reference_dependency_shape_bins=0,
        apk_dependency_shape_bins=0,
        dependency_shape_score=0.0,
        dependency_score=0.0,
        matched_string_literals=0,
        reference_string_literals=0,
        apk_string_literals=0,
        literal_score=0.0,
        matched_api_references=0,
        reference_api_references=0,
        apk_api_references=0,
        api_reference_score=0.0,
        matched_unique_classes=0,
        reference_unique_classes=0,
        unique_class_score=0.0,
        matched_unique_methods=0,
        reference_unique_methods=0,
        unique_method_score=0.0,
        matched_unique_literals=0,
        reference_unique_literals=0,
        unique_literal_score=0.0,
        unique_version_score=0.0,
    )


def make_artifacts() -> ReportArtifacts:
    return ReportArtifacts(
        output_dir="data/results/report",
        matches_json="data/results/report/matches.json",
        sbom_json="data/results/report/sbom.cdx.json",
        vulnerabilities_json="data/results/report/osv-vulnerabilities.json",
        report_json="data/results/report/report.json",
        report_markdown="data/results/report/report.md",
        report_html="data/results/report/report.html",
    )


def make_r8_phase5_experiment() -> dict:
    return {
        "report_only": True,
        "source": "data/results/experiments/r8-phase5-scoped-trigger-diagnostics.json",
        "verdict": "phase5-scoped-trigger-experiment-clean-not-promoted",
        "policy": ["report-only"],
        "summary": {
            "rows_evaluated": 286,
            "triggered_rows": 4,
            "target_improvements_kept": 4,
            "triggered_regressions": 0,
            "triggered_conflicts": 0,
            "matching_rows": 1,
            "matching_triggered_rows": 1,
        },
        "matching_rows": [],
        "matching_triggered_rows": [
            {
                "case": "sample",
                "coordinate": "androidx.viewpager2:viewpager2",
                "baseline_selected_version": "1.0.0",
                "diagnostic_selected_version": "1.1.0",
                "trigger_outcome": "trigger-target-improvement",
                "trigger_decision": {
                    "profile_id": "androidx-viewpager2-1.1.0-modern-or-security-low-confidence"
                },
            }
        ],
        "triggered_rows_sample": [],
    }


def make_r8_minified_confidence_policy() -> dict:
    return {
        "report_only": True,
        "source": "data/results/experiments/r8-minified-confidence-policy-diagnostics.json",
        "verdict": "r8-minified-confidence-policy-report-only-ready",
        "policy": ["report-only"],
        "summary": {
            "rows_classified": 286,
            "regression_rows_blocked": 36,
            "phase5_report_only_suggestions": 4,
            "report_default_selection_changes": 0,
            "matching_rows": 2,
            "matching_report_only_suggestions": 1,
            "matching_blocked_regression_risks": 1,
        },
        "matching_rows": [],
        "matching_report_only_suggestions": [
            {
                "case": "sample",
                "coordinate": "androidx.viewpager2:viewpager2",
                "baseline_selected_version": "1.0.0",
                "diagnostic_selected_version": "1.1.0",
                "confidence_label": "low-confidence-source-backed",
                "policy_action": "surface-report-only-suggestion",
                "signals": ["baseline-low-confidence", "phase5-report-only-trigger"],
            }
        ],
        "matching_blocked_regression_risks": [
            {
                "case": "sample",
                "coordinate": "androidx.viewpager2:viewpager2",
                "baseline_selected_version": "1.0.0",
                "diagnostic_selected_version": "1.2.0",
                "policy_action": "do-not-change-selected-version",
                "signals": ["source-rejects-diagnostic", "near-zero-score-margin"],
            }
        ],
    }


def test_generate_final_report_passes_api_reference_weight(tmp_path, monkeypatch):
    seen: dict[str, float | bool] = {}

    def fake_match_apk_to_reference_db(*args, **kwargs):
        seen["api_reference_weight"] = kwargs["api_reference_weight"]
        seen["opcode_ngram_weight"] = kwargs["opcode_ngram_weight"]
        seen["enable_version_unique_literal_context_reranker"] = kwargs[
            "enable_version_unique_literal_context_reranker"
        ]
        seen["enable_composite_family_shortlist"] = kwargs[
            "enable_composite_family_shortlist"
        ]
        seen["composite_family_shortlist_margin"] = kwargs[
            "composite_family_shortlist_margin"
        ]
        return make_match_summary()

    monkeypatch.setattr("apk_sbom.report.inspect_apk", lambda apk_path: make_apk())
    monkeypatch.setattr(
        "apk_sbom.report.match_apk_to_reference_db",
        fake_match_apk_to_reference_db,
    )

    generate_final_report(
        "sample.apk",
        output_dir=tmp_path,
        query_osv=False,
        api_reference_weight=0.05,
        opcode_ngram_weight=0.07,
        enable_version_unique_literal_context_reranker=True,
        enable_composite_family_shortlist=True,
        composite_family_shortlist_margin=0.2,
    )

    assert seen["api_reference_weight"] == 0.05
    assert seen["opcode_ngram_weight"] == 0.07
    assert seen["enable_version_unique_literal_context_reranker"] is True
    assert seen["enable_composite_family_shortlist"] is True
    assert seen["composite_family_shortlist_margin"] == 0.2


def test_generate_final_report_enables_version_unique_literal_context_by_default(
    tmp_path,
    monkeypatch,
):
    seen: dict[str, bool] = {}

    def fake_match_apk_to_reference_db(*args, **kwargs):
        seen["enable_version_unique_literal_context_reranker"] = kwargs[
            "enable_version_unique_literal_context_reranker"
        ]
        return make_match_summary()

    monkeypatch.setattr("apk_sbom.report.inspect_apk", lambda apk_path: make_apk())
    monkeypatch.setattr(
        "apk_sbom.report.match_apk_to_reference_db",
        fake_match_apk_to_reference_db,
    )

    generate_final_report("sample.apk", output_dir=tmp_path, query_osv=False)

    assert seen["enable_version_unique_literal_context_reranker"] is True


def test_generate_final_report_enables_composite_family_shortlist_by_default(
    tmp_path,
    monkeypatch,
):
    seen: dict[str, bool] = {}

    def fake_match_apk_to_reference_db(*args, **kwargs):
        seen["enable_composite_family_shortlist"] = kwargs[
            "enable_composite_family_shortlist"
        ]
        return make_match_summary()

    monkeypatch.setattr("apk_sbom.report.inspect_apk", lambda apk_path: make_apk())
    monkeypatch.setattr(
        "apk_sbom.report.match_apk_to_reference_db",
        fake_match_apk_to_reference_db,
    )

    generate_final_report("sample.apk", output_dir=tmp_path, query_osv=False)

    assert seen["enable_composite_family_shortlist"] is True


def test_generate_final_report_attaches_r8_phase5_evidence_only_when_requested(
    tmp_path,
    monkeypatch,
):
    component = DetectedLibrary(
        group="androidx.viewpager2",
        artifact="viewpager2",
        version="1.0.0",
        confidence=0.42,
        match_type="hybrid-candidate",
        evidence=[],
    )
    experiment_path = tmp_path / "phase5.json"
    experiment_path.write_text(
        json.dumps(
            {
                "verdict": "phase5-scoped-trigger-experiment-clean-not-promoted",
                "summary": {
                    "rows_evaluated": 1,
                    "triggered_rows": 1,
                    "target_improvements_kept": 1,
                    "triggered_regressions": 0,
                    "triggered_conflicts": 0,
                },
                "rows": [
                    {
                        "case": "sample",
                        "apk_path": "sample.apk",
                        "coordinate": component.coordinate,
                        "baseline_selected_version": "1.0.0",
                        "diagnostic_selected_version": "1.1.0",
                        "trigger_outcome": "trigger-target-improvement",
                        "trigger_decision": {
                            "apply": True,
                            "profile_id": "androidx-viewpager2-1.1.0-modern-or-security-low-confidence",
                        },
                    }
                ],
                "triggered_rows": [
                    {
                        "case": "sample",
                        "apk_path": "sample.apk",
                        "coordinate": component.coordinate,
                        "baseline_selected_version": "1.0.0",
                        "diagnostic_selected_version": "1.1.0",
                        "trigger_outcome": "trigger-target-improvement",
                        "trigger_decision": {
                            "apply": True,
                            "profile_id": "androidx-viewpager2-1.1.0-modern-or-security-low-confidence",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("apk_sbom.report.inspect_apk", lambda apk_path: make_apk())
    monkeypatch.setattr(
        "apk_sbom.report.match_apk_to_reference_db",
        lambda *args, **kwargs: make_match_summary(),
    )
    monkeypatch.setattr(
        "apk_sbom.report.detected_libraries_from_match_summary",
        lambda *args, **kwargs: [component],
    )

    artifacts = generate_final_report(
        "sample.apk",
        output_dir=tmp_path / "report",
        query_osv=False,
        r8_phase5_experiment_json=experiment_path,
    )
    report = json.loads((tmp_path / "report" / "report.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "report" / "report.md").read_text(encoding="utf-8")

    assert report["detected_components"][0]["version"] == "1.0.0"
    assert report["r8_phase5_experiment"]["report_only"] is True
    assert report["r8_phase5_experiment"]["summary"]["matching_triggered_rows"] == 1
    assert report["r8_phase5_experiment"]["matching_triggered_rows"][0][
        "diagnostic_selected_version"
    ] == "1.1.0"
    assert "Experimental R8 Phase 5 Evidence" in markdown
    assert "does not change detected components" in markdown
    assert "1.1.0" in markdown
    assert artifacts.sbom_json.endswith("sbom.cdx.json")


def test_generate_final_report_attaches_version_band_evidence_as_report_only(
    tmp_path,
    monkeypatch,
):
    component = DetectedLibrary(
        group="androidx.appcompat",
        artifact="appcompat",
        version="1.2.0",
        confidence=0.48,
        match_type="hybrid-candidate",
        evidence=[],
    )
    version_band_path = tmp_path / "version-band.json"
    version_band_path.write_text(
        json.dumps(
            {
                "verdict": "scoped-downgrade-experiment-promising-not-promoted",
                "summary": {
                    "introduced_mismatch_rows": 1,
                    "introduced_mismatches_flagged": 1,
                    "resolved_target_rows_blocked": 0,
                },
                "introduced_mismatch_rows": [
                    {
                        "case_id": "sample",
                        "coordinate": component.coordinate,
                        "selected_version": "1.2.0",
                        "source_versions": "1.7.1",
                        "trigger_decision": {
                            "apply": True,
                            "reason_codes": ["scoped-old-version-steal-profile"],
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    lifecycle_path = tmp_path / "lifecycle.json"
    lifecycle_path.write_text(
        json.dumps(
            {
                "verdict": "lifecycle-family-separation-promising-not-promoted",
                "summary": {
                    "introduced_lifecycle_rows": 1,
                    "public_claim_downgrade_candidates": 1,
                    "resolved_target_rows_blocked": 0,
                },
                "introduced_rows": [
                    {
                        "case_id": "sample",
                        "coordinate": "androidx.lifecycle:lifecycle-runtime",
                        "selected_version": "2.6.2",
                        "source_versions": "2.8.7",
                        "lifecycle_decision": {
                            "downgrade_public_claim": True,
                            "classification": "source-version-backed-target-family-evidence",
                            "target_coordinate": "androidx.lifecycle:lifecycle-runtime-android",
                            "target_version": "2.8.7",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("apk_sbom.report.inspect_apk", lambda apk_path: make_apk())
    monkeypatch.setattr(
        "apk_sbom.report.match_apk_to_reference_db",
        lambda *args, **kwargs: make_match_summary(),
    )
    monkeypatch.setattr(
        "apk_sbom.report.detected_libraries_from_match_summary",
        lambda *args, **kwargs: [component],
    )

    artifacts = generate_final_report(
        "sample.apk",
        output_dir=tmp_path / "report",
        query_osv=False,
        version_band_experiment_json=version_band_path,
        lifecycle_family_experiment_json=lifecycle_path,
    )
    report = json.loads((tmp_path / "report" / "report.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "report" / "report.md").read_text(encoding="utf-8")
    sbom = json.loads((tmp_path / "report" / "sbom.cdx.json").read_text(encoding="utf-8"))
    metadata_properties = {
        item["name"]: item["value"]
        for item in sbom["metadata"]["component"]["properties"]
    }

    assert report["detected_components"][0]["version"] == "1.2.0"
    assert report["version_band_experiments"]["report_only"] is True
    assert (
        report["version_band_experiments"]["old_version_steal"]["summary"][
            "matching_downgrade_rows"
        ]
        == 1
    )
    assert (
        report["version_band_experiments"]["lifecycle_family"]["summary"][
            "matching_downgrade_rows"
        ]
        == 1
    )
    assert "Experimental Version-Band Evidence" in markdown
    assert "version claim downgrade suggested" in markdown
    assert metadata_properties["apk-sbom:mvp:version-band-experiments-report-only"] == "true"
    assert "matching_downgrade_rows" in metadata_properties[
        "apk-sbom:mvp:version-band-experiment-summary"
    ]
    assert artifacts.sbom_json.endswith("sbom.cdx.json")


def test_generate_final_report_attaches_r8_minified_confidence_policy_as_report_only(
    tmp_path,
    monkeypatch,
):
    component = DetectedLibrary(
        group="androidx.viewpager2",
        artifact="viewpager2",
        version="1.0.0",
        confidence=0.42,
        match_type="hybrid-candidate",
        evidence=[],
    )
    policy_path = tmp_path / "r8-minified-policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "verdict": "r8-minified-confidence-policy-report-only-ready",
                "summary": {
                    "rows_classified": 2,
                    "regression_rows_blocked": 1,
                    "phase5_report_only_suggestions": 1,
                    "report_default_selection_changes": 0,
                },
                "rows": [
                    {
                        "case": "sample",
                        "apk_path": "sample.apk",
                        "coordinate": component.coordinate,
                        "baseline_selected_version": "1.0.0",
                        "diagnostic_selected_version": "1.1.0",
                        "source_versions": ["1.1.0"],
                        "confidence_label": "low-confidence-source-backed",
                        "policy_action": "surface-report-only-suggestion",
                        "policy_label": "report-only-source-backed-low-confidence-suggestion",
                        "signals": [
                            "baseline-low-confidence",
                            "phase5-report-only-trigger",
                        ],
                    },
                    {
                        "case": "sample",
                        "apk_path": "sample.apk",
                        "coordinate": component.coordinate,
                        "baseline_selected_version": "1.0.0",
                        "diagnostic_selected_version": "1.2.0",
                        "confidence_label": "ambiguous",
                        "policy_action": "do-not-change-selected-version",
                        "policy_label": "block-default-change-regression-risk",
                        "signals": [
                            "source-rejects-diagnostic",
                            "near-zero-score-margin",
                        ],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("apk_sbom.report.inspect_apk", lambda apk_path: make_apk())
    monkeypatch.setattr(
        "apk_sbom.report.match_apk_to_reference_db",
        lambda *args, **kwargs: make_match_summary(),
    )
    monkeypatch.setattr(
        "apk_sbom.report.detected_libraries_from_match_summary",
        lambda *args, **kwargs: [component],
    )

    generate_final_report(
        "sample.apk",
        output_dir=tmp_path / "report",
        query_osv=False,
        r8_minified_confidence_policy_json=policy_path,
    )
    report = json.loads((tmp_path / "report" / "report.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "report" / "report.md").read_text(encoding="utf-8")
    html = (tmp_path / "report" / "report.html").read_text(encoding="utf-8")
    sbom = json.loads((tmp_path / "report" / "sbom.cdx.json").read_text(encoding="utf-8"))

    assert report["detected_components"][0]["version"] == "1.0.0"
    assert report["r8_minified_confidence_policy"]["report_only"] is True
    assert report["r8_minified_confidence_policy"]["summary"]["matching_rows"] == 2
    assert (
        report["r8_minified_confidence_policy"]["summary"][
            "matching_report_only_suggestions"
        ]
        == 1
    )
    assert (
        report["r8_minified_confidence_policy"]["summary"][
            "matching_blocked_regression_risks"
        ]
        == 1
    )
    assert (
        report["r8_minified_confidence_policy"]["matching_report_only_suggestions"][0][
            "diagnostic_selected_version"
        ]
        == "1.1.0"
    )
    assert "Experimental R8 Minified Confidence Policy" in markdown
    assert "does not change detected components" in markdown
    assert "1.1.0" in markdown
    assert "Experimental R8 Minified Confidence Policy" in html
    sbom_component_versions = {
        component["bom-ref"]: component["version"] for component in sbom["components"]
    }
    assert sbom_component_versions["pkg:maven/androidx.viewpager2/viewpager2@1.0.0"] == "1.0.0"


def test_generate_final_report_applies_source_validation_to_osv(tmp_path, monkeypatch):
    component = DetectedLibrary(
        group="com.google.code.gson",
        artifact="gson",
        version="2.8.9",
        confidence=0.95,
        match_type="hybrid-exact",
        evidence=[],
    )
    validation_path = tmp_path / "source-validation.json"
    validation_path.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "coordinate": component.coordinate,
                        "status": "version-mismatch",
                        "source_versions": ["2.8.0"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    def fake_query_osv_for_libraries(*args, **kwargs):
        return OsvScanSummary(
            source="detected-libraries",
            api_url="https://api.osv.dev/v1/querybatch",
            components=1,
            vulnerable_components=1,
            vulnerabilities=1,
            results=[
                OsvComponentResult(
                    coordinate=component.coordinate,
                    version=component.version,
                    purl=component.purl,
                    status="ok",
                    vulnerabilities=[OsvVulnerability(id="GHSA-test-0001")],
                    finding_confidence="confirmed",
                    finding_reason="exact/high version confidence",
                )
            ],
            confirmed_vulnerable_components=1,
            confirmed_vulnerabilities=1,
        )

    monkeypatch.setattr("apk_sbom.report.inspect_apk", lambda apk_path: make_apk())
    monkeypatch.setattr("apk_sbom.report.match_apk_to_reference_db", lambda *args, **kwargs: make_match_summary())
    monkeypatch.setattr("apk_sbom.report.detected_libraries_from_match_summary", lambda *args, **kwargs: [component])
    monkeypatch.setattr("apk_sbom.report.query_osv_for_libraries", fake_query_osv_for_libraries)

    artifacts = generate_final_report(
        "sample.apk",
        output_dir=tmp_path / "report",
        query_osv=True,
        source_validation_json=validation_path,
    )
    osv = json.loads((tmp_path / "report" / "osv-vulnerabilities.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "report" / "report.md").read_text(encoding="utf-8")

    assert artifacts.vulnerabilities_json is not None
    assert osv["confirmed_vulnerabilities"] == 0
    assert osv["potential_vulnerabilities"] == 1
    assert osv["results"][0]["source_validation_finding"] == "source-version-mismatch"
    assert "1 potential (source-version-mismatch)" in markdown


def test_build_markdown_report_contains_summary_and_limitations():
    component = DetectedLibrary(
        group="com.google.code.gson",
        artifact="gson",
        version="2.8.9",
        confidence=0.95,
        match_type="hybrid-exact",
        evidence=[
            ComponentEvidence(
                source="package-overlap",
                detail="package matched",
                weight=1.0,
            )
        ],
    )
    osv_summary = OsvScanSummary(
        source="detected-libraries",
        api_url="https://api.osv.dev/v1/querybatch",
        components=1,
        vulnerable_components=1,
        vulnerabilities=1,
        results=[
            OsvComponentResult(
                coordinate=component.coordinate,
                version=component.version,
                purl=component.purl,
                status="ok",
                vulnerabilities=[
                    OsvVulnerability(
                        id="GHSA-test-0001",
                        aliases=["CVE-2026-0001"],
                        summary="Example vulnerability",
                        severity="HIGH",
                    )
                ],
                finding_confidence="confirmed",
                finding_reason="exact/high version confidence",
                source_validation_status="confirmed",
                source_versions=["2.8.9"],
                source_validation_finding="source-confirmed",
                source_validation_reason="the source dependency tree confirms this coordinate and version",
            )
        ],
        confirmed_vulnerable_components=1,
        confirmed_vulnerabilities=1,
    )

    markdown = build_markdown_report(
        make_apk(),
        make_match_summary(),
        [component],
        osv_summary,
        make_artifacts(),
        r8_phase5_experiment=make_r8_phase5_experiment(),
    )

    assert "# APK SBOM Recovery Report" in markdown
    assert "`com.google.code.gson:gson`" in markdown
    assert "Identity confidence" in markdown
    assert "Version confidence" in markdown
    assert "Candidate reasons" in markdown
    assert "Obfuscation Risk" in markdown
    assert "R8 / Obfuscation Diagnostics" in markdown
    assert "Inert Multi-Scale Feature Availability" in markdown
    assert "Experimental R8 Phase 5 Evidence" in markdown
    assert "Phase 5 suggestion" in markdown
    assert "does not change detected components" in markdown
    assert "Call-chain opcode fingerprints" in markdown
    assert "not used for matcher scoring" in markdown
    assert "`short_name_density`" in markdown
    assert "com.example.app" in markdown
    assert "HIGH" in markdown
    assert "1 confirmed" in markdown
    assert "source-confirmed" in markdown
    assert "hybrid-exact" in markdown
    assert "CVE-2026-0001" in markdown
    assert "Example vulnerability" in markdown
    assert "No native `.so` files were found" in markdown
    assert "Heavy R8 optimization" in markdown


def test_build_markdown_report_lists_native_libraries():
    apk = ApkInspection(
        apk_path="native.apk",
        apk_size=123,
        apk_sha256="b" * 64,
        dex_files=["classes.dex"],
        has_multidex=False,
        manifest_present=True,
        resources_arsc_present=False,
        native_libraries=[
            NativeLibrary(
                path="lib/arm64-v8a/libdemo.so",
                abi="arm64-v8a",
                filename="libdemo.so",
                size=12,
                sha256="c" * 64,
            )
        ],
    )

    markdown = build_markdown_report(
        apk,
        make_match_summary(),
        [],
        None,
        make_artifacts(),
    )

    assert "Native file components: 1" in markdown
    assert "`lib/arm64-v8a/libdemo.so`" in markdown
    assert "`" + ("c" * 64) + "`" in markdown


def test_build_json_report_contains_artifact_paths():
    payload = build_json_report(
        make_apk(),
        make_match_summary(),
        [],
        None,
        make_artifacts(),
    )

    assert payload["apk"]["apk_path"] == "sample.apk"
    assert payload["apk"]["manifest_metadata"]["package_name"] == "com.example.app"
    assert payload["match_summary"]["dex_files_analyzed"] == 1
    assert (
        payload["match_summary"]["inert_multiscale_features"]["scoring_status"]
        == "disabled"
    )
    assert payload["obfuscation_risk"]["level"] == "low"
    diagnostics = payload["obfuscation_diagnostics"]
    assert diagnostics["report_only"] is True
    assert {
        "short_name_density",
        "package_flattening_or_repackaging",
        "class_method_coverage_loss",
        "low_structural_coverage",
        "low_confidence_component_ratio",
        "nonstandard_dex_or_protector_hints",
        "resource_shrinking_symptoms",
        "method_inlining_or_class_merging_indicators",
    } <= set(diagnostics)
    assert payload["detected_components"] == []
    assert payload["artifacts"]["report_markdown"] == "data/results/report/report.md"
    assert payload["artifacts"]["report_html"] == "data/results/report/report.html"


def test_build_html_report_contains_dashboard_sections_and_escapes_values():
    component = DetectedLibrary(
        group="com.example",
        artifact="demo",
        version="1.0.0",
        confidence=0.5,
        match_type="hybrid-candidate",
        evidence=[],
    )
    apk = ApkInspection(
        apk_path="sample<danger>.apk",
        apk_size=123,
        apk_sha256="d" * 64,
        dex_files=["classes.dex"],
        has_multidex=False,
        manifest_present=True,
        resources_arsc_present=True,
        native_libraries=[],
    )

    html = build_html_report(
        apk,
        make_match_summary(),
        [component],
        None,
        make_artifacts(),
        r8_phase5_experiment=make_r8_phase5_experiment(),
    )

    assert "<!doctype html>" in html
    assert "APK SBOM Recovery Report" in html
    assert "Detected Components" in html
    assert "Version Decisions" in html
    assert "Version confidence" in html
    assert "APK Forensics" in html
    assert "R8 / Obfuscation Diagnostics" in html
    assert "Inert Multi-Scale Feature Availability" in html
    assert "Experimental R8 Phase 5 Evidence" in html
    assert "Phase 5 suggestion" in html
    assert "Basic-block opcode fingerprints" in html
    assert "short_name_density" in html
    assert "sample&lt;danger&gt;.apk" in html
    assert "hybrid-candidate" in html
    assert "report.html" in html


def test_report_surfaces_source_validation_caveat_for_vulnerabilities():
    component = DetectedLibrary(
        group="com.google.code.gson",
        artifact="gson",
        version="2.8.9",
        confidence=0.95,
        match_type="hybrid-exact",
        evidence=[],
    )
    osv_summary = OsvScanSummary(
        source="detected-libraries",
        api_url="https://api.osv.dev/v1/querybatch",
        components=1,
        vulnerable_components=1,
        vulnerabilities=1,
        results=[
            OsvComponentResult(
                coordinate=component.coordinate,
                version=component.version,
                purl=component.purl,
                status="ok",
                vulnerabilities=[OsvVulnerability(id="GHSA-test-0001", severity="HIGH")],
                finding_confidence="potential",
                finding_reason="source mismatch",
                source_validation_status="version-mismatch",
                source_versions=["2.8.0"],
                source_validation_finding="source-version-mismatch",
                source_validation_reason="the source dependency tree resolves version(s) 2.8.0",
            )
        ],
        potential_vulnerable_components=1,
        potential_vulnerabilities=1,
    )

    markdown = build_markdown_report(
        make_apk(),
        make_match_summary(),
        [component],
        osv_summary,
        make_artifacts(),
    )
    html = build_html_report(make_apk(), make_match_summary(), [component], osv_summary, make_artifacts())

    assert "1 potential (source-version-mismatch)" in markdown
    assert "Source validation" in markdown
    assert "2.8.0" in markdown
    assert "source-version-mismatch" in html


def test_reports_surface_version_ambiguity_notes():
    decision = VersionDecision(
        coordinate="androidx.startup:startup-runtime",
        group_id="androidx.startup",
        artifact_id="startup-runtime",
        selected_version="1.1.1",
        purl="pkg:maven/androidx.startup/startup-runtime@1.1.1",
        score=0.548511,
        confidence=0.548511,
        confidence_label="low",
        version_decision="candidate",
        gap_to_next=0.000655,
        reference_versions_considered=2,
        evidence=make_overlap_evidence(),
        alternatives=[],
        identity_confidence=0.55,
        identity_confidence_label="low",
        identity_status="candidate",
        version_confidence=0.548511,
        version_confidence_label="low",
        version_status="candidate",
        version_ambiguity_reason="Version ambiguity: 1.1.1 and 1.2.0 have equivalent evidence.",
        ambiguous_versions=[
            VersionAlternative(
                version="1.1.1",
                purl="pkg:maven/androidx.startup/startup-runtime@1.1.1",
                score=0.548511,
            ),
            VersionAlternative(
                version="1.2.0",
                purl="pkg:maven/androidx.startup/startup-runtime@1.2.0",
                score=0.547856,
            ),
        ],
    )
    summary = make_match_summary(decisions=[decision])

    markdown = build_markdown_report(make_apk(), summary, [], None, make_artifacts())
    html = build_html_report(make_apk(), summary, [], None, make_artifacts())
    payload = build_json_report(make_apk(), summary, [], None, make_artifacts())

    assert "Version ambiguity" in markdown
    assert "Notes" in markdown
    assert "Version ambiguity" in html
    assert payload["match_summary"]["decisions"][0]["version_ambiguity_reason"].startswith(
        "Version ambiguity"
    )
    assert payload["match_summary"]["decisions"][0]["ambiguous_versions"][1]["version"] == "1.2.0"


def test_reports_surface_generic_version_uncertainty_summary_without_selection_change():
    near_tie = VersionDecision(
        coordinate="androidx.startup:startup-runtime",
        group_id="androidx.startup",
        artifact_id="startup-runtime",
        selected_version="1.1.1",
        purl="pkg:maven/androidx.startup/startup-runtime@1.1.1",
        score=0.548511,
        confidence=0.548511,
        confidence_label="low",
        version_decision="candidate",
        gap_to_next=0.000655,
        reference_versions_considered=2,
        evidence=make_overlap_evidence(),
        alternatives=[
            VersionAlternative(
                version="1.2.0",
                purl="pkg:maven/androidx.startup/startup-runtime@1.2.0",
                score=0.547856,
            )
        ],
        identity_confidence=0.55,
        identity_confidence_label="low",
        identity_status="candidate",
        version_confidence=0.548511,
        version_confidence_label="low",
        version_status="candidate",
        version_ambiguity_reason=(
            "Version near-tie: 1.1.1 and 1.2.0 are within 0.001 score."
        ),
        ambiguous_versions=[
            VersionAlternative(
                version="1.1.1",
                purl="pkg:maven/androidx.startup/startup-runtime@1.1.1",
                score=0.548511,
            ),
            VersionAlternative(
                version="1.2.0",
                purl="pkg:maven/androidx.startup/startup-runtime@1.2.0",
                score=0.547856,
            ),
        ],
    )
    single_reference = VersionDecision(
        coordinate="example:single",
        group_id="example",
        artifact_id="single",
        selected_version="1.0.0",
        purl="pkg:maven/example/single@1.0.0",
        score=0.75,
        confidence=0.75,
        confidence_label="low",
        version_decision="candidate",
        gap_to_next=0.75,
        reference_versions_considered=1,
        evidence=make_overlap_evidence(),
        alternatives=[],
        identity_confidence=0.9,
        identity_confidence_label="high",
        identity_status="likely",
        version_confidence=0.75,
        version_confidence_label="low",
        version_status="candidate",
    )
    component = DetectedLibrary(
        group="androidx.startup",
        artifact="startup-runtime",
        version="1.1.1",
        confidence=0.548511,
        match_type="hybrid-candidate",
        evidence=[],
    )
    summary = make_match_summary(decisions=[near_tie, single_reference])

    uncertainty = build_version_uncertainty_summary(summary, [component])
    markdown = build_markdown_report(make_apk(), summary, [component], None, make_artifacts())
    html = build_html_report(make_apk(), summary, [component], None, make_artifacts())
    payload = build_json_report(make_apk(), summary, [component], None, make_artifacts())

    counts = uncertainty["summary"]["category_counts"]
    assert counts["near-tie"] == 1
    assert counts["single-reference-boundary"] == 1
    assert counts["low-confidence-version"] == 2
    assert uncertainty["rows"][0]["emitted_component"] is True
    assert payload["detected_components"][0]["version"] == "1.1.1"
    assert payload["version_uncertainty_summary"]["report_only"] is True
    assert (
        payload["version_uncertainty_summary"]["summary"]["uncertainty_rows"] == 2
    )
    assert "Version Uncertainty Summary" in markdown
    assert "single-reference-boundary" in markdown
    assert "does not change matcher scoring" in markdown
    assert "Version Uncertainty Summary" in html
    assert "near-tie" in html


def test_report_only_obfuscation_diagnostics_keep_selected_component_unchanged():
    decision = VersionDecision(
        coordinate="com.google.code.gson:gson",
        group_id="com.google.code.gson",
        artifact_id="gson",
        selected_version="2.8.9",
        purl="pkg:maven/com.google.code.gson/gson@2.8.9",
        score=0.42,
        confidence=0.42,
        confidence_label="low",
        version_decision="candidate",
        gap_to_next=0.01,
        reference_versions_considered=2,
        evidence=OverlapEvidence(
            matched_packages=0,
            reference_packages=1,
            apk_packages=3,
            package_score=0.0,
            matched_classes=2,
            reference_classes=10,
            apk_classes=40,
            class_score=0.2,
            matched_methods=3,
            reference_methods=80,
            apk_methods=300,
            method_score=0.0375,
            shared_opcodes=12,
            reference_distinct_opcodes=15,
            reference_opcode_total=100,
            apk_distinct_opcodes=20,
            apk_opcode_total=400,
            opcode_score=0.7,
            shared_opcode_ngrams=0,
            reference_distinct_opcode_ngrams=0,
            reference_opcode_ngram_total=0,
            apk_distinct_opcode_ngrams=0,
            apk_opcode_ngram_total=0,
            opcode_ngram_score=0.0,
            matched_dependency_edges=0,
            reference_dependency_edges=10,
            apk_dependency_edges=40,
            dependency_edge_score=0.0,
            reference_dependency_shape_bins=4,
            apk_dependency_shape_bins=4,
            dependency_shape_score=0.1,
            dependency_score=0.035,
            matched_string_literals=0,
            reference_string_literals=5,
            apk_string_literals=10,
            literal_score=0.0,
            matched_api_references=0,
            reference_api_references=0,
            apk_api_references=0,
            api_reference_score=0.0,
            matched_unique_classes=0,
            reference_unique_classes=2,
            unique_class_score=0.0,
            matched_unique_methods=0,
            reference_unique_methods=2,
            unique_method_score=0.0,
            matched_unique_literals=0,
            reference_unique_literals=1,
            unique_literal_score=0.0,
            unique_version_score=0.0,
        ),
        alternatives=[],
    )
    component = DetectedLibrary(
        group="com.google.code.gson",
        artifact="gson",
        version="2.8.9",
        confidence=0.42,
        match_type="hybrid-candidate",
        evidence=[],
        version_confidence=0.42,
        version_confidence_label="low",
        version_status="candidate",
    )

    payload = build_json_report(
        make_apk(),
        make_match_summary(decisions=[decision]),
        [component],
        None,
        make_artifacts(),
    )

    assert payload["detected_components"][0]["version"] == "2.8.9"
    assert payload["match_summary"]["decisions"][0]["selected_version"] == "2.8.9"
    diagnostics = payload["obfuscation_diagnostics"]
    assert diagnostics["class_method_coverage_loss"]["status"] == "warning"
    assert diagnostics["low_confidence_component_ratio"]["value"] == 1.0
    assert diagnostics["method_inlining_or_class_merging_indicators"]["status"] == "warning"
