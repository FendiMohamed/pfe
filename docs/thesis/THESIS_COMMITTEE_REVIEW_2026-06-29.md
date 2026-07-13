# Committee-Style Review of the Master and Engineering Theses

Review date: 2026-06-29

Reviewed artifacts:

- Master thesis PDF: `C:\Users\PC CABA DZ\Downloads\main-master.pdf`
- Engineering/PFE thesis PDF: `C:\Users\PC CABA DZ\Downloads\main-pfe.pdf`
- Supporting LaTeX and evidence files in `C:\Users\PC CABA DZ\Documents\pfe-final`

## Scope and Method

I reviewed the two submitted PDFs independently as defense artifacts. I extracted page text, table of contents, captions, references, citation usage, and unresolved tokens; rendered representative pages; checked source `\cite{...}` keys against BibTeX; inspected the generated evaluation evidence that supports the PFE numbers; and spot-checked the most exposed state-of-the-art metrics against local primary PDFs.

External spot checks used public/primary-style records for recent works where relevant:

- TPL-Benchmark / Revisiting Third-Party Library Detection: https://arxiv.org/abs/2509.04091
- UniBOM DOI: https://doi.org/10.1145/3770501.3770512
- SAD DOI: https://doi.org/10.1145/3756681.3756933
- LibAttention DOI: https://doi.org/10.1109/SANER64311.2025.00028
- LibHunter DOI: https://doi.org/10.1145/3691620.3695554

The review is intentionally strict. Scores below are for the PDFs as submitted, not for the project potential after revision.

## Overall Verdict

The Engineering/PFE thesis is the stronger submission. It presents a real implemented system, a defensible evidence-gated methodology, concrete evaluation numbers, and unusually honest separation between controlled success, emitted-row confirmation, full source-denominator recall, upper-bound experiments, and report-only AI. It is defendable after fixing formal placeholders and tightening a few evaluation and reference issues.

The Master thesis is not yet convincing as a research-oriented thesis in its submitted PDF form. It contains a strong and well-written literature synthesis, but it does not actually deliver the conceptual framework and case-study evaluation promised by the abstract. It reads closer to a state-of-the-art survey plus conclusion than to a complete research thesis with methodology, contribution, evaluation, and discussion.

Critical submission blocker for both: the cover pages still contain visible red placeholders for final defense date, jury president, and examiner.

## Master Thesis Review

### Quick Facts

- Title: `Towards Trustworthy SBOM Recovery from Compiled Android Applications`
- PDF metadata: 48 pages, A4, created 2026-06-24.
- Approximate extracted words: 12,717.
- Main body structure in submitted PDF: introduction, background, state of the art/taxonomy, general conclusion, bibliography.
- Submitted PDF references: numeric references span `[1]` to `[36]`.

### Strengths

- The problem framing is mature: it correctly distinguishes a syntactically valid SBOM from an evidentially trustworthy SBOM.
- The taxonomy is useful and committee-relevant: technique families, evidence sources, transformation threats, and evaluation practices are the right axes.
- The writing is generally polished and academically toned.
- The thesis avoids a naive leaderboard and correctly warns against mixing incompatible precision/recall/F1 claims.
- Key recent works are included: LibHunter, LibAttention, SAD, TPL-Benchmark, UniBOM.

### Major Issues

