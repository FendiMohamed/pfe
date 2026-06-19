from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_source_observed_failed_download_retry_plan import version_key


DEFAULT_RECOVERY_JSON = Path(
    "data/results/evaluation/real-apk-priority-existing-db-recovery.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/evaluation/real-apk-priority-lightweight-retry-plan.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/REAL_APK_PRIORITY_LIGHTWEIGHT_RETRY_PLAN.md"
)
DEFAULT_JCENTER_AAR_CONFIG = Path(
    "configs/libraries.real_apk_priority_lightweight_jcenter_aar.json"
)
DEFAULT_JCENTER_JAR_CONFIG = Path(
    "configs/libraries.real_apk_priority_lightweight_jcenter_jar.json"
)
DEFAULT_GOOGLE_AAR_CONFIG = Path(
    "configs/libraries.real_apk_priority_lightweight_google_aar.json"
)
DEFAULT_ALIYUN_JCENTER_AAR_CONFIG = Path(
    "configs/libraries.real_apk_priority_lightweight_aliyun_jcenter_aar.json"
)
DEFAULT_ALIYUN_JCENTER_JAR_CONFIG = Path(
    "configs/libraries.real_apk_priority_lightweight_aliyun_jcenter_jar.json"
)

JCENTER = "https://jcenter.bintray.com"
ALIYUN_JCENTER = "https://maven.aliyun.com/repository/jcenter"
GOOGLE_MAVEN = "https://dl.google.com/dl/android/maven2"

