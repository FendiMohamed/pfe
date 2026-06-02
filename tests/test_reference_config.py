from __future__ import annotations

from apk_sbom.reference_config import load_libraries_config


def test_load_libraries_config_has_expected_seed_libraries():
    libraries = load_libraries_config("configs/libraries.json")
    coordinates = {library.coordinate for library in libraries}

    assert "com.squareup.okhttp3:okhttp" in coordinates
    assert "com.squareup.okio:okio-jvm" in coordinates
    assert "com.google.code.gson:gson" in coordinates
    assert "com.fasterxml.jackson.core:jackson-databind" in coordinates


def test_maven_library_builds_purl():
    libraries = load_libraries_config("configs/libraries.json")
    okhttp = next(library for library in libraries if library.coordinate == "com.squareup.okhttp3:okhttp")

    assert okhttp.purl_for("4.9.0") == "pkg:maven/com.squareup.okhttp3/okhttp@4.9.0"


def test_load_libraries_config_supports_packaging_and_repository_url(tmp_path):
    config_path = tmp_path / "libraries.json"
    config_path.write_text(
        """
{
  "libraries": [
    {
      "group": "androidx.core",
      "artifact": "core",
      "packaging": "aar",
      "repository_url": "https://dl.google.com/dl/android/maven2",
      "versions": ["1.13.1"]
    }
  ]
}
""",
        encoding="utf-8",
    )

    libraries = load_libraries_config(config_path)

    assert libraries[0].packaging == "aar"
    assert libraries[0].repository_url == "https://dl.google.com/dl/android/maven2"


def test_load_calibration_config_contains_source_versions_and_android_variants():
    libraries = load_libraries_config("configs/libraries.calibration.json")
    by_coordinate = {library.coordinate: library for library in libraries}

    assert by_coordinate["androidx.core:core"].versions == (
        "1.9.0",
        "1.15.0",
        "1.16.0",
        "1.18.0",
    )
    assert by_coordinate["androidx.work:work-runtime"].versions == (
        "2.10.0",
        "2.10.3",
        "2.10.5",
        "2.11.2",
    )
    assert "androidx.compose.ui:ui-android" in by_coordinate
    assert "androidx.datastore:datastore-core-android" in by_coordinate
