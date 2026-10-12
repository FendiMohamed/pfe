# Project Study Index

## Purpose

Maintain a source-grounded map of the complete project checkout so the paper
can use the implementation, data, experiment history, tests, research sources,
and presentation artifacts consistently. Every available path is treated as
potentially informative. Inclusion in this index records that a file exists;
it does not make the file authoritative for numerical claims.

## Checkout snapshot

Inventory captured 2026-09-29 from the extracted ZIP at
`C:\Users\ACER\Downloads\pfe-main\pfe-main`:

| Area | Files | Approx. size | Initial interpretation |
|---|---:|---:|---|
| `data/` | 437 | 399 MB | Evaluation case folders, configs/proofs, fixture sources, partial APK/source artifacts; reference and result directories are mostly absent/ignored. |
| `docs/` | 300 | 2.7 MB | Project handbook, evaluation runs, experiment reports, research decisions, thesis evidence and process history. |
| `outputs/` | 526 | 34.2 MB | Defense-deck source, intermediate renderings, slide assets, QA, reports and screenshots. |
| `scripts/` | 114 | 1.6 MB | Data collection, build, analysis, experiment, evaluation, and presentation helpers. |
| `thesis/` | 107 | 29.2 MB | PFE and Master source, bibliography, figures, drafts and compiled PDFs/ZIPs. |
| `tests/` | 57 | 0.4 MB | Unit and integration-style tests covering runtime and experiment/report boundaries. |
| `src/` | 47 | 1.0 MB | Python package: production pipeline plus diagnostic and experiment implementations. |
| `ressources/` | 17 | 19.9 MB | Research papers and prior student reports used for context. |
| `work/` | 9 | 0.7 MB | Earlier supervisor proposal, technical note, and state-of-the-art drafts/matrices. |
| `configs/` | 50 | 3.0 MB | Reference catalogs and per-experiment/database configuration. |
| `output/` | 22 | 13.8 MB | Exported PDFs, certificates, and report/dashboard output. |
| `papers/` | 16 | 0.1 MB | Paper plan/rules plus early literature review and structured paper analyses. |

The current checkout is about 530 MB, not the former >100 GB working set. It
contains 14 real APK binaries (including the root `data/test_apks/real/F-Droid.apk`)
and one controlled limitation APK. Under `data/test_apks/real/` there are 118
`metadata.json` files: 103 F-Droid candidate records (each marked report
generated but excluded from source-validated metrics) and 15 APK inspection
snapshots with APK/DEX/manifest/native-file metadata. These are not 118
independent evaluation cases. The available documentation reconciles the
denominators as follows: 102 source-validated real APKs that emitted Maven
components form the primary `927/1,837` accuracy set; four source-validated
no-Maven-signal controls bring the source-tree set to 106; four additional
limitation examples bring the transparency dataset inventory to 110. The root
`.gitignore` excludes APKs,
`data/source/`, `data/results/*`, and `data/reference_db/*`. There is no `.git`
directory in this ZIP, so commit history cannot be inspected here; the task
board, decision ledgers, dated logs, and generated evidence must carry the
chronology. These omissions are constraints on independent reproduction, not
evidence that the work was not done.

## Source authority and interpretation

1. Current source code/configuration defines implemented behavior.
2. Test source defines encoded invariants; tests have not been run during this
   study.
3. Generated JSON/CSV/Markdown and proof bundles define recorded experiment
   outcomes; preserve run identity, baseline, lane, and denominator.
4. Thesis sources and evidence snapshots define written claims and their
   interpretation; resolve conflicts against generated artifacts where
   possible.
5. Compiled thesis PDFs, slide decks, old proposals, and old drafts preserve
   presentation history and may expose changed or stale claims.
6. Missing APK/reference/source/result files prevent direct re-execution or
   byte-for-byte validation; report this boundary for affected claims.

Different artifacts may be useful while carrying different authority. Stale
or superseded drafts should be retained as chronology and not treated as the
latest result surface.

## Review register

| Area | Status | Coverage recorded |
|---|---|---|
| Paper plan and ongoing writing rules | Reviewed | Supervisor order, claim discipline, citation and evaluation-lane constraints. |
| Root project overview and architecture | Reviewed | README, root instructions, package metadata, Docker setup, core task-board milestones. |
| Project handbook | Reviewed | All 34 handbook pages inventoried; the start/current-state, pipeline, module maps, metrics, negative experiments, priority DB, safe rules, troubleshooting, research mapping, command and proof-index pages reviewed. Treat it as navigation and interpretation, not sole authority for claims. |
| PFE thesis | Core review completed; exhaustive source pass pending | Main technical/evaluation argument, including AI, implementation, failures and threats; revisit all chapters/appendices and compare compiled versions. |
| Master thesis | Core review in progress | Introduction, background concepts, taxonomy/framework and case-study argument reviewed; complete every chapter/appendix and review artifacts against source. |
| Runtime package | Partial | Core pipeline plus reference acquisition/conversion/features and CLI dispatch inspected. Continue remaining modules and experiment modules. |
| Scripts | Partial | CLI exposes 31 commands spanning acquisition, conversion, matching, reporting, AI/R8 diagnostics, experiments, and source validation; 114 standalone scripts still need grouped source-to-output tracing. |
| Tests | Partial | Test inventory and key matcher, extractor, DEX, SBOM, source-validation, vulnerability, AI/R8/report-only cases reviewed. Continue every test file by behavior group; do not execute unless asked. |
| Evaluation docs and raw artifacts | In progress | Decision ledger and representative negative results reviewed. Continue complete family map and artifact cross-checks. |
| Dataset/configuration/source trees | Not yet fully reviewed | 15 APK binaries plus sparse real-case folders; 134 Kotlin files and numerous JSON/YAML/XML proof/config files require mapping to fixtures and case IDs. |
| Research papers and prior reports | Not yet fully reviewed | 15 research PDFs plus 2 prior-report PDFs; extract/index all, then read paper-specific evidence for works used in related work. |
| Defense/output artifacts | Partially reviewed | Identified multiple deck generations and audited the final 39-slide academic deck's plan, source notes, QA, build manifest and speaker companion; it has 31 main slides and 8 backup slides. Earlier 12-, 13-, 43-, 52- and 60-slide decks preserve chronology. Next inspect slide text/notes and generated report screenshots against canonical evaluation evidence. |

## Study sequence

1. Read instructions and project-level framing; establish artifact/source
   authority and chronology.
2. Complete documentation and decision history, retaining positive, negative,
   blocked, and superseded experiment families.
3. Trace every source/script entry point to its configs, tests, inputs, and
   generated outputs.
4. Map all evaluation cases, fixture code, proof bundles, source trees, APKs,
   and unavailable artifact references.
5. Review both thesis sources and relevant compiled outputs against primary
   evidence; inspect all supplied research-reference files used in the paper.
6. Reconcile any conflicting case counts, denominators, and paper claims. Do
   not execute evaluation or tests without an explicit request.
7. Update this register and `PAPER_WRITING_SESSION_LOG.md` at each checkpoint.

## Current technical understanding

The PFE is an implemented, static APK-to-SBOM pipeline: inspect APK/manifest
and DEX, build Maven reference profiles by downloading and D8-converting JARs
or AARs, extract comparable features, rank candidates with guarded version
decisions, emit CycloneDX 1.5, query OSV, optionally validate against source
Gradle trees, and report evidence/uncertainty. The Master thesis contributes a
research framework for evidence provenance, quality, ambiguity, abstention,
validation lanes, and downstream authority; it does not describe a second
detector.

The current default matcher is more specific than this high-level summary:
base signals include package/class/method/opcode/dependency/literal evidence;
class, method, and literal evidence also contribute to a version-unique score.
API-reference and opcode-ngram weights default to zero. The version-unique
literal/context reranker and composite-family shortlist are enabled by default
in the present code. Version selection then uses bounded evidence-based
rerankers (including supported version-unique evidence, POM dependency
coherence, and selected app-era rules), while confidence labels distinguish
library identity from version certainty. Do not describe the matcher as an
unqualified weighted-similarity system without its abstention, family, and
version-selection stages.

The reference-side profile is produced by fetching Maven artifacts and POM
metadata, converting JAR/AAR bytecode to DEX, and extracting matching features
into a SQLite database. APK inspection covers standard and nonstandard DEX,
manifest metadata, ZIP-level extraction indicators, and native `.so` hashes.
The matcher normalizes weighted signals over active weights, groups candidate
versions by coordinate, computes separate identity and version confidence,
records close alternatives/ambiguity, and applies artifact-family suppression.
The report path emits CycloneDX 1.5 with evidence and confidence properties,
queries OSV, and can compare emitted rows to resolved Gradle dependency trees.
Source validation confirms only coordinate/version membership in the supplied
tree; it is not a proof that the APK bytecode was completely decomposed.
Native files are hash-only file components. Source validation can downgrade
OSV claims to potential on mismatch or absent source evidence.

The CLI makes a clear boundary between the core pipeline and research tooling:
the default route is download/expand references -> convert -> extract SQLite
features -> match -> CycloneDX/OSV/report, with source validation as a separate
command/artifact. R8, version-band, family, and AI commands produce diagnostics,
gates, or report attachments; report help strings explicitly state that the
opt-in AI/R8/version-band attachments do not alter matcher choices or
source-validation metrics. Confirm downstream imports and test guards before
making broader “report-only” claims about each family.

Code-review note, not evaluated behavior: `_store_conversion_features` clears
an existing component's feature rows before checking each DEX path. If a later
DEX path is missing, it returns a failed result after earlier database writes;
the surrounding SQLite context commits on normal function exit. The current
`tests/test_reference_features.py` covers successful extraction but has no
missing-late-DEX regression case. Do not infer that this affected the historical
reference database; that database is absent from this ZIP and the project was
not run for this study.

Reference expansion has three distinct lanes in the code/docs: the popular or
calibrated baseline catalogs; broad source-observed candidate catalogs derived
from the coverage dashboard (exact source versions, with metadata-only BOM
entries excluded from bytecode builds); and real-APK-priority catalogs derived
from resolved Gradle runtime trees, ranked by the number of distinct APK trees
supporting each coordinate/version. The latter configs explicitly describe an
evaluation-only lane. A separate guarded promotion workflow consumes current
control comparison JSON: target gains with no regressions are safe, gains plus
regressions are app-specific, regressions without target gain are regression
risk, and no gain/regression is no-change. Only safe singleton evidence can
support a per-version global promotion; a clean tested bundle stays scoped to
that exact bundle. Unit tests cover the classification and scope safeguards.

Recorded promotion discipline rejected global opcode/API weights, a global
multi-scale R8 blend, recency tie-breaking and unsafe reference expansion
after no benefit or regressions. Narrow R8 and AI analyses remain
experiment/report-only. Source-known runs are upper bounds, and native/hidden
payloads remain explicit boundaries. These are provisional study conclusions
to verify against each linked source family before paper drafting.

The Phase 5 R8 trigger is implemented as a separately callable scoped reranker
and exposed by an explicit experiment command; a source scan finds no import or
call from `matcher.py` or the default report path. Its retained Markdown report
records 286 rows (24 controlled, 262 real), four target improvements, and zero
triggered regressions/conflicts, and calls the outcome experiment-only. Tests
encode the trigger profile conditions (low-confidence target context), blocks
strong baselines and generated controls, checks the 4/0/0 counts, and checks
that production wiring fails a static gate. The JSON evidence files those tests
reference are absent from this ZIP, so the checks were read, not executed or
independently recalculated.

Controlled fixtures are generated by `scripts/build_controlled_apk.py` from
downloaded Maven artifacts and compile a small Java caller where `javac`/`jar`
are available; otherwise the builder can fall back to library-only input. Clear
fixtures use D8, R8 variants use explicit ProGuard/R8 rules, and the APK ZIP is
assembled with the produced DEX files plus a minimal manifest/resources entry.
Each generated fixture writes a `.ground-truth.json` with expected Maven
coordinates/versions, DEX filenames, variant, and build provenance. The
inventory builder reads those truth files and per-APK `report.json`s, compares
coordinate and coordinate-version pairs, and puts limitation APKs in a
separate non-accuracy lane. In the current ZIP there are no controlled APK
ground-truth files or controlled APK binaries, and `data/results/` contains
only `.gitkeep`; thus the retained `APK_TESTSET_INVENTORY.md` is a historical
summary, not a regenerable current inventory. The source test
`test_controlled_r8_matrix.py` checks builder variants, R8 rules, matrix
definitions, and reuse behavior but does not provide those missing fixtures.

Two matcher changes have explicit promotion histories and are now `True` by
default in source, each with a disable flag for baseline reproduction:

- Composite-family shortlist: readiness evidence records 81/81 cases, 62
  controlled plus 19 real, removal of 1,347/8,100 reference rows (16.63%),
  zero tracked source-family losses, zero tracked selection regressions, and
  zero reportable version changes. A later June 3 verification records the
  promotion, no-flag/disable-flag smoke, and test/compile checks. This is
  candidate pruning with intended unchanged selections, not an accuracy gain.
- Version-unique literal/context reranker: raw literal/context and broad
  one-match signals had regressions; a stricter rule requires at least two
  matching features, score >=0.10, advantage >=0.05, raw leader score >=0.35,
  within 0.020 raw-score margin, and identity-confidence tolerance. The
  readiness report says 24 controlled plus 224 real rows, keeps one VLC
  RecyclerView improvement, filters three weak suggestions including two
  regression risks, and shows the VLC slice improving 6/26 to 7/26 while
  AntennaPod/OsmAnd remain unchanged. June 2 verification records its
  promotion and no-flag VLC smoke.

These are materially different contributions: family shortlisting prunes
candidate coordinates while preserving selected versions; literal/context
reranking changes one guarded version choice. Their promotion-readiness reports
predate the promotions; use the dated verification reports and current code for
state. The referenced databases, raw experiment JSONs, report JSONs, and APKs
are absent from the ZIP, so the historic smoke/test results are documented
evidence, not independently reproduced results in this study. The unit tests
for readiness gates use synthetic temporary JSON; other feature-level tests
cover shortlist behavior and reranker CLI/default/disable behavior.

