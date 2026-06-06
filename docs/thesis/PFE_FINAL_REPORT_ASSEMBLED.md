# Evidence-Based SBOM Recovery from Compiled Android APKs

Hybrid Static Library Version Detection and Vulnerability Lookup for APK-Only Analysis

## Report Status

This is the assembled thesis/report draft. It combines the current report draft, evaluation chapter, traceability matrix, and artifact index into one university-ready structure. Replace the cover-page placeholders with the university template details before final submission.

## Cover Page Placeholders

| Field | Value |
|---|---|
| University | TODO |
| Faculty / Department | TODO |
| Program | TODO |
| Project type | Final-year project / PFE |
| Student | TODO |
| Supervisor | TODO |
| Academic year | TODO |
| Repository | `C:\Users\PC CABA DZ\Documents\pfe-final` |

## Abstract

Software Bills of Materials are increasingly used to identify vulnerable dependencies, but most SBOM generation tools rely on source code, package manager metadata, build manifests, or dependency lock files. In Android security-audit scenarios, the available artifact may be only a compiled APK. Recovering an SBOM from an APK is difficult because third-party libraries are embedded into DEX bytecode, Maven coordinates and versions are usually absent, and optimizers such as ProGuard and R8 may rename, shrink, inline, or remove evidence.

This project implements a static APK-to-SBOM MVP that extracts DEX, manifest, resource, and native-file evidence from compiled Android APKs; compares bytecode features against a Maven reference database; estimates library identities and versions with confidence labels; emits CycloneDX SBOMs; and queries OSV for vulnerability information. The matcher combines package, class, method, opcode, class-dependency-graph, string-literal, Maven metadata, API-reference, and optional opcode-trigram evidence. It deliberately separates library identity confidence from version confidence and reports ambiguous nearby versions instead of forcing exact claims when evidence is weak.

The evaluation is organized by APK family rather than by a single perfect-looking score. The MVP confirms 84/84 expected Maven versions across 72 controlled fixtures, 47/47 emitted Maven versions across 5 clean source-validated real APKs, and 864/1755 emitted Maven versions across 95 harder source-validated real APKs. Overall, the current source-validated real APK set reaches a 911/1802 emitted Maven version confirmation rate. Blocked and limitation cases are kept visible but excluded from accuracy metrics. The result is a practical, paper-backed MVP that produces useful SBOM evidence while making uncertainty explicit.

## Keywords

Android security; APK analysis; SBOM; CycloneDX; third-party library detection; Maven; R8; obfuscation; vulnerability detection; OSV.

## Table of Contents

1. Introduction
2. State of the Art
3. Proposed Approach
4. Implementation
5. Evaluation Methodology
6. Results and Discussion
7. Limitations and Threats to Validity
8. Conclusion and Future Work
9. Appendix Pointers

## 1. Introduction

### 1.1 Context

Modern Android applications depend heavily on third-party libraries for networking, serialization, cryptography, storage, user interface components, and platform integration. These libraries can contain known vulnerabilities. A Software Bill of Materials records the components included in an application and can help developers, auditors, and security teams determine whether vulnerable dependencies are present.

Most SBOM tools work best when they have access to source code, Gradle dependency files, lock files, package manager metadata, or container/package manifests. In many Android audit situations, however, the available artifact is only the compiled APK. This APK contains DEX bytecode, resources, a manifest, and sometimes native `.so` files, but it usually does not preserve Maven coordinates or exact dependency versions.

The Android build pipeline also transforms library code. D8 converts Java/Kotlin bytecode into DEX. R8 and ProGuard can rename identifiers, remove unused code, inline methods, optimize call sites, and make nearby library versions nearly indistinguishable. Therefore, APK-to-SBOM recovery is harder than source-based SBOM generation.

### 1.2 Problem Statement

Given only a compiled Android APK, this project aims to recover useful third-party library evidence, estimate Maven library versions, generate a standard CycloneDX SBOM, and map detected components to known vulnerabilities.

The goal is not perfect recovery for every APK. The goal is a credible MVP that:

