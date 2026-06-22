# PFE Thesis Writing Plan

## Working Title

**Evidence-Based SBOM Recovery from Compiled Android APKs: Design,
Implementation, and Evaluation of a Hybrid Static Analysis Pipeline**

Suggested French title:

**Reconstruction de SBOM à partir d'applications Android compilées :
conception, implémentation et évaluation d'une approche hybride fondée sur les
preuves**

## Purpose of the PFE Thesis

The PFE thesis is the engineering and experimental report of the project. It
must explain:

- the practical security problem;
- the system that was designed and implemented;
- how the implementation relates to previous research;
- how it is executed and evaluated;
- what succeeded, what failed, and why;
- what the current MVP can and cannot claim.

The PFE must not be presented as a general survey. Its central contribution is
the implemented APK-to-SBOM pipeline and the evidence collected through its
evaluation.

## Binding Writing and Resumption Rules

All work on this thesis must follow:

- `docs/thesis/THESIS_WRITING_AND_RESUMPTION_RULES.md`
- `docs/thesis/THESIS_WRITING_SESSION_LOG.md`

Before editing PFE content, the writer must read the shared rules, this plan,
the current checkpoint below, and the latest PFE session-log entry.

PFE-specific binding rules:

1. The PFE remains implementation and evaluation focused.
2. Every described component must exist in the current architecture or be
   clearly labeled proposed/future.
3. Every result must identify its dataset, evidence class, numerator,
   denominator, exclusions, and artifact.
4. Controlled, clean, partial, upper-bound, report-only, experimental, and
   boundary results must remain separate.
5. Failed and rejected experiments must be included when they justify a design
   decision.
6. Commands and flags must be checked against the current CLI before
   publication.
7. Diagrams must match the implemented modules and data flow.
8. AI must remain report-only unless the project records a later validated
   authority change.
9. Existing Markdown drafts are source material, not automatically approved
   thesis prose.
10. A chapter is complete only after evidence, citation, structure, and render
    audits.

## School Style to Follow

The final document should reproduce the school's presentation conventions
without copying text from earlier reports:

1. Institutional cover page.
2. Dedication and acknowledgements.
3. Abstract in English.
4. Résumé in French.
5. Arabic abstract.
6. Keywords after every abstract.
7. Table of contents.
8. List of figures.
9. List of tables.
10. List of acronyms.
11. Part divider pages where appropriate.
12. An introduction and conclusion in every chapter.
13. General conclusion, limitations, perspectives, bibliography, and
    appendices.

## Fixed Evidence Rules

The report must preserve the following distinctions:

- Library identity and exact-version confidence are separate decisions.
- The normal real-APK result is an **emitted Maven version confirmation rate**,
  not full dependency recall.
- Clean and partial real APKs must be reported separately.
- Source-validated, controlled, report-only, experiment-only, and limitation
  evidence must not be mixed.
- The source-known v2 lane is an upper-bound constrained evaluation, not
  unconstrained APK-only accuracy.
- Native `.so` files are hash-based CycloneDX file components; the MVP does not
  recover their package versions.
- AI results remain report-only and cannot be described as SBOM, matcher, CVE,
  or source-validation authority.
- Failed and rejected experiments must remain visible.

Before final submission, all numeric claims must be refreshed from generated
evaluation artifacts rather than copied from an older draft.

## Planned Structure

### Front Matter

Required content:

- university and school identity;
- thesis title;
- student, supervisor, jury, specialty, and academic year;
- dedication and acknowledgements;
- English, French, and Arabic abstracts;
- keywords;
- contents and lists;
- acronym glossary.

The abstract should contain, in this order:

1. Context.
2. APK-only SBOM recovery problem.
3. Proposed approach.
4. Evaluation methodology.
5. Main bounded results.
6. Limitations and contribution.

---

## Chapter 1 - General Introduction

### Objective

Introduce the security and transparency problem, define the research scope,
and state exactly what the project contributes.

### Planned Sections

#### 1.1 Context

- Modern software supply chains.
- Heavy use of third-party components in Android applications.
- Dependency vulnerabilities and the need for software transparency.
- Why an auditor may possess only a compiled APK.

#### 1.2 Problem Statement

- Source-based SBOM tools depend on build manifests and package metadata.
- APK compilation removes or transforms dependency identity and version
  information.
- R8, shrinking, optimization, multidex, artifact variants, and native code
  complicate recovery.
