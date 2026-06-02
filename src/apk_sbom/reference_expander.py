from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from packaging.version import InvalidVersion, Version

from apk_sbom.maven_downloader import DEFAULT_MAVEN_REPOSITORY_URL, USER_AGENT
from apk_sbom.reference_config import MavenLibrary


DEFAULT_REFERENCE_CATALOG = Path("configs/popular_android_maven_catalog.json")
DEFAULT_EXPANDED_CONFIG = Path("configs/libraries.expanded.json")
PRE_RELEASE_RE = re.compile(
    r"(?:^|[.\-_])(?:alpha|beta|rc|cr|m|milestone|snapshot|dev|preview|eap)(?:[.\-_0-9]|$)",
    re.IGNORECASE,
)
MetadataFetcher = Callable[[str, int], str]


@dataclass(frozen=True)
class CatalogEntry:
    group: str
    artifact: str
    packaging: str
    category: str
    repository_url: str | None = None
    versions: tuple[str, ...] = ()
    notes: str | None = None

    @property
    def coordinate(self) -> str:
        return f"{self.group}:{self.artifact}"


@dataclass(frozen=True)
class ExpandedLibraryResult:
    entry: CatalogEntry
    status: str
    selected_versions: tuple[str, ...]
    metadata_url: str
    available_versions: tuple[str, ...] = ()
    error: str | None = None

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["entry"] = asdict(self.entry)
        return payload


