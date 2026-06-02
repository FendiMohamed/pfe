from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/external-scanner-validation-status.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/EXTERNAL_SCANNER_VALIDATION_STATUS.md")

SCANNER_TOOLS = [
    {
        "name": "cyclonedx",
        "command": ["cyclonedx", "--version"],
        "purpose": "CycloneDX SBOM validation",
    },
    {
        "name": "cyclonedx-cli",
        "command": ["cyclonedx-cli", "--version"],
        "purpose": "CycloneDX SBOM validation",
    },
    {
        "name": "trivy",
        "command": ["trivy", "--version"],
        "purpose": "SBOM vulnerability scanning",
    },
    {
        "name": "grype",
        "command": ["grype", "version"],
        "purpose": "SBOM vulnerability scanning",
    },
    {
        "name": "syft",
        "command": ["syft", "version"],
        "purpose": "SBOM generation/comparison",
    },
    {
        "name": "cdxgen",
        "command": ["cdxgen", "--version"],
        "purpose": "SBOM generation/comparison",
    },
]

SUPPORT_TOOLS = [
    {
        "name": "node",
        "command": ["node", "--version"],
        "purpose": "Required for npm-installed cdxgen/cyclonedx tooling",
    },
    {
        "name": "npm",
        "command": ["npm", "--version"],
        "purpose": "Installation/runtime route for npm scanner tools",
    },
    {
        "name": "dotnet",
        "command": ["dotnet", "--version"],
        "purpose": "Installation/runtime route for .NET CycloneDX CLI variants",
    },
]

