# Source-Observed Reference DB Batch Log

This log records evaluation-only reference DB growth from the source-observed catalog. It does not change the shared calibrated DB, matcher scoring, SBOM output, vulnerability labels, or source-validation metrics.

## Current Inputs

| Input | Value |
|---|---:|
| Source-observed catalog | `configs/source_observed_reference_catalog.json` |
| Source-version build config | `configs/libraries.source_observed_versions.json` |
| Buildable source-observed coordinates | 1361 |
| Buildable source-version artifact slots | 3347 |
| Metadata-only skips before build | 9 |

## Batch 000

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 25 --offset 0` into `data/reference_db/artifacts_source_observed_versions` | 25 downloaded, 0 failed |
| Convert | `--limit 25 --offset 0` into `data/reference_db/dex_source_observed_versions` | 25 converted, 0 skipped, 0 failed |
| Extract | `--reset` into `data/reference_db/reference_features_source_observed_versions.sqlite` | 25 stored, 0 failed |

Feature extraction counts for this first evaluation-only DB slice:

| Feature table / metric | Rows |
|---|---:|
| Components | 25 |
| DEX files | 25 |
| Packages | 103 |
| Classes | 2671 |
| Methods | 12200 |
| Opcodes | 1689 |
| API references | 16620 |
| String literals | 2563 |
| Dependency shapes | 326 |
| Class dependencies | 4348 |
| Opcode n-grams | 28288 |
| Call-chain opcode fingerprints | 2645 |
| Basic-block opcode fingerprints | 9681 |
| Class-neighbor summaries | 885 |
| Field-operation sequences | 1757 |
| Literal/context features | 6438 |

## Batch 001

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 25 --offset 25` into `data/reference_db/artifacts_source_observed_versions` | 25 downloaded, 0 failed |
| Convert | `--limit 25 --offset 25` into `data/reference_db/dex_source_observed_versions` | 15 converted, 10 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `25` | 15 stored, 0 failed |

No-bytecode skips in this batch were AndroidX wrapper/metadata artifacts where D8 completed but produced no `classes*.dex`: `androidx.activity:activity-ktx` (`1.10.1`, `1.11.0`, `1.12.2`, `1.12.4`, `1.13.0`, `1.9.0`, `1.9.1`, `1.9.2`, `1.9.3`) and `androidx.annotation:annotation@1.10.0`.

## Batch 002

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 25 --offset 50` into `data/reference_db/artifacts_source_observed_versions` | 18 downloaded, 7 failed |
| Convert | downloaded records after artifact offset `50` into `data/reference_db/dex_source_observed_versions` | 10 converted, 8 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `40` | 10 stored, 0 failed |

Download failures were real `404 Not Found` results for `androidx.annotation:annotation-experimental` source versions `1.0.0`, `1.1.0`, `1.3.0`, `1.4.0`, `1.4.1`, `1.5.0`, and `1.5.1`. No-bytecode skips were `androidx.annotation:annotation` versions `1.6.0`, `1.7.0`, `1.7.1`, `1.8.0`, `1.8.1`, `1.8.2`, `1.9.0`, and `1.9.1`.

## Batch 003

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 25 --offset 75` into `data/reference_db/artifacts_source_observed_versions` | 22 downloaded, 3 failed |
| Convert | downloaded records after artifact offset `68` into `data/reference_db/dex_source_observed_versions` | 22 converted, 0 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `50` | 22 stored, 0 failed |

Download failures were real `404 Not Found` results for `androidx.arch.core:core-runtime` source versions `2.0.0`, `2.1.0`, and `2.2.0`.

## Batch 004

This batch switches from 25-slot slices to 100-slot slices for faster source-observed DB growth while keeping failures explicit.

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 100` into `data/reference_db/artifacts_source_observed_versions` | 100 downloaded, 0 failed |
| Convert | downloaded records after artifact offset `90` into `data/reference_db/dex_source_observed_versions` | 58 converted, 42 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `72` | 58 stored, 0 failed |

No-bytecode skips in this batch were AndroidX wrapper/platform artifacts. The skip reasons were `D8 completed but no classes*.dex files were produced` for `androidx.collection:collection` / `collection-ktx` versions, and `AAR contains no classes.jar; no JVM bytecode to dex` for public Compose wrapper artifacts such as `androidx.compose.animation:animation`, `androidx.compose.animation:animation-core`, and `androidx.compose.foundation:foundation`.

## Batch 005

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 200` into `data/reference_db/artifacts_source_observed_versions` | 95 downloaded, 5 failed |
| Convert | downloaded records after artifact offset `190` into `data/reference_db/dex_source_observed_versions` | 53 converted, 42 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `130` | 53 stored, 0 failed |

