# Clean Real APK Candidate Proof Results V10

This artifact records the tenth no-native clean-candidate sweep. The goal was
to keep searching for a clean, non-sparse source-validated real APK while
preserving honest bucket boundaries for partial and blocked rows.

## Candidate Sweep

Five untried no-native F-Droid candidates were selected from the local
F-Droid index using source-tarball availability, no native-code manifest entry,
target SDK, APK size, source size, and category diversity:

- Etar - OpenSource Calendar 1.0.55
- RadioDroid 0.86
- SimpleLogin Anti-spam 1.22.0
- Omni Notes 6.3.1
- Primitive FTPd 8.1

All five APKs were downloaded from F-Droid, SHA-256 checked against the local
index, and reported in Docker with the calibrated combined reference DB under
`data/results/evaluation/clean-real-apk-candidate-sweep-v10/`. Exact F-Droid
source tarballs were downloaded and checked under `data/source/csv10/`.

## Source-Validated Rows

| App | Package | APK | Report | Dependency tree | Source validation | Result |
|---|---|---|---|---|---|---|
| Etar - OpenSource Calendar 1.0.55 | `ws.xsoh.etar` | `data/test_apks/real/etar/etar.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-etar/report.json` | `data/results/source-validation/csv10/etar/root1-app-dependencies-releaseRuntimeClasspath.txt` | `data/results/source-validation/csv10/etar/source-validation/source-validation.json` | 15/38 confirmed, 2 mismatches, 21 missing |
| RadioDroid 0.86 | `net.programmierecke.radiodroid2` | `data/test_apks/real/radiodroid/radiodroid.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-radiodroid/report.json` | `data/results/source-validation/csv10/radiodroid/root1-app-dependencies-freeReleaseRuntimeClasspath.txt` | `data/results/source-validation/csv10/radiodroid/source-validation/source-validation.json` | 5/39 confirmed, 15 mismatches, 19 missing |
| SimpleLogin Anti-spam 1.22.0 | `io.simplelogin.android.fdroid` | `data/test_apks/real/simplelogin/simplelogin.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-simplelogin/report.json` | `data/results/source-validation/csv10/simplelogin/root1-app-dependencies-fdroidReleaseRuntimeClasspath.txt` | `data/results/source-validation/csv10/simplelogin/source-validation/source-validation.json` | 9/39 confirmed, 13 mismatches, 17 missing |
| Omni Notes 6.3.1 | `it.feio.android.omninotes.foss` | `data/test_apks/real/omni-notes/omni-notes.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-omni-notes/report.json` | `data/results/source-validation/csv10/omni-notes/root1-omniNotes-dependencies-fossReleaseRuntimeClasspath.txt` | `data/results/source-validation/csv10/omni-notes/source-validation/source-validation.json` | 4/39 confirmed, 16 mismatches, 19 missing |
| Primitive FTPd 8.1 | `org.primftpd` | `data/test_apks/real/primitive-ftpd/primitive-ftpd.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-primitive-ftpd/report.json` | `data/results/source-validation/csv10/primitive-ftpd/root1-primitiveFTPd-dependencies-releaseRuntimeClasspath.txt` | `data/results/source-validation/csv10/primitive-ftpd/source-validation/source-validation.json` | 12/38 confirmed, 4 mismatches, 22 missing |

Etar, RadioDroid, SimpleLogin, Omni Notes, and Primitive FTPd are source-validated partial
rows. Etar is useful because it is a no-native, non-sparse calendar/time app
with successful source and Gradle proof gates. RadioDroid was rescued by a
JCenter validation copy plus a Docker Gradle 8.13 compatibility lane.
SimpleLogin was rescued by copying the real `SimpleLogin` Gradle root,
disabling only Detekt build-time analysis configuration, and using Docker Gradle
8.13 for `:app` `fdroidReleaseRuntimeClasspath`. Omni Notes was rescued by a
validation copy that disables only SonarQube/test-logger/Jacoco build-time
analysis wiring, narrows Gradle probing to `:omniNotes`, and uses Docker Gradle
8.13 for `fossReleaseRuntimeClasspath`. Primitive FTPd was rescued by
narrowing the proof runner to the actual `:primitiveFTPd` module. They add
no-native calendar, multimedia/radio, email/security, notes/productivity, and
connectivity/file-transfer evidence, but none closes the clean non-sparse
bucket.

## Interpretation

This pass now adds five richer no-native partial rows. It increases
source-validated real APK coverage, but it still does not satisfy the desired
clean non-sparse admission target.
