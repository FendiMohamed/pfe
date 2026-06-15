from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_MD = Path("docs/evaluation/GRADUATION_DEMO_REHEARSAL.md")
OUTPUT_JSON = Path("data/results/evaluation/graduation-demo-rehearsal.json")


CASES: list[dict[str, Any]] = [
    {
        "id": "clean-real-fdroid",
        "title": "Clean real APK: F-Droid",
        "purpose": "Open with the strongest real-APK proof: clean source validation and OSV-negative result.",
        "apk_path": "data/test_apks/real/F-Droid.apk",
        "report_json": "data/results/report-real-f-droid-final-demo-osv/report.json",
        "source_validation_md": "data/results/source-validation/fdroid-final-demo-osv/source-validation.md",
        "command": (
            "docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report "
            "data/test_apks/real/F-Droid.apk "
            "--output-dir data/results/report-real-f-droid-final-demo-osv "
            "--db-path data/reference_db/reference_features_calibrated_combined.sqlite "
            "--top 30"
        ),
        "open_first": [
            "data/results/report-real-f-droid-final-demo-osv/report.html",
            "data/results/source-validation/fdroid-final-demo-osv/source-validation.md",
            "data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json",
        ],
        "safe_claim": (
            "This real APK has source-validation evidence: the emitted Maven versions "
            "are confirmed against the resolved source dependency tree."
        ),
        "do_not_claim": "Do not generalize this clean result to every arbitrary APK.",
    },
    {
        "id": "controlled-vulnerable-jackson",
        "title": "CVE-positive controlled APK: Jackson Databind",
        "purpose": "Show that the SBOM-to-OSV layer can produce positive vulnerability findings.",
        "apk_path": "data/test_apks/controlled-com-fasterxml-jackson-core-jackson-databind-2.9.10.8-clear.apk",
        "report_json": "data/results/demo-osv-vulnerable-jackson-databind/report.json",
        "command": (
            "docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report "
            "data/test_apks/controlled-com-fasterxml-jackson-core-jackson-databind-2.9.10.8-clear.apk "
            "--output-dir data/results/demo-osv-vulnerable-jackson-databind "
            "--db-path data/reference_db/reference_features.sqlite "
            "--top 10"
        ),
        "open_first": [
            "data/results/demo-osv-vulnerable-jackson-databind/report.html",
            "data/results/demo-osv-vulnerable-jackson-databind/osv-vulnerabilities.json",
            "data/results/demo-osv-vulnerable-jackson-databind/sbom.cdx.json",
        ],
        "safe_claim": (
            "This controlled APK proves the vulnerability lookup path: detected Maven "
            "component, CycloneDX component, OSV advisories."
        ),
        "do_not_claim": "Do not present this controlled fixture as real-world APK accuracy.",
    },
    {
        "id": "partial-real-k9",
        "title": "Partial real APK: K-9 / Thunderbird Android",
        "purpose": "Show honest source-validated partial evidence and explain version mismatches.",
        "apk_path": "data/test_apks/real/k9-thunderbird-android/k9-thunderbird-android.apk",
        "report_json": "data/results/report-real-k9-thunderbird-android/report.json",
        "source_validation_md": "data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.md",
        "command": (
            "docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report "
            "data/test_apks/real/k9-thunderbird-android/k9-thunderbird-android.apk "
            "--output-dir data/results/report-real-k9-thunderbird-android "
            "--db-path data/reference_db/reference_features_calibrated_combined.sqlite "
            "--top 30"
        ),
        "open_first": [
            "data/results/report-real-k9-thunderbird-android/report.html",
            "data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.md",
            "docs/evaluation/K9_BLOCKER_DIAGNOSTICS.md",
        ],
        "safe_claim": (
            "K-9 is now source-validated partial evidence: some emitted Maven versions "
            "confirm, and the remaining rows are visible mismatches."
        ),
        "do_not_claim": (
            "Do not call K-9 clean; its dependency tree came from a validation-only "
            "plugin-lite included-build reduction."
        ),
    },
    {
        "id": "framework-boundary-jitsi",
        "title": "Framework boundary: Jitsi Meet",
        "purpose": "Show React Native/native-heavy boundaries without hiding the useful Maven evidence.",
        "apk_path": "data/test_apks/real/jitsi-meet/jitsi-meet.apk",
        "report_json": "data/results/report-real-jitsi-meet/report.json",
        "source_validation_md": "data/results/source-validation/jitsi-meet-report-validation/source-validation.md",
        "command": (
            "docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report "
            "data/test_apks/real/jitsi-meet/jitsi-meet.apk "
            "--output-dir data/results/report-real-jitsi-meet "
            "--db-path data/reference_db/reference_features_calibrated_combined.sqlite "
            "--top 30"
        ),
        "open_first": [
            "data/results/report-real-jitsi-meet/report.html",
            "data/results/source-validation/jitsi-meet-report-validation/source-validation.md",
            "docs/evaluation/JITSI_MEET_PROOF_BUNDLE.md",
        ],
        "safe_claim": (
            "Jitsi demonstrates that the tool can report Maven evidence while clearly "
            "flagging native and framework-heavy boundaries."
        ),
        "do_not_claim": (
            "Do not present React Native/native code as fully recovered Maven "
            "dependency evidence."
        ),
    },
    {
        "id": "obfuscated-limitation-simplify",
        "title": "Obfuscated limitation sample: Simplify",
        "purpose": "Show how the report surfaces obfuscation and uncertainty instead of pretending certainty.",
        "apk_path": "data/test_apks/limitation/simplify-obfuscated-app/simplify-obfuscated-app.apk",
        "report_json": "data/results/report-limitation-simplify-obfuscated-app/report.json",
        "readiness_json": "data/results/graduation-demo/simplify-obfuscated-offline/demo-readiness.json",
        "command": (
            "docker compose run --rm apk-sbom python scripts/run_graduation_demo_report.py "
            "data/test_apks/limitation/simplify-obfuscated-app/simplify-obfuscated-app.apk "
            "--output-dir data/results/graduation-demo/simplify-obfuscated-offline "
            "--db-path data/reference_db/reference_features_calibrated_combined.sqlite "
            "--top 30 --include-uncertain"
        ),
        "open_first": [
            "data/results/graduation-demo/simplify-obfuscated-offline/demo-readiness.md",
            "data/results/report-limitation-simplify-obfuscated-app/report.html",
            "docs/evaluation/SIMPLIFY_OBFUSCATED_LIMITATION.md",
        ],
        "safe_claim": (
            "This is limitation evidence: the APK is processed, obfuscation risk is "
            "reported, and weak candidates stay low-confidence."
        ),
        "do_not_claim": "Do not include this limitation sample in source-validated accuracy metrics.",
    },
    {
        "id": "surprise-apk-wrapper",
        "title": "Surprise APK fallback wrapper",
        "purpose": "Handle a professor-provided APK without source code or network assumptions.",
        "apk_path": "path/to/app.apk",
        "readiness_json": "data/results/graduation-demo/controlled-gson-smoke/demo-readiness.json",
        "command": (
            "python scripts/run_graduation_demo_report.py path/to/app.apk "
            "--output-dir data/results/graduation-demo/app"
        ),
        "open_first": [
            "data/results/graduation-demo/app/demo-readiness.md",
            "data/results/graduation-demo/app/report.html",
            "data/results/graduation-demo/app/sbom.cdx.json",
        ],
        "safe_claim": (
            "This is APK-only evidence unless a source-validation artifact is supplied."
        ),
        "do_not_claim": "Do not claim full dependency recall or source validation for a surprise APK.",
    },
]


