from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve


DEFAULT_BATCH_JSON = Path("data/results/evaluation/real-apk-growth-batch-v2.json")
DEFAULT_SOURCE_ROOT = Path("data/source/real-apk-growth-batch-v2")
DEFAULT_VALIDATION_ROOT = Path("data/results/source-validation/real-apk-growth-batch-v2")
DEFAULT_DOC = Path("docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md")
DEFAULT_JSON = Path("data/results/evaluation/real-apk-growth-batch-v2-proof-status.json")
DEFAULT_RESCUE_PROFILE_JSON = Path("configs/real_apk_blocker_rescue_profiles.json")

COMMON_CONFIGURATIONS = [
    "releaseRuntimeClasspath",
    "debugRuntimeClasspath",
    "fdroidReleaseRuntimeClasspath",
    "fdroidDebugRuntimeClasspath",
    "freeReleaseRuntimeClasspath",
    "freeDebugRuntimeClasspath",
    "fullReleaseRuntimeClasspath",
    "fullDebugRuntimeClasspath",
    "blueReleaseRuntimeClasspath",
    "fossReleaseRuntimeClasspath",
    "standardReleaseRuntimeClasspath",
    "playReleaseRuntimeClasspath",
    "googleplayReleaseRuntimeClasspath",
    "prodReleaseRuntimeClasspath",
    "mainlineReleaseRuntimeClasspath",
]

COMMON_DEPENDENCY_TASKS = [
    ":app:dependencies",
    ":mobile:dependencies",
    ":main:dependencies",
    "dependencies",
]

SLUG_CONFIGURATIONS = {
    "floccus": [
        "releaseRuntimeClasspath",
        "debugRuntimeClasspath",
        "fdroidReleaseRuntimeClasspath",
    ],
    "opencloud": [
        "originalReleaseRuntimeClasspath",
        "qaReleaseRuntimeClasspath",
        "originalDebugRuntimeClasspath",
        "qaDebugRuntimeClasspath",
        "releaseRuntimeClasspath",
        "debugRuntimeClasspath",
    ],
    "localsend": ["prodReleaseRuntimeClasspath", "releaseRuntimeClasspath"],
    "davx5": ["oseReleaseRuntimeClasspath", "releaseRuntimeClasspath"],
    "keepassdx": ["libreReleaseRuntimeClasspath", "releaseRuntimeClasspath"],
    "shelter": ["releaseRuntimeClasspath", "debugRuntimeClasspath"],
    "fennec-fdroid": ["fennecReleaseRuntimeClasspath", "releaseRuntimeClasspath"],
    "openvpn-for-android": [
        "uiOvpn23ReleaseRuntimeClasspath",
        "uiOvpn2ReleaseRuntimeClasspath",
        "releaseRuntimeClasspath",
    ],
    "gadgetbridge": [
        "mainlineReleaseRuntimeClasspath",
        "fdroidReleaseRuntimeClasspath",
        "releaseRuntimeClasspath",
    ],
}

SLUG_DEPENDENCY_TASKS = {
    "floccus": [":app:dependencies"],
    "opencloud": [":opencloudApp:dependencies"],
    "davx5": [":app-ose:dependencies", "dependencies"],
    "openvpn-for-android": [":main:dependencies", "dependencies"],
    "shelter": [":app:dependencies", "dependencies"],
    "keepassdx": [":app:dependencies", "dependencies"],
    "gadgetbridge": [":app:dependencies", "dependencies"],
}

VALIDATION_COPY_SLUGS = {"openvpn-for-android", "shelter", "opencloud"}
VALIDATION_COPY_ONLY_SLUGS: set[str] = set()
STRICT_CONFIGURATION_SLUGS: set[str] = set()
SLUG_GRADLE_COMMANDS: dict[str, list[str]] = {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Advance the real APK growth batch through source/proof-bundle gates together.",
    )
    parser.add_argument("--batch-json", default=str(DEFAULT_BATCH_JSON))
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--validation-root", default=str(DEFAULT_VALIDATION_ROOT))
    parser.add_argument("--output-doc", default=str(DEFAULT_DOC))
    parser.add_argument("--output-json", default=str(DEFAULT_JSON))
    parser.add_argument("--slug", action="append", help="Limit to selected APK slugs.")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-extract", action="store_true")
    parser.add_argument("--attempt-gradle", action="store_true")
    parser.add_argument("--gradle-timeout", type=int, default=300)
    parser.add_argument("--rescue-profile-json", default=str(DEFAULT_RESCUE_PROFILE_JSON))
    parser.add_argument(
        "--reuse-existing-proofs",
        action="store_true",
        help="Rebuild the combined proof status from validation_root/<slug>/proof-status.json files.",
    )
    parser.add_argument("--continue-on-error", action="store_true")
    return parser


