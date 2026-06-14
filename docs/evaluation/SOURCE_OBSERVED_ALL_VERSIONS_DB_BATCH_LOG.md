# Source-Observed All-Versions Reference DB Batch Log

This log records evaluation-only reference DB growth from every metadata-published version available for the TPL coordinates observed in source-validated APK dependency trees. It does not change the shared calibrated DB, matcher scoring, SBOM output, vulnerability labels, or source-validation metrics.

## Inputs

| Input | Value |
|---|---|
| Source-observed coordinate catalog | `configs/source_observed_reference_catalog.json` |
| All-versions build config | `configs/libraries.source_observed_all_versions.json` |
| Expansion retry catalog | `configs/source_observed_all_versions_failed_retry_catalog.json` |
| Artifact root | `data/reference_db/artifacts_source_observed_all_versions` |
| DEX root | `data/reference_db/dex_source_observed_all_versions` |
| Evaluation DB | `data/reference_db/reference_features_source_observed_all_versions.sqlite` |

## Expansion

| Metric | Value |
|---|---:|
| Source-observed buildable coordinates | 1361 |
| Coordinates resolved by first expansion | 1212 |
| Coordinates failed by first expansion | 149 |
| Coordinates recovered by longer-timeout retry | 2 |
| Final resolved coordinates | 1214 |
| Final all-version coordinate-version slots | 60979 |

The first expansion used `expand-reference-config --all-versions --include-prerelease` against the source-observed coordinate catalog and produced `60747` version slots. A retry catalog was built from the `149` failed metadata rows; the longer-timeout retry recovered `2` more coordinates. The merged config now contains `60979` coordinate-version slots.

## Batch 000

| Step | Command scope | Result |
|---|---|---|
| Download | `--limit 100 --offset 0` into `data/reference_db/artifacts_source_observed_all_versions` | 100 downloaded, 0 failed |
| Convert | `--limit 100 --offset 0` into `data/reference_db/dex_source_observed_all_versions` | 100 converted, 0 skipped, 0 failed |
| Extract | `--reset` into `data/reference_db/reference_features_source_observed_all_versions.sqlite` | 100 stored, 0 failed |

Current feature extraction counts:

| Feature table / metric | Rows |
|---|---:|
| Components | 100 |
| DEX files | 100 |
| Packages | 388 |
| Classes | 6704 |
| Methods | 31961 |
| Opcodes | 5804 |
| API references | 44934 |
| String literals | 6353 |
| Dependency shapes | 1312 |
| Class dependencies | 12573 |
| Opcode n-grams | 76442 |
| Call-chain opcode fingerprints | 7577 |
| Basic-block opcode fingerprints | 26235 |
| Class-neighbor summaries | 2780 |
| Field-operation sequences | 5379 |
| Literal/context features | 14340 |

## Next Batch

Continue all-versions downloads with `--limit 100 --offset 100`, then convert from artifact offset `100` and append extraction without `--reset`.

## Macro-Batch 001

| Step | Command scope | Result |
|---|---|---|
| Download | target `--limit 6000 --offset 100`, resumed in smaller chunks after tool timeouts | downloads covered through config offset `6100`; `5589` artifact metadata records present so far |
| Convert | backfilled missing conversion ranges after download ordering changed | `5589` conversion records present; downloaded ledger fully converted/skipped (`3285` converted, `755` existing, `1549` skipped) |
| Extract | append/targeted extraction into `data/reference_db/reference_features_source_observed_all_versions.sqlite` | all non-icon extractable rows in the downloaded macro-batch are stored; DB raised to `3966` stored components, 0 failed in recent chunks |

The initial `6000`-slot download command timed out but wrote progress. Follow-up `1000`, `500`, and tail chunks continued the same macro-batch through config offset `6100`; the artifact ledger now has `5589` downloaded metadata records. Conversion also hit the tool timeout, so the batch was resumed by computing the first missing converter offset from `sorted(root.rglob("metadata.json"))` rather than using a naive normalized-path sort. This matters because later downloads inserted alphabetically earlier AndroidX rows. The heavy `androidx.compose.material:material-icons-extended`, `material3-android`, `runtime-android`, and `ui-android` regions required smaller chunks; no conversion failures are recorded in the current checkpoint. As of this checkpoint, the downloaded ledger is fully converted/skipped. Targeted extraction uses offsets over converted/existing records, not all conversion metadata records, and offsets are not the same as unique component counts because later chunks can upsert already-stored coordinate-version rows. A live reconciliation found the first missing row at offset `1104`; follow-up chunks at offsets `1104`, `1129`, and `1154` raised the DB to `2510` components. Heavy one-row chunks at offsets `2309`, `2311`, and `2312` stored `androidx.compose.material:material-icons-extended` versions and raised the DB to `2513` components. The next missing row is offset `2313`, `androidx.compose.material:material-icons-extended:1.2.0-alpha07`, so keep using one-row chunks.