def main() -> int:
    case_summaries = [build_case_summary(case) for case in CASES]
    payload = {
        "source": "scripts/build_graduation_demo_rehearsal.py",
        "cases": case_summaries,
        "outputs": {
            "markdown": str(OUTPUT_MD),
            "json": str(OUTPUT_JSON),
        },
    }
    write_json(OUTPUT_JSON, payload)
    write_text(OUTPUT_MD, render_markdown(case_summaries))
    print(f"wrote {OUTPUT_MD}")
    print(f"wrote {OUTPUT_JSON}")
    return 0


def build_case_summary(case: dict[str, Any]) -> dict[str, Any]:
    summary = dict(case)
    report_path = case.get("report_json")
    if report_path:
        summary["report"] = summarize_report(Path(report_path))
    readiness_path = case.get("readiness_json")
    if readiness_path:
        summary["readiness"] = summarize_readiness(Path(readiness_path))
    source_validation_path = case.get("source_validation_md")
    if source_validation_path:
        summary["source_validation"] = summarize_source_validation(
            Path(source_validation_path)
        )
    summary["available"] = check_availability(case)
    return summary


def summarize_report(path: Path) -> dict[str, Any]:
    full_path = REPO_ROOT / path
    if not full_path.exists():
        return {"exists": False, "path": str(path)}
    payload = json.loads(full_path.read_text(encoding="utf-8"))
    apk = payload.get("apk") or {}
    manifest = apk.get("manifest_metadata") or {}
    components = payload.get("detected_components") or []
    native_libraries = apk.get("native_libraries") or []
    obfuscation = payload.get("obfuscation_risk") or {}
    osv = payload.get("osv")
    return {
        "exists": True,
        "path": str(path),
        "package_name": manifest.get("package_name") or "unknown",
        "version_name": manifest.get("version_name") or "unknown",
        "dex_files": len(apk.get("dex_files") or []),
        "native_libraries": len(native_libraries),
        "maven_components": len(components),
        "obfuscation_level": obfuscation.get("level") or "unknown",
        "osv": summarize_osv(osv),
    }