Download failures were real `404 Not Found` results for `androidx.compose.material:material-icons-extended@1.6.8` and `androidx.compose.runtime:runtime-annotation` versions `1.10.3`, `1.10.4`, `1.10.6`, and `1.11.1`. No-bytecode skips were mostly public Compose wrapper artifacts without `classes.jar`, including `foundation`, `foundation-layout`, `material`, `material-icons-core`, `material-icons-extended`, `material-ripple`, `material3`, adaptive Material3 artifacts, and `runtime`.

## Batch 006

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 300` into `data/reference_db/artifacts_source_observed_versions` | 96 downloaded, 4 failed |
| Convert | downloaded records after artifact offset `285` into `data/reference_db/dex_source_observed_versions` | 52 converted, 44 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `183` | 52 stored, 0 failed |

Download failures were real `404 Not Found` results for `androidx.compose.runtime:runtime-annotation` versions `1.9.0`, `1.9.2`, `1.9.4`, and `1.9.5`. No-bytecode skips were public Compose runtime/UI wrapper artifacts without `classes.jar`, including `runtime-retain`, `runtime-saveable`, `ui`, `ui-geometry`, and `ui-graphics`.

## Batch 007

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 400` into `data/reference_db/artifacts_source_observed_versions` | 91 downloaded, 9 failed |
| Convert | downloaded records after artifact offset `381` into `data/reference_db/dex_source_observed_versions` | 52 converted, 39 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `235` | 52 stored, 0 failed |

Download failures were real `404 Not Found` results for `androidx.concurrent:concurrent-futures-ktx` versions `1.1.0`, `1.2.0`, and `1.3.0`; `androidx.constraintlayout:constraintlayout-core` versions `1.0.0`, `1.0.2`, `1.0.4`, `1.1.0`, and `1.1.1`; and `androidx.constraintlayout:constraintlayout-solver@1.1.3`. No-bytecode skips were public Compose UI wrapper artifacts without `classes.jar`, plus `androidx.constraintlayout:constraintlayout-compose@1.1.1`.

## Batch 008

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 500` into `data/reference_db/artifacts_source_observed_versions` | 88 downloaded, 12 failed |
| Convert | downloaded records after artifact offset `472` into `data/reference_db/dex_source_observed_versions` | 88 converted, 0 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `287` | 88 stored, 0 failed |

Download failures were real `404 Not Found` results for `androidx.constraintlayout:constraintlayout-solver@2.0.1`, `androidx.core:core-location-altitude-external-protobuf` versions `1.0.0-beta01` and `1.0.0-rc01`, `androidx.core:core-location-altitude-proto` versions `1.0.0-beta01` and `1.0.0-rc01`, and `androidx.databinding:databinding-common` versions `8.1.4`, `8.13.1`, `8.13.2`, `8.2.2`, `8.7.3`, `9.0.1`, and `9.1.0`.

## Batch 009

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 600` into `data/reference_db/artifacts_source_observed_versions` | 88 downloaded, 12 failed |
| Convert | downloaded records after artifact offset `560` into `data/reference_db/dex_source_observed_versions` | 83 converted, 5 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `375` | 83 stored, 0 failed |

Download failures were real `404 Not Found` results for DataStore/protobuf, Glance/protobuf, Health Connect/protobuf, and Hilt common coordinates: `androidx.datastore:datastore-core@1.0.0`, `androidx.datastore:datastore-core-okio@1.2.0`, `androidx.datastore:datastore-core-okio-jvm@1.2.0`, `androidx.datastore:datastore-preferences-external-protobuf@1.2.0`, `androidx.datastore:datastore-preferences-proto@1.2.0`, `androidx.glance:glance-appwidget-external-protobuf@1.1.1`, `androidx.glance:glance-appwidget-proto@1.1.1`, `androidx.health.connect:connect-client-external-protobuf@1.1.0`, `androidx.health.connect:connect-client-proto@1.1.0`, and `androidx.hilt:hilt-common` versions `1.0.0`, `1.2.0`, and `1.3.0`. No-bytecode skips were `androidx.datastore` wrapper artifacts and `androidx.graphics:graphics-shapes@1.0.1`.

