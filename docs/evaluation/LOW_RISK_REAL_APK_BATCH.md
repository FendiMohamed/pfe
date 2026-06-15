# Real APK Growth Batch V2

This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.
It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 4 |
| Succeeded | 4 |
| Failed | 0 |
| APK root | `data/test_apks/real` |
| Report root | `data/results/evaluation/low-risk-real-apk-batch` |
| Classes covered | has-declared-dependencies, low-risk-candidate, low-risk-preflight, modern-gradle, no-native, normal-gradle-root, small-apk |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Stopwatch | `com.github.muellerma.stopwatch` | 1.6 (7) | source-validated-real | 1 | 0 | 5 | low-risk-preflight, no-native, small-apk, normal-gradle-root, low-risk-candidate, modern-gradle, has-declared-dependencies | ok: `data/results/evaluation/low-risk-real-apk-batch/report-real-stopwatch/report.json` | Selected by low-risk preflight: no native ABI, small APK/source tarball, modern AGP project, declared Maven dependencies, and quick Gradle dependency-tree success. |
| Blue Square Speedometer | `net.nhiroki.bluesquarespeedometer` | 1.1.0 (13) | source-validated-real | 1 | 0 | 0 | low-risk-preflight, no-native, small-apk, normal-gradle-root, low-risk-candidate, modern-gradle, has-declared-dependencies | ok: `data/results/evaluation/low-risk-real-apk-batch/report-real-blue-square-speedometer/report.json` | Selected by low-risk preflight: no native ABI, small APK/source tarball, modern AGP project, declared Maven dependencies, and quick Gradle dependency-tree success. |
| Bubble | `org.woheller69.level` | 3.4 (34) | source-validated-real | 1 | 0 | 7 | low-risk-preflight, no-native, small-apk, normal-gradle-root, low-risk-candidate, modern-gradle, has-declared-dependencies | ok: `data/results/evaluation/low-risk-real-apk-batch/report-real-bubble/report.json` | Selected by low-risk preflight: no native ABI, small APK/source tarball, modern AGP project, declared Maven dependencies, and quick Gradle dependency-tree success. |
| Audio Source | `fr.dzx.audiosource` | 1.5 (7) | source-validated-real | 1 | 0 | 3 | low-risk-preflight, no-native, small-apk, normal-gradle-root, low-risk-candidate, modern-gradle, has-declared-dependencies | ok: `data/results/evaluation/low-risk-real-apk-batch/report-real-audio-source/report.json` | Selected by low-risk preflight: no native ABI, small APK/source tarball, modern AGP project, declared Maven dependencies, and quick Gradle dependency-tree success. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
