from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass


@dataclass
class ToolStatus:
    name: str
    kind: str
    available: bool
    detail: str


CLI_TOOLS = {
    "python": ["python", "--version"],
    "java": ["java", "-version"],
    "gradle": ["gradle", "--version"],
    "apktool": ["apktool", "--version"],
    "jadx": ["jadx", "--version"],
    "d8": ["d8", "--version"],
    "trivy": ["trivy", "--version"],
    "grype": ["grype", "version"],
    "cyclonedx": ["cyclonedx", "--version"],
    "cyclonedx-cli": ["cyclonedx-cli", "--version"],
    "syft": ["syft", "version"],
    "cdxgen": ["cdxgen", "--version"],
    "node": ["node", "--version"],
    "npm": ["npm", "--version"],
    "dotnet": ["dotnet", "--version"],
}

PYTHON_PACKAGES = [
    "androguard",
    "networkx",
    "requests",
    "packaging",
    "pydantic",
    "rich",
    "pytest",
]


def run_version(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as exc:
        return f"error: {exc}"

    output = (completed.stdout or completed.stderr).strip()
    if not output:
        output = f"exit_code={completed.returncode}"
    first_line = output.splitlines()[0] if output else ""
    return first_line


def check_cli_tool(name: str, command: list[str]) -> ToolStatus:
    executable = shutil.which(command[0])
    if not executable:
        return ToolStatus(name=name, kind="cli", available=False, detail="missing from PATH")
    return ToolStatus(name=name, kind="cli", available=True, detail=run_version(command))


def check_python_package(name: str) -> ToolStatus:
    spec = importlib.util.find_spec(name)
    if spec is None:
        return ToolStatus(name=name, kind="python", available=False, detail="missing")
    return ToolStatus(name=name, kind="python", available=True, detail="importable")


def main() -> int:
    statuses: list[ToolStatus] = []
    statuses.append(
        ToolStatus(
            name="python-runtime",
            kind="runtime",
            available=True,
            detail=sys.version.split()[0],
        )
    )

    for name, command in CLI_TOOLS.items():
        statuses.append(check_cli_tool(name, command))

    for package in PYTHON_PACKAGES:
        statuses.append(check_python_package(package))

    print(json.dumps([asdict(status) for status in statuses], indent=2))

    missing_required = [
        status.name
        for status in statuses
        if not status.available and status.name in {"python", "java", "androguard", "networkx", "requests"}
    ]
    if missing_required:
        print(f"Missing required tools/packages: {', '.join(missing_required)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
