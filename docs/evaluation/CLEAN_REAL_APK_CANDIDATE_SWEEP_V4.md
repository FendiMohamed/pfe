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
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v4` |
| Classes covered | browser, clean-candidate, cloud-storage, finance, health, modern-source, no-native, older-profile, reader, security, source-linked |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Cryptomator | `org.cryptomator.lite` | 1.12.3 (3030) | source-validated-real | 6 | 0 | 24 | clean-candidate, no-native, security, cloud-storage, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-cryptomator-lite/report.json` | No-native security/cloud-storage app with a non-trivial APK size; likely to expose richer AndroidX/Kotlin Maven evidence. |
| Daily Dozen | `org.nutritionfacts.dailydozen` | 28 (93) | source-validated-real | 1 | 0 | 2 | clean-candidate, no-native, health, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-daily-dozen/report.json` | No-native health app with source tarball metadata and moderate dependency surface; useful as another clean/non-sparse candidate. |
| Privacy Browser | `com.stoutner.privacybrowser.standard` | 3.20.1 (81) | source-validated-real | 1 | 0 | 0 | clean-candidate, no-native, browser, security, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-privacy-browser/report.json` | No-native browser/security app with source tarball metadata; tests a different app family without native library claims. |
| MoneyWallet | `com.oriondev.moneywallet` | 4.0.5.10 (75) | source-validated-real | 2 | 0 | 9 | clean-candidate, no-native, finance, older-profile, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-moneywallet/report.json` | No-native finance app that may expose older dependency/version-band behavior while still avoiding native/toolchain blockers. |
| Easy Xkcd | `de.tap.easy_xkcd` | 8.4 (193) | source-validated-real | 2 | 0 | 23 | clean-candidate, no-native, reader, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-easy-xkcd/report.json` | No-native reader app with source tarball metadata; useful as a compact candidate if it emits more than sparse Maven evidence. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
