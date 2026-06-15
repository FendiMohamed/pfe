# PFE Report Draft: APK-to-SBOM Recovery for Android Applications

## Working Title

Evidence-Based SBOM Recovery from Compiled Android APKs Using Hybrid Static Library Version Detection

## Abstract Draft

Software Bills of Materials are increasingly used to identify vulnerable dependencies, but most SBOM generation tools rely on source code, build manifests, package manager metadata, or dependency lock files. In Android security-audit scenarios, the available artifact is often only a compiled APK. This makes SBOM recovery harder because third-party libraries are embedded into DEX bytecode and may be renamed, optimized, shrunk, split across multidex files, or mixed with native libraries.

This project implements a static APK-to-SBOM MVP that extracts DEX, manifest, resource, and native-file evidence from Android APKs; compares bytecode features against a Maven reference database; estimates Maven library versions with confidence labels; emits CycloneDX SBOMs; and queries OSV for vulnerabilities. The tool combines package, class, method, opcode, class-dependency-graph, literal, Maven metadata, API-reference, and optional opcode-trigram evidence, while deliberately separating library identity confidence from exact version confidence.

The evaluation is organized by APK family instead of presenting a single perfect-looking score. The MVP confirms 84/84 expected Maven versions across 72 controlled fixtures, 47/47 emitted Maven versions on 5 clean source-validated real APKs, and 880/1790 emitted Maven versions on 97 harder source-validated real APKs. Overall, the current source-validated real APK set reaches a 927/1837 emitted Maven version confirmation rate. The remaining mismatches are reported as version-band, artifact-family, source-reference-coverage, or native/hidden-code limitations rather than hidden from the results.

## 1. Introduction

### 1.1 Context

Android applications frequently embed third-party libraries for networking, serialization, cryptography, user interface components, and platform integration. These dependencies can contain known vulnerabilities. A standard SBOM can help auditors and developers understand which components are present and which versions may be affected by CVEs or advisories.

However, Android APKs are not source packages. They are compiled archives containing DEX bytecode, resources, manifests, and sometimes native `.so` files. Maven coordinates and versions are usually absent from the APK. Optimization tools such as ProGuard and R8 can rename classes, remove unused code, inline methods, and make adjacent library versions nearly indistinguishable.

### 1.2 Problem Statement

Given only a compiled Android APK, the project aims to recover useful third-party library and version evidence, generate a standard CycloneDX SBOM, and map detected versions to known vulnerabilities.

The goal is not perfect recovery for every APK. The goal is a practical, evidence-based tool that gives strong claims when evidence is strong, partial claims when APK or reference evidence is ambiguous, and limitation warnings when the APK falls outside the supported scope.

### 1.3 Contributions

The project contributes:

1. A static APK analysis pipeline that extracts DEX, manifest, resource, and native-file evidence.
2. A Maven reference database workflow that downloads JAR/AAR artifacts, converts bytecode to DEX, and stores comparable features in SQLite.
3. A hybrid matcher that combines bytecode, graph, literal, metadata, and confidence signals for library identity and version estimation.
4. CycloneDX SBOM generation with PURL, confidence, evidence, native file components, and application metadata.
5. OSV vulnerability lookup with confidence-aware confirmed versus potential findings.
6. A controlled and real-APK evaluation methodology that separates clean, partial, blocked, and limitation cases.

## 2. State of the Art

The literature on Android third-party library detection shows that no single feature family is enough. Package names are useful but fragile under obfuscation. Reference profiles improve exact-version detection but depend on reference coverage. Graph and structural features improve robustness but can still fail under shrinking and method inlining. Recent studies also show that earlier papers often overestimate real-world accuracy, especially when benchmarks do not include modern R8 behavior.

This project adopts the practical parts of prior work:

| Research lesson | Project decision |
|---|---|
| Package names are fragile. | Treat package evidence as weak and combine it with structural evidence. |
| Reference profiles are needed for versions. | Build calibrated Maven reference databases. |
| Graph and opcode features help under obfuscation. | Use class dependency graphs and opcode-related features. |
| Version-level detection is harder than identity detection. | Separate identity confidence from version confidence. |
| R8 and shrinking must be evaluated directly. | Include controlled R8 fixtures and real partial cases. |
| SBOM output needs standard identifiers. | Emit CycloneDX with Maven PURLs and evidence properties. |
| Vulnerability matching depends on version confidence. | Mark low-confidence version findings as potential. |

