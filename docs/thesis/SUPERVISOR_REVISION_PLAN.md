# Supervisor Revision Plan

Status legend:

- `[ ]` Not started
- `[~]` In progress
- `[x]` Fixed in source
- `[v]` Rendered and visually verified in the compiled PDF
- `[?]` Needs user/supervisor input

This file tracks the supervisor notes for both the Master thesis and the PFE thesis. Each fix should be checked here after the LaTeX source is changed, then upgraded to `[v]` only after a PDF render confirms the page, numbering, references, and spacing are correct.

## Global Fix Rules for Both Theses

- [v] Correct supervisor name in both theses to `Abdelhak Djamel Seriai`.
- [x] Add explicit in-text callouts before every important new or edited figure and table, using forms such as "Figure~\ref{...} illustrates..." and "Table~\ref{...} summarizes...".
- [x] Ensure every new or edited figure and table caption/title contains a clear title plus the citation/reference when the content comes from a paper, external source, or adapted source.
- [?] Use existing student theses/memoires as layout and organization references when expanding state-of-the-art narratives and fixing empty page space.
  - The supervisor-provided model thesis has not been added to the workspace yet; recheck this item when it is available.
- [x] Rebalance chapter introductions so they are similar in length and level of detail across chapters.
- [x] Rebalance chapter conclusions so they are not extremely short compared with the chapter body.
- [v] Rebuild both PDFs and inspect the table of contents, list of figures, list of tables, page numbering, blank pages, and under-filled pages with large unused space.

## Master Thesis Plan

Target source directory: `thesis/master`

### Master Structure

- [v] Remove the current proposed-work chapter from the Master thesis.
  - Source to remove from flow: `thesis/master/chapters/ch04_evidence_trust_framework.tex`
  - Expected final structure:
    - Chapter 1: General Introduction
    - Chapter 2: Background
    - Chapter 3: State of the Art
    - Chapter 4: General Conclusion
- [v] Update `thesis/master/main.tex` so the Master contains only the four expected chapters and does not mention PFE-specific proposed work.
- [v] Rename/retitle the final conclusion chapter so it becomes Chapter 4 after the proposed-work chapter is removed.
- [v] Remove any PFE wording from the Master thesis so it reads as an independent Master thesis.

### Master Chapter 1

- [v] Expand the context section with more background on APK SBOM extraction, vulnerability tracking, third-party libraries, and obfuscation.
- [v] In the Thesis Organization section, bold each chapter entry.
- [v] Check Chapter 1 introduction size against other chapter introductions and adjust if it is much larger or smaller.

### Master Chapter 2

- [v] Expand the Background chapter with more detail.
- [v] Add or adapt schemas/figures where useful, for example:
  - Android APK structure and build pipeline.
  - Third-party library reuse and dependency flow.
  - SBOM-to-CVE matching pipeline.
  - Obfuscation/R8 transformation overview.
- [v] Add proper figure callouts before the new or existing figures.
- [v] Expand the Chapter 2 conclusion so it summarizes the background and transitions to state of the art.

### Master Chapter 3

- [v] Before the comparative table, add narrative explanations of each major related work/method.
- [v] Explain the approaches in the state of the art before showing the synthesis/comparison table.
- [?] Compare the organization with the available example memoires/reports before finalizing the State of the Art chapter flow.
  - Needs the supervisor-provided model thesis for a meaningful comparison.
- [x] Add figures/schemas if they help explain tool families or method categories.
  - No extra Master Chapter 3 figure was added because the edited narrative and taxonomy table already explain the method families without introducing a weak decorative schema.
- [v] Keep the comparative table, but ensure it is introduced by text and has a referenced caption.

### Master Final Conclusion

- [v] Keep only:
  - General Conclusion
  - Answers to the Research Questions, if still useful
  - Future Works / Perspectives
- [v] Remove other conclusion subsections, especially contribution-style or implementation/proposed-work sections.
- [v] Ensure the final conclusion does not reference the PFE work as a separate known project.

### Master Formatting and Verification

- [v] Fix pages without numbers.
- [v] Check page 5 after the thesis-organization bolding.
- [v] Rebuild the Master PDF.
- [v] Visually inspect page numbering, blank pages, figure/table references, chapter order, and table of contents.

## PFE Thesis Plan

Target source directory: `thesis/pfe`

### PFE Chapter 1

- [v] Remove Section 1.7 Contributions.
  - Source: `thesis/pfe/chapters/ch01_general_introduction.tex`
- [v] Remove Section 1.8 Scope and Limitations.
  - Source: `thesis/pfe/chapters/ch01_general_introduction.tex`