| Issue | Severity | Why it is problematic | Recommendation |
|---|---:|---|---|
| Cover page contains red placeholders for defense date, jury president, and examiner. | Critical | A defense committee or administration can reject the PDF as unfinished before reading the content. | Fill all official values or remove placeholder rendering before submission. |
| Abstract promises a conceptual framework and implemented case-study evaluation, but the submitted body has no dedicated framework or evaluation chapter. | Critical | The central contribution claimed in the abstract is not delivered in the PDF. This is the most serious academic inconsistency. | Either include the missing framework/evaluation chapter, or rewrite the abstract/objectives so the thesis is honestly a structured literature review. |
| Scope section says the thesis "does not present an implemented detector" while the abstract says an implemented APK-to-SBOM system is used as a bounded case study. | Major | This contradiction will be easy for an examiner to expose. | Align scope, abstract, and conclusion. If the implementation is only a motivating case, say so and provide a short, bounded evidence appendix. |
| Review protocol is claimed but not sufficiently shown in the submitted PDF. | Major | Chapter 2 says it "froze" a structured mapping protocol, but the concrete search strings, databases, screening counts, quality rubric, and extracted-study table are not included in the PDF body. | Include the review protocol appendix in the submitted PDF, or add a concise protocol section with search dates, queries, counts, exclusion rules, and quality scoring. |
| No real methodology chapter for the proposed framework. | Major | A research thesis should explain how the framework was derived, validated, and bounded. The current text mostly synthesizes literature. | Add a methodology chapter: research design, extraction fields, coding process, claim model construction, validation strategy, and threats to validity. |
| No experiments or empirical evaluation in the submitted Master PDF. | Major | The user brief expects methodology, experimentation, results, and discussion. The submitted PDF has only synthesis/conclusion tables. | Add an evaluation chapter, even if qualitative: case-study mapping, coverage of framework fields, expert review, artifact audit, or controlled application to selected APK reports. |
| "15 Tier A studies" is asserted, but the submitted PDF does not provide the full audit trail. | Moderate | The count may be true in project files, but the reader cannot verify it from the PDF. | Add the frozen corpus table and quality scoring to the PDF. |
| Novelty is under-formalized. | Major | The contribution is phrased as "trustworthy claim model", but the model is not formal enough: no schema, no rules, no decision table beyond conclusion-level text. | Add a claim schema, claim classes, evidence hierarchy, confidence caps, vulnerability policy, and a worked example. |
| Some central terms are repeated without enough operational definition. | Moderate | "Trust", "authority", "evidence", "bounded claim", and "abstention" are good terms, but repetition without a formal model weakens rigor. | Define each term once, then use a table or notation consistently. |
| Figures and tables are readable but mostly descriptive. | Minor | Taxonomy tables help, but there are few diagrams showing the actual proposed framework. | Add one framework architecture figure and one example claim-lifecycle figure. |

### Scientific and Technical Quality

The scientific insight is good, but the submitted artifact is incomplete. The thesis understands the hard problem: binary-derived component claims have evidence limits, reference limits, version ambiguity, and security authority boundaries. However, it stops too early. A committee will likely ask: "Where is the actual framework?" and "How was it evaluated?"

### Objectives and Problem Statement

The problem statement is clear and defensible. The six research questions are appropriate. The weakness is not the problem framing; it is the lack of delivery against those questions.

### Structure and Flow

The flow is coherent as a survey: context -> background -> taxonomy -> conclusion. It is weak as a research thesis because the expected contribution chapter is missing. The existing source tree even contains a file named like a framework chapter, but the submitted `main.tex` does not include it.

### Literature Review and State of the Art

The literature coverage is strong for Android TPL detection and includes relevant recent works. Local spot checks confirmed that:

- TPL-Benchmark supports the cited 6,055 apps, 5,756 TPLs, 60.15% best library-level F1 for LibPecker, and 76.48% version-level recall for LibHunter.
- SAD supports the cited 97.64% library-level F1, 84.82% version-level F1, and 94.12% class-level F1, while also acknowledging optimization/inlining limitations.
- LibAttention supports R8-resilience and a 30%+ F1 improvement claim, but it is presence detection, not exact-version attribution. The thesis mostly treats this boundary correctly.

Weakness: the review should be auditable inside the thesis, not only in project files.

### Methodology and Evaluation

This is the weakest part. The PDF states methodological principles but does not provide enough process evidence. It also lacks experimental or case-study results in the body, despite claiming a bounded implemented case study in the abstract.

### Writing Quality

The prose is polished, precise, and academic. It is sometimes too repetitive and could be more concise. The main writing risk is not grammar; it is overclaiming the thesis contribution relative to what is included.

### Figures, Tables, Diagrams

The taxonomy tables are readable but dense. The rendered title page is clean except for placeholders. A few table columns use stretched spacing, but this is cosmetic. The larger issue is the absence of framework/evaluation figures.

### Novelty and Contribution

Potential contribution: evidence-qualified SBOM claim model for compiled Android APKs. Actual submitted contribution: structured state-of-the-art synthesis and research agenda. That is useful, but weaker than the abstract promises.

### Master Reference Audit

Mechanical audit:

- No unresolved citation markers were found in the PDF text.
- Source-level BibTeX audit found no undefined citation keys.
- Source-level BibTeX audit found unused entries: `androidAbi`, `androidSigning`.
- Many official web/spec references have no year/date or access date.
- `ramirez2024empirical` and `shafer1976evidence` lack DOI/URL/ISBN fields in the BibTeX audit.
- No duplicate DOI or duplicate-title issue was detected.

Support audit:

- Android build/R8 claims are supported by Android documentation citations.
- TPL-Benchmark, SAD, and LibAttention quantitative claims are supported by local primary PDFs.
- UniBOM supports adjacent SBOM workflow claims, not Android TPL exact-version claims. The thesis mostly states this correctly.
- If ObfDetector, LibMD, or LibScope are considered current state-of-the-art in the project context, they are not adequately integrated in the submitted Master PDF. They should be either added with traceable records or explicitly excluded.

