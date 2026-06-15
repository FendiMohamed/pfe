from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/external-scanner-validation.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/EXTERNAL_SCANNER_VALIDATION.md")

SBOM_TARGETS = [
    {
        "id": "clean-f-droid",
        "name": "Clean F-Droid real APK SBOM",
        "path": "data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json",
        "expected": "negative-or-low-noise",
    },
    {
        "id": "controlled-vulnerable-jackson",
        "name": "Controlled vulnerable Jackson SBOM",
        "path": "data/results/demo-osv-vulnerable-jackson-databind/sbom.cdx.json",
        "expected": "positive",
    },
    {
        "id": "osmand-source-aware-partial",
        "name": "OsmAnd source-aware partial SBOM",
        "path": "data/results/report-real-osmand/sbom.cdx.json",
        "expected": "partial-source-mismatch-review",
    },
]

SCANNERS = [
    {
        "id": "grype",
        "name": "Grype",
        "executable": "grype",
        "command": lambda path: ["grype", f"sbom:{path}", "-o", "json"],
        "parser": "grype",
    },
    {
        "id": "trivy",
        "name": "Trivy",
        "executable": "trivy",
        "command": lambda path: ["trivy", "sbom", "--quiet", "--format", "json", str(path)],
        "parser": "trivy",
    },
]

