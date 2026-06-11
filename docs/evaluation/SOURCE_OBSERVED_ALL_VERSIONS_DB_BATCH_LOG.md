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
| Extract | append/targeted extraction into `data/reference_db/reference_features_source_observed_all_versions.sqlite` | heavy icon extraction paused after offset `2327`; repeated/light coordinate-filtered extraction raised DB to `3095` stored components, 0 failed in recent chunks |

The initial `6000`-slot download command timed out but wrote progress. Follow-up `1000`, `500`, and tail chunks continued the same macro-batch through config offset `6100`; the artifact ledger now has `5589` downloaded metadata records. Conversion also hit the tool timeout, so the batch was resumed by computing the first missing converter offset from `sorted(root.rglob("metadata.json"))` rather than using a naive normalized-path sort. This matters because later downloads inserted alphabetically earlier AndroidX rows. The heavy `androidx.compose.material:material-icons-extended`, `material3-android`, `runtime-android`, and `ui-android` regions required smaller chunks; no conversion failures are recorded in the current checkpoint. As of this checkpoint, the downloaded ledger is fully converted/skipped. Targeted extraction uses offsets over converted/existing records, not all conversion metadata records, and offsets are not the same as unique component counts because later chunks can upsert already-stored coordinate-version rows. A live reconciliation found the first missing row at offset `1104`; follow-up chunks at offsets `1104`, `1129`, and `1154` raised the DB to `2510` components. Heavy one-row chunks at offsets `2309`, `2311`, and `2312` stored `androidx.compose.material:material-icons-extended` versions and raised the DB to `2513` components. The next missing row is offset `2313`, `androidx.compose.material:material-icons-extended:1.2.0-alpha07`, so keep using one-row chunks.

Latest heavy-region update: one-row chunks through offset `2327` completed cleanly, but `androidx.compose.material:material-icons-extended` and `material-icons-extended-android` are now deferred as a heavy icon-pack backlog because each row costs several minutes. The value-first extraction policy is to process real-APK repeated and lightweight rows before returning to icon packs. Coordinate-filtered extraction then stored `44` versions for `androidx.compose.runtime:runtime-annotation-android`, `53` versions for `androidx.compose.material3.adaptive:adaptive-android`, `100` versions for `androidx.compose.runtime:runtime-saveable-android`, `100` versions for `androidx.compose.ui:ui-geometry-android`, `27` versions for `androidx.compose.runtime:runtime-retain-android`, `100` bounded versions for `androidx.compose.runtime:runtime-android`, `100` bounded versions for `androidx.compose.ui:ui-android`, and `50` bounded versions for `androidx.compose.material3:material3-android`, raising the DB to `3095` components. The repeated/non-icon missing queue is now exhausted: `0` rows remain after covering `material3-android` `1.3.1` and `1.4.0`.

Current feature extraction counts:

| Feature table / metric | Rows |
|---|---:|
| Components | 3095 |
| DEX files | 3086 |
| Packages | 19210 |
| Classes | 1664168 |
| Methods | 7427881 |
| Opcodes | 287998 |
| API references | 8740677 |
| String literals | 1705334 |
| Dependency shapes | 36703 |
| Class dependencies | 1799310 |
| Opcode n-grams | 11260080 |
| Call-chain opcode fingerprints | 1304920 |
| Basic-block opcode fingerprints | 5336910 |
| Class-neighbor summaries | 196285 |
| Field-operation sequences | 723301 |
| Literal/context features | 3116490 |

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

For the full all-versions lane, continue Macro-Batch 001 with value-first extraction: prioritize lightweight coordinates and thesis-relevant source-observed rows, then return to heavy icon packs later. Current durable ledger: `5589` artifacts and `5589` conversion records (`3285` converted, `755` existing, `1549` skipped), `4040` extractable converted/existing rows, `3095` stored components, and `945` still-missing extractable rows in the already-downloaded macro-batch. The repeated/non-icon queue is exhausted (`0` rows). The heavy icon backlog starts at converted/existing offset `2328`; do not resume it until lightweight rows are exhausted or explicitly needed.
