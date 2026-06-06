# Version Handling and R8/Obfuscation Experiment Summary

Date: 2026-06-03.

This note summarizes the version-handling and R8/obfuscation work in a form that can be shown to a professor or pasted into a continuation account. The detailed evidence remains in the linked evaluation and planning artifacts.

## Executive Summary

The experiments were not random scoring changes. They were based on the state-of-the-art review and on the current real-APK failure modes in this repository:

- version mismatches often happen because the tool finds the right library family but cannot safely distinguish nearby versions;
- adding many source-used versions to the shared reference database can improve one APK while hurting another;
- R8/minification creates real evidence loss, but broad R8-aware scoring introduced too many regressions to promote globally.

Final decision:

- promote only the version-handling changes that passed guarded controls;
- keep R8/obfuscation improvements diagnostic or opt-in/report-only until a future scorer passes fresh clean-real and partial-real controls;
- expose uncertainty instead of forcing weak exact-version claims.

## Version Handling Results

### Promoted To Default

1. Guarded version-unique literal/context reranker.

   The broad literal/context signal was tested and rejected, because one-match evidence produced both improvements and regression risks. A stricter gate was then tested: require at least two matched version-unique literal/context features before reranking a near-version decision.

   Result:

   - broad raw literal/context signal: rejected;
   - one-match version-unique context signal: rejected;
   - strict `>=2` matched version-unique evidence: promoted;
   - VLC improved from `6/26` to `7/26`;
   - RecyclerView was corrected from `1.2.1` to source-confirmed `1.3.2`;
   - AntennaPod stayed `19/20`;
   - OsmAnd stayed `16/25`;
   - missing counts stayed `0`;
   - readiness gates passed with `1` kept improvement and `0` kept regressions;
   - full Docker suite passed after promotion.

2. Composite family shortlist pruning.

   This is a coarse-to-fine candidate reduction step. It removes irrelevant reference rows before final version scoring while preserving all versions inside retained families.

   Result:

   - `81/81` generated and real cases evaluated;
   - `1,347/8,100` reference rows removed, or `16.63%`;
   - `0` tracked source-family losses;
   - `0` tracked source-selection regressions;
   - `0` reportable selected-version changes;
   - promoted to default matcher/report/SBOM behavior;
   - `--disable-composite-family-shortlist` remains available for baseline reproduction.

3. Generic version uncertainty reporting.

   Reports now expose ambiguity instead of hiding it behind a single confident-looking selected version.

   Result:

   - JSON includes `version_uncertainty_summary`;
   - Markdown and HTML include a "Version Uncertainty Summary";
   - labels include explicit ambiguity, near-tie, low-confidence version, uncertain version, single-reference boundary, and policy-selected version;
   - controlled R8 smoke recorded `26` decisions, `26` uncertainty rows, `18` near-ties, and `7` single-reference boundaries;
   - emitted Gson stayed unchanged at `2.8.9`;
   - this is report-only and does not change matcher scoring, selected versions, SBOM components, CVE labels, or source-validation metrics.

### Rejected Or Kept Diagnostic

- Raw literal/context overlap was rejected.
- Broad one-match version-unique context reranking was rejected.
- Class-correspondence pruning was kept diagnostic-only because stricter reducing configurations lost tracked source families.
- Shared reference database growth remains guarded; new versions should be promoted only after current-control comparison.

## R8 And Obfuscation Results

The R8/obfuscation work followed a phased plan:

`report-only classifier -> controlled R8 matrix -> inert multi-scale features -> scoped experiments -> optional scoring promotion`

### Completed Phases

1. Phase 1: report-only R8/obfuscation diagnostics.

   `inspect-apk` and `generate-report` expose R8/minification risk signals such as short-name density, package flattening, coverage loss, low structural coverage, low-confidence component ratio, nonstandard DEX/protector hints, resource-shrinking symptoms, and inlining/class-merging indicators.

   Production impact: no scoring or SBOM behavior changed.

2. Phase 2: controlled R8 matrix expansion.

   The controlled generated fixture set covers rename, shrink, optimize, shrink+optimize, package flattening/repackaging, inline-like stress, clear controls, and multidex/multi-library controls.

   Result:

   - latest R8 matrix batch: `44` fixtures / `48` expected Maven components;
   - `0` failures;
   - `1.000` component recall;
   - `1.000` exact-version recall;
   - `1.000` candidate-version recall.

   Important limitation: this proves the mechanics on controlled cases. It is not broad proof that real-world heavy R8 is solved.

3. Phase 3: inert multi-scale feature extraction.

   The tool now extracts paper-backed features such as call-chain opcode fingerprints, basic-block opcode fingerprints, class-neighbor summaries, field-operation sequences, and version-unique literal/context features.

   Production impact: features are stored/surfaced but not used in default scoring.

