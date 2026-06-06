from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from apk_sbom.report import generate_final_report  # noqa: E402
from apk_sbom.reference_features import DEFAULT_FEATURE_DB_PATH  # noqa: E402
from apk_sbom.vulnerability import DEFAULT_OSV_BATCH_URL  # noqa: E402


DEFAULT_DEMO_OUTPUT_DIR = Path("data/results/graduation-demo-report")
CALIBRATED_COMBINED_DB = Path(
    "data/reference_db/reference_features_calibrated_combined.sqlite"
)


def default_demo_db_path() -> Path:
    calibrated = REPO_ROOT / CALIBRATED_COMBINED_DB
    if calibrated.exists():
        return CALIBRATED_COMBINED_DB
    return DEFAULT_FEATURE_DB_PATH


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run an offline-safe APK report and write a graduation-demo readiness "
            "summary."
        )
    )
    parser.add_argument("apk_path", help="APK to analyze.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_DEMO_OUTPUT_DIR),
        help=f"Output directory. Default: {DEFAULT_DEMO_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--db-path",
        default=str(default_demo_db_path()),
        help=(
            "Reference feature DB. Defaults to the calibrated combined DB when "
            "available."
        ),
    )
    parser.add_argument(
        "--coordinate",
        help="Optional Maven coordinate filter, for rehearsing a known demo case.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=30,
        help="Number of matcher candidates to keep per coordinate.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.05,
        help="Minimum matcher score to report.",
    )
    parser.add_argument(
        "--include-uncertain",
        action="store_true",
        help="Include uncertain component candidates in the SBOM/report.",
    )
    parser.add_argument(
        "--query-osv",
        action="store_true",
        help="Opt in to OSV network vulnerability lookup.",
    )
    parser.add_argument(
        "--osv-api-url",
        default=DEFAULT_OSV_BATCH_URL,
        help="OSV querybatch endpoint.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="OSV request timeout in seconds.",
    )
    parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="When querying OSV, skip per-advisory enrichment requests.",
    )
    parser.add_argument(
        "--source-validation-json",
        help=(
            "Optional source-validation result JSON. Supplying this makes the "
            "readiness summary source-validation aware, but only for that artifact."
        ),
    )
    parser.add_argument(
        "--strict-exit",
        action="store_true",
        help=(
            "Return a non-zero exit code if report generation fails. By default "
            "the live-demo wrapper writes a failure readiness artifact and exits 0."
        ),
    )
    return parser.parse_args(argv)


def build_demo_readiness(
    report_payload: dict[str, Any],
    *,
    apk_path: str,
    output_dir: str,
    db_path: str,
    artifacts: dict[str, Any],
    query_osv: bool,
    source_validation_json: str | None,
) -> dict[str, Any]:
    source_validation = summarize_source_validation_artifact(source_validation_json)
    classification = classify_report(
        report_payload,
        query_osv=query_osv,
        source_validation_present=source_validation["mode"] == "provided",
    )
    apk = report_payload.get("apk") or {}
    manifest = apk.get("manifest_metadata") or {}
    match_summary = report_payload.get("match_summary") or {}
    obfuscation_risk = report_payload.get("obfuscation_risk") or {}
    forensic = apk.get("forensic_summary") or {}

    summary = {
        "status": "report-generated",
        "readiness_level": readiness_level_for_classification(
            classification["classification"]
        ),
        "demo_outcome": demo_outcome_for_classification(
            classification["classification"]
        ),
        "classification": classification["classification"],
        "classification_reason": classification["reason"],
        "apk_path": apk_path,
        "output_dir": output_dir,
        "db_path": db_path,
        "package_name": manifest.get("package_name") or "unknown",
        "version_name": manifest.get("version_name") or "unknown",
        "version_code": manifest.get("version_code") or "unknown",
        "counts": classification["counts"],
        "component_status_counts": classification["component_status_counts"],
        "framework_hints": classification["framework_hints"],
        "obfuscation_risk": {
            "level": obfuscation_risk.get("level") or "unknown",
            "score": obfuscation_risk.get("score"),
        },
        "risk_indicators": summarize_risk_indicators(forensic),
        "source_validation": source_validation,
        "osv": {
            "mode": "queried" if query_osv else "skipped-offline-safe",
            "summary_present": bool(report_payload.get("osv")),
        },
        "safe_claims": build_safe_claims(
            classification,
            query_osv=query_osv,
            source_validation_present=source_validation["mode"] == "provided",
        ),
        "limitations": build_limitations(
            classification,
            query_osv=query_osv,
            source_validation_present=source_validation["mode"] == "provided",
        ),
        "next_steps": build_next_steps(
            classification,
            query_osv=query_osv,
            source_validation=source_validation,
        ),
        "supervisor_wording": build_supervisor_wording(
            classification,
            source_validation=source_validation,
            query_osv=query_osv,
        ),
        "artifacts": artifacts,
    }
    return summary