def summarize_osv(osv: dict[str, Any] | None) -> dict[str, Any]:
    if not osv:
        return {"mode": "not-run"}
    cves = sorted(
        {
            alias
            for result in osv.get("results") or []
            for vulnerability in result.get("vulnerabilities") or []
            for alias in vulnerability.get("aliases") or []
            if str(alias).startswith("CVE-")
        }
    )
    findings = []
    for result in osv.get("results") or []:
        vulnerabilities = result.get("vulnerabilities") or []
        if vulnerabilities:
            findings.append(
                {
                    "coordinate": result.get("coordinate"),
                    "version": result.get("version"),
                    "finding_confidence": result.get("finding_confidence"),
                    "vulnerabilities": len(vulnerabilities),
                }
            )
    return {
        "mode": "queried",
        "components": osv.get("components", 0),
        "vulnerable_components": osv.get("vulnerable_components", 0),
        "vulnerabilities": osv.get("vulnerabilities", 0),
        "confirmed_vulnerabilities": osv.get("confirmed_vulnerabilities", 0),
        "potential_vulnerabilities": osv.get("potential_vulnerabilities", 0),
        "severity_counts": osv.get("severity_counts") or {},
        "cves": cves,
        "findings": findings,
    }


def summarize_readiness(path: Path) -> dict[str, Any]:
    full_path = REPO_ROOT / path
    if not full_path.exists():
        return {"exists": False, "path": str(path)}
    payload = json.loads(full_path.read_text(encoding="utf-8"))
    return {
        "exists": True,
        "path": str(path),
        "status": payload.get("status"),
        "readiness_level": payload.get("readiness_level"),
        "demo_outcome": payload.get("demo_outcome"),
        "classification": payload.get("classification"),
        "classification_reason": payload.get("classification_reason"),
        "counts": payload.get("counts") or {},
        "osv_mode": (payload.get("osv") or {}).get("mode"),
        "source_validation_mode": (payload.get("source_validation") or {}).get("mode"),
        "supervisor_wording": payload.get("supervisor_wording"),
    }


def summarize_source_validation(path: Path) -> dict[str, Any]:
    full_path = REPO_ROOT / path
    if not full_path.exists():
        return {"exists": False, "path": str(path)}
    text = full_path.read_text(encoding="utf-8")
    row = parse_source_validation_summary(text)
    row["exists"] = True
    row["path"] = str(path)
    return row


