# Build, Experiment, and Validate Workflows

## Build an isolated reference DB

Choose unique names:

```powershell
$config = "configs/libraries.handbook.json"
$artifacts = "data/reference_db/artifacts_handbook"
$dex = "data/reference_db/dex_handbook"
$db = "data/reference_db/reference_features_handbook.sqlite"
```

Preview downloads:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven `
  --config $config --output-root $artifacts --dry-run
```

Download:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven `
  --config $config --output-root $artifacts --quiet
```

Convert:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex `
  --artifact-root $artifacts --output-root $dex --quiet
```

Extract into the new DB:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features `
  --dex-root $dex --db-path $db --reset --quiet
```

Use `--reset` only because `$db` is a new experiment path.

## Add later batches

Use `--limit` and `--offset` for downloads. Conversion can safely revisit the
cache, and extraction can upsert:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features `
  --dex-root $dex --db-path $db --quiet
```

Do not use `--reset` on later batches.

## Compare a matcher change

Record baseline and candidate commands separately:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli match-apk APP.apk `
  --db-path BASELINE.sqlite --top 30

docker compose run --rm apk-sbom python -m apk_sbom.cli match-apk APP.apk `
  --db-path EXPERIMENT.sqlite --top 30
```

Check more than the intended target:

- at least two targets;
- a clean source-validated control;
- a partial control;
- a no-Maven control;
- a native/hidden/boundary control.

Stop on the first meaningful regression.

## Validate a report against source

Generate the report:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report APP.apk `
  --output-dir data/results/experiment/app `
  --db-path EXPERIMENT.sqlite --skip-osv --top 30
```

Validate:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps `
  --sbom data/results/experiment/app/sbom.cdx.json `
  --dependency-tree data/results/source-validation/app/runtimeClasspath.txt `
  --output-dir data/results/experiment/app/source-validation
```

Compare:

- emitted count;
- confirmed;
- wrong version;
- missing from source;
- intended target rows;
- runtime and candidate volume.

An improvement from 10 to 72 confirmations is not safe if emitted rows expand
from 18 to 111 with false positives.

## Run the final demo path

Use the maintained runbook and final checklist rather than inventing demo
commands at the last minute:

- [Final demo runbook v2](../../evaluation/FINAL_DEMO_RUNBOOK_V2.md)
- [Final demo checklist](../../evaluation/FINAL_DEMO_CHECKLIST.md)
- [Defense presentation guide](../../thesis/DEFENSE_PRESENTATION_GUIDE.md)

## After a successful promotion

Update together:

- generated JSON/CSV/Markdown evidence;
- `TASKS.md`;
- `docs/codex/CODEX_CONTEXT.md`;
- evaluation dashboards;
- thesis tables and claim wording;
- presentation metrics if the authoritative numbers changed.
