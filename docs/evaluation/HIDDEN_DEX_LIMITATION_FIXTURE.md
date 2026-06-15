# Hidden DEX Limitation Fixture

Status: completed synthetic limitation fixture.

## Purpose

This fixture tests whether the MVP reports dynamic-code/protector-style APK packaging cautiously. It is not an accuracy benchmark and must not be used for precision/recall.

## Artifacts

| Artifact | Path / value |
|---|---|
| APK | `data/test_apks/limitation/controlled-hidden-dex-loader-limitation.apk` |
| Metadata | `data/test_apks/limitation/controlled-hidden-dex-loader-limitation.limitation.json` |
| APK SHA-256 | `ff6bd63aa357bfa87e63e0845d5d77918e8b08f727146b1609b87089eb9a082d` |
| Report | `data/results/report-limitation-hidden-dex-loader/report.md` |
| HTML report | `data/results/report-limitation-hidden-dex-loader/report.html` |
| SBOM | `data/results/report-limitation-hidden-dex-loader/sbom.cdx.json` |

## Fixture Contents

| Entry | Purpose |
|---|---|
| `classes.dex` | Tiny primary DEX-like loader stub. |
| `assets/classes2.dex` | DEX-like payload outside the normal top-level `classes*.dex` layout. |
| `assets/protect_payload.dat` | Large opaque asset with protector-style naming. |
| `lib/armeabi-v7a/libshell.so` | Native loader-style file name. |

## MVP Result

| Field | Result |
|---|---:|
| Extraction risk | medium |
| Obfuscation risk | high |
| DEX files analyzed | 0 |
| DEX files failed | 2 |
| Detected Maven components | 0 |
| Native file components | 1 |
| OSV vulnerabilities | 0 |

Forensic indicators raised:

- `nonstandard-dex`
- `tiny-primary-dex`
- `protector-name-hint`
- `large-opaque-assets`

## Interpretation

This is the desired MVP behavior for a dynamic/protected-style boundary case: the tool reports risk indicators, records the native file as hash-only evidence, and avoids claiming recovered Java/Kotlin Maven components from invalid or hidden DEX payloads.

## Reproduction Commands

```powershell
python scripts/build_limitation_apk.py
docker compose run --rm apk-sbom python -m apk_sbom.cli inspect-apk data/test_apks/limitation/controlled-hidden-dex-loader-limitation.apk
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/limitation/controlled-hidden-dex-loader-limitation.apk --output-dir data/results/report-limitation-hidden-dex-loader --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
```
