# Master Thesis Writing Plan

## Recommended Title

**Towards Trustworthy SBOM Recovery from Compiled Android Applications: An
Evidence-Based Component Attribution Framework**

Suggested French title:

**Vers une reconstruction fiable des SBOM à partir d'applications Android
compilées : un cadre d'attribution des composants fondé sur les preuves**

## Purpose of the Master Thesis

The master thesis is the research-oriented companion to the PFE. It must not
repeat the implementation manual or reproduce the complete PFE evaluation.

Its role is to:

- generalize the lessons learned from the APK-to-SBOM project;
- organize the literature into a clear taxonomy;
- formalize what makes a recovered component claim trustworthy;
- propose an evidence, provenance, confidence, and uncertainty framework;
- use the PFE implementation as a case study and source of empirical
  observations;
- identify open research problems.

The central academic contribution is the **evidence-based component attribution
framework**, not the implementation itself.

## Binding Writing and Resumption Rules

All work on this thesis must follow:

- `docs/thesis/THESIS_WRITING_AND_RESUMPTION_RULES.md`
- `docs/thesis/THESIS_WRITING_SESSION_LOG.md`

Before editing master-thesis content, the writer must read the shared rules,
this plan, the current checkpoint below, and the latest master session-log
entry.

Master-specific binding rules:

1. The master thesis remains research and framework focused.
2. PFE implementation details may appear only when needed to explain a case
   study or motivate a framework requirement.
3. PFE results must be identified as project case-study evidence, not new
   master experiments.
4. The taxonomy must be applied consistently to every selected paper.
5. The literature-review protocol must be recorded before claiming systematic
   coverage.
6. “Trustworthy”, “evidence”, “confidence”, “provenance”, and “uncertainty”
   must receive operational definitions.
7. Confidence levels must not be described as calibrated probabilities without
   empirical calibration.
8. Every framework element must answer an identified research gap.
9. The introduction, body, and conclusion must describe the same contribution;
   removed implementation chapters must not remain promised elsewhere.
10. A chapter is complete only after evidence, citation, structure, overlap,
    and render audits.

## Relationship with the PFE

| PFE thesis | Master thesis |
|---|---|
| Describes the implemented APK-to-SBOM tool. | Generalizes trustworthy SBOM recovery as a research problem. |
| Explains modules, code, commands, and outputs. | Defines evidence, provenance, confidence, and attribution concepts. |
| Evaluates controlled and real APKs in detail. | Uses selected PFE results as motivating observations and a case study. |
| Reports engineering decisions and failures. | Converts those decisions into principles, challenges, and research directions. |
| Answers “What did we build and how well did it work?” | Answers “What should make a recovered SBOM claim trustworthy?” |

Material may be adapted from the PFE background and state of the art, as seen
in the school examples, but it must be reframed around the master research
question and revised to avoid internal contradictions or unnecessary
duplication.

## Central Research Question

> How can heterogeneous evidence extracted from compiled and obfuscated Android
> applications be combined to produce trustworthy SBOM component and version
> claims with explicit provenance, confidence, uncertainty, and validation
> boundaries?

## Supporting Research Questions

1. What evidence sources are available for recovering software components from
   compiled Android APKs?
2. How have existing Android library-detection and binary component-recovery
   approaches combined these sources?
3. Which factors determine evidence strength for identity and exact-version
   attribution?
4. How should conflicting, missing, transformed, or source-dependent evidence
   be represented?
5. What information must accompany a reconstructed SBOM claim for it to be
   auditable and useful in vulnerability management?
6. How can such a framework be evaluated without overstating accuracy?

## Expected Research Contributions

1. A taxonomy of compiled-software component recovery techniques.
2. A taxonomy of APK evidence sources and transformation risks.
3. A model separating identity, version, provenance, and vulnerability-claim
   strength.
4. An evidence hierarchy and fusion framework.
5. A lifecycle for recovered SBOM claims.
6. A validation model separating controlled, source-validated, upper-bound,
   report-only, and limitation evidence.
7. A research agenda for trustworthy Android SBOM reconstruction.

## School Style to Follow

Use the same institutional presentation as the PFE:

- multilingual abstracts;
- contents and lists;
- part divider pages;
- chapter introductions and conclusions;
- academic comparative tables;
- general conclusion and future work;
- bibliography.

