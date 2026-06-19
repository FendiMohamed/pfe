# Start Here

## The project in one sentence

Given an Android APK without its source code, the project extracts bytecode
evidence, compares it with known Maven library versions, emits a CycloneDX
SBOM, and queries vulnerability databases while preserving uncertainty.

## Why this is difficult

An APK does not contain the original `build.gradle` file. During compilation,
R8 may rename classes, remove unused methods, inline code, merge classes, and
repackage namespaces. Different versions of a library may also have almost
identical bytecode. Native `.so` files and dynamically loaded code create
additional boundaries.

The project therefore solves an evidence-ranking problem, not a simple string
search:

```text
APK
  -> extract DEX and manifest evidence
  -> compare with reference-library fingerprints
  -> rank candidate coordinates and versions
  -> separate identity confidence from version confidence
  -> emit confirmed or explicitly uncertain SBOM evidence
  -> query OSV and label vulnerability certainty
```

## What the MVP produces

A normal full run can produce:

- `report.json`: machine-readable analysis and evidence;
- `report.md`: readable technical report;
- `report.html`: presentation-friendly report;
- `sbom.cdx.json`: CycloneDX 1.5 SBOM;
- vulnerability results from OSV, unless scanning is disabled.

## What the MVP does not promise

- Perfect reconstruction of every source dependency.
- Exact versions when adjacent versions are bytecode-equivalent.
- Identification of arbitrary native libraries from hashes alone.
- Recovery of code downloaded after installation.
- Automatic trust in AI predictions.

## A useful mental model

Think of the project as three connected systems:

1. **Reference construction**: turn known Maven releases into comparable
   fingerprints.
2. **APK matching**: extract the same feature families from an APK and rank
   references.
3. **Evidence and reporting**: translate ranked candidates into cautious SBOM
   and vulnerability claims.

The reference database is a closed-world memory. If a library version is not
in it, exact recovery may be impossible even when the APK contains that
library. This is why reference coverage and matcher quality are measured
separately.

## First practical exercise

After reading the concept guides, follow
[First APK walkthrough](workflows/FIRST_APK_WALKTHROUGH.md). Start with
`inspect-apk`, then `analyze-dex`, then `match-apk`, and only then run the full
report. This lets you see each layer instead of treating the tool as a black
box.

## Presentation-safe summary

> The MVP combines static APK extraction, multi-feature reference matching,
> CycloneDX generation, OSV vulnerability mapping, and source-backed
> evaluation. It is designed to expose uncertainty instead of converting weak
> evidence into false precision.

For exact current numbers and claim boundaries, read
[Datasets, metrics, and results](evaluation/DATASETS_METRICS_AND_RESULTS.md).
