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
    "davx5": [":app-ose:dependencies", "dependencies"],
    "openvpn-for-android": [":main:dependencies", "dependencies"],
    "shelter": [":app:dependencies", "dependencies"],
    "keepassdx": [":app:dependencies", "dependencies"],
    "gadgetbridge": [":app:dependencies", "dependencies"],
}

VALIDATION_COPY_SLUGS = {"openvpn-for-android", "shelter"}


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
    parser.add_argument(
        "--reuse-existing-proofs",
        action="store_true",
        help="Rebuild the combined proof status from validation_root/<slug>/proof-status.json files.",
    )
    parser.add_argument("--continue-on-error", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    batch = read_json(Path(args.batch_json))
    rows = batch["apks"]
    if args.slug:
        wanted = set(args.slug)
        rows = [row for row in rows if row["slug"] in wanted]
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
            proofs.append(read_json(proof_path))
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
        dependency_tree = attempt_dependency_tree(
            slug=slug,
            gradle_roots=[root["root"] for root in validation_gradle_roots] + gradle_roots,
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
        "metric_eligibility": "excluded-from-source-validated-metrics",
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
    configs = list(dict.fromkeys(SLUG_CONFIGURATIONS.get(slug, []) + COMMON_CONFIGURATIONS))
    tasks = list(dict.fromkeys(SLUG_DEPENDENCY_TASKS.get(slug, COMMON_DEPENDENCY_TASKS)))
    attempts = []
    for root_index, root in enumerate(gradle_roots[:3], start=1):
        metadata = (validation_root_metadata or {}).get(normalize_path(root))
        gradle_cmd = gradle_command(root)
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


def gradle_command(root: Path) -> list[str]:
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