Reference recommendation:

- Add access dates to web sources.
- Update UniBOM to the published ACM citation if using the later publication record.
- Include the review protocol/corpus appendix.
- Avoid using anonymous artifacts as strong literature authority unless the claim is only "artifact observed" or "emerging direction".

### Master Score

Score as submitted: **55/100**

| Category | Points |
|---|---:|
| Scientific and technical quality | 8/12 |
| Objectives and problem statement | 8/10 |
| Structure and logical flow | 5/10 |
| Literature review/state of the art | 12/15 |
| Methodology and technical approach | 4/12 |
| Experiments/evaluation/results discussion | 2/12 |
| Writing and academic style | 7/8 |
| Figures/tables/captions | 4/6 |
| Novelty/originality/contribution | 3/10 |
| References and citation quality | 2/5 |
| Total | 55/100 |

Expected committee reaction: **major revisions required**. A generous committee may accept it as a strong survey if the program allows research-synthesis theses. A stricter committee will challenge whether the thesis has an original research contribution at all.

## Engineering/PFE Thesis Review

### Quick Facts

- Title: `Evidence-Based SBOM Recovery from Compiled Android APKs`
- PDF metadata: 124 pages, A4, created 2026-06-24.
- Approximate extracted words: 30,951.
- Structure: introduction, technical background, AI background, state of the art, system design, implementation/evaluation, conclusion, reproducibility appendix.
- Headline evaluation claims in PDF are supported by generated project evidence files, especially `data/results/evaluation/thesis-evaluation-tables.json`.

### Strengths

- Clear engineering problem: APK-only SBOM recovery where source/build metadata is unavailable.
- The system design is coherent: APK extraction, DEX evidence, Maven reference profiles, scoring, CycloneDX output, OSV lookup, source validation, and report generation.
- The thesis is unusually honest about evidence boundaries. It distinguishes 84/84 controlled success, 50.5% emitted-version confirmation, 7.7% full source-denominator exact emission, and 6,772/6,772 source-known upper-bound recognition.
- The implementation chapter maps modules, commands, outputs, and artifacts.
- Failed experiments are preserved and discussed, which is a real engineering strength.
- The appendix gives reproducibility commands and artifact categories.

### Major Issues

| Issue | Severity | Why it is problematic | Recommendation |
|---|---:|---|---|
| Cover page contains red placeholders for defense date, jury president, and examiner. | Critical | Formally unfinished thesis PDF. | Fill official values before any submission. |
| Practical headline may be misunderstood: 50.5% emitted-version confirmation versus 7.7% full-denominator exact recall. | Major | A committee may ask whether the system is practically useful if full source-denominator exact emission is only 7.7%. | Put these metrics side by side earlier, with a plain explanation of target use: high-confidence partial SBOM, not complete dependency recovery. |
| Controlled fixture success is not independent validation. | Major | 84/84 is useful for regression/mechanics but not evidence of deployment accuracy. | Explicitly label fixtures as internal controlled tests and avoid letting them dominate the abstract. |
| No direct baseline run against existing tools in the evaluation. | Major | The thesis compares dimensions, not performance. A defense committee may ask why LibScout/LibPecker/LibHunter/SAD were not run on the same APKs. | Add a short "why no executable baseline" section, or run at least one available baseline on a small comparable subset. |
| Source dependency trees are used as ground truth, but source trees are not perfect APK presence truth. | Major | The thesis acknowledges this, but the artifact validity depends heavily on source-validation quality. | Add a compact table: source app, version, source commit/tag, Gradle config, dependency command, validation artifact path, and known limitations. |
| The reference database coverage limitation is severe. | Major | Exact source-version coverage of 1,231/12,082 rows means many misses are caused before matching. | Discuss how this limits real deployment and what minimum reference coverage is needed for useful operation. |
| AI/DL chapter risks distracting from the deterministic MVP. | Moderate | The high Transformer score with shortcuts may sound impressive but is explicitly non-authoritative; examiners may ask why it is central. | Shorten or move details to appendix; keep only the report-only authority gate and negative raw-opcode result in the main chapter. |
| Some figures are too small, especially report screenshots. | Moderate | Rendered dashboard screenshots are visible but details are hard to read on paper. | Replace full-page screenshots with zoomed panels or pair screenshots with artifact paths and extracted key values. |
| Matcher scoring weights are not fully justified. | Moderate | Weights appear engineered/calibrated but not statistically learned or theoretically derived. | Add a table explaining each weight source, ablation evidence, and why zero-weight features stay diagnostic. |
| The thesis uses "research questions" in an engineering thesis. | Minor | Acceptable, but some committees prefer requirements, validation questions, or engineering objectives. | Add a sentence mapping RQs to engineering validation criteria. |
| Bibliography includes anonymous/Zenodo artifact style reference for LibScope. | Moderate | Anonymous artifacts are weak for strong state-of-the-art claims. | Keep it as emerging artifact evidence only, or replace with a peer-reviewed/public author record if available. |