The detailed paper synthesis is maintained in `papers/data/`, `papers/state_of_the_art.md`, and `work/state of the art/`.

### 2.1 Paper-To-Implementation Traceability

The implemented MVP is deliberately traceable to the state of the art. Reference-database matching follows the LibScout/ATVHunter/SAD family of approaches; class dependency and structural evidence follow LibPecker, LibID, LibScan, SAD, and LibMD; version confidence and ambiguity reporting adapt SAD's tie-breaking lesson and LibMD's probability-scoring direction; the R8-aware evaluation split is motivated by LibHunter, LibAttention, TPL-Benchmark, and ObfDetector; and the SBOM/CVE workflow follows LibMD's goal while using CycloneDX, PURL, and OSV as practical open standards.

The full traceability matrix is maintained in `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`. It should be used while writing the final state-of-the-art and implementation chapters so each MVP feature is presented as a paper-backed adaptation, not as an isolated engineering choice.

## 3. System Architecture

The MVP is a static pipeline:

```text
APK
-> extract DEX, manifest, resources, strings, and native files
-> analyze bytecode features
-> compare against Maven reference features
-> rank library and version candidates
-> assign identity/version confidence
-> emit CycloneDX SBOM
-> query OSV vulnerabilities
-> generate JSON, Markdown, and HTML reports
```

### 3.1 APK Extraction

The extraction layer reads the APK archive, discovers standard and nonstandard DEX files, extracts native `.so` files, records hashes, and collects manifest/application metadata when available. It also raises risk indicators such as tiny primary DEX, nonstandard DEX paths, protector-like asset names, and opaque payloads.

### 3.2 Reference Database

The reference database is built from curated Maven coordinates and versions. Artifacts are downloaded from Maven repositories, AAR/JAR packaging is handled explicitly, bytecode is converted to DEX with D8 when needed, and extracted features are stored in SQLite.

The project uses multiple reference DB modes:

| DB type | Purpose |
|---|---|
| Focused DB | Small controlled library set for early development. |
| Expanded DB | Broad latest-version identity stress testing. |
| Calibrated DB | Source-used versions and guarded promotions for evaluation. |
| Experiment DBs | Temporary API-reference, opcode-trigram, and app-specific calibration tests. |

### 3.3 Feature Extraction and Matching

The matcher uses several evidence families:

| Evidence | Role |
|---|---|
| Package/class/method overlap | Candidate generation and identity evidence. |
| Opcode histograms | Bytecode similarity signal. |
| Class dependency graph | Structural similarity under some obfuscation. |
| String literals and version-unique evidence | Tie-breaking when versions differ in literals or changed classes. |
| Maven POM dependencies | Conservative dependency-coherence support. |
| API/member references | Optional experimental signal, disabled by default in official reports. |
| Opcode tri-grams | Optional experimental sequence signal, disabled globally after regression tests. |

The official matcher is intentionally conservative. It avoids generic "newer version wins" rules because experiments showed that such rules can improve one APK while regressing others.

### 3.4 SBOM and Vulnerability Workflow

The tool emits CycloneDX JSON with Maven PURLs, component versions, evidence properties, confidence labels, and native file components. Native `.so` files are represented as file components with path, ABI, size, and SHA-256, not as Maven package/version claims.

OSV is used as the primary vulnerability lookup source. Findings are confidence-aware: high-confidence exact versions can be reported as confirmed findings, while low-confidence or ambiguous version candidates are treated as potential findings.

The report also surfaces version-band ambiguity directly. When two nearby versions are feature-equivalent or fall within a very small score gap without matched version-unique APK evidence, the selected version is kept as a candidate but the report adds explicit `version-ambiguity` evidence and a structured ambiguous-version set. The same set is written into CycloneDX as `apk-sbom:mvp:ambiguous-versions`. This improves practical usefulness because users can distinguish a strong exact version from a nearby-version hypothesis that needs source, dependency, or app-era confirmation.