- Vulnerability lookup is unsafe when component versions are uncertain.

#### 1.3 Motivation

- Security auditing without source access.
- Supply-chain transparency.
- Vulnerability-management support.
- Need for explicit uncertainty rather than forced exact-version claims.

#### 1.4 Research Questions

Recommended questions:

1. Can static analysis recover Maven component identities and exact versions
   from compiled APK evidence?
2. Which combinations of metadata, bytecode, structural, and contextual
   evidence are useful for component attribution?
3. How does the pipeline behave across controlled, clean, partial, obfuscated,
   native-heavy, and hidden-code cases?
4. Can recovered evidence be exported as a standard CycloneDX SBOM and used
   for confidence-aware vulnerability lookup?
5. What are the principal limitations preventing trustworthy exact-version
   recovery?

#### 1.5 Objectives

- Design an APK extraction and DEX analysis pipeline.
- Build a Maven reference-feature database.
- Implement hybrid library and version matching.
- Generate CycloneDX SBOMs.
- Map sufficiently supported component versions to vulnerabilities.
- Evaluate the system honestly across distinct evidence classes.

#### 1.6 Contributions

- End-to-end APK-to-SBOM MVP.
- Hybrid evidence extraction and matching.
- Identity/version confidence separation.
- Explicit version ambiguity.
- Guarded reference-database workflow.
- Source-validation and evaluation methodology.
- Report-only AI/R8 assistance.
- Failure and decision ledger.

#### 1.7 Scope and Limitations

- Static APK analysis.
- Maven/JVM dependencies embedded in DEX.
- No general dynamic-code recovery.
- Native package identification outside the current MVP.
- Source validation used as evaluation ground truth, not production input.

#### 1.8 Thesis Organization

Provide one paragraph for each following chapter.

### Primary Project Sources

- `README.md`
- `docs/project_handbook/overview/PROJECT_GOALS_AND_CURRENT_STATE.md`
- `docs/thesis/PFE_FINAL_REPORT_ASSEMBLED.md`
- `docs/thesis/THESIS_ARTIFACT_INDEX.md`

### Planned Visuals

- One motivating Android software-supply-chain diagram.
- One compact diagram contrasting source-based and APK-only SBOM generation.

### Completion Gate

- Every contribution maps to an implementation or evidence artifact.
- Research questions are answered explicitly in Chapter 6 or Chapter 7.
- No result is introduced before its metric is defined.

---

## Chapter 2 - Technical Background

### Objective

Give the reader only the technical knowledge needed to understand the system.
This chapter must establish a continuous path from software supply chains to
APK evidence recovery.

### Planned Sections

#### 2.1 Introduction

Explain the chapter's progression and connection to the research problem.

#### 2.2 Software Supply-Chain Security

- Software supply chain.
- Third-party dependencies.
- Supply-chain attacks.
- Transparency, traceability, and provenance.

#### 2.3 Software Bill of Materials

- Definition and purpose.
- Components, identifiers, versions, hashes, licenses, and relationships.
- SPDX and CycloneDX.
- Package URL.
- SBOM use cases and limitations.

#### 2.4 Vulnerability Identification

- CVE, CWE, CVSS, NVD, OSV, EPSS, and KEV.
- Why accurate identity and version information matter.
- Confirmed, potential, and report-only vulnerability claims.

#### 2.5 Android Application Ecosystem

- Android architecture.
- Java/Kotlin application development.
- Gradle and Maven dependencies.
- AAR and JAR artifacts.
- Public, target, KTX, JVM, Android, and multiplatform artifact families.

#### 2.6 APK Structure

- Manifest.
- `classes.dex` and multidex.
- Resources and assets.
- Signing information.
- Native `.so` files.
- Nonstandard and dynamically loaded code.

#### 2.7 Android Compilation and Optimization

- Compilation from Java/Kotlin to bytecode and DEX.
- D8.
- R8 and ProGuard.
- Renaming, shrinking, optimization, inlining, and package flattening.
- Consequences for library and version identification.

#### 2.8 Reverse Engineering and Static Analysis

- Static versus dynamic analysis.
- APK decoding and DEX parsing.
- Classes, methods, opcodes, literals, calls, and graphs.
- Reverse-engineering challenges.

#### 2.9 Dependency and Component Identification

- Third-party library detection.
- Library identity versus version identification.
- Reference profiles.
- Candidate generation.
- Similarity and confidence.

