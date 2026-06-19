# Experiment and AI CLI Reference

These commands generate evidence. Unless a promotion document says otherwise,
they do not change production matcher, SBOM, or CVE authority.

## AI dataset and model commands

### `ai-r8-build-dataset`

Builds JSON and CSV training rows from existing diagnostics.

- `--matcher-recall-json`: matcher-recall input.
- `--transparency-json`: final transparency export.
- `--phase5-json`: scoped R8 trigger evidence.
- `--r8-obfuscation-json`: obfuscation diagnostics.
- `--output-json`, `--output-csv`: destinations.

Expected result: labeled, case-addressable evidence rows. It does not train.

### `ai-r8-train`

Trains the optional RandomForest.

- `--dataset-json`: training rows.
- `--model-output`: Joblib model.
- `--metrics-output`: split, metrics, baselines, feature importance, ablations.

### `ai-r8-suggest`

Creates report-only recommendations.

- `--dataset-json`: rows to score.
- `--model-path`: optional trained model.
- `--metrics-json`: training metrics.
- `--output-json`: suggestions.
- `--output-doc`: readable diagnostics.

### `ai-r8-final-eval`

Combines all ML/DL proof into one final JSON and Markdown report. Inputs include
the complete evidence package:

- `--ai-summary-json`: compact RandomForest assistant summary.
- `--ai-metrics-json`: RandomForest training/evaluation metrics.
- `--dl-metrics-json`: structured-token Transformer metrics.
- `--report-only-demo-json`: proof that AI attachment preserves authoritative
  output.
- `--independent-corpus-json`: larger project-heldout corpus manifest.
- `--raw-opcode-corpus-json`: bounded raw DEX/opcode corpus.
- `--raw-opcode-transformer-metrics-json`: raw-opcode model and baseline
  metrics.
- `--mvp-integration-gate-json`: current authority verdict.
- `--output-json`, `--output-doc`: combined destinations.

### `ai-r8-integration-gate`

Evaluates whether AI may enter the MVP and at what authority level. Inputs
are:

- `--ai-metrics-json`
- `--ai-suggestions-json`
- `--structured-dl-metrics-json`
- `--mvp-safe-dl-metrics-json`
- `--raw-opcode-dl-metrics-json`
- `--independent-corpus-json`
- `--hybrid-production-json`
- `--final-smoke-json`
- `--strict-gate-matrix-json`
- `--output-json`
- `--output-doc`

Together they cover RandomForest evidence, full and MVP-safe Transformers,
raw-opcode DL, the independent corpus, hybrid production evidence, the final
smoke run, and the strict promotion matrix.

## Hybrid routing

### `hybrid-matcher-router`

Combines matcher recall, transparency, source gaps, wrong-version evidence, and
optional AI suggestions into investigation routes.

Flags:

- `--matcher-recall-json`
- `--transparency-json`
- `--source-gap-json`
- `--wrong-version-json`
- `--ai-suggestions-json`
- `--output-json`
- `--output-doc`

The output recommends a diagnostic lane; it does not select components.

## R8 experiments

### `r8-phase5-experiment`

Reads `--phase4-json` and writes `--output-json` plus `--output-doc`.
`--json-only` skips Markdown.

### `r8-structural-recall-experiment`

Uses `--router-json`, `--large-analysis-json`, and
`--ai-suggestions-json`; writes JSON/Markdown. It analyzes hard structural
rows without changing matcher output.

### `r8-apk-structural-promotion-gate`

Uses the router, large analysis, and AI evidence. Threshold flags are:

- `--min-opcode-score`
- `--min-literal-score`
- `--min-dependency-score`
- `--max-name-score`
- `--min-identity-confidence`

`--output-json` and `--output-doc` store the verdict. Threshold changes must be
tested on both targets and controls.

## Version and family experiments

### `version-band-experiment`

Reads `--input-json`; writes `--output-json` and `--output-doc`. Diagnoses
older-version stealing in AndroidX-like families.

### `version-band-rerank-experiment`

Uses `--router-json`, `--large-analysis-json`, and `--v2-dashboard-json`.
This is source-known/report-only evidence, not APK-only authority.

### `version-band-apk-reranker`

Uses APK-only baseline alternatives and sibling-era anchors.

- `--max-score-drop`: largest allowed drop from selected to alternative.
- `--min-sibling-era-anchors`: minimum family anchors required.
- input/output flags select router, analysis, JSON, and Markdown.

### `version-band-candidate-expansion`

Combines `--source-known-json` and `--apk-only-json` into a v3 promotion gate.

### `lifecycle-family-experiment`

Reads `--input-json` and writes JSON/Markdown for public-versus-Android
Lifecycle artifact separation.

## No-Maven and literal experiments

### `no-maven-androidx-experiment`

Tests report-only AndroidX signals when no normal Maven result is emitted.

### `no-maven-fork-family-experiment`

Audits Mastodon-style fork-family signals without forcing a Maven identity.

Both use `--input-json`, `--output-json`, and `--output-doc`.

### `literal-context-experiment`

Measures raw literal/context tie evidence from `--input-json`.

### `version-unique-literal-context-experiment`

Uses `--phase4-json` for row metadata and `--reference-db` for version-unique
features, then writes `--output-json` and `--output-doc`.

## Reading experiment results

Every experiment should answer:

1. Which target rows improved?
2. Which clean/partial/no-Maven/boundary controls changed?
3. Was source knowledge used?
4. Did candidate count or runtime become unacceptable?
5. Is the result promoted, report-only, rejected, or blocked?

If a document does not answer these, it is exploratory evidence, not a final
MVP change.