Latest heavy-region update: one-row chunks through offset `2327` completed cleanly, but `androidx.compose.material:material-icons-extended` and `material-icons-extended-android` were deferred as a heavy icon-pack backlog because each row costs several minutes. The value-first extraction policy processed real-APK repeated rows first, then source-observed non-icon rows, then lightweight and medium non-icon all-version rows. Coordinate-filtered extraction now covers every non-icon extractable row in the downloaded macro-batch, including the Compose runtime/material3/ui tails (`runtime-livedata`, `adaptive-navigation-android`, `adaptive-layout-android`, `runtime-saveable-android`, `ui-geometry-android`, `runtime-android`, `ui-android`, `material3-android`, `material3:1.1.2`, `runtime-saveable`, `ui-geometry`, `ui-graphics`, `ui-graphics-android`, `material3`, and `runtime`). This raised the DB to `3966` components. Remaining extractable rows are heavy icon-pack only: `55` `androidx.compose.material:material-icons-extended-android` rows and `19` `androidx.compose.material:material-icons-extended` rows. The only source-observed rows still missing are `2` deferred `material-icons-extended-android` versions (`1.7.8`, `1.6.8`) at roughly `29.5 MB` DEX each.

Current feature extraction counts:

| Feature table / metric | Rows |
|---|---:|
| Components | 3966 |
| DEX files | 3957 |
| Packages | 25109 |
| Classes | 1975652 |
| Methods | 9602026 |
| Opcodes | 366894 |
| API references | 11402599 |
| String literals | 2096354 |
| Dependency shapes | 45468 |
| Class dependencies | 2332113 |
| Opcode n-grams | 14642158 |
| Call-chain opcode fingerprints | 1617566 |
| Basic-block opcode fingerprints | 6884798 |
| Class-neighbor summaries | 253347 |
| Field-operation sequences | 930850 |
| Literal/context features | 3903932 |

## Deadline Pivot

The first all-versions macro-batch demonstrated that broad expansion is technically possible but too slow for the thesis deadline. The first `6100` config slots required many small conversion/extraction chunks, and the Compose `material-icons-extended` families alone can consume more than ten minutes per extraction row.

The deadline-safe lane is now the real-APK priority catalog generated by `scripts/build_real_apk_priority_reference_catalog.py`:

- Config: `configs/libraries.real_apk_priority_versions.json`
- Evidence doc: `docs/evaluation/REAL_APK_PRIORITY_REFERENCE_CATALOG.md`
- Evidence JSON: `data/results/evaluation/real-apk-priority-reference-catalog.json`
- Scope: `3241` exact coordinate-version slots across `1339` coordinates from runtime dependency-tree evidence
- Tier 1: `1132` repeated coordinate-version slots observed in at least two APK source-validation trees
- Tier 2: `2109` single-observed coordinate-version slots

This is not a replacement for the full `60979`-slot transparency lane. It is the deadline-prioritized evaluation DB lane for versions that actually appear in the real APK corpus.

## Resume Point

For the full all-versions lane, Macro-Batch 001 has completed every non-icon extractable row in the already-downloaded ledger. Current durable ledger: `5589` artifacts and `5589` conversion records (`3285` converted, `755` existing, `1549` skipped), `4040` extractable converted/existing rows, `3966` stored components, and `74` still-missing extractable rows in the already-downloaded macro-batch. The remaining rows are only the deferred heavy icon backlog: `55` `androidx.compose.material:material-icons-extended-android` rows and `19` `androidx.compose.material:material-icons-extended` rows. The only source-observed missing rows are `2` deferred `material-icons-extended-android` versions (`1.7.8`, `1.6.8`). Continue here only if the deadline can absorb very slow icon-pack extraction, otherwise move to the next 6000-slot download macro-batch or priority DB evaluation reruns.

## Macro-Batch 002

| Step | Command scope | Result |
|---|---|---|
| Download | target `--limit 6000 --offset 6100` into `data/reference_db/artifacts_source_observed_all_versions` | tool timed out after writing progress, but latest metadata maps to flattened config offset `12099`; artifact ledger now has `10657` metadata records |
| Convert | chunks from sorted artifact offsets `5588`, `6588`, `7588`, `8588`, and `9588` | downloaded ledger fully converted/skipped; `10657` conversion records (`7756` converted, `756` existing, `2145` skipped), 0 conversion failures in the recent chunks |
| Extract | coordinate-filtered append into `data/reference_db/reference_features_source_observed_all_versions.sqlite` | light/high-return extraction slices stored `495` `androidx.databinding:viewbinding`, `2` `androidx.hilt:hilt-common`, `10` `androidx.lifecycle:lifecycle-common-java8`, `4` `androidx.core:core-viewtree`, `21` `androidx.fragment:fragment-compose`, `10` `androidx.hilt:hilt-lifecycle-viewmodel`, `8` `androidx.glance:glance-preview`, `6` `androidx.legacy:legacy-support-core-utils`, `6` `androidx.interpolator:interpolator`, `129` `androidx.fragment:fragment-ktx`, `37` `androidx.emoji2:emoji2-bundled`, `13` `androidx.glance:glance-material3`, `21` `androidx.hilt:hilt-work`, `401` `androidx.databinding:databinding-ktx`, `89` `androidx.compose.ui:ui-util`, `39` `androidx.emoji2:emoji2-views`, `22` `androidx.hilt:hilt-navigation-compose`, `8` `androidx.customview:customview-poolingcontainer`, `7` `androidx.hilt:hilt-lifecycle-viewmodel-compose`, `117` `androidx.compose.ui:ui-util-android`, `65` `androidx.compose.ui:ui-tooling-preview`, `117` `androidx.compose.ui:ui-tooling-preview-android`, `6` `androidx.legacy:legacy-support-core-ui`, `6` `androidx.cursoradapter:cursoradapter`, `11` `androidx.documentfile:documentfile`, `15` `androidx.datastore:datastore-preferences`, and `32` `androidx.datastore:datastore-preferences-android` rows; DB now has `5663` stored components |