4. Phase 4: expanded generated-plus-real diagnostic.

   The multi-scale diagnostic was tested across controlled R8 cases and real APK component rows.

   Result:

   - `24` controlled R8 rows evaluated;
   - `262` real APK component rows evaluated;
   - `4` real source-validated improvement candidates found;
   - `6` controlled regression blockers found;
   - `30` real source-validated regression blockers found;
   - `8` clean-real regression blockers found.

   Decision: reject global multi-scale default scoring.

5. Phase 5: scoped R8 trigger, experiment-only/report-only.

   A narrow trigger was implemented for the four Phase 4 improvement profiles. It is exposed through the explicit experiment command and optional report-only evidence.

   Result:

   - `286` Phase 4 rows evaluated;
   - trigger applies to `4` target rows;
   - `4` improvements kept;
   - `0` triggered regressions;
   - `0` triggered conflicts;
   - `11` control gates passed;
   - `0` production imports;
   - `0` default report selection changes.

   Current surfaced report-only suggestions:

   - AntennaPod `androidx.core:core` official MVP `1.15.0`, diagnostic suggestion `1.16.0`;
   - Wikipedia `androidx.viewpager2:viewpager2` official MVP `1.0.0`, diagnostic suggestion `1.1.0`;
   - Aegis `androidx.viewpager2:viewpager2` official MVP `1.0.0`, diagnostic suggestion `1.1.0`;
   - Nextcloud `androidx.swiperefreshlayout:swiperefreshlayout` official MVP `1.0.0`, diagnostic suggestion `1.2.0`.

   Production impact: no default matcher scoring, selected versions, SBOM components, vulnerability labels, or source-validation metrics changed.

6. Minified confidence/ambiguity policy.

   A report-only policy was added for minified rows.

   Result:

   - `286` Phase 4 rows classified;
   - `36` regression-risk rows blocked from default changes;
   - `4` source-backed suggestions kept report-only;
   - `4` target reports validated;
   - `10` blocked regression-risk rows shown in report evidence;
   - `4` SBOM artifacts checked;
   - `0` default selection changes;
   - `0` production imports.

## What This Means For The Thesis

This supports an honest thesis claim:

- the MVP improved exact-version handling where the evidence was strong enough;
- it does not overclaim heavy R8 recovery;
- it records R8/minified suggestions separately from official SBOM selections;
- it explains uncertainty in the report instead of hiding hard cases;
- it uses control gates to avoid a common paper/tool weakness: overfitting to a small set of success cases.

Recommended thesis wording:

> The project promotes guarded version-disambiguation improvements only when they pass current-control validation across controlled and real APKs. For R8/minified APKs, multi-scale and scoped-trigger evidence is currently exposed as diagnostic/report-only because broader default scoring produced regression risks on controlled, clean-real, and partial-real controls. This preserves SBOM correctness while documenting where future R8-aware scoring can safely continue.

## Detailed Evidence Files

Version handling:

- `docs/planning/VERSION_DISAMBIGUATION_OPTIMIZATION_PLAN.md`
- `docs/research/STATE_OF_ART_VERSION_HANDLING_COMPARISON.md`
- `docs/evaluation/LITERAL_CONTEXT_VERSION_TIE_DIAGNOSTICS.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DIAGNOSTICS.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_PROMOTION_CANDIDATE.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_CURRENT_CONTROL_VALIDATION.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DEFAULT_PROMOTION_READINESS.md`
- `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DEFAULT_PROMOTION_VERIFICATION.md`
- `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_READINESS.md`
- `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_VERIFICATION.md`
- `docs/evaluation/CLASS_CORRESPONDENCE_PRUNING_DIAGNOSTICS.md`
- `docs/evaluation/VERSION_UNCERTAINTY_REPORTING.md`

R8/obfuscation:

- `docs/planning/R8_OBFUSCATION_CON_EXECUTION_PLAN.md`
- `docs/research/R8_OBFUSCATION_METHOD_SELECTION.md`
- `docs/evaluation/R8_OBFUSCATION_DIAGNOSTICS.md`
- `docs/evaluation/R8_MULTISCALE_FEATURE_DIAGNOSTICS.md`
- `docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md`
- `docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md`
- `docs/evaluation/R8_PHASE5_TRIGGER_CONTROL_VALIDATION.md`
- `docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md`
- `docs/evaluation/R8_OPTIMIZATION_AWARE_DIAGNOSTICS.md`
- `docs/evaluation/R8_MINIFIED_CONFIDENCE_POLICY_DIAGNOSTICS.md`
- `docs/evaluation/R8_MINIFIED_CONFIDENCE_REPORT_EVIDENCE.md`

Continuation:

- `docs/codex/ACCOUNT_HANDOFF_CONTINUATION_PROMPT.md`
- `docs/codex/CODEX_CONTEXT.md`
- `TASKS.md`

## Safe Next Work

The safe next work is not to force R8 scoring into default behavior. Continue real-APK evidence growth and blocker resolution, then revisit R8 scoring only if a future scoped scorer improves target cases while passing fresh controlled, clean-real, and partial-real controls.