The expected body is more compact than the PFE and should resemble the stronger
master example reviewed from the school: background, critical state of the art,
challenges, conceptual contribution, and perspectives.

## Planned Structure

### Front Matter

- Institutional cover.
- Dedication and acknowledgements.
- English abstract.
- French résumé.
- Arabic abstract.
- Keywords.
- Contents.
- Lists of figures, tables, and acronyms.

The abstract should emphasize:

1. the trust problem in reconstructed SBOMs;
2. the Android compiled-artifact context;
3. review/taxonomy methodology;
4. proposed evidence-based framework;
5. use of the PFE as a case study;
6. research implications.

---

## Chapter 1 - General Introduction

### Objective

Frame trustworthy SBOM reconstruction as an academic problem derived from, but
broader than, the implemented PFE.

### Planned Sections

#### 1.1 Context

- Software supply-chain security.
- SBOM adoption and regulatory/industrial interest.
- Source-based versus binary-only transparency.
- Android as a challenging compiled ecosystem.

#### 1.2 Problem Statement

- A generated SBOM is not automatically trustworthy.
- Binary recovery can produce identity errors, wrong versions, missing
  components, artifact-family confusion, and unsupported CVE claims.
- Existing work often reports detection scores without a unified model of
  provenance and claim strength.

#### 1.3 Motivation

- Auditable software transparency.
- Security decisions depend on component and version reliability.
- Need to expose evidence and uncertainty.
- Lessons from real APK evaluation show that exact version, reference coverage,
  matcher recall, and source validation are different dimensions.

#### 1.4 Research Questions

Present the central question and supporting questions.

#### 1.5 Objectives

- Review recovery techniques.
- Develop a taxonomy.
- Identify trust requirements.
- Formalize an evidence-based attribution framework.
- Illustrate it through the PFE case study.
- Define research directions.

#### 1.6 Contributions

List the expected research contributions without claiming a second independent
software implementation.

#### 1.7 Scope

- Compiled Android APKs as the primary domain.
- Maven/JVM and DEX component attribution.
- SBOM reconstruction and vulnerability-management implications.
- Native and dynamic code treated as boundary categories.
- Framework is conceptual and evidence-informed, not a formal proof of
  completeness.

#### 1.8 Thesis Organization

One paragraph per chapter.

### Planned Visuals

- Source-based versus reconstructed SBOM trust gap.
- Research-question map.

### Completion Gate

- The introduction does not promise implementation chapters that are absent.
- Contributions are clearly different from the PFE contributions.
- “Trustworthy” is defined operationally, not used as a vague adjective.

---

## Chapter 2 - Background and Research Methodology

### Objective

Define the concepts used by the framework and explain how the literature and
project evidence were selected and analyzed.

### Planned Sections

#### 2.1 Introduction

Explain the background-to-methodology progression.

#### 2.2 Software Supply Chains and SBOMs

- Supply-chain transparency.
- SBOM content and standards.
- SPDX and CycloneDX.
- Component identity, version, relationships, hashes, and provenance.

#### 2.3 Trust, Evidence, and Provenance

- Trustworthiness.
- Claim and evidence.
- Evidence provenance.
- Confidence and uncertainty.
- Completeness and correctness.
- Reproducibility and auditability.

#### 2.4 Android Compiled-Artifact Context

- APK, DEX, resources, native files.
- Maven artifacts and Gradle dependency graphs.
- Compilation and artifact transformations.
- R8, shrinking, optimization, and obfuscation.

#### 2.5 Software Component Attribution

- Presence detection.
- Library identity.
- Artifact family.
- Exact version.
- Dependency relationship.
- Vulnerability attribution.

#### 2.6 Evidence Sources in APKs

- Package and class names.
- Methods and signatures.
- Opcodes and instruction sequences.
- APIs and call relations.
- Graph structures.
- Literals and resources.
- Build or Maven remnants.
- Native hashes.
- Contextual and app-era evidence.

#### 2.7 Research Methodology

Use a transparent structured-review methodology:

1. Research questions.
2. Search sources and keywords.
3. Inclusion and exclusion criteria.
4. Duplicate removal.
5. Quality assessment.
6. Data-extraction schema.
7. Taxonomy construction.
8. Comparative synthesis.
9. PFE case-study triangulation.

The review need not be mislabeled as a full systematic literature review unless
all protocol requirements are actually completed. “Structured literature
review” or “systematic mapping-inspired review” is safer if the process is
lighter.

