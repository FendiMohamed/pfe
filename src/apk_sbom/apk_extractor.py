from __future__ import annotations

import hashlib
import json
import re
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEX_PATTERN = re.compile(r"^classes(?:\d*)\.dex$")
NATIVE_PATTERN = re.compile(r"^lib/([^/]+)/([^/]+\.so)$")


@dataclass(frozen=True)
class NativeLibrary:
    path: str
    abi: str
    filename: str
    size: int
    sha256: str


@dataclass(frozen=True)
class ApkInspection:
    apk_path: str
    apk_size: int
    apk_sha256: str
    dex_files: list[str]
    has_multidex: bool
    manifest_present: bool
    resources_arsc_present: bool
    native_libraries: list[NativeLibrary]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_zip_names(names: Iterable[str]) -> list[str]:
    return sorted(name.replace("\\", "/") for name in names)


def inspect_apk(apk_path: str | Path) -> ApkInspection:
    path = Path(apk_path)
    if not path.exists():
        raise FileNotFoundError(f"APK not found: {path}")
    if not path.is_file():
        raise ValueError(f"APK path is not a file: {path}")

    with zipfile.ZipFile(path) as apk_zip:
        names = normalized_zip_names(apk_zip.namelist())
        dex_files = [name for name in names if DEX_PATTERN.match(Path(name).name)]
        native_libraries: list[NativeLibrary] = []

        for name in names:
            match = NATIVE_PATTERN.match(name)
            if not match:
                continue
            info = apk_zip.getinfo(name)
            data = apk_zip.read(name)
            native_libraries.append(
                NativeLibrary(
                    path=name,
                    abi=match.group(1),
                    filename=match.group(2),
                    size=info.file_size,
                    sha256=sha256_bytes(data),
                )
            )

        return ApkInspection(
            apk_path=str(path),
            apk_size=path.stat().st_size,
            apk_sha256=sha256_file(path),
            dex_files=dex_files,
            has_multidex=len(dex_files) > 1,
            manifest_present="AndroidManifest.xml" in names,
            resources_arsc_present="resources.arsc" in names,
            native_libraries=native_libraries,
        )

