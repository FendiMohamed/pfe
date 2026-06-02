# R8 Obfuscation Con Continuation Prompt

Use this prompt in a later Codex session to continue the R8/obfuscation con without losing the reasoning.

```text
Read these files first:

- docs/codex/CODEX_CONTEXT.md
- TASKS.md
- docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md
- docs/planning/R8_OBFUSCATION_CON_EXECUTION_PLAN.md
- docs/research/R8_OBFUSCATION_METHOD_SELECTION.md
- docs/evaluation/R8_OBFUSCATION_DIAGNOSTICS.md
- docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md
- docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md
- docs/evaluation/R8_PHASE5_TRIGGER_CONTROL_VALIDATION.md
- docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md
- docs/evaluation/NEXT_REAL_APK_GROWTH_QUEUE.md
- docs/thesis/EXPERIMENT_DECISION_LEDGER.md

Continue the final P4 R8/obfuscation con.

Important context:

- The research decision is already made: build a best-of-tools layered R8 approach.
- Do not choose one detector blindly. Combine the strongest ideas:
  - LibAttention for later R8 identity/risk assistance.
  - LibHunter for method inlining and call-site optimization.
  - SAD for class-neighbor summaries, stateful/stateless handling, field-operation sequences, and literal tie-breakers.
  - ATVHunter, LibID, and LibScan for basic-block opcode, CFG, and call-chain evidence.
  - LibMD for multi-scale fusion and Bayesian/confidence scoring.
- The current status is Phases 1, 2, 3, expanded layered Phase 4 diagnostics, and the Phase 5 scoped trigger diagnostic complete, default scoring unchanged.
- The expanded Phase 4 diagnostic uses a calibrated 100-component multi-scale DB and ranks 24 controlled R8 cases plus 262 real APK component rows. It finds 4 real source-validated improvement candidates, but 6 controlled regressions, 30 real source-validated regressions, and 8 clean-real regressions still reject global multi-scale scoring.
- The Phase 5 diagnostic implements `src/apk_sbom/r8_scoped_reranker.py` and exposes it through the explicit opt-in `apk-sbom r8-phase5-experiment` command. `generate-report --include-r8-phase5-experiment` can attach the saved experiment summary and matching suggestions as report-only evidence. It evaluates a profile-scoped trigger across 286 Phase 4 rows, keeps the 4 target improvements, and triggers 0 regressions/conflicts, but it is not promoted into default matcher scoring, selected versions, SBOM output, vulnerability labels, or source-validation metrics.
- The Phase 5 trigger control validation passes 11 gates, including blocking 24 controlled rows, 43 clean real rows, and 36 boundary rows while keeping 4 partial target improvements.
- The generated `docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md` summary validates the opt-in report path on the four target APKs: 4 separate suggestions, 4 SBOM artifacts, and 0 default selection changes.
- Before Phase 6/ML work, grow the dataset by classification. The generated dataset-growth-v2 slice adds Okio/Ktor/modern-networking controlled coverage; the next real APK batch should follow `docs/evaluation/NEXT_REAL_APK_GROWTH_QUEUE.md` and include clean non-sparse, older dependency, real R8/minified, protected/heavy-obfuscated, framework-boundary, and native-heavy classes.
- The first category-balanced real smoke batch is now collected and reported in `docs/evaluation/REAL_APK_GROWTH_BATCH_V2.md`: LocalSend, OpenVPN for Android, KeePassDX, Gadgetbridge, DAVx5, Shelter, TheXTech, and Fennec F-Droid. DAVx5, OpenVPN for Android, Gadgetbridge, and Shelter have partial source-validation proof bundles in `docs/evaluation/REAL_APK_GROWTH_BATCH_V2_PROOF_STATUS.md`; keep the remaining four rows out of source-validated metrics until matching source/runtime dependency-tree proof bundles exist. A low-risk preflight batch in `docs/evaluation/LOW_RISK_REAL_APK_PROOF_STATUS.md` adds Stopwatch, Bubble, and Audio Source as source-validated partial no-native/modern-Gradle candidates, plus Blue Square Speedometer as a successful no-Maven-signal control. The remaining important acquisition gap is a legal real protected/packed or strongly obfuscated limitation APK.
- `docs/evaluation/LOW_RISK_SOURCE_VERSION_EXPERIMENT.md` records the guarded reference-coverage follow-up: the broad 10-version source-used experiment improves targets but regresses controls, and narrow `recyclerview@1.0.0` / `lifecycle-runtime@2.1.0` checks still regress controls. Keep these versions experiment-only and leave the shared calibrated DB unchanged until a stronger version-band discriminator is proven.
- `docs/evaluation/LOW_RISK_VERSION_BAND_DIAGNOSTICS.md` is the reproducible per-coordinate follow-up. It records 9 resolved target mismatch rows and 13 new mismatch rows elsewhere, with AppCompat, Core, Fragment, Lifecycle Runtime, and Lifecycle ViewModel conflicts. Use this artifact as the fixture set for any future scoped discriminator; do not wire a new rule into default scoring without a fresh zero-regression control matrix.
- `apk-sbom version-band-experiment` is now an explicit opt-in AppCompat/Core old-version-steal diagnostic. `docs/evaluation/LOW_RISK_VERSION_BAND_TRIGGER_DIAGNOSTICS.md` records 7/13 introduced mismatch rows flagged for downgrade and 0/9 resolved target rows blocked. Keep it disconnected from default scoring. The next version-band research task is Lifecycle public-vs-Android artifact-family separation, not promotion of this small learned fixture trigger.
- `apk-sbom lifecycle-family-experiment` is the corresponding opt-in Lifecycle public-vs-Android separation diagnostic. It records 5 introduced Lifecycle rows, 2 public-coordinate downgrade candidates, 1 patch near-tie kept ambiguous, 2 insufficient-evidence rows, and 0/3 resolved target rows blocked. Keep it disconnected from default scoring and do not force Android-target replacement versions.
- `generate-report --include-version-band-experiments` can now attach both saved version-band diagnostics as report-only annotations in JSON/Markdown/HTML and CycloneDX application metadata. This is an annotation surface only; it must not change detected components, selected versions, SBOM component selection, vulnerability labels, source-validation metrics, matcher scoring, or the shared DB.

Work instructions:

1. Inspect the Phase 3 diagnostic artifacts, generated R8 matrix, real source-validation controls, matcher feature-loading, report schema, and tests before editing.
2. Do not rerun the same global blend as a promotion attempt. Use the explicit `r8-phase5-experiment` command and optional report-only `generate-report --include-r8-phase5-experiment` evidence for scoped diagnostics only, and require fresh controls before any production scorer promotion.
3. Continue real APK proof-bundle growth before Phase 6/ML. Start from the 8-app smoke batch in `docs/evaluation/REAL_APK_GROWTH_BATCH_V2.md`; prioritize promoting feasible source-linked rows, and acquire a legal protected/heavy-obfuscated limitation APK separately.
4. Keep all Phase 3 features diagnostic-only by default; do not change matcher scoring, selected versions, vulnerability classification, SBOM component selection, or source-validation metrics unless a narrower scoped experiment proves a clean promotion.
5. Add targeted tests proving any experiment is opt-in and default scoring behavior is unchanged.
6. Regenerate the relevant diagnostic/evaluation/research docs after experiment output changes.
7. Update TASKS.md, docs/codex/CODEX_CONTEXT.md, and docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md.
8. Run verification:
   - python -m compileall src scripts tests
   - docker compose run --rm apk-sbom pytest -q
   - docker compose run --rm apk-sbom python -m compileall src scripts tests
   - git diff --check

Completion rule:

Move beyond experiment-only Phase 5 only if an explicit flag or scorer improves target cases, avoids the current controlled, clean-real, and partial-real regression risks, and stays scoped, opt-in or narrowly triggered, and clean against fresh controls.
```
