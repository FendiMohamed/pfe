# Paper Writing Session Log

## 2026-09-29 — Paper plan and rules established

- **Objective:** Establish a persistent plan and writing rules for the English
  implementation-and-evaluation paper, using the supervisor's proposed
  structure.
- **Files created/updated:**
  - `papers/implementation_evaluation_paper_plan.md`
  - `papers/PAPER_WRITING_RULES.md`
  - `papers/AGENTS.md`
  - `papers/PAPER_WRITING_SESSION_LOG.md`
- **Decisions:** The supervisor's order controls: Abstract; Introduction;
  State of the Art; Proposed Approach; Implementation and Experimental
  Evaluation; Conclusion. Research questions are stated formally in the
  evaluation section and answered by result subsections.
- **Evidence reviewed:** Current project brief, thesis writing rules and PFE
  plan, paper-to-implementation traceability, thesis evaluation tables,
  artifact index, final v2 results section, experiment decision ledger, and
  relevant implementation modules.
- **Open evidence issues:** `data/results/` and `data/reference_db/` are empty
  except `.gitkeep`; `data/source/` is absent; only 15 APK files are present.
  Reconcile the 102-, 106-, and 110-case result sets; audit reference
  calibration overlap with evaluated apps; refresh all numerical results.
- **Checks:** Read back the new plan and confirm linked project sources exist.
  No tests run; no manuscript or generated evaluation data changed.
- **Next action:** Recover or regenerate the frozen evaluation evidence, then
  build the related-work evidence matrix and Proposed Approach figure before
  drafting Results.

## 2026-09-29 — Thesis, implementation, experiment, and test audit

- **Objective:** Establish a reliable working understanding of both theses,
  the principal implementation path, and the recorded positive and negative
  experiments before drafting the paper.
- **Thesis material reviewed:** PFE introduction, technical background,
  AI-assisted analysis, state of the art, solution/design, implementation and
  evaluation (including results, failed/non-promoted experiments, discussion,
  and validity threats), conclusion, and reproducibility material. Master
  introduction, background/methodology, state-of-the-art taxonomy, proposed
  evidence-trust framework, case-study evaluation, limitations, and conclusion.
- **Implementation material reviewed:** Core data models; APK inspection and
  DEX analysis; Maven reference conversion/features; matcher scoring, version
  decisions, ambiguity and confidence; CycloneDX emission; source validation;
  OSV classification; and report orchestration/report-only gates.
- **Experiment/test material reviewed:** `EXPERIMENT_DECISION_LEDGER.md`, the
  PFE's failed/non-promoted experiment table, key R8/AI/version-band decision
  summaries, plus test inventories and representative matcher, SBOM,
  vulnerability, source-validation, and report authority tests. Tests were
  read but not run.
- **Established interpretation:** The central PFE contribution is a static,
  evidence-gated APK-to-SBOM pipeline with separate identity/version claims,
  source-aware validation, and downstream vulnerability authority. The
  Master thesis contributes a research-synthesis framework for provenance,
  evidence quality, lanes, conflict, abstention, and permitted claim authority;
  it is not a second detector implementation. Global opcode/API weights and
  global multi-scale R8 fusion were rejected or disabled due to no gain or
  regression evidence. Version recency/tie changes and broad reference-database
  expansion were not promoted because they can select unsupported releases or
  inflate false emissions. The narrow Phase 5 R8 trigger and AI remain
  experiment/report-only. Raw-opcode Transformer underperformed its simple
  baseline. Decisions are preserved in the ledger rather than omitted.
- **Scope boundary:** This was a focused deep audit of the thesis arguments,
  main runtime path, canonical decision ledger, and representative tests. It
  was not a line-by-line audit of every source module, every historical
  diagnostic artifact, or every test body. No tests or experiments were run.
- **Open evidence issues unchanged:** Evaluation result/reference/source
  artifacts are not present in this checkout; reconcile the 102/106/110 case
  sets and denominators; inspect reference/calibration overlap; and independently
  regenerate or recover frozen outputs before publishing numerical claims.
- **Next action:** Use this audited understanding to build the paper's source
  matrix and evidence map; treat unresolved data/evaluation questions as gates
  before finalizing quantitative claims.

## 2026-09-29 — Full-checkout study checkpoint

- **Objective:** Continue the user's requested deep study of every project area,
  including historical and presentation artifacts, as preparation for the paper.
- **Inventory refinement:** Confirmed 14 real APK binaries plus one controlled
  limitation APK. The 118 `metadata.json` files under `data/test_apks/real/`
  comprise 103 candidate inventory records (each marked report-generated but
  excluded from source-validated metrics) and 15 APK inspection snapshots;
  they must not be represented as 118 evaluated APKs. Confirmed the checkout
  contains multiple evidence generations and no
  Git history.
- **Handbook/docs reviewed:** Completed the 34-page project-handbook inventory
  and reviewed its architecture, implementation maps, command references,
  evaluation rules, datasets/metrics, failure decisions, workflows, concepts,
  troubleshooting, and file/proof index. This is a navigation layer; primary
  claims still require source or artifact verification.
- **Defense artifacts reviewed:** Mapped deck generations and audited the
  final 39-slide academic deck's plan, source notes, QA scorecard, build
  manifest, and chronology. It separates the 927/1,837 normal emitted-version
  confirmation result from the 6,772/6,772 source-known upper bound. Its source
  paths point to original result files mostly absent from this ZIP.
- **Open count issue:** The records describe 102 primary source-validated cases,
  four no-Maven auxiliary cases (106 total), a v2 set of 106 source-tree cases,
  and older 110-case references. Resolve row-level membership and denominators
  before manuscript claims.
- **Scope boundary:** This remains a systematic ongoing review, not a complete
  line-by-line reading of 1,713 files. No tests or evaluation runs were executed.
- **Next action:** Continue the traced review of runtime modules, scripts,
  configs, every test family, case/source proof records, thesis versions,
  research-source PDFs, and deck slide content; update this index at the next
  reconciliation checkpoint.

### Count reconciliation correction

Further review of `THESIS_EVALUATION_TABLES.md`, `FINAL_V2_RESULTS_SECTION.md`,
`DEMO_FINAL_TRANSPARENCY_REPORT.md`, and `FINAL_DEMO_RUNBOOK_V2.md` explains the
three counts by inclusion rule: 102 Maven-emitting source-validated APKs form
the normal `927/1,837` metric; four no-Maven-signal source-tree controls expand
that source-tree population to 106; four limitation cases expand the complete
transparency inventory to 110. The v2 source-known lane uses 106 source-tree
cases. Case identities/raw row artifacts are mostly missing from this ZIP, so
the count semantics are documented and consistent but still cannot be
independently recomputed from the omitted frozen result exports.

### Runtime behavior checkpoint

Read additional core implementation bodies in `models.py`, `reference_config.py`,
`reference_converter.py`, `reference_features.py`, `source_validation.py`,
`apk_extractor.py`, `dex_analyzer.py`, `matcher.py`, `sbom.py`, `report.py`, and
`vulnerability.py`. Confirmed directly in code: API and opcode-ngram weights are
zero by default; version-unique literal/context reranking and composite-family
shortlisting are enabled; scoring is normalized over active weights; ambiguity
and identity/version confidence are explicit; output is CycloneDX 1.5; native
files are hash-only; Gradle source validation compares coordinate and resolved
version; OSV findings are downgraded where identity/version/source evidence is
insufficient. This confirms the conceptual summary but adds implementation
qualifiers that need to survive paper compression. No tests or experiments ran.

### Dataset/source provenance checkpoint

- Inspected `data/test_apks/real/` metadata schemas. Besides 15 APK-inspection
  snapshots, 103 F-Droid candidate records are marked `report-generated` but
  explicitly `excluded-from-source-validated-metrics`; these candidate records
  must not be confused with source-validated evaluation membership.
- Inspected the retained Simple Time Tracker 1.57 source tree, Gradle reports,
  and source-validation output. Docker `/tmp` extraction solved the Windows
  path-length blocker, after which Gradle produced `:app`
  `baseReleaseRuntimeClasspath`: 105 source coordinates; the recorded SBOM
  validates 6/12 emitted Maven rows and has six version mismatches. Earlier
  status documents still say failed/unknown, so chronology matters. The APK
  and report JSON themselves are not retained in this checkout.
- Identified a stale dataset-planning row that labels controlled multidex as a
  gap despite listing multiple such fixtures. Use generated inventory and
  evaluation evidence when resolving this contradiction.

## 2026-09-29 — Evaluation/configuration trace checkpoint

- Read the real-case/role and group definitions in
  `scripts/build_apk_type_evaluation.py` and the inventory builder's ground
  truth, comparison, source-validation, and limitation logic. Controlled
  expected versions come from fixture truth JSON; real-case result metrics are
  computed from emitted Maven components checked against resolved Gradle
  trees. The current frozen result inputs required to regenerate those outputs
  are absent from this checkout.
- Mapped the 50 configuration JSONs into seed/calibration, expanded, source
  observed, real-APK priority, retry variants, scoped experiments, and
  sequential candidate-selection families. These are alternative/staged
  evidence inputs, not all shared-default reference contents.
- Cataloged test names and assertions without executing them. Important
  invariant families include source-validation classification, identity versus
  version confidence, ambiguity/abstention, report-only AI/R8, zero-change
  integration guards, and current-control promotion rejection.
- **Next:** Inspect the reference acquisition/build path and CLI, then trace
  each major experiment family to its source, input config, report, and test.

## 2026-09-29 — Reference/CLI implementation trace checkpoint

- Read the CLI parser and dispatch for 31 commands. Confirmed the documented
  primary data path: Maven config expansion/download -> JAR/AAR conversion ->
  DEX feature database -> APK matching -> CycloneDX/OSV report, with source
  validation performed as a separate command/artifact. The CLI also exposes
  AI/R8, version-band, family, and literal-context analysis/gate commands.
- Cross-checked `generate-report` flags and help text: opt-in AI, R8, and
  version-band evidence are attached conditionally; their descriptions say
  they do not change matcher scoring, selected versions, SBOM component
  selection, vulnerability labels, or source-validation metrics. This is
  direct interface documentation; each experiment family still needs source
  and test-level confirmation before generalizing.
- Read the full reference-feature storage path and the successful-path unit
  test. SQLite stores component metadata, DEX file hashes/counts, packages,
  classes, methods, opcode/ngram histograms, dependency graph/shape features,
  literals/context, API references, multi-scale fingerprints, and shallow POM
  dependencies. The test asserts those expected rows but does not exercise a
  missing later DEX path.
- **Implementation caveat to verify if reference rebuilding matters:** the
  storage function clears existing feature rows before validating every DEX
  path. It can return `failed` after writes; a normal SQLite context exit
  commits those writes. This is a source-level edge case, not evidence of
  corruption in the omitted historical database, and no project command was
  run.
- Updated `PROJECT_STUDY_INDEX.md`. Script inventory remains 114 files and
  requires grouped tracing from outputs/configs/tests. No tests or evaluation
  runs were executed.
- **Next:** Trace the build/reference catalog scripts as families, then the
  experiment-to-config-to-report-to-test paths; continue thesis/research-PDF
  and artifact review before treating any paper claim as finalized.

## 2026-09-29 — Reference catalog and promotion policy trace

- Traced source-observed catalog generation from the coverage-first dashboard
  and popular catalog into JSON/Markdown/CSV plus download configs. It records
  exact source versions, distinguishes coordinate/version gaps, infers Maven
  Central versus Google Maven, and excludes metadata-only BOM entries from
  bytecode builds. This is a candidate-generation step, not itself evidence of
  improved detection.
