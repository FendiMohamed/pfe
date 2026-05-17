# MVP Implementation Plan

## Guiding Principle

Build end-to-end first, then improve accuracy.

The first success is not perfect detection. The first success is:

```text
one APK
-> one detected known Maven library
-> one version decision
-> one CycloneDX SBOM
-> one vulnerability lookup result
```

## Milestone 1: Skeleton And Extraction

Deliverables:

- CLI entrypoint.
- APK raw extractor.
- DEX file discovery including multidex.
- Metadata extraction placeholders.
- Output analysis folder under `data/results/`.

Verification:

- Run against a sample APK.
- Confirm all `classes*.dex` files and native files are listed.

## Milestone 2: Reference DB

Deliverables:

- Library list file with selected Maven coordinates.
- Downloader for selected versions.
- Reference metadata schema.
- SQLite DB creation.

Initial library candidates:

```text
com.squareup.okhttp3:okhttp
com.squareup.okio:okio
com.squareup.retrofit2:retrofit
com.google.code.gson:gson
commons-codec:commons-codec
com.fasterxml.jackson.core:jackson-databind
```

Verification:

- Download at least 3 versions of one library.
- Store PURL and version metadata.

## Milestone 3: DEX Feature Extraction

Deliverables:

- Extract classes, packages, methods, method descriptors.
- Extract opcode sequences or opcode histograms.
- Extract API calls/references if available.
- Store APK and reference features.

Verification:

- Compare feature counts between an APK and one reference version.

## Milestone 4: Basic Matching

Deliverables:

- Candidate generation using package/class/method overlap.
- First version ranking.
- Confidence output.

Verification:

- Controlled test APK with known dependency is identified.

## Milestone 5: Hybrid Matching

Deliverables:

- Opcode similarity score.
- Class dependency graph construction.
- Graph/class structural score.
- Weighted final version score.

Verification:

- Show top 3 versions with evidence and score breakdown.

## Milestone 6: SBOM And Vulnerability

Deliverables:

- CycloneDX JSON output.
- PURL generation.
- OSV vulnerability query.
- Optional Trivy/Grype scan.
- Final report.

Verification:

- Generated SBOM is valid or scanner-readable.
- Vulnerability lookup works for at least one known vulnerable library version.

## Milestone 7: Evaluation

Deliverables:

- Controlled APK dataset with ground truth.
- Clear and obfuscated variants.
- Metrics table.
- Limitations and failure analysis.

Metrics:

- library-level precision, recall, F1
- version-level precision, recall, F1
- exact/range/uncertain rate
- runtime per APK
- SBOM completeness
- vulnerability lookup correctness