#### 2.8 Analysis Dimensions

For every work, extract:

- target artifact;
- detected unit;
- evidence features;
- identity/version capability;
- obfuscation resilience;
- reference dependency;
- dataset;
- evaluation metrics;
- reproducibility;
- SBOM output;
- confidence/provenance treatment;
- limitations.

#### 2.9 Threats to the Review

- Publication bias.
- Incompatible datasets.
- Missing implementations.
- Rapidly evolving Android toolchain.
- Ambiguous definitions of library and version detection.

#### 2.10 Conclusion

Transition from concepts and methodology to the taxonomy.

### Main References

- CycloneDX, SPDX, PURL, NIST, and CISA.
- Android and R8 official documentation.
- Academic TPL, binary analysis, SBOM, provenance, and evidence-fusion research.
- Original papers in `ressources/papers/`.

### Planned Visuals and Tables

- Component-claim hierarchy.
- APK evidence map.
- Review-selection flow diagram.
- Literature data-extraction schema.
- Terminology table.

### Completion Gate

- The review process can be reproduced.
- Trust concepts are tied to observable properties.
- Background does not become a generic Android textbook.

---

## Chapter 3 - State of the Art and Taxonomy

### Objective

Organize existing research by technique and evaluate it through the lens of
trustworthy SBOM recovery.

### Planned Sections

#### 3.1 Introduction

State the review dimensions and taxonomy objective.

#### 3.2 Taxonomy of Component-Recovery Techniques

Proposed top-level categories:

1. Metadata and package-namespace techniques.
2. Hash and signature techniques.
3. API and semantic-feature techniques.
4. Opcode and instruction-sequence techniques.
5. Structural and graph techniques.
6. Multi-scale and evidence-fusion techniques.
7. Machine-learning and representation-learning techniques.
8. Source-assisted and hybrid recovery.
9. SBOM-oriented reconstruction approaches.

#### 3.3 Taxonomy of Evidence Sources

Classify evidence by:

- origin;
- granularity;
- stability under transformation;
- discriminative value;
- version specificity;
- provenance;
- cost;
- source dependence.

#### 3.4 Taxonomy of Transformation Threats

- Identifier renaming.
- Dead-code removal.
- Method inlining and outlining.
- Optimization.
- Package flattening/repackaging.
- Partial inclusion.
- Multidex and split delivery.
- Artifact-family aliases.
- Native code.
- Dynamic or hidden code.

#### 3.5 Representative Research Approaches

Critically synthesize the relevant Android TPL and SBOM literature. Avoid
describing papers as isolated summaries; group them by the taxonomy and compare
their design choices.

#### 3.6 Evaluation Practices

- Controlled libraries.
- Synthetic APKs.
- Open-source APKs.
- Ground-truth construction.
- Library-level and version-level metrics.
- Effects of unrealistic dataset filtering.
- Reference coverage.
- Runtime and scalability.

#### 3.7 Comparative Analysis

Main comparison dimensions:

- detection level;
- input assumptions;
- evidence sources;
- transformation resilience;
- version reliability;
- confidence and provenance;
- standard SBOM support;
- vulnerability integration;
- reproducibility.

#### 3.8 Limitations in Existing Research

- Accuracy without denominator transparency.
- Library presence conflated with exact version.
- Reference DB coverage hidden from matcher performance.
- Limited evidence provenance.
- Confidence scores not calibrated.
- Conflicting evidence not represented.
- CVE claims stronger than component evidence.
- Limited realistic R8 and modern Android evaluation.
- Native and dynamic-code boundaries often ignored.

#### 3.9 Research Gap

State the gap:

> Existing Android component detectors provide valuable identification
> techniques, but the field lacks a unified framework that connects each
> recovered SBOM claim to its provenance, evidence strength, transformation
> risk, uncertainty, validation class, and permitted security interpretation.

#### 3.10 Conclusion

Derive the framework requirements for Chapter 4.

### Primary Project Sources