- Traced the real-APK-priority catalog from resolved Gradle runtime dependency
  trees. It deduplicates dependency occurrences per APK tree and ranks exact
  coordinate/version slots by distinct-APK support (default tier-one threshold
  is two APK trees). Its declared scope is evaluation-only and it does not
  replace the calibrated/shared DB.
- Read the guarded promotion workflow and unit tests. Policy preserves singleton
  versus exact-bundle claim scope, requires target improvement and zero
  regressions for `safe`, labels target gains with regressions `app-specific`,
  and rejects global promotion when controls regress. Tests exercise these
  classifications, tested-bundle scoping, and invalid scope rejection.
- These scripts consume saved dashboards/comparison JSON and write artifacts;
  they were inspected but not executed. Their input evidence is not fully
  available in this ZIP, so the recorded workflow/policy can be described while
  specific promotion outcomes require artifact-level confirmation.
- Updated `PROJECT_STUDY_INDEX.md`. **Next:** Trace other build/evaluate script
  families (controlled APK generation, inventory/metrics, R8/AI, and version
  experiments) against their fixtures, report artifacts, and tests.

### Phase 5 R8 cross-check

- Read the scoped reranker conditions, CLI integration, test source, and retained
  Phase 5 Markdown. The trigger is only invoked through `r8-phase5-experiment`;
  a search of `matcher.py` and default report code finds no production wiring.
  The report records 286 rows (24 controlled, 262 real), four target
  improvements, and zero triggered regressions/conflicts, and explicitly
  remains experiment-only.
- Test source checks target-context activation, blocks strong baselines and
  generated controls, asserts those reported counts, and statically fails if
  matcher production code imports the scoped reranker. The two phase JSONs
  referenced by these tests are absent from this checkout, so these assertions
  have not been executed or independently recomputed.
- Added this distinction and evidence boundary to `PROJECT_STUDY_INDEX.md`.

## 2026-09-29 — Controlled-fixture and test-inventory trace

- Read controlled fixture generation and the inventory builder. The generator
  resolves artifact metadata, optionally compiles a small Java caller, uses D8
  for clear fixtures and R8 with variant-specific rules for transformed
  fixtures, writes an APK ZIP, and records expected coordinates/versions plus
  build/DEX provenance in `.ground-truth.json`.
- The inventory builder takes those ground-truth files, selected saved report
  JSONs, and source-validation records; controlled comparisons include both
  coordinate presence and exact coordinate-version pairs. Limitation APKs
  exercise unsupported/protected packaging warnings and are expressly outside
  precision/recall metrics.
- Verified current-state absence directly: there are no `.ground-truth.json`
  files or controlled APK binaries in `data/`; `data/results/` has only
  `.gitkeep`. Therefore the long retained `docs/evaluation/APK_TESTSET_INVENTORY.md`
  is a historical compiled inventory, not a current artifact that can be
  regenerated from this ZIP.
- Read `tests/test_controlled_r8_matrix.py`: it checks the R8 variant/rule
  definitions, generated batch categories and tags, phase filtering, and
  reuse-existing behavior using temporary fake files. It does not supply the
  missing controlled dataset. No tests, build tools, or APK generation were run.
- Updated `PROJECT_STUDY_INDEX.md`. **Next:** Continue evaluation builder review
  (real-case case roles/groups and comparison denominators), then connect the
  R8/AI/version-band experiment families to test gates and retained outputs.

### Evaluation role/group consistency check

- Read the real-case registry, group specifications, aggregation functions,
  thesis-ready tables, and retained APK-type report. The registry classifies
  Flying Carpet and FitoTrack as `source-validated-partial` with current
  validation paths (11/17 and 5/18, respectively), and the thesis tables state
  zero blocked source-linked cases.
- Found stale grouping: the APK-type `blocked-source-linked` group still
  contains those two case IDs; its report title says blocked even though its
  result summary aggregates 16/35 emitted versions as source-validated. Treat
  these rows as partial per current roles/validation evidence; do not repeat the
  old group label in the paper.
- `tests/` contains no dedicated test file for `build_apk_type_evaluation.py`.
  The retained `APK_TYPE_EVALUATION.md` is not fully consistent with its current
  source registry. The underlying result JSON is missing, so regeneration and
  whether the stale output can be corrected from current inputs remain
  unverified.
- Added this issue to `PROJECT_STUDY_INDEX.md`. Continue auditing group/report
  drift and the remaining metric producers before claiming the evaluation
  artifact set is reconciled.

### Thesis table generator review

- Read `scripts/build_thesis_evaluation_tables.py`. Its clean/partial/blocked
  case counts derive from the case `role` field, separate from whether current
  validation JSON exists. The current source roles and retained table agree on
  5 clean, 97 partial, 102 total, and 0 blocked, but missing raw input artifacts
  would leave the numerical validation totals unverified even while roles stay
  fixed.
- Found a potential controlled-metric implementation bug: the script parses
  only the first fraction in each controlled group summary. That fraction is
  component true positives / expected components, while the summary's second
  fraction is exact-version true positives / expected components. The parser
  labels the first numerator `confirmed_versions`. Retained data reports 84/84
  on both measures, so this may not change the recorded result, but it would
  misstate exact-version counts if component matches included version errors.
- Neither the APK-type builder nor thesis-table builder has a dedicated test
  file in the 57-file test directory. No builder was executed; this finding is
  from reading the source and retained reports. Added the caveat to
  `PROJECT_STUDY_INDEX.md`.

## 2026-09-29 — Current-default promotion evidence cross-check

- Verified in current `matcher.py` and CLI definitions that composite-family
  shortlisting and version-unique literal/context reranking are both enabled by
  default, with explicit disable flags that reproduce pre-promotion behavior.
- Read both dated verification records, readiness reports, gate logic, and
  promotion-gate tests. Composite shortlisting is a candidate-pruning
  optimization: the report records 81/81 cases, 1,347/8,100 rows removed,
  zero tracked family losses/regressions, and zero reportable selected-version
  changes. The June 3 verification records successful default/disable smoke
  and prior passing focused/full test suites.
- The literal/context reranker changes a version choice under a narrow guard:
  at least two matched features, feature score >=0.10, advantage >=0.05, raw
  leader score >=0.35, raw-score gap <=0.020, and identity-confidence
  tolerance. Its broad one-match diagnostic found regression risks; stricter
  support filtering kept one VLC RecyclerView target change and filtered three
  weak suggestions. The source-validation slice reports VLC 6/26 -> 7/26,
  AntennaPod and OsmAnd unchanged. June 2 verification records default
  promotion and a no-flag real-APK smoke.
- Clarified in the index that these are distinct effects (pruning versus a
  selected-version change), and that the pre-promotion readiness reports are
  superseded by dated verification for current state. Raw DBs/APKs/JSON outputs
  referenced in smokes are missing from this ZIP, so I have not independently
  reproduced historical figures or tests. Promotion gate unit tests use
  synthetic input JSON; feature tests cover the rule itself.
- **Next:** Trace AI/R8 and remaining version-band/lifecycle experiment
  families, including which suggestions can reach reports and which remain
  diagnostic-only; then continue the thesis and research-reference audit.

### AI/R8 authority and evidence boundary

- Read AI dataset construction, feature schema, deterministic case-group split,
  Random Forest training/suggestion path, integration-gate decisions, final
  evaluation, and report-only smoke summary. Training rows combine project
  matcher-recall, source-transparency, Phase 5, and R8-boundary evidence; the
  classifier's permitted output is report wording/triage, never component or
  version selection or vulnerability labels.
- Retained reports give RF macro-F1 0.708; structured-token Transformer 0.977
  with acknowledged source/context shortcuts; source-free/MVP-safe Transformer
  0.882; raw opcode Transformer 0.110 compared with count baseline 0.128. The
  final integration gate blocks matcher authority: strict APK-only eligibility
  is zero after controls. These are project-derived diagnostic corpus results,
  not evidence of external-corpus generalization.
- The report-only smoke says SBOM semantic content and vulnerability labels
  stayed unchanged, while raw SBOM SHA equality is false. This points to
  semantic preservation, not byte-for-byte identity. Underlying metrics,
  models, raw corpora, reports, and APK inputs in `data/results/` are absent in
  this ZIP; figures have not been reproduced here.
- Updated `PROJECT_STUDY_INDEX.md`. Continue AI family review through the
  Transformer training scripts/tests, strict promotion gate, and hybrid-router
  output paths; also trace version-band/lifecycle diagnostics.

### Transformer profiles and hybrid router

- Read the token-corpus builder and tiny-Transformer training path. The `full`
  corpus tokens raw coordinate, source and candidate versions, row source,
  selected project context, and matcher-evidence buckets. The `mvp-safe`
  profile omits raw coordinate/source-version/context tokens and uses candidate
  version shape plus score/overlap/R8 evidence fields. Both classify report
  triage labels and declare production wiring disabled.
- The deterministic split holds cases together but does not group by
  coordinate; cross-case coordinate overlap is therefore possible. This is a
  source-schema risk, not a measured leakage result (the corpus JSON is missing).
  The full structured model's high score should remain qualified by the
  documented source/context shortcut risk; the source-free score is a safer,
  lower-performing research signal.
- Read raw-opcode corpus/trainer and unit-test source. Corpus defaults cap at
  14 APKs, 120 methods per APK, and 128 opcode tokens per method. Its target is
  APK role/obfuscation-profile triage, not library versioning. Case-heldout test
  rows have only two APK cases per label; the retained report says the model
  does not beat opcode-count logistic regression, so this remains a negative,
  research-only result.
- Read hybrid-router catalog and tests. Router outputs an experiment-priority
  recommendation from recall gaps, source gaps, wrong-version pairs, and AI
  suggestions; its declared allowed effects are experiment prioritization,
  report explanation, and future control planning. It explicitly forbids
  selected-version, SBOM, vulnerability, source-validation, or default-score
  changes. Tests exercise sample routes and no-bytecode boundary behavior.
- These experiment inputs and trained model files are absent from the ZIP;
  current source/tests and retained Markdown provide design/history but no
  re-execution in this study. Index updated; next continue R8 strict promotion
  and version-band/lifecycle experiment paths.

### R8 structural gate and version-band/lifecycle decisions

- Read the APK-only R8 structural gate and test source. Candidate pass uses APK
  scores/AI triage plus same-coordinate exact/wrong/false-positive controls;
  source truth is only used after the gate to grade outcomes. The gate is always
  report-only and never promotes by itself. The retained integration matrix
  says strict controls leave zero production candidates (219 pre-control gate
  rows across profiles).
- Read the version-band source-known and source-free reranker reports. Source-
  known candidate restriction suggests 565/582 scoped wrong-version rows may
  be fixable, while 820 exact rows and 120 false-positive emissions are
  controls. The APK-only reranker changes/fixes zero rows; source versions appear
  among baseline alternatives for 44/582 rows (7.6%). Candidate expansion v3
  stays rejected: a deep pilot selected `1.2.0-alpha01` where the source
  version was `1.8.1`. The 565 figure is an oracle/source-constrained upper
  bound, not production accuracy.
