# Defense Presentation Guide

> The current expanded 39-slide deck has a dedicated companion at
> `docs/thesis/EXPANDED_DEFENSE_PRESENTER_COMPANION.md`. It includes the
> component-by-component evolution, design rationale, matcher algorithm,
> implementation paths, all 31 main slides, and all 8 backup slides.
>
> This file remains the shorter 13-slide rehearsal script.

Use this file with the editable deck:

`outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/output/apk-sbom-defense-deck.pptx`

Recommended duration: 12 to 15 minutes, followed by a 2 to 4 minute demo and questions.

## The Story In One Sentence

The project reconstructs third-party library and version evidence from compiled Android APKs, exports a confidence-aware CycloneDX SBOM, maps vulnerability evidence, and keeps hard R8 and missing-reference cases visible instead of hiding them.

## Numbers You Must Know

| Meaning | Number |
|---|---:|
| Controlled expected Maven versions | `84/84` |
| Normal real-APK emitted versions confirmed | `927/1837` |
| Normal emitted confirmation rate | `50.5%` |
| Clean real-APK emitted versions confirmed | `47/47` |
| Partial real-APK emitted versions confirmed | `880/1790` |
| Source-validated real APKs | `102` |
| Source-known v2 cases | `106` |
| Source-known v2 emitted rows confirmed | `6772/6772` |
| Remaining source-gap rows | `5238` |
| Explained or boundary rows | `2515` |
| Matcher-recall candidates | `2281` |
| Missing-reference candidates | `442` |
| RandomForest test macro-F1 | `0.708` |
| MVP-safe Transformer test macro-F1 | `0.882` |
| Raw-opcode Transformer test macro-F1 | `0.110` |
| Raw-opcode baseline macro-F1 | `0.128` |
| Largest local AI/R8 evidence package | `31,589` rows |

Do not try to memorize every secondary experiment count. Memorize the headline numbers and know where the detailed evidence is stored.

## Exact Wording To Use

Use:

> The normal real-APK metric is emitted Maven version confirmation, not full dependency recall.

Use:

> The v2 result is a source-version constrained upper-bound lane. It proves exact recognition when the correct source versions are known, not unconstrained APK-only production accuracy.

Use:

> AI is integrated as report-only assistance. The deterministic matcher remains responsible for selected versions, SBOM components, and vulnerability labels.

Avoid:

> The tool has 100 percent real-world accuracy.

Avoid:

> The AI detects the correct version automatically.

Avoid:

> Every dependency missing from the SBOM is a matcher failure.

## Slide-By-Slide Script

### Slide 1: Title

**Time:** 45 seconds

**Main message:** This is a reverse-SBOM problem starting from a compiled APK.

Say:

> My project starts from a compiled Android APK, where Gradle dependency metadata is no longer available. The tool extracts static evidence, matches it against a Maven reference database, exports CycloneDX, and maps vulnerability findings with explicit confidence.

Mention the three numbers only briefly:

- `927/1837` is the normal real-APK emitted-version metric.
- `84/84` validates the controlled mechanics.
- `6772/6772` is a separate source-known upper-bound lane.

### Slide 2: The Problem

**Time:** 55 seconds

**Main message:** Source SBOM tools and APK reverse-SBOM tools receive different evidence.

Explain:

- Source projects expose Gradle files, version catalogs, and resolved dependency trees.
- APKs contain mixed DEX bytecode, resources, manifests, and native files.
- R8 can rename, shrink, remove, or inline code.
- Maven coordinates and exact versions normally do not survive compilation.

### Slide 3: Research Positioning

**Time:** 60 seconds

**Main message:** The literature moved from signatures to structure and learned models, but exact R8-resistant version recovery remains difficult.

Explain:

- Gen 1 tools use package or class signatures.
- Gen 2 tools use structural and opcode evidence.
- Gen 3 work explores learned representations for R8 resilience.
- Few tools connect detection to standard SBOM and CVE output.

Do not claim that the project invented every signal. The contribution is the evidence-backed integration, evaluation, transparency, and guarded AI extension.

### Slide 4: Project Objective

**Time:** 50 seconds

**Main message:** The output is a security artifact with confidence, not a forced exact answer.

Explain:

- Input: compiled APK.
- Evidence engine: identity, version, and ambiguity.
- Outputs: CycloneDX, confidence properties, alternatives, and OSV evidence.
- Weak evidence remains uncertain or report-only.

### Slide 5: Architecture

**Time:** 70 seconds

**Main message:** The project is an end-to-end pipeline, not only a matching formula.

Walk through:

1. Extract APK content.
2. Fingerprint DEX features.
3. Retrieve Maven candidates.
4. Match using multiple scales.
5. Decide confidence and ambiguity.
6. Export CycloneDX and vulnerability reports.

Then explain that Maven JAR/AAR artifacts are converted into DEX-compatible reference features stored in SQLite.

