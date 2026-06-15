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
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v8` |
| Classes covered | browser, clean-candidate, email, internet, modern-source, money, multimedia, no-native, source-linked, wallet |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Drift // Audio | `io.github.probably_oxy.drift` | 0.1.0 (1) | source-validated-real | 1 | 0 | 13 | clean-candidate, no-native, multimedia, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-drift-audio/report.json` | No-native modern multimedia app with a medium APK, target SDK 36, and a sizeable source tree that may emit a richer Kotlin/AndroidX dependency surface than the sparse clean rows. |
| JaMuz | `org.phramusca.jamuz` | 0.6.14 (21) | source-validated-real | 2 | 0 | 21 | clean-candidate, no-native, internet, multimedia, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-jamuz/report.json` | No-native media/internet client with target SDK 36, a balanced APK size, and a large source tarball that looks promising for non-sparse emitted Maven evidence. |
| monocles browser | `de.monocles.browser` | 1.9.3 (14) | source-validated-real | 1 | 0 | 0 | clean-candidate, no-native, browser, internet, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-monocles-browser/report.json` | No-native privacy browser with a large modern source tree and target SDK 36; useful for another high-surface browser-family attempt toward a clean non-sparse row. |
| Conceal Mobile | `com.concealnetwork.concealmobile` | 5.0.4 (50) | source-validated-real | 2 | 0 | 13 | clean-candidate, no-native, internet, money, wallet, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-conceal-mobile/report.json` | No-native wallet app with a medium APK, target SDK 35, and a substantial source tarball that broadens the clean-candidate search into the money/security-adjacent family. |
| Ltt.rs | `rs.ltt.android` | 0.4.4 (19) | source-validated-real | 2 | 0 | 12 | clean-candidate, no-native, email, internet, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-lttrs/report.json` | No-native email/internet app with a medium APK, target SDK 35, and a large source tree; it is a good candidate for a richer modern communication-family proof row. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