BOUNDARY_COORDINATES = {
    "com.facebook.react:hermes-android",
    "com.facebook.react:react-android",
    "com.facebook.react:react-native",
    "io.github.Rosemoe.sora-editor:bom",
    "org.apache.commons:commons-numbers-parent",
}
BOUNDARY_PREFIXES = ("net.i2p",)
INVALID_ALIAS_VERSIONS = {
    "androidx.annotation",
    "androidx.appcompat",
    "androidx.constraintlayout",
    "androidx.core",
    "androidx.exifinterface",
    "androidx.fragment",
    "androidx.legacy",
    "androidx.multidex",
    "androidx.recyclerview",
    "androidx.vectordrawable",
    "com.facebook.react",
    "org.slf4j",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a bounded lightweight retry set for still-missing real-APK "
            "priority references, excluding heavy and non-bytecode boundaries."
        )
    )
    parser.add_argument("--recovery-json", default=str(DEFAULT_RECOVERY_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--jcenter-aar-config", default=str(DEFAULT_JCENTER_AAR_CONFIG))
    parser.add_argument("--jcenter-jar-config", default=str(DEFAULT_JCENTER_JAR_CONFIG))
    parser.add_argument("--google-aar-config", default=str(DEFAULT_GOOGLE_AAR_CONFIG))
    parser.add_argument(
        "--aliyun-jcenter-aar-config",
        default=str(DEFAULT_ALIYUN_JCENTER_AAR_CONFIG),
    )
    parser.add_argument(
        "--aliyun-jcenter-jar-config",
        default=str(DEFAULT_ALIYUN_JCENTER_JAR_CONFIG),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_plan(Path(args.recovery_json))
    outputs = {
        "jcenter_aar": Path(args.jcenter_aar_config),
        "jcenter_jar": Path(args.jcenter_jar_config),
        "google_aar": Path(args.google_aar_config),
        "aliyun_jcenter_aar": Path(args.aliyun_jcenter_aar_config),
        "aliyun_jcenter_jar": Path(args.aliyun_jcenter_jar_config),
    }
    for name, path in outputs.items():
        write_json(path, payload["retry_configs"][name])
    payload["outputs"] = {name: normalize_path(path) for name, path in outputs.items()}
    write_json(Path(args.output_json), payload)
    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


def build_plan(recovery_json: Path) -> dict[str, Any]:
    recovery = read_json(recovery_json)
    rows = recovery["not_available_in_source_db"]
    classified = [classify(row) for row in rows]
    jcenter_rows = [
        row for row in classified if row["action"] == "retry-jcenter"
    ]
    google_rows = [
        row for row in classified if row["action"] == "retry-google-aar"
    ]
    deferred = [row for row in classified if row["action"].startswith("defer-")]
    retry_configs = {
        "jcenter_aar": {"libraries": build_libraries(jcenter_rows, JCENTER, "aar")},
        "jcenter_jar": {"libraries": build_libraries(jcenter_rows, JCENTER, "jar")},
        "google_aar": {"libraries": build_libraries(google_rows, GOOGLE_MAVEN, "aar")},
        "aliyun_jcenter_aar": {
            "libraries": build_libraries(jcenter_rows, ALIYUN_JCENTER, "aar")
        },
        "aliyun_jcenter_jar": {
            "libraries": build_libraries(jcenter_rows, ALIYUN_JCENTER, "jar")
        },
    }
    return {
        "schema_version": 1,
        "source": normalize_path(recovery_json),
        "summary": {
            "remaining_after_existing_db_recovery": len(rows),
            "lightweight_retry_slots": len(jcenter_rows) + len(google_rows),
            "jcenter_retry_slots": len(jcenter_rows),
            "google_retry_slots": len(google_rows),
            "deferred_slots": len(deferred),
            "deferred_action_counts": dict(
                sorted(Counter(row["action"] for row in deferred).items())
            ),
        },
        "classified_rows": classified,
        "deferred_rows": deferred,
        "retry_configs": retry_configs,
    }


def classify(source: dict[str, Any]) -> dict[str, Any]:
    row = dict(source)
    coordinate = str(row["coordinate"])
    version = str(row["version"])
    group, artifact = coordinate.split(":", maxsplit=1)
    action = "defer-unsupported"
    reason = "No bounded lightweight repository retry is justified."

    if version in INVALID_ALIAS_VERSIONS:
        action = "defer-alias-version"
        reason = "The recorded version is a coordinate/family alias, not a Maven version."
    elif coordinate == "org.jetbrains.kotlin:kotlin-stdlib-common":
        action = "defer-no-jvm-bytecode-boundary"
        reason = "Modern kotlin-stdlib-common is metadata-oriented and not a useful JVM DEX reference."
    elif coordinate in BOUNDARY_COORDINATES:
        action = "defer-heavy-or-parent-boundary"
        reason = "React/parent/BOM rows are heavy, repository-local, or provide no bytecode."
    elif group.startswith(BOUNDARY_PREFIXES):
        action = "defer-special-repository-boundary"
        reason = "I2P rows require a project-specific repository; do not spend the bounded pass guessing."
    elif row.get("retry_class") == "jitpack-candidate":
        action = "defer-exhausted-jitpack"
        reason = "Both JitPack package forms were already attempted in earlier priority/demo retries."
    elif row.get("retry_class") == "google-alt-packaging":
        action = "retry-google-aar"
        reason = "Small Google/Android artifact; one bounded Google Maven AAR retry is cheap."
    elif row.get("retry_class") == "legacy-support-alias" and version[0].isdigit():
        action = "retry-google-aar"
        reason = "Numeric legacy support-library version; bounded Google Maven AAR retry."
    elif row.get("retry_class") == "manual-repository-or-unavailable":
        action = "retry-jcenter"
        reason = "Small legacy Android/JVM artifact; retry archived JCenter as both AAR and JAR."

    return {
        **row,
        "group": group,
        "artifact": artifact,
        "action": action,
        "reason": reason,
    }


def build_libraries(
    rows: list[dict[str, Any]],
    repository_url: str,
    packaging: str,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["group"], row["artifact"])].append(row)
    libraries = []
    for (group, artifact), items in sorted(
        grouped.items(),
        key=lambda item: (
            -max(int(row.get("apk_support_count", 0)) for row in item[1]),
            -sum(int(row.get("occurrence_count", 0)) for row in item[1]),
            item[0],
        ),
    ):
        libraries.append(
            {
                "group": group,
                "artifact": artifact,
                "versions": sorted(
                    {str(row["version"]) for row in items},
                    key=version_key,
                ),
                "packaging": packaging,
                "repository_url": repository_url,
                "notes": (
                    "Bounded lightweight real-APK priority recovery; "
                    "heavy and non-bytecode boundaries excluded."
                ),
            }
        )
    return libraries


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Real APK Priority Lightweight Retry Plan",
        "",
        "This is a bounded, value-first recovery pass. It retries only small plausible "
        "Google/JCenter artifacts and defers heavy, metadata-only, alias, and exhausted "
        "repository boundaries.",
        "",
        "## Summary",
        "",
        f"- Remaining after local existing-DB recovery: `{summary['remaining_after_existing_db_recovery']}`",
        f"- Lightweight retry slots: `{summary['lightweight_retry_slots']}`",
        f"- JCenter retry slots: `{summary['jcenter_retry_slots']}`",
        f"- Google Maven retry slots: `{summary['google_retry_slots']}`",
        f"- Deferred boundary slots: `{summary['deferred_slots']}`",
        "",
        "## Deferred Classes",
        "",
    ]
    for action, count in summary["deferred_action_counts"].items():
        lines.append(f"- `{action}`: `{count}`")
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "Only `data/reference_db/reference_features_real_apk_priority_versions.sqlite` "
            "may receive recovered rows. The shared calibrated DB remains unchanged.",
            "",
        ]
    )
    return "\n".join(lines)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def normalize_path(path: Path) -> str:
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
