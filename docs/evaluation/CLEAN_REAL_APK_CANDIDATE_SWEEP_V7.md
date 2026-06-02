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
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v7` |
| Classes covered | browser, clean-candidate, internet, modern-source, money, no-native, security, social-network, source-linked, time, vpn-proxy |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| AndStatus | `org.andstatus.app` | 62.03 (370) | source-validated-real | 2 | 0 | 19 | clean-candidate, no-native, internet, social-network, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-andstatus/report.json` | No-native social/internet app with a medium APK, target SDK 35, source tarball metadata, and a size profile that may yield richer emitted Maven evidence. |
| Fulguris Web Browser | `net.slions.fulguris.full.fdroid` | 2.0.10 (261) | source-validated-real | 2 | 0 | 21 | clean-candidate, no-native, browser, internet, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-fulguris-web-browser/report.json` | No-native browser candidate with a medium APK and large source tree; useful for another richer browser/internet clean-candidate pass. |
| I2P | `net.i2p.android.router` | 2.11.0 (4745304) | source-validated-real | 3 | 0 | 18 | clean-candidate, no-native, internet, security, vpn-proxy, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-i2p/report.json` | No-native security/networking candidate with a medium APK and large source tree; useful for a richer security-family proof attempt. |
| Working Time Account | `askanimus.arbeitszeiterfassung2` | 2.11.012 (211012) | source-validated-real | 1 | 0 | 15 | clean-candidate, no-native, money, time, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-working-time-account/report.json` | No-native work/time candidate with target SDK 36 and a medium APK/source size; adds a different app family to the clean non-sparse search. |
| Mastodon | `org.joinmastodon.android` | 2.12.3 (182) | source-validated-real | 2 | 0 | 0 | clean-candidate, no-native, internet, social-network, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-mastodon/report.json` | No-native modern social app with source tarball metadata and a likely non-trivial AndroidX/Kotlin dependency surface despite a smaller APK. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
