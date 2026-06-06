# Real APK Growth Batch V2

This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.
It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 12 |
| Succeeded | 12 |
| Failed | 0 |
| APK root | `data/test_apks/real` |
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v16` |
| Classes covered | clean-candidate, cloud-admin, connectivity, development, dictionary, ebook-reader, education, fdroid, file-transfer, hardware-companion, internet, messaging, modern-source, no-native, password-manager, phone-sms, reading, security, source-linked, sports-health, study-tracking, system, task, time, tracker, weather, widget, workout, writing |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| OceanNex for DigitalOcean | `com.swatian.oceannex.free` | 1.0.0 (100) | source-validated-real | 3 | 0 | 21 | clean-candidate, no-native, internet, cloud-admin, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-oceannex/report.json` | No-native DigitalOcean administration client with target SDK 36, a 16 MB APK, and a compact source tarball; selected to add a cloud/admin internet row outside the earlier file-transfer and weather batches. |
| Praktika Vortaro | `com.esperantajvortaroj.app` | 0.26 (26) | source-validated-real | 1 | 0 | 1 | clean-candidate, no-native, reading, dictionary, education, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-praktika-vortaro/report.json` | No-native dictionary/reading app with target SDK 34, a large APK, and a small source tarball; selected as a language/reference row distinct from Poet Assistant. |
| MsgGo | `top.yztz.msggo` | 3.9 (26000309) | source-validated-real | 5 | 0 | 4 | clean-candidate, no-native, phone-sms, messaging, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-msggo/report.json` | No-native SMS/messaging app with target SDK 35, a medium APK, and source tarball metadata; selected to broaden messaging evidence without native framework boundaries. |
| AF Weather Widget | `net.gitsaibot.af` | 3.2 (23) | source-validated-real | 2 | 0 | 18 | clean-candidate, no-native, internet, weather, widget, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-af-weather-widget/report.json` | No-native weather/widget app with target SDK 36 and a compact source tarball; selected as a second weather-family row after Forecastie and RadarWeather showed useful partial evidence. |
| Study Tracker | `com.edward.studytracker` | 1.0.7 (7) | source-validated-real | 2 | 0 | 15 | clean-candidate, no-native, education, study-tracking, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-study-tracker/report.json` | No-native education/study tracker with target SDK 34, a medium APK, and a compact source tarball; selected to add a student/productivity row with likely AndroidX/Compose evidence. |
| Calliope mini | `cc.calliope.mini` | 2.0.9 (27) | source-validated-real | 3 | 0 | 18 | clean-candidate, no-native, connectivity, education, hardware-companion, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-calliope-mini/report.json` | No-native hardware/connectivity companion app with target SDK 36 and a manageable source tarball; selected to add a device-connectivity row without native `.so` evidence. |
| ProseReader | `timur.prose` | 1.9.6 (10906) | source-validated-real | 1 | 0 | 0 | clean-candidate, no-native, ebook-reader, reading, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-prosereader/report.json` | No-native ebook/reading app with target SDK 36, a medium APK, and a moderate source tarball; selected to diversify the reading bucket beyond dictionary/reference apps. |
| Flying Carpet | `dev.spiegl.flyingcarpet` | 9.0.8 (21) | source-validated-real | 2 | 0 | 17 | clean-candidate, no-native, connectivity, file-transfer, system, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-flying-carpet/report.json` | No-native local file-transfer app with target SDK 35 and a compact Android source tarball; selected to add another connectivity/file-transfer row outside FTPClient. |
| FitoTrack | `de.tadris.fitness` | 15.6 (1560) | source-validated-real | 4 | 0 | 18 | clean-candidate, no-native, sports-health, workout, tracker, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-fitotrack/report.json` | No-native workout tracker with target SDK 34, a medium APK, and source tarball metadata; selected as a sports-health row distinct from RunnerUp. |
| F-Droid Build Status | `de.storchp.fdroidbuildstatus` | 5.14.0 (118) | source-validated-real | 2 | 0 | 24 | clean-candidate, no-native, development, fdroid, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-fdroid-build-status/report.json` | No-native F-Droid/development utility with target SDK 36 and a compact source tarball; selected to add a development-tool row different from Json List. |
| Password Master | `com.vecturagames.android.app.passwordmaster` | 1.5.1 (15) | source-validated-real | 3 | 0 | 18 | clean-candidate, no-native, security, password-manager, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-password-master/report.json` | No-native password/security utility with target SDK 36 and source tarball metadata; selected to add a compact security row outside KeePassDX and Password Generator. |
| Todo List (PFA) | `org.secuso.privacyfriendlytodolist` | 3.4.0 (103) | source-validated-real | 3 | 0 | 17 | clean-candidate, no-native, task, time, writing, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v16/report-real-todo-list-pfa/report.json` | No-native task/time utility with target SDK 36 and a small source tarball; selected as a compact productivity row after Todo Agenda and Working Time Account. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