def classify_report(
    report_payload: dict[str, Any],
    *,
    query_osv: bool,
    source_validation_present: bool,
) -> dict[str, Any]:
    apk = report_payload.get("apk") or {}
    forensic = apk.get("forensic_summary") or {}
    match_summary = report_payload.get("match_summary") or {}
    components = _as_list(report_payload.get("detected_components"))
    native_libraries = _as_list(apk.get("native_libraries"))

    status_counts = component_status_counts(components)
    framework_hints = infer_framework_hints(native_libraries)
    extraction_risk = str(forensic.get("extraction_risk") or "unknown").lower()
    obfuscation_level = str(
        (report_payload.get("obfuscation_risk") or {}).get("level") or "unknown"
    ).lower()

    counts = {
        "maven_components": len(components),
        "native_libraries": len(native_libraries),
        "dex_files": len(_as_list(apk.get("dex_files"))),
        "dex_files_analyzed": _int_value(match_summary.get("dex_files_analyzed")),
        "dex_files_failed": _int_value(match_summary.get("dex_files_failed")),
        "uncertain_or_candidate_components": count_uncertain_or_candidate_components(
            components
        ),
    }

    all_components_uncertain = (
        counts["maven_components"] > 0
        and counts["uncertain_or_candidate_components"] == counts["maven_components"]
    )

    if obfuscation_level in {"high", "critical"} or extraction_risk in {
        "high",
        "critical",
    }:
        classification = "obfuscation-risk-boundary"
        reason = "High obfuscation or extraction risk makes the result a boundary case."
    elif obfuscation_level == "medium" and all_components_uncertain:
        classification = "obfuscation-risk-boundary"
        reason = (
            "Medium obfuscation risk plus only candidate/uncertain component "
            "evidence makes this a boundary case."
        )
    elif framework_hints and counts["maven_components"] <= 2:
        classification = "framework-boundary"
        reason = (
            "Framework/native hints dominate the APK while Maven evidence is thin."
        )
    elif counts["maven_components"] == 0 and counts["native_libraries"] > 0:
        classification = "native-or-framework-boundary"
        reason = "Native files are present but no Maven component signal was recovered."
    elif counts["maven_components"] == 0:
        classification = "no-maven-signal"
        reason = "The APK parsed, but no Maven component candidates were recovered."
    elif source_validation_present:
        classification = "source-validation-aware-report"
        reason = "A source-validation artifact was supplied for this report."
    else:
        classification = "apk-only-sbom-evidence"
        reason = "Maven components were detected from APK evidence only."

    return {
        "classification": classification,
        "reason": reason,
        "counts": counts,
        "component_status_counts": dict(status_counts),
        "framework_hints": framework_hints,
        "query_osv": query_osv,
        "source_validation_present": source_validation_present,
    }


