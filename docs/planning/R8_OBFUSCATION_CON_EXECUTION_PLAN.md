# R8 Obfuscation Con Execution Plan

Status: Phase 1 report-only classifier, Phase 2 controlled matrix expansion, Phase 3 inert multi-scale feature extraction, expanded Phase 4 layered generated+real diagnostics, the Phase 5 scoped trigger diagnostic, and Phase 5 trigger control validation are complete without a default scoring change; Phase 6A now adds a report-only classical ML assistant and Phase 6B now has isolated DL prototype scaffolding. No R8 behavior is justified as global/default behavior.

This con is based on a deep review of the project literature notes and the current diagnostic artifacts, not on a single intuition. The decision is to build a best-of-tools R8 layer: combine the strongest ideas from LibAttention, LibHunter, SAD, ATVHunter, LibID/LibScan, and LibMD, but integrate them in guarded stages so the tool stays honest about exact-version confidence.

Companion artifacts:

- `docs/research/R8_OBFUSCATION_METHOD_SELECTION.md`
- `docs/evaluation/R8_OBFUSCATION_DIAGNOSTICS.md`
- `docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md`
- `docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md`
- `docs/evaluation/R8_PHASE5_TRIGGER_CONTROL_VALIDATION.md`
- `docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md`
- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`
- `docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md`

## Evidence Basis

| Source/tool | Best idea | How it affects this con |
|---|---|---|
| Android R8 documentation | R8 is not only renaming; it shrinks, optimizes, inlines, merges classes, rewrites code, and can shrink resources. | The classifier must track multiple R8 symptoms, not just obfuscated names. |
| LibAttention | Strongest reported R8/obfuscation robustness for library presence through learned Smali/code representations. | Useful later as identity/risk assistance, but not first authority for exact Maven versions or SBOM claims. |
| LibHunter | Best R8-specific idea for method inlining and call-site optimization. | This is the key future scorer upgrade, after controlled matrix expansion. |
| SAD | Strong version-level structural matching using CDG summaries, stateful/stateless class handling, field-operation sequences, and literals. | Use these features for version disambiguation after report-only classifier work. |
| ATVHunter | Version-to-vulnerability pipeline with CDG module decoupling and CFG/opcode matching. | Use two-stage matching and basic-block/opcode evidence, but do not assume this alone solves R8. |
| LibID / LibScan | CFG/basic-block/class signatures, containment, method opcode similarity, and call-chain similarity. | Use these as inert diagnostic features before any weight promotion. |
| LibMD | Best conceptual architecture: multi-scale fusion, dependency graph evidence, Bayesian/probability scoring, SBOM goal. | Use as the north-star scoring model once enough evidence layers exist. |
| ObfDetector / TPL-Benchmark | Realistic benchmarks show hard obfuscation can sharply reduce version-level detection. | Keep claims confidence-based and require control matrices before any scorer promotion. |

## Core Decision

Do not choose one tool as the winner. Build a layered hybrid:

1. LibAttention-like identity/risk thinking for difficult R8 cases.
2. LibHunter-like inlining and call-site awareness.
3. SAD-like structural version matching.
4. ATVHunter, LibID, and LibScan-like opcode/basic-block/call-chain evidence.
5. LibMD-like evidence fusion and confidence scoring.

The important engineering rule is to add these layers in this order:

`report-only classifier -> controlled matrix -> inert features -> scoped experiments -> scoring promotion`

No global scoring change should happen before the classifier and matrix exist.

## Phase 1 - Report-Only Obfuscation Classifier

Goal: explain R8/protector risk without changing selected components or versions.

Status: complete for Phase 1. `inspect-apk` and `generate-report` now expose the structured diagnostics block, and representative controlled R8 plus hidden-DEX reports were regenerated. Matcher scoring, selected component/version behavior, source-validation metrics, vulnerability classification, and SBOM component selection remain unchanged.

Add app-level and component-level fields for:

- short-name density: one-letter/two-letter package, class, method, and field ratios.
- package flattening or repackaging: package-depth collapse, shallow-package concentration, default/unknown package concentration.
- class/method coverage loss: top-candidate class and method coverage compared with reference.
- low structural coverage: low CDG/class/method/literal evidence even when a candidate is emitted.
- low-confidence component ratio: app-level ratio of candidate/low components.
- nonstandard DEX/protector hints: existing hidden-DEX indicators carried into the R8 risk summary.
- resource-shrinking symptoms: low resource count or missing resource namespaces where the extractor can observe them.
- inlining/class-merging indicators: method-count collapse, large caller-method concentration, class-count mismatch, many-reference-to-one-class concentration.

Expected output:

- `inspect-apk` and `generate-report` expose a structured obfuscation/R8 diagnostics block.
- Markdown, HTML, and JSON reports explain why confidence is low.
- Existing component/version choices remain unchanged.

Completion rule:

- Add targeted tests for the classifier fields.
- Regenerate a representative controlled R8 report and hidden-DEX report.
- Run local compileall, Docker tests, Docker compileall, and `git diff --check`.

## Phase 2 - Controlled R8 Matrix Expansion

Goal: test harder R8 conditions before touching scoring.

Status: complete for Phase 2. `scripts/build_controlled_apk.py` and `scripts/run_generated_apk_batch.py` now generate/evaluate the expanded controlled R8 matrix without changing matcher scoring or selected component/version behavior. The latest generated batch built/reported 44 fixtures with 48 expected Maven components and 0 failures; component recall, exact-version recall, and candidate-version recall are all `1.000`. The generated R8 slice covers 30 expected components across rename, shrink, optimize, shrink+optimize, package flattening/repackaging, and inline-like call-site stress. Package-flattening, rename, shrink, and shrink+optimize fixtures stay low-confidence/medium-risk evidence rather than broad R8-proof claims.

Expand controlled fixtures beyond current rename/shrink:

- clear baseline.
- rename/minify.
- shrink.
- optimize.
- shrink plus optimize.
- package flattening/repackaging where feasible.
- inline-like/call-site stress where feasible.

Target libraries:

- Gson
- Jackson Databind
- OkHttp / Okio
- Retrofit
- Commons Codec
- one AndroidX/Kotlin library if the fixture pipeline can support it

Expected output:

- A generated matrix report showing component recall, exact-version recall, candidate-version recall, confidence distribution, and risk labels per R8 mode.
- Current rename/shrink successes stay visible as mechanics evidence, not broad R8-proof evidence.

Completion rule:

- New fixture rows are generated and evaluated. Complete for Phase 2.
- Existing controlled and real controls do not regress. Complete for Phase 2 and the later dataset-growth-v2 controlled expansion: no matcher/scoring/source-validation/vulnerability/SBOM selection code changed, controlled evaluation is 84/84 exact confirmations in the regenerated thesis tables, and real source-validation totals are unchanged by the R8 diagnostic itself. After later dataset growth, the overall source-validated emitted Maven confirmation total is 250/369.
- The thesis/evaluation tables are regenerated. Complete for Phase 2.

## Phase 3 - Inert Multi-Scale Feature Extraction

Goal: add the strongest paper-backed features without letting them affect scoring yet.

Status: complete for Phase 3. DEX analysis now extracts call-chain opcode fingerprints, basic-block opcode fingerprints, class-neighbor summaries, field-operation sequences, and literal/context features; reference feature extraction stores them in SQLite; matcher summaries and JSON/Markdown/HTML reports expose availability counts. These features remain diagnostic-only and are not consumed by matcher scoring, selected versions, source-validation metrics, vulnerability labels, or SBOM component selection.

Add or store diagnostic features:

- LibHunter-like call-site and inlining evidence.
- SAD-like class-neighbor summaries.
- SAD-like stateful/stateless class classification.
- SAD-like field-operation sequences.
- ATVHunter/LibID/LibScan-like basic-block opcode fingerprints.
- LibScan-like call-chain opcode fingerprints.
- version-unique literal and structural context features.

Expected output:

- Features are visible in debug/experiment JSON or reference DB tables.
- All weights remain disabled by default.
- Reports can show feature availability without claiming better accuracy.

Completion rule:

- Feature extraction tests pass. Complete for Phase 3.
- Existing source-validation metrics are unchanged at default settings. Complete for Phase 3: no scoring or component-selection code consumes the new features, and the representative inline-stress report marks them as disabled/inert.

## Phase 4 - Scoped Experiments

Goal: prove whether the new evidence improves hard R8 cases without hurting controls.

Status: expanded layered diagnostic complete. `docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md` first ranked 24 generated R8 cases, then rebuilt a calibrated 100-component multi-scale DB and ranked 24 controlled R8 cases plus 262 real APK component rows from the layered APK taxonomy. The calibrated pass finds 4 real source-validated improvement candidates, but also 6 controlled regression blockers, 30 real source-validated regression blockers, and 8 clean-real regression blockers. This blocks any global multi-scale scorer promotion.

Experiment policy:

- Run experiments only on high-obfuscation, low-confidence, or known R8/minified cases.
- Compare against the fresh current-control matrix.
- Track confirmed, mismatched, missing, and ambiguous versions.
- Reject any global rule that regresses clean or partial controls.

Candidate experiments:

- call-chain/basic-block evidence as a reranker for low-confidence candidates.
- field-operation sequence evidence for stateful classes.
- class-neighbor summaries for adjacent-version ambiguity.
- containment-style matching for inlined callee evidence.

Completion rule:

- A diagnostic report records improved, unchanged, and regressed cases. Complete for the first controlled Phase 4 pass.
- Only scoped, control-clean improvements can move to scoring. Current result: no promotion, because regression-risk rows exist.

## Phase 5 - Scoped R8-Aware Scoring

Goal: use new evidence only where it is justified.

Status: experiment-only scoped trigger diagnostic, explicit opt-in command, report-only evidence surface, confidence/ambiguity report wording, and current-control validation complete. `src/apk_sbom/r8_scoped_reranker.py` implements a pure trigger decision around the four Phase 4 improvement profiles. `apk-sbom r8-phase5-experiment` runs that trigger only as an explicit diagnostic command and writes experiment JSON/Markdown from the Phase 4 artifact. `generate-report --include-r8-phase5-experiment` can attach the saved experiment summary and matching suggestions to JSON/Markdown/HTML reports as report-only evidence. `generate-report --include-r8-minified-confidence-policy` can attach the saved minified confidence policy labels as wording-only evidence. `docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md` evaluates it across 286 Phase 4 rows: the trigger applies to 4 target rows, preserves all 4 improvements, and triggers 0 regressions/conflicts. `docs/evaluation/R8_PHASE5_TRIGGER_CONTROL_VALIDATION.md` validates 11 gates. `docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md` validates the opt-in Phase 5 report surface on four target APKs: 4 suggestions, 4 SBOM artifacts, and 0 default selection changes. `docs/evaluation/R8_MINIFIED_CONFIDENCE_REPORT_EVIDENCE.md` validates the minified confidence report surface on the same target set: 4 report-only suggestions, 10 blocked regression-risk rows, 4 SBOM artifacts, and 0 default selection changes. It is not wired into default matcher scoring, selected versions, SBOM output, vulnerability labels, or source-validation metrics.

Promotion requirements:

- A target hard case improves.
- Clean source-validated real APKs do not regress.
- Existing partial source-validated APKs do not regress.
- Controlled R8 matrix improves or stays stable.
- The scorer still emits ambiguity when exact version evidence is weak.

Allowed scoring shape:

- scoped reranker, not global weight.
- high-obfuscation or low-version-confidence trigger only.
- identity confidence and version confidence remain separate.
- source-validation-aware vulnerability labels remain conservative.

Current result:

- The Phase 5 trigger is cleaner than the rejected Phase 4 global blend and is exposed through the explicit opt-in `r8-phase5-experiment` command plus optional report-only `generate-report --include-r8-phase5-experiment` evidence.
- The four generated target reports keep official MVP versions unchanged while surfacing four separate Phase 5 suggestions; see `docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md`.
- The minified confidence report surface can also show the four source-backed suggestions plus ten blocked regression-risk rows as report-only wording; see `docs/evaluation/R8_MINIFIED_CONFIDENCE_REPORT_EVIDENCE.md`.
- Keep it diagnostic-only. Any future production scorer wiring needs its own fresh regression tests.
- Do not enable it by default.

## Phase 6 - AI-Assisted R8 Layer

Goal: add AI knowledge for hard R8/minified and matcher-recall analysis while preserving the thesis honesty rules.

### Phase 6A - Classical ML Report-Only Assistant

Implemented first because it is explainable, fast, and trainable from current project evidence.

Commands:

- `apk-sbom ai-r8-build-dataset`
- `apk-sbom ai-r8-train`
- `apk-sbom ai-r8-suggest`

Artifacts:

- `data/results/experiments/ai-r8-assistant/training-dataset.json`
- `data/results/experiments/ai-r8-assistant/training-dataset.csv`
- `data/results/experiments/ai-r8-assistant/model.joblib`
- `data/results/experiments/ai-r8-assistant/metrics.json`
- `data/results/experiments/ai-r8-assistant/suggestions.json`
- `docs/evaluation/AI_R8_ASSISTANT_DIAGNOSTICS.md`

Use ML only as:

- identity hint,
- obfuscation/risk classifier,
- candidate generator,
- or report-only triage support.

Do not use ML as the sole exact-version or CVE authority. The AI assistant must not change matcher scoring, selected versions, SBOM output, vulnerability labels, or source-validation metrics.

### Phase 6B - Isolated DL/Transformer Prototype

Implemented only as research scaffolding:

- `scripts/build_ai_r8_token_corpus.py`
- `scripts/train_ai_r8_tiny_transformer.py`

This is LibAttention-inspired future work over opcode/DEX token sequences. It is not wired into `generate-report` and must stay separate unless it clearly outperforms Phase 6A and passes controls.

## What Counts As Done

This con is not done when one report looks better. It is done only when:

- report-only classifier fields exist and are tested;
- expanded R8 matrix exists;
- multi-scale features are extracted inertly;
- scoped experiments show no control regressions;
- any scoring change is narrowly promoted and documented;
- AI output remains report-only unless a separate future validation proves otherwise;
- docs, thesis artifacts, and tasks are regenerated;
- verification passes.

## Current Next Step

Current next step:

Do not promote the multi-scale diagnostic blend globally. Use Phase 6A AI only as opt-in report-only assistance and keep the Phase 6B Transformer prototype isolated. Default matcher scoring and SBOM selection remain unchanged.
