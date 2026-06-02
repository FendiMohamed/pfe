# VLC Android Proof Bundle

## Case Identity

| Field | Value |
|---|---|
| App | VLC Android |
| Package | `org.videolan.vlc` |
| APK version | `3.7.1` / code `13070106` |
| F-Droid commit | `baeb1edae0678927ebe16d482d979e9c7e75ead6` |
| F-Droid subdir | `application/app` |
| ABI | `arm64-v8a` |
| APK SHA-256 | `355ff246a0348c094a256926ea31cbec92701a2faca3d41d49170798c550ee3b` |
| Source tarball SHA-256 | `0c0cafe8bc69b4313ba031e74469e96bd20a15a57f1377439fe2ac45cefbc421` |

## Artifacts

| Artifact | Path |
|---|---|
| APK | `data/test_apks/real/vlc-android/vlc-android.apk` |
| APK metadata | `data/test_apks/real/vlc-android/metadata.json` |
| F-Droid metadata | `data/test_apks/real/vlc-android/fdroid-metadata.yml` |
| Source tarball | `data/source/vlc-android-3.7.1/source.tar.gz` |
| Extracted source | `data/source/vlc-android-3.7.1/org.videolan.vlc_13070106_src.tar.gz` |
| Dependency tree script | `data/results/source-validation/vlc-android/run-gradle-deps.sh` |
| Dependency tree | `data/results/source-validation/vlc-android/releaseRuntimeClasspath.txt` |
| MVP report | `data/results/report-real-vlc-android/report.json` |
| CycloneDX SBOM | `data/results/report-real-vlc-android/sbom.cdx.json` |
| Source validation | `data/results/source-validation/vlc-android-report-validation/source-validation.json` |

## APK Evidence

- Manifest parsing succeeded: package `org.videolan.vlc`, versionName `3.7.1`, versionCode `13070106`, minSdk `17`, targetSdk `36`.
- The APK contains 6 standard DEX files and 4 native `arm64-v8a` libraries.
- Native file components are reported as hashes only:
  - `libc++_shared.so`
  - `libmla.so`
  - `libvlc.so`
  - `libvlcjni.so`
- Extraction risk is low; obfuscation risk is low (`0.20`) because many emitted Maven versions are low-confidence candidates.

## Report Result

The calibrated shared DB report emits:

| Metric | Value |
|---|---:|
| Maven SBOM components | 26 |
| Native file components | 4 |
| OSV findings | 3 |
| Confirmed OSV findings | 1 |
| Potential OSV findings | 2 |

Vulnerability interpretation is confidence-aware. The Okio finding is marked confirmed because the APK-side version evidence is high, while the Ktor and OkHttp findings are potential because their selected versions are candidate/low confidence.

## Source Validation

The resolved Gradle dependency tree was generated from a fresh in-container extraction of the F-Droid source tarball. This avoids the Windows tar limitation where two source symlinks named `values-iw` cannot be materialized.

The Gradle run applies the F-Droid prebuild edits and one validation-only patch: the source tarball is not a Git checkout, so `git rev-parse --short HEAD` is replaced with the known F-Droid commit prefix `baeb1ed` for dependency-tree generation.

| Metric | Value |
|---|---:|
| Source components parsed | 209 |
| SBOM components checked | 26 |
| Confirmed versions | 6 |
| Version mismatches | 20 |
| Missing coordinates | 0 |

Interpretation: VLC is admitted as a source-validated partial case. It is not a clean accuracy case. It is valuable because it combines a large native-heavy media APK, multidex Java/Kotlin code, older source-resolved dependency versions, and native hash-only SBOM boundaries.

## Main Mismatches

The mismatches are mostly dependency-era/reference-coverage cases rather than missing-coordinate failures. Examples include:

| Coordinate | MVP selected | Source resolved |
|---|---:|---:|
| `androidx.core:core` | `1.9.0` | `1.12.0` |
| `androidx.recyclerview:recyclerview` | `1.2.1` | `1.3.2` |
| `com.squareup.okhttp3:okhttp` | `4.9.1` | `4.9.3` |
| `com.squareup.retrofit2:retrofit` | `2.8.1` | `2.7.1` |
| `io.ktor:ktor-client-core-jvm` | `2.3.12` | `2.3.7` |
| `org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm` | `1.7.3` | `1.7.1` |

## Classification

| Dimension | Label |
|---|---|
| Dataset layer | Source-validated real APK |
| Result class | Partial version mismatch |
| APK family | Native-heavy media app |
| Multidex | Yes |
| Native handling | Hash-only CycloneDX file components |
| Metric eligibility | Count in source-validated emitted-version confirmation rate; keep clean/partial split visible |

## Next Use

Use VLC as a hard-case guard when improving reference coverage or dependency-coherence diagnostics. Do not use it to justify a generic newer-version or older-version rule; the mismatches go in both directions and need source-supported, non-regressing experiments.