## 4. Implementation

The implementation is a Python CLI package under `src/apk_sbom/` with helper scripts under `scripts/`.

| Area | Main files |
|---|---|
| CLI orchestration | `src/apk_sbom/cli.py` |
| APK extraction | `src/apk_sbom/apk_extractor.py` |
| DEX analysis | `src/apk_sbom/dex_analyzer.py` |
| Maven download/reference build | `src/apk_sbom/maven_downloader.py`, `src/apk_sbom/reference_converter.py`, `src/apk_sbom/reference_features.py` |
| Matching | `src/apk_sbom/matcher.py` |
| SBOM generation | `src/apk_sbom/sbom.py` |
| Vulnerability lookup | `src/apk_sbom/osv.py` |
| Report generation | `src/apk_sbom/report.py` |
| Evaluation scripts | `scripts/build_apk_type_evaluation.py`, `scripts/build_thesis_evaluation_tables.py` |

The implementation avoids hardcoded perfect results: reports are generated from matcher outputs, and source validation compares emitted SBOM components against resolved dependency trees where available.

## 5. Evaluation

The detailed evaluation prose is available in `docs/evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md`. This section summarizes the current results.

### 5.1 Dataset Layers

| Layer | Cases | Role |
|---|---:|---|
| Controlled generated APKs | 72 | Known ground truth for matcher mechanics across clear, R8, and multidex/multi-library categories. |
| Clean source-validated real APKs | 5 | Strong exact-version real APK evidence. |
| Partial source-validated real APKs | 97 | Hard APK families with useful partial results. |
| Source-linked blocked APKs | 0 | No current blocked rows remain; future rows stay here until dependency-tree and source-validation gates pass. |
| Limitation/boundary cases | 4 | Native/hidden-code boundaries, excluded from exact-version accuracy. |

### 5.2 Main Metric

For real APKs, the project uses emitted Maven version confirmation rate:

```text
confirmed emitted Maven versions / checked emitted Maven versions
```

This is not full dependency recall. It asks whether the Maven components emitted by the tool are confirmed by the source dependency tree.

### 5.3 Current Results

| Dataset slice | Cases | Checked emitted versions | Confirmed | Mismatches | Missing/nuance | Rate |
|---|---:|---:|---:|---:|---:|---:|
| Controlled APKs | 72 | 84 | 84 | 0 | 0 | 100.0% |
| Clean source-validated real APKs | 5 | 47 | 47 | 0 | 0 | 100.0% |
| Partial source-validated real APKs | 97 | 1790 | 880 | 636 | 274 | 49.2% |
| All source-validated real APKs | 102 | 1837 | 927 | 636 | 274 | 50.5% |

The clean cases show that the MVP can produce exact source-confirmed versions when reference coverage and bytecode evidence are strong. The partial cases are the more important realism test: they show that the tool remains useful on modern AndroidX/Kotlin, R8/minified, older-dependency, native-heavy media, large-tree, and security/email apps while exposing unresolved version ties.

### 5.4 Vulnerability Demonstration

The vulnerability workflow is demonstrated with:

| Case | Result |
|---|---|
| Calibrated F-Droid real APK | 0 OSV vulnerabilities on source-confirmed emitted components. |
| Controlled vulnerable Jackson Databind fixture | 3 confirmed HIGH advisories: `CVE-2020-36518`, `CVE-2022-42003`, `CVE-2022-42004`. |

Real-APK OSV findings are triaged against source-validation evidence in `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md`. The current triage contains 8 advisories across 6 vulnerable component rows: 1 source-confirmed advisory, 6 source-version-mismatch advisories, and 1 report-only advisory. Only the source-confirmed row should be described as source-validated vulnerability evidence; the rest are potential findings caused by partial version recovery or blocked validation.

The report generator now supports the same rule directly through `generate-report --source-validation-json`. When this option is used, OSV JSON, Markdown, and HTML output include source-validation labels and downgrade contradicted source-version rows to potential findings. The regenerated OsmAnd report is the concrete proof: its Jackson/Gson OSV advisories are shown as `potential` with `source-version-mismatch` rather than as confirmed vulnerabilities.

## 6. Discussion

