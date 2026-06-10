# Real APK Priority Reference Catalog

This is the deadline-friendly reference expansion lane. It keeps the full all-versions lane honest, but prioritizes exact versions that actually appear in the real APK source-validation dependency trees.

## Summary

- Dependency tree files scanned: `4599`
- Unique coordinates: `1339`
- Unique coordinate-version slots: `3241`
- Tier 1 repeated real-APK versions: `1132`
- Tier 2 single real-APK versions: `2109`
- Download config libraries: `1339`
- Download config slots: `3241`

## Policy

- This is an evaluation-only priority DB lane.
- It prioritizes exact versions observed in the real APK source-validation corpus.
- It does not replace the full 60979-slot all-versions transparency lane.
- No shared calibrated DB, matcher scoring, SBOM emission, or vulnerability labels are changed by this catalog.

## Build Checkpoint

Current local build state:

- Download config slots: `3241`
- Downloaded artifact metadata records: `2610`
- Downloaded artifact rows not recovered: `631` honest 404/source-boundary rows
- Conversion records present: `2610`
- Conversion statuses: `1892` converted, `20` existing, `698` skipped
- Remaining downloaded artifacts awaiting conversion: `0`
- Next conversion offset: complete
- Feature DB extraction: advanced through converted/existing offset `799`
- Stored priority DB components: `800`
- Extraction failures so far: `0`
- Next extraction offset: `800`

The high 404 count is expected because the Gradle dependency trees include source/module aliases, JitPack-style coordinates, plugin/internal artifacts, relocated AndroidX/common variants, and repository-specific rows that are valid source evidence but not directly downloadable from the default Maven/Google repositories used by this evaluation-only builder.

## Top Repeated Versions

| Rank | Tier | Coordinate | Version | APK support | Occurrences |
|---:|---|---|---|---:|---:|
| 1 | tier1-repeated-real-apk-version | `androidx.loader:loader` | `1.0.0` | 35 | 169 |
| 2 | tier1-repeated-real-apk-version | `androidx.customview:customview` | `1.1.0` | 34 | 486 |
| 3 | tier1-repeated-real-apk-version | `androidx.interpolator:interpolator` | `1.0.0` | 34 | 331 |
| 4 | tier1-repeated-real-apk-version | `androidx.resourceinspection:resourceinspection-annotation` | `1.0.1` | 34 | 179 |
| 5 | tier1-repeated-real-apk-version | `androidx.cursoradapter:cursoradapter` | `1.0.0` | 34 | 144 |
| 6 | tier1-repeated-real-apk-version | `androidx.viewpager:viewpager` | `1.0.0` | 34 | 143 |
| 7 | tier1-repeated-real-apk-version | `androidx.versionedparcelable:versionedparcelable` | `1.1.1` | 34 | 127 |
| 8 | tier1-repeated-real-apk-version | `androidx.arch.core:core-common` | `2.2.0` | 33 | 466 |
| 9 | tier1-repeated-real-apk-version | `androidx.arch.core:core-runtime` | `2.2.0` | 33 | 346 |
| 10 | tier1-repeated-real-apk-version | `androidx.cardview:cardview` | `1.0.0` | 33 | 138 |
| 11 | tier1-repeated-real-apk-version | `androidx.slidingpanelayout:slidingpanelayout` | `1.2.0` | 32 | 126 |
| 12 | tier1-repeated-real-apk-version | `androidx.vectordrawable:vectordrawable` | `1.1.0` | 31 | 276 |
| 13 | tier1-repeated-real-apk-version | `androidx.concurrent:concurrent-futures` | `1.1.0` | 31 | 230 |
| 14 | tier1-repeated-real-apk-version | `androidx.vectordrawable:vectordrawable-animated` | `1.1.0` | 31 | 112 |
| 15 | tier1-repeated-real-apk-version | `androidx.preference:preference` | `1.2.1` | 31 | 98 |
| 16 | tier1-repeated-real-apk-version | `org.jspecify:jspecify` | `1.0.0` | 30 | 472 |
| 17 | tier1-repeated-real-apk-version | `androidx.tracing:tracing` | `1.2.0` | 30 | 252 |
| 18 | tier1-repeated-real-apk-version | `androidx.coordinatorlayout:coordinatorlayout` | `1.1.0` | 30 | 121 |
| 19 | tier1-repeated-real-apk-version | `androidx.legacy:legacy-support-core-utils` | `1.0.0` | 30 | 120 |
| 20 | tier1-repeated-real-apk-version | `androidx.print:print` | `1.0.0` | 30 | 62 |
| 21 | tier1-repeated-real-apk-version | `androidx.core:core-viewtree` | `1.0.0` | 29 | 216 |
| 22 | tier1-repeated-real-apk-version | `androidx.drawerlayout:drawerlayout` | `1.1.1` | 29 | 210 |
| 23 | tier1-repeated-real-apk-version | `org.jetbrains:annotations` | `23.0.0` | 29 | 144 |
| 24 | tier1-repeated-real-apk-version | `androidx.customview:customview-poolingcontainer` | `1.0.0` | 29 | 71 |
| 25 | tier1-repeated-real-apk-version | `androidx.annotation:annotation` | `1.9.1` | 28 | 3182 |
| 26 | tier1-repeated-real-apk-version | `androidx.startup:startup-runtime` | `1.1.1` | 28 | 244 |
| 27 | tier1-repeated-real-apk-version | `androidx.localbroadcastmanager:localbroadcastmanager` | `1.0.0` | 28 | 59 |
| 28 | tier1-repeated-real-apk-version | `androidx.annotation:annotation-jvm` | `1.9.1` | 28 | 58 |
| 29 | tier1-repeated-real-apk-version | `androidx.appcompat:appcompat` | `1.7.1` | 27 | 433 |
| 30 | tier1-repeated-real-apk-version | `androidx.annotation:annotation-experimental` | `1.4.1` | 27 | 363 |

## Next Commands

```powershell
python scripts\build_real_apk_priority_reference_catalog.py
docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven --config configs/libraries.real_apk_priority_versions.json --output-root data/reference_db/artifacts_real_apk_priority_versions --limit 500 --offset 0 --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex --artifact-root data/reference_db/artifacts_real_apk_priority_versions --output-root data/reference_db/dex_real_apk_priority_versions --limit 100 --offset 0 --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features --dex-root data/reference_db/dex_real_apk_priority_versions --db-path data/reference_db/reference_features_real_apk_priority_versions.sqlite --limit 100 --offset 800 --quiet
```