AI/R8 work is a separate report-assistance/research track. Current source marks
training data, model, suggestions, and report artifacts `report_only`; the MVP
integration gate explicitly forbids ML authority over selected versions,
SBOM components, and vulnerability labels. The retained final evaluation
reports Random Forest macro-F1 0.708, structured-token Transformer 0.977 (with
source/context shortcut risk), source-free/MVP-safe Transformer 0.882, and raw
opcode Transformer 0.110 versus an opcode-count baseline 0.128. The final gate
shows zero strict APK-only candidates after controls, so matcher authority is
blocked. The dataset split is deterministic and case-grouped, but the corpus is
derived from project-held diagnostic evidence, not an independent external APK
corpus; scores are not generalization claims. The report-only smoke records
semantic SBOM content and vulnerability labels unchanged, but the raw SBOM SHA
differs; describe semantic output preservation, not byte-for-byte equality.
All source result JSON/model artifacts referenced by these reports are absent
from this ZIP, so these metrics remain retained report evidence pending
independent reproduction.

Version-band/lifecycle diagnostics preserve a similar authority boundary. A
source-known v2 analysis marks 565 of 582 scoped wrong-version rows as
potentially fixable, but it is an upper bound because the source version
constrains the candidate choice. The source-free APK-only reranker using only
baseline alternatives and sibling era anchors makes zero changes/fixes; the
source version appears in only 44/582 baseline alternatives (7.6%). Candidate
expansion v3 is rejected: its narrow deep same-coordinate pilot selected an
older incorrect alpha version. Thus do not present 565 as achievable recall or
as an implemented matcher gain.

The low-risk AppCompat/Core trigger and Lifecycle-family experiment remain
report-only diagnostics, not matcher integrations. The former can downgrade a
selected-version claim when at least two stronger AndroidX family anchors
support a later era; it does not assert a replacement. The latter maps public
Lifecycle coordinates to Android-target variants, downgrades only a public
coordinate claim with source-backed target evidence or at least two family
anchors, and keeps patch near-ties ambiguous. Retained reports show 7/13
introduced AppCompat/Core mismatches flagged and 2/5 Lifecycle public claims
eligible for downgrade; these are narrow fixture diagnostics, not broad
accuracy results. Tests check no default matcher/report import of the
Lifecycle experiment. Their raw reports/source trees are absent here.

The no-Maven AndroidX and Mastodon fork-family lanes also deliberately use
source trees as diagnostic context and cannot be counted as APK-only detection.
The AndroidX experiment requires a source-runtime overlap and an exact
source-version candidate already in the report, plus score/package/opcode
floors; it may surface a report-only suggestion but never changes SBOM
components or selection. Retained output reports six suggestions among 14
overlap rows across three no-Maven AndroidX cases, with eight suppressed.
Mastodon handling separately maps `me.grishka.litex` fork coordinates to
upstream AndroidX candidates only when source-version compatibility and
evidence floors hold. Retained output reports two Litex suggestions, seven
suppressed, and one direct Gson suggestion; all effects remain report-only.
Tests verify boundary routing and static absence from matcher/report imports.

The full structured-token Transformer corpus includes raw coordinate tokens,
source-version and candidate-version tokens, source/row type, and selected
diagnostic context tokens in addition to matcher evidence. Its split groups by
case ID, not by coordinate; therefore same-coordinate evidence can span split
cases (a leakage/generalization risk inferred from the source schema and split
policy). The separate `mvp-safe` profile removes raw coordinate and source
version/context tokens, keeps only candidate-version shape and APK-derived
matcher/R8 features, and is positioned only as report-only risk triage. The raw
opcode Transformer is another distinct task: a bounded method-opcode corpus
(default cap 14 APKs, 120 methods/APK, sequence length 128) predicts APK role/
obfuscation profile, not library identity/version. The retained test report
states only two APK cases per label in its case-held-out test split and records
the Transformer below the opcode-count baseline. It remains research-only.

Evaluation artifact inconsistency to resolve before paper use: the current
`REAL_CASES` registry marks Flying Carpet and FitoTrack as
`source-validated-partial` and gives each a resolved-tree validation path and
counts; the retained `THESIS_EVALUATION_TABLES.md` reports zero blocked cases.
Yet `GROUPS` still assigns those two IDs to `blocked-source-linked`, and the
retained `APK_TYPE_EVALUATION.md` labels their group “Source-linked but
validation-blocked” while aggregating 16/35 emitted versions across them. The
group/category text is stale relative to current case roles and should not be
used as evidence that those rows remained blocked. No dedicated test file for
`build_apk_type_evaluation.py` was found in `tests/`.

The downstream thesis-table builder (`scripts/build_thesis_evaluation_tables.py`)
has a separate source-level metric caveat: its controlled aggregation parses
only the first fraction in each group summary, which `summarize_controlled`
defines as component true positives / expected components; it then stores that
numerator under `confirmed_versions`. The exact-version fraction is the second
fraction in the text. The retained table reports 84/84 for both, so the present
recorded number may coincide, but the generator would overstate exact versions
if component identity were correct while versions mismatched. It also derives
the number of source-validated cases from static case roles even when current
report/validation JSONs are missing; role population and available metric
evidence must be checked separately. No dedicated test was found for this
table-generation script either.

## Evidence and chronology notes (checkpoint 2026-09-29)

- The defense artifacts are useful synthesis layers, but their `source-notes.txt`
  points to `data/results/...` paths from the original working tree. Most such
  result files are absent from this ZIP. Some screenshots are retained, while
  direct JSON/HTML bundles are not consistently retained.
- The final deck distinguishes the normal 927/1,837 emitted-Maven-version
  confirmation result from the 6,772/6,772 source-known upper-bound lane and
  explicitly states that the latter is not APK-only production accuracy.
- Case-count meanings are now reconciled at the documented category level:
  `102` Maven-emitting source-validated APKs underpin `927/1,837`; four
  no-Maven-signal source-tree controls make 106 source-tree cases; four
  additional limitation cases make the 110-case transparency inventory. The
  v2 upper-bound lane uses the 106 source-tree set; keep all three denominators
  distinct in the paper.
- Map each module/script/config family to its evidence producer and tests. The
  current test inventory contains 57 Python files; tests are being read but
  have not been executed.
- A stale `DATASET_COVERAGE_MATRIX.md` row claims exact controlled multidex is a
  gap while listing multiple controlled multi-library multidex fixtures in the
  same row. This is an example of why dated planning matrices should not
  override generated inventory/evaluation evidence.
- The one source tree retained under `data/s3/` is Simple Time Tracker 1.57;
  its build/config/source material is unpacked, and `data/v3/` retains Gradle
  dependency trees plus source-validation output (105 source coordinates;
  6/12 emitted Maven components exact, 6 version mismatches). Earlier v3
  candidate-status documents still call its source validation failed/unknown;
  later proof results explain that Docker `/tmp` extraction and a successful
  `:app` `baseReleaseRuntimeClasspath` resolved that blocker. The later result
  supersedes the earlier status for this case. The underlying APK/report output
  is not retained in the frozen results directory.

## Current pass: evaluation/configuration trace

- The controlled inventory builder uses fixture ground-truth JSON files to
  define exact expected components and compares those coordinate/version pairs
  against generated report components. Real proof inputs come from selected
  report plus Gradle validation artifacts; the current result/reference
  directories are missing, so the evaluator cannot be rebuilt from this ZIP
  alone.
- `build_apk_type_evaluation.py` declares real cases/roles and evaluation groups
  in source, then aggregates confirmed, version-mismatch, and missing emitted
  component rows. Its principal source-validated count includes clean and
  partial roles; no-Maven-signal cases are separate and are not included in the
  102-row-bearing metric. Limitation and blocked cases remain outside it.
- The 50 configuration JSONs are not one flat reference catalog: they cover
  seed/calibration (12/35 coordinates), an expanded catalog (147),
  source-observed version catalogs (about 1.2k–1.36k coordinates), real-APK
  priority versions (1,339 coordinates), retry/repository/packaging subsets,
  scoped experiments, and 16 sequential clean-candidate selections. They
  describe alternative and staged evidence-generation lanes; presence does not
  mean a catalog was promoted to the shared default DB.
- Test-source inventory shows separate assertions for code mechanics, dataset
  role/exclusion, report-only boundaries, promotion gates, and CLI artifact
  writing. Tests explicitly require AI/R8 diagnostics to leave default
  selection untouched, source-context/controlled-regression gates to reject
  unsafe promotion, and validation-copy cases not to be called clean. Tests
  have not been run during this study.

## Current pass: first full-text literature read

- Began a page-level review of the supplied `Revisiting Third-Party Library Detection - TPL-Benchmark.pdf` (20 pages) rather than relying on citation metadata. Reviewed its framing, dependency semantics, TPL-Extractor workflow and exceptions, benchmark composition, detector comparison, reported limitations, and dependency-declaration appendices.
- The benchmark explicitly aims to label dependencies packaged in the APK, while deriving labels from source build configuration. Its extraction process filters configurations expected to contribute packaged code, resolves variables and module reachability, normalizes/deduplicates coordinates, and manually handles mixed DSLs, custom scripts, multiple APK targets, and ambiguous versions. This illustrates that source-derived labels require careful mapping to the particular APK; ordinary source presence alone is not proof of packaged presence.
- The paper reports 6,055 projects, 5,756 unique TPLs, 15,274 versions and 62,218 verified App-TPL mappings. Its tool comparison distinguishes library- and version-level precision/recall and reports differences in profiling cost, compatibility and effectiveness. Reported failure themes include transformation sensitivity, poor version discrimination, database/candidate correspondence, threshold generalization, runtime/memory costs, lightweight libraries, structural similarity and Kotlin metadata-only libraries.
- Relevance to our study: supports separating component identity, version identity, source-tree corroboration, packaged-code evidence and scale/cost. It is a benchmark paper with APK/source pairs and manually resolved cases; it does not establish our current selected-case denominators or validate our outputs. Do not transfer its metrics or describe its ground truth as directly comparable to our narrower source-validation evidence.
- Literature reading is in progress. Other supplied PDFs, PFE/Master citations without local PDFs, and the complete details of this paper's RQs, evaluation protocol and validity discussion remain to be read and recorded. No experiments or tests were run.

## Literature cross-check: detector assessments and version identification

- Read the abstract/intro and selected evaluation, failure-analysis and validity passages of `A Systematic Assessment on Android Third-party Library Detection Tools.pdf`. The study compares publicly available tools over construction quality, effectiveness, efficiency, version identification, obfuscation resilience and usability. It reports recurring limits from package-based candidate separation, incomplete handling of partial imports and formats, weak version discrimination, thresholds and differing transformations. Its tool suite/data/metrics differ from this project, so it is contextual related work rather than a baseline we can claim to reproduce.
- Read the abstract and proposed-method summary of `Version-level Third-Party Library Detection in Android Applications via Class Structural Similarity.pdf` (SAD, 2025). SAD uses class dependency graphs, class summaries and structural subgraph similarity for version-level detection, and reports distinct library- and version-level performance on three datasets. It directly confirms that version identity requires separate evaluation from library identity. The method and reported scores still need full protocol/threats review before precise comparison.
- These are partial literature passes, not complete readings. Preserve source-specific years, datasets, candidate/reference construction and transformation settings in the related-work matrix before quoting or comparing any numeric results.

## Current pass: thesis claims and decision-ledger cross-check

- Re-read the English abstracts and key framing/evaluation passages in the PFE and Master LaTeX sources. The PFE's research object is a static compiled-APK-to-CycloneDX 1.5 pipeline, with distinct component identity/version decisions, evidence, ambiguity, OSV interpretation and optional source-tree evaluation. Its four RQs address controlled exact-version recovery, quality by real APK family, full source-denominator representation, and authority/uncertainty in SBOM, vulnerability and AI outputs.
- The Master thesis is conceptually distinct: it proposes a claim/evidence trust framework, synthesizes detection research, then uses the PFE system as a bounded case study. Its central dimensions include claim granularity, provenance, directness/uniqueness/independence, transformation risk, reference coverage, conflict/abstention, validation lane and allowed downstream authority. For the implementation-and-evaluation paper, this may inform interpretation, but should not be represented as if it were a novel detector implemented in the APK matcher.
- Read the 49-line `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`, relevant PFE failed/non-promoted experiment table, and the final V2 results/traceability materials. Decision reasons include: global opcode weight regressed established apps without confirmed-version gain; API weight did not change guarded metrics; global multi-scale R8 blend improved four targets but caused controlled/real regressions; source-known version opportunities did not yield APK-only fixes; wider candidates selected an incorrect older alpha; priority DB growth broadened emissions and produced source-missing rows; reference promotions require target gain plus controls; no-bytecode/unavailable slots are retained as evidence. AI/R8 and scoped experiments stay report-only, and native identity/version recovery remains out of scope.
- Verified live ZIP state: exactly 15 `.apk` files are retained (14 real APKs and one hidden-DEX limitation APK); `data/results/` and `data/reference_db/` each contain only `.gitkeep`; `data/source/` is absent; one unpacked source project exists under `data/s3/`. These boundaries prevent re-running historical test sets and rebuilding/independently checking many reported metrics from this checkout.
- Cross-check of current matcher/CLI and promotion tests confirms two promoted controls are default-enabled and disableable: composite-family shortlist and guarded version-unique literal/context near-tie reranker. Core default weights are package .15, class .45, method .25, opcode histogram .15, dependency .10, literal .08, unique-version .12; API and opcode n-gram weights are zero. Promotion readiness tests contain synthetic input gates; these tests prove policy logic, not historical result reproduction. No tests were executed.
- These reads refine earlier notes but do not complete the full thesis, implementation, experiment, tests, PDF, output and data review. Keep the study active.

## Current pass: production pipeline source cross-check

- Read current source for APK inspection/forensics, DEX extraction, data models, CycloneDX serialization, Gradle source validation, OSV classification/source-validation propagation, and the feature-store write path. This pass is partial for large modules (`matcher.py`, `report.py`, `cli.py`, `dex_analyzer.py`, `reference_features.py`); their full implementations and all test contracts remain to be reviewed.
- APK inspection hashes the APK, enumerates standard and nonstandard DEX-like entries, reads manifest metadata, and inventories native `.so` files by path/ABI/size/SHA-256. Forensic indicators are heuristic (e.g., protector-like filenames, tiny primary DEX, opaque assets, many native files), not proof that code is hidden. Native components are emitted as hash-only CycloneDX file components.
- DEX extraction uses Androguard for package/class/method/opcode evidence and, when member extraction is enabled, internal dependency edges, fields, literals, invoked API references, opcode n-grams, block/call-chain fingerprints, class-neighbor summaries, and literal-context features. Their presence in the feature model does not imply scoring: defaults/gates must be followed signal by signal.
- `validate_cyclonedx_against_gradle_tree` parses Gradle resolved coordinates and compares each emitted Maven coordinate/version. Confirmed means present with that selected version in the provided tree; mismatch/missing are explicit. Its own report says this does not prove APK-bytecode completeness. It also does not validate non-Maven/native components.
- CycloneDX 1.5 serialization includes APK SHA-256, Maven PURLs, evidence/confidence/identity-version state and ambiguity properties; native entries contain hashes and explicit `hash-only` identification. OSV findings are confirmed only with sufficiently supported identity and exact/high version; source validation can downgrade unsupported or mismatched findings to potential.
- Reconfirmed a possible feature-store failure-path integrity issue in `reference_features._store_conversion_features`: it upserts and deletes previous rows before checking every DEX path, and returns `failed` on a later missing path without rolling back prior writes. Record as static code risk only; it does not prove an existing DB was corrupted. No tests were run.

