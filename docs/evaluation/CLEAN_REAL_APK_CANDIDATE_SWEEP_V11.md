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
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v11` |
| Classes covered | bookmark, clean-candidate, clock, cloud-storage, connectivity, diet, file-transfer, health, internet, modern-source, no-native, reading, source-linked, weather |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| floccus bookmark sync | `org.handmadeideas.floccus` | 5.9.1 (5009001) | source-validated-real | 2 | 0 | 13 | clean-candidate, no-native, bookmark, internet, reading, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-floccus/report.json` | No-native bookmark-sync app with target SDK 35, a medium APK, and a large source tarball; selected as a richer internet/reading clean non-sparse candidate. |
| Waistline | `com.waist.line` | 3.10.1 (31001) | source-validated-real | 1 | 0 | 15 | clean-candidate, no-native, health, diet, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-waistline/report.json` | No-native health/diet tracker with target SDK 35, non-trivial APK and source sizes, and a maintained GitHub source link; useful for a dependency-rich non-sparse clean probe outside internet apps. |
| OpenCloud | `eu.opencloud.android` | 1.2.3 (9) | source-validated-real | 3 | 0 | 22 | clean-candidate, no-native, cloud-storage, internet, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-opencloud/report.json` | No-native cloud/file-sync client with target SDK 35 and source tarball metadata; adds another sync-client clean-candidate while avoiding previously blocked ownCloud. |
| NightDream | `com.firebirdberlin.nightdream.noGms` | 2.11.26 (348) | source-validated-real | 2 | 0 | 21 | clean-candidate, no-native, clock, weather, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-nightdream/report.json` | No-native clock/weather app with target SDK 36, medium APK size, and a sizeable source tarball; selected for a compact utility/media-adjacent clean non-sparse attempt. |
| SambaLite | `de.schliweb.sambalite` | 2.5.1 (20501) | source-validated-real | 2 | 0 | 19 | clean-candidate, no-native, cloud-storage, connectivity, file-transfer, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v11/report-real-sambalite/report.json` | No-native SMB/CIFS client with target SDK 36, medium APK size, and source tarball metadata; broadens the clean sweep into connectivity/file-transfer without repeating Primitive FTPd. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
