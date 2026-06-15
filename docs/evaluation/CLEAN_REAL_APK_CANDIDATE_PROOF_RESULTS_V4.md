# Clean Real APK Candidate Proof Results V4

This artifact records the fourth no-native clean-candidate sweep. The goal was
to keep searching for a clean, non-sparse source-validated real APK while
preserving report-only and blocked outcomes honestly.

## Candidate Sweep

Five no-native F-Droid candidates were collected and SHA-256 checked against the
local F-Droid index:

- Cryptomator Lite 1.12.3
- Daily Dozen 28
- Privacy Browser 3.20.1
- MoneyWallet 4.0.5.10
- Easy Xkcd 8.4

All five APK reports were generated in Docker with the calibrated combined
reference DB under `data/results/evaluation/clean-real-apk-candidate-sweep-v4/`.

## Source-Validated Rows

| App | Package | APK | Report | Dependency tree | Source validation | Result |
|---|---|---|---|---|---|---|
| Daily Dozen 28 | `org.nutritionfacts.dailydozen` | `data/test_apks/real/daily-dozen/daily-dozen.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-daily-dozen/report.json` | `data/results/source-validation/csv4/daily-dozen/docker-app-fdroidReleaseRuntimeClasspath.txt` | `data/results/source-validation/csv4/daily-dozen/source-validation/source-validation.json` | 2/2 confirmed, 0 mismatches, 0 missing |
| Cryptomator Lite 1.12.3 | `org.cryptomator.lite` | `data/test_apks/real/cryptomator-lite/cryptomator-lite.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-cryptomator-lite/report.json` | `data/results/source-validation/csv4/cryptomator-lite/docker-presentation-liteReleaseRuntimeClasspath-gradle8.13.txt` | `data/results/source-validation/csv4/cryptomator-lite/source-validation-gradle8.13/source-validation.json` | 13/24 confirmed, 11 mismatches, 0 missing |
| Easy Xkcd 8.4 | `de.tap.easy_xkcd` | `data/test_apks/real/easy-xkcd/easy-xkcd.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-easy-xkcd/report.json` | `data/results/source-validation/csv4/easy-xkcd/docker-app-fdroidReleaseRuntimeClasspath-gradle8.13.validation-copy.txt` | `data/results/source-validation/csv4/easy-xkcd/source-validation-gradle8.13-validation-copy/source-validation.json` | 6/23 confirmed, 17 mismatches, 0 missing |
| MoneyWallet 4.0.5.10 | `com.oriondev.moneywallet` | `data/test_apks/real/moneywallet/moneywallet.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-moneywallet/report.json` | `data/results/source-validation/csv4/moneywallet/docker-app-flossOsmReleaseRuntimeClasspath-gradle6.1.1-jdk11.validation-copy.txt` | `data/results/source-validation/csv4/moneywallet/source-validation-gradle6.1.1-jdk11-validation-copy/source-validation.json` | 2/9 confirmed, 6 mismatches, 1 missing |
| Privacy Browser 3.20.1 | `com.stoutner.privacybrowser.standard` | `data/test_apks/real/privacy-browser/privacy-browser.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-privacy-browser/report.json` | `data/results/source-validation/csv4/privacy-browser/docker-app-standardReleaseRuntimeClasspath-gradle9.5.txt` | `data/results/source-validation/csv4/privacy-browser/source-validation-gradle9.5/source-validation.json` | 0/0 emitted Maven components; source tree resolves 87 Maven components |

Daily Dozen is clean but sparse: the APK report emits only two Maven
components. It is valid source-validated clean evidence, but it does not close
the clean non-sparse bucket.

Cryptomator Lite, Easy Xkcd, and MoneyWallet are source-validated partial rows.
The APKs and generated reports are kept in the dataset/results tree for thesis
statistics, but they must not be counted as clean exact-version evidence.

Privacy Browser is source-validated no-Maven-signal evidence. Docker installed
Android platform 36 in the validation container and Gradle 9.5 captured
`:app` `standardReleaseRuntimeClasspath`, but the APK report emits 0 Maven
components. It is useful as no-native browser/security smoke evidence, not as
an accuracy row.

## Blocked Or Report-Only Rows

No rows remain blocked or report-only in this v4 pass. Privacy Browser is
resolved as a source-validated no-Maven-signal control.

## Interpretation

This pass found one clean source-validated row, three no-native partial
source-validated rows, and one no-Maven-signal source-validated control after
adding Gradle 8.13, Gradle 9.5, Android platform 36, and JDK 11/Gradle 6.1.1
validation runtimes. It still does not close the desired clean non-sparse
bucket: the high-component rows mostly confirm coordinate identity, but version
selection remains the dominant error surface.