#### 2.10 Evidence-Based SBOM Recovery

- Evidence source.
- Evidence provenance.
- Evidence strength.
- Conflicting evidence.
- Uncertainty and ambiguity.
- Relationship to the project's approach.

#### 2.11 Conclusion

Summarize why no single APK signal is sufficient and introduce the AI and
state-of-the-art chapters.

### Main References

Use standards and primary sources wherever possible:

- CycloneDX specification.
- SPDX specification.
- Package URL specification.
- Android developer documentation for APK, DEX, D8, and R8.
- NIST/CISA SBOM guidance.
- NVD, OSV, FIRST CVSS, CISA KEV, and FIRST EPSS documentation.
- Academic Android TPL detection papers from `ressources/papers/`.

### Planned Visuals and Tables

- Android build-to-APK diagram.
- APK internal structure.
- R8 transformation diagram.
- SPDX versus CycloneDX comparison table.
- Evidence-source table.
- Identity versus version decision example.

### Completion Gate

- Every definition is cited.
- Generic textbook explanations are kept concise.
- Every subsection helps explain a later design or evaluation decision.

---

## Chapter 3 - Artificial Intelligence for Component Identification

### Objective

Explain only the ML/DL concepts actually used or evaluated in the project and
make the report-only authority boundary explicit.

### Planned Sections

#### 3.1 Introduction

Explain why deterministic matching remains the production authority and why AI
was studied as assistance for difficult evidence.

#### 3.2 Problem Formulation

- Classification and triage tasks.
- Candidate rows and labels.
- Report-only actions such as suggesting, suppressing uncertainty, or marking
  risk.

#### 3.3 Data and Feature Representations

- Structured matcher/evidence features.
- Source-free safe features.
- Raw opcode sequences.
- Case-level train/test separation.

#### 3.4 Classical Machine Learning

- Random Forest.
- Why it was chosen.
- Input features and labels.
- Macro-F1 and class imbalance.

#### 3.5 Transformer-Based Experiments

- Structured-token Transformer.
- MVP-safe/source-free profile.
- Raw-opcode Transformer.
- Shortcut-learning and leakage risks.

#### 3.6 Evaluation Metrics

- Accuracy.
- Precision and recall.
- Macro, micro, and weighted F1.
- Baselines.
- Confusion matrices.
- Held-out cases.

#### 3.7 Results and Interpretation

Current evidence to refresh during final writing:

- Random Forest report-only result.
- Structured Transformer result and shortcut risk.
- Source-free MVP-safe Transformer result.
- Raw-opcode negative result versus the opcode-count baseline.

#### 3.8 Production Authority and Safety Boundary

- AI may add report assistance.
- AI may not change selected components or versions.
- AI may not alter CycloneDX SBOMs.
- AI may not transform potential CVEs into confirmed findings.
- AI may not alter source-validation metrics.

#### 3.9 Conclusion

Present AI as a bounded supporting experiment, not the central MVP.

### Primary Project Sources

- `docs/project_handbook/implementation/AI_R8_AND_HYBRID.md`
- `docs/evaluation/AI_R8_FINAL_EVALUATION.md`
- `docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md`
- `docs/evaluation/AI_R8_DL_PROTOTYPE_MVP_SAFE.md`
- `docs/evaluation/AI_R8_RAW_OPCODE_TRANSFORMER.md`
- `docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md`

### Planned Visuals and Tables

- AI evidence pipeline.
- Train/test/held-out split diagram.
- Feature-family table.
- Model comparison table.
- Report-only authority boundary diagram.
- Confusion matrix where meaningful.

### Completion Gate

- No AI metric is presented without its split, baseline, and limitations.
- Shortcut-risk results are not advertised as deployment performance.
- The raw-opcode failed experiment remains visible.

---

## Chapter 4 - State of the Art

### Objective

Critically compare existing approaches and establish the research gap addressed
by the MVP.

### Planned Sections

#### 4.1 Introduction

State review scope, paper-selection criteria, and comparison dimensions.

#### 4.2 Evolution of Android TPL Detection

- Package and signature approaches.
- Reference-profile approaches.
- Hash, opcode, API, and structural approaches.
- Graph and multi-scale approaches.
- Learned representations.
- SBOM-oriented work.

#### 4.3 Representative Tools and Research

Cover the paper families already analyzed:

- LibScout.
- LibRadar.
- LibD.
- ORLIS.
- LibPecker.
- ATVHunter.
- LibAttention.
- SAD.
- LibMD.
- LibScope, Libra, LibScan/LibHunter, LIBLOOM.
- Systematic Assessment.
- TPL-Benchmark.
- ObfDetector.
- UniBOM and other relevant SBOM work.

#### 4.4 Comparison Dimensions

- Library-level versus version-level identification.
- Required input.
- Feature families.
- Obfuscation and R8 resilience.
- Dataset realism.
- Evaluation metrics.
- Runtime and scalability.
- SBOM output.
- Vulnerability mapping.
- Availability and reproducibility.

#### 4.5 Comparative Table

Create one readable summary table in the main chapter and move the expanded
table to an appendix.

#### 4.6 Limitations of Existing Approaches

- Unrealistic benchmarks.
- Incomplete R8 evaluation.
- Weak exact-version reliability.
- Reference-database dependence.
- Missing transitive-dependency discussion.
- Limited standard SBOM generation.
- Limited provenance and uncertainty reporting.

#### 4.7 Impact on the Project

For every major research idea, classify the decision as:

- adopted;
- adapted;
- diagnostic only;
- rejected;
- deferred.

#### 4.8 Research Gap and Positioning

Position the project as:

> an end-to-end, evidence-gated Android APK-to-CycloneDX pipeline that combines
> research-backed static signals with explicit confidence, source validation,
> failure reporting, and vulnerability-claim boundaries.

#### 4.9 Conclusion

Transition from the identified gap to the proposed system.

### Primary Project Sources

