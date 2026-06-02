from __future__ import annotations

import json

from apk_sbom.reference_expander import (
    expand_reference_catalog,
    load_reference_catalog,
    maven_metadata_url,
    parse_maven_metadata_versions,
    select_versions,
)


MAVEN_METADATA = """
<metadata>
  <groupId>com.example</groupId>
  <artifactId>demo</artifactId>
  <versioning>
    <versions>
      <version>1.0.0</version>
      <version>1.1.0-alpha01</version>
      <version>1.1.0</version>
      <version>2.0.0-rc01</version>
      <version>2.0.0</version>
    </versions>
  </versioning>
</metadata>
"""


def test_popular_catalog_contains_more_than_100_unique_coordinates():
    entries = load_reference_catalog("configs/popular_android_maven_catalog.json")
    coordinates = {entry.coordinate for entry in entries}

    assert len(entries) >= 100
    assert len(coordinates) == len(entries)
    assert "androidx.core:core" in coordinates
    assert "com.squareup.okhttp3:okhttp" in coordinates
    assert "com.google.firebase:firebase-messaging" in coordinates


def test_maven_metadata_url_supports_google_maven_repository():
    url = maven_metadata_url(
        "androidx.core",
        "core",
        repository_url="https://dl.google.com/dl/android/maven2",
    )

    assert url == "https://dl.google.com/dl/android/maven2/androidx/core/core/maven-metadata.xml"


def test_parse_and_select_latest_stable_versions():
    versions = parse_maven_metadata_versions(MAVEN_METADATA)

    assert versions == ["1.0.0", "1.1.0-alpha01", "1.1.0", "2.0.0-rc01", "2.0.0"]
    assert select_versions(versions, latest_count=2) == ["1.1.0", "2.0.0"]
    assert select_versions(versions, latest_count=2, include_prerelease=True) == [
        "2.0.0-rc01",
        "2.0.0",
    ]


def test_expand_reference_catalog_resolves_versions_and_writes_config(tmp_path):
    catalog_path = tmp_path / "catalog.json"
    output_path = tmp_path / "libraries.expanded.json"
    catalog_path.write_text(
        json.dumps(
            {
                "libraries": [
                    {
                        "group": "com.example",
                        "artifact": "demo",
                        "packaging": "jar",
                        "category": "test",
                    },
                    {
                        "group": "androidx.example",
                        "artifact": "ui",
                        "packaging": "aar",
                        "category": "test",
                        "repository_url": "https://dl.google.com/dl/android/maven2",
                    },
                    {
                        "group": "com.example",
                        "artifact": "pinned",
                        "packaging": "jar",
                        "category": "test",
                        "versions": ["3.0.0"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    fetched_urls = []

    def fake_fetcher(url: str, timeout: int) -> str:
        fetched_urls.append((url, timeout))
        return MAVEN_METADATA

    summary = expand_reference_catalog(
        catalog_path,
        output_path=output_path,
        latest_count=2,
        timeout=9,
        fetcher=fake_fetcher,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    demo = next(item for item in payload["libraries"] if item["artifact"] == "demo")
    ui = next(item for item in payload["libraries"] if item["artifact"] == "ui")
    pinned = next(item for item in payload["libraries"] if item["artifact"] == "pinned")

    assert summary.selected_libraries == 3
    assert summary.failed == 0
    assert demo["versions"] == ["1.1.0", "2.0.0"]
    assert ui["packaging"] == "aar"
    assert ui["repository_url"] == "https://dl.google.com/dl/android/maven2"
    assert pinned["versions"] == ["3.0.0"]
    assert fetched_urls == [
        ("https://repo1.maven.org/maven2/com/example/demo/maven-metadata.xml", 9),
        ("https://dl.google.com/dl/android/maven2/androidx/example/ui/maven-metadata.xml", 9),
    ]


def test_expand_reference_catalog_dry_run_does_not_write_config(tmp_path):
    catalog_path = tmp_path / "catalog.json"
    output_path = tmp_path / "libraries.expanded.json"
    catalog_path.write_text(
        json.dumps(
            {
                "libraries": [
                    {
                        "group": "com.example",
                        "artifact": "demo",
                        "packaging": "jar",
                        "category": "test",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    summary = expand_reference_catalog(
        catalog_path,
        output_path=output_path,
        dry_run=True,
        fetcher=lambda url, timeout: MAVEN_METADATA,
    )

    assert summary.selected_libraries == 1
    assert not output_path.exists()
