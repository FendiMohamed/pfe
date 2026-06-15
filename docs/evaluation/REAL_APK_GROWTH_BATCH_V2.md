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
| Report root | `data/results/evaluation/real-apk-growth-batch-v2` |
| Classes covered | androidx, browser, crypto-password, device-connectivity, file-transfer, flutter, framework-boundary, game, large-apk, modern, multidex-likely, native-heavy, native-so, no-native, older-long-lived, r8-likely, security, simple-real, small-apk, source-linked, sync-client, vpn-security, work-profile |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| LocalSend | `org.localsend.localsend_app` | 1.17.0 (583) | smoke-real | 1 | 4 | 8 | flutter, framework-boundary, file-transfer, modern, native-so, r8-likely | ok: `data/results/evaluation/real-apk-growth-batch-v2/report-real-localsend/report.json` | Flutter/file-transfer app that exercises framework-boundary behavior and native artifacts. |
| OpenVPN for Android | `de.blinkt.openvpn` | 0.7.64 (219) | limitation | 3 | 24 | 44 | native-heavy, vpn-security, source-linked, large-apk, native-so | ok: `data/results/evaluation/real-apk-growth-batch-v2/report-real-openvpn-for-android/report.json` | Native-heavy VPN/security case; useful for keeping native hash-only behavior separate from Maven accuracy. |
| KeePassDX | `com.kunzisoft.keepass.libre` | 4.4.3 (44300) | smoke-real | 3 | 8 | 25 | security, crypto-password, native-so, source-linked, modern | ok: `data/results/evaluation/real-apk-growth-batch-v2/report-real-keepassdx/report.json` | Security/password manager case with native code and a compact source tarball for a later proof bundle. |
| Gadgetbridge | `nodomain.freeyourgadget.gadgetbridge` | 0.91.1 (248) | smoke-real | 3 | 8 | 29 | older-long-lived, device-connectivity, native-so, source-linked | ok: `data/results/evaluation/real-apk-growth-batch-v2/report-real-gadgetbridge/report.json` | Long-lived device-connectivity app that adds an older/legacy-style real APK family. |
| DAVx5 | `at.bitfire.davdroid` | 4.5.12-ose (405120004) | smoke-real | 2 | 8 | 13 | sync-client, modern, androidx, native-so, source-linked | ok: `data/results/evaluation/real-apk-growth-batch-v2/report-real-davx5/report.json` | Modern sync client with source tarball metadata and a likely non-trivial dependency tree. |
| Shelter | `net.typeblog.shelter` | 1.9.1 (445) | smoke-real | 1 | 0 | 3 | no-native, simple-real, security, work-profile, small-apk | ok: `data/results/evaluation/real-apk-growth-batch-v2/report-real-shelter/report.json` | Small no-native security/work-profile app to balance the native-heavy batch members. |
| TheXTech | `ru.wohlsoft.thextech.fdroid` | 1.3.7.2 (1030702) | limitation | 1 | 4 | 21 | game, native-heavy, framework-boundary, native-so | ok: `data/results/evaluation/real-apk-growth-batch-v2/report-real-thextech/report.json` | Game/native-heavy case for the Unity/game-engine-style boundary, even though it is not Unity itself. |
| Fennec F-Droid | `org.mozilla.fennec_fdroid` | 151.0.2 (1510220) | smoke-real | 3 | 15 | 34 | large-apk, browser, native-so, modern, multidex-likely | ok: `data/results/evaluation/real-apk-growth-batch-v2/report-real-fennec-fdroid/report.json` | Large browser APK that stress-tests extraction/reporting and broadens the modern/native coverage. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