### Slide 6: Matcher Evidence

**Time:** 60 seconds

**Main message:** No single signal is reliable enough for every APK.

Explain:

- Package evidence supports candidate recall.
- Classes and methods support identity.
- Opcodes and class dependency graphs add structural evidence.
- Literals and version-distinctive features help separate nearby versions.
- POM coherence is guarded.
- API-reference and opcode tri-gram experiments remain disabled globally because controls did not justify promotion.

### Slide 7: Confidence Model

**Time:** 55 seconds

**Main message:** Library presence and exact-version correctness are different claims.

Explain:

- Identity asks whether the library is present.
- Version confidence asks whether the exact version is supported.
- Ambiguity records nearby plausible versions.
- CVE confirmation requires strong identity and version evidence.

The key sentence:

> A real library with an uncertain version must not become a fake confirmed vulnerability.

### Slide 8: Evaluation Design

**Time:** 65 seconds

**Main message:** APK families are separated so difficult cases remain visible.

Explain:

- Controlled APKs have exact ground truth.
- Clean real APKs have strong source validation.
- Partial real APKs represent realistic difficult cases.
- The source-linked blocked category is now zero.
- Native, protected, and hidden-code limitations stay visible but outside exact Maven-version metrics.

### Slide 9: Results

**Time:** 90 seconds

This is the most important slide.

First explain the normal metric:

> Across 102 source-validated real APKs, 927 of 1837 emitted Maven versions were confirmed, which is 50.5 percent.

Then explain the source-known v2 lane:

> Across 106 source-tree cases, the bounded source-version lane confirmed all 6772 emitted rows. This is not APK-only accuracy because the correct source versions constrain the reference slice.

Never combine the two results into one accuracy number.

### Slide 10: Result Interpretation

**Time:** 60 seconds

**Main message:** Mixed results identify where engineering work is needed.

Explain:

- Clean cases show successful end-to-end operation.
- Partial cases expose AndroidX, Kotlin, adjacent-version, and older-dependency ambiguity.
- Boundary cases include native, dynamically loaded, protected, or heavily transformed code.

Say:

> Difficult cases are not discarded. They become the roadmap for reference growth and matcher recall.

### Slide 11: Demo Evidence

**Time:** 60 seconds before the live demo

Explain the three proof lanes:

- Clean F-Droid: 23 Maven components, 23/23 source-confirmed, zero OSV vulnerabilities.
- Vulnerable Jackson fixture: three confirmed HIGH advisories.
- Transparency export: remaining source, matcher-recall, and missing-reference rows are visible.

The vulnerability CVEs are:

- `CVE-2020-36518`
- `CVE-2022-42003`
- `CVE-2022-42004`

### Slide 12: Guarded AI Contribution

**Time:** 75 seconds

**Main message:** The project demonstrates ML/DL work without allowing models to overrule SBOM evidence.

Explain:

- RandomForest: `0.708` test macro-F1, integrated for report-only suggestions.
- MVP-safe Transformer: `0.882`, removes source-version and source-validation shortcuts.
- Structured Transformer: `0.977`, kept as research evidence because the full token profile may contain contextual shortcuts.
- Raw-opcode Transformer: `0.110`, below the `0.128` baseline, so it is an honest negative result.

Say:

> The integration gate permits report wording, prioritization, and risk triage. It blocks AI-selected versions, SBOM changes, and CVE-label changes.

### Slide 13: Conclusion

**Time:** 45 seconds

Close with three contributions:

1. End-to-end APK to CycloneDX and CVE pipeline.
2. Transparent evaluation that preserves hard cases and remaining gaps.
3. Guarded hybrid and AI research without unsupported production authority.

Closing sentence:

> The value of the project is not a perfect-looking score. It is a useful, measurable, and transparent reverse-SBOM system.

## Live Demo Plan

Do not rebuild the large database or rerun the 106-APK evaluation live.

Open these before presenting:

1. `data/results/report-real-f-droid-final-demo-osv/report.html`
2. `data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json`
3. `data/results/demo-osv-vulnerable-jackson-databind/report.html`
4. `docs/evaluation/FINAL_AI_DEFENSE_DEMO.md`

Recommended demo:

1. Show the F-Droid component table.
2. Open the CycloneDX JSON and point to a Maven PURL and confidence properties.
3. Show zero vulnerabilities for the clean case.
4. Open the Jackson report and show the three confirmed HIGH advisories.
5. Open the AI defense verdict and show `10/10` checks passed.

If the network is unavailable, do not query OSV live. Use the saved reports.

## Expected Jury Questions

### Why not use Gradle or a normal SBOM scanner?

Because the target scenario starts from a compiled APK without source dependency metadata. Source-based tools remain preferable when the source project is available.

### What is the main technical contribution?

