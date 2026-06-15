from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_DB_PATH = Path("data/reference_db/reference_features_calibrated_combined.sqlite")
DEFAULT_OUTPUT_DIR = Path("data/results/evaluation")

PHASE2_R8_TARGETS: list[dict[str, str]] = [
    {
        "slug": "gson",
        "coordinate": "com.google.code.gson:gson",
        "version": "2.8.9",
    },
    {
        "slug": "jackson-databind",
        "coordinate": "com.fasterxml.jackson.core:jackson-databind",
        "version": "2.13.5",
    },
    {
        "slug": "okhttp",
        "coordinate": "com.squareup.okhttp3:okhttp",
        "version": "4.10.0",
    },
    {
        "slug": "retrofit",
        "coordinate": "com.squareup.retrofit2:retrofit",
        "version": "2.8.1",
    },
    {
        "slug": "commons-codec",
        "coordinate": "commons-codec:commons-codec",
        "version": "1.16.1",
    },
]

PHASE2_R8_VARIANTS: list[dict[str, str]] = [
    {"variant": "r8-optimize", "category": "r8-optimize"},
    {"variant": "r8-shrink-optimize", "category": "r8-shrink-optimize"},
    {"variant": "r8-repackage", "category": "r8-package-flattening"},
    {"variant": "r8-inline-stress", "category": "r8-inline-stress"},
]

PHASE2_R8_RENAME_SHRINK_FILL_TARGETS: list[dict[str, str]] = [
    {
        "slug": "gson",
        "coordinate": "com.google.code.gson:gson",
        "version": "2.8.9",
    },
    {
        "slug": "commons-codec",
        "coordinate": "commons-codec:commons-codec",
        "version": "1.16.1",
    },
]

PHASE2_R8_RENAME_SHRINK_VARIANTS: list[dict[str, str]] = [
    {"variant": "r8-rename", "category": "r8-rename"},
    {"variant": "r8-shrink", "category": "r8-shrink"},
]

DATASET_GROWTH_CLEAR_FIXTURES: list[dict[str, Any]] = [
    {
        "name": "generated-okio-jvm-3-0-0-clear",
        "category": "kotlin-networking-version-band",
        "coordinate": "com.squareup.okio:okio-jvm",
        "version": "3.0.0",
        "variant": "clear",
        "classification_tags": ["artifact-family", "kotlin-era", "networking"],
    },
    {
        "name": "generated-okio-jvm-3-6-0-clear",
        "category": "kotlin-networking-version-band",
        "coordinate": "com.squareup.okio:okio-jvm",
        "version": "3.6.0",
        "variant": "clear",
        "classification_tags": ["artifact-family", "kotlin-era", "networking"],
    },
    {
        "name": "generated-okio-jvm-3-7-0-clear",
        "category": "kotlin-networking-version-band",
        "coordinate": "com.squareup.okio:okio-jvm",
        "version": "3.7.0",
        "variant": "clear",
        "classification_tags": ["artifact-family", "kotlin-era", "networking"],
    },
    {
        "name": "generated-okhttp-4-9-0-clear",
        "category": "networking-version-band",
        "coordinate": "com.squareup.okhttp3:okhttp",
        "version": "4.9.0",
        "variant": "clear",
    },
    {
        "name": "generated-okhttp-4-12-0-clear",
        "category": "networking-version-band",
        "coordinate": "com.squareup.okhttp3:okhttp",
        "version": "4.12.0",
        "variant": "clear",
    },
    {
        "name": "generated-ktor-client-core-jvm-2-3-12-clear",
        "category": "modern-kotlin-framework",
        "coordinate": "io.ktor:ktor-client-core-jvm",
        "version": "2.3.12",
        "variant": "clear",
        "classification_tags": ["framework-ktor", "kotlin-era", "networking"],
    },
    {
        "name": "generated-ktor-client-okhttp-jvm-2-3-12-clear",
        "category": "modern-kotlin-framework",
        "coordinate": "io.ktor:ktor-client-okhttp-jvm",
        "version": "2.3.12",
        "variant": "clear",
        "classification_tags": ["framework-ktor", "kotlin-era", "networking"],
    },
    {
        "name": "generated-ktor-http-jvm-2-3-12-clear",
        "category": "modern-kotlin-framework",
        "coordinate": "io.ktor:ktor-http-jvm",
        "version": "2.3.12",
        "variant": "clear",
        "classification_tags": ["framework-ktor", "kotlin-era", "networking"],
    },
    {
        "name": "generated-ktor-io-jvm-2-3-12-clear",
        "category": "modern-kotlin-framework",
        "coordinate": "io.ktor:ktor-io-jvm",
        "version": "2.3.12",
        "variant": "clear",
        "classification_tags": ["framework-ktor", "kotlin-era", "networking"],
    },
    {
        "name": "generated-ktor-utils-jvm-2-3-12-clear",
        "category": "modern-kotlin-framework",
        "coordinate": "io.ktor:ktor-utils-jvm",
        "version": "2.3.12",
        "variant": "clear",
        "classification_tags": ["framework-ktor", "kotlin-era", "networking"],
    },
]

