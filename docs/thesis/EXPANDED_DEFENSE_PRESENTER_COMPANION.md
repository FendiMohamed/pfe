# Expanded Defense Presenter Companion

Use this file with:

`outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/output/apk-sbom-defense-academic-deck.pptx`

The deck contains:

- `31` main defense slides;
- `8` backup slides;
- speaker notes embedded in every slide;
- implementation, evaluation, and experiment evidence linked below.

## Recommended Presentation Routes

### Full technical defense: 20 to 25 minutes

Present slides `1-31`, then use slides `32-39` only during questions.

### Compressed defense: 12 to 15 minutes

Present:

`1, 2, 3, 4, 6, 10, 11, 15, 16, 17, 19, 20, 21, 22, 24, 28, 29, 30, 31`

Mention that slides `7-14` contain the detailed component evolution and are
available when the jury asks how a subsystem was designed.

## The Story In One Sentence

The project reconstructs third-party library evidence from compiled Android
APKs, compares that evidence with reproducible Maven reference profiles,
separates library identity from exact-version confidence, emits CycloneDX, maps
OSV findings, and keeps ambiguity and hard R8 cases visible instead of forcing
unsupported answers.

## Numbers To Memorize

| Claim | Number |
|---|---:|
| Controlled expected Maven versions | `84/84` |
| Source-validated real APKs | `102` |
| Normal emitted Maven versions confirmed | `927/1837` |
| Normal emitted-version confirmation rate | `50.5%` |
| Clean real APK emitted versions confirmed | `47/47` |
| Partial real APK emitted versions confirmed | `880/1790` |
| Source-known v2 cases | `106` |
| V2 exact emitted rows | `6772/6772` |
| V2 source-gap rows | `5238` |
| Explained/boundary source-gap rows | `2515` |
| Matcher-recall candidates | `2281` |
| Missing-reference candidates | `442` |
| RandomForest test macro-F1 | `0.708` |
| MVP-safe Transformer test macro-F1 | `0.882` |
| Raw-opcode Transformer / baseline macro-F1 | `0.110 / 0.128` |

Primary evidence:

- `docs/evaluation/THESIS_EVALUATION_TABLES.md`
- `docs/evaluation/DEMO_FINAL_V2_PACKAGE.md`
- `docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md`
- `docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md`

## Wording Guardrails

Say:

> The normal real-APK metric is emitted Maven version confirmation, not full dependency recall.

Say:

> The v2 result is a source-version constrained upper-bound lane, not unconstrained APK-only production accuracy.

Say:

> AI is report-only assistance. It cannot change selected versions, SBOM components, or CVE labels.

Do not say:

- “The tool has 100% real-world accuracy.”
- “Every missing source dependency is a matcher failure.”
- “The AI chooses the correct version.”
- “The tool is obfuscation-proof.”

## Component Evolution And Why Each Choice Was Made

### 1. APK extraction

Evolution:

1. ZIP and standard `classes*.dex` inventory.
2. Manifest decoding and application metadata.
3. Native `.so` inventory and SHA-256 hashes.
4. Nonstandard DEX, hidden-code, and protector-like forensic indicators.

Why this design:

- A matcher cannot make credible claims if it does not first know which code is
  actually available.
- Native and hidden code require explicit boundaries rather than false Maven
  identities.
- Static extraction is reproducible and suitable for the MVP; dynamic analysis
  would still miss dormant code and greatly increase execution cost.

Implementation:

- `src/apk_sbom/apk_extractor.py`
- `inspect_apk()`
- `parse_manifest_metadata()`
- `build_forensic_summary()`
- `apk_indicators()`

Evidence:

- `docs/evaluation/HIDDEN_DEX_DIAGNOSTICS.md`
- `docs/evaluation/NATIVE_BOUNDARY_DIAGNOSTICS.md`

### 2. DEX analysis

Evolution:

1. Package names and opcode counts.
2. Class descriptors and method signatures.
3. Class dependency edges, graph shape, literals, and API references.
4. Opcode tri-grams and multi-scale basic-block, call-chain, neighbor,
   field-operation, and literal-context features.

Why this design:

- Package names are useful but fragile under R8.
- Classes and methods give identity evidence.
- Opcodes and dependency structure survive some renaming.
- Literals and version-unique context can distinguish nearby versions.
- New multi-scale signals are extracted broadly but remain inert until guarded
  experiments prove they are safe.

Implementation:

- `src/apk_sbom/dex_analyzer.py`
- `analyze_dex_bytes()`
- `analyze_apk_dex()`

Evidence:

- `docs/evaluation/R8_MULTISCALE_FEATURE_DIAGNOSTICS.md`
- `docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md`
- `docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md`

### 3. Maven reference database

Evolution:

1. Small manually configured library/version set.
2. Automated Maven JAR/AAR and POM download.
3. AAR `classes.jar` extraction and D8 normalization to DEX.
4. Shared APK/reference feature extraction into SQLite.
5. Guarded source-observed and v2 reference-growth lanes.

Why this design:

- APK and reference artifacts must be compared in the same representation.
- Maven coordinates, versions, PURLs, and POM metadata are reproducible.
- Blind reference growth is unsafe: adding a correct adjacent version can steal
  a match from another APK.
- Reference additions are therefore evaluated against current controls before
  promotion.

Implementation:

- `src/apk_sbom/maven_downloader.py`
- `src/apk_sbom/reference_converter.py`
- `src/apk_sbom/reference_features.py`
- `src/apk_sbom/reference_config.py`

Important functions:

- `artifacts_from_libraries()`
- `convert_reference_artifacts()`
- `initialize_feature_db()`
- `extract_reference_features_to_db()`

Evidence:

- `docs/evaluation/GUARDED_REFERENCE_DB_PROMOTION_WORKFLOW.md`
- `docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md`
- `docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_GROWTH_RESULT.md`

### 4. Matcher

Evolution:

1. Package-driven reference comparison.
2. Weighted package, class, method, opcode, dependency, and literal fusion.
3. Version-unique class/method/literal evidence.
4. Separate identity and version decisions.
5. Explicit ambiguity and alternative versions.
6. Guarded version-unique literal/context reranking.
7. Composite coordinate-family shortlisting.
8. Scoped artifact-family and app-era coherence rules.
9. Report-only hybrid router and R8 structural experiments.

Why this design:

- No individual signal is reliable across clear, shrunk, renamed, and
  dependency-rich APKs.
- Exact version recovery is harder than library identity.
- A target improvement is rejected if it regresses controlled or real APK
  controls.
- Narrow evidence-backed rules are safer than global recency or broad scoring
  changes.

Main implementation:

- `src/apk_sbom/matcher.py`
- `match_apk_to_reference_db()`
- `score_reference_component()`
- `build_version_decisions()`
- `classify_identity_candidate()`
- `classify_version_candidate()`
- `_choose_version_candidate()`
- `reportable_version_decisions()`
- `detected_libraries_from_match_summary()`

Related experiment logic:

- `src/apk_sbom/hybrid_matcher_router.py`
- `src/apk_sbom/r8_structural_recall_experiment.py`
- `src/apk_sbom/r8_apk_structural_promotion_gate.py`
- `src/apk_sbom/version_band_apk_reranker.py`

Evidence:

- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`
- `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_VERIFICATION.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DEFAULT_PROMOTION_VERIFICATION.md`
- `docs/evaluation/HYBRID_MATCHER_ROUTER_V1.md`

### 5. Confidence and ambiguity

Evolution:

1. One overall match score.
2. Identity confidence separated from version confidence.
3. Score-gap thresholds and exact/likely/candidate/uncertain states.
4. Single-reference coordinates capped unless evidence is nearly complete.
5. Near-tie and feature-equivalent versions exported as alternatives.

Why this design:

- A library can clearly be present while its exact version remains ambiguous.
- Treating those claims as equal would create false exact SBOM and CVE output.
- Explicit ambiguity is more useful and scientifically honest than silently
  forcing one version.

Implementation:

- `src/apk_sbom/matcher.py`
- `src/apk_sbom/models.py`
- `identity_confidence_score()`
- `classify_identity_candidate()`
- `classify_version_candidate()`
- `_cap_single_reference_version_decision()`

Evidence:

- `docs/evaluation/VERSION_UNCERTAINTY_REPORTING.md`
- `docs/evaluation/VERSION_BAND_TIE_EVIDENCE.md`

### 6. CycloneDX SBOM

Evolution:

1. Internal detection JSON.
2. CycloneDX `1.5` component output.
3. Maven PURLs and evidence properties.
4. Separate identity/version confidence and ambiguous versions.
5. Native `.so` files included as hash-only file components.

Why this design:

- CycloneDX is interoperable with vulnerability and SBOM tooling.
- PURLs preserve Maven identity.
- Confidence and evidence properties keep the reverse-engineering uncertainty
  visible.
- Native files are useful evidence, but the MVP must not invent Maven
  coordinates for them.

Implementation:

- `src/apk_sbom/sbom.py`
- `build_cyclonedx_bom()`
- `_component_to_cyclonedx()`
- `_native_library_to_cyclonedx()`

### 7. Vulnerability mapping

Evolution:

1. Considered NVD/CPE-first mapping.
2. Selected OSV Maven package/version queries.
3. Added batch queries, aliases, severity enrichment, and deduplication.
4. Added confidence-aware confirmed/potential classification.
5. Added source-validation relabeling for real APK evidence.

Why this design:

- OSV maps directly to Maven package/version identities.
- A vulnerability claim must be no stronger than the component identity and
  version evidence.
- Weak or mismatched versions remain potential instead of becoming false
  confirmed CVEs.

Implementation:

- `src/apk_sbom/vulnerability.py`
- `query_osv_for_libraries()`
- `classify_vulnerability_finding()`
- `apply_source_validation_to_osv_summary()`

Evidence:

- `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md`
- `data/results/demo-osv-vulnerable-jackson-databind/report.html`

### 8. Reporting

Evolution:

1. Raw JSON artifacts.
2. Unified JSON, Markdown, and HTML report generation.
3. Extraction/obfuscation risk and source-validation evidence.
4. Experiment-only sections.
5. Report-only hybrid and AI assistance with unchanged production authority.

Why this design:

- Reporting is the transparency boundary between production decisions and
  research suggestions.
- Every output format is generated from the same evidence model.
- Experimental and AI suggestions can be useful without changing the SBOM.

Implementation:

- `src/apk_sbom/report.py`
- `generate_final_report()`
- `build_json_report()`
- `build_markdown_report()`
- `build_html_report()`

Evidence:

- `docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md`
- `docs/evaluation/FINAL_HYBRID_AI_DEMO_SMOKE.md`

### 9. AI/R8 assistance

Evolution:

1. Report-only R8 diagnostics.
2. RandomForest over structured matcher/evaluation evidence.
3. Structured-token Transformer.
4. MVP-safe Transformer with source shortcuts removed.
5. Raw-opcode Transformer with case-heldout evaluation.
6. Explicit integration gate blocking matcher/SBOM/CVE authority.

Why this design:

- The current evidence is structured and tabular, making RandomForest
  explainable and practical.
- The Transformer demonstrates sequence representation learning.
- The raw-opcode negative result is retained because it defines the need for a
  larger independent corpus.
- AI is useful for triage but is not yet safe for exact version authority.

Implementation:

- `src/apk_sbom/ai_r8_assistant.py`
- `src/apk_sbom/ai_r8_mvp_integration_gate.py`
- `scripts/build_ai_r8_token_corpus.py`
- `scripts/train_ai_r8_tiny_transformer.py`
- `scripts/train_ai_r8_raw_opcode_transformer.py`

Evidence:

- `docs/evaluation/AI_R8_FINAL_EVALUATION.md`
- `docs/evaluation/AI_R8_DL_PROTOTYPE_MVP_SAFE.md`
- `docs/evaluation/AI_R8_RAW_OPCODE_TRANSFORMER.md`
- `docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md`

## How The Matcher Actually Works

Use this section when the jury asks for algorithmic detail.

### Step 1: analyze the APK

`match_apk_to_reference_db()` calls:

`analyze_apk_dex(apk_path, include_members=True)`

This produces package, class, method, opcode, dependency, literal, API, and
multi-scale feature collections.

### Step 2: load and shortlist references

The matcher loads reference components from SQLite.

The default composite family shortlist:

- groups references by Maven coordinate;
- scores coordinate families with class, method, dependency, and literal
  evidence;
- retains families inside a guarded margin;
- keeps every version belonging to a retained coordinate;
- rescues independently supported families.

This reduces candidate pressure without deleting tracked source families.

### Step 3: score every retained coordinate-version candidate

Default normalized fusion weights:

| Signal | Weight |
|---|---:|
| Package overlap | `0.15` |
| Class overlap | `0.45` |
| Method overlap | `0.25` |
| Opcode cosine similarity | `0.15` |
| Class dependency evidence | `0.10` |
| String literal overlap | `0.08` |
| Version-unique evidence | `0.12` |
| API-reference score | `0.00` |
| Opcode tri-gram score | `0.00` |

The score is the weighted sum divided by the total enabled weight.

Dependency evidence itself is:

`0.65 * dependency-edge coverage + 0.35 * dependency-shape similarity`

Version-unique evidence is built against sibling versions of the same
coordinate:

`0.35 * unique classes + 0.45 * unique methods + 0.20 * unique literals`

API-reference and opcode tri-gram extraction exists, but their global weights
remain zero because guarded experiments did not justify promotion.

### Step 4: form one version decision per coordinate

Candidates are grouped by Maven coordinate.

The matcher may choose a non-raw leader only when guarded evidence supports it:

1. version-distinctive class/method/literal evidence;
2. version-unique literal/context evidence;
3. independently supported POM dependency coherence;
4. scoped app-era coherence.

It does not use a generic “newest version wins” rule.

### Step 5: classify version confidence

Important states:

- `high / exact`: nearly complete evidence, or a strong score with a safe gap;
- `medium / likely`: strong score and meaningful gap;
- `low / candidate`: useful but insufficient evidence;
- `uncertain`: no safe exact claim.

A coordinate with only one reference version is capped unless the match is
essentially complete. This prevents “only candidate in the DB” from looking
like proof.

### Step 6: classify identity separately

Identity confidence uses available package, class, method, opcode, dependency,
literal, and optional API evidence.

This answers:

> Is the library present?

Version confidence answers:

> Is this exact version supported?

These are intentionally separate decisions.

### Step 7: resolve artifact-family overlap

Some Maven artifacts contain overlapping bytecode:

- `okio` / `okio-jvm`;
- `okhttp` / `okhttp-android`;
- Lifecycle public / Android target artifacts.

Scoped family rules select a representative and preserve suppression evidence.
They are not broad coordinate rewriting rules.

### Step 8: export evidence

Every reported component includes:

- package/class/method/opcode/dependency/literal evidence;
- identity decision;
- version decision;
- alternatives and ambiguity;
- reranking reason when a guarded rule changes the raw leader;
- artifact-family suppression details.

## Rejected Or Guarded Matcher Choices

| Choice | Decision | Why |
|---|---|---|
| Package-only matching | Rejected | Fragile under renaming and repackaging. |
| Hash-only matching | Rejected | Breaks after recompilation and optimization. |
| Generic newest-version tie break | Rejected globally | Recency is not APK evidence and regressed controls. |
| Global opcode tri-gram weight | Disabled | Regressed OpenTracks and Conversations without confirmed gain. |
| Global API-reference weight | Disabled | Produced no source-validation improvement. |
| Global multi-scale R8 blend | Rejected | Improved targets but caused controlled and real regressions. |
| Phase 5 scoped R8 trigger | Experiment/report-only | Four improvements survived scoped gates, but evidence is still narrow. |
| APK-only version-band reranker | Not promoted | Produced zero safe fixes. |
| Deep candidate expansion alone | Not promoted | More candidates still selected an incorrect old Activity version. |
| R8 structural automatic emission | Not promoted | Same-coordinate wrong-version and false-positive controls remain. |

Full record:

`docs/thesis/EXPERIMENT_DECISION_LEDGER.md`

## Slide-By-Slide Speaking Guide

### Slide 1 — Title and headline metrics

Say that the project starts from a compiled APK, not a Gradle project. Introduce
the three metrics only after separating the normal and source-known lanes.

Open if questioned:

- `docs/evaluation/THESIS_EVALUATION_TABLES.md`
- `docs/evaluation/DEMO_FINAL_V2_PACKAGE.md`

### Slide 2 — Compilation removes dependency metadata

Contrast Gradle dependencies with mixed APK evidence. Explain that Maven
coordinates and exact versions normally do not survive compilation.

Open:

- `docs/architecture/MVP_ARCHITECTURE.md`
- `src/apk_sbom/apk_extractor.py`

### Slide 3 — Literature evolution

Present the progression:

`signatures -> structural evidence -> learned representations`

Then state the remaining gap: exact version recovery under optimization plus
standard SBOM/CVE output.

Open:

- `papers/state_of_the_art.md`
- `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`

### Slide 4 — Objective and output policy

Explain that the output is a useful security artifact, not forced certainty.
Show identity, version, vulnerability, and limitation outcomes.

Open:

- `docs/architecture/DECISIONS_LOG.md`

### Slide 5 — Why this architecture

Walk through the decision table: hybrid static analysis, Maven reference
profiles, CycloneDX/PURL, OSV-first lookup, and confidence-aware obfuscation
handling. For each decision, state the rejected alternative and why it was not
safe or suitable for this MVP.

Open:

- `docs/architecture/DECISIONS_LOG.md`

### Slide 6 — End-to-end pipeline

This is the complete MVP architecture diagram. Walk through the upper APK lane:

`extract -> fingerprint -> retrieve -> match -> decide -> report`

Then explain the lower Maven reference-profile lane:

`Maven JAR/AAR -> D8 normalization -> equivalent feature extraction -> SQLite DB`

Show where that lane feeds candidate profiles into the matcher. Finish with the
three architectural properties: static/reproducible, equivalent feature space,
and a confidence gate before CVE claims.

Open:

- `src/apk_sbom/report.py`
- `docs/architecture/MVP_ARCHITECTURE.md`

### Slide 7 — APK extractor evolution

Use the APK extraction component section above. Emphasize hidden-code and native
boundaries.

Open:

- `src/apk_sbom/apk_extractor.py`

### Slide 8 — DEX analysis evolution

Explain coarse-to-multi-scale extraction and the “extract first, promote only
after controls” rule.

Open:

- `src/apk_sbom/dex_analyzer.py`
- `docs/evaluation/R8_MULTISCALE_FEATURE_DIAGNOSTICS.md`

### Slide 9 — Reference database evolution

Explain Maven download, D8 normalization, feature extraction, and SQLite.
Mention that reference growth is guarded against regressions.

Open:

- `src/apk_sbom/maven_downloader.py`
- `src/apk_sbom/reference_converter.py`
- `src/apk_sbom/reference_features.py`

### Slide 10 — Matcher evolution

Explain the weighted multi-signal fusion, candidate shortlisting, guarded
reranking, and rejected unsafe global rules.

Open:

- `src/apk_sbom/matcher.py`
- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`

