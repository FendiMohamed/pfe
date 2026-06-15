# Low-Risk Version-Band Annotated Reports

This check validates the opt-in `generate-report --include-version-band-experiments`
surface on the four low-risk real APK proof cases.

The purpose is narrow: attach saved AppCompat/Core and Lifecycle version-band
diagnostics to the report artifacts without changing matcher output, selected
versions, SBOM component selection, vulnerability labels, source-validation
metrics, or the shared calibrated reference DB.

## Command Pattern

Each report was regenerated with the calibrated shared DB and OSV disabled to
keep the check local and focused on report annotation behavior:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report `
  data/test_apks/real/<app>/<app>.apk `
  --output-dir data/results/evaluation/low-risk-real-apk-batch/report-real-<app>-version-band-annotated `
  --db-path data/reference_db/reference_features_calibrated_combined.sqlite `
  --top 30 `
  --skip-osv `
  --include-version-band-experiments
```

## Artifact Summary

| APK | Annotated report folder | Detected components unchanged | CycloneDX components unchanged | Matching old-version downgrade rows | Matching Lifecycle downgrade rows |
|---|---|---:|---:|---:|---:|
| Stopwatch | `data/results/evaluation/low-risk-real-apk-batch/report-real-stopwatch-version-band-annotated/` | yes, 5/5 | yes, 5/5 | 1 | 0 |
| Bubble | `data/results/evaluation/low-risk-real-apk-batch/report-real-bubble-version-band-annotated/` | yes, 7/7 | yes, 7/7 | 0 | 0 |
| Audio Source | `data/results/evaluation/low-risk-real-apk-batch/report-real-audio-source-version-band-annotated/` | yes, 3/3 | yes, 3/3 | 0 | 0 |
| Blue Square Speedometer | `data/results/evaluation/low-risk-real-apk-batch/report-real-blue-square-speedometer-version-band-annotated/` | yes, 0/0 | yes, 0/0 | 0 | 0 |

## Interpretation

- The opt-in annotation surface works on the real low-risk reports.
- Stopwatch receives one matching AppCompat old-version diagnostic downgrade row.
- Audio Source and Blue Square Speedometer match diagnostic rows, but not rows
  that trigger a downgrade under the saved experiment policy.
- Blue Square Speedometer remains a no-Maven-signal control with 0 emitted Maven
  components.
- The annotated reports include JSON, Markdown, HTML, and CycloneDX application
  metadata evidence.
- The baseline report components and SBOM components are unchanged for all four
  APKs.

## Policy

These artifacts are report-only evidence. They should not be counted as improved
source-validation metrics and should not be used to promote reference versions or
matcher scoring rules without a separate current-control matrix.
