# Simplify Obfuscated APK Limitation Sample

This artifact adds a legal public obfuscated APK sample to the limitation layer.
It is not a source-validated accuracy case and must not be used in precision,
recall, or version-confirmation metrics.

## Source

- APK: `data/test_apks/limitation/simplify-obfuscated-app/simplify-obfuscated-app.apk`
- Source URL: `https://raw.githubusercontent.com/CalebFenton/simplify/master/simplify/obfuscated-app.apk`
- SHA-256: `a8d5d044fb78c5b3c01d53c659e3dac09149442c58c8c34f8d0be798240016d1`
- Package: `org.cf.obfuscated`
- Version: `1.0` / `1`
- Layer: limitation

The sample comes from the public Simplify deobfuscator repository. It is useful
because it is an obfuscated APK sample with a normal APK/DEX layout, giving a
different limitation shape than the synthetic hidden-DEX fixture.

## Report Artifacts

- Report folder: `data/results/report-limitation-simplify-obfuscated-app/`
- JSON report: `data/results/report-limitation-simplify-obfuscated-app/report.json`
- Markdown report: `data/results/report-limitation-simplify-obfuscated-app/report.md`
- HTML report: `data/results/report-limitation-simplify-obfuscated-app/report.html`
- CycloneDX SBOM: `data/results/report-limitation-simplify-obfuscated-app/sbom.cdx.json`

Generated command:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report `
  data/test_apks/limitation/simplify-obfuscated-app/simplify-obfuscated-app.apk `
  --output-dir data/results/report-limitation-simplify-obfuscated-app `
  --db-path data/reference_db/reference_features_calibrated_combined.sqlite `
  --top 30 `
  --skip-osv
```

## Observed Behavior

| Field | Result |
|---|---|
| Standard DEX files | `classes.dex` |
| Nonstandard DEX files | none |
| Native `.so` files | 0 |
| Extraction risk | low |
| Obfuscation risk | medium, score `0.4` |
| Main risk reasons | low-confidence candidate ratio; structural evidence stronger than package-name evidence |
| Class/method coverage diagnostic | warning |
| Emitted Maven components | 3 candidate/likely components |
| OSV | skipped for this local limitation check |

The report emits three Maven library candidates:

| Coordinate | Version | Identity / version status |
|---|---:|---|
| `androidx.appcompat:appcompat` | `1.7.1` | likely / candidate |
| `androidx.core:core` | `1.9.0` | candidate / candidate |
| `androidx.lifecycle:lifecycle-runtime` | `2.6.2` | candidate / candidate |

## Interpretation

This APK is different from the hidden-DEX fixture:

- It does not trigger packed/dynamic-code forensic indicators.
- It does trigger report-level obfuscation uncertainty through matcher evidence:
  large class/method coverage gaps, low-confidence candidate ratio, and
  structural-over-package scoring.
- The emitted Maven rows are candidates, not source-confirmed dependencies.

The correct thesis use is limitation evidence: the MVP can still produce an SBOM
candidate view, but without source/dependency-tree validation these rows must
remain outside accuracy metrics and CVE-confirmation claims.

## Policy

Do not promote this sample into source-validated metrics. Use it to discuss
obfuscated-sample behavior and the difference between:

- hidden/dynamic-code packaging, where the tool should warn and avoid Java/Kotlin
  recovery claims; and
- normal-layout obfuscated APKs, where the tool may emit low-confidence candidate
  Maven evidence but must label it honestly.
