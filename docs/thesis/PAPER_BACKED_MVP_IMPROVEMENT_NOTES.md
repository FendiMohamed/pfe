# Paper-Backed MVP Improvement Notes

This note preserves the current MVP weaknesses, the improvement plan, and the state-of-the-art basis for each decision. Use it when writing the final thesis, preparing slides, or explaining why the tool reports uncertainty instead of hiding difficult cases.

Companion traceability matrix: `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`.
Experiment decision ledger: `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`.

Operational generated plan: `docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md`.

## Position

The MVP should keep improving, but it should not chase a perfect-looking score by removing hard APKs or forcing versions that are not supported by evidence. The thesis argument is stronger if the tool is evaluated by APK family and if every improvement is tied to a paper, tool, or experiment.

The current direction is:

```text
measure limitation -> connect to state of the art -> implement guarded improvement -> rerun controls -> report the remaining uncertainty
```

## Current MVP Cons And Planned Improvements

| Current con | Evidence from our experiments | Paper/tool basis | Improvement policy |
|---|---|---|---|
| Exact version recovery is fragile for nearby AndroidX/Kotlin versions. | NewPipe, Wikipedia, Conversations, AntennaPod, KDE Connect, Aegis, and Nextcloud still contain near-version AndroidX ties. | SAD shows adjacent versions need structural and literal tie-breakers; LibMD proposes probability-style version scoring; TPL-Benchmark and ObfDetector show realistic version recovery is lower under modern APK conditions. | Keep version confidence separate from identity confidence. Emit exact only when evidence is strong, and emit ambiguous version sets for feature-equivalent or near-tie candidates. |
| R8, shrinking, inlining, and optimization reduce stable bytecode evidence. | Controlled R8 fixtures are handled well, but real APKs still expose version-band and missing-evidence limits. | LibHunter and LibAttention make R8 a first-class threat model; ObfDetector shows advanced obfuscation can severely reduce version-level accuracy. | Evaluate by R8/obfuscation category. Use lower confidence or uncertainty when APK evidence is weak instead of claiming R8-proof recovery. |
| Reference DB coverage strongly affects results. | Markor source-used calibration reaches 19/19 only as an app-specific experiment; a guarded follow-up promoted only `core@1.9.0`, improving Markor to 7/19 with no control regressions. Nextcloud's full source-version experiment improves Nextcloud but regresses F-Droid, NewPipe, and AntennaPod. | LibScout-style reference profiles require coverage; TPL-Benchmark shows real tools fail when datasets and versions are incomplete. | Promote only guarded source-used versions that improve a target and do not regress the current-control matrix. Keep risky versions as experiment evidence. |
| App-specific improvement can be unsafe globally. | Activity `1.9.2`, ViewPager2 `1.1.0-beta02`, Activity `1.6.0`, and Concurrent Futures `1.0.0` improve one case but regress controls. A generic newer-near-tie rule also creates false flips. | Systematic Assessment and TPL-Benchmark both support realistic cross-app evaluation instead of cherry-picked success cases. | Require current-control regression runs before any global rule or DB promotion. Preserve partial cases instead of hiding them. |
| Overlapping artifact families are hard to resolve. | Okio/Okio-JVM, OkHttp public-vs-Android targets, Lifecycle public-vs-Android targets, and KMP Android variants need special handling. | LibMD's multi-scale and metadata graph idea supports combining bytecode evidence with dependency/coherence evidence. | Keep scoped artifact-family rules only where they are validated across controls. Prefer Android bytecode-bearing target artifacts when public coordinates contain little or no comparable bytecode. |
| Dependency metadata helps, but it is not enough by itself. | Maven POM dependency coherence is implemented, but it remains dormant for Startup because no independently detected supporting dependency is present. | LibMD's LDG/dependency-graph idea supports metadata coherence, but SBOM tools also show that metadata alone is not APK evidence. | Use POM coherence only as a conservative tie-breaker when another independently selected component supports the candidate. |
| Opcode/API signals can regress if globally weighted. | API-reference weight `0.05` changed no metrics. Opcode tri-gram weight `0.02` regressed OpenTracks and Conversations without improving Nextcloud. | ATVHunter, LibScan, LibID, SAD, and LibHunter justify opcode/API/call-chain features, but these signals need calibration. | Keep API-reference and opcode tri-gram weighting disabled by default. Revisit only as scoped per-coordinate rerankers with fresh controls. |
| R8 multi-scale evidence helps only when tightly scoped. | Phase 4 global blending found 4 real source-validated improvement candidates but regressed controlled and real rows. Phase 5 narrowed the trigger to those profiles, kept 4 target improvements with 0 triggered regressions/conflicts, passed 11 current-control validation gates, and is available through the opt-in `r8-phase5-experiment` command plus optional `generate-report --include-r8-phase5-experiment` report-only evidence. The generated report-evidence summary validates 4 target APK reports with 4 separate suggestions and 0 default selection changes. | LibHunter, SAD, ATVHunter, LibID, LibScan, and LibMD support multi-scale R8 evidence; TPL-Benchmark and Systematic Assessment require realistic controls. | Keep Phase 5 command and report evidence experiment-only; production scorer wiring needs separate fresh controls. |
| Native libraries are outside Maven version recovery. | Organic Maps and Termux emit native file components, not Maven package versions. | CycloneDX supports file components; APK reverse-SBOM papers mostly focus on bytecode libraries, not native package identity. | Report native `.so` files as hash-only file components and exclude them from Maven-version accuracy. |
| Hidden DEX, packed payloads, and dynamic loading can hide code from static extraction. | The hidden-DEX limitation fixture raises nonstandard DEX, tiny primary DEX, protector-name, and opaque-payload indicators, then avoids false Maven claims. | Obfuscation studies and systematic assessments show that advanced packaging and dynamic behavior remain hard for static tools. | Raise extraction/obfuscation risk and avoid accuracy claims when code is not recoverable. |
| K-9 / Thunderbird Android is source-linked but not dependency-tree validated. | APK/source/report/catalog evidence exists, but Gradle dependency-tree generation still stalls before `fossReleaseRuntimeClasspath`. | Evaluation methodology papers support separating validated, blocked, and excluded cases. | Keep K-9 as `partial-gradle-blocked` until resolved dependency-tree validation exists. Do not count it in source-validated accuracy. |
| CVE mapping can mislead when the version is uncertain. | OSV matching is useful, but a wrong exact version can create a wrong vulnerability conclusion. | ATVHunter emphasizes vulnerable-version detection; LibMD is SBOM-oriented; CycloneDX/Syft/cdxgen/Trivy/Grype-style workflows depend on correct package identities and versions. | Classify high-confidence exact matches as confirmed and low-confidence or ambiguous versions as potential findings. |

