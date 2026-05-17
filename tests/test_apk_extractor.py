from __future__ import annotations

import zipfile

from apk_sbom.apk_extractor import inspect_apk


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

