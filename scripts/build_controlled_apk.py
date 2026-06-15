from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


DEFAULT_ARTIFACT_ROOT = Path("data/reference_db/artifacts")
DEFAULT_OUTPUT_DIR = Path("data/test_apks")
DEFAULT_COORDINATE = "com.google.code.gson:gson"
DEFAULT_VERSION = "2.8.9"
FIXTURE_VARIANTS = (
    "clear",
    "r8-rename",
    "r8-shrink",
    "r8-optimize",
    "r8-shrink-optimize",
    "r8-repackage",
    "r8-inline-stress",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a tiny controlled APK fixture with one known Maven library.",
    )
    parser.add_argument("--coordinate", default=DEFAULT_COORDINATE)
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument(
        "--dependency",
        action="append",
        default=[],
        help=(
            "Additional Maven dependency as coordinate@version. "
            "Can be repeated to build multi-library fixtures."
        ),
    )
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument(
        "--name",
        help="Optional fixture base name. Defaults to a coordinate-derived controlled-* name.",
    )
    parser.add_argument(
        "--variant",
        default="clear",
        choices=FIXTURE_VARIANTS,
        help="Fixture variant to build.",
    )
    parser.add_argument(
        "--multidex-mode",
        default="auto",
        choices=["auto", "file-per-class"],
        help="Use file-per-class to force multiple standard classes*.dex files.",
    )
    parser.add_argument("--min-api", type=int, default=21)
    parser.add_argument("--javac-command", default="javac")
    parser.add_argument("--jar-command", default="jar")
    parser.add_argument("--d8-command", default="d8")
    parser.add_argument("--r8-command", default="r8")
    parser.add_argument(
        "--keep-build-dir",
        action="store_true",
        help="Keep the temporary build directory under data/test_apks/build for debugging.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    artifacts = load_fixture_artifacts(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = args.name or fixture_base_name(args.coordinate, args.version, args.variant)
    apk_path = output_dir / f"{base_name}.apk"
    metadata_path = output_dir / f"{base_name}.ground-truth.json"

    if args.keep_build_dir:
        build_dir = output_dir / "build" / base_name
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)
        result = build_fixture(args, artifacts, apk_path, metadata_path, build_dir)
    else:
        with tempfile.TemporaryDirectory(prefix=f"{base_name}-") as tmp:
            result = build_fixture(args, artifacts, apk_path, metadata_path, Path(tmp))

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def load_fixture_artifacts(args: argparse.Namespace) -> list[dict]:
    requested = [(args.coordinate, args.version)]
    requested.extend(parse_dependency(value) for value in args.dependency)
    return [
        load_artifact_metadata(args.artifact_root, coordinate, version)
        for coordinate, version in requested
    ]


def parse_dependency(value: str) -> tuple[str, str]:
    if "@" not in value:
        raise ValueError(f"Dependency must use coordinate@version: {value}")
    coordinate, version = value.rsplit("@", 1)
    if coordinate.count(":") != 1 or not version:
        raise ValueError(f"Dependency must use Maven coordinate@version: {value}")
    return coordinate, version


def load_artifact_metadata(artifact_root: str | Path, coordinate: str, version: str) -> dict:
    root = Path(artifact_root)
    for metadata_path in sorted(root.rglob("metadata.json")):
        with metadata_path.open("r", encoding="utf-8") as handle:
            metadata = json.load(handle)
        if metadata.get("coordinate") == coordinate and metadata.get("version") == version:
            artifact_path = resolve_artifact_path(metadata_path, metadata["path"])
            if not artifact_path.exists():
                raise FileNotFoundError(f"Artifact file not found: {artifact_path}")
            return {
                **metadata,
                "metadata_path": str(metadata_path),
                "artifact_path": str(artifact_path),
            }
    raise FileNotFoundError(f"No metadata found for {coordinate}@{version} under {root}")


