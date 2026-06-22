# Thesis Writing Session Log

## Purpose

This append-only log allows thesis work to resume reliably after a new thread,
context compaction, interruption, or handoff.

The binding process is defined in:

- `docs/thesis/THESIS_WRITING_AND_RESUMPTION_RULES.md`
- `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
- `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`

## Entry Template

Copy this template for each writing session:

```markdown
## YYYY-MM-DD - PFE or Master - Short session title

- Objective:
- Chapter/subsection:
- Status before:
- Work completed:
- Files changed:
- Project evidence used:
- Academic references added or verified:
- Figures/tables created:
- Checks performed:
- Decisions made:
- Unresolved items:
- Exact next action:
```

## 2026-06-19 - Shared - Writing plans and operating rules

- Objective: Establish separate durable plans and resumption rules for the PFE
  and master theses.
- Chapter/subsection: Planning and governance.
- Status before: Project evidence and earlier report drafts existed, but no
  agreed document-specific writing plans or durable resume protocol existed.
- Work completed: Created the PFE plan, master plan, shared writing rules, and
  this append-only session log.
- Files changed:
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_AND_RESUMPTION_RULES.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
- Project evidence used: Current thesis artifact index, report-readiness
  package, project handbook, architecture, experiment ledger, evaluation
  chapter, and state-of-the-art data.
- Academic references added or verified: None; this session planned the
  reference workflow.
- Figures/tables created: Planning tables only.
- Checks performed: Plan structures, referenced project paths, Markdown
  formatting, and PFE/master scope separation.
- Decisions made: The PFE uses seven chapters and remains
  implementation/evaluation focused. The master uses five chapters and centers
  on an evidence-based trustworthy SBOM attribution framework.
- Unresolved items: Final thesis language, university LaTeX template, personal
  cover information, and supervisor approval of the master title.
- Exact next action: Create the shared LaTeX workspace and bibliography
  structure, then begin the PFE with Chapter 5, Proposed Solution and System
  Design.

## 2026-06-19 - Shared - School LaTeX template adaptation

- Objective: Adapt the supplied school PFE and master LaTeX source into clean,
  independently buildable projects following the approved thesis plans.
- Chapter/subsection: PFE Chapter 5 initial design draft; master Chapter 4
  initial framework draft; shared front matter and build structure.
- Status before: Writing plans existed, but no final LaTeX source projects had
  been created.
- Work completed:
  - Inspected `togive.zip` without modifying the original archive.
  - Identified separate engineering and master projects, multilingual front
    matter, preambles, Biber bibliographies, and the school logo.
  - Created standalone `thesis/pfe/` and `thesis/master/` projects.
  - Replaced the original web-security topic, macros, chapters, and references
    with project-specific material.
  - Added complete chapter skeletons matching the approved seven-chapter PFE
    and five-chapter master structures.
  - Drafted the PFE architecture/evidence design and the master
    evidence-based trust framework.
- Files changed:
  - `thesis/README.md`
  - `thesis/pfe/`
  - `thesis/master/`
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
- Project evidence used: PFE and master writing plans, project architecture,
  current thesis abstract/results draft, handbook, and school template source.
- Academic references added or verified: CycloneDX, SPDX, Package URL, Android
  R8 documentation, and LibScout.
- Figures/tables created:
  - PFE high-level APK-to-SBOM architecture.
  - PFE evidence-family table.
  - Master framework overview.
  - Master evidence-hierarchy table.
- Checks performed: Archive structure inspection, standalone include-path
  review, bibliography wiring, chapter-structure comparison, and source-file
  consistency checks.
- Decisions made:
  - Keep both projects independently uploadable to Overleaf.
  - Use LuaLaTeX and Biber, matching the supplied project settings.
  - Reuse only school layout conventions and binary logo; do not reuse the
    original thesis prose or domain-specific macros.
  - Start in English while retaining French and Arabic front-matter slots.
- Unresolved items:
  - Student, supervisor, jury, and defense-date metadata.
  - Final French and Arabic abstracts.
  - Supervisor approval of the master title.
  - Local compilation is unavailable because no TeX distribution is installed.
- Exact next action: Compile both projects in Overleaf or an installed TeX
  environment, visually inspect the front matter and diagrams, then complete
  the remaining PFE Chapter 5 diagrams.

## 2026-06-19 - PFE - Chapter 5 behavioral and deployment design

- Objective: Complete the UML-style and behavioral views required for PFE
  Chapter 5 and verify that they reflect the implemented MVP rather than an
  aspirational architecture.
- Chapter/subsection: Chapter 5, Actors and Use Cases; APK-to-Report Activity;
  runtime and reference-construction sequences; component/deployment view;
  reference-database data model.
- Status before: The chapter contained the high-level architecture and
  evidence-family table, but the remaining diagrams were represented by one
  placeholder.
- Work completed:
  - Audited the extractor, DEX analyzer, matcher, report orchestrator,
    CycloneDX generator, OSV client, reference conversion pipeline, and SQLite
    schema.
  - Added an actor/use-case view for analysts, database maintainers,
    researchers, source validation, and the external vulnerability service.
  - Added the conservative APK-to-report activity flow, including ambiguity,
    abstention, native-file handling, and offline OSV behavior.
  - Added separate sequence diagrams for runtime APK analysis and Maven
    reference-database construction.
  - Added a component/deployment view distinguishing the authoritative MVP
    path from dashed report-only AI/R8 and isolated-database experiments.
  - Added a simplified physical schema using the implementation's actual
    SQLite table names and `component_id` relationships.
  - Removed the Chapter 5 diagram placeholder and added explanatory prose
    before and after each figure.
- Files changed:
  - `thesis/pfe/chapters/ch05_solution_and_design.tex`
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
- Project evidence used:
  - `docs/architecture/MVP_ARCHITECTURE.md`
  - `docs/project_handbook/architecture/END_TO_END_PIPELINE.md`
  - `docs/project_handbook/implementation/EXTRACTOR_AND_DEX_ANALYZER.md`
  - `docs/project_handbook/implementation/REFERENCE_DB_PIPELINE.md`
  - `docs/project_handbook/implementation/MATCHER_AND_VERSION_SELECTION.md`
  - `docs/project_handbook/implementation/SBOM_REPORT_AND_VULNERABILITIES.md`
  - `docs/project_handbook/implementation/SOURCE_VALIDATION.md`
  - `docs/project_handbook/implementation/AI_R8_AND_HYBRID.md`
  - `src/apk_sbom/cli.py`, `apk_extractor.py`, `dex_analyzer.py`,
    `reference_features.py`, `matcher.py`, `sbom.py`, `vulnerability.py`, and
    `report.py`
- Academic references added or verified: None; this session documented the
  implemented design using project-primary evidence.
- Figures/tables created:
  - Actor and use-case diagram.
  - APK-to-report activity diagram.
  - APK-to-report interaction sequence.
  - Reference-database construction sequence.
  - Component and deployment diagram.
  - Simplified SQLite reference-feature schema.
- Checks performed:
  - Confirmed seven matched `figure` and `tikzpicture` environments in Chapter
    5, seven unique figure labels, zero Chapter 5 placeholders, and balanced
    braces.
  - Checked all 21 PFE TeX files for missing `input` targets, bibliography
    files, citation keys, duplicate labels, unresolved references, and the
    school logo; the static check passed.
  - Reconfirmed that `latexmk`, LuaLaTeX, XeLaTeX, Biber, ChkTeX, and Lacheck
    are unavailable locally.
- Decisions made:
  - Use actual schema table names but group the child tables by role so the
    figure remains readable.
  - Show AI/R8 diagnostics and isolated databases as dashed, non-authoritative
    paths.
  - Keep Chapter 5 unapproved until the generated PDF has been visually
    inspected.
- Unresolved items:
  - Compile with LuaLaTeX and Biber in Overleaf or an installed TeX
    environment.
  - Inspect diagram scaling, page breaks, captions, and line crossings in the
    rendered PDF.
- Exact next action: Compile the PFE in Overleaf, visually inspect all seven
  Chapter 5 figures, correct any layout defects, then approve Chapter 5 and
  refresh the Chapter 6 evidence snapshot.

## 2026-06-20 - PFE - Chapter 6 implementation and evaluation draft

- Objective: Freeze the current evidence baseline and replace the Chapter 6
  skeleton with an implementation-faithful, denominator-safe thesis draft.
- Chapter/subsection: Chapter 6, complete source draft from development
  environment through threats to validity and conclusion.
- Status before: Chapter 5 source diagrams were complete but unrendered.
  Chapter 6 contained headings only, and the evidence snapshot had not been
  frozen for LaTeX writing.
- Work completed:
  - Regenerated the thesis evaluation tables and thesis artifact index.
  - Reconciled the normal emitted-version metric, the full source dependency
    denominator, the source-known v2 lane, vulnerability evidence, AI/R8
    results, and failed experiments.
  - Added a dated Chapter 6 evidence snapshot with metric definitions,
    permitted interpretations, artifact paths, and stale-document warnings.
  - Audited the current Python/Docker/Android/SQLite implementation
    environment, module responsibilities, matcher weights, CLI commands, and
    reference-database workflow.
  - Replaced the Chapter 6 skeleton with complete prose covering
    implementation, commands, evaluation methodology, controlled results,
    clean/partial real results, full-denominator coverage, v2 upper-bound
    recognition, vulnerability demonstrations, AI/R8 results, rejected
    experiments, dimensional comparison, discussion, and validity threats.
  - Kept `927/1837` explicitly labeled as emitted Maven version confirmation
    and `927/12082` as end-to-end exact source recall.
  - Kept `6772/6772` explicitly constrained to the source-known v2 upper-bound
    lane.
- Files changed:
  - `thesis/pfe/chapters/ch06_implementation_evaluation.tex`
  - `thesis/pfe-overleaf.zip`
  - `thesis/README.md`
  - `docs/thesis/PFE_CHAPTER6_EVIDENCE_SNAPSHOT_2026-06-20.md`
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
  - regenerated `docs/evaluation/THESIS_EVALUATION_TABLES.md`
  - regenerated `docs/thesis/THESIS_ARTIFACT_INDEX.md`
- Project evidence used:
  - generated thesis evaluation and artifact-index JSON;
  - coverage-first and v2 source-version dashboards;
  - AI/R8 final evaluation and integration gate;
  - OSV source-validation triage;
  - wrong-version, priority-DB, multi-scale R8, and version-band promotion
    diagnostics;
  - current implementation, command handbook, `pyproject.toml`, Dockerfile,
    and test suite.
- Academic references added or verified: No new bibliography keys were
  required in this session. The chapter cites the existing CycloneDX
  specification and defers detector-method citations to Chapters 3 and 4.
- Figures/tables created:
  - Development environment table.
  - Implementation module map.
  - Matcher-weight table and scoring equation.
  - Core-command table and command listings.
  - Evidence-layer and metric definitions.
  - Controlled category results.
  - Main real-APK results and full-denominator coverage tables.
  - V2, vulnerability, AI/R8, failed-experiment, and dimensional-comparison
    tables.
- Checks performed:
  - `.venv\Scripts\python.exe -m pytest -q`: 275 passed in 34.64 seconds.
  - `python -m compileall -q src scripts tests`: passed.
  - Thesis evaluation table and artifact-index regeneration: passed.
  - All 21 PFE TeX files: no missing inputs, citation keys, duplicate labels,
    or unresolved references.
  - Chapter 6: 15 sections, 24 subsections, 13 balanced tables, 4 balanced
    equations, 2 balanced listings, balanced braces, and zero placeholders.
  - `git diff --check`: passed.
  - Overleaf ZIP verification: 25 entries, `main.tex` at the archive root,
    bibliography present, Chapters 5 and 6 present, and no backslash-separated
    ZIP entry names.
- Decisions made:
  - Treat generated JSON and dashboards as authoritative over historical
    narrative documents.
  - Keep Chapter 5 and Chapter 6 unapproved until their rendered pages are
    visually inspected.
  - Use dimension-based comparison in Chapter 6 and leave detailed
    paper-by-paper citations to Chapter 4.
- Unresolved items:
  - Compile the document with LuaLaTeX and Biber.
  - Inspect Chapter 5 diagrams and Chapter 6 wide tables, equations, listings,
    captions, and page breaks in the generated PDF.
  - Select and insert final printable report/dashboard screenshots if they add
    evidence not already communicated by tables.
- Exact next action: Compile the PFE in Overleaf, visually inspect Chapters 5
  and 6, correct layout defects, then begin Chapter 4 from the verified
  state-of-the-art paper data.

## 2026-06-20 - PFE - Chapter 4 state-of-the-art draft

- Objective: Replace the Chapter 4 skeleton with a source-verified,
  synthesis-oriented state of the art that explains the project's technical
  choices without ranking incompatible paper results.
- Chapter/subsection: Chapter 4, complete source draft from review scope and
  technique evolution through comparative analysis, limitations, project
  decisions, research gap, and conclusion.
- Status before: Chapters 5 and 6 had complete but unrendered source drafts.
  Chapter 4 was a short skeleton, and the PFE bibliography did not yet contain
  the detector papers needed for the comparative review.
- Work completed:
  - Audited the PFE Chapter 4 plan, structured paper data, state-of-the-art
    synthesis, paper-to-implementation traceability, experiment-decision
    ledger, and original local paper PDFs.
  - Verified paper metadata and quantitative claims against original papers
    or primary publication pages where available.
  - Corrected the distinction between the 2018 LibPecker paper and the 2020
    systematic tool-assessment paper.
  - Replaced the Chapter 4 skeleton with complete academic prose organized by
    technique families rather than a sequence of isolated paper summaries.
  - Added a technique-evolution diagram, a capability-oriented comparison
    table, and an adopt/adapt/reject decision table tied to the implemented
    MVP.
  - Kept reported results in their original evaluation context and explicitly
    rejected a universal ranking across incompatible datasets.
  - Avoided unverified quantitative claims for tools whose primary
    publication metadata was not independently accessible.
  - Added and verified the bibliography entries required by the chapter.
  - Built a non-destructive, versioned Overleaf upload package because the
    sandbox refused to overwrite the earlier ZIP after its approval quota was
    exhausted.
- Files changed:
  - `thesis/pfe/chapters/ch04_state_of_the_art.tex`
  - `thesis/pfe/bib/references.bib`
  - `thesis/pfe-overleaf-ch04-2026-06-20.zip`
  - `thesis/README.md`
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
- Project evidence used:
  - `papers/data/papers_overview.json`
  - `papers/data/SBOM_Tools_Synthesis_Table.md`
  - `papers/state_of_the_art.md`
  - `papers/data/impact_on_project.md`
  - `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`
  - `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`
  - original PDFs under `ressources/papers/`
- Academic references added or verified:
  - LibScout, LibD, ORLIS, LibPecker, LibID, the 2020 automated-tool
    assessment, the 2021 systematic assessment, ATVHunter, LibScan,
    LibHunter, LibAttention, SAD, TPL-Benchmark, UniBOM, and the public
    LibScope artifact.
- Figures/tables created:
  - Timeline of Android third-party-library identification techniques.
  - Capability-oriented comparison of representative approaches.
  - Research-idea disposition table documenting adopted, adapted, and
    rejected project choices.
- Checks performed:
  - All 21 PFE TeX files: 20 bibliography records, 19 used citation keys, zero
    missing citations, 35 labels, zero duplicate labels, 20 references, and
    zero unresolved references.
  - Chapter 4: 21,928 characters, 11 sections, 7 subsections, balanced braces,
    one balanced figure/TikZ environment, two balanced tables/tabularx
    environments, and balanced itemize/enumerate environments.
  - The apparent placeholder search hit was ordinary explanatory prose; no
    `TODO`, `TBD`, `FIXME`, `[REF]`, or unfinished section marker remains.
  - Exact 12-word overlap check against the 13 locally available source PDFs:
    zero matches.
  - `git diff --check`: passed.
  - Versioned Overleaf ZIP: 25 entries, `main.tex` at the archive root,
    bibliography and Chapters 4--6 present, and zero backslash-separated
    entry names.
- Decisions made:
  - Keep Chapter 4 unapproved until the generated PDF is visually inspected.
  - Present literature by evidence and technique families, not by a
    paper-by-paper performance leaderboard.
  - Treat primary-paper percentages as reported results within their own
    datasets and use TPL-Benchmark as realistic cross-tool evidence.
  - Keep unverified LibMD and ObfDetector details out of quantitative claims.
  - Retain the old Chapter 6 ZIP and publish the current Chapter 4 package
    under a versioned filename instead of destructively replacing it.
- Unresolved items:
  - Compile the PFE with LuaLaTeX and Biber.
  - Inspect the Chapter 4 timeline and wide tables, the seven Chapter 5
    diagrams, and the Chapter 6 tables/listings/page breaks in the rendered
    PDF.
  - Resolve final cover-page metadata and multilingual front matter later in
    the planned sequence.
- Exact next action: Begin Chapter 2 by auditing the verified standards,
  Android architecture/build/package, APK/DEX, reverse-engineering,
  dependency-identification, and evidence-recovery sources. Compile and
  visually inspect Chapters 4--6 when Overleaf or a local TeX environment
  becomes available.

## 2026-06-20 - PFE - Chapter 2 technical-background draft

- Objective: Replace the Chapter 2 skeleton with a concise but complete
  technical foundation that connects software supply-chain risk to
  evidence-based SBOM recovery from compiled Android APKs.
- Chapter/subsection: Chapter 2, complete source draft covering supply-chain
  security, SBOMs and standards, vulnerability terminology, the Android
  ecosystem, APK/DEX structure, D8/R8, static reverse engineering,
  library/version identification, and evidence-based recovery.
- Status before: Chapters 4--6 had complete source drafts. Chapter 2
  contained section headings and several introductory paragraphs but did not
  yet provide the definitions, diagrams, comparison tables, or evidence
  model required by the plan.
- Work completed:
  - Audited the Chapter 2 plan, current skeleton, project handbook concepts,
    architecture documents, implementation terminology, macros, and acronym
    list.
  - Verified definitions and technical descriptions against primary NIST,
    NTIA, CycloneDX, SPDX, Package URL, CVE, CWE, NVD, FIRST, CISA, OSV,
    Android, Gradle, and OWASP sources.
  - Replaced the Chapter 2 skeleton with a complete 11-section narrative
    progressing from software supply chains to compiled-artifact evidence.
  - Distinguished source dependency graphs, build-generated SBOMs, and
    binary-recovered SBOM observations.
  - Explained why component identity, exact version, vulnerability mapping,
    reachability, and exploitability are separate claims.
  - Added Android build, APK structure, multidex, native ABI, dynamic-code,
    D8, R8, reverse-engineering, reference-profile, similarity, confidence,
    conflict, and abstention concepts.
  - Extended the glossary with AAB, AAR, ABI, ART, CWE, JAR, and JVM.
  - Extended the PFE bibliography with the primary technical and standards
    references required by the chapter.
  - Built and verified a new non-destructive Overleaf checkpoint package.
- Files changed:
  - `thesis/pfe/chapters/ch02_technical_background.tex`
  - `thesis/pfe/bib/references.bib`
  - `thesis/pfe/frontmatter/acronyms.tex`
  - `thesis/pfe-overleaf-ch02-2026-06-20.zip`
  - `thesis/README.md`
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
- Project evidence used:
  - `docs/project_handbook/concepts/APK_DEX_ANDROID_BASICS.md`
  - `docs/project_handbook/concepts/SBOM_CYCLONEDX_CVE.md`
  - `docs/project_handbook/concepts/R8_AND_UNCERTAINTY.md`
  - `docs/project_handbook/concepts/TPL_MATCHING_FEATURES.md`
  - `docs/project_handbook/architecture/END_TO_END_PIPELINE.md`
  - `docs/architecture/MVP_ARCHITECTURE.md`
  - implementation handbooks for extraction, matching, reference
    construction, SBOM generation, vulnerability lookup, and source
    validation.
- Academic and standards references added or verified:
  - NIST SP 800-161 Revision 1 and the NTIA SBOM guidance;
  - CycloneDX, SPDX, and Package URL specifications;
  - CVE, CWE, NVD, CVSS, EPSS, CISA KEV, and OSV documentation;
  - Android build, AAR, APK Analyzer, manifest, multidex, D8, R8, signing,
    ABI, and dynamic-code documentation;
  - Gradle variant-aware dependency resolution and OWASP Android
    static/reverse-engineering guidance.
- Figures/tables created:
  - APK internal evidence structure.
  - Simplified Android build-to-APK pipeline.
  - R8 transformation-to-evidence impact diagram.
  - SPDX versus CycloneDX comparison.
  - Vulnerability terminology table.
  - Identity-versus-version decision examples.
  - Static APK evidence-source and failure-mode table.
- Checks performed:
  - All 21 PFE TeX files: 42 bibliography records, 42 used citation keys,
    zero missing citations, 42 labels, zero duplicate labels, 28 references,
    and zero unresolved references.
  - Chapter 2: 40,285 characters, 11 sections, 28 subsections, balanced
    braces, three balanced figure/TikZ environments, four balanced
    table/tabularx environments, nine balanced itemize environments, zero
    placeholders, and zero non-ASCII characters.
  - Exact 12-word overlap check against 15 local research-paper and
    school-report PDFs: zero matches and zero extraction failures.
  - `git diff --check`: passed.
  - Versioned Overleaf ZIP: 25 entries, `main.tex` at the archive root,
    bibliography and Chapters 2 and 4--6 present, and zero
    backslash-separated entry names.
  - ZIP SHA-256:
    `62E8EC6F66FF960889C5266C8ADC7767571AD0330C7EA8425EABBD4C1CF33D2B`.
- Decisions made:
  - Keep generic textbook material brief and connect every subsection to a
    later design, implementation, or evaluation decision.
  - Treat an APK-derived SBOM as an evidence-backed observation of the
    delivered binary, not as a reconstructed original Gradle manifest.
  - Separate component identity, exact version, affected-range membership,
    exploitability, and operational priority.
  - Present abstention and reference absence as valid evidence outcomes.
  - Keep Chapter 2 unapproved until its diagrams, tables, page breaks, and
    references are visually inspected in a compiled PDF.
- Unresolved items:
  - Compile the PFE with LuaLaTeX and Biber.
  - Inspect Chapter 2's four wide tables and three diagrams together with the
    previously pending Chapter 4--6 pages.
  - Finalize front-matter metadata and translated abstracts later in the
    planned writing sequence.
- Exact next action: Freeze the generated AI evidence and draft Chapter 3
  around the grouped case split, RandomForest, structured and MVP-safe
  Transformers, raw-opcode negative result, baselines, shortcut risks, and
  report-only authority boundary.

## 2026-06-20 - PFE - Chapter 3 artificial-intelligence draft

- Objective: Replace the Chapter 3 skeleton with an implementation-faithful
  account of the project's ML/DL contribution while making shortcut risk,
  negative evidence, and the report-only authority boundary explicit.
- Chapter/subsection: Chapter 3, complete source draft from problem
  formulation and data representations through Random Forest, Transformer
  experiments, metrics, results, integration guardrails, validity threats,
  and conclusion.
- Status before: Chapters 2 and 4--6 had complete source drafts. Chapter 3
  contained headings and two authority-boundary paragraphs but did not yet
  document the dataset, split, features, algorithms, baselines, results, or
  failed experiment.
- Work completed:
  - Audited the Chapter 3 plan, writing rules, current checkpoint, existing
    skeleton, AI/R8 implementation modules, training scripts, generated
    corpora, model metrics, integration gate, report-only smoke test, and
    Chapter 6 summary.
  - Verified that the structured split groups rows by `case_id` before
    assigning train, validation, and test partitions.
  - Verified that the full structured Transformer receives raw coordinate,
    source-version, candidate-version, source-rank, role, and diagnostic
    context tokens that can act as shortcuts.
  - Verified the exact feature exclusions used by the MVP-safe Transformer.
  - Verified that the raw-opcode test holds out one APK case per label and
    that the Transformer does not beat the opcode-count logistic-regression
    baseline.
  - Added a dated Chapter 3 evidence snapshot containing metric definitions,
    permitted claims, limitations, model results, split counts, authority
    decisions, and SHA-256 hashes for all source artifacts.
  - Added verified academic references for Random Forests, Transformers,
    shortcut learning, and multiclass evaluation metrics.
  - Replaced the Chapter 3 skeleton with a complete 11-section academic
    narrative focused only on methods actually implemented or evaluated.
  - Added AI, DL, and MVP to the acronym list.
  - Built and verified a new non-destructive Overleaf checkpoint package.
- Files changed:
  - `thesis/pfe/chapters/ch03_artificial_intelligence.tex`
  - `thesis/pfe/bib/references.bib`
  - `thesis/pfe/frontmatter/acronyms.tex`
  - `thesis/pfe-overleaf-ch03-2026-06-20.zip`
  - `thesis/README.md`
  - `docs/thesis/PFE_CHAPTER3_AI_EVIDENCE_SNAPSHOT_2026-06-20.md`
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
- Generated project evidence used:
  - `data/results/experiments/ai-r8-assistant/training-dataset.json`
  - `data/results/experiments/ai-r8-assistant/metrics.json`
  - `data/results/experiments/ai-r8-dl-prototype/token-corpus.json`
  - `data/results/experiments/ai-r8-dl-prototype/token-corpus-mvp-safe.json`
  - `data/results/experiments/ai-r8-dl-prototype/metrics.json`
  - `data/results/experiments/ai-r8-dl-prototype/metrics-mvp-safe.json`
  - `data/results/experiments/ai-r8-raw-opcode-prototype/raw-opcode-corpus.json`
  - `data/results/experiments/ai-r8-raw-opcode-prototype/metrics.json`
  - `data/results/experiments/ai-r8-independent-corpus/independent-corpus.json`
  - `data/results/evaluation/ai-r8-mvp-integration-gate.json`
  - `data/results/evaluation/final-hybrid-ai-demo-smoke.json`
- Academic references added or verified:
  - Breiman's Random Forests;
  - Vaswani et al.'s Transformer architecture;
  - Geirhos et al.'s shortcut-learning analysis;
  - Sokolova and Lapalme's classification-metric analysis.
- Figures/tables created:
  - AI evidence pipeline and authority separation.
  - Case-grouped structured train/validation/test split.
  - Production authority-boundary diagram.
  - Triage-label and structured-feature-family tables.
  - Structured-split, Random Forest ablation, raw-opcode baseline, model
    comparison, per-class result, and authority-matrix tables.
- Checks performed:
  - All 21 PFE TeX files: 46 bibliography records, 46 used citation keys,
    zero missing citations, 53 labels, zero duplicate labels, 40 references,
    and zero unresolved references.
  - Chapter 3: 40,948 characters, 11 sections, 31 subsections, balanced
    braces, three balanced figure/TikZ environments, eight balanced
    table/tabularx environments, 17 balanced itemize environments, three
    balanced enumerate environments, zero placeholders, and zero non-ASCII
    characters.
  - Exact 12-word overlap check against 15 local research-paper and
    school-report PDFs: zero matches and zero extraction failures.
  - Cross-chapter exact-phrase inspection found no prose overlap; the only
    matches were repeated TikZ style declarations.
  - `git diff --check`: passed.
  - Versioned Overleaf ZIP: 25 entries, `main.tex` at the archive root,
    bibliography and Chapters 2--6 present, and zero backslash-separated
    entry names.
  - ZIP SHA-256:
    `61C142DCE1A8DC6C673FF65B692F7410429CC3E52B0C927BCFEB17233493738E`.
- Decisions made:
  - Treat the 0.977 full-profile Transformer result as workflow/research
    evidence, not deployment performance, because shortcut-prone source and
    diagnostic tokens are present.
  - Present the 0.882 MVP-safe result as the more defensible report-only
    structured-token result while retaining its project-derived-data limit.
  - Preserve the raw-opcode Transformer result of 0.110 macro-F1 below the
    0.128 logistic-regression baseline as a failed experiment.
  - Report the Random Forest's weak risk/mismatch classes rather than
    advertising only its 0.708 aggregate macro-F1.
  - Keep learned models blocked from component, version, CycloneDX,
    vulnerability, and source-validation authority.
  - Keep Chapter 3 unapproved until its diagrams, wide tables, equations,
    citations, and page breaks are visually inspected in a compiled PDF.
- Unresolved items:
  - Compile the PFE with LuaLaTeX and Biber.
  - Inspect Chapter 3's three diagrams, eight tables, and metric equations
    together with the previously pending Chapters 2 and 4--6 pages.
  - A truly external AI corpus and independently reviewed labels remain
    future work, not current evidence.
- Exact next action: Audit the current Chapter 1 skeleton against completed
  Chapters 2--6, then write the general context, problem statement,
  motivation, research questions, objectives, contributions, scope,
  methodology overview, and thesis organization without duplicating later
  chapters.

## 2026-06-20 - PFE - Chapter 1 general-introduction draft

- Objective: Replace the Chapter 1 skeleton with a concise general
  introduction that frames the APK-only SBOM problem, aligns the research
  questions with Chapter 6, and maps the project objectives and contributions
  without prematurely repeating evaluation results.
- Chapter/subsection: Chapter 1, complete source draft covering context,
  problem statement, motivation, research questions, objectives, methodology,
  contributions, scope, thesis organization, and conclusion.
- Status before: Chapters 2--6 had complete source drafts. Chapter 1 contained
  a short seven-section skeleton with four research questions but lacked
  citations, diagrams, methodology, explicit contribution mapping, and a
  chapter conclusion.
- Work completed:
  - Audited the Chapter 1 plan, checkpoint, completed Chapters 2--6, frozen
    Chapter 3 and Chapter 6 evidence, project goals, architecture decisions,
    paper-to-implementation traceability, and experiment-decision ledger.
  - Verified that Chapter 6 operationalizes and answers four research
    questions, then copied those four questions exactly into Chapter 1 rather
    than introducing an unmatched fifth question.
  - Replaced the skeleton with a complete academic framing of software
    supply-chain risk, source-versus-binary composition views, Android
    compilation and R8 evidence loss, vulnerability authority, and the
    project's evidence-gated response.
  - Added separate general and specific objectives.
  - Added an iterative methodology explaining literature review, scope,
    reference construction, APK analysis, reporting, evaluation, and
    fail-fast target/control promotion.
  - Added an eight-row contribution map covering the end-to-end MVP, common
    DEX representation, hybrid matching, identity/version separation,
    reference governance, standards-based output, source-backed evaluation,
    and transparent AI/experiment governance.
  - Expanded scope and limitations without claiming general native,
    dynamic-code, heavy-protector, complete Gradle-graph, or AI authority.
  - Added a chapter-by-chapter thesis organization and a transition to the
    technical background.
  - Avoided all headline evaluation values so Chapter 6 remains the first
    place where metrics and denominators are introduced.
  - Built and verified a new non-destructive Overleaf checkpoint package.
- Files changed:
  - `thesis/pfe/chapters/ch01_general_introduction.tex`
  - `thesis/pfe-overleaf-ch01-2026-06-20.zip`
  - `thesis/README.md`
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
- Project and standards evidence used:
  - `docs/project_handbook/overview/PROJECT_GOALS_AND_CURRENT_STATE.md`
  - `docs/architecture/DECISIONS_LOG.md`
  - `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`
  - `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`
  - the completed PFE Chapters 2--6;
  - the Chapter 3 and Chapter 6 frozen evidence snapshots;
  - existing NIST, NTIA, SPDX, CycloneDX, Android R8, and primary Android
    TPL-detection references already verified in the bibliography.
- Figures/tables created:
  - Android software-supply-chain motivation diagram.
  - Source-based versus APK-only SBOM generation diagram.
  - Fail-fast target/control improvement methodology.
  - Contribution-to-realization mapping table.
- Checks performed:
  - All 21 PFE TeX files: 46 bibliography records, 46 used citation keys,
    zero missing citations, 57 labels, zero duplicate labels, 46 references,
    and zero unresolved references.
  - Chapter 1: 25,588 characters, 10 sections, 10 subsections, balanced
    braces, three balanced figure/TikZ environments, one balanced
    table/tabularx environment, six balanced itemize environments, three
    balanced enumerate environments, one balanced quote environment, zero
    placeholders, and zero non-ASCII characters.
  - Confirmed that Chapter 1 and Chapter 6 contain the same four research
    questions in the same order.
  - Confirmed that Chapter 1 contains none of the frozen headline evaluation
    values.
  - Exact 12-word overlap check against 15 local research-paper and
    school-report PDFs: zero matches and zero extraction failures.
  - Cross-chapter check found only the intentionally repeated research
    questions in Chapter 6; excluding that required alignment, exact
    12-word prose overlap was zero.
  - `git diff --check`: passed.
  - Versioned Overleaf ZIP: 25 entries, `main.tex` at the archive root,
    bibliography and Chapters 1--6 present, and zero backslash-separated
    entry names.
  - ZIP SHA-256:
    `F6702AFA74A38BD8680AC1B887E100997A341141301AF0C36D6F233195175A59`.
- Decisions made:
  - Use the four research questions already evaluated in Chapter 6 rather
    than the five-question optional structure in the early plan.
  - Keep quantitative results out of the general introduction until their
    metrics and evidence classes are defined.
  - Present the contribution as an evidence-gated engineering system and
    evaluation methodology, not as a universally superior detector.
  - Treat source-generated and APK-recovered SBOMs as related but
    non-identical composition views.
  - Keep Chapter 1 unapproved until its three diagrams, contribution table,
    citations, and page breaks are visually inspected in a compiled PDF.
- Unresolved items:
  - Compile the PFE with LuaLaTeX and Biber.
  - Inspect Chapter 1 and all previously pending Chapters 2--6 in the rendered
    PDF.
  - Personal cover-page data and French/Arabic front matter still require
    finalization later in the plan.
- Exact next action: Draft Chapter 7 by synthesizing the contribution,
  answering the same four research questions without introducing new
  metrics, stating limitations, and prioritizing realistic future
  perspectives. Then audit the English abstract against the completed framing
  and conclusion.

## 2026-06-20 - PFE - Chapter 7 conclusion and English abstract

- Objective: Complete the seven-chapter PFE narrative with a bounded
  conclusion, explicit answers to the four research questions, limitations,
  prioritized future perspectives, and an English abstract aligned with the
  final evidence story.
- Chapter/subsection: Chapter 7, complete source draft; English abstract,
  complete revised draft.
- Status before: Chapters 1--6 had complete source drafts. Chapter 7 contained
  five empty section headings. The English abstract predated the completed
  Chapter 1 framing and Chapter 7 conclusions and omitted the full source
  denominator.
- Work completed:
  - Audited the Chapter 7 plan, Chapter 1 research questions, Chapter 6
    answers and validity threats, frozen Chapter 3 and Chapter 6 evidence,
    the project improvement plan, failed-experiment handbook, and current
    project-state summary.
  - Replaced the Chapter 7 skeleton with a complete synthesis of the problem,
    implemented MVP, evaluation findings, practical significance, research
    question answers, limitations, future work, and closing position.
  - Kept the main real-APK result explicitly labeled as the emitted Maven
    version confirmation rate and reported the full source-denominator recall
    separately.
  - Kept the source-known v2 result explicitly constrained and outside
    unconstrained APK-only authority.
  - Added a four-row RQ answer table that preserves the same questions and
    evidence boundaries used in Chapters 1 and 6.
  - Added a prioritized future-work table beginning with safer large-catalog
    candidate retrieval and exact-version abstention, followed by reference
    growth, scoped R8 evidence, native/dynamic recovery, independent
    benchmarks, and guarded AI research.
  - Expanded future perspectives for calibrated evidence, provenance-aware
    knowledge graphs, native and dynamic components, independent evaluation,
    and APK-only AI inputs.
  - Rewrote the English abstract to include the problem, method, evidence
    classes, controlled result, emitted-version confirmation result, full
    source denominator, constrained upper bound, limitations, and the
    report-only AI boundary.
  - Built and verified a new non-destructive Overleaf package containing all
    seven chapters.
- Files changed:
  - `thesis/pfe/chapters/ch07_general_conclusion.tex`
  - `thesis/pfe/frontmatter/abstract_en.tex`
  - `thesis/pfe-overleaf-ch07-2026-06-20.zip`
  - `thesis/README.md`
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
- Evidence used:
  - `docs/thesis/PFE_CHAPTER6_EVIDENCE_SNAPSHOT_2026-06-20.md`
  - `docs/thesis/PFE_CHAPTER3_AI_EVIDENCE_SNAPSHOT_2026-06-20.md`
  - completed PFE Chapters 1--6;
  - `docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md`
  - `docs/project_handbook/evaluation/FAILED_EXPERIMENTS.md`
  - `docs/project_handbook/overview/PROJECT_GOALS_AND_CURRENT_STATE.md`
- Figures/tables created:
  - Research-question answer and evidence-boundary table.
  - Prioritized future-work and promotion-evidence table.
- Checks performed:
  - All 21 PFE TeX files: 46 bibliography records, 46 used citation keys,
    zero missing citations, 59 labels, zero duplicate labels, 48 references,
    and zero unresolved references.
  - Chapter 7: 21,005 characters, 5 sections, 16 subsections, balanced
    braces, two balanced table/tabularx environments, five balanced itemize
    environments, zero placeholders, and zero non-ASCII characters.
  - English abstract: 2,201 characters, approximately 254 words, balanced
    braces, zero placeholders, and zero non-ASCII characters.
  - Verified all Chapter 7 and abstract values against the frozen Chapter 6
    snapshot.
  - Verified the same four research questions occur in Chapters 1 and 6 and
    each has a corresponding Chapter 7 answer.
  - Exact 12-word overlap check against 15 local research-paper and
    school-report PDFs: zero matches and zero extraction failures.
  - Cross-chapter exact 12-word prose overlap: zero.
  - `git diff --check`: passed.
  - Versioned Overleaf ZIP: 25 entries, `main.tex` at the archive root,
    bibliography, Chapters 1--7, and the English abstract present, with zero
    backslash-separated entry names.
  - ZIP SHA-256:
    `FC41114B1301B9869BB303B8B24AA7AF4D4D4A1E2C452B6654F4200DFC8004DD`.
- Decisions made:
  - Present the central conclusion as conditional usefulness: exact recovery
    is demonstrable when references and surviving evidence are favorable,
    while complete APK-only reconstruction remains unsolved.
  - Make safer candidate retrieval and calibrated abstention higher priority
    than simply adding more reference rows or a larger model.
  - Keep vulnerability exploitability, native package attribution, dynamic
    code, and AI component authority outside demonstrated scope.
  - Preserve the conclusion's main principle: transparent partial knowledge
    is preferable to unsupported certainty.
  - Keep Chapter 7 and the abstract unapproved until rendered-page inspection
    is complete.
- Unresolved items:
  - Compile the complete PFE with LuaLaTeX and Biber and inspect every page.
  - Replace the Appendix A skeleton with the final reproducibility and
    evidence index.
  - Rewrite the French and Arabic abstract files; their current placeholder
    text is incomplete and displays encoding damage in the shell.
  - Obtain student, supervisor, co-supervisor, jury, and defense-date
    metadata plus personal dedication and acknowledgement text.
- Exact next action: Complete Appendix A, then rewrite the French and Arabic
  abstracts from the audited English version and inventory all remaining
  personal placeholders before full-document compilation.

## 2026-06-20 - PFE - Source-complete appendix and multilingual front matter

- Objective: Complete the remaining technical PFE sources by replacing the
  Appendix A skeleton, translating the audited abstract into French and
  Arabic, isolating personal front-matter inputs, and producing a complete
  Overleaf package.
- Chapter/subsection: Appendix A, French résumé, Arabic abstract, and final
  source-quality checkpoint.
- Status before: Chapters 1--7 and the English abstract were complete.
  Appendix A contained only section headings, the French and Arabic files
  contained placeholder text, and personal metadata had not been inventoried
  in one place.
- Work completed:
  - Replaced Appendix A with a reproducibility and evidence index covering
    Docker and host setup, pinned tools, stage-level APK commands, report
    outputs, isolated reference-database construction, reset and promotion
    safety, OSV enrichment, source validation, dataset roles, claim
    traceability, and external reproducibility constraints.
  - Kept the shared calibrated database path distinct from all isolated
    experiment paths and recorded the fail-fast target/control promotion
    policy.
  - Rewrote the French résumé from the audited English abstract while
    preserving the evidence classes, denominators, and bounded wording.
  - Rewrote the Arabic abstract as valid UTF-8 text and retained English
    technical identifiers where they improve precision.
  - Added a personal front-matter checklist containing exactly six
    administrative fields plus the dedication and acknowledgements.
  - Updated the thesis upload instructions and PFE writing checkpoint.
  - Built and verified a new non-destructive source-complete Overleaf package.
- Files changed:
  - `thesis/pfe/appendices/appendix_a_reproducibility.tex`
  - `thesis/pfe/frontmatter/abstract_fr.tex`
  - `thesis/pfe/frontmatter/abstract_ar.tex`
  - `docs/thesis/PFE_PERSONAL_FRONT_MATTER_CHECKLIST.md`
  - `thesis/pfe-overleaf-source-complete-2026-06-20.zip`
  - `thesis/README.md`
  - `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
