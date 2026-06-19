# Reference Database CLI Reference

The usual sequence is:

```text
expand config -> download -> convert -> extract features
```

Always use isolated paths while experimenting.

## `expand-reference-config`

Resolves a coordinate catalog into a concrete coordinate/version download
configuration.

- `--catalog PATH`: input coordinate catalog.
- `--output PATH`: generated library config.
- `--repository-url URL`: Maven repository base URL.
- `--latest-count N`: latest stable versions per coordinate; default `1`.
- `--all-versions`: select every metadata-published version. Potentially very
  large and slow.
- `--include-prerelease`: allow alpha, beta, RC, milestone, preview, EAP, and
  snapshot releases.
- `--coordinate GROUP:ARTIFACT`: process one coordinate.
- `--limit N`: process at most N coordinates.
- `--timeout SECONDS`: metadata request timeout.
- `--dry-run`: show resolution without writing the config.
- `--summary-output PATH`: full expansion summary JSON.
- `--quiet`: print only the short summary.

Expected output: a deterministic downloader config plus optional resolution
statistics.

## `download-maven`

Downloads artifacts and metadata.

- `--config PATH`: selected libraries and versions.
- `--output-root DIR`: artifact/metadata cache.
- `--repository-url URL`: repository base.
- `--coordinate GROUP:ARTIFACT`: one-coordinate filter.
- `--limit N`: process a bounded batch.
- `--offset N`: skip the first N selected artifacts.
- `--packaging jar|aar`: requested extension.
- `--timeout SECONDS`: timeout per artifact.
- `--force`: redownload existing complete entries.
- `--dry-run`: print URLs and destinations without network writes.
- `--quiet`: status counts instead of full records.

Expected statuses include downloaded, existing, skipped, and failed. HTTP 404
may mean wrong packaging, removed repository content, alias versions, or a
metadata-only module.

## `convert-reference-dex`

Converts cached JAR/AAR bytecode with D8.

- `--artifact-root DIR`: downloaded cache.
- `--output-root DIR`: conversion metadata and DEX destination.
- `--coordinate GROUP:ARTIFACT`: filter.
- `--limit N`, `--offset N`: bounded slicing.
- `--d8-command COMMAND`: D8 executable, default `d8`.
- `--min-api N`: Android minimum API passed to D8, default `21`.
- `--timeout SECONDS`: per-artifact D8 timeout.
- `--force`: repeat completed conversions.
- `--dry-run`: show planned records only.
- `--quiet`: compact status counts.

For AAR files, `classes.jar` is extracted first. No-bytecode artifacts are
honest skips, not necessarily failures.

## `extract-reference-features`

Parses converted DEX and writes SQLite rows.

- `--dex-root DIR`: conversion cache.
- `--db-path PATH`: target SQLite DB.
- `--coordinate GROUP:ARTIFACT`: filter.
- `--limit N`, `--offset N`: bounded slicing.
- `--include-skipped`: include skipped conversions in the summary.
- `--reset`: delete and recreate the target DB before extraction.
- `--quiet`: compact DB and status counts.

### `--reset` warning

`--reset` is destructive to the selected DB. Use it only for a new or explicitly
rebuildable experiment database. Later batches should omit it so existing rows
are preserved and updated.

## Safe batch example

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven `
  --config configs/libraries.example.json `
  --output-root data/reference_db/artifacts_example `
  --limit 20 --offset 0 --quiet

docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex `
  --artifact-root data/reference_db/artifacts_example `
  --output-root data/reference_db/dex_example --quiet

docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features `
  --dex-root data/reference_db/dex_example `
  --db-path data/reference_db/reference_features_example.sqlite `
  --reset --quiet
```

For the next download batch, increase `--offset`; rerun conversion over the
cache and feature extraction without `--reset`.
