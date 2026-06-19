from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_ROOT = Path(
    "data/results/experiments/real-apk-priority-i2p-source-build/i2p.i2p"
)
DEFAULT_ARTIFACT_ROOT = Path(
    "data/results/experiments/real-apk-priority-i2p-source-build/artifacts"
)
DEFAULT_MANIFEST = Path(
    "data/results/experiments/real-apk-priority-i2p-source-build/"
    "source-build-manifest.json"
)
SOURCE_TARBALL = Path("data/source/csv7/i2p/source.tar.gz")
SOURCE_TARBALL_SHA256 = (
    "dded22feee758ab414b3d2bd44e95f5f33764b84c5d0de8abd59534409c8d3f2"
)

MODULES = (
    {
        "coordinate": "net.i2p:i2p",
        "jar": "core/build/libs/i2p.jar",
        "dependencies": [],
    },
    {
        "coordinate": "net.i2p:router",
        "jar": "router/build/libs/router.jar",
        "dependencies": [
            {"group": "net.i2p", "artifact": "i2p", "version": "2.11.0-1"},
        ],
    },
    {
        "coordinate": "net.i2p.client:mstreaming",
        "jar": "apps/ministreaming/build/libs/mstreaming.jar",
        "dependencies": [
            {"group": "net.i2p", "artifact": "i2p", "version": "2.11.0-1"},
        ],
    },
    {
        "coordinate": "net.i2p.client:streaming",
        "jar": "apps/streaming/build/libs/streaming.jar",
        "dependencies": [
            {"group": "net.i2p", "artifact": "i2p", "version": "2.11.0-1"},
            {
                "group": "net.i2p.client",
                "artifact": "mstreaming",
                "version": "2.11.0-1",
            },
        ],
    },
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stage exact-source I2P JARs for priority reference extraction."
    )
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    return parser


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_exact_version(source_root: Path) -> str:
    core_text = (
        source_root / "core/java/src/net/i2p/CoreVersion.java"
    ).read_text(encoding="utf-8")
    router_text = (
        source_root / "router/java/src/net/i2p/router/RouterVersion.java"
    ).read_text(encoding="utf-8")
    release_match = re.search(
        r'public final static String VERSION\s*=\s*"([^"]+)"', core_text
    )
    build_match = re.search(
        r"public final static long BUILD\s*=\s*(\d+)", router_text
    )
    extra_match = re.search(
        r'public final static String EXTRA\s*=\s*"([^"]*)"', router_text
    )
    if not release_match or not build_match or not extra_match:
        raise ValueError("Could not derive the exact I2P source version")
    return f"{release_match.group(1)}-{build_match.group(1)}{extra_match.group(1)}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def stage(source_root: Path, artifact_root: Path) -> dict[str, Any]:
    version = read_exact_version(source_root)
    if version != "2.11.0-1":
        raise ValueError(f"Expected I2P 2.11.0-1, found {version}")
    if sha256_file(SOURCE_TARBALL) != SOURCE_TARBALL_SHA256:
        raise ValueError("The exact F-Droid source tarball hash changed")

    artifacts = []
    for module in MODULES:
        group, artifact = str(module["coordinate"]).split(":", maxsplit=1)
        source_jar = source_root / str(module["jar"])
        if not source_jar.is_file():
            raise FileNotFoundError(f"Built JAR not found: {source_jar}")
        output_dir = artifact_root / Path(*group.split(".")) / artifact / version
        output_dir.mkdir(parents=True, exist_ok=True)
        output_jar = output_dir / f"{artifact}-{version}.jar"
        shutil.copy2(source_jar, output_jar)
        digest = sha256_file(output_jar)
        metadata = {
            "artifact": artifact,
            "coordinate": module["coordinate"],
            "dependencies": module["dependencies"],
            "group": group,
            "packaging": "jar",
            "path": output_jar.as_posix(),
            "pom_error": "Exact-source local build; no published POM used.",
            "pom_path": None,
            "pom_sha256": None,
            "pom_size": None,
            "pom_url": None,
            "purl": f"pkg:maven/{group}/{artifact}@{version}",
            "sha256": digest,
            "size": output_jar.stat().st_size,
            "url": (
                "source-build:https://f-droid.org/repo/"
                "net.i2p.android.router_4745304_src.tar.gz"
            ),
            "version": version,
        }
        write_json(output_dir / "metadata.json", metadata)
        artifacts.append(
            {
                "coordinate": module["coordinate"],
                "version": version,
                "source_jar": source_jar.as_posix(),
                "staged_jar": output_jar.as_posix(),
                "sha256": digest,
                "size": output_jar.stat().st_size,
            }
        )

    return {
        "schema_version": 1,
        "source_root": source_root.as_posix(),
        "source_tarball": SOURCE_TARBALL.as_posix(),
        "source_tarball_sha256": SOURCE_TARBALL_SHA256,
        "exact_version": version,
        "artifact_root": artifact_root.as_posix(),
        "artifacts": artifacts,
    }


def main() -> int:
    args = build_parser().parse_args()
    payload = stage(Path(args.source_root), Path(args.artifact_root))
    write_json(Path(args.manifest), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
