# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 4 |
| Source tarballs available | 4 |
| Dependency trees captured | 4 |
| Source validations completed | 4 |
| Script failures | 0 |
| Source root | `data/source/low-risk-apk-preflight` |
| Validation root | `data/results/source-validation/low-risk-real-apk-batch` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Stopwatch | 1.6 (7) | source-validated-partial | ok: `data/source/low-risk-apk-preflight/stopwatch/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/low-risk-real-apk-batch/stopwatch/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 4/5 confirmed, 1 mismatch(es), 0 missing: `data/results/source-validation/low-risk-real-apk-batch/stopwatch/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Blue Square Speedometer | 1.1.0 (13) | source-validated-no-maven-signal | ok: `data/source/low-risk-apk-preflight/blue-square-speedometer/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/low-risk-real-apk-batch/blue-square-speedometer/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 0/0 confirmed, 0 mismatch(es), 0 missing: `data/results/source-validation/low-risk-real-apk-batch/blue-square-speedometer/source-validation/source-validation.md` | Record as successful no-Maven-signal control; do not use as accuracy evidence. |
| Bubble | 3.4 (34) | source-validated-partial | ok: `data/source/low-risk-apk-preflight/bubble/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/low-risk-real-apk-batch/bubble/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 1/7 confirmed, 6 mismatch(es), 0 missing: `data/results/source-validation/low-risk-real-apk-batch/bubble/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Audio Source | 1.5 (7) | source-validated-partial | ok: `data/source/low-risk-apk-preflight/audio-source/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/low-risk-real-apk-batch/audio-source/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 0/3 confirmed, 3 mismatch(es), 0 missing: `data/results/source-validation/low-risk-real-apk-batch/audio-source/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Legacy Rescue Follow-Up

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| DNG Processor | 5 (5) | source-validated-no-maven-signal | ok: `data/source/low-risk-apk-preflight/dng-processor/source.tar.gz` | ok: `data/results/source-validation/low-risk-apk-preflight-gradle/dng-processor/docker-app-releaseRuntimeClasspath-gradle5.1.1-jdk11.validation-copy.txt` | ok: 0/0 emitted Maven components; source tree contains 2 Maven components: `data/results/source-validation/low-risk-apk-preflight-gradle/dng-processor/source-validation-gradle5.1.1-jdk11-validation-copy/source-validation.md` | Record as successful legacy-toolchain rescue and no-Maven-signal control; do not use as accuracy evidence. |
| Private DNS Quick Tile | 1.5 (6) | source-validated-no-maven-signal | ok: `data/source/low-risk-apk-preflight/private-dns-quick-tile/source.tar.gz` | ok: `data/results/source-validation/low-risk-apk-preflight-gradle/private-dns-quick-tile/docker-app-releaseRuntimeClasspath-gradle6.1.1-jdk11.txt` | ok: 0/0 emitted Maven components; source tree contains 2 Maven components: `data/results/source-validation/low-risk-apk-preflight-gradle/private-dns-quick-tile/source-validation-gradle6.1.1-jdk11/source-validation.md` | Record as successful legacy-toolchain rescue and no-Maven-signal control; do not use as accuracy evidence. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
