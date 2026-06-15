from __future__ import annotations

import json
import shutil
import xml.etree.ElementTree as ET
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

from apk_sbom.apk_extractor import sha256_file
from apk_sbom.reference_config import MavenLibrary


DEFAULT_MAVEN_REPOSITORY_URL = "https://repo1.maven.org/maven2"
DEFAULT_REFERENCE_ARTIFACT_ROOT = Path("data/reference_db/artifacts")
USER_AGENT = "apk-sbom-mvp/0.1.0"


@dataclass(frozen=True)
class MavenPomDependency:
    group: str
    artifact: str
    version: str | None = None
    scope: str | None = None
    optional: bool = False
    type: str | None = None
    classifier: str | None = None

    @property
    def coordinate(self) -> str:
        return f"{self.group}:{self.artifact}"


@dataclass(frozen=True)
class MavenArtifact:
    group: str
    artifact: str
    version: str
    packaging: str
    repository_url: str

    @property
    def coordinate(self) -> str:
        return f"{self.group}:{self.artifact}"

    @property
    def purl(self) -> str:
        return f"pkg:maven/{self.group}/{self.artifact}@{self.version}"

    @property
    def filename(self) -> str:
        return f"{self.artifact}-{self.version}.{self.packaging}"

    @property
    def pom_filename(self) -> str:
        return f"{self.artifact}-{self.version}.pom"

    @property
    def url(self) -> str:
        repository = self.repository_url.rstrip("/")
        group_path = self.group.replace(".", "/")
        return f"{repository}/{group_path}/{self.artifact}/{self.version}/{self.filename}"

    @property
    def pom_url(self) -> str:
        repository = self.repository_url.rstrip("/")
        group_path = self.group.replace(".", "/")
        return f"{repository}/{group_path}/{self.artifact}/{self.version}/{self.pom_filename}"

    def output_dir(self, root: str | Path) -> Path:
        group_path = Path(*self.group.split("."))
        return Path(root) / group_path / self.artifact / self.version

    def artifact_path(self, root: str | Path) -> Path:
        return self.output_dir(root) / self.filename

    def pom_path(self, root: str | Path) -> Path:
        return self.output_dir(root) / self.pom_filename

    def metadata_path(self, root: str | Path) -> Path:
        return self.output_dir(root) / "metadata.json"


@dataclass(frozen=True)
class ArtifactRecord:
    group: str
    artifact: str
    version: str
    coordinate: str
    purl: str
    packaging: str
    url: str
    path: str
    sha256: str
    size: int
    pom_url: str | None = None
    pom_path: str | None = None
    pom_sha256: str | None = None
    pom_size: int | None = None
    pom_error: str | None = None
    dependencies: list[MavenPomDependency] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, payload: dict) -> ArtifactRecord:
        dependencies = [
            item
            if isinstance(item, MavenPomDependency)
            else MavenPomDependency(
                group=str(item["group"]),
                artifact=str(item["artifact"]),
                version=item.get("version"),
                scope=item.get("scope"),
                optional=bool(item.get("optional", False)),
                type=item.get("type"),
                classifier=item.get("classifier"),
            )
            for item in payload.get("dependencies", [])
        ]
        fields = {
            "group",
            "artifact",
            "version",
            "coordinate",
            "purl",
            "packaging",
            "url",
            "path",
            "sha256",
            "size",
            "pom_url",
            "pom_path",
            "pom_sha256",
            "pom_size",
            "pom_error",
        }
        values = {key: payload[key] for key in fields if key in payload}
        return cls(**values, dependencies=dependencies)


@dataclass(frozen=True)
class DownloadResult:
    artifact: MavenArtifact
    status: str
    path: str
    metadata_path: str
    error: str | None = None

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["artifact"] = asdict(self.artifact)
        return payload