- Read low-risk AppCompat/Core and Lifecycle-family diagnostic reports plus
  source/tests. The AppCompat/Core trigger downgrades confidence on supported
  old-version-steal signals; it does not choose a replacement version. The
  Lifecycle experiment distinguishes public coordinates from Android-target
  artifacts, downgrades the public claim only on source-backed target evidence
  or >=2 family anchors, and keeps close patch alternatives ambiguous. Reports
  show 7/13 introduced rows flagged and 2/5 Lifecycle public claims eligible;
  both remain opt-in/report-only diagnostics. The Lifecycle test explicitly
  checks it is not imported into default matcher/report code.
- Verified referenced experiment JSON and router/analysis inputs are missing
  from `data/results/`. Retained Markdown and source/tests describe recorded
  policy and outcomes; this study did not reproduce the numbers. Index updated.

### No-Maven and fork-family boundaries

- Read the AndroidX no-Maven report-only experiment and its tests. It only
  examines cases already classified as AndroidX identity-coverage misses, then
  requires source runtime overlap, the exact source version to already appear
  among report candidates, and candidate/package/opcode floors. Its six retained
  suggestions among 14 rows across three cases are source-backed triage, not
  APK-only component detections. The rest remain suppressed; outputs claim zero
  selection, SBOM, or source-validation metric changes.
- Read Mastodon's `me.grishka.litex` fork-family audit and tests. It uses
  explicit Litex-to-upstream AndroidX mappings and semantic version
  compatibility plus score/package/opcode thresholds; separate direct
  candidates use exact source versions and score/opcode/literal floors. Retained
  report has two Litex suggestions, seven suppressed, and one direct Gson
  suggestion. These remain report-only alias/triage evidence, not proof the APK
  contains upstream coordinates.
- Both test suites assert that matcher and standard report modules do not
  import the experiment modules. The source reports and dependency-tree JSON
  inputs are in the omitted `data/results/` area, so the retained counts are not
  recomputed here. Index updated.

## 2026-09-29 — Deep project and literature study continued

- **Objective:** Continue the user's requested deep understanding of all useful project materials before drafting the paper.
- **Work reviewed:** Started full-text inspection of the 20-page TPL-Benchmark paper, including its dependency-label construction, special-case handling, dataset characteristics, detector comparisons and reported limitations. Connected its APK/source distinction to the project's separate APK evidence and source-validation lanes.
- **Interpretation:** Treat source build declarations as valuable but scoped corroborating evidence. Their mapping to a particular packaged APK depends on modules, variants, build configurations and artifact identity; they must not silently become APK-only ground truth. Keep this distinction explicit in research questions, protocol, results and validity discussion.
- **Status:** This is one PDF pass, not a complete literature review or complete project understanding. Remaining research PDFs, uncited/source materials, thesis passages, code/test links and unavailable APK/results artifacts still require requirement-by-requirement review. No project tests were executed.

- **Additional research papers inspected:** Reviewed selected passages from the systematic assessment of Android TPL tools and the 2025 SAD version-level detector paper. Recorded their methodological relevance and the need to avoid cross-paper metric comparisons without matching datasets, candidate construction and transformations.
- **Remaining:** The complete 15-paper local literature set, prior-student reports, thesis source/PDFs, code/test crosswalk and artifact-level evidence review are still outstanding. No tests were run.

## 2026-09-29 — Thesis and current-state evidence cross-check

- **Work reviewed:** Revisited both English thesis abstracts and the PFE research-question/evaluation definitions; Master trust-framework principles and RQ answers; PFE failed/non-promoted experiment table; experiment decision ledger; V2 results/traceability material; current matcher defaults, CLI flags and selected promotion-gate tests.
- **Substantive distinction:** PFE is the implemented APK-to-SBOM case study. The Master contribution is the evidence-trust framework built around it. Keep these contributions and their evidentiary strength separate when deciding what the paper claims.
- **Current artifact boundary reverified:** 15 APKs present (14 real plus one hidden-DEX limitation case); only `.gitkeep` in results and reference DB; no `data/source/`; one retained unpacked source tree under `data/s3/`. Historical outputs cited in thesis Markdown/LaTeX are not all reproducible from this ZIP.
- **Code/test cross-check:** Current defaults enable the promoted shortlist and guarded version-unique reranker; their regression/disable controls exist in source/tests. Some promotion readiness tests use synthetic JSON and cannot substitute for the absent APK/report/database artifacts. Tests remain unrun.
- **Status:** Partial, evidence-led progress; the complete project review remains open. No experiment was run.

- **Production-source pass:** Read portions of the current APK forensic extractor, DEX analyzer, data models, CycloneDX writer, source validator, OSV confidence/source propagation, and reference-feature transaction/write path. Confirmed code semantics behind the central evidence-boundary claims.
- **Review note:** The Gradle validator checks coordinate/version membership in one supplied dependency tree and explicitly disclaims proving bytecode completeness. APK forensic flags are heuristics. Native `.so` files are hash-only. OSV authority is bounded by component/version confidence and can be downgraded by source validation.
- **Static issue:** In the feature-store builder, old feature rows are cleared before all referenced DEX paths are verified. A later missing file returns failure without an explicit rollback. This is a potential failure-path defect, not proof of historical database damage; no test was run.
- **Remaining in this pass:** Full `matcher.py`, `report.py`, `cli.py`, `reference_features.py`, and all tests/diagnostic modules are not yet fully reviewed.

- **Matcher review:** Inspected core scoring, selection, ambiguity and output filtering. Reference-feature coverage and opcode cosine are combined in a normalized weighted score; sibling-version-unique features inform version decisions. Identity and version labels are separate, near-ties can stay ambiguous, and one-version catalogs do not automatically earn exact status.
- **Promoted controls:** Composite family shortlist is a pre-score pruning step (not accuracy uplift); the literal/context reranker selects only among existing candidate versions under strict thresholds. Both are currently default-enabled with disable flags. This is checked against current source and tests; historical evaluation totals still depend on omitted artifacts.
- **Status:** Matcher core partly reviewed; exhaustive review of every branch, diagnostic, report/CLI path and test is still pending.

- **Historical-documents pass:** Read root guidance, README, TASKS chronology, architecture proposal and decision log, plus the paper-to-implementation traceability and selected final evaluation summaries. Found substantial stale early planning text: it still describes a research-phase project/future prototype and target architecture that differ from the implemented tool and the current final theses.
- **Use policy:** Retain early documents as rationale and chronology, but prefer current source/code, dated frozen artifacts, and later reconciled theses/evaluation records for present-state claims. `TASKS.md` currently has an in-progress combined-results entry whose machine-readable files are not retained in this ZIP; do not treat that historical status as reproducible now.
- **Remaining:** The 222-file evaluation archive, scripts, tests, and non-code evidence/output directories are not fully read. Review is continuing with current-final artifacts before older iterations.

- **Core tests inspected (source only):** Read extractor, DEX helper, reference-feature, matcher (first 568 lines), source-validation, SBOM and vulnerability tests. They mostly use synthetic APK ZIPs, mocked DEX/network behavior and temporary SQLite data. They establish code contracts, not real-APK evaluation reproducibility.
- **Coverage boundaries:** Source-validation tests check parsed Gradle resolved rows; SBOM tests assert serialized fields; OSV tests use mocked responses. `test_reference_features.py` covers only discovery and successful feature storage and contains no missing-later-DEX rollback assertion. This aligns with a potential uncovered failure path, not an observed runtime failure.
- **PDF method:** Because the primary benchmark PDF is two-column and pypdf text order is imperfect, rendered and visually inspected page 1 and results table page 9. Rendering warned about missing font names but the pages were legible; temporary render files were cleaned up.
- **Remaining:** Continue through matcher tests, other tests, report/CLI, experiment modules, scripts and historical evidence artifacts. No test execution.

- **Matcher tests:** Finished source review across the matcher suite. Tests cover reference-based scoring, inert features, identity/version confidence separation, ambiguity, single-version caps, POM-supported decisions, app-era consistency, and scoped artifact family suppression. Most use hand-built candidates/synthetic SQLite rather than real APK evaluation.
- **CLI/report pass:** Traced command groups and `generate_final_report`: deterministic matcher builds components/SBOM; optional AI/R8/version-band/Phase 5 evidence is attached on opt-in as report text/JSON (plus a report-only metadata marker where applicable). Integration tests assert unchanged selected component versions and source-validation caveats. Obfuscation diagnostics can repeat DEX analysis.
- **Evidence boundary:** These source tests show intended behavior on their fixtures, not universal runtime equivalence across real APKs. No commands, tests, or experiments were executed.
- **Remaining:** Continue through report tests/modules, all remaining tests, experiment algorithms, scripts and time-ordered evidence reports.

- **Experiment reports cross-check:** Re-read current Phase 4/5 R8, source-known/version-band v2/v3, and the two promoted-feature decision records. Broad multi-scale scoring rejected after regressions; the narrower Phase 5 remains opt-in despite zero triggered regressions in its retained diagnostic; source-known 565/582 fixability yields zero APK-only fixes; deep expansion chose the wrong old alpha; literal/context promotion narrowed after broader gates showed regressions; composite pruning is supported as candidate reduction with selection-preservation, not accuracy gain.
- **Report-only contract:** Phase 5 report test keeps baseline SBOM version while rendering the suggestion. Current source and fixture support the authority boundary; raw report outputs/APK DB set are absent, so retained performance counts are not reproduced.
- **Examiner corrections:** Current extractor confirms no APK-signature inspection; only successfully parsed DEX is used; ZIP resources/assets are not DEX literals. Final compiled report PDF is documented as stale relative to later source corrections.
- **Status:** Decision rationale has been cross-checked against some primary reports/tests; remaining experiment and test families still require study. No commands/tests/experiments run.

- **Auditability improvement:** Created `papers/PROJECT_FILE_REVIEW_REGISTER.csv` from the current recursive workspace inventory. It records 1,714 other file paths and 303 directories, with separate inventoried / partial / full states and a note that full content review does not equal empirical reproduction. At capture, 10 files were full, 51 partial and 1,653 inventoried only. The register omits its own self-row and is time-stamped by this session; the current tree has one additional study-register file. The earlier index snapshot predates/under-counts a paper-study artifact, so the live register now controls file-path accounting.
- **Status:** The register shows the remaining breadth explicitly; most files are still only inventoried. Continue content review and update status rather than claiming completion.