### Slide 11 — Confidence evolution

Explain why library identity and exact version are separate claims. Mention
alternatives and score-gap evidence.

Open:

- `src/apk_sbom/matcher.py`
- `src/apk_sbom/models.py`

### Slide 12 — SBOM evolution

Explain the move from internal JSON to CycloneDX `1.5`, PURLs, confidence
properties, ambiguity, and hash-only native components.

Open:

- `src/apk_sbom/sbom.py`
- `data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json`

### Slide 13 — Vulnerability evolution

Explain why OSV fits Maven better than NVD/CPE-only lookup and why weak versions
produce potential, not confirmed, findings.

Open:

- `src/apk_sbom/vulnerability.py`
- `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md`

### Slide 14 — Reporting evolution

Explain that reporting preserves provenance and separates default authority
from experiment-only and AI evidence.

Open:

- `src/apk_sbom/report.py`
- `docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md`

### Slide 15 — Layered dataset

Explain controlled, clean, partial, no-signal, and limitation roles. The purpose
is to prevent one polished score from hiding different claims.

Open:

- `docs/evaluation/DATASET_DESIGN.md`

### Slide 16 — Real-APK proof bundle

Explain that an APK is counted only after binary, source, dependency-tree,
report, and source-validation evidence are connected.

Open:

- `docs/evaluation/REAL_APK_PROOF_BUNDLE_PLAN.md`
- `docs/evaluation/REAL_APK_CURRENT_PROOF_BUNDLE.md`

### Slide 17 — Evaluation evidence buckets

Explain what each bucket supports and why limitation cases stay outside exact
Maven metrics.

Open:

- `docs/evaluation/APK_TYPE_EVALUATION.md`

### Slide 18 — Dataset composition

State:

- `72` controlled fixtures;
- `102` source-validated real APKs;
- `5` clean and `97` partial;
- `4` explicit boundary cases.

Open:

- `data/results/evaluation/thesis-evaluation-tables.json`

### Slide 19 — Evaluation method

Explain that controlled fixtures can support full metrics, while real APKs use
source trees to confirm emitted versions. Do not call the real-APK metric full
dependency recall.

Open:

- `docs/evaluation/THESIS_EVALUATION_TABLES.md`

### Slide 20 — Normal result versus v2 lane

State `927/1837` first. Then present `6772/6772` as a separate bounded,
source-known recognition result.

Open:

- `docs/thesis/FINAL_V2_RESULTS_SECTION.md`

### Slide 21 — V2 upper-bound explanation

Explain that exact source coordinate-version slices isolate recognition from
candidate-selection difficulty. Mention the remaining `5238` source-gap rows.