- Evidence used:
  - `docs/thesis/PFE_CHAPTER6_EVIDENCE_SNAPSHOT_2026-06-20.md`
  - `docs/thesis/PFE_CHAPTER3_AI_EVIDENCE_SNAPSHOT_2026-06-20.md`
  - `docs/thesis/THESIS_ARTIFACT_INDEX.md`
  - `docs/project_handbook/commands/SETUP_AND_ENVIRONMENT.md`
  - `docs/project_handbook/commands/CORE_CLI_REFERENCE.md`
  - `docs/project_handbook/commands/REFERENCE_DB_CLI_REFERENCE.md`
  - `docs/project_handbook/workflows/FIRST_APK_WALKTHROUGH.md`
  - `docs/project_handbook/workflows/BUILD_AND_VALIDATE_WORKFLOWS.md`
- Checks performed:
  - Project test suite: 275 tests passed in 22.32 seconds.
  - All 21 PFE TeX files: 46 bibliography records, 46 used citation keys,
    zero missing citations, 63 labels, zero duplicate labels, 63 references,
    and zero unresolved references.
  - All TeX environments and braces pass the static balance check.
  - Appendix A: 14,557 characters, seven sections, six subsections, five code
    listings, four table/longtable environments, and zero placeholders.
  - French abstract: 3,008 characters and approximately 441 lexical tokens;
    Arabic abstract: 2,394 characters, approximately 335 lexical tokens, and
    1,633 Arabic-script characters.
  - UTF-8 checks found no replacement characters or mojibake markers in the
    new appendix and abstract sources.
  - Exact 12-word overlap check against 15 local research-paper and
    school-report PDFs covering 400 pages: zero matches and zero extraction
    failures.
  - `git diff --check`: passed for the completed thesis sources and checklist.
  - Versioned Overleaf ZIP: 25 entries, `main.tex` at the archive root, seven
    chapters, Appendix A, three abstracts, bibliography, and zero
    backslash-separated entry names.
  - ZIP SHA-256:
    `18B14B51E93A5C63826C4BEA7349765C4B14AC92FDFDF8FCDAC7152839C7C111`.
