# Real APK Growth Batch V2

This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.
It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 8 |
| Succeeded | 8 |
| Failed | 0 |
| APK root | `data/test_apks/real` |
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v15` |
| Classes covered | clean-candidate, clock, cloud-storage, development, dictionary, email, file-transfer, gps-tracker, internet, json-viewer, modern-source, multimedia, music-streaming, no-native, notes, source-linked, sports-health, time, timer, tts, weather, workout, writing |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Clock | `com.best.deskclock` | 2.29 (2032) | source-validated-real | 3 | 0 | 38 | clean-candidate, no-native, time, clock, timer, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-clock/report.json` | No-native clock/timer app with target SDK 36, a 12 MB APK, and a moderate source tarball; selected as a dependency-rich time utility outside the already counted Todo Agenda and Working Time rows. |
| Poet Assistant | `ca.rmen.android.poetassistant` | 1.31.1 (113101) | source-validated-real | 1 | 0 | 37 | clean-candidate, no-native, writing, dictionary, tts, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-poet-assistant/report.json` | No-native writing/dictionary app with target SDK 35, a large APK, and source tarball metadata; selected as a likely non-sparse reading/writing row with different dependencies from prior note apps. |
| Ultrasonic | `org.moire.ultrasonic` | 4.9.0 (131) | source-validated-real | 1 | 0 | 39 | clean-candidate, no-native, internet, multimedia, music-streaming, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-ultrasonic/report.json` | No-native Subsonic music client with target SDK 36, a medium APK, and a source tarball; selected to broaden media/internet evidence without native `.so` boundaries. |
| FTPClient | `de.qwerty287.ftpclient` | 3.0.1 (27) | source-validated-real | 5 | 0 | 39 | clean-candidate, no-native, internet, cloud-storage, file-transfer, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-ftpclient/report.json` | No-native FTP/FTPS/SFTP client with target SDK 36 and a 10 MB APK; selected as a compact connectivity/file-transfer row likely to expose networking dependencies. |
| RunnerUp | `org.runnerup.free` | 2.11.0.1 (23000372) | source-validated-real | 3 | 0 | 39 | clean-candidate, no-native, sports-health, workout, gps-tracker, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-runnerup/report.json` | No-native workout/GPS tracker with target SDK 36, a medium APK, and a manageable source tarball; selected for a sports-health row with likely AndroidX/location/audio dependency evidence. |
| Json List | `com.sjapps.jsonlist` | 1.10 (1000) | source-validated-real | 3 | 0 | 38 | clean-candidate, no-native, development, json-viewer, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-json-list/report.json` | No-native development/JSON viewer app with target SDK 36, a moderate APK, and a source tarball; selected to add a development-tool row outside browser, note, and media categories. |
| ImapNotes3 | `de.niendo.ImapNotes3` | v1.4-07 (10407) | source-validated-real | 2 | 0 | 39 | clean-candidate, no-native, email, internet, notes, writing, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-imapnotes3/report.json` | No-native IMAP note/checklist app with target SDK 35 and a non-sparse generated report; selected as an email/internet writing row that exercises mail and sync dependencies without native code. |
| Forecastie | `cz.martykan.forecastie` | 1.23 (75) | source-validated-real | 1 | 0 | 37 | clean-candidate, no-native, internet, weather, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v15/report-real-forecastie/report.json` | No-native weather app with target SDK 36, a manageable APK/source pair, and likely standard Gradle wiring; selected as a weather/internet row after v14 proved this family can produce useful partial evidence. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
