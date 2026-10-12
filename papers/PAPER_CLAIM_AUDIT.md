# Paper Claim-by-Claim Audit

This audit freezes the wording that can be used in the working manuscript and
identifies what still needs a citation, a final implementation snapshot, or a
restored raw artifact. It is deliberately stricter than a prose review: a
claim is marked **bounded** only when its scope, unit, and limitation are
explicit.

## Section 2 — Introduction

| Claim | Evidence | Status | Required manuscript action |
|---|---|---|---|
| APK-only Android analysis operates on DEX/resources after bytecode conversion and possible R8 removal, rewriting, renaming, and AAR packaging. | Official Android APK Analyzer, D8, R8, and library documentation; project scope in `MVP_ARCHITECTURE.md`. | Bounded | Keep the source/build-graph distinction clear and retain author-year mapping to the exact Android documentation pages. |
| Identity, exact version, and vulnerability applicability are different decisions. | `PAPER_EVIDENCE_MATRIX.md`; matcher/report implementation; OSV workflow artifacts. | Bounded | Preserve this separation throughout the abstract and results. |
| Build transformations and reference coverage make exact-version attribution harder than family identification. | LibHunter, LibScan, SAD, ATVHunter audits; project R8 and coverage diagnostics. | Bounded | Preserve primary-study citations and avoid universal transformation-resilience claims. |
| The contribution is an evidence-aware APK-to-CycloneDX workflow, not universal dependency recovery. | `PROPOSED_APPROACH_DRAFT.md`; architecture and decision log. | Bounded | Keep the negative scope statement in the abstract and conclusion. |
| The reported real-APK metric is emitted-version confirmation. | Thesis tables and claim contracts. | Verified snapshot | Never call it recall, precision, or general APK accuracy. |

## Section 3 — State of the Art

| Claim | Evidence | Status | Required manuscript action |
|---|---|---|---|
| TPL-Benchmark demonstrates denominator and benchmark-construction sensitivity. | Full TPL-Benchmark PDF audit; literature matrix. | Bounded | Insert final citation and retain its dataset-specific metric wording. |
| UniBOM motivates integrated SBOM and vulnerability workflow, but is not Android exact-version ground truth. | Full UniBOM PDF audit. | Bounded | Cite as adjacent workflow evidence only. |
| SAD, LibScan, ATVHunter, and LibHunter use structural, opcode, call-chain, or transformation-aware evidence. | Full primary-paper audits and evidence matrix. | Bounded | Check every method description against the final selected citation. |
| Systematic assessment identifies package-structure, multidex/AAR, partial-import, dependency, obfuscation, and usability issues. | Full 24-page systematic assessment PDF audit. | Bounded | Cite its six criteria and do not pool its percentages with project results. |
| Existing work does not provide the same evidence-bearing APK-to-CycloneDX workflow with the project’s explicit validation and uncertainty separation. | Comparative matrix plus implementation audit. | Provisional gap claim | Phrase as the scope of this review; avoid an absolute novelty claim until the final literature search is frozen. |

## Section 4 — Proposed Approach

| Claim | Evidence | Status | Required manuscript action |
|---|---|---|---|
| The pipeline performs static APK inspection, feature extraction, versioned reference matching, CycloneDX output, and optional OSV lookup. | `src/apk_sbom/`, `MVP_ARCHITECTURE.md`, current implementation draft. | Bounded | Freeze the final source snapshot and add one architecture figure. |
| Reference profiles are stored in a SQLite feature database and compatible JAR/AAR artifacts are converted to DEX for comparison. | Source modules and architecture documentation. | Bounded | Verify exact module names and CLI defaults at manuscript freeze. |
| Identity confidence and exact-version confidence are kept separate; identity statuses are `confirmed`, `likely`, `candidate`, and `uncertain`, while version statuses are `exact`, `likely`, `candidate`, and `uncertain`. | `models.py`, `matcher.py`, `report.py`, `sbom.py`. | Verified implementation | Preserve the two distinct status contracts and do not imply that either label is a calibrated probability. |
| The promoted default includes the composite family shortlist and guarded literal/context reranker. | Promotion verification artifacts. | Verified policy | Include thresholds in an implementation table, not as accuracy claims. |
| Global R8 blending and broader AI/structural experiments are not production authority. | Decision ledger, R8 phase reports, AI integration gate. | Verified decision | Report the regression evidence in Section 5 or limitations. |
| Native `.so` files receive hash-only file components rather than Maven package/version claims. | SBOM implementation and native-boundary evaluations. | Verified implementation | Preserve this scope in the architecture and threat sections. |
| The CLI enables the two promoted guarded behaviors by default and keeps R8/version-band/AI additions opt-in report-only paths. | `src/apk_sbom/cli.py` parser definitions and promotion-gate tests. | Bounded implementation | Verify the final CLI snapshot and retain the explicit no-score-change wording. |
| Promotion policy rejects incomplete control coverage, reportable drift, unsafe global reference scope, and APK-only rerankers with no safe fixes. | Promotion-gate test suite. | Bounded policy evidence | Cite as gate behavior; do not convert test fixtures into experimental accuracy. |

## Section 5 — Evaluation

