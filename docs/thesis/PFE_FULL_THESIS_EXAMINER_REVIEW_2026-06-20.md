# PFE Full-Thesis Examiner Review

Date: 2026-06-20

Thesis: *Evidence-Based SBOM Recovery from Compiled Android APKs: Design,
Implementation, and Evaluation of a Hybrid Static Analysis Pipeline*

Student: Fendi Mohamed

## Overall Assessment

The thesis is a strong and defensible computer-science engineering report. Its
main quality is not a claim of universal APK dependency recovery, but a
reproducible system that separates authoritative evidence, uncertain evidence,
source-known upper bounds, experiment-only results, and unsupported cases.

The implemented pipeline, the evaluation artifacts, the failed-experiment
ledger, and the explicit authority boundary for ML/DL assistance give the work
substantial engineering and research value. The document is suitable for
defense after the final administrative fields are supplied and the corrected
source is rebuilt once more with LuaLaTeX and Biber.

Provisional examiner classification: very good. The strongest defense will
emphasize evidence governance, reproducibility, and honest limitations rather
than presenting the matcher as a universal Android dependency detector.

## Principal Strengths

- The research problem is relevant to software-supply-chain security and is
  clearly narrowed to APK-only evidence recovery.
- The contribution is implemented end to end: APK inspection, DEX evidence,
  reference-feature construction, matching, CycloneDX output, OSV enrichment,
  source validation, and reproducible reports.
- Controlled, clean, partial, source-known, report-only, experiment-only, and
  limitation evidence are reported separately.
- Negative experiments are preserved and used to justify design decisions.
- The ML/DL/R8 layer is explicitly blocked from authoritative matcher, SBOM,
  CVE, and source-validation decisions.
- The evaluation reports numerators and denominators instead of relying only
  on headline percentages.
- The appendix connects claims to commands and frozen evidence artifacts.

## Corrections Applied During This Review

### Evidence and Result Consistency

- Corrected the matcher equation and explanation to match the implementation:
  the denominator is the sum of configured feature weights; a missing feature
  contributes a zero score, while a disabled feature has zero configured
  weight.
- Distinguished the 102 source-validated APKs that emitted Maven rows from
  four additional source-validated no-Maven-signal controls. The complete
  source-tree evaluation therefore contains 106 cases, while the
  927/1,837 emitted-version metric applies only to the 102 emitting cases.
- Clarified that 50.5% is emitted Maven version confirmation, not complete
  dependency recall.
- Clarified that the 6,772/6,772 source-known v2 result is a constrained upper
  bound and not unconstrained APK-only accuracy.
- Clarified which difficult families expose wrong, missing, or ambiguous Maven
  rows and which boundary cases are outside Maven-version accuracy.
- Added the exact regression counts for the rejected global R8 blend:
  four target improvements, six controlled regressions, thirty real
  source-validated regressions, and eight clean-real regressions.

### Implementation Accuracy

- Removed the unsupported claim that the extractor inspects APK signatures.
- Replaced “all discovered DEX files” with “all successfully parsed DEX
  files.”
- Distinguished archive resource/asset inventory from DEX string-literal
  evidence.
- Described manifest extraction as declared-permission extraction rather than
  unspecified application-property recovery.
- Clarified that the raw-opcode dataset is separate, not statistically
  independent.
- Clarified that the MVP-safe Transformer is promising report-only evidence
  whose production decision wiring remains disabled.

### Reproducibility

- Replaced the nonexistent sample APK with
  `data/test_apks/real/F-Droid.apk`.
- Replaced the obsolete shared-database filename with
  `data/reference_db/reference_features_calibrated_combined.sqlite`.
- Reworked the reference-database example so it first creates
  `configs/libraries.reproduction.json` from the existing catalog and then
  uses isolated artifact, DEX, and SQLite output paths.
- Replaced the nonexistent appendix configuration example with the real
  `configs/libraries.json` path where appropriate.
- Qualified Docker as a standardized environment, not a guarantee of
  bit-for-bit reproduction when Maven repositories, Gradle metadata, OSV, or
  unpinned installers change.

### References and Academic Writing

- Confirmed that all 46 citation keys used by the thesis have matching
  bibliography entries and that no bibliography entry is unused.
- Checked official web references and primary-paper records where available.
- Corrected venue, page, and DOI metadata for LibD, LibPecker, ATVHUNTER,
  LibAttention, SAD, and UniBOM.
- Verified the TPL-Benchmark dataset sizes and the reported 60.15% LibPecker
  library-level F1 against the primary paper.
- Replaced informal expressions such as “microscopic near ties” and “old
  wrong alpha release” with precise academic wording.
- Standardized number formatting and the spelling of “Random Forest.”
- Rephrased an uncited named future method as a generic calibrated set-valued
  method.

## Validation Performed

- Complete source review of the front matter, seven chapters, appendix, and
  bibliography.
- Cross-check of thesis claims against generated Chapter 3 and Chapter 6
  evidence snapshots, evaluation dashboards, experiment ledgers, and current
  implementation modules.
- CLI-help verification for the commands and flags published in the thesis.
- Citation-key audit: 46 cited keys and 46 bibliography entries, with no
  missing or unused key.
- Official URL and academic-metadata checks, supplemented by direct inspection
  of locally stored primary papers.
- Exact 12-word-overlap scan against the local research-paper and previous
  school-report corpus; no suspicious exact overlap was found. This is a local
  screening check, not a substitute for an institutional plagiarism service.
- Visual inspection of all 122 pages of the latest available compiled draft,
  including full-resolution checks of abstracts, dense tables, architecture
  diagrams, use cases, Chapter 6 results, appendix listings, and bibliography.
  No clipping, overlap, rotated header, or broken diagram remains in that
  build.

## Remaining Items Before Submission

1. Supply the jury president, examiner, and exact defense date.
2. Rebuild the examiner-corrected source with LuaLaTeX and Biber.
3. Inspect the title page, abstracts, Chapter 6 result tables, appendix command
   listings, and bibliography in that final rebuild.
4. Run the institution’s plagiarism checker if one is required.

The current 122-page PDF predates the last source-level corrections to
bibliography metadata, reproducibility paths, and several evidence
clarifications. The authoritative deliverable from this review is therefore
the LaTeX source and the examiner-audited upload package until the final rebuild
is completed.

## Likely Defense Questions

- Why is 50.5% not dependency recall?
- Why is the 6,772/6,772 lane only an upper bound?
- How does the matcher avoid converting ambiguity into false certainty?
- Why are ML/DL predictions blocked from the production SBOM?
- What evidence survives R8, and what remains unsolved?
- Why did the priority database and global R8 blend fail promotion?
- How are native libraries represented when package versions cannot be
  recovered?
- What would be required to promote an experiment into the shared calibrated
  database or authoritative matcher?