## Matcher semantics cross-check

- Read the core `match_apk_to_reference_db`, feature-to-candidate scorer, selection/classification and output-filter paths in `src/apk_sbom/matcher.py` plus selected control tests. Candidate overlap for names/strings/graphs is measured against the reference feature set; opcode histogram uses cosine similarity. Weighted score is normalized by enabled weights. Unique class/method/literal features are computed against sibling versions. Identity confidence is classified separately from version confidence; near-tie or feature-equivalent versions can retain ambiguity, and a lone reference version is capped unless its feature match is effectively complete.
- The composite family shortlist ranks coordinate families before detailed matching, retains families within a score margin or rescued by guard policy, and records rows removed. Therefore its performance claim is about candidate pruning/runtime and preserved selections, not new detection accuracy. Default enabled is confirmed in core API/CLI and tests.
- The version-unique literal/context reranker is a narrow near-tie selector: raw leader floor .35, margin .020, at least two supported matched unique literal/context features, score advantage at least .05, and bounded identity-confidence loss. It selects among reference versions already in the database; it does not create new coordinate/version candidates. Default enabled is confirmed in code and the historical promotion record; disable flags exist.
- These code details support the distinction between rank, claim confidence and source validation. Full branch-by-branch matcher review and complete report/CLI/tests review remain open.

## Project-history and stale-planning document review

- Read root `AGENTS.md`, `README.md`, `TASKS.md` (including its current tail), `docs/architecture.md`, and the beginning/end of `docs/architecture/DECISIONS_LOG.md`. These are useful design/history records, but several are early snapshots, not current truth. Root `AGENTS.md` describes a research-phase/future prototype and a 9-paper resource folder, while the current tree has the implemented pipeline, two theses, and 15 local research PDFs. It labels all papers deeply read, which is not established by the current review. The root README's task list still marks evaluation/implementation as not started and repeats broad result claims; the architecture proposal assumes LibScout as a baseline and basic-block fusion, while the actual system is a separate Python pipeline with guarded/inert multi-scale signals and no Bayesian scoring. Do not use these old summaries as manuscript evidence.
- The architecture decision log records the original approved scope (static APK analysis, selected Maven references, confidence, CycloneDX/OSV, native hash-only) and exclusions (dynamic loading, full native identity/version and universal coverage). These decisions align with the current implementation at a high level, but current details and later boundary additions must be checked in code and newer evidence.
- `TASKS.md` has 296 rows; most describe chronological completed work and include a trailing `in-progress` combined-analysis task. That entry cites 102-APK outputs now absent from `data/results/`. Treat it as a historical checkpoint pending artifact restoration, not a current reproducible job.
- Read the traceability matrix and selected evaluation table / Chapter 6 evidence snapshot. They provide links from state-of-art ideas to implementation, evidence and limits; they are secondary summaries, often rich in concrete case roles, and still require source/evidence verification. The traceability matrix itself says not to treat `927/1837` as full recall and identifies external scanner checks as unavailable/optional.
- More than 200 evaluation Markdown files exist. A complete review of the timeline remains open; future passes must prioritize final/current reports, decision evidence, and then historical predecessors to resolve supersession instead of treating every dated sweep as the current result.

## Core test-contract review

- Read all of `test_apk_extractor.py`, `test_source_validation.py`, `test_sbom.py`, `test_dex_analyzer.py`, `test_reference_features.py`, and the first 568 lines of the large `test_matcher.py`. These tests construct synthetic ZIPs/objects/SQLite rows and mock Androguard/network calls; they verify specified behavior but do not constitute a run on retained real APKs or an independent accuracy rerun.
- Covered contracts include archive multidex/native enumeration, manifest metadata, heuristic forensic warnings, Gradle requested-to-resolved version parsing, confirmed/mismatch/missing source validation, CycloneDX 1.5 fields and ambiguity properties, native hash-only entries, feature extraction helpers, parse-error handling, SQLite feature persistence, weighted score arithmetic, optional signal isolation, and shortlist pruning while preserving reference versions within the retained coordinate.
- The source-validation test fixture confirms a project dependency tree can contain coordinates/versions that do not match the APK's emitted row; this reinforces that the lane evaluates membership of emissions in the supplied tree, not completeness of APK attribution.
- `test_reference_features.py` has only three tests (discovery filters/offset and successful synthetic feature insertion). No missing-later-DEX rollback test was found by searching its complete test source, so the previously recorded partial-write risk is not directly guarded. This is a coverage gap finding, not an executed failure.
- The systematic-assessment and TPL-Benchmark PDFs use two-column layouts. For TPL-Benchmark, visually rendered page 1 and the detector-results page confirmed the title/abstract, multi-column text and Table 4 after extracted text appeared out of reading order. Bundled Poppler emitted missing-font warnings while rendering, but the inspected pages were legible; temporary renders were removed after inspection.
- Review of the remaining matcher test body, test files, report/CLI integration, scripts and data/test manifests remains incomplete. No tests were executed.

## Matcher tests and CLI/report authority boundary

- Completed review of the 1,687-line `tests/test_matcher.py` by reading its test-name inventory and test blocks across scoring, integration, confidence, version tie-breaking, POM/dependency context, app-era coherence, ambiguity and artifact-family reporting. It covers reference-denominator overlap and cosine scoring; zero default score impact from inert multi-scale feature fields; version-unique features; identity/version confidence separation; confidence caps for one-version references; reranker enable/disable behavior; ambiguity sets; POM preference only with independently matched supporting components; and scoped Compose/Lifecycle/Okio/OkHttp choices. Most decision tests construct `MatchCandidate`/`VersionDecision` objects or synthetic SQLite records rather than parsing a real APK.
- Inspected `cli.py` command dispatch and `report.py` workflow. Production commands include APK inspection/DEX analysis, mock and real SBOM generation, Maven download/config expansion/JAR-AAR-to-DEX conversion/reference features, APK matching, OSV lookup, report generation, and source validation. Separate experiment commands cover AI/R8, version bands, family aliases, Phase 5, router/gates, and literal-context diagnostics.
- `generate_final_report` gets selections only from the deterministic matcher and writes `matches.json`, CycloneDX, optional OSV JSON, and JSON/Markdown/HTML reports. Experiment evidence is attached only when corresponding CLI include flags are set. Tests explicitly assert Phase 5, version-band and AI/router evidence stays report-only; default detected component versions remain unchanged; uncertainty summaries and source-validation caveats appear in reports. The SBOM metadata may carry a report-only version-band marker, but experiment-selected versions do not replace components.
- Diagnostics may re-run DEX analysis for report-only obfuscation signals, separate from matcher analysis; this is additional runtime work and reinforces that report diagnostics are not additional matching authority.
- This establishes interface-level intent in source/tests, not correctness on every path or empirical no-change across all real data (the original reports/reference DBs are absent). No CLI command, test, or experiment was executed.

## Experiment decision evidence: multi-scale R8 and version-band branches

- Re-opened current Phase 4/5 diagnostic reports, version-band v2/v3 artifacts, and promotion-verification reports. The Phase 4 full multi-scale blend is treated as rejected globally after target gains co-occurred with regressions; the report taxonomy keeps controlled cases, source-aligned real rows, conflicting rows, unvalidated rows, target-improvement candidates and regression-risk rows distinct. Phase 5 narrows the Phase 4 candidate profiles to four target suggestions, reports zero triggered regressions/conflicts in its retained diagnostic, and remains experiment-only because profiles came from a small candidate set and require explicit opt-in.
- Phase 5's report-evidence artifact says four report-only suggestions across AntennaPod, Wikipedia, Aegis and Nextcloud; zero default selection changes. In `test_report.py`, an explicit fixture similarly keeps baseline SBOM version 1.0.0 while displaying diagnostic suggestion 1.1.0. Historical runtime smoke is documented, but its report JSON is absent in this ZIP.
- Candidate-expansion v3 separates a source-known opportunity (565/582 upper-bound fixable wrong rows) from source-free reranking (0 APK-only changes/fixes, 0 exact-control regressions) and a deep candidate expansion pilot that selected old incorrect `1.2.0-alpha01` from 134 versions instead of source `1.8.1`. Thus it is rejected: source knowledge shows an opportunity but cannot drive APK-only version selection.
- Guarded literal/context promotion verification documents a progression: raw signal (0 improvements, 2 regressions), broad one-match gate (2 improvements, 2 risks), strict >=2 gate (one VLC improvement while filtering three weak suggestions), then a 24-controlled/224-row real control readiness pass and no-flag VLC smoke. Current code/tests confirm threshold mechanics; the reports' APK/DB evidence inputs are unavailable here, so counts remain historical rather than reproduced.
- Composite shortlist promotion record describes the prior rejected package/class-only proxy losing source families, then the balanced dependency/literal-aware profile retaining full version bands and independent-support rescue. Its historic 81-case validation and full-control no-flag/disable smoke report no selected-version drift and 16.63% fewer reference rows. This supports a search-cost/pruning claim, not accuracy improvement; source rows/results needed for independent verification are missing.
- The dated PFE examiner review records corrections to unsupported scope language: the extractor does not inspect APK signatures; it analyzes successfully parsed DEX files; archive asset/resource inventory is separate from DEX literals; manifest data are declared permissions/metadata. Current extractor code is consistent with those corrections. The review itself says its compiled 122-page PDF predates the last source changes and requires a final rebuild, so do not treat its older PDF as the final source snapshot.
- These results add decision rationale but do not constitute raw-data re-execution. No tests or experiments were run.

## Path-level review register

`papers/PROJECT_FILE_REVIEW_REGISTER.csv` is the working path census. Current register snapshot covers **1,714 files plus 303 directories** under the workspace; it excludes its own CSV row by design, and its metadata size is only a point-in-time snapshot. Current register states: 67 files fully read, 53 partially read, and 1,897 inventoried entries not content-reviewed (1,594 files plus 303 directories). Directory rows remain inventoried until their role/contents have been considered. Update this register as review progresses. The early checkout table above was captured before later paper-study artifacts and differs by one or more files; use the live register for current path accounting.

## Literature synthesis audit: early design claims vs retained implementation

- Read all of `papers/state_of_the_art.md` and `papers/data/impact_on_project.md`; inspected the synthesis table's opening section and the structured paper overview in part. The narrative documents are historical synthesis/planning material, not a reliable description of the final implemented system.
- The early synthesis proposes Bayesian version scoring, LibMD-style multi-scale fusion as the MVP foundation, LibAttention as an R8 first-pass filter, and evaluation on TPL-Benchmark. Current matcher source does not implement Bayesian scoring; multi-scale/R8 branches are diagnostic or report-only/rejected; the AI path is opt-in report evidence rather than LibAttention; and the retained empirical evaluation is not a TPL-Benchmark evaluation. These are design lineage or proposals, not paper claims about completed work.
- The synthesis also overstates cross-study conclusions: a single TPL-Benchmark score is described as a “realistic ceiling” or universal benchmark to beat; metrics from different datasets/protocols are placed in direct rankings; and resilience matrices/open-challenge claims need paper-by-paper verification. Treat each number as source-specific and record dataset, transformation, candidate universe, metric, and denominator before using it.
- Path review state: `impact_on_project.md` is content-read (claims not all source-verified); `state_of_the_art.md` is content-read but its empirical references are not all validated; `SBOM_Tools_Synthesis_Table.md` and `papers_overview.json` are partial reads. Primary PDFs still control related-work claims. No tests or experiments were run.
- This reinforces the paper rule: distinguish implemented behavior, diagnostic experiments, rejected branches, early proposals, and independently reproduced evidence. Review remains incomplete across the project tree.

## Thesis contribution and evaluation boundary: initial source cross-check

- Inspected the source chapter structures and the research-question passages in both thesis source trees. The Master thesis asks how heterogeneous APK evidence can support trustworthy component/version claims with provenance, confidence, uncertainty, and validation boundaries; its supporting questions concern evidence types, prior combinations, evidence strength, conflict/missing evidence, auditable SBOM claims, and bounded evaluation.
- The PFE thesis has a separate implementation/evaluation objective: a static, bounded CycloneDX SBOM workflow with confidence-aware vulnerability analysis. Its four RQs separate controlled exact-version capability, clean vs difficult real APK behavior, reference/matcher coverage vs the full source denominator, and downstream uncertainty/authority preservation.
- PFE's own conclusion reports 927/1,837 emitted Maven versions confirmed across 102 source-validated APKs that emitted Maven rows, four further source-validated no-Maven-signal controls, and 927/12,082 end-to-end source dependency denominator. Keep these denominators attached to their claims; do not collapse them into a single accuracy percentage. These are thesis-retained documented results; the current checkout does not contain all inputs needed to independently recalculate them.
- The PFE chapter structure explicitly separates implementation/evaluation, vulnerability demonstration, AI/R8 evaluation, failed/non-promoted experiments, discussion, and threats to validity. This supports selecting a narrow implementation/evaluation paper while retaining rejected experiments as rationale/limitations rather than presenting all work as successful.
- This was a source-structure and selected-passage pass, not a full read of either thesis. The Master framework chapter, full PFE evaluation chapter, appendices, and final PDF/source version reconciliation still need line-by-line review. Relevant source files remain `partial` in the path register.

## PFE evaluation chapter: complete source read and evidence-availability cross-check

