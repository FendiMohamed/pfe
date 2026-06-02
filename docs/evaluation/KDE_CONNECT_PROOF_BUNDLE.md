# KDE Connect Proof Bundle

This note records the KDE Connect `1.35.5` source-validation proof attempt. It is useful because it is a modern, multidex, permissions-heavy AndroidX/Kotlin/Java app with release minification and resource shrinking enabled.

## APK And Source Proof

| Field | Value |
|---|---|
| App | KDE Connect |
| Package | `org.kde.kdeconnect_tp` |
| APK version | `1.35.5` |
| APK versionCode | `13505` |
| APK path | `data/test_apks/real/kde-connect/kde-connect.apk` |
| APK SHA-256 | `77f61f9ba58d5f6402d5b7ad6a2b2f8904e82ccdd038dbb86b6ab693bb470c4e` |
| F-Droid source tarball | `data/source/kde-connect/source.tar.gz` |
| F-Droid source tarball SHA-256 | `31b28cc438d9fb68264a1af03fe39972a7488f0a096311d555cb4bf01ba262fb` |
| F-Droid metadata | `data/test_apks/real/kde-connect/fdroid-metadata.yml` |
| F-Droid source commit | `0f3cc84446065102c064f78d4276bb4ebd00d3c9` |
| Gradle configuration | root `releaseRuntimeClasspath` |

The APK manifest matches the selected F-Droid build: package `org.kde.kdeconnect_tp`, versionName `1.35.5`, and versionCode `13505`.

## APK Structure

| Field | Value |
|---|---|
| DEX files | 2 standard DEX files: `classes.dex`, `classes2.dex` |
| Multidex | true |
| Native files | 4 |
| Native ABIs | `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64` |
| Native library family | `libandroidx.graphics.path.so` |
| minSdk / targetSdk | `23` / `35` |
| Release shrinking | R8/minify enabled and resource shrinking enabled |
| Extraction risk | low |
| Obfuscation risk | low, score `0.20` |

## MVP Report And Validation Result

| Field | Value |
|---|---:|
| Report folder | `data/results/report-real-kde-connect/` |
| Dependency tree | `data/results/source-validation/kde-connect/releaseRuntimeClasspath.txt` |
| Source validation | `data/results/source-validation/kde-connect-validation/source-validation.md` |
| Maven SBOM components | 9 |
| Native file components | 4 |
| OSV vulnerabilities | 0 |
| Source components parsed | 166 |
| Confirmed SBOM versions | 8 |
| Version mismatches | 1 |
| Missing coordinates | 0 |

## Remaining Mismatches

| Component | SBOM selected | Source resolved | Notes |
|---|---:|---:|---|
| `androidx.viewpager2:viewpager2` | `1.1.0` | `1.1.0-beta02` | Source resolves a beta version. Adding it to calibration was tested and rejected because it did not improve validation and selected an older candidate. |

The earlier Lifecycle runtime mismatch was improved by scoped artifact-family coherence. The matcher now selects `androidx.lifecycle:lifecycle-runtime-android@2.10.0` as a low-confidence candidate when the public coordinate is weak and the Android target variant has supported identity evidence. This is not a generic newer-version rule.

## Interpretation

KDE Connect is a source-validated partial-mismatch case:

- real modern app;
- multidex;
- R8/minify and resource shrinking enabled for release;
- permissions-heavy networking/device-integration profile;
- native `.so` reporting boundary through AndroidX graphics path helpers;
- resolved Gradle dependency tree available;
- 8/9 emitted Maven SBOM components confirmed;
- one documented version limitation, not hidden.
