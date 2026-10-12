# Supervisor Briefing: How to Explain the Paper

## Paper title

**Evidence-Gated Recovery of Maven Components from Compiled Android APKs**

The paper presents an implemented static-analysis pipeline that tries to recover third-party Maven components and their versions from compiled Android APKs. The central idea is that the system must preserve the strength and limitations of its evidence instead of presenting every similarity match as a certain dependency or vulnerability.

---

## 1. Abstract

### What this section does

The abstract gives the supervisor a compact summary of:

1. The practical problem.
2. The implemented solution.
3. The main evaluation evidence.
4. The limits of the claims.

### How to explain it

The problem is that an APK often arrives without its source code, Gradle files, dependency tree, or build metadata. The system therefore analyzes compiled DEX code and compares it with versioned Maven reference profiles.

The important design choice is to separate three decisions:

- Is a component family probably present?
- Is one exact published version supported by the evidence?
- Is the evidence strong enough to support a downstream vulnerability report?

The abstract reports the recorded evaluation results, including:

- **84/84 expected component-version rows** across **72 controlled fixtures**.
- **927/1,837 emitted Maven version rows** agreeing with source-side evidence across **102 APKs**.
- **927/12,082 source dependency rows** emitted exactly across **106 source-tree cases**.
- **6,772/6,772** in a separate source-version-constrained upper-bound analysis.

These numbers come from the retained theses and evaluation records. The current checkout does not contain every row-level input and frozen run manifest, so the paper explicitly does not claim a fresh rerun or independent recalculation.

### Main message

The abstract should be presented as a summary of a bounded engineering and evaluation contribution, not as a claim of universal Android dependency recovery.

---

## 2. Introduction

The introduction motivates the work and tells the reader how to read the rest of the paper.

### 2.1 Context

SBOMs are used to inventory software components and support supply-chain risk management. For Android, the auditor may only have the final APK. The APK contains compiled DEX files, resources, and possibly native code, while the original dependency declarations and build decisions are unavailable.

The build process can also change the observable code:

- D8 converts Java bytecode to DEX.
- R8 can remove, rename, rewrite, or inline code.
- Android libraries can include resources, manifests, and native libraries.
- Multiple Maven artifacts may contribute to the same packaged application.

Therefore, recovering a Maven dependency from an APK is an evidence problem, not a simple package-name lookup.

### 2.2 Problem statement

This subsection defines the exact problem studied:

> Recover component and version evidence from a compiled APK using a versioned reference set, and report the result with enough provenance and uncertainty for SBOM and vulnerability workflows.

The paper deliberately separates:

- component-family identity,
- exact-version attribution,
- vulnerability interpretation.

This separation is necessary because a likely library family does not automatically prove a precise release, and a vulnerability database result does not independently prove that the component is present.

The source dependency tree is used as validation evidence, but not as a perfect oracle. A dependency declared in the source project may be removed during packaging, while code in the APK may not be represented by a simple source dependency declaration.

### 2.3 Related work and motivation

The paper briefly introduces previous Android third-party-library detectors. Earlier systems use:

- package and class profiles,
- dependency graphs,
- opcode and call-chain features,
- class structural similarity,
- learned representations.

The literature shows that library-family detection and exact-version detection are different tasks. It also shows that performance depends on reference coverage, obfuscation, shrinking, optimization, candidate construction, and the definition of the evaluation denominator.

This motivates two decisions in the project:

1. Results must be reported with their exact unit and denominator.
2. The system must preserve evidence and ambiguity in the SBOM instead of collapsing every plausible match into a definitive claim.

### 2.4 Approach overview

This paragraph gives the high-level workflow:

1. Inspect the APK and parse available DEX files.
2. Extract bytecode-derived features.
3. Compare the features with versioned Maven reference profiles stored in SQLite.
4. Shortlist component families.
5. Rank candidate versions using weighted evidence.
6. Preserve close alternatives when exact-version evidence is weak.
7. Emit CycloneDX records.
8. Optionally query OSV using the reported component/version evidence.

The OSV output is treated as associated evidence. It is not treated as independent proof of component presence or exploitability.

### 2.5 Contributions and scope

The paper claims four contributions:

1. An implemented static pipeline for Maven/JVM component and version evidence recovery.
2. An evidence-aware reporting policy for identity, version confidence, ambiguity, native files, and vulnerabilities.
3. An evaluation that separates controlled fixtures, source-validated emitted rows, source-denominator coverage, and source-constrained recognition.
4. Documentation of failed, rejected, and report-only experiments.