- reports exact versions when evidence is strong;
- reports likely or candidate versions when evidence is partial;
- reports ambiguous version sets when nearby versions cannot be separated safely;
- reports scope and extraction limitations when the APK falls outside the supported static-analysis model.

### 1.3 Research Questions

This project focuses on four research questions:

1. Can a static APK analysis pipeline recover exact Maven component versions on controlled APKs with known ground truth?
2. Can the same pipeline produce source-confirmed emitted Maven versions on real open-source APKs?
3. How does accuracy change across APK families such as clean apps, modern AndroidX/Kotlin apps, R8/minified apps, older dependency stacks, native-heavy apps, and hidden-code cases?
4. Can the generated SBOM support vulnerability lookup while preserving confidence and uncertainty labels?

### 1.4 Contributions

The project contributes:

1. A static APK analysis pipeline that extracts DEX, manifest, resource, and native-file evidence.
2. A Maven reference database workflow that downloads JAR/AAR artifacts, converts bytecode to DEX, and stores comparable features in SQLite.
3. A hybrid matcher that combines bytecode, graph, literal, metadata, and confidence signals for library identity and version estimation.
4. A confidence model that separates identity confidence from version confidence and exposes ambiguous nearby versions.
5. CycloneDX SBOM generation with Maven PURLs, evidence properties, native file components, and application metadata.
6. OSV vulnerability lookup with confidence-aware confirmed versus potential findings.
7. An evaluation methodology that separates controlled, clean real, partial real, blocked, and limitation cases.

## 2. State of the Art

### 2.1 Android Third-Party Library Detection

The literature on Android third-party library detection shows that no single feature family is sufficient. Package names are useful but fragile. Reference profiles help with exact versions but depend on coverage. Graph and structural features improve robustness but can fail under shrinking, inlining, or partial inclusion. Recent benchmark work also shows that earlier reported results can be optimistic when evaluations exclude realistic R8 and modern AndroidX/Kotlin cases.

This project adapts the practical lessons from the state of the art:

| State-of-the-art lesson | MVP adaptation |
|---|---|
| Package names alone are fragile. | Treat package evidence as weak and combine it with structural evidence. |
| Reference profiles are needed for version recovery. | Build calibrated Maven reference databases. |
| Graph/opcode features help under obfuscation. | Use class dependency graphs, opcode features, and version-unique evidence. |
| Exact version detection is harder than library identity detection. | Separate identity confidence from version confidence. |
| Adjacent versions can be almost indistinguishable. | Report ambiguity instead of forcing unsupported exact versions. |
| R8/shrinking must be evaluated directly. | Evaluate controlled R8 fixtures and real partial APK families. |
| SBOM output needs standard identifiers. | Emit CycloneDX with Maven PURLs and evidence properties. |
| Vulnerability matching depends on version certainty. | Classify low-confidence findings as potential rather than confirmed. |

### 2.2 Paper-to-Implementation Traceability

The MVP is deliberately traceable to the papers and tools gathered during the state of the art:

| MVP decision | Paper/tool basis |
|---|---|
| Maven reference DB and version comparison | LibScout, ATVHunter, SAD, LibMD, LibScan |
| Class dependency and structural matching | LibPecker, LibID, LibScan, SAD, LibMD |
| Literal and version-unique tie-breaking | SAD, ATVHunter |
| Confidence and version ambiguity | SAD, LibMD, TPL-Benchmark, ObfDetector |
| R8-aware evaluation and limitation reporting | LibHunter, LibAttention, ObfDetector, TPL-Benchmark |
| CycloneDX/PURL/OSV workflow | LibMD goal, CISA SBOM guidance, CycloneDX, PURL, OSV, Syft/cdxgen-style tooling |
| Native/hash-only boundary reporting | LibRARIAN/DroidNative motivation, CycloneDX file components |

The detailed traceability matrix is maintained in `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`. It should be used as an appendix source for defense questions such as "Which paper justifies this feature?" or "Why did you not force exact versions?"

### 2.3 Positioning