### Scientific and Technical Quality

Strong for a practice-oriented engineering thesis. The work is not merely a literature review: it implements a pipeline, produces standard SBOM artifacts, validates outputs against source evidence, and keeps uncertainty visible. The main technical weakness is that exact recovery is still limited by reference coverage and candidate generation, and the thesis must frame this as the core result rather than a defect to hide.

### Objectives and Problem Statement

Very clear. The thesis correctly identifies binary-only Android SBOM recovery as a different problem from source-based SBOM generation. The objectives are concrete and map well to implementation modules.

### Structure and Flow

Generally strong. The flow from problem to background to state of the art to design to implementation/evaluation is appropriate. The AI chapter before the state-of-the-art chapter is slightly awkward because it foregrounds a secondary/report-only component before the main deterministic contribution.

### Literature Review and State of the Art

Good coverage, especially for Android TPL detection, R8 challenges, and SBOM standards. The PFE thesis is better than the Master at integrating the literature into engineering decisions. It correctly bounds LibAttention as presence detection and UniBOM as adjacent, not a direct Android exact-version detector.

Weakness: there is no executable baseline comparison with existing tools. The dimensional comparison is honest, but it is not a replacement for an empirical baseline if a committee expects one.

### Methodology and Technical Approach

Strong. The target/control promotion protocol is one of the best parts of the thesis. The separation between authoritative matcher output and report-only AI/R8 diagnostics is defensible. The methodology should, however, include a more compact traceability map from each major metric to the exact generated artifact that supports it.

### Experiments and Results

The evaluation is meaningful and honest:

- 72 controlled fixtures and 84 expected versions: 84/84 exact.
- 5 clean real APKs: 47/47 exact emitted versions.
- 97 partial real APKs: 880/1,790 exact, 636 wrong, 274 missing/nuanced.
- Aggregate emitted-version confirmation: 927/1,837 = 50.5%.
- Full source denominator: 927/12,082 = 7.7%.
- Shared DB exact source-version coverage: 1,231/12,082 = 10.2%.
- Source-known upper-bound lane: 6,772/6,772 emitted rows, but only under source-constrained candidate space.

The thesis does the right thing by not merging these into one inflated score. The defense challenge will be practical significance: "What can a user safely do with this partial SBOM?" The answer should be prepared with examples.

### Writing Quality

Clear and careful. The tone is sometimes defensive because it repeatedly states what the system does not claim. That honesty is valuable, but the final version should make the main positive engineering contribution more prominent.

### Figures, Tables, Diagrams

Architecture figures are readable and helpful. Evaluation tables are dense but generally acceptable. The dashboard screenshots are too small for a printed thesis; they should be zoomed, cropped, or supported by a table of extracted facts.

### Novelty and Practical Contribution

The novelty is not a new theoretical matcher that beats all prior work. The contribution is a working, evidence-governed APK-to-CycloneDX pipeline with source-validation-aware interpretation, vulnerability lookup, artifact generation, and negative-experiment governance. That is a valid engineering contribution.

### PFE Reference Audit

Mechanical audit:

- No unresolved citation markers were found in the PDF text.
- Source-level BibTeX audit found no undefined citation keys.
- Source-level BibTeX audit found unused entry: `sokolova2009measures`.
- Many official web/spec references have no year/date or access date.
- No duplicate DOI or duplicate-title issue was detected.
- The bibliography is recent enough for the core domain: 2024/2025 references are present.

Support audit:

- R8 transformation claims are supported by Android documentation and modern TPL papers.
- TPL-Benchmark supports the realistic benchmark framing and the 60.15% / 76.48% figures.
- SAD supports the 97.64% / 84.82% / 94.12% figures, but the thesis should keep those as original-study performance, not deployment guarantees.
- LibAttention supports R8-resilient presence detection and a 30%+ F1 improvement claim, but not exact-version recovery.
- UniBOM supports SBOM workflow integration, not APK-side Maven exact-version recovery.
- LibScope as an anonymous Zenodo artifact is weak evidence and should be clearly labeled.
- Implementation and evaluation claims rely more on generated project artifacts than on citations; this is acceptable for an engineering thesis, but artifact paths must be explicit.

### PFE Score

