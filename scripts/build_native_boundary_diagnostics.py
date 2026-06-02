from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_APK_TYPE_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/native-boundary-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/NATIVE_BOUNDARY_DIAGNOSTICS.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize native .so boundary evidence for the MVP scope.",
    )
    parser.add_argument("--apk-type-json", default=str(DEFAULT_APK_TYPE_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    apk_type_path = Path(args.apk_type_json)
    payload = build_payload(read_json(apk_type_path), apk_type_path=apk_type_path)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "native_cases": len(payload["native_cases"]),
                "total_native_files": payload["summary"]["total_native_files"],
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(apk_type: dict[str, Any], *, apk_type_path: Path) -> dict[str, Any]:
    native_cases = []
    for case in apk_type.get("real_cases", []):
        native_count = int(case.get("native_files") or 0)
        if native_count <= 0:
            continue
        native_cases.append(build_case_row(case))

    role_counts: dict[str, int] = {}
    for row in native_cases:
        role_counts[row["role"]] = role_counts.get(row["role"], 0) + 1

    source_validated_native_cases = [
        row for row in native_cases if row["role"] in {"clean-source-validated", "source-validated-partial"}
    ]
    boundary_cases = [
        row for row in native_cases if row["role"].startswith("limitation") or row["role"].endswith("blocked")
    ]
    return {
        "schema_version": 1,
        "sources": {
            "apk_type": normalize_path(apk_type_path),
        },
        "policy": [
            "Native .so files are emitted as CycloneDX file components with path, ABI, size, and SHA-256 evidence.",
            "Native package and native version identification are outside the Maven/DEX matcher scope.",
            "Native file counts are excluded from Maven version confirmation metrics.",
            "Native-heavy APKs remain useful stress or limitation evidence, not Maven-version failures.",
        ],
        "summary": {
            "native_case_count": len(native_cases),
            "source_validated_native_case_count": len(source_validated_native_cases),
            "boundary_or_blocked_native_case_count": len(boundary_cases),
            "total_native_files": sum(row["native_files"] for row in native_cases),
            "role_counts": role_counts,
        },
        "native_cases": native_cases,
        "verdict": "native-boundary-complete",
        "conclusion": (
            "Complete for the current MVP: native handling is correctly documented as hash-only file-component "
            "reporting. The evidence spans source-validated native APKs and explicit native-heavy boundary cases, "
            "so no native package/version recovery claim should be added."
        ),
    }


def build_case_row(case: dict[str, Any]) -> dict[str, Any]:
    report = read_json(Path(str(case.get("report_path") or "")))
    native_libraries = report.get("apk", {}).get("native_libraries", [])
    if not native_libraries:
        native_libraries = report.get("native_libraries", [])
    filenames = sorted({str(item.get("filename")) for item in native_libraries if item.get("filename")})
    abis = sorted({str(item.get("abi")) for item in native_libraries if item.get("abi")})
    return {
        "case_id": case.get("case_id"),
        "name": case.get("name"),
        "role": case.get("role"),
        "tags": case.get("tags", []),
        "maven_components": int(case.get("maven_components") or 0),
        "native_files": int(case.get("native_files") or 0),
        "dex_count": int(case.get("dex_count") or 0),
        "validation_summary": case.get("validation_summary") or "not source-validated",
        "native_abis": abis,
        "native_filenames": filenames,
        "proof_path": normalize_path(case.get("proof_path")),
        "report_path": normalize_path(case.get("report_path")),
        "interpretation": case.get("interpretation"),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Native Boundary Diagnostics",
        "",
        "Generated by `scripts/build_native_boundary_diagnostics.py`.",
        "",
        "This diagnostic checks whether native `.so` handling is properly scoped as hash-only SBOM file evidence, not native package/version recovery.",
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Native APK cases: {summary['native_case_count']}",
            f"- Source-validated native APK cases: {summary['source_validated_native_case_count']}",
            f"- Boundary or blocked native APK cases: {summary['boundary_or_blocked_native_case_count']}",
            f"- Native `.so` files represented as hash-only file components: {summary['total_native_files']}",
            f"- Verdict: `{payload['verdict']}`",
            f"- Conclusion: {payload['conclusion']}",
            "",
            "## Native Cases",
            "",
            "| Case | Role | Maven components | Native files | ABIs | Native filenames | Validation |",
            "|---|---|---:|---:|---|---|---|",
        ]
    )
    for row in payload["native_cases"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["name"] or row["case_id"]),
                    f"`{row['role']}`",
                    str(row["maven_components"]),
                    str(row["native_files"]),
                    md(", ".join(row["native_abis"]) or "n/a"),
                    md(", ".join(row["native_filenames"][:6]) + (" ..." if len(row["native_filenames"]) > 6 else "")),
                    md(row["validation_summary"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Mark the native con complete for the current Maven/DEX MVP.",
            "- Keep native `.so` entries as CycloneDX file components with hashes and ABI metadata.",
            "- Do not count native file components in Maven version confirmation rates.",
            "- Do not claim native package/version identification without a separate native-analysis module.",
            "",
        ]
    )
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