- [v] Remove Section 1.10 Conclusion.
  - Source: `thesis/pfe/chapters/ch01_general_introduction.tex`
- [v] Recheck numbering after removing these sections.
- [x] Rebalance the Chapter 1 introduction length with other chapter introductions.

### PFE Chapter 2

- [v] Reduce wasted space around page 19 by moving or reshaping the subsection "2.6.2 Manifest, Resources, and Assets" so it begins earlier if possible.
  - Specific supervisor suggestion to place on/near page 19 if the layout allows it: "The manifest declares the application package, components, permissions, features, SDK..."
- [v] Remove Section 2.10.4 "Relationship to the Proposed System" because the contribution is not defined yet at that point.
- [x] Add explicit in-text callouts before every figure and table in the chapter.
- [v] Number every displayed mathematical formula with equation numbers, following the style shown in the supervisor image.
- [v] Rebuild and inspect the page around current page 24 to confirm formulas are numbered.

### PFE Chapter 3: Artificial Intelligence

- [v] Rewrite the chapter so it defines AI methods used in the domain, instead of describing what was personally implemented.
- [v] Move the detailed AI implementation/evaluation work into the Contribution part instead of leaving it in Chapter 3.
  - Detailed AI evidence now appears in Chapter 6 under the AI and R8 evaluation section.
- [?] Use the supervisor-provided model thesis as a style guide when available.
  - Waiting for the model thesis from the supervisor/user.
- [v] Keep method explanations general and educational:
  - Machine learning basics.
  - Supervised learning.
  - Classification and imbalanced data.
  - Evaluation metrics.
  - Deep learning / transformers if relevant.
  - AI-assisted report analysis only as a method category, not as "what we did".
- [v] Move or adjust the class-distribution paragraph and "Allowed and Forbidden Actions" text to reduce the page 30 blank space if it remains appropriate after the rewrite.
  - Specific supervisor text to place on/near page 30 if the chapter still keeps this material: "The class distribution is imbalanced. The largest class contains 7,811 rows, while the smallest contains 594..."
  - Specific supervisor text to place after it if still relevant: "3.2.3 Allowed and Forbidden Actions" with allowed actions and forbidden actions.
- [v] Reduce Figure 3.3 if needed to remove the large blank space around page 44.
- [v] Add explicit in-text callouts before all figures and tables.

### PFE Chapter 4: State of the Art

- [v] Add narrative explanations of each method/tool before the comparative table.
- [?] Compare the organization with the supervisor-provided model thesis when available and with the existing example memoires/reports.
  - Waiting for the model thesis from the supervisor/user.
- [v] Cover the methods listed in the supervisor screenshot and current comparative table:
  - LibScout
  - LibD
  - ORLIS
  - LibPecker
  - LibID
  - ATVHUNTER
  - LibScan
  - LibHunter
  - SAD
  - LibAttention
  - UniBOM
- [v] Add explanatory images/schemas where possible, especially for method families.
- [v] Keep the comparative table after the method explanations, with a proper in-text introduction and caption/reference.
- [v] Fix the large blank/under-filled page around current page 59 by resizing a figure or moving/copying the following paragraph naturally onto that page if it improves layout.
- [v] Check and fix under-filled pages around current pages 65 and 67.

### PFE Final Conclusion

- [v] Keep only:
  - General Conclusion
  - Answers to the Research Questions, if still useful
  - Future Perspectives
- [v] Remove the rest of the final-conclusion subsections.
- [v] Ensure the conclusion reads as a clean final closing, not another implementation chapter.

### PFE Formatting and Verification

- [v] Rebuild the PFE PDF.
- [v] Inspect current pages 19, 24, 30, 44, 59, 65, and 67 after edits.
- [x] Inspect figure/table captions and in-text references across the full PDF.
- [v] Inspect equation numbering across Chapter 2.
- [v] Inspect table of contents, list of figures, list of tables, page numbering, and blank/under-filled pages.

## Execution Order

1. [v] Master structural cleanup: remove proposed-work chapter and make final chapter Chapter 4.
2. [v] Master content pass: expand context, background, state-of-the-art explanations, and conclusion.
3. [v] Master formatting pass: figure/table references, page numbers, page 5, render verification.
4. [v] PFE structural cleanup: remove requested Chapter 1 and Chapter 2 sections.
5. [v] PFE Chapter 2 formula/reference/spacing pass.
6. [v] PFE Chapter 3 AI rewrite and Figure 3.3 spacing pass.
7. [v] PFE Chapter 4 state-of-the-art narrative expansion and blank-page fixes.
8. [v] PFE final conclusion cleanup.
9. [v] Final render verification for both PDFs and update this checklist to `[v]` for verified items.
