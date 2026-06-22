# Thesis Writing and Resumption Rules

## Status of This Document

This is the binding operating guide for writing or resuming the PFE and master
theses. It applies to human and AI-assisted work.

The document-specific plans remain authoritative for chapter structure:

- `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
- `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`

If a future writing session begins without reading this file and the relevant
plan, it is not ready to modify thesis content.

## 1. Instruction Priority

When instructions or sources disagree, use this order:

1. The user's latest explicit instruction.
2. An approved supervisor requirement.
3. The relevant thesis writing plan.
4. This shared rules file.
5. Current generated project evidence and implementation.
6. Primary academic papers, standards, and official documentation.
7. Existing thesis drafts.
8. Old planning documents.
9. Previous school reports, which are style examples only.

Never preserve an older thesis sentence merely because it is already written.
Correctness, evidence, and the approved structure have priority.

## 2. Mandatory Startup Protocol

Before writing or resuming either thesis:

1. Identify whether the task concerns the PFE, the master thesis, or shared
   material.
2. Read the relevant thesis plan completely.
3. Read the `Current Writing Checkpoint` in that plan.
4. Read the latest relevant entries in
   `docs/thesis/THESIS_WRITING_SESSION_LOG.md`.
5. Read this shared rules file.
6. Inspect the working tree and preserve unrelated user changes.
7. Read the existing target chapter before editing it.
8. Identify the claims, figures, tables, and references required by the planned
   subsection.
9. Refresh any time-sensitive project results from current generated artifacts.
10. State the bounded writing objective for the session.

Do not restart from Chapter 1 merely because a new session or context window
began. Resume from the recorded checkpoint unless the user changes the plan.

## 3. Source-of-Truth Hierarchy for Project Claims

For current project status and evaluation claims, prefer:

1. Generated JSON/CSV evaluation artifacts.
2. Generated evaluation dashboards and tables.
3. Current implementation and tests.
4. `TASKS.md` and `docs/codex/CODEX_CONTEXT.md`.
5. `docs/thesis/THESIS_ARTIFACT_INDEX.md`.
6. Project handbook explanations.
7. Existing prose drafts.
8. Historical planning files.

Any count, percentage, dataset size, model result, or experiment status that
could have changed must be verified before it is inserted into thesis prose.

## 4. Evidence Classes Must Remain Separate

Never merge the following classes:

- controlled ground truth;
- clean source-validated real APKs;
- partial source-validated real APKs;
- source-known constrained upper-bound evaluation;
- report-only evidence;
- experiment-only evidence;
- rejected or failed experiments;
- limitation and boundary cases.

Every result paragraph and table must identify its evidence class and
denominator.

## 5. Claim Construction Rule

Every important project claim should be writable in this form:

```text
claim
-> evidence class
-> metric and denominator
-> supporting artifact
-> limitation
-> permitted interpretation
```

If one of these elements is missing, weaken the claim or postpone it.

Examples of forbidden shortcuts:

- “The tool has 100% accuracy on real APKs.”
- “The AI identifies library versions.”
- “The system detects all dependencies.”
- “A detected component is vulnerable” when its exact version is uncertain.

## 6. PFE and Master Separation Rule

### PFE

The PFE answers:

> What was designed, implemented, evaluated, and learned?

It may contain:

- architecture;
- implementation;
- commands;
- experimental protocol;
- results;
- failed experiments;
- screenshots;
- engineering decisions.

### Master

The master thesis answers:

> What general research framework or understanding can be derived from the
> problem and project evidence?

It may contain:

- structured literature review;
- taxonomies;
- evidence and provenance concepts;
- conceptual framework;
- selected PFE case studies;
- research limitations and directions.

The master must not become a shortened PFE implementation report. The PFE must
not become a purely theoretical survey.

## 7. Writing Style Rules

- Use formal academic prose in the selected thesis language.
- Prefer precise sentences over decorative language.
- Introduce one concept before using it.
- Define specialized terms once and use them consistently.
- Keep paragraph purpose clear: claim, explanation, evidence, or transition.
- Avoid repeated introductions to the same concept across chapters.
- Avoid unsupported superlatives such as “novel”, “best”, “robust”, or
  “state-of-the-art”.
- Distinguish “proposed”, “implemented”, “evaluated”, “observed”, and
  “demonstrated”.
- Do not describe planned work in the past tense.
- Do not describe report-only work as production behavior.
- End every chapter with a synthesis and a transition to the next chapter.

## 8. Citation Rules

- Cite definitions, standards, external facts, algorithms, datasets, and
  comparative performance claims.
- Prefer original papers, standards, and official documentation.
- Cite a survey for synthesis, but return to the original paper for a method's
  detailed claims whenever possible.
- Do not invent references, authors, venues, DOIs, dates, or page numbers.
- Verify every bibliography entry before final submission.
- A paragraph with several distinct external claims may require several
  references.
- Internal project files are evidence sources, not replacements for academic
  citations.
- Web sources should be limited to official documentation and clearly separated
  from academic references if the school template requires a webography.

## 9. Originality and Anti-Plagiarism Rules

- Previous school theses are layout and style references only.
- Do not copy their sentences, paragraph structures, diagrams, or tables.
- Do not paraphrase a source by replacing isolated words.
- Read the source, close it, write the idea independently, then verify accuracy
  and add the citation.
- Mark direct quotations explicitly and use them rarely.
- Redraw external diagrams when useful and label them “adapted from”.
- Record the source of every borrowed visual.
- Check phrase overlap against school reports, source papers, and the other
  thesis.
- Self-reuse between PFE and master must be deliberate, limited, and reframed.
- Reused PFE figures or case evidence in the master must be identified as
  adapted from or derived from the PFE project.

## 10. Literature Review Rules

- Define the review question before collecting papers.
- Record search terms, inclusion criteria, exclusion criteria, and extraction
  fields.
- Compare papers using the same dimensions.
- Do not compare percentages from incompatible datasets as if they were a
  ranking.
- Separate library-level from version-level results.
- Separate reported benchmark performance from realistic benchmark findings.
- Record whether tools and datasets are publicly available.
- Include negative findings and methodological limitations.
- Synthesize papers by technique or research question instead of writing a long
  sequence of isolated summaries.

## 11. Figures, Tables, and Diagram Rules

- Every figure and table must serve a specific argument.
- Every figure and table must be introduced and interpreted in the text.
- Captions must explain what is shown, not merely repeat the title.
- Use consistent visual vocabulary across both theses.
- Prefer vector diagrams for architecture, flow, UML, and taxonomies.
- Ensure all text remains readable when printed.
- Do not include generic technology logos unless they communicate a meaningful
  relationship.
- Do not use screenshots as architecture diagrams.
- Screenshots must hide irrelevant personal or machine-specific information.
- Tables must state units, denominators, dataset, and evidence class where
  applicable.
- Large comparison tables should move to appendices when they damage
  readability.

## 12. Metrics and Results Rules

Before writing a result:

1. Define the metric.
2. Define the numerator.
3. Define the denominator.
4. Identify exclusions.
5. Identify the dataset and evidence class.
6. Link the generated artifact.
7. State the permitted interpretation.
8. State the principal limitation.

Do not silently round values differently across chapters, abstracts, tables,
and slides.

If the underlying evaluation changes, search and synchronize all thesis-facing
surfaces in the same pass.

## 13. AI/ML Reporting Rules

- Report the train, validation, test, and held-out strategy.
- State whether splits are random, grouped, case-heldout, or temporal.
- Report class balance and relevant baselines.
- Prefer macro-F1 for imbalanced multiclass results and explain why.
- Discuss leakage and shortcut risks.
- Do not select only the strongest model result.
- Preserve failed models and negative baselines when they affect conclusions.
- Keep the project authority boundary visible: AI is report-only unless a later
  validated project decision changes that status.

## 14. Chapter Writing Workflow

Each chapter passes through these states:

1. **Outlined** - sections, purpose, evidence, and references identified.
2. **Evidence-ready** - required artifacts and sources collected.
3. **Drafted** - complete prose exists without placeholders.
4. **Evidence-audited** - claims and numbers checked.
5. **Citation-audited** - external claims and bibliography checked.
6. **Structure-audited** - no duplication; transitions are clear.
7. **Rendered** - figures, tables, references, and layout visually checked.
8. **Approved baseline** - suitable for later refinement without structural
   rewriting.

Do not mark a chapter complete merely because prose exists.

## 15. Subsection Completion Checklist

Before leaving a subsection:

- Its purpose is clear.
- It supports the chapter objective.
- Terminology is consistent.
- Claims are supported.
- References exist and are verified.
- Project evidence is current.
- Limitations are visible.
- No placeholder such as `TODO`, `TBD`, `[REF]`, or invented number remains.
- Figures and tables are referenced in order.
- The next subsection follows logically.

## 16. End-of-Session Protocol

At the end of every thesis-writing session:

1. Run formatting and consistency checks.
2. Compile/render the affected document when a LaTeX structure exists.
3. Inspect the modified pages visually.
4. Update the relevant plan's `Current Writing Checkpoint`.
5. Append an entry to `docs/thesis/THESIS_WRITING_SESSION_LOG.md`.
6. Record:
   - document;
   - chapter/subsection;
   - files changed;
   - evidence used;
   - references added;
   - unresolved questions;
   - exact next action.
7. Do not mark work complete if required verification remains.

## 17. Resumption Protocol

When the user says “continue”, “resume”, or returns after context compaction:

1. Read the relevant checkpoint and latest session-log entry.
2. Verify the referenced files still exist.
3. Inspect current uncommitted changes.
4. Re-read the last modified subsection.
5. Verify time-sensitive evidence.
6. Continue the recorded next action.
7. Do not rewrite approved sections unless new evidence or user direction
   requires it.

## 18. When to Stop and Ask

Ask the user or supervisor when:

- the thesis language is not fixed;
- an institutional template requirement is unknown and materially affects
  structure;
- the supervisor changes the approved chapter organization;
- a topic/title decision would change the master research contribution;
- personal cover-page information is required;
- a claim depends on unavailable or contradictory evidence;
- a major scope expansion is proposed.

Do not stop for minor wording choices that can be resolved consistently from
the plans.

## 19. File and Version-Control Rules

- Keep PFE and master source files in separate directories.
- Share bibliography, glossary, and reusable project-owned figures only where
  appropriate.
- Do not overwrite evidence artifacts manually.
- Do not edit generated evaluation files to make thesis numbers match.
- Preserve unrelated user changes.
- Use descriptive commits by chapter or artifact group.
- Before final submission, tag or archive the exact thesis and evidence
  snapshot.

## 20. Definition of a Successful Writing Session

A session is successful when it:

- advances a bounded planned section;
- leaves claims better supported than before;
- preserves PFE/master separation;
- records its evidence and references;
- updates the checkpoint and session log;
- leaves an exact next action for resumption.

