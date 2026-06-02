# Clean Real APK Candidate Proof Results V3

This artifact records the third no-native clean-candidate sweep. The goal was
again to find a clean, non-sparse source-validated real APK after F-Droid,
OpenTracks, and sparse Tusky.

## Candidate Sweep

Four no-native F-Droid candidates were collected and SHA-256 checked against the
local F-Droid index:

- Simple Time Tracker 1.57
- MedTimer 1.22.18
- Doodle 6.0.0
- KeePassVault 1.16.0

All four APK reports were generated with the calibrated combined reference DB
under `data/results/evaluation/clean-real-apk-candidate-sweep-v3/`. Host Python
does not have the project report dependencies, so reports were generated in the
Docker runtime and the sweep summary was refreshed with `--reuse-reports`.

## Source-Validated Rows

The useful source-validated rows from this pass are partial:

| App | Package | APK | Report | Dependency tree | Source validation | Result |
|---|---|---|---|---|---|---|
| MedTimer 1.22.18 | `com.futsch1.medtimer` | `data/test_apks/real/medtimer/medtimer.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-medtimer/report.json` | `data/results/source-validation/csv3/medtimer/docker-app-fossReleaseRuntimeClasspath.txt` | `data/results/source-validation/csv3/medtimer/source-validation/source-validation.json` | 12/18 confirmed, 6 mismatches, 0 missing |
| Doodle 6.0.0 | `xyz.zedler.patrick.doodle` | `data/test_apks/real/doodle/doodle.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-doodle/report.json` | `data/results/source-validation/csv3/doodle/docker-app-releaseRuntimeClasspath.txt` | `data/results/source-validation/csv3/doodle/source-validation/source-validation.json` | 3/6 confirmed, 2 mismatches, 1 missing |
| Simple Time Tracker 1.57 | `com.razeeman.util.simpletimetracker` | `data/test_apks/real/simple-time-tracker/simple-time-tracker.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-simple-time-tracker/report.json` | `data/results/source-validation/csv3/simple-time-tracker/docker-app-baseReleaseRuntimeClasspath.txt` | `data/results/source-validation/csv3/simple-time-tracker/source-validation/source-validation.json` | 6/12 confirmed, 6 mismatches, 0 missing |
| KeePassVault 1.16.0 | `com.ivanovsky.passnotes` | `data/test_apks/real/keepassvault/keepassvault.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-keepassvault/report.json` | `data/results/source-validation/csv3/keepassvault/docker-app-fdroidReleaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv3/keepassvault/source-validation-gradle8.13/source-validation.json` | 8/24 confirmed, 15 mismatches, 1 missing |

## Interpretation

MedTimer is the strongest v3 row: it is no-native, multidex, low obfuscation
risk, and confirms 12 of 18 emitted Maven component versions. It is still not a
clean row because ViewPager2, Kotlin stdlib, Gson, Material, Fragment, and
ExifInterface differ from the source-resolved dependency tree.

Doodle is useful because it is a simple no-native UI app with release shrinking
and optimization enabled but name obfuscation disabled. It remains partial at
3/6.

Simple Time Tracker required Docker `/tmp` extraction because the Windows
workspace path was too long for its deeply nested source tree. Its F-Droid
flavor is `base`, and `baseReleaseRuntimeClasspath` validates 6 of 12 emitted
Maven versions.

KeePassVault is a dependency-rich no-native security/password-manager row with
multidex, AndroidX, Compose, Kotlin, OkHttp, and Okio evidence. It required
Android platform 34 in the validation container, and Gradle 8.13 captured
`:app` `fdroidReleaseRuntimeClasspath`. It validates 8 of 24 emitted Maven
versions; AndroidX/Compose/Kotlin/Okio version drift and one missing Lifecycle
Android-target coordinate keep it partial.

The clean non-sparse bucket remains open. These rows should be counted as
source-validated partial evidence only.