- **Literature synthesis audit:** Read the full state-of-the-art narrative and per-paper impact note, plus portions of the tools table and structured JSON overview. These early documents propose methods and evaluations that did not become the current system (Bayesian scoring, LibMD multi-scale fusion as core, LibAttention first-pass filtering, TPL-Benchmark evaluation). They also use “realistic ceiling” language and cross-paper rankings without enough protocol qualification. Preserve them as design history; verify related-work facts against each primary paper and do not present proposals as completed implementation.
- **Review state:** Updated the file register for the read/partial-read distinction. No tests or experiments were run. The full project review remains active; primary literature verification and most file content reviews remain outstanding.
- **Thesis cross-check:** Inspected chapter maps and selected RQ/conclusion passages. Confirmed the Master thesis is an evidence-trust framework synthesis, while PFE is the implemented static APK-to-CycloneDX system evaluation. PFE's retained denominator claims are 927/1,837 emitted Maven versions across 102 source-validated APKs that emitted Maven rows; plus four no-Maven-signal controls; and 927/12,082 against the full source dependency denominator. These are historical thesis figures, not independently reproduced from this ZIP. Full thesis reading and final source/PDF reconciliation remain outstanding.
- **PFE Chapter 6 read:** Read the full implementation/evaluation chapter and reconciled its protocol, denominators, AI/R8 authority gates, negative experiments, and threats with the retained evidence snapshot, table-generation script, current data directories, and current feature-store source. The core metrics are explicitly lane-qualified in the thesis, but their raw JSON/results and reference DB are absent from this ZIP; `.git` is also absent, so the cited snapshot commit cannot be checked. The 275-test and compileall results are dated historical results, not rerun here.
- **Discrepancy logged:** Chapter text describes feature storage as transactional, while current code clears old rows before verifying every DEX path and returns a failure normally on a missing file; this may commit cleared/partial rows. Static code inspection only, no failure was executed. Review/update the code evidence and test coverage before using an atomicity claim.
- **Status:** Chapter content review is complete, empirical reproduction is not. Retained dashboard images exist but cited source report outputs are missing. No tests or experiments were run.
- **Master framework chapter:** Read the complete 804-line evidence-trust chapter and checked its scope against the current runtime with a targeted source/test search. The formal claim tuple, E0-E5 levels, quality dimensions, conflict/abstention classes, confidence caps, lane policy, and monotonic vulnerability authority form a proposed analytical framework; the trust equation is conceptual and explicitly not calibrated or Dempster-Shafer inference. Runtime implements some corresponding confidence/ambiguity/source/report-only mechanisms but not a formal claim schema or E-level lifecycle. The PFE case study tests whether outcomes can be represented without authority drift; it does not establish calibration, completeness, or inter-rater agreement. No tests/experiments were run, and case-study figures remain historical due to missing raw artifacts.
- **Feature-store verification:** Read the complete 696-line `reference_features.py` and entire three-test feature-store suite. Tests cover discovery filtering/offset and a successful synthetic write only; no failed replacement/rollback test exists. Static flow shows component upsert and child-row deletion occur before DEX-path validation; a missing DEX returns normally from the inner function, so the outer sqlite context commits instead of rolling back. Python sqlite3 context-manager documentation confirms commit-on-normal-exit, rollback-on-uncaught-exception. This substantiates the failure-path risk and contradicts the thesis's unqualified transactionality statement, but it does not show an actual failure run or historical DB damage. No code was changed and no tests were run.
- **AI/R8 evaluation aggregator:** Read the complete final-evaluation aggregator, wrapper, two-test suite, and retained final-evaluation/integration-gate Markdown. Tests synthesize input JSON and prove aggregation/file writing only, not model scores, grouped split quality, or historical smoke. Missing JSON is silently loaded as `{}`, so the builder does not fail fast on missing required evidence. The report-only predicate checks unchanged components, semantic SBOM, vulnerability labels, and the report-only flag. Retained report distinguishes raw SBOM hash changed from semantic SBOM content unchanged; manuscript claims should stay at semantic component/version/vulnerability authority. AI metrics remain project-derived report-action classification, not external APK detection results; the raw-opcode model is below its simple baseline. The underlying metrics/corpus/smoke JSON files are missing here. No tests or experiments were run.
- **AI/R8 integration gate:** Read the full gate decision source, wrapper, four-test suite and retained report. Report-only readiness uses model thresholds plus upstream JSON claims that smoke outputs/sections remained unchanged; the code does not rerun the smoke. The test suite covers MVP-safe token exclusions, tiny corpus metadata, a negative decision, and serialization, but not the positive strict-candidate path or promotion-flag contradictions. The decision function ignores strict-gate `production_promotion` and `default_matcher_unchanged` when deciding candidacy; if other inputs turn positive, `matcher_authority_ready` may become true as a candidate even though `sbom_or_cve_authority_ready` is hard-coded false and the reason still requires a live regression suite. Current historical output has zero eligible rows and stays blocked. Underlying JSON absent; no tests/experiments run.
- **Structured-token corpus:** Read the full token-corpus builder and DL prototype test. Full tokens include raw source/candidate versions, coordinate, 17 features and diagnostic context. MVP-safe removes those direct values/context and several source flags but retains `row_source` categories, group/artifact tokens, selected matcher features, candidate-version shape and R8 flag. Labels are themselves derived from project recall/source-validation/Phase-5 fields. Case split is deterministic 70/10/20 by sorted case ID, not coordinate/project holdout; vocabulary is built across all rows before split (transductive feature vocabulary). Tests use 12 synthetic rows and do not detect row-source/context proxies or cross-case coordinate overlap. Transformer scores measure project-label report-action classification, not library/version detection or external generalization. No tests/training run.
- **Phase 6A assistant full read:** Read all 1,241 lines of assistant source, its full seven-test suite, and the diagnostics report. Dataset merges five project-evidence row families; labels are rule-generated; Random Forest is case-split, not stratified/coordinate-heldout; scores/probabilities are internal report-action results, not APK detection performance. Found direct target leakage: transparency boundary row's `is_boundary_or_limitation` feature is set from the already-derived `boundary_do_not_suggest` label. It is a major feature (0.217 importance); no-context-flag ablation macro-F1 drops 0.708->0.564. Full Transformer also receives label-generating context (recorded above); MVP-safe omits direct source/version/context fields but retains row-source categories that constrain label groups. Fallback suggestions copy labels with fixed confidence and are heuristic, not ML predictions. Tests never fit/train the RF or validate historical scores. Raw metrics/model/dataset absent; no tests/model training run.
- **Phase 6B structured Transformer:** Read the complete trainer and both retained reports. Small embedding/position + one-layer Transformer; weighted cross-entropy; fixed epochs, no early stopping/best-validation checkpoint restore. Full profile final-epoch test is 0.977 macro-F1/.992 accuracy after validation peaked epoch 2 and declined by epoch 3; MVP-safe five-epoch report is .882/.907. This is a project-label token classifier, not Smali pretraining or APK detection. No trainer test exists (DL test covers token corpus only). Rechecked that both corpus JSONs, metrics JSONs, and `.pt` model are absent. No model/test execution.
- **Raw-opcode corpus and Transformer:** Read the complete corpus builder, trainer, four-test suite, and both retained Markdown reports. The corpus uses APK-filename/path-derived seven-way profile/role labels, 120 capped nonempty method sequences per APK, opcode-name tokens truncated to 126 plus special tokens/padding, and an all-row vocabulary of 135 tokens. It comprises 14 APKs / 1,680 method rows. Test holds one complete APK case out per label (840 rows), but validation is a deterministic row sample from train APK cases, not an APK-heldout validation set. The final-epoch Transformer test macro-F1 is 0.1098 vs 0.1281 for opcode-count logistic regression (both accuracy .1464), so the retained conclusion is non-promotion. This is APK/profile triage rather than component/version detection. Four synthetic tests do not execute the corpus/trainer or validate group isolation. The corpus JSON, metrics JSON, and model checkpoint are absent, so these historical values were not regenerated; no tests/training were run.
- **Register update:** Marked the two raw-opcode reports, two scripts, and test file fully read. Current file review totals are 36 full, 53 partial, and 1,625 inventoried; 303 directory rows remain inventoried. The full-project review remains in progress.
- **APK inspection and DEX extraction:** Read both modules completely. `apk_extractor.py` inventories archive/hash/manifest/native metadata and heuristic packaging indicators; `dex_analyzer.py` parses standard `classes*.dex` files into package/class/method, opcode and derived structural features. Nonstandard DEX-like files may be reported but are not sent to the normal DEX parser path. Manifest fields are limited; native libraries are file/hash records, not native upstream identities; string/API and structural features depend on parser output and heuristic definitions. Marked both source files full; source review only, with no APK processing/tests executed.
- **Source validation:** Read the complete parser/validator and existing synthetic tests. It compares `group:artifact` and exact resolved-version strings against provided Gradle dependency-tree rows, with confirmed/mismatch/missing and extra-candidate outputs. This is source-tree concordance, not APK completeness or source-to-bytecode equivalence. Multiple resolved versions grouped under one coordinate can make any matching emitted version “confirmed”; preserve source variant/row context. Synthetic tests cover basic resolution and three statuses, not all Gradle formats or multi-variant completeness. Source file marked full; no tests/real validation run.
- **Matcher source (partial continued pass):** Inspected orchestration, weighted score, identity/version confidence logic, version rerankers and uncertain-candidate filtering. Default weighted similarity uses package/class/method/opcode/dependency/literal/version-unique features; API and opcode n-gram weights are zero. Score is a normalized heuristic, not probability. Selection may deviate from raw score via gated unique features/context, POM support, and app-era coherence; identity and version status are separate, with a cap for single-reference version claims. Matcher remains partial: shortlist/family policies, other helper paths and full test mapping remain; no tests were run.
- **Composite family shortlist and tests:** Inspected matcher family-level pruning and the report-backed simulation gate, read the simulation policy/scoring/rescue portion, and read all three synthetic tests. Runtime retains every version in a retained coordinate family; scores complete family evidence, retains within 0.10 of best, and rescues by dependency/literal/combined class support. This reduces reference search space but does not directly improve version selection accuracy. Synthetic tests exercise policy decisions; absent report JSON prevents historical source-retention numbers from reproduction. Simulation source is partial, tests full; no tests/experiments were run.
- **Matcher follow-up:** Confirmed hard-coded Okio, OkHttp, and selected Lifecycle variant families; Compose version coherence across four named Android artifacts; and independently supported POM coherence. Scoped Lifecycle logic can promote certain uncertain target variants to low-confidence candidates. Package-overlap SQL filter is opt-in/off by default and can limit reference versions by shared-package ranking, unlike the enabled family shortlist that retains the complete band. Matcher and its 30-test suite remain partial-read; no tests run.
- **CycloneDX and OSV path:** Reconfirmed complete SBOM model/builder/tests, then fully read OSV implementation and tests. Output is CycloneDX 1.5 with direct APK-to-emitted-component edges; native libraries remain hash-only file components. OSV queries detected Maven coordinate/version pairs, confidence-gates hits into confirmed/potential, and source mismatch/missing/no validation downgrades vulnerable results to potential. Detail enrichment is best-effort; batch pagination tokens are retained but not followed. Mocked tests cover these mechanics only. No test/network scan run.
- **Report orchestration:** Read the complete high-level report-generation path; `report.py` remains partial. It reruns DEX analysis for obfuscation diagnostics, adds optional experimental evidence as report annotations, writes SBOM and reports, and optionally calls OSV/source validation. Diagnostic analysis errors are swallowed as missing diagnostics; OSV query errors propagate. Source validation is opt-in. No end-to-end report generated.
- **Report evidence attachment follow-up:** Inspected experiment, AI, router, structural-gate and DL-status JSON loaders plus focused report tests. Data are attached from supplied JSON, not recomputed; case matching may be substring-based and some loaders include rows by detected coordinate, so report annotations are not automatically APK-specific ground truth. Verified version-band option adds two diagnostic metadata properties to CycloneDX while leaving selected component versions unchanged; phrase semantic component/version authority stability, not unchanged raw SBOM bytes. Hybrid AI attachment test shows it does not feed SBOM component selection. Report source/tests remain partial.
- **Report uncertainty/risk logic:** Inspected current obfuscation-risk and version-uncertainty functions. Both are deterministic report summaries over existing archive indicators/matcher decisions; risk is a hand-weighted heuristic, and uncertainty categories annotate but do not alter decisions. Their counts should not be presented as calibrated probabilities or independent error counts. Report module remains partial.
- **Matcher completion audit:** Finished content review of all matcher implementation functions and all 33 test functions/fixtures; updated both paths to `full` in the register. Rule tests use synthetic feature sets/SQLite records; they do not run APK extraction or reproduce historical results. Corrected the earlier interim “30 tests remain partial” note: current source has 33 test functions, fully read but not executed. Overall project review remains active.
- **Implementation handbook cross-check:** Read all six implementation handbook pages and compared them with current source. Identified stale/broad wording: composite shortlist described as optional though enabled by default (disableable); analyzer said to process all DEX although standard paths only are analyzed; reference-feature transactionality claim conflicts with the normal-return failure path; version-band diagnostic metadata changes CycloneDX metadata even though component/version authority does not change. Source-validation denominator guidance is consistent. Marked all six pages full; no tests/experiments run.
- **Obfuscation diagnostics:** Read all of `obfuscation.py`. It provides separate hand-coded indicators and fixed thresholds for short names, package flattening, class/method coverage loss, low structural evidence, low-confidence component share, archive/protector hints, resource symptoms, and collapse/merge patterns. These are explanation heuristics, not calibrated obfuscator detection; large-caller concentration is not measured. No dedicated obfuscation test exists; extractor/report tests assert visibility and report-only behavior rather than threshold accuracy. Marked implementation full; no tests run.