| Claim | Evidence | Status | Required manuscript action |
|---|---|---|---|
| Controlled lane: 84/84 expected versions across 72 fixtures. | Retained thesis tables, controlled-evaluation documents, and project task history. | Documented final snapshot; 30 fixtures/35 components is an earlier expansion checkpoint | Use the later 72/84 aggregate as the final recorded controlled result and describe 30/35 only as an earlier milestone. |
| Clean real lane: 47/47 across five APKs. | Thesis tables and source-validation summaries. | Verified retained snapshot | State that several clean rows are sparse. |
| Partial real lane: 880/1790 across 97 APKs. | Thesis tables and source-validation summaries. | Verified retained snapshot | Explain partial rows by family and version mismatch categories. |
| Combined emitted-version confirmation: 927/1837 across 102 Maven-emitting APKs. | Thesis tables and claim contracts. | Verified retained snapshot | Keep the 102-case denominator attached to this metric. |
| Source-denominator coverage: 927/12082 across 106 source-tree cases. | Coverage dashboard and claim contracts. | Verified retained snapshot | Keep this separate from 102-case emitted confirmation and 110-case transparency inventory. |
| Shared reference database coverage is 2220/12082 coordinate-present and 1231/12082 exact-version-present. | Coverage-first dashboard. | Verified retained snapshot | Present as a coverage threat, not matcher precision. |
| Source-known constrained lane: 6772/6772 across 106 cases. | Final v2 evaluation artifacts and claim contracts. | Bounded upper-bound | Put “source-version-constrained upper bound” in the table title and text. |
| OSV demonstrations establish workflow preservation, not vulnerability precision/recall. | Controlled Jackson fixture, F-Droid demonstration, vulnerability module/tests. | Bounded | Do not generalize from the examples to population vulnerability detection. |
| Threats include calibration overlap, source validation copies, sampling bias, missing references, native/hidden code, external OSV dependence, and unavailable machine-readable row exports for independent recalculation. | `IMPLEMENTATION_EVALUATION_DRAFT.md` and readiness audit. | Verified | Keep construct and conclusion validity distinct; cite the thesis and retained evaluation records as the numerical provenance. |

| Thesis framing remains compatible with the paper framing. | Full `thesis/pfe/chapters/ch01_general_introduction.tex` and `thesis/master/chapters/ch05_general_conclusion.tex` review. | Verified | Reuse only the bounded problem, RQs, evidence-quality principle, and future directions; avoid copying thesis chapter structure or unsupported thesis wording. |

### Snapshot conflict requiring release control

The retained R8 Phase-4 materials are internally inconsistent at the count
level. The examiner/decision-ledger snapshot records 4 target improvements,
6 controlled regressions, 30 source-validated regressions, and 8 clean-real
regressions. The expanded Phase-4 Markdown records 10 potential improvements,
6 controlled blockers, 121 real blockers, and 10 clean-real blockers across
1,093 covered rows. Both reject global promotion, but neither count set can be
used without its matching database, input manifest, and generation snapshot.
The integrated manuscript therefore uses the qualitative rejection decision
and does not combine counts from incompatible diagnostic snapshots.

## Cross-section release gates

1. Replace working literature anchors with final citation keys and selected
   venue formatting.
2. Cite the retained thesis tables, evaluation dashboards, and task history as
   the provenance for reported numerical snapshots; identify the 20 June 2026
   PFE snapshot and commit where applicable.
3. If a machine-readable release package is available, use it to regenerate
   tables; otherwise retain the documented numbers and disclose that they
   were not independently recalculated for this paper.
4. Generate figures and tables from the documented values with denominator
   scopes visible.
5. Run a final pass ensuring that no section uses `accuracy`, `recall`,
   `precision`, `ground truth`, or `vulnerability detection` where the claim
   contract permits only emitted-version confirmation, source-denominator
   coverage, constrained recognition, or workflow demonstration.

## Full-draft checkpoint — 2026-09-29

The integrated manuscript now contains all six supervisor-requested sections.
The abstract is provisional and deliberately excludes a controlled-lane
number pending final abstract editing. The project history records the 30/35
controlled-set checkpoint before expansion to the later thesis snapshot of
72/84. Real-APK and source-denominator values are documented in the thesis and
evaluation records; the checkout lacks some machine-readable exports needed
for independent recalculation. The next release work is to finish the
cross-section metric/claim audit and venue formatting, while keeping the
documented evidence provenance visible.

The current author–year citations in Sections 2–3 map to `REFERENCES_DRAFT.md`.
Android Developers web references are explicitly mapped to the APK Analyzer
and R8 optimization documentation; the two Zhan et al. (2021) works are
disambiguated as 2021a (ATVHunter) and 2021b (systematic assessment), following
the order in the current working reference list. The NIST report is cited by
its listed authors (Boyens et al., 2022). This resolves
working-list consistency, but final venue style and publication metadata still
require a venue-specific check.

## Historical project-description caveat

The root `README.md` and `AGENTS.md` describe an earlier research baseline and
contain broader or stale statements, including Bayesian scoring, an early MVP
target, and literature claims not used by the current paper. Current source
modules, architecture decisions, evaluation artifacts, and the paper evidence
matrix are authoritative for the manuscript. The README remains useful as
project history, not as implementation evidence.
