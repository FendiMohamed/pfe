from __future__ import annotations

import argparse
import json
import re
import tomllib
from collections import defaultdict
from pathlib import Path
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare emitted Maven components against a Gradle version catalog. "
            "This is weaker than resolved dependency-tree validation because catalogs "
            "can contain unused aliases and omit transitive dependency resolution."
        )
    )
    parser.add_argument("--report", required=True, help="Generated report.json file.")
    parser.add_argument("--catalog", required=True, help="Gradle libs.versions.toml file.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--name", default="version-catalog-validation")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report_path = Path(args.report)
    catalog_path = Path(args.catalog)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report = read_json(report_path)
    catalog = read_version_catalog(catalog_path)
    components = report_components(report)
    rows = [compare_component(component, catalog) for component in components]
    summary = summarize(rows)

    payload = {
        "name": args.name,
        "scope": "catalog-only",
        "warning": (
            "This is weaker than resolved Gradle dependency-tree validation. "
            "It compares emitted SBOM components to declared catalog aliases only; "
            "transitive resolution and variant selection are not proven."
        ),
        "report": str(report_path),
        "catalog": str(catalog_path),
        "summary": summary,
        "rows": rows,
    }

    json_path = output_dir / f"{args.name}.json"
    md_path = output_dir / f"{args.name}.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")

    print(json.dumps({"json": str(json_path), "markdown": str(md_path), **summary}, indent=2))
    return 0


def read_version_catalog(path: Path) -> dict[str, Any]:
    raw = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    versions = raw.get("versions", {})
    libraries = raw.get("libraries", {})
    by_coordinate: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_group: dict[str, list[dict[str, str]]] = defaultdict(list)

    for alias, value in libraries.items():
        if not isinstance(value, dict):
            continue
        module = value.get("module")
        if not isinstance(module, str) or ":" not in module:
            continue
        group, artifact = module.split(":", 1)
        version = resolve_catalog_version(value, versions)
        if not version:
            continue
        entry = {
            "alias": alias,
            "coordinate": module,
            "group": group,
            "artifact": artifact,
            "version": version,
        }
        by_coordinate[module].append(entry)
        by_group[group].append(entry)

    return {"by_coordinate": by_coordinate, "by_group": by_group}


def resolve_catalog_version(value: dict[str, Any], versions: dict[str, Any]) -> str | None:
    direct = value.get("version")
    if isinstance(direct, str):
        return direct
    if isinstance(direct, dict):
        ref = direct.get("ref")
        if isinstance(ref, str):
            resolved = versions.get(ref)
            return str(resolved) if resolved is not None else None
    ref = value.get("version.ref")
    if isinstance(ref, str):
        resolved = versions.get(ref)
        return str(resolved) if resolved is not None else None
    return None


def report_components(report: dict[str, Any]) -> list[dict[str, str]]:
    components = []
    for component in report.get("detected_components", []):
        group = component.get("group")
        artifact = component.get("artifact")
        version = component.get("version")
        if not group or not artifact or not version:
            continue
        components.append(
            {
                "coordinate": f"{group}:{artifact}",
                "group": str(group),
                "artifact": str(artifact),
                "version": str(version),
                "purl": str(component.get("purl", "")),
            }
        )
    return components


def compare_component(component: dict[str, str], catalog: dict[str, Any]) -> dict[str, Any]:
    coordinate = component["coordinate"]
    exact_entries = catalog["by_coordinate"].get(coordinate, [])
    if exact_entries:
        expected_versions = sorted({entry["version"] for entry in exact_entries})
        status = "confirmed" if component["version"] in expected_versions else "version-mismatch"
        return {
            **component,
            "status": status,
            "catalog_match_type": "exact-coordinate",
            "catalog_expected_versions": expected_versions,
            "catalog_aliases": sorted(entry["alias"] for entry in exact_entries),
            "note": "Exact coordinate appears in version catalog.",
        }

    family_entries = family_candidates(component, catalog)
    if family_entries:
        expected_versions = sorted({entry["version"] for entry in family_entries})
        status = "family-confirmed" if component["version"] in expected_versions else "family-version-mismatch"
        return {
            **component,
            "status": status,
            "catalog_match_type": "artifact-family",
            "catalog_expected_versions": expected_versions,
            "catalog_aliases": sorted(entry["alias"] for entry in family_entries),
            "catalog_coordinates": sorted(entry["coordinate"] for entry in family_entries),
            "note": "Catalog has a related artifact-family alias, but not the exact emitted coordinate.",
        }

    return {
        **component,
        "status": "not-in-catalog",
        "catalog_match_type": "none",
        "catalog_expected_versions": [],
        "catalog_aliases": [],
        "note": "Not directly declared in catalog; may be transitive or absent from catalog aliases.",
    }


def family_candidates(component: dict[str, str], catalog: dict[str, Any]) -> list[dict[str, str]]:
    group_entries = catalog["by_group"].get(component["group"], [])
    artifact_stem = artifact_stem_for_family(component["artifact"])
    result = []
    for entry in group_entries:
        if artifact_stem_for_family(entry["artifact"]) == artifact_stem:
            result.append(entry)
    return result


def artifact_stem_for_family(artifact: str) -> str:
    stem = artifact
    for suffix in ("-jvm", "-android", "-ktx", "-compose", "-testing"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    stem = re.sub(r"-(api|impl|common|runtime)$", "", stem)
    return stem


def summarize(rows: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "emitted_components": len(rows),
        "confirmed": 0,
        "version_mismatches": 0,
        "family_confirmed": 0,
        "family_version_mismatches": 0,
        "not_in_catalog": 0,
    }
    for row in rows:
        status = row["status"]
        if status == "confirmed":
            summary["confirmed"] += 1
        elif status == "version-mismatch":
            summary["version_mismatches"] += 1
        elif status == "family-confirmed":
            summary["family_confirmed"] += 1
        elif status == "family-version-mismatch":
            summary["family_version_mismatches"] += 1
        elif status == "not-in-catalog":
            summary["not_in_catalog"] += 1
    return summary


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"# {payload['name'].replace('-', ' ').title()}",
        "",
        payload["warning"],
        "",
        "## Summary",
        "",
        f"- Emitted Maven components checked: {summary['emitted_components']}",
        f"- Exact catalog confirmations: {summary['confirmed']}",
        f"- Exact catalog version mismatches: {summary['version_mismatches']}",
        f"- Artifact-family confirmations: {summary['family_confirmed']}",
        f"- Artifact-family version mismatches: {summary['family_version_mismatches']}",
        f"- Not declared in catalog: {summary['not_in_catalog']}",
        "",
        "## Components",
        "",
        "| Component | Emitted version | Status | Catalog expected | Catalog aliases | Note |",
        "|---|---:|---|---|---|---|",
    ]
    for row in payload["rows"]:
        expected = ", ".join(f"`{version}`" for version in row["catalog_expected_versions"]) or "n/a"
        aliases = ", ".join(f"`{alias}`" for alias in row["catalog_aliases"]) or "n/a"
        lines.append(
            "| "
            f"`{row['coordinate']}` | "
            f"`{row['version']}` | "
            f"{row['status']} | "
            f"{expected} | "
            f"{aliases} | "
            f"{row['note']} |"
        )
    lines.append("")
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


if __name__ == "__main__":
    raise SystemExit(main())
