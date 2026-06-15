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
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v10` |
| Classes covered | calendar, clean-candidate, connectivity, email, file-transfer, internet, modern-source, multimedia, no-native, notes, radio, security, source-linked, task, time, writing |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Etar - OpenSource Calendar | `ws.xsoh.etar` | 1.0.55 (55) | source-validated-real | 4 | 0 | 38 | clean-candidate, no-native, calendar, time, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-etar/report.json` | No-native calendar/time app with target SDK 36, medium APK size, and a source tarball; useful for a richer clean non-sparse AndroidX candidate probe. |
| RadioDroid | `net.programmierecke.radiodroid2` | 0.86 (96) | source-validated-real | 2 | 0 | 39 | clean-candidate, no-native, internet, multimedia, radio, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-radiodroid/report.json` | No-native internet/radio app with target SDK 33 and a moderate dependency surface; broadens clean-candidate coverage into multimedia streaming. |
| SimpleLogin Anti-spam | `io.simplelogin.android.fdroid` | 1.22.0 (12200) | source-validated-real | 2 | 0 | 39 | clean-candidate, no-native, email, internet, security, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-simplelogin/report.json` | No-native email/security app with target SDK 34 and source tarball metadata; useful for a compact modern account/security clean-candidate probe. |
| Omni Notes | `it.feio.android.omninotes.foss` | 6.3.1 (331) | source-validated-real | 1 | 0 | 39 | clean-candidate, no-native, notes, task, writing, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-omni-notes/report.json` | No-native notes/task app with target SDK 33, a medium APK, and a larger source tarball; useful for a non-sparse writing/productivity clean-candidate attempt. |
| Primitive FTPd | `org.primftpd` | 8.1 (70) | source-validated-real | 5 | 0 | 38 | clean-candidate, no-native, connectivity, file-transfer, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v10/report-real-primitive-ftpd/report.json` | No-native connectivity/file-transfer app with target SDK 36 and source tarball metadata; adds a network-service clean-candidate probe distinct from prior internet apps. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
