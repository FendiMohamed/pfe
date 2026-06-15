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
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v6` |
| Classes covered | calculator, clean-candidate, diary, health-manager, internet, local-media-player, modern-source, multimedia, no-native, online-media-player, recipe-manager, science-education, source-linked, sports-health |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| microMathematics Plus | `com.mkulesh.micromath.plus` | 2.23.3 (325) | source-validated-real | 2 | 0 | 16 | clean-candidate, no-native, calculator, science-education, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-micromathematics-plus/report.json` | No-native modern calculator/science app with a medium APK, source tarball metadata, target SDK 36, and enough size to plausibly emit non-sparse Maven evidence. |
| Retro Music | `code.name.monkey.retromusic` | 6.6.0 (10660) | source-validated-real | 1 | 0 | 6 | clean-candidate, no-native, multimedia, local-media-player, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-retro-music/report.json` | No-native media player with source tarball metadata, target SDK 36, and a medium APK/source size; useful for a richer AndroidX/Kotlin clean-candidate probe. |
| Broccoli | `com.flauschcode.broccoli` | 1.4.4 (1040400) | source-validated-real | 3 | 0 | 20 | clean-candidate, no-native, recipe-manager, sports-health, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-broccoli/report.json` | No-native recipe/health app with source tarball metadata and a non-trivial source tree; adds a different app family to the clean non-sparse search. |
| Diaguard | `com.faltenreich.diaguard` | 3.15.1 (68) | source-validated-real | 1 | 0 | 5 | clean-candidate, no-native, health-manager, diary, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-diaguard/report.json` | No-native health/diary app with source tarball metadata, target SDK 36, and a moderate dependency surface candidate. |
| LibreTube | `com.github.libretube` | 31.4 (70) | source-validated-real | 3 | 0 | 13 | clean-candidate, no-native, internet, multimedia, online-media-player, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v6/report-real-libretube/report.json` | No-native internet/media app with source tarball metadata, target SDK 36, and a medium APK; useful as another modern media-family clean-candidate probe. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