## Report rendering and presentation audit (partial)

- Followed `generate_final_report` through component selection, report-only evidence loading, matches JSON, CycloneDX writing, optional OSV/source validation, and JSON/Markdown/HTML serialization. The report function does not run model training or regenerate the experimental JSON files; those are optional input attachments. Diagnostic DEX analysis is wrapped so its exceptions become missing diagnostics, whereas the optional OSV query path can fail the report call. Output directory creation and successive writes mean a failure can leave a partial set of artifacts.
- Read the complete Markdown and HTML report builders and major table helpers. JSON carries APK, matcher summary, uncertainty, heuristic obfuscation risk, diagnostics, components, OSV, paths and optionally attached experiment evidence. Markdown presents forensic summary, diagnostics, uncertainty, experiment annotations, components, version alternatives, OSV findings and limitations. HTML presents corresponding dashboard sections and escapes dynamic HTML text via `html.escape(..., quote=True)`; static styles/structure are embedded.
- Markdown table interpolation does not escape all dynamic values for pipes/newlines/backticks. This can affect display/structure if APK-derived or external report text contains those characters; distinguish output-format robustness from component-selection correctness. HTML escaping coverage is materially stronger. This was static source review, not a security test.
- Read the full `test_report.py` contents: 17 tests use synthetic domain objects and temporary JSON fixtures. They assert report sections, serialization, escaping of a `<` in APK path, uncertainty/risk presentation, optional evidence attachment, and that report-only evidence leaves selected component versions unchanged. They do not validate Markdown adversarial delimiters, historical report outputs, or real APK end-to-end results. Test bodies were read but not executed.
- `report.py` remains `partial`; the full contents of `tests/test_report.py` are now read and marked `full`. Experiment builders and generated outputs remain separate evidence sources to review. Overall repository review remains active.

### Specialized report renderer follow-up

- Read both Markdown and HTML renderers for the R8 Phase 5 and version-band evidence. Phase 5 presents dataset counts and matching triggered rows; version-band evidence presents AppCompat/Core old-version-steal and Lifecycle public-vs-Android family downgrade annotations. Renderer text explicitly labels these report-only and states selection/vulnerability authority is unchanged. Those source claims do not establish the quality or correctness of the underlying experiment; the attached JSON remains the evidence source.
- Renderers provide a dataset-context explanation when no triggered row matches the current APK, so presence of an experiment section is not itself per-APK support. Some Markdown dynamic table cells are escaped through `_markdown_cell`, while other strings are interpolated directly; table rendering can be malformed by delimiter/newline content. HTML values in the inspected builders pass through `_html`.
- Read the test fixtures/helpers at the start of `tests/test_report.py`; they use hand-built APK/matcher records and canned experiment JSON. No test was run. Remaining report review includes the full specialized minified-confidence and AI/hybrid renderers and cross-checking their inputs with their experiment producers.
### Report-only AI/minification rendering and evidence-producer checks

- Read the remaining Markdown/HTML renderers for minified-confidence policy, hybrid router/structural-gate/Phase 6A/6B assistance, and AI R8 suggestions. They are presentation layers over supplied JSON and repeatedly declare themselves report-only; hybrid says the weighted matcher remains SBOM authority, and DL production wiring is shown as disabled/status metadata. The UI summarizes dataset counts alongside any rows matching the report, so these quantities must not be conflated.
- Cross-read `scripts/build_r8_minified_confidence_report_evidence.py`: it aggregates the optional policy section from four pre-generated report JSONs; for each suggestion/blocked row it compares the matching detected-component version to the policy baseline, treating any inequality (including no component found) as a default-selection change. It labels the aggregate clean only when the selection guard holds, every report has policy evidence, rows are report-only, and at least one suggestion exists. It summarizes reporting evidence, not policy accuracy.
- Cross-read `scripts/build_hybrid_ai_production_report_evidence.py`: it aggregates prebuilt router, ML, DL and structural-gate JSON. Its “representative report context” is synthesized from the first P1 router row (or first row), constructing a case-id `.apk` string and a one-component fixture, then asking the report loader what matches. That is an integration/payload-shape demonstration, not a real-APK end-to-end accuracy evaluation. The script reports DL metric fields while preserving disabled production wiring.
- Confirmed live `data/results/` currently contains only `.gitkeep`; generated JSON/SQLite/APK outputs are absent from this checkout. Many retained `docs/evaluation/*.md` summaries exist, but are secondary textual records. Historical numeric claims remain documentary until the underlying inputs and generated artifacts are available.
- `report.py` remains partial pending final review of all helper paths and its source-to-producer trace. `tests/test_report.py` is fully read; tests were not executed. The two evidence-builder scripts were sampled for this pass and remain inventoried until completely read. No test, report generation, or experiment was run.
- Completed content review of eport.py helpers/loaders/renderers and all 17 functions in 	est_report.py. Marked both full (not executed). Current register: 53 full, 46 partial, 1,918 inventoried entries (1,615 files and 303 directories). Report evidence-builder scripts and underlying experiments remain to be traced.

## Thesis source/PDF reconciliation (partial review)

- Read the thesis directory README, both editable `main.tex` files, both metadata and title-page files, and the master introduction/background chapters. The Master thesis text says it is a literature-synthesis/framework proposal and does not implement a second detector; the July 6 PDF omits the chapter that specifies/evaluates that framework. Its framework distinguishes claim identity, version, vulnerability authority, provenance, transformation exposure, evidence independence, reference coverage, validation class, conflict and abstention.
- Compared the current source with the named PDFs. The June 21 named Master/PFE PDFs visibly show placeholder date/president/examiner fields and internal creation dates of June 22. Later July 6 output PDFs have completed cover metadata. Both named June pairs and both July output pairs are same-byte duplicates within each pair, not independent builds.
- Current Master `main.tex` omits the framework chapter and Appendix A. The later July 6 48-page PDF follows that chapter set despite an abstract claiming the framework contribution; the older June 22 74-page PDF and chapter5 checkpoint ZIP include them. README-referenced `main.pdf` files are absent, though later copies are under `output/pdf/`.
- PFE `main.tex` includes chapters 1–7 and Appendix A; the July 6, 124-page output PDF carries completed metadata and includes these sections. The older June 22 138-page PDF has placeholders. Checkpoint ZIPs have differently sized chapter-6 snapshots; full version comparison remains.
- Extracted text from the two named PDFs (74-page Master, 138-page PFE; selectable text on all pages) and visually inspected their cover pages. PDF content review beyond cover/abstract/contents and targeted chapter-4 checks is partial; chapter/source reconciliation continues. No compilation, test, or experiment was run.
- Thesis pass register update: 62 full, 51 partial, 1,904 inventoried entries.

### Master state-of-the-art chapter (initial partial read)

- Began `ch03_state_of_the_art_taxonomy.tex`. It says its corpus uses 15 locally full-text-verified Tier A studies, with Tier B as supplementary search coverage; it avoids a cross-paper leaderboard because tasks, data, obfuscation settings and ground truth differ. Its taxonomy groups work into namespace/metadata heuristics, profile/signature matching, graph segmentation, coarse-to-fine methods, version-discriminating semantics, learned representations, and empirical assessment/benchmarking. The reviewed work’s outputs generally are not provenance-rich CycloneDX/SPDX SBOMs.
- The chapter’s opening paragraph currently has an apparent source defect: `Fields not reported by a Tier A publication are treated asSearches combined...` joins an unfinished phrase to the search-method paragraph. It may be a source/compiled-text merge error; verify against PDF and surrounding sources before treating as an editorial artifact. The chapter remains partial; only its opening technique taxonomy and start of evidence taxonomy have been read.
- Source/PDF findings above are directly observed. Master title-page source metadata includes a date and jury names while its sampled PDF cover visibly has placeholders. Current Master `main.tex` omits framework chapter/Appendix A that appear in the PDF. The PFE source includes all chapters and appendix, but its cover metadata also conflicts with the sampled PDF. `main.pdf` files referenced in README are absent. This is a reproducibility/provenance issue for the thesis artifacts, not evidence that the implementation or cited evaluation data are wrong.
- Register after beginning the state-of-the-art chapter: 62 full, 52 partial, 1,903 inventoried.

### Master state-of-the-art and review-protocol completion

- Completed `ch03_state_of_the_art_taxonomy.tex` and Appendix A. The review protocol is explicitly version 1.0 frozen on 21 June 2026 after iterative seed-corpus assembly; it disclaims retrospective raw database query/result/dedup counts and does not claim an exhaustive selection flow. Its four concept blocks cover Android/APK/DEX, component/SBOM, recovery tasks, and transformation/version/vulnerability terms. It defines inclusion/exclusion, Tier A full-text verification, Tier B supplementary records, Tier C contextual authorities, 12 extraction dimensions, and eight quality questions scored 0/0.5/1. It explicitly keeps incompatible metrics, task levels, and original vs independent evaluations separate.
- The seed table has 20 units: 15 Tier A studies (S01–S13 plus S17–S18) and five Tier B items (LibRadar, Libra, LibMD, LibScope, ObfDetector). UniBOM is Tier A but adjacent evidence only, not Android exact-version authority. TPL-Benchmark and UniBOM are dated promotions on 21 June. Quality totals range 5.5–8.0/8; these are reporting/reproducibility quality, not scientific merit.
- The SOTA synthesis spans seven technique families and evidence-source/transformation/evaluation taxonomies. It warns that reference profiles bound recognition, inlining/shrinking threaten adjacent-version distinctions, and most studied systems do not emit provenance-rich standard SBOM claims. It states the gap narrowly for the reviewed corpus: no verified reviewed study unifies evidence provenance, coverage, transformation risk, ambiguity, validation class and permitted vulnerability interpretation. TPL-Benchmark’s 60.15% library F1 and LibHunter’s 76.48% version recall are tied to the benchmark’s compatible slice, not a universal ceiling.
- Correction: the apparent SOTA opening splice was caused by truncated concatenated tool output. Direct inspection of the source and July 6 PDF shows a complete sentence: unreported Tier A fields are recorded as not reported rather than inferred. Appendix A uses `NR` as the extraction-table code.
- Register after reading SOTA and protocol: 64 full, 51 partial, 1,902 inventoried entries.

- Latest PDF review-count correction: 64 full, 55 partial, 1,898 inventoried entries; four July output PDF copies have been added as partial reviews.

## Historical literature notes and current protocol cross-check

