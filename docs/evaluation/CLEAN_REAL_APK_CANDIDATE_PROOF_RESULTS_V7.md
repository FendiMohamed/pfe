# Clean Real APK Candidate Proof Results V7

This artifact records the seventh no-native clean-candidate sweep. The goal was
to keep searching for a clean, non-sparse source-validated real APK while
preserving partial and no-signal outcomes honestly.

## Candidate Sweep

Five no-native F-Droid candidates were collected and SHA-256 checked against the
local F-Droid index:

- AndStatus 62.03
- Fulguris Web Browser 2.0.10
- I2P 2.11.0
- Working Time Account 2.11.012
- Mastodon 2.12.3

All five APK reports were generated in Docker with the calibrated combined
reference DB under `data/results/evaluation/clean-real-apk-candidate-sweep-v7/`.
Exact F-Droid source tarballs were downloaded and extracted under
`data/source/csv7/`.

## Source-Validated Rows

| App | Package | APK | Report | Dependency tree | Source validation | Result |
|---|---|---|---|---|---|---|
| Fulguris Web Browser 2.0.10 | `net.slions.fulguris.full.fdroid` | `data/test_apks/real/fulguris-web-browser/fulguris-web-browser.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-fulguris-web-browser/report.json` | `data/results/source-validation/csv7/fulguris-web-browser/docker-app-slionsFullFdroidReleaseRuntimeClasspath-gradle8.14.3.txt` | `data/results/source-validation/csv7/fulguris-web-browser/source-validation-gradle8.14.3/source-validation.json` | 17/21 confirmed, 4 mismatches, 0 missing |
| Working Time Account 2.11.012 | `askanimus.arbeitszeiterfassung2` | `data/test_apks/real/working-time-account/working-time-account.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-working-time-account/report.json` | `data/results/source-validation/csv7/working-time-account/docker-app-releaseRuntimeClasspath-gradle9.5.txt` | `data/results/source-validation/csv7/working-time-account/source-validation-gradle9.5/source-validation.json` | 12/15 confirmed, 3 mismatches, 0 missing |
| AndStatus 62.03 | `org.andstatus.app` | `data/test_apks/real/andstatus/andstatus.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-andstatus/report.json` | `data/results/source-validation/csv7/andstatus/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv7/andstatus/source-validation-gradle8.13/source-validation.json` | 12/19 confirmed, 7 mismatches, 0 missing |
| I2P 2.11.0 | `net.i2p.android.router` | `data/test_apks/real/i2p/i2p.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-i2p/report.json` | `data/results/source-validation/csv7/i2p/docker-app-legacyReleaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv7/i2p/source-validation-gradle8.13/source-validation.json` | 10/18 confirmed, 8 mismatches, 0 missing |
| Mastodon 2.12.3 | `org.joinmastodon.android` | `data/test_apks/real/mastodon/mastodon.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-mastodon/report.json` | `data/results/source-validation/csv7/mastodon/docker-mastodon-releaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv7/mastodon/source-validation-gradle8.13/source-validation.json` | 0/0 emitted Maven components; source tree resolves 20 Maven components |

Fulguris Web Browser, Working Time Account, AndStatus, and I2P are
source-validated partial rows. The APKs and generated reports are kept in the
dataset/results tree for thesis statistics, but they must not be counted as
clean exact-version evidence.

Mastodon is source-validated no-Maven-signal evidence. The source proof is
successful, but the current APK report emits 0 Maven components, so it should
be treated as a control rather than as accuracy evidence.

## Blocked Or Report-Only Rows

No rows remain blocked or report-only in this v7 pass.

## Interpretation

This pass did not close the clean non-sparse bucket, but it adds four richer
no-native partial rows and one additional no-Maven-signal control. Fulguris Web
Browser and Working Time Account are especially useful because they emit
non-sparse SBOMs with relatively strong confirmation rates without requiring
native-boundary caveats.
