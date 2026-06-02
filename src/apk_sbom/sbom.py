from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from apk_sbom.apk_extractor import ApkInspection, NativeLibrary
from apk_sbom.models import ComponentEvidence, DetectedLibrary


TOOL_NAME = "apk-sbom-mvp"
TOOL_VERSION = "0.1.0"
CYCLONEDX_SPEC_VERSION = "1.5"


@dataclass(frozen=True)
class CycloneDxBom:
    payload: dict

    def to_dict(self) -> dict:
        return self.payload

    def to_json(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True)

    def write_json(self, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json() + "\n", encoding="utf-8")
        return path


def make_mock_detection() -> DetectedLibrary:
    return DetectedLibrary(
        group="com.google.code.gson",
        artifact="gson",
        version="2.8.9",
        confidence=0.85,
        match_type="mock",
        evidence=[
            ComponentEvidence(
                source="mock",
                detail="Temporary mocked detection used to validate CycloneDX output before matcher integration.",
                weight=1.0,
            )
        ],
    )


def build_cyclonedx_bom(
    apk: ApkInspection,
    components: list[DetectedLibrary],
    *,
    timestamp: datetime | None = None,
    serial_number: str | None = None,
    metadata_properties: list[dict[str, str]] | None = None,
) -> CycloneDxBom:
    created_at = timestamp or datetime.now(UTC)
    serial = serial_number or f"urn:uuid:{uuid4()}"

    apk_ref = f"apk:{Path(apk.apk_path).name}"
    library_components = [_component_to_cyclonedx(component) for component in components]
    native_components = [_native_library_to_cyclonedx(library) for library in apk.native_libraries]
    component_refs = [component.bom_ref for component in components] + [
        _native_library_bom_ref(library) for library in apk.native_libraries
    ]

    application_properties = [
        {
            "name": "apk-sbom:mvp:dex-files",
            "value": str(len(apk.dex_files)),
        },
        {
            "name": "apk-sbom:mvp:has-multidex",
            "value": str(apk.has_multidex).lower(),
        },
        {
            "name": "apk-sbom:mvp:native-libraries",
            "value": str(len(apk.native_libraries)),
        },
        {
            "name": "apk-sbom:mvp:manifest-package",
            "value": apk.manifest_metadata.package_name or "",
        },
        {
            "name": "apk-sbom:mvp:manifest-version-code",
            "value": apk.manifest_metadata.version_code or "",
        },
        {
            "name": "apk-sbom:mvp:manifest-version-name",
            "value": apk.manifest_metadata.version_name or "",
        },
        {
            "name": "apk-sbom:mvp:min-sdk",
            "value": apk.manifest_metadata.min_sdk or "",
        },
        {
            "name": "apk-sbom:mvp:target-sdk",
            "value": apk.manifest_metadata.target_sdk or "",
        },
        {
            "name": "apk-sbom:mvp:nonstandard-dex-files",
            "value": str(len(apk.forensic_summary.nonstandard_dex_files)),
        },
        {
            "name": "apk-sbom:mvp:extraction-risk",
            "value": apk.forensic_summary.extraction_risk,
        },
    ]
    if metadata_properties:
        application_properties.extend(metadata_properties)

    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": CYCLONEDX_SPEC_VERSION,
        "serialNumber": serial,
        "version": 1,
        "metadata": {
            "timestamp": created_at.isoformat().replace("+00:00", "Z"),
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": TOOL_NAME,
                        "version": TOOL_VERSION,
                    }
                ]
            },
            "component": {
                "type": "application",
                "name": Path(apk.apk_path).name,
                "bom-ref": apk_ref,
                "hashes": [
                    {
                        "alg": "SHA-256",
                        "content": apk.apk_sha256,
                    }
                ],
                "properties": application_properties,
            },
        },
        "components": library_components + native_components,
        "dependencies": [
            {
                "ref": apk_ref,
                "dependsOn": component_refs,
            }
        ],
    }

    return CycloneDxBom(payload)


def _component_to_cyclonedx(component: DetectedLibrary) -> dict:
    properties = [
        {
            "name": "apk-sbom:mvp:confidence",
            "value": f"{component.confidence:.3f}",
        },
        {
            "name": "apk-sbom:mvp:identity-confidence",
            "value": f"{component.identity_confidence:.3f}",
        },
        {
            "name": "apk-sbom:mvp:identity-confidence-label",
            "value": str(component.identity_confidence_label),
        },
        {
            "name": "apk-sbom:mvp:identity-status",
            "value": str(component.identity_status),
        },
        {
            "name": "apk-sbom:mvp:version-confidence",
            "value": f"{component.version_confidence:.3f}",
        },
        {
            "name": "apk-sbom:mvp:version-confidence-label",
            "value": str(component.version_confidence_label),
        },
        {
            "name": "apk-sbom:mvp:version-status",
            "value": str(component.version_status),
        },
        {
            "name": "apk-sbom:mvp:match-type",
            "value": component.match_type,
        },
        {
            "name": "apk-sbom:mvp:evidence",
            "value": _evidence_to_json(component.evidence),
        },
    ]
    if component.ambiguous_versions:
        properties.append(
            {
                "name": "apk-sbom:mvp:ambiguous-versions",
                "value": json.dumps(component.ambiguous_versions, sort_keys=True),
            }
        )

    return {
        "type": "library",
        "group": component.group,
        "name": component.artifact,
        "version": component.version,
        "purl": component.purl,
        "bom-ref": component.bom_ref,
        "properties": properties,
    }


def _native_library_to_cyclonedx(library: NativeLibrary) -> dict:
    return {
        "type": "file",
        "name": library.filename,
        "bom-ref": _native_library_bom_ref(library),
        "hashes": [
            {
                "alg": "SHA-256",
                "content": library.sha256,
            }
        ],
        "properties": [
            {
                "name": "apk-sbom:mvp:native-path",
                "value": library.path,
            },
            {
                "name": "apk-sbom:mvp:native-abi",
                "value": library.abi,
            },
            {
                "name": "apk-sbom:mvp:native-size",
                "value": str(library.size),
            },
            {
                "name": "apk-sbom:mvp:native-identification",
                "value": "hash-only",
            },
        ],
    }


def _native_library_bom_ref(library: NativeLibrary) -> str:
    return f"apk-native:{library.path}"


def _evidence_to_json(evidence: list[ComponentEvidence]) -> str:
    return json.dumps(
        [
            {
                "source": item.source,
                "detail": item.detail,
                "weight": item.weight,
            }
            for item in evidence
        ],
        sort_keys=True,
    )