- Finished reading the older May 2026 `papers/state_of_the_art.md`, `papers/data/impact_on_project.md`, and `papers/data/papers_overview.json`; read the first 131 lines of `papers_6-10_analysis.json` (partial). These are valuable records of research direction, but several statements are stronger than the later frozen thesis protocol and implementation evidence warrant.
- The older notes call LibMD the project's most relevant paper and describe its multi-scale CDG, Bayesian scoring, LDG and explicit SBOM pipeline as an MVP foundation, while also admitting exact metrics/full-text evidence are unverified. They recommend TPL-Benchmark as a target and sometimes call 60.15% a “realistic ceiling.” Current thesis protocol places LibMD in Tier B (no locally verified full text) and does not use it for precise claims. Current runtime matcher is a normalized heuristic with explicit rules; the review to date found no calibrated Bayesian version posterior, implemented multi-scale graph engine, or LibMD-derived transitive dependency graph. Treat these early statements as proposal/history, not as description of delivered code or evidence.
- Older notes also state broad unverified claims about ObfDetector (<10% version F1), LibScope, tool resilience matrices, advanced obfuscation, transitive-dependency prevalence, and precise adoption of techniques. Later thesis text limits such claims to verified Tier A or explicitly Tier B context, and avoids a pooled leaderboard. Each quantitative statement must be checked against its local primary PDF and task/denominator before paper use.
- The old `impact_on_project.md` contains replacement-character glyphs (for example the title separator and “Adapt” separator), malformed fragments such as `=10 app threshold`, and `?` where arrows should be. Record this as encoding/editorial damage; do not silently normalize its intended meaning without source comparison.
- Local primary research PDFs are present under `ressources/papers/` for the main Tier A studies (including LibScout, LibD, ORLIS, LibID, LibPecker, LibScan/LibHunter, ATVHUNTER, LibAttention, SAD, Ramirez, both assessments, TPL-Benchmark and UniBOM). Full-text-by-full-text study verification remains necessary; local presence alone does not prove every claim in notes was checked correctly.
- `papers_overview.json`, the older synthesis markdown, and the per-paper impact notes are now content-read and marked full as historical records, not independently validated sources. `papers_6-10_analysis.json` remains partial. No experiments or tests were run.
- Register update after reading the early research notes: 67 full, 53 partial, 1,897 inventoried entries.

### Legacy per-paper extraction and comparison matrix

- Completed the 206-line `papers_6-10_analysis.json` and `SBOM_Tools_Synthesis_Table.md`. The structured extraction includes ATVHUNTER and the systematic assessment, Ramirez thesis, SAD, LibMD, LibScope, Libra, LibAttention, LibScan/LibHunter, LibPecker, TPL-Benchmark, ObfDetector, and UniBOM. These are older project synthesis records; several rows explicitly say evidence/metrics are unverified while elsewhere recommending those methods as the MVP blueprint.
- This is an important chronology distinction: “planned/adapted from” LibMD multi-scale graphs, Bayesian version scoring, LDG, NVD/cve-mcp, or a TPL-Benchmark run describe early design proposals, not implementation evidence. Current code and later thesis sources control the description of what was built. The Master review protocol's Tier-B rule supersedes the old table's confident “only explicit SBOM tool/most relevant” framing for precise academic claims.
- The old comparisons state that tools have non-comparable datasets and protocols, but also present pooled performance rankings, “best/current SOTA,” a universal “realistic ceiling,” and obfuscation resilience matrices. This is internally inconsistent and the later thesis correctly narrows those claims. The local primary papers should adjudicate each surviving comparison; do not copy the tables directly into the paper.
- All content in these two files was read; neither their factual claims nor the referenced external papers were fully validated in this pass. Marked both full as historical project records, not validated research evidence. No tests or experiments were run.

## 2026-09-29 — Continued deep project study: primary papers and decision ledger

- Objective: continue the evidence audit before drafting the implementation/evaluation paper.
- Read in full: TPL-Benchmark, UniBOM, SAD, and LibHunter primary PDFs; the experiment decision ledger; controlled evaluation; MVP results summary; Phase 5 R8 trigger diagnostics; and K-9 blocker diagnostics.
- Key conclusions: TPL-Benchmark’s 60.15% LibPecker F1 is candidate-set and subset-specific; UniBOM is adjacent SBOM workflow evidence without Android exact-version ground truth; SAD demonstrates stricter version-level accounting and transformation-specific limits; LibHunter motivates R8 inlining/CallSiteOptimization stress tests but uses controlled, tuned datasets. Project failures show why global R8 blends, generic recency, broad metadata scoring, and global signal weights were rejected or kept diagnostic.
- Reconciled caveats: controlled perfect scores apply only to generated fixtures; R8 candidates are low-confidence; the expanded 72-fixture/84-version snapshot is historical and raw generated artifacts are absent; K-9 is source-validated partial after a validation-only rescue, not clean evidence.
- Files changed: `papers/PROJECT_FILE_REVIEW_REGISTER.csv`, `papers/PROJECT_STUDY_INDEX.md`, and this log. No implementation, tests, experiments, or generated results were changed or rerun.
- Next action: continue the remaining primary Android-paper and source-artifact audit, then build the state-of-the-art evidence matrix and paper-ready claim contracts.

## 2026-09-29 — Evaluation dashboards reconciled and evidence matrix consolidated

- Read `docs/evaluation/APK_TYPE_EVALUATION.md`, `docs/evaluation/THESIS_EVALUATION_TABLES.md`, and `docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md`.
- Confirmed the paper-ready separation of evaluation lanes: 72 controlled fixtures with 84 expected Maven versions; five clean source-validated real APKs with 47/47 emitted-version confirmation; 97 partial source-validated real APKs with 880/1,790 confirmation; and 102 source-validated real APKs with 927/1,837 confirmation (50.5% of emitted rows).
- Confirmed the denominator limitation: the coverage-first dashboard reports 12,082 source dependency rows across 106 cases, 18.4% coordinate presence in the shared reference DB, 10.2% exact-version presence, and 927 exact emitted confirmations (7.7% of all source rows). The paper must not call emitted confirmation full dependency recall.
- Recorded boundary categories for native-heavy, hidden-code, no-Maven-signal, and report-only cases. Native libraries remain hash-only in the MVP and are excluded from Maven exact-version accuracy metrics.
- Added `papers/PAPER_EVIDENCE_MATRIX.md` as the working claim-contract table. It links each planned quantitative statement to its evidence source, unit, permitted interpretation, and limitations, and keeps related-work metrics tied to their original datasets and protocols.
- Current register verification: 78 full, 48 partial, and 1,891 inventoried entries. No tests, experiments, or generated outputs were run or modified.

## 2026-09-29 — Initial State of the Art drafting artifact

- Created `papers/STATE_OF_ART_DRAFT.md` as a venue-neutral working draft for Section 3.
- The draft follows the approved structure: review scope, identity detection, version ambiguity, transformations, SBOM/vulnerability integration, evaluation practice, and research gap.
- Every quantitative or comparative statement is bounded by the evidence matrix: original dataset and metric conditions are preserved, and no incompatible percentages are presented as a leaderboard.
- The draft explicitly distinguishes the project’s weighted evidence fusion from the reviewed graph/opcode/structural methods, and keeps R8/AI behavior diagnostic or report-only unless separately validated.
- Remaining prerequisites before manuscript integration are bibliographic metadata verification, citation-style conversion, implementation-snapshot cross-checking, and reconciliation of the 102/106/110-case source-coverage denominators.

## 2026-09-29 — Proposed Approach drafting artifact

- Created `papers/PROPOSED_APPROACH_DRAFT.md` as the first Section 4 draft.
- The draft describes the implemented APK/DEX-to-reference-profile workflow,
  weighted evidence fusion, separate identity/version decisions, ambiguity and
  provenance handling, CycloneDX output, and downstream OSV qualification.
- It explicitly excludes unsupported claims: the matcher is not described as
  Bayesian or probabilistic, native `.so` files remain hash-only, and R8/AI or
  structural experiments do not silently become default authority.
- Final manuscript work still requires a frozen implementation/run manifest,
  reference-database metadata, verified CLI defaults, and an architecture figure.

## 2026-09-29 — Source-case denominator reconciliation frozen

- Traced the 102/106/110 counts through `papers/PROJECT_STUDY_INDEX.md`,
  `docs/thesis/FINAL_V2_RESULTS_SECTION.md`, the examiner review, and the
  thesis evaluation tables.
- Frozen mapping for the paper: 102 Maven-emitting source-validated APKs are
  the `927/1,837` emitted-version confirmation set; four additional
  source-validated no-Maven-signal controls expand the source-tree population
  to 106 and belong to the source-known upper-bound and `12,082`-row coverage
  analyses; four further limitation examples belong only to the 110-case
  transparency inventory.
- Updated `PAPER_EVIDENCE_MATRIX.md`,
  `implementation_evaluation_paper_plan.md`, and `STATE_OF_ART_DRAFT.md` to
  preserve this mapping and remove the unresolved-denominator wording.
- The raw row-level exports and reference database remain absent from this
  checkout, so the final paper must cite the retained snapshot and disclose
  that the figures were not independently regenerated here.

## 2026-09-29 — Citation metadata checkpoint

- Created `papers/LITERATURE_CITATION_REGISTER.md` for the studies used in the
  State of the Art draft.
- The register links each working citation key to the local primary PDF and
  the project metadata record, while explicitly marking DOI, publisher URL, or
  complete-author verification as pending where the current files do not prove
  it.
- This prevents the older synthesis tables from becoming the bibliographic
  authority during manuscript drafting.

## 2026-09-29 — Section 5 evaluation drafting artifact

- Created `papers/IMPLEMENTATION_EVALUATION_DRAFT.md` covering RQ1–RQ4,
  implementation scope, experimental lanes, dataset membership, metric
  definitions, constrained upper-bound interpretation, OSV demonstrations,
  and threats to validity.
- The draft preserves the frozen denominator mapping: 102 Maven-emitting
  cases for `927/1,837`, 106 source-tree cases for the `12,082`-row and
  source-known analyses, and 110 cases for transparency-only boundaries.
- It explicitly labels all result numbers as retained historical snapshots
  because raw exports, reference DB, source trees, and run manifests are not
  present in this checkout.

## 2026-09-29 — Figure and table specification

- Created `papers/PAPER_FIGURE_TABLE_SPEC.md`.
- Defined four figures and five tables with their purpose, unit, evidence
  source, denominator, lane boundaries, and interpretation rules.
- The specification keeps the 50.5% emitted-row rate, 7.7% source-denominator
  coverage, and 6,772/6,772 constrained result in separate visuals so later
  plotting cannot merge incompatible claims.

## 2026-09-29 — Paper readiness audit

- Created `papers/PAPER_READINESS_AUDIT.md`.
- Mapped the supervisor structure, literature, implementation, research
  questions, evaluation lanes, denominator mapping, upper-bound result,
  vulnerability workflow, threats, visuals, reproducibility, bibliography,
  and final numerical verification to authoritative evidence and remaining
  actions.
- The audit concludes that Sections 2–5 are ready for bounded working-paper
  drafting, while submission-ready Results and independent reproducibility
  remain pending raw result artifacts, reference DB/source exports, run
  manifest, and final bibliographic verification.

## 2026-09-29 — Manuscript scaffold consolidation

- Created `papers/MANUSCRIPT_SCAFFOLD.md` with the supervisor-approved six
  sections, contribution framing, section links, required numerical wording,
  and final integration checklist.
