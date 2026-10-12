# Paper Writing Rules

These rules govern every writing or revision session for the implementation and
evaluation paper in `papers/`. The user's latest instruction and supervisor's
requirements take priority over this file.

## 1. Startup and resumption

Before each paper-writing session:

1. Read `papers/implementation_evaluation_paper_plan.md` and this file.
2. Read the current paper checkpoint and latest paper-session log entry, if a
   log exists.
3. Inspect the files and generated artifacts relevant to the proposed change.
4. Confirm the bounded objective and the section being changed.
5. Check whether evidence, code, literature, or venue requirements have changed
   since the previous session.
6. Read the full current target section before revising it; preserve sound
   material and avoid restarting completed work.

Do not draft a numerical result from memory or from an old abstract. If a
required artifact is unavailable, keep the claim provisional and record the
missing input.

## 2. Authority and sources

When sources disagree, use this order:

1. The user's latest explicit instruction and approved supervisor requirements.
2. The paper plan and these rules.
3. Current machine-readable evaluation outputs and frozen run manifests.
4. Current implementation, tests, and command-line behavior.
5. Current project evidence indexes and evaluation tables.
6. Original academic papers, standards, and official documentation.
7. Thesis prose, project notes, handoff documents, and historic summaries.

Project Markdown is a map to evidence, not a replacement for the evidence.
For scientific and comparative claims, verify the original paper or
authoritative source. Use the web when a referenced publication, standard,
tool, API, benchmark, venue requirement, or other changeable fact needs
verification.

## 3. Claim evidence contract

Every empirical or comparative claim must be recorded in this form before it
enters the manuscript:

```text
claim
-> evidence class
-> numerator and denominator / unit
-> exact supporting artifact and snapshot
-> limitations and exclusions
-> permitted interpretation
```

If any part is missing, either weaken the statement, mark it provisional, or
defer it. Keep internal project evidence distinct from external academic
citations.

## 4. Evaluation-lane boundaries

Never merge these evidence classes into one score:

- controlled APK ground truth;
- clean source-validated APKs;
- partial source-validated APKs;
- no-Maven-signal controls;
- full source dependency denominator analysis;
- source-version-constrained upper-bound evaluation;
- report-only or experiment-only results;
- rejected/failed experiments;
- native, hidden-code, packed, and other limitation cases.

Rules for current project metrics:

- Call `927/1837` the documented **emitted Maven version confirmation rate**
  across 102 source-validated APKs; do not call it full dependency recall or
  general APK accuracy.
- Show the clean (`47/47`, five APKs) and partial (`880/1790`, 97 APKs) strata
  with their denominators.
- Use `927/12082` as source-denominator coverage for the reconciled 106-case
  source-tree layer; keep the 102-emitting-case metric and 110-case
  transparency inventory separate, and state row semantics/exclusions.
- Describe `6772/6772` as a **source-version-constrained upper-bound** result.
  The source-known version restriction must appear in the same table or
  paragraph as the result.
- Do not count zero-emission controls in emitted-row rates; report them
  separately as no-signal controls.
- Do not turn controlled fixture results into claims about all real APKs.
- State whether source dependency trees were resolved from original source or
  a validation-only copy, and list any material modifications.
- A Gradle runtime dependency tree is source-side evidence; do not imply that
  every resolved dependency is proven present in the final packaged APK.
- Treat the current numerical summaries as documented thesis/evaluation
  snapshots. If raw results, the reference DB, source copies, or run manifests
  are unavailable, disclose that independent recalculation is limited; do not
  imply that the experiments were rerun for the paper.

## 5. Reference database and data leakage

For every evaluation snapshot, record:

- artifact coordinates and versions in the reference DB;
- database build inputs, timestamp/version, row/component count, and hash;
- source used to choose each calibration or promotion candidate;
- whether each evaluated APK, app family, or source tag contributed to those
  candidates;
- all per-APK reference filters or constraints;
- the exact APK and source revision used for each evaluation row.

If an evaluated APK helped select its reference versions, do not describe that
row as independent held-out evaluation. Prefer leave-one-app-out or grouped
held-out results when feasible. If those are unavailable, disclose potential
reference-selection optimism and limit the interpretation to calibrated case
evidence.

The source-version-constrained run is an upper-bound analysis. Never present
its per-APK exact source references as the ordinary APK-only matcher input.

## 6. Literature review and research gap

- Describe the review as a structured mapping review unless a prospectively
  recorded protocol supports the term “systematic literature review.”
- Preserve search dates, databases, query families, inclusion/exclusion
  criteria, snowballing, screening counts, and extraction dimensions.
- Compare studies using common attributes: task, evidence, version-level
  support, transformations, output, datasets, ground truth, availability, and
  limitations.
