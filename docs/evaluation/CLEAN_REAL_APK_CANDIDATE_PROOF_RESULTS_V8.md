# Clean Real APK Candidate Proof Results V8

This artifact records the eighth no-native clean-candidate sweep. The goal was
to keep searching for a clean, non-sparse source-validated real APK while also
growing the source-validated real APK set toward 50 total cases.

## Candidate Sweep

Five no-native F-Droid candidates were collected and SHA-256 checked against the
local F-Droid index:

- Drift // Audio 0.1.0
- JaMuz 0.6.14
- monocles browser 1.9.3
- Conceal Mobile 5.0.4
- Ltt.rs 0.4.4

All five APK reports were generated in Docker with the calibrated combined
reference DB under `data/results/evaluation/clean-real-apk-candidate-sweep-v8/`.
Exact F-Droid source tarballs were downloaded and extracted under
`data/source/csv8/`.

## Source-Validated Rows

| App | Package | APK | Report | Dependency tree | Source validation | Result |
|---|---|---|---|---|---|---|
| Drift // Audio 0.1.0 | `io.github.probably_oxy.drift` | `data/test_apks/real/drift-audio/drift-audio.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-drift-audio/report.json` | `data/results/source-validation/csv8/drift-audio/root1-app-dependencies-releaseRuntimeClasspath.txt` | `data/results/source-validation/csv8/drift-audio/source-validation/source-validation.json` | 7/13 confirmed, 6 mismatches, 0 missing |
| JaMuz 0.6.14 | `org.phramusca.jamuz` | `data/test_apks/real/jamuz/jamuz.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-jamuz/report.json` | `data/results/source-validation/csv8/jamuz/root1-app-dependencies-releaseRuntimeClasspath.txt` | `data/results/source-validation/csv8/jamuz/source-validation/source-validation.json` | 14/21 confirmed, 7 mismatches, 0 missing |
| monocles browser 1.9.3 | `de.monocles.browser` | `data/test_apks/real/monocles-browser/monocles-browser.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-monocles-browser/report.json` | `data/results/source-validation/csv8/monocles-browser/root1-app-dependencies-standardReleaseRuntimeClasspath.txt` | `data/results/source-validation/csv8/monocles-browser/source-validation/source-validation.json` | 0/0 emitted Maven components |

Drift // Audio and JaMuz are source-validated partial rows. The APKs and
generated reports are kept in the dataset/results tree for thesis statistics,
but they must not be counted as clean exact-version evidence.

monocles browser is source-validated no-Maven-signal evidence. The source proof
is successful, but the current APK report emits 0 Maven components, so it
should be treated as a control rather than as accuracy evidence.

## Blocked Or Report-Only Rows

| App | Status | Why it stays out of source-validated metrics |
|---|---|---|
| Conceal Mobile 5.0.4 | Gradle-blocked | The APK/source/report bundle is collected, but no attempted runtime dependency-tree configuration succeeded across the extracted Gradle roots. |
| Ltt.rs 0.4.4 | Gradle-blocked | The APK/source/report bundle is collected, but no attempted runtime dependency-tree configuration succeeded across the extracted Gradle roots. |

## Interpretation

This pass still does not close the clean non-sparse bucket, but it adds two
more honest no-native partial rows and one additional no-Maven-signal control.
JaMuz is especially useful because it contributes another richer 21-component
row, while Drift // Audio broadens the multimedia slice without native-boundary
caveats.
