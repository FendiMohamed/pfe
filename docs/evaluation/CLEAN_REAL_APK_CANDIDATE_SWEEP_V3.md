# Real APK Growth Batch V2

This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.
It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 4 |
| Succeeded | 4 |
| Failed | 0 |
| APK root | `data/test_apks/real` |
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v3` |
| Classes covered | clean-candidate, health-utility, modern-source, no-native, password-manager, security, source-linked, time-tracker, wallpaper |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Simple Time Tracker | `com.razeeman.util.simpletimetracker` | 1.57 (139) | source-validated-real | 2 | 0 | 12 | clean-candidate, no-native, time-tracker, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-simple-time-tracker/report.json` | No-native maintained Kotlin/Android utility with a larger APK than prior clean-candidate utilities; likely to expose non-sparse AndroidX/Kotlin Maven evidence. |
| MedTimer | `com.futsch1.medtimer` | 1.22.18 (173) | source-validated-real | 4 | 0 | 18 | clean-candidate, no-native, health-utility, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-medtimer/report.json` | No-native health/reminder utility with source tarball metadata and enough APK size to test a non-sparse clean candidate. |
| Doodle | `xyz.zedler.patrick.doodle` | 6.0.0 (42) | source-validated-real | 1 | 0 | 6 | clean-candidate, no-native, wallpaper, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-doodle/report.json` | No-native modern wallpaper app with source tarball metadata; useful UI-heavy AndroidX/Kotlin clean-candidate evidence if source validation succeeds. |
| KeePassVault | `com.ivanovsky.passnotes` | 1.16.0 (11600) | source-validated-real | 4 | 0 | 24 | clean-candidate, no-native, security, password-manager, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-keepassvault/report.json` | No-native security/password-manager app with source tarball metadata; tests whether a more dependency-rich security app can become clean source-validated evidence. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