The project shows that useful APK-to-SBOM recovery is possible without claiming perfect accuracy. The strongest behavior appears when the correct source-used version exists in the calibrated reference database and version-specific evidence is visible in bytecode. The hardest behavior appears when adjacent AndroidX/Kotlin versions are feature-equivalent after compilation or when the reference database lacks the exact source-used version.

Several experiments improved individual APKs but regressed others. This is why the final MVP keeps risky ties visible instead of forcing them. This design choice makes the report less cosmetically perfect, but more scientifically credible.

## 7. Limitations

The MVP has several explicit limitations:

- The real APK dataset is still smaller than the long-term dataset plan.
- Source dependency trees validate resolved Maven dependencies, not necessarily every bytecode path after shrinking.
- Exact version recovery depends on calibrated reference coverage.
- Native `.so` files are hash-only components; native package/version identification is not solved.
- Packed, encrypted, hidden-DEX, and dynamic-loading cases are risk-labeled rather than fully recovered.
- K-9 / Thunderbird Android is now source-validated partial after the plugin-lite runtime-graph rescue; Jitsi Meet is also source-validated partial, while its React Native/WebRTC native files remain hash-only boundary evidence.
- Optional scanner validation is now reproducible for CycloneDX CLI, Trivy, and Grype in Docker. `docs/evaluation/EXTERNAL_SCANNER_VALIDATION.md` records 6/6 successful Grype/Trivy runs and 6/6 successful CycloneDX schema-validation runs across clean, vulnerable, and partial SBOM targets; scanner results are comparison evidence, while source-validation-aware OSV labels remain the authority for real-APK vulnerability claims.

## 8. Conclusion

This PFE implements a working APK-to-SBOM MVP that turns compiled Android APK evidence into CycloneDX SBOMs and vulnerability lookup results. Its main contribution is not perfect matching. Its contribution is an evidence-based workflow that combines static Android library detection methods with SBOM generation, version confidence, source validation, and transparent limitation reporting.

The current evaluation supports the tool as a credible MVP: exact on controlled and clean source-validated cases, useful but explicitly partial on harder real APK families, and honest about native, hidden-code, and blocked validation boundaries.

## 9. Next Work

Near-term:

1. Convert the assembled report into the final university template.
2. Add figures from the architecture diagram, evaluation tables, report screenshots, CVE demo, and v2 package table.
3. Use `docs/thesis/FINAL_REPORT_READINESS_PACKAGE.md` for final wording and figure placement.
4. Rehearse the defense using `docs/evaluation/FINAL_DEMO_CHECKLIST.md`.

Longer-term:

1. Improve matcher recall for source-version constrained gaps that already exist in the DB.
2. Continue bounded reference growth for the remaining missing-reference candidates.
3. Add more framework families such as Flutter, Unity, and additional protected/native-heavy samples.
4. Keep optional scanner integration regenerated when scanner versions or selected SBOM targets change.

## Appendix Pointers

| Artifact | Path |
|---|---|
| Assembled final report draft | `docs/thesis/PFE_FINAL_REPORT_ASSEMBLED.md` |
| Thesis artifact index | `docs/thesis/THESIS_ARTIFACT_INDEX.md` |
| Paper-to-implementation traceability | `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md` |
| Paper-backed improvement notes | `docs/thesis/PAPER_BACKED_MVP_IMPROVEMENT_NOTES.md` |
| Evaluation chapter prose | `docs/evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md` |
| Thesis tables | `docs/evaluation/THESIS_EVALUATION_TABLES.md` |
| APK type evaluation | `docs/evaluation/APK_TYPE_EVALUATION.md` |
| Dataset design | `docs/evaluation/DATASET_DESIGN.md` |
| Coverage matrix | `docs/evaluation/DATASET_COVERAGE_MATRIX.md` |
| Supervisor demo/runbook | `docs/dev/RUNBOOK.md` |
| Codebase audit | `docs/evaluation/CODEBASE_AUDIT_AND_SUPERVISOR_BRIEF.md` |
| Architecture | `docs/architecture/MVP_ARCHITECTURE.md` |
| Evidence map | `docs/research/EVIDENCE_MAP.md` |
