# Paper Figures and Tables Specification

This specification defines the manuscript visuals before they are generated.
Every item has a purpose, source, unit, denominator, and interpretation rule.

## Figures

### Figure 1 — APK-to-SBOM evidence workflow

- **Purpose:** Explain the proposed approach at the architectural level.
- **Flow:** APK/manifest/DEX inspection → feature extraction → versioned Maven
  reference profiles → family and version matching → identity/version
  confidence and ambiguity → CycloneDX → optional OSV qualification.
- **Evidence source:** `papers/PROPOSED_APPROACH_DRAFT.md` and current modules
  under `src/apk_sbom/`.
- **Must show:** source validation as an evaluation-side path, not an ordinary
  APK-only matcher input; native `.so` files as hash-only file components.
- **Must not show:** diagnostic or report-only R8/AI paths as default authority.

### Figure 2 — Evaluation lanes and claim boundaries

- **Purpose:** Prevent readers from interpreting all reported numbers as one
  score.
- **Lanes:** controlled fixtures; clean source-validated; partial
  source-validated; no-Maven-signal controls; source-denominator coverage;
  source-known upper bound; report-only/experiment-only; limitation cases.
- **Evidence source:** `papers/IMPLEMENTATION_EVALUATION_DRAFT.md` and
  `papers/PAPER_EVIDENCE_MATRIX.md`.
- **Visual rule:** use separate boxes or bands with arrows showing which claims
  each lane permits.
- **Must not imply:** that the 6,772/6,772 constrained result is ordinary
  APK-only accuracy.

### Figure 3 — Per-family emitted-version confirmation

- **Purpose:** Show variation hidden by the aggregate 50.5% rate.
- **Unit:** APK family or documented bucket, with confirmed and checked
  emitted Maven version rows.
- **Source:** `docs/evaluation/APK_TYPE_EVALUATION.md` and the retained thesis
  tables.
- **Required strata:** clean, modern AndroidX/Kotlin partials, R8/minified,
  native-heavy, dependency-era drift, and no-signal/boundary controls.
- **Display:** counts and rates together; sparse clean cases labeled.
- **Must not include:** no-Maven-signal or limitation cases in the denominator
  of an emitted-row rate.

### Figure 4 — Source-denominator coverage decomposition

- **Purpose:** Explain why emitted confirmation is not full recall.
- **Unit:** source coordinate/version rows across the 106 source-tree cases.
- **Source:** `docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md` and the
  retained v2 transparency summary.
- **Categories:** exact source version present and emitted; exact version in
  DB but not emitted; matcher-recall candidate; artifact-family alias;
  metadata/source-only; source boundary; missing reference.
- **Must display:** 12,082 total source rows and the 927 exact emitted rows;
  category definitions must be visible in the caption or table.

## Tables

### Table 1 — Related-work comparison

Columns: study or method family, task/evidence, version/transformation scope,
and relevance/comparison limit. Table 1 is qualitative; study-specific
datasets and metrics remain described in the accompanying prose and primary
source notes rather than ranked in a common score column.

Sources: `papers/PAPER_EVIDENCE_MATRIX.md` plus the primary-paper register.
Percentages remain attached to their original protocol and are not ranked as a
single leaderboard.

### Table 2 — Dataset strata and metric eligibility

| Stratum | Cases | Ground truth | Metric eligibility |
|---|---:|---|---|
| Controlled fixtures | 72 | Manifest/fixture construction | Exact coordinate/version confirmation |
| Clean source-validated | 5 | Resolved source dependency tree | Emitted-version confirmation |
| Partial source-validated | 97 | Resolved source dependency tree | Emitted-version confirmation and failure taxonomy |
| No-Maven-signal controls | 4 | Source tree plus report proof | No emitted-row rate; report as zero-signal control |
| Source-known upper bound | 106 source-tree cases | Exact source coordinate/version slices | Constrained recognition only |
| Limitation inventory | 4 additional cases | Boundary/proof evidence | Excluded from Maven accuracy |

The current manuscript's Table 2 expands this layout to show row units,
historical snapshot qualifiers, and the separate source-denominator and
source-constrained lanes. It also states that the 110-case inventory is
broader than the 106-case source-tree denominator and the 102-case
emitted-row metric.

### Table 3 — Main results with denominators

| Lane | Cases | Checked | Confirmed | Interpretation |
|---|---:|---:|---:|---|
| Controlled | 72 | 84 expected | 84 | Controlled recovery only |
| Clean source-validated | 5 | 47 emitted | 47 | Emitted-version confirmation |
| Partial source-validated | 97 | 1,790 emitted | 880 | Emitted-version confirmation |
| Combined emitting set | 102 | 1,837 emitted | 927 | Emitted-version confirmation, not recall |
| Source-known upper bound | 106 | 6,772 emitted | 6,772 | Source-constrained recognition |

The full source denominator `927/12,082` should appear in a separate coverage
row or table, not be conflated with the emitted-row metric.

### Table 4 — Failure and boundary taxonomy

Columns: category, operational meaning, representative project examples,
metric treatment, and future action.

Required categories: missing reference coordinate/version, version-band tie,
artifact-family alias, metadata-only dependency, native file, hidden or
unparsed DEX, dynamic/native boundary, and validation-only source copy.

### Table 5 — Experiment decision ledger

Columns: experiment, intended signal, evaluation lane, observed benefit,
regressions or threats, final status, and effect on default authority.

Include only decisions that explain the method or limitations: rejected global
R8 blend, scoped trigger experiments, source-version upper-bound lane, AI/R8
report-only gate, and guarded reference promotion.

## Generation and verification rules

1. Generate every visual from a frozen machine-readable snapshot when such
   exports are available. Otherwise, transcribe only documented aggregate
   values and cite their thesis or evaluation record; do not invent per-case
   values.
2. Put numerator, denominator, unit, exclusions, and lane in each caption or
   table note.
3. Keep clean, partial, no-signal, constrained, and limitation rows visually
   distinct.
4. Verify that all repeated numbers match the claim contracts and the cited
   evidence records before submission.