Open:

- `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_VERSION_EVALUATION.md`
- `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_GAP_TRIAGE.md`

### Slide 22 — Demo proof artifacts

Show:

1. clean F-Droid report;
2. CycloneDX SBOM;
3. controlled vulnerable Jackson report;
4. transparency export.

Open:

- `data/results/report-real-f-droid-final-demo-osv/report.html`
- `data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json`
- `data/results/demo-osv-vulnerable-jackson-databind/report.html`
- `data/results/evaluation/demo-final-transparency-export.json`

### Slide 23 — Mixed result interpretation

Explain clean, partial, and boundary outcomes. Difficult cases become the
research roadmap rather than being deleted.

Open:

- `docs/evaluation/LARGE_COMBINED_REAL_APK_ANALYSIS.md`

### Slide 24 — Failed experiments

Present rejected experiments as evidence of regression discipline. Explain that
fixing one target is insufficient if controls regress.

Open:

- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`

### Slide 25 — AI problem formulation

Explain that AI predicts evidence roles and risk states, not final Maven
versions. Splits are grouped by APK case.

Open:

- `src/apk_sbom/ai_r8_assistant.py`
- `docs/research/AI_R8_ASSISTED_METHOD_SELECTION.md`

### Slide 26 — RandomForest

Explain why it was chosen: structured numeric evidence, fast training, class
weights, and feature importance. State `0.708` macro-F1 and report-only use.

Open:

- `docs/evaluation/AI_R8_ASSISTANT_SUMMARY.md`

### Slide 27 — Deep learning

Contrast:

- MVP-safe structured-token Transformer: `0.882`;
- raw-opcode Transformer: `0.110`;
- opcode-count baseline: `0.128`.

Explain that the negative result is retained honestly.

Open:

- `docs/evaluation/AI_R8_DL_PROTOTYPE_MVP_SAFE.md`
- `docs/evaluation/AI_R8_RAW_OPCODE_TRANSFORMER.md`

### Slide 28 — AI integration gate

State that report-only assistance is ready, while matcher, SBOM, and CVE
authority remain blocked.

Open:

- `docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md`
- `docs/evaluation/FINAL_AI_DEFENSE_DEMO.md`

### Slide 29 — Live demo flow

Use saved artifacts. Do not rebuild the large reference DB or rerun the full
evaluation live.

Open:

- `docs/evaluation/FINAL_DEMO_CHECKLIST.md`

### Slide 30 — Limitations and next work

Priorities:

1. stronger version-distinctive evidence;
2. better independent candidate recall;
3. larger independent R8/opcode corpus;
4. strict APK-only promotion controls;
5. separate native and hidden-code research.

Open:

- `docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md`

### Slide 31 — Conclusion

Close with:

1. end-to-end APK-to-CycloneDX/CVE pipeline;
2. transparent realistic evaluation;
3. guarded matcher and AI research.

Final sentence:

> The contribution is not a perfect-looking score; it is a useful, measurable, and transparent reverse-SBOM system.

## Backup Slides: When And How To Use Them

### Slide 32 — Architecture module-to-file map

Use when asked:

- “Where is this implemented?”
- “Which module owns each pipeline stage?”

Point the jury to the component paths in this companion.

### Slide 33 — Matcher weights

Use when asked:

- “What is the scoring formula?”
- “Which signal is strongest?”
- “Are weights probabilities?”

Explain that weights are normalized evidence contributions, not probabilities.
API and opcode tri-gram global weights remain zero.

### Slide 34 — Reference DB scale

Use when asked:

- “How large is the database?”
- “Why are dependencies still missing?”

Separate reference coverage from matcher recall.

### Slide 35 — APK-family classification

Use when asked:

- “Why do some APKs behave differently?”
- “Are native/protected apps counted as failures?”

Explain that categories control which claims each APK can support.

### Slide 36 — Source-gap taxonomy

Use when asked:

- “Why are `5238` source rows missing?”

Separate boundary/alias rows, missing-reference rows, and matcher-recall rows.

### Slide 37 — Regression matrix

Use when asked:

- “Which ideas failed?”
- “How did you avoid overfitting?”

Show that unsafe global improvements were retained as negative evidence.

### Slide 38 — RandomForest detail

Use when asked:

- “Which classes are hard?”
- “Did one feature dominate?”

Discuss confusion and ablation evidence; do not imply production authority.

### Slide 39 — Transformer detail

Use when asked:

- “How was the split performed?”
- “Why did raw opcode learning fail?”

Explain the small case-heldout corpus and the need for broader independent APK
coverage.

## Live Demo Preparation

Open these before entering presentation mode:

1. `data/results/report-real-f-droid-final-demo-osv/report.html`
2. `data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json`
3. `data/results/source-validation/fdroid-final-demo-osv/source-validation.md`
4. `data/results/demo-osv-vulnerable-jackson-databind/report.html`
5. `data/results/demo-osv-vulnerable-jackson-databind/osv-vulnerabilities.json`
6. `data/results/evaluation/demo-final-transparency-export.json`
7. `docs/evaluation/FINAL_AI_DEFENSE_DEMO.md`

Do not depend on live OSV access. The saved artifacts are sufficient.

## Fast Jury Answers

### Why not use Gradle or a normal source SBOM tool?

The target begins with a compiled APK where source dependency metadata is not
available. If the source project is available, source-based SBOM generation is
preferable.

### Why not use only package names?

Package names are useful for recall but can be renamed, flattened, or shared.
The matcher combines name, structural, opcode, dependency, literal, and
version-distinctive evidence.

### Is `927/1837` precision or recall?

It is an emitted Maven version confirmation rate. It is not full dependency
recall.

### Why is v2 `6772/6772`?

V2 constrains each case to its known source coordinate-version slice. It tests
recognition under bounded candidate selection and is therefore an upper bound,
not APK-only accuracy.

### Why separate identity and version?

Library presence can be strong while adjacent versions are bytecode-equivalent.
Combining the claims would create false exact versions and false confirmed CVEs.

### How does the matcher resist R8?

It combines package, class, method, opcode, dependency-graph, literal, and
version-distinctive evidence. It is obfuscation-aware, not obfuscation-proof.

### Why are some advanced signals disabled?

They were implemented and tested, but global promotion either produced no
benefit or regressed controls. The project keeps them diagnostic or scoped.

### Why RandomForest?

The evidence is structured and numeric. RandomForest trains quickly, supports
class weighting, exposes feature importance, and is easier to defend.

### Why keep the failed raw-opcode Transformer?

It is an honest negative result that demonstrates the implementation and shows
that the current 14-APK corpus is insufficient.

### Does AI modify the SBOM?

No. AI is report-only and cannot change matcher scoring, selected versions,
components, or vulnerability labels.

### What is the strongest future improvement?

Stronger independent version-distinctive evidence and candidate recall, followed
by larger independent R8 corpora and strict APK-only promotion gates.

## Project Navigation Index

| Topic | Start here |
|---|---|
| Architecture | `docs/architecture/MVP_ARCHITECTURE.md` |
| Design choices | `docs/architecture/DECISIONS_LOG.md` |
| APK extraction | `src/apk_sbom/apk_extractor.py` |
| DEX features | `src/apk_sbom/dex_analyzer.py` |
| Maven download | `src/apk_sbom/maven_downloader.py` |
| Reference conversion | `src/apk_sbom/reference_converter.py` |
| Reference SQLite DB | `src/apk_sbom/reference_features.py` |
| Matcher logic | `src/apk_sbom/matcher.py` |
| Detection models | `src/apk_sbom/models.py` |
| CycloneDX output | `src/apk_sbom/sbom.py` |
| OSV/CVE logic | `src/apk_sbom/vulnerability.py` |
| JSON/Markdown/HTML reporting | `src/apk_sbom/report.py` |
| AI assistant | `src/apk_sbom/ai_r8_assistant.py` |
| AI authority gate | `src/apk_sbom/ai_r8_mvp_integration_gate.py` |
| Hybrid router | `src/apk_sbom/hybrid_matcher_router.py` |
| Accepted/rejected experiments | `docs/thesis/EXPERIMENT_DECISION_LEDGER.md` |
| Paper-to-code traceability | `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md` |
| Normal evaluation | `docs/evaluation/THESIS_EVALUATION_TABLES.md` |
| V2 package | `docs/evaluation/DEMO_FINAL_V2_PACKAGE.md` |
| Transparency | `docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md` |
| Final demo checklist | `docs/evaluation/FINAL_DEMO_CHECKLIST.md` |

## Final Rehearsal Checklist

- Add student, supervisor, university, and defense-date details.
- Rehearse the compressed route once and the full route once.
- Keep slides `20-21` wording exact.
- Open all saved demo artifacts before presenting.
- Do not run long evaluation or database-build commands live.
- Use backup slides only when they answer a jury question.
- Finish with the three contributions and invite questions.