- Read all of `thesis/pfe/chapters/ch06_implementation_evaluation.tex`. Its scope is broader than the paper's eventual core: implementation and CLI, evaluation protocol, controlled and source-validated real APKs, full source denominator, source-known upper bound, vulnerability examples, AI/R8 experiments, failed promotions, comparison, RQ discussion, and validity threats.
- The thesis correctly separates key measures: 84/84 expected versions in 72 controlled fixtures; clean 47/47 emitted rows across 5 apps; partial 880/1,790 across 97; aggregate 927/1,837 across 102 apps with emitted Maven rows (50.5%, explicitly an emitted-version confirmation rate); 4 additional zero-emission source controls; full source denominator 927/12,082 (7.7%); and 6,772/6,772 only after source-version-constrained candidate slicing. Preserve the denominators, app counts, and lane labels whenever these figures are considered.
- AI figures are project-derived, not an external Android benchmark. The chapter itself reports grouped case splits, shortcut risks, Random Forest class weakness, an MVP-safe Transformer drop from the full profile, and a raw-opcode model below the simple baseline. AI/R8 remains report-only; the integration gate compares default and opt-in outputs on two targets and is not evidence of broad generalization.
- Reproducibility check: the chapter and `docs/thesis/PFE_CHAPTER6_EVIDENCE_SNAPSHOT_2026-06-20.md` cite a frozen 2026-06-20 snapshot, commit `2983d54`, and JSON outputs under `data/results/evaluation/`. In the current ZIP, `data/results/` and `data/reference_db/` contain only `.gitkeep`, `.git` is absent, and the named `apk-type-evaluation.json` is absent. `docs/evaluation/THESIS_EVALUATION_TABLES.md` and other narrative snapshots remain, but `scripts/build_thesis_evaluation_tables.py` cannot regenerate them without its default input. Treat thesis numbers as retained historical evidence pending the raw artifacts; the snapshot's test count (275) and successful compileall are historical and were not rerun.
- The chapter says feature storage is transactional. Current `reference_features.py` upserts the component and clears old feature rows before checking each DEX path; a missing DEX returns a failed result without raising, so the surrounding SQLite context may commit the removal/partial write. This failure-path discrepancy needs code/test repair or at minimum accurate documentation before the paper calls storage atomic. No test or execution was performed to trigger it.
- The dashboard PNGs are retained in the thesis tree, but the cited original `report.html`, SBOM and OSV output directories are absent from this ZIP. The figures can document the retained presentation only after visual review; their historical generated artifacts cannot be independently re-opened here.
- Review status: this thesis source chapter is now content-read in full, but its empirical claims are not independently reproduced. The evidence snapshot is read in full as a claim map; evaluation tables, results summary, and decision ledger are partial reads. Do not conflate content review with reproduction.

## Master thesis core: evidence-trust framework fully read

- Read all 804 lines of `thesis/master/chapters/ch04_evidence_trust_framework.tex`. Its contribution is a policy/model above detectors: explicit claim fields; separate identity/version/relationship/security granularity; evidence levels E0-E5; quality dimensions (directness, uniqueness, independence, version specificity, transformation resilience, reference coverage, provenance and conflict); conflict/abstention actions; confidence caps; claim classes; validation-lane boundaries; and monotonic vulnerability authority.
- The expression `trust(C)=f(S,D,I,V)-g(K,R,T)` is explicitly conceptual, not calibrated probability. The chapter also explicitly says it does not implement Dempster-Shafer inference. The proposed lifecycle runs from extraction/candidate generation through provenance/quality/fusion/claim class to emit-or-abstain.
- Its PFE case study is framed as representational coverage and authority preservation: can project outcomes (clean/partial, source-known upper bound, failed promotions, AI/R8 report-only, native/hidden boundaries) be expressed without changing their evidentiary meaning? It expressly does not establish calibrated probabilities, complete detector coverage, or independent analyst agreement.
- Runtime distinction verified with a scoped search of `src/apk_sbom` and `tests`: the implementation has practical overlapping controls (identity and version confidence, ambiguity, source-validation labels, report-only gates), but no `RecoveredClaim`, formal claim-class hierarchy, E0-E5 ledger, or general framework lifecycle implementation. Thus the Master framework is a proposed analytical/reporting framework evaluated retrospectively through PFE artifacts, not a second implemented matcher or inference engine.
- This matters to the English implementation/evaluation paper: present the PFE software and empirical results as the implemented system; use the Master framework to motivate evidence/authority boundaries only to the extent the paper's scope needs it. Do not claim the framework schema itself is encoded by the current runtime.
- The chapter's case-study numbers inherit the PFE frozen snapshot limits already recorded: underlying result JSON/DB/APKs are absent in this ZIP, and no reproduction or tests were run. The chapter content is fully reviewed; independent numerical verification is not.

## Reference feature-store implementation and test coverage: full pass

- Read all of `src/apk_sbom/reference_features.py` (696 lines) and all of `tests/test_reference_features.py`. The module loads conversion JSON, discovers/sorts metadata with coordinate/offset/limit/skipped filters, creates a SQLite component table and child tables for DEX evidence and POM dependencies, extracts DEX feature rows, aggregates database counts, and re-extracts by upserting a coordinate/version then clearing child rows.
- The test file has exactly three tests: skip/include-skipped discovery, offset behavior, and successful synthetic feature insertion. It checks persistence of package/class/method/opcode/dependency-shape/literal/API and diagnostic feature families plus a POM dependency row. It does not test missing DEX paths, failed replacement behavior, mid-write exceptions, rollback, or old row preservation.
- Failure-path control flow is now established statically: `_store_conversion_features` upserts the component and deletes existing child rows before checking each DEX path. A missing file returns a `status="failed"` result normally; the outer `with sqlite3.connect(path)` then exits without an exception. Python's documented SQLite connection context manager commits when its body finishes without exceptions and rolls back on uncaught exceptions ([Python sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html#how-to-use-the-connection-context-manager)). Thus the current structure can commit deleted old rows and/or a partial set of new rows; if it returns early, component class/method counts may remain from the old record. This is a code-path defect risk, not an observed run or evidence that a retained historical database was damaged.
- This statically confirms that Chapter 6's statement that re-extraction rewrites child rows transactionally is too broad for failure cases. Before relying on that property, the implementation should stage/validate all DEX input before destructive writes or use a per-component savepoint/exception rollback, and tests should cover missing-first/missing-later DEX plus preservation of old data. This study did not modify the source or run tests.

## AI/R8 final evaluation aggregation: source, tests, wrapper, and retained reports

- Read the full 450-line `src/apk_sbom/ai_r8_final_evaluation.py`, its CLI wrapper, all 202 lines of `tests/test_ai_r8_final_evaluation.py`, and the retained AI final-evaluation and MVP integration-gate Markdown reports.
- The module aggregates upstream JSON for Phase 6A/6B metrics, corpus summaries, integration-gate decisions, and one report-only comparison. It is not the model training/evaluation implementation. `_load_json` returns `{}` for a missing path; therefore a rebuild can write an incomplete report rather than fail fast. The required raw JSON inputs are absent under current `data/results/`, so none of the documented metrics can be regenerated from this ZIP.
- `test_ai_r8_final_evaluation.py` contains two synthetic-input tests: dictionary-to-report aggregation and CLI file emission. They do not train models, recreate the grouped split, or validate the historical smoke-test JSON. `report_only_guardrail_passed` is specifically the conjunction of `detected_components_unchanged`, `sbom_semantic_content_unchanged`, `vulnerability_labels_unchanged`, and `ai_report.report_only`; it is an aggregator predicate, not an independent replay of the report comparison.
- The retained report records 20,523 project-derived rows, Random Forest macro-F1 0.7076/accuracy 0.6903, full structured-token Transformer macro-F1 0.9772/accuracy 0.9920, MVP-safe Transformer 0.8822/0.9069, and raw-opcode Transformer macro-F1 0.1098 versus 0.1281 baseline. Keep them framed as project-evidence report-action classification, not external APK library-detection performance. The grouped split reduces same-case row leakage, but the corpus remains internal and has label/context shortcut risks acknowledged by the report/thesis.
- The report-only retained demo states `sbom_raw_sha256_unchanged=False` while `sbom_semantic_content_unchanged=True`; it supports unchanged component semantics, not byte-for-byte SBOM identity. This aligns with report metadata allowing diagnostic markers. Paper language should state semantic component/version/vulnerability stability and disclose report metadata where relevant.
- The separate integration-gate Markdown reports two smoke targets and zero strict APK-only candidates after controls, but those source JSONs are absent. The distinction remains: retained reports document the historical decision; current tests prove only aggregation on synthetic fixtures. No test/experiment was run here.


## AI/R8 MVP integration gate: decision logic and negative-only test coverage

- Read the full 576-line `src/apk_sbom/ai_r8_mvp_integration_gate.py`, its CLI wrapper, all 184 lines of `tests/test_ai_r8_mvp_integration_gate.py`, and the complete retained gate report.
- The gate combines metric/corpus/smoke JSON; it does not execute training or replay report comparisons. Missing source JSON is read as `{}`. Report-only readiness requires trained Random Forest, macro-F1 >= 0.60, positive accuracy delta over a baseline, and report-only guardrails (hybrid report flag/verdict/default matcher unchanged plus final smoke `all_outputs_unchanged` and all sections visible). MVP-safe DL has a similar >=0.60/report-only threshold; structured DL stays research evidence; raw-opcode remains research-only and its baseline delta is considered for the higher authority candidate gate.
- Strict-gate summary computes eligible rows after controls and gate-pass rows, but the authority decision function only consumes `strict_candidates_available`, raw-opcode delta > 0, and report-only guardrails. It does not consume the reported `production_promotion` or `default_matcher_unchanged` fields. If future inputs satisfy those three conditions despite `production_promotion=False`, the output can label matcher authority “ready” as a candidate. Other fields still hard-code `sbom_or_cve_authority_ready=False` and say no authority until a live regression suite passes, so this is a status-consistency weakness rather than current promotion; the retained real report has zero eligible rows and decision blocked.
+- The tests cover source-token removal for the MVP-safe profile, a tiny corpus metadata result, a synthetic negative decision with 0 eligible rows, and JSON serialization with empty inputs. They do not cover the positive strict-gate path, contradictions between eligibility and production-promotion flags, nor perform the two-target smoke comparison. The `all_outputs_unchanged` value is supplied as fixture/input evidence.
+- The report's two-target smoke and zero strict-candidate values are retained historical claims; their JSON sources are absent. The gate's tests show decision-policy behavior on synthetic fixtures, not that historical smoke or model metrics are reproducible from this ZIP. No tests or experiments were run.


## Structured-token AI corpus construction: source shortcuts and evaluation scope

- Read the full `scripts/build_ai_r8_token_corpus.py` and `tests/test_ai_r8_dl_prototype.py`, including the token-generation functions and grouped-split handoff to `ai_r8_assistant.py`.
- The full profile exposes raw coordinate, source version, candidate version, all 17 structured features, and diagnostic context fields. The MVP-safe profile removes raw coordinate, raw source/candidate versions, source-rank and boundary/clean/partial flags, and context labels; it retains row source (`src:...`), group/artifact name tokens, selected matcher features, candidate-version shape, and R8/minification flag. So describe it as removing explicit source-version and diagnostic-context shortcuts; “source-free” without qualification overstates independence from source-derived row lineage.
- The row labels themselves are derived from project evidence rules (`recall_status`/`next_action`, source-validation `reason_label`/coverage/triage, and Phase 5 outcomes). The full profile includes fields closely related to those labeling rules, which explains its shortcut-risk warning. The safe profile drops context but still preserves row-source categories such as `emitted-result`, `matcher-recall`, `boundary`, and `phase5`.
- Group split is case-level: case IDs are sorted and assigned deterministically by position modulo ten (20% test, 10% validation, 70% train; with small-data fallbacks). This avoids rows from one APK/case crossing splits, but does not enforce coordinate- or project-level holdout; the same coordinate family can occur across cases and group/artifact tokens remain in the safe profile. The token corpus builds its vocabulary by scanning all rows before splitting; token vocabulary is unsupervised, but it still uses held-out feature distribution and should be understood as transductive rather than strict train-only preprocessing.
- `test_ai_r8_dl_prototype.py` uses 12 hand-built rows. It checks no explicit `label:` token, padding/split names, and output metadata; it does not detect context-derived label leakage, row-source proxies, coordinate/project overlap, or train-only vocabulary leakage. The separate gate suite tests some safe-profile exclusions but also uses synthetic rows.
- Therefore Transformer macro-F1 is evidence about reproducing project-defined report-action labels on a case-held-out internal corpus. It is not a library/version detection score and is not evidence of out-of-project generalization. No model was trained and no tests were run during this review.


## Phase 6A assistant: training labels, leakage, suggestions, and unit-test boundary

- Read all of `src/apk_sbom/ai_r8_assistant.py` (1,241 lines), all of `tests/test_ai_r8_assistant.py` (295 lines), and `docs/evaluation/AI_R8_ASSISTANT_DIAGNOSTICS.md`.
- Phase 6A combines rows from matcher-recall diagnostics, transparency emitted results, transparency source-boundary rows, Phase 5 diagnostics, and R8 boundary rows. Its six labels are generated by rules from recall status/next action, source-validation reason/coverage/triage, or Phase 5 outcome. It trains a 200-tree, depth-8, class-balanced RandomForest (random state 42) over 17 numeric/boolean features; case IDs are sorted and assigned to test/validation/train in 2/1/7 modulo-ten buckets. Splitting is case-level, deterministic, and not stratified or coordinate/project-heldout. Test macro-F1 averages all six labels with zero-division set to zero; prediction probabilities are reported as confidence without a calibration study.
- Direct target leakage is present in at least the transparency boundary rows: the label is computed from reason/coverage/triage, then `is_boundary_or_limitation` is set to true when that label is `boundary_do_not_suggest`. The classifier trains on that same field; it is also the second-highest feature importance (0.217) and removing all boolean context flags drops macro-F1 from 0.708 to 0.564. This means reported RF performance is partly label-rule recovery, not independent evidence of robust report triage. The full Transformer has further explicit context-token leakage already recorded above.
- The MVP-safe Transformer omits that feature and diagnostic context, but retains row-source tokens. Row-source categories constrain/encode label construction (e.g. emitted-result rows are exact vs mismatch; boundary rows are restricted to boundary/mismatch/risk labels), so describe any result as an internal, source-lineage-aware report-action task, not an independent source-free ML benchmark. It also leaves cross-case coordinate overlap possible.
- Suggestion generation loads the saved RF when available and uses predicted labels/probabilities; if no model exists it falls back to training labels (`heuristic-label-fallback`) with fixed 0.5/1.0 confidence, so that mode is rule replay, not inference. `confirmed_exact` predictions are suppressed; mismatch and boundary predictions become `risk_only`; all outputs are marked report-only with forbidden effects. The retained diagnostics report 13,736 suggestion rows, but source JSON/model files are absent, so this output is not regenerated here.
- The seven tests construct four synthetic rows for label mapping, check feature normalization/vector helpers, boundary labeling, optional dependency detection, heuristic suggestion schema, and opt-in report rendering with a synthetic component. They do not call `train_ai_r8_assistant`, fit RandomForest, validate predictions/metrics, assess calibration, test label leakage, or run an actual APK.
- Consequence for paper framing: do not cite RF macro-F1 0.708 as evidence of general Android detection or independent triage quality. If AI is retained, identify it as an exploratory classifier that learns project-defined report labels, flag boundary-label leakage and row-source shortcuts, and keep deterministic matcher authority. No source was changed; no model/test/experiment was run.