SBOM_TARGETS = [
    {
        "name": "Clean F-Droid real APK SBOM",
        "path": "data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json",
        "role": "negative scanner check",
    },
    {
        "name": "Controlled vulnerable Jackson SBOM",
        "path": "data/results/demo-osv-vulnerable-jackson-databind/sbom.cdx.json",
        "role": "positive scanner check",
    },
    {
        "name": "OsmAnd source-aware partial SBOM",
        "path": "data/results/report-real-osmand/sbom.cdx.json",
        "role": "partial/source-mismatch scanner check",
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate external SBOM scanner availability and validation-blocker evidence.",
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument(
        "--environment",
        default="current-runtime",
        help="Human-readable environment label, for example docker-apk-sbom or windows-host.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(args.environment)

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
                "environment": payload["environment"],
                "scanner_tools_available": payload["summary"]["scanner_tools_available"],
                "status": payload["summary"]["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(environment: str) -> dict[str, Any]:
    scanners = [check_tool(tool) for tool in SCANNER_TOOLS]
    support = [check_tool(tool) for tool in SUPPORT_TOOLS]
    targets = [check_target(target) for target in SBOM_TARGETS]
    available_scanners = [tool for tool in scanners if tool["available"]]
    runnable_targets = [target for target in targets if target["exists"]]
    status = "scanner-ready" if available_scanners else "blocked-missing-scanners"
    return {
        "schema_version": 1,
        "environment": environment,
        "summary": {
            "status": status,
            "scanner_tools_checked": len(scanners),
            "scanner_tools_available": len(available_scanners),
            "support_tools_checked": len(support),
            "sbom_targets_checked": len(targets),
            "sbom_targets_available": len(runnable_targets),
        },
        "scanner_tools": scanners,
        "support_tools": support,
        "sbom_targets": targets,
        "interpretation": build_interpretation(status, scanners, support, targets),
    }


def check_tool(tool: dict[str, Any]) -> dict[str, Any]:
    command = [str(part) for part in tool["command"]]
    executable = shutil.which(command[0])
    if not executable:
        return {
            "name": tool["name"],
            "purpose": tool["purpose"],
            "available": False,
            "executable": None,
            "version": None,
            "detail": "missing from PATH",
        }
    return {
        "name": tool["name"],
        "purpose": tool["purpose"],
        "available": True,
        "executable": executable,
        "version": run_version(command),
        "detail": "available",
    }


def run_version(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as exc:
        return f"error: {exc}"
    output = strip_ansi((completed.stdout or completed.stderr).strip())
    return output.splitlines()[0] if output else f"exit_code={completed.returncode}"


def check_target(target: dict[str, str]) -> dict[str, Any]:
    path = Path(target["path"])
    return {
        "name": target["name"],
        "path": normalize_path(path),
        "role": target["role"],
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def build_interpretation(
    status: str,
    scanners: list[dict[str, Any]],
    support: list[dict[str, Any]],
    targets: list[dict[str, Any]],
) -> list[str]:
    missing_scanners = [tool["name"] for tool in scanners if not tool["available"]]
    missing_support = [tool["name"] for tool in support if not tool["available"]]
    missing_targets = [target["path"] for target in targets if not target["exists"]]
    lines = []
    if status == "blocked-missing-scanners":
        lines.append(
            "External scanner validation is blocked in this runtime because no scanner CLI is available."
        )
    elif not missing_scanners:
        lines.append(
            "All configured external scanner and validator CLIs are available in this runtime."
        )
    else:
        lines.append(
            "At least one external scanner CLI is available; scanner comparison can run in this runtime."
        )
    if missing_scanners:
        lines.append(f"Missing scanner tools: {', '.join(missing_scanners)}.")
    if missing_support:
        lines.append(f"Missing support runtimes: {', '.join(missing_support)}.")
    if missing_targets:
        lines.append(f"Missing SBOM target artifacts: {', '.join(missing_targets)}.")
    else:
        lines.append("All selected SBOM target artifacts exist for scanner runs.")
    if status == "blocked-missing-scanners":
        lines.append(
            "This artifact is blocker evidence, not external scanner validation evidence."
        )
    else:
        lines.append(
            "This artifact is readiness evidence; see `docs/evaluation/EXTERNAL_SCANNER_VALIDATION.md` for scanner-run results."
        )
    return lines


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# External Scanner Validation Status",
        "",
        "Generated by `scripts/build_external_scanner_validation_status.py`.",
        "",
        "This file records whether optional external SBOM/scanner validation can run in the checked runtime. It is intentionally separate from the MVP's built-in OSV workflow.",
        "",
        "## Summary",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Environment | {md(payload['environment'])} |",
        f"| Status | `{summary['status']}` |",
        f"| Scanner tools available | {summary['scanner_tools_available']}/{summary['scanner_tools_checked']} |",
        f"| Support tools checked | {summary['support_tools_checked']} |",
        f"| SBOM targets available | {summary['sbom_targets_available']}/{summary['sbom_targets_checked']} |",
        "",
        "## Scanner Tools",
        "",
        "| Tool | Purpose | Status | Detail |",
        "|---|---|---|---|",
    ]
    for tool in payload["scanner_tools"]:
        status = "available" if tool["available"] else "missing"
        detail = tool["version"] or tool["detail"]
        lines.append(
            f"| `{tool['name']}` | {md(tool['purpose'])} | `{status}` | {md(detail)} |"
        )

    lines.extend(
        [
            "",
            "## Support Tools",
            "",
            "| Tool | Purpose | Status | Detail |",
            "|---|---|---|---|",
        ]
    )
    for tool in payload["support_tools"]:
        status = "available" if tool["available"] else "missing"
        detail = tool["version"] or tool["detail"]
        lines.append(
            f"| `{tool['name']}` | {md(tool['purpose'])} | `{status}` | {md(detail)} |"
        )

    lines.extend(
        [
            "",
            "## SBOM Targets",
            "",
            "| Target | Role | Path | Status |",
            "|---|---|---|---|",
        ]
    )
    for target in payload["sbom_targets"]:
        status = "available" if target["exists"] else "missing"
        lines.append(
            f"| {md(target['name'])} | {md(target['role'])} | `{target['path']}` | `{status}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    lines.extend(f"- {line}" for line in payload["interpretation"])
    lines.append("")
    return "\n".join(lines)


def md(value: object) -> str:
    return str(value).replace("|", "\\|")


def normalize_path(path: Path) -> str:
    return path.as_posix()


def strip_ansi(value: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", value)


if __name__ == "__main__":
    raise SystemExit(main())
