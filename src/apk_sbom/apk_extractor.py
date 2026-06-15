from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


DEX_PATTERN = re.compile(r"^classes(?:\d*)\.dex$")
NATIVE_PATTERN = re.compile(r"^lib/([^/]+)/([^/]+\.so)$")
DEX_LIKE_PATTERN = re.compile(r"(?:^|/)classes(?:\d*)\.dex$|\.dex$", re.IGNORECASE)
ANDROID_XML_NAMESPACE = "{http://schemas.android.com/apk/res/android}"
PROTECTOR_HINTS = (
    "bangcle",
    "dexguard",
    "ijiami",
    "jiagu",
    "legu",
    "protect",
    "qihoo",
    "secneo",
    "shell",
)


@dataclass(frozen=True)
class NativeLibrary:
    path: str
    abi: str
    filename: str
    size: int
    sha256: str


@dataclass(frozen=True)
class ManifestMetadata:
    package_name: str | None = None
    version_code: str | None = None
    version_name: str | None = None
    min_sdk: str | None = None
    target_sdk: str | None = None
    permissions: list[str] = field(default_factory=list)
    parse_status: str = "not-present"
    parse_error: str | None = None


@dataclass(frozen=True)
class ApkIndicator:
    severity: str
    code: str
    detail: str


@dataclass(frozen=True)
class ApkForensicSummary:
    zip_entries: int = 0
    standard_dex_files: list[str] = field(default_factory=list)
    nonstandard_dex_files: list[str] = field(default_factory=list)
    resource_entry_count: int = 0
    asset_entry_count: int = 0
    native_library_count: int = 0
    native_abis: list[str] = field(default_factory=list)
    extraction_risk: str = "low"
    indicators: list[ApkIndicator] = field(default_factory=list)


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
    manifest_metadata: ManifestMetadata = field(default_factory=ManifestMetadata)
    forensic_summary: ApkForensicSummary = field(default_factory=ApkForensicSummary)

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
        info_by_name = {
            info.filename.replace("\\", "/"): info
            for info in apk_zip.infolist()
        }
        names = sorted(info_by_name)
        standard_dex_files = [name for name in names if DEX_PATTERN.match(name)]
        nonstandard_dex_files = [
            name
            for name in names
            if name not in standard_dex_files and DEX_LIKE_PATTERN.search(name)
        ]
        dex_files = standard_dex_files + nonstandard_dex_files
        native_libraries: list[NativeLibrary] = []

        for name in names:
            match = NATIVE_PATTERN.match(name)
            if not match:
                continue
            info = info_by_name[name]
            data = apk_zip.read(info)
            native_libraries.append(
                NativeLibrary(
                    path=name,
                    abi=match.group(1),
                    filename=match.group(2),
                    size=info.file_size,
                    sha256=sha256_bytes(data),
                )
            )

        manifest_info = info_by_name.get("AndroidManifest.xml")
        manifest_metadata = parse_manifest_metadata(
            apk_zip.read(manifest_info) if manifest_info else None
        )
        forensic_summary = build_forensic_summary(
            names,
            info_by_name,
            standard_dex_files=standard_dex_files,
            nonstandard_dex_files=nonstandard_dex_files,
            native_libraries=native_libraries,
        )

        return ApkInspection(
            apk_path=str(path),
            apk_size=path.stat().st_size,
            apk_sha256=sha256_file(path),
            dex_files=dex_files,
            has_multidex=len(standard_dex_files) > 1,
            manifest_present="AndroidManifest.xml" in names,
            resources_arsc_present="resources.arsc" in names,
            native_libraries=native_libraries,
            manifest_metadata=manifest_metadata,
            forensic_summary=forensic_summary,
        )


def parse_manifest_metadata(data: bytes | None) -> ManifestMetadata:
    if data is None:
        return ManifestMetadata()

    try:
        manifest_xml = decode_manifest_xml(data)
        root = ET.fromstring(manifest_xml)
    except Exception as exc:
        return ManifestMetadata(parse_status="failed", parse_error=str(exc))

    uses_sdk = root.find("uses-sdk")
    permissions = sorted(
        {
            value
            for element in root.findall("uses-permission")
            + root.findall("uses-permission-sdk-23")
            if (value := _android_attribute(element, "name"))
        }
    )
    return ManifestMetadata(
        package_name=root.attrib.get("package"),
        version_code=_android_attribute(root, "versionCode"),
        version_name=_android_attribute(root, "versionName"),
        min_sdk=_android_attribute(uses_sdk, "minSdkVersion") if uses_sdk is not None else None,
        target_sdk=_android_attribute(uses_sdk, "targetSdkVersion") if uses_sdk is not None else None,
        permissions=permissions,
        parse_status="parsed",
    )