- Decisions made:
  - Keep Appendix A focused on executable reproduction and evidence
    traceability instead of repeating Chapter 6's implementation narrative.
  - State that source validation is evaluation evidence and not an input to
    normal APK matching.
  - Preserve the distinction between frozen results and a future rerun against
    mutable Maven, Gradle, and OSV infrastructure.
  - Leave all eight personal or administrative values explicit rather than
    inventing names or personal prose.
  - Keep every chapter unapproved until the compiled PDF has been visually
    inspected.
- Unresolved items:
  - Obtain the six administrative values, dedication, and acknowledgements
    listed in `docs/thesis/PFE_PERSONAL_FRONT_MATTER_CHECKLIST.md`.
  - Compile with LuaLaTeX and Biber in Overleaf or a local TeX installation.
  - Inspect every page for table width, diagram placement, Arabic direction,
    typography, page breaks, references, headers, and front-matter alignment.
- Exact next action: Fill the eight personal fields, compile
  `thesis/pfe-overleaf-source-complete-2026-06-20.zip` in Overleaf using
  LuaLaTeX and Biber, and complete the visual page-by-page approval pass.

## 2026-06-20 - PFE - Partial personal front-matter completion

- Filled the confirmed student, supervisor, and co-supervisor names:
  Fendi Mohamed, Serai Abdelhak, and Manel Baba Ahmed.
