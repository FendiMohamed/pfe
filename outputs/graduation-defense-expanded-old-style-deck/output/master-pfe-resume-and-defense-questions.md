# Master and PFE Defense Resume and Likely Jury Questions

Prepared for Fendi Mohamed.

This file is based on the current thesis sources, evaluation documents, failed-experiment ledger, AI/R8 reports, final v2 evidence package, and the current 102-slide defense deck.

## Sources Checked

- `thesis/master/frontmatter/abstract_en.tex`
- `thesis/master/chapters/ch01_general_introduction.tex`
- `thesis/master/chapters/ch04_evidence_trust_framework.tex`
- `thesis/master/chapters/ch05_general_conclusion.tex`
- `thesis/pfe/frontmatter/abstract_en.tex`
- `thesis/pfe/chapters/ch01_general_introduction.tex`
- `thesis/pfe/chapters/ch07_general_conclusion.tex`
- `docs/evaluation/THESIS_EVALUATION_TABLES.md`
- `docs/thesis/FINAL_V2_RESULTS_SECTION.md`
- `docs/evaluation/DEMO_FINAL_V2_PACKAGE.md`
- `docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md`
- `docs/evaluation/DEMO_FINAL_V2_MATCHER_RECALL_DIAGNOSTICS.md`
- `docs/evaluation/AI_R8_FINAL_EVALUATION.md`
- `docs/evaluation/FINAL_AI_DEFENSE_DEMO.md`
- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`
- `docs/thesis/THESIS_COMMITTEE_REVIEW_2026-06-29.md`
- `outputs/graduation-defense-expanded-old-style-deck/output/presentation-speech-page-by-page.md`
- `outputs/graduation-defense-expanded-old-style-deck/output/artifact-build-manifest.json`

## One-Minute Defense Story

My work studies how to recover a useful Software Bill of Materials from a compiled Android APK when the source code and build files are not available. The Master thesis focuses on the trust problem: what kind of evidence can support a recovered component, an exact version, and a vulnerability claim. It proposes an evidence-based framework that separates identity, version, provenance, confidence, ambiguity, validation context, and downstream authority.

The Engineering/PFE thesis implements that idea as a static APK-to-SBOM pipeline. It extracts APK and DEX evidence, compares it with Maven reference profiles, emits CycloneDX SBOM output, queries OSV for vulnerabilities, and generates dashboards. The main result is not "perfect dependency recovery." The main result is an auditable partial SBOM workflow that tells the user what is confirmed, what is uncertain, what is report-only, and what is outside the current scope.

## Master Thesis Resume

### Short Resume

The Master thesis, titled "Towards Trustworthy SBOM Recovery from Compiled Android Applications", studies the conditions required for recovered SBOM claims to be trustworthy when they are produced from compiled Android APKs. It treats APK-to-SBOM recovery as an evidence and trust problem rather than only a detection problem.

### Problem

A valid SBOM file is not automatically trustworthy. In Android, the compiled APK does not preserve a clean dependency manifest. Libraries are merged into DEX bytecode, transformed by R8, split across multidex, or hidden behind native and dynamic loading boundaries. A tool may output a precise-looking package and version even when the supporting evidence is weak.

### Central Research Question

How can heterogeneous evidence extracted from compiled and obfuscated Android applications be combined to produce trustworthy SBOM component and version claims with explicit provenance, confidence, uncertainty, and validation boundaries?

### Supporting Questions

1. What evidence sources are available in compiled Android applications?
2. How do existing Android library detection approaches combine these sources?
3. Which factors determine evidence strength for identity and exact-version attribution?
4. How should conflict, missing evidence, transformations, and source-dependent evidence be represented?
5. What information must accompany a reconstructed SBOM claim for vulnerability management?
6. How can such a framework be evaluated without overstating accuracy?

### Method

The Master thesis reviews and organizes state-of-the-art Android third-party library detection and binary component recovery work. It extracts technique families, evidence sources, transformation threats, version capability, validation practices, and trust implications. It then turns these observations into a conceptual evidence-trust framework.

### Main Contribution

The Master contribution is a trust framework for recovered SBOM claims. Its central idea is that every recovered result must be treated as a claim with evidence and authority boundaries. The framework includes:

- claim explicitness;
- identity-version separation;
- evidence provenance;
- reference coverage awareness;
- transformation-bounded confidence;
- conflict preservation;
- validation-lane separation;
- authority monotonicity;
- report-only containment;
- auditable abstention.

### Evidence Hierarchy

The framework ranks evidence by what it can safely support:

- E0: no usable component evidence;
- E1: weak contextual evidence, useful only as a hint;
- E2: identity-supporting evidence, enough for a candidate component but not exact version;
- E3: independent multi-source identity evidence;
- E4: version-discriminating APK evidence;
- E5: externally validated exact evidence, such as source dependency tree or controlled ground truth.

The important defense point is that a signal can be strong for identity but weak for exact version. This is why identity and exact version must be separated.

### Validation Lanes

The Master framework says that evaluation must keep evidence lanes separate:

- controlled ground truth;
- clean source-validated real APKs;
- partial source-validated real APKs;
- source-known upper-bound experiments;
- report-only diagnostics;
- experiment-only optimization lanes;
- boundary and limitation cases.

This protects the thesis from mixing a controlled fixture result, a real APK result, and an upper-bound result into one misleading score.

### Vulnerability Policy

The Master thesis states that a vulnerability claim cannot be stronger than the component and version claim behind it. If the version is confirmed, a CVE can be treated as confirmed. If the version is uncertain or report-only, the vulnerability must also remain potential or report-only.

### Limitations

The framework is conceptual and conservative. It does not solve all component recovery problems by itself. It also does not make native package-version recovery, dynamic code, or hidden payloads automatically solvable. Its value is to define how a recovery system should report evidence honestly.

### Future Work

The Master thesis points toward calibrated evidence fusion, larger realistic benchmarks, provenance-aware SBOM formats, better reference coverage, native component recovery, dynamic-code handling, and stronger evaluation protocols.

## PFE Thesis Resume

### Short Resume

The PFE thesis, titled "Evidence-Based SBOM Recovery from Compiled Android APKs", implements and evaluates a static APK-to-SBOM pipeline. It starts from a compiled APK, extracts bytecode and metadata evidence, matches it against Maven reference profiles, emits CycloneDX SBOM output, maps vulnerabilities through OSV, and generates human-readable dashboards.

### Problem

Most SBOM generation workflows assume access to source code, Gradle files, package managers, or build metadata. In many audit situations, the only available artifact is the APK. The challenge is to recover useful component information from bytecode while avoiding false confidence, especially under R8, version similarity, reference DB gaps, native code, and hidden code.

### Research Questions

1. Can the pipeline recover exact Maven versions when ground truth and adequate reference evidence are available?
2. How does emitted-version quality change between clean and difficult real APK families?
3. How much of the full source dependency denominator is represented by the reference database and emitted by the matcher?
4. Can SBOM, vulnerability, and AI assistance preserve uncertainty and authority boundaries?

### General Objective

Design, implement, and evaluate a static evidence-based system that recovers a bounded CycloneDX SBOM from a compiled Android APK and supports confidence-aware vulnerability analysis.

### Implemented Pipeline

The implemented MVP performs these steps:

1. Inspect the APK archive, manifest, DEX files, resources, assets, native files, and extraction-risk indicators.
2. Extract packages, classes, methods, opcodes, literals, API references, dependency relations, and structural features.
3. Acquire selected Maven JAR/AAR releases and convert them to comparable DEX reference profiles.
4. Store versioned reference features in a SQLite database.
5. Rank component and version candidates with explainable static evidence.
6. Separate component identity confidence from exact-version confidence.
7. Preserve ambiguity and competing candidates.
8. Emit accepted components as CycloneDX JSON using Package URLs.
9. Query OSV for vulnerability information while preserving confidence boundaries.
10. Produce JSON, Markdown, and HTML report bundles.
11. Validate emitted Maven rows against source dependency trees when auditable source is available.
12. Keep AI/R8 assistance report-only unless it passes promotion gates.

### Main Contribution

The PFE contribution is not only a detector. It is an end-to-end evidence-governed APK-to-CycloneDX workflow:

- APK evidence extraction;
- Maven reference profile construction;
- static component and version matching;
- confidence-aware SBOM generation;
- OSV vulnerability lookup;
- source-validation evaluation;
- dashboard reporting;
- failed-experiment governance;
- report-only AI and R8 diagnostics.

### Main Results To Memorize

- Controlled fixtures: 72 APKs, 84 expected Maven versions, 84/84 confirmed.
- Clean source-validated real APKs: 5 APKs, 47/47 emitted Maven versions confirmed.
- Partial source-validated real APKs: 97 APKs, 880/1790 emitted Maven versions confirmed.
- All source-validated real APKs: 102 APKs, 927/1837 emitted Maven versions confirmed, 50.5%.
- Full source denominator: 927/12082 exact rows emitted end to end, 7.7%.
- Shared DB exact source-version coverage: 1231/12082 source rows, 10.2%.
- Source-version constrained v2 lane: 106 source-tree APK cases, 6772/6772 emitted rows confirmed, 0 wrong-version emitted rows, 0 missing emitted rows.
- V2 source gaps: 5238 rows remain outside the emitted result.
- Missing-reference candidates: 442 rows.
- Matcher-recall candidates: 2281 rows.
- F-Droid clean demo: 23 Maven components, 4 native files, 2 DEX files, 0 vulnerabilities.
- Controlled Jackson vulnerable demo: jackson-databind 2.9.10.8 with CVE-2020-36518, CVE-2022-42003, and CVE-2022-42004.
- Final AI defense demo: 10/10 checks passed.

### What The Numbers Mean

84/84 means the matcher mechanics work on controlled fixtures with known ground truth and adequate reference evidence.

47/47 means the tool can produce exact emitted Maven versions for clean real APKs when source validation and reference coverage support the claim.

927/1837 is the normal real-APK emitted-version confirmation rate. It is not full dependency recall. It only measures correctness among Maven rows emitted by the tool and checked against source evidence.

927/12082 is the full source-denominator exact emission rate. It shows how much of the resolved source dependency denominator appears as exact emitted rows.

6772/6772 is a source-version constrained upper-bound result. It proves recognition when the correct source coordinate and version are available in a per-APK constrained reference slice. It must not be presented as general APK-only accuracy.

### Failed and Non-Promoted Experiments

The thesis records failed experiments because they prove the system avoids unsafe promotion.

- Generic recency or newer-version rules were rejected because recency is not independent evidence of the compiled version.
- Global opcode tri-gram weighting was disabled because it regressed controls without confirmed improvement.
- Global API-reference weighting was disabled because it did not improve guarded source-validation metrics.
- Broad POM/dependency coherence remains diagnostic because metadata should not override APK evidence.
- Global multi-scale R8 fusion was rejected because it produced real improvements but also controlled and clean-real regressions.
- Phase 5 R8 trigger is experiment-only because it is promising but does not change default matcher behavior.
- Version-band source-known reranking found many fixable rows but is not promoted because the APK-only reranker produced 0 safe fixes.
- R8 structural recall found 1000 report-only candidates, but the stricter APK-only promotion gates left 0 production promotion candidates.
- Raw-opcode Transformer is a negative result: test macro-F1 0.110, below opcode-count baseline 0.128.
- AI/ML/DL assistance remains report-only because it cannot change selected versions, SBOM components, vulnerability labels, or source-validation metrics.

### AI, ML, and DL Results

The AI layer is useful for triage but not authoritative.

- RandomForest:
  - rows: 20523;
  - test macro-F1: 0.708;
  - decision: keep integrated as report-only.
- Structured-token Transformer:
  - rows: 20523;
  - test macro-F1: 0.977;
  - decision: research status only because it uses structured project-evidence tokens.
- MVP-safe Transformer:
  - rows: 20523;
  - test macro-F1: 0.882;
  - test accuracy: 0.907;
  - decision: candidate for report-only risk triage.
- Raw-opcode Transformer:
  - rows: 1680;
  - test macro-F1: 0.110;
  - baseline macro-F1: 0.128;
  - decision: research-only, not promotable.

The safest sentence is: "AI helps explain and triage uncertain cases, but the deterministic matcher remains the authority for SBOM and CVE output."

## Difference Between Master and PFE

| Aspect | Master thesis | PFE thesis |
|---|---|---|
| Main focus | Trustworthy recovered SBOM claims | Implemented APK-to-SBOM pipeline |
| Main question | What evidence is enough to trust identity, version, and vulnerability claims? | Can a static tool recover useful SBOM evidence from compiled APKs? |
| Contribution type | Conceptual framework and research synthesis | Engineering system and evaluation |
| Output | Evidence hierarchy, claim model, trust policy, validation lanes | CLI pipeline, reference DB, CycloneDX output, OSV lookup, dashboards |
| Evaluation role | Defines how evidence should be evaluated without overclaiming | Produces controlled, real APK, v2, AI, and demo evidence |
| AI role | Report-only containment principle | Implemented report-only AI/R8 assistance |
| Best defense phrase | "The Master defines what a trustworthy recovered claim must expose." | "The PFE builds and measures a system that follows that principle." |

## Presentation Alignment

The current defense deck has 102 slides and follows this structure:

1. Introduction.
2. Background.
3. State of the Art.
4. Contribution.
5. Implementation.
6. Demonstration.
7. Conclusion.

The deck includes detailed demonstration screenshots:

- F-Droid dashboard summary;
- detected-components panels;
- version-decision panels;
- vulnerability and artifact panels;
- vulnerable Jackson dashboard;
- confirmed Jackson CVE findings;
- hybrid AI R8 diagnostics;
- AI assistance summary;
- RandomForest metrics;
- Deep Learning results;
- full F-Droid and Jackson report screenshots.

During the defense, use those screenshots as evidence, not decoration. For each screenshot, say what decision it proves.

## Most Likely Jury Questions and Prepared Answers

### 1. What is the difference between a build-generated SBOM and your recovered SBOM?

A build-generated SBOM comes from source code, package managers, or build metadata. My recovered SBOM starts only from the compiled APK. That means the evidence is weaker and transformed, so the system must expose confidence, ambiguity, and limitations. I do not claim to replace a trusted build SBOM. I provide a useful recovered SBOM when no build context is available.

### 2. Why is APK-to-SBOM recovery difficult?

Because Android compilation merges libraries into DEX bytecode, removes source-level dependency metadata, applies R8 shrinking and optimization, and may include native or dynamically loaded code. Exact versions are especially hard because adjacent library versions can share very similar bytecode.

### 3. What is the main contribution of the Master thesis?

The Master thesis proposes an evidence-based trust framework for recovered SBOM claims. It defines how to separate component identity, exact version, evidence provenance, confidence, ambiguity, validation lane, and vulnerability authority.

### 4. What is the main contribution of the PFE thesis?

The PFE thesis implements an end-to-end static APK-to-SBOM pipeline. It extracts bytecode evidence, matches Maven reference profiles, emits CycloneDX SBOM output, queries OSV, generates dashboards, validates against source trees, and keeps uncertainty visible.

### 5. Are the two theses the same work?

No. They share the same domain, but they answer different questions. The Master is the research framework for trustworthy recovered claims. The PFE is the engineering implementation and evaluation of a practical APK-to-SBOM pipeline.

### 6. Why should a user trust the system if full source-denominator exact emission is only 7.7%?

Because the system is not presented as complete dependency recovery. It is an evidence-qualified partial SBOM tool. The 7.7% number is useful because it exposes the full denominator honestly. The tool is valuable for confirmed emitted components, vulnerability triage, and gap analysis, while clearly showing what it did not recover.

### 7. What is the difference between 50.5% and 7.7%?

50.5% is the emitted-version confirmation rate: among emitted Maven rows checked against source evidence, 927 out of 1837 were exact. 7.7% is the full source-denominator exact emission rate: 927 exact emitted rows out of 12082 resolved source dependency rows. The first measures correctness of emitted rows. The second measures coverage of the full source dependency denominator.

### 8. What does 84/84 prove?

It proves that the matcher mechanics work on controlled fixtures with known expected components and adequate reference evidence. It does not prove perfect real-world accuracy.

### 9. What does 6772/6772 prove?

It proves recognition under a source-version constrained upper-bound lane. For each APK, the candidate space is constrained to exact source coordinate and version rows. It shows that the system can recognize and report those rows without version mismatches under favorable conditions. It is not general APK-only accuracy.

### 10. Is the v2 result cheating?

No, because it is explicitly labeled as a source-version constrained upper bound. The thesis reports it separately from the normal APK-only metric. It also exports the remaining source gaps, including missing-reference candidates and matcher-recall candidates.

### 11. Why did you not present only the best number?

Because that would be misleading. Controlled fixtures, normal real APK validation, full source-denominator recall, source-known upper bounds, and report-only diagnostics answer different questions. The thesis keeps them separate to avoid false claims.

### 12. How do you know the source dependency tree is valid ground truth?

It is valid as a source-validation reference for resolved dependencies, but it is not perfect proof of APK-side presence. Some source dependencies may be metadata-only, test-only, source-only, excluded by shrinking, or represented by sibling artifacts. That is why the thesis calls the main metric emitted-version confirmation, not full dependency recall.

### 13. What prevents source-known information from leaking into APK-only decisions?

The production matcher works from APK evidence and the reference DB. Source dependency trees are used after the fact for validation and for separate source-version constrained upper-bound experiments. The thesis keeps those lanes separate and labels source-known results as upper bounds.

### 14. Why did you use CycloneDX?

CycloneDX is a standard SBOM format and supports Package URLs and properties that can carry evidence, confidence, and metadata. Using a standard format makes the output interoperable instead of only producing a private report.

### 15. Why use OSV for vulnerability lookup?

OSV supports package ecosystem vulnerability lookup and fits Maven package coordinates. The important point is that the system does not treat every OSV hit as equally confirmed. Vulnerability interpretation inherits the confidence of the component and version evidence.

### 16. How do you handle vulnerabilities when the version is uncertain?

If the version is source-confirmed or exact, the vulnerability can be confirmed. If the version is uncertain, mismatched, or report-only, the vulnerability is reported as potential or report-only. The vulnerability claim cannot be stronger than the component-version claim.

### 17. What is the F-Droid demo proving?

It proves a clean real APK case. The report shows 23 Maven components, 4 native files, 2 DEX files, low extraction and obfuscation risk, and 0 vulnerabilities. It also demonstrates the dashboard, detected-components panel, version-decision panel, and generated artifacts.

### 18. What is the vulnerable Jackson demo proving?

It proves the end-to-end positive vulnerability path. The controlled APK contains jackson-databind 2.9.10.8. The system identifies it and reports three high-severity CVEs: CVE-2020-36518, CVE-2022-42003, and CVE-2022-42004.

### 19. Why are some real APKs only partial?

Because real APKs contain modern AndroidX/Kotlin dependencies, adjacent versions, large source trees, native code, minification, missing reference versions, artifact-family aliases, and dependencies that may not appear in compiled bytecode. Partial does not mean useless. It means the report separates confirmed rows from mismatches and gaps.

### 20. What is the biggest current limitation?

The biggest limitation is the combination of reference coverage and matcher recall. A missing exact reference cannot be selected, and a large reference DB can still fail if candidate generation or version discrimination is weak.

### 21. Is R8 solved?

No. R8 is handled as a risk and diagnostic dimension. Some controlled R8 cases are covered, and R8 diagnostics are visible, but hard R8 structural recall remains report-only until promotion gates pass.

### 22. Why not promote the R8 structural approach?

Because the stricter APK-only promotion gate produced 0 production promotion candidates. Some rows looked promising, but same-coordinate risk and missing representative controls blocked promotion.

### 23. What did the failed experiments teach?

They showed that promising signals can improve one target and regress controls. This is why the project uses target/control promotion gates. Failed experiments are evidence that the system avoids unsafe exact-version claims.

### 24. Why did the APK-only version-band reranker fail?

The source-known experiment showed a real opportunity, but the APK-only reranker made 0 safe fixes. That means the correct version was not sufficiently visible in APK-only alternatives for safe promotion.

### 25. Why include AI if it cannot change the SBOM?

Because AI can still help triage uncertainty, highlight risk, and guide future work. In security reporting, assistance is useful as long as it does not silently modify authoritative outputs.

### 26. What exactly can AI change?

In the current system, AI can add report-only sections and suggestions. It cannot change selected versions, detected components, CycloneDX SBOM components, vulnerability labels, or source-validation metrics.

### 27. Why is the structured Transformer not authoritative if its macro-F1 is high?

Because it uses structured project-evidence tokens, so it is not proof of general raw APK exact-version detection. The MVP-safe profile is more defensible for report-only triage, and the raw-opcode Transformer is an honest negative result.

### 28. What is the RandomForest result?

The RandomForest uses 20523 rows and reaches about 0.708 test macro-F1. It is kept integrated as report-only assistance.

### 29. What is the MVP-safe Transformer result?

It uses 20523 rows, reaches about 0.882 test macro-F1 and 0.907 test accuracy, and remains a candidate for report-only risk triage.

### 30. What is the raw-opcode Transformer result?

It uses 1680 method-level opcode sequences from 14 APKs and reaches 0.110 macro-F1, below the opcode-count baseline of 0.128. It is not promotable.

### 31. Why not run existing tools as baselines?

The thesis includes state-of-the-art comparison and dimensional analysis, but a full executable baseline is difficult because many tools are unreleased, outdated, dataset-specific, not version-focused, or not SBOM-producing. The honest answer is that this is a limitation. A future work item is to run executable baselines where reproducible toolchains are available.

### 32. How is your work different from LibScout or LibPecker?

Those tools focus on Android third-party library detection and matching. My work builds an evidence-governed APK-to-CycloneDX pipeline with vulnerability lookup, confidence boundaries, source-validation interpretation, failed-experiment governance, and dashboard reporting.

### 33. How is your work different from LibAttention?

LibAttention motivates learned R8-resilient presence detection. My work is focused on exact-version SBOM recovery and vulnerability authority. Learned assistance is kept report-only unless it passes strict validation gates.

### 34. How is your work different from UniBOM?

UniBOM is related to SBOM workflows, but it is not an Android APK-side exact-version recovery system. My project starts from compiled APKs and tries to recover Maven component evidence from bytecode.

### 35. Why is identity-version separation important?

Because detecting that a library family is present is easier than proving the exact version. Vulnerability decisions are often version-dependent, so version claims require stronger evidence than identity claims.

### 36. What is abstention?

Abstention means the system refuses to make an exact claim when evidence is insufficient. It may emit identity only, a bounded candidate set, a risk note, or no Maven component. In this project, abstention is a safety mechanism, not a failure.

### 37. How do you handle native libraries?

Native `.so` files are reported as hash-backed CycloneDX file components or boundary evidence. The MVP does not claim native package/version identification.

### 38. How do you handle hidden or dynamically loaded code?

The system reports hidden DEX or protector-style behavior as risk or boundary evidence. It avoids inventing Maven components when the static evidence is unsupported.

### 39. What are the most important future works?

Safer large-catalog candidate retrieval, better exact-version separability, calibrated abstention, stronger APK-only matcher recall, executable baseline evaluation, larger realistic benchmarks, native package-version recovery, and dynamic-code analysis.

### 40. What is the main thing you want the jury to remember?

The project is useful because it is honest. It recovers APK-derived SBOM evidence, emits standard CycloneDX artifacts, maps vulnerabilities when evidence supports them, and exposes uncertainty instead of hiding it behind a precise-looking dependency list.

## Hard Criticism Scripts

### If they say: "Only 7.7% full recall is weak."

Answer:

Yes, if the goal is complete dependency recovery, 7.7% is limited. But that is exactly why I report it. The implemented system is a high-confidence partial recovery tool, not a replacement for a source-generated SBOM. Its practical value is confirmed emitted components, vulnerability triage, and transparent gap analysis.

### If they say: "The v2 result looks like you used the answer."

Answer:

The v2 lane intentionally uses source-known exact-version slices, and I label it as an upper-bound recognition test. It is not used as the normal APK-only accuracy number. It answers a different question: when correct reference rows are available, can the system recognize and report them without version mismatches?

### If they say: "Why include failed experiments?"

Answer:

Because failed experiments protect the credibility of the result. In exact-version recovery, a change can improve one target and regress other APKs. Keeping failed experiments proves that I did not promote signals unless they passed controls.

### If they say: "Why include AI if it is not authoritative?"

Answer:

Because report-only AI is still useful for triage and explanation. In a security tool, the authority boundary matters. The current system lets AI help the analyst while keeping selected versions, SBOM output, and CVE labels under deterministic control.

### If they say: "Where is the Master contribution?"

Answer:

The Master contribution is the claim-trust model. It formalizes what every recovered SBOM claim must expose: identity, version or version set, evidence provenance, evidence quality, confidence, ambiguity, validation lane, and permitted vulnerability interpretation. The PFE is the case study implementation that follows those principles.

## Short Closing Statement

This work does not claim that compiled APKs can always be converted into complete and perfect SBOMs. The conclusion is more precise: static APK analysis can recover useful SBOM evidence when the reference and bytecode evidence support it, but trustworthy security use requires explicit confidence, separate validation lanes, and honest abstention. That is why the project combines implementation, evaluation, dashboards, CVE mapping, failed-experiment evidence, and report-only AI under one evidence-gated workflow.
