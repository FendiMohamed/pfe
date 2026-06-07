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

Continue with `--limit 25 --offset 25` for download and conversion. Append to `data/reference_db/reference_features_source_observed_versions.sqlite` without `--reset` after the first extraction.