- Replaced the dedication placeholder with a polished version of the
  student's message to parents, siblings, family, and lifelong friends.
- Replaced the acknowledgements placeholder with original prose inspired only
  by the requested structure; no names or distinctive wording from the sample
  acknowledgement were retained.
- Kept the jury president, examiner, and exact defense date as explicit
  placeholders because the supplied dots and `xx/xx/2026` were not final
  values.
- Static environment balance and `git diff --check` passed.
- Built `thesis/pfe-overleaf-frontmatter-partial-2026-06-20.zip` with 25
  root-relative entries and zero backslash-separated names.
- ZIP SHA-256:
  `4ADC3B2DAA3C94BFC15A6BA7655300BBF4DC8FE39D77ACA9BFFEDB4F837509BB`.
- Exact next action: Obtain the jury president, examiner, and exact defense
  date, then compile and visually inspect the complete thesis.

## 2026-06-20 - PFE - Successful local compilation and rendered-page QA

- Objective: Compile the complete PFE locally with MiKTeX, repair all blocking
  LaTeX and visible layout defects, and produce a verified handoff package.
- Work completed:
  - Updated the local MiKTeX installation and installed the packages required
    by the thesis, including Polyglossia, LuaBidi, Amiri, PGF, BibLaTeX, and
    PDF landscape support.
  - Fixed the undefined `\SBOMs` command and the Arabic bookmark/language
    warnings.
  - Corrected title-page page anchors and front-matter numbering.
  - Resized the methodology, architecture, and activity diagrams so they fit
    their pages without clipping.
  - Reflowed the Package URL syntax and moved the state-of-the-art comparison
    table to a readable landscape page.
  - Simplified and resized the reference-database schema so labels and
    long diagnostic feature names no longer overlap.
  - Compiled all 46 bibliography entries with Biber and resolved all
    cross-references.
- Checks performed:
  - `latexmk main.tex`: passed with exit code 0.
  - Final output: 119 pages and 991,695 bytes.
  - Fatal errors, undefined controls, undefined citations, undefined
    references, duplicate PDF destinations, and Biber rerun requests: zero.
  - Full contact-sheet review plus full-resolution inspection of the title
    page, Arabic abstract, corrected diagrams, landscape table, database
    schema, and bibliography.
  - `git diff --check`: passed.
  - Overleaf ZIP: 25 root-relative entries, seven chapter files,
    `main.tex` at the root, and zero backslash-separated entry names.
- Artifacts:
  - Compiled PDF:
    `thesis/PFE_Fendi_Mohamed_compiled_draft_2026-06-20.pdf`
  - PDF SHA-256:
    `F09CDB2B397995EED45E353CC208378078110C0831034A4D4CDACA0B9FACCFCE`
  - Upload package:
    `thesis/pfe-overleaf-local-build-verified-2026-06-20.zip`
  - ZIP SHA-256:
    `A7783BEE49EBEE8F8AF4E52FB393FD5AEF095DECF8B8ED438271816CC40CE947`
- Remaining boundary:
  - Jury president, examiner, and exact defense date remain explicit
    placeholders.
  - Existing narrow-table and long-URL box warnings are non-fatal and were
    checked against the rendered pages.
- Exact next action: Fill the three remaining administrative values, rebuild,
  and inspect the title page once more before submission.

## 2026-06-20 - PFE - Figure overlap and table readability corrections

- Objective: Correct the layout defects reported during manual PDF review and
  improve table readability consistently across the thesis.
- Corrections completed:
  - Figure 1.1: anchored both auditor connectors at the node boundary so no
    arrow or line crosses the box text.
  - Table 3.1: widened the label column, split the longest technical label,
    prevented label/count overlap, and added thin row separators.
  - Figure 3.1: moved the no-authority marker outside the CycloneDX output
    node and added clear horizontal spacing.
  - Figure 3.3: placed the authority-feedback block below the report path and
    rerouted its dashed connector away from every node.
  - Figure 5.2: enlarged the use-case spacing, assigned fixed text widths, and
    removed the overlapping actor/use-case and experiment ellipses.
  - All `tabularx` prose columns now use ragged-right alignment to avoid
    stretched spaces in narrow cells. Tables use slightly increased row
    height and restrained alternating row shading for visual separation.
- Checks performed:
  - `latexmk main.tex`: passed with exit code 0.
  - Final output: 121 pages and 1,000,005 bytes.
  - Fatal errors, undefined controls, undefined citations, undefined
    references, duplicate PDF destinations, and Biber rerun requests: zero.
  - Full-resolution review of every reported figure and Table 3.1.
  - Representative table inspection in Chapters 2, 6, and 7.
  - Complete 121-page contact-sheet sweep after the pagination change.
  - Overleaf ZIP: 25 root-relative entries, seven chapter files,
    `main.tex` at the root, and zero backslash-separated entry names.
- Refreshed artifacts:
  - PDF:
    `thesis/PFE_Fendi_Mohamed_compiled_draft_2026-06-20.pdf`
  - PDF SHA-256:
    `FD3F5277DE74B14B0E1E96111B7607C181B19BA19D8091CE7B0BE87CAA95BBAA`
  - Overleaf package:
    `thesis/pfe-overleaf-local-build-verified-2026-06-20.zip`
  - ZIP SHA-256:
    `0137DF300BC67FEB313AB64D06A47810994FD458D0B2E1597F3DD22CD84A9DC9`
- Remaining boundary: Jury president, examiner, and exact defense date remain
  explicit placeholders.
- Exact next action: Fill the three remaining administrative values and
  perform the final title-page check.

## 2026-06-20 - PFE - Architecture expansion and final diagram routing

- Objective: Align the thesis architecture with the implemented project
  architecture, expose the ML/DL/R8 research boundary, and correct the latest
  reported page and diagram layout defects.
- Corrections completed:
  - Expanded Figure 5.1 into a detailed two-input architecture covering APK
    evidence extraction, Maven reference construction, SQLite reference
    features, multi-feature matching, identity/version decisions, CycloneDX,
    OSV, and human-readable reports.
  - Added a separate dashed report-only layer for R8 and multi-scale
    diagnostics, Random Forest and Transformer experiments, and the hybrid
    version-band router. Its arrows cannot feed authoritative matching or SBOM
    decisions.
  - Rerouted all Figure 5.1 output and research connectors so they do not pass
    through component boxes.
  - Added margins in Figure 5.2 so the actors and lower experiment use cases no
    longer overlap.
  - Rerouted Figure 5.6 connectors around deployed components and preserved the
    promotion-only boundary for isolated reference-database experiments.
  - Replaced the rotated landscape running header with a horizontal Chapter 4
    header and page number.
  - Changed the title-page specialty to
    `Computer Systems Engineering (CIS)`.
- Checks performed:
  - `latexmk main.tex`: passed with exit code 0.
  - Final output: 122 pages and 1,005,097 bytes.
  - Fatal errors, undefined controls, undefined citations, undefined
    references, duplicate PDF destinations, and Biber rerun requests: zero.
  - Full-resolution inspection of the title page, landscape comparison table,
    Figure 5.1, Figure 5.2, and Figure 5.6.
  - Overleaf ZIP: 25 root-relative entries, seven chapter files,
    `main.tex` at the root, and zero backslash-separated entry names.
- Refreshed artifacts:
  - PDF:
    `thesis/PFE_Fendi_Mohamed_compiled_draft_2026-06-20.pdf`
  - PDF SHA-256:
    `8838020F23831097A2B35D0876D17029A0CCA249F2EC771733FBCC9184FF0724`
  - Overleaf package:
    `thesis/pfe-overleaf-local-build-verified-2026-06-20.zip`
  - ZIP SHA-256:
    `B08DC62F11C50300E218BE329CCFE42A5B28C45AC337EA573BD392C58F33A963`
- Remaining boundary: Jury president, examiner, and exact defense date remain
  explicit placeholders.
- Exact next action: Fill the three remaining administrative values and
  perform the final title-page check.

## 2026-06-20 - PFE - Full examiner, evidence, reference, and reproducibility audit

- Objective: Review the complete PFE as a thesis examiner, research reviewer,
  and software-engineering evaluator; correct claims that disagreed with the
  implementation or frozen project evidence.
- Scope reviewed:
  - English, French, and Arabic abstracts;
  - Chapters 1--7;
  - Appendix A;
  - all 46 cited bibliography entries;
  - Chapter 3 and Chapter 6 frozen evidence snapshots;
  - current matcher, extractor, reference-feature, CLI, dashboard, and
    experiment-ledger artifacts.
- Substantive corrections:
  - aligned the matcher formula with the configured-weight implementation;
  - separated the 102 Maven-emitting source-validated APKs from four
    no-Maven-signal source-tree controls;
  - preserved 50.5% as emitted-version confirmation rather than dependency
    recall;
  - qualified 6,772/6,772 as a source-constrained recognition upper bound;
  - removed unsupported signature-inspection and all-discovered-DEX claims;
  - clarified resource inventory, manifest permissions, report-only AI, and
    difficult-family evidence boundaries;
  - added exact rejected global-R8-blend regression counts;
  - corrected nonexistent APK, configuration, database, artifact, and DEX
    paths in the reproducibility workflow;
  - qualified Docker reproducibility against mutable external infrastructure.
- Reference and writing audit:
  - 46 citation keys and 46 bibliography entries, with no missing or unused
    key;
  - official URLs and academic records checked where available;
  - venue, page, and DOI metadata corrected for LibD, LibPecker, ATVHUNTER,
    LibAttention, SAD, and UniBOM;
  - TPL-Benchmark dataset and 60.15% LibPecker F1 claims checked against the
    primary paper;
  - informal or ambiguous phrases replaced with precise academic wording;
  - exact 12-word local overlap scan found no suspicious copying from the
    stored papers or previous school reports.
- Visual validation:
  - rendered and inspected all 122 pages of the latest available compiled
    draft;
  - inspected abstracts, dense tables, architecture and use-case diagrams,
    Chapter 6 results, appendix listings, and bibliography at full resolution;
  - found no clipping, overlap, rotated header, or broken diagram in that
    build.
- Build boundary:
  - the sandbox blocked the final MiKTeX/Biber refresh after the source audit;
    therefore the existing PDF is retained only as a layout checkpoint and
    predates the last bibliography, path, and wording corrections.
- New artifacts:
  - examiner report:
    `docs/thesis/PFE_FULL_THESIS_EXAMINER_REVIEW_2026-06-20.md`;
  - audited source package:
    `thesis/pfe-overleaf-examiner-audited-source-2026-06-20.zip`;
  - source package entries: 25;
  - source package SHA-256:
    `6EDC98E634831D82A51132FAB575E64BAC9DF8EB164420C62C75064E65D49528`.
- Remaining boundary:
  - rebuild the corrected package with LuaLaTeX and Biber;
  - fill jury president, examiner, and exact defense date;
  - run an institutional plagiarism checker if required.
- Exact next action: Rebuild the examiner-audited source, inspect the changed
  pages, and then finalize the administrative title-page values.