Score as submitted: **72/100**

| Category | Points |
|---|---:|
| Scientific and technical quality | 10/12 |
| Objectives and problem statement | 8/10 |
| Structure and logical flow | 8/10 |
| Literature review/state of the art | 11/15 |
| Methodology and technical approach | 9/12 |
| Experiments/evaluation/results discussion | 8/12 |
| Writing and academic style | 7/8 |
| Figures/tables/captions | 4/6 |
| Novelty/originality/practical contribution | 6/10 |
| References and citation quality | 1/5 |
| Total | 72/100 |

The low reference score is mostly because of missing access dates/metadata, weak anonymous artifact use, and lack of empirical baseline references in the evaluation framing, not because citations are broken.

Expected committee reaction: **defendable with revisions**. A typical CS engineering committee would likely see a substantial implemented project and pass it if the administrative placeholders are fixed and the student can explain the metrics honestly. It is not an "excellent" submission until baseline comparison, artifact traceability, and visual polish are improved.

## Cross-Thesis Consistency Issues

| Issue | Severity | Why it matters | Recommendation |
|---|---:|---|---|
| The Master and PFE overlap heavily in topic and vocabulary. | Moderate | A committee may ask what distinct role each thesis plays. | Explicitly distinguish: Master = conceptual/evidence model; PFE = implemented system and empirical validation. Then ensure the Master actually contains the conceptual model. |
| The PFE delivers the case study that the Master abstract claims. | Major | This makes the Master look dependent on a contribution not present in its own body. | Either include a bounded case-study chapter in the Master or remove that abstract claim. |
| Both documents rely on the same literature base. | Minor | Acceptable, but repeated text can feel recycled. | Ensure each thesis has a distinct research question, contribution table, and conclusion. |
| Both title pages are unfinished. | Critical | Formal submission risk. | Fix immediately. |

## Prioritized Revision List

1. Fix all title-page placeholders in both PDFs.
2. Master: include the missing conceptual framework and case-study/evaluation chapter, or downgrade the abstract/objectives to a structured-review thesis.
3. Master: include the review protocol appendix or a compact protocol section with search queries, screening counts, inclusion/exclusion criteria, quality scoring, and corpus table.
4. PFE: add a one-page "metric interpretation" box showing 84/84, 47/47, 927/1,837, 927/12,082, 1,231/12,082, and 6,772/6,772 with permitted and forbidden interpretations.
5. PFE: add an artifact traceability table mapping each headline result to generated JSON/report paths, APK/source version, Gradle command, and date.
6. Add or justify absence of empirical baselines against existing tools. If tool execution is infeasible, explain installation/runtime/data incompatibilities and compare only what can be compared.
7. Update bibliography metadata: access dates for web specs, current published record for UniBOM where applicable, and explicit status for LibScope/LibMD/ObfDetector.
8. Reduce or relocate non-authoritative AI details in the PFE main text; keep the authority gate and negative result prominent.
9. Improve screenshots: crop dashboard panels, enlarge report excerpts, or replace full screenshots with tables plus artifact paths.
10. Tighten wording where claims are broader than evidence, especially "trustworthy", "framework", "evaluation confirms", "state of the art", and "current".

## Top 10 Likely Defense Questions

1. What exactly is the difference between a build-generated SBOM and your recovered APK-derived SBOM?
2. In the PFE, why should a user trust the system if full source-denominator exact recall is only 7.7%?
3. What is the difference between the 50.5% emitted-version confirmation rate and full dependency recall?
4. Why did you not run LibScout, LibPecker, LibHunter, SAD, or another baseline on the same APK set?
5. How do you know a source dependency tree is valid ground truth for what is actually present in the APK?
6. What prevents source-known or validation-only information from leaking into the APK-only decision path?
7. Why are AI and Transformer results included if they are report-only and cannot change SBOM/CVE output?
8. What is the most important failure mode: missing references, wrong-version near ties, candidate generation, R8, native code, or dynamic code?
9. For the Master thesis: where is the proposed framework formally specified and how was it evaluated?
10. Which recent papers or tools are missing from the state of the art, and how would their inclusion change your conclusions?

## Final Assessment

The Engineering/PFE thesis can become a solid defense document with targeted revisions. Its main defense posture should be: "This is not complete dependency recovery; it is an evidence-qualified partial SBOM recovery system that exposes when exact claims are unsafe." That is a defensible and practical engineering contribution.

The Master thesis needs deeper revision. The current PDF contains a promising research argument but not enough research artifact. It must either become a complete conceptual-framework thesis with evaluation, or it must be honestly reframed as a structured state-of-the-art review with a research agenda.
