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
| Convert | backfilled missing conversion ranges after download ordering changed | `4500` conversion records present; `1089` downloaded artifacts still awaiting conversion |
| Extract | append/targeted extraction into `data/reference_db/reference_features_source_observed_all_versions.sqlite` | 1230 stored components, 0 failed |

The initial `6000`-slot download command timed out but wrote progress. Follow-up `1000`, `500`, and tail chunks continued the same macro-batch through config offset `6100`; the artifact ledger now has `5589` downloaded metadata records. Conversion also hit the tool timeout, so the batch was resumed by computing the first missing converter offset from `sorted(root.rglob("metadata.json"))` rather than using a naive normalized-path sort. This matters because later downloads inserted alphabetically earlier AndroidX rows. The heavy `androidx.compose.material:material-icons-extended`, `material3-android`, and `runtime-android` regions required smaller chunks; no conversion failures are recorded in the current checkpoint. As of this checkpoint, conversion is complete through artifact offset `4499`; the next missing offset is `4500` in `androidx.compose.runtime:runtime-saveable`.

Current feature extraction counts:

| Feature table / metric | Rows |
|---|---:|
| Components | 1230 |
| DEX files | 1230 |
| Packages | 6675 |
| Classes | 213926 |
| Methods | 1268979 |
| Opcodes | 97640 |
| API references | 1697200 |
| String literals | 302045 |
| Dependency shapes | 14426 |
| Class dependencies | 417157 |
| Opcode n-grams | 2550977 |
| Call-chain opcode fingerprints | 239304 |
| Basic-block opcode fingerprints | 1008277 |
| Class-neighbor summaries | 65183 |
| Field-operation sequences | 171319 |
| Literal/context features | 478135 |

## Resume Point

Continue Macro-Batch 001 conversion from artifact offset `4500`, then run targeted extraction for the newly converted bytecode-bearing rows. Current ledger: `5589` artifacts, `4500` conversion records, `1089` downloaded artifacts still awaiting conversion, and `1230` stored DB components.
