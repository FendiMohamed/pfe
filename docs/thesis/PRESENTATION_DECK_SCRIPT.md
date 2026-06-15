# Presentation Deck Script

This is the slide-ready defense script for the APK-to-SBOM MVP. It expands `docs/thesis/PRESENTATION_OUTLINE.md` into concrete slide claims, visible content, proof objects, and speaker notes.

Recommended length: 12 slides, 10-15 minutes, plus demo and questions.

Editable generated deck: `outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/output/apk-sbom-defense-deck.pptx`.

Rendered QA contact sheet: `outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/preview/contact-sheet.png`.

Current deck refresh: regenerated on 2026-06-15 with the final v2 source-known lane, transparency export, updated QA scorecard, and the guardrail that v2 is not APK-only production accuracy.

## Slide 1: Title

**Slide claim:** This project recovers useful SBOM evidence from compiled Android APKs.

**On-slide content:**

```text
Evidence-Based SBOM Recovery from Compiled Android APKs
Hybrid static library version detection and vulnerability lookup
```

**Proof object:** Small pipeline strip:

```text
APK -> Evidence -> Maven version candidates -> CycloneDX SBOM -> OSV results
```

**Speaker notes:**

The project starts from a realistic audit situation: we may only have an APK, not the source code or Gradle files. The goal is to recover third-party library and version evidence, generate a standard SBOM, and connect that SBOM to vulnerability lookup.

**Defense hook:** This is not a source-based SBOM generator. It is an APK reverse-SBOM MVP.

## Slide 2: Problem

**Slide claim:** Android APKs hide the dependency information that SBOM tools usually need.

**On-slide content:**

- Source SBOM tools use Gradle files, lock files, or package metadata.
- APKs contain compiled DEX, resources, manifest data, and native files.
- Maven coordinates and versions are usually absent.
- R8/ProGuard can rename, shrink, inline, and remove evidence.

**Proof object:** Problem diagram:

```text
Source project: Gradle metadata visible
Compiled APK: dependency metadata missing, bytecode transformed
```

**Speaker notes:**

In source code, dependency versions are often explicit. In an APK, the dependencies are mixed into bytecode. This is why the problem is harder than simply scanning a package manifest.

**Likely question:** Why not use normal SBOM tools?

**Answer:** Normal tools are still useful when source metadata exists. Here the input is only a compiled APK, so the tool must infer library identity and versions from static APK evidence.

## Slide 3: State-of-the-Art Gap

**Slide claim:** Existing Android library detectors are useful, but exact version recovery remains fragile under realistic APK conditions.

**On-slide content:**

| Lesson | Evidence from state of the art |
|---|---|
| Package names are fragile. | LibScout, LibRadar, Systematic Assessment |
| Graph/opcode features help. | LibPecker, LibID, LibScan, ATVHunter, SAD |
| R8 changes the game. | LibHunter, LibAttention, ObfDetector |
| Exact versions are harder than identity. | SAD, TPL-Benchmark, LibMD |
| SBOM output is still rare. | LibMD is the closest SBOM-oriented paper |

**Proof object:** Reference `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`.

**Speaker notes:**

The state of the art does not say that perfect matching is realistic. It says that a strong tool must combine multiple signals and evaluate limitations honestly. This project follows that lesson.

**Defense hook:** Our improvements are paper-backed: reference DB, graph/opcode/literal evidence, confidence labels, ambiguity reporting, and category-based evaluation.

## Slide 4: Project Goal

**Slide claim:** The MVP gives strong claims when evidence is strong and transparent uncertainty when evidence is weak.

**On-slide content:**

```text
Input: compiled APK
Output:
- detected Maven components
- version confidence
- ambiguous version sets when needed
- CycloneDX SBOM
- OSV vulnerability results
```

**Speaker notes:**

The goal is not to force a perfect score. The goal is a useful security artifact: an SBOM with evidence, confidence, and limitations. If the version evidence is ambiguous, the tool should say that.

**Likely question:** Is ambiguity a weakness?

**Answer:** It is a limitation of the evidence, but reporting it is a strength. It prevents false certainty and makes vulnerability interpretation safer.

## Slide 5: Architecture

**Slide claim:** The MVP is an end-to-end static APK-to-SBOM pipeline.

**On-slide content:**

```text
APK
-> extraction
-> DEX analysis
-> Maven reference DB
-> hybrid matching
-> confidence scoring
-> CycloneDX SBOM
-> OSV vulnerability lookup
-> report
```