def build_fixture(
    args: argparse.Namespace,
    artifacts: list[dict],
    apk_path: Path,
    metadata_path: Path,
    build_dir: Path,
) -> dict:
    dex_dir = build_dir / "dex"
    dex_dir.mkdir(parents=True, exist_ok=True)

    primary_artifact = artifacts[0]
    artifact_paths = [Path(artifact["artifact_path"]) for artifact in artifacts]
    d8_inputs = [str(path) for path in artifact_paths]
    fixture_mode = "library-only"

    if command_available(args.javac_command) and command_available(args.jar_command):
        source_dir = build_dir / "src" / "com" / "example" / "fixture"
        classes_dir = build_dir / "classes"
        source_dir.mkdir(parents=True, exist_ok=True)
        classes_dir.mkdir(parents=True, exist_ok=True)

        source_path = source_dir / "FixtureEntry.java"
        source_path.write_text(
            java_source_for(primary_artifact["coordinate"], args.variant),
            encoding="utf-8",
        )
        app_jar = build_dir / "fixture-app.jar"

        run_command(
            [
                args.javac_command,
                "-cp",
                os.pathsep.join(str(path) for path in artifact_paths),
                "-d",
                str(classes_dir),
                str(source_path),
            ]
        )
        run_command(
            [
                args.jar_command,
                "--create",
                "--file",
                str(app_jar),
                "-C",
                str(classes_dir),
                ".",
            ]
        )
        d8_inputs.insert(0, str(app_jar))
        fixture_mode = "app-plus-library"

    if args.variant == "clear":
        d8_command = [
            args.d8_command,
            "--min-api",
            str(args.min_api),
            "--output",
            str(dex_dir),
        ]
        if args.multidex_mode == "file-per-class":
            d8_command.append("--file-per-class")
        run_command([*d8_command, *d8_inputs])
    else:
        if args.multidex_mode != "auto":
            raise ValueError("Forced multidex is currently supported only for the clear variant.")
        rules_path = build_dir / f"{args.variant}.pro"
        rules_path.write_text(r8_rules_for(primary_artifact["coordinate"], args.variant), encoding="utf-8")
        r8_command = resolve_command(
            args.r8_command,
            [Path("/opt/android-sdk/cmdline-tools/latest/bin/r8")],
        )
        run_command(
            [
                r8_command,
                "--release",
                "--min-api",
                str(args.min_api),
                "--output",
                str(dex_dir),
                "--pg-conf",
                str(rules_path),
                *d8_inputs,
            ]
        )

    dex_files = normalized_dex_files(dex_dir, args.multidex_mode)
    if not dex_files:
        raise RuntimeError(f"D8 did not produce classes*.dex under {dex_dir}")

    with zipfile.ZipFile(apk_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "AndroidManifest.xml",
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android" '
            'package="com.example.fixture" />\n',
        )
        archive.writestr("resources.arsc", b"")
        for dex_file in dex_files:
            archive.write(dex_file, dex_file.name)

    expected_components = [
        {
            "coordinate": artifact["coordinate"],
            "version": artifact["version"],
            "purl": artifact["purl"],
            "artifact_path": str(Path(artifact["artifact_path"])),
            "artifact_metadata_path": artifact["metadata_path"],
        }
        for artifact in artifacts
    ]
    ground_truth = {
        "apk_path": str(apk_path),
        "coordinate": primary_artifact["coordinate"],
        "version": primary_artifact["version"],
        "purl": primary_artifact["purl"],
        "artifact_path": str(artifact_paths[0]),
        "artifact_metadata_path": primary_artifact["metadata_path"],
        "expected_components": expected_components,
        "dex_files": [dex_file.name for dex_file in dex_files],
        "fixture_mode": fixture_mode,
        "multidex_mode": args.multidex_mode,
        "variant": args.variant,
        "builder": "scripts/build_controlled_apk.py",
    }
    metadata_path.write_text(json.dumps(ground_truth, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return ground_truth


def normalized_dex_files(dex_dir: Path, multidex_mode: str) -> list[Path]:
    if multidex_mode == "auto":
        return sorted(dex_dir.glob("classes*.dex"))

    produced = sorted(path for path in dex_dir.rglob("*.dex") if path.is_file())
    normalized: list[Path] = []
    for index, dex_file in enumerate(produced, start=1):
        name = "classes.dex" if index == 1 else f"classes{index}.dex"
        target = dex_dir / name
        if dex_file != target:
            dex_file.replace(target)
        normalized.append(target)
    return normalized


def java_source_for(coordinate: str, variant: str = "clear") -> str:
    if variant == "r8-inline-stress":
        return inline_stress_java_source_for(coordinate)

    if coordinate == "com.google.code.gson:gson":
        return """package com.example.fixture;

import com.google.gson.Gson;

public final class FixtureEntry {
    private FixtureEntry() {}

    public static String render(Object value) {
        return new Gson().toJson(value);
    }
}
"""

    return """package com.example.fixture;

public final class FixtureEntry {
    private FixtureEntry() {}

    public static String render(Object value) {
        return String.valueOf(value);
    }
}
"""


def inline_stress_java_source_for(coordinate: str) -> str:
    if coordinate == "com.google.code.gson:gson":
        return """package com.example.fixture;

import com.google.gson.Gson;

public final class FixtureEntry {
    private FixtureEntry() {}

    public static String render(Object value) {
        return first(value);
    }

    private static String first(Object value) {
        return second(String.valueOf(value));
    }

    private static String second(String value) {
        return third(value + ":gson");
    }

    private static String third(String value) {
        return new Gson().toJson(value);
    }
}
"""

    if coordinate == "commons-codec:commons-codec":
        return """package com.example.fixture;

import org.apache.commons.codec.digest.DigestUtils;

public final class FixtureEntry {
    private FixtureEntry() {}

    public static String render(Object value) {
        return first(value);
    }

    private static String first(Object value) {
        return second(String.valueOf(value));
    }

    private static String second(String value) {
        return third(value + ":codec");
    }

    private static String third(String value) {
        return DigestUtils.sha256Hex(value);
    }
}
"""

    return """package com.example.fixture;

public final class FixtureEntry {
    private FixtureEntry() {}

    public static String render(Object value) {
        return first(value);
    }

    private static String first(Object value) {
        return second(String.valueOf(value));
    }

    private static String second(String value) {
        return third(value + ":inline");
    }

    private static String third(String value) {
        return value.toUpperCase(java.util.Locale.ROOT);
    }
}
"""


def r8_rules_for(coordinate: str, variant: str) -> str:
    if variant == "r8-rename":
        return "\n".join(
            [
                "-dontshrink",
                "-dontoptimize",
                "-dontwarn **",
                "-keep,allowobfuscation class ** { *; }",
                "",
            ]
        )
    if variant == "r8-optimize":
        return "\n".join(
            [
                "-dontshrink",
                "-dontobfuscate",
                "-dontwarn **",
                "-allowaccessmodification",
                "-keep,allowoptimization class ** { *; }",
                "",
            ]
        )
    if variant == "r8-shrink" and coordinate == "com.google.code.gson:gson":
        return "\n".join(
            [
                "-dontwarn **",
                "-keep,allowobfuscation class com.google.gson.Gson { public *; }",
                "",
            ]
        )
    if variant == "r8-shrink-optimize" and coordinate == "com.google.code.gson:gson":
        return "\n".join(
            [
                "-dontwarn **",
                "-allowaccessmodification",
                "-keep,allowobfuscation,allowoptimization class com.google.gson.Gson { public *; }",
                "-keep,allowobfuscation,allowoptimization class com.example.fixture.FixtureEntry { public static java.lang.String render(...); }",
                "",
            ]
        )
    if variant == "r8-shrink-optimize":
        return "\n".join(
            [
                "-dontwarn **",
                "-allowaccessmodification",
                "-keep,allowobfuscation,allowoptimization class ** { public *; }",
                "-keep,allowobfuscation,allowoptimization class com.example.fixture.FixtureEntry { public static java.lang.String render(...); }",
                "",
            ]
        )
    if variant == "r8-repackage":
        return "\n".join(
            [
                "-dontshrink",
                "-dontoptimize",
                "-dontwarn **",
                "-allowaccessmodification",
                "-repackageclasses r8flat",
                "-keep,allowobfuscation class ** { *; }",
                "",
            ]
        )
    if variant == "r8-inline-stress":
        return "\n".join(
            [
                "-dontshrink",
                "-dontobfuscate",
                "-dontwarn **",
                "-allowaccessmodification",
                "-keep,allowoptimization class ** { *; }",
                "-keep,allowoptimization class com.example.fixture.FixtureEntry { public static java.lang.String render(...); }",
                "",
            ]
        )
    if variant == "r8-shrink":
        return "\n".join(
            [
                "-dontwarn **",
                "-keep,allowobfuscation class ** { public *; }",
                "",
            ]
        )
    raise ValueError(f"Unsupported R8 variant: {variant}")


def run_command(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Command failed with exit code "
            f"{completed.returncode}: {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )


def command_available(command: str) -> bool:
    return shutil.which(command) is not None or Path(command).exists()


def resolve_command(command: str, fallback_paths: list[Path]) -> str:
    resolved = shutil.which(command)
    if resolved:
        return resolved
    for fallback in fallback_paths:
        if fallback.exists():
            return str(fallback)
    return command


def resolve_artifact_path(metadata_path: Path, artifact_path: str) -> Path:
    candidate = Path(artifact_path)
    if candidate.exists():
        return candidate
    normalized = Path(artifact_path.replace("\\", "/"))
    if normalized.exists():
        return normalized
    sibling = metadata_path.parent / Path(artifact_path.replace("\\", "/")).name
    if sibling.exists():
        return sibling
    return normalized


def fixture_base_name(coordinate: str, version: str, variant: str) -> str:
    return f"controlled-{coordinate.replace(':', '-').replace('.', '-')}-{version}-{variant}"


if __name__ == "__main__":
    raise SystemExit(main())