## 2026-06-21 - PFE - Prototype output screenshots added to Chapter 6

- Objective: Add thesis-visible proof that the implemented MVP produces real
  reports for both a clean and a vulnerable demonstration lane.
- Source artifacts used:
  - clean lane:
    `data/results/demo-osv-clean-fdroid/report.md`,
    `report.html`, `report.json`, `sbom.cdx.json`, and
    `osv-vulnerabilities.json`;
  - vulnerable lane:
    `data/results/demo-osv-vulnerable-jackson-databind/report.md`,
    `report.html`, `report.json`, `sbom.cdx.json`, and
    `osv-vulnerabilities.json`.
- Thesis changes:
  - copied five report screenshots into `thesis/pfe/figures/`;
  - added a Chapter 6 prototype-output paragraph after the vulnerability
    demonstration table;
  - added five figures showing the clean F-Droid report summary/component
    evidence and the vulnerable Jackson report summary/CVE/artifact evidence;
  - captions explicitly state that the screenshots demonstrate the working
    end-to-end output path and do not introduce a new evaluation denominator.
- New upload package:
  - `thesis/pfe-overleaf-prototype-screenshots-source-2026-06-21.zip`;
  - entries: 29;
  - SHA-256:
    `28739F9E43DC68159FDF6A980A17E9EE56A8E6EFC390274000642226F3A09DD8`.
- Build boundary:
  - local `latexmk` still points to a broken TinyTeX shim;
  - direct LuaLaTeX fails before reading `main.tex` because the local TinyTeX
    runtime rejects the Windows user path;
  - rebuild the new ZIP in TeXPage/Overleaf or a repaired local TeX
    environment before treating the PDF as final.

## 2026-06-21 - PFE - Local MiKTeX rebuild fixed and screenshots verified

- Objective: Replace the stale "local rebuild unavailable" boundary with an
  actual local PDF rebuild and visual proof that the Chapter 6 prototype
  screenshots compile correctly.
- Build fix:
  - TinyTeX remains broken on this workstation before it reads `main.tex`;
  - MiKTeX `latexmk` is installed but cannot run until a Perl engine is
    available;
  - bypassed both blockers with the direct MiKTeX sequence:
    `lualatex`, `biber`, `lualatex`, `lualatex`.
- Build result:
  - `thesis/pfe/main.pdf`;
  - pages: 131;
  - size: 1,703,533 bytes;
  - no fatal LaTeX errors, undefined-reference warnings, Biber rerun requests,
    or label rerun warnings remained in the final log;
  - remaining warnings are minor overfull boxes/vboxes in tight tables or
    paragraphs, not missing content.
- Source correction made during rebuild:
  - shortened the List-of-Figures entries for the five prototype screenshots so
    the long Jackson coordinate and report descriptions do not overflow the
    front-matter list.
- Visual QA:
  - located the actual screenshot pages at physical PDF pages 97--101, shown as
    Chapter 6 pages 79--83;
  - rendered them to
    `tmp/pdfs/pfe-local-build-2026-06-21/prototype-page-097.png` through
    `prototype-page-101.png`;
  - visually inspected all five rendered pages; the clean F-Droid and
    controlled vulnerable Jackson screenshots are readable, centered, captioned,
    and not clipped or overlapping.
- Deliverables:
  - current compiled draft:
    `thesis/PFE_Fendi_Mohamed_compiled_draft_2026-06-21.pdf`;
  - PDF SHA-256:
    `6E56D18C6617E5A39C6B5C01402FD67AE8B914673900FDEA7AFE68AB1F05E6D8`;
  - refreshed TeXPage/Overleaf source ZIP:
    `thesis/pfe-overleaf-prototype-screenshots-source-2026-06-21.zip`;
  - ZIP entries: 29, including `main.tex` and all five prototype PNG figures;
  - ZIP SHA-256:
    `8598CA673954E162FAFDE9A95DE501C87876876259DBD540D6BE5D9B2F7B8A6D`.
- Remaining blocker:
  - jury president, examiner, and exact defense date are still placeholders in
    the title-page metadata.
- Exact next action: Fill the three administrative values in
  `thesis/pfe/metadata.tex`, then run one final local or Overleaf/TeXPage build
  before submission.

## 2026-06-21 - PFE - Complete HTML dashboards and AI/R8 report evidence

- Objective: Replace the limited prototype report excerpts with the complete
  clean and vulnerable HTML dashboard evidence used by the defense
  presentation, and add visible report output for the R8/ML/DL layer.
- Dashboard sources:
  - clean lane:
    `data/results/demo-osv-clean-fdroid/report.html`;
  - controlled vulnerable lane:
    `data/results/demo-osv-vulnerable-jackson-databind/report.html`;
  - report-only hybrid lane:
    `data/results/evaluation/final-hybrid-ai-demo-smoke/aegis-authenticator/hybrid-ai/report.html`.
- Thesis changes:
  - replaced the five Markdown/PDF-style report excerpts in Chapter 6 with six
    consecutive browser-rendered panels covering the complete clean F-Droid
    HTML dashboard;
  - added three consecutive panels covering the complete controlled vulnerable
    Jackson HTML dashboard, including exact component/version evidence, all
    three confirmed HIGH CVEs, artifacts, and limitations;
  - added four report-only panels covering R8/obfuscation diagnostics, hybrid
    authority and integration status, Phase 6A Random Forest recommendations,
    and Phase 6B Transformer status;
  - captions and surrounding text explicitly preserve the authority boundary:
    the weighted deterministic matcher remains the SBOM authority, and the
    R8/ML/DL panels are implementation/report evidence rather than new accuracy
    denominators.
- Build and QA:
  - rebuilt with direct MiKTeX `lualatex`, `biber`, `lualatex`, `lualatex`
    passes, followed by crop-polish rebuilds;
  - final result: 139 pages, 1,921,967 bytes;
  - no fatal LaTeX errors, undefined references, Biber rerun requests, or label
    rerun warnings remain;
  - rendered physical PDF pages 97--110 and the two List-of-Figures pages;
  - visually verified all new panels, captions, page headers, and list entries;
    no clipping, overlap, or neighboring-section crop artifacts remain.
- Deliverables:
  - compiled PDF:
    `thesis/PFE_Fendi_Mohamed_compiled_draft_full_reports_2026-06-21.pdf`;
  - PDF SHA-256:
    `81B89BE5C061931F97ADAA3CCB529BC8097FE1B5E380A8FE5EB0B2DDAA3E63AC`;
  - Overleaf/TeXPage source ZIP:
    `thesis/pfe-overleaf-full-reports-ai-r8-2026-06-21.zip`;
  - ZIP entries: 37 source files and referenced image assets;
  - ZIP SHA-256:
    `3F6B2903A18DD6FF427C99229CBDDD040235EF4F67EF00FCAD8337E6F26326C6`.
- Remaining blocker: jury president, examiner, and exact defense date are still
  placeholders in `thesis/pfe/metadata.tex`.
- Exact next action: Fill those three administrative values and perform the
  final submission build.

## 2026-06-21 - Master - Structured review protocol and first compiled baseline

- Objective: Start substantive master-thesis writing by freezing the
  literature-review method, reconciling the existing paper corpus, and
  producing a locally compiled baseline.
- Chapter/subsection: Chapter 2, Background and Research Methodology; Appendix
  A, Literature Review Protocol.
- Status before:
  - the master project contained a five-chapter skeleton and an initial
    Chapter 4 framework sketch;
  - the review protocol was not frozen;
  - older notes inconsistently described the corpus as 15 studies while the
    structured overview contained 17 records and the local paper directory
    contained 13 PDFs;
  - the checkpoint incorrectly stated that local TeX compilation was
    unavailable.
- Work completed:
  - created protocol version 1.0 at
    `docs/thesis/MASTER_STRUCTURED_REVIEW_PROTOCOL.md`;
  - defined six review questions, the four-block search strategy, inclusion
    and exclusion rules, screening stages, extraction fields, eight quality
    questions, synthesis constraints, and change control;
  - reconciled the corpus as 20 seed publication units rather than treating
    incompatible historical counts as equivalent;
  - classified 13 locally inspected full texts as Tier A and seven
    supplementary records as Tier B pending full-text verification;
  - expanded Chapter 2 from a heading skeleton into the conceptual and
    methodological basis for authoritative versus reconstructed SBOMs,
    evidence provenance, uncertainty, identity/version/security authority,
    Android transformation threats, and the structured mapping method;
  - expanded Appendix A into the executable review protocol and selected-study
    table;
  - added the review-method reference and 12 additional verified Tier A study
    records to the master bibliography;
  - updated the master writing checkpoint to begin MASTER-2 and Chapter 3.
- Files changed:
  - `docs/thesis/MASTER_STRUCTURED_REVIEW_PROTOCOL.md`
  - `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
  - `thesis/master/chapters/ch02_background_methodology.tex`
  - `thesis/master/appendices/appendix_a_review_protocol.tex`
  - `thesis/master/bib/references.bib`
- Project evidence used:
  - `papers/data/papers_overview.json`;
  - the individual structured extraction JSON files;
  - `papers/data/papers_6-10_analysis.json`;
  - `papers/data/SBOM_Tools_Synthesis_Table.md`;
  - `papers/data/impact_on_project.md`;
  - the 13 locally stored paper PDFs;
  - the existing PFE bibliography audit.
- Academic references added or verified:
  - Kitchenham and Charters, EBSE-2007-01;
  - LibD, ORLIS, LibPecker, LibID, the ASE 2020 assessment, the 2021
    systematic assessment, ATVHUNTER, LibScan, the Ramirez thesis, LibHunter,
    LibAttention, and SAD;
  - final audit: 18 cited keys, 18 bibliography entries, zero missing and zero
    unused keys.
- Figures/tables created:
  - search concept-block table;
  - structured extraction-schema table;
  - frozen 20-publication seed-corpus table.
- Checks performed:
  - direct MiKTeX sequence: LuaLaTeX, Biber, LuaLaTeX, LuaLaTeX;
  - final PDF: 39 pages and 420,216 bytes;
  - PDF SHA-256:
    `44E959A2BDF100A163D9C44BA9CBB4E8E67557171342BB737C517FE40219F616`;
  - no fatal LaTeX errors, undefined controls, undefined citations, undefined
    references, or Biber rerun requests remained;
  - rendered all 39 pages with Poppler and inspected seven contact sheets plus
    full-resolution methodology, query, corpus-table, framework, and
    bibliography pages;
  - no clipping, overlap, broken table, unreadable diagram, or missing content
    was found;
  - Overleaf ZIP contains 22 source entries, `main.tex` at the root, and zero
    backslash-separated entry names.
- Decisions made:
  - describe the work as a structured mapping review rather than claiming a
    completed exhaustive systematic literature review;
  - keep Tier A and Tier B evidence visibly separate;
  - prohibit precise quantitative synthesis from Tier B records until their
    full texts are verified;
  - keep library identity, exact version, and vulnerability authority as
    separate analysis dimensions;
  - retain the recommended title as provisional pending supervisor approval.
- Deliverables:
  - `thesis/Master_compiled_draft_review_protocol_2026-06-21.pdf`;
  - `thesis/master-overleaf-review-protocol-2026-06-21.zip`;
  - ZIP SHA-256:
    `150CFE1A78A83154E0ACAEA41514A14111B3B121E6BF522EB1173B76B2BA3520`.
- Unresolved items:
  - supervisor approval of the title and thesis research questions;
  - seven Tier B records require local full-text verification;
  - student, supervisor, defense date, dedication, acknowledgements, and
    translated abstracts remain explicit administrative or drafting
    placeholders in the master source.
- Exact next action: Expand Chapter 3 by applying the frozen schema to the 13
  Tier A studies and construct the technique, evidence-source,
  transformation-threat, and evaluation-practice taxonomies.

## 2026-06-21 - Master - Chapter 3 taxonomy drafted and rendered

- Objective: Continue MASTER-2 by turning the Chapter 3 skeleton into a
  taxonomy-based state-of-the-art synthesis grounded in the frozen Tier A
  corpus.
- Chapter/subsection: Chapter 3, State of the Art and Taxonomy.
- Status before:
  - Chapter 3 contained only headings and one LibScout sentence;
  - the review protocol was frozen, but the technique, evidence,
    transformation-threat, evaluation, and comparative taxonomies were not yet
    written.
- Work completed:
  - expanded Chapter 3 into a full synthesis chapter with an introduction,
    technique taxonomy, evidence-source taxonomy, transformation-threat
    taxonomy, representative approach synthesis, evaluation-practice taxonomy,
    Tier A comparative table, limitations, research gap, and conclusion;
  - kept Tier B records as provisional context only and did not use them for
    precise quantitative conclusions;
  - classified the 13 Tier A studies consistently by recovery role and SBOM
    trust implication;
  - converted the large taxonomy tables to breakable `longtable` layouts after
    the first build exposed overfull-vbox layout pressure;
  - updated the master writing checkpoint with the rendered Chapter 3 baseline
    and the next audit action.
- Files changed:
  - `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
  - `thesis/master/chapters/ch03_state_of_the_art_taxonomy.tex`