The paper does **not** claim:

- universal Android dependency recovery,
- complete recall of all packaged code,
- calibrated probabilistic confidence,
- reliable native package/version attribution,
- vulnerability precision or recall,
- promotion of unvalidated AI or structural signals into authority.

### 2.6 Paper organization

This final introduction paragraph gives the roadmap:

- Section 3 reviews the state of the art.
- Section 4 explains the proposed evidence model and workflow.
- Section 5 presents implementation and experimental evaluation.
- Section 6 concludes with findings, limitations, and future work.

---

## 3. State of the Art

### Purpose

This section demonstrates why the proposed approach is needed and identifies the research gap.

### Review method

The review protocol searched ACM Digital Library, IEEE Xplore, SpringerLink, ScienceDirect, USENIX, arXiv, and used Google Scholar for discovery and citation chaining.

The review distinguishes:

- library-family detection,
- exact-version detection,
- transformation robustness,
- SBOM and vulnerability use,
- evaluation ground truth and reference coverage.

The paper is transparent that the original database query counts and complete screening flow were not retained. Therefore, it presents a structured mapping review, not a claim of a fully reproducible systematic review.

### Main findings from the literature

Existing methods provide useful signals, but each has limits:

- Package and class profiles can be affected by renaming and packaging changes.
- Graph and opcode methods may depend on candidate generation and class mapping.
- Learned models address presence detection but do not automatically verify Maven coordinates and exact versions.
- Optimization, shrinking, inlining, and partial library reuse can remove or change the features used for matching.
- Version-level results are not directly comparable when studies use different datasets, candidate sets, and false-positive rules.

Benchmark and assessment studies further show that percentages cannot be compared fairly without knowing:

- the reference database,
- the candidate construction,
- the transformation setting,
- the ground-truth unit,
- whether extra wrong versions count as false positives.

### Research gap

The gap addressed by this project is operational and evidence-oriented:

> Existing work provides detectors and version-matching techniques, but the complete path from APK evidence to an uncertainty-aware SBOM and vulnerability report is not adequately represented by a single match score.

The proposed paper therefore focuses on preserving evidence, ambiguity, denominator definitions, and downstream qualification.

---

## 4. Proposed Approach

This section explains what was built and how it works.

### 4.1 Evidence model

The system treats evidence as layered:

1. **APK evidence**: metadata, DEX content, extracted features, and native files.
2. **Reference evidence**: versioned Maven profiles in the SQLite database.
3. **Matching evidence**: family-level and version-level similarity signals.
4. **Validation evidence**: source-side dependency information where available.
5. **Downstream evidence**: CycloneDX records and OSV responses.

These layers are not interchangeable. A source dependency tree can validate an emitted result, but it is not the same as evidence directly observed in the APK.

### 4.2 Pipeline workflow

The workflow can be explained as:

1. Parse APK metadata and available DEX files.
2. Extract features from the compiled code.
3. Query reference profiles.
4. Fuse weighted signals to identify likely component families.
5. Rank version candidates.
6. Keep alternatives when the margin is insufficient.
7. Assign evidence-aware status and confidence labels.
8. Emit CycloneDX components.
9. Record native libraries as hash-identified file components when Maven attribution is not justified.
10. Query OSV only using the reported identity/version evidence.

### 4.3 Decision policy

The policy avoids overclaiming:

- A family match does not automatically become an exact-version match.
- A close candidate can remain ambiguous.
- Missing reference coverage is recorded as a limitation.
- Native-only, hidden, dynamically loaded, or unsupported code remains outside ordinary Maven attribution.
- Advisory results are qualified according to component/version evidence.
- AI suggestions, structural rerankers, and scoped R8 signals remain diagnostic or report-only unless a validated promotion rule is established.

### 4.4 AI and R8 assistance workflow

The project also implemented a report-only assistance path for R8-risk and
evidence triage. Its structured dataset contains 20,523 rows grouped into 149
case identifiers. The split contains 14,905 training rows, 1,750 validation
rows, and 3,868 test rows, with rows from one APK case kept in one partition.
The labels describe project evidence states such as confirmed exact, risk-only,
boundary, report-only suggestion, suppressed uncertainty, and mismatch/extra;
they are not universal APK ground truth.

The Random Forest uses 17 evidence features, including identity confidence,
matcher scores, dependency and opcode signals, and boundary/context indicators.
The structured-token Transformer was evaluated with a full profile and a safer
source-free profile. The safer profile removes source-version, raw
candidate-version, coordinate, rank, and diagnostic context fields. A separate
raw-opcode Transformer uses method opcode sequences from 14 APK cases.

