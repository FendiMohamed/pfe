# PFE and Master Thesis Sources

This directory contains two independently buildable LaTeX projects adapted
from the school template supplied in `togive.zip`:

- `pfe/` - implementation and evaluation thesis;
- `master/` - research and evidence-framework thesis.

The supplied template was used only for its LaTeX organization, multilingual
front matter, typography, and school presentation conventions. Its original
topic text, chapters, macros, and bibliography are not part of these theses.

## Required compiler

Use LuaLaTeX and Biber. In Overleaf:

1. Upload either the complete `pfe/` or `master/` directory as a project. The
   latest PFE source directory is `thesis/pfe/`. The previous PFE source
   package is `pfe-overleaf-full-reports-ai-r8-2026-06-21.zip`; regenerate it
   before upload if the new cover-page design must be included as a ZIP. It
   includes the
   examiner-audited source, consecutive panels covering the complete clean
   F-Droid and controlled vulnerable Jackson HTML dashboards, and report-only
   R8, hybrid-assistance, Random Forest, and Transformer dashboard evidence.
   It contains all seven chapters, Appendix A, all three abstracts, the
   confirmed student and supervisor names, and the drafted dedication and
   acknowledgements. The jury president, examiner, and final defense date
   remain placeholders. The current 139-page local PDF was rebuilt from this
   source on 2026-06-21 with LuaLaTeX and Biber, and all new dashboard pages
   were visually inspected. Older packages are retained as source checkpoints.
2. Select `main.tex` as the main document.
3. Select LuaLaTeX as the compiler.
4. Use TeX Live 2023 or newer.

For a local TeX installation with a working `latexmk`:

```text
cd thesis/pfe
latexmk -lualatex main.tex

cd thesis/master
latexmk -lualatex main.tex
```

On this Windows workstation, MiKTeX's `latexmk` wrapper currently requires a
Perl engine, so the verified local PFE build was produced with the equivalent
manual sequence:

```text
cd thesis/pfe
lualatex -interaction=nonstopmode -halt-on-error main.tex
biber main
lualatex -interaction=nonstopmode -halt-on-error main.tex
lualatex -interaction=nonstopmode -halt-on-error main.tex
```

The latest locally compiled PFE draft source is `thesis/pfe/main.pdf`. The
current named cover-template checkpoint is
`thesis/PFE_Fendi_Mohamed_page_de_garde_template_2026-06-21.pdf`, with an
output copy at `output/pdf/pfe-page-de-garde-template-2026-06-21.pdf`. It keeps
the complete clean and vulnerable dashboard sequence plus the report-only
AI/R8 evidence included, and updates the `page de garde` to match the ESI
template style. The jury president, examiner, and final submission/defense date
remain placeholders.

The latest locally compiled master draft source is `thesis/master/main.pdf`.
The current evidence-review checkpoint is
`thesis/Master_Fendi_Mohamed_evidence_review_2026-06-21.pdf`, with an output
copy at `output/pdf/master-thesis-evidence-review-2026-06-21.pdf`. The older
cover-only checkpoint and Overleaf/TeXPage source package
`thesis/master-overleaf-frontmatter-admin-2026-06-21.zip` remain previous
checkpoints; the source package should be regenerated before upload. This
74-page checkpoint
includes corrected ORLIS and Ramirez descriptions, 15 full-text-verified Tier A
studies, completed quality scores, foundational provenance/uncertainty/SBOM
references, an audited PFE framework evaluation, synchronized conclusions and
multilingual abstracts, and the ESI-style `page de garde`. The jury president,
examiner, and final submission date remain visible front-matter placeholders.

## Writing governance

Before editing either document, read:

- `docs/thesis/THESIS_WRITING_AND_RESUMPTION_RULES.md`
- `docs/thesis/PFE_THESIS_WRITING_PLAN.md`
- `docs/thesis/MASTER_THESIS_WRITING_PLAN.md`
- `docs/thesis/THESIS_WRITING_SESSION_LOG.md`

The PFE and master projects intentionally remain standalone so either can be
uploaded to Overleaf without relying on files outside its directory.
