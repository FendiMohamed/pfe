from __future__ import annotations

from datetime import UTC, datetime
import json
import zipfile

from apk_sbom.apk_extractor import inspect_apk
from apk_sbom.models import ComponentEvidence, DetectedLibrary
from apk_sbom.sbom import build_cyclonedx_bom, make_mock_detection


def test_build_cyclonedx_bom_contains_maven_component(tmp_path):
    apk_path = tmp_path / "sample.apk"
    with zipfile.ZipFile(apk_path, "w") as archive:
        archive.writestr("classes.dex", b"dex\n035\0")
        archive.writestr(
            "AndroidManifest.xml",
            """<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app"
    android:versionCode="42"
    android:versionName="1.2.3">
    <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="35" />
</manifest>""",
        )
        archive.writestr("lib/arm64-v8a/libdemo.so", b"native-bytes")

    inspection = inspect_apk(apk_path)
    bom = build_cyclonedx_bom(
        inspection,
        [make_mock_detection()],
        timestamp=datetime(2026, 5, 18, tzinfo=UTC),
        serial_number="urn:uuid:00000000-0000-0000-0000-000000000000",
    ).to_dict()

    assert bom["bomFormat"] == "CycloneDX"
    assert bom["specVersion"] == "1.5"
    assert bom["metadata"]["component"]["name"] == "sample.apk"
    assert bom["metadata"]["component"]["hashes"][0]["content"] == inspection.apk_sha256
    metadata_properties = {
        item["name"]: item["value"]
        for item in bom["metadata"]["component"]["properties"]
    }
    assert metadata_properties["apk-sbom:mvp:manifest-package"] == "com.example.app"
    assert metadata_properties["apk-sbom:mvp:manifest-version-code"] == "42"
    assert metadata_properties["apk-sbom:mvp:target-sdk"] == "35"
    assert metadata_properties["apk-sbom:mvp:extraction-risk"] == "low"
    assert bom["components"][0]["group"] == "com.google.code.gson"
    assert bom["components"][0]["name"] == "gson"
    assert bom["components"][0]["version"] == "2.8.9"
    assert bom["components"][0]["purl"] == "pkg:maven/com.google.code.gson/gson@2.8.9"
    component_properties = {
        item["name"]: item["value"] for item in bom["components"][0]["properties"]
    }
    assert component_properties["apk-sbom:mvp:identity-confidence"] == "0.850"
    assert component_properties["apk-sbom:mvp:identity-status"] == "mock"
    assert component_properties["apk-sbom:mvp:version-confidence"] == "0.850"
    assert component_properties["apk-sbom:mvp:version-status"] == "mock"
    assert bom["components"][1]["type"] == "file"
    assert bom["components"][1]["name"] == "libdemo.so"
    assert bom["components"][1]["hashes"][0]["content"] == inspection.native_libraries[0].sha256
    assert {
        item["value"]
        for item in bom["components"][1]["properties"]
        if item["name"] == "apk-sbom:mvp:native-identification"
    } == {"hash-only"}
    assert bom["dependencies"][0]["dependsOn"] == [
        "pkg:maven/com.google.code.gson/gson@2.8.9",
        "apk-native:lib/arm64-v8a/libdemo.so",
    ]


def test_cyclonedx_bom_write_json(tmp_path):
    apk_path = tmp_path / "sample.apk"
    output_path = tmp_path / "result" / "mock-sbom.cdx.json"
    with zipfile.ZipFile(apk_path, "w") as archive:
        archive.writestr("classes.dex", b"dex\n035\0")

    bom = build_cyclonedx_bom(inspect_apk(apk_path), [make_mock_detection()])
    written_path = bom.write_json(output_path)

    assert written_path == output_path
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["components"][0]["purl"] == "pkg:maven/com.google.code.gson/gson@2.8.9"


def test_cyclonedx_bom_surfaces_ambiguous_versions(tmp_path):
    apk_path = tmp_path / "sample.apk"
    with zipfile.ZipFile(apk_path, "w") as archive:
        archive.writestr("classes.dex", b"dex\n035\0")

    component = DetectedLibrary(
        group="androidx.startup",
        artifact="startup-runtime",
        version="1.1.1",
        confidence=0.55,
        match_type="hybrid-candidate",
        evidence=[
            ComponentEvidence(
                source="version-ambiguity",
                detail="Version ambiguity: 1.1.1 and 1.2.0 are feature-equivalent.",
                weight=0.55,
            )
        ],
        ambiguous_versions=["1.1.1", "1.2.0"],
    )

    bom = build_cyclonedx_bom(inspect_apk(apk_path), [component]).to_dict()
    component_properties = {
        item["name"]: item["value"] for item in bom["components"][0]["properties"]
    }

    assert json.loads(component_properties["apk-sbom:mvp:ambiguous-versions"]) == [
        "1.1.1",
        "1.2.0",
    ]
