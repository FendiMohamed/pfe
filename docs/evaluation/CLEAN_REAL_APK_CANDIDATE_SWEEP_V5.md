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
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v5` |
| Classes covered | calculator, clean-candidate, dictionary, firewall, habit-tracker, internet, modern-source, no-native, reader, science-education, security, source-linked, sports-health, weather |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| yetCalc | `yetzio.yetcalc` | 2.0.8 (24) | source-validated-real | 3 | 0 | 17 | clean-candidate, no-native, calculator, science-education, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-yetcalc/report.json` | No-native modern calculator/unit-converter app with source tarball metadata and a non-trivial APK size; candidate for clean non-sparse Maven evidence. |
| Loop Habit Tracker | `org.isoron.uhabits` | 2.3.1 (20301) | source-validated-real | 1 | 0 | 11 | clean-candidate, no-native, habit-tracker, sports-health, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-loop-habit-tracker/report.json` | No-native maintained habit-tracking app with source tarball metadata and a moderate APK/source size; useful health/productivity candidate. |
| QuickDic | `de.reimardoeffinger.quickdic` | 5.8.2 (131) | source-validated-real | 2 | 0 | 2 | clean-candidate, no-native, dictionary, reader, science-education, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-quickdic/report.json` | No-native dictionary/reader app with source tarball metadata and enough APK size to expose richer Java/Kotlin Maven evidence if present. |
| Cirrus | `org.woheller69.omweather` | 4.7 (47) | source-validated-real | 3 | 0 | 19 | clean-candidate, no-native, weather, internet, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-cirrus/report.json` | No-native weather app with source tarball metadata; adds a compact internet/weather family to the clean-candidate search. |
| AFWall+ | `dev.ukanth.ufirewall` | 4.0.3 (20260301) | source-validated-real | 3 | 0 | 18 | clean-candidate, no-native, security, firewall, internet, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v5/report-real-afwall-plus/report.json` | No-native firewall/security app with source tarball metadata; tests another security family without native library claims. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