- The scaffold makes the current state explicit: Sections 3–5 have working
  drafts, Section 2 has a source-grounded outline, Section 1 is intentionally
  deferred until results are frozen, and Section 6 must not introduce new
  evidence.
- Current register verification after this artifact: 83 full, 48 partial, and
  1,891 inventoried entries.

## 2026-09-29 — Introduction drafting artifact

- Created `papers/INTRODUCTION_DRAFT.md` covering context, problem statement,
  bounded state-of-the-art motivation, approach overview, contributions,
  exclusions, and paper organization.
- The draft keeps the central distinction between component identity, exact
  version evidence, and vulnerability interpretation, and avoids unsupported
  “first” or universal-accuracy claims.

## 2026-09-29 — Paper-artifact consistency sweep

- Searched all paper artifacts for stale denominator language, conflicting
  counts, and pre-draft status text.
- Updated `PAPER_WRITING_RULES.md` and the plan to use the reconciled 106-case
  source-tree scope for `927/12082`, while keeping the 102-emitting and
  110-transparency layers separate.
- Re-read the full plan and writing rules and promoted both register entries to
  full review. Current register verification: 86 full, 46 partial, and 1,891
  inventoried entries.

## 2026-09-29 — Final thesis-package evidence reconciliation

- Fully read the final report readiness package, final v2 results section,
  paper-to-implementation traceability matrix, and examiner review.
- Added the v2 database size, constrained lane conditions, 5,238-row source-gap
  taxonomy, exact rejected-R8 regression counts, and thesis bibliography audit
  to the evidence matrix and citation register.
- Promoted these four thesis artifacts to full review. Current register
  verification: 90 full, 42 partial, and 1,891 inventoried entries.

## 2026-09-29 — Bibliographic alignment with thesis BibTeX

- Read the primary-paper entries in `thesis/pfe/bib/references.bib` and aligned
  the literature register with verified author lists, venues, years, BibTeX
  keys, and DOI or official URLs for LibScout, LibD, ORLIS, ATVHunter, LibScan,
  LibHunter, LibAttention, SAD, TPL-Benchmark, and UniBOM.
- The literature register now distinguishes verified metadata from the local
  PDF evidence used for technical claims. Remaining citation work is limited
  to selecting the final subset and venue formatting.
- Updated `PAPER_READINESS_AUDIT.md`: bibliography metadata is ready for the
  working draft; only final subset selection and venue-specific formatting
  remain.

## 2026-09-29 — Systematic assessment primary-paper completion

- Read all 24 pages of `ressources/papers/A Systematic Assessment on Android
  Third-party Library Detection Tools.pdf`.
- Recorded its six evaluation criteria, 221-app/59-TPL/2,115-version datasets,
  and findings on package-structure assumptions, multidex and AAR handling,
  partial imports, TPL dependencies, obfuscation, and complementary tools.
- Added the study to `PAPER_EVIDENCE_MATRIX.md` and the State of the Art draft;
  its percentages remain protocol-specific and are not pooled with project
  results.

## 2026-09-29 — Architecture provenance audit

- Read `docs/architecture.md` and `docs/architecture/DECISIONS_LOG.md` in full.
- Recorded that the former is a historical BlockFusion/LibScout proposal,
  while the decision log controls the delivered MVP description. The paper
  must not import the proposal’s basic-block EMD, LibScout baseline, or
  cve-mcp claims into the implementation section.
- Current register verification: 93 full, 39 partial, and 1,891 inventoried
  entries.

## 2026-09-29 — Promoted matcher and experiment-policy audit

- Fully read the composite shortlist, literal/context promotion, guarded
  reference-DB workflow, Phase 5 report evidence, APK-only reranker, and
  candidate-expansion diagnostics.
- Updated the Proposed Approach and evidence matrix to distinguish the two
  guarded default promotions from rejected or report-only R8/version-band
  experiments.
- Recorded zero safe APK-only reranker changes, four Phase 5 report-only
  suggestions, and the singleton/app-specific reference-promotion policy.
- Current register verification: 99 full, 33 partial, and 1,891 inventoried
  entries.

## 2026-09-29 — Current MVP architecture completion

- Read `docs/architecture/MVP_ARCHITECTURE.md` in full and compared it with
  the implementation and decision log.
- Confirmed that it is the current high-level architecture: APK extraction,
  DEX/metadata evidence, reference DB, candidate generation, hybrid matching,
  confidence/uncertainty, CycloneDX, and OSV-first reporting.
- Kept its broad “exact/range/uncertain” wording subordinate to the actual
  implementation statuses (`confirmed`, `candidate`, and `uncertain`) in the
  Proposed Approach draft.

## 2026-09-29 — Thesis evaluation tables and generator completion

- Read `docs/evaluation/THESIS_EVALUATION_TABLES.md` and
  `scripts/build_thesis_evaluation_tables.py` end to end.
- Confirmed that the generated document separates controlled fixtures, clean
  source-validated real APKs, partial source-validated APKs, blocked cases,
  and limitation/boundary cases before producing claim, metric, per-APK, and
  exclusion tables.
- Reconciled the generator’s role filter (`clean-source-validated` and
  `source-validated-partial`) and aggregation logic with the paper’s frozen
  denominators: 72/84 controlled, 47/47 clean, 880/1790 partial, and
  927/1837 overall emitted-version confirmation.
- Confirmed the generator is an evidence-producing script; it was not run in
  this audit, so no experiment or result file was modified.
- Current register verification: 102 full, 31 partial, and 1,890 inventoried
  entries.

## 2026-09-29 — Raw artifact availability check

- Checked the expected raw-data locations before treating the retained tables
  as reproducible outputs.
- `data/source` is absent; `data/results` and `data/reference_db` contain only
  `.gitkeep` placeholders; the machine-readable evaluation exports and frozen
  run manifest are not present in this checkout.
- Kept reproducibility and final numerical verification marked pending in
  `PAPER_READINESS_AUDIT.md`. The paper may use the retained tables as a
  historical snapshot, but must not claim an independently regenerated run.

## 2026-09-29 — Claim-by-claim manuscript audit

- Created `PAPER_CLAIM_AUDIT.md` covering the Introduction, State of the Art,
  Proposed Approach, and Implementation/Evaluation drafts.
- Mapped major claims to implementation files, retained evaluation tables,
  primary-paper audits, and explicit claim contracts.
- Marked the remaining release gates: final citation formatting, frozen
  implementation/database/run identifiers, raw-artifact restoration or explicit
  historical-snapshot wording, single-snapshot figure generation, and a final
  terminology check against accuracy/recall/vulnerability overclaims.

## 2026-09-29 — Integrated working manuscript assembly

- Created `INTEGRATED_MANUSCRIPT_DRAFT.md` as the ordered manuscript layer for
  Sections 1–6.
- Integrated the audited Introduction, State of the Art, Proposed Approach,
  and Implementation/Evaluation content with the supervisor’s required order,
  explicit RQs, result denominators, lane boundaries, and threats to validity.
- Kept the abstract intentionally deferred until the numerical snapshot and
  reproducibility conditions are frozen.

## 2026-09-29 — CLI authority and promotion-path audit

- Inspected the CLI parser definitions for the production report path and the
  guarded matcher options.
- Confirmed that the composite family shortlist and version-unique
  literal/context reranker default to enabled, with explicit disable flags for
  reproducing the pre-promotion baseline.
- Confirmed that R8, version-band, AI, and hybrid-router additions are exposed
  as opt-in report-only paths whose help text states that matcher scoring,
  selected versions, SBOM output, vulnerability labels, and source-validation
  metrics remain unchanged.
- Added this interface-level authority contract to the evidence matrix and
  claim audit. The CLI remains partial in the file register because the full
  89-kB module has not yet been reviewed line by line.

## 2026-09-29 — R8 Phase-4 snapshot conflict identified

- Read the Phase-4 diagnostic summary and compared it with the examiner review
  and experiment decision ledger.
- Found two retained count sets: the ledger/examiner snapshot reports 4 target
  improvements, 6 controlled regressions, 30 real source-validated
  regressions, and 8 clean-real regressions; the expanded Phase-4 diagnostic
  reports 10 potential improvements, 6 controlled blockers, 121 real blockers,
  and 10 clean-real blockers across 1,093 covered rows.
- Both artifacts reject global promotion, but their denominators and likely
  database snapshots differ. Added an explicit reconciliation contract and
  removed any implication that the count sets may be pooled.
- The integrated manuscript now uses the qualitative rejection decision until
  the matching run manifest and database snapshot are restored.

## 2026-09-29 — Thesis framing reconciliation

- Read `thesis/pfe/chapters/ch01_general_introduction.tex` and
  `thesis/master/chapters/ch05_general_conclusion.tex` in full.
- Confirmed alignment on the source-to-binary information gap, identity versus
  exact-version confidence, evidence quality, four evaluation questions,
  emitted-row versus full-dependency recall, uncertainty propagation, and
  future work.
- Promoted both chapter sources to full review in the file register. The paper
  will reuse the bounded concepts and evidence contracts, not copy the thesis
  chapter organization or broaden the claims.

## 2026-09-29 — Promotion-gate test audit

- Read the composite-shortlist, literal/context, guarded-reference, Phase-5
  control-validation, and version-band candidate-expansion tests in full.
- Confirmed that the tests enforce zero reportable drift, complete control
  coverage, rejection of unsafe global reference scope, experiment-only R8
  wiring, and blocking of APK-only reranking when no safe fixes exist.
- Recorded the tests as policy evidence rather than accuracy evidence; they
  were not executed during this audit because the current task does not run
  tests and the referenced raw experiment inputs are absent.

## 2026-09-29 — Default-promotion live and opt-in test completion

- Read the live shortlist, shortlist opt-in verification, and literal/context
  promotion tests in full.
- Confirmed the tests cover family rescue and loss, source-selection
  regression/improvement accounting, smoke/broad/all case selection, complete
  control gates, and filtering of low-support one-feature suggestions.
- These tests complete the available policy-level evidence for the two promoted
  defaults; they do not replace the missing raw evaluation snapshots.

## 2026-09-29 — Negative-experiment test completion

- Read the Phase-4 classification, Phase-5 scoped-trigger, and APK-only
  version-band reranker tests in full.
- Confirmed that regression-risk rows reject global promotion, strong and
  generated controls block the scoped R8 trigger, and APK-only reranking is
  gated by sibling-anchor availability while preserving the default matcher.
- Added these tests as policy evidence. They do not recompute the conflicting
  historical Phase-4 population counts.

## 2026-09-29 — Historical README and instruction audit

- Read the root `AGENTS.md`, `README.md`, and `papers/AGENTS.md` in full.
- Classified the root README and AGENTS description as early project history:
  they contain stale or broader targets such as Bayesian scoring and early
  research-baseline numbers that do not describe the delivered MVP.
- Confirmed that the paper workspace instructions require the supervisor’s
  six-section structure and current evidence contracts. Added the historical
  README caveat to the claim audit so it cannot silently re-enter the paper.

## 2026-09-29 — Foundation completion audit

- Created `PAPER_FOUNDATION_COMPLETION_AUDIT.md` to verify the goal’s explicit
  requirements against current artifacts.
- Confirmed that the source-grounded foundation is ready for section-by-section
  working drafting, while keeping the broader audit active for the remaining
  partial high-value files and the absent raw-artifact/run-manifest package.

## 2026-09-29 — Remaining audit scope classification

