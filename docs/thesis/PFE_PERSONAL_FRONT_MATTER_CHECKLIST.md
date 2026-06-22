# PFE Personal Front-Matter Checklist

This checklist separates the completed technical thesis content from personal
and administrative information that must be supplied or approved by the
student. No name or personal message should be guessed.

## Required Personal Values

| Item | Current source | Value needed |
|---|---|---|
| Student name | `thesis/pfe/metadata.tex` - `\StudentName` | Completed: Fendi Mohamed |
| Supervisor | `thesis/pfe/metadata.tex` - `\SupervisorName` | Completed: Serai Abdelhak |
| Co-supervisor | `thesis/pfe/metadata.tex` - `\CoSupervisorName` | Completed: Manel Baba Ahmed |
| Jury president | `thesis/pfe/metadata.tex` - `\PresidentName` | Full name and preferred title |
| Examiner | `thesis/pfe/metadata.tex` - `\ExaminerName` | Full name and preferred title |
| Defense date | `thesis/pfe/metadata.tex` - `\DefenseDate` | Final date in the school's required format |
| Acknowledgements | `thesis/pfe/frontmatter/acknowledgements.tex` | Draft completed; awaiting final student approval |
| Dedication | `thesis/pfe/frontmatter/dedication.tex` | Draft completed; awaiting final student approval |

## Existing Administrative Values to Confirm

These fields are already populated, but they should be checked against the
school's official wording before submission:

| Item | Current value |
|---|---|
| Thesis title | Evidence-Based SBOM Recovery from Compiled Android APKs |
| Subtitle | Design, Implementation, and Evaluation of a Hybrid Static Analysis Pipeline |
| Specialty | Computer Systems Engineering (CIS) |
| Academic year | 2025--2026 |
| Institution and degree wording | Defined in `thesis/pfe/frontmatter/titlepage.tex` |

## Completion Procedure

1. Replace the three remaining placeholder values in
   `thesis/pfe/metadata.tex`.
2. Confirm the completed acknowledgements draft.
3. Confirm the completed dedication draft, or remove the dedication input from
   `main.tex` if no dedication page is wanted.
4. Compile with LuaLaTeX and Biber.
5. Visually inspect the title page, jury table, dedication, acknowledgements,
   English abstract, French résumé, and Arabic abstract.
6. Confirm spelling, titles, date format, Arabic direction, page breaks, and
   table alignment before marking the front matter approved.

## Current Boundary

The student, supervisor, and co-supervisor names are now filled, and the
dedication and acknowledgements have complete drafts. The jury president,
examiner, and final defense date remain pending. The current 122-page draft
has compiled successfully and passed the rendered-page inspection; one final
title-page check is required after those three values are supplied.