def component_status_counts(components: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for component in components:
        status = str(component.get("version_status") or "").lower()
        label = str(component.get("version_confidence_label") or "").lower()
        if status in {"exact", "likely", "candidate", "uncertain"}:
            counts[status] += 1
        else:
            counts["other"] += 1
        if label == "low":
            counts["low_confidence"] += 1
    for key in ("exact", "likely", "candidate", "uncertain", "low_confidence", "other"):
        counts.setdefault(key, 0)
    return counts


def count_uncertain_or_candidate_components(components: list[dict[str, Any]]) -> int:
    count = 0
    for component in components:
        status = str(component.get("version_status") or "").lower()
        label = str(component.get("version_confidence_label") or "").lower()
        if status in {"candidate", "uncertain"} or label == "low":
            count += 1
    return count


def infer_framework_hints(native_libraries: list[dict[str, Any]]) -> list[str]:
    names = {
        str(library.get("filename") or library.get("path") or "").lower()
        for library in native_libraries
    }
    hints: set[str] = set()
    if "libflutter.so" in names:
        hints.add("Flutter")
    if {"libunity.so", "libil2cpp.so"} & names:
        hints.add("Unity")
    if {
        "libhermes.so",
        "libreactnativejni.so",
        "libfbjni.so",
        "libjsc.so",
        "libjscexecutor.so",
        "libturbomodulejsijni.so",
    } & names:
        hints.add("React Native")
    if "libjingle_peerconnection_so.so" in names:
        hints.add("WebRTC")
    return sorted(hints)


def summarize_source_validation_artifact(path: str | None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "mode": "not-provided",
        "path": path,
        "available": False,
    }
    if not path:
        return summary

    summary["mode"] = "provided"
    validation_path = Path(path)
    if not validation_path.exists():
        summary["error"] = "source-validation JSON path does not exist"
        return summary

    try:
        payload = load_json(validation_path)
    except Exception as error:  # pragma: no cover - defensive user-input path.
        summary["error"] = f"{type(error).__name__}: {error}"
        return summary

    sbom_components = _int_value(payload.get("sbom_components"))
    confirmed = _int_value(payload.get("confirmed"))
    mismatches = _int_value(payload.get("version_mismatches"))
    missing = _int_value(payload.get("missing"))
    summary.update(
        {
            "available": True,
            "sbom_components": sbom_components,
            "confirmed": confirmed,
            "version_mismatches": mismatches,
            "missing": missing,
            "extra_candidates": _int_value(payload.get("extra_candidates")),
            "candidate_confirmed": _int_value(payload.get("candidate_confirmed")),
            "candidate_version_mismatches": _int_value(
                payload.get("candidate_version_mismatches")
            ),
            "candidate_missing": _int_value(payload.get("candidate_missing")),
            "confirmation_rate": (
                round(confirmed / sbom_components, 4)
                if sbom_components > 0
                else None
            ),
        }
    )
    return summary


def summarize_risk_indicators(forensic: dict[str, Any]) -> list[dict[str, str]]:
    indicators = []
    for indicator in _as_list(forensic.get("indicators")):
        if not isinstance(indicator, dict):
            continue
        indicators.append(
            {
                "code": str(indicator.get("code") or "unknown"),
                "severity": str(indicator.get("severity") or "unknown"),
                "detail": str(indicator.get("detail") or ""),
            }
        )
    return indicators


def readiness_level_for_classification(classification: str) -> str:
    if classification in {"source-validation-aware-report", "apk-only-sbom-evidence"}:
        return "presentable"
    if classification in {
        "framework-boundary",
        "native-or-framework-boundary",
        "obfuscation-risk-boundary",
        "no-maven-signal",
    }:
        return "presentable-with-limitations"
    return "needs-explanation"


def demo_outcome_for_classification(classification: str) -> str:
    if classification == "source-validation-aware-report":
        return "source-validation-aware-demo"
    if classification == "apk-only-sbom-evidence":
        return "apk-only-sbom-demo"
    if classification in {"framework-boundary", "native-or-framework-boundary"}:
        return "framework-or-native-boundary-demo"
    if classification == "obfuscation-risk-boundary":
        return "obfuscation-boundary-demo"
    if classification == "no-maven-signal":
        return "parsed-but-no-maven-signal-demo"
    return "manual-explanation-needed"


def build_safe_claims(
    classification: dict[str, Any],
    *,
    query_osv: bool,
    source_validation_present: bool,
) -> list[str]:
    counts = classification["counts"]
    claims = [
        "The APK was processed through the compiled-APK evidence pipeline.",
        "The generated CycloneDX SBOM is based on recovered APK evidence.",
    ]
    if counts["maven_components"]:
        claims.append(
            "Detected Maven components can be discussed with their confidence labels."
        )
    if counts["native_libraries"]:
        claims.append("Native libraries are represented as hash-only file components.")
    if source_validation_present:
        claims.append(
            "Source-validation-aware statements are allowed only for the supplied "
            "source-validation artifact."
        )
    else:
        claims.append("This run is APK-only and is not source-validated.")
    if query_osv:
        claims.append("OSV lookup was requested for detected Maven components.")
    else:
        claims.append("OSV lookup was skipped for offline-safe demo execution.")
    return claims


def build_limitations(
    classification: dict[str, Any],
    *,
    query_osv: bool,
    source_validation_present: bool,
) -> list[str]:
    counts = classification["counts"]
    limitations = []
    if not source_validation_present:
        limitations.append(
            "Do not claim ground-truth dependency recall without source validation."
        )
    if counts["uncertain_or_candidate_components"]:
        limitations.append(
            "Some component versions are candidate or uncertain and must not be "
            "presented as exact."
        )
    if counts["native_libraries"]:
        limitations.append(
            "Native libraries are visible as files, but native package/version "
            "recovery is outside this Maven matcher."
        )
    if classification["framework_hints"]:
        limitations.append(
            "Framework hints were detected: "
            + ", ".join(classification["framework_hints"])
            + ". Treat this as a framework-boundary case when Maven evidence is thin."
        )
    if classification["classification"] == "obfuscation-risk-boundary":
        limitations.append(
            "Obfuscation, extraction risk, or weak component evidence makes this a "
            "boundary case; low-confidence matches need extra caution."
        )
    if not query_osv:
        limitations.append(
            "Vulnerability lookup was not run; enable --query-osv for live OSV results."
        )
    return limitations


def build_next_steps(
    classification: dict[str, Any],
    *,
    query_osv: bool,
    source_validation: dict[str, Any],
) -> list[str]:
    steps = [
        "Open demo-readiness.md first, then report.html, then sbom.cdx.json.",
    ]
    kind = classification["classification"]
    counts = classification["counts"]
    if kind == "source-validation-aware-report" and source_validation.get("available"):
        steps.append(
            "Use the source-validation summary to explain confirmed, mismatch, and missing rows."
        )
    elif kind == "apk-only-sbom-evidence":
        steps.append(
            "Explain this as APK-only evidence and avoid source-validated recall claims."
        )
    elif kind in {"framework-boundary", "native-or-framework-boundary"}:
        steps.append(
            "Lead with extracted native/framework evidence and describe Maven recovery as partial."
        )
    elif kind == "obfuscation-risk-boundary":
        steps.append(
            "Lead with the obfuscation or extraction-risk warning before showing candidates."
        )
    elif kind == "no-maven-signal":
        steps.append(
            "Show that the APK parsed, then explain that no Maven library signal was recovered."
        )

    if counts["native_libraries"]:
        steps.append("Point out that native libraries are hash-only SBOM file components.")
    if counts["uncertain_or_candidate_components"]:
        steps.append("Call candidate or uncertain versions hypotheses, not exact findings.")
    if not query_osv:
        steps.append("Run again with --query-osv only if network access is available.")
    if source_validation["mode"] == "provided" and not source_validation.get("available"):
        steps.append(
            "Fix or remove the source-validation JSON path before making source-validation claims."
        )
    return steps


def build_supervisor_wording(
    classification: dict[str, Any],
    *,
    source_validation: dict[str, Any],
    query_osv: bool,
) -> str:
    kind = classification["classification"]
    counts = classification["counts"]
    if kind == "source-validation-aware-report" and source_validation.get("available"):
        wording = (
            "This APK report is source-validation aware for the supplied APK/source "
            "pair: {confirmed}/{total} emitted Maven versions are confirmed, with "
            "{mismatches} version mismatches and {missing} missing coordinates."
        ).format(
            confirmed=source_validation.get("confirmed", 0),
            total=source_validation.get("sbom_components", 0),
            mismatches=source_validation.get("version_mismatches", 0),
            missing=source_validation.get("missing", 0),
        )
    elif kind == "apk-only-sbom-evidence":
        wording = (
            "This is an APK-only recovery report. It recovered {components} Maven "
            "component candidates from compiled APK evidence, so I can discuss the "
            "SBOM and confidence labels, but not ground-truth dependency recall."
        ).format(components=counts["maven_components"])
    elif kind in {"framework-boundary", "native-or-framework-boundary"}:
        wording = (
            "This APK is a framework/native boundary case. The tool still extracted "
            "APK evidence and hash-only native file components, but Maven version "
            "recovery should be described as limited."
        )
    elif kind == "obfuscation-risk-boundary":
        wording = (
            "This APK is an obfuscation or extraction-risk boundary case. The useful "
            "result is the warning plus any low-confidence candidates, not a clean "
            "exact-version claim."
        )
    elif kind == "no-maven-signal":
        wording = (
            "The APK was parsed, but no Maven component signal was recovered. That is "
            "a presentable limitation result for APK-only static analysis."
        )
    else:
        wording = (
            "This APK needs manual explanation. I will use the readiness file to "
            "separate what was extracted from what cannot be claimed."
        )

    if not query_osv:
        wording += " OSV was skipped to keep the demo offline-safe."
    return wording


def build_failure_summary(
    *,
    apk_path: str,
    output_dir: str,
    db_path: str,
    query_osv: bool,
    source_validation_json: str | None,
    error: Exception,
) -> dict[str, Any]:
    return {
        "status": "failed-before-report",
        "readiness_level": "failure-summary-written",
        "demo_outcome": "presentable-failure-summary",
        "classification": "failed-before-report",
        "classification_reason": (
            "The wrapper could not generate the underlying APK report artifact."
        ),
        "apk_path": apk_path,
        "output_dir": output_dir,
        "db_path": db_path,
        "source_validation": {
            "mode": "provided" if source_validation_json else "not-provided",
            "path": source_validation_json,
        },
        "osv": {
            "mode": "queried" if query_osv else "skipped-offline-safe",
            "summary_present": False,
        },
        "error": {
            "type": type(error).__name__,
            "message": str(error),
        },
        "safe_claims": [
            "The demo wrapper caught the failure and wrote a readiness artifact.",
        ],
        "limitations": [
            "No SBOM or match report should be claimed from this failed run.",
            "Use the error message to explain whether the issue is input, database, "
            "DEX parsing, or environment related.",
        ],
        "next_steps": [
            "Open demo-readiness.md and explain the failure boundary.",
            "Check that the APK path exists and that the calibrated reference DB is available.",
            "Use --strict-exit in automation if this condition should fail the command.",
        ],
        "supervisor_wording": (
            "The wrapper did not hide the failure. It wrote a readiness artifact with "
            "the exception type and message, so I can explain the input or environment "
            "boundary instead of pretending an SBOM was generated."
        ),
        "artifacts": {
            "demo_readiness_json": str(Path(output_dir) / "demo-readiness.json"),
            "demo_readiness_markdown": str(Path(output_dir) / "demo-readiness.md"),
        },
    }


def write_readiness_files(summary: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary["artifacts"]["demo_readiness_json"] = str(
        output_dir / "demo-readiness.json"
    )
    summary["artifacts"]["demo_readiness_markdown"] = str(
        output_dir / "demo-readiness.md"
    )
    (output_dir / "demo-readiness.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "demo-readiness.md").write_text(
        render_readiness_markdown(summary),
        encoding="utf-8",
    )


def render_readiness_markdown(summary: dict[str, Any]) -> str:
    counts = summary.get("counts") or {}
    artifacts = summary.get("artifacts") or {}
    lines = [
        "# Graduation Demo APK Readiness",
        "",
        "## Status",
        "",
        f"- Status: {summary.get('status', 'unknown')}",
        f"- Readiness: {summary.get('readiness_level', 'unknown')}",
        f"- Demo outcome: {summary.get('demo_outcome', 'unknown')}",
        f"- Classification: {summary.get('classification', 'unknown')}",
        f"- Reason: {summary.get('classification_reason', 'unknown')}",
        f"- APK: `{summary.get('apk_path', 'unknown')}`",
        f"- Output directory: `{summary.get('output_dir', 'unknown')}`",
        f"- Reference DB: `{summary.get('db_path', 'unknown')}`",
    ]
    if "package_name" in summary:
        lines.extend(
            [
                f"- Package: `{summary.get('package_name')}`",
                f"- Version: `{summary.get('version_name')}` / code `{summary.get('version_code')}`",
            ]
        )

    if summary.get("status") == "failed-before-report":
        error = summary.get("error") or {}
        lines.extend(
            [
                "",
                "## Failure",
                "",
                f"- Type: {error.get('type', 'unknown')}",
                f"- Message: {error.get('message', 'unknown')}",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Counts",
                "",
                f"- DEX files in APK: {counts.get('dex_files', 0)}",
                f"- DEX files analyzed: {counts.get('dex_files_analyzed', 0)}",
                f"- DEX files failed: {counts.get('dex_files_failed', 0)}",
                f"- Maven components: {counts.get('maven_components', 0)}",
                f"- Native libraries: {counts.get('native_libraries', 0)}",
                "- Candidate/uncertain/low-confidence versions: "
                f"{counts.get('uncertain_or_candidate_components', 0)}",
                "",
                "## Modes",
                "",
                f"- Source validation: {summary['source_validation']['mode']}",
                f"- OSV: {summary['osv']['mode']}",
            ]
        )
        source_validation = summary.get("source_validation") or {}
        if source_validation.get("available"):
            lines.extend(
                [
                    "- Source-validation counts: "
                    f"{source_validation.get('confirmed', 0)}/"
                    f"{source_validation.get('sbom_components', 0)} confirmed, "
                    f"{source_validation.get('version_mismatches', 0)} mismatches, "
                    f"{source_validation.get('missing', 0)} missing",
                ]
            )
        elif source_validation.get("mode") == "provided":
            lines.append(
                "- Source-validation artifact problem: "
                f"{source_validation.get('error', 'unknown')}"
            )

        risk_indicators = summary.get("risk_indicators") or []
        if risk_indicators:
            lines.extend(["", "## Risk Indicators", ""])
            for indicator in risk_indicators:
                lines.append(
                    "- {code} ({severity}): {detail}".format(
                        code=indicator.get("code", "unknown"),
                        severity=indicator.get("severity", "unknown"),
                        detail=indicator.get("detail", ""),
                    )
                )

    lines.extend(
        [
            "",
            "## Safe Claims",
            "",
            *_markdown_bullets(summary.get("safe_claims") or []),
            "",
            "## Limitations",
            "",
            *_markdown_bullets(summary.get("limitations") or []),
            "",
            "## Next Steps",
            "",
            *_markdown_bullets(summary.get("next_steps") or []),
            "",
            "## Report Artifacts",
            "",
        ]
    )
    for label, value in sorted(artifacts.items()):
        if value:
            lines.append(f"- {label}: `{value}`")

    lines.extend(
        [
            "",
            "## Supervisor Wording",
            "",
            "This is the safe way to describe this run:",
            "",
            f"> {summary.get('supervisor_wording', 'No wording available.')}",
            "",
        ]
    )
    if summary.get("status") == "failed-before-report":
        lines.append(
            "- The wrapper caught the failure and preserved the reason, so I can "
            "explain the boundary instead of silently losing the demo."
        )
    elif summary["source_validation"]["mode"] == "provided":
        lines.append(
            "- This report is source-validation aware for the supplied validation "
            "artifact; I will not generalize that claim beyond this APK/source pair."
        )
    else:
        lines.append(
            "- This is an APK-only recovery report, so I will use it to demonstrate "
            "evidence extraction and SBOM generation, not ground-truth recall."
        )
    if summary["osv"]["mode"] == "skipped-offline-safe":
        lines.append(
            "- OSV was intentionally skipped for offline safety; I can enable it with "
            "`--query-osv` when network access is available."
        )
    return "\n".join(lines) + "\n"


def _markdown_bullets(items: list[str]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {item}" for item in items]


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _int_value(value: Any) -> int:
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        artifacts = generate_final_report(
            args.apk_path,
            output_dir=output_dir,
            db_path=args.db_path,
            coordinate=args.coordinate,
            top=args.top,
            min_score=args.min_score,
            include_uncertain=args.include_uncertain,
            query_osv=args.query_osv,
            osv_api_url=args.osv_api_url,
            timeout=args.timeout,
            enrich_vulnerabilities=not args.no_enrich,
            source_validation_json=args.source_validation_json,
        )
        report_payload = load_json(Path(artifacts.report_json))
        summary = build_demo_readiness(
            report_payload,
            apk_path=args.apk_path,
            output_dir=str(output_dir),
            db_path=args.db_path,
            artifacts=artifacts.to_dict(),
            query_osv=args.query_osv,
            source_validation_json=args.source_validation_json,
        )
        exit_code = 0
    except Exception as error:
        summary = build_failure_summary(
            apk_path=args.apk_path,
            output_dir=str(output_dir),
            db_path=args.db_path,
            query_osv=args.query_osv,
            source_validation_json=args.source_validation_json,
            error=error,
        )
        exit_code = 1 if args.strict_exit else 0

    write_readiness_files(summary, output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
