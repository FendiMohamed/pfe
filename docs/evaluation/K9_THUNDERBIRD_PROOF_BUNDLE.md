# K-9 / Thunderbird Android Proof Bundle

This note records the current K-9 / Thunderbird Android proof. It is now admitted as source-validated partial evidence after a validation-only included-build/plugin-lite rescue produced the resolved `fossReleaseRuntimeClasspath` tree. It is not a clean source-validated accuracy case because 6 of 11 emitted Maven versions still mismatch source.

## APK And Source Proof

| Field | Value |
|---|---|
| App | K-9 Mail / Thunderbird Android |
| Package | `com.fsck.k9` |
| APK version | `18.0` |
| APK versionCode | `39035` |
| APK path | `data/test_apks/real/k9-thunderbird-android/k9-thunderbird-android.apk` |
| APK SHA-256 | `1381c04bd9619749ed965c9f26fe8de8196e2b0dbb8a4eda345f99d19dfed43b` |
| Source tarball | `data/source/k9-thunderbird-android-18.0/source.tar.gz` |
| Source tarball SHA-256 | `4a8c0710984a7386159c8fc0a69d57fe26827b87ec17093464b31bf0ebd707f7` |
| F-Droid metadata | `data/test_apks/real/k9-thunderbird-android/fdroid-metadata.yml` |
| F-Droid source commit | `23016c71d2f075700a0e258b9fe374bd06d8257b` |
| F-Droid subdir/flavor | `app-k9mail` / `foss` |

The APK manifest matches the selected F-Droid build: package `com.fsck.k9`, versionName `18.0`, and versionCode `39035`.

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

This makes K-9 a good real-app dataset candidate for modern Android, multidex, security/email, networking, and native-file boundary coverage.

## MVP Report Result

| Field | Value |
|---|---:|
| Report folder | `data/results/report-real-k9-thunderbird-android/` |
| Maven SBOM components | 11 |
| Native file components | 8 |
| OSV vulnerabilities | 0 |

Detected Maven components:

| Component | Selected version | Source catalog status |
|---|---:|---|
| `androidx.appcompat:appcompat` | `1.7.1` | catalog declares `1.7.1` |
| `androidx.recyclerview:recyclerview` | `1.4.0` | catalog declares `1.4.0` |
| `androidx.fragment:fragment` | `1.8.9` | catalog declares `1.8.9` |
| `com.squareup.okio:okio-jvm` | `3.16.4` | catalog declares Okio `3.16.4`; JVM artifact-family mapping is expected |
| `androidx.swiperefreshlayout:swiperefreshlayout` | `1.2.0` | resolved tree confirms source version `1.1.0`, version mismatch |
| `androidx.lifecycle:lifecycle-runtime` | `2.6.2` | resolved tree confirms source version `2.10.0`, version mismatch |
| `androidx.localbroadcastmanager:localbroadcastmanager` | `1.0.0` | resolved tree confirms source version `1.1.0`, version mismatch |

The remaining emitted components are now compared against the resolved Gradle tree in the source-validation report.

## Version Catalog Check

A bounded catalog-only check was added at:

```text
data/results/source-validation/k9-thunderbird-android/k9-version-catalog-validation.md
```

This check is weaker than resolved Gradle dependency-tree validation because it compares emitted components only against declared `libs.versions.toml` aliases. It does not prove transitive resolution or final APK variant selection.

Summary:

| Status | Count |
|---|---:|
| Exact catalog confirmations | 3 |
| Exact catalog version mismatches | 2 |
| Artifact-family confirmations | 1 |
| Artifact-family version mismatches | 1 |
| Not declared in catalog | 4 |

The catalog check is retained as weak supporting evidence. K-9 is admitted because the resolved runtime dependency tree and `validate-source-deps` output now exist.

## Gradle Dependency Tree Status

Attempted command target:

```text
:app-k9mail:dependencies --configuration fossReleaseRuntimeClasspath
```

F-Droid build metadata requires these source edits before the Gradle run:

```text
sed -i -e 's|maven.mozilla.org/maven2|jitpack.io|' -e '/glean/d' -e '/googleplay/d' -e '/:app-thunderbird/d' -e '/foojay/d' ../settings.gradle.kts
sed -i -e 's/feature.funding.googleplay/feature.funding.link/' build.gradle.kts
```

Older blocker context:

- Gradle `9.5.0` and a temporary source-declared Gradle `9.4.0` both stalled after K-9's included `build-plugin` setup for 30 minutes.
- A configuration-cache-disabled Gradle `9.5.0` run failed resolving `org.gradle.kotlin.kotlin-dsl` `6.5.7`.
- A fresh validation-only extraction added `google()` and `mavenCentral()` before `gradlePluginPortal()` in the included build-plugin settings to avoid resolving TensorFlow metadata through the plugin portal first. That retry advanced into the included `build-plugin` Kotlin/resource tasks, but still timed out before producing `fossReleaseRuntimeClasspath`.

Successful rescue:

- A validation-only source copy at `data/results/source-validation/k9-thunderbird-android/source-plugin-lite/` keeps the `app-k9mail` `fossRelease` runtime project graph while disabling build-time quality, test, full-flavor, and plugin overhead that is irrelevant to dependency-tree capture.
- Docker Gradle `9.5.0` generated `data/results/source-validation/k9-thunderbird-android/fossReleaseRuntimeClasspath.plugin-lite-runtimegraph-composefix.txt`.
- The tree contains 333 parsed source components and ends with `BUILD SUCCESSFUL in 7m 11s`.

## Source Dependency Validation

`validate-source-deps` was run against:

```text
data/results/report-real-k9-thunderbird-android/sbom.cdx.json
data/results/source-validation/k9-thunderbird-android/fossReleaseRuntimeClasspath.plugin-lite-runtimegraph-composefix.txt
```

Output:

```text
data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.md
data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.json
```

Summary:

| Group | Components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| SBOM components | 11 | 5 | 6 | 0 |

K-9 is now classified as `source-validated-partial`, not blocked.

## Interpretation

This is a valuable research case precisely because it is not perfect:

- it confirms APK extraction, manifest metadata, multidex, native file reporting, and OSV querying on a modern security-sensitive app;
- it provides resolved source dependency evidence for 11 emitted Maven components;
- it exposes a realistic build-system rescue pattern for complex included Gradle build logic;
- it must not be described as clean because 6 emitted Maven versions still mismatch source.
