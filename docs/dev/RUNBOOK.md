# Developer Runbook

## Current Status

The MVP scope is frozen. The first implementation slice is available:

```text
APK -> archive inspection summary JSON -> minimal DEX feature summary JSON
```

It detects:

- all `classes*.dex` files
- multidex status
- `AndroidManifest.xml`
- `resources.arsc`
- native libraries under `lib/<abi>/*.so`
- SHA-256 hashes
- DEX classes, methods, packages, and opcode histogram when Androguard is available

## Host Commands

Run CLI help:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli --help
```

Inspect an APK:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli inspect-apk data\test_apks\sample.apk
```

Analyze DEX features:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli analyze-dex data\test_apks\sample.apk
```

Run syntax check:

```powershell
python -m compileall src scripts tests
```

Load the initial Maven library config:

```powershell
$env:PYTHONPATH='src'
python -c "from apk_sbom.reference_config import load_libraries_config; print([lib.coordinate for lib in load_libraries_config('configs/libraries.json')])"
```

Run toolchain audit:

```powershell
python scripts/check_toolchain.py
```

The host audit currently fails because required Python packages are not installed on Windows. This is expected until the Docker runtime is built.

## Docker Commands

Validate Compose syntax:

```powershell
docker compose config
```

After Docker Desktop is running:

```powershell
docker info
docker compose build
docker compose run --rm apk-sbom python scripts/check_toolchain.py
docker compose run --rm apk-sbom python -m apk_sbom.cli analyze-dex data/test_apks/sample.apk
```

## Next Implementation Step

After minimal DEX feature extraction works, implement:

```text
first minimal CycloneDX SBOM from mocked detection results
```

Expected first DEX feature output:

```json
{
  "dex_files_analyzed": 2,
  "classes_count": 1234,
  "methods_count": 9876,
  "packages": ["okhttp3", "retrofit2", "com.google.gson"]
}
```