- Created `REMAINING_AUDIT_SCOPE_CLASSIFICATION.md`.
- Classified the remaining partial artifacts into paper-relevant paths already
  audited at the claim/control level and historical/archive or
  submission-release dependencies.
- Confirmed that the paper-relevant evidence foundation is complete for
  section-by-section working drafting; raw artifacts and a frozen run manifest
  remain separate submission/reproducibility gates.

## 2026-09-29 — Introduction drafting checkpoint

- Reworked `INTRODUCTION_DRAFT.md` into a sectioned, citation-grounded
  Introduction covering context, problem formulation, brief related-work
  motivation, approach, contributions/scope, and organization.
- Used working author–year citations linked to the local bibliography for
  SBOM/supply-chain context, Android build transformations, and primary
  Android library/version-detection studies. Final venue style remains open.
- Synchronized the Introduction prose into
  `INTEGRATED_MANUSCRIPT_DRAFT.md` and updated the plan to record that
  section-by-section drafting has begun; the abstract remains last.
- Kept evaluation numbers out of the Introduction and retained the distinct
  emitted-version, source-denominator, and source-constrained claims.
- No tests or evaluation runs were performed; this was a manuscript edit.
- Next: refine Section 3 against the verified primary-source register, then
  synchronize it into the integrated manuscript. Raw exports and the frozen
  run manifest remain gates before Results become submission-ready.

## 2026-09-29 — State of the Art drafting checkpoint

- Re-read the full paper-writing rules, current State of the Art draft,
  citation register, evidence matrix, master-thesis state-of-the-art chapter,
  and literature-review protocol before revising Section 3.
- Replaced the thin synthesis with a structured, citation-grounded section
  organized around review scope, identity evidence, exact-version ambiguity,
  transformations, SBOM/vulnerability integration, and evaluation practice.
- Added the actual review boundary: protocol v1.0 frozen 21 June 2026; iterative
  seed-corpus assembly; 15 Tier A full texts and five Tier B supplementary
  records; search sources and concept blocks; original raw search-result and
  deduplication counts unavailable. The prose therefore does not claim an
  exhaustive selection flow.
- Used primary-source and verified bibliography evidence for LibScout, LibD,
  ORLIS, LibPecker, LibID, ATVHunter, LibScan, LibHunter, LibAttention, SAD,
  the systematic assessment, TPL-Benchmark, and UniBOM. Kept cross-study
  percentages tied to their datasets and metric definitions.
- Included TPL-Benchmark's 6,055 APK/source pairs and its 946-application,
  28,210-mapping detector-comparison slice; the 60.15% LibPecker F1 is
  explicitly labeled slice-specific. SAD's 84.82% strict version-level F1 is
  also tied to its obfuscated dataset and metric.
- Verified a post-freeze primary preprint, LibFan (arXiv:2609.31409), and
  described it as a separate post-freeze update, outside the frozen corpus
  count. Full-text metadata and approach were checked against the arXiv PDF.
- Synchronized the Section 3 draft into `INTEGRATED_MANUSCRIPT_DRAFT.md`,
  added used-source entries to `LITERATURE_CITATION_REGISTER.md`, and updated
  the paper plan. Venue citation style remains provisional.
- No code, tests, or empirical evaluation were changed or run. Raw project
  result exports and the frozen evaluation manifest remain submission gates.
- Next: refine Section 4 (Proposed Approach) against the current architecture,
  implementation, and evidence-provenance rules, then synchronize it into the
  integrated manuscript.

## 2026-09-29 — Proposed Approach drafting checkpoint

- Re-read the full existing Section 4 draft and claim-audit entries, located
  the current architecture under `docs/architecture/`, and checked the
  matcher, DEX analyzer, reference-feature store, CycloneDX serializer,
  vulnerability classifier, and decision log. The root architecture summary
  is older than the current implementation, so current source controlled the
  method wording.
- Rewrote `PROPOSED_APPROACH_DRAFT.md` to describe the input assumptions,
  seven-stage workflow, evidence roles, normalized weighted scoring, separate
  identity/version decisions, ambiguity and abstention boundaries, reference
  and transformation limits, and downstream SBOM/OSV claim handling.
- Corrected the status contract: identity uses confirmed/likely/candidate/
  uncertain; version uses exact/likely/candidate/uncertain. Both are
  rule-based labels, not calibrated probabilities. Explained that one
  reference version does not automatically justify an exact result.
- Kept concrete module names, database details, exact thresholds, and CLI
  settings for Section 5. Marked the guarded defaults and the diagnostic,
  experiment-only, and report-only boundary without treating these as
  population-level results.
- Synchronized an accurate concise Section 4 into
  `INTEGRATED_MANUSCRIPT_DRAFT.md`; Section 4 remains bounded by the current
  source snapshot, with final run/database manifest details still open.
- No code, tests, or evaluation runs were changed or performed.
- Next: refine Section 5 from current implementation and retained evidence,
  maintaining the raw-artifact/run-manifest gate and provisional status of
  documented historical counts.

## 2026-09-29 — Full six-section working-draft checkpoint

- Completed and integrated the Section 5 implementation/evaluation draft, with
  RQ1–RQ4, implementation defaults, evidence-lane definitions, historical
  results, failure/decision context, threats to validity, and reproducibility
  limits. The 84/84 controlled snapshot remains excluded from the provisional
  abstract because a separate 30-fixture/35-component summary conflicts with it.
- Drafted Section 6 and a provisional Abstract from only lane-qualified retained
  summaries; stated the 6,772/6,772 source-known analysis as an upper bound and
  preserved the caveat that raw evaluation inputs, database, source trees, and
  run manifest are absent from this checkout.
- Synchronized all six sections into `INTEGRATED_MANUSCRIPT_DRAFT.md`, then
  updated the paper plan, readiness audit, and claim audit. Corrected the
  identity/version status contract to match current source labels.
- Final release remains gated on restoring or explicitly publishing the
  evidence snapshot, reconciling the controlled and Phase-4 count conflicts,
  generating tables from one frozen dataset, final citation/venue formatting,
  and a claim-contract audit.
- No tests or new evaluation runs were performed.

## 2026-09-29 — Citation and reference-list audit

- Audited every author–year citation in the integrated Sections 2–3 against
  the paper citation register and the PFE/master thesis BibTeX records.
- Added a venue-neutral `REFERENCES_DRAFT.md` covering the works cited in the
  current manuscript and linked it from the integrated manuscript.
- Verified the official Android APK Analyzer and current R8 optimization page
  titles/URLs; mapped them consistently to Android Developers n.d.-a/n.d.-b.
- Disambiguated the two Zhan et al. (2021) works as 2021a (systematic
  assessment) and 2021b (ATVHunter), correcting the citations in the detailed
  Introduction, State of the Art, and integrated manuscript.
- Matched the NIST in-text citation to the personal authors listed in the
  local verified bibliography (Boyens et al., 2022).
- Venue-specific style conversion and final publisher metadata review remain
  open; no empirical data or code was changed, and no tests were run.

## 2026-09-29 — Method workflow figure and citation completeness

- Added a working Figure 1 flow diagram to the detailed Proposed Approach and
  integrated manuscript. It separates ordinary APK-only matching from the
  source-tree validation path, shows identity and version evidence separately,
  represents native files as SHA-256 file components, and makes OSV lookup
  optional and evidence-qualified.
- Added the official OSV API documentation to `REFERENCES_DRAFT.md` after
  finding that Section 4 cited OSV but the previous reference list omitted it.
- Confirmed the official OSV API documentation describes version-specific and
  batched vulnerability queries; the citation is used only to identify the
  API, not to support project evaluation claims.
- The Mermaid figure is a working editable source, not yet a venue-ready
  exported graphic. The venue, final claim audit, and result-artifact gates
  remain unresolved. No tests or empirical runs were performed.

## 2026-09-29 — Structured comparison and evaluation-strata tables

- Added a qualitative related-work comparison table to Section 3 and aligned
  the figure/table specification with its task/evidence focus. It compares
  representative profile, structural, hybrid version, transformation-aware,
  learned, benchmark, and SBOM-workflow approaches without ranking
  incompatible metrics.
- Added the Section 5 evaluation-strata table from retained project claim
  contracts. It distinguishes 72/84 controlled fixtures, clean and partial
  emitted-row strata, the 102-case emitting set, the 106-case source-tree
  denominator, the source-version-constrained lane, and four additional
  boundary cases in the 110-case inventory.
- Preserved the unresolved 30-fixture/35-component versus 72-fixture/84-row
  discrepancy and labeled all tabulated project figures as retained
  historical summaries.
- Synchronized the detailed Section 3 and Section 5 drafts into the integrated
  manuscript. No missing row-level values were inferred, and no tests or new
  evaluations were run.

## 2026-09-29 — Introduction polishing and evidence synchronization

- Reworked the opening context around the APK-only audit setting and tied DEX,
  D8, R8, and AAR statements to official Android documentation. Added the D8
  and Android library documentation to the working references with explicit
  author-date mappings.
- Strengthened the source-versus-binary distinction: a resolved source tree is
  a validation proxy, not a complete oracle for code present in the APK. Kept
  source-side versions out of ordinary candidate generation and retained the
  constrained result's upper-bound label.
- Reconciled `INTRODUCTION_DRAFT.md` with Section 2 of the integrated
  manuscript, restoring the full 2.1–2.6 structure (context, problem,
  motivating literature, approach, contributions/scope, and paper organization).
- Updated the claim audit and readiness/source registers. No tests or
  evaluation runs were performed.

## 2026-09-29 — Citation suffix ordering correction

- During the final Introduction/reference cross-check, corrected the provisional
  suffix assignment for the two Zhan et al. (2021) works to follow the current
  working reference-list order: ATVHunter is 2021a and the systematic
  assessment is 2021b. Updated the detailed Introduction, State of the Art,
  integrated manuscript, citation register, and claim audit consistently.
- The earlier session entry records the initial mapping and is retained as
  history; this correction supersedes it. Final venue style may still specify
  different bibliography details.

## 2026-09-29 — Integrated manuscript editorial cleanup

- Removed internal drafting instructions, submission gates, working-source links,
  and release checklists from the integrated paper body; retained those controls
  in the plan, readiness audit, and writing log.
- Normalized integrated manuscript heading hierarchy for Sections 1–6 and
  their subsections, removed provisional/internal labels from section headings,
  and embedded the working reference entries at the end so the manuscript is
  self-contained.
- Rephrased archive-availability statements for a scholarly manuscript rather
  than a local checkout, while retaining the material limitation that raw
  evaluation inputs and a frozen manifest are absent.
- Preserved the substantive historical-snapshot caveats, conflicting
  controlled counts, source-version upper-bound label, and metric denominators.
  No code, tests, or fresh evaluation runs were involved.

## 2026-09-29 — Readiness and scaffold status reconciliation

- Rewrote `PAPER_FOUNDATION_COMPLETION_AUDIT.md` to distinguish the completed
  first six-section working-draft pass from the still-pending raw-result,
  frozen-manifest, and submission gates.
- Updated `MANUSCRIPT_SCAFFOLD.md` to identify the integrated manuscript as the
  current authoritative draft, retain the abstract-last rule, and describe
  remaining visuals/failure taxonomy as gated on row-level data.
- The integrated manuscript remains historical-evidence work: the claim scan
  preserved 72/84 versus 30/35 as an unresolved controlled discrepancy,
  927/1,837 emitted confirmation across 102 APKs, 927/12,082 source coverage
  across 106 source trees, and 6,772/6,772 only as source-constrained upper
  bound. No tests or new evaluations were run.
