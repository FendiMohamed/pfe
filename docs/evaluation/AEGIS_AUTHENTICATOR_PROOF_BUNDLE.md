# Aegis Authenticator Proof Bundle

This note records the Aegis Authenticator proof bundle. It is a source-validated partial-version-mismatch case, not a clean source-validated accuracy case.

## APK And Source Proof

| Field | Value |
|---|---|
| App | Aegis Authenticator |
| Package | `com.beemdevelopment.aegis` |
| APK version | `3.4.2` |
| APK versionCode | `81` |
| APK path | `data/test_apks/real/aegis-authenticator/aegis-authenticator.apk` |
| APK SHA-256 | `ab633d31cc0fa49e3ae29a3b816a7fcbe04033a3227f42bd30cf86fcd3be4159` |
| Source tarball | `data/source/aegis-authenticator-3.4.2/source.tar.gz` |
| Source tarball SHA-256 | `0478420f7b0a0181ecc83adbddfe915389be3d83bf27c3c615be2ef37a6b4868` |
| F-Droid metadata | `data/test_apks/real/aegis-authenticator/fdroid-metadata.yml` |
| F-Droid source commit | `59d5c640d6a2d0d16f243dbdd735758eed65bc63` |
| F-Droid subdir/flavor | `app` / Gradle `yes` |

The APK manifest matches the selected F-Droid build: package `com.beemdevelopment.aegis`, versionName `3.4.2`, and versionCode `81`.

## APK Structure

| Field | Value |
|---|---|
| DEX files | 2 standard DEX files: `classes.dex`, `classes2.dex` |
| Multidex | true |
| Native files | 8 |
| Native ABIs | `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64` |
| minSdk / targetSdk | `23` / `35` |
| Extraction risk | low |
| Obfuscation risk | low, score `0.20` |

This makes Aegis a useful security/crypto real-app case with AndroidX, multidex, source validation, and small native barcode-scanning libraries.

## MVP Report Result

| Field | Value |
|---|---:|
| Report folder | `data/results/report-real-aegis-authenticator/` |
| Maven SBOM components | 7 |
| Native file components | 8 |
| OSV vulnerabilities | 0 |

Detected Maven components after adding source-used `androidx.lifecycle:lifecycle-runtime-android@2.9.0` to calibration:

| Component | Selected version | Source validation |
|---|---:|---|
| `androidx.exifinterface:exifinterface` | `1.3.6` | confirmed |
| `androidx.concurrent:concurrent-futures` | `1.1.0` | confirmed |
| `androidx.startup:startup-runtime` | `1.1.1` | confirmed |
| `androidx.appcompat:appcompat` | `1.7.0` | confirmed |
| `androidx.recyclerview:recyclerview` | `1.4.0` | confirmed |
| `androidx.viewpager2:viewpager2` | `1.0.0` | version mismatch; source resolves `1.1.0` |
| `androidx.lifecycle:lifecycle-runtime-android` | `2.9.0` | confirmed |

## Source Validation

| Field | Value |
|---|---:|
| Gradle tree | `data/results/source-validation/aegis-authenticator/releaseRuntimeClasspath.txt` |
| Validation folder | `data/results/source-validation/aegis-authenticator-report-validation/` |
| Source components parsed | 144 |
| Emitted SBOM components | 7 |
| Confirmed versions | 6 |
| Version mismatches | 1 |
| Missing coordinates | 0 |

Gradle notes:

- The F-Droid source archive is tar-formatted despite the `.tar.gz` suffix, so Docker extraction used `tar -xf`.
- Project Gradle `9.5.0` failed because the Aegis build script uses `exec` during project evaluation.
- Cached Gradle `8.13` generated `releaseRuntimeClasspath`.
- The source tarball has no `.git` directory, but the build script calls `git rev-parse`; a temporary Git snapshot was created inside `/tmp` only for dependency-tree generation.

## Interpretation

Aegis should be counted as source-validated partial-mismatch evidence:

- it confirms APK extraction, manifest metadata, multidex, native file reporting, report generation, OSV querying, Gradle dependency-tree generation, and source validation;
- it adds a security/crypto app that is simpler than K-9 and FairEmail;
- it should not be counted as a fully clean version-accuracy case because `androidx.viewpager2:viewpager2` remains selected as `1.0.0` while the source resolves `1.1.0`;
- the Lifecycle mismatch was fixed by adding the source-used Android target variant `lifecycle-runtime-android@2.9.0` to calibration.
