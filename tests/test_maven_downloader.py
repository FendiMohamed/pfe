from __future__ import annotations

import json

from apk_sbom.maven_downloader import (
    DEFAULT_MAVEN_REPOSITORY_URL,
    MavenArtifact,
    artifact_record_from_file,
    artifact_record_from_files,
    artifacts_from_libraries,
    parse_pom_dependencies,
    write_artifact_metadata,
)
from apk_sbom.reference_config import MavenLibrary


def test_maven_artifact_url_and_paths():
    artifact = MavenArtifact(
        group="com.google.code.gson",
        artifact="gson",
        version="2.8.9",
        packaging="jar",
        repository_url=DEFAULT_MAVEN_REPOSITORY_URL,
    )

    assert artifact.filename == "gson-2.8.9.jar"
    assert artifact.purl == "pkg:maven/com.google.code.gson/gson@2.8.9"
    assert artifact.url == (
        "https://repo1.maven.org/maven2/com/google/code/gson/gson/2.8.9/gson-2.8.9.jar"
    )
    assert str(artifact.artifact_path("root")).endswith("com/google/code/gson/gson/2.8.9/gson-2.8.9.jar")
    assert str(artifact.metadata_path("root")).endswith("com/google/code/gson/gson/2.8.9/metadata.json")


def test_artifacts_from_libraries_filter_and_limit():
    libraries = [
        MavenLibrary(group="com.google.code.gson", artifact="gson", versions=("2.8.6", "2.8.9")),
        MavenLibrary(group="commons-codec", artifact="commons-codec", versions=("1.15",)),
    ]

    artifacts = artifacts_from_libraries(
        libraries,
        coordinate="com.google.code.gson:gson",
        limit=1,
    )

    assert len(artifacts) == 1
    assert artifacts[0].coordinate == "com.google.code.gson:gson"
    assert artifacts[0].version == "2.8.6"


def test_artifacts_from_libraries_supports_offset():
    libraries = [
        MavenLibrary(group="com.google.code.gson", artifact="gson", versions=("2.8.6", "2.8.9")),
        MavenLibrary(group="commons-codec", artifact="commons-codec", versions=("1.15",)),
    ]

    artifacts = artifacts_from_libraries(libraries, offset=1, limit=2)

    assert [(artifact.coordinate, artifact.version) for artifact in artifacts] == [
        ("com.google.code.gson:gson", "2.8.9"),
        ("commons-codec:commons-codec", "1.15"),
    ]


def test_artifacts_from_libraries_rejects_negative_offset():
    libraries = [MavenLibrary(group="com.google.code.gson", artifact="gson", versions=("2.8.9",))]

    try:
        artifacts_from_libraries(libraries, offset=-1)
    except ValueError as exc:
        assert "offset" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_artifacts_from_libraries_uses_per_library_packaging_and_repository():
    libraries = [
        MavenLibrary(
            group="androidx.core",
            artifact="core",
            versions=("1.13.1",),
            packaging="aar",
            repository_url="https://dl.google.com/dl/android/maven2",
        )
    ]

    artifacts = artifacts_from_libraries(libraries, packaging="jar")

    assert artifacts[0].packaging == "aar"
    assert artifacts[0].url == (
        "https://dl.google.com/dl/android/maven2/androidx/core/core/1.13.1/core-1.13.1.aar"
    )


def test_artifact_metadata_write(tmp_path):
    artifact = MavenArtifact(
        group="commons-codec",
        artifact="commons-codec",
        version="1.16.1",
        packaging="jar",
        repository_url=DEFAULT_MAVEN_REPOSITORY_URL,
    )
    artifact_path = tmp_path / "commons-codec-1.16.1.jar"
    artifact_path.write_bytes(b"fake jar bytes")

    record = artifact_record_from_file(artifact, artifact_path)
    metadata_path = write_artifact_metadata(record, tmp_path / "metadata.json")

    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert payload["coordinate"] == "commons-codec:commons-codec"
    assert payload["purl"] == "pkg:maven/commons-codec/commons-codec@1.16.1"
    assert payload["packaging"] == "jar"
    assert payload["size"] == len(b"fake jar bytes")
    assert len(payload["sha256"]) == 64


def test_parse_pom_dependencies_extracts_direct_compile_dependencies(tmp_path):
    pom_path = tmp_path / "demo.pom"
    pom_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <groupId>com.example</groupId>
  <artifactId>demo</artifactId>
  <version>1.0.0</version>
  <properties>
    <androidx.core.version>1.16.0</androidx.core.version>
  </properties>
  <dependencies>
    <dependency>
      <groupId>androidx.core</groupId>
      <artifactId>core</artifactId>
      <version>${androidx.core.version}</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
      <scope>test</scope>
      <optional>true</optional>
    </dependency>
  </dependencies>
</project>
""",
        encoding="utf-8",
    )

    dependencies = parse_pom_dependencies(pom_path)

    assert [(item.coordinate, item.version, item.scope, item.optional) for item in dependencies] == [
        ("androidx.core:core", "1.16.0", None, False),
        ("junit:junit", "4.13.2", "test", True),
    ]


def test_artifact_record_from_files_includes_pom_metadata(tmp_path):
    artifact = MavenArtifact(
        group="com.example",
        artifact="demo",
        version="1.0.0",
        packaging="jar",
        repository_url=DEFAULT_MAVEN_REPOSITORY_URL,
    )
    artifact_path = tmp_path / "demo-1.0.0.jar"
    artifact_path.write_bytes(b"fake jar bytes")
    pom_path = tmp_path / "demo-1.0.0.pom"
    pom_path.write_text(
        """<project>
  <dependencies>
    <dependency>
      <groupId>androidx.startup</groupId>
      <artifactId>startup-runtime</artifactId>
      <version>1.2.0</version>
    </dependency>
  </dependencies>
</project>
""",
        encoding="utf-8",
    )

    record = artifact_record_from_files(artifact, artifact_path, pom_path=pom_path)

    assert record.pom_url.endswith("/com/example/demo/1.0.0/demo-1.0.0.pom")
    assert record.pom_path == str(pom_path)
    assert record.pom_size == pom_path.stat().st_size
    assert record.dependencies[0].coordinate == "androidx.startup:startup-runtime"
