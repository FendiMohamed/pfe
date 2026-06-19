# Project Evolution Timeline

This timeline combines repository history with the generated project evidence.
The research reading and structured paper analysis began before the first code
baseline. “Day 1” below means the first current Git commit.

## Before Day 1: research foundation

- Read and structured the Android TPL/SBOM literature.
- Corrected optimistic or incomparable reported metrics.
- Identified R8, exact-version ambiguity, missing transitive reconstruction,
  and lack of standard SBOM output as the central gaps.
- Chose a multi-feature, evidence-gated MVP rather than a name/hash detector.

## 2026-05-18 — Day 1: initial MVP baseline

Commit `98c7261`.

- Established the Python package and CLI.
- Added APK/DEX inspection, reference construction, matching, CycloneDX, OSV,
  tests, and initial documentation.
- Froze the first scope around static APK analysis and Java/Kotlin Maven
  libraries.

## Late May — controlled mechanics and R8 foundations

The working tree evolved through:

- calibrated reference profiles;
- controlled clear and R8 fixtures;
- confidence-aware matching;
- source validation;
- report generation;
- phased R8 diagnostics and inert multi-scale features.

The current Git history compresses much of this early work into the baseline,
while the evaluation artifacts preserve the phase details.

## 2026-06-02 — real-APK evidence checkpoint

- Published real APK evidence and planning.
- Shifted from prototype demonstrations toward source-backed validation and
  category-separated evaluation.

## 2026-06-06 — rescue and no-Maven work

- Rescued blocked source trees with compatible Gradle/JDK and isolated
  validation copies.
- Expanded source-validated real APK evidence.
- Added no-Maven signal diagnostics and AndroidX report-only experiment.

## 2026-06-07 — honest limitations and coverage-first pivot

- Added fork-family and limitation dashboards.
- Added wrong-version optimization evidence.
- Recorded a guarded coroutines experiment.
- Built the coverage-first source denominator.
- Started the source-observed reference-growth lane.

This date is a major methodological change: the project stopped treating
emitted-component correctness as if it were full dependency recall.

## 2026-06-08 to 2026-06-09 — source-observed DB growth

- Processed source-observed catalogs in batches through the complete queue.
- Retried failed downloads.
- Classified metadata-only, alias, repository, and conversion boundaries.
- Started an all-versions DB lane.

## 2026-06-10 — priority reference DB pivot

- Recognized that the full all-versions lane was too slow for the thesis
  deadline.
- Built a value-first real-APK priority catalog.
- Downloaded, converted, and extracted the first priority DB.
- Added priority coverage evaluation and rerun tooling.

## 2026-06-11 to 2026-06-14 — large DB completion

- Continued heavy all-version extraction, especially Android material-icon
  families.
- Prioritized repeated and lightweight rows.
- Built and analyzed a large combined DB.
- Probed package and coordinate-preserving prefilters.
- Completed source-version-constrained evaluation across 106 cases.

## 2026-06-15 — final v2 and thesis packaging

- Added large-DB readiness, matcher-recall diagnostics, and transparency
  exports.
- Produced the final v2 thesis/demo layer.
- Refreshed the defense deck, checklist, and final report readiness package.

## 2026-06-16 — AI/R8 and hybrid diagnostics

- Added the report-only RandomForest assistant.
- Trained the structured-token Transformer.
- Created final AI evaluation commands and evidence.
- Added hybrid routing and version-band rerank experiments.

## 2026-06-17 — promotion gates and negative DL result

- Added hybrid production-report assistance.
- Added R8 structural-recall and APK-only promotion gates.
- Built heldout and raw-opcode corpora.
- Trained the raw-opcode Transformer; it failed to beat its baseline.
- Added the MVP AI integration gate and final AI defense demo.

## 2026-06-18 — presentation modernization and final bounded experiments

- Modernized the defense presentation.
- Recovered the final lightweight priority rows.
- Evaluated Fragment 1.6.2 in isolation and kept it experiment-only.
- Ran the priority DB I2P fail-fast preflight.
- Rejected priority DB production promotion and kept the shared calibrated DB
  unchanged.

## Evolution in one line

```text
paper review -> static MVP -> controlled proof -> real source validation
-> honest coverage denominator -> large/priority DB research
-> transparent final v2 -> report-only AI/R8 assistance
```

For commit-level detail:

```powershell
git log --reverse --date=short --pretty=format:"%ad %h %s"
```
