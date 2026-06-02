from __future__ import annotations

import json

from apk_sbom.source_validation import (
    parse_gradle_dependency_tree,
    parse_maven_component_spec,
    validate_cyclonedx_against_gradle_tree,
    write_source_validation_report,
)


def make_sbom(path):
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "components": [
            {
                "type": "library",
                "group": "com.squareup.okhttp3",
                "name": "okhttp",
                "version": "4.12.0",
                "purl": "pkg:maven/com.squareup.okhttp3/okhttp@4.12.0",
                "properties": [
                    {"name": "apk-sbom:mvp:confidence", "value": "0.807"},
                    {"name": "apk-sbom:mvp:match-type", "value": "hybrid-likely"},
                ],
            },
            {
                "type": "library",
                "group": "com.squareup.okio",
                "name": "okio-jvm",
                "version": "3.6.0",
                "purl": "pkg:maven/com.squareup.okio/okio-jvm@3.6.0",
                "properties": [
                    {"name": "apk-sbom:mvp:confidence", "value": "0.543"},
                    {"name": "apk-sbom:mvp:match-type", "value": "hybrid-candidate"},
                ],
            },
            {
                "type": "library",
                "group": "missing.group",
                "name": "missing-artifact",
                "version": "1.0.0",
                "purl": "pkg:maven/missing.group/missing-artifact@1.0.0",
            },
            {
                "type": "file",
                "name": "libdemo.so",
            },
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_parse_gradle_dependency_tree_handles_resolved_versions():
    tree = """
fullReleaseRuntimeClasspath - Runtime classpath.
+--- com.squareup.okhttp3:okhttp:4.12.0
|    +--- com.squareup.okio:okio:3.6.0 -> 3.7.0
|    |    \\--- com.squareup.okio:okio-jvm:3.7.0
+--- project :libs:download
\\--- org.jetbrains.kotlin:kotlin-stdlib:2.0.20 -> 2.0.21 (c)
"""

    dependencies = parse_gradle_dependency_tree(tree)

    assert dependencies["com.squareup.okhttp3:okhttp"].resolved_versions == ["4.12.0"]
    assert dependencies["com.squareup.okio:okio"].requested_versions == ["3.6.0"]
    assert dependencies["com.squareup.okio:okio"].resolved_versions == ["3.7.0"]
    assert dependencies["com.squareup.okio:okio-jvm"].resolved_versions == ["3.7.0"]
    assert "project :libs:download" not in dependencies


def test_validate_cyclonedx_against_gradle_tree_marks_confirmed_mismatch_and_missing(tmp_path):
    sbom_path = tmp_path / "sbom.cdx.json"
    tree_path = tmp_path / "dependencies.txt"
    make_sbom(sbom_path)
    tree_path.write_text(
        """
+--- com.squareup.okhttp3:okhttp:4.12.0
|    +--- com.squareup.okio:okio:3.6.0 -> 3.7.0
|    |    \\--- com.squareup.okio:okio-jvm:3.7.0
""",
        encoding="utf-8",
    )

    summary = validate_cyclonedx_against_gradle_tree(sbom_path, tree_path)

    assert summary.sbom_components == 3
    assert summary.confirmed == 1
    assert summary.version_mismatches == 1
    assert summary.missing == 1
    statuses = {result.coordinate: result.status for result in summary.results}
    assert statuses["com.squareup.okhttp3:okhttp"] == "confirmed"
    assert statuses["com.squareup.okio:okio-jvm"] == "version-mismatch"
    assert statuses["missing.group:missing-artifact"] == "missing"


def test_write_source_validation_report_includes_extra_candidate_section(tmp_path):
    sbom_path = tmp_path / "sbom.cdx.json"
    tree_path = tmp_path / "dependencies.txt"
    output_dir = tmp_path / "validation"
    make_sbom(sbom_path)
    tree_path.write_text(
        """
+--- com.squareup.okhttp3:okhttp:4.12.0
+--- com.squareup.okio:okio:3.6.0 -> 3.7.0
\\--- com.squareup.okio:okio-jvm:3.7.0
""",
        encoding="utf-8",
    )

    artifacts = write_source_validation_report(
        sbom_path,
        tree_path,
        output_dir=output_dir,
        extra_candidates=[parse_maven_component_spec("com.squareup.okio:okio@2.8.0")],
    )

    payload = json.loads((output_dir / "source-validation.json").read_text(encoding="utf-8"))
    markdown = (output_dir / "source-validation.md").read_text(encoding="utf-8")
    assert artifacts.validation_json.endswith("source-validation.json")
    assert payload["extra_candidates"] == 1
    assert payload["candidate_version_mismatches"] == 1
    assert "## Extra Candidate Comparison" in markdown
    assert "`com.squareup.okio:okio`" in markdown
    assert "version-mismatch" in markdown
