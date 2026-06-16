# Experiment Decision Ledger

This ledger preserves both positive and negative experiment results for the thesis/paper. A method is allowed into the MVP only when it improves a target case and passes the current controls. Rejected, disabled, blocked, or deferred methods are kept here as evidence instead of being hidden.

Companion files:

- `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`
- `docs/thesis/PAPER_BACKED_MVP_IMPROVEMENT_NOTES.md`
- `docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md`
- `docs/research/R8_OBFUSCATION_METHOD_SELECTION.md`

## Decision Policy

| Rule | Why it matters |
|---|---|
| Keep negative experiments | Failed promotions show where the MVP avoids overfitting and false exact-version claims. |
| Separate diagnostic from default scoring | Report-only and experiment-only signals can be useful without changing SBOM output. |
| Require current controls | A target improvement is not enough if clean, partial, generated, or source-validated controls regress. |
| Prefer narrow scoped rules over global weights | Android libraries often have adjacent-version and app-era ambiguity, so broad scoring changes can flip correct versions. |
| Keep paper/tool evidence attached | The final report should explain which state-of-the-art idea motivated each feature and why the MVP accepted, changed, or rejected it. |

## Method Decisions

| Method or idea | Paper/tool evidence | Project evidence | MVP decision | Reason |
|---|---|---|---|---|
| LibScout-style reference profile backbone | LibScout and later reference-profile tools show exact matching works when code evidence is preserved. | Current matcher and calibrated reference DB produce clean exact confirmations on controlled and clean real APKs. | Implemented | It is explainable and stable for normal APKs, but confidence is capped when evidence is weak. |
| Guarded source-used reference promotion | TPL-Benchmark warns against overfitted version coverage; LibScout-style methods depend heavily on reference coverage. | Nextcloud and Markor source-used experiments improved targets, but broad additions regressed other apps; guarded subsets were safer. | Implemented only with current-control gates | Reference expansion helps only when every promoted version passes clean and partial controls. |
| Generic newer-version or near-tie recency rule | Version-level detectors often fail on adjacent versions; TPL-Benchmark and Systematic Assessment warn against simple thresholds. | Version-band diagnostics show Activity, ViewPager2 beta, Concurrent Futures, and Lifecycle ties can improve one app while regressing another. | Rejected globally | Recency is not independent evidence of the compiled version. |
| Global opcode tri-gram weighting | ATVHunter, LibScan, LibID, SAD, and LibHunter motivate opcode/call-chain evidence. | `docs/evaluation/OPCODE_API_SIGNAL_DIAGNOSTICS.md`: opcode weight `0.02` regressed OpenTracks and Conversations with no confirmed-version improvement. | Disabled by default | Opcode evidence is useful diagnostically, but the current global weight is unsafe. |
| Global API-reference weighting | API evidence is common in static analysis and can survive renaming. | `docs/evaluation/OPCODE_API_SIGNAL_DIAGNOSTICS.md`: API-reference weight `0.05` changed no source-validation metrics. | Disabled by default | No measured benefit in the guarded slice. |
| POM/dependency coherence as a broad scorer | Dependency metadata can support ambiguous version decisions when coherent with nearby artifacts. | `docs/evaluation/POM_COHERENCE_DIAGNOSTICS.md` keeps risky rows diagnostic because generic metadata rules are not clean enough. | Diagnostic or scoped only | Metadata helps explain candidates, but it must not override stronger APK evidence. |
| Artifact-family disambiguation | Real Android libraries split artifacts across runtime, KTX, JVM, Android, and Compose families. | `docs/evaluation/ARTIFACT_FAMILY_DIAGNOSTICS.md` confirms existing scoped Okio/OkHttp/Lifecycle behavior and rejects new global family rules. | Scoped existing rules only | Family evidence is useful only for known ambiguity patterns. |
| Phase 1 R8/obfuscation classifier fields | Android R8 guide, ObfDetector, LibHunter, and TPL-Benchmark show shrink, optimize, package changes, and low confidence are important signals. | `inspect-apk` and report outputs expose report-only R8 diagnostics. | Implemented report-only | The fields explain risk without changing selected components or versions. |
| Phase 2 controlled R8 matrix | R8 official behavior and ObfDetector motivate rename, shrink, optimize, repackage, and inlining stress coverage. | Generated matrix covers clear, rename, shrink, optimize, shrink+optimize, package flattening, inline-like stress, multidex/multi-library controls. | Implemented as controls | The matrix is used to reject unsafe future scoring changes. |
| Phase 3 inert multi-scale features | LibHunter, SAD, ATVHunter, LibID, LibScan, and LibMD motivate call-chain, basic-block, class-neighbor, field-operation, literal/context, and multi-scale fusion evidence. | `docs/evaluation/R8_MULTISCALE_FEATURE_DIAGNOSTICS.md` confirms extraction and report availability with scoring disabled. | Implemented inertly | Feature extraction is useful, but no score consumes it until experiments prove safety. |
| Global Phase 4 multi-scale R8 blend | LibMD is the north-star for multi-scale fusion; SAD/LibHunter/ATVHunter motivate the feature families. | `docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md`: 4 real improvements, but 6 controlled regressions, 30 real source-validated regressions, and 8 clean-real regressions. | Rejected globally | The signal is real but unsafe as a default scorer. |
| Phase 5 scoped R8 trigger | Same multi-scale tool family, plus TPL-Benchmark/Systematic Assessment guardrails for realistic controls. | `docs/evaluation/R8_PHASE5_SCOPED_TRIGGER_DIAGNOSTICS.md`: 286 rows evaluated, 4 target improvements kept, 0 triggered regressions, 0 triggered conflicts. `docs/evaluation/R8_PHASE5_TRIGGER_CONTROL_VALIDATION.md`: 11 validation gates pass, including controlled/clean/boundary blocking. `docs/evaluation/R8_PHASE5_REPORT_EVIDENCE.md`: 4 opt-in target reports, 4 separate suggestions, and 0 default selection changes. The opt-in `r8-phase5-experiment` command writes diagnostic JSON/Markdown, and `generate-report --include-r8-phase5-experiment` can show saved report-only evidence. | Experiment-only, not promoted | The trigger is narrow and promising, but default matcher/SBOM behavior remains unchanged. |
| LibAttention-style ML/DL assistance | LibAttention reports strong R8 library-presence improvement with learned representations. ObfDetector and TPL-Benchmark require caution for exact-version claims under hard R8. | Phase 6A now builds a classical ML training dataset from matcher-recall, transparency, Phase 5, and R8 diagnostic evidence and exposes `apk-sbom ai-r8-*` report-only commands. Phase 6B has a trained isolated structured-token Transformer prototype. | Implemented report-only / DL isolated | AI can assist identity/risk triage and PhD-facing methodology, but it cannot change selected versions, SBOM components, CVE labels, or source-validation metrics. |
| Hidden DEX/protector Maven recovery | Packers/protectors can hide code; ObfDetector and Android malware literature motivate explicit boundary handling. | `docs/evaluation/HIDDEN_DEX_DIAGNOSTICS.md` emits nonstandard DEX/protector risk and avoids false Maven claims. | Boundary/report-only | Hidden code should produce risk warnings, not invented Maven components. |
| Native package/version recovery | Native `.so` libraries need a separate native-analysis and provenance pipeline. | `docs/evaluation/NATIVE_BOUNDARY_DIAGNOSTICS.md` reports native files as hash-only components. | Out of MVP scope | Maven package/version recovery from native blobs is a different problem. |
| K-9 dependency-tree source validation | Source validation improves confidence when dependency trees can be resolved. | `docs/evaluation/K9_BLOCKER_DIAGNOSTICS.md` records repeated Gradle dependency-tree timeouts/failures. | Blocked, not counted as clean accuracy | Build-system blockers are documented as scope limitations instead of forced metrics. |

## Paper Framing

The thesis should describe the MVP as evidence-gated rather than perfect. The important contribution is not that every state-of-the-art idea was promoted. The stronger claim is:

> We integrated paper-backed signals only when they survived controlled and real APK regression checks; when they failed, we preserved them as diagnostics or future work.

This supports a realistic Android APK-to-SBOM story: R8/obfuscation, app-era drift, reference coverage, native code, hidden DEX, and dependency metadata all affect version-level SBOM recovery. The MVP therefore reports confidence and limitations instead of forcing exact versions where the evidence is unsafe.
