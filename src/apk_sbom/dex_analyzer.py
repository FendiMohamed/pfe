from __future__ import annotations

import json
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from apk_sbom.apk_extractor import DEX_PATTERN, normalized_zip_names


@dataclass(frozen=True)
class DexParseError:
    dex_file: str
    error: str


@dataclass(frozen=True)
class DexFileFeatures:
    dex_file: str
    classes_count: int
    methods_count: int
    packages: list[str]
    opcode_histogram: dict[str, int]


@dataclass(frozen=True)
class ApkDexAnalysis:
    apk_path: str
    dex_files_analyzed: int
    dex_files_failed: int
    classes_count: int
    methods_count: int
    packages: list[str]
    opcode_histogram: dict[str, int]
    dex_files: list[DexFileFeatures]
    parse_errors: list[DexParseError]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def class_descriptor_to_package(descriptor: str) -> str | None:
    if not descriptor.startswith("L") or "/" not in descriptor:
        return None

    package_path = descriptor[1:].rsplit("/", maxsplit=1)[0]
    if not package_path:
        return None

    return package_path.replace("/", ".")


def analyze_dex_bytes(dex_file: str, data: bytes) -> DexFileFeatures:
    from androguard.core.dex import DEX

    dex = DEX(data)
    packages: set[str] = set()
    opcode_counter: Counter[str] = Counter()
    classes_count = 0
    methods_count = 0

    for dex_class in dex.get_classes():
        classes_count += 1
        package_name = class_descriptor_to_package(dex_class.get_name())
        if package_name:
            packages.add(package_name)

        class_methods = list(dex_class.get_methods())
        methods_count += len(class_methods)

        for method in class_methods:
            try:
                instructions = method.get_instructions()
            except Exception:
                continue

            for instruction in instructions:
                opcode_counter[instruction.get_name()] += 1

    return DexFileFeatures(
        dex_file=dex_file,
        classes_count=classes_count,
        methods_count=methods_count,
        packages=sorted(packages),
        opcode_histogram=dict(sorted(opcode_counter.items())),
    )


def analyze_apk_dex(apk_path: str | Path) -> ApkDexAnalysis:
    path = Path(apk_path)
    if not path.exists():
        raise FileNotFoundError(f"APK not found: {path}")
    if not path.is_file():
        raise ValueError(f"APK path is not a file: {path}")

    dex_features: list[DexFileFeatures] = []
    parse_errors: list[DexParseError] = []
    package_names: set[str] = set()
    opcode_counter: Counter[str] = Counter()

    with zipfile.ZipFile(path) as apk_zip:
        names = normalized_zip_names(apk_zip.namelist())
        dex_files = [name for name in names if DEX_PATTERN.match(Path(name).name)]

        for dex_file in dex_files:
            try:
                features = analyze_dex_bytes(dex_file, apk_zip.read(dex_file))
            except Exception as exc:
                parse_errors.append(DexParseError(dex_file=dex_file, error=str(exc)))
                continue

            dex_features.append(features)
            package_names.update(features.packages)
            opcode_counter.update(features.opcode_histogram)

    return ApkDexAnalysis(
        apk_path=str(path),
        dex_files_analyzed=len(dex_features),
        dex_files_failed=len(parse_errors),
        classes_count=sum(features.classes_count for features in dex_features),
        methods_count=sum(features.methods_count for features in dex_features),
        packages=sorted(package_names),
        opcode_histogram=dict(sorted(opcode_counter.items())),
        dex_files=dex_features,
        parse_errors=parse_errors,
    )