def parse_source_validation_summary(text: str) -> dict[str, Any]:
    for line in text.splitlines():
        if not line.startswith("| SBOM components |"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 5:
            return {
                "components": int_or_zero(cells[1]),
                "confirmed": int_or_zero(cells[2]),
                "version_mismatch": int_or_zero(cells[3]),
                "missing": int_or_zero(cells[4]),
            }
    return {
        "components": 0,
        "confirmed": 0,
        "version_mismatch": 0,
        "missing": 0,
    }


def check_availability(case: dict[str, Any]) -> dict[str, bool]:
    keys = [
        "apk_path",
        "report_json",
        "source_validation_md",
        "readiness_json",
    ]
    return {
        key: (REPO_ROOT / Path(case[key])).exists()
        for key in keys
        if key in case and not str(case[key]).startswith("path/")
    }


def render_markdown(cases: list[dict[str, Any]]) -> str:
    lines = [
        "# Graduation Demo Rehearsal Pack",
        "",
        "This file is generated by `scripts/build_graduation_demo_rehearsal.py`.",
        "It is the short, practical playbook for a supervisor or graduation-day demo.",
        "",
        "## Demo Order",
        "",
        "1. Start with F-Droid to show the clean real-APK path.",
        "2. Open the Jackson fixture to show a positive CVE result.",
        "3. Show K-9 or Jitsi to explain honest partial/framework-boundary evidence.",
        "4. Show Simplify to discuss obfuscation limitations.",
        "5. Use the surprise-APK wrapper only if someone provides a new APK live.",
        "",
        "## One-Minute Opening",
        "",
        "I am not claiming that every APK can be perfectly reconstructed. The tool recovers APK-side evidence, maps it to Maven components when possible, emits a CycloneDX SBOM, optionally queries OSV, and separates clean, partial, boundary, and limitation cases. Source-validated claims only happen when I also have a source dependency tree for the same APK/source pair.",
        "",
        "## Case Matrix",
        "",
        "| Case | Purpose | APK evidence | Source validation | OSV | First file to open |",
        "|---|---|---:|---|---|---|",
    ]
    for case in cases:
        report = case.get("report") or {}
        source = case.get("source_validation") or {}
        readiness = case.get("readiness") or {}
        osv = report.get("osv") or {}
        source_text = source_validation_text(source)
        osv_text = osv_text_from_summary(osv)
        first_file = (case.get("open_first") or [""])[0]
        evidence = evidence_text(report, readiness)
        lines.append(
            "| {title} | {purpose} | {evidence} | {source} | {osv} | `{first}` |".format(
                title=case["title"],
                purpose=case["purpose"],
                evidence=evidence,
                source=source_text,
                osv=osv_text,
                first=first_file,
            )
        )

    lines.extend(["", "## Case Details", ""])
    for case in cases:
        lines.extend(render_case_detail(case))

    lines.extend(
        [
            "## Surprise APK Command",
            "",
            "Default offline-safe run:",
            "",
            "```powershell",
            "python scripts\\run_graduation_demo_report.py path\\to\\app.apk --output-dir data\\results\\graduation-demo\\app",
            "```",
            "",
            "Docker equivalent:",
            "",
            "```powershell",
            "docker compose run --rm apk-sbom python scripts/run_graduation_demo_report.py path/to/app.apk --output-dir data/results/graduation-demo/app",
            "```",
            "",
            "This wrapper is fail-soft by default for live demos. If the underlying report fails, it still writes `demo-readiness.md` with the exception and supervisor-safe wording, then exits successfully so the result is explainable. Use strict mode for automation:",
            "",
            "```powershell",
            "python scripts\\run_graduation_demo_report.py path\\to\\app.apk --output-dir data\\results\\graduation-demo\\app --strict-exit",
            "```",
            "",
            "Optional OSV run when network is available:",
            "",
            "```powershell",
            "python scripts\\run_graduation_demo_report.py path\\to\\app.apk --output-dir data\\results\\graduation-demo\\app-osv --query-osv",
            "```",
            "",
            "## Phrases To Use",
            "",
            "- This is APK-only evidence unless I provide a source-validation artifact.",
            "- The SBOM contains recovered Maven evidence and native files as hash-only components.",
            "- Confirmed source-validation rows mean the emitted Maven version matched the resolved source dependency tree.",
            "- Version mismatches are useful evidence, not a failure to hide.",
            "- OSV findings are only as strong as the component/version confidence and source-validation context.",
            "",
            "## Phrases To Avoid",
            "",
            "- Do not say the tool recovers every dependency from every APK.",
            "- Do not call partial rows clean.",
            "- Do not call native `.so` files Maven dependencies.",
            "- Do not claim source validation for a live surprise APK without source evidence.",
            "- Do not describe emitted Maven version confirmation rate as full dependency recall.",
            "",
            "## Verification Checklist",
            "",
            "- `python -m compileall src scripts tests`",
            "- `docker compose run --rm apk-sbom pytest tests/test_graduation_demo_report.py -q`",
            "- `python scripts/build_graduation_demo_rehearsal.py`",
            "- `git diff --check`",
            "",
            "## Generated Index",
            "",
            f"- JSON index: `{OUTPUT_JSON}`",
            "",
        ]
    )
    return "\n".join(lines)


def render_case_detail(case: dict[str, Any]) -> list[str]:
    report = case.get("report") or {}
    source = case.get("source_validation") or {}
    readiness = case.get("readiness") or {}
    lines = [
        f"### {case['title']}",
        "",
        f"- Purpose: {case['purpose']}",
        f"- APK: `{case.get('apk_path', 'n/a')}`",
        f"- Command: `{case.get('command', 'n/a')}`",
    ]
    if report.get("exists"):
        lines.extend(
            [
                f"- Package: `{report.get('package_name')}`",
                f"- DEX/native/components: {report.get('dex_files')} DEX, "
                f"{report.get('native_libraries')} native files, "
                f"{report.get('maven_components')} Maven components",
                f"- Obfuscation risk: {report.get('obfuscation_level')}",
                f"- OSV: {osv_text_from_summary(report.get('osv') or {})}",
            ]
        )
    if source.get("exists"):
        lines.append(f"- Source validation: {source_validation_text(source)}")
    if readiness.get("exists"):
        counts = readiness.get("counts") or {}
        lines.append(
            "- Readiness: {status}, {level}, {classification}; {maven} Maven candidates, "
            "{uncertain} candidate/uncertain/low-confidence".format(
                status=readiness.get("status"),
                level=readiness.get("readiness_level"),
                classification=readiness.get("classification"),
                maven=counts.get("maven_components", 0),
                uncertain=counts.get("uncertain_or_candidate_components", 0),
            )
        )
        if readiness.get("demo_outcome"):
            lines.append(f"- Demo outcome: {readiness.get('demo_outcome')}")
        if readiness.get("supervisor_wording"):
            lines.append(
                f"- Wrapper wording: {readiness.get('supervisor_wording')}"
            )
    lines.extend(
        [
            f"- Safe claim: {case['safe_claim']}",
            f"- Do not claim: {case['do_not_claim']}",
            "- Open first:",
        ]
    )
    lines.extend([f"  - `{path}`" for path in case.get("open_first") or []])
    lines.append("")
    return lines


def evidence_text(report: dict[str, Any], readiness: dict[str, Any]) -> str:
    if readiness.get("exists"):
        counts = readiness.get("counts") or {}
        return (
            f"{counts.get('maven_components', 0)} Maven, "
            f"{counts.get('native_libraries', 0)} native, "
            f"{readiness.get('classification')}"
        )
    if report.get("exists"):
        return (
            f"{report.get('maven_components')} Maven, "
            f"{report.get('native_libraries')} native, "
            f"{report.get('obfuscation_level')} obfuscation"
        )
    return "artifact missing"


def source_validation_text(source: dict[str, Any]) -> str:
    if not source.get("exists"):
        return "not source-validated"
    return (
        f"{source.get('confirmed', 0)}/{source.get('components', 0)} confirmed, "
        f"{source.get('version_mismatch', 0)} mismatches, "
        f"{source.get('missing', 0)} missing"
    )


def osv_text_from_summary(osv: dict[str, Any]) -> str:
    if osv.get("mode") == "not-run" or not osv:
        return "not run"
    vulnerabilities = int_or_zero(str(osv.get("vulnerabilities", 0)))
    confirmed = int_or_zero(str(osv.get("confirmed_vulnerabilities", 0)))
    potential = int_or_zero(str(osv.get("potential_vulnerabilities", 0)))
    if vulnerabilities == 0:
        return "0 vulnerabilities"
    return f"{vulnerabilities} findings ({confirmed} confirmed, {potential} potential)"


def int_or_zero(value: str) -> int:
    match = re.search(r"-?\d+", str(value))
    if not match:
        return 0
    return int(match.group(0))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    full_path = REPO_ROOT / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    full_path = REPO_ROOT / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