def decode_manifest_xml(data: bytes) -> str:
    if data.lstrip().startswith(b"<"):
        return data.decode("utf-8", errors="replace")

    silence_androguard_logging()
    import_errors: list[str] = []
    for import_path in (
        "androguard.core.axml",
        "androguard.core.bytecodes.axml",
    ):
        try:
            module_name, class_name = import_path, "AXMLPrinter"
            module = __import__(module_name, fromlist=[class_name])
            printer_class = getattr(module, class_name)
        except Exception as exc:
            import_errors.append(f"{import_path}: {exc}")
            continue

        try:
            printer = printer_class(data)
            xml_object = _safe_call(printer, "get_xml_obj")
            if xml_object is not None:
                root = xml_object.getroot() if hasattr(xml_object, "getroot") else xml_object
                return ET.tostring(root, encoding="unicode")
            buffer = _safe_call(printer, "get_buff")
            if isinstance(buffer, bytes):
                return buffer.decode("utf-8", errors="replace")
            if buffer is not None:
                return str(buffer)
        except Exception as exc:
            import_errors.append(f"{import_path}: {exc}")

    detail = "; ".join(import_errors) if import_errors else "no decoder attempted"
    raise ValueError(f"binary AndroidManifest.xml could not be decoded ({detail})")


def build_forensic_summary(
    names: list[str],
    info_by_name: dict[str, zipfile.ZipInfo],
    *,
    standard_dex_files: list[str],
    nonstandard_dex_files: list[str],
    native_libraries: list[NativeLibrary],
) -> ApkForensicSummary:
    indicators = apk_indicators(
        names,
        info_by_name,
        standard_dex_files=standard_dex_files,
        nonstandard_dex_files=nonstandard_dex_files,
        native_libraries=native_libraries,
    )
    return ApkForensicSummary(
        zip_entries=len(names),
        standard_dex_files=standard_dex_files,
        nonstandard_dex_files=nonstandard_dex_files,
        resource_entry_count=sum(1 for name in names if name.startswith("res/")),
        asset_entry_count=sum(1 for name in names if name.startswith("assets/")),
        native_library_count=len(native_libraries),
        native_abis=sorted({library.abi for library in native_libraries}),
        extraction_risk=_extraction_risk(indicators),
        indicators=indicators,
    )


def apk_indicators(
    names: list[str],
    info_by_name: dict[str, zipfile.ZipInfo],
    *,
    standard_dex_files: list[str],
    nonstandard_dex_files: list[str],
    native_libraries: list[NativeLibrary],
) -> list[ApkIndicator]:
    indicators: list[ApkIndicator] = []
    if nonstandard_dex_files:
        indicators.append(
            ApkIndicator(
                severity="warning",
                code="nonstandard-dex",
                detail=(
                    "DEX-like files were found outside the normal top-level classes*.dex "
                    f"layout: {', '.join(nonstandard_dex_files[:5])}"
                ),
            )
        )

    total_payload_size = sum(info.file_size for info in info_by_name.values())
    if (
        "classes.dex" in info_by_name
        and info_by_name["classes.dex"].file_size < 4096
        and total_payload_size >= 128 * 1024
    ):
        severity = "warning" if native_libraries or nonstandard_dex_files else "info"
        indicators.append(
            ApkIndicator(
                severity=severity,
                code="tiny-primary-dex",
                detail=(
                    "Primary classes.dex is very small; this can be normal for tiny APKs, "
                    "but may also indicate loader-style packaging when combined with native "
                    "libraries or hidden payloads."
                ),
            )
        )

    protector_matches = [
        name
        for name in names
        if any(hint in name.lower() for hint in PROTECTOR_HINTS)
    ]
    if protector_matches:
        indicators.append(
            ApkIndicator(
                severity="warning",
                code="protector-name-hint",
                detail=(
                    "File names contain packer/protector-like terms: "
                    f"{', '.join(protector_matches[:5])}"
                ),
            )
        )

    opaque_assets = [
        name
        for name in names
        if name.startswith("assets/")
        and Path(name).suffix.lower() in {".bin", ".dat", ".enc", ".pak"}
        and info_by_name[name].file_size >= 1024 * 1024
    ]
    if opaque_assets:
        indicators.append(
            ApkIndicator(
                severity="info",
                code="large-opaque-assets",
                detail=f"Large opaque asset files found: {', '.join(opaque_assets[:5])}",
            )
        )

    if len(native_libraries) >= 10:
        indicators.append(
            ApkIndicator(
                severity="info",
                code="native-heavy",
                detail=f"APK contains {len(native_libraries)} native libraries.",
            )
        )
    return indicators


def _android_attribute(element: ET.Element | None, name: str) -> str | None:
    if element is None:
        return None
    return (
        element.attrib.get(f"{ANDROID_XML_NAMESPACE}{name}")
        or element.attrib.get(f"android:{name}")
        or element.attrib.get(name)
    )


def _extraction_risk(indicators: list[ApkIndicator]) -> str:
    severities = {indicator.severity for indicator in indicators}
    if "high" in severities:
        return "high"
    if "warning" in severities:
        return "medium"
    return "low"


def _safe_call(target: object, method_name: str) -> object | None:
    method = getattr(target, method_name, None)
    if method is None:
        return None
    try:
        return method()
    except Exception:
        return None


def silence_androguard_logging() -> None:
    try:
        from loguru import logger
    except Exception:
        return
    logger.disable("androguard")
