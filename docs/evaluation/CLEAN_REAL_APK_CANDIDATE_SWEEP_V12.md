# Real APK Growth Batch V2

This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.
It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 6 |
| Succeeded | 6 |
| Failed | 0 |
| APK root | `data/test_apks/real` |
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v12` |
| Classes covered | calendar, clean-candidate, connectivity, internet, maps, modern-source, navigation, network-monitor, news, no-native, password, security, source-linked, sync-client, task, time, time-tracker |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Password Generator | `com.vecturagames.android.app.passwordgenerator` | 1.9.0 (48) | source-validated-real | 2 | 0 | 16 | clean-candidate, no-native, security, password, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-password-generator/report.json` | No-native security/password utility with target SDK 36, medium APK size, and a substantial source tarball; selected as a modern non-sparse clean candidate likely to exercise AndroidX/Kotlin dependencies without native boundaries. |
| Todo Agenda | `org.andstatus.todoagenda` | 4.13.3 (717) | source-validated-real | 1 | 0 | 16 | clean-candidate, no-native, calendar, time, task, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-todo-agenda/report.json` | No-native calendar/task widget with target SDK 35 and a medium dependency-looking source tree; selected as a practical utility candidate with enough surface to avoid another sparse 1-2 component row. |
| Keep it up | `net.ibbaa.keepitup` | 1.11.1 (20) | source-validated-real | 1 | 0 | 5 | clean-candidate, no-native, connectivity, internet, network-monitor, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-keep-it-up/report.json` | No-native network-monitoring app with target SDK 36, internet/connectivity behavior, and manageable source size; selected for a likely non-sparse dependency tree without native code. |
| SkillApp | `com.theskillapp.skillapp` | 4.1.0 (357) | source-validated-real | 2 | 0 | 2 | clean-candidate, no-native, time, time-tracker, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-skillapp/report.json` | No-native time-tracking app with target SDK 36, moderate APK/source sizes, and a maintained source tarball; selected as a modern Kotlin/AndroidX-style candidate outside the already saturated note/browser families. |
| c3nav | `de.c3nav.droid` | 4.7.0 (18040700) | source-validated-real | 1 | 0 | 14 | clean-candidate, no-native, navigation, maps, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-c3nav/report.json` | No-native navigation app with target SDK 35, medium APK size, and a large enough source tarball to suggest meaningful Android dependencies without native map libraries. |
| Nextcloud News | `de.luhmer.owncloudnewsreader` | 0.9.9.95 (196) | source-validated-real | 2 | 0 | 3 | clean-candidate, no-native, internet, news, sync-client, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v12/report-real-nextcloud-news/report.json` | No-native news/sync client with target SDK 35, internet behavior, and a non-trivial source tree; selected as a dependency-rich clean candidate while avoiding native-heavy Nextcloud app boundaries. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
