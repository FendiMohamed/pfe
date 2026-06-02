from __future__ import annotations

import json
import zipfile

from apk_sbom.apk_extractor import inspect_apk
from apk_sbom.cli import main


def test_inspect_apk_detects_multidex_and_native_library(tmp_path):
    apk_path = tmp_path / "sample.apk"
    with zipfile.ZipFile(apk_path, "w") as archive:
        archive.writestr("classes.dex", b"dex\n035\0")
        archive.writestr("classes2.dex", b"dex\n035\0")
        archive.writestr("AndroidManifest.xml", b"manifest")
        archive.writestr("resources.arsc", b"resources")
        archive.writestr("lib/arm64-v8a/libdemo.so", b"native")

    inspection = inspect_apk(apk_path)

    assert inspection.dex_files == ["classes.dex", "classes2.dex"]
    assert inspection.has_multidex is True
    assert inspection.manifest_present is True
    assert inspection.resources_arsc_present is True
    assert len(inspection.native_libraries) == 1
    assert inspection.native_libraries[0].abi == "arm64-v8a"
    assert inspection.native_libraries[0].filename == "libdemo.so"
    assert inspection.forensic_summary.standard_dex_files == ["classes.dex", "classes2.dex"]
    assert inspection.forensic_summary.extraction_risk == "low"


def test_inspect_apk_extracts_text_manifest_metadata_and_forensic_indicators(tmp_path):
    apk_path = tmp_path / "sample.apk"
    manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app"
    android:versionCode="42"
    android:versionName="1.2.3">
    <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="35" />
    <uses-permission android:name="android.permission.INTERNET" />
</manifest>
"""
    with zipfile.ZipFile(apk_path, "w") as archive:
        archive.writestr("classes.dex", b"dex")
        archive.writestr("assets/classes2.dex", b"dex\n035\0")
        archive.writestr("assets/protect_payload.dat", b"x" * (1024 * 1024))
        archive.writestr("AndroidManifest.xml", manifest)

    inspection = inspect_apk(apk_path)

    assert inspection.manifest_metadata.package_name == "com.example.app"
    assert inspection.manifest_metadata.version_code == "42"
    assert inspection.manifest_metadata.version_name == "1.2.3"
    assert inspection.manifest_metadata.min_sdk == "23"
    assert inspection.manifest_metadata.target_sdk == "35"
    assert inspection.manifest_metadata.permissions == ["android.permission.INTERNET"]
    assert inspection.manifest_metadata.parse_status == "parsed"
    assert inspection.forensic_summary.nonstandard_dex_files == ["assets/classes2.dex"]
    assert inspection.forensic_summary.extraction_risk == "medium"
    assert {indicator.code for indicator in inspection.forensic_summary.indicators} >= {
        "nonstandard-dex",
        "tiny-primary-dex",
        "protector-name-hint",
    }


def test_inspect_apk_cli_exposes_report_only_obfuscation_diagnostics(tmp_path, capsys):
    apk_path = tmp_path / "sample.apk"
    with zipfile.ZipFile(apk_path, "w") as archive:
        archive.writestr("classes.dex", b"dex\n035\0")
        archive.writestr("AndroidManifest.xml", "<manifest package=\"com.example\" />")

    exit_code = main(["inspect-apk", str(apk_path)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    diagnostics = payload["obfuscation_diagnostics"]
    assert diagnostics["report_only"] is True
    assert "short_name_density" in diagnostics
    assert "package_flattening_or_repackaging" in diagnostics
    assert "method_inlining_or_class_merging_indicators" in diagnostics