## Phase 6B structured-token Transformer: trainer and metric provenance

- Read all 488 lines of `scripts/train_ai_r8_tiny_transformer.py` and the complete full-profile and MVP-safe Markdown reports. The script reads a pre-split corpus, constructs a small embedding + learned positional embedding + one-layer TransformerEncoder + masked mean-pooling classifier, trains with AdamW and inverse-frequency weighted cross-entropy, and evaluates macro-F1/accuracy over the six project-defined report-action labels.
- Default configuration is 3 epochs, batch size 128, d_model 64, four heads, one encoder layer, learning rate .001, and torch seed 42. It evaluates validation after each epoch but does not early-stop or restore the best validation checkpoint; the full-profile report's validation macro-F1 is best at epoch 2 (~0.979) and falls to ~0.948 at epoch 3, while the reported test result is from the final epoch (~0.977 macro-F1, .992 accuracy). The MVP-safe run reports five epochs and final-epoch .882 macro-F1/.907 accuracy.
+- It saves state dict/config metadata but does not define or exercise a production inference path; report wiring remains disabled. The trainer has no matching unit test: `test_ai_r8_dl_prototype.py` tests tokenization/corpus construction only, and no test references `TinyTransformerClassifier`, `_evaluate`, or this trainer. Thus retained Markdown training histories/metrics are not reproducible from the current tests.
+- Rechecked current workspace paths: both token corpus JSONs, both metrics JSONs, and `tiny-transformer.pt` are absent. The two Markdown reports remain, but the actual model/corpus cannot be reloaded or independently rescored.
+- The prototype is a learned classifier over engineered/project-labelled evidence tokens, not LibAttention's large-scale Smali pretraining and not a bytecode library/version detector. Its high full-profile score is especially vulnerable to context leakage recorded above; the lower safe-profile score still inherits case-only split, row-source/name-token shortcuts, and transductive vocabulary construction. Retain only as workflow/negative-authority evidence and explain these validity boundaries.


## Raw-opcode corpus and Transformer: implementation and retained negative result

- Read the complete raw-opcode corpus builder, Transformer trainer, four-test suite, and both retained Markdown reports. The builder processes DEX files and methods in APK/archive iteration order, stores only nonempty opcode-name sequences, and caps each APK at 120 sequences. It wraps each sequence in `<cls>`/`<sep>`, retains at most 126 opcode tokens, then pads to length 128. The corpus contains 14 APKs (12 generated Commons Codec/Gson transform variants and two real smoke APKs), 1,680 method rows, seven labels with two APK cases apiece, and a vocabulary of 135 tokens.
- Labels come from the APK filename's R8 profile for generated/controlled fixtures or path-derived role for real APKs. They describe APK/profile classes, not method-level ground truth or library identity. Vocabulary is constructed from all rows before train/test splitting, so token identities are seen for held-out cases (without labels); evaluation should disclose this transductive vocabulary construction.
- Test holds out the lexically last APK case for each label (one APK per class; 840 method rows). Validation selects a deterministic hash bucket of method rows from the remaining APK cases, so those APK cases contribute rows to both train and validation. The experiment uses a one-layer 64-dimensional Transformer encoder, eight fixed epochs, and final-epoch weights; there is no early stopping or best-validation checkpoint restore. The main baseline is logistic regression over opcode-token counts.
- Retained results: test macro-F1 is 0.1098 for the Transformer versus 0.1281 for the opcode-count logistic-regression baseline; both test accuracies are 0.1464. The report verdict is not promotable. This is a small project-local negative result for seven-way APK/profile triage, not component/version detection or an external generalization benchmark. The code keeps it report-only with no matcher, SBOM, or CVE wiring.
- Four tests cover held-out test-case assignment, special-token filtering in count features, non-promotion verdict logic, and report guardrail wording. They do not train the model, build the corpus, or assert that validation is APK-case-disjoint. Both Markdown reports are retained, but corpus JSON, metrics JSON, and the saved `.pt` model are absent from this ZIP; numbers remain historical outputs and were not regenerated. No tests/training were run.
- The five reviewed corpus/trainer/test/report paths are marked `full` in `papers/PROJECT_FILE_REVIEW_REGISTER.csv`; full means content-read, not empirical reproduction. The broad project review remains active.

## APK inspection and DEX feature extraction: full source read

- Read all of `src/apk_sbom/apk_extractor.py` and `src/apk_sbom/dex_analyzer.py`. APK inspection hashes the whole archive, enumerates ZIP entries, separates standard top-level `classes*.dex` from DEX-like nonstandard paths, reads native libraries fully to hash them, parses a small subset of manifest metadata/permissions, and creates heuristic packaging-risk indicators. It does not verify APK signatures or recover native package/version identities. Manifest parsing failure is retained as parse status/error rather than inferred metadata.
- Main DEX analysis includes only ZIP members whose basename matches `classes*.dex`; DEX-like files elsewhere can appear in forensic reporting but are not sent to `analyze_dex_bytes`. Each successfully parsed DEX contributes packages, classes/method counts, opcode histograms, 3-opcode n-grams, and structural fingerprints. With `include_members=True`, it additionally gathers signatures, references, internal dependency edges/shapes, string literals, API references, field operation summaries, and literal-context hashes. Feature extraction is static and parser-dependent; parse errors are recorded per DEX instead of failing the whole APK analysis.
- Specific boundaries: string literal parsing depends on Androguard-rendered instruction text; “API references” are descriptor-like references found in instruction output and are not a platform compatibility or vulnerability verdict. Basic-block splitting uses a finite opcode-prefix list; call-chain and field-operation fingerprints hash the encountered subsequences. These are engineered features, not control-flow graph recovery or semantic equivalence proof.
- Both modules are now marked `full` in the path register. This is source review only; no APK was reprocessed, no tests were run, and downstream CLI/report/matcher behavior still needs its own complete source and test trace.

## Source-validation implementation and interpretation boundary

- Read all of `src/apk_sbom/source_validation.py` and the complete `tests/test_source_validation.py`. The parser considers Gradle dependency-tree rows with `+---`, `\---`, or `|` prefixes, extracts Maven-like `group:artifact:requested` tokens and any `-> resolved` version, and groups all occurrences by `group:artifact`. The validator compares Maven CycloneDX component coordinates against that grouped tree and marks exact version-string membership as confirmed, coordinate-present with a different version as mismatch, and absent coordinate as missing. It can separately compare manually supplied candidates.
- The result does not compare APK bytes to source code, prove that every source dependency appears in the APK, identify variants/classifiers beyond the coordinate/version token, or establish source completeness. It is a source-tree concordance check when a relevant resolved Gradle tree is available. If multiple resolved versions for one coordinate occur in the input tree, any exact match is counted confirmed; retain the source versions/variant context when interpreting aggregates.
- Tests are synthetic: they exercise Gradle parsing/resolution, confirmed/mismatch/missing classification, and extra-candidate report output. They do not establish that all real Gradle output dialects or multi-variant source trees are parsed exhaustively. Test file had already been read and remains `full`; the implementation is now marked `full`. No tests or real-case validation were run.

## Matcher implementation: current orchestration and score semantics (partial pass)

- Re-read the matcher’s orchestration, data models, weighted component scoring, confidence/decision classification, version candidate selection, and reportable-candidate filtering. For each reference version, score combines reference-denominator package/class/method coverage, opcode cosine similarity, dependency evidence (65% exact internal dependency-edge coverage + 35% dependency-shape similarity), literal coverage, and sibling-version-unique class/method/literal coverage. Default weights are package .15, class .45, method .25, opcode .15, dependency .10, literal .08, version-unique .12; API and opcode n-gram weights are zero. The aggregate is normalized by active weight and rounded; it is a heuristic similarity score, not a calibrated probability.
- Version selection is not always the raw aggregate leader. The reviewed selection path can choose a nearby candidate with more version-distinctive features, guarded unique-literal/context evidence, POM dependency support, or application-era coherence. Thresholds and score margins gate these rerankers. Identity confidence is recomputed from a separate weighted set of evidence dimensions and classified separately from version confidence; single-reference version evidence is capped unless near-complete match conditions hold. Uncertain versions are normally suppressed, with limited artifact-family exceptions and suppressed alternatives preserved in the output.
- At the time of this entry, this was a partial source pass; see the completed matcher audit below for the later full-file review. No empirical results were reproduced.

## Composite family shortlist: runtime meaning and test boundary (partial)

- Read the matcher’s shortlist implementation, the simulation policy/scoring path in part, and all three synthetic shortlist tests. Runtime first scores each Maven coordinate over package, class, method, dependency and literal evidence using the balanced-context weights. It compares each coordinate’s best version-family score to the best family score; every version row for a retained coordinate is preserved, so pruning is at family level and cannot reduce that coordinate’s version band. Families within the configured 0.10 margin are kept; rescue can also retain families with at least one matched dependency edge, at least two matched literals, or class overlap plus one additional method/dependency/literal signal.
- The controlled simulation is an offline design gate over report-derived rows, grouped per APK report, with profiles/margins and source-family-loss rejection. The unit tests use small synthetic rows and check recommendation/rescue rules only. Historical validation figures remain dependent on absent input report JSONs; the tests do not establish live accuracy improvement or source-family retention over the original APK corpus. The runtime shortlist narrows search work before scoring; it does not itself select versions or demonstrate accuracy uplift.
- At the time of this entry, matcher-test review was partial. The 33-test file has since been read in full (but not run), as recorded below. The shortlist simulation module remains `partial`; its test module is `full` in the register.

## Matcher follow-up: family rules, version coherence, and prefilter boundaries

- Re-read the remaining artifact-family and coherence logic plus representative end-of-suite matcher tests. Hard-coded artifact-family rules cover Okio (`okio`/`okio-jvm`), OkHttp (`okhttp`/`okhttp-android`), and selected Lifecycle public/Android pairs. The winner logic applies confidence-aware score margins and lifecycle version hints; selected/suppressed alternatives are recorded as `artifact-family-disambiguation` evidence. A scoped Lifecycle path may allow an otherwise uncertain Android target row back into output and relabel it as a low-confidence candidate if its identity is supported; this is an explicit exception, not the default uncertain-version policy.
- Compose version coherence is restricted to four named Android coordinates. It can rerank a lower-scoring candidate when independent same-version selected candidates in the family provide greater support, or downgrade a weak `runtime-android` decision when at least two other supported family components point to another release. The POM coherence path similarly uses runtime, non-optional, explicit dependency versions only when another independently supported component matches. These rules are deterministic project-specific coherence heuristics; their assumptions and domain scope must be named if discussed.
- The package-overlap SQL prefilter is opt-in and defaults off. If used with `per_coordinate_limit`, it ranks reference versions by shared package count and lexicographic version/component tie-breaks before expensive feature scoring; this can exclude the true version for package-poor/obfuscated APKs. It is distinct from the promoted composite family shortlist, which is enabled by default and preserves every version for a retained coordinate.
- Matcher unit tests include synthetic cases for component coverage, optional opcode/API/ngram weights, disabled multiscale features, DB-backed ranking, optional shortlist pruning, unique-version/context selection and disable flag, ambiguity reporting, POM/app-era coherence, and scoped artifact-family selection. I read several separated portions but not the complete test file or every test fixture/helper, so `tests/test_matcher.py` and `src/apk_sbom/matcher.py` remain `partial`. No tests were run.

## CycloneDX, vulnerability triage, and report orchestration

- `src/apk_sbom/models.py`, `src/apk_sbom/sbom.py`, and `tests/test_sbom.py` are content-read. The SBOM is CycloneDX 1.5: APK is the metadata application component; Maven library components carry PURL, score/status properties, serialized evidence and ambiguous-version properties; native `.so` entries are CycloneDX file components with path/ABI/size/hash and explicit `hash-only` identification. The dependency graph lists the APK as depending directly on all emitted Maven and native components; it does not reconstruct transitive dependency relationships from APK bytes. Serial UUID/time are generated unless explicitly supplied. Synthetic tests verify shape/properties/hash-only native identity, not a formal CycloneDX schema validator.
- Read all of `src/apk_sbom/vulnerability.py` and `tests/test_vulnerability.py`. OSV queries use each detected Maven coordinate and selected version in one batch request; each input library is paired to the response by list index. Missing per-library response slots become failed results; the implementation records but does not page through a returned `next_page_token`. A finding is `confirmed` if identity is supported and version is exact/high or its score is at least .90; otherwise an OSV hit is `potential`. Optional detail fetch is best-effort for request exceptions; duplicate IDs/aliases are merged and OSV severity labels normalized.
- Source validation can only preserve or reduce downstream authority: a confirmed source row leaves the existing finding class intact; mismatch, missing coordinate, unknown status, or missing source row makes a vulnerability potential. Source concordance does not independently prove bytecode inclusion. Tests mock HTTP and cover request shape, parsing/enrichment, low-confidence potential status, source mismatch downgrading, severity/deduplication, and SBOM property reload. These are deterministic unit tests, not a live OSV retrieval demonstration. The two vulnerability paths are marked full; no test or network scan was run.
- Read the main `generate_final_report` path in `report.py` (still partial overall). It inspects the APK, matches against the reference DB, converts decisions to reportable Maven components, computes obfuscation diagnostics, attaches optional report-only experiment/AI evidence, writes `matches.json` and CycloneDX JSON, optionally queries OSV and applies source validation, then writes JSON/Markdown/HTML reports. Diagnostic DEX analysis is a second pass and its exceptions are caught as `None`. OSV HTTP errors from the main query are not caught by this orchestration path. Source validation is optional and must be supplied explicitly. Experimental report loaders annotate evidence but do not train models or re-run their source dataset.
- Report and matcher test files remain partial. No report generation, OSV request, test, or end-to-end experiment was run. Missing source APK/reference DB/result JSON still prevents reproducing retained evaluation tables.

