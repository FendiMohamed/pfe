from __future__ import annotations

from apk_sbom.reference_config import load_libraries_config


def test_load_libraries_config_has_expected_seed_libraries():
    libraries = load_libraries_config("configs/libraries.json")
    coordinates = {library.coordinate for library in libraries}

    assert "com.squareup.okhttp3:okhttp" in coordinates
    assert "com.google.code.gson:gson" in coordinates
    assert "com.fasterxml.jackson.core:jackson-databind" in coordinates


def test_maven_library_builds_purl():
    libraries = load_libraries_config("configs/libraries.json")
    okhttp = next(library for library in libraries if library.coordinate == "com.squareup.okhttp3:okhttp")

    assert okhttp.purl_for("4.9.0") == "pkg:maven/com.squareup.okhttp3/okhttp@4.9.0"

