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
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v14` |
| Classes covered | clean-candidate, dns, education, internet, media-client, modern-source, multimedia, navigation, no-native, public-transport, reading, science, source-linked, weather, writing |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Bimba | `xyz.apiote.bimba.czwek` | 3.99 (48) | source-validated-real | 5 | 0 | 25 | clean-candidate, no-native, navigation, public-transport, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-bimba/report.json` | No-native public-transport app with target SDK 36, a non-sparse APK, and a source tarball; selected as a transport/navigation row after v13 railway/map rows validated well. |
| wX | `joshuatee.wx` | 55990 (55990) | source-validated-real | 3 | 0 | 19 | clean-candidate, no-native, weather, science, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-wx/report.json` | No-native weather/science app with target SDK 36 and substantial APK signal; selected to add a dependency-rich weather row outside the already validated map/note/security families. |
| Egyptian Writer | `com.blueapps.egyptianwriter` | 14.05.2026@0.1.0.1 (10) | source-validated-real | 3 | 0 | 17 | clean-candidate, no-native, reading, science, writing, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-egyptian-writer/report.json` | No-native reading/education/writing app with target SDK 36, a moderate source tarball, and likely UI/text-processing dependencies; selected for category diversity. |
| Smouldering Durtles | `com.smouldering_durtles.wk` | 1.2.3 (84) | source-validated-real | 4 | 0 | 22 | clean-candidate, no-native, science, education, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-smouldering-durtles/report.json` | No-native WaniKani education client with target SDK 34 and a substantial source tree; selected as a likely dependency-rich education client. |
| Baby Books | `com.serwylo.babybook` | 0.9.2 (12) | source-validated-real | 3 | 0 | 29 | clean-candidate, no-native, reading, science, writing, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-baby-books/report.json` | No-native reading/writing app with target SDK 34 and a moderate source tarball; selected as a content-authoring row likely to emit nontrivial Maven evidence. |
| Odysee | `com.odysee.floss` | 0.0.124 (124) | source-validated-real | 1 | 0 | 15 | clean-candidate, no-native, internet, multimedia, media-client, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-odysee/report.json` | No-native media/internet client with target SDK 36 and a moderate source tree; selected to diversify source validation into online-media behavior without native files. |
| DNS Hero | `com.gianlu.dnshero` | 1.7.0 (42) | source-validated-real | 1 | 0 | 11 | clean-candidate, no-native, internet, dns, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-dns-hero/report.json` | No-native DNS/internet utility with target SDK 36 and a manageable APK; selected as a networking utility row with a likely standard Gradle dependency tree. |
| RadarWeather | `org.woheller69.weather` | 6.7 (67) | source-validated-real | 1 | 0 | 17 | clean-candidate, no-native, internet, weather, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v14/report-real-radarweather/report.json` | No-native weather app with target SDK 34, internet behavior, and a moderate source tarball; selected as a second weather-style row to improve the chance of v14 proof yield. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