## Report evidence attachment and SBOM metadata nuance

- Further read the evidence loaders in `report.py` and selected report tests. Phase 5, version-band, minified-policy, RF, hybrid-router, DL-status, and structural-gate records are loaded from supplied JSON and matched by APK path/stem/case and, in some paths, by detected coordinate. They are not recomputed during report generation. Matching is not uniformly exact: case matching allows either normalized case string to be contained in the APK stem, and several loaders also include any row whose coordinate is among emitted components. A report-only label is a policy declaration; the code still trusts and renders those JSON fields.
- Clarification verified in both source and `test_generate_final_report_attaches_version_band_evidence_as_report_only`: optional version-band evidence leaves selected component versions unchanged but adds two `apk-sbom:mvp:version-band-*` properties to CycloneDX metadata. Therefore claim semantic component/version authority stability, not byte-for-byte/metadata-identical SBOM output. This is consistent with the retained final evaluation distinguishing raw-SHA change from semantic component stability.
- The hybrid AI/router attachments are embedded in JSON/Markdown/HTML reports and do not feed `components` or the OSV input; their test keeps the baseline component version in CycloneDX. Report loader and test modules remain partial-read; no report was generated.

## Report-only uncertainty and obfuscation indicators (partial report-module pass)

- `assess_obfuscation_risk` is a fixed heuristic score built from nonstandard DEX-like entries, APK extraction-indicator level, parser failures, low-confidence emitted-version share, and structural-over-package evidence. It is not a trained obfuscation detector or a calibrated probability. The additional R8/obfuscation diagnostics are separately serialized and presented as report-only evidence.
- `build_version_uncertainty_summary` derives display categories from existing decisions (explicit ambiguity, near tie, uncertain/low-confidence status, one-reference boundary, or policy-selected version) and records whether that decision was actually emitted as a component. It does not change selection. This is useful for describing transparent uncertainty, but category counts are decision-row counts, not independent component errors.
- Current `report.py` and `tests/test_report.py` remain partial-read: core generation, JSON evidence loaders, risk/uncertainty functions and focused tests have been inspected; full Markdown/HTML rendering and full test coverage still remain.

## Matcher source and complete test file audit

- Completed a function-by-function source review of `src/apk_sbom/matcher.py` and content review of all 33 `tests/test_matcher.py` test functions/fixtures. The matcher loads reference feature rows by component/version, computes reference-coverage and cosine/graph scores, derives sibling-version-unique class/method/literal sets, makes separate identity and version classifications, applies guarded version rerankers/ambiguity rules, then groups selected decisions under explicit artifact-family policies. It also supports a separate package-overlap SQL prefilter that is off by default.
- The test file primarily unit-tests score arithmetic and policy decisions with hand-constructed features; one SQLite-backed test exercises end-to-end matcher orchestration on synthetic DB rows, and one tests default composite-shortlist pruning versus disabling it. It exercises negative as well as positive guardrails (single-match cap, no weak context flip, no unsupported POM support, near-tie ambiguity, unsupported app-era downgrade). Tests do not call real APK parsing or the archived historical data/results; no tests were executed.
- Updated register status: matcher implementation and its test file are now `full` (content reviewed), not empirically reproduced. The matcher review is complete as source reading; overall project review remains active with other files and folders unreviewed.

## Project handbook implementation pages: cross-check against current code

- Read all six `docs/project_handbook/implementation/*.md` pages and compared their claims to current source. The matcher page correctly explains reference-coverage scoring, non-probabilistic score meaning, identity/version distinction, ambiguity and coordinate-filter limitations, but calls the shortlist “optional”; current `match_apk_to_reference_db` defaults `enable_composite_family_shortlist=True` (there is an explicit disable switch), while package prefilter defaults off. Wording should distinguish “enabled by default but disableable” from “opt-in.”
- The extractor guide says APK DEX analysis aggregates all DEX files; current analyzer selects ZIP entries whose basename matches standard `classes*.dex`. Nonstandard DEX-like paths are forensic indicators, not analyzed by that default path. It also correctly says parser errors must be inspected and native hashes do not identify versions.
- The reference DB handbook says feature writes are transactional; static inspection of the full implementation already established that the failure path can return normally after old feature deletion, allowing commit. Treat “transactionally” as a claimed design intent that is not guaranteed on all error paths. The source-validation handbook’s denominator distinction aligns with the code and PFE evaluation: emitted-row confirmation and full source-denominator coverage are distinct quantities.
- The SBOM/report guide says report-only AI evidence leaves component/selection authority unchanged; current source supports that. Optional version-band report evidence does add a metadata marker/summary to CycloneDX, so keep “component/version semantics unchanged” distinct from “SBOM byte/metadata output unchanged.” The AI/R8 guide gives rounded retained results but is not the raw experiment source; direct leakage/source-category limitations and absent metric JSON remain controlling context.
- All six handbook pages are now marked `full` as content read. The broader docs, all report code/tests, experiment artifacts and remaining project paths are still being reviewed; no tests or experiments were run.

## Obfuscation diagnostic implementation and direct test coverage

- Read all of `src/apk_sbom/obfuscation.py`. It emits separate report-only signals rather than a unified trained detector: short-name density (info at mean ratio >= .25, warning >= .45), package flattening/repackaging cues (default-package ratio >= .20, or shallow-package ratio >= .85 with mean depth <= 2, or >= .90 concentration in a root of at most two characters), class/method reference loss (warning if any decision loses >= .70 of reference classes or methods), low structural average (< .25), low-confidence emitted component share (warning at >= .50), nonstandard-Dex/protector hints, weak resource-shrinking symptoms, and method-collapse/class-merging indicators. These thresholds are hand-coded heuristics; the feature values depend on parser output and the local reference candidate, and ordinary package naming/shrinking can trigger them.
- `_inlining_rows` marks method-collapse when class coverage >= .50 and method coverage is at least .35 lower (with a .20 floor); class-merging when class coverage <= .35 but opcode or dependency score >= .55. The returned `large_caller_method_concentration` is explicitly `None`; it is not measured. No one signal establishes that R8 or another obfuscator was used.
- No dedicated `test_obfuscation.py` exists. `test_apk_extractor.py` checks the CLI returns report-only diagnostic keys, while selected `test_report.py` checks that reports surface the fields and preserve selected component versions. Those tests do not validate the heuristic thresholds against labeled obfuscated/clean APKs. Source is marked full; report and report-test review remain partial. No tests were run.

## Report rendering and presentation audit (partial)

- Followed `generate_final_report` through component selection, report-only evidence loading, matches JSON, CycloneDX writing, optional OSV/source validation, and JSON/Markdown/HTML serialization. The report function does not run model training or regenerate the experimental JSON files; those are optional input attachments. Diagnostic DEX analysis is wrapped so its exceptions become missing diagnostics, whereas the optional OSV query path can fail the report call. Output directory creation and successive writes mean a failure can leave a partial set of artifacts.
- Read the complete Markdown and HTML report builders and major table helpers. JSON carries APK, matcher summary, uncertainty, heuristic obfuscation risk, diagnostics, components, OSV, paths and optionally attached experiment evidence. Markdown presents forensic summary, diagnostics, uncertainty, experiment annotations, components, version alternatives, OSV findings and limitations. HTML presents corresponding dashboard sections and escapes dynamic HTML text via `html.escape(..., quote=True)`; static styles/structure are embedded.
- Markdown table interpolation does not escape all dynamic values for pipes/newlines/backticks. This can affect display/structure if APK-derived or external report text contains those characters; distinguish output-format robustness from component-selection correctness. HTML escaping coverage is materially stronger. This was static source review, not a security test.
- Read the full `test_report.py` contents: 17 tests use synthetic domain objects and temporary JSON fixtures. They assert report sections, serialization, escaping of a `<` in APK path, uncertainty/risk presentation, optional evidence attachment, and that report-only evidence leaves selected component versions unchanged. They do not validate Markdown adversarial delimiters, historical report outputs, or real APK end-to-end results. Test bodies were read but not executed.
- `report.py` and `tests/test_report.py` are now marked `full` as content read; report behavior was not executed. Evidence-producer scripts and experiment artifacts are separate sources and remain under review. Overall repository review remains active.
### Specialized report renderer follow-up

- Read both Markdown and HTML renderers for the R8 Phase 5 and version-band evidence. Phase 5 presents dataset counts and matching triggered rows; version-band evidence presents AppCompat/Core old-version-steal and Lifecycle public-vs-Android family downgrade annotations. Renderer text explicitly labels these report-only and states selection/vulnerability authority is unchanged. Those source claims do not establish the quality or correctness of the underlying experiment; the attached JSON remains the evidence source.
- Renderers provide a dataset-context explanation when no triggered row matches the current APK, so presence of an experiment section is not itself per-APK support. Some Markdown dynamic table cells are escaped through `_markdown_cell`, while other strings are interpolated directly; table rendering can be malformed by delimiter/newline content. HTML values in the inspected builders pass through `_html`.
- Read the test fixtures/helpers at the start of `tests/test_report.py`; they use hand-built APK/matcher records and canned experiment JSON. No test was run. Remaining report review includes the full specialized minified-confidence and AI/hybrid renderers and cross-checking their inputs with their experiment producers.
### Report-only AI/minification rendering and evidence-producer checks

- Read the remaining Markdown/HTML renderers for minified-confidence policy, hybrid router/structural-gate/Phase 6A/6B assistance, and AI R8 suggestions. They are presentation layers over supplied JSON and repeatedly declare themselves report-only; hybrid says the weighted matcher remains SBOM authority, and DL production wiring is shown as disabled/status metadata. The UI summarizes dataset counts alongside any rows matching the report, so these quantities must not be conflated.
- Cross-read `scripts/build_r8_minified_confidence_report_evidence.py`: it aggregates the optional policy section from four pre-generated report JSONs; for each suggestion/blocked row it compares the matching detected-component version to the policy baseline, treating any inequality (including no component found) as a default-selection change. It labels the aggregate clean only when the selection guard holds, every report has policy evidence, rows are report-only, and at least one suggestion exists. It summarizes reporting evidence, not policy accuracy.
- Cross-read `scripts/build_hybrid_ai_production_report_evidence.py`: it aggregates prebuilt router, ML, DL and structural-gate JSON. Its “representative report context” is synthesized from the first P1 router row (or first row), constructing a case-id `.apk` string and a one-component fixture, then asking the report loader what matches. That is an integration/payload-shape demonstration, not a real-APK end-to-end accuracy evaluation. The script reports DL metric fields while preserving disabled production wiring.
- Confirmed live `data/results/` currently contains only `.gitkeep`; generated JSON/SQLite/APK outputs are absent from this checkout. Many retained `docs/evaluation/*.md` summaries exist, but are secondary textual records. Historical numeric claims remain documentary until the underlying inputs and generated artifacts are available.
- Full source read of `report.py` and all 17 report-test functions is complete; tests were not executed. The two evidence-builder scripts were sampled for this pass and remain inventoried until completely read. Source-to-producer traces, historical inputs and experiment artifacts remain under review. No test, report generation, or experiment was run.
- Current counts following completion of the report source/test reading: 53 full, 46 partial, 1,918 inventoried (includes 303 directory entries). 
eport.py and 	ests/test_report.py are marked full for content reading only.

## Thesis source/PDF reconciliation (partial review)

- Read the thesis directory README, both editable `main.tex` files, both metadata and title-page files, and the master introduction/background chapters. The Master thesis text in the source/older PDF explicitly states it is a literature-synthesis/framework proposal and does not implement a second detector; however, the July 6 PDF omits the chapter that actually specifies/evaluates the framework. Its framework distinguishes claim identity, version, vulnerability authority, provenance, transformation exposure, evidence independence, reference coverage, validation class, conflict and abstention.
- Compared the current source with the named PDFs. The PDFs named `Master_Fendi_Mohamed_evidence_review_2026-06-21.pdf` and `PFE_Fendi_Mohamed_FINAL_SUBMISSION_2026-06-21.pdf` visibly show placeholder date/president/examiner fields and internal creation dates of June 22. Later July 6 PDFs under `output/pdf/` have completed cover metadata. Same-byte duplicate pairs are Master evidence-review/FINAL_SUBMISSION and PFE FINAL_SUBMISSION/page-de-garde-template; the July output pairs `master-thesis-jury-updated`/`MASTER-thesis-updated` and `pfe-thesis-jury-updated`/`PFE-thesis-updated` are also identical copies, not independent builds.
- Material thesis-version issue: current `thesis/master/main.tex` (also `master/main.tex` in `thesis/master.zip`) inputs chapters 1, 2, 3, and 5, omitting the present chapter 4 framework source and Appendix A. The later July 6 48-page Master PDF has the completed cover but its outline confirms it likewise contains only the introduction, background, state of the art, conclusion, and bibliography: it omits the proposed framework chapter and review-protocol appendix even though its abstract still describes the framework as a contribution. An older `master-overleaf-chapter5-conclusion-2026-06-21.zip` and June 22 74-page PDF do include both. README-referenced `thesis/master/main.pdf` and `thesis/pfe/main.pdf` are absent; later PDF copies exist under `output/pdf/`.
- `thesis/pfe/main.tex` includes chapters 1–7 and Appendix A. Its July 6, 124-page output PDF carries the metadata values from current editable source and includes the expected AI/R8 and reproducibility chapters. The older June 22, 138-page PDF is a different checkpoint with placeholders. PFE checkpoint ZIPs contain differently sized chapter-6 snapshots; full checkpoint-by-checkpoint comparison remains outstanding.
- Extracted text from the two named PDFs (74-page Master, 138-page PFE; selectable text on all pages) and visually inspected their cover pages. PDF content review beyond cover/abstract/contents and targeted chapter-4 checks is partial; chapter/source reconciliation continues. No compilation, test, or experiment was run.
- Thesis pass update: Master/PFE main, metadata and title-page files plus README and Master chapters 1–2 read. Two PDFs and four ZIP checkpoints are partial. Current register: 62 full, 51 partial, 1,904 inventoried.

### Master state-of-the-art chapter (initial partial read)

