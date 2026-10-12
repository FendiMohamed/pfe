# Paper Evidence Matrix

This is the working evidence matrix for the implementation-and-evaluation paper.
It separates what a source supports from what it does not support. Project
results are traced to the retained theses, evaluation notes, and dashboards.
The paper uses these recorded results without rerunning the experiments;
missing machine-readable exports limit independent recalculation, not the
existence of documented evidence.

## Related-work evidence

| Source | Main evidence contribution | Dataset/metric condition | Permitted use in paper | Do not claim |
|---|---|---|---|---|
| TPL-Benchmark | Realistic benchmark construction and cross-tool limitations | 6,055 APK/source pairs; detector comparison uses 946 selected apps and 28,210 valid mappings; 60.15% LibPecker library F1 is candidate-set specific | Motivate realistic denominators, reference coverage, R8 and version ambiguity | Universal accuracy ceiling or directly comparable baseline |
| UniBOM | Integrated binary/filesystem/source SBOM workflow and visualization | 258 firmware images plus IoT source trees; comparative vulnerability counts without complete component gold standard | Motivate end-to-end SBOM and downstream analysis integration | Android exact-version accuracy or higher-count-equals-higher-precision |
| SAD | Structural class/CDG evidence and stricter version-level accounting | LibScan-derived 1,231-app/562-version data; separate tuning strata; version-level† counts extra wrong versions as false positives | Motivate ambiguity-aware version evaluation and structural evidence | Current implementation of SAD or general population F1 |
| LibHunter | R8 prevalence and optimization-specific failure modes | 2,347-app prevalence sample; controlled 200-app/31-TPL variants and 650 single-strategy variants; tuned thresholds | Motivate inlining/CallSiteOptimization stress testing and report-only R8 diagnostics | R8-proof detection or vulnerability accuracy from warning counts |
| LibScan | Coarse-to-fine signatures, opcode/call-chain evidence, early stopping | 939-app/5,956-existence benchmark plus controlled D8/R8 variants; thresholds tuned by stratum | Motivate layered evidence and transformation-specific evaluation | Direct score comparison with project APK lanes |
| ATVHunter | CDG decoupling, CFG/opcode matching, large reference database | 356-app/189-TPL ground truth; 6,819 version files; thresholds selected on separate groups | Motivate reference coverage and version-aware downstream workflow | Complete native/dynamic coverage or vulnerability precision |
| Systematic Assessment | Cross-tool empirical criteria and failure taxonomy | 221 Android apps, 59 unique TPLs, 2,115 version files; six criteria including candidate construction, effectiveness, efficiency, version identification, obfuscation resilience, and ease of use | Motivate separate module-decoupling, version, transformation, and usability dimensions; support multidex/AAR/package-structure limitations | Pooled tool percentages remain protocol-specific; its 2021 corpus is not the current project’s ground truth |

## Project claim contracts

### Controlled recovery

- **Claim:** The implementation recovers expected components and versions on the generated controlled fixture set.
- **Evidence:** `docs/evaluation/CONTROLLED_EVALUATION.md` and the retained thesis snapshot.
- **Unit:** expected component/version rows in generated APK fixtures.
- **Documented values:** the project history records 30 fixtures/35 components as an earlier checkpoint, followed by expansion to the final thesis snapshot of 72 fixtures/84 expected versions.
- **Permitted interpretation:** controlled fixture behavior, including cautious candidate labels for R8 rename/shrink.
- **Limitations:** generated library-focused fixtures, small coordinate set, no general real-APK accuracy claim; the generated batch is not present here for independent regeneration.

### Source-validated emitted-version confirmation

- **Claim:** Among Maven versions emitted by the matcher for source-validated APKs, the reported version agrees with the resolved source dependency evidence at the documented rate.
- **Evidence:** retained thesis tables, evaluation summaries, and dashboards; the source records document the reported counts, while machine-readable row exports are not present in this checkout for independent recalculation.
- **Unit:** emitted Maven coordinate/version rows.
- **Documented values:** clean 47/47 across five APKs; partial 880/1,790 across 97 APKs; combined 927/1,837 across 102 APKs.
- **Permitted interpretation:** emitted-version confirmation rate.
- **Limitations:** not full dependency recall, not all APKs, source dependency trees are a proxy for packaged code, and raw artifacts/calibration overlap require reconciliation.