At inference time, the models add report sections, risk indicators, or
investigation suggestions alongside the deterministic matcher. They cannot
select Maven versions, modify CycloneDX components, change OSV labels, or alter
source-validation metrics. A two-target smoke test confirmed that authoritative
outputs stayed unchanged.

### 4.5 Implementation boundary

The implementation uses a SQLite reference database and emits CycloneDX output. The paper separates theoretical decisions from tool details so that the contribution is understandable even if the implementation changes.

The system is intentionally conservative because a false exact-version claim can create an incorrect vulnerability report or an overconfident SBOM.

---

## 5. Implementation and Experimental Evaluation

This is the evidence section of the paper.

### 5.1 Research questions

The evaluation is organized around four questions:

- **RQ1:** Can the pipeline recover expected component versions in controlled fixtures?
- **RQ2:** How often do emitted Maven versions agree with source-side validation evidence in real APK cases?
- **RQ3:** What limits end-to-end source dependency coverage, and what failure causes were recorded?
- **RQ4:** Can the reporting workflow qualify vulnerability findings according to the strength of component/version evidence?

### 5.2 Experimental protocol

The evaluation uses separate evidence lanes because their denominators answer different questions:

- controlled generated fixtures,
- clean source-validated APKs,
- partial source-validated APKs,
- source-denominator coverage,
- source-version-constrained recognition,
- documented vulnerability workflow examples.

The paper does not merge these lanes into one accuracy number.

### 5.3 Results

#### Controlled fixtures

The final recorded snapshot reports **84/84 expected component-version rows confirmed across 72 fixtures**.

The earlier **30-fixture/35-component** count is identified as an earlier project checkpoint, not a contradictory final result.

This result demonstrates controlled behavior only. It is not a population estimate for arbitrary Android applications.

#### Real APK emitted-version confirmation

The recorded results are:

| Stratum | Confirmed / checked | APKs | Interpretation |
|---|---:|---:|---|
| Clean source-validated | 47/47 | 5 | 100.0% agreement among emitted rows |
| Partial source-validated | 880/1,790 | 97 | 49.2% agreement among emitted rows |
| Combined | 927/1,837 | 102 | 50.5% agreement among emitted rows |

The denominator is the number of emitted Maven version rows that were checked. This is not full dependency recall and is not called ordinary precision or accuracy.

#### Source-denominator coverage

The project records **927 exact emitted rows among 12,082 source coordinate/version rows** across 106 source-tree cases.

This is a different measure from emitted-version confirmation. It shows the gap between confirming emitted results and covering the full source-side dependency denominator.

#### Source-version-constrained analysis

A separate experiment reports **6,772/6,772** exact confirmations after restricting each APK’s candidate set using the exact source-known versions.

This is an upper-bound recognition analysis. It is not ordinary APK-only performance because source information was used to restrict the candidates.

#### Vulnerability workflow

Two examples are used:

- A clean F-Droid report with no returned OSV findings.
- A controlled Jackson Databind 2.9.10.8 fixture with three returned advisories.

These examples demonstrate evidence-qualified reporting behavior. They do not measure vulnerability precision, recall, exploitability, or the absence of vulnerabilities.

### 5.4 Failed and report-only experiments

The project records decisions that were not promoted:

- A global R8 blend was rejected after regression checks.
- Scoped R8 triggers remained report-only where controls were insufficient.
- AI suggestions and structural rerankers were not given default authority.
- Source-specific reference additions that helped one target but caused regressions elsewhere were not promoted globally.
- APK-only version-band expansion was not adopted without safe evidence.

These failures are useful because they explain why the final pipeline is conservative.

### 5.5 R8 and AI report-only experiments

R8 was tested through controlled rename, shrink, optimize, shrink-plus-optimize,
package-flattening, inline-like, and multidex fixtures. These cases contribute
to the controlled 84/84 result, but that result should not be described as
universal R8 robustness.

The broader R8 blend was rejected because it improved some target cases while
causing regressions in control and real-APK cases. A narrower Phase-5 trigger
was evaluated on 286 rows, passed 11 validation gates, and generated four
opt-in suggestions with zero changes to the default selected components or
versions. It remains experiment-only.

The retained Phase-4 records use different inputs and denominators, so their
improvement and regression counts are not combined in the paper. The paper
keeps the qualitative decision: the broader global R8 promotion was rejected.

