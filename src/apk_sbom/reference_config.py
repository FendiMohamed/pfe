from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MavenLibrary:
    group: str
    artifact: str
    versions: tuple[str, ...]

    @property
    def coordinate(self) -> str:
        return f"{self.group}:{self.artifact}"

    def purl_for(self, version: str) -> str:
        return f"pkg:maven/{self.group}/{self.artifact}@{version}"


def load_libraries_config(path: str | Path) -> list[MavenLibrary]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    libraries = payload.get("libraries")
    if not isinstance(libraries, list):
        raise ValueError("libraries config must contain a 'libraries' list")

    parsed: list[MavenLibrary] = []
    for index, item in enumerate(libraries):
        if not isinstance(item, dict):
            raise ValueError(f"library entry #{index} must be an object")

        group = item.get("group")
        artifact = item.get("artifact")
        versions = item.get("versions")

        if not group or not isinstance(group, str):
            raise ValueError(f"library entry #{index} has invalid group")
        if not artifact or not isinstance(artifact, str):
            raise ValueError(f"library entry #{index} has invalid artifact")
        if not isinstance(versions, list) or not versions or not all(isinstance(v, str) for v in versions):
            raise ValueError(f"library entry #{index} has invalid versions")

        parsed.append(MavenLibrary(group=group, artifact=artifact, versions=tuple(versions)))

    return parsed