An end-to-end pipeline combining APK extraction, multi-scale Maven reference matching, identity/version confidence separation, CycloneDX output, vulnerability mapping, and transparent evaluation.

### Is `927/1837` precision, recall, or accuracy?

It is an emitted Maven version confirmation rate. It measures how many emitted versions are confirmed by source evidence. It is not full dependency recall.

### Why is the v2 lane `6772/6772` if the normal metric is much lower?

The v2 lane uses exact source coordinate-version slices. It tests whether the pipeline recognizes and emits correct rows when the correct versions are present in a constrained reference set. The normal lane is the realistic APK-only selection result.

### Does `6772/6772` mean 100 percent real-world accuracy?

No. It is a source-known upper-bound recognition result, not unconstrained APK-only accuracy.

### Why are many source dependencies not emitted?

Some are source-only modules, BOMs, aliases, metadata-only dependencies, or components without distinguishable bytecode. Others are missing-reference or matcher-recall candidates. The transparency export classifies them separately.

### Why did adding correct versions sometimes reduce other APK results?

Adjacent versions often share almost identical bytecode. Adding an older or newer version can steal a match from another APK unless the matcher has stronger version-specific evidence.

### Why not use the source version to force the answer?

That would invalidate APK-only evaluation. Source versions are used only for validation or clearly labeled bounded upper-bound experiments.

### How does the matcher resist R8?

It combines package, class, method, opcode, dependency-graph, literal, and other structural evidence. R8 can still remove or transform evidence, so the tool reports risk and uncertainty instead of claiming complete resilience.

### What happens with native libraries?

Native `.so` files are reported with file and hash evidence. Exact Maven identity and version are not claimed unless independent evidence supports them.

### What happens with hidden or dynamically loaded DEX?

The tool reports forensic indicators and a limitation boundary. Static analysis cannot guarantee recovery of code unavailable in the APK's normal DEX surface.

### Why RandomForest?

It works well on the structured numeric evidence already produced by the matcher, trains quickly, provides feature importance, supports class weighting, and is easier to explain than a deep model.

### Why use a Transformer?

The Transformer demonstrates sequence-model and representation-learning knowledge inspired by LibAttention. The MVP-safe profile tests whether learned structured evidence remains useful after removing obvious source shortcuts.

### Why is the structured Transformer score higher than the MVP-safe score?

The full structured token profile can use more contextual and source-derived cues. The MVP-safe profile removes those shortcuts, making `0.882` the more defensible result for report-only risk triage.

### Why keep the raw-opcode Transformer if it performs poorly?

It is a useful negative result. The current corpus has only 14 APKs and 1680 method sequences. Reporting the failure demonstrates honest evaluation and defines the data requirements for future work.

### Is AI used to choose the final library version?

No. AI is report-only. The deterministic matcher remains the authority for versions, SBOM components, and vulnerability labels.

### How did you avoid training/test leakage?

The ML/DL evaluation uses deterministic grouped splits by case ID. The MVP-safe token profile also removes source-version, candidate raw-version, source-rank, validation-only flags, and diagnostic context shortcuts.

### How are vulnerabilities confirmed?

OSV results are connected to detected Maven PURLs and version evidence. Strong exact evidence can support a confirmed finding; ambiguous or mismatched versions remain potential or report-only.

### Why CycloneDX?

CycloneDX is a standard SBOM format with support for components, package URLs, properties, and vulnerability-oriented workflows.

### How does your work compare with LibAttention?

LibAttention motivates learned representations for R8-resistant library identity. This project extends the research story toward version confidence, standard SBOM output, CVE mapping, and explicit production guardrails.

### What would you improve first with more time?

Stronger version-distinctive evidence, more independent R8 APKs for raw-code learning, broader reference coverage, and strict representative APK-only promotion controls.

### What is the biggest limitation?

Exact versions can be indistinguishable after optimization, especially across adjacent AndroidX and Kotlin ecosystem versions. Static evidence also cannot fully solve native or dynamically loaded code.

### Why should the jury trust the evaluation?

The project separates controlled, clean, partial, and limitation cases; exports the remaining denominator; keeps failed experiments; and prevents source-known or AI-assisted lanes from being described as APK-only production accuracy.

## Difficult Question Strategy

When you do not know an answer:

1. State the boundary clearly.
2. Refer to the evidence you do have.
3. Explain how you would test the question.

Example:

> I did not validate that configuration independently, so I would not claim it. I would add it as a controlled profile, run the clean and hard APK regression matrix, and promote it only if target improvements do not create regressions.

## Final Checklist

- Rehearse once in 12 minutes and once in 15 minutes.
- Keep Slide 9 under two minutes.
- Never call the v2 lane APK-only accuracy.
- Never say AI selects final versions.
- Open the saved reports before entering presentation mode.
- Disable notifications.
- Keep the PPTX, PDF report, and demo artifacts available offline.
- Finish with the three contributions, then stop and invite questions.