- `papers/state_of_the_art.md`
- `papers/data/SBOM_Tools_Synthesis_Table.md`
- `papers/data/impact_on_project.md`
- `papers/data/papers_overview.json`
- `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`
- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`

### Planned Visuals and Tables

- Technique taxonomy.
- Timeline or generations of approaches.
- Main comparative table.
- Research-gap diagram.
- Adopt/adapt/reject decision table.

### Completion Gate

- Every performance number is tied to the paper's dataset and metric.
- Reported and realistic benchmark results are not mixed.
- Existing figures are redrawn or clearly marked as adapted.
- The chapter ends with an explicit gap answered by Chapter 5.

---

## Chapter 5 - Proposed Solution and System Design

### Objective

Describe the system conceptually before discussing implementation details.

### Planned Sections

#### 5.1 Introduction

Restate the design goals derived from Chapter 4.

#### 5.2 Requirements

Functional requirements:

- accept an APK;
- extract analyzable evidence;
- detect known Maven components;
- estimate versions and confidence;
- emit CycloneDX;
- query vulnerabilities;
- generate human-readable reports.

Non-functional requirements:

- explainability;
- reproducibility;
- bounded runtime;
- conservative claims;
- isolated experiments;
- auditability.

#### 5.3 Actors and Use Cases

Actors:

- analyst/auditor;
- reference-database maintainer;
- researcher;
- external vulnerability service.

Use cases:

- inspect APK;
- build reference DB;
- match components;
- generate SBOM/report;
- validate against source;
- run an isolated experiment.

#### 5.4 General Architecture

Layers:

1. APK extraction.
2. DEX and metadata analysis.
3. Reference-feature construction.
4. Candidate generation.
5. Evidence fusion and version selection.
6. Confidence and ambiguity.
7. CycloneDX generation.
8. Vulnerability lookup.
9. Reporting and optional AI assistance.

#### 5.5 Dataset and Reference-Database Design

- Maven coordinates and versions.
- JAR/AAR acquisition.
- D8 conversion.
- SQLite feature storage.
- Focused, calibrated, evaluation, and experiment databases.
- Shared DB promotion gates.

#### 5.6 Evidence Model

- Package/class/method evidence.
- Opcodes and opcode tri-grams.
- API/member references.
- Class dependency graph.
- Literals and version-unique evidence.
- POM/dependency coherence.
- Application metadata and contextual evidence.
- Provenance attached to decisions.

#### 5.7 Matching and Version Selection

- Candidate generation.
- Weighted evidence.
- Identity score.
- Version score.
- Exact, likely, ambiguous, or uncertain status.
- Version-band handling.
- Guarded artifact-family logic.

#### 5.8 SBOM and Vulnerability Design

- CycloneDX components and PURLs.
- Evidence/confidence properties.
- Native file components.
- OSV lookup.
- Confirmed, potential, and report-only vulnerability claims.

#### 5.9 AI and Experimental Isolation

- Default deterministic lane.
- Opt-in AI/report-only lane.
- Isolated reference DBs.
- Regression controls and fail-fast policy.

#### 5.10 UML and Behavioral Design

Required diagrams:

- use-case diagram;
- global architecture;
- activity diagram;
- sequence diagram for APK-to-report;
- sequence diagram for reference DB construction;
- component or deployment diagram;
- data model or simplified database schema.

#### 5.11 Conclusion

Transition from design to implementation and evaluation.

### Primary Project Sources

- `docs/architecture/MVP_ARCHITECTURE.md`
- `docs/project_handbook/architecture/END_TO_END_PIPELINE.md`
- `docs/project_handbook/concepts/REFERENCE_DB_AND_GROUND_TRUTH.md`
- `docs/project_handbook/concepts/TPL_MATCHING_FEATURES.md`
- `docs/project_handbook/operations/SAFE_EXPERIMENT_RULES.md`

### Completion Gate

- The architecture is understandable without reading source code.
- Every component has a defined input, output, and responsibility.
- UML diagrams agree with the implemented system.
- Experiment-only paths are visually separated from production decisions.

---

## Chapter 6 - Implementation, Evaluation, and Discussion

### Objective

Prove that the proposed system exists, explain how it works, and evaluate it
with bounded and reproducible claims.

### Planned Sections

#### 6.1 Introduction

Explain the chapter's three parts: implementation, evaluation protocol, and
discussion.

#### 6.2 Development Environment

- Python and major libraries.
- Docker.
- Android build tools and D8.
- SQLite.
- CLI and report outputs.
- Testing environment.

Avoid pages of generic technology logos. Use one concise technology table.

#### 6.3 Implementation by Module

- CLI orchestration.
- APK extractor.
- DEX analyzer.
- Maven downloader and converter.
- Reference-feature database.
- Matcher.
- Confidence and ambiguity model.
- SBOM generator.
- OSV/vulnerability layer.
- Report generator.
- Source validator.
- AI/report-only modules.

For each module:

1. responsibility;
2. inputs and outputs;
3. important algorithm or policy;
4. relevant code files;
5. failure handling.

#### 6.4 User Workflow and Commands

- Minimal end-to-end command sequence.
- Expected output files.
- Meaning of important flags.
- Example APK walkthrough.

The complete command reference can be placed in an appendix and linked to the
project handbook.

#### 6.5 Evaluation Methodology

- Research questions and hypotheses.
- Controlled fixtures.
- Clean real APKs.
- Partial real APKs.
- Boundary and limitation cases.
- Source-validation process.
- Metrics and denominators.
- Regression controls.
- Reproducibility protocol.

#### 6.6 Controlled Results

- Clear fixtures.
- R8 rename.
- Shrink and optimize.
- Repackaging/flattening.
- Multidex and multiple libraries.

#### 6.7 Real-APK Results

Report separately:

- clean source-validated APKs;
- partial source-validated APKs;
- overall emitted-version confirmation rate;
- full source dependency denominator and reference coverage;
- boundary cases excluded from accuracy.

#### 6.8 Source-Known Upper-Bound Lane

- Explain the purpose of the source-version constrained v2 lane.
- Report its results.
- Explicitly state why it is not APK-only production accuracy.
- Present the remaining source-gap taxonomy.

#### 6.9 Vulnerability Demonstration

- Clean real APK example.
- Controlled vulnerable component example.
- Source-version-mismatch example.
- Vulnerability claim strength.

#### 6.10 AI/R8 Results

- Classical ML.
- Transformer experiments.
- Negative raw-opcode result.
- Report-only integration proof.
- Authority gate.

#### 6.11 Failed and Non-Promoted Experiments

Include:

- unsafe newer-version tie-breaking;
- global opcode/API weighting;
- global multi-scale R8 blend;
- version-band reranking failures;
- priority reference DB false-positive expansion;
- Fragment 1.6.2 near-tie experiment;
- AI shortcut and raw-opcode limitations.

For every experiment:

- hypothesis;
- target;
- controls;
- result;
- decision;
- lesson.

#### 6.12 Comparison with Existing Work

Compare only compatible dimensions:

- supported outputs;
- exact-version claims;
- R8 evaluation;
- standard SBOM generation;
- vulnerability mapping;
- evidence transparency;
- realistic dataset limitations.

Do not directly compare percentages from incompatible datasets.

#### 6.13 Discussion

- Answers to research questions.
- Strengths.
- Error categories.
- Reference coverage versus matcher recall.
- Exact-version ambiguity.
- Runtime and scalability.
- Practical value of partial results.

#### 6.14 Threats to Validity

- Internal validity.
- Construct validity.
- External validity.
- Dataset representativeness.
- Source-dependency-tree limitations.
- Reference-database bias.
- Measurement and implementation risks.

#### 6.15 Conclusion

Summarize what the evaluation establishes and what remains unresolved.

### Primary Project Sources

- `src/apk_sbom/`
- `docs/project_handbook/implementation/`
- `docs/project_handbook/commands/`
- `docs/evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md`
- `docs/evaluation/THESIS_EVALUATION_TABLES.md`
- `docs/thesis/FINAL_V2_RESULTS_SECTION.md`
- `docs/thesis/THESIS_ARTIFACT_INDEX.md`
- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`

