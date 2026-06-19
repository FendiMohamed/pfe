# Core CLI Reference

Use `python -m apk_sbom.cli COMMAND --help` for parser-authoritative defaults.
The explanations below describe what to expect and when a flag changes the
meaning of the result.

## `inspect-apk APK_PATH`

Reads archive and manifest evidence and prints JSON.

- `APK_PATH`: APK to inspect.

Expected output: hashes, DEX paths, native libraries, manifest metadata, and
forensic indicators. No library matching occurs.

## `analyze-dex APK_PATH`

Parses every discovered DEX and prints feature counts and summaries.

- `APK_PATH`: APK to analyze.

Expected output: packages, classes, methods, opcodes, dependencies, literals,
API references, multidex information, and parse errors.

## `generate-mock-sbom APK_PATH`

Generates a minimal CycloneDX example from a mocked detection. This validates
formatting only; it is not an APK detection result.

- `--output PATH`: destination, default
  `data/results/mock-sbom.cdx.json`.

## `match-apk APK_PATH`

Ranks reference candidates without building a full report.

### Candidate-selection flags

- `--db-path PATH`: SQLite reference DB.
- `--coordinate GROUP:ARTIFACT`: diagnose only one coordinate. This supplies
  identity externally and is not normal unconstrained detection.
- `--top N`: maximum ranked candidates returned.
- `--min-score FLOAT`: discard candidates below this score.

### Weight flags

- `--package-weight`: package coverage.
- `--class-weight`: class coverage.
- `--method-weight`: method coverage.
- `--opcode-weight`: opcode histogram cosine similarity.
- `--dependency-weight`: class-dependency similarity.
- `--literal-weight`: string-literal overlap.
- `--unique-version-weight`: version-unique class/method/literal evidence.
- `--api-reference-weight`: invoked API/member overlap; default is zero.
- `--opcode-ngram-weight`: opcode tri-gram similarity; default is zero.

Changing weights creates an experiment. Record the complete command and compare
targets and controls before treating the result as an improvement.

### Guard flags

- `--enable-version-unique-literal-context-reranker`: enabled by default;
  compatibility flag.
- `--disable-version-unique-literal-context-reranker`: reproduce the
  pre-promotion baseline.
- `--enable-composite-family-shortlist`: enabled by default.
- `--enable-composite-family-shortlist-experiment`: compatibility alias.
- `--disable-composite-family-shortlist`: reproduce the earlier baseline.
- `--composite-family-shortlist-margin FLOAT`: score window used by the family
  shortlist. Larger windows retain more sibling candidates.

Expected output: candidate scores, component-level feature evidence, and
identity/version decisions.

## `generate-sbom APK_PATH`

Runs real matching and writes CycloneDX.

- `--output PATH`: SBOM destination.
- `--db-path`, `--coordinate`, `--top`, `--min-score`: same meaning as matching.
- `--include-uncertain`: emit uncertain decisions too. Use only when the
  consumer understands that these are not exact confirmed components.
- reranker and family-shortlist flags: same as `match-apk`.

## `scan-sbom-osv SBOM_PATH`

Queries OSV for Maven components.

- `--output PATH`: vulnerability JSON destination.
- `--api-url URL`: override OSV `querybatch`; normally leave unchanged.
- `--timeout SECONDS`: HTTP timeout.
- `--no-enrich`: do not retrieve each advisory's details. Faster, fewer calls,
  less alias/summary/severity context.

Expected output: per-component advisories, deduplicated identifiers, severity,
and confirmed/potential labels.

## `generate-report APK_PATH`

Runs the normal end-to-end pipeline.

### Core flags

- `--output-dir DIR`: report artifact directory.
- `--db-path PATH`: reference DB.
- `--coordinate`, `--top`, `--min-score`: matcher controls.
- `--api-reference-weight`, `--opcode-ngram-weight`: optional matcher signals.
- `--include-uncertain`: include uncertain components.
- reranker and family-shortlist flags: same as `match-apk`.

### Experimental reference prefilter

- `--enable-reference-package-prefilter`: score only reference components that
  share enough packages with the APK. Experiment-only.
- `--reference-package-prefilter-min-overlap N`: required shared package count.
- `--reference-package-prefilter-limit N`: global maximum candidates.
- `--reference-package-prefilter-per-coordinate-limit N`: maximum retained
  versions per coordinate before the global limit.

These flags may improve runtime but can remove true candidates or inflate
package-family false positives. They do not define the stable default.

### OSV flags

- `--skip-osv`: fully offline matcher/SBOM report.
- `--osv-api-url URL`: OSV endpoint.
- `--timeout SECONDS`: OSV timeout.
- `--no-enrich`: skip per-advisory detail calls.
- `--source-validation-json PATH`: attach existing validation and relabel
  findings as source-confirmed, mismatch, missing, or not validated.

### Report-only attachment flags

- `--include-r8-phase5-experiment` and
  `--r8-phase5-experiment-json`.
- `--include-version-band-experiments`,
  `--version-band-experiment-json`, and
  `--lifecycle-family-experiment-json`.
- `--include-r8-minified-confidence-policy` and
  `--r8-minified-confidence-policy-json`.
- `--include-ai-r8-suggestions` and `--ai-r8-suggestions-json`.
- `--include-hybrid-ai-assistance`, `--hybrid-matcher-router-json`,
  `--ai-r8-dl-metrics-json`, and
  `--r8-apk-structural-promotion-gate-json`.

All of these add explanatory sections. They must not change selected versions,
the SBOM, CVE labels, or source-validation metrics.

Expected files include `matches.json`, `sbom.cdx.json`, `report.json`,
`report.md`, and `report.html`.

## `validate-source-deps`

Compares emitted Maven SBOM rows with a Gradle dependency tree.

- `--sbom PATH`: required CycloneDX JSON.
- `--dependency-tree PATH`: required Gradle dependency output.
- `--output-dir DIR`: validation JSON/Markdown destination.
- `--candidate GROUP:ARTIFACT@VERSION`: optional extra candidate; repeatable.
  PURL form is also accepted.

Expected output: confirmed, version-mismatch, and missing classifications for
the emitted or explicitly requested candidates.