Macro-Batch 002 download covered the next `6000` config slots (`6100` through `12099`), so the next download resume point is flattened config offset `12100`. Conversion is complete for all currently downloaded artifacts: `0` metadata records are missing conversion output. Feature extraction started with high-count/lightweight coordinates. Across all downloaded batches, there were `8512` extractable converted/existing rows, `5663` stored DB components, and `2849` extractable rows still missing before the targeted missing-row extractor.

## Targeted Missing-Row Extraction

`scripts/extract_missing_source_observed_all_versions.py` consumes `data/results/evaluation/source-observed-all-versions-missing-extraction-rows.json`, skips rows already present in the DB, and processes the remaining conversion records by DEX-size tier.

| Step | Command scope | Result |
|---|---|---|
| Build missing-row queue | compare all conversion records with `reference_features_source_observed_all_versions.sqlite` | `8512` extractable conversion rows, `5663` initially stored rows, `2849` missing rows across `47` coordinates |
| Smoke non-icon extraction | `androidx.graphics:graphics-shapes` | `3` stored, 0 failed |
| Small DEX tier | sorted rows up to `100000` DEX bytes | `1709` stored, 0 failed |
| Medium DEX tier | sorted rows up to `250000` DEX bytes | `365` stored, 0 failed |
| Larger DEX tier | sorted rows up to `500000` DEX bytes | `204` stored, 0 failed |
| Large non-icon tier | sorted rows up to `1000000` DEX bytes | `428` stored, 0 failed |
| Final non-icon tier | sorted rows up to `2000000` DEX bytes | `66` stored, 0 failed |
| Heavy icon-pack probe | one `androidx.compose.material:material-icons-extended` row | `1` stored in about 14 minutes, 0 failed |
| Heavy icon-pack continuation | next two `androidx.compose.material:material-icons-extended` rows | `2` stored in about 12 minutes, 0 failed |
| Heavy icon-pack continuation 2 | next two `androidx.compose.material:material-icons-extended` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy icon-pack continuation 3 | next two `androidx.compose.material:material-icons-extended` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy icon-pack continuation 4 | next two `androidx.compose.material:material-icons-extended` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy icon-pack continuation 5 | next two `androidx.compose.material:material-icons-extended` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy icon-pack continuation 6 | next two `androidx.compose.material:material-icons-extended` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy icon-pack continuation 7 | next two `androidx.compose.material:material-icons-extended` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy icon-pack continuation 8 | next two `androidx.compose.material:material-icons-extended` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy icon-pack continuation 9 | final two `androidx.compose.material:material-icons-extended` rows | `2` stored in about 8 minutes, 0 failed |
| Heavy Android icon-pack continuation 1 | first two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 14 minutes, 0 failed |
| Heavy Android icon-pack continuation 2 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 13 minutes, 0 failed |
| Heavy Android icon-pack continuation 3 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 13 minutes, 0 failed |
| Heavy Android icon-pack continuation 4 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 13 minutes, 0 failed |
| Heavy Android icon-pack continuation 5 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 13 minutes, 0 failed |
| Heavy Android icon-pack continuation 6 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 14 minutes, 0 failed |
| Heavy Android icon-pack continuation 7 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 12 minutes, 0 failed |
| Heavy Android icon-pack continuation 8 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy Android icon-pack continuation 9 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 10 minutes, 0 failed |
| Heavy Android icon-pack continuation 10 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy Android icon-pack continuation 11 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 9 minutes, 0 failed |
| Heavy Android icon-pack continuation 12 | next two `androidx.compose.material:material-icons-extended-android` rows | `2` stored in about 13 minutes, 0 failed |

Current all-versions DB state:

- Stored components: `8481`
- Unique coordinates: `129`
- Extractable rows still not stored: `31`
- Remaining coordinates: only `androidx.compose.material:material-icons-extended-android` (`31` rows)
- Remaining DEX volume: about `0.85` GiB

The regular `androidx.compose.material:material-icons-extended` coordinate is complete. The remaining rows are the heavy Material Icons Extended Android tail. They are valid extractable bytecode rows, but Android chunks are taking about 9-14 minutes per two rows and the combined DB rebuild now needs a longer timeout, so finishing the last `31` rows remains a many-hour extraction tail and should not block the large combined DB/reporting experiment.
