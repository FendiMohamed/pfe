# Version Disambiguation Optimization Plan

Date: 2026-06-02.

This plan captures the most useful optimization work for the current APK-to-SBOM tool based on:

- the state-of-the-art comparison in `docs/research/STATE_OF_ART_VERSION_HANDLING_COMPARISON.md`
- the current real-APK evaluation evidence
- the project's existing guardrails around regression-safe reference DB growth

The focus is not on chasing a bigger raw match count. The main goal is to improve exact-version recovery without destabilizing other APKs.

## Core Recommendation

Prioritize improvements in this order:

1. better near-version disambiguation
2. more systematic guarded reference-DB promotion
3. stronger coarse-to-fine candidate pruning
4. limited optimization-aware logic for R8/minified cases
5. better uncertainty output
6. defer any major ML jump

## Priority Plan

| Priority | Area | Why this matters now | Recommended work | Risk level |
| --- | --- | --- | --- | --- |
| P1 | Near-version disambiguation | The tool often finds the right library family but struggles with nearby versions, especially AndroidX, Kotlin, coroutines, and Okio/OkHttp bands. | Increase weighting for version-unique evidence, strengthen literal and constant tie-breakers, improve artifact-family coherence, and prefer explicit version-band scoring over forced exact winners. | Medium |
| P1 | Guarded reference-DB promotion workflow | Reference growth helps some APKs but can regress cleaner controls. This is already a demonstrated risk in the repo. | Automate candidate version experiments, control-matrix comparison, and outcome labels such as `safe`, `app-specific`, and `regression-risk`. Keep shared promotion gated by clean controls. | Low to medium |
| P2 | Coarse-to-fine candidate pruning | The literature repeatedly supports staged filtering before expensive or fragile version scoring. | Improve family-level pruning, class-subset candidate mapping, and candidate reduction before final version scoring. | Medium |
| P2 | Optimization-aware logic | R8/minified cases remain an important practical weakness, but a full architecture rewrite is not needed yet. | Add targeted handling for shrinking and inlining damage patterns, downweight brittle signals in minified builds, and improve confidence policy for release/minified APKs. | Medium to high |
| P3 | Uncertainty and ambiguity output | Better output quality immediately improves thesis honesty and tool usability even when exact matching remains hard. | Expand version-range or competing-version output, expose reason labels such as `coverage-gap`, `near-tie`, and `artifact-family`, and strengthen report/SBOM confidence wording. | Low |
| P4 | Major ML-based detection jump | ML may help under heavy obfuscation, but it is not the best next move for the current project stage. | Defer large LibAttention-style work until the current rule-based and evidence-based weaknesses are pushed further. | High |

## Detailed Actions

### P1 - Better Near-Version Disambiguation

This is the highest-value optimization.

Progress on 2026-06-02:

- added a diagnostic-only raw literal/context version-tie experiment
- tested the existing Phase 4 source-validated rows with a minimum score of `0.10` and a minimum advantage of `0.05`
- rejected direct production promotion because the raw signal produces `2` regression-risk replacements and `0` confirmed target improvements
- kept matcher scoring, selected versions, SBOM output, vulnerability labels, and source-validation metrics unchanged
- added a fresh version-unique literal/context diagnostic over `24` controlled rows and `224` real source-validated rows
- rejected the broad one-match version-unique context signal because it finds `2` target improvements but also `2` one-match regression risks
- added a stricter minimum-support promotion candidate: `>=2` matched version-unique literal/context features keeps the VLC RecyclerView `1.2.1 -> 1.3.2` recovery and filters all `3` one-match suggestions, leaving `1` target improvement and `0` regression risks in the diagnostic matrix
- added an opt-in matcher/report/SBOM flag for the guarded reranker; the default matcher path remains unchanged
- targeted VLC validation with the opt-in flag selected `androidx.recyclerview:recyclerview@1.3.2` while keeping `androidx.gridlayout:gridlayout@1.0.0`
- regenerated the affected target/control report slice with the same Phase 4 DB and only the opt-in flag changed: VLC improves from `6/26` to `7/26` source-confirmed Maven versions, AntennaPod remains `19/20`, OsmAnd remains `16/25`, missing counts stay `0`, and all `6` current-control gates pass
- added a broader default-promotion readiness gate that combines the broad diagnostic matrix with report/source-validation evidence: `248` rows inspected, `3` low-support rows filtered, `1` kept improvement, `0` kept regressions, and `8/8` readiness gates pass
- promoted the guarded `>=2` matched version-unique literal/context reranker to default matcher/report/SBOM behavior while keeping `--disable-version-unique-literal-context-reranker` for pre-promotion baseline reproduction
- verified the promoted no-flag default path on VLC: `androidx.recyclerview:recyclerview@1.3.2` is emitted and source-confirmed, VLC validates `7/26`, focused Docker promotion tests pass `50/50`, and the full Docker suite passes `178/178`
- automated the guarded reference-DB promotion policy layer with a manifest-driven generator over existing isolated experiment comparisons
- classified `7` historical experiments / `24` candidate-version slots: `2` singleton-safe versions, `1` clean exact tested bundle, `4` app-specific experiments, `0` regression-risk experiments in the current manifest, and `0` failed workflow gates