- Began `ch03_state_of_the_art_taxonomy.tex`. It says its corpus uses 15 locally full-text-verified Tier A studies, with Tier B as supplementary search coverage; it avoids a cross-paper leaderboard because tasks, data, obfuscation settings and ground truth differ. Its taxonomy groups work into namespace/metadata heuristics, profile/signature matching, graph segmentation, coarse-to-fine methods, version-discriminating semantics, learned representations, and empirical assessment/benchmarking. The reviewed work’s outputs generally are not provenance-rich CycloneDX/SPDX SBOMs.
- The chapter’s opening paragraph currently has an apparent source defect: `Fields not reported by a Tier A publication are treated asSearches combined...` joins an unfinished phrase to the search-method paragraph. It may be a source/compiled-text merge error; verify against PDF and surrounding sources before treating as an editorial artifact. The chapter remains partial; only its opening technique taxonomy and start of evidence taxonomy have been read.
- Source/PDF findings above are directly observed. Master title-page source metadata includes a date and jury names while its sampled PDF cover visibly has placeholders. Current Master `main.tex` omits framework chapter/Appendix A that appear in the PDF. The PFE source includes all chapters and appendix, but its cover metadata also conflicts with the sampled PDF. `main.pdf` files referenced in README are absent. This is a reproducibility/provenance issue for the thesis artifacts, not evidence that the implementation or cited evaluation data are wrong.
- Master state-of-the-art chapter started; opening and first taxonomy read. Current register: 62 full, 52 partial, 1,903 inventoried.

### Master state-of-the-art and review-protocol completion

- Completed `ch03_state_of_the_art_taxonomy.tex` and Appendix A. The review protocol is explicitly version 1.0 frozen on 21 June 2026 after iterative seed-corpus assembly; it disclaims retrospective raw database query/result/dedup counts and does not claim an exhaustive selection flow. Its four concept blocks cover Android/APK/DEX, component/SBOM, recovery tasks, and transformation/version/vulnerability terms. It defines inclusion/exclusion, Tier A full-text verification, Tier B supplementary records, Tier C contextual authorities, 12 extraction dimensions, and eight quality questions scored 0/0.5/1. It explicitly keeps incompatible metrics, task levels, and original vs independent evaluations separate.
- The seed table has 20 units: 15 Tier A studies (S01–S13 plus S17–S18) and five Tier B items (LibRadar, Libra, LibMD, LibScope, ObfDetector). UniBOM is Tier A but adjacent evidence only, not Android exact-version authority. TPL-Benchmark and UniBOM are dated promotions on 21 June. Quality totals range 5.5–8.0/8; these are reporting/reproducibility quality, not scientific merit.
- The SOTA synthesis spans seven technique families and evidence-source/transformation/evaluation taxonomies. It warns that reference profiles bound recognition, inlining/shrinking threaten adjacent-version distinctions, and most studied systems do not emit provenance-rich standard SBOM claims. It states the gap narrowly for the reviewed corpus: no verified reviewed study unifies evidence provenance, coverage, transformation risk, ambiguity, validation class and permitted vulnerability interpretation. TPL-Benchmark’s 60.15% library F1 and LibHunter’s 76.48% version recall are tied to the benchmark’s compatible slice, not a universal ceiling.
- Correction: the apparent SOTA opening splice was caused by truncated concatenated tool output. Direct inspection of the source and July 6 PDF shows a complete sentence: unreported Tier A fields are recorded as not reported rather than inferred. Appendix A uses `NR` as the extraction-table code.
- Completed the master state-of-the-art chapter and review-protocol appendix. Current register: 64 full, 51 partial, 1,902 inventoried.

- Latest PDF review-count correction: 64 full, 55 partial, 1,898 inventoried entries; four July output PDF copies have been added as partial reviews.

## Historical literature notes and current protocol cross-check

- Finished reading the older May 2026 `papers/state_of_the_art.md`, `papers/data/impact_on_project.md`, and `papers/data/papers_overview.json`; read the first 131 lines of `papers_6-10_analysis.json` (partial). These are valuable records of research direction, but several statements are stronger than the later frozen thesis protocol and implementation evidence warrant.
- The older notes call LibMD the project's most relevant paper and describe its multi-scale CDG, Bayesian scoring, LDG and explicit SBOM pipeline as an MVP foundation, while also admitting exact metrics/full-text evidence are unverified. They recommend TPL-Benchmark as a target and sometimes call 60.15% a “realistic ceiling.” Current thesis protocol places LibMD in Tier B (no locally verified full text) and does not use it for precise claims. Current runtime matcher is a normalized heuristic with explicit rules; the review to date found no calibrated Bayesian version posterior, implemented multi-scale graph engine, or LibMD-derived transitive dependency graph. Treat these early statements as proposal/history, not as description of delivered code or evidence.
- Older notes also state broad unverified claims about ObfDetector (<10% version F1), LibScope, tool resilience matrices, advanced obfuscation, transitive-dependency prevalence, and precise adoption of techniques. Later thesis text limits such claims to verified Tier A or explicitly Tier B context, and avoids a pooled leaderboard. Each quantitative statement must be checked against its local primary PDF and task/denominator before paper use.
- The old `impact_on_project.md` contains replacement-character glyphs (for example the title separator and “Adapt” separator), malformed fragments such as `=10 app threshold`, and `?` where arrows should be. Record this as encoding/editorial damage; do not silently normalize its intended meaning without source comparison.
- Local primary research PDFs are present under `ressources/papers/` for the main Tier A studies (including LibScout, LibD, ORLIS, LibID, LibPecker, LibScan/LibHunter, ATVHUNTER, LibAttention, SAD, Ramirez, both assessments, TPL-Benchmark and UniBOM). Full-text-by-full-text study verification remains necessary; local presence alone does not prove every claim in notes was checked correctly.
- `papers_overview.json`, the older synthesis markdown, and the per-paper impact notes are now content-read and marked full as historical records, not independently validated sources. `papers_6-10_analysis.json` remains partial. No experiments or tests were run.
- Historical literature notes and overview extraction read; current protocol cross-check added. Current register: 67 full, 53 partial, 1,897 inventoried.

### Legacy per-paper extraction and comparison matrix

- Completed the 206-line `papers_6-10_analysis.json` and `SBOM_Tools_Synthesis_Table.md`. The structured extraction includes ATVHUNTER and the systematic assessment, Ramirez thesis, SAD, LibMD, LibScope, Libra, LibAttention, LibScan/LibHunter, LibPecker, TPL-Benchmark, ObfDetector, and UniBOM. These are older project synthesis records; several rows explicitly say evidence/metrics are unverified while elsewhere recommending those methods as the MVP blueprint.
- This is an important chronology distinction: “planned/adapted from” LibMD multi-scale graphs, Bayesian version scoring, LDG, NVD/cve-mcp, or a TPL-Benchmark run describe early design proposals, not implementation evidence. Current code and later thesis sources control the description of what was built. The Master review protocol's Tier-B rule supersedes the old table's confident “only explicit SBOM tool/most relevant” framing for precise academic claims.
- The old comparisons state that tools have non-comparable datasets and protocols, but also present pooled performance rankings, “best/current SOTA,” a universal “realistic ceiling,” and obfuscation resilience matrices. This is internally inconsistent and the later thesis correctly narrows those claims. The local primary papers should adjudicate each surviving comparison; do not copy the tables directly into the paper.
- All content in these two files was read; neither their factual claims nor the referenced external papers were fully validated in this pass. Marked both full as historical project records, not validated research evidence. No tests or experiments were run.

### Primary paper audit: TPL-Benchmark (full-text read)

- Read all 20 pages of `ressources/papers/Revisiting Third-Party Library Detection - TPL-Benchmark.pdf`, including appendices A–H. It is a benchmark/data-construction and comparative-study paper, not evidence about the performance of this project’s implementation.
- TPL-Benchmark reports 6,055 APK/source pairs, 5,756 unique library coordinates, 15,274 versions, and 62,218 app–TPL mappings. Its detector comparison selects 946 apps, largely those with more than 20 TPLs, excludes 841 ground-truth JARs with little or no code features, and evaluates 28,210 remaining mappings. Thus those comparison metrics do not describe the whole 6,055-app collection.
- The 60.15% library-level F1 is LibPecker under the *candidate-set* comparison: ground-truth libraries, 100 randomly selected other versions for those libraries, and 100 additional randomly selected libraries. The full-database methods are a separate protocol. It is not a universal accuracy ceiling. LibPecker’s version-level F1 is 49.28%; LibHunter has the highest version-level recall at 76.48%, with 39.69% F1.
- The authors’ 200-app construction reliability sample reports Pearson correlation 0.99 on dependency *counts*, MAE 0.75 dependencies, and exact set match 0.50. The first two do not imply exact identity/version labels; the exact match rate is a material caveat. The method also reports manual handling for mixed DSL, custom scripts, multiple APK targets, and ambiguous versions.
- The paper itself says the corpus is primarily open-source, APK/source alignment and dependency resolution can be imperfect, and its labels are a practical approximation. Gradle runtime resolution is the comparison oracle for the 200-app check; it does not by itself prove every dependency is present in the packaged APK. Keep this source’s external findings and limitations distinct from the project’s own experiments.
- Apparent count distinction to retain: the abstract says 835,250 secrets across 22 types, while the body prose calls 829,580 the total and the channel table assigns 829,580 to the F-Droid row; the other channel counts sum to 5,670, giving 835,250 overall. If this downstream result is ever discussed, cite the table and describe the inconsistency, or omit it.
- Register update: the full-text review is complete; the study was not rerun, the dataset was not independently audited, and no detector baseline was executed.

### Project experiment and failure-decision audit

- Read the complete `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`, `docs/evaluation/CONTROLLED_EVALUATION.md`, `docs/evaluation/MVP_RESULTS_SUMMARY.md`, `docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md`, and `docs/evaluation/K9_BLOCKER_DIAGNOSTICS.md`.
- The controlled evaluation documents 30 fixture APKs/35 expected components as an earlier checkpoint and a later expanded thesis snapshot of 72 fixtures/84 expected versions. Both are retained evidence from successive milestones; the paper uses the later 72/84 aggregate for the final controlled result and describes 30/35 as the earlier checkpoint.
- The controlled lane reports perfect component/version precision and recall on its fixture ground truth, but R8 rename/shrink outcomes are deliberately emitted as low-confidence candidates. Baselines show package overlap can select a wrong Commons Codec version, while exact DEX hash fails under transformations. These are fixture results, not real-APK population accuracy.
- The decision ledger explains accepted and rejected changes: global opcode/API weights, global multi-scale R8 blending, generic recency, broad POM coherence, and global artifact rules were disabled or rejected after control regressions or no measured benefit. The Phase 4 R8 blend reportedly improved four real rows but caused six controlled, 30 source-validated, and eight clean-real regressions; it was rejected globally. The narrower Phase 5 trigger evaluated 286 rows, retained four target improvements, saw zero triggered regressions/conflicts, and remains experiment-only.
- The same ledger records report-only obfuscation/R8 diagnostics, report-only or isolated AI/DL assistance, hash-only native components, hidden-DEX boundary handling, and the K-9 Gradle blocker. K-9 had repeated plugin-resolution/time-out failures; a validation-only plugin-lite source copy later produced a runtime tree and confirmed 5/11 emitted versions, with six mismatches and zero missing coordinates. It is partial evidence, not a clean case.
- The paper should present failed promotions and blocked validations as design evidence: they explain why the default matcher remains deterministic and confidence-aware, and why diagnostic signals do not silently change SBOM or CVE authority.

Current register snapshot after this pass: 76 full, 48 partial, 1,893 inventoried entries (read-state counts from the CSV; no claim of empirical reproduction).

### Primary paper audit: LibScan (full-text read)

- Read all 19 pages of `ressources/papers/Libscan.pdf` (USENIX Security 2023). LibScan uses three stages: Boolean class-feature signatures, set-inclusion method-opcode similarity, and call-chain-opcode similarity, with confidence thresholds, early stopping, and feature caching.
- Its main ground-truth evaluation uses 939 apps and 5,956 TPL existences from the Orlis/ATVHunter-derived `AS1` set; a separate controlled `AS2` set contains 204 app variants built from 51 source apps with D8 and three R8 configurations. Thresholds are tuned on 110 `AS1` and 20 `AS2` apps, with different settings for compiler/obfuscation strata. This is why its F1 values are not directly comparable to our APK lanes.
- On `AS1`, the complete LibScan deployment reports library-level F1 0.9550 and version-level F1 0.9414. On controlled `AS2`, version-level F1 drops from 0.800 for D8 non-obfuscated apps to 0.114 for R8 shrink-plus-optimization. The paper explicitly says method inlining and reflection contribute to the optimized-case degradation.
- LibScan’s efficiency results show the trade-off behind layered evidence: signature filtering excludes most candidate classes early, while opcode and call-chain stages reduce false positives but add cost. It reports mean per-app detection times of 45.99 seconds on its large app set and average memory use of 4.88 GB; these are tool-specific measurements on its hardware and candidate corpus.
- Its large-scale 100,000-app scan detects vulnerable TPL-version occurrences, but the paper presents those as potential findings and reuse observations, not vulnerability precision/recall. The authors also state that app-level DEX encryption, virtualization, reflection, and method inlining are outside or weakly supported boundaries.
- LibScan supports the paper’s discussion of coarse-to-fine evidence, explicit transformation scopes, and separate identity/version metrics. The current project borrows the general lesson but does not implement LibScan’s algorithm; its matcher remains weighted evidence fusion with confidence and ambiguity reporting.

### Primary paper audit: ATVHunter (full-text read)

- Read all 13 pages of `ressources/papers/ATVHUNTER.pdf`. ATVHunter decouples candidate modules using class-dependency relations, uses CFG signatures for coarse retrieval, fuzzy-hashed opcode features for version matching, and maps detected versions to a separate CVE/security-bug database.
- Its ground-truth evaluation uses 356 F-Droid apps, 189 unique TPLs, and 6,819 complete version files after excluding 144 apps whose TPL versions were incomplete in Maven. Thresholds are chosen from three separate groups of 200 apps, and the reported overall version-level result is 90.55% precision, 87.16% recall, and 88.82% F1. The study also evaluates 100 apps with four DashO transformations and reports detection rates, not full precision/recall, for that stress set.
- The paper explicitly reports false positives from reused components, group/artifact migrations, and near-identical releases, and false negatives from dead-code removal, host/TPL namespace overlap, missing GitHub-hosted libraries, dynamic loading, native libraries, and incomplete reference coverage. These are directly relevant to the project’s artifact-family, reference-coverage, and limitation lanes.
- The large-scale vulnerable-TPL analysis covers 104,446 Google Play apps collected in 2019–2020 and reports 9,050 vulnerable-app detections. These are static potential-risk findings based on detected versions; they are not vulnerability precision/recall or exploitability measurements.
- ATVHunter is useful related work for coarse-to-fine version evidence and vulnerability-aware downstream workflow. It does not justify presenting the current project’s lower-confidence candidates or OSV findings as equivalent to ATVHunter’s database-backed results.

