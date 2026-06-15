# Clean Real APK Candidate Proof Results V9

This artifact records the ninth no-native clean-candidate sweep. The goal was
to keep searching for a clean, non-sparse source-validated real APK while
preserving honest bucket boundaries for partial and blocked rows.

## Candidate Sweep

Five untried no-native F-Droid candidates were selected from the local
F-Droid index using source-tarball availability, no native-code manifest entry,
target SDK, APK size, source size, and category diversity:

- DoliDroid 3.0.69
- ownCloud 4.8.0
- Your local weather 6.4.0-FOSS
- OpenKeychain: Easy PGP 6.0.4
- HomeFeed - RSS Widget 1.3.0

All five APKs were downloaded from F-Droid, SHA-256 checked against the local
index, and reported in Docker with the calibrated combined reference DB under
`data/results/evaluation/clean-real-apk-candidate-sweep-v9/`. Exact F-Droid
source tarballs were downloaded and checked under `data/source/csv9/`.

## Source-Validated Rows

| App | Package | APK | Report | Dependency tree | Source validation | Result |
|---|---|---|---|---|---|---|
| DoliDroid 3.0.69 | `com.nltechno.dolidroidpro` | `data/test_apks/real/dolidroid/dolidroid.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-dolidroid/report.json` | `data/results/source-validation/csv9/dolidroid/root1-app-dependencies-releaseRuntimeClasspath.txt` | `data/results/source-validation/csv9/dolidroid/source-validation/source-validation.json` | 7/14 confirmed, 7 mismatches, 0 missing |
| ownCloud 4.8.0 | `com.owncloud.android` | `data/test_apks/real/owncloud/owncloud.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-owncloud/report.json` | `data/results/source-validation/csv9/owncloud/root1-owncloudApp-dependencies-originalReleaseRuntimeClasspath.txt` | `data/results/source-validation/csv9/owncloud/source-validation/source-validation.json` | 7/22 confirmed, 14 mismatches, 1 missing |
| OpenKeychain: Easy PGP 6.0.4 | `org.sufficientlysecure.keychain` | `data/test_apks/real/openkeychain/openkeychain.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-openkeychain/report.json` | `data/results/source-validation/csv9/openkeychain/root1-OpenKeychain-dependencies-releaseRuntimeClasspath.txt` | `data/results/source-validation/csv9/openkeychain/source-validation/source-validation.json` | 5/12 confirmed, 7 mismatches, 0 missing |
| Your local weather 6.4.0-FOSS | `org.thosp.yourlocalweather` | `data/test_apks/real/your-local-weather/your-local-weather.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-your-local-weather/report.json` | `data/results/source-validation/csv9/your-local-weather/root1-app-dependencies-fossReleaseRuntimeClasspath.txt` | `data/results/source-validation/csv9/your-local-weather/source-validation/source-validation.json` | 15/17 confirmed, 2 mismatches, 0 missing |
| HomeFeed - RSS Widget 1.3.0 | `com.byterdevs.rsswidget` | `data/test_apks/real/homefeed-rss-widget/homefeed-rss-widget.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-homefeed-rss-widget/report.json` | `data/results/source-validation/csv9/homefeed-rss-widget/root1-app-dependencies-releaseRuntimeClasspath.txt` | `data/results/source-validation/csv9/homefeed-rss-widget/source-validation/source-validation.json` | 11/17 confirmed, 6 mismatches, 0 missing |

DoliDroid, ownCloud, OpenKeychain, Your local weather, and HomeFeed are
source-validated partial rows. DoliDroid was rescued by a validation copy that
replaces removed `jcenter()` repository calls with Maven Central for
dependency-tree capture. ownCloud was rescued by a validation copy that disables
build-time Kotlin/KSP/Parcelize/Ktlint/Detekt/Sonar/CycloneDX wiring, pins
`:owncloudApp`, and captures `originalReleaseRuntimeClasspath` with Docker
Gradle 8.13. OpenKeychain was rescued by a minimal validation copy
that adds the missing wrapper-root `settings.gradle`, replaces removed
`jcenter()` calls, enables AGP-required BuildConfig/AndroidX properties, and
omits unavailable local project wires while preserving Maven runtime
declarations. All five rows are useful no-native, non-sparse real APK evidence,
but none closes the clean non-sparse bucket.

## Blocked Rows

| App | Status | Why it stays out of source-validated metrics |
|---|---|---|
| None | n/a | All v9 rows now have dependency-tree and source-validation output. |

No v9 row remains source-linked blocked. ownCloud stays partial rather than clean
because 14 emitted versions mismatch the source tree and 1 emitted coordinate is
missing from the resolved runtime dependency tree.

## Interpretation

This pass now adds five richer no-native partial rows. It increases
source-validated real APK coverage, but it still
does not satisfy the desired clean non-sparse admission target.
