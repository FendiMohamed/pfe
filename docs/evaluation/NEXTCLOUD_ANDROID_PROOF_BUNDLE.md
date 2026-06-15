# Nextcloud Android Proof Bundle

Nextcloud Android is a source-linked, source-validated real APK case for the dataset. It is useful as a large modern cloud-sync app with many AndroidX/Compose/Kotlin dependencies, multidex, and native libraries. It is not a clean source-validated accuracy case because the current shared calibrated DB still has many version mismatches on this very new dependency stack.

## Identity Proof

| Field | Result |
|---|---|
| App | Nextcloud Android |
| Package | `com.nextcloud.client` |
| APK | `data/test_apks/real/nextcloud-android/nextcloud.apk` |
| APK SHA-256 | `faaa64b5d88724a6a6461dfb01ed5938f0ffbc111fe53c456ec869d82ec50334` |
| F-Droid versionName | `33.1.0` |
| F-Droid versionCode | `330010090` |
| Source tag | `stable-33.1.0` |
| Source repo | `https://github.com/nextcloud/android.git` |
| Source archive | `data/source/nextcloud-android-33.1.0/source.tar.gz` |
| Source archive SHA-256 | `f49d474fb2bfed9e3854c1ba029cfa212cddc47ce5b7cf77378df03eaaa84198` |
| F-Droid metadata | `data/test_apks/real/nextcloud-android/fdroid-metadata.yml` |

The APK manifest matches the F-Droid build metadata: package `com.nextcloud.client`, versionName `33.1.0`, and versionCode `330010090`. The F-Droid build block points to commit/tag `stable-33.1.0`, subdir `app`, and Gradle flavor `generic`.

## APK Characteristics

| Field | Result |
|---|---:|
| Standard DEX files | 6 |
| Multidex | true |
| Native libraries | 12 |
| Native ABIs | `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64` |
| Native filenames | `libandroidx.graphics.path.so`, `libconscrypt_jni.so`, `libpl_droidsonroids_gif.so` |
| minSdk | 28 |
| targetSdk | 36 |
| Extraction risk | low |
| Obfuscation risk | low (`0.00`) |
| Nonstandard DEX files | 0 |
| OSV vulnerabilities | 0 |

## Source Dependency Tree

The validated Gradle configuration is:

```text
genericReleaseRuntimeClasspath
```

Evidence path:

```text
data/results/source-validation/nextcloud-android/genericReleaseRuntimeClasspath.txt
```

Gradle notes:

- The F-Droid build uses subdir `app` and flavor `generic`.
- The extracted source root is `data/source/nextcloud-android-33.1.0/com.nextcloud.client_330010090_src.tar.gz/`.
- Docker Gradle `9.5.0` generated the dependency tree successfully from the source root with `:app:dependencies --configuration genericReleaseRuntimeClasspath`.
- PowerShell redirection wrote the first tree as UTF-16, so the generated dependency tree was converted to UTF-8 before running `validate-source-deps`.

## MVP Report

| Artifact | Path |
|---|---|
| Markdown report | `data/results/report-real-nextcloud-android/report.md` |
| HTML report | `data/results/report-real-nextcloud-android/report.html` |
| CycloneDX SBOM | `data/results/report-real-nextcloud-android/sbom.cdx.json` |
| OSV output | `data/results/report-real-nextcloud-android/osv-vulnerabilities.json` |
| Source validation | `data/results/source-validation/nextcloud-android-report-validation/source-validation.md` |

Current report result:

```text
Detected Maven components: 29
Native file components: 12
OSV vulnerabilities: 0
```

Source validation result:

```text
Source components parsed: 250
SBOM components: 29
Confirmed: 22
Version mismatches: 6
Missing: 1
```

Confirmed components:

- `commons-codec:commons-codec@1.15`
- `androidx.exifinterface:exifinterface@1.4.2`
- `androidx.lifecycle:lifecycle-runtime-android@2.10.0`
- `com.google.code.gson:gson@2.13.2`
- `androidx.compose.ui:ui-android@1.10.6`
- `androidx.core:core@1.18.0`
- `org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm@1.9.0`
- `org.jetbrains.kotlin:kotlin-stdlib@2.3.10`
- `com.google.android.material:material@1.13.0`
- `androidx.recyclerview:recyclerview@1.3.2`
- `androidx.localbroadcastmanager:localbroadcastmanager@1.0.0`
- `androidx.fragment:fragment@1.8.9`
- `androidx.lifecycle:lifecycle-viewmodel-android@2.10.0`
- `androidx.appcompat:appcompat@1.7.1`
- `androidx.work:work-runtime@2.11.2`
- `androidx.core:core-ktx@1.18.0`
- `androidx.compose.foundation:foundation-android@1.10.6`
- `androidx.compose.runtime:runtime-android@1.10.6`
- `androidx.compose.ui:ui-tooling-preview-android@1.10.6`
- `androidx.lifecycle:lifecycle-livedata@2.10.0`
- `org.jetbrains.kotlinx:kotlinx-coroutines-android@1.9.0`
- `androidx.compose.material3:material3-android@1.4.0`