The MVP is not a clone of a single academic detector. It is a practical hybrid pipeline that adapts the strongest ideas from several tools into an end-to-end SBOM workflow:

```text
APK evidence -> reference matching -> confidence-aware version decision -> CycloneDX SBOM -> OSV vulnerability lookup
```

The most important design choice is transparency. The tool should not remove difficult APKs from the evaluation to look perfect. It should expose where it works, where it partially works, and where static evidence is insufficient.

## 3. Proposed Approach

### 3.1 Pipeline Overview

The MVP is a static APK-to-SBOM pipeline:

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

### 3.2 APK Extraction

The extraction layer reads APK archives, discovers standard and nonstandard DEX files, collects manifest/application metadata, extracts resources and strings, and records native `.so` files with hashes, ABI, path, and size. It also raises risk indicators for cases such as tiny primary DEX files, nonstandard DEX paths, protector-like asset names, and opaque payloads.

Native files are represented as hash-only SBOM file components. The MVP does not claim native package or native version identification.

### 3.3 Reference Database

The reference database contains curated Maven coordinates and versions. The workflow downloads JAR/AAR artifacts, handles packaging explicitly, converts bytecode to DEX with D8 when needed, extracts comparable features, and stores them in SQLite.

The project uses several reference DB modes:

| DB type | Purpose |
|---|---|
| Focused DB | Small controlled library set for early development. |
| Expanded DB | Broad latest-version identity stress testing. |
| Calibrated DB | Source-used versions and guarded promotions for evaluation. |
| Experiment DBs | Temporary API-reference, opcode-trigram, and app-specific calibration tests. |

### 3.4 Feature Extraction and Matching

The matcher combines several evidence families:

| Evidence family | Purpose |
|---|---|
| Package/class/method overlap | Candidate generation and identity evidence. |
| Opcode histograms | Bytecode similarity. |
| Class dependency graph | Structural similarity under some obfuscation. |
| String literals and version-unique features | Version tie-breaking when versions differ in literals or changed classes. |
| Maven POM dependencies | Conservative dependency-coherence support. |
| API/member references | Optional experimental signal, disabled by default. |
| Opcode tri-grams | Optional experimental sequence signal, disabled globally after regression tests. |

The official matcher is conservative. Generic "newer version wins" logic is rejected because experiments showed that it can fix one APK and regress another.

### 3.5 Confidence and Ambiguity

The MVP separates library identity confidence from version confidence. This matters because a library can be present even when the exact version is uncertain.

The report can output:

- exact or high-confidence version evidence;
- likely or candidate versions;
- ambiguous nearby versions;
- uncertain results when static evidence is too weak.

Version-band ambiguity is now first-class output. When nearby versions are feature-equivalent or within a close score gap without matched version-unique APK evidence, the tool keeps the selected candidate but also exports the competing versions as structured `ambiguous_versions` data and as the CycloneDX property `apk-sbom:mvp:ambiguous-versions`.

### 3.6 SBOM and Vulnerability Workflow

The tool emits CycloneDX JSON with Maven PURLs, component versions, confidence and evidence properties, application metadata, and native file components. OSV is used for vulnerability lookup.

Findings are confidence-aware. A high-confidence exact version can support a confirmed vulnerability result. Low-confidence or ambiguous version evidence should be treated as potential until source validation or stronger evidence confirms it.

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
| Vulnerability lookup | `src/apk_sbom/osv.py`, `src/apk_sbom/vulnerability.py` |
| Report generation | `src/apk_sbom/report.py` |
| Evaluation scripts | `scripts/build_apk_type_evaluation.py`, `scripts/build_thesis_evaluation_tables.py`, `scripts/build_thesis_artifact_index.py` |

The implementation avoids hardcoded perfect results. Reports are generated from matcher outputs, and source validation compares emitted SBOM components against resolved dependency trees when available.

### 4.1 Guarded Improvement Policy

Several experiments improved one target app but regressed other apps. Therefore, the MVP uses a guarded improvement policy:

```text
try improvement -> run current-control matrix -> promote only if no harmful regression -> otherwise keep as experiment evidence
```

Examples:

- Nextcloud source-used-version experiments improved Nextcloud but regressed other cases, so only the safe subset was promoted.
- Activity `1.9.2` and ViewPager2 `1.1.0-beta02` were not globally promoted because isolated tests caused regressions.
- API-reference and opcode tri-gram signals were implemented but kept disabled by default because global weights did not improve the validation matrix.

This policy is important for the thesis because it shows that the tool was not tuned only to produce a cleaner-looking result.

## 5. Evaluation Methodology

### 5.1 Dataset Layers

The evaluation is organized by dataset layer:

| Layer | Cases | Role |
|---|---:|---|
| Controlled generated APKs | 72 | Known ground truth for matcher mechanics across clear, R8, and multidex/multi-library categories. |
| Clean source-validated real APKs | 5 | Strong exact-version real APK evidence. |
| Partial source-validated real APKs | 83 | Hard APK families with useful partial results. |
| Source-linked blocked APKs | 3 | Diversity evidence is tracked separately; these rows have source/report evidence but no runtime dependency tree yet. |
| Limitation/boundary cases | 4 | Native/hidden-code boundaries, excluded from exact Maven-version accuracy. |

This split is intentional. A single global score would hide the main research result: APK-to-SBOM quality depends on APK family, reference coverage, R8 behavior, dependency era, and static evidence quality.

### 5.2 Metrics

For controlled APKs, the main metric is exact expected-version confirmation:

```text
correct expected Maven component versions / expected Maven component versions
```

For real APKs, the main metric is emitted Maven version confirmation rate:

```text
confirmed emitted Maven versions / checked emitted Maven versions
```

This is not full dependency recall. It asks whether the Maven components emitted by the MVP are confirmed by the source dependency tree. It does not claim that every Gradle-resolved dependency must appear in APK bytecode or be recovered by the static matcher.

### 5.3 Validation Sources

The validation uses:

- controlled fixture ground truth;
- source-resolved Gradle dependency trees for real open-source APKs;
- proof bundles with APK hashes, source hashes, F-Droid metadata, reports, and validation outputs;
- boundary cases for native-heavy and hidden-code behavior.

K-9 / Thunderbird Android is now source-validated partial after a validation-only plugin-lite/runtime-graph source copy generated its resolved runtime dependency tree.

## 6. Results and Discussion

### 6.1 Main Results

| Dataset slice | Cases | Checked emitted versions | Confirmed | Mismatches | Missing/nuance | Rate |
|---|---:|---:|---:|---:|---:|---:|
| Controlled APKs | 72 | 84 | 84 | 0 | 0 | 100.0% |
| Clean source-validated real APKs | 5 | 47 | 47 | 0 | 0 | 100.0% |
| Partial source-validated real APKs | 95 | 1755 | 864 | 617 | 274 | 49.2% |
| All source-validated real APKs | 100 | 1802 | 911 | 617 | 274 | 50.6% |

The controlled fixtures confirm that the implementation can recover exact versions when the dependency is represented in the reference database and bytecode evidence is not ambiguous. This validates the pipeline mechanics across clear version-band, controlled obfuscation, R8 rename, R8 shrink, multidex, and multi-library cases.

The clean source-validated real APKs confirm 47/47 emitted Maven versions across F-Droid, OpenTracks, Tusky, Daily Dozen, and QuickDic. This is the strongest exact-version evidence, but it should not be used alone as the whole result because Tusky, Daily Dozen, and QuickDic are sparse and clean cases do not represent all APK families.

The partial source-validated real APKs confirm 864/1755 emitted Maven versions across 95 harder apps. These are useful partial results, not failures. They show that the tool can recover meaningful SBOM evidence while exposing version-band ties, artifact-family ambiguity, native hash-only boundaries, and reference-coverage limits.

Across all 100 source-validated real APKs, the MVP confirms 911/1802 emitted Maven versions, a 50.6% emitted Maven version confirmation rate. This number should always be reported with the clean/partial split.

