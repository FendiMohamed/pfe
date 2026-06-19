# APK SBOM Project Handbook

This folder is the self-study guide for the complete project. It explains the
research problem, the Android concepts, the implemented pipeline, every CLI
command family, the evaluation evidence, the failed experiments, and the
decisions that shaped the final MVP.

The handbook does not replace the generated evidence under `docs/evaluation/`
or the implementation under `src/apk_sbom/`. It explains those artifacts and
links back to them as proof.

## Recommended reading order

1. [Start here](00_START_HERE.md)
2. [Project goals and current state](overview/PROJECT_GOALS_AND_CURRENT_STATE.md)
3. [Research foundations](research/RESEARCH_FOUNDATIONS.md)
4. [Paper-to-implementation map](research/PAPER_TO_IMPLEMENTATION.md)
5. Concepts:
   - [APK, DEX, and Android bytecode](concepts/APK_DEX_ANDROID_BASICS.md)
   - [SBOM, CycloneDX, PURL, OSV, and CVEs](concepts/SBOM_CYCLONEDX_CVE.md)
   - [Library matching features](concepts/TPL_MATCHING_FEATURES.md)
   - [R8, ambiguity, and uncertainty](concepts/R8_AND_UNCERTAINTY.md)
   - [Reference databases and ground truth](concepts/REFERENCE_DB_AND_GROUND_TRUTH.md)
6. Architecture and implementation:
   - [End-to-end architecture](architecture/END_TO_END_PIPELINE.md)
   - [APK extractor and DEX analyzer](implementation/EXTRACTOR_AND_DEX_ANALYZER.md)
   - [Reference database builder](implementation/REFERENCE_DB_PIPELINE.md)
   - [Matcher and version selection](implementation/MATCHER_AND_VERSION_SELECTION.md)
   - [SBOM, reports, and vulnerabilities](implementation/SBOM_REPORT_AND_VULNERABILITIES.md)
   - [Source validation](implementation/SOURCE_VALIDATION.md)
   - [AI/R8 and hybrid experiments](implementation/AI_R8_AND_HYBRID.md)
7. Running the project:
   - [Setup and environment](commands/SETUP_AND_ENVIRONMENT.md)
   - [Core CLI reference](commands/CORE_CLI_REFERENCE.md)
   - [Reference DB CLI reference](commands/REFERENCE_DB_CLI_REFERENCE.md)
   - [Experiment and AI CLI reference](commands/EXPERIMENT_AND_AI_CLI_REFERENCE.md)
   - [First APK walkthrough](workflows/FIRST_APK_WALKTHROUGH.md)
8. Evidence and history:
   - [Datasets, metrics, and results](evaluation/DATASETS_METRICS_AND_RESULTS.md)
   - [Failed and non-promoted experiments](evaluation/FAILED_EXPERIMENTS.md)
   - [Priority reference DB experiment](evaluation/PRIORITY_DB_EXPERIMENT.md)
   - [Project timeline](history/DAY_BY_DAY_TIMELINE.md)
   - [Decision rationale](decisions/DECISION_RATIONALE.md)
9. Daily reference:
   - [Troubleshooting](operations/TROUBLESHOOTING.md)
   - [Safe experiment rules](operations/SAFE_EXPERIMENT_RULES.md)
   - [Glossary](reference/GLOSSARY.md)
   - [File and proof index](reference/FILE_AND_PROOF_INDEX.md)

## Five facts to remember

- The tool analyzes compiled APKs and emits evidence-backed CycloneDX SBOM
  components; it does not reconstruct a perfect Gradle build.
- Library identity and exact-version confidence are separate decisions.
- The normal real-APK metric is `927/1837` confirmed **emitted Maven versions**
  across 102 source-validated APKs. It is not full dependency recall.
- The `6772/6772` result is a separate source-version-constrained upper-bound
  lane, not APK-only production accuracy.
- AI, R8 diagnostics, large reference databases, and the priority DB remain
  report-only or evaluation-only unless their promotion gates pass.

## Sources of current truth

When two documents disagree, use this order:

1. [TASKS.md](../../TASKS.md) and
   [CODEX_CONTEXT.md](../codex/CODEX_CONTEXT.md) for current status.
2. Generated evaluation dashboards and JSON artifacts.
3. Implementation and tests.
4. This handbook for explanation.
5. Older planning documents for historical intent only.