def artifacts_from_libraries(
    libraries: list[MavenLibrary],
    *,
    repository_url: str = DEFAULT_MAVEN_REPOSITORY_URL,
    packaging: str = "jar",
    coordinate: str | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> list[MavenArtifact]:
    if offset < 0:
        raise ValueError("offset must be >= 0")

    artifacts: list[MavenArtifact] = []
    seen = 0

    for library in libraries:
        if coordinate and library.coordinate != coordinate:
            continue
        for version in library.versions:
            if seen < offset:
                seen += 1
                continue
            seen += 1
            artifacts.append(
                MavenArtifact(
                    group=library.group,
                    artifact=library.artifact,
                    version=version,
                    packaging=library.packaging or packaging,
                    repository_url=library.repository_url or repository_url,
                )
            )
            if limit is not None and len(artifacts) >= limit:
                return artifacts

    return artifacts


def artifact_record_from_file(artifact: MavenArtifact, artifact_path: str | Path) -> ArtifactRecord:
    path = Path(artifact_path)
    return ArtifactRecord(
        group=artifact.group,
        artifact=artifact.artifact,
        version=artifact.version,
        coordinate=artifact.coordinate,
        purl=artifact.purl,
        packaging=artifact.packaging,
        url=artifact.url,
        path=str(path),
        sha256=sha256_file(path),
        size=path.stat().st_size,
    )


def artifact_record_from_files(
    artifact: MavenArtifact,
    artifact_path: str | Path,
    *,
    pom_path: str | Path | None = None,
    pom_error: str | None = None,
) -> ArtifactRecord:
    record = artifact_record_from_file(artifact, artifact_path)
    base = {
        "group": record.group,
        "artifact": record.artifact,
        "version": record.version,
        "coordinate": record.coordinate,
        "purl": record.purl,
        "packaging": record.packaging,
        "url": record.url,
        "path": record.path,
        "sha256": record.sha256,
        "size": record.size,
    }
    if pom_path is None:
        return ArtifactRecord(
            **base,
            pom_url=artifact.pom_url,
            pom_error=pom_error,
        )

    resolved_pom = Path(pom_path)
    return ArtifactRecord(
        **base,
        pom_url=artifact.pom_url,
        pom_path=str(resolved_pom),
        pom_sha256=sha256_file(resolved_pom),
        pom_size=resolved_pom.stat().st_size,
        pom_error=pom_error,
        dependencies=parse_pom_dependencies(resolved_pom),
    )


def write_artifact_metadata(record: ArtifactRecord, metadata_path: str | Path) -> Path:
    path = Path(metadata_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record.to_json() + "\n", encoding="utf-8")
    return path


def parse_pom_dependencies(pom_path: str | Path) -> list[MavenPomDependency]:
    path = Path(pom_path)
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        return []

    properties = _pom_properties(root)
    dependencies: list[MavenPomDependency] = []
    for dependency in root.findall("./{*}dependencies/{*}dependency"):
        group = _pom_child_text(dependency, "groupId", properties)
        artifact = _pom_child_text(dependency, "artifactId", properties)
        if not group or not artifact:
            continue
        dependencies.append(
            MavenPomDependency(
                group=group,
                artifact=artifact,
                version=_pom_child_text(dependency, "version", properties),
                scope=_pom_child_text(dependency, "scope", properties),
                optional=(_pom_child_text(dependency, "optional", properties) == "true"),
                type=_pom_child_text(dependency, "type", properties),
                classifier=_pom_child_text(dependency, "classifier", properties),
            )
        )
    return dependencies


def download_artifact(
    artifact: MavenArtifact,
    *,
    output_root: str | Path = DEFAULT_REFERENCE_ARTIFACT_ROOT,
    timeout: int = 60,
    force: bool = False,
) -> DownloadResult:
    artifact_path = artifact.artifact_path(output_root)
    pom_path = artifact.pom_path(output_root)
    metadata_path = artifact.metadata_path(output_root)

    if artifact_path.exists() and metadata_path.exists() and not force:
        return DownloadResult(
            artifact=artifact,
            status="existing",
            path=str(artifact_path),
            metadata_path=str(metadata_path),
        )

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = artifact_path.with_suffix(artifact_path.suffix + ".tmp")

    request = urllib.request.Request(
        artifact.url,
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            with temp_path.open("wb") as handle:
                shutil.copyfileobj(response, handle)
        temp_path.replace(artifact_path)
        pom_error = _download_pom(artifact, pom_path, timeout=timeout)
        record = artifact_record_from_files(
            artifact,
            artifact_path,
            pom_path=pom_path if pom_path.exists() else None,
            pom_error=pom_error,
        )
        write_artifact_metadata(record, metadata_path)
    except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        if temp_path.exists():
            temp_path.unlink()
        return DownloadResult(
            artifact=artifact,
            status="failed",
            path=str(artifact_path),
            metadata_path=str(metadata_path),
            error=str(exc),
        )

    return DownloadResult(
        artifact=artifact,
        status="downloaded",
        path=str(artifact_path),
        metadata_path=str(metadata_path),
    )


def _download_pom(artifact: MavenArtifact, pom_path: Path, *, timeout: int) -> str | None:
    temp_path = pom_path.with_suffix(pom_path.suffix + ".tmp")
    request = urllib.request.Request(
        artifact.pom_url,
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            with temp_path.open("wb") as handle:
                shutil.copyfileobj(response, handle)
        temp_path.replace(pom_path)
    except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        if temp_path.exists():
            temp_path.unlink()
        return str(exc)
    return None


def _pom_properties(root: ET.Element) -> dict[str, str]:
    properties: dict[str, str] = {}
    for child in root.findall("./{*}properties/*"):
        tag = _strip_namespace(child.tag)
        if child.text:
            properties[tag] = child.text.strip()
    group = root.findtext("./{*}groupId") or root.findtext("./{*}parent/{*}groupId")
    version = root.findtext("./{*}version") or root.findtext("./{*}parent/{*}version")
    artifact = root.findtext("./{*}artifactId")
    if group:
        properties["project.groupId"] = group.strip()
        properties["pom.groupId"] = group.strip()
    if version:
        properties["project.version"] = version.strip()
        properties["pom.version"] = version.strip()
    if artifact:
        properties["project.artifactId"] = artifact.strip()
        properties["pom.artifactId"] = artifact.strip()
    return properties


def _pom_child_text(
    parent: ET.Element,
    child_name: str,
    properties: dict[str, str],
) -> str | None:
    value = parent.findtext(f"{{*}}{child_name}")
    if value is None:
        return None
    return _resolve_pom_property(value.strip(), properties)


def _resolve_pom_property(value: str, properties: dict[str, str]) -> str:
    if value.startswith("${") and value.endswith("}"):
        return properties.get(value[2:-1], value)
    return value


def _strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", maxsplit=1)[-1]
    return tag


def download_artifacts(
    artifacts: list[MavenArtifact],
    *,
    output_root: str | Path = DEFAULT_REFERENCE_ARTIFACT_ROOT,
    timeout: int = 60,
    force: bool = False,
) -> list[DownloadResult]:
    return [
        download_artifact(artifact, output_root=output_root, timeout=timeout, force=force)
        for artifact in artifacts
    ]