### 6.2 Per-APK Interpretation

| APK family | Interpretation |
|---|---|
| F-Droid, OpenTracks, Tusky, Daily Dozen, QuickDic | Clean source-validated evidence. F-Droid and OpenTracks are richer cases; Tusky, Daily Dozen, and QuickDic are clean but sparse. |
| NewPipe, AntennaPod, KDE Connect, Wikipedia, Conversations, Aegis, FairEmail, Nextcloud | Modern AndroidX/Kotlin, R8/minified, security/email, and large-tree cases. These show useful identity recovery but remaining exact-version ambiguity. |
| Markor | Older-dependency profile. App-specific source-version calibration can fix it, but global promotion regresses other cases. |
| K-9 / Thunderbird Android | Source-validated partial after a plugin-lite included-build/runtime-graph rescue. Useful proof and report evidence, with remaining version mismatches kept visible. |
| Jitsi Meet | React Native/native-heavy source-validated partial case. Validates 5/7 emitted Maven versions, while React Native/WebRTC/Hermes native files remain hash-only boundary evidence. |
| Organic Maps, Termux, hidden-DEX fixture, Simplify obfuscated sample | Native-heavy, hidden-code, and obfuscation boundary cases. Native files are reported as hashes, and unsupported hidden/nonstandard code evidence is risk-labeled instead of converted into Maven claims. |
| Hidden DEX fixture | Static-analysis boundary case. Correct behavior is to raise risk and avoid false Maven claims. |

### 6.3 Vulnerability Demonstration

The vulnerability workflow is demonstrated by two cases:

| Case | Result |
|---|---|
| Calibrated F-Droid real APK | 0 OSV vulnerabilities on source-confirmed emitted Maven components. |
| Controlled vulnerable Jackson Databind fixture | 3 confirmed HIGH advisories: `CVE-2020-36518`, `CVE-2022-42003`, and `CVE-2022-42004`. |

The key point is not only that vulnerabilities can be queried. The key point is that the vulnerability result is linked to version confidence. Ambiguous or low-confidence versions should be treated as potential findings.

The same rule is applied to real APKs in `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md`. The current triage records 8 advisories across 6 vulnerable component rows: 1 source-confirmed advisory, 6 source-version-mismatch advisories, and 1 report-only advisory. This prevents partial cases such as VLC, OsmAnd, and Jitsi from being presented as stronger vulnerability evidence than their version validation supports.

This is also implemented in the report generator. With `generate-report --source-validation-json`, the OSV JSON, Markdown report, and HTML report include source-validation labels. In the regenerated OsmAnd report, the Jackson/Gson advisories are downgraded to `potential` because source validation resolves different versions.

### 6.4 Discussion

The results support the main design choice: combine static bytecode features with reference evidence, confidence labels, and explicit scope boundaries. The MVP is strongest when the reference database contains the source-used version and when bytecode features distinguish versions clearly. It remains useful but less exact when nearby AndroidX/Kotlin versions share almost identical bytecode evidence.

The partial cases are important. Hiding them would make the tool look cleaner, but it would weaken the research. Recent state-of-the-art work already shows that Android library detection and version identification degrade under realistic conditions. Reporting partial results by APK family makes the evaluation more honest and more useful.

The experiments also show why generic recency rules are unsafe. Several versions improved one app but regressed others. Therefore, the MVP preserves risky ties as ambiguity unless there is independent evidence such as version-unique features, dependency coherence, app-era support, or source validation.

## 7. Limitations and Threats to Validity

### 7.1 Limitations

The MVP has the following limitations:

