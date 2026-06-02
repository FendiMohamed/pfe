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
- downweight brittle name- or layout-dependent signals when minification indicators are strong
- tune confidence and ambiguity policy specifically for minified builds

Why later than the first two:

- the problem is real, but the current repo evidence says version-band ambiguity is the bigger immediate issue
- optimization-aware logic can become risky if introduced too broadly

Success condition:

- better behavior on real release-minified partial rows
- fewer overconfident exact claims on R8-damaged evidence

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