- Project evidence used:
  - `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`;
  - `docs/thesis/THESIS_WRITING_AND_RESUMPTION_RULES.md`;
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`;
  - `docs/thesis/MASTER_STRUCTURED_REVIEW_PROTOCOL.md`;
  - `papers/data/papers_overview.json`;
  - `papers/data/SBOM_Tools_Synthesis_Table.md`;
  - `papers/data/impact_on_project.md`;
  - `papers/state_of_the_art.md`;
  - `papers/data/libscout.json`;
  - `papers/data/libd.json`;
  - `papers/data/orlis.json`;
  - `papers/data/zhan_ase2020.json`;
  - `papers/data/libattention.json`;
  - `papers/data/papers_6-10_analysis.json`;
  - `docs/research/EVIDENCE_MAP.md`.
- Academic references used:
  - all 13 Tier A study keys already present in
    `thesis/master/bib/references.bib`;
  - Android R8 documentation for transformation context.
- Figures/tables created:
  - Table 3.1, technique taxonomy;
  - Table 3.2, evidence-source taxonomy;
  - Table 3.3, transformation-threat taxonomy;
  - Table 3.4, evaluation-practice taxonomy;
  - Table 3.5, Tier A comparative trust interpretation table.
- Checks performed:
  - placeholder scan of Chapter 3: zero `TODO`, `TBD`, `[REF]`, or
    `PLACEHOLDER` markers;
  - non-ASCII scan of Chapter 3: zero matches;
  - direct MiKTeX build sequence after editing: LuaLaTeX, Biber, LuaLaTeX,
    LuaLaTeX, followed by two additional LuaLaTeX passes after table-layout
    fixes;
  - final PDF: 50 pages and 486,346 bytes;
  - PDF SHA-256:
    `C5250A64F6AAFD17D48BD9904DD1D9C02C9746FDA5132715FD7565D9F08E7E89`;
  - no fatal LaTeX errors, undefined controls, undefined citations,
    undefined references, Biber rerun requests, or label-rerun requests
    remained in the final log;
  - rendered all 50 pages with Poppler at 120 DPI to
    `tmp/pdfs/master-ch3-2026-06-21`;
  - inspected contact sheets and full-resolution Chapter 3 pages covering the
    chapter opening, all taxonomy tables, the representative-approach prose,
    the evaluation table, the comparative longtable, the limitations, research
    gap, and conclusion.
- Visual QA result:
  - no clipping, overlap, broken table, unreadable text, or missing content was
    found on the inspected Chapter 3 pages;
  - the previous severe overfull-vbox table layout issue was resolved by using
    breakable longtables.
- Remaining warnings:
  - existing harmless front-matter warnings remain: Arabic biblatex dummy
    language warning, duplicate `page.i` destination, and Arabic PDF-string
    hyperref warning;
  - small overfull boxes remain in tight tables/headings, including 2.47pt
    Chapter 3 longtable alignment warnings, visually inspected as readable;
  - the existing bibliography SPDX URL overfull remains.
- Deliverables:
  - compiled PDF:
    `thesis/Master_compiled_draft_chapter3_taxonomy_2026-06-21.pdf`;
  - PDF SHA-256:
    `C5250A64F6AAFD17D48BD9904DD1D9C02C9746FDA5132715FD7565D9F08E7E89`;
  - Overleaf/TeXPage source ZIP:
    `thesis/master-overleaf-chapter3-taxonomy-2026-06-21.zip`;
  - ZIP entries: 22, with `main.tex` at the root and zero backslash-separated
    entry names;
  - ZIP SHA-256:
    `10E4CB2A31752D4CB491C69B25B1751B453DF7F6C86546F11332ED1CADD54C30`.
- Unresolved items:
  - supervisor approval of the provisional master title and research questions;
  - seven Tier B records still need local full-text verification before they
    support strong synthesis;
  - Chapter 3 is drafted and rendered but not yet approved because it still
    needs final evidence and PFE-overlap polish;
  - student, supervisor, defense date, dedication, acknowledgements, and
    translated abstracts remain explicit administrative or drafting
    placeholders.
- Exact next action: Audit Chapter 3 against the Tier A extraction notes and
  PFE overlap, polish table spacing if desired, then begin expanding Chapter
  4's evidence-based trust framework.

## 2026-06-21 - Master - Chapter 4 framework drafted and rendered

- Objective:
  - continue from the Chapter 3 taxonomy checkpoint;
  - expand Chapter 4 from a skeleton into the master thesis's principal
    evidence-based trust framework chapter;
  - keep PFE material scoped as case-study evidence rather than implementation
    documentation or independent master experiments.
- Source changes:
  - replaced the Chapter 4 scaffold in
    `thesis/master/chapters/ch04_evidence_trust_framework.tex`;
  - added a full framework chapter covering:
    - design principles;
    - recovered claim model and claim granularity;
    - evidence hierarchy;
    - evidence quality dimensions;
    - evidence fusion, conflict handling, confidence caps, and abstention;
    - claim classes;
    - validation and evidence lanes;
    - vulnerability-claim policy;
    - recovered claim lifecycle;
    - PFE case-study mapping;
    - framework evaluation;
    - limitations and research agenda;
    - conclusion;
  - corrected the Chapter 4 title rendering with a deliberate line break while
    preserving the short title in the table of contents and page headers.
- Project evidence used:
  - `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`;
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`;
  - `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`;
  - `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`;
  - `docs/evaluation/THESIS_EVALUATION_TABLES.md`;
  - `docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md`;
  - `docs/evaluation/LIMITATION_BOUNDARY_DASHBOARD.md`;
  - `docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md`.
- Evidence-boundary decisions:
  - Chapter 3 was checked for PFE metric leakage and remains literature
    focused;
  - Chapter 4 uses PFE evidence only in a bounded case-study table and avoids
    embedding volatile exact evaluation counts;
  - report-only AI/R8 outputs remain explicitly non-authoritative;
  - native and hidden-code cases remain boundary/out-of-scope evidence rather
    than Maven package-version claims;
  - confidence is described as a policy class, not a calibrated probability.
- Figures/tables created in Chapter 4:
  - Table 4.1, reconstructed SBOM claim core fields;
  - Table 4.2, evidence hierarchy;
  - Table 4.3, evidence quality dimensions;
  - Figure 4.1, conceptual trust-framework flow;
  - Table 4.4, claim classes and permitted use;
  - Table 4.5, validation and evidence lanes;
  - Table 4.6, vulnerability interpretation policy;
  - Table 4.7, PFE case-study mapping.
- Build and verification:
  - ran LuaLaTeX, Biber, and stabilizing LuaLaTeX passes after the Chapter 4
    expansion;
  - final compiled draft: 62 pages and 574,885 bytes;
  - no fatal LaTeX errors, undefined controls, undefined citations,
    undefined references, Biber rerun requests, or label-rerun requests
    remained in the final log;
  - remaining warnings are known layout/front-matter warnings:
    - Arabic biblatex dummy language warning;
    - duplicate `page.i` destination;
    - Arabic PDF-string hyperref warning;
    - small table/header overfull boxes in earlier chapters and appendix;
    - existing SPDX bibliography URL overfull;
    - one tiny 0.73pt Chapter 4 paragraph overfull around inline code names.
- Visual QA:
  - rendered all 62 pages with Poppler at 120 DPI to
    `tmp/pdfs/master-ch4-2026-06-21`;
  - generated and inspected contact sheets for the whole PDF;
  - inspected full-resolution Chapter 4 pages covering the opener, dense claim
    schema table, evidence hierarchy, evidence quality table, framework figure,
    claim classes, validation lanes, and PFE case-study mapping;
  - re-rendered and inspected the Chapter 4 opener after the title-linebreak
    polish;
  - no clipping, overlap, broken table, unreadable text, or missing content was
    found on the inspected Chapter 4 pages.
- Deliverables:
  - compiled PDF:
    `thesis/Master_compiled_draft_chapter4_framework_2026-06-21.pdf`;
  - PDF SHA-256:
    `A74BC6B9506BA27C06F1BCEA6972761BBFDA5C22106D8AC04C35AA2741025CD7`;
  - Overleaf/TeXPage source ZIP:
    `thesis/master-overleaf-chapter4-framework-2026-06-21.zip`;
  - ZIP entries: 21, with `main.tex` at the root and no build artifacts;
  - ZIP SHA-256:
    `07FFA2CF602EEBC93B22583B3133A808F6A062F3FA6F03AF2D112E7F0CB21AB0`.
- Updated checkpoint:
  - active chapter is now Chapter 4;
  - active work moved to Chapter 4 case-study polish and Chapter 5 synthesis;
  - exact next action is to audit Chapter 4 case-study mappings against the
    current PFE evaluation artifacts and overlap boundaries, then draft Chapter
    5's research-question answers and general conclusion.
- Unresolved items:
  - supervisor approval of the provisional master title and research questions;
  - seven Tier B records still need local full-text verification before strong
    synthesis;
  - Chapters 3 and 4 are drafted and rendered but not approved until final
    evidence and PFE-overlap polish is complete;
  - Chapter 5 remains skeletal;
  - student, supervisor, defense date, dedication, acknowledgements, and
    translated abstracts remain explicit administrative or drafting
    placeholders.

## 2026-06-21 - Master - Chapter 4 audit and Chapter 5 conclusion drafted

- Objective:
  - complete the recorded Chapter 4 PFE case-study evidence and overlap audit;
  - align the introduction with the six supporting research questions in the
    master plan;
  - replace the Chapter 5 skeleton with a complete research synthesis,
    limitations analysis, and future-research agenda.
- Chapter 4 audit:
  - checked the case-study mapping against
    `docs/evaluation/THESIS_EVALUATION_TABLES.md`,
    `docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md`,
    `docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md`,
    `docs/evaluation/LIMITATION_BOUNDARY_DASHBOARD.md`,
    `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`, and
    `docs/thesis/EXPERIMENT_DECISION_LEDGER.md`;
  - retained the controlled, clean real, partial real, version-band,
    report-only, and native/hidden-code observations;
  - added explicit rows for reference coverage versus matcher recall,
    source-known upper-bound reruns, failed target/control promotions, and the
    scoped AndroidX Fragment 1.6.2 experiment-only decision;
  - converted Table 4.7 to a breakable longtable so all ten observations remain
    readable;
  - confirmed that every row identifies PFE evidence as a bounded case study,
    not a new master experiment.
- Framing and Chapter 5 changes:
  - aligned Chapter 1 with the central research question and all six supporting
    questions recorded in the master plan;
  - replaced the Chapter 5 headings-only scaffold with 322 lines covering:
    - the general conclusion and central answer;
    - a six-row research-question answer table;
    - six master-specific contributions;
    - review, domain, calibration, case-study, source/reference, and
      native/dynamic limitations;
    - a seven-direction future-research table;
    - detailed calibration, independent validation, provenance,
      broader-domain, and knowledge-graph directions;
    - closing remarks;
  - preserved the short Chapter 5 title in the table of contents and running
    header while using a deliberate two-line display title.
- Evidence and overlap controls:
  - Chapter 5 summarizes the framework rather than repeating the PFE
    implementation and evaluation conclusion;
  - no volatile PFE metric was inserted into the master conclusion;
  - exact 12-word overlap scanning across master Chapters 4--5 and PFE
    Chapters 4--7 found zero prose overlaps; the only three matches were TikZ
    style tokens;
  - all changed TeX files are ASCII-only, have balanced environments, and
    contain no `TODO`, `TBD`, `FIXME`, or accidental `\SBOMs` token.
- Build verification:
  - ran three LuaLaTeX passes after the source expansion and title polish;
  - final compiled draft: 68 pages and 609,795 bytes;
  - PDF SHA-256:
    `64889EEABB6907C88EED9279DC062D89B20CF03A4AE5BDFED6102116CAFDE667`;
  - no fatal LaTeX errors, undefined controls, undefined citations, undefined
    references, Biber rerun requests, or label-rerun requests remain;
  - existing non-fatal front-matter, earlier-chapter table, appendix query, and
    bibliography URL warnings remain unchanged;
  - Chapter 5 introduced no overfull-box warning.
- Visual QA:
  - rendered the changed pages at 140 DPI to
    `tmp/pdfs/master-ch5-2026-06-21`;
  - inspected physical PDF pages 15--16 and 49--60, covering the research
    questions, expanded Chapter 4 mapping, framework transition, part divider,
    all Chapter 5 pages, both longtables, and closing remarks;
  - corrected the initially hyphenated Chapter 5 display title and rerendered
    the final opener;
  - found no clipping, overlap, broken table, unreadable text, missing content,
    or incoherent page transition.
- Deliverables:
  - compiled PDF:
    `thesis/Master_compiled_draft_chapter5_conclusion_2026-06-21.pdf`;
  - PDF output copy:
    `output/pdf/master-thesis-chapter5-conclusion-2026-06-21.pdf`;
  - Overleaf/TeXPage source ZIP:
    `thesis/master-overleaf-chapter5-conclusion-2026-06-21.zip`;
  - ZIP entries: 21, with `main.tex` at the root and no build artifacts;
  - ZIP SHA-256:
    `833E147E26D8FCCF7C5B1C7A06C629138827BC53643FEB6316E06B987E2FCE46`.
- Updated checkpoint:
  - Chapter 4 is approved after evidence, PFE-overlap, and render audits;
  - Chapter 5 is drafted and rendered but remains unapproved until the
    introduction, abstracts, and whole-thesis contribution framing are
    consistent;
  - active work moves to Chapter 1 framing completion and final consistency QA.
- Unresolved items:
  - supervisor approval of the provisional title and research questions;
  - seven Tier B records still need local full-text verification before strong
    synthesis;
  - Chapter 3 still needs final evidence and PFE-overlap polish;
  - Chapter 1 Motivation, Scope, and Thesis Organization remain empty;
  - student, supervisor, defense date, dedication, acknowledgements, and
    translated abstracts remain explicit administrative or drafting
    placeholders.
- Exact next action: Draft Chapter 1's Motivation, Scope, and Thesis
  Organization sections, then compare the introduction, Chapter 5, and
  abstracts for contribution and scope consistency.

## 2026-06-21 - Master - Chapter 1 framing and consistency audit completed

- Objective:
  - complete Chapter 1's empty Motivation, Scope, and Thesis Organization
    sections;
  - align the introduction's objectives and contributions with Chapter 5;
  - compare the introduction, conclusion, and English abstract for consistent
    contribution, case-study, uncertainty, and scope claims.
