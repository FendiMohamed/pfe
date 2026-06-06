# Real APK Growth Batch V2

This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.
It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 5 |
| Succeeded | 5 |
| Failed | 0 |
| APK root | `data/test_apks/real` |
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v9` |
| Classes covered | clean-candidate, cloud-storage, crypto, erp-crm, internet, modern-source, news, no-native, older-profile, rss-widget, security, source-linked, weather |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| DoliDroid | `com.nltechno.dolidroidpro` | 3.0.69 (69) | source-validated-real | 2 | 0 | 14 | clean-candidate, no-native, internet, erp-crm, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-dolidroid/report.json` | No-native ERP/CRM front-end with target SDK 36, a medium APK, and a large source tarball; useful for another dependency-rich internet/business clean-candidate probe. |
| ownCloud | `com.owncloud.android` | 4.8.0 (48000000) | source-validated-real | 3 | 0 | 22 | clean-candidate, no-native, cloud-storage, internet, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-owncloud/report.json` | No-native cloud-storage client with target SDK 35 and a non-trivial APK/source profile; adds a maintained sync-client family to the clean non-sparse search. |
| Your local weather | `org.thosp.yourlocalweather` | 6.4.0-FOSS (193) | source-validated-real | 3 | 0 | 17 | clean-candidate, no-native, internet, weather, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-your-local-weather/report.json` | No-native weather app with target SDK 36, medium APK/source sizes, and internet/weather coverage distinct from earlier weather candidates. |
| OpenKeychain: Easy PGP | `org.sufficientlysecure.keychain` | 6.0.4 (60400) | source-validated-real | 1 | 0 | 12 | clean-candidate, no-native, security, crypto, older-profile, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-openkeychain/report.json` | No-native security/PGP app with target SDK 34 and a sizeable source tree; useful as a security-family clean-candidate attempt and an older-profile comparison row. |
| HomeFeed - RSS Widget | `com.byterdevs.rsswidget` | 1.3.0 (4) | source-validated-real | 2 | 0 | 17 | clean-candidate, no-native, internet, news, rss-widget, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v9/report-real-homefeed-rss-widget/report.json` | No-native RSS/news widget with target SDK 36 and a moderate source tree; adds a compact modern internet/news candidate to the clean non-sparse probe. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
