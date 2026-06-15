from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("data/test_apks/limitation")
DEFAULT_NAME = "controlled-hidden-dex-loader-limitation"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a synthetic APK limitation fixture with hidden DEX and "
            "packer/protector-style forensic indicators."
        )
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--name", default=DEFAULT_NAME)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    apk_path = output_dir / f"{args.name}.apk"
    metadata_path = output_dir / f"{args.name}.limitation.json"

    manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.limitation.dynamicloader"
    android:versionCode="1"
    android:versionName="1.0">
    <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="35" />
    <uses-permission android:name="android.permission.INTERNET" />
</manifest>
"""

    with zipfile.ZipFile(apk_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("AndroidManifest.xml", manifest)
        archive.writestr("resources.arsc", b"")
        archive.writestr("classes.dex", b"dex\n035\0")
        archive.writestr("assets/classes2.dex", b"dex\n035\0hidden dynamic payload")
        archive.writestr("assets/protect_payload.dat", b"x" * (1024 * 1024))
        archive.writestr("lib/armeabi-v7a/libshell.so", b"synthetic loader stub")

    metadata = {
        "apk_path": str(apk_path),
        "builder": "scripts/build_limitation_apk.py",
        "dataset_layer": "limitation",
        "validation_level": "L3 limitation fixture",
        "metrics_allowed": ["forensic warning quality", "limitation behavior"],
        "package_name": "com.example.limitation.dynamicloader",
        "expected_behavior": {
            "accuracy_claim": "none",
            "forensic_indicators": [
                "nonstandard-dex",
                "tiny-primary-dex",
                "protector-name-hint",
                "large-opaque-assets",
            ],
            "reporting_expectation": (
                "The MVP should warn about hidden/dynamic-code-style packaging "
                "and avoid claiming complete Java/Kotlin library recovery."
            ),
        },
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"apk": str(apk_path), "metadata": str(metadata_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
