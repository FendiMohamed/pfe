# Real APK Growth Batch V2

This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.
It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 1 |
| Succeeded | 1 |
| Failed | 0 |
| APK root | `data/test_apks/real` |
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v11` |
| Classes covered | clean-candidate, cloud-storage, connectivity, file-transfer, modern-source, no-native, source-linked |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
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
