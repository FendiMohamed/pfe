# Real APK Growth Batch V2

This batch adds category-balanced real APK smoke/report coverage before Phase 6 or ML work.
It is intentionally not source-validated accuracy evidence yet: rows remain excluded from source-validated metrics until each app has APK/source matching, a resolved dependency tree, generated report, and source-validation output.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 6 |
| Succeeded | 6 |
| Failed | 0 |
| APK root | `data/test_apks/real` |
| Report root | `data/results/evaluation/clean-real-apk-candidate-sweep-v13` |
| Classes covered | bookmark, clean-candidate, internet, library-inspection, maps, messaging, modern-source, navigation, news, no-native, public-transport, reading, rss, source-linked, system |

## APKs

| App | Package | Version | Layer | DEX | Native `.so` | SBOM components | Classes | Report | Why selected |
|---|---|---|---|---:|---:|---:|---|---|---|
| LibChecker | `com.absinthe.libchecker` | 2.5.3 (2515) | source-validated-real | 1 | 0 | 2 | clean-candidate, no-native, system, library-inspection, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-libchecker/report.json` | No-native system/library-inspection app with target SDK 36, a moderate APK, and a nontrivial source tarball; selected as a modern AndroidX/Kotlin-style candidate likely to exercise useful dependency evidence without native boundaries. |
| OpenTopoMap Viewer | `org.nitri.opentopo` | 1.29 (66) | source-validated-real | 2 | 0 | 22 | clean-candidate, no-native, navigation, maps, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-opentopomap-viewer/report.json` | No-native navigation/map app with target SDK 36, a medium APK, source tarball, and internet/location behavior; selected for non-sparse map-style Android dependencies without native map libraries. |
| Railway station photos | `de.bahnhoefe.deutschlands.bahnhofsfotos` | 16.4.0 (97) | source-validated-real | 2 | 0 | 23 | clean-candidate, no-native, navigation, public-transport, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-railway-station-photos/report.json` | No-native public-transport/navigation app with target SDK 36, source tarball, and location/network permissions; selected to diversify clean-candidate evidence beyond notes, browsers, and password utilities. |
| LinkDroid for Linkwarden | `com.sbv.linkdroid` | 2.1.9 (26) | source-validated-real | 2 | 0 | 20 | clean-candidate, no-native, internet, bookmark, reading, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-linkdroid/report.json` | No-native internet/bookmark client with target SDK 36, manageable source size, and likely modern networking/UI dependencies; selected as a practical sync-client-style clean candidate. |
| Quasseldroid | `com.iskrembilen.quasseldroid` | 1.8.0 (1398) | source-validated-real | 1 | 0 | 17 | clean-candidate, no-native, internet, messaging, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-quasseldroid/report.json` | No-native internet/messaging app with target SDK 36 and a larger source tarball; selected as a real networking client likely to produce a meaningful runtime dependency tree. |
| TTRSS-Reader | `org.ttrssreader` | 1.98.1 (1981) | source-validated-real | 1 | 0 | 0 | clean-candidate, no-native, internet, news, rss, modern-source, source-linked | ok: `data/results/evaluation/clean-real-apk-candidate-sweep-v13/report-real-ttrss-reader/report.json` | No-native RSS/news client with target SDK 36, source tarball, and network/background-service behavior; selected as a likely non-sparse internet app while avoiding already-used Nextcloud News and HomeFeed rows. |

## Proof-Gate Follow-Up

- Companion proof status: `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`.
- The companion artifact records source tarball checks, Gradle dependency-tree attempts, and source-validation output when available.
- A row becomes source-validated evidence only when the companion proof status shows a resolved dependency tree and completed source validation.

## Remaining Admission Work

- Promote none of these rows into source-validated metrics from this file alone.
- For source-linked candidates, download or checkout the matching source and capture the runtime dependency tree.
- For framework/native-heavy candidates, preserve limitation labels when the report has little Java/Kotlin Maven evidence.
- Add a separate protected or packed real APK if a legal redistribution source is found; F-Droid apps are useful but usually not commercial-protected samples.