### Primary paper audit: UniBOM (full-text read)

- Read all nine pages of `ressources/papers/UniBOM - Unified Software Bill of Materials.pdf`, including its architecture, binary/source workflows, evaluation tables, GUI discussion, and references.
- UniBOM integrates Binwalk, Syft, Grype, and CCScanner in a Node.js workflow for firmware, filesystem, and source-code SBOM analysis. Its evaluation covers 258 Linux wireless-gateway firmware images and five IoT operating-system source trees; it reports vulnerability counts and severity distributions rather than precision/recall or complete component-level ground-truth agreement.
- The paper’s comparative result is therefore workflow evidence: higher detected CVE counts demonstrate broader findings under the chosen scanners and mappings, not higher attribution precision or proof that every listed component is present. Its binary/source and C/C++ scope is adjacent to this Android APK/Maven problem; Android DEX, R8, and adjacent-version discrimination are outside its evaluation.
- The project can cite UniBOM for the motivation to integrate component evidence, standardized SBOM output, vulnerability analysis, history/comparison, and visualization. It should not use UniBOM to support Android exact-version accuracy, a universal SBOM completeness claim, or a claim that more findings means better detection.
- The local `papers/data/unibom.json` records these limitations and rates its evidence quality 5.5/8 for reporting quality, not scientific merit. No UniBOM artifact, dataset, or external scanner was executed during this study.

### Primary paper audit: SAD (full-text read)

- Read all 12 pages of `ressources/papers/Version-level Third-Party Library Detection in Android Applications via Class Structural Similarity.pdf` (EASE 2025). SAD combines class-dependency graphs, candidate class lists, opcode/field matching, call-sequence field-operation summaries, structural-path validation, and literal overlap for adjacent-version tie-breaking.
- The evaluation uses a LibScan-derived database and app sets: 1,231 apps, 562 TPL versions, with unobfuscated/obfuscated sets `D1`/`D2` and 51-app-family optimization variants in `D3`. Ten percent of each dataset is used for threshold tuning. The paper manually corrected the LibScan ground truth and manually built one-to-one class mappings for only 20 selected app–library pairs, so class-level results are a small selected sample rather than a general APK population estimate.
- SAD proposes a stricter version-level† metric: if a tool reports multiple versions, every incorrect extra version is counted as a false positive, even when the correct version is included. On `D2`, SAD reports 84.82% version-level† F1; on `D3` its overall version-level† F1 is 49.31%, with LibHunter highest at 59.54%. This supports the paper’s distinction between identity/library detection and exact-version attribution.
- Thresholds are tuned separately by dataset, and the authors acknowledge that mixed real-world transformation status makes one optimal threshold difficult. Optimization failures are attributed partly to incorrect or missing reference versions and method reduction/removal. Advanced reflection, encrypted DEX, virtualization, and native libraries remain outside or beyond the method’s reliable scope.
- There is a headline inconsistency to preserve: the abstract reports 84.82% version-level F1 on obfuscated apps, while page 2 also states 95.35% in a contribution paragraph; Table 3 identifies 84.82% as the stricter version-level† F1 and 95.35% as ordinary version-level F1. Any citation must name the metric and table rather than repeat an unqualified headline.
- SAD is a primary source for the paper’s discussion of structural evidence, stricter version ambiguity handling, and transformation-specific evaluation. It is not evidence that the current project implements SAD’s CDG/class-summary algorithm; the current matcher remains weighted evidence fusion with reportable ambiguity.

### Primary paper audit: LibHunter (full-text read)

- Read all 13 pages of `ressources/papers/LibHunter.pdf` (ASE 2024). LibHunter studies R8/D8 prevalence and optimization effects, then models CallSiteOptimization and method inlining using enhanced TPL features, partial/cross-inlining method matching, opcode/string evidence, and thresholded library scores.
- Its prevalence sample is 2,347 F-Droid apps after filtering; 41.1% are classified as R8 and 58.8% as D8. Its controlled detection data starts from 200 randomly selected apps and 31 vulnerable TPLs, builds five variants per app, and adds a 650-app single-strategy dataset from 50 apps × 13 modified R8 variants. Thresholds are tuned on 20% of the variant set (40×5 apps; 61×5 app–TPL pairs), leaving 318×5 pairs for evaluation.
- On the held-out controlled variants, LibHunter reports 51.1% version-level F1 for `Opt+Obf+Srk`, 71.4% library-level F1, and 62.4%/69.7% version-level F1 for CallSiteOptimization/Inlining-only strategy variants. These are controlled, vulnerable-TPL datasets with tuned thresholds, not general APK population accuracy.
- The paper’s 10,000 Google Play scan reports warnings, not vulnerability precision or exploitability: 1,855 apps with 8,659 detected versions among 31 vulnerable TPLs, 3,761 warnings, and 15-minute average processing per app. The authors explicitly caution that shrinking may remove vulnerable methods and that a warning is not proof of exploitability.
- LibHunter’s limitations include incomplete modeling of all R8 strategies, bias toward R8 rather than commercial obfuscators, and dependence on reference versions. The paper supports treating inlining/CallSiteOptimization as important stressors and keeping R8 assistance scoped; it does not support claiming that the current project is LibHunter-equivalent or R8-proof.
- The paper’s external result is useful for transformation-specific motivation. The current project’s R8/AI and structural paths remain report-only or experiment-only unless a guarded evaluation promotes them; default matcher/SBOM/CVE authority is unchanged.

### Evaluation dashboard and evidence-matrix consolidation

- Read the current APK-type evaluation and thesis evaluation tables. They preserve the 72 controlled fixtures/84 expected-version snapshot, the clean 47/47 emitted-version confirmation across five real APKs, and the partial 880/1,790 confirmation across 97 real APKs. These are separate evidence lanes; the clean subset must not be presented as the global real-APK score.
- Read the reference-DB coverage-first dashboard. Across 106 source-validated cases there are 12,082 source coordinate/version rows, 1,370 unique coordinates, and 3,391 unique coordinate/version pairs. The shared reference DB covers 18.4% of source rows by coordinate and 10.2% by exact version; 927/1,837 emitted rows are confirmed. The dashboard therefore requires coverage-first reporting before version-selection optimization.
- The current project evidence matrix is now the working bridge from source files to paper claims. It records related-work conditions for TPL-Benchmark, UniBOM, SAD, LibHunter, LibScan, and ATVHunter, and defines claim contracts for controlled recovery, emitted-version confirmation, source-denominator coverage, the source-version-constrained upper bound, and downstream vulnerability workflow.
- Current register verification after the latest literature and dashboard pass: 78 full, 48 partial, and 1,891 inventoried entries. The count is a bookkeeping snapshot; it does not imply that every inventoried artifact has been interpreted.

### Paper drafting readiness artifacts

- Created and reviewed `papers/IMPLEMENTATION_EVALUATION_DRAFT.md`, which
  drafts Section 5 around RQ1–RQ4, implementation scope, protocol lanes,
  metrics, and threats to validity.
- Created and reviewed `papers/PAPER_FIGURE_TABLE_SPEC.md`, which fixes the
  purpose, unit, denominator, evidence source, and interpretation boundary for
  four figures and five tables. It keeps the 50.5% emitted-row rate, the
  12,082-row source denominator, and the 6,772/6,772 constrained result in
  separate visual lanes.
- Created and reviewed `papers/LITERATURE_CITATION_REGISTER.md`, linking the
  State of the Art draft to local primary PDFs and marking DOI/publisher
  metadata that still needs external verification.
- Added these three paper artifacts to the file-review register as full
  reviews. The register currently contains 81 full, 48 partial, and 1,891
  inventoried entries.

### Paper readiness audit

- Created `papers/PAPER_READINESS_AUDIT.md` to map every paper requirement to
  authoritative evidence, readiness status, and remaining action.
- The audit verifies that the supervisor structure, literature foundation,
  implementation description, RQs, evaluation-lane definitions, denominator
  mapping, constrained upper-bound interpretation, vulnerability workflow,
  threats, and visual specifications are ready for bounded working-paper
  drafting.
- It also records the remaining submission gates: raw result/reference/source
  artifacts, frozen run metadata, complete bibliographic verification, and a
  final single-snapshot numerical audit.
- The manuscript scaffold is now registered as a full review; current register
  verification is 83 full, 48 partial, and 1,891 inventoried entries.

### Introduction drafting

- Created `papers/INTRODUCTION_DRAFT.md` with source-grounded context, problem
  statement, bounded related-work motivation, approach overview, contributions,
  scope exclusions, and organization.
- The Introduction preserves the evidence-gated central argument and avoids
  universal accuracy, “first,” calibrated-probability, native-version, and
  vulnerability-precision claims.
- Current register verification after this artifact: 84 full, 48 partial, and
  1,891 inventoried entries.
- The paper plan and writing rules were then re-read in full after the
  consistency sweep and promoted in the register; current verification is 86
  full, 46 partial, and 1,891 inventoried entries.

### Final thesis-package reconciliation

- Read `docs/thesis/FINAL_REPORT_READINESS_PACKAGE.md`,
  `docs/thesis/FINAL_V2_RESULTS_SECTION.md`,
  `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`, and
  `docs/thesis/PFE_FULL_THESIS_EXAMINER_REVIEW_2026-06-20.md` in full.
- The v2 evidence is now contractually recorded as 6,772/6,772 constrained
  confirmations across 106 source-tree cases using a 10,517-component local
  database, with 5,238 source-gap rows and a triage split of 2,281
  matcher-recall candidates and 442 missing-reference candidates.
- The examiner review confirms the exact rejected global-R8 result: four target
  improvements, six controlled regressions, 30 real source-validated
  regressions, and eight clean-real regressions. It also records a completed
  46-key/46-entry thesis bibliography audit.
- Current register verification: 90 full, 42 partial, and 1,891 inventoried
  entries.

### Bibliographic alignment

- Read the relevant primary-paper entries in `thesis/pfe/bib/references.bib`
  and aligned `papers/LITERATURE_CITATION_REGISTER.md` with verified BibTeX
  keys, author lists, venues, years, and DOI/official URLs.
- The working paper now has a verified metadata path for the main related-work
  studies; final work is limited to selecting the venue-specific citation
  subset and style.

### Systematic assessment paper completion

- Read all 24 pages of `ressources/papers/A Systematic Assessment on Android
  Third-party Library Detection Tools.pdf` and promoted it to full review.
- It contributes the six-criteria evaluation taxonomy and a documented
  221-app/59-TPL/2,115-version protocol, with findings on package structure,
  multidex, AAR format, partial imports, TPL dependencies, and obfuscation.
- Added its bounded evidence to the related-work matrix and State of the Art
  draft. Current register verification: 91 full, 41 partial, and 1,891
  inventoried entries.

### Architecture provenance audit

- Read `docs/architecture.md` and `docs/architecture/DECISIONS_LOG.md` in full.
- `docs/architecture.md` is an early proposal centered on a LibScout/BlockFusion
  basic-block module, Earth Mover’s Distance, and cve-mcp. Those elements are
  historical design intent and are not descriptions of the delivered MVP.
- `docs/architecture/DECISIONS_LOG.md` is the current scope authority: the
  implemented MVP uses static metadata/class/opcode/CDG evidence, selected
  Maven reference profiles, confidence scoring, CycloneDX, OSV-first lookup,
  and native hash-only reporting, while excluding packed/dynamic/native
  version recovery and perfect heavy-R8 recovery.
- The Proposed Approach draft follows the current decision log; this
  distinction is now an explicit provenance rule for manuscript integration.
- Current register verification: 93 full, 39 partial, and 1,891 inventoried
  entries.

### Promoted matcher and experiment-policy audit

- Read the composite-family shortlist promotion, version-unique literal/context
  promotion, guarded reference-DB workflow, Phase 5 report evidence, APK-only
  reranker, and candidate-expansion diagnostics in full.
- The delivered default path includes only two narrow promotions: the balanced
  composite shortlist (margin `0.10`, complete version bands) and the guarded
  version-unique literal/context reranker (two-feature and score-margin gates).
- APK-only version-band reranking produced zero safe changes and was rejected;
  Phase 5 produced four report-only suggestions with zero default selection
  changes. App-specific reference promotions remain isolated unless singleton
  control gates pass.
- Updated `PROPOSED_APPROACH_DRAFT.md` and `PAPER_EVIDENCE_MATRIX.md` to match
  these implementation decisions. Current register verification: 99 full, 33
  partial, and 1,891 inventoried entries.

### Current MVP architecture completion

- Read `docs/architecture/MVP_ARCHITECTURE.md` in full and reconciled it with
  the source modules and decision log.
- It is the current high-level architecture authority for extraction, DEX and
  metadata evidence, reference profiles, candidate generation, hybrid
  matching, confidence/uncertainty, CycloneDX, and OSV-first reporting.
- The implementation draft uses the code-level `confirmed`, `candidate`, and
  `uncertain` statuses rather than importing the architecture document’s broad
  shorthand without qualification.
- Current register verification: 100 full, 32 partial, and 1,891 inventoried
  entries.

### Thesis evaluation tables and generator completion

- Read `docs/evaluation/THESIS_EVALUATION_TABLES.md` and
  `scripts/build_thesis_evaluation_tables.py` end to end.
- The generated tables are the thesis-facing aggregation layer over
  `data/results/evaluation/apk-type-evaluation.json`; they keep controlled,
  clean, partial, blocked, and limitation evidence in separate scopes.
- The source-role filter and totals reproduce the manuscript contracts:
  72 controlled fixtures with 84 expected/84 confirmed versions; 5 clean
  real APKs with 47/47; 97 partial real APKs with 880/1790; and 102 combined
  source-validated real APKs with 927/1837.
- The script was inspected but not executed during this audit. It writes the
  Markdown and JSON outputs deterministically from the input evidence file.
- Current register verification: 102 full, 31 partial, and 1,890 inventoried
  entries.