Version mismatches:

- `androidx.viewpager2:viewpager2`: selected `1.1.0`, source resolves `1.1.0-beta02`.
- `androidx.concurrent:concurrent-futures`: selected `1.3.0`, source resolves `1.2.0`.
- `androidx.startup:startup-runtime`: selected `1.2.0`, source resolves `1.1.1`.
- `com.squareup.okio:okio-jvm`: selected `3.16.4`, source resolves `3.9.0`.
- `androidx.swiperefreshlayout:swiperefreshlayout`: selected `1.0.0`, source resolves `1.2.0`.
- `androidx.activity:activity`: selected `1.10.1`, source resolves `1.9.2`.

Missing/equivalence nuance:

- `com.squareup.okhttp3:okhttp-android@5.3.2` is emitted as a bytecode-bearing Android target artifact, while the Gradle source tree reports public `com.squareup.okhttp3:okhttp@4.12.0`; treat this as an artifact-family validation nuance rather than a clean confirmed version.

The guarded promotions fixed the safe reference-coverage gaps for Gson, Kotlin stdlib, RecyclerView, Compose Foundation/UI/tooling-preview, and now Compose Runtime through scoped app-era coherence. The remaining mismatches are risky version-band ties: several source versions already exist but are not selected (`startup-runtime`, `swiperefreshlayout`), while others are intentionally withheld from global promotion because they regressed other current-control APKs in the full experiment.

## Source-Used Version Experiment

A guarded experiment added 11 Nextcloud source-resolved versions to a separate reference DB:

```text
androidx.activity:activity@1.9.2
androidx.compose.foundation:foundation-android@1.10.6
androidx.compose.runtime:runtime-android@1.10.6
androidx.compose.ui:ui-android@1.10.6
androidx.compose.ui:ui-tooling-preview-android@1.10.6
androidx.concurrent:concurrent-futures@1.2.0
androidx.recyclerview:recyclerview@1.3.2
androidx.viewpager2:viewpager2@1.1.0-beta02
com.google.code.gson:gson@2.13.2
com.squareup.okio:okio-jvm@3.9.0
org.jetbrains.kotlin:kotlin-stdlib@2.3.10
```

Artifacts:

| Field | Value |
|---|---|
| Experiment config | `configs/libraries.nextcloud_experiment.json` |
| Experiment DB | `data/reference_db/reference_features_nextcloud_experiment_combined.sqlite` |
| Experiment summary | `data/results/experiments/nextcloud-source-versions/nextcloud-source-versions-summary.md` |
| Experiment runner | `scripts/evaluate_nextcloud_source_versions.py` |

Full 11-version result for Nextcloud:

```text
App-era current-control shared DB: 21/28 confirmed, 6 mismatches, 1 missing/artifact-family nuance
Full experiment DB: 24/29 confirmed, 4 mismatches, 1 missing/artifact-family nuance
Delta: +3 confirmed, -2 mismatches
```

Remaining Nextcloud mismatches after adding the source-used versions:

- `com.squareup.okio:okio-jvm`: selected `3.7.0`, source resolves `3.9.0`.
- `androidx.startup:startup-runtime`: selected `1.2.0`, source resolves `1.1.1`.
- `androidx.concurrent:concurrent-futures`: selected `1.3.0`, source resolves `1.2.0`.
- `androidx.swiperefreshlayout:swiperefreshlayout`: selected `1.0.0`, source resolves `1.2.0`.
- `com.squareup.okhttp3:okhttp-android@5.3.2` remains an OkHttp public-vs-Android target artifact-family validation nuance.

Full 11-version regression result:

| Case | Fresh control | Experiment | Delta |
|---|---|---|---|
| F-Droid | 23 confirmed, 0 mismatches | 22 confirmed, 1 mismatch | regressed |
| OpenTracks | 19 confirmed, 0 mismatches | 19 confirmed, 0 mismatches | unchanged |
| Tusky | 1 confirmed, 0 mismatches | 1 confirmed, 0 mismatches | unchanged |
| NewPipe | 9 confirmed, 2 mismatches | 7 confirmed, 4 mismatches | regressed |
| AntennaPod | 19 confirmed, 1 mismatch | 18 confirmed, 2 mismatches | regressed |
| KDE Connect | 8 confirmed, 1 mismatch | 8 confirmed, 1 mismatch | unchanged |
| Wikipedia Android | 11 confirmed, 2 mismatches | 11 confirmed, 2 mismatches | unchanged |
| Conversations | 6 confirmed, 2 mismatches, 1 missing | 6 confirmed, 2 mismatches, 1 missing | unchanged |
| Aegis Authenticator | 6 confirmed, 1 mismatch | 6 confirmed, 1 mismatch | unchanged |
| Markor | 6 confirmed, 13 mismatches | 6 confirmed, 13 mismatches | unchanged |
| Nextcloud Android | 21 confirmed, 6 mismatches, 1 missing | 24 confirmed, 4 mismatches, 1 missing | improved |

