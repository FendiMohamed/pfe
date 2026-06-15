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
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v2` |
| Classes covered | clean-candidate, kde-utility, launcher, messaging-notification, modern-source, no-native, source-linked, system-utility |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Gotify | `com.github.gotify` | 2.10.0 (35) | source-validated-real | 2 | 0 | 23 | clean-candidate, no-native, messaging-notification, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-gotify/report.json` | Recent no-native notification client with source tarball metadata; likely to expose networking/AndroidX Maven evidence. |
| BetterCounter | `org.kde.bettercounter` | 6.0.3 (60003) | source-validated-real | 2 | 0 | 7 | clean-candidate, no-native, kde-utility, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-bettercounter/report.json` | Recent no-native KDE utility app; useful as a compact modern clean candidate if Maven evidence is non-sparse. |
| Olauncher | `app.olauncher` | v6.4.2 (105) | source-validated-real | 1 | 0 | 2 | clean-candidate, no-native, launcher, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-olauncher/report.json` | Recent no-native launcher with source tarball metadata; tests a UI-heavy Java/Kotlin app family. |
| Coffee | `com.github.muellerma.coffee` | 2.26 (46) | source-validated-real | 1 | 0 | 11 | clean-candidate, no-native, system-utility, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-coffee/report.json` | Recent no-native system utility from the same family as Stopwatch; useful if it emits more Maven evidence. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
