# Final Report Readiness Package

Use this file as the final thesis/report assembly checklist. It assumes the MVP demo package is already ready and focuses on the written report, figures, screenshots, and consistency guardrails.

## Current Status

| Area | Status | Evidence |
|---|---|---|
| Main report draft | ready for university template | `docs/thesis/PFE_FINAL_REPORT_ASSEMBLED.md` |
| Final v2 addendum | ready | `docs/thesis/FINAL_V2_RESULTS_SECTION.md` |
| Thesis artifact index | regenerated | `docs/thesis/THESIS_ARTIFACT_INDEX.md` |
| Final demo checklist | ready | `docs/evaluation/FINAL_DEMO_CHECKLIST.md` |
| Defense deck | ready/editable | `outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/output/apk-sbom-defense-deck.pptx` |
| Graduation rehearsal | regenerated | `docs/evaluation/GRADUATION_DEMO_REHEARSAL.md` |

The remaining report work is human/template work: fill the university cover page, insert screenshots/figures, apply required formatting, and export the final PDF/Word file.

## Cover Page Fields To Fill

| Field | Status |
|---|---|
| University | human input required |
| Faculty / Department | human input required |
| Program | human input required |
| Project type | ready: PFE / final-year project |
| Student | human input required |
| Supervisor | human input required |
| Academic year | human input required |

## Required Wording

Use this for the normal real-APK metric:

```text
The normal source-validated real-APK metric is emitted Maven version confirmation rate. The MVP confirms 927/1837 emitted Maven versions across 102 source-validated real APKs, with clean and partial APKs reported separately.
```

Use this for the v2 lane:

```text
The final v2 package is a source-version constrained upper-bound evaluation. Across 106 source-tree APK cases, all 6772 emitted rows were exact source confirmations, with 0 wrong-version emitted rows and 0 missing emitted rows. This is not unconstrained APK-only production accuracy.
```

Use this for transparency:

```text
The remaining 5238 source-gap rows are exported and triaged instead of hidden: 2515 are boundary or alias rows, while 2723 remain actionable as 442 missing-reference candidates and 2281 matcher-recall candidates.
```

Avoid:

```text
The tool has 100% accuracy on real APKs.
```

## Figure And Screenshot Plan

| Figure | Source artifact | Insert near | Caption |
|---|---|---|---|
| Architecture pipeline | `docs/architecture/MVP_ARCHITECTURE.md` | Chapter 3: Proposed Approach | Static APK-to-SBOM pipeline from APK extraction to CycloneDX SBOM and OSV reporting. |
| Dataset/evaluation layers | `docs/evaluation/DATASET_DESIGN.md` and `docs/evaluation/APK_TYPE_EVALUATION.md` | Chapter 5: Evaluation Methodology | Controlled, clean real, partial real, and limitation layers with separate metric rules. |
| Main results table | `docs/evaluation/THESIS_EVALUATION_TABLES.md` | Chapter 6: Results | Controlled and source-validated emitted Maven version confirmation results. |
| Clean report screenshot | `data/results/report-real-f-droid-final-demo-osv/report.html` | Chapter 6.3: Vulnerability Demonstration | Calibrated F-Droid APK report with source-confirmed SBOM components and 0 OSV vulnerabilities. |
| Clean SBOM snippet | `data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json` | Chapter 4 or 6.3 | CycloneDX component evidence with Maven PURLs and confidence properties. |
| Vulnerable CVE screenshot | `data/results/demo-osv-vulnerable-jackson-databind/report.html` | Chapter 6.3: Vulnerability Demonstration | Controlled Jackson Databind fixture returning three HIGH OSV advisories. |
| V2 package table | `docs/evaluation/DEMO_FINAL_V2_PACKAGE.md` | Chapter 6.5: Final V2 Package | Source-version constrained v2 package metrics and remaining gap categories. |
| Transparency export table | `docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md` | Chapter 6.5 or appendix | Row-level dataset/source/emitted/vulnerability classifications. |
| Defense deck contact sheet | `outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/preview/contact-sheet.png` | Appendix or defense preparation | Visual overview of the final 12-slide defense deck. |

## Final Report Assembly Order

1. Start from `docs/thesis/PFE_FINAL_REPORT_ASSEMBLED.md`.
2. Fill the cover-page fields from the university template.
3. Insert or recreate the figures listed above.
4. Keep `docs/thesis/FINAL_V2_RESULTS_SECTION.md` as the final subsection of Chapter 6.
5. Use `docs/thesis/THESIS_ARTIFACT_INDEX.md` as the appendix/evidence map.
6. Use `docs/evaluation/FINAL_DEMO_CHECKLIST.md` for defense-day file order.
7. Export the final document to the format requested by the university.

## Consistency Checks

Before submission, search the final document for these risky phrases:

| Search | Required handling |
|---|---|
| `100% accuracy` | Only allowed when immediately scoped to controlled fixtures or the source-version constrained v2 lane. |
| `real-world accuracy` | Avoid. Use `emitted Maven version confirmation rate` instead. |
| `full dependency recall` | Avoid for the normal metric. Use only when discussing the full source dependency denominator. |
| `106 real APKs` | Must say `106 source-tree APK cases` and mention source-version constraints. |
| `K-9 clean` | Avoid. K-9 is source-validated partial after validation-only rescue. |
| `native version` | Avoid. Native files are hash-only CycloneDX file components. |

## Non-Blocking Future Work

These are valid thesis future-work items, but they should not block the final report/demo:

| Item | Current evidence |
|---|---|
| Matcher recall | `2281` v2 matcher-recall candidates; `1425` report-only source-context suggestions. |
| Remaining reference growth | `442` v2 missing-reference candidate rows. |
| Unconstrained large-DB production run | Still blocked by matcher runtime/regression behavior; needs safer shortlist/reranking. |
| Native package/version identification | Native `.so` files are currently hash-only SBOM file components. |
| Packed/hidden/dynamic code | Hidden DEX and obfuscation samples are limitation evidence, not accuracy rows. |
| Broader framework families | Flutter, Unity, and more commercial protected samples remain future dataset work. |

## Validation Snapshot

The final report package was checked after the final demo checklist checkpoint:

| Check | Result |
|---|---|
| Transparency export regeneration | passed |
| Thesis artifact index regeneration | passed |
| Graduation demo rehearsal regeneration | passed |
| V2 dashboard counts | `106` cases, `6772` checked, `0` mismatches, `0` missing |
| Transparency export counts | `110` cases, `12082` source rows, `6772` emitted rows, `232` vulnerability rows |
| Deck validation | passed earlier: `12` slides and `12` notes slides |
