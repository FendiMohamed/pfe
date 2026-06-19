# Setup and Environment

## Recommended path: Docker

Docker is the most reproducible environment because the image includes:

- Python 3.12 and project dependencies;
- Android command-line tools and D8;
- Android build tools 36.0.0 and legacy 29.0.3;
- Gradle 9.5 plus compatibility versions;
- Java and a separate Java 11 runtime;
- Syft, Grype, Trivy, CycloneDX CLI, and cdxgen.

Build and verify:

```powershell
docker compose build
docker compose run --rm apk-sbom python scripts/check_toolchain.py
docker compose run --rm apk-sbom python -m apk_sbom.cli --help
```

The repository is mounted at `/app`, so generated files written inside the
container appear in the Windows workspace.

## Host Python path

The project requires Python 3.12 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
$env:PYTHONPATH = "src"
python -m apk_sbom.cli --help
```

For the RandomForest work:

```powershell
python -m pip install -e ".[ml]"
```

For Transformer experiments:

```powershell
python -m pip install -e ".[dl]"
```

Host execution also needs D8/Android tools for reference conversion and a
working Java/Gradle setup for controlled APK builds. Docker avoids most of
those host-specific problems.

## Run tests

```powershell
docker compose run --rm apk-sbom pytest -q
```

or:

```powershell
pytest -q
```

## Command forms

All examples use the module form:

```powershell
python -m apk_sbom.cli COMMAND ...
```

After an editable installation, this is equivalent to:

```powershell
apk-sbom COMMAND ...
```

Docker prefix:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli COMMAND ...
```

## Network expectations

Network is required for:

- Maven metadata and artifact downloads;
- OSV scanning and advisory enrichment;
- first Docker image/tool downloads;
- some Gradle source builds.

Use `--dry-run`, `--skip-osv`, or `--no-enrich` where appropriate.

## Storage expectations

Reference artifacts, converted DEX, SQLite DBs, APKs, and reports can consume
substantial space. Keep generated reference data under `data/reference_db/`
and reports under `data/results/`. Do not delete Docker or DB artifacts merely
because they are large; first verify whether they support current evidence.

## Existing detailed runbook

This handbook explains the system. The operational command history remains in
[Developer Runbook](../../dev/RUNBOOK.md).