### Planned Visuals and Tables

- Module implementation map.
- CLI workflow.
- Dataset-role diagram.
- Main controlled and real-APK result tables.
- Reference coverage versus emitted-confirmation diagram.
- Error-category chart.
- V2 gap taxonomy.
- AI model comparison.
- Experiment decision table.
- Dashboard/report screenshots.

### Completion Gate

- Every number is generated or traceable.
- Denominators are visible.
- Controls and exclusions are explained.
- Failed experiments are not hidden.
- Screenshots are readable in print.
- Results answer the Chapter 1 questions.

---

## Chapter 7 - General Conclusion and Perspectives

### Objective

Give a concise synthesis without introducing new experiments.

### Planned Sections

#### 7.1 General Conclusion

- Problem revisited.
- Approach summary.
- Main implementation contribution.
- Main evaluation findings.
- Practical significance.

#### 7.2 Answers to Research Questions

One short subsection or table mapping each question to the established answer.

#### 7.3 Limitations

- Real-world exact-version performance.
- Reference coverage.
- Matcher recall.
- Adjacent-version ambiguity.
- Native code.
- Dynamic/hidden code.
- Runtime for very large reference databases.
- AI authority limitations.

#### 7.4 Future Perspectives

- Safer candidate shortlisting and reranking.
- Better matcher recall.
- Broader reference coverage.
- Native component provenance.
- Dynamic-code analysis.
- Larger realistic benchmarks.
- Calibrated evidence/probability models.
- Knowledge graphs and provenance-aware SBOMs.

#### 7.5 Final Closing

Conclude that the system favors transparent, auditable partial knowledge over
unsupported certainty.

---

## Appendices

Recommended appendices:

- Full command and flag reference.
- Expanded literature comparison table.
- Complete per-APK result table.
- Experiment decision ledger.
- Dataset and proof inventory.
- CycloneDX example.
- JSON evidence example.
- Additional dashboard screenshots.
- Reproducibility checklist.

## Bibliography Plan

- Maintain one shared `.bib` database for PFE and master theses.
- Use a consistent IEEE numeric citation style unless the school template
  requires another style.
- Prioritize papers, standards, and official documentation.
- Avoid using Wikipedia as an academic authority.
- Record DOI, authors, title, venue, year, and URL/access date where relevant.
- Cite the source of every external figure and label redrawn figures as
  “adapted from”.
- Do not cite internal project Markdown files as academic references; use them
  as evidence for writing and point to the repository in appendices where
  appropriate.

## Originality and Anti-Plagiarism Plan

- School reports provide layout and organizational examples only.
- No paragraph will be copied from those reports.
- Definitions will be paraphrased and cited.
- Related-work descriptions will be synthesized from the original papers.
- Existing diagrams will be redrawn when practical.
- Direct quotations will be exceptional, short, and clearly marked.
- Run chapter-level phrase-overlap checks against:
  - the school reports;
  - source papers;
  - web sources used during writing.
- Perform a final manual check for uncited definitions, borrowed structures,
  and suspiciously generic text.

## Recommended Writing Order

The numerical order is not the most efficient writing order. Use:

1. Chapter 5 - Proposed Solution and System Design.
2. Chapter 6 - Implementation, Evaluation, and Discussion.
3. Chapter 4 - State of the Art.
4. Chapter 2 - Technical Background.
5. Chapter 3 - Artificial Intelligence.
6. Chapter 1 - General Introduction.
7. Chapter 7 - General Conclusion.
8. Abstracts, front matter, appendices, and final formatting.