- Chapter 1 changes:
  - expanded Motivation to distinguish build-generated metadata from
    reconstructed binary evidence and explain the security consequences of
    unsupported exact-version claims;
  - defined a trustworthy reconstructed claim operationally through visible
    identity/version strength, evidence, provenance, transformation exposure,
    uncertainty, validation context, and permitted downstream use;
  - expanded Objectives and Contributions into the same six contribution
    classes summarized in Chapter 5;
  - stated explicitly that the software implementation and detailed
    engineering evaluation belong to the PFE rather than constituting a
    second master implementation or experiment campaign;
  - completed Scope with included evidence/review topics and exclusions for
    universal calibration, complete dependency recovery, native attribution,
    runtime-loaded code, protected payloads, and unsupported domains;
  - completed Thesis Organization with a paragraph for Chapters 2--5 and the
    review-protocol appendix.
- Abstract and transition polish:
  - changed the English abstract from the ambiguous phrase “generated SBOM”
    to “syntactically valid SBOM”;
  - aligned the case-study lane vocabulary with Chapters 4 and 5:
    controlled, clean/partial source-validated, source-known upper-bound,
    experiment-only, report-only, and boundary evidence;
  - changed the Chapter 2 display title to a deliberate two-line break while
    preserving its short table-of-contents and running-header title.
- Consistency and overlap checks:
  - Chapter 1, Chapter 5, and the English abstract now agree that the central
    contribution is the evidence-based attribution framework, not the PFE
    implementation;
  - all three surfaces preserve provenance, validation, abstention, boundary,
    conceptual-framework, and bounded-PFE-case-study language;
  - exact 12-word overlap scanning found zero matches between the master
    introduction and the PFE introduction/conclusion;
  - exact 12-word overlap scanning found zero duplicated prose between the
    master introduction and conclusion;
  - changed files are ASCII-only, structurally balanced, and contain no
    `TODO`, `TBD`, `FIXME`, or accidental `\SBOMs` token.
- Build verification:
  - ran an initial and stabilizing LuaLaTeX pass, followed by a final pass
    after the Chapter 2 title polish;
  - final compiled draft: 70 pages and 619,827 bytes;
  - PDF SHA-256:
    `50E968A90B7C8E720FC2B86D9E9F274952A1C8EFCFBB20B5C0B18832325092B8`;
  - no fatal LaTeX errors, undefined controls, undefined citations, undefined
    references, Biber rerun requests, or label-rerun requests remain;
  - Chapter 1 introduced no overfull-box warning; the existing warnings remain
    confined to earlier known tables, the review-protocol query, the small
    Chapter 4 inline-code line, and the SPDX bibliography URL.
- Visual QA:
  - rendered the English abstract and physical PDF pages 14--20 at 140 DPI to
    `tmp/pdfs/master-ch1-2026-06-21`;
  - inspected the abstract, part divider, all four Chapter 1 body pages,
    Chapter 1-to-Part II transition, and Chapter 2 opener;
  - corrected the initial automatic split inside “Methodology” and rerendered
    the Chapter 2 opener;
  - found no clipping, overlap, broken list, unreadable text, missing content,
    or incoherent transition.
- Deliverables:
  - compiled PDF:
    `thesis/Master_compiled_draft_chapter1_framing_2026-06-21.pdf`;
  - PDF output copy:
    `output/pdf/master-thesis-chapter1-framing-2026-06-21.pdf`;
  - Overleaf/TeXPage source ZIP:
    `thesis/master-overleaf-chapter1-framing-2026-06-21.zip`;
  - ZIP entries: 21, with `main.tex` at the root and no build artifacts;
  - ZIP SHA-256:
    `8EA0546288312B001B87DE7D7147178CE9191C5EE1DF9A734BD747D244D5A141`.
- Updated checkpoint:
  - Chapter 1 is approved after framing, consistency, overlap, structure, and
    render audits;
  - Chapter 5 is approved because its contribution and scope claims now match
    the introduction and English abstract;
  - active work moves to Chapter 3's Tier A evidence and PFE-overlap polish.
- Unresolved items:
  - supervisor approval of the provisional master title and research
    questions;
  - seven Tier B records still need local full-text verification before strong
    synthesis;
  - Chapter 3 still needs final Tier A evidence and PFE-overlap polish;
  - French and Arabic abstracts remain placeholders;
  - student, supervisor, defense date, dedication, and acknowledgements remain
    explicit administrative or drafting placeholders.
- Exact next action: Audit Chapter 3 against the Tier A extraction notes and
  PFE overlap, then correct any evidence wording or table presentation issues
  and rerender the affected pages.

## 2026-06-21 - Master - Chapter 3 Tier A evidence and overlap audit completed

- Objective:
  - reconcile Chapter 3 with the frozen 13-study Tier A corpus;
  - keep original-paper claims separate from later benchmark observations;
  - verify that Tier B records do not independently support precise claims;
  - complete the final prose-overlap and rendered-page approval gates.
- Evidence audit:
  - checked all 13 Tier A publication units against the frozen structured
    review protocol and local full texts;
  - confirmed 13/13 Tier A citation coverage in Chapter 3;
  - confirmed that the only non-Tier-A citation is the official Android
    shrinking documentation used for transformation context;
  - found no Tier B publication supporting an independent precise
    quantitative conclusion;
  - recorded explicitly that unreported fields remain not reported rather
    than inferred and that original claims remain separate from cross-tool
    observations.
- Chapter 3 corrections:
  - described LibScout similarity as graded matching rather than assigning a
    broader partial-evidence interpretation;
  - clarified that LibID uses binary integer programming for consistent class
    correspondence and identifies specific versions under its tested
    shrinking and package-modification conditions;
  - replaced generic LibHunter wording with its call-site-optimization feature
    enhancement and cross-inlining method matching;
  - bounded LibAttention to binary presence output without claiming an
    explicit class or library-boundary mapping;
  - strengthened the comparative table's supported-role and no-inference
    language.
- Overlap and source checks:
  - exact 12-word overlap between master Chapter 3 and PFE Chapter 4: zero;
  - exact 8-word overlap between master Chapter 3 and PFE Chapter 4: zero;
  - placeholder scan: zero `TODO`, `TBD`, `[REF]`, or `PLACEHOLDER` markers;
  - non-ASCII scan: zero matches.
- Build verification:
  - ran LuaLaTeX, Biber, LuaLaTeX, and a final LuaLaTeX stabilization pass;
  - final compiled draft: 70 pages and 620,445 bytes;
  - PDF SHA-256:
    `159C20F973C4EE07824A84B96429D362467042AC301FB5B498B0025F74B730DF`;
  - no fatal LaTeX errors, undefined controls, undefined citations, undefined
    references, Biber rerun requests, or label-rerun requests remain;
  - existing cosmetic warnings remain limited to narrow longtable columns,
    earlier known tables, the review-protocol query, the small Chapter 4
    inline-code line, and the SPDX bibliography URL.
- Visual QA:
  - located Chapter 3 at physical PDF pages 26--38;
  - rendered the complete span at 140 DPI to
    `tmp/pdfs/master-ch3-audit-2026-06-21`;
  - inspected the contact sheet and full-resolution pages containing the
    revised introduction, representative approaches, LibAttention boundary
    statement, and both halves of the Tier A comparison table;
  - found no clipping, overlap, broken row, unreadable text, or missing
    content.
- Deliverables:
  - compiled PDF:
    `thesis/Master_compiled_draft_chapter3_audit_2026-06-21.pdf`;
  - PDF output copy:
    `output/pdf/master-thesis-chapter3-audit-2026-06-21.pdf`;
  - Overleaf/TeXPage source ZIP:
    `thesis/master-overleaf-chapter3-audit-2026-06-21.zip`;
  - ZIP entries: 21, with `main.tex` at the root, zero build artifacts, and
    forward-slash entry names;
  - ZIP SHA-256:
    `37AB182036431C20D030F3442364F583C116C1ED6CB5AE615AC0840225446CB9`.
- Updated checkpoint:
  - Chapter 3 is approved after Tier A evidence, citation, Tier B boundary,
    PFE-overlap, build, and render audits;
  - Chapters 1, 4, and 5 remain approved;
  - active work moves to Chapter 2's review-method consistency and
    PFE-overlap audit.
- Unresolved items:
  - supervisor approval of the provisional master title and research
    questions;
  - seven Tier B records still need local full-text verification before strong
    synthesis;
  - Chapter 2 still needs final review-method consistency and PFE-overlap QA;
  - French and Arabic abstracts remain placeholders;
  - student, supervisor, defense date, dedication, and acknowledgements remain
    explicit administrative or drafting placeholders.
- Exact next action: Audit Chapter 2 against the frozen structured-review
  protocol and Appendix A, check overlap with the PFE background/methodology
  chapters, then correct any inconsistent review or evidence wording and
  rerender the affected pages.

## 2026-06-21 - Master - Chapter 2 review-method consistency audit completed

- Objective:
  - audit Chapter 2 against the frozen structured-review protocol and
    Appendix A;
  - check role separation and prose overlap against the PFE introduction,
    technical background, and state-of-the-art chapters;
  - correct any review-method wording that overstated the pre-freeze audit
    trail.
- Methodology corrections:
  - clarified that the thesis preserves the canonical query and future
    database-specific recording requirements, not unrecoverable pre-freeze
    query executions or result counts;
  - clarified that full-text eligibility screening and structured extraction
    are complete for Tier A, while records without verified local full text
    remain Tier B pending that stage;
  - changed "locally available full texts" to "locally inspected full texts"
    for Tier A;
  - added an explicit threat-to-review sentence that the seed corpus cannot
    retroactively establish an exhaustive or PRISMA-style selection history;
  - mirrored the same screening and audit-trail boundaries in Appendix A;
  - added protocol clarification note 1.0a to
    `docs/thesis/MASTER_STRUCTURED_REVIEW_PROTOCOL.md`.
- Overlap and source checks:
  - exact 12-word overlap between master Chapter 2 and PFE Chapter 1: zero;
  - exact 8-word overlap between master Chapter 2 and PFE Chapter 1: zero;
  - exact 12-word overlap between master Chapter 2 and PFE Chapter 2: zero;
  - exact 8-word overlap between master Chapter 2 and PFE Chapter 2: zero;
  - exact 12-word overlap between master Chapter 2 and PFE Chapter 4: zero;
  - exact 8-word overlap between master Chapter 2 and PFE Chapter 4: zero;
  - Chapter 2 citation keys all resolve in the master bibliography;
  - placeholder scan of Chapter 2, Appendix A, and the protocol doc: zero
    `TODO`, `TBD`, `[REF]`, or `PLACEHOLDER` markers;
  - Chapter 2 and Appendix A source files are ASCII-only.
- Build verification:
  - ran LuaLaTeX, Biber, LuaLaTeX, and a final LuaLaTeX stabilization pass;
  - final compiled draft: 70 pages and 621,331 bytes;
  - PDF SHA-256:
    `B89049C5BD7CEB7E455F58AA283187201E8055642B5309B6F81D19CC9C3E830E`;
  - no fatal LaTeX errors, undefined controls, undefined citations, undefined
    references, Biber rerun requests, or label-rerun requests remain;
  - existing cosmetic warnings remain limited to narrow longtable columns,
    the review-protocol query, the small Chapter 4 inline-code line, and the
    SPDX bibliography URL.
- Visual QA:
  - located Chapter 2 at physical PDF pages 21--25 and Appendix A at pages
    63--68;
  - rendered both changed spans at 140 DPI to
    `tmp/pdfs/master-ch2-method-audit-2026-06-21`;
  - inspected the contact sheet and full-resolution pages containing the new
    Chapter 2 search/audit limitation, Tier A/Tier B screening language,
    threat-to-review paragraph, Appendix A canonical query note, and Appendix
    A evidence-tier clarification;
  - found no clipping, overlap, broken table, unreadable text, or missing
    content.
- Deliverables:
  - compiled PDF:
    `thesis/Master_compiled_draft_chapter2_method_audit_2026-06-21.pdf`;
  - PDF output copy:
    `output/pdf/master-thesis-chapter2-method-audit-2026-06-21.pdf`;
  - Overleaf/TeXPage source ZIP:
    `thesis/master-overleaf-chapter2-method-audit-2026-06-21.zip`;
  - ZIP entries: 21, with `main.tex` at the root, zero build artifacts, and
    forward-slash entry names;
  - ZIP SHA-256:
    `8C0C7931B4D45A23A5FA2A6BB0E8C8BCE0E3CC0C83C0621A04CF253AC119FB85`.
- Updated checkpoint:
  - Chapter 2 is approved after review-method, protocol, PFE-overlap, build,
    and render audits;
  - Chapters 1--5 and Appendix A are now approved;
  - active work moves to the French and Arabic front-matter abstracts.
- Unresolved items:
  - supervisor approval of the provisional master title and research
    questions;
  - seven Tier B records still need local full-text verification before strong
    synthesis;
  - French and Arabic abstracts remain placeholders;
  - student, supervisor, defense date, dedication, and acknowledgements remain
    explicit administrative or drafting placeholders.
- Exact next action: Rewrite the French and Arabic abstracts from the
  approved English abstract and thesis scope, then rerender and inspect the
  front matter pages.

## 2026-06-21 - Master - Multilingual abstract front matter completed

- Objective:
  - replace the French and Arabic abstract placeholders with translations
    derived from the approved English abstract;
  - rebuild, rerender, and visually inspect the front-matter pages.
- Chapter/subsection: Front matter, French resume and Arabic abstract.
- Status before:
  - Chapters 1--5 and Appendix A were approved after their evidence,
    overlap, build, and render audits;
  - the English abstract was approved;
  - French and Arabic abstracts still contained placeholders.
- Work completed:
  - rewrote the French abstract as a full three-paragraph resume plus
    keywords aligned with the English abstract;
  - rewrote the Arabic abstract as a full three-paragraph abstract plus
    keywords aligned with the English abstract;
  - preserved the existing polyglossia structure and Amiri Arabic rendering;
  - kept the abstract claims within the approved thesis scope: trustworthy
    SBOM recovery, evidence-based component attribution, bounded PFE case
    study, explicit uncertainty, provenance, abstention, and vulnerability
    authority boundaries.
