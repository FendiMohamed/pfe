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

## Current Evaluation-Only DB Totals

| Metric | Value |
|---|---:|
| Source-version slots attempted | 300 |
| Downloaded artifact metadata records | 285 |
| Download failures recorded | 15 |
| Converted bytecode artifacts | 183 |
| No-bytecode conversion skips | 102 |
| Stored DB components | 183 |

Current feature extraction counts:

| Feature table / metric | Rows |
|---|---:|
| Components | 183 |
| DEX files | 183 |
| Packages | 1229 |
| Classes | 88993 |
| Methods | 452319 |
| Opcodes | 17154 |
| API references | 528838 |
| String literals | 83226 |
| Dependency shapes | 2228 |
| Class dependencies | 121597 |
| Opcode n-grams | 701262 |
| Call-chain opcode fingerprints | 72932 |
| Basic-block opcode fingerprints | 333054 |
| Class-neighbor summaries | 12579 |
| Field-operation sequences | 45185 |
| Literal/context features | 132222 |

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

Continue source-version downloads with `--limit 100 --offset 300`. Because failed downloads are absent from the artifact metadata list, compute the conversion offset from the current downloaded metadata count before converting the next slice. Append to `data/reference_db/reference_features_source_observed_versions.sqlite` without `--reset`.