Current artifacts:

- `docs/evaluation/LITERAL_CONTEXT_VERSION_TIE_DIAGNOSTICS.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DIAGNOSTICS.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_PROMOTION_CANDIDATE.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_CURRENT_CONTROL_VALIDATION.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DEFAULT_PROMOTION_READINESS.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DEFAULT_PROMOTION_VERIFICATION.md`
- `docs/evaluation/GUARDED_REFERENCE_DB_PROMOTION_WORKFLOW.md`

Next optimization:

- move to limited optimization-aware diagnostics for R8/minified cases
- identify shrink/inlining damage patterns, brittle signal risks, and confidence/ambiguity policy without changing default selected versions
- keep any optimization-aware scoring or reranking disabled until fresh controlled and real source-validation controls justify it

Recommended actions:

- strengthen version-unique feature weighting where the APK contains evidence that only one nearby version explains
- improve literal, constant, and resource-backed tie-breakers
- keep artifact-family disambiguation scoped and evidence-driven
- export a version-band result when multiple nearby candidates remain feature-equivalent

Why first:

- this matches the strongest recent papers most closely, especially SAD and LibMD
- this also matches the current partial real-APK failure pattern in the repo better than broad "detect more things" work

Success condition:

- fewer false exact-version flips
- more correct exact recoveries in current partial rows
- more ambiguity rows that are justified rather than guessed

### P1 - Systematic Guarded Reference-DB Promotion

We should keep growing the reference DB, but make the growth process cheaper and more repeatable.

Completed on 2026-06-02:

- added `configs/guarded_reference_db_promotion_experiments.json`
- added `scripts/build_guarded_reference_db_promotion_workflow.py`
- generated `docs/evaluation/GUARDED_REFERENCE_DB_PROMOTION_WORKFLOW.md`
- classified `7` existing isolated comparisons and `24` candidate-version slots with explicit singleton versus exact-tested-bundle scope
- recorded `2` singleton-safe candidates, `1` safe tested bundle, `4` app-specific experiments, and `0` failed gates
- kept future `regression-risk` and `no-change` outcomes as first-class policy labels even though the current manifest does not contain examples of those outcomes

Recommended actions:

- batch-test candidate source-used versions in isolated experiment DBs
- auto-compare target APK improvements against current controls
- label each candidate addition as:
  - `safe`
  - `app-specific`
  - `regression-risk`
- generate a promotion summary before touching the shared calibrated DB

Why first:

- the repo already shows that broad source-used coverage can improve one APK and hurt others
- this is one of the clearest places where our tool can be stronger than the papers operationally

Success condition:

- faster safe coverage growth
- fewer manual calibration loops
- clearer thesis evidence for why some versions were not globally promoted

### P2 - Stronger Coarse-to-Fine Candidate Pruning

This is the best structural optimization after the two top priorities.

Diagnostic progress on 2026-06-02:

- added `scripts/build_coarse_to_fine_pruning_diagnostics.py`
- generated `docs/evaluation/COARSE_TO_FINE_PRUNING_DIAGNOSTICS.md`
- measured `81` existing generated and real reports with `3,561` post-threshold pre-reportability decision rows and `8,106` candidate-version slots
- found `2,360` high-pressure rows, including `2,212` close bands and `2,074` near ties
- kept this phase diagnostic-only: matcher scoring, selected versions, SBOM output, and vulnerability labels remain unchanged
- recommended an offline family-identity prefilter simulation that preserves every version inside retained close bands
- ran the report-backed family-identity proxy simulation with `(0.35 * package_score) + (0.65 * class_score)` across `8` guarded margins
- rejected the simple proxy: every reducing margin loses tracked source families; even margin `0.50` drops `9` real source families, while margin `1.0` stays clean only by pruning nothing
- kept production matching unchanged and moved the next offline experiment toward a stronger dependency/literal or class-subset family signal
- added `scripts/build_composite_family_shortlist_simulation.py`
- evaluated `54` stronger report-backed configurations across package, class, method, dependency, and literal evidence
- kept the balanced-context profile plus independent-support rescue at margin `0.10` as a live-offline-validation candidate: it removes `1,351/8,106` candidate-version slots (`16.67%`) with `0` tracked controlled/real source-family losses while retaining complete version bands
- kept the result pre-production: a live offline recomputation must still confirm selected-version and source-validation behavior
- added `scripts/build_composite_family_shortlist_live_validation.py` with per-case caching and progress output after the initial full run proved too slow as an all-or-nothing command
- restored `data/test_apks/real/termux/termux.apk` from F-Droid and verified SHA-256 `fdd476982cd74f2f00aac12d3683b1fa260a0b2d146411b94e09d773be3a7b56`
- live validation now recomputes APK features for `81/81` cases (`62` controlled, `19` real), removes `1,347/8,100` reference rows (`16.63%`), and produces `0` tracked source-family losses, `0` tracked source-selection regressions, `0` reportable selected-version changes, and `0` failed gates
- kept the result as an opt-in candidate only; production matching remains unchanged until a separate explicit matcher experiment and fresh controls pass
- added explicit matcher/report flags: `--enable-composite-family-shortlist-experiment` and `--composite-family-shortlist-margin`
- generated `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_OPT_IN_MATCHER_EXPERIMENT.md` as broad implementation-control evidence: all `62` controlled-generated cases plus `4` representative real APKs keep the shortlist disabled by default, enable it only under the flag, remove `1,311` reference rows, keep `0` reportable selected-version changes, and pass `0` failed gates
- kept the broad opt-in control as a pre-default gate, not a default-promotion gate; a full all-case opt-in control run must still pass before any default change
- reran the same opt-in control artifact over the full all-case inventory: `81/81` cases (`62` controlled-generated and `19` real), default path disabled in `81/81`, opt-in enabled in `81/81`, `1,347` reference rows removed, `0` reportable selected-version changes, and `0` failed gates
- added `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_READINESS.md` as the default-promotion readiness gate: full live validation and full opt-in matcher controls both cover `81/81` cases, remove `1,347/8,100` reference rows (`16.63%`), preserve `0` tracked source-family losses, `0` tracked source-selection regressions, `0` reportable selected-version changes, and pass `11/11` gates
- promoted the composite family shortlist to default behavior, added `--disable-composite-family-shortlist` for pre-promotion baseline reproduction, kept `--enable-composite-family-shortlist-experiment` as a compatibility alias, and added `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_VERIFICATION.md`
- the no-flag generated Gson smoke enables the shortlist, removes `31` reference rows, and keeps top selected version `2.8.6`; the disable flag restores the disabled baseline
- focused Docker promotion tests pass `56/56`, full Docker `pytest -q` passes `201/201`, local and Docker `python -m compileall src scripts tests` pass, and `git diff --check` passes with only normal Windows LF/CRLF warnings
- added `docs/evaluation/CLASS_CORRESPONDENCE_PRUNING_DIAGNOSTICS.md` as the final P2 pruning comparison beyond the promoted shortlist: `54` class/package/method correspondence configurations over `3,561` family decision rows and `8,106` candidate-version slots; strict reducing class-correspondence has `0` clean configurations and all `24` strict reducing configurations lose tracked source families, while the best rescued lane is safe but removes only `1,210` slots versus the promoted composite shortlist's `1,351`
- class-correspondence pruning stays diagnostic-only; the P2 candidate-pruning lane is stable enough to move to limited optimization-aware diagnostics

Recommended actions:

- improve family-level candidate pruning before exact version scoring
- add stronger class-subset or class-correspondence candidate mapping
- reduce final version scoring to a narrower and better-supported candidate set

Why next:

- ATVHunter, ORLIS, and LibScan all support staged filtering
- this can improve both speed and precision without changing the whole tool

Success condition:

- fewer noisy close-version comparisons
- lower scoring load on clearly irrelevant version candidates
- better precision on large dependency trees

### P2 - Limited Optimization-Aware Logic

This should be a targeted improvement, not a rewrite.

Recommended actions:

- recognize common shrink/inlining damage patterns in release-minified APKs
- keep global optimization-aware scoring diagnostic-only while Phase 4 regression blockers remain
- tune confidence and ambiguity policy specifically for minified builds before changing selected versions

Why later than the first two:

- the problem is real, but the current repo evidence says version-band ambiguity is the bigger immediate issue
- optimization-aware logic can become risky if introduced too broadly

Success condition:

- better behavior on real release-minified partial rows
- fewer overconfident exact claims on R8-damaged evidence

Progress:

- added `docs/evaluation/R8_OPTIMIZATION_AWARE_DIAGNOSTICS.md` as the limited optimization-aware decision gate
- combined Phase 4, Phase 5 trigger-control validation, and Phase 5 report-only evidence
- kept global multi-scale default scoring rejected because the expanded Phase 4 signal still has `6` controlled and `30` real regression blockers, including `8` clean-real blockers
- kept the scoped Phase 5 trigger experiment/report-only: `4` target suggestions, `0` triggered regressions/conflicts, `0` default report selection changes, and `0` production imports
- added `docs/evaluation/R8_MINIFIED_CONFIDENCE_POLICY_DIAGNOSTICS.md` as the minified-row confidence/ambiguity policy gate: `286` Phase 4 rows classified, `36` regression-risk rows blocked from default changes, `4` source-backed Phase 5 improvements kept report-only, `0` default report selection changes, `0` production imports, and `6/6` gates pass
- implemented opt-in report wording through `generate-report --include-r8-minified-confidence-policy` and added `docs/evaluation/R8_MINIFIED_CONFIDENCE_REPORT_EVIDENCE.md`: `4` target reports, `4` report-only suggestions, `10` blocked regression-risk rows, `4` SBOM artifacts, and `0` default selection changes
- added generic report uncertainty wording through `version_uncertainty_summary` in JSON plus Markdown/HTML "Version Uncertainty Summary"; `docs/evaluation/VERSION_UNCERTAINTY_REPORTING.md` records a controlled R8 smoke with `26` decisions, `26` uncertainty rows, `18` near-ties, `7` single-reference boundaries, and the emitted Gson component unchanged at `2.8.9`
- next safe work is outside this optimization plan: resume real-APK evidence growth or blocker resolution from the documented queue, while preserving source-validation bucket boundaries

### P3 - Better Uncertainty Output

This is low-risk and immediately useful.

Recommended actions:

- export competing versions or version bands more clearly
- label mismatch causes with stable categories such as `coverage-gap`, `near-tie`, and `artifact-family`
- improve Markdown, JSON, HTML, and CycloneDX wording for ambiguity and confidence

Why it matters:

- it improves the quality of the SBOM and report output even before any scoring breakthrough
- it supports the thesis argument that partial and ambiguous results are useful evidence, not failures

Success condition:

- easier review of hard rows
- cleaner proof bundles
- less temptation to overstate weak exact-version selections

Progress:

- `generate-report` now writes `version_uncertainty_summary` to JSON and shows a matching Markdown/HTML "Version Uncertainty Summary" section
- the section labels explicit ambiguity, near-ties, low-confidence version claims, uncertain rows, single-reference boundaries, and existing policy-selected rows
- the section is report-only and does not change matcher scoring, selected versions, SBOM components, vulnerability labels, or source-validation metrics

### P4 - Defer Major ML Work

Recommended stance:

- do not make ML the next implementation priority
- revisit only after the current interpretable bottlenecks are pushed further

Why defer:

- the current bottlenecks are still explainable and local
- ML would increase complexity, training burden, and evaluation cost
- the project still has more obvious wins in version disambiguation and guarded coverage growth

## Best Next 3

If only three optimization tracks should be worked on next, use this order:

1. better near-version disambiguation
2. automated guarded reference-DB promotion
3. stronger coarse-to-fine candidate pruning

This combination best matches both:

- the strongest ideas from the literature
- the actual failure modes in the current real-APK dataset

## What Not To Optimize First

- do not start with a broad global scoring rule like "newer near-tie wins"
- do not add many source-used versions directly to the shared calibrated DB without current-control checks
- do not prioritize a large ML pipeline before improving interpretable version disambiguation
- do not chase higher apparent accuracy by hiding partial or ambiguous rows

## Companion Docs

- `docs/research/STATE_OF_ART_VERSION_HANDLING_COMPARISON.md`
- `docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md`
- `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`
- `docs/evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md`