DATASET_GROWTH_R8_VARIANTS: list[dict[str, str]] = [
    {"variant": "r8-rename", "category": "kotlin-networking-r8-rename"},
    {"variant": "r8-shrink", "category": "kotlin-networking-r8-shrink"},
    {"variant": "r8-optimize", "category": "kotlin-networking-r8-optimize"},
    {"variant": "r8-shrink-optimize", "category": "kotlin-networking-r8-shrink-optimize"},
    {"variant": "r8-repackage", "category": "kotlin-networking-r8-repackage"},
    {"variant": "r8-inline-stress", "category": "kotlin-networking-r8-inline-stress"},
]


def dataset_growth_fixtures() -> list[dict[str, Any]]:
    fixtures = [
        {
            **fixture,
            "phase": "dataset-growth-v2",
        }
        for fixture in DATASET_GROWTH_CLEAR_FIXTURES
    ]
    fixtures.extend(
        {
            "name": f"generated-okio-jvm-3-7-0-{variant['variant']}",
            "category": variant["category"],
            "coordinate": "com.squareup.okio:okio-jvm",
            "version": "3.7.0",
            "variant": variant["variant"],
            "phase": "dataset-growth-v2",
            "classification_tags": ["artifact-family", "kotlin-era", "networking"],
        }
        for variant in DATASET_GROWTH_R8_VARIANTS
    )
    fixtures.extend(
        [
            {
                "name": "generated-multi-okhttp-4-12-0-okio-jvm-3-7-0-clear-multidex",
                "category": "modern-networking-multidex",
                "coordinate": "com.squareup.okhttp3:okhttp",
                "version": "4.12.0",
                "variant": "clear",
                "phase": "dataset-growth-v2",
                "multidex_mode": "file-per-class",
                "dependencies": ["com.squareup.okio:okio-jvm@3.7.0"],
                "classification_tags": ["artifact-family", "kotlin-era", "networking"],
            },
            {
                "name": "generated-multi-ktor-okhttp-jvm-2-3-12-stack-clear-multidex",
                "category": "modern-framework-multidex",
                "coordinate": "io.ktor:ktor-client-okhttp-jvm",
                "version": "2.3.12",
                "variant": "clear",
                "phase": "dataset-growth-v2",
                "multidex_mode": "file-per-class",
                "dependencies": [
                    "io.ktor:ktor-client-core-jvm@2.3.12",
                    "io.ktor:ktor-http-jvm@2.3.12",
                    "io.ktor:ktor-io-jvm@2.3.12",
                    "io.ktor:ktor-utils-jvm@2.3.12",
                    "com.squareup.okhttp3:okhttp@4.12.0",
                    "com.squareup.okio:okio-jvm@3.7.0",
                ],
                "classification_tags": ["framework-ktor", "kotlin-era", "networking"],
            },
        ]
    )
    return fixtures


