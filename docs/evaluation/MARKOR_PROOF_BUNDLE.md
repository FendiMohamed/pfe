# Markor Proof Bundle

This note records the Markor proof bundle. It is a source-validated partial-version-mismatch case, not a clean source-validated accuracy case.

## APK And Source Proof

| Field | Value |
|---|---|
| App | Markor |
| Package | `net.gsantner.markor` |
| APK version | `2.16.1` |
| APK versionCode | `163` |
| APK path | `data/test_apks/real/markor/markor.apk` |
| APK SHA-256 | `3f9f260dc3e32a1281cb8803eea6f926eef897579f68a5d35f922523974b84b9` |
| Source tarball | `data/source/markor-2.16.1/source.tar.gz` |
| Source tarball SHA-256 | `0faaa23762c509567c48c5195026cf224c0919d83b15c8aa88e28f43abda4858` |
| F-Droid metadata | `data/test_apks/real/markor/fdroid-metadata.yml` |
| F-Droid source commit | `f33eb6a8dfb210f27bfe7294430d4d39b795bd0f` |
| F-Droid subdir/flavor | `app` / `flavorDefault` |

The APK manifest matches the selected F-Droid build: package `net.gsantner.markor`, versionName `2.16.1`, and versionCode `163`.

## APK Structure

| Field | Value |
|---|---|
| DEX files | 2 standard DEX files: `classes.dex`, `classes2.dex` |
| Multidex | true |
| Native files | 0 |
| minSdk / targetSdk | `18` / `35` |
| Extraction risk | medium |
| Obfuscation risk | medium, score `0.35` |

The extraction-risk warning is caused by a syntax-highlighting asset path containing the substring `shell`: `assets/prism/components/prism-shell-session.min.js`. No nonstandard DEX files or native libraries were present.

## MVP Report Result

| Field | Value |
|---|---:|
| Shared-DB report folder | `data/results/report-real-markor/` |
| Maven SBOM components | 19 |
| Native file components | 0 |
| OSV vulnerabilities | 0 |

## Source Validation

| Field | Value |
|---|---:|
| Gradle tree | `data/results/source-validation/markor/flavorDefaultReleaseRuntimeClasspath.txt` |
| Shared-DB validation folder | `data/results/source-validation/markor-report-validation/` |
| Source components parsed | 106 |
| Emitted SBOM components | 19 |
| Confirmed versions | 7 |
| Version mismatches | 12 |
| Missing coordinates | 0 |

Confirmed components:

| Component | Version |
|---|---:|
| `androidx.viewpager2:viewpager2` | `1.0.0` |
| `androidx.recyclerview:recyclerview` | `1.2.1` |
| `com.google.code.gson:gson` | `2.10.1` |
| `androidx.swiperefreshlayout:swiperefreshlayout` | `1.0.0` |
| `androidx.core:core` | `1.9.0` |
| `androidx.localbroadcastmanager:localbroadcastmanager` | `1.0.0` |
| `androidx.startup:startup-runtime` | `1.1.1` |

The remaining 12 emitted coordinates are present in the source tree but with older resolved versions than the SBOM selected. This makes Markor useful as older-dependency drift evidence rather than a clean accuracy case.

## Guarded Coverage Follow-Up

The queued Markor coverage gaps were tested in isolated experiment DBs before any shared promotion:

| Experiment | Result | Decision |
|---|---|---|
| Add `activity@1.6.0`, `concurrent-futures@1.0.0`, and `core@1.9.0` together | Markor improved from 6/19 to 9/19, but F-Droid, OpenTracks, NewPipe, AntennaPod, KDE Connect, Wikipedia, and Aegis regressed. | Do not promote the combined set. |
| Add only `core@1.9.0` | Markor improved from 6/19 to 7/19; all 10 other current-control APKs stayed unchanged. | Promoted to the shared calibrated DB. |

Evidence: `data/results/experiments/markor-coverage-gaps-vs-current-control.md` and `data/results/experiments/markor-core-1-9-0-vs-current-control.md`.

## Source-Used Calibration Experiment

An app-specific calibration experiment added Markor's source-resolved older versions to the reference DB:

```text
androidx.activity:activity@1.6.0
androidx.appcompat:appcompat@1.6.1
androidx.concurrent:concurrent-futures@1.0.0
androidx.core:core@1.9.0
androidx.core:core-ktx@1.9.0
androidx.fragment:fragment@1.3.6
androidx.lifecycle:lifecycle-runtime@2.5.1
androidx.lifecycle:lifecycle-viewmodel@2.5.1
com.google.android.material:material@1.6.1
commons-codec:commons-codec@1.10
org.jetbrains.kotlin:kotlin-stdlib@1.7.10
org.jetbrains.kotlinx:kotlinx-coroutines-android@1.6.1
org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm@1.6.1
```

That targeted experiment improved Markor from 6/19 to 19/19 confirmed versions:

| Field | Value |
|---|---:|
| Source-calibrated report | `data/results/report-real-markor-source-calibrated/` |
| Source-calibrated validation | `data/results/source-validation/markor-source-calibrated/` |
| Confirmed versions | 19 |
| Version mismatches | 0 |
| Missing coordinates | 0 |

The full older-stack set was not kept in the shared calibration DB because it regressed newer baselines. A later guarded follow-up promoted only `androidx.core:core@1.9.0`, because it improved Markor without regressing the current controls. This result is best used as evidence that source-used reference coverage can fix version matching, but global version selection needs app-era or dependency-coherence safeguards before mixing old and new stacks.

Gradle notes:

- The F-Droid build uses Gradle flavor `flavorDefault`.
- The F-Droid prebuild edit removes `-XX:MaxPermSize=512m` from `gradle.properties`.
- Cached Gradle `8.13` generated `flavorDefaultReleaseRuntimeClasspath`.
- The source tarball has no `.git` directory, but the build calls Git during configuration; a temporary Git snapshot was created under `/tmp` only for dependency-tree generation.

## Interpretation

Markor should be counted as source-validated partial-mismatch evidence:

- it confirms APK extraction, manifest metadata, multidex, report generation, OSV querying, Gradle dependency-tree generation, and source validation on a smaller real app;
- it has no native `.so` files, giving a contrast with native-heavy or native-boundary cases;
- it demonstrates that exact version recovery is weaker on older dependency stacks when the reference DB is skewed toward newer AndroidX/Kotlin versions;
- it also shows that naively adding older source-used versions globally can regress newer apps, so version-band selection needs safeguards;
- it should not be counted as a clean version-accuracy case.
