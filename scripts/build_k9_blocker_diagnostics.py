from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_JSON = Path("data/results/source-validation/k9-thunderbird-android/k9-blocker-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/K9_BLOCKER_DIAGNOSTICS.md")
DEFAULT_PROOF_BUNDLE = Path("docs/evaluation/K9_THUNDERBIRD_PROOF_BUNDLE.md")
DEFAULT_CATALOG_VALIDATION = Path(
    "data/results/source-validation/k9-thunderbird-android/k9-version-catalog-validation.md"
)
DEFAULT_GRADLE_PROJECTS_ERROR = Path(
    "data/results/source-validation/k9-thunderbird-android/gradle-projects-error.log"
)
DEFAULT_DEPENDENCY_ATTEMPT = Path(
    "data/results/source-validation/k9-thunderbird-android/fossReleaseRuntimeClasspath.txt"
)
DEFAULT_RETRY_ATTEMPT = Path(
    "data/results/source-validation/k9-thunderbird-android/fossReleaseRuntimeClasspath.retry-google-first.txt"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize K-9 dependency-tree blocker evidence.",
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload()

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
                "status": payload["status"],
                "attempts": len(payload["attempts"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "case_id": "k9-thunderbird-android",
        "status": "completed-blocked",
        "classification": "source-linked-blocked",
        "policy": [
            "Do not count K-9 in source-validated accuracy metrics until a resolved Gradle dependency tree exists.",
            "Catalog-only validation is useful source-linked evidence, but it is weaker than runtime classpath validation.",
            "The blocker is in source/Gradle build configuration, not in APK extraction or matcher scoring.",
        ],
        "artifacts": {
            "proof_bundle": normalize_path(DEFAULT_PROOF_BUNDLE),
            "catalog_validation": normalize_path(DEFAULT_CATALOG_VALIDATION),
            "initial_dependency_attempt": normalize_path(DEFAULT_DEPENDENCY_ATTEMPT),
            "repository_order_retry_attempt": normalize_path(DEFAULT_RETRY_ATTEMPT),
            "gradle_projects_error": normalize_path(DEFAULT_GRADLE_PROJECTS_ERROR),
        },
        "attempts": [
            {
                "name": "configuration-cache-disabled Gradle 9.5.0 projects probe",
                "result": "failed",
                "evidence": summarize_text(DEFAULT_GRADLE_PROJECTS_ERROR),
                "interpretation": "The included build-plugin tried to resolve TensorFlow metadata through the plugin portal and failed before project configuration completed.",
            },
            {
                "name": "Gradle 9.4.0 runtime classpath attempt",
                "result": "timed-out",
                "evidence": summarize_text(DEFAULT_DEPENDENCY_ATTEMPT),
                "interpretation": "The run advanced through included build-plugin compilation tasks but did not emit fossReleaseRuntimeClasspath.",
            },
            {
                "name": "repository-order retry",
                "result": "timed-out",
                "evidence": summarize_text(DEFAULT_RETRY_ATTEMPT),
                "interpretation": "The validation-only source copy preferred google() and mavenCentral() before the plugin portal, but the run still stalled in included build-plugin setup.",
            },
            {
                "name": "2026-05-27 bounded Docker retry",
                "result": "timed-out",
                "evidence": (
                    "Ran `gradle --no-daemon --no-configuration-cache :app-k9mail:dependencies "
                    "--configuration fossReleaseRuntimeClasspath` in the validation-only source copy. "
                    "The command timed out after 600 seconds without producing a dependency tree."
                ),
                "interpretation": "A fresh bounded retry confirms the blocker is still active in the current Docker runtime.",
            },
        ],
        "catalog_summary": {
            "exact_confirmations": 3,
            "exact_mismatches": 2,
            "artifact_family_confirmations": 1,
            "artifact_family_mismatches": 1,
            "not_in_catalog": 4,
        },
        "conclusion": (
            "Complete for the current MVP as a blocked con: K-9 has APK/source/report/catalog evidence, "
            "but repeated bounded Gradle attempts still do not produce a resolved fossReleaseRuntimeClasspath. "
            "Keep it as source-linked blocked evidence unless a deeper K-9 build-system investigation becomes a separate task."
        ),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# K-9 Blocker Diagnostics",
        "",
        "Generated by `scripts/build_k9_blocker_diagnostics.py`.",
        "",
        "This diagnostic records the current K-9 / Thunderbird Android dependency-tree blocker. It does not change matcher output or source-validation metrics.",
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
            f"- Status: `{payload['status']}`",
            f"- Classification: `{payload['classification']}`",
            f"- Conclusion: {payload['conclusion']}",
            "",
            "## Catalog-Only Validation",
            "",
            "| Status | Count |",
            "|---|---:|",
        ]
    )
    for key, value in payload["catalog_summary"].items():
        lines.append(f"| {md(key.replace('_', ' '))} | {value} |")

    lines.extend(
        [
            "",
            "## Gradle Attempts",
            "",
            "| Attempt | Result | Evidence | Interpretation |",
            "|---|---|---|---|",
        ]
    )
    for attempt in payload["attempts"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(attempt["name"]),
                    f"`{attempt['result']}`",
                    md(attempt["evidence"]),
                    md(attempt["interpretation"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep K-9 excluded from source-validated accuracy metrics.",
            "- Preserve the catalog-only validation as weak source-linked evidence.",
            "- Treat another K-9 retry as a separate build-system investigation, not as matcher work.",
            "",
        ]
    )
    return "\n".join(lines)


def summarize_text(path: Path, limit: int = 350) -> str:
    if not path.exists():
        return "artifact missing"
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return "artifact exists but has no captured stderr output"
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