Runtime-only guarded promotion result:

| Case | App-era current control | Runtime-only promoted DB | Delta |
|---|---|---|---|
| F-Droid | 23 confirmed, 0 mismatches | 23 confirmed, 0 mismatches | unchanged |
| OpenTracks | 19 confirmed, 0 mismatches | 19 confirmed, 0 mismatches | unchanged |
| Tusky | 1 confirmed, 0 mismatches | 1 confirmed, 0 mismatches | unchanged |
| NewPipe | 9 confirmed, 2 mismatches | 9 confirmed, 2 mismatches | unchanged |
| AntennaPod | 19 confirmed, 1 mismatch | 19 confirmed, 1 mismatch | unchanged |
| KDE Connect | 8 confirmed, 1 mismatch | 8 confirmed, 1 mismatch | unchanged |
| Wikipedia Android | 11 confirmed, 2 mismatches | 11 confirmed, 2 mismatches | unchanged |
| Conversations | 6 confirmed, 2 mismatches, 1 missing | 6 confirmed, 2 mismatches, 1 missing | unchanged |
| Aegis Authenticator | 6 confirmed, 1 mismatch | 6 confirmed, 1 mismatch | unchanged |
| Markor | 6 confirmed, 13 mismatches | 6 confirmed, 13 mismatches | unchanged |
| Nextcloud Android | 21 confirmed, 6 mismatches, 1 missing | 22 confirmed, 6 mismatches, 1 missing | improved |

Interpretation: source-used reference coverage can be promoted when it passes a fresh current-control regression run. The safe promoted subset is `foundation-android@1.10.6`, `runtime-android@1.10.6`, `ui-android@1.10.6`, `ui-tooling-preview-android@1.10.6`, `recyclerview@1.3.2`, `gson@2.13.2`, and `kotlin-stdlib@2.3.10`. Runtime is safe only with the scoped Compose app-era coherence rule: unrelated apps leave `runtime-android@1.10.6` uncertain, while Nextcloud has coherent Compose family support.

The remaining source versions are now explicitly triaged in `docs/evaluation/VERSION_BAND_TIE_EVIDENCE.md`. Activity `1.9.2` alone improves Nextcloud but regresses F-Droid, and ViewPager2 `1.1.0-beta02` alone improves Nextcloud but regresses NewPipe and AntennaPod. Concurrent Futures `1.2.0` and Okio-JVM `3.9.0` are also not safe: adding them does not give a clean source-version win under current bytecode evidence. Keep these as documented version-band limitations unless a new independent signal passes the same current-control regression gate.

The matcher now surfaces feature-equivalent version ties as explicit evidence instead of hiding them. This does not improve Nextcloud's current count, but it prevents ambiguous cases such as Startup `1.1.1` vs `1.2.0` from looking like confident exact version claims. The regenerated NewPipe/Wikipedia/Conversations slice under `data/results/experiments/version-ambiguity-signal-current/` confirms the ambiguity note is visible while source-validation metrics stay unchanged.

## Reproduction Commands

Generate the APK report:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/nextcloud-android/nextcloud.apk --output-dir data/results/report-real-nextcloud-android --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
```

Generate the source dependency tree:

```powershell
docker compose run --rm -w /app/data/source/nextcloud-android-33.1.0/com.nextcloud.client_330010090_src.tar.gz apk-sbom /opt/gradle/bin/gradle --no-daemon :app:dependencies --configuration genericReleaseRuntimeClasspath > data\results\source-validation\nextcloud-android\genericReleaseRuntimeClasspath.txt 2> data\results\source-validation\nextcloud-android\gradle-error.log
```

Convert the dependency tree to UTF-8 if PowerShell wrote it as UTF-16:

```powershell
$text = Get-Content -Raw data\results\source-validation\nextcloud-android\genericReleaseRuntimeClasspath.txt
Set-Content -Path data\results\source-validation\nextcloud-android\genericReleaseRuntimeClasspath.txt -Value $text -Encoding utf8
```

Validate the SBOM against source:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-nextcloud-android/sbom.cdx.json --dependency-tree data/results/source-validation/nextcloud-android/genericReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/nextcloud-android-report-validation
```

## Interpretation

Nextcloud should be counted as source-validated partial-mismatch evidence. It strengthens the dataset because it is a large modern app with a very broad dependency tree, modern AndroidX/Compose/Kotlin versions, multidex, native libraries, and a fully generated source dependency tree. It should not be used as a clean version-accuracy case. The main lesson is that large modern apps need calibrated source-version coverage plus stronger version-band/app-era or dependency-coherence safeguards before their near-version outputs can be claimed as exact.