**Proof object:** Use architecture diagram from `docs/architecture/MVP_ARCHITECTURE.md`.

**Speaker notes:**

The architecture connects reverse engineering, reference matching, SBOM generation, and vulnerability lookup. The key contribution is not only detecting a library; it is carrying the evidence through to a standard SBOM and report.

## Slide 6: Evidence Signals

**Slide claim:** The matcher combines complementary evidence instead of trusting one fragile signal.

**On-slide content:**

| Signal | Purpose |
|---|---|
| Package/class/method overlap | Candidate generation and identity |
| Opcode histograms | Bytecode similarity |
| Class dependency graph | Structural evidence |
| Literals/version-unique evidence | Version tie-breaking |
| Maven POM metadata | Conservative dependency coherence |
| API refs/opcode tri-grams | Experimental, disabled by default |

**Speaker notes:**

Each signal has strengths and weaknesses. Package evidence is useful but fragile. Graph and opcode evidence can survive some obfuscation. Literal and version-unique evidence helps with adjacent versions. POM metadata is useful only when independently supported by APK-side evidence.

**Defense hook:** API-reference and opcode tri-gram signals were implemented and tested, but kept disabled because they did not safely improve the current validation matrix.

## Slide 7: Confidence and Ambiguity

**Slide claim:** The MVP separates library identity confidence from exact version confidence.

**On-slide content:**

```text
Library identity:
  Is this component present?

Version confidence:
  Is this exact version supported?

Ambiguous versions:
  Which nearby versions are also plausible?
```

**Proof object:** Mention CycloneDX properties:

```text
apk-sbom:mvp:identity-confidence
apk-sbom:mvp:version-confidence
apk-sbom:mvp:ambiguous-versions
```

**Speaker notes:**

A component can be real even if the exact version is uncertain. This matters for vulnerability analysis because an incorrect exact version can create a wrong vulnerability conclusion.

**Likely question:** Why not always choose the newest near version?

**Answer:** We tested that idea. It fixed some cases but regressed others, so the safe policy is to report the ambiguity unless there is independent evidence.

## Slide 8: Evaluation Design

**Slide claim:** The evaluation is organized by APK family, not by hiding hard cases.

**On-slide content:**

| Layer | Role |
|---|---|
| Controlled APKs | Known ground truth |
| Clean source-validated real APKs | Strong exact-version evidence |
| Partial source-validated real APKs | Realistic hard cases |
| Source-linked blocked APKs | Proof exists, metric excluded |
| Limitation cases | Native/hidden-code boundaries |

**Speaker notes:**

This split is essential. A single global score can hide why the tool succeeds or fails. APK type matters: R8, multidex, AndroidX/Kotlin, native code, older dependencies, and build-system blockers all affect evaluation.

**Defense hook:** Partial cases are not thrown away. They are part of the research result.

## Slide 9: Main Results

**Slide claim:** The MVP is exact on controlled and clean cases, and useful but partial on harder real APKs.

**On-slide content:**

| Dataset slice | Result |
|---|---:|
| Controlled APKs | 84/84 expected versions |
| Clean source-validated real APKs | 47/47 emitted versions |
| Partial source-validated real APKs | 880/1790 emitted versions |
| All source-validated real APKs | 927/1837 emitted versions |
| Final v2 source-known lane | 6772/6772 emitted rows, 0 wrong versions |

**Required phrase:** emitted Maven version confirmation rate.

**Speaker notes:**

The controlled set validates the mechanics. Clean real APKs show that source-confirmed emitted versions are possible. Partial real APKs show realistic behavior on harder APK families. The overall 927/1837 number is useful, but it must be reported together with the clean/partial split. The final v2 source-known lane is a separate upper-bound result: it reruns 106 source-tree APK cases against exact source coordinate+version slices and confirms all 6772 emitted rows with zero wrong-version emissions.

**Do not say:** full dependency recall.

**Do not say:** the v2 lane is APK-only production accuracy.

## Slide 10: What Mixed Results Mean

**Slide claim:** Mixed results are evidence about APK types, not a total failure.

**On-slide content:**

