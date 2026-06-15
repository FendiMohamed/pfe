# Real APK Growth Batch V2

This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.
It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 3 |
| Succeeded | 3 |
| Failed | 0 |
| APK root | `data/test_apks/real` |
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep` |
| Classes covered | androidx-likely, app-store-client, clean-candidate, network-media, no-native, source-linked, utility |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| Foxy Droid | `nya.kitsunyan.foxydroid` | 1.3 (4) | source-validated-real | 1 | 0 | 6 | clean-candidate, no-native, app-store-client, androidx-likely, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep/report-real-foxy-droid/report.json` | No-native F-Droid app-store client with source tarball metadata; likely to emit non-sparse Java/Kotlin Maven evidence. |
| WebRadio | `starcom.snd` | 1.5 (5) | source-validated-real | 1 | 0 | 0 | clean-candidate, no-native, network-media, androidx-likely, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep/report-real-webradio/report.json` | Small no-native radio/network app with source tarball metadata; useful as a low-friction clean/non-sparse candidate if the report emits Maven components. |
| Equate | `com.llamacorp.equate` | 2.0 (12) | source-validated-real | 1 | 0 | 0 | clean-candidate, no-native, utility, androidx-likely, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep/report-real-equate/report.json` | No-native unit-converter app with source tarball metadata; included as a compact Java/Kotlin control candidate. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