## Improvements Already Implemented

| Improvement | Why it matters | Evidence anchor |
|---|---|---|
| Identity confidence and version confidence are separated. | A library can be real while its exact version remains uncertain. | Current reports and CycloneDX properties expose identity and version status separately. |
| Version ambiguity is first-class output. | Near-tie versions are no longer silently presented as exact. | Reports, JSON, HTML, CycloneDX, and SBOM reload preserve `ambiguous_versions`. |
| Source-validation splits clean, partial, blocked, and limitation cases. | Mixed results become scientifically readable instead of being reduced to one misleading score. | Thesis evaluation tables and APK-type evaluation keep these rows separate. |
| Guarded reference DB promotion is the default policy. | It prevents one APK improvement from damaging the shared tool behavior. | Nextcloud guarded subset and runtime-only promotion improved Nextcloud without regressing current controls. |
| POM dependency metadata is stored and conservatively used. | Metadata is useful only when supported by independently detected APK-side evidence. | Startup remains honest because the POM rule does not force unsupported ties. |
| API-reference and opcode tri-gram experiments are preserved but disabled. | Negative experiments are useful thesis evidence and prevent overfitting. | API weight had no metric change; opcode tri-gram global weighting regressed controls. |
| Generated APK evaluation was expanded by category. | Controlled tests cover clear version-band, R8 rename, R8 shrink, and multi-library multidex behavior. | Controlled set is 30 fixtures / 35 expected Maven components / 35 exact confirmations. |
| Native-heavy and hidden-code cases are explicit limitations. | Boundary behavior is part of the tool's honesty. | Organic Maps, Termux, and the hidden-DEX fixture are excluded from Maven-version accuracy. |

## Next Plan

1. Use this note and `docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md` as the cons/improvement source for the final report.
2. Keep the current ambiguity/confidence behavior as an MVP strength, not an apology.
3. Use the diagnostic per-coordinate reranker report in `docs/evaluation/VERSION_TIE_RERANKER_DIAGNOSTICS.md` as current no-change evidence: no clean independent signal currently justifies a matcher scoring change for the risky ties.
4. Use `docs/evaluation/SOURCE_VERSION_CANDIDATE_QUEUE.md` before any future reference DB experiment; source-used versions must be tracked as target benefit plus control risk.
5. If more accuracy work continues, require version-unique APK evidence or independent support before any scoped reranker is proposed.
6. Require a fresh current-control regression matrix before any scoped reranker, global rule, or DB promotion becomes official.
7. Grow the source-validated real APK set by category rather than by convenience. Prioritize missing families such as framework-heavy apps, stronger obfuscation, older dependency stacks, native-heavy boundaries, and blocked build-system cases.
8. Keep K-9 blocked unless the Gradle build-plugin issue is worth a deeper investigation.
9. Add external SBOM scanner validation only after `cyclonedx-cli`, Trivy, or Grype are installed.

## Thesis Framing

When writing the thesis, do not describe partial APKs as failures. Describe them as evidence that Android APK-to-SBOM recovery depends on APK type, reference coverage, compiler behavior, and version-band similarity.

The strongest claim is:

```text
The MVP improves APK-to-SBOM recovery by combining state-of-the-art static library-detection ideas with SBOM evidence, confidence-aware version reporting, and APK-category evaluation. It reports exact versions when supported, ambiguous candidates when evidence is close, and limitations when static evidence is insufficient.
```

This aligns the implementation with the state of the art while keeping the results credible.