| Case family | Interpretation |
|---|---|
| F-Droid, OpenTracks, Tusky | Clean source-validated evidence |
| NewPipe, AntennaPod, KDE, Wikipedia, Conversations, Aegis, FairEmail, Nextcloud | Useful partial evidence with AndroidX/Kotlin/version-band ambiguity |
| Markor | Older-dependency drift; app-specific calibration can regress others |
| K-9 / Thunderbird Android | Source-validated partial after a plugin-lite included-build rescue |
| Organic Maps, Termux, hidden DEX fixture | Boundary and limitation evidence |

**Speaker notes:**

This is the point where we defend the scientific honesty of the evaluation. If we only showed clean cases, the tool would look stronger but the thesis would be weaker. The partial cases show exactly where future work should focus.

## Slide 11: SBOM and CVE Demonstration

**Slide claim:** The MVP produces standard SBOM output and confidence-aware vulnerability results.

**On-slide content:**

| Demo | Result |
|---|---|
| Calibrated F-Droid | 23/23 source-confirmed emitted Maven versions, OSV 0 |
| Vulnerable Jackson fixture | 3 confirmed HIGH advisories |
| OsmAnd source-aware report | 4 OSV advisories, all potential due source-version mismatch |
| Real APK OSV triage | 1 source-confirmed advisory; remaining real findings are mismatch/report-only |

**Proof object:** Show `report.html`, `sbom.cdx.json`, the OSV section from `docs/dev/RUNBOOK.md`, and `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md`.

**Speaker notes:**

The SBOM is CycloneDX JSON with Maven PURLs and evidence properties. OSV results are tied to version confidence and source validation when available. Strong exact evidence can produce a confirmed finding; source-version mismatches and report-only real APK findings stay potential until validation supports them.

## Slide 12: Limitations and Next Work

**Slide claim:** The MVP is credible because it exposes scope boundaries and next improvements.

**On-slide content:**

Limitations:

- reference DB coverage affects exact version recovery;
- adjacent AndroidX/Kotlin versions can be indistinguishable;
- native `.so` files are hash-only;
- hidden DEX/dynamic loading is risk-labeled, not solved;
- K-9 is source-validated partial after a validation-only plugin-lite rescue;
- external scanner validation now runs with Trivy and Grype; scanner output is comparison evidence, not the final source-validated vulnerability authority.

Next work:

- scale source-validated real APKs;
- add more framework families;
- investigate scoped per-coordinate rerankers;
- explore stronger multi-scale graph fusion;
- add Trivy/Grype validation when available.

**Speaker notes:**

The conclusion is not that the MVP is perfect. It is that the MVP is useful, measurable, and transparent about uncertainty. That is stronger than a polished score that hides difficult APKs.

## Demo Flow

Recommended live or recorded demo:

1. Open the architecture diagram.
2. Open the clean F-Droid HTML report.
3. Open the CycloneDX SBOM and show Maven PURLs/evidence properties.
4. Open the source-validation output showing confirmed emitted versions.
5. Open the vulnerable Jackson report and show the three HIGH OSV advisories.
6. Open the thesis evaluation table and show clean/partial separation.
7. Open the final v2 package and transparency export to show the source-known upper-bound lane and remaining gap taxonomy.
8. Optional: open version-band evidence to show ambiguity reporting.

## Defense Questions And Short Answers

| Question | Short answer |
|---|---|
| Why not aim for perfect matching? | Current papers and our experiments show exact version recovery is not always possible under realistic APK conditions; the tool should improve while reporting uncertainty honestly. |
| Are partial APKs failures? | No. They are evidence about hard APK families and show where the tool is useful but not exact. |
| Why use emitted Maven version confirmation rate? | It validates whether emitted SBOM components are confirmed by source evidence without pretending to measure full dependency recall. |
| Why not force the source version in near ties? | Generic near-tie and newer-version rules caused regressions in other APKs. |
| Why keep API/opcode tri-gram signals disabled? | They were implemented and tested, but global weights did not improve metrics and opcode tri-grams regressed some controls. |
| Why is K-9 excluded? | It has APK/source/report proof, but the resolved dependency tree is still blocked, so it is not a source-validated accuracy case. |
| How is this based on the papers? | The traceability matrix maps every main MVP feature to state-of-the-art tools and papers plus implementation and evaluation artifacts. |

## Closing Statement

This project contributes a practical APK-to-SBOM MVP that combines Android third-party-library detection research with standard SBOM and vulnerability workflows. Its value is not a perfect score. Its value is an evidence-backed pipeline that produces useful component/version information, exposes uncertainty, and evaluates behavior across different APK families.
