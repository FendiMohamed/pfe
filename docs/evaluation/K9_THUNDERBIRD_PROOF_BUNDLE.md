# K-9 / Thunderbird Android Proof Bundle

This note records the current K-9 / Thunderbird Android proof attempt. It is a useful source-linked real APK case, but it is not admitted as a clean source-validated accuracy case because the resolved Gradle dependency tree is currently blocked.

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
| `androidx.swiperefreshlayout:swiperefreshlayout` | `1.2.0` | catalog declares `1.1.0`; likely mismatch until resolved tree confirms |
| `androidx.lifecycle:lifecycle-runtime` | `2.6.2` | catalog declares Lifecycle `2.10.0`; likely mismatch until resolved tree confirms |
| `androidx.localbroadcastmanager:localbroadcastmanager` | `1.0.0` | catalog declares `1.1.0`; likely mismatch until resolved tree confirms |

The remaining emitted components are likely transitive and require the full resolved Gradle tree before making version-correctness claims.

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

The catalog check supports using K-9 as a source-linked diversity case, but it is not enough to admit K-9 into source-validated accuracy metrics.

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

Current blocker:

- Gradle `9.5.0` and a temporary source-declared Gradle `9.4.0` both stalled after K-9's included `build-plugin` setup for 30 minutes.
- A configuration-cache-disabled Gradle `9.5.0` run failed resolving `org.gradle.kotlin.kotlin-dsl` `6.5.7`.
- A fresh validation-only extraction added `google()` and `mavenCentral()` before `gradlePluginPortal()` in the included build-plugin settings to avoid resolving TensorFlow metadata through the plugin portal first. That retry advanced into the included `build-plugin` Kotlin/resource tasks, but still timed out before producing `fossReleaseRuntimeClasspath`.

Therefore K-9 is currently classified as `partial-gradle-blocked`, not `source-validated-real`.

## Interpretation

This is a valuable research case precisely because it is not perfect:

- it confirms APK extraction, manifest metadata, multidex, native file reporting, and OSV querying on a modern security-sensitive app;
- it provides source and version-catalog evidence for some emitted components;
- it exposes a realistic source-validation blocker caused by complex Gradle build logic;
- it must not be used for precision/recall or full version-accuracy claims until the resolved dependency tree is generated.