- The real APK dataset is still smaller than the long-term target.
- Source dependency trees validate resolved Maven dependencies, not necessarily every bytecode path after shrinking.
- Exact version recovery depends on calibrated reference coverage.
- Some adjacent AndroidX/Kotlin versions are nearly indistinguishable after compilation.
- Native `.so` files are hash-only components; native package/version identification is not solved.
- Packed, encrypted, hidden-DEX, and dynamic-loading cases are risk-labeled rather than fully recovered.
- K-9 / Thunderbird Android is now source-validated partial after the plugin-lite runtime-graph rescue; Jitsi Meet is also source-validated partial, while its React Native/WebRTC native files remain hash-only boundary evidence.
- External scanner validation is optional but now reproducible for CycloneDX CLI, Trivy, and Grype in Docker; `docs/evaluation/EXTERNAL_SCANNER_VALIDATION.md` records 6/6 successful Grype/Trivy runs and 6/6 successful CycloneDX schema-validation runs across clean, vulnerable, and partial SBOM targets. Source-validation-aware OSV labels remain the authority for real-APK vulnerability claims.

### 7.2 Threats to Validity

The controlled fixtures validate matcher mechanics but do not represent the full diversity of real-world Android apps. The real source-validated dataset is more realistic but still limited in size. Source dependency trees are strong evidence, but Gradle may resolve dependencies that are removed, transformed, shaded, or not packaged into the final APK. Reference database coverage can also bias results: if a source-used version is absent, the matcher may select a nearby version or report ambiguity.

These threats are mitigated by separating controlled, clean real, partial real, blocked, and limitation cases. The thesis should present this split as part of the contribution, because it prevents overstating the MVP's capability.

## 8. Conclusion and Future Work

This PFE implements a working APK-to-SBOM MVP that turns compiled Android APK evidence into CycloneDX SBOMs and vulnerability lookup results. Its main contribution is not perfect matching. Its contribution is an evidence-based workflow that combines Android library detection research with SBOM generation, source validation, confidence-aware version reporting, and transparent limitation handling.

The current evaluation supports the MVP as credible: exact on controlled and clean source-validated cases, useful but explicitly partial on harder real APK families, and honest about native, hidden-code, and blocked validation boundaries.

Future work should:

1. Scale the source-validated real APK set toward the planned 50 cases.
2. Add more framework families such as Flutter, React Native, Unity, and additional native-heavy apps.
3. Investigate scoped per-coordinate rerankers for AndroidX version-band ties.
4. Explore stronger multi-scale graph or basic-block fusion inspired by LibMD.
5. Consider ML-assisted identity detection inspired by LibAttention only as a future layer, not as a replacement for explainable version evidence.
6. Regenerate external scanner validation when scanner versions or selected SBOM targets change.

## 9. Appendix Pointers

| Artifact | Use |
|---|---|
| `docs/thesis/THESIS_ARTIFACT_INDEX.md` | Main map from claims to evidence files. |
| `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md` | Paper/tool basis for each implemented feature and policy. |
| `docs/thesis/PRESENTATION_DECK_SCRIPT.md` | Slide-ready defense script with claims, proof objects, and speaker notes. |
| `docs/thesis/PAPER_BACKED_MVP_IMPROVEMENT_NOTES.md` | Current cons, improvement plan, and thesis framing. |
| `docs/evaluation/THESIS_EVALUATION_TABLES.md` | Thesis-ready numbers and claim wording. |
| `docs/evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md` | Expanded evaluation prose. |
| `docs/evaluation/APK_TYPE_EVALUATION.md` | APK family split and case interpretation. |
| `docs/evaluation/VERSION_BAND_TIE_EVIDENCE.md` | Version ambiguity and unsafe-promotion evidence. |
| `docs/dev/RUNBOOK.md` | Supervisor demo commands and expected outputs. |
| `docs/architecture/MVP_ARCHITECTURE.md` | Architecture diagram and module map. |
| `docs/research/EVIDENCE_MAP.md` | Short mapping from papers/tools to architecture choices. |

## Writing Guardrails

- Use "emitted Maven version confirmation rate" for real APK validation.
- Do not call the real-APK metric full dependency recall.
- Always show clean and partial real APK rows separately.
- Explain partial APKs as useful hard-case evidence, not total failures.
- Keep native-heavy, hidden-DEX, scanner-tool, and K-9 validation-copy caveats visible.
- Describe ambiguity as a strength of the report, because it prevents unsupported exact-version claims.