- `papers/state_of_the_art.md`
- `papers/data/SBOM_Tools_Synthesis_Table.md`
- `papers/data/impact_on_project.md`
- `papers/data/papers_overview.json`
- `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`
- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`

### Planned Visuals and Tables

- Technique taxonomy tree.
- Evidence versus transformation-resilience matrix.
- Evaluation-practice taxonomy.
- Expanded comparative table.
- Research-gap diagram.

### Completion Gate

- Taxonomy categories are mutually understandable and consistently applied.
- Comparisons distinguish reported performance from realistic performance.
- The chapter synthesizes rather than merely listing papers.
- The research gap leads directly to the proposed framework.

---

## Chapter 4 - Proposed Evidence-Based Trust Framework

### Objective

Present the master thesis's principal conceptual contribution.

### Planned Sections

#### 4.1 Introduction

Explain how the framework responds to the gaps identified in Chapter 3.

#### 4.2 Framework Design Principles

Recommended principles:

1. Every claim must expose its evidence.
2. Identity and version claims must be separated.
3. Evidence provenance must be preserved.
4. Missing evidence must not be interpreted as absence.
5. Conflicting evidence must remain visible.
6. Confidence must be bounded by transformation and coverage risks.
7. Vulnerability claims cannot be stronger than component/version evidence.
8. Source-assisted validation must be distinguished from APK-only inference.
9. Report-only assistance must be distinguished from authoritative output.
10. Evaluation denominators and exclusions must be explicit.

#### 4.3 Claim Model

Define a recovered SBOM claim as a structured object containing:

- subject APK;
- component identity candidate;
- artifact family;
- version or version set;
- claim type;
- evidence list;
- provenance;
- evidence coverage;
- transformation risk;
- confidence;
- uncertainty/ambiguity;
- validation class;
- allowed downstream interpretation.

#### 4.4 Evidence Hierarchy

Propose evidence levels, for example:

- **E0 - no component evidence**
- **E1 - weak contextual evidence**
- **E2 - identity-supporting evidence**
- **E3 - multi-source identity evidence**
- **E4 - version-discriminating APK evidence**
- **E5 - externally validated exact evidence**

The final names and thresholds must be justified and should not pretend to be a
universal standard.

#### 4.5 Evidence Quality Dimensions

Score or classify evidence using:

- directness;
- uniqueness;
- independence;
- transformation resilience;
- version specificity;
- provenance reliability;
- reference coverage;
- reproducibility.

#### 4.6 Evidence Fusion

Explain conceptual fusion:

- candidate generation;
- independent evidence families;
- corroboration;
- conflict detection;
- confidence capping;
- ambiguous version sets;
- abstention.

If mathematical notation is introduced, keep it interpretable. A possible
conceptual form is:

```text
claim confidence =
    fused supporting evidence
    × provenance quality
    × reference coverage factor
    × transformation-risk factor
    - conflict penalty
