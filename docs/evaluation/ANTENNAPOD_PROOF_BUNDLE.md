# AntennaPod Proof Bundle

This note records the AntennaPod `3.11.4` source-validation proof. It is a useful real APK case because it is mostly correct but still exposes one honest version-level limitation.

## APK And Source Proof

| Field | Value |
|---|---|
| App | AntennaPod |
| Package | `de.danoeh.antennapod` |
| APK version | `3.11.4` |
| APK versionCode | `3110495` |
| APK path | `data/test_apks/real/antennapod/antennapod.apk` |
| APK SHA-256 | `8faee459f952e62e5c12be18620911b01c15b5fa0ee67768dcf8ae1e1a68b09c` |
| F-Droid source tarball | `data/source/antennapod/source.tar.gz` |
| F-Droid source tarball SHA-256 | `ae23465c744ea643157f8212b53fcc7c99ea4cd7a3b7d562541f040edef95aab` |
| GitHub source archive | `data/source/antennapod/github-source.tar.gz` |
| GitHub source archive SHA-256 | `c74c5946c16bbf90c8584d9000e2f34f57a3f71eb412701934feb5d60aebc439` |
| F-Droid metadata | `data/test_apks/real/antennapod/fdroid-metadata.yml` |
| F-Droid source commit | `6c3492af7239b46e8c9933ff04984fcdd07c3a6f` |
| F-Droid subdir/flavor | `app` / `free` |

The APK manifest matches the selected F-Droid build: package `de.danoeh.antennapod`, versionName `3.11.4`, and versionCode `3110495`.

## APK Structure

| Field | Value |
|---|---|
| DEX files | 3 standard DEX files: `classes.dex`, `classes2.dex`, `classes3.dex` |
| Multidex | true |
| Native files | 4 |
| Native ABIs | `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64` |
| Native library family | `libconscrypt_jni.so` |
| minSdk / targetSdk | `21` / `35` |
| Extraction risk | low |
| Obfuscation risk | low, score `0.20` |

## MVP Report And Validation Result

| Field | Value |
|---|---:|
| Report folder | `data/results/report-real-antennapod/` |
| Dependency tree | `data/results/source-validation/antennapod/freeReleaseRuntimeClasspath.txt` |
| Source validation | `data/results/source-validation/antennapod-report-validation/source-validation.md` |
| Maven SBOM components | 20 |
| Native file components | 4 |
| OSV vulnerabilities | 0 |
| Source components parsed | 138 |
| Confirmed SBOM versions | 19 |
| Version mismatches | 1 |
| Missing coordinates | 0 |

## Calibration Step

Initial AntennaPod validation found 18/20 confirmed versions. Two source-used versions were missing from the calibrated DB:

- `androidx.work:work-runtime@2.10.3`
- `androidx.core:core@1.16.0`

After adding those versions and rebuilding the calibrated combined DB, `work-runtime` became confirmed. The combined calibrated DB now has 89 components.

## Remaining Limitation

The remaining mismatch is:

| Component | SBOM selected | Source resolved | Notes |
|---|---:|---:|---|
| `androidx.core:core` | `1.15.0` | `1.16.0` | Score near-tie: selected `1.15.0` score `0.490`, alternative `1.16.0` score `0.484`. |

This should not be forced by a generic newer-version rule. It is the same type of lesson as NewPipe's Startup case: bytecode-near-equivalent AndroidX versions need metadata coherence or stronger version-distinctive evidence.

## Interpretation

AntennaPod is a strong source-validated partial-mismatch case:

- real modern app;
- multidex;
- native `.so` reporting boundary;
- resolved Gradle dependency tree available;
- 19/20 emitted Maven SBOM components confirmed;
- one documented version limitation, not hidden.