### Full source-denominator coverage

- **Claim:** The matcher emits a documented subset of source-observed coordinate/version rows.
- **Evidence:** retained source-denominator summaries and coverage dashboards.
- **Unit:** source dependency coordinate/version rows.
- **Documented value:** 927/12,082, where the 12,082-row denominator belongs to the 106 source-tree cases (102 Maven-emitting cases plus four no-Maven-signal controls).
- **Permitted interpretation:** source-denominator coverage for the source-tree evaluation layer; report the 110-case transparency inventory separately.
- **Limitations:** the row-level export is not present in this checkout, so preserve the documented snapshot and its exclusion rules; never substitute accuracy, recall, or packaged-code completeness without a stronger oracle.

### Reference-database coverage

- **Claim:** The shared reference database is incomplete relative to the source-observed evaluation population, so coverage is a first-order threat to end-to-end recall.
- **Evidence:** `docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md`.
- **Unit:** source coordinate/version rows across 106 inspected source trees.
- **Documented values:** 12,082 source rows; 18.4% have a coordinate present in the shared DB; 10.2% have the exact source version present; 927 rows are emitted with the exact source version.
- **Permitted interpretation:** motivates a coverage-first evaluation and explains why emitted-row confirmation and source-denominator coverage must be reported separately.
- **Limitations:** the dashboard is a retained historical snapshot and must be cited with its 106-case source-tree scope; the 110-case transparency inventory adds boundary examples but does not redefine the 927/1,837 metric. Coverage values do not by themselves measure matcher precision.

### APK-family and boundary stratification

- **Claim:** Evaluation outcomes vary by APK family and validation status, and native/hidden-code/no-Maven-signal cases define explicit scope boundaries.
- **Evidence:** `docs/evaluation/APK_TYPE_EVALUATION.md` and `docs/evaluation/THESIS_EVALUATION_TABLES.md`.
- **Unit:** APK bucket and emitted Maven component/version row.
- **Permitted interpretation:** report clean, partial, controlled, report-only, and limitation buckets separately; use failure categories to explain where the pipeline has evidence.
- **Limitations:** bucket membership is project-defined and some historical dashboard snapshots differ in case counts; no pooled score should hide the bucket definitions.

### Source-version-constrained upper bound

- **Claim:** A source-version-restricted candidate analysis confirms the source-known versions in the documented cases.
- **Evidence:** retained evaluation summaries.
- **Unit:** source-constrained coordinate/version rows across 106 cases.
- **Documented value:** 6,772/6,772 across 106 source-tree cases, using a
  10,517-component v2 reference database and per-APK exact source-version
  slices.
- **Permitted interpretation:** upper-bound recognition under source-known version constraints.
- **Additional diagnostic:** 5,238 source-gap rows remain; the retained v2
  triage identifies 2,281 matcher-recall candidates and 442 missing-reference
  candidates, with the remainder classified as artifact-family, metadata, or
  other source boundaries.
- **Limitations:** not ordinary APK-only production performance; source
  versions constrain candidate selection and the v2 DB is a local evaluation
  artifact.

### Downstream vulnerability workflow

- **Claim:** The pipeline preserves confidence and source-validation status when mapping emitted Maven coordinates to OSV findings.
- **Evidence:** `src/apk_sbom/vulnerability.py`, SBOM/report tests, and controlled demonstrations.
- **Unit:** report finding/component, not vulnerability precision or recall.
- **Documented examples:** clean F-Droid demonstration with zero OSV findings; controlled Jackson 2.9.10.8 fixture with three confirmed advisories.
- **Permitted interpretation:** workflow and evidence-gating demonstration.
- **Limitations:** live API dependence, no vulnerability gold standard, and finding authority depends on component/version evidence.

### Rejected global transformation promotion

- **Claim:** The project rejected a global R8 blend after explicit regression
  checks, keeping transformation-aware signals diagnostic or scoped.
- **Evidence:** examiner review and the experiment decision ledger.
- **Documented result:** four target improvements were accompanied by six
  controlled regressions, 30 real source-validated regressions, and eight
  clean-real regressions.
- **Permitted interpretation:** supports the conservative promotion policy and
  the separation of experiment-only from default matcher authority.
- **Limitations:** this is a design-decision result, not a general benchmark
  score; the exact experiment snapshot must be cited.