@dataclass(frozen=True)
class ReferenceExpansionSummary:
    catalog_path: str
    output_path: str | None
    repository_url: str
    latest_count: int
    include_prerelease: bool
    total_entries: int
    selected_libraries: int
    failed: int
    results: list[ExpandedLibraryResult]

    def to_dict(self) -> dict:
        return {
            "catalog_path": self.catalog_path,
            "output_path": self.output_path,
            "repository_url": self.repository_url,
            "latest_count": self.latest_count,
            "include_prerelease": self.include_prerelease,
            "total_entries": self.total_entries,
            "selected_libraries": self.selected_libraries,
            "failed": self.failed,
            "results": [result.to_dict() for result in self.results],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    def write_json(self, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json() + "\n", encoding="utf-8")
        return path


def load_reference_catalog(path: str | Path) -> list[CatalogEntry]:
    catalog_path = Path(path)
    with catalog_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    entries = payload.get("libraries")
    if not isinstance(entries, list):
        raise ValueError("reference catalog must contain a 'libraries' list")

    parsed: list[CatalogEntry] = []
    seen: set[str] = set()
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise ValueError(f"catalog entry #{index} must be an object")
        group = item.get("group")
        artifact = item.get("artifact")
        packaging = item.get("packaging", "jar")
        category = item.get("category", "uncategorized")
        repository_url = item.get("repository_url")
        versions = item.get("versions", [])
        notes = item.get("notes")

        if not isinstance(group, str) or not group:
            raise ValueError(f"catalog entry #{index} has invalid group")
        if not isinstance(artifact, str) or not artifact:
            raise ValueError(f"catalog entry #{index} has invalid artifact")
        if packaging not in {"jar", "aar"}:
            raise ValueError(f"catalog entry #{index} has invalid packaging")
        if not isinstance(category, str) or not category:
            raise ValueError(f"catalog entry #{index} has invalid category")
        if repository_url is not None and (not isinstance(repository_url, str) or not repository_url):
            raise ValueError(f"catalog entry #{index} has invalid repository_url")
        if not isinstance(versions, list) or not all(isinstance(version, str) for version in versions):
            raise ValueError(f"catalog entry #{index} has invalid versions")
        if notes is not None and not isinstance(notes, str):
            raise ValueError(f"catalog entry #{index} has invalid notes")

        entry = CatalogEntry(
            group=group,
            artifact=artifact,
            packaging=packaging,
            category=category,
            repository_url=repository_url,
            versions=tuple(versions),
            notes=notes,
        )
        if entry.coordinate in seen:
            raise ValueError(f"duplicate catalog coordinate: {entry.coordinate}")
        seen.add(entry.coordinate)
        parsed.append(entry)

    return parsed


def expand_reference_catalog(
    catalog_path: str | Path = DEFAULT_REFERENCE_CATALOG,
    *,
    output_path: str | Path | None = DEFAULT_EXPANDED_CONFIG,
    repository_url: str = DEFAULT_MAVEN_REPOSITORY_URL,
    latest_count: int = 1,
    include_prerelease: bool = False,
    coordinate: str | None = None,
    limit: int | None = None,
    timeout: int = 30,
    dry_run: bool = False,
    fetcher: MetadataFetcher | None = None,
) -> ReferenceExpansionSummary:
    if latest_count < 1:
        raise ValueError("latest_count must be at least 1")

    entries = _select_entries(
        load_reference_catalog(catalog_path),
        coordinate=coordinate,
        limit=limit,
    )
    fetch = fetcher or fetch_maven_metadata_text
    results = [
        expand_catalog_entry(
            entry,
            repository_url=repository_url,
            latest_count=latest_count,
            include_prerelease=include_prerelease,
            timeout=timeout,
            fetcher=fetch,
        )
        for entry in entries
    ]

    libraries = [
        MavenLibrary(
            group=result.entry.group,
            artifact=result.entry.artifact,
            versions=result.selected_versions,
            packaging=result.entry.packaging,
            repository_url=result.entry.repository_url,
        )
        for result in results
        if result.selected_versions
    ]
    output = Path(output_path) if output_path else None
    if output and not dry_run:
        write_libraries_config(libraries, output)

    return ReferenceExpansionSummary(
        catalog_path=str(catalog_path),
        output_path=str(output) if output else None,
        repository_url=repository_url,
        latest_count=latest_count,
        include_prerelease=include_prerelease,
        total_entries=len(entries),
        selected_libraries=len(libraries),
        failed=sum(1 for result in results if result.status == "failed"),
        results=results,
    )


def expand_catalog_entry(
    entry: CatalogEntry,
    *,
    repository_url: str = DEFAULT_MAVEN_REPOSITORY_URL,
    latest_count: int = 1,
    include_prerelease: bool = False,
    timeout: int = 30,
    fetcher: MetadataFetcher | None = None,
) -> ExpandedLibraryResult:
    effective_repository_url = entry.repository_url or repository_url
    metadata_url = maven_metadata_url(
        entry.group,
        entry.artifact,
        repository_url=effective_repository_url,
    )
    if entry.versions:
        return ExpandedLibraryResult(
            entry=entry,
            status="pinned",
            selected_versions=entry.versions,
            metadata_url=metadata_url,
            available_versions=entry.versions,
        )

    try:
        metadata_text = (fetcher or fetch_maven_metadata_text)(metadata_url, timeout)
        versions = parse_maven_metadata_versions(metadata_text)
        selected = select_versions(
            versions,
            latest_count=latest_count,
            include_prerelease=include_prerelease,
        )
    except (OSError, ValueError, ET.ParseError, urllib.error.URLError) as exc:
        return ExpandedLibraryResult(
            entry=entry,
            status="failed",
            selected_versions=(),
            metadata_url=metadata_url,
            error=str(exc),
        )

    return ExpandedLibraryResult(
        entry=entry,
        status="resolved" if selected else "failed",
        selected_versions=tuple(selected),
        metadata_url=metadata_url,
        available_versions=tuple(versions),
        error=None if selected else "no stable versions selected",
    )


def fetch_maven_metadata_text(url: str, timeout: int) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def maven_metadata_url(
    group: str,
    artifact: str,
    *,
    repository_url: str = DEFAULT_MAVEN_REPOSITORY_URL,
) -> str:
    repository = repository_url.rstrip("/")
    group_path = group.replace(".", "/")
    return f"{repository}/{group_path}/{artifact}/maven-metadata.xml"


def parse_maven_metadata_versions(metadata_text: str) -> list[str]:
    root = ET.fromstring(metadata_text)
    versions = [
        version.text.strip()
        for version in root.findall("./versioning/versions/version")
        if version.text and version.text.strip()
    ]
    if not versions:
        raise ValueError("maven metadata contains no versions")
    return versions


def select_versions(
    versions: list[str] | tuple[str, ...],
    *,
    latest_count: int = 1,
    include_prerelease: bool = False,
) -> list[str]:
    candidates = [
        version
        for version in versions
        if include_prerelease or is_stable_version(version)
    ]
    candidates = sorted(set(candidates), key=version_sort_key)
    return candidates[-latest_count:]


def is_stable_version(version: str) -> bool:
    if version.endswith("-SNAPSHOT"):
        return False
    return PRE_RELEASE_RE.search(version) is None


def version_sort_key(version: str) -> tuple[int, object]:
    try:
        return (1, Version(version))
    except InvalidVersion:
        parts = tuple(int(part) if part.isdigit() else part for part in re.split(r"([0-9]+)", version))
        return (0, parts)


def write_libraries_config(libraries: list[MavenLibrary], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "libraries": [
            _library_to_config_entry(library)
            for library in sorted(libraries, key=lambda item: item.coordinate)
        ]
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _select_entries(
    entries: list[CatalogEntry],
    *,
    coordinate: str | None = None,
    limit: int | None = None,
) -> list[CatalogEntry]:
    selected = [
        entry
        for entry in entries
        if coordinate is None or entry.coordinate == coordinate
    ]
    if limit is not None:
        return selected[:limit]
    return selected


def _library_to_config_entry(library: MavenLibrary) -> dict:
    payload = {
        "group": library.group,
        "artifact": library.artifact,
        "packaging": library.packaging or "jar",
        "versions": list(library.versions),
    }
    if library.repository_url:
        payload["repository_url"] = library.repository_url
    return payload
