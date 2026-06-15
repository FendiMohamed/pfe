# FairEmail Proof Bundle

This note records the current FairEmail proof attempt. It is now admitted as a source-validated partial-version-mismatch real APK case. The original source tree still requires Android NDK `27.2.12479018`, so the dependency tree was generated from a validation-only source copy with native build disabled. That copy is used only for Maven runtime dependency resolution; native build output is not claimed.

## APK And Source Proof

| Field | Value |
|---|---|
| App | FairEmail |
| Package | `eu.faircode.email` |
| APK version | `1.2315` |
| APK versionCode | `2315` |
| APK path | `data/test_apks/real/fairemail/fairemail.apk` |
| APK SHA-256 | `6154673f6282c4d884d7dacb6ae5b264cc3dc4271bec449721bb2f19bfd4e602` |
| Source tarball | `data/source/fairemail-1.2315/source.tar.gz` |
| Source tarball SHA-256 | `710cc57773e422467b185c4ac75291989d423c70c30e8e39f72e1c61667d80bf` |
| F-Droid metadata | `data/test_apks/real/fairemail/fdroid-metadata.yml` |
| F-Droid source commit | `5d3dea660e8bb1aa0082e78f338123d0fd8c4287` |
| F-Droid subdir/flavor | `app` / `fdroid` |

The APK manifest matches the selected F-Droid build: package `eu.faircode.email`, versionName `1.2315`, and versionCode `2315`.

## APK Structure

| Field | Value |
|---|---|
| DEX files | 3 standard DEX files: `classes.dex`, `classes2.dex`, `classes3.dex` |
| Multidex | true |
| Native files | 4 |
| Native ABIs | `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64` |
| minSdk / targetSdk | `21` / `36` |
| Extraction risk | low |
| Obfuscation risk | low, score `0.20` |

This makes FairEmail a good real-app dataset candidate for modern Android, multidex, email/security, networking, AndroidX, and native-file boundary coverage.

## MVP Report Result

| Field | Value |
|---|---:|
| Report folder | `data/results/report-real-fairemail/` |
| Maven SBOM components | 13 |
| Native file components | 4 |
| OSV vulnerabilities | 0 |

Detected Maven components:

| Component | Selected version | Current status |
|---|---:|---|
| `androidx.exifinterface:exifinterface` | `1.4.2` | likely, needs resolved-tree validation |
| `androidx.localbroadcastmanager:localbroadcastmanager` | `1.0.0` | candidate, needs resolved-tree validation |
| `androidx.concurrent:concurrent-futures` | `1.1.0` | candidate, needs resolved-tree validation |
| `androidx.appcompat:appcompat` | `1.7.1` | candidate, needs resolved-tree validation |
| `androidx.swiperefreshlayout:swiperefreshlayout` | `1.0.0` | candidate, needs resolved-tree validation |
| `androidx.recyclerview:recyclerview` | `1.4.0` | likely, needs resolved-tree validation |
| `androidx.fragment:fragment` | `1.8.9` | likely, needs resolved-tree validation |
| `androidx.startup:startup-runtime` | `1.2.0` | likely, needs resolved-tree validation |
| `androidx.work:work-runtime` | `2.10.5` | candidate, needs resolved-tree validation |
| `androidx.lifecycle:lifecycle-runtime` | `2.6.2` | candidate, needs resolved-tree validation |
| `androidx.activity:activity` | `1.10.1` | candidate, needs resolved-tree validation |
| `androidx.lifecycle:lifecycle-viewmodel` | `2.6.2` | candidate, needs resolved-tree validation |
| `androidx.core:core` | `1.18.0` | candidate, needs resolved-tree validation |

## Gradle Dependency Tree Status

Attempted command target:

```text
:app:dependencies --configuration fdroidReleaseRuntimeClasspath
```

Original blocker:

- Gradle `9.5.0` reached `Configure project :app`.
- The build then tried to install Android NDK `27.2.12479018`.
- The Docker runtime currently has no `/opt/android-sdk/ndk`.
- The run timed out before a resolved dependency tree was produced.

Workaround used for validation:

- Created validation-only source copy: `data/results/source-validation/fairemail/source-no-native/`.
- Disabled only `externalNativeBuild`, `ndkVersion`, and ABI filter blocks in that copy.
- Generated resolved runtime dependency tree successfully at `data/results/source-validation/fairemail/fdroidReleaseRuntimeClasspath.no-native.txt`.
- Kept the original source proof under `data/source/fairemail-1.2315/source/` unchanged.

FairEmail is therefore no longer `partial-toolchain-blocked`; it is `source-validated-partial` for Java/Kotlin Maven dependencies.

## Source Validation Result

| Field | Value |
|---|---:|
| Validation folder | `data/results/source-validation/fairemail-report-validation/` |
| Source components parsed | 183 |
| SBOM Maven components checked | 13 |
| Confirmed versions | 7 |
| Version mismatches | 6 |
| Missing coordinates | 0 |

Confirmed:

- `androidx.exifinterface:exifinterface@1.4.2`
- `androidx.concurrent:concurrent-futures@1.1.0`
- `androidx.appcompat:appcompat@1.7.1`
- `androidx.recyclerview:recyclerview@1.4.0`
- `androidx.fragment:fragment@1.8.9`
- `androidx.startup:startup-runtime@1.2.0`
- `androidx.work:work-runtime@2.10.5`

Version mismatches:

- `androidx.localbroadcastmanager:localbroadcastmanager` selected `1.0.0`, source resolves `1.1.0`.
- `androidx.swiperefreshlayout:swiperefreshlayout` selected `1.0.0`, source resolves `1.2.0-beta01`.
- `androidx.lifecycle:lifecycle-runtime` selected `2.6.2`, source resolves `2.8.6`.
- `androidx.activity:activity` selected `1.10.1`, source resolves `1.11.0`.
- `androidx.lifecycle:lifecycle-viewmodel` selected `2.6.2`, source resolves `2.8.6`.
- `androidx.core:core` selected `1.18.0`, source resolves `1.17.0`.

## Interpretation

This is still a useful proof attempt:

- it confirms APK extraction, manifest metadata, multidex, native file reporting, report generation, and OSV querying on a security-sensitive real app;
- it expands the source-validated evidence beyond K-9 with another email/security application;
- it exposes a concrete toolchain gap: source validation for some native-enabled Android apps may require installing/caching the required Android NDK, or a carefully documented no-native dependency-resolution copy;
- it should be counted as a partial source-validated Maven dependency case, not as a clean exact-version case.