## Batch 010

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 700` into `data/reference_db/artifacts_source_observed_versions` | 91 downloaded, 9 failed |
| Convert | downloaded records after artifact offset `648` into `data/reference_db/dex_source_observed_versions` | 54 converted, 37 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `458` | 54 stored, 0 failed |

Download failures were real `404 Not Found` results for `androidx.lifecycle:lifecycle-common-jvm` versions `2.10.0`, `2.8.2`, `2.8.4`, `2.8.6`, `2.8.7`, `2.9.0`, `2.9.1`, `2.9.3`, and `2.9.4`. No-bytecode skips were AndroidX legacy and Lifecycle wrapper artifacts, including `androidx.legacy:legacy-preference-v14@1.0.0`, `androidx.legacy:legacy-support-v4@1.0.0`, `androidx.lifecycle:lifecycle-common`, `androidx.lifecycle:lifecycle-common-java8`, `androidx.lifecycle:lifecycle-livedata-core-ktx`, and `androidx.lifecycle:lifecycle-livedata-ktx`.

## Batch 011

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 800` into `data/reference_db/artifacts_source_observed_versions` | 100 downloaded, 0 failed |
| Convert | downloaded records after artifact offset `739` into `data/reference_db/dex_source_observed_versions` | 60 converted, 40 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `512` | 60 stored, 0 failed |

No-bytecode skips were mostly AndroidX Lifecycle wrapper artifacts where the public artifact has no JVM bytecode or D8 produced no `classes*.dex`, including `lifecycle-reactivestreams-ktx`, `lifecycle-runtime`, `lifecycle-runtime-compose`, `lifecycle-runtime-ktx`, `lifecycle-runtime-ktx-android`, and `lifecycle-viewmodel` versions from the `2.8.x`, `2.9.x`, and `2.10.0` bands.

## Batch 012

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 900` into `data/reference_db/artifacts_source_observed_versions` | 100 downloaded, 0 failed |
| Convert | downloaded records after artifact offset `839` into `data/reference_db/dex_source_observed_versions` | 83 bytecode-bearing records, 17 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `572` | 83 stored, 0 failed |

The first two conversion attempts timed out after making progress, so the resumed conversion recorded `58` newly `converted` rows and `25` `existing` rows for bytecode outputs that were already present on disk. Extraction accepts both statuses and stored all `83` bytecode-bearing records. No-bytecode skips were Lifecycle wrapper artifacts, including `androidx.lifecycle:lifecycle-viewmodel-compose`, `androidx.lifecycle:lifecycle-viewmodel-ktx`, and `androidx.lifecycle:lifecycle-viewmodel-savedstate` versions from the `2.8.x`, `2.9.x`, and `2.10.0` bands.

## Batch 013

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 1000` into `data/reference_db/artifacts_source_observed_versions` | 100 downloaded, 0 failed |
| Convert | downloaded records after artifact offset `939` into `data/reference_db/dex_source_observed_versions` plus a six-record backfill at sorted artifact offset `889` | 68 bytecode-bearing records, 32 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `655`, plus targeted `--coordinate androidx.media:media` extraction | 68 stored, 0 failed |

The download command timed out after writing all `100` metadata records. The first conversion attempt also timed out after progress, and the resumed conversion recorded `43` newly `converted` rows, `25` `existing` rows, and `32` no-bytecode skips across Navigation/NavigationEvent wrapper artifacts. A post-conversion consistency check found six missing conversion records for `androidx.media:media` versions `1.0.0`, `1.4.1`, `1.6.0`, `1.7.0`, `1.7.1`, and `1.8.0`; those were backfilled with `convert-reference-dex --limit 6 --offset 889` and then extracted with `extract-reference-features --coordinate androidx.media:media`. The final DB count matches the bytecode-bearing conversion count.

