# Clean Real APK Candidate Proof Results V5

This artifact records the fifth no-native clean-candidate sweep. The goal was
to keep searching for a clean, non-sparse source-validated real APK while
preserving partial outcomes honestly.

## Candidate Sweep

Five no-native F-Droid candidates were collected and SHA-256 checked against the
local F-Droid index:

- yetCalc 2.0.8
- Loop Habit Tracker 2.3.1
- QuickDic 5.8.2
- Cirrus 4.7
- AFWall+ 4.0.3

All five APK reports were generated in Docker with the calibrated combined
reference DB under `data/results/evaluation/clean-real-apk-candidate-sweep-v5/`.
Exact F-Droid source tarballs were downloaded and extracted under
`data/source/csv5/`.

## Source-Validated Rows

| App | Package | APK | Report | Dependency tree | Source validation | Result |
|---|---|---|---|---|---|---|
| QuickDic 5.8.2 | `de.reimardoeffinger.quickdic` | `data/test_apks/real/quickdic/quickdic.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-quickdic/report.json` | `data/results/source-validation/csv5/quickdic/docker-root-releaseRuntimeClasspath-gradle8.14.3.txt` | `data/results/source-validation/csv5/quickdic/source-validation-gradle8.14.3/source-validation.json` | 2/2 confirmed, 0 mismatches, 0 missing |
| Cirrus 4.7 | `org.woheller69.omweather` | `data/test_apks/real/cirrus/cirrus.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-cirrus/report.json` | `data/results/source-validation/csv5/cirrus/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv5/cirrus/source-validation-gradle8.13/source-validation.json` | 14/19 confirmed, 5 mismatches, 0 missing |
| AFWall+ 4.0.3 | `dev.ukanth.ufirewall` | `data/test_apks/real/afwall-plus/afwall-plus.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-afwall-plus/report.json` | `data/results/source-validation/csv5/afwall-plus/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv5/afwall-plus/source-validation-gradle8.13/source-validation.json` | 12/18 confirmed, 6 mismatches, 0 missing |
| Loop Habit Tracker 2.3.1 | `org.isoron.uhabits` | `data/test_apks/real/loop-habit-tracker/loop-habit-tracker.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-loop-habit-tracker/report.json` | `data/results/source-validation/csv5/loop-habit-tracker/docker-uhabits-android-releaseRuntimeClasspath-gradle8.14.3.txt` | `data/results/source-validation/csv5/loop-habit-tracker/source-validation-gradle8.14.3/source-validation.json` | 7/11 confirmed, 4 mismatches, 0 missing |
| yetCalc 2.0.8 | `yetzio.yetcalc` | `data/test_apks/real/yetcalc/yetcalc.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-yetcalc/report.json` | `data/results/source-validation/csv5/yetcalc/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv5/yetcalc/source-validation-gradle8.13/source-validation.json` | 6/17 confirmed, 11 mismatches, 0 missing |

QuickDic is clean but sparse: the APK report emits only two Maven components.
It is valid source-validated clean evidence, but it does not close the clean
non-sparse bucket.

Cirrus, AFWall+, Loop Habit Tracker, and yetCalc are source-validated partial
rows. The APKs and generated reports are kept in the dataset/results tree for
thesis statistics, but they must not be counted as clean exact-version evidence.

## Blocked Or Report-Only Rows

No rows remain blocked or report-only in this v5 pass.

## Interpretation

This pass found one clean source-validated sparse row and four no-native partial
source-validated rows. Docker Gradle 8.13 resolved Cirrus, AFWall+, and yetCalc;
Docker Gradle 8.14.3 resolved the modular Loop Habit Tracker Android module and
the QuickDic root project. The desired clean non-sparse bucket remains open:
coordinate recovery is useful, but exact version selection remains the dominant
error surface.