- Separate library-level and version-level performance.
- Do not compare percentages across incompatible datasets as a leaderboard.
- Do not claim “no prior work,” “first,” “novel,” “best,” or “state of the art”
  unless a documented search and direct comparison justify the exact wording.
- Prefer synthesis by research question or technique over one paragraph per
  paper.
- Cite original papers for methods and results; cite surveys for broad framing.

## 7. Citations and originality

- Verify authors, title, year, venue, DOI/URL, publication status, and the
  specific claim supported before adding a reference.
- Cite definitions, standards, algorithms, datasets, external facts, and
  comparative results close to the supported statement.
- Never invent citations, page numbers, results, tool capabilities, or quotes.
- Paraphrase from understanding, not by replacing isolated words in source
  prose. Keep direct quotations rare and clearly marked.
- Do not copy school reports or other theses. Avoid unexamined self-reuse
  between the PFE, master thesis, and paper; cite or identify reused project
  material where required by the venue.
- Redraw adapted diagrams and cite their origin. Track sources for all visual
  assets.

## 8. Method and implementation accuracy

- Distinguish **proposed**, **implemented**, **enabled by default**,
  **optional**, **diagnostic**, **experiment-only**, and **report-only**.
- Describe the current matcher as weighted evidence fusion, not Bayesian
  inference or calibrated probability unless new implementation/evidence
  supports that description.
- Explain identity confidence separately from version confidence.
- Do not claim exact version authority solely from a high library-identity
  score.
- State that the AI/R8 assistants are report-only unless a later, validated
  decision explicitly changes their role.
- Native `.so` files are hash-only file components in the current MVP; do not
  imply native package/version attribution.
- Check all commands, options, defaults, and module descriptions against the
  current source before publication.

## 9. Metrics and statistics

Before reporting a metric, define:

1. target event and matching rule;
2. unit of analysis (APK, component, or coordinate/version row);
3. numerator and denominator;
4. exact dataset lane and database snapshot;
5. duplicate handling, exclusions, and missing cases;
6. whether samples are independent or grouped by app/family;
7. interpretation and primary limitation.

Use consistent rounding throughout abstract, text, tables, and figures. Show
counts with percentages. Do not substitute “accuracy,” “precision,” “recall,”
or “F1” for a custom confirmation rate. Do not claim statistical significance
without a suitable analysis and sampling basis.

## 10. AI/ML evidence

If AI results appear in the article:

- state the exact input representation and task labels;
- report train/validation/test construction, group or case separation, class
  balance, baselines, and macro-F1 where appropriate;
- discuss source-derived feature leakage and shortcut learning;
- distinguish structured project-evidence tokens from raw APK or raw opcode
  learning;
- include negative baselines and failed models when they qualify the result;
- preserve the report-only authority boundary in the abstract, results, and
  conclusion.

Do not add AI detail merely because models exist in the repository. It belongs
only if it answers an RQ or materially explains the system's decision policy.

## 11. Writing and structure

- Follow the supervisor's six-section sequence in the paper plan.
- Introduce each concept before relying on it; define terms once and use them
  consistently.
- Give every paragraph one purpose: claim, explanation, evidence, or
  transition.
- Use formal, direct academic prose. Avoid unsupported superlatives and
  promotional language.
- Keep Introduction and State of the Art complementary: the Introduction
  motivates; Section 3 substantiates and synthesizes.
- State each research question once in its final form, then map results and
  discussion to it explicitly.
- Keep Section 4 conceptual/methodological and Section 5 implementation and
  empirical. Avoid explaining the same architecture twice.
- Every table/figure must be introduced, interpreted, readable, and include
  units, denominators, and evidence class where relevant.
- Prefer original vector diagrams for architecture and evaluation flow.
- Follow venue rules for length, style, anonymization, artifact sharing, and
  supplementary material after the venue is selected.

## 12. Change control and end-of-session protocol

At the end of a writing session:

1. Check consistency among changed prose, tables, citations, and referenced
   artifacts.
2. Recompute or refresh any changed project result from source artifacts; do
   not edit generated outputs to match prose.
3. Check for placeholders, unsupported claims, outdated counts, broken links,
   and conflicting terminology.
4. Update the **Current checkpoint** in
   `papers/implementation_evaluation_paper_plan.md`.
5. Append a dated entry to `papers/PAPER_WRITING_SESSION_LOG.md` with objective,
   files changed, evidence used, checks made, unresolved items, and next action.
6. If LaTeX or another formatted manuscript exists, compile and inspect the
   affected pages before calling the section ready.

Do not mark the paper or a section complete while evidence, citation, or
reproducibility checks remain open.