AI was evaluated as report-only evidence using project-derived data, not an
independent Android benchmark. The Random Forest reached about 0.708 test
macro-F1. A structured-token Transformer reached about 0.977 macro-F1 with
the full profile and 0.882 with a safer source-free profile. The raw-opcode
Transformer reached about 0.110 macro-F1 and did not beat its simple baseline.

The full Transformer profile includes source and candidate-version information
that may encode shortcuts related to how the project labels were generated.
The safer source-free profile is therefore the more relevant result for
report-only APK evidence triage.

These numbers describe bounded triage experiments, not APK-only deployment
accuracy. The integration gate prevents AI from changing selected versions,
CycloneDX components, OSV labels, or source-validation metrics. A two-target
smoke test confirmed that the authoritative outputs remained unchanged.

### 5.6 Discussion

The results support four bounded conclusions:

1. The pipeline performs strongly on the final controlled fixture snapshot.
2. Emitted-version agreement varies substantially between clean and partial real APK cases.
3. Reference coverage and the APK-to-source gap limit end-to-end dependency coverage.
4. The vulnerability workflow can preserve evidence qualifications, but the examples do not establish vulnerability detection accuracy.

The main contribution is therefore a useful, evidence-aware workflow with explicit limits, rather than a claim of complete recovery.

### 5.7 Threats to validity

#### Internal validity

Results may be affected by reference database construction, threshold choices, calibration history, evaluator decisions, and unavailable run metadata.

#### External validity

The sample is not representative of all Android applications. Native-heavy apps, commercial protectors, dynamic loading, encrypted payloads, and unsupported ecosystems remain difficult or outside the evaluated scope.

#### Construct validity

A source dependency tree is not a perfect oracle for packaged APK code. Emitted-version confirmation is not full recall. Rule-based confidence labels are not calibrated probabilities.

#### Conclusion validity

Rows inside an APK or application family may not be independent. The clean subset is small, and missing row-level exports prevent independent uncertainty calculations or grouped-family analysis.

### 5.8 Reproducibility status

The paper uses the records preserved in the theses, dashboards, evaluation notes, and project history. It does not rerun the original experiments.

The current checkout lacks some required artifacts for full independent reproduction, including:

- row-level exports,
- generated fixture APKs,
- the reference database snapshot,
- APK/source hashes,
- source revisions,
- a frozen run manifest.

The correct explanation to the supervisor is that the results are documented evaluation snapshots, with their provenance and limitations stated explicitly.

---

## 6. Conclusion

The conclusion returns to the central claim:

The project implemented a static workflow that can recover useful Maven component and version evidence from compiled APKs and carry that evidence into CycloneDX and optional OSV reporting.

The strongest points are:

- separation of family identity from exact-version support,
- preservation of ambiguity,
- explicit treatment of native and inaccessible code,
- denominator-aware evaluation,
- documentation of rejected approaches.

The results support a bounded conclusion: the implementation is useful in controlled and some source-validated cases, but reference coverage, build transformations, ambiguity, and the difference between source dependencies and packaged code limit end-to-end coverage.

The paper should finish by proposing:

- release of a frozen machine-readable evaluation package,
- held-out or leave-one-family-out testing,
- expanded reference coverage,
- better APK-only candidate recall,
- confidence calibration on independent data,
- vulnerability evaluation against an explicit component/version oracle.

---

## Short oral explanation

If the supervisor asks for the paper in one minute:

> This paper presents an implemented APK-only static-analysis workflow for recovering Maven components and versions from compiled Android applications. Its main contribution is not just matching code, but preserving the evidence strength, ambiguity, and limitations of each attribution before generating an SBOM or vulnerability report. We evaluate the workflow through controlled fixtures and source-validated APK cases using separate denominators. The results show strong controlled recovery and useful emitted-version confirmation in some real cases, while also exposing reference coverage, code transformation, and source-to-package limitations. The paper therefore makes a bounded engineering and evaluation claim rather than claiming universal dependency recovery.

---

## Key points to emphasize during supervision

- The paper distinguishes **component presence**, **exact version**, and **vulnerability interpretation**.
- The percentages are never presented without their denominators.
- The 30/35 and 72/84 figures are successive milestones.
- The 6,772/6,772 result is source-version-constrained and must not be described as ordinary APK-only accuracy.
- The 927/1,837 result concerns emitted rows, not full dependency recall.
- Failed experiments are included to justify conservative design decisions.
- The paper does not claim a fresh rerun because the current checkout lacks some original machine-readable artifacts.

