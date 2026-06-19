# Project Goals and Current State

## Goal

The project investigates whether a useful Software Bill of Materials can be
recovered from compiled Android APKs, including APKs affected by R8
optimization and obfuscation, and whether the recovered components can be
mapped to known vulnerabilities.

The MVP target is practical rather than magical:

- identify Maven library coordinates when evidence is strong;
- recover exact versions when the reference data supports separation;
- expose ambiguous versions instead of guessing;
- emit a standard CycloneDX document;
- map components to OSV advisories;
- validate results against source dependency trees where available.

## Current stable MVP

The stable pipeline includes:

- APK archive, manifest, DEX, and native-library extraction;
- package, class, method, opcode, dependency, literal, API-reference, and
  opcode n-gram features;
- SQLite reference fingerprints built from Maven JAR/AAR releases;
- weighted candidate ranking plus guarded family and literal-context logic;
- separate identity and version confidence;
- CycloneDX 1.5 output with Package URLs;
- OSV lookup with confirmed-versus-potential vulnerability labels;
- source validation against Gradle dependency trees;
- JSON, Markdown, and HTML reporting.

## Current evaluation headline

| Evidence lane | Result | Meaning |
|---|---:|---|
| Controlled fixtures | `84/84` exact versions | Pipeline mechanics work when ground truth and references are controlled. |
| Clean source-validated APKs | `47/47` emitted versions | Strong real-APK cases can be exactly confirmed. |
| Partial source-validated APKs | `880/1790` emitted versions | Harder real APKs expose ambiguity and coverage limits. |
| All source-validated APKs | `927/1837` across 102 APKs | `50.5%` emitted Maven version confirmation rate. |
| Source-known v2 lane | `6772/6772` emitted rows | Upper-bound recognition with exact source-version constraints. |

The `927/1837` denominator contains Maven components emitted by the APK-only
pipeline and then checked against source evidence. It is not the number of all
dependencies present in the source tree.

The v2 result deliberately asks a different question: if the matcher is given
an exact source-known coordinate/version slice from the large DB, can it
recognize the emitted evidence? It cannot be presented as general APK-only
accuracy.

## Current reference-coverage experiment

The evaluation-only priority database contains `2477` components across `1164`
coordinates. It covers `9657/12082` exact source rows (`79.9%`) and
`10767/12082` source rows at coordinate level (`89.1%`).

That database was not promoted. An I2P preflight showed that broad package
overlap increased confirmations but also emitted many false candidates. The
fail-fast gate stopped the wider rerun. The shared calibrated database remains
unchanged.

## Current AI position

The RandomForest and Transformer work proves a report-only assistance
workflow. The strongest defensible source-free structured-token result is
macro-F1 `0.882`. A raw-opcode Transformer scored `0.110`, below its `0.128`
baseline. Therefore AI can annotate risk and uncertainty but cannot change
selected versions, SBOM components, or CVE labels.

## Where to verify

- [Current task board](../../../TASKS.md)
- [Current Codex context](../../codex/CODEX_CONTEXT.md)
- [Thesis evaluation tables](../../evaluation/THESIS_EVALUATION_TABLES.md)
- [Final v2 results section](../../thesis/FINAL_V2_RESULTS_SECTION.md)
- [Priority coverage dashboard](../../evaluation/REFERENCE_DB_COVERAGE_PRIORITY_DASHBOARD.md)
- [Priority preflight](../../evaluation/REAL_APK_PRIORITY_TARGET_CONTROL_PREFLIGHT.md)
- [AI/R8 integration gate](../../evaluation/AI_R8_MVP_INTEGRATION_GATE.md)
