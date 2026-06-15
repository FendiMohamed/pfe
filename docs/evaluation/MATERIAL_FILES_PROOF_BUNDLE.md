# Material Files Proof Bundle

## Case Identity

| Field | Value |
|---|---|
| App | Material Files |
| Package | `me.zhanghai.android.files` |
| APK version | `1.7.4` / code `39` |
| F-Droid commit | `61a3cffede303d159ee9ad805319b89c21c3aa04` |
| F-Droid subdir | `app` |
| APK SHA-256 | `ebc5138b6f713f0f73b5467a1a8a4ac3ccfcb2e82135372665b6811a8947641f` |
| Source tarball SHA-256 | `3b35020d0d6832dc977223721391fe037bddc463a4622b2743e5d2e7495addba` |

## Artifacts

| Artifact | Path |
|---|---|
| APK | `data/test_apks/real/material-files/material-files.apk` |
| APK metadata | `data/test_apks/real/material-files/metadata.json` |
| F-Droid metadata | `data/test_apks/real/material-files/fdroid-metadata.yml` |
| Source tarball | `data/source/material-files-1.7.4/source.tar.gz` |
| Extracted source | `data/source/material-files-1.7.4/me.zhanghai.android.files_39_src.tar.gz` |
| Validation-only no-native source copy | `data/results/source-validation/material-files/source-no-native` |
| Dependency tree | `data/results/source-validation/material-files/releaseRuntimeClasspath.no-native.txt` |
| MVP report | `data/results/report-real-material-files/report.json` |
| CycloneDX SBOM | `data/results/report-real-material-files/sbom.cdx.json` |
| Source validation | `data/results/source-validation/material-files-report-validation/source-validation.json` |

## APK Evidence

- Manifest parsing succeeded: package `me.zhanghai.android.files`, versionName `1.7.4`, versionCode `39`, minSdk `21`, targetSdk `34`.
- The APK contains 1 standard DEX file and 16 native libraries across `arm64-v8a`, `armeabi-v7a`, `x86`, and `x86_64`.
- Native file components include `libarchive-jni.so`, `libhiddenapi.so`, `libselinux-jni.so`, and `libsyscall.so` for each ABI.
- Extraction risk is low; obfuscation risk is low (`0.20`) but the report notes that emitted components are low-confidence candidates.

## Report Result

The calibrated shared DB report emits:

| Metric | Value |
|---|---:|
| Maven SBOM components | 2 |
| Native file components | 16 |
| OSV findings | 0 |

Detected Maven components:

| Component | MVP selected version | Source resolved version | Result |
|---|---:|---:|---|
| `androidx.lifecycle:lifecycle-runtime` | `2.6.2` | `2.8.2` | version mismatch |
| `androidx.activity:activity` | `1.10.1` | `1.9.0` | version mismatch |

## Source Validation

The F-Droid metadata for versionCode `39` points to source commit `61a3cffede303d159ee9ad805319b89c21c3aa04`, subdir `app`, Gradle build `yes`, nonfree-source removal, and NDK `26.3.11579264`.

Gradle `9.5.0` is incompatible with this source because the build uses `jcenter()`, which is no longer available in Gradle 9. The source-declared Gradle `8.7` reaches configuration but requires the F-Droid NDK. For Maven runtime dependency validation, the project uses a validation-only no-native source copy: F-Droid nonfree-source removal is applied, then `ndkVersion` and `externalNativeBuild` hooks are disabled so `releaseRuntimeClasspath` can be resolved without claiming a native build.

| Metric | Value |
|---|---:|
| Source components parsed | 145 |
| SBOM components checked | 2 |
| Confirmed versions | 0 |
| Version mismatches | 2 |
| Missing coordinates | 0 |

Interpretation: Material Files is admitted as a source-validated partial case. It is useful because it adds a file-manager/network-storage/native-JNI family and shows low-confidence AndroidX version-band drift. It is not a clean exact-version accuracy case.

## Classification

| Dimension | Label |
|---|---|
| Dataset layer | Source-validated real APK |
| Result class | Partial version mismatch |
| APK family | File manager / network storage / native JNI |
| Multidex | No |
| Native handling | Hash-only CycloneDX file components |
| Metric eligibility | Count in source-validated emitted-version confirmation rate; keep clean/partial split visible |

## Next Use

Use Material Files as a guard for future AndroidX version-band and sparse-identity improvements. Do not use it to justify a generic newer-version rule: one mismatch selects newer than source (`activity`), while the other selects older than source (`lifecycle-runtime`).