def phase2_r8_matrix_fixtures() -> list[dict[str, str]]:
    fixtures: list[dict[str, str]] = []
    for target in PHASE2_R8_RENAME_SHRINK_FILL_TARGETS:
        version_slug = target["version"].replace(".", "-")
        for variant in PHASE2_R8_RENAME_SHRINK_VARIANTS:
            fixtures.append(
                {
                    "name": (
                        f"generated-{target['slug']}-{version_slug}-"
                        f"{variant['variant']}"
                    ),
                    "category": variant["category"],
                    "coordinate": target["coordinate"],
                    "version": target["version"],
                    "variant": variant["variant"],
                    "phase": "r8-phase-2-matrix",
                }
            )
    for target in PHASE2_R8_TARGETS:
        version_slug = target["version"].replace(".", "-")
        for variant in PHASE2_R8_VARIANTS:
            fixtures.append(
                {
                    "name": (
                        f"generated-{target['slug']}-{version_slug}-"
                        f"{variant['variant']}"
                    ),
                    "category": variant["category"],
                    "coordinate": target["coordinate"],
                    "version": target["version"],
                    "variant": variant["variant"],
                    "phase": "r8-phase-2-matrix",
                }
            )
    return fixtures


FIXTURES: list[dict[str, Any]] = [
    {
        "name": "generated-gson-2-8-5-clear",
        "category": "clear-version-band",
        "coordinate": "com.google.code.gson:gson",
        "version": "2.8.5",
        "variant": "clear",
    },
    {
        "name": "generated-gson-2-8-6-clear",
        "category": "clear-version-band",
        "coordinate": "com.google.code.gson:gson",
        "version": "2.8.6",
        "variant": "clear",
    },
    {
        "name": "generated-jackson-databind-2-12-7-1-clear",
        "category": "clear-version-band",
        "coordinate": "com.fasterxml.jackson.core:jackson-databind",
        "version": "2.12.7.1",
        "variant": "clear",
    },
    {
        "name": "generated-jackson-databind-2-13-5-clear",
        "category": "clear-version-band",
        "coordinate": "com.fasterxml.jackson.core:jackson-databind",
        "version": "2.13.5",
        "variant": "clear",
    },
    {
        "name": "generated-jackson-databind-2-15-2-clear",
        "category": "clear-version-band",
        "coordinate": "com.fasterxml.jackson.core:jackson-databind",
        "version": "2.15.2",
        "variant": "clear",
    },
    {
        "name": "generated-okhttp-4-8-0-clear",
        "category": "clear-version-band",
        "coordinate": "com.squareup.okhttp3:okhttp",
        "version": "4.8.0",
        "variant": "clear",
    },
    {
        "name": "generated-okhttp-4-10-0-clear",
        "category": "clear-version-band",
        "coordinate": "com.squareup.okhttp3:okhttp",
        "version": "4.10.0",
        "variant": "clear",
    },
    {
        "name": "generated-retrofit-2-8-1-clear",
        "category": "clear-version-band",
        "coordinate": "com.squareup.retrofit2:retrofit",
        "version": "2.8.1",
        "variant": "clear",
    },
    {
        "name": "generated-commons-codec-1-15-clear",
        "category": "clear-version-band",
        "coordinate": "commons-codec:commons-codec",
        "version": "1.15",
        "variant": "clear",
    },
    {
        "name": "generated-commons-codec-1-16-0-clear",
        "category": "clear-version-band",
        "coordinate": "commons-codec:commons-codec",
        "version": "1.16.0",
        "variant": "clear",
    },
    {
        "name": "generated-okhttp-4-10-0-r8-rename",
        "category": "r8-rename",
        "coordinate": "com.squareup.okhttp3:okhttp",
        "version": "4.10.0",
        "variant": "r8-rename",
        "phase": "r8-phase-2-matrix",
    },
    {
        "name": "generated-okhttp-4-10-0-r8-shrink",
        "category": "r8-shrink",
        "coordinate": "com.squareup.okhttp3:okhttp",
        "version": "4.10.0",
        "variant": "r8-shrink",
        "phase": "r8-phase-2-matrix",
    },
    {
        "name": "generated-retrofit-2-8-1-r8-rename",
        "category": "r8-rename",
        "coordinate": "com.squareup.retrofit2:retrofit",
        "version": "2.8.1",
        "variant": "r8-rename",
        "phase": "r8-phase-2-matrix",
    },
    {
        "name": "generated-retrofit-2-8-1-r8-shrink",
        "category": "r8-shrink",
        "coordinate": "com.squareup.retrofit2:retrofit",
        "version": "2.8.1",
        "variant": "r8-shrink",
        "phase": "r8-phase-2-matrix",
    },
    {
        "name": "generated-jackson-databind-2-13-5-r8-rename",
        "category": "r8-rename",
        "coordinate": "com.fasterxml.jackson.core:jackson-databind",
        "version": "2.13.5",
        "variant": "r8-rename",
        "phase": "r8-phase-2-matrix",
    },
    {
        "name": "generated-jackson-databind-2-13-5-r8-shrink",
        "category": "r8-shrink",
        "coordinate": "com.fasterxml.jackson.core:jackson-databind",
        "version": "2.13.5",
        "variant": "r8-shrink",
        "phase": "r8-phase-2-matrix",
    },
    *phase2_r8_matrix_fixtures(),
    {
        "name": "generated-multi-gson-2-8-6-commons-codec-1-16-0-clear-multidex",
        "category": "multi-library-multidex",
        "coordinate": "com.google.code.gson:gson",
        "version": "2.8.6",
        "variant": "clear",
        "multidex_mode": "file-per-class",
        "dependencies": ["commons-codec:commons-codec@1.16.0"],
    },
    {
        "name": "generated-multi-okhttp-4-10-0-okio-jvm-3-7-0-clear-multidex",
        "category": "multi-library-multidex",
        "coordinate": "com.squareup.okhttp3:okhttp",
        "version": "4.10.0",
        "variant": "clear",
        "multidex_mode": "file-per-class",
        "dependencies": ["com.squareup.okio:okio-jvm@3.7.0"],
    },
    {
        "name": "generated-multi-retrofit-2-8-1-okhttp-4-9-1-clear-multidex",
        "category": "multi-library-multidex",
        "coordinate": "com.squareup.retrofit2:retrofit",
        "version": "2.8.1",
        "variant": "clear",
        "multidex_mode": "file-per-class",
        "dependencies": ["com.squareup.okhttp3:okhttp@4.9.1"],
    },
    {
        "name": "generated-multi-jackson-2-13-5-gson-2-8-6-clear-multidex",
        "category": "multi-library-multidex",
        "coordinate": "com.fasterxml.jackson.core:jackson-databind",
        "version": "2.13.5",
        "variant": "clear",
        "multidex_mode": "file-per-class",
        "dependencies": ["com.google.code.gson:gson@2.8.6"],
    },
    *dataset_growth_fixtures(),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and evaluate a larger generated controlled APK batch by category.",
    )
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--skip-report-generation", action="store_true")
    parser.add_argument(
        "--reuse-existing",
        action="store_true",
        help="Reuse existing APK, ground-truth, and report files instead of rebuilding fixtures.",
    )
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument(
        "--phase",
        action="append",
        default=[],
        help="Run only fixtures from this phase. Can be repeated.",
    )
    parser.add_argument(
        "--fixture",
        action="append",
        default=[],
        help="Run only this fixture name. Can be repeated.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    fixtures = selected_fixtures(args)
    results = []
    for fixture in fixtures:
        result = run_fixture(
            fixture,
            Path(args.db_path),
            skip_report=args.skip_report_generation,
            reuse_existing=args.reuse_existing,
        )
        results.append(result)
        if result["status"] != "ok" and not args.continue_on_error:
            write_outputs(results, Path(args.output_dir))
            return 1

    evaluation = run_evaluation()
    payload = write_outputs(results, Path(args.output_dir), evaluation=evaluation)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if all(result["status"] == "ok" for result in results) else 1


def selected_fixtures(args: argparse.Namespace) -> list[dict[str, Any]]:
    phases = set(args.phase or [])
    names = set(args.fixture or [])
    fixtures = [
        fixture
        for fixture in FIXTURES
        if (not phases or fixture.get("phase", "baseline-generated-category-batch") in phases)
        and (not names or fixture["name"] in names)
    ]
    if not fixtures:
        raise SystemExit("No generated APK fixtures matched the requested filters.")
    return fixtures


def run_fixture(
    fixture: dict[str, Any],
    db_path: Path,
    *,
    skip_report: bool,
    reuse_existing: bool = False,
) -> dict[str, Any]:
    name = fixture["name"]
    result: dict[str, Any] = {
        "name": name,
        "category": fixture["category"],
        "coordinate": fixture["coordinate"],
        "version": fixture["version"],
        "variant": fixture["variant"],
        "phase": fixture.get("phase", "baseline-generated-category-batch"),
        "dependencies": fixture.get("dependencies", []),
        "multidex_mode": fixture.get("multidex_mode", "auto"),
        "status": "ok",
    }
    try:
        if reuse_existing:
            result["apk_path"] = f"data/test_apks/{name}.apk"
            result["ground_truth_path"] = f"data/test_apks/{name}.ground-truth.json"
            if not Path(result["apk_path"]).exists():
                raise FileNotFoundError(f"Existing APK not found: {result['apk_path']}")
            if not Path(result["ground_truth_path"]).exists():
                raise FileNotFoundError(
                    f"Existing ground truth not found: {result['ground_truth_path']}"
                )
            enrich_ground_truth(Path(result["ground_truth_path"]), fixture)
            if not skip_report:
                report_dir = Path("data/results") / f"report-{name}"
                result["report_dir"] = str(report_dir)
                result["report_path"] = str(report_dir / "report.json")
                if not Path(result["report_path"]).exists():
                    raise FileNotFoundError(f"Existing report not found: {result['report_path']}")
            result["reused_existing"] = True
            return result

        build_command = [
            sys.executable,
            "scripts/build_controlled_apk.py",
            "--coordinate",
            fixture["coordinate"],
            "--version",
            fixture["version"],
            "--variant",
            fixture["variant"],
            "--name",
            name,
            "--multidex-mode",
            fixture.get("multidex_mode", "auto"),
        ]
        for dependency in fixture.get("dependencies", []):
            build_command.extend(["--dependency", dependency])
        build_output = run_command(build_command)
        result["build_stdout"] = build_output.stdout
        result["apk_path"] = f"data/test_apks/{name}.apk"
        result["ground_truth_path"] = f"data/test_apks/{name}.ground-truth.json"
        enrich_ground_truth(Path(result["ground_truth_path"]), fixture)

        if not skip_report:
            report_dir = Path("data/results") / f"report-{name}"
            report_command = [
                sys.executable,
                "-m",
                "apk_sbom.cli",
                "generate-report",
                result["apk_path"],
                "--output-dir",
                str(report_dir),
                "--db-path",
                str(db_path),
                "--skip-osv",
                "--top",
                "30",
            ]
            report_output = run_command(report_command)
            result["report_stdout"] = report_output.stdout
            result["report_dir"] = str(report_dir)
            result["report_path"] = str(report_dir / "report.json")
    except Exception as exc:  # noqa: BLE001 - batch must preserve failure evidence
        result["status"] = "failed"
        result["error"] = str(exc)
    return result


def enrich_ground_truth(path: Path, fixture: dict[str, Any]) -> None:
    payload = read_json(path)
    payload["generated_batch"] = "category-expansion-v1"
    payload["generated_phase"] = fixture.get("phase", "baseline-generated-category-batch")
    payload["evaluation_category"] = fixture["category"]
    payload["classification_tags"] = classification_tags(fixture)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def classification_tags(fixture: dict[str, Any]) -> list[str]:
    tags = ["controlled", "generated", fixture["category"], fixture["variant"]]
    tags.extend(str(tag) for tag in fixture.get("classification_tags", []))
    if fixture.get("phase"):
        tags.append(str(fixture["phase"]))
    if fixture.get("dependencies"):
        tags.append("multi-library")
    if fixture.get("multidex_mode") == "file-per-class":
        tags.append("multidex")
    if fixture["coordinate"].startswith("androidx."):
        tags.append("androidx")
    elif fixture["coordinate"].startswith("com.squareup"):
        tags.append("networking")
    elif fixture["coordinate"].startswith("com.fasterxml"):
        tags.append("serialization")
    elif fixture["coordinate"].startswith("com.google.code.gson"):
        tags.append("serialization")
    return sorted(set(tags))


def run_evaluation() -> dict[str, Any]:
    output = run_command([sys.executable, "scripts/evaluate_controlled_reports.py"])
    evaluation = read_json(Path("data/results/evaluation/controlled-evaluation.json"))
    return {"stdout": output.stdout, "evaluation": evaluation}


def write_outputs(
    results: list[dict[str, Any]],
    output_dir: Path,
    *,
    evaluation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = evaluation_rows_for_generated(results, evaluation["evaluation"] if evaluation else None)
    payload = {
        "summary": summarize(results, rows),
        "fixtures": results,
        "evaluation_rows": rows,
    }
    json_path = output_dir / "generated-apk-category-batch.json"
    md_path = output_dir / "generated-apk-category-batch.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    return payload


def evaluation_rows_for_generated(
    results: list[dict[str, Any]],
    evaluation: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not evaluation:
        return []
    by_apk = {
        normalize_path(result["apk_path"]): result
        for result in results
        if result.get("apk_path")
    }
    rows = []
    for row in evaluation.get("rows", []):
        fixture = by_apk.get(normalize_path(row["apk_path"]))
        if not fixture:
            continue
        rows.append(
            {
                **row,
                "category": fixture["category"],
                "fixture_name": fixture["name"],
                "phase": fixture.get("phase", "baseline-generated-category-batch"),
                **report_risk_fields(fixture),
            }
        )
    return rows


def summarize(results: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    success = [result for result in results if result["status"] == "ok"]
    failed = [result for result in results if result["status"] != "ok"]
    categories = sorted({result["category"] for result in results})
    expected = len(rows)
    component_hits = sum(1 for row in rows if row.get("component_detected"))
    version_hits = sum(1 for row in rows if row.get("version_detected"))
    candidate_hits = sum(1 for row in rows if row.get("candidate_version_correct"))
    return {
        "batch_scope": batch_scope(results),
        "planned_fixtures": len(results),
        "built_and_reported": len(success),
        "failed": len(failed),
        "categories": categories,
        "expected_components": expected,
        "component_recall": safe_divide(component_hits, expected),
        "version_recall": safe_divide(version_hits, expected),
        "exact_version_recall": safe_divide(version_hits, expected),
        "candidate_version_recall": safe_divide(candidate_hits, expected),
        "confidence_distribution": count_values(rows, "candidate_confidence"),
        "obfuscation_risk_levels": count_values(rows, "obfuscation_risk_level"),
        "category_summary": summarize_by_category(rows),
    }


def batch_scope(results: list[dict[str, Any]]) -> dict[str, Any]:
    phases = sorted({result.get("phase", "baseline-generated-category-batch") for result in results})
    return {
        "phases": phases,
        "filtered": set(phases) != {
            "baseline-generated-category-batch",
            "dataset-growth-v2",
            "r8-phase-2-matrix",
        },
    }


def summarize_by_category(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["category"], []).append(row)
    summary = {}
    for category, category_rows in sorted(grouped.items()):
        expected = len(category_rows)
        summary[category] = {
            "expected_components": expected,
            "component_recall": safe_divide(
                sum(1 for row in category_rows if row.get("component_detected")),
                expected,
            ),
            "version_recall": safe_divide(
                sum(1 for row in category_rows if row.get("version_detected")),
                expected,
            ),
            "exact_version_recall": safe_divide(
                sum(1 for row in category_rows if row.get("version_detected")),
                expected,
            ),
            "candidate_version_recall": safe_divide(
                sum(1 for row in category_rows if row.get("candidate_version_correct")),
                expected,
            ),
            "confidence_distribution": count_values(category_rows, "candidate_confidence"),
            "obfuscation_risk_levels": count_values(category_rows, "obfuscation_risk_level"),
        }
    return summary


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Generated APK Category Batch",
        "",
        "This batch expands the controlled/generated APK evidence by category. "
        "It is still synthetic ground truth, so it complements but does not replace real source-validated APKs.",
        "",
        "## Summary",
        "",
        f"- Planned fixtures: {summary['planned_fixtures']}",
        f"- Built and reported: {summary['built_and_reported']}",
        f"- Failed: {summary['failed']}",
        f"- Expected Maven components: {summary['expected_components']}",
        f"- Component recall: {summary['component_recall']:.3f}",
        f"- Exact version recall: {summary['exact_version_recall']:.3f}",
        f"- Candidate version recall: {summary['candidate_version_recall']:.3f}",
        f"- Confidence distribution: {format_counter(summary['confidence_distribution'])}",
        f"- Obfuscation risk levels: {format_counter(summary['obfuscation_risk_levels'])}",
        "",
        "## Category Summary",
        "",
        "| Category | Expected components | Component recall | Exact version recall | Candidate version recall | Confidence distribution | Risk levels |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for category, row in summary["category_summary"].items():
        lines.append(
            f"| {category} | {row['expected_components']} | "
            f"{row['component_recall']:.3f} | {row['exact_version_recall']:.3f} | "
            f"{row['candidate_version_recall']:.3f} | "
            f"{format_counter(row['confidence_distribution'])} | "
            f"{format_counter(row['obfuscation_risk_levels'])} |"
        )

    lines.extend(
        [
            "",
            "## Fixture Results",
            "",
            "| Category | Fixture | Ground truth | Component | Version | Candidate | Decision | Risk |",
            "|---|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in payload["evaluation_rows"]:
        lines.append(
            f"| {row['category']} | `{row['fixture_name']}` | "
            f"`{row['coordinate']}@{row['version']}` | "
            f"{str(row['component_detected']).lower()} | "
            f"{str(row['version_detected']).lower()} | "
            f"{str(row['candidate_version_correct']).lower()} | "
            f"{row['candidate_decision']}/{row['candidate_confidence']} | "
            f"{row.get('obfuscation_risk_level', 'unknown')} |"
        )

    failed = [fixture for fixture in payload["fixtures"] if fixture["status"] != "ok"]
    if failed:
        lines.extend(["", "## Failures", "", "| Fixture | Error |", "|---|---|"])
        for fixture in failed:
            lines.append(f"| `{fixture['name']}` | {fixture.get('error', '')} |")
    lines.append("")
    return "\n".join(lines)


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def report_risk_fields(fixture: dict[str, Any]) -> dict[str, Any]:
    report_path = fixture.get("report_path")
    if not report_path or not Path(report_path).exists():
        return {
            "obfuscation_risk_level": "missing",
            "obfuscation_risk_score": 0.0,
            "r8_diagnostic_statuses": {},
        }
    report = read_json(Path(report_path))
    diagnostics = report.get("obfuscation_diagnostics", {})
    diagnostic_statuses = {
        key: value.get("status")
        for key, value in diagnostics.items()
        if isinstance(value, dict) and "status" in value
    }
    risk = report.get("obfuscation_risk", {})
    return {
        "obfuscation_risk_level": risk.get("level", "unknown"),
        "obfuscation_risk_score": risk.get("score", 0.0),
        "r8_diagnostic_statuses": diagnostic_statuses,
    }


def count_values(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, "missing"))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def format_counter(values: dict[str, int]) -> str:
    if not values:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in values.items())


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


if __name__ == "__main__":
    raise SystemExit(main())
