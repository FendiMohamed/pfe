from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
from urllib.request import urlretrieve


FDROID_REPO_URL = "https://f-droid.org/repo"
DEFAULT_INDEX = Path("data/results/evaluation/fdroid-index-v2.json")
DEFAULT_APK_ROOT = Path("data/test_apks/real")
DEFAULT_REPORT_ROOT = Path("data/results/evaluation/real-apk-growth-batch-v2")
DEFAULT_SUMMARY_JSON = Path("data/results/evaluation/real-apk-growth-batch-v2.json")
DEFAULT_SUMMARY_DOC = Path("docs/evaluation/REAL_APK_GROWTH_BATCH_V2.md")
DEFAULT_DB_PATH = Path("data/reference_db/reference_features_calibrated_combined.sqlite")


DEFAULT_SELECTIONS = [
    {
        "package_name": "org.localsend.localsend_app",
        "slug": "localsend",
        "app": "LocalSend",
        "target_layer": "smoke-real",
        "validation_level": "L3-report-with-source-link",
        "classifications": [
            "flutter",
            "framework-boundary",
            "file-transfer",
            "modern",
            "native-so",
            "r8-likely",
        ],
        "reason": "Flutter/file-transfer app that exercises framework-boundary behavior and native artifacts.",
    },
    {
        "package_name": "de.blinkt.openvpn",
        "slug": "openvpn-for-android",
        "app": "OpenVPN for Android",
        "target_layer": "limitation",
        "validation_level": "L3-report-with-source-link",
        "classifications": [
            "native-heavy",
            "vpn-security",
            "source-linked",
            "large-apk",
            "native-so",
        ],
        "reason": "Native-heavy VPN/security case; useful for keeping native hash-only behavior separate from Maven accuracy.",
    },
    {
        "package_name": "com.kunzisoft.keepass.libre",
        "slug": "keepassdx",
        "app": "KeePassDX",
        "target_layer": "smoke-real",
        "validation_level": "L3-report-with-source-link",
        "classifications": [
            "security",
            "crypto-password",
            "native-so",
            "source-linked",
            "modern",
        ],
        "reason": "Security/password manager case with native code and a compact source tarball for a later proof bundle.",
    },
    {
        "package_name": "nodomain.freeyourgadget.gadgetbridge",
        "slug": "gadgetbridge",
        "app": "Gadgetbridge",
        "target_layer": "smoke-real",
        "validation_level": "L2-report-only-source-repo",
        "classifications": [
            "older-long-lived",
            "device-connectivity",
            "native-so",
            "source-linked",
        ],
        "reason": "Long-lived device-connectivity app that adds an older/legacy-style real APK family.",
    },
    {
        "package_name": "at.bitfire.davdroid",
        "slug": "davx5",
        "app": "DAVx5",
        "target_layer": "smoke-real",
        "validation_level": "L3-report-with-source-link",
        "classifications": [
            "sync-client",
            "modern",
            "androidx",
            "native-so",
            "source-linked",
        ],
        "reason": "Modern sync client with source tarball metadata and a likely non-trivial dependency tree.",
    },
    {
        "package_name": "net.typeblog.shelter",
        "slug": "shelter",
        "app": "Shelter",
        "target_layer": "smoke-real",
        "validation_level": "L3-report-with-source-link",
        "classifications": [
            "no-native",
            "simple-real",
            "security",
            "work-profile",
            "small-apk",
        ],
        "reason": "Small no-native security/work-profile app to balance the native-heavy batch members.",
    },
    {
        "package_name": "ru.wohlsoft.thextech.fdroid",
        "slug": "thextech",
        "app": "TheXTech",
        "target_layer": "limitation",
        "validation_level": "L3-report-with-source-link",
        "classifications": [
            "game",
            "native-heavy",
            "framework-boundary",
            "native-so",
        ],
        "reason": "Game/native-heavy case for the Unity/game-engine-style boundary, even though it is not Unity itself.",
    },
    {
        "package_name": "org.mozilla.fennec_fdroid",
        "slug": "fennec-fdroid",
        "app": "Fennec F-Droid",
        "target_layer": "smoke-real",
        "validation_level": "L3-report-with-source-link",
        "classifications": [
            "large-apk",
            "browser",
            "native-so",
            "modern",
            "multidex-likely",
        ],
        "reason": "Large browser APK that stress-tests extraction/reporting and broadens the modern/native coverage.",
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download a category-balanced F-Droid real APK smoke batch and generate reports.",
    )
    parser.add_argument("--index", default=str(DEFAULT_INDEX))
    parser.add_argument("--apk-root", default=str(DEFAULT_APK_ROOT))
    parser.add_argument("--report-root", default=str(DEFAULT_REPORT_ROOT))
    parser.add_argument("--summary-json", default=str(DEFAULT_SUMMARY_JSON))
    parser.add_argument("--summary-doc", default=str(DEFAULT_SUMMARY_DOC))
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument(
        "--selection-json",
        help="Optional JSON file containing a custom list under selections/apks/candidates.",
    )
    parser.add_argument("--package", action="append", help="Limit to one or more package names.")
    parser.add_argument("--slug", action="append", help="Limit to one or more selection slugs.")
    parser.add_argument("--skip-download", action="store_true", help="Require APK files to already exist.")
    parser.add_argument("--skip-report", action="store_true", help="Do not call apk-sbom generate-report.")
    parser.add_argument("--reuse-reports", action="store_true", help="Reuse existing report artifacts when present.")
    parser.add_argument("--skip-osv", action="store_true", help="Pass --skip-osv to generate-report.")
    parser.add_argument("--include-uncertain", action="store_true", help="Include uncertain matcher decisions.")
    parser.add_argument("--continue-on-error", action="store_true", help="Keep processing after a failure.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    selections = (
        load_selection_json(Path(args.selection_json))
        if args.selection_json
        else select_selections(args.package, args.slug)
    )
    selections = filter_selections(selections, args.package, args.slug)
    index = read_json(Path(args.index))
    result = collect_batch(
        index=index,
        selections=selections,
        apk_root=Path(args.apk_root),
        report_root=Path(args.report_root),
        db_path=Path(args.db_path),
        skip_download=args.skip_download,
        skip_report=args.skip_report,
        reuse_reports=args.reuse_reports,
        skip_osv=args.skip_osv,
        include_uncertain=args.include_uncertain,
        continue_on_error=args.continue_on_error,
    )
    write_outputs(result, Path(args.summary_json), Path(args.summary_doc))
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 1 if result["summary"]["failed"] and not args.continue_on_error else 0


def select_selections(package_names: list[str] | None, slugs: list[str] | None) -> list[dict[str, Any]]:
    return filter_selections(DEFAULT_SELECTIONS, package_names, slugs)


def load_selection_json(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    if isinstance(payload, list):
        selections = payload
    else:
        selections = (
            payload.get("selections")
            or payload.get("apks")
            or payload.get("candidates")
            or payload.get("rows")
        )
    if not isinstance(selections, list):
        raise ValueError(f"selection JSON must contain a list: {path}")
    normalized = [normalize_selection(item) for item in selections]
    if not normalized:
        raise ValueError(f"selection JSON has no selections: {path}")
    return normalized


def normalize_selection(item: dict[str, Any]) -> dict[str, Any]:
    required = ["package_name", "slug", "app"]
    missing = [field for field in required if not item.get(field)]
    if missing:
        raise ValueError(f"selection is missing required fields {missing}: {item}")
    return {
        "package_name": item["package_name"],
        "slug": item["slug"],
        "app": item["app"],
        "target_layer": item.get("target_layer", "smoke-real"),
        "validation_level": item.get("validation_level", "L3-report-with-source-link"),
        "classifications": list(item.get("classifications") or []),
        "reason": item.get("reason", "Custom F-Droid real APK selection."),
    }


def filter_selections(
    selections: list[dict[str, Any]],
    package_names: list[str] | None,
    slugs: list[str] | None,
) -> list[dict[str, Any]]:
    if package_names:
        packages = set(package_names)
        selections = [selection for selection in selections if selection["package_name"] in packages]
    if slugs:
        wanted_slugs = set(slugs)
        selections = [selection for selection in selections if selection["slug"] in wanted_slugs]
    if not selections:
        raise ValueError("no APK selections matched the requested filters")
    return selections


def collect_batch(
    *,
    index: dict[str, Any],
    selections: list[dict[str, Any]],
    apk_root: Path,
    report_root: Path,
    db_path: Path,
    skip_download: bool,
    skip_report: bool,
    reuse_reports: bool,
    skip_osv: bool,
    include_uncertain: bool,
    continue_on_error: bool,
) -> dict[str, Any]:
    apk_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    failures = 0
    for selection in selections:
        try:
            row = collect_one(
                index=index,
                selection=selection,
                apk_root=apk_root,
                report_root=report_root,
                db_path=db_path,
                skip_download=skip_download,
                skip_report=skip_report,
                reuse_reports=reuse_reports,
                skip_osv=skip_osv,
                include_uncertain=include_uncertain,
            )
        except Exception as exc:
            failures += 1
            if not continue_on_error:
                raise
            row = {
                "app": selection["app"],
                "package_name": selection["package_name"],
                "slug": selection["slug"],
                "status": "failed",
                "error": str(exc),
                "classifications": selection["classifications"],
                "target_layer": selection["target_layer"],
                "validation_level": selection["validation_level"],
                "reason": selection["reason"],
            }
        rows.append(row)

    successful = [row for row in rows if row.get("status") == "ok"]
    classes = sorted({item for row in successful for item in row["classifications"]})
    return {
        "schema_version": 1,
        "batch_id": "real-apk-growth-batch-v2",
        "source": "F-Droid index-v2",
        "policy": (
            "Report-only/smoke APKs stay out of source-validated accuracy metrics until "
            "matching source tags or tarballs, resolved dependency trees, generated reports, "
            "and source-validation outputs are complete."
        ),
        "summary": {
            "selected": len(rows),
            "succeeded": len(successful),
            "failed": failures,
            "classes_covered": classes,
            "apk_root": normalize_path(apk_root),
            "report_root": normalize_path(report_root),
        },
        "apks": rows,
    }


def collect_one(
    *,
    index: dict[str, Any],
    selection: dict[str, Any],
    apk_root: Path,
    report_root: Path,
    db_path: Path,
    skip_download: bool,
    skip_report: bool,
    reuse_reports: bool,
    skip_osv: bool,
    include_uncertain: bool,
) -> dict[str, Any]:
    package = index["packages"][selection["package_name"]]
    metadata = package.get("metadata", {})
    version = latest_version(package)
    file_info = version["file"]
    apk_url = fdroid_url(file_info["name"])
    slug = selection["slug"]
    apk_dir = apk_root / slug
    apk_dir.mkdir(parents=True, exist_ok=True)
    apk_path = apk_dir / f"{slug}.apk"

    if skip_download and not apk_path.exists():
        raise FileNotFoundError(f"missing APK while --skip-download is set: {apk_path}")
    if not skip_download and should_download(apk_path, file_info):
        download_file(apk_url, apk_path)

    computed_sha256 = sha256_file(apk_path)
    expected_sha256 = file_info.get("sha256")
    if expected_sha256 and computed_sha256.lower() != expected_sha256.lower():
        raise ValueError(f"SHA-256 mismatch for {apk_path}: expected {expected_sha256}, got {computed_sha256}")

    source_info = version.get("src") or {}
    source_name = source_info.get("name")
    source_tarball = {
        "url": fdroid_url(source_name) if source_name else None,
        "sha256": source_info.get("sha256"),
        "size": source_info.get("size"),
    }
    report_dir = report_root / f"report-real-{slug}"
    report_status = "skipped"
    report_error = None
    if reuse_reports and (report_dir / "report.json").exists() and (report_dir / "sbom.cdx.json").exists():
        report_status = "ok"
    elif not skip_report:
        report_status, report_error = generate_report(
            apk_path=apk_path,
            report_dir=report_dir,
            db_path=db_path,
            skip_osv=skip_osv,
            include_uncertain=include_uncertain,
        )
    report_summary = summarize_report(report_dir) if report_status == "ok" else {}

    row = {
        "status": "ok",
        "app": selection["app"],
        "package_name": selection["package_name"],
        "slug": slug,
        "version_name": version.get("manifest", {}).get("versionName"),
        "version_code": version.get("manifest", {}).get("versionCode"),
        "target_layer": selection["target_layer"],
        "validation_level": selection["validation_level"],
        "metric_eligibility": "excluded-from-source-validated-metrics",
        "proof_status": "report-generated" if report_status == "ok" else "apk-collected",
        "classifications": selection["classifications"],
        "reason": selection["reason"],
        "categories": metadata.get("categories", []),
        "license": metadata.get("license"),
        "source_repo": metadata.get("sourceCode"),
        "fdroid_package_url": f"https://f-droid.org/packages/{selection['package_name']}/",
        "apk": {
            "path": normalize_path(apk_path),
            "url": apk_url,
            "sha256": computed_sha256,
            "expected_sha256": expected_sha256,
            "size": apk_path.stat().st_size,
            "index_size": file_info.get("size"),
        },
        "source_tarball": source_tarball,
        "native_code": sorted(version.get("manifest", {}).get("nativecode", [])),
        "report": {
            "status": report_status,
            "error": report_error,
            "dir": normalize_path(report_dir),
            "json": normalize_path(report_dir / "report.json"),
            "html": normalize_path(report_dir / "report.html"),
            "sbom": normalize_path(report_dir / "sbom.cdx.json"),
            **report_summary,
        },
    }
    (apk_dir / "metadata.json").write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (apk_dir / "fdroid-index-entry.json").write_text(
        json.dumps({"metadata": metadata, "version": version}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return row


def latest_version(package: dict[str, Any]) -> dict[str, Any]:
    versions = package.get("versions", {})
    if not versions:
        raise ValueError("package has no versions")
    return max(
        versions.values(),
        key=lambda version: int(version.get("manifest", {}).get("versionCode", 0)),
    )


def should_download(path: Path, file_info: dict[str, Any]) -> bool:
    if not path.exists():
        return True
    expected_size = file_info.get("size")
    if expected_size and path.stat().st_size != int(expected_size):
        return True
    expected_sha256 = file_info.get("sha256")
    return bool(expected_sha256 and sha256_file(path).lower() != expected_sha256.lower())


def generate_report(
    *,
    apk_path: Path,
    report_dir: Path,
    db_path: Path,
    skip_osv: bool,
    include_uncertain: bool,
) -> tuple[str, str | None]:
    report_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "apk_sbom.cli",
        "generate-report",
        str(apk_path),
        "--output-dir",
        str(report_dir),
        "--db-path",
        str(db_path),
    ]
    if skip_osv:
        cmd.append("--skip-osv")
    if include_uncertain:
        cmd.append("--include-uncertain")
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        return "failed", (completed.stderr or completed.stdout).strip()
    return "ok", None


def summarize_report(report_dir: Path) -> dict[str, Any]:
    report = read_json(report_dir / "report.json")
    sbom = read_json(report_dir / "sbom.cdx.json")
    apk = report["apk"]
    return {
        "detected_component_count": len(report.get("detected_components", [])),
        "sbom_component_count": len(sbom.get("components", [])),
        "dex_file_count": len(apk.get("dex_files", [])),
        "has_multidex": bool(apk.get("has_multidex")),
        "native_library_count": len(apk.get("native_libraries", [])),
        "obfuscation_risk": report.get("obfuscation_risk"),
    }


def write_outputs(result: dict[str, Any], summary_json: Path, summary_doc: Path) -> None:
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_doc.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_doc.write_text(build_markdown(result), encoding="utf-8")


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Real APK Growth Batch V2",
        "",
        "This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.",
        "It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Selected APKs | {summary['selected']} |",
        f"| Succeeded | {summary['succeeded']} |",
        f"| Failed | {summary['failed']} |",
        f"| APK root | `{summary['apk_root']}` |",
        f"| Report root | `{summary['report_root']}` |",
        f"| Classes covered | {', '.join(summary['classes_covered'])} |",
        "",
        "## APKs",
        "",
        "| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |",
        "|---|---|---|---|---:|---:|---:|---|---|---|",
    ]
    for row in result["apks"]:
        version = f"{row.get('version_name') or 'n/a'} ({row.get('version_code') or 'n/a'})"
        report = row.get("report", {})
        report_value = report.get("status", row.get("status", "unknown"))
        if report.get("json"):
            report_value = f"{report_value}: `{report['json']}`"
        dex_count = report.get("dex_file_count", "n/a")
        native_count = report.get("native_library_count", "n/a")
        component_count = report.get("sbom_component_count", "n/a")
        lines.append(
            "| "
            f"{row['app']} | "
            f"`{row['package_name']}` | "
            f"{version} | "
            f"{row['target_layer']} | "
            f"{dex_count} | "
            f"{native_count} | "
            f"{component_count} | "
            f"{', '.join(row['classifications'])} | "
            f"{report_value} | "
            f"{row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Proof-Gate Follow-Up",
            "",
            "- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.",
            "- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.",
            "- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.",
            "",
            "## Remaining Admission Work",
            "",
            "- Promote none of these rows into source-validated metrics from this file alone.",
            "- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.",
            "- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.",
            "- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.",
            "",
        ]
    )
    return "\n".join(lines)


def fdroid_url(name: str | None) -> str | None:
    if not name:
        return None
    return FDROID_REPO_URL + name


def download_file(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Path | str) -> str:
    return Path(path).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
