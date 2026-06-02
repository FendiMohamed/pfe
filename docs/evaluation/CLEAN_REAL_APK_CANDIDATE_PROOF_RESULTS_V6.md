# Clean Real APK Candidate Proof Results V6

This artifact records the sixth no-native clean-candidate sweep. The goal was
to keep searching for a clean, non-sparse source-validated real APK while
preserving partial outcomes honestly.

## Candidate Sweep

Five no-native F-Droid candidates were collected and SHA-256 checked against the
local F-Droid index:

- microMathematics Plus 2.23.3
- Retro Music 6.6.0
- Broccoli 1.4.4
- Diaguard 3.15.1
- LibreTube 31.4

All five APK reports were generated in Docker with the calibrated combined
reference DB under `data/results/evaluation/clean-real-apk-candidate-sweep-v6/`.
Exact F-Droid source tarballs were downloaded and extracted under
`data/source/csv6/`.

## Source-Validated Rows

| App | Package | APK | Report | Dependency tree | Source validation | Result |
|---|---|---|---|---|---|---|
| Broccoli 1.4.4 | `com.flauschcode.broccoli` | `data/test_apks/real/broccoli/broccoli.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-broccoli/report.json` | `data/results/source-validation/csv6/broccoli/docker-app-fdroidReleaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv6/broccoli/source-validation-gradle8.13/source-validation.json` | 11/20 confirmed, 9 mismatches, 0 missing |
| LibreTube 31.4 | `com.github.libretube` | `data/test_apks/real/libretube/libretube.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-libretube/report.json` | `data/results/source-validation/csv6/libretube/docker-app-releaseRuntimeClasspath-gradle9.5.txt` | `data/results/source-validation/csv6/libretube/source-validation-gradle9.5/source-validation.json` | 9/13 confirmed, 4 mismatches, 0 missing |
| Retro Music 6.6.0 | `code.name.monkey.retromusic` | `data/test_apks/real/retro-music/retro-music.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-retro-music/report.json` | `data/results/source-validation/csv6/retro-music/docker-app-fdroidReleaseRuntimeClasspath-gradle8.14.3.txt` | `data/results/source-validation/csv6/retro-music/source-validation-gradle8.14.3/source-validation.json` | 4/6 confirmed, 2 mismatches, 0 missing |
| microMathematics Plus 2.23.3 | `com.mkulesh.micromath.plus` | `data/test_apks/real/micromathematics-plus/micromathematics-plus.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-micromathematics-plus/report.json` | `data/results/source-validation/csv6/micromathematics-plus/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv6/micromathematics-plus/source-validation-gradle8.13/source-validation.json` | 4/16 confirmed, 12 mismatches, 0 missing |
| Diaguard 3.15.1 | `com.faltenreich.diaguard` | `data/test_apks/real/diaguard/diaguard.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-diaguard/report.json` | `data/results/source-validation/csv6/diaguard/docker-app-demoReleaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv6/diaguard/source-validation-gradle8.13/source-validation.json` | 2/5 confirmed, 3 mismatches, 0 missing |

All five rows are source-validated partial rows. The APKs and generated reports
are kept in the dataset/results tree for thesis statistics, but they must not
be counted as clean exact-version evidence.

## Blocked Or Report-Only Rows

No rows remain blocked or report-only in this v6 pass.

## Interpretation

This pass found five no-native partial source-validated rows. Docker Gradle 8.13
resolved microMathematics Plus, Broccoli, and Diaguard; Docker Gradle 8.14.3
resolved Retro Music; Docker Gradle 9.5 resolved LibreTube. The desired clean
non-sparse bucket remains open, but the batch adds richer no-native media,
health, recipe, and science/calculator evidence. Diaguard also contributes a
real no-native release-minified row for the R8/minified bucket.