## Batch 014

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 1100` into `data/reference_db/artifacts_source_observed_versions` | 90 downloaded, 10 failed |
| Convert | downloaded records after artifact offset `1039` into `data/reference_db/dex_source_observed_versions` | 62 converted, 28 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `723` | 62 stored, 0 failed |

Download failures were real `404 Not Found` results for `androidx.paging:paging-common-ktx` versions `3.1.1`, `3.2.1`, `3.3.6`, and `3.5.0`; `androidx.resourceinspection:resourceinspection-annotation@1.0.1`; and `androidx.room:room-common-jvm` versions `2.7.0`, `2.7.1`, `2.7.2`, `2.8.0`, and `2.8.4`. No-bytecode skips were AndroidX NavigationEvent, Paging, Room, and SavedState wrapper artifacts without JVM bytecode or without produced `classes*.dex`.

## Batch 015

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 1200` into `data/reference_db/artifacts_source_observed_versions` | 100 downloaded, 0 failed |
| Convert | downloaded records after artifact offset `1129` into `data/reference_db/dex_source_observed_versions` | 81 converted, 19 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `785` | 81 stored, 0 failed |

No-bytecode skips were AndroidX SavedState, SQLite, SQLite Framework, and Tracing wrapper artifacts without JVM bytecode or without produced `classes*.dex`, including `androidx.savedstate:savedstate`, `savedstate-compose`, `savedstate-ktx`, `androidx.sqlite:sqlite`, `androidx.sqlite:sqlite-framework`, and `androidx.tracing:tracing` versions from the source-observed slice.

## Batch 016

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 1300` into `data/reference_db/artifacts_source_observed_versions` | 65 downloaded, 35 failed |
| Convert | downloaded records after artifact offset `1229` into `data/reference_db/dex_source_observed_versions` | 54 converted, 11 skipped, 0 failed |
| Extract | append into `data/reference_db/reference_features_source_observed_versions.sqlite` from conversion offset `866` | 54 stored, 0 failed |

Download failures were real `404 Not Found` results across AndroidX Window, SparkButton Compose, CustomActivityOnCrash, ACRA, Material Dialogs, Lottie, Pin/Pattern lock widgets, Billing, and legacy Android support-library alias rows. Some source-observed rows were not valid Maven versions, such as support aliases like `androidx.appcompat:appcompat:1.7.0` recorded under `com.android.support:appcompat-v7`. No-bytecode skips were `androidx.work:work-runtime-ktx` and Touchlab Stately wrapper artifacts where D8 produced no `classes*.dex`.

## Current Evaluation-Only DB Totals

| Metric | Value |
|---|---:|
| Source-version slots attempted | 1400 |
| Downloaded artifact metadata records | 1294 |
| Download failures recorded | 106 |
| Bytecode-bearing conversion records | 920 |
| No-bytecode conversion skips | 374 |
| Stored DB components | 920 |

Current feature extraction counts:

| Feature table / metric | Rows |
|---|---:|
| Components | 920 |
| DEX files | 920 |
| Packages | 4730 |
| Classes | 186589 |
| Methods | 1107983 |
| Opcodes | 68457 |
| API references | 1366838 |
| String literals | 214703 |
| Dependency shapes | 9412 |
| Class dependencies | 294674 |
| Opcode n-grams | 2171101 |
| Call-chain opcode fingerprints | 188074 |
| Basic-block opcode fingerprints | 905241 |
| Class-neighbor summaries | 38860 |
| Field-operation sequences | 128343 |
| Literal/context features | 353668 |

## Commands

```powershell
python scripts\build_reference_db_coverage_dashboard.py
python scripts\build_source_observed_reference_catalog.py
docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven --config configs/libraries.source_observed_versions.json --output-root data/reference_db/artifacts_source_observed_versions --limit 25 --offset 0 --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex --artifact-root data/reference_db/artifacts_source_observed_versions --output-root data/reference_db/dex_source_observed_versions --limit 25 --offset 0 --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features --dex-root data/reference_db/dex_source_observed_versions --db-path data/reference_db/reference_features_source_observed_versions.sqlite --reset --quiet
```

The download step was executed through the Python downloader after sandboxed network access failed with `WinError 10013`; the approved unsandboxed run downloaded 25/25 artifacts. The artifact, DEX, and SQLite outputs live under ignored `data/reference_db/*` paths.

## Next Batch

Continue source-version downloads with `--limit 100 --offset 1400`. Because failed downloads are absent from the artifact metadata list, compute the conversion offset from the current downloaded metadata count before converting the next slice. Append to `data/reference_db/reference_features_source_observed_versions.sqlite` without `--reset`.