### R8 Phase-4 snapshot reconciliation

- **Finding:** The retained artifacts contain two Phase-4 summaries that must
  not be silently combined. The examiner/decision-ledger snapshot reports 4
  target improvements, 6 controlled regressions, 30 real source-validated
  regressions, and 8 clean-real regressions. The expanded
  `R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md` reports 10 potential target
  rows, 6 controlled regression blockers, 121 real source-validated regression
  blockers, and 10 clean-real blockers over 1,093 covered component rows.
- **Interpretation:** Both artifacts reject global promotion, but they are not
  the same evaluation snapshot or denominator. The paper must select one
  frozen artifact, name its scope, and avoid presenting the two count sets as
  one result.
- **Current paper rule:** Describe the decision qualitatively (global
  multi-scale R8 promotion was rejected after control and real-row
  regressions), or cite the examiner/ledger counts with an explicit
  retained-snapshot qualifier. Do not combine the expanded Phase-4 counts with
  the examiner/ledger counts without their matching database and run
  identifiers.

### Promoted guarded matcher behavior

- **Claim:** The delivered default matcher includes only narrowly gated
  promotions whose control checks passed.
- **Evidence:** `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_VERIFICATION.md`,
  `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DEFAULT_PROMOTION_VERIFICATION.md`,
  and `docs/evaluation/GUARDED_REFERENCE_DB_PROMOTION_WORKFLOW.md`.
- **Documented conditions:** composite shortlist margin `0.10` with complete
  version bands; literal/context reranking requires at least two matched
  version-unique features, unique score at least `0.10`, advantage at least
  `0.05`, and raw-score distance at most `0.020`.
- **Permitted interpretation:** these are implementation-policy details and
  guarded design decisions, not standalone population accuracy claims.
- **Limitations:** promotion results are tied to their control slices and
  database snapshots; app-specific reference experiments remain isolated.

### CLI authority and report-only separation

- **Claim:** The user-facing CLI enables the two promoted guarded matcher
  behaviors by default and exposes R8, version-band, AI, and hybrid-router
  additions through explicit opt-in report-only flags.
- **Evidence:** `src/apk_sbom/cli.py` parser definitions and report-generation
  options; promotion verification tests.
- **Permitted interpretation:** implementation behavior and interface
  provenance. The flags document authority boundaries; they do not establish
  population-level accuracy.
- **Documented details:** both promoted rerankers default to enabled and can
  be disabled to reproduce the pre-promotion baseline. Report-only options
  explicitly state that they do not change matcher scoring, selected versions,
  SBOM output, vulnerability labels, or source-validation metrics.
- **Limitations:** this audit inspected the parser and targeted promotion
  paths; final manuscript wording still requires a frozen source snapshot and
  CLI/version record.

### Promotion-gate test evidence

- **Claim:** The promoted defaults require complete control coverage and zero
  reportable drift; guarded reference additions reject global scope when
  regressions occur; Phase-5 R8 remains experiment-only; and the APK-only
  version-band candidate expansion is blocked when it produces zero APK-only
  fixes.
- **Evidence:** `tests/test_composite_family_shortlist_default_promotion.py`,
  `tests/test_version_unique_literal_context_default_promotion.py`,
  `tests/test_guarded_reference_db_promotion.py`,
  `tests/test_r8_phase5_trigger_control_validation.py`, and
  `tests/test_version_band_candidate_expansion_v3.py`.
- **Permitted interpretation:** These are gate-policy and classification
  assertions, not population accuracy results.
- **Limitation:** The tests were read but not executed in this audit; raw
  experiment inputs referenced by some tests are absent from the checkout.

### Negative-experiment test evidence

- **Claim:** Global multi-scale R8 promotion is rejected when any controlled
  or real regression-risk row appears; the scoped R8 trigger blocks strong and
  generated controls; and APK-only sibling-anchor reranking remains diagnostic
  unless sufficient anchors exist, without changing the default matcher.
- **Evidence:** `tests/test_r8_phase4_scoped_experiment_diagnostics.py`,
  `tests/test_r8_phase5_scoped_trigger.py`, and
  `tests/test_version_band_apk_reranker.py`.
- **Permitted interpretation:** rejection and report-only policy behavior.
- **Limitation:** these tests use synthetic inputs or absent retained Phase-4
  JSON paths; they do not independently reproduce the historical population
  counts.