## Work Packages and Review Gates

### PFE-1 - Template and Evidence Freeze

- Create the LaTeX structure.
- Import school front matter.
- Build bibliography and acronym files.
- Refresh generated metrics.
- Freeze the evidence snapshot used for the submitted version.

### PFE-2 - Design and Architecture

- Write Chapter 5.
- Produce architecture, use-case, activity, sequence, and data diagrams.
- Verify every diagram against the implementation.

### PFE-3 - Implementation and Evaluation

- Write Chapter 6.
- Insert generated tables and screenshots.
- Complete research-question answers and validity threats.

### PFE-4 - Research Chapters

- Write Chapters 2, 3, and 4.
- Complete citations and comparison tables.
- Verify adoption/rejection decisions.

### PFE-5 - Framing and Conclusion

- Write Chapters 1 and 7.
- Finalize abstracts and keywords.
- Check that claims remain consistent across all sections.

### PFE-6 - Final QA

- Compile with no missing references.
- Inspect every rendered page.
- Check figure/table readability.
- Run overlap and citation checks.
- Verify glossary and acronyms.
- Verify chapter transitions.
- Export final PDF and archive the exact evidence snapshot.

## Current Writing Checkpoint

This section must be updated at the end of every PFE writing session.

| Field | Current value |
|---|---|
| Plan status | Approved working baseline |
| Active work package | PFE-6 - Final QA |
| Active chapter | Chapter 6 prototype screenshots added; administrative front-matter completion still pending |
| Last approved chapter | None |
| Evidence snapshot | Chapter 6 results are frozen at `docs/thesis/PFE_CHAPTER6_EVIDENCE_SNAPSHOT_2026-06-20.md`; Chapter 3 AI evidence and artifact hashes are frozen at `docs/thesis/PFE_CHAPTER3_AI_EVIDENCE_SNAPSHOT_2026-06-20.md`; refresh the affected chapter if generated artifacts change |
| LaTeX source status | Chapters 1--7, Appendix A, all three abstracts, and all 46 bibliography entries received a full examiner-level source audit on 2026-06-20. Evidence denominators, implementation descriptions, reproducibility paths, academic wording, and selected bibliography metadata were corrected. On 2026-06-21, Chapter 6 was expanded with 13 browser-rendered dashboard panels: six consecutive panels covering the complete clean F-Droid report, three covering the complete controlled vulnerable Jackson report, and four showing report-only R8, hybrid, ML, and DL output. The current PFE source was rebuilt locally with direct MiKTeX LuaLaTeX + Biber passes, producing a 139-page PDF. The dashboard pages and the two-page List of Figures were rendered and visually inspected with no clipping, overlap, or neighboring-section crop artifacts observed |
| Current upload package | `thesis/pfe-overleaf-full-reports-ai-r8-2026-06-21.zip` contains 37 source entries, including `main.tex` at the archive root and the 14 referenced image assets under `figures/`; SHA-256 `3F6B2903A18DD6FF427C99229CBDDD040235EF4F67EF00FCAD8337E6F26326C6`. The current compiled draft is `thesis/PFE_Fendi_Mohamed_compiled_draft_full_reports_2026-06-21.pdf`; SHA-256 `81B89BE5C061931F97ADAA3CCB529BC8097FE1B5E380A8FE5EB0B2DDAA3E63AC` |
| Current blocker | Jury president, examiner, and exact defense date are still required before the title page can be finalized |
| Exact next action | Fill the three remaining administrative values in `thesis/pfe/metadata.tex`, then run one final LuaLaTeX/Biber build and page check before submission/export |

Checkpoint update rules:

- Change `Active chapter` when work moves to another chapter.
- Record only genuinely approved baselines under `Last approved chapter`.
- Never mark the evidence snapshot frozen until generated counts and artifacts
  have been checked.
- Put the smallest executable next step in `Exact next action`.
- Append the supporting detail to
  `docs/thesis/THESIS_WRITING_SESSION_LOG.md`.

## Definition of Done

The PFE thesis is complete when:

- all seven chapters are written and reviewed;
- every external claim has a reference;
- every project result has a traceable artifact;
- all metrics use correct denominators and evidence classes;
- all diagrams match the actual architecture;
- the AI and v2 boundaries are explicit;
- failed experiments and threats to validity are included;
- the rendered PDF follows school conventions and has no visual defects;
- the document passes originality and citation checks.