def read_rescue_profiles(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = read_json(path)
    return payload.get("assignments", {})


def apply_rescue_profile_hints(rows: list[dict[str, Any]], assignments: dict[str, Any]) -> None:
    for row in rows:
        slug = row.get("slug")
        profile = assignments.get(slug) or {}
        configs = profile.get("configurations") or []
        tasks = profile.get("tasks") or []
        if configs:
            if profile.get("strict_configurations"):
                SLUG_CONFIGURATIONS[slug] = [str(item) for item in configs]
            else:
                SLUG_CONFIGURATIONS[slug] = list(
                    dict.fromkeys([str(item) for item in configs] + SLUG_CONFIGURATIONS.get(slug, []))
                )
        if tasks:
            SLUG_DEPENDENCY_TASKS[slug] = list(
                dict.fromkeys([str(item) for item in tasks] + SLUG_DEPENDENCY_TASKS.get(slug, []))
            )
        if profile.get("validation_copy"):
            VALIDATION_COPY_SLUGS.add(slug)
        if profile.get("validation_copy_only"):
            VALIDATION_COPY_ONLY_SLUGS.add(slug)
        if profile.get("strict_configurations"):
            STRICT_CONFIGURATION_SLUGS.add(slug)
        gradle_command_hint = profile.get("gradle_command")
        if isinstance(gradle_command_hint, str):
            SLUG_GRADLE_COMMANDS[slug] = [gradle_command_hint]
        elif isinstance(gradle_command_hint, list):
            SLUG_GRADLE_COMMANDS[slug] = [str(item) for item in gradle_command_hint]


def main() -> int:
    args = build_parser().parse_args()
    batch = read_json(Path(args.batch_json))
    rows = batch["apks"]
    if args.slug:
        wanted = set(args.slug)
        rows = [row for row in rows if row["slug"] in wanted]
    rescue_profiles = read_rescue_profiles(Path(args.rescue_profile_json))
    apply_rescue_profile_hints(rows, rescue_profiles)
    if args.reuse_existing_proofs:
        result = reuse_existing_proofs(
            rows=rows,
            source_root=Path(args.source_root),
            validation_root=Path(args.validation_root),
            continue_on_error=args.continue_on_error,
        )
    else:
        result = advance_batch(
            rows=rows,
            source_root=Path(args.source_root),
            validation_root=Path(args.validation_root),
            skip_download=args.skip_download,
            skip_extract=args.skip_extract,
            attempt_gradle=args.attempt_gradle,
            gradle_timeout=args.gradle_timeout,
            continue_on_error=args.continue_on_error,
        )
    write_outputs(result, Path(args.output_json), Path(args.output_doc))
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 1 if result["summary"]["failed"] and not args.continue_on_error else 0


def advance_batch(
    *,
    rows: list[dict[str, Any]],
    source_root: Path,
    validation_root: Path,
    skip_download: bool,
    skip_extract: bool,
    attempt_gradle: bool,
    gradle_timeout: int,
    continue_on_error: bool,
) -> dict[str, Any]:
    source_root.mkdir(parents=True, exist_ok=True)
    validation_root.mkdir(parents=True, exist_ok=True)
    proofs: list[dict[str, Any]] = []
    failures = 0
    for row in rows:
        try:
            proofs.append(
                advance_one(
                    row=row,
                    source_root=source_root,
                    validation_root=validation_root,
                    skip_download=skip_download,
                    skip_extract=skip_extract,
                    attempt_gradle=attempt_gradle,
                    gradle_timeout=gradle_timeout,
                )
            )
        except Exception as exc:
            failures += 1
            if not continue_on_error:
                raise
            proofs.append(
                {
                    "slug": row["slug"],
                    "app": row["app"],
                    "package_name": row["package_name"],
                    "status": "failed",
                    "error": str(exc),
                    "target_layer": row["target_layer"],
                    "validation_level": row["validation_level"],
                }
            )
    return build_batch_result(
        proofs=proofs,
        failures=failures,
        source_root=source_root,
        validation_root=validation_root,
    )


def reuse_existing_proofs(
    *,
    rows: list[dict[str, Any]],
    source_root: Path,
    validation_root: Path,
    continue_on_error: bool,
) -> dict[str, Any]:
    proofs: list[dict[str, Any]] = []
    failures = 0
    for row in rows:
        proof_path = validation_root / row["slug"] / "proof-status.json"
        if proof_path.exists():
            proof = read_json(proof_path)
            if normalize_proof_metric_eligibility(proof):
                proof_path.write_text(
                    json.dumps(proof, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            proofs.append(proof)
            continue
        failures += 1
        if not continue_on_error:
            raise FileNotFoundError(proof_path)
        proofs.append(
            {
                "slug": row["slug"],
                "app": row["app"],
                "package_name": row["package_name"],
                "status": "failed",
                "error": f"missing proof status: {proof_path}",
                "target_layer": row["target_layer"],
                "validation_level": row["validation_level"],
            }
        )
    return build_batch_result(
        proofs=proofs,
        failures=failures,
        source_root=source_root,
        validation_root=validation_root,
    )


def build_batch_result(
    *,
    proofs: list[dict[str, Any]],
    failures: int,
    source_root: Path,
    validation_root: Path,
) -> dict[str, Any]:
    gradle_ok = [proof for proof in proofs if proof.get("dependency_tree", {}).get("status") == "ok"]
    source_available = [proof for proof in proofs if proof.get("source", {}).get("status") == "ok"]
    source_validation_ok = [proof for proof in proofs if proof.get("source_validation", {}).get("status") == "ok"]
    return {
        "schema_version": 1,
        "batch_id": "real-apk-growth-batch-v2-proof-status",
        "policy": "This is a batch proof-gate status artifact. Do not promote rows into source-validated metrics unless dependency_tree.status and source_validation.status are ok.",
        "summary": {
            "selected": len(proofs),
            "source_available": len(source_available),
            "dependency_tree_ok": len(gradle_ok),
            "source_validation_ok": len(source_validation_ok),
            "failed": failures,
            "source_root": normalize_path(source_root),
            "validation_root": normalize_path(validation_root),
        },
        "proofs": proofs,
    }


def advance_one(
    *,
    row: dict[str, Any],
    source_root: Path,
    validation_root: Path,
    skip_download: bool,
    skip_extract: bool,
    attempt_gradle: bool,
    gradle_timeout: int,
) -> dict[str, Any]:
    slug = row["slug"]
    work_dir = source_root / slug
    validation_dir = validation_root / slug
    work_dir.mkdir(parents=True, exist_ok=True)
    validation_dir.mkdir(parents=True, exist_ok=True)
    source_tarball = row.get("source_tarball", {})
    source_url = source_tarball.get("url") or derive_fdroid_source_tarball_url(row)
    source_path = work_dir / "source.tar.gz"
    source_status = "missing-source-tarball"
    source_error = None
    if source_url:
        if not skip_download and should_download(source_path, source_tarball):
            download_file(source_url, source_path)
        if source_path.exists():
            computed = sha256_file(source_path)
            expected = source_tarball.get("sha256")
            if expected and computed.lower() != expected.lower():
                raise ValueError(f"source SHA-256 mismatch for {slug}: expected {expected}, got {computed}")
            source_status = "ok"
        else:
            source_error = "source tarball not downloaded"

    extract_dir = work_dir / "source"
    if source_status == "ok" and not skip_extract:
        if not extract_dir.exists() or not any(extract_dir.iterdir()):
            extract_dir.mkdir(parents=True, exist_ok=True)
            safe_extract_tar(source_path, extract_dir)

    gradle_roots = find_gradle_roots(extract_dir) if extract_dir.exists() else []
    validation_gradle_roots = prepare_validation_gradle_roots(
        slug=slug,
        extract_dir=extract_dir,
        validation_dir=validation_dir,
    )
    dependency_tree = {"status": "not-attempted", "reason": "run with --attempt-gradle"}
    if attempt_gradle:
        active_gradle_roots = (
            [root["root"] for root in validation_gradle_roots]
            if slug in VALIDATION_COPY_ONLY_SLUGS and validation_gradle_roots
            else [root["root"] for root in validation_gradle_roots] + gradle_roots
        )
        dependency_tree = attempt_dependency_tree(
            slug=slug,
            gradle_roots=active_gradle_roots,
            validation_root_metadata=validation_root_metadata(validation_gradle_roots),
            validation_dir=validation_dir,
            timeout=gradle_timeout,
        )

    source_validation = attempt_source_validation(
        row=row,
        dependency_tree=dependency_tree,
        validation_dir=validation_dir,
    )
    proof_status = classify_status(
        source_status,
        dependency_tree.get("status"),
        source_validation,
        dependency_tree,
    )
    proof = {
        "slug": slug,
        "app": row["app"],
        "package_name": row["package_name"],
        "version_name": row.get("version_name"),
        "version_code": row.get("version_code"),
        "target_layer": row["target_layer"],
        "validation_level": row["validation_level"],
        "metric_eligibility": metric_eligibility_for(proof_status),
        "proof_status": proof_status,
        "source": {
            "status": source_status,
            "error": source_error,
            "repo": row.get("source_repo"),
            "tarball_url": source_url,
            "tarball_url_source": "fdroid-index" if source_tarball.get("url") else "derived-fdroid-version-url",
            "tarball_path": normalize_path(source_path) if source_path.exists() else None,
            "expected_sha256": source_tarball.get("sha256"),
            "size": source_path.stat().st_size if source_path.exists() else None,
            "extracted_dir": normalize_path(extract_dir) if extract_dir.exists() else None,
            "gradle_roots": [normalize_path(path) for path in gradle_roots],
            "validation_gradle_roots": [
                {
                    "root": normalize_path(item["root"]),
                    "reason": item["reason"],
                    "modified_files": [normalize_path(path) for path in item.get("modified_files", [])],
                }
                for item in validation_gradle_roots
            ],
        },
        "apk_report": row.get("report", {}),
        "dependency_tree": dependency_tree,
        "source_validation": source_validation,
    }
    (validation_dir / "proof-status.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return proof


def attempt_source_validation(
    *,
    row: dict[str, Any],
    dependency_tree: dict[str, Any],
    validation_dir: Path,
) -> dict[str, Any]:
    if dependency_tree.get("status") != "ok":
        return {
            "status": "blocked-until-dependency-tree",
            "reason": "Run validate-source-deps after a runtime dependency tree is captured.",
        }
    sbom_path = row.get("report", {}).get("sbom")
    tree_path = dependency_tree.get("tree_path")
    if not sbom_path or not Path(sbom_path).exists():
        return {"status": "blocked", "reason": "generated SBOM artifact is missing"}
    if not tree_path or not Path(tree_path).exists():
        return {"status": "blocked", "reason": "dependency tree artifact is missing"}

    output_dir = validation_dir / "source-validation"
    cmd = [
        sys.executable,
        "-m",
        "apk_sbom.cli",
        "validate-source-deps",
        "--sbom",
        sbom_path,
        "--dependency-tree",
        tree_path,
        "--output-dir",
        str(output_dir),
    ]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        return {
            "status": "failed",
            "reason": (completed.stderr or completed.stdout).strip(),
            "output_dir": normalize_path(output_dir),
        }

    validation_json = output_dir / "source-validation.json"
    validation_markdown = output_dir / "source-validation.md"
    payload = read_json(validation_json) if validation_json.exists() else {}
    return {
        "status": "ok",
        "output_dir": normalize_path(output_dir),
        "validation_json": normalize_path(validation_json),
        "validation_markdown": normalize_path(validation_markdown),
        "sbom_components": payload.get("sbom_components"),
        "confirmed": payload.get("confirmed"),
        "version_mismatches": payload.get("version_mismatches"),
        "missing": payload.get("missing"),
    }


def derive_fdroid_source_tarball_url(row: dict[str, Any]) -> str | None:
    apk_url = row.get("apk", {}).get("url")
    package_name = row.get("package_name")
    version_code = row.get("version_code")
    if not apk_url or not package_name or not version_code:
        return None
    prefix = f"https://f-droid.org/repo/{package_name}_{version_code}"
    if not apk_url.startswith(prefix):
        return None
    return f"{prefix}_src.tar.gz"


def prepare_validation_gradle_roots(
    *,
    slug: str,
    extract_dir: Path,
    validation_dir: Path,
) -> list[dict[str, Any]]:
    if slug not in VALIDATION_COPY_SLUGS or not extract_dir.exists():
        return []
    source_project_root = single_extracted_project_root(extract_dir)
    if not source_project_root:
        return []
    if slug == "openvpn-for-android":
        return [prepare_openvpn_validation_copy(source_project_root, validation_dir)]
    if slug == "shelter":
        return [prepare_shelter_validation_copy(source_project_root, validation_dir)]
    if slug == "opencloud":
        return [prepare_opencloud_validation_copy(source_project_root, validation_dir)]
    if slug == "owncloud":
        return [prepare_owncloud_validation_copy(source_project_root, validation_dir)]
    if slug == "waistline":
        return [prepare_waistline_validation_copy(source_project_root, validation_dir)]
    if slug == "odysee":
        return [prepare_odysee_validation_copy(source_project_root, validation_dir)]
    if slug == "baby-books":
        return [prepare_baby_books_validation_copy(source_project_root, validation_dir)]
    if slug == "radarweather":
        return [prepare_radarweather_validation_copy(source_project_root, validation_dir)]
    if slug == "simplelogin":
        return [prepare_simplelogin_validation_copy(source_project_root, validation_dir)]
    if slug == "omni-notes":
        return [prepare_omni_notes_validation_copy(source_project_root, validation_dir)]
    if slug == "openkeychain":
        return [prepare_openkeychain_validation_copy(source_project_root, validation_dir)]
    if slug == "todo-agenda":
        return [prepare_todo_agenda_validation_copy(source_project_root, validation_dir)]
    if slug in {"dolidroid", "radiodroid", "poet-assistant"}:
        return [prepare_jcenter_repository_validation_copy(source_project_root, validation_dir, slug)]
    return []


def single_extracted_project_root(extract_dir: Path) -> Path | None:
    children = [path for path in extract_dir.iterdir() if path.is_dir()]
    if len(children) == 1:
        return children[0]
    if any((extract_dir / name).exists() for name in ("settings.gradle", "settings.gradle.kts", "build.gradle", "build.gradle.kts")):
        return extract_dir
    return None


def prepare_openvpn_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / "validation-source-openvpn-no-native",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    main_build = destination / "main" / "build.gradle.kts"
    if main_build.exists():
        text = main_build.read_text(encoding="utf-8")
        patched = text.replace(
            '    // Also update runcoverity.sh\n    ndkVersion = "29.0.14206865"\n',
            "    // Validation copy: native CMake/NDK config disabled for dependency-tree capture.\n",
        )
        patched = patched.replace(
            """        externalNativeBuild {
            cmake {
                //arguments+= "-DCMAKE_VERBOSE_MAKEFILE=1"
            }
        }
""",
            "        // Validation copy: externalNativeBuild disabled.\n",
        )
        patched = patched.replace(
            """    externalNativeBuild {
        cmake {
            path = File("${projectDir}/src/main/cpp/CMakeLists.txt")
        }
    }
""",
            "    // Validation copy: externalNativeBuild disabled.\n",
        )
        if patched != text:
            main_build.write_text(patched, encoding="utf-8")
            modified_files.append(main_build)
    local_properties = destination / "local.properties"
    if local_properties.exists():
        lines = local_properties.read_text(encoding="utf-8").splitlines()
        patched_lines = [
            line
            for line in lines
            if not line.startswith("ndk.dir=") and not line.startswith("ndk-location=")
        ]
        if patched_lines != lines:
            local_properties.write_text("\n".join(patched_lines) + "\n", encoding="utf-8")
            modified_files.append(local_properties)
    return {
        "root": destination,
        "reason": "Validation copy disables native CMake/NDK configuration so Gradle can resolve the Java/Kotlin runtime dependency tree in the Docker image without an Android NDK.",
        "modified_files": modified_files,
    }


def prepare_shelter_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / "validation-source-shelter-app-only",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    settings = destination / "settings.gradle"
    settings.write_text("rootProject.name = 'shelter-validation'\ninclude ':app'\n", encoding="utf-8")
    modified_files.append(settings)
    root_build = destination / "build.gradle"
    if root_build.exists():
        text = root_build.read_text(encoding="utf-8")
        patched = text.replace(
            "classpath 'com.android.tools.build:gradle:8.1.2'",
            "classpath 'com.android.tools.build:gradle:8.13.2'",
        )
        if patched != text:
            root_build.write_text(patched, encoding="utf-8")
            modified_files.append(root_build)
    app_build = destination / "app" / "build.gradle"
    if app_build.exists():
        text = app_build.read_text(encoding="utf-8")
        patched = text.replace(
            "    jcenter {\n",
            '    maven {\n        url "https://jcenter.bintray.com"\n',
        )
        patched = patched.replace(
            "    debugImplementation project(path: ':setup-wizard-lib', configuration: 'gingerbreadCompatDebugRuntimeElements')\n",
            "    // Validation copy: omitted incomplete local setup-wizard-lib project dependency.\n",
        )
        patched = patched.replace(
            "    releaseImplementation project(path: ':setup-wizard-lib', configuration: 'gingerbreadCompatReleaseRuntimeElements')\n",
            "    // Validation copy: omitted incomplete local setup-wizard-lib project dependency.\n",
        )
        if patched != text:
            app_build.write_text(patched, encoding="utf-8")
            modified_files.append(app_build)
    return {
        "root": destination,
        "reason": "Validation copy adds missing settings.gradle, upgrades the Android Gradle plugin and jcenter declaration only for Docker Gradle compatibility, and omits the incomplete local SetupWizardLibrary project wiring to capture Shelter app Maven runtime dependencies.",
        "modified_files": modified_files,
    }


def prepare_opencloud_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / "validation-source-opencloud-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    root_build = destination / "build.gradle"
    if root_build.exists():
        text = root_build.read_text(encoding="utf-8")
        patched = text.replace(
            "    alias libs.plugins.sonarqube\n"
            "    alias libs.plugins.ksp apply false\n"
            "    alias libs.plugins.detekt\n",
            "    // Validation copy: analysis/codegen plugins disabled for dependency-tree capture.\n",
        )
        patched = patched.replace(
            '    apply plugin: "com.google.devtools.ksp"\n',
            '    // Validation copy: KSP disabled for dependency-tree capture.\n',
        )
        patched = patched.replace(
            '    apply plugin: "io.gitlab.arturbosch.detekt"\n',
            '    // Validation copy: Detekt disabled for dependency-tree capture.\n',
        )
        if patched != text:
            root_build.write_text(patched, encoding="utf-8")
            modified_files.append(root_build)
    for build_file in destination.rglob("build.gradle"):
        text = build_file.read_text(encoding="utf-8")
        patched = patch_opencloud_module_build(text)
        if build_file.name == "build.gradle" and build_file.parent.name == "opencloudApp":
            patched = (
                "// Validation copy: output-name helper expects this legacy property.\n"
                "ext.archivesBaseName = 'opencloudApp'\n"
                + patched
            )
        if patched != text:
            build_file.write_text(patched, encoding="utf-8")
            modified_files.append(build_file)
    return {
        "root": destination,
        "reason": "Validation copy disables OpenCloud KSP/Kotlin/Parcelize/Detekt/Sonar build-time plugins that use Gradle APIs incompatible with the current Docker Gradle fallback; runtime dependency declarations are preserved for source-validation tree capture.",
        "modified_files": modified_files,
    }


def patch_opencloud_module_build(text: str) -> str:
    lines = text.splitlines()
    patched_lines: list[str] = []
    skip_block_depth = 0
    for line in lines:
        stripped = line.strip()
        if skip_block_depth:
            skip_block_depth += line.count("{") - line.count("}")
            if skip_block_depth <= 0:
                skip_block_depth = 0
            continue
        if stripped == "apply plugin: 'com.google.devtools.ksp'":
            patched_lines.append("// Validation copy: KSP plugin disabled for dependency-tree capture.")
            continue
        if stripped in {"apply plugin: 'kotlin-android'", "apply plugin: 'kotlin-parcelize'"}:
            patched_lines.append("// Validation copy: Kotlin build plugin disabled for dependency-tree capture.")
            continue
        if stripped == "ksp {":
            skip_block_depth = 1
            patched_lines.append("// Validation copy: KSP configuration omitted for runtime dependency-tree capture.")
            continue
        if stripped == "kotlinOptions {":
            skip_block_depth = 1
            patched_lines.append("// Validation copy: Kotlin compiler options omitted for dependency-tree capture.")
            continue
        if stripped.startswith("ksp ") or stripped.startswith("ksp("):
            patched_lines.append("// Validation copy: KSP dependency omitted for runtime dependency-tree capture.")
            continue
        if stripped.startswith("detektPlugins "):
            patched_lines.append("// Validation copy: Detekt dependency omitted for runtime dependency-tree capture.")
            continue
        if stripped.startswith("tasks.withType(io.gitlab.arturbosch.detekt.Detekt)"):
            skip_block_depth = line.count("{") - line.count("}")
            patched_lines.append("// Validation copy: Detekt task configuration omitted for dependency-tree capture.")
            if skip_block_depth <= 0:
                skip_block_depth = 0
            continue
        patched_lines.append(line)
    return "\n".join(patched_lines) + ("\n" if text.endswith("\n") else "")


def prepare_owncloud_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / "validation-source-owncloud-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    root_build = destination / "build.gradle"
    if root_build.exists():
        text = root_build.read_text(encoding="utf-8")
        patched = patch_owncloud_root_build(text)
        if patched != text:
            root_build.write_text(patched, encoding="utf-8")
            modified_files.append(root_build)
    for build_file in destination.rglob("build.gradle"):
        text = build_file.read_text(encoding="utf-8")
        patched = patch_opencloud_module_build(text)
        if build_file.name == "build.gradle" and build_file.parent.name == "owncloudApp":
            patched = (
                "// Validation copy: output-name helper expects this legacy property.\n"
                "ext.archivesBaseName = 'owncloudApp'\n"
                + patched
            )
        if patched != text:
            build_file.write_text(patched, encoding="utf-8")
            modified_files.append(build_file)
    return {
        "root": destination,
        "reason": "Validation copy disables ownCloud Kotlin/KSP/Parcelize/Ktlint/Detekt/Sonar/CycloneDX build-time wiring that fails before runtime dependency-tree capture; runtime implementation/api dependencies and local project module links are preserved.",
        "modified_files": modified_files,
    }


def patch_owncloud_root_build(text: str) -> str:
    lines = text.splitlines()
    patched_lines: list[str] = []
    skip_block_depth = 0
    for line in lines:
        stripped = line.strip()
        if skip_block_depth:
            skip_block_depth += line.count("{") - line.count("}")
            if skip_block_depth <= 0:
                skip_block_depth = 0
            continue
        if stripped.startswith("alias libs.plugins."):
            patched_lines.append("    // Validation copy: root plugin alias disabled for dependency-tree capture.")
            continue
        if stripped.startswith('apply plugin: "com.google.devtools.ksp"'):
            patched_lines.append('    // Validation copy: KSP plugin disabled for dependency-tree capture.')
            continue
        if stripped.startswith('apply plugin: "org.jlleitschuh.gradle.ktlint"'):
            patched_lines.append('    // Validation copy: Ktlint plugin disabled for dependency-tree capture.')
            continue
        if stripped.startswith('apply plugin: "org.sonarqube"'):
            patched_lines.append('    // Validation copy: SonarQube plugin disabled for dependency-tree capture.')
            continue
        if stripped.startswith('apply plugin: "io.gitlab.arturbosch.detekt"'):
            patched_lines.append('    // Validation copy: Detekt plugin disabled for dependency-tree capture.')
            continue
        if stripped == "sonarqube {":
            skip_block_depth = 1
            patched_lines.append("// Validation copy: SonarQube configuration omitted for dependency-tree capture.")
            continue
        patched_lines.append(line)
    return "\n".join(patched_lines) + ("\n" if text.endswith("\n") else "")


def prepare_simplelogin_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    project_root = source_root / "SimpleLogin"
    if not project_root.exists():
        project_root = source_root
    destination = recreate_validation_copy(
        source_root=project_root,
        destination=validation_dir / "validation-source-simplelogin-detekt-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    root_build = destination / "build.gradle"
    if root_build.exists():
        text = root_build.read_text(encoding="utf-8")
        patched = patch_simplelogin_root_build(text)
        if patched != text:
            root_build.write_text(patched, encoding="utf-8")
            modified_files.append(root_build)
    return {
        "root": destination,
        "reason": "Validation copy disables the SimpleLogin Detekt build-time analysis plugin/configuration that requires removed Gradle ConfigureUtil APIs; runtime dependency declarations are preserved for source-validation tree capture.",
        "modified_files": modified_files,
    }


def patch_simplelogin_root_build(text: str) -> str:
    lines = text.splitlines()
    patched_lines: list[str] = []
    skip_block_depth = 0
    for line in lines:
        stripped = line.strip()
        if skip_block_depth:
            skip_block_depth += line.count("{") - line.count("}")
            if skip_block_depth <= 0:
                skip_block_depth = 0
            continue
        if stripped.startswith('id("io.gitlab.arturbosch.detekt")'):
            patched_lines.append("    // Validation copy: Detekt plugin disabled for dependency-tree capture.")
            continue
        if stripped == "detekt {":
            skip_block_depth = 1
            patched_lines.append("// Validation copy: Detekt configuration omitted for dependency-tree capture.")
            continue
        patched_lines.append(line)
    return "\n".join(patched_lines) + ("\n" if text.endswith("\n") else "")


def prepare_omni_notes_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / "validation-source-omni-notes-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    root_build = destination / "build.gradle"
    if root_build.exists():
        text = root_build.read_text(encoding="utf-8")
        patched = patch_omni_notes_root_build(text)
        if patched != text:
            root_build.write_text(patched, encoding="utf-8")
            modified_files.append(root_build)
    app_build = destination / "omniNotes" / "build.gradle"
    if app_build.exists():
        text = app_build.read_text(encoding="utf-8")
        patched = patch_omni_notes_app_build(text)
        if patched != text:
            app_build.write_text(patched, encoding="utf-8")
            modified_files.append(app_build)
    return {
        "root": destination,
        "reason": "Validation copy disables Omni Notes SonarQube/test-logger/Jacoco build-time analysis wiring that uses Gradle APIs incompatible with the current Docker Gradle lanes; runtime implementation/api dependencies are preserved for source-validation tree capture.",
        "modified_files": modified_files,
    }


def patch_omni_notes_root_build(text: str) -> str:
    patched_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if "org.sonarsource.scanner.gradle:sonarqube-gradle-plugin" in stripped:
            patched_lines.append("        // Validation copy: SonarQube plugin classpath disabled for dependency-tree capture.")
            continue
        if "com.adarshr:gradle-test-logger-plugin" in stripped:
            patched_lines.append("        // Validation copy: test-logger plugin classpath disabled for dependency-tree capture.")
            continue
        patched_lines.append(line)
    return "\n".join(patched_lines) + ("\n" if text.endswith("\n") else "")


def patch_omni_notes_app_build(text: str) -> str:
    lines = text.splitlines()
    patched_lines: list[str] = []
    skip_block_depth = 0
    for line in lines:
        stripped = line.strip()
        if skip_block_depth:
            skip_block_depth += line.count("{") - line.count("}")
            if skip_block_depth <= 0:
                skip_block_depth = 0
            continue
        if stripped == "apply plugin: 'jacoco'":
            patched_lines.append("// Validation copy: Jacoco plugin disabled for dependency-tree capture.")
            continue
        if stripped == "jacoco {":
            skip_block_depth = 1
            patched_lines.append("// Validation copy: Jacoco configuration omitted for dependency-tree capture.")
            continue
        if stripped.startswith("task jacocoTestReport("):
            skip_block_depth = line.count("{") - line.count("}")
            patched_lines.append("// Validation copy: Jacoco report task omitted for dependency-tree capture.")
            if skip_block_depth <= 0:
                skip_block_depth = 0
            continue
        if stripped == "apply plugin: 'com.adarshr.test-logger'":
            patched_lines.append("// Validation copy: test-logger plugin disabled for dependency-tree capture.")
            continue
        if stripped.startswith("tasks.withType(Test).configureEach"):
            skip_block_depth = line.count("{") - line.count("}")
            patched_lines.append("// Validation copy: test task logging/Jacoco wiring omitted for dependency-tree capture.")
            if skip_block_depth <= 0:
                skip_block_depth = 0
            continue
        patched_lines.append(line)
    return "\n".join(patched_lines) + ("\n" if text.endswith("\n") else "")


def prepare_waistline_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    android_source_root = source_root / "platforms" / "android"
    if not android_source_root.exists():
        android_source_root = source_root
    destination = recreate_validation_copy(
        source_root=android_source_root,
        destination=validation_dir / "validation-source-waistline-cordova-android-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    local_properties = destination / "local.properties"
    local_properties.write_text("sdk.dir=/opt/android-sdk\nsdk-location=/opt/android-sdk\n", encoding="utf-8")
    modified_files.append(local_properties)
    cdv_config = destination / "cdv-gradle-config.json"
    if cdv_config.exists():
        config_payload = json.loads(cdv_config.read_text(encoding="utf-8"))
        if config_payload.get("MIN_BUILD_TOOLS_VERSION") != "36.0.0":
            config_payload["MIN_BUILD_TOOLS_VERSION"] = "36.0.0"
            cdv_config.write_text(json.dumps(config_payload, indent=2) + "\n", encoding="utf-8")
            modified_files.append(cdv_config)
    cordova_gradle = destination / "CordovaLib" / "cordova.gradle"
    if cordova_gradle.exists():
        text = cordova_gradle.read_text(encoding="utf-8")
        patched = text
        if "import groovy.xml.XmlParser" not in patched:
            patched = patched.replace(
                "import java.util.regex.Pattern\n",
                "import java.util.regex.Pattern\nimport groovy.xml.XmlParser\n",
            )
        if patched != text:
            cordova_gradle.write_text(patched, encoding="utf-8")
            modified_files.append(cordova_gradle)
    barcode_gradle = destination / "phonegap-plugin-barcodescanner" / "line-barcodescanner.gradle"
    if barcode_gradle.exists():
        text = barcode_gradle.read_text(encoding="utf-8")
        patched = text.replace(
            "    jcenter()\n",
            '    maven {\n        url "https://jcenter.bintray.com"\n    }\n',
        )
        if patched != text:
            barcode_gradle.write_text(patched, encoding="utf-8")
            modified_files.append(barcode_gradle)
    return {
        "root": destination,
        "reason": "Validation copy clones only the Cordova Android Gradle project, adds Docker Android SDK local.properties, imports the Cordova Groovy XML parser class, aligns Cordova build-tools metadata with Docker build-tools 36.0.0, and replaces a removed plugin jcenter() repository call with the archived Maven URL; runtime dependency declarations are preserved for source-validation tree capture.",
        "modified_files": modified_files,
    }


def prepare_odysee_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / "validation-source-odysee-cordova-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files = patch_cordova_runtime_tree_copy(destination)
    return {
        "root": destination,
        "reason": "Validation copy keeps Odysee's Cordova Android project intact, adds Docker Android SDK local.properties, and imports the Cordova Groovy XML parser class so Gradle can expose the app runtime dependency tree; runtime dependency declarations are preserved.",
        "modified_files": modified_files,
    }


def patch_cordova_runtime_tree_copy(destination: Path) -> list[Path]:
    modified_files: list[Path] = []
    local_properties = destination / "local.properties"
    local_properties.write_text("sdk.dir=/opt/android-sdk\nsdk-location=/opt/android-sdk\n", encoding="utf-8")
    modified_files.append(local_properties)
    cdv_config = destination / "cdv-gradle-config.json"
    if cdv_config.exists():
        config_payload = json.loads(cdv_config.read_text(encoding="utf-8"))
        if config_payload.get("MIN_BUILD_TOOLS_VERSION") != "36.0.0":
            config_payload["MIN_BUILD_TOOLS_VERSION"] = "36.0.0"
            cdv_config.write_text(json.dumps(config_payload, indent=2) + "\n", encoding="utf-8")
            modified_files.append(cdv_config)
    cordova_gradle = destination / "CordovaLib" / "cordova.gradle"
    if cordova_gradle.exists():
        text = cordova_gradle.read_text(encoding="utf-8")
        patched = text
        if "import groovy.xml.XmlParser" not in patched:
            patched = patched.replace(
                "import java.util.regex.Pattern\n",
                "import java.util.regex.Pattern\nimport groovy.xml.XmlParser\n",
            )
        if patched != text:
            cordova_gradle.write_text(patched, encoding="utf-8")
            modified_files.append(cordova_gradle)
    return modified_files


def prepare_baby_books_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / "validation-source-baby-books-android-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    settings = destination / "settings.gradle"
    settings.write_text(
        "pluginManagement {\n"
        "    repositories {\n"
        "        google()\n"
        "        mavenCentral()\n"
        "        gradlePluginPortal()\n"
        "    }\n"
        "}\n"
        "\n"
        "dependencyResolutionManagement {\n"
        "    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)\n"
        "    repositories {\n"
        "        google()\n"
        "        mavenCentral()\n"
        "        maven { url 'https://jitpack.io' }\n"
        "    }\n"
        "}\n"
        "\n"
        "rootProject.name = 'Baby Book validation'\n"
        "include ':android'\n"
        "include ':library'\n",
        encoding="utf-8",
    )
    modified_files.append(settings)
    local_properties = destination / "local.properties"
    local_properties.write_text("sdk.dir=/opt/android-sdk\nsdk-location=/opt/android-sdk\n", encoding="utf-8")
    modified_files.append(local_properties)
    root_build = destination / "build.gradle"
    if root_build.exists():
        text = root_build.read_text(encoding="utf-8")
        patched = text.replace(
            "tasks.register('stage') { dependsOn[':web:dist'] }\n",
            "// Validation copy: web deployment task omitted for Android runtime dependency-tree capture.\n",
        )
        if patched != text:
            root_build.write_text(patched, encoding="utf-8")
            modified_files.append(root_build)
    return {
        "root": destination,
        "reason": "Validation copy limits Baby Books to the Android app and shared library modules, omitting unrelated frontend/web/CLI modules that block Gradle configuration; Android runtime dependency declarations are preserved.",
        "modified_files": modified_files,
    }


def prepare_radarweather_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / "validation-source-radarweather-agp-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    root_build = destination / "build.gradle"
    if root_build.exists():
        text = root_build.read_text(encoding="utf-8")
        patched = text.replace(
            "classpath 'com.android.tools.build:gradle:7.1.1'",
            "classpath 'com.android.tools.build:gradle:8.13.2'",
        )
        if patched != text:
            root_build.write_text(patched, encoding="utf-8")
            modified_files.append(root_build)
    app_build = destination / "app" / "build.gradle"
    if app_build.exists():
        text = app_build.read_text(encoding="utf-8")
        patched = text.replace(
            "android {\n\n    compileSdkVersion 34\n",
            "android {\n\n    namespace \"org.woheller69.weather\"\n    compileSdkVersion 34\n\n    buildFeatures {\n        buildConfig true\n    }\n",
        )
        if patched != text:
            app_build.write_text(patched, encoding="utf-8")
            modified_files.append(app_build)
    local_properties = destination / "local.properties"
    local_properties.write_text("sdk.dir=/opt/android-sdk\nsdk-location=/opt/android-sdk\n", encoding="utf-8")
    modified_files.append(local_properties)
    return {
        "root": destination,
        "reason": "Validation copy upgrades RadarWeather's obsolete Android Gradle plugin only for dependency-tree capture, adds the AGP-required namespace/BuildConfig settings, and preserves declared Maven runtime dependencies.",
        "modified_files": modified_files,
    }


def prepare_jcenter_repository_validation_copy(
    source_root: Path,
    validation_dir: Path,
    slug: str,
) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / f"validation-source-{slug}-maven-central-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    for build_file in destination.rglob("build.gradle"):
        text = build_file.read_text(encoding="utf-8")
        patched = text.replace("jcenter()", "mavenCentral()")
        if patched != text:
            build_file.write_text(patched, encoding="utf-8")
            modified_files.append(build_file)
    return {
        "root": destination,
        "reason": "Validation copy replaces removed Gradle jcenter() repository calls with Maven Central only for runtime dependency-tree capture; declared runtime dependencies are preserved.",
        "modified_files": modified_files,
    }


def prepare_todo_agenda_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = recreate_validation_copy(
        source_root=source_root,
        destination=validation_dir / "validation-source-todo-agenda-runtime-tree",
        allowed_root=validation_dir,
    )
    modified_files: list[Path] = []
    app_build = destination / "app" / "build.gradle"
    if app_build.exists():
        text = app_build.read_text(encoding="utf-8")
        patched = text.replace(
            '        archivesBaseName = "TodoAgenda-$versionName".toString()\n',
            "        // Validation copy: obsolete APK archive naming omitted for dependency-tree capture.\n",
        )
        if patched != text:
            app_build.write_text(patched, encoding="utf-8")
            modified_files.append(app_build)
    return {
        "root": destination,
        "reason": "Validation copy omits Todo Agenda's obsolete defaultConfig archivesBaseName output naming that fails under the current Docker Gradle/AGP lane; runtime implementation/api/project dependencies are preserved for source-validation tree capture.",
        "modified_files": modified_files,
    }


def prepare_openkeychain_validation_copy(source_root: Path, validation_dir: Path) -> dict[str, Any]:
    destination = validation_dir / "validation-source-openkeychain-runtime-tree-v2"
    allowed = validation_dir.resolve()
    target = destination.resolve()
    if target != allowed and allowed not in target.parents:
        raise ValueError(f"refusing to recreate validation copy outside {allowed}: {target}")
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    modified_files: list[Path] = []
    root_build = source_root / "build.gradle"
    if root_build.exists():
        shutil.copy2(root_build, destination / "build.gradle")
    openkeychain_source = source_root / "OpenKeychain"
    if openkeychain_source.exists():
        shutil.copytree(
            openkeychain_source,
            destination / "OpenKeychain",
            ignore=shutil.ignore_patterns(".gradle", "build", ".idea"),
        )
    material_source = source_root / "extern" / "MaterialChipsInput"
    if material_source.exists():
        shutil.copytree(
            material_source,
            destination / "extern" / "MaterialChipsInput",
            ignore=shutil.ignore_patterns(".gradle", "build", ".idea"),
        )
    settings = destination / "settings.gradle"
    settings.write_text(
        "rootProject.name = 'openkeychain-validation'\n"
        "include ':OpenKeychain'\n"
        "include ':extern:MaterialChipsInput'\n",
        encoding="utf-8",
    )
    modified_files.append(settings)
    local_properties = destination / "local.properties"
    local_properties.write_text("sdk.dir=/opt/android-sdk\nsdk-location=/opt/android-sdk\n", encoding="utf-8")
    modified_files.append(local_properties)
    gradle_properties = destination / "gradle.properties"
    gradle_properties.write_text("android.useAndroidX=true\n", encoding="utf-8")
    modified_files.append(gradle_properties)
    for build_file in destination.rglob("build.gradle"):
        text = build_file.read_text(encoding="utf-8")
        patched = text.replace("jcenter()", "mavenCentral()")
        if build_file == destination / "OpenKeychain" / "build.gradle":
            patched = patch_openkeychain_app_build(patched, destination)
        if patched != text:
            build_file.write_text(patched, encoding="utf-8")
            modified_files.append(build_file)
    return {
        "root": destination,
        "reason": "Validation copy adds the missing wrapper-root settings.gradle, replaces removed jcenter() calls with Maven Central, enables AGP-required BuildConfig/AndroidX properties, and omits unavailable local project dependency wires; declared Maven runtime dependencies are preserved for OpenKeychain dependency-tree capture.",
        "modified_files": modified_files,
    }


def patch_openkeychain_app_build(text: str, destination: Path) -> str:
    text = text.replace(
        "    buildFeatures {\n        dataBinding true\n    }\n",
        "    buildFeatures {\n        dataBinding true\n        buildConfig true\n    }\n",
    )
    missing_projects = {
        "openpgp-api-lib": destination / "extern" / "openpgp-api-lib",
        "nfcsweetspot": destination / "nfcsweetspot",
        "sshauthentication-api": destination / "sshauthentication-api",
        "extern:bouncycastle:pg": destination / "extern" / "bouncycastle" / "pg",
    }
    patched_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        omitted = False
        for project_name, project_dir in missing_projects.items():
            if f"project(':{project_name}')" in stripped and (
                project_name == "extern:bouncycastle:pg" or not project_dir.exists()
            ):
                patched_lines.append(
                    f"    // Validation copy: omitted unavailable local project dependency {project_name!r}."
                )
                omitted = True
                break
        if not omitted:
            patched_lines.append(line)
    return "\n".join(patched_lines) + ("\n" if text.endswith("\n") else "")


def recreate_validation_copy(*, source_root: Path, destination: Path, allowed_root: Path) -> Path:
    allowed = allowed_root.resolve()
    target = destination.resolve()
    if target != allowed and allowed not in target.parents:
        raise ValueError(f"refusing to recreate validation copy outside {allowed}: {target}")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(
        source_root,
        destination,
        ignore=shutil.ignore_patterns(".gradle", "build", ".idea"),
    )
    return destination


def validation_root_metadata(validation_roots: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {normalize_path(item["root"]): item for item in validation_roots}


def attempt_dependency_tree(
    *,
    slug: str,
    gradle_roots: list[Path],
    validation_dir: Path,
    timeout: int,
    validation_root_metadata: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    validation_dir.mkdir(parents=True, exist_ok=True)
    if not gradle_roots:
        return {"status": "blocked", "reason": "no Gradle root found in extracted source"}
    slug_configs = SLUG_CONFIGURATIONS.get(slug, [])
    configs = list(dict.fromkeys(slug_configs if slug in STRICT_CONFIGURATION_SLUGS else slug_configs + COMMON_CONFIGURATIONS))
    tasks = list(dict.fromkeys(SLUG_DEPENDENCY_TASKS.get(slug, COMMON_DEPENDENCY_TASKS)))
    attempts = []
    for root_index, root in enumerate(gradle_roots[:3], start=1):
        metadata = (validation_root_metadata or {}).get(normalize_path(root))
        gradle_cmd = gradle_command(root, slug)
        for task in tasks:
            for config in configs:
                label = attempt_label(root_index, task, config)
                output = validation_dir / f"{label}.txt"
                error = validation_dir / f"{label}.stderr.txt"
                cmd = gradle_cmd + [
                    "--no-daemon",
                    task,
                    "--configuration",
                    config,
                ]
                try:
                    with output.open("w", encoding="utf-8") as stdout, error.open("w", encoding="utf-8") as stderr:
                        completed = subprocess.run(
                            cmd,
                            cwd=root,
                            stdout=stdout,
                            stderr=stderr,
                            text=True,
                            timeout=timeout,
                            check=False,
                        )
                except FileNotFoundError as exc:
                    attempts.append(
                        {
                            "root": normalize_path(root),
                            "root_type": root_type(metadata),
                            "task": task,
                            "configuration": config,
                            "status": "tool-unavailable",
                            "error": str(exc),
                            "stdout": normalize_path(output),
                            "stderr": normalize_path(error),
                        }
                    )
                    return {
                        "status": "blocked",
                        "reason": "Gradle command unavailable",
                        "attempts": attempts,
                    }
                except subprocess.TimeoutExpired:
                    attempts.append(
                        {
                            "root": normalize_path(root),
                            "root_type": root_type(metadata),
                            "task": task,
                            "configuration": config,
                            "status": "timeout",
                            "timeout_seconds": timeout,
                            "stdout": normalize_path(output),
                            "stderr": normalize_path(error),
                        }
                    )
                    continue
                status = "ok" if completed.returncode == 0 and output.stat().st_size > 0 else "failed"
                attempt = {
                    "root": normalize_path(root),
                    "root_type": root_type(metadata),
                    "task": task,
                    "configuration": config,
                    "status": status,
                    "exit_code": completed.returncode,
                    "stdout": normalize_path(output),
                    "stderr": normalize_path(error),
                }
                if metadata:
                    attempt["validation_copy_reason"] = metadata["reason"]
                attempts.append(attempt)
                if status == "ok":
                    result = {"status": "ok", "tree_path": normalize_path(output), "attempts": attempts}
                    if metadata:
                        result.update(
                            {
                                "validation_copy": True,
                                "validation_copy_reason": metadata["reason"],
                                "validation_copy_root": normalize_path(root),
                            }
                        )
                    return result
    return {"status": "blocked", "reason": "no attempted Gradle configuration succeeded", "attempts": attempts}


def root_type(metadata: dict[str, Any] | None) -> str:
    return "validation-copy" if metadata else "original-source"


def attempt_label(root_index: int, task: str, config: str) -> str:
    task_label = task.strip(":").replace(":", "-") or "root"
    return f"root{root_index}-{task_label}-{config}"


def classify_status(
    source_status: str,
    dependency_status: str | None,
    source_validation: dict[str, Any] | None = None,
    dependency_tree: dict[str, Any] | None = None,
) -> str:
    if source_status != "ok":
        return "source-linked-no-tarball"
    if dependency_status == "ok":
        if source_validation and source_validation.get("status") == "ok":
            total = source_validation.get("sbom_components")
            if total is not None and int(total) == 0:
                return "source-validated-no-maven-signal"
            mismatches = int(source_validation.get("version_mismatches") or 0)
            missing = int(source_validation.get("missing") or 0)
            if dependency_tree and dependency_tree.get("validation_copy"):
                return "source-validated-partial"
            return "source-validated-clean" if mismatches == 0 and missing == 0 else "source-validated-partial"
        return "dependency-tree-captured"
    if dependency_status == "blocked":
        return "gradle-blocked"
    if dependency_status == "not-attempted":
        return "source-downloaded"
    return "source-downloaded"


def metric_eligibility_for(proof_status: str) -> str:
    if proof_status == "source-validated-clean":
        return "clean-source-validated-metrics"
    if proof_status == "source-validated-partial":
        return "partial-source-validated-metrics"
    if proof_status == "source-validated-no-maven-signal":
        return "source-validated-no-maven-signal-control"
    return "excluded-from-source-validated-metrics"


def normalize_proof_metric_eligibility(proof: dict[str, Any]) -> bool:
    proof_status = proof.get("proof_status")
    if not isinstance(proof_status, str):
        return False
    expected = metric_eligibility_for(proof_status)
    if proof.get("metric_eligibility") == expected:
        return False
    proof["metric_eligibility"] = expected
    return True


def find_gradle_roots(root: Path) -> list[Path]:
    if not root.exists():
        return []
    roots = []
    for path in root.rglob("*"):
        if path.name in {"settings.gradle", "settings.gradle.kts"}:
            roots.append(path.parent)
    if not roots:
        for path in root.rglob("*"):
            if path.name in {"build.gradle", "build.gradle.kts"}:
                roots.append(path.parent)
    return sorted(set(roots), key=lambda path: (len(path.parts), str(path)))[:10]


def gradle_command(root: Path, slug: str) -> list[str]:
    if slug in SLUG_GRADLE_COMMANDS:
        return SLUG_GRADLE_COMMANDS[slug]
    wrapper = root / ("gradlew.bat" if sys.platform == "win32" else "gradlew")
    if wrapper.exists():
        if sys.platform != "win32":
            wrapper.chmod(wrapper.stat().st_mode | 0o111)
        return [str(wrapper)]
    return ["/opt/gradle/bin/gradle"] if Path("/opt/gradle/bin/gradle").exists() else ["gradle"]


def should_download(path: Path, source_info: dict[str, Any]) -> bool:
    if not path.exists():
        return True
    expected_size = source_info.get("size")
    if expected_size and path.stat().st_size != int(expected_size):
        return True
    expected_sha256 = source_info.get("sha256")
    return bool(expected_sha256 and sha256_file(path).lower() != expected_sha256.lower())


def safe_extract_tar(tar_path: Path, destination: Path) -> None:
    destination = destination.resolve()
    with tarfile.open(tar_path) as archive:
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            if destination not in target.parents and target != destination:
                raise ValueError(f"unsafe tar member path: {member.name}")
        archive.extractall(destination)


def write_outputs(result: dict[str, Any], output_json: Path, output_doc: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_doc.write_text(build_markdown(result), encoding="utf-8")


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Real APK Batch Proof Status",
        "",
        "This batch artifact advances selected real APK rows through the same proof gates together.",
        "It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Selected APKs | {summary['selected']} |",
        f"| Source tarballs available | {summary['source_available']} |",
        f"| Dependency trees captured | {summary['dependency_tree_ok']} |",
        f"| Source validations completed | {summary.get('source_validation_ok', 0)} |",
        f"| Script failures | {summary['failed']} |",
        f"| Source root | `{summary['source_root']}` |",
        f"| Validation root | `{summary['validation_root']}` |",
        "",
        "## Per-APK Status",
        "",
        "| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |",
        "|---|---|---|---|---|---|---|",
    ]
    for proof in result["proofs"]:
        version = f"{proof.get('version_name') or 'n/a'} ({proof.get('version_code') or 'n/a'})"
        source = proof.get("source", {})
        dependency = proof.get("dependency_tree", {})
        source_value = source.get("status", proof.get("status", "unknown"))
        if source.get("tarball_path"):
            source_value += f": `{source['tarball_path']}`"
        dependency_value = describe_dependency_tree(dependency)
        if dependency.get("tree_path"):
            dependency_value += f": `{dependency['tree_path']}`"
        validation_value = describe_source_validation(proof.get("source_validation", {}))
        next_gate = next_gate_for(proof)
        lines.append(
            "| "
            f"{proof['app']} | "
            f"{version} | "
            f"{proof.get('proof_status', proof.get('status', 'unknown'))} | "
            f"{source_value} | "
            f"{dependency_value} | "
            f"{validation_value} | "
            f"{next_gate} |"
        )
    lines.extend(
        [
            "",
            "## Rules",
            "",
            "- Source tarball checksum success is only a source-availability gate.",
            "- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.",
            "- Framework/native-heavy rows may remain limitation evidence even after source capture.",
            "- Rows with blocked Gradle trees stay out of source-validated metrics.",
            "",
        ]
    )
    return "\n".join(lines)


def describe_dependency_tree(dependency: dict[str, Any]) -> str:
    status = dependency.get("status", "unknown")
    reason = dependency.get("reason")
    attempts = dependency.get("attempts") or []
    details = []
    if dependency.get("validation_copy"):
        details.append("validation-copy")
    if reason:
        details.append(reason)
    if attempts:
        details.append(f"{len(attempts)} attempted config(s)")
    return f"{status}: {'; '.join(details)}" if details else status


def describe_source_validation(source_validation: dict[str, Any]) -> str:
    status = source_validation.get("status", "unknown")
    if status == "ok":
        confirmed = source_validation.get("confirmed", "n/a")
        total = source_validation.get("sbom_components")
        if total is None and all(
            int(source_validation.get(key) or 0) == 0
            for key in ("confirmed", "version_mismatches", "missing")
        ):
            total = 0
        if total is None:
            total = "n/a"
        mismatches = source_validation.get("version_mismatches", "n/a")
        missing = source_validation.get("missing", "n/a")
        value = f"ok: {confirmed}/{total} confirmed, {mismatches} mismatch(es), {missing} missing"
        if source_validation.get("validation_markdown"):
            value += f": `{source_validation['validation_markdown']}`"
        elif source_validation.get("path"):
            value += f": `{source_validation['path']}`"
        return value
    reason = source_validation.get("reason")
    return f"{status}: {reason}" if reason else status


def next_gate_for(proof: dict[str, Any]) -> str:
    source_status = proof.get("source", {}).get("status")
    dependency_status = proof.get("dependency_tree", {}).get("status")
    validation = proof.get("source_validation", {})
    if source_status != "ok":
        return "Find source tag/repo proof or keep source-linked smoke only."
    if validation.get("status") == "ok":
        confirmed = int(validation.get("confirmed") or 0)
        total = int(validation.get("sbom_components") or 0)
        mismatches = int(validation.get("version_mismatches") or 0)
        missing = int(validation.get("missing") or 0)
        if proof.get("proof_status") == "source-validated-clean" or (
            total > 0 and confirmed == total and mismatches == 0 and missing == 0
        ):
            return "Eligible for clean source-validated metrics after doc admission."
        if proof.get("proof_status") == "source-validated-no-maven-signal":
            return "Record as successful no-Maven-signal control; do not use as accuracy evidence."
        return "Record as source-validated partial; keep mismatches explicit."
    if dependency_status == "ok":
        return "Run validate-source-deps against this dependency tree."
    if dependency_status == "blocked":
        return "Investigate Gradle configuration/toolchain blocker."
    return "Attempt Gradle runtime dependency tree."


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
