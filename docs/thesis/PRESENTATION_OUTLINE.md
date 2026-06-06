# Presentation Outline: APK-to-SBOM MVP

Expanded slide script: `docs/thesis/PRESENTATION_DECK_SCRIPT.md`.

Editable generated deck: `outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/output/apk-sbom-defense-deck.pptx`.

Rendered QA contact sheet: `outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/preview/contact-sheet.png`.

## Slide 1: Title

Evidence-Based SBOM Recovery from Compiled Android APKs

Subtitle: Hybrid static library version detection and vulnerability lookup for APK-only analysis.

## Slide 2: Problem

Most SBOM tools work from source code, Gradle files, or package metadata. In Android audits, the available artifact may be only a compiled APK.

Key difficulty:

```text
APK bytecode does not directly contain Maven coordinates or versions.
R8/ProGuard can rename, shrink, inline, and remove evidence.
```

## Slide 3: Research Gap

State-of-the-art Android library detectors are useful but imperfect under realistic conditions.

Message to deliver:

- version-level detection is harder than library-level detection;
- modern R8 and AndroidX/Kotlin artifacts create near-version ambiguity;
- SBOM output and vulnerability mapping need standard identifiers, not only library names.

## Slide 4: Project Goal

Given a compiled APK:

```text
recover third-party library evidence
estimate Maven versions with confidence
generate CycloneDX SBOM
query vulnerabilities
report uncertainty honestly
```

Do not claim perfect matching. Claim useful, evidence-backed recovery with transparent uncertainty.

## Slide 5: Architecture

Show the pipeline:

```text
APK
-> extraction
-> DEX feature analysis
-> Maven reference DB
-> hybrid matching
-> confidence scoring
-> CycloneDX SBOM
-> OSV vulnerability lookup
-> report
```

Use the diagram from `docs/architecture/MVP_ARCHITECTURE.md`.

## Slide 6: Evidence Features

The matcher combines:

| Feature | Purpose |
|---|---|
| package/class/method overlap | identity and candidate generation |
| opcode histograms | bytecode similarity |
| class dependency graph | structural evidence |
| literals/version-unique evidence | tie-breaking |
| Maven POM metadata | conservative dependency coherence |
| API refs / opcode tri-grams | experimental signals, disabled by default |

Key point: the tool separates identity confidence from version confidence.

Paper-backed traceability:

- LibScout / ATVHunter / SAD justify reference-version comparison;
- LibPecker / LibID / LibScan / LibMD justify structural and multi-feature fusion;
- SAD / LibMD justify version tie-breaking, confidence, and ambiguity;
- LibHunter / LibAttention / TPL-Benchmark / ObfDetector justify R8-aware evaluation and honest limits;
- CycloneDX / PURL / OSV justify standard SBOM and vulnerability output.

Use `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md` for the thesis appendix or defense questions.

## Slide 7: SBOM and CVE Workflow

Output:

- CycloneDX JSON;
- Maven PURLs;
- confidence and evidence properties;
- native `.so` files as hash-only file components;
- OSV vulnerability results.

Example:

- clean F-Droid case: 0 OSV vulnerabilities;
- vulnerable Jackson fixture: 3 HIGH CVEs.

## Slide 8: Evaluation Design

Evaluation is by APK family, not a single polished score.

| Layer | Role |
|---|---|
| controlled APKs | known ground truth |
| clean source-validated real APKs | strongest exact-version evidence |
| partial source-validated real APKs | realistic hard cases |
| blocked source-linked APKs | proof exists, metric excluded |
| limitation cases | native/hidden-code boundaries |

## Slide 9: Main Results

| Dataset slice | Result |
|---|---:|
| Controlled fixtures | 84/84 confirmed across 72 fixtures |
| Clean source-validated real APKs | 47/47 confirmed |
| Partial source-validated real APKs | 880/1790 confirmed |
| All source-validated real APKs | 927/1837 confirmed |

Use the phrase: emitted Maven version confirmation rate.

Do not call it full dependency recall.

## Slide 10: What the Mixed Results Mean

Clean cases prove the pipeline can produce exact source-confirmed versions.

Partial cases are useful, not failures:

- NewPipe, AntennaPod, KDE Connect, Wikipedia, Conversations, Aegis, FairEmail, Markor, Nextcloud;
- hard families include AndroidX/Kotlin, R8/minified, old dependencies, large modern trees, and security/email apps.

The tool reports version-band and artifact-family ambiguity instead of forcing unsupported versions.

## Slide 11: Limitations

Be explicit:

- reference DB coverage controls exact version recovery;
- native `.so` versions are not identified, only hashed;
- hidden DEX/dynamic loading is detected as risk, not fully recovered;
- K-9 is source-validated partial after a validation-only plugin-lite rescue;
- scanners such as Trivy/Grype are optional and currently blocked by missing tools.

## Slide 12: Contribution and Next Work

Contribution:

```text
A working APK-to-SBOM MVP that connects Android library detection research
to CycloneDX SBOM and vulnerability workflows.
```

Next work:

- final report formatting;
- optional K-9 dependency-tree retry;
- scale real source-validated dataset;
- add more framework families;
- investigate scoped rerankers for AndroidX version-band ties.

## Demo Path

Use the supervisor demo from `docs/dev/RUNBOOK.md`.
Use the assembled final report, evidence map, traceability matrix, and artifact list from `docs/thesis/PFE_FINAL_REPORT_ASSEMBLED.md`, `docs/research/EVIDENCE_MAP.md`, `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`, and `docs/thesis/THESIS_ARTIFACT_INDEX.md` while assembling screenshots and appendix material.

Recommended demo:

1. Show the pipeline diagram.
2. Open a generated HTML report.
3. Open the CycloneDX SBOM.
4. Show clean OSV result for F-Droid.
5. Show positive OSV result for vulnerable Jackson.
6. Show evaluation table with clean/partial split.

## Speaker Notes

Important phrasing:

- "The tool is not perfect, and it does not claim to be."
- "The evaluation separates clean, partial, blocked, and limitation cases."
- "Partial version mismatch cases are useful evidence about hard APK families."
- "The metric is emitted Maven version confirmation rate, not full dependency recall."
- "The MVP prefers honest uncertainty over forced perfect-looking matches."
- "Each major improvement is traceable to a state-of-the-art lesson and to our own regression evidence."