- Files changed:
  - `thesis/master/frontmatter/abstract_fr.tex`
  - `thesis/master/frontmatter/abstract_ar.tex`
  - `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
  - `thesis/README.md`
- Project evidence used:
  - approved English abstract;
  - approved master thesis scope and contribution framing;
  - current master checkpoint and session log.
- Academic references added or verified: None; this was front-matter
  translation and rendering work.
- Figures/tables created: None.
- Checks performed:
  - placeholder scan of the French and Arabic abstract files: zero
    `thesisplaceholder`, `TODO`, `TBD`, `PLACEHOLDER`, or `[REF]` markers;
  - rebuilt with LuaLaTeX, Biber, LuaLaTeX, and a final LuaLaTeX pass;
  - final compiled draft: 70 pages and 637,948 bytes;
  - PDF SHA-256:
    `68224C642431D2D8D3292AE2F1E14A9BC52CFDAFBCEB83B10B07973AA30B8AE8`;
  - no fatal LaTeX errors, undefined controls, undefined citations,
    undefined references, Biber rerun requests, or label-rerun requests
    remain;
  - rendered physical PDF pages 1--7 at 150 DPI to
    `tmp/pdfs/master-frontmatter-abstracts-2026-06-21`;
  - inspected the contact sheet, the French abstract page, the Arabic abstract
    page, and the first contents page;
  - found no clipping, overlap, unreadable glyphs, broken page transition, or
    missing front-matter entry;
  - Overleaf/TeXPage ZIP verification: 21 entries, `main.tex` at the root,
    zero build artifacts, and zero backslash-separated entry names;
  - ZIP SHA-256:
    `29A9265E96A9FB0A99DC54A13A7B3E967DBAF2B9CE218AD548A0533A6A702593`.
- Deliverables:
  - compiled PDF:
    `thesis/Master_compiled_draft_frontmatter_abstracts_2026-06-21.pdf`;
  - PDF output copy:
    `output/pdf/master-thesis-frontmatter-abstracts-2026-06-21.pdf`;
  - Overleaf/TeXPage source ZIP:
    `thesis/master-overleaf-frontmatter-abstracts-2026-06-21.zip`.
- Decisions made:
  - treat the French and Arabic abstracts as thesis-source complete and
    render-verified, while leaving human language review available if the
    supervisor requests it;
  - keep the remaining administrative placeholders explicit rather than
    inventing student, supervisor, defense-date, dedication, or
    acknowledgement text.
- Unresolved items:
  - supervisor approval of the provisional master title and research
    questions;
  - seven Tier B records still need local full-text verification before strong
    synthesis;
  - student, supervisor, defense date, dedication, and acknowledgements remain
    administrative placeholders.
- Exact next action: Resolve the remaining administrative front-matter
  placeholders, then rerender and inspect the title, dedication, and
  acknowledgements pages.

## 2026-06-21 - Master - Administrative front matter drafted and rendered

- Objective:
  - fill the master front matter with confirmed personal values where the
    repository already contains them;
  - replace the dedication and acknowledgements placeholders with complete
    draft text;
  - rebuild, rerender, and inspect the title, dedication, and
    acknowledgements pages.
- Chapter/subsection: Front matter, title-page metadata, dedication, and
  acknowledgements.
- Status before:
  - French and Arabic abstracts were complete and render-verified;
  - master metadata still had student, supervisor, and defense-date
    placeholders;
  - dedication and acknowledgements still had placeholders.
- Work completed:
  - filled the confirmed student name `Fendi Mohamed`;
  - filled the confirmed supervisor name `Serai Abdelhak`;
  - kept the final defense date as an explicit placeholder because the PFE
    checklist and metadata also show that the exact date is still unavailable;
  - replaced the dedication placeholder with the complete dedication draft
    already used on the PFE side;
  - replaced the acknowledgements placeholder with a master-appropriate
    acknowledgement draft adapted from the existing PFE front matter.
- Files changed:
  - `thesis/master/metadata.tex`
  - `thesis/master/frontmatter/dedication.tex`
  - `thesis/master/frontmatter/acknowledgements.tex`
  - `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
  - `thesis/README.md`
- Project evidence used:
  - `thesis/pfe/metadata.tex`
  - `thesis/pfe/frontmatter/dedication.tex`
  - `thesis/pfe/frontmatter/acknowledgements.tex`
  - `docs/thesis/PFE_PERSONAL_FRONT_MATTER_CHECKLIST.md`
- Academic references added or verified: None; this was administrative
  front-matter work.
- Figures/tables created: None.
- Checks performed:
  - rebuilt with LuaLaTeX, Biber, LuaLaTeX, and a final LuaLaTeX pass;
  - final compiled draft: 70 pages and 634,325 bytes;
  - PDF SHA-256:
    `75D9F44B2B500583C59DB63B76233C6CF8C24BD7BAF1EBEBF1176882CF1B51A0`;
  - no fatal LaTeX errors, undefined controls, undefined citations,
    undefined references, Biber rerun requests, or label-rerun requests
    remain;
  - placeholder scan of the edited front matter found only the intentional
    `\DefenseDate` placeholder;
  - rendered physical PDF pages 1--3 at 150 DPI to
    `tmp/pdfs/master-frontmatter-admin-2026-06-21`;
  - inspected the title page, dedication page, and acknowledgements page;
  - found no clipping, overlap, unreadable text, broken page transition, or
    malformed name rendering;
  - Overleaf/TeXPage ZIP verification: 21 entries, `main.tex` at the root,
    zero build artifacts, and zero backslash-separated entry names;
  - ZIP SHA-256:
    `0EE5BA2BC3A49D68F2BA74735EA557D2FA3D16F069AC2BCF619202BAD9C63A28`.
- Deliverables:
  - compiled PDF:
    `thesis/Master_compiled_draft_frontmatter_admin_2026-06-21.pdf`;
  - PDF output copy:
    `output/pdf/master-thesis-frontmatter-admin-2026-06-21.pdf`;
  - Overleaf/TeXPage source ZIP:
    `thesis/master-overleaf-frontmatter-admin-2026-06-21.zip`.
- Decisions made:
  - use only confirmed repository-backed names;
  - keep the defense date visibly pending rather than guessing a date;
  - treat the dedication and acknowledgements as complete drafts pending final
    student approval of personal wording.
- Unresolved items:
  - final defense date;
  - supervisor approval of the provisional master title and research
    questions;
  - seven Tier B records still need local full-text verification before strong
    synthesis.
- Exact next action: Obtain the final defense date, fill `\DefenseDate` in
  `thesis/master/metadata.tex`, then rerender the title page and build the
  final front-matter export candidate.

## 2026-06-21 - Shared - PFE and master cover pages matched to school template

- Objective:
  - redesign the PFE and master title pages so their `page de garde` follows
    the ESI examples provided by the student screenshots;
  - keep existing thesis metadata and preserve visible placeholders for
    administrative values that are still unknown.
- Chapter/subsection: PFE and master front matter, title pages.
- Status before:
  - both title pages used a simpler ruled layout with a reduced institutional
    header;
  - the PFE had jury placeholders, while the master title page did not yet
    expose a full jury block.
- Work completed:
  - rebuilt the PFE cover with Arabic/English institutional lines, centered ESI
    logo, `Engineering's Thesis`, State Engineer diploma wording, theme rules,
    presenter block, submission date, jury table, and academic year;
  - rebuilt the master cover with Arabic/French institutional lines, centered
    ESI logo, `THESIS`, Master diploma wording, theme rules, presenter block,
    submission date, jury table, and academic year;
  - added master metadata commands for jury president, co-supervisor, and
    examiner as explicit placeholders rather than guessing names.
- Files changed:
  - `thesis/pfe/frontmatter/titlepage.tex`
  - `thesis/master/frontmatter/titlepage.tex`
  - `thesis/master/metadata.tex`
  - `docs/thesis/THESIS_WRITING_SESSION_LOG.md`
  - `thesis/README.md`
- Checks performed:
  - rebuilt `thesis/pfe/main.pdf` with MiKTeX LuaLaTeX: 139 pages,
    1,923,196 bytes;
  - rebuilt `thesis/master/main.pdf` with MiKTeX LuaLaTeX: 70 pages,
    637,288 bytes;
  - rendered physical PDF page 1 for both documents with Poppler to:
    `tmp/pdfs/pfe-cover-template-2026-06-21-001.png` and
    `tmp/pdfs/master-cover-template-2026-06-21-01.png`;
  - visually inspected both rendered covers and found no clipping, overlap, or
    off-page content;
  - scanned the current logs for fatal errors, undefined controls, undefined
    references, and rerun requests; none were present.
- Deliverables:
  - `output/pdf/pfe-page-de-garde-template-2026-06-21.pdf`
  - `output/pdf/master-page-de-garde-template-2026-06-21.pdf`
  - `thesis/PFE_Fendi_Mohamed_page_de_garde_template_2026-06-21.pdf`
  - `thesis/Master_page_de_garde_template_2026-06-21.pdf`
- PDF SHA-256:
  - PFE:
    `3D525D2491F677F80F5D329EDC8C64EA73CA2920DAE580AC0BD3A807957C288E`
  - Master:
    `71D572E5E076BC2ED151E62DE0AB6F5BF194D101F45FE0B4A78C8C7378F2D29A`
- Unresolved items:
  - PFE jury president, examiner, and final submission/defense date remain
    placeholders;
  - master jury president, co-supervisor, examiner, and final submission date
    remain placeholders.
- Exact next action: Fill the remaining administrative names and dates in the
  metadata files, then rerender page 1 of each PDF before final submission.

## 2026-06-21 - Master - Expert evidence review and framework evaluation revision

- Objective:
  - review the master thesis as an academic researcher against the implemented
    PFE evidence;
  - correct unsupported literature descriptions and bibliography metadata;
  - replace the proposed-only framework evaluation with an audited case-study
    evaluation;
  - rebuild and visually verify the revised thesis.
- Main corrections:
  - corrected ORLIS from an inaccurate CFG/Jaccard description to its actual
    call-graph-derived features, `sdhash` filtering, `ssdeep` class digests,
    and injective class mapping;
  - corrected the Ramirez thesis dataset description: 75 ORLIS APKs, 75
    LIBLOOM APKs, and 50 manually selected Google Play APKs; removed the
    unsupported F-Droid/source-known and standard-SBOM claims;
  - verified and promoted TPL-Benchmark and UniBOM from Tier B to Tier A,
    bringing the corpus to 15 Tier A and five Tier B publication units;
  - added structured extraction records for both promoted studies;
  - completed the eight-question reporting-quality assessment for all current
    Tier A studies;
  - added foundational sources for SBOM minimum elements, supply-chain risk,
    empirical SBOM practice, W3C provenance, reject-option decisions,
    evidence theory, calibration, and VEX;
  - corrected LibScan page, publisher, and ISBN metadata and updated the
    Android R8 documentation URL/title.
- Framework evaluation:
  - added a seven-criterion case-study table covering evidence-lane separation,
    denominator separation, source-known upper-bound containment, negative
    controls, report-only AI/R8 containment, transformation-risk containment,
    and native/hidden-code boundaries;
  - preserved the audited evidence boundaries:
    `84/84` controlled, `47/47` clean real, `880/1790` partial real,
    `927/1837` emitted-version confirmation, `927/12082` full source-row
    recall, `6772/6772` source-known upper-bound emissions, four boundary
    cases excluded, and zero strict AI/R8 promotion candidates;
  - synchronized Chapter 5 and the English, French, and Arabic abstracts with
    the evaluated-framework conclusion.
- Files changed:
  - `thesis/master/bib/references.bib`
  - `thesis/master/chapters/ch02_background_methodology.tex`
  - `thesis/master/chapters/ch03_state_of_the_art_taxonomy.tex`
  - `thesis/master/chapters/ch04_evidence_trust_framework.tex`
  - `thesis/master/chapters/ch05_general_conclusion.tex`
  - `thesis/master/frontmatter/abstract_en.tex`
  - `thesis/master/frontmatter/abstract_fr.tex`
  - `thesis/master/frontmatter/abstract_ar.tex`
  - `thesis/master/appendices/appendix_a_review_protocol.tex`
  - `thesis/master/preamble/packages.tex`
  - `papers/data/orlis.json`
  - `papers/data/papers_overview.json`
  - `papers/data/SBOM_Tools_Synthesis_Table.md`
  - `papers/data/tpl_benchmark.json`
  - `papers/data/unibom.json`
  - `papers/state_of_the_art.md`
  - `docs/thesis/MASTER_STRUCTURED_REVIEW_PROTOCOL.md`
  - `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`
  - `thesis/README.md`
- Checks performed:
  - downloaded and locally inspected arXiv full texts 2509.04091 and
    2511.22359;
  - validated all edited JSON records;
  - rebuilt with MiKTeX LuaLaTeX, Biber, and two final LuaLaTeX passes;
  - final PDF: 74 pages, 675,386 bytes;
  - no fatal LaTeX errors, undefined citations, undefined references, Biber
    rerun requests, or label-rerun requests remain;
  - remaining overfull warnings are limited to approximately 2.5-point table
    alignments and one sub-1-point prose line;
  - rendered and inspected the English, French, and Arabic abstracts, revised
    literature pages, complete framework-evaluation table, general conclusion,
    quality-assessment table, selected-study status table, protocol change
    note, and bibliography;
  - found no clipping, overlap, off-page content, malformed Arabic rendering,
    or unreadable table cells.
- Deliverables:
  - `thesis/Master_Fendi_Mohamed_evidence_review_2026-06-21.pdf`
  - `output/pdf/master-thesis-evidence-review-2026-06-21.pdf`
- PDF SHA-256:
  - `EB4716CC4B9FAF6C6F612F93B3006142EBF066554EDADCE941036323E3BDB272`
- Unresolved items:
  - supervisor approval of the provisional title and research questions;
  - jury president, examiner, and final defense/submission date;
  - five Tier B records remain supplementary and cannot independently support
    precise claims.
- Exact next action: Send the evidence-review PDF to the supervisor, obtain
  academic and administrative approvals, update `thesis/master/metadata.tex`,
  then rebuild the final submission PDF and source ZIP.