VALIDATORS = [
    {
        "id": "cyclonedx",
        "name": "CycloneDX CLI",
        "executable": "cyclonedx",
        "command": lambda path: [
            "cyclonedx",
            "validate",
            "--input-file",
            str(path),
            "--input-format",
            "json",
            "--input-version",
            "v1_5",
            "--fail-on-errors",
        ],
    },
    {
        "id": "cyclonedx-cli",
        "name": "CycloneDX CLI alias",
        "executable": "cyclonedx-cli",
        "command": lambda path: [
            "cyclonedx-cli",
            "validate",
            "--input-file",
            str(path),
            "--input-format",
            "json",
            "--input-version",
            "v1_5",
            "--fail-on-errors",
        ],
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run available external vulnerability scanners against selected CycloneDX SBOMs.",
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--timeout", type=int, default=300)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(timeout=args.timeout)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": output_doc.as_posix(),
                "json": output_json.as_posix(),
                "status": payload["summary"]["status"],
                "scanner_runs": payload["summary"]["scanner_runs"],
                "successful_runs": payload["summary"]["successful_runs"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if payload["summary"]["successful_runs"] else 1


def build_payload(timeout: int) -> dict[str, Any]:
    targets = [load_target(target) for target in SBOM_TARGETS]
    scanners = [load_scanner(scanner) for scanner in SCANNERS]
    validators = [load_validator(validator) for validator in VALIDATORS]
    runs = [
        run_scanner(scanner, target, timeout)
        for scanner in scanners
        for target in targets
        if scanner["available"] and target["exists"]
    ]
    validation_runs = [
        run_validator(validator, target, timeout)
        for validator in validators
        for target in targets
        if validator["available"] and target["exists"]
    ]
    successful_runs = [run for run in runs if run["status"] == "completed"]
    successful_validation_runs = [
        run for run in validation_runs if run["status"] == "completed"
    ]
    status = "completed" if successful_runs and successful_validation_runs else "blocked-or-failed"
    return {
        "schema_version": 1,
        "summary": {
            "status": status,
            "targets_checked": len(targets),
            "targets_available": sum(1 for target in targets if target["exists"]),
            "scanners_checked": len(scanners),
            "scanners_available": sum(1 for scanner in scanners if scanner["available"]),
            "validators_checked": len(validators),
            "validators_available": sum(1 for validator in validators if validator["available"]),
            "scanner_runs": len(runs),
            "successful_runs": len(successful_runs),
            "validation_runs": len(validation_runs),
            "successful_validation_runs": len(successful_validation_runs),
        },
        "targets": targets,
        "scanners": scanners,
        "validators": validators,
        "runs": runs,
        "validation_runs": validation_runs,
        "interpretation": build_interpretation(
            status,
            scanners,
            validators,
            targets,
            runs,
            validation_runs,
        ),
    }


def load_target(target: dict[str, str]) -> dict[str, Any]:
    path = Path(target["path"])
    metadata: dict[str, Any] = {}
    if path.exists():
        try:
            sbom = json.loads(path.read_text(encoding="utf-8"))
            metadata = {
                "bom_format": sbom.get("bomFormat"),
                "spec_version": sbom.get("specVersion"),
                "component_count": len(sbom.get("components", [])),
            }
        except Exception as exc:
            metadata = {"parse_error": str(exc)}
    return {
        **target,
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "metadata": metadata,
    }


def load_scanner(scanner: dict[str, Any]) -> dict[str, Any]:
    executable = shutil.which(scanner["executable"])
    version = None
    if executable:
        version = run_version([scanner["executable"], "--version"])
    return {
        "id": scanner["id"],
        "name": scanner["name"],
        "executable": executable,
        "available": bool(executable),
        "version": version,
    }


def load_validator(validator: dict[str, Any]) -> dict[str, Any]:
    executable = shutil.which(validator["executable"])
    version = None
    if executable:
        version = run_version([validator["executable"], "--version"])
    return {
        "id": validator["id"],
        "name": validator["name"],
        "executable": executable,
        "available": bool(executable),
        "version": version,
    }


def run_scanner(scanner: dict[str, Any], target: dict[str, Any], timeout: int) -> dict[str, Any]:
    scanner_def = next(item for item in SCANNERS if item["id"] == scanner["id"])
    command = scanner_def["command"](target["path"])
    base = {
        "scanner": scanner["id"],
        "target": target["id"],
        "target_path": target["path"],
        "command": command,
    }
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:
        return {
            **base,
            "status": "failed",
            "exit_code": None,
            "error": str(exc),
            "vulnerability_count": None,
            "sample": [],
        }
    parsed = parse_scanner_output(scanner_def["parser"], completed.stdout)
    return {
        **base,
        "status": "completed" if completed.returncode == 0 and parsed["parsed"] else "failed",
        "exit_code": completed.returncode,
        "stderr_tail": tail(completed.stderr),
        **parsed,
    }


def run_validator(validator: dict[str, Any], target: dict[str, Any], timeout: int) -> dict[str, Any]:
    validator_def = next(item for item in VALIDATORS if item["id"] == validator["id"])
    command = validator_def["command"](target["path"])
    base = {
        "validator": validator["id"],
        "target": target["id"],
        "target_path": target["path"],
        "command": command,
    }
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:
        return {
            **base,
            "status": "failed",
            "exit_code": None,
            "error": str(exc),
        }
    return {
        **base,
        "status": "completed" if completed.returncode == 0 else "failed",
        "exit_code": completed.returncode,
        "stdout_tail": tail(completed.stdout),
        "stderr_tail": tail(completed.stderr),
    }


def parse_scanner_output(parser: str, output: str) -> dict[str, Any]:
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        return {
            "parsed": False,
            "parse_error": str(exc),
            "vulnerability_count": None,
            "sample": [],
        }
    if parser == "grype":
        matches = payload.get("matches", [])
        return {
            "parsed": True,
            "vulnerability_count": len(matches),
            "sample": [
                {
                    "id": match.get("vulnerability", {}).get("id"),
                    "package": match.get("artifact", {}).get("name"),
                    "version": match.get("artifact", {}).get("version"),
                    "severity": match.get("vulnerability", {}).get("severity"),
                }
                for match in matches[:5]
            ],
        }
    if parser == "trivy":
        vulnerabilities = []
        for result in payload.get("Results", []):
            for vuln in result.get("Vulnerabilities", []) or []:
                vulnerabilities.append(
                    {
                        "id": vuln.get("VulnerabilityID"),
                        "package": vuln.get("PkgName"),
                        "version": vuln.get("InstalledVersion"),
                        "severity": vuln.get("Severity"),
                    }
                )
        return {
            "parsed": True,
            "vulnerability_count": len(vulnerabilities),
            "sample": vulnerabilities[:5],
        }
    return {
        "parsed": True,
        "vulnerability_count": None,
        "sample": [],
    }


def run_version(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception as exc:
        return f"error: {exc}"
    output = (completed.stdout or completed.stderr).strip()
    return output.splitlines()[0] if output else f"exit_code={completed.returncode}"


def build_interpretation(
    status: str,
    scanners: list[dict[str, Any]],
    validators: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    validation_runs: list[dict[str, Any]],
) -> list[str]:
    lines = []
    if status == "completed":
        lines.append("External scanner validation ran successfully for at least one scanner/target pair.")
    else:
        lines.append("External scanner validation did not produce a successful scanner result.")
    missing_scanners = [scanner["id"] for scanner in scanners if not scanner["available"]]
    missing_targets = [target["path"] for target in targets if not target["exists"]]
    failed_runs = [run for run in runs if run["status"] != "completed"]
    failed_validation_runs = [
        run for run in validation_runs if run["status"] != "completed"
    ]
    if missing_scanners:
        lines.append(f"Missing scanner executables: {', '.join(missing_scanners)}.")
    missing_validators = [validator["id"] for validator in validators if not validator["available"]]
    if missing_validators:
        lines.append(f"Missing validator executables: {', '.join(missing_validators)}.")
    if missing_targets:
        lines.append(f"Missing SBOM targets: {', '.join(missing_targets)}.")
    if failed_runs:
        lines.append(f"Failed scanner runs: {len(failed_runs)}.")
    if failed_validation_runs:
        lines.append(f"Failed CycloneDX validation runs: {len(failed_validation_runs)}.")
    if validation_runs and not failed_validation_runs:
        lines.append("All selected SBOM targets passed CycloneDX CLI schema validation.")
    lines.append(
        "Scanner findings are comparison evidence only; source-validation-aware OSV labels remain the thesis vulnerability authority for real APK claims."
    )
    return lines


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# External Scanner Validation",
        "",
        "Generated by `scripts/run_external_scanner_validation.py`.",
        "",
        "This file records optional external scanner results for selected CycloneDX SBOMs.",
        "",
        "## Summary",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Status | `{summary['status']}` |",
        f"| Scanners available | {summary['scanners_available']}/{summary['scanners_checked']} |",
        f"| CycloneDX validators available | {summary['validators_available']}/{summary['validators_checked']} |",
        f"| Targets available | {summary['targets_available']}/{summary['targets_checked']} |",
        f"| Scanner runs | {summary['scanner_runs']} |",
        f"| Successful runs | {summary['successful_runs']} |",
        f"| CycloneDX validation runs | {summary['validation_runs']} |",
        f"| Successful CycloneDX validation runs | {summary['successful_validation_runs']} |",
        "",
        "## Scanner Runs",
        "",
        "| Scanner | Target | Status | Vulnerabilities | Sample |",
        "|---|---|---|---:|---|",
    ]
    if payload["runs"]:
        for run in payload["runs"]:
            sample = ", ".join(
                f"{item.get('id')} ({item.get('package')} {item.get('version')})"
                for item in run.get("sample", [])
                if item.get("id")
            )
            lines.append(
                f"| `{run['scanner']}` | `{run['target']}` | `{run['status']}` | {md(run.get('vulnerability_count'))} | {md(sample or '-')} |"
            )
    else:
        lines.append("| - | - | `not-run` | - | - |")
    lines.extend(
        [
            "",
            "## CycloneDX Validation Runs",
            "",
            "| Validator | Target | Status | Detail |",
            "|---|---|---|---|",
        ]
    )
    if payload["validation_runs"]:
        for run in payload["validation_runs"]:
            detail = run.get("stdout_tail") or run.get("stderr_tail") or "-"
            lines.append(
                f"| `{run['validator']}` | `{run['target']}` | `{run['status']}` | {md(detail)} |"
            )
    else:
        lines.append("| - | - | `not-run` | - |")
    lines.extend(
        [
            "",
            "## Targets",
            "",
            "| Target | Expected role | CycloneDX | Components | Path |",
            "|---|---|---|---:|---|",
        ]
    )
    for target in payload["targets"]:
        metadata = target["metadata"]
        lines.append(
            f"| {md(target['name'])} | `{target['expected']}` | `{md(metadata.get('spec_version', '-'))}` | {metadata.get('component_count', '-')} | `{target['path']}` |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {line}" for line in payload["interpretation"])
    lines.append("")
    return "\n".join(lines)


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>")


def tail(value: str, max_chars: int = 600) -> str:
    value = value.strip()
    return value[-max_chars:] if len(value) > max_chars else value


if __name__ == "__main__":
    raise SystemExit(main())