```

This must be described as a framework model unless empirically calibrated
probabilities are available.

#### 4.7 Claim Classes

Recommended classes:

- confirmed exact;
- strongly supported exact;
- likely exact;
- version-band ambiguous;
- identity-only;
- report-only candidate;
- unsupported/abstained;
- boundary/out-of-scope.

#### 4.8 Validation and Evidence Lanes

Formalize:

- controlled ground truth;
- APK-only source-validated output;
- source-known constrained upper bound;
- report-only diagnostic;
- experiment-only result;
- limitation/boundary case.

Explain what each lane may and may not prove.

#### 4.9 Vulnerability-Claim Policy

Map component evidence to security interpretation:

| Component/version evidence | Allowed vulnerability interpretation |
|---|---|
| Externally validated exact | Source-confirmed/confirmed for that evaluation context |
| Strong APK-only exact evidence | High-confidence potential finding |
| Ambiguous version set | Potential finding across affected candidates |
| Identity only | Risk or investigation hint |
| Report-only candidate | Report-only vulnerability suggestion |
| Boundary/unsupported | No package-level CVE claim |

#### 4.10 Recovered Claim Lifecycle

Proposed lifecycle:

1. Evidence extraction.
2. Candidate generation.
3. Attribution.
4. Confidence and ambiguity assessment.
5. SBOM claim emission or abstention.
6. Vulnerability interpretation.
7. External/source validation.
8. Revision as reference evidence grows.

#### 4.11 PFE System as a Case Study

Use selected observations—not the complete PFE evaluation—to demonstrate the
framework:

- controlled exact-version success;
- clean and partial real APK distinction;
- version-band ambiguity;
- reference coverage versus matcher recall;
- source-known upper-bound lane;
- failed DB and reranking promotions;
- Fragment 1.6.2 experiment-only decision;
- native and hidden-code boundaries;
- report-only AI authority.

#### 4.12 Framework Evaluation

Evaluate the framework qualitatively and, where possible, quantitatively:

- Can it represent every major PFE evidence class?
- Does it prevent misleading 100% claims?
- Does it distinguish identity and version?
- Does it constrain vulnerability claims?
- Does it preserve failed experiments and abstentions?
- Can two analysts trace a claim to the same evidence?

Possible evaluation methods:

- scenario walkthroughs;
- mapping of real project cases;
- coverage of known failure categories;
- expert/supervisor review;
- comparison against a naive binary present/absent model.

#### 4.13 Limitations

- Framework derived mainly from Android/Maven evidence.
- Confidence levels are not universally calibrated probabilities.
- PFE case study may introduce design bias.
- Native and dynamic-code attribution remain incomplete.
- Broader validation is future work.

#### 4.14 Research Agenda

- Calibrated probabilistic evidence fusion.
- Provenance-aware SBOM extensions.
- Knowledge graphs.
- Cross-tool evidence exchange.
- Standard confidence vocabularies.
- Native and dynamic component provenance.
- Realistic public benchmark datasets.
- Human-understandable uncertainty.

#### 4.15 Conclusion

Summarize the framework and transition to the general conclusion.

### Primary PFE Case-Study Sources

- `docs/thesis/THESIS_ARTIFACT_INDEX.md`
- `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`
- `docs/evaluation/THESIS_EVALUATION_TABLES.md`
- `docs/thesis/FINAL_V2_RESULTS_SECTION.md`
- `docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md`
- `docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md`
- `docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md`
- `docs/evaluation/LIMITATION_BOUNDARY_DASHBOARD.md`

### Planned Visuals and Tables

- Framework overview.
- Claim object/model.
- Evidence hierarchy.
- Evidence-quality dimensions.
- Claim lifecycle.
- Validation-lane diagram.
- Component-to-vulnerability authority matrix.
- Case-study mapping table.
- Research-agenda map.

### Completion Gate

- The framework is more than a redrawing of the PFE architecture.
- Every framework concept answers a state-of-the-art limitation.
- Case-study examples are correctly scoped.
- Confidence is not presented as probability unless calibrated.
- Vulnerability authority is explicitly bounded.

---

## Chapter 5 - General Conclusion and Future Directions

### Objective

Synthesize the academic contribution and identify the next research steps.

### Planned Sections

#### 5.1 General Conclusion

- Revisit the trust problem.
- Summarize the taxonomy.
- Summarize the framework.
- Explain the significance of explicit provenance and uncertainty.

#### 5.2 Answers to Research Questions

Use a compact question-answer table.

#### 5.3 Main Contributions

- Taxonomy.
- Trust requirements.
- Evidence-based claim model.
- Validation and vulnerability authority model.
- PFE-informed case study.

#### 5.4 Limitations

- Domain scope.
- Review completeness.
- Lack of universal calibration.
- Case-study dependence.
- Native and dynamic-code boundaries.

#### 5.5 Future Research

- Empirical framework calibration.
- Independent tool validation.
- Public benchmark construction.
- Provenance-aware CycloneDX extensions or profiles.
- Knowledge-graph representation.
- Native component attribution.
- Dynamic loading and protected APKs.
- Human factors and explainability.

#### 5.6 Final Closing

Conclude that trustworthy SBOM recovery requires not only detecting components
but also communicating why each claim should be believed and how it may safely
be used.

---

## Appendices

Recommended appendices:

- Literature-review protocol.
- Search strings and selection criteria.
- Full paper-extraction schema.
- Expanded taxonomy.
- Full comparative table.
- Framework claim schema.
- PFE case-study evidence mappings.
- Glossary.

## Bibliography Plan

- Share a curated bibliography database with the PFE.
- Add master-specific references on:
  - evidence fusion;
  - provenance;
  - uncertainty;
  - trustworthy software analysis;
  - SBOM quality and validation;
  - binary software composition analysis;
  - knowledge graphs where relevant.
- Use primary papers and standards.
- Distinguish academic bibliography from official web documentation if the
  school template uses separate bibliography/webography lists.
- Verify DOI, venue, year, authors, and publication status.

## Originality and Reuse Policy

Allowed:

- Reusing factual background researched for the PFE after rewriting it for the
  master question.
- Reusing a limited number of self-created diagrams with a note that they were
  adapted from the PFE project.
- Referencing PFE results as a case study.

Not allowed:

- Copying school reports.
- Copying full PFE chapters without reframing.
- Claiming PFE experiments as new master experiments.
- Leaving implementation promises in the introduction after removing the
  implementation chapters.
- Reusing literature summaries without returning to the original sources.

Required controls:

- Compare master chapters against the PFE draft.
- Rewrite overlapping passages where the master purpose differs.
- Clearly identify PFE-derived case-study evidence.
- Run phrase-overlap and citation checks before submission.

## Recommended Writing Order

1. Chapter 3 - State of the Art and Taxonomy.
2. Chapter 4 - Evidence-Based Trust Framework.
3. Chapter 2 - Background and Research Methodology.
4. Chapter 1 - General Introduction.
5. Chapter 5 - General Conclusion and Future Directions.
6. Abstracts, appendices, and final formatting.

## Work Packages and Review Gates

### MASTER-1 - Topic and Protocol Freeze

- Confirm the final title with the supervisor.
- Freeze the central and supporting research questions.
- Define search strings and inclusion/exclusion criteria.
- Create the paper-extraction spreadsheet or structured dataset.

### MASTER-2 - Taxonomy

- Classify all reviewed papers.
- Build technique, evidence, transformation, and evaluation taxonomies.
- Produce the main comparative table.
- Validate terminology consistency.

### MASTER-3 - Framework

- Define trust principles.
- Define claim schema and evidence hierarchy.
- Define fusion, ambiguity, abstention, and vulnerability policies.
- Map framework elements to identified research gaps.

### MASTER-4 - PFE Case Study

- Select representative PFE evidence.
- Map cases to framework concepts.
- Exclude irrelevant implementation detail.
- Verify all case-study metrics against current artifacts.

### MASTER-5 - Framing and Synthesis

- Write background/methodology.
- Write introduction and conclusion.
- Complete research-question answers.
- Add limitations and future research.

### MASTER-6 - Final QA

- Check consistency with the final PFE.
- Ensure the master has an independent academic contribution.
- Run citation and overlap checks.
- Compile and inspect every rendered page.
- Verify tables, taxonomies, and framework diagrams.
- Export final PDF.

## Current Writing Checkpoint

This section must be updated at the end of every master-thesis writing session.

| Field | Current value |
|---|---|
| Plan status | Evidence-review revision complete; supervisor/admin review remains |
| Active work package | MASTER-6 - Final QA / supervisor and front-matter approval |
| Active chapter | Whole-thesis evidence review completed; administrative finalization remains |
| Last approved chapter | Chapters 1--5 and Appendix A are internally reviewed after source correction, framework-evaluation, citation, build, and render audits |
| Topic status | Recommended title remains provisional; supervisor approval is still required |
| Review protocol | Version 1.0b: 15 Tier A full texts, five Tier B records, completed per-study quality scores, and logged TPL-Benchmark/UniBOM promotions |
| LaTeX source status | Standalone multilingual project rebuilt with LuaLaTeX and Biber as a visually inspected 74-page evidence-review checkpoint on 2026-06-21 |
| Current blocker | Supervisor approval of the provisional title and research questions remains; the jury names and defense/submission date were filled on 2026-07-06; five Tier B records remain supplementary only |
| Exact next action | Send the current evidence-review PDF to the supervisor, obtain title/RQ approval, then regenerate the final source ZIP if required |

Checkpoint update rules:

- Record changes to the approved title or research questions immediately.
- Do not begin the final taxonomy until inclusion/exclusion and extraction
  criteria are recorded.
- Mark a chapter approved only after checking overlap with the PFE.
- Put the smallest executable next step in `Exact next action`.
- Append the supporting detail to
  `docs/thesis/THESIS_WRITING_SESSION_LOG.md`.

## Definition of Done

The master thesis is complete when:

- its title and research questions are approved;
- the review methodology is transparent;
- the taxonomy is consistently applied;
- the proposed framework directly answers identified research gaps;
- the PFE is used only as a bounded case study;
- no implementation or experimental claims are promised without corresponding
  chapters;
- every external claim is referenced;
- overlap with the PFE and school reports has been reviewed;
- the rendered PDF follows school conventions;
- the conclusion answers every research question and states limitations
  honestly.
